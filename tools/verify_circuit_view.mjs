/**
 * verify_circuit_view.mjs — the gate for what the schematic canvas DRAWS.
 *
 * Four gates already point at this editor and not one of them judges the drawing.
 * verify_circuit_ui.mjs says so in its own header — it drives the keyboard and the
 * lifetime, and "nothing here judges the drawing". verify_circuit_model.mjs took the
 * solver and the analysis plot, and left the schematic canvas alone. verify_circuits
 * and verify_numeric ask whether an answer is right, which is a question about the
 * netlist and not about the picture. So the largest drawing surface in the app — 386
 * published schematics, 85 graded build exercises, and every learner's own saved work —
 * had never been fed a hostile coordinate, resized mid-gesture, or driven faster than
 * it repaints, which is this track's brief almost word for word.
 *
 * Eight sections, driving the shipped createCircuit rather than a copy of it:
 *
 *   1  a drawing the editor was handed is not one it can trust — every hostile shape
 *      recovered or dropped, and never quietly moved to the origin
 *   2  the catalogue survives that sanitising UNCHANGED, because a guard that edits
 *      published content is worse than the defect it was written for
 *   3  no loop a caller can hang: Fit and paint at and past the arithmetic, on a clock
 *   4  nothing unpaintable reaches the canvas, at seven widths, both modes
 *   5  faster than it can repaint: N gestures in one frame are one repaint
 *   6  the canvas says what is on it, and stops saying it when nothing moved
 *   7  Fit reports the zoom it reached, and says when it could not fit
 *   8  every published schematic draws, inside its own canvas, at a legible scale
 *
 *     node tools/verify_circuit_view.mjs
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { El, windowShim } from './dom_stub.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = readFileSync(join(ROOT, 'src', 'circuit.js'), 'utf8');

/* A DEFERRED frame queue, and the reason is written down rather than left to be
   rediscovered. perFrame sets `pending`, asks for a frame, and the callback clears
   `pending` before it runs. Hand that an immediate stub — `(fn) => fn()`, which the two
   older editor gates use because they are not measuring coalescing — and every call
   runs synchronously with `pending` already false again, so a perfectly good coalescer
   reports one repaint per event and section 5 can never fail. Cycle 15 shipped that
   mistake into a first draft and had to repair the gate; this one starts from the
   repair. */
const queue = [];
const raf = (fn) => { queue.push(fn); return queue.length; };
const flushFrame = () => { const q = queue.splice(0); q.forEach((f) => f()); };

/* A ResizeObserver the gate can fire. The two older editor gates pass `undefined` and so
   never exercise the observer at all, which means the resize path — the one this track's
   brief names outright — has never been driven. Recording the callbacks and calling them
   is what "resize the window mid-interaction" actually is: a browser does not repaint a
   canvas because its box moved, it calls this. */
const observers = [];
class RO {
  constructor(cb) { this.cb = cb; this.targets = []; observers.push(this); }
  observe(el) { this.targets.push(el); }
  disconnect() { this.targets = []; observers.splice(observers.indexOf(this), 1); }
}
const resizeTo = (el, w, h) => {
  el.resize(w, h);
  observers.forEach((o) => { if (o.targets.includes(el)) o.cb([{ target: el }]); });
};

const mod = { exports: {} };
new Function('module', 'window', 'requestAnimationFrame', 'ResizeObserver', 'devicePixelRatio',
  SRC + '\nmodule.exports = { createCircuit, Netlist, MNA, sanitiseDrawing, cellOf, ' +
        'CELL_LIMIT, DRAW_DEPTH, PART_KINDS, VALUE_CEIL };'
)(mod, windowShim, raf, RO, 1);
const { createCircuit, Netlist, sanitiseDrawing, cellOf, CELL_LIMIT, DRAW_DEPTH } = mod.exports;

const problems = [];
const note = (where, line) => {
  const row = problems.find((p) => p[0] === where);
  if (row) row[1].push(line); else problems.push([where, [line]]);
};
function section(name, fn) {
  try { fn(); }
  catch (e) {
    note(name, 'the gate fell over here: ' + (e && e.message) +
      ' — which is a defect in the editor, in the gate, or in both');
  }
}

