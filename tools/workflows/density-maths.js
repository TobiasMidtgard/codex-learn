export const meta = {
  name: 'density-maths',
  description: 'Give the mathematics courses a syllabus and then modules you can learn from',
  phases: [
    { title: 'Syllabus', detail: 'one agent per course: design the missing topics' },
    { title: 'Write', detail: 'courses in parallel, modules sequential within each' },
    { title: 'Audit', detail: 'one fact-check per course' },
  ],
}

/* Args: ['MA101', 'MA111', ...] */
const ROOT = 'C:/Users/Tobit/Documents/ProgrammingProjects/Programlearningplatform'
const COURSES = (Array.isArray(args) && args.length ? args : [])
if (!COURSES.length) throw new Error('pass a course list as args')

const CONTEXT = `
These are the worst courses in the catalog by a distance. Across the five mathematics
courses there are twenty units in twenty modules — ONE unit per module, and that unit
is a Python lab. They currently teach mathematics by asking you to write code, with
no explanation, no derivation and not one worked problem. They are also prerequisites
for much of the engineering side, so a learner arrives at circuit analysis having been
taught none of the mathematics it assumes.
`

const SYLLABUS = (id) => `
REPO: ${ROOT}
COURSE: ${id}
AUTHOR FILE: catalog/authors/${id}.py   <-- the ONLY file you may edit.
${CONTEXT}
## Your job: design the missing syllabus

1. READ the course first — catalog/authors/${id}.py in full, and its entry in
   catalog/_spine.json (which year it sits in, its level, its summary, what depends on
   it). Read the ids and titles of the neighbouring maths courses so you do not
   duplicate a topic that belongs to one of them, and read the EE courses that name
   this one as a prerequisite so you cover what they actually assume.

2. Write down the topics a real version of this subject covers at this level, in
   teaching order. Keep the existing modules where they sit — do not rewrite or
   reorder them — and add the missing ones to reach 9-11 modules total. If the
   subject honestly does not carry that many distinct topics at this level, add fewer
   and say so; a padded module is worse than a missing one.

3. For each NEW module write only: \`title\`, \`summary\`, 3-5 \`concepts\`, and ONE
   \`quiz\` so the module is not empty. The units come in a later pass — do not write
   them now. Do not add labs.

The emitter allows 3-14 modules. Verify with:

    python -X utf8 tools/emit.py catalog/authors/${id}.py

Do NOT run \`emit.py --all\` or \`node build.mjs\`.

Report the syllabus you designed, which modules are new, and the final emit line.
`

const BRIEF = (id, n, total) => `
REPO: ${ROOT}
COURSE: ${id}
YOUR MODULE: module ${n} of ${total}
AUTHOR FILE: catalog/authors/${id}.py   <-- the ONLY file you may edit, and only the
module-${n} dict. Other modules are being written by other agents in sequence.
${CONTEXT}
## What this module must contain: 10-13 units

Keep whatever is already there. Where a \`read\` unit exists but is short, EXPAND it.

  * 1-3 \`read\` units, **1200-2500 words each**. The explanation someone learns the
    mathematics from. Each must
      - open with the question the idea answers, or the thing that goes wrong without
        it — not with a definition
      - build to the statement rather than announcing it, and PROVE it or show why it
        is true, at the level the course sits at
      - carry AT LEAST TWO worked examples all the way through, every line of algebra
        shown. One should be routine; one should be the case people get wrong
      - name the mistake people actually make, and say why it is tempting
      - say where the result STOPS holding — the hypothesis that matters, the case it
        excludes — and what happens there
      - use markdown headings for the stages, and \`$...$\` / \`$$...$$\` LaTeX for
        every symbol and equation. Both render. Do not write mathematics as plain
        ASCII in a mathematics course.
    The emitter rejects a reading unit under 400 words.

  * 2-4 \`derive\` units. THIS IS THE CENTRE OF A MATHEMATICS MODULE, not an
    afterthought. A derivation is 2-8 steps; each has a prompt, the answer the
    learner must produce, and a hint or a deconstruction for when they are stuck.
    Every step is checked SYMBOLICALLY against SymPy by
    tools/verify_derivations.py, so an answer that is algebraically equivalent to the
    expected one passes and a step that does not follow fails. That makes this the
    one unit kind in the catalog that can grade mathematics properly — use it.
    A placeholder must never be the answer.

  * 3-5 \`numeric\` units, a LADDER, easiest first: evaluate, then apply, then a case
    where the value has to be derived before it can be computed. Use \`figure\` (a
    text statement of the problem) and NOT \`diagram\` — \`diagram\` draws an
    electronic schematic and the emitter will demand a circuit-solver check for it.
    Give an explicit \`tol\` that reflects the precision the method actually yields.

  * 1-2 \`blanks\`. In a mathematics course the listing with \`___\` holes is usually
    a DERIVATION or an equation written out line by line, not code — a step of an
    integration, the terms of an expansion, the entries of a matrix, the cases of a
    piecewise definition. Blanks work on mathematics as readily as on code, and that
    is how a mathematics module asks a question without pretending to be a
    programming one.

  * 1 \`quiz\`: 3-10 questions, exactly 4 options, \`a\` the 0-3 index, a \`why\` on
    every one.

  * a \`sandbox\` ONLY if the module is genuinely about the behaviour one of these
    visualisers shows: \`phase-portrait\` (systems of differential equations),
    \`pole-step\` (second-order response), \`bode\`, \`z-plane\`, \`spectrum\`.
    Otherwise skip the kind.

  * do NOT add a lab, and leave the lab this module already has.

## Unit kinds that do NOT apply

\`build\`, \`match\` and \`tune\` are circuit machinery — a schematic editor, a symbol
drill over electronic components, three analogue circuit models. They will fail the
build in a mathematics course.

## Correctness

Every line of every derivation and every worked example must be right. Check the
algebra, then let verify_derivations confirm what it can. A worked example with a slip
is worse than none: it is followed line by line by someone who cannot yet tell.

## Voice

Match the existing modules. A knowledgeable person explaining something to someone
capable — not a textbook reciting, not enthusiasm standing in for content. State the
thing, show why it is true, say where it stops being true.

## Verify, from ${ROOT}

    python -X utf8 tools/emit.py catalog/authors/${id}.py
    python -X utf8 tools/verify_derivations.py catalog/${id}.json
    python -X utf8 tools/verify_labs.py catalog/${id}.json

All must be clean; re-emitting is REQUIRED. Do NOT run \`emit.py --all\` or
\`node build.mjs\`.

Report: units added by kind, word count of each reading unit, the derivations and how
many steps each, the numeric ladder with answers, and the final line of each gate.
`

