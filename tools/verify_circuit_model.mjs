/**
 * verify_circuit_model.mjs — the extremes gate for the schematic solver.
 *
 * The circuit editor has two gates already and neither of them asks this question.
 * verify_circuits.mjs asks whether each exercise's reference drawing passes its own
 * checks; verify_numeric.mjs asks whether a stated answer matches the solver. Both feed
 * it the values an author chose. verify_circuit_ui.mjs drives the keyboard and never
 * reaches the matrix. So the one thing nobody asked was the Simulation Auditor's whole
 * brief: what does this thing do when it is fed zero, negative, enormous and identical
 * values, resized mid-interaction, and clicked faster than it can re-solve.
 *
 * The four defects that prompted it, all found by hand and then written down here:
 *
 *   * AN ANSWER OF NaN, REPORTED AS A SUCCESS. src/circuit.js opens by promising that
 *     "an iteration that does not settle says so and returns no numbers at all". The
 *     Newton path keeps that promise — allFinite() guards every pass. The LINEAR path,
 *     which is where every one of the 376 published schematics lives, because not one of
 *     them holds a device to iterate on, had no such check: a
 *     capacitance of 1e308 F made the companion conductance C/h overflow, and a
 *     transient came back with 900 of its 901 samples non-finite, no error, and the
 *     panel announcing "Transient run finished over 2 nodes". The node the source holds
 *     up still drew a convincing flat line; the node behind the capacitor drew nothing
 *     at all, and nothing anywhere said why.
 *
 *   * A CLAMP WITH ONE END. Cycle 6 gave the value box a floor, because a resistance of
 *     zero was being stamped as a 1 pΩ short while the panel read 0 Ω. It never gained a
 *     ceiling, so the other end of the same field was open: 1e308 was accepted, drawn,
 *     saved and reloaded.
 *
 *   * A SWEEP FROM A FREQUENCY TO ITSELF. The From and To boxes are clamped one at a
 *     time and never against each other. From = To ran 220 points at one frequency and
 *     handed the plot a zero-width logarithmic axis, so every gridline, every tick label
 *     and the whole curve mapped to NaN and silently were not drawn — over a status line
 *     saying the sweep had finished.
 *
 *   * A PLOT WIDER THAN ITS BOX. paintPlot measured the PARENT's border box, which under
 *     box-sizing:border-box includes .ckt-plot's 8px of padding on each side. The canvas
 *     came out 16px wider than the space it had at every viewport size, and .ckt's
 *     overflow:hidden clipped the right-hand end of every trace.
 *
 *     node tools/verify_circuit_model.mjs
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { El, stubCtx, windowShim, DOC } from './dom_stub.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

/* ---- the plotting library, loaded as shipped. palette() reads custom properties off
   the document, so hand it a stub and let every colour fall through to its fallback. */
const smod = { exports: {} };
new Function('module', 'PyRunner', 'getComputedStyle', 'document',
  readFileSync(join(ROOT, 'src', 'studio.js'), 'utf8') + '\nmodule.exports = { Sandbox };'
)(smod, { run: async () => {} }, () => ({ getPropertyValue: () => '' }), { documentElement: {} });
const { Sandbox } = smod.exports;

/* ---- requestAnimationFrame that a gate can hold. perFrame() is the editor's answer to
   a slider dragged faster than it can re-solve, and a synchronous rAF would collapse the
   thing being measured: with one, every input event runs its own solve and the gate
   would report perfect coalescing over code that does none. */
let frameQ = [];
const raf = (fn) => { frameQ.push(fn); return frameQ.length; };
const flushFrame = () => { const q = frameQ; frameQ = []; q.forEach((fn) => fn()); };

/* ---- a ResizeObserver a gate can fire. The editor makes one and never disconnects it
   until dispose, so holding the callbacks is how "resize the window mid-interaction"
   gets asked at all. */
const observers = [];
class RO {
  constructor(fn) { this.fn = fn; this.targets = []; observers.push(this); }
  observe(el) { this.targets.push(el); }
  disconnect() { this.targets = []; observers.splice(observers.indexOf(this), 1); }
}
const fireResize = () => observers.slice().forEach((o) => o.fn([]));

