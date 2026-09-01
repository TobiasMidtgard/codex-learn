# Codex Learn — platform optimisation and curriculum completion

Date: 2026-09-01. Status: approved for implementation (autonomous session; the
brief was "review and optimise for function, form, size and speed, improve the
webpage as much as you can, and make the courses a fleshed-out five-year degree
that actually prepares you for a master's").

Specs live under `design/superpowers/` rather than `docs/`, because `docs/` is
what GitHub Pages publishes.

## What was found

Measured on the current build (`node build.mjs --check`, and the split shell
served locally and opened in Chrome):

| Measurement | Value |
|---|---|
| Split shell (`index.html`) | 1300 KB, parsed before first paint |
| Block comments in that shell | ~280 KB (circuit.js is 45 % comment by bytes) |
| Payloads fetched **before the first screen paints** | 62 files, 13 146 KB |
| JS heap after boot | 72 MB |
| CS courses with any reading unit | 1 of 32 (CS101) |
| CS courses that are labs only (no quiz, no reading) | 13 |
| EE courses in bands 2–5 with reading units | 2 of 24, and those hold one each |

The first two are size and speed. The last three are the reason the CS degree
does not yet read as a degree: a module goes from a bullet list of concepts
straight to a lab or a quiz, which examines a subject rather than teaching it.
The EE first year shows what the platform can hold — 45 000 to 55 000 words of
explanation per course — and the rest of the catalogue is not at that standard.

## Decisions

### 1. Load a course when it is opened, not all of them at boot

The build emits one small **catalog index** (`programs/catalog.<hash>.json`)
holding every course with its units reduced to metadata — title, minutes, type,
and the counts the course page prints (checks, questions, blanks, steps …) —
plus the per-course full payloads it already emits. The shell fetches the index
at boot, builds `LESSON_INDEX` from it, and fetches a course's full payload the
first time a route needs its content (a lesson view, or the runner). Opening a
course page prefetches its payload in the background.

Why this and not a service worker or bigger caches: the payloads are hashed and
already cache well; the defect is the 13 MB that stands between a learner and
the first screen. An index is about 3 % of that.

Constraints the change must keep, each of which has been broken here before:

- lesson ids are progress keys and do not change;
- `recomputeXp` must never persist a deflated figure — with the index loaded
  every unit's type is known, so the `MISSING_PROGRAMS` guard keeps its meaning
  for "the index did not arrive";
- a payload that fails to fetch fails one course's content with a retry, not the
  degree;
- the inlined `codewright.html` still fetches nothing.

### 2. Strip comments and indentation from the shipped scripts and styles

A dependency-free tokenizer in `build.mjs` removes comments and leading
indentation from the JS and CSS that ship, leaving strings, template literals
and regular expressions untouched. Source files stay exactly as they are — the
comments are the repository's memory and are worth keeping. A new gate,
`tools/verify_minify.mjs`, checks that the stripped output has the same token
stream as the source and still passes `node --check`; the build refuses to ship
a stripped script that fails either.

### 3. Load the circuit editor and the sketch interpreter on demand

`src/circuit.js` and `src/mcu.js` are used by the build, numeric-diagram, match
and playground screens and nowhere else; app.js reaches them through
`createCircuit` and `Schematic` only. In the split shape they become
`lib/circuit.<hash>.js`, loaded by an `ensureCircuit()` awaited by those
renderers. The inlined shape keeps them inline. This was named in build.mjs as
"the honest lever" the next time the shell budget was hit.

### 4. Page improvements

- **Study plan**: the right column gains the selected subject's outcomes and
  module list, so choosing a subject answers "what will I learn" without leaving
  the page; the year's theme sentence appears under the year tabs.
- **Search** becomes a results list (up to 8 hits, type chips, arrow keys,
  Enter opens) instead of opening the top hit blind.
- **Light theme**: `color:var(--lime)` used as ink is 3.4–4.1:1 on the light
  ground; those rules move to `--accent-ink` (5.3:1). Fills keep `--lime`.
- **Fonts** load without blocking render (`preload` + swap).

### 5. Curriculum

**Every module of every CS course gets a reading unit** of 1200–2500 words,
written to the Senior Educator brief in `GAUNTLET_CURRICULUM.md`: a concrete
picture before formalism, the formula derived rather than announced, one worked
example carried through with real numbers, the mistake people actually make and
why it tempts, and where the idea stops holding. Fenced Python in a reading is
runnable (standard library only) and is executed by a new gate,
`tools/verify_reads.py`. The thirteen lab-only CS courses also gain a quiz per
module, with a per-option explanation on every question.

Then the same for the EE courses in bands 2–5, budget permitting, CS first.

**Four new CS courses**, each authored to the same schema as the existing
ones (3–5 modules, a checked lab per module, quizzes, a capstone with a rubric
that sums to 100 and at least four checks), chosen because a master's admissions
committee expects them and the catalogue lacks them:

| Id | Year | Title | Why |
|---|---|---|---|
| MA211 | 2 | Numerical Methods & Scientific Computing | floating point, roots, linear systems, quadrature, ODE solvers — assumed by every graduate systems, ML and graphics course |
| MA301 | 3 | Optimisation | convexity, gradient and Newton methods, KKT, LP and duality, discrete search — the mathematics ML401 and ROB520 stand on |
| CS411 | 4 | Information Theory & Coding | entropy, source coding, capacity, error-correcting codes — the vocabulary of ML, networks and compression at graduate level |
| CS451 | 5 | Research Methods & Experimental Computer Science | reading papers, designing experiments, statistics for benchmarks, reproducibility — what a master's thesis actually requires |

Ids are new, so no existing progress key moves. Each course is added to
`catalog/_spine.json` with prerequisites inside the existing graph.

## What is deliberately not done

- No dependency is added. Minification is hand-written for that reason.
- No service worker: it would add an update path the version check already
  covers, and offline use is what `codewright.html` is for.
- Existing lesson ids, lab files and tests are not edited by the content work;
  readings and quizzes are added beside them. The derivation, tune and circuit
  gates therefore keep their exact counts.
- No author writes `derive` units: the symbolic gate is exacting and a wrong
  answer key there costs a learner more than a missing derivation.

## Verification

Every gate in `GAUNTLET_CURRICULUM.md` is run before and after, and the
pre-existing numbers must not move except by exactly what was added. The two new
gates (`verify_minify`, `verify_reads`) join the list. The split shell is opened
in a real browser and the boot payload measured again.
