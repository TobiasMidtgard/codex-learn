/**
 * verify_circuit_ui.mjs — the resilience and keyboard gate for the schematic editor.
 *
 * Track 6's ground had no gate at all, which is why the defects it found were years
 * old. Nothing here judges the drawing; it drives the real editor and asks whether the
 * things a learner does with a keyboard actually happen.
 *
 *   * KEYS THAT ESCAPE THE EDITOR. Every shortcut was on `document`, guarded only
 *     against a target that was an input or a textarea. So `Space` was preventDefault()ed
 *     for the whole page — and a <button> is only activated on keyup if its keydown left
 *     it active, which the browser does in the keydown default action, so cancelling the
 *     keydown cancels the press. Ctrl+A was taken from the document with preventDefault.
 *     R, G, U, Delete and Backspace fired from anywhere. All of it whenever a build
 *     exercise was on screen. This gate mounts an editor and presses those keys at an
 *     element outside it: the model must not move and preventDefault must not be called.
 *
 *   * A GRADED UNIT NO KEYBOARD CAN SIT. The canvas took no focus and had no key model,
 *     so the 80 circuit exercises could be done with a mouse and no other way. The gate
 *     builds a circuit through the keyboard alone — arrow, place, wire, select, rotate,
 *     delete — and checks the model each time.
 *
 *   * A VALUE THE SOLVER WILL NOT HONOUR. The value box was the one field on the panel
 *     with no clamp, so a resistance of 0 or of −5 was accepted and saved, while the
 *     stamp quietly read it as 1 pΩ. The gate types nonsense into every kind and checks
 *     the model against what the solver can actually use.
 *
 *   * AN EDITOR THAT OUTLIVED ITS DOM. `teardown` is one slot and renderBuild's paint()
 *     is re-entrant, so "Start over" abandoned a live editor that could still write the
 *     learner's saved circuit. Checked at the call sites, in app.js, as source.
 *
 *     node tools/verify_circuit_ui.mjs
 */

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

/* The tiny DOM this gate mounts the editor into is shared with
   verify_circuit_model.mjs — one stub, so both gates drive the same editor. */
import { El, stubCtx, DOC, WIN, windowShim, windowListenerCount } from './dom_stub.mjs';
/* ================================================================== the editor */
const mod = { exports: {} };
new Function('module', 'window', 'requestAnimationFrame', 'ResizeObserver', 'devicePixelRatio',
  /* the editor listens for the browser's own way out of fullscreen */
  'document',
  readFileSync(join(ROOT, 'src', 'circuit.js'), 'utf8') +
  '\nmodule.exports = { createCircuit, Netlist, MNA, PART_KINDS, VALUE_FLOOR, clampValue, parseEng };'
)(mod, windowShim, (fn) => fn(), undefined, 1, DOC);
const { createCircuit, Netlist, MNA, PART_KINDS, VALUE_FLOOR, clampValue } = mod.exports;

const problems = [];
const note = (where, line) => {
  const row = problems.find((p) => p[0] === where);
  if (row) row[1].push(line); else problems.push([where, [line]]);
};

/* ---- the harness a test drives ---- */
function mount(opts) {
  const root = new El('div');
  let saves = 0, last = null;
  const handle = createCircuit(root, Object.assign({
    onChange: (m) => { saves++; last = m; },
  }, opts || {}));
  const cv = root.querySelector('.ckt-canvas canvas');
  const say = () => (root.querySelector('[data-say]') || { textContent: '' }).textContent.trim();
  const key = (el, k, extra) => {
    const ev = Object.assign({ type: 'keydown', key: k, code: k === ' ' ? 'Space' : k,
      shiftKey: false, ctrlKey: false, metaKey: false, altKey: false, target: el }, extra || {});
    el.dispatchEvent(ev);
    return ev;
  };
  const click = (el) => el.dispatchEvent({ type: 'click', target: el });
  return { root, handle, cv, say, key, click,
    model: () => handle.getModel(),
    saveCount: () => saves, lastSaved: () => last,
    tool: (t) => click(root.querySelector('[data-tool="' + t + '"]')) };
}