const mod = { exports: {} };
new Function('module', 'window', 'requestAnimationFrame', 'ResizeObserver', 'devicePixelRatio',
  /* the editor listens for the browser's own way out of fullscreen, and paints its
     palette icons in whichever ink the page is using */
  'document', 'getComputedStyle',
  'Sandbox',
  readFileSync(join(ROOT, 'src', 'circuit.js'), 'utf8') +
  /* typeof, so a build with no ceiling at all is a finding this gate REPORTS rather
     than a ReferenceError that takes the whole run with it */
  '\nmodule.exports = { createCircuit, Netlist, MNA, PART_KINDS, VALUE_FLOOR,' +
  ' VALUE_CEIL: (typeof VALUE_CEIL === "undefined" ? null : VALUE_CEIL),' +
  ' clampValue, parseEng, fmtEng, ohmsOf, potSplit, Sensors };'
)(mod, windowShim, raf, RO, 1, DOC, () => ({ getPropertyValue: () => '' }), Sandbox);
const { createCircuit, Netlist, MNA, PART_KINDS, VALUE_FLOOR, VALUE_CEIL, clampValue,
  ohmsOf, potSplit, Sensors } = mod.exports;

const problems = [];
const note = (where, line) => {
  const row = problems.find((p) => p[0] === where);
  if (row) row[1].push(line); else problems.push([where, [line]]);
};
function section(name, fn) {
  try { fn(); }
  catch (e) {
    note(name, 'the gate fell over here: ' + (e && e.message) +
      ' — which is a defect in the solver, in the gate, or in both');
  }
}

let solves = 0, refusals = 0, draws = 0;

/* The resize section below models a browser's layout: it lays the plot canvas out at its
   container's width less .ckt-plot's padding, and that is only the right answer while the
   stylesheet says so. A gate enforcing a rule the source has abandoned is a failure this
   repository has already had, so the rule is read back rather than assumed — and if it has
   changed shape, that is itself the finding. */
const CSS = readFileSync(join(ROOT, 'src', 'index.head.html'), 'utf8');
const PLOT_CSS = (() => {
  const wrap = /\.ckt-plot\{[^}]*padding:(\d+)px[^}]*\}/.exec(CSS);
  const canvas = /\.ckt-plot canvas\{([^}]*)\}/.exec(CSS);
  if (!wrap) {
    note('stylesheet', '.ckt-plot no longer declares one padding, so this gate cannot say ' +
      'how wide its canvas ought to be');
    return null;
  }
  if (!canvas || !/width:\s*100%/.test(canvas[1])) {
    note('stylesheet', '.ckt-plot canvas is no longer stretched to its box by CSS — so ' +
      'paintPlot, which measures the canvas itself, measures its own last answer, and ' +
      'the plot can grow on a resize and never shrink again');
    return null;
  }
  const floor = /min-width:\s*(\d+)px/.exec(canvas[1]);
  return { pad: +wrap[1], floor: floor ? +floor[1] : 0 };
})();

/* ================================================================== circuits to feed it
 *
 * Small on purpose. The question is not whether the solver can do a big circuit — the
 * catalogue sweep at the end asks that of all 376 of them — it is what it does when one
 * number in a small one is impossible.
 */
const GND = (id, x, y) => ({ id: id, kind: 'GND', x: x, y: y });

/* V -- R -- node -- X -- gnd, with X whatever kind is under test */
function twoPart(kind, value, rv) {
  return {
    parts: [
      { id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5 },
      { id: 'p1', kind: 'R', x: 6, y: 4, rot: 0, value: rv === undefined ? 1000 : rv },
      { id: 'p2', kind: kind, x: 9, y: 6, rot: 1, value: value },
      GND('p3', 3, 9), GND('p4', 9, 9),
    ],
    wires: [
      { a: [3, 5], b: [3, 4] }, { a: [3, 4], b: [5, 4] }, { a: [7, 4], b: [9, 4] },
      { a: [9, 4], b: [9, 5] }, { a: [3, 7], b: [3, 9] }, { a: [9, 7], b: [9, 9] },
    ],
  };
}

/* a diode to ground, so the Newton path is exercised beside the linear one */
const withDiode = (value) => twoPart('D', value === undefined ? 1e-14 : value);

/* Three resistors in a chain, pin to pin with no wire between them, so deleting the
   last two takes their shared node away with them rather than leaving a wire behind
   that is a node with nothing on it — which the solver would rightly refuse, and the
   picker question below would never get asked. */
const chain = {
  parts: [
    { id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5 },
    { id: 'p1', kind: 'R', x: 6, y: 4, rot: 0, value: 1000 },
    { id: 'p2', kind: 'R', x: 8, y: 4, rot: 0, value: 2000 },
    { id: 'p3', kind: 'R', x: 10, y: 4, rot: 0, value: 3000 },
    GND('p4', 3, 9), GND('p5', 11, 4),
  ],
  wires: [{ a: [3, 5], b: [3, 4] }, { a: [3, 4], b: [5, 4] }, { a: [3, 7], b: [3, 9] }],
};
/* Where the caret lands when it is first woken: the middle of the canvas, which the
   stub lays out at 900x400, is column 18 row 9. caretHome() computes it and this is the
   same arithmetic — stated once here rather than three times below. */
