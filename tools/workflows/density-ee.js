export const meta = {
  name: 'density-ee',
  description: 'Bring named EE modules to 10-13 units each, opening with a real explanation',
  phases: [{ title: 'Write', detail: 'courses in parallel, named modules sequential within each' }],
}

/* Args: [{ id: 'EE101', only: [7, 8, 9, 10, 11] }, ...]
   `only` names the modules still to do, so a resumed run never rewrites a module that
   is already dense — this exists because two runs have now been cut off by a usage
   limit partway through a course. */
const ROOT = 'C:/Users/Tobit/Documents/ProgrammingProjects/Programlearningplatform'
const COURSES = (Array.isArray(args) && args.length ? args : [])
if (!COURSES.length) throw new Error('pass [{id, only:[...]}] as args')

const BRIEF = (c, n) => `
REPO: ${ROOT}
COURSE: ${c.id}
YOUR MODULE: module ${n} (the ${n}th entry of MODULES in the file)
AUTHOR FILE: catalog/authors/${c.id}.py   <-- the ONLY file you may edit, and only
the module-${n} dict inside it. Other modules of this course are written by other
agents in sequence; leave them exactly as they are.

## The problem, in the reader's own words

"I refuse to believe you can actually learn series, parallel and Kirchhoff's two laws
and make it stick with a quiz, a build and a lab. The subject matter isn't even
explained. This should probably be at least 10-12 tasks."

Then, on seeing a first attempt at ~800 words of explanation: "Longer, make it more
detailed."

## Target: 10-13 units in this module

Keep every unit already there. Where a \`read\` unit exists but is shorter than the
length below, EXPAND it — do not discard work that is correct, only short.

  * 1-3 \`read\` units, **1200-2500 words each**. The centre of the work: the
    explanation someone learns from, not a summary. Each must
      - start from the physical picture, not the formula
      - derive or motivate the formula rather than announcing it
      - carry AT LEAST TWO worked examples all the way through with real numbers and
        units, showing intermediate steps
      - name the mistake people actually make, and say why it is tempting
      - say where the idea STOPS holding, and what replaces it there
      - use markdown headings for the stages, fenced blocks for worked arithmetic
    Maths in LaTeX: \`$...$\` inline, \`$$...$$\` display. Both render.
    The emitter rejects a reading unit under 400 words.
    Two separable ideas in the module means two reading units, not one enormous one.

  * 3-5 \`numeric\` units, a LADDER, easiest first. The first nearly mechanical: one
    unknown, one rule. The last real work: several unknowns, a quantity that is not a
    node voltage, or a source that is not the obvious one. Vary what is asked —
    voltage, current, resistance, power, time, frequency.

  * 1 \`quiz\`, 1-2 \`blanks\`, and a \`derive\` where the material carries genuine
    algebra to work through.

  * an applied unit (\`build\`, \`match\`, \`tune\`, \`sandbox\`) if one fits and the
    module has none.

  * do NOT add a lab. Leave the lab this module already has.

## Circuit problems are machine-verified

A \`numeric\` unit carrying a \`diagram\` MUST carry a \`check\`: one line of
JavaScript run against the app's own MNA solver, returning the quantity the prompt
asks for. tools/verify_numeric.mjs solves the schematic and compares to your stated
answer; the emitter refuses a schematic without one.

    c.vout()        voltage at the probed OUT node
    c.dc()          -> { v: nodeVoltages, currents: keyed by part id }
    c.values('R')   resistor values in declaration order
    c.net.parts     each with .id .kind .value .n1 .n2
    c.gain(f)       magnitude at a frequency

Read src/circuit.js (circuitContext) for the authority and catalog/authors/EE101.py
M1/M3/M4 for worked examples. Prefer reading values off the circuit to repeating
constants that also appear in the diagram — a check that restates the numbers cannot
catch a diagram edited without re-working the answer.

Diagram parts take kinds R, C, L, V, I, GND, OUT with integer x/y grid positions plus
a \`wires\` list. If a question is about a circuit you cannot draw, either draw the
circuit the question is actually about, or use \`figure\` (text) instead of
\`diagram\`. Never state an answer the drawn circuit does not produce.

Sandbox visualisers: divider rc-lowpass rlc pole-step bode z-plane phase-portrait
pole-place kalman sliding-mode spectrum noise-corner switching smith pipeline cache.
Match symbols: R C L D LED GND V BATT I NPN PNP SW OPAMP.
Tune models: divider (vout i ratio), rc-lowpass (fc keep reject tau), rlc (wn fn zeta peak).
A sandbox \`notice\` must describe what the visualiser ACTUALLY draws — read the draw
loop in src/studio.js rather than assuming. One shipped claiming three curves where
two are drawn.

## Correctness

Every number right, including every intermediate step of every worked example. A
worked example with a slip is worse than none: it is followed line by line by someone
who cannot yet tell it is wrong. Check the direction of every dependence you assert —
a correction to one of these courses inverted "proportional" and "inversely
proportional" in the sentence it was written to fix.

## Voice

Read the existing modules of this course and match them. A knowledgeable person
explaining something to someone capable. Not marketing, not a textbook reciting, not
enthusiasm standing in for content.

## Verify, from ${ROOT}

    python -X utf8 tools/emit.py catalog/authors/${c.id}.py
    node tools/verify_numeric.mjs catalog/${c.id}.json
    node tools/verify_circuits.mjs catalog/${c.id}.json
    node tools/verify_tune.mjs catalog/${c.id}.json
    python -X utf8 tools/verify_derivations.py catalog/${c.id}.json

All must be clean. Re-emitting is REQUIRED. Do NOT run \`emit.py --all\` or
\`node build.mjs\`.

Report: units added by kind, the word count of each reading unit, the ladder easiest
to hardest with answers, and the final line of each gate.
`

const WROTE = {
  type: 'object', additionalProperties: false,
  required: ['course', 'module', 'unitsAfter', 'readWords', 'added', 'gatesClean', 'notes'],
  properties: {
    course: { type: 'string' }, module: { type: 'integer' }, unitsAfter: { type: 'integer' },
    readWords: { type: 'string' }, added: { type: 'string' },
    gatesClean: { type: 'boolean' }, notes: { type: 'string' },
  },
}

phase('Write')
const out = await parallel(COURSES.map((c) => async () => {
  const done = []
  for (const n of c.only) {
    const r = await agent(BRIEF(c, n), { label: `${c.id}/M${n}`, phase: 'Write', schema: WROTE })
    if (r) {
      done.push(r)
      log(`${c.id} M${n}: ${r.unitsAfter} units, reading ${r.readWords}` +
        (r.gatesClean ? '' : '  [GATES NOT CLEAN]'))
    } else log(`${c.id} M${n}: produced nothing`)
  }
  return { course: c.id, modules: done }
}))

const wrote = out.filter(Boolean)
log(`wrote ${wrote.reduce((n, w) => n + w.modules.length, 0)} module(s) across ${wrote.length} course(s)`)
return wrote.map((w) => ({ course: w.course, done: w.modules.map((m) => m.module),
  units: w.modules.reduce((n, m) => n + m.unitsAfter, 0) }))
