# Platform optimisation and curriculum completion — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut what a browser parses and fetches before the first screen by an order of magnitude, polish the study plan, search and light theme, and give every module of the CS degree (then EE bands 2–5) a real reading, adding four courses a master's programme expects.

**Architecture:** The build (`build.mjs`) gains a catalog index shape and a comment/indentation stripper; `src/app.js` gains lazy per-course hydration and lazy loading of the circuit editor. Content is authored in `catalog/authors/<ID>.py` exactly as today and emitted by `tools/emit.py`; two new gates (`tools/verify_reads.py`, `tools/verify_minify.mjs`) join the existing ones.

**Tech Stack:** Node 22 (no dependencies), Python 3.14 (standard library), the repository's own gates.

Spec: `design/superpowers/specs/2026-09-01-platform-optimisation-and-curriculum-design.md`.

---

## Gate baseline (captured before any change)

```
verify_circuits     87 circuit exercises, 369 checks · 593 labels
verify_tune         21 tune units
verify_numeric      216 answers verified, 0 schematics with no check, 218 figure-only
verify_derivations  1294 steps across 46 courses
build --check       32/32 + 30/30 · shell 1300 KB · 62 payloads 13146 KB · inlined 14474 KB
```

---

### Task 1: `tools/verify_reads.py` — every fenced Python example in a reading runs

**Files:** Create `tools/verify_reads.py`.

- [ ] For every `catalog/<ID>.json` given (or all), walk `modules[].read[]` (a key holds a dict or a list — iterate with the same `asList` rule as everything else), pull every fenced `python` block out of `body`, and execute it with `exec` in a fresh globals dict with stdout captured and a time limit. Reject imports outside the Pyodide standard library, reusing the module list `verify_labs.py` already has.
- [ ] A fence whose first line is a comment containing `raises` (e.g. `# raises NameError`) is expected to raise; it fails the gate if it does NOT raise.
- [ ] Report per course: `[ok  ] CS201  14 examples` / `[FAIL] CS201/M2/read1 block 3: NameError …`, exit 1 on any failure. Also count words per reading and fail below 400 (emit.py already does; this re-checks the artifact).
- [ ] Run on `catalog/CS101.json` and on every EE band-1 course to prove it passes existing content; fix the tool, not the content, if it does not.

### Task 2: the spine gains four courses

**Files:** Modify `catalog/_spine.json`.

- [ ] Insert, in year order:
  - `MA211` year 2, "Numerical Methods & Scientific Computing", Intermediate, prereqs `["MA112","MA121","CS101"]`, stack `["Python"]`, credits 10, hours 130, icon `≈`
  - `MA301` year 3, "Optimisation", Advanced, prereqs `["MA121","MA112","CS201"]`, stack `["Python"]`, credits 10, hours 130, icon `∇`
  - `CS411` year 4, "Information Theory & Coding", Advanced, prereqs `["MA201","CS301"]`, stack `["Python"]`, credits 10, hours 140, icon `⊕`
  - `CS451` year 5, "Research Methods & Experimental Computer Science", Advanced, prereqs `["MA201","SE201","CS301"]`, stack `["Python"]`, credits 10, hours 120, icon `⌕`
- [ ] `node build.mjs --check` must report `cs-degree: 4 course(s) not yet authored -> MA211, MA301, CS411, CS451` and otherwise pass.

### Task 3: content agents — readings (and quizzes) for the CS degree

One subagent per course, run in parallel waves of eight. Each agent receives the brief below verbatim plus its course id. Courses: CS102, CS201, CS210, CS220, CS301, CS310, CS320, CS330, CS401, SE201, WEB301, CE101, CE201, ML401, HPC401, GFX401, ELEC410, ELEC420, ELEC430, DL501, FM501, ETH501, QC510, ROB520, SEC301, CAP501, MA101, MA112, MA201.

**Agent brief (verbatim):**