let mounts = 0, paints = 0, hostile = 0, drawn = 0;

/* ---- the harness ---- */
function mount(opts, w, h) {
  const root = new El('div');
  const handle = createCircuit(root, Object.assign({ onChange() {} }, opts || {}));
  mounts++;
  const cv = root.querySelector('.ckt-canvas canvas');
  const ctx = cv.getContext('2d');
  /* The transform the editor actually set, recorded here rather than in dom_stub.mjs.
     The stub is shared with the two older editor gates, and adding to it would mean
     re-proving both report identically; a spy that lives in the gate that needs it costs
     nobody anything. `lastTransform` is the viewport in force when the drawing was laid
     down — the read-only fit, or the editor's own pan and zoom. */
  if (!ctx._spied) {
    ctx._spied = true;
    const of = ctx.setTransform;
    ctx.setTransform = (...a) => { ctx.lastTransform = a.slice(); return of(...a); };
  }
  if (w) { resizeTo(cv.parentElement, w, h === undefined ? 400 : h); }
  flushFrame();
  return {
    root, handle, cv, ctx,
    say: () => (root.querySelector('[data-say]') || { textContent: '' }).textContent.trim(),
    act: (name) => {
      const b = root.querySelector('[data-act="' + name + '"]');
      if (b) b.dispatchEvent({ type: 'click' });
      flushFrame();
    },
    tool: (t) => {
      root.querySelectorAll('[data-tool]').forEach((b) => {
        if (b.dataset.tool === t) b.dispatchEvent({ type: 'click' });
      });
      flushFrame();
    },
    key: (k, extra) => {
      cv.dispatchEvent(Object.assign({ type: 'keydown', key: k, code: k, target: cv,
        shiftKey: false, ctrlKey: false, metaKey: false, altKey: false }, extra || {}));
      flushFrame();
    },
  };
}

/* ------------------------------------------------- 1. a drawing on trust
 *
 * Both shapes below were measured through the shipped editor before the guard existed:
 * a coordinate of 1e17 froze the tab on the first press of Fit, and a coordinate that
 * came back from a save as the string "6" put one pin of a resistor at cell 5 and the
 * other at cell "61", so the netlist joined a node 55 cells from the drawing.
 *
 * The rule this section enforces is not a list of the shapes already known to be wrong.
 * It is: whatever comes in, what comes out is a NUMBER inside the stated bound, or the
 * part is not there at all. In particular a missing coordinate must be DROPPED and not
 * read as zero — Number(null), Number(false) and Number('') are all 0, so the lazy
 * version of this guard silently moves a part to the origin, on top of whatever is
 * already there, and the netlist joins them. A part that is gone is visible. A part in
 * the wrong place is a different circuit that looks like a right one.
 */
