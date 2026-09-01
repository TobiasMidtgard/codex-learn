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

## Cycle 2 — TRACK 2: Interactive Models & Visualisers

**Target: the Sandbox subsystem in `src/studio.js` — the mount framework, its 13
visualisers and 3 tune models, plus every catalog `notice` a code fix falsified.** One
subsystem, chosen over the circuit editor because the persona brief for this track is
almost entirely a description of what a sandbox does: extremes, resize, rapid input, and
"does a sandbox's `notice` describe behaviour the visualiser **actually draws**". 113
sandbox units across 13 visualisers depend on this file, and nothing anywhere checked it —
a sandbox is the one unit kind with no answer to grade, which is exactly why it had no
gate.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 217 figure-only
1128 derivation steps across 45 courses
build: 3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
       3 tune models · 15 symbols · 62 payloads · inlined 13618 KB
```

### The attacks

**3. Simulation Auditor** — taken first, because this is its track.

- **A "centre" was drawn as an outward spiral, and the readout underneath called it a
  centre.** `phase-portrait` integrated with forward Euler at `dt = 0.012`. The Euler map
  is `I + A·dt`, whose determinant at trace zero is `1 + det·dt²`, so the enclosed area is
  multiplied by that once per step and by `(1 + det·dt²)^1400` over the run. Measured: the
  unit centre grows **22.3%**, and at the top of the sliders (`a12 = 3, a21 = -6`) it grows
  by a factor of **37** — the rings leave the frame entirely. RK4 over the identical run
  holds the same quantity to `3e-5 %`. The catalog had already noticed and could not agree
  with itself: four notices apologise for the creep ("about a tenth of their radius … the
  forward-Euler step in the drawing code"), while eight others assert the orbits close
  ("closed orbits — energy never leaves", "every trajectory closes on itself at a fixed
  distance", "rings that circle forever"). Both sets described the same drawing.
- **A caption told the learner they were at the floor while the marker beside it read
  100%.** `cache`'s `explain()` re-derived its claims from the slider positions instead of
  from the simulation `draw()` had just run. At 4 KB with a 512-byte stride it printed "the
  compulsory miss on first touch — the floor no cache can go below" over a measured miss
  rate of 100%: 64 addresses land on 8 sets of a 64-set direct-mapped cache, so every
  access in passes 2 and 3 evicts the line it will want next. Its other branch claimed a
  conflict was unfixable "no matter how big it gets", which is false the moment `sets`
  exceeds the stride in lines.
- **"Below the Nyquist limit … nothing is lost", drawn over samples that are all zero.**
  `spectrum` tested `|fa − fsig| < 0.5`, which is satisfied *at* `f = fs/2` as well as
  below it. At `fsig = 100, fs = 200` — reachable, and the sliders reach several such
  pairs — every sample is `sin(πn)`, largest magnitude `5.4e-15`. The picture draws the
  entire sampled sequence lying on the axis under a sentence saying the samples determine
  the wave uniquely. The strict inequality is the whole theorem.
- **Four axes silently truncated what they were drawing.** `pole-step`'s s-plane was fixed
  at ±14 while the poles reach −34.2 at `ζ = 1.6, ωₙ = 12`, so the overdamped case — whose
  entire point is where the second pole went — showed one pole. `bode`'s magnitude axis
  stopped at 40 dB against a 46 dB peak at `K = 20, ζ = 0.05`. The `rlc` tune plot capped
  at 6 against a peak of 1414 at `R = 1 Ω, L = 200 mH, C = 0.1 µF`, so a Q of 1400 was
  indistinguishable from a flat response. The `rc-lowpass` plot ran 10 Hz–1 MHz while its
  corner ranges 1.59 Hz–1.59 MHz, putting the marker off *both* ends.
- **The stride slider froze the tab.** `cache`'s memo keyed on `(associativity, stride)`,
  so dragging the *stride* — step 1 across 1..512 — missed every time and re-simulated four
  full 64-point sweeps per frame: **627 ms at stride 1**, 317 ms at 2, 164 ms at 4. The
  slider redrew about once a second, and EE241/M2's brief asks the learner to step the
  stride through 8, 16, 32 and 64.
- **`explain()` printed the word "Infinity" at the setting a lesson sends learners to.**
  Found by the new gate, not by hand. `pole-step` computes settling time as `4/(ζωₙ)`, and
  CTRL510/M2's first notice bullet is "Take ζ to zero." Reachable: `ζ` has `min: 0`.
- **A broken LCG, currently harmless.** `kalman`'s `seed * 1103515245` reaches `2.4e18`,
  past `2^53`, so 299 of 300 products lost their low bits: period **10466** rather than
  `2^31`, and bit 0 came up set **422 times in 100000** draws. The visible output is fine
  today — the 240 values it draws are distinct and pass as Gaussian, mean 0.024, sd 0.98 —
  so this is recorded as luck rather than design, and fixed with `Math.imul`.
- **Checked and found correct, recorded so the next cycle does not re-derive them:**
  `kalman`'s steady-state gain `(√(ρ²+4ρ) − ρ)/2` really does equal `P/(P+R)` for
  `P = (Q + √(Q²+4QR))/2` — verified symbolically and numerically. `smith`'s reflection
  coefficient and its `−4πℓ/λ` rotation are both right. `pipeline`'s `N + 4 + stalls` agrees
  with the schedule its draw loop builds. `spectrum`'s alias folding is right everywhere
  except the boundary above. EE131/M6's and EE241/M2's cache notices — nine numeric claims
  between them — were recomputed against the model and all nine hold.

**4. UX & Accessibility Hardener.**

- **Every accent colour on every canvas in the app failed or nearly failed contrast in the
  light theme.** `--editor` is deliberately dark in both themes, and `palette()` says so —
  it takes ink from `--on-editor*` "rather than the page's ink". It then took `accent`,
  `blue`, `purple` and `amber` from `--lime`/`--blue`/`--purple`/`--amber`, which the light
  theme re-tints *dark for a light ground*. Measured against `#12151A`: lime 15.79 → **4.47**,
  amber 12.70 → **3.09**, blue 7.31 → **3.06**, purple 7.23 → **2.96**, the last under WCAG
  1.4.11's 3:1 floor for a meaningful graphical object — and purple is the Nyquist line, the
  1/f corner, the constant-VSWR circle and the sliding surface. The discipline existed and
  had been applied to four of the nine colours.
