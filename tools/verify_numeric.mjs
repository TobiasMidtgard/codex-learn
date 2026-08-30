/**
 * verify_numeric.mjs — the correctness gate for "find the value" units.
 *
 * A numeric unit states a schematic, a question, and an answer. Nothing checked that
 * the answer was the one the schematic actually produces. Every other unit kind is
 * machine-verified: a lab's reference solution has to pass its own tests, a build's
 * reference has to satisfy its own checks, a derivation's every step is confirmed
 * symbolically, a tune target is swept for reachability. A circuit problem's answer
 * was the one number in this catalog taken on trust — and it is about to become the
 * most common unit in it, because a graduated ladder of them is how you learn to
 * analyse a circuit.
 *
 * So: a numeric unit carrying a `diagram` also carries a `check` — a line of
 * JavaScript, evaluated against the SAME solver the app runs, that computes the
 * quantity the prompt asks for. This gate solves the schematic, runs the check, and
 * compares it to the stated answer within the stated tolerance.
 *
 * That catches four things reading cannot: an answer worked out by hand and got
 * wrong, a diagram edited without re-working the answer, a tolerance so tight the
 * intended answer misses it, and a prompt that asks for a quantity the drawn circuit
 * does not have.
 *
 *     node tools/verify_numeric.mjs                 # every course
 *     node tools/verify_numeric.mjs catalog/EE101.json
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

/* the app's own solver, loaded as shipped so this gate cannot drift from the browser */
const mod = { exports: {} };
new Function('module',
  readFileSync(join(ROOT, 'src', 'circuit.js'), 'utf8') +
  '\nmodule.exports = { circuitContext, Netlist, MNA, fmtEng };'
)(mod);
const { circuitContext } = mod.exports;

const asList = (x) => (!x ? [] : (Array.isArray(x) ? x : [x]));

const args = process.argv.slice(2);
const files = args.length
  ? args.map((a) => join(ROOT, a))
  : readdirSync(join(ROOT, 'catalog'))
      .filter((f) => f.endsWith('.json') && !f.startsWith('_'))
      .map((f) => join(ROOT, 'catalog', f));

let problems = 0;
let checked = 0;
let unverifiable = 0;
let noDiagram = 0;

for (const file of files) {
  const course = JSON.parse(readFileSync(file, 'utf8'));
  const found = [];
  for (const [mi, m] of (course.modules || []).entries()) {
    asList(m.numeric).forEach((q, qi) => {
      found.push([`M${mi + 1}${qi ? '.' + (qi + 1) : ''}`, q]);
    });
  }
  if (!found.length) continue;

  const lines = [];
  let bad = false;

  for (const [where, q] of found) {
    if (!q.diagram) { noDiagram++; continue; }
    if (!q.check) {
      unverifiable++;
      lines.push(`            ~ ${where} draws a schematic but states no \`check\`, so its ` +
        `answer of ${q.answer}${q.unit ? ' ' + q.unit : ''} is not verified by anything`);
      continue;
    }

    checked++;
    let ctx;
    try {
      ctx = circuitContext(q.diagram);
    } catch (e) {
      bad = true;
      lines.push(`            ! ${where} the schematic will not build: ${e && e.message}`);
      continue;
    }

    let got;
    try {
      got = new Function('c', '"use strict";\n' + q.check)(ctx);
    } catch (e) {
      bad = true;
      lines.push(`            ! ${where} the check threw: ${e && e.message}`);
      continue;
    }

    if (typeof got !== 'number' || !isFinite(got)) {
      bad = true;
      lines.push(`            ! ${where} the check returned ${JSON.stringify(got)}, not a number`);
      continue;
    }

    const diff = Math.abs(got - q.answer);
    if (diff > Math.abs(q.tol) + 1e-12) {
      bad = true;
      lines.push(`            ! ${where} says the answer is ${q.answer}${q.unit ? ' ' + q.unit : ''} ` +
        `±${q.tol}, but the circuit gives ${Number(got.toPrecision(8))} ` +
        `(off by ${Number(diff.toPrecision(4))})`);
    } else {
      lines.push(`            ${where.padEnd(7)} ${String(q.answer).padStart(10)}` +
        `${q.unit ? ' ' + q.unit : ''}  ✓ circuit gives ${Number(got.toPrecision(8))}`);
    }
  }

  if (!lines.length) continue;
  console.log(`[${bad ? 'FAIL' : 'ok  '}] ${course.id.padEnd(8)} ${found.length} numeric unit(s)`);
  lines.forEach((l) => console.log(l));
  if (bad) problems++;
}

console.log();
if (!checked && !unverifiable) {
  console.log(`no numeric units with a schematic found (${noDiagram} use a text figure)`);
  process.exit(0);
}
console.log(`${checked} answer(s) verified against the solver, ` +
  `${unverifiable} schematic(s) with no check, ${noDiagram} figure-only unit(s)`);
if (problems) {
  console.log(`\n${problems} course(s) state an answer their own circuit does not produce`);
  process.exit(1);
}
if (unverifiable) {
  console.log('\nEvery numeric unit that draws a circuit should carry a `check`, or its ' +
    'answer rests on arithmetic nobody re-did.');
}
process.exit(0);
