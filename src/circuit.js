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

  /* ---- parts that are a resistance the learner does not type ----
   *
   * A switch, a light-dependent resistor and a thermistor are all the same thing to
   * this solver: a resistance whose number comes from somewhere other than the value
   * box. Netlist.build works that number out before stamping, so the matrix never
   * learns that anything moved — no Newton loop, no iteration, no pretending. What
   * makes them worth having is that the "somewhere else" is a state you can click or
   * a slider you can drag, and the circuit answers.
   *
   * `state` is the extra data a kind carries beyond `value`, copied onto the part
   * when it is placed. */
  SW: { name: 'Switch', unit: 'Ω', def: 0, pins: 2, sym: 'SW', state: { closed: false } },
  LDR: { name: 'Light sensor', unit: 'Ω', def: 10000, pins: 2, sym: 'LDR', state: { gamma: 0.7 },
         senses: 'lux' },
  NTC: { name: 'Thermistor', unit: 'Ω', def: 10000, pins: 2, sym: 'NTC', state: { beta: 3950 },
         senses: 'tempC' },
  POT: { name: 'Potentiometer', unit: 'Ω', def: 10000, pins: 3, sym: 'POT', state: { wiper: 0.5 } },

  /* ---- readouts ----
   * LAMP and METER are resistances too, and say so. BAR touches nothing: it reads a
   * node the way the probe does and draws the answer. */
  LAMP: { name: 'Lamp', unit: 'Ω', def: 220, pins: 2, sym: 'LAMP', state: { pnom: 0.25 } },
  METER: { name: 'Ammeter', unit: 'Ω', def: 0.1, pins: 2, sym: 'METER' },
  BAR: { name: 'Bar display', unit: 'V', def: 5, pins: 1, sym: 'BAR' },
};

/* The simulated world the sensors sense. Not part of the schematic — a circuit is
   the same circuit in the dark and in the light — so it is passed in beside the
   model and defaulted here for every caller that has no opinion. */
const ENV_DEFAULT = { lux: 200, tempC: 25 };

/* Switch resistances. Open is a very large resistance rather than a deleted branch:
   removing the branch would leave whatever hangs off the far side connected to
   nothing, and the solver reports that as an under-determined circuit — a baffling
   thing to show someone whose only crime was opening a switch. At 100 MΩ the far
   side still has a defined voltage, and the leakage through it (50 nA from a 5 V
   supply) is smaller than any real switch's. */
const SW_ON = 0.05, SW_OFF = 1e8;

/* How a sensor turns a simulated quantity into ohms. Both are the textbook models,
   named and parameterised in the component panel so the learner reads the curve
   rather than trusting it. Getting the SIGN of either one backwards would teach
   something false, so each is written to make the direction obvious:
   more light -> less resistance, more heat -> less resistance. */
const Sensors = {
  /* photoresistor power law: R = R10 * (10 lx / E)^gamma.
     gamma ~ 0.7 is a typical CdS cell. 10 lx is the stated reference point because
     a datasheet quotes one, and quoting it makes R10 a number you can look up. */
  ldr: function (r10, gamma, lux) {
    const E = Math.min(Math.max(lux, 0.01), 1e5);
    const g = Math.min(Math.max(gamma, 0.05), 3);
    return Math.min(Math.max(Math.max(r10, 1) * Math.pow(10 / E, g), 1), 1e9);
  },
  /* beta (B-parameter) model: R = R25 * exp(B * (1/T - 1/298.15)), T in kelvin.
     B > 0 makes the exponent negative as T rises, so the resistance falls — which is
     what the N in NTC means. It is a two-point fit, good to a few percent over a
     50 K span and no better; the Steinhart-Hart form is what you use when you need
     more, and this panel says so. */
  ntc: function (r25, beta, tempC) {
    const T = Math.max(tempC + 273.15, 1);
    const B = Math.min(Math.max(beta, 1), 20000);
    return Math.min(Math.max(Math.max(r25, 1) * Math.exp(B * (1 / T - 1 / 298.15)), 0.01), 1e12);
  },
};

/* The one resistance a dynamic part is worth, right now. Returns null for anything
   the solver already understands on its own. */
function ohmsOf(p, env) {
  const e = env || ENV_DEFAULT;
  if (p.kind === 'SW') return p.closed ? SW_ON : SW_OFF;
  if (p.kind === 'LDR') return Sensors.ldr(p.value, p.gamma === undefined ? 0.7 : p.gamma, e.lux);
  if (p.kind === 'NTC') return Sensors.ntc(p.value, p.beta === undefined ? 3950 : p.beta, e.tempC);
  if (p.kind === 'LAMP') return Math.max(p.value, 1e-3);
  if (p.kind === 'METER') return Math.max(p.value, 1e-6);
  return null;
}

/* Wiper 0..1 -> the two track resistances either side of it. Clamped away from a
   dead short at each end so a wiper wound fully over does not put a zero-ohm branch
   in the matrix. */
function potSplit(p) {
  const total = Math.max(p.value, 1e-3);
  const w = Math.min(Math.max(p.wiper === undefined ? 0.5 : p.wiper, 0), 1);
  return [Math.max(total * w, 1e-3), Math.max(total * (1 - w), 1e-3)];
}