- **The readout changed in silence.** `.sbx-read` carries the entire pedagogical payload of
  a sandbox — the sentence saying what the picture now means — with no live region.
- **The sliders announced numbers the page does not show.** A range input reports its own
  raw value: "1" where the label reads *direct*, "0" where it reads *no*.
- **An opening state the slider could not reach.** `noise-corner.fc` ran 1 Hz–100 kHz with
  `step: 100` from `min: 1`, so the reachable set was 1, 101, 201 … — the whole of 1–100 Hz,
  which is the region a chopper amplifier exists for, was a single notch, and 999 of 1000
  positions sat above 101 Hz. RFIC520 M1 and M2 open at 100 Hz and 20 kHz, neither of which
  is on that grid: the thumb snapped to a different value than the draw and the readout
  used, and the opening state could not be returned to. EE221/M10's `1001` is the same
  defect wearing a workaround — the author picked 1001 because 1000 was unreachable.
- **`initial` was never sanitised.** `build.mjs` checks that an `initial` *key* names a real
  parameter and nothing checked the *value*. An out-of-range one leaves the input clamped to
  its own limit while draw, readout and explain all use the authored figure.
- **Checked and found sound, recorded rather than changed:** the `ResizeObserver` cannot
  loop, because `.sbx-canvas` has a fixed height and grid-determined width, so setting
  `cv.style.*` cannot resize the observed parent — verified in `index.head.html`, not
  assumed. The `Math.max(240, …)` floor in `paint()` never bites at 375px, where the stacked
  column is ~343px. Nothing in this subsystem animates on a timer, so `prefers-reduced-motion`
  has nothing to honour; the single `requestAnimationFrame` is a one-shot coalescer.

