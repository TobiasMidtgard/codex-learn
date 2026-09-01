/**
 * verify_tune_ui.mjs — the gate for the "hit the target" view a learner actually touches.
 *
 * Three gates already look at tune units and none of them mounts one. verify_tune.mjs
 * asks whether a target can be reached, sweeping the model with the values an author
 * chose. verify_sandbox.mjs asks whether the model's plot survives its extremes, using
 * the model's OWN constants and never the catalogue's overrides. verify_circuit_ui.mjs
 * proved the trick works but points it at the schematic editor. So nobody had ever fed
 * this renderer a value the slider cannot hold, resized it, or clicked faster than it
 * could redraw — which is this track's brief, almost word for word.
 *
 * Ten sections, driving the shipped renderTune rather than a copy of it:
 *
 *   1  every number the view trusts is clamped and on the step grid, whatever it was
 *   2  a readout row is graded by EVERY constraint on its key, not the first
 *   3  every target the model places lies inside that model's own axes — over the
 *      extremes grid AND the catalogue's real constants, which nothing else does
 *   4  nothing unpaintable reaches the canvas, at five widths
 *   5  faster than it can redraw: N drags in one frame are one repaint
 *   6  what a screen reader meets: a named canvas, a named slider, one live region
 *   7  focus survives the two buttons that throw the page away
 *   8  a refusal says what the learner has, not only what was asked for
 *   9  the app's constraint rule and verify_tune.mjs's are the same rule
 *  10  the whole catalogue mounts, paints and reports finite numbers
 *
 *     node tools/verify_tune_ui.mjs
 */

import { stage, tuneUnits } from './tune_stage.mjs';

const S = stage();
const UNITS = tuneUnits();
const problems = [];
const fail = (where, line) => problems.push([where, line]);

const ROT = /NaN|undefined|Infinity/;
const rowsOf = (root) => root.querySelectorAll('.tn-r').map((r) => String(r.textContent));
const chipsOf = (root) => root.querySelectorAll('.tn-c').map((c) => String(c.textContent));

/* the grid a slider can actually land on — the same arithmetic verify_sandbox.mjs and
   verify_tune.mjs use, so "reachable" means one thing across all three */
function onGrid(p, x) {
  if (typeof x !== 'number' || !isFinite(x)) return false;
  if (x < p.min || x > p.max) return false;
  const st = p.step || (p.max - p.min) / 100;
  const n = (x - p.min) / st;
  return Math.abs(n - Math.round(n)) < 1e-6;
}

let mounts = 0, repaints = 0, clampCases = 0, markChecks = 0, drags = 0;

/* ============================================================ 1. the value clamp
 *
 * `initial` and `def` are author-written and build.mjs checks only that a key names a
 * real parameter. The saved position is worse: it outlives any change to a slider's
 * range and is plain text in localStorage. A range input clamps and steps its own value
 * silently, so an unsanitised one leaves the thumb, the printed number, the plot and
 * the grade describing different circuits — and it is not theoretical. Before the fix a
 * saved r1 of -100 put Infinity in all three graded readouts under a thumb resting at
 * 100; a saved "2200" concatenated instead of adding and read 0.000 V for a divider
 * sitting at 2.5 V; a saved NaN read "NaN" in every one. */
const HOSTILE = [
  ['below the floor', (p) => p.min - 10 * (p.step || 1)],
  ['negative', () => -100],
  ['above the ceiling', (p) => p.max + 10 * (p.step || 1)],
  ['enormous', () => 1e308],
  ['off the step grid', (p) => p.min + (p.step || 1) * 1.5],
  ['a string', (p) => String(p.def)],
  ['not a number', () => NaN],
  ['null', () => null],
  ['an object', () => ({})],
];

