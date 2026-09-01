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

## Cycle 11 — TRACK 5: UI, Layout & Visual Aesthetics

*(the runner labels this commit "cycle 5"; its counter restarts per run and this log's
does not. Cycles 1–4 of the current run are entries 7–10 above.)*

**Target: the answering surface — the chrome the four graded unit kinds are delivered
on.** `.blk*` (fill in the blanks), `.opt` / `.quiz-q` / `.explain` (quiz), `.nq-*` /
`.numq-*` (find the value) and `.mt-*` (symbol drill), plus the `.q-*` pieces the last
three share, all in `src/index.head.html`. One subsystem, defined by what it does rather
than by where it sits: it is every surface on which a learner gives an answer and is told
whether it was right. **217 blanks units holding 1103 holes, 252 quiz units holding 1366
questions, 434 numeric units and 11 match units.**

Chosen because the two obvious Track 5 targets are already taken and this one had never
been looked at by anybody. The previous run's Track 5 cycle took the *reading* surface;
cycle 5 above took the *shell*. Both left `theme_budget.json` behind them, and the 58
surfaces in it are the shell, the buttons and the circuit editor's panel — **not one entry
for any of the four kinds a learner is actually graded on.** Cycle 3 hardened the quiz's
focus and live regions and cycle 9 did the same for blanks, so this surface has had two
accessibility passes; neither was a *visual* pass, and both recorded a colour defect they
declined to fix on the grounds that the token ramp is Track 5's call. It is.

### Baseline, captured before any edit

```
82 circuit exercises / 348 checks · 543 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1170 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     · 3160 per-option explanations · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1457 analyses, 84 refusals,
     380 published schematics / 359 with a DC point
theme: 14 written exemptions · 58 contrast surfaces x 2 themes · tightest text 4.63:1
build: 3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers · 3 tune models ·
       15 symbols · 62 payloads totalling 12706 KB · inlined 13893 KB · shell 1159 KB
```

### The attacks

**4. UX & Accessibility Hardener** — taken first, because this track's brief is mostly its
brief. Every ratio below is from the WCAG 2.1 sRGB formula against the *composited* stack,
computed before the fix and again after, not eyeballed.

- **The whole of a blanks unit is unreadable in the light theme, and the mechanism is one
  sentence.** `.blk-wrap` is `background:var(--editor)`, and `--editor` is `#0A0B0E` dark
  and `#12151A` light — deliberately dark in both, with the comment `/* code stays dark in
  both themes */` sitting on the token. Everything painted inside it took the *page's* ink.
  So in the light theme the listing itself, `--ink-2` = `#3D4539`, measures **1.84:1** on
  that ground, and **a hole with an answer typed into it is `--ink` `#131712` on
  `--surface-2` over `#12151A`: 1.01:1.** Black on black. The three answer-state colours
  are the same story — `--ans-ok/-no/-wait` flip dark for a light ground, so a hole marked
  right is 3.21, marked wrong 2.90 and still waiting 3.07. And the bar across the top of
  the box is `--sunk`, which *does* follow the theme, so a near-white strip sat over a dark
  listing. **This is the trap cycle 2 measured on the canvas and minted `--on-editor-*`
  for, in CSS rather than in a draw loop, in the one unit kind whose entire content is the
  learner's own answer.**
- **The number you type into a numeric question is invisible in the light theme, and the
  placeholder is not.** `.nq-in` is also `--editor`; its input was `color:var(--ink)` —
  **1.01:1** — while `::placeholder` was `--ink-5`, which in the light theme is a *pale*
  grey on a dark ground and so measures **8.74:1**. The hint was eight times more legible
  than the answer it stood in for, in both directions at once: 1.86 against 17.09 in the
  dark theme, the exact inversion. 434 numeric units.
- **`--ink-5` used for two labels that are not disabled controls.** `.nq-lbl` — the
  "Your answer" above the only input the unit has — at **1.81 / 2.07**, and `.blk-count`,
  the "4 / 6 right" a learner reads after checking, at **1.88 / 1.77**. Cycle 5 made this
  exact repair on `.rail-miss` and recorded why the tier itself must stay where it is.
- **The same fact — right or wrong — is drawn at three different strengths in three unit
  kinds, and two of them are invisible.** `.blk-row` 30%, `.q-verdict` 34%, `.mt-card` 45%,
  all `color-mix` of the answer colour against the card: 2.32 / **1.61** for ok and 1.70 /
  1.76 for wrong, against a 3:1 floor. Three numbers for one idea, none of them chosen.
- **`--lime` as ink on its own tint, three more times**, which is the trap cycle 5 minted
  `--accent-ink` for: `.quiz-q .qt code` **3.65** and `.opt code` **3.51** — both recorded
  by cycle 3 as left alone because "changing it is a Track 5 decision about the token ramp
  rather than something a Track 3 cycle should do on its own" — and `.opt.correct .k`, the
  letter of the right answer, at **3.16**.
- **`.opt .k` at 4.37:1 in the dark theme**, marginally under the floor. It is the A/B/C/D
  key, `--ink-4` on `--surface-2` over `--surface-2` over the card — two tints deep, which
  is what takes it under.
- **`.numq-nofig` at 3.27 light** — the prose shown when a numeric unit has no schematic.
  Same editor ground, same page ink.

**1. Senior Educator** — no prose in a stylesheet, so this persona was pointed at the type
scale, which is the visual equivalent of whether a thing explains itself.

- **`.nq-lbl` is 10px.** It is the label on the primary input of an entire unit kind, in
  uppercase mono with 0.13em tracking. `.quiz-q .qn` — "QUESTION 3 / 6", the only thing
  telling a learner where they are in a bank of six — is 10px for the same reason. Cycle 5
  raised the rail's 9.5px module titles to 11px on precisely this argument and the
  answering surface was never swept for the same thing.
- *Checked and left:* the `.q-prompt` at 21px / 1.3 with `text-wrap:balance`, the `.explain`
  at 13px / 1.6 with `text-wrap:pretty`, and `.blk-listing` at 13.5px / 2.05 — the tall
  line height is there to give the inline holes room and it is correct. The hierarchy above
  11px is sound; the defect is only at the bottom of the ramp.

**3. Simulation Auditor** — no solver here, so it was pointed at the layout, computed from
the stylesheet's own lengths rather than trusted.

- **The narrowest real lesson column is 275px, and two earlier cycles have been reasoning
  about 343.** At 375px: `.app` is `grid-template-columns:var(--rail-icon) minmax(0,1fr)`
  with `--rail-icon:60px` below 980px and the icon rail present at every width outside
  focus mode, so `.main` is 315px; `.body` drops to one column at 980px so the rail's 272px
  track is not reserved; `.lesson-read` is `padding:24px 20px` there, and `box-sizing` is
  `border-box` globally. **315 − 40 = 275px.** Cycle 2 concluded that `paint()`'s
  `Math.max(240, …)` floor "never bites at 375px, where the stacked column is ~343px", and
  cycle 8's gate resizes the schematic at 343px as its narrowest case. The *conclusion*
  survives — 275 is still above 240 — but the number both rest on is 68px too generous, and
  a future floor chosen against 343 would be chosen against a column that does not exist.
  Recorded rather than acted on: changing another track's gate from inside this one is the
  move cycle 4 reverted and cycle 7 declined.
- **Checked at 275px and found sound, so the next cycle need not re-derive it:** `.numq`
  and `.tune` collapse to one column at 900px; `.mt-grid` is `minmax(160px,1fr)` and gives
  one 275px card; `.blk-listing` is `white-space:pre` with `overflow-x:auto` **and a
  `tabindex="0"`**, which cycle 9 added, so the sideways scroller is reachable; `.opt`,
  `.blk`, `.blk-opt` and `.mt-lb` all compute to 28–32px tall against WCAG 2.5.8's 24px;
  and `.nq-in input` is **17px**, over the 16px at which iOS Safari stops zooming the
  viewport when a field takes focus — which is a real property of this surface and not an
  accident, since it is the one field on a phone a learner types into.
- **`prefers-reduced-motion` needs nothing here.** The blanket `*{animation:none!important;
  transition:none!important}` covers `.blk-pick`'s `fadeUp`, `.quiz-result`'s `popIn` and
  `.mt-card:hover`'s `translateY`; and `renderQuiz`'s `scrollIntoView` already tests the
  media query in script, because a CSS rule cannot reach a scroll the script asks for.

**2. Assessment Inquisitor.** No graded question in a stylesheet, so — as in cycles 2, 5
and 6 — it was pointed at the one thing in scope it can judge: whether a state *announces
itself or merely exists*.

- **After answering, the two options nobody picked look exactly like live buttons.**
  `renderQuiz` sets `disabled` on all four and adds `.correct` to the key and `.wrong` to
  the one that was picked. The other two get no class, and **there was no `.opt:disabled`
  rule at all** — same fill, same border, same key chip, the only difference being that
  the hover no longer fires, which is not a thing you can see without trying it.
- **The hover on a quiz option is 1.10:1 in the dark theme** — `rgba(255,255,255,.04)` over
  a card that is already `rgba(255,255,255,.02)`, a two-per-cent step. That is under the
  1.1 floor cycle 5 set for exactly this question, and it is the faintest state in the
  application. Found by the gate, not by hand, on the first run after this surface was
  written into the budget.
- *Checked and found sound:* right and wrong are **not** conveyed by colour alone anywhere
  here. The quiz's `.ex-head` writes "✓ Right." or "✗ Not quite — the answer is **B**";
  `.q-verdict` and `.blk-row` each carry a `.gmark` in an 18px column beside the text; and
  `.mt-slot` states the name it was given. The colour is confirmation in all four kinds,
  which is why the border strengths above are a *state* defect rather than a 1.4.1 one.

### The defect this cycle found in the machinery, which is the largest thing in it

**`verify_theme.mjs` was describing the stylesheet, not enforcing it.** For every entry
except a `state` one, the gate took the ink from `theme_budget.json` and the background
stack from `theme_budget.json`, and read out of `src/index.head.html` only the token
*table*. So an entry said "`.blk-listing` is `--on-editor-2` on `--editor`" and the gate
dutifully measured 7.20:1 — **whether or not `.blk-listing` still said that.**

This is not a hypothetical. Fourteen mutations were built, each one putting a surface this
cycle had just repaired back on the token it had that morning, and the gate was asked to
object. **It rejected two and accepted twelve** — including the blanks listing back to
1.84:1, the numeric answer box back to 1.01:1, and every one of the `--lime`-as-ink
reverts. The two it caught were the option hover (a `state` entry, which has always read
the stylesheet through `hoverBg`) and a bare hex planted on `.blk-file` (the *tokens*
section, which reads the stylesheet too).

Cycle 6 came within one step of this. Its entry records writing the editor's rows "**as the
stylesheet actually declares them**" and letting the gate find the 4.06:1 — which worked,
because at that moment the budget and the source disagreed. What neither of us noticed is
that the technique is a one-shot: the instant the CSS is repaired and the entry matches, the
tie is cut and nothing holds it. Fifty-eight surfaces had been in that state for two cycles.

**Fixed.** `hoverBg` is generalised to `declared(sel, prop, theme)` — the same lookup, for
any property: `sel` in the dark theme, `[data-theme=light] sel` in the light one, falling
back to the dark rule when the light one is missing, which *is* the `.inav:hover` defect and
so stays measured rather than restated. An entry that names `sel` now takes its ink from the
stylesheet and its declared `fg` is ignored; an entry whose named rule declares no such
property is a failure, which is what catches a rule being deleted outright. `bg` stays in
the budget, and that is deliberate: a background *stack* is a fact about the DOM's nesting,
not about one rule, and inventing it from a stylesheet would mean modelling the cascade.

**46 of the 107 surfaces now read their ink from the source** — the 46 this cycle added and
annotated. Back-filling the shell's 58 is mechanical and is the obvious next Track 5 job;
it is not this cycle's, because those 58 name rules this cycle has no business reading.
The gate prints the count, so the number cannot quietly stop growing.

### What changed

**Tokens — five, all in `:root` only, so no theme can override them.** They follow the
`--on-editor-{lime,blue,purple,amber}` precedent exactly, and their values are the dark
theme's own answer colours, which were already tuned for a dark ground.

| token | value | why |
|---|---|---|
| `--on-editor-ok` | `#5BE58A` | the answer state, on a surface that does not flip |
| `--on-editor-no` | `#FF5C7A` | " |
| `--on-editor-wait` | `#FFB020` | " |
| `--on-editor-sunk` | `rgba(255,255,255,0.04)` | a recessed bar on that surface |
| `--on-editor-fill` | `rgba(255,255,255,0.06)` | a filled chip on it |

**The measurements, before → after. The dark theme barely moves, which is the point: this
repairs the broken theme without redesigning the working one.**

| surface | dark | light |
|---|---|---|
| `.blk.filled` — the answer put into a hole | 16.54 → 15.17 | **1.01 → 13.68** |
| `.blk-listing` — the code around the holes | 10.33 → 7.74 | **1.84 → 7.20** |
| `.blk` — a hole still waiting | 8.91 | **3.07 → 8.02** |
| `.blk.right` / `.blk.wrong` | 9.45 / 5.68 | **3.21 → 8.45 · 2.90 → 5.17** |
| `.blk-count` — "4 / 6 right" | **1.88 → 7.20** | **1.77 → 6.55** |
| `.blk-file` · `.nq-u` | 4.95 → 7.20 | 4.27 → 6.55 |
| `.nq-in input` — the answer being typed | 17.09 | **1.01 → 15.89** |
| `.nq-in input::placeholder` | **1.86 → 2.93** | **8.74 → 2.72** |
| `.nq-lbl` — "Your answer" | **1.81 → 4.75** | **2.07 → 4.98** |
| `.numq-nofig` | 6.14 → 7.74 | **3.27 → 7.20** |
| `.quiz-q .qt code` · `.opt code` | 13.03 · 12.35 | **3.65 → 6.31 · 3.51 → 6.07** |
| `.opt.correct .k` — the right answer's letter | 9.43 | **3.16 → 5.47** |
| `.opt .k` — an idle letter | **4.37 → 5.49** | 4.60 → 5.11 |
| `.q-verdict` / `.mt-card` / `.blk-row` borders, ok | **2.32–3.21 → 7.82** | **1.61–1.91 → 3.45** |
| the same, wrong | **1.70–2.15 → 4.45** | **1.76–2.16 → 4.17** |
| STATE `.opt` hover against idle | **1.10 → clears** | 1.11 |

The placeholder is the one figure that went *down* in the light theme, deliberately: 2.72:1
against the value's 15.89, with its own floor written into the budget. A placeholder that
reaches AA stops being distinguishable from a filled field, which is the decision cycle 5
recorded when it declined to darken `--ink-5`, and the defect here was never that the
placeholder was too quiet — it was that it was **louder than the answer**.

The three answer-state borders are one number now, 80%, chosen rather than inherited: it is
the lowest mix that clears 3:1 on all four of {ok, no} × {dark, light} — 7.82, 3.45, 4.45,
4.17. 60% and 70% both leave the light theme's `ok` under the floor.

**Type.** `.nq-lbl` 10px → 11px and `.quiz-q .qn` 10px → 11px, matching what cycle 5 did to
the rail.

**Micro-interactions.** A spent quiz option loses its raised fill *and* its key chip, so an
answered card reads as answered: two channels, because the fill alone is 1.04:1 against the
card. The option hover goes from a 2% step to a 5% one. `.opt`'s `transition:all .16s`
became the three properties it actually animates.

**The gate**, as above, plus two smaller repairs to its reporting: a surface with a declared
`floor` no longer sets the headline "tightest text" — adding the placeholder made the
summary read 2.72:1 where it had read 4.63, which looks exactly like a regression and is
not — and the count of source-read surfaces is printed.

### Found in my own work, and fixed

Three, and every one of them was caught by measuring rather than by re-reading.

- **My fix for the spent quiz option was a contrast regression.** The first version was
  `opacity:.62`, which is the obvious way to say "spent" and which drops the option's own
  text to **4.41 / 3.38:1** and its key to **2.91 / 2.47** — so three quarters of every
  answered question would have become harder to read than before the cycle that was
  repairing it. This is the failure mode the curriculum names: a correction that inverts
  what it was written to fix. Replaced with a change to the surfaces only; the option's ink
  is untouched at 10.03 / 9.86 and the key lands on `--ink-4` at 4.95 / 4.62.
- **`--accent-ink` was not enough for `.opt.correct .k`.** I reached for the token cycle 5
  minted for this, measured, and got **4.47:1** — under the floor by three hundredths,
  because that key sits on `--lime-12` over the option's own `--lime-08`, two tints deep,
  where `.btn.accent` sits on one. `--code-ink`, the darker of the two accent inks, clears
  it at 5.47. The token being *for* this problem is not the same as it solving this
  instance of it.
- **The option hover I did not touch was the one the gate rejected.** `rgba(255,255,255,.04)`
  had been there all along and my own hand audit had walked past it, because a 2% step over
  a 2% card looks fine written down. It failed on the first run after the entry existed.

### Left alone, deliberately

- **`--lime` is still used as ink in 35 places, and the light theme puts most of them at
  3.4–4.1:1.** Counted, not estimated: `a` — every link in the app — at **3.76**,
  `.eyebrow` 3.76, `.lesson-title .lnum` **3.40**, `.chip.done` / `.chip.lab` /
  `.chip.prereq.met` 3.65, `.pcard code` 3.65, `.dv-substep b` and `.sbx-v` 4.06. Each is a
  one-token edit; together they are the accent weight of every screen in the application,
  which is a decision about the design language rather than a repair, and it belongs in a
  cycle that does nothing else. This cycle took only the three inside its own subsystem.
- **55 rules are still under 11px.** The two in the answering surface were raised; the rest
  are across the course screen, the profile, the workbench and the planner. Same argument:
  a type-scale pass is its own cycle, and doing it from inside this one would have meant
  touching every screen and verifying none of them.
- **The 58 shell and editor surfaces still describe rather than enforce.** The mechanism now
  exists and 45 surfaces use it; annotating the other 58 with their `sel` is mechanical, and
  it is the first thing the next Track 5 cycle should do. Recorded as the debt this cycle
  created the tool for and did not spend.
- **`P.dim` at 2.93:1 and `P.faint` at 1.86:1 on the canvas.** Cycle 2 measured them and
  handed them to Track 5 by name; cycle 5 re-measured them and did not take them; cycles 6
  and 8 both recorded them again, cycle 8 adding the analysis plot's axis labels to the
  list. This cycle did not take them either, and the reason has not changed: they are the
  grid, ticks and legends of 13 visualisers plus two canvases, in `src/studio.js` rather
  than in the stylesheet, and moving them changes the visual weight of every drawing in the
  app. Cycle 5's three candidate values still stand — `#6B7280` → 4.07, `#767D8A` → 4.75,
  `#7E8694` → 5.36 — and it is now the *only* Track 5 debt that four separate cycles have
  named without anyone taking it. It should be the target, not the leftovers.
- **`.blk.open`'s outline and `.blk`'s dashed border are budgeted without a `sel`.** Both
  are composite shorthands (`outline:2px solid …`, `border:1px dashed …`) and teaching
  `declared()` to parse shorthand is a real parser, not a regex. They measure 10.76 / 10.00
  and are nowhere near a floor; recorded so the gap in coverage is known rather than
  implied by silence.
- **`.q-prompt` has no `sel` either**, for the opposite reason: it declares no colour at all
  and inherits `--ink` from the body. An entry naming it would fail. Left declarative.
- **The 275px column, above.** Cycle 2's and cycle 8's numbers are wrong and their
  conclusions are not; correcting another track's gate from inside this one is what cycle 4
  reverted the 41-file re-emit for.
- **No author file, no `catalog/*.json`, no lesson id and no schema was touched**, so
  `emit.py` was not run and the staleness guard is not armed. The mechanical confirmation is
  that the payload total is **12706 KB before and after** and `git status` reports nothing
  under `docs/programs` — no course's JSON moved, so no payload could.
- **`docs/programs` holds 64 payloads against 62 in the current generation.** The rolling
  window, as cycles 1–10 all established, and this cycle built twice. Verified rather than
  assumed: 3 generations retained, 64 files on disk, all 64 named by a retained generation,
  **0 orphaned and 0 missing**.

### Gates, after

Every pre-existing number unmoved. Two moved by exactly what was added — the theme gate's
surface count, by the 49 answering-surface rows written into its budget, and the two
artifact sizes, by the CSS and the gate's own new code.

```
verify_theme         All good: 14 exemptions · 58 -> 107 contrast surfaces x 2 themes,
                     tightest text 4.61:1 (.q-hint [light]), faintest state 1.11:1
                     (.opt hover [light]) · 1 held below the standard floor on purpose ·
                     46 read their ink out of the stylesheet · the 375px topbar ·
                     the 50px id column · the closed drawer is out of the tab order
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3160 per-option explanations · 6572 live draws,
                     4384 options picked and read back · every bank within its budget
verify_circuits      All good: 82 circuit exercises, 348 checks · 543 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1457 analyses, 84 refusals · 15 plots · 380 published
                     schematics, 359 with a DC point, all three ways
verify_derivations   All good: 1170 steps across 46 courses
verify_labs CS201    All good: 6 labs
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12706 KB — unchanged ·
                     inlined 13893 -> 13897 KB · shell 1159 -> 1163 KB, of 1536
```

Beyond the gates: every ratio in this entry computed from the WCAG 2.1 sRGB formula against
the composited stack, before the fix and again after; the 375px column summed from the
stylesheet's own lengths and the grid it actually declares at that width; the target sizes
of four control kinds computed rather than assumed; the `--lime`-as-ink instances and the
sub-11px rules **counted** rather than estimated, at 35 and 55; and the gate run against
**16 mutations — 15 it had to reject and one it had to pass** — which is the run that found
it was rejecting only 2 of 14 to begin with, and the reason this entry has a machinery
section at all.

---

## Cycle 12 — TRACK 6: Edge Cases, Resilience & Accessibility

*(the runner labels this commit "cycle 6"; its counter restarts per run and this log's
does not. Cycles 1–5 of the current run are entries 7–11 above.)*

**Target: `src/desk.js` — the notepad and calculator that open as a modal over whatever
the learner is doing.** The whole file: its expression language, its storage, its modal
and its stylesheet.

One subsystem, and the one this track was left. Track 6's row of the curriculum names
three files — `src/app.js`, `src/desk.js`, `src/circuit.js`. Cycle 6 took the schematic
editor's input, focus and lifetime layer and left `app.js` and this. **No cycle has ever
audited `desk.js`**, and it is where a Track 6 defect is least likely to be found by
accident: a modal nobody opens on a route nobody is graded on. It is also the one file
in the codebase that carries its own CSS, which turned out to matter far more than it
sounds.

### Baseline, captured before any edit

```
82 circuit exercises / 348 checks · 543 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1170 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     · 3160 per-option explanations · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1457 analyses, 84 refusals,
     380 published schematics / 359 with a DC point
theme: 14 written exemptions · 107 contrast surfaces x 2 themes ·
     tightest text 4.61:1 · 46 read their ink out of the stylesheet
build: 3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers · 3 tune models ·
       15 symbols · 62 payloads totalling 12706 KB · inlined 13897 KB · shell 1163 KB
```

### The defect that made this cycle worth doing

**`tools/verify_theme.mjs` reads `src/index.head.html`. The desk's CSS is not in it.**

The file says so itself, in its own header, as a design decision with a reason attached:
*"This is the one file in the codebase that carries its own CSS … a modal that is inert
until summoned pays for none of it until it is opened."* The reasoning is sound and the
consequence was never followed up. `theme_budget.json` held **107 surfaces and not one
of them from this file** — so for as long as both have existed, the gate that measures
every colour in the application in both themes has been measuring every colour except
these, and the curriculum's own invariant, *every colour from a token*, was never applied
here either.

This is not the same as nobody having looked. It is worse: the *mechanism* that would
have looked could not reach the file, so five cycles of contrast work passed it by while
reporting complete coverage.

**Fixed at the seam rather than by copying the CSS somewhere the gate can see it.**
`ensureStyle`'s inline `const css = [...]` became a `deskCss()` function, exposed as
`Desk.css()`, and the gate loads `src/desk.js` through the same public entry point the
app uses and walks both stylesheets as one. So what is measured is what ships, the rules
stay in the file that owns them, and the modal still builds nothing until it is opened.
The desk's two own tokens (`--dsk-veil`, `--dsk-shadow`) now reach `tokensFrom()` as
well, so they are tokens to the gate and not literals.

**107 → 135 surfaces. The 28 new ones are this file, and six of them failed on the first
run.**

### The attacks

**4. UX & Accessibility Hardener** — taken first, because this track's brief is mostly
its brief. Every ratio below was computed by the existing gate from the WCAG 2.1 sRGB
formula against the composited stack, before the fix and again after.

- **The answer is 4.10:1 in the light theme.** `.dsk-val` is `--lime` on
  `--surface-solid`, and it is the number the calculator exists to produce. This is
  *exactly* the defect cycle 6 found on `.ckt-tab td:last-child` — the schematic editor's
  result table, also the answer, at 4.06:1 — and cycle 11 found again on `.opt code` at
  3.51. The token minted to fix it, `--accent-ink`, has existed since cycle 5. It had
  never been applied here because nothing here was ever measured.
- **Five more instances of the same trap in the same file.** `.dsk-title` 3.77,
  `.dsk-empty code` 3.69, `.dsk-tips code` 3.77, `.dsk-pick[aria-pressed=true]` 3.69 —
  the pad you are currently on, so the light theme again makes the current state fainter
  than the states you are not in — and `.dsk-mini.on` 3.89.
- **`.dsk-mini.on` and `.dsk-in .car` are the *other* half of the trap**, and the file
  had already got it right three lines away. Both sit on `--editor`, which is dark in
  both themes; `.dsk-mini` and `.dsk-in input` correctly take `--on-editor-2` and
  `--on-editor`, the tokens cycle 2 minted for a surface a theme cannot help. The lit
  state and the prompt caret took `--lime` instead. The caret measures **4.47:1** in the
  light theme, which is the figure cycle 2 recorded for this exact pair — it cleared the
  3:1 graphical floor and so was never flagged, and it is a `›` on the box a learner
  types into.
- **Checked and found sound, recorded so the next cycle does not re-derive it:** the
  focus trap is real and complete — `onKey` wraps Tab in both directions, `focusables()`
  excludes the roving tablist's `tabindex="-1"` and the hidden pane's controls by
  measurement rather than by selector, Escape and Alt+K both close, `.app` takes
  `aria-hidden` on open and has it *removed* on close rather than set to false, and
  `lastFocus` is restored with `preventScroll`. The tablist is one Tab stop with
  Left/Right/Home/End, which is what `role=tab` promises. `prefers-reduced-motion` is
  honoured in the desk's own CSS. The history rows are reachable: `.dsk-ex` is a real
  `<button>`, `.dsk-val` is `role=button` with `tabindex=0` and an Enter/Space handler,
  and `.dsk-send` reveals itself on `:focus-visible` and not only on `:hover`. None of
  this needed touching, which is worth writing down.

**3. Simulation Auditor.** Its brief is zero, negative, enormous and identical values, so
the expression language was driven with all four, plus the two the brief does not name
and a text box invites: very long, and very deep.

- **"Maximum call stack size exceeded", shown to the learner as the account of their own
  arithmetic.** The parser is recursive descent at about eight frames per bracket and had
  no depth limit, and `evaluate()`'s catch repeated `err.message` whatever it was. So a
  deep enough expression put a JavaScript internal in the history row, saved it, and —
  since cycle 6's work gave this modal a live region — **read it out to a screen reader**.
  Reached at 5000 nested brackets and, by a different route, at a 20000-term sum: the
  `+` parser is a loop, so that one overflows in `evalNode` walking the left-leaning AST
  rather than in `parse`. Both are a paste, not a typo.
- **A history row keeps the source it was worked out from, and eighty of them are
  serialised into `localStorage` on every result.** Nothing capped the expression, so
  nothing capped the store. This is the mechanism that fills the quota, and the next
  finding is the mechanism that hides it.
- **The "unrounded value" is rounded three figures harder outside 1e-4..1e12.**
  `rawNum` uses `toPrecision(10)` in the middle of its range and `toExponential(6)` —
  seven figures — outside it. The dim line under every result exists so that *"a learner
  checking whether 3.20 k really was 3197.28 should not have to take it on faith"*, and
  outside that range it was asking for exactly that faith: `2^40` read `1.099512e+12` for
  1099511627776. Outside that range is also where a picofarad and a gigahertz live.
  Found by the new gate, not by hand — the check that the reading round-trips to the
  value the history actually holds.
- **Checked and found sound, recorded rather than changed:** `par2` refuses `x || -x`
  and returns 0 for a short across anything, which is right. `Math.pow` catches the
  negative-fractional case explicitly. Division and modulo by zero are named. `asin`
  and `acos` state their domain. Every overflow returns "larger than this can hold"
  rather than `Infinity`, and every `NaN` is caught before it can be displayed. The
  window can be resized mid-drag without stranding the modal: `place()` clamps to the
  viewport and `onWinResize` re-clamps, so a panel dragged to an edge and then squeezed
  comes back. `onDragStart` already handles a `pointerdown` with no real pointer.
  `4k7 || 10k` gives 3.20 k, agreeing with the schematic beside it.

**1. Senior Educator** and **2. Assessment Inquisitor** have no prose and no graded
question in a calculator, so both were pointed at the thing in scope they can judge:
whether what it says is written for a learner or merely emitted.

- **The engine's sentence is not a sentence.** "Maximum call stack size exceeded" names
  no cause the learner controls and suggests no next step. Both new limits refuse **by
  name**: *"that is 40001 characters long — this box works out expressions up to 1000.
  Name the parts and combine them"*, and *"that is nested more than 64 brackets deep —
  work it out in a few steps, or name the parts"*. Both point at `r1 = 4k7`, which is a
  feature the language already has and this is the moment to mention it.
- **Refusing beats truncating, and the difference matters here.** A `maxlength` on the
  input would have bounded the store in one line, and a pasted expression cut at 1000
  characters returns a confident wrong answer. The limit is enforced where the answer is
  computed, not where the text is typed.

### The persistence defect

**`saveState()` threw away the one thing that told it the write had failed.**

`writeJSON` returns false when `localStorage` refuses — a full quota, a private window,
storage switched off. `flushSave`, which saves the *note*, has always checked it and
said "could not save — storage is full". `saveState` called the same function and
discarded the boolean.

`saveState` is the one that carries **the history, the variables, `ans`, the angle mode
and the panel's geometry** — every calculation made in the session and every value the
learner named. So a learner whose store was full worked for an hour, closed the tab, and
found an empty calculator, having been told nothing at any point. The function that
reports lives on the other tab.

Fixed, and the fix was wrong the first time in a way worth recording — see below.

### What changed

**Colour — the six the gate rejected, and two it did not.** Dark was already clear
throughout and barely moves; this repairs the broken theme without redesigning the
working one.

| surface | light before → after |
|---|---|
| `.dsk-val` — **the answer** | **4.10 → 5.79** |
| `.dsk-title` — the modal's own name | **3.77 → 5.34** |
| `.dsk-tips code` — the examples in the help | **3.77 → 6.52** |
| `.dsk-empty code` — the worked example before anything is typed | **3.69 → 6.37** |
| `.dsk-pick[aria-pressed=true]` — the pad you are on | **3.69 → 5.21** |
| `.dsk-mini.on` — the lit DEG/RAD, on the dark editor ground | **3.89 → 12.79** |
| `.dsk-in .car` — the prompt caret, same ground, never flagged at 3:1 | **4.47 → 14.68** |
| `.dsk-send:hover` — send this result to the note | to `--accent-ink` |

No new token was minted. `--accent-ink` (cycle 5), `--code-ink` (cycle 11) and
`--on-editor-lime` (cycle 2) already existed for precisely these three situations; the
work was recognising which of the three each surface was in. The two code spans take
`--code-ink` because that is what a code span takes everywhere else in the app.

**The language gained two limits and a backstop.** `SRC_MAX = 1000` characters, checked
before tokenising; `DEPTH_MAX = 64`, counted in `parsePrimary` where the grammar actually
re-enters itself. Both far past any expression anyone writes and far short of the
engine's stack. And `evaluate()`'s catch now distinguishes a `calc` error — a sentence
written for a learner — from anything else, which becomes "that was too much to work out
in one go" rather than being repeated verbatim.

**`rawNum` carries ten significant figures in both branches.**

**`saveState` reports.** It records whether the write landed, marks the panel, and writes
the reason above the input box — because the notes tab has a place for this and the
calculator does not. The announcement is folded into the sentence `run()` was already
going to say: *"2+2 equals 4 — but it could not be saved; storage is full, so this will
not be here next time."*

**A new gate — `tools/verify_desk.mjs`.** This file had no gate at all. It mounts the
**real modal** — `src/desk.js` loaded with `document`, `window`, `localStorage` and
`navigator` passed in as parameters, on the `El` stub `dom_stub.mjs` already provides for
the two circuit gates — and drives it. Five sections:

- **The language, at the extremes.** 55 expressions: zero, negative, enormous, identical,
  malformed, deep and long. None may throw out of `evaluate()`, and no message may
  contain engine text. "log of zero is undefined" is struck out first, because that is
  mathematics using the word and not JavaScript.
- **The stack.** The six worst shapes the grammar allows, at exactly the longest input
  the box accepts — nested brackets, nested calls, a long sum, a long product, unary
  depth, an argument list — none reaching the engine's stack. And both limits must refuse
  **by name**, which is what makes them load-bearing rather than merely defensive.
- **What it shows is what it holds.** Ten results whose unrounded reading round-trips to
  the double the history keeps, so clicking a value and carrying it with `ans` cannot
  diverge.
- **Persistence, driven both ways.** A `localStorage` that refuses every write must be
  reported *in the live region* and *on the panel* — asked separately — and one that
  works must not be, and the result must be announced either way.
- **The stylesheet is still reachable**, so the wiring this cycle added to the theme gate
  cannot be quietly removed.

The gate was not trusted until it was seen to fail. **Eighteen mutations, eighteen
intended verdicts**, across both gates: each cap removed alone and both together, the
engine error repeated verbatim with the caps kept and with them gone, `saveState`
discarding the boolean again, `saveState` returning true whatever the store did, the
panel warned with the live region silenced, the live region kept with the panel silenced,
the unrounded reading back to seven figures, `Desk.css()` removed, four colour reverts
including the answer, and a bare hex planted on a desk rule.

### Found in my own work, and fixed

- **My first fix for the storage warning was a warning nobody hears.** I had `saveState`
  call `say()` itself, suppressed to once per run of failures. `show()` calls `saveState`
  during `open()`, so the warning fired the moment the desk opened — and then `run()`
  announced the result 60 ms later, and `say()` cancels whatever is pending. The live
  region ended up reading "2+2 equals 4" with the warning gone, and every later failure
  was suppressed because one had already been issued. **Caught by the gate's own control
  case failing after the mutation run had passed.** The state is now recorded in
  `saveState` and folded into the sentence `run()` was already saying, so both facts
  arrive in one announcement that is true about both.
- **A condition in my own gate that let four mutations through.** The "is this engine
  text" test tried to allow the mathematical "is undefined" and reject the JavaScript one
  in a single expression, and got it wrong: the first mutation run **rejected 9 of 13**,
  passing the depth cap removed, the length cap removed, and both. Strike the
  mathematical phrase out first, then test what is left. This is cycle 11's finding
  happening again one file over — a check that reads plausibly and enforces nothing — and
  it is the whole argument for the mutation run.
- **An assertion covering two channels at once.** The storage check asked whether the
  live region *or* the panel carried the message, so a mutation that silenced only the
  announcement passed. The learner that mutation strands is the one reading with a
  screen reader. Asked separately now.
- **Two mutations whose expected verdict was mine to correct, not the gate's.** With
  either cap in place the other's inputs are refused, so removing one alone changes
  nothing a learner sees — and with both gone the new backstop still converts the engine
  error, so no engine text escapes either. My first expectation was that any of these
  should fail. What actually earns the caps their place is that they refuse *by name*, so
  that is what the gate now checks, and all three cases became genuine failures rather
  than being written down as expected passes.

### Left alone, deliberately

- **`src/app.js`'s own persistence layer was not audited** — `P`, `saveSoon`,
  `resetProgress`, the progress export and import, `warnNoStorage`. It is the third file
  in Track 6's row, it is where a storage defect costs a learner their whole record
  rather than their calculator history, and it is a cycle of its own. This is the main
  debt this cycle leaves.
- **`state.vars` has no cap and is never pruned.** A learner can name values without
  limit and they persist forever. Each is a short name and a double, and the 1000-character
  input now bounds the name; capping the *count* would silently delete a value someone
  deliberately named, which is worse than the leak. Recorded with the reason rather than
  fixed.
- **`0^-1` reports "the result is larger than this can hold".** It is `Math.pow(0,-1)`,
  so the message is true of the result and not of the cause. Defensible; the division
  operator names zero properly, and inventing a special case for a power would be a
  worse rule than the one already there.
- **`1e-320/1e10` returns 0.** A silent underflow, and the alternative — refusing every
  subnormal — would refuse arithmetic that is correct. Left, recorded.
- **The MCU sketch panel and the workbench were not touched.** Cycle 6 recorded the first
  as its own subsystem and that has not changed.
- **`P.dim` at 2.93:1 and `P.faint` at 1.86:1 on the canvas.** Cycle 2 measured them and
  handed them to Track 5; cycles 5, 6, 8 and 11 have each recorded them again without
  taking them. That is now **five cycles**, and cycle 11's case for making them a target
  rather than a leftover stands unchanged. They are in `src/studio.js`, they are not this
  file, and a Track 6 cycle taking them would change the visual weight of 13 visualisers.
  Cycle 5's candidate values still stand: `#6B7280` → 4.07, `#767D8A` → 4.75,
  `#7E8694` → 5.36.
- **The desk goes full-bleed below 560px**, so cycle 11's correction of the narrowest
  lesson column to 275px does not reach it. Checked rather than assumed.
- **No author file, no `catalog/*.json`, no lesson id and no schema was touched**, so
  `emit.py` was not run and the staleness guard is not armed. The mechanical confirmation
  is that the payload total is **12706 KB before and after**.
- **`docs/programs` holds 64 payloads against 62 in the current generation.** The rolling
  window, as cycles 1–11 all established. Verified rather than assumed: 3 generations
  retained, 64 files on disk, all 64 named by a retained generation, **0 orphaned and 0
  missing**.

### Gates, after

Every pre-existing number unmoved. Three moved by exactly what was added — the theme
gate's surface count, by the 28 desk rows written into its budget, and the two artifact
sizes.