> You are adding teaching text to one course of Codex Learn, a learning platform whose courses are authored as Python modules in `catalog/authors/<ID>.py` (a single dict `COURSE`) and emitted to `catalog/<ID>.json` by `python -X utf8 tools/emit.py catalog/authors/<ID>.py`. Your course is `<ID>`. Work only in that one author file. Do not run `emit.py --all`, `node build.mjs`, or edit any other file under `catalog/` or `src/`.
>
> **Read first**: `GAUNTLET_CURRICULUM.md` (the four personas; you are the Senior Educator and the Assessment Inquisitor), the first module of `catalog/authors/CS101.py` (the house voice for a `read` unit and the exact `"read": [{"title","minutes","body": r'''…'''}]` shape), the `quiz` in module 1 of `catalog/authors/CS201.py` (the shape with `whys`), and then your whole author file, including every lab brief and test, so that what you write teaches exactly what the labs then check.
>
> **What to add**: for EVERY module, a `read` list with one reading unit of 1200–2500 words (two units if the module's concepts genuinely need it). If the module has no `quiz`, add one quiz of 5–6 questions. Put `read` before `quiz` in the module dict, before any existing keys, so the learner meets it first. Do not touch any existing unit, lab, test, id or the capstone. Do not add `derive`, `numeric`, `tune`, `build` or `match` units.
>
> **How a reading must be written** (each of these is checked by a reviewer):
> 1. Open with a concrete picture or a real situation, before any definition.
> 2. Derive every formula or rule from that picture; never announce one.
> 3. Carry at least one worked example all the way through with real numbers or a real trace, not just a result.
> 4. Name the mistake people actually make, and say why it is tempting.
> 5. Say where the idea stops holding.
> 6. Tie it to the lab in that module by name, so the reader knows what they are about to build.
> 7. No "clearly", "simply", "just", "obviously". No bullet-list summaries in place of explanation. Headings with `##`, prose in paragraphs, code in fenced blocks.
> 8. Every fenced `python` block must run on its own under CPython with the standard library only (no numpy, pandas, pytest), deterministically (seed every RNG), and print what the prose says it prints. A block that is meant to raise starts with a comment `# raises <ExceptionName>`. Other languages (`text`, `sql`, `c`, `js`, `html`, `verilog`) are fine for illustration and are not executed.
> 9. Maths is LaTeX in `$…$` / `$$…$$` (fractions, scripts, radicals, Greek, `\text`, matrices). Use `r'''…'''` for the body (never `r"""…"""` — code samples contain docstrings). Code inside the block starts at column 0.
>
> **How a quiz must be written**: 4 options each, one correct (`"a"` is its 0-based index), every distractor a real misconception a confused learner would hold, options of similar length and register (a longest-option strategy must not beat guessing), a `why` addressed to whoever answered, and `whys` with one sentence per option explaining what the person who picked it was thinking and why it fails. Never refer to an option by position ("option B", "the first choice"); options are shuffled per learner. Questions test understanding, not recall of a sentence in the reading.
>
> **Verify before you finish** (all three must pass, and paste their last lines in your report):
> ```
> python -X utf8 tools/emit.py catalog/authors/<ID>.py
> python -X utf8 tools/verify_reads.py catalog/<ID>.json
> node tools/verify_quiz.mjs
> ```
> If `verify_quiz.mjs` reports your course's longest-option score got worse than its budget entry in `tools/quiz_budget.json`, rebalance the option lengths; do not edit the budget file.
>
> **Report**: the module titles and reading titles you added, word counts, the quiz counts, and the three gate outputs. Nothing else.

- [ ] Wave 1: CS102, CS201, CS210, CS220, CS301, CS310, CS320, CS330.
- [ ] Wave 2: CS401, SE201, WEB301, CE101, CE201, ML401, HPC401, GFX401.
- [ ] Wave 3: ELEC410, ELEC420, ELEC430, DL501, FM501, ETH501, QC510, ROB520.
- [ ] Wave 4: SEC301, CAP501, MA101, MA112, MA201, plus the four new courses (Task 4).
- [ ] After each wave: `python -X utf8 tools/emit.py --all` must be a no-op for untouched courses (it is a drift detector), and `node build.mjs --check` passes.

### Task 4: content agents — four new courses

Same rules as Task 3, plus the course must be complete: 4–5 modules, each with `read`, `quiz`, `blanks` (use `catalog/authors/CS201.py` module 1 as the shape) and a `lab` with 6–10 tests; a capstone with ≥3 deliverables, a rubric of 3–5 rows summing to 100, ≥4 tests, and a solution that passes them. Before finishing: `python -X utf8 tools/verify_labs.py catalog/<ID>.json` must report every solution passing and every starter failing at least one check. Syllabi are in the spec. Ids: MA211, MA301, CS411, CS451.

### Task 5: catalog index and lazy hydration

**Files:** Modify `build.mjs`, `src/app.js`; create `tools/skeleton.mjs`, `tools/verify_lazy.mjs`.

- [ ] `tools/skeleton.mjs`: export `skeletonOf(course)` — a deep copy with every unit reduced to `{title, minutes, n: {tests, checks, questions, items, blanks, steps, constraints, given}}` (only keys that apply), labs to `{title, minutes, runtime, n:{tests}}`, capstone to `{title, minutes, runtime, n:{tests, deliverables}}`, module `title/summary/concepts` kept, course metadata kept, and `skeleton: true`.
- [ ] `build.mjs`: emit `programs/catalog.<hash>.json` = `{programs, courses:[skeletons]}`. `DEGREE_CHUNKS` in the shell becomes `{index: url, courses: {ID: url}}`. Keep the per-course payload files exactly as they are. `pruneChunks` keeps the index files too.
- [ ] `src/app.js`: hoist `UNIT_SPEC` to module level; `buildDegreeIndex` copies `u.n` onto each lesson as `l.n` and creates the capstone lesson when `cap.tests.length || (cap.n && cap.n.tests)`. `unitMeta` and `checksPassed` read `l.n` when `l.tests` is absent. New `hydrateCourse(id)` (memoised promise): fetches the course payload, and for each module/unit/lab/capstone `Object.assign`s the mapped fields onto the existing lesson objects (same ids), replaces `c.modules`/`c.capstone`, sets `c.skeleton = false`. `go(r)`: if the route is a lesson (or the runner's focus lesson) on a skeleton course, paint a "Loading <course>…" panel, await hydration, and re-enter `go(r)` unless a newer `go` has run since (sequence counter); on failure paint an error with a Try again button. `renderCourse` prefetches. `loadDegreeChunks` fetches the index only; inlined builds skip all of this because `DEGREE_CHUNK_LIST.index` is absent.
- [ ] `tools/verify_lazy.mjs`: stage app.js through `tools/app_stage.mjs` with a skeleton catalog built by `skeletonOf`, assert every lesson id present in the full index is present in the skeleton index with the same type and `n` counts, hydrate one course with a stubbed `fetch`, and assert the lesson objects are the same identities and now carry `files`/`tests`/`mdText`.
- [ ] Run every gate; open the split shell in Chrome and record boot bytes.

### Task 6: strip comments and indentation at build time

**Files:** Create `tools/minify.mjs` (exported `stripJs(src)` and `stripCss(src)`), `tools/verify_minify.mjs`; modify `build.mjs`.

- [ ] `stripJs`: single pass over the source tracking state: code, line comment, block comment, `'`/`"` string, template literal (with a stack for `${…}` nesting), regex literal (decided by the last significant token: regex after `( , = : [ ! & | ? { } ; + - * % < > ~ ^` or after the keywords `return typeof instanceof in of new delete void throw case do else yield await`, division otherwise; `)` and `]` and identifiers/numbers mean division). Drops comments, drops leading whitespace on each line, collapses runs of blank lines, keeps every newline otherwise (ASI-safe).
- [ ] `stripCss`: drops `/* … */` outside strings and leading whitespace.
- [ ] `verify_minify.mjs`: for each `src/*.js` and the style block of `src/index.head.html`: tokenise the source and the stripped output with the same tokenizer and assert identical token streams ignoring comments/whitespace; `node --check` the stripped script; and stage the stripped app through `app_stage.mjs` to render the front page. Report the byte savings.
- [ ] `build.mjs`: apply to both shapes; add the savings line to the report.

### Task 7: the circuit editor loads on demand

**Files:** Modify `build.mjs`, `src/app.js`.

- [ ] Split shape: emit `lib/circuit.<hash>.js` = stripped `mcu.js + circuit.js`; the shell's script omits them. `DEGREE_CHUNKS.circuit = url`.
- [ ] `src/app.js`: `ensureCircuit()` returns a resolved promise when `typeof createCircuit === 'function'`, otherwise injects the script once and resolves on load. Awaited (through the same loading panel as hydration) before `renderBuild`, `renderNumeric` with a diagram, `renderMatch`, and the playground's circuit mode.
- [ ] Every gate that stages circuit.js keeps loading it from `src/`; unaffected.

### Task 8: page improvements

**Files:** Modify `src/app.js`, `src/index.head.html`.

- [ ] Study plan right column: after the summary, "What you will be able to do" (up to 5 outcomes) and "Modules" (numbered titles with unit counts). Under the year tabs: the band's `theme` sentence.
- [ ] Search: a `#omni-list` listbox under the input, rendered on input with up to 8 hits (courses first, then lessons with their type chip and course id), ArrowUp/Down + Enter, Escape closes, click opens; `aria-activedescendant`. Enter with no list open keeps today's behaviour.
- [ ] Light theme ink: change the `color:var(--lime)` rules that colour text (not fills, not `accent-color`) to `color:var(--accent-ink)`; run `node tools/verify_theme.mjs` and update its budget only if the change *improves* a surface.
- [ ] Fonts: `<link rel="preload" as="style" …>` + `<link rel="stylesheet" media="print" onload="this.media='all'">` with a `<noscript>` fallback.

### Task 9: EE bands 2–5 readings (budget permitting)

Same brief as Task 3 for EE201, EE202, EE221, EE241, CTRL510, CTRL520, CTRL530, DSP510, DSP520, DSP530, EMAG510, EMAG520, EMAG530, PWR510, PWR520, PWR530, RFIC510, RFIC520, RFIC530, VLSI510, VLSI520, VLSI530.

### Task 10: finish

- [ ] `python -X utf8 tools/emit.py --all`, every gate, `node build.mjs`, Chrome check of the split shell (boot bytes, a lesson opening, a circuit build unit opening, light theme).
- [ ] README: verification table and the build shapes; `GAUNTLET_CURRICULUM.md`: the two new gates and the new baseline numbers.
- [ ] Commit in slices: build/loader, minify, circuit-on-demand, page, content per wave, new courses, docs.