for (const u of UNITS) {
  const spec = S.Tune.get(u.unit.model);
  if (!spec) continue;
  for (const p of spec.params) {
    for (const [label, make] of HOSTILE) {
      clampCases++;
      const v = {};
      spec.params.forEach((q) => { v[q.k] = q.def; });
      v[p.k] = make(p);
      S.forget(u.id);
      S.save(u.id, v);
      let root;
      try { root = S.mount(u.id, u.unit); mounts++; }
      catch (e) { fail(u.where, `${p.k} ${label}: renderTune threw — ${e.message}`); continue; }
      const sl = root.querySelector('input[data-k="' + p.k + '"]');
      const held = Number(sl.getAttribute('value'));
      if (!onGrid(p, held)) {
        fail(u.where, `${p.k} saved ${label} (${JSON.stringify(v[p.k])}) reaches the slider as ` +
          `${JSON.stringify(sl.getAttribute('value'))}, which is off its ${p.min}..${p.max} ` +
          `step-${p.step} grid — the thumb will sit somewhere else`);
      }
      const printed = String(root.querySelector('[data-out="' + p.k + '"]').textContent);
      if (!printed.startsWith(String(held))) {
        fail(u.where, `${p.k} saved ${label}: the slider holds ${held} and the number beside ` +
          `the label reads "${printed}" — the panel is describing a different circuit`);
      }
      const rot = rowsOf(root).find((r) => ROT.test(r));
      if (rot) fail(u.where, `${p.k} saved ${label}: a graded readout reads "${rot}"`);
      S.forget(u.id);
    }
  }
}

/* ============================================================ 2. every constraint on a key
 *
 * refresh() found the FIRST test whose key matched and coloured the row with it. Two
 * units state two bounds on one readout — EE121 M5 wants the divider current under 0.50
 * mA and over 0.25 mA, EE211 M5 under 0.50 and over 0.20 — so a learner satisfying only
 * the first saw the row drawn green with the constraint chip below it still unticked. */
{
  const dupes = UNITS.filter((u) => {
    const ks = (u.unit.constraints || []).map((c) => c.k);
    return ks.some((k, i) => ks.indexOf(k) !== i);
  });
  if (!dupes.length) {
    fail('two constraints on one readout', 'no unit in the catalogue states two ' +
      'constraints on one readout any more, so this section cannot ask its question — ' +
      'give it a synthetic unit rather than deleting it');
  }
  for (const u of dupes) {
    const spec = S.Tune.get(u.unit.model);
    const keys = [...new Set((u.unit.constraints || []).map((c) => c.k))]
      .filter((k) => (u.unit.constraints || []).filter((c) => c.k === k).length > 1);
    for (const key of keys) {
      const on = (u.unit.constraints || []).filter((c) => c.k === key);
      /* a position satisfying some but not all of them, found on the real grid */
      let found = null;
      const consts = Object.assign({}, spec.constants, u.unit.constants || {});
      const axes = spec.params.map((p) => {
        const vals = [];
        const st = p.step || (p.max - p.min) / 100;
        for (let x = p.min; x <= p.max + 1e-9; x += st * Math.max(1, Math.floor((p.max - p.min) / st / 60))) {
          vals.push(+x.toFixed(6));
        }
        return { k: p.k, vals };
      });
      const walk = (i, v) => {
        if (found) return;
        if (i === axes.length) {
          const out = spec.compute(v, consts);
          const r = out[key];
          if (!r) return;
          const hits = on.map((c) => S.Tune.holds(c, r.value));
          /* The FIRST must hold and a later one must fail. "some but not all" is not
             enough: the first position that satisfies it has the first constraint
             failing, and a renderer grading by the first would mark the row failing too
             and pass this section. The mutation run caught exactly that. */
          if (hits[0] && hits.some((x) => !x)) found = { ...v };
          return;
        }
        for (const x of axes[i].vals) { v[axes[i].k] = x; walk(i + 1, v); if (found) return; }
      };
      walk(0, {});
      if (!found) {
        fail(u.where, `no reachable position satisfies some but not all of the ${on.length} ` +
          `constraints on "${key}", so this section cannot test that unit`);
        continue;
      }
      S.forget(u.id);
      S.save(u.id, found);
      const root = S.mount(u.id, u.unit); mounts++;
      const label = spec.compute(found, consts)[key].label;
      const row = root.querySelectorAll('.tn-r').find((r) =>
        String(r.textContent).startsWith(label));
      if (!row) { fail(u.where, `no readout row for "${label}"`); S.forget(u.id); continue; }
      if (!row.classList.contains('no')) {
        fail(u.where, `at ${JSON.stringify(found)} the "${label}" row is marked ` +
          `"${row.getAttribute('class')}" while ${on.filter((c) => !S.Tune.holds(c, spec.compute(found, consts)[key].value)).length} ` +
          `of the ${on.length} constraints on it fail — the row is being graded by one of them`);
      }
      S.forget(u.id);
    }
  }
}