```
verify_desk          All good: 61 expressions at the extremes answered without an
                     engine error · 6 worst-case shapes at the 1000-character limit,
                     none reaching the engine stack, both limits refusing by name ·
                     10 readings that round-trip to the value held · a refusing store
                     reported in the live region and on the panel, a working one not ·
                     the stylesheet handed to the theme gate                    [NEW]
verify_theme         All good: 14 exemptions · 107 -> 135 contrast surfaces x 2 themes,
                     tightest text 4.61:1, faintest state 1.11:1 · 3 held below the
                     standard floor on purpose · 46 -> 74 read their ink out of the
                     stylesheet · the 375px topbar · the 50px id column · the closed
                     drawer is out of the tab order
verify_circuits      All good: 82 circuit exercises, 348 checks · 543 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1457 analyses, 84 refusals · 15 plots · 380 published
                     schematics, 359 with a DC point, all three ways
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3160 per-option explanations · 6572 live draws
verify_derivations   All good: 1170 steps across 46 courses
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12706 KB — unchanged ·
                     inlined 13897 -> 13903 KB · shell 1163 -> 1168 KB, of 1536
```

Beyond the gates: every ratio in this entry computed by the existing theme gate from the
stylesheet's own tokens rather than eyeballed, before the fix and again after; the two
new gates run against **18 mutations, 18 intended verdicts** — a run that began by
rejecting 9 of 13 and is the reason this entry has two findings about its own gate; the
parser driven over 61 expressions at the extremes before any limit was chosen, so the
limits were set against measured behaviour and not guessed; and the payload window
checked for orphans rather than assumed.

---

## Cycle 13 — TRACK 1: Content & Conceptual Depth

*(The runner labels this cycle 7 — its counter restarted when the second run began,
while this log kept counting. Commit `ee95ded`, labelled "cycle 1", is this file's
cycle 7. Recorded so the next cycle does not go looking for cycles 7–12 in the
history under those names.)*

**Target: MA112 (Calculus II — Integration & Series), modules 5–11 — the analytic
core.** One course, one contiguous block: the Fundamental Theorem, substitution,
parts, trigonometric integrals, partial fractions, applications and power series.
Each of the seven held **a `quiz` and nothing else**, so a learner met the technique
as a bulleted claim and was examined on it in the next unit.

Chosen on measurement rather than on the shape. Scoring all 62 courses by units per
module, MA112 sits at **2.09**, the lowest in the catalogue among courses with a real
question bank — 11 modules holding 23 units. It is also the course cycle 1's target
runs into: MA111's modules 4–9 were six consecutive quiz-only modules, cycle 1 gave
them readings, and its sequel had seven of the identical defect that nothing had
picked up. And it is a prerequisite of MA201, which is the *next* worst at 2.09 with
ten bare modules, so repairing it in this order is the one that compounds.

M1–M4 were excluded: M1 is the densest module in the course (3 readings, 3
derivations, a lab) and M2–M4 each carry a full lab and teach by construction, which
is cycle 1's MA111 reasoning applied unchanged.

### Baseline, captured before any edit

```
82 circuit exercises / 348 checks · 543 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1170 derivation steps across 46 courses (MA112: 18)
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3160 per-option explanations · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1457 analyses, 84 refusals, 380 schematics
desk 61 expressions · theme 14 exemptions, 135 contrast surfaces
MA112: 11 modules · 23 units · 3 read · 3 derive · 10 bare modules · 5 labs
       42 questions (longest-is-key 21, budget 21, margin +7.4)
       1164 math fragments: 1164 render, 0 raw, 22 swallowed, 0 unpaired
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads, 12706 KB ·
       inlined 13903 KB · shell 1168 KB
catalogue: 62 courses, 368 modules, 1885 units, 239 readings
       46030 math fragments: 1053 raw, 161 swallowed
```

### The attacks

**1. Senior Educator.** Seven findings, all acted on.

- *Announced, never derived, seven times over.* Fixed: seven readings and seven
  derivations, each deriving what its module states. Substitution comes out of the
  chain rule plus the Fundamental Theorem in two lines; parts out of the product rule
  in the same two; LIATE is replaced by the criterion underneath it; the three
  orthogonality integrals are computed rather than listed; the partial-fraction
  decomposition is shown to exist by counting unknowns against equations; the five
  formulas of module 10 are shown to be one template; and the arctangent series is
  derived at the endpoint where the licence to derive it does not reach.

- **The course teaches the Fundamental Theorem twice and says so nowhere.** M1's
  second reading — *"The Fundamental Theorem, and the two things it says"*, 1498 words
  — proves both parts, works the moving-limit trap, reads $\mathrm{Si}(x)$ off part
  one, and closes on $\int_{-1}^{1}\frac{\mathrm{d}x}{x^{2}} = -2$. M5 then
  re-announces the same theorem in five concepts bullets and examines it. The two
  halves of this course — M1–M4 numerical, M5–M11 analytic — were written
  independently and never joined. This was found by reading M1 before drafting M5, and
  it changed what M5 became: not a second proof, but the search the theorem leaves
  open. Obtaining a $G$ with $G' = f$ has no algorithm and no composition rule, and
  M6–M9 are the collected techniques for conducting it. M5's summary was rewritten to
  say that, and its reading is now the hinge between the two halves rather than a
  duplicate of M1.

- **The one orthogonality claim that matters is stated falsely, in a concepts
  bullet.** M8 said $\int\sin(mx)\sin(nx)$ and $\int\sin(mx)\cos(nx)$ over a full
  period "vanish unless the frequencies match". True of the first pair; **false of the
  second**, which is zero for *every* $m$ and $n$ including $m = n$, because
  $\sin(nx)\cos(nx) = \frac{1}{2}\sin(2nx)$ is a pure sinusoid at double the frequency.
  The false version is not a harmless simplification: it says the sine coefficient at
  frequency $n$ picks up the cosine content at frequency $n$, which would mean Fourier
  analysis does not separate. Verified by integrating all three products symbolically
  at $(m,n) = (3,5), (3,3), (2,2), (1,4)$, and worked in the reading on
  $f(x) = 2\sin 3x + 5\cos 3x - \sin 5x$, where extracting $b_3$ returns exactly $2$
  and the $5\cos 3x$ term — larger than the one being measured, and at precisely the
  frequency being measured — contributes zero.

- **The module teaches "solve for the integral" and never says when it is legal.**
  M7/Q3 walks the learner through $I = e^{x}\sin x - e^{x}\cos x - I$ and cancelling.
  The identical manoeuvre on $\int\frac{\mathrm{d}x}{x}$ with $u = \frac{1}{x}$ gives
  $I = 1 + I$ and hence $0 = 1$. The difference is the coefficient: $-1$ collects to
  $2I$ and divides, $+1$ collects to $0\cdot I = 1$ and does not. The reading derives
  the condition, gives the second reading of the same fault (an indefinite integral is
  a family, and the two $I$s are different members of it), shows the definite version
  reading $0 = 0$, and then points out that the sine reduction formula is safe for
  exactly this reason — collecting leaves a factor of $n$.

- **The classical $\frac{\pi}{4}$ series is obtained by a step the next question
  forbids.** M11/Q3's explanation puts $x = 1$ into the integrated series; M11/Q4
  answers that term-by-term integration is valid "strictly inside the radius, and the
  endpoints must be checked separately". At $t = 1$ the series being integrated is
  $1 - 1 + 1 - \cdots$, which has no sum. The reading and the derivation replace the
  appeal with an argument that needs no endpoint theorem: integrate the **finite**
  identity $\frac{1}{1+t^{2}} = \sum_{k=0}^{n}(-1)^{k}t^{2k} + R_n(t)$, which is exact
  algebra at every real $t$, and bound $|R_n| \le \frac{1}{2n+3}$ by dropping the
  denominator. That establishes convergence *and* prices it: 500 terms for three
  digits, against module 2's adaptive Simpson reaching nine on the same integrand.

- **The slice template's admissibility condition is missing, and it is not
  decorative.** M10 lists five formulas and never says why a curved slice may be
  replaced by a straight one. The condition is that the per-slice error carry one more
  power of $\Delta x$ than the slice contributes. Slicing a cone into cylinders
  satisfies it for volume and violates it for lateral area: the disc integral gives
  $\frac{\pi}{3}$, correct, and the cylinder integral gives $\pi = 3.1416$ against the
  true $\pi\sqrt2 = 4.4429$ — **29.3 per cent short, at every panel count**. The
  general factor is $\sqrt{1+m^{2}}$, equal to $1$ exactly when the surface is flat,
  which is why nobody meets this failure until the first cone.

- **`+C` is one constant only on an interval.** The general antiderivative of
  $\frac{1}{x}$ carries two independent constants, because the mean value theorem
  argument behind "any two antiderivatives differ by a constant" runs inside one
  interval at a time and the domain is in two pieces. Stated nowhere; it is the same
  hypothesis whose absence produces M1's $-2$.

- *Left alone:* M6's existing bullet that a reverse substitution needs $h$
  one-to-one was already correct **and** already said the forward direction needs no
  such condition. The reading spends that rather than restating it, showing
  $\int_{-1}^{1}2x\cos(x^{2})\,\mathrm{d}x$ substituting to an integral from $1$ to
  $1$ — alarming, and right, confirmed against the odd-symmetry argument.

**2. Assessment Inquisitor.** All 42 questions in the course were checked against the
mathematics rather than skimmed. **Every key is correct and no option text was
changed**, which is confirmed mechanically rather than asserted: the 42 stems, option
sets and keys are byte-identical to `HEAD`, and the gate reports MA112 unmoved at
longest-is-key 21 against a budget of 21 with margin +7.4. Three explanations gained
scope they lacked — the coefficient condition in M7/Q3, the mixed-pair case in
M8/Q2, the endpoint licence in M11/Q3 — all in the `why`, none in an option, so the
answer-tell budget could not move.

Recomputed rather than assumed, so the next cycle need not: $\int_1^e\frac{dx}{x} = 1$;
$\int_5^3 f = +5$ from $\int_3^5 f = -5$; $A'(x) = \sin(x^{2})$; the area between
$y = x$ and $y = x^{2}$ as $\frac12 - \frac13 = \frac16$; $\frac{5}{(1+4)} = 1$ by
cover-up; $\int_0^{\pi}x\sin x\,dx = \pi$; $\frac12 kL^{2}$; the discriminant
$36 - 52 = -16$; $\int e^{x}\sin x = \frac12 e^{x}(\sin x - \cos x)$; and the geometric
series at $x = \frac12$ summing to $2$. All hold.

**3. Simulation Auditor.** M5–M11 contain no sandbox, tune, build or schematic
`numeric`, so there is no draw loop or solver in the target. The persona was pointed
at the two things in scope that no gate covers — **what the renderer actually draws**,
and **arithmetic in prose** — and the first is where the largest finding is.

- **22 fragments in MA112 draw a fraction as a single wrong number, and it is worse
  than cycle 7 recorded.** `src/studio.js` tokenises `12` as one number, so
  `\tfrac`/`\frac`'s first `group()` swallows it whole. Cycle 7 described the symptom
  as "a single wrong number"; driving the shipped renderer over each fragment shows
  **two** distinct failures. At the end of an expression, `\frac13` produces
  `<mfrac><mn>13</mn></mfrac>` — an `mfrac` with one child — so
  $\int_0^1 x^{2}\,\mathrm{d}x = \frac13$ reads **"= 13"**. Mid-expression it is
  worse: `R_n - \frac13 = \frac{1}{2n}` produces `<mfrac><mn>13</mn><mo>=</mo></mfrac>`
  — **the equals sign is eaten as the denominator**, and the equation loses its
  relation entirely. Likewise `\frac13 + 0.125 + …` draws "13 over +". All 22 were in
  M1, the one dense module, including its derivation's closing line and three blanks
  explanations. All 22 repaired by bracing; MA112 is now **0 swallowed**.

- **A third failure mode nothing in this repository had measured: inline mathematics
  broken across a source line is not rendered at all.** `protectMath` in
  `src/engine.js` matches inline maths with `/(^|[^\\])\$([^$\n]+?)\$/` — the character
  class excludes a newline — and it runs on the raw source *before* markdown, so a
  `$…$` that wraps onto the next line is never matched and reaches the page as literal
  dollar signs and LaTeX. It renders nothing and throws nothing, which is why no gate
  and no review round has ever caught it. **273 prose lines across 18 courses** are in
  this state, led by EE141 64, EE211 30, EE231 26, EE102 22, EE111 and MA111 20 each.
  MA112 was at zero and is still at zero.

- **Every number written into the seven readings was computed before it was written,**
  in SymPy: the trapezoid rule on $\int_1^2\frac{dx}{x}$ giving $T_4 = 0.6970238$
  against $\ln 2$, with M1's own error term solved for $\xi = 1.39025$ and confirmed to
  lie in $(1,2)$; $n = \lceil 1000/\sqrt6\rceil = 409$ panels for six digits, and
  $|T_{409} - \ln 2| = 3.74\times10^{-7}$ under the promised $9.96\times10^{-7}$;
  $\int_0^2 xe^{x^{2}}dx = 26.799$ against the unmoved-limits $3.1945$, a factor of
  $e^{2}+1 = 8.39$; $W_6 = \frac{5\pi}{32} = 0.490874$; $\ln(1+\sqrt2) = 0.881374$;
  $230\sqrt2 = 325.27$; the three orthogonality integrals at four frequency pairs;
  $\int_3^4\frac{dx}{x(x-2)^{2}} = \frac14\ln\frac23 + \frac14 = 0.148634$, with the
  claimed antiderivative of $\frac{3x+5}{x^{2}+4x+13}$ differentiated back to the
  integrand; the cone's $\frac{\pi}{3}$, $\pi\sqrt2$ and $\pi$; the arc length of
  $y = x^{2}$ as $1.478943$, bracketed by the chord $1.41421$ and the two-segment path
  $1.46043$; $|\frac{\pi}{4} - \frac{13}{15}| = 0.081269$ under the bound
  $\frac17 = 0.142857$; seven terms of $\int_0^1 e^{-x^{2}}$ giving $0.7468360$ with an
  error of $1.19\times10^{-5}$ under the next term's $1.32\times10^{-5}$; $\sqrt{1.2}$
  to four binomial terms as $1.09550$ against $1.0954451$; $\sum n(\frac12)^{n-1} = 4$;
  and $\int_2^3\frac{x^{3}}{x^{2}-1}dx = 2.99042$.

- **All 42 new derivation answers were truth-checked separately from the gate,** each
  against an expression derived independently of the one written into the catalogue —
  42 of 42 agree. Three of them ($R_n$, the $k$-th term's integral, the bound's
  integral) are checked over the integers they are about, because SymPy will only
  answer those with a `Piecewise` carrying edge conditions at $t = -i$, $k = -\frac12$
  and $n = -\frac32$.

**4. UX & Accessibility Hardener.** Content-side, as cycles 1, 4, 7 and 10 established.
Checked rather than assumed: `math[display=block]` carries its own `overflow-x:auto`
and `.article .tw` wraps tables in a scroller, both re-verified in
`src/index.head.html`; no hard-coded colour, no raw HTML and no markdown table was
introduced. Every figure is a fenced `text` block inside `overflow-x:auto`, which is
cycle 4's rule for staying safe at 375px. The fenced listings in these readings are
prose figures rather than runnable programs, so none makes a claim about its own
output that a **▶ Run** button would be needed to check.

### Found in my own work, and fixed

Every one of these was found by a mechanical sweep, and every one is a defect this
cycle had just finished repairing in somebody else's text.

- **Four of my own fractions would have shipped swallowed** — `\frac12 v^2`,
  `x = \frac12`, `x = \frac13`, and `1 - \frac13 + \frac15` — written in the same
  session that rebraced 23 of them. The rebracing pass runs last now, after the
  reading extensions are inserted; running it before them is how the last two were
  left behind.
- **Six of my own fragments would have shipped as raw markup.** Five are the escaped
  space `\ ` — cycle 10's finding, in `20\ \mathrm{m/s}` and four like it — and one is
  `\overset`, which I had already removed from one reading and not from another. Two
  more, `\begin{cases}` and a second `\overset`, were caught before the first apply by
  checking the draft against the renderer's own command tables.
- **Fifteen of my own inline fragments crossed a source line**, which is the third
  defect class above, discovered *because* I was auditing for it. Repaired by a reflow
  pass that joins any line leaving an inline `$…$` open, and the pass itself had a bug
  worth recording: the module 11 extension begins on the last line of a fenced listing,
  so the fence toggle was inverted for the whole block and nothing was joined. The
  reflow now takes the starting fence state as an argument.
- **Four of my seven readings came in under the 1200-word target** (1042–1156, all
  above the emitter's 400 floor, so nothing would have failed). Extended with material
  rather than padding: three lookalike integrands over $1+x^{2}$ needing three
  unrelated methods; $\int_0^1\arctan x\,dx$, where parts creates a second factor out
  of nothing; the long division that must precede a decomposition, with the argument
  for *why* — a sum of $\frac{A}{x-r}$ terms tends to zero at infinity and
  $\frac{x^{3}}{x^{2}-1}$ does not; and term-by-term *differentiation*, which the
  module's own bullet claims and my reading had covered in only one direction.
- **Four hedge words in prose I had just written against a brief that names them.**
  Three `simply` and one `obviously`, found by diffing against `HEAD` rather than by
  counting — the file was at 11 before and is at 16 now, and all five additions are
  temporal `just` or contrastive `merely`, which carry meaning.
- **My unpaired-dollar detector over-counted by 54 on its first run**, reporting 357
  where the truth is 273. A `$` inside code is not mathematics: CAP501's
  `^[a-z0-9_]{3,32}$` and its `pbkdf2_sha256$rounds$salt$digest` accounted for most of
  it. Fenced blocks, inline code spans and whole source-bearing fields are excluded
  now. A measurement that condemns correct content is the failure cycle 3 recorded
  about its own gate, and reporting 357 in this entry would have been the same error
  one layer up.
- **My first truth-check harness scored 30 of 42** and was wrong about all twelve. Six
  were stale: I had planned M5's derivation as a mean-value-theorem telescope, changed
  it to the logarithm once M1's reading made the telescope a duplicate, and left the
  old expected values in the harness. Three were `e` read as a symbol rather than as
  Euler's number — which is the repository's own convention, confirmed rather than
  changed: **15 derive answers in 8 courses already use a bare `e^`**. Three were
  SymPy `Piecewise` results, handled above.

### What changed

**Fourteen new units in seven modules** — one `read` and one `derive` each.

| Module | Reading | Words | Derivation | Steps |
|---|---|---|---|---|
| M5 | The antiderivative as something you have to go and find | 1367 | The exponent the power rule misses, and the function that fills the gap | 6 |
| M6 | One line of chain rule, and the hypothesis that appears only in one direction | 1390 | One substitution, done twice: once with the limits moved and once without | 6 |
| M7 | The product rule backwards, and when solving for the integral is allowed | 1445 | The sine reduction formula, and the coefficient that licences it | 6 |
| M8 | Which products vanish, computed rather than remembered | 1350 | Three orthogonality integrals, and the one that is zero even at equal frequencies | 6 |
| M9 | Why the decomposition exists, and what its coefficients cost | 1308 | Three coefficients, one check, and the piece that is not a logarithm | 6 |
| M10 | One template, five formulas, and the slice that is not good enough | 1417 | One cone, two slicings, and the factor a cylinder leaves out | 6 |
| M11 | Term-by-term integration, with the remainder carried instead of assumed | 1370 | The arctangent series at the endpoint, with its remainder carried | 6 |

**9,644 new words**, every reading inside the 1200–2500 target and in line with M1's
existing three (1322, 1333, 1498). MA112: 23 units → 37, 3 readings → 10, 3 derivations → 10,
10 bare modules → 3, and 2.09 units per module → 3.36. Every reading carries a worked
example through to a checked number, names the mistake people make and says why it is
tempting, and closes on where the idea stops holding.

**Sixteen concepts bullets added or repaired** across M5–M11, so the new material is
reachable from the list a learner skims and not only from the reading: the search the
Fundamental Theorem leaves open, the two constants on a disconnected domain, the
logarithm as the antiderivative the power rule cannot reach, differentiating to check
and to correct, Liouville; the two-line proof of substitution and the folding $g$ it
survives, and the unmoved limits priced at $e^{2}+1$; the terminating-derivative-chain
criterion behind LIATE, and the coefficient that licences solving for $I$; the counting
argument for the decomposition, cover-up's reach, the check at an unused $x$, and the
ill-conditioning at near-equal roots; the slice-error order and the cone that violates
it; the endpoint, the non-analytic smooth function, and a radius with no real-line
explanation. The M8 orthogonality bullet was **replaced** by two that state the two
cases correctly; every other bullet in these modules is untouched.

**Twenty-three swallowed fractions repaired in M1** — the whole of MA112's share of
the catalogue-wide debt cycle 7 measured and handed on, in 22 fragments, one of which
carried two.

### Left alone, deliberately

- **M2, M3 and M4 still hold a lone lab.** Each is a full lab with a reference
  solution the gate runs, so they teach by construction rather than examining cold,
  which is not the defect this cycle was chasing. They should get readings; that is a
  following cycle. Three bare modules remain against ten.
- **The 42 questions were audited and, apart from three `why` extensions, not
  changed.** They are Track 3's ground, and MA112's inherited answer-tell figure (21 of
  42) is cycle 3's recorded debt pinned by `quiz_budget.json`, not this cycle's to
  spend. No option text moved, so it could not have.
- **273 unpaired inline fragments in 18 courses**, measured above and handed on with
  the per-course numbers rather than the symptom. It is the cheapest of the three
  render debts to retire and the only one with no fix in the catalogue at all: it can
  be repaired mechanically, by joining the offending lines, with no judgement about
  what the author meant — and unlike the other two it can also be *prevented*, by
  widening `protectMath`'s inline rule to allow a single newline. Which of those is
  right is a Track 2/5 machinery decision, not a Track 1 one.
- **1053 raw-markup fragments and 139 swallowed fractions outside MA112.** Cycle 7
  measured the first at 1053 and the second at 161; both are unmoved except by this
  cycle's own 22. Cycle 10's refinement stands: 369 of the 1053 are the escaped space
  `\ ` alone, which is one rule in the tokeniser.
- **`\frac` swallowing its argument is still a `studio.js` defect and was not fixed
  there.** Bracing 23 fragments repairs this course; it does not stop the next author
  writing `\frac12`. The tokeniser fix — make `group()` take one digit when it follows
  `\frac` — is provably safe in the same way cycle 10's `DIAGRAM_KINDS` widening would
  be, and it is a Track 2 machinery cycle. Recorded with the two failure modes above so
  it starts from the diff rather than the symptom.
- **`verify_derivations.py` still proves translation rather than truth**, as cycle 1
  established and cycle 7 restated. All 42 new answers were therefore truth-checked
  separately, and the harness is in this session's scratchpad. Nothing about the gate
  was changed: rewriting the spec from inside a cycle it governs remains the wrong move.
- **A bare `e` in a derive answer is read as a free symbol, not as Euler's number.**
  So the reference `\frac{e^4-1}{2}` matches a learner who types `e^4` and not one who
  types `exp(4)`. This is pre-existing and established — 15 answers across 8 courses,
  including EE102, EE131 and CTRL510 — so this cycle followed the convention rather
  than inventing a second one. Recorded because it looks like a defect in the new
  answers and is a property of `MathCheck`.
- **MA201 is the next-worst course in the catalogue and was not touched.** 2.09 units
  per module, ten bare modules, and MA112 is its only prerequisite. It is the obvious
  next Track 1 target and widening this cycle to cover it would have meant fourteen
  units built to no standard.
- **`docs/programs` holds 65 payloads against 62 in the current generation.** The
  rolling window, as cycles 1–12 all established. Verified rather than assumed: 3
  generations retained at 62 each, 65 files on disk, all 65 named by a retained
  generation, **0 orphaned and 0 missing**, covering 62 distinct courses.

### Gates, after

Every pre-existing number unmoved. Three moved by exactly what was added — the
derivation-step count by the 42 new steps, and the two artifact sizes by the content.

```
verify_derivations   All good: 1212 steps across 46 courses   (1170 + 42 new;
                     MA112 18 -> 60)
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3160 per-option explanations · 6572 live draws —
                     unmoved.  MA112: 42 questions · longest-is-key 21 (budget 21) ·
                     margin +7.4 — unmoved, and no option text changed
verify_labs MA112    All good: 5 labs  (M1 8/8, M2 7/7, M3 7/7, M4 8/8, CAP 12/12)
verify_circuits      All good: 82 circuit exercises, 348 checks · 543 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1457 analyses, 84 refusals · 15 plots · 380 schematics
verify_desk          All good: 61 expressions at the extremes
verify_theme         All good: 14 exemptions · 135 contrast surfaces x 2 themes
emit.py MA112        ok — 11 modules, 4 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12706 -> 12796 KB ·
                     inlined 13903 -> 13993 KB · shell 1168 KB — unchanged
catalogue            62 courses, 368 modules, 1885 -> 1899 units, 239 -> 246 readings
```

Beyond the gates: every MA112 math fragment pushed through the shipped
`MathML.render` — **2163 of 2163 draw, 0 raw, 0 swallowed, 0 unpaired**, against
1164 of 1164 with 22 swallowed at baseline; the catalogue-wide totals confirmed to have
moved only by MA112's share (raw 1053 unmoved, swallowed 161 → 139); all 42 derivation
answers truth-checked against independently derived expressions, 42 of 42; every number
in 9,644 new words recomputed in SymPy before it was written; the 42 question stems,
option sets and keys diffed against `HEAD` at 0 changes; 14 lesson ids added and **0
lost**, so no completed work is orphaned; hedge words counted by diff against `HEAD`
rather than by counting twice; and the payload window checked at 0 orphaned, 0 missing.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 5975) was live
throughout, and this cycle is the process it launched — so the lock is this cycle's own
and `emit.py` and `build.mjs` were safe to run. The diff is `catalog/MA112.json`,
`catalog/authors/MA112.py` and the `docs/` build output, and nothing else.

---

## Cycle 14 — TRACK 1: Content & Conceptual Depth

*(The runner labels this cycle 1 — a third run began at 11:05 and its counter restarted,
while this log kept counting. Commit "cycle 1" of run C is this file's cycle 14, exactly
as `ee95ded` was its cycle 7 and `f1a161b` its cycle 13.)*

**Target: MA201 (Probability & Statistics for Computing), the six modules holding a
quiz and nothing else — M2, M4, M5, M7, M8 and M11.** Conditional probability,
continuous densities, joint distributions, tail bounds, estimators, and least squares. A
learner met each as five concepts bullets and was examined on it in the next unit.

This is the course cycle 13 named on its way out, and the measurement holds: **23 units
across 11 modules, 2.09 per module, ten of eleven modules with neither a `read` nor a
`derive`** — the worst in the catalogue now that MA112 has been repaired, and MA112 is
its only prerequisite, so the two compound.

M1 was excluded because it is already the densest module in the course (3 readings, 4
derivations, 4 numerics, a quiz and a blanks unit) and is visibly the model the rest was
never built up to. **M3, M6, M9 and M10 were excluded because each carries a full lab
with a reference solution the gate runs** — they teach by construction rather than
examining cold, which is cycle 13's MA112 reasoning and cycle 1's MA111 reasoning applied
unchanged. That leaves exactly the six modules that examine without teaching.

### Baseline, captured before any edit

```
82 circuit exercises / 348 checks · 21 tune units
216 numeric answers verified, 0 unchecked, 218 figure-only
1212 derivation steps across 46 courses (MA201: 18)
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3160 per-option explanations · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1457 analyses, 84 refusals, 380 schematics
desk 61 expressions · theme 14 exemptions, 135 contrast surfaces
MA201: 11 modules · 23 units · 3 read · 4 derive · 10 bare modules · 5 labs
       35 questions · 901 math fragments: 901 render, 0 raw, 0 swallowed, 0 unpaired
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads, 12796 KB ·
       inlined 13993 KB · shell 1168 KB
catalogue: 62 courses, 368 modules, 1899 units, 246 readings
```

### The attacks

**1. Senior Educator.** Six modules, six findings acted on, plus two false or misleading
claims found in prose the cycle was not pointed at.

- *Announced, never derived, six times over.* Fixed: six readings and six derivations,
  each deriving what its module asserts. Conditioning is shown to satisfy the three
  axioms, so every module-1 theorem transfers instead of being restated; the exponential
  is built from a constant hazard rather than quoted and checked; the correlation bound
  comes out of the non-negativity of a variance, read twice; Chebyshev is derived *from*
  Markov by squaring; the $n-1$ divisor is derived to an exact identity; and the normal
  equations are obtained from two partial derivatives.

- **A concepts bullet in M4 licenses a mistake it does not name.** It said
  $z = (x-\mu)/\sigma$ "puts any of them on one scale", immediately after naming the
  uniform, exponential and normal. Read as "so you can use a normal table", that is
  false, and the size is measurable: an $\mathrm{Exp}(1)$ variable is *already*
  standardised, has mean $1$ and standard deviation $1$, and $P(X \le 0.5) = 1 - e^{-0.5}
  = 0.393469$ against the normal table's $0.308538$ — **$8.5$ percentage points apart on
  a perfectly standardised variable**. The bullet was split into two: one saying what the
  normal is fixed by, one saying that standardising fixes location and scale and never
  shape, with the number. The reading works it.

- **M2/Q5's explanation states something false.** It said $P(A|B)$ and $P(B|A)$ "agree
  only when $P(A) = P(B)$". They also agree whenever the shared numerator is zero:
  disjoint events with $P(A) = 0.3$ and $P(B) = 0.5$ give $P(A|B) = P(B|A) = 0$ with
  marginals nowhere near each other. Verified symbolically. The `why` now carries both
  cases. **No option text was touched**, so the answer-tell budget could not move, and
  the gate confirms it did not.

- **The module teaches the complement rule for conditionals and never says which
  neighbouring statement is false.** $P(A^{c}|B) = 1 - P(A|B)$ is exact — it is A3
  inside the world $B$. $P(A|B^{c}) = 1 - P(A|B)$ is not, and the derivation ends on the
  counterexample: $P(A) = 0.5$, $P(B) = 0.4$, $P(A \cap B) = 0.3$ give $P(A|B) = 0.75$
  and $P(A|B^{c}) = \frac{1}{3}$, which sum to $1.083$.

- **"Independence" is presented as though it were a fact about mechanism.** The reading
  makes it arithmetic: ace and spade are independent in a full deck
  ($\frac{4}{52}\times\frac{13}{52} = \frac{1}{52}$ exactly) and dependent once the two
  of clubs — neither an ace nor a spade — is removed ($\frac{1}{51} = 0.019608$ against
  $\frac{52}{2601} = 0.019992$). Nothing physical changed. The module's own cohort
  example turns out to be exactly the independent case, which is why conditioning on it
  returns $0.60$ unchanged; moving one student breaks it.

- **Pairwise independence is not mutual independence, and M6 assumes the stronger one.**
  Two fair coins with $A$ = first heads, $B$ = second heads, $C$ = they agree: every pair
  is independent at $\frac{1}{4}$, and $P(A \cap B \cap C) = \frac{1}{4}$ against
  $P(A)P(B)P(C) = \frac{1}{8}$. Mutual independence is $2^{n}-n-1$ equations, and
  "independent trials" in module 6 is doing more work than it looks.

- **The concepts list calls the exponential *the* memoryless distribution and never
  justifies the article.** The reading closes the uniqueness: $S(s+t) = S(s)S(t)$ with
  $S(0)=1$ and $S$ non-increasing forces $S(t) = e^{-\lambda t}$, and $S(t) = 1/(1+t)$ is
  shown failing it ($\frac{1}{6}$ against $\frac{1}{4}$).

- **M8 asserts that dividing by $n-1$ "corrects that shortfall exactly" and never shows
  the shortfall.** Derived: $E[\sum(x_i-\bar{x})^{2}] = (n-1)\sigma^{2}$, with the
  worked sample showing the deviations about $\bar{x}$ ($10.58$) genuinely smaller than
  about $13.0$ ($12.20$) or $14.0$ ($13.00$). And the correction's limit is named:
  $s^{2}$ unbiased does **not** make $s$ unbiased — $E[s] = 0.9400\sigma$ at $n=5$ —
  because the square root is concave.

- *Left alone:* M7's existing bullets on Markov, Chebyshev, Hoeffding and the union bound
  are all correct as stated, including the $e^{-2n\varepsilon^{2}}$ rate. The reading
  spends its space on deriving them and on what separates them, rather than restating.

**2. Assessment Inquisitor.** All 35 questions checked against the mathematics rather
than skimmed. **Every key is correct and no option text was changed**, confirmed
mechanically: the 35 stems, option sets and keys are byte-identical to `HEAD`, and the
quiz gate reports every catalogue figure unmoved. One `why` gained the case it was
missing (M2/Q5, above).

Recomputed rather than assumed: $4/12 = 1/3$; $\frac{4}{52}\cdot\frac{3}{51} =
\frac{1}{221}$; $0.70(0.02) + 0.30(0.05) = 0.029$ against the unweighted $0.035$;
$2 \times 0.5 = 1$ for the uniform density; $300/(20 \times 30) = 0.5$; $4+4 = 8$ with
$\sqrt{8} = 2.828$; $E[X^{3}] = 0$ for the symmetric counterexample; $10/50 = 0.2$;
Chebyshev's $1/4$ at $k=2$ against a normal's true $0.0455$; $1000 \times 0.0001 = 0.1$
against an independent $0.0952$; $7/20 = 0.35$; bias $1$, variance $0$, MSE $1$; and
$\mathrm{Cov}(x,y)/\mathrm{Var}(x)$ as the slope. All hold.

**3. Simulation Auditor.** M2, M4, M5, M7, M8 and M11 contain no sandbox, tune, build or
schematic `numeric`, so there is no draw loop or solver in the target. The persona was
pointed at the two things in scope no gate covers — **what the renderer actually draws**
and **arithmetic in prose** — and at the derivation checker, where the largest finding
is.

- **`\varepsilon` renders correctly and is silently dropped by the answer checker.**
  `MathCheck.latexToPy` translates `\frac{\sigma^{2}}{n\varepsilon^{2}}` to
  `sigma**2/n**2` — the `\varepsilon` vanishes and the exponent attaches itself to the
  wrong symbol. `MathML.render` draws it perfectly, so a prompt would show $\varepsilon$
  while the checker graded a different expression. `\epsilon` is handled correctly.
  This was found by testing candidate answers *before* writing them; all six M7 answers
  use `\epsilon`.

- **`\bar` and `\hat` are dropped by the same translator.** `\bar{x}` becomes plain `x`,
  so a barred mean silently collides with the variable it is the mean of. This is why
  the M11 derivation declares `m_x` and `m_y` rather than using bars in its answers, and
  says so in its brief.

- **Two subscripted multi-letter symbols juxtaposed corrupt each other.**
  `\sqrt{S_{xx}S_{yy}}` parses as `sqrt(S_xxS*y*y)`. With a space or `\cdot` between them
  it is correct. M11 step 3 uses `\cdot`.

- **Every number written into the six readings was computed before it was written**, in
  SymPy: the two-machine partition forwards ($0.029$) and backwards
  ($\frac{15}{29} = 0.517$, so machine 2 makes $30$ per cent of parts and $51.7$ per cent
  of defects); the deck independence at $52$ and $51$ cards; the pairwise/mutual coin
  triple; the constant-hazard integration and $E[T] = 1/\lambda$; inverse-transform
  sampling at $U = 0.37$ giving $t = 46.2035$ hours and $F(46.2035) = 0.370000$ back;
  the Weibull hazard at $0.002$ and $0.040$ per hour; the standardised-exponential gap of
  $8.49$ points; the joint table's marginals, $\mathrm{Cov} = -0.0275$,
  $\rho = -0.0747$, $\mathrm{Var}(X+Y) = 0.74$ and $\mathrm{Var}(X-Y) = 0.85$, and its
  three row conditionals $0.600$, $0.556$, $0.500$ against an unconditional $0.550$; the
  four-row bound comparison on $10{,}000$ flips (Markov $0.909$, Chebyshev $0.01$,
  Hoeffding $e^{-50} = 1.93\times10^{-22}$, **exact binomial $7.76\times10^{-24}$** —
  twenty-two orders of magnitude, and the exact figure summed rather than approximated);
  the union bound's exact and worst cases; Markov's failure on $[-10,10]$; the eight-point
  sample through $\bar{x} = 13.45$, $S = 10.58$, $s^{2} = 1.511429$, $s = 1.229402$,
  $\mathrm{SE} = 0.434659$ and $[12.4222,\ 14.4778]$; $c_4(n)$ at $n = 2, 5, 10, 30$; the
  shrinkage optimum $c = \theta^{2}/(\sigma^{2}+\theta^{2})$ and its halved error; and
  the whole regression — $\beta_1 = 0.795$, $\beta_0 = 1.33$, residuals summing to $0$,
  $\mathrm{SSE} = 0.739$, $R^{2} = r^{2} = 0.971599$, the reverse slope $1.222137$ with
  the product equal to $r^{2}$, $s = 0.49632$ on $n-2 = 3$, $\mathrm{SE}(\beta_1) =
  0.078475$, $t = 10.13$ and a slope interval of $[0.5453,\ 1.0447]$.

- **All 36 new derivation answers were truth-checked separately from the gate**, each
  against an expression written independently of the one in the catalogue — 36 of 36
  agree.

**4. UX & Accessibility Hardener.** Content-side, as cycles 1, 4, 7, 10 and 13
established. Checked rather than assumed: every figure is a fenced `text` block inside
`overflow-x:auto`, which is cycle 4's rule for staying safe at 375px; **no markdown
table, no hard-coded colour and no raw HTML was introduced**, all three verified
mechanically over the draft. The fenced listings are prose figures rather than runnable
programs, so none makes a claim about its own output that a **▶ Run** button would be
needed to check.

### The defect this cycle found beyond its own course

**CTRL510/M4 step 1 accepts any answer that is zero, including `0`.** The step asks for
$\dot{e}$ in terms of $A$, $x$, $\hat{x}$, $L$ and $C$, and its reference answer is
`A x - A \hat{x} - L C x + L C \hat{x}`. Because `\hat` is dropped by the translator,
`\hat{x}` and `x` become the same symbol and the whole expression translates to

```
A * x - A * x - L * C * x + L * C * x     ==  0
```

`verify_derivations.py` passes it, and cannot do otherwise: the gate checks each answer
**against itself**, so both sides lose the same term and $0 = 0$. The step therefore
grades as correct anything a learner types that collapses to zero — the right answer
$(A - LC)(x - \hat{x})$, and equally `0` or `x - x`.

Swept the whole catalogue for the general case — any answer containing a command that
contributes nothing, tested by translating it twice, once as written and once with the
command deleted, and comparing. **Exactly one of the catalogue's 1248 steps is affected**,
and it is this one. Not fixed here: the right repair is in `src/studio.js`, mapping
`\hat{z}` to a distinct symbol the way `\lambda` is already mapped to `lambda_`, and that
is a Track 2 machinery cycle. Recorded with the diff so it starts from the cause rather
than the symptom.