const CARET_HOME = [18, 9];

/* Every number an analysis hands back, flattened. A transient is a list of samples, an
   AC sweep a list of complex vectors, a DC point one vector and a bag of currents —
   three shapes, one question asked of all of them. */
function numbersIn(r) {
  const out = [];
  if (r.v && Array.isArray(r.v)) {
    for (const row of r.v) {
      if (Array.isArray(row)) for (const c of row) (Array.isArray(c) ? out.push(c[0], c[1]) : out.push(c));
      else out.push(row);
    }
  }
  if (r.currents) for (const k of Object.keys(r.currents)) out.push(r.currents[k]);
  if (r.sweep) for (const s of r.sweep) { out.push(s.f); for (const c of s.v) out.push(c[0], c[1]); }
  if (r.t) for (const x of r.t) out.push(x);
  return out;
}

/* The one rule this gate exists for: an analysis either refuses, or every number in what
   it hands back is one a plot can draw and a learner can read. There is no third
   answer — and "success, with NaN in it" was the third answer for as long as the linear
   path had no allFinite. */
function vouches(where, r) {
  if (r.error) { refusals++; return true; }
  solves++;
  const ns = numbersIn(r);
  if (!ns.length) { note('vouch', where + ': reported success and returned nothing at all'); return false; }
  const bad = ns.filter((x) => !isFinite(x)).length;
  if (bad) {
    note('vouch', where + ': reported SUCCESS with ' + bad + ' of ' + ns.length +
      ' numbers non-finite — the panel announces a finished run over a plot of nothing');
    return false;
  }
  return true;
}

/* ---------------------------------------------------------------- 1. the extremes grid
 *
 * Zero, negative, enormous and identical, on every kind whose value reaches a stamp, in
 * all three analyses. The values below the floor and above the ceiling are here because
 * a catalogue file, a saved circuit from before the clamp existed, or a check written by
 * an author all reach Netlist.build without passing the value box.
 */
section('extremes', () => {
  const VALUES = [0, -5, -1e12, 1e-30, 1e-12, 1, 1e6, 1e12, 1e150, 1e300, 1e308];
  const KINDS = ['R', 'C', 'L', 'V', 'I', 'LDR', 'NTC', 'LAMP', 'METER', 'D', 'LED'];
  for (const kind of KINDS) {
    for (const v of VALUES) {
      const m = twoPart(kind, v);
      vouches(kind + '=' + v + ' dc', MNA.dc(Netlist.build(m, null)));
      vouches(kind + '=' + v + ' ac', MNA.ac(Netlist.build(m, null), 10, 1e6, 220));
      vouches(kind + '=' + v + ' tran', MNA.tran(Netlist.build(m, null), 5e-3, 5e-3 / 900));
    }
  }
  /* identical values, which is the case that makes a matrix singular rather than large:
     two sources of the same size across the same pair of nodes, and a divider of two
     equal halves */
  const twin = twoPart('R', 1000);
  twin.parts.push({ id: 'p5', kind: 'V', x: 3, y: 6, rot: 1, value: 5 });
  vouches('two identical supplies in parallel', MNA.dc(Netlist.build(twin, null)));
  vouches('equal halves of a divider', MNA.dc(Netlist.build(twoPart('R', 1000, 1000), null)));

  /* the same grid through the Newton path, which had the check and must keep it */
  for (const v of [0, -5, 1e-30, 1e12, 1e308]) {
    vouches('diode Is=' + v + ' dc', MNA.dc(Netlist.build(withDiode(v), null)));
    vouches('diode Is=' + v + ' tran', MNA.tran(Netlist.build(withDiode(v), null), 5e-3, 5e-3 / 900));
  }

  /* the two spans the panel lets a learner type, at both ends */
  for (const ts of [1e-9, 1e-6, 1, 1e6, 1e30, 1e300]) {
    vouches('tstop=' + ts, MNA.tran(Netlist.build(twoPart('C', 1e-6), null), ts, ts / 900));
  }
  for (const f2 of [1e3, 1e12, 1e100, 1e300, 1e308]) {
    vouches('sweep to ' + f2, MNA.ac(Netlist.build(twoPart('C', 1e-7), null), 10, f2, 220));
  }
});