/* ============================================================ 3. a target inside its own axes
 *
 * app.js used to draw a band wherever a constraint's key matched `plotKey || 'vout'`,
 * and `vout` is a readout of the divider model alone: sixteen of the twenty-one units
 * drew no target at all, and EE111 M6's 1 kHz resonance target was drawn as a
 * horizontal line at y = 1000 on an axis running 0 to 2.375. The model now says where a
 * constraint belongs, so what has to be checked is that it is telling the truth — over
 * the extremes grid AND over the constants the catalogue overrides, which is the case
 * verify_sandbox.mjs never sees because it only ever passes spec.constants. */
function corners(p) {
  const out = new Set([p.min, p.max, p.def, (p.min + p.max) / 2]);
  const st = p.step || (p.max - p.min) / 100;
  out.add(Math.min(p.max, p.min + st));
  out.add(Math.max(p.min, p.max - st));
  return [...out].filter(isFinite);
}
for (const u of UNITS) {
  const spec = S.Tune.get(u.unit.model);
  if (!spec || !spec.marks || !spec.plot) continue;
  const consts = Object.assign({}, spec.constants, u.unit.constants || {});
  const cases = [];
  const def = {};
  spec.params.forEach((p) => { def[p.k] = p.def; });
  cases.push({ ...def });
  spec.params.forEach((p) => corners(p).forEach((x) => cases.push({ ...def, [p.k]: x })));
  cases.push(Object.fromEntries(spec.params.map((p) => [p.k, p.min])));
  cases.push(Object.fromEntries(spec.params.map((p) => [p.k, p.max])));
  /* A mark whose coordinates are in the wrong units is not a crash: paintMark filters
     every edge outside the axis, so it simply draws nothing, for ever, in silence —
     which is the failure this whole section exists to stop and the one shape of it a
     per-case check cannot see. So: a constraint the model claims it can place must be
     visible at SOME reachable position. `reject` quoted in dB against a linear |H| axis
     would satisfy every per-case test above and never once be drawn. */
  const everVisible = new Map();
  for (const v of cases) {
    let pl;
    try { pl = spec.plot(v, consts); } catch (e) { fail(u.where, `plot() threw at ${JSON.stringify(v)} — ${e.message}`); continue; }
    for (const c of u.unit.constraints || []) {
      let m;
      try { m = spec.marks(c, v, consts); }
      catch (e) { fail(u.where, `marks("${c.k}") threw at ${JSON.stringify(v)} — ${e.message}`); continue; }
      if (!m) continue;
      markChecks++;
      if (!['x', 'y', 'point'].includes(m.axis)) {
        fail(u.where, `marks("${c.k}") returned axis "${m.axis}", which nothing can draw`);
        continue;
      }
      for (const edge of ['lo', 'hi']) {
        if (m[edge] === undefined) fail(u.where, `marks("${c.k}") has no ${edge}`);
        else if (Number.isNaN(m[edge])) fail(u.where, `marks("${c.k}").${edge} is NaN`);
      }
      if (m.axis === 'point' && !isFinite(m.x)) {
        fail(u.where, `marks("${c.k}") is a point target at a non-finite frequency ${m.x}`);
      }
      if (!isFinite(m.lo) && !isFinite(m.hi)) {
        fail(u.where, `marks("${c.k}") is open at both ends, so it states nothing`);
      }
      /* a point target's x has to be somewhere on the frequency axis, or the tick is
         drawn off the frame — the defect this section exists for, in its other form */
      if (m.axis === 'point') {
        const [x0, x1] = pl.xRange || [0, 1];
        if (m.x < x0 || m.x > x1) {
          fail(u.where, `marks("${c.k}") puts its target at x = ${m.x} on an axis running ` +
            `${x0} to ${x1} — it would be drawn off the frame`);
        }
      }
      /* is any edge of it actually on the frame here? */
      const range = m.axis === 'x' ? (pl.xRange || [0, 1]) : (pl.yRange || [0, 1]);
      const near = Math.min(range[0], range[1]), far = Math.max(range[0], range[1]);
      const seen = [m.lo, m.hi].some((e) => isFinite(e) && e >= near && e <= far);
      if (!everVisible.has(c.k)) everVisible.set(c.k, false);
      if (seen) everVisible.set(c.k, true);
    }
  }
  for (const [k, seen] of everVisible) {
    if (!seen) {
      const c = (u.unit.constraints || []).find((x) => x.k === k);
      const m = spec.marks(c, def, consts);
      fail(u.where, `the model places "${k}" on the ${m.axis} axis at [${m.lo}, ${m.hi}] and ` +
        'not one reachable position puts either end on the frame, so it is never drawn — ' +
        'the coordinates are in units the axis does not use');
    }
  }
}

