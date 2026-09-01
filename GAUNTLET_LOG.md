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

## Cycle 4 — TRACK 4: Subject Breadth & Progression

**Target: MA101 (Discrete Mathematics).** One course, chosen on measurement. Two
numbers picked it out of 62.

*Progression.* Scoring every course by units per module, MA101 sits at **1.0** — eleven
modules holding eleven units, seven of which are a lone `quiz` and four a lone `lab`.
Seven modules therefore go from a list of concept bullets straight to being examined,
which tests whether you already knew, and the course has **no reading unit at all**.
Only the fifteen syllabus-only stubs score as low, and none of those is a prerequisite
of anything.

*Prerequisite bridge.* MA101 is a declared prerequisite of **CS201, CS301, CS310 and
MA121** — four courses, including the one cycle 3 rebuilt to a 30-question,
120-explanation standard. Counting occurrences of asymptotic notation:

| | MA101 | CS201 | CS301 | CS310 | MA121 |
|---|---|---|---|---|---|
| `O(...)` | **2** | 91 | 13 | 6 | 8 |
| `Theta` | 0 | 1 | 16 | 0 | 0 |
| "geometric series" | 0 | 8 | 2 | 0 | 0 |
| countability | 0 | 0 | 0 | 1 | 0 |

MA101's two uses are `O(log e)` in M9 and `O(n^3)` in M10 — the notation **used and
never defined**. And a search of all 62 courses for the definition behind it (a
constant, a threshold, `f(n) <= c*g(n)` beyond it) returns **nothing anywhere in the
catalogue**. The language four downstream courses are written in was defined by no
course in the repository, including the one they name as the place it comes from.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 21 tune units
216 numeric answers verified, 0 unchecked, 217 figure-only
1128 derivation steps across 45 courses
1356 questions in 250 quiz units · 120 per-option explanations
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
MA101: 11 modules · 11 units · 0 read · 0 derive · 28 questions
       (longest-is-key 21, budget 21, margin +28.8) · 5 labs
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads · inlined 13667 KB
62 courses, 366 modules, 1864 units
```

### The attacks

**1. Senior Educator.** Pointed at the progression, which is this track's half of the
persona's brief.

- **Seven modules examine before they explain.** M2, M3, M4, M5, M6, M8 and M11 hold a
  quiz and nothing else. Recorded, mostly **not fixed** — see below; that is Track 1's
  ground and cycle 1 established that a density pass is its own cycle.
- **The two `O(...)` claims are announcements.** Both were swept for — exactly two in
  the whole course, both in concept bullets — and both are now picked up in M12 and
  turned into counts with the constant and threshold attached: Warshall's innermost line
  runs exactly `n^3` times, so `c = 1`, `n0 = 1`; square-and-multiply costs at most
  `2(floor(log2 e) + 1) <= 4 log2 e`, so `c = 4`, `n0 = 2`, and at `e = 1000` that is 20
  multiplications against the naive loop's 999.
- **M5 states pigeonhole without its scope doing any work.** "No injection runs from a
  larger finite set into a smaller one" is correct and the word *finite* is load-bearing,
  and nothing said so. It is exactly what `n -> 2n` stops obeying, which is the first
  thing M13 needs.
- **M8's characteristic-equation method is presented as the way to solve a recurrence.**
  It handles linear homogeneous recurrences with constant coefficients and cannot touch
  `T(n) = a*T(n/b) + f(n)`, whose argument is divided rather than decremented — and that
  is the shape CS301's entire first module is about. The boundary was nowhere stated.

**2. Assessment Inquisitor.** The existing 28 questions were audited and **not changed**:
every key is correct, every `why` walks the options, and none uses a positional
reference. The one measured defect is inherited debt cycle 3 already recorded — MA101
scores **21/28 (75%)** on "pick the longest option" — and it is pinned by the budget
file. The persona's real work this cycle was on my own new questions, and it caught them:
see below.

**3. Simulation Auditor.** No sandbox, tune or schematic in this course, so the persona
was pointed at what it can still check — arithmetic in prose, and code that claims an
output.

- **Every number written into the two new modules was recomputed independently**: 62
  checks covering the geometric sums, the harmonic block bound for `k = 1..11`, the
  threshold table, the exponentiation bound over `e = 2..10000`, the pairing function's
  bijectivity over 200 diagonals, and the diagonal-argument table. All agree.
- **Both new code listings were filled with their own answer key and executed.** The M12
  sweep prints 35, 1 and `limit + 1`, matching all three claims made about it; the M13
  listing's asserts pass, including `pair(*unpair(n)) == n` for `n` in `range(1000)`.
  Nothing in the repository would have caught a wrong stated output — the blanks gate
  checks structure and never runs anything.

**4. UX & Accessibility Hardener.** Content-side only, as cycle 1's reading surface work
still holds. Checked rather than assumed: every equation is `$...$` or `$$...$$` and
inherits the token ramp, the two fenced listings are the block markup `renderMd` and
`quizProse` both draw, and no hard-coded colour, raw HTML or wide table was introduced.
The one thing an author can still break at 375px — a wide table — was avoided by writing
the threshold data as a fenced text figure inside `overflow-x:auto` rather than as a
markdown table.

### The defect this cycle found in the machinery

**`emit.py --all` is not the drift detector the log says it is.** Running it rewrote
**41 courses this cycle never touched**. The diff is 78 lines and every one of them is
the same thing: `"check": ""` appended to 26 figure-only `numeric` units, because
`norm_numeric` has emitted `check` unconditionally since `verify_numeric.mjs` was written
and those 41 files were never re-emitted afterwards. Cycle 3's line — "all 46 untouched
courses still round-trip byte for byte" — was true of the `whys` key it added and not of
the emitter as a whole.

**Reverted, not landed.** The field is inert (`verify_numeric` already reports 0
schematics with no check, and figure-only units are exactly the ones that carry an empty
one), and a 41-file whole-catalogue reformat has nothing to do with subject breadth.
Burying it inside a Track 4 content cycle would make this cycle's diff unreviewable. It
is a one-command mechanical change and belongs in its own commit.

### What changed

**Two new modules, appended.** MA101 goes 11 modules to 13, 11 units to 20.

| | M12 | M13 |
|---|---|---|
| title | Growth of functions: sums, and what an O actually claims | Infinite sets: counting past the finite |
| reading | 1580 words | 1516 words |
| derivation | the geometric sum, 6 steps | the pairing function, 6 steps |
| quiz | 5 questions, 20 per-option explanations | 5 questions, 20 per-option explanations |
| blanks | 5 holes, 20 per-option explanations | 5 holes, 20 per-option explanations |
| numeric | the threshold at `c = 4` | — |
| concepts | 9 bullets | 8 bullets |

**Appended, not inserted, and that is deliberate.** M12 belongs after M8 by subject. A
lesson id is `MA101-M<n>-<KIND>` and it is the record of what a learner has finished, so
inserting would renumber M9–M11 and orphan their progress — the invariant the curriculum
names. Appending costs nothing here: M12 needs induction (M6), the sums of M7 and the
recurrences of M8, and M13 needs the bijections of M5 and the triangular number of M7.
All of it is already behind them. The reason is written into the source beside the module.

**M12 derives rather than announces.** The geometric sum comes out of multiply-and-
subtract, not from a table; the `1 + 2 + 4 + ... + 2^k = 2^(k+1) - 1` that CS201's
amortised argument leans on is then read off it, together with the sentence that argument
actually needs — *the total is less than twice the last term*. The harmonic sum is pinned
between `1 + k/2` and `1 + k` by blocking on powers of two, since it has no closed form
and looking for one is the mistake rather than the exercise. Then the definition, with a
worked witness: `3n^2 + 20n + 500 <= 4n^2` fails at `n = 34` (4648 against 4624) and holds
at `n = 35` (4875 against 4900), the positive root being `10 + sqrt(600) = 34.4949` — and
`c = 523, n0 = 1` is a second witness to the same claim, because the pair is never unique
and the two trade against each other.

Four misreadings are named and refuted: that `O` means worst case (it is a claim about
functions, and best and worst are two different functions); that `O` is tight (`n = O(n^2)`
is true and useless); that the hidden constant is always constant (`2^(n+1) = 2*2^n` is
`O(2^n)`, `2^(2n) = (2^n)^2` is not, and no fixed `c` bounds `2^n`); and that
asymptotically better means better (`100n` beats `n log2 n` only past `n = 2^100`, about
`1.27e30`, so the correct mathematics recommends the slower program on every input that
will ever exist).

**M12 stops exactly where CS301 starts.** CS301 already derives the master theorem from
the recursion tree, and this module does not duplicate it. It supplies the layer under it
— the sum, and the notation — and its closing says so explicitly: the ratio between
consecutive levels is `a/b^d`, the three cases are the three things this geometric series
can do, and the algorithms course does that sum with the sum proved here.

**M13 completes M5 rather than opening a new topic.** Same definition of size, applied
where counting is impossible: the hotel, then `n -> 2n` onto the evens, then the integers
by interleaving — with the *failed* listing shown first, because "all the naturals, then
the negatives" is the attempt everyone makes and its failure is the definition doing its
work. Then the diagonal sweep of the pairs, the Cantor pairing function derived from M7's
triangular number, the countable union, the rationals, and the finite strings — which is
the one that matters, because a program is a finite string. Then Cantor's diagonal on a
worked 4x4 table, with the objection everyone raises (*just add `d` to the list*) stated
in its own voice and answered: the hypothesis was an arbitrary list, so patching an
instance answers a claim nobody made. It closes on the counting argument for
undecidability — countably many programs, uncountably many languages, no injection — and
is careful to say what that does **not** deliver: no example, no construction, and nothing
about any language anyone cares about. CS310 builds the specific one.

**Six bridge bullets in the existing modules**, so the new material is reachable from
where it is needed rather than only from the end: M5 (pigeonhole is finite, and `n -> 2n`
is what that permits), M6 (induction confirms a closed form but never proposes one), M7
(the triangular number, spent on numbering an infinite grid), M8 (the divide-and-conquer
shape the characteristic equation cannot touch), M9 and M10 (the two undefined `O`s, now
pointing at their definition). Plus the course summary, two outcomes, and the two
references the new modules are actually written from.

### Found in my own work, and fixed

**Eight of my ten new questions had the longest option as the key**, and two had the
shortest. That is precisely the defect cycle 3 measured across the catalogue and named the
cause of: the key gets written as a complete hedged correct sentence and the distractors
as short dismissals. Left alone it would have taken MA101 from 21/28 to 29/38 and the gate
would have failed it — correctly. All ten option sets were rewritten to a tight length band
and re-measured: **0 longest-is-key, 0 shortest-is-key**, mean margin −2.6 characters
against the course's existing +28.8. Writing the fix is not the same as having internalised
it; the measurement is what caught it.

**A comment in the M13 listing described the wrong loop condition** — it said the test was
on diagonal `s+1` when the code tests diagonal `s`. Caught by executing the filled listing
rather than by re-reading it.

**One "obviously", one "simply" and one hand-waving "just"** in prose I had just written
against a persona brief that names them as the tells. Removed. The two remaining `just`s
are temporal ("the bound has just failed at `n`") and one is a quoted objection in the
objector's voice, which is deliberate.

### Left alone, deliberately

- **The seven modules that still examine before explaining.** M2, M3, M4, M5, M6, M8 and
  M11 each still hold one quiz and nothing else, and MA101 is still at 1.5 units per
  module against EE101's 12.6. This is the largest remaining defect in the course and it
  is real. It is also a density pass over seven modules — cycle 1's MA111 shape, and its
  own cycle. Widening this one to cover it would have meant two new modules built to no
  standard and seven readings written in a hurry.
- **No lab in either new module.** MA101's four labs are its assessment structure ("4 lab
  checkpoints, 10% each") and a fifth would change the weighting. More to the point,
  CS201's M1 lab already instruments a growable array and asserts its write count, so an
  MA101 lab counting array copies would duplicate the course this module exists to feed.
  The blanks units carry the code instead, and both were executed. A pairing-function lab
  in M13 would duplicate nothing and is the honest next step.
- **The 41-file `check` drift, reverted and recorded above.**
- **Topics considered and rejected for want of downstream demand.** Boolean CNF/DNF and
  satisfiability: my first search flagged CS310 with 13 hits, and reading them showed
  every one is *Chomsky* normal form in the CYK module — a false lead from an ambiguous
  regex, and a topic no course in the catalogue actually needs from here. Likewise
  MA121's six "diagonalis-" hits are matrix diagonalisation, not Cantor. DAG and
  topological order: zero hits anywhere in the catalogue, downstream included, so adding
  it would be padding. Complexity reductions (CS301, 11 hits) are CS301's own subject and
  not a discrete-maths prerequisite. Recording all four so the next cycle does not
  re-derive them.
- **`credits` and `hours` unchanged at 10 and 110**, and `catalog/_spine.json` untouched.
  The spine carries course metadata only, no module counts, and 13 modules holding 20
  units remains far lighter than MA111's 11 modules and 59 units at the same nominal load.
- **A pre-existing "is simply" in M8's quiz explanation** was seen and left; sweeping the
  prose of modules this cycle did not otherwise touch is Track 1's job.
- **`docs/programs` aged out two CS201 payloads and gained two MA101 ones.** The rolling
  generation window, as cycles 1, 2 and 3 all established — and this cycle built twice, so
  it could also have left an orphan the pruner never knew about. Verified rather than
  assumed: 64 payload files on disk, all 64 referenced by one of the 3 retained
  generations, covering 62 distinct courses, **0 orphaned and 0 missing**.

### Gates, after

Every pre-existing number unmoved. Four numbers moved, each by exactly what was added.

```
verify_derivations   All good: 1140 steps across 46 courses   (1128 + 12 new; MA101 0 -> 12,
                     and MA101 is the 46th course to have any)
verify_quiz          All good: 1366 questions in 252 quiz units · 160 per-option
                     explanations · every course within its answer-tell budget
                     (1356 + 10 · 250 + 2 · 120 + 40)
                     MA101: 38 questions · longest-is-key 21 (budget 21, unmoved in count,
                     75% -> 55% in rate) · shortest-is-key 0 · margin +28.8 -> +20.6
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
                     (217 + the 1 new)
verify_labs MA101    All good: 5 labs   (M1 7/7, M7 7/7, M9 7/7, M10 8/8, CAP 12/12)
verify_circuits      All good: 80 circuit exercises, 340 checks
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
emit.py MA101        ok — 13 modules, 4 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads · inlined 13726 KB
catalogue            62 courses, 368 modules, 1873 units, 234 readings
```

Beyond the gates: 62 arithmetic claims recomputed independently before being written;
both code listings filled with their own key and executed against every output they
claim; the option-length tell measured on all ten new questions and driven to zero; and
the whole-catalogue re-emit run, read, and reverted rather than shipped.

---

## Cycle 5 — TRACK 5: UI, Layout & Visual Aesthetics

**Target: the application shell — the icon rail, the top bar and the curriculum rail.**
`renderShell`, `renderRail`, `toggleRail`, `syncRailToggle` and `renderDegradeBanner` in
`src/app.js`; `.app`, `.iconrail`, `.logo`, `.inav`, `.avatar`, `.topbar`, `.screen-id`,
`.search`, `.metric`, `.tbtn`, `.menu-btn`, `.rail-btn`, `.body`, `.rail`, `.rail-*`,
`.gmark` and `.scrim` in `src/index.head.html`. One subsystem, and the one that is on
the screen on every route — a defect here is a defect on all 1873 units at once.

Chosen because the alternative was already done: the previous run's Track 5 cycle took
the *reading* surface, and its work is landed (`--code-ink`, `.article`'s `66ch`
measure, the `.tw` table scroller, the pre-paint theme resolution — all present and
verified in the file, not assumed). The shell had never been audited. Track 5's four
sub-headings each have something to answer for in it, and three of the four turned out
to be answering for the same thing.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 21 tune units
216 numeric answers verified, 0 unchecked, 218 figure-only
1140 derivation steps across 46 courses
1366 questions in 252 quiz units · 160 per-option explanations
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
build: 3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers · 3 tune models ·
       15 symbols · 62 payloads · inlined 13726 KB · shell 1089 KB
```

### The attacks

**4. UX & Accessibility Hardener** — taken first, because this track's brief is mostly
its brief. Every ratio below was computed from the WCAG 2.1 sRGB formula against the
*composited* stack — the tint over the surface over `--ground` — not against the ground.

- **The hover state on the primary navigation is not faint in the light theme. It is
  absent: 1.00:1.** `.inav:hover` is `rgba(255,255,255,0.05)` with no
  `[data-theme=light]` override, painted over `--nav`, which the light theme makes
  `rgba(255,255,255,0.80)`. White at 5% over white. The discipline exists and had been
  applied three times in the same file — `.tbtn:hover`, `.rail-track>button:hover` and
  the rail rows all carry their override — and was missed on the one element that is
  the app's only navigation.
- **It is five more places.** Sweeping for the pattern rather than fixing the line:
  `.btn.ghost:hover` 1.00, `.btn.dark`'s own fill 1.00 (the button has no background at
  all in the light theme), `.btn.dark:hover` 1.00, `.mod>.mod-head:hover` 1.00. The
  sixth was `.inav`. Every other bare white wash in the stylesheet — `.ftab`, `.ptab`,
  `.mobile-tabs`, `.wbar`, `.btn.run:disabled` — sits on `--editor`, which is
  deliberately dark in both themes, and is correct.
