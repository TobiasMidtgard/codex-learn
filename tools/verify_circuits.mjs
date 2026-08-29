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
  '\nmodule.exports = { runCircuitChecks, Netlist, MNA };'
)(mod);
const { runCircuitChecks } = mod.exports;

const args = process.argv.slice(2);
const files = args.length ? args.map((a) => join(ROOT, a))
  : readdirSync(join(ROOT, 'catalog'))
      .filter((f) => f.endsWith('.json') && !f.startsWith('_'))
      .map((f) => join(ROOT, 'catalog', f));

let problems = 0;
let exercises = 0;
let totalChecks = 0;

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

if (!exercises) {
  console.log('no circuit exercises found');
  process.exit(0);
}
console.log(problems
  ? `\n${problems} course(s) with a circuit exercise that cannot be completed as written`
  : `\nAll good: ${exercises} circuit exercises, ${totalChecks} checks verified.`);
process.exit(problems ? 1 : 0);