/* ============================================================ 4. nothing unpaintable
 * and ============================================== 10. the whole catalogue paints
 *
 * The recording canvas from dom_stub objects to any coordinate nobody can draw. Five
 * widths including the 375px phone and the 240px floor renderTune clamps to. */
const WIDTHS = [1200, 900, 640, 375, 320];
let paints = 0;
for (const u of UNITS) {
  S.forget(u.id);
  let root;
  try { root = S.mount(u.id, u.unit); mounts++; }
  catch (e) { fail(u.where, `renderTune threw on a clean mount — ${e.message}`); continue; }
  const cv = root.querySelector('#tn-cv');
  if (!cv) { fail(u.where, 'no plot canvas was drawn'); continue; }
  for (const w of WIDTHS) {
    S.resizeTo(cv, w, 296);
    S.frame();
    paints++;
    const ctx = cv.getContext('2d');
    if (ctx.bad.length) {
      fail(u.where, `at ${w}px the plot made ${ctx.bad.length} non-finite draw call(s), ` +
        `first ${ctx.bad[0]}`);
      ctx.bad.length = 0;
    }
    if (cv.width > 2 * w || cv.width < w) {
      fail(u.where, `at ${w}px CSS the backing store is ${cv.width}px — the device pixel ` +
        'ratio is not being capped, or the canvas is not being measured from its own box');
    }
  }
  /* the readouts at the opening position and at both ends of every slider */
  const spec = S.Tune.get(u.unit.model);
  for (const p of spec.params) {
    for (const x of [p.min, p.max, p.def]) {
      S.drag(root, p.k, x); drags++;
      S.frame();
      const rot = rowsOf(root).find((r) => ROT.test(r));
      if (rot) fail(u.where, `with ${p.k} at ${x} a graded readout reads "${rot}"`);
      const chip = chipsOf(root).find((c) => ROT.test(c));
      if (chip) fail(u.where, `with ${p.k} at ${x} a constraint chip reads "${chip}"`);
    }
  }
  S.forget(u.id);
}