let drives = 0, said = [];
function collect(h, fn) { fn(); drives++; const s = h.say(); if (s) said.push(s); return s; }

/* A section that throws has still found something — but it prints a stack trace and
   loses every finding recorded before it, which is how the first run of this gate
   reported a TypeError instead of the four defects it had already collected. Each
   section runs inside this, and falling over is itself a failure. */
function section(name, fn) {
  try { fn(); }
  catch (e) { note(name, 'the gate fell over here: ' + (e && e.message) + ' — which is a defect in the editor, in the gate, or in both'); }
}

/* ---------------------------------------------------------------- 1. keys stay put */
section('keys', () => {
  const h = mount();
  h.cv.focus();
  h.tool('R');
  h.key(h.cv, 'ArrowRight');
  h.key(h.cv, 'Enter');       /* something on the drawing for a stray key to damage */
  drives += 3;

  /* Two shapes of "not the canvas". The detached button is every control in the app
     shell, the footer navigation and the desk modal — nothing in the editor's subtree.
     The tool button is the harder case: it IS inside the editor, and a handler put on
     the root, on the document or on the window would still hear it. Only a handler on
     the canvas does not. */
  const elsewhere = [['a control elsewhere on the page', new El('button')],
                     ['the editor\'s own toolbar', h.root.querySelector('[data-tool="C"]')]];
  const before = JSON.stringify(h.model());
  const leaked = [];
  for (const [where, el] of elsewhere) {
    for (const [k, extra] of [[' ', {}], ['Delete', {}], ['Backspace', {}], ['r', {}], ['g', {}],
      ['u', {}], ['0', {}], ['Escape', {}], ['a', { ctrlKey: true }], ['ArrowLeft', {}]]) {
      const ev = h.key(el, k, extra);
      drives++;
      if (ev.defaultPrevented) leaked.push('"' + k + '" pressed on ' + where + ' was preventDefault()ed');
    }
  }
  if (JSON.stringify(h.model()) !== before) leaked.push('a key pressed outside the canvas changed the model');
  if (WIN.listenerCount('keydown') || WIN.listenerCount('keyup')) {
    leaked.push('the editor still listens for keys on the window');
  }
  leaked.forEach((l) => note('keys', l));
  h.handle.dispose();
});

/* ---------------------------------------------------------------- 2. the canvas is reachable */
section('reach', () => {
  const h = mount();
  const cv = h.cv;
  if (cv.getAttribute('tabindex') !== '0') note('reach', 'the canvas is not a focus stop (no tabindex="0")');
  if (!cv.getAttribute('role')) note('reach', 'the canvas has no role');
  if (!(cv.getAttribute('aria-label') || '').trim()) note('reach', 'the canvas has no accessible name');
  const desc = cv.getAttribute('aria-describedby');
  const target = desc && h.root.querySelector('[id="' + desc + '"]');
  if (!target) note('reach', 'aria-describedby="' + desc + '" points at nothing in this editor');
  else if (target.textContent.trim().length < 80) note('reach', 'the key map the canvas points at is empty or a stub');
  else {
    /* the map has to name the keys the editor actually answers to */
    for (const word of ['Arrow', 'Shift', 'Enter', 'Escape', 'Tab']) {
      if (!target.textContent.includes(word)) note('reach', 'the key map never mentions ' + word);
    }
  }
  h.handle.dispose();
});

