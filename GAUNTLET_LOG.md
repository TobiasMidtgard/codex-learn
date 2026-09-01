# Codex Learn — Gauntlet Execution Log

Seeded from the session that preceded the runner, so cycle 1 does not redo work that
is already done. Everything below is committed and gate-clean.

---

## Cycle 0 — prior session (seed)

### Machinery the tracks depend on

- **A module can hold more than one unit of a kind.** Every unit key was singular
  (`"quiz": norm_quiz(m.get("quiz"))`, nine times over), which capped a module at nine
  units and made a graduated ladder of problems unexpressible. Each key now holds a
  list; the first entry keeps its original id so no completed work is orphaned.
- **A `read` unit kind exists.** There was none: modules went from concept bullets
  straight to being examined, which tests whether you already knew. 400-word floor in
  the emitter, 1200–2500 target.
- **`verify_numeric.mjs`** — a new gate. A circuit answer was the only number in the
  catalog nothing checked. It now solves the schematic with the app's own MNA solver
  and compares. Caught, within minutes, a superposition question whose drawn circuit
  had both supplies live (6.50 V) against a stated answer for the killed-source case
  (2.50 V).
- **Staleness guard in `build.mjs`** — refuses to build when an author file is newer
  than its emitted JSON. Three EE131 defects had been corrected at source, never
  re-emitted, and shipped anyway.
- Module ceiling 5 → 14. Payloads chunked per course. Display equations fixed
  (`display:block` was replacing MathML layout, so every `$$…$$` fraction bar stretched
  the width of the column).

### TRACK 1 / 4 — content and breadth (done, do not redo)

- **EE spine, first and second year: complete.** EE101 (11 modules, 139 units),
  EE102, EE111, EE121, EE131, EE141, EE211 (124 each), EE231 (116, 9 of 10 modules).
  Every module 11–13 units, opening with 1200–2500-word readings.
- EE201, EE221, EE241 have full syllabi (10 modules) but **still need density**.
- MA111, MA121: modules 1–3 dense. **Modules 4–11 outstanding.**
- MA101, MA112, MA201: syllabi only (11 modules each). **All units outstanding.**
- CS side: 12 courses gained ~156 units (quiz, fill-in, reasoning per module) but are
  still at 4–5 modules — **breadth pass outstanding**.
- **Untouched entirely:** 18 graduate EE courses (CTRL/DSP/EMAG/PWR/RFIC/VLSI) and 27
  CS/elective courses still need a syllabus pass before density.

### TRACK 2 — interactive models (partly done)

- Circuit editor: viewport (zoom anchored on the cursor, pan by middle-drag or space),
  multi-selection (shift-click, rubber band, Ctrl+A), and **moving parts**, which was
  not previously possible at all.
- 14 new placeable kinds: SW, LDR, NTC, POT, LAMP, METER, BAR, and — behind a new
  Newton-Raphson loop — D, LED, NPN, PNP, NMOS, PMOS, OPAMP. Sensors have a live
  simulated-environment panel.
- **Outstanding:** subcircuit ICs (group a selection into a block with derived pins),
  breadboard (strip connectivity), programmable microcontroller.
- A notepad/calculator modal (`src/desk.js`, Alt+K) with an engineering-notation
  parser: `4k7 || 10k` → 3.20 k.

### Verification standard already in force

127 content defects were found and closed across seven review rounds. The pattern
worth carrying forward:

- Round 2 found **10 more, two of which the round-1 fixes had introduced**.
- Round 3 found **9 further echoes** of claims already corrected once — the same false
  statement surviving in a concepts bullet three lines above the repaired sentence.
- Two defects were in **app code, not content**, which is why three content review
  rounds walked past them.

**Gate baseline at seed time:** 80 circuit exercises / 340 checks · 21 tune units ·
1091 derivation steps across 45 courses · every numeric answer verified, none
unchecked · 62 courses, 366 modules.

---

## Cycle 1 — TRACK 1: Content & Conceptual Depth

**Target: MA111 (Calculus I), modules 4–9 — the differentiation core.** One course, one
contiguous block. Modules 4 through 9 each held a `quiz` and nothing else: the learner
met the product rule for the first time as a bulleted claim and was examined on it in the
next unit. Modules 1–3 open with 1400–1700-word readings, so the course was collapsing
into announcement at exactly the point where the rules arrive. That is the defect the
`read` kind was created for, and it had six consecutive instances.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 217 figure-only
1091 derivation steps across 45 courses (MA111: 54)
MA111: 5 labs · 47 units · 9 read units, 8 modules with none
build: 3 parts / 111 keys · 32+30 courses bundled · 13 visualisers ·
       3 tune models · 15 symbols · 62 payloads · inlined 13538 KB
