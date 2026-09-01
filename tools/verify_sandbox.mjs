/**
 * verify_sandbox.mjs — the correctness gate for intuition sandboxes and tune plots.
 *
 * A sandbox is the one unit kind with no answer to check, which is why nothing checked
 * it. Three things go wrong with one, and none of them is visible by reading it:
 *
 *   * the unit OPENS SOMEWHERE THE SLIDER CANNOT GO. build.mjs checks that an `initial`
 *     key names a real parameter; nothing checked the value. A number outside [min,max],
 *     or off the step grid, leaves the input clamped to its own notch while the draw and
 *     the readout still use the authored figure — thumb, number and picture disagreeing,
 *     with nothing anywhere saying so. Worse, the learner cannot get back to the opening
 *     state once they move it. Two lessons shipped like this.
 *
 *   * the model FALLS OVER AT AN EXTREME. Zero damping, identical poles, a stride of one,
 *     a load of 2 Ω: the persona brief says to feed a model zero, negative, enormous and
 *     identical values, and doing that by hand does not survive contact with 13
 *     visualisers and 44 parameters. A non-finite coordinate is a marker that silently
 *     is not drawn; a NaN in the readout is a sentence that says "NaN".
 *
 *   * a TUNE PLOT DRAWS ITS MARKER OUTSIDE ITS OWN AXES. The dot saying "you are here"
 *     is the only thing on the plot the learner is steering, and the axis ranges are
 *     authored by hand beside it. The RLC peak reaches 1414 against an axis capped at 6.
 *
 *     node tools/verify_sandbox.mjs
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

/* ---- load the models exactly as shipped, so this gate cannot drift from the browser.
   palette() reads CSS custom properties off the document, so hand it a stub that returns
   nothing and let every colour fall through to its declared fallback. */
const styleStub = { getPropertyValue: () => '' };
const docStub = { documentElement: {} };
const mod = { exports: {} };
new Function('module', 'PyRunner', 'getComputedStyle', 'document',
  readFileSync(join(ROOT, 'src', 'studio.js'), 'utf8') + '\nmodule.exports = { Sandbox, Tune };'
)(mod, { run: async () => {} }, () => styleStub, docStub);
const { Sandbox, Tune } = mod.exports;

/* ---- a canvas that records rather than paints, and objects to anything unpaintable.
   Everything a visualiser is allowed to call has to be here: a missing method throws
   TypeError and would be reported as a model failure, which is a lie about the model. */
function stubCtx() {
  const bad = [];
  const check = (op, args) => {
    for (const a of args) {
      if (typeof a === 'number' && !isFinite(a)) { bad.push(op + '(' + args.join(', ') + ')'); return; }
    }
  };
  const ctx = { bad, canvas: { width: 900, height: 320 } };
  for (const op of ['moveTo', 'lineTo', 'arc', 'rect', 'fillRect', 'strokeRect', 'clearRect',
    'translate', 'scale', 'setTransform', 'transform', 'quadraticCurveTo', 'bezierCurveTo',
    'arcTo', 'ellipse', 'rotate']) {
    ctx[op] = (...a) => check(op, a);
  }
  for (const op of ['beginPath', 'closePath', 'stroke', 'fill', 'clip', 'save', 'restore',
    'setLineDash', 'getLineDash', 'createLinearGradient', 'createRadialGradient']) {
    ctx[op] = () => undefined;
  }
  /* text position matters, the string does not */
  ctx.fillText = (s, x, y) => check('fillText', [x, y]);
  ctx.strokeText = (s, x, y) => check('strokeText', [x, y]);
  ctx.measureText = () => ({ width: 10 });
  return ctx;
}

const KIT = { frame: Sandbox.frame, palette: Sandbox.palette, fmt: Sandbox.fmt };

/* The reachable notches of one parameter, thinned to the ends and the interesting middle.
   A log parameter carries a tick index in the DOM, so its reachable set is the ticks. */