/* ---------------------------------------------------------------- 3. build one by keyboard */
section('keyboard', () => {
  const h = mount({ model: { parts: [], wires: [] } });
  h.cv.focus();
  h.tool('R');
  collect(h, () => h.key(h.cv, 'ArrowRight'));           /* first arrow only lands the caret */
  const home = h.model().parts.length;
  if (home !== 0) note('keyboard', 'the first arrow key placed something');

  collect(h, () => h.key(h.cv, 'ArrowRight'));
  const ev = h.key(h.cv, 'Enter');
  drives++;
  if (!ev.defaultPrevented) note('keyboard', 'Enter on the canvas was not claimed by the editor');
  let m = h.model();
  if (m.parts.length !== 1) note('keyboard', 'Enter placed ' + m.parts.length + ' parts, expected 1');
  else if (m.parts[0].kind !== 'R') note('keyboard', 'Enter placed a ' + m.parts[0].kind + ' with the resistor tool chosen');
  const placedAt = m.parts.length ? [m.parts[0].x, m.parts[0].y] : null;

  /* a second Enter on the same cell must refuse rather than stack */
  h.key(h.cv, 'Enter'); drives++;
  if (h.model().parts.length !== 1) note('keyboard', 'Enter twice on one cell stacked two parts');

  /* rotate, and see the model move. Shift+R, because the bare letters place parts —
     and the bare R is checked below to be sure it does NOT rotate, since a key that
     does two things depending on what is selected is the failure mode this split was
     meant to avoid. */
  const rot0 = h.model().parts[0].rot || 0;
  collect(h, () => h.key(h.cv, 'R', { shiftKey: true }));
  if (((h.model().parts[0].rot || 0) - rot0 + 4) % 4 !== 1) {
    note('keyboard', 'Shift+R did not turn the part a quarter');
  }
  const rot1 = h.model().parts[0].rot || 0;
  collect(h, () => h.key(h.cv, 'r'));
  if ((h.model().parts[0].rot || 0) !== rot1) {
    note('keyboard', 'a bare R turned the part as well as picking the resistor up');
  }

  /* a wire, drawn between two presses */
  h.tool('wire');
  collect(h, () => h.key(h.cv, 'Enter'));
  collect(h, () => h.key(h.cv, 'ArrowDown'));
  collect(h, () => h.key(h.cv, 'ArrowDown'));
  collect(h, () => h.key(h.cv, 'Enter'));
  if (h.model().wires.length !== 1) note('keyboard', 'two Enters with the wire tool drew ' + h.model().wires.length + ' wires');

  /* select the part again and delete it */
  h.tool('select');
  h.cv.focus();
  /* walk back up to where the resistor is */
  while (true) {
    const before2 = h.model().parts.length;
    collect(h, () => h.key(h.cv, 'ArrowUp'));
    if (h.model().parts.length !== before2) { note('keyboard', 'an arrow key changed the model'); break; }
    break;
  }
  h.key(h.cv, 'ArrowUp'); drives++;
  const sel = collect(h, () => h.key(h.cv, 'Enter'));
  if (!/Selected|already|Selection/.test(sel)) note('keyboard', 'Enter with the select tool said "' + sel + '"');
  /* The caret has to be on the canvas, not only in a variable. Same model, same
     viewport, one paint with the canvas focused and one without: the focused frame has
     to carry more drawing than the blurred one, and that difference is the caret. */
  /* A frame is closed by the NEXT clearRect, so each reading is taken one paint late:
     the blur closes the focused frame, and the focus after it closes the blurred one. */
  const frames = h.cv._ctx.frames;
  const last = () => frames[frames.length - 1];
  h.cv.focus();
  h.key(h.cv, 'ArrowRight'); drives++;
  h.cv.blur();
  const lit = last();
  h.cv.focus();
  const dark = last();
  if (!(lit > dark)) {
    note('keyboard', 'the caret is tracked but never drawn: a focused frame is ' + lit +
      ' draw calls against ' + dark + ' for the same drawing unfocused');
  }

  /* And the other way: a learner who goes back to the mouse must get the canvas they
     had before this cycle. Clicking focuses the canvas — it has to, or the tab order
     runs past the editor — so the ring is gated on a key having been pressed, and the
     click has to put that gate back down. Testing it on a fresh editor proves nothing,
     because nothing has raised the gate yet: the sequence that matters is arrow, then
     click. */
  {
    const m = mount({ model: { parts: [], wires: [] } });
    m.tool('select');
    m.cv.focus();
    m.key(m.cv, 'ArrowRight'); m.key(m.cv, 'ArrowDown'); drives += 2;
    m.cv.dispatchEvent({ type: 'pointerdown', button: 0, clientX: 200, clientY: 150, pointerId: 1, target: m.cv });
    drives++;
    const f = m.cv._ctx.frames;
    m.cv.blur(); m.cv.focus(); m.cv.blur();
    const mouseLit = f[f.length - 1], mouseDark = f[f.length - 2];
    if (mouseLit !== mouseDark) {
      note('keyboard', 'the caret survives a click back onto the canvas: ' + mouseLit +
        ' draw calls focused against ' + mouseDark + ' unfocused, for the same model');
    }
    m.handle.dispose();
  }
  h.cv.focus();

  if (placedAt) {
    /* park the caret exactly on the part, however the walk above went, and delete it */
    h.key(h.cv, 'Escape'); drives++;
    const target = h.model().parts[0];
    /* Shift+arrow is the drag gesture: with nothing selected it must refuse rather than move */
    const refused = collect(h, () => h.key(h.cv, 'ArrowLeft', { shiftKey: true }));
    if (!/Nothing is selected/.test(refused)) note('keyboard', 'Shift+arrow with an empty selection said "' + refused + '"');
    if (target.x !== h.model().parts[0].x) note('keyboard', 'Shift+arrow moved a part that was not selected');
  }
  h.handle.dispose();
});