```

### The attacks

**1. Senior Educator.** Six findings, four of them acted on.

- *Announced, never derived.* Six modules of rules with no derivation anywhere. Fixed:
  six readings, each deriving what it states — the power rule from the binomial theorem,
  the product rule from the rectangle whose corner square dies in the limit, the quotient
  rule solved out of the product rule rather than memorised, the chain rule with its
  proof's actual hole shown, the inverse rule as one line of chain rule applied to
  `f(f_inv(y)) = y`, Rolle from the extreme value theorem, the mean value theorem from
  Rolle by subtracting the chord, and the linearisation error from Taylor's remainder.
- **The power rule was asserted well outside the argument offered for it.** The M4
  concepts bullet said it "falls straight out of the binomial expansion of `(x + h)^n`" —
  a proof for whole-number `n` only — and the M4 quiz then applies it at `n = 1/2` and
  states it "works for any real exponent". The course was claiming a theorem for real
  exponents on the strength of an argument valid for integers, and nothing said so. Fixed
  in both places: the bullet now names the scope and where each remaining case comes
  from, and the reading and derivation prove the rational case by squaring `y = sqrt(x)`
  instead — a genuinely different argument that the binomial theorem cannot reach.
- **A circularity the quiz named and nothing resolved.** M6's quiz asks why
  `lim sin(h)/h = 1` must be proved geometrically, and answers that it is "settled first
  by squeezing `sin(h)` between two areas on the unit circle" — a squeeze that appeared
  nowhere in the course. Learners were examined on the existence of an argument they had
  never been shown. Fixed: the reading proves it, from the three nested areas through to
  the reciprocal-and-squeeze, and then makes the radian hypothesis explicit, because the
  sector area is `h/2` for radians and nothing else. In degrees the limit is `pi/180` and
  every derivative in the module changes by a factor of 57.3.
- **The inverse rule was stated unconditionally.** The hypothesis `f'` non-zero appeared
  only in the last sentence of one quiz explanation. Fixed in the bullet and worked in
  the reading: `x^3` at the origin, where the inverse exists and is continuous but has a
  vertical tangent, so it is differentiability that fails and not invertibility.
- **L'Hopital's rule was one-way and the course said so nowhere.** Added a bullet and a
  worked case: `(x + sin x)/x` tends to 1 as `x -> inf`, while the derivative quotient
  `(1 + cos x)/1` oscillates in `[0,2]` forever. A failed application is a reason to try
  something else, never a conclusion.
- *Left alone:* M7's "substitute the instantaneous values only after differentiating" was
  already stated with its reason attached. Nothing to repair; the reading now shows it
  producing `dV/dt = 0` rather than only warning about it.

**2. Assessment Inquisitor.** All 26 questions across M4–M9 were checked against the
mathematics, not skimmed. **Every key is correct and nothing was changed.** Every `why`
explains the correct answer and names why the tempting wrong one is tempting; none uses a
positional reference. The numeric claims inside the explanations were recomputed:
`sqrt(4.02)` high by `6.2e-6` (true `6.234e-6`), `1/1.02` off by `4e-4` (true `3.92e-4`),
`4*pi*25*2 = 200*pi`, `10e-6 * 3000 = 30 mA`, `f''(4) = -1/32`. All hold. Recording this
so the next cycle does not re-audit them.

**3. Simulation Auditor.** M4–M9 contain no sandbox, no schematic `numeric`, no `tune`
and no `build` unit, so there is no draw loop or solver in the target to attack; the
course's simulation surface is M1–M3 and the M10/M11 labs, all outside this block and all
still gate-clean. The persona was pointed at the thing in scope that no gate covers
instead: **arithmetic in prose and in derivation answers.** Every number written into the
six readings was computed independently in SymPy *before* it was written, and all 37 new
derivation answers were checked against SymPy for mathematical correctness, separately
from the gate. One reference solution changed as a result: the folium slope at
`(4/3, 2/3)` is `5/4`, and that point was confirmed to lie on the curve before being used.

**4. UX & Accessibility Hardener.** Content-side only, since Cycle 5 of the previous run
already hardened the reading surface. Checked what an author can still break at 375px:
display equations are safe because `math[display=block]` carries its own
`overflow-x:auto`, and tables are safe because `.article .tw` wraps them in a scroller —
verified in `src/index.head.html`, not assumed. No hard-coded colour, no raw HTML and no
wide table was introduced; every equation is `$$...$$` and inherits the token ramp.