section('trust', () => {
  const drop = [NaN, Infinity, -Infinity, null, undefined, true, false, '', '   ',
    'abc', {}, [], 1e7, -1e7, 1e308, 1e17, 2 ** 58];
  const keep = [[0, 0], [5, 5], [-5, -5], [7.6, 8], [-7.4, -7], ['7', 7], [' 12 ', 12],
    [CELL_LIMIT, CELL_LIMIT], [-CELL_LIMIT, -CELL_LIMIT]];
  for (const v of drop) {
    hostile++;
    if (cellOf(v) !== null) {
      note('trust', 'cellOf(' + JSON.stringify(v) + ') returned ' + cellOf(v) +
        ' instead of refusing — a coordinate that cannot be recovered must be dropped');
    }
    const out = sanitiseDrawing({ parts: [{ id: 'p0', kind: 'R', x: v, y: 4, value: 1e3 }], wires: [] }, 0);
    if (out.parts.length) {
      note('trust', 'a part with x = ' + JSON.stringify(v) + ' survived at x = ' +
        JSON.stringify(out.parts[0].x) + ' — it must be dropped, not placed');
    }
    const wo = sanitiseDrawing({ parts: [], wires: [{ a: [v, 2], b: [5, 2] }] }, 0);
    if (wo.wires.length) note('trust', 'a wire ending at ' + JSON.stringify(v) + ' survived');
  }
  for (const [v, want] of keep) {
    hostile++;
    const out = sanitiseDrawing({ parts: [{ id: 'p0', kind: 'R', x: v, y: 4, value: 1e3 }], wires: [] }, 0);
    if (!out.parts.length) { note('trust', 'a part at x = ' + JSON.stringify(v) + ' was dropped'); continue; }
    const got = out.parts[0].x;
    if (got !== want || typeof got !== 'number') {
      note('trust', 'x = ' + JSON.stringify(v) + ' became ' + JSON.stringify(got) +
        ' (' + typeof got + '), wanted the number ' + want);
    }
  }
  /* the string case end to end: the pins the netlist builds must be the pins drawn */
  const strung = sanitiseDrawing({ parts: [{ id: 'p1', kind: 'R', x: '6', y: 4, rot: 0, value: 1e3 }], wires: [] }, 0);
  const pins = Netlist.pinsOf(strung.parts[0]);
  if (!pins.every((pt) => pt.every((n) => typeof n === 'number' && isFinite(n)))) {
    note('trust', 'a part saved with a string coordinate still reports pins at ' +
      JSON.stringify(pins) + ' — the solver would answer about a circuit that is not drawn');
  }
  /* a sanitiser that drops what it was not asked about is its own defect */
  const carried = sanitiseDrawing({ parts: [], wires: [], env: { lux: 200 }, title: 'keep' }, 0);
  if (carried.env === undefined || carried.title !== 'keep') {
    note('trust', 'sanitiseDrawing dropped a field that is not geometry');
  }
  /* nesting is bounded by the number the netlist bounds itself by, not a second opinion */
  let deep = { parts: [], wires: [] };
  for (let i = 0; i < DRAW_DEPTH + 4; i++) {
    deep = { parts: [{ id: 'b', kind: 'IC', x: 2, y: 2, inner: deep, ports: [] }], wires: [] };
  }
  let d = sanitiseDrawing(deep, 0), levels = 0;
  while (d.parts.length && d.parts[0].inner) { d = d.parts[0].inner; levels++; }
  if (levels > DRAW_DEPTH) note('trust', 'nesting survived ' + levels + ' deep, past DRAW_DEPTH');
  /* a port is a cell too, and reaches paint() through pinsOf exactly as a part does */
  const ports = sanitiseDrawing({ parts: [{ id: 'b', kind: 'IC', x: 2, y: 2,
    ports: [{ cells: [[0, 0], [1e17, 3], [NaN, 1]] }] }], wires: [] }, 0);
  if ((ports.parts[0].ports[0].cells || []).length !== 1) {
    note('trust', 'a block port kept a cell it cannot draw: ' +
      JSON.stringify(ports.parts[0].ports[0].cells));
  }
  console.log('[ok  ] trust     ' + hostile + ' hostile coordinates recovered or dropped, ' +
    'never moved to the origin · ports, nesting and non-geometry fields held');
});

/* ------------------------------------------------- 2. the catalogue is not edited
 *
 * The guard above rewrites every drawing that reaches the editor. If it changed one that
 * is already correct it would be condemning working content, which is worse than the
 * defect it was written for — cycle 8's rule about the value ceiling, applied to
 * geometry. Every published drawing must come out of it byte-identical.
 */
function catalogueDrawings() {
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
  return models;
}
const CATALOGUE = catalogueDrawings();

section('catalogue', () => {
  let moved = 0;
  for (const [at, m] of CATALOGUE) {
    const before = JSON.stringify(m);
    const after = JSON.stringify(sanitiseDrawing(JSON.parse(before), 0));
    if (before !== after) {
      moved++;
      if (moved <= 3) {
        note('catalogue', at + ' is changed by the sanitiser — published content must ' +
          'pass through it untouched');
      }
    }
  }
  if (moved > 3) note('catalogue', 'and ' + (moved - 3) + ' more');
  console.log('[ok  ] catalogue ' + CATALOGUE.length + ' published drawings pass through ' +
    'the guard unchanged');
});