/* ---------------------------------------------------------------- 4. Space, both meanings */
section('space', () => {
  const h = mount({ model: { parts: [], wires: [] } });
  h.cv.focus();
  h.tool('R');
  h.key(h.cv, 'ArrowRight'); drives++;
  const n0 = h.model().parts.length;
  const ev = h.key(h.cv, ' ');
  drives++;
  if (!ev.defaultPrevented) note('space', 'Space on the focused canvas was left to the page');
  if (h.model().parts.length !== n0 + 1) note('space', 'Space on the canvas did not place a part');

  /* With the pointer over the drawing, Space is the pan modifier and places nothing.
     The caret has to move first: pressing it twice on one cell is refused by the
     no-stacking rule, so the part count would not move either way and the test would
     pass whatever the editor did — which is exactly how the first draft of this check
     was blind to the branch being deleted. */
  h.key(h.cv, 'ArrowRight'); h.key(h.cv, 'ArrowDown'); drives += 2;
  h.cv.dispatchEvent({ type: 'pointermove', clientX: 100, clientY: 100, target: h.cv });
  const n1 = h.model().parts.length;
  const before = h.say();
  h.key(h.cv, ' '); drives++;
  if (h.model().parts.length !== n1) note('space', 'Space with the pointer over the canvas placed a part instead of arming the pan');
  if (h.say() !== before) note('space', 'Space with the pointer over the canvas acted, and said "' + h.say() + '"');
  h.handle.dispose();
});

/* ---------------------------------------------------------------- 5. what it says */
section('announce', () => {
  for (const s of said) {
    if (/NaN|undefined|Infinity/.test(s)) note('announce', 'the status line reads "' + s + '"');
  }
  if (said.length < 8) note('announce', 'only ' + said.length + ' of ' + drives + ' actions said anything');
});