### Found in my own work, and fixed

Every one of these was found by a mechanical sweep run *before* applying, and most are
defects this cycle was in the middle of repairing in somebody else's text.

- **My own render harness condemned correct content on its first run.** It reported
  `\frac{n!}{k! \, (n-k)!}` as a swallowed fraction, because `<mspace …/>` is
  self-closing and the child counter treated it as an opening tag that never closed. A
  measurement that condemns correct content is the failure cycle 3 recorded about its own
  gate and cycle 13 recorded about its unpaired-dollar count, and reporting that hit as a
  finding would have been the same error a third time. Fixed, then self-tested on nine
  cases — four that must flag and five that must not.
- **The same harness then missed the worse half of the defect.** Cycle 13 recorded that
  `\frac13` mid-expression eats the relation
  (`<mfrac><mn>13</mn><mo>=</mo></mfrac>`); that `mfrac` has exactly two children, so a
  child count cannot see it. Added the source-level signature (`\frac` followed by an
  unbraced multi-digit run) alongside the structural one.
- **Ten of my own fragments would have shipped as raw markup.** Three classes: `\big[`
  and `\big(` (five), `\{…\}` set braces (three), and — for the third cycle running —
  **cycle 10's escaped space `\ `**, in `[12.4222,\ 14.4778]` and `[0.5453,\ 1.0447]`.
  Repaired to `\left(`/`\right)`, `\left\{`/`\right\}` and `\,`, each verified against
  the renderer's own tables rather than assumed.
- **Ten of my own inline fragments crossed a source line**, which is cycle 13's third
  defect class, discovered because I was auditing for it. Rewrapped, and the rewrap
  itself missed one because I wrote `\tfrac` in the pattern where the text had `\frac` —
  caught by re-running the checker rather than by trusting the first pass.
- **Five of my six readings came in under the 1200-word target** (1058–1195, all above
  the emitter's 400 floor, so nothing would have failed) — the identical finding cycle 13
  made about its own work. Extended with material rather than padding: the uniqueness of
  the exponential among memoryless distributions; the row conditionals read straight off
  the joint table; when the union bound is exact and when it is worst by a factor of $n$;
  the bias–variance decomposition derived, with the shrinkage estimator that beats the
  unbiased one on MSE; and the residual standard error on $n-2$ with a confidence
  interval for the slope, which connects M11 back to M8's derivation.
- **My first catalogue survey ranked MA201 at 6.82 units per module, and the true figure
  is 2.09.** `lab` holds a dict, and `len()` on a dict counts its keys, so every
  lab-bearing module was scored as eight units instead of one. The ranking survived
  because the error is roughly uniform, but the number was wrong by a factor of three and
  would have gone into this entry. The corrected count agrees exactly with the 2.09 cycle
  13 reported, which is what caught it.
- **My truth harness scored 32 of 36 on its first run against the emitted file, and was
  wrong about all four.** All four are cycle 13's finding restated: a bare `e` in a
  derive answer is a free symbol, not Euler's number. Confirmed rather than changed —
  **13 pre-existing answers across 7 other courses** already use a bare `e^`, so these
  four follow the convention.
- **My payload-window check reported 65 orphaned files.** It read `docs/version.json`,
  which holds only a build hash and names no payload at all; the manifest is
  `docs/programs/_generations.json`. Corrected, the window is 3 generations at 62 each,
  64 files, **0 orphaned and 0 missing**.

### What changed

**Twelve new units in six modules** — one `read` and one `derive` each.

| Module | Reading | Words | Derivation | Steps |
|---|---|---|---|---|
| M2 | The world where B already happened, and the rule that survives the move | 1442 | The complement that survives conditioning, and the one that does not | 6 |
| M4 | Where the probability went, and the rate that replaced it | 1386 | The exponential, out of one assumption about its hazard | 6 |
| M5 | Two variables at once, and the bound a correlation cannot cross | 1326 | Why a correlation cannot leave the interval from minus one to one | 6 |
| M7 | Guarantees you can prove without knowing the distribution | 1351 | Markov, then Chebyshev, then the law of large numbers | 6 |
| M8 | The degree of freedom the mean spends, and the correction it does not buy | 1353 | The degree of freedom the mean spends | 6 |
| M11 | The line that minimises squares, and the two claims it cannot make | 1302 | The normal equations, and the shrinkage hiding in the slope | 6 |

**8,160 new words**, every reading inside the 1200–2500 target and in line with M1's
existing three. MA201: 23 units → 35, 3 readings → 9, 4 derivations → 10, 18 derivation
steps → 54, 10 bare modules → 4, and **2.09 units per module → 3.18**. Every reading
carries a worked example through to a checked number, names the mistake people make and
says why it is tempting, and closes on where the idea stops holding.

**Twenty-five concepts bullets added or repaired** across the six modules, so the new
material is reachable from the list a learner skims and not only from the reading: that
conditioning is a probability model in its own right, the complement that does not
survive it, independence as arithmetic, pairwise against mutual; the vanishing of every
point, the density as a rate, the constant hazard and the rising one; covariance as a
definition rather than a formula, the bound from non-negativity, the difference that is
less variable than the sum, the finite-variance requirement; Chebyshev as Markov twice,
Markov's inversion without non-negativity, a bound against an estimate, the price of a
confidence; the exact $(n-1)\sigma^{2}$, the standard deviation that stays biased,
maximum likelihood's small-sample bias, the bootstrap's failure on the maximum; the
vertical residual and the two slopes, regression to the mean, the residuals summing to
zero, and $R^{2} = r^{2}$. **The M4 z-score bullet was replaced** by two that state the
claim correctly; **every other pre-existing bullet in these modules is untouched.**

**One `why` extended** (M2/Q5), adding the zero-numerator case to a claim that was false
without it. No option text, stem or key was changed anywhere in the course.

### Left alone, deliberately

- **M3, M6, M9 and M10 still hold a lone lab.** Each is a full lab whose reference
  solution the gate runs, so they teach by construction rather than examining cold, which
  is not the defect this cycle was chasing. They should get readings; that is a following
  cycle. Four bare modules remain against ten.
- **The 35 questions were audited and, apart from the one `why`, not changed.** They are
  Track 3's ground. No option text moved, so the answer-tell budget could not move, and
  the gate confirms every catalogue figure unchanged.
- **`\varepsilon`, `\bar` and `\hat` are dropped by `MathCheck.latexToPy` and were not
  fixed there.** Writing `\epsilon` and `m_x` repairs this course; it does not stop the
  next author writing `\varepsilon` in an answer and shipping a step that grades a
  different expression from the one it displays. The fix is the same shape as the
  existing `lambda` → `lambda_` rename and is a Track 2 machinery cycle. Handed on with
  the three reproductions above and the one live casualty (CTRL510/M4).
- **`verify_derivations.py` still proves translation rather than truth**, as cycles 1, 7
  and 13 established — and the CTRL510 finding is the sharpest demonstration yet, since a
  step translating to `0` self-checks perfectly. All 36 new answers were therefore
  truth-checked separately, and the harness is in this session's scratchpad. Nothing about
  the gate was changed: rewriting the spec from inside a cycle it governs remains the
  wrong move.
- **1041 raw fragments, 138 swallowed and 312 unpaired remain catalogue-wide.** MA201 is
  at zero in all three, before and after. These figures come from *this* cycle's harness,
  which is independently written from cycle 13's lost one, so they are not directly
  comparable to its 1053 / 139 / 273 — the durable claim is that only MA201 changed, and
  it changed from zero to zero.
- **MA201's four lab modules and the capstone were not touched**, and neither was M1,
  which is already the model the rest of the course has now been brought toward.
- **`docs/programs` holds 64 payloads against 62 in the current generation.** The rolling
  window, as every cycle since 1 has established. Verified rather than assumed: 3
  generations retained at 62 each, 64 files on disk, all 64 named by a retained
  generation, **0 orphaned and 0 missing**, covering 62 distinct courses.

### Gates, after

Every pre-existing number unmoved. Three moved by exactly what was added — the
derivation-step count by the 36 new steps, and the two artifact sizes by the content.

```
verify_derivations   All good: 1248 steps across 46 courses   (1212 + 36 new;
                     MA201 18 -> 54)
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3160 per-option explanations · 6572 live draws —
                     unmoved, and no stem, option or key changed
verify_labs MA201    All good: 5 labs  (M3 7/7, M6 7/7, M9 7/7, M10 7/7, CAP 11/11)
verify_circuits      All good: 82 circuit exercises, 348 checks
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1457 analyses, 84 refusals · 15 plots · 380 schematics
verify_desk          All good: 61 expressions at the extremes
verify_theme         All good: 14 exemptions · 135 contrast surfaces x 2 themes
emit.py MA201        ok — 11 modules, 4 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12796 -> 12875 KB ·
                     inlined 13993 -> 14072 KB · shell 1168 KB — unchanged
catalogue            62 courses, 368 modules, 1899 -> 1911 units, 246 -> 252 readings
```

Beyond the gates: every MA201 math fragment pushed through the shipped `MathML.render` —
**1892 of 1892 draw, 0 raw, 0 swallowed, 0 unpaired**, against 901 of 901 with the same
three zeros at baseline, so 991 fragments were added and none of them is a defect; all 36
new derivation answers truth-checked against independently written expressions, 36 of 36;
every number in 8,160 new words recomputed in SymPy before it was written; the 35
question stems, option sets and keys diffed against `HEAD` at **0 changes**; **12 lesson
ids added and 0 lost**, so no completed work is orphaned; hedge words counted at 0 in the
new prose; no markdown table, hard-coded colour or raw HTML introduced; the whole
catalogue swept for answers containing a silently-dropped command, finding exactly one,
in CTRL510; and the payload window checked at 0 orphaned, 0 missing.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 9133) was live
throughout, and this cycle is the process it launched — so the lock is this cycle's own
and `emit.py` and `build.mjs` were safe to run. The diff is `catalog/MA201.json`,
`catalog/authors/MA201.py` and the `docs/` build output, and nothing else.

---

## Cycle 15 — TRACK 2: Interactive Models & Visualisers

*(The runner labels this cycle 2 — run 2's counter, started 11:05, while this log keeps
counting. Commit "cycle 2" of run C is this file's cycle 15, exactly as `997eaef` was its
cycle 1 and this file's cycle 14.)*

**Target: the "hit the target" unit end to end — `renderTune` in `src/app.js`, the three
tune models in `src/studio.js`, and the 21 tune units that depend on both.** One
subsystem, and the third of this track's three slider surfaces. Cycle 2 took the first
and hardened `Sandbox.mount`: `initial` clamped, a `log` parameter kind, `aria-live` on
the readout with a change guard, `role="img"` and a name on the canvas, `aria-valuetext`
carrying the formatted value, per-parameter lookups resolved once, a one-shot rAF
coalescer. Cycle 8 took the second, the circuit editor's numerical core, and wrote the
same discipline into the plot. **`renderTune` is a hand-rolled copy of `mount()` that
predates both and received none of it** — twelve of cycle 2's framework fixes are absent
from it one by one — and no gate has ever mounted it. `verify_tune.mjs` asks whether a
target can be reached; `verify_sandbox.mjs` asks whether the model's plot survives its
extremes, using the model's own constants and never the catalogue's overrides. Nobody had
fed this renderer a value the slider cannot hold, resized it, or clicked faster than it
could redraw, which is this track's brief almost word for word.

### Baseline, captured before any edit

```
82 circuit exercises / 348 checks · 21 tune units
216 numeric answers verified, 0 unchecked, 218 figure-only
1248 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3160 per-option explanations · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1457 analyses, 84 refusals, 380 schematics
desk 61 expressions · theme 135 contrast surfaces in both themes
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads, 12875 KB ·
       inlined 14072 KB · shell 1168 KB
```

### The attacks

**3. Simulation Auditor** — taken first, because this is its track and its brief. Every
number below was measured through the shipped renderer before it was changed.

- **An unsanitised saved value freezes the tab and then kills it.** `renderTune` took
  three numbers on trust — an author's `initial`, a model's `def`, and the learner's own
  saved position — and put them straight into `v`, the range input's `value` attribute,
  the readout, the plot and the grading. A range input silently clamps its own value and
  snaps it to its step; `v` did neither. Measured: a saved `r1` of **−100** printed
  "−100 Ω" beside a thumb resting at 100 and put **Infinity in all three graded
  readouts**; a saved **`"2200"`** — a string, which is what an older save or a
  hand-edited store yields — concatenated instead of adding and reported **0.000 V for a
  divider actually sitting at 2.5 V**; a saved **NaN** read "NaN" in every readout, the
  exact rot `verify_sandbox.mjs` rejects in a sandbox and nothing rejected here. And the
  worst case is not a wrong number at all: a saved `r` of **1e308** on `rc-lowpass` makes
  `2 * Math.PI * v.r * c` overflow to Infinity, so `fc` is exactly **0**, `log10(0)` is
  −Infinity, `10 ** -Infinity` is 0, and the plot's `for (let f = 0; f <= hi; f *= 1.06)`
  **never advances** — it pushes a point per iteration until the heap dies. It killed
  Node outright during the mutation run rather than reporting a failure.
- **Sixteen of the twenty-one tune units drew no target at all, and the one that tried
  drew it off the canvas.** `drawPlot` drew a dashed line wherever a constraint's key
  matched `plotKey || 'vout'`, and `vout` is a readout of the `divider` model alone. So
  every `rc-lowpass` and `rlc` unit that did not override the key matched nothing. EE111
  M6, which *does* override it and asks for a **1 kHz resonance**, got a **horizontal**
  line at **y = 1000** on an axis running **0 to 2.375** — a frequency drawn on a gain
  axis, off the frame entirely, invisible rather than wrong-looking. Counted at the
  opening position: **4 targets visible across the whole catalogue**, and a fifth drawn
  where nobody could see it.
- **EE121 M8 states a requirement at a frequency its own plot does not reach.** Found by
  the new gate on its first run, not by hand. `rc-lowpass`'s axis floor was
  `min(10, 10^floor(log10(fc/4)))` and never went below 10 Hz however low `fsig` was set
  — and EE121 M8 is a debounce filter whose whole subject is a **5 Hz** button press.
- **A readout row graded by one of the two constraints on it.** `refresh` used
  `ts.find`, which returns the first match. **Two units state two bounds on one readout**
  — EE121 M5 wants the divider current under 0.50 mA *and* over 0.25 mA, EE211 M5 under
  0.50 and over 0.20. A learner satisfying only the first saw the "I total" row drawn
  **green** while the constraint chip immediately below it was still unticked: one panel
  disagreeing with itself about one number. Reproduced at `r1 = 100, r2 = 20400`.
- **The app and its own gate were grading by different rules.** `renderTune`'s `holdsC`
  tested the bounds before the equality; `verify_tune.mjs`'s `holds` tested the equality
  first. At `{eq: 6, tol: 0.05, max: 8}` and x = 7 the **app passes it and the gate fails
  it**. Swept: **0 catalogue constraints carry both**, so nothing published was ever
  mis-graded — but the gate whose one job is to say whether a target can be hit was
  answering about a rule the learner is not scored against, and that divergence only ever
  surfaces as "this exercise is impossible" from somebody who has just solved it.
- **The model ran twice a frame and the canvas was rebuilt sixty times a second.**
  `refresh()` called `readouts()` and then `tests()` called it again; there was no
  coalescing of any kind. Measured: **60 slider events → 120 `compute()` calls, 60
  `plot()` calls, 60 canvas backing-store reallocations, 0 requestAnimationFrame.** The
  model itself is cheap — **0.13 ms an event** — so this is not an arithmetic problem;
  assigning `canvas.width` clears and reallocates the backing store even at an unchanged
  size, which at the shipped 900×296 and a dpr of 2 is **4.3 MB of zeroing per event of a
  drag**, and `saveSoon()` ran on every one beside it.
- **Checked and found sound, recorded so the next cycle does not re-derive them:**
  `compute()` is finite everywhere on the reachable grid for all three models — swept at
  every corner of every parameter against every unit's real constants, zero non-finite
  readouts, so the Infinity above comes only from the unvalidated path. The
  `ResizeObserver` cannot loop: `#tn-cv` is `width:100%; height:296px` in the stylesheet,
  so its layout box is settled by CSS and `drawPlot`'s writes to the backing store cannot
  reach it — read in `index.head.html` rather than assumed, the way cycle 2 checked
  `.sbx-canvas` and cycle 8 checked `.ckt-canvas`. `divider`'s plot loop is literal
  (`100` to `47000`) and cannot be driven off its ends by a saved value. `.tune` collapses
  to one column at 900px, so the 375px case is the stacked one and the canvas is floored
  at 240.

**4. UX & Accessibility Hardener.** Everything cycle 2 gave a sandbox, absent here.

- **The plot canvas had no role and no name** — `role` null, `aria-label` null. Cycle 8
  called the schematic plot "the only canvas left in the app with no accessible name".
  This was the one after it.
- **Neither slider had an accessible name at all.** Bare `<input type="range">`, no
  wrapping `<label>`, no `aria-label`, no `for`. A screen reader announces "slider" and
  nothing else, twice.
- **No `aria-valuetext`**, so a range input announced its own raw number: "2200" where the
  page reads 2200 Ω, "2.5" where it reads 2.5 µF.
- **The block that says whether the exercise is finished was not a live region.** Neither
  `#tn-read` nor `#tn-state` had one, and `#tn-state` is the only thing on the page that
  says the unit is done.
- **Focus was stranded on a discarded button.** Reset and a passing Check both call
  `paint()`, which replaces the whole page; the button that was pressed no longer exists
  and the keyboard lands back on the body. Verified by identity, not by id.

**1. Senior Educator** and **2. Assessment Inquisitor** have no prose and no graded
question in a slider, so both were pointed at the thing in scope they can judge — whether
what the panel says **explains** or merely **announces**, which is the standard cycle 8
set with the solver's failure messages.

- **The refusal restated the target and stopped.** Pressing Check on EE101 M4 said
  *"2 constraints still unmet: Vout = 3.30 V ± 0.03; I ≤ 1.00 mA"* — the two sentences
  already printed on the panel the learner is staring at, and not the one thing they do
  not know, which is how far off they are. It now reads *"2 constraints still unmet: Vout
  = 3.30 V ± 0.03 — you have 2.500 V; I ≤ 1.00 mA — you have 1.136 mA"*, and the
  constraint chips carry the same pairing permanently, which is also what makes the live
  region worth having: "one of two met" gives a screen-reader user nothing to act on.

### What changed

**`src/app.js` — `renderTune`, held to `Sandbox.mount`'s standard.**

| Fix | Before | After |
|---|---|---|
| every value sanitised | `initial`, `def` and the saved position taken on trust | clamped, type-checked and snapped to the step grid |
| the readout row | graded by the first constraint on its key | graded by every constraint on its key |
| the constraint rule | a private copy that disagreed with the gate | `Tune.holds`, shared with `verify_tune.mjs` |
| the target | `plotKey \|\| 'vout'`, matching one model | the model says where it belongs |
| repaint | none coalesced, model run twice | one rAF-coalesced repaint, model run once |
| the canvas | reallocated every event | written only when the size moves; dpr capped at 2 |
| the canvas | no role, no name | `role="img"` and a name built from what was drawn |
| the sliders | no accessible name, no valuetext | wrapped in a `<label>`, value `aria-hidden`, `aria-valuetext` |
| the goal block | silent | `aria-live="polite"` with a change guard |
| focus | stranded on a discarded button | restored to the same button in the new page |
| a refusal | restated the target | names the value too |
| `plot()` throwing | a stale picture | a drawn message, and a name that says so |

**`src/studio.js` — the models say where a target lives.** A new `marks(c, v, k)` on each
spec returning a mark in that model's own plot coordinates: `divider` puts a `vout`
constraint on the y-axis; `rlc` puts `fn` on the **x**-axis and `peak` on the y-axis, and
`zeta` on neither because it shapes the curve rather than sitting on it; `rc-lowpass`
puts `fc` on the x-axis and treats `keep` and `reject` as **points on the curve** — they
are |H| read at one stated frequency each, so they become two gates the response has to
thread between, converted out of dB where the model that chose the units is. `frame()`
gains `vline`, the mirror of `hline`, which is what EE111 M6's target needed and did not
have. A boundary outside the axis is not drawn and neither is a fill that reaches for
one, which is the honest answer rather than a compromise: EE102 M7's `peak ≤ 30` cannot
be violated on a frame ending at 2.4, and the line arrives on its own once the learner
winds the Q up far enough for the axis to grow to meet it.

**The result, counted at every unit's opening position: 4 targets drawn before, 27 after;
19 of the 21 units now show what they are asking for.** The two that do not are correct
to show nothing — EE111 M10 constrains a ratio and a current on a Vout-against-R2 axis,
and EE231 M3 constrains a time constant. **All three notices that claim a dashed line
still have one**, checked mechanically rather than by reading.

**Two unbounded loops bounded.** `rc-lowpass` and `rlc` both build their point lists with
a geometric loop from a computed start, and a start of zero never advances. Both now
refuse a degenerate axis and cap the iteration count, because "the caller is careful" is
not a property of a loop — and the caller was not careful.

**A new gate — `tools/verify_tune_ui.mjs`, on `tools/tune_stage.mjs`.** Ten sections
driving the shipped `renderTune`: the value clamp over **423 hostile opening values**
(below the floor, negative, above the ceiling, 1e308, off the step grid, a string, NaN,
null, an object — every parameter of every unit); a readout row graded by every
constraint on its key; **462 targets** required to lie inside their own axes over the
extremes grid **and the catalogue's overridden constants, which `verify_sandbox.mjs`
never passes**; a mark that is never drawable anywhere, which is how a coordinate in the
wrong units fails silently; **105 paints at five widths** on the recording canvas from
`dom_stub.mjs`; sixty drags inside one frame required to be one repaint and one model
evaluation and zero reallocations; the canvas named out of what it drew; one live region
that does not flood; focus after both repainting buttons; a refusal that names the value;
and the app's rule and `verify_tune.mjs`'s required to agree — asked of the **renderer**,
through a synthetic unit whose constraint carries both an equality and a bound.

**`tools/app_stage.mjs`.** Two gates now mount real views out of `app.js`, and the 360 KB
they each stand up was about to exist twice. Extracted, for the reason cycle 8 extracted
`dom_stub.mjs`: two copies drift, and then two different applications are under test and
neither is the one that ships. **`verify_quiz.mjs` reports byte-identically before and
after, checked by diff.**

### Verification beyond the gates

**The gate was not trusted until it had been seen to fail. Eighteen mutations, eighteen
intended verdicts** — and on the first run **it got five of them wrong**, which is the
whole argument for doing it:

- *The unclamped saved value* killed Node instead of failing. That was the gate telling
  the truth about something worse than the defect I was chasing, and it is where the
  infinite plot loop above came from.
- *The first-constraint grading* passed. My search for a discriminating position asked
  for "some but not all" constraints holding, and the first such position has the **first**
  one failing — so a renderer grading by the first marks the row failing too and the check
  never discriminates. It now requires the first to hold and a later one to fail.
- *The raw-number `aria-valuetext`* passed, because I read the attribute off the opening
  markup and the mutation was in the drag handler. It is now read after a drag as well.
- *The removed canvas-size guard* passed, because I compared `cv.width` before and after
  and reassigning the same number does not change the value. It now counts **assignments**
  through a property setter, which is what a browser reacts to.
- *The restored private `holdsC`* passed, because section 9 tested `Tune.holds` — proving
  studio.js consistent with itself and saying nothing about what the renderer uses. It now
  drives the real view.

After those five repairs: **18 of 18**, including the unmodified tree as a control.

Every defect was measured before it was fixed and re-measured after: the Infinity, the
0.000 V, the "NaN", the 120-computes-per-60-events, the 60 reallocations, the 4-versus-27
targets, the y = 1000 on an axis ending at 2.375, and the 5 Hz target on an axis starting
at 10 Hz. `verify_tune.mjs` reports **byte-identically** before and after its rule was
replaced by the shared one, so unifying the rule moved no verdict and no example
solution. The catalogue was swept for a constraint carrying both an equality and a bound
before that unification was written — **0 of them** — rather than assumed. Every notice
claiming a drawn line was checked against what is now drawn. The payload window was
checked rather than assumed: **3 generations, 64 files, 0 orphaned, 0 missing**.

### Left alone, deliberately

- **`plotKey` is now vestigial on two units and was not removed.** Every authored
  `plotKey` in the catalogue is legitimate — seven `vout` on `divider` units where it was
  redundant, and EE111 M6's `fn`, which the model now places correctly — so **no catalogue
  edit was needed and none was made**. The two that name a key their model cannot place
  (EE111 M7's `fc`, EE111 M10's `vout`) drew nothing before and draw nothing now.
  Removing the field means re-emitting EE111 for no behaviour change, so the gate
  **reports** them in a note instead. Recorded so the next author is not the one to find it.
- **`sliding-mode` still keeps forward Euler** and **`P.dim` (2.93:1) and `P.faint`
  (1.86:1) still fail contrast on every canvas.** Cycle 2 measured them and handed them to
  Track 5; cycles 5, 6 and 8 each re-recorded them without taking them. This cycle adds
  the tune plot's own axis labels to the list and takes them no further, for the reason
  that has held every time: changing them changes the visual weight of 13 visualisers and
  two more canvases, which is a decision about the design language.
- **The `rlc` marker at `(fₙ, 1/2ζ)` is not the peak, and the readout beside it calls
  1/(2ζ√(1−ζ²)) the "peak gain".** Both are correct — the dot marks where you are at ωₙ,
  the readout reports the true maximum — and they are different numbers by design. With
  `peak` now drawn as a horizontal target the picture finally shows the constraint the
  learner is steering, so the dot's meaning matters less than it did. Recorded rather than
  changed, because moving the dot would be changing what the plot is about.
- **`Sandbox.mount`'s own coalescer has the same `raf = requestAnimationFrame(cb)` shape**
  that made an immediate rAF stub wedge it shut. It is correct in a browser, where the
  assignment lands before the callback runs; only a synchronous test stub inverts it. Not
  changed — recorded, because it is the reason `tune_stage.mjs`'s frame queue is deferred
  and `blanks_stage.mjs`'s is not.
- **Nothing here animates on a timer**, so `prefers-reduced-motion` has nothing to honour;
  the single `requestAnimationFrame` is a one-shot coalescer. Cycle 2's finding, still true.
- **No `emit.py` run, and no author file, `catalog/*.json`, lesson id or schema touched.**
  Presentation, behaviour and gates only, so the staleness guard is not armed — and the
  payload total is unchanged at **12875 KB**, which is the mechanical confirmation that no
  content moved. `git status` reports **0 changes under `catalog/` and 0 under
  `docs/programs`**.

### Gates, after

Every pre-existing number unmoved. The only new numbers are the new gate's; the only two
that moved are the artifact sizes, by exactly the source that was added.

```
verify_tune_ui       All good: 21 tune units mount and answer — 423 hostile opening
                     values clamped onto the grid, 462 targets inside their own axes,
                     105 paints at 5 widths, 270 drags, 493 mounts, one repaint a
                     frame, and a refusal that names the value                    [NEW]
verify_tune          All good: 21 tune units reachable and not pre-solved
                     — byte-identical to before the rule was unified
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuits      All good: 82 circuit exercises, 348 checks
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1457 analyses, 84 refusals · 15 plots · 380 schematics
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3160 explanations · 6572 live draws
                     — byte-identical to before app_stage.mjs was extracted
verify_derivations   All good: 1248 steps across 46 courses
verify_desk          All good: 61 expressions at the extremes
verify_theme         All good: 135 contrast surfaces x 2 themes
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12875 KB — unchanged ·
                     inlined 14072 -> 14091 KB · shell 1168 -> 1187 KB, of 1536
```

Beyond the gates: **18 mutations the new gate had to reject and one it had to pass**, five
of which it failed on its first run and was repaired for; `verify_quiz.mjs` and
`verify_tune.mjs` both reporting byte-identically across the refactors under them, checked
by diff rather than by reading; the catalogue swept for a constraint carrying both an
equality and a bound before the rule was unified; every notice claiming a drawn line
checked against what is now drawn; and the payload window checked at 0 orphaned, 0 missing.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 9133) was live
throughout and this cycle is the process it launched, so `build.mjs` was safe to run. The
diff is `src/app.js`, `src/studio.js`, `src/index.head.html`, four files under `tools/`
and the `docs/` build output, and nothing else.

---
## Cycle 16 — TRACK 3: Question Bank & Quizzes

*(The runner labels this cycle 3 — run C's counter. This log keeps counting, exactly as
cycle 15 recorded: run C's cycle 1 was this file's cycle 14, its cycle 2 was cycle 15,
and its cycle 3 is this.)*

**Target: CS301 (Design & Analysis of Algorithms) — its 25 quiz questions — and
`renderQuiz`, the surface that delivers all 1366 of them.** One course and one subsystem,
which is cycle 3's shape and cycle 9's: cycle 3 gave `quiz` its per-option explanations
and rebuilt CS201 on top of them, cycle 9 did the same for `blanks` and rebuilt EE211.
This one pays the debt both of those cycles named by name, and closes the hole they left
between them.

Chosen on measurement rather than taste. Three numbers picked it out.

*The largest single block of the answer tell.* CS301 scores **22 of 25** on "read
nothing, pick the longest option" — 88%, against 25% for guessing — with a mean length
margin of **+47.7 characters**, the widest of any course in the catalogue. RFIC510 is
nominally worse at 90%, but that is 9 questions of 10; CS301 is 25 questions and 100
options, and it is the course cycle 3 named first in its recorded debt and cycle 9
re-recorded as unpaid.

*Nothing explained the wrong answer.* **0 per-option explanations across 25 questions and
100 options** — the largest quiz bank in the catalogue with none. The rest of the course
does not have this problem: all 20 of its blanks holes carry `whys` and both numeric
units carry `wrong` and `hint`. The quiz was the one graded surface in CS301 that
answered the same paragraph whichever option was pressed.

*The key was authored at index 0 in all 25.* Catalogue-wide the authored key sits at
index 0 for **548 of 1366 questions (40.1%)**, spread 548 / 431 / 280 / 107, and **22
courses author every key there**, covering 289 questions. `shuffledOptions()` is the only
thing standing between that and a bank answerable by pressing the top button — which is
precisely the state cycle 9 found the blanks bank in, where no shuffle existed and
pressing the first option scored 735 of 1103. One mechanism, and no gate had ever
watched it run.

### Baseline, captured before any edit

```
82 circuit exercises / 348 checks · 21 tune units
216 numeric answers verified, 0 unchecked, 218 figure-only
1248 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3160 per-option explanations (160 quiz, 3000 blanks) · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1457 analyses, 84 refusals
desk 61 expressions · theme 135 contrast surfaces · tune_ui 423 hostile values
CS301: 25 questions in 5 quiz units · 20 blanks holes · 2 numeric · 6 labs
       longest-is-key 22/25 (88%) · mean margin +47.7 · whys 0/100 · 4482 words
quiz view: renderQuiz mounted by NO GATE — 1366 questions in 252 units
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads, 12875 KB ·
       inlined 14091 KB · shell 1187 KB
```

### The attacks

**2. Assessment Inquisitor** — taken first, because this is its track. The three numbers
above are its findings. Two more, both of the kind cycle 3 catalogued in CS201 and which
had survived here untouched:

- **Options eliminated by grammar rather than by understanding.** `M4/Q1` asks *"Why does
  Dijkstra insist on non-negative weights?"* and offered *"It does not — Dijkstra is fine
  with negative edges as long as there is no negative cycle"*, which denies the premise of
  its own stem. `M2/Q2` says Huffman **merges** the two least frequent subtrees and then
  offered *"They never end up in the same subtree"*. `M3/Q2` offered *"a reconstructed
  script can come out cheaper than the value in the table"*, which states its own
  impossibility — the table's value is by definition the cheapest achievable. Each of
  these silently turned a four-way question into a three-way one.
- **Wrong numbers standing in for misconceptions.** `M5/Q3` offered *"The optimum is 4 and
  the approximation found 8"* about a graph with four vertices in it. `M2/Q3` offered
  *"0.75"* as a Kraft sum, which no arithmetic slip actually produces — the sums a learner
  really lands on are 0.875 (the three distinct lengths summed, the repeated depth-3
  codeword counted once) and 1.25 (both depth-3 codewords charged at `2^-2`, an off-by-one
  in the depth). Both of those are now the options, each with the slip behind it named.

**1. Senior Educator.** CS301's explanations already derive rather than assert and every
`why` already walked all four options, which is the standard cycle 3's brief asks for and
this course met. What this persona found is the asymmetry cycle 3 described and did not
reach: a learner who picked the third option has to read a paragraph written for whoever
picked the first, and find the clause that is about them. And the prose named *that* an
option was wrong far more often than it named *why anyone believes it* — which is the
half of the brief that produces teaching rather than marking.

**3. Simulation Auditor.** No sandbox, tune or schematic in this course, so it was pointed
where it can still bite: every number and code claim in the bank, against the labs that
ship beside them. It found a false claim CS301 has been shipping, and it is recorded in
full below because the shape of the error is the interesting part.

**4. UX & Accessibility Hardener.** Cycle 3 hardened this surface — focus moved onto the
explanation when the clicked button is disabled, `role="status"` on the score region,
`role="group"` and `aria-labelledby` on the options, a `code` style in `.explain`. Every
one of those repairs was still in the source and **not one of them was under a gate**.
That is this cycle's machinery half. Two more defects were mine and are in the
self-audit below.

### The false claim the recompute found, and why the example could not fail

`M4/Q1`'s explanation has been saying:

> take `a->b` at 2, `a->c` at 3 and `c->b` at -2. There is no cycle at all, and Dijkstra
> still settles `b` at 2 while the true distance is 1.

Run that graph through the course's own reference `dijkstra` and it returns `b = 1`. The
claim is false, and it is false twice over.

First, the lab's `dijkstra` **raises `ValueError` on any negative weight** before it does
anything else, so it never runs on that graph at all. Second — and this is the part worth
keeping — even with that guard removed the implementation gets the right answer here,
because `b` has no outgoing edge. `dist[b]` is written down as 2, `c` is expanded later
and lowers it to 1, and since nothing was ever relaxed *out of* `b` the stale 2 never
propagated anywhere. A settled-set Dijkstra corrupts distances **downstream of** the
vertex it settled too early, not the vertex itself.

So the counterexample needs the corrected vertex to have somewhere to send its mistake:
`s->a` at 2, `s->b` at 3, `b->a` at -2, `a->t` at 1. Still acyclic, still four edges. `a`
is extracted at 2 and relaxes `a->t` to 3; only afterwards does `b` reveal that `a` is
really 1 away; `a` is settled by then and its outgoing edge is never looked at again, so
`t` comes out at **3 against a true distance of 2**. Verified by running the lab's own
reference with the negativity guard removed, against Bellman-Ford on the same graph, and
by checking the graph is acyclic rather than asserting it.

Everything else in the bank was re-derived rather than skimmed, and all of it holds:
`log_2 3 = 1.585` against `log_3 2 = 0.63`, and the level costs `n`, `1.5n`, `2.25n`
growing by `3/2`; the `2d`-by-`d` box holding eight points with the two shared corners
counted twice and **six** distinct; `[2, 5, 1, 3]` having 3 inversions with `len(left) - i`
contributing 2 at the first emission, and `[3, 4, 1, 2]` reporting 2 against a true 4
under the one-per-emission rule; the two interval counterexamples, one of which the lab
asserts on by name; the three Kraft sums; coins 1, 3, 4 optimal at every amount below 6,
3 coins against 2 at 6, and **3 against 3 at 9**, which is what refutes the "multiple of
3" reading; the knapsack instance at 9 against 14, with 23 the infeasible bundle and 14.6
the fractional relaxation; `lcs(AGGTAB, GXTXAYB) = 4` with `6 + 7 - 8 = 5`, and `AB`/`BA`
where `max(len) - ed = 0` against an LCS of 1; the triangle's matching of 1 against an
optimum of 2; the path of four at 2.0 and at 1.0 under a reordering; and `H_n - 1` at 6.5
for a thousand vertices and 13.4 for a million.

### The gate that had never opened the door

`verify_quiz.mjs` has read the artifact since cycle 3 and driven the real `renderBlanks`
since cycle 9. Between those two, **`renderQuiz` — 1366 questions in 252 units, every
graded question in the catalogue that is not a blank — was mounted by nothing.** Three
things it does are invisible in the JSON and invisible to any rule written about the
source: the shuffle, the `whys` remap `q.whys[shuffled[qi].order[oi]]`, and the letter a
wrong answer is pointed at, which is the key's **drawn** slot and differs from its
authored index on three questions in four.