/* ------------------------------------------------- 3. no loop a caller can hang
 *
 * paint()'s grid was `for (X = start; X < end; X += GRID)`, and a step is only a step
 * while the numbers are small: above 2^58 adding 26 to a double does not change it, so X
 * stops advancing and the condition stays true. zoomFit puts the viewport at about 13
 * times the largest coordinate, so ONE wire ending at x = 1e17 in a saved circuit froze
 * the page on the first press of Fit — measured, and not slowly: it had not returned
 * when the run was killed at 25 seconds, and there is no way out of it but closing the
 * tab. Every case here is on a clock, and the threshold itself is asserted so the bound
 * cannot silently drift past it.
 */
section('bounded', () => {
  const step = 26;
  let x = 1;
  for (let i = 0; i < 200; i++) { const n = x * 2; if (n + step === n) { x = n; break; } x = n; }
  if (x + step !== x) note('bounded', 'could not find the arithmetic threshold to assert against');
  if (CELL_LIMIT * 13 * 26 >= x) {
    note('bounded', 'CELL_LIMIT of ' + CELL_LIMIT + ' allows a viewport of ' +
      (CELL_LIMIT * 13 * 26).toExponential(2) + ', at or past the ' + x.toExponential(3) +
      ' where a grid step stops advancing — the bound no longer bounds the loop');
    /* and stop. Everything below mounts drawings at the limit, and the line above has
       just said the limit no longer keeps the loop finite: running on would not report a
       second problem, it would hang the gate. */
    return;
  }
  const BUDGET = 4000;
  const shapes = [
    ['a wire at the limit', { parts: [], wires: [{ a: [CELL_LIMIT, 2], b: [5, 2] }] }],
    ['a wire past it', { parts: [], wires: [{ a: [1e17, 2], b: [5, 2] }] }],
    ['a part past it', { parts: [{ id: 'p0', kind: 'R', x: 1e18, y: 4, value: 1e3 }], wires: [] }],
    ['1e308', { parts: [{ id: 'p0', kind: 'R', x: 1e308, y: 1e308, value: 1e3 }], wires: [] }],
    ['Infinity', { parts: [{ id: 'p0', kind: 'R', x: Infinity, y: 4, value: 1e3 }], wires: [] }],
    ['NaN', { parts: [{ id: 'p0', kind: 'R', x: NaN, y: NaN, value: 1e3 }], wires: [] }],
    ['a span across the limit', { parts: [
      { id: 'p0', kind: 'R', x: -CELL_LIMIT, y: 0, value: 1e3 },
      { id: 'p1', kind: 'R', x: CELL_LIMIT, y: 0, value: 1e3 }], wires: [] }],
  ];
  for (const [name, model] of shapes) {
    const t0 = Date.now();
    const m = mount({ model });
    m.act('fit');
    m.act('zoomout'); m.act('zoomout'); m.act('zoomin');
    paints += 4;
    const ms = Date.now() - t0;
    if (ms > BUDGET) {
      note('bounded', name + ': mounting, fitting and zooming took ' + ms + ' ms — a ' +
        'viewport this far out is walking a loop it should have counted');
    }
    if (m.ctx.bad.length) {
      note('bounded', name + ': ' + m.ctx.bad.length + ' unpaintable coordinate(s), e.g. ' + m.ctx.bad[0]);
    }
  }
  console.log('[ok  ] bounded   ' + shapes.length + ' drawings at and past the arithmetic ' +
    'return · the grid step asserted against ' + x.toExponential(3));
});

