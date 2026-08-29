/* ============ circuits ============
 *
 * A schematic you draw, and a solver that actually solves it.
 *
 *   Netlist   parts on a grid, wires between grid points, nodes by union-find
 *   MNA       modified nodal analysis — DC operating point, AC sweep, transient
 *   Editor    place, wire, move, edit values, delete; canvas only, no libraries
 *
 * The solver is the real method, not a lookup table of textbook answers: the same
 * stamps a SPICE engine uses, assembled into a matrix and solved by Gaussian
 * elimination with partial pivoting. Capacitors and inductors get companion models
 * for transient, and complex admittances for AC. What it will not do is non-linear
 * devices — there is no Newton loop, so no diodes or transistors. That limit is
 * stated rather than hidden, because a learner who trusts a wrong answer is worse
 * off than one who knows where the tool stops.
 */

/* ---------------------------------------------------------------- linear algebra */
const Lin = (function () {

  /* complex numbers as [re, im] — enough for AC, and cheaper than objects */
  function cadd(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
  function csub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function cmul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
  function cdiv(a, b) {
    const d = b[0] * b[0] + b[1] * b[1];
    if (d === 0) return [0, 0];
    return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
  }
  function cabs(a) { return Math.hypot(a[0], a[1]); }

  /* Gaussian elimination with partial pivoting, over complex numbers.
     A singular matrix means the circuit is under-determined — a floating node, or a
     loop of voltage sources — and the caller turns that into a readable message. */
  function solve(A, b) {
    const n = b.length;
    const M = A.map(function (row, i) { return row.slice().concat([b[i]]); });
    for (let col = 0; col < n; col++) {
      let piv = col, best = cabs(M[col][col]);
      for (let r = col + 1; r < n; r++) {
        const m = cabs(M[r][col]);
        if (m > best) { best = m; piv = r; }
      }
      if (best < 1e-14) return null;
      if (piv !== col) { const t = M[col]; M[col] = M[piv]; M[piv] = t; }
      const d = M[col][col];
      for (let c = col; c <= n; c++) M[col][c] = cdiv(M[col][c], d);
      for (let r = 0; r < n; r++) {
        if (r === col) continue;
        const f = M[r][col];
        if (cabs(f) === 0) continue;
        for (let c = col; c <= n; c++) M[r][c] = csub(M[r][c], cmul(f, M[col][c]));
      }
    }
    return M.map(function (row) { return row[n]; });
  }

  function zeros(n) {
    const A = [];
    for (let i = 0; i < n; i++) {
      const row = [];
      for (let j = 0; j < n; j++) row.push([0, 0]);
      A.push(row);
    }
    return A;
  }

  return { solve: solve, zeros: zeros, cadd: cadd, csub: csub, cmul: cmul, cdiv: cdiv, cabs: cabs };
})();

/* ---------------------------------------------------------------- parts */
const PART_KINDS = {
  R: { name: 'Resistor', unit: 'Ω', def: 1000, pins: 2, sym: 'R' },
  C: { name: 'Capacitor', unit: 'F', def: 1e-6, pins: 2, sym: 'C' },
  L: { name: 'Inductor', unit: 'H', def: 1e-3, pins: 2, sym: 'L' },
  V: { name: 'Voltage source', unit: 'V', def: 5, pins: 2, sym: 'V' },
  I: { name: 'Current source', unit: 'A', def: 0.001, pins: 2, sym: 'I' },
  GND: { name: 'Ground', unit: '', def: 0, pins: 1, sym: '⏚' },
  /* Node numbering falls out of however the schematic was drawn, so a check has no
     way to name "the output" on its own. The learner marks it. Placing a probe is
     also the habit you want: measure where you meant to, not where it was easy. */
  OUT: { name: 'Probe', unit: '', def: 0, pins: 1, sym: '◦' },
};

/* engineering notation both ways, because 1e-6 is not how anyone says a microfarad */
function fmtEng(v, unit) {
  if (v === 0) return '0 ' + unit;
  const a = Math.abs(v);
  const P = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'],
             [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p']];
  for (const [mul, pre] of P) {
    if (a >= mul * 0.999) {
      const s = (v / mul);
      return (Math.abs(s) >= 100 ? s.toFixed(0) : Math.abs(s) >= 10 ? s.toFixed(1) : s.toFixed(2))
        .replace(/\.?0+$/, '') + ' ' + pre + unit;
    }
  }
  return v.toExponential(2) + ' ' + unit;
}

function parseEng(text, fallback) {
  const m = /^\s*(-?[\d.]+(?:[eE][-+]?\d+)?)\s*([GMkmunpµ]?)/.exec(String(text));
  if (!m) return fallback;
  const mul = { G: 1e9, M: 1e6, k: 1e3, '': 1, m: 1e-3, u: 1e-6, 'µ': 1e-6, n: 1e-9, p: 1e-12 };
  const v = parseFloat(m[1]) * (mul[m[2]] !== undefined ? mul[m[2]] : 1);
  return isFinite(v) ? v : fallback;
}

/* ---------------------------------------------------------------- netlist */
const Netlist = (function () {

  /* Pins in grid coordinates. A part sits at (x, y) and is either horizontal or
     vertical; two-pin parts span two cells so a wire can meet them squarely. */
  function pinsOf(p) {
    if (p.kind === 'GND' || p.kind === 'OUT') return [[p.x, p.y]];
    return p.rot ? [[p.x, p.y - 1], [p.x, p.y + 1]] : [[p.x - 1, p.y], [p.x + 1, p.y]];
  }

  /* Sources need a polarity, and it has to be the one people draw. A schematic is
     read left to right and bottom to top, so the + terminal is the RIGHT pin of a
     horizontal source and the TOP pin of a vertical one. Ordering the pins that way
     here means a divider laid out with ground on the left gives a positive output,
     which is what anyone building one expects. R, C and L are symmetric and do not
     care. The editor draws the + so it is never a guess. */
  function plusFirst(p) {
    const pins = pinsOf(p);
    if (p.kind !== 'V' && p.kind !== 'I') return pins;
    return p.rot ? pins : [pins[1], pins[0]];
  }

  function key(pt) { return pt[0] + ',' + pt[1]; }

  /* Union-find over every point touched by a wire or a pin: two points in the same
     set are electrically the same node. */
  function build(model) {
    const parent = {};
    function find(a) {
      if (parent[a] === undefined) { parent[a] = a; return a; }
      while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; }
      return a;
    }
    function union(a, b) {
      const ra = find(a), rb = find(b);
      if (ra !== rb) parent[ra] = rb;
    }

    model.parts.forEach(function (p) { pinsOf(p).forEach(function (pt) { find(key(pt)); }); });
    model.wires.forEach(function (w) {
      /* a wire is a straight run; every grid point along it joins the same node */
      const dx = Math.sign(w.b[0] - w.a[0]), dy = Math.sign(w.b[1] - w.a[1]);
      const n = Math.max(Math.abs(w.b[0] - w.a[0]), Math.abs(w.b[1] - w.a[1]));
      let cur = [w.a[0], w.a[1]];
      find(key(cur));
      for (let i = 0; i < n; i++) {
        const nxt = [cur[0] + dx, cur[1] + dy];
        union(key(cur), key(nxt));
        cur = nxt;
      }
    });

    /* ground first, so it becomes node 0 and drops out of the unknowns */
    const gnd = model.parts.filter(function (p) { return p.kind === 'GND'; });
    let gndRoot = null;
    gnd.forEach(function (p) {
      const r = find(key(pinsOf(p)[0]));
      if (gndRoot === null) gndRoot = r; else union(r, gndRoot);
    });
    if (gndRoot !== null) gndRoot = find(gndRoot);

    const nodeOf = {};
    let next = 1;
    Object.keys(parent).forEach(function (k) {
      const r = find(k);
      if (nodeOf[r] === undefined) nodeOf[r] = (r === gndRoot) ? 0 : next++;
    });

    const probes = model.parts
      .filter(function (p) { return p.kind === 'OUT'; })
      .map(function (p) { return nodeOf[find(key(pinsOf(p)[0]))]; });

    const parts = model.parts
      .filter(function (p) { return p.kind !== 'GND' && p.kind !== 'OUT'; })
      .map(function (p) {
        const pins = plusFirst(p).map(function (pt) { return nodeOf[find(key(pt))]; });
        return { id: p.id, kind: p.kind, value: p.value, n1: pins[0], n2: pins[1], ac: p.ac };
      });

    return { parts: parts, probes: probes, nodeCount: next, hasGround: gndRoot !== null,
             nodeAt: function (pt) { const k = key(pt); return parent[k] === undefined ? null : nodeOf[find(k)]; } };
  }

  return { build: build, pinsOf: pinsOf, plusFirst: plusFirst };
})();

/* ---------------------------------------------------------------- MNA */
const MNA = (function () {

  /* Which parts need a current unknown of their own: voltage sources always, and
     inductors in DC (a short is a zero-volt source) and in transient. */
  function currentCarriers(parts, mode) {
    return parts.filter(function (p) {
      return p.kind === 'V' || (p.kind === 'L' && mode !== 'ac');
    });
  }

  function frame(net, mode) {
    const carriers = currentCarriers(net.parts, mode);
    const n = net.nodeCount - 1 + carriers.length;
    return { carriers: carriers, n: n, idxOf: function (p) { return net.nodeCount - 1 + carriers.indexOf(p); } };
  }

  function stampG(A, i, j, g) {
    /* i and j are node numbers; node 0 is ground and has no row */
    if (i > 0) A[i - 1][i - 1] = Lin.cadd(A[i - 1][i - 1], g);
    if (j > 0) A[j - 1][j - 1] = Lin.cadd(A[j - 1][j - 1], g);
    if (i > 0 && j > 0) {
      A[i - 1][j - 1] = Lin.csub(A[i - 1][j - 1], g);
      A[j - 1][i - 1] = Lin.csub(A[j - 1][i - 1], g);
    }
  }

  function stampCurrent(b, i, j, cur) {
    if (i > 0) b[i - 1] = Lin.csub(b[i - 1], cur);
    if (j > 0) b[j - 1] = Lin.cadd(b[j - 1], cur);
  }

  function problems(net) {
    if (!net.hasGround) return 'No ground. Every circuit needs one, or the node voltages have nothing to be measured against.';
    if (!net.parts.length) return 'Nothing to solve yet — place some components and wire them up.';
    return null;
  }

  /* ---- DC operating point ---- */
  function dc(net) {
    const bad = problems(net);
    if (bad) return { error: bad };
    const f = frame(net, 'dc');
    if (f.n === 0) return { error: 'Everything is tied to ground; there is nothing to solve for.' };
    const A = Lin.zeros(f.n);
    const b = [];
    for (let i = 0; i < f.n; i++) b.push([0, 0]);

    net.parts.forEach(function (p) {
      if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
      else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
      else if (p.kind === 'C') { /* open circuit at DC */ }
      else if (p.kind === 'V' || p.kind === 'L') {
        const k = f.idxOf(p);
        /* an inductor is a zero-volt source at DC */
        const volts = p.kind === 'V' ? p.value : 0;
        if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
        if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
        b[k] = [volts, 0];
      }
    });

    const x = Lin.solve(A, b);
    if (!x) return { error: 'The circuit is under-determined — usually a node connected to nothing, or two voltage sources in a loop.' };
    const v = [0];
    for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i][0]);
    const currents = {};
    f.carriers.forEach(function (p) { currents[p.id] = x[f.idxOf(p)][0]; });
    return { v: v, currents: currents };
  }

  /* ---- AC, one frequency ---- */
  function acAt(net, w) {
    const f = frame(net, 'ac');
    const A = Lin.zeros(f.n);
    const b = [];
    for (let i = 0; i < f.n; i++) b.push([0, 0]);

    net.parts.forEach(function (p) {
      if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
      else if (p.kind === 'C') stampG(A, p.n1, p.n2, [0, w * p.value]);
      else if (p.kind === 'L') stampG(A, p.n1, p.n2, Lin.cdiv([1, 0], [0, w * Math.max(p.value, 1e-15)]));
      else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
      else if (p.kind === 'V') {
        const k = f.idxOf(p);
        if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
        if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
        b[k] = [p.value, 0];
      }
    });

    const x = Lin.solve(A, b);
    if (!x) return null;
    const v = [[0, 0]];
    for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i]);
    return v;
  }

  function ac(net, f1, f2, points) {
    const bad = problems(net);
    if (bad) return { error: bad };
    if (!net.parts.some(function (p) { return p.kind === 'V' || p.kind === 'I'; })) {
      return { error: 'No source to sweep. Add a voltage or current source.' };
    }
    const out = [];
    for (let i = 0; i < points; i++) {
      const fq = Math.pow(10, Math.log10(f1) + i / (points - 1) * (Math.log10(f2) - Math.log10(f1)));
      const v = acAt(net, 2 * Math.PI * fq);
      if (!v) return { error: 'The circuit is under-determined at ' + fmtEng(fq, 'Hz') + '.' };
      out.push({ f: fq, v: v });
    }
    return { sweep: out };
  }

  /* ---- transient, backward Euler ----
     Backward Euler rather than trapezoidal: it is unconditionally stable and never
     rings on a step, so a learner watching an RC charge sees the physics rather than
     an artefact of the integrator. */
  function tran(net, tStop, h) {
    const bad = problems(net);
    if (bad) return { error: bad };
    const f = frame(net, 'tran');
    /* A step cap has to cost resolution, never span: clamping the count while
       keeping h shortened the simulation instead of coarsening it, so a run asked to
       cover five time constants quietly stopped at two and the curve looked as if it
       had settled somewhere it had not. */
    const MAX_STEPS = 4000;
    let steps = Math.max(2, Math.round(tStop / h));
    if (steps > MAX_STEPS) { h = tStop / MAX_STEPS; steps = MAX_STEPS; }
    const prevV = {};
    const prevI = {};
    net.parts.forEach(function (p) { prevV[p.id] = 0; prevI[p.id] = 0; });

    const times = [], volts = [];
    /* The initial condition, before any step. Backward Euler solves for the state at
       the *end* of a step, so without this the first sample already shows one step of
       charging and an RC curve appears not to start at zero. */
    const v0 = [];
    for (let i = 0; i < net.nodeCount; i++) v0.push(0);
    net.parts.forEach(function (p) {
      if (p.kind === 'V') { if (p.n1 > 0) v0[p.n1] = p.value; }
    });
    times.push(0);
    volts.push(v0);

    for (let s = 1; s <= steps; s++) {
      const t = s * h;
      const A = Lin.zeros(f.n);
      const b = [];
      for (let i = 0; i < f.n; i++) b.push([0, 0]);

      net.parts.forEach(function (p) {
        if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
        else if (p.kind === 'C') {
          /* companion: conductance C/h with a current source carrying the history */
          const g = Math.max(p.value, 1e-18) / h;
          stampG(A, p.n1, p.n2, [g, 0]);
          stampCurrent(b, p.n1, p.n2, [-g * prevV[p.id], 0]);
        } else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
        else if (p.kind === 'V' || p.kind === 'L') {
          const k = f.idxOf(p);
          if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
          if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
          if (p.kind === 'V') {
            b[k] = [p.value, 0];
          } else {
            /* inductor companion: v = (L/h)(i - i_prev) */
            const Lh = Math.max(p.value, 1e-15) / h;
            A[k][k] = Lin.csub(A[k][k], [Lh, 0]);
            b[k] = [-Lh * prevI[p.id], 0];
          }
        }
      });

      const x = Lin.solve(A, b);
      if (!x) return { error: 'The circuit is under-determined.' };
      const v = [0];
      for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i][0]);
      times.push(t);
      volts.push(v);

      net.parts.forEach(function (p) {
        if (p.kind === 'C') prevV[p.id] = v[p.n1] - v[p.n2];
        if (p.kind === 'L') prevI[p.id] = x[f.idxOf(p)][0];
      });
    }
    /* h may have been coarsened above, so report the one actually used */
    return { t: times, v: volts, h: h };
  }

  return { dc: dc, ac: ac, tran: tran, acAt: acAt };
})();