It also could not have been mounted. `dom_stub.mjs` had no `firstElementChild`, and
`app.js`'s `el(html)` is `createElement('div'); d.innerHTML = html; return
d.firstElementChild` — so every view built out of `el()` handed `appendChild` an
`undefined`, and `renderQuiz` is built entirely out of `el()`. Three additive stub
methods close it: `firstElementChild`, `contains` (the focus guard asks
`card.contains(document.activeElement)`) and `scrollIntoView` (`finish()` scrolls the
result into view, so without it the last question of every quiz in the catalogue throws
instead of being scored). **The five other gates standing on that stub were proved
byte-identical before and after rather than assumed** — `verify_circuit_ui`,
`verify_circuit_model`, `verify_tune_ui`, `verify_sandbox`, `verify_desk`.

**`tools/quiz_stage.mjs`**, on the `app_stage.mjs` cycle 15 extracted. Over the whole
catalogue: **1260 mounts and 5464 options pressed, each one's explanation read back.** Per
question it requires that the drawn options are a permutation of the authored ones and
carry one authored index each, with each index attached to the option it names; that the
key lands in the top slot at a rate a shuffle produces — **24.0%, against 38.8% in the
order they were authored** — and that no unit draws all of its keys on top; that the
per-option explanation shown is the one authored for **the option actually pressed**,
which is what proves the remap; that a wrong answer is pointed at the key's drawn letter;
that the explanation can take focus, since the button just pressed was disabled and a
disabled element cannot hold it; that the options are a group labelled by the question;
that the result region exists, is empty and is `role="status"`, which is the one order a
live region announces in; that a second press on an answered question changes nothing;
that the score matches the options pressed; and that a learner's best score survives a
worse retry.

**`data-ai` on the option button, and the six questions that made it necessary.** The
authored index behind a drawn slot had to be recovered from the option's text, and it
cannot be: MathML lives in structure rather than in characters, so `$I_m/\sqrt{2}$` and
`$I_m/2$` both flatten to `Im/2`. **Six questions in six courses hold such a pair** —
EE111/M3, EE141/M8, EE201/M3, EMAG530/M3, MA112/M8 and PWR510/M4. All six draw and are
announced correctly in a browser, because `<msqrt>` and `<mfrac>` are real elements and
`MathML.render` emits them; this is the gate's flattening, not those questions' defect,
and it is recorded so the next author is not the one to rediscover it. The fix is the one
`renderBlanks` has used since cycle 9: `renderQuiz` now carries the authored index in
`data-ai` beside the drawn `data-oi`, and the gate reads it instead of guessing. Writing
the shuffle out a second time inside the gate would have been a gate enforcing a comment.

### What changed

**Content — all 25 questions rewritten, 100 per-option explanations written.**

| | before | after |
|---|---|---|
| questions | 25 | 25 |
| "pick the longest option" | 22 / 25 — **88%** | 0 / 25 — **0%** |
| mean length margin | +47.7 chars | −5.1 chars |
| per-option explanations | 0 | **100** |
| words of question text and feedback | 4482 | **13355** |
| authored key index | 25 at 0 | 7 / 6 / 6 / 6 |

The length tell was removed by moving the justification out of the key and into the
feedback, not by trimming the key until it was shortest — the rule refuses that inversion
just as hard, and the pre-flight check caught two questions where a first draft had done
exactly that. Every
distractor is now a misconception with a name. The ones worth recording, because they took
the most work to find: *"the whole level of the recursion tree, since every level of merge
sort costs `Theta(n)`"* — a true statement about the solved recurrence offered as the
meaning of its additive term, which is using the answer as its own input; *"`Theta(n log
n)`, since every level of the tree costs the same"* for Karatsuba, the equality case
attached to a recurrence that is not in it; *"the points are y-sorted, so distances grow
along the scan"* — the y-*difference* is monotone and the distance is not, which is
exactly what the loop's `strip[j][1] - strip[i][1] >= d` exit tests; *"their codewords are
the longest in the code, but a later merge can still separate the two"*, half of the
correct argument attached to a thing the algorithm structurally cannot do; *"exactly 1 —
but every prefix-free code sums to 1, so the value tells you nothing extra"*, the Kraft
inequality mistaken for an equality, which is where its whole diagnostic power lives;
*"9 against 14.6 — the optimum is what the densities are pointing at"*, the fractional
relaxation's value offered as the integral optimum in the module whose entire subject is
the gap between them; *"only a negative cycle actually breaks it; a single negative edge is
caught by the guard after the pop"*, which is what a reader of `M4/Q2` two questions later
would conclude; *"the `V`-th round is reserved for the negative-cycle test, so one round
has to be surrendered"*, the consequence of the bound offered as its cause; and *"the
vertex count is even, so the edges the algorithm picks match up all of them exactly"* — a
true observation about the instance, and not the mechanism, refuted by extending the path
to five vertices where the matching covers four of them and the ratio is still exactly 2.

**CS301's own keys are spread across the four indices.** The renderer shuffles, so this is
invisible to a learner and it is not a defect that was fixed. It is defence in depth: 21
courses still depend on the shuffle alone, and this one no longer does. The rotation moved
`opts` and `whys` together and the gate presses every option of every question to confirm
the pairing survived.

**Machinery — `src/app.js`.** `data-ai` on each option button, as above. Nothing else in
the renderer changed; the focus move, the live region and the group label are cycle 3's
and are now held in place by a gate.

**Machinery — `tools/dom_stub.mjs`.** `firstElementChild`, `contains`, `scrollIntoView`,
all additive, all with the reason written beside them.

**Machinery — `tools/verify_quiz.mjs`.** The quiz-view section above, plus `authoredTop`,
which reports how often the key sits at index 0 in the file so the shuffle's rate has
something to be compared against rather than a constant to be trusted.

### Verification beyond the gates

**The gate was not trusted until it had been seen to fail. Twenty mutations, twenty
intended verdicts, one of them a required pass:** the shuffle removed from `renderQuiz`;
`data-ai` carrying the drawn index; the `whys` lookup indexed by the drawn slot; a wrong
answer pointed at the authored index; the explanation losing `tabindex="-1"`; the option
group losing its role; the result region losing `role="status"`; the result region drawn
with content already in it; the already-answered guard removed; the score counted against
the authored key; the best score no longer a high-water mark; `quizProse` losing its fence
support and five EE131 stems with it; a duplicated option; a `whys` list one entry short;
"the third option" planted in an explanation; **"the final answer" planted in one, which
must pass** — cycle 9's narrowing, re-checked; a bullet the renderer cannot draw; an
improvement left unrecorded in the budget; a course with no budget entry; and the
unmodified tree as a control. The shuffle mutation was checked twice, because the blanks
half shares `shuffledOptions` and reports first: the quiz half names it independently, per
unit, on every course.

**Every number in the new prose was recomputed rather than re-read** — sixty-odd checks,
run against implementations of the lab's own algorithms, including the Dijkstra
counterexample against the reference with its guard removed. Two were wrong and are in the
self-audit below. **CS301's quiz was swept for the three failure modes this repository has
already shipped**: 0 strings with an unpaired `$`, 0 with a backslash before a quote
(cycle 3's raw-string leak), and 0 reaching the screen with a delimiter still in them
(cycle 7's raw markup) — measured before and after, both at zero. And the payload window
was checked rather than assumed: **3 generations naming 64 files, 64 on disk, 0 orphaned,
0 missing.**

### Found in my own work, and fixed

- **Two figures written from memory instead of computed.** The `log n` construction's
  ratio is `H_n - 1`, which is 6.5 at a thousand vertices and 13.4 at a million; I had
  written 5.5 and 12.4. Found by the recompute, not by re-reading the sentence, which is
  the only way this class of error is ever found.
- **A claim the lab's API cannot express.** I wrote that adding a fifth *isolated* vertex
  to the tight path instance flips the parity with nothing else changing — but `ratio`
  takes an edge list, and an isolated vertex has no edge to name it, so the instance does
  not exist. Replaced with the path of five, `[(0,1),(1,2),(2,3),(3,4)]`, which is odd,
  whose matching covers four of the five, and which still scores exactly 2.0. Computed
  before it was written down this time.
- **Two references pointing the wrong way down the page.** A per-option explanation said
  "the counterexample above" and the shared account said "the counterexamples below" —
  but `renderQuiz` draws `.ex-picked` **before** `quizProse(q.why)`, so the first points
  at something below it and the second at something above, and a learner sees exactly one
  per-option explanation rather than the set. Found by sweeping all 125 new strings for
  spatial words and reading the twenty-eight hits, of which twenty-six were ordinary prose
  ("below 1", "the row above it", "a new parent above two roots").
- **My own gate failed a correct single-course run.** The slot-distribution check fired on
  CS301 alone at 36% of 25 questions — well inside the spread of a fair shuffle at that
  sample size. It now needs 200 questions before it measures a distribution, with the
  reason written next to it. This is the fourth cycle running to meet a gate condemning
  working content, and the rule holds: a gate that fails correct work is worse than the
  defect it was written to catch.

### Left alone, deliberately

- **24 courses are still over 50% on the quiz length tell**, down from 25 — CS301 is the
  one that left the list. The catalogue moves from
  **646/1366 (47%) to 624/1366 (46%)** — CS301's 22 and nothing else. RFIC510 90%,
  CS310 84%, VLSI530 / EMAG530 / DSP530 / DSP520 80%, CS330 77%, CS210 / CS102 71%. This
  is cycle 3's main recorded debt, one course smaller, and every course is still pinned in
  `quiz_budget.json` so it cannot grow while it waits.
- **21 courses still author every key at index 0**, covering 264 questions, and the
  catalogue's authored spread is still 530 / 437 / 286 / 113. Not a defect while the
  shuffle runs — and the shuffle is now under a gate that presses every option of every
  question in the catalogue, which is the guard that was actually missing. Rotating 264
  questions across 21 courses is a mechanical sweep, not a cycle that also claims to have
  verified anything.
- **347 blanks holes in ten courses still have no per-option feedback** — EE102 102,
  EE121 93, EE101 87, MA111 20, MA121 17, EE241 11, EE221 / MA112 / MA201 5 each, EE202 2.
  Cycle 9's debt, unmoved, and deliberately not taken here: this cycle went to the bank
  whose *renderer* had no gate rather than to the one whose content debt is larger.
- **The six MathML-ambiguous option pairs** in EE111, EE141, EE201, EMAG530, MA112 and
  PWR510. They are correct in a browser and correct to a screen reader that parses
  MathML, so rewriting six questions in six courses this cycle is not looking at would be
  churn. Recorded with the courses named, because the next author to flatten an option to
  text will meet them.
- **`.quiz-q .qt code` still takes its colour from `--lime` rather than `--code-ink`, and
  `P.dim` (2.93:1) and `P.faint` (1.86:1) still fail contrast on every canvas.** Cycles 2,
  3, 5, 6, 8, 9 and 15 have each recorded these. Track 5.
- **The emitter adds `"check": ""` to CS301's two numeric units, and it was kept.** This
  is not the `emit.py --all` drift cycles 4 and 9 reverted: **194 units across the
  catalogue already carry an empty `check` on disk** and CS301's JSON simply predates the
  emitter behaviour, so re-emitting the course brings its artifact into line rather than
  away from it. Verified that everything outside `quiz` is otherwise byte-identical and
  that **every lesson id is unchanged**, which is what progress is keyed on.
- **The retained window holds two intermediate CS301 payloads.** Capturing the gate
  baseline means running `build.mjs` before editing, and re-running it after each round of
  content repair; the window keeps three generations, so the two most recent of those
  intermediate builds are still on disk beside the final one. Both are named by a
  generation and both are present — **3 generations naming 64 files, 64 on disk, 0
  orphaned, 0 missing** — so the invariant holds and HEAD's own payload has aged out
  normally. Recorded because it is the visible cost of capturing a baseline properly, and
  because it means CS301's next two edits will age these out rather than growing the set.

### Gates, after

Every pre-existing number unmoved. The numbers that moved are the new gate's, the
per-option explanation count — by exactly the 100 written — CS301's budget entry, and the
artifact sizes.

```
verify_quiz          All good: 1366 questions in 252 quiz units and 1103 holes in 217
                     blanks units · 3260 per-option explanations (3160 -> 3260, +100)
                     · quiz view: 1260 mounts, 5464 options pressed and the explanation
                     read back, the answer drawn in the top slot 24.0% against 38.8%
                     as authored · blanks: 6572 draws, 4384 options, 24.5% — unmoved
                     · every bank within its answer-tell budget   [QUIZ VIEW NEW]
verify_circuits      All good: 82 circuit exercises, 348 checks · 543 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_derivations   All good: 1248 steps across 46 courses
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_desk          All good: 61 expressions at the extremes
verify_theme         All good: 135 contrast surfaces x 2 themes
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1457 analyses, 84 refusals · 15 plots · 15 floors, 17 ceilings
verify_tune_ui       All good: 21 tune units, 423 hostile opening values, 462 targets,
                     105 paints, 270 drags, 493 mounts
verify_labs CS301    All good: 6 labs
emit.py CS301        ok — 5 modules, 5 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12875 -> 12923 KB ·
                     inlined 14091 -> 14140 KB · shell 1187 -> 1188 KB, of 1536
```

Beyond the gates: **20 mutations, each producing the verdict it had to, including one the
gate was required to pass**; the five other stub-driven gates proved byte-identical after
`dom_stub.mjs` was extended, by diff rather than by reading; every number in the new prose
recomputed against implementations of the labs' own algorithms, which is how the shipped
Dijkstra counterexample was found not to be one; CS301's quiz swept for unpaired `$`,
escaped quotes and raw delimiters at 0, 0 and 0; all 125 new strings swept for references
that point the wrong way down the page; and the payload window checked at 3 generations,
64 files, 0 orphaned, 0 missing.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 9133) was live
throughout, so `build.mjs` was safe to run. The diff is `catalog/authors/CS301.py`,
`catalog/CS301.json`, `src/app.js`, three files under `tools/` — one of them new — and the
`docs/` build output, and nothing else. No lesson id, no other course, and no unit kind
other than `quiz` was touched.

---

## Cycle 17 — TRACK 4: Subject Breadth & Progression

*(the runner labels this commit "cycle 4"; its counter restarts per run and this log's
does not. This is the log's seventeenth entry.)*

**Target: EE202 (Transistor Amplifiers).** One course, and the debt cycle 10 handed this
track by name: *"`NPN`, `PNP`, `NMOS`, `PMOS` and `OPAMP` are still drawn by nothing, and
EE202 — Transistor Amplifiers, 11 modules, 13 schematics, no transistor — is the obvious
next instalment of exactly this cycle. It is also a second course, and the brief says
one."* Nothing had picked it up.

Re-measured before starting rather than taking the handed-over number. Across **380
published schematics** the catalogue drew **9 part kinds**, the two new ones being cycle
10's own:

```
GND 826 · R 717 · V 396 · OUT 332 · C 171 · L 91 · I 53 · D 4 · LED 4
never drawn: NPN · PNP · NMOS · PMOS · OPAMP · SW · LDR · NTC · POT · LAMP · METER · BAR
```

EE202 is where that costs most and it is not close. Its **13 schematics contain no
transistor**; every one of them replaces the device with an ideal current source. It is
also the thinnest of the four courses cycle 0 flagged as *"full syllabi, still need
density"* that anyone has yet reached: **3.18 units per module, and no `read` unit at
all** across eleven modules.

### Baseline, captured before any edit

```
82 circuit exercises / 348 checks · 543 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1248 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3260 per-option explanations · 6572 draws · answer in the top slot 24.5%
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_model: 1457 analyses · 84 refusals · 15 plots · 15 floors, 17 ceilings
               380 published schematics, 359 with a DC operating point
EE202: 11 modules · 35 units · 0 read · 6 build · 6 derive · 5 labs
       13 schematics, 0 containing a transistor
build: 3 parts / 111 keys · 32/32 + 30/30 · 13 visualisers · 3 tune models · 15 symbols ·
       62 payloads, 12923 KB · inlined 14140 KB · shell 1188 KB
catalogue: 62 courses, 368 modules, 1911 units · 1911 lesson ids
```

### The attacks

**1. Senior Educator** — taken first, and this track's half of the brief turned out to be
the whole finding: **the prerequisite chain does not deliver what the course says it
delivers.**

- **EE201 is EE202's only declared prerequisite, and it contains the word "MOSFET" zero
  times.** Also "channel" zero times, "inversion" zero times. EE202's own file docstring
  says *"the physics that produces that behaviour belongs to EE201"*. It does not live
  there. Counted across the whole chain below EE202:

```
             mosfet   transistor   "square law"   channel
  EE101 *       0         20             0           1
  EE102 *       0          9             0           1
  EE111         0          6             0           1
  EE131         0          1             0           5
  EE141         1          5             2           0
  EE201 *       0          1             0           0   <- the declared prerequisite
  EE202        19         42            25          10
       * on the prerequisite chain: EE101 -> EE102 -> EE201 -> EE202, and that is
         the whole of it. EE111, EE131 and EE141 are shown for context and are not
         courses a learner has to have passed to arrive here.
```

  EE202 uses "square law" **25 times**. Not one course on the chain a learner reaches it
  through uses the phrase even once. So M1 opens by announcing
  $I_D = \tfrac{1}{2}kV_{ov}^2$ and $k = k'(W/L)$ with nowhere behind it to have got
  either.
- **The course already marks an error it never explains.** M1's quiz says *"Answering
  2.0 mA is forgetting the factor of one half"* — correct, and the one half had no
  origin anywhere in the catalogue. It is the average of a channel charge that ramps from
  full at the source to zero at the drain, and that sentence could not be written without
  the integral nobody had done.

**2. The false claim, swept rather than repaired where it was found.**

- **Three places in EE202 tell the learner the tool cannot do the thing the tool does.**
  The module docstring: *"The schematic solver has no transistors — it is linear only"*.
  M2's build brief: *"The schematic solver is linear and has no transistors in it"*.
  M5's build brief: *"As before, the schematic solver has no transistors"*. All false.
  `src/circuit.js` carries a SPICE level-1 MOSFET (cut-off, triode, saturation, a
  source/drain swap for pass-gate use, and $(1+\lambda V_{DS})$), an Ebers-Moll bipolar
  in transport form with two betas, and a finite-gain op-amp with `tanh` rails — all run
  by the same Newton-Raphson loop the diode uses, and all shipped since cycle 0.
- **Swept the catalogue, not the module, and found two more.** EE121: *"This is also why
  the schematic editor in this course has no transistors. Its solver is linear — the same
  modified nodal analysis a SPICE engine uses, **without the Newton iteration that
  non-linear devices need**."* The file has `iterate()`, `pnjlim`, `fetlim`, `vcritOf`
  and an `EXP_CAP`; the whole point of them is the Newton iteration. EE241: *"The
  schematic editor has no transistor symbol"* — `define('NPN', …)`, `define('PNP', …)`,
  `define('NMOS', …)` and `define('PMOS', …)` are all in `src/circuit.js`, and `NPN` is
  in `emit.py`'s `MATCH_SYMBOLS`. Both repaired; see below for why two other courses were
  touched at all.

**3. Simulation Auditor** — every number below was computed by loading `src/circuit.js`
as shipped and solving, before anything was written.

- **The bias exercise cannot fail on bias.** M2's four-resistor build grades a network
  whose device is an ideal `I` source, so **the drain current is stipulated**. Any gate
  divider whatever — 1 V, 8 V, upside down — still passes 1.000 mA, because that is what
  an ideal current source does. The one quantity a bias network exists to control is the
  one quantity that drawing cannot get wrong.
- **What the stand-in hides, measured.** Two networks, both worked out by hand for
  exactly 1.000 mA, then solved with the real device and then with the device changed
  underneath them:

```
                            hand    device     k +50%    V_th -0.2 V
  four-resistor, R_S = 2k  1.000   1.0202 mA   +7.1 %      +7.7 %
  gate bias, no R_S        1.000   1.1400 mA  +42.9 %     +37.9 %
```

  Degeneration did not remove the errors, it divided them — including the $\lambda$ the
  hand calculation drops, which arrives as 2.02% with $R_S$ and 14.0% without.
- **And the divisor has a closed form the check can measure.** Differentiating the fixed
  point gives $\frac{k}{I_D}\frac{\partial I_D}{\partial k} = \frac{1}{1+g_mR_S}$.
  Confirmed against the solver by perturbing $k$ by $\pm1\%$:

```
                        measured    1/(1+g_m R_S)
  four-resistor R_S=2k   0.1853        0.1904
  R_S = 1k               0.3041        0.3158
  gate bias, no R_S      0.9000        1.0000
```

  The gap in the last row is real and is $r_o$: with no source resistor the drain still
  moves, and channel-length modulation supplies a little feedback of its own.
- **M9 states a fact the course could not show.** Its concepts say a bipolar divider
  *"has to be much stiffer than module 2's"*. Measured: module 2's own 500 kΩ/250 kΩ
  divider, with a base on it instead of a gate, falls from **4.0000 V to 2.4866 V** — a
  1.51 V collapse — and $I_C$ lands at 0.9081 mA. Holding the ratio and scaling the
  impedance isolates it: 75 kΩ/24 kΩ sags 186 mV and gives 1.0236 mA; 750 kΩ/240 kΩ sags
  1074 mV and gives 0.5909 mA. Across $\beta$ = 50…300 the stiff pair moves −8.3%/+6.4%
  and the weak one −32.1%/+46.3%.
- **Checked and found correct, recorded so the next cycle does not re-derive it:** a
  diode-connected MOSFET sits exactly $V_{th}$ inside saturation at every current
  ($V_{DS}-V_{ov} = 1.0000$ V measured, against the device's $V_{th}$ of 1.0); the
  saturation square law evaluated at the overdrive the circuit settles on reproduces the
  solved current to five figures; and the shipped `VT` is 25.852 mV, so the course's
  $g_m = I_C/V_T = 40$ mA/V is the 25 mV hand convention and the device gives 39.59.

**4. Assessment Inquisitor.** EE202's existing questions are Track 3's ground and were
not rewritten. Audited for the one thing this cycle could falsify — whether any key
depends on the current-source stand-in being the device — and **none does**. The three
new units add no question deliberately: each is graded by the solver against the real
device, which is a stronger check than a distractor set, and each was additionally run
against wrong-but-plausible designs to confirm it discriminates rather than merely
passing its own answer (below).

**5. UX & Accessibility Hardener.** Content-side, as cycles 1, 4, 7 and 10 established.
Every math fragment in the units this cycle wrote or touched was pushed through the
shipped `MathML.render` — **250 fragments, 8 came back raw**. Two constructs, isolated by
probing 34 of them one at a time rather than guessing: the **escaped space `\ `**, which
is cycle 10's finding still unfixed in the tokeniser, and **`\bigl`/`\bigr`**. Everything
else renders, including `\int`, `\int_0^{L}`, `\mathrm`, `\mathrm{V\,s}`, `\left`/
`\right`, `\,`, `~`, `\mu`, `\partial`, `\propto`, `\parallel` and `\varepsilon`.
Repaired to **250 of 250, 0 raw, 0 swallowed**. No hard-coded colour and no raw HTML was
introduced; all four data tables are fenced `text` blocks inside `overflow-x:auto` rather
than markdown tables, which is cycle 4's rule for staying safe at 375px.

### The machinery finding this cycle did not spend

**The AC sweep has no separate small-signal excitation.** `MNA.acSolve` stamps
`b[k] = [p.value, 0]` for every voltage source — the **DC value is the AC drive** — and
`p.ac` is copied into the netlist at line 1165 and then read by nothing. Confirmed by
probe: a plain 12 V DC source appears at 12.0 in the AC solution.

This is not a defect for linear circuits, and the catalogue already knows it: EE102's
checks divide by `c.values('V')[0]` throughout, and `c.corner()` bisects on a ratio and
is amplitude-free either way. But it means the supply that **biases** a transistor also
**drives** the sweep, so the small-signal gain of a real stage cannot be separated from
the supply's own feedthrough without a decoupling capacitor placed for the simulator's
benefit rather than the circuit's.

**Not changed, and the reason is that the change is a real design decision.** Making
`ac` the AC excitation would be correct and is what SPICE does, but it silently reinterprets
every existing schematic that carries an `ac` field, and `c.gain()` checks across EE102
and CTRL510 are written against the present behaviour. That is a Track 2 change with a
migration in it, not a line. What it cost here is recorded honestly: a planned M3
common-source **gain** exercise became three DC-graded exercises instead, which is why
this cycle adds no AC build to a course whose subject is gain.

### Found in my own work, and fixed

- **A brief that named the wrong failure.** M1's build says the tempting wrong answer is
  a 12 kΩ resistor, from dividing the whole supply by the target current. My check message
  said that produces 1200 µA. **It produces 842 µA** — *below* target, not above — because
  the current the transistor settles at is not the current the mistaken arithmetic assumed.
  Caught by solving it rather than by re-reading the sentence. Both the message and the
  brief now carry the measured number, and the brief says why *both* 1000 and 1200 are
  answers that assume their own conclusion.
- **A claim about my own exercise, falsified by running it.** The M2.2 brief said the
  gate-biased design "passes every check the previous exercise had". Executed against the
  unit's real checks, it scores **1/4**. Rewritten to the truth, which is a better
  sentence: it passes the *first* check, so it is a properly saturated MOSFET carrying
  about a milliamp, and every other thing about it is wrong. A bias network can be right
  about the operating point and wrong about everything that matters.
- **Two check messages that recited a diagnosis whatever the reading was.** M9's told a
  learner showing 2383 µA that "around 590 uA is the signature of a divider at module 2
  impedances". Both messages now branch on the measurement, and the 2383 µA case gets the
  missing emitter resistor it actually has.
- **An orientation check that fired on the wrong circuit.** M2.2's `vov > 0` assert ran
  before the orientation assert, so a device turned upside down was told its gate divider
  was missing. Reordered — and written `!(vs - vd > 0.1)` rather than `vd > vs`, because
  an untouched canvas has every terminal at the same potential and the naive test would
  tell someone their device is upside down when it is merely unwired. Verified on all
  five cases: reference 4/4, bare canvas 0/4 reporting cut-off, turned device 0/4
  reporting orientation.

### What changed

**Four new units, appended to the modules they belong to**, and no module added. Each
existing unit kept its unsuffixed id, so nothing anyone has completed is orphaned —
checked rather than asserted: building every lesson id exactly as `src/app.js` does, at
HEAD and now, gives **1911 → 1915 ids, 4 new, 0 orphaned, 0 duplicated**, and the four
new ones are `EE202-M1-RD`, `EE202-M1-BD`, `EE202-M2-BD2` and `EE202-M9-BD`.

| | M1 `read` | M1 `build` | M2 `build2` | M9 `build` |
|---|---|---|---|---|
| title | Where the square law comes from, and where it stops | The device itself, and the line that finds its operating point | The same bias, with the device left in | Biasing a bipolar stage, with the base drawing what it draws |
| device | — | 1 × `NMOS` | 1 × `NMOS` | 1 × `NPN` |
| the measurement | 1707 words, one integral | 1.002 mA at $V_{GS}=V_{DS}=1.9797$ V | 1.0202 mA, stiffness 0.190 | 1.0236 mA, $I_{div}/I_B$ = 12.1 |
| reference / start | — | 4/4 · 1/4 | 4/4 · 0/4 | 4/4 · 0/4 |

**The reading is the prerequisite bridge**, and it uses only what EE201 actually
contains: the electrostatics of its module 1, the parallel-plate capacitor of its module
7, the drift equation of its module 5. It builds the MOS capacitor, gets the channel
charge $|Q_n| = C_{ox}V_{ov}$ with $C_{ox} = 3.45$ fF/µm² worked from a 10 nm oxide,
notices that the oxide voltage is $V_{GS}-V(y)$ and not $V_{GS}$, integrates along the
channel to the triode expression, reads $k = \mu C_{ox}W/L$ off it and puts this course's
$k = 2$ mA/V² at $W/L = 14.5$, then gets saturation from pinch-off — and with it **the
factor of one half, as the average of a linear ramp**, which is the error M1's quiz was
already marking. It closes on three places the result stops holding: velocity saturation
(and that the square law is a *long*-channel result, false of the device in the processor
running the page), sub-threshold conduction at $V_T\ln 10 = 59.5$ mV per decade — the
same 59.5 mV cycle 10 measured on EE201's diode, because it is the same statistics — and
the body effect, which module 2's own bias network provokes.

**M1's build is the novice rung the course did not have**: a diode-connected MOSFET and
one resistor, which is EE201's load line moved to a transistor without a symbol changing.
**M2.2 is the flagship**: the same specification as the exercise before it, with the
current source removed, so that $V_G$ sets $V_{GS}$ sets $I_D$ sets $V_S$ sets $V_{GS}$
and the solver has to iterate to the fixed point. Its fourth check measures
$1+g_mR_S$ from the learner's own circuit — $g_m$ as $2I_D/V_{ov}$, $R_S$ as $V_S/I_D$,
with only the data-sheet threshold imported — and requires at least 4. **M9's build is
the second device family**, and the first `NPN` anywhere in the catalogue.

**Each new build was run against wrong-but-plausible designs**, not only against its own
answer, because a check that only ever sees the reference has not been shown to
discriminate:

```
  M2.2   reference 4/4 · bare canvas 0/4 · gate bias with no R_S 1/4 ·
         device turned upside down 0/4 · R_S halved to 1k 2/4
  M9     reference 4/4 · bare canvas 0/4 · same ratio at 10x impedance 1/4 ·
         module 2's own 500k/250k divider 1/4 · no emitter resistor 0/4 ·
         divider 100x too stiff 1/4
```

**Six pre-existing items changed**, verified structurally rather than by reading the
diff — **4 units added, 0 removed, exactly 6 pre-existing items changed**: M1, M2 and M9
concept lists (each gaining the bullet that points at the new unit and carries its
measured number), M2's and M5's build briefs (the false sentences), and the course
outcomes, which gain two — one naming $1+g_mR_S$ as the thing a bias network is judged
on, one on checking the notebook model against the device.

**Two other courses touched, one sentence each.** EE121's and EE241's false claims about
the editor, above. This widens the cycle's diff and the brief says one course, so the
repair was kept to the sentence: no content restructuring, no new units, and the emitted
JSON for both files changed **exactly one line each** — checked, because cycle 4 found
that re-emitting a long-untouched course can carry `emit.py` drift with it. Neither did.
The alternative was to leave a claim this cycle had just proved false sitting in two
courses, which is how the EE131 defects sat in the artifact for weeks.

EE202: 35 units → **39** · 3.18 units per module → **3.55** · 0 read → **1** · 6 build →
**9** · 13 schematics → **19**, of which **6 contain a transistor**, against 0 in the
whole catalogue before this cycle.

### Left alone, deliberately

- **`PNP`, `PMOS` and `OPAMP` are still drawn by nothing**, and the catalogue is now at
  10 non-linear schematics out of 386. The op-amp is the interesting one: it is fully
  modelled, with rails and a finite gain and a `tanh` that keeps Newton steerable, and
  **not one module in the catalogue is titled for an op-amp**, and the phrase appears
  19 times across all 62 courses — EE221 4, EE211 4, EE101 4, EE202 3, EE102 2, EE231 1.
  EE202 ends at output stages and the differential pair "every op-amp starts with", and
  then stops. That is a missing *topic* rather than missing practice, it is the largest
  single one this track has found, and the device to teach it with is already modelled.
  Recorded with the counts.
- **The AC excitation, above.** Recorded with the line number and the reason it is a
  migration rather than a fix.
- **EE202 still has 3.55 units per module and one reading in eleven modules.** M2 through
  M11 have no reading. This cycle added the one that closes the prerequisite gap and did
  not write ten more; that is Track 1's density pass and cycle 1 established it is its own
  cycle. **Fifteen** courses remain thinner, all at exactly 1.00 units per module —
  CAP501, CE101, CE201, DL501, ELEC410, ELEC420, ELEC430, ETH501, FM501, GFX401, HPC401,
  ML401, QC510, ROB520, SEC301 — so this is a shared debt rather than a worst case.
- **CE101 was weighed again and passed over again.** Cycle 10 recorded it as *"a root of
  the CS degree's hardware chain"* and a stronger target than its stub status suggests —
  4 modules, 4 units, prerequisite of CE201 → CS210 and HPC401. It is still that. It is
  also a build-a-course cycle whose only gates would be `verify_quiz` and the emitter,
  where EE202 was a handed-over debt with three gates that can prove the fix. The graph
  cycle 10 recorded still holds and this cycle did not re-derive it.
- **M5's clipping-and-distortion build keeps its current source, and this was checked
  rather than assumed.** A perfectly linear current source cannot distort, so the module
  whose subject is distortion has an exercise that cannot exhibit it — which reads like
  this cycle's target defect. It is not fixable here: showing distortion needs either a
  time-varying source, which `MNA.tran` does not have (cycle 10 established this and it
  is still true — there is no `Math.sin` in the solver and `V` carries a DC value), or a
  DC sweep across several operating points, which one graded schematic cannot express.
  The clipping half *is* reachable with a real device and would make a good M5.2. Recorded
  as the next instalment rather than started.
- **EE202's `credits` and `hours` unchanged at 10 and 130**, and `catalog/_spine.ee.json`
  untouched. The spine carries course metadata only, and 39 units against a nominal 130
  hours remains light rather than heavy.
- **Pre-existing hedge words left where they are.** EE202 carries one "simply" and 17
  "just" at HEAD, and carries exactly the same at the end of this cycle — measured by
  diff rather than by counting twice, so the number is "0 introduced" rather than "17
  found". Sweeping prose in modules this cycle did not otherwise touch is Track 1's job.
- **The escaped space is still 35% of the catalogue's raw-markup debt.** Cycle 10
  measured 369 of 1053 fragments and named the one-line tokeniser fix. This cycle
  rediscovered it in its own drafts, repaired its own eight, and did not touch the
  tokeniser — that is a `src/studio.js` change and Track 2's ground.
- **`docs/programs` aged out two payloads and gained new ones for EE202, EE121 and
  EE241.** The rolling generation window, as every cycle since 1 has established, and
  this cycle built three times. Verified rather than assumed: **65 payload files on disk,
  65 named by one of the 3 retained generations, covering 62 distinct courses, 0 orphaned
  and 0 missing.**

### Gates, after

Every pre-existing number unmoved. Six numbers moved, each by exactly what was added.

```
verify_circuits      All good: 85 circuit exercises, 360 checks · 564 labels
                     (82 + 3 · 348 + 12 · 543 + 21)
                     EE202/M1   reference 4/4 · start 1/4
                     EE202/M2.2 reference 4/4 · start 0/4
                     EE202/M9   reference 4/4 · start 0/4
verify_circuit_model All good: 1475 analyses vouch for every number they return and 84
                     refuse rather than guess · 15 plots · 15 floors, 17 ceilings ·
                     386 published schematics, 365 with a DC point   (1457 + 18 · 380 + 6)
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_quiz          All good: 1366 questions in 252 quiz units and 1103 holes in 217
                     blanks units · 3260 per-option explanations · 6572 draws · 24.5%
verify_derivations   All good: 1248 steps across 46 courses
verify_labs          All good: 20 labs across EE202, EE121 and EE241
verify_circuit_ui    All good: 78 driven keys and gestures, says 10 things while doing it
verify_theme         All good: theme tokens, 135 contrast surfaces in both themes,
                     the 375px topbar and the mobile drawer
                     — these two were NOT captured at baseline, and are reported here
                     without a before. The diff is content-only (catalog/ and the build
                     artifacts under docs/; no file under src/ was touched), so neither
                     can be affected by it. verify_circuit_ui's 78/10/15 is in any case
                     identical to the figure cycle 10 recorded.
emit.py EE202        ok — 11 modules, 5 labs, capstone +tests
emit.py EE121        ok — 10 modules, 7 labs, capstone +tests   (JSON diff: 1 line)
emit.py EE241        ok — 10 modules, 5 labs, capstone +tests   (JSON diff: 1 line)
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12923 -> 12967 KB ·
                     inlined 14140 -> 14183 KB · shell 1188 KB unchanged
catalogue            62 courses, 368 modules, 1915 units (1911 + 4)
```

Beyond the gates: every number written into the four new units computed by loading
`src/circuit.js` as shipped and solving, before it was written — the 1.0202 mA and the
0.1853 sensitivity measured by perturbing $k$, the 1.51 V divider collapse, the 842 µA
that falsified my own brief, and the $\beta$ and $k$ spreads at four network stiffnesses;
all three new builds run against **five and six wrong-but-plausible designs** to confirm
they discriminate; all 250 math fragments rendered through the shipped `MathML.render`
(250 of 250, 0 raw); hedge words counted by diff against HEAD rather than by counting
twice (0 introduced); the EE202 diff compared structurally against HEAD rather than as
lines (4 added, 0 removed, 6 changed); every lesson id in the catalogue rebuilt exactly
as `src/app.js` builds them at HEAD and now (1911 → 1915, 0 orphaned); and the payload
window checked for orphans.

---
## Cycle 18 — TRACK 5: UI, Layout & Visual Aesthetics

*(the runner labels this commit "cycle 5"; its counter restarts per run and this log's
does not. Cycles 1–4 of the current run are entries 14–17 above.)*

**Target: the canvas palette — `Sandbox.palette()` in `src/studio.js`, and the two quiet
tiers it hands to every drawing surface in the application.** One subsystem, defined by
what it paints rather than by where it sits: 13 visualisers, 3 tune models, the analysis
plot, the schematic canvas and the breadboard, **62 paint sites** across `src/studio.js`
and `src/circuit.js`. It is the only ink in the app that is not a DOM node.

Chosen because it is the debt this track has named six times and taken none. Cycle 2
measured `P.dim` at 2.93:1 and `P.faint` at 1.86:1 and handed them to Track 5 by name;
cycle 5 re-measured them, published three candidate values and did not take them; cycles
6, 8, 11 and 15 each re-recorded them. Cycle 11's entry closes: *"it is now the only
Track 5 debt that four separate cycles have named without anyone taking it. It should be
the target, not the leftovers."* This cycle is that.

### Baseline, captured before any edit

```
85 circuit exercises / 360 checks · 564 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1248 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3260 per-option explanations · 6572 draws · answer in the top slot 24.5%
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui   78 driven keys, 10 things said, 15 kinds above their stamp floor
circuit_model 1475 analyses · 84 refusals · 15 plots · 15 floors, 17 ceilings
              386 published schematics, 365 with a DC operating point
tune_ui      423 clamped openings · 462 targets · 105 paints · 270 drags · 493 mounts
desk         61 expressions · Desk.css() hands the theme gate 102 lines
theme        14 exemptions · 135 contrast surfaces x 2 themes · tightest text 4.61:1
             (.q-hint [light]) · faintest state 1.11:1 · 3 held below the floor on
             purpose · 74 read their ink out of the stylesheet
build: 3 parts / 111 keys · 32/32 + 30/30 · 13 visualisers · 3 tune models · 15 symbols ·
       62 payloads, 12967 KB · inlined 14183 KB · shell 1188 KB
```

### The attacks

**4. UX & Accessibility Hardener** — taken first, as this track's brief is mostly its
brief. Every ratio computed from the WCAG 2.1 sRGB formula against the composited stack,
in **both** themes, before the fix and again after.

- **The handed-over description was too kind, and the number was single-theme.** Five
  cycles recorded these two tiers as *"the axis grid, tick labels and legends of 13
  visualisers plus two canvases"*. Classified all 62 sites instead of trusting that:
  **47 of them draw text, and `P.dim` is the stroke of every wire the learner draws.**
  `src/circuit.js:3149` sets `strokeStyle = pal.dim` and then strokes `cur.wires` — the
  whole netlist. It is also the MCU pin names, the H/L and `pu` pin-state tags, the
  bar-graph range caption, the breadboard holes, the junction dots and the empty-block
  placeholder. The primary object on the schematic canvas was painted at **2.93:1 dark
  and 2.72:1 light**, under 1.4.11's 3:1 floor in both themes.
- **`P.faint` is a text colour 32 times out of 38.** Tick labels and axis captions —
  "dB", "Hz", "ω rad/s", "seconds", "thermal floor", "dB re 1 nV/√Hz", "cache size KB",
  "miss rate %" — at 10px, so WCAG 1.4.3 small text, at **1.86 / 1.73:1.**
- **Cycle 5's three candidate values were measured in the dark theme only, and the light
  theme is the binding one.** `--editor` is `#0A0B0E` dark and `#12151A` light, so every
  ratio on this surface is *lower* in the light theme. The handed-over candidates
  re-measured in both: `#6B7280` → 4.07 **/ 3.78**, `#767D8A` → 4.75 **/ 4.42**,
  `#7E8694` → 5.36 **/ 4.99**. **Two of the three do not clear 4.5 where it counts**, and
  a cycle that had taken the middle one on the strength of the recorded 4.75 would have
  shipped a light-theme failure. Corrected here rather than inherited.