/* ============================================================ 5. faster than it can redraw
 *
 * The frame queue in tune_stage.mjs is deferred for this section's sake; an immediate
 * one wedges the coalescer's own flag and reports perfect batching for a renderer that
 * has none. */
{
  const u = UNITS[0];
  const spec = S.Tune.get(u.unit.model);
  const p = spec.params[0];
  const real = spec.compute;
  let computes = 0;
  spec.compute = function (...a) { computes++; return real.apply(this, a); };
  S.forget(u.id);
  const root = S.mount(u.id, u.unit); mounts++;
  const cv = root.querySelector('#tn-cv');
  /* Settle the size FIRST. The opening paint runs inside renderTune, before this stage
     has told the canvas how big the stylesheet makes it, so it lands on the 600px
     fallback; taking the baseline there makes the next legitimate repaint look like a
     spurious reallocation. The gate's own first run reported exactly that. */
  S.resizeTo(cv, 900, 296);
  S.frame();
  const store = cv.width;
  if (!store) fail('rapid input', 'the canvas never sized its backing store');
  /* count ASSIGNMENTS, not the value. A browser clears and reallocates on every write to
     canvas.width even when the number is unchanged, so comparing the value before and
     after cannot see the defect — the mutation run passed this check with the guard
     removed entirely. */
  let widthWrites = 0;
  let held = store;
  Object.defineProperty(cv, 'width', {
    get() { return held; },
    set(x) { widthWrites++; held = x; },
    configurable: true,
  });
  computes = 0;
  const N = 60;
  const st = p.step || 1;
  for (let i = 0; i < N; i++) S.drag(root, p.k, Math.min(p.max, p.min + (i % 40) * st));
  drags += N;
  if (computes !== 0) {
    fail('rapid input', `${N} slider events ran the model ${computes} time(s) before a ` +
      'frame was drawn — the repaint is not being coalesced onto one');
  }
  const ran = S.frame();
  repaints += ran;
  if (ran !== 1) {
    fail('rapid input', `${N} slider events queued ${ran} frame callback(s); one frame is one repaint`);
  }
  if (computes !== 1) {
    fail('rapid input', `one repaint ran the model ${computes} time(s) — refresh() and ` +
      'tests() each used to call it, so a drag cost two evaluations a frame');
  }
  if (widthWrites) {
    fail('rapid input', `the canvas backing store was written ${widthWrites} time(s) at an ` +
      'unchanged size; assigning canvas.width clears and reallocates it even when the ' +
      'number is the same, which at 900x296 and a dpr of 2 is 4.3 MB of zeroing a frame');
  }
  delete cv.width;
  cv.width = held;
  spec.compute = real;
  S.forget(u.id);
}

