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

## Cycle 3 — TRACK 3: Question Bank & Quizzes

**Target: CS201 (Data Structures & Algorithms) — its 26 quiz questions, 26 blanks and 2
numeric units.** One course, chosen on measurement rather than taste. Before editing
anything I scored every course in the catalogue against the strategy *"read nothing,
pick the longest option"*, which survives the shuffle, survives every reviewer who
reads the questions one at a time, and is invisible except in aggregate:

| course | Q | longest option is the key | mean length margin |
|---|---|---|---|
| **CS201** | 26 | **92%** (24 of 26) | **+43.5 chars** |
| CS301 | 25 | 88% | +37.1 |
| CS310 | 25 | 84% | +26.4 |
| … | | | |
| EE101 | 61 | 31% | −1.3 |
| **whole catalogue** | **1352** | **48%** | — |

Guessing scores 25%. CS201 scored 92% — the worst in the repository, and enough to pass
every quiz in the course without reading a single question.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 217 figure-only
1128 derivation steps across 45 courses
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
CS201: 7 labs · 26 quiz questions in 5 quiz units · 26 blanks · 2 numeric · 0 match
build: 3 parts / 111 keys · 32/32 + 30/30 courses · 13 visualisers · 3 tune models ·
       15 symbols · 62 payloads · inlined 13638 KB
```

### The attacks

**2. Assessment Inquisitor** — taken first, because this is its track.

- **The length tell, measured above.** The cause is uniform across the course: the key
  is written as a complete, hedged, correct sentence and the distractors as short
  dismissals. `M5/Q2` ran 178 characters against 83, 77 and 64; `M3/Q1` 169 against 65,
  61 and 55; `M4/Q4` 161 against 91, 88 and 57. Nothing about any individual question
  looks wrong. The bank as a whole is answerable without it.
- **Distractors that state their own falsity.** "It is not strictly safe; it is an
  approximation that is correct for almost all inputs." "They are the same cost; the
  $O(n)$ claim is a loose bound that nobody has tightened." "$k$ is small in practice,
  so the $k$ factor does not matter." Nobody picks a hedge. These are not misconceptions,
  they are filler, and each one silently turned a four-way question into a three-way one.
- **Two options denied the premise of their own stem.** `M3/Q1` asks *"In-order traversal
  of a BST comes out sorted. Why?"* and offers "It does not — the traversal has to be
  sorted afterwards". `M5/Q4` asks *"Why is heap sort not stable?"* and offers "It is
  stable; only quicksort is not". An option that contradicts the question it is answering
  is eliminated by grammar, not by understanding.
- **The explanation was one block written for whoever got it right.** Every `why` did
  walk all four options — which is the standard the brief asks for, and CS201 met it —
  but a learner who picked the third option has to read a paragraph about the first and
  find the clause that is about them. `blanks` has had per-option explanations (`whys`)
  since it was written; `quiz` never had them. That asymmetry is the machinery fix below.
- **Recall rather than understanding: one instance, `M5/Q1`** (the children of index $i$).
  Left as a recall question deliberately — a course needs somewhere to check that a
  definition landed — but it now carries four explanations that each say what the wrong
  formula would *do*, e.g. that $2i, 2i+1$ makes index 0 its own left child.

**3. Simulation Auditor.** No sandbox, tune or schematic in this course, so the persona
was pointed at what it can still check: every number and code claim in the bank, against
the labs that ship beside them.

- Re-derived rather than skimmed, and all hold: the doubling series `$2^{\lceil\log_2
  n\rceil} - 1$` — 16 appends copy 15, 17 copy 31, agreeing with the blanks unit's stated
  write count of 31; the fixed-increment comparison, 5×10⁹ against 2.05×10⁶ slot writes at
  $n = 10^6, c = 100$; the two-stack queue's 4000 operations; `½(1 + 1/(1−α)²) = 8.5`
  probes at $α = 0.75$ against 2.5 for a hit; random-BST height $≈3\log_2 n$ with average
  depth $1.39\log_2 n$; $2^{(3^2)} = 512$ against $(2^3)^2 = 64$.
- Two claims were checked against the lab source rather than assumed. `M1/Q4` says "1000
  `push_back` calls must cost 0 steps" — the lab asserts exactly `_l.steps == 0`.
  `M3/Q2` says "delete 50 from the lab's tree and the successor 60 happens to be a leaf,
  but insert 65 first and it is not" — the lab builds `50, 30, 70, 20, 40, 60, 80`, where
  60 is a leaf, and 65 descends right-left-right onto 60. Both correct.
- Every new number was computed before it was written: `$\binom{23}{2} = 253$`, the
  birthday threshold at $k ≈ 1.18\sqrt{m}$ giving 23 in 365 slots and 118 in ten thousand,
  and the shunting-yard counter-example `3 4 5 - -` evaluating to $3-(4-5) = 4$ rather
  than $-6$.

**4. UX & Accessibility Hardener.** Four defects in the quiz surface itself, which is the
delivery mechanism for everything this track authors.

- **Answering with the keyboard lost your place in the page.** `btn.disabled = true` is
  applied to the button that was just clicked, and a disabled element cannot hold focus,
  so the browser drops it on `<body>`. Answer question 1 with the keyboard and the next
  Tab restarts at the top of the document.
- **The explanation appeared in silence.** `.ex-slot` is filled with the entire
  pedagogical payload of the unit — right or wrong, and why — with no announcement of any
  kind. And `#quiz-out`, which carries the score, had none either.