- **The reason it could not simply be raised, which is why five cycles walked past it.**
  `--on-editor-3` was *also* the placeholder colour of `.nq-in input`, `.dsk-in input` and
  `.dsk-ta` — three rules cycle 11 wrote a deliberate `floor: 2.5` into the budget for,
  on the argument that a placeholder reaching AA stops being distinguishable from a filled
  field. So the canvas and the placeholder shared one token with opposite requirements,
  and moving it broke whichever one you were not looking at. `--on-editor-4`, by contrast,
  had **no consumer but the canvas** — checked, not assumed: it appears exactly twice in
  the repository, its definition and `palette()`.

**The machinery finding, which is the largest thing in this cycle**

**No gate had ever painted with the real palette, and that is why the defect survived six
cycles of gates.** `tools/verify_sandbox.mjs:35` says so in its own comment: *"palette()
reads CSS custom properties off the document, so hand it a stub that returns nothing and
let every colour fall through to its declared fallback."* `verify_circuit_model.mjs` does
the same. So all 747 draws, and every schematic analysis, painted with the **fallback
literals** — and the fallbacks were not the tokens:

```
                          dark   light        the token it stood in for
  circuit.js  dim  #888   5.55   5.16    vs   --on-editor-3  2.93 / 2.72
  circuit.js  faint #555  2.64   2.45    vs   --on-editor-4  1.86 / 1.73
```

`circuit.js` kept its own standalone palette for when `Sandbox` is absent, and it had
drifted since cycle 0. Every gate that exercises the drawing code was therefore looking at
a **different and, for `dim`, twice-as-legible picture** than a browser draws. A gate that
paints with a stand-in for the thing under test cannot see a defect in the thing under
test. This is the same shape as cycle 11's finding — the budget describing the stylesheet
rather than enforcing it — one layer further down.

**1. Senior Educator** — no prose in a palette, so pointed at the type scale, which is the
visual equivalent of whether a thing explains itself.

- **The canvas's own type scale bottoms out below the stylesheet's.** Counted: the
  stylesheet's smallest rule is 9.5px and there are 55 under 11px, exactly as cycle 11
  left it. The canvas draws at **8.5px** in two places (`circuit.js:2676`, the breadboard
  column numbers, and `:2805`, the MCU supply caption) — smaller than anything in the DOM,
  on a surface where a browser's text zoom does nothing at all, because canvas text is not
  text. Recorded, not fixed; see below.
- *Checked and left:* the 10px tick labels are the plotting convention and are now legible
  rather than merely small, which was the actual defect.

**3. Simulation Auditor** — no solver in a palette, so pointed at the composite, computed
from the source's own numbers rather than eyeballed.

- **Three sites paint a quiet tier through a `globalAlpha`, and raising the token raises
  them with it.** This is where a contrast fix turns into a visual regression, so each was
  computed before and after rather than assumed:

```
                                    before        after, alpha unchanged     shipped
  schematic snapping grid (faint)  1.28 / 1.27      2.06 / 2.07          0.50 -> 0.20
  breadboard channel wash (faint)  1.14 / 1.14      1.45 / 1.49          0.30 -> 0.12
  breadboard holes        (dim)    2.00 / 1.95      3.44 / 3.34          0.70 kept
```

  The first two are decoration and were held where they were. The third is not decoration
  — a hole is where a lead may go — so its alpha was kept and it clears 3:1 for the first
  time. Making the snapping grid the loudest thing behind a circuit would have been a
  worse defect than the one being repaired.
- *Checked and found sound:* `verify_sandbox`'s 747 draws at the extremes, `verify_tune_ui`'s
  423 hostile openings, 105 paints at 5 widths and 270 drags, and `verify_circuit_ui`'s 78
  driven keys all pass unmoved — a palette change cannot move them, and confirming that is
  the point of running them.

**2. Assessment Inquisitor.** No graded question in a palette, so — as in cycles 2, 5, 6
and 11 — pointed at the one thing in scope it can judge: whether a state announces itself
or merely exists.

- *Checked and found sound, recorded so it is not re-derived:* the bar-graph's out-of-range
  state is **not** colour alone. Over range draws a caret past the bar's end as well as
  turning amber (`circuit.js:2731`); under range draws no bar at all; and the numeric
  readout prints the value either way. Amber is confirmation, not the message.
- **The two decorations were the state defect here**, and they are above: a background that
  rises with the foreground is a state that stops announcing itself by becoming the thing
  it sits behind.

### What changed

**Tokens — `src/index.head.html`, `:root` only, so no theme can override them.**

| token | before | after | dark → light |
|---|---|---|---|
| `--on-editor-3` (`P.dim`) | `#565C68` | `#868E9C` | **2.93 → 5.96 · 2.72 → 5.54** |
| `--on-editor-4` (`P.faint`) | `#3A3F49` | `#78808E` | **1.86 → 4.94 · 1.73 → 4.60** |
| `--on-editor-rule` (`P.rule`) | — | `#6A7280` | 4.06 · 3.77 |
| `--on-editor-hint` | — | `#565C68` | 2.93 · 2.72 |

`--on-editor-hint` is the old `--on-editor-3`, unchanged in value and moved out of the
ramp under a name that says what it is for. The three placeholders now read it, which is
what let the canvas tiers move at all. **The ramp descends monotonically and every step
below the top is now legible in both themes:** 15.89 / 7.20 / 5.54 / 4.60 / 3.77, then
2.72 for the one job that is deliberately below AA.

**A fourth tier, `P.rule`, because both old names encoded loudness and neither encoded
kind.** `dim` and `faint` are both used for small text, so both have to clear 4.5:1
whatever they are called — which collapses the hierarchy the two names existed to express.
`rule` is where that hierarchy went: a mark found by position rather than by reading it,
held to 1.4.11's 3:1 and no more. Five dashed reference lines moved onto it — 0 dB, −90°,
the thermal floor, the settling band, and the unity line — plus the breadboard channel's
two edges, which the code's own comment calls *"the one feature of the board that is a
fact about the netlist"* and which were painted at 1.73:1.

**Both fallback tables now agree with the tokens.** `circuit.js`'s standalone palette went
from `{dim:'#888', faint:'#555', ink:'#eee', line:'#333'}` to the token values, and gained
`rule`. The gates have been painting the browser's picture since.

**The gate — a `canvas` section in `tools/verify_theme.mjs`, and a `canvas` block in
`tools/theme_budget.json`.** This track's gate read CSS, and the palette is JavaScript, so
nothing connected them. Four checks:

- **Every tier's fallback equals its token**, in `studio.js`'s own `v(name, fallback)` and
  in `circuit.js`'s standalone copy — the drift above, now held.
- **Every tier clears the floor its own use demands**, in both themes, against `--editor`.
- **The paint sites are recounted from source.** A tier's `kind` is a claim about how it is
  used; if the count moves, the claim has not been re-checked. This is what stops the next
  `f.text(…, P.rule)` from quietly putting small text on a 3:1 tier.
- **The two decorations are held under a ceiling, at the alpha read out of the source** —
  not out of the budget, because writing it in the budget would describe the code instead
  of holding it, which is precisely the failure cycle 11 found in this gate's first
  version.

**And a ceiling on the contrast section**, which had only ever had floors. The three
placeholders are surfaces whose defect is being *too loud*; a floor cannot say that, and
until this cycle they shared a token with the canvas, so raising the canvas would have
raised them and nothing would have objected. They now carry `"ceiling": 3.2`.

**The gate was not trusted until it was seen to fail. 13 mutations, 12 it had to reject
and one it had to pass**, each applied to the real files, run, and restored with the
restore verified by SHA-256:

```
   1  the faint tier reverted — token AND both fallbacks, so only the floor can bite
   2  the dim tier reverted the same way — the wires, the axes, the pin names
   3  the rule tier dropped under 3:1 in all three files
   4  the placeholders folded back onto the canvas tier (they get LOUDER — the ceiling)
   5  circuit.js's fallback back to '#888', where it had been since cycle 0
   6  studio.js's own fallback left behind when the token moved
   7  the snapping grid's alpha back to 0.5
   8  the breadboard channel wash back to 0.3
   9  a new tick label painted on the 3:1 rule tier — the site count moves
  10  the rule tier deleted from the palette while the budget still names it
  11  --on-editor-rule removed from :root
  12  both decorations pointed at one anchor
  13  a comment reflowed and nothing else — the control, which passes
```

Mutations 1–3 move the token **and** both fallbacks together, deliberately: with all three
in step the agreement check cannot be what objects, so only the contrast floor can. Without
that pair the entry would be claiming the gate enforces a number when it only enforced
consistency.

### Found in my own work, and fixed

Both were found by the mutation suite, not by re-reading the gate.

- **My first decoration check measured one site twice and the other never.** It matched
  `pal.<tier>` followed by a `globalAlpha` from the top of the file, so both entries
  resolved to whichever paints first. **Putting the snapping grid's alpha back to 0.5 was
  ACCEPTED**, and mutation 8 was rejected with a message naming the wrong surface — which
  is how it was caught, because the message was wrong rather than the verdict. This is the
  curriculum's own invariant: *a gate that skips what it did not expect is worse than no
  gate.* Each entry now names an `anchor` and the search starts there.
- **The fix for that was itself incomplete.** I added a check that an anchor occurs only
  once in the file — which does not catch two *entries* sharing one anchor, since that
  anchor is still unique. Mutation 12 was written for the repaired gate and was still
  accepted. The gate now records where each entry **landed** and rejects a second entry
  resolving to the same paint site.

### Left alone, deliberately

- **55 stylesheet rules are still under 11px, and `src/desk.js` has 6 more that cycle 11
  never counted** — it was not wired into this gate until cycle 12. Same argument as cycle
  11: a type-scale pass touches every screen and would have meant verifying none of them.
  The count is unchanged at 55, measured rather than assumed.
- **The canvas draws at 8.5px in two places**, above. Fixing it means re-laying-out the
  breadboard's column numbering inside a fixed grid pitch, which is a layout change to the
  board rather than a colour one, and this cycle's diff is already in three source files.
  Recorded with the line numbers, which is more than it had.
- **`--lime` is still used as ink in 35 places and the light theme puts most at 3.4–4.1:1.**
  Cycle 11 counted them and declined for the reason that still holds: it is the accent
  weight of every screen in the application, a decision about the design language rather
  than a repair. Unchanged and unattempted here.
- **The 61 shell surfaces that describe rather than enforce.** 135 budgeted, 74 read their
  ink from the stylesheet. Cycle 11 built the mechanism and called back-filling the rest
  *"the first thing the next Track 5 cycle should do"*. This cycle did not do it, and the
  reason is that it is a strictly larger job than it looks — annotating 61 entries with a
  `sel` each means reading 61 rules — and it competes with a defect five cycles had
  already proved nobody would take if it stayed in the leftovers pile. The debt is
  restated with its current number so the next cycle inherits 61 rather than 58.
- **`palette()` runs a `getComputedStyle` per `frame()` call and there are 7 call sites.**
  A visualiser that calls both `frame()` and `kit.palette()` reads the token table twice a
  draw. It is bounded — `verify_tune_ui` confirms one repaint a frame — and caching it
  means an invalidation hook on the theme toggle, which is a Track 2 change with a
  lifecycle in it rather than a line. Recorded with the count.
- **No author file, no `catalog/*.json`, no lesson id and no schema was touched**, so
  `emit.py` was not run and the staleness guard is not armed. The mechanical confirmation
  is that the payload total is **12967 KB before and after** and `git status` reports
  nothing under `docs/programs` — no course's JSON moved, so no payload could.
- **`docs/programs` is untouched for the same reason**, so the rolling-generation check
  every cycle since 1 has run has nothing to check this time.

### Gates, after

Every pre-existing number unmoved. Three moved: the theme gate's two new `canvas` lines,
and the two artifact sizes, by the CSS, the palette tier and the gate's own new code.

```
verify_theme         All good: 14 exemptions · 135 contrast surfaces x 2 themes —
                     unmoved — tightest text 4.61:1 (.q-hint [light]), faintest state
                     1.11:1, 3 held below the floor on purpose, 74 read from source
                     canvas  10 palette tiers, both fallback tables agree with the
                             tokens they stand in for                            [NEW]
                     canvas  154 paint sites across 9 tiers clear their floor in both
                             themes · quietest 3.77:1 (rule [light]) · 2 decorations
                             held under their ceiling at the alpha the source
                             declares                                            [NEW]
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuit_ui    All good: 78 driven keys and gestures, says 10 things while doing
                     it, holds 15 kinds above their stamp floor
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_tune_ui       All good: 423 hostile openings clamped, 462 targets inside their
                     axes, 105 paints at 5 widths, 270 drags, 493 mounts
verify_circuits      All good: 85 circuit exercises, 360 checks · 564 labels
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_circuit_model All good: 1475 analyses, 84 refusals · 15 plots · 386 published
                     schematics, 365 with a DC point · 15 floors, 17 ceilings
verify_desk          All good: 61 expressions · Desk.css() hands the gate 102 lines
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3260 per-option explanations · 6572 draws · 24.5%
verify_derivations   All good: 1248 steps across 46 courses
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12967 KB — unchanged ·
                     inlined 14183 -> 14186 KB · shell 1188 -> 1191 KB, of 1536
```

Beyond the gates: all 62 paint sites classified by what they actually paint rather than by
the name of the tier, which is what turned "the axis grid and some legends" into "every
wire on the schematic canvas"; every ratio computed from the WCAG 2.1 sRGB formula against
the composited stack in **both** themes, before and after; cycle 5's three handed-over
candidates re-measured and **two of them falsified** for the light theme; the three
alpha-composited surfaces computed before, after, and after retuning, so a contrast repair
did not ship a decoration regression; the fallback tables measured to show the gates had
been painting a different picture from the browser; and the new gate run against **13
mutations — 12 it had to reject and one it had to pass** — which is the run that found it
was accepting two of them.

---

---

## Cycle 19 — TRACK 6: Edge Cases, Resilience & Accessibility

*(the runner labels this commit "cycle 6"; its counter restarts per run and this log's
does not. Cycles 1–5 of the current run are entries 14–18 above.)*

**Target: `src/app.js`'s progress persistence layer** — `P` and the three doors into it,
`saveSoon`/`saveNow`, `warnNoStorage` and the save indicator, `exportProgress`,
`importProgress`, `resetProgress`, and the profile controls that drive them. With it the
two files it cannot be audited apart from: `Store` in `src/engine.js`, which is the thing
that actually writes, and `server/merge.mjs`, which is what decides whether a write means
anything once an account is involved.

One subsystem, and the one this track was explicitly left. Cycle 12 closed with it named
as the debt it was leaving: *"`src/app.js`'s own persistence layer was not audited — `P`,
`saveSoon`, `resetProgress`, the progress export and import, `warnNoStorage`. It is the
third file in Track 6's row, it is where a storage defect costs a learner their whole
record rather than their calculator history, and it is a cycle of its own."* Seven cycles
have passed and no Track 6 cycle has run since. This is that cycle.

### Baseline, captured before any edit

```
85 circuit exercises / 360 checks · 564 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1248 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     · 3260 per-option explanations · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys, 10 things said
circuit_model 1475 analyses, 84 refusals · 15 plots
     · 386 published schematics / 365 with a DC point
tune_ui 21 tune units · 423 hostile opening values · 462 targets · 270 drags · 493 mounts
desk 61 expressions · 6 worst-case shapes · 10 readings · 102 css lines
theme 135 contrast surfaces x 2 themes · 154 paint sites / 9 tiers · quietest 3.77:1
api 30 passed, 0 failed
build: 3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers · 3 tune models ·
       15 symbols · 62 payloads totalling 12967 KB · inlined 14186 KB · shell 1191 KB
```

`test_api.mjs` was captured too, and it is not in the curriculum's list. It is the only
gate that covers `mergeProgress`, this cycle changes `mergeProgress`, and a baseline taken
after the edit is not a baseline.

### The defect that made this cycle worth doing

**"Reset progress" did not reset anything, for exactly the learners who had most to lose.**

`server/merge.mjs` states its own rule in its header: *"Every field here has a rule chosen
so that a merge can only ever move progress forward."* Union on `completed`, max on `quiz`
and `activity` and `xp`, newest-wins per key on `code`. That rule is right for two devices
both doing work. It is wrong for the one action whose entire purpose is removal, and the
server has no other endpoint — `PUT /api/progress` is merge-only, there is no replace.

So for a signed-in learner the sequence was: press Reset, confirm, `resetProgress()` empties
`P` and calls `saveNow()`; `saveNow()` calls `syncSoon()`; 2.5 seconds later `syncNow()`
pushes the empty document; the server unions it with the full one and hands everything
back; `adopt()` puts it into `P`; and `Store.save(P)` writes it to local storage as well —
so even the local copy, which really had been cleared, is restored from the server. The
toast is on screen for 2.6 seconds. It says "Progress cleared".

Driven, not reasoned about — the real `mergeProgress` with the document `resetProgress`
actually produces:

```
completed after "Progress cleared": {"EE101-M1":true,"EE101-QZ":true,"EE111-M3":true}
xp after "Progress cleared": 260
quiz: {"EE101-QZ":100}   activity: {"2026-08-30":5}
```

The card above the button reads *"this cannot be undone"*. It was the only sentence on
that card that was not true.

**Import had the same shape in the other direction.** It replaces `P` locally and merged
remotely, so importing a one-unit export onto a three-unit account left all three on the
server and told the learner *"Restored 1 completed unit"*.

### The attacks

**4. UX & Accessibility Hardener** — taken first, because this track's brief is mostly its
brief.

- **The one channel in the app that says whether progress is being kept was a bare
  `<span>`.** `#save-state` goes to "Saving…", "Saved" and "Not saved", and it had no
  role, no accessible name and no live region. Driven against a store that refuses: the
  element reads `"Not saved"`, carries class `bad`, and `aria-live` is `null`. A screen
  reader is told nothing. The only other channel is `warnNoStorage`'s toast, which is
  latched to fire **once per session** and shows for 2.6 seconds.
- **`.save-state{display:none}` below 640px.** Every phone. `display:none` takes the node
  out of the accessibility tree as well as the layout, so on a phone the indicator did not
  exist at all — and a phone in a private tab is precisely where progress is not being
  stored. This is the same mistake the topbar's own metric pills shipped with until cycle
  11 measured them, three rules further up the same media block, with the correction
  written in a comment beside it.
- **The reset confirmation was invisible to the people most likely to press twice.**
  Arming un-hid `<span hidden>Press again to confirm</span>` and changed nothing else. Two
  compounding faults: revealing text a live region *already holds* announces nothing in
  most screen readers — the region has to be present and empty and the text has to arrive
  — and the button's accessible name stayed "Reset progress" in both states. So a
  screen-reader user pressed it, heard nothing, pressed it again because nothing had
  happened, and erased everything. A confirmation that cannot be perceived is not a
  confirmation; it is a delay that only sighted users get the benefit of.
- **The 4-second disarm window** was not long enough to hear a sentence, find the button
  again and press it.
- **`#acc-msg` — "Wrong email or password" — was a bare span too.** Press Sign in with a
  bad password and a screen-reader user is left on the form with no way to find out why.
- **The sign-in buttons disable themselves while the request is in flight,** and a browser
  will not keep focus on a disabled element. So a keyboard user pressing Sign in was
  thrown to the top of the document for the length of the round trip, and then had to find
  their way back to read the failure they could not hear.
- **Reset and import both call `go({view:'profile'})`,** which replaces `main.innerHTML`.
  The control that was just pressed is destroyed, focus falls to `<body>`, and a keyboard
  user is silently returned to the top of the page.

**3. Simulation Auditor.** Its brief is zero, negative, enormous and identical values, and
here the "model" is the progress document: a JSON file a learner is invited to hand the
app from their own disk.

- **`importProgress` believed the file.** `Object.assign` straight into `P`, guarded only
  by `typeof inc.completed === 'object'`. Driven with hostile documents, and none of them
  threw — which is what made them survivable long enough to be saved and pushed:

  | file says | what the learner got |
  |---|---|
  | `"xp": "9999"` | level **67**, topbar reads `9999` — a string has its own `toLocaleString` |
  | `"xp": {"a":1}` | level **NaN**, topbar reads `[object Object]` |
  | `"activity": [1,2,3]` | passes `typeof === 'object'`; every lookup then misses, so the streak reads 0 for ever |
  | `"completed": {"B": false}` | counted as a finished unit in "Restored N completed units" |
  | `"__proto__": {…}` | `Object.assign` writes through `[[Set]]`, so the inherited setter ran and **the prototype of `P` was replaced** |

  And the consequence is worse than the display. `mergeProgress` settles XP with
  `Math.max(Number(a.xp) || 0, Number(b.xp) || 0)`, so a non-numeric `xp` does not merely
  look wrong — it pushes as 0 and **zeroes the XP the account already held**.
- **The three doors into `P` trusted their input to three different degrees.** `adopt()`
  (sync) recomputed XP from `completed` and repaired `activity`; `boot()` (local store)
  repaired `activity` only; `importProgress()` (a file off a disk) did neither. The
  disagreement was the defect, not any one door, and the loosest one was the door that
  opens onto the least trustworthy source.
- **Checked and found sound, recorded so the next cycle does not re-derive it:** `Store.save`
  catches everything and returns `false`, so `saveChain` cannot be poisoned by a rejection
  — I expected it could be, drove it, and it cannot: `setSaveState` runs *before* the chain,
  so a throw there throws out of `saveNow` synchronously and leaves the chain untouched.
  `Store.load` already refuses anything that will not parse. `parseEng`-style clamping is
  not this file's problem. `syncNow` is guarded by `syncState.busy` against re-entry, and
  `Sync.call` bounds every request with an `AbortController` so an unreachable server
  cannot hold boot hostage. `bootFailed` already catches an unhandled boot rejection and
  paints something explaining it.

**1. Senior Educator** and **2. Assessment Inquisitor** have no prose and no graded
question in a storage layer, so both were pointed at the thing in scope they can judge:
whether what the app *says about the learner's own record* is true.

- **"Progress cleared" was false.** So was **"Restored 1 completed unit"**. So was
  **"this cannot be undone"** — it could be, and was, automatically, within seconds. Three
  sentences the app tells a learner about their own work, and all three were wrong for
  anyone signed in. The Inquisitor's rule that an explanation must be true whichever
  option was taken applies exactly here: the sentence has to be true about the account as
  well as about the tab.
- **`Store.status()`'s own comment describes a call that did not exist.** It reads:
  *"Called before the first save so the UI can warn straight away rather than after the
  learner has already earned progress they are about to lose."* Nothing called it.
  `setSaveState` ran only from inside `saveNow`, and `Store.status()` was reached only
  from `storageNote()`, which runs only if the learner opens Profile. So the indicator was
  blank from boot until the first write, and in a private window the first thing it ever
  said was "Not saved" — after the loss it was written to prevent. The mechanism existed;
  nothing was wired to it.

### The persistence defect

**The last 900 ms of every session were never written.**

`saveSoon` is `debounce(saveNow, 900)`, and nothing flushed it. Finish a unit and close the
tab inside that window and the completion, its XP and the day's activity were simply gone.
On a phone there is no close at all — the tab is backgrounded and then killed, and
`visibilitychange` is the only warning there is.

`src/desk.js` has flushed on `pagehide` and `visibilitychange` since cycle 12. The file
that carries every completed unit, every quiz score and every saved code file did not. The
discipline existed in the codebase, in the file holding the least valuable data of the two.

It also could not simply be wired to the existing save. `saveNow` queues its write through
`saveChain.then(...)` — a microtask, which an unloading document is under no obligation to
run — and `Store.save` is an `async` function that `await`s the backend before it ever
reaches `localStorage`. Measured rather than assumed: with `window.storage` present,
`Store.save()` returns with **nothing** in `localStorage`, and `Store.saveSync()` returns
with the document in it.

### What changed

**A synchronous unload write.** `Store.saveSync` in `src/engine.js` — `backendSet`'s
localStorage half with the awaits taken out, everything it can honestly finish before the
handler returns and nothing it cannot. The backend needs a round trip and is deliberately
not attempted; the next open syncs it. `flushSave` in `app.js` is bound to `pagehide` and
to `visibilitychange`-when-hidden, and writes only when something is actually owed —
`saveDirty` is set when the *intent* to save is formed rather than when the timer fires,
so an unload knows about a write the debounce has not made yet, and a tab switch with
nothing pending does not serialise the whole record.

**A reset that crosses the wire — `clearedAt`.** A document carries it when its owner
cleared or replaced it wholesale. `mergeProgress` takes the larger of the two sides' and
discards any document whose own `updatedAt` predates it. Still order-independent, because
both sides compute the same value and are tested against it rather than against each other
— asserted, not asserted-to-be: `merge(a,b)` and `merge(b,a)` are byte-identical.

A timestamp rather than a `replace: true` flag on the endpoint, and the difference is the
whole point. A replace fixes the resetting device and nothing else: a second machine that
has been asleep since before the reset pushes the copy it still holds and the union brings
everything back. The tombstone travels with the document, so the second machine honours a
clear it has never seen. And because it is a *time* and not a flag, work genuinely done on
another machine *after* the reset is not the reset's to delete — both directions are
gated, and both are checked.

**One rule for taking a document into `P`.** `sanitiseProgress` — collections are objects
of the shape we declare (`Array.isArray` is the half `typeof` cannot do), scalars are
coerced, `__proto__` is skipped rather than copied because copying it *is* the pollution,
and XP is a floor that `recomputeXp` replaces with the exact figure. Applied at all three
doors: `boot`, `adopt` and `importProgress`. XP is deliberately left as stored at boot and
not recomputed there, because boot runs before `loadDegreeChunks` and the catalog cannot
yet value a course unit — the same reasoning `recomputeXp`'s own `MISSING_PROGRAMS` guard
already encodes.

**The save indicator says something, to somebody, without saying it constantly.** The word
moved into `#save-state-txt`, which is `aria-hidden`; the announcement goes to
`#save-state-say`, a `.vh` `role="status"` sibling. A session is hundreds of saves, and a
live region wired to the visible word would read "Saving, Saved, Saving, Saved" over the
top of the lesson — which is how a live region gets switched off, and then the one
announcement that mattered is gone with it. Only a change of *health* is announced.
Measured: **2 announcements across 62 state writes**, one when it breaks and one when it
recovers, with the visible word still tracking every save.

**And it survives a phone.** The 640px rule no longer hides the element; it hides the
*word* and zeroes the box's `min-width`. The announcement channel is `position:absolute`
and out of flow, so this costs nothing — which matters, because the theme gate's topbar
arithmetic has no column for this element and 291px of bar has none to spare. Standing the
word down rather than the element is what keeps both true at once.

**The confirmation can be heard, and says which press this is.** The note is an empty
`aria-live="assertive"` region and the sentence arrives when the button is armed —
assertive rather than polite because the very next thing this learner does is press again,
and a queued announcement arrives after the erase. The button's *visible* label changes to
"Confirm — erase all progress", so the accessible name changes with it rather than
diverging from it (WCAG 2.5.3). The window is 12 s, re-armed from scratch rather than
stacking timers.

**Focus is returned** after reset and import, to the control that did the thing.
**`#acc-msg` is a live region.** **The sign-in buttons report busy with `aria-disabled`
and a re-entry guard** instead of `disabled`, so the button that was pressed keeps focus;
`button[aria-disabled=true]` takes the same dimming `button:disabled` already had, so
nothing new was introduced to the palette.

**A new gate — `tools/verify_progress.mjs`.** This subsystem had none, which is why several
of the defects above are as old as the files. It mounts the **real app** through the
existing `app_stage.mjs` and drives it, in seven sections: the unload flush (including with
a backend in front of it, and `visibilitychange` separately from `pagehide`); a store that
refuses, reported on the panel **and** in the live region, asked separately; the live
region's silence across 20 healthy saves; 29 hostile documents; the reset and the import
driven through the real `mergeProgress`; the confirmation driven by actually pressing the
button twice; and the markup and stylesheet contract. Two small additive changes to shared
harness made it possible — `app_stage` now takes a `localStorage` (a store that never fails
cannot show a failure is reported) and records document listeners (a listener that went
nowhere could not tell a registered handler from an absent one).

The gate was not trusted until it was seen to fail. **29 mutations, 29 rejected**, with the
control run passing before and after: both unload listeners removed separately, the dirty
flag dropped, the flush made unconditional, the flush put back through the async save,
`saveSync` stopped from writing, the boot-time status check removed, the panel warned with
the region silenced and the region warned with the panel silenced, the live region wired to
every save and wired to none, the word un-hidden from screen readers, the import returned to
`Object.assign`, `xp` uncoerced, `Array.isArray` dropped, the `__proto__` skip dropped, the
falsy-completion filter dropped, the tombstone unstamped, the merge stopped from honouring
it, the tombstone's own `>=` narrowed to `>`, the confirmation returned to un-hiding its
text, arming silenced, the button's label frozen, the second press made unnecessary, focus
left dropped, the phone rule returned to `display:none` and inverted, `.vh` returned to
`display:none`, and the sign-in buttons disabled again.

### Found in my own work, and fixed

- **A hypothesis I had to kill.** I was confident `saveChain` could be poisoned — one
  throwing continuation leaves a rejected promise, and every later `.then` skips its
  callback, so all persistence would die silently for the rest of the session. Drove it:
  it cannot happen. `setSaveState` runs before the chain, so a throw there throws out of
  `saveNow` synchronously and the chain is untouched, and `Store.save` catches everything
  internally. Recorded rather than quietly dropped, because a plausible defect that turns
  out not to exist is worth the next cycle not re-deriving.
- **My first gate read a different node than the app writes to, and three sections were
  wrong because of it.** `app_stage` memoises one element per id and hands *that* to every
  `$('#thing')` the app makes, while `renderShell` parses a string of HTML into `#app` —
  two trees, and nothing re-points the memo at the parsed children. So the gate asserted
  behaviour against nodes nobody writes to and reported correct code broken. It would have
  reported broken code clean just as readily. Behaviour is now checked through `shellEl`
  and markup through the parsed shell, each labelled, with the reason in the file header.
- **Five mutations walked straight through the first run — 24 of 29 — and every one was a
  real hole.** `visibilitychange` was never fired, so half the flush was untested. The
  async-save mutation passed because the stage had no `window.storage`, and without a
  backend `Store.save` *is* synchronous — so the check that mattered most was passing for
  a reason that would evaporate in the browser it was written for. `boot()`'s call to
  `paintSaveState` was never checked, only the function itself. The array check asked
  whether the *result* was an array rather than whether anything had survived being one —
  drop `Array.isArray` and `completed: ["A","B"]` becomes `{0:true,1:true}`, two units
  nobody finished, and every assertion passed. And the `__proto__` check tested the
  document, which is rebuilt from a fixed key list and is clean whether the guard exists
  or not; what the guard actually protects is the **slots**, which are carried through.
  All five are cycle 11's finding happening again: a check that reads plausibly and
  enforces nothing. It is the entire argument for the mutation run.
- **A stray `—` left as literal text in a comment**, from an escape-swapping edit.
  Cosmetic, caught reading my own diff rather than by any gate.

### Left alone, deliberately

- **A second device can still resurrect work if its clock is wrong.** The tombstone
  compares timestamps across machines, so a device running ten minutes fast keeps a stale
  document through a reset. The alternatives are a server-assigned logical clock or
  per-key tombstones, both of which are a redesign of `mergeProgress` rather than a repair
  to it. Recorded with the reason.
- **`P.activity` still grows without bound** — one key per active day, for ever. A day is
  a short string and a small integer; pruning would silently delete a streak's evidence,
  which is worse than the leak. Same judgement cycle 12 made about `state.vars`.
- **No size cap on the progress document.** `P.build` holds whole schematics and `P.code`
  whole files, and `localStorage` will eventually refuse — which is now *reported* on both
  channels and at boot, and that is the honest half of the fix. Capping would mean
  choosing which of the learner's own work to discard, which is not a decision this layer
  should make silently.
- **`Store.status()` can still report `backend` while writes are actually landing in
  localStorage.** `backendSet` sets `mode = 'backend'` on a successful backend write and
  never demotes it, so a backend that starts failing while localStorage keeps working
  leaves the Profile card claiming progress "follows this page wherever you open it".
  Found while reading, not fixed: the demotion rule needs to distinguish a transient
  network failure from a dead backend, and getting that wrong makes the card flap between
  two claims. Handed on with the mechanism named.
- **The empty `#prof-reset-note` now contributes one 10px flex gap** where `hidden`
  contributed nothing. Checked rather than assumed: `.pcard-acts` is a left-aligned
  `display:flex` with `flex-wrap`, the note is the last child, and a zero-width element at
  the end of a left-aligned row moves nothing visible. The alternative — `:empty
  {display:none}` — would reintroduce the exact defect being fixed, because a live region
  that is `display:none` when its text arrives announces nothing.
- **`src/mcu.js` and the workbench were not touched.** Cycle 6 recorded the sketch panel
  as its own subsystem and cycle 12 agreed; nothing here changes that.
- **`P.dim` at 2.93:1 and `P.faint` at 1.86:1 on the canvas.** Cycle 2 measured them and
  handed them to Track 5; cycles 5, 6, 8, 11 and 12 have each recorded them again without
  taking them. That is now **six cycles**. They are in `src/studio.js`, they are not this
  subsystem, and a Track 6 cycle taking them would change the visual weight of 13
  visualisers. Cycle 5's candidate values still stand: `#6B7280` → 4.07, `#767D8A` → 4.75,
  `#7E8694` → 5.36. This has stopped being a leftover and is now the clearest single
  target Track 5 has.
- **No author file, no `catalog/*.json`, no lesson id and no schema was touched**, so
  `emit.py` was not run and the staleness guard is not armed. The mechanical confirmation
  is that the payload total is **12967 KB before and after**.
- **`docs/programs` holds 66 files against 62 in the current generation.** The rolling
  window, as every cycle since 1 has established. Verified rather than assumed: 62 named
  by the shell, **0 referenced but missing**, and the 4 unnamed are `_generations.json`
  plus three older payloads (`EE121`, `EE202`, `EE241`) whose courses each have a current
  payload on disk.

### Gates, after

Every pre-existing number unmoved, including `test_api`'s, which is the one this cycle put
most at risk. Two numbers moved by exactly what was added — the two artifact sizes.

```
verify_progress      All good: the progress store lands 6 unload writes without
                     outrunning the document, coerces 29 hostile documents into shape,
                     keeps a reset cleared across 7 merges, announces 2 things in
                     62 state writes, and holds 12 accessibility contracts      [NEW]
test_api             30 passed, 0 failed — against a server restarted on the new merge
verify_desk          All good: 61 expressions at the extremes · 6 worst-case shapes ·
                     10 readings that round-trip · a refusing store reported on both
                     channels · the stylesheet handed to the theme gate
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_theme         All good: 135 contrast surfaces x 2 themes · 154 paint sites
                     across 9 tiers, quietest 3.77:1 · the 375px topbar ·
                     the 50px id column · the closed drawer is out of the tab order
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3260 per-option explanations · 6572 live draws
verify_tune_ui       All good: 21 tune units · 423 hostile opening values · 462 targets
                     · 105 paints at 5 widths · 270 drags · 493 mounts
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuits      All good: 85 circuit exercises, 360 checks · 564 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_circuit_model All good: 1475 analyses, 84 refusals · 15 plots · 386 published
                     schematics, 365 with a DC point, all three ways
verify_derivations   All good: 1248 steps across 46 courses
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12967 KB — unchanged ·
                     inlined 14186 -> 14202 KB · shell 1191 -> 1207 KB, of 1536
```

Beyond the gates: the new gate run against **29 mutations, 29 intended verdicts** — a run
that began by letting 5 through and is the reason this entry has a finding about each of
them; the reset and the import driven through the **real** `mergeProgress` rather than a
restatement of it, in both directions and for order-independence; `Store.save` measured
against `Store.saveSync` with a backend present, which is the measurement that justifies
the second function existing at all; `test_api` captured before the edit and re-run against
a server restarted on the new merge, because a sync test run against a stale process
verifies the code it replaced; and the payload window checked for orphans and for missing
files rather than assumed.

---

## Cycle 20 — TRACK 1: Content & Conceptual Depth

*(The runner labels this commit "cycle 1" — a fourth run began and its counter restarted,
while this log kept counting. Run C's "cycle 1" is this file's cycle 14, exactly as
`ee95ded` was its cycle 7 and `f1a161b` its cycle 13.)*

**Target: MA121 (Linear Algebra), the seven modules holding a quiz and nothing else —
M4, M5, M6, M8, M9, M10 and M11.** Vector spaces and the complete solution, independence
and the four subspaces, change of basis, least squares, eigenvalues, the spectral
theorem, and the SVD. A learner met each as five concepts bullets and was examined on it
in the next unit.

Chosen on measurement. Scoring all 62 courses by **modules that examine without teaching**
— neither a `read` nor a `derive`, and no lab either — MA121 leads the catalogue with
**7 of 11**, ahead of EE241 at 4 and EE221 at 3. It is also a prerequisite of five
courses (DL501, GFX401, ML401, QC510, ROB520), the widest fan-out of any course in the
list, and its own prerequisite MA101 was repaired by cycle 7 — so the two compound in the
direction cycles 13 and 14 established.

M1, M2 and M3 were excluded because they are already the model the rest was never built
up to: three readings, three derivations, four numerics, a quiz, a blanks unit and a lab
each. **M7 was excluded because it carries a full lab** whose reference solution the gate
runs — cycle 1's MA111 reasoning applied unchanged — though its concepts list is repaired
below, because it states the same false claim M9 does. That leaves exactly the seven
modules that examine cold.

### Baseline, captured before any edit

```
85 circuit exercises / 360 checks · 21 tune units
216 numeric answers verified, 0 unchecked, 218 figure-only
1248 derivation steps across 46 courses (MA121: 55)
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     · 3260 per-option explanations · 6572 live draws
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys, 10 things said
circuit_model 1475 analyses, 84 refusals · 15 plots
desk 61 expressions · theme 135 contrast surfaces x 2 themes
tune_ui 423 hostile opening values · 462 targets · 270 drags · 493 mounts
progress 6 unload writes · 29 hostile documents · 7 merges · 12 a11y contracts
MA121: 11 modules · 47 units · 9 read · 9 derive · 8 bare modules · 5 labs
       49 questions · longest-is-key 22 (budget 22) · margin +7.2
       2550 math fragments: 2550 render, 0 raw, 0 swallowed, 2 unpaired
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads, 12967 KB ·
       inlined 14202 KB · shell 1207 KB
catalogue: 62 courses, 368 modules, 1915 units, 253 readings
```

`test_api.mjs` was captured too and **fails at baseline with `ECONNREFUSED` on port
4180** — it needs a live server, which is not running. It reads no catalogue file and
this cycle touches no server code, so it is out of scope rather than broken by this
cycle. Recorded because a gate that was failing *before* the edit must be said to have
been failing before the edit.