/* ------------------------------------------------- 2. a range that is not a range */
section('range', () => {
  const net = () => Netlist.build(twoPart('C', 1e-7), null);
  const RANGES = [
    [1000, 1000, 'From and To the same frequency'],
    [0.01, 0.01, 'the same frequency at the bottom of the box'],
    [1e6, 10, 'To below From'],
    [0, 1e6, 'From at zero'],
    [-10, 1e6, 'a negative From'],
    [10, Infinity, 'To at infinity'],
    [NaN, 1e6, 'From that did not parse'],
  ];
  for (const [f1, f2, what] of RANGES) {
    const r = MNA.ac(net(), f1, f2, 220);
    if (!r.error) {
      note('range', what + ' (' + f1 + '..' + f2 + ') was swept rather than refused' +
        (new Set(r.sweep.map((s) => s.f)).size === 1
          ? ' — 220 points at one frequency, which is a zero-width log axis' : ''));
    } else refusals++;
  }
  /* and the range that IS a range must go on working, at both ends of what the boxes
     accept, or this check would have fixed the defect by refusing everything */
  for (const [f1, f2] of [[0.01, 1], [10, 1e6], [1, 1e9]]) {
    const r = MNA.ac(net(), f1, f2, 220);
    if (r.error) note('range', 'a legitimate sweep ' + f1 + '..' + f2 + ' was refused: ' + r.error);
    else vouches('sweep ' + f1 + '..' + f2, r);
  }
});

/* ------------------------------------------------- 3. the clamp, at both ends */
section('clamp', () => {
  if (!VALUE_CEIL) {
    note('clamp', 'there is no VALUE_CEIL: the value box has a floor and no ceiling, so ' +
      'a capacitance of 1e308 F is accepted, drawn, saved and reloaded');
    return;
  }
  /* The union, not the floor table: V and I are deliberately unfloored — a source may
     sit at zero and may be negative — and just as deliberately capped, so a table
     driven off the floors alone would test neither end of them. */
  const kinds = [...new Set([...Object.keys(VALUE_FLOOR), ...Object.keys(VALUE_CEIL)])];
  for (const kind of kinds) {
    const lo = VALUE_FLOOR[kind], hi = VALUE_CEIL[kind];
    if (hi === undefined) { note('clamp', kind + ' has a floor and no ceiling'); continue; }
    if (lo !== undefined && !(hi > lo)) { note('clamp', kind + ': the ceiling ' + hi + ' is not above the floor ' + lo); continue; }
    for (const v of [0, -5, -1e300, 1e-300, 1e308, Infinity, -Infinity, NaN,
                     (lo === undefined ? 1 : lo) / 10, hi * 10, -hi * 10]) {
      const got = clampValue(kind, v, lo === undefined ? 1 : lo);
      if (!isFinite(got) || Math.abs(got) > hi || (lo !== undefined && got < lo)) {
        note('clamp', kind + ': ' + v + ' clamped to ' + got + ', outside what the stamps can use');
      }
      /* an unfloored kind keeps its sign, or superposition cannot be written */
      if (lo === undefined && isFinite(v) && v < 0 && got > 0) {
        note('clamp', kind + ': ' + v + ' came back positive — a source\'s sign is its direction');
      }
    }
  }
  /* A ceiling that is not above what the catalogue already uses would condemn working
     content, which is worse than the defect it was written to catch. */
  const asList = (x) => (!x ? [] : Array.isArray(x) ? x : [x]);
  const walk = (m, where) => {
    if (!m || !m.parts) return;
    for (const p of m.parts) {
      if (p.value === undefined) continue;
      const v = Math.abs(Number(p.value));
      const lo = VALUE_FLOOR[p.kind], hi = VALUE_CEIL[p.kind];
      if (lo !== undefined && v !== 0 && v < lo) note('clamp', where + ': ' + p.kind + ' = ' + p.value + ' is under the floor ' + lo);
      if (hi !== undefined && v > hi) note('clamp', where + ': ' + p.kind + ' = ' + p.value + ' is over the ceiling ' + hi);
      /* a value at zero is the floor's job and cycle 6 already checked it */
    }
    for (const p of m.parts) if (p.model) walk(p.model, where);
  };
  for (const f of readdirSync(join(ROOT, 'catalog')).filter((x) => x.endsWith('.json') && !x.startsWith('_'))) {
    const c = JSON.parse(readFileSync(join(ROOT, 'catalog', f), 'utf8'));
    (c.modules || []).forEach((m, mi) => {
      const at = c.id + '/M' + (mi + 1);
      for (const b of asList(m.build)) { walk(b.solution, at); walk(b.start, at); }
      for (const q of asList(m.numeric)) walk(q.diagram, at);
      for (const q of asList(m.quiz)) walk(q.diagram, at);
      for (const t of asList(m.tune)) walk(t.model, at);
    });
  }
});