- **Four buttons with nothing to say which question they answer.** `.opts` was a bare
  `div`; the question text was a `div` with no id. A screen reader met four unrelated
  buttons.
- **`.explain` had no `code` style at all**, so `` `self.tail.next` `` and
  `` `& 0xFFFFFFFF` `` — which the explanations are full of — rendered at full size in
  the browser's default monospace, mid-sentence.

**1. Senior Educator.** The stems are concrete and the explanations already derive rather
than assert, so this persona found less than the others. What it did find:

- **Four concepts the module lists and nothing tests.** M1's "random access needs
  contiguous slots; $O(1)$ splicing needs references" — the quiz never asked when a linked
  list actually *wins*. M2's "RPN removes the need for precedence and parentheses". M3's
  invariant-versus-local-check distinction. M4's "collisions are certain — the birthday
  bound bites long before the table is full", which is the concept in the module most
  likely to be disbelieved. One question added to each, taking every module to six.

### The defect the new gate found, in a course this cycle was not looking at

**Five EE131 question stems are fenced Python blocks, and the quiz renderer had no fence
support.** `mdInline()` handles code spans, bold, italic, links and maths — and no block
markup whatever. So `EE131/M2` asks

> With `v = 5.5`, what does this print?
> ```python
> if v > 0:
>     print("positive")
> elif v > 5:
>     print("big")
> else:
>     print("other")
> ```

and what reached the screen was a literal ``` followed by
`if v > 0: print("positive") elif v > 5: print("big") else: print("other")` on one
unindented line, because HTML collapses newlines. In a language whose meaning *is* its
indentation, that is the question destroyed — five of them, across M2 and M3.

`renderMd()` would have drawn the block. It would also have hung a **▶ Run** button off
it, so a question asking what a snippet prints would have offered to print it. So the
quiz got its own `quizProse()`: the two pieces of block markup a question actually uses —
paragraphs and fenced code — highlighted, whitespace preserved, scrolling in its own box
at 375px, with nothing to press. Options keep `mdInline`, because they live inside a
`<button>` where a `<pre>` has no business.

This repairs all five EE131 stems with no content edit at all, and it makes the paragraph
breaks that CS201, CS320 and EE131 already authored into their explanations actually
paragraph. Verified by rendering **all 2832 quiz texts in the catalogue** through
`quizProse()` as shipped: 6 contain a fence and all 6 now draw, and the other 2826 come
out byte-identical to what `mdInline()` produced, so nothing that was working changed.

### Found in my own work, and fixed

Three, all caught by mechanical sweeps rather than by re-reading.

- **A correction that inverted itself.** `M1/Q3`'s new explanation for the "keeps `pop` at
  $O(1)$ worst case" distractor said "`pop` is $O(1)$ amortised under either rule" —
  directly contradicting the key of the same question, which is that the half-full trigger
  destroys the amortised bound. The sentence I replaced had carried the hedge "when it is
  not being adversarially poked" and I dropped it. This is the failure mode the curriculum
  names: *a correction can invert what it was written to fix.* It now separates the two
  bounds explicitly — worst case unchanged under both rules, amortised case rescued only
  by the quarter.
- **Four raw-string escapes shipped as literal backslashes.** `r"the string \"1\""` keeps
  its backslashes in Python, so `M4/Q5` would have read `the string \"1\"` on screen.
  Found by sweeping the whole catalogue for a backslash before a quote — 4 hits, all mine,
  none pre-existing.