- **The current section is fainter than the sections you are not on.** `.inav.active` is
  `--lime` on `--lime-08`: 13.34:1 in the dark theme and **3.63:1** in the light one,
  against an idle `.inav` at 4.82 / **4.95**. The light theme inverts the emphasis.
  Same inversion, same cause, three more times: `.rail-btn.on` 3.61 against an idle
  4.92, `.metric.xp b` **3.61 as text** at 12px bold, `.rail-sec` **3.93** on 10px
  uppercase mono with 0.16em tracking. And `.btn.accent`'s label, **3.48**.
  The cause is one thing: `--lime` in the light theme is `#5F8A0B`, which is 3.76:1 on
  the ground and drops further on its own tint — and it cannot simply be darkened,
  because it is also `.btn.primary`'s *background* against a near-black `--on-lime`.
  This is the trap the previous run measured on `.article code` and on `--amber`; it
  had four more instances and a fifth in the button component.
- **The avatar's ink is a hard-coded `#0B0C0E` on a gradient that flips.** `--blue` and
  `--purple` are pale in the dark theme and dark in the light one, so the level number
  measures 7.26 / 7.19 dark and **3.27 / 3.17 light**, at 12px weight 600. `.prof-av`
  shares the literal at 24px bold, where 3:1 applies and it passes — which is why it
  had never looked broken.
- **The status ring is invisible in both themes: 1.43:1 dark, 1.61:1 light.** `.gmark`
  took its border from `--line-3`, the generic hairline. The unfilled ring is what says
  "not started" in the rail, and `renderBuild` uses the same element for a check that
  has not run yet — so a build exercise's check list drew its pending rows with nothing
  in the status column.
- **"Could not be loaded" was written in the disabled-text tier.** `.rail-miss` is
  `--ink-5`: **1.87 / 2.01**. It is the line that tells a learner an entire programme's
  courses are missing from every total on screen.
- **The avatar is a `<div>`, and it is the only route to Profile in the application.**
  No `NAV` entry points there; the two other `go({view:'profile'})` calls are inside
  import and reset, both already on that screen. So the learner's name, the progress
  export, the import and the reset were reachable by mouse only — and `warnNoStorage`
  raises a toast reading "open Profile (avatar, bottom left)" about a control a keyboard
  cannot reach. `navSectionFor` even returns `'profile'`, for a section with no icon.
- **The closed mobile drawer is still in the tab order.** At ≤980px `.rail` is
  `transform:translateX(-110%)`, and a transform removes nothing from focus. Tab from
  the menu button on a phone and you walk every programme heading, every band and every
  course in an open band — the current route opens its own band, so this is the normal
  case, not the worst one — before reaching a word of the lesson.
- **There is no skip link.** On desktop the DOM order is brand, four section icons,
  avatar, drawer button, panel toggle, search, notepad, theme — and then the entire
  curriculum rail, before `<main>`. On every page.
- **Nothing announces state.** Four `[data-nav]` buttons carry `.active` as a class and
  no `aria-current`, so a screen reader meets four identically-described buttons with
  nothing to say which one it is on. The band buttons and the track disclosure expand
  and collapse lists with no `aria-expanded`. `#menu-btn` never changes from "Open
  curriculum" and has no `aria-expanded`. `#brand`'s accessible name is its glyph, `</>`.

**3. Simulation Auditor** — pointed at the layout, computed rather than trusted, since
this repository has no browser and this subsystem has no solver.

- **The top bar does not fit a phone, and the screen title is what pays.** At 375px the
  icon rail takes 60px and the bar's own padding 44, leaving 271. Its six gaps are 96.
  Three 32px buttons are 96. Two metric pills are 48px of padding before any digits.
  That is **275.4px of fixed furniture in 271px of bar** with a one-digit streak and a
  one-digit XP, and none of it is text I had to estimate. `.screen-id` has `min-width:0`
  and the largest flex base, so it absorbs the entire overflow first and collapses to
  zero — and the bar is *still* over, so `.tbtn` and `.menu-btn` shrink. Their automatic
  minimum size is min-content: one 14px glyph, an 18px svg. The theme toggle, the
  notepad and the only way to open the curriculum on a phone all shrink through WCAG
  2.5.8's 24×24 floor. With a realistic five-character XP it is 298px in 271.
- **Fifteen course ids do not fit their column.** `.rail-course` gave the id a 32px
  track with a 9px right pad — 23px of text — and `text-align:right`, so anything wider
  spills leftwards. Fifteen of the 62 ids in the two spines are seven characters
  (`CTRL510`, `VLSI510`, `EMAG510`, `RFIC510`, `ELEC430`…), which at 10px JetBrains Mono
  — 0.6em per glyph, the font's own metric, every glyph — is 42.0px. That is 19px of
  overflow into a 16px row padding, so the id ends 3px past the rail's own edge and
  under the active row's 2px marker.
- **A band's colour is authored, passed into the rail, and dropped.** `renderRail`
  writes `style="--tt:<tint>"` onto `.rail-track .t-icon`, and the rule read
  `background:var(--surface-2)`. `.year-badge` on the study plan and `.pb-icon` on the
  programmes card — the same icon, the same band — both read `--tt`. Every band in both
  spines has a real tint, checked; none is undefined.

**1. Senior Educator** — this persona has no prose here, so it was pointed at the
type scale, which is the shell's equivalent of whether the thing explains itself.

- **`.rail-module h4` is 9.5px.** It is a module *title* in the curriculum tree, and it
  is the smallest type in the application — smaller than the 9.5px table headers the
  previous run raised to 11px on the reading surface for exactly this reason.
- **`.rail-sub>button .cid` is 9px**, and it is not an id: it holds `▸`/`▾`, the only
  expand/collapse affordance in the rail.
- **`.screen-id b` is `white-space:nowrap` with no overflow rule of its own.** The
  parent clips, so a long lesson title is cut mid-glyph rather than ellipsised.

**2. Assessment Inquisitor.** No graded question in this subsystem. Pointed at the one
thing in scope it can judge — whether a state *announces itself or merely exists* — and
that is the `aria-current` / `aria-expanded` finding above, plus one more: at ≤640px
`.metric span` was `display:none`, which removes the label from the accessibility tree
as well as the screen. What was left was a lime bubble reading "1,250" and an amber one
reading "4", with no word anywhere saying what either number counts.

### What changed

**Tokens — `src/index.head.html`.** Three, each named for the job rather than the hue,
following the `--code-ink` precedent the previous run set.

| token | dark | light | why |
|---|---|---|---|
| `--accent-ink` | `var(--lime)` | `#4C7005` | the accent used as *ink on its own tint* |
| `--on-avatar` | `#0B0C0E` | `#FFFFFF` | ink on a gradient that flips lightness |
| `--mark-idle` | `#666666` | `#8C8C8C` | the unfilled status ring |

`#4C7005` is already this palette's `--lime-hi` and `--link`, so no new hue enters the
design. `--mark-idle` is per theme because the surfaces are: aimed at WCAG 1.4.11's 3:1
rather than past it, so the ring stays quiet.

| surface | dark before → after | light before → after |
|---|---|---|
| `.inav.active` current section | 13.34 → 12.01 | **3.63 → 4.89** |
| `.rail-btn.on` lit panel toggle | 13.75 → 12.42 | **3.61 → 4.86** |
| `.metric.xp b` the XP figure | 13.75 | **3.61 → 5.10** |
| `.rail-sec` programme heading | 15.86 | **3.93 → 5.55** |
| `.btn.accent` label | 11.71 | **3.48 → 4.92** |
| `.avatar` blue end / purple end | 7.26 / 7.19 | **3.27 / 3.17 → 5.98 / 6.17** |
| `.rail-miss` "could not be loaded" | **1.87 → 6.16** | **2.01 → 5.36** |
| `.gmark` idle ring, rail / card / drawer | **1.43 → 3.44 / 3.33 / 3.27** | **1.61 → 3.22 / 3.33 / 3.36** |
| `.inav:hover` against its own idle | 1.11 | **1.00 → 1.13** |
| `.btn.dark` fill, `.btn.dark:hover`, `.btn.ghost:hover`, `.mod-head:hover` | 1.06–1.12 | **1.00 → 1.11–1.13** |
| rail row hover against idle | **1.07 → 1.12** | **1.08 → 1.13** |
| `.inav.active` / rail row *background* against idle | **1.17 → 1.77** / 1.16 → 1.75 | **1.11 → 1.30** / 1.11 → 1.29 |

The current-state tints went `--lime-08` → `--lime-22` because 1.11:1 is not a state.
The icon on it is a graphical object, not text, and still measures 8.78 / 4.38. Three
glows and a shadow that were baked `rgba(199,247,81,…)` now go through
`color-mix(… var(--lime) …)` so they follow the theme, and the mobile drawer's
`rgba(0,0,0,.5)` shadow gained the light-theme override `.ac-sighint` already had.

**Layout.** `--topbar-gap` and `--topbar-pad` became tokens so the 640px block can turn
them down: padding 44 → 24, gaps 96 → 60, metric padding 12 → 8. That is still not
enough — a six-character XP and a three-figure streak leave the title 17px — so the XP
pill stands down below 640px, which is the one real trade in this cycle. It is a running
total, it is on the avatar's label, on Progress and on Profile, and the streak is both
narrower and the number that changes what a reader does today. The title gets **86.4px**
and an ellipsis instead of nothing. `.tbtn`, `.menu-btn`, `.metric` and `.save-state`
became `flex:none` so no pressure can shrink a control through its own box. The rail's
id column went 32px → 50px against a measured 50.0px requirement, and its gmark column
26 → 22 to pay for it.

**Type.** `.rail-module h4` 9.5px → 11px (tracking eased 0.14em → 0.1em to suit),
`.rail-sub>button .cid` 9px → 11px, `.screen-id b` gained `overflow:hidden` and an
ellipsis. Rail rows and band buttons gained a 150ms background transition, which
`.inav` and `.btn` already had and they did not.

**The band tint, restored without a light-theme regression.** The six spine tints are
pale (`#E4EEFA`, `#FFE9DC`, …) and tuned for a dark ground: against the rail they
measure 1.56–1.59:1 dark and **1.01–1.02:1 light**, while the grey chip they would have
replaced measures 1.03 dark and 1.04 light. Swapping outright would have traded a
visible chip for an invisible one on every light install. So the tint layers over
`--surface-2` as a `background-image` and the border stays `--line`: dark goes
1.03 → 1.62, light stays where it was.

**Behaviour — `src/app.js`.** A skip link as the first focusable element, with
`tabindex="-1"` on `<main>` so it actually moves focus rather than only scrolling. The
avatar is a `<button>` with a label carrying the name, level and XP — Profile is
reachable from a keyboard for the first time — and takes `aria-current` on that screen,
since it is the one route no icon claims. `aria-current="page"` on the lit section icon;
`aria-expanded` on `#menu-btn`, on every band button and on the track disclosure, whose
chevron is now `aria-hidden` so it is not read as content. `#brand` gained a name that
is not `</>`. `toggleRail` learned the difference between a dismissal and a navigation:
Escape, the scrim and the menu button return focus to the button that opened the drawer,
while picking a lesson lands focus on `<main>` with `preventScroll` so it does not undo
the scroll `go()` has just restored. Opening the drawer focuses the *current* row rather
than the first, so the rail does not jump to the top of the tree.

**The closed drawer leaves the tab order, with no script.** `visibility:hidden` on
`.rail` at ≤980px, `visible` on `.rail.open`, with the transition delayed by the length
of the slide on the way out and 0s on the way in. That removes it from focus *and* the
accessibility tree in every browser, needs no `inert` feature test, and keeps the
closing animation.

**A new gate — `tools/verify_theme.mjs` and `tools/theme_budget.json`.** This track had
no gate, which is why five of the defects above are years old. It does not judge the
design; it checks the parts of it that are arithmetic, reading `src/index.head.html` as
shipped through a rule walker that understands `@media` (the obvious regex reads
`@media (max-width:980px){ :root` as one selector and then enforces nothing inside).

- **Every colour comes from a token**, or from an exemption written down with its reason
  — 14 of them, each naming a surface a theme cannot help: the editor chrome, the
  scrims, the iframe that renders the learner's own HTML. This is the curriculum's own
  invariant, and it has now been broken twice.
- **49 surfaces × 2 themes** against WCAG floors by kind: 4.5 for text, 3.0 for large
  text and graphical objects, and 1.1 between two *backgrounds* — which is not a WCAG
  number but is the only way to ask whether a hover exists, and 1.1 is the floor that
  catches 1.00. A `state` entry names the rule it is asking about and the gate reads the
  colour out of the stylesheet, from `sel` and from `[data-theme=light] sel`, falling
  back to the dark value when the light rule is missing — that fallback *is* the
  `.inav:hover` defect, so it is measured rather than restated.
- **The 375px top bar**, summed from the stylesheet's own knobs, against a 60px floor
  for the screen title; and `flex:none` on the controls that must not shrink.
- **The rail's id column against the catalogue**, so the 50px is tied to the data rather
  than to today's longest id.
- **The closed drawer is out of the tab order.**

The gate was not trusted until it was seen to fail. **Ten mutations, ten intended
verdicts:** the light override removed; the light override *weakened back to white*
rather than removed, which only the `from` mechanism can see; a bare hex planted on a
shell rule; `--accent-ink` reverted; `flex:none` dropped; the XP pill put back on the
phone; the drawer returned to transform-only; the id column returned to 32px;
`--mark-idle` returned to the hairline token; and the untouched control, which passes.

### Found in my own work, and fixed

- **A desktop regression I introduced.** I gave `.screen-id` `flex:1 1 auto` to make it
  survive at 375px. It already had `min-width:0`, which is what lets a flex item shrink;
  `flex-grow` would have made it *expand* on a wide screen and split the free space with
  `.spacer`, so the metrics and tool buttons would no longer sit against the right edge.
  Caught by re-reading the diff and asking what each declaration was for, rather than by
  any gate — none of them measures a desktop layout.
- **A comment that contradicted the comment four lines below it.** The 640px block said
  the knobs leave the title "67.6px", a figure from an earlier draft with a one-digit XP;
  the next comment said 17px and then 86.4px. Three numbers for one bar. The stale one
  came from before the XP pill stood down.
- **A gate bug that read a property name as a value.** `xpHidden` tested the *returned
  value* `"none"` against `/display\s*:\s*none/`, which never matches, so the gate
  silently believed the XP pill was still visible and reported 27.3px where the truth was
  86.4. It was reporting a failure, so it looked like the stylesheet was wrong. Found by
  printing the parsed inputs instead of re-reading the CSS.
- **A gate whose per-section summaries vanished after any earlier failure.** Every `ok()`
  was guarded on the global `fails` count, so a tokens failure hid the contrast result
  entirely — the operator sees one problem and fixes it, runs again, and meets the next.
  Now each section tracks its own.
- **`--tt` would have been a light-theme regression**, caught by measuring the tint
  against the rail in both themes *before* shipping it rather than after: 1.01:1. The
  layered form above is the result.
- **`--mark-idle` was one value for both themes and I split it.** A single `#919191`
  does clear 3:1 everywhere, but it lands at 6.27 in the dark theme — twice the floor,
  on an element whose whole point is to be quiet.

### Left alone, deliberately

- **`P.dim` at 2.93:1 and `P.faint` at 1.86:1 on the canvas.** Cycle 2 measured these
  and handed them to Track 5 by name, and this cycle did not take them. Re-measured and
  confirmed, so the numbers do not need finding again: `--on-editor-3` is 2.93:1 on
  `--editor` and `--on-editor-4` is 1.86:1, and `faint` is used for *text*. They are
  the axis grid, tick labels and legends on 13 visualisers and the circuit canvas — a
  different subsystem in different files, and raising them changes the visual weight of
  every canvas in the app. Candidate values, measured, so the next cycle can start from
  one: `#6B7280` → 4.07, `#767D8A` → 4.75, `#7E8694` → 5.36. A cycle that did the shell
  *and* the canvas would have verified neither.
- **`--ink-5` is still roughly 2:1 in both themes.** `.rail-miss` moved to `--ink-3`
  rather than the tier being repaired, because `--ink-5` is placeholder and disabled
  text and darkening it to AA stops a placeholder being distinguishable from a filled
  value. That is a design decision, as the previous run recorded; what this cycle fixed
  is a status message that had no business in that tier.
- **`.btn.accent`'s border at 1.48:1 in the light theme.** `--lime-30` against the card.
  It is a border on a button that already has a filled background and an AA label, so it
  is decoration rather than the affordance. Recorded with the number.
- **The search box is `display:none` below 980px.** So is `⌘K`'s target, which means the
  keyboard shortcut is live on a phone and focuses an invisible input. Pre-existing, not
  introduced here, and giving mobile a search is a feature rather than a repair.
- **`.screen-id span`, the crumb, is hidden below 640px** along with `.save-state`.
  Deliberate: 86.4px holds a title or a title and a crumb badly.