/* engineering notation both ways, because 1e-6 is not how anyone says a microfarad */
function fmtEng(v, unit) {
  if (v === 0) return '0 ' + unit;
  const a = Math.abs(v);
  const P = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'],
             [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p']];
  for (const [mul, pre] of P) {
    if (a >= mul * 0.999) {
      const s = (v / mul);
      let txt = Math.abs(s) >= 100 ? s.toFixed(0)
        : Math.abs(s) >= 10 ? s.toFixed(1) : s.toFixed(2);
      /* Trim only the zeros that follow a decimal point. Trimming unconditionally
         ate the zeros of an integer, so a 100 pF capacitor was labelled 1 pF and a
         200 ohm resistor 2 ohm — on the schematic the learner reads while working
         out why the answer is a hundred times off. */
      if (txt.indexOf('.') >= 0) txt = txt.replace(/0+$/, '').replace(/\.$/, '');
      return txt + ' ' + pre + unit;
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
  /* Pin count comes from the registry rather than from a list of kind names here, so
     a new kind gets its geometry by declaring how many pins it has. One pin sits on
     its cell; two span it; the third — so far only a potentiometer's wiper — leaves
     the body at right angles to the track, one cell out, which is where the arrow in
     the symbol points. The first two pins of a three-pin part are exactly where a
     two-pin part's pins would be, so nothing that already worked has moved. */
  function pinsOf(p) {
    const k = PART_KINDS[p.kind];
    const n = k ? k.pins : 2;
    if (n === 1) return [[p.x, p.y]];
    const span = p.rot ? [[p.x, p.y - 1], [p.x, p.y + 1]] : [[p.x - 1, p.y], [p.x + 1, p.y]];
    if (n < 3) return span;
    span.push(p.rot ? [p.x + 1, p.y] : [p.x, p.y - 1]);
    return span;
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
  function build(model, env) {
    const world = Object.assign({}, ENV_DEFAULT, env || {});
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

    /* A bar display is deliberately left out of this pass. Every other pin creates a
       node whether or not anything else reaches it, which is right for a part that
       carries current — but a display dropped on an empty cell would then be a node
       with nothing stamped on it, and the solver would call the whole circuit
       under-determined. A readout must never be able to break the answer it exists to
       show, so a bar takes the node it lands on and creates none. */
    model.parts.forEach(function (p) {
      if (p.kind === 'BAR') return;
      pinsOf(p).forEach(function (pt) { find(key(pt)); });
    });
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

    /* Everything the learner placed, in the order they placed it, with GND and OUT
       left out exactly as before — this is what `count` and `values` answer from, so
       a potentiometer that stamps as two resistors is still one potentiometer and
       not two resistors. */
    const placed = [];
    /* What the solver is given. Every entry here is an R, C, L, V or I with a plain
       number in `value`: a switch state and a sensor reading against the simulated
       environment are resolved HERE, before any stamping, and the matrix downstream
       stays linear and has no idea anything varies. */
    const parts = [];
    /* Parts that read the solution instead of taking part in it, plus the resolved
       ohms of the ones that do both, so the editor can label them without re-deriving
       any of this. */
    const readouts = [];

    model.parts.forEach(function (p) {
      if (p.kind === 'GND' || p.kind === 'OUT') return;
      if (p.kind === 'BAR') {
        /* look the node up without creating one — see the pass above */
        const kk = key(pinsOf(p)[0]);
        placed.push({ id: p.id, kind: p.kind, value: p.value });
        readouts.push({ id: p.id, kind: 'BAR', full: p.value,
                        node: parent[kk] === undefined ? null : nodeOf[find(kk)] });
        return;
      }
      const pins = plusFirst(p).map(function (pt) { return nodeOf[find(key(pt))]; });
      placed.push({ id: p.id, kind: p.kind, value: p.value });

      if (p.kind === 'POT') {
        const rr = potSplit(p);
        /* two resistances sharing the wiper node: pin A to wiper, wiper to pin B */
        parts.push({ id: p.id + '#a', kind: 'R', value: rr[0], n1: pins[0], n2: pins[2], of: p.id });
        parts.push({ id: p.id + '#b', kind: 'R', value: rr[1], n1: pins[2], n2: pins[1], of: p.id });
        readouts.push({ id: p.id, kind: 'POT', nodes: pins, ohms: rr[0] + rr[1], split: rr });
        return;
      }
      const ohms = ohmsOf(p, world);
      if (ohms !== null) {
        parts.push({ id: p.id, kind: 'R', value: ohms, n1: pins[0], n2: pins[1], of: p.id, was: p.kind });
        readouts.push({ id: p.id, kind: p.kind, nodes: pins, ohms: ohms });
        return;
      }
      parts.push({ id: p.id, kind: p.kind, value: p.value, n1: pins[0], n2: pins[1], ac: p.ac });
    });

    return { parts: parts, probes: probes, nodeCount: next, hasGround: gndRoot !== null,
             placed: placed, readouts: readouts, env: world,
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

/* ---------------------------------------------------------------- symbols
 *
 * The schematic editor draws parts small, rotated, and only for the kinds the solver
 * understands. A drill needs the opposite: one symbol, large, centred, and a
 * vocabulary wider than the solver's — a learner has to recognise a transistor long
 * before anything here can simulate one.
 *
 * So this is a separate table on purpose. Adding a symbol here teaches it; it does
 * not claim the solver can do anything with it.
 */
const Symbols = (function () {
  const DEF = {};
  function define(id, name, draw) { DEF[id] = { id: id, name: name, draw: draw }; }
  function get(id) { return DEF[id] || null; }
  function ids() { return Object.keys(DEF); }

  /* Every draw() works in a box from (-60,-40) to (60,40); the caller scales. */
  define('R', 'Resistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    const n = 6, w = 60 / n;
    for (let i = 0; i < n; i++) c.lineTo(-30 + (i + 0.5) * w, i % 2 ? 17 : -17);
    c.lineTo(30, 0); c.lineTo(60, 0);
  });

  define('C', 'Capacitor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-9, 0);
    c.moveTo(9, 0); c.lineTo(60, 0);
    c.moveTo(-9, -26); c.lineTo(-9, 26);
    c.moveTo(9, -26); c.lineTo(9, 26);
  });

  define('L', 'Inductor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-32, 0);
    for (let i = 0; i < 4; i++) c.arc(-32 + 8 + i * 16, 0, 8, Math.PI, 0, false);
    c.lineTo(60, 0);
  });

  define('D', 'Diode', function (c) {
    c.moveTo(-60, 0); c.lineTo(-16, 0);
    c.moveTo(-16, -20); c.lineTo(-16, 20); c.lineTo(18, 0); c.closePath();
    c.moveTo(18, -20); c.lineTo(18, 20);
    c.moveTo(18, 0); c.lineTo(60, 0);
  });

  define('LED', 'LED', function (c) {
    c.moveTo(-60, 0); c.lineTo(-16, 0);
    c.moveTo(-16, -20); c.lineTo(-16, 20); c.lineTo(18, 0); c.closePath();
    c.moveTo(18, -20); c.lineTo(18, 20);
    c.moveTo(18, 0); c.lineTo(60, 0);
    /* the two arrows that separate an LED from an ordinary diode */
    for (const dx of [0, 15]) {
      c.moveTo(2 + dx, -26); c.lineTo(16 + dx, -40);
      c.moveTo(16 + dx, -40); c.lineTo(9 + dx, -38);
      c.moveTo(16 + dx, -40); c.lineTo(14 + dx, -33);
    }
  });

  define('GND', 'Ground', function (c) {
    c.moveTo(0, -30); c.lineTo(0, 0);
    c.moveTo(-34, 0); c.lineTo(34, 0);
    c.moveTo(-21, 13); c.lineTo(21, 13);
    c.moveTo(-9, 26); c.lineTo(9, 26);
  });

  define('V', 'Voltage source', function (c) {
    c.arc(0, 0, 30, 0, Math.PI * 2);
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    c.moveTo(30, 0); c.lineTo(60, 0);
    c.moveTo(-15, -9); c.lineTo(-3, -9);
    c.moveTo(-9, -15); c.lineTo(-9, -3);
    c.moveTo(3, -9); c.lineTo(15, -9);
  });

  define('BATT', 'Battery', function (c) {
    c.moveTo(-60, 0); c.lineTo(-18, 0);
    c.moveTo(-18, -26); c.lineTo(-18, 26);
    c.moveTo(-6, -13); c.lineTo(-6, 13);
    c.moveTo(6, -26); c.lineTo(6, 26);
    c.moveTo(18, -13); c.lineTo(18, 13);
    c.moveTo(18, 0); c.lineTo(60, 0);
  });

  define('I', 'Current source', function (c) {
    c.arc(0, 0, 30, 0, Math.PI * 2);
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    c.moveTo(30, 0); c.lineTo(60, 0);
    c.moveTo(0, 16); c.lineTo(0, -16);
    c.moveTo(-7, -8); c.lineTo(0, -17); c.lineTo(7, -8);
  });

  define('NPN', 'NPN transistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-14, 0);          /* base lead */
    c.moveTo(-14, -28); c.lineTo(-14, 28);       /* base bar */
    c.moveTo(-14, -14); c.lineTo(22, -34);       /* collector */
    c.lineTo(22, -60);
    c.moveTo(-14, 14); c.lineTo(22, 34);         /* emitter */
    c.lineTo(22, 60);
    /* the emitter arrow, pointing out — this is what makes it NPN */
    c.moveTo(9, 20); c.lineTo(22, 34); c.lineTo(7, 31);
  });

  define('PNP', 'PNP transistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-14, 0);
    c.moveTo(-14, -28); c.lineTo(-14, 28);
    c.moveTo(-14, -14); c.lineTo(22, -34);
    c.lineTo(22, -60);
    c.moveTo(-14, 14); c.lineTo(22, 34);
    c.lineTo(22, 60);
    /* the arrow points IN at the base, which is the whole difference */
    c.moveTo(-1, 8); c.lineTo(-14, 14); c.lineTo(-3, 22);
  });

  define('SW', 'Switch', function (c) {
    c.moveTo(-60, 0); c.lineTo(-24, 0);
    c.moveTo(-24, 0); c.lineTo(20, -24);
    c.moveTo(24, 0); c.lineTo(60, 0);
    c.arc(-24, 0, 4, 0, Math.PI * 2);
    c.moveTo(28, 0); c.arc(24, 0, 4, 0, Math.PI * 2);
  });

  define('OPAMP', 'Op-amp', function (c) {
    c.moveTo(-26, -38); c.lineTo(-26, 38); c.lineTo(34, 0); c.closePath();
    c.moveTo(-60, -19); c.lineTo(-26, -19);
    c.moveTo(-60, 19); c.lineTo(-26, 19);
    c.moveTo(34, 0); c.lineTo(60, 0);
    c.moveTo(-21, -24); c.lineTo(-9, -24);      /* + */
    c.moveTo(-15, -30); c.lineTo(-15, -18);
    c.moveTo(-21, 24); c.lineTo(-9, 24);        /* - */
  });

  /* Paint one symbol into a canvas, sized to it and centred. */
  function paint(canvas, id, colour) {
    const spec = DEF[id];
    if (!canvas || !spec) return;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 200, h = canvas.clientHeight || 130;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const scale = Math.min(w / 150, h / 110);
    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.scale(scale, scale);
    ctx.strokeStyle = colour || '#EDEFF3';
    ctx.lineWidth = 3.4 / scale * Math.max(scale, 0.6);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    spec.draw(ctx);
    ctx.stroke();
    ctx.restore();
  }

  return { define: define, get: get, ids: ids, paint: paint, all: DEF };
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
  /* The viewport. `s` is the zoom, `px`/`py` are the world-pixel coordinates of the
     top-left corner of what you can see. Every screen<->grid conversion goes through
     it, so there is one place that knows where things are. */
  let view = { s: 1, px: 0, py: 0 };
  let selIds = new Set();      /* selected part ids */
  let drag = null;             /* a move in progress */
  let marquee = null;          /* a rubber-band selection in progress */
  let panFrom = null;          /* a pan in progress */
  let wireFrom = null;         /* grid point a wire is being drawn from */
  let hover = null;
  let analysis = { mode: 'dc', node: 1, f1: 10, f2: 1e6, tstop: 5e-3 };
  let result = null;
  let disposed = false;

  /* A question that shows a circuit wants the drawing and nothing else — no tools,
     no analysis panel, nothing to click. Same painter, so a diagram can never drift
     from what the editor would show for the same model. */
  if (opts.readOnly) {
    root.innerHTML = '<div class="ckt ckt-ro"><div class="ckt-main">' +
      '<div class="ckt-canvas"><canvas></canvas></div></div></div>';
  } else {
  root.innerHTML =
    '<div class="ckt">' +
      '<div class="ckt-bar">' +
        '<div class="ckt-tools">' +
          [['select', 'Select', 'Select and move parts'], ['wire', 'Wire', 'Draw a wire'],
           ['R', 'R', 'Resistor'], ['C', 'C', 'Capacitor'], ['L', 'L', 'Inductor'],
           ['V', 'V', 'Voltage source'], ['I', 'I', 'Current source'],
           ['GND', 'GND', 'Ground'], ['OUT', 'Probe', 'Mark the output node'],
           ['SW', 'SW', 'Switch — click it on the canvas to open and close it'],
           ['LDR', 'LDR', 'Light sensor — resistance falls as light rises'],
           ['NTC', 'NTC', 'Thermistor — resistance falls as temperature rises'],
           ['POT', 'POT', 'Potentiometer — three pins, a wiper along the track'],
           ['LAMP', 'Lamp', 'Indicator lamp — a resistance that lights with the power in it'],
           ['METER', 'Meter', 'Ammeter — reads the current through it'],
           ['BAR', 'Bar', 'Bar display — reads the node it sits on']].map(function (t) {
            return '<button class="ckt-t" data-tool="' + t[0] + '" title="' + t[2] + '">' + t[1] + '</button>';
          }).join('') +
        '</div>' +
        '<span class="spacer"></span>' +
        '<button class="ckt-t" data-act="zoomout" title="Zoom out (-)">−</button>' +
        '<button class="ckt-t" data-act="zoomin" title="Zoom in (+)">+</button>' +
        '<button class="ckt-t" data-act="fit" title="Fit the drawing to the window (0)">Fit</button>' +
        '<button class="ckt-t" data-act="rotate" title="Rotate the selection (R)">Rotate</button>' +
        '<button class="ckt-t" data-act="delete" title="Delete the selection (Del)">Delete</button>' +
        '<button class="ckt-t" data-act="clear">Clear</button>' +
      '</div>' +
      '<div class="ckt-main">' +
        '<div class="ckt-canvas"><canvas></canvas></div>' +
        '<div class="ckt-side">' +
          '<div class="ckt-panel" data-panel="part"></div>' +
          '<div class="ckt-panel" data-panel="env" hidden></div>' +
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
  }

  const cv = root.querySelector('.ckt-canvas canvas');
  const ctx = cv.getContext('2d');
  const plotWrap = root.querySelector('[data-plot]');
  const ro_ = !!opts.readOnly;
  const plotCv = plotWrap ? plotWrap.querySelector('canvas') : null;
  const outEl = root.querySelector('[data-out]');
  const partPanel = root.querySelector('[data-panel="part"]');
  const envPanel = root.querySelector('[data-panel="env"]');
  const optsEl = root.querySelector('[data-opts]');

  /* The simulated world, held beside the model rather than in it: a schematic is the
     same schematic in the dark and in the light, and a saved circuit should not
     remember what the light slider happened to be at. Seeded from the model when one
     arrives carrying an environment, so the editor shows the world its own grading
     resolves sensors against rather than a different one. */
  const env = Object.assign({}, ENV_DEFAULT, (opts.model && opts.model.env) || null);

  /* The model as the outside world gets it. The environment rides along, because a
     grader that is handed only the model has no other way to learn what the learner
     set the sliders to — and grading an LDR at a light level the learner is not
     looking at makes the grade disagree with the schematic in front of them, silently.
     It rides along NON-ENUMERABLY: JSON.stringify sees only the schematic, so a saved
     circuit still does not remember the sliders, exactly as the panel promises. */
  function snapshot() {
    const copy = JSON.parse(JSON.stringify(model));
    Object.defineProperty(copy, 'env', {
      value: Object.assign({}, env), enumerable: false, writable: true, configurable: true,
    });
    return copy;
  }

  function P() { return typeof Sandbox !== 'undefined' ? Sandbox.palette() : { ink: '#eee', dim: '#888', faint: '#555', line: '#333', accent: '#C7F751', blue: '#6E9BFF', amber: '#FFC66D', purple: '#A78BFA' }; }

  /* ---- geometry ----
     gx/gy map a grid cell to WORLD pixels and know nothing about zoom or scroll; the
     canvas transform applies the viewport. Keeping the two apart is what lets every
     drawing routine below stay exactly as it was when zoom arrived. */
  const originX = 2, originY = 2;
  function gx(x) { return (x - originX) * GRID + GRID; }
  function gy(y) { return (y - originY) * GRID + GRID; }
  /* screen pixels -> world pixels -> the nearest grid cell */
  function toWorld(sx, sy) { return [sx / view.s + view.px, sy / view.s + view.py]; }
  function toGrid(sx, sy) {
    const w = toWorld(sx, sy);
    return [Math.round((w[0] - GRID) / GRID) + originX, Math.round((w[1] - GRID) / GRID) + originY];
  }
  function evPt(e) {
    const r = cv.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  }

  /* Everything the drawing occupies, in grid cells. Used by zoom-to-fit and by the
     read-only painter, which have always needed the same answer. */
  function contentBounds() {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    const see = function (px, py) {
      if (px < x0) x0 = px; if (px > x1) x1 = px;
      if (py < y0) y0 = py; if (py > y1) y1 = py;
    };
    model.parts.forEach(function (p) { Netlist.pinsOf(p).forEach(function (pt) { see(pt[0], pt[1]); }); see(p.x, p.y); });
    model.wires.forEach(function (wr) { see(wr.a[0], wr.a[1]); see(wr.b[0], wr.b[1]); });
    if (!isFinite(x0)) return null;
    return { x0: x0, y0: y0, x1: x1, y1: y1 };
  }

  function zoomTo(scale, anchorSx, anchorSy) {
    const ns = Math.max(0.3, Math.min(4, scale));
    if (anchorSx === undefined) { view.s = ns; paint(); return; }
    /* keep the point under the cursor still: it is the difference between zooming
       and being thrown across the drawing */
    const before = toWorld(anchorSx, anchorSy);
    view.s = ns;
    const after = toWorld(anchorSx, anchorSy);
    view.px += before[0] - after[0];
    view.py += before[1] - after[1];
    paint();
  }

  function zoomFit() {
    const b = contentBounds();
    const box = cv.parentElement.getBoundingClientRect();
    const w = Math.max(320, box.width), h = Math.max(260, box.height);
    if (!b) { view = { s: 1, px: 0, py: 0 }; paint(); return; }
    const pad = 1.5;
    const needW = (b.x1 - b.x0 + pad * 2) * GRID, needH = (b.y1 - b.y0 + pad * 2) * GRID;
    view.s = Math.max(0.3, Math.min(4, Math.min(w / needW, h / needH)));
    view.px = gx(b.x0 - pad) - (w / view.s - needW) / 2;
    view.py = gy(b.y0 - pad) - (h / view.s - needH) / 2;
    paint();
  }

  function selOne() {
    if (selIds.size !== 1) return null;
    const id = selIds.values().next().value;
    return model.parts.find(function (p) { return p.id === id; }) || null;
  }
  function selParts() { return model.parts.filter(function (p) { return selIds.has(p.id); }); }

  function partAt(pt) {
    return model.parts.find(function (p) {
      if (p.kind === 'GND') return p.x === pt[0] && p.y === pt[1];
      return p.x === pt[0] && p.y === pt[1];
    });
  }

  /* ---- reading the answer back off the schematic ----
   *
   * A readout shows the operating point and nothing else. A lamp brightening through
   * a transient would need an animation nobody asked for, and a lamp showing the
   * first point of a frequency sweep would be showing a number that means nothing —
   * so until there is a DC answer on the canvas, the displays sit blank rather than
   * inventing a reading. */
  function dcAt(pt) {
    if (!result || result.kind !== 'dc' || !result.net) return null;
    const n = result.net.nodeAt(pt);
    if (n === null || n === undefined || result.v[n] === undefined) return null;
    return result.v[n];
  }
  /* volts across a two-pin part, in the pin order the netlist uses */
  function acrossOf(p) {
    const pins = Netlist.pinsOf(p);
    const a = dcAt(pins[0]), b = dcAt(pins[1]);
    return (a === null || b === null) ? null : a - b;
  }
  function lampPower(p) {
    const u = acrossOf(p);
    return u === null ? null : u * u / Math.max(p.value, 1e-3);
  }

  /* What a part writes next to itself. A sensor shows the resistance it has resolved
     to in the current environment, not the parameter in its value box: the whole
     point of a sensor is that the number moves, and watching it move as the slider
     moves is the fastest way to see which way round the model goes. */
  function labelOf(p, k) {
    const n = p.id.replace('p', '');
    if (p.kind === 'SW') return 'SW' + n + '  ' + (p.closed ? 'closed' : 'open');
    if (p.kind === 'LDR' || p.kind === 'NTC') return p.kind + n + '  ' + fmtEng(ohmsOf(p, env), 'Ω');
    if (p.kind === 'POT') {
      const w = p.wiper === undefined ? 0.5 : p.wiper;
      return 'POT' + n + '  ' + fmtEng(p.value, 'Ω') + ' w=' + w.toFixed(2);
    }
    if (p.kind === 'LAMP') {
      const pw = lampPower(p);
      return 'LAMP' + n + '  ' + fmtEng(p.value, 'Ω') + (pw === null ? '' : '  ' + fmtEng(pw, 'W'));
    }
    if (p.kind === 'METER') {
      const u = acrossOf(p);
      return 'A' + n + (u === null ? '  in series' : '  ' + fmtEng(u / Math.max(p.value, 1e-6), 'A'));
    }
    return p.kind + n + '  ' + fmtEng(p.value, k.unit);
  }

  /* ---- drawing ---- */
  function drawPart(p, colour, pal) {
    const x = gx(p.x), y = gy(p.y);
    const k = PART_KINDS[p.kind];
    pal = pal || P();
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

    /* A bar display hangs off one node and takes no part in the solution, so it is
       drawn like the probe: a stub up to a gauge, the number above it, and the scale
       it is being read against written underneath. A bar with no stated full scale
       is a bar you cannot read. */
    if (p.kind === 'BAR') {
      const full = Math.abs(p.value) > 1e-12 ? Math.abs(p.value) : 5;
      const v = dcAt([p.x, p.y]);
      const bw = 48, bh = 11, bx = x - bw / 2, by = y - 8 - bh;
      ctx.beginPath();
      ctx.moveTo(x, y); ctx.lineTo(x, by + bh);
      ctx.stroke();
      ctx.strokeRect(bx, by, bw, bh);
      if (v !== null) {
        const frac = Math.min(Math.max(v / full, 0), 1);
        ctx.fillStyle = v < 0 ? pal.amber : colour;
        if (frac > 0) ctx.fillRect(bx + 1.5, by + 1.5, (bw - 3) * frac, bh - 3);
        /* over-range gets a caret rather than a full bar that quietly lies */
        if (v > full) {
          ctx.beginPath();
          ctx.moveTo(bx + bw + 3, by + 1); ctx.lineTo(bx + bw + 8, by + bh / 2);
          ctx.lineTo(bx + bw + 3, by + bh - 1);
          ctx.fillStyle = pal.amber;
          ctx.fill();
        }
      }
      ctx.font = '10.5px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = v === null ? pal.dim : (v < 0 || v > full ? pal.amber : colour);
      ctx.fillText(v === null ? 'BAR' + p.id.replace('p', '') : fmtEng(v, 'V'), x, by - 8);
      ctx.fillStyle = pal.dim;
      ctx.fillText('0–' + fmtEng(full, 'V'), x, y + 11);
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
    } else if (p.kind === 'SW') {
      /* The blade is the state: drawn lying down when closed and lifted when open, so
         the schematic answers "is it on?" without anyone opening a panel. */
      ctx.moveTo(-L, 0); ctx.lineTo(-12, 0);
      ctx.moveTo(12, 0); ctx.lineTo(L, 0);
      if (p.closed) { ctx.moveTo(-12, 0); ctx.lineTo(12, 0); }
      else { ctx.moveTo(-12, 0); ctx.lineTo(10, -12); }
      ctx.stroke();
      ctx.beginPath(); ctx.arc(-12, 0, 2.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(12, 0, 2.2, 0, Math.PI * 2); ctx.fill();
    } else if (p.kind === 'LDR' || p.kind === 'NTC' || p.kind === 'POT') {
      /* all three are a resistor body with something done to it */
      ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
      for (let i = 0; i < 6; i++) ctx.lineTo(-13 + (i + 0.5) * 26 / 6, (i % 2 ? 6 : -6));
      ctx.lineTo(13, 0); ctx.lineTo(L, 0);
      if (p.kind === 'LDR') {
        /* two arrows pointing IN at the body: light arriving, the sense the symbol
           has always had — an LED's arrows point away because it emits */
        for (const ax of [-8, 2]) {
          ctx.moveTo(ax - 9, -21); ctx.lineTo(ax, -12);
          ctx.moveTo(ax, -12); ctx.lineTo(ax - 5, -13.5);
          ctx.moveTo(ax, -12); ctx.lineTo(ax - 1.5, -17);
        }
      } else if (p.kind === 'NTC') {
        /* the thermistor's diagonal, with its foot along the bottom */
        ctx.moveTo(-16, 12); ctx.lineTo(-11, 12); ctx.lineTo(13, -12);
      } else {
        /* the wiper: an arrow down the third pin onto the track */
        ctx.moveTo(0, -L); ctx.lineTo(0, -10);
        ctx.moveTo(-3.5, -14); ctx.lineTo(0, -9.5); ctx.lineTo(3.5, -14);
      }
      ctx.stroke();
    } else if (p.kind === 'LAMP') {
      const pw = lampPower(p);
      const br = pw === null ? 0 : Math.min(Math.max(pw / Math.max(p.pnom === undefined ? 0.25 : p.pnom, 1e-9), 0), 1);
      if (br > 0.002) {
        /* brightness is shown, not stated: the fill and the rays both scale with it,
           and the square root is there because the eye is not linear in power */
        const g = Math.sqrt(br);
        ctx.save();
        ctx.globalAlpha = 0.18 + 0.55 * g;
        ctx.fillStyle = pal.amber;
        ctx.beginPath(); ctx.arc(0, 0, 11, 0, Math.PI * 2); ctx.fill();
        ctx.globalAlpha = 0.35 + 0.5 * g;
        ctx.strokeStyle = pal.amber;
        ctx.beginPath();
        for (let i = 0; i < 8; i++) {
          const a = i * Math.PI / 4 + Math.PI / 8;
          ctx.moveTo(Math.cos(a) * 13, Math.sin(a) * 13);
          ctx.lineTo(Math.cos(a) * (14 + 5 * g), Math.sin(a) * (14 + 5 * g));
        }
        ctx.stroke();
        ctx.restore();
        ctx.beginPath();
      }
      ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
      ctx.moveTo(11, 0); ctx.lineTo(L, 0);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, 11, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      const d = 11 * Math.SQRT1_2;
      ctx.moveTo(-d, -d); ctx.lineTo(d, d);
      ctx.moveTo(-d, d); ctx.lineTo(d, -d);
      ctx.stroke();
    } else if (p.kind === 'METER') {
      ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
      ctx.moveTo(11, 0); ctx.lineTo(L, 0);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, 11, 0, Math.PI * 2);
      ctx.stroke();
      /* the reference direction the reading is signed against — an ammeter that does
         not say which way is positive turns every answer into a coin toss */
      ctx.beginPath();
      ctx.moveTo(-7, -16); ctx.lineTo(7, -16);
      ctx.moveTo(3, -19); ctx.lineTo(7, -16); ctx.lineTo(3, -13);
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
        /* + on the terminal the solver treats as positive — which is the RIGHT pin
           flat and the TOP pin rotated (see plusFirst). Rotating the canvas by +90°
           sends local +x to the BOTTOM of the screen, so drawing the + at a fixed
           local +x put it on the bottom pin of a vertical source: the drawn polarity
           was the opposite of the solved one, and a learner reading the sign off the
           symbol got it backwards. The glyphs swap ends with the symbol instead. The
           solver's convention is untouched; only the label moves. */
        const s = p.rot ? -1 : 1;
        ctx.moveTo(3 * s, -4); ctx.lineTo(9 * s, -4);
        ctx.moveTo(6 * s, -7); ctx.lineTo(6 * s, -1);
        ctx.moveTo(-9 * s, -4); ctx.lineTo(-3 * s, -4);
      } else {
        ctx.moveTo(0, 7); ctx.lineTo(0, -7);
        ctx.moveTo(-3.5, -3.5); ctx.lineTo(0, -7); ctx.lineTo(3.5, -3.5);
      }
      ctx.stroke();
    }
    ctx.restore();

    /* Letters go on outside the rotation, or a vertical meter reads sideways. */
    if (p.kind === 'METER') {
      ctx.font = 'bold 10px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = colour;
      ctx.fillText('A', x, y + 0.5);
    }

    /* Value label, clear of the body — and clear of whatever the body grew. R, C, L,
       V and I keep the placement they have always had, because a hundred and fifty
       published figures are drawn with it. The kinds that carry a mark outside the
       body (an LDR's arrows, a meter's direction arrow, a lamp's glow) need more room
       than that, and a potentiometer needs its label on the side its wiper is not:
       the wiper is a pin, a wire arrives on it, and a label centred there would be
       written across the wire. */
    ctx.font = '10.5px ui-monospace, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = colour;
    const lab = labelOf(p, k);
    const wide = { LDR: 24, METER: 22, LAMP: 22, SW: 20, NTC: 20 }[p.kind];
    if (p.kind === 'POT') {
      if (p.rot) { ctx.textAlign = 'right'; ctx.fillText(lab, x - 22, y); }
      else ctx.fillText(lab, x, y + 22);
    } else if (wide) {
      if (p.rot) { ctx.textAlign = 'left'; ctx.fillText(lab, x + wide, y); }
      else ctx.fillText(lab, x, y - 26);
    } else if (p.rot) ctx.fillText(lab, x + 34, y);
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

    /* A diagram is a question's illustration, so cropping it is not a cosmetic
       failure — the probe the question asks about was falling off the right-hand edge
       at ordinary laptop widths. The editor can scroll and pan; a diagram cannot, so
       it scales itself to fit and centres what is left. */
    if (ro_ && model.parts.length) {
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      const see = function (px, py) {
        if (px < x0) x0 = px; if (px > x1) x1 = px;
        if (py < y0) y0 = py; if (py > y1) y1 = py;
      };
      model.parts.forEach(function (p2) { Netlist.pinsOf(p2).forEach(function (pt) { see(pt[0], pt[1]); }); see(p2.x, p2.y); });
      model.wires.forEach(function (wr) { see(wr.a[0], wr.a[1]); see(wr.b[0], wr.b[1]); });
      const pad = 1.2;
      const needW = (x1 - x0 + pad * 2) * GRID, needH = (y1 - y0 + pad * 2) * GRID;
      const s2 = Math.min(w / needW, h / needH, 1.6);
      ctx.setTransform(dpr * s2, 0, 0, dpr * s2,
        dpr * ((w - needW * s2) / 2 - (x0 - pad - originX) * GRID * s2 - GRID * s2),
        dpr * ((h - needH * s2) / 2 - (y0 - pad - originY) * GRID * s2 - GRID * s2));
    }

    /* The editor's viewport. The read-only branch above has already set its own
       fit-to-box transform and must not be overwritten. */
    if (!ro_) {
      ctx.setTransform(dpr * view.s, 0, 0, dpr * view.s,
        -view.px * view.s * dpr, -view.py * view.s * dpr);
    }

    /* Grid dots, drawn across whatever part of the world is currently visible rather
       than across the canvas: at any zoom other than 1 those are different regions,
       and drawing the canvas one leaves the dots pinned to the screen while the
       circuit slides underneath. */
    const vx0 = ro_ ? 0 : view.px, vy0 = ro_ ? 0 : view.py;
    const vx1 = vx0 + (ro_ ? w : w / view.s), vy1 = vy0 + (ro_ ? h : h / view.s);
    ctx.fillStyle = pal.faint;
    ctx.globalAlpha = 0.5;
    for (let X = Math.floor(vx0 / GRID) * GRID; X < vx1 + GRID; X += GRID) {
      if (X < GRID) continue;
      for (let Y = Math.floor(vy0 / GRID) * GRID; Y < vy1 + GRID; Y += GRID) {
        if (Y < GRID) continue;
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
      drawPart(p, selIds.has(p.id) ? pal.accent : pal.ink, pal);
    });

    paintMarquee();

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
  function paintMarquee() {
    if (!marquee) return;
    const a = marquee.a, b = marquee.b;
    const x = Math.min(a[0], b[0]), y = Math.min(a[1], b[1]);
    ctx.save();
    ctx.strokeStyle = P().accent;
    ctx.setLineDash([4, 3]);
    ctx.lineWidth = 1 / view.s;
    ctx.strokeRect(x, y, Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1]));
    ctx.restore();
  }

  function paintPart() {
    const p = selOne();
    if (selIds.size > 1) {
      partPanel.innerHTML = '<h4>' + selIds.size + ' parts selected</h4>' +
        '<p class="ckt-hint">Drag to move them together. R rotates, Delete removes. ' +
        'Click an empty cell to deselect.</p>';
      return;
    }
    if (!p || p.kind === 'GND' || p.kind === 'OUT') {
      partPanel.innerHTML = '<h4>Component</h4><p class="ckt-hint">' +
        (tool === 'wire' ? 'Click a pin, then click where the wire should end.'
          : tool === 'select' ? 'Click a component to select it.'
          : 'Click the grid to place a ' + PART_KINDS[tool].name.toLowerCase() + '.') + '</p>';
      return;
    }
    const k = PART_KINDS[p.kind];
    partPanel.innerHTML = '<h4>' + k.name + ' ' + esc2(p.id.replace('p', '')) + '</h4>' +
      (p.kind === 'SW'
        ? '<button class="ckt-t" data-sw style="width:100%;margin-bottom:8px">' +
          (p.closed ? 'Closed — click to open' : 'Open — click to close') + '</button>'
        : '<label class="ckt-f"><span>' + esc2(VALUE_LABEL[p.kind] || ('Value (' + k.unit + ')')) + '</span>' +
          '<input data-val value="' + esc2(fmtEng(p.value, '').trim()) + '"></label>') +
      (PART_FIELDS[p.kind] || []).map(function (f) {
        const cur = p[f[0]] === undefined ? PART_KINDS[p.kind].state[f[0]] : p[f[0]];
        return '<label class="ckt-f"><span>' + esc2(f[1]) + '</span>' +
          '<input data-x="' + f[0] + '" value="' + esc2(String(cur)) + '"></label>';
      }).join('') +
      (p.kind === 'POT'
        ? '<div class="ckt-f" style="grid-template-columns:auto 1fr auto">' +
          '<span>Wiper</span><input type="range" data-wiper min="0" max="1000" step="1" value="' +
          Math.round((p.wiper === undefined ? 0.5 : p.wiper) * 1000) +
          '" style="height:18px;padding:0;border:0;background:none;accent-color:var(--lime);width:100%">' +
          '<span data-wiperval style="color:var(--lime)">' +
          (p.wiper === undefined ? 0.5 : p.wiper).toFixed(2) + '</span></div>'
        : '') +
      '<p class="ckt-hint" data-note>' + modelNote(p) + '</p>';

    const inp = partPanel.querySelector('[data-val]');
    if (inp) inp.addEventListener('change', function () {
      p.value = parseEng(inp.value, p.value);
      changed();
      paintPart();
    });
    partPanel.querySelectorAll('[data-x]').forEach(function (el) {
      el.addEventListener('change', function () {
        const f = (PART_FIELDS[p.kind] || []).filter(function (q) { return q[0] === el.dataset.x; })[0];
        const v = parseEng(el.value, p[el.dataset.x]);
        p[el.dataset.x] = Math.min(Math.max(isFinite(v) ? v : f[2], f[2]), f[3]);
        changed();
        paintPart();
      });
    });
    const sw = partPanel.querySelector('[data-sw]');
    if (sw) sw.addEventListener('click', function () { toggleSwitch(p); });
    const wip = partPanel.querySelector('[data-wiper]');
    if (wip) wip.addEventListener('input', function () {
      p.wiper = Math.min(Math.max(+wip.value / 1000, 0), 1);
      partPanel.querySelector('[data-wiperval]').textContent = p.wiper.toFixed(2);
      /* The note quotes the two stamped resistances, so it goes stale the instant the
         wiper moves — and it is the one label that exists so the learner can read the
         model rather than trust it. Rewritten in place rather than through
         paintPart(), which would rebuild the slider out from under the pointer. */
      refreshNote();
      retouchSoon();
    });
  }

  /* What the value box means for a kind whose value is not simply "the value". */
  const VALUE_LABEL = {
    LDR: 'R at 10 lx (Ω)', NTC: 'R at 25 °C (Ω)', POT: 'Total (Ω)',
    LAMP: 'Resistance (Ω)', METER: 'Burden (Ω)', BAR: 'Full scale (V)',
  };
  /* The extra numbers a kind carries beyond `value`: key, label, and the range it is
     clamped to, because a γ of zero or a negative B is a model that means nothing. */
  const PART_FIELDS = {
    LDR: [['gamma', 'γ slope', 0.05, 3]],
    NTC: [['beta', 'B (K)', 1, 20000]],
    LAMP: [['pnom', 'Full at (W)', 1e-9, 1e6]],
  };

  /* The model, written where the learner can read it. A sensor whose curve you have
     to take on trust is a magic box, and a magic box teaches nothing — so each of
     these states the equation, its parameters, and what it does NOT model. */
  function modelNote(p) {
    const n = p.id.replace('p', '');
    if (p.kind === 'SW') {
      return 'A state, not a value. Closed stamps ' + fmtEng(SW_ON, 'Ω') + '; open stamps ' +
        fmtEng(SW_OFF, 'Ω') + ' rather than deleting the branch, so whatever hangs off the far ' +
        'side still has a defined voltage instead of the solver calling the circuit ' +
        'under-determined. Click the switch on the canvas to toggle it.';
    }
    if (p.kind === 'LDR') {
      return 'R = R₁₀ · (10 lx / E)^γ — the photoresistor power law, R₁₀ being the resistance ' +
        'at the 10 lx a datasheet quotes. More light, less resistance. At E = ' +
        fmtEng(env.lux, 'lx') + ' this one is ' + fmtEng(ohmsOf(p, env), 'Ω') +
        '. Drag the light slider and watch it move.';
    }
    if (p.kind === 'NTC') {
      return 'R = R₂₅ · exp(B · (1/T − 1/298.15)), T in kelvin — the beta model. B > 0 makes ' +
        'the exponent negative as T rises, so resistance FALLS with heat, which is what the N ' +
        'in NTC means. It is a two-point fit, worth a few percent over a 50 K span and no more; ' +
        'Steinhart–Hart is what you reach for beyond that. At ' + env.tempC.toFixed(1) +
        ' °C this one is ' + fmtEng(ohmsOf(p, env), 'Ω') + '.';
    }
    if (p.kind === 'POT') {
      const rr = potSplit(p);
      return 'Three pins, stamped as two resistances sharing the wiper node: ' +
        fmtEng(rr[0], 'Ω') + ' from the first pin to the wiper and ' + fmtEng(rr[1], 'Ω') +
        ' from the wiper to the second. The wiper is the third pin, leaving the body at ' +
        'right angles to the track — ' + (p.rot ? 'to the right' : 'above') + ' it as drawn.';
    }
    if (p.kind === 'LAMP') {
      const pw = lampPower(p);
      return 'An ordinary resistance to the solver. The brightness is drawn from the power in ' +
        'it, P = V²/R, against ' + fmtEng(p.pnom === undefined ? 0.25 : p.pnom, 'W') +
        ' for full brightness' + (pw === null ? '' : '; right now P = ' + fmtEng(pw, 'W')) +
        '. Nothing here is non-linear: a real filament\'s resistance climbs as it heats, and ' +
        'that is not modelled.';
    }
    if (p.kind === 'METER') {
      const u = acrossOf(p);
      return 'An ammeter goes IN SERIES: break the branch and put it in the gap. It reads the ' +
        'current through itself as V / ' + fmtEng(p.value, 'Ω') + ', positive from the ' +
        (p.rot ? 'top' : 'left') + ' pin to the ' + (p.rot ? 'bottom' : 'right') +
        ' — the arrow says which way' + (u === null ? '' : '; now ' + fmtEng(u / Math.max(p.value, 1e-6), 'A')) +
        '. The burden resistance is honest rather than ideal: it is what the measurement costs ' +
        'the circuit, and it keeps the meter a resistor the linear solver already understands.';
    }
    if (p.kind === 'BAR') {
      const v = dcAt([p.x, p.y]);
      return 'Reads the node it sits on, against ground, and takes no part in the solution — ' +
        'placing it changes no answer. The bar fills from 0 to the full scale; past that it ' +
        'gets a caret rather than a full bar that quietly lies, and a negative voltage reads ' +
        'in amber with the bar empty' + (v === null ? '. Solve to give it something to show.' :
        ', and it is showing ' + fmtEng(v, 'V') + ' now.');
    }
    if (p.kind === 'V' || p.kind === 'I') {
      return 'The + terminal is the ' + (p.rot ? 'top' : 'right') + ' pin. ' +
        'A frequency sweep drives it at this same amplitude, so set it to 1 for a plain transfer function.';
    }
    return 'Part ' + n + '. Type a value with the usual prefixes — 4k7 is not understood, 4.7k is.';
  }

  /* The model note quotes numbers that move — the two halves of a potentiometer, the
     power in a lamp, the current through a meter, the voltage a bar is showing — so
     any in-place change makes it stale, and it is the one label that exists for the
     learner to read the model rather than trust it. Rewritten in place rather than
     through paintPart(), which rebuilds the panel and would take a slider out from
     under the pointer mid-drag. */
  function refreshNote() {
    const sel = selOne();
    const note = partPanel && partPanel.querySelector('[data-note]');
    if (sel && note) note.textContent = modelNote(sel);
  }

  /* A change that alters numbers but not topology: a switch thrown, a wiper moved, a
     slider dragged. The model is saved and the answer re-solved in place, rather than
     thrown away the way an edit to the drawing throws it away — the whole point of
     flipping a switch is to see what it did to the answer you were already looking
     at. */
  function retouch() {
    if (opts.onChange) opts.onChange(snapshot());
    if (result) solve(); else paint();
    paintEnv();
  }

  /* One run per frame however fast the input arrives. A DC point is cheap, but a
     220-point sweep is not, and queueing one per pointer event would make a slider
     feel like it was stuck in treacle. Every continuous control goes through this —
     the wiper as well as the environment sliders, since they cost the same solve. */
  function perFrame(fn) {
    let pending = false;
    return function () {
      if (pending) return;
      pending = true;
      const later = function () {
        pending = false;
        if (disposed) return;
        fn();
      };
      if (typeof requestAnimationFrame === 'function') requestAnimationFrame(later);
      else setTimeout(later, 16);
    };
  }
  const retouchSoon = perFrame(function () { retouch(); });

  function toggleSwitch(p) {
    p.closed = !p.closed;
    retouch();
    paintPart();
  }
  function esc2(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }

  /* ---- the simulated world ----
   *
   * A sensor whose reading cannot be varied is a resistor with a fancy name. This is
   * the panel that makes it a sensor: one slider per quantity something on the canvas
   * actually senses, and the circuit re-solves as it moves.
   *
   * The sliders appear only when a part needs them. A light slider above a schematic
   * with no light sensor in it is a control that does nothing, and a control that
   * does nothing is a lie about what the model contains. */
  const ENV_Q = [
    { key: 'lux', label: 'Light', unit: 'lx', log: true, min: 0.1, max: 1e5,
      note: 'Moonlight is about 0.1 lx, a lit room 200 lx, an overcast day 1 klx, ' +
            'direct sun 100 klx.' },
    { key: 'tempC', label: 'Temperature', unit: '°C', log: false, min: -20, max: 120,
      note: 'Kelvin is what the beta model wants; this slider is in °C because that is ' +
            'what a datasheet and a room both speak.' },
  ];
  function envQ(key) { return ENV_Q.filter(function (q) { return q.key === key; })[0]; }
  function envToSlider(q, v) {
    const t = q.log ? Math.log(Math.max(v, q.min) / q.min) / Math.log(q.max / q.min)
                    : (v - q.min) / (q.max - q.min);
    return Math.round(Math.min(Math.max(t, 0), 1) * 1000);
  }
  function envFromSlider(q, t) {
    const f = Math.min(Math.max(t / 1000, 0), 1);
    return q.log ? q.min * Math.pow(q.max / q.min, f) : q.min + f * (q.max - q.min);
  }
  function envShow(q) {
    return q.log ? fmtEng(env[q.key], q.unit) : env[q.key].toFixed(1) + ' ' + q.unit;
  }
  /* which quantities anything on the canvas actually senses, in a fixed order */
  function envInUse() {
    return ENV_Q.filter(function (q) {
      return model.parts.some(function (p) {
        const k = PART_KINDS[p.kind];
        return k && k.senses === q.key;
      });
    });
  }

  let envSig = null;
  function paintEnv() {
    if (!envPanel) return;
    const qs = envInUse();
    const sig = qs.map(function (q) { return q.key; }).join(',');
    if (sig === envSig) {
      /* same sliders, new numbers: leave the inputs alone so a drag is not interrupted */
      qs.forEach(function (q) {
        const el = envPanel.querySelector('[data-envval="' + q.key + '"]');
        if (el) el.textContent = envShow(q);
      });
      return;
    }
    envSig = sig;
    if (!qs.length) { envPanel.hidden = true; envPanel.innerHTML = ''; return; }
    envPanel.hidden = false;
    envPanel.innerHTML = '<h4>Environment</h4>' + qs.map(function (q) {
      return '<div style="margin-bottom:10px">' +
        '<div style="display:flex;justify-content:space-between;gap:8px;font-family:var(--mono);' +
        'font-size:10.5px;color:var(--ink-4);margin-bottom:4px">' +
        '<span>' + esc2(q.label) + '</span>' +
        '<span data-envval="' + q.key + '" style="color:var(--lime)">' + esc2(envShow(q)) + '</span></div>' +
        '<input type="range" data-env="' + q.key + '" min="0" max="1000" step="1" value="' +
        envToSlider(q, env[q.key]) + '" aria-label="' + esc2(q.label) +
        '" style="width:100%;height:18px;padding:0;border:0;background:none;accent-color:var(--lime)">' +
        '<p class="ckt-hint" style="margin-top:4px">' + esc2(q.note) + '</p>' +
        '</div>';
    }).join('') +
      '<p class="ckt-hint">Simulated, not measured — and not part of the schematic, so a ' +
      'saved circuit does not remember where you left these. The solution updates as you drag.</p>';

    envPanel.querySelectorAll('[data-env]').forEach(function (el) {
      el.addEventListener('input', function () {
        const q = envQ(el.dataset.env);
        env[q.key] = envFromSlider(q, +el.value);
        const out = envPanel.querySelector('[data-envval="' + q.key + '"]');
        if (out) out.textContent = envShow(q);
        envTouched();
      });
    });
  }

  /* One re-solve per frame however fast the slider moves — see perFrame. retouch()
     rather than a bare solve, because where the sliders stand is now part of what
     grading sees, and the outside world has to hear about it the same way it hears
     about a thrown switch. */
  const envTouched = perFrame(function () {
    retouch();
    paintPart();
  });

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
    /* the environment is resolved into resistances here, once, before any stamping */
    const net = Netlist.build(model, env);
    let r;
    if (analysis.mode === 'dc') r = MNA.dc(net);
    else if (analysis.mode === 'ac') r = MNA.ac(net, analysis.f1, analysis.f2, 220);
    else r = MNA.tran(net, analysis.tstop, analysis.tstop / 900);

    if (r.error) {
      result = null;
      plotWrap.hidden = true;
      outEl.innerHTML = '<div class="ckt-err">' + esc2(r.error) + '</div>';
      paint();
      refreshNote();
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
    /* the numbers the note quotes are the ones that just changed */
    refreshNote();
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
    if (opts.onChange) opts.onChange(snapshot());
    /* a sensor may have arrived or left, and with it the slider that drives it */
    paintEnv();
    paint();
  }

  /* A diagram is a picture. Everything from here down is editing, analysis and
     chrome — pointer handlers that place parts, a document-level keydown listener,
     and lookups for a toolbar this DOM does not have. Returning above all of it is
     what actually makes read-only read-only: the previous version returned below the
     handlers, so clicking a question's schematic inserted a resistor into it. */
  if (ro_) {
    let dro = null;
    if (typeof ResizeObserver !== 'undefined') {
      dro = new ResizeObserver(function () { paint(); });
      dro.observe(cv.parentElement);
    }
    paint();
    return {
      getModel: function () { return snapshot(); },
      solve: function () { return null; },
      dispose: function () {
        disposed = true;
        if (dro) dro.disconnect();
        root.innerHTML = '';
      },
    };
  }

  /* ---- interaction ---- */
  /* How far the pointer has moved, in screen pixels, since it went down. A click and
     a drag start identically, so nothing commits to being a drag until it has moved
     far enough that the learner clearly meant it. */
  const DRAG_SLOP = 4;
  let down = null;

  cv.addEventListener('pointermove', function (e) {
    const sp = evPt(e);
    hover = toGrid(sp[0], sp[1]);

    if (panFrom) {
      view.px = panFrom.px + (panFrom.sx - sp[0]) / view.s;
      view.py = panFrom.py + (panFrom.sy - sp[1]) / view.s;
      paint();
      return;
    }

    if (down && !drag && !marquee && down.mode === 'maybe-move' &&
        Math.hypot(sp[0] - down.sx, sp[1] - down.sy) > DRAG_SLOP) {
      drag = { from: down.grid, moved: false };
    }
    if (down && !drag && !marquee && down.mode === 'maybe-marquee' &&
        Math.hypot(sp[0] - down.sx, sp[1] - down.sy) > DRAG_SLOP) {
      marquee = { a: toWorld(down.sx, down.sy), b: toWorld(sp[0], sp[1]) };
    }

    if (drag) {
      const dx = hover[0] - drag.from[0], dy = hover[1] - drag.from[1];
      if (dx || dy) {
        selParts().forEach(function (p) { p.x += dx; p.y += dy; });
        drag.from = hover;
        drag.moved = true;
        paint();
      }
      return;
    }

    if (marquee) { marquee.b = toWorld(sp[0], sp[1]); paint(); return; }
    if (wireFrom) paint();
  });

  cv.addEventListener('pointerleave', function () { hover = null; if (wireFrom) paint(); });

  /* Wheel zooms about the cursor. Ctrl+wheel is the browser's own page zoom on some
     setups, so it is left alone. */
  cv.addEventListener('wheel', function (e) {
    if (e.ctrlKey) return;
    e.preventDefault();
    const sp = evPt(e);
    zoomTo(view.s * (e.deltaY < 0 ? 1.12 : 1 / 1.12), sp[0], sp[1]);
  }, { passive: false });

  cv.addEventListener('pointerdown', function (e) {
    const sp = evPt(e);
    const pt = toGrid(sp[0], sp[1]);

    /* Middle button, or space held: pan. Both are what a drawing tool does, and the
       second is the one people already have in their fingers. */
    if (e.button === 1 || spaceDown) {
      panFrom = { sx: sp[0], sy: sp[1], px: view.px, py: view.py };
      cv.setPointerCapture(e.pointerId);
      e.preventDefault();
      return;
    }
    if (e.button !== 0) return;

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
      cv.setPointerCapture(e.pointerId);
      if (hit) {
        if (e.shiftKey) {
          if (selIds.has(hit.id)) selIds.delete(hit.id); else selIds.add(hit.id);
        } else if (!selIds.has(hit.id)) {
          selIds.clear();
          selIds.add(hit.id);
        }
        /* Dragging a part that is already part of a multiple selection moves the
           whole selection; that is why the clear above is conditional. `shift` is
           carried so the click-to-use gesture below can tell a plain click from one
           that was only ever adjusting the selection. */
        down = { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-move', hit: hit.id, shift: e.shiftKey };
      } else {
        if (!e.shiftKey) selIds.clear();
        down = { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-marquee' };
      }
      paintPart();
      paint();
      return;
    }

    /* placing: refuse to stack two parts on one cell */
    const existing = partAt(pt);
    if (existing) { selIds.clear(); selIds.add(existing.id); paintPart(); paint(); return; }
    const kind = tool;
    const p = { id: 'p' + (seq++), kind: kind, x: pt[0], y: pt[1], rot: 0,
                value: PART_KINDS[kind].def };
    /* kinds that carry state beyond a value start with the registry's defaults, so a
       part is never placed half-defined and then behaves oddly */
    const st = PART_KINDS[kind].state;
    if (st) Object.keys(st).forEach(function (key2) { p[key2] = st[key2]; });
    model.parts.push(p);
    selIds.clear();
    selIds.add(p.id);
    changed();
    paintPart();
  });

  function endPointer(e) {
    if (panFrom) { panFrom = null; return; }
    if (marquee) {
      const x0 = Math.min(marquee.a[0], marquee.b[0]), x1 = Math.max(marquee.a[0], marquee.b[0]);
      const y0 = Math.min(marquee.a[1], marquee.b[1]), y1 = Math.max(marquee.a[1], marquee.b[1]);
      model.parts.forEach(function (p) {
        const wx = gx(p.x), wy = gy(p.y);
        if (wx >= x0 && wx <= x1 && wy >= y0 && wy <= y1) selIds.add(p.id);
      });
      marquee = null;
      paintPart();
      paint();
    }
    /* A switch is the one part whose state you set by using it rather than by typing
       a number, so a plain click on one throws it. It has to be a CLICK and not a
       press, and not a drag either: toggling on pointerdown would flip the switch
       every time you picked one up to move it. Nor a shift-click: that gesture is
       aimed at the selection, and adding a switch to a selection should no more throw
       it than adding a resistor should change its value. Nor a cancelled gesture: the
       browser taking the pointer away is not the learner using the switch. */
    if (!drag && down && down.mode === 'maybe-move' && down.hit &&
        !down.shift && !(e && e.type === 'pointercancel')) {
      const hp = model.parts.filter(function (p) { return p.id === down.hit; })[0];
      if (hp && hp.kind === 'SW') toggleSwitch(hp);
    }
    if (drag) {
      /* one undo entry per gesture, not one per grid cell crossed */
      if (drag.moved) changed();
      drag = null;
    }
    down = null;
  }
  cv.addEventListener('pointerup', endPointer);
  cv.addEventListener('pointercancel', endPointer);

  /* Space is held to pan, the way it is in every drawing tool. Tracked on the
     document because the canvas does not take keyboard focus. */
  let spaceDown = false;
  function onSpaceDown(e) {
    if (e.code !== 'Space' || spaceDown) return;
    if (e.target && /input|textarea/i.test(e.target.tagName)) return;
    spaceDown = true;
    cv.style.cursor = 'grab';
    e.preventDefault();
  }
  function onSpaceUp(e) {
    if (e.code !== 'Space') return;
    spaceDown = false;
    cv.style.cursor = '';
  }
  document.addEventListener('keydown', onSpaceDown);
  document.addEventListener('keyup', onSpaceUp);

  function onKey(e) {
    if (e.target && /input|textarea/i.test(e.target.tagName)) return;
    if (e.key === 'Delete' || e.key === 'Backspace') { doDelete(); e.preventDefault(); }
    else if (e.key === 'r' || e.key === 'R') { doRotate(); }
    else if (e.key === 'Escape') { wireFrom = null; marquee = null; selIds.clear(); paintPart(); paint(); }
    else if ((e.ctrlKey || e.metaKey) && (e.key === 'a' || e.key === 'A')) {
      selIds.clear();
      model.parts.forEach(function (p) { selIds.add(p.id); });
      paintPart(); paint(); e.preventDefault();
    }
    else if (e.key === '+' || e.key === '=') { zoomTo(view.s * 1.2); }
    else if (e.key === '-' || e.key === '_') { zoomTo(view.s / 1.2); }
    else if (e.key === '0') { zoomFit(); }
  }
  document.addEventListener('keydown', onKey);

  function doRotate() {
    /* one-pin parts sit on their cell and have no direction to turn — which is now a
       question of how many pins a kind declares rather than a list of two names */
    const ps = selParts().filter(function (p) {
      const k = PART_KINDS[p.kind];
      return !k || k.pins > 1;
    });
    if (!ps.length) return;
    ps.forEach(function (p) { p.rot = p.rot ? 0 : 1; });
    changed();
    paintPart();
  }
  function doDelete() {
    if (!selIds.size) return;
    /* A wire with nothing left at either end is a wire the learner cannot see the
       purpose of, but it may still be carrying a connection between two other
       things, so deleting parts leaves wires alone. */
    model.parts = model.parts.filter(function (p) { return !selIds.has(p.id); });
    selIds.clear();
    changed();
    paintPart();
  }

  /* A diagram has no tools, no analysis panel and nothing to click, so there is
     nothing below this line to wire up. Returning early is what makes the read-only
     DOM safe to shrink: every lookup after this point assumes the full chrome. */
  root.querySelectorAll('[data-tool]').forEach(function (b) {
    b.addEventListener('click', function () {
      tool = b.dataset.tool;
      wireFrom = null;
      root.querySelectorAll('[data-tool]').forEach(function (o) { o.classList.toggle('on', o === b); });
      paintPart();
      paint();
    });
  });
  root.querySelector('[data-act="zoomin"]').addEventListener('click', function () { zoomTo(view.s * 1.2); });
  root.querySelector('[data-act="zoomout"]').addEventListener('click', function () { zoomTo(view.s / 1.2); });
  root.querySelector('[data-act="fit"]').addEventListener('click', zoomFit);
  root.querySelector('[data-act="rotate"]').addEventListener('click', doRotate);
  root.querySelector('[data-act="delete"]').addEventListener('click', doDelete);
  root.querySelector('[data-act="clear"]').addEventListener('click', function () {
    model.parts = []; model.wires = []; selIds.clear();
    view = { s: 1, px: 0, py: 0 };
    changed(); paintPart();
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
  paintEnv();
  paintOpts();
  paint();

  return {
    getModel: function () { return snapshot(); },
    solve: solve,
    dispose: function () {
      disposed = true;
      document.removeEventListener('keydown', onKey);
      /* space-to-pan is tracked on the document because the canvas takes no keyboard
         focus, so it has to be released here or every editor ever opened keeps
         listening for the rest of the session */
      document.removeEventListener('keydown', onSpaceDown);
      document.removeEventListener('keyup', onSpaceUp);
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
function circuitContext(model, env) {
  /* The environment can arrive two ways: named by the caller, or riding on the model
     the editor handed out. Grading gets only a model, so without the second door a
     light or temperature sensor would always be resolved at ENV_DEFAULT and the grade
     would disagree with the numbers on the learner's screen. A model with neither
     still lands on ENV_DEFAULT, which is every exercise that has no sensor in it. */
  const net = Netlist.build(model, env || (model && model.env) || null);
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
    /* How many of a kind the learner used. Asked of what was PLACED, not of what was
       stamped: a potentiometer reaches the solver as two resistors and a lamp as one,
       and neither should make count('R') go up. For R, C, L, V and I the two lists
       are the same list. */
    count: function (kind) { return net.placed.filter(function (p) { return p.kind === kind; }).length; },
    values: function (kind) { return net.placed.filter(function (p) { return p.kind === kind; }).map(function (p) { return p.value; }); },
    /* what a dynamic part actually resolved to in this environment */
    ohms: function (id) {
      const r = net.readouts.filter(function (x) { return x.id === id; })[0];
      return r ? r.ohms : null;
    },
    env: net.env,
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

/* Run every check of a circuit exercise against one schematic, in one simulated
   environment: the one named here, else the one the model carries, else the default.
   A sensor is graded against the world the learner set, not a world nobody chose. */
function runCircuitChecks(model, checks, env) {
  return (checks || []).map(function (c) {
    let ctx;
    try { ctx = circuitContext(model, env); }
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