/* ------------------------------------------------- 4. nothing unpaintable, at any width */
section('paints', () => {
  const SIZES = [[1600, 900], [1200, 800], [900, 400], [820, 400], [640, 400], [375, 400], [320, 260]];
  const model = {
    parts: [
      { id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5 },
      { id: 'p1', kind: 'R', x: 6, y: 4, rot: 0, value: 1000 },
      { id: 'p2', kind: 'C', x: 9, y: 6, rot: 1, value: 1e-7 },
      { id: 'p3', kind: 'GND', x: 3, y: 9 },
      { id: 'p4', kind: 'OUT', x: 9, y: 4 },
    ],
    wires: [{ a: [3, 5], b: [3, 4] }, { a: [3, 4], b: [5, 4] }, { a: [7, 4], b: [9, 4] },
            { a: [9, 4], b: [9, 5] }, { a: [3, 7], b: [3, 9] }],
  };
  for (const [w, h] of SIZES) {
    for (const readOnly of [false, true]) {
      const m = mount(readOnly ? { model, readOnly: true, label: 'A filter' } : { model }, w, h);
      if (!readOnly) { m.act('fit'); m.act('zoomin'); m.act('zoomout'); }
      paints += 4;
      if (m.ctx.bad.length) {
        note('paints', (readOnly ? 'diagram' : 'editor') + ' at ' + w + 'x' + h + ': ' +
          m.ctx.bad.length + ' unpaintable coordinate(s), e.g. ' + m.ctx.bad[0]);
      }
      /* the backing store is the box, floored, and CSS is told the same number */
      const wantW = Math.max(320, w), wantH = Math.max(260, h);
      if (m.cv.width !== wantW || m.cv.style.width !== wantW + 'px') {
        note('paints', 'at ' + w + 'x' + h + ' the canvas is ' + m.cv.width + ' backing / ' +
          m.cv.style.width + ' css, wanted ' + wantW);
      }
      if (m.cv.height !== wantH) {
        note('paints', 'at ' + w + 'x' + h + ' the canvas is ' + m.cv.height + ' tall, wanted ' + wantH);
      }
    }
  }
  /* a resize in the middle of a drag must move the part by what the pointer did, and
     must not leave the canvas measuring the size it had when the drag started */
  const m = mount({ model: { parts: [{ id: 'p0', kind: 'R', x: 5, y: 4, value: 1e3 }], wires: [] } }, 900, 400);
  m.tool('select');
  m.cv.dispatchEvent({ type: 'pointerdown', button: 0, clientX: 104, clientY: 78, target: m.cv, pointerId: 1 });
  m.cv.dispatchEvent({ type: 'pointermove', clientX: 130, clientY: 78, target: m.cv, pointerId: 1 });
  resizeTo(m.cv.parentElement, 375, 400);
  m.cv.dispatchEvent({ type: 'pointermove', clientX: 156, clientY: 78, target: m.cv, pointerId: 1 });
  m.cv.dispatchEvent({ type: 'pointerup', button: 0, clientX: 156, clientY: 78, target: m.cv, pointerId: 1 });
  flushFrame();
  if (m.handle.getModel().parts[0].x !== 7) {
    note('paints', 'a drag across a resize moved the part to x = ' +
      m.handle.getModel().parts[0].x + ', wanted 7');
  }
  if (m.cv.width !== 375) {
    note('paints', 'after narrowing to 375 mid-drag the canvas is still ' + m.cv.width + ' wide');
  }
  console.log('[ok  ] paints    ' + (SIZES.length * 2) + ' mounts across 7 widths in both modes, ' +
    'and a drag across a resize');
});

/* ------------------------------------------------- 5. faster than it can repaint
 *
 * Measured before the coalescer: 60 pan moves inside one frame were 61 full repaints and
 * 40 wheel notches were 40, while one repaint at the 0.3 zoom floor on a 1200x800 canvas
 * is 13478 fillRect calls. The solver has been coalesced through perFrame since it was
 * written; the drawing never was.
 *
 * The canvas is focused first, on purpose. pointerdown calls focusCanvas() and gaining
 * focus repaints — a discrete event that SHOULD paint at once — so a measurement that
 * did not focus first would count it and report the pan as one repaint more than it is.
 */