- **`syncRailToggle` flips the panel toggle's `title` but not its `aria-label`**, so a
  screen reader hears "Toggle the curriculum panel" and its `aria-pressed` state rather
  than "Hide"/"Show". That is a defensible reading of the pattern and was left as is.
- **`.rail-module h4` is an `h4` inside a `nav` with no h1–h3 above it.** A heading-level
  jump in a landmark. Changing the element changes the rail's markup contract with
  nothing measuring it; recorded instead.
- **The webfont still reflows on a cold load.** `fonts.googleapis.com` with
  `display=swap` and no metric-matched fallback, as the previous run recorded. The fix
  wants `size-adjust`/`ascent-override` tuned to Instrument Sans's real metrics, which
  cannot be guessed without measuring, and a decision about self-hosting.
- **`docs/programs` holds 64 payloads against 62 in the current generation.** The
  rolling window, as cycles 1–4 all established, and this cycle built four times.
  Verified rather than assumed: 3 generations retained at 62 files each, **0 orphaned
  and 0 missing**, the current generation covering 62 distinct courses.
- **No author file, no `catalog/*.json`, no lesson id and no schema was touched**, so
  `emit.py` was not run and the staleness guard is not armed. Presentation and behaviour
  only.

### Gates, after

Every pre-existing number unmoved. The only new numbers are the new gate's; the only
others that moved are the two artifact sizes, by the CSS, script and comments added.

```
verify_theme         All good: theme tokens (14 written exemptions) · 49 contrast
                     surfaces in both themes, tightest text 4.63:1, faintest state
                     1.11:1 · the 375px topbar (204.6px of furniture in 291px of bar,
                     86.4px for the title) · the 50px id column holds CTRL510, the
                     longest of 62 course ids · the closed drawer is out of the tab
                     order                                                      [NEW]
verify_derivations   All good: 1140 steps across 46 courses
verify_quiz          All good: 1366 questions in 252 quiz units · 160 per-option
                     explanations · every course within its answer-tell budget
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_labs MA101    All good: 5 labs
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads ·
                     inlined 13726 -> 13740 KB · shell 1089 -> 1103 KB, of 1536
```

Beyond the gates: every ratio in this entry computed from the WCAG 2.1 sRGB formula
against the composited stack rather than the ground; the 375px bar summed from fixed
CSS lengths with only two font advances involved, both the fonts' own published metrics;
the seven-character course ids counted from both spines rather than assumed; every band
tint checked to exist before `--tt` was made load-bearing; the band tint measured in
both themes *before* shipping, which is what stopped it; and the new gate run against
ten mutations it had to reject and one it had to pass.

---

## Cycle 6 — TRACK 6: Edge Cases, Resilience & Accessibility

