export const meta = {
  name: 'density-cs',
  description: 'Bring computing modules to 10-13 units each, opening with a real explanation',
  phases: [
    { title: 'Write', detail: 'courses in parallel, modules sequential within each' },
    { title: 'Audit', detail: 'one fact-check per course, running the code' },
  ],
}

/* Args: [{ id: 'CS201', modules: 5 }, ...]  — module counts come from the catalog. */
const ROOT = 'C:/Users/Tobit/Documents/ProgrammingProjects/Programlearningplatform'
const COURSES = (Array.isArray(args) && args.length ? args : [])
if (!COURSES.length) throw new Error('pass a course list as args')

const BRIEF = (c, n) => `
REPO: ${ROOT}
COURSE: ${c.id}
YOUR MODULE: module ${n} of ${c.modules} (the ${n}th entry of MODULES in the file)
AUTHOR FILE: catalog/authors/${c.id}.py   <-- the ONLY file you may edit, and only
the module-${n} dict inside it. Other modules of this course are being written by
other agents in sequence; leave them exactly as they are.

## The problem

This module currently holds two or three units — typically a quiz and a Python lab —
and nowhere does it EXPLAIN its subject. A learner meets a list of concept bullets
and is then examined on them, which tests whether they already knew the material.

The reader's words, about a circuits module in the same catalog: "I refuse to believe
you can actually learn this and make it stick with a quiz, a build and a lab. The
subject matter isn't even explained. This should probably be at least 10-12 tasks."
Then, on seeing a first attempt at ~800 words of explanation: "Longer, make it more
detailed."

## What this module must contain: 10-13 units

Keep every unit already there. Where a \`read\` unit exists but is shorter than the
length below, EXPAND it — do not discard work that is correct, only short.

  * 1-3 \`read\` units, **1200-2500 words each**. The centre of the work: the
    explanation someone learns from, not a summary or a revision sheet. Each must
      - start from the concrete problem the idea exists to solve
      - build the idea up rather than announcing it
      - carry AT LEAST TWO worked examples all the way through. For computing that
        usually means TRACING: step through the code or the algorithm line by line
        with real values, showing the state after each step — the table filling in,
        the pointers moving, the packets arriving, the rows joining. Show the
        intermediate states, not just the answer.
      - name the mistake people actually make, and say why it is tempting
      - say where the idea STOPS being the right one, and what replaces it there
      - use markdown headings for the stages of the argument, and fenced code blocks
        for traces and listings
    Maths in LaTeX: \`$...$\` inline, \`$$...$$\` display; both render. Use it for
    complexity, recurrences and probability — do not write \`O(n log n)\` as plain
    text when the module is about growth rates.
    The emitter rejects a reading unit under 400 words.

  * 3-5 \`numeric\` units, a LADDER, easiest first. In a computing course a numeric
    unit asks for a number that has to be WORKED OUT, not looked up: operations
    executed for a given input, the value in a dynamic-programming cell, a cache hit
    rate, a bandwidth-delay product, index depth for a row count, throughput under a
    stated window, bits needed to address something, the constant a recurrence
    resolves to. Start nearly mechanical — one rule, one substitution. End with real
    work: several steps, or a quantity that has to be derived before it can be
    computed. Vary what is asked.

    IMPORTANT: use \`figure\` (a text description or a small listing) and NOT
    \`diagram\`. \`diagram\` draws an electronic schematic and is meaningless here;
    the emitter will demand a circuit-solver \`check\` for it.

  * 1-2 \`blanks\`. A listing with \`___\` holes. For computing the listing can be
    code, a SQL statement, a shell session, a protocol exchange, a config file, a
    regular expression, a state table, or a recurrence — whatever the module is
    actually about. Each hole needs 2-5 options and an explanation for every option,
    shown whichever was picked. Verify by substitution: run the listing with each
    option and know what actually happens, including whether it is a syntax error
    rather than a wrong answer.

  * 1 \`quiz\`. 3-10 questions, exactly 4 options, \`a\` the 0-3 index, a \`why\` on
    every question.

  * a \`derive\` ONLY where there is genuine algebra to work through and check
    symbolically: solving a recurrence to a closed form, an amortised bound, an
    expected value, a throughput or latency relation, a probability of collision.
    Every step is verified by tools/verify_derivations.py against SymPy, so a step
    that does not follow will fail the gate. Do not invent algebra for a module that
    has none — a second \`blanks\` on different material is the better answer there.

  * do NOT add a lab, and do not touch the lab this module already has.

## Unit kinds that do NOT apply here

\`build\`, \`match\` and \`tune\` are circuit machinery — a schematic editor, a
symbol drill over electronic components, and three analogue circuit models. They will
fail the build in a computing course. \`sandbox\` has sixteen registered visualisers
and only two are relevant to computing (\`pipeline\` and \`cache\`); use one only if
your module is genuinely about CPU pipelining or cache behaviour, and otherwise skip
the kind entirely.

## Correctness

Every claim must be true and every number must be right, including each intermediate
step of every trace. RUN THE CODE. A trace with a slip in it is worse than no trace:
it is followed line by line by someone who cannot yet tell it is wrong. Where you
state what an error message says, produce it. Where you state a complexity, be able
to defend the constant as well as the order.

## Voice

Read the existing modules of this course first and match them. This catalog reads as
a knowledgeable person explaining something to someone capable. Not marketing, not a
textbook reciting, not enthusiasm standing in for content.

## Verify, from ${ROOT}

    python -X utf8 tools/emit.py catalog/authors/${c.id}.py
    python -X utf8 tools/verify_derivations.py catalog/${c.id}.json
    python -X utf8 tools/verify_labs.py catalog/${c.id}.json

All must be clean. Re-emitting is REQUIRED: a correction made at source and never
emitted reaches nobody, and that has already happened in this repo. Do NOT run
\`emit.py --all\` or \`node build.mjs\`.

Report: units added by kind, the word count of each reading unit, the ladder easiest
to hardest with answers, and the final line of each gate.
`

