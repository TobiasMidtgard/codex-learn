/**
 * verify_tune.mjs — the correctness gate for "hit the target" units.
 *
 * A tune unit states constraints and hands the learner sliders. Two things can be
 * wrong with one, and neither is visible by reading it:
 *
 *   * the target is UNREACHABLE — no combination of slider positions satisfies every
 *     constraint at once, so the exercise cannot be finished. A tolerance one decimal
 *     place too tight, or a current cap that the required ratio rules out, does this
 *     without looking wrong on the page.
 *   * the target is ALREADY MET at the opening position, so there is nothing to do
 *     and the unit completes itself the moment anyone presses Check.
 *
 * So this sweeps the actual slider grid — the same values a learner can reach, at the
 * same step — against the actual model from src/studio.js, and reports both.
 *
 *     node tools/verify_tune.mjs                 # every course
 *     node tools/verify_tune.mjs catalog/EE101.json
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

/* load the models exactly as shipped, so this gate cannot drift from the browser */
const mod = { exports: {} };
new Function('module', 'PyRunner',
  readFileSync(join(ROOT, 'src', 'studio.js'), 'utf8') + '\nmodule.exports = { Tune };'
)(mod, { run: async () => {} });
const { Tune } = mod.exports;

function holds(c, x) {
  if (c.eq !== undefined) return Math.abs(x - c.eq) <= (c.tol === undefined ? 0.01 : c.tol);
  if (c.min !== undefined && c.max !== undefined) return x >= c.min && x <= c.max;
  if (c.max !== undefined) return x <= c.max;
  if (c.min !== undefined) return x >= c.min;
  return false;
}

function allHold(spec, consts, cons, v) {
  const out = spec.compute(v, consts);
  return cons.every((c) => out[c.k] && holds(c, out[c.k].value));
}

/* Sweep the reachable grid.
 *
 * The first version strided the axes to stay inside a budget, and that is exactly
 * wrong for this question: a target with a narrow solution band lives in the notches
 * a stride skips, so the gate reported UNREACHABLE for targets a learner can hit —
 * the one verdict that must never be wrong, because it condemns working content.
 *
 * So: sweep EVERY notch for one and two sliders, which is the whole catalogue today
 * (470 and 470x470 = 221k positions, well under a second). Only a three-slider model
 * needs thinning, and there the stride is reported rather than hidden, so a FAIL from
 * a thinned sweep can be read as "not found" instead of "does not exist". */
function sweep(spec, consts, cons, budget) {
  let thinned = false;
  const axes = spec.params.map((p) => {
    const n = Math.floor((p.max - p.min) / p.step) + 1;
    const per = Math.round(Math.pow(budget, 1 / spec.params.length));
    const stride = spec.params.length <= 2 ? 1 : Math.max(1, Math.ceil(n / per));
    if (stride > 1) thinned = true;
    const vals = [];
    for (let i = 0; i < n; i += stride) vals.push(+(p.min + i * p.step).toFixed(6));
    if (vals[vals.length - 1] !== p.max) vals.push(p.max);
    return { k: p.k, vals };
  });
  let found = null;
  let tried = 0;
  const walk = (i, v) => {
    if (found) return;
    if (i === axes.length) {
      tried++;
      if (allHold(spec, consts, cons, v)) found = { ...v };
      return;
    }
    for (const x of axes[i].vals) { v[axes[i].k] = x; walk(i + 1, v); if (found) return; }
  };
  walk(0, {});
  return { found, tried, thinned };
}

const args = process.argv.slice(2);
const files = args.length ? args.map((a) => join(ROOT, a))
  : readdirSync(join(ROOT, 'catalog'))
      .filter((f) => f.endsWith('.json') && !f.startsWith('_'))
      .map((f) => join(ROOT, 'catalog', f));

let problems = 0;
let units = 0;

for (const file of files) {
  const course = JSON.parse(readFileSync(file, 'utf8'));
  const found = [];
  for (const [mi, m] of (course.modules || []).entries()) {
    if (m.tune) found.push([`M${mi + 1}`, m.tune]);
  }
  if (!found.length) continue;

  const lines = [];
  let bad = false;

  for (const [where, t] of found) {
    units++;
    const spec = Tune.get(t.model);
    if (!spec) {
      lines.push(`            ! names the "${t.model}" model, which is not registered`);
      bad = true;
      continue;
    }
    const consts = Object.assign({}, spec.constants, t.constants || {});
    const cons = t.constraints || [];

    /* the position the unit opens at */
    const start = {};
    spec.params.forEach((p) => {
      start[p.k] = (t.initial && t.initial[p.k] !== undefined) ? t.initial[p.k] : p.def;
    });
    const startMet = allHold(spec, consts, cons, start);

    const { found: soln, tried, thinned } = sweep(spec, consts, cons, 1000000);

    if (!soln) {
      bad = true;
      const out = spec.compute(start, consts);
      lines.push(`            ! ${where} is ${thinned ? 'probably unreachable' : 'UNREACHABLE'} — ` +
        `swept ${tried} slider position(s)` +
        (thinned ? ' on a THINNED grid, so a very narrow solution could have been missed'
                 : ' (every reachable one)') +
        ' and none satisfies every constraint at once');
      cons.forEach((c) => {
        const r = out[c.k];
        lines.push(`                ${c.label}  (at the opening position: ` +
          `${r ? (+r.value).toFixed(r.dp) + (r.unit ? ' ' + r.unit : '') : '?'})`);
      });
    } else if (startMet) {
      bad = true;
      lines.push(`            ! ${where} is ALREADY MET where it opens — there is nothing to do`);
    } else {
      lines.push(`            ${where.padEnd(4)} ${t.model.padEnd(11)} solvable, e.g. ` +
        Object.entries(soln).map(([k, x]) => `${k}=${x}`).join(' ') + `  · start fails`);
    }
  }

  console.log(`[${bad ? 'FAIL' : 'ok  '}] ${course.id.padEnd(8)} ${found.length} tune unit(s)`);
  lines.forEach((l) => console.log(l));
  if (bad) problems++;
}

if (!units) {
  console.log('no tune units found');
  process.exit(0);
}
console.log(problems
  ? `\n${problems} course(s) with a target that cannot be hit, or that is already met`
  : `\nAll good: ${units} tune unit(s) verified reachable and not pre-solved.`);
process.exit(problems ? 1 : 0);