**1. Senior Educator** and **2. Assessment Inquisitor** had little ground here — a sandbox
has no prose beyond its brief and no graded question. Both were pointed at the thing in
scope they *can* judge: whether the readout explains or merely announces. Three now explain
where they announced. `cache` performs an actual three-C decomposition by running the trace
against an unbounded cache and a fully associative one and reporting all three terms, rather
than naming one from the slider positions. `noise-corner` said "the noise rises as 1/f" over
a plot in nV/√Hz whose drawn slope is 10 dB/decade — while EE221/M10's notice, on the same
screen, spells out that distinction and contradicted it. `phase-portrait` now names the
integrator artefact and puts the number on it instead of leaving the learner to decide
whether the creep is the physics.

### What changed

**Code — `src/studio.js`.**

| Fix | Before | After |
|---|---|---|
| `phase-portrait` integrator | Euler; centre area +22% to ×37 | RK4 default, Euler switchable; `3e-5 %` |
| `cache` model | address-by-address, 627 ms/repaint at stride 1 | run-collapsed, **13 ms**, bit-identical |
| `cache` caption | guessed from sliders; said "the floor" at 100% | measured 3-C split from the drawn trace |
| `spectrum` at `f = fs/2` | "nothing is lost" over all-zero samples | names the excluded boundary |
| `pole-step` s-plane | fixed ±14, poles to −34.2 | scales to the poles, ±14 floor |
| `pole-step` at `ζ = 0` | "settling in about Infinity s" | no settling time, and why |
| `bode` magnitude axis | fixed −80..40 dB, peak 46 | opens to hold the curve |
| `rlc` / `rc-lowpass` plots | marker and peak off-frame | axes hold both |
| `noise-corner` slider | linear, step 100 from 1 | logarithmic, 200 ticks per decade |
| `z-plane` at `θ = 0, r = 1` | "it oscillates forever" | `h[n] = 1`; a pure integrator |
| `switching` ZVS current | rose during the voltage swing | rises after the tank finishes it |
| `kalman` PRNG | period 10466, bit 0 dead | `Math.imul`, exact 32-bit |
| `kalman` RMS error | computed, hung on `ctx._err`, never read | drawn |
| `pipeline` bubbles | stalls shifted the row, drew nothing | bubbles drawn and counted |
| `pipeline` tint | baked `rgba(199,247,81,.22)` | `P.accent` at alpha |

**Framework — `mount()`.** `initial` clamped and type-checked; a `log` parameter kind
(slider carries a tick index, value exponentiated back at three significant figures);
`aria-live` on the readout with a change guard so a drag does not flood it; `role="img"`
and a label on the canvas; `aria-valuetext` carrying the formatted value; per-parameter DOM
lookups resolved once instead of twice per parameter per frame.

**Theme — `src/index.head.html`.** Four `--on-editor-{lime,blue,purple,amber}` tokens,
defined once so no theme overrides them, read by `palette()`. Light-theme contrast on the
canvas goes 4.47 → 14.68, 3.09 → 11.80, 3.06 → 6.79 and 2.96 → 6.72. Because
`circuit.js`'s `P()` delegates to `Sandbox.palette()`, this reaches every canvas in the
app — schematics, build exercises, the breadboard and the MCU views — not only sandboxes.

**A new gate — `tools/verify_sandbox.mjs`.** Loads the models as shipped, exactly as
`verify_tune.mjs` does, and paints them onto a recording canvas that objects to any
non-finite coordinate. It drives every visualiser over an extremes grid — each parameter at
min, max, default, zero, one notch in from each end, plus all-min, all-max and all-mid — at
three viewport sizes including the 820px breakpoint and the 240px floor, and rejects a
readout that throws, says nothing, or contains `NaN`/`undefined`/`Infinity`. It checks every
tune plot's marker lies inside its own axes and that the curve's peak does. And it checks
every catalog opening value is reachable: on the step grid for a linear parameter, and
surviving the round trip to a tick and back for a log one. **747 draws, 249 readouts, 364
opening values.** It found the `pole-step` Infinity, both `rc-lowpass` off-frame markers,
and — after I tightened its own log-parameter rule, which I had first written too leniently —
EE221/M10's unreachable 1001.