phase('Syllabus')
const spines = await parallel(COURSES.map((id) => () =>
  agent(SYLLABUS(id), { label: 'syllabus:' + id, phase: 'Syllabus', schema: {
    type: 'object', additionalProperties: false,
    required: ['course', 'modulesBefore', 'modulesAfter', 'newTitles', 'emitClean'],
    properties: {
      course: { type: 'string' }, modulesBefore: { type: 'integer' },
      modulesAfter: { type: 'integer' },
      newTitles: { type: 'array', items: { type: 'string' } },
      emitClean: { type: 'boolean' },
    },
  } })
))

const planned = spines.filter(Boolean)
log(`syllabus: ${planned.map((p) => `${p.course} ${p.modulesBefore}->${p.modulesAfter}`).join(', ')}`)

phase('Write')
const perCourse = await parallel(planned.map((p) => async () => {
  const done = []
  for (let n = 1; n <= p.modulesAfter; n++) {
    const r = await agent(BRIEF(p.course, n, p.modulesAfter),
      { label: `${p.course}/M${n}`, phase: 'Write', schema: {
        type: 'object', additionalProperties: false,
        required: ['course', 'module', 'unitsAfter', 'readWords', 'derivations', 'gatesClean', 'notes'],
        properties: {
          course: { type: 'string' }, module: { type: 'integer' },
          unitsAfter: { type: 'integer' }, readWords: { type: 'string' },
          derivations: { type: 'string' }, gatesClean: { type: 'boolean' }, notes: { type: 'string' },
        },
      } })
    if (r) {
      done.push(r)
      log(`${p.course} M${n}: ${r.unitsAfter} units, reading ${r.readWords}, derive ${r.derivations}` +
        (r.gatesClean ? '' : '  [GATES NOT CLEAN]'))
    } else log(`${p.course} M${n}: produced nothing`)
  }
  return { course: p.course, modules: done }
}))

const wrote = perCourse.filter(Boolean)

phase('Audit')
const audited = await parallel(wrote.map((w) => () =>
  agent(`You are fact-checking newly written mathematics teaching content. Be
adversarial: find what is WRONG.

REPO: ${ROOT}
COURSE: ${w.course}

Every module has just been written to open with a long explanation, prove its result,
and carry derivations and a ladder of problems. The authors' accounts:

${w.modules.map((m) => `M${m.module} (${m.unitsAfter} units, reading ${m.readWords}, derive ${m.derivations}): ${m.notes}`).join('\n\n').slice(0, 40000)}

Read catalog/${w.course}.json. Do the algebra yourself — every line of every worked
example and every derivation step — before you look at what is claimed.

Hunt for:
  * a line of algebra in a worked example that does not follow from the one above it
  * a proof that assumes what it is proving, or that quietly needs a hypothesis the
    statement does not carry
  * a derivation step whose stated answer is not what the prompt asks for, even if
    verify_derivations passed it — the gate checks equivalence to the stated answer,
    not that the answer answers the question
  * a stated limit or hypothesis that is wrong about where the result fails, or a
    counterexample that is not one
  * a quiz option marked correct that is not, or two defensible correct answers
  * a numeric answer miscalculated, or a tolerance so loose a wrong method passes
  * a fill-in whose key does not work, or where another option works equally well
  * a definition that is subtly non-standard without saying so

Report ONLY defects of fact, with the exact module and unit and your working. Not
style, not difficulty, not coverage. An empty list is a fine answer.`,
    { label: 'audit:' + w.course, phase: 'Audit', effort: 'high', schema: {
      type: 'object', additionalProperties: false,
      required: ['course', 'defects'],
      properties: {
        course: { type: 'string' },
        defects: {
          type: 'array',
          items: {
            type: 'object', additionalProperties: false,
            required: ['where', 'claim', 'truth', 'severity'],
            properties: {
              where: { type: 'string' }, claim: { type: 'string' }, truth: { type: 'string' },
              severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
            },
          },
        },
      },
    } })
))

const defects = audited.filter(Boolean).flatMap((a) =>
  a.defects.map((d) => Object.assign({ course: a.course }, d)))
log(`wrote ${wrote.reduce((n, w) => n + w.modules.length, 0)} module(s); ` +
  `${defects.length} defect(s), ${defects.filter((d) => d.severity !== 'minor').length} major or worse`)
return { planned, wrote: wrote.map((w) => ({ course: w.course, modules: w.modules.length })), defects }
