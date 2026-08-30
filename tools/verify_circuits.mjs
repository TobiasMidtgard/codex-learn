/**
 * verify_circuits.mjs — the correctness gate for circuit-building exercises.
 *
 * Same two questions `verify_labs.py` asks of a code lab, asked of a schematic:
 *
 *   1. Does the reference circuit pass every check?   (must be yes)
 *   2. Does the starting circuit fail at least one?   (must be yes, or the exercise
 *      is already solved and the learner is asked to do nothing)
 *
 * It runs the real grading code out of src/circuit.js, so it cannot drift from what
 * the browser does.
 *
 *   node tools/verify_circuits.mjs
 *   node tools/verify_circuits.mjs catalog/EE101.json
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

/* load the grading code exactly as shipped */
const mod = { exports: {} };
new Function('module',
  readFileSync(join(ROOT, 'src', 'circuit.js'), 'utf8') +
  '\nmodule.exports = { runCircuitChecks, Netlist, MNA, fmtEng, parseEng };'
)(mod);
const { runCircuitChecks, fmtEng, parseEng } = mod.exports;

const args = process.argv.slice(2);
const files = args.length ? args.map((a) => join(ROOT, a))
  : readdirSync(join(ROOT, 'catalog'))
      .filter((f) => f.endsWith('.json') && !f.startsWith('_'))
      .map((f) => join(ROOT, 'catalog', f));

let problems = 0;
let exercises = 0;
let totalChecks = 0;
const partValues = [];

for (const file of files) {
  const course = JSON.parse(readFileSync(file, 'utf8'));
  const found = [];

  for (const [mi, m] of (course.modules || []).entries()) {
    if (m.build) found.push([`M${mi + 1}`, m.build]);
  }
  if (!found.length) continue;

  const lines = [];
  let bad = false;

  for (const [where, b] of found) {
    exercises++;
    totalChecks += b.checks.length;
    for (const model of [b.start, b.solution]) {
      for (const part of (model && model.parts) || []) {
        if (part.value !== undefined && part.kind !== 'GND' && part.kind !== 'OUT') {
          partValues.push([part.value, `${course.id}/${where}`]);
        }
      }
    }

    const sol = runCircuitChecks(b.solution, b.checks);
    const solPassed = sol.filter((r) => r.pass).length;

    const start = runCircuitChecks(b.start || { parts: [], wires: [] }, b.checks);
    const startPassed = start.filter((r) => r.pass).length;

    lines.push(`          ${course.id}/${where}`.padEnd(26) +
      `reference ${solPassed}/${sol.length} · start ${startPassed}/${start.length}`);

    if (solPassed !== sol.length) {
      bad = true;
      for (const r of sol.filter((x) => !x.pass)) {
        lines.push(`            ! reference fails "${r.name}": ${r.message}`);
      }
    }
    if (startPassed === start.length && start.length) {
      bad = true;
      lines.push('            ! the starting circuit already passes everything — ' +
        'there is nothing for the learner to build');
    }
  }

  console.log(`[${bad ? 'FAIL' : 'ok  '}] ${course.id.padEnd(8)} ${found.length} circuit exercise(s)`);
  lines.forEach((l) => console.log(l));
  if (bad) problems++;
}

/* ---------------------------------------------------------------- part labels
 *
 * Every check above asks what the SOLVER computed. None of them asked what the
 * EDITOR displays, and for a long time it displayed 100 pF as "1 pF": the trailing
 * zeros of an integer were being stripped along with the trailing zeros of a decimal.
 * A learner comparing the canvas against the brief would have concluded the brief was
 * wrong. Formatting a value and reading it back has to return the value. */
{
  const table = [
    100e-12, 200, 1e-10, 0.1, 100e-9, 10, 1000, 150, 2.5e-6,
    42.2e-9, 1e-6, 4545, 0.01, 20, 1.5e9, 470, 3300, 25,
  ].map((v) => [v, 'the fixed table']);

  const bad = [];
  for (const [v, where] of table.concat(partValues)) {
    const text = fmtEng(v, '');
    const back = parseEng(text, NaN);
    /* the label rounds for display, so allow the rounding and nothing beyond it */
    if (!(Math.abs(back - v) <= Math.abs(v) * 0.006)) {
      bad.push(`${where}: ${v} is labelled "${text.trim()}", which reads back as ${back}`);
    }
  }

  if (bad.length) {
    console.log('\nPART LABELS THAT DO NOT SAY WHAT THE VALUE IS');
    for (const b of bad.slice(0, 12)) console.log('  !', b);
    if (bad.length > 12) console.log(`  ... and ${bad.length - 12} more`);
    problems++;
  } else {
    console.log(`[ok  ] labels   ${table.length + partValues.length} part values ` +
      'format and read back unchanged');
  }
}

if (!exercises) {
  console.log('no circuit exercises found');
  process.exit(0);
}
console.log(problems
  ? `\n${problems} course(s) with a circuit exercise that cannot be completed as written`
  : `\nAll good: ${exercises} circuit exercises, ${totalChecks} checks verified.`);
process.exit(problems ? 1 : 0);