/* ============================================================ 6. what a screen reader meets */
{
  for (const u of UNITS) {
    S.forget(u.id);
    const root = S.mount(u.id, u.unit); mounts++;
    const spec = S.Tune.get(u.unit.model);
    const cv = root.querySelector('#tn-cv');
    if (cv.getAttribute('role') !== 'img') {
      fail(u.where, 'the plot canvas has no role="img" — a screen reader announces it as nothing');
    }
    const name = String(cv.getAttribute('aria-label') || '');
    if (!name.trim()) fail(u.where, 'the plot canvas has no accessible name');
    if (ROT.test(name)) fail(u.where, `the plot's name reads "${name.match(ROT)[0]}" — ${name.slice(0, 90)}`);
    /* the name has to describe THIS plot, not a constant */
    if (!name.includes(String((spec.plot(
      Object.fromEntries(spec.params.map((p) => [p.k, p.def])),
      Object.assign({}, spec.constants, u.unit.constants || {})).points || []).length))) {
      fail(u.where, `the plot's name does not describe what was drawn — "${name.slice(0, 90)}"`);
    }
    for (const p of spec.params) {
      const sl = root.querySelector('input[data-k="' + p.k + '"]');
      const lab = sl.closest('label');
      if (!lab) fail(u.where, `the ${p.k} slider is not inside a label, so it has no accessible name`);
      /* read it on the opening markup AND after a drag: the two are written by
         different lines, and the mutation run passed this section with the drag path
         broken because only the opening one was ever checked */
      S.drag(root, p.k, p.def); drags++;
      S.frame();
      for (const [when, vt] of [['as drawn', String(sl.getAttribute('aria-valuetext') || '')]]) {
        if (!vt.includes(p.label)) {
          fail(u.where, `${when}, the ${p.k} slider announces its own raw number rather ` +
            `than what the page shows (aria-valuetext "${vt}")`);
        }
        if (p.unit && !vt.includes(p.unit)) {
          fail(u.where, `${when}, the ${p.k} slider's aria-valuetext "${vt}" drops the ` +
            `unit "${p.unit}"`);
        }
      }
      /* the printed value is hidden from the name, or it would BE the name */
      const b = root.querySelector('[data-out="' + p.k + '"]');
      if (b.getAttribute('aria-hidden') !== 'true') {
        fail(u.where, `the ${p.k} value is inside the label and not aria-hidden, so it lands ` +
          'in the slider\'s NAME and changes on every drag');
      }
    }
    const goal = root.querySelector('#tn-state');
    if (goal.getAttribute('aria-live') !== 'polite') {
      fail(u.where, 'the constraint list is the block that says whether the exercise is ' +
        'finished and it is not a live region');
    }
    /* and it must not flood: an unchanged sentence must not be rewritten */
    const before = goal.innerHTML;
    let writes = 0;
    Object.defineProperty(goal, 'innerHTML', {
      get() { return before; },
      set() { writes++; },
      configurable: true,
    });
    const p0 = spec.params[0];
    /* the value the slider is HOLDING, not the one it opened at: the aria-valuetext
       check above has already moved it, and dragging back to the opening figure is a
       real change for every unit whose `initial` differs from its model's `def` */
    const sl0 = root.querySelector('input[data-k="' + p0.k + '"]');
    S.drag(root, p0.k, sl0.value);
    drags++;
    S.frame();
    if (writes) {
      fail(u.where, `a drag that changed nothing rewrote the live region ${writes} time(s) — ` +
        'a screen reader gets one thing to consider saying per frame');
    }
    delete goal.innerHTML;
    S.forget(u.id);
  }
}

/* ============================================================ 7. focus survives a repaint
 *
 * Reset and a passing Check both rebuild the whole page, so the button that was pressed
 * no longer exists and the keyboard lands back on the body. */
{
  const u = UNITS.find((x) => x.unit.model === 'divider');
  S.forget(u.id);
  const root = S.mount(u.id, u.unit); mounts++;
  const reset = root.querySelector('#tn-reset');
  reset.focus();
  S.click(root, 'tn-reset');
  const now = S.DOC.activeElement;
  const fresh = root.querySelector('#tn-reset');
  if (now !== fresh) {
    fail('focus', 'after Reset the keyboard is ' +
      (now === reset ? 'still on the button that was thrown away' : 'nowhere') +
      ' rather than on the Reset button of the page that replaced it');
  }
  /* and a passing Check */
  const spec = S.Tune.get(u.unit.model);
  const consts = Object.assign({}, spec.constants, u.unit.constants || {});
  let soln = null;
  const axes = spec.params.map((p) => {
    const vals = []; const st = p.step || 1;
    for (let x = p.min; x <= p.max + 1e-9; x += st) vals.push(+x.toFixed(6));
    return { k: p.k, vals };
  });
  const walk = (i, v) => {
    if (soln) return;
    if (i === axes.length) {
      const out = spec.compute(v, consts);
      if ((u.unit.constraints || []).every((c) => out[c.k] && S.Tune.holds(c, out[c.k].value))) soln = { ...v };
      return;
    }
    for (const x of axes[i].vals) { v[axes[i].k] = x; walk(i + 1, v); if (soln) return; }
  };
  walk(0, {});
  if (!soln) fail('focus', `no solution found for ${u.where}, so the passing-Check path is untested`);
  else {
    S.forget(u.id);
    S.save(u.id, soln);
    const root2 = S.mount(u.id, u.unit); mounts++;
    const check = root2.querySelector('#tn-check');
    check.focus();
    S.click(root2, 'tn-check');
    if (!S.completed(u.id)) fail('focus', `Check refused a position the sweep says satisfies every constraint`);
    if (S.DOC.activeElement !== root2.querySelector('#tn-check')) {
      fail('focus', 'after a passing Check the keyboard is not on the Check button of the ' +
        'page that replaced it');
    }
    /* and the view that replaced it is live, not the one the teardown marked dead */
    const p0 = spec.params[0];
    const was = rowsOf(root2).join('|');
    S.drag(root2, p0.k, p0.k === 'r1' ? p0.max : p0.max); drags++;
    S.frame();
    if (rowsOf(root2).join('|') === was) {
      fail('focus', 'after the repaint a drag changes nothing — paint() runs the previous ' +
        'teardown, and every call closes over the same `dead` flag, so the page now on ' +
        'the screen is the one marked gone');
    }
  }
  S.forget(u.id);
}