- **A false positive in my own gate, which condemned correct content.** The duplicate-option
  check normalised case, and `MA201/M4` offers `$f(x) = F'(x)$ and $F = \int f$` against
  `$F(x) = f'(x)$ and $f = \int F$` — two opposite claims that differ in nothing but the
  case of two letters. The gate reported that correct question as a duplicate on its first
  run. Case folding removed from both the gate and the emitter check, with the reason
  written next to it: a gate that condemns working content is worse than the defect it was
  written to catch.

### What changed

**Machinery — `quiz` gains the per-option explanations `blanks` already had.**
`emit.py` accepts an optional `whys` on a question: one entry per option, the key
included, each rejected if empty or if it names an option by position. The renderer shows
the entry for the option that was actually picked, above the shared account of the
question. The key is emitted **only when authored**, so all 46 untouched courses still
round-trip byte for byte and `emit.py --all` stays a drift detector — confirmed by the
diff, in which `catalog/CS201.json` is the only catalogue file that moved.

**Machinery — the shuffle was never per-learner, and its own comment said it was.** The
comment reads "stable for a given learner (their best score keeps its meaning) but not the
authoring order"; the hash key was `lessonId + ':' + qi` and nothing else, so the order was
identical for every learner on earth and publishable as a list of letters that stays
correct forever. `quizSeed()` mints one random value per install, folded into the hash: the
order is still fixed for one person across retries, and no longer shared between two. It
rides along with name and theme through `resetProgress`, so clearing progress does not
silently reshuffle the catalogue. Measured over 20000 synthetic installs, the key now lands
at 25.1% / 25.0% / 24.9% / 25.0% across the four slots — the position tell is gone rather
than tuned.

**Content — all 26 questions rewritten, 4 added.**

| | before | after |
|---|---|---|
| questions | 26 | 30 |
| "pick the longest option" | 24 / 26 — **92%** | 0 / 30 — **0%** |
| mean length margin | +43.5 chars | −6.7 chars |
| per-option explanations | 0 | **120** |
| words of feedback | 3049 | 7079 |

Every distractor is now a misconception with a name. The ones worth recording, because
they took the most work to find: *"exactly $2n$ — each element written once and copied
once"* (the nearly-right amortised argument, which misses that the first element is copied
at every resize); *"doubling holds less memory, because it grows the store less often"*
(exactly backwards, and the answer explains that doubling is the wasteful policy and the
half-empty store is what buys the cheap append); *"`push_back` is $O(1)$ amortised — the
walk happens, but rarely"* (amortised versus true constant, in a module that has just spent
two units on amortisation); *"$1 + n/(2m)$ — a failed lookup stops half way down the
chain"* (successful search mistaken for unsuccessful); *"an in-place sort cannot be
stable"* (a false general rule, refuted by insertion sort); and *"the dropped index can
still be a maximum, but only of windows already reported"* — half of the correct argument,
attached to the wrong half of the reason.

The four new questions: when a linked list actually beats an array (a cursor you already
hold, not deletion in general); how RPN can mean anything without parentheses; a four-node
tree that passes a parent-versus-child check and is not a BST, which is why the lab's
checker carries `lo`/`hi` down the recursion; and the birthday bound, where 23 keys in 365
slots is even odds and ten thousand slots reach it at 118.

**Accessibility — `src/app.js`, `src/index.head.html`.** Focus moves deliberately onto the
explanation when the clicked option is disabled, so a keyboard learner keeps their place
and the next Tab is the next question. `#quiz-out` is rendered empty and given
`role="status"`, which is the one order a live region actually announces in. `.opts`
becomes a `role="group"` labelled by the question text. `.explain` gains a `code` style,
taken from `--code-ink` rather than `--lime` — the light-theme trap cycle 2 documented, and
the one `.quiz-q .qt code` beside it still falls into.

**A new gate — `tools/verify_quiz.mjs`.** This track had no gate at all, because there is
nothing in a quiz for a solver to disagree with. So it does not try to mark the questions;
it measures whether they can be answered without reading them. Structural failures are
hard and unbudgeted: two options that read the same, an empty option or explanation,
`whys` that is not one entry per option, a positional reference anywhere in the feedback,
and block markup the renderer cannot draw. The length tell is ratcheted against
`tools/quiz_budget.json`, which records what each of the 47 courses scores today: the gate
fails when a course gets **worse**, and also when it gets better without the entry being
lowered, so the number cannot drift in either direction unnoticed. It re-reads `emit.py`'s
positional-reference rule and `app.js`'s `quizProse` and refuses to run if either has
changed shape, so it cannot end up enforcing a rule the source has abandoned.