section('rapid', () => {
  const m = mount({ model: { parts: [{ id: 'p0', kind: 'R', x: 5, y: 4, value: 1e3 }], wires: [] } });
  m.cv.focus();
  flushFrame();
  const frames = () => m.ctx.frames.length;

  let f0 = frames();
  m.cv.dispatchEvent({ type: 'pointerdown', button: 1, clientX: 100, clientY: 100, target: m.cv, pointerId: 1 });
  for (let i = 0; i < 60; i++) {
    m.cv.dispatchEvent({ type: 'pointermove', clientX: 100 + i, clientY: 100, target: m.cv, pointerId: 1 });
  }
  const midPan = frames() - f0;
  flushFrame();
  const pan = frames() - f0;
  m.cv.dispatchEvent({ type: 'pointerup', button: 1, clientX: 160, clientY: 100, target: m.cv, pointerId: 1 });
  if (midPan !== 0 || pan !== 1) {
    note('rapid', '60 pan moves inside one frame drew ' + pan + ' repaint(s) (' + midPan +
      ' of them before the frame ran), wanted exactly 1 and none early');
  }

  f0 = frames();
  for (let i = 0; i < 40; i++) {
    m.cv.dispatchEvent({ type: 'wheel', deltaY: -1, clientX: 100, clientY: 100, target: m.cv });
  }
  flushFrame();
  if (frames() - f0 !== 1) {
    note('rapid', '40 wheel notches inside one frame drew ' + (frames() - f0) + ' repaint(s), wanted 1');
  }

  /* a rubber band, and a part dragged across many cells */
  /* A rubber band, measured from AFTER the pointerdown. Pressing the button is a
     discrete event and SHOULD paint at once - it clears the selection, and a selection
     that cleared a frame later would be a canvas disagreeing with its own panel. What is
     being measured here is the 50 moves that follow. */
  m.tool('select');
  m.cv.dispatchEvent({ type: 'pointerdown', button: 0, clientX: 400, clientY: 300, target: m.cv, pointerId: 1 });
  flushFrame();
  f0 = frames();
  for (let i = 0; i < 50; i++) {
    m.cv.dispatchEvent({ type: 'pointermove', clientX: 400 + i * 3, clientY: 300 + i, target: m.cv, pointerId: 1 });
  }
  flushFrame();
  const band = frames() - f0;
  m.cv.dispatchEvent({ type: 'pointerup', button: 0, clientX: 550, clientY: 350, target: m.cv, pointerId: 1 });
  flushFrame();
  if (band > 1) note('rapid', '50 rubber-band moves inside one frame drew ' + band + ' repaint(s)');

  /* and the observer that fires while a window is being dragged */
  /* And the observer that fires all the way through a window drag: a browser calls it
     once per layout pass, not once per frame. */
  f0 = frames();
  for (let i = 0; i < 30; i++) resizeTo(m.cv.parentElement, 900 - i * 10, 400);
  const midResize = frames() - f0;
  flushFrame();
  const resized = frames() - f0;
  if (midResize !== 0 || resized !== 1) {
    note('rapid', '30 resize callbacks inside one frame drew ' + resized + ' repaint(s) (' +
      midResize + ' before the frame ran), wanted exactly 1 and none early');
  }

  /* a queued repaint must not run after dispose — an editor nothing is showing */
  const d = mount({ model: { parts: [], wires: [] } });
  d.cv.focus();
  d.cv.dispatchEvent({ type: 'pointerdown', button: 1, clientX: 10, clientY: 10, target: d.cv, pointerId: 1 });
  d.cv.dispatchEvent({ type: 'pointermove', clientX: 40, clientY: 40, target: d.cv, pointerId: 1 });
  const before = d.ctx.frames.length;
  d.handle.dispose();
  flushFrame();
  if (d.ctx.frames.length !== before) {
    note('rapid', 'a repaint queued before dispose() drew afterwards, into a canvas ' +
      'nothing is showing');
  }
  console.log('[ok  ] rapid     150 gestures inside one frame draw one repaint each, and a ' +
    'repaint queued before dispose does not run');
});

/* ------------------------------------------------- 6. the canvas says what is on it
 *
 * role="application" with a fixed name is what this was: "Schematic canvas. Press Enter
 * for the key map." on an empty canvas and on a finished filter alike. The status line
 * announces each action as it happens, which serves somebody doing the actions and
 * nobody who arrives at the canvas afterwards. Cycle 8 gave the analysis plot a name
 * built out of what it drew; this is that rule on the other canvas.
 */