### The attacks

**1. Senior Educator.** Seven findings acted on, plus three claims that are false or
imprecise as stated in prose the cycle was not pointed at.

- *Announced, never derived, seven times over.* Fixed: seven readings and seven
  derivations, each deriving what its module asserts. The column space is obtained as
  "what $Ax$ can be" rather than defined; the complete solution is proved as a set
  equality by two inclusions; **every basis is shown to have the same size** rather than
  told to; the change-of-basis matrix is assembled from three steps instead of quoted;
  the normal equations come out of one perturbation argument; power iteration's rate is
  derived with both its hypotheses; the spectral theorem's two halves come out of one
  identity; and the SVD is built from module 10 applied to $A^{\mathsf{T}}A$.

- **The module states that power iteration converges, and its own quiz four questions
  later is the counterexample.** M9's bullet said long-run behaviour is decided by the
  largest $|\lambda|$, *"which is why power iteration converges to it"* — with no
  hypothesis attached. M7 says the same with a rate. The derivation needs
  $|\lambda_2| < |\lambda_1|$ **strictly**, and M9/Q4 asks for the real eigenvectors of
  the quarter-turn $\begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix}$, whose eigenvalues are
  $\pm i$ — both of modulus $1$. The course asks you to know that no real eigenvector
  exists and, through module 7's lab, hands you one. Fixed in both bullets and derived in
  the reading, with the failure worked on $\operatorname{diag}(5, -5)$ and the rate
  confirmed against measurement on $\begin{bmatrix} 4 & 1 \\ 2 & 3 \end{bmatrix}$
  (predicted $0.4$; observed consecutive error ratios $0.388$, $0.392$, $0.396$, $0.399$,
  $0.399$, $0.400$).

- **The projection matrix is stated with no hypothesis, and the course states the missing
  one three modules later.** M8's bullet gives
  $P = A(A^{\mathsf{T}}A)^{-1}A^{\mathsf{T}}$ unconditionally; the inverse exists only
  when $A$'s columns are independent, which **M10's own concepts list says** about
  $A^{\mathsf{T}}A$ and which M8 never connects. Worked: for $A$ with two proportional
  columns, $\det(A^{\mathsf{T}}A) = 64 - 64 = 0$ and the formula does not exist, while
  the projection onto the line through $(1,1,1,1)$ is $(3,3,3,3)$ — the mean, unique, and
  perfectly ordinary. **The projection always exists; the formula does not**, and what
  fails is the uniqueness of $\hat{x}$, not of $p$. Two bullets added.

- **Change of basis gives $B = S^{-1}AS$ and never says what $S$ holds** — the one thing
  people actually get wrong. Derived: $S$'s columns are the new basis vectors in the old
  coordinates, forced by $S(1,0) = b_1$. And the swap is priced: for
  $A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$ with the shear
  $S = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}$, the right answer is
  $\begin{bmatrix} 1 & 0 \\ 1 & 3 \end{bmatrix}$ and the swap gives
  $\begin{bmatrix} 3 & 0 \\ 1 & 1 \end{bmatrix}$ — **with the same determinant $3$, the
  same trace $4$ and the same characteristic polynomial $(\lambda-3)(\lambda-1)$.** Every
  invariant M6/Q3 lists as a test of similarity is passed by the wrong answer, because
  $SAS^{-1}$ is also a conjugation. Only pushing a known vector through separates them.
  Recorded because the obvious self-check cannot catch the commonest error.

- **"Never exactly two" is true and its hypothesis is invisible.** The argument needs
  infinitely many scalars, not anything about matrices. Over the field with two elements
  $x_1 + x_2 = 1$ has a genuinely non-trivial null space $\{(0,0),(1,1)\}$ and **exactly
  two** solutions, because the line $x_{\text{p}} + tz$ has only $t = 0$ and $t = 1$ to
  offer. That is the field a parity check lives over, so it is not an exotic footnote.

- **"The curvature along each eigenvector is that eigenvalue" is out by a factor of two.**
  The form along the unit eigenvector $q_1$ of $\begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$
  is $3t^{2}$, whose second derivative is $6$; the Hessian of $x^{\mathsf{T}}Ax$ is $2A$.
  What *is* exactly the eigenvalue is the **value** of the form on the unit eigenvector,
  and the useful general statement is the Rayleigh bound
  $\lambda_{\min} \le x^{\mathsf{T}}Ax/x^{\mathsf{T}}x \le \lambda_{\max}$. The bullet was
  replaced by one that says both.

- **The quadratic form sees only the symmetric part, and nothing said so.**
  $\begin{bmatrix} 1 & 4 \\ 0 & 1 \end{bmatrix}$ and
  $\begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}$ have the identical form
  $x_1^{2} + 4x_1x_2 + x_2^{2}$, verified symbolically, while the first has the single
  repeated eigenvalue $1$ and is defective and the second has $3$ and $-1$. The form
  cannot see either of the first matrix's eigenvalues. Bullet added.

- **The condition number is presented as a prediction.** M11/Q3's "about 4 digits" is a
  worst case attained only when the perturbation lines up with $u_{\min}$ while $b$ lines
  up with $u_{\max}$. The `why` was not touched — it is Track 3's ground and it is not
  wrong — but a bullet now says what the bound is and is not, and the reading derives it
  from $\sigma_{\min} \le ||Ax|| \le \sigma_{\max}$, confirmed by driving all unit
  directions: $||A^{-1}d||$ ranges over exactly $[0.14907, 0.44721]$, which is
  $[1/\sigma_{\max}, 1/\sigma_{\min}]$.

- *Left alone:* M5's four-subspaces bullet, M9's defective-matrix bullet and M10's
  Hermitian/unitary bullet are all correct as stated. The readings spend their space
  deriving them rather than restating them.

**2. Assessment Inquisitor.** All 49 questions in the course were checked against the
mathematics rather than skimmed. **Every key is correct, and no stem, option or `why` was
changed anywhere** — confirmed mechanically rather than asserted: the 49 stems, option
sets and keys are byte-identical to `HEAD`, the 49 explanations are byte-identical too,
and the gate reports MA121 unmoved at longest-is-key 22 against a budget of 22 with
margin +7.2. Everything this cycle added went into `read`, `derive` and `concepts`, so
the answer-tell budget could not move.

Recomputed rather than assumed, so the next cycle need not: $7 - 3 = 4$ for the nullity
of a $4\times7$ of rank $3$; five vectors in $\mathbf{R}^{4}$ dependent; $\det M = -3$
giving area $3$ with orientation reversed; $x = Q^{\mathsf{T}}b$ for orthonormal columns;
QR at roughly twice the flops of the normal equations; $\begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$
with eigenvalues $3$ and $1$; trace $7$ and determinant $12$ giving $3$ and $4$;
$\begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}$ defective; the quarter-turn's $\pm i$;
$\begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}$ at eigenvalues $3$ and $-1$ with the form
at $(1,-1)$ equal to $-2$; $\begin{bmatrix} 2 & -1 \\ -1 & 2 \end{bmatrix}$ with pivots
$2$ and $\tfrac{3}{2}$; $\begin{bmatrix} 0 & 5 \\ 0 & 0 \end{bmatrix}$ with both
eigenvalues $0$ and singular values $5$ and $0$; and $\kappa = 10^{6}$ against $10$
digits leaving about $4$. All hold.

**3. Simulation Auditor.** Six of the seven target modules contain no sandbox, tune,
build or schematic `numeric`. The persona was therefore pointed at the one executable
thing the modules make claims *about* — module 7's `power_method`, which M9's bullet
invokes by name — and at arithmetic in prose. The first is where the largest finding is.

- **`power_method` returns `0` as an eigenvalue, silently, in two iterations, for every
  matrix whose dominant eigenvalues are $\pm\lambda$.** Driven against the lab's own
  reference solution, extracted from the emitted catalogue and executed:

```
diag(5,-5)      -> value 0.0   vec [0.707107, 0.707107]   iters 2   ||Av - 0v|| = 5
diag(1,-1)      -> value 0.0   vec [0.707107, 0.707107]   iters 2   ||Av - 0v|| = 1
quarter-turn    -> value 0.0   vec [0.707107, 0.707107]   iters 2   ||Av - 0v|| = 1
```

  Zero is not an eigenvalue of any of the three. The cause is exact: the routine's
  stopping rule compares two consecutive Rayleigh quotients, and a vector that **swings**
  symmetrically has a *stationary* quotient — $v \cdot Av = \tfrac12(5) + \tfrac12(-5) = 0$
  at every step — so the test cannot tell "converged" from "oscillating". It fires on the
  earliest iteration it possibly can, which makes the wrong answer the most
  confident-looking output the function produces. The quarter-turn is **M9/Q4's own
  matrix**, whose correct answer is that it has no real eigenvector.

- **The capstone escapes this, and the reason is worth recording rather than assuming.**
  It runs power iteration on $A^{\mathsf{T}}A$, which is symmetric positive semidefinite,
  so every eigenvalue is $\ge 0$ and a $\pm\lambda$ pair is impossible. Verified by
  driving it. That is a property of $A^{\mathsf{T}}A$, not of `power_method`, and it stops
  protecting anything the moment the routine meets a general matrix.

- **One diagnostic names the opposite of its cause.** `power_method([[1e300,0],[0,1]])`
  raises `"iteration collapsed to the zero vector"`. It did not collapse — it
  **overflowed**: $\|w\|$ is $\sqrt{10^{600}} = \infty$, then every $x/\infty$ is $0.0$,
  and the *next* norm is genuinely zero. The message describes the symptom one step
  downstream of the fault.

- **Every number written into the seven readings was computed before it was written**, in
  SymPy and NumPy: the $3\times5$ system's rref, its three special solutions and the check
  that $(-4,3,0,-2,5)$ returns $(3,8,11)$; the inconsistent $b$ raising the augmented rank
  from $2$ to $3$; the GF(2) solution count; the exchange matrix
  $\begin{bmatrix} 1 & 1 & 2 \\ 1 & -1 & 1 \end{bmatrix}$ and its null vector
  $(-\tfrac32, -\tfrac12, 1)$ applied back to the original vectors to give $(0,0)$; the
  four-subspace dimensions of $B$ with its left null vector $(-1,-1,1)$; the change of
  basis and its swap with all three invariants; the least-squares fit
  $\hat{x} = (\tfrac32, 1)$ with residuals $(-0.5, 0.5, 0.5, -0.5)$, $A^{\mathsf{T}}r = 0$,
  $\|r\|^{2} = 1$, and $P$'s entries, trace $2$ and eigenvalues $\{1,1,0,0\}$; the
  rank-deficient Gram determinant $0$ against the projection $(3,3,3,3)$; seven steps of
  power iteration with their error ratios; $2.51$ and $113.97$ steps per digit at ratios
  $0.4$ and $0.98$, a factor of $45$; the symmetric discriminant $(a-d)^{2} + 4b^{2}$;
  the ellipse semi-axes $0.5774$ and $1$; the Hessian $2A$; the non-symmetric form
  identity; $A^{\mathsf{T}}A = \begin{bmatrix} 25 & 20 \\ 20 & 25 \end{bmatrix}$ with
  eigenvalues $45$ and $5$, singular values $3\sqrt5$ and $\sqrt5$, product $15 = |\det A|$
  and squared sum $50$ matching the sum of squared entries; and the ill-conditioned
  $M$ at $\kappa = 2.4495\times10^{4}$ with $\kappa(M^{\mathsf{T}}M) = 6.0000\times10^{8}$
  — the ratio to $\kappa^{2}$ being $1.0000000114$ — and its best rank-1 error equal to
  $\sigma_2$ to nine figures.

- **All 42 new derivation answers were truth-checked separately from the gate**, each
  against an expression written independently of the one in the catalogue — **42 of 42
  agree**.

**4. UX & Accessibility Hardener.** Content-side, as cycles 1, 4, 7, 10, 13 and 14
established. Checked rather than assumed over the whole draft: **no markdown table, no
raw HTML and no hard-coded colour was introduced**, all three verified mechanically. Every
figure is a fenced `text` block inside `overflow-x:auto`, which is cycle 4's rule for
staying safe at 375px. The fenced listings are prose figures rather than runnable
programs, so none makes a claim about its own output that a **▶ Run** button would be
needed to check.

### Found in my own work, and fixed

Every one of these was found by a mechanical sweep run *before* applying, and most are
defects this cycle was in the middle of repairing in somebody else's text.

- **Twenty of my own fragments would have shipped as raw markup**, in five classes, none
  of which the renderer supports: `\|` norm bars (thirteen), escaped set braces `\{ \}`
  (four), `\textbf`, `\Longleftrightarrow` and `\underbrace`. Every one falls back to
  `<code class="math-raw">` and puts LaTeX source on the page. Repaired to `||`,
  `\left\{`/`\right\}`, `\text`, `\Leftrightarrow` and a plain `\text{where}`, each
  candidate verified against the shipped renderer before use rather than assumed.
  **`\|` is the catalogue's own established habit** — 16 instances of `\|b`, 14 of `\|a`
  and more — and copying it would have added to the 1052 raw fragments rather than
  avoiding them.
- **My own harness reported 3 of 6 on its first self-test.** It checked whether
  `render()` returned `null`, and the shipped `render()` never returns null — on a parse
  failure it returns the *source* wrapped in `<code class="math-raw">`. So `\ `,
  `\overset` and `\begin{cases}` all scored "ok". Checking for the fallback class instead
  took it to 6 of 6 flagged with 0 false positives on 8 correct fragments. This is the
  third cycle running in which the harness had to be self-tested before it could be
  believed, and the first in which it was wrong in the *lenient* direction.
- **Four of my own inline fragments crossed a source line** — cycle 13's third defect
  class, discovered because I was auditing for it. Two in M6's derivation closing, two in
  M10's reading. Reflowed; one of the two was rewritten as display maths instead, because
  the fragment was too long to fit a line at all.
- **Two hedge words in prose I had just written against a brief that names them** —
  a `simply` in M4 and an `Of course` in M6. Found by diffing the draft against the hedge
  list rather than by reading.
- **My baseline said 269 readings; the true figure is 253.** `read` holds a bare **dict**
  rather than a list in 8 modules (7 in MA101, 1 in EE202), and `len()` on a dict counts
  its keys. This is cycle 14's `lab` finding recurring for a different key, in my own
  survey, and it would have made this entry claim the catalogue *lost* nine readings while
  seven were added. Checked whether it reaches anything shipped: **it does not** —
  `verify_derivations.py`, `verify_labs.py`, `spec.mjs`, `tune_stage.mjs` and
  `verify_circuit_model.mjs` all define an `as_list`/`asList` and none reads a unit key
  directly. The trap is laid for new measurement code, not for the app.
- **Two numbers in the M9 draft were written from memory and were wrong.** "$\approx 2.6$
  steps per digit" is $2.51$, and "a factor of forty" is $45.35$. Both caught by a second
  computation pass over the numbers that appear in the prose but had not been in the first
  run — which is the pass that exists because the first draft is where remembered numbers
  get in.
- **My own truth-check harness crashed on `lambda`**, which is a Python keyword — the
  exact failure `verify_derivations.py`'s docstring names as a reason answers fail. The
  shipped translator renames it to `lambda_`; the harness had to match.
- **My first payload-window check read the manifest's shape wrong** and threw. The
  generations file is a list of plain filename lists, not a list of objects with a `files`
  key. Corrected, the window is 3 generations, 65 files, **0 orphaned and 0 missing**.
- **I named a scratchpad script `numbers.py`**, which shadowed the standard library
  module `mpmath` imports, so SymPy failed to load with a circular-import error that
  pointed at SymPy rather than at me. Renamed.

### What changed

**Fourteen new units in seven modules** — one `read` and one `derive` each.

| Module | Reading | Words | Derivation | Steps |
|---|---|---|---|---|
| M4 | Which right-hand sides are reachable, and the count that is never two | 1473 | From one solution to the whole family, on a matrix small enough to check | 6 |
| M5 | Why every basis is the same size, and what the count is measuring | 1381 | Rank plus nullity, by turning one free variable on at a time | 6 |
| M6 | What the change-of-basis matrix actually holds, and the swap that survives every check | 1371 | Building the change-of-basis matrix instead of remembering it | 6 |
| M8 | The closest answer, and the hypothesis the projection formula needs | 1396 | The normal equations, one dot product at a time | 6 |
| M9 | Why the largest eigenvalue wins, and the case where nothing wins | 1288 | The ratio that decides how fast the largest eigenvalue takes over | 6 |
| M10 | Why symmetry forces real eigenvalues and right angles, and what the form can see | 1317 | Real roots from a sum of two squares | 6 |
| M11 | Every matrix diagonalised, and the number that says how many digits you keep | 1230 | Singular values out of A-transpose-A, and the ratio that prices the digits | 6 |

**9,456 new words**, every reading inside the 1200–2500 target and in line with M1–M3's
existing nine. MA121: 47 units → 61, 9 readings → 16, 9 derivations → 16, 55 derivation
steps → 97, **8 bare modules → 1**, and **4.27 units per module → 5.55**. Every reading
carries a worked example through to a checked number, names the mistake people make and
says why it is tempting, and closes on where the idea stops holding.

The derivations are deliberately **scalar** throughout — entries and coefficients, never
matrix identities. That is not a stylistic choice: `MathCheck` hands answers to SymPy with
commutative symbols, so `A(A^{\mathsf{T}}A)^{-1}A^{\mathsf{T}}` collapses to $1$ and a
step built on it would accept anything. Established by probing the shipped translator
before drafting, and it is the same failure mode as cycle 14's CTRL510 finding.

**Sixteen concepts bullets added or replaced** across the seven target modules and M7, so
the new material is reachable from the list a learner skims: the scalar-supply hypothesis
behind "never exactly two"; the dependence argument that makes dimension well defined, and
that rank plus nullity counts columns; what $S$ holds and that no similarity invariant
catches the swap; the independence hypothesis $P$ needs, that the projection survives
without it, and that residuals summing to zero comes from the intercept; the eigenbasis
reading of $A^{k}$, both power-iteration hypotheses with the $\pm5$ counterexample, and
the residual as the only real check; the Rayleigh statement of the quadratic form with the
factor of two corrected, and the symmetric-part blindness; the condition number as a worst
case; the Eckart–Young error as an exact equality; and the stability of singular values
against the instability of singular vectors. **The M7 power-iteration bullet, M9's
convergence bullet, M8's projection bullet, M6's conjugation bullet and M10's curvature
bullet were replaced** because each was false or incomplete as written; **every other
pre-existing bullet in these modules is untouched.**

**One pre-existing render defect repaired.** `$100 \times 100$` was broken across two
source lines in M3, so `MathML.inText`'s inline rule — `/(^|[^\\])\$([^$\n]+?)\$/`, whose
character class excludes a newline — never matched it and the page showed literal dollar
signs and LaTeX. Reflowed. MA121 is now **0 unpaired**, and the catalogue figure moves
$273 \to 271$ by exactly this.

### Left alone, deliberately

- **`power_method` was not fixed.** The defect above is real and it is in module 7's lab —
  code, with a reference solution the gate runs, which is not this track's ground. The
  repair is a residual check at the end of the routine plus a brief that says so, and it
  touches the lab's tests; that is a Track 3 or Track 6 cycle. Handed on with the three
  reproductions, the residuals, the cause (a swinging vector has a stationary Rayleigh
  quotient), the reason the capstone is safe, and the mislabelled overflow diagnostic, so
  the next cycle starts from the diff rather than the symptom. **The prose defect that
  pointed at it — the two bullets claiming unconditional convergence — is fixed here**, so
  a learner meeting the lab is now warned even though the lab is unchanged.
- **The 49 questions were audited and not changed at all** — no stem, no option, no key,
  and no `why`. They are Track 3's ground, and MA121's inherited answer-tell figure (22 of
  49) is cycle 3's recorded debt pinned by `quiz_budget.json`, not this cycle's to spend.
- **M1, M2, M3 and M7 were not given new units.** The first three are the densest modules
  in the course and are the model the rest has now been brought toward; M7 carries a lab.
  One bare module remains against eight, and it is M7.
- **`\hat`, `\bar` and `\varepsilon` are still dropped by `MathCheck.latexToPy`**, and
  `CTRL510/M4` step 1 still grades any answer that collapses to zero as correct. Re-swept
  the whole catalogue for the general case: **still exactly one casualty in 1290 steps**,
  and it is that one, unmoved since cycle 14 measured it. Not fixed here for cycle 14's
  reason — the repair is in `src/studio.js` and is a Track 2 machinery cycle.
- **A new member of that family was found and avoided rather than fixed:
  `\sigma_{\max}` translates to `s * i * g * m * a`.** The subscript pass strips `\max`,
  leaving `\sigma` with a dangling underscore, and the name then splits into single
  letters. A ratio $\sigma_{\max}/\sigma_{\min}$ therefore translates to the same soup
  over itself and self-checks as trivially true. **No existing answer in the catalogue is
  affected** — the sweep found none — so this is a hazard for future authors rather than a
  live defect, and M11's derivation writes `\sigma_1` and `\sigma_n` instead. Recorded
  with the reproduction so the Track 2 cycle that fixes `\hat` fixes this too.
- **1052 raw fragments, 127 swallowed and 271 unpaired remain catalogue-wide**, led by
  EE231 (376 raw), EE141, EE211 and EE111. MA121 is at zero in all three. These come from
  this cycle's independently written harness and agree closely with cycle 13's
  1053/139/273 and cycle 14's 1041/138/312, which is the strongest evidence yet that the
  three measurements are measuring the same thing.
- **`verify_derivations.py` still proves translation rather than truth**, as cycles 1, 7,
  13 and 14 established. All 42 new answers were therefore truth-checked separately, and
  the harness is in this session's scratchpad. Nothing about the gate was changed:
  rewriting the spec from inside a cycle it governs remains the wrong move.
- **`test_api.mjs` was failing before this cycle and is failing after it**, identically,
  with `ECONNREFUSED` on port 4180 — it needs a server this session did not start. It
  reads no catalogue file. Not repaired, because starting a server to make a gate pass is
  not the same as the gate passing.
- **EE241 (4 bare-and-lab-free modules of 10, and 0 readings against 18 derivations) and
  EE221 (3, and 0 readings against 30) are the next Track 1 targets**, and were not
  touched. Both are courses that derive heavily and explain nothing, which is a different
  shape from MA121's and probably wants a different remedy.

### Gates, after

Every pre-existing number unmoved. Three moved by exactly what was added — the
derivation-step count by the 42 new steps, and the two artifact sizes by the content.

```
verify_derivations   All good: 1290 steps across 46 courses   (1248 + 42 new;
                     MA121 55 -> 97)
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3260 per-option explanations · 6572 live draws —
                     unmoved.  MA121: 49 questions · longest-is-key 22 (budget 22) ·
                     margin +7.2 — unmoved, and no stem, option, key or why changed
verify_labs MA121    All good: 5 labs  (M1 8/8, M2 7/7, M3 7/7, M7 7/7, CAP 12/12)
verify_circuits      All good: 85 circuit exercises, 360 checks
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1475 analyses, 84 refusals · 15 plots
verify_desk          All good: 61 expressions at the extremes
verify_theme         All good: 135 contrast surfaces x 2 themes
verify_tune_ui       All good: 21 tune units · 423 hostile opening values · 462 targets
                     · 270 drags · 493 mounts
verify_progress      All good: 6 unload writes · 29 hostile documents · 7 merges
                     · 12 accessibility contracts
test_api             ECONNREFUSED :4180 — needs a live server, and failed identically
                     at baseline. Out of scope: reads no catalogue file.
emit.py MA121        ok — 11 modules, 4 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 12967 -> 13053 KB ·
                     inlined 14202 -> 14288 KB · shell 1207 KB — unchanged
catalogue            62 courses, 368 modules, 1915 -> 1929 units, 253 -> 260 readings
```

Beyond the gates: every MA121 math fragment pushed through the shipped `MathML.render` —
**3623 of 3623 draw, 0 raw, 0 swallowed, 0 unpaired**, against 2550 of 2550 with 2
unpaired at baseline, so 1073 fragments were added, none of them a defect, and the two
pre-existing ones were repaired; the catalogue-wide totals confirmed to have moved only by
MA121's share (raw 1052 unmoved, swallowed 127 unmoved, unpaired 273 → 271); all 42 new
derivation answers truth-checked against independently written expressions, 42 of 42;
every number in 9,456 new words computed in SymPy or NumPy before it was written, and a
second pass run over the numbers that reached the prose without being in the first; the 49
question stems, option sets, keys **and explanations** diffed against `HEAD` at **0
changes**; **14 lesson ids added and 0 lost**, so no completed work is orphaned; 0 hedge
words in the new prose, counted by sweep rather than by eye; no markdown table, hard-coded
colour or raw HTML introduced; the whole catalogue re-swept for answers containing a
silently-dropped command, finding the same single CTRL510 casualty and no new one; and the
payload window checked at 3 generations, 65 files, 0 orphaned, 0 missing.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 11729) was live
throughout, and this cycle is the process it launched — the claude process is pid 11799,
a child of 11729 — so the lock is this cycle's own and `emit.py` and `build.mjs` were safe
to run. The diff is `catalog/MA121.json`, `catalog/authors/MA121.py` and the `docs/` build
output, and nothing else.

## Cycle 21 — TRACK 2: Interactive Models & Visualisers

*(The runner labels this commit "cycle 2" — run D's counter, while this log keeps
counting. Run D's "cycle 1" is this file's cycle 20.)*

**Target: the schematic canvas's geometry and viewport — `paint()`, `contentBounds()`,
`zoomFit`, the grid, and the model coordinates all four of them read, in
`src/circuit.js`.** One subsystem, and the last piece of this track with no gate on it.
Cycle 2 took the sandbox half of the canvas work. Cycle 8 took the circuit editor's
**numerical** core and the analysis **plot**. Cycle 15 took the third slider surface,
`renderTune`. Cycle 6 took the editor's input, focus and lifetime, and says in its own
gate's header that "nothing here judges the drawing" — which was true of all four. So
the largest drawing surface in the app, carrying 386 published schematics and 85 graded
build exercises, had never been fed a hostile coordinate, resized mid-gesture, or driven
faster than it repaints. That is this track's brief almost word for word, and it was the
one surface nobody had pointed it at.

### Baseline, captured before any edit

```
85 circuit exercises / 360 checks · 564 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1290 derivation steps across 46 courses
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1475 analyses, 84 refusals,
     15 plots · 386 published schematics, 365 with a DC point
tune_ui 21 units · 423 hostile openings · 462 targets · 270 drags · 493 mounts
desk 61 expressions · theme 135 contrast surfaces · progress 29 hostile documents
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads, 13053 KB ·
       inlined 14288 KB · shell 1207 KB
```

### The attacks

**3. Simulation Auditor** — taken first, because this is its track and its brief. Every
number below was measured through the shipped editor before anything was changed.

- **One coordinate in a saved circuit freezes the tab, permanently, on the first press
  of Fit.** `paint()`'s grid ran `for (X = start; X < end; X += GRID)`, and a step is
  only a step while the numbers are small: above **2^58 = 2.882e17** adding 26 to a
  double does not change it, so X stops advancing and the condition stays true. That is
  world pixels; in cells it is **1.109e16**. `zoomFit` puts `view.px` at about 13 times
  the largest coordinate in the drawing, so the reachable threshold is a coordinate near
  2.2e16. Measured through the real editor: a wire ending at **x = 1e16 fits in 1 ms**,
  and **x = 1e17 had not returned when the run was killed at 25 seconds**. It is not a
  slow frame — the loop never takes a second step, there is no error, nothing to
  interrupt, and no way out but closing the page.
  **Reachable through a supported gesture, not through dev tools.** `sanitiseProgress`
  lists `build` among its slots and does `out[k] = plainObject(src[k])`, which
  shape-checks the *map* and passes every drawing inside it through **verbatim**;
  `importProgress` fills that map from a file the learner picks off disk. `renderBuild`
  reads `P.build[l.id]` straight into `createCircuit`'s `model`, and `createCircuit`
  deep-copied it with `JSON.parse(JSON.stringify(...))` and drew it. Import a progress
  file, open the exercise, press `0`.
- **A coordinate that came back from a save as a string splits the part in two, and the
  solver answers about the half that is not drawn.** `x - 1` coerces and `x + 1`
  concatenates. Measured: `Netlist.pinsOf` on a resistor saved with `x: "6"` returns
  **`[[5,4],["61",4]]`** — the left pin at cell 5, where it is drawn, and the right one
  at cell **61** where the drawing has one at 7. The resistor is painted where it was
  put and the netlist joins a node fifty-four cells away, so the circuit that is solved
  and graded is not the circuit on the screen, with nothing anywhere saying so. It
  cannot be picked up and put right either: driven through the real editor, an identical
  part with a numeric x **drags from 5 to 8** and the string one **does not move at
  all**, because the drawing coerces and the hit test does not.
- **The drawing repainted once per input event, not once per frame.** Measured: **60 pan
  moves inside one frame cost 61 full repaints**, **40 wheel notches cost 40**, and the
  `ResizeObserver` called `paint()` directly, so a window drag repainted per layout pass.
  One repaint at the 0.3 zoom floor on a 1200x800 canvas is **13478 `fillRect` calls**
  against 1236 at zoom 1. This file has had a `perFrame` coalescer since it was written
  and cycle 8 verified it for the solver; the drawing never went through it. Cycle 15
  found and fixed the same shape in `renderTune`.
- **`paint()` carried a second copy of `contentBounds()`.** The read-only branch — the
  one every question diagram is drawn by — recomputed the same bounds inline, differing
  only in its padding, so a fix applied to one of them reached half the canvases in the
  app and not the other half. Its scale also had a ceiling (1.6) and **no floor**, so a
  diagram whose span is large enough draws at a scale near zero: every part inside one
  pixel, an empty box, no error.
- **Checked and found sound, recorded so the next cycle does not re-derive them:**
  `zoomFit`'s centring is **correct at both ends of its clamp** — a first reading called
  it a bug because at spread 200 neither pin is on screen, and the algebra says
  otherwise: the drawing's centre is put on the viewport's centre whether the 0.3 floor
  bit or not, and both ends being off is what a drawing wider than the window looks like.
  It was checked symbolically and then at five spreads through the real transform, and
  **not** "fixed". Canvas sizing is sound at seven widths from 1600 down to 320, floored
  at 320x260 as intended, with the backing store and the CSS size agreeing. A resize in
  the middle of a drag moves the part by what the pointer did (5 → 7 across a narrowing
  from 900 to 375) and the canvas follows the new box. The `ResizeObserver` observes
  `.ckt-canvas`, whose height is settled by the flex chain rather than by its canvas
  child, so writing the backing store cannot feed back into it — read in
  `index.head.html`, the way cycles 2, 8 and 15 each checked their own canvas.
  The catalogue was swept rather than assumed: **386 drawings, 0 non-numeric or
  non-finite coordinates**, widest **EE121 at 27 x 8 cells**, tallest **EE121 at 14 x
  19**, **0** that the 0.3 zoom floor cannot fit and **0** that would draw below quarter
  scale — so none of the geometry defects above is reachable from published content, and
  all of them are reachable from a learner's own saved work.

**4. UX & Accessibility Hardener.**

- **The canvas's accessible name never changed.** Measured: `"Schematic canvas. Press
  Enter for the key map."` on an empty canvas and after parts were placed, identically.
  It is `role="application"`, which means a screen reader hands every key to this file
  and announces the name as the whole description of what the learner is working on. The
  status line announces each action as it happens, which serves somebody performing the
  actions and nobody who *arrives* — a learner returning to saved work, or tabbing back
  from the value box, had no way to ask what is on the drawing. Cycle 8 called the
  analysis plot "the only canvas left in the app with no accessible name" and gave it one
  built from what it drew; cycle 15 did the same for the tune plot. This is the one after
  those two, and the biggest.
- **"Fitted the drawing to the window" was said whether it had been or not** — by the
  key. The toolbar button said **nothing at all**, so the same action announced itself
  through one door and was silent through the other.

**1. Senior Educator** and **2. Assessment Inquisitor** have no prose and no graded
question in a viewport, so both were pointed at the thing in scope they can judge —
whether what the editor says **explains** or merely **announces**, the standard cycle 8
set with the solver's failure messages and cycle 15 carried into the tune refusal. The
fit announcement now reports the zoom it reached, which is the one thing the learner
cannot see, and when the floor bites it says *why* the canvas looks the way it does
rather than claiming a success: *"Fitted as far as the zoom goes, 30 per cent. The
drawing is wider than the window can show at that zoom, so this is the middle of it."*

### What changed

**`src/circuit.js` only.** No author file, no `catalog/*.json`, no lesson id, no schema.

| Fix | Before | After |
|---|---|---|
| a handed model | deep-copied and drawn, unvalidated | `sanitiseDrawing` — every cell a bounded number, or the part is not there |
| a coordinate of 1e17 | Fit froze the tab, no way out | dropped on load; Fit returns in 1 ms |
| `x: "6"` | pins at 5 and `"61"`, undraggable | pins at 5 and 7, drags |
| the grid | `X += GRID`, unbounded | counted, capped, and skipped below 5px spacing |
| a pan / wheel / band / resize | 61, 40, 50, 30 repaints a frame | **1** each |
| the read-only branch | its own copy of `contentBounds`, no scale floor | one bounds function, floor 0.08 |
| the canvas name | fixed, on `role="application"` | parts, wires, selection and zoom, rewritten only when they move |
| Fit | key lied, button silent | one sentence, reporting the zoom and saying when it could not fit |

**`sanitiseDrawing`, and where the bound came from.** `CELL_LIMIT` is **1e6 cells** — the
widest published drawing is 27 cells, counted, so it is four orders above anything real
and, at the viewport `zoomFit` can build from it, **1.11e10 times below** where the
arithmetic goes (worst reachable `|view.px|` + viewport width is 2.600e7 against
2.882e17). The rule `VALUE_CEIL` is set by, applied to geometry: reject the impossible,
do not police the unusual. A part whose cell cannot be recovered is **dropped, never
moved to the origin** — `Number(null)`, `Number(false)` and `Number('')` are all 0, so
the lazy version of this guard puts the part on top of whatever is already at the origin
and the netlist joins them: a wrong circuit that looks like a right one, which is the
defect the string case had already produced. A part that is gone is visible. Block ports
and nested `inner` drawings go through the same rule, bounded by `DRAW_DEPTH = 8` —
the number `Netlist.flatten` already stops at, rather than a second opinion about
nesting. `value` goes through the existing `clampValue`, so a saved capacitance of 1e308
lands on `VALUE_CEIL.C` instead of reaching the stamp.

**Order matters, and it is written down.** The sanitiser runs **before** the JSON deep
copy and on the raw object, because `JSON.stringify` turns `NaN` into `null` and `null`
is a value `Number()` reads as **zero** — copying first would convert "this part has no
position" into "this part is at the origin" before anything could reject it.

**A new gate — `tools/verify_circuit_view.mjs`.** Eight sections, driving the shipped
`createCircuit` rather than a copy of it: 26 hostile coordinate shapes recovered or
dropped and never moved to the origin, with ports, nesting and non-geometry fields held;
the whole catalogue required to pass through the guard **unchanged**; the arithmetic
threshold asserted against `CELL_LIMIT` and seven drawings at and past it required to
return on a clock; 14 mounts at seven widths in both modes plus a drag across a resize;
150 gestures inside one frame required to be one repaint each, and a repaint queued
before `dispose()` required not to run; the canvas required to name what it drew, to
follow the zoom, and **not** to rewrite the name when nothing moved; Fit required to
report the empty, the fitting and the too-wide case differently and to centre at five
spreads; and all 386 published schematics painted and required to land inside their own
canvas **at the transform `paint()` actually set**, spied off the context rather than
recomputed — a gate that rebuilds the arithmetic it is checking passes exactly when its
copy and the original are wrong the same way.

It brings a **ResizeObserver the gate can fire**. The two older editor gates pass
`undefined` for it, so the resize path — the one this track's brief names outright — had
never been driven by anything. A browser does not repaint a canvas because its box moved;
it calls this.

### Verification beyond the gates

**The gate was not trusted until it had been seen to fail: 16 mutations, and the
unmodified tree as a control. 15 rejected.** The sanitiser bypassed; `cellOf` trusting
bare `Number()`; the size bound dropped; `CELL_LIMIT` raised past the arithmetic; a
part with no position placed at the origin; wires no longer checked; the pan repainting
per event; the coalescer made a pass-through; the resize observer repainting per
callback; the canvas name suppressed; the name written on every frame; Fit claiming a fit
it did not have; Fit no longer centring; the read-only branch no longer fitting; and the
`rot` normalisation restored on content that is already right.

**The sixteenth passed, it was labelled in the mutation table as expected to pass before
the run, and the reason is a measured number rather than a shrug.** Putting the grid loop
back to `X += GRID` while leaving `CELL_LIMIT` in place is caught by nothing, because
with the coordinates bounded the walked loop **cannot** hang: the worst viewport
`zoomFit` can construct is 2.600e7 against a threshold of 2.882e17, a margin of 1.11e10.
The two guards are independent, and removing *either* one on its own is caught — the
raised limit by the arithmetic assertion, the removed limit by the trust section. What
the gate cannot distinguish is redundancy, and that is the honest description of it.

**Two weaknesses were found in the gate by running it, and repaired before the mutation
pass.** Its resize section proved nothing, because the stub had no `ResizeObserver` and
the canvas simply kept the size from its first paint — the "at 1600x900 the canvas is
900" failures were the gate's, not the editor's. And its catalogue section recomputed
paint()'s transform instead of reading it, which is a gate marking its own homework.

**One defect was found in my own work by the gate, on its first run.** The sanitiser
added `rot: 0` to every part that did not carry one — **1081 parts across the 386
published drawings**, classified by diff rather than eyeballed. `turnsOf` already reads a
missing `rot` as zero, so it bought no behaviour at all, and it would have been written
back into the learner's save on the next edit. A guard is measured by what it does to
what is already right, and the right answer there is nothing. Now: **386 of 386
byte-identical through the guard.**

Every defect above was measured before it was fixed and re-measured after: the 25-second
non-return, the `[[5,4],["61",4]]`, the part that would not drag, the 61 / 40 / 50 / 30
repaints against 1 each, and the static canvas name. The 13478 `fillRect` at the zoom
floor was re-measured too and is **unchanged** — the density cut-off does not bite at 0.3,
where the dots are 7.8px apart, and the comment saying so was corrected when the numbers
came back, because the first draft claimed a saving that does not happen. What made that
number stop mattering is the coalescer.

### Left alone, deliberately