/* ------------------------------------------------- 3b. the panel and the stamp agree
 *
 * A floor is only honest if a value AT it reaches the solver unchanged. Cycle 6 wrote
 * the table "checked against the floor its own stamp needs" and for R, C and L that is
 * what it was; for the five kinds whose resistance is RESOLVED rather than typed it was
 * not. ohmsOf holds a lamp at 1 mΩ and a meter at 1 µΩ, potSplit holds a track at 1 mΩ
 * per half, and Sensors holds both R10 and R25 at 1 Ω — while the table let all five
 * down to a micro-ohm. So an LDR set to a micro-ohm was accepted, drawn, saved and
 * reloaded at a micro-ohm and stamped at one ohm: the panel reading one number and the
 * solver using another, which is the defect the floor exists to close, surviving in a
 * third of the kinds it was written for.
 *
 * Each resolver is asked at ITS OWN reference point, where the model is the identity —
 * 10 lx is the light an R10 is quoted at, 25 °C the temperature an R25 is — so anything
 * that comes back other than the value is a guard biting and not the physics.
 */
section('stamped', () => {
  const RESOLVE = {
    LDR: (v) => Sensors.ldr(v, 0.7, 10),
    NTC: (v) => Sensors.ntc(v, 3950, 25),
    LAMP: (v) => ohmsOf({ kind: 'LAMP', value: v }, null),
    METER: (v) => ohmsOf({ kind: 'METER', value: v }, null),
    POT: (v) => { const r = potSplit({ kind: 'POT', value: v }); return r[0] + r[1]; },
  };
  for (const kind of Object.keys(RESOLVE)) {
    for (const [what, v] of [['floor', VALUE_FLOOR[kind]], ['ceiling', VALUE_CEIL && VALUE_CEIL[kind]]]) {
      if (v === undefined || v === null) continue;
      const got = RESOLVE[kind](v);
      /* exact, not close: the point is that nothing replaced the number */
      if (Math.abs(got - v) > Math.abs(v) * 1e-12) {
        note('stamped', kind + ' at its ' + what + ' (' + v + ') is stamped as ' + got +
          ' — ' + (got / v).toExponential(1) + ' times the number on the panel, which the ' +
          'learner then saves and reloads');
      }
    }
  }
  /* And one end to end, because a resolver agreeing with itself is not the same as the
     matrix agreeing with the panel: a lone resistor across 5 V must pass 5/R. */
  for (const R of [VALUE_FLOOR.R, 1000, VALUE_CEIL ? VALUE_CEIL.R : 1e12]) {
    const m = {
      parts: [{ id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5 },
              { id: 'p1', kind: 'R', x: 6, y: 4, rot: 0, value: R }, GND('p2', 3, 9), GND('p3', 7, 6)],
      wires: [{ a: [3, 5], b: [3, 4] }, { a: [3, 4], b: [5, 4] }, { a: [7, 4], b: [7, 6] },
              { a: [3, 7], b: [3, 9] }],
    };
    const r = MNA.dc(Netlist.build(m, null));
    if (r.error) { note('stamped', 'a lone ' + R + ' Ω resistor across 5 V would not solve: ' + r.error); continue; }
    solves++;
    const i = Math.abs(r.currents.p0);
    const want = 5 / R;
    if (Math.abs(i - want) > want * 1e-6) {
      note('stamped', 'a ' + R + ' Ω resistor across 5 V passes ' + i.toExponential(4) +
        ' A, not ' + want.toExponential(4) + ' — the stamp is not using the value on the panel');
    }
  }
});

/* ================================================================== the editor itself */
function mount(opts) {
  const root = new El('div');
  const handle = createCircuit(root, Object.assign({ model: chain }, opts || {}));
  const cv = root.querySelector('.ckt-canvas canvas');
  const plotWrap = root.querySelector('[data-plot]');
  const plotCv = plotWrap.querySelector('canvas');
  const say = () => (root.querySelector('[data-say]') || { textContent: '' }).textContent.trim();
  const key = (k, extra) => {
    const ev = Object.assign({ type: 'keydown', key: k, code: k === ' ' ? 'Space' : k,
      shiftKey: false, ctrlKey: false, metaKey: false, altKey: false, target: cv }, extra || {});
    cv.dispatchEvent(ev);
    return ev;
  };
  const click = (el) => el && el.dispatchEvent({ type: 'click', target: el });
  const mode = (m) => click(root.querySelector('[data-an="' + m + '"]'));
  const field = (sel, v) => {
    const el = root.querySelector(sel);
    if (!el) throw new Error('no ' + sel + ' on the panel');
    el.value = v;
    el.dispatchEvent({ type: 'change', target: el });
  };
  const run = () => { click(root.querySelector('.ckt-run')); draws++; };
  /* Walk the caret from its home cell to a grid cell and back, which is the only route
     into the canvas that has no screen coordinate in it. The first Enter wakes the
     caret and does nothing else, so it is pressed by the caller before any of this. */
  const walkTo = (cell) => {
    const dx = cell[0] - CARET_HOME[0], dy = cell[1] - CARET_HOME[1];
    for (let i = 0; i < Math.abs(dx); i++) key(dx > 0 ? 'ArrowRight' : 'ArrowLeft');
    for (let i = 0; i < Math.abs(dy); i++) key(dy > 0 ? 'ArrowDown' : 'ArrowUp');
    return () => {
      for (let i = 0; i < Math.abs(dx); i++) key(dx > 0 ? 'ArrowLeft' : 'ArrowRight');
      for (let i = 0; i < Math.abs(dy); i++) key(dy > 0 ? 'ArrowUp' : 'ArrowDown');
    };
  };
  return { root, handle, cv, plotWrap, plotCv, say, key, click, mode, field, run, walkTo,
    err: () => { const e = root.querySelector('.ckt-err'); return e ? e.textContent.trim() : ''; },
    nodes: () => root.querySelectorAll('[data-node]'),
    tool: (t) => click(root.querySelector('[data-tool="' + t + '"]')),
    model: () => handle.getModel() };
}