/* ============================================================ 8. a refusal explains */
{
  for (const u of UNITS) {
    S.forget(u.id);
    const root = S.mount(u.id, u.unit); mounts++;
    S.click(root, 'tn-check');
    const said = S.toastText();
    if (S.completed(u.id)) {
      fail(u.where, 'the unit is already met where it opens — verify_tune.mjs owns that, ' +
        'but this section cannot read a refusal that never happens');
      S.forget(u.id); continue;
    }
    if (!said.trim()) { fail(u.where, 'Check refused and said nothing'); S.forget(u.id); continue; }
    if (ROT.test(said)) fail(u.where, `the refusal reads "${said.match(ROT)[0]}" — ${said.slice(0, 90)}`);
    /* it has to name the value, not only restate the target the panel already shows */
    if (!/you have/.test(said)) {
      fail(u.where, `the refusal restates the constraint and stops: "${said.slice(0, 110)}"`);
    }
    S.forget(u.id);
  }
}

/* ============================================================ 9. one constraint rule
 *
 * renderTune tested the bounds before the equality and verify_tune.mjs tested the
 * equality first, so a constraint carrying both was graded one way and swept the other.
 * Both now read Tune.holds; this asks whether that is true rather than assuming it. */
{
  const gateRule = (c, x) => {
    if (c.eq !== undefined) return Math.abs(x - c.eq) <= (c.tol === undefined ? 0.01 : c.tol);
    if (c.min !== undefined && c.max !== undefined) return x >= c.min && x <= c.max;
    if (c.max !== undefined) return x <= c.max;
    if (c.min !== undefined) return x >= c.min;
    return false;
  };
  const probes = [
    [{ k: 'x', eq: 6, tol: 0.05 }, [5.9, 5.96, 6, 6.04, 6.1]],
    [{ k: 'x', eq: 6, tol: 0.05, max: 8 }, [5.9, 6, 7, 8, 9]],
    [{ k: 'x', min: 2, max: 3 }, [1.9, 2, 2.5, 3, 3.1]],
    [{ k: 'x', max: 1 }, [0, 1, 1.1, -5]],
    [{ k: 'x', min: 1 }, [0.9, 1, 5]],
  ];
  for (const [c, xs] of probes) {
    for (const x of xs) {
      if (S.Tune.holds(c, x) !== gateRule(c, x)) {
        fail('one rule', `${JSON.stringify(c)} at x = ${x}: the app says ` +
          `${S.Tune.holds(c, x)} and verify_tune.mjs's rule says ${gateRule(c, x)}`);
      }
    }
  }
  /* and a non-finite reading satisfies nothing, however open the bound */
  for (const x of [NaN, Infinity, -Infinity]) {
    if (S.Tune.holds({ k: 'x', max: 1 }, x)) {
      fail('one rule', `a readout of ${x} satisfies "at most 1" — a model that has ` +
        'overflowed would report its target met');
    }
  }
  if (S.Tune.holds({ k: 'x' }, 0)) fail('one rule', 'a constraint stating nothing is satisfied by anything');

  /* And the RENDERER has to be the thing using it. Checking Tune.holds proves only that
     studio.js is consistent with itself; renderTune kept a private copy for as long as
     this defect existed, and the mutation run put that copy back and this section did
     not notice. So: a synthetic unit whose constraint carries an equality AND a bound,
     driven through the real view, at a value the two rules disagree about.

     Vout = 3.000 V against {eq: 2.5, tol: 0.05, max: 4}. Equality-first says FAIL,
     bounds-first says PASS, and the tick on the page says which one is running. */
  const probe = {
    model: 'divider', title: 'staged', constants: { vin: 5 },
    initial: { r1: 2000, r2: 3000 },
    constraints: [{ k: 'vout', label: 'staged probe', eq: 2.5, tol: 0.05, max: 4 }],
  };
  S.forget('STAGE-M1-TN');
  const root = S.mount('STAGE-M1-TN', probe); mounts++;
  const chip = String((root.querySelectorAll('.tn-c')[0] || {}).textContent || '');
  const vout = S.Tune.get('divider').compute({ r1: 2000, r2: 3000 }, { vin: 5 }).vout.value;
  if (Math.abs(vout - 3) > 1e-9) {
    fail('one rule', `the probe was built to read 3.000 V and reads ${vout} — rebuild it`);
  } else if (chip.startsWith('✓')) {
    fail('one rule', 'the view grades a constraint carrying both an equality and a bound ' +
      'by the bound: Vout is 3.000 V against a target of 2.50 ± 0.05 and the page ticks ' +
      'it. renderTune is not using Tune.holds, so it and verify_tune.mjs are answering ' +
      'about different rules');
  }
  S.forget('STAGE-M1-TN');
}