const WROTE = {
  type: 'object', additionalProperties: false,
  required: ['course', 'module', 'unitsAfter', 'readWords', 'added', 'gatesClean', 'notes'],
  properties: {
    course: { type: 'string' }, module: { type: 'integer' },
    unitsAfter: { type: 'integer' }, readWords: { type: 'string' },
    added: { type: 'string' }, gatesClean: { type: 'boolean' }, notes: { type: 'string' },
  },
}

phase('Write')
const perCourse = await parallel(COURSES.map((c) => async () => {
  const done = []
  for (let n = 1; n <= c.modules; n++) {
    const r = await agent(BRIEF(c, n), { label: `${c.id}/M${n}`, phase: 'Write', schema: WROTE })
    if (r) {
      done.push(r)
      log(`${c.id} M${n}: ${r.unitsAfter} units, reading ${r.readWords}` +
        (r.gatesClean ? '' : '  [GATES NOT CLEAN]'))
    } else log(`${c.id} M${n}: produced nothing`)
  }
  return { course: c.id, modules: done }
}))

const wrote = perCourse.filter(Boolean)

phase('Audit')
const audited = await parallel(wrote.map((w) => () =>
  agent(`You are fact-checking newly written computing teaching content. Be
adversarial: find what is WRONG.

REPO: ${ROOT}
COURSE: ${w.course}

Every module of this course has just been rewritten to open with a long explanation
and carry a ladder of problems. The authors' accounts:

${w.modules.map((m) => `M${m.module} (${m.unitsAfter} units, reading ${m.readWords}): ${m.notes}`).join('\n\n').slice(0, 40000)}

Read catalog/${w.course}.json. RUN THE CODE — do not reason about what a listing
does when you can execute it. Work every answer out before looking at the key.

Hunt for:
  * a trace in a reading unit whose intermediate state is wrong, or whose final
    result contradicts a question elsewhere in the module
  * code in a reading unit or a listing that would not actually run
  * a quiz option marked correct that is not, or two defensible correct answers
  * a fill-in whose key would not work in that listing, or where another offered
    option works equally well, or whose explanation describes a wrong ANSWER when
    substituting it actually produces a syntax error
  * a stated error message that is not the one Python, SQL or the shell produces
  * a complexity, a count or a rate that is simply miscalculated
  * a numeric tolerance loose enough that a wrong method passes
  * a claim about a language, a protocol or a system that is false
  * a stated limit ("this stops working when...") that is wrong about where it stops

Report ONLY defects of fact, with the exact module and unit and the evidence you ran.
Not style, not difficulty, not coverage. An empty list is a fine answer.`,
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
return { wrote: wrote.map((w) => ({ course: w.course, modules: w.modules.length })), defects }