/* ---------------------------------------------------------------- 6. a value the solver can use */
section('values', () => {
  const kinds = Object.keys(VALUE_FLOOR);
  for (const kind of kinds) {
    const h = mount({ model: { parts: [], wires: [] } });
    h.tool(kind);
    h.cv.focus();
    h.key(h.cv, 'ArrowRight'); drives++;
    h.key(h.cv, 'Enter'); drives++;
    const inp = h.root.querySelector('[data-val]');
    if (!inp) { note('values', kind + ' has no value box on its panel'); h.handle.dispose(); continue; }
    for (const typed of ['0', '-5', '-1e12', 'nonsense', '']) {
      inp.value = typed;
      inp.dispatchEvent({ type: 'change', target: inp });
      const p = h.model().parts[0];
      if (!isFinite(p.value)) { note('values', kind + ' took "' + typed + '" and its value is not a number'); break; }
      if (p.value < VALUE_FLOOR[kind]) {
        note('values', kind + ' took "' + typed + '" and kept ' + p.value +
          ', under the ' + VALUE_FLOOR[kind] + ' its own stamp needs');
        break;
      }
    }
    h.handle.dispose();
  }
  /* A VALUE TYPED AND NEVER BLURRED. Every field on the component panel committed on
     `change`, and `change` fires on blur — but dispose() empties root.innerHTML, and
     removing a focused element from the document fires no pending change. So a learner
     who typed "4.7k" and then left by the footer, the icon rail or the back button was
     saved the value they started with, silently. Measured through the shipped editor:
     the model still read 1000. Found by sweeping for the shape the sketch box had. */
  {
    const h = mount({ model: { parts: [], wires: [] } });
    h.tool('R');
    h.cv.focus();
    h.key(h.cv, 'ArrowRight'); h.key(h.cv, 'Enter'); drives += 2;
    const inp = h.root.querySelector('[data-val]');
    inp.value = '4.7k';
    inp.dispatchEvent({ type: 'input', target: inp });
    drives++;
    /* Staged, not committed: committing per keystroke would clamp "4" on the way to
       "4.7k" and rewrite the box under the typist. */
    if (h.model().parts[0].value !== 1000) {
      note('values', 'the value box committed on a keystroke — "4" on the way to "4.7k" ' +
        'would be clamped and written back into the box mid-type');
    }
    h.handle.dispose();
    const saved = h.lastSaved();
    if (!saved || saved.parts[0].value !== 4700) {
      note('values', 'a resistance typed and never blurred was lost on the way out: ' +
        'progress kept ' + (saved ? saved.parts[0].value : 'nothing'));
    }
  }
  /* and the clamp itself, directly, including the kinds that are allowed to be negative */
  if (clampValue('V', -5, 1) !== -5) note('values', 'a voltage source was refused a negative value');
  if (clampValue('I', 0, 1) !== 0) note('values', 'a current source was refused zero');
  if (clampValue('R', NaN, 1000) !== 1000) note('values', 'a NaN did not fall back to the old value');
});

/* ---------------------------------------------------------------- 7. disposal */
section('dispose', () => {
  const before = windowListenerCount();
  const h = mount({ model: { parts: [], wires: [] } });
  h.cv.focus();
  h.tool('R');
  h.key(h.cv, 'ArrowRight'); h.key(h.cv, 'Enter'); drives += 2;
  const saved = h.saveCount();
  if (!saved) note('dispose', 'placing a part never reached onChange, so nothing was ever saved');
  const cv = h.cv;
  h.handle.dispose();
  if (windowListenerCount() !== before) {
    note('dispose', 'dispose() left ' + (windowListenerCount() - before) + ' window listener(s) behind');
  }
  /* the abandoned editor must not be able to write the learner's circuit */
  cv.dispatchEvent({ type: 'keydown', key: 'Delete', code: 'Delete', target: cv });
  cv.dispatchEvent({ type: 'keydown', key: 'R', code: 'R', shiftKey: true, target: cv });
  if (h.saveCount() !== saved) note('dispose', 'a disposed editor still called onChange');
  h.handle.dispose();          /* idempotent */
  if (windowListenerCount() !== before) note('dispose', 'a second dispose() unbalanced the window listeners');
});