/* ============================================================ the resize observer */
{
  const u = UNITS[0];
  S.forget(u.id);
  const root = S.mount(u.id, u.unit); mounts++;
  const before = S.liveObservers();
  S.leave();
  if (S.liveObservers() !== before - 1) {
    fail('resize', 'leaving the lesson left its ResizeObserver connected, redrawing a ' +
      'canvas that is no longer on the page');
  }
  const cv = root.querySelector('#tn-cv');
  const wasBad = cv.getContext('2d').bad.length;
  S.resizeTo(cv, 500, 296);
  const ran = S.frame();
  if (ran) fail('resize', 'a resize after the lesson was left still queued a repaint');
  if (cv.getContext('2d').bad.length !== wasBad) fail('resize', 'a repaint ran after dispose');
  S.forget(u.id);
}

/* ============================================================ report */
const vestigial = UNITS.filter((u) => {
  if (!u.unit.plotKey) return false;
  const spec = S.Tune.get(u.unit.model);
  if (!spec || !spec.marks) return true;
  return !(u.unit.constraints || []).some((c) => c.k === u.unit.plotKey && spec.marks(c, {}, {}));
});

const byWhere = new Map();
for (const [where, line] of problems) {
  if (!byWhere.has(where)) byWhere.set(where, []);
  byWhere.get(where).push(line);
}
for (const [where, lines] of byWhere) {
  console.log(`[FAIL] ${where}`);
  lines.slice(0, 8).forEach((l) => console.log(`            ! ${l}`));
  if (lines.length > 8) console.log(`            ... and ${lines.length - 8} more`);
}

if (vestigial.length) {
  console.log(`[note ] ${vestigial.length} unit(s) carry a plotKey nothing reads: ` +
    vestigial.map((u) => `${u.where} (${u.unit.plotKey})`).join(', '));
  console.log('        The model now says where a constraint belongs, so the field only ' +
    'names a key its model cannot place. Harmless, and recorded rather than removed ' +
    'because removing it means re-emitting the course.');
}

console.log(problems.length
  ? `\n${problems.length} problem(s) across ${byWhere.size} place(s) in the tune view`
  : `\nAll good: ${UNITS.length} tune units mount and answer — ${clampCases} hostile ` +
    `opening values clamped onto the grid, ${markChecks} targets inside their own axes, ` +
    `${paints} paints at ${WIDTHS.length} widths, ${drags} drags, ` +
    `${mounts} mounts, one repaint a frame, and a refusal that names the value.`);
process.exit(problems.length ? 1 : 0);