/* ------------------------------------------------- 3c. the correction says which end
 *
 * A value silently corrected is a correction nobody learns from, which is why the box
 * says what it did. It now has two ends to say, and the first version of the sentence
 * chose between them by comparing magnitudes — so −5 Ω, which is larger than the floor
 * it lands on, was told it was too big for the arithmetic to hold. The end that was
 * actually hit is a fact about the ceiling, not about the two numbers.
 */
section('correction', () => {
  const h = mount();
  h.tool('select');
  h.key('Enter');
  h.walkTo([6, 4]);                     /* the first resistor in the chain */
  h.key('Enter');
  const box = h.root.querySelector('[data-val]');
  if (!box) { note('correction', 'the gate could not reach the value box'); h.handle.dispose(); return; }
  for (const [typed, want, why] of [
    ['-5', /more than zero/, 'a negative resistance'],
    ['0', /more than zero/, 'a resistance of zero'],
    ['1e308', /arithmetic/, 'a resistance too large to stamp'],
  ]) {
    box.value = typed;
    box.dispatchEvent({ type: 'change', target: box });
    const said = h.say();
    if (!want.test(said)) {
      note('correction', why + ' typed as "' + typed + '" was corrected and announced as ' +
        '"' + said + '", which is the wrong end of the clamp');
    }
  }
  h.handle.dispose();
});

/* ------------------------------------------------- 4. what the plot actually draws */
section('plot', () => {
  for (const m of ['ac', 'tran']) {
    const h = mount();
    h.mode(m);
    h.run();
    if (h.err()) { note('plot', m + ': a plain three-resistor chain would not solve — ' + h.err()); h.handle.dispose(); continue; }
    if (h.plotWrap.hidden) { note('plot', m + ': solved and left the plot hidden'); h.handle.dispose(); continue; }
    const bad = (h.plotCv._ctx && h.plotCv._ctx.bad) || [];
    if (bad.length) note('plot', m + ': ' + bad.length + ' coordinate(s) nobody can draw, first ' + bad[0]);
    if (!h.plotCv._ctx || !h.plotCv._ctx.frames.length) note('plot', m + ': nothing was drawn on the plot at all');
    /* The plot is a picture and has to say what it is a picture OF — every other canvas
       in this app was named by cycle 2 or cycle 6 and this one was left bare. The name
       has to be about the plot that is there, not the placeholder: it must name the node
       and carry numbers off the curve. */
    if (h.plotCv.getAttribute('role') !== 'img') note('plot', m + ': the plot canvas has no role');
    const name = h.plotCv.getAttribute('aria-label') || '';
    if (!/node \d/.test(name) || /Press Solve/.test(name) || !/\d/.test(name.replace(/node \d/, ''))) {
      note('plot', m + ': the plot is named "' + name + '", which does not describe the plot that is on the screen');
    }
    if (/NaN|undefined|Infinity/.test(name)) note('plot', m + ': the plot names itself "' + name + '"');
    h.handle.dispose();
  }

  /* From and To typed as the same number, and To typed below From. Either the panel
     refuses and says which of the two boxes is the problem, or it draws — and if it
     draws, every coordinate has to be one a canvas can take. What it must not do is
     announce a finished sweep over a plot with no gridline, no tick label and no
     curve on it, which is what a zero-width logarithmic axis produces. */
  for (const [from, to, what] of [['1 kHz', '1 kHz', 'from 1 kHz to 1 kHz'],
                                  ['1 MHz', '10 Hz', 'from 1 MHz down to 10 Hz']]) {
    const h = mount();
    h.mode('ac');
    h.field('[data-f1]', from);
    h.field('[data-f2]', to);
    h.run();
    const bad = (h.plotCv._ctx && h.plotCv._ctx.bad) || [];
    if (h.err()) {
      refusals++;
      if (!/frequenc|From|To/.test(h.err())) {
        note('plot', 'a sweep ' + what + ' was refused without saying which box is wrong: ' + h.err());
      }
      if (!/frequenc/i.test(h.say())) {
        note('plot', 'a sweep ' + what + ' was refused on screen and the status line did not say so');
      }
    } else if (bad.length) {
      note('plot', 'a sweep ' + what + ' reported success and put ' + bad.length +
        ' non-finite coordinates on the plot, first ' + bad[0]);
    }
    h.handle.dispose();
  }
});