- **`sanitiseProgress` still passes every saved drawing through verbatim**, and that is
  the door all of this came through. It was closed in `createCircuit` instead, on
  purpose: the editor sanitising its own input closes **all three** doors at once — the
  build exercise, the Playground's `circuit.json`, and a question's authored diagram —
  where a fix in the store closes one. It is also the architecture the other two
  renderers already have, cycle 2's clamped `initial` and cycle 15's clamped saved
  slider. The store is Track 6's ground and has its own gate; recorded with the exact
  line (`out[k] = plainObject(src[k])`) so the next cycle there starts from it.
- **The zoom floor was not lowered so that Fit could always fit.** `zoomTo` clamps to
  [0.3, 4] and a second, lower range only for Fit would make `+` and `-` jump afterwards.
  No published drawing reaches the floor — 0 of 386, measured — so the honest
  announcement is the whole of what was owed here.
- **`P.dim` at 2.93:1 and `P.faint` at 1.86:1 on every canvas.** Cycle 2 measured them
  and handed them to Track 5; cycles 5, 6, 8 and 15 each re-recorded them without taking
  them. This cycle adds nothing new to the list and takes it no further, for the reason
  that has held every time: changing them changes the visual weight of 13 visualisers and
  three more canvases, which is a decision about the design language.
- **The MCU sketch panel is still unaudited**, as cycles 6, 8 and 15 each left it.
  Nothing here reaches it: `paintMcu` draws a part body through the same transform, and
  the sanitiser bounds the cell that body is drawn at, which is a fix it receives rather
  than a change made to it.
- **`plotKey` is still vestigial on EE111 M7 and M10** — cycle 15's note, unchanged,
  because removing the field still means re-emitting the course for no behaviour.
- **`sliding-mode` still keeps forward Euler.** Cycle 2's finding, still deliberate.
- **No `emit.py` run, and no author file, `catalog/*.json`, lesson id or schema touched.**
  The staleness guard is not armed, and the payload total is **unchanged at 13053 KB**,
  which is the mechanical confirmation that no content moved. `git status` reports **0
  changes under `catalog/` and 0 under `docs/programs`**, checked rather than assumed.

### Gates, after

Every pre-existing number unmoved. The only new numbers are the new gate's; the only two
that moved are the artifact sizes, by exactly the source that was added.

```
verify_circuit_view  All good: 26 hostile coordinates held off the drawing · 386 published
                     drawings unchanged by the guard · 7 drawings at and past the
                     arithmetic return, the grid step asserted against 2.882e+17 · 420
                     mounts at 7 widths in both modes · 150 gestures, one repaint a
                     frame · the canvas names what it drew · 386 schematics inside
                     their own box                                              [NEW]
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1475 analyses, 84 refusals · 15 plots · 386 published
                     schematics, 365 with a DC point, all three analyses
verify_circuits      All good: 85 circuit exercises, 360 checks · 564 labels
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_tune_ui       All good: 21 tune units · 423 hostile opening values · 462 targets
                     · 105 paints · 270 drags · 493 mounts
verify_derivations   All good: 1290 steps across 46 courses
verify_desk          All good: 61 expressions at the extremes
verify_theme         All good: 135 contrast surfaces x 2 themes
verify_progress      All good: 6 unload writes · 29 hostile documents · 7 merges
                     · 12 accessibility contracts
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 13053 KB — unchanged ·
                     inlined 14288 -> 14301 KB · shell 1207 -> 1220 KB, of 1536
```

The pre-existing gates were compared on the figures they report, which are reproduced
above against the baseline block at the top of this entry and match it line for line; a
byte-level diff of their output was not run, and that is stated rather than implied.

Beyond the gates: **16 mutations the new gate was run against and one clean control**,
15 rejected and the 16th predicted, labelled and explained with the margin that makes it
redundant; two weaknesses found in the gate by running it and repaired before that pass;
the `rot: 0` regression found by the gate in my own work and classified by diff across
1081 parts; the catalogue swept for coordinate shapes, drawing spans and fit scales
before any bound was chosen; and the payload window checked at 66 files on disk with 0
changes under `docs/programs`.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 11729) was live
throughout and this cycle is the process it launched, so `build.mjs` was safe to run. The
diff is `src/circuit.js`, the new `tools/verify_circuit_view.mjs`, and the `docs/` build
output, and nothing else.

---

## Cycle 22 — TRACK 3: Question Bank & Quizzes

*(The runner labels this commit "cycle 3" — run D's counter, while this log keeps
counting. Run D's cycle 1 was this file's cycle 20 and its cycle 2 was cycle 21.)*

**Target: CS310 (Theory of Computation & Automata) — its 25 quiz questions — and the
`whys` field itself, across all 47 courses that carry a bank.** One course and one
mechanism. This is cycle 16's shape and it pays cycle 16's own recorded debt: it named
CS310 at 84% as the largest remaining block of the answer tell after CS301 left the list,
and it is the course cycle 3 and cycle 9 both left standing.

Chosen on measurement, and the measurement is in the survey below rather than in taste.

*The largest remaining block of the answer tell.* CS310 scores **21 of 25 on "read
nothing, pick the longest option"** — 84%, against 25% for guessing — with a mean length
margin of **+26.4 characters**. RFIC510 is nominally worse at 9 of 10, but that is ten
questions; CS310 is 25 questions and 100 options, and it is the biggest single bank still
answerable without reading it.

*Nothing explained the wrong answer.* **0 per-option explanations across 25 questions and
100 options.** The rest of the course does not have this problem — all 21 of its blanks
holes carry `whys` — so the quiz was the one graded surface in CS310 that answered the
same paragraph whichever option was pressed.

*And the field that fixes it was pinned by nothing.* 3260 per-option explanations existed
across the catalogue and **not one gate would have noticed a course losing every one of
them.** `whys` is optional; the structure rules only fire when it is present. That is the
machinery half, and it is why this cycle is not simply cycle 16 run again on a second
course.

### Baseline, captured before any edit

```
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3260 per-option explanations (260 quiz, 3000 blanks) · 6572 live draws
     quiz view: 1260 mounts, 5464 options pressed · top slot 24.0% vs 38.8% authored
     blanks: 4384 options picked · top slot 24.5% vs 66.6% before the shuffle
CS310: 25 questions in 5 quiz units · 21 blanks holes · 2 numeric · 6 labs
       longest-is-key 21/25 (84%) · shortest 2 · margin +26.4 · quiz whys 0/100
       blanks whys 84 · 3670 words of question text and feedback
85 circuit exercises / 360 checks · 21 tune units · 216 numeric answers, 0 unchecked
1290 derivation steps across 46 courses
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui 78 driven keys · circuit_model 1475 analyses, 84 refusals · 386 schematics
tune_ui 423 hostile openings · desk 61 expressions · theme 135 contrast surfaces
progress 29 hostile documents
build: 3 parts / 111 keys · 32/32 + 30/30 · 62 payloads, 13053 KB ·
       inlined 14301 KB · shell 1220 KB
```

### The attacks

**2. Assessment Inquisitor** — taken first, because this is its track. Beyond the three
numbers above, four failure modes in the options themselves, all of the kind cycle 16
catalogued in CS301 and all of which had survived here untouched:

- **Options an informed learner eliminates without knowing the subject.** `M1/Q1` offered
  *"Exactly one state is accepting"* against a stem about `delta`; `M4/Q1` offered
  *"Because no regular expression is allowed to use exponents"* and *"Because a DFA is
  allowed only one accepting state"*, neither of which anybody believes. Each silently
  turned a four-way question into a two- or three-way one.
- **A distractor that is plainly false rather than tempting.** `M2/Q5` offered *"no
  machine has ever been found needing more than `n`"* — an appeal to absence that no
  learner holds. The belief people actually hold is that the blow-up is theoretical and
  the reachable part is polynomial in practice, and that is now the option.
- **A near-miss nobody had written down.** `M1/Q1` had no option for **at most one** arrow
  per state and symbol — the partial DFA — which is *the* thing the totality requirement
  is about and the source of the empty subset two modules later. The question tested
  whether you could spot the word `delta` rather than whether you knew what totality buys.
- **The key doing the teaching.** In 21 of 25 the key was the only option carrying its own
  justification, which is what produces both the length margin and the silence about the
  other three. The repair is the same one in both directions: move the justification out
  of the key and into feedback addressed to whoever pressed each option.

**1. Senior Educator.** CS310's shared `why` paragraphs already derive rather than assert
and already walk all four options — the standard cycle 3 set, and this course met it. What
this persona found is the asymmetry: a learner who pressed the fourth option reads a
paragraph written for whoever pressed the second and has to find the clause that is about
them. And the prose named *that* an option was wrong far more often than it named **why
anyone believes it**, which is the half that produces teaching rather than marking. All
100 new explanations are written to that second standard; the ones that took the most work
are listed under *What changed*.

**3. Simulation Auditor.** No sandbox, tune or schematic in this course, so it was pointed
at the only thing here it can still falsify: every code and behaviour claim in the bank,
against the labs shipped beside them. **Every claim was re-derived by running the course's
own reference solutions, not by re-reading the sentence that states it** —
`minimise()` on the three-state machine (`reachable()` returns `{s, t}`, two states out,
and refinement without pruning leaves **3 blocks**); `ABB.epsilon_closure({0, 3}) ==
{0, 3}`; the subset construction on `ABB` giving **exactly four subsets — `{0}`, `{0,1}`,
`{0,2}`, `{0,3}` — none of them empty**, with `abb` landing in `{0,3}` and accepted while
`0` is not accepting; the `k`-th-symbol-from-the-end family determinising to **4, 8 and 16
reachable subsets at k = 2, 3, 4**; `parse("ab|c*")` returning `("alt", ("cat", …),
("star", …))` and **all four readings in `M3/Q1` enumerated to four letters and confirmed
to be four different languages**; `parse("a|") == ("alt", ("char","a"), ("eps",))` matching
`a` and the empty word and **not `aa`**, where `a*` does — which is what makes the
inserted-`*` distractor refutable by one word; `thompson` costing **4 states for `ab`, 6
for `a|b`, 4 for `a*`**, so concatenation demonstrably allocates none; `detect_loop` on the
right-then-left machine returning **2** and on `RIGHTWARD` returning **`None`**; and
`run(RIGHTWARD, "", 50)` reporting `halted` False with `steps` 50 against a rule-less
machine halting at **step 0, not accepted**.

It also **refuted one option I had drafted before it was written down**, which is recorded
below because the near-miss was the good part.

**4. UX & Accessibility Hardener.** This surface was hardened by cycle 3 and put under a
gate by cycle 16 — focus onto the explanation when the pressed button is disabled,
`role="status"` on the result region, `role="group"` and `aria-labelledby` on the options,
`data-ai` carrying the authored index. All of it still holds and all of it is still driven:
**1260 mounts and 5464 options pressed**, unchanged. What this persona found instead is
that the *content* of what a screen reader announces was empty for 100 of those presses,
because CS310 authored no `whys` and the renderer therefore drew no `.ex-picked` block at
all. That is a content defect wearing an accessibility cost, and it is fixed by the same
100 strings.

### The near-miss the recompute killed before it shipped

`M1/Q5` asks why walking two DFAs in lock-step is correct *and* terminating. The distractor
I drafted was *"it tries every word up to `|Q1| + |Q2|` letters, and a difference always
shows up by then"*, on the assumption that the real bound is the **product** `|Q1| * |Q2|`
and that the sum is the misconception.

The sum is right. Two inequivalent DFAs are separated by a word shorter than
`|Q1| + |Q2|` — Moore's theorem applied to their disjoint union, where two distinguishable
states of a `k`-state machine are distinguishable by a word of length at most `k - 2`. A
distractor whose stated fact is true and whose feedback calls it false would have taught
the opposite of the truth, and it would have passed every gate in this repository, because
no gate can mark a quiz.

It is kept, reworded, and it is now the better question: the bound is real, and it is still
not why *this* procedure works — the walk never counts letters and has no depth limit in
it. A true fact attached to the wrong mechanism, with the fact affirmed in its feedback
rather than denied. **This is the second cycle running in which the interesting finding was
a claim that survived drafting because it sounded like a misconception.**

### The field that 3260 explanations were resting on

`verify_quiz.mjs` has enforced four structure rules on `whys` since cycle 3 — one entry per
option, none empty, no positional reference, no undrawable markup — and **every one of them
only fires when `whys` is present**. Delete the field and the gate says `All good`. So the
3000 blanks explanations cycle 9 wrote and the 260 quiz explanations cycles 3 and 16 wrote
were held in place by nothing but the fact that nobody had removed them.

**Two additions, and they ratchet in opposite directions.**

**A coverage floor.** `quiz_budget.json` now carries `whys` beside `longest` and
`shortest`, per course and per bank, and the gate fails when the count **falls**. The
length tell is a debt that must not grow, so it is a ceiling; per-option feedback is work
done, so it is a floor. A course with no floor recorded fails and is told the number to
write, exactly as the missing `blanks` entry already does — because a bank with no recorded
coverage is a bank that can shed it unwatched. **47 courses, floors set from what is on
disk today: 360 quiz and 3000 blanks.**

**A duplicate rule.** Counting entries is satisfied by pasting one paragraph four times,
which is precisely the undifferentiated feedback the field exists to replace — a `why` with
no `whys` beside it already does that, for free. So two per-option explanations in the same
question or hole that read the same are now a hard failure, no budget. **Measured before it
was written: 0 of 1366 questions and 0 of 1103 holes offend**, so it refuses a new defect
rather than condemning existing content, which is the rule four previous cycles have each
had to learn. It uses the existing `norm` and is deliberately **not** case-folded, for the
MA201 reason recorded above that function.

One thing it deliberately does not flag: **677 blanks holes whose `whys` entry for the key
repeats the shared `why` verbatim.** Every one of the 677 is at the key and none at a wrong
option, checked rather than assumed — that is the authoring convention, not a defect, and a
rule that condemned it would have failed ten courses on its first run.

### What changed

**Content — all 25 questions rewritten, 100 per-option explanations written.**

| | before | after |
|---|---|---|
| questions | 25 | 25 |
| "pick the longest option" | 21 / 25 — **84%** | 0 / 25 — **0%** |
| "pick the shortest option" | 2 | **0** |
| mean length margin | +26.4 chars | **−4.3 chars** |
| per-option explanations | 0 | **100** |
| words of question text and feedback | 3670 | **9383** |

The length tell was removed by moving the justification into the feedback, not by trimming
the key until it was shortest — the ratchet refuses that inversion just as hard, and the
pre-flight caught it happening three times: `M1/Q3`, `M2/Q1` and `M4/Q3` each passed
through a draft where the key had become the shortest option, and were rebalanced by giving
a distractor the weight it deserved rather than by cutting further.

Every distractor is now a misconception with a name. The ones worth recording, because they
took the most work to find: ***at most one* arrow per state and symbol** — the partial DFA,
which does remove all choice and leaves runs with no verdict, and whose usual repair is the
dead state the next module builds on purpose; *"`u` and `v` are both in the language, or
both outside it"* — Myhill-Nerode with `z` fixed at the empty word, refuted in four
characters by `0` and `1` under *ends in `01`*; *"one of `u` and `v` is a suffix of the
other"*, which is the right instinct for that language generalised one step too far and is
not even an equivalence relation — `1` is a suffix of both `01` and `11`, and neither of
those is a suffix of the other; *"when two states in it disagree about acceptance, checked
again each round"*, the seed of the partition offered as its rule, a check that can never
fire; *"it is purely a speed optimisation — the state count comes out the same either
way"*, which is the reading the algorithm's correctness depends on being false and which
the three-state machine refutes by returning 3 instead of 2; *"the run the simulation
actually follows"*, which imagines a machine that guesses once where the implementation
never guesses at all; *"at most `n^2`, since a subset is fixed by its smallest and largest
member"* — a bound for a different data structure, and one that is real and nearby, since
`n^2` **is** the bound for the product construction of the previous module; *"because this
notation has no backreferences, and backreferences are what make matching slow"*, true
about a different problem, refuted by `(a?){20}a{20}` which uses none; *"regular expressions
and finite automata describe exactly the same languages"* and *"every regular expression
denotes a language some **deterministic** finite automaton accepts"* — both **true**, and
neither the direction one construction proves; *"because it has no regular expression, and
Kleene's theorem then rules out an automaton"*, which offers the conclusion as its own
premise; *"a parser that also returns the trees, since the count is built out of them"* —
sums keep no record of what was added, which is exactly why `count_parses` stays polynomial
while counting exponentially many trees; *"each cell holds one count per nonterminal, and
there are `n` nonterminals"*, conflating `|G|` with `n`; *"because a run that used up its
whole budget has halted — it did stop, after all"*, the conflation the two fields exist to
prevent; *"it answers only for machines that halt"*, sound and complete with the classes
the wrong way round; and *"because deciding would mean simulating, and a simulation cannot
outrun the machine it simulates"* — the commonest wrong answer to the halting problem,
correct about one method and silent about all the others, which is exactly the gap the
diagonal argument closes without examining any method at all.

**Machinery — `tools/verify_quiz.mjs`.** The coverage floor and the duplicate rule above,
plus both reported per bank on every course line so the numbers are visible rather than
merely enforced. The header now documents coverage as a third kind of check alongside
structure and exploitability.

**Machinery — `tools/quiz_budget.json`.** `whys` floors for all 47 courses, and CS310's
length entries lowered from 21 / 2 to **0 / 0** so the improvement cannot be given back.

### Verification beyond the gates

**The gate was not trusted until it had been seen to fail. 16 mutations, 16 intended
verdicts, two of them required passes, and all 16 produced the verdict they had to:** two
per-option explanations in a question made identical; the same in a blanks hole; identical
but for whitespace, to prove `norm` is folding; the `whys` list dropped from one question,
and from one hole, so coverage falls below the floor; the floor removed from the budget,
and the blanks floor removed separately; one explanation emptied to whitespace; a list one
entry short; a positional reference planted in an explanation; the length tell reintroduced
by lengthening every key; the tell **inverted** by lengthening every distractor, which the
`shortest` ceiling is what catches; a duplicated option so the key has an unmarkable twin;
a bullet list in an explanation the renderer cannot draw; **"the final answer" planted in an
explanation, which must pass** — cycle 9's narrowing, re-checked; and the unmodified tree as
a control.

**Every number in the new prose was recomputed against the labs' own reference solutions**,
listed under the Simulation Auditor above — the refinement block count, the four subsets,
the 4/8/16 blow-up, the four `M3/Q1` readings enumerated to four letters, the `a|` language
including its refutation by `aa`, the three Thompson state counts, and the four Turing
machine runs. One drafted distractor was refuted by that pass before it shipped.

**CS310's quiz was swept for the three failure modes this repository has already shipped:**
0 strings with an unpaired `$`, 0 with a backslash before a quote (cycle 3's raw-string
leak), 0 carrying block markup the renderer cannot draw (cycle 7's raw markup) — measured
after the rewrite, all three at zero. All 125 new strings were swept for references that
point the wrong way down the page, which is cycle 16's finding; **three hits, all read, all
ordinary prose** — "one level below `parse_cat`", "a count above one", "can still halt later
on".

**The artifact was proved to be what the source says.** Everything outside `quiz` is
identical to HEAD except the two `"check": ""` fields discussed below, **all 20 lesson units
unchanged**, and the JSON is byte-identical before and after a re-emit — which also proves
the mutation pass restored the tree it borrowed. The payload window was checked rather than
assumed: **3 generations naming 64 files, 64 on disk, 0 orphaned, 0 missing.**

### Found in my own work, and fixed

- **A distractor whose "misconception" was a theorem.** The `|Q1| + |Q2|` bound in `M1/Q5`,
  above. Found by checking a fact I was about to call false, which is the only way this
  class of error is ever found — the drafted feedback would have read as confidently as the
  rest.
- **Three keys trimmed into being the shortest option.** `M1/Q3`, `M2/Q1` and `M4/Q3`. The
  first draft removed the length tell by cutting the key, which inverts the defect rather
  than removing it; the pre-flight measured `shortest-is-key` alongside `longest` and caught
  all three. Rebalanced by lengthening a distractor, never by padding the key.
- **`RIGHTWARD` described as "three symbols long".** Inherited prose, ambiguous between the
  machine's description and its single transition. It is **one rule**, and it now says so —
  checked against the definition in the lab rather than against the sentence.
- **A `run()` claim I could not have made from the sentence I wrote it in.** The feedback
  for the tape-cells distractor asserts that `steps` and `head` agree for `RIGHTWARD` only
  because that machine happens to move right every step; both were read off an actual run
  (`steps` 50, `head` 50) rather than asserted.

### Left alone, deliberately

- **23 courses are still over 50% on the quiz length tell**, down from 24 — CS310 is the one
  that left the list. The catalogue moves from **624/1366 (46%) to 603/1366 (44%)**, CS310's
  21 and nothing else. RFIC510 9/10; DSP520, DSP530, EMAG530 and VLSI530 8/10; CS330
  20/26; CS102 and CS210 17/24; CTRL520 and CTRL530 7/10. Cycle 3's main recorded debt,
  one course smaller, and every course still pinned in `quiz_budget.json` so it cannot
  grow while it waits.
- **21 courses still author every key at index 0**, covering 264 questions. Unchanged, and
  not a defect while the shuffle runs — which cycle 16's quiz-view section presses every
  option of every question to prove, on every run.
- **CS310 authors no key at index 0 at all** — the spread is 0 / 9 / 8 / 8, and it was left
  exactly as it was. It is the mirror of the debt above and equally invisible to a learner:
  the gate measures the **drawn** slot and reports CS310's key on top 20% of the time. Moving
  `opts` and `whys` together for no learner-visible effect is churn, and the shuffle is the
  thing under gate.
- **347 blanks holes in ten courses still have no per-option feedback** — EE102 102, EE121
  93, EE101 87, MA111 20, MA121 17, EE241 11, EE221 / MA112 / MA201 5 each, EE202 2. Cycle
  9's debt, unmoved. It is now **pinned at its current value in 47 courses' floors**, which
  is the part of it this cycle could pay without becoming a cycle that touches everything.
- **Two candidate answer tells were measured and deliberately not made into gates.** The
  *stem-overlap* strategy — pick the option sharing the most distinctive words with the stem
  — scores **113/1366 (8%)** against 39 for its mirror, which is no exploit worth a rule. The
  *absolute-qualifier* strategy — eliminate options carrying always/never/only/every — is
  live at **347/1366 (25%)**, and it was still rejected: **CS301, the bank cycle 16 rebuilt
  question by question, scores 40% on it, exactly as CS310 does.** A measure that condemns
  the catalogue's most carefully written bank is measuring good writing, since a wrong claim
  about computation usually *is* an overgeneralisation. Recorded with the numbers so the next
  cycle does not re-derive them and does not ship the gate.
- **The six MathML-ambiguous option pairs** in EE111, EE141, EE201, EMAG530, MA112 and
  PWR510 — cycle 16's note, unchanged. Correct in a browser, correct to a screen reader that
  parses MathML, and a flattening artefact of the gate rather than a content defect.
- **`.quiz-q .qt code` still takes its colour from `--lime` rather than `--code-ink`, and
  `P.dim` (2.93:1) and `P.faint` (1.86:1) still fail contrast on every canvas.** Cycles 2,
  3, 5, 6, 8, 9, 15, 16 and 21 have each recorded these. Track 5.
- **The emitter adds `"check": ""` to CS310's two numeric units, and it was kept.** Cycle 16
  met and documented exactly this on CS301: 194 units across the catalogue already carry an
  empty `check` on disk, so re-emitting brings the artifact into line rather than away from
  it. It is not the `emit.py --all` drift cycles 4 and 9 reverted. `verify_numeric` is
  unmoved at 216 answers, 0 schematics with no check, 218 figure-only.
- **The retained window holds two CS310 payloads.** Capturing the baseline means running
  `build.mjs` before editing, so the baseline build's payload is one generation back. Both
  are named by a generation and both are present — 3 generations, 64 named, 64 on disk, 0
  orphaned, 0 missing — and two older EE121 and EE241 payloads aged out normally in the same
  run, which is the window working rather than anything this cycle did.

### Gates, after

Every pre-existing number unmoved. The numbers that moved are the per-option explanation
count — by exactly the 100 written — CS310's budget entry, and the two artifact sizes.

```
verify_quiz          All good: 1366 questions in 252 quiz units and 1103 holes in 217
                     blanks units · 3360 per-option explanations (3260 -> 3360, +100)
                     · quiz view: 1260 mounts, 5464 options pressed and the explanation
                     read back, the answer drawn in the top slot 24.0% against 38.8%
                     as authored · blanks: 6572 draws, 4384 options, 24.5% — unmoved
                     · every bank within its answer-tell budget and above its whys
                     floor                                     [COVERAGE FLOOR NEW]
                     CS310: 25 questions · longest-is-key 0 (budget 0) · shortest 0
                     (budget 0) · whys 100 (floor 100) · mean length margin -4.3
verify_labs CS310    All good: 6 labs
emit.py CS310        ok — 5 modules, 5 labs, capstone +tests
verify_derivations   All good: 1290 steps across 46 courses
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_circuits      All good: 85 circuit exercises, 360 checks · 564 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_theme         All good: 135 contrast surfaces x 2 themes
verify_desk          All good: 61 expressions at the extremes
verify_circuit_ui    All good: 78 driven keys and gestures, 10 things said
verify_circuit_model All good: 1475 analyses, 84 refusals · 15 plots
verify_tune_ui       All good: 21 tune units, 423 hostile opening values, 462 targets,
                     105 paints, 270 drags, 493 mounts
verify_circuit_view  All good: 26 hostile coordinates · 386 published drawings
                     unchanged by the guard · 420 mounts at 7 widths · 150 gestures
verify_progress      All good: 6 unload writes · 29 hostile documents · 7 merges
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 13053 -> 13086 KB ·
                     inlined 14301 -> 14334 KB · shell 1220 KB — unchanged, of 1536
```

The pre-existing gates were compared on the figures they report, which are reproduced above
against the baseline block at the top of this entry and match it line for line; a byte-level
diff of their output was not run, and that is stated rather than implied.

Beyond the gates: **16 mutations, every one producing the verdict it had to, including two
the gate was required to pass**; every number in the new prose recomputed by running the
course's own reference solutions, which is how one drafted distractor was found to be a
theorem; three keys caught mid-draft having become the shortest option; CS310's quiz swept
for unpaired `$`, escaped quotes and undrawable markup at 0, 0 and 0; all 125 new strings
swept for references that point the wrong way down the page, three hits, all read, all
ordinary prose; the artifact proved byte-identical across a re-emit and identical to HEAD
outside `quiz` but for the two known `check` fields, with all 20 lesson units unchanged; and
the payload window checked at 3 generations, 64 files, 0 orphaned, 0 missing.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 11729) was live
throughout and this cycle is the process it launched, so `build.mjs` was safe to run. The
diff is `catalog/authors/CS310.py`, `catalog/CS310.json`, `tools/verify_quiz.mjs`,
`tools/quiz_budget.json` and the `docs/` build output, and nothing else. No lesson id, no
other course's content, no renderer, and no unit kind other than `quiz` was touched.

---

## Cycle 23 — TRACK 4: Subject Breadth & Progression

*(The runner labels this commit "cycle 4" — run D's counter, while this log keeps
counting. Run D's cycle 1 was this file's cycle 20, and its cycle 3 was cycle 22.)*

**Target: EE221 (Measurement and Instrumentation).** One course, and the missing *topic*
cycle 17 named as the largest this track had found: *"not one module in the catalogue is
titled for an op-amp … That is a missing topic rather than missing practice, it is the
largest single one this track has found, and the device to teach it with is already
modelled."* Nothing had picked it up.

Re-measured before starting rather than taking the handed-over number. At HEAD the
catalogue mentioned an operational amplifier **19 times across 7 courses**, **no module
anywhere was titled for one**, and `OPAMP` was drawn in **0 of 386 published schematics**
— while `src/circuit.js` has carried a finite-gain op-amp with `tanh` rails and a 75 Ω
output resistance since cycle 0, and `emit.py`'s `MATCH_SYMBOLS` has carried `OPAMP` long
enough for EE221's own symbol drill to draw one.

EE221 is where that costs most, and the reason is that **every one of those 19 mentions
is the op-amp being offered as the answer to a problem the course has just posed.**

```
  EE101 M4   "or buffer the tap, with a unity-gain op-amp whose input draws nanoamps"
  EE101 M9   "an op-amp output behaves like a few milliohms because feedback holds it"
  EE102 M5   "put a buffer between the stages — an op-amp wired as a follower"
  EE102 M8   "or with an op-amp made to imitate an inductor. Both are outside this course"
  EE121 M1   "follow the network with an amplifier that draws no input current, which is
              one of the things an operational amplifier is for"
  EE211 M1   "a real integrator built from an op-amp does not run off to infinity"
  EE211 M3   "a filter anyone can build out of one op-amp and six passives"
  EE231 M2   "which is why op-amp buffers appear between passive stages"
  EE221 M4   "here it is the buffer between the divider chain and the converter"
  EE221 M7   "a one-op-amp difference amplifier rejects common mode only as well as its
              two resistor ratios match — 0.1% resistors cap it near 66 dB"
```