The gate was not trusted until it was seen to fail. Seven adversarial mutations of CS201
were fed to it: a duplicated option, a positional reference planted in a `whys` entry, a
`whys` list one entry short, the length tell restored by padding every key, an improvement
left unrecorded, a course with no budget entry, and the unmodified file as a control. All
seven produced the intended verdict.

### Left alone, deliberately

- **CS201's 26 blanks were audited and not changed.** They already carry per-option
  explanations on all 26, the distractors are real (`self.capacity - 1` for the off-by-one,
  `0.25` for writing the quarter directly instead of multiplying out, `<=`/`>`/`>=`/`<`
  for the tie-break that implements stability), and the arithmetic in them agrees with the
  quiz. Two soft spots recorded rather than fixed: `M1/B1`'s `self.writes` is not a
  misconception anyone holds, and `M4/B2` is a two-option True/False and so a coin flip.
  Neither is exploitable — a blanks unit is graded as six holes together — and inventing a
  third option for a genuinely binary fact would be worse than the coin flip.
- **Both numeric units were audited and not changed.** Both carry `wrong` and `hint`, both
  answers were recomputed. Catalogue-wide, all 433 numeric units carry both, so the
  "explain the wrong answer too" standard is already met by that kind everywhere; recording
  it so the next cycle does not re-survey it.
- **CS201 has no `match` unit and cannot have one.** `MATCH_SYMBOLS` in `emit.py` is 15
  circuit symbols (`R`, `C`, `L`, `D`, `NPN`, `OPAMP`, …) and `norm_match` rejects anything
  else, so `match` is an electronics-only kind by construction — which is why the whole
  catalogue has 11 of them. Giving it a non-symbol mode is a machinery cycle of its own,
  not a widening of this one.
- **The other 24 courses over 50% on the length tell were not touched**, and this is the
  main debt this cycle leaves. CS301 (88%), CS310 (84%), DSP520/DSP530/EMAG530/VLSI530
  (80%), CS330 (77%), MA101 (75%). The catalogue as a whole sits at 48%, against 25% for
  guessing. Fixing them means rewriting roughly 650 questions across 24 courses, which is
  several cycles and certainly not one that also claims to have verified anything. The
  budget file pins every one of those numbers so the debt cannot grow while it waits.
- **387 blanks in 11 courses have no per-option explanations** — EE102 (102), EE121 (93),
  EE101 (87), EE211 (40), MA111 (20), MA121 (17), EE241 (11), EE221/MA112/MA201 (5 each),
  EE202 (2). The field has existed all along and the CS courses use it on 100% of theirs.
  This is the same defect as the quiz one this cycle fixed, in the kind next door.
- **`.quiz-q .qt code` still takes its colour from `--lime` rather than `--code-ink`**, so
  an inline code span in a *question* keeps the light-theme problem that cycle 2 measured
  on the canvas. It is legible, unlike the canvas case, and changing it is a Track 5
  decision about the token ramp rather than something a Track 3 cycle should do on its own.
- **`docs/programs` lost five payload files.** The rolling generation window, as cycles 1
  and 2 both established. Verified rather than assumed: the current generation lists 62
  entries covering 62 distinct courses, every one present on disk, and no file on disk sits
  outside a retained generation.

### Gates, after

Every pre-existing number unmoved. The only new numbers are the new gate's.

```
verify_quiz          All good: 1356 questions in 250 quiz units · 120 per-option
                     explanations · every course within its answer-tell budget   [NEW]
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 217 figure-only
verify_derivations   All good: 1128 steps across 45 courses
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_labs          CS201 6 labs · EE131 10 labs, all good
emit.py CS201        ok — 5 modules, 5 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads · inlined 13667 KB
```

Beyond the gates: 2832 quiz texts rendered through `quizProse()` with 0 fences leaking and
0 drift from the previous renderer; the option-to-explanation mapping checked on all 30
CS201 questions through the real `shuffledOptions`; the shuffle checked for stability under
one seed, for reaching all four slots, and for 25% uniformity over 20000 installs; and the
new gate checked against seven mutations it had to reject.

---