/* ------------------------------------------------- 5. the picker and the plot agree */
section('picker', () => {
  const h = mount();
  h.mode('ac');
  h.run();
  const before = h.nodes();
  if (before.length < 3) { note('picker', 'the chain solved to ' + before.length + ' nodes, not 3 — the gate cannot ask its question'); h.handle.dispose(); return; }
  h.click(before[before.length - 1]);          /* plot the highest node */

  /* Two resistors off the end of the chain, so the node between them disappears.
     Deleted through the keyboard because that is the route with no screen coordinate
     in it — and because cycle 6 built it for exactly this kind of use. */
  h.tool('select');
  h.key('Enter');                               /* wake the caret at its home cell */
  for (const [id, cell] of [['p3', [10, 4]], ['p2', [8, 4]]]) {
    const was = h.model().parts.length;
    const back = h.walkTo(cell);
    h.key('Enter');                             /* select what is under the caret */
    h.key('Delete');
    back();
    if (h.model().parts.length !== was - 1) {
      note('picker', 'the gate could not delete ' + id + ' with the keyboard, so it cannot ask its question');
      h.handle.dispose();
      return;
    }
  }

  h.run();
  if (h.err()) { note('picker', 'the shortened chain would not solve: ' + h.err()); h.handle.dispose(); return; }
  const after = h.nodes();
  const pressed = after.filter((b) => b.getAttribute('aria-pressed') === 'true');
  if (pressed.length !== 1) {
    note('picker', 'after the node the learner picked stopped existing, ' + pressed.length +
      ' of ' + after.length + ' node buttons say they are the one being plotted — the plot ' +
      'falls back to the highest node there is and the picker says nothing about it');
  }
  h.handle.dispose();
});

/* ------------------------------------------------- 6. resize, mid-interaction */
section('resize', () => {
  const h = mount();
  h.mode('tran');
  h.run();
  if (h.err()) { note('resize', 'the chain would not solve, so there is no plot to resize'); h.handle.dispose(); return; }
  if (!PLOT_CSS) { h.handle.dispose(); return; }
  /* .ckt-plot carries its padding under box-sizing:border-box, so the space its canvas
     actually has is the parent's box less twice that. A browser lays a width:100% canvas
     out at exactly that, held at min-width; the gate does the same sum from the numbers
     it just read out of the stylesheet, and then checks the backing store agrees. */
  const PAD = PLOT_CSS.pad;
  for (const W of [1200, 900, 640, 375, 320]) {
    h.plotWrap.resize(W, 190 + PAD * 2);
    h.plotCv.resize(Math.max(PLOT_CSS.floor, W - PAD * 2), 190);
    fireResize();
    draws++;
    const want = Math.max(PLOT_CSS.floor, W - PAD * 2);
    const got = h.plotCv.width;                       /* devicePixelRatio is 1 here */
    if (got !== want) {
      note('resize', 'at ' + W + 'px the plot asks for ' + got + ' pixels of a box that is ' +
        want + ' wide' + (got > want ? ' — .ckt overflow:hidden clips the difference off the ' +
        'right-hand end of the trace' : ''));
    }
    const bad = (h.plotCv._ctx && h.plotCv._ctx.bad) || [];
    if (bad.length) { note('resize', 'at ' + W + 'px the plot drew ' + bad.length + ' coordinate(s) nobody can draw'); break; }
  }
  /* and the schematic itself, at the narrowest the app ever is */
  h.root.querySelector('.ckt-canvas').resize(343, 340);
  fireResize();
  draws++;
  const cbad = (h.cv._ctx && h.cv._ctx.bad) || [];
  if (cbad.length) note('resize', 'at 343px the schematic drew ' + cbad.length + ' coordinate(s) nobody can draw, first ' + cbad[0]);
  h.handle.dispose();
});