Ten sites, nine courses' worth of problems, one device, and no derivation of it anywhere.
EE221 is the course where the debt compounds rather than merely appears: its **only
declared prerequisite is EE102**, which mentions the op-amp twice and says of it *"both
are outside this course"*; its module 4 **draws the symbol in a `match` unit** and
describes the buffer's job in the `why`; its module 4 derivation **ends by pointing at
the missing topic by name** (*"why the rule of 99 was out of reach until an amplifier was
put in front of the divider instead of a coil of wire"*); its module 5 derivation opens on
*"the summing node"*, a term defined by nothing in the catalogue; and its module 7 is
titled *"…and the in-amp"* while telling the learner *"no amplifier analysis is needed to
use this"*.

EE221 is also one of the two courses cycle 0 flagged as *"full syllabi, still need
density"* that no cycle had reached — EE201 went in cycle 10, EE202 in cycle 17 — and it
had **0 `read` units across 10 modules**, so the progression half of this track's brief
lands in the same course as the breadth half.

### Baseline, captured before any edit

```
85 circuit exercises / 360 checks · 564 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1290 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3360 per-option explanations · 6572 draws · answer in the top slot 24.5%
     quiz view 1260 mounts, 5464 options pressed, top slot 24.0%
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui: 78 driven keys and gestures · 10 things said · 15 floored kinds
circuit_model: 1475 analyses · 84 refusals · 15 plots · 15 floors, 17 ceilings
               386 published schematics, 365 with a DC operating point
circuit_view: 26 hostile coordinates · 420 mounts at 7 widths · 150 gestures
theme 135 contrast surfaces · desk 61 expressions · tune_ui 423 hostile openings
progress 29 hostile documents
EE221: 10 modules · 32 units · 3.20 u/m · 0 read · 5 derive · 4 build ·
       5 labs and a capstone · 19 derivation steps · 54 questions · 5 blanks holes
       8 published schematics, 0 containing an op-amp
catalogue: 62 courses, 368 modules, 1929 units · 1991 lesson ids
           386 schematics drawing 9 part kinds; OPAMP among the 12 never drawn
build: 3 parts / 111 keys · 32/32 + 30/30 · 13 visualisers · 3 tune models · 15 symbols ·
       62 payloads, 13086 KB · inlined 14334 KB · shell 1220 KB
```

### The attacks

**1. Senior Educator** — taken first, and this track's half of the brief turned out to be
the whole finding: **the course's central technique is the one thing it never explains.**

- **EE221's subject is loading, and its answer to loading is a device it does not teach.**
  Module 2 derives the rule of 99 ($R_{in} \ge 99R_{th}$ for 1%) and module 4's derivation
  closes by admitting the rule was unreachable until an amplifier replaced the coil of
  wire — and then the course moves on. Between those two units sits the `match` drill that
  draws the op-amp and says it "takes almost no current from the tap", which is an
  announcement of exactly the fact a learner has no way to have acquired.
- **Module 7 marks an error it never derives.** Its concepts say *"0.1% resistors cap it
  near 66 dB"*. That number is correct — it is measured below — and nothing in the
  catalogue could produce it, because the formula behind it needs the difference
  amplifier, which needs the virtual short, which needs negative feedback.
- **Module 5's "summing node" is used and never defined.** Its dual-slope derivation opens
  *"a resistor $R$ into the summing node of an amplifier with a capacitor $C$ in
  feedback"*, and the whole ramp rate $-V/RC$ depends on two facts about that node — it
  sits at zero and it takes no current — neither of which is stated anywhere.
- **A claim that is defensible as written and misleading as read.** Module 7 says putting
  the gain in the buffer pair is *"why an in-amp keeps its CMRR at high gain and a bare
  difference stage … does not"*. The derivation this cycle adds says the bare stage's
  rejection is $(1+k)/t$, which **rises** with gain; measured, a gain-100 stage with one
  resistor 0.1% out gives 100.10 dB where a unity one gives 66.03. The real cost is that
  changing the gain means re-scaling two of the four resistors and re-earning the match,
  and the real second reason for the buffers is input impedance. Rewritten to say both,
  with the "note what this is *not*" spelled out rather than left to be inferred.

**3. Simulation Auditor** — every number below was computed by loading `src/circuit.js` as
shipped and solving, before anything was written.

- **The op-amp's whole linear input window is 300 µV wide.** $(v_{pos}-v_{neg})/2$ divided
  by the gain is $15/10^5 = 150$ µV either side of balance. The device as sold is a
  comparator; everything else it does, it does inside a loop.
- **The follower's error is $-1/(1+A)$, and the solver reproduces it to three figures at
  every gain from 10 to $10^6$** — 0.908989532, 0.990084736, 0.998999519, 0.999899862,
  0.999989985, 0.999998999 for 1.000000 V in. That table is in the reading, because a
  device gain moving five orders of magnitude while the circuit gain moves in the sixth
  decimal is the entire argument for feedback and it is better shown than asserted.
- **The meter's own numbers, solved.** The chain is 9 MΩ over 1 MΩ, $R_{th}$ at the tap
  900 kΩ. A 100 kΩ converter hung straight on it drags the tap from 1.000000 V to
  **0.100000 V — a factor of ten, not a per cent.** The rule of 99 says 89.1 MΩ would be
  needed to reach 1%; solved at 100 MΩ the tap reads 0.991080 V, 0.89% low, so the rule is
  right. A follower feeding the same 100 kΩ converter reads **0.999989 V, 11 ppm low** —
  and module 1's own bullet says a 6½-digit instrument resolves 1 ppm and is specified to
  35, so the buffer's error is a real line in the budget and not what limits the
  instrument. Both halves of that are true and neither could be said before.
- **The closed-loop output resistance is 0.75 mΩ, measured** — 0.752 µV of droop per
  milliamp drawn — being the device's own 75 Ω divided by $1+A$. EE102's cascading module
  has claimed for a long time that a follower's output impedance is "milliohms". It is,
  and this is where they come from.
- **The model has no bandwidth at all, checked rather than assumed.** `MNA.acAt` on the
  follower returns 0.999989955 at 1 Hz and 0.999989955 at $10^{12}$ Hz. There is no
  gain-bandwidth product in the device, so every error in the reading is a DC error. Said
  so in the reading rather than left for a learner to trip over.
- **The inputs draw exactly zero.** Not a small number — the device's current vector is
  `[0, …, 0]` at both input pins by construction. A real one draws femtoamps to hundreds
  of nanoamps, and 1 nA on a 10 MΩ chain is 10 mV, which would swamp everything on the
  page. Recorded in the reading as a place the simulator stops being the world.
- **The 66 dB claim, measured three ways.** Difference amplifier, one resistor off by $t$:

```
   gain k    resistor off by t    CMRR formula (1+k+kt)/t     solved in the editor
      1            0.1%                   66.03 dB                  66.03 dB
      1            0.01%                  86.02 dB                  86.01 dB
      1            0.4%                   54.01 dB                  53.98 dB
    100            0.1%                  100.10 dB                 100.10 dB
```

  So module 7's sentence is right, and right for a reason it never gave: 66 dB is the
  **unity-gain** figure, and unity gain is what the difference stage inside an in-amp runs
  at. Two things the slogan hides and the derivation now says: the cap rises with gain, and
  four resistors each within 0.1% can be out in opposing directions, which is $t = 0.004$
  and **54 dB guaranteed against 66 dB typical**. The worst case was confirmed separately
  by perturbing all four ($R_1 -t$, $R_2 +t$, $R_3 +t$, $R_4 -t$): 73.98, 53.98, 40.00 and
  33.98 dB at $t$ = 0.01%, 0.1%, 0.5% and 1%, against $(1+k)/4t$ exactly.
- **With the ratios perfect, what is left is the model rather than physics.** A matched
  unity-gain stage measures 102.50, 122.50, 142.50 and 162.50 dB at $A = 10^3 \ldots 10^6$
  — exactly 20 dB per decade, and the residual is $A R_2/R_{out}$, i.e. the shipped 75 Ω
  output resistance leaking through the feedback network. A real op-amp's residual is its
  own CMRR specification, which this device does not have. **Not written into any lesson**,
  because a number that is an artefact of `OP_ROUT` should not be taught as a property of
  amplifiers; recorded here so the next cycle does not mistake it for one.
- **Checked and found correct, recorded so the next cycle does not re-derive it:** the
  bridge arms 350/350/350/350.7 at 10 V give 5.004995 V and 5.000000 V, so 4995.005 µV of
  differential on 5.0 V of common mode; the diode, MOSFET and bipolar counts from cycle 10
  and cycle 17 are unmoved; and EE221's existing four build exercises still score exactly
  as they did (M2 5/5·1/5, M3 5/5·2/5, M7 4/4·3/4, M8 4/4·1/4).

**2. Assessment Inquisitor.** EE221's 54 existing questions and 5 blanks holes are Track
3's ground and were not rewritten — `verify_quiz` is unmoved at 1366/252/1103/217/3360 and
EE221's budget entry is untouched. Audited for the one thing this cycle could falsify:
whether any key depends on the op-amp being absent, or on the 66 dB figure being taken on
trust. **None does.** M7/Q5's key — *"because the difference stage's rejection depends on a
matched resistor ratio, and changing the gain there would unbalance it"* — is precisely
what the new derivation proves, so the derivation strengthens the question rather than
contradicting it. The two new graded units add no question deliberately: both are graded by
the solver against the real device, and each was additionally run against wrong-but-plausible
designs to show it discriminates rather than merely passing its own answer.

**4. UX & Accessibility Hardener.** Content-side, as cycles 1, 4, 7, 10 and 17 established.
Every math fragment in the units this cycle wrote or touched was pushed through the shipped
`MathML.render` — **263 fragments, 263 rendered, 0 raw, 0 swallowed** — with cycle 10's
escaped space and cycle 17's `\bigl`/`\bigr` avoided from the start rather than repaired
after. No hard-coded colour and no raw HTML was introduced; both data tables are fenced
`text` blocks inside `overflow-x:auto` rather than markdown tables, which is cycle 4's rule
for staying safe at 375px. The two new schematics went through `verify_circuit_view`'s
recording canvas at seven widths as part of the catalogue sweep: 424 mounts, all 390
drawings inside their own box.

### What changed

**Four new units, appended to the two modules they belong to**, and no module added. Every
existing unit kept its unsuffixed id, so nothing anyone has completed is orphaned — checked
rather than asserted, by building every lesson id in the catalogue exactly as
`src/app.js` does, at HEAD and now: **1991 → 1995 ids, 4 new, 0 orphaned, 0 duplicated.**

| | M4 `read` | M4 `build` | M7 `derive` | M7 `build2` |
|---|---|---|---|---|
| title | The amplifier the rule of 99 was waiting for | The buffer between the chain and the converter | Where the rejection of a difference amplifier actually lives | A gain of 100 on the bridge, without losing the rejection |
| size | 2243 words | 1 × `OPAMP`, 5 checks | 4 steps | 1 × `OPAMP`, 4 checks |
| the measurement | 11 ppm against the rule of 99's 1% | 0.100000 V → 0.999989 V | $A_{cm} = kt/(1+k+kt)$ | 0.4903 V, and −15 V when one resistor moves |
| reference / start | — | 5/5 · 2/5 | — | 4/4 · 3/4 |

**The reading is EE221's first**, and the prerequisite bridge. It uses only what EE102 and
this course's own earlier modules contain: it starts from module 2's divider and module 4's
ohms-per-volt, states the device as one equation and one gain, notices that a $10^5$ gain
into a 15 V rail leaves a 300 µV input window, closes the loop and solves
$v_{out} = A(v_{in} - v_{out})$ **rather than announcing a virtual short** — the short then
falls out as $v_+ - v_- = v_{out}/A$, with both cases where it fails named and measured. It
derives the follower, the non-inverting and the inverting stages, notes that the inverting
one's input resistance is $R_1$ and nothing else (which is the bill module 7 pays), prices
the buffer against the rule of 99 on this course's own chain, and closes on four places it
stops holding — rails, $1/(1+A\beta)$ once the gain is not 1, zero input current, and no
bandwidth — of which the middle two are exactly the errors module 7's exercise is measured
showing, so they arrive as expected rather than as defects.

**M4's build is the novice rung**: three wires and a part, and the whole lesson is in one of
the wires. **M7's is the flagship**: the same specification as the difference stage the
module already describes, on the bridge module 6 built, where **raising the obvious resistor
puts the output on a rail**. Its third check measures the gain from the difference *actually
present at the learner's own input resistors* — so the 1.7% the 10 kΩ inputs take off a
350 Ω bridge is reported by the fourth check as loading rather than blamed on the amplifier,
and the 0.101% the finite loop gain takes is inside the tolerance and named in the message.

**Each new build was run against wrong-but-plausible designs, using the checks as emitted**,
because a check that has only ever seen its own reference has not been shown to discriminate:

```
  M4    reference 5/5 · start 2/5 · no feedback wire 2/5 (output at 14.99 V) ·
        inputs swapped 4/5 · old tap wire never deleted 2/5 (tap collapses to 83 µV) ·
        output never joined to the converter 2/5 · converter swapped for a 1 GΩ one 4/5
  M7.2  reference 4/4 · start 3/4 · only R2 raised 1/4 (−14.999 V, on the rail) ·
        only R4 raised 3/4 (4.910 V, almost all of it common mode) ·
        gain 100 at 1k/100k 3/4 (bridge loaded 15%) · gain 100 at 100k/10M 4/4 ·
        ratios 0.1% apart 3/4 · ratios 1% apart 3/4 · gain 10 by mistake 3/4 ·
        stretched gauge in the other leg 3/4 (−0.4903 V)
```

**Six pre-existing items changed**, verified structurally rather than by reading the diff —
**4 units added, 0 removed, exactly 6 pre-existing items changed**: M4's and M7's concept
lists (each gaining a bullet that carries the measured number), M4's derive closing and M5's
derive brief (the two forward pointers, one of which defines "summing node" where it is
used), the course outcomes, which gain two, and the course assessment, which said "four
circuits … five guided derivations" and would otherwise have become false.

EE221: 32 units → **36** · 3.20 units per module → **3.60** · 0 read → **1** · 4 build →
**6** · 5 derive → **6** · 19 derivation steps → **23** · 8 published schematics → **12**,
of which **3 contain an op-amp**, against 0 in the whole catalogue before this cycle.
Questions and blanks holes unmoved at 54 and 5.

### Found in my own work, and fixed

- **Two hostile variants that were not the circuits I said they were.** The first drafts of
  the "inputs swapped" and "buffer in front of the chain" designs each routed a wire through
  a cell another run already occupied — one shorting the op-amp's own inputs together at
  (12,5), the other shorting the 9 MΩ arm — so both reported failures that had nothing to do
  with the fault being tested. Caught by printing the netlist each variant actually builds
  and reading the node assignments, rather than by trusting that a drawing does what it looks
  like. Every variant in the table above was re-checked that way before its number was
  written down. The second was replaced with a better one anyway: leaving the old tap wire in
  is a mistake learners actually make, and putting a buffer in front of the chain is not.
- **A check that passed a latching circuit.** With the tap on the inverting input and the
  feedback on the non-inverting one, **every voltage in the M4 circuit comes out the same to
  five figures** — the reference reads 0.9999891 and the positive-feedback version 1.000009,
  which is $A/(A+1)$ against $A/(A-1)$ and differs only in the *sign* of an 11 ppm error. A
  DC operating point is a solution of the circuit's equations and is never asked whether the
  circuit would stay there, so no measurement on the page could tell them apart. The fifth
  check therefore reads the wiring — the only one in either exercise that does — and its
  message says why, because that is a fact about simulators worth knowing. Rejected the
  alternative of a one-sided ppm test: it would pass and fail on a 20 ppm difference that any
  change of load or gain moves.
- **A common-mode gain I stated from memory and had wrong by a factor of sixteen.** The M7
  brief said raising $R_2$ alone leaves "a common-mode gain of about −3". The derivation on
  the same page gives $(R_1R_4 - R_2R_3)/(R_1(R_3+R_4))$, which for 10k/1M/10k/10k is
  **−49.5**. Recomputed and rewritten, with the consequence stated — 50 V per volt against
  5 V of common mode is −250 V asked of a 15 V rail, which is why it rails rather than merely
  reads high.
- **A bridge voltage written to one more digit than it has.** "5.005000 V" for a node that
  solves to 5.0049950. Corrected to 5.004995.
- **A "hundred times worse" that is nearer a thousand.** The M4 concepts bullet compared the
  rule of 99's 1% against the follower's 11 ppm and called it a hundred. It is 10 000 ppm
  against 11, so roughly nine hundred. Rewritten to "nearly a thousand times larger", which
  is true at either end of the arithmetic.
- **One hedge word introduced and removed.** A "just as readily as" in a check message.
  Counted by diff against HEAD rather than by counting twice: EE221 carries **15 at HEAD and
  15 now**, so 0 introduced.

### Left alone, deliberately

- **The three-op-amp instrumentation amplifier itself is still not built**, and this is the
  clearest next instalment. The module now derives why its difference stage runs at unity,
  measures what a bare stage costs on a bridge, and says what the two buffers buy — but the
  in-amp is still described rather than drawn. It is buildable: three `OPAMP` parts, two
  feedback resistors and a gain resistor, all inside the solver's reach. What stopped this
  cycle is routing, not physics — the front pair's two inverting nodes have to cross the
  output rails of both buffers on a grid where a wire joins every cell it passes through, and
  three failed layouts (each verified by printing the netlist, above) is where the budget for
  it went. Recorded with the reason so the next cycle starts from the layout problem rather
  than rediscovering the topology.
- **`PNP`, `PMOS`, `SW`, `LDR`, `NTC`, `POT`, `LAMP`, `METER` and `BAR` are still drawn by
  nothing.** Nine kinds, down from ten: the census across all **390 published schematics** is
  now `GND 854 · R 748 · V 406 · OUT 342 · C 171 · L 91 · I 53 · D 4 · LED 4 · NMOS 4 ·
  OPAMP 3 · NPN 2`. `METER` and `LAMP` are the interesting pair for this course specifically:
  EE221 module 4 is *about* a meter's shunts and multipliers and could draw one.
- **`emit.py`'s `DIAGRAM_KINDS` is still `{R, C, L, V, I, GND, OUT}`**, so a `numeric` unit
  still cannot draw an op-amp even though `MATCH_SYMBOLS` next to it can and `drawPart`
  renders one. Cycle 10 recorded this with both list contents and did not spend it; this
  cycle did not need it either, because a `build` unit carries a real schematic and is graded
  by the same solver. Unchanged, and the reason is unchanged: widening a gate to serve
  content nobody has written is how a gate ends up enforcing a comment.
- **The op-amp is still invoked and not taught in six other courses.** The ten sites above
  minus EE221's two: EE101 ×3, EE102 ×2, EE121, EE211 ×3, EE231. All of them are now
  *reachable* — EE221's reading derives what each one assumes — but none of them says so, and
  EE221 is not on any of their prerequisite chains, so a learner arriving at EE102's
  cascading module still meets the follower as an assertion. The honest fix is a reading in
  EE101 or EE102, which is a second course and the brief says one. Recorded with the sites.
- **EE221 still has one reading in ten modules**, and modules 1, 2, 3, 5, 6, 8, 9 and 10 have
  none. This cycle wrote the one that closes the prerequisite gap and did not write nine
  more; that is Track 1's density pass and cycle 1 established it is its own cycle. **Fifteen
  courses remain thinner**, all at exactly 1.00 units per module — CAP501, CE101, CE201,
  DL501, ELEC410, ELEC420, ELEC430, ETH501, FM501, GFX401, HPC401, ML401, QC510, ROB520,
  SEC301 — unchanged from cycle 17's list, so this is a shared debt rather than a worst case.
- **CE101 was weighed a third time and passed over a third time.** Cycles 10 and 17 both
  recorded it as a root of the CS degree's hardware chain (no prerequisites, prerequisite of
  CE201 → CS210 and HPC401) and both chose a course where gates could prove the fix instead.
  The graph is unchanged and was not re-derived. It is still the strongest remaining
  *build-a-course* target and it will still have only `verify_quiz`, `verify_labs` and the
  emitter to hold it up; that is an argument about what kind of cycle it needs, not about
  whether it needs one.
- **EE202's M5 clipping-and-distortion build still has its current source**, cycle 17's
  recorded next instalment, untouched. So is the AC-excitation finding cycle 17 recorded at
  `src/circuit.js:1165` — `p.ac` is still copied into the netlist and read by nothing, and it
  is still a migration rather than a line. Neither was needed here: both new exercises are
  DC-graded.
- **EE221's `credits` and `hours` unchanged at 10 and 120**, and `catalog/_spine.ee.json`
  untouched. The spine carries course metadata only, and 36 units against a nominal 120 hours
  remains light rather than heavy.
- **The two 6½-digit numbers in module 1 were left as they are.** The reading leans on them —
  1 ppm of resolution, 35 ppm of specification — and they are module 1's wording, correct,
  and not this cycle's to restate.
- **`docs/programs` aged out one MA121 payload and one CS310 payload and gained two for
  EE221.** Two because this cycle built three times, and both are inside a retained
  generation. The rolling window, as every cycle since 1 has established. Verified rather than
  assumed: **3 generations naming 64 files, 64 on disk, covering 62 distinct courses,
  0 orphaned and 0 missing.**

### Gates, after

Every pre-existing number unmoved. Seven numbers moved, each by exactly what was added.

```
verify_circuits      All good: 87 circuit exercises, 369 checks · 593 labels
                     (85 + 2 · 360 + 9 · 564 + 29)
                     EE221/M4   reference 5/5 · start 2/5
                     EE221/M7.2 reference 4/4 · start 3/4
                     and the four that were already there, unmoved:
                     M2 5/5·1/5 · M3 5/5·2/5 · M7 4/4·3/4 · M8 4/4·1/4
verify_derivations   All good: 1294 steps across 46 courses   (1290 + 4; EE221 19 -> 23)
verify_circuit_model All good: 1487 analyses vouch for every number they return and 84
                     refuse rather than guess · 15 plots · 15 floors, 17 ceilings ·
                     390 published schematics, 369 with a DC point   (1475 + 12 · 386 + 4)
verify_circuit_view  All good: 26 hostile coordinates · 390 published drawings unchanged
                     by the guard · 424 mounts at 7 widths · 150 gestures   (420 + 4)
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_quiz          All good: 1366 questions in 252 quiz units and 1103 holes in 217
                     blanks units · 3360 per-option explanations · 6572 draws · 24.5% ·
                     quiz view 1260 mounts, 5464 options pressed, 24.0% · every bank
                     within its answer-tell budget and above its whys floor
verify_labs EE221    All good: 6 labs
verify_circuit_ui    All good: 78 driven keys and gestures, says 10 things while doing it
verify_theme         All good: theme tokens, 135 contrast surfaces in both themes,
                     the 375px topbar and the mobile drawer
verify_desk          All good: 61 expressions at the extremes
verify_tune_ui       All good: 21 tune units, 423 hostile opening values, 462 targets,
                     105 paints, 270 drags, 493 mounts
verify_progress      All good: 6 unload writes · 29 hostile documents · 7 merges
emit.py EE221        ok — 10 modules, 5 labs, capstone +tests
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 13086 -> 13129 KB ·
                     inlined 14334 -> 14378 KB · shell 1220 KB unchanged
catalogue            62 courses, 368 modules, 1933 units (1929 + 4) · 1995 lesson ids
```

The pre-existing gates were compared on the figures they report, which are reproduced above
against the baseline block at the top of this entry and match it line for line; a byte-level
diff of their output was not run, and that is stated rather than implied.

Beyond the gates: every number written into the four new units computed by loading
`src/circuit.js` as shipped and solving, before it was written — the follower's
$-1/(1+A)$ at six gains, the 0.100000 V collapse and the 11 ppm that replaces it, the
0.75 mΩ closed-loop output resistance, the flat gain from 1 Hz to a terahertz, and the
66.03 / 86.01 / 53.98 / 100.10 dB that the new derivation predicts to two decimal places;
all four derivation steps checked symbolically in SymPy **and** through the shipped
`MathCheck.latexToPy` before authoring, so neither the algebra nor the LaTeX was discovered
to be wrong by the gate; both new builds run against **seven and ten** wrong-but-plausible
designs using the checks as emitted, with each hostile variant's netlist printed and read
before its score was believed; all 263 math fragments rendered through the shipped
`MathML.render` (263 of 263, 0 raw, 0 swallowed); hedge words counted by diff against HEAD
(15 and 15, 0 introduced); the EE221 diff compared structurally against HEAD rather than as
lines (4 added, 0 removed, 6 changed); every lesson id in the catalogue rebuilt exactly as
`src/app.js` builds them at HEAD and now (1991 → 1995, 0 orphaned, 0 duplicated); and the
payload window checked for orphans.

**A note on the working tree.** The runner's lock (`.gauntlet.pid`, pid 11729) was live
throughout and this cycle is the process it launched, so `emit.py` and `build.mjs` were safe
to run. The diff is `catalog/authors/EE221.py`, `catalog/EE221.json` and the `docs/` build
output, and nothing else. No other course, no renderer, no gate and no tool was touched.

---

## Cycle 24 — TRACK 5: UI, Layout & Visual Aesthetics

*(the runner labels this commit "cycle 5"; its counter restarts per run and this log's does
not. Run D's cycle 1 was this file's cycle 20, and its cycle 4 was cycle 23.)*

**Target: the type scale — every `font-size` and every positive `letter-spacing` in
`src/index.head.html` and `Desk.css()`.** One subsystem, defined by what it is rather than
where it sits: **323 size declarations and 36 tracking declarations**, across every screen
the application has.

Chosen because it is the one dimension of this design that **nothing has ever measured.**
Every colour has come from a token since cycle 5 and been held to a computed contrast since
cycle 11; `verify_theme` has 135 contrast surfaces, a canvas palette section and a topbar
budget, and **not one number in it is a size.** Cycles 11 and 18 both recorded the
consequence and both declined it with the same sentence — *"a type-scale pass touches every
screen and would have meant verifying none of them"* — which is true exactly as long as
there is no gate. Building the gate is what makes the pass verifiable, so this cycle is
both halves or neither.

### Baseline, captured before any edit

```
87 circuit exercises / 369 checks · 593 part labels round-trip
21 tune units · 216 numeric answers verified, 0 unchecked, 218 figure-only
1294 derivation steps across 46 courses
1366 questions in 252 quiz units · 1103 holes in 217 blanks units
     3360 per-option explanations · 6572 draws, 4384 options picked · top slot 24.5%
     quiz view 1260 mounts, 5464 options pressed, top slot 24.0%
13 visualisers / 3 tune models · 747 draws, 249 readouts · 364 opening values
circuit_ui    78 driven keys, 10 things said, 15 kinds above their stamp floor
circuit_model 1487 analyses · 84 refusals · 15 plots · 15 floors, 17 ceilings
              390 published schematics, 369 with a DC operating point
circuit_view  26 hostile coordinates · 424 mounts at 7 widths · 150 gestures
tune_ui       423 clamped openings · 462 targets · 105 paints · 270 drags · 493 mounts
desk          61 expressions · Desk.css() hands the theme gate 102 lines
theme         14 exemptions · 135 contrast surfaces x 2 themes · tightest text 4.61:1
              (.q-hint [light]) · faintest state 1.11:1 · 3 held below the floor on
              purpose · 74 of 135 read their ink out of the stylesheet
              canvas 10 palette tiers · 154 paint sites / 9 tiers · quietest 3.77:1
progress      29 hostile documents
TYPE          36 distinct sizes in 323 declarations · 20 tracking spellings in 36
              declarations · 61 rules under 11px · measured by nothing
build: 3 parts / 111 keys · 32/32 + 30/30 · 13 visualisers · 3 tune models · 15 symbols ·
       62 payloads, 13129 KB · inlined 14378 KB · shell 1220 KB
```

### The attacks

**1. Senior Educator** — taken first, because a type scale is a hierarchy, and this
persona's whole brief is whether a hierarchy explains itself.

- **The scale does not exist. 36 distinct sizes, and the bottom of it is twelve
  consecutive half-pixel steps.** Counted, not estimated: 9.5, 10, 10.5, 11, 11.5, 12,
  12.5, 13, 13.5, 14, 14.5, 15, then 16, 16.5, 17. Adjacent ratios **1.034 to 1.053.**
  **285 of the 323 declarations — 88% — live in that band.** A 4% size difference is not a
  distinction a reader makes, so two elements written to read as different levels render as
  the same one. This is the visual form of the defect this persona names in prose: a
  structure asserted rather than delivered. The fifteen values were not a scale anybody
  chose; they are fifteen separate decisions taken one rule at a time, and the tell is that
  **`.1em` and `.10em` both appear** in the tracking beside them — the same number, written
  twice, by two people-moments that never met.
- **61 rules are under 11px, nine of them at 9.5px**, and the 9.5px ones are tracked
  uppercase mono — `.ring span`, `.deg-stats .stat span`, `.pc-stats .stat span`,
  `.meta-card dt`, `.rubric th`, `.cb-head .lang`, `.cb-out-head b`, `.ftab .ro-tag`,
  `.ac-kind`. Uppercase, tracked, monospace and 9.5px is four separate legibility taxes on
  one string. The stylesheet's own comment at `.rail-module h4` says a 9.5px module title
  was *"the smallest type in the application"* and was raised out of exactly this; the
  sweep stopped at that one rule. **Fixing the line you were pointed at is not fixing the
  defect** — the curriculum's own invariant, and this is it in the stylesheet.
- *Checked and left, so it is not re-derived:* the **display band above 18px is genuinely
  per-component and three of its entries are not text at all** — `.track-head .t-icon` and
  `.prof-av` at 24px and `.ch-icon` at 19px are emoji and avatar boxes. Collapsing 19–34px
  onto a ramp would have flattened real hierarchy between distinct screens and resized
  three things that are not type. It is held by enumeration instead; see below.

**4. UX & Accessibility Hardener** — this track's brief is mostly its brief, and here it
produced the cycle's largest finding, which is not about size at all.

- **The rail draws the wrong lesson number on 596 of 1990 rows, and has been doing it since
  before this cycle.** `.rail-lesson` is `grid-template-columns:30px 22px minmax(0,1fr)` and
  `.rail-lesson .num` carries `padding-right:8px`, so the number gets **22px of glyph — 3.6
  characters of JetBrains Mono at the 10px it was set in.** A lesson number is written by
  `app.js` in one of two forms: `<module>·<kind><n>` for a catalogue course (`app.js:181`)
  and `<module>.<lesson>` for a foundation track (`app.js:23`). Derived from the catalogue
  and `src/tracks.js` rather than assumed: **1990 numbers, of which 546 are four glyphs and
  50 are five** (`1·r2`, `10·r2`). The cell is `text-align:right` inside `overflow:hidden`,
  which does **not** ellipsise — it cuts the **leading** glyph. So `10·r2` was drawn as
  `0·r2`: not a truncation a learner can see is a truncation, but a different module's
  number, sitting in the rail, looking correct. **30% of the rail.**
- **The gate that would have caught it was written for the rule one line below and stopped
  there.** `verify_theme`'s `railid` section measures `.rail-course .cid` against the
  longest of the 62 course ids — and `.rail-lesson .num` **shares the very declaration it
  reads** (`.rail-lesson .num,.rail-course .cid{...font-size:10px...padding-right:8px}`) and
  was never measured. The stylesheet even carries a 4-line comment above `.rail-course`
  doing this arithmetic for the id column. One rule up, same sum, nobody did it. *A gate
  that skips what it did not expect is worse than no gate*, one more time.
- **The id column had exactly zero slack, which is why the type could not be raised without
  finding this.** `CTRL510` is 7 glyphs; at 10px that is 42px of glyph plus 8px of pad =
  **50.0px in a 50px track.** Raising the tier to 11px needs 54.2. The two columns are the
  reason a type floor could not be a one-token edit, and they are why this debt looked
  bigger than it was.
- *Measured and found sound:* every one of the **7 rules that sit on the raised tier and
  declare a fixed box** — `.save-state` (a `min-width`, so it grows), `.dv-n` 24px,
  `.pq-b` 18px, `.pq-arrow` 10px, `.pb-icon` 22px, `.opt .k` 19px, `.ac-ic` 18px — centres a
  single glyph with `place-items:center` or `text-align:center`. None can overflow
  meaningfully at 11px, checked individually rather than assumed from the count.
- *Measured and found sound:* `prefers-reduced-motion` is honoured with
  `*{animation:none!important;transition:none!important}`, which covers all 26 animations
  and 35 transitions in the file. No gap to repair.

**3. Simulation Auditor** — no solver in a stylesheet, so pointed at the arithmetic
downstream of the change, computed from the source rather than eyeballed.

- **Raising the ramp had to not move the topbar, and that was checked before choosing the
  steps, not after.** The 375px budget reads two type sizes out of the stylesheet:
  `.metric.streak .fl` at 13px and `.metric.streak b` at 12px. Both are already whole
  pixels and both are on the chosen ramp, so **204.6px of furniture and 86.4px for the
  title are unmoved** — confirmed by the gate after the edit, not predicted. Had the ramp
  been built by rounding to nearest instead of upward, 12.5 and 13.5 would have pulled
  those two and the phone layout would have moved for no reason.
- **The rail's title track pays for the wider number column, and the amount was computed:**
  a lesson row goes from 176px of title to 165px on desktop and 186 to 175 at ≤980px; a
  course row loses 5px. Both keep `text-overflow:ellipsis`, so the cost is ellipsising ~11px
  sooner on a 262px rail, against drawing 596 correct numbers. Recorded because it is a real
  cost and not a free repair.
- **Every relative size resolved against its actual parent.** Eight rules are `em`-relative,
  and a declared-size check is blind to them by construction — `.88em` is fine on a 14px
  parent and 10.56px on a 12px one. Computed: `.explain code` is **11.44px**, the smallest
  rendered text in the application, and the only one within one ramp step of the floor.

**2. Assessment Inquisitor.** No graded question in a stylesheet, so — as in cycles 2, 5, 6,
11 and 18 — pointed at the one thing in scope it can judge: whether a distinction announces
itself or merely exists.

- **The whole cycle is that question.** A distractor that no one could pick is not a
  distractor, and a type step no one can see is not a step. Twelve half-pixel steps and
  twelve tracking values are the stylesheet's version of four options where only one is
  defensible: the structure is present in the source and absent from the reader's
  experience. That is why the ramp is held to a **minimum ratio** rather than merely to a
  count of values — a gate that allowed six steps of 1.02 would be counting names, not
  differences.

### What changed

**A type ramp, in `:root`, and 285 declarations moved onto it.** Six steps, every one a
whole pixel, every adjacent ratio at least 1.071:

| token | px | absorbs | n |
|---|---|---|---|
| `--t-label` | 11 | 9.5, 10, 10.5, 11 | 107 |
| `--t-meta` | 12 | 11.5, 12 | 52 |
| `--t-ui` | 13 | 12.5, 13 | 63 |
| `--t-read` | 14 | 13.5, 14 | 33 |
| `--t-body` | 15 | 14.5, 15 | 23 |
| `--t-title` | 17 | 16, 16.5, 17 | 7 |

**Every half-step rounds up and the three tiers under the floor come up to it, so nothing
in the application got smaller** — every delta in the transform report is ≥ 0. Rounding up
rather than to nearest is the deliberate choice: this ramp is repairing a legibility floor,
and a collapse that made 71 half-step surfaces 0.5px *smaller* would have spent the cycle's
budget against itself.

**The two rail tracks, sized against the strings they actually hold.** `.rail-lesson`'s
number column **30px → 41px** (5 glyphs at 11px = 33px, plus the 8px pad) and
`.rail-course`'s id column **50px → 55px**. The module headings that are positioned against
the lesson grid moved with it, `margin-left` 44 → 55 and the sub-rail's 56 → 67, so the rail
keeps its alignment rather than acquiring a new one.

**Tracking, which is the same dimension one layer in.** All 36 positive `letter-spacing`
declarations sit on `--t-label` doing one job — a small mono label, 33 of them uppercase —
and carried **twelve values from .01em to .16em**, including `.1em` and `.10em` for the same
number. Two tokens now: `--tr-caps:.14em` (where 13 of the 36 already were, the largest
group) for uppercase mono micro-labels, and `--tr-mono:.03em` for mono that is not
uppercase. `.chip`'s `.01em` — 0.11px at 11px, on a sans chip that is not a tracked label —
became `0`. The negative ramp is **left as literals**: it descends correctly with size
(-.015 at 14–17px, -.02 at 19–25, -.025 at 20–26, -.03 at 27–38) and each value belongs to a
display heading this cycle deliberately did not collapse; only its **two duplicate
spellings** (`-0.03em`, `-0.025em`) were normalised so the set is countable.

**Two repairs to gate machinery that the tokens exposed:**

- **`typePx()`**, because a size now comes from a token the way a colour does, and both
  existing consumers `parseFloat`-ed the declaration.
- **The topbar check was reporting `[ok]` on a number it could not compute.** With the sizes
  tokenised it printed *"NaNpx of furniture, NaNpx for the screen title"* and **passed**,
  because `NaN < 60` is `false`. Every input is now named and checked finite, and the
  verdict refuses rather than defaults. This is a pre-existing defect in a check cycle 5
  wrote; it was invisible while the inputs were literals and would have stayed invisible.

**`railid` became `tracks`, and measures both columns.** The worst case is derived from the
catalogue and from `app.js`'s own `UNIT_SPEC` — read out of `app.js` rather than copied, so
a new unit kind cannot silently widen the column — plus `src/tracks.js` for the second num
format. It reports **how many rows would be cut, not merely whether the worst one is**,
because a column that clips 0.4% and one that clips 30% are not the same defect.

**A `type` section in `verify_theme.mjs` and a `type` block in `theme_budget.json`**, with
six checks: the ramp is whole-pixel, ascending, above the floor and above a minimum ratio;
nothing under 18px declares a literal; the display band is enumerated **in both directions**,
so a new size fails and a listed size nothing uses also fails; relative sizes are resolved
against the parent named in the budget; the canvas is held to its own floor and its
sub-11px count may shrink but not grow; and positive tracking comes from a token.

**The gate was not trusted until it was seen to fail. 16 mutations, 15 it had to reject and
one it had to pass**, each applied to the real files, run, restored, with the restore
verified by SHA-256:

```
   1  the floor back to 10px, where 61 rules were
   2  a half-pixel step reintroduced on the label tier
   3  --t-title to 16px — a 1.067 step, under the minimum
   4  the ramp made non-monotone
   5  one rule reverted to a literal, the way all fifteen values began
   6  a new display size nothing wrote down
   7  a budget display entry whose size nothing uses any more
   8  the PARENT dropped a step — the only way .88em goes under the floor
   9  canvas text under the floor the canvas is held to
  10  one more canvas site under the DOM floor
  11  the lesson-number column back to 30px, cutting 596 leading glyphs
  12  the id column back to 50px, which fitted only at 10px type
  13  one label's tracking hand-picked again
  14  one display value written two ways again
  15  a size token the topbar reads pointed at nothing — the NaN that used to pass
  16  a comment reflowed and nothing else — the control, which passes
```

### Found in my own work, and fixed

Five, and every one was caught by a measurement rather than by re-reading.

- **My transform's idempotence guard suppressed the thing it was guarding.** It skipped
  inserting the token block `if '--t-label' not in styles` — but the remap had *already*
  written `var(--t-label)` into 107 rules, so the test was true and **the six token
  definitions were never written at all.** The stylesheet referenced a ramp that did not
  exist. Found because the gate then failed to resolve `var(--t-label)`, not because I
  re-read the script.
- **My first measurement of the rail defect used the wrong number format and an incomplete
  unit list.** I modelled every lesson number as `(mi+1).(li+1)` — which is `app.js:23`, the
  *foundation track* format — and enumerated unit kinds from a hand-written list that
  **omitted `sandbox`**. It produced "401 of 1820, 22%", and I had already written that into
  a stylesheet comment. The real figures, taken from `UNIT_SPEC` and both formats, are **596
  of 1990, 30%**, and the worst case is `10·r2` rather than `10.10`. The comment was
  corrected before anything else was built on it. This is the `len()`-on-a-unit-key trap in
  a new coat: the kinds are a list and I typed the list from memory.
- **The `underFloor` number I wrote into the budget was wrong, and the gate rejected it.**
  I put 12, having counted `circuit.js`'s sub-11px draw sites and stopped; `studio.js` has
  two more. The gate said *"14 canvas draw sites are under the DOM's 11px floor and the
  budget records 12"* on its first run. Corrected to 14, with the miscount recorded in the
  budget's own comment so the next reader knows the number was contested.
- **My mutation harness scored a mutation on the wrong evidence.** Mutation 2 sets
  `--t-label` to 11.5px; the suite marked it "ok" because the gate exited non-zero — but the
  failure it printed was the **id column overflowing**, a true side effect and not the
  half-pixel check under test. A suite that accepts any rejection measures that the gate is
  noisy, not that the check exists. Each mutation now names a phrase the *right* check
  produces and only counts if that check spoke. All 16 still pass, and mutation 2 now shows
  the half-pixel message with "(+3 other checks also objected)" beside it.
- **My rule walker lost one rule inside `desk.js` and I nearly shipped the gap.** The desk's
  CSS is an array of JavaScript strings, and the brace walker mistook a function body for a
  rule, skipping `.dsk-mini`'s `.06em`. The transform's own closing sweep — *"positive
  letter-spacing literals remaining: 1"* — is what caught it; without that line it would
  have been a silent one-rule hole in a change whose whole claim is completeness.

### Left alone, deliberately

- **The display band above 18px: 24 declarations across 13 values, uncollapsed.** They are
  per-component headings on distinct screens, and `.track-head .t-icon`, `.prof-av` and
  `.ch-icon` are emoji and avatar boxes rather than type at all. Held by enumeration in the
  budget with a reason per value, and the gate fails in both directions, so the band cannot
  grow silently — but it is not a ramp and this cycle did not make it one.
- **The negative tracking ramp stays literal**, for the same reason: five values that
  descend correctly with size and belong to headings that were not collapsed. Only the
  duplicate spellings were fixed. Recorded so the next cycle does not read "5 values" as
  neglect.
- **The canvas still draws at 8.5px in two places** — `circuit.js:2805` (the breadboard's
  column numbers) and `:2934` (the MCU supply caption) — and **14 of its 23 draw sites are
  under the DOM's new 11px floor.** Cycle 18 recorded these two and declined them because
  the fix means re-laying-out the breadboard's column pitch, which is a Track 2 change to
  the board. Still true. They are now **held rather than merely recorded**: a floor stops
  the canvas getting smaller and a count stops the sub-floor set growing. Both numbers are
  debts that may shrink and be written down and may not grow.
- **`--lime` is used as ink in 36 places and the light theme puts most at 3.4–4.1:1.**
  Re-counted rather than inherited: cycle 11 recorded 35, it is **36** now. Cycles 11 and 18
  both declined it as *"the accent weight of every screen in the application, a decision
  about the design language rather than a repair"* that *"belongs in a cycle that does
  nothing else."* This cycle did not take it either, and it is now the debt **three** Track 5
  cycles have named without anyone taking it. It is the strongest candidate for the next
  one — the same position the canvas palette was in before cycle 18 took it.
- **61 of the 135 contrast surfaces still describe rather than enforce.** Re-measured, not
  inherited: 74 carry a `sel` and read their ink from the stylesheet, 61 do not. Unchanged
  from cycle 18, which inherited 61 from cycle 11's 58. Cycle 11 called back-filling them
  *"the first thing the next Track 5 cycle should do"* and no Track 5 cycle has. This one
  spent its budget on the dimension that had **no** gate rather than on making an existing
  gate stricter, which is a defensible ordering and is recorded as a choice rather than an
  oversight.
- **Five `transition:all` declarations remain** — `.seg button`, `.ftab`, `.ptab` and two
  card rules. Cycle 11 replaced `.opt`'s with the three properties it actually animates and
  the rest were never swept. Counted and left: they are tab and segment controls, a
  different subsystem from the type scale, and folding them in would have been the "cycle
  that touches everything" the curriculum warns about. `prefers-reduced-motion` neutralises
  all of them for the readers most affected.
- **`palette()` still runs a `getComputedStyle` per `frame()` and there are 7 call sites.**
  Unchanged from cycle 18; a Track 2 change with a lifecycle in it.
- **No author file, no `catalog/*.json`, no lesson id and no schema was touched**, so
  `emit.py` was not run and the staleness guard is not armed. The mechanical confirmation is
  that the payload total is **13129 KB before and after** and `git status` reports **nothing
  under `docs/programs`** — no course's JSON moved, so no payload could.
- **`docs/programs` holds 65 payloads against the 62 the current shell names**, verified
  rather than assumed: 62 named, **0 missing**, 3 retained from earlier generations. It was
  65 before this cycle too — the build wrote byte-identical payloads — so the rolling window
  grew during cycles 19–23, not here.

### Gates, after

Every pre-existing number unmoved. Four moved: the theme gate's three new `type` lines and
its `railid` line becoming `tracks`, and the two artifact sizes, by the CSS, the tokens and
the gate's own new code.

```
verify_theme         All good: 14 exemptions · 135 contrast surfaces x 2 themes — unmoved
                     — tightest text 4.61:1 (.q-hint [light]), faintest state 1.11:1,
                     3 held below the floor on purpose, 74 read from source
                     topbar  at 375px: 291px of bar, 204.6px of furniture, 86.4px for
                             the screen title — UNMOVED across a whole-file type change
                     tracks  55px holds "CTRL510", the longest of 62 course ids, at
                             54.2px · 41px holds "10·r2", the longest of 1990 lesson
                             numbers the rail can draw, at 41.0px            [WAS railid]
                     canvas  10 palette tiers, both fallback tables agree
                     canvas  154 paint sites across 9 tiers, quietest 3.77:1 (rule
                             [light]), 2 decorations under their ceiling
                     type    6 steps from 11px to 17px hold every one of 285 sized
                             declarations · tightest step 1.071 · 13 display sizes
                             enumerated · smallest relative 11.44px (.explain code) [NEW]
                     type    23 canvas draw sites across 2 files, smallest 8.5px, 14
                             under the DOM floor — held from growing              [NEW]
                     type    36 positive tracking declarations come from 2 tokens, and
                             the display ramp's 5 negative values are each written one
                             way                                                  [NEW]
verify_desk          All good: 61 expressions · Desk.css() hands the gate 102 lines
verify_sandbox       All good: 13 visualisers, 3 tune models (747 draws, 249 readouts)
                     · 364 opening values reachable
verify_circuit_ui    All good: 78 driven keys and gestures, says 10 things, holds 15
                     kinds above their stamp floor
verify_tune_ui       All good: 423 hostile openings clamped, 462 targets, 105 paints at
                     5 widths, 270 drags, 493 mounts
verify_circuit_view  All good: 26 hostile coordinates · 424 mounts at 7 widths · 150
                     gestures · 390 published schematics
verify_progress      All good: 29 hostile documents · 12 accessibility contracts
verify_quiz          All good: 1366 questions in 252 quiz units · 1103 holes in 217
                     blanks units · 3360 per-option explanations · 6572 draws · 24.5%
verify_circuits      All good: 87 circuit exercises, 369 checks · 593 labels
verify_tune          All good: 21 tune units reachable and not pre-solved
verify_numeric       216 answers verified, 0 schematics with no check, 218 figure-only
verify_circuit_model All good: 1487 analyses, 84 refusals · 15 plots · 390 published
                     schematics, 369 with a DC point
verify_derivations   All good: 1294 steps across 46 courses
build.mjs            3 parts / 111 keys · 32/32 + 30/30 bundled · 13 visualisers ·
                     3 tune models · 15 symbols · emit.py's copies agree ·
                     both syntax checks clean · 62 payloads, 13129 KB — unchanged ·
                     inlined 14378 -> 14384 KB · shell 1220 -> 1226 KB, of 1536
```

Beyond the gates: all 323 size declarations and 36 tracking declarations classified from
source rather than sampled; the fifteen-value bottom band and its 1.034–1.053 ratios
computed rather than described; the 61 sub-11px rules listed by selector; **1990 lesson
numbers generated from `app.js`'s own two formats and `UNIT_SPEC` read out of `app.js`**,
which is what turned "the rail is a bit tight" into 596 rows drawing another lesson's
number; the id column's 50.0px-in-50px shown to be the reason the floor could not be raised
in one edit; the topbar's two type inputs checked to be on-ramp **before** the ramp was
chosen, so a whole-file type change moved neither 204.6 nor 86.4; all 7 fixed boxes on the
raised tier checked individually; all 8 relative sizes resolved against their real parents;
and the new gate run against **16 mutations — 15 it had to reject and one it had to pass** —
which is the run that found the suite was scoring one of them on the wrong check.

---