**Content — five courses re-emitted.** The three notices apologising for the Euler artefact
(EE141 M1 and M6, PWR520 M1) now describe rings that close and point at the switch. EE131's
module 9 sandbox, which *teaches* the artefact and measures it in its lab, opens with
`"solver": 0` and keeps its exhibit — it is the only unit in the catalogue that does, and it
now says so and invites the comparison. Four VLSI520 cache notices were already false, having
been written before the working set was changed from cache-proportional to a fixed 32 KB and
never revisited: "the curve does not move: a horizontal line at 100 per cent" (33.33% at
64 KB), "pins to 100 per cent at every size" (33.33%), "12.5 per cent, flat across the whole
size axis" (4.17%), "nothing on this plot goes below it, at any size" (2.08%). One even
stated the retired premise as its reason — "the working set is defined as four times the
cache". All four rewritten against computed values, and the cliff at 24–32 KB where the walk
finally fits is now the thing they are about. Two of them gained the genuinely surprising
fact that at 24 KB direct-mapped beats 4-way and 16-way, 66.7% against 100%.

### Verification beyond the gates

The fast cache model is not an approximation and was not taken on trust: it was compared
against the address-by-address original over **12096 (size, associativity, stride)
combinations with zero mismatches and a largest difference of exactly 0**, and its
compulsory floor was checked against a simulated 1 GB cache at eight strides — agreeing to
the last digit at every one. The RK4 switch was checked not to disturb the pictures it was
not aimed at: saddles, nodes and spirals land within a few thousandths of where Euler put
them, all of it past the frame edge. The log slider was checked for monotonicity, for 1001
distinct in-range values, for exactness at every decade and at both authored openings, and
for leaving linear parameters untouched. Contrast ratios were computed from the WCAG 2.1
formula rather than eyeballed.

### Left alone, deliberately

- **`sliding-mode` keeps forward Euler.** Its subject is chatter — a switching law with no
  continuous solution — and Euler's stepping *is* the chatter there rather than an artefact
  of drawing it. RK4 would smooth away the thing the sandbox exists to show.
- **`P.dim` (2.93:1) and `P.faint` (1.86:1) fail contrast in both themes.** They are the
  axis grid, the tick labels and the de-emphasised legends. `faint` in particular is used
  for *text*. Raising them changes the visual weight of all 13 visualisers and the circuit
  canvas with them, which is a decision about the design language and belongs to Track 5,
  not to a Track 2 cycle acting unilaterally. Recorded with the measured numbers so the next
  cycle does not have to find it again.
- **`switching`'s hard-switched trace keeps its `exp(-(td-dead)·6e6)` damping fudge.** It is
  a shape, not a model, and the caption does not claim otherwise.
- **The `cache` memo still wipes itself entirely past 60 entries.** Crude, but now that a
  sweep costs 13 ms rather than 627 the eviction policy stopped mattering.
- **The circuit editor was not touched.** It is the other half of this track and its own
  cycle; the only thing that reached it here is the palette fix, and that was unavoidable
  because it shares `Sandbox.palette()`.
- **`docs/programs` lost two MA111 payloads.** The rolling generation window, as cycle 1
  established — not a regression.

### Gates, after

Every pre-existing number unmoved. The only new number is the new gate's.

```
verify_sandbox       All good: 13 visualisers, 3 tune models survive their extremes
                     (747 draws, 249 readouts) · 364 opening values reachable   [NEW]
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 217 figure-only
verify_derivations   All good: 1128 steps across 45 courses
verify_labs          EE131 10 · EE141 8 · EE221 5 · PWR520 5 · VLSI520 5, all good
emit.py              EE131, EE141, EE221, PWR520, VLSI520 — all ok
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads · inlined 13638 KB
```

---