/* ---------------------------------------------------------------- 8. the read-only diagram */
section('diagram', () => {
  const root = new El('div');
  const h = createCircuit(root, { model: { parts: [{ id: 'p0', kind: 'R', x: 3, y: 3, rot: 0, value: 1000 }], wires: [] }, readOnly: true });
  const cv = root.querySelector('.ckt-canvas canvas');
  if (cv.getAttribute('role') !== 'img') note('diagram', 'a question\'s schematic is not labelled as an image');
  if (!(cv.getAttribute('aria-label') || '').trim()) note('diagram', 'a question\'s schematic has no accessible name');
  if (cv.hasAttribute('tabindex')) note('diagram', 'a picture nobody can edit is in the tab order');
  if (cv._ctx && cv._ctx.bad.length) note('diagram', 'the diagram drew ' + cv._ctx.bad.length + ' non-finite coordinate(s)');
  h.dispose();
});

/* ---------------------------------------------------------------- 9. state that can be read */
section('state', () => {
  const h = mount();
  const tools = () => h.root.querySelectorAll('[data-tool]');
  const pressed = () => tools().filter((b) => b.getAttribute('aria-pressed') === 'true');
  if (pressed().length !== 1) note('state', pressed().length + ' tools report aria-pressed=true on open, expected 1');
  /* Every one of them, not just the lit one: a button with no aria-pressed at all is
     not announced as a toggle, so the other twenty-four would say nothing about being
     off. Checking only "exactly one is true" passes a bar with one button in it. */
  const mute = tools().filter((b) => b.getAttribute('aria-pressed') === null);
  if (mute.length) note('state', mute.length + ' tool button(s) carry no aria-pressed at all, so they never say they are off');
  h.tool('C');
  const on = pressed();
  if (on.length !== 1 || on[0].dataset.tool !== 'C') {
    note('state', 'choosing a tool did not move aria-pressed to it');
  }
  for (const b of h.root.querySelectorAll('[data-tool]')) {
    if (!(b.getAttribute('aria-label') || '').trim()) note('state', 'a tool button has no name but its glyph');
    if (b.getAttribute('aria-label') === b.textContent.trim() && b.textContent.trim().length <= 2) {
      note('state', 'the tool "' + b.textContent.trim() + '" is named after its glyph');
    }
  }
  const modes = h.root.querySelectorAll('[data-an]');
  if (modes.filter((b) => b.getAttribute('aria-pressed') === 'true').length !== 1) {
    note('state', 'the analysis mode does not report which one is chosen');
  }
  h.handle.dispose();
});

/* ---------------------------------------------------------------- 10. the call sites */
section('lifetime', () => {
  const app = readFileSync(join(ROOT, 'src', 'app.js'), 'utf8');
  const lines = app.split(/\r?\n/);
  lines.forEach((ln, i) => {
    if (!/createCircuit\s*\(/.test(ln)) return;
    /* Every mount must be preceded, within a few lines, by the flush of the single
       teardown slot — or by go(), which does the flush itself. renderBuild's paint()
       and renderNumeric's paint() are both re-entrant and both used to skip it. */
    const before = lines.slice(Math.max(0, i - 12), i).join('\n');
    if (!/if\s*\(teardown\)\s*\{\s*try\s*\{\s*teardown\(\)/.test(before) &&
        !/^function renderCircuitPlayground/m.test(lines.slice(Math.max(0, i - 40), i).join('\n'))) {
      note('lifetime', 'src/app.js:' + (i + 1) + ' mounts an editor without flushing the teardown slot first');
    }
  });
});

/* ---------------------------------------------------------------- report */
for (const [where, lines] of problems) {
  console.log('[FAIL] ' + where);
  lines.forEach((l) => console.log('            ' + l));
}
console.log(problems.length
  ? '\n' + problems.reduce((n, p) => n + p[1].length, 0) + ' circuit-editor problem(s)'
  : '\nAll good: the editor answers ' + drives + ' driven keys and gestures, says ' + said.length +
    ' things while doing it, keeps every shortcut inside its own canvas, holds ' +
    Object.keys(VALUE_FLOOR).length + ' kinds above the floor their stamps need, and ' +
    'disposes without leaving a listener behind.');
process.exit(problems.length ? 1 : 0);