function corners(p) {
  const out = new Set([p.min, p.max, p.def]);
  if (p.min < 0 && p.max > 0) out.add(0);
  const mid = (p.min + p.max) / 2;
  out.add(p.log ? Math.sqrt(Math.max(p.min, 1e-12) * p.max) : mid);
  /* one notch in from each end: the value just past a guard is where a guard is wrong */
  const st = p.step || (p.max - p.min) / 100;
  if (!p.log) { out.add(Math.min(p.max, p.min + st)); out.add(Math.max(p.min, p.max - st)); }
  return [...out].filter((x) => isFinite(x)).sort((a, b) => a - b);
}

/* Every parameter at every corner, one at a time against the defaults, plus the all-min,
   all-max and all-mid combinations — the "identical values" case the brief asks for. */
function cases(params) {
  const def = {};
  params.forEach((p) => { def[p.k] = p.def; });
  const out = [{ label: 'defaults', v: { ...def } }];
  for (const p of params) {
    for (const x of corners(p)) out.push({ label: p.k + '=' + x, v: { ...def, [p.k]: x } });
  }
  const all = (pick) => {
    const v = {};
    params.forEach((p) => { v[p.k] = pick(p); });
    return v;
  };
  out.push({ label: 'every slider at min', v: all((p) => p.min) });
  out.push({ label: 'every slider at max', v: all((p) => p.max) });
  out.push({ label: 'every slider mid', v: all((p) => (p.log ? Math.sqrt(Math.max(p.min, 1e-12) * p.max) : (p.min + p.max) / 2)) });
  return out;
}

const asList = (x) => (!x ? [] : (Array.isArray(x) ? x : [x]));
const problems = [];
let drawn = 0, explained = 0;

/* ---------------------------------------------------------------- 1. the models */
const SIZES = [[900, 320], [420, 260], [240, 160]];   /* desktop, the 820px breakpoint, the floor */

for (const [id, spec] of Object.entries(Sandbox.all)) {
  const lines = [];
  for (const c of cases(spec.params)) {
    for (const [w, h] of SIZES) {
      const ctx = stubCtx();
      try { spec.draw(ctx, w, h, c.v, KIT); drawn++; }
      catch (e) { lines.push(`${c.label} at ${w}x${h}: draw() threw — ${e && e.message}`); continue; }
      if (ctx.bad.length) {
        lines.push(`${c.label} at ${w}x${h}: ${ctx.bad.length} non-finite draw call(s), first ${ctx.bad[0]}`);
      }
    }
    if (!spec.explain) continue;
    let text;
    try { text = spec.explain(c.v); explained++; }
    catch (e) { lines.push(`${c.label}: explain() threw — ${e && e.message}`); continue; }
    if (typeof text !== 'string' || !text.trim()) { lines.push(`${c.label}: explain() said nothing`); continue; }
    const rot = /NaN|undefined|Infinity/.exec(text);
    if (rot) lines.push(`${c.label}: explain() reads "${rot[0]}" — ${text.replace(/<[^>]*>/g, '').slice(0, 90)}`);
  }
  if (lines.length) problems.push([`visualiser ${id}`, lines]);
}