**Target: the schematic editor's input, focus and lifetime layer.** `createCircuit`'s
interaction section in `src/circuit.js` — its pointer and key handlers, the toolbar and
panel DOM it owns, and its `dispose` — plus the three places in `src/app.js` that own
its lifetime (`renderBuild`, `renderNumeric`'s diagram, `renderCircuitPlayground`).

One subsystem, and the one this track was left. Cycle 2 took the sandbox half of the
canvas work and wrote down why it stopped: *"The circuit editor was not touched. It is
the other half of this track and its own cycle."* Nothing had audited it since. It is
also where a Track 6 defect costs the most: **80 circuit exercises are graded work**, and
a build unit is the only unit kind whose answer is a drawing.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1140 derivation steps across 46 courses
1366 questions in 252 quiz units · 160 per-option explanations
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
theme: 14 exemptions · 49 contrast surfaces x 2 themes · tightest text 4.63:1
build: 3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers · 3 tune models ·
       15 symbols · 62 payloads · inlined 13740 KB · shell 1103 KB
```

### The attacks

**4. UX & Accessibility Hardener** — taken first, because this track's brief is mostly
its brief.

- **The editor's keyboard shortcuts were on `document`, and one of them broke the space
  bar for the whole page.** `onSpaceDown` called `e.preventDefault()` on any Space
  keydown whose target was not an input or a textarea. A `<button>` is activated on
  *keyup*, and only if its keydown left it active — which the browser does in the
  keydown's default action. Cancel the keydown and the press is cancelled with it. So
  with a build exercise on screen, Space no longer worked on **"Check the circuit"**, on
  the footer navigation, on the icon rail, on anything inside the desk modal, and it no
  longer scrolled the 1200-word reading sitting above the canvas. Every one of the 80
  build units, and the circuit playground.
- **`Ctrl+A` was taken from the document, with `preventDefault`.** A lesson carrying an
  editor was a lesson whose text could not be selected — and the keystroke silently
  selected every part in a drawing somewhere down the page instead.
- **`R`, `G`, `U`, `Delete` and `Backspace` fired from anywhere outside an input.** Tab
  to the footer's "Next lesson" and press R and a part rotates. The desk modal is
  `aria-modal` and traps Tab, but its own key handler stops propagation for **Escape and
  Alt+K only**, so R, G, U and Delete all reached the canvas behind it.
- **The canvas took no keyboard focus at all, and the file said so twice** — *"Tracked
  on the document because the canvas does not take keyboard focus."* No `tabindex`, no
  role, no name. Placing a part needs a click at a grid cell and there was no other way
  to do it: **the 80 circuit exercises could not be sat with a keyboard.** That is the
  headline of this cycle. Everything else here is smaller than it.
- **Nothing announced.** `[data-out]` is filled with the entire answer — every node
  voltage, every branch current — with no live region and no name. `.ckt-err`, the
  sentence saying the circuit would not solve, was silent too. Cycle 2 gave the sandbox
  readout `aria-live`; the editor, which has far more to say, got nothing.
- **Eighteen tool buttons are named after their key caps.** `R`, `C`, `L`, `V`, `I`,
  `D`, `SW`, `NTC`, `LDR`, `POT`, `BAR`… the whole accessible name of each is its glyph.
  The full name was already there in the `title`, which a screen reader reads as a
  description and a keyboard user never sees at all.
- **`.on` and `.active` were the only record of which tool and which analysis mode were
  chosen** — a class is a fact about CSS, not a state anything can read.
- **The wiper slider announces 500 where the page reads 0.50.** `min=0 max=1000` for a
  0..1 quantity, no `aria-valuetext`. This is precisely the defect cycle 2 measured on
  the sandbox sliders, in the file next door, unrepaired.

**3. Simulation Auditor.** Pointed at what the persona brief actually asks for — zero,
negative, enormous and identical values, and whether the panel describes what the solver
does.

- **The value box was the one field on the panel with no clamp.** Two lines below it,
  every `[data-x]` field is held inside the range its kind declares:
  `Math.min(Math.max(isFinite(v) ? v : f[2], f[2]), f[3])`. The `[data-val]` box — the
  field *every* part has — was `p.value = parseEng(inp.value, p.value)` and nothing else.
  Type `0` into a resistor and the model takes 0. Type `-5` and it takes −5.
  And what shipped was worse than a crash, because every stamp already defends itself:
  `1 / Math.max(p.value, 1e-12)`. So the solver quietly treated the part as a **1 pΩ
  short** while the panel beside it went on reading −5 Ω, the canvas drew −5 Ω, and
  `onChange` wrote −5 Ω into `P.build[l.id]` and saved it. The learner's own stored
  circuit was the thing lying to them, and it survived a reload.
- **`spaceDown` had no way back if the window went away with the key held.** `onSpaceUp`
  was on the document; Alt+Tab sends the keyup to another window. The flag stayed true
  for the rest of the session, the cursor stayed `grab`, and the next plain left-click on
  the canvas panned instead of placing a part.
- **Checked and found sound, recorded so the next cycle does not re-derive them:**
  `zoomFit` cannot divide by zero — a single-point drawing still has `pad = 1.5` either
  side, so `needW ≥ 3 · GRID`. `parseEng` cannot return NaN; it falls back on both a
  failed match and a non-finite result, so the value box could reach 0 and negatives but
  never NaN. `paint()` already guards on `disposed`, and `perFrame` guards its callback —
  the discipline was there and only the leaked editor escaped it. The read-only path
  returns *above* the interaction layer, with a comment recording that an earlier version
  returned below it and clicking a question's schematic inserted a resistor into it; that
  fix is intact. Nothing in this subsystem animates on a timer, so
  `prefers-reduced-motion` has nothing to honour beyond the stylesheet's blanket rule,
  which already covers the one `.ckt-t` transition.

**1. Senior Educator** and **2. Assessment Inquisitor** have no prose and no graded
question in an editor, so both were pointed at the thing in scope they can judge:
whether the panel *explains* or merely *displays*.

- **The default panel hint described the mouse and only the mouse** — "Click the grid to
  place a resistor." — which was an accurate description of the whole interface and is
  the defect stated as a sentence.
- **A value silently corrected would be a correction the learner never learns from.** The
  clamp added below says what it did and why, rather than snapping the number back and
  leaving them to notice.

**The defect the personas found in the same file but a different subsystem**

- **The answer the editor exists to produce is 4.06:1 in the light theme.**
  `.ckt-tab td:last-child` — every node voltage and branch current — is `--lime` on
  `--surface`. So is `.ckt-panel h4` at 10px uppercase, and the wiper's own readout.
  Under the 4.5:1 floor for text, and exactly the trap cycle 5 minted `--accent-ink` for.
  Found by writing the editor's surfaces into `theme_budget.json` **as the stylesheet
  actually declares them** and letting the existing gate measure them — the first draft of
  those entries said `--accent-ink`, which would have been a budget describing a fix
  nobody had made.
- **`.ckt-tab td:first-child` was `--ink-5`**, the placeholder-and-disabled tier that
  cycle 5 measured at about 2:1 in both themes and moved `.rail-miss` off. This column is
  not a placeholder: it is the half of each row that says *which* node the volts belong to.

**The lifetime defect, which is a persistence defect**

`teardown` is a single slot, and `renderBuild`'s `paint()` is re-entrant — "Start over"
calls it. It assigned a second editor into that slot and **dropped the first on the floor
undisposed**: its `document` keydown listeners, its `ResizeObserver` and its model all
still live. Press "Start over" and then press `R` or `Delete`, and the abandoned editor
heard the key too, ran `doDelete` on a drawing nobody was looking at, and called
`opts.onChange` — which is the function that writes `P.build[l.id]` and calls
`saveSoon()`. **The stale copy saved itself over the learner's visible circuit.** Five
presses of "Start over" meant five stale editors and five writes per keystroke.

The discipline exists in the same file and reads, at `renderTune`:

> *paint() is re-entrant — Reset and Check both call it — so the previous observer has to
> go before a new one is made, or every press leaves one behind redrawing a canvas that is
> no longer on the page.*

Two renderers needed that line. One had it. `renderNumeric` needed it too — its `paint()`
runs again on Hint and on Check, leaking a read-only diagram's observer each time.

### What changed

**The keyboard moved onto the canvas, which is now a focus stop.** `tabindex="0"`,
`role="application"`, a name, and an `aria-describedby` pointing at the key map. Every
shortcut is bound to `cv` rather than to `document`, so a key with a meaning here has that
meaning while the caret is here and no other time. `Ctrl+A`, `Space`, `R`, `G`, `U`,
`Delete` and `Backspace` are all back in the page's hands everywhere else.

**The editor can be driven entirely from a keyboard.** A caret on the grid, moved by the
arrow keys and drawn as a ring with cross-hairs; `Shift`+arrow moves the selection, which
is the drag gesture without a pointer; `Enter` does what a click does — places the chosen
part, draws a wire between two presses, picks up what is under it, throws a switch, and
opens a block on the second press, which is what a double click is. `Escape` lets go and
then closes a block. The caret keeps itself on screen, so an arrow key can never walk it
out of the viewport. It survives tabbing to a value box and back, because typing a
resistance and coming back is one gesture. And it is drawn **only once a key has been
pressed**: clicking focuses the canvas, as it must or the tab order runs past the editor,
but a learner who has only ever used the mouse gets the canvas they had before.

The three gestures the pointer and the keyboard share are now literally the same code —
`wireAt`, `selectAt`, `placeAt` — rather than a near-miss of each other, so the
no-stacking rule and the orthogonal-wire rule are enforced once.

**It says what it did.** A `role="status"` region carries every action in a sentence:
the cell the caret is on and what is under it, what was placed and where, the wire's two
ends, how many parts were deleted, the angle after a rotation, the zoom, the tool that was
chosen — and the solve, which is the one message a learner is least likely to be looking
at because they pressed Solve and are watching the drawing. A repeated sentence is
re-stamped with U+200A rather than a plain space, since a trailing ordinary space is
collapsed out of the computed name and would change the DOM without changing the string.
The result table itself is a named `region` and *not* live: making it live would read every
node and every current on every solve.

**State that can be read.** `aria-pressed` on all 25 tool buttons, on the three analysis
modes and on the node picker; `aria-label` on every tool taken from the first clause of
its own `title`, so a name and a description that could drift apart do not exist;
`aria-keyshortcuts` on the five toolbar buttons that have a key; `aria-valuetext` on the
wiper; `role="img"` and a name on a question's read-only schematic, which had neither.

**The value box is clamped, and says so.** A `VALUE_FLOOR` table for the fifteen kinds
whose value is a quantity with no meaning at zero — resistances, a capacitance, an
inductance, a saturation current, a transconductance, an open-loop gain. `V`, `I` and
`BAR` are deliberately absent: a source may sit at zero and may be negative, and
superposition cannot be written without it. The floors are set far below anything a lesson
uses (a femtofarad, a picohenry, a micro-ohm) because the job is to reject the impossible,
not to police the unusual — checked against the catalogue: **975 parts of a floored kind,
none under its floor.**

**The lifetime.** The teardown flush added to `renderBuild` and to `renderNumeric`'s
diagram, with the reason written beside it. `dispose()` made idempotent and its window
listener released. And `changed()` now returns early when `disposed` — nothing can deliver
a key to a detached editor any more, but that makes it a rule rather than a consequence:
an editor that has been disposed can never reach `onChange`, which is the function that
saves.

**Contrast.** `.ckt-tab td:last-child`, `.ckt-panel h4` and the wiper readout to
`--accent-ink` (4.06 → 4.92:1 light); `.ckt-tab td:first-child` off `--ink-5` to
`--ink-3`; a `.ckt-vh` class for the key map and the status line — `clip-path`, not
`display:none`, which would take both out of the accessibility tree; and an inset focus
ring on the canvas, because `--editor` is dark in both themes and the page's own offset
ring sits outside the box.

**A new gate — `tools/verify_circuit_ui.mjs`.** This track had no gate at all, which is
why several of the defects above are years old. It does not judge the drawing: it mounts
**the real editor** and drives it. circuit.js touches no `document` — the whole editor is
built by assigning `innerHTML` to the root it is handed — so what the gate needed was one
element that parses HTML, answers the selector shapes this file uses, and delivers events
up a parent chain. That is written into the gate, because the repository has no
dependencies and this was not the place to start having them. Ten sections:

- **Keys stay put.** The ten shortcuts pressed at two kinds of "not the canvas": a
  detached button, which is every control in the shell and the footer and the desk; and
  the editor's *own toolbar*, which is the harder case, because a handler on the root, on
  the document or on the window would still hear it. Neither may move the model and
  neither may be `preventDefault`ed.
- **The canvas is reachable** — focus stop, role, name, and a description that resolves
  and actually names Arrow, Shift, Enter, Escape and Tab.
- **A circuit built by keyboard alone**, checked against the model at each step: the first
  arrow places nothing, Enter places one part of the chosen kind, a second Enter on the
  same cell refuses rather than stacks, R turns it a quarter, two Enters with the wire tool
  draw one wire, Shift+arrow with an empty selection refuses and moves nothing.
- **The caret is drawn, and only for the keyboard.** Frames are segmented on `clearRect`,
  so a focused frame and an unfocused frame of the same drawing can be compared: focused
  must carry more draw calls, and after a click back onto the canvas the two must be equal.
- **Space, both meanings** — the primary action when the pointer is away, the pan modifier
  when it is over the drawing, and claimed from the page in both cases.
- **Nothing it says contains NaN, undefined or Infinity.**
- **Every floored kind** fed `0`, `-5`, `-1e12`, `nonsense` and an empty box, with the
  model checked against the floor its own stamp needs — and the clamp itself checked to
  leave a negative voltage source and a zero current source alone.
- **Disposal** — the window listeners balance, a second dispose does not unbalance them,
  and a disposed editor cannot reach `onChange`.
- **The read-only diagram** is an `img` with a name, is *not* in the tab order, and draws
  no non-finite coordinate.
- **The call sites**, read out of `src/app.js` as source: every `createCircuit` is preceded
  by the teardown flush, or is `renderCircuitPlayground`, which is reachable only through
  `go()` and so is flushed by `go()` itself.

The gate was not trusted until it was seen to fail. **Fourteen mutations, fourteen
intended verdicts:** the keyboard put back on the window; the handler moved up to the
editor root, which only the toolbar half of section 1 can see; Space no longer yielding to
the pointer; the canvas out of the tab order; `changed()` free to write after dispose;
`dispose()` keeping its window listener; the value box unclamped; `aria-pressed` off the
buttons; the click handler no longer moving it; the tools named after their glyphs; the
caret never drawn; the caret drawn for a mouse user too; the status line silenced; and
`renderBuild` abandoning its editor again.

### Found in my own work, and fixed

- **A `let` in the temporal dead zone that would have broken every schematic in the
  catalogue.** I declared `caret` and `cvFocused` beside the key handlers, where they
  belong by subject, and read them in `paint()`. The read-only branch paints and returns
  about 2,300 lines *above* that declaration, so the first draw of every question's
  diagram would have thrown `Cannot access 'caret' before initialization`. Caught by
  asking what the read-only early return actually skips rather than by running anything —
  and then confirmed by the gate's read-only section. Both now sit with the editor's other
  state, with the reason written next to them.
- **The first mutation run reported a `TypeError` instead of the four defects it had
  already found.** With the keyboard back on the window the keyboard-build section threw,
  and the throw took the whole report with it. Each section now runs inside a wrapper that
  records falling over as a failure of its own — a gate that dies is not a gate that
  reports.
- **Two checks that passed for the wrong reason, both caught by mutation rather than by
  re-reading.** The Space-with-pointer test pressed Space twice on the *same* cell, which
  the no-stacking rule refuses anyway, so the part count would not have moved whatever the
  editor did. And the `aria-pressed` check asked only that exactly one button was `true` —
  a bar with one button in it — while twenty-four buttons carrying no `aria-pressed` at all
  say nothing about being off.
- **A frame counter off by one.** Frames are closed by the *next* `clearRect`, so every
  reading is taken one paint late. The first version compared a frame with itself and
  reported 595 against 595 for correct code.
- **A budget entry that described the fix instead of the stylesheet.** I first wrote the
  new `theme_budget.json` rows with `--accent-ink`, which is what they *should* say, and
  the gate duly reported 58 clean surfaces over a stylesheet that still said `--lime`. A
  gate enforcing a rule the source has abandoned is the failure this repository has already
  had once. Corrected to what the file declares; it failed at 4.06:1; then the CSS was fixed
  and the entry followed it.
- **A comment that had become false.** The key handler's `input|textarea` guard cannot fire
  now that the listener is on the canvas — a canvas has no focusable children. The comment
  still claimed the value boxes were what it was for. Rewritten to say plainly that it
  cannot fire today and why it is still there.
- **A caret that would have changed the editor for everyone.** The first version drew the
  ring whenever the canvas held focus, and clicking focuses the canvas — so every mouse
  click would have left a mark on the drawing. An accessibility cycle that changes what the
  other 99% see has traded one defect for another. Gated on a key having been pressed, and
  the gate now measures both directions.

### Left alone, deliberately

- **`renderCircuitPlayground` did not get the teardown flush.** It is reachable only
  through `go()`, which flushes the slot itself, so the line would be a defence against
  nothing — and the gate encodes that exemption by name rather than by silence, so if the
  playground ever gains a re-entrant `paint()` the exemption is the thing to delete.
- **The MCU sketch panel was not audited.** `paintMcu` is a code editor, a console and a
  fault report inside the side panel — its own subsystem, in `src/mcu.js` as much as here,
  and the only part of the editor with a second language in it. Nothing this cycle changed
  reaches it beyond the key scoping, which strictly helps: a sketch is a `textarea`, and
  the shortcuts that used to fire from anywhere outside one no longer fire at all.
- **`P.dim` at 2.93:1 and `P.faint` at 1.86:1 on the canvas.** Cycle 2 measured them and
  handed them to Track 5; cycle 5 re-measured and did not take them, leaving three
  candidate values. This is a Track 6 cycle and taking them would change the visual weight
  of 13 visualisers as well as this canvas. Still open, still recorded.
- **A negative resistance is now refused; a negative *voltage* is not, and should not be.**
  Recording the asymmetry because it looks like an inconsistency and is not: `V` and `I`
  carry a sign that means direction, and half the superposition material in the catalogue
  depends on being able to write it.
- **The marquee, the pan and the block breadcrumb have no keyboard equivalent.** `Ctrl+A`
  selects everything and Shift+click still builds a selection by hand, so the marquee is a
  convenience rather than the only route to anything; the caret scrolls the viewport itself,
  so pan is not needed to reach a cell; and the breadcrumb's buttons are ordinary focusable
  buttons. Worth having, not worth widening this cycle for.
- **No `emit.py` run and no author file, `catalog/*.json`, lesson id or schema touched.**
  Presentation and behaviour only, so the staleness guard is not armed.
- **`docs/programs` holds 64 payloads against 62 in the current generation.** The rolling
  window, as cycles 1–5 all established, and this cycle built four times. Verified rather
  than assumed: 3 generations retained at 62 files each, 64 files on disk, **0 orphaned and
  0 missing**, the newest generation covering 62 distinct course ids.

### Gates, after

Every pre-existing number unmoved. Two numbers moved by exactly what was added — the
theme gate's surface count, by the 9 editor surfaces written into its budget, and the two
artifact sizes.

```
verify_circuit_ui    All good: the editor answers 78 driven keys and gestures, says 10
                     things while doing it, keeps every shortcut inside its own canvas,
                     holds 15 kinds above the floor their stamps need, and disposes
                     without leaving a listener behind                            [NEW]
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_quiz          All good: 1366 questions in 252 quiz units · 160 per-option
                     explanations · every course within its answer-tell budget
verify_derivations   All good: 1140 steps across 46 courses
verify_labs EE131    All good: 10 labs
verify_theme         All good: 14 exemptions · 49 -> 58 contrast surfaces x 2 themes,
                     tightest text 4.63:1 · the 375px topbar · the 50px id column ·
                     the closed drawer is out of the tab order
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads ·
                     inlined 13740 -> 13776 KB · shell 1103 -> 1139 KB, of 1536
```

Beyond the gates: the new gate run against **14 mutations it had to reject and one it had
to pass**; the whole catalogue scanned for a value under the new floor — 975 parts of a
floored kind, 0 under; the payload window checked for orphans rather than assumed; and
every contrast figure in this entry computed by the existing theme gate from the
stylesheet's own tokens, not eyeballed.

**A note on this cycle's commits.** While it was running, a second session committed the
tree twice — `edfe4db` swept this cycle's `src/circuit.js`, `src/app.js` and
`src/index.head.html` under the label "cycle 5 (partial)", and `fa4d59b` swept
`tools/verify_circuit_ui.mjs` and `tools/theme_budget.json` in alongside its own
`src/mathinput.js`. Nothing was lost and every gate above was run on the tree as it stands
afterwards, but the history does not read the way the log does. Recorded so the next cycle
does not go looking for a cycle 6 commit that is not there. The curriculum's rule about two
writers is written for `emit.py --all` and `build.mjs`; it turns out to want saying about
`git commit` too.

---

## Cycle 7 — TRACK 1: Content & Conceptual Depth

**Target: MA101 (Discrete Mathematics), modules 2–6 — the proof core.** One course, one
contiguous block: predicate logic, methods of proof, sets, functions and pigeonhole,
induction. Each of the five held **a `quiz` and nothing else**, so a learner met the
quantifier, the contrapositive, the power set, pigeonhole and the inductive step as
bulleted claims and was examined on them in the next unit — which tests whether you
already knew. Cycle 4 built M12 and M13 onto this course and named the density pass as
its own cycle; this is it.

Chosen on measurement rather than on that pointer. Scoring all 62 courses by modules
holding neither a `read` nor a `derive` unit, MA101 led the catalogue with **11 of 13**,
at 1.54 units per module against EE101's 12.64. It is also a declared prerequisite of
CS201, CS301, CS310 and MA121, so the ratio is not a cosmetic one.

M1, M7, M9, M10 and M11 were excluded deliberately: the first four carry a full lab and
teach by construction rather than examining cold, which is cycle 1's MA111 reasoning
applied unchanged.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1140 derivation steps across 46 courses (MA101: 12)
1366 questions in 252 quiz units · 160 per-option explanations
     (MA101: 38 · longest-is-key 21, budget 21 · margin +20.6)
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
theme: 14 written exemptions · 58 contrast surfaces in both themes
MA101: 13 modules · 20 units · 2 read · 2 derive · 11 bare modules · 5 labs
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads ·
       inlined 13776 KB · shell 1139 KB
catalogue: 62 courses, 368 modules, 1873 units, 234 readings
```

### The attacks

**1. Senior Educator.** Six findings, all acted on.

- *Announced, never derived, five times over.* Fixed: five readings and five
  derivations, each deriving what its module states. The empty-domain convention comes
  out of a count of predicates rather than being adopted; the contrapositive is chosen by
  which end carries algebra; the power set is one independent decision per element, shown
  to be the same object as a truth-table row rather than a formula with the same value;
  pigeonhole is derived as the point where the injection count reaches zero; and the
  inductive step is shown to be worthless on its own.
- **Vacuous truth was presented as a convention adopted for tidiness.** M2's bullet said
  that on an empty domain `forall` is true and `exists` false, with the quiz explanation
  arguing it from an English sentence about resits. It is not a convention. On a domain
  of `n` elements a predicate *is* a subset, so there are `2^n` of them; `forall` holds
  of exactly 1 and `exists` of `2^n - 1`; at `n = 0` that is 1 of 1 and 0 of 1. The count
  was not arranged to produce the result and produces it anyway. Fixed in the bullet, the
  reading and the derivation.
- **The quantifier-order asymmetry had no size.** M2 said order changes the claim and
  gave the standard "everybody loves somebody". Nothing said *how much* it changes, so
  nothing ruled out the reading that it is a rare edge case. It is now counted: over a
  domain of size `n` there are `2^(n^2)` binary relations, `(2^n - 1)^n` satisfy
  `forall x exists y`, and `2^(n^2) - (2^n - 1)^n` satisfy `exists y forall x`. The gap
  is `2(2^n - 1)^n - 2^(n^2)` — **0 at `n = 1`**, which is why a single example never
  exposes the difference, 2 at `n = 2`, and 174 at `n = 3`. The two relations at `n = 2`
  are exhibited, and they are *everyone is related to themselves* and *everyone is
  related to the other one*. Recorded as an `n = 2` observation only: both are
  permutations, and that does **not** generalise — at `n = 3` the gap is 174 against 6
  permutations, and the reading says so rather than leaving the pattern to be
  extrapolated.
- **The course used a distinction in M13 that M3 never taught.** M13 proves an
  undecidable problem exists by counting and is careful to say it delivers no example.
  Nothing in *Methods of proof* had ever drawn the line between proving a thing exists
  and producing one, so the module that owed the distinction did not make it. Added as a
  bullet and worked in the reading, pointing forward to where the course spends it.
- **The `sqrt(2)` argument was never bounded.** Presented as the standard proof, with
  nothing saying what makes it work. It is now run a second time on `sqrt(4)`, which is
  rational, so it must fail: from `a^2 = 4b^2` the step you would like is *`a^2` divisible
  by 4 implies `a` divisible by 4*, false at `a = 2`, and putting `a = 2c` gives
  `b^2 = c^2` with no descent. The argument is about 2 being prime, not about roots.
- **Inclusion-exclusion's alternation was a pattern extended on faith.** M4's bullet said
  the correction "continues for three sets and beyond" with no reason attached. Derived:
  an element in exactly `j` of the sets is counted `C(j,1) - C(j,2) + C(j,3) - ...`
  times, and the binomial theorem on `(1-1)^j = 0` makes that exactly 1 for every `j` at
  once. One identity, checked once, rather than a patch reapplied per set.
- *Left alone:* M6's "induction can confirm a formula but never propose one" was already
  stated with its reason and its forward reference. The reading spends it rather than
  restating it, showing where the guess actually comes from — four computed cases and the
  L-shaped gnomon.

**2. Assessment Inquisitor.** All 20 questions across M2–M6 were checked against the
mathematics rather than skimmed. **Every key is correct**; every `why` walks the options;
none uses a positional reference. One repair, and it is a scope defect rather than a
wrong key:

- **M5/Q2 stated both one-sided inverses unconditionally.** "An injection has a left
  inverse and a surjection a right inverse" — the first fails for an empty domain, which
  is the case M2's own first question is entirely about, and the second is the axiom of
  choice once the codomain is infinite. Both conditions are now stated in the `why` and
  in the reading. The option text is untouched, so the course's answer-tell budget cannot
  move; confirmed by the gate, which reports MA101 unchanged at 38 questions,
  longest-is-key 21, margin +20.6.
- Recomputed rather than assumed, so the next cycle need not: 30 students with 18 and 15
  and 7 both leaves 4; `2^5 = 32` subsets against 32 truth-table rows; `ceil(1000/512) =
  2`; the ages map is a function and neither injective nor surjective; `S = {3,6,9,...}`
  under the recursive definition. All hold.

**3. Simulation Auditor.** M2–M6 contain no sandbox, tune, build or schematic `numeric`,
so there is no draw loop or solver in the target. The persona was pointed at the two
things in scope that no gate covers — **what the renderer actually draws**, and
**arithmetic in prose** — and the first is where this cycle's largest finding is.

- **`\tfrac12` does not draw as one half. It draws as "12".** `src/studio.js` tokenises
  `12` as a single number, so `\tfrac`'s first `group()` swallows it whole and the second
  takes whatever token follows. In MA101's M12 reading that put
  **`4 \times \tfrac14 = 1` on the page as `4×14=1`**, `4 \times \tfrac18 = \tfrac12` as
  `4×18=12`, and a derivation hint's `1 - \tfrac12 = \tfrac12` as `1-12=12`. Three false
  equations, rendering without error, in a module written to explain a bound. This is
  worse than a fallback, because a fallback at least shows its source: this silently
  shows a *different number*. **7 fragments in MA101, all repaired by bracing the
  arguments.** Catalogue-wide there are 161 more, listed below.
- **16 MA101 fragments rendered as raw LaTeX markup.** `MathML.render` returns
  `<code class="math-raw">` holding the source the moment it meets a command outside its
  subset, so it neither throws nor looks broken to any gate. Cycle 4's entry records
  checking that every equation is `$...$` or `$$...$$` — which is true, and is not the
  same as checking the renderer can draw it. `\mathbb`, `\lfloor`, `\rfloor`,
  `\underbrace`, `\Longrightarrow` and `\{` are all outside the subset. All 16 repaired
  in the supported subset: `\mathbf{N}` for `\mathbb{N}`, `\Rightarrow`, explicit
  parentheses for the harmonic blocks, code spans for set braces, and — for the floors —
  the exponentiation bound rewritten around `b`, the number of bits, which removes the
  floor entirely and is a shorter argument: `b <= log2 e + 1 <= 2 log2 e` for `e >= 2`,
  so the cost `2b` is at most `4 log2 e`. Verified over `e = 2..100000`.
- **My own five readings were written against the same check, not merely spell-checked.**
  The first draft of M2 used `\neg` and `\wedge` in six fragments, all of which would have
  shipped as raw markup. The module's own quiz already writes logic in code spans, so the
  reading now matches the module rather than importing a second notation. **MA101 now
  renders 962 of 962 fragments**, against 456 of 472 before.
- **Every number written into the five readings was computed before it was written** —
  the relation counts by brute force over all `2^(n^2)` relations for `n <= 4`, the
  three-language faculty checked for regional consistency as well as arithmetic (all
  seven regions non-negative, summing to 90), `5^5 = 3125` against `5! = 120` at 3.84%,
  the birthday probability at 23 people to four figures (0.5073), the alternating
  binomial sum for `j = 1..9`, and the handshake theorem by exhaustive search over every
  graph on up to 6 vertices.
- **Both code listings were extracted from the shipped JSON and executed**, not from the
  draft. M2's prints `1 1 1 0 1 1 / 2 9 7 2 9 7 / 3 343 169 174 343 169`, and M5's prints
  `None` on all five lines. Both match what the prose says they print, string for string.

**4. UX & Accessibility Hardener.** Content-side, as cycles 1 and 4 established. Checked
rather than assumed: `math[display=block]` carries its own `overflow-x:auto` and
`.article .tw` wraps tables in a scroller, both verified in `src/index.head.html`; no
hard-coded colour, no raw HTML and no wide table was introduced. The two fenced listings
are block markup `renderMd` draws, and each gets a **▶ Run** button from `mdCodeBlock`,
which for a self-contained listing that the prose makes a claim about is the right
behaviour — the learner can check the claim. Both were confirmed to run standalone with
only `itertools` imported, which is what the browser's Pyodide runtime has.

### The defect this cycle found beyond its own course

The two renderer failures are catalogue-wide, and both were measured rather than
estimated. Each command was probed on its own rather than inferred from a failing
fragment, because a fragment that fails names every command it contains and not the
offender.

**1053 fragments in 33 courses still render as raw markup** (down from 1069; MA101's 16
were this cycle's). **37 commands** are outside the subset, led by:

```
\top 237 · \mathcal 66 · \Longrightarrow 61 · \big 30 · \bmod 15 · \bigl/\bigr 12
\displaystyle 11 · \binom 9 · \lceil/\rceil 9 · \lfloor/\rfloor 6 · \underbrace 6
\boldsymbol 5 · \succeq 5 · \lVert/\rVert 3 · \blacksquare 2 · \boxed 1 · \pmod 1
```

**161 fragments still draw a fraction as a single wrong number** (down from 168):
EE211 57, EE111 32, MA112 22, EE102 22, EE141 12, MA111 6, EE231 4, EE121 3, EE131 2,
EE101 1. `MA112/M1` has `\int_0^1 x^2\,dx = \frac13` drawing as `= 13`.

**Not fixed here, and the reason is scope.** Both are repairable two ways: additively, by
extending the tables in `src/studio.js` — which is provably safe, since a command that
currently reaches `default: fail()` can only start succeeding — or by rewriting 1214
fragments across 33 courses. The first is Track 2/5 machinery touching every rendered
fragment in the app; the second is a whole-catalogue content sweep. Either is its own
cycle, and burying either inside a Track 1 content cycle would make this diff
unreviewable — which is cycle 4's reason for reverting the 41-file `check` drift, applied
unchanged. What this cycle owed was its own course, and MA101 is now clean on both
counts. The measurement is written down so the next cycle starts from it. **The
`\frac13` one should go first**: a fallback shows its source and looks broken, while a
swallowed fraction shows a plausible wrong number and does not.

### What changed

**Ten new units in five modules** — one `read` and one `derive` each.

| Module | Reading | Words | Derivation | Steps |
|---|---|---|---|---|
| M2 | What a quantifier is quantifying over | 1490 | Counting the models, and pricing the order of two quantifiers | 6 |
| M3 | Choosing the technique by what it hands you to work with | 1310 | The parity of a square, the descent that proves an irrational, and where it stalls | 6 |
| M4 | Membership is the only primitive, and counting is what it costs | 1315 | From one decision per element to the alternating correction | 6 |
| M5 | One value out, and what happens when there is not enough room | 1438 | Injections, counted until there are none left | 6 |
| M6 | The first domino, and the rung nobody checked | 1299 | Two obligations, and what happens when you discharge only one | 6 |

6852 new words, every reading inside the 1200–2500 target and in line with M12 and M13
(1631, 1516). MA101: 20 units → 30, 2 readings → 7, 11 bare modules → 6.

**Eleven concepts bullets added or repaired** across M2–M6, so the new material is
reachable from the bullet list a learner skims rather than only from the reading: the
empty-domain count, the sized quantifier gap, the negation law behind counterexamples,
contradiction's failure to construct, the `sqrt(4)` boundary, the binomial identity under
inclusion-exclusion, the finiteness of all the counting in M4, pigeonhole as a count
reaching zero, certainty against likelihood, the horses' overlap at `k = 1`, the `c` that
survives every inductive step, and induction's dependence on the naturals' structure.

**Worked examples that end in checked numbers rather than in results:** the two relations
that separate `forall exists` from `exists forall` at `n = 2`, exhibited as grids; the
`sqrt(4)` descent stalling at `b^2 = c^2`; Euler's polynomial prime for `n = 0..39` and
`1681 = 41 x 41` at 40, with `n^2 + n` proved even by cases so the polynomial is always
odd; a faculty of 100 where `60+45+30-25-15-10+5 = 90` and an element in exactly `j` sets
is counted `3-3+1 = 1` time; 3125 functions against 120 injections; 512 buckets holding
at most 512 keys against 1000; and `S(n) = n(n+1)/2 + 5` surviving a flawless inductive
step while claiming `1 + 2 + 3 = 11`.

### Found in my own work, and fixed

- **A code listing's docstring closed the reading it was inside.** The M5 listing opened
  with a `"""..."""` docstring, inside a Python `r"""..."""` body — so it terminated the
  string and `emit.py` failed on a syntax error 200 lines further down. Caught by the
  emitter, not by reading. The docstring is a `#` comment now.
- **Six fragments of my own M2 would have shipped as raw markup**, for exactly the reason
  the persona section above describes. Caught by running the renderer over the draft
  rather than by trusting that `$...$` is enough.
- **I reported a hedge-word count from a truncated run.** An early `| head -80` cut the
  survey off, and I read its last line as the total: 5, when the file had 9. Corrected by
  diffing the working tree against `HEAD` instead of counting twice — **9 at HEAD, 9 now,
  0 introduced by this cycle**, all in modules this cycle did not otherwise touch.
- **I concluded no gauntlet was running by grepping for the wrong filename.** The lock is
  `.gauntlet.pid`; I searched for "lock", found nothing, and ran `node build.mjs` on that
  basis. A run *was* live (pid 5975, started 07:31). See below.

### Left alone, deliberately

- **M1, M7, M9, M10 and M11 still have no reading.** M1, M7, M9 and M10 each carry a full
  lab and teach by construction; M11 holds a lone quiz and is the one genuine remaining
  instance of the defect this cycle was chasing. Six bare modules remain against eleven.
  They should get readings, and that is the next Track 1 cycle on this course, not a
  widening of this one.
- **The 20 existing questions in M2–M6 were audited and, apart from the M5/Q2 scope
  repair, not changed.** They are Track 3's ground, and MA101's inherited answer-tell debt
  (21 of 38, pinned by `quiz_budget.json`) is cycle 3's recorded debt rather than this
  cycle's to spend.
- **1053 raw-markup fragments and 161 swallowed fractions outside MA101**, measured above
  and handed on with the numbers rather than the symptom.
- **`\mathbf` emits a duplicate attribute.** `<mi mathvariant="normal" mathvariant="bold">`
  — `studio.js`'s `variant.replace(' mathvariant="normal"', '')` strips from the wrong
  string, so browsers take the first attribute and bold never applies. Harmless here, since
  an upright `N` is correct typography for a number set, and it is a one-line fix in a file
  this cycle should not be editing. Recorded with the line.
- **`verify_derivations.py` still proves translation rather than truth**, as cycle 1
  established — its checker computes `simplify(together(expr - expr))`. So all 30 new
  answers were truth-checked separately, each against an independently derived expression,
  and the harness is in this session's scratchpad. Nothing about the gate was changed:
  rewriting the spec from inside a cycle it governs remains the wrong move.
- **`docs/programs` aged out one MA101 payload and gained one.** The rolling window, as
  cycles 1–5 all established. Verified rather than assumed: 3 generations of 62 retained,
  64 files on disk, **0 orphaned and 0 missing**, the current generation covering 62
  distinct courses.

### Two sessions were writing this repository at once

Recording it because it affects how this entry should be read, and because the memory
that describes the runner is now wrong.

`marathon-gauntlet.sh` no longer runs its cycles without permissions — it passes
`--permission-mode acceptEdits` and gates on a write-and-execute preflight. So a headless
cycle **can** now write the repo and run the gates, and one was live throughout this one
(pid 5975 from 07:31, with its `claude` child at 07:31:30). Two further consequences,
both visible in the tree: commit `b6f8c26` landed mid-cycle from another session and
changed `src/`, and the runner's post-cycle step is `git add -A`, so it commits whatever
is in the working tree under its own track's label — which is how `edfe4db` came to sweep
another session's `circuit.js` under "cycle 5 (partial)".

Nothing here was lost or corrupted: the catalogue diff is `catalog/MA101.json` and
`catalog/authors/MA101.py` and nothing else, and every gate below was run against the
tree as it stands, after `b6f8c26`. The artifact attribution is clean too — MA101's JSON
grew 180.0 KB → 240.9 KB, and the inlined artifact grew by exactly the same 60 KB, so the
2 KB of shell growth is the other session's `src/` change rather than this cycle's.

### Gates, after

Every pre-existing number unmoved. One number moved, by exactly what was added.

```
verify_derivations   All good: 1170 steps across 46 courses   (1140 + 30 new;
                     MA101 12 -> 42)
verify_quiz          All good: 1366 questions in 252 quiz units · 160 per-option
                     explanations · every course within its answer-tell budget
                     (MA101 38 · longest-is-key 21, budget 21 · margin +20.6 — unmoved)
verify_labs MA101    All good: 5 labs   (M1 7/7, M7 7/7, M9 7/7, M10 8/8, CAP 12/12)
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_theme         All good: 14 exemptions · 58 contrast surfaces in both themes ·
                     the 375px topbar · the mobile drawer
emit.py MA101        ok — 13 modules, 4 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads ·
                     inlined 13776 -> 13836 KB · shell 1139 -> 1141 KB
catalogue            62 courses, 368 modules, 1883 units, 239 readings
```

Beyond the gates: every MA101 math fragment rendered through the real `MathML.render`
from `src/studio.js` — **962 of 962**, against 456 of 472 at baseline — and every
fraction checked for a swallowed argument, 0 remaining against 7; all 30 derivation
answers truth-checked against independently computed expressions rather than against
themselves; every number in 6852 new words recomputed before it was written; both code
listings extracted from the shipped JSON and executed against every output they claim;
all 15 `Module N` references in the new prose resolved against the real module titles;
0 hedge words introduced, confirmed by diff against `HEAD` rather than by counting; and
the payload window verified at 0 orphaned, 0 missing.

---

## Cycle 8 — TRACK 2: Interactive Models & Visualisers

**Target: the schematic editor's numerical core — `MNA` in `src/circuit.js`, the panel
that feeds it and the plot that draws its answer.** One subsystem, and the one this
track was left. Cycle 2 took the sandbox half of the canvas work and wrote down why it
stopped there. Cycle 6 took the editor's *input, focus and lifetime* layer and said in
its own gate's header that it "does not judge the drawing". So the solver has two gates
already and neither of them asks this track's question: `verify_circuits.mjs` asks
whether each exercise's reference drawing passes its own checks, `verify_numeric.mjs`
whether a stated answer matches the solver, and both feed it the values an author chose.
Nobody had ever fed it **zero, negative, enormous and identical values, resized it
mid-interaction, or clicked faster than it could re-solve** — which is the persona brief
for this track, almost word for word.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1170 derivation steps across 46 courses
1366 questions in 252 quiz units · 160 per-option explanations
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui: 78 driven keys and gestures · 10 things said · 15 floored kinds
theme: 14 exemptions · 58 contrast surfaces in both themes
build: 3 parts / 111 keys · 32/32 + 30/30 · 13 visualisers · 3 tune models · 15 symbols ·
       62 payloads · inlined 13836 KB · shell 1141 KB
```

### The attacks

**3. Simulation Auditor** — taken first, because this is its track and its brief.

- **An answer of NaN, reported as a success — and on the branch every published
  schematic is on.** `src/circuit.js` opens by promising that *"an iteration that does
  not settle says so and returns no numbers at all"*. The Newton path keeps that promise:
  `allFinite()` guards every pass, because a device driven far enough produces a
  non-finite guess routinely. The **linear** path never had the check. The mechanism is
  one line in `Lin.solve`: the pivot test is `if (best < 1e-14) return null`, and
  `NaN < 1e-14` is **false**, so a matrix that has overflowed sails straight through the
  test written to catch a matrix that is degenerate. Measured: a capacitance of 1e308 F
  gives a transient of **900 non-finite samples out of 901** with no error at all, and an
  AC sweep of **220 non-finite points out of 220**; an inductance the same; a current
  source at 1e308 A puts **2 of 4 numbers** non-finite in a *DC operating point*. In every
  case the panel announced "Transient run finished over 2 nodes" and the plot drew
  nothing. Worse than nothing: the node the supply holds up still drew a **convincing
  flat 5 V line**, because its value comes out of the voltage source's own row, so the
  learner sees a plausible trace, switches to the other node, and finds an empty box with
  no explanation anywhere.
  The guarded path turned out to be the one **nobody** is on. Counted rather than
  assumed: of 80 build exercises and 376 published schematics, **zero** contain a diode,
  an LED, a bipolar, a MOSFET or an op-amp. Every published schematic in the repository
  is linear and takes the unguarded branch.
- **A clamp with one end.** Cycle 6 gave the value box a floor, because a resistance of
  zero was being stamped as a 1 pΩ short while the panel read 0 Ω. It never gained a
  ceiling — `clampValue` was `return v < floor ? floor : v` — so the other end of the same
  field was wide open. `parseEng('1e308')` returns 1e308, `clampValue` passes it through,
  and it is drawn, written into `P.build[l.id]` and reloaded. The stamp is not the value
  but something *built* from it: a capacitor's companion conductance is `C/h`, so it
  leaves double precision at a capacitance the box was perfectly happy with.
- **A sweep from a frequency to itself.** The From and To boxes are clamped one at a time
  (`Math.max(0.01, …)`, `Math.max(1, …)`) and **never against each other**. From = To ran
  220 points at one frequency and handed the plot `xRange: [1000, 1000]`, on which
  `Sandbox.frame`'s `fx` divides by `log10(x1) − log10(x0)` = 0: every gridline, every
  tick label and the whole curve map to NaN and are silently not drawn. Measured through
  the real editor: **18 non-finite coordinates**, first `moveTo(NaN, 12)`, under a status
  line saying the sweep had finished. Six more degenerate ranges reach the same place —
  To below From, From at zero, a negative From, To at infinity, and a From that did not
  parse.
- **Five floors that are not the floor their own stamp needs.** Cycle 6's table is
  described as "checked against the floor its own stamp needs", and for `R`, `C` and `L`
  it is. For the five kinds whose resistance is *resolved* rather than typed it is not:
  `ohmsOf` holds a lamp at 1 mΩ and a meter at 1 µΩ, `potSplit` holds a track at 1 mΩ per
  half, and `Sensors` holds both `R10` and `R25` at 1 Ω — while the table let all five
  down to a micro-ohm. Measured at each declared floor: an **LDR and an NTC are stamped
  at 10⁶ times** the number on the panel, a **POT at 2×10³**, a **LAMP and a METER at
  10³**. That is precisely the defect the floor was minted to close — the panel reading
  one number and the solver using another — surviving in a third of the kinds the table
  was written for.
- **Checked and found sound, recorded so the next cycle does not re-derive them:**
  `perFrame`'s coalescing is real — 60 wiper events fired inside one frame queue exactly
  **one** re-solve, and a solve queued before `dispose()` does not run afterwards, so it
  cannot reach `onChange` and write the learner's saved circuit. The cost it is
  protecting is small anyway: the largest circuit in the catalogue (EMAG510/M1, 18 parts,
  6 nodes) takes 0.44 ms for a DC point, 2.6 ms for a 220-point sweep and 17.0 ms for a
  901-step transient, so even the worst case is inside one frame. `MNA.tran`'s
  `MAX_STEPS` coarsening is unreachable from the editor, which always asks for
  `tstop/900` and therefore always gets 900 steps. The `ResizeObserver` observes
  `.ckt-canvas`, not `.ckt-plot`, so the plot's own sizing cannot feed back into it.
  `modelNote`'s stated models agree with the code exactly — the LDR's `R = R₁₀·(10/E)^γ`,
  the NTC's `R = R₂₅·exp(B·(1/T − 1/298.15))` with T in kelvin — and both quote the
  computed resistance rather than the formula's value, so neither can drift. Only one
  catalogue check calls the solver directly (an `MNA.dc` in EE231) and **nothing** calls
  `MNA.ac`, so changing `acAt`'s failure path could not reach graded content.

**4. UX & Accessibility Hardener.**

- **The plot is 16px wider than its box, at every viewport size.** `paintPlot` measured
  `plotCv.parentElement.getBoundingClientRect()`, and under the global
  `*{box-sizing:border-box}` a parent's rect **includes** `.ckt-plot`'s 8px of padding on
  each side. So the canvas was set to the padded width and then set to that same width in
  CSS pixels, and `.ckt{overflow:hidden}` clipped the difference off the right-hand end of
  every trace and the axis label with it. Measured at five widths: 1200 asked of 1184,
  900 of 884, 640 of 624, **375 of 359**.
- **The plot is the only canvas left in the app with no accessible name.** Cycle 2 gave
  every sandbox canvas `role="img"` and a label; cycle 6 gave the schematic canvas a role
  and a name and gave a question's read-only diagram both. The plot — the entire output of
  a frequency sweep or a transient run, and the only place those answers exist — was a
  bare `<canvas>`, which a screen reader announces as nothing at all.
- **The picker and the plot disagreed about which node was on screen.** `paintPlot`
  clamps with `Math.min(analysis.node, nodeCount − 1)` for its own use; the buttons compare
  `n === analysis.node` un-clamped. Pick node 3, edit the circuit down to two nodes, solve
  again: the plot silently falls back to node 2 and labels itself "V at node 2", while
  **none of the two buttons is `aria-pressed="true"`**. Driven through the real editor with
  the keyboard cycle 6 built, and that is the number the gate reports: 0 of 2.
- **Two of the three analysis boxes corrected silently.** Typing 0 into From made it 0.01
  with nothing said, which is exactly the correction-nobody-learns-from that cycle 6
  minted the value box's announcement for.

**1. Senior Educator** and **2. Assessment Inquisitor** have no prose and no graded
question in a solver, so both were pointed at the thing in scope they can judge — whether
what the panel says **explains** or merely **reports**. The existing failure messages set
the standard (`stalled` names the node still moving and by how much; `blewUp` names the
diode across a supply). The three new ones are written to it: the overflow message says
*why* a capacitance overflows before its own value does (the companion model divides it by
the time step), the AC one says why a sweep can overflow at its top end and be well behaved
at its bottom (an admittance is `wC`, so it is the frequency and the reactance *together*),
and the range refusal says why a logarithmic axis has no room between a frequency and
itself. The value box's correction now says **which end** was hit and why that end is
there, rather than "out of range".

### What changed

**The solver vouches for every number it hands back.** `iterate`'s linear branch gains the
`allFinite` check the Newton branch has always had, and `acSolve` — extracted from `acAt`
so a sweep can report a cause while `acAt` keeps the vector-or-null shape catalogue checks
call — gains it too. Three exits, one rule: an analysis either refuses, or every number in
what it returns is one a plot can draw. There is no third answer, and "success, with NaN in
it" was the third answer for as long as the linear path had no check.

**`VALUE_CEIL`, and five floors moved onto their own resolvers.** Seventeen kinds now have
a ceiling, set far above anything a lesson uses — the largest of each kind in the whole
catalogue is 9 MΩ, 20 F, 15 H, 230 V and 25 A, so every ceiling has five orders of headroom
or more. `V` and `I` are in the ceiling table and deliberately not in the floor one: a
source's sign is its direction and half the superposition material depends on being able
to write it, while none of it depends on being able to write 1e308 V — so the ceiling is on
the **size** and a −230 V supply is still a −230 V supply. The five resolved kinds move to
the number their own resolver will honour: LDR and NTC to 1 Ω, POT to 10 mΩ, LAMP to 1 mΩ,
METER to 1 µΩ. None of the five appears anywhere in the catalogue, so no published content
could move.

**The analysis panel is held at both ends and says when it corrects.** One table for the
three boxes, with the floors kept to the number they already were — 0.01 Hz, 1 Hz and 1 ns
— because a floor that moved would be a behaviour change this cycle was not asked for, and
the defect was never at that end.

**A range that is not a range is refused rather than drawn.** `MNA.ac` requires two finite,
positive, *different* frequencies in increasing order, and at least two points, and says
which box is wrong when it refuses.

**The plot.** Measured from its own box rather than its parent's, with the stylesheet
stretching it (`width:100%; min-width:320px`) and JS setting only the backing store — CSS
owns the layout or the next resize measures the last one's answer and the canvas can never
shrink again. `role="img"` and a name rewritten on every repaint out of the same arrays the
curve is drawn from: *"Frequency response at node 2, 220 points from 10 Hz to 1 MHz. −0.0 dB
at the bottom, −40.0 dB at the top, highest −0.0 dB at 10 Hz."* And `analysis.node` clamped
where it is **stored**, so the picker and the plot agree by construction rather than by
both happening to do the same sum.

**A new gate — `tools/verify_circuit_model.mjs`.** Eight sections, and it drives the real
editor rather than a copy of it:

- **The extremes grid.** Eleven kinds × eleven values (0, −5, −1e12, 1e-30 … 1e308) × three
  analyses, plus identical values — two equal supplies across one pair of nodes, a divider
  of two equal halves — plus the Newton path at the same extremes, plus every span the
  panel accepts at both ends. Every one must refuse or return only finite numbers.
- **A range that is not a range**, seven ways, and three legitimate sweeps that must still
  run, so the check could not have "fixed" the defect by refusing everything.
- **The clamp at both ends**, over the union of the floor and ceiling tables so `V` and `I`
  are not skipped, with the sign required to survive the ceiling — and the whole catalogue
  swept against both, because a ceiling below what published content uses would condemn
  working content, which is worse than the defect it was written to catch.
- **The panel and the stamp agree**, asked of each resolver at its own reference point —
  10 lx is the light an `R10` is quoted at, 25 °C the temperature an `R25` is — where the
  model is the identity, so anything but the value back is a guard biting. Plus one end to
  end: a lone resistor across 5 V must pass 5/R at the floor, at 1 kΩ and at the ceiling.
- **The correction says which end.**
- **What the plot actually draws**, on a recording canvas that objects to any non-finite
  coordinate, in both modes, with the name required to describe the plot on the screen.
- **The picker and the plot**, by building a circuit, choosing its highest node, deleting
  two resistors **through the keyboard** and solving again.
- **Resize**, at 1200, 900, 640, 375 and 320px, and the schematic at 343px.
- **Faster than it can re-solve**: 60 wiper events inside one frame, and a re-solve queued
  before dispose.
- **The whole catalogue**, all three analyses: 376 published schematics, 355 of which reach
  a DC operating point, as the regression net that would show a fix turning working content
  into a refusal.

The gate reads `.ckt-plot`'s padding and its canvas rule **out of the stylesheet** and
refuses to run if either has changed shape, rather than modelling a browser's layout from a
constant it invented. A gate enforcing a rule the source has abandoned is a failure this
repository has already had once.

**The DOM stub is now one file, `tools/dom_stub.mjs`.** Two gates drive the same editor,
and two stubs would drift — which would mean two different editors being tested and neither
of them the one that ships. Extracted from `verify_circuit_ui.mjs` unchanged; that gate's
report is byte-identical before and after, checked by diff rather than by reading.

### Verification beyond the gates

**The gate was not trusted until it was seen to fail. Fourteen mutations, fourteen intended
verdicts:** the linear path's check removed; the AC point's check removed; the range guard
disabled; the value ceiling removed; a ceiling set below what the catalogue already uses;
`paintPlot` measuring its parent and writing its own width again; the node clamp removed;
`perFrame` giving every event its own solve; the dispose guard removed from the queued
callback; the five sensor floors put back under their own resolvers; the plot's name
suppressed; the correction choosing its end by comparing magnitudes; the stylesheet no
longer stretching the canvas; and the unmodified tree as a control.

Every defect above was measured before it was fixed and re-measured after: the 900 of 901,
the 220 of 220, the 2 of 4, the 18 non-finite plot coordinates, the 16px at five widths, the
10⁶/2×10³/10³ stamp factors, and the 60-events-to-one-solve. The catalogue's own value
extremes were surveyed before a single ceiling was chosen, and the count of non-linear
published schematics was taken rather than estimated — which is how the first draft of the
comment saying "78 of the 80" became "every one of the 376", the defect being larger than
first written.

### Found in my own work, and fixed

- **A correction that told the truth about the wrong end.** The value box's new sentence
  chose between "has to be more than zero" and "too large for the arithmetic" by comparing
  `|want|` with `|clamped|` — so **−5 Ω**, whose magnitude is larger than the floor it lands
  on, was told it was too big for the solver to hold. The end that was hit is a fact about
  the ceiling, not about the two numbers. Fixed, and the gate gained a section that types
  `-5`, `0` and `1e308` into a real value box and reads the announcement back.
- **A ceiling with the floor's defect wearing the other hat.** I set `VALUE_CEIL.LDR` to a
  terohm; `Sensors.ldr` caps its own result at a gigohm. So the box would have accepted a
  terohm and the stamp used a gigohm — the same panel-says-one-thing failure I had just
  spent the section fixing, introduced at the opposite end. **Found by the gate on the first
  run of the check written for the floor**, which is the argument for writing a check as a
  rule rather than as a list of the cases already known to be wrong.
- **A comment I closed one paragraph early**, leaving three lines of prose loose in the
  middle of a function. Caught by re-reading the block after the edit rather than by
  `node --check`, which parsed it happily because the stray lines sat inside the following
  string concatenation.
- **A false count in a comment I had just written.** "78 of the 80 published exercises are
  linear" was an estimate dressed as a number. Counted: 80 of 80, and 376 of 376
  schematics.
- **A test circuit that could not ask its own question.** The picker section's chain joined
  its resistors with wires, so deleting two of them left a wire that was a node with nothing
  on it — which the solver correctly refuses, and the gate reported that refusal instead of
  the defect it was built to find. Rebuilt pin-to-pin with no wire between the parts.

### Left alone, deliberately

- **Not one published schematic uses a non-linear device.** All seven — D, LED, NPN, PNP,
  NMOS, PMOS, OPAMP — and the sensor and instrument kinds beside them (SW, LDR, NTC, POT,
  LAMP, METER) appear in **zero** of the 376 catalogue schematics. Cycle 0 built the
  Newton-Raphson loop and 14 placeable kinds; the whole of it is reachable only from the
  Playground and from a learner's own drawing. That is a large piece of working machinery
  no lesson spends, and it is a breadth debt rather than a defect — Track 4's ground, and a
  content cycle, not a widening of this one. Recorded with the count so the next cycle
  starts from it rather than rediscovering it.
- **`P.dim` at 2.93:1 and `P.faint` at 1.86:1 on every canvas.** Cycle 2 measured them and
  handed them to Track 5; cycle 5 re-measured and did not take them; cycle 6 recorded them
  again. This cycle adds one more instance to the list — the plot's own axis labels, "dB at
  node 2" and "Hz", are drawn in `P.faint` — and takes them no further, for the same reason:
  changing them changes the visual weight of 13 visualisers and the schematic canvas as
  well, which is a decision about the design language.
- **`Sensors.ldr` clamps its result to 1 GΩ and `modelNote` does not say so.** The note
  quotes `ohmsOf`'s computed value, so the **number** is always the number the solver uses;
  it is the formula line beside it that describes the unclamped model. Only reachable at a
  small `R10` under bright light, and fixing it means putting a caveat on a sentence whose
  whole value is that it is short. Recorded, not changed.
- **The MCU sketch panel was not audited**, as cycle 6 also left it. `paintMcu` is a code
  editor, a console and a fault report, and it is its own subsystem in `src/mcu.js` as much
  as here. Nothing this cycle changed reaches it: the analysis clamps are on the three boxes
  the panel owns, and the solver changes it shares are the ones that stop it being handed
  NaN.
- **`MNA.tran`'s `MAX_STEPS` coarsening still says nothing when it bites.** It cannot bite
  from the editor, which always asks for `tstop/900`. Left as a latent issue with the reason
  written down rather than defended against a caller that does not exist.
- **The plot's name is not a live region**, deliberately. It is a picture, and a picture
  that announced itself on every frame of a dragged slider would be unusable. The status
  line already carries the event; the name is there for someone who goes to the plot.
- **No `emit.py` run, and no author file, `catalog/*.json`, lesson id or schema touched.**
  Presentation, behaviour and gates only, so the staleness guard is not armed — and the
  payload total is unchanged at 12666 KB, which is the mechanical confirmation that no
  content moved.
- **`docs/programs` was not touched at all this cycle.** Verified rather than assumed: 3
  generations retained naming 64 files, 64 payload files on disk, the current generation
  referencing 62 covering 62 distinct courses, **0 orphaned and 0 missing** — and `git
  status` reports no change under `docs/programs`, because no course's JSON moved.

### Gates, after

Every pre-existing number unmoved. The only new numbers are the new gate's; the only two
that moved are the artifact sizes, by exactly the source that was added.

```
verify_circuit_model All good: 1445 analyses vouch for every number they return and 84
                     refuse rather than guess · 15 plots and repaints, none unpaintable ·
                     the clamp holds 15 kinds off a floor and 17 under a ceiling ·
                     376 published schematics, 355 with a DC point, all three ways  [NEW]
verify_circuit_ui    All good: 78 driven keys and gestures, says 10 things while doing it,
                     keeps every shortcut inside its own canvas, holds 15 kinds above the
                     floor their stamps need, disposes without leaving a listener behind
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_quiz          All good: 1366 questions in 252 quiz units · 160 per-option
                     explanations · every course within its answer-tell budget
verify_derivations   All good: 1170 steps across 46 courses
verify_theme         All good: 14 exemptions · 58 contrast surfaces in both themes ·
                     the 375px topbar · the mobile drawer
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12666 KB — unchanged ·
                     inlined 13836 -> 13849 KB · shell 1141 -> 1154 KB, of 1536
```

Beyond the gates: the new gate run against **14 mutations it had to reject and one it had
to pass**; `verify_circuit_ui.mjs` reporting byte-identically before and after the stub was
extracted out from under it, checked by diff; the catalogue swept for every part value
before a ceiling was chosen and for every non-linear device before the claim about the
linear branch was written; and the payload window checked for orphans rather than assumed.

---

## Cycle 9 — TRACK 3: Question Bank & Quizzes

**Target: the `blanks` unit kind — the one graded surface in the repository with no
gate — and EE211 (Signals and Systems), the course that most exposes it.** One
subsystem and one course, which is cycle 3's shape: that cycle gave `quiz` its
per-option explanations and its per-learner shuffle, and rebuilt CS201 on top of them.
This one does the same for the kind next door, and the reason it needed doing is that
cycle 3 explicitly looked at a blanks bank and concluded it was safe.

Chosen on measurement rather than taste. Three numbers picked it out.

*Nothing was watching it.* `verify_quiz.mjs` iterates `m.quiz` and stops. **1103 graded
holes in 217 blanks units across 47 courses** — 4327 options, 1103 explanations —
were checked by nothing at all: not for a duplicate option, not for a positional
reference, not for markup the renderer cannot draw, not for the answer tell the quiz
half of that gate exists to measure. This is the "a gate that skips what it did not
expect is worse than no gate" invariant, in the file that enforces it.

*Press the first button.* The options were drawn in the order they were authored and
never shuffled, and the answer to **735 of the 1103 (66.6%)** is the first one. Guessing
is 25.8% on this bank (1043 four-way holes, 35 three-way, 25 two-way). **26 courses are
at 100%**, covering 350 holes:

| course | first-option | course | first-option |
|---|---|---|---|
| **EE231** | **89 / 89** | CS210 | 16 / 16 |
| **EE131** | **65 / 65** | EE241 | 11 / 11 |
| CS301 | 20 / 20 | MA101, CTRL530, VLSI530 | 10 / 10 |
| CS101 | 19 / 19 | …and 18 more | all of them |
| EE141 | 51 / 61 (84%) | EE102 | 75 / 102 (74%) |

Cycle 3 built `quizSeed()` because the quiz order "was identical for every learner on
earth and publishable as a list of letters that stays correct forever". The same
sentence was true of the blanks bank the whole time, and the same cycle audited CS201's
26 blanks by hand and wrote that they were "not exploitable — a blanks unit is graded as
six holes together". That is true of CS201, whose key is first 5 times in 26. It is not
true of EE231, where a learner who presses the top option 89 times finishes the course's
entire fill-in bank at 89 out of 89. **A hand audit of one course cannot see a tell that
is a property of the bank**, which is the argument for the gate rather than against the
audit.

*Half a course explains itself and half does not.* 387 holes carry no per-option
feedback. EE211 holds 40 of them, and the split is the reason it was picked over the
larger debts in EE102 (102) and EE101 (87): its M1–M4 have none and its M4.2–M10 all
have it, so the same course tells a learner why their wrong answer was tempting in its
second half and says nothing in its first.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1170 derivation steps across 46 courses
1366 questions in 252 quiz units · 160 per-option explanations
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui: 78 driven keys and gestures · 10 things said · 15 floored kinds
circuit_model: 1445 analyses · 84 refusals · 15 plots · 15 floors, 17 ceilings
theme: 14 exemptions · 58 contrast surfaces in both themes
blanks: 217 units · 1103 holes · 4327 options — NO GATE
        735/1103 (66.6%) answered by pressing the first option; 26 courses at 100%
        716 holes with per-option feedback, 387 without
        165 prompts carrying mathematics and 80 a code span, all drawn with esc()
        66 options carrying markup the monospace slot draws literally
EE211:  15 blanks units · 81 holes · 41 with per-option feedback · 13 marked-up options
        60 questions · longest-is-key 27 · shortest 4
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads ·
       inlined 13849 KB · shell 1154 KB
```

### The attacks

**2. Assessment Inquisitor** — taken first, because this is its track. The position
tell above is its finding and the rest of this entry is mostly its consequences. Two
more:

- **387 holes answer the same paragraph whichever option was pressed.** EE102 102,
  EE121 93, EE101 87, EE211 40, MA111 20, MA121 17, EE241 11, EE221/MA112/MA201 5 each,
  EE202 2. The field has existed since `blanks` was written and 716 holes use it; this
  is cycle 3's recorded debt, and EE211's share of it is what this cycle paid.
- **The length tell was measured on the blanks bank for the first time and is fine.**
  162 of 1103 (14.7%) against 25.8% for guessing, mean margin −1.7 characters. Recorded
  per course in the budget so it cannot drift, and deliberately not "fixed" — it is
  already below chance, and pushing it further would only invert it. Worth writing down
  because the quiz bank sits at 48% on the same measure: the difference is that a blanks
  option is a fragment of a listing and has nowhere to hide a hedged sentence.

**4. UX & Accessibility Hardener.** Five defects, all in the delivery mechanism rather
than in any course.

- **245 prompts reach the screen as their own source.** `chooser()` builds
  `esc(b.prompt)`, and `esc` in `src/engine.js` is four `.replace` calls on `& < > "` and
  nothing else. So **165 prompts carrying mathematics** print their dollar signs —
  EE101/M2.2 asks for "`$I^2$`, with the current from the line above" — and **80 carrying
  a code span** print their backticks: "Which function does `` `badge` `` call?" reaches
  a learner as `` `badge` `` with the punctuation. Ten courses, led by EE102 (56),
  EE211 (49), EE231 (40) and EE121 (29). Verified against the real renderer, not
  assumed: `mdInline` draws `$1/n^{2}$` as `<math>…</math>` and `esc` hands back
  `$1/n^{2}$`, both run out of the shipped files.
- **Every press throws the keyboard back to the top of the document.** `paint()`
  reassigns `main.innerHTML`, so the focused element ceases to exist — and it is called
  four ways: opening a blank, picking an option, Check, and Clear and retry. Cycle 3
  fixed this class of defect in the quiz, where a learner meets it once per question.
  Here it is once per interaction, and a six-hole unit takes at least thirteen.
- **A row of buttons all called "?".** `.blk` carries `b.hole` and nothing else, so a
  screen reader met six identical buttons with nothing to say which blank each was,
  what was in it, or whether its list was open.
- **The chooser was an unlabelled group.** `.blk-pick` is a heading and some buttons
  with no `role` and no `aria-labelledby` — exactly what cycle 3 repaired on the quiz's
  `.opts` and did not carry across to the kind next door.
- **The listing scrolls sideways with no tab stop.** `.blk-listing` is
  `overflow-x:auto`, and `.article .tw` has had `tabindex="0"` for a wide table since
  before cycle 1. Checked in the stylesheet rather than assumed.

**1. Senior Educator.** A blanks unit has no prose beyond its brief, so this persona was
pointed at the thing in scope it can judge: whether the feedback *explains* or merely
*announces*. In EE211's M1–M4 it announced — one paragraph written for whoever got it
right, shown to everyone. What 40 holes have now is below.

**3. Simulation Auditor.** No sandbox, no tune and no schematic in a blanks unit, so it
was pointed at the two things in scope no gate covers: **what the renderer actually
draws** — which is where the `esc()` finding above came from, and it was found by
running the shipped `renderBlanks` rather than by reading it — and **arithmetic in
prose**. Every number written into the 146 new explanations was computed before it was
written. One was wrong anyway; see below.

### The gate that condemns correct content

Extending `no_positional_refs` to a blank's `whys` — which `emit.py` has always applied
to a quiz's and never to these — fires immediately on EE231/M1.2, whose fourth
explanation ends *"if it is missing here it will be missing from the final answer too"*.
That is the ordinary way to say **the end of a calculation**, and the rule was reading it
as a pointer at an option. Cycle 3 hit the identical trap with case folding and wrote the
reason next to the fix; this is the same failure in the other half of the same pattern.

Swept before deciding, rather than patched around the one hit: across every graded text
in the catalogue there are **4** occurrences of "the final/last answer" — two in
derivation hints, one in a blanks explanation, one in a numeric aside — and **all four
are prose about a calculation**. There are **0** of "the first/last option", **0** of
"option B" and friends, and 2 of "the second/third answer", both in MA121 derivation
hints meaning *the answer to step 2*. So `last|final` now pairs only with
`option|choice`; `first|second|third|fourth|fifth` keeps `answer`. An option is never
called "the final answer" — it is called "the last option", and that is still refused.
Both directions are in the mutation set: the EE231 sentence must pass, and "the third
option" planted in the same field must not.

### Why the options are still escaped, and the fix that would have broken them

The obvious repair for the prompt is the obvious repair for the option, and it is wrong.

**14 options contain `**` and every one of them is Python.** `a**2 - b**2`,
`sqrt(a1**2 + a2**2 + a3**2)`, `n1**2 - n2**2` — EE111, EE141, EMAG530. Through
`mdInline` those come out as `a<strong>2 - b</strong>2`: a fix that breaks correct
content, which is what the invariants call the worst kind. And an option is dropped into
a `white-space:pre` monospace listing — EE211/M1's is an ASCII table with three aligned
columns — where a MathML fraction moves every column after it.

So the option stays literal, deliberately, with the reason written where the next author
will read it. The **66 options authored with `$...$` anyway** are then a content defect
rather than a rendering one: EE211's 13 are rewritten the way the listing beside them is
written (`1/n^2`, not `$1/n^{2}$`), and the remaining 53 — EE102 45, EE231 8 — are
pinned in the budget at their current numbers so a 67th cannot appear.

### What changed

**`renderBlanks` shuffles, through the same helper the quiz uses.** One per-install seed
governs both, so the order is fixed for a learner across retries and not shared between
two. The remap is the load-bearing part: `order` maps a drawn slot back to the index the
author numbered, `data-opt` carries the **authored** index, and what is stored in
`P.blanks` is what was always stored — so **every saved answer in every learner's
progress means exactly what it meant before the shuffle**. The gate proves it by loading
a saved set of authored key indices into a fresh mount and pressing Check.

**The prompt goes through `mdInline`.** 245 fragments across ten courses repaired with
no content edit at all, which is the same shape as cycle 3's `quizProse()` repairing
five EE131 stems.

**The view keeps the keyboard.** Each handler names where focus should go next and
`paint()` puts it there: opening a blank moves to its option list, closing gives it back
to the blank, picking returns to the blank you just filled, Check moves to the score, and
Clear and retry goes to the first blank. Check's target is a new `.blk-fb-h` line reading
"4 of 6 right", so the announcement is the score rather than a region that may or may not
fire — the reason cycle 3 chose focus over `aria-live` for the quiz explanation, applied
unchanged. Plus `aria-expanded` and a real name on every blank ("Blank 3 of 6, holding
h[1], correct"), `role="group"` and `aria-labelledby` on the chooser, and `tabindex="0"`
on the listing.

**`emit.py`'s blanks path gains the three checks its quiz path already had** — duplicate
options, `whys` entries that are empty, and positional references inside them — and
`POSITIONAL` is narrowed as above. Confirmed to change no output: EE231, EE102 and CS201
re-emit byte for byte, and `emit.py --all` produces the same catalogue it did before.

**Content — EE211's M1–M4, 40 holes.** 146 per-option explanations, 4988 words; the
feedback across all 45 holes in modules 1–4 goes from 2949 words to 7937. Every distractor was audited
for being a misconception someone actually holds rather than a wrong number. The ones
worth recording: *"4"* for where a four-sample convolution ends (the length mistaken for
the last index, and the commonest off-by-one there is); *"5"* for the same (the two
lengths added without the sample they share); *"1.75"* for the sum of an impulse
response (magnitudes added, sign discarded — a real quantity, the bound on a bounded
input, attached to the wrong question); *"6"* for a DC term (`a_0` rather than `a_0/2`)
against *"1.5"* for the same hole (`a_0/2` halved a second time), which are the two
opposite ways the same notation is misread; *"8"* for a cosine coefficient and *"−1"* for
a sine one (both the complex-form habit, where a real amplitude splits into two lines of
half the size); *"6 kHz"* for an alias (the Nyquist line treated as a floor to subtract
from rather than as a mirror to reflect in — and 6 kHz is genuinely the distance the tone
sits above it); *"1 + w^2 L C"* for a second-order denominator, where the missing minus
sign is the entire difference between resonance and two cascaded first-order sections;
and *"(R/2) sqrt(L/C)"* for a damping ratio, which rises with the inductor — and a bigger
inductor stores more energy per cycle and damps *less*.

**A new half to `verify_quiz.mjs`, and a stage for it.** The gate now reads the blanks
bank for the structural failures it already refuses in the quiz bank, plus two of its
own — the listing's `___` count against the number of blanks defined, and markup in an
option — and ratchets the length tell and the markup count against
`tools/quiz_budget.json`, which gains a `blanks` entry per course.

The part that matters is `tools/blanks_stage.mjs`, because **both of this cycle's largest
defects were invisible in the JSON and invisible to any rule written about the source**.
A source-shape check saying "renderBlanks calls shuffledOptions" would have been a gate
enforcing a comment. So the stage loads `lang.js`, `tracks.js`, `studio.js`, `engine.js`
and `app.js` in the order `build.mjs` uses, hands them the tiny DOM the two circuit gates
already share, and calls the real `renderBlanks` — then clicks its buttons. Per unit it
checks that one button is drawn per `___`; that the blank buttons have names and the
listing a tab stop; that the chooser is labelled by its prompt; that a prompt whose
source carries mathematics or a code span reaches the screen with neither delimiter left
in it; that the drawn options are a permutation of the authored ones carrying one
authored index each; that pressing the r-th drawn option puts *that* option's text in the
blank; that Check answers with the explanation for **the option actually pressed**, which
is what proves the remap; that Check draws a score for the keyboard to land on; and that
a saved set of authored key indices still grades as right. **6572 draws and 4384 options
picked and read back**, over the whole catalogue, in about two seconds.

`tools/dom_stub.mjs` gained `#id` selectors, purely additively — a term that used to
throw now matches and nothing that used to match behaves differently. Checked rather than
asserted: `verify_circuit_ui.mjs` and `verify_circuit_model.mjs` report identically
before and after.

### Verification beyond the gates

**The gate was not trusted until it was seen to fail. Seventeen mutations, seventeen
intended verdicts:** the shuffle removed from `renderBlanks`; the prompt escaped again;
`data-opt` carrying the shown index; a saved answer stored as the shown index; two
options in one blank reading the same; a `whys` list one entry short; "the third option"
planted in a blanks explanation; **"the final answer" added to one, which must pass**;
markup put back into an option; a course's blanks budget deleted; the listing losing one
of its `___`; a bullet list in an explanation; the blank buttons losing their names; the
listing losing its tab stop; Check drawing no score; the chooser losing its label; and
the unmodified tree as a control.

Every claim in this entry was measured rather than estimated: the 735 of 1103 and the 26
courses at 100%; the 25.8% a shuffle produces on this particular mix of hole widths,
against the 24.5% the gate now measures through the real renderer; the 165 and 80
prompts; the 66 marked-up options and the 14 Python `**` ones that made rendering them
the wrong fix; the four "final answer" occurrences that made the positional rule too
wide. And all 226 mathematical fragments in the 159 strings this cycle wrote were pushed
through the shipped `MathML.render`: **226 of 226 draw**, none is a swallowed fraction,
none has an unpaired `$`, and none carries a backslash before a quote — cycle 3's
raw-string leak, cycle 7's `\tfrac12` drawing as "12", and cycle 7's raw-markup fallback,
all three swept for rather than hoped about.

### Found in my own work, and fixed

- **A number that was wrong for a reason worth keeping.** My new explanation for the
  "46 kHz" distractor said 46 is `f_s - f`. It is not: `48 - 50 = -2`. 46 is
  `2f_s - f = 96 - 50`, a reflection about the sample **rate** rather than about half of
  it, which is a different and more interesting mistake than the one I had written. Found
  by recomputing every number in the new prose against the model rather than by
  re-reading the sentence.
- **My own gate condemned fourteen correct options on its first run.** The tiny DOM keeps
  a text node as the source that was assigned, so an option holding `&`, `<` or `"` reads
  back as the entity `esc()` wrote it as: `s & nfa.accepting` came back as
  `s &amp; nfa.accepting` and the gate reported that the shuffle's index map was wrong.
  A browser hands back the character. Decoded in the stage, with the reason written
  beside it — this is the third cycle in a row to meet a gate condemning working content.
- **I deleted this cycle's own content and had to recover it.** The clean-up that put
  back the 41 catalogue files `emit.py --all` rewrites filtered on
  `startswith('catalog/')` and excluded only `catalog/EE211.json` — so it restored
  `catalog/authors/EE211.py` from HEAD as well, discarding all 146 explanations along
  with it. Recovered by re-running the three generator scripts, and the recovered file
  was re-checked to the same figures rather than assumed identical: 159 strings, 226
  fragments, 226 rendering, 0 swallowed, 0 unpaired, and the course's own pre-existing
  raw and swallowed counts unmoved at 54 and 58. Recorded because the near-miss is the
  lesson: a path filter written for one directory swept up its subdirectory, and
  `git status` was the only thing that showed it.

### Left alone, deliberately

- **347 holes in ten courses still have no per-option feedback**: EE102 102, EE121 93,
  EE101 87, MA111 20, MA121 17, EE241 11, EE221/MA112/MA201 5 each, EE202 2. EE211's 40
  are done. This is cycle 3's debt, one course smaller, and it is now watched: the gate
  reports the count and the budget file pins every course's tells, so the debt cannot
  grow while it waits.
- **53 options still carry markup the monospace slot draws literally** — EE102 45,
  EE231 8 — pinned at exactly those numbers.
- **EE211/M1's six two-option holes stay two-option.** "Is this system time invariant?"
  has two answers, and cycle 3's finding stands: inventing a third option for a genuinely
  binary fact is worse than the coin flip. What they gained is an explanation on **both**
  answers, so the coin flip at least teaches. The unit is graded as six holes together,
  so guessing it whole is 1 in 64.
- **The 24 courses over 50% on the quiz length tell were not touched** — CS301 88%,
  CS310 84%, DSP520/DSP530/EMAG530/VLSI530 80%, CS330 77%, MA101 75%. Cycle 3's main
  recorded debt, still pinned, still unpaid. This cycle deliberately went to the *other*
  bank instead, because the quiz bank had a gate and the blanks bank had none.
- **EE211's 54 raw-markup fragments and 58 swallowed fractions.** Cycle 7 measured this
  catalogue-wide (1053 and 161) and handed it on with the numbers; this cycle measured
  EE211's share before and after and confirms it introduced none and fixed none —
  unmoved at 54 and 58. It is a `studio.js` table change or a whole-catalogue sweep, and
  cycle 7's reasoning for not burying it inside a content cycle applies here unchanged.
- **`emit.py --all`'s 41-file drift was reverted, again.** Running it adds `"check": ""`
  to units whose author file does not set one and rewrites every file with CRLF. Cycle 4
  reverted the same 41 files for the same reason. Only `catalog/EE211.json` is in this
  diff; verified by restoring the other 31 byte-exactly from HEAD and re-checking
  `git status`, not by trusting `git diff`, which normalises line endings and reported
  30 of them as unchanged while the bytes on disk differed.
- **`.quiz-q .qt code` still takes its colour from `--lime` rather than `--code-ink`,
  and `P.dim` (2.93:1) and `P.faint` (1.86:1) still fail contrast on every canvas.**
  Cycles 2, 3, 5, 6 and 8 have each recorded these. Track 5.
- **`docs/programs` aged out one MA101 payload and gained one for EE211.** The rolling
  generation window, as cycles 1–8 all established. Verified rather than assumed: 3
  generations naming 64 files, 64 payload files on disk, **0 orphaned and 0 missing**,
  the current generation listing 62 entries covering 62 distinct courses.

### Gates, after

Every pre-existing number unmoved. The only numbers that moved are the new gate's, the
per-option explanation count — by exactly the 146 written — and the artifact sizes.

```
verify_quiz          All good: 1366 questions in 252 quiz units and 1103 holes in 217
                     blanks units · 3160 per-option explanations (160 quiz, 3000 blanks;
                     3014 -> 3160, +146) · 6572 live draws, 4384 options picked and read
                     back · the answer is drawn in the top slot 24.5% of the time,
                     against 66.6% before the shuffle · every bank within budget   [BLANKS HALF NEW]
verify_circuits      All good: 80 circuit exercises, 340 checks · 527 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_derivations   All good: 1170 steps across 46 courses
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_theme         All good: 14 exemptions · 58 contrast surfaces in both themes ·
                     the 375px topbar · the mobile drawer
verify_circuit_ui    All good: 78 driven keys and gestures, says 10 things while doing it
verify_circuit_model All good: 1445 analyses vouch for every number, 84 refuse ·
                     15 plots · 15 floors, 17 ceilings
verify_labs EE211    All good: 5 labs
emit.py EE211        ok — 10 modules, 4 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12666 -> 12693 KB ·
                     inlined 13849 -> 13880 KB · shell 1154 -> 1159 KB, of 1536
```

Beyond the gates: 17 mutations, each producing the verdict it had to, including one the
gate was required to **pass**; the shuffle's index remap proved by pressing every option
of every hole in the catalogue and reading the explanation back; saved progress proved to
still grade correctly on all 217 units; the two older stub-driven gates confirmed
byte-identical after the shared DOM was extended; 226 of 226 new math fragments rendered
through the shipped renderer; and the payload window checked for orphans rather than
assumed.

---

## Cycle 10 — TRACK 4: Subject Breadth & Progression

**Target: EE201 (Semiconductor Devices and Diodes).** One course, and the debt cycle 8
handed this track by name: *"Not one published schematic uses a non-linear device …
That is a large piece of working machinery no lesson spends, and it is a breadth debt
rather than a defect — Track 4's ground, and a content cycle, not a widening of this
one."* Nothing had picked it up.

Re-measured before starting, because a handed-on number is still a number somebody else
took. Across **376 published schematics** the whole catalogue draws **7 part kinds**:

```
GND 814 · R 713 · V 392 · OUT 328 · C 171 · L 91 · I 53
never drawn: D · LED · NPN · PNP · NMOS · PMOS · OPAMP · SW · LDR · NTC · POT · LAMP · METER · BAR
```

Fourteen placeable kinds, zero uses. EE201 is where that costs the most, and it is not
close: its own summary opens *"Every component in the first year was linear … The diode
is the first one that is not"*, its module 4 is titled *"why a diode is not a resistor"*,
and its **14 schematics contain no diode**. EE202 (*Transistor Amplifiers*, the one
course EE201 is a prerequisite of) has 13 schematics and no transistor.

Chosen over the alternative on the evidence below rather than on taste. EE201 is also
thin: 3.5 units per module against EE101's 12.6, no `read` unit at all, and six of its
ten modules holding neither a reading nor a derivation. It is one of the four courses
cycle 0 flagged as *"full syllabi, still need density"* (EE201, EE202, EE221, EE241),
so the progression half of this track's brief lands in the same course as the breadth
half.

### Baseline, captured before any edit

```
80 circuit exercises / 340 checks · 527 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1170 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3160 per-option explanations · 6572 draws · answer in the top slot 24.5%
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui: 78 driven keys and gestures · 10 things said · 15 floored kinds
circuit_model: 1445 analyses · 84 refusals · 15 plots · 15 floors, 17 ceilings
               376 published schematics, 355 with a DC operating point
theme: 14 exemptions · 58 contrast surfaces in both themes
EE201: 10 modules · 35 units · 0 read · 4 derive · 7 build · 9 labs
       14 schematics, 0 containing a diode
build: 3 parts / 111 keys · 32/32 + 30/30 · 13 visualisers · 3 tune models · 15 symbols ·
       62 payloads, 12693 KB · inlined 13880 KB · shell 1159 KB
catalogue: 62 courses, 368 modules, 1883 units
```

### The attacks

**1. Senior Educator** — taken first, because the defect turned out to be a false
sentence rather than a missing one.

- **The course tells the learner the tool cannot do the thing the tool does.** EE201/M2's
  build opens: *"The schematic editor solves linear circuits, and a diode is not
  linear."* That is false, and has been since cycle 0 built the Newton-Raphson loop.
  `src/circuit.js` carries a full Shockley junction with `pnjlim` limiting, a `vcrit`
  cold start and an `EXP_CAP` guard, and `PART_KINDS.D` has shipped the whole time. The
  exercise then teaches the piecewise-linear model **as a workaround for a limitation
  that does not exist**, which is the one framing that makes a genuinely important
  modelling technique look like a chore.
- **Swept rather than repaired in place**, per the invariant. Four sites in EE201 make
  the claim in some form: the M2 build brief (false about the app), the M2 quiz `why`
  and the build's title (true of *a* linear solver, and defensible), and a course
  outcome. Only the first is false; the others are about the technique and were left
  saying what they say, with the outcome extended rather than replaced.
- **The model's number is stated as the device's number, in a concepts bullet.** M10's
  bullet reads *"sharing one resistor at 20 mA, split it 14.1 mA and 5.8 mA — a 100 mV
  spread in $V_F$ becoming a 2.4:1 spread in brightness"*. 14.1 and 5.8 are what the
  **straight-line stand-ins** do. The junctions split **18.17 mA and 2.63 mA**, a ratio
  of **6.92**. The bullet asserts a property of the linearisation as a property of LEDs,
  three lines above an exercise that does the same — exactly the shape the curriculum
  warns about.

**3. Simulation Auditor** — this persona had unusual purchase here, because for once the
thing under audit is a *stated answer* that the app's own solver can be made to check.
Every number below was computed by loading `src/circuit.js` as shipped and solving, not
by hand.

- **The exercise's own headline number understates its own lesson by 2.8×.** M10 is
  called *"Two LEDs that are meant to look the same"* and contains no LED: two `V`
  sources (1.85 V, 1.95 V) and two 12 Ω resistors. Solved as authored it reproduces the
  brief exactly — 14.1026 mA and 5.7692 mA, ratio 2.4444 — so the brief is right about
  its own circuit. Rebuild it out of `LED` parts carrying the saturation currents those
  drops imply and the split is 18.1679 mA and 2.6263 mA, **ratio 6.9178**.
- **And the real ratio is a constant the model cannot express.** Measured at six ballast
  values from 50 Ω to 10 kΩ: **6.9178 every time**, to four decimal places. At a shared
  node both junctions are held at one voltage, so $I_A/I_B = I_{SA}/I_{SB}$ — the
  exponential cancels and the ballast drops out. The piecewise-linear ratio is
  $(V-1.85)/(V-1.95)$, which moves with $V$. The stand-in does not merely get the number
  wrong; it gets the *shape of the answer* wrong.
- **The three descriptions of a diode are indistinguishable at the design point and
  separate immediately away from it.** Solved on the same 430 Ω branch:

```
                       0.1 mA       10 mA      change
  the real device      0.5773 V    0.6964 V    119.05 mV
  the tangent model    0.6708 V    0.6964 V     25.59 mV
  a 69.64 ohm resistor 0.0070 V    0.6964 V    689.44 mV
```

  119.05 mV is $nV_T\ln 100$ to five figures, and the device reproduces the 59.5 mV per
  decade **three consecutive times** across 0.1 mA → 100 mA (0.05952, 0.05953, 0.05952 V).
  That is module 2's own concepts bullet, and until this cycle the course had no way to
  show it happening.
- **Checked and found correct, recorded so the next cycle does not re-derive it:** the
  existing M2 brief's arithmetic is right in every particular — $V_D = 0.6964$ V,
  $r_d = 2.5852$ Ω, $V_{D0} = 0.6705$ V, and the shipped `VT` is 25.8520 mV, so the
  brief's `25.852` is the solver's own constant rather than a rounded quote. The M10
  hints' claims that 330 Ω passes and 390 Ω and 220 Ω fail hold against the real
  junctions too (9.55/9.26 mA; 7.85 mA under the 8 mA floor; 14.2 mA and 28.0 mA out of
  the rail).

**2. Assessment Inquisitor.** EE201's questions are Track 3's ground and were not
rewritten. Audited for the one thing this cycle could falsify — whether any *key*
depends on the linear stand-in being the device — and **none does**: the M2 question
that asks where a piecewise-linear model is exact answers "at 10 mA and nowhere else,
though it stays useful for a decade either side", which the measurement above confirms
rather than contradicts. Recorded so it is not re-audited. The new material adds no
question, deliberately: the two new units are graded by the solver, which is a stronger
check than a distractor set.

**4. UX & Accessibility Hardener.** Content-side, as cycles 1, 4 and 7 established.
Every math fragment this cycle wrote was pushed through the shipped `MathML.render` —
which is how the defect in *my own* work below was found. No hard-coded colour, no raw
HTML and no wide table was introduced; the one table is a fenced `text` block inside
`overflow-x:auto` rather than a markdown table, which is cycle 4's rule for staying safe
at 375px. The two new schematics were driven through `verify_circuit_model`'s recording
canvas at five widths as part of the catalogue sweep: no non-finite coordinate.

### The machinery finding this cycle did not spend

**`emit.py` forbids the device from the one unit kind whose answer a gate checks.**
`DIAGRAM_KINDS = {"R", "C", "L", "V", "I", "GND", "OUT"}`, so a `numeric` unit — the kind
that *must* carry a `check` run against the MNA solver, by the curriculum's own
invariant — cannot draw a diode. `MATCH_SYMBOLS` next to it already contains `D`, `LED`,
`NPN`, `PNP`, `NMOS`, `PMOS` and `OPAMP`, and `drawPart` renders all of them, so the two
lists in one file disagree about which devices exist.

**Not changed, and the reason is scope.** Widening it is provably safe — a kind that
currently raises can only start being accepted — but it is an emitter change whose value
is entirely in units nobody has written yet, and this cycle's content did not need it:
a `build` unit carries a real schematic and is graded by the same solver. Adding a rule
to serve content that does not exist is how a gate ends up enforcing a comment. Recorded
with both list contents so the next cycle starts from the diff rather than the symptom.

### Found in my own work, and fixed

- **Six of my own new fragments would have shipped as raw LaTeX markup.** `$430.4\ \Omega$`
  and five like it. The offender is the **escaped space `\ `**, which `src/studio.js` has
  no rule for, so `MathML.render` returns `<code class="math-raw">` holding the source —
  no error, nothing for a gate to catch. Caught by rendering the draft rather than by
  trusting that `$…$` is enough, which is cycle 7's discipline applied to its own lesson.
  Repaired to `\,`, which renders; `~` and a plain space also work, `\text`, `\!`,
  `\frac`, `\left`/`\right`, `\Omega` and `\times` were all confirmed fine.
- **That is a refinement of cycle 7's catalogue-wide measurement, and worth carrying.**
  Cycle 7 listed 37 unsupported commands and did not name this one, because it probed
  `\[a-zA-Z]+` and `\ ` is not a word. Measured now: of the **1053** raw-markup fragments
  in the catalogue, **369 (35%) are caused by the escaped space alone** — EE231 110,
  EE111 45, EE141 34, EE101 29, EE121 20, EE201 20, EE211 19, EE131 17, MA111 14,
  EE102 13. It is by some distance the cheapest third of that debt to retire: one rule in
  the tokeniser, or a mechanical `\ ` → `\,` sweep.
- **My first patch script would have written `r\'\'\'` into the source and searched for
  the wrong bytes.** The target file writes a LaTeX backslash doubled inside `"…"` and
  single inside `r'''…'''`, so a non-raw anchor matched neither. Rewritten with raw
  strings throughout and a triple-quote assembled at runtime. Every anchor is asserted
  unique before anything is written, so the script cannot half-apply — it was run
  `--check` first and reported all nine.
- **A check that said `NaN` when both LEDs were dark.** The within-10% check divided one
  current by the other, and on the starting circuit both are zero. It now refuses with a
  sentence about the LEDs being unpowered or upside down, because the repository's
  standard since cycle 2 is that nothing a unit says contains `NaN`.

### What changed

**Two new build exercises, both graded against the real device**, appended to the module
they belong to. Each existing build kept its unsuffixed lesson id (`-M2`, `-M10`) and the
new ones took `M2.2` and `M10.2`, so no completed work is orphaned — the invariant, and
confirmed by the gate's own labelling.

| | EE201/M2.2 | EE201/M10.2 |
|---|---|---|
| title | The diode itself, and the decade it lives in | The same two LEDs, with the junctions left in |
| parts | 2 × `D`, $I_S = 2\times10^{-14}$, $n = 1$ | 2 × `LED`, $n = 2$, $I_S$ 2.889e-18 / 4.176e-19 |
| asks for | 0.1 mA and 10 mA, two decades apart | the same 8–12 mA / 10% / 22 mA specification |
| the measurement | the drop moves **119.05 mV** | the split is **6.92**, not 2.4 |
| reference / start | 4/4 · 1/4 | 4/4 · 2/4 |

**M2.2** is the exercise the module was missing: the previous unit builds the tangent,
this one puts the device beside it and measures where the tangent stops being the curve.
The four checks read the junctions through `c.device()` — an API written for exactly this
and, until now, called by nothing in the catalogue. Its last check is the interesting
one: it asks for 119 mV and names the two wrong answers, so a learner who has quietly
left a `V`+`R` pair in place fails on the number the model cannot produce.

**M10.2** rebuilds M10's specification out of junctions, and the shared-ballast trap
now fails on the physics rather than on a stipulation: 18.17 mA against 2.63 mA. The
brief derives why the ratio is the ratio of saturation currents and therefore independent
of the ballast, which is a fact the course could state and could not previously show.

**Four repairs to what was already there**, all in the two modules touched:
the false sentence about the editor; a course outcome extended to name checking the model
against the device; M2's concepts gaining the *range* of the piecewise-linear model as
three measured numbers rather than "a decade either side"; and M10's concepts and brief
corrected so the 2.4:1 is attributed to the model and the junction's 6.92:1 stated beside
it. Verified structurally rather than by reading the diff: **2 units added, 0 removed,
and exactly 4 pre-existing items changed** — the two briefs and the two concept lists.

EE201: 35 units → 37 · 7 build units → 9 · 14 schematics → 18, of which **4 contain a
non-linear device**, against 0 in the whole catalogue before this cycle.

### Left alone, deliberately

- **The other twelve unused part kinds, and EE202.** `NPN`, `PNP`, `NMOS`, `PMOS` and
  `OPAMP` are still drawn by nothing, and EE202 — *Transistor Amplifiers*, 11 modules,
  13 schematics, no transistor — is the obvious next instalment of exactly this cycle.
  It is also a second course, and the brief says one. The bridge is now at least
  half-built: EE201 ends by pointing at EE202, and EE202's M1 introduces the MOSFET from
  first principles rather than assuming it, so the prerequisite chain is sound even while
  the practice is thin. Recorded with the count.
- **M3 cannot have a device-bearing build, and this was checked rather than assumed.**
  *Rectifiers, the reservoir capacitor and ripple* is the canonical diode circuit and
  the obvious third exercise. `MNA.tran` has **no time-varying source** — there is no
  `Math.sin` anywhere in the solver, and `V` carries a DC value and an `ac` field used
  only by the small-signal path — so a rectifier cannot be run. That is a Track 2
  machinery gap, not a content one, and it is the single change that would unlock the
  most catalogue content: rectifiers, clippers, clamps and multipliers are four of
  EE201's ten modules.
- **M4's Zener and M7's varactor have no part kind either.** `D` has no breakdown
  voltage and no junction capacitance, so *Zener regulation* and *the junction as a
  capacitor* cannot be drawn even now. M9's reverse recovery is the same: the model is
  static and stores no charge. Three more modules whose device exists in the prose and
  not in the solver, recorded so the next cycle does not rediscover them one at a time.
- **EE201 still has no `read` unit and six modules hold neither a reading nor a
  derivation.** Six real courses are thinner still on units per module (MA112 and MA201
  at 2.09, MA101 2.31, EE202 3.18, EE221 and EE241 3.20), so this is a shared debt rather
  than a worst case. That is Track 1's ground and cycle 1 established that a density pass
  is its own cycle. There is also a **stranded patch for exactly this work** — six EE201
  readings, written by a cycle that could not write to the repo, sitting in another
  session's scratchpad at the path recorded in `memory/unapplied-gauntlet-patches-on-disk.md`.
  This cycle deliberately touched neither M2's nor M10's `read` slot (both modules
  already have neither), so that patch's anchors are undisturbed and it can still land.
- **Cycle 4's claim that "none of the fifteen syllabus-only stubs is a prerequisite of
  anything" is false, and this cycle checked before relying on it.** Built the
  prerequisite graph from both spines: **CE101 → CE201 → CS210 and HPC401**, **ML401 →
  DL501, ELEC410, ETH501, ROB520**, **SEC301 → ELEC420**. Four of the fifteen are
  prerequisites of eight courses between them, and CE101 (*Digital Logic & Computer
  Systems*, no prerequisites of its own, 4 modules holding one lab each) is a **root** of
  the CS degree's hardware chain. That is a stronger Track 4 target than its stub status
  suggested and it was the serious alternative to EE201 this cycle weighed; EE201 won on
  being a handed-over debt with gates that can prove the fix, where CE101 is a
  build-a-course cycle whose only checks would be `verify_quiz` and the emitter.
  Recorded with the graph so the next cycle starts from it.
- **`emit.py`'s `DIAGRAM_KINDS`, above.**
- **The 21 catalogue JSONs that sit CRLF on disk**, EE201 among them before and after.
  `.gitattributes` is `* text=auto eol=lf`, so the committed bytes are LF and only EE201
  shows as modified — verified rather than assumed, since cycle 9 recorded that `git
  diff` normalises line endings and can mislead in both directions.
- **`docs/programs` aged out one MA101 payload and one EE211 payload and gained two for
  EE201.** Two, not one, because this cycle built twice — the second build followed the
  escaped-space repair — and both EE201 payloads are still inside a retained generation.
  The rolling generation window, as cycles 1–9 all established. Verified rather than
  assumed: **64 files named by a retained generation, 64 on disk, 0 orphaned and 0
  missing.**

### Gates, after

Every pre-existing number unmoved. Four numbers moved, each by exactly what was added.

```
verify_circuits      All good: 82 circuit exercises, 348 checks · 543 labels
                     (80 + 2 · 340 + 8 · 527 + 16)
                     EE201/M2.2 reference 4/4 · start 1/4
                     EE201/M10.2 reference 4/4 · start 2/4
verify_circuit_model All good: 1457 analyses vouch for every number they return and 84
                     refuse rather than guess · 15 plots · 15 floors, 17 ceilings ·
                     380 published schematics, 359 with a DC point   (1445 + 12 · 376 + 4)
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_quiz          All good: 1366 questions in 252 quiz units and 1103 holes in 217
                     blanks units · 3160 per-option explanations · 6572 draws · 24.5%
verify_derivations   All good: 1170 steps across 46 courses
verify_circuit_ui    All good: 78 driven keys and gestures, says 10 things while doing it
verify_theme         All good: 14 exemptions · 58 contrast surfaces in both themes
verify_labs EE201    All good: 9 labs
emit.py EE201        ok — 10 modules, 8 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12693 -> 12706 KB ·
                     inlined 13880 -> 13893 KB · shell 1159 KB unchanged
```

Beyond the gates: every number written into the two new units computed by loading
`src/circuit.js` as shipped and solving, before it was written — the 119.05 mV against
$nV_T\ln 100$, the 59.5 mV per decade reproduced three times, the 6.9178 split measured
at six ballasts from 50 Ω to 10 kΩ, and the authored stand-ins re-solved to confirm the
brief they already had; all 32 math fragments of the new units rendered through the
shipped `MathML.render` (**32 of 32, 0 raw, 0 swallowed**) and the catalogue's raw count
confirmed unmoved at 1053; hedge words counted at HEAD and now by diff rather than by
counting twice (**5 and 5, 0 introduced**); the EE201 diff compared structurally against
HEAD rather than as lines; and the payload window checked for orphans.

---