section('named', () => {
  const m = mount({ model: { parts: [], wires: [] } });
  const name = () => String(m.cv.getAttribute('aria-label') || '');
  const empty = name();
  if (!/no parts/i.test(empty) || !/key map/i.test(empty)) {
    note('named', 'an empty canvas calls itself ' + JSON.stringify(empty) +
      ' — it should say there is nothing on it, and still offer the key map');
  }
  m.cv.focus();
  m.key('Enter');                       /* the caret */
  m.key('Enter');                       /* places a resistor */
  m.key('ArrowRight'); m.key('ArrowRight');
  m.key('Enter');                       /* and another */
  const two = name();
  if (two === empty) {
    note('named', 'the canvas still calls itself ' + JSON.stringify(two) + ' after two ' +
      'parts were placed — the name does not describe the drawing');
  }
  if (!/2 parts/.test(two)) {
    note('named', 'after placing two parts the name is ' + JSON.stringify(two) +
      ', which does not count them');
  }
  const before = name();
  m.act('zoomin');
  if (name() === before) note('named', 'the name does not follow the zoom');
  /* and it must not be rewritten when nothing moved: this runs on every frame of a drag */
  let writes = 0;
  const set = m.cv.setAttribute.bind(m.cv);
  m.cv.setAttribute = (k, v) => { if (k === 'aria-label') writes++; return set(k, v); };
  for (let i = 0; i < 10; i++) { m.act('fit'); }
  if (writes > 1) {
    note('named', 'ten repaints that changed nothing rewrote the name ' + writes +
      ' times — an attribute set to the value it already holds is a mutation a screen ' +
      'reader reacts to');
  }
  /* a diagram keeps the label its author wrote */
  const ro = mount({ model: { parts: [{ id: 'p0', kind: 'R', x: 3, y: 3, value: 1e3 }], wires: [] },
    readOnly: true, label: 'A voltage divider' });
  if (ro.cv.getAttribute('aria-label') !== 'A voltage divider') {
    note('named', 'a read-only diagram lost its authored label: ' +
      JSON.stringify(ro.cv.getAttribute('aria-label')));
  }
  console.log('[ok  ] named     the canvas names its parts, wires, selection and zoom, ' +
    'writes only when they move, and leaves a diagram\'s own label alone');
});

/* ------------------------------------------------- 7. Fit reports what it did
 *
 * The button said nothing at all and the key said "Fitted the drawing to the window."
 * whether it had or not. Below the 0.3 zoom floor the drawing is wider than the window
 * can hold, so the middle is shown and both ends are off — which for a sparse drawing is
 * an empty canvas under a sentence claiming success. The centring itself is correct at
 * both ends and was checked algebraically rather than replaced.
 */
section('fit', () => {
  const two = (spread) => ({ parts: [
    { id: 'p0', kind: 'R', x: 3, y: 3, value: 1e3 },
    { id: 'p1', kind: 'R', x: 3 + spread, y: 3, value: 1e3 }], wires: [] });

  const empty = mount({ model: { parts: [], wires: [] } });
  empty.act('fit');
  if (!/nothing to fit/i.test(empty.say())) {
    note('fit', 'fitting an empty canvas said ' + JSON.stringify(empty.say()));
  }

  const near = mount({ model: two(10) }, 900, 400);
  near.act('fit');
  if (!/fitted/i.test(near.say()) || !/per cent/.test(near.say())) {
    note('fit', 'a drawing that fits said ' + JSON.stringify(near.say()) +
      ' — it should say so and report the zoom it reached');
  }
  if (/as far as the zoom goes/i.test(near.say())) {
    note('fit', 'a drawing that fits reported that it could not: ' + JSON.stringify(near.say()));
  }

  const far = mount({ model: two(400) }, 900, 400);
  far.act('fit');
  if (!/as far as the zoom goes/i.test(far.say())) {
    note('fit', 'a drawing too wide for the zoom floor said ' + JSON.stringify(far.say()) +
      ' — claiming a fit it did not have');
  }

  /* the centring is the property, at both ends of the clamp: the drawing's middle lands
     on the viewport's middle whether the floor bit or not */
  for (const spread of [1, 10, 40, 200, 2000]) {
    const m = mount({ model: two(spread) }, 900, 400);
    let last = null;
    const of = m.ctx.setTransform;
    m.ctx.setTransform = (...a) => { last = a; return of(...a); };
    m.act('fit');
    if (!last) { note('fit', 'no transform was set for spread ' + spread); continue; }
    const GRID = 26, originX = 2;
    const gx = (x) => (x - originX) * GRID + GRID;
    const mid = (gx(3) + gx(3 + spread)) / 2;
    const sx = last[0] * mid + last[4];
    if (Math.abs(sx - 900 / 2) > 2) {
      note('fit', 'at spread ' + spread + ' the drawing\'s centre landed at x = ' +
        sx.toFixed(1) + ' on a 900px canvas — fit is not centring');
    }
  }
  console.log('[ok  ] fit       the empty, the fitting and the too-wide case each say what ' +
    'happened · the centre lands on the centre at 5 spreads');
});

