"""EE102 — Circuit Analysis II: Alternating Current.

A first-year course. It assumes school mathematics — trigonometry, a little
calculus notation, and nothing else — and it assumes EE101, which means Ohm's law
and a divider with steady voltages. Everything else is defined where it is used.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number here was produced by running the code, not assumed
"""

COURSE = {
    "id": "EE102",
    "title": "Circuit Analysis II — Alternating Current",
    "band": 1,
    "level": "Beginner",
    "prereqs": ["EE101"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 120,
    "icon": "◉",
    "summary": (
        "In EE101 the voltages stood still. Here they move: every source is a sinusoid, "
        "and the two components that ignored a steady voltage — the capacitor and the "
        "inductor — start to matter more than the resistors. The course builds the "
        "vocabulary first (peak, RMS, phase, angular frequency), then the one idea that "
        "makes alternating current no harder than direct current: impedance, a resistance "
        "that depends on frequency. By the end you can look at a resistor and a capacitor "
        "and say, without simulating anything, which frequencies get through."
    ),
    "outcomes": [
        "Describe a sinusoid by its amplitude, frequency, angular frequency and phase, and convert between peak and RMS.",
        "State the impedance of a resistor, a capacitor and an inductor, and use it in a divider exactly as you used resistance.",
        "Explain, in terms of reactance rather than slogans, why a capacitor blocks direct current and passes alternating current.",
        "Find the corner frequency of a first-order RC or RL circuit, and predict the response a decade either side of it.",
        "Measure a filter you did not build: sweep it, find its −3 dB point, and infer a component value from the measurement.",
    ],
    "assessment": "Four quizzes, three circuits drawn and measured in the schematic editor, three short Python labs, and a capstone that identifies three unknown filters from their responses alone.",
    "reading": [
        "*The Art of Electronics*, Horowitz & Hill — chapter 1, sections on capacitors and RC circuits.",
        "*Fundamentals of Electric Circuits*, Alexander & Sadiku — chapters 9 and 10 for phasors and impedance.",
        "Any oscilloscope manual, for the difference between the peak, peak-to-peak and RMS readings it offers.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Sinusoids, RMS and average power",
            "summary": "Before any circuit: how to describe a voltage that will not sit still, and how to say how big it is.",
            "concepts": [
                "A sinusoid is written $v(t) = V_p \\sin(2\\pi f t + \\phi)$. $V_p$ is the **amplitude** or peak value in volts, $f$ is the **frequency** in hertz (cycles per second), and $\\phi$ is the **phase** in radians.",
                "The **period** $T$ is the time for one complete cycle, in seconds, and $T = 1/f$. A 50 Hz wave has a period of 20 ms.",
                "**Angular frequency** $\\omega = 2\\pi f$ is the same fact in radians per second. It exists because $\\sin$ takes an angle, not a count of cycles. Almost every mistake in this course is a missing $2\\pi$.",
                "The **average** of a sinusoid over a whole cycle is exactly zero — the positive half cancels the negative half — so the average says nothing about how big the wave is.",
                "The **RMS** value is the root of the mean of the square: square the waveform, average that over a whole cycle, take the square root. For a sinusoid, and only for a sinusoid, $V_{rms} = V_p/\\sqrt{2} \\approx 0.707\\,V_p$.",
                "RMS is defined that way so that the average power in a resistor is $P = V_{rms}^2/R$, the same formula direct current uses. An RMS volt heats a resistor exactly as a steady volt does.",
            ],
            "sandbox": {
                "title": "One frequency, two ways of drawing it",
                "visualiser": "spectrum",
                "minutes": 8,
                "initial": {"fsig": 20, "fs": 200},
                "brief": r'''
The upper panel is a sinusoid against time, over a window of 100 ms. The lower panel
is the same wave against frequency: a single vertical line at the frequency of the
wave, and a dashed line at half the sample rate.

The dots are samples — the values a digital instrument would actually record. Ignore
them for now if you like; the two panels are the point.
''',
                "notice": [
                    "The window is 100 ms wide. At 20 Hz you count two complete cycles across it; set the frequency to 50 Hz and you count five, because the period is one over the frequency and nothing else.",
                    "The lower panel is one spike, at whatever the frequency slider says. A pure sinusoid is a single frequency and nothing else, which is exactly why the rest of this course can work at one frequency at a time.",
                    "The dots are 21 samples taken across the window at 200 Hz. Push the signal frequency past the dashed line at half the sample rate and an amber wave appears, at the lower frequency those samples have folded down to. Set the frequency to 220 Hz and the amber wave runs exactly through the dots: 21 samples that cannot tell 220 Hz from 20 Hz. That is aliasing, it belongs to a later course, and for now it is a reminder that a measurement is only as good as its sample rate.",
                ],
            },
            "quiz": {
                "title": "Describing a wave",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A voltage completes one full cycle every 20 ms. What is its frequency?",
                        "opts": ["20 Hz", "50 Hz", "0.02 Hz", "200 Hz"],
                        "a": 1,
                        "why": r'''
Frequency is one over the period: $f = 1/T = 1/0.020 = 50$ Hz. The trap is reading
the number 20 off the question and answering 20 Hz — that is the period in
milliseconds, not a frequency at all. Keep the units in the arithmetic and the
mistake becomes impossible: 1/(20 ms) is 50 per second.
''',
                    },
                    {
                        "q": "The mains supply in Europe runs at 50 Hz. What is its angular frequency $\\omega$?",
                        "opts": ["50 rad/s", "314 rad/s", "3.14 rad/s", "0.02 rad/s"],
                        "a": 1,
                        "why": r'''
$\omega = 2\pi f = 2\pi \times 50 = 314.16$ rad/s. Frequency counts cycles per
second; angular frequency counts radians per second, and there are $2\pi$ radians in
a cycle. The reason to bother is that $\sin$ takes an angle: you must write
$\sin(2\pi f t)$ or $\sin(\omega t)$, never $\sin(f t)$. A missing factor of $2\pi$
is the single most common error in this course.
''',
                    },
                    {
                        "q": "Why is the plain average of a sinusoid a useless measure of how big it is?",
                        "opts": [
                            "Because averaging is only defined for steady voltages",
                            "Because the average is 0.637 of the peak, which is hard to remember",
                            "Because over a whole cycle the positive and negative halves cancel exactly, giving zero",
                            "Because the average depends on where you start measuring",
                        ],
                        "a": 2,
                        "why": r'''
Over a complete cycle a sinusoid spends as long below zero as above, by the same
amounts, so the mean is exactly zero — for a 1 V wave and for a 1000 V wave alike.
A measure that returns zero for every sinusoid distinguishes nothing. The figure
0.637 is real but it belongs to the *rectified* wave, the one with its negative half
flipped upwards, which is a different waveform. Squaring before averaging is what
fixes this: a square is never negative, so nothing cancels.
''',
                    },
                    {
                        "q": "A 10 V peak sinusoid is applied across a 100 Ω resistor. What average power does the resistor dissipate?",
                        "opts": ["1 W", "0.5 W", "0.707 W", "0.1 W"],
                        "a": 1,
                        "why": r'''
Use the RMS value, not the peak: $V_{rms} = 10/\sqrt{2} = 7.071$ V, and
$P = V_{rms}^2/R = 50/100 = 0.5$ W. Putting the peak into the power formula gives
$100/100 = 1$ W, exactly twice the truth, and that is the whole reason RMS exists —
it is defined so that the direct-current power formula keeps working. The peak power
does momentarily reach 1 W, at the instants the wave is at its crest, but the
resistor's heating follows the average.
''',
                    },
                    {
                        "q": "A mains socket is labelled 230 V. That is an RMS figure. What is the peak voltage?",
                        "opts": ["230 V", "325 V", "163 V", "460 V"],
                        "a": 1,
                        "why": r'''
$V_p = \sqrt{2}\,V_{rms} = 1.414 \times 230 = 325$ V. RMS is always the smaller
number for a sinusoid, so dividing by $\sqrt{2}$ instead of multiplying (giving
163 V) has the relationship upside down. This is not a formality: the insulation and
the voltage rating of anything connected to that socket has to survive 325 V, not
230 V.
''',
                    },
                    {
                        "q": "A square wave switches instantly between +5 V and −5 V, spending equal time at each. What is its RMS value?",
                        "opts": ["5 V", "3.54 V", "0 V", "2.5 V"],
                        "a": 0,
                        "why": r'''
RMS is defined by the squaring, not by a fixed factor. Square this waveform and you
get a constant 25 V², whichever half of the cycle you are in; the mean of 25 is 25,
and the root of that is 5 V. The answer 3.54 V comes from applying $V_p/\sqrt{2}$ out
of habit, but that factor is a property of the *sine* shape alone. Zero is the plain
average, which cancels here exactly as it does for a sinusoid — which is why nobody
uses it.
''',
                    },
                ],
            },
            "lab": {
                "title": "Measure RMS from samples",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
An instrument does not know any formulae. It takes samples and computes.

Write three small functions.

`sample(vp, f, fs, n, phase=0.0)` returns `n` samples of
$v(t) = V_p\sin(2\pi f t + \phi)$, taken at `fs` samples per second, as a NumPy
array. Sample `k` is taken at time $t = k/f_s$, so the first sample is at $t = 0$.

`rms(v)` returns the root of the mean of the square of an array — square every
sample, take the mean, take the square root. Do not use the $\sqrt{2}$ shortcut: the
point is that this definition works for any waveform.

`average_power(v, r)` returns the average power a resistance `r` would dissipate
with that waveform across it.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def sample(vp, f, fs, n, phase=0.0):
    """n samples of vp*sin(2*pi*f*t + phase), taken at fs samples per second."""
    # TODO: build the time array first, then the waveform.
    return np.zeros(n)


def rms(v):
    """Root of the mean of the square. No sqrt(2) shortcuts."""
    # TODO
    return 0.0


def average_power(v, r):
    """Average power dissipated in a resistance r by the waveform v."""
    # TODO
    return 0.0


if __name__ == "__main__":
    v = sample(10.0, 50.0, 10000.0, 10000)
    print("peak:", round(float(np.max(v)), 4))
    print("rms:", round(rms(v), 6))
    print("average power into 100 ohms:", round(average_power(v, 100.0), 6), "W")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def sample(vp, f, fs, n, phase=0.0):
    """n samples of vp*sin(2*pi*f*t + phase), taken at fs samples per second."""
    t = np.arange(n) / float(fs)
    return vp * np.sin(2.0 * np.pi * f * t + phase)


def rms(v):
    """Root of the mean of the square. No sqrt(2) shortcuts."""
    v = np.asarray(v, dtype=float)
    return float(np.sqrt(np.mean(v * v)))


def average_power(v, r):
    """Average power dissipated in a resistance r by the waveform v."""
    return rms(v) ** 2 / float(r)


if __name__ == "__main__":
    v = sample(10.0, 50.0, 10000.0, 10000)
    print("peak:", round(float(np.max(v)), 4))
    print("rms:", round(rms(v), 6))
    print("average power into 100 ohms:", round(average_power(v, 100.0), 6), "W")
'''}],
                "hints": [
                    "`np.arange(n) / fs` is the time array: sample `k` sits at $t = k/f_s$.",
                    "`np.mean(v * v)` is the mean of the square; the elementwise product is what you want, not a dot product.",
                    "`average_power` can call `rms` — it is $V_{rms}^2/R$, and reusing the function you just wrote is the whole point of having written it.",
                ],
                "tests": [
                    {"name": "the waveform starts at zero and peaks a quarter-cycle later", "code": r'''
import numpy as np
_v = sample(10.0, 50.0, 10000.0, 10000)
assert len(_v) == 10000, f"expected 10000 samples, got {len(_v)}"
assert abs(_v[0]) < 1e-12, f"sin(0) is 0, so the first sample should be 0, got {_v[0]}"
assert abs(_v[50] - 10.0) < 1e-9, \
    f"a quarter of a 20 ms period is 5 ms, which is sample 50, and there the wave is at its peak; got {_v[50]}"
'''},
                    {"name": "the RMS of a sinusoid is the peak over root two", "code": r'''
import numpy as np
_v = sample(10.0, 50.0, 10000.0, 10000)
_r = rms(_v)
assert abs(_r - 10.0 / np.sqrt(2)) < 1e-9, \
    f"50 whole cycles of a 10 V peak sine should give 7.0710678 V rms, got {_r}"
'''},
                    {"name": "the RMS of a steady voltage is that voltage", "code": r'''
import numpy as np
_r = rms(np.full(500, 4.0))
assert abs(_r - 4.0) < 1e-12, \
    f"a steady 4 V is already 4 V rms — the sqrt(2) belongs to the sine shape alone; got {_r}"
'''},
                    {"name": "the RMS of a square wave is its peak", "code": r'''
import numpy as np
_sq = np.array([5.0] * 100 + [-5.0] * 100)
_r = rms(_sq)
assert abs(_r - 5.0) < 1e-12, \
    f"squaring gives a constant 25, so the rms is 5; got {_r} (3.54 would mean a sqrt(2) was applied out of habit)"
'''},
                    {"name": "phase does not change the RMS", "code": r'''
import numpy as np
_a = rms(sample(3.0, 50.0, 10000.0, 10000, phase=0.0))
_b = rms(sample(3.0, 50.0, 10000.0, 10000, phase=1.234))
assert abs(_a - 3.0 / np.sqrt(2)) < 1e-9, f"a 3 V peak sine is 2.1213 V rms, got {_a}"
assert abs(_a - _b) < 1e-9, f"shifting a wave in time cannot change its size: {_a} vs {_b}"
'''},
                    {"name": "average power uses the RMS, not the peak", "code": r'''
import numpy as np
_p = average_power(sample(10.0, 50.0, 10000.0, 10000), 100.0)
assert abs(_p - 0.5) < 1e-9, \
    f"10 V peak into 100 ohms averages 0.5 W; 1.0 W would mean the peak went into the formula. Got {_p}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Phasors and impedance",
            "summary": "One idea replaces all of the calculus: at a fixed frequency, a capacitor and an inductor are just resistances that depend on frequency.",
            "concepts": [
                "In a resistor the current and the voltage rise and fall together — they are **in phase**. In a capacitor the current reaches its peak a quarter of a cycle *before* the voltage does; in an inductor, a quarter of a cycle *after*.",
                "A **phasor** is a complex number that carries the amplitude and the phase of a sinusoid at one fixed frequency. It is a bookkeeping device: it lets you add two sinusoids of the same frequency by adding two complex numbers.",
                "The $j$ below is the square root of −1 — electrical engineering writes $j$ because $i$ already means current. Two facts about it carry this whole course: the number $a + jb$ has **magnitude** $\\sqrt{a^2 + b^2}$, and multiplying by $j$ advances a phasor by a quarter of a cycle. EE111 develops the algebra properly; nothing here needs more than those two.",
                "**Impedance** $Z$ is the ratio of voltage phasor to current phasor, measured in ohms. It is complex: its magnitude says how much the component resists, its angle says how far the current is shifted from the voltage.",
                "$Z_R = R$, $Z_C = \\dfrac{1}{j\\omega C}$ with magnitude $\\dfrac{1}{\\omega C}$, and $Z_L = j\\omega L$ with magnitude $\\omega L$.",
                "A capacitor's magnitude $1/(\\omega C)$ grows without bound as the frequency falls to zero, so at DC it is an open circuit — it blocks. It falls towards zero as frequency rises, so at high frequency it is nearly a wire.",
                "An inductor is the mirror image: $\\omega L$ is zero at DC, so it is a plain wire there, and large at high frequency.",
                "Impedances in series add, exactly as resistances do — but as complex numbers, so a 100 Ω resistor in series with 100 Ω of reactance gives $|Z| = \\sqrt{100^2 + 100^2} = 141$ Ω, not 200 Ω.",
                "**Reactance** is the part of the impedance that shifts the phase. It stores energy and hands it back; it dissipates nothing. Only resistance turns electrical energy into heat.",
            ],
            "quiz": {
                "title": "Reactance and impedance",
                "minutes": 9,
                "questions": [
                    {
                        "q": "What is the magnitude of the impedance of a 1 µF capacitor at 1 kHz?",
                        "opts": ["1000 Ω", "159 Ω", "6.28 Ω", "0.159 Ω"],
                        "a": 1,
                        "why": r'''
$|Z_C| = 1/(\omega C) = 1/(2\pi \times 1000 \times 10^{-6}) = 159.2$ Ω. The answer
1000 Ω comes from writing $1/(fC)$ and forgetting that the formula wants angular
frequency: $\omega$, not $f$. That single factor of $2\pi$ is worth a factor of 6.28
in every capacitor calculation you will ever do, so it is worth writing $\omega$
explicitly until it becomes automatic.
''',
                    },
                    {
                        "q": "What does an ideal capacitor look like to a steady, unchanging voltage?",
                        "opts": [
                            "A short circuit — a plain wire",
                            "A resistance equal to $1/C$",
                            "An open circuit — a break in the wire",
                            "It depends on the voltage",
                        ],
                        "a": 2,
                        "why": r'''
At DC the frequency is zero, so $|Z_C| = 1/(\omega C)$ is infinite: an open circuit.
No steady current flows through a capacitor, ever. Notice this is a statement about
current *through* it, not charge stored on it — the plates do charge up, and then the
current stops. The short-circuit answer describes what a capacitor becomes at *high*
frequency, which is the opposite end of the same formula.
''',
                    },
                    {
                        "q": "And what does an ideal inductor look like to a steady, unchanging voltage?",
                        "opts": [
                            "An open circuit",
                            "A short circuit — a plain wire",
                            "A resistance equal to $L$",
                            "A source of voltage",
                        ],
                        "a": 1,
                        "why": r'''
$|Z_L| = \omega L$, and at $\omega = 0$ that is zero: a wire. An inductor is a coil
of wire, so this should be reassuring rather than surprising — with nothing changing,
there is nothing for the magnetic field to oppose. It is the exact mirror of the
capacitor, which is worth holding on to: whatever a capacitor does at one end of the
frequency range, an inductor does at the other.
''',
                    },
                    {
                        "q": "In a capacitor, how does the current relate in time to the voltage across it?",
                        "opts": [
                            "The current lags the voltage by a quarter of a cycle",
                            "The current leads the voltage by a quarter of a cycle",
                            "They peak at the same instant",
                            "The current is always zero",
                        ],
                        "a": 1,
                        "why": r'''
The current into a capacitor is largest when the voltage is changing fastest, which
for a sinusoid is when the voltage is passing through zero — a quarter cycle, or 90°,
*before* the voltage reaches its peak. So the current leads. The lagging answer is
the inductor, and mixing the two up is so common that it has a mnemonic: in a
capacitor, C, the current I leads; in an inductor, L, the current I lags.
''',
                    },
                    {
                        "q": "A 100 Ω resistor is in series with a capacitor whose reactance at this frequency is also 100 Ω. What is the magnitude of the total impedance?",
                        "opts": ["200 Ω", "141 Ω", "100 Ω", "0 Ω"],
                        "a": 1,
                        "why": r'''
Impedances in series add, but as complex numbers: $Z = 100 - j100$, and its magnitude
is $\sqrt{100^2 + 100^2} = 141$ Ω. Adding the magnitudes to get 200 Ω is the standard
error, and it fails because the two contributions are at right angles to one another —
the resistor's voltage and the capacitor's voltage peak a quarter cycle apart, so
they never add up at their full values at the same instant.
''',
                    },
                    {
                        "q": "How much average power does an ideal capacitor dissipate?",
                        "opts": [
                            "None — it stores energy and returns it",
                            "$V_{rms}^2/|Z_C|$, the same as a resistor of that size",
                            "Half of what a resistor of the same magnitude would",
                            "It depends on the frequency",
                        ],
                        "a": 0,
                        "why": r'''
None. Over each cycle an ideal capacitor draws energy in and pushes exactly the same
energy back out, because its current and voltage are a quarter cycle apart: for a
quarter of the time the product is positive, for the next quarter it is negative, and
the average is zero. That is the real distinction between resistance and reactance —
both impede current, but only resistance turns the energy into heat. A real capacitor
has a little loss, and it is modelled by adding a small resistance, never by treating
the reactance as one.
''',
                    },
                ],
            },
            "build": {
                "title": "A capacitor that blocks DC and passes AC",
                "minutes": 22,
                "brief": r'''
The claim from the concepts, drawn and measured.

You are given a source, a ground, a load resistor and a probe, wired straight
through — whatever the source does, the probe sees. Break that connection with a
capacitor so that the circuit becomes a **coupling network**: a steady voltage is
stopped completely, and a fast enough signal gets through untouched.

The circuit must do three things.

1. **Nothing at DC.** With the source held at a steady voltage, the probe reads zero.
2. **Everything well above 1 kHz.** At 500 kHz the probe reads the full source
   amplitude.
3. **Exactly 70.7% at 1 kHz.** That is the corner: the frequency where the capacitor's
   reactance equals the resistance, and the output has fallen to $1/\sqrt{2}$ of the
   amplitude it has in the pass band.

Point 3 fixes the *product* of the resistance and the capacitance, not either one on
its own: $f_c = 1/(2\pi R C)$. Any pair with the right product passes, so choose a
resistance you like and work out the capacitance, or the other way round.

The source value is used both as its steady level and as its amplitude when the
checks sweep frequency, so the exact number you give it does not matter — every check
compares the output against the source rather than against a fixed voltage.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "C", "x": 7, "y": 3, "rot": 0, "value": 1.6e-7},
                        {"id": "p3", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [6, 3]},
                        {"a": [8, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "checks": [
                    {"name": "no steady voltage reaches the output", "code": r'''
c.assert(Math.abs(c.vout()) < 1e-6,
  "at DC the probe reads " + c.fmt(c.vout(), "V") +
  " — a steady voltage is still getting through, so nothing is blocking it");
'''},
                    {"name": "the full amplitude gets through at 500 kHz", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(c.gain(500000), vs, 0.02,
  "far above the corner the capacitor's reactance is negligible and the output should equal the source");
'''},
                    {"name": "the output is 70.7% of the source at 1 kHz", "code": r'''
var vs = Math.abs(c.values("V")[0]);
c.close(c.gain(1000) / vs, 0.70711, 0.03,
  "1 kHz is meant to be the corner, where the reactance equals the resistance");
'''},
                    {"name": "the output leads the input by 90 degrees far below the corner", "code": r'''
var d = c.phase(10) - c.phase(500000);
while (d > 180) d -= 360;
while (d < -180) d += 360;
c.close(Math.abs(d), 90, 0.03,
  "two decades below the corner the capacitor dominates, and its current leads its voltage by a quarter cycle");
'''},
                ],
                "hints": [
                    "The capacitor goes in series, between the source and the output node — it has to be the only path the signal can take. A capacitor to ground would do the opposite job.",
                    "Delete the long wire between the source and the probe, then place the capacitor in the gap and wire both of its pins.",
                    "$f_c = 1/(2\\pi R C)$, so with the 1 kΩ resistor already there you need $C = 1/(2\\pi \\times 1000 \\times 1000) = 159$ nF. 160 nF is within the tolerance.",
                    "Click a part to edit its value. Values accept engineering suffixes, so 160n is 160 nF.",
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "The series RC filter and its corner frequency",
            "summary": "A resistor and a capacitor in series make a divider whose ratio depends on frequency. One number describes the whole thing.",
            "concepts": [
                "A divider works with impedances exactly as it worked with resistances in EE101: $V_{out}/V_{in} = Z_2/(Z_1 + Z_2)$, where $Z_2$ is the impedance the output is measured across.",
                "Resistor first, capacitor to ground, output across the capacitor: $H = \\dfrac{1}{1 + j\\omega R C}$. This is a **low-pass** filter — low frequencies pass, high ones do not.",
                "Its magnitude is $|H| = \\dfrac{1}{\\sqrt{1 + (f/f_c)^2}}$, where the **corner frequency** is $f_c = \\dfrac{1}{2\\pi R C}$.",
                "At the corner, $|H| = 1/\\sqrt{2} = 0.707$ and the phase is exactly −45°. In decibels that is $20\\log_{10}(0.707) = -3.01$ dB, which is why it is called the −3 dB point.",
                "A decade above the corner the output is a tenth; two decades, a hundredth. A first-order filter rolls off at **20 dB per decade**, and no first-order filter rolls off faster.",
                "The **time constant** $\\tau = RC$ is the same fact in the time domain: $f_c = 1/(2\\pi\\tau)$. Charge the capacitor through the resistor and it reaches 63% of its final voltage after one $\\tau$.",
                "Only the product $RC$ sets the corner. 1 kΩ with 1 µF and 1 MΩ with 1 nF are the same filter — but not the same circuit, because the impedance level decides how heavily it loads whatever drives it.",
            ],
            "sandbox": {
                "title": "Reading a corner off a response curve",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 20, "zeta": 0.7, "K": 1},
                "brief": r'''
A **Bode plot**: magnitude in decibels on top, phase in degrees underneath, both
against frequency on a logarithmic axis. This is how every frequency response is
drawn, and reading one is a skill worth ten minutes on its own.

The plant here has two energy stores rather than the one in your RC filter, so the
numbers are doubled — that turns out to make the pattern easier to see, not harder.
The dashed lines mark 0 dB on top and −90° underneath, and the amber dot marks the
gain exactly at the corner.

The sliders are the corner ωₙ in radians per second, the **damping** ζ, which decides
how sharply the curve bends there and whether it overshoots, and K, a plain gain that
multiplies the output at every frequency alike.
''',
                "notice": [
                    "The phase curve crosses the dashed −90° line exactly at ω = ωₙ, whatever ζ is set to. When a magnitude curve bends too gently to place the corner by eye, the phase still tells you where it is.",
                    "The amber dot is the gain at the corner. Take ζ below 0.5 and it climbs above the dashed 0 dB line: at that one frequency the output is bigger than the input, with nothing in the circuit that could amplify. Passive components can do that; only the source supplies energy, and it has to top up nothing more than what the resistor turns into heat.",
                    "Raise K. The magnitude curve shifts bodily upwards and the phase curve does not move at all — a plain gain changes how much, never when.",
                    "Far above the corner the magnitude falls at 40 dB per decade and the phase settles at −180°, because there are two stores. The RC filter you are about to build has one, so it gets half of each: 20 dB per decade and −90°.",
                ],
            },
            "quiz": {
                "title": "Corners, decades and decibels",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A 10 kΩ resistor and a 10 nF capacitor form a low-pass filter. Where is its corner frequency?",
                        "opts": ["10 kHz", "1.59 kHz", "159 Hz", "100 kHz"],
                        "a": 1,
                        "why": r'''
$f_c = 1/(2\pi R C) = 1/(2\pi \times 10^4 \times 10^{-8}) = 1592$ Hz. The product $RC$
is $10^{-4}$ s, so $1/RC = 10\,000$ — and that is where 10 kHz comes from. But
$1/RC$ is an angular frequency in radians per second, not a frequency in hertz;
dividing by $2\pi$ converts it. Whenever an answer comes out as a suspiciously round
number, check whether a $2\pi$ went missing.
''',
                    },
                    {
                        "q": "At exactly the corner frequency, the output amplitude is what fraction of the input?",
                        "opts": ["0.5", "0.707", "0.9", "0.1"],
                        "a": 1,
                        "why": r'''
$1/\sqrt{2} = 0.707$. The corner is defined as the half-*power* point, and power goes
as the square of voltage, so half the power is $\sqrt{0.5} = 0.707$ of the voltage —
not half. In decibels, $20\log_{10}(0.707) = -3.01$, which is the −3 dB you will hear
quoted everywhere. Answering 0.5 means the half-power definition was taken as a
statement about voltage.
''',
                    },
                    {
                        "q": "In a series RC low-pass filter, which component is the output measured across?",
                        "opts": ["The resistor", "The capacitor", "Either — it makes no difference", "Both in turn"],
                        "a": 1,
                        "why": r'''
Across the capacitor. The output is the bottom half of a divider, so it is large when
the impedance you are measuring across is large: the capacitor's reactance
$1/(\omega C)$ is large at low frequency, so low frequencies come through — a
low-pass. Take the same two components and measure across the *resistor* instead and
you have a high-pass, with the same corner frequency. The components do not decide
which it is; where you put the probe does.
''',
                    },
                    {
                        "q": "A first-order low-pass filter has its corner at 1 kHz. Roughly what is the output at 10 kHz, as a fraction of the input?",
                        "opts": ["A half", "A tenth", "A hundredth", "Unchanged"],
                        "a": 1,
                        "why": r'''
A tenth, which is −20 dB. One decade above the corner, $|H| = 1/\sqrt{1 + 10^2}
= 0.0995$, near enough a tenth, and the pattern continues: a hundredth at 100 kHz.
That is what "20 dB per decade" means, and it is the fastest a single resistor and
capacitor can ever roll off. A hundredth at 10 kHz would need two such filters in
cascade.
''',
                    },
                    {
                        "q": "You double both the resistance and the capacitance. What happens to the corner frequency?",
                        "opts": ["It halves", "It quarters", "It doubles", "It is unchanged"],
                        "a": 1,
                        "why": r'''
The corner depends on the product $RC$, and doubling both quadruples the product, so
$f_c = 1/(2\pi RC)$ falls to a quarter of what it was. Answering "halves" is what
happens when only one of the two is doubled. This is worth internalising because it
runs both ways: to move a corner by a factor of ten you can change either component
by ten, or both by about three.
''',
                    },
                    {
                        "q": "You replace a 1 kΩ, 1 µF filter with a 1 MΩ, 1 nF filter. What have you changed?",
                        "opts": [
                            "The corner frequency has moved up by a factor of a thousand",
                            "Nothing at all — the two circuits are identical in every respect",
                            "The corner frequency is the same, but the new filter draws far less current from whatever drives it",
                            "The corner frequency is the same, and the new filter draws far more current",
                        ],
                        "a": 2,
                        "why": r'''
Both have $RC = 10^{-3}$ s, so both corner at 159 Hz. What changed is the impedance
level: the megohm version draws a thousand times less current from the source, which
is often exactly what you want — but it is also a thousand times more easily disturbed
by whatever you connect to its output, and by stray capacitance in the wiring. The
corner is set by the product; the practicality is set by the individual values.
''',
                    },
                ],
            },
            "build": {
                "title": "A low-pass filter with a 1 kHz corner",
                "minutes": 25,
                "brief": r'''
Build the filter the concepts describe, from a source, a ground and a probe.

You are given the source wired straight to the probe, and a ground rail along the
bottom. Add a resistor and a capacitor so that the circuit behaves like this.

1. **At DC the output equals the source.** No current flows in the resistor, because
   the capacitor is an open circuit, so there is no voltage dropped across the
   resistor at all.
2. **The corner sits at 1 kHz**, within 5%. That is the frequency where the output has
   fallen to 0.707 of its low-frequency value.
3. **It rolls off at 20 dB per decade** — at 10 kHz the output is about a tenth of
   what it is at 10 Hz.
4. **The phase at the corner is 45° of lag** relative to the low-frequency phase.

Only the product $RC$ is fixed by the corner, so any sensible pair works.
Something in the region of 1 kΩ to 100 kΩ for the resistor keeps the capacitor a
believable size.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [9, 3]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 1600},
                        {"id": "p3", "kind": "C", "x": 9, "y": 4, "rot": 1, "value": 1e-7},
                        {"id": "p4", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "checks": [
                    {"name": "at DC the output equals the source", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(Math.abs(c.vout()), vs, 0.01,
  "with the capacitor open at DC no current flows, so nothing is dropped across the resistor");
'''},
                    {"name": "the corner is at 1 kHz", "code": r'''
var fc = c.corner(10, 1e6);
c.close(fc, 1000, 0.05,
  "the corner measured from the response is " + c.fmt(fc, "Hz") + "; adjust the R-C product");
'''},
                    {"name": "it rolls off at 20 dB per decade", "code": r'''
var ratio = c.gain(10000) / c.gain(10);
c.close(ratio, 0.0995, 0.08,
  "a decade above a first-order corner the output should be about a tenth of the pass-band value");
'''},
                    {"name": "the phase at the corner is 45 degrees of lag", "code": r'''
var d = c.phase(1000) - c.phase(1);
while (d > 180) d -= 360;
while (d < -180) d += 360;
c.close(Math.abs(d), 45, 0.06,
  "at the corner the reactance equals the resistance, which puts the output exactly 45 degrees behind");
'''},
                ],
                "hints": [
                    "The resistor goes in series between the source and the output node; the capacitor goes from the output node down to the ground rail.",
                    "Delete the wire between the source and the probe first, so there is somewhere to put the resistor.",
                    "You need $RC = 1/(2\\pi \\times 1000) = 1.59 \\times 10^{-4}$. For example 1.6 kΩ with 100 nF, or 16 kΩ with 10 nF.",
                    "If the corner check reports a huge frequency, the response is flat — the capacitor is probably not connected to ground.",
                ],
            },
            "lab": {
                "title": "The response of the filter you just drew",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
The same filter, now as three lines of arithmetic.

`corner_hz(r, c)` returns $f_c = 1/(2\pi R C)$ in hertz.

`response(f, r, c)` returns the complex ratio $V_{out}/V_{in}$ of the low-pass
filter at frequency `f`. Written in terms of the corner it is

```text
H = 1 / (1 + 1j * (f / fc))
```

Python writes the imaginary unit as `1j`, and `abs(H)` gives the magnitude of a
complex number while `np.angle(H)` gives its angle in radians.

`gain_db(f, r, c)` returns the magnitude in decibels: $20\log_{10}|H|$.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def corner_hz(r, c):
    """The -3 dB frequency of an R-C low-pass, in hertz."""
    # TODO
    return 0.0


def response(f, r, c):
    """Complex Vout/Vin of the low-pass filter at frequency f."""
    # TODO
    return 0j


def gain_db(f, r, c):
    """Magnitude of the response in decibels."""
    # TODO
    return 0.0


if __name__ == "__main__":
    R, C = 1600.0, 1e-7
    fc = corner_hz(R, C)
    print("corner:", round(fc, 3), "Hz")
    print("gain at the corner:", round(abs(response(fc, R, C)), 6))
    print("dB at the corner:", round(gain_db(fc, R, C), 4))
    print("dB a decade up:", round(gain_db(10 * fc, R, C), 4))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def corner_hz(r, c):
    """The -3 dB frequency of an R-C low-pass, in hertz."""
    return 1.0 / (2.0 * np.pi * r * c)


def response(f, r, c):
    """Complex Vout/Vin of the low-pass filter at frequency f."""
    return 1.0 / (1.0 + 1j * (f / corner_hz(r, c)))


def gain_db(f, r, c):
    """Magnitude of the response in decibels."""
    return 20.0 * np.log10(abs(response(f, r, c)))


if __name__ == "__main__":
    R, C = 1600.0, 1e-7
    fc = corner_hz(R, C)
    print("corner:", round(fc, 3), "Hz")
    print("gain at the corner:", round(abs(response(fc, R, C)), 6))
    print("dB at the corner:", round(gain_db(fc, R, C), 4))
    print("dB a decade up:", round(gain_db(10 * fc, R, C), 4))
'''}],
                "hints": [
                    "`np.pi` is $\\pi$. The corner is one over $2\\pi RC$, so a bracket in the wrong place costs a factor of $4\\pi^2$.",
                    "`response` can call `corner_hz` — writing $f/f_c$ rather than $\\omega R C$ keeps the $2\\pi$ in exactly one place.",
                    "`abs()` on a Python complex number gives its magnitude, so `gain_db` is one call to `np.log10` away.",
                ],
                "tests": [
                    {"name": "the corner of a 1.6 kilohm, 100 nF filter", "code": r'''
_fc = corner_hz(1600.0, 1e-7)
assert abs(_fc - 994.7183943243459) < 1e-6, \
    f"1/(2*pi*1600*1e-7) is 994.718 Hz; got {_fc} (10000 would mean the 2*pi is missing)"
'''},
                    {"name": "only the product of R and C matters", "code": r'''
_a = corner_hz(1e3, 1e-6)
_b = corner_hz(1e6, 1e-9)
assert abs(_a - _b) < 1e-9, f"both have RC = 1 ms, so both corner at the same place: {_a} vs {_b}"
assert abs(_a - 159.15494309189535) < 1e-9, f"expected 159.155 Hz, got {_a}"
'''},
                    {"name": "the response is 0.707 and minus 45 degrees at the corner", "code": r'''
import numpy as np
_fc = corner_hz(1600.0, 1e-7)
_h = response(_fc, 1600.0, 1e-7)
assert abs(abs(_h) - 0.7071067811865475) < 1e-9, f"magnitude at the corner should be 1/sqrt(2), got {abs(_h)}"
assert abs(np.angle(_h) * 180 / np.pi + 45.0) < 1e-9, \
    f"phase at the corner should be -45 degrees, got {np.angle(_h) * 180 / np.pi}"
'''},
                    {"name": "at DC the filter passes everything", "code": r'''
_h = response(0.0, 1600.0, 1e-7)
assert abs(abs(_h) - 1.0) < 1e-12, f"a capacitor is open at DC, so H(0) = 1; got {abs(_h)}"
'''},
                    {"name": "the corner is minus 3 dB and a decade up is minus 20", "code": r'''
_fc = corner_hz(1600.0, 1e-7)
_at = gain_db(_fc, 1600.0, 1e-7)
_up = gain_db(10 * _fc, 1600.0, 1e-7)
assert abs(_at + 3.010299956639812) < 1e-9, f"the corner should be -3.01 dB, got {_at}"
assert abs(_up + 20.043213737826427) < 1e-9, f"a decade above should be -20.04 dB, got {_up}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Inductors, RL circuits and the time constant",
            "summary": "The mirror image of the capacitor, and the same first-order behaviour seen in time rather than in frequency.",
            "concepts": [
                "An inductor is a coil of wire. It opposes a *change* in the current through it: $v = L\\,di/dt$, with $L$ in henries.",
                "So at DC an ideal inductor is a plain wire, and at high frequency it is nearly a break in the circuit — the exact opposite of a capacitor at both ends.",
                "A resistor and an inductor in series, with the output taken across the resistor, is a low-pass filter: $H = \\dfrac{R}{R + j\\omega L}$, with corner $f_c = \\dfrac{R}{2\\pi L}$.",
                "Its **time constant** is $\\tau = L/R$ seconds — note that it is a ratio, not a product, so a *larger* resistance makes an RL circuit faster while it makes an RC circuit slower.",
                "Switch a step of voltage onto a first-order circuit and the output moves towards its final value as $1 - e^{-t/\\tau}$: 63% of the way after one $\\tau$, 86% after two, 99.3% after five. In practice, five time constants is settled.",
                "The time constant and the corner frequency are two descriptions of one circuit: $f_c = 1/(2\\pi\\tau)$. A fast circuit in time is a wide one in frequency, always.",
                "A capacitor blocks DC because its reactance $1/(\\omega C)$ grows without bound as the frequency goes to zero — not because charge cannot cross the gap. Charge never crosses the gap at any frequency, yet alternating current flows in the wires all the same, because charge arriving on one plate pushes an equal charge off the other.",
            ],
            "sandbox": {
                "title": "What a second energy store adds",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 8, "zeta": 0.25, "K": 1},
                "brief": r'''
Put an inductor and a capacitor in the same circuit and something appears that no
first-order filter can do: a peak.

This is a resistor, an inductor and a capacitor in series, with the output measured
across the capacitor. Its corner is $\omega_n = 1/\sqrt{LC}$, and the damping $\zeta$
falls as the resistance falls. You do not need to design one yet. The point is to see
what the second store buys, and what it costs.
''',
                "notice": [
                    "At ζ = 0.25 the amber dot — the gain exactly at the corner — sits about 6 dB above the dashed 0 dB line. The output is twice the input at that one frequency, with nothing in the circuit that could amplify: the inductor and the capacitor are handing energy back and forth, and the source only replaces what the resistor turns into heat.",
                    "Take ζ up to 1 and the peak is gone; the dot drops to 6 dB below the line, half the input. Damping is what a resistor does to a resonance.",
                    "Above the corner the magnitude falls at 40 dB per decade and the phase ends at −180°: each store contributes 20 dB per decade and 90° of lag, and the RC and RL filters you have built are simply the one-store version.",
                    "Slide ωₙ along. The whole picture translates sideways on the logarithmic axis with its shape unchanged — the same filter, tuned somewhere else.",
                ],
            },
            "quiz": {
                "title": "Inductors and time constants",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is the magnitude of the impedance of a 10 mH inductor at 1 kHz?",
                        "opts": ["10 Ω", "62.8 Ω", "0.0159 Ω", "6.28 Ω"],
                        "a": 1,
                        "why": r'''
$|Z_L| = \omega L = 2\pi \times 1000 \times 0.010 = 62.8$ Ω. Writing $fL$ instead of
$\omega L$ gives 10 Ω — the same missing $2\pi$ that turns up in every capacitor
calculation, and worth the same care. Notice the direction: raise the frequency and
an inductor impedes *more*, where a capacitor impedes less.
''',
                    },
                    {
                        "q": "What is the time constant of a 1 kΩ resistor in series with a 100 mH inductor?",
                        "opts": ["100 µs", "100 s", "10 µs", "0.1 s"],
                        "a": 0,
                        "why": r'''
$\tau = L/R = 0.1/1000 = 10^{-4}$ s, or 100 µs. It is a ratio, not a product, and
that is the part worth remembering: multiplying gives 100 s, which is absurd for a
circuit of this size and is the standard slip. It also means that increasing the
resistance makes an RL circuit *faster*, while increasing the resistance makes an RC
circuit slower.
''',
                    },
                    {
                        "q": "A step of voltage is applied to a first-order circuit. After one time constant, how far has the output moved towards its final value?",
                        "opts": ["37%", "50%", "63%", "100%"],
                        "a": 2,
                        "why": r'''
$1 - e^{-1} = 0.632$, so 63%. The figure 37% is $e^{-1}$ itself, which is how much of
the *gap* is still left — the same number seen from the other side, and the usual
confusion. Both are worth carrying: after one $\tau$ you are 63% of the way there and
37% short, and after five $\tau$ you are 99.3% there, which is why five time constants
is the working definition of settled.
''',
                    },
                    {
                        "q": "In a series RL circuit with the output taken across the resistor, what kind of filter do you have?",
                        "opts": [
                            "A low-pass, with corner $R/(2\\pi L)$",
                            "A high-pass, with corner $R/(2\\pi L)$",
                            "A low-pass, with corner $L/(2\\pi R)$",
                            "Neither — an inductor cannot filter",
                        ],
                        "a": 0,
                        "why": r'''
The divider is $R/(R + j\omega L)$. At DC the inductor is a wire and the whole source
appears across the resistor; at high frequency the inductor's $\omega L$ dominates
and almost nothing does. That is a low-pass, cornering where $\omega L = R$, which is
$f_c = R/(2\pi L)$. Putting $L$ over $R$ instead gives a corner in seconds rather
than hertz — that combination is the time constant, and $f_c = 1/(2\pi\tau)$.
''',
                    },
                    {
                        "q": "Which statement best explains why a capacitor blocks direct current but passes alternating current?",
                        "opts": [
                            "Charge cannot cross the insulating gap, so no current can pass at any frequency",
                            "Alternating current is small enough to leak across the gap, while direct current is not",
                            "Its reactance $1/(\\omega C)$ grows without bound as the frequency falls to zero, and shrinks as it rises",
                            "The capacitor discharges itself between cycles",
                        ],
                        "a": 2,
                        "why": r'''
The reactance is the answer, and the first option is a true statement with a false
conclusion attached: charge really does not cross the gap, at any frequency — yet
alternating current flows in the wires perfectly well, because charge arriving on one
plate pushes an equal charge off the other. Nothing leaks. What changes with frequency
is how much voltage it takes to push a given current in and out of the plates, and
that is exactly what $1/(\omega C)$ measures.
''',
                    },
                ],
            },
            "build": {
                "title": "An RL circuit with a 100 µs time constant",
                "minutes": 25,
                "brief": r'''
Same first-order behaviour, different pair of components, and this time the
specification is written in the time domain.

You are given a source, a ground and a 1 kΩ load resistor wired directly across the
source, with the probe on the resistor. Insert an inductor in series so that the
circuit has a **time constant of 100 µs**.

What that must produce:

1. **At DC the output still equals the source**, because an ideal inductor is a plain
   wire to a steady voltage.
2. **A step reaches 63% of its final value after 100 µs.** That is what a time
   constant of 100 µs means.
3. **The corner sits at 1591.5 Hz**, which is the same statement in frequency:
   $f_c = 1/(2\pi\tau)$.
4. **It rolls off at 20 dB per decade** above the corner, like every first-order
   circuit.

$\tau = L/R$, so the resistor you were given and the time constant you were asked for
fix the inductance between them. You may change the resistor if you prefer, provided
the ratio comes out right.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "L", "x": 5, "y": 3, "rot": 0, "value": 0.1},
                        {"id": "p3", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "checks": [
                    {"name": "at DC the output equals the source", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(Math.abs(c.vout()), vs, 0.01,
  "an ideal inductor is a plain wire at DC, so the whole source should appear across the resistor");
'''},
                    {"name": "a step reaches 63% after 100 microseconds", "code": r'''
var s = c.step(1e-3);
var last = Math.abs(s.v[s.v.length - 1]);
c.assert(last > 1e-9, "the output never rises at all — check that the source reaches the resistor");
var i = 0;
while (i < s.t.length - 1 && s.t[i] < 1e-4) i++;
c.close(Math.abs(s.v[i]) / last, 0.632, 0.06,
  "after one time constant a first-order step should be 63% of the way to its final value");
'''},
                    {"name": "the corner is at 1591.5 Hz", "code": r'''
var fc = c.corner(10, 1e6);
c.close(fc, 1591.55, 0.05,
  "measured corner " + c.fmt(fc, "Hz") + "; a 100 microsecond time constant corners at 1/(2*pi*tau)");
'''},
                    {"name": "it rolls off at 20 dB per decade", "code": r'''
var ratio = c.gain(15915) / c.gain(10);
c.close(ratio, 0.0995, 0.08,
  "a decade above a first-order corner the output should be about a tenth of the pass-band value");
'''},
                ],
                "hints": [
                    "The inductor goes in series between the source and the top of the resistor, exactly where the resistor went in the RC filter.",
                    "Delete the wire from the source to the probe first, then place the inductor in the gap.",
                    "$\\tau = L/R$, so with 1 kΩ you need $L = \\tau R = 10^{-4} \\times 1000 = 0.1$ H.",
                    "If the step check says the output never rises, one of the inductor's pins is not wired to anything.",
                ],
            },
            "lab": {
                "title": "The RL step, by formula and by simulation",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
The circuit you just drew, checked two ways.

`tau(r, l)` returns the time constant $L/R$ in seconds.

`resistor_voltage(r, l, vs, t)` returns the analytic answer: the voltage across the
resistor at time `t` after a step of `vs` volts is applied, which is
$v_s\left(1 - e^{-t/\tau}\right)$. `t` may be a NumPy array, and if you use
`np.exp` it will work for both an array and a single number without any extra effort.

`simulate(r, l, vs, dt, n)` gets the same answer without the formula. The inductor
obeys $L\,di/dt = v_s - iR$, so step the current forward:

```text
i_next = i + dt * (vs - i * r) / l
```

Start from `i = 0`, record the resistor voltage `i * r` **before** each update, and
return a list of `n` values. Then compare the two: they should agree.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def tau(r, l):
    """The time constant of a series R-L circuit, in seconds."""
    # TODO
    return 0.0


def resistor_voltage(r, l, vs, t):
    """Analytic voltage across the resistor, t seconds after a step of vs volts."""
    # TODO
    return 0.0


def simulate(r, l, vs, dt, n):
    """Forward Euler on the inductor current; return n resistor voltages."""
    i = 0.0
    out = []
    # TODO: record i * r, then advance the current by one step, n times.
    return out


if __name__ == "__main__":
    R, L, VS = 1000.0, 0.1, 5.0
    print("tau:", tau(R, L), "s")
    print("analytic at one tau:", round(float(resistor_voltage(R, L, VS, tau(R, L))), 6))
    vs_sim = simulate(R, L, VS, 1e-6, 500)
    print("simulated at one tau:", round(vs_sim[100], 6) if len(vs_sim) > 100 else None)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def tau(r, l):
    """The time constant of a series R-L circuit, in seconds."""
    return float(l) / float(r)


def resistor_voltage(r, l, vs, t):
    """Analytic voltage across the resistor, t seconds after a step of vs volts."""
    return vs * (1.0 - np.exp(-np.asarray(t, dtype=float) / tau(r, l)))


def simulate(r, l, vs, dt, n):
    """Forward Euler on the inductor current; return n resistor voltages."""
    i = 0.0
    out = []
    for _ in range(n):
        out.append(i * r)
        i = i + dt * (vs - i * r) / l
    return out


if __name__ == "__main__":
    R, L, VS = 1000.0, 0.1, 5.0
    print("tau:", tau(R, L), "s")
    print("analytic at one tau:", round(float(resistor_voltage(R, L, VS, tau(R, L))), 6))
    vs_sim = simulate(R, L, VS, 1e-6, 500)
    print("simulated at one tau:", round(vs_sim[100], 6) if len(vs_sim) > 100 else None)
'''}],
                "hints": [
                    "`tau` is a ratio: inductance over resistance. If the number comes out enormous, they are the wrong way round.",
                    "`np.exp` accepts an array, so `resistor_voltage` needs no loop and no `if`.",
                    "In `simulate`, append first and update afterwards — otherwise the first entry is already one step in and the response appears to start above zero.",
                ],
                "tests": [
                    {"name": "the time constant is a ratio, not a product", "code": r'''
_t = tau(1000.0, 0.1)
assert abs(_t - 1e-4) < 1e-15, f"L/R = 0.1/1000 = 100 microseconds; got {_t}"
_t2 = tau(2000.0, 0.1)
assert _t2 < _t, "more resistance makes an R-L circuit faster, not slower"
'''},
                    {"name": "the analytic step is 63% after one tau and 99.3% after five", "code": r'''
import numpy as np
_v1 = float(resistor_voltage(1000.0, 0.1, 5.0, 1e-4))
_v5 = float(resistor_voltage(1000.0, 0.1, 5.0, 5e-4))
assert abs(_v1 - 3.160602794142788) < 1e-9, f"one tau should give 0.6321*5 = 3.1606 V, got {_v1}"
assert abs(_v5 - 4.966310265004573) < 1e-9, f"five taus should give 4.9663 V, got {_v5}"
'''},
                    {"name": "the analytic step handles an array of times", "code": r'''
import numpy as np
_v = resistor_voltage(1000.0, 0.1, 5.0, np.array([0.0, 1e-4, 1e9]))
assert len(_v) == 3, f"expected three values back, got {_v}"
assert abs(_v[0]) < 1e-12, f"at t = 0 the current is still zero, so the resistor sees 0 V; got {_v[0]}"
assert abs(_v[2] - 5.0) < 1e-9, f"long afterwards the inductor is a wire and the resistor sees all 5 V; got {_v[2]}"
'''},
                    {"name": "the simulation starts at zero and has the right length", "code": r'''
_s = simulate(1000.0, 0.1, 5.0, 1e-6, 500)
assert len(_s) == 500, f"expected 500 samples, got {len(_s)}"
assert abs(_s[0]) < 1e-15, f"the current starts at zero, so the first sample is 0 V; got {_s[0]}"
'''},
                    {"name": "the simulation agrees with the formula", "code": r'''
import numpy as np
_s = simulate(1000.0, 0.1, 5.0, 1e-6, 500)
_want = float(resistor_voltage(1000.0, 0.1, 5.0, 100 * 1e-6))
assert abs(_s[100] - _want) / _want < 0.01, \
    f"at one tau the simulation gives {_s[100]:.6f} and the formula {_want:.6f} — they should agree to 1%"
assert abs(_s[-1] - 5.0) < 0.05, f"after 500 microseconds it should be close to 5 V, got {_s[-1]}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Identify three filters you cannot open",
        "runtime": "python",
        "minutes": 100,
        "brief": r'''
Three sealed boxes sit on the bench. Each contains one first-order filter — a
resistor and a capacitor, nothing else — and you cannot see inside any of them.

What you *can* do is drive a box with a sinusoid of your choosing and capture the
waveform that comes out. `bench.py` does exactly that and no more: give it a box name
and a frequency, and it hands back a captured waveform. The input is always 1 V peak.

From that alone, work out for each box whether it is a low-pass or a high-pass, where
its corner frequency is, and what resistor it must contain if the capacitor is 10 nF.

## What the bench gives you

`capture(name, f)` returns a NumPy array: 8 complete cycles of the output, at 256
samples per cycle, whatever the frequency. Because it is always a whole number of
cycles, the RMS of that array is an exact measure of the output size, so you never
have to worry about where the capture starts or stops.

The generator is not perfectly pure — there is about 5% of a third harmonic riding on
the drive, which is normal, and the box filters that harmonic at its own frequency
like any other. It shifts every corner you measure about 0.2% low. Do not try to
remove it; the tolerances allow for it.

## Suggested order

Get `rms` working first and check it against a waveform you already know. Then
`amplitude`, which is one line on top of it. Then `classify`, which needs only two
measurements. `find_corner` is last, and it is a bisection: the same bisection you
would run to find any crossing, in the logarithm of the frequency rather than the
frequency itself, because a filter's response is a straight line on a log axis and
nothing like one on a linear axis.

One trap is worth naming in advance. The corner is 0.707 of the **pass-band** level,
so you have to measure that level somewhere the filter is genuinely doing nothing. If
you read it at the edge of your search bracket, the response there has already begun
to sag, your target comes out low, and the corner you report moves whenever you change
the bracket. Read the pass band a couple of decades outside the bracket instead.
''',
        "deliverables": [
            "`rms(v)`, the root of the mean of the square of a captured waveform, working for any waveform rather than only for a sinusoid.",
            "`amplitude(name, f)`, the RMS of one capture from a named box at one frequency.",
            "`classify(name)`, returning the string `\"low-pass\"` or `\"high-pass\"`, decided by measurement at two well-separated frequencies rather than by any knowledge of what is in the box.",
            "`find_corner(name, f_lo, f_hi)`, returning the −3 dB frequency in hertz, found by bisecting on the measured response between the two bounds, and correct for either kind of filter.",
            "`resistor_for(fc, c)`, returning the resistance a filter of that corner frequency must contain given its capacitance.",
            "A comment at the top of `main.py` recording the corner frequency you measured for each of the three boxes and the resistor value each implies for a 10 nF capacitor.",
        ],
        "constraints": [
            "NumPy and the standard library only.",
            "`find_corner` must locate the crossing from measurements. Fitting a straight line to a formula you assumed, or returning a constant, is not measuring.",
            "Nothing may import the internals of `bench.py`: `capture` is the whole interface, and reading `_FILTERS` defeats the exercise.",
            "The corner is defined against the pass band, not against 1 V — measure the pass-band level rather than assuming the filter has unity gain there, and measure it well clear of the corner.",
        ],
        "rubric": [
            {"criterion": "RMS from samples", "weight": 20,
             "evidence": "`rms` computes the root mean square from the array itself and returns the correct value for a sinusoid, a steady level and a square wave alike."},
            {"criterion": "Classification by measurement", "weight": 20,
             "evidence": "`classify` returns the right kind for all three boxes, decided by comparing measured amplitudes far below and far above the corner."},
            {"criterion": "Corner by bisection", "weight": 35,
             "evidence": "`find_corner` returns each box's corner to within 2%, works for both the low-pass and the high-pass boxes, and locates the crossing relative to the measured pass band."},
            {"criterion": "From measurement to component", "weight": 15,
             "evidence": "`resistor_for` inverts the corner formula correctly, and the header comment records a measured corner and an implied resistance for each box."},
            {"criterion": "Robustness", "weight": 10,
             "evidence": "The bisection converges from wide bounds, does not depend on the number of samples in a capture, and gives the same answer when the search bounds are changed."},
        ],
        "hints": [
            "The RMS of one capture is all the amplitude information you need: because the capture is always a whole number of cycles, `np.sqrt(np.mean(v * v))` is exact.",
            "For `classify`, measure at 10 Hz and at 200 kHz. Whichever end is larger is the pass band, and that says which kind of filter it is.",
            "Bisect in the logarithm: the midpoint of `lo` and `hi` should be `np.sqrt(lo * hi)`, not `(lo + hi) / 2`. Sixty iterations is plenty.",
            "One bisection can serve both kinds. Work out which end is the pass band first, then at each midpoint ask whether the measurement is still above the target, and move whichever bound is on the pass-band side.",
            "Take the pass-band reading two decades outside the bracket — `f_lo / 100` for a low-pass, `f_hi * 100` for a high-pass. Reading it at the bracket edge makes the answer drift as the bracket changes, which is exactly what one of the checks looks for.",
            "`resistor_for` is the corner formula rearranged: $R = 1/(2\\pi f_c C)$.",
        ],
        "files": [
            {"name": "bench.py", "ro": True, "content": r'''
"""The sealed bench. Do not edit, and do not read the filter table.

`capture(name, f)` drives box `name` with a 1 V peak sinusoid at `f` hertz and
returns the waveform that comes out: CYCLES complete cycles, SAMPLES_PER_CYCLE
samples in each, so the array is always a whole number of periods long.

The generator produces about 5% of a third harmonic alongside the fundamental. The
box filters that harmonic too, at its own frequency, exactly as it would in reality.
"""
import numpy as np

SAMPLES_PER_CYCLE = 256
CYCLES = 8
HARMONIC = 0.05

_FILTERS = {
    "A": ("low", 1200.0),
    "B": ("high", 3400.0),
    "C": ("low", 480.0),
}

BOXES = tuple(sorted(_FILTERS))


def _gain_phase(kind, fc, f):
    x = f / fc
    h = 1.0 / (1.0 + 1j * x) if kind == "low" else (1j * x) / (1.0 + 1j * x)
    return abs(h), float(np.angle(h))


def capture(name, f):
    """One captured output waveform for a 1 V peak input at f hertz."""
    if name not in _FILTERS:
        raise KeyError("no such box: %r (try one of %s)" % (name, ", ".join(BOXES)))
    if f <= 0:
        raise ValueError("frequency must be positive")
    kind, fc = _FILTERS[name]
    n = SAMPLES_PER_CYCLE * CYCLES
    t = np.arange(n) / (SAMPLES_PER_CYCLE * float(f))
    w = 2.0 * np.pi * f
    a1, p1 = _gain_phase(kind, fc, f)
    a3, p3 = _gain_phase(kind, fc, 3.0 * f)
    return a1 * np.sin(w * t + p1) + HARMONIC * a3 * np.sin(3.0 * w * t + p3)


def sample_rate(f):
    """The rate the capture was taken at, in samples per second."""
    return SAMPLES_PER_CYCLE * float(f)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from bench import capture

# Measured corners, and the resistor each implies with a 10 nF capacitor:
#   box A -> TODO Hz, TODO ohms
#   box B -> TODO Hz, TODO ohms
#   box C -> TODO Hz, TODO ohms


def rms(v):
    """Root of the mean of the square of a captured waveform."""
    # TODO
    return 0.0


def amplitude(name, f):
    """The RMS of one capture from box `name` at frequency `f`."""
    # TODO
    return 0.0


def classify(name):
    """Return "low-pass" or "high-pass", decided by measurement."""
    # TODO: compare the amplitude far below and far above any plausible corner.
    return "unknown"


def find_corner(name, f_lo=10.0, f_hi=200000.0):
    """The -3 dB frequency in hertz, found by bisection on the measured response."""
    # TODO: pass-band level first, then bisect in the logarithm of the frequency.
    return 0.0


def resistor_for(fc, c):
    """The resistance a first-order filter of corner fc must contain, given c."""
    # TODO
    return 0.0


if __name__ == "__main__":
    for box in ("A", "B", "C"):
        fc = find_corner(box)
        print(box, classify(box), round(fc, 1), "Hz ->",
              round(resistor_for(fc, 1e-8), 1), "ohms")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from bench import capture

# Measured corners, and the resistor each implies with a 10 nF capacitor:
#   box A -> 1197.6 Hz, 13289 ohms   (low-pass)
#   box B -> 3393.2 Hz,  4690 ohms   (high-pass)
#   box C ->  479.0 Hz, 33224 ohms   (low-pass)
# All three read about 0.2% low, which is the third harmonic sitting in the
# pass-band reading and lifting the target very slightly.


def rms(v):
    """Root of the mean of the square of a captured waveform."""
    v = np.asarray(v, dtype=float)
    return float(np.sqrt(np.mean(v * v)))


def amplitude(name, f):
    """The RMS of one capture from box `name` at frequency `f`."""
    return rms(capture(name, f))


def classify(name):
    """Return "low-pass" or "high-pass", decided by measurement."""
    return "low-pass" if amplitude(name, 10.0) > amplitude(name, 200000.0) else "high-pass"


def find_corner(name, f_lo=10.0, f_hi=200000.0):
    """The -3 dB frequency in hertz, found by bisection on the measured response."""
    lo, hi = float(f_lo), float(f_hi)
    low_side_passes = amplitude(name, lo) > amplitude(name, hi)
    # Read the pass-band level two decades outside the bracket, not at its edge:
    # at the edge the response has usually already begun to sag, and the target
    # then drifts with wherever the bracket happens to start.
    band_f = lo / 100.0 if low_side_passes else hi * 100.0
    target = amplitude(name, band_f) / np.sqrt(2.0)
    for _ in range(60):
        mid = float(np.sqrt(lo * hi))
        in_band = amplitude(name, mid) > target
        if in_band == low_side_passes:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


def resistor_for(fc, c):
    """The resistance a first-order filter of corner fc must contain, given c."""
    return 1.0 / (2.0 * np.pi * float(fc) * float(c))


if __name__ == "__main__":
    for box in ("A", "B", "C"):
        fc = find_corner(box)
        print(box, classify(box), round(fc, 1), "Hz ->",
              round(resistor_for(fc, 1e-8), 1), "ohms")
'''},
        ],
        "tests": [
            {"name": "rms is computed from the samples, not from a shortcut", "code": r'''
import numpy as np
_t = np.arange(2048) / 2048.0
_sine = 3.0 * np.sin(2 * np.pi * 4 * _t)
assert abs(rms(_sine) - 3.0 / np.sqrt(2)) < 1e-9, \
    f"four whole cycles of a 3 V peak sine is 2.1213 V rms, got {rms(_sine)}"
assert abs(rms(np.full(64, 2.5)) - 2.5) < 1e-12, \
    f"a steady 2.5 V is 2.5 V rms — no sqrt(2) belongs here; got {rms(np.full(64, 2.5))}"
_sq = np.array([4.0] * 50 + [-4.0] * 50)
assert abs(rms(_sq) - 4.0) < 1e-12, f"a square wave's rms is its peak, got {rms(_sq)}"
'''},
            {"name": "amplitude reads the pass band and the stop band apart", "code": r'''
_pass = amplitude("A", 10.0)
_stop = amplitude("A", 200000.0)
assert abs(_pass - 0.7071) < 0.01, \
    f"box A passes a 1 V peak almost untouched at 10 Hz, which is 0.707 V rms; got {_pass}"
assert _stop < 0.01, f"box A should be far into its stop band at 200 kHz; got {_stop}"
'''},
            {"name": "every box is classified correctly", "code": r'''
assert classify("A") == "low-pass", f'box A passes low frequencies; classify said {classify("A")!r}'
assert classify("B") == "high-pass", f'box B passes high frequencies; classify said {classify("B")!r}'
assert classify("C") == "low-pass", f'box C passes low frequencies; classify said {classify("C")!r}'
'''},
            {"name": "the corner of the low-pass box is found", "code": r'''
_fc = find_corner("A")
assert abs(_fc - 1200.0) / 1200.0 < 0.02, \
    f"box A corners at 1200 Hz; the bisection returned {_fc:.1f} Hz"
'''},
            {"name": "the same routine finds the high-pass corner", "code": r'''
_fc = find_corner("B")
assert abs(_fc - 3400.0) / 3400.0 < 0.02, \
    f"box B corners at 3400 Hz; the bisection returned {_fc:.1f} Hz. One bisection must handle both kinds"
'''},
            {"name": "and a third box, so nothing is hard-coded", "code": r'''
_fc = find_corner("C")
assert abs(_fc - 480.0) / 480.0 < 0.02, \
    f"box C corners at 480 Hz; the bisection returned {_fc:.1f} Hz"
'''},
            {"name": "the answer does not depend on the search bounds", "code": r'''
_wide = find_corner("A", 1.0, 1000000.0)
_tight = find_corner("A", 200.0, 20000.0)
assert abs(_wide - _tight) / _tight < 0.01, \
    f"widening the bracket changed the answer: {_wide:.1f} vs {_tight:.1f} Hz"
'''},
            {"name": "the corner is where the response is 0.707 of the pass band", "code": r'''
import numpy as np
_fc = find_corner("B")
_band = amplitude("B", 200000.0)
_here = amplitude("B", _fc)
assert abs(_here / _band - 1 / np.sqrt(2)) < 0.02, \
    f"at the corner the output should be 0.707 of the pass band, measured {_here / _band:.4f}"
'''},
            {"name": "the resistor follows from the corner", "code": r'''
import numpy as np
_r = resistor_for(1200.0, 1e-8)
assert abs(_r - 13262.911924324612) < 1e-6, \
    f"R = 1/(2*pi*1200*1e-8) = 13262.9 ohms, got {_r}"
_r2 = resistor_for(find_corner("C"), 1e-8)
assert abs(_r2 - 33157.3) / 33157.3 < 0.03, \
    f"box C at 480 Hz with 10 nF implies about 33.2 kilohms, got {_r2:.1f}"
'''},
        ],
    },
}
