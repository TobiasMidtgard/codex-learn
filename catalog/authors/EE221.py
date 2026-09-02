"""EE221 — Measurement and Instrumentation.

Second year. It assumes the first-year circuits sequence: DC analysis, AC steady
state, phasors and impedance, complex numbers and calculus, and enough Python to
write a function. It assumes nothing above that.

Authoring rules, as for every course module:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number was produced by running the code, not assumed
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it to the reference drawing
  * sandbox notices were written after reading the visualiser's source in
    src/studio.js, and describe what that code actually draws at those values

The four circuit exercises were run through src/circuit.js while being written:
the module 2 reference gives 9.900990 V at the tip, 0.990099 V at the probe and
990.099 nA out of the source; the module 3 reference holds the ratio at 0.100000
at 100 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz and 10 MHz, where the uncompensated
start falls to 0.0008842 at 1 MHz. The module 7 reference leaves the probed node at
0.005000 V where the unfixed circuit has it at 0.405000 V, with 2.000 A still in the
0.2 ohm of shared ground; the module 8 reference reads 4.096 mV where the uncompensated
loop reads 3.096 mV, with all three sources carrying the same 4.096 nA.
"""

COURSE = {
    "id": "EE221",
    "title": "Measurement and Instrumentation",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE102"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 120,
    "icon": "▤",
    "summary": (
        "Every measurement changes the thing it measures, and every instrument has a "
        "floor below which it is inventing digits. This course is about the gap between "
        "the number on the display and the quantity in the circuit: what the meter's "
        "input resistance did to the node, what the probe's capacitance did to the edge, "
        "what the amplifier's noise did to the last two digits, and what any of it "
        "entitles you to claim. It ends where a laboratory notebook should end, with a "
        "value, an uncertainty, and a statement of where that uncertainty came from."
    ),
    "outcomes": [
        "Predict the loading error an instrument of stated input impedance imposes on a node of stated Thévenin impedance, at DC and at frequency, and correct for it.",
        "Explain what a ×10 probe is made of, why it needs compensating, and what an uncompensated or badly grounded probe does to a fast edge.",
        "Convert between bandwidth and rise time, and separate the instrument's contribution from the signal's in a measured edge.",
        "Design a Wheatstone bridge for a resistive sensor, choosing an excitation that trades signal against self-heating, and account for the bridge's own nonlinearity.",
        "Distinguish random from systematic error, use averaging where it helps, and report a result as a value with a combined standard uncertainty and a stated coverage factor.",
        "Read an instrument specification of the form \u00b1(% of reading + % of range), turn it into an uncertainty in volts, and say what a traceable calibration certificate does and does not guarantee.",
        "Explain how a dual-slope converter's result becomes independent of its own resistor, capacitor and clock, why integrating over a whole number of line cycles rejects mains interference, and what is left when the line frequency is not what the aperture assumed.",
        "Separate common-mode from differential-mode interference, size the error that a stated CMRR and a stated source imbalance leave behind, and wire a measurement so that a shared ground conductor is not part of the signal path.",
        "Compensate a thermocouple's cold junction, invert a thermistor's \u03b2 model, judge a calibration fit by its residuals, and say how long an instrument of known time constant must be left alone before its reading may be believed.",
        "Derive what negative feedback does to an operational amplifier's gain, input current and output impedance, and use a follower to read a divider chain that no achievable input resistance could have read.",
        "Show that a difference amplifier's common-mode rejection is set by the match between two resistor ratios rather than by the amplifier, size the rejection a stated tolerance leaves at a stated gain, and say what an instrumentation amplifier's two input buffers buy that a bare difference stage cannot.",
    ],
    "assessment": (
        "Nine quizzes, six circuits drawn and measured in the schematic editor, six "
        "guided derivations and five Python labs checked by execution, together with "
        "shorter work \u2014 a reading, two slider designs, two numerical problems, a symbol "
        "drill and a fill-in \u2014 ending in a capstone that takes one bench measurement "
        "from raw readings to a reported temperature with a full uncertainty budget."
    ),
    "reading": [
        "*The Art of Electronics*, Horowitz & Hill — appendix on oscilloscopes, and section 8.1 on noise.",
        "*Measurement, Instrumentation and Sensors Handbook*, Webster — chapters on bridge circuits and on strain gauges.",
        "*Evaluation of measurement data — Guide to the expression of uncertainty in measurement*, JCGM 100:2008, freely available from the BIPM. Sections 3 and 4 are the whole of module 10 in twelve pages.",
        "Tektronix, *ABCs of Probes*, primer 60W-6053. Trade literature, and the clearest account of compensation in print.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "What a reading is allowed to claim",
            "summary": "Every measurement is a comparison, and the thing you are comparing against is at the far end of a chain of other comparisons. What the chain costs you is printed on the data sheet, in a notation worth learning to read.",
            "concepts": [
                "The volt is realised from the Josephson effect: a junction irradiated at frequency $f$ steps in voltage by $fh/2e$, and since 2019 both $h$ and $e$ have been defined constants. The unit is therefore exact by construction, and the only question left is how well your instrument is tied to it.",
                "That tie is the *traceability chain* — your meter against a calibration laboratory's transfer standard, that standard against a national one, the national one against the realisation. Each link carries a certificate stating an uncertainty and a coverage factor, and the uncertainties combine in quadrature down the chain. Traceability is a documented chain, not a sticker.",
                "Accuracy, precision and resolution are three different quantities. Accuracy is closeness to the true value, precision is repeatability, resolution is the smallest change the display can show. A 6½-digit meter resolves about one part in $10^6$ and is specified to perhaps 35 parts in $10^6$; the difference between those two numbers is where most laboratory arguments live.",
                "Calibration is a *comparison* and produces numbers. Adjustment is a *change* and produces a different instrument. A certificate reading “10.00021 V displayed for 10.00000 V applied” is more useful than an adjustment, because a known correction can be subtracted while an adjustment's residual cannot.",
                "Specifications read ±(a% of reading + b% of range), or ±(a% of reading + n counts). The first term follows the signal and the second does not, so the same voltage measured near the bottom of a range is far worse than the same voltage near the top of a smaller one — and every specification is conditional on a temperature band, a warm-up, and a time since calibration.",
            ],
            "read": {
                "title": "Two meters, one reference, and the brackets on the data sheet",
                "minutes": 14,
                "body": r'''
Two bench multimeters sit side by side, their leads clipped to the same solid-state
10 V reference. Both are 6½-digit instruments, both were calibrated inside the last
twelve months, neither has been dropped. Watch them settle.

```text
  left meter     10.000 21 V
  right meter     9.999 84 V
```

They disagree by 370 µV, which is 37 parts per million of the reading. Nothing is
broken. Both meters are inside their published specifications, both certificates are
valid, and between them they are showing you twelve digits of which the last two on
each display cannot both be meaningful.

The useful question is not which one to believe. It is what either of them was
entitled to claim before you looked.

## The last digit is a step, not a promise

Behind that display is a converter that counts. A 1 200 000-count instrument on its
10 V range runs to 12.00000 V, so one count is $12/1\,200\,000 = 10$ µV. That is the
*resolution*: the smallest change the display is able to show. It is a property of the
counter and of nothing else.

Take ten readings from the left meter and they come back 10.000 21, 10.000 21,
10.000 22, 10.000 21, 10.000 22 and so on — a spread of about one count. That is the
*precision*: the repeatability, and it is genuinely good. Neither number says anything
at all about where the reading sits relative to the volt, which is *accuracy*, and no
amount of staring at the display will produce it. This is the whole reason calibration
exists as a separate activity from measurement: the information you need is not
available from inside the instrument.

## Two mechanisms, and therefore two terms

A meter takes your voltage and does two things to it before the counter sees it. It
multiplies it by a gain, set by a resistor chain and a reference, and it adds an
offset, contributed by an amplifier whose two inputs are not quite identical and by
whatever thermal emfs the input connectors are generating that afternoon. Write that
down as it is:

$$V_{disp} = G\,V_{in} + V_{os}$$

Nominally $G = 1$ and $V_{os} = 0$, and neither is exact. Put $G = 1 + g$ and subtract:

$$V_{disp} - V_{in} = g\,V_{in} + V_{os}$$

The error has fallen into two pieces of different character. The first, $g V_{in}$, is
proportional to the signal — a 20 ppm gain error is 20 ppm of whatever you are
measuring, at any level. The second, $V_{os}$, is a fixed number of volts and knows
nothing about the signal at all; it is a property of the analogue front end that the
range switch selected, and so it scales with the *range* rather than with the reading.
Write it as a fraction $b$ of the range's full scale $V_{rng}$, bound the gain error
by $a$, and the worst case is

$$|V_{disp} - V_{in}| \le a\,V_{in} + b\,V_{rng}$$

That is the bracket on the data sheet — $\pm(a\,\text{% of reading} + b\,\text{% of
range})$ — and it is not a convention somebody chose. It is the shape the error has
because there are two mechanisms, one of which scales and one of which does not.

## Working one specification all the way down a range

Take the left meter: $\pm(0.0035\,\text{% of reading} + 0.0005\,\text{% of range})$,
one year after calibration, over 23 ± 5 °C. In parts per million that is 35 ppm of
reading plus 5 ppm of range, which is how the same sentence appears on the next data
sheet you pick up.

```python
def allowed(reading, full_scale, pct_rdg, pct_rng):
    """The bracket, in volts: a fraction of the reading plus a fraction of the range."""
    return pct_rdg / 100.0 * reading + pct_rng / 100.0 * full_scale


for reading, full_scale in [(10.0, 10.0), (5.0, 10.0), (0.5, 10.0),
                            (0.5, 1.0), (0.1, 10.0)]:
    u = allowed(reading, full_scale, 0.0035, 0.0005)
    print("%6.3f V on the %4.1f V range: %7.1f uV = %7.1f ppm of reading"
          % (reading, full_scale, u * 1e6, u / reading * 1e6))
```

```text
10.000 V on the 10.0 V range:   400.0 uV =    40.0 ppm of reading
 5.000 V on the 10.0 V range:   225.0 uV =    45.0 ppm of reading
 0.500 V on the 10.0 V range:    67.5 uV =   135.0 ppm of reading
 0.500 V on the  1.0 V range:    22.5 uV =    45.0 ppm of reading
 0.100 V on the 10.0 V range:    53.5 uV =   535.0 ppm of reading
```

Read the last column down. At the top of the range this is a 40 ppm instrument. At a
tenth of the range it is a 535 ppm instrument — fifteen times worse, on the same
meter, on the same afternoon, with nothing changed but the size of the signal. The
range term did not move; it was 50 µV in every one of those rows and it is 50 µV when
the input is shorted.

Compare the third and fourth rows. Same voltage, same meter, one range apart:
67.5 µV against 22.5 µV, three times better for pressing a button. That is what an
autoranging meter is doing when it drops a range as soon as the reading will fit, and
it is the one habit worth acquiring from this page.

Now go back to the two meters on the reference. Each is allowed 400 µV at 10 V. They
differ by 370 µV. Two instruments both behaving to specification can disagree by up to
800 µV, and these two are comfortably inside that. There was never a contradiction to
resolve — the display offered six digits and the specification only ever underwrote
four and a half.

## What the reference itself is standing on

Neither meter is the authority here; the reference is, and it is not the authority
either. Since 2019 the volt has been realised from the Josephson effect, a junction
irradiated at frequency $f$ stepping in voltage by $fh/2e$ with $h$ and $e$ both
defined constants. Between that and your bench is a chain of comparisons, each with a
certificate and an uncertainty of its own, and the uncertainties combine in quadrature:

```python
import math

links = [("your meter against the calibration laboratory", 8.0),
         ("the laboratory standard against the national one", 2.0),
         ("the national standard against the realisation", 0.5)]
total = 0.0
for name, u in links:
    print("%-48s %5.2f ppm" % (name, u))
    total += u * u
print("%-48s %5.2f ppm" % ("combined in quadrature", math.sqrt(total)))
print("%-48s %5.2f ppm" % ("the worst single link", max(u for _, u in links)))
```

```text
your meter against the calibration laboratory     8.00 ppm
the laboratory standard against the national one  2.00 ppm
the national standard against the realisation     0.50 ppm
combined in quadrature                            8.26 ppm
the worst single link                             8.00 ppm
```

The whole chain costs 8.26 ppm and its worst link costs 8.00 ppm. Quadrature is
brutal to small contributions: a term three times smaller than the leader adds 5% to
the total, and one sixteen times smaller adds nothing you can write down. That is
worth carrying into module 10, where it becomes the reason an uncertainty budget is
mostly about finding the one line that matters.

Notice also what the chain does *not* say. It is a documented sequence of comparisons,
each with a stated uncertainty. It does not promise that your meter meets its
published specification — a certificate reporting an out-of-tolerance instrument is a
perfectly valid traceable certificate. It does not promise the meter will still be
right next month; that is what the drift specification and the calibration interval
are for. Traceability is a chain, not a sticker.

## The mistake, and why it is tempting

The mistake is reading the display as the answer and the specification as paperwork.
It is tempting for an entirely rational reason: the display is the only quantitative
thing in the room, it updates five times a second, and it has six digits, while the
specification is three lines of small print in a PDF that nobody opened. Every
incentive in front of you points at the number.

It has a second half, which is worse. Faced with the 370 µV disagreement, the reflex
is to take more readings and average. The left meter averaged over a hundred readings
gives 10.000 213 with a standard error under a microvolt — and it is still 370 µV
away from the right meter, because the disagreement is not random. Averaging attacks
the scatter and leaves the offset exactly where it was. It buys resolution, never
accuracy, and the fastest way to quote six meaningless digits is to average your way
to them.

The third half, if a thing may have three, is the certificate. "The meter was
calibrated in March" is not a statement about accuracy. A certificate that says the
meter displayed 10.000 21 V for exactly 10.000 00 V applied is a *correction*: subtract
210 µV from readings near 10 V and carry the certificate's own uncertainty into your
budget. That is strictly better than having the meter adjusted, because a stated
correction has a stated uncertainty while the residual left behind by an adjustment
has none.

## Where this stops holding

The two-term bracket is a bound, not a distribution. It says the error lies somewhere
inside ±400 µV and says nothing about where. Turning it into a standard uncertainty
means assuming a shape — with nothing else stated, a rectangular one, giving
$400/\sqrt{3} = 231$ µV — and that assumption is a choice, made properly in module 10.
Treating the 400 µV as though it were a standard deviation and combining it in
quadrature with genuine standard uncertainties overstates the total by about 70%.

The bracket is also conditional in ways the bracket does not mention. Outside 23 ± 5 °C
a temperature coefficient applies, quoted per degree *outside* the band and not per
degree from 23 °C. The instrument has to have warmed up. The figures are for one year
since calibration, and the ninety-day column on the same data sheet is a different set
of numbers. A specification is a conditional promise, and a meter used in a plant room
is not being used under its conditions.

Finally, the linear model $V_{disp} = GV_{in} + V_{os}$ is a linearisation. A real
converter also has integral nonlinearity — a gain that varies slightly with where in
the range you are — and it does not appear as a third term because the manufacturer
folded it into the reading term when choosing $a$. The bracket is a bound over the
whole range, so it is loose in the middle of the range and tight at the ends.

## What this module asks you to do with it

Two exercises turn this into arithmetic you own. **What the data sheet is promising**
gives you the specification above and one reading and asks for the allowance in
microvolts; the whole of it is deciding which term takes the reading and which takes
the range, and the two answers people get wrong are the two ways of forgetting that
distinction.

**A ratio you can trust, at a current you can afford** goes at the other half of the
problem. A reference is one number, 10.000 V and nothing else; every voltage below it
has to be reached by a *ratio*, and a divider is a ratio standard. What makes it an
exercise rather than a division is that the resistor values are constrained twice
over: the ratio fixes their proportion, and their sum fixes the current, which decides
whether the pair runs warm enough to drift or cold enough for board leakage to join
the circuit. Both constraints have to hold at once, which is the ordinary condition of
instrument design and the reason the slider opens satisfying one of them.
''',
            },
            "quiz": {
                "title": "Chains, certificates and the small print",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A meter specified ±(0.005% of reading + 0.003% of range) is left on its 10 V range to measure 0.100 V. Which term dominates, and by how much?",
                        "opts": [
                            "the reading term, at 5 µV",
                            "the range term, at 300 µV",
                            "they contribute equally",
                            "the range term, at 30 µV",
                        ],
                        "a": 1,
                        "why": r'''
The reading term is $0.005\% \times 0.100 = 5$ µV and the range term is
$0.003\% \times 10 = 300$ µV, sixty times larger. Together they allow 305 µV on a
100 mV reading, which is 0.3% — a meter sold as a 0.005% instrument delivering 0.3%,
entirely because of the range it happens to be on. The range term is a fixed number of
volts once the range is chosen; it does not shrink when the signal does, and that is
the single most useful thing to know about reading a specification.
''',
                    },
                    {
                        "q": "Which is the reason an autoranging meter drops to a lower range as soon as the reading will fit?",
                        "opts": [
                            "the converter is more linear near the bottom of its input span",
                            "the fixed part of the specification is a fraction of the range, and the range just got smaller",
                            "the input resistance rises on the lower ranges",
                            "it reduces the burden voltage",
                        ],
                        "a": 1,
                        "why": r'''
The range term is a percentage of full scale, so stepping from the 10 V range to the
1 V range divides it by ten while the reading term is unchanged. Measuring 0.200 V on
a $\pm(0.0035\%\ \text{rdg} + 0.0005\%\ \text{rng})$ meter costs 7 + 50 = 57 µV on the
10 V range and 7 + 5 = 12 µV on the 1 V range: the same signal, the same meter, nearly
five times better. Input resistance and burden voltage are real effects too, but they
belong to the modules that follow and to the current function respectively, and neither
is what the autoranging logic is chasing.
''',
                    },
                    {
                        "q": "A source is truly 9.9950 V. A meter reads 10.0001, 10.0002, 10.0001, 10.0002 V. The instrument is:",
                        "opts": [
                            "accurate but not precise",
                            "precise but not accurate",
                            "both accurate and precise",
                            "neither accurate nor precise",
                        ],
                        "a": 1,
                        "why": r'''
The readings agree with each other to 10 ppm — 100 µV of spread on 10 V — and disagree
with the truth by 515 ppm, since 10.00015 − 9.9950 is 5.15 mV, or 0.05%.
That is precision without accuracy, and it is the ordinary condition of an instrument
that has drifted or was never calibrated: nothing about the readings themselves gives
it away, which is the whole reason calibration exists as a separate activity. Note
also that averaging these four readings improves nothing, for the reason the next
module gives — a fixed offset is not a random error.
''',
                    },
                    {
                        "q": "Your calibration certificate says the meter displayed 10.00021 V when exactly 10.00000 V was applied. What is the best use of that line?",
                        "opts": [
                            "nothing — the meter must be adjusted before it can be used",
                            "subtract 210 µV from readings near 10 V, and carry the certificate's own uncertainty into the budget",
                            "treat the 210 µV as a random error and average it away",
                            "ignore it, since 21 ppm is below anything a real measurement can resolve",
                        ],
                        "a": 1,
                        "why": r'''
A certificate is a set of corrections, and applying them is cheaper and better than
adjusting: the residual after an adjustment is unknown, whereas a stated correction has
a stated uncertainty of its own that goes straight into the budget. Averaging cannot
touch it — it is systematic. And 21 ppm is not below the resolution of a 6½-digit
meter, which resolves about 1 ppm; that is exactly the gap between resolution and
accuracy. The one genuine caveat is that the correction is valid near 10 V, at the
certificate's temperature, and for as long as the drift specification says.
''',
                    },
                    {
                        "q": "What does a calibration traceable to a national metrology institute actually guarantee?",
                        "opts": [
                            "that the instrument meets its published specification",
                            "an unbroken chain of comparisons, each with a stated uncertainty, back to the realisation of the unit",
                            "that the instrument was adjusted at the institute",
                            "that the instrument will not drift before its next calibration",
                        ],
                        "a": 1,
                        "why": r'''
Traceability is a property of the *chain*, not of the instrument: an unbroken sequence
of documented comparisons, each with its own uncertainty, ending at a realisation of
the SI unit. It says nothing about whether your meter still meets its specification
tomorrow — that is what the drift specification and the calibration interval are for —
and nothing about where the adjustment was done. A certificate that reports a
measurement outside the published specification is still a perfectly valid traceable
certificate; it just tells you the instrument is out of tolerance.
''',
                    },
                    {
                        "q": "A meter is specified ±0.0035% of reading over 23 ± 5 °C, with an additional 0.0005% of reading per °C outside that band. You use it at 38 °C to read 10 V. The specified uncertainty becomes:",
                        "opts": [
                            "unchanged — a specification is a specification",
                            "about 2.4 times larger, 850 µV instead of 350 µV",
                            "exactly double, 700 µV",
                            "about 15 times larger",
                        ],
                        "a": 1,
                        "why": r'''
38 °C is 10 °C outside the top of the band, so the extra allowance is
$10 \times 0.0005\% = 0.005\%$ of reading, on top of the 0.0035% inside the band: 0.0085%
of 10 V, which is 850 µV against the 350 µV the same meter would be allowed in a
23 °C laboratory. The temperature coefficient is quoted per degree *outside* the band,
not per degree from 23 °C — a distinction worth reading carefully, since taking it from
23 °C would give 15 °C of excursion and 1.10 mV. The practical lesson is that a
specification is a conditional statement, and a meter used in a plant room is not being
used under its conditions.
''',
                    },
                ],
            },
            "tune": {
                "title": "A ratio you can trust, at a current you can afford",
                "minutes": 10,
                "brief": r'''
A voltage reference is a single number: 10.000 V and nothing else. To calibrate
anything below that you need a *ratio* — a divider whose output is a known fraction of
its input — and the ratio, not the resistors, is what has to be right.

Two things pull against each other. The ratio is set by $R_2/(R_1+R_2)$ and cares
about nothing but the proportion, so a 9:1 pair of any size gives 1.000 V from 10.000 V.
The **current** is set by the sum $R_1+R_2$, and it decides two other things you cannot
see on the readout:

- too much current and the resistors warm themselves. A metal-film resistor drifts by
  tens of parts per million per kelvin, and self-heating is a temperature rise
  proportional to the power it dissipates, so a divider that runs warm has a ratio that
  depends on how long it has been switched on.
- too little current and the leakage across the board, the meter's own bias current and
  the surface resistance of a slightly dirty PCB start to matter. Below a microamp or
  so the divider is no longer only the two resistors you drew.

Land in the window between them.
''',
                "prompt": "Take 10.000 V down to 1.000 V, with the divider drawing between 0.20 and 0.60 mA.",
                "note": "The dashed line is the 1.000 V target. Both constraints have to hold at once, and the opening position already satisfies one of them.",
                "model": "divider",
                "initial": {"r1": 9000, "r2": 1000},
                "constants": {"vin": 10},
                "plotKey": "vout",
                "constraints": [
                    {"k": "vout", "label": "Vout = 1.000 V ± 0.005", "eq": 1.0, "tol": 0.005},
                    {"k": "i", "label": "total current between 0.20 and 0.60 mA", "min": 0.20, "max": 0.60},
                ],
            },
            "numeric": {
                "title": "What the data sheet is promising",
                "minutes": 7,
                "brief": r'''
The whole of a specification is in the brackets. Two terms, added, one of which follows
the reading and one of which follows the range — and the arithmetic below is the one
you will do more often than any other in a laboratory.
''',
                "prompt": "What uncertainty does the specification allow on that reading?",
                "note": "Give the answer in microvolts.",
                "figure": "A bench multimeter's DC voltage function is specified, one year after calibration and "
                          "over 23 ± 5 °C, as ±(0.0035% of reading + 0.0005% of range). It is warmed up, "
                          "sitting in a 24 °C laboratory, set to its 10 V range, and displaying 5.00000 V.",
                "given": [
                    {"label": "Reading term", "value": "0.0035% of reading"},
                    {"label": "Range term", "value": "0.0005% of range"},
                    {"label": "Range in use", "value": "10 V"},
                    {"label": "Displayed reading", "value": "5.00000 V"},
                ],
                "aside": "0.0035% is 35 parts per million, and 0.0005% is 5 parts per million. Working in ppm "
                         "saves a decimal point or two, and is how the same specification is written on the "
                         "next data sheet you pick up.",
                "answer": 225.0,
                "tol": 2.0,
                "unit": "µV",
                "hint": "The first term is a fraction of the 5 V on the display. The second is a fraction of the "
                        "10 V range, and does not know or care what the display says.",
                "wrong": "If you got 175, only the reading term was counted — the range term is there even "
                         "when the reading is zero. If you got 400, both percentages went onto the 10 V range; "
                         "only the second one belongs there.",
                "why": r'''
$0.0035\% \times 5.00000\ \text{V} = 175$ µV, $0.0005\% \times 10\ \text{V} = 50$ µV,
and the specification is the sum: **225 µV**, or 45 ppm of the reading.

Three things follow from those two numbers. The range term is 22% of the total here,
and it grows as a share of the total as the reading falls: at 0.5 V on the same range
the allowance is 17.5 + 50 = 67.5 µV, of which the range term is nearly three quarters,
and the meter that was a 35 ppm instrument at 5 V is a 135 ppm instrument at 0.5 V.
Second, this is a *limit*, not a standard uncertainty — converting it for a budget means
dividing by $\sqrt{3}$ if nothing else is stated, which the last module of the course
does properly. Third, none of it applies if the meter is outside 23 ± 5 °C, has not
warmed up, or was calibrated fourteen months ago; a specification is a conditional
promise and the conditions are not decoration.
''',
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "What the instrument does to the circuit",
            "summary": "A meter is a component you have added. The reading it gives is the reading of the circuit that now exists, not the one you drew.",
            "concepts": [
                "Any pair of terminals in a linear network looks, from outside, like one voltage source $V_{th}$ behind one resistance $R_{th}$. Measuring is what happens when you connect something across those two terminals.",
                "A voltmeter of input resistance $R_{in}$ reads $V_{th}R_{in}/(R_{th}+R_{in})$. The fractional error is $-R_{th}/(R_{th}+R_{in})$, and it is always negative: an attached instrument can only pull a node down.",
                "Loading error is *systematic*. Repeating the reading gives the same wrong answer, and averaging a thousand of them gives the same wrong answer to more decimal places.",
                "To hold the loading error below 1% you need $R_{in} \\ge 99R_{th}$. The familiar 10 MΩ of a digital multimeter is therefore honest up to a source resistance of about 100 kΩ, and no further.",
                "An ammeter goes *into* the loop rather than across it, and its shunt drops a burden voltage $IR_{shunt}$ which subtracts from the circuit's own supply. The current you read is the current that flows with the meter present.",
                "An oscilloscope input is 1 MΩ in parallel with 10–20 pF. A ×10 probe raises that to 10 MΩ and lowers the capacitance to about 10 pF, and charges you a factor of ten in signal for it.",
                "Input resistance is a DC figure. At 1 MHz a 15 pF input is an impedance of 10.6 kΩ, so an instrument that loads a 100 kΩ node by 0.1% at DC loads it by 90% at 1 MHz.",
                "Loading is correctable when $R_{th}$ is known: multiply the reading by $(1 + R_{th}/R_{in})$. It is a design error only when $R_{th}$ is unknown, which is most of the time.",
            ],
            "read": {
                "title": "The meter is a component, and you soldered it in",
                "minutes": 15,
                "body": r'''
Two 1 MΩ resistors in series across a 9 V battery. Nothing else on the board. Put a
digital multimeter on the junction between them and ask what it should read.

Half of 9 V is 4.500 V. The meter says **4.286 V**.

Both resistors measure 1.000 MΩ on the same meter. The battery measures 9.000 V on the
same meter. The arithmetic is not in dispute, and the reading is 214 mV — 4.8% — away
from it. Nothing here is faulty, and the meter is not lying: it is reporting, correctly,
the voltage at that junction *while the meter is attached to it*, which is not the
circuit you drew.

## The third resistor

The meter's input is a resistance to its own low terminal. On an ordinary bench
instrument it is 10 MΩ, and it is not optional — it is the top of the divider chain
that every range is tapped off. Clip it to the junction and there are now three
resistors on the board, not two.

Look at what the junction sees. Above it, 1 MΩ to the battery; below it, 1 MΩ to
ground; and now 10 MΩ to ground as well. Reduce the original network at those two
terminals the way any linear network reduces: an open-circuit voltage of 4.500 V behind
a resistance of $1\,\text{M} \parallel 1\,\text{M} = 500$ kΩ. The meter is a 10 MΩ
lower arm hung on a 4.500 V source with 500 kΩ in series. That is a voltage divider,
whether you meant to build one or not, and its output is

$$V_m = V_{th}\,\frac{R_{in}}{R_{th} + R_{in}} = 4.500 \times \frac{10}{10.5} = 4.286\,\text{V}$$

Subtract the true value and divide by it and the $V_{th}$ falls out of the expression
entirely:

$$\delta = \frac{V_m - V_{th}}{V_{th}} = \frac{R_{in}}{R_{th}+R_{in}} - 1
        = -\frac{R_{th}}{R_{th}+R_{in}}$$

Three things are contained in that line. The error is always negative — an attached
instrument can pull a node down and can never push it up. It does not depend on the
signal, so changing the battery to 12 V changes the reading and not the percentage.
And it is set by the ratio of the *source* resistance to the meter, not the other way
round, which is the direction people reverse.

```python
V_BATT, R_TOP, R_BOT, R_IN = 9.0, 1e6, 1e6, 10e6

v_th = V_BATT * R_BOT / (R_TOP + R_BOT)
r_th = R_TOP * R_BOT / (R_TOP + R_BOT)
v_m = v_th * R_IN / (r_th + R_IN)

print("unloaded midpoint      %.4f V" % v_th)
print("Thevenin resistance    %.0f ohm" % r_th)
print("what the meter reads   %.4f V" % v_m)
print("fractional error       %+.2f %%" % (100.0 * (v_m - v_th) / v_th))
print("corrected reading      %.4f V" % (v_m * (1.0 + r_th / R_IN)))
print("---")
for r in [1e3, 1e4, 1e5, 1e6, 1e7]:
    print("source %9.0f ohm into 10 M: %+8.3f %%" % (r, -100.0 * r / (r + R_IN)))
```

```text
unloaded midpoint      4.5000 V
Thevenin resistance    500000 ohm
what the meter reads   4.2857 V
fractional error       -4.76 %
corrected reading      4.5000 V
---
source      1000 ohm into 10 M:   -0.010 %
source     10000 ohm into 10 M:   -0.100 %
source    100000 ohm into 10 M:   -0.990 %
source   1000000 ohm into 10 M:   -9.091 %
source  10000000 ohm into 10 M:  -50.000 %
```

The fifth line is the way out when the source resistance is known. Rearranging
$V_m = V_{th}R_{in}/(R_{th}+R_{in})$ for $V_{th}$ gives

$$V_{th} = V_m\left(1 + \frac{R_{th}}{R_{in}}\right)$$

and multiplying 4.2857 by 1.05 returns 4.5000 exactly. The correction costs nothing and
is available whenever you can put a number on $R_{th}$ — which, on a divider you built
yourself, you can. On a node inside somebody else's design you cannot, and that is when
loading stops being an arithmetic nuisance and becomes a design error.

Read the sweep at the bottom. A 10 MΩ instrument is honest to 0.1% up to a source
resistance of about 10 kΩ and to 1% up to about 100 kΩ. Above that the reading is
worse in the second digit than the meter is in its sixth, and the 6½ digits on the
display are decoration.

## The same argument, turned inside out, is the ammeter

An ammeter does not go across the circuit; it goes *into* it. Break the loop, insert
the meter, and its shunt resistance $R_s$ is now in series with everything else. The
current that flows is no longer $V/R$ but $V/(R+R_s)$, and the meter honestly reports
the smaller current that its own presence created. The fractional error is

$$\frac{I_m - I}{I} = -\frac{R_s}{R + R_s}$$

which is the voltmeter expression with the roles of the two resistances exchanged: the
voltmeter wants $R_{in}$ enormous compared with the source, the ammeter wants $R_s$
tiny compared with the loop. One expression, two instruments, opposite requirements.

Data sheets quote the ammeter's side of it as a *burden voltage* — the volts the meter
develops across itself at full scale — because that is the number you can compare with
the supply the circuit had to work with.

```python
V, R_LOAD = 5.0, 47.0
i_true = V / R_LOAD
for r_s in [0.01, 0.1, 1.0, 10.0]:
    i = V / (R_LOAD + r_s)
    print("shunt %6.2f ohm: reads %8.4f mA against %8.4f mA, %+6.2f %%, burden %7.2f mV"
          % (r_s, i * 1e3, i_true * 1e3, 100.0 * (i - i_true) / i_true, i * r_s * 1e3))
```

```text
shunt   0.01 ohm: reads 106.3603 mA against 106.3830 mA,  -0.02 %, burden    1.06 mV
shunt   0.10 ohm: reads 106.1571 mA against 106.3830 mA,  -0.21 %, burden   10.62 mV
shunt   1.00 ohm: reads 104.1667 mA against 106.3830 mA,  -2.08 %, burden  104.17 mV
shunt  10.00 ohm: reads  87.7193 mA against 106.3830 mA, -17.54 %, burden  877.19 mV
```

The third row is an ordinary handheld meter on its milliamp range, and it has taken
104 mV out of a 5 V supply. On a 3.3 V rail that is 3%. The place it does real damage
is the row below: measuring the sleep current of a battery-powered board through the
microamp range, where the shunt is hundreds of ohms, can drop the rail far enough that
the board browns out and the current you are measuring is the current of a device that
is no longer running.

## The megohms on the front page are a DC number

The input is not a resistor. It is a resistor in parallel with a capacitance — 10 to
20 pF of amplifier, connector and cable on a scope input, and something similar inside
a meter. At DC the capacitor is absent and the front page is telling the truth. At
frequency it is the capacitor that does the loading, because its impedance falls as
$1/2\pi f C$ while the resistor stays where it is. The two are equal at

$$f = \frac{1}{2\pi R_{in}C_{in}}$$

which for 10 MΩ and 15 pF is 1.06 kHz. Above about a kilohertz, an instrument sold as
a 10 MΩ input is not a 10 MΩ input in any way that matters.

```text
at      1000 Hz the 15 pF alone is 10610329 ohm
at     10000 Hz the 15 pF alone is  1061033 ohm
at    100000 Hz the 15 pF alone is   106103 ohm
at   1000000 Hz the 15 pF alone is    10610 ohm
```

An instrument that loads a 100 kΩ node by 1% at DC loads the same node by about 90% at
1 MHz. This is the single most surprising line in the module, and it is the reason
module 3 exists.

## The mistake, and why it is tempting

The mistake is treating "high impedance" as a property that removes the instrument from
the circuit. It is tempting because the number is real, it is large, it is printed on
the front page of the data sheet, and it is correct — at DC, on that range, against a
source impedance the data sheet does not know. Ten megohms sounds like infinity right
up to the moment you put it on a 1 MΩ node, where it is a 9% error, or on a 10 kHz
signal, where the megohms have quietly become a hundred kilohms.

The second half of the mistake is the response to it. A loading error is *systematic*:
the same meter on the same node builds the same divider on every reading. Average a
thousand of them and you have the same wrong answer with a smaller standard error
attached to it, which is a worse situation than the one you started in, because now it
looks defensible. The only two exits are a larger $R_{in}$ or the correction above,
and the correction needs a number for $R_{th}$ that you are prepared to defend.

## Where this stops holding

Thévenin's theorem is a theorem about *linear* networks. A node behind a diode, a
saturating amplifier or a switching regulator does not reduce to one source and one
resistance, and the divider argument above says nothing about it — attaching a meter
there can change the circuit's operating point rather than merely scale its output.

The meter's input is not purely a resistance either, in a second way. It has an input
bias current, and a current flowing out of the instrument into a high-value source
develops a voltage in it that has nothing to do with the divider: 1 nA into 1 MΩ is
1 mV, and it does not scale with the signal, so it appears as an offset rather than as
a percentage. On some bench meters the input arrangement itself changes with range —
more than 10 GΩ on the 10 V range and below, and the plain 10 MΩ chain above — so
autoranging in the middle of a measurement can change the loading by three orders of
magnitude and the data sheet is where that is written down.

And the whole picture assumes two terminals, one of which is a perfect return. It is
not. Module 7 is about what happens when the low lead is a piece of copper shared with
somebody else, at which point the error is no longer a divider at all.

## What this module asks you to build

**The loading error, and the rule of 99** takes the algebra above and makes you produce
it, ending at the smallest input resistance that holds a given error: $R_{in} \ge
R_{th}(1-e)/e$, which at $e = 1\%$ is the factor of 99 the course refers to afterwards.

**A probe that costs the circuit a tenth of what a bare input would** is the answer to
the sweep table. A scope input is 1 MΩ, and on the 100 kΩ source in that exercise a
bare 1 MΩ input takes the node from 10 V to 9.09 V. You add one series resistor so
that the tip presents ten megohms instead of one and the attenuation is exactly 10:1 —
which is the entire content of a ×10 probe, apart from the capacitor module 3 makes
you add for the reason the last section gave.
''',
            },
            "quiz": {
                "title": "Loading, burden and what averaging cannot fix",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A node whose Thévenin resistance is 100 kΩ is measured with a 10 MΩ digital multimeter. The reading is low by about:",
                        "opts": ["0.01%", "0.1%", "1%", "10%"],
                        "a": 2,
                        "why": r'''
The error is $-R_{th}/(R_{th}+R_{in}) = -100\,\text{k}/10.1\,\text{M} = -0.99\%$, which
rounds to 1%. The useful shortcut is that for $R_{in} \gg R_{th}$ the error is simply
the ratio $R_{th}/R_{in}$, here one part in a hundred. Answering 0.1% is dividing by
the wrong one of the two resistances; the error is set by how large the *source*
resistance is compared with the meter, not the other way round.
''',
                    },
                    {
                        "q": "You take that same reading nine more times and average all ten. What happens to the 1% error?",
                        "opts": [
                            "nothing at all — every reading is wrong by the same amount",
                            "it falls by $\\sqrt{10}$, to about 0.3%",
                            "it falls by 10, to 0.1%",
                            "it becomes unpredictable",
                        ],
                        "a": 0,
                        "why": r'''
Nothing. Averaging attacks the *random* part of an error, and loading is not random:
the same meter on the same node makes the same divider every time. This is the single
most important distinction in the whole course, and the one that survives into every
laboratory you will ever work in — averaging buys you resolution, never accuracy. The
$\sqrt{N}$ answer is the right formula applied to the wrong kind of error, and it is
the reason people quote six digits of a measurement that is wrong in the second.
''',
                    },
                    {
                        "q": "A 5 V supply drives a 47 Ω load. You break the loop and insert an ammeter whose shunt is 1 Ω. What does it read?",
                        "opts": [
                            "106.4 mA, the current that flowed before",
                            "104.2 mA, because the meter's own resistance reduced the current",
                            "106.4 mA, but the true current has risen to 108 mA",
                            "5 mA, because the shunt carries the current instead",
                        ],
                        "a": 1,
                        "why": r'''
The loop is now 48 Ω, so $I = 5/48 = 104.2$ mA, and the meter honestly reports the
104.2 mA that is now flowing. The 2.1% error is the current-measurement twin of
voltage loading, and it is quoted on data sheets as the *burden voltage*: 104 mV
across that shunt, taken out of the 5 V the circuit had to work with. It matters most
where it is least expected — measuring the sleep current of a battery-powered board
through a 100 Ω shunt can stop the board working.
''',
                    },
                    {
                        "q": "You need the loading error on a 47 kΩ source to stay under 0.5%. What is the smallest acceptable instrument input resistance?",
                        "opts": ["470 kΩ", "4.7 MΩ", "23.5 MΩ", "9.4 MΩ"],
                        "a": 3,
                        "why": r'''
The condition is $R_{th}/(R_{th}+R_{in}) \le 0.005$, which rearranges to
$R_{in} \ge 199R_{th} = 9.35$ MΩ. The general rule is $R_{in} \ge (1/e - 1)R_{th}$ for a
fractional error $e$, which for 1% is the familiar factor of 99. Answering 4.7 MΩ is
the factor of 100 applied as though it were the requirement rather than roughly twice
it; a factor of 100 buys you 1%, not 0.5%.
''',
                    },
                    {
                        "q": "An oscilloscope input is 1 MΩ in parallel with 15 pF. What is the magnitude of its input impedance at 1 MHz?",
                        "opts": ["1 MΩ", "106 kΩ", "10.6 kΩ", "1.06 kΩ"],
                        "a": 2,
                        "why": r'''
At 1 MHz the capacitor's reactance is $1/(2\pi fC) = 10.6$ kΩ, which is so far below
1 MΩ that the resistor might as well not be there: the parallel combination is 10.6 kΩ
to three figures. The DC input resistance is a number for the data sheet's front page;
what actually loads a high-frequency node is the capacitance. Answering 1 MΩ is
reading the input as a resistance at all frequencies, which is exactly the assumption
that makes a probe surprise you.
''',
                    },
                    {
                        "q": "Which of these is reduced by averaging many readings?",
                        "opts": [
                            "the loading error of the meter's input resistance",
                            "the offset voltage of the meter's input amplifier",
                            "the calibration error of the meter's voltage reference",
                            "the thermal noise of the source resistance",
                        ],
                        "a": 3,
                        "why": r'''
Thermal noise is genuinely random and uncorrelated between readings, so averaging $N$
of them shrinks it by $\sqrt{N}$. The other three are fixed for the duration of the
measurement: loading is a divider, an offset is a constant added to every reading, and
a reference that is 0.02% high is 0.02% high all afternoon. Sorting your error sources
into these two boxes — random, reducible by repetition; systematic, reducible only by
correction or better equipment — is the whole method of module 10.
''',
                    },
                ],
            },
            "derive": {
                "title": "The loading error, and the rule of 99",
                "minutes": 12,
                "vars": ["V_m", "V_th", "R_th", "R_in", "delta", "e"],
                "brief": r'''
The node you want to measure is a Thévenin source: an ideal $V_{th}$ behind a
resistance $R_{th}$. Your voltmeter is a resistance $R_{in}$ to ground. Connect the
two and you have built a voltage divider, whether you meant to or not.

Derive the reading, the fractional error, and the rule that tells you when a meter is
good enough.
''',
                "steps": [
                    {
                        "prompt": "Write the reading $V_m$ that appears across the meter, in terms of $V_{th}$, $R_{th}$ and $R_{in}$.",
                        "given": "The meter's resistance is the lower arm of the divider.",
                        "answer": "\\frac{V_{th} R_{in}}{R_{th} + R_{in}}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "This is the ordinary divider result. The resistance you are measuring *across* goes on top.",
                        "deconstruct": [
                            "The current round the loop is $V_{th}/(R_{th}+R_{in})$.",
                            "The voltage across $R_{in}$ is that current times $R_{in}$.",
                        ],
                    },
                    {
                        "prompt": "The fractional error is $\\delta = (V_m - V_{th})/V_{th}$. Write $\\delta$ in terms of $R_{th}$ and $R_{in}$ alone.",
                        "given": "Substitute the $V_m$ you just wrote and simplify. $V_{th}$ must cancel.",
                        "answer": "-\\frac{R_{th}}{R_{th} + R_{in}}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Take the ratio first: $V_m/V_{th} = R_{in}/(R_{th}+R_{in})$. Then subtract one, over the common denominator.",
                        "deconstruct": [
                            "$V_m/V_{th} = R_{in}/(R_{th}+R_{in})$.",
                            "Subtracting 1 gives $(R_{in} - R_{th} - R_{in})/(R_{th}+R_{in})$.",
                            "The numerator collapses to $-R_{th}$.",
                        ],
                    },
                    {
                        "prompt": "You will accept a fractional error of magnitude $e$ at worst. Write the smallest acceptable $R_{in}$ in terms of $R_{th}$ and $e$.",
                        "given": "Set $R_{th}/(R_{th}+R_{in}) = e$ and solve for $R_{in}$.",
                        "answer": "\\frac{R_{th}(1 - e)}{e}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Cross-multiply to $R_{th} = e R_{th} + e R_{in}$, then collect the $R_{th}$ terms.",
                        "deconstruct": [
                            "$R_{th} = e(R_{th} + R_{in})$.",
                            "So $eR_{in} = R_{th} - eR_{th} = R_{th}(1-e)$.",
                            "Divide by $e$.",
                        ],
                    },
                ],
                "closing": r'''
Put $e = 0.01$ into the last line and it reads $R_{in} \ge 99R_{th}$ — the rule of 99,
which is worth carrying around. For $e = 0.001$ it is 999, and the approximation
$R_{in} \ge R_{th}/e$ is good to within the 1% or 0.1% you were arguing about anyway.

Notice what the second step tells you: $\delta$ contains no $V_{th}$. The loading error
is a fixed fraction of whatever the node was doing, so it cannot be spotted by looking
at the number on the display, and it does not go away when you change the signal. The
only two ways out are a bigger $R_{in}$ or the correction $V_{th} = V_m(1 + R_{th}/R_{in})$,
and the second one requires you to know $R_{th}$.
''',
            },
            "build": {
                "title": "A probe that costs the circuit a tenth of what a bare input would",
                "minutes": 25,
                "brief": r'''
The canvas holds a circuit under test — a 10 V source behind a **100 kΩ** output
resistance — and, well to the right of it, an oscilloscope input drawn as a **1 MΩ**
resistor to ground with the probe on top of it. The two halves are not joined.

Join them, but not with a wire.

A bare 1 MΩ input on a 100 kΩ node is a divider: the node collapses from 10 V to
9.09 V, and the scope faithfully displays the 9.09 V that now exists. Your job is to
add **one series resistor** between the circuit and the scope input so that

- the tip of the probe presents at least 9.5 MΩ to the circuit, so the node under test
  sags by about 1% instead of 9%,
- the attenuation from the tip to the scope input is **10.0:1**, so the reading can be
  multiplied by ten and mean something,
- the scope's own 1 MΩ input is left exactly as it is.

That is a ×10 probe, and there is nothing else inside one except the compensation you
will add in module 3.

## Working it out

Call the series resistor $R_1$ and the scope input $R_2 = 1$ MΩ. The attenuation from
tip to scope is $(R_1+R_2)/R_2$, and the resistance the circuit sees at the tip is
$R_1 + R_2$. Fix the attenuation first; the input resistance then follows without any
further choice, which is exactly why the ×10 convention exists.

## Drawing it

Place a resistor in the gap, wire its left pin to the free end of the 100 kΩ and its
right pin to the top of the 1 MΩ. Click the part to set its value; `9M` is understood.
The checks measure the finished circuit, so any layout that behaves correctly passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 100000},
                        {"id": "p3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 100000},
                        {"id": "p3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 15, "y": 5},
                        {"id": "p6", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 9000000},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 5], "b": [15, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [13, 5]},
                    ],
                },
                "checks": [
                    {"name": "the circuit under test is still a 10 V source behind 100 kΩ", "code": r'''
c.assert(c.count('V') === 1,
  'One source, please: the circuit under test. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 10, 0.001, 'the source of the circuit under test');
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1,
  'The 100 kΩ output resistance of the circuit under test must stay in series with ' +
  'the source — it is the reason this exercise is hard, not an obstacle to remove.');
'''},
                    {"name": "the scope's 1 MΩ input is untouched", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the current" means one thing.');
const i = Math.abs(cur[ids[0]]);
c.assert(i > 1e-12,
  'No current is flowing at all, so nothing is connected to the scope input yet.');
const rbot = c.vout() / i;
c.close(rbot, 1e6, 0.05,
  'the resistance measured from the probed node to ground — that is the scope input, ' +
  'and it is a given, not a design variable');
'''},
                    {"name": "the attenuation from tip to scope input is 10.0:1", "code": r'''
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
c.assert(srcs.length === 1, 'Use exactly one source.');
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1, 'The 100 kΩ source resistance must stay in series with the source.');
const tip = series[0].n1 === plus ? series[0].n2 : series[0].n1;
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(i > 1e-12, 'No current is flowing, so there is no attenuation to measure yet.');
const ratio = c.dc().v[tip] / c.vout();
c.assert(isFinite(ratio), 'The probed node is at 0 V, so the ratio is meaningless.');
c.close(ratio, 10, 0.02,
  'the attenuation from the probe tip to the scope input');
'''},
                    {"name": "the node under test barely notices the probe", "code": r'''
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1, 'The 100 kΩ source resistance must stay in series with the source.');
const tip = series[0].n1 === plus ? series[0].n2 : series[0].n1;
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(i > 1e-9,
  'Nothing is drawing current from the node under test, so it is not being measured at all.');
const vt = c.dc().v[tip];
c.assert(vt >= 9.85,
  'With the probe attached the node under test sits at ' + c.fmt(vt, 'V') +
  '. It was 10 V unloaded, and the specification allows it to sag by 1.5% at most.');
'''},
                    {"name": "the probe presents 10 MΩ, give or take a tenth", "code": r'''
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1, 'The 100 kΩ source resistance must stay in series with the source.');
const tip = series[0].n1 === plus ? series[0].n2 : series[0].n1;
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(i > 1e-12, 'No current flows into the probe, so it has no input resistance to measure.');
const rp = c.dc().v[tip] / i;
c.assert(rp >= 9e6 && rp <= 11e6,
  'The probe presents ' + c.fmt(rp, 'Ω') + ' at its tip. A ×10 probe on a 1 MΩ input ' +
  'is 10 MΩ by construction; anything else means the ratio or the scope input has been changed.');
'''},
                ],
                "hints": [
                    "The attenuation you want is 10, and the lower arm of the divider is the scope's 1 MΩ. Ten parts in total, one of them below the probe point: nine above it.",
                    "So the series resistor is 9 MΩ. Type `9M` into the value box — the editor understands the M, k, m, µ, n and p suffixes.",
                    "Wire the free end of the 100 kΩ to one pin of your resistor and the other pin to the top of the 1 MΩ. The probe already sits on the scope input node; leave it there.",
                    "Check yourself before running: 10 V across 100 kΩ + 9 MΩ + 1 MΩ is 990 nA, which puts 9.901 V at the tip and 0.9901 V at the scope. Multiply the reading by ten and you recover 9.901 V — exactly what the node is doing with the probe on it, and within 1% of the 10 V it had before you touched it.",
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Probes, compensation and rise time",
            "summary": "The resistors set the ratio at DC; the capacitors set it everywhere else. Getting them to agree is the whole of probe compensation.",
            "concepts": [
                "Every resistor in a probe has capacitance across it, wanted or not: the 9 MΩ has a few picofarads of its own, and the scope's 1 MΩ has 10–20 pF of input and cable.",
                "Each arm of the divider is therefore $R$ in parallel with $C$, of impedance $R/(1+j\\omega RC)$. The ratio is frequency independent only if the two arms have the same time constant.",
                "The compensation condition is $R_1C_1 = R_2C_2$. Satisfy it and the divider gives $R_2/(R_1+R_2)$ at every frequency, which is also $C_1/(C_1+C_2)$ — the resistive and capacitive dividers agree.",
                "Leave it unsatisfied and the probe is a filter. With $C_1 = 0$, a 9 MΩ/1 MΩ probe into 20 pF rolls off at $1/(2\\pi(R_1\\|R_2)C_2) = 8.8$ kHz: useless above the audio band.",
                "On a square wave, under-compensation ($R_1C_1 < R_2C_2$) rounds the top of each edge and the trace creeps up to the flat level; over-compensation spikes and settles back down. The trimmer in the probe body adjusts $C_1$ until the corners are square.",
                "A first-order system's 10–90% rise time and its −3 dB bandwidth are locked together: $t_r = \\ln(9)\\tau$ and $f_{3dB} = 1/(2\\pi\\tau)$, so $t_r f_{3dB} = \\ln(9)/2\\pi = 0.3497$, which everyone rounds to 0.35 and this course does too.",
                "Cascaded stages add rise times in quadrature: $t_{measured}^2 \\approx t_{signal}^2 + t_{scope}^2$. A 1 ns edge on a 350 MHz scope (1 ns of its own) displays as 1.41 ns, and reading 1.41 ns off the screen as though it were the signal is a 41% error.",
                "The probe's ground lead is an inductor — roughly 1 nH per millimetre — and with the tip capacitance it forms a resonant tank. Every fast edge rings it, and the ringing is on the screen, not in the circuit.",
            ],
            "read": {
                "title": "Two capacitors nobody drew, and the corner they round off",
                "minutes": 16,
                "body": r'''
On the front of every oscilloscope there is a small metal tab with a square wave on it,
labelled something like PROBE COMP: about a volt, about a kilohertz, and square to
within a few tens of nanoseconds. Clip a ×10 probe to it and look at the top of the
waveform.

On a probe that has never been adjusted you will see one of two things. Either the
corner is rounded and the top creeps upward across the next half millisecond, arriving
at the flat level shortly before the next edge; or the corner overshoots into a spike
and the top sags back down to the flat level from above. Turn the little trimmer in the
probe body with a plastic screwdriver and the shape moves between those two, passing
through square on the way.

The calibrator is not producing any of those shapes. Every one of them is manufactured
between the probe tip and the screen, by two capacitors that were never on the drawing.

## Where the capacitors come from

Module 2 finished with the probe as two resistors: 9 MΩ from the tip down to the probe
point and the scope's own 1 MΩ from there to ground, giving a tenth at the input and
ten megohms at the tip. That is the entire probe at DC, and it is the wrong circuit
everywhere else. A 9 MΩ resistor has a couple of picofarads across its own body. A
metre of probe cable has tens of picofarads. The scope input has 10 to 20 pF of
amplifier and connector. None of it is optional and none of it was chosen.

So each arm is a resistor in parallel with a capacitor, and a parallel $RC$ has
impedance

$$Z = \frac{R \cdot \frac{1}{j\omega C}}{R + \frac{1}{j\omega C}} = \frac{R}{1 + j\omega RC}$$

Write the divider with both arms in that form and clear the fractions by multiplying
top and bottom by $(1+j\omega R_1C_1)(1+j\omega R_2C_2)$:

$$\frac{Z_2}{Z_1+Z_2}
 = \frac{R_2\,(1 + j\omega R_1C_1)}{R_1\,(1 + j\omega R_2C_2) + R_2\,(1 + j\omega R_1C_1)}$$

Now look for the condition under which $\omega$ disappears. It cannot cancel term by
term — but if the two products are equal, $R_1C_1 = R_2C_2 = \tau$, then every bracket
in sight is the same $(1+j\omega\tau)$, it factors out of the top and out of both terms
of the bottom, and what is left is

$$\frac{R_2}{R_1+R_2}$$

at every frequency. That is the compensation condition, and it was not announced: it is
the one arrangement of four numbers that lets the frequency out of the expression.
Written the other way, $R_1C_1 = R_2C_2$ rearranges to $C_1/(C_1+C_2) = R_2/(R_1+R_2)$ —
the capacitive divider and the resistive divider give the same ratio, which is the same
statement wearing different clothes and is the more useful of the two when you are
choosing a part.

## What it costs to miss it

Set $C_1 = 0$ and the numerator's bracket is 1, so the denominator is
$R_1 + R_2 + j\omega R_1R_2C_2$, which factors as $(R_1+R_2)\left(1 + j\omega\,
\frac{R_1R_2}{R_1+R_2}C_2\right)$. The probe is the DC ratio followed by a single pole
at

$$f = \frac{1}{2\pi (R_1 \parallel R_2) C_2}$$

For a 9 MΩ/1 MΩ probe into 20 pF that is $1/(2\pi \times 900\,\text{k} \times 20\,
\text{pF}) = 8.8$ kHz. An instrument sold as a wideband probe has become an audio
low-pass filter.

```python
import math

R1, R2, C2 = 9e6, 1e6, 20e-12
rp = R1 * R2 / (R1 + R2)
print("R1 || R2 = %.0f ohm, uncompensated corner %.0f Hz"
      % (rp, 1.0 / (2 * math.pi * rp * C2)))


def ratio(f, c1):
    w = 2 * math.pi * f
    z1 = R1 / complex(1.0, w * R1 * c1)
    z2 = R2 / complex(1.0, w * R2 * C2)
    return abs(z2 / (z1 + z2))


for c1 in (0.0, 1.5e-12, 2.0e-12, 20e-12 / 9.0, 3.0e-12):
    print("C1 = %5.3f pF:  DC %.5f   10 kHz %.5f   1 MHz %.7f"
          % (c1 * 1e12, ratio(1e-6, c1), ratio(1e4, c1), ratio(1e6, c1)))
```

```text
R1 || R2 = 900000 ohm, uncompensated corner 8842 Hz
C1 = 0.000 pF:  DC 0.10000   10 kHz 0.06624   1 MHz 0.0008842
C1 = 1.500 pF:  DC 0.10000   10 kHz 0.08330   1 MHz 0.0697699
C1 = 2.000 pF:  DC 0.10000   10 kHz 0.09458   1 MHz 0.0909097
C1 = 2.222 pF:  DC 0.10000   10 kHz 0.10000   1 MHz 0.1000000
C1 = 3.000 pF:  DC 0.10000   10 kHz 0.12003   1 MHz 0.1304332
```

Read the DC column: it never moves. The resistors own DC and the trimmer cannot touch
it, which is why a badly compensated probe measures supply rails perfectly and lies
about everything with an edge in it. Read the 1 MHz column: the same probe delivers
anything from 0.00088 to 0.130 depending on a capacitor of two picofarads. And read the
fourth row — 20 pF divided by 9 is 2.222 pF, and the response is flat to seven figures.

## The picture on the screen, derived

The frequency table explains nothing about the shape of the corner, and the shape of
the corner is what you actually have to adjust. Take the two extremes of an edge.

At the instant the calibrator steps, the capacitors are the low-impedance path in each
arm and the resistors carry nothing worth counting: the divider is capacitive, and the
trace goes to $C_1/(C_1+C_2)$ of the step. Long afterwards the capacitors are charged
and pass no current at all: the divider is resistive, and the trace sits at
$R_2/(R_1+R_2)$. Between the two there is one time constant, and it is the one the pole
above already gave: $(R_1 \parallel R_2)(C_1+C_2)$.

So the trace jumps to the capacitive ratio and relaxes exponentially to the resistive
one. If $C_1$ is too small the jump falls short and the top creeps up; too large and it
overshoots and sags back. A square corner means the two ratios are already equal, which
is $R_1C_1 = R_2C_2$ arriving for the third time. You are adjusting a trimmer until an
exponential disappears from a step response.

```python
import math

R1, R2, C2, C1 = 9e6, 1e6, 20e-12, 1.5e-12
rp = R1 * R2 / (R1 + R2)
tau = rp * (C1 + C2)
start, end = C1 / (C1 + C2), R2 / (R1 + R2)
print("tau = %.2f us; the trace jumps to %.4f and ends at %.4f" % (tau * 1e6, start, end))
for t in (0.0, 10e-6, 20e-6, 50e-6, 100e-6):
    print("  t = %6.1f us: %.4f" % (t * 1e6, end + (start - end) * math.exp(-t / tau)))
```

```text
tau = 19.35 us; the trace jumps to 0.0698 and ends at 0.1000
  t =    0.0 us: 0.0698
  t =   10.0 us: 0.0820
  t =   20.0 us: 0.0892
  t =   50.0 us: 0.0977
  t =  100.0 us: 0.0998
```

That is a probe 0.7 pF short of compensation: 30% low at the corner, correct 100 µs
later. Now notice why the calibrator runs at a kilohertz. Its half period is 500 µs,
which is twenty-six of those time constants, so the trace has all the room it needs to
arrive and the defect appears as a *visible curve* at full amplitude. Put the same
probe on a 100 kHz square wave and the half period is 5 µs, a quarter of a time
constant: the trace never arrives, the amplitude is 30% low, and there is no curve on
the screen to warn you. The calibrator makes the fault visible precisely because it is
slow.

## Bandwidth and rise time are one number

The pole above is also where the two figures on a scope's front panel come from. A
first-order step response is $1-e^{-t/\tau}$, so it reaches 10% at $\tau\ln(10/9)$ and
90% at $\tau\ln 10$, and the 10–90% rise time is the difference:

$$t_r = \tau\ln 10 - \tau\ln\tfrac{10}{9} = \tau\ln 9 = 2.1972\,\tau$$

The −3 dB frequency of the same pole is $f_{3dB} = 1/2\pi\tau$. Multiply the two and
$\tau$ vanishes:

$$t_r\,f_{3dB} = \frac{\ln 9}{2\pi} = 0.3497$$

which everyone writes as 0.35. A 350 MHz oscilloscope has a rise time of 1.0 ns, and
that is not a separate specification — it is the same specification.

Two stages in cascade — the probe and the scope, or the signal and the instrument —
combine their rise times in quadrature, $t_{obs} = \sqrt{t_1^2+t_2^2}$.

```python
import math

for sig, inst in ((5e-9, 3.5e-9), (1e-9, 1e-9), (20e-9, 3.5e-9)):
    obs = math.sqrt(sig * sig + inst * inst)
    print("a %5.2f ns edge on a %4.2f ns instrument displays as %5.2f ns (%+5.1f %%)"
          % (sig * 1e9, inst * 1e9, obs * 1e9, 100.0 * (obs - sig) / sig))
```

```text
a  5.00 ns edge on a 3.50 ns instrument displays as  6.10 ns (+22.1 %)
a  1.00 ns edge on a 1.00 ns instrument displays as  1.41 ns (+41.4 %)
a 20.00 ns edge on a 3.50 ns instrument displays as 20.30 ns ( +1.5 %)
```

The third row is the working rule hidden in the first two: an instrument four or five
times faster than the edge contributes a per cent or two and can be forgotten, and one
of comparable speed is a co-author of the number on the screen.

## The mistake, and why it is tempting

Every scope has a rise-time measurement in its menu. It prints three digits, it updates
live, and it is a completely correct measurement — of the trace on the screen. Nothing
on that screen separates the signal's edge from the sum of the signal's edge and the
instrument's, and there is no cue that the separation is needed. Reading 6.10 ns off a
350 MHz scope and writing "the edge is 6.1 ns" in a notebook is the ordinary way this
goes wrong, and the true edge was 5.00 ns.

The other mistake is treating compensation as a factory setting. The trimmer is
matching $C_1$ to the input capacitance of *the channel it is plugged into*, and two
channels of the same instrument differ by a picofarad or two. Move a compensated probe
to the next channel and it is out again, which is why the calibration tab is on the
front panel rather than inside the case.

## Where the model stops holding

The quadrature rule is exact for Gaussian responses and approximate for everything
else. Two identical single poles in cascade actually give a 10–90% rise time of
$3.358\tau$, where quadrature predicts $\sqrt{2}\times 2.197\tau = 3.107\tau$ — 7.5%
low. Scope front ends are deliberately shaped so that the rule holds to a few per cent;
it is a convention that manufacturers design towards, not a theorem.

The 0.35 belongs to a single pole. An instrument with a flatter, multi-pole response
has a product nearer 0.40 or 0.45, and its data sheet quotes both figures rather than
letting you infer one from the other. Applying 0.35 to such a scope understates its own
rise time and therefore overstates the signal you extract.

The lumped two-arm model is itself a fiction above a few tens of megahertz. A metre of
probe cable is a transmission line, and a real ×10 probe is not a 9 MΩ resistor with
2.2 pF across it — it uses a deliberately lossy centre conductor and networks at both
ends whose job is to stop that line ringing. Soldering a 9 MΩ resistor to a length of
coax does not produce a usable probe.

And the divider contains no ground lead at all, which is where the remaining trouble
lives. A wire is about 1 nH per millimetre, so the 8 cm flying lead on a new probe is
roughly 80 nH; with 150 pF at the tip that is a tank resonating at
$1/(2\pi\sqrt{LC}) = 46$ MHz, and every fast edge rings it. Shorten the lead to 2 cm
and the same capacitance rings at 92 MHz and dies away sooner; keep the lead and drop
the tip capacitance to 20 pF and it rings at 126 MHz instead. None of that oscillation
is in the circuit under test, and none of it can be compensated away.

## What this module asks you to do

**The ring that lives in your ground lead** puts that tank on a slider. The visualiser
was written for a power switch, so read its loop inductance as the ground lead and its
device capacitance as the tip, and watch what 80 nH does to an edge that never
oscillated.

**Compensating the probe you just built** hands you the module 2 probe with the scope's
20 pF now drawn in, and asks for one capacitor that holds the ratio at 0.1 from 100 Hz
to 10 MHz. The whole of it is $R_2C_2 = 20$ µs and therefore $C_1 = 20\,\text{pF}/9$.

**Bandwidth, rise time, and what the scope added** turns the last two sections into five
functions, ending with the one that matters on a bench: given an edge you must measure
and an error you are willing to tolerate, what bandwidth do you have to buy.
''',
            },
            "quiz": {
                "title": "Trimmers, corners and the edge that was not there",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A ×10 probe reads supply rails perfectly but shows a rounded, creeping top on the 1 kHz calibrator square wave. What is wrong?",
                        "opts": [
                            "the 9 MΩ series resistor has drifted high, so the ratio is no longer ten to one",
                            "the probe's own compensation capacitance is below what it needs to be",
                            "the scope's input resistance has fallen and now loads the tip",
                            "the ground lead is too long and its inductance is rounding the corner",
                        ],
                        "a": 1,
                        "why": r'''
The resistors alone set the DC ratio, and the rails read correctly, so the resistors are
right — which rules out both a drifted 9 MΩ and a changed input resistance, since either
one would put the rails wrong first. What is left is the capacitive divider. A top that
starts low and creeps upward means the trace jumped to $C_1/(C_1+C_2)$ and had to climb
to $R_2/(R_1+R_2)$, so the capacitive ratio is the smaller of the two and $C_1$ is short
of the $C_2R_2/R_1$ it needs. Lead inductance is a genuine problem but not this one: it
rings at tens of megahertz and is finished within nanoseconds, while this defect lasts
tens of microseconds and has no oscillation in it.
''',
                    },
                    {
                        "q": "A 9 MΩ/1 MΩ probe with no compensation capacitor at all feeds a scope input of 20 pF. Above roughly what frequency does the ratio stop being a tenth?",
                        "opts": [
                            "884 Hz, the corner of the 9 MΩ arm working into the scope's 20 pF",
                            "8.8 kHz, the corner of 900 kΩ — the arms in parallel — into 20 pF",
                            "nowhere: two resistors divide the same way at every frequency",
                            "8.8 MHz, close to the bandwidth a probe like this is sold with",
                        ],
                        "a": 1,
                        "why": r'''
With $C_1 = 0$ the divider's denominator is $R_1+R_2+j\omega R_1R_2C_2$, which factors
into $(R_1+R_2)$ times $1 + j\omega(R_1\parallel R_2)C_2$: a single pole whose resistance
is the *parallel* combination, 900 kΩ, not either arm on its own. That puts the corner at
$1/(2\pi \times 900\,\text{k} \times 20\,\text{pF}) = 8.8$ kHz — an audio filter sold as a
wideband probe, and nowhere near the megahertz figure on its label. Taking the 9 MΩ alone
gives 884 Hz, a factor of ten out, and comes from picking an arm instead of asking what
resistance the capacitor actually discharges into. The answer that the ratio never rolls
off would be right if the arms were resistors, and the whole content of this module is
that they are not.
''',
                    },
                    {
                        "q": "Compensation is achieved when $R_1C_1 = R_2C_2$. What does that condition do to the divider?",
                        "opts": [
                            "it moves the pole of each arm well above the highest frequency of interest",
                            "it makes the capacitive divider give the resistive one's ratio",
                            "it cancels the capacitance, leaving two resistors",
                            "it puts the two arms in resonance at the frequency being measured",
                        ],
                        "a": 1,
                        "why": r'''
Rearranged, $R_1C_1 = R_2C_2$ is $C_1/(C_1+C_2) = R_2/(R_1+R_2)$: the two dividers
present in the circuit agree, so it no longer matters which one is carrying the signal
and the ratio is the same at every frequency. The capacitance has not gone anywhere —
each arm still has a pole, and the point is that the two poles are identical and cancel
between numerator and denominator. Nor has anything been pushed out of band: an
uncompensated probe has a pole at 8.8 kHz and a compensated one is flat to 10 MHz, which
no amount of moving a single pole achieves. Resonance needs an inductor, and there is
none in the divider.
''',
                    },
                    {
                        "q": "You measure an edge at 6.10 ns on an oscilloscope whose own rise time is 3.50 ns. What was the signal doing?",
                        "opts": [
                            "2.60 ns — subtract the instrument's rise time from the measurement",
                            "5.00 ns, from the square root of the difference of the squares",
                            "6.10 ns; the instrument is faster, so it is not a factor",
                            "9.60 ns — the instrument speeds up the edge it displays",
                        ],
                        "a": 1,
                        "why": r'''
Rise times add in quadrature, so they come apart the same way:
$\sqrt{6.10^2 - 3.50^2} = 5.00$ ns. Subtracting directly gives 2.60 ns, which is the
right instinct with the wrong arithmetic and is out by a factor of two here; adding
gives 9.60 ns, which has the sign of the effect backwards, since an instrument can only
make an edge look slower than it is. Believing the screen at 6.10 ns costs 22% — and
the reason to distrust it is the ratio: an instrument less than about four times faster
than the edge is a co-author of the number displayed.
''',
                    },
                    {
                        "q": "Why is the probe compensation output a 1 kHz square wave rather than a 100 kHz one?",
                        "opts": [
                            "a slower edge is easier for the calibrator circuit to produce accurately",
                            "at 1 kHz the trace reaches its final level, so the fault shows as a shape",
                            "1 kHz sits in the middle of the band a ×10 probe works in",
                            "the trimmer only affects frequencies below the probe's compensation corner",
                        ],
                        "a": 1,
                        "why": r'''
The relaxation between the capacitive and resistive ratios takes
$(R_1\parallel R_2)(C_1+C_2)$, about 20 µs. A 1 kHz half period is 500 µs — twenty-six
of those — so a badly compensated trace arrives at full amplitude and the error appears
as a visible curve at the corner. At 100 kHz the half period is 5 µs and the trace never
arrives: the amplitude is wrong and the corner looks fine, which is the fault hiding
rather than showing. The calibrator's own edge quality is not the point, and neither is
the middle of the band; the trimmer acts at every frequency, and there is no corner
below which it works and above which it does not.
''',
                    },
                    {
                        "q": "A fast edge shows 40 MHz ringing that dies away in about 120 ns. Replacing the 8 cm flying ground lead with a 2 cm spring tip changes it. To what, and why?",
                        "opts": [
                            "the ring is unchanged: it is genuinely there in the circuit",
                            "a faster ring that settles sooner, since the loop inductance fell",
                            "a slower ring, because the shorter lead has raised the tank's capacitance",
                            "no ring at all, as the tip now has a direct connection to the ground plane",
                        ],
                        "a": 1,
                        "why": r'''
A wire is roughly 1 nH per millimetre, so 80 mm of lead is about 80 nH and 20 mm is
about 20 nH. With the tip capacitance unchanged, $f = 1/(2\pi\sqrt{LC})$ rises by
$\sqrt{4} = 2$ and the disturbance is over in roughly a third of the time. The
capacitance is set by the tip and the input, not by the lead, so nothing about it went
up. Shortening the lead does not abolish the tank either — there is always some loop —
it makes it small enough and fast enough to sit outside the band you care about. And the
ring is not in the circuit under test: it is made by the probe, which is why changing
the probe changes it.
''',
                    },
                ],
            },
            "sandbox": {
                "title": "The ring that lives in your ground lead",
                "visualiser": "switching",
                "minutes": 10,
                "initial": {"ls": 80, "coss": 150, "dead": 0},
                "brief": r'''
This visualiser was written for a power switch, and its labels say so: a drain voltage
in green or amber, a device current in blue, and a dead time in nanoseconds. Read it
here as a probe instead. The tank it draws — an
inductance, a capacitance and a fast edge — is exactly the tank your probe makes, with
**loop inductance** standing for the ground lead and **device $C_{oss}$** standing for
the capacitance at the tip.

The trace is flat until 100 ns; that is the edge arriving. What happens after it is
what your screen shows you, and none of it is in the circuit you are measuring.

The two sliders that matter here are the inductance and the capacitance. The dead time
is the one control with no probe counterpart; leave it at 0 until the last notice.
''',
                "notice": [
                    "At the opening values — 80 nH of lead and 150 pF of tip, which is a 1× probe on the ordinary 8 cm flying ground lead — the trace falls at 100 ns and rings. The period is about 22 ns, so the ring is at $1/(2\\pi\\sqrt{LC}) = 46$ MHz, and it takes about 120 ns to fall to a twentieth of the step height. That is a 46 MHz oscillation printed on top of a step that never oscillated.",
                    "Look at the first swing below zero: it runs a little past the bottom gridline of the frame, which is drawn for a switching waveform rather than for this ring. The ring genuinely overshoots by most of the step height — that is the point, not a drawing error.",
                    "Take the capacitance down to 20 pF — the bottom of the slider, and the right order for a ×10 probe tip rather than the 150 pF of a bare 1× one. The ring speeds up to about 126 MHz (a period near 8 ns) and reaches that same twentieth in about 50 ns instead of 120. The *number* of visible cycles barely moves — about five and a half becomes about six and a half — because most of the damping in this model is a fixed fraction of the ring period; what you have bought is a disturbance that is finished sooner.",
                    "Put the capacitance back to 150 pF and cut the inductance from 80 nH to 20 nH — at the 1 nH per millimetre of the concepts above, an 8 cm ground lead replaced by a 2 cm one. The frequency doubles to 92 MHz and the ring is down to that twentieth in about 70 ns. Nothing about the scope changed. This is why the little spring-clip ground tip exists.",
                    "Finally, raise the dead time. With 80 nH and 150 pF the visualiser computes a quarter-period of 5.4 ns, and somewhere between the 5 ns and 10 ns settings the whole picture changes: the trace switches colour, falls once as a smooth quarter-cosine to zero and stays there, and the blue current becomes a 60 ns ramp. That is the visualiser's soft-switching branch, and it is a power-electronics result with no probe counterpart — a probe has nothing that can hold the edge off until the tank has finished swinging. It is worth one look as a picture of what a ring-free edge would be, then put the slider back to 0.",
                ],
            },
            "build": {
                "title": "Compensating the probe you just built",
                "minutes": 25,
                "brief": r'''
Here is the same ×10 probe, now with the parts nobody draws: the scope's input
capacitance, **20 pF**, sits across its 1 MΩ input, and the source is an ideal 1 V
signal generator with no output resistance so that the probe's own behaviour is all
that is on show.

Run the frequency response as it stands and you will find a divider that gives 0.1 at
DC, 0.0662 at 10 kHz and 0.00088 at 1 MHz. The resistors set the ratio at DC; above a
few kilohertz the 20 pF has taken over and there is nothing above the probe point to
balance it.

Add **one capacitor** so that the ratio is 0.1 at every frequency from 100 Hz to
10 MHz.

## What you are solving

Each arm is a resistor in parallel with a capacitor, of impedance $R/(1+j\omega RC)$.
Write the divider ratio with both arms in that form and you will find the $\omega$
cancels out of the whole expression exactly when $R_1C_1 = R_2C_2$. That is the only
condition; everything else about compensation follows from it.

The scope's 20 pF is fixed — it is inside the instrument. So is the 9 MΩ and the
1 MΩ. There is exactly one unknown.

## Drawing it

A capacitor placed above the 9 MΩ with a wire down to each of its pins puts the two in
parallel. `2.22p` is understood by the value box, and so is `2.222e-12`.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 9},
                        {"id": "p5", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 2e-11},
                        {"id": "p6", "kind": "GND", "x": 15, "y": 9},
                        {"id": "p7", "kind": "OUT", "x": 17, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [12, 5]},
                        {"a": [12, 5], "b": [15, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [15, 7], "b": [15, 9]},
                        {"a": [15, 5], "b": [17, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 9},
                        {"id": "p5", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 2e-11},
                        {"id": "p6", "kind": "GND", "x": 15, "y": 9},
                        {"id": "p7", "kind": "OUT", "x": 17, "y": 5},
                        {"id": "p8", "kind": "C", "x": 8, "y": 2, "rot": 0, "value": 2.2222222222222223e-12},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [12, 5]},
                        {"a": [12, 5], "b": [15, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [15, 7], "b": [15, 9]},
                        {"a": [15, 5], "b": [17, 5]},
                        {"a": [7, 2], "b": [7, 5]},
                        {"a": [9, 2], "b": [9, 5]},
                    ],
                },
                "checks": [
                    {"name": "the scope input is still 1 MΩ in parallel with 20 pF", "code": r'''
const out = c.outNode();
function across(kind, value, tol) {
  return c.net.parts.some(function (p) {
    return p.kind === kind && Math.abs(p.value - value) <= tol &&
      ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
  });
}
c.assert(across('R', 1e6, 1e4),
  'The 1 MΩ scope input must still run from the probed node to ground.');
c.assert(across('C', 20e-12, 1e-12),
  'The 20 pF input capacitance must still run from the probed node to ground. It is ' +
  'inside the instrument; compensating a probe means balancing it, not deleting it.');
'''},
                    {"name": "the ratio is still a tenth at DC", "code": r'''
c.close(c.vout() / c.values('V')[0], 0.1, 0.02,
  'the DC ratio — the resistors alone decide this one, and it was already right');
'''},
                    {"name": "the ratio is a tenth at 1 MHz as well", "code": r'''
c.close(c.gain(1e6), 0.1, 0.03,
  'the ratio at 1 MHz, where the capacitors alone decide it');
'''},
                    {"name": "and everywhere between: flat from 100 Hz to 10 MHz", "code": r'''
const fs = [100, 1e3, 1e4, 1e5, 1e6, 1e7];
const gs = fs.map(function (f) { return c.gain(f); });
const hi = Math.max.apply(null, gs);
const lo = Math.min.apply(null, gs);
c.assert(lo > 0, 'The response has collapsed to zero somewhere in the band.');
c.assert(hi / lo <= 1.03,
  'The ratio varies by ' + ((hi / lo - 1) * 100).toFixed(1) + '% across the band ' +
  '(from ' + lo.toPrecision(3) + ' to ' + hi.toPrecision(3) + '). Compensation means ' +
  'the two arms share one time constant, so nothing is left for frequency to change.');
'''},
                    {"name": "the phase shift is gone too", "code": r'''
const ph = c.phase(1e5);
c.assert(Math.abs(ph) <= 3,
  'At 100 kHz the probe shifts the phase by ' + ph.toFixed(1) + '°. A compensated ' +
  'divider is a pure real ratio: no amplitude change with frequency and no phase shift.');
'''},
                ],
                "hints": [
                    "Write the two arm impedances as $R_1/(1+j\\omega R_1C_1)$ and $R_2/(1+j\\omega R_2C_2)$ and form the divider ratio $Z_2/(Z_1+Z_2)$.",
                    "The ratio loses its frequency dependence exactly when $R_1C_1 = R_2C_2$. Everything else is arithmetic.",
                    "$R_2C_2 = 10^6 \\times 20\\,\\text{pF} = 20$ µs. Your capacitor has to make $9\\,\\text{M}\\Omega \\times C_1$ come to the same 20 µs.",
                    "That is $C_1 = 20\\,\\text{pF}/9 = 2.22$ pF. Notice it is the capacitive divider $C_1/(C_1+C_2) = 2.22/22.2 = 0.1$ — the same tenth the resistors give.",
                ],
            },
            "lab": {
                "title": "Bandwidth, rise time, and what the scope added",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Five functions, all one-liners once you have the two relations straight, and together
they answer the question every fast measurement asks: is that edge real?

- `rise_time(bandwidth_hz)` — the 10–90% rise time of a first-order system of that
  bandwidth. Use $t_r f_{3dB} = 0.35$.
- `bandwidth(rise_s)` — the same relation the other way round.
- `observed_rise(times)` — several stages in cascade, each with its own rise time,
  combine in quadrature: the result is the square root of the sum of the squares.
- `signal_rise(measured, instrument)` — undo that combination to recover the signal's
  own rise time from what the screen showed. If the measured edge is not slower than
  the instrument's own, the measurement is impossible rather than merely difficult, so
  raise a `ValueError` in that case.
- `bandwidth_needed(edge_s, max_error)` — the instrument bandwidth required so that a
  signal edge of `edge_s` is displayed no more than a fraction `max_error` too slow.
  Set $t_{obs} = t_{sig}\sqrt{1+(t_{inst}/t_{sig})^2} \le t_{sig}(1+e)$, solve for the
  largest acceptable $t_{inst}$, and convert that to a bandwidth.

Import `math` and use `math.sqrt`. Nothing here needs NumPy.
''',
                "files": [{"name": "main.py", "content": r'''
"""Bandwidth and rise time: what the instrument added to the edge."""

import math

BW_RISE_PRODUCT = 0.35  # ln(9)/(2 pi) = 0.3497, rounded as everyone rounds it


def rise_time(bandwidth_hz):
    """10-90% rise time of a first-order system of this bandwidth, in seconds."""
    # TODO: the product of bandwidth and rise time is BW_RISE_PRODUCT.
    return 0.0


def bandwidth(rise_s):
    """The -3 dB bandwidth implied by this 10-90% rise time, in hertz."""
    # TODO: the same relation, rearranged.
    return 0.0


def observed_rise(times):
    """Rise time seen when stages with these rise times are cascaded."""
    # TODO: square each one, add them, take the square root.
    return 0.0


def signal_rise(measured, instrument):
    """The signal's own rise time, given what was measured and what the
    instrument contributes. Raise ValueError if the measurement is impossible."""
    # TODO: invert observed_rise for two stages, after checking it can be inverted.
    return 0.0


def bandwidth_needed(edge_s, max_error):
    """Instrument bandwidth that displays an edge of edge_s no more than a
    fraction max_error too slow."""
    # TODO: the allowed instrument rise time is edge_s * sqrt((1 + e)**2 - 1).
    return 0.0


if __name__ == "__main__":
    print("a 100 MHz scope rises in", rise_time(100e6), "s")
    print("a 1 ns edge needs about", bandwidth(1e-9) / 1e6, "MHz")
    print("1 ns signal on a 1 ns scope shows as", observed_rise([1e-9, 1e-9]), "s")
    print("6.1 ns measured on a 3.5 ns scope was really",
          signal_rise(6.1e-9, 3.5e-9), "s")
    print("a 10 ns edge to within 2% needs", bandwidth_needed(10e-9, 0.02) / 1e6, "MHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Bandwidth and rise time: what the instrument added to the edge."""

import math

BW_RISE_PRODUCT = 0.35  # ln(9)/(2 pi) = 0.3497, rounded as everyone rounds it


def rise_time(bandwidth_hz):
    """10-90% rise time of a first-order system of this bandwidth, in seconds."""
    return BW_RISE_PRODUCT / bandwidth_hz


def bandwidth(rise_s):
    """The -3 dB bandwidth implied by this 10-90% rise time, in hertz."""
    return BW_RISE_PRODUCT / rise_s


def observed_rise(times):
    """Rise time seen when stages with these rise times are cascaded."""
    return math.sqrt(sum(t * t for t in times))


def signal_rise(measured, instrument):
    """The signal's own rise time, given what was measured and what the
    instrument contributes. Raise ValueError if the measurement is impossible."""
    if measured <= instrument:
        raise ValueError(
            "a measured edge of %g s is not slower than the instrument's own %g s, "
            "so the signal's rise time cannot be recovered" % (measured, instrument)
        )
    return math.sqrt(measured * measured - instrument * instrument)


def bandwidth_needed(edge_s, max_error):
    """Instrument bandwidth that displays an edge of edge_s no more than a
    fraction max_error too slow."""
    allowed = edge_s * math.sqrt((1.0 + max_error) ** 2 - 1.0)
    return BW_RISE_PRODUCT / allowed


if __name__ == "__main__":
    print("a 100 MHz scope rises in", rise_time(100e6), "s")
    print("a 1 ns edge needs about", bandwidth(1e-9) / 1e6, "MHz")
    print("1 ns signal on a 1 ns scope shows as", observed_rise([1e-9, 1e-9]), "s")
    print("6.1 ns measured on a 3.5 ns scope was really",
          signal_rise(6.1e-9, 3.5e-9), "s")
    print("a 10 ns edge to within 2% needs", bandwidth_needed(10e-9, 0.02) / 1e6, "MHz")
'''}],
                "hints": [
                    "`rise_time` is `BW_RISE_PRODUCT / bandwidth_hz`, and `bandwidth` is the same division with the argument in the denominator instead.",
                    "`observed_rise` is `math.sqrt(sum(t * t for t in times))`. It must work for a list of any length, not just two.",
                    "`signal_rise` needs its guard *before* the subtraction, or you will be taking the square root of a negative number and getting a `ValueError` with an unhelpful message instead of an informative one.",
                    "For `bandwidth_needed`: the observed edge is $t\\sqrt{1+(t_i/t)^2}$, and you want that at or below $t(1+e)$. Squaring both sides gives $1 + (t_i/t)^2 \\le (1+e)^2$, so $t_i \\le t\\sqrt{(1+e)^2-1}$. A 2% error allowance on a 10 ns edge leaves 2.01 ns, which is 174 MHz.",
                ],
                "tests": [
                    {"name": "the 0.35 product both ways", "code": r'''
tr = rise_time(100e6)
assert abs(tr - 3.5e-9) < 1e-15, f"a 100 MHz bandwidth rises in 3.5 ns, got {tr}"
bw = bandwidth(3.5e-9)
assert abs(bw - 100e6) < 1.0, f"3.5 ns implies 100 MHz, got {bw}"
assert abs(bandwidth(rise_time(2.5e8)) - 2.5e8) < 1.0, \
    "the two functions must be exact inverses of each other"
'''},
                    {"name": "a 350 MHz scope has a 1 ns rise time", "code": r'''
tr = rise_time(350e6)
assert abs(tr - 1.0e-9) < 1e-12, f"0.35 / 350 MHz is 1.0 ns, got {tr}"
'''},
                    {"name": "cascaded stages add in quadrature", "code": r'''
two = observed_rise([1e-9, 1e-9])
assert abs(two - 1.4142135623730951e-9) < 1e-18, \
    f"two 1 ns stages show as 1.414 ns, not 2 ns, got {two}"
three = observed_rise([5e-9, 3.5e-9, 1e-9])
assert abs(three - 6.184658438426491e-9) < 1e-18, \
    f"5, 3.5 and 1 ns in quadrature is 6.1847 ns, got {three}"
one = observed_rise([4.2e-9])
assert abs(one - 4.2e-9) < 1e-18, f"a single stage adds nothing, got {one}"
'''},
                    {"name": "the instrument's contribution comes back out", "code": r'''
sig = signal_rise(6.1e-9, 3.5e-9)
assert abs(sig - 4.995998398718719e-9) < 1e-18, \
    f"6.1 ns measured through a 3.5 ns scope was a 5.00 ns edge, got {sig}"
back = observed_rise([sig, 3.5e-9])
assert abs(back - 6.1e-9) < 1e-18, \
    f"putting it back through observed_rise must return 6.1 ns, got {back}"
'''},
                    {"name": "an impossible measurement is refused, not fudged", "code": r'''
raised = False
try:
    signal_rise(2.0e-9, 3.5e-9)
except ValueError:
    raised = True
assert raised, \
    "an edge measured faster than the instrument itself is impossible; raise ValueError"
raised = False
try:
    signal_rise(3.5e-9, 3.5e-9)
except ValueError:
    raised = True
assert raised, "equal rise times imply a signal edge of zero; that is impossible too"
'''},
                    {"name": "choosing a scope for an edge", "code": r'''
bw = bandwidth_needed(10e-9, 0.02)
assert abs(bw - 174131508.28674808) < 1.0, \
    f"a 10 ns edge to within 2% needs 174 MHz, got {bw}"
fast = bandwidth_needed(2e-9, 0.03)
assert abs(fast - 709135786.1639695) < 10.0, \
    f"a 2 ns edge to within 3% needs 709 MHz, got {fast}"
tight = bandwidth_needed(10e-9, 0.005)
assert tight > bw, "a tighter error allowance must demand more bandwidth, not less"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Inside the meter: ranging, shunts and the multiplier",
            "summary": "One converter, with a fixed full scale of a fraction of a volt. Everything else on the front panel is resistors arranged to bring the world down to that fraction, and a switch that chooses the arrangement.",
            "concepts": [
                "Behind every DC voltage range is one converter and one resistor chain. The chain's *total* is what loads your circuit — the 10 MΩ the loading module kept insisting on — and on a handheld meter it is deliberately the same on every range: only the tap moves, so autoranging in the middle of a measurement does not change what the circuit is carrying. Bench meters break that rule on purpose, buffering the ranges at and below 10 V to more than 10 GΩ and reverting to the 10 MΩ chain above them, so on those instruments the loading does change with range, and the data sheet says where.",
                "A current range is a shunt beside the movement. With a movement of resistance $R_m$ and full-scale current $I_m$, a shunt $R_s$ makes full scale $I_m(1 + R_m/R_s)$, so multiplying the range by $N$ needs $R_s = R_m/(N-1)$. The same algebra connected in series instead gives the voltage multiplier $(N-1)R_m$.",
                "The price of a current range is the burden voltage $I_mR_m$ across that parallel pair, and it is the same on every current range because the shunt is chosen to make it so. A meter with 100 mV of burden at full scale is a 100 mV battery inserted into your loop — 3% of a 3.3 V rail, taken out of the circuit you are trying to characterise.",
                "The current jack is a separate socket behind a fuse because on that setting the meter is a few tens of milliohms. Probes left in the current jack and then laid across a supply make the meter a short circuit; it is the commonest way a bench meter dies, and the reason the fuse is a consumable.",
                "A meter's AC function is a separate signal path with its own limits: it is AC-coupled, so a DC offset is subtracted rather than measured; it has a specified bandwidth, typically tens of kilohertz on a bench meter; and its converter has a crest-factor limit. Outside any of the three the display is not noisy — it is confidently wrong.",
                "The buffer between the chain and the converter is an operational amplifier with its output wired back to its own inverting input, and the reading below derives what that wire does. Two numbers from this module's chain say why it is there: hang an ordinary 100 kΩ converter straight on the 10:1 tap and the tap collapses from 1.000000 V to 0.100000 V, a factor of ten; put the follower in between and the converter reads 0.999989 V, eleven parts per million low. The rule of 99 would have demanded an 89 MΩ converter to reach 1%, which is an error nearly a thousand times larger than the one the follower leaves.",
            ],
            "read": {
                "title": "The amplifier the rule of 99 was waiting for",
                "minutes": 15,
                "body": r'''
## The problem this course has been carrying since module 2

Module 2 said the only honest thing there is to say about a voltmeter: connecting one
makes a divider out of the node you wanted to measure, the reading comes out low by
$R_{th}/(R_{th}+R_{in})$, and the only defence is to make $R_{in}$ large. The rule of 99
came out of that — 1% of error needs $R_{in} \ge 99R_{th}$ — and this module's own
derivation ended by showing why the analogue instrument could not obey it. Its input
resistance is the movement's own, $1/I_m$ ohms per volt of range, which for a 50 µA
movement is 20 000 Ω/V and therefore 200 kΩ on the 10 V range. On a 100 kΩ node that
reads a third low. Buying a better movement does not rescue it either: a more sensitive
movement is a finer suspension and a weaker hairspring, and the mechanism gives out long
before the ohms arrive.

So the instrument needs something that will read a voltage and take no current for doing
it. No component does that. What does it is a **loop**, and the device the loop is built
around is the triangle in this module's symbol drill — the one sitting between the
divider chain and the converter, which is the only part of a meter's front end this
course has named without opening.

## The device, from the outside

Three terminals matter: two inputs, marked $+$ and $-$, and one output. One equation
describes it,

$$v_{out} = A\,(v_{+} - v_{-})$$

and one number: $A$, the open-loop gain, which for the device in this course's editor is
$10^{5}$. The output cannot leave its supply rails, here $\pm 15$ V.

Put those two facts together before reading on, because their consequence is the whole
subject. If the output stops at 15 V and the gain is $10^{5}$, the largest input
difference the device can respond to *at all* is

$$\frac{15\,\text{V}}{10^{5}} = 150\,\mu\text{V}$$

so the window over which it behaves as an amplifier is 300 µV wide, rail to rail. An
amplifier whose entire useful input range is three hundred microvolts is not an
amplifier. It is a comparator: feed it anything larger and the output sits at one rail or
the other, and which one tells you the sign of the difference and nothing else.

That is the device as sold. Everything useful it does, it does with a wire from its
output back to its inverting input.

## The loop, with the algebra rather than the slogan

Join the output straight back to the $-$ input and drive the $+$ input with $v_{in}$.
Now $v_{-} = v_{out}$, so the one equation reads

$$v_{out} = A\,(v_{in} - v_{out})$$

which rearranges with no approximation anywhere to

$$\frac{v_{out}}{v_{in}} = \frac{A}{1 + A}$$

The gain is 1, near enough. *How* near is the interesting part: the shortfall is
$-1/(1+A)$, which at $A = 10^{5}$ is ten parts per million. Run it on the editor's own
device and that is what comes back.

```text
  open-loop gain A     v_out for 1.000000 V in     shortfall      -1/(1+A)
            10           0.908989532               -9.101 %       -9.091 %
           100           0.990084736               -0.9915 %      -0.9901 %
         1 000           0.998999519               -0.1000 %      -0.09990 %
        10 000           0.999899862               -0.01001 %     -0.009999 %
       100 000           0.999989985               -0.001001 %    -0.001000 %
     1 000 000           0.999998999               -0.0001001 %   -0.0001000 %
```

Read the first column and the third together. The device's own gain changes by five
orders of magnitude down that table and the *circuit's* gain changes in the sixth decimal
place. That is the trade the loop makes, and it is why the operational amplifier is worth
having: you give up almost all of a very large and very badly controlled gain, and what
you get back is a small one controlled by nothing but the feedback path.

## The virtual short is a consequence, not an axiom

Rearranged the other way, the same equation says

$$v_{+} - v_{-} = \frac{v_{out}}{A}$$

The difference between the two inputs is the output divided by the open-loop gain, and
the output cannot exceed a rail, so that difference cannot exceed $15/10^{5} = 150$ µV.
Textbooks compress this to "the two inputs are at the same voltage", and it is worth
knowing exactly what kind of sentence that is. It is not a property of the device. It is
what a large $A$ and a *closed* loop force between them, and it fails at once in either
case where those conditions do not hold.

- **The loop is open.** With no feedback path nothing is holding $v_{out}$ small, and the
  output goes to a rail. Build this module's exercise and leave out the feedback wire:
  the amplifier's output sits at 14.99 V with its $+$ input at 1.00 V, and the two inputs
  are a volt apart.
- **The output is against a rail.** The loop is closed and still cannot act, because the
  output has nowhere left to go. Ask the follower above for 16 V and it delivers
  15.000000 and stops. The input difference is then a volt rather than a microvolt, and
  every conclusion drawn from the virtual short is false for that circuit.

"The inputs are at the same voltage" is the last line of the argument, not the first.
Starting from it is how people end up asserting it about a comparator, which is the same
silicon with the wire left off.

## The mistake this produces, every time

Asked what a follower's output does, the answer that arrives is "the amplifier multiplies
the difference between its inputs by $10^{5}$". That is true, and using it to predict the
circuit gets you nowhere, because you cannot know the difference until you know the
output. The equation is not a recipe to be evaluated left to right; it is a constraint
the circuit must satisfy, and it is the *circuit* — device plus feedback path — that has
a solution. That is why the algebra above writes both relationships and solves them
together, and it is why the editor's solver has to iterate on this circuit rather than
evaluate it.

The other half of the same mistake is reading feedback as a loss: the device had a gain
of $10^{5}$ and you have thrown all but one of them away. What was thrown away was never
spendable — 300 microvolts of input range, and a gain that varies by a factor of two or
three between two devices out of the same tube, and with temperature besides. What came
back is a gain set by two resistors you chose, holding to a tenth of a per cent, with an
output that keeps its voltage under load. The bargain looks bad only if you count what
was given up and not what it was worth.

## Three circuits, and all of them are one argument

**The follower**, above. Gain 1, and its whole value is in what it does not do: the $+$
input takes no current from whatever it is connected to, and the output holds its voltage
against a load. That is a buffer, and it is the part this module's symbol drill described
as taking "almost no current from the tap".

**The non-inverting amplifier.** Instead of joining the output straight back, feed back a
*fraction* of it through a divider — $R_1$ from the $-$ input to ground and $R_2$ from
the output down to the same node — so that $v_{-} = v_{out}R_1/(R_1+R_2)$. Setting that
equal to $v_{+} = v_{in}$ gives

$$v_{out} = v_{in}\left(1 + \frac{R_2}{R_1}\right)$$

**The inverting amplifier.** Ground the $+$ input instead, and drive the $-$ input
through $R_1$ with $R_2$ from the output back to that node. The loop holds $v_{-}$ at
almost exactly zero — a *virtual earth*, and this node is what module 5's dual-slope
derivation calls the summing node. The input current is therefore $v_{in}/R_1$; none of
it enters the amplifier; so all of it continues through $R_2$, and

$$v_{out} = -v_{in}\frac{R_2}{R_1}$$

Notice what the third circuit costs, because module 7 is where the bill arrives. Its
input resistance is $R_1$ and nothing else: the source is looking into a node pinned at
zero, so what it sees is one resistor. The follower's input resistance is the amplifier's
own, which is to say none worth writing down. Two circuits out of one device, one of
which loads its source and one of which does not.

And the output impedance is part of the same bargain. The editor's device has 75 Ω of its
own output resistance. Measured closed-loop, the follower's output sags 0.75 µV per
milliamp drawn from it — **0.75 mΩ**, which is that 75 Ω divided by the same $1+A$.
EE102's cascading module says a follower's output impedance is "milliohms". It is, and
this is where the milliohms come from.

## What it buys the meter, in this course's own numbers

Take this module's chain: 10 MΩ from the input to ground, tapped 9 MΩ above and 1 MΩ
below, so 10 V in puts exactly 1.000000 V on the tap.

The tap's Thévenin resistance is $9\,\text{M}\parallel 1\,\text{M} = 900$ kΩ, so module
2's rule of 99 says a converter that is to read it to 1% must present
$99 \times 900\,\text{k} = 89.1$ MΩ. Solved: at 100 MΩ the tap reads 0.991080 V, which is
0.89% low. The rule is right.

Now put a real converter on it. A dual-slope front end is a resistor into a summing node,
and 100 kΩ is an ordinary value for that resistor.

```text
  converter input        tap            error
       100 kΩ         0.100000 V       -90.0 %
         1 MΩ         0.526316 V       -47.4 %
        10 MΩ         0.917431 V        -8.3 %
       100 MΩ         0.991080 V        -0.89 %
         1 GΩ         0.999101 V        -0.090 %
```

A factor of ten wrong on the first line. Put a follower between the tap and that same
100 kΩ converter and the converter reads **0.999989 V** — eleven parts per million low,
and those eleven parts are the $1/(1+A)$ of the earlier table and nothing else.

That number is worth sitting with. Module 1 said a 6½-digit instrument resolves about one
part in $10^{6}$ and is specified to perhaps 35 parts in $10^{6}$. The buffer's own error
is 11 ppm: larger than the resolution, so it is a real line in the uncertainty budget
rather than a rounding, and smaller than the specification, so it is not what limits the
instrument. Both halves of that sentence matter, and neither can be said about the 90%
error of the unbuffered chain.

## Where this stops holding

Four places, and the first two live in the model you are about to use.

**The rails.** Everything above assumes the output is free to move. The editor's device
runs on ±15 V and saturates smoothly rather than clipping square, which is a numerical
convenience rather than a claim about silicon: asked for 14 V it gives 13.999748, for
15 V it gives 14.999210, and past that, exactly 15.000000.

**Finite gain, once the closed-loop gain is not 1.** The shortfall is not $1/(1+A)$ in
general. It is $1/(1+A\beta)$, where $\beta$ is the fraction of the output fed back. A
follower has $\beta = 1$. A gain-of-100 stage feeds back a hundredth of its output, so
$A\beta = 10^{5}/101 = 990$ and the shortfall is 0.101% — a thousand times the follower's,
out of the same device. That is exactly the shortfall module 7's difference amplifier is
measured showing, and it is not a defect in the drawing when it appears.

**Input current, which this model does not have.** The editor's amplifier draws *exactly*
zero at both inputs — not a small number; a zero. A real one draws anywhere between a few
femtoamps and a few hundred nanoamps depending on what its input stage is made of, and on
a 10 MΩ chain even 1 nA is 10 mV, which would swamp everything on this page. The
simulator cannot show you that error and a laboratory will. The same goes for input
offset voltage: a real device's two inputs are not identical, and the tens of microvolts
between them add straight to the reading — the same size as the 11 ppm above.

**Bandwidth, which this model also does not have.** Run the follower's gain against
frequency in the editor and it is 0.999989955 at 1 Hz and 0.999989955 at a terahertz. A
real op-amp's open-loop gain falls at 20 dB per decade above a few hertz, so $A\beta$
shrinks as the frequency rises and every error on this page grows with it. That is why a
data sheet quotes a gain-bandwidth product, and why module 3's rise-time arithmetic
exists. Nothing in this solver knows it, so a number it gives you at 1 MHz should be read
as a number about DC.

## What module 7 does with this

One more circuit, and it is the one instrumentation is actually built out of. Drive
*both* inputs — $V_1$ through $R_1$ into the summing node, $V_2$ through $R_3$ into a
divider on the $+$ input — and the output becomes a scaled difference of the two. That is
the difference amplifier, the block module 7 asks you to take "as a block subtracting its
two inputs", and the interesting thing about it is a defect: it subtracts correctly only
if two resistor ratios match. How closely they must match, and what it costs when they do
not, is derived and then measured there.
''',
            },
            "quiz": {
                "title": "Chains, shunts and the socket that blows fuses",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A handheld multimeter's DC input is 10 MΩ on the 10 V range and 10 MΩ on the 1 V range. Why go to the trouble?",
                        "opts": [
                            "so that the burden voltage stays constant across ranges",
                            "so that the loading a circuit sees does not change when the meter changes range",
                            "because a lower input resistance would overload the converter",
                            "so that the input capacitance stays constant",
                        ],
                        "a": 1,
                        "why": r'''
One tapped chain totalling 10 MΩ, with the converter connected to different taps, gives
every range the same input resistance. If the ranges were separate dividers the loading
would jump as the meter autoranged, and a reading on a high-impedance node would change
by several per cent at the moment the range changed — which looks exactly like the
circuit doing something. Burden voltage belongs to the current function, not this one,
and the input capacitance is set by the cable and the front end rather than by the
chain.
''',
                    },
                    {
                        "q": "A movement takes 50 µA at full scale and has a resistance of 2.0 kΩ. What shunt turns it into a 1.00 A meter?",
                        "opts": ["100 mΩ", "40 Ω", "2.0 Ω", "10 mΩ"],
                        "a": 0,
                        "why": r'''
$N = 1.00\ \text{A}/50\ \mu\text{A} = 20\,000$, and $R_s = R_m/(N-1) = 2000/19999
= 0.10001$ Ω. The approximation $R_s \approx R_m/N$ is good to five parts in $10^5$ here
and is what anyone would use in practice, but the $-1$ matters when $N$ is small: for a
range of twice full scale the shunt equals $R_m$, not half of it. Answering 40 Ω divides
the movement's resistance by 50 rather than by 20 000 — the “50” of 50 µA is a number of
microamps, not a ratio of anything.
''',
                    },
                    {
                        "q": "The same 50 µA, 2.0 kΩ movement is used on a 1 A range and then on a 10 mA range. What happens to the burden voltage at full scale?",
                        "opts": [
                            "it falls by a factor of 100 on the lower range",
                            "it is 100 mV on both",
                            "it rises by a factor of 100 on the lower range",
                            "it depends on the circuit being measured",
                        ],
                        "a": 1,
                        "why": r'''
At full scale the movement always takes its own 50 µA and always drops
$50\ \mu\text{A} \times 2\ \text{k}\Omega = 100$ mV, and the shunt is in parallel with it,
so the burden voltage at full scale is 100 mV on every range. That is why a data sheet
quotes one burden figure per function rather than one per range. It also means that
measuring a 1 mA current on the 1 A range costs only 0.1 mV of burden while measuring it
on a 1 mA range costs the full 100 mV — the burden follows the *fraction of full scale*,
which is the opposite of the way the accuracy specification behaves.
''',
                    },
                    {
                        "q": "An analogue multimeter is marked “20 000 Ω/V”. On its 10 V range, what does it present to the circuit?",
                        "opts": ["20 kΩ", "200 kΩ", "2 MΩ", "20 MΩ"],
                        "a": 1,
                        "why": r'''
The ohms-per-volt figure is the reciprocal of the movement's full-scale current —
$1/50\ \mu\text{A} = 20\,000$ Ω/V — and the input resistance of a range is that figure
times the range: 200 kΩ on the 10 V range. This is the number that made analogue meters
treacherous. On a node of 100 kΩ source resistance, 200 kΩ of meter reads a third low,
and the rule of 99 from the loading module says you would need 9.9 MΩ to be within 1%. The
digital meter's fixed 10 MΩ was not a refinement; it was a different order of
instrument.
''',
                    },
                    {
                        "q": "Your probes are still in the current jack from the last measurement and you lay them across a 12 V battery. What have you built?",
                        "opts": [
                            "a voltmeter reading 12 V, since the meter is still on the volts setting",
                            "an open circuit — the current jack is high impedance until a current is applied",
                            "a short circuit across the battery through a few tens of milliohms and a fuse",
                            "a current source of 12 A",
                        ],
                        "a": 2,
                        "why": r'''
The current jack goes to the shunt, which is a few tens of milliohms, so the leads and
the meter are a short circuit across the battery. What limits the current is the
battery's own internal resistance and the lead resistance, and what interrupts it is
the fuse — which is why that jack has a fuse and the volts jack does not. Nothing about
the *rotary switch* saves you: the jack is the connection, and on many meters the switch
position and the jack can disagree.
''',
                    },
                    {
                        "q": "A meter's ACV function is specified from 45 Hz to 20 kHz with a crest factor limit of 3. You point it at a 100 Hz rectangular pulse train of 5% duty cycle. What should you expect?",
                        "opts": [
                            "a correct RMS reading — 100 Hz is comfortably inside the stated band",
                            "a reading that cannot be trusted: the crest factor reaching the converter is 4.4",
                            "a reading high by the form factor 1.111",
                            "no reading at all, since the input is not a sine",
                        ],
                        "a": 1,
                        "why": r'''
The meter is AC-coupled, so what reaches the converter is the pulse train with its mean
removed: it sits at $-0.05V$ for 95% of the period and jumps to $+0.95V$ for the other
5%. Its RMS is $V\sqrt{D(1-D)} = 0.218V$ and its peak excursion is $0.95V$, so the crest
factor at the converter is $\sqrt{(1-D)/D} = \sqrt{19} = 4.36$ — well beyond the 3 the
data sheet allows, and a converter asked to handle a crest factor beyond its limit reads
low. The frequency specification is not the rescue either: a 5% duty pulse at 100 Hz has
a spectrum whose first null is at 2 kHz and which carries real energy far past 20 kHz.
Being inside the frequency band is necessary and not sufficient.
''',
                    },
                ],
            },
            "match": {
                "title": "The five parts behind the input jacks",
                "minutes": 6,
                "brief": r'''
Open any bench meter and the first centimetre past the input terminals is the same five
or six components, doing jobs the earlier modules have already argued about: dividing
the input down, keeping the divider's ratio honest at frequency, deciding which tap the
converter sees, keeping the whole chain out of the converter's way, and stopping a
mains transient from reaching any of it.

Name them.
''',
                "prompt": "Pick a label, then tap the symbol it belongs to.",
                "labels": ["Resistor", "Capacitor", "Diode", "Switch", "Operational amplifier", "Ground"],
                "items": [
                    {"sym": "R", "a": 0, "why": "A resistor. In a meter's front end these are the divider chain "
                     "— on a bench instrument a 10 MΩ ladder with taps for each range, and on the current "
                     "function a set of shunts running down to a few tens of milliohms. The zig-zag is the "
                     "symbol most of the world learned; the plain rectangle is the IEC form and means the same."},
                    {"sym": "C", "a": 1, "why": "A capacitor: two plates that never touch. Two of them appear "
                     "in the front end. Small trimmers sit across the divider taps to compensate the chain the "
                     "way module 3 compensated the probe, and a much larger one couples the AC function so "
                     "that a DC offset is blocked rather than measured."},
                    {"sym": "D", "a": 2, "why": "A diode — the triangle points the way current passes, into "
                     "the bar that stops it coming back. In a meter's input these are the clamps: a pair back "
                     "to back from the input to each supply rail, conducting only when the input tries to go "
                     "beyond them, which turns a 2 kV transient into a current the series resistance can "
                     "survive."},
                    {"sym": "SW", "a": 3, "why": "A switch. On a bench meter this is a set of relays or "
                     "analogue switches rather than the rotary contact the symbol suggests, but it is doing "
                     "the same thing: choosing which tap of the divider chain the converter looks at. That "
                     "choice is the range, and it is why the range term of the specification exists."},
                    {"sym": "OPAMP", "a": 4, "why": "An operational amplifier — a triangle with two inputs "
                     "marked + and −, and one output. Here it is the buffer between the divider chain and the "
                     "converter: it takes almost no current from the tap, so the chain's ratio is the ratio "
                     "the resistors were trimmed to and not one loaded by whatever comes next."},
                    {"sym": "GND", "a": 5, "why": "Ground: the node every reading is quoted against, and in "
                     "an instrument it is a choice with consequences. The meter's LO terminal is not the "
                     "chassis and not the mains earth; keeping those three separate is what lets a bench "
                     "meter float, and a later module of this course is about what happens when they are "
                     "accidentally joined."},
                ],
            },
            "build": {
                "title": "The buffer between the chain and the converter",
                "minutes": 26,
                "brief": r'''
The canvas holds the front end this module has been describing, wired the naive way.

On the left, the input under measurement — **10 V** — across the meter's divider chain:
**9 MΩ** above the tap and **1 MΩ** below, 10 MΩ in total, which is the number module 2
kept insisting on. Ten volts across a 10:1 chain puts **1.000000 V** on the tap, and that
is the voltage the converter is supposed to read.

On the right, the converter, drawn as its input resistance: **100 kΩ** to ground with the
probe on it. A dual-slope front end is a resistor into a summing node, and 100 kΩ is an
ordinary value for that resistor — module 5 derives what happens after it.

Between them, at the moment, a wire. **Solve the circuit as it stands and the probe reads
0.100000 V.** Not 1% low. A factor of ten.

## Why it is that bad

The tap is not a voltage; it is a source of Thévenin resistance
$9\,\text{M}\parallel 1\,\text{M} = 900$ kΩ. Hanging 100 kΩ on 900 kΩ leaves a ninth of
the signal. Module 2's rule of 99 says that to read this tap to 1% by brute force the
converter would have to present $99 \times 900\,\text{k} = 89.1$ MΩ, and no converter
does.

## What to build

Put a **follower** between the tap and the converter, exactly as the symbol drill on this
page described it: an op-amp with its output wired back to its own inverting input.

Place an **Op-amp** from the parts list. Its three pins are not where a beginner expects,
so read them off the symbol rather than guessing: the **non-inverting input is in line
with the body on one side**, the **output is in line on the other**, and the **inverting
input leaves at right angles**, one cell out. The editor draws the $+$ and the $-$ inside
the triangle and turns them with it, so which pin is which is never a guess — zoom in if
you have to.

Then three connections:

- the tap to the $+$ input,
- the output to the converter,
- the output back to the $-$ input. This is the wire that does all the work, and leaving
  it out is not a partial answer: with no feedback the output goes to a supply rail and
  stays there.

**Delete the wire that runs straight from the tap to the converter.** Leaving it in
short-circuits the amplifier's input to its output, which is a shorter way of saying you
have wired the converter to the tap again.

## What has to be true when you are finished

- the tap sits at **1.000 V** — the ratio the resistors were trimmed to, not one bent by
  what came after,
- the converter node reads the same voltage to better than **50 parts per million** (the
  follower's own error on this device is about 11),
- the chain draws **1.000 µA** from the circuit under test — 10 V across 10 MΩ, and not
  the 1.100 µA it was drawing with the converter hung on the tap.

Nothing is graded on layout, and the values you were given are not design variables. Any
drawing that behaves this way passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 12},
                        {"id": "p2", "kind": "R", "x": 7, "y": 6, "rot": 1, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 7, "y": 10, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 13},
                        {"id": "p5", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 100000},
                        {"id": "p6", "kind": "GND", "x": 17, "y": 12},
                        {"id": "p7", "kind": "OUT", "x": 19, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 4]},
                        {"a": [3, 4], "b": [7, 4]},
                        {"a": [7, 4], "b": [7, 5]},
                        {"a": [3, 9], "b": [3, 12]},
                        {"a": [7, 7], "b": [7, 9]},
                        {"a": [7, 11], "b": [7, 13]},
                        {"a": [17, 8], "b": [19, 8]},
                        {"a": [17, 10], "b": [17, 12]},
                        {"a": [7, 8], "b": [17, 8]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 12},
                        {"id": "p2", "kind": "R", "x": 7, "y": 6, "rot": 1, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 7, "y": 10, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 13},
                        {"id": "p5", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 100000},
                        {"id": "p6", "kind": "GND", "x": 17, "y": 12},
                        {"id": "p7", "kind": "OUT", "x": 19, "y": 8},
                        {"id": "p8", "kind": "OPAMP", "x": 12, "y": 8, "rot": 0, "value": 100000},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 4]},
                        {"a": [3, 4], "b": [7, 4]},
                        {"a": [7, 4], "b": [7, 5]},
                        {"a": [3, 9], "b": [3, 12]},
                        {"a": [7, 7], "b": [7, 9]},
                        {"a": [7, 11], "b": [7, 13]},
                        {"a": [17, 8], "b": [19, 8]},
                        {"a": [17, 10], "b": [17, 12]},
                        {"a": [7, 8], "b": [11, 8]},
                        {"a": [13, 8], "b": [17, 8]},
                        {"a": [15, 8], "b": [15, 11]},
                        {"a": [15, 11], "b": [12, 11]},
                        {"a": [12, 11], "b": [12, 7]},
                    ],
                },
                "checks": [
                    {"name": "the chain and the converter are the ones you were given", "code": r'''
c.assert(c.count('V') === 1,
  'One source: the 10 V being measured. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 10, 0.001, 'the input under measurement');
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const top = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 9e6) <= 9e4 &&
    (p.n1 === src.n1 || p.n2 === src.n1);
});
c.assert(top.length === 1,
  'The 9 MOhm upper arm of the meter chain has to stay connected to the input. It is ' +
  'the instrument, not the thing under test.');
const bot = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 1e6) <= 1e4 && (p.n1 === 0 || p.n2 === 0);
});
c.assert(bot.length === 1,
  'The 1 MOhm lower arm has to stay, one end on ground. Found ' + bot.length + '.');
const conv = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 1e5) <= 1e3;
});
c.assert(conv.length === 1,
  'The converter is the 100 kOhm resistor with the probe on it, and its input ' +
  'resistance is a fact about the converter rather than a number you may change. ' +
  'Found ' + conv.length + ' of them.');
'''},
                    {"name": "the tap is back at the ratio the resistors were trimmed to", "code": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const top = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 9e6) <= 9e4 &&
    (p.n1 === src.n1 || p.n2 === src.n1);
})[0];
c.assert(top, 'The 9 MOhm arm is no longer connected to the input.');
const tap = top.n1 === src.n1 ? top.n2 : top.n1;
c.close(c.dc().v[tap], 1.0, 0.002,
  'the tap between the 9 MOhm and the 1 MOhm. Ten volts across a 10:1 chain puts ' +
  '1.000 V here, and it did so before anything was hung on it');
'''},
                    {"name": "the converter reads that tap and not a loaded copy of it", "code": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const top = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 9e6) <= 9e4 &&
    (p.n1 === src.n1 || p.n2 === src.n1);
})[0];
c.assert(top, 'The 9 MOhm arm is no longer connected to the input.');
const tap = top.n1 === src.n1 ? top.n2 : top.n1;
const vt = c.dc().v[tap];
c.assert(Math.abs(vt) > 1e-6, 'The tap is at zero volts, so there is nothing to follow.');
const ppm = (c.vout() - vt) / vt * 1e6;
c.assert(Math.abs(ppm) <= 50,
  'The converter is reading ' + c.fmt(c.vout(), 'V') + ' where the tap sits at ' +
  c.fmt(vt, 'V') + ' — a difference of ' + ppm.toFixed(0) + ' parts per million. A ' +
  'follower tracks its input to about ten parts in a million on a device of this gain, ' +
  'so a gap this size means the two nodes are not joined by one.');
'''},
                    {"name": "the chain has stopped paying for the converter", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1,
  'The supply current has to mean one thing, so this exercise wants exactly one part ' +
  'carrying a solved-for current — the 10 V input. Found ' + ids.length + '.');
c.close(Math.abs(cur[ids[0]]), 1e-6, 0.01,
  'the current the meter draws from the circuit under test. Ten volts across a 10 MOhm ' +
  'chain is 1.000 uA and nothing may be added to it; with the converter hung straight ' +
  'on the tap it was 1.100 uA, and that extra tenth of a microamp is the entire fault');
const u = c.net.placed.filter(function (p) { return p.kind === 'OPAMP'; });
c.assert(u.length === 1,
  'This exercise wants exactly one amplifier. Found ' + u.length + '.');
const d = c.device(u[0].id);
c.assert(Math.abs(d.v[1]) < 14,
  'The amplifier output is at ' + c.fmt(d.v[1], 'V') + ', hard against a supply rail. ' +
  'An op-amp with no path from its output back to its inverting input has nothing ' +
  'holding it anywhere else.');
c.assert(Math.abs(d.v[0] - d.v[2]) < 1e-3,
  'The two inputs are ' + c.fmt(d.v[0] - d.v[2], 'V') + ' apart, so the loop is not ' +
  'closed. Negative feedback drives that difference to almost nothing; nothing else does.');
'''},
                    {"name": "the loop closes onto the inverting input", "code": r'''
/* The one check on this page that reads the wiring rather than a voltage, and it says so
   because the reason is worth knowing. Wire the same three parts with the feedback on the
   + input instead and every voltage in the circuit comes out the same to five figures: an
   operating point is a solution of the circuit equations, and nothing in it asks whether
   that solution is one the circuit would stay at. The positive-feedback version solves.
   A real one latches against a rail the moment anything nudges it. */
const u = c.net.readouts.filter(function (x) { return x.kind === 'OPAMP'; });
c.assert(u.length === 1,
  'This exercise wants exactly one amplifier. Found ' + u.length + '.');
const n = u[0].nodes;
c.assert(n[2] === n[1],
  'The output has to come back to the INVERTING input — the pin that leaves the body at ' +
  'right angles, marked with a minus inside the triangle. Feedback onto the + input is ' +
  'positive feedback, and the solver will still hand you an answer for it, because an ' +
  'operating point is a solution of the equations rather than a promise that the circuit ' +
  'stays there.');
c.assert(n[0] !== n[1],
  'The non-inverting input is on the output node too, so both inputs are tied together ' +
  'and there is nothing left for the amplifier to follow.');
'''},
                ],
                "hints": [
                    "Nothing needs a value changed and nothing needs deleting except one wire — the one running straight from the tap across to the converter's node. Delete it first; the rest of the exercise is easier to see once the two halves are apart.",
                    "Place the Op-amp between them. At its default rotation the non-inverting input is the pin on the left, in line with the body; the output is the pin on the right; the inverting input is the pin sticking up above it. The $+$ and $-$ drawn inside the triangle turn with the part, so they always name the right pins.",
                    "Wire the tap to the left-hand pin and the right-hand pin across to the converter. Run the circuit now: the output is at about 15 V, because you have built a comparator. Nothing is holding the output anywhere until the loop is closed.",
                    "Now the wire that matters: from the output node back up to the pin above the body. Take it out sideways and then up, so it does not touch the run between the tap and the $+$ input. Solve again and the probe should read 0.999989 V.",
                    "Check yourself before running: the tap is at 1.000000 V, the converter node is 11 ppm below it, the source is delivering 1.000 µA rather than 1.100 µA, and the two amplifier inputs are about 10 µV apart rather than a volt.",
                ],
            },
            "derive": {
                "title": "The shunt, the multiplier, and the burden they share",
                "minutes": 12,
                "vars": ["I_m", "R_m", "R_s", "R_x", "N", "V_b"],
                "brief": r'''
One movement: full scale $I_m$, resistance $R_m$. On its own it reads currents up to
$I_m$ and voltages up to $I_mR_m$, and neither is a useful range.

Two resistors turn it into every range on the front panel — one beside it and one in
front of it. Derive both, and the burden voltage that comes with the first.
''',
                "steps": [
                    {
                        "prompt": "You want full scale to be $N$ times larger, so at full scale the pair carries $NI_m$ while the movement itself still carries $I_m$. Write the shunt's current.",
                        "given": "Kirchhoff's current law at the junction where the shunt joins the movement.",
                        "answer": "(N - 1) I_m",
                        "placeholder": "e.g. (a + b) c",
                        "hint": "Everything that does not go through the movement goes through the shunt.",
                        "deconstruct": [
                            "The total arriving is $NI_m$.",
                            "The movement takes $I_m$ of it.",
                            "The rest is the difference.",
                        ],
                    },
                    {
                        "prompt": "The shunt is in parallel with the movement, so the two hold the same voltage. Write $R_s$ in terms of $R_m$ and $N$.",
                        "given": "$I_mR_m = I_sR_s$, with $I_s$ the current you just wrote.",
                        "answer": "\\frac{R_m}{N - 1}",
                        "placeholder": "e.g. \\frac{a}{b + c}",
                        "hint": "Divide both sides by $I_m$; it appears once on each side and cancels.",
                        "deconstruct": [
                            "$I_mR_m = (N-1)I_mR_s$.",
                            "Cancel $I_m$: $R_m = (N-1)R_s$.",
                            "Divide by $(N-1)$.",
                        ],
                    },
                    {
                        "prompt": "The burden voltage $V_b$ is the voltage the meter inserts into the loop, which is the voltage across that parallel pair at full scale. Write it in terms of $I_m$ and $R_m$.",
                        "given": "The movement is one of the two arms, and it is carrying $I_m$.",
                        "answer": "I_m R_m",
                        "placeholder": "e.g. a b c",
                        "hint": "You do not need the shunt at all: the pair holds whatever the movement holds.",
                        "deconstruct": [
                            "The two arms are in parallel, so they hold one common voltage.",
                            "The movement's own drop is $I_mR_m$, and it is at full scale.",
                        ],
                    },
                    {
                        "prompt": "Now the voltmeter. Put a resistance $R_x$ in *series* instead, so that the range becomes $N$ times the $I_mR_m$ the movement reads alone. Write $R_x$.",
                        "given": "At full scale the current is still $I_m$, because that is what full scale means.",
                        "answer": "(N - 1) R_m",
                        "placeholder": "e.g. (a + b) c",
                        "hint": "Of the $NI_mR_m$ applied, $I_mR_m$ appears across the movement. The rest has to appear across $R_x$, at a current of $I_m$.",
                        "deconstruct": [
                            "Total applied at full scale: $NI_mR_m$.",
                            "Across the movement: $I_mR_m$.",
                            "Across $R_x$: $(N-1)I_mR_m$, at a current $I_m$.",
                        ],
                    },
                ],
                "closing": r'''
Put the classic movement into all four: 50 µA full scale, 2.0 kΩ, so $I_mR_m = 100$ mV.

A 1 A range needs $N = 20\,000$ and a shunt of $2000/19999 = 100.0$ mΩ, and the burden
is 100 mV whatever range you pick — the third line never mentioned $N$. A 10 V range
needs $N = 100$ and a multiplier of 198 kΩ, giving an input resistance of 200 kΩ. That
last number is the ohms-per-volt figure printed on the front of every analogue meter,
because $R_x + R_m = NI_mR_m/I_m$ divided by the range $NI_mR_m$ is exactly $1/I_m$:
the input resistance per volt of range is the reciprocal of the movement's full-scale
current, and nothing else.

Which is a compact statement of why a sensitive movement was worth paying for, and why
the rule of 99 was out of reach until an amplifier was put in front of
the divider instead of a coil of wire.

That amplifier is this module's reading, and its arithmetic is the mirror image of the
four lines above. Where the movement's input resistance is fixed at $1/I_m$ per volt by
what the mechanism can be made of, a follower's is set by nothing at all: it draws no
current from the tap, so the chain's ratio stays the ratio its resistors were trimmed to.
On the 10 MΩ chain of this module that is the difference between a converter reading
0.100000 V and one reading 0.999989 V, and the build exercise on this page is that
difference in one wire.
''',
            },
        },

        # ---- M5 -----------------------------------------------------------
        {
            "title": "Counts, digits and the integrating converter",
            "summary": "A digital meter does not measure a voltage; it counts. What it counts, and for how long, decides both the digits on the display and which interference never reaches them.",
            "concepts": [
                "A “6½-digit” display is a count. A 1 200 000-count meter runs its 10 V range to 12.00000 V, so one count is 10 µV: that is the *resolution*, and whether the last digit means anything is decided by the specification and by the noise, not by the display.",
                "A dual-slope converter integrates the input for a fixed time $T_1$ and then integrates a reference of the opposite sign until the integrator returns to zero, taking $T_2$. The result is $V_{in} = V_{ref}T_2/T_1$: the integrator's own $R$ and $C$ appear in both halves and cancel, and so does the clock, provided neither drifts within one conversion.",
                "Integrating over a whole number of power line cycles rejects mains interference exactly, because the average of a sine over an integer number of its own periods is zero. That is what NPLC means on the front panel — 1 NPLC is 20 ms at 50 Hz and 16.67 ms at 60 Hz — and it is why asking for more digits makes a meter slower.",
                "The rejection is only as good as the line frequency is known. Over an aperture of $n$ cycles a line frequency wrong by a fraction $\\varepsilon$ leaves about $\\varepsilon$ of the interference behind — 0.1% of error is 60 dB of rejection — and, unexpectedly, that figure barely improves with more cycles, because the accumulated phase error grows exactly as fast as the averaging shrinks it.",
                "Anything above half the sampling rate folds down into the band and stays there. A logger taking ten readings a second records 50 Hz hum as a slow wander or a fixed offset depending on the exact rate, and nothing done after the converter can undo it. The defence is analogue and comes first — a filter, or the converter's own aperture, which is a filter with nulls exactly where you put them.",
            ],
            "read": {
                "title": "The reading is an average, and that is where the hum goes",
                "minutes": 16,
                "body": r'''
A 6½-digit bench meter, its leads on the output of a thermocouple amplifier, on a bench
under a fluorescent fitting. Set the integration to its fastest — 0.02 NPLC — and the
display looks like this:

```text
  0.024 61   0.024 83   0.024 42   0.024 79   0.024 38   0.024 71 V
```

The last three digits are wandering over about 450 counts. Now press the setting up to
10 NPLC and wait:

```text
  0.024 601   0.024 600   0.024 601   0.024 601   0.024 600 V
```

Nothing was filtered, nothing was screened, no lead was moved. The only thing that
changed is how long the converter looked, and the interference has gone. Where did it
go, and how much of it is really gone?

## What the display is counting

Begin with what a digit is. A "6½-digit" meter is a converter with a count: 1 200 000
of them, with the 10 V range running to 12.00000 V, so one count is
$12/1\,200\,000 = 10$ µV. That number is the *resolution* — the smallest step the
display can take — and the specification from module 1 allows 350 µV at 10 V, which is
thirty-five counts. The display steps in units of one and the instrument is honest to
about thirty-five of them, and both statements are true at once.

The wandering above is neither. It is interference reaching the converter, and it is
worth 450 counts, or 4.5 mV, on a signal of 24.6 mV.

## The converter reports a mean, not a sample

A dual-slope converter works in two phases. In the **run-up** the input is switched onto
a resistor into an integrator and left there for a fixed time $T_1$. In the
**run-down** the input is disconnected, a reference of the opposite sign is applied
instead, and a counter runs until a comparator sees the integrator cross zero again,
after a time $T_2$.

The integrator's output after the run-up is $\frac{1}{RC}\int_0^{T_1} v(t)\,dt$; the
run-down takes it back down at a rate $V_{ref}/RC$, so the fall $V_{ref}T_2/RC$ equals
the rise. Set them equal, the $RC$ divides out of both sides, and

$$V_{ref}\,T_2 = \int_0^{T_1} v(t)\,dt
\qquad\text{so}\qquad
\frac{V_{ref}T_2}{T_1} = \frac{1}{T_1}\int_0^{T_1} v(t)\,dt$$

That is the fact this whole module rests on, and this module's derivation, **Why a
dual-slope converter does not care what it is made of**, takes it further into what
cancels. The left side is what the meter displays. The right side is the *average of
the input over the aperture*. A digital meter does not sample your voltage; it averages
it, and it is entitled to display a number that the input never actually held.

## What an average does to a sine

So put a sine on the input and average it, and the answer follows without any new
physics. Take interference $a\sin(\omega t + \phi)$ over a window of length $T$:

$$\frac{1}{T}\int_0^{T} a\sin(\omega t + \phi)\,dt
 = \frac{a}{\omega T}\left(\cos\phi - \cos(\omega T + \phi)\right)$$

Turn the difference of cosines into a product with
$\cos A - \cos B = 2\sin\frac{A+B}{2}\sin\frac{B-A}{2}$, and with $\omega = 2\pi f$:

$$= a\,\frac{\sin(\pi f T)}{\pi f T}\,\sin(\pi f T + \phi)$$

The second sine carries the starting phase and cannot exceed one, so whatever phase the
mains happens to have when the conversion begins, the surviving interference is at most

$$a\left|\frac{\sin(\pi f T)}{\pi f T}\right|$$

This is the entire interference behaviour of an integrating meter, and it was derived
from "the reading is an average" and nothing else. It is 1 at $f = 0$, it falls away as
$1/\pi f T$, and — the useful part — it is **exactly zero whenever $fT$ is a whole
number**. Make the aperture a whole number of periods of the interference and the
average of that interference is zero at any starting phase.

That is what NPLC means. One power line cycle is 20 ms at 50 Hz and 16.67 ms at 60 Hz,
which is why the setting is quoted in cycles: the quantity that matters is how many
whole periods of the interference fit inside the window, and that depends on where the
instrument is standing.

## The numbers, and the surprise inside them

```python
import math


def surviving(f_hz, aperture_s):
    x = math.pi * f_hz * aperture_s
    return 1.0 if x == 0.0 else abs(math.sin(x) / x)


def rejection_db(m):
    return math.inf if m == 0.0 else -20.0 * math.log10(m)


for nplc in (0.02, 1, 10, 100):
    T = nplc / 50.0
    row = "%6.2f NPLC (%8.2f ms):" % (nplc, T * 1e3)
    for f in (50.0, 50.2, 50.5):
        m = surviving(f, T)
        row += "  %5.1f Hz %6.2f dB" % (f, rejection_db(m))
    print(row)
print("aperture set for 60 Hz, used on a 50 Hz supply: %.2f dB"
      % rejection_db(surviving(50.0, 1 / 60.0)))
```

```text
  0.02 NPLC (    0.40 ms):   50.0 Hz   0.01 dB   50.2 Hz   0.01 dB   50.5 Hz   0.01 dB
  1.00 NPLC (   20.00 ms):   50.0 Hz 328.18 dB   50.2 Hz  47.99 dB   50.5 Hz  40.09 dB
 10.00 NPLC (  200.00 ms):   50.0 Hz 322.60 dB   50.2 Hz  48.02 dB   50.5 Hz  40.23 dB
100.00 NPLC ( 2000.00 ms):   50.0 Hz 344.08 dB   50.2 Hz  50.41 dB   50.5 Hz 331.12 dB
aperture set for 60 Hz, used on a 50 Hz supply: 14.38 dB
```

The first row explains the dancing display: a 0.4 ms window is a fiftieth of a mains
cycle, the average over it is very nearly an instantaneous sample, and 0.01 dB of
rejection means the hum arrives essentially intact.

The 50.0 Hz column is a null. The three-hundred-odd decibels are the floating-point
arithmetic failing to represent zero exactly, and the honest reading of that column is
"exact".

Now compare 1 NPLC and 10 NPLC in the 50.2 Hz column: 47.99 dB against 48.02 dB. Ten
times the waiting has bought three hundredths of a decibel. That is worth understanding
rather than memorising. Write the line frequency as fractionally wrong by $\varepsilon$,
so over $n$ cycles $fT = n(1+\varepsilon)$. Then

$$\sin(\pi f T) = \sin(\pi n + \pi n\varepsilon) = \pm\sin(\pi n \varepsilon)
 \approx \pm\,\pi n \varepsilon$$

and dividing by $\pi f T \approx \pi n$ leaves $\varepsilon$. The $n$ cancels: the
surviving fraction is the *fractional frequency error itself*, no matter how many cycles
you integrate over. A supply 0.4% off leaves 0.4% of the hum, which is 48 dB, at 1 NPLC
and at 10 NPLC alike. The accumulated phase error grows exactly as fast as the longer
average shrinks it.

The last line is the one that costs people afternoons. A meter configured for a 60 Hz
supply and used on a 50 Hz one integrates for 16.67 ms, which is 0.833 of a cycle, and
its rejection collapses from exact to **14.4 dB**. That is one line-frequency setting in
a menu, and getting it wrong throws away almost everything the architecture was built to
provide.

## What you buy by waiting, and what you pay

```python
import math

OVERHEAD = 5e-3
base = None
for nplc in (0.02, 1, 10, 100):
    T = nplc / 50.0
    rate = 1.0 / (T + OVERHEAD)
    if base is None:
        base = T
    print("%6.2f NPLC: %8.2f readings/s, white noise x %.3f, mains 50.2 Hz %5.2f dB"
          % (nplc, rate, math.sqrt(base / T),
             -20.0 * math.log10(abs(math.sin(math.pi * 50.2 * T) / (math.pi * 50.2 * T)))))
```

```text
  0.02 NPLC:   185.19 readings/s, white noise x 1.000, mains 50.2 Hz  0.01 dB
  1.00 NPLC:    40.00 readings/s, white noise x 0.141, mains 50.2 Hz 47.99 dB
 10.00 NPLC:     4.88 readings/s, white noise x 0.045, mains 50.2 Hz 48.02 dB
100.00 NPLC:     0.50 readings/s, white noise x 0.014, mains 50.2 Hz 50.41 dB
```

Two different mechanisms, moving at different rates. Uncorrelated noise falls as the
square root of the aperture, forever: a factor of 70 down the column, and it would keep
going. Mains rejection leaps 48 dB on the first step, because a fraction of a cycle
became a whole one, and then goes essentially flat — a further hundredfold in waiting
buys 2.4 dB, and the last section explains why even that is an accident of where the
sinc ripple landed rather than a trend to rely on. Anyone who has turned the NPLC up and
watched the reading get quieter has seen the first mechanism and credited the second.

## The mistake, and why it is tempting

The mistake is treating NPLC as a volume control for interference. It is tempting
because the evidence supports it: turn it up and the reading visibly steadies, every
time, on every meter. What steadied was the white noise. If a hum is surviving because
the supply is not at the frequency the aperture assumed, a longer aperture will not
touch it, and you can spend a minute per reading discovering that. The right response is
to measure the line frequency and set the aperture to it, which is what a meter with
line-frequency tracking does automatically and what the front-panel line setting does by
hand.

The second mistake is thinking of NPLC as a time. Set 10 NPLC on a meter told it is on a
60 Hz supply and you get 167 ms; tell the same meter 50 Hz and you get 200 ms. Both are
"10 NPLC" and only one of them nulls the hum you have.

## Where this stops holding

The aperture is $T_1$ alone. The run-down, the auto-zero phase and the interval between
conversions are not integrating anything, so a meter delivering 4.88 readings a second
at 10 NPLC is averaging for 200 ms out of every 205 ms and is blind for the rest. What
happens during the blind interval is not rejected — it is missed, and a burst of
interference that lands there is invisible rather than averaged.

The small-$\varepsilon$ result has a range. Look at the 100 NPLC row: the prediction is
0.4% surviving, and the exact figure is 50.41 dB rather than 48. The approximation
$\sin(\pi n\varepsilon)\approx \pi n \varepsilon$ needs $\pi n \varepsilon \ll 1$, and
at $n = 100$, $\varepsilon = 0.004$ that product is 1.26 radians. Past that point the
rejection stops tracking $\varepsilon$ and starts wandering through the sinc function's
own ripples — which is also why the same row shows an exact null at 50.5 Hz, where
$fT = 101$ lands on a whole number by accident.

The $RC$ cancellation assumes the same $R$ and the same $C$ in both phases, with no
memory between them. Dielectric absorption is exactly memory: a capacitor that has been
charged one way for 200 ms gives a little of that charge back afterwards, and it does
not cancel. It is why the integrating capacitor in a real converter is polypropylene or
polystyrene rather than whatever was cheapest.

And most modern bench meters are not dual-slope at all; they are sigma-delta converters
whose line rejection comes from a digital decimation filter rather than one aperture.
The picture survives, because a boxcar average *is* a sinc and a multi-stage comb filter
is a $\text{sinc}^k$, but the nulls are broader — which makes the instrument more
forgiving of a wandering supply than the arithmetic above suggests.

Finally, none of this helps if the converter is fed by a sampler rather than an
integrator. A logger taking ten readings a second with no aperture worth the name does
not reject 50 Hz; it *folds* it, and 50 Hz being exactly five times 10 Hz means the hum
arrives as a constant offset whose size depends on when the run happened to start. A
constant is worse than a ripple, because a ripple can be recognised.

## What this module asks you to do

**Where the hum goes when you sample** is that last paragraph on a pair of sliders: set
the interferer and the sample rate and watch the alias land, including the case where it
lands at 0 Hz and disappears into your calibration.

**Why a dual-slope converter does not care what it is made of** is the derivation, and
its point is what is missing from the answer: not $R$, not $C$, not the clock. Arrange a
measurement so the imprecise things appear twice, once on each side, and cancel.

**What an aperture rejects, and what it costs** turns the two tables above into six
functions, ending at the practical question: given a required reading rate, what is the
largest whole NPLC you are allowed?
''',
            },
            "sandbox": {
                "title": "Where the hum goes when you sample",
                "visualiser": "spectrum",
                "minutes": 10,
                "initial": {"fsig": 50, "fs": 50},
                "brief": r'''
The upper panel is 100 ms of a sine in dim grey, the instants at which a converter takes
its samples as accent dots, and — when the two disagree — the wave those samples are
actually consistent with, in amber. The lower panel is the same story on a frequency
axis: the signal, the dashed purple Nyquist line at half the sample rate, and the amber
spike where the signal has been folded to.

Read the sine as 50 Hz mains interference on your input rather than as a signal you
want. The question is not whether it is there — it is — but where it ends up in the
record.
''',
                "notice": [
                    "The opening position takes 50 readings a second of a 50 Hz interferer. Every sample lands at the same point of the cycle, so the amber alias trace is a flat line and the lower panel puts the alias spike at 0 Hz: the hum has become a *constant*. The visualiser starts its sine at zero, so here that constant is zero and all six dots sit exactly on the axis — but a run that began a quarter of a cycle later would hold the full amplitude just as steadily, and that offset would be indistinguishable from the thing you were measuring. Note what this is *not*. An integrating converter rejects mains because it averages over a whole cycle, which comes to zero at any starting phase; point samples that happen to be commensurate with the line do not reject the hum, they freeze it.",
                    "Drag the sample rate down to 45 Hz. The alias lands at $50 - 45 = 5$ Hz, the amber trace now runs through every one of the five dots, and the record contains a 5 Hz wander that was never in the circuit. Nothing downstream can remove it: the samples are genuinely consistent with a 5 Hz signal.",
                    "Take the rate up to 200 Hz. The Nyquist line moves out to 100 Hz, the amber trace disappears, and the caption says nothing is lost. Notice what has *not* happened: the hum is still there, at 50 Hz, exactly as large as it was. Sampling faster did not remove the interference — it stopped disguising it, which is a different and much smaller favour than it looks.",
                    "Now set the signal to 240 Hz and the rate to 100 Hz. The alias appears at 40 Hz. There is nothing special about 50 Hz here: any frequency at all folds into the band, and a switching supply at 240 Hz is as capable of putting a false 40 Hz signal in your record as the mains is. Only something that removes it *before* the samples are taken can help.",
                    "Finally, signal 50 Hz and rate 100 Hz — exactly twice, the textbook minimum. The visualiser is content: the caption says the samples determine the wave uniquely. Look at the dots. Every one of them is at zero, because two samples per cycle taken at the zero crossings measure nothing at all. Nyquist's condition is *strictly* greater than twice, and this is the picture of the boundary case that the strict inequality exists to exclude.",
                ],
            },
            "quiz": {
                "title": "Apertures, counts and what the average throws away",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A 1 200 000-count meter's 10 V range runs to 12.00000 V. How much is one count?",
                        "opts": ["10 µV", "8.3 µV", "1 µV", "100 µV"],
                        "a": 0,
                        "why": r'''
$12\ \text{V}/1\,200\,000 = 10$ µV, which is why the display shows five decimal places on
that range. The 8.3 µV answer divides the 10 V *range name* by the count instead of the
full scale, and the difference between those two — 12 V of span on a range called 10 V —
is the overrange that lets the meter keep its resolution while the reading wanders above
nominal full scale. None of this says the last digit is *accurate*: at 35 ppm of reading
the specification allows 350 µV on a 10 V reading, which is 35 counts.
''',
                    },
                    {
                        "q": "In $V_{in} = V_{ref}T_2/T_1$, which of these does the answer NOT depend on?",
                        "opts": [
                            "the reference voltage",
                            "the value of the integrating capacitor",
                            "the ratio of the two intervals",
                            "the stability of the reference during the conversion",
                        ],
                        "a": 1,
                        "why": r'''
The capacitor — and the resistor, and the clock frequency — appear identically in both
slopes and divide out. That is the whole reason the architecture exists: it converts a
demand for a precise capacitor, which nobody can supply, into a demand for a precise
*reference* and a stable clock over 40 milliseconds, which everybody can. What is left
is genuinely load-bearing: the reference sets the scale directly, and the ratio of
intervals is the measurement itself.
''',
                    },
                    {
                        "q": "A meter is set to 10 NPLC on a 50 Hz supply. How long does one conversion's integration take?",
                        "opts": ["200 ms", "20 ms", "500 ms", "10 ms"],
                        "a": 0,
                        "why": r'''
One power line cycle at 50 Hz is 20 ms, so ten of them is 200 ms — five readings a
second before any overhead. On a 60 Hz supply the same setting would be 167 ms, which
is why NPLC is quoted in cycles rather than in milliseconds: the number that matters is
how many whole periods of the interference fit inside the aperture, and that depends on
where you are standing.
''',
                    },
                    {
                        "q": "Your converter's aperture is set for exactly 50.000 Hz and the supply is actually running at 50.2 Hz. Roughly how much of the mains interference survives?",
                        "opts": [
                            "none — the aperture is still a whole number of the converter's own cycles",
                            "about 0.4% of it, which is 48 dB of rejection",
                            "about 4% of it, which is 28 dB of rejection",
                            "all of it — the aperture no longer matches at all",
                        ],
                        "a": 1,
                        "why": r'''
The aperture is 20.000 ms and the interference now has a period of 19.920 ms, so the
average covers 1.004 cycles and the 0.004 of a cycle left over is what survives: the
rejection is $|\sin(\pi f T)/(\pi f T)|$, which comes to 0.00398, or 48.0 dB. The
useful shortcut is that the surviving fraction is about the fractional frequency error
itself — 0.4% of error, 0.4% of hum left, 48 dB. Mains frequency is held to far better
than this over minutes, which is why the technique works at all; it is short-term
excursions and generator supplies that spoil it.
''',
                    },
                    {
                        "q": "You raise the setting from 1 NPLC to 10 NPLC on that same 50.2 Hz supply. What actually improves?",
                        "opts": [
                            "the mains rejection, by a factor of ten",
                            "the mains rejection, by $\\sqrt{10}$",
                            "the white noise, by about $\\sqrt{10}$ — the mains rejection barely moves",
                            "nothing at all",
                        ],
                        "a": 2,
                        "why": r'''
Averaging for ten times as long reduces uncorrelated noise by $\sqrt{10}$, which is the
ordinary result from the last module of this course. The mains rejection, though, goes
from 48.0 dB to 48.0 dB: over ten cycles the accumulated phase error is ten times
larger, and it grows exactly as fast as the longer average shrinks it. This is worth
knowing before you spend a minute per reading trying to kill a hum that will not go —
if the interference is at a frequency the aperture cannot null, a longer aperture is
not the answer. A better answer is to measure the line frequency and set the aperture
to *it*, which is what a meter with line-frequency tracking does.
''',
                    },
                    {
                        "q": "A logger takes 10 readings a second, with no anti-alias filter and a negligible aperture. A 50 Hz hum on the input appears in the record as:",
                        "opts": [
                            "a 50 Hz ripple, correctly recorded",
                            "a 5 Hz beat",
                            "a constant offset, whose size depends on where in the cycle the samples happen to fall",
                            "nothing — 50 Hz is above the Nyquist limit, so it cannot be recorded",
                        ],
                        "a": 2,
                        "why": r'''
50 Hz is exactly five times 10 Hz, so every sample catches the hum at the same phase
and the whole interference collapses to a fixed offset — which might be zero, or might
be the full amplitude, depending on when the run happened to start. That is worse than
a visible ripple, because a ripple can be recognised and a constant cannot. Being above
Nyquist does not mean a signal is excluded; it means it is *folded*, and the folding
happens in the sampler, where no later filtering can reach it. The defence is a filter
in front of the converter, or an aperture long enough to average the hum away.
''',
                    },
                ],
            },
            "derive": {
                "title": "Why a dual-slope converter does not care what it is made of",
                "minutes": 13,
                "vars": ["V_in", "V_ref", "R", "C", "T_1", "T_2", "N_1", "N_2", "t_c"],
                "brief": r'''
An integrator: a resistor $R$ into the summing node of an amplifier with a capacitor $C$
in feedback, whose output ramps at $-V/RC$ volts per second for an input $V$.

The *summing node* is the inverting input of an operational amplifier with its feedback
closed round it, and module 4's reading derives why it sits at almost exactly zero volts
and takes no current for itself. Those are the two facts the ramp rate above depends on:
the whole of $V/R$ arrives at that node and has nowhere to go but into $C$. It is also
the reason $R$ is a real load on whatever is being measured — 100 kΩ of it, which is why
that module puts a follower in front.

The conversion has two phases. In the **run-up** the input is applied for a fixed time
$T_1$. In the **run-down** the input is disconnected and a reference $V_{ref}$ of the
opposite sign is applied instead, and a comparator stops the count at the instant the
integrator's output crosses zero again, after a time $T_2$.

Derive what the converter reports, and then notice what is missing from it.
''',
                "steps": [
                    {
                        "prompt": "Write the magnitude of the integrator's output at the end of the run-up, in terms of $V_{in}$, $R$, $C$ and $T_1$.",
                        "given": "The ramp rate is the input divided by $RC$, and it runs for $T_1$ from a starting value of zero.",
                        "answer": "\\frac{V_{in} T_1}{R C}",
                        "placeholder": "e.g. \\frac{a b}{c d}",
                        "hint": "Rate times time. The integrator started at zero because the converter shorts the capacitor before each conversion.",
                        "deconstruct": [
                            "The rate of change is $V_{in}/RC$.",
                            "It is constant for the whole of $T_1$.",
                        ],
                    },
                    {
                        "prompt": "During the run-down the reference drives the same integrator the other way. Write the magnitude of the fall in time $T_2$.",
                        "given": "The same $R$ and the same $C$: the switch changed what is applied to the resistor, and nothing else.",
                        "answer": "\\frac{V_{ref} T_2}{R C}",
                        "placeholder": "e.g. \\frac{a b}{c d}",
                        "hint": "The identical expression with the reference in place of the input, and the second interval in place of the first.",
                        "deconstruct": [
                            "The rate is now $V_{ref}/RC$, in the opposite direction.",
                            "It runs for $T_2$.",
                        ],
                    },
                    {
                        "prompt": "The run-down ends when the output is back at zero, so the fall equals the rise. Solve for $V_{in}$.",
                        "given": "Set the two expressions equal and cancel everything that appears on both sides.",
                        "answer": "\\frac{V_{ref} T_2}{T_1}",
                        "placeholder": "e.g. \\frac{a b}{c}",
                        "hint": "$RC$ is a common factor of both sides and divides out.",
                        "deconstruct": [
                            "$V_{in}T_1/RC = V_{ref}T_2/RC$.",
                            "Multiply both sides by $RC$: $V_{in}T_1 = V_{ref}T_2$.",
                            "Divide by $T_1$.",
                        ],
                    },
                    {
                        "prompt": "Both intervals are measured by counting cycles of one clock of period $t_c$, so $T_1 = N_1t_c$ and $T_2 = N_2t_c$. Write $V_{in}$ in terms of the two counts.",
                        "given": "Substitute both, and cancel.",
                        "answer": "\\frac{V_{ref} N_2}{N_1}",
                        "placeholder": "e.g. \\frac{a b}{c}",
                        "hint": "$t_c$ appears once on the top and once on the bottom.",
                        "deconstruct": [
                            "$V_{in} = V_{ref}N_2t_c/(N_1t_c)$.",
                            "The clock period cancels.",
                        ],
                    },
                ],
                "closing": r'''
Look at what is *not* in the final line. Not $R$, not $C$, not the clock frequency, not
the amplifier's gain, not the comparator's threshold — provided none of them changes
between the run-up and the run-down, a few tens of milliseconds later. All that survives
is the reference and a ratio of two integer counts, and integers are exact.

That is why a converter built from an ordinary resistor and an ordinary capacitor can
be a parts-per-million instrument, and it is the single most important architectural
idea in bench measurement: arrange the measurement so that the imprecise things appear
twice, once on each side, and cancel.

$N_1$ is fixed by the designer, and choosing it to make $T_1$ a whole number of power
line cycles is free — the run-up is an average of the input over exactly that time, and
the average of mains hum over a whole number of its own periods is zero. The
architecture that makes the parts cancel also, for nothing, rejects the interference
those parts sit in.
''',
            },
            "lab": {
                "title": "What an aperture rejects, and what it costs",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
An integrating converter averages its input over an aperture $T$. Averaging a sine of
frequency $f$ over a window of length $T$ leaves a fraction

$$\left|\frac{\sin(\pi f T)}{\pi f T}\right|$$

of it — a function that is 1 at DC, has zeros wherever $fT$ is a whole number, and falls
away as $1/\pi f T$ in between. That single expression is the whole of an integrating
meter's interference behaviour, and these six functions turn it into the numbers on a
front panel.

- `aperture(nplc, line_hz)` — the integration time in seconds for that many power line
  cycles.
- `sinc_magnitude(f_hz, aperture_s)` — the expression above, as a plain ratio. At
  $f = 0$ the formula is $0/0$; the limit is 1, and your code has to say so.
- `rejection_db(f_hz, aperture_s)` — the same thing as a positive number of decibels of
  rejection, so more is better. Return `math.inf` if the magnitude is exactly zero.
- `line_rejection_db(nplc, line_hz, actual_hz)` — the rejection you actually get when
  the aperture was set for `line_hz` and the supply is running at `actual_hz`.
- `readings_per_second(nplc, line_hz, overhead_s)` — conversions per second, with a
  fixed overhead between them.
- `largest_nplc(rate, line_hz, overhead_s)` — the largest *whole* NPLC that still
  achieves `rate` readings per second. Raise `ValueError` if even 1 NPLC is too slow.

Only `math` is needed.
''',
                "files": [{"name": "main.py", "content": r'''
"""The aperture of an integrating converter: what it rejects, and what it costs."""

import math


def aperture(nplc, line_hz):
    """Integration time in seconds for this many power line cycles."""
    # TODO: cycles divided by cycles per second.
    return 0.0


def sinc_magnitude(f_hz, aperture_s):
    """|sin(pi f T) / (pi f T)| — the gain an average over T has at frequency f."""
    # TODO: guard the zero-frequency case, where the limit is 1.
    return 0.0


def rejection_db(f_hz, aperture_s):
    """Rejection in dB (positive means rejected) of a sine at f_hz."""
    # TODO: -20 log10 of the magnitude, and math.inf at an exact null.
    return 0.0


def line_rejection_db(nplc, line_hz, actual_hz):
    """Rejection obtained when the aperture was set for line_hz and the
    supply is actually running at actual_hz."""
    # TODO: one aperture, evaluated at the frequency that is really there.
    return 0.0


def readings_per_second(nplc, line_hz, overhead_s):
    """Conversions per second, including a fixed overhead between them."""
    # TODO: one over the total time for one reading.
    return 0.0


def largest_nplc(rate, line_hz, overhead_s):
    """Largest whole NPLC that still achieves `rate` readings per second."""
    # TODO: work out the time budget, convert it to cycles, take the floor,
    # and refuse the job if even one cycle will not fit.
    return 0


if __name__ == "__main__":
    t = aperture(1, 50.0)
    print("1 NPLC at 50 Hz is", t, "s")
    print("  rejection at 50 Hz  ", rejection_db(50.0, t), "dB")
    print("  rejection at 25 Hz  ", rejection_db(25.0, t), "dB")
    print("  rejection at 75 Hz  ", rejection_db(75.0, t), "dB")
    for n in (1, 10, 100):
        print("  %3d NPLC on a 50.2 Hz supply: %6.2f dB"
              % (n, line_rejection_db(n, 50.0, 50.2)))
    print("1 NPLC + 5 ms overhead gives", readings_per_second(1, 50.0, 0.005), "readings/s")
    print("10 readings/s allows at most", largest_nplc(10.0, 50.0, 0.005), "NPLC")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The aperture of an integrating converter: what it rejects, and what it costs."""

import math


def aperture(nplc, line_hz):
    """Integration time in seconds for this many power line cycles."""
    return nplc / line_hz


def sinc_magnitude(f_hz, aperture_s):
    """|sin(pi f T) / (pi f T)| — the gain an average over T has at frequency f."""
    x = math.pi * f_hz * aperture_s
    if x == 0.0:
        return 1.0
    return abs(math.sin(x) / x)


def rejection_db(f_hz, aperture_s):
    """Rejection in dB (positive means rejected) of a sine at f_hz."""
    m = sinc_magnitude(f_hz, aperture_s)
    if m == 0.0:
        return math.inf
    return -20.0 * math.log10(m)


def line_rejection_db(nplc, line_hz, actual_hz):
    """Rejection obtained when the aperture was set for line_hz and the
    supply is actually running at actual_hz."""
    return rejection_db(actual_hz, aperture(nplc, line_hz))


def readings_per_second(nplc, line_hz, overhead_s):
    """Conversions per second, including a fixed overhead between them."""
    return 1.0 / (aperture(nplc, line_hz) + overhead_s)


def largest_nplc(rate, line_hz, overhead_s):
    """Largest whole NPLC that still achieves `rate` readings per second."""
    budget = 1.0 / rate - overhead_s
    n = math.floor(budget * line_hz)
    if n < 1:
        raise ValueError(
            "%g readings/s leaves %g s for the conversion, which is less than one "
            "cycle of a %g Hz supply" % (rate, budget, line_hz)
        )
    return n


if __name__ == "__main__":
    t = aperture(1, 50.0)
    print("1 NPLC at 50 Hz is", t, "s")
    print("  rejection at 50 Hz  ", rejection_db(50.0, t), "dB")
    print("  rejection at 25 Hz  ", rejection_db(25.0, t), "dB")
    print("  rejection at 75 Hz  ", rejection_db(75.0, t), "dB")
    for n in (1, 10, 100):
        print("  %3d NPLC on a 50.2 Hz supply: %6.2f dB"
              % (n, line_rejection_db(n, 50.0, 50.2)))
    print("1 NPLC + 5 ms overhead gives", readings_per_second(1, 50.0, 0.005), "readings/s")
    print("10 readings/s allows at most", largest_nplc(10.0, 50.0, 0.005), "NPLC")
'''}],
                "hints": [
                    "`sinc_magnitude` needs its zero-frequency guard before the division, not after: at $f = 0$ the expression is $0/0$ and Python raises rather than taking a limit.",
                    "`rejection_db` is `-20 * math.log10(m)`. The sign is the awkward part — the magnitude is below 1, so its logarithm is negative, and the minus turns the answer into decibels *of rejection*.",
                    "`line_rejection_db` should call the two functions you already have. The aperture was chosen for the frequency you believed; the rejection is evaluated at the frequency that is actually there.",
                    "For `largest_nplc`: one reading takes `nplc / line_hz + overhead_s`, and that must be at most `1 / rate`. Rearranged, `nplc <= line_hz * (1 / rate - overhead_s)`, and `math.floor` of that is the answer — with a check that it did not come out below 1.",
                ],
                "tests": [
                    {"name": "the aperture is cycles over frequency", "code": r'''
assert abs(aperture(1, 50.0) - 0.02) < 1e-15, "1 NPLC at 50 Hz is 20 ms"
assert abs(aperture(10, 60.0) - 0.16666666666666666) < 1e-15, \
    "10 NPLC at 60 Hz is 166.7 ms"
assert abs(aperture(0.02, 50.0) - 4e-4) < 1e-18, "0.02 NPLC at 50 Hz is 400 us"
'''},
                    {"name": "the shape of the sinc", "code": r'''
assert abs(sinc_magnitude(0.0, 0.02) - 1.0) < 1e-15, \
    "at DC the average passes everything; the limit of sin(x)/x is 1"
half = sinc_magnitude(25.0, 0.02)
assert abs(half - 0.6366197723675814) < 1e-12, \
    f"half the line frequency fits half a period in the window: 2/pi, got {half}"
assert sinc_magnitude(50.0, 0.02) < 1e-12, \
    "a whole period in the window averages to zero"
assert sinc_magnitude(100.0, 0.02) < 1e-12, "so does two whole periods"
worst = sinc_magnitude(75.0, 0.02)
assert abs(worst - 0.21220659078919377) < 1e-12, \
    f"between the nulls the leak is 2/(3 pi), got {worst}"
'''},
                    {"name": "decibels, and the null", "code": r'''
d = rejection_db(25.0, 0.02)
assert abs(d - 3.9223975406030527) < 1e-9, \
    f"half the line frequency is rejected by only 3.92 dB, got {d}"
assert abs(rejection_db(75.0, 0.02) - 13.4648226349963) < 1e-9, \
    "1.5 times the line frequency is rejected by 13.46 dB"
assert rejection_db(50.0, 0.02) > 250, \
    "at the null the arithmetic runs out of floating point long before the physics does"
assert abs(rejection_db(0.0, 0.02)) < 1e-12, "an average does not reject DC at all"
'''},
                    {"name": "a supply that is not quite where you thought", "code": r'''
one = line_rejection_db(1, 50.0, 50.2)
assert abs(one - 47.99370303427637) < 1e-6, \
    f"0.4% of frequency error leaves 48.0 dB of rejection, got {one}"
ten = line_rejection_db(10, 50.0, 50.2)
assert abs(ten - one) < 0.1, \
    "ten times the aperture must NOT give ten times the rejection: the accumulated " \
    "phase error grows as fast as the averaging shrinks it"
tight = line_rejection_db(1, 50.0, 50.05)
assert abs(tight - 60.00869583730649) < 1e-6, \
    f"0.1% of error is 60 dB, which is the rule of thumb worth carrying, got {tight}"
assert line_rejection_db(1, 50.0, 60.0) < 20, \
    "an aperture set for 50 Hz is nearly useless against a 60 Hz supply"
'''},
                    {"name": "digits cost time", "code": r'''
r = readings_per_second(1, 50.0, 0.005)
assert abs(r - 40.0) < 1e-12, f"20 ms plus 5 ms is 25 ms, so 40 a second, got {r}"
slow = readings_per_second(10, 50.0, 0.005)
assert abs(slow - 4.878048780487805) < 1e-12, \
    f"10 NPLC plus the same overhead is 4.88 a second, got {slow}"
assert slow < r / 8, "ten times the aperture costs nearly ten times the time"
'''},
                    {"name": "choosing the setting a rate can afford", "code": r'''
assert largest_nplc(10.0, 50.0, 0.005) == 4, \
    "10 readings/s leaves 95 ms, which is 4.75 cycles: four whole ones"
assert largest_nplc(2.0, 50.0, 0.005) == 24, "2 readings/s allows 24 NPLC"
assert largest_nplc(1.0, 60.0, 0.01) == 59, "1 reading/s on a 60 Hz supply allows 59"
assert isinstance(largest_nplc(10.0, 50.0, 0.005), int), "NPLC settings are whole"
raised = False
try:
    largest_nplc(200.0, 50.0, 0.005)
except ValueError:
    raised = True
assert raised, \
    "200 readings a second leaves no room for a single cycle; refuse rather than round"
'''},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "The Wheatstone bridge",
            "summary": "Two dividers, one excitation, and a difference. It is how a resistance change of one part in a thousand becomes a voltage you can amplify.",
            "concepts": [
                "A bridge is two voltage dividers across one excitation, read as the difference between their midpoints: $V_o = V_{ex}\\left(\\frac{R_2}{R_1+R_2} - \\frac{R_4}{R_3+R_4}\\right)$, with $R_2$ and $R_4$ the lower arms.",
                "The bridge balances — $V_o = 0$ — when $R_1/R_2 = R_3/R_4$. Balance is a condition on *ratios*, so it does not depend on the excitation voltage at all.",
                "That is why a null measurement is the most accurate kind: at balance the excitation may drift, and the reading stays zero. Only its *stability during the reading* matters, never its calibration.",
                "In a quarter bridge one arm is a sensor of resistance $R(1+x)$ and the other three are fixed at $R$. Then $V_o = V_{ex}\\,x/(4+2x)$, which is $V_{ex}x/4$ for small $x$ and never exactly that.",
                "Reading a quarter bridge with the linear formula therefore under-reads by a fraction $x/(2+x)$, about $x/2$: at $x = 1\\%$ the strain you infer is 0.5% low. Half and full bridges cancel this term exactly.",
                "A strain gauge converts strain to resistance through its gauge factor: $x = G\\varepsilon$, with $G \\approx 2$ for foil gauges. A 1000 µε strain on a 350 Ω gauge is 0.7 Ω, and at 5 V excitation that is 2.5 mV — which is what the instrumentation amplifier is for.",
                "Each arm dissipates $V_{ex}^2/4R$ when the bridge is balanced with equal arms, so doubling the excitation doubles the signal and quadruples the self-heating. For a platinum resistance thermometer, self-heating is a temperature error that looks exactly like the temperature you are trying to measure.",
                "Lead resistance in series with a remote sensor adds directly to its arm and is indistinguishable from signal. The three-wire connection puts an equal length of lead in the adjacent arm so that the two cancel to first order.",
                "If the excitation also serves as the reference of the analogue-to-digital converter, the conversion is *ratiometric*: excitation drift divides out of the final number and stops being an error source at all.",
            ],
            "read": {
                "title": "Subtracting a divider from itself",
                "minutes": 16,
                "body": r'''
A foil strain gauge is glued to a steel beam. It is 350.0 Ω, its gauge factor is 2.00,
and when somebody stands on the beam the steel stretches by 1000 microstrain — a large
but entirely ordinary strain, about a millimetre per metre. The gauge's resistance
therefore changes by

$$\Delta R = R\,G\,\varepsilon = 350.0 \times 2.00 \times 10^{-3} = 0.700\,\Omega$$

so it goes from 350.000 Ω to 350.700 Ω. A 6½-digit ohmmeter can resolve that a thousand
times over. Try to measure it that way anyway and watch what happens.

The gauge is thirty metres from the instrument, on two copper leads of 1.5 Ω each. That
is 3 Ω added to the 350 Ω — four times the whole signal, before the beam is touched.
Worse, copper's resistance rises by 0.39% per kelvin, so a one-degree change in the
temperature of the cable run is $3 \times 0.0039 = 0.0117$ Ω, which is **1.7% of the
strain signal**, from nothing but the sun coming out. The gauge itself has a temperature
coefficient too. Every one of those effects lands in the same digits as the measurement,
and none of them is distinguishable from it.

The whole difficulty is that 0.700 Ω has to be found on top of 350.000 Ω. What is
needed is a way of asking about the *change* without asking about the resistance.

## Subtract a divider that did not move

Put the gauge in the lower half of a voltage divider — a fixed 350 Ω above it, both
across an excitation $V_{ex}$ — and its midpoint sits at $V_{ex}R_2/(R_1+R_2)$. That
midpoint moves when the gauge moves, and it also moves when the excitation drifts, when
the leads warm, when everything warms.

Now build a second divider of two fixed 350 Ω resistors across the *same* excitation,
and read the difference between the two midpoints:

$$V_o = V_{ex}\left(\frac{R_2}{R_1+R_2} - \frac{R_4}{R_3+R_4}\right)$$

That is a Wheatstone bridge, and it is two dividers and a subtraction. The subtraction
is the entire idea: anything that moves both midpoints together leaves the difference
alone.

Set the difference to zero and the condition falls out with no work:

$$\frac{R_2}{R_1+R_2} = \frac{R_4}{R_3+R_4}
\quad\Leftrightarrow\quad
\frac{R_1}{R_2} = \frac{R_3}{R_4}$$

Balance is a condition on *ratios*, and $V_{ex}$ is nowhere in it. So a bridge adjusted
to null is a measurement whose answer does not depend on the excitation being accurate,
or stable, or even known: multiplying zero by a drifting number leaves zero. That is why
a null method beats a deflection method, and it is the same reason a beam balance beats
a spring scale.

## What one arm moving is worth

Let three arms be $R$ and the lower left one be $R(1+x)$. The left midpoint is a
fraction $(1+x)/(2+x)$ of the excitation — every $R$ cancels, which is the second sign
that a bridge only sees proportions — and the right midpoint is exactly a half.
Subtracting over the common denominator $2(2+x)$:

$$\frac{V_o}{V_{ex}} = \frac{2(1+x) - (2+x)}{2(2+x)} = \frac{x}{4+2x}$$

For small $x$ that is $x/4$, and the 4 is worth understanding rather than memorising. It
is the slope of the divider: differentiate $(1+x)/(2+x)$ at $x = 0$ and you get exactly
$1/4$. An equal-arm divider moves by a quarter of the fractional change in one of its
arms, and the reference branch contributes nothing because nothing in it moved.

Carry the beam all the way through. With $x = G\varepsilon = 0.00200$:

```python
R, GAUGE_FACTOR, STRAIN = 350.0, 2.00, 1000e-6
x = GAUGE_FACTOR * STRAIN
print("dR = %.4f ohm, x = %.5f (%.3f %% of the arm)" % (R * x, x, 100 * x))
for vex in (2.0, 5.0, 10.0):
    vo = vex * x / (4.0 + 2.0 * x)
    i = vex / (2.0 * R)
    print("  Vex %5.2f V: Vo %7.4f mV, arm current %6.3f mA, arm power %7.3f mW"
          % (vex, vo * 1e3, i * 1e3, i * i * R * 1e3))
```

```text
dR = 0.7000 ohm, x = 0.00200 (0.200 % of the arm)
  Vex  2.00 V: Vo  0.9990 mV, arm current  2.857 mA, arm power   2.857 mW
  Vex  5.00 V: Vo  2.4975 mV, arm current  7.143 mA, arm power  17.857 mW
  Vex 10.00 V: Vo  4.9950 mV, arm current 14.286 mA, arm power  71.429 mW
```

At 5 V excitation the answer is **2.4975 mV**, and that number is the whole reason
module 7 exists: two and a half millivolts, riding on a 2.5 V common-mode pedestal,
arriving on thirty metres of cable in a building with volts of mains on its floor.

## The price of turning the excitation up

Read the last two columns of that table together. Going from 2 V to 5 V multiplies the
output by two and a half and the power in the arm by six and a quarter; going from 2 V
to 10 V multiplies the output by five and the power by twenty-five. Each arm carries
$V_{ex}/2R$ and dissipates

$$P = \left(\frac{V_{ex}}{2R}\right)^{2}R = \frac{V_{ex}^{2}}{4R}$$

Signal is linear in the excitation; heating is quadratic. Nearly 18 mW in a foil gauge
bonded to a thin section will warm it measurably, and the gauge's own temperature
coefficient turns that into apparent strain.

For a temperature sensor the same trade is far worse, because the error is in the
measured quantity itself. A Pt1000 in a 2 V bridge carries 1.000 mA and dissipates
1.000 mW; a sensor with a self-heating coefficient of 0.5 K/mW in still air is then
reading half a kelvin high, permanently, on an instrument sold as good to a tenth. The
inversion cannot detect it: a self-heated sensor is genuinely at that temperature.
Rearranging $P = V_{ex}^2/4R$ gives the ceiling $V_{ex} = 2\sqrt{P_{max}R}$, which for
5 mW in a 350 Ω arm is 2.646 V.

## Where the linear formula runs out

Inverting the exact relation the other way, someone reading the bridge and computing
$\hat{x} = 4V_o/V_{ex}$ gets $\hat{x} = 2x/(2+x)$, which is low by a fraction
$-x/(2+x)$ — about $x/2$.

```text
   x = 0.002  (strain gauge, 1000 ue)   the linear formula is  0.100 % low
   x = 0.010  (strain gauge at its limit)                      0.498 % low
   x = 0.100  (Pt100 over 25 kelvin)                           4.762 % low
   x = 0.500  (thermistor over its range)                     20.000 % low
```

At 1000 µε the nonlinearity costs 1 µε out of 1000, which nobody will ever find. On a
thermistor changing by tens of per cent it dominates every other error in the system.
The rule is not "the bridge is linear"; it is "the bridge is nonlinear by about half the
fractional change", and whether that matters is arithmetic you do once per sensor.

## The leads, which is where this started

The three-wire connection is the answer to the opening paragraph. Run a third conductor
to the remote sensor and arrange the wiring so that one lead sits in the sensor's arm
and an identical lead sits in the arm next to it. Both leads are the same copper, the
same length, at the same temperature, so their resistances appear on both sides of the
balance ratio and cancel to first order. The 3 Ω is still physically in the circuit;
what has gone is its *effect*.

The other half is ratiometric conversion. If the same excitation that drives the bridge
is also the reference of the converter reading it, then the converter reports
$V_o/V_{ex}$ rather than $V_o$, and the excitation divides out of the final number
completely. It stops being an error source instead of being a well-controlled one, which
is cheaper and better.

## The mistake, and why it is tempting

Turn the excitation up. Every piece of evidence in front of you supports it: the output
doubles, the reading gets visibly cleaner because the amplifier's noise and offset have
not changed, and no other knob in instrumentation gives signal away for free. What it is
doing is heating the sensor quadratically, and for a temperature sensor the result looks
exactly like the thing being measured — not noise, not drift, but a plausible, stable,
repeatable temperature that is wrong. The trade is signal against self-heating and it is
1:2 in the exponents, so the honest way to pick an excitation is to start from the power
the sensor is allowed and work backwards.

The second mistake is carrying $V_o = V_{ex}x/4$ from a strain gauge to a thermistor. It
is tempting because it is correct where most people first meet it, to a part in a
thousand, and nothing about the formula announces that its error grows with $x$. The
fix is to use the exact inversion $x = 4V_o/(V_{ex}-2V_o)$ always, which costs one
subtraction and never has to be revisited.

## Where this stops holding

The detector is assumed to draw nothing. It does not. Looking into the two midpoints of
a balanced equal-arm bridge with the excitation shorted, each branch contributes
$R\parallel R = R/2$, so the differential Thévenin resistance across the pair is $R$ and
the resistance at either midpoint alone is $R/2$. Read a 350 Ω bridge differentially
with an amplifier of 10 kΩ across the pair and it comes out 3.4% low; hang 10 kΩ on one
midpoint only, which is what a bare difference stage does, and that midpoint alone is
1.7% low. Either figure is a systematic error more than thirty times the nonlinearity
being fussed over above, and it is why module 7 insists that an instrumentation
amplifier's two input buffers are not a luxury.

The excitation is assumed to be a voltage source. Drive the bridge from a current source
instead and every expression above changes, generally in the direction of better
linearity, which is why precision resistance thermometry often does exactly that.

The lead cancellation is first order and needs the two leads genuinely matched: same
gauge, same length, same run, same temperature. A three-wire sensor with one lead taped
to a hot pipe is a two-wire sensor with extra confidence.

And the nonlinearity result belongs to a *quarter* bridge. Put sensors in two opposite
arms so that one rises as the other falls and the $2x$ in the denominator cancels
exactly, giving $V_o = V_{ex}x/2$ with no error term at all — twice the signal and
perfect linearity, which is why load cells are built as full bridges and why the
quarter-bridge arithmetic on this page is the awkward case rather than the general one.

## What this module asks you to do

**The quarter bridge, exactly and then approximately** makes you produce the
$x/(4+2x)$ above step by step and then price the linear shortcut, ending at the
$-x/(2+x)$ that the table uses.

**A bridge, its sensitivity and its limits** turns all of it into five functions: the
general four-arm output, the quarter bridge written as one call to it, the
nonlinearity, an exact inversion that must round-trip to twelve figures, and the
excitation ceiling $2\sqrt{P_{max}R}$. The round-trip test is the one that matters —
it is the difference between a formula that works on a strain gauge and one that works
on a sensor.
''',
            },
            "quiz": {
                "title": "Balance, sensitivity and the price of excitation",
                "minutes": 10,
                "questions": [
                    {
                        "q": "The left branch of a bridge is 1 kΩ on top and 2 kΩ below. The right branch has 4.7 kΩ on top. What lower arm balances the bridge?",
                        "opts": ["2.35 kΩ", "9.4 kΩ", "4.7 kΩ", "2 kΩ"],
                        "a": 1,
                        "why": r'''
Balance needs $R_1/R_2 = R_3/R_4$, so $R_4 = R_3R_2/R_1 = 4.7\text{k} \times 2 = 9.4$ kΩ.
The two branches must have the same *ratio*, not the same resistances: 1:2 on the left
has to be matched by 4.7:9.4 on the right. Answering 2.35 kΩ inverts the ratio, which
is the commonest slip; check by asking which side of each branch is the larger one —
both lower arms must be the bigger of their pair.
''',
                    },
                    {
                        "q": "You balance a bridge by adjusting one arm until the detector reads zero. Your excitation supply then drifts by 2%. What happens to the balance point?",
                        "opts": [
                            "the reading moves by 2%",
                            "the reading moves by 1%",
                            "nothing — zero times anything is still zero",
                            "the balance point shifts to a different arm value",
                        ],
                        "a": 2,
                        "why": r'''
Nothing. The output is $V_{ex}$ multiplied by a difference of two ratios, and at
balance that difference is exactly zero: scaling zero changes nothing. This is what
makes a null method so much better than a deflection method — the accuracy of the
excitation drops out of the result entirely, and all that is left is how well you can
detect zero. It is the same reason a beam balance beats a spring scale.
''',
                    },
                    {
                        "q": "A Pt1000 sits in one arm of a bridge whose other three arms are 1000 Ω, excited at 2.000 V. The sensor rises to 1003.85 Ω. What is the output?",
                        "opts": ["1.92 mV", "3.85 mV", "7.70 mV", "0.96 mV"],
                        "a": 0,
                        "why": r'''
$V_o = V_{ex}x/(4+2x)$ with $x = 3.85/1000$, which gives 1.9213 mV — near enough
$V_{ex}x/4 = 1.925$ mV. The factor of four is the thing to remember, and it comes from
the divider alone: differentiate the sensor branch's $(1+x)/(2+x)$ at $x = 0$ and you
get exactly $1/4$, so an equal-arm divider moves by a quarter of the fractional change
in one of its arms. The reference branch adds nothing, because none of its arms moved.
Answering 3.85 mV forgets both the excitation and the four.
''',
                    },
                    {
                        "q": "A quarter bridge is read with the linear formula $x = 4V_o/V_{ex}$ when the true $x$ is 0.01. The inferred value is:",
                        "opts": ["exact", "0.5% low", "0.5% high", "2% low"],
                        "a": 1,
                        "why": r'''
The exact output is $V_{ex}x/(4+2x)$, so the linear inversion returns
$x/(1+x/2)$ — low by $x/(2+x) = 0.4975\%$. The rule of thumb is that a quarter bridge
is nonlinear by about half the fractional resistance change. For a strain gauge at
1000 µε that is a 0.1% error and usually ignorable; for a thermistor changing by tens
of per cent it dominates everything else, and you either use the exact inversion or a
bridge configuration that cancels it.
''',
                    },
                    {
                        "q": "You double the excitation of a balanced equal-arm bridge to get more signal. What happens to the power dissipated in the sensor?",
                        "opts": ["unchanged", "doubles", "quadruples", "halves"],
                        "a": 2,
                        "why": r'''
Each arm carries $V_{ex}/2R$ and dissipates $V_{ex}^2/4R$, so doubling the excitation
doubles the signal and multiplies the heating by four. That trade is the whole of
excitation design: signal goes up linearly, self-heating goes up quadratically, and for
a temperature sensor the self-heating is not merely a nuisance but an error in the
measured quantity itself. Answering 'doubles' is reading $P = VI$ while holding the
current fixed, but the current doubles too.
''',
                    },
                    {
                        "q": "A remote 100 Ω platinum sensor is wired to a bridge with two long leads of 1.5 Ω each. What does the three-wire connection achieve?",
                        "opts": [
                            "it removes the lead resistance from the circuit entirely",
                            "it doubles the sensitivity by using both leads as signal",
                            "it lowers the total lead resistance to 0.75 Ω by paralleling the leads",
                            "it puts an equal lead in the adjacent arm, which cancels it",
                        ],
                        "a": 3,
                        "why": r'''
The third wire lets one lead sit in the sensor's arm and an identical lead in the
neighbouring arm, so their equal resistances — and, more importantly, their equal
temperature coefficients — cancel to first order in the ratio that sets balance. The
resistance is still physically there; what has gone is its *effect*. Nothing removes
lead resistance from the circuit, and 3 Ω added to a 100 Ω sensor would otherwise read
as about 7.7 °C of temperature that is not there.
''',
                    },
                ],
            },
            "derive": {
                "title": "The quarter bridge, exactly and then approximately",
                "minutes": 14,
                "vars": ["V_o", "V_ex", "R", "x", "G", "epsilon"],
                "brief": r'''
Four arms across an excitation $V_{ex}$. Three of them are $R$; the lower left one is
a sensor whose resistance has moved to $R(1+x)$, where $x$ is the fractional change —
a few parts per thousand for a strain gauge, a few per cent for a resistance
thermometer over its range.

The output is the left midpoint minus the right midpoint. Derive it exactly, then find
out what the usual linear formula costs you.
''',
                "steps": [
                    {
                        "prompt": "Write the left midpoint as a fraction of $V_{ex}$. The upper arm is $R$, the lower is $R(1+x)$.",
                        "given": "An ordinary divider, with the output taken across the lower arm.",
                        "answer": "\\frac{1+x}{2+x}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "The fraction is lower arm over total. Every $R$ cancels, which is the first sign that a bridge only cares about ratios.",
                        "deconstruct": [
                            "The fraction is $R(1+x) / (R + R(1+x))$.",
                            "Take $R$ out of the top and bottom and it cancels.",
                        ],
                    },
                    {
                        "prompt": "The right-hand branch is two equal arms, so its midpoint sits at exactly half the excitation. Write $V_o/V_{ex}$, the left fraction minus the right.",
                        "given": "Put the difference over a single denominator and simplify.",
                        "answer": "\\frac{x}{4+2x}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Subtract $1/2$ from the fraction you just found, over the common denominator $2(2+x)$.",
                        "deconstruct": [
                            "$\\frac{1+x}{2+x} - \\frac{1}{2} = \\frac{2(1+x) - (2+x)}{2(2+x)}$.",
                            "The numerator is $2 + 2x - 2 - x = x$.",
                            "So the result is $x/(2(2+x))$, which is $x/(4+2x)$.",
                        ],
                    },
                    {
                        "prompt": "For $x \\ll 1$ the denominator is nearly 4. Write the small-signal approximation for $V_o$ itself, in terms of $V_{ex}$ and $x$.",
                        "answer": "\\frac{V_{ex} x}{4}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Drop the $2x$ next to the 4 and multiply back through by $V_{ex}$.",
                        "deconstruct": [
                            "$V_o = V_{ex}\\,x/(4+2x)$.",
                            "With $2x$ negligible beside 4, the denominator is just 4.",
                        ],
                    },
                    {
                        "prompt": "Someone reads the bridge and infers $\\hat{x} = 4V_o/V_{ex}$. Write the fractional error $(\\hat{x}-x)/x$ of that inference, in terms of $x$.",
                        "given": "Substitute the exact $V_o$ from step 2 into $\\hat{x} = 4V_o/V_{ex}$ first.",
                        "answer": "-\\frac{x}{2+x}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "You will find $\\hat{x} = 4x/(4+2x)$. Divide that by $x$, subtract 1, and tidy up.",
                        "deconstruct": [
                            "$\\hat{x} = 4x/(4+2x) = 2x/(2+x)$.",
                            "$\\hat{x}/x = 2/(2+x)$.",
                            "Subtracting 1 gives $(2 - 2 - x)/(2+x) = -x/(2+x)$.",
                        ],
                    },
                ],
                "closing": r'''
The last line is the bridge's nonlinearity, and it is negative: the linear formula
always under-reads a positive $x$. Its size is about $x/2$, so a 1% resistance change
is inferred 0.5% low, and a 0.1% change 0.05% low — which is why strain gauge work
mostly ignores it and thermistor work never can.

Two things are worth noticing about the algebra. First, $R$ vanished in step 1 and
never came back: the output depends on the *fractional* change, not on whether the
sensor is 120 Ω or 1 kΩ. Second, every term still carries a factor of $V_{ex}$, so
doubling the excitation doubles the output — and that is the temptation the
self-heating limit exists to resist.
''',
            },
            "lab": {
                "title": "A bridge, its sensitivity and its limits",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Five functions that between them size a bridge and read it back.

- `bridge_output(vex, r1, r2, r3, r4)` — the general four-arm result, with `r2` and
  `r4` the lower arms and the output taken as left midpoint minus right midpoint.
- `quarter_output(vex, r, dr)` — three arms at `r`, the lower left at `r + dr`. Write
  it as one call to `bridge_output`, not as a second copy of the algebra.
- `nonlinearity(x)` — the fractional error of inferring $x$ from the linear formula,
  which you derived as $-x/(2+x)$.
- `strain_from_output(vout, vex, gf)` — invert the *exact* quarter-bridge relation to
  recover $x$, then divide by the gauge factor to get strain. Inverting
  $V_o = V_{ex}x/(4+2x)$ gives $x = 4V_o/(V_{ex} - 2V_o)$.
- `max_excitation(r, p_max)` — the largest excitation an equal-arm bridge may use if
  no arm is to dissipate more than `p_max`. Each arm carries $V_{ex}/2R$.

Import `math` for the square root. The point of `nonlinearity` being separate is that
you can then ask, of any bridge, whether the linear formula is good enough before
deciding to use it.
''',
                "files": [{"name": "main.py", "content": r'''
"""The Wheatstone bridge: output, inversion, nonlinearity and excitation limits."""

import math


def bridge_output(vex, r1, r2, r3, r4):
    """Left midpoint minus right midpoint, in volts. r2 and r4 are the lower arms."""
    # TODO: two dividers, subtracted.
    return 0.0


def quarter_output(vex, r, dr):
    """Output when the lower left arm is r + dr and the other three are r."""
    # TODO: one call to bridge_output.
    return 0.0


def nonlinearity(x):
    """Fractional error of inferring x with the linear formula 4 Vo / Vex."""
    # TODO: the result you derived in this module.
    return 0.0


def strain_from_output(vout, vex, gf):
    """Strain, from an exact inversion of the quarter-bridge relation."""
    # TODO: recover x first, then divide by the gauge factor.
    return 0.0


def max_excitation(r, p_max):
    """Largest excitation for which no arm of an equal-arm bridge exceeds p_max."""
    # TODO: arm current is vex / 2r, and the arm dissipates i squared times r.
    return 0.0


if __name__ == "__main__":
    print("balanced:", bridge_output(2.0, 1000, 1000, 1000, 1000), "V")
    print("Pt1000 at +3.85 ohm:", quarter_output(2.0, 1000.0, 3.85), "V")
    print("nonlinearity at x = 1%:", nonlinearity(0.01))
    out = quarter_output(5.0, 350.0, 0.7)
    print("350 ohm gauge, 0.7 ohm change:", out, "V")
    print("recovered strain:", strain_from_output(out, 5.0, 2.0))
    print("max excitation for 1 mW in a 1k arm:", max_excitation(1000.0, 1e-3), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The Wheatstone bridge: output, inversion, nonlinearity and excitation limits."""

import math


def bridge_output(vex, r1, r2, r3, r4):
    """Left midpoint minus right midpoint, in volts. r2 and r4 are the lower arms."""
    return vex * (r2 / (r1 + r2) - r4 / (r3 + r4))


def quarter_output(vex, r, dr):
    """Output when the lower left arm is r + dr and the other three are r."""
    return bridge_output(vex, r, r + dr, r, r)


def nonlinearity(x):
    """Fractional error of inferring x with the linear formula 4 Vo / Vex."""
    return -x / (2.0 + x)


def strain_from_output(vout, vex, gf):
    """Strain, from an exact inversion of the quarter-bridge relation."""
    x = 4.0 * vout / (vex - 2.0 * vout)
    return x / gf


def max_excitation(r, p_max):
    """Largest excitation for which no arm of an equal-arm bridge exceeds p_max."""
    return 2.0 * math.sqrt(p_max * r)


if __name__ == "__main__":
    print("balanced:", bridge_output(2.0, 1000, 1000, 1000, 1000), "V")
    print("Pt1000 at +3.85 ohm:", quarter_output(2.0, 1000.0, 3.85), "V")
    print("nonlinearity at x = 1%:", nonlinearity(0.01))
    out = quarter_output(5.0, 350.0, 0.7)
    print("350 ohm gauge, 0.7 ohm change:", out, "V")
    print("recovered strain:", strain_from_output(out, 5.0, 2.0))
    print("max excitation for 1 mW in a 1k arm:", max_excitation(1000.0, 1e-3), "V")
'''}],
                "hints": [
                    "`bridge_output` is `vex * (r2 / (r1 + r2) - r4 / (r3 + r4))`. Keep the two dividers side by side and the sign convention looks after itself.",
                    "`quarter_output` should call `bridge_output(vex, r, r + dr, r, r)`. If you find yourself typing a division, you are writing the algebra out a second time.",
                    "`strain_from_output` needs the exact inversion $x = 4V_o/(V_{ex} - 2V_o)$, not $4V_o/V_{ex}$ — the tests check that a value put in through `quarter_output` comes back out to twelve figures.",
                    "For `max_excitation`: the arm current is $V_{ex}/2R$, so the arm power is $V_{ex}^2/4R$. Setting that equal to `p_max` gives $V_{ex} = 2\\sqrt{P_{max}R}$, which is 2.0 V for 1 mW in a 1 kΩ arm.",
                ],
                "tests": [
                    {"name": "a balanced bridge reads zero and an unbalanced one does not", "code": r'''
z = bridge_output(2.0, 1000, 1000, 1000, 1000)
assert abs(z) < 1e-15, f"equal arms must give exactly zero, got {z}"
r = bridge_output(2.0, 1000, 2000, 4700, 9400)
assert abs(r) < 1e-15, f"1:2 against 4.7k:9.4k is also balanced, got {r}"
u = bridge_output(2.0, 1000, 1003.85, 1000, 1000)
assert abs(u - 0.0019213014946228846) < 1e-15, \
    f"one arm 3.85 ohms high should give 1.9213 mV, got {u}"
'''},
                    {"name": "the quarter bridge agrees with the general form", "code": r'''
q = quarter_output(2.0, 1000.0, 3.85)
assert abs(q - 0.0019213014946228846) < 1e-15, \
    f"a Pt1000 3.85 ohms up at 2 V excitation gives 1.9213 mV, got {q}"
g = quarter_output(5.0, 350.0, 0.7)
assert abs(g - 0.0024975024975021354) < 1e-15, \
    f"a 350 ohm gauge 0.7 ohms up at 5 V gives 2.4975 mV, got {g}"
assert abs(quarter_output(2.0, 1000.0, 0.0)) < 1e-15, "no change means no output"
neg = quarter_output(2.0, 1000.0, -3.85)
assert neg < 0, f"a falling sensor resistance must give a negative output, got {neg}"
'''},
                    {"name": "the bridge is not quite linear", "code": r'''
n = nonlinearity(0.01)
assert abs(n - (-0.0049751243781094535)) < 1e-15, \
    f"at x = 1% the linear formula is 0.4975% low, got {n}"
assert nonlinearity(0.002) < 0, "the error is always negative for a positive x"
assert abs(nonlinearity(0.002) - (-0.0009990009990009992)) < 1e-15, \
    "at x = 0.2% the error should be about -0.0999%"
small, large = abs(nonlinearity(0.001)), abs(nonlinearity(0.1))
assert large > 10 * small, \
    "the error grows with x, so a thermistor cannot be read the way a strain gauge is"
'''},
                    {"name": "an exact inversion round-trips", "code": r'''
out = quarter_output(5.0, 350.0, 0.7)
eps = strain_from_output(out, 5.0, 2.0)
assert abs(eps - 1e-3) < 1e-12, \
    f"0.7 ohms on a 350 ohm gauge of factor 2 is 1000 microstrain, got {eps}"
big = quarter_output(2.0, 1000.0, 100.0)
x = strain_from_output(big, 2.0, 1.0)
assert abs(x - 0.1) < 1e-12, \
    f"the inversion must stay exact for a 10% change, got {x} instead of 0.1"
'''},
                    {"name": "excitation is limited by what the arm can dissipate", "code": r'''
v = max_excitation(1000.0, 1e-3)
assert abs(v - 2.0) < 1e-12, f"1 mW in a 1 k arm allows 2.000 V, got {v}"
v2 = max_excitation(350.0, 5e-3)
assert abs(v2 - 2.6457513110645907) < 1e-12, \
    f"5 mW in a 350 ohm arm allows 2.6458 V, got {v2}"
arm_power = (v / (2 * 1000.0)) ** 2 * 1000.0
assert abs(arm_power - 1e-3) < 1e-15, \
    f"check yourself: the arm at that excitation dissipates {arm_power} W"
'''},
                ],
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "Common mode: ground loops, differential inputs and the in-amp",
            "summary": "Two points on a piece of copper are not at the same voltage, and the difference arrives in series with your signal. Everything here is about not letting it.",
            "concepts": [
                "Any input has a differential part — the difference between its two terminals — and a common-mode part, which is what they share. A single-ended input has no common-mode terminal at all: it measures its live lead against *its own* ground, so whatever the two grounds differ by has already been added to the signal before the instrument sees it.",
                "A ground is a conductor. A metre of wire is a few milliohms and a few hundred nanohenries, and a return shared with somebody else's amps develops millivolts along it. The cure is topological rather than electrical: give the signal its own return to a single point, so the noisy current has no conductor in common with it to develop a voltage in.",
                "Common-mode rejection ratio is the differential gain divided by the common-mode gain, quoted in dB, and it converts a common-mode volt into an input-referred error. 100 dB turns 1.8 V of 50 Hz into 18 µV at the input — which is 0.7% of a 2.5 mV bridge output, from interference that is not even in the signal path.",
                "An instrumentation amplifier is two buffers feeding a difference stage, with a single resistor setting the gain of the buffer pair. The difference stage is a block that subtracts its two inputs, and the one fact that matters about it is that its rejection is set by how closely the two ratios of its four surrounding resistors match — a property of the resistors, not of the amplifier between them, and 0.1% parts cap it near 66 dB. Module 4's reading has the amplifier itself and the derivation on this page has that cap; neither is assumed here.",
                "Putting the gain in the buffer pair rather than in the difference stage buys two separate things, and it is worth keeping them apart. First, the four matched resistors are trimmed once and never touched again: a bare difference stage's gain can only be changed by re-scaling two of the four, and every change is a fresh chance to unmatch them. Note what this is *not* — the rejection of a bare stage does not fall as its gain rises, it climbs as $(1+k)/t$, and the exercise on this page measures a gain-100 stage at 100 dB where a unity one manages 66. The cost is that you have to re-earn the match at every gain. Second, and this is the one you can feel on a bridge, the buffers make the input impedance high and equal on both sides where a bare stage's inverting leg presents $R_1$ and nothing more — 10 kΩ on a 350 Ω bridge takes 1.7% straight off the reading.",
                "The rejection you get is the *system's*, not the amplifier's. A source imbalance $\\Delta R$ working against whatever impedance $Z_{cm}$ the two inputs see to common turns common mode straight into differential in the ratio $\\Delta R/Z_{cm}$ — and at mains frequency $Z_{cm}$ is usually not the amplifier at all but the cable's own capacitance to its screen, about 1 MΩ of reactance for thirty metres at 50 Hz. 100 Ω against that is 80 dB, and it caps a 100 dB amplifier at 80 dB whatever the amplifier cost.",
                "The “66 dB from 0.1% parts” above is a real number with a formula behind it, and the derivation on this page produces it: the common-mode gain of a difference stage of gain $k$ with one resistor off by a fraction $t$ is $kt/(1+k+kt)$, so the rejection is $(1+k)/t$ to a very good approximation. At unity gain and $t = 0.001$ that is 2001, which is 66.0 dB — and unity gain is exactly what the difference stage inside an in-amp runs at, which is why 66 dB is the figure quoted for it. Two consequences follow that the slogan hides. The cap rises with gain, so the same 0.1% resistors give 100 dB at $k = 100$; and 66 dB is the *typical* case, because four resistors each within 0.1% can be wrong in opposite directions, which is $t = 0.004$ and 54 dB. Solving the circuit confirms all three: 66.03 dB, 100.10 dB and 53.98 dB.",
            ],
            "read": {
                "title": "The volt that arrives in series with your signal",
                "minutes": 16,
                "body": r'''
A sensor thirty metres away produces 5 mV. Its signal lead runs back to an amplifier and
its return runs back along a piece of copper — a chassis bond, a rail, a strap to the
star ground at the bottom of the rack — whose resistance is 0.2 Ω. That is a poor bond
but not a rare one: twelve metres of 1 mm² copper, or thirty of 2.5 mm², or one screw
joint that has been painted over.

On the same rack there is a motor, and its return runs down the same 0.2 Ω. It draws
2 A.

$$2.0\,\text{A} \times 0.2\,\Omega = 0.400\,\text{V}$$

Put an instrument on the sensor and it reads **405 mV**. The signal is 5 mV. The reading
is eighty-one times the quantity being measured, and every component in the circuit has
exactly the value it should have. The motor is genuinely drawing its 2 A, the copper
genuinely has its 0.2 Ω, and the sensor is genuinely producing its 5 mV. There is
nothing to repair.

## Why it is in series and not in parallel

A ground is not a node; it is a conductor, and a conductor with current in it has a
voltage along it. Follow the signal's loop: out of the sensor, up the signal lead, into
the instrument, out of the instrument's low terminal, and back along the shared copper
to the sensor. The last leg of that loop is *inside* the signal path, and whatever
voltage exists along it is added to the sensor's own before anything measures anything:

$$V_{measured} = V_{sig} + I_{other}\,R_{shared}$$

That is the whole mechanism, and the shape of it decides what can be done about it. The
interference is not riding on the signal, or coupling into it, or contaminating it — it
is *in series* with it, as though somebody had soldered a 400 mV battery into the loop.
No amount of amplification separates two voltages in series, because gain multiplies
both. No filter separates them either when they overlap in frequency, and mains
interference sits squarely in the band where sensors live.

So the fix cannot be electrical. It is topological: the interference exists because two
circuits share one conductor, so give the sensor its own return to the star ground. The
motor still draws its 2 A and still develops its 0.4 V, but now in a conductor the
signal loop does not contain, and the sensor's return carries nothing but the sensor's
own microamps. That is the whole content of this module's build exercise, **The motor in
your signal path**, and the reason it is drawn with the motor as a current source is to
make it plain that nothing about the motor changes.

## When you cannot avoid a difference

Single-point grounding solves the rack. It does not solve the building. Two ends of a
thirty-metre run in an industrial installation sit at different potentials — a volt or
two of 50 Hz is ordinary — and no wiring discipline available to you removes it, because
the current making it belongs to somebody else's equipment.

At that point the input itself has to change. A **single-ended** input has one live
terminal and measures it against *its own* ground, so any difference between the two
grounds has already been added to the signal before the instrument exists; there is no
terminal at which it could be told apart. A **differential** input has two live
terminals and responds to the difference between them, which splits any input into two
parts:

$$v_d = v_{+} - v_{-} \qquad\qquad v_{cm} = \frac{v_{+} + v_{-}}{2}$$

Run the sensor's two wires as a twisted pair to a differential input and the building's
1.8 V appears on both cores equally: it is common mode, it is not a difference, and an
ideal differential input ignores it. The 5 mV is a difference and survives.

## How well "ignores it" works, in volts

A real differential input has a small gain for common mode too, and the ratio of the two
gains is quoted as CMRR in decibels. Decibels of a voltage ratio are $20\log_{10}$, so
100 dB is a ratio of $10^{5}$, and the error it leaves referred to the input is the
common-mode voltage divided by that:

$$v_{err} = \frac{1.8\,\text{V}}{10^{5}} = 18\,\mu\text{V}$$

Eighteen microvolts is meaningless next to a 2.5 V signal and is 0.72% of the 2.5 mV a
strain-gauge bridge produces. That is why CMRR in decibels tells you nothing on its own:
the number that matters is the fraction of *your* signal it becomes.

Where that rejection comes from is this module's derivation, **Where the rejection of a
difference amplifier actually lives**, and its result is worth stating before you work
it: the common-mode gain of a difference stage has $R_1R_4 - R_2R_3$ on top, so it is
exactly zero when two resistor ratios match and never otherwise. The rejection is a
property of four resistors, not of the amplifier between them.

## The half nobody quotes

Now the term that is not on any data sheet, and it is the larger one.

The two cores of the cable are not connected to nothing. Each has a capacitance to the
screen around it — about 100 pF per metre, so 3 nF over thirty metres, whose reactance
at 50 Hz is $1/(2\pi f C) = 1.06$ MΩ. Call that $Z_{cm}$. The common-mode voltage drives
a current down each core through that impedance, and each core drops a share of it
across its own source resistance. If the two source resistances were identical the two
drops would be identical and the whole thing would stay common mode.

They are not identical. Let one leg have $\Delta R$ more source resistance than the
other. Then the two inputs differ by

$$v_{err} \approx v_{cm}\,\frac{\Delta R}{Z_{cm}}$$

and this is a genuine *differential* voltage, manufactured out of common mode by the
cable and the source before the amplifier is reached. No CMRR can reject it. By the time
it arrives it is indistinguishable from signal.

```python
import math

V_CM, V_SIG, CABLE_C, F = 1.8, 2.5e-3, 3.0e-9, 50.0
z_cm = 1.0 / (2.0 * math.pi * F * CABLE_C)
print("30 m of cable is %.1f nF to screen; Zcm at %.0f Hz is %.3f Mohm"
      % (CABLE_C * 1e9, F, z_cm / 1e6))
print("the amplifier at 100 dB leaves %.2f uV = %.2f %% of the signal"
      % (V_CM / 1e5 * 1e6, 100.0 * (V_CM / 1e5) / V_SIG))
for d_r in (10.0, 100.0, 1000.0):
    ratio = d_r / z_cm
    print("  source imbalance %6.0f ohm: %5.1f dB, %8.2f uV, %6.2f %% of the signal"
          % (d_r, -20.0 * math.log10(ratio), V_CM * ratio * 1e6,
             100.0 * V_CM * ratio / V_SIG))
```

```text
30 m of cable is 3.0 nF to screen; Zcm at 50 Hz is 1.061 Mohm
the amplifier at 100 dB leaves 18.00 uV = 0.72 % of the signal
  source imbalance     10 ohm: 100.5 dB,    16.96 uV,   0.68 % of the signal
  source imbalance    100 ohm:  80.5 dB,   169.65 uV,   6.79 % of the signal
  source imbalance   1000 ohm:  60.5 dB,  1696.46 uV,  67.86 % of the signal
```

Read the middle row against the line above it. A hundred ohms of imbalance — one leg of
a bridge with a longer lead, a connector with a poorer contact, a completion resistor
from a different reel — contributes ten times what a 100 dB amplifier does. The system
is an 80 dB measurement and the money spent on the amplifier bought nothing. Matching
the two source impedances costs nothing at all, and it is the single most effective
thing on this page. This module's fill-in, **Two ways for the common mode to get in**,
walks that budget down a page in five steps, and the point of its layout is that the two
halves sit one above the other so the comparison cannot be avoided.

## The instrumentation amplifier, and what its buffers are for

The block that does this properly is two buffers feeding a difference stage, with one
resistor between the buffers setting the gain. Two separate things are bought, and they
are worth keeping apart because they are often run together into one vague claim about
quality.

The first is that the four matched resistors are trimmed once and never touched again.
Changing the gain of a bare difference stage means re-scaling two of its four resistors,
and every change is a fresh chance to unmatch the ratios. This module's second circuit
exercise, **A gain of 100 on the bridge, without losing the rejection**, is that chance
taken: raise $R_2$ alone and the numerator $R_1R_4 - R_2R_3$ becomes enormous, the
common-mode gain reaches $-50$, and 5 V of common mode drives the output into a rail
before the signal has contributed anything. Raise $R_4$ alone and it is quieter and
therefore worse — the output lands on scale, believable, and mostly common mode. Note
also what this is *not*: the rejection of a bare stage does not fall as its gain rises —
the derivation on this page shows it climbing as $(1+k)/t$, so the same 0.1% resistors
give 66 dB at unity gain and 100 dB at a gain of 100. The cost is that the match has to
be re-earned at every gain setting, and an in-amp moves the gain to a single resistor
that is not part of any ratio.

The second is the one a bridge notices. A bare difference stage's inverting leg presents
$R_1$ to its source and nothing more — 10 kΩ, typically. A 350 Ω bridge has 175 Ω at
each midpoint, so 10 kΩ hung on one of them alone reads 1.7% low, and it is a
*systematic* 1.7%, present on every reading. The buffers make the input resistance high
and, more importantly, equal on both sides, which is also the $\Delta R$ of the previous
section.

## The mistake, and why it is tempting

The mistake is buying rejection. CMRR is the number on the front of the data sheet, it
is quoted in decibels, and decibels feel like a property of the system rather than of
one component. So the response to a hum problem is a better amplifier — and the table
above says what that achieves when the source is unbalanced: nothing, because the error
was already differential when it arrived. The habit worth forming is to ask what the
*source* looks like from the amplifier's two terminals before asking what the amplifier
costs.

The second mistake is bonding both ends of a run to earth because two earths sound safer
than one. Two earths at opposite ends of a room are a ground loop: a closed conductive
circuit enclosing an area, in a building full of alternating magnetic field, with the
signal cable as one of its sides. Safety earthing is not negotiable, which is precisely
why the signal return has to be arranged so that it is not also the safety path.

## Where this stops holding

CMRR is a function of frequency, and the figure on the front page is usually at DC or at
50/60 Hz. It falls with frequency, often steeply, so an amplifier quoted at 100 dB may
have 60 dB at the switching frequency of the supply sitting next to it — and that
interference is common mode too.

Common-mode *range* is a separate limit and a harder one. An in-amp rejects what it can
see, and its inputs have to stay inside a window a few volts wide relative to its own
supplies. Eighteen hundred millivolts is comfortable; a sensor floating at 200 V is not
being poorly rejected, it is outside the amplifier's world altogether, and the answer
there is galvanic isolation rather than a better ratio.

The two error terms in the table are both input-referred voltages at 50 Hz with a fixed
phase relationship, so they do not combine in quadrature the way independent
uncertainties do. Worst case they add, and 18 + 170 µV is the honest figure to carry
into a budget.

And the 0.2 Ω of the opening is a resistance. The same conductor is also an inductance —
a few hundred nanohenries per metre — so at 50 Hz the resistive term dominates, and by a
few hundred kilohertz the inductive one does. A ground that is adequate for a
thermocouple can be useless for a switching converter's return, which is why
high-frequency grounding is about loop *area* rather than about milliohms.

Finally, a screen is only a screen if it is grounded at exactly one end. Grounded at
both, it is a low-resistance conductor joining two points at different potentials — a
ground loop with a braid around your signal, which is the arrangement the opening
paragraph described.
''',
            },
            "derive": {
                "title": "Where the rejection of a difference amplifier actually lives",
                "minutes": 14,
                "vars": ["V_1", "V_2", "V_o", "V_n", "V_p", "V_cm",
                         "R_1", "R_2", "R_3", "R_4", "A_cm", "k", "t"],
                "brief": r'''
One op-amp and four resistors. $V_1$ drives the inverting input through $R_1$, with $R_2$
from that node back to the output; $V_2$ drives the non-inverting input through $R_3$,
with $R_4$ from that node to ground. Module 4's reading has the two facts this needs: the
loop holds the two inputs together, and neither input takes any current.

The concepts above assert that this circuit rejects common mode only as well as two
resistor ratios match. Derive it, and get the number.
''',
                "steps": [
                    {
                        "prompt": "The non-inverting input is a plain divider hanging on $V_2$, loaded by nothing, because the amplifier's input takes no current. Write $V_p$.",
                        "given": "$R_3$ from $V_2$ down to the node, $R_4$ from the node down to ground.",
                        "answer": "\\frac{R_4 V_2}{R_3 + R_4}",
                        "placeholder": "e.g. \\frac{a b}{c + d}",
                        "hint": "The ordinary divider result. The resistor you are measuring *across* goes on top.",
                        "deconstruct": [
                            "The current down the pair is $V_2/(R_3+R_4)$.",
                            "The voltage at the tap is that current times $R_4$.",
                        ],
                    },
                    {
                        "prompt": "Now the inverting side. The node sits at $V_n$, and the current arriving through $R_1$ leaves through $R_2$ because none of it enters the amplifier. Write $V_o$ in terms of $V_n$, $V_1$, $R_1$ and $R_2$.",
                        "given": "$(V_1 - V_n)/R_1 = (V_n - V_o)/R_2$.",
                        "answer": "V_n\\left(1 + \\frac{R_2}{R_1}\\right) - \\frac{R_2 V_1}{R_1}",
                        "placeholder": "e.g. a\\left(1 + \\frac{b}{c}\\right) - d",
                        "hint": "Multiply out, then collect the two $V_n$ terms on one side and leave the $V_1$ term where it is.",
                        "deconstruct": [
                            "$R_2(V_1 - V_n) = R_1(V_n - V_o)$.",
                            "So $R_1V_o = R_1V_n + R_2V_n - R_2V_1$.",
                            "Divide through by $R_1$.",
                        ],
                    },
                    {
                        "prompt": "The loop makes $V_n = V_p$. Substitute, then set $V_1 = V_2 = V_{cm}$ — the same voltage on both inputs, which is what common mode *is* — and write the common-mode gain $A_{cm} = V_o/V_{cm}$.",
                        "given": "$V_{cm}$ must cancel completely; if it does not, something has gone wrong above.",
                        "answer": "\\frac{R_1 R_4 - R_2 R_3}{R_1 (R_3 + R_4)}",
                        "placeholder": "e.g. \\frac{a b - c d}{a (b + d)}",
                        "hint": "You have $V_o = V_{cm}\\left[\\frac{R_4}{R_3+R_4}\\left(1+\\frac{R_2}{R_1}\\right) - \\frac{R_2}{R_1}\\right]$. Put the bracket over the common denominator $R_1(R_3+R_4)$ and expand the numerator; four terms appear and two of them cancel.",
                        "deconstruct": [
                            "The first term is $R_4(R_1+R_2)$ over $R_1(R_3+R_4)$.",
                            "The second is $R_2(R_3+R_4)$ over the same denominator.",
                            "Subtracting: $R_1R_4 + R_2R_4 - R_2R_3 - R_2R_4$.",
                            "The $R_2R_4$ terms cancel.",
                        ],
                    },
                    {
                        "prompt": "Build the stage for a gain of $k$ — $R_1 = R_3 = R$ and $R_2 = R_4 = kR$ — but let one resistor be wrong: $R_4 = kR(1+t)$. Write $A_{cm}$ in terms of $k$ and $t$ alone.",
                        "given": "Substitute all four into the previous line. Every $R$ cancels.",
                        "answer": "\\frac{k t}{1 + k + k t}",
                        "placeholder": "e.g. \\frac{a b}{1 + a + a b}",
                        "hint": "The numerator is $R \\cdot kR(1+t) - kR \\cdot R = kR^2t$. The denominator is $R(R + kR(1+t))$.",
                        "deconstruct": [
                            "Numerator: $R_1R_4 - R_2R_3 = kR^2(1+t) - kR^2 = kR^2t$.",
                            "Denominator: $R_1(R_3+R_4) = R(R + kR + kRt) = R^2(1 + k + kt)$.",
                            "The $R^2$ cancels top and bottom.",
                        ],
                    },
                ],
                "closing": r'''
Read the third line before the fourth, because it is the general statement and the one
worth carrying: $A_{cm}$ has $R_1R_4 - R_2R_3$ on top, so it is **exactly zero when
$R_2/R_1 = R_4/R_3$ and at no other time**. Not small. Zero. The rejection of this
circuit is not a property of the amplifier at all; it is a property of whether two ratios
of resistors are equal, and the amplifier's own contribution only appears once they are.

The fourth line prices the failure. With the differential gain sitting at $k$ to within
the same small $t$, the rejection ratio is

$$\text{CMRR} = \frac{A_d}{A_{cm}} = \frac{1 + k + kt}{t} \approx \frac{1+k}{t}$$

Put the numbers in.

```text
  gain k    one resistor off by t      CMRR      in dB     solved in the editor
     1            0.1%                  2001      66.0            66.03
     1            0.01%                20001      86.0            86.01
     1            0.4%                   501      54.0            53.98
   100            0.1%                101100     100.1           100.10
```

The first row is the *"0.1% parts cap it near 66 dB"* of this module's concepts, and now
it has a reason: 66 dB is the unity-gain figure, and unity gain is what the difference
stage inside an instrumentation amplifier runs at. The third row is the same 0.1% parts
in their worst arrangement — four resistors each allowed to be 0.1% out can be out in
opposing directions, which is $t = 0.004$ between the two ratios, so 0.1% parts
*guarantee* 54 dB and merely *tend* to give 66. The fourth row is the part the slogan
hides: raise the gain and the same resistors do better, because $A_d$ grows while
$A_{cm}$ hardly moves.

Which is where the instrumentation amplifier comes from. Nothing above can be improved by
buying a better op-amp, so the trimming has to happen in four resistors, and every time
you change the gain you have to do it again. Put the gain somewhere else — in a pair of
buffers ahead of a difference stage left permanently at $k = 1$ — and the four resistors
are trimmed once and never touched, while the gain lives in a single resistor that is not
part of any ratio. The buffers are worth having twice over: the build exercise on this
page measures the second reason, which is that the bare difference stage's input
resistance is $R_1$, and a bridge notices.
''',
            },
            "quiz": {
                "title": "Loops, screens and the rejection you actually get",
                "minutes": 10,
                "questions": [
                    {
                        "q": "An amplifier with 100 dB of CMRR sees 1.8 V of 50 Hz common mode. What error does that put at its input?",
                        "opts": ["18 µV", "1.8 µV", "180 µV", "18 mV"],
                        "a": 0,
                        "why": r'''
100 dB is a ratio of $10^{100/20} = 10^5$, so the common mode appears referred to the
input divided by 100 000: $1.8/10^5 = 18$ µV. Whether that matters depends entirely on
the signal it is sitting next to — it is 0.0007% of a 2.5 V signal and 0.7% of a 2.5 mV
one. This is why CMRR is quoted in dB and errors are quoted in volts: only the second
of those can be compared with anything.
''',
                    },
                    {
                        "q": "Two racks at opposite ends of a room are each bonded to the building earth, and you run a coaxial cable between them. What have you built?",
                        "opts": [
                            "a properly earthed installation, with two independent paths to earth for safety",
                            "a loop, in which any current circulating in the building earth develops a voltage in series with the signal",
                            "a screened connection, immune to interference by construction",
                            "nothing electrical — earth is earth",
                        ],
                        "a": 1,
                        "why": r'''
The cable's screen and the building's earth conductor now form a closed loop of a few
square metres. Anything that drives current round that loop — the return current of a
motor, a fault current, or simply the magnetic field of a nearby cable inducing a
current in it — develops a voltage along the screen, and the screen is one of the two
conductors carrying your signal. The loop is why the interference exists; the fix is to
break it, usually by earthing the screen at one end only, and never by disconnecting a
protective earth.
''',
                    },
                    {
                        "q": "A screened cable carries a 1 kHz sensor signal thirty metres across a plant. Where should the screen be connected?",
                        "opts": [
                            "at both ends, for the lowest impedance to earth",
                            "at one end only, usually the amplifier's",
                            "at neither end — a floating screen picks up less",
                            "at its midpoint, so the two halves are symmetrical",
                        ],
                        "a": 1,
                        "why": r'''
At low frequencies a screen earthed at both ends is a second conductor between two
grounds, and it carries the loop current the previous question described. Earthed at one
end it still intercepts electric fields — which is its job — and carries no circulating
current. A floating screen is worse than useless, because it capacitively couples
whatever it picks up into the conductors inside it. The argument reverses above a few
megahertz, where the screen's own inductance means a single-ended screen is no longer at
one potential along its length and both ends have to be bonded; the rule is a
consequence, not a commandment, and which end of it applies depends on the frequency.
''',
                    },
                    {
                        "q": "Your in-amp is specified at 120 dB of CMRR. One leg of the cable has 100 Ω more source resistance than the other, and each core sees about 1 MΩ to common mode through the cable's capacitance to its screen. What rejection does the measurement get?",
                        "opts": ["120 dB", "80 dB", "200 dB", "40 dB"],
                        "a": 1,
                        "why": r'''
The imbalanced source converts common mode into differential in the ratio
$100/10^6 = 10^{-4}$, which is 80 dB, and that conversion happens *before* the amplifier
— so the amplifier's own 120 dB is applied to what is by then a genuine differential
signal and cannot help. The two mechanisms combine as $10^{-4} + 10^{-6}$, and the
system is 80 dB whatever the data sheet says. Matching the two source impedances is
free; buying a better amplifier is not, and here it would buy nothing.
''',
                    },
                    {
                        "q": "Why does an instrumentation amplifier set its gain with a resistor between the two input buffers rather than in the difference stage?",
                        "opts": [
                            "because the difference stage cannot provide gain at all",
                            "because the difference stage's rejection depends on a matched resistor ratio, and changing the gain there would unbalance it",
                            "to keep the input impedance low",
                            "because a single resistor is cheaper than four",
                        ],
                        "a": 1,
                        "why": r'''
A one-op-amp difference amplifier rejects common mode only as well as its two resistor
ratios match — 0.1% resistors cap it near 66 dB — and changing the gain means changing
two of those four resistors and re-matching them. Putting the gain in the input pair
leaves the matched network alone: the difference stage stays at unity with its ratios
trimmed once, and the single external resistor changes the *differential* gain only. The
result is an amplifier whose CMRR improves as the gain is raised, which is the opposite
of what an unbalanced network does.
''',
                    },
                    {
                        "q": "A transmitter 200 m away sends its reading as a 4–20 mA current rather than as a voltage. What does that buy?",
                        "opts": [
                            "immunity to a voltage induced in the loop, since the transmitter regulates the current whatever the loop does",
                            "a higher bandwidth than a voltage signal over the same cable",
                            "freedom from the need for a screened cable",
                            "a signal that cannot be affected by temperature",
                        ],
                        "a": 0,
                        "why": r'''
The transmitter holds the loop current at whatever the measurement says, and it does so
by adjusting its own terminal voltage — so a series interference emf, or the resistance
of 400 m of copper, or a receiver resistor of 100 Ω instead of 250 Ω, changes what the
transmitter has to produce and not what it delivers. The only limit is compliance: run
out of voltage headroom and regulation stops. The live zero is the second half of the
idea — 4 mA rather than 0 mA for the bottom of the range, so a broken wire reads 0 mA
and is distinguishable from a genuine zero. Bandwidth is unaffected, screening is still
worth having against capacitively coupled spikes, and nothing here is about temperature.
''',
                    },
                ],
            },
            "build": [{
                "title": "The motor in your signal path",
                "minutes": 25,
                "brief": r'''
A sensor thirty metres away produces **5 mV**, drawn here as an ideal source. Its signal
lead runs to an amplifier whose input is the **1 MΩ** resistor with the probe on it, and
its return runs back along a piece of copper of **0.2 Ω** to the star ground at the
bottom right.

That same 0.2 Ω is the return path for a motor on the same rack, drawn as the **2 A**
current source. Solve the circuit as it stands and the probed node sits at 405 mV: your
5 mV signal, riding on 400 mV of somebody else's return current.

Nothing here is broken. Every component has the value it should have, the 2 A is
genuinely flowing, and no amount of amplification or filtering will separate 400 mV of
50 Hz from 5 mV of signal once they are in series.

## What to change

The interference exists because two circuits share one conductor. Give the sensor its
own return to the star ground, so that the motor's 2 A develops its 0.4 V somewhere your
signal does not have to pass through.

That is one wire deleted and the sensor's own return drawn in its place: a ground symbol
placed under the sensor and a wire down to it. No value changes, and nothing but that
one shared wire is deleted. The motor must still be drawing its 2 A through the same
0.2 Ω when you are finished; removing the interference by removing the ground is not a
fix, it is a different circuit.

## Reading the drawing

The ground symbols are all the same node — that is what a star ground *is*, one point
that everything returns to. What matters is which conductor each return travels along
to get there, and that is decided by the wires you draw, not by how many ground symbols
are on the page.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 0.005},
                        {"id": "p1", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p2", "kind": "GND", "x": 11, "y": 9},
                        {"id": "p3", "kind": "OUT", "x": 14, "y": 4},
                        {"id": "p4", "kind": "R", "x": 5, "y": 11, "rot": 0, "value": 0.2},
                        {"id": "p5", "kind": "GND", "x": 8, "y": 11},
                        {"id": "p6", "kind": "I", "x": 4, "y": 14, "rot": 0, "value": 2},
                        {"id": "p7", "kind": "GND", "x": 8, "y": 14},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [14, 4]},
                        {"a": [11, 4], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 9]},
                        {"a": [3, 7], "b": [3, 11]},
                        {"a": [3, 11], "b": [4, 11]},
                        {"a": [6, 11], "b": [8, 11]},
                        {"a": [3, 14], "b": [3, 11]},
                        {"a": [5, 14], "b": [8, 14]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 0.005},
                        {"id": "p1", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p2", "kind": "GND", "x": 11, "y": 9},
                        {"id": "p3", "kind": "OUT", "x": 14, "y": 4},
                        {"id": "p4", "kind": "R", "x": 5, "y": 11, "rot": 0, "value": 0.2},
                        {"id": "p5", "kind": "GND", "x": 8, "y": 11},
                        {"id": "p6", "kind": "I", "x": 4, "y": 14, "rot": 0, "value": 2},
                        {"id": "p7", "kind": "GND", "x": 8, "y": 14},
                        {"id": "p8", "kind": "GND", "x": 3, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [14, 4]},
                        {"a": [11, 4], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 9]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 11], "b": [4, 11]},
                        {"a": [6, 11], "b": [8, 11]},
                        {"a": [3, 14], "b": [3, 11]},
                        {"a": [5, 14], "b": [8, 14]},
                    ],
                },
                "checks": [
                    {"name": "the sensor and the amplifier input are as you found them", "code": r'''
c.assert(c.count('V') === 1,
  'One voltage source: the sensor. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 0.005, 0.02, 'the sensor emf');
const out = c.outNode();
const amp = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 1e6) <= 2e4 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(amp.length === 1,
  'The amplifier input is 1 MOhm from the probed node to ground. It is what you are ' +
  'measuring with, not part of what you are allowed to redesign.');
'''},
                    {"name": "the motor is still returning 2 A through the same 0.2 Ω", "code": r'''
c.assert(c.count('I') === 1,
  'One current source: the motor return. Found ' + c.count('I') + '.');
c.close(Math.abs(c.values('I')[0]), 2, 0.02, 'the motor current');
const wire = c.net.parts.filter(function (p) {
  return p.kind === 'R' && p.value > 0.05 && p.value < 1;
});
c.assert(wire.length === 1,
  'The 0.2 ohm of copper back to the star ground has to stay, and there has to be ' +
  'exactly one of it. Deleting it removes the interference by removing the ground, ' +
  'which is not the same as solving the problem.');
const d = c.dc();
const i = Math.abs(d.v[wire[0].n1] - d.v[wire[0].n2]) / wire[0].value;
c.close(i, 2, 0.05,
  'the current still flowing in the shared ground conductor');
'''},
                    {"name": "the disturbance is still on the ground conductor", "code": r'''
const found = c.net.parts.filter(function (p) {
  return p.kind === 'R' && p.value > 0.05 && p.value < 1;
});
c.assert(found.length === 1,
  'There should be exactly one resistor of a few tenths of an ohm — the shared ground ' +
  'conductor. Found ' + found.length + '.');
const wire = found[0];
const d = c.dc();
const drop = Math.abs(d.v[wire.n1] - d.v[wire.n2]);
c.close(drop, 0.4, 0.05,
  'the volts the motor current develops along that copper. It has not gone anywhere ' +
  'and it was never supposed to — the exercise is to stop sharing it');
'''},
                    {"name": "the amplifier now sees the sensor and nothing else", "code": r'''
c.close(c.vout(), 0.005, 0.02,
  'the voltage at the probed node. It started at 405 mV, of which 400 mV was the ' +
  'motor; it should now be the sensor alone');
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const ret = c.dc().v[src.n2];
c.assert(Math.abs(ret) <= 5e-4,
  'The sensor returns to a node sitting at ' + c.fmt(ret, 'V') + '. Every volt on the ' +
  'conductor a signal returns along is added to that signal, and this one is eighty ' +
  'times the signal.');
'''},
                ],
                "hints": [
                    "Nothing needs its value changed, and the only thing to delete is a wire. Look at where the sensor's lower terminal goes, and follow that conductor to the star ground: it passes through the 0.2 Ω that the motor is also using.",
                    "Delete the wire running from the sensor's lower pin down to the left-hand end of the 0.2 Ω. That is the shared conductor, and it is the whole fault.",
                    "Now give the sensor a return of its own: place a ground symbol just below the sensor and wire the sensor's lower pin straight down to it. Both ground symbols are the same node, so the sensor still has a return — it just no longer travels along the motor's copper to get there.",
                    "Check yourself before running: the left end of the 0.2 Ω is still at 2 A × 0.2 Ω = 0.400 V, exactly as before, and the probed node is now at 5.00 mV. The interference was never removed; it was moved out of the signal's path, which is the only thing that ever works.",
                ],
            }, {
                "title": "A gain of 100 on the bridge, without losing the rejection",
                "minutes": 30,
                "brief": r'''
A quarter bridge and the difference amplifier that reads it, both already drawn.

**The bridge**, on the left: 10 V of excitation across four 350 Ω arms, of which the
lower left one is the gauge and is stretched to **350.7 Ω**. Solve it on its own and its
two outputs sit at 5.004995 V and 5.000000 V — **4995.0 µV of signal riding on 5.0 V of
common mode**, which is the situation module 6 built and this module exists to survive.

**The amplifier**, on the right: one op-amp and four resistors, wired as the difference
stage the concepts describe. $V_1$ — the right-hand bridge output — enters the inverting
input through $R_1$, with $R_2$ from that node back to the output. $V_2$ — the gauge side
— enters the non-inverting input through $R_3$, with $R_4$ from that node to ground.
Module 4's reading has the two facts you need about the amplifier itself, and this
module's derivation has the one fact you need about the four resistors.

All four are **10 kΩ** as it stands, so the stage has a gain of one and the probe reads
about 4.87 mV.

## What to change

**Make the differential gain 100**, so the output is around half a volt, and do it
without losing the rejection.

That is two resistor values and nothing else. No part is added, no part is deleted, and
no wire moves.

## The trap, stated in advance because it catches nearly everybody

The gain of an inverting stage is $R_2/R_1$, so the obvious move is to raise $R_2$ to
1 MΩ and stop. Do that and **the output slams to −15 V**, hard against the negative rail,
and the reading is gone entirely.

Nothing has broken. The stage now has a differential gain of about 100 and a *common-mode*
gain of about **−50**, and there is 5 V of common mode on this bridge against 5 mV of
signal. Fifty volts per volt of common mode is asking the output for −250 V before the
signal has contributed anything at all, so it goes to the rail and stays there. The
derivation on this page says exactly this: $A_{cm}$ carries $R_1R_4 - R_2R_3$ on top, and
raising $R_2$ alone is precisely the move that makes that numerator large.

Raising $R_4$ alone is the mirror image and is quieter, which makes it worse: the output
lands at **4.91 V**, on scale, believable, and almost entirely the common mode. A reading
that is wrong by a factor of ten and looks fine is the failure this module is about.

## What has to be true when you are finished

- the gain from the difference **actually present at your two input resistors** to the
  output is **100**, to within half a per cent. About a tenth of a per cent of shortfall
  is the amplifier's own finite gain, as module 4's reading derives, and it is expected;
  anything beyond that is the two ratios failing to match.
- the amplifier is inside its rails, with the loop closed on the inverting input,
- the bridge is not dragged more than **3%** off the 4995.0 µV it produces unloaded.

That last one is not decoration. The inverting leg's input resistance is $R_1$ and
nothing else — the source is looking into a node pinned by the loop — and 350 Ω of bridge
notices a 10 kΩ load. Expect the differential input to come out near 4908 µV rather than
4995, and the output near **0.4903 V** rather than 0.5000. Both of those errors are real
and neither is a mistake in your drawing: 1.7 points of the 1.8% shortfall is the bridge
being loaded, and 0.1 is the amplifier's finite gain.

## The point of the constraint you are about to feel

Try to fix the loading by making $R_1$ and $R_3$ smaller and the loading gets worse. Fix
it by making them larger and you need a feedback resistor a hundred times larger still,
which is where noise and bias current start to cost more than the loading did. There is
no arrangement of four resistors that is both a high impedance to the bridge and a
matched ratio pair, and that is the whole reason the instrumentation amplifier has two
buffers in front of a difference stage rather than being a difference stage.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 1, "y": 4, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 1, "y": 7},
                        {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 1, "value": 350},
                        {"id": "p3", "kind": "R", "x": 6, "y": 8, "rot": 1, "value": 350.7},
                        {"id": "p4", "kind": "GND", "x": 6, "y": 11},
                        {"id": "p5", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 350},
                        {"id": "p6", "kind": "R", "x": 12, "y": 8, "rot": 1, "value": 350},
                        {"id": "p7", "kind": "GND", "x": 12, "y": 11},
                        {"id": "p8", "kind": "R", "x": 18, "y": 9, "rot": 0, "value": 10000},
                        {"id": "p9", "kind": "R", "x": 18, "y": 12, "rot": 0, "value": 10000},
                        {"id": "p10", "kind": "OPAMP", "x": 22, "y": 12, "rot": 0, "value": 100000},
                        {"id": "p11", "kind": "R", "x": 25, "y": 6, "rot": 0, "value": 10000},
                        {"id": "p12", "kind": "R", "x": 20, "y": 15, "rot": 1, "value": 10000},
                        {"id": "p13", "kind": "GND", "x": 20, "y": 18},
                        {"id": "p14", "kind": "OUT", "x": 28, "y": 12},
                    ],
                    "wires": [
                        {"a": [1, 3], "b": [1, 2]},
                        {"a": [1, 2], "b": [12, 2]},
                        {"a": [6, 2], "b": [6, 3]},
                        {"a": [12, 2], "b": [12, 3]},
                        {"a": [1, 5], "b": [1, 7]},
                        {"a": [6, 5], "b": [6, 7]},
                        {"a": [6, 9], "b": [6, 11]},
                        {"a": [12, 5], "b": [12, 7]},
                        {"a": [12, 9], "b": [12, 11]},
                        {"a": [6, 6], "b": [3, 6]},
                        {"a": [3, 6], "b": [3, 16]},
                        {"a": [3, 16], "b": [15, 16]},
                        {"a": [15, 16], "b": [15, 12]},
                        {"a": [15, 12], "b": [17, 12]},
                        {"a": [12, 6], "b": [14, 6]},
                        {"a": [14, 6], "b": [14, 9]},
                        {"a": [14, 9], "b": [17, 9]},
                        {"a": [19, 9], "b": [22, 9]},
                        {"a": [22, 9], "b": [22, 11]},
                        {"a": [19, 12], "b": [21, 12]},
                        {"a": [20, 12], "b": [20, 14]},
                        {"a": [20, 16], "b": [20, 18]},
                        {"a": [22, 9], "b": [22, 6]},
                        {"a": [22, 6], "b": [24, 6]},
                        {"a": [26, 6], "b": [27, 6]},
                        {"a": [27, 6], "b": [27, 12]},
                        {"a": [27, 12], "b": [23, 12]},
                        {"a": [27, 12], "b": [28, 12]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 1, "y": 4, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 1, "y": 7},
                        {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 1, "value": 350},
                        {"id": "p3", "kind": "R", "x": 6, "y": 8, "rot": 1, "value": 350.7},
                        {"id": "p4", "kind": "GND", "x": 6, "y": 11},
                        {"id": "p5", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 350},
                        {"id": "p6", "kind": "R", "x": 12, "y": 8, "rot": 1, "value": 350},
                        {"id": "p7", "kind": "GND", "x": 12, "y": 11},
                        {"id": "p8", "kind": "R", "x": 18, "y": 9, "rot": 0, "value": 10000},
                        {"id": "p9", "kind": "R", "x": 18, "y": 12, "rot": 0, "value": 10000},
                        {"id": "p10", "kind": "OPAMP", "x": 22, "y": 12, "rot": 0, "value": 100000},
                        {"id": "p11", "kind": "R", "x": 25, "y": 6, "rot": 0, "value": 1000000},
                        {"id": "p12", "kind": "R", "x": 20, "y": 15, "rot": 1, "value": 1000000},
                        {"id": "p13", "kind": "GND", "x": 20, "y": 18},
                        {"id": "p14", "kind": "OUT", "x": 28, "y": 12},
                    ],
                    "wires": [
                        {"a": [1, 3], "b": [1, 2]},
                        {"a": [1, 2], "b": [12, 2]},
                        {"a": [6, 2], "b": [6, 3]},
                        {"a": [12, 2], "b": [12, 3]},
                        {"a": [1, 5], "b": [1, 7]},
                        {"a": [6, 5], "b": [6, 7]},
                        {"a": [6, 9], "b": [6, 11]},
                        {"a": [12, 5], "b": [12, 7]},
                        {"a": [12, 9], "b": [12, 11]},
                        {"a": [6, 6], "b": [3, 6]},
                        {"a": [3, 6], "b": [3, 16]},
                        {"a": [3, 16], "b": [15, 16]},
                        {"a": [15, 16], "b": [15, 12]},
                        {"a": [15, 12], "b": [17, 12]},
                        {"a": [12, 6], "b": [14, 6]},
                        {"a": [14, 6], "b": [14, 9]},
                        {"a": [14, 9], "b": [17, 9]},
                        {"a": [19, 9], "b": [22, 9]},
                        {"a": [22, 9], "b": [22, 11]},
                        {"a": [19, 12], "b": [21, 12]},
                        {"a": [20, 12], "b": [20, 14]},
                        {"a": [20, 16], "b": [20, 18]},
                        {"a": [22, 9], "b": [22, 6]},
                        {"a": [22, 6], "b": [24, 6]},
                        {"a": [26, 6], "b": [27, 6]},
                        {"a": [27, 6], "b": [27, 12]},
                        {"a": [27, 12], "b": [23, 12]},
                        {"a": [27, 12], "b": [28, 12]},
                    ],
                },
                "checks": [
                    {"name": "the bridge is the one you were given, still on its 10 V", "code": r'''
c.assert(c.count('V') === 1,
  'One source: the 10 V bridge excitation. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 10, 0.001, 'the bridge excitation');
const arms = c.net.parts.filter(function (p) {
  return p.kind === 'R' && p.value > 300 && p.value < 400;
});
c.assert(arms.length === 4,
  'A bridge has four arms, and this one is three gauges at 350 Ohm and a stretched one ' +
  'at 350.7. Found ' + arms.length + ' resistors in that range. The bridge is the thing ' +
  'being measured, not part of the amplifier you are designing.');
const u = c.net.readouts.filter(function (x) { return x.kind === 'OPAMP'; });
c.assert(u.length === 1,
  'This exercise wants exactly one amplifier. Found ' + u.length + '.');
'''},
                    {"name": "the amplifier is inside its rails, with the loop on the inverting input", "code": r'''
const u = c.net.readouts.filter(function (x) { return x.kind === 'OPAMP'; })[0];
c.assert(u, 'There is no amplifier in this circuit.');
const d = c.device(u.id);
c.assert(Math.abs(d.v[1]) < 14,
  'The output is at ' + c.fmt(d.v[1], 'V') + ', hard against a supply rail. On this ' +
  'bridge that almost always means the two resistor ratios no longer match, so the five ' +
  'volts of common mode is being amplified alongside the five millivolts of signal.');
c.assert(Math.abs(d.v[0] - d.v[2]) < 1e-3,
  'The two inputs are ' + c.fmt(d.v[0] - d.v[2], 'V') + ' apart, so the loop is not ' +
  'closed. Negative feedback holds them together and nothing else does.');
c.assert(u.nodes[2] !== u.nodes[0],
  'Both amplifier inputs are on the same node, so there is no difference left to take.');
'''},
                    {"name": "the differential gain is 100, which is what proves the ratios match", "code": r'''
const u = c.net.readouts.filter(function (x) { return x.kind === 'OPAMP'; })[0];
const inp = u.nodes[0], out = u.nodes[1], inm = u.nodes[2];
const legOf = function (node, avoid, what) {
  const r = c.net.parts.filter(function (p) {
    return p.kind === 'R' && ((p.n1 === node && p.n2 !== avoid && p.n2 !== 0) ||
      (p.n2 === node && p.n1 !== avoid && p.n1 !== 0));
  });
  c.assert(r.length === 1,
    'Exactly one resistor should run from the ' + what + ' input back towards the ' +
    'bridge. Found ' + r.length + '.');
  return r[0].n1 === node ? r[0].n2 : r[0].n1;
};
const A = legOf(inp, 0, 'non-inverting');
const B = legOf(inm, out, 'inverting');
const v = c.dc().v;
const vd = v[A] - v[B], vcm = (v[A] + v[B]) / 2;
c.assert(Math.abs(vd) > 1e-4,
  'The two bridge outputs differ by ' + c.fmt(vd, 'V') + '. There is no signal to amplify.');
c.assert(vcm > 4 && vcm < 6,
  'The two amplifier inputs sit at ' + c.fmt(vcm, 'V') + ' between them. A bridge at half ' +
  'its excitation should put them near 5 V, so this amplifier is not reading across the ' +
  'bridge at all.');
const g = c.vout() / vd;
c.assert(g > 0,
  'The gain came out at ' + g.toPrecision(4) + ', which is negative, so the two bridge ' +
  'outputs are on the wrong legs. The arm whose node rises when the gauge is stretched ' +
  'is the one that belongs on the non-inverting side.');
c.close(g, 100, 0.005,
  'the gain from the difference actually present at your two input resistors to the ' +
  'output. A tenth of a per cent of shortfall is the finite gain of the amplifier ' +
  'itself; anything past that is the two ratios failing to match, and a mismatch turns ' +
  'the 5 V of common mode into output as readily as it turns the 5 mV of signal');
'''},
                    {"name": "the bridge is not dragged more than 3% off its own answer", "code": r'''
const u = c.net.readouts.filter(function (x) { return x.kind === 'OPAMP'; })[0];
const inp = u.nodes[0], out = u.nodes[1], inm = u.nodes[2];
const legOf = function (node, avoid) {
  const r = c.net.parts.filter(function (p) {
    return p.kind === 'R' && ((p.n1 === node && p.n2 !== avoid && p.n2 !== 0) ||
      (p.n2 === node && p.n1 !== avoid && p.n1 !== 0));
  })[0];
  c.assert(r, 'One of the two input resistors is missing.');
  return r.n1 === node ? r.n2 : r.n1;
};
const v = c.dc().v;
const vd = v[legOf(inp, 0)] - v[legOf(inm, out)];
const open = 4.995005e-3;
const d = c.device(u.id);
c.assert(!(vd < 0 && Math.abs(d.v[1]) > 14),
  'The bridge is reading backwards at ' + (vd * 1e6).toFixed(1) + ' uV while the output ' +
  'sits at ' + c.fmt(d.v[1], 'V') + ', against a rail. Nothing can be said about loading ' +
  'until the amplifier is back inside its supplies: what is bending the bridge is an ' +
  'amplifier input dragged up with the output, not the resistors.');
c.assert(vd >= open * 0.97,
  'The bridge is delivering ' + (vd * 1e6).toFixed(1) + ' uV where on its own it ' +
  'produces 4995.0 uV — it is loaded by ' + ((1 - vd / open) * 100).toFixed(2) + '%, and ' +
  'every bit of that comes straight off the reading. The inverting legs input resistance ' +
  'is R1 and nothing else, and 350 Ohm of bridge notices resistors this small.');
'''},
                ],
                "hints": [
                    "The gain of this stage is the ratio $R_2/R_1$ on the inverting side and $R_4/R_3$ on the non-inverting side, and the derivation on this page says the common-mode gain is zero only when those two ratios are *equal*. So there are two resistors to change, not one.",
                    "$R_1$ and $R_3$ are the two 10 kΩ resistors the bridge feeds into. $R_2$ is the one running from the amplifier's inverting input up and over to its output; $R_4$ is the one running from the non-inverting input down to ground. Raise $R_2$ and $R_4$ together to 1 MΩ — type `1M` into the value box.",
                    "If you changed only one of them, solve it and look at the output before changing anything back. Raising $R_2$ alone puts it on the negative rail; raising $R_4$ alone puts it at 4.91 V. Both are the common mode arriving, and the second one is the dangerous one because it looks like an answer.",
                    "Check yourself before running: the two bridge nodes should be about 5.0041 V and 4.9992 V — 4908 µV apart rather than the 4995 µV the bridge produces unloaded, because your 10 kΩ resistors are loading it — and the output should be 0.4903 V.",
                    "1 MΩ is not the only right answer. 100 kΩ and 10 MΩ is the same ratio, loads the bridge ten times less, and passes every check here; the reason nobody builds it that way is noise and bias current, neither of which this solver models.",
                ],
            }],
            "blanks": {
                "title": "Two ways for the common mode to get in",
                "minutes": 9,
                "caption": "the amplifier's contribution, and the one the data sheet cannot tell you about",
                "lang": "text",
                "brief": r'''
A bridge on a plant floor, thirty metres of twisted pair, and an instrumentation
amplifier at the far end. There is 1.8 V of 50 Hz between the two ends of the run —
ordinary for a building — and it appears equally on both cores, which is exactly the
situation an in-amp exists for.

Work the budget down the page. The first half is the number on the data sheet. The
second half is the one nobody quotes, and it is the larger of the two.
''',
                "listing": """a 2.50 mV bridge output, 30 m away, on a floor with 1.8 V of 50 Hz on it
-----------------------------------------------------------------------

  differential signal      v_d    =  2.50 mV       what the bridge produced
  common-mode voltage      v_cm   =  1.80 V        50 Hz, equal on both cores
  amplifier CMRR at 50 Hz         =  100 dB        from the data sheet

  the data sheet figure, as a plain ratio

      rejection  =  10 ** (100 / 20)   =  ___

  what the amplifier itself lets through, referred to its input

      v_err      =  1.80 V / 100000    =  ___ uV

  as a fraction of the signal you came to measure

      v_err / v_d  =  18.0 uV / 2.50 mV  =  ___ %

  now the half that is not on any data sheet. One leg of the pair has 100 ohm
  more source resistance than the other, and each core sees about 1 M to common
  mode — the reactance at 50 Hz of the 3 nF that 30 m of cable has to its
  screen. The pair itself converts common mode into differential in the ratio

      ___          =  1.0e-4                       which is 80 dB

      v_imb      =  1.80 V * 1.0e-4    =  ___ uV
""",
                "blanks": [
                    {
                        "prompt": "100 dB, written as a plain ratio.",
                        "hole": "ratio",
                        "opts": ["100000", "10000", "1000000", "5"],
                        "a": 0,
                        "why": "Decibels of a *voltage* ratio are $20\\log_{10}$, so 100 dB is "
                               "$10^{100/20} = 10^5$. Answering 10 000 uses the power convention, "
                               "$10\\log_{10}$, which is right for watts and wrong for volts and is "
                               "the single commonest slip in this arithmetic. Answering 5 stops at "
                               "the exponent.",
                    },
                    {
                        "prompt": "1.80 V divided by 100 000, in microvolts.",
                        "hole": "v_err",
                        "opts": ["18.0", "180", "1.80", "0.18"],
                        "a": 0,
                        "why": "$1.80/10^5 = 1.8\\times10^{-5}$ V, and $1.8\\times10^{-5}$ V is 18.0 µV. "
                               "It is worth doing this conversion slowly once: a microvolt is $10^{-6}$ V, "
                               "so the exponent $-5$ is ten microvolts, and the 1.8 makes it eighteen.",
                    },
                    {
                        "prompt": "18.0 µV as a percentage of 2.50 mV.",
                        "hole": "share",
                        "opts": ["0.72", "7.2", "0.072", "1.39"],
                        "a": 0,
                        "why": "$18.0\\times10^{-6}/2.50\\times10^{-3} = 7.2\\times10^{-3}$, which is 0.72%. "
                               "That is the honest measure of an amplifier's CMRR: not the decibels, "
                               "which say nothing on their own, but the fraction of *your* signal the "
                               "interference has become. The same 100 dB amplifier on a 2.50 V signal "
                               "would be contributing 0.00072%, and nobody would think about it again.",
                    },
                    {
                        "prompt": "What ratio does a 100 Ω imbalance against 1 MΩ of common-mode impedance produce?",
                        "hole": "imbalance",
                        "opts": ["100 / 1 M", "1 M / 100", "100 / 2.50 m", "1.80 / 1 M"],
                        "a": 0,
                        "why": "The unbalanced leg makes a divider with the shunt impedance that its "
                               "partner does not, so a common-mode voltage appears differentially in the "
                               "ratio of the *extra* series resistance to the impedance it works against: "
                               "$100/10^6 = 10^{-4}$. Inverting it gives the rejection rather than the "
                               "leakage, which is a factor of $10^8$ in the wrong direction.",
                    },
                    {
                        "prompt": "1.80 V times 1.0e-4, in microvolts.",
                        "hole": "v_imb",
                        "opts": ["180", "18.0", "1800", "0.18"],
                        "a": 0,
                        "why": "$1.80 \\times 10^{-4}$ V is 180 µV — ten times what the amplifier itself "
                               "contributed, and 7.2% of the 2.50 mV signal. The whole point of the page "
                               "is this comparison: a 100 dB amplifier fed from a source balanced to "
                               "100 ohms in a megohm is an 80 dB measurement, and the money spent on the "
                               "amplifier bought nothing. Matching the two source impedances, or lowering "
                               "them both, is free.",
                    },
                ],
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Thermocouples, thermistors and the calibration curve",
            "summary": "Two of the commonest temperature sensors are badly non-linear, and one of them cannot measure a temperature at all — only a difference. Both are good to a tenth of a kelvin, and what makes them so is arithmetic done afterwards.",
            "concepts": [
                "A thermocouple produces an emf because a temperature *gradient* along a conductor produces one. The junction matters only because it is where two different metals meet, so their two gradient-driven emfs do not cancel. The loop emf therefore depends on the temperatures at the two ends and not on anything in between — a thermocouple measures a difference, and cannot be made to do anything else.",
                "So the reference junction's temperature has to be known: hold it at 0 °C in an ice bath, or measure it with a second sensor and add the emf it would have produced. That second method is cold-junction compensation, it is what every thermocouple instrument does, and the accuracy of a thermocouple reading is therefore capped by the accuracy of the little sensor in the terminal block.",
                "A type K couple gives about 41 µV/K near room temperature — 1.000 mV at 25 °C and 4.096 mV at 100 °C, both against a 0 °C reference. Those are table values and the table is not a straight line: the sensitivity itself changes with temperature, which is why instruments carry polynomials rather than a slope.",
                "A thermistor is the opposite trade. $R = R_0\\exp\\left(\\beta(1/T - 1/T_0)\\right)$ with $T$ in kelvin gives about $\\beta/T^2 = 4.4\\%$ per kelvin at 25 °C for a $\\beta$ of 3950 K — ten times a platinum sensor's 0.39%/K — bought with a severe non-linearity and a useful range of perhaps a hundred kelvin.",
                "None of it is a measurement until there is a calibration curve, and a curve is only as good as its residuals. Fit the model, then look at what it failed to explain: residuals that wander smoothly mean the model is the wrong *shape* and more data will not help, while residuals that scatter mean you have reached the noise. Quote the worst residual over the range you will actually use.",
            ],
            "read": {
                "title": "A sensor that cannot tell you a temperature",
                "minutes": 17,
                "body": r'''
Put the tip of a type K thermocouple into boiling water and lay its two tails on a
terminal block on the bench at 25 °C. A microvoltmeter across the tails reads
**3.096 mV**.

Now close your hand around the terminal block and hold it there for a minute. The
reading falls, to somewhere near 2.7 mV. The water is still boiling. Nothing has
happened at the end of the probe that is in the bath, and the reading has moved by 400
microvolts — ten degrees' worth.

This is not a fault, and it is not drift. It is the defining property of the sensor,
and everything else in this module follows from it.

## Why the far end matters

The emf does not come from the junction. It comes from the *gradient*: a temperature
gradient along a conductor drives a small emf along that conductor, of a size set by the
metal it is made of. Take a loop of one metal with a hot spot anywhere in it and the two
sides of the loop develop equal and opposite emfs, which cancel — which is why you
cannot make a thermocouple out of one wire.

Make the loop out of two different metals joined at each end, and the two sides no
longer cancel, because the same temperature gradient produces different emfs in
chromel and in alumel. What survives is a loop emf that depends on the temperature at
each of the two joins and on nothing whatever in between. Run the wire through an oven,
coil it in liquid nitrogen, bend it round a hot pipe: as long as both ends stay where
they are, the emf does not change.

That is the law of intermediate temperatures, and its consequence is the hand on the
terminal block. The loop emf is

$$E_{loop} = E(T_{meas}) - E(T_{ref})$$

where $E$ is the tabulated emf of that couple against a 0 °C reference. Warming the
reference junction raises $E(T_{ref})$ and lowers the difference. A thermocouple
measures a difference of temperatures and has no mechanism by which it could measure
anything else.

## Getting a temperature out of it

Rearrange, and the recipe is forced:

$$E(T_{meas}) = E_{loop} + E(T_{ref})$$

Measure the temperature of the reference junction with some other sensor, look up the
emf that junction *would have* produced against 0 °C, add it to what you measured, and
invert the table. That is cold-junction compensation, and every thermocouple instrument
does it. Carry the opening numbers through it, using this course's table values —
$E(25) = 1.000$ mV, $E(100) = 4.096$ mV:

```text
  loop emf measured                     3.096 mV
  block at 25 C, table gives         +  1.000 mV
                                     ------------
  emf against a 0 C reference           4.096 mV
  invert the table                        100.0 C
```

Two ways of getting this wrong are worth naming because they look alike here. Putting
3.096 mV straight into the table lands between $E(75) = 3.059$ and $E(76) = 3.100$, at
75.9 °C. Subtracting the reference *temperature* from the answer instead of adding its
*emf* gives $100 - 25 = 75$ °C. The two mistakes agree to within a degree at this point
on the curve and disagree by tens of degrees elsewhere, which is exactly the kind of
coincidence that lets a wrong method survive a first test. This module's build exercise,
**Compensating a cold junction**, draws the loop as two emf sources with the reference
one turned to oppose the measuring one, so that the subtraction is visible as a circuit
rather than asserted as a rule.

Now differentiate the recipe with respect to the thing you had to measure separately:

$$\frac{\partial T_{meas}}{\partial T_{ref}}
 = \frac{\left(dE/dT\right)_{T_{ref}}}{\left(dE/dT\right)_{T_{meas}}}$$

From the course's own table values the mean slope from 0 to 25 °C is 40.0 µV/K and the
local slope near 75 °C is 41.0 µV/K, so that ratio is 0.976. A kelvin of error in the
little sensor under the terminal block is very nearly a kelvin of error in the answer.
The accuracy of a thermocouple measurement is capped by the accuracy of a component
that is not the thermocouple, is not near the thing being measured, and costs a few
pence.

## The table is not a line

The same two slopes say the other thing worth knowing: 40.0 µV/K in one place and
41.0 µV/K in another. The sensitivity itself changes with temperature, which is why
instruments carry polynomials rather than a slope.

Price the shortcut. Inverting 4.096 mV with a constant 41.0 µV/K gives 99.90 °C — a
tenth of a degree out, respectable. Inverting the same emf with the 40.0 µV/K measured
near room temperature gives 102.40 °C, which is 2.4 K wrong. The linear model is not
merely approximate; it is approximate in a way that depends on which part of the curve
you calibrated it against, and it goes wrong fastest exactly where nobody checked.

## The other trade: a thermistor

An NTC thermistor takes the opposite bargain. Its two-parameter model is

$$R = R_0\exp\left(\beta\left(\frac{1}{T}-\frac{1}{T_0}\right)\right)$$

with $T$ in kelvin. Take logarithms and differentiate to get the fractional sensitivity:

$$\frac{1}{R}\frac{dR}{dT} = -\frac{\beta}{T^{2}}$$

For $\beta = 3950$ K at 25 °C that is $3950/298.15^{2} = 0.0444$ per kelvin — **4.4% per
kelvin**, against 0.385% for a platinum sensor, a factor of eleven and a half. That
sensitivity is the reason to use one, and it is bought with a resistance that falls by a
factor of 48 between 0 and 100 °C. This module's derivation, **Reading a temperature off
a thermistor**, inverts the model to
$T = \left(1/T_0 + \ln(R/R_0)/\beta\right)^{-1}$, which is where the arithmetic below
starts.

## Fitting, and then looking at what the fit failed to explain

Neither sensor is a measurement until there is a curve, and a curve is worth exactly
what its residuals say it is. Here is the fit the lab asks for, on the lab's own table —
nine points generated from the three-parameter Steinhart–Hart model that manufacturers
publish, with no noise on them at all.

```python
import math

K = 273.15
TABLE = [(0.0, 32650.4), (12.5, 17668.7), (25.0, 9999.9), (37.5, 5892.6),
         (50.0, 3601.0), (62.5, 2274.4), (75.0, 1480.0), (87.5, 989.7),
         (100.0, 678.4)]


def fit(points, t0=25.0):
    xs = [1.0 / (t + K) for t, _ in points]
    ys = [math.log(r) for _, r in points]
    n = len(points)
    mx, my = sum(xs) / n, sum(ys) / n
    beta = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            / sum((x - mx) ** 2 for x in xs))
    return beta, math.exp(my - beta * mx + beta / (t0 + K))


def temperature(r, beta, r0, t0=25.0):
    return 1.0 / (1.0 / (t0 + K) + math.log(r / r0) / beta) - K


for lo, hi in ((0.0, 100.0), (12.5, 50.0)):
    pts = [p for p in TABLE if lo <= p[0] <= hi]
    beta, r0 = fit(pts)
    res = [temperature(r, beta, r0) - t for t, r in pts]
    print("%5.1f to %5.1f C: beta %7.2f K, R0 %8.2f, worst residual %+.4f K"
          % (lo, hi, beta, r0, max(res, key=abs)))
    print("   ", "  ".join("%+.3f" % e for e in res))
```

```text
  0.0 to 100.0 C: beta 3951.30 K, R0  9908.45, worst residual +0.6254 K
    +0.387  +0.032  -0.207  -0.331  -0.346  -0.256  -0.060  +0.233  +0.625
 12.5 to  50.0 C: beta 3915.00 K, R0  9971.43, worst residual +0.0708 K
    +0.053  -0.065  -0.058  +0.071
```

Look at the first row of residuals before looking at the number beside it. They go
positive, cross to negative, reach a minimum in the middle, and climb back through zero
to a large positive value at the top. That is not scatter. It is a smooth curve, and a
smooth residual means the model has the wrong *shape*: the data are Steinhart–Hart and
the fit is a straight line in $\ln R$ against $1/T$, and no amount of extra data will
close a gap between two different functions.

The second row is the same model on a third of the range, and the worst residual drops
from 0.63 K to 0.071 K — a factor of nine, for doing nothing but declining to promise
anything outside 12.5–50 °C. A two-parameter model is a local approximation, and the
honest way to report one is with the range attached to it.

## The mistake, and why it is tempting

The mistake is quoting a thermocouple to a tenth of a kelvin. Everything visible
supports it: the probe is the exotic, specified, expensive part; the display shows
tenths; the microvoltmeter is a six-digit instrument. The cold-junction sensor is a
three-pence package under the terminal block that nobody has thought about since the
instrument was designed, and the derivative above says its error arrives in the answer
essentially one for one. A thermocouple system is only as good as the least interesting
component in it.

The second mistake is judging a fit by a single summary number. A residual standard
deviation of 0.3 K, or a correlation coefficient of 0.9999, is entirely consistent with
the first row above — and the first row is a *wrong model*, not a noisy one. The two
situations call for opposite responses: scattered residuals mean you have reached the
noise and more averaging will help; wandering residuals mean more data will change
nothing and the model has to change instead. Only the pattern distinguishes them, and
only looking at the pattern reveals it.

## Where this stops holding

The law that only the two ends matter assumes the wire is *homogeneous*. It is the
weakest assumption in the whole subject. A section that has been cold-worked by bending,
contaminated by a furnace atmosphere, or annealed unevenly is locally a different
material, and if it happens to sit in a temperature gradient it generates its own emf
that no compensation can find. This, rather than the table or the instrument, is what
limits thermocouple accuracy in industrial service, and it is why a probe that has been
in a furnace for a year is recalibrated rather than trusted.

The same law governs the wiring. Extension leads must be the same alloy pair, or a
matched compensating alloy, all the way to the point where the reference temperature is
measured. Splice copper into the middle of a run that lies in a gradient and you have
created a new pair of junctions at an unknown temperature.

The $\beta$ model above is two parameters and the fit shows what that buys. Steinhart–
Hart uses three and reduces the residual by orders of magnitude over the same span; the
lab's table was generated from it precisely so that the mismatch is a difference between
models rather than noise.

And a thermistor is a resistor, so reading it dissipates power in it, and module 6's
self-heating argument returns in a nastier form. A 10 kΩ thermistor with 5 V across it
dissipates 2.5 mW, which at a typical 0.2 K/mW in still air is 0.5 K of error — five
times the residual being worried about above, and in the measured quantity itself. Drop
the excitation to 0.5 V and it is 0.005 K. The measurement circuit is part of the sensor.

Finally, residuals only report on the range you sampled. The 0.071 K over 12.5–50 °C is
a statement about four points; it says nothing about 60 °C, and a two-parameter model
extrapolated past its data is a guess with a decimal point on it.

## What this module asks you to do

**Compensating a cold junction** builds the loop of the opening paragraph as a circuit,
with the reference junction's 1.000 mV opposing the measuring junction's 4.096 mV, and
asks you to add the compensation that recovers the 4.096.

**Reading a temperature off a thermistor** inverts the $\beta$ model symbolically, which
is the function the lab then needs.

**Fitting a curve, and reading its residuals** is the table above, done by you: the
least-squares line in $\ln R$ against $1/T$, the inversion, the residuals, and the worst
of them over two different ranges. The gap between those two numbers is the lesson.
''',
            },
            "quiz": {
                "title": "Junctions, curves and the sensor that measures a difference",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A type K thermocouple whose reference junction sits at 25 °C produces 3.096 mV. What is the measuring junction at?",
                        "opts": ["75 °C", "100 °C", "125 °C", "76 °C"],
                        "a": 1,
                        "why": r'''
The tables are written against a 0 °C reference, so a loop emf of 3.096 mV with the
reference at 25 °C means $E(T) = 3.096 + E(25) = 3.096 + 1.000 = 4.096$ mV, and the table
puts 4.096 mV at 100 °C. The two wrong answers are two different slips. Putting 3.096 mV
straight through the table — forgetting the compensation entirely — lands between
$E(75) = 3.059$ and $E(76) = 3.100$ mV, at 75.9 °C: that is the 76 °C answer. The 75 °C
answer is 100 − 25, subtracting the reference *temperature* from the result instead of
adding its *emf*; the two slips look alike here only because the table happens to be
nearly linear over this stretch, and over a wider range that coincidence disappears.
''',
                    },
                    {
                        "q": "You extend a type K couple from the terminal block to the instrument with ordinary copper wire. The block is at 40 °C and the instrument at 25 °C. What happens to the reading?",
                        "opts": [
                            "nothing — copper is copper",
                            "it reads about 15 °C low",
                            "it reads about 15 °C high",
                            "it reads 40 °C regardless of the process temperature",
                        ],
                        "a": 1,
                        "why": r'''
Joining copper to the two thermocouple alloys creates a new pair of junctions at the
terminal block, and *those* are now the reference junctions. The loop delivers
$E(T) - E(40)$, while the instrument — compensating for its own terminals at 25 °C —
adds $E(25)$ back. The result is short by $E(40) - E(25) = 1.612 - 1.000 = 0.612$ mV,
which at 41 µV/K is about 15 K low. This is what thermocouple extension cable exists to
prevent: it is made of the same alloy pair, so it moves the reference junction to the
instrument instead of creating one at the block.
''',
                    },
                    {
                        "q": "An NTC thermistor with $\\beta = 3950$ K sits at 25 °C. Its fractional resistance change per kelvin is about:",
                        "opts": ["0.39%/K", "4.4%/K", "13%/K", "0.044%/K"],
                        "a": 1,
                        "why": r'''
Differentiating $R = R_0\exp(\beta(1/T - 1/T_0))$ gives $\frac{1}{R}\frac{dR}{dT} =
-\beta/T^2$, and at $T = 298$ K that is $3950/88\,900 = 0.0444$, or 4.4% per kelvin. The
0.39%/K answer is platinum's, and the comparison is the whole reason both sensors exist:
a thermistor gives ten times the signal from the same excitation, and pays for it with a
curve that has to be inverted and a range of about a hundred kelvin instead of six
hundred. Note the sign — resistance *falls* as it warms, which is what the N in NTC is.
''',
                    },
                    {
                        "q": "Which of these does a thermocouple's loop emf NOT depend on?",
                        "opts": [
                            "the temperature of the measuring junction",
                            "the temperature of the reference junction",
                            "the temperature of the wire halfway between them",
                            "which two alloys the wires are made of",
                        ],
                        "a": 2,
                        "why": r'''
Provided each wire is homogeneous along its length, the emfs generated by the gradients
in the middle sum to a result that depends only on the temperatures at the two ends: the
wire can pass through a furnace and a freezer on the way without changing the reading.
That is the law of homogeneous circuits, and it is what makes a thermocouple usable at
all. The caveat carries the practical failure mode: a wire that has been work-hardened
by bending, oxidised, or contaminated is no longer homogeneous, and then the gradient
along *that* stretch does contribute — which is why an aged thermocouple drifts in a way
no calibration of its junction can predict.
''',
                    },
                    {
                        "q": "You fit a calibration curve and its residuals run smoothly from −0.3 K at the bottom of the range, through +0.4 K in the middle, and back to −0.3 K at the top. What does that tell you?",
                        "opts": [
                            "the sensor is noisy and more points would help",
                            "the model is the wrong shape — that residual is structure, not scatter",
                            "the fit is as good as this data allows",
                            "the sensor has hysteresis",
                        ],
                        "a": 1,
                        "why": r'''
Noise scatters; this curves. A residual that is a smooth function of the input is the
part of the physics your model does not contain, and averaging more readings at each
point will reduce the scatter around that curve without moving the curve itself. The
answers are a better model, a narrower range, or an extra term — and the choice between
them is an engineering judgement about what the measurement is for. Hysteresis would
show as a *split*: two different residuals at the same temperature depending on which
way you approached it, which is why a calibration run should always go up and back down.
''',
                    },
                    {
                        "q": "The little sensor doing your cold-junction compensation is good to ±0.5 °C. What is the best your thermocouple measurement can be?",
                        "opts": [
                            "better than ±0.5 °C, because the thermocouple is the more sensitive of the two",
                            "±0.5 °C, degree for degree",
                            "±0.5 °C divided by the amplifier's gain",
                            "it depends on the measured temperature",
                        ],
                        "a": 1,
                        "why": r'''
The compensation adds $E(T_{ref})$ to the measured loop emf, so an error in $T_{ref}$
becomes an error in the sum, and — since both are converted through the same table — an
error of one kelvin in the reference junction is an error of one kelvin in the result.
It passes through degree for degree, undiminished and unnoticeable. This is the single
most important fact about thermocouple instrumentation: the expensive, high-temperature,
wide-range sensor is only ever as good as the cheap sensor measuring its terminal block,
which is why good instruments put that sensor in the isothermal block itself and let it
settle.
''',
                    },
                ],
            },
            "build": {
                "title": "Compensating a cold junction",
                "minutes": 22,
                "brief": r'''
A type K thermocouple, drawn the way it actually behaves: two emf sources in one loop.

- The **measuring junction** is in a bath at 100 °C. Against a 0 °C reference the table
  gives it **4.096 mV**, and it is the vertical source on the left. (The editor rounds
  part labels to three figures and then drops any trailing zeros, so it is drawn as
  4.1 mV; the value in the part is 4.096 mV.)
- The **reference junction** is the terminal block, sitting at the laboratory's 25 °C.
  The table gives it **1.000 mV**, and it is the horizontal source at the bottom, drawn
  with its + terminal towards the meter's LO so that it *opposes* the measuring
  junction. That opposition is not a drawing convention: it is why a thermocouple
  measures a difference.
- The meter is the **1 MΩ** input with the probe on it.

Solve it and the meter reads 4.096 − 1.000 = **3.096 mV**, which the table converts to
75.9 °C. The bath is at 100 °C.

## What to add

Every thermocouple instrument fixes this the same way. It measures the terminal block
with a second sensor, looks up the emf that block *would* have produced against 0 °C,
and adds it back — in series, aiding the measuring junction, so that what reaches the
converter is the emf a 0 °C reference would have given.

Add **one voltage source** to the loop to do that. Its value is not a free choice; it is
whatever the table says the reference junction is worth at the temperature it is
actually at.

## Drawing it

Series is series, so it may go anywhere in the loop — break a wire, drop the source into
the gap, and rejoin. What is not free is which way round it goes: the + terminal of a
horizontal source is its right-hand pin and of a vertical one its top pin, and the
editor draws the + so it is never a guess. Get it backwards and the meter will read
2.096 mV, which the table puts at 51.8 °C, and the checks will say so.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 0.004096},
                        {"id": "p1", "kind": "V", "x": 5, "y": 8, "rot": 0, "value": 0.001},
                        {"id": "p2", "kind": "GND", "x": 8, "y": 8},
                        {"id": "p3", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 14, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [14, 4]},
                        {"a": [12, 4], "b": [12, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [3, 7], "b": [3, 8]},
                        {"a": [3, 8], "b": [4, 8]},
                        {"a": [6, 8], "b": [8, 8]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 0.004096},
                        {"id": "p1", "kind": "V", "x": 5, "y": 8, "rot": 0, "value": 0.001},
                        {"id": "p2", "kind": "GND", "x": 8, "y": 8},
                        {"id": "p3", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 14, "y": 4},
                        {"id": "p6", "kind": "V", "x": 7, "y": 4, "rot": 0, "value": 0.001},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [6, 4]},
                        {"a": [8, 4], "b": [14, 4]},
                        {"a": [12, 4], "b": [12, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [3, 7], "b": [3, 8]},
                        {"a": [3, 8], "b": [4, 8]},
                        {"a": [6, 8], "b": [8, 8]},
                    ],
                },
                "checks": [
                    {"name": "both junctions are still in the loop, and the compensation matches the block", "code": r'''
c.assert(c.count('V') === 3,
  'Three sources: the measuring junction, the reference junction, and the compensation ' +
  'you add. Found ' + c.count('V') + '. Deleting the reference junction is not ' +
  'compensating for it — the terminal block is at 25 C whether or not it is drawn.');
const vals = c.values('V').map(Math.abs).sort(function (a, b) { return a - b; });
c.close(vals[0], 0.001, 0.02, 'the smallest of the three emfs');
c.close(vals[1], 0.001, 0.02,
  'the middle of the three emfs — the compensation has to be worth what the reference ' +
  'junction is worth at the temperature the block is actually at, which is 1.000 mV');
c.close(vals[2], 0.004096, 0.02, 'the largest of the three, the measuring junction');
'''},
                    {"name": "the meter is still a 1 MΩ input on the probed node", "code": r'''
const out = c.outNode();
const meter = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 1e6) <= 2e4 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(meter.length === 1,
  'The meter is the 1 MOhm from the probed node to ground, and it stays where it is.');
'''},
                    {"name": "all three are in series, not across one another", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 3, 'Three sources carry three currents; found ' + ids.length + '.');
const mags = ids.map(function (k) { return Math.abs(cur[k]); });
const hi = Math.max.apply(null, mags);
const lo = Math.min.apply(null, mags);
c.assert(lo > 1e-12 && hi / lo <= 1.02,
  'The three sources are not all carrying the same current, so they are not all in the ' +
  'same loop. A compensating emf placed across a junction cancels nothing and shorts ' +
  'something; it has to be in series with the loop.');
'''},
                    {"name": "the meter now reads what 100 °C is worth", "code": r'''
c.close(c.vout(), 0.004096, 0.01,
  'the voltage at the meter. Uncompensated it was 3.096 mV, which the table reads as ' +
  '75.9 C; compensated it should be the 4.096 mV that means 100 C');
'''},
                ],
                "hints": [
                    "The loop delivers $E(100) - E(25)$ and you want $E(100)$. The difference between those two is one term, and it is the one you have to put back.",
                    "So the source you add is 1.000 mV — the same value as the reference junction, because it is standing in for a reference junction at 0 °C instead of at 25 °C.",
                    "Break the top wire between the measuring junction and the meter, place a horizontal source in the gap, and wire both sides back up. Set its value to `1m`; the value box understands the suffix.",
                    "Orientation is the whole exercise. The reference junction opposes the measuring junction, so your compensation must *aid* it: going along the top rail towards the meter you should be climbing, not falling. Check yourself before running — the meter should read 4.096 mV and the current round the loop should be 4.096 nA, since the only resistance in it is the meter's 1 MΩ.",
                ],
            },
            "derive": {
                "title": "Reading a temperature off a thermistor",
                "minutes": 13,
                "vars": ["beta", "T", "T_0", "R", "R_0", "u", "alpha"],
                "brief": r'''
The two-parameter model of an NTC thermistor is

$$R = R_0\exp\left(\beta\left(\frac{1}{T} - \frac{1}{T_0}\right)\right)$$

with both temperatures in **kelvin**, $R_0$ the resistance at the reference temperature
$T_0$, and $\beta$ a constant of the material in kelvin — around 3950 K for the ordinary
10 kΩ parts.

That gives resistance from temperature, and you need the other direction. Write $u$ for
the quantity $\ln(R/R_0)$, which is a number your code can produce from a reading, and
work through to $T$.
''',
                "steps": [
                    {
                        "prompt": "Take logarithms of both sides. Write $u = \\ln(R/R_0)$ in terms of $\\beta$, $T$ and $T_0$, over a single denominator.",
                        "given": "$\\ln(R/R_0)$ is exactly the exponent, since the logarithm and the exponential undo one another.",
                        "answer": "\\frac{\\beta (T_0 - T)}{T T_0}",
                        "placeholder": "e.g. \\frac{a (b + c)}{d}",
                        "hint": "$1/T - 1/T_0$ over the common denominator $TT_0$ is $(T_0 - T)/TT_0$. Mind the order in the numerator.",
                        "deconstruct": [
                            "$u = \\beta(1/T - 1/T_0)$.",
                            "Put the bracket over $TT_0$: $(T_0 - T)/(TT_0)$.",
                        ],
                    },
                    {
                        "prompt": "Now solve for $1/T$, in terms of $T_0$, $u$ and $\\beta$.",
                        "given": "Go back to $u = \\beta(1/T - 1/T_0)$ and rearrange; this is one division and one addition.",
                        "answer": "\\frac{1}{T_0} + \\frac{u}{\\beta}",
                        "placeholder": "e.g. \\frac{a}{b} - \\frac{c}{d}",
                        "hint": "Divide both sides by $\\beta$, then move the $1/T_0$ across.",
                        "deconstruct": [
                            "$u/\\beta = 1/T - 1/T_0$.",
                            "Add $1/T_0$ to both sides.",
                        ],
                    },
                    {
                        "prompt": "Invert that to get $T$ itself, in terms of $\\beta$, $T_0$ and $u$.",
                        "given": "Put the previous line over one denominator before turning it upside down.",
                        "answer": "\\frac{\\beta T_0}{\\beta + u T_0}",
                        "placeholder": "e.g. \\frac{a b}{c - d}",
                        "hint": "$1/T_0 + u/\\beta = (\\beta + uT_0)/(\\beta T_0)$, and $T$ is the reciprocal of that.",
                        "deconstruct": [
                            "Common denominator $\\beta T_0$.",
                            "The numerator becomes $\\beta + uT_0$.",
                            "$T$ is one over the whole thing.",
                        ],
                    },
                    {
                        "prompt": "Finally the sensitivity. Differentiating the model gives $dR/dT = -(\\beta/T^2)R$. Write the fractional sensitivity $\\alpha = (1/R)(dR/dT)$.",
                        "given": "One substitution and one cancellation; $R$ appears on both sides.",
                        "answer": "-\\frac{\\beta}{T^2}",
                        "placeholder": "e.g. -\\frac{a}{b}",
                        "hint": "Divide the given derivative by $R$. Nothing else has to happen.",
                        "deconstruct": [
                            "$\\frac{1}{R}\\frac{dR}{dT} = \\frac{1}{R}\\left(-\\frac{\\beta}{T^2}R\\right)$.",
                            "The two $R$ cancel.",
                        ],
                    },
                ],
                "closing": r'''
Three things worth carrying away from those four lines.

The inversion is exact and cheap: one logarithm, one reciprocal, no iteration and no
lookup table, which is why the $\beta$ model survives in firmware that has neither room
nor time for a polynomial.

The sensitivity $-\beta/T^2$ is the reason a thermistor is worth the trouble at all. At
298 K with $\beta = 3950$ K it is 4.4% per kelvin, more than ten times a platinum
sensor's 0.39%/K, so the divider or bridge in front of it can be crude and the amplifier
after it can be ordinary. It is also the reason the useful range is short: at 373 K the
same part gives 2.8%/K and at 233 K it gives 7.3%/K, so a circuit scaled for one end of
the range is badly scaled for the other.

And $\beta$ is not a constant. It is fitted, over a stated interval, to a curve that is
not really an exponential in $1/T$ at all — which is what the lab below is about.
''',
            },
            "lab": {
                "title": "Fitting a curve, and reading its residuals",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
`table.py` holds nine points of a 10 kΩ NTC thermistor's resistance against temperature,
from 0 °C to 100 °C. They were produced from the three-parameter Steinhart–Hart model
that manufacturers' tables follow, so they are not a $\beta$ curve with noise on it —
they are a different curve, and that is the point of the exercise.

Fit the two-parameter model to them, invert it, and then look at what the fit could not
explain.

- `fit_beta(temps_c, resistances, t0_c=25.0)` — a least-squares straight line of
  $\ln R$ against $1/T$ (with $T$ in kelvin). Its slope is $\beta$; return
  `(beta, r0)`, where `r0` is the resistance the *fitted line* gives at `t0_c`. Do not
  reach for the measured value at 25 °C: a least-squares line does not pass through any
  particular point, and using one that it misses would put a systematic offset into
  everything downstream.
- `resistance_at(t_c, beta, r0, t0_c=25.0)` — the model, forwards.
- `temperature_at(r, beta, r0, t0_c=25.0)` — the model, inverted, in degrees Celsius.
  You derived this above.
- `residuals(temps_c, resistances, beta, r0, t0_c=25.0)` — for each point, the
  temperature the model infers from the measured resistance, minus the temperature that
  point was actually taken at. In kelvin, signed, one per point.
- `worst(residuals_k)` — the largest magnitude in a list of residuals.

`KELVIN = 273.15` is defined for you. `math` is all you need; a straight line fit is two
sums and a division, and writing it out once is worth more than importing it.

The last thing the file prints is the fit over the whole 0–100 °C range and the same fit
restricted to 12.5–50 °C. The difference between those two numbers is the lab.
''',
                "files": [
                    {"name": "table.py", "ro": True, "content": r'''
"""Nine points of a 10 k NTC thermistor, resistance in ohms against temperature in C.

Generated from the Steinhart-Hart model

    1/T = A + B ln(R) + C (ln R)^3

with A = 1.129148e-3, B = 2.34125e-4, C = 8.76741e-8 — the coefficients quoted for an
ordinary 10 k / 3950 K part — and rounded to the 0.1 ohm a table would print. There is
no measurement noise in these numbers at all, which is deliberate: everything the fit
below fails to explain is the difference between two models, not scatter.
"""

TABLE = [
    (0.0, 32650.4),
    (12.5, 17668.7),
    (25.0, 9999.9),
    (37.5, 5892.6),
    (50.0, 3601.0),
    (62.5, 2274.4),
    (75.0, 1480.0),
    (87.5, 989.7),
    (100.0, 678.4),
]

TEMPS = [t for t, _ in TABLE]
RESISTANCES = [r for _, r in TABLE]
'''},
                    {"name": "main.py", "content": r'''
"""A thermistor's beta model, fitted to a table, and the residuals it leaves."""

import math

from table import TABLE, TEMPS, RESISTANCES

KELVIN = 273.15


def fit_beta(temps_c, resistances, t0_c=25.0):
    """Least-squares fit of ln(R) against 1/T. Returns (beta, r0)."""
    # TODO: x is 1/(t + KELVIN), y is log(r). Slope is beta; the intercept plus
    # beta / (t0_c + KELVIN) is log(r0).
    return (0.0, 0.0)


def resistance_at(t_c, beta, r0, t0_c=25.0):
    """The model, forwards: resistance in ohms at this temperature."""
    # TODO: r0 * exp(beta * (1/T - 1/T0)), both temperatures in kelvin.
    return 0.0


def temperature_at(r, beta, r0, t0_c=25.0):
    """The model, inverted: degrees Celsius from a resistance."""
    # TODO: 1/T = 1/T0 + ln(r/r0)/beta, then back to Celsius.
    return 0.0


def residuals(temps_c, resistances, beta, r0, t0_c=25.0):
    """Inferred temperature minus true temperature, in kelvin, one per point."""
    # TODO: one call to temperature_at per point.
    return []


def worst(residuals_k):
    """The largest magnitude in a list of residuals."""
    # TODO: the largest absolute value.
    return 0.0


if __name__ == "__main__":
    beta, r0 = fit_beta(TEMPS, RESISTANCES)
    print("over 0 to 100 C:  beta = %.1f K, R25 = %.1f ohm" % (beta, r0))
    res = residuals(TEMPS, RESISTANCES, beta, r0)
    for t, e in zip(TEMPS, res):
        print("   %6.1f C   %+7.4f K" % (t, e))
    print("   worst %.4f K" % worst(res))

    narrow = [(t, r) for t, r in TABLE if 12.5 <= t <= 50.0]
    nt = [t for t, _ in narrow]
    nr = [r for _, r in narrow]
    b2, r2 = fit_beta(nt, nr)
    print("over 12.5 to 50 C: beta = %.1f K, R25 = %.1f ohm" % (b2, r2))
    print("   worst %.4f K" % worst(residuals(nt, nr, b2, r2)))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""A thermistor's beta model, fitted to a table, and the residuals it leaves."""

import math

from table import TABLE, TEMPS, RESISTANCES

KELVIN = 273.15


def fit_beta(temps_c, resistances, t0_c=25.0):
    """Least-squares fit of ln(R) against 1/T. Returns (beta, r0)."""
    xs = [1.0 / (t + KELVIN) for t in temps_c]
    ys = [math.log(r) for r in resistances]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    beta = sxy / sxx
    intercept = my - beta * mx
    return (beta, math.exp(intercept + beta / (t0_c + KELVIN)))


def resistance_at(t_c, beta, r0, t0_c=25.0):
    """The model, forwards: resistance in ohms at this temperature."""
    return r0 * math.exp(beta * (1.0 / (t_c + KELVIN) - 1.0 / (t0_c + KELVIN)))


def temperature_at(r, beta, r0, t0_c=25.0):
    """The model, inverted: degrees Celsius from a resistance."""
    inv = 1.0 / (t0_c + KELVIN) + math.log(r / r0) / beta
    return 1.0 / inv - KELVIN


def residuals(temps_c, resistances, beta, r0, t0_c=25.0):
    """Inferred temperature minus true temperature, in kelvin, one per point."""
    return [temperature_at(r, beta, r0, t0_c) - t
            for t, r in zip(temps_c, resistances)]


def worst(residuals_k):
    """The largest magnitude in a list of residuals."""
    return max(abs(e) for e in residuals_k)


if __name__ == "__main__":
    beta, r0 = fit_beta(TEMPS, RESISTANCES)
    print("over 0 to 100 C:  beta = %.1f K, R25 = %.1f ohm" % (beta, r0))
    res = residuals(TEMPS, RESISTANCES, beta, r0)
    for t, e in zip(TEMPS, res):
        print("   %6.1f C   %+7.4f K" % (t, e))
    print("   worst %.4f K" % worst(res))

    narrow = [(t, r) for t, r in TABLE if 12.5 <= t <= 50.0]
    nt = [t for t, _ in narrow]
    nr = [r for _, r in narrow]
    b2, r2 = fit_beta(nt, nr)
    print("over 12.5 to 50 C: beta = %.1f K, R25 = %.1f ohm" % (b2, r2))
    print("   worst %.4f K" % worst(residuals(nt, nr, b2, r2)))
'''}],
                "hints": [
                    "The fit is an ordinary least-squares line: with $x = 1/T$ and $y = \\ln R$, the slope is $\\sum(x-\\bar{x})(y-\\bar{y})/\\sum(x-\\bar{x})^2$ and the intercept is $\\bar{y} - \\text{slope}\\,\\bar{x}$.",
                    "`r0` is not `resistances[2]`. The line's value at $T_0$ is $\\exp(\\text{intercept} + \\beta/T_0)$, and it comes out about 1% below the table's own 25 °C entry — which is what a least-squares fit over a curve does, and part of what the residuals are showing you.",
                    "`temperature_at` is the derivation from this module: `1/T0 + log(r/r0)/beta`, inverted, minus `KELVIN`. Test it against `resistance_at` first — a value put through one and back through the other must return to where it started.",
                    "The residual is *inferred minus true*, in that order, so a model that reads high gives a positive residual. Getting the sign backwards will still pass a test on the magnitude and fail every test that reads the shape.",
                ],
                "tests": [
                    {"name": "the fit over the whole range", "code": r'''
beta, r0 = fit_beta(TEMPS, RESISTANCES)
assert abs(beta - 3951.302326216045) < 0.05, \
    f"the least-squares beta over 0-100 C is 3951.3 K, got {beta}"
assert abs(r0 - 9908.445164254643) < 0.5, \
    f"the fitted line gives 9908.4 ohm at 25 C, got {r0}"
assert abs(r0 - 9999.9) > 50, \
    "r0 must come from the fit, not from the table's own 25 C entry"
'''},
                    {"name": "the model runs both ways", "code": r'''
beta, r0 = fit_beta(TEMPS, RESISTANCES)
assert abs(resistance_at(25.0, beta, r0) - r0) < 1e-9, \
    "at the reference temperature the model must return r0 exactly"
assert abs(temperature_at(r0, beta, r0) - 25.0) < 1e-9, \
    "and the inverse must return the reference temperature"
back = temperature_at(resistance_at(60.0, beta, r0), beta, r0)
assert abs(back - 60.0) < 1e-9, f"a round trip through both must return 60.0, got {back}"
cold = resistance_at(0.0, beta, r0)
assert cold > 30000.0, f"an NTC gets bigger as it cools; at 0 C expect over 30 k, got {cold}"
hot = resistance_at(100.0, beta, r0)
assert hot < 750.0, f"and smaller as it warms; at 100 C expect under 750 ohm, got {hot}"
'''},
                    {"name": "the residuals are a shape, not a scatter", "code": r'''
beta, r0 = fit_beta(TEMPS, RESISTANCES)
res = residuals(TEMPS, RESISTANCES, beta, r0)
assert len(res) == len(TEMPS), "one residual per point"
assert abs(res[0] - 0.3873) < 0.002, f"the 0 C point should sit +0.387 K high, got {res[0]}"
assert abs(res[4] - (-0.3459)) < 0.002, f"the 50 C point should sit -0.346 K low, got {res[4]}"
assert abs(res[8] - 0.6254) < 0.002, f"the 100 C point should sit +0.625 K high, got {res[8]}"
signs = [1 if e > 0 else -1 for e in res]
assert signs[0] > 0 and signs[4] < 0 and signs[8] > 0, \
    "positive at both ends and negative in the middle: that is a curve the model is missing"
'''},
                    {"name": "the worst residual, and what shrinking the range does to it", "code": r'''
beta, r0 = fit_beta(TEMPS, RESISTANCES)
full = worst(residuals(TEMPS, RESISTANCES, beta, r0))
assert abs(full - 0.6254221379604701) < 0.002, \
    f"over the full range the two-parameter model is out by 0.625 K, got {full}"
narrow = [(t, r) for t, r in TABLE if 12.5 <= t <= 50.0]
nt = [t for t, _ in narrow]
nr = [r for _, r in narrow]
b2, r2 = fit_beta(nt, nr)
assert abs(b2 - 3915.0032823860997) < 0.05, \
    f"fitted over 12.5-50 C the slope is 3915.0 K, not 3951.3, got {b2}"
tight = worst(residuals(nt, nr, b2, r2))
assert abs(tight - 0.0707977280235923) < 0.001, \
    f"over the narrower range the same model is out by only 0.071 K, got {tight}"
assert full > 8 * tight, \
    "restricting the range by a factor of three improved the fit by nearly ten"
'''},
                    {"name": "worst() reads magnitudes, not values", "code": r'''
assert abs(worst([0.1, -0.4, 0.2]) - 0.4) < 1e-15, \
    "the worst residual is the largest magnitude, whichever way it points"
assert abs(worst([-0.9]) - 0.9) < 1e-15, "a single residual is its own worst case"
assert abs(worst([0.0, 0.0]) - 0.0) < 1e-15, "a perfect fit has a worst case of zero"
'''},
                ],
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "How long before the reading is true",
            "summary": "Everything in the chain has a time constant and none of them is on the front panel. A reading taken too early is not noisy; it is wrong, by an amount you can work out in advance.",
            "concepts": [
                "A sensor with thermal or mechanical inertia is a first-order low-pass on the quantity it is measuring. After a step it closes the remaining gap as $e^{-t/\\tau}$, so reaching a fraction $\\varepsilon$ of the step takes $\\tau\\ln(1/\\varepsilon)$: 2.3τ for 10%, 4.6τ for 1%, 6.9τ for 0.1%. Five time constants is a habit, not a specification.",
                "Under a *ramp* the same lag settles to a constant error rather than a decaying one. A sensor of time constant $\\tau$ following a quantity changing at $k$ per second reads $k\\tau$ behind, indefinitely — a thermowell with $\\tau = 20$ s watching a bath ramped at 2 K/min reads 0.67 K low the whole way up, and becomes correct only after the ramp stops.",
                "$\\tau$ belongs to the installation and not to the sensor. The same probe is a second or two in stirred water and most of a minute in still air, because $\\tau$ is the heat capacity divided by the conductance to the medium — which is why a data sheet quotes a time constant with a medium attached to it, and why a thermowell that improves the mechanical protection makes the dynamics worse.",
                "A sensor with mass and a restoring force is second order, with the $\\omega_n$ and $\\zeta$ of any RLC. Damping near 0.6–0.7 gives the flattest amplitude response; at $\\zeta = 0.707$ the response is within 1% of flat only up to about $0.37\\omega_n$, so a transducer's natural frequency has to be several times the highest frequency in the signal, not merely above it.",
                "It shows up far from sensors. An autoranging meter throws away readings after a range change while its input chain settles; a longer aperture is a narrower filter and therefore a longer wait; and every averaging setting that quietens a reading has bought that quiet with a settling time somebody now has to sit through. Bandwidth traded for noise is always paid for in time.",
            ],
            "read": {
                "title": "The display stops moving before the probe arrives",
                "minutes": 15,
                "body": r'''
A sheathed temperature probe, time constant 8.00 s in stirred water, is lifted out of
20.0 °C air and lowered into a bath held at 80.0 °C. The display updates twice a second
and shows tenths. Watch it.

```text
     t        reading      still to go     change in the next 0.5 s
   0.0 s     20.000 C       60.000 K            3.750 K
   8.0 s     57.927 C       22.073 K            1.380 K
  16.0 s     71.880 C        8.120 K            0.508 K
  24.0 s     77.013 C        2.987 K            0.187 K
  32.0 s     78.901 C        1.099 K            0.069 K
  40.0 s     79.596 C        0.404 K            0.025 K
  51.2 s     79.900 C        0.100 K            0.006 K
```

Look at the last column against the display's 0.1 K resolution. From about 32 seconds
onwards the reading changes by less than one digit between updates; from 40 seconds it
is changing by a quarter of a digit. To anybody watching, the display has stopped. It
has 0.4 K still to go, and it will not be within 0.1 K of the bath for another eleven
seconds.

The reading did not become correct when it stopped moving. It stopped moving because the
approach is exponential and the tail of an exponential is slower than the instrument can
show.

## Where the exponential comes from

The probe has a heat capacity $C$ and it exchanges heat with the bath through some
conductance $hA$ — a surface area times a film coefficient. Heat flows in proportion to
the temperature difference, so

$$C\,\frac{dT}{dt} = hA\,(T_{\infty} - T)$$

which is a first-order equation with a time constant

$$\tau = \frac{C}{hA}$$

and, after a step from $T_0$ to $T_\infty$, the solution

$$T(t) = T_{\infty} - (T_{\infty}-T_0)\,e^{-t/\tau}$$

Two facts are already visible in $\tau = C/hA$, and they are the ones that matter on a
plant. The numerator belongs to the probe. The denominator belongs to the *medium and
the mounting*. The same probe is a second or two in stirred water, ten in slow water,
and most of a minute in still air, because $h$ changes by more than an order of
magnitude between them. A data sheet that quotes a time constant without naming a medium
has quoted nothing. And a thermowell — which improves the mechanical protection, allows
the probe to be withdrawn under pressure, and is often mandatory — adds mass to the
numerator and a thermal resistance in series with the denominator, so it makes both
terms worse at once. The 8 s probe above can be 40 s in a dry well.

## How long to wait, and what it costs

Set the outstanding gap to a fraction $\varepsilon$ of the step and take logarithms:

$$e^{-t/\tau} = \varepsilon
\qquad\Rightarrow\qquad
t = \tau\ln\frac{1}{\varepsilon}$$

which is 2.30τ for 10%, 4.61τ for 1% and 6.91τ for 0.1%. Put the opening numbers in: a
60.0 K step and a 0.100 K tolerance is $\varepsilon = 1/600$, so
$t = 8\ln 600 = 51.2$ s. That is this module's numerical problem, **Waiting for a
thermometer**, and its two wrong answers are the two ways people skip the logarithm.

Now read the shape of that result rather than the number. The wait grows with the
*logarithm* of the precision demanded, so every further factor of ten costs the same
$\tau\ln 10$ regardless of where you started. Set that against the other way of buying
precision: module 10's averaging improves a random uncertainty as $\sqrt{N}$, so ten
times better costs a hundred times longer.

```python
import math

TAU, STEP = 8.0, 60.0
for tol in (0.1, 0.01, 0.001):
    print("within %6.3f K: wait %5.1f s   (for the same gain by averaging: %7.0f readings)"
          % (tol, TAU * math.log(STEP / tol), (0.1 / tol) ** 2))
print("every further factor of ten costs tau*ln(10) = %.1f s" % (TAU * math.log(10.0)))
```

```text
within  0.100 K: wait  51.2 s   (for the same gain by averaging:       1 readings)
within  0.010 K: wait  69.6 s   (for the same gain by averaging:     100 readings)
within  0.001 K: wait  88.0 s   (for the same gain by averaging:   10000 readings)
every further factor of ten costs tau*ln(10) = 18.4 s
```

Eighteen more seconds against ten thousand readings, for the same factor of a hundred.
Settling is a cheap purchase and averaging is an expensive one, and the reason to know
both scalings is to know which of the two problems you actually have.

## Five time constants is a habit, not a specification

$e^{-5} = 0.0067$, so five time constants leaves 0.67% of the step outstanding. On the
60 K step above that is 0.40 K — four times the 0.1 K tolerance somebody asked for. The
rule of five is fine when the required tolerance happens to be under a per cent of the
step, and it is silently wrong the moment it is not. The step size is half of the
calculation and the habit does not contain it.

## Under a ramp the lag never goes away

A step is the easy case, because the error decays. Most process measurements are not
steps: a bath is ramped, a furnace is brought up, an oven cycles. Put
$T_\infty(t) = kt$ into the equation and try the solution $T = k(t - \tau)$:

$$\tau\,\frac{dT}{dt} + T = \tau k + k t - k\tau = kt$$

It satisfies the equation exactly, so once any initial transient has died the sensor
reads

$$T(t) = k\,(t - \tau)$$

a *constant* $k\tau$ behind the truth, indefinitely. A thermowell with $\tau = 20$ s
watching a bath ramped at 2 K/min reads $0.0333 \times 20 = 0.667$ K low the whole way
up, and becomes correct only after the ramp stops.

This is worth separating from the step case because it looks nothing like it on a chart.
There is no visible settling, no approach, nothing to wait for — the trace is smooth and
parallel to the truth and offset from it, which is indistinguishable from a calibration
error. A controller comparing that reading with a setpoint is being told the batch is
0.667 K cooler than it is, and will overshoot by about that much when the ramp ends.

## Sensors with mass and a spring

An accelerometer, a diaphragm pressure sensor and a moving-coil galvanometer all have
inertia and a restoring force, so they are second order, with the $\omega_n$ and $\zeta$
of any RLC. The amplitude response is

$$|H| = \frac{1}{\sqrt{(1-r^{2})^{2} + (2\zeta r)^{2}}},\qquad r = \frac{f}{f_n}$$

At $\zeta = 1/\sqrt{2}$ the middle term does something worth noticing: $(2\zeta r)^2 =
2r^2$, and $(1-r^2)^2 + 2r^2 = 1 + r^4$, so

$$|H| = \frac{1}{\sqrt{1+r^{4}}}$$

with no $r^2$ term at all. That is the flattest response any second-order system has,
and it is why 0.707 is the number everybody quotes. Ask for 1% flatness and it gives

$$1 + r^4 \le \frac{1}{0.99^{2}} = 1.0203
\qquad\Rightarrow\qquad
r \le 0.3775$$

So a transducer damped to 0.707 is honest to 1% only up to about **0.38 of its natural
frequency**. Measuring 100 Hz components to 1% needs $f_n \ge 265$ Hz, not 100 Hz and
not 150 Hz. A natural frequency merely *above* the signal is not enough; it has to be
several times above, and this module's slider exercise, **Damping a transducer you
cannot see**, asks for 300–500 Hz with $\zeta$ between 0.60 and 0.75 for exactly that
reason. The two constraints are not independent — $\zeta = \frac{R}{2}\sqrt{C/L}$ and
$\omega_n = 1/\sqrt{LC}$ — so every change to $L$ or $C$ moves both, which is the
ordinary condition of transducer design.

## The mistake, and why it is tempting

The mistake is treating "the display has stopped changing" as evidence that the reading
has arrived. It is tempting because it is a genuine observation, made carefully, and
because for a first-order system the criterion is self-defeating in a way nothing on the
bench announces: the closer the probe gets, the slower it approaches, so a display
resolving 0.1 K and updating twice a second necessarily goes still while an error larger
than 0.1 K remains. The evidence of your eyes is a statement about the display, not
about the probe.

The second mistake is the ramp case, and it is worse because there is nothing at all to
watch. Nobody stands over a chart recorder waiting for a smooth ramp to settle, because
it never occurs to them that it has not. The tell is arithmetic rather than observation:
if the quantity is moving at $k$ per second and your sensor's time constant is $\tau$,
you are $k\tau$ behind, and the only question is whether $k\tau$ matters.

## Where this stops holding

The first-order model assumes the probe is isothermal — one temperature throughout, one
heat capacity, one conductance. A sheathed probe in a thermowell is a stack: fluid to
well, well to air gap, gap to sheath, sheath to element. That is three or four time
constants in series, and its step response is S-shaped rather than exponential: it
starts *slower* than $e^{-t/\tau}$ predicts, so fitting a single $\tau$ to the tail and
extrapolating backwards understates the wait. Where a real settling time matters,
measure it rather than compute it.

The step assumes the bath does not care. Lower a probe with real heat capacity into a
small volume and it cools it, so $T_\infty$ moves during the measurement and the
exponential is chasing something that is itself relaxing.

$\tau$ is not a constant even in one installation. $h$ depends on flow, so a probe
characterised in stirred water is a different instrument in a stagnant pocket, and a
flow that stops during a shutdown makes the sensor several times slower at precisely the
moment somebody is watching it most closely.

The ramp result is a steady state, reached after several time constants. Immediately
after the ramp begins, the lag is still growing towards $k\tau$; immediately after it
ends, the sensor spends several more time constants catching up. The constant-offset
picture holds in the middle and not at either end.

And for the second-order case, $\zeta$ and $f_n$ belong to the installation too. A
pressure transducer connected through a metre of narrow tubing has a natural frequency
set by that tubing and the fluid in it, not by the sensor, and it is usually far lower
than the sensor's own. Every number in this module is a property of what you built, not
of what you bought.
''',
            },
            "quiz": {
                "title": "Lags, ramps and reading too early",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A thermometer with a time constant of 8.0 s is moved from 20 °C air into an 80 °C bath. What does it read 24 s later?",
                        "opts": ["77.0 °C", "80.0 °C", "60.0 °C", "79.6 °C"],
                        "a": 0,
                        "why": r'''
Three time constants leaves $e^{-3} = 4.98\%$ of the 60 K step, which is 2.99 K, so the
reading is 77.0 °C. The instrument is not broken, not noisy and not miscalibrated; it is
3 K wrong because it was read too early, and it will still be 0.4 K wrong at five time
constants and 0.06 K wrong at seven. The 79.6 °C answer is that same $e^{-5}$ residual
of 0.40 K — what the thermometer reads after 40 s rather than after 24 s, which is
exactly the decision this module is about.
''',
                    },
                    {
                        "q": "A thermowell with a 20 s time constant watches a bath being ramped at 2 K per minute. Once the transient has died away, the reading is:",
                        "opts": [
                            "correct — the exponential has finished",
                            "0.67 K low, and stays there for the whole ramp",
                            "0.67 K high, and stays there for the whole ramp",
                            "40 K low",
                        ],
                        "a": 1,
                        "why": r'''
A first-order lag following a ramp of slope $k$ settles to a steady error of $k\tau$:
$2\ \text{K/min} = 0.0333$ K/s, times 20 s, is 0.67 K, and the sensor reads *low*
because it is always catching up. The exponential really has finished — there is nothing
left to settle — and the error is now a fixed offset that no amount of further waiting
removes. It is the most quietly misleading behaviour in the module, because the reading
is perfectly steady and perfectly wrong, and the only ways out are to stop the ramp, to
ramp more slowly, or to correct for $k\tau$ knowing both.
''',
                    },
                    {
                        "q": "Your reading is noisy, so you switch on the meter's ten-reading average. What else have you done?",
                        "opts": [
                            "nothing — averaging is free",
                            "added a settling time: the display now takes ten readings to respond to a step",
                            "reduced the systematic error by $\\sqrt{10}$ as well",
                            "increased the resolution by a factor of ten",
                        ],
                        "a": 1,
                        "why": r'''
An average of the last ten readings is a low-pass filter, and every low-pass filter is a
delay. The noise falls by about $\sqrt{10}$ and the response to a real change is
smeared over ten conversion times — so a value that is changing is now reported late as
well as smoothly, and the smoothness makes it look more trustworthy rather than less.
Systematic error is untouched, as the loading module insisted, and
resolution is a property of the converter and the display.
''',
                    },
                    {
                        "q": "A pressure transducer's step response overshoots by 5%. Its damping ratio is about:",
                        "opts": ["0.69", "0.05", "0.95", "0.35"],
                        "a": 0,
                        "why": r'''
The overshoot of a second-order step response is $\exp(-\pi\zeta/\sqrt{1-\zeta^2})$.
Setting that to 0.05 gives $\pi\zeta/\sqrt{1-\zeta^2} = \ln 20 = 3.00$ and hence
$\zeta = 0.69$ — which is, conveniently, almost exactly the damping that gives the
flattest amplitude response. 5% overshoot and maximal flatness are the same design point
seen from the time and frequency sides, and that coincidence is why so many transducers
are damped there.
''',
                    },
                    {
                        "q": "Why does a probe's data sheet say “1.5 s in stirred water, 40 s in still air” rather than just quoting a time constant?",
                        "opts": [
                            "because the sensor's heat capacity changes with the medium",
                            "because $\\tau$ is the sensor's heat capacity divided by its conductance to the medium, and the medium sets that conductance",
                            "because water is a better conductor of electricity",
                            "because the manufacturer cannot measure it accurately in air",
                        ],
                        "a": 1,
                        "why": r'''
The heat capacity is the probe's own and does not change; what changes by a factor of
nearly thirty is how fast heat crosses the boundary into it. Still air is a poor
conductor and a poor convector, stirred water is neither, and a thermowell adds a
further layer of metal and trapped air on the outside of that. A time constant is
therefore a property of an installation, and a figure quoted without the medium is not
a specification at all — which is worth remembering when the process fluid is neither
water nor air.
''',
                    },
                    {
                        "q": "A transducer with $\\zeta = 0.707$ and a natural frequency of 318 Hz is used on a signal containing components up to 200 Hz. What should you expect?",
                        "opts": [
                            "no error — 200 Hz is below the natural frequency",
                            "components near 200 Hz read about 7% low",
                            "components near 200 Hz read about 7% high",
                            "the transducer will not respond above 159 Hz at all",
                        ],
                        "a": 1,
                        "why": r'''
At $\zeta = 0.707$ the magnitude is $1/\sqrt{1 + (\omega/\omega_n)^4}$, and
$200/318 = 0.63$ gives $1/\sqrt{1.156} = 0.930$: 7% low. Being below the natural
frequency buys nothing on its own — the response is only flat to within 1% up to about
$0.37\omega_n$, or 118 Hz here, and everything above that is being attenuated by an
amount that depends on frequency, which is a distortion of the waveform rather than a
scale error. The fix is a transducer with a higher $\omega_n$, or a correction applied
knowing both $\omega_n$ and $\zeta$.
''',
                    },
                ],
            },
            "tune": {
                "title": "Damping a transducer you cannot see",
                "minutes": 11,
                "brief": r'''
A seismic transducer — an accelerometer, a pressure sensor with a diaphragm, a
moving-coil galvanometer — is a mass on a spring with something dissipating energy. That
is a second-order system, and its electrical twin is the series RLC of the prerequisite
course: the inductance stands for the mass, the capacitance for the compliance of the
spring, and the resistance for the damping.

The sliders below are that RLC, and the two numbers that matter are the ones the
readout calls $\zeta$ and $f_n$.

- **$f_n$** has to be well above the highest frequency you intend to measure, because
  the response is flat only to a fraction of it. Below 300 Hz this transducer cannot
  honestly report the 100 Hz components it will be asked about.
- **$\zeta$** decides the shape near $f_n$. Too little and the response peaks, the step
  response rings, and the transducer reports resonances that are its own. Too much and
  the useful band shrinks from the other end. Between 0.60 and 0.75 is the classical
  window, and 0.707 is its middle.

The transducer opens badly damped and far too slow. Both have to be fixed at once, and
they are not independent: $\zeta = \frac{R}{2}\sqrt{C/L}$ and
$\omega_n = 1/\sqrt{LC}$, so every change to $L$ or $C$ moves both.
''',
                "prompt": "Bring the natural frequency into 300–500 Hz and the damping into 0.60–0.75, at the same time.",
                "note": "The curve is the amplitude response. When both constraints hold, its peak has gone and its flat region reaches past 100 Hz.",
                "model": "rlc",
                "initial": {"r": 60, "l": 180, "c": 12},
                "constraints": [
                    {"k": "fn", "label": "f\u2099 between 300 and 500 Hz", "min": 300.0, "max": 500.0},
                    {"k": "zeta", "label": "damping ζ between 0.60 and 0.75", "min": 0.60, "max": 0.75},
                ],
            },
            "numeric": {
                "title": "Waiting for a thermometer",
                "minutes": 7,
                "brief": r'''
The everyday version of the whole module. You know the time constant, you know how close
you need to be, and the question is how long to stand there — which is exactly the
question a process controller asks before it decides a batch has reached temperature.
''',
                "prompt": "How long after the probe enters the bath may the reading be trusted to 0.1 °C?",
                "note": "Give the answer in seconds, to the nearest tenth.",
                "figure": "A sheathed probe with a time constant of 8.00 s in stirred water is lifted out of "
                          "air at 20.0 °C and lowered into a bath held at 80.0 °C. The bath is large, so its "
                          "temperature does not move; the probe's response to the step is a single "
                          "exponential.",
                "given": [
                    {"label": "Time constant in stirred water", "value": "8.00 s"},
                    {"label": "Starting temperature", "value": "20.0 °C"},
                    {"label": "Bath temperature", "value": "80.0 °C"},
                    {"label": "Tolerance required", "value": "0.100 °C"},
                ],
                "aside": "The step is 60.0 K and you need to be within 0.100 K of the end of it, so the "
                         "fraction of the step still outstanding is 0.100/60.0.",
                "answer": 51.2,
                "tol": 0.4,
                "unit": "s",
                "hint": "The gap left after time $t$ is $60.0\\,e^{-t/\\tau}$ kelvin. Set that equal to 0.100 K and take logarithms.",
                "wrong": "If you got 40.0, that is five time constants — the habit rather than the "
                         "calculation, and it leaves $60 e^{-5} = 0.404$ K, four times the tolerance you "
                         "were given. If you got 8.0, only one time constant has gone by and 22 K of the "
                         "step is still outstanding.",
                "why": r'''
The outstanding gap is $60.0e^{-t/8}$ K. Setting that to 0.100 K gives
$e^{-t/8} = 1/600$, so $t = 8\ln(600) = 8 \times 6.397 = 51.2$ s.

Two things are worth taking from the number. First, the answer scales with the
*logarithm* of the precision you want: 0.1 K takes 51 s, 0.01 K takes 69 s, and 0.001 K
takes 88 s — each further factor of ten costs another $8\ln 10 = 18.4$ s, which is a much
kinder scaling than the $N^2$ that averaging charges for the same improvement.

Second, everything depends on $\tau$, and $\tau$ is a property of the installation. Move
this probe into a dry thermowell and its time constant might be 40 s, at which point the
same tolerance needs 256 s and any batch process reading it every minute is reporting a
temperature the bath had four minutes ago. The tolerance you can claim is set by how
long you are willing to wait, and the exchange rate between them is $\tau$.
''',
            },
        },

        # ---- M10 -----------------------------------------------------------
        {
            "title": "Noise, averaging and the number you report",
            "summary": "Below some level every instrument is reporting its own noise. Knowing where that level is, and saying so, is the last skill in the course.",
            "concepts": [
                "Any resistance generates thermal noise of spectral density $\\sqrt{4kTR}$ volts per root hertz: 4.07 nV/√Hz for 1 kΩ at 300 K, and 128.7 nV/√Hz for 1 MΩ. It is set by physics, not by workmanship.",
                "Density is per root hertz because noise powers add: over a bandwidth $B$ the total is density $\\times\\sqrt{B}$. Halving the bandwidth improves the r.m.s. noise by $\\sqrt{2}$, and costs you speed.",
                "Below the flicker corner the density rises as $1/\\sqrt{f}$ — the *power* goes as $1/f$ — so integrating for longer stops helping. Chopper stabilisation and correlated double sampling exist to move signals above that corner.",
                "Averaging $N$ independent readings reduces the random part by $\\sqrt{N}$ and the systematic part by nothing. Ten times better costs a hundred times longer, which is why averaging is a last resort rather than a first one.",
                "A Type A uncertainty is evaluated statistically from repeated readings: the standard uncertainty of the mean is $s/\\sqrt{n}$, with $s$ the sample standard deviation.",
                "A Type B uncertainty comes from anywhere else — a data sheet, a calibration certificate, a tolerance band. A stated limit $\\pm a$ with no other information is treated as a rectangular distribution of standard uncertainty $a/\\sqrt{3}$.",
                "Independent contributions combine in quadrature into the combined standard uncertainty $u_c$, and each is weighted by its sensitivity coefficient $\\partial y/\\partial x_i$ — how much the result moves when that input moves.",
                "Reporting: multiply by a coverage factor, conventionally $k = 2$ for about 95% confidence, and quote the expanded uncertainty to two significant figures with the value rounded to the same decimal place. State $k$; a bare $\\pm$ means nothing.",
                "Resolution is not accuracy. A 6½-digit display of a quantity known to 0.1% is showing four digits of measurement and two of decoration.",
            ],
            "read": {
                "title": "Powers add, and everything else on this page follows",
                "minutes": 17,
                "body": r'''
A 1 MΩ resistor sits in a screened box with nothing else in it, its two leads going to a
6½-digit meter on its fastest aperture. The resistor is connected to no source. The
meter reads a few microvolts, and the last digits wander continuously.

Swap it for a 1 kΩ resistor and the wander shrinks by a factor of about thirty. Cool the
1 MΩ one and the wander shrinks a little. Buy a better resistor and nothing happens at
all.

What the meter is reading is the resistor's thermal noise, of spectral density

$$e_n = \sqrt{4kTR}$$

which is 4.07 nV/√Hz for the 1 kΩ and 128.7 nV/√Hz for the 1 MΩ at 300 K — a ratio of
$\sqrt{1000} = 31.6$, which is the factor of thirty you saw. This is set by the
temperature and the resistance and by nothing that anybody can manufacture better.

The odd unit is the interesting part, and unpacking it gives most of this module.

## One identity, three results

Take two fluctuating voltages $v_1$ and $v_2$ and add them. The mean square of the sum
is

$$\langle (v_1+v_2)^2 \rangle
 = \langle v_1^2 \rangle + 2\langle v_1 v_2 \rangle + \langle v_2^2 \rangle$$

If the two are *uncorrelated*, the cross term averages to zero, and what is left is that
**mean squares add**. Voltages do not; powers do. Three things follow from that one line,
and they are the three things this module is about.

**First, why the density is per root hertz.** Split a bandwidth into narrow slices. The
noise in each slice is uncorrelated with the noise in every other, so their mean squares
add, so the total mean square is proportional to the bandwidth $B$ and the r.m.s. voltage
goes as $\sqrt{B}$. Quote the noise as volts per root hertz and you can get the answer by
multiplying:

$$v_{rms} = e_n\sqrt{B}$$

```python
import math

k, T = 1.380649e-23, 300.0
for r in (1e3, 1e5, 1e6):
    print("%9.0f ohm at 300 K: %8.3f nV/rtHz" % (r, math.sqrt(4 * k * T * r) * 1e9))
for bw in (1e6, 1e3, 10.0):
    print("  10 nV/rtHz over %9.0f Hz = %8.3f uV rms" % (bw, 10e-9 * math.sqrt(bw) * 1e6))
print("  narrowing 1 MHz to 10 Hz is worth a factor of %.1f" % math.sqrt(1e6 / 10))
```

```text
     1000 ohm at 300 K:    4.070 nV/rtHz
   100000 ohm at 300 K:   40.704 nV/rtHz
  1000000 ohm at 300 K:  128.716 nV/rtHz
  10 nV/rtHz over   1000000 Hz =   10.000 uV rms
  10 nV/rtHz over      1000 Hz =    0.316 uV rms
  10 nV/rtHz over        10 Hz =    0.032 uV rms
  narrowing 1 MHz to 10 Hz is worth a factor of 316.2
```

The same amplifier, the same signal, a factor of 316 in noise, decided by nothing but how
much bandwidth you left open. And module 9 says what that costs: a narrower filter is a
longer time constant, so every one of those factors was paid for in waiting.

**Second, why averaging works.** The mean of $N$ readings is $\frac{1}{N}\sum x_i$. If
the readings are independent, their mean squares add, so the variance of the sum is
$N\sigma^2$ and the variance of the mean is $N\sigma^2/N^2 = \sigma^2/N$. The standard
error is therefore

$$\frac{\sigma}{\sqrt{N}}$$

Ten times better costs a hundred times as many readings.

**Third, why averaging does not work on a systematic error** — and this is the same
identity with the opposite assumption. A fixed offset is perfectly correlated with
itself: $\langle v_1 v_2\rangle = \langle v^2\rangle$ rather than zero. Adding $N$ copies
of the same offset and dividing by $N$ returns the offset, exactly, however large $N$ is.
The $\sqrt{N}$ result was never a statement about errors in general; it was a statement
about the cross term vanishing, and for a loading error, a calibration offset or a
self-heated sensor it does not vanish.

## Where averaging stops helping even on random noise

The $\sqrt{N}$ result also assumes the noise density is flat over the band being
averaged. Below a device's flicker corner it is not: the density rises as $1/\sqrt{f}$,
because the *power* goes as $1/f$. Averaging for longer reaches down to lower
frequencies, and down there the noise is larger, so the improvement flattens out and
stops. This module's sandbox, **Where the floor stops falling**, is that curve on two
sliders: put the corner at 1 Hz and the trace is flat from 10 Hz up, which is a
chopper-stabilised amplifier and is why one is worth buying for a bridge measurement
that takes seconds; put the corner at 100 kHz and five of the seven decades on the axis
are sloped, and a slow average is working in the region where it does not pay.

## Turning all of it into one reported number

A measurement result is a value, an uncertainty, and a statement of where the
uncertainty came from. The contributions come in two kinds and neither is better than
the other.

A **Type A** uncertainty is evaluated statistically from repeated readings: take $n$ of
them, compute the sample standard deviation $s$ with the $n-1$ divisor, and the standard
uncertainty of the mean is $s/\sqrt{n}$ — the result derived above.

A **Type B** uncertainty comes from anywhere else: a data sheet, a calibration
certificate, a tolerance band. Module 1's specification is one of these. It arrives as a
*limit* $\pm a$ rather than as a standard deviation, so it has to be converted, and the
conversion needs an assumption about the shape. With nothing else stated, assume the
value is equally likely anywhere in the band — a rectangular distribution — and compute
its variance directly:

$$\frac{1}{2a}\int_{-a}^{a} x^{2}\,dx = \frac{a^{2}}{3}
\qquad\Rightarrow\qquad
u = \frac{a}{\sqrt{3}} = 0.577\,a$$

That is where the $\sqrt{3}$ comes from, and it is worth having derived once rather than
remembered, because it makes plain that it is an assumption of ignorance and not a law.

Each input then has to be converted into the units of the answer by its **sensitivity
coefficient** $\partial y/\partial x_i$ — how much the result moves when that input
moves — and the converted contributions combine the way mean squares always do:

$$u_c = \sqrt{\sum_i \left(\frac{\partial y}{\partial x_i}\right)^{2} u_i^{2}}$$

Finally, multiply by a coverage factor, conventionally $k = 2$ for about 95%, and quote
the expanded uncertainty to two significant figures with the value rounded to the same
decimal place. State $k$. A bare ± means nothing at all.

## The whole thing on one measurement

Here is the budget this course ends with: a Pt1000 in a bridge, twelve readings of its
output on a bench meter, and the temperature that comes out. Each line has already been
converted into kelvin by its sensitivity coefficient.

```python
import math

contributions = [
    ("twelve readings, Type A", 5.291301263200489e-05),
    ("excitation, Type B", 0.0005784739432217952),
    ("completion resistors, Type B", 0.15053847137212684),
    ("sensor nominal value, Type B", 0.09032308282327609),
]
u_c = math.sqrt(sum(u * u for _, u in contributions))
for name, u in contributions:
    print("  %-30s %10.6f K   %5.1f %% of the variance"
          % (name, u, 100.0 * u * u / (u_c * u_c)))
print("  %-30s %10.6f K" % ("combined standard uncertainty", u_c))
print("  reported: 1.00 C +/- %.2f C (k = 2)" % (2.0 * u_c))
```

```text
  twelve readings, Type A          0.000053 K     0.0 % of the variance
  excitation, Type B               0.000578 K     0.0 % of the variance
  completion resistors, Type B     0.150538 K    73.5 % of the variance
  sensor nominal value, Type B     0.090323 K    26.5 % of the variance
  combined standard uncertainty    0.175557 K
  reported: 1.00 C +/- 0.35 C (k = 2)
```

Read the variance column and the whole point of building a budget arrives. Two ordinary
resistor tolerances account for every part of the result that matters. The twelve
readings — the only part of this that involved standing at a bench — contribute 0.000053
K, which is one two-thousand-eight-hundredth of the leading term and rounds to nothing.
Quadrature is brutal to small contributions, exactly as it was in module 1's traceability
chain: a term three times below the leader adds 5% to the total and one sixteen times
below adds nothing you could write down.

And look at what is reported. The chain computes 1.0000211828 °C; the budget says the
last five of those digits are noise and the sixth is guesswork. The published line is
**1.00 °C ± 0.35 °C (k = 2)**, which is two digits of measurement out of eleven the
software was happy to print.

## The mistake, and why it is tempting

The mistake is improving the term you can see. Taking more readings is the one thing at
a bench that is entirely under your control, it costs only time, and the scatter is the
only error that is *visible* — it is right there on the display, moving. Every other line
in that budget came from a data sheet and cannot be attacked by working harder. So the
afternoon goes into driving a contribution of 0.000053 K down to 0.000017 K, and the
answer does not move, because it was never being limited by that. Build the budget
first; then you know which single component to change, and here it is a pair of 1%
resistors that cost pennies.

The second mistake is the bare ±. "1.00 ± 0.35 °C" with no $k$ could be a standard
uncertainty, an expanded one at $k = 2$, a manufacturer's limit, or half the spread of
three readings, and those differ from one another by a factor of four. A number without
a stated coverage factor is not a result; it is a rumour about one. The same goes for
digits: module 1's distinction between resolution and accuracy is the reason eleven
printed digits became two.

## Where this stops holding

Quadrature assumes independence, and the assumption is often quietly false. Two bridge
completion resistors from the same reel, at the same temperature, on the same board are
correlated; two readings taken from the same meter share its calibration entirely. When
inputs are correlated the cross term is real and the GUM's covariance terms are needed —
and the error runs both ways, because correlated contributions can also *cancel*, which
is exactly what a ratiometric measurement is engineered to make happen.

$s/\sqrt{n}$ assumes the readings are independent, and readings taken faster than the
instrument settles are not. Module 9 is the reason: sample a chain with a one-second
time constant ten times a second and consecutive readings share most of their content,
so the effective $n$ is far below the count and the Type A uncertainty comes out
optimistically small. Nothing in the arithmetic detects this; only knowing the settling
time does.

$k = 2$ gives about 95% coverage when the combined distribution is roughly normal, which
needs several contributions of comparable size. In the budget above one rectangular term
supplies three quarters of the variance, and the true coverage of $k = 2$ there is a
little different from 95%; the GUM's Welch–Satterthwaite formula exists for that case.

The rectangular assumption is itself a choice. If a manufacturer's ± limit is really a
99% statistical bound rather than a hard one, dividing by $\sqrt3$ overstates the
uncertainty; if the specification is a guarantee with no distribution behind it,
$a/\sqrt3$ is the conventional and defensible reading.

And none of this covers blunders. A wrong range, a lead left in the current jack, a
transposed digit in a notebook — an uncertainty budget describes a measurement that went
as intended, and says nothing about one that did not. That is what a second measurement
by a different route is for.

## What this module asks you to do

**Noise floors, averaging and an uncertainty budget** is every relation on this page as
seven small functions: the thermal density, the density-to-r.m.s. conversion, the number
of averages needed for a target, the Type A standard error, the Type B rectangular
conversion, the quadrature combination, and the rounding that turns a float into a
publishable line. The last one is fussier than it looks and it is the one that decides
whether your notebook says 1.0000211828 °C or 1.00 °C.
''',
            },
            "sandbox": {
                "title": "Where the floor stops falling",
                "visualiser": "noise-corner",
                "minutes": 9,
                "initial": {"fc": 1000, "nth": 10},
                "brief": r'''
This is the noise density of an amplifier input, in decibels relative to 1 nV/√Hz,
against frequency from 1 Hz to 10 MHz on a logarithmic axis. The curve is
$e_n = e_{th}\sqrt{1 + f_c/f}$: a flat thermal floor with a $1/f$ tail rising out of it
at low frequency.

Two markers are drawn for you. The faint dashed horizontal line is the thermal floor
itself, and the purple dashed vertical line is the corner frequency $f_c$ where the
two mechanisms contribute equally.

The vertical axis rescales itself as you move the sliders, so read the *numbers* on it
rather than the height of the trace.
''',
                "notice": [
                    "At the opening values — a floor of 10 nV/√Hz and a corner at 1 kHz — the dashed floor sits at 20 dB, because 20 dB re 1 nV/√Hz is 10 nV/√Hz. Where the purple line crosses the trace, the trace is 23 dB: exactly 3 dB above the floor, since at $f = f_c$ the formula gives $e_{th}\\sqrt{2}$.",
                    "Below the corner the trace falls at **10 dB per decade**, not 20: read 50 dB at 1 Hz, 40 dB at 10 Hz, 30.4 dB at 100 Hz. The noise *power* goes as $1/f$, so the density, which is a voltage, goes as $1/\\sqrt{f}$.",
                    "Push the thermal floor slider up to 40 nV/√Hz and the drawn curve does not change shape at all — only the axis labels move, by $20\\log_{10}4 = 12$ dB. The floor and the corner are independent: one is set by resistance and temperature, the other by the device's flicker mechanism.",
                    "Drag the corner slider all the way left, to 1 Hz. The purple line lands on the left-hand axis and the trace is within half a decibel of flat from 10 Hz upwards; that is what a chopper-stabilised amplifier looks like, and it is why one is worth having for a bridge measurement that takes seconds.",
                    "Now drag the corner all the way right, to 100 kHz. The $1/f$ region now covers five of the seven decades on the axis, and only the top two are flat. Averaging a slow measurement helps in the flat region and stops helping in the sloped one, so this is the picture that decides whether averaging is worth the time.",
                ],
            },
            "quiz": {
                "title": "Floors, averages and honest numbers",
                "minutes": 10,
                "questions": [
                    {
                        "q": "An amplifier with a 10 nV/√Hz input noise density is used over a 1 MHz bandwidth. What is the r.m.s. noise at its input?",
                        "opts": ["10 µV", "10 mV", "1 µV", "3.2 nV"],
                        "a": 0,
                        "why": r'''
$10\,\text{nV}/\sqrt{\text{Hz}} \times \sqrt{10^6\,\text{Hz}} = 10\,\text{nV} \times 1000
= 10$ µV. The root hertz in the unit is the whole instruction: multiply by the square
root of the bandwidth, never by the bandwidth. Answering 10 mV is multiplying by
$10^6$ instead of $10^3$, and it is worth doing the unit arithmetic explicitly once —
$\text{V}/\sqrt{\text{Hz}} \times \sqrt{\text{Hz}} = \text{V}$ — to see why.
''',
                    },
                    {
                        "q": "Your reading has a random uncertainty of 1 mV and you need 0.1 mV. How many readings must you average, assuming they are independent?",
                        "opts": ["10", "32", "100", "1000"],
                        "a": 2,
                        "why": r'''
Averaging improves the random part by $\sqrt{N}$, so a factor of ten needs $N = 100$.
The cost is brutal and worth internalising: the next factor of ten costs 10 000
readings. Answering 10 is applying the improvement linearly, which is the mistake that
makes people think a slow measurement can be made arbitrarily good by waiting. If the
noise is flicker rather than white, even the $\sqrt{N}$ is optimistic.
''',
                    },
                    {
                        "q": "A data sheet says the reference is accurate to ±2 mV, with no other information. What standard uncertainty do you enter in the budget?",
                        "opts": ["2 mV", "1 mV", "1.15 mV", "0.67 mV"],
                        "a": 2,
                        "why": r'''
A stated limit with no distribution named is treated as rectangular: every value in the
band is equally likely, and the standard deviation of a rectangular distribution of
half-width $a$ is $a/\sqrt{3} = 2/1.732 = 1.15$ mV. Entering the 2 mV itself
double-counts, because a limit is not a standard deviation; entering 1 mV is the
half-width halved, which corresponds to no distribution at all. This is the single
most-used conversion in an uncertainty budget.
''',
                    },
                    {
                        "q": "Two independent contributions to a result are 0.3 °C and 0.4 °C. What is the combined standard uncertainty?",
                        "opts": ["0.7 °C", "0.5 °C", "0.35 °C", "0.1 °C"],
                        "a": 1,
                        "why": r'''
Independent uncertainties add in quadrature: $\sqrt{0.3^2 + 0.4^2} = 0.5$ °C. Adding
them arithmetically to 0.7 °C assumes the two always err in the same direction, which
is a worst case rather than an uncertainty. Notice how little the smaller one matters:
had it been 0.1 °C the total would have been 0.41 °C. Chasing the second-largest term
in a budget is nearly always wasted effort.
''',
                    },
                    {
                        "q": "A result is 24.318 °C with a combined standard uncertainty of 0.176 °C. How should it be reported at $k = 2$?",
                        "opts": [
                            "24.318 °C ± 0.176 °C",
                            "24.3 °C ± 0.2 °C",
                            "24.32 °C ± 0.35 °C (k = 2)",
                            "24.318 °C ± 0.352 °C (k = 2)",
                        ],
                        "a": 2,
                        "why": r'''
Expand first: $U = 2 \times 0.176 = 0.352$ °C, quoted to two significant figures as
0.35 °C, with the value rounded to the same decimal place — 24.32 °C — and $k$ stated.
Quoting 24.318 ± 0.352 keeps three digits the uncertainty says are meaningless; quoting
24.318 ± 0.176 reports a *standard* uncertainty as though it were an interval and omits
$k$ entirely, so the reader cannot tell whether it covers 68% or 95%; and 24.3 ± 0.2 has
thrown away a figure the measurement had earned.
''',
                    },
                    {
                        "q": "You replace a 6½-digit meter with an 8½-digit one to measure a bridge output whose dominant error is the 0.1% tolerance of the completion resistors. What improves?",
                        "opts": [
                            "the accuracy, by two orders of magnitude",
                            "only the speed of the measurement",
                            "the random part, by a factor of 100, and the total by the same",
                            "nothing that matters — the resistors still dominate the budget",
                        ],
                        "a": 3,
                        "why": r'''
Nothing that matters. A budget is a sum in quadrature, and a term that is already
negligible cannot become more negligible: if the resistors contribute 0.1% and the
meter 0.0001%, removing the meter term entirely changes the total in the fifth decimal
place. The money belongs on the resistors — or on a configuration that cancels them.
Reading a budget before buying equipment is the practical use of module 10, and the
capstone is built around exactly this comparison.
''',
                    },
                ],
            },
            "lab": {
                "title": "Noise floors, averaging and an uncertainty budget",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Seven small functions covering the arithmetic of module 10.

- `johnson_density(r, t)` — thermal noise density $\sqrt{4kTR}$ in volts per root
  hertz. `BOLTZMANN` is defined for you.
- `rms_noise(density, bw)` — total r.m.s. noise of a white density over a bandwidth.
- `averages_needed(single, target)` — how many independent readings must be averaged
  to bring a random uncertainty of `single` down to `target`. Return a whole number,
  rounded **up**: 99.2 readings is not a thing.
- `type_a(values)` — the standard uncertainty of the mean of repeated readings, which
  is the sample standard deviation (the $n-1$ one) divided by $\sqrt{n}$.
- `type_b_rect(halfwidth)` — the standard uncertainty of a stated limit, $a/\sqrt{3}$.
- `combined(us)` — independent contributions in quadrature.
- `round_report(value, u)` — return `(value, u)` rounded for publication: `u` to two
  significant figures, and `value` to that same decimal place. Find the decimal place
  with `math.floor(math.log10(abs(u)))`; if that exponent is $e$, you are keeping
  $1-e$ decimals.

Use `math.ceil` for the rounding up, and Python's built-in `round` for the last one.
''',
                "files": [{"name": "main.py", "content": r'''
"""Noise floors, averaging, and the arithmetic of an uncertainty budget."""

import math

BOLTZMANN = 1.380649e-23  # J/K, exact by definition since 2019


def johnson_density(r, t):
    """Thermal noise density of a resistance r at temperature t, in V/sqrt(Hz)."""
    # TODO: the square root of 4 k T R.
    return 0.0


def rms_noise(density, bw):
    """Total r.m.s. noise of a white density over a bandwidth, in volts."""
    # TODO: density times the square root of the bandwidth.
    return 0.0


def averages_needed(single, target):
    """Readings to average to bring a random uncertainty down to target."""
    # TODO: averaging improves as the square root of the count. Round up.
    return 0


def type_a(values):
    """Standard uncertainty of the mean of these repeated readings."""
    # TODO: sample standard deviation over the square root of the count.
    return 0.0


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit of plus or minus halfwidth."""
    # TODO: a rectangular distribution has standard deviation a / sqrt(3).
    return 0.0


def combined(us):
    """Combined standard uncertainty of independent contributions."""
    # TODO: in quadrature.
    return 0.0


def round_report(value, u):
    """(value, u) rounded for publication: u to two significant figures."""
    # TODO: find the decimal place from the exponent of u, then round both.
    return (0.0, 0.0)


if __name__ == "__main__":
    print("1 k at 300 K:", johnson_density(1000.0, 300.0), "V/sqrt(Hz)")
    print("over 1 MHz that is:", rms_noise(johnson_density(1000.0, 300.0), 1e6), "V")
    print("1 mV down to 0.1 mV needs", averages_needed(1e-3, 1e-4), "readings")
    xs = [9.9012, 9.9008, 9.9015, 9.9006, 9.9011, 9.9009]
    ua = type_a(xs)
    ub = type_b_rect(0.0030)
    uc = combined([ua, ub])
    print("type A:", ua, " type B:", ub, " combined:", uc)
    print("reported:", round_report(sum(xs) / len(xs), 2 * uc))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Noise floors, averaging, and the arithmetic of an uncertainty budget."""

import math

BOLTZMANN = 1.380649e-23  # J/K, exact by definition since 2019


def johnson_density(r, t):
    """Thermal noise density of a resistance r at temperature t, in V/sqrt(Hz)."""
    return math.sqrt(4.0 * BOLTZMANN * t * r)


def rms_noise(density, bw):
    """Total r.m.s. noise of a white density over a bandwidth, in volts."""
    return density * math.sqrt(bw)


def averages_needed(single, target):
    """Readings to average to bring a random uncertainty down to target."""
    return math.ceil((single / target) ** 2)


def type_a(values):
    """Standard uncertainty of the mean of these repeated readings."""
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(var) / math.sqrt(n)


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit of plus or minus halfwidth."""
    return halfwidth / math.sqrt(3.0)


def combined(us):
    """Combined standard uncertainty of independent contributions."""
    return math.sqrt(sum(u * u for u in us))


def round_report(value, u):
    """(value, u) rounded for publication: u to two significant figures."""
    places = 1 - math.floor(math.log10(abs(u)))
    return (round(value, places), round(u, places))


if __name__ == "__main__":
    print("1 k at 300 K:", johnson_density(1000.0, 300.0), "V/sqrt(Hz)")
    print("over 1 MHz that is:", rms_noise(johnson_density(1000.0, 300.0), 1e6), "V")
    print("1 mV down to 0.1 mV needs", averages_needed(1e-3, 1e-4), "readings")
    xs = [9.9012, 9.9008, 9.9015, 9.9006, 9.9011, 9.9009]
    ua = type_a(xs)
    ub = type_b_rect(0.0030)
    uc = combined([ua, ub])
    print("type A:", ua, " type B:", ub, " combined:", uc)
    print("reported:", round_report(sum(xs) / len(xs), 2 * uc))
'''}],
                "hints": [
                    "`johnson_density` is `math.sqrt(4.0 * BOLTZMANN * t * r)`. A 1 kΩ resistor at 300 K comes to 4.07 nV/√Hz; if you get a number near $10^{-17}$ you have forgotten the square root.",
                    "`averages_needed` is `math.ceil((single / target) ** 2)` — square the ratio, because the improvement goes as the square root of the count.",
                    "`type_a` needs the $n-1$ divisor for the variance and then a further division by $\\sqrt{n}$ for the standard error of the mean. Two square roots, or one on the whole quotient.",
                    "For `round_report`, `math.floor(math.log10(0.0035))` is −3, so you keep $1-(-3) = 4$ decimals: `round(u, 4)` gives 0.0035 and the value is rounded to four decimals as well.",
                ],
                "tests": [
                    {"name": "thermal noise of a resistor", "code": r'''
d = johnson_density(1000.0, 300.0)
assert abs(d - 4.070354775692163e-09) < 1e-20, \
    f"1 k at 300 K is 4.0704 nV/rtHz, got {d}"
big = johnson_density(1e6, 300.0)
assert abs(big - 1.2871591976131003e-07) < 1e-18, \
    f"1 M at 300 K is 128.7 nV/rtHz, got {big}"
assert abs(big / d - math.sqrt(1000.0)) < 1e-9, \
    "a thousand times the resistance is only sqrt(1000) times the noise"
'''},
                    {"name": "density becomes volts through a bandwidth", "code": r'''
v = rms_noise(10e-9, 1e6)
assert abs(v - 1e-5) < 1e-18, f"10 nV/rtHz over 1 MHz is 10 uV, got {v}"
wide = rms_noise(10e-9, 20e6)
assert abs(wide - 4.4721359549995795e-05) < 1e-16, \
    f"the same density over 20 MHz is 44.7 uV, got {wide}"
assert abs(wide / v - math.sqrt(20.0)) < 1e-9, \
    "twenty times the bandwidth is sqrt(20) times the noise, not twenty times"
'''},
                    {"name": "averaging is expensive", "code": r'''
n = averages_needed(1e-3, 1e-4)
assert n == 100, f"a factor of ten costs a hundred readings, got {n}"
assert averages_needed(2.5e-3, 5e-4) == 25, "a factor of five costs twenty-five"
assert averages_needed(1e-3, 9.9e-5) == 103, \
    "a non-integer answer must round up, not down or to nearest"
assert isinstance(averages_needed(1e-3, 1e-4), int), "return a whole number of readings"
'''},
                    {"name": "Type A from repeats, Type B from a limit", "code": r'''
xs = [9.9012, 9.9008, 9.9015, 9.9006, 9.9011, 9.9009]
ua = type_a(xs)
assert abs(ua - 0.00013017082793169405) < 1e-15, \
    f"the standard uncertainty of that mean is 0.13 mV, got {ua}"
ub = type_b_rect(0.0030)
assert abs(ub - 0.0017320508075688774) < 1e-15, \
    f"a +/- 3 mV limit is a 1.73 mV standard uncertainty, got {ub}"
assert ub > ua, "the data sheet limit dominates these repeats, which is the usual case"
'''},
                    {"name": "contributions combine in quadrature", "code": r'''
c = combined([0.3, 0.4])
assert abs(c - 0.5) < 1e-12, f"0.3 and 0.4 combine to 0.5, not 0.7, got {c}"
one = combined([0.42])
assert abs(one - 0.42) < 1e-15, "a single contribution combines to itself"
lopsided = combined([0.4, 0.04])
assert abs(lopsided - 0.4019950248448356) < 1e-12, \
    "a contribution ten times smaller adds half a per cent, which is why budgets are read top-down"
'''},
                    {"name": "the reported number keeps only the digits it has", "code": r'''
v, u = round_report(9.901016666666667, 0.0034738707197847322)
assert abs(u - 0.0035) < 1e-12, f"the uncertainty rounds to two figures, 0.0035, got {u}"
assert abs(v - 9.901) < 1e-12, f"the value follows to the same decimal place, got {v}"
v2, u2 = round_report(1234.5678, 2.13)
assert abs(u2 - 2.1) < 1e-12 and abs(v2 - 1234.6) < 1e-12, \
    f"1234.5678 +/- 2.13 reports as 1234.6 +/- 2.1, got {(v2, u2)}"
v3, u3 = round_report(0.0512345, 0.00123)
assert abs(u3 - 0.0012) < 1e-15 and abs(v3 - 0.0512) < 1e-15, \
    f"0.0512345 +/- 0.00123 reports as 0.0512 +/- 0.0012, got {(v3, u3)}"
'''},
                ],
            },
        },
    ],

    "capstone": {
        "title": "One temperature, reported honestly",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
A platinum resistance thermometer sits in one arm of a bridge on the bench next door.
The run has already been done, and `bench.py` holds everything that was written down:

- twelve readings of the bridge output, taken with a digital multimeter,
- the excitation, 2.000 V, from a supply specified to ±2 mV,
- the three completion resistors, nominally 1000 Ω, from a 0.1% batch,
- the sensor's nominal resistance at 0 °C, 1000 Ω, from a class A Pt1000 specified
  to ±0.6 Ω at that point,
- the bridge's Thévenin output resistance, 1000 Ω, and the multimeter's input
  resistance, 10 MΩ.

Your job is to turn that into one line of a report: a temperature, an expanded
uncertainty, and a coverage factor. Along the way you have to decide which of the four
input quantities actually matters, which is the question the whole course has been
building towards.

## The measurement chain

Four steps, each a function you write.

1. **Undo the loading.** The multimeter's 10 MΩ sits across a bridge whose Thévenin
   resistance is 1 kΩ, so every reading is low by $R_{th}/(R_{th}+R_{in})$. The
   correction is $V = V_{meas}(1 + R_{th}/R_{in})$.
2. **Invert the bridge.** From $V_o = V_{ex}x/(4+2x)$, recover
   $x = 4V_o/(V_{ex}-2V_o)$ and hence the sensor's resistance $R_s = R_c(1+x)$, where
   $R_c$ is the completion resistance the sensor is compared against.
3. **Convert to temperature.** Take the sensor as linear over this range:
   $R_s = R_0(1 + \alpha T)$ with $\alpha = 3.85\times10^{-3}$ per kelvin, so
   $T = (R_s/R_0 - 1)/\alpha$.
4. **Propagate the uncertainties.** Each input $x_i$ has a standard uncertainty
   $u(x_i)$, and it contributes $|\partial T/\partial x_i|\,u(x_i)$ to the result.

## Sensitivity coefficients without calculus

You are not asked to differentiate the chain by hand. Evaluate each coefficient
numerically, by nudging one input and seeing how far the answer moves:

```text
c_i = (T(x_i + h) - T(x_i - h)) / (2h),  with h a millionth of x_i
```

That central difference is accurate to well under a part in a million on a function
this smooth, and it keeps working when you change the model — which is the real reason
professional budgets are computed this way rather than symbolically.

## What the answer is for

When your budget prints, one term will be a hundred times larger than another. Write
one sentence in the module docstring of `main.py` naming the dominant term and saying
what you would change to improve the result — and, just as usefully, what you would
*not* bother changing. The last deliverable is that sentence; it is the difference
between operating an instrument and understanding one.
''',
        "deliverables": [
            "`corrected_output`, undoing the multimeter's loading of the bridge output, in the correct direction: the corrected value must be larger than the reading.",
            "`sensor_resistance`, inverting the exact quarter-bridge relation — not the linear approximation — to recover the sensor's resistance from the corrected output.",
            "`temperature`, converting a sensor resistance to a temperature through the linear platinum model.",
            "`budget`, returning one contribution in kelvin for each named input, each evaluated as a numerical sensitivity coefficient times that input's standard uncertainty.",
            "`combine` and `report`, giving the combined standard uncertainty and the final published string, with the uncertainty at two significant figures, the value at the same decimal place, the coverage factor stated, and the unit the chain actually produced — the result is a Celsius temperature, not a kelvin one.",
            "One sentence in the module docstring of `main.py` naming the dominant contribution and saying what would and would not be worth improving.",
        ],
        "constraints": [
            "The standard library only. `math` is all this needs; NumPy is permitted by the course but buys nothing here.",
            "Do not edit `bench.py`. It is the record of what was measured, and editing your data to fit your analysis is the one unforgivable sin in this subject.",
            "`budget` must work for any subset of the four inputs, and must key its result by the same names it was given, so that a budget can be re-run with one term switched off.",
            "Sensitivity coefficients are to be evaluated numerically from your own chain, not hard-coded. A budget that stops agreeing with the model when the model changes is worse than no budget.",
            "`report` states the coverage factor. A value with a ± and no $k$ is not a result.",
        ],
        "rubric": [
            {"criterion": "Measurement chain", "weight": 30,
             "evidence": "corrected_output, sensor_resistance and temperature compose into a temperature that reproduces the reference value from the bench data to nine figures, with the loading correction applied in the direction that makes the reading larger rather than smaller."},
            {"criterion": "Uncertainty budget", "weight": 30,
             "evidence": "budget returns one contribution per named input, each equal to a numerically evaluated sensitivity coefficient times that input's standard uncertainty, and agrees with independently computed values on the bench case and on a second case with different numbers."},
            {"criterion": "Combination and reporting", "weight": 20,
             "evidence": "combine gives the quadrature sum, and report rounds the expanded uncertainty to two significant figures with the value at the same decimal place and the coverage factor stated, including the awkward case where the uncertainty is larger than one."},
            {"criterion": "Interpretation", "weight": 20,
             "evidence": "The docstring sentence names the completion and sensor resistors as the dominant terms, and identifies the multimeter and the averaging as the places where further effort would be wasted."},
        ],
        "hints": [
            "Write `temperature_from(v_out, vex, rc, r0)` as a single function composing steps 2 and 3. `budget` then needs to perturb only that one function, which is what makes the numerical derivative easy.",
            "For the perturbation size, `h = abs(x) * 1e-6` works for every input here. Guard against a zero input with a small floor, or a budget entry for a quantity that happens to be zero will divide by nothing.",
            "Build the perturbed argument lists with `dict(args)` copies and keyword expansion — `temperature_from(**hi)` — rather than four `if` branches. The result is shorter and does not have to be rewritten when the model gains a fifth input.",
            "The completion resistance is what the sensor is measured against: the chain returns $R_s = R_c(1+x)$, so a 1 Ω error in it is very nearly a 1 Ω error in the sensor. Its sensitivity coefficient comes out near 0.26 K per ohm, so 0.577 Ω of standard uncertainty is 0.15 K — and $R_0$ has a coefficient of the same size and the opposite sign.",
            "For `report`, the number of decimals is `max(0, 1 - math.floor(math.log10(abs(u))))`, and `\"%.*f\" % (places, value)` takes the count as an argument. The clamp at zero matters: an uncertainty of 21 would otherwise ask for minus one decimal place and raise.",
            "Pass the unit you are actually reporting. The chain returns degrees Celsius, and 1.00 °C is not 1.00 K — the interval is 0.35 kelvin wide either way, but the value is not a thermodynamic temperature and must not be labelled as one.",
        ],
        "files": [
            {"name": "bench.py", "ro": True, "content": r'''
"""The record of one bench run. Do not edit.

Twelve readings of a Pt1000 quarter bridge, taken with a 6.5-digit multimeter on its
100 mV range, plus every specification that was copied off the instruments and the
component reels at the time. Nothing here is a measurement you can repeat; it is what
the notebook says, which is all any analysis ever has.
"""

# bridge output readings, volts
RAW = [
    0.00192055, 0.00192172, 0.00192096, 0.00192140,
    0.00192118, 0.00192083, 0.00192155, 0.00192101,
    0.00192129, 0.00192074, 0.00192147, 0.00192110,
]

EXCITATION = 2.000        # V, bridge excitation
COMPLETION = 1000.0       # ohm, the three fixed arms
NOMINAL = 1000.0          # ohm, sensor resistance at 0 C
BRIDGE_RTH = 1000.0       # ohm, Thevenin resistance at the bridge output
DMM_RIN = 10.0e6          # ohm, multimeter input resistance

# stated limits, half-widths, all rectangular
U_EXCITATION_HALFWIDTH = 2.0e-3   # V, supply specification
U_COMPLETION_HALFWIDTH = 1.0      # ohm, 0.1% of 1000
U_NOMINAL_HALFWIDTH = 0.6         # ohm, class A Pt1000 at 0 C
'''},
            {"name": "main.py", "content": r'''
"""A Pt1000 bridge measurement, from twelve readings to one reported temperature.

TODO: one sentence naming the dominant contribution to the uncertainty, and saying
what you would change to improve the result and what you would not bother changing.
"""

import math

from bench import (RAW, EXCITATION, COMPLETION, NOMINAL, BRIDGE_RTH, DMM_RIN,
                   U_EXCITATION_HALFWIDTH, U_COMPLETION_HALFWIDTH,
                   U_NOMINAL_HALFWIDTH)

ALPHA = 3.85e-3  # per kelvin, platinum


def corrected_output(v_meas, r_th, r_in):
    """The bridge output before the multimeter loaded it, in volts."""
    # TODO: multiply by (1 + r_th / r_in).
    return 0.0


def sensor_resistance(v_out, vex, rc):
    """Sensor resistance, from an exact inversion of the quarter bridge."""
    # TODO: recover x = 4 Vo / (Vex - 2 Vo), then return rc * (1 + x).
    return 0.0


def temperature(rs, r0):
    """Temperature in degrees Celsius from a platinum sensor resistance."""
    # TODO: invert rs = r0 (1 + ALPHA T).
    return 0.0


def temperature_from(v_out, vex, rc, r0):
    """The whole chain, as one function of four inputs."""
    # TODO: compose sensor_resistance and temperature.
    return 0.0


def type_a(values):
    """Standard uncertainty of the mean of repeated readings."""
    # TODO: sample standard deviation over the square root of the count.
    return 0.0


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit."""
    # TODO: a rectangular distribution has standard deviation a / sqrt(3).
    return 0.0


def budget(v_out, vex, rc, r0, u):
    """Contribution of each named input to the temperature, in kelvin.

    `u` maps input names -- any of "v_out", "vex", "rc", "r0" -- to their standard
    uncertainties. The result has the same keys.
    """
    # TODO: for each named input, a central difference for the sensitivity
    # coefficient, times that input's standard uncertainty, in magnitude.
    return {}


def combine(us):
    """Combined standard uncertainty of independent contributions."""
    # TODO: in quadrature.
    return 0.0


def report(value, u, k, unit):
    """The published string: value, expanded uncertainty, coverage factor."""
    # TODO: two significant figures on u, the value to the same decimal place.
    return ""


if __name__ == "__main__":
    v_mean = sum(RAW) / len(RAW)
    v_true = corrected_output(v_mean, BRIDGE_RTH, DMM_RIN)
    rs = sensor_resistance(v_true, EXCITATION, COMPLETION)
    t = temperature(rs, NOMINAL)
    print("mean reading      ", v_mean, "V")
    print("loading corrected ", v_true, "V")
    print("sensor resistance ", rs, "ohm")
    print("temperature       ", t, "C")

    u = {
        "v_out": type_a(RAW),
        "vex": type_b_rect(U_EXCITATION_HALFWIDTH),
        "rc": type_b_rect(U_COMPLETION_HALFWIDTH),
        "r0": type_b_rect(U_NOMINAL_HALFWIDTH),
    }
    b = budget(v_true, EXCITATION, COMPLETION, NOMINAL, u)
    print("budget, kelvin:")
    for name in sorted(b):
        print("   %-6s %s" % (name, b[name]))
    uc = combine(list(b.values()))
    print("combined standard uncertainty", uc, "K")
    print("reported:", report(t, 2.0 * uc, 2, "°C"))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A Pt1000 bridge measurement, from twelve readings to one reported temperature.

The completion resistors dominate: their 0.1% tolerance contributes 0.151 K of the
0.176 K combined standard uncertainty, with the sensor's own 0.6 ohm tolerance next at
0.090 K. Measuring the three completion resistors once against a calibrated standard,
and using the measured values, would remove most of the budget; buying a better
multimeter would not, because the twelve readings contribute 0.00005 K and averaging
more of them would be effort spent on the smallest term in the sum.
"""

import math

from bench import (RAW, EXCITATION, COMPLETION, NOMINAL, BRIDGE_RTH, DMM_RIN,
                   U_EXCITATION_HALFWIDTH, U_COMPLETION_HALFWIDTH,
                   U_NOMINAL_HALFWIDTH)

ALPHA = 3.85e-3  # per kelvin, platinum


def corrected_output(v_meas, r_th, r_in):
    """The bridge output before the multimeter loaded it, in volts."""
    return v_meas * (1.0 + r_th / r_in)


def sensor_resistance(v_out, vex, rc):
    """Sensor resistance, from an exact inversion of the quarter bridge."""
    x = 4.0 * v_out / (vex - 2.0 * v_out)
    return rc * (1.0 + x)


def temperature(rs, r0):
    """Temperature in degrees Celsius from a platinum sensor resistance."""
    return (rs / r0 - 1.0) / ALPHA


def temperature_from(v_out, vex, rc, r0):
    """The whole chain, as one function of four inputs."""
    return temperature(sensor_resistance(v_out, vex, rc), r0)


def type_a(values):
    """Standard uncertainty of the mean of repeated readings."""
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(var) / math.sqrt(n)


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit."""
    return halfwidth / math.sqrt(3.0)


def budget(v_out, vex, rc, r0, u):
    """Contribution of each named input to the temperature, in kelvin.

    `u` maps input names -- any of "v_out", "vex", "rc", "r0" -- to their standard
    uncertainties. The result has the same keys.
    """
    args = {"v_out": v_out, "vex": vex, "rc": rc, "r0": r0}
    out = {}
    for name, ux in u.items():
        h = abs(args[name]) * 1e-6
        if h == 0.0:
            h = 1e-12
        hi = dict(args)
        lo = dict(args)
        hi[name] = args[name] + h
        lo[name] = args[name] - h
        coeff = (temperature_from(**hi) - temperature_from(**lo)) / (2.0 * h)
        out[name] = abs(coeff * ux)
    return out


def combine(us):
    """Combined standard uncertainty of independent contributions."""
    return math.sqrt(sum(u * u for u in us))


def report(value, u, k, unit):
    """The published string: value, expanded uncertainty, coverage factor."""
    places = max(0, 1 - math.floor(math.log10(abs(u))))
    return "%.*f %s ± %.*f %s (k = %d)" % (places, value, unit,
                                                places, u, unit, k)


if __name__ == "__main__":
    v_mean = sum(RAW) / len(RAW)
    v_true = corrected_output(v_mean, BRIDGE_RTH, DMM_RIN)
    rs = sensor_resistance(v_true, EXCITATION, COMPLETION)
    t = temperature(rs, NOMINAL)
    print("mean reading      ", v_mean, "V")
    print("loading corrected ", v_true, "V")
    print("sensor resistance ", rs, "ohm")
    print("temperature       ", t, "C")

    u = {
        "v_out": type_a(RAW),
        "vex": type_b_rect(U_EXCITATION_HALFWIDTH),
        "rc": type_b_rect(U_COMPLETION_HALFWIDTH),
        "r0": type_b_rect(U_NOMINAL_HALFWIDTH),
    }
    b = budget(v_true, EXCITATION, COMPLETION, NOMINAL, u)
    print("budget, kelvin:")
    for name in sorted(b):
        print("   %-6s %s" % (name, b[name]))
    uc = combine(list(b.values()))
    print("combined standard uncertainty", uc, "K")
    print("reported:", report(t, 2.0 * uc, 2, "°C"))
'''},
        ],
        "tests": [
            {"name": "the loading correction goes the right way", "code": r'''
v = corrected_output(0.00192115, 1000.0, 10.0e6)
assert v > 0.00192115, "the true output is larger than the loaded reading, not smaller"
assert abs(v - 0.001921342115) < 1e-15, \
    f"0.00192115 V through a 1 k / 10 M divider was really 0.001921342115 V, got {v}"
hard = corrected_output(1.0, 1e6, 1e4)
assert abs(hard - 101.0) < 1e-12, \
    f"a 1 M source read on a 10 k input is out by a factor of 101, got {hard}"
'''},
            {"name": "the bridge inversion is exact, not linearised", "code": r'''
rs = sensor_resistance(0.001921342115, 2.000, 1000.0)
assert abs(rs - 1003.8500815538356) < 1e-9, \
    f"that output means a sensor of 1003.85008 ohm, got {rs}"
forward = 2.000 * (1003.8500815538356 / 1000.0 - 1.0) / (4.0 + 2.0 * 0.0038500815538356)
assert abs(forward - 0.001921342115) < 1e-15, \
    "the forward relation must reproduce the output your inversion consumed"
big = sensor_resistance(2.000 * 0.1 / (4.0 + 0.2), 2.000, 1000.0)
assert abs(big - 1100.0) < 1e-9, \
    f"a 10% change must invert exactly to 1100 ohm, got {big} (the linear formula gives 1105)"
'''},
            {"name": "resistance becomes temperature", "code": r'''
assert abs(temperature(1000.0, 1000.0)) < 1e-12, "1000 ohm is 0 C by definition"
t = temperature(1003.85, 1000.0)
assert abs(t - 1.0) < 1e-12, f"1003.85 ohm is 1.000 C for alpha = 3.85e-3, got {t}"
cold = temperature(961.5, 1000.0)
assert abs(cold - (-10.0)) < 1e-9, f"961.5 ohm is -10.00 C, got {cold}"
'''},
            {"name": "the whole chain on the bench data", "code": r'''
v_mean = sum(RAW) / len(RAW)
assert abs(v_mean - 0.00192115) < 1e-15, f"the mean of the twelve readings is 1.92115 mV, got {v_mean}"
t = temperature_from(corrected_output(v_mean, BRIDGE_RTH, DMM_RIN),
                     EXCITATION, COMPLETION, NOMINAL)
assert abs(t - 1.0000211828144399) < 1e-9, \
    f"the bench run comes to 1.0000212 C, got {t}"
raw_t = temperature_from(v_mean, EXCITATION, COMPLETION, NOMINAL)
assert raw_t < t, "skipping the loading correction reads low; that is what loading does"
assert abs(t - raw_t - 1.00184587e-4) < 1e-9, \
    f"the loading correction is worth 0.0001 K here, got {t - raw_t}"
'''},
            {"name": "every input gets its own line in the budget", "code": r'''
u = {"v_out": type_a(RAW),
     "vex": type_b_rect(U_EXCITATION_HALFWIDTH),
     "rc": type_b_rect(U_COMPLETION_HALFWIDTH),
     "r0": type_b_rect(U_NOMINAL_HALFWIDTH)}
assert abs(u["v_out"] - 1.0146651933250557e-07) < 1e-15, \
    f"the Type A uncertainty of those twelve readings is 0.101 uV, got {u['v_out']}"
assert abs(u["rc"] - 0.5773502691896258) < 1e-12, "a 1 ohm limit is a 0.577 ohm standard uncertainty"
v_true = corrected_output(sum(RAW) / len(RAW), BRIDGE_RTH, DMM_RIN)
b = budget(v_true, EXCITATION, COMPLETION, NOMINAL, u)
assert set(b) == set(u), f"the budget must be keyed by the inputs it was given, got {sorted(b)}"
assert abs(b["rc"] - 0.15053847137212684) < 1e-6, \
    f"the completion resistors contribute 0.1505 K, got {b['rc']}"
assert abs(b["r0"] - 0.09032308282327609) < 1e-6, \
    f"the sensor tolerance contributes 0.0903 K, got {b['r0']}"
assert abs(b["vex"] - 0.0005784739432217952) < 1e-8, \
    f"the excitation contributes 0.00058 K, got {b['vex']}"
assert abs(b["v_out"] - 5.291301263200489e-05) < 1e-9, \
    f"the twelve readings contribute 0.000053 K, got {b['v_out']}"
assert b["rc"] > 1000 * b["v_out"], "the resistors dominate the readings by three orders of magnitude"
'''},
            {"name": "a budget can be re-run with terms switched off", "code": r'''
v_true = corrected_output(sum(RAW) / len(RAW), BRIDGE_RTH, DMM_RIN)
only = budget(v_true, EXCITATION, COMPLETION, NOMINAL, {"rc": 0.5773502691896258})
assert set(only) == {"rc"}, f"only the named inputs get a line, got {sorted(only)}"
assert abs(only["rc"] - 0.15053847137212684) < 1e-6, \
    "a contribution must not depend on which other terms were asked for"
none = budget(v_true, EXCITATION, COMPLETION, NOMINAL, {})
assert none == {}, "an empty budget is empty, not an error"
'''},
            {"name": "combination and the published line", "code": r'''
c = combine([0.15053847137212684, 0.09032308282327609,
             0.0005784739432217952, 5.291301263200489e-05])
assert abs(c - 0.1755574780111828) < 1e-9, \
    f"those four combine to 0.17556 K, got {c}"
line = report(1.0000211828144399, 2.0 * 0.1755574780111828, 2, "°C")
assert line == "1.00 °C ± 0.35 °C (k = 2)", \
    f"the chain returns a Celsius temperature, and 1.00 °C is not 1.00 K; got {line!r}"
volts = report(9.901016666666667, 0.0034738707197847322, 2, "V")
assert volts == "9.9010 V ± 0.0035 V (k = 2)", f"got {volts!r}"
coarse = report(1234.5678, 21.3, 2, "V")
assert coarse == "1235 V ± 21 V (k = 2)", \
    f"an uncertainty above ten leaves no decimals at all, got {coarse!r}"
'''},
        ],
    },
}