/* ---------------------------------------------------------------- 2. the tune plots */
for (const id of Tune.ids()) {
  const spec = Tune.get(id);
  if (!spec.plot) continue;
  const lines = [];
  for (const c of cases(spec.params)) {
    let pl;
    try { pl = spec.plot(c.v, spec.constants || {}); }
    catch (e) { lines.push(`${c.label}: plot() threw — ${e && e.message}`); continue; }
    const [x0, x1] = pl.xRange || [0, 1];
    const [y0, y1] = pl.yRange || [0, 1];
    if (![x0, x1, y0, y1].every(isFinite)) { lines.push(`${c.label}: axis range is not finite`); continue; }
    if (pl.at) {
      const [ax, ay] = pl.at;
      if (!isFinite(ax) || !isFinite(ay)) lines.push(`${c.label}: the marker is at a non-finite point`);
      else if (ax < x0 || ax > x1 || ay < y0 || ay > y1) {
        lines.push(`${c.label}: the marker sits at (${ax.toPrecision(4)}, ${ay.toPrecision(4)}), ` +
          `outside the axes [${x0.toPrecision(3)}..${x1.toPrecision(3)}] x [${y0}..${y1}]`);
      }
    }
    /* the curve may leave the frame, but the top of it is what the model is about */
    const peak = (pl.points || []).reduce((m, p) => (isFinite(p[1]) && p[1] > m ? p[1] : m), -Infinity);
    if (isFinite(peak) && peak > y1 * 1.02) {
      lines.push(`${c.label}: the curve peaks at ${peak.toPrecision(4)} against an axis ending at ${y1}`);
    }
    for (const p of pl.points || []) {
      if (!isFinite(p[0]) || !isFinite(p[1])) { lines.push(`${c.label}: a plotted point is not finite`); break; }
    }
  }
  if (lines.length) problems.push([`tune model ${id}`, lines]);
}

/* ---------------------------------------------------------------- 3. the opening state */
let initials = 0;
const files = readdirSync(join(ROOT, 'catalog'))
  .filter((f) => f.endsWith('.json') && !f.startsWith('_'));

for (const f of files) {
  const course = JSON.parse(readFileSync(join(ROOT, 'catalog', f), 'utf8'));
  const lines = [];
  for (const [mi, m] of (course.modules || []).entries()) {
    const seen = [];
    asList(m.sandbox).forEach((u) => seen.push([Sandbox.get(u.visualiser), u, u.visualiser]));
    asList(m.tune).forEach((u) => seen.push([Tune.get(u.model), u, u.model]));
    for (const [spec, unit, name] of seen) {
      if (!spec) continue;                       /* build.mjs owns the unknown-id case */
      for (const [k, val] of Object.entries(unit.initial || {})) {
        const p = spec.params.find((x) => x.k === k);
        if (!p) continue;                        /* build.mjs owns the unknown-key case */
        initials++;
        const at = `M${mi + 1} ${name}.${k}`;
        if (typeof val !== 'number' || !isFinite(val)) {
          lines.push(`${at} opens at ${JSON.stringify(val)}, which is not a number`);
          continue;
        }
        if (val < p.min || val > p.max) {
          lines.push(`${at} opens at ${val}, outside the slider's ${p.min}..${p.max}`);
          continue;
        }
        /* "in range" is not the same as "reachable". A log parameter's slider carries a
           tick index, so the test is that the authored value survives the round trip to
           a tick and back; a linear one has to land on the step grid. Both failures look
           identical to the learner: the opening state is one they cannot return to. */
        if (p.log) {
          const back = Sandbox.fromTick(p, Sandbox.toTick(p, val));
          if (back !== val) {
            lines.push(`${at} opens at ${val}, which its log slider cannot represent — ` +
              `the nearest tick reads back as ${back}`);
          }
          continue;
        }
        const n = (val - p.min) / (p.step || (p.max - p.min) / 100);
        if (Math.abs(n - Math.round(n)) > 1e-6) {
          const near = p.min + Math.round(n) * (p.step || (p.max - p.min) / 100);
          lines.push(`${at} opens at ${val}, which the slider cannot reach — ` +
            `it steps by ${p.step} from ${p.min}, so the nearest notch is ${+near.toFixed(6)}`);
        }
      }
    }
  }
  if (lines.length) problems.push([course.id, lines]);
}

/* ---------------------------------------------------------------- report */
for (const [where, lines] of problems) {
  console.log(`[FAIL] ${where}`);
  lines.forEach((l) => console.log(`            ${l}`));
}
console.log(problems.length
  ? `\n${problems.length} sandbox or tune problem(s)`
  : `\nAll good: ${Object.keys(Sandbox.all).length} visualiser(s) and ${Tune.ids().length} tune model(s) ` +
    `survive their extremes (${drawn} draws, ${explained} readouts), ` +
    `${initials} opening value(s) reachable.`);
process.exit(problems.length ? 1 : 0);