### Found in my own work, and fixed

The M8 reading first attributed the extreme value theorem to "Module 2". Module 2 holds
the *intermediate* value theorem; the extreme value theorem is nowhere in modules 1–3.
Caught by extracting every `Module N` reference from the new prose and resolving each
against the actual module titles — 15 references, one wrong. It now states the theorem
plainly as continuity's other purchase on a closed interval and points forward to Module
11, which is where the course actually uses it.

### What changed

Twelve new units in six modules — one `read` and one `derive` each — plus three
`concepts` repairs.

| Module | Reading | Words | Derivation | Steps |
|---|---|---|---|---|
| M4 | Three rules, and the two lines behind each one | 1451 | The three rules, proved rather than quoted | 6 |
| M5 | One rate feeding another | 1218 | Peeling layers, and reading a slope backwards | 6 |
| M6 | Where these derivatives actually come from | 1426 | Sine from a squeeze, and the rest from inverses | 7 |
| M7 | Differentiating an equation nobody solved | 1272 | A curve that is not a graph, and a rate that follows | 6 |
| M8 | The theorem that lets a derivative speak about the function | 1427 | Rolle, tilted, and the numbers it produces | 6 |
| M9 | The tangent line as a stand-in, and how far it can be trusted | 1293 | The tangent line, the error it leaves, and a tolerance budget | 6 |

8087 new words, all inside the 1200–2500 target and in line with the existing nine
readings (1396–1737). Every reading carries a worked example through to a number, names
the mistake people make and says why it is tempting, and closes on where the idea stops
holding. MA111: 47 units → 59; 8 modules without a reading → 2.

Worked examples that end in checked numbers rather than results: `d/dx (x^2+1)/(x^3-x)`
at `x = 2` giving `-31/36`, confirmed against a central difference to seven figures;
`(2x^3-5)^4` at `x = 1` giving `-648` against a forward difference of `-646.70`, with the
0.2% gap identified as Module 3's first-order truncation error rather than waved at;
`x^x` at 2 giving `4(1+ln 2) = 6.7726` against `6.7793`; two resistors in parallel where
a `0.5 ohm/s` drift in one arrives as `0.236 ohm/s` in the combination, because the
sensitivity is the *square* of the divider ratio; and `sqrt(4.02)`, where the second-order
remainder predicts an error of `6.25e-6` before the true value is looked at and the actual
error is `6.234e-6`.

### Left alone, deliberately

- **M10 and M11 still have no reading.** Both carry a full lab (Newton-Raphson with
  guards; critical points and classification), so they teach by construction rather than
  examining cold — which is not the defect this cycle was chasing. They should get
  readings; that is a following cycle, not a widening of this one.
- **The question bank was not touched.** It audited clean, and it is Track 3's ground.
- **`verify_derivations.py` is weaker than the curriculum claims, and I did not change
  it.** Its checker computes `simplify(together(expr - expr))`, which is zero for every
  expression that parses. So it proves each answer *survives the app's own LaTeX-to-SymPy
  translation* — which is a real gate, and the one that catches a symbol missing from
  `vars`, a Python keyword as a name, a relation where an expression was needed, and
  LaTeX outside the supported subset, all of which ship a step nobody can pass. What it
  does **not** do is check that the answer is the right answer, so the curriculum's line
  "every derivation step, symbolically, against SymPy" overstates it. Two consequences
  worth carrying: a backslashed `\ln x` is silently stripped to ` x` by the translator and
  the gate would not notice, so function names must be written bare (`ln(x)`, `sin(x)`) —
  and every answer in this cycle was therefore both translation-inspected and
  truth-checked by hand. Fixing the gate, or the curriculum line, is its own cycle;
  rewriting the spec from inside a cycle it governs is the wrong move.
- **`docs/programs` lost eight older payload files.** That is `build.mjs` pruning its
  rolling generation window — every build after a content change advances a generation and
  ages the oldest one out — and not a regression. Verified rather than assumed: the current
  generation lists 62 entries covering 62 distinct courses, every one present on disk, with
  no orphaned file on disk outside the retained generations.

### Gates, after

Every pre-existing number unmoved. The only number that moved is the derivation-step
count, which rose by exactly the 37 steps added.

```
verify_derivations   All good: 1128 steps across 45 courses   (1091 + 37 new; MA111 54 -> 91)
verify_labs MA111    All good: 5 labs                          (M1 7/7, M3 7/7, M10 8/8, M11 9/9, CAP 13/13)
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 217 figure-only
emit.py MA111        ok — 11 modules, 4 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads · inlined 13618 KB
```

---
