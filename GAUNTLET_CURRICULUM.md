# Codex Learn — Adversarial Gauntlet

An autonomous enhancement pipeline. Each cycle targets one track, audits it through
four adversarial lenses, patches, **verifies against the repository's own gates**, and
appends to `GAUNTLET_LOG.md`.

---

## The four personas

Audit the target through all four. Write the attacks down in the log, not just the
fixes — a defect you decided not to fix is worth recording so the next cycle does not
rediscover it.

**1. The Senior Educator.** Is the idea explained from a concrete picture before any
formalism? Is the formula derived or merely announced? Is there a worked example
carried all the way through with real numbers, not just a result? Does the text name
the mistake people actually make and say why it is tempting? Does it say where the
idea stops holding? Vague, hand-waving prose is the defect; "clearly", "simply" and
"just" are its usual tells.

**2. The Assessment Inquisitor.** Does the question test understanding or recall? Are
all four options defensible enough that a confused learner would pick one? Is every
distractor a real misconception rather than an obviously wrong number? Does the `why`
explain the correct answer **and** why the tempting wrong one is wrong — and is it
written to be read whichever option was picked, because it is?

**3. The Simulation Auditor.** Feed the model zero, negative, enormous and identical
values. Resize the window mid-interaction. Click faster than it can re-solve. Does a
sandbox's `notice` describe behaviour the visualiser **actually draws** — check the
draw loop, do not assume. Does a stated answer match what the solver returns for the
schematic on the page?

**4. The UX & Accessibility Hardener.** Tab order, focus restoration, `aria-live` on
anything that updates, contrast in **both** themes, layout at 375px, `prefers-reduced-
motion`. Every colour from a token: a hard-coded hex is a light-theme bug waiting.

---

## Tracks

| # | Track | Where it lives |
|---|---|---|
| 1 | Content & conceptual depth | `catalog/authors/*.py` — `read`, `derive` units |
| 2 | Interactive models & visualisers | `src/studio.js` (sandboxes, tune), `src/circuit.js` |
| 3 | Question bank & quizzes | `catalog/authors/*.py` — `quiz`, `blanks`, `numeric`, `match` |
| 4 | Subject breadth & progression | `catalog/authors/*.py` modules, `catalog/_spine*.json` |
| 5 | UI, layout & aesthetics | `src/index.head.html`, `src/app.js` |
| 6 | Edge cases, resilience, a11y | `src/app.js`, `src/desk.js`, `src/circuit.js` |

---

## Verification — this is not optional, and it is not "no console errors"

This repository has real gates. A cycle that does not run the ones touching its track
has not verified anything. Run from the repo root:

```
python -X utf8 tools/emit.py catalog/authors/<ID>.py   # schema; REQUIRED after any author edit
python -X utf8 tools/verify_labs.py catalog/<ID>.json  # every reference solution passes, every starter fails
python -X utf8 tools/verify_derivations.py             # every derivation step, symbolically, against SymPy
node tools/verify_circuits.mjs                         # every build exercise's reference satisfies its own checks
node tools/verify_tune.mjs                             # every tune target reachable and not already met
node tools/verify_numeric.mjs                          # every circuit answer against the MNA solver
node build.mjs                                         # duplicate ids, size budgets, registry guards, staleness
```

**Baseline first.** Capture the gate numbers *before* editing. A number that moves is a
regression in existing content, not a new feature. At the time of writing: 80 circuit
exercises / 340 checks, 21 tune units, 1091 derivation steps, every numeric answer
verified with none unchecked.

---

## Invariants that have already been broken here

These are not style preferences. Each one shipped a real defect.

- **Re-emit after editing an author file.** `catalog/<ID>.json` is what the app serves.
  A fix made at source and never emitted reaches nobody — three EE131 defects sat in
  the artifact for weeks reading correctly at source. `build.mjs` now refuses to build
  when an author file is newer than its JSON.
- **Never run `emit.py --all` or `node build.mjs` while another cycle may be writing.**
  Both read the whole catalog.
- **Lesson ids are progress.** The first unit of a kind keeps its unsuffixed id
  (`-QZ`, and the bare `-M3` for a lab). Changing one orphans completed work.
- **A gate that skips what it did not expect is worse than no gate.** Every unit key
  holds a *list*. Iterate; do not read `m.quiz` and stop.
- **Fixing the line you were pointed at is not fixing the defect.** Three review rounds
  found the same false claim surviving in a concepts bullet three lines above the
  sentence just repaired. EE121 alone had six. Sweep the whole module.
- **A correction can invert what it was written to fix.** One rewrote "inversely
  proportional" as "proportional", one paragraph from numbers that contradicted it.
  Re-read the corrected sentence against the numbers beside it.
- **A schematic `numeric` unit needs a `check`** — one line of JS run against the app's
  own MNA solver. Without it the answer rests on arithmetic nobody re-did.
- **Reading units:** 400 words is the emitter's floor, 1200–2500 is the target.

---

## Cycle workflow

1. Read `GAUNTLET_LOG.md`. Do not redo completed work; the log records what was
   deliberately left alone as well as what was changed.
2. Pick the smallest target that still gives the cycle something real to do — one
   course, or one subsystem. A cycle that touches everything verifies nothing.
3. Capture the gate baseline.
4. Audit through all four personas and write the attacks down.
5. Patch.
6. Run every gate that touches the track. All must be clean, and the pre-existing
   numbers must not have moved.
7. Append to `GAUNTLET_LOG.md`: what was attacked, what changed, what was left and
   why, and the gate output.