/* ------------------------------------------------- 7. faster than it can re-solve */
section('rapid', () => {
  /* A potentiometer, because its wiper is the one continuous control every schematic
     can have and it is wired straight to a re-solve. */
  const pot = {
    parts: [
      { id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5 },
      { id: 'p1', kind: 'POT', x: 8, y: 4, rot: 0, value: 10000, wiper: 0.5 },
      GND('p2', 3, 9), GND('p3', 10, 9),
    ],
    wires: [
      { a: [3, 5], b: [3, 4] }, { a: [3, 4], b: [7, 4] },
      { a: [9, 4], b: [10, 4] }, { a: [10, 4], b: [10, 9] }, { a: [3, 7], b: [3, 9] },
    ],
  };
  let saves = 0;
  const h = mount({ model: pot, onChange: () => { saves++; } });
  h.mode('tran');
  h.run();
  /* select the pot, so its panel — and the wiper on it — exist */
  h.tool('select');
  h.key('Enter');                               /* wake the caret */
  h.walkTo([8, 4]);
  h.key('Enter');                               /* and select what is under it */
  const wip = h.root.querySelector('[data-wiper]');
  if (!wip) { note('rapid', 'the gate could not reach the wiper, so it cannot ask its question'); h.handle.dispose(); return; }

  const before = saves;
  frameQ = [];
  for (let i = 0; i < 60; i++) {
    wip.value = String(i * 16);
    wip.dispatchEvent({ type: 'input', target: wip });
  }
  const queued = frameQ.length;
  if (queued !== 1) {
    note('rapid', '60 wiper events in one frame queued ' + queued + ' re-solves; a 220-point ' +
      'sweep costs one matrix per point and the slider would drag like treacle');
  }
  flushFrame();
  draws++;
  if (saves <= before) note('rapid', 'dragging the wiper never told the outside world anything');

  /* and the one that matters more than the cost: a solve queued before dispose must not
     run after it, because solve() reaches onChange and onChange is what saves */
  const savedAtDispose = saves;
  wip.dispatchEvent({ type: 'input', target: wip });
  h.handle.dispose();
  flushFrame();
  if (saves !== savedAtDispose) {
    note('rapid', 'a re-solve queued before dispose() ran afterwards and wrote the ' +
      'learner\'s saved circuit from an editor nothing was showing');
  }
});

/* ------------------------------------------------- 8. the whole catalogue, all three ways
 *
 * The regression net. Every published schematic must go on giving the numbers it gives
 * today — verify_circuits and verify_numeric check that — and must also survive the two
 * analyses those gates never run on it. A fix that turned a working exercise into a
 * refusal would show up here as a refusal count that moved.
 */
section('catalogue', () => {
  const asList = (x) => (!x ? [] : Array.isArray(x) ? x : [x]);
  const models = [];
  for (const f of readdirSync(join(ROOT, 'catalog')).filter((x) => x.endsWith('.json') && !x.startsWith('_'))) {
    const c = JSON.parse(readFileSync(join(ROOT, 'catalog', f), 'utf8'));
    (c.modules || []).forEach((m, mi) => {
      const at = c.id + '/M' + (mi + 1);
      for (const b of asList(m.build)) {
        if (b.solution) models.push([at + ' solution', b.solution]);
        if (b.start) models.push([at + ' start', b.start]);
      }
      for (const q of asList(m.numeric)) if (q.diagram) models.push([at + ' numeric', q.diagram]);
      for (const q of asList(m.quiz)) if (q.diagram) models.push([at + ' quiz', q.diagram]);
    });
  }
  let solvedDC = 0;
  for (const [at, m] of models) {
    const dc = MNA.dc(Netlist.build(m, null));
    if (vouches(at + ' dc', dc) && !dc.error) solvedDC++;
    vouches(at + ' ac', MNA.ac(Netlist.build(m, null), 10, 1e6, 60));
    vouches(at + ' tran', MNA.tran(Netlist.build(m, null), 1e-3, 1e-3 / 120));
  }
  if (solvedDC < 200) {
    note('catalogue', 'only ' + solvedDC + ' of ' + models.length + ' published schematics ' +
      'reached a DC answer — a fix has turned working content into a refusal');
  }
  console.log('[ok  ] catalogue  ' + models.length + ' published schematics, ' + solvedDC +
    ' with a DC operating point, all three analyses');
});

/* ---------------------------------------------------------------- report */
for (const [where, lines] of problems) {
  console.log('[FAIL] ' + where);
  lines.forEach((l) => console.log('            ' + l));
}
console.log(problems.length
  ? '\n' + problems.reduce((n, p) => n + p[1].length, 0) + ' solver problem(s)'
  : '\nAll good: ' + solves + ' analyses vouch for every number they return and ' + refusals +
    ' refuse rather than guess · ' + draws + ' plots and repaints, none of them ' +
    'unpaintable · the value clamp holds ' + Object.keys(VALUE_FLOOR).length + ' kinds off ' +
    'a floor and ' + (VALUE_CEIL ? Object.keys(VALUE_CEIL).length : 0) + ' under a ceiling.');
process.exit(problems.length ? 1 : 0);