/* ---------------------------------------------------------------- editor
 *
 * A schematic canvas: pick a part, click to place it, drag to wire. Everything is
 * on a grid so a pin either meets a wire or it does not — no near-misses, and no
 * hunting for the one connection that was two pixels out.
 */
function createCircuit(root, opts) {
  opts = opts || {};
  const GRID = 26;
  const model = opts.model && opts.model.parts
    ? JSON.parse(JSON.stringify(opts.model))
    : { parts: [], wires: [] };
  let seq = model.parts.reduce(function (n, p) {
    const m = /^p(\d+)$/.exec(p.id);
    return m ? Math.max(n, +m[1] + 1) : n;
  }, 0);

  let tool = 'R';
  let sel = null;              /* selected part id */
  let wireFrom = null;         /* grid point a wire is being drawn from */
  let hover = null;
  let analysis = { mode: 'dc', node: 1, f1: 10, f2: 1e6, tstop: 5e-3 };
  let result = null;
  let disposed = false;

  root.innerHTML =
    '<div class="ckt">' +
      '<div class="ckt-bar">' +
        '<div class="ckt-tools">' +
          [['select', 'Select'], ['wire', 'Wire'], ['R', 'R'], ['C', 'C'], ['L', 'L'],
           ['V', 'V'], ['I', 'I'], ['GND', 'GND'], ['OUT', 'Probe']].map(function (t) {
            return '<button class="ckt-t" data-tool="' + t[0] + '" title="' + t[1] + '">' + t[1] + '</button>';
          }).join('') +
        '</div>' +
        '<span class="spacer"></span>' +
        '<button class="ckt-t" data-act="rotate" title="Rotate the selected part (R)">Rotate</button>' +
        '<button class="ckt-t" data-act="delete" title="Delete the selection (Del)">Delete</button>' +
        '<button class="ckt-t" data-act="clear">Clear</button>' +
      '</div>' +
      '<div class="ckt-main">' +
        '<div class="ckt-canvas"><canvas></canvas></div>' +
        '<div class="ckt-side">' +
          '<div class="ckt-panel" data-panel="part"></div>' +
          '<div class="ckt-panel">' +
            '<h4>Analysis</h4>' +
            '<div class="seg ckt-modes">' +
              '<button data-an="dc" class="active">Operating point</button>' +
              '<button data-an="ac">Frequency</button>' +
              '<button data-an="tran">Transient</button>' +
            '</div>' +
            '<div class="ckt-opts" data-opts></div>' +
            '<button class="btn success ckt-run">Solve</button>' +
          '</div>' +
          '<div class="ckt-out" data-out></div>' +
        '</div>' +
      '</div>' +
      '<div class="ckt-plot" data-plot hidden><canvas></canvas></div>' +
    '</div>';

  const cv = root.querySelector('.ckt-canvas canvas');
  const ctx = cv.getContext('2d');
  const plotWrap = root.querySelector('[data-plot]');
  const plotCv = plotWrap.querySelector('canvas');
  const outEl = root.querySelector('[data-out]');
  const partPanel = root.querySelector('[data-panel="part"]');
  const optsEl = root.querySelector('[data-opts]');

  function P() { return typeof Sandbox !== 'undefined' ? Sandbox.palette() : { ink: '#eee', dim: '#888', faint: '#555', line: '#333', accent: '#C7F751', blue: '#6E9BFF', amber: '#FFC66D', purple: '#A78BFA' }; }

  /* ---- geometry ---- */
  let originX = 2, originY = 2;
  function gx(x) { return (x - originX) * GRID + GRID; }
  function gy(y) { return (y - originY) * GRID + GRID; }
  function toGrid(px, py) {
    return [Math.round((px - GRID) / GRID) + originX, Math.round((py - GRID) / GRID) + originY];
  }

  function partAt(pt) {
    return model.parts.find(function (p) {
      if (p.kind === 'GND') return p.x === pt[0] && p.y === pt[1];
      return p.x === pt[0] && p.y === pt[1];
    });
  }

  /* ---- drawing ---- */
  function drawPart(p, colour) {
    const x = gx(p.x), y = gy(p.y);
    const k = PART_KINDS[p.kind];
    ctx.strokeStyle = colour;
    ctx.fillStyle = colour;
    ctx.lineWidth = 1.8;
    ctx.lineCap = 'round';

    if (p.kind === 'OUT') {
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x, y - 5); ctx.lineTo(x, y - 13);
      ctx.stroke();
      ctx.font = '10px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('out', x, y - 18);
      return;
    }

    if (p.kind === 'GND') {
      ctx.beginPath();
      ctx.moveTo(x, y); ctx.lineTo(x, y + 8);
      ctx.moveTo(x - 9, y + 8); ctx.lineTo(x + 9, y + 8);
      ctx.moveTo(x - 5, y + 12); ctx.lineTo(x + 5, y + 12);
      ctx.moveTo(x - 2, y + 16); ctx.lineTo(x + 2, y + 16);
      ctx.stroke();
      return;
    }

    ctx.save();
    ctx.translate(x, y);
    if (p.rot) ctx.rotate(Math.PI / 2);
    const L = GRID;                       /* pin-to-pin half span */
    ctx.beginPath();
    if (p.kind === 'R') {
      ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
      for (let i = 0; i < 6; i++) ctx.lineTo(-13 + (i + 0.5) * 26 / 6, (i % 2 ? 6 : -6));
      ctx.lineTo(13, 0); ctx.lineTo(L, 0);
      ctx.stroke();
    } else if (p.kind === 'C') {
      ctx.moveTo(-L, 0); ctx.lineTo(-4, 0);
      ctx.moveTo(4, 0); ctx.lineTo(L, 0);
      ctx.moveTo(-4, -9); ctx.lineTo(-4, 9);
      ctx.moveTo(4, -9); ctx.lineTo(4, 9);
      ctx.stroke();
    } else if (p.kind === 'L') {
      ctx.moveTo(-L, 0); ctx.lineTo(-14, 0);
      for (let i = 0; i < 4; i++) ctx.arc(-14 + 7 + i * 7, 0, 3.5, Math.PI, 0, false);
      ctx.lineTo(L, 0);
      ctx.stroke();
    } else {
      /* V and I share a circle; the marking inside says which */
      ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
      ctx.moveTo(11, 0); ctx.lineTo(L, 0);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, 11, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      if (p.kind === 'V') {
        /* + on the terminal the solver treats as positive */
        ctx.moveTo(3, -4); ctx.lineTo(9, -4);
        ctx.moveTo(6, -7); ctx.lineTo(6, -1);
        ctx.moveTo(-9, -4); ctx.lineTo(-3, -4);
      } else {
        ctx.moveTo(0, 7); ctx.lineTo(0, -7);
        ctx.moveTo(-3.5, -3.5); ctx.lineTo(0, -7); ctx.lineTo(3.5, -3.5);
      }
      ctx.stroke();
    }
    ctx.restore();

    /* value label, clear of the body */
    ctx.font = '10.5px ui-monospace, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = colour;
    const lab = p.kind + (p.id.replace('p', '')) + '  ' + fmtEng(p.value, k.unit);
    if (p.rot) ctx.fillText(lab, x + 34, y);
    else ctx.fillText(lab, x, y - 17);
  }

  function paint() {
    if (disposed) return;
    const box = cv.parentElement.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(320, Math.round(box.width));
    const h = Math.max(260, Math.round(box.height));
    if (cv.width !== w * dpr || cv.height !== h * dpr) {
      cv.width = w * dpr; cv.height = h * dpr;
      cv.style.width = w + 'px'; cv.style.height = h + 'px';
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const pal = P();
    ctx.clearRect(0, 0, w, h);

    /* grid dots */
    ctx.fillStyle = pal.faint;
    for (let X = GRID; X < w; X += GRID) {
      for (let Y = GRID; Y < h; Y += GRID) {
        ctx.globalAlpha = 0.5;
        ctx.fillRect(X - 0.5, Y - 0.5, 1, 1);
      }
    }
    ctx.globalAlpha = 1;

    /* wires */
    ctx.strokeStyle = pal.dim;
    ctx.lineWidth = 2;
    model.wires.forEach(function (wr) {
      ctx.beginPath();
      ctx.moveTo(gx(wr.a[0]), gy(wr.a[1]));
      ctx.lineTo(gx(wr.b[0]), gy(wr.b[1]));
      ctx.stroke();
    });

    /* junction dots where three or more things meet */
    const count = {};
    function bump(pt) { const k = pt[0] + ',' + pt[1]; count[k] = (count[k] || 0) + 1; }
    model.wires.forEach(function (wr) { bump(wr.a); bump(wr.b); });
    model.parts.forEach(function (p) { Netlist.pinsOf(p).forEach(bump); });
    ctx.fillStyle = pal.dim;
    Object.keys(count).forEach(function (k) {
      if (count[k] < 3) return;
      const xy = k.split(',').map(Number);
      ctx.beginPath();
      ctx.arc(gx(xy[0]), gy(xy[1]), 3, 0, Math.PI * 2);
      ctx.fill();
    });

    /* parts */
    model.parts.forEach(function (p) {
      drawPart(p, p.id === sel ? pal.accent : pal.ink);
    });

    /* the wire being drawn */
    if (wireFrom && hover) {
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = pal.accent;
      ctx.beginPath();
      ctx.moveTo(gx(wireFrom[0]), gy(wireFrom[1]));
      const straight = Math.abs(hover[0] - wireFrom[0]) > Math.abs(hover[1] - wireFrom[1])
        ? [hover[0], wireFrom[1]] : [wireFrom[0], hover[1]];
      ctx.lineTo(gx(straight[0]), gy(straight[1]));
      ctx.stroke();
      ctx.restore();
    }

    /* DC answers, written on the schematic where they belong */
    if (result && result.kind === 'dc' && result.net) {
      ctx.font = '10.5px ui-monospace, monospace';
      ctx.textAlign = 'left';
      const seen = {};
      model.parts.forEach(function (p) {
        Netlist.pinsOf(p).forEach(function (pt) {
          const n = result.net.nodeAt(pt);
          if (n === null || n === 0 || seen[n]) return;
          seen[n] = 1;
          ctx.fillStyle = pal.accent;
          ctx.fillText(fmtEng(result.v[n], 'V'), gx(pt[0]) + 6, gy(pt[1]) - 8);
        });
      });
    }
  }

  /* ---- panels ---- */
  function paintPart() {
    const p = model.parts.find(function (q) { return q.id === sel; });
    if (!p || p.kind === 'GND' || p.kind === 'OUT') {
      partPanel.innerHTML = '<h4>Component</h4><p class="ckt-hint">' +
        (tool === 'wire' ? 'Click a pin, then click where the wire should end.'
          : tool === 'select' ? 'Click a component to select it.'
          : 'Click the grid to place a ' + PART_KINDS[tool].name.toLowerCase() + '.') + '</p>';
      return;
    }
    const k = PART_KINDS[p.kind];
    partPanel.innerHTML = '<h4>' + k.name + ' ' + esc2(p.id.replace('p', '')) + '</h4>' +
      '<label class="ckt-f"><span>Value (' + k.unit + ')</span>' +
      '<input data-val value="' + esc2(fmtEng(p.value, '').trim()) + '"></label>' +
      (p.kind === 'V' || p.kind === 'I'
        ? '<p class="ckt-hint">The + terminal is the ' + (p.rot ? 'top' : 'right') + ' pin. ' +
          'A frequency sweep drives it at this same amplitude, so set it to 1 for a plain transfer function.</p>' : '');
    const inp = partPanel.querySelector('[data-val]');
    inp.addEventListener('change', function () {
      p.value = parseEng(inp.value, p.value);
      changed();
      paintPart();
    });
  }
  function esc2(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }

  function paintOpts() {
    if (analysis.mode === 'ac') {
      optsEl.innerHTML =
        '<label class="ckt-f"><span>From</span><input data-f1 value="' + fmtEng(analysis.f1, 'Hz') + '"></label>' +
        '<label class="ckt-f"><span>To</span><input data-f2 value="' + fmtEng(analysis.f2, 'Hz') + '"></label>';
      optsEl.querySelector('[data-f1]').addEventListener('change', function (e) { analysis.f1 = Math.max(0.01, parseEng(e.target.value, analysis.f1)); });
      optsEl.querySelector('[data-f2]').addEventListener('change', function (e) { analysis.f2 = Math.max(1, parseEng(e.target.value, analysis.f2)); });
    } else if (analysis.mode === 'tran') {
      optsEl.innerHTML = '<label class="ckt-f"><span>Stop after</span><input data-ts value="' + fmtEng(analysis.tstop, 's') + '"></label>';
      optsEl.querySelector('[data-ts]').addEventListener('change', function (e) { analysis.tstop = Math.max(1e-9, parseEng(e.target.value, analysis.tstop)); });
    } else {
      optsEl.innerHTML = '<p class="ckt-hint">Solves the DC operating point and writes each node voltage onto the schematic.</p>';
    }
  }

  /* ---- solving ---- */
  function solve() {
    const net = Netlist.build(model);
    let r;
    if (analysis.mode === 'dc') r = MNA.dc(net);
    else if (analysis.mode === 'ac') r = MNA.ac(net, analysis.f1, analysis.f2, 220);
    else r = MNA.tran(net, analysis.tstop, analysis.tstop / 900);

    if (r.error) {
      result = null;
      plotWrap.hidden = true;
      outEl.innerHTML = '<div class="ckt-err">' + esc2(r.error) + '</div>';
      paint();
      return;
    }
    result = Object.assign({ kind: analysis.mode, net: net }, r);
    if (analysis.mode === 'dc') {
      plotWrap.hidden = true;
      const rows = [];
      for (let n = 1; n < net.nodeCount; n++) rows.push('<tr><td>node ' + n + '</td><td>' + fmtEng(r.v[n], 'V') + '</td></tr>');
      Object.keys(r.currents).forEach(function (id) {
        rows.push('<tr><td>' + id.replace('p', 'part ') + '</td><td>' + fmtEng(Math.abs(r.currents[id]), 'A') + '</td></tr>');
      });
      outEl.innerHTML = '<table class="ckt-tab">' + rows.join('') + '</table>';
    } else {
      plotWrap.hidden = false;
      const picks = [];
      for (let n = 1; n < net.nodeCount; n++) {
        picks.push('<button data-node="' + n + '"' + (n === analysis.node ? ' class="active"' : '') + '>node ' + n + '</button>');
      }
      outEl.innerHTML = '<div class="seg ckt-nodes">' + picks.join('') + '</div>';
      outEl.querySelectorAll('[data-node]').forEach(function (b) {
        b.addEventListener('click', function () { analysis.node = +b.dataset.node; solveRepaint(); });
      });
      paintPlot();
    }
    paint();
  }
  function solveRepaint() { paintPlot(); outEl.querySelectorAll('[data-node]').forEach(function (b) { b.classList.toggle('active', +b.dataset.node === analysis.node); }); }

  function paintPlot() {
    if (!result || typeof Sandbox === 'undefined') return;
    const box = plotCv.parentElement.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(320, Math.round(box.width)), h = 190;
    plotCv.width = w * dpr; plotCv.height = h * dpr;
    plotCv.style.width = w + 'px'; plotCv.style.height = h + 'px';
    const c = plotCv.getContext('2d');
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.min(analysis.node, result.net.nodeCount - 1);

    if (result.kind === 'ac') {
      const pts = result.sweep.map(function (s) {
        return [s.f, 20 * Math.log10(Math.max(Lin.cabs(s.v[n]), 1e-12))];
      });
      const ys = pts.map(function (p) { return p[1]; });
      const f = Sandbox.frame(c, w, h, {
        xRange: [analysis.f1, analysis.f2], yRange: [Math.min.apply(null, ys) - 4, Math.max.apply(null, ys) + 4],
        logX: true, xTicks: 5, yTicks: 4, margin: { l: 50, r: 14, t: 12, b: 26 },
        xLabel: function (x) { return x >= 1e6 ? (x / 1e6) + 'M' : x >= 1e3 ? (x / 1e3) + 'k' : String(Math.round(x)); },
      });
      f.line(pts, f.P.accent, 2);
      f.text('dB at node ' + n, f.x0 + 6, f.y0 + 13, f.P.faint);
      f.text('Hz', f.x1 - 6, f.y1 + 18, f.P.faint, 'right');
    } else {
      const pts = result.t.map(function (t, i) { return [t, result.v[i][n]]; });
      const ys = pts.map(function (p) { return p[1]; });
      const lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
      const pad = Math.max((hi - lo) * 0.12, 1e-6);
      const f = Sandbox.frame(c, w, h, {
        xRange: [0, result.t[result.t.length - 1]], yRange: [lo - pad, hi + pad],
        xTicks: 5, yTicks: 4, margin: { l: 50, r: 14, t: 12, b: 26 },
        xLabel: function (x) { return fmtEng(x, ''); },
      });
      f.line(pts, f.P.accent, 2);
      f.text('V at node ' + n, f.x0 + 6, f.y0 + 13, f.P.faint);
      f.text('seconds', f.x1 - 6, f.y1 + 18, f.P.faint, 'right');
    }
  }

  function changed() {
    result = null;
    plotWrap.hidden = true;
    if (opts.onChange) opts.onChange(JSON.parse(JSON.stringify(model)));
    paint();
  }

  /* ---- interaction ---- */
  cv.addEventListener('pointermove', function (e) {
    const r = cv.getBoundingClientRect();
    hover = toGrid(e.clientX - r.left, e.clientY - r.top);
    if (wireFrom) paint();
  });
  cv.addEventListener('pointerleave', function () { hover = null; if (wireFrom) paint(); });

  cv.addEventListener('pointerdown', function (e) {
    const r = cv.getBoundingClientRect();
    const pt = toGrid(e.clientX - r.left, e.clientY - r.top);

    if (tool === 'wire') {
      if (!wireFrom) { wireFrom = pt; paint(); return; }
      /* wires stay orthogonal: take the dominant direction */
      const end = Math.abs(pt[0] - wireFrom[0]) > Math.abs(pt[1] - wireFrom[1])
        ? [pt[0], wireFrom[1]] : [wireFrom[0], pt[1]];
      if (end[0] !== wireFrom[0] || end[1] !== wireFrom[1]) {
        model.wires.push({ a: wireFrom, b: end });
        changed();
      }
      wireFrom = null;
      paint();
      return;
    }

    if (tool === 'select') {
      const hit = partAt(pt);
      sel = hit ? hit.id : null;
      paintPart();
      paint();
      return;
    }

    /* placing: refuse to stack two parts on one cell */
    if (partAt(pt)) { sel = partAt(pt).id; paintPart(); paint(); return; }
    const kind = tool;
    const p = { id: 'p' + (seq++), kind: kind, x: pt[0], y: pt[1], rot: 0,
                value: PART_KINDS[kind].def };
    model.parts.push(p);
    sel = p.id;
    changed();
    paintPart();
  });

  function onKey(e) {
    if (e.target && /input|textarea/i.test(e.target.tagName)) return;
    if (e.key === 'Delete' || e.key === 'Backspace') { doDelete(); e.preventDefault(); }
    else if (e.key === 'r' || e.key === 'R') { doRotate(); }
    else if (e.key === 'Escape') { wireFrom = null; paint(); }
  }
  document.addEventListener('keydown', onKey);

  function doRotate() {
    const p = model.parts.find(function (q) { return q.id === sel; });
    if (!p || p.kind === 'GND' || p.kind === 'OUT') return;
    p.rot = p.rot ? 0 : 1;
    changed();
    paintPart();
  }
  function doDelete() {
    if (!sel) return;
    model.parts = model.parts.filter(function (p) { return p.id !== sel; });
    sel = null;
    changed();
    paintPart();
  }

  root.querySelectorAll('[data-tool]').forEach(function (b) {
    b.addEventListener('click', function () {
      tool = b.dataset.tool;
      wireFrom = null;
      root.querySelectorAll('[data-tool]').forEach(function (o) { o.classList.toggle('on', o === b); });
      paintPart();
      paint();
    });
  });
  root.querySelector('[data-act="rotate"]').addEventListener('click', doRotate);
  root.querySelector('[data-act="delete"]').addEventListener('click', doDelete);
  root.querySelector('[data-act="clear"]').addEventListener('click', function () {
    model.parts = []; model.wires = []; sel = null; changed(); paintPart();
  });
  root.querySelectorAll('[data-an]').forEach(function (b) {
    b.addEventListener('click', function () {
      analysis.mode = b.dataset.an;
      root.querySelectorAll('[data-an]').forEach(function (o) { o.classList.toggle('active', o === b); });
      paintOpts();
    });
  });
  root.querySelector('.ckt-run').addEventListener('click', solve);

  let ro = null;
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(function () { paint(); if (result && !plotWrap.hidden) paintPlot(); });
    ro.observe(cv.parentElement);
  }

  root.querySelector('[data-tool="R"]').classList.add('on');
  paintPart();
  paintOpts();
  paint();

  return {
    getModel: function () { return JSON.parse(JSON.stringify(model)); },
    solve: solve,
    dispose: function () {
      disposed = true;
      document.removeEventListener('keydown', onKey);
      if (ro) ro.disconnect();
      root.innerHTML = '';
    },
  };
}