/* ------------------------------------------------- 8. every published schematic draws
 *
 * The regression net, and the one question no gate asked: a diagram that solves
 * correctly can still be drawn off its own canvas. verify_circuit_model.mjs proves each
 * of these reaches an answer; this paints all of them and requires the picture to be on
 * the screen.
 */
section('drawn', () => {
  let tiny = 0, off = 0;
  for (const [at, model] of CATALOGUE) {
    const m = mount({ model, readOnly: true, label: at }, 900, 400);
    drawn++;
    if (m.ctx.bad.length) {
      note('drawn', at + ': ' + m.ctx.bad.length + ' unpaintable coordinate(s), e.g. ' + m.ctx.bad[0]);
      continue;
    }
    /* The transform paint() ACTUALLY set, spied off the context rather than recomputed
       here. A gate that rebuilds the arithmetic it is checking passes whenever its copy
       and the original are wrong in the same way, which is the one case that matters. */
    const t = m.ctx.lastTransform;
    if (!t) { note('drawn', at + ': nothing was drawn at all'); continue; }
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    const see = (px, py) => {
      if (!isFinite(px) || !isFinite(py)) return;
      if (px < x0) x0 = px; if (px > x1) x1 = px;
      if (py < y0) y0 = py; if (py > y1) y1 = py;
    };
    (model.parts || []).forEach((p) => {
      Netlist.pinsOf(p).forEach((pt) => see(pt[0], pt[1]));
      see(p.x, p.y);
    });
    (model.wires || []).forEach((w) => { see(w.a[0], w.a[1]); see(w.b[0], w.b[1]); });
    if (!isFinite(x0)) continue;
    const GRID = 26, originX = 2, originY = 2;
    const gx = (v) => (v - originX) * GRID + GRID, gy = (v) => (v - originY) * GRID + GRID;
    /* device pixels, which is what the canvas is: dpr is 1 in this stub */
    const sx = (v) => t[0] * gx(v) + t[4], sy = (v) => t[3] * gy(v) + t[5];
    if (t[0] < 0.3) { tiny++; note('drawn', at + ' draws at ' + t[0].toFixed(3) + ' scale — unreadable'); }
    const M = 1;                        /* a pixel of slack for rounding */
    if (sx(x0) < -M || sx(x1) > 900 + M || sy(y0) < -M || sy(y1) > 400 + M) {
      off++;
      note('drawn', at + ' is drawn from (' + sx(x0).toFixed(0) + ', ' + sy(y0).toFixed(0) +
        ') to (' + sx(x1).toFixed(0) + ', ' + sy(y1).toFixed(0) +
        ') on a 900x400 canvas — part of it is off the picture');
    }
  }
  console.log('[ok  ] drawn     ' + drawn + ' published schematics painted, each inside its ' +
    'own canvas at a legible scale');
});

/* ---------------------------------------------------------------- report */
for (const [where, lines] of problems) {
  console.log('[FAIL] ' + where);
  lines.forEach((l) => console.log('            ' + l));
}
console.log(problems.length
  ? '\n' + problems.reduce((n, p) => n + p[1].length, 0) + ' drawing problem(s)'
  : '\nAll good: the schematic canvas holds ' + hostile + ' hostile coordinates off the ' +
    'drawing, returns from ' + CELL_LIMIT.toExponential(0) + ' cells out, paints ' + mounts +
    ' mounts at 7 widths in both modes, draws one repaint a frame under 150 gestures, ' +
    'names what it drew, and puts all ' + drawn + ' published schematics inside their own box.');
process.exit(problems.length ? 1 : 0);