/* a worked example, so the canvas is never empty on first open */
const CIRCUIT_EXAMPLE = {
  parts: [
    { id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5, ac: 1 },
    { id: 'p1', kind: 'R', x: 6, y: 4, rot: 0, value: 1000 },
    { id: 'p2', kind: 'C', x: 9, y: 6, rot: 1, value: 1e-7 },
    { id: 'p3', kind: 'GND', x: 3, y: 9 },
    { id: 'p4', kind: 'GND', x: 9, y: 9 },
  ],
  wires: [
    { a: [3, 5], b: [3, 4] },
    { a: [3, 4], b: [5, 4] },
    { a: [7, 4], b: [9, 4] },
    { a: [9, 4], b: [9, 5] },
    { a: [3, 7], b: [3, 9] },
    { a: [9, 7], b: [9, 9] },
  ],
};

/* ---------------------------------------------------------------- grading
 *
 * A circuit exercise is checked the way a code lab is: the learner's work is run,
 * and each check either raises or does not. The check writes ordinary JavaScript
 * against a small API, so "the corner is at 1 kHz" is expressed as the measurement
 * it actually is rather than as a shape the schematic has to match. Two learners
 * who build different but equally correct filters both pass.
 */
function circuitContext(model) {
  const net = Netlist.build(model);
  const cache = {};

  function need(what) {
    if (!net.hasGround) throw new Error('Add a ground before ' + what + ' can mean anything.');
  }
  function out() {
    if (!net.probes.length) throw new Error('Place a probe on the node you are treating as the output.');
    if (net.probes.length > 1) throw new Error('There is more than one probe; the checks read a single output.');
    return net.probes[0];
  }

  return {
    net: net,
    /* how many of a kind the learner used */
    count: function (kind) { return net.parts.filter(function (p) { return p.kind === kind; }).length; },
    values: function (kind) { return net.parts.filter(function (p) { return p.kind === kind; }).map(function (p) { return p.value; }); },
    outNode: out,
    nodeCount: function () { return net.nodeCount; },

    /* DC operating point; throws with the solver's own message on a bad circuit */
    dc: function () {
      need('a DC answer');
      if (!cache.dc) {
        const r = MNA.dc(net);
        if (r.error) throw new Error(r.error);
        cache.dc = r;
      }
      return cache.dc;
    },
    vout: function () { return this.dc().v[out()]; },

    /* magnitude and phase of the probed node at one frequency */
    gain: function (f) {
      need('a frequency response');
      const v = MNA.acAt(net, 2 * Math.PI * f);
      if (!v) throw new Error('The circuit is under-determined at ' + fmtEng(f, 'Hz') + '.');
      return Lin.cabs(v[out()]);
    },
    phase: function (f) {
      need('a frequency response');
      const v = MNA.acAt(net, 2 * Math.PI * f);
      if (!v) throw new Error('The circuit is under-determined at ' + fmtEng(f, 'Hz') + '.');
      return Math.atan2(v[out()][1], v[out()][0]) * 180 / Math.PI;
    },
    /* the -3 dB point, found by bisection on the measured response */
    corner: function (lo, hi) {
      need('a corner frequency');
      const self = this;
      const ref = self.gain(lo);
      const target = ref / Math.SQRT2;
      let a = lo, b = hi;
      for (let i = 0; i < 60; i++) {
        const mid = Math.sqrt(a * b);
        if (self.gain(mid) > target) a = mid; else b = mid;
      }
      return Math.sqrt(a * b);
    },
    /* the probed node over time */
    step: function (tstop) {
      need('a transient');
      const r = MNA.tran(net, tstop, tstop / 600);
      if (r.error) throw new Error(r.error);
      const n = out();
      return { t: r.t, v: r.v.map(function (row) { return row[n]; }) };
    },

    assert: function (cond, msg) { if (!cond) throw new Error(msg || 'Assertion failed'); },
    close: function (got, want, tolFrac, msg) {
      const tol = Math.abs(want * (tolFrac === undefined ? 0.05 : tolFrac));
      if (!(Math.abs(got - want) <= tol)) {
        throw new Error((msg ? msg + ' — ' : '') + 'measured ' + Number(got).toPrecision(4) +
          ', expected ' + Number(want).toPrecision(4));
      }
    },
    fmt: fmtEng,
  };
}

/* Run every check of a circuit exercise against one schematic. */
function runCircuitChecks(model, checks) {
  return (checks || []).map(function (c) {
    let ctx;
    try { ctx = circuitContext(model); }
    catch (e) { return { name: c.name, pass: false, message: String(e && e.message || e) }; }
    try {
      const fn = new Function('c', '"use strict";\n' + c.code);
      fn(ctx);
      return { name: c.name, pass: true };
    } catch (e) {
      return { name: c.name, pass: false, message: String((e && e.message) || e) };
    }
  });
}
