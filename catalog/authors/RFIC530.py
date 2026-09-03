"""RFIC530 — Mixers, PLLs and Frequency Synthesis.

Authored to the same rules as CTRL510:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; no scipy, no control or DSP packages
  * seed every RNG, and every expected value is one that was computed by running
    the reference code, never one that was assumed

Every numeric constant in a test below was produced by executing the reference
solution and copying the result.
"""

COURSE = {
    "id": "RFIC530",
    "title": "Mixers, PLLs and Frequency Synthesis",
    "band": 1,
    "level": "Expert",
    "prereqs": ["RFIC520"],
    "stack": ["Python", "NumPy"],
    "credits": 12,
    "hours": 150,
    "icon": "◈",
    "summary": (
        "A radio moves information between frequencies, and two circuits do almost all "
        "of that work: the mixer that translates a spectrum, and the phase-locked loop "
        "that decides where to translate it to. This course derives the conversion gain "
        "of a Gilbert cell from the Fourier series of its switching pair, turns a "
        "charge-pump loop into a second-order system with a natural frequency and a "
        "damping ratio, and then uses that second-order model to explain where phase "
        "noise goes — the reference multiplied up inside the loop bandwidth, the "
        "oscillator left alone outside it, and the quantisation noise a fractional-N "
        "divider adds in between."
    ),
    "outcomes": [
        "Derive the conversion gain of a switching mixer from the Fourier series of the LO, and explain why the answer is 2/π rather than 1/2.",
        "Reduce a charge-pump PLL with a resistor–capacitor filter to ω_n and ζ, and predict its overshoot and lock time from those two numbers alone.",
        "Separate the reference, divider and VCO contributions to output phase noise, and choose the loop bandwidth where their sum is smallest.",
        "Explain fractional-N resolution, why the quantisation error is high-pass shaped, and what that shaping costs at the top of the loop bandwidth.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that sizes the loop filter of a 2.4 GHz fractional-N synthesiser and defends the bandwidth it chose with an integrated-jitter number.",
    "reading": [
        "*RF Microelectronics*, Razavi — chapters 6 and 9, for the Gilbert cell and the loop.",
        "*Phaselock Techniques*, Gardner — the second-order loop, done properly.",
        "Riley, Copeland & Kwasniewski, *Delta-Sigma Modulation in Fractional-N Frequency Synthesis*, JSSC 1993 — the paper the last module is built on.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The Gilbert cell and conversion gain",
            "summary": "A mixer multiplies. A Gilbert cell multiplies by a square wave, and the Fourier series of that square wave is the whole gain calculation.",
            "concepts": [
                "The transconductance stage turns the RF voltage into a current; the switching pair steers that current; the load turns it back into a voltage.",
                "A hard-switched LO pair multiplies by ±1, not by a sinusoid — so the LO amplitude drops out of the gain entirely.",
                "The fundamental of a unit square wave has amplitude $4/\\pi$, and the product-to-sum identity halves it: conversion gain $= (2/\\pi) g_m R_L$.",
                "Every odd LO harmonic downconverts as well, with gain $2/(k\\pi)$ — which is where half-IF and harmonic-mixing problems come from.",
                "Two RF frequencies land on the same IF: the wanted signal and its image, reflected about the LO. Nothing after the mixer can separate them.",
                "Single-balanced versus double-balanced: the Gilbert cell cancels both LO and RF feedthrough at the output, leaving only the products.",
            ],
            "read": [{
                "title": "Six decibels on the schematic, two on the analyser",
                "minutes": 17,
                "body": r'''
A double-balanced Gilbert cell on a $1.8$ V supply. The tail sinks $2$ mA, so each side
of the transconductance pair runs at $1$ mA; at an overdrive of $400$ mV that is
$g_m = 2I_D/V_{ov} = 5$ mS. The load resistors are $400\ \Omega$, sized so the same
$1$ mA drops $400$ mV across them and leaves the switching pair its headroom. The LO
port is driven from a limiting buffer, hard enough that the upper devices are never both
on for long.

$g_m R_L = 2.0$. The schematic is annotated "$6$ dB", the review minutes say $6$ dB, and
with a $900$ MHz LO and a small tone at the RF port the analyser reads an IF $3.9$ dB
below that: $2.10$ dB of conversion gain.

Nothing has gone wrong. The missing $3.92$ dB was never on offer, the same $3.92$ dB is
what an ideal mixer charges the receiver in noise figure, and accounting for it is the
whole of this module.

## The upper pair is a switch, and a switch has a Fourier series

Follow the signal. The bottom pair is a small-signal transconductor: an RF voltage
$A\cos\omega_{rf}t$ at its gates becomes a current of amplitude $g_mA$ in its drains,
and so far the stage is an amplifier like any other. The upper pair does something an
amplifier does not do. Its gates see the LO, and once the LO swing exceeds a few hundred
millivolts one device has the entire tail current and the other has none. Half a period
later they exchange. The signal current is not scaled by the LO; it is *steered* by it.

Steering a current alternately into the two halves of a differential load is
multiplication by a function that is $+1$ for half the period and $-1$ for the other
half. That function is where the arithmetic lives, and the Fourier series of a $\pm1$
square wave is

$$s(t) = \frac{4}{\pi}\left(\sin\omega_{lo}t + \frac{1}{3}\sin3\omega_{lo}t
        + \frac{1}{5}\sin5\omega_{lo}t + \dots\right)$$

Two things in that line decide the answer. The fundamental has amplitude $4/\pi = 1.273$
— larger than the square wave's own peak of $1$, because the harmonics subtract near the
edges to make the corners square. And multiplying two sinusoids splits the result in
half: $\cos a\cos b = \tfrac12[\cos(a-b) + \cos(a+b)]$, and only the difference term
lands at the IF. Multiply the two factors and the load turns the current back into a
voltage:

$$G_c = \frac{4}{\pi}\cdot\frac12\cdot g_mR_L = \frac{2}{\pi}g_mR_L = 0.6366\,g_mR_L$$

$2/\pi$ is $-3.92$ dB, and it is not a defect of any implementation. It is what
translating a spectrum costs when the thing doing the translating is a switch. The
derivation unit *Conversion gain of a switching mixer* walks the same five steps and
ends by asking for the answer when the LO is too small to commutate: a unit sinusoid has
fundamental amplitude $1$, not $4/\pi$, so the gain falls to $g_mR_L/2 = 1.0$, exactly
$2.1$ dB below. That gap is the entire argument for driving the LO port hard, and it is
also why nothing is gained by driving it harder still.

```python
import math

g_m, R_L = 5e-3, 400.0            # 1 mA a side, 400 ohm of load

print(f"g_m R_L, the promise     : {g_m * R_L:6.4f} = {20 * math.log10(g_m * R_L):+7.3f} dB")
for k in (1, 3, 5, 7):
    g = 2.0 / (k * math.pi) * g_m * R_L
    print(f"  LO harmonic {k}          : {g:6.4f} = {20 * math.log10(g):+7.3f} dB")
print(f"a sinusoidal LO instead  : {g_m * R_L / 2:6.4f} = {20 * math.log10(g_m * R_L / 2):+7.3f} dB")
```

The promise is $2.0000$ and $+6.021$ dB; the fundamental delivers $1.2732$ and $+2.098$
dB; the sinusoidal LO would give $1.0000$ and $0.000$ dB.

## The $3.92$ dB is not lost. It is spread over nine other bands

The three lines under the fundamental in that output are the rest of the series, and
they are not bookkeeping. Every odd harmonic of the LO is a working mixer with
conversion gain $2/(k\pi)$: an RF signal near $3f_{lo}$ arrives at the same IF, $9.5$ dB
below the wanted one, and near $5f_{lo}$, $14$ dB below. A blocker $9.5$ dB stronger
than the wanted signal, sitting at $3f_{lo} \pm f_{if}$, reaches the IF as an equal.

Now count the power. Each odd harmonic folds *two* RF bands onto the IF — one above
$kf_{lo}$ and one below — so a source of broadband noise at the RF port is amplified by
$\sum_k 2\,(2/k\pi)^2$ over odd $k$, while the wanted single sideband is amplified by
$(2/\pi)^2$.

```python
import math

# every odd harmonic folds two bands, k*f_lo +/- f_if, onto the same IF
folded = sum(2.0 * (2.0 / (k * math.pi)) ** 2 for k in range(1, 200001, 2))
wanted = (2.0 / math.pi) ** 2
print(f"noise power gain, 100000 odd harmonics : {folded:.6f}")
print(f"wanted-signal power gain               : {wanted:.6f}")
print(f"ratio                                  : {folded / wanted:.4f}"
      f" = {10 * math.log10(folded / wanted):.3f} dB")
print(f"pi^2 / 4 and the conversion loss       : {math.pi ** 2 / 4:.4f}"
      f" = {-20 * math.log10(2.0 / math.pi):.3f} dB")
```

The noise power gain reads $0.999998$ after a hundred thousand odd harmonics, and the
limit is exactly one for a reason worth holding on to: multiplying by $\pm1$ leaves
$y^2 = x^2s^2 = x^2$ at every instant, so
the total output power equals the total input power however the spectrum was rearranged.
The wanted signal, meanwhile, keeps only $(2/\pi)^2 = 0.405285$ of its power. The ratio
is $\pi^2/4 = 2.4674$, which is $3.922$ dB — the same number as the conversion loss,
printed twice from two unrelated calculations. A perfect switching mixer, with no
resistors and no transistors and no noise of its own, has a single-sideband noise figure
of $3.922$ dB, and it has it because its signal gain is $2/\pi$ while its noise gain is
$1$.

## Priced against the receiver RFIC520 built

RFIC520's capstone front end is an LNA at $1.4$ dB and $16$ dB of gain, a mixer at
$9.0$ dB, an IF amplifier and an ADC driver, and it cascades to $1.960$ dB. Put a
perfect switching mixer in the mixer's place — $3.922$ dB of noise figure and the
$2.098$ dB of conversion gain this cell actually measured — and run Friis again.

```python
import math

CHAIN = [("LNA", 1.4, 16.0), ("mixer", 9.0, 5.0),
         ("IF amp", 4.5, 22.0), ("ADC driver", 14.0, 0.0)]


def lin(db):
    return 10.0 ** (db / 10.0)


def cascade(stages):
    F, G = 1.0, 1.0
    for _, nf, gain in stages:
        F += (lin(nf) - 1.0) / G
        G *= lin(gain)
    return 10.0 * math.log10(F)


ideal_nf = 10.0 * math.log10(math.pi ** 2 / 4.0)
perfect = [CHAIN[0], ("ideal mixer", ideal_nf, 2.098)] + CHAIN[2:]
print(f"the specified chain            : {cascade(CHAIN):.4f} dB")
print(f"with a perfect switching mixer : {cascade(perfect):.4f} dB")
print(f"mixer excess, as specified     : {(lin(9.0) - 1) / lin(16.0):.6f}")
print(f"mixer excess, perfect          : {(lin(ideal_nf) - 1) / lin(16.0):.6f}")
```

$1.9602$ dB becomes $1.6070$ dB. Two things are worth reading off that. Of the $9$ dB
the real mixer costs, $3.92$ dB is arithmetic that no design can remove and about
$5.1$ dB is implementation — switching-pair noise during the transitions, the load
resistors, and the $1/f$ noise the module-2 course showed folding up around the LO. And
replacing that real mixer with a physically impossible one buys the receiver only
$0.35$ dB, because the LNA's $16$ dB of gain has already divided the mixer's excess from
$0.1744$ down to where it competes with the LNA's own $1.4$ dB. The mixer is the second
noise contributor in the chain and it is worth less attention than its own datasheet
line suggests.

## The mistake: the filter after the mixer will sort out the image

Two RF frequencies convert to the same IF — $f_{lo} + f_{if}$ and $f_{lo} - f_{if}$ —
and the belief that the IF filter can separate them is the most expensive misconception
in receiver design, because it is discovered after the board exists. The lab for this
module, *Measure the conversion gain of a switching mixer*, settles it by measurement.
Its constants are an LO at $900$ Hz, an RF at $1000$ Hz, $g_m = 5$ mS and
$R_L = 400\ \Omega$; the code below is that lab's arithmetic in the standard library.

```python
import math

FS, N_SAMP = 20000.0, 20000       # the lab's own record: exactly one second


def lo_wave(t, f_lo, n_harm):
    """The lab's band-limited square LO: the first n_harm odd harmonics."""
    s = 0.0
    for i in range(n_harm):
        k = 2 * i + 1
        s += math.sin(2.0 * math.pi * k * f_lo * t) / k
    return (4.0 / math.pi) * s


def gain_at(f_if, f_rf, f_lo, a_rf, gm, rl, n_harm=9):
    """Amplitude at f_if of the mixer output, divided by the input amplitude."""
    c = s = 0.0
    for i in range(N_SAMP):
        t = i / FS
        y = gm * rl * a_rf * math.cos(2.0 * math.pi * f_rf * t) * lo_wave(t, f_lo, n_harm)
        c += y * math.cos(2.0 * math.pi * f_if * t)
        s += y * math.sin(2.0 * math.pi * f_if * t)
    return math.hypot(2.0 * c / N_SAMP, 2.0 * s / N_SAMP) / a_rf


wanted = gain_at(100.0, 1000.0, 900.0, 0.01, 0.005, 400.0)
image = gain_at(100.0, 800.0, 900.0, 0.01, 0.005, 400.0)
third = gain_at(100.0, 2800.0, 900.0, 0.01, 0.005, 400.0)
print(f"wanted, 100 Hz above the LO  : {wanted:.13f}")
print(f"image,  100 Hz below the LO  : {image:.13f}")
print(f"the two differ by            : {abs(wanted - image):.2e}")
print(f"RF at 3*f_lo + f_if          : {third:.13f}"
      f"  ({20 * math.log10(third / wanted):.2f} dB down)")
```

Both read $1.2732395447351$, and they differ by $2.6\times10^{-14}$ — which is the
arithmetic, not the physics. The lab's own check asserts the same equality to within
$10^{-6}$. After the multiplication the two signals occupy the same frequency and the
same bandwidth; they are one waveform. No filter, no amount of IF gain and no digital
processing downstream can undo an addition that has already happened.

It is a tempting mistake because everything else in a receiver *is* fixed later. Out-of-
band blockers, LO feedthrough, the sum product at $f_{rf}+f_{lo}$ — all of those land
somewhere the IF filter can reach. The image is the one product that lands exactly where
the wanted signal is, which is why the filter has to come *before* the mixer, and why
choosing the IF is largely a fight about how far away the image sits and how sharp a
front-end filter can be. The same block prints the third-harmonic path as
$0.4244131815784$, which is $2/(3\pi)\,g_mR_L$ and $9.54$ dB below the wanted gain: the
half-IF and harmonic-mixing spurs are the same phenomenon at higher $k$, and the lab's
last test pins that number too.

## Where the $\pm1$ model stops holding

The switching pair is not instantaneous. During the LO transition both devices conduct,
the multiplying function is trapezoidal rather than square, and its fundamental is
smaller than $4/\pi$ — a few tenths of a decibel of gain, and rather more noise, because
the overlap interval is when the pair contributes noise directly to the output. That is
the real reason more LO amplitude helps after the gain has saturated: faster edges, a
shorter overlap.

The model also has no compression. The lab's check that conversion gain is identical at
$10$ mV and $40$ mV of RF passes exactly, because $g_m$ is a constant in the code. On
silicon the transconductance pair is a differential pair, its linear range is a couple
of overdrives wide, and the gain starts falling a decibel by around $V_{ov}$ of input —
so $P_{1\text{dB}}$ and $IIP3$ are properties of the *lower* stage, which the whole
$\pm1$ picture never touches. A mixer's linearity and its conversion gain pull in
opposite directions through the same $g_m$.

Finally, the model as written is discrete-time, and that carries a limit worth knowing
before trusting a number out of it. At $f_{lo} = 900$ Hz with `n_harm = 9`, the series
runs to the $17$th harmonic at $15\,300$ Hz, well above the $10$ kHz Nyquist frequency
of a $20$ kHz record. Those components fold back. None of them lands on a bin the lab
measures, so every check it makes is sound, but move the RF tone and one can: measuring
the fundamental downconversion of a $2800$ Hz input at its own $1900$ Hz IF returns
$1.348$ rather than $1.2732$, a $0.50$ dB error contributed entirely by the aliased
$17$th harmonic. Keep $(2n_{harm}-1)f_{lo}$ below $F_S/2$ and the folding is gone.

What the model does capture completely is the IF node itself, which is where the
sandbox, *Conversion gain and the IF load*, takes over: the mixer has no frequency
response worth the name, and every corner in that plot belongs to $R_L$ working against
the capacitance hanging off the output. Raising $R_L$ raises the gain and lowers the
corner in exact proportion, so the IF node has a fixed gain–bandwidth product — one more
thing $g_mR_L$ on a schematic does not say.
'''
            }],
            "sandbox": {
                "title": "Conversion gain and the IF load",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 40, "zeta": 0.7, "K": 8},
                "brief": r'''
Read this plot as the IF side of a mixer. The frequency axis is offset from the LO,
$K$ is the conversion gain, and the corner is the pole formed by the load resistance
and the capacitance hanging off the mixer output.

The mixer itself has no frequency response worth speaking of; everything you see
here belongs to the load it drives.
''',
                "notice": [
                    "Raise $K$ alone. The whole magnitude curve lifts by $20\\log_{10}K$ and the corner does not move — conversion gain and IF bandwidth are set by different things ($g_m R_L$ against $1/R_L C_L$).",
                    "Now imagine holding $g_m$ fixed and doubling $R_L$: the gain doubles and the corner halves. The gain–bandwidth product of the IF node is fixed, which is why a high-gain mixer is a narrow one.",
                    "Drop $\\zeta$ below 0.5. The peak near the corner is what an inductively peaked IF load does — useful for extending bandwidth, and a group-delay problem for a wideband signal.",
                ],
            },
            "derive": {
                "title": "Conversion gain of a switching mixer",
                "minutes": 14,
                "vars": ["A", "g_m", "R_L", "G_c", "t", "omega_lo", "omega_rf", "omega_if", "k"],
                "brief": r'''
A Gilbert cell in three stages. The bottom pair has transconductance $g_m$ and turns
the RF voltage $A\cos(\omega_{rf} t)$ into a current. The upper pair is driven hard
by the LO, so it steers that entire current one way and then the other: a
multiplication by a square wave that alternates between $+1$ and $-1$ at
$\omega_{lo}$. The load $R_L$ turns the result back into a voltage.

Work out the amplitude of the output at the difference frequency
$\omega_{if} = \omega_{rf} - \omega_{lo}$.
''',
                "steps": [
                    {
                        "prompt": "The transconductance stage sees an input of amplitude $A$. Write the amplitude of the signal current it produces.",
                        "answer": "g_m A",
                        "hint": "Transconductance is current out per volt in, and nothing here is nonlinear yet.",
                        "deconstruct": [
                            "By definition $i = g_m v$ for a small signal.",
                            "The input amplitude is $A$, so the current amplitude is $g_m A$.",
                        ],
                    },
                    {
                        "prompt": "The switching pair multiplies that current by a square wave of $\\pm 1$. Write the amplitude of the fundamental component of a unit square wave.",
                        "answer": "\\frac{4}{\\pi}",
                        "hint": "The Fourier series of a $\\pm 1$ square wave is $\\frac{4}{\\pi}\\left(\\sin\\theta + \\frac{1}{3}\\sin 3\\theta + \\dots\\right)$.",
                        "deconstruct": [
                            "The square wave is odd, so only sine terms survive and only odd harmonics.",
                            "The first coefficient works out to $4/\\pi \\approx 1.273$ — larger than the square wave's own peak of 1, because the higher harmonics subtract near the edges.",
                        ],
                    },
                    {
                        "prompt": "Multiplying two tones splits the product into a sum and a difference term, each carrying half the amplitude. Write the amplitude of the current at $\\omega_{if}$.",
                        "given": "You have a current of amplitude $g_m A$ multiplied by a fundamental of amplitude $\\frac{4}{\\pi}$.",
                        "answer": "\\frac{2 g_m A}{\\pi}",
                        "hint": "Multiply the two amplitudes, then halve the result.",
                        "deconstruct": [
                            "The product amplitude is $\\frac{4}{\\pi} g_m A$.",
                            "The identity $\\cos a \\cos b = \\frac{1}{2}\\left(\\cos(a-b) + \\cos(a+b)\\right)$ puts half of it at the difference frequency.",
                        ],
                    },
                    {
                        "prompt": "That current flows in the load $R_L$. Write the voltage conversion gain $G_c$ — output amplitude at $\\omega_{if}$ divided by input amplitude at $\\omega_{rf}$.",
                        "answer": "\\frac{2 g_m R_L}{\\pi}",
                        "hint": "Ohm's law, then divide by $A$ — which cancels.",
                        "deconstruct": [
                            "The output amplitude is $\\frac{2 g_m A}{\\pi} R_L$.",
                            "Dividing by $A$ removes the input amplitude, as a gain must.",
                        ],
                    },
                    {
                        "prompt": "Suppose the LO were too small to switch the pair hard, so the upper stage multiplied by a *sinusoid* of unit amplitude instead. Write the conversion gain in that case.",
                        "answer": "\\frac{g_m R_L}{2}",
                        "hint": "Repeat the last two steps with a fundamental amplitude of 1 instead of $\\frac{4}{\\pi}$.",
                        "deconstruct": [
                            "A unit sinusoid has fundamental amplitude 1, not $4/\\pi$.",
                            "Halving for the difference term leaves $g_m R_L / 2$.",
                        ],
                    },
                ],
                "closing": r'''
The two answers differ by $4/\pi$, about 2.1 dB, and that is the entire argument for
driving the LO port hard. It also explains why conversion gain is insensitive to LO
amplitude once the pair is switching: past that point, more LO buys nothing but
more LO leakage.

Notice what never appeared: any statement about the LO frequency. Every odd
harmonic of the square wave downconverts too, with gain $2/(k\pi)$ — the lab measures
that directly.
''',
            },
            "quiz": {
                "title": "A mixer multiplies by a square wave",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A hard-driven LO switching pair multiplies the signal by what?",
                        "opts": [
                            "A square wave alternating between $+1$ and $-1$",
                            "A sinusoid at the LO frequency",
                            "The LO voltage itself",
                            "A constant",
                        ],
                        "a": 0,
                        "why": r"""
Once the LO is large enough to fully commutate the pair, the switching is
all-or-nothing and the signal current is simply steered one way then the other. That is
multiplication by $\pm1$ — and it explains the most useful practical property of the
topology, which is the next question.
""",
                    },
                    {
                        "q": "What is the fundamental amplitude of a unit square wave?",
                        "opts": ["$4/\\pi$", "$1$", "$\\pi/4$", "$2/\\pi$"],
                        "a": 0,
                        "why": r"""
$4/\pi = 1.273$ — the fundamental of a $\pm1$ square wave is *larger* than the square
wave's own amplitude, which is worth pausing on and is exactly what the Fourier series
says. It also means only $8/\pi^2 = 0.811$ of the energy is at the fundamental and the
rest sits at odd harmonics, each of which is another band the mixer will happily downconvert.
""",
                    },
                    {
                        "q": "What is the single-sideband conversion gain of a single-balanced cell, relative to the transconductance stage's gain?",
                        "opts": [
                            "$2/\\pi$",
                            "$4/\\pi$",
                            "$1/2$",
                            "$\\pi/2$",
                        ],
                        "a": 0,
                        "why": r"""
$4/\pi$ from the square wave's fundamental, times $1/2$ because multiplying two sinusoids
splits the energy into a sum and a difference and you keep one — giving $2/\pi = 0.64$,
or $-3.9$ dB. That loss is intrinsic to the multiplication and not a defect of the
implementation, which is why a mixer's gain is quoted separately from the stage's and why
the LNA in front of it matters so much.
""",
                    },
                    {
                        "q": "Once the LO is large enough to fully switch the pair, what does increasing it further do to the conversion gain?",
                        "opts": [
                            "Nothing",
                            "Increases it proportionally",
                            "Decreases it",
                            "Increases it as the square root",
                        ],
                        "a": 0,
                        "why": r"""
The multiplication is by $\pm1$ regardless of how hard you drive it, so the gain
saturates — which is a considerable practical virtue, since LO amplitude then does not
have to be controlled precisely. What more LO *does* buy is faster switching edges, which
shortens the interval when both devices conduct and reduces noise; and what it costs is
power and LO leakage. Below full commutation the gain does depend on amplitude, and the
mixer is noisier there.
""",
                    },
                    {
                        "q": "What does the double-balanced (full Gilbert) cell add over the single-balanced one?",
                        "opts": [
                            "Rejection of both LO and RF feedthrough at the output",
                            "Higher conversion gain",
                            "Lower noise figure",
                            "Wider bandwidth",
                        ],
                        "a": 0,
                        "why": r"""
Both the LO and the RF appear as common-mode at the differential output and cancel,
leaving the wanted product. It matters enormously in a direct-conversion receiver, where
LO leakage back out of the antenna is a regulatory problem and self-mixing produces a DC
offset that can swamp the signal. The gain is the same, the noise is generally slightly
worse, and it costs another pair of devices and more headroom.
""",
                    },
                ],
            },
            "lab": {
                "title": "Measure the conversion gain of a switching mixer",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
Build the mixer in the time domain and measure what you derived.

`lo_wave(t, f_lo, n_harm)` returns the LO waveform as the sum of the first `n_harm`
odd harmonics of a unit square wave:

```text
(4/pi) * ( sin(w t) + sin(3 w t)/3 + sin(5 w t)/5 + ... )
```

Building it from the series rather than from `np.sign` matters: a hard-switched
square wave sampled at a finite rate carries harmonics above Nyquist, and those
aliases mix down onto the IF and corrupt the very number you are measuring.

`mixer_output(t, f_rf, f_lo, a_rf, gm, rl, n_harm)` multiplies an RF cosine of
amplitude `a_rf` by that LO and scales by `gm * rl`.

`tone_amplitude(x, t, f)` returns the amplitude of the component of `x` at
frequency `f`, by projecting onto a cosine and a sine and taking the magnitude:
`2*mean(x*cos)` and `2*mean(x*sin)`.

`conversion_gain(f_rf, f_lo, a_rf, gm, rl, n_harm)` builds the record, measures the
component at `abs(f_rf - f_lo)`, and divides by `a_rf`.

`FS` and `N_SAMP` give exactly one second of data at 20 kHz, so every frequency the
checks use is a whole number of cycles in the record. Leave them alone — the
projection is only exact because of it.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

FS = 20000.0      # sample rate, Hz
N_SAMP = 20000    # exactly one second, so every test tone is coherent


def lo_wave(t, f_lo, n_harm=5):
    """A band-limited square LO: the first n_harm odd harmonics, amplitude 4/pi."""
    t = np.asarray(t, dtype=float)
    # TODO: sum sin(2*pi*k*f_lo*t)/k over odd k, then scale by 4/pi.
    return np.zeros_like(t)


def mixer_output(t, f_rf, f_lo, a_rf, gm, rl, n_harm=5):
    """The IF voltage: an RF cosine multiplied by the LO, scaled by gm*rl."""
    t = np.asarray(t, dtype=float)
    # TODO
    return np.zeros_like(t)


def tone_amplitude(x, t, f):
    """Amplitude of the component of x at frequency f, by projection."""
    x = np.asarray(x, dtype=float)
    t = np.asarray(t, dtype=float)
    # TODO: project onto cos and sin, then take the magnitude.
    return 0.0


def conversion_gain(f_rf, f_lo, a_rf, gm, rl, n_harm=5):
    """Output amplitude at |f_rf - f_lo| divided by the input amplitude."""
    t = np.arange(N_SAMP) / FS
    # TODO
    return 0.0


if __name__ == "__main__":
    t = np.arange(N_SAMP) / FS
    print("LO fundamental:", round(tone_amplitude(lo_wave(t, 900.0, 9), t, 900.0), 6))
    print("conversion gain:", round(conversion_gain(1000.0, 900.0, 0.01, 1.0, 1.0, 9), 6))
    print("2/pi =", round(2.0 / np.pi, 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

FS = 20000.0      # sample rate, Hz
N_SAMP = 20000    # exactly one second, so every test tone is coherent


def lo_wave(t, f_lo, n_harm=5):
    """A band-limited square LO: the first n_harm odd harmonics, amplitude 4/pi."""
    t = np.asarray(t, dtype=float)
    out = np.zeros_like(t)
    for i in range(int(n_harm)):
        k = 2 * i + 1
        out = out + np.sin(2.0 * np.pi * k * f_lo * t) / k
    return (4.0 / np.pi) * out


def mixer_output(t, f_rf, f_lo, a_rf, gm, rl, n_harm=5):
    """The IF voltage: an RF cosine multiplied by the LO, scaled by gm*rl."""
    t = np.asarray(t, dtype=float)
    rf = a_rf * np.cos(2.0 * np.pi * f_rf * t)
    return gm * rl * rf * lo_wave(t, f_lo, n_harm)


def tone_amplitude(x, t, f):
    """Amplitude of the component of x at frequency f, by projection."""
    x = np.asarray(x, dtype=float)
    t = np.asarray(t, dtype=float)
    c = 2.0 * np.mean(x * np.cos(2.0 * np.pi * f * t))
    s = 2.0 * np.mean(x * np.sin(2.0 * np.pi * f * t))
    return float(np.hypot(c, s))


def conversion_gain(f_rf, f_lo, a_rf, gm, rl, n_harm=5):
    """Output amplitude at |f_rf - f_lo| divided by the input amplitude."""
    t = np.arange(N_SAMP) / FS
    y = mixer_output(t, f_rf, f_lo, a_rf, gm, rl, n_harm)
    return float(tone_amplitude(y, t, abs(f_rf - f_lo)) / a_rf)


if __name__ == "__main__":
    t = np.arange(N_SAMP) / FS
    print("LO fundamental:", round(tone_amplitude(lo_wave(t, 900.0, 9), t, 900.0), 6))
    print("conversion gain:", round(conversion_gain(1000.0, 900.0, 0.01, 1.0, 1.0, 9), 6))
    print("2/pi =", round(2.0 / np.pi, 6))
'''}],
                "hints": [
                    "The odd harmonics are `k = 1, 3, 5, ...`, so `k = 2*i + 1` for `i` in `range(n_harm)`.",
                    "`tone_amplitude` needs both projections: a signal at the right frequency but the wrong phase projects to zero on the cosine alone.",
                    "`np.hypot(c, s)` is the magnitude of the two projections, and it is what makes the measurement phase-blind.",
                    "`conversion_gain` divides by `a_rf`, so the number it returns should not change when you change the input amplitude.",
                ],
                "tests": [
                    {"name": "the LO fundamental carries four over pi", "code": r'''
import numpy as np
_t = np.arange(N_SAMP) / FS
_w = lo_wave(_t, 900.0, 9)
_a = tone_amplitude(_w, _t, 900.0)
assert abs(_a - 4.0 / np.pi) < 1e-6, \
    f"the fundamental of a unit square wave has amplitude 4/pi = 1.2732, got {_a:.6f}"
'''},
                    {"name": "the third harmonic is one third the size", "code": r'''
import numpy as np
_t = np.arange(N_SAMP) / FS
_w = lo_wave(_t, 900.0, 9)
_a = tone_amplitude(_w, _t, 2700.0)
assert abs(_a - 4.0 / (3.0 * np.pi)) < 1e-6, \
    f"the k-th harmonic has amplitude 4/(k*pi), so 0.4244 at 3f, got {_a:.6f}"
'''},
                    {"name": "the projection recovers a known amplitude", "code": r'''
import numpy as np
_t = np.arange(N_SAMP) / FS
_x = 0.3 * np.cos(2.0 * np.pi * 100.0 * _t + 1.1)
_a = tone_amplitude(_x, _t, 100.0)
assert abs(_a - 0.3) < 1e-9, \
    f"amplitude must come out as 0.3 whatever the phase; got {_a:.9f} — project onto both cos and sin"
'''},
                    {"name": "the switching mixer converts with a gain of two over pi", "code": r'''
import numpy as np
_g = conversion_gain(1000.0, 900.0, 0.01, 1.0, 1.0, 9)
assert abs(_g - 0.6366197723675814) < 1e-6, \
    f"with gm*rl = 1 the conversion gain is 2/pi = 0.63662, not 1/2; got {_g:.6f}"
'''},
                    {"name": "gain scales with transconductance and load", "code": r'''
_g = conversion_gain(1000.0, 900.0, 0.01, 0.005, 400.0, 9)
assert abs(_g - 1.2732395447351657) < 1e-6, \
    f"expected (2/pi)*gm*rl = (2/pi)*0.005*400 = 1.27324, got {_g:.6f}"
_g2 = conversion_gain(1000.0, 900.0, 0.01, 0.005, 800.0, 9)
assert abs(_g2 - 2.0 * _g) < 1e-6, \
    "doubling the load resistance must double the conversion gain exactly"
'''},
                    {"name": "gain does not depend on the input amplitude", "code": r'''
_a = conversion_gain(1000.0, 900.0, 0.01, 0.005, 400.0, 9)
_b = conversion_gain(1000.0, 900.0, 0.04, 0.005, 400.0, 9)
assert _a > 0.1, f"the gain should be about 1.273 before this comparison means anything, got {_a:.6f}"
assert abs(_a - _b) < 1e-9, \
    f"a gain is a ratio: {_a:.6f} at 10 mV should equal {_b:.6f} at 40 mV"
'''},
                    {"name": "the image lands on the same IF", "code": r'''
_wanted = conversion_gain(1000.0, 900.0, 0.01, 0.005, 400.0, 9)
_image = conversion_gain(800.0, 900.0, 0.01, 0.005, 400.0, 9)
assert _image > 0.1, \
    f"the image should convert with a gain of about 1.273, not vanish; got {_image:.6f}"
assert abs(_wanted - _image) < 1e-6, \
    ("100 kHz above the LO and 100 kHz below it convert with the same gain — "
     f"got {_wanted:.6f} and {_image:.6f}. That is why an image-reject filter comes first.")
'''},
                    {"name": "the third LO harmonic downconverts as well", "code": r'''
import numpy as np
_t = np.arange(N_SAMP) / FS
_y = mixer_output(_t, 2800.0, 900.0, 0.01, 1.0, 1.0, 9)
_g = tone_amplitude(_y, _t, 100.0) / 0.01
assert abs(_g - 0.2122065907891931) < 1e-6, \
    f"RF at 3*f_lo + f_if reaches the IF with gain 2/(3*pi) = 0.21221, got {_g:.6f}"
_y1 = mixer_output(_t, 2800.0, 900.0, 0.01, 1.0, 1.0, 1)
_g1 = tone_amplitude(_y1, _t, 100.0) / 0.01
assert _g1 < 1e-9, \
    f"with only the fundamental in the LO there is no third-harmonic path; got {_g1:.3e}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "The charge-pump PLL as a second-order system",
            "summary": "A phase detector, an integrator and a VCO make two poles at the origin. One resistor is what stops the loop ringing forever.",
            "concepts": [
                "The charge pump delivers an average current $I_{cp}\\theta_e / 2\\pi$, so its gain is $I_{cp}/2\\pi$ amperes per radian.",
                "The VCO integrates: control voltage sets frequency, and phase is the integral of frequency, so its transfer is $K_{vco}/s$.",
                "Two integrators in the loop means a type-II system — zero steady-state phase error, and no stability at all without a zero.",
                "The series resistor in the loop filter is that zero. It contributes the entire damping term.",
                "$\\omega_n = \\sqrt{I_{cp}K_{vco}/2\\pi N C}$ and $\\zeta = (R/2)\\omega_n C$ — every design decision reduces to those two numbers.",
                "Overshoot in the phase step response is frequency overshoot in the hop: a synthesiser that rings is a synthesiser that fails its settling mask.",
            ],
            "read": [{
                "title": "Four times the pump current, and the loop locks slower",
                "minutes": 18,
                "body": r'''
Five numbers, and they are the ones the lab for this module uses. A charge pump that
sources $1$ mA. A VCO that tunes at $30$ MHz per volt, so
$K_{vco} = 2\pi\times30\times10^6$ rad/s/V. A divide ratio of $100$. A loop filter of
$R = 1.5\ \text{k}\Omega$ in series with $C = 3$ nF.

Those five give a natural frequency of $316\,228$ rad/s — $50.33$ kHz — and a damping
ratio of $0.7115$. Hop the divide ratio and the output frequency settles inside a
$5\%$ window in $9.32\ \mu\text{s}$. The specification says $5\ \mu\text{s}$.

The move everyone reaches for first is more pump current: $\omega_n$ goes as
$\sqrt{I_{cp}}$, so four times the current doubles it, and lock time goes as
$1/\omega_n$. Four milliamps, and the loop settles in $12.25\ \mu\text{s}$. It is
slower.

## Two integrators, and the resistor that rescues them

Build the loop gain block by block and the reason will be in the algebra.

The phase–frequency detector and pump together turn a phase error into an average
current. For an error $\theta_e$ the pump is on for a fraction $\theta_e/2\pi$ of each
reference period, so the average is $I_{cp}\theta_e/2\pi$ and the gain is
$I_{cp}/2\pi$ amperes per radian. That current flows into the filter impedance
$Z(s) = R + 1/sC$, making a voltage. The VCO turns voltage into *frequency*, and phase
is the integral of frequency, so it is $K_{vco}/s$. The divider contributes $1/N$.
Multiply:

$$T(s) = \frac{I_{cp}}{2\pi}\left(R + \frac{1}{sC}\right)\frac{K_{vco}}{Ns}
       = \frac{I_{cp}K_{vco}}{2\pi N}\cdot\frac{sRC + 1}{s^2C}$$

Count the poles at the origin: one from the capacitor and one from the VCO. That is a
type-II loop, and a type-II loop has zero steady-state phase error — set $s\to0$ and the
gain is infinite, so any constant error is driven out. It also has $-180°$ of phase from
those two integrators alone and therefore no margin whatsoever. The only thing standing
between this loop and an oscillator is the $sRC + 1$ in the numerator, which is the
resistor.

Set $1 + T(s) = 0$, clear denominators, and the characteristic polynomial is

$$s^2 + \frac{I_{cp}K_{vco}R}{2\pi N}s + \frac{I_{cp}K_{vco}}{2\pi NC} = 0$$

Compare it with $s^2 + 2\zeta\omega_ns + \omega_n^2$ and both design numbers fall out:

$$\omega_n = \sqrt{\frac{I_{cp}K_{vco}}{2\pi NC}}, \qquad
  \zeta = \frac{R}{2}\,\omega_n C = \frac{R}{2}\sqrt{\frac{I_{cp}K_{vco}C}{2\pi N}}$$

The derivation unit *From charge pump and filter to omega_n and zeta* walks those five
steps one at a time. Read the two results side by side and the opening paradox is
already visible: $I_{cp}$ appears under a square root in **both**. Raising the pump
current does not move $\omega_n$ and leave $\zeta$ alone; it moves them together.

## What raising the pump current actually buys

The lab, *Loop parameters, overshoot and lock time*, holds all four of these functions.
Here they are in the standard library, on the lab's own constants.

```python
import math

TWO_PI = 2.0 * math.pi


def loop_params(icp, kvco, n_div, r, c):
    """The lab's own two lines: wn from the constant term, zeta from the s term."""
    wn = math.sqrt(icp * kvco / (TWO_PI * n_div * c))
    return wn, 0.5 * r * wn * c


def step_response(wn, zeta, dt, steps):
    y = v = 0.0
    out = []
    for _ in range(steps):
        out.append(y)
        a = wn * wn * (1.0 - y) - 2.0 * zeta * wn * v
        y += dt * v
        v += dt * a
    return out


def overshoot(ys):
    final = ys[-1]
    return max(0.0, (max(ys) - final) / final)


def lock_time(ys, dt, tol=0.05):
    final, last = ys[-1], 0
    for i, y in enumerate(ys):
        if abs(y - final) > tol * abs(final):
            last = i
    return (last + 1) * dt


for icp, r in ((1e-3, 1500.0), (4e-3, 1500.0), (4e-3, 750.0)):
    wn, zeta = loop_params(icp, TWO_PI * 30e6, 100.0, r, 3e-9)
    ys = step_response(1.0, zeta, 1e-3, 60000)
    t = lock_time(ys, 1e-3)
    print(f"I_cp {icp * 1e3:.0f} mA, R {r:6.0f} ohm : wn {wn / TWO_PI / 1e3:7.3f} kHz  "
          f"zeta {zeta:.4f}  overshoot {overshoot(ys) * 100:5.2f}%  "
          f"lock {t:6.3f}/wn = {t / wn * 1e6:6.3f} us")
```

The first line is the design as specified: $50.329$ kHz, $\zeta = 0.7115$, $4.16\%$
overshoot, $2.948/\omega_n$ and $9.322\ \mu\text{s}$. The second is four times the
current with nothing else touched: $\omega_n$ has indeed doubled to $100.658$ kHz, but
$\zeta$ has doubled too, to $1.4230$. The response no longer overshoots at all, and it
takes $7.745/\omega_n$ to settle rather than $2.948$ — a factor of $2.63$ in normalised
time against a factor of $2$ in $\omega_n$. Net result $12.246\ \mu\text{s}$, which is
$31\%$ worse than the $9.322$ it started from, and $2.5$ times the specification.

The third line is the fix, and it is one component. Halve $R$ to $750\ \Omega$ and
$\zeta$ returns to $0.7115$ while $\omega_n$ stays doubled: $4.661\ \mu\text{s}$,
exactly half. The pump current was never the wrong lever, but pulling it alone changes
two things and one of them undoes the other. The lab's second test pins the same pair of
numbers — $632\,455.5$ rad/s and $\zeta = 1.4230$ — precisely so this cannot be
discovered by accident later.

## Where $\zeta \approx 0.7$ comes from, and what it is worth

The value $0.707$ is quoted so often it sounds like a constant of nature. It is not; it
is the answer to a question about the *tolerance window*, and changing the window
changes the answer.

```python
import math


def step_response(zeta, dt, steps):
    """The lab's normalised response, wn = 1."""
    y = v = 0.0
    out = []
    for _ in range(steps):
        out.append(y)
        a = (1.0 - y) - 2.0 * zeta * v
        y += dt * v
        v += dt * a
    return out


def settle(ys, dt, tol):
    final, last = ys[-1], 0
    for i, y in enumerate(ys):
        if abs(y - final) > tol * abs(final):
            last = i
    return (last + 1) * dt


for z in (0.60, 0.69, 0.70, 0.7115, 0.77, 0.78, 1.00, 1.4230):
    ys = step_response(z, 1e-3, 60000)
    os_ = math.exp(-math.pi * z / math.sqrt(1 - z * z)) if z < 1 else 0.0
    print(f"zeta {z:.4f}: overshoot {os_ * 100:6.2f}%   "
          f"5% settling {settle(ys, 1e-3, 0.05):7.3f}/wn   "
          f"2% settling {settle(ys, 1e-3, 0.02):7.3f}/wn")
for tol in (0.05, 0.02):
    z = 1.0 / math.sqrt(1.0 + (math.pi / math.log(1.0 / tol)) ** 2)
    print(f"overshoot equals {tol * 100:.0f}% exactly at zeta = {z:.4f}")
```

Look at what the $5\%$ column does between $\zeta = 0.69$ and $\zeta = 0.70$: it falls
from $4.418/\omega_n$ to $2.899/\omega_n$, a third of the settling time gone for a
hundredth of damping. Nothing about the response changed by a third. What changed is
that the *overshoot crossed the window*. Below $\zeta = 0.6901$ — where
$e^{-\pi\zeta/\sqrt{1-\zeta^2}} = 0.05$ exactly — the first peak pokes out of the $5\%$
band, so the loop enters the window, leaves it again, and only settles on the way down
from the peak. Above it the peak fits inside and the response never leaves once it has
arrived.

That is the whole of the $0.707$ folklore. It is not a resonance condition and it is not
a phase-margin optimum: it is the smallest damping at which the first overshoot fits
inside a $5\%$ mask, with a little margin. Change the mask to $2\%$ and the same
argument gives $\zeta = 0.7797$, and the table confirms it — the $2\%$ column falls from
$5.477$ to $3.603$ between $0.77$ and $0.78$. A synthesiser specified against a tight
mask wants more damping than the textbook number, and paying for the extra damping with
$R$ costs nothing at all, whereas paying for it with $I_{cp}$ costs power and moves
$\omega_n$ as well.

The sandbox, *Damping, ringing and lock time*, is the same result as a picture: at
$\zeta = 0.1$ the frequency enters the tolerance window and leaves it again several
times, and it is the *peak*, not the average approach, that decides when the hop is
declared complete.

## The loop filter is an impedance, and its middle is the margin

The build exercise, *The loop filter, driven by the charge pump itself*, makes the point
physically: push $1$ mA into the filter and the control voltage in volts is the
impedance in kilohms. Its values are $C_2 = 100$ nF in series with $R_2 = 1$ k$\Omega$,
and $C_1 = 10$ nF straight to ground.

```python
import cmath
import math

R2, C1, C2 = 1000.0, 10e-9, 100e-9
TWO_PI = 2.0 * math.pi


def z_filter(f):
    s = 2j * math.pi * f
    series = R2 + 1.0 / (s * C2)
    shunt = 1.0 / (s * C1)
    return series * shunt / (series + shunt)


print(f"zero  1/(2 pi R2 C2)        : {1 / (TWO_PI * R2 * C2):9.1f} Hz")
print(f"pole  1/(2 pi R2 (C1||C2))  : {1 / (TWO_PI * R2 * C1 * C2 / (C1 + C2)):9.1f} Hz")
for f in (100.0, 1000.0, 5000.0, 200e3):
    z = z_filter(f)
    print(f"  {f:8.0f} Hz : |Z| {abs(z) / 1e3:8.4f} kohm   phase "
          f"{math.degrees(cmath.phase(z)):7.2f} deg")
```

At $100$ Hz the impedance is $14.50$ k$\Omega$ at $-86.73°$: two capacitors in parallel,
integrating, and that integration is what makes the loop type II. At $5$ kHz it is
$0.9174$ k$\Omega$ at $-33.60°$ — $R_2$ has taken over and dragged the phase back by
more than fifty degrees. **That recovered phase is the loop's entire margin**, and the
shelf is where the loop bandwidth belongs. Notice the shelf reaches only $0.917$ of
$R_2$ rather than $1.000$: the zero at $1591.5$ Hz and the pole at $17\,507$ Hz sit a
decade apart, and neither has finished before the other starts. At $200$ kHz the phase
has fallen back to $-85.45°$, which is $C_1$ shorting out the ripple that would
otherwise appear across $R_2$ as reference spurs on the tuning line.

## The named mistake, and a second-order model that is not the loop

The mistake priced above is worth naming plainly: **treating $\omega_n$ and $\zeta$ as
independent knobs**. It is tempting because that is exactly how they behave in the
sandbox, where two sliders move two numbers, and because the notation encourages it —
they are written as separate symbols in the standard form. In a charge-pump PLL they
share $I_{cp}$, $K_{vco}$, $N$ and $C$, and only $R$ moves one without the other. Every
channel change moves both as well, since $N$ sits in a denominator of each: hop from
$N = 100$ to $N = 400$ and $\omega_n$ halves while $\zeta$ halves too, which is why a
synthesiser is designed at its worst-case divide ratio rather than its typical one.

There is a second thing the model does not say, and it matters more than it looks. The
step response that the sandbox draws and the lab integrates is
$\omega_n^2/(s^2 + 2\zeta\omega_ns + \omega_n^2)$ — the textbook prototype. The actual
closed-loop transfer of this type-II loop carries the loop filter's zero in its
numerator, $(2\zeta\omega_ns + \omega_n^2)$ over the same denominator, and a zero in the
numerator makes a response overshoot far more.

```python
import math


def prototype(zeta, dt, steps):
    """What the sandbox draws and the lab integrates: no zero."""
    y = v = 0.0
    out = []
    for _ in range(steps):
        out.append(y)
        a = (1.0 - y) - 2.0 * zeta * v
        y += dt * v
        v += dt * a
    return out


def type_two(zeta, dt, steps):
    """The real closed loop: (2 zeta s + 1)/(s^2 + 2 zeta s + 1), wn = 1."""
    x1 = x2 = 0.0
    out = []
    for _ in range(steps):
        out.append(x1 + 2.0 * zeta * x2)
        d1, d2 = x2, -x1 - 2.0 * zeta * x2 + 1.0
        x1 += dt * d1
        x2 += dt * d2
    return out


def peak(ys):
    return (max(ys) - ys[-1]) / ys[-1] * 100.0


for z in (0.5, 0.7071, 0.7115, 1.4230):
    print(f"zeta {z:.4f}: prototype overshoot {peak(prototype(z, 1e-3, 60000)):6.2f}%   "
          f"with the loop-filter zero {peak(type_two(z, 1e-3, 60000)):6.2f}%")
```

At the design point, $4.16\%$ becomes $20.66\%$ — five times as much — and even
$\zeta = 1.423$, which the prototype says cannot overshoot at all, still peaks $8.20\%$
above target. The prototype is the right object for learning how $\zeta$ and $\omega_n$
shape a response, and it is what the sandbox and lab use; the capstone switches to the
exact form, where $|H_{ref}|$ peaks at $73.49$ against a divide ratio of $60$ at
$\zeta = 0.707$. Carry the prototype's *shapes* forward and the exact transfer's
*numbers*.

## Where it stops holding

The loop is not continuous. The phase detector delivers one correction per reference
cycle, so everything above assumes $\omega_n$ is far below $\omega_{ref}$; Gardner's
stability limit puts the ceiling near $\omega_{ref}/10$, and above it the sampled loop
goes unstable at a damping the continuous model calls comfortable. The second-order form
also omits $C_1$ entirely, so it has no ripple rejection and cannot predict a reference
spur. And none of it describes acquisition: before lock, the phase–frequency detector is
running its non-linear frequency-pull mode and the linear model has nothing to say
about how long that takes.
'''
            }],
            "quiz": {
                "title": "Two numbers, and neither moves alone",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A loop is built with $I_{cp} = 1$ mA, $R = 1.5\\ \\text{k}\\Omega$ and $C = 3$ nF, and it settles too slowly. The pump current is raised to 4 mA and nothing else is touched. What happens to the 5% lock time?",
                        "opts": [
                            "It gets worse: $\\zeta$ doubles as well and the loop goes overdamped",
                            "It halves, because $\\omega_n$ doubles and lock time goes as $1/\\omega_n$",
                            "It is unchanged, because $I_{cp}$ cancels out of the closed-loop poles",
                            "It halves, and the extra ringing then adds most of the saving back",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\omega_n$ does double, to $632\,456$ rad/s, but $\zeta$ goes from $0.7115$ to $1.4230$ and the normalised settling time rises from $2.948/\omega_n$ to $7.745/\omega_n$. The net is $12.25\ \mu\text{s}$ against $9.32$ — a third worse. Halving $R$ to $750\ \Omega$ restores $\zeta$ and delivers the $4.66\ \mu\text{s}$ that was wanted.",
                            r"This is right about $\omega_n$ and silent about $\zeta$, which is the whole trap: both expressions carry $\sqrt{I_{cp}}$, so the damping doubles at the same time and costs more in normalised time than the frequency gained.",
                            r"$I_{cp}$ is inside both $\omega_n$ and $\zeta$ and cancels from neither. The place it genuinely does cancel is the *ratio* $R\omega_nC/2$ written in terms of $\omega_n$ — which is why $R$ is the knob that moves damping alone.",
                            r"There is no extra ringing: at $\zeta = 1.4230$ the poles are real and the response cannot overshoot at all. The loss comes from an overdamped approach being slow, not from oscillation.",
                        ],
                        "why": r'''
Both $\omega_n = \sqrt{I_{cp}K_{vco}/2\pi NC}$ and $\zeta = (R/2)\sqrt{I_{cp}K_{vco}C/2\pi N}$
carry $\sqrt{I_{cp}}$, so the pump current is not a bandwidth knob — it is a knob that
moves the bandwidth and the damping together. Four times the current doubles both, and
the settling time at $\zeta = 1.4230$ is $7.745/\omega_n$ against $2.948$ at $0.7115$.
The resistor is the only component that changes damping on its own.
''',
                    },
                    {
                        "q": "Take the series resistor out of the loop filter, leaving the capacitor alone. What does the loop do?",
                        "opts": [
                            "It oscillates: $\\zeta$ falls to zero and both poles reach the axis",
                            "It locks with no phase error at all, and settles more slowly",
                            "It stops integrating, so a constant phase error survives in lock",
                            "It locks, but the control node acquires a large ripple at $f_{ref}$",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\zeta = (R/2)\omega_nC$ is proportional to $R$, so removing the resistor sets the damping to exactly zero. The two poles land on the imaginary axis at $\pm j\omega_n$ and the loop rings at constant amplitude for ever, which is an oscillator rather than a synthesiser.",
                            r"The zero steady-state error is right — it is a type-II loop either way — but there is no settling to be slower or faster about, because with $\zeta = 0$ the response never settles at all.",
                            r"Backwards. The capacitor is the integrator, and it is still there; what leaves with the resistor is the zero, which supplied the phase lead. Zero steady-state error survives and stability does not.",
                            r"Ripple is what the shunt capacitor $C_1$ deals with and it is a separate concern. Removing $R$ actually *reduces* the ripple, because the pump's current pulses no longer drop across a resistance — and it destroys the loop while doing so.",
                        ],
                        "why": r'''
Two integrators — the filter capacitor and the VCO — give $-180°$ of phase and no margin
whatsoever. The resistor contributes the zero $sRC + 1$ whose phase lead is the entire
damping term: $\zeta = (R/2)\omega_nC$. With $R = 0$ the characteristic polynomial is
$s^2 + \omega_n^2$, the poles sit exactly on the imaginary axis, and the loop rings
without decaying. Everything a real loop filter's middle region does is this.
''',
                    },
                    {
                        "q": "Why do charge-pump PLL designs so often sit at $\\zeta \\approx 0.7$?",
                        "opts": [
                            "It is the least damping whose first peak fits a 5% mask",
                            "It is where two closed-loop poles become real and equal",
                            "It is the damping that gives the loop its largest phase margin",
                            "It is where the closed-loop noise peak at $\\omega_n$ vanishes",
                        ],
                        "a": 0,
                        "whys": [
                            r"$e^{-\pi\zeta/\sqrt{1-\zeta^2}} = 0.05$ at $\zeta = 0.6901$, and the $5\%$ settling time falls off a cliff there — $4.418/\omega_n$ at $\zeta = 0.69$ against $2.899$ at $0.70$. Specify a $2\%$ mask instead and the same argument moves the answer to $0.7797$, which is why the number is not universal.",
                            r"That is critical damping, and it happens at $\zeta = 1$ exactly. It gives no overshoot and a settling time of $4.742/\omega_n$ — considerably slower than $0.7$, which is why designs stop short of it.",
                            r"Phase margin does rise with damping, and it keeps rising past $\zeta = 1$ where the loop is unambiguously slower. If margin alone decided it, the answer would be as much damping as the components allow.",
                            r"The peak shrinks with damping but does not vanish at $0.7$; the exact type-II transfer still peaks to $73.49$ against $N = 60$ at $\zeta = 0.707$. Flattening that peak is a real reason to add damping, and it points past $0.7$, not at it.",
                        ],
                        "why": r'''
The $5\%$ settling time is discontinuous in $\zeta$, because the first overshoot either
fits inside the tolerance window or it does not. It fits from $\zeta = 0.6901$ upward,
where $e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ equals $0.05$, and the settling time drops from
$4.418/\omega_n$ to $2.899/\omega_n$ across that boundary. So $0.707$ is an answer about
a $5\%$ mask, with a little margin, and a $2\%$ mask moves it to $0.7797$.
''',
                    },
                    {
                        "q": "A synthesiser hops from a channel needing $N = 100$ to one needing $N = 400$, with every component unchanged. What has happened to the loop?",
                        "opts": [
                            "$\\omega_n$ and $\\zeta$ have both halved, since each carries $N$",
                            "$\\omega_n$ has halved and $\\zeta$ is unchanged, having no $N$ in it",
                            "Neither moves: $N$ divides out of both expressions",
                            "$\\zeta$ has halved while $\\omega_n$ held, as $N$ scales damping only",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\omega_n = \sqrt{I_{cp}K_{vco}/2\pi NC}$ and $\zeta = (R/2)\sqrt{I_{cp}K_{vco}C/2\pi N}$ both carry $N$ under the same root, so quadrupling it halves both. The loop is slower and less damped at the top of the band than at the bottom, which is why a synthesiser is designed at its worst-case ratio.",
                            r"The first half is right and the second is the error: $\zeta$ carries $N$ under its root exactly as $\omega_n$ does. Checking one expression and assuming the other is independent is how this gets missed in a review.",
                            r"$N$ divides the phase fed back, so it divides the loop gain, and loop gain is what sets both parameters. Far from dividing out it sits under the square root in each, so quadrupling it halves both.",
                            r"Inverted. $N$ appears in both, and it appears in $\omega_n$ with more weight than the damping-only picture suggests — the ratio $\zeta/\omega_n$ is $RC/2$, fixed by components alone.",
                        ],
                        "why": r'''
Both expressions have $N$ under a square root in a denominator, so quadrupling the divide
ratio halves $\omega_n$ and halves $\zeta$. Their ratio $\zeta/\omega_n = RC/2$ is set by
components and never moves, which is a useful thing to hold: a channel change slides the
design along a line of constant $RC$, and the worst-case channel is the one with the
largest $N$, where the loop is slowest and closest to ringing.
''',
                    },
                    {
                        "q": "In the loop filter of the build exercise, the impedance flattens near $R_2$ between the zero at 1.6 kHz and the pole at 17.5 kHz. What is that flat region for?",
                        "opts": [
                            "Phase lead — the loop's whole stability margin comes from it",
                            "Rejecting the charge pump's ripple at the reference rate",
                            "Setting the DC control voltage the VCO has to sit at",
                            "Making the loop type II, so that any constant phase error is driven out",
                        ],
                        "a": 0,
                        "whys": [
                            r"The phase runs $-86.7°$ at $100$ Hz and $-33.6°$ at $5$ kHz: more than fifty degrees recovered, and that recovery is the margin. Placing the loop bandwidth on the shelf is what makes the PLL damped; placing it below the zero leaves two integrators and no margin.",
                            r"Ripple rejection is what $C_1$ and the pole above the shelf do, and it works by pulling the impedance back *down*. A flat impedance rejects nothing.",
                            r"The filter has no DC path to ground at all — that is the first check in the build exercise. The DC control voltage is set by where the VCO has to sit, not by the filter.",
                            r"Type II comes from the two integrations, which live *below* the zero where $|Z|$ falls at 20 dB per decade. The shelf is the region where the filter has stopped integrating.",
                        ],
                        "why": r'''
Below the zero the filter integrates and the phase is near $-90°$; adding the VCO's own
integration makes $-180°$ and no margin at all. On the shelf $R_2$ dominates, the phase
recovers to $-33.6°$ at $5$ kHz, and that recovery is the phase lead the loop is stable
by. The measured shelf reaches $0.917$ k$\Omega$ rather than the full $1$ k$\Omega$
because the zero and the pole sit barely a decade apart.
''',
                    },
                    {
                        "q": "The step response drawn in the sandbox and integrated in the lab overshoots 4.16% at the design damping of 0.7115. The real closed loop overshoots 20.66%. Where does the difference come from?",
                        "opts": [
                            "The loop filter's zero, which the prototype form leaves out",
                            "Sampling: the detector corrects once per reference cycle",
                            "The shunt capacitor $C_1$, a third pole the two-pole form omits",
                            "Numerical error in the forward-Euler integration of the response",
                        ],
                        "a": 0,
                        "whys": [
                            r"The true transfer is $(2\zeta\omega_ns + \omega_n^2)$ over $(s^2 + 2\zeta\omega_ns + \omega_n^2)$, and the numerator zero — the same $sRC+1$ that supplies the damping — pushes the peak up. It is unavoidable: the component that stabilises the loop is the component that makes it overshoot.",
                            r"Sampling does change the loop, but in the direction of *less* stability at high $\omega_n/\omega_{ref}$, and both figures above come from continuous-time models where sampling plays no part.",
                            r"$C_1$ adds a third pole, and poles reduce overshoot rather than increasing it. Neither number above includes $C_1$; the exact second-order transfer has only the zero.",
                            r"Forward Euler at $10^{-3}/\omega_n$ over 60000 steps reproduces the closed-form $e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ to two decimals, and the same integrator produces both figures. A five-fold gap is structure, not arithmetic.",
                        ],
                        "why": r'''
$\omega_n^2/(s^2+2\zeta\omega_ns+\omega_n^2)$ is the textbook prototype and it has no
zero. A charge-pump PLL's reference-to-output transfer is
$(2\zeta\omega_ns+\omega_n^2)/(s^2+2\zeta\omega_ns+\omega_n^2)$ — the loop filter's zero
sits in the numerator, and a numerator zero adds a differentiated copy of the response to
itself, raising the peak. At $\zeta = 0.7115$ that is $4.16\%$ against $20.66\%$, and even
at $\zeta = 1.4230$, where the prototype cannot overshoot at all, the true loop peaks
$8.20\%$ above target.
''',
                    },
                ],
            },
            "sandbox": {
                "title": "Damping, ringing and lock time",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 0.7, "wn": 5},
                "brief": r'''
The closed-loop poles of a charge-pump PLL and the frequency step it produces when
the divide ratio changes. Read the step response as the output frequency settling
after a channel hop.

Everything the loop filter does reaches this picture through only two numbers.
''',
                "notice": [
                    "Set $\\zeta$ to 0.1 and watch the ringing. That is a real synthesiser failing a settling mask — the frequency is inside the tolerance window and then leaves it again.",
                    "Raise $\\omega_n$ with $\\zeta$ fixed. The shape is unchanged and only the time axis compresses: lock time scales as $1/\\omega_n$, which is the argument for a wide loop.",
                    "Take $\\zeta$ past 1. The poles split onto the real axis, the overshoot vanishes, and the loop gets *slower* — the classic reason designs sit near 0.7 rather than higher.",
                ],
            },
            "derive": {
                "title": "From charge pump and filter to omega_n and zeta",
                "minutes": 16,
                "vars": ["s", "I_cp", "K_vco", "N", "C", "R", "zeta", "omega_n", "theta_e", "Z"],
                "brief": r'''
A charge-pump PLL. The phase detector and pump deliver a current proportional to the
phase error into a filter of a resistor $R$ in series with a capacitor $C$. That
voltage tunes a VCO of sensitivity $K_{vco}$ in rad/s per volt, and a divide-by-$N$
closes the loop.

Build the open-loop gain, then read $\omega_n$ and $\zeta$ off the closed-loop
characteristic polynomial.
''',
                "steps": [
                    {
                        "prompt": "The pump sources $I_{cp}$ for the fraction of each reference period that the phase error lasts. Averaged over a cycle, write its gain in amperes per radian of phase error.",
                        "answer": "\\frac{I_{cp}}{2 \\pi}",
                        "hint": "A full reference period is $2\\pi$ radians of phase error, and over that period the pump would be on the whole time.",
                        "deconstruct": [
                            "For a phase error $\\theta_e$ the pump is on for a fraction $\\theta_e / 2\\pi$ of the period.",
                            "The average current is therefore $I_{cp}\\theta_e/2\\pi$, and the gain is that divided by $\\theta_e$.",
                        ],
                    },
                    {
                        "prompt": "Write the impedance $Z$ of the loop filter — a resistor $R$ in series with a capacitor $C$.",
                        "answer": "R + \\frac{1}{s C}",
                        "hint": "Series impedances add, and a capacitor is $1/sC$.",
                        "deconstruct": [
                            "The capacitor contributes $1/sC$.",
                            "In series with $R$ the two simply add.",
                        ],
                    },
                    {
                        "prompt": "Multiply the four blocks — pump gain, filter impedance, VCO $K_{vco}/s$, divider $1/N$ — to get the open-loop gain. Write it in terms of $s$, $I_{cp}$, $K_{vco}$, $R$, $C$ and $N$.",
                        "given": "The pump current flows into the filter impedance, producing the tuning voltage.",
                        "answer": "\\frac{I_{cp} K_{vco} \\left( R + \\frac{1}{s C} \\right)}{2 \\pi N s}",
                        "hint": "Cascaded blocks multiply. Keep the filter impedance as a factor rather than expanding it yet.",
                        "deconstruct": [
                            "Pump times filter is $\\frac{I_{cp}}{2\\pi} Z$, a voltage per radian.",
                            "VCO times divider contributes $\\frac{K_{vco}}{N s}$.",
                        ],
                    },
                    {
                        "prompt": "Setting $1 + T(s) = 0$ and clearing denominators gives $s^2 + \\frac{I_{cp}K_{vco}R}{2\\pi N}s + \\frac{I_{cp}K_{vco}}{2\\pi N C}$. Compare with $s^2 + 2\\zeta\\omega_n s + \\omega_n^2$ and write $\\omega_n$.",
                        "answer": "\\sqrt{\\frac{I_{cp} K_{vco}}{2 \\pi N C}}",
                        "hint": "Match the constant terms, then take the square root.",
                        "deconstruct": [
                            "The constant term of your polynomial is $I_{cp}K_{vco}/2\\pi N C$.",
                            "The constant term of the standard form is $\\omega_n^2$.",
                        ],
                    },
                    {
                        "prompt": "Now match the coefficient of $s$ and write $\\zeta$ in terms of $R$, $I_{cp}$, $K_{vco}$, $C$ and $N$.",
                        "answer": "\\frac{R}{2}\\sqrt{\\frac{I_{cp} K_{vco} C}{2 \\pi N}}",
                        "hint": "You need $\\zeta = \\frac{I_{cp}K_{vco}R}{4\\pi N \\omega_n}$; substitute the $\\omega_n$ you just found and simplify.",
                        "deconstruct": [
                            "Matching gives $2\\zeta\\omega_n = I_{cp}K_{vco}R/2\\pi N$.",
                            "Dividing by $2\\omega_n$ and substituting $\\omega_n = \\sqrt{I_{cp}K_{vco}/2\\pi N C}$ moves $C$ into the numerator of the root.",
                        ],
                    },
                ],
                "closing": r'''
Written the other way round, $\zeta = \frac{R}{2}\omega_n C$ — the damping is the
resistor measured against the impedance of the capacitor at $\omega_n$. Remove the
resistor and $\zeta$ goes to zero: two integrators, poles exactly on the imaginary
axis, a loop that oscillates and never locks.

Both expressions carry $N$ in a denominator. Change channel by changing $N$ and you
have changed $\omega_n$ and $\zeta$ as well, which is why a synthesiser is only ever
designed at the worst-case divide ratio.
''',
            },
            "build": {
                "title": "The loop filter, driven by the charge pump itself",
                "minutes": 26,
                "brief": r"""
A charge pump is a current source. A loop filter is an impedance. The control voltage is
the product of the two — so the loop filter's job can be measured directly, by pushing a
known current into it and looking at the voltage that results.

## What is on the canvas

A **1 mA current source**, which is $I_{cp}$, and a probe on the control-voltage node.
Ground and nothing else.

## What to build

The standard second-order loop filter:

- $C_2 = 100$ nF in series with $R_2 = 1\ \text{k}\Omega$, that series pair from the
  control node to ground,
- $C_1 = 10$ nF directly from the control node to ground.

## Read the impedance, and you have read the loop

Because the excitation is 1 mA, the voltage the probe reports is numerically the
impedance in kilohms — and that impedance has three regions, which are the three things
the filter is for.

- **Below the zero** at $1/(2\pi R_2C_2) = 1.6$ kHz, the pair of capacitors integrates
  and $|Z|$ falls at 20 dB per decade. This is the second integrator in the loop, and it
  is what makes the PLL type II with zero steady-state phase error.
- **Between the zero and the pole**, $|Z|$ flattens out at $R_2$. **This flat region is
  the entire reason the loop is stable.** Two integrators alone give $-180°$ of phase and
  no margin whatsoever; $R_2$ contributes a zero whose phase lead pulls the loop back
  from the brink. Set the loop bandwidth in this region and the PLL is damped; set it
  below the zero and it rings or oscillates.
- **Above the pole** at $1/(2\pi R_2(C_1\|C_2)) = 17.5$ kHz, $C_1$ takes over and the
  impedance falls again. That is not incidental either: without $C_1$ the charge pump's
  current pulses would drop across $R_2$ as a square wave of ripple, straight onto the
  VCO control line and out as reference spurs.

The checks measure all three regions and the phase in the middle one.

## No DC operating point, and that is correct

There is no resistive path from the control node to ground, so the circuit has no DC
solution and the checks are all AC. That is a property of the real filter, not a
limitation of the model: the loop's DC control voltage is set by where the VCO has to
sit, and the filter contributes only the integration.
""",
                "start": {
                    "parts": [
                        {"id": "icp", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 4},
                        {"id": "g1", "kind": "GND", "x": 7, "y": 11},
                        {"id": "g2", "kind": "GND", "x": 11, "y": 14},
                        {"id": "out", "kind": "OUT", "x": 5, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [7, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "icp", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 4},
                        {"id": "c1", "kind": "C", "x": 7, "y": 9, "rot": 1, "value": 10e-9},
                        {"id": "g1", "kind": "GND", "x": 7, "y": 11},
                        {"id": "r2", "kind": "R", "x": 11, "y": 9, "rot": 1, "value": 1000},
                        {"id": "c2", "kind": "C", "x": 11, "y": 12, "rot": 1, "value": 100e-9},
                        {"id": "g2", "kind": "GND", "x": 11, "y": 14},
                        {"id": "out", "kind": "OUT", "x": 5, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [7, 7]},
                        {"a": [7, 7], "b": [7, 8]},
                        {"a": [7, 10], "b": [7, 11]},
                        {"a": [7, 7], "b": [11, 7]},
                        {"a": [11, 7], "b": [11, 8]},
                        {"a": [11, 10], "b": [11, 11]},
                        {"a": [11, 13], "b": [11, 14]},
                    ],
                },
                "checks": [
                    {
                        "name": "one resistor, two capacitors, and no DC path to ground",
                        "code": r"""
c.assert(c.count('R') === 1, 'One resistor, R2; there are ' + c.count('R') + '.');
c.assert(c.count('C') === 2, 'Two capacitors, C1 and C2; there are ' + c.count('C') + '.');
let hasDc = true;
try { c.vout(); } catch (e) { hasDc = false; }
c.assert(!hasDc,
  'The control node reached a DC solution, which means there is a resistive path from ' +
  'it to ground. R2 must be in series with C2, not straight to ground — otherwise the ' +
  'charge pump would be fighting a load resistor and the loop could not integrate.');
""",
                    },
                    {
                        "name": "below the zero it integrates: 14.5 kohm at 100 Hz",
                        "code": r"""
c.close(c.gain(100), 14.47, 0.06,
  'the impedance at 100 Hz, in volts per milliamp (so, kilohms). Down here both ' +
  'capacitors are in parallel and R2 is negligible, giving 1/(2*pi*f*(C1+C2)) with ' +
  'C1 + C2 = 110 nF');
c.close(c.gain(10) / c.gain(100), 10.0, 0.04,
  'the fall from 10 Hz to 100 Hz, both far below the 1.6 kHz zero, where the pair of ' +
  'capacitors is integrating on its own. Measured closer to the zero this ratio is ' +
  'already softening: 100 Hz against 1 kHz gives only 8.5');
""",
                    },
                    {
                        "name": "the flat region between zero and pole is R2, and it is the phase margin",
                        "code": r"""
c.close(c.gain(5e3), 0.917, 0.06,
  'the impedance at 5 kHz, between the 1.6 kHz zero and the 17.5 kHz pole. R2 is ' +
  '1 kohm and the shelf only reaches 0.92 of it, because the zero and the pole sit ' +
  'barely a decade apart and neither has finished before the other begins. This ' +
  'shelf is where a loop bandwidth is placed');
const ph = c.phase(5e3);
c.assert(ph > -45,
  'The phase at 5 kHz is ' + ph.toFixed(0) + ' degrees. In the flat region it should ' +
  'have recovered well away from the -90 degrees of pure integration — that recovery ' +
  'IS the phase margin R2 contributes, and without it two integrators in the loop ' +
  'leave none at all.');
c.assert(c.phase(100) < -75,
  'At 100 Hz the filter should be integrating, which means close to -90 degrees. It ' +
  'reads ' + c.phase(100).toFixed(0) + ', so the low-frequency behaviour is not a ' +
  'pure integration and the loop would not be type II.');
""",
                    },
                    {
                        "name": "above the pole C1 takes over, and kills the ripple",
                        "code": r"""
c.assert(c.gain(200e3) < 0.2 * c.gain(5e3),
  'Above the C1 pole the impedance must fall away again — that is what stops the ' +
  'charge pump current pulses appearing across R2 as reference spurs on the VCO ' +
  'control line. It reads ' + c.gain(200e3).toFixed(3) + ' kohm at 200 kHz against ' +
  c.gain(5e3).toFixed(3) + ' on the shelf, which is not enough attenuation.');
c.close(c.gain(200e3) / c.gain(2e6), 10.0, 0.10,
  'the fall over a decade well above the pole. C1 alone is a single pole, so a ' +
  'factor of 10 per decade');
""",
                    },
                ],
                "hints": [
                    "$C_1$ goes straight from the control node to ground. $R_2$ and $C_2$ go from the same node to ground *through each other*, in series.",
                    "The order of $R_2$ and $C_2$ within the series branch makes no electrical difference; put $R_2$ at the top so the drawing matches the way the filter is usually printed.",
                    "If the first check complains about a DC solution, $R_2$ has a path to ground that does not pass through $C_2$.",
                ],
            },
            "lab": {
                "title": "Loop parameters, overshoot and lock time",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Turn component values into loop behaviour.

`loop_params(icp, kvco, n_div, r, c)` returns `(wn, zeta)` from the expressions you
just derived. `kvco` is in rad/s per volt.

`step_response(wn, zeta, dt, steps)` integrates the standard second-order system

```text
y'' = wn**2 * (1 - y) - 2*zeta*wn*y'
```

with forward Euler, starting from `y = 0` and `y' = 0`, and returns `y` at every
step as a list. Record `y` *before* advancing, so the first entry is 0.

`overshoot(ys)` returns the peak excursion above the final value, as a fraction of
it — 0 when the response never exceeds it.

`lock_time(ys, dt, tol)` returns the time after which the response stays within
`tol` (a fraction) of its final value: find the *last* index that is outside the
window and return `(index + 1) * dt`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

TWO_PI = 2.0 * np.pi


def loop_params(icp, kvco, n_div, r, c):
    """Return (wn, zeta) for a charge-pump PLL with a series R-C loop filter."""
    # TODO: wn from the constant term, zeta from the coefficient of s.
    return 0.0, 0.0


def step_response(wn, zeta, dt, steps):
    """Forward-Euler the normalised second-order step response. Returns a list."""
    y = 0.0
    v = 0.0
    out = []
    # TODO: record y, then advance y and v by one Euler step, `steps` times.
    return out


def overshoot(ys):
    """Peak excursion above the final value, as a fraction of it. 0 if none."""
    # TODO
    return 0.0


def lock_time(ys, dt, tol=0.05):
    """Time after which the response stays inside +/- tol of its final value."""
    # TODO: find the last sample outside the window.
    return 0.0


if __name__ == "__main__":
    wn, zeta = loop_params(1e-3, TWO_PI * 30e6, 100.0, 1500.0, 3e-9)
    print("wn =", round(wn, 3), "rad/s  ->", round(wn / TWO_PI, 1), "Hz")
    print("zeta =", round(zeta, 4))
    ys = step_response(1.0, 0.5, 1e-3, 20000)
    print("overshoot:", round(overshoot(ys), 6))
    print("5% lock time:", round(lock_time(ys, 1e-3, 0.05), 4), "in units of 1/wn")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

TWO_PI = 2.0 * np.pi


def loop_params(icp, kvco, n_div, r, c):
    """Return (wn, zeta) for a charge-pump PLL with a series R-C loop filter."""
    wn = float(np.sqrt(icp * kvco / (TWO_PI * n_div * c)))
    zeta = float(0.5 * r * np.sqrt(icp * kvco * c / (TWO_PI * n_div)))
    return wn, zeta


def step_response(wn, zeta, dt, steps):
    """Forward-Euler the normalised second-order step response. Returns a list."""
    y = 0.0
    v = 0.0
    out = []
    for _ in range(int(steps)):
        out.append(y)
        a = wn * wn * (1.0 - y) - 2.0 * zeta * wn * v
        y = y + dt * v
        v = v + dt * a
    return out


def overshoot(ys):
    """Peak excursion above the final value, as a fraction of it. 0 if none."""
    final = ys[-1]
    return float(max(0.0, (max(ys) - final) / final))


def lock_time(ys, dt, tol=0.05):
    """Time after which the response stays inside +/- tol of its final value."""
    final = ys[-1]
    last = 0
    for i, y in enumerate(ys):
        if abs(y - final) > tol * abs(final):
            last = i
    return float((last + 1) * dt)


if __name__ == "__main__":
    wn, zeta = loop_params(1e-3, TWO_PI * 30e6, 100.0, 1500.0, 3e-9)
    print("wn =", round(wn, 3), "rad/s  ->", round(wn / TWO_PI, 1), "Hz")
    print("zeta =", round(zeta, 4))
    ys = step_response(1.0, 0.5, 1e-3, 20000)
    print("overshoot:", round(overshoot(ys), 6))
    print("5% lock time:", round(lock_time(ys, 1e-3, 0.05), 4), "in units of 1/wn")
'''}],
                "hints": [
                    "`wn = sqrt(icp*kvco/(2*pi*n_div*c))`, and `zeta = 0.5*r*sqrt(icp*kvco*c/(2*pi*n_div))`.",
                    "In the Euler loop, compute the acceleration from the *current* `y` and `v` before updating either.",
                    "`overshoot` must use the final value as the reference, not 1 — the numerical final value is never exactly 1.",
                    "`lock_time` wants the *last* violation, not the first: a ringing response leaves the window and comes back.",
                ],
                "tests": [
                    {"name": "the reference design lands on its stated parameters", "code": r'''
import numpy as np
_wn, _z = loop_params(1e-3, 2.0 * np.pi * 30e6, 100.0, 1500.0, 3e-9)
assert abs(_wn - 316227.7660168379) < 1.0, \
    f"wn should be sqrt(icp*kvco/(2*pi*N*C)) = 316228 rad/s, got {_wn:.1f}"
assert abs(_z - 0.7115124735378854) < 1e-6, \
    f"zeta should be (R/2)*sqrt(icp*kvco*C/(2*pi*N)) = 0.71151, got {_z:.6f}"
'''},
                    {"name": "pump current moves both parameters together", "code": r'''
import numpy as np
_wn, _z = loop_params(4e-3, 2.0 * np.pi * 30e6, 100.0, 1500.0, 3e-9)
assert abs(_wn - 632455.5320336758) < 1.0, \
    f"four times the pump current doubles wn to 632456 rad/s, got {_wn:.1f}"
assert abs(_z - 1.4230249470757708) < 1e-6, \
    f"zeta scales as sqrt(icp) too, so it doubles to 1.42302; got {_z:.6f}"
'''},
                    {"name": "the step response starts at zero and settles at one", "code": r'''
_ys = step_response(1.0, 0.5, 1e-3, 20000)
assert len(_ys) == 20000, f"expected 20000 samples, got {len(_ys)}"
assert abs(_ys[0]) < 1e-12, f"the loop starts with zero phase error correction, got {_ys[0]}"
assert abs(_ys[-1] - 1.0) < 1e-3, \
    f"a type-II loop has no steady-state error, so the response ends at 1.0; got {_ys[-1]:.6f}"
'''},
                    {"name": "overshoot matches the damping formula", "code": r'''
import numpy as np
_ys = step_response(1.0, 0.5, 1e-3, 20000)
_os = overshoot(_ys)
_want = np.exp(-np.pi * 0.5 / np.sqrt(1.0 - 0.25))
assert abs(_os - _want) < 2e-3, \
    f"at zeta = 0.5 the overshoot is exp(-pi*z/sqrt(1-z^2)) = {_want:.5f}, got {_os:.5f}"
'''},
                    {"name": "an overdamped loop does not overshoot at all", "code": r'''
_ys = step_response(1.0, 1.2, 1e-3, 20000)
assert overshoot(_ys) < 1e-6, \
    "with zeta above 1 the poles are real and the response cannot exceed its final value"
_ys7 = step_response(1.0, 0.7, 1e-3, 20000)
assert 0.03 < overshoot(_ys7) < 0.06, \
    f"zeta = 0.7 should give roughly 4.6% overshoot, got {overshoot(_ys7):.4f}"
'''},
                    {"name": "lock time scales inversely with the natural frequency", "code": r'''
_slow = lock_time(step_response(1.0, 0.5, 1e-3, 20000), 1e-3, 0.05)
_fast = lock_time(step_response(2.0, 0.5, 5e-4, 20000), 5e-4, 0.05)
assert abs(_slow - 5.288) < 0.02, f"expected a 5% lock time of about 5.29/wn, got {_slow:.3f}"
assert abs(_fast - _slow / 2.0) < 0.02, \
    f"doubling wn should halve the lock time: {_slow:.3f} against {_fast:.3f}"
'''},
                    {"name": "ringing delays lock even though the peak comes early", "code": r'''
_light = lock_time(step_response(1.0, 0.15, 1e-3, 40000), 1e-3, 0.05)
_good = lock_time(step_response(1.0, 0.7, 1e-3, 40000), 1e-3, 0.05)
assert _light > 3.0 * _good, \
    (f"a lightly damped loop crosses the target first and then rings outside the window: "
     f"zeta 0.15 took {_light:.2f}/wn against {_good:.2f}/wn at zeta 0.7")
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Where phase noise goes",
            "summary": "The loop is a low-pass for everything in front of the VCO and a high-pass for the VCO itself. The bandwidth is where you choose which noise to keep.",
            "concepts": [
                "Reference and divider noise reach the output through $N \\cdot L(s)$, a low-pass: in band, the reference phase noise is multiplied by $N^2$ in power, $20\\log_{10}N$ in dB.",
                "VCO noise reaches the output through $1 - L(s)$, a high-pass: the loop corrects it below the bandwidth and does nothing above.",
                "The two transfer functions sum to unity at every frequency, which is why widening the loop never removes noise, only exchanges one source for another.",
                "The optimum loop bandwidth is where the two contributions cross — narrower and the VCO dominates, wider and the multiplied reference does.",
                "Integrated phase noise becomes RMS jitter: $\\sigma_t = \\sqrt{2\\int S_\\phi\\,df} / 2\\pi f_c$.",
                "A low $\\zeta$ puts a peak in $|L(j\\omega)|$ near the bandwidth, and that peak appears directly in the output spectrum as a noise bump.",
            ],
            "read": [{
                "title": "Forty-three decibels between the crystal and the output",
                "minutes": 18,
                "body": r'''
A $2.4$ GHz synthesiser locked to a crystal reference, divide ratio $100$, on a
phase-noise analyser. The crystal is excellent: measured at the phase detector it
contributes a flat $10^{-16}$ per hertz, which the instrument writes as $-160$ dBc/Hz.
The synthesiser output is flat at $-117$ dBc/Hz from close in out to about a megahertz,
and then falls at $20$ dB per decade.

Forty-three decibels appeared between the reference and the output, and nothing in the
loop is broken or badly built. Forty of them are the divide ratio, and the other three
are the VCO — which the loop has suppressed almost exactly to the level of the
multiplied reference, and not below it. Both halves of that sentence come out of one
transfer function, and this reading is about where the corner belongs.

## One loop, two entry points, two different filters

Take the open-loop gain as a single integrator, $T(s) = \omega_c/s$, where $\omega_c$ is
the unity-gain frequency — the loop bandwidth. It is a crude stand-in for the
second-order loop of the previous module and it gets every asymptote right.

Noise enters at two places and they are not symmetric. Reference phase noise arrives
*ahead* of the divider, where the loop is trying to follow it, so it reaches the output
through $N\,T/(1+T)$. VCO phase noise is generated *at* the output, where the loop is
trying to remove it, so it reaches the output through $1/(1+T)$. Substitute and clear
the inner fractions:

$$H_{ref}(s) = \frac{N\omega_c}{s + \omega_c}, \qquad
  H_{vco}(s) = \frac{s}{s + \omega_c}$$

A low-pass with DC gain $N$, and a high-pass with gain $1$ far out. The derivation unit
*Noise transfer functions and the optimum bandwidth* builds both, and the thing to carry
away from it is that $H_{ref}/N$ and $H_{vco}$ sum to exactly one at every frequency —
$\omega_c/(s+\omega_c) + s/(s+\omega_c)$ — so there is no bandwidth at which both
sources are suppressed. Widening the loop does not remove noise. It exchanges one source
for the other.

## Where the forty decibels went

Phase noise is a density, and a density scales as the *square* of a voltage-like
transfer function. In band $H_{ref}$ is flat at $N$, so the reference density is
multiplied by $N^2$: $20\log_{10}100 = 40$ dB. Outside the loop bandwidth $H_{vco}$ is
unity, so the free-running VCO's $k/f^2$ arrives untouched; inside, it is multiplied by
$(f/f_c)^2$, and $(f/f_c)^2\cdot k/f^2 = k/f_c^2$ — a constant. The suppressed VCO is
*flat* in band, at a level set only by how wide the loop is.

```python
import math

N, S_REF, K = 100.0, 1e-16, 1.0       # the lab's constants
FC = 1e6                              # loop bandwidth, Hz


def contributions(f, fc):
    ref = (N * fc / math.sqrt(f * f + fc * fc)) ** 2 * S_REF
    vco = (f / math.sqrt(f * f + fc * fc)) ** 2 * (K / (f * f))
    return ref, vco


print(f"the reference at the detector : {10 * math.log10(S_REF):7.2f} dBc/Hz")
for f in (1e3, 1e4, 1e5, 1e6, 1e7):
    ref, vco = contributions(f, FC)
    print(f"  {f / 1e3:8.0f} kHz : ref {ref:.4e}  vco {vco:.4e}  "
          f"sum {10 * math.log10(ref + vco):7.2f} dBc/Hz")
print(f"20 log10 N                    : {20 * math.log10(N):7.2f} dB")
```

The two columns are identical at every offset, which is not a coincidence and is worth
a moment. The reference term is $N^2S_{ref}f_c^2/(f^2+f_c^2)$ and the VCO term is
$k/(f^2+f_c^2)$; they share a denominator, so they are equal *everywhere* exactly when
$N^2S_{ref}f_c^2 = k$ — which is the condition $f_c = \sqrt{k/N^2S_{ref}}$, and that is
the crossover the derivation unit ends on. At the optimum bandwidth the two curves do
not cross, they coincide, and the output is $3$ dB above either one alone. The
$-160$ dBc/Hz crystal becomes $-120$ under $N^2$, and the $3$ dB of VCO on top of it is
the $-117$ the analyser reads.

## What the optimum is worth

Set $f_c$ to the crossover and the integral takes a closed form. Since
$N^2S_{ref}f_c^2 = k$ there, the total density collapses to $2k/(f^2+f_c^2)$, and
$\int_0^\infty df/(f^2+f_c^2) = \pi/2f_c$, so

$$\sigma_\phi^2 = 2\int_0^\infty S\,df = \frac{2\pi k}{f_c}
   = 2\pi N\sqrt{k\,S_{ref}}$$

Three exponents fall out of that and they are the price list for the whole design.
Jitter is the square root of the variance, so it goes as $\sqrt{N}$, as $k^{1/4}$ and as
$S_{ref}^{1/4}$.

```python
import math

N, S_REF, K, F_CARRIER = 100.0, 1e-16, 1.0, 2.4e9


def grid(lo_dec, hi_dec, n):
    return [10.0 ** (lo_dec + (hi_dec - lo_dec) * i / (n - 1)) for i in range(n)]


def density(f, fc):
    return ((N * fc) ** 2 * S_REF + K) / (f * f + fc * fc)


def jitter(fc, fs):
    area = sum(0.5 * (density(fs[i], fc) + density(fs[i - 1], fc)) * (fs[i] - fs[i - 1])
               for i in range(1, len(fs)))
    return math.sqrt(2.0 * area) / (2.0 * math.pi * F_CARRIER)


F = grid(2, 8, 6001)
opt = math.sqrt(K / (N * N * S_REF))
print(f"crossover sqrt(k / N^2 S_ref)   : {opt / 1e3:9.1f} kHz")
for fc in (1e5, opt / math.sqrt(10.0), opt, opt * math.sqrt(10.0), 1e7):
    print(f"  fc {fc / 1e3:9.2f} kHz : {jitter(fc, F) * 1e12:.5f} ps"
          f"   {jitter(fc, F) / jitter(opt, F):6.4f} x")
closed = math.sqrt(2.0 * math.pi * N * math.sqrt(K * S_REF)) / (2.0 * math.pi * F_CARRIER)
print(f"closed form at the optimum      : {closed * 1e12:.5f} ps")
```

The search in the lab, *Shape the noise and find the best bandwidth*, returns $1$ MHz on
these constants and $0.16569$ ps of RMS jitter, and the closed form agrees to
$0.16623$ ps — the small gap is the tail beyond $100$ MHz that the grid does not reach.

Now read the basin. A factor of $\sqrt{10}$ either side of the optimum costs about
$32\%$ of jitter, and a full decade either side costs a factor of $2.2$. The minimum is
real and it is *broad*, which is the useful part: the bandwidth can be moved by a factor
of two for settling time, or for stability against the reference, at a cost of a few per
cent of jitter. What the basin does not tolerate is a decade.

```python
import math

F_CARRIER = 2.4e9


def grid(lo_dec, hi_dec, n):
    return [10.0 ** (lo_dec + (hi_dec - lo_dec) * i / (n - 1)) for i in range(n)]


def best_jitter(n_div, s_ref, k, fs):
    fc = math.sqrt(k / (n_div * n_div * s_ref))
    area = sum(0.5 * (((n_div * fc) ** 2 * s_ref + k) / (fs[i] ** 2 + fc * fc)
                      + ((n_div * fc) ** 2 * s_ref + k) / (fs[i - 1] ** 2 + fc * fc))
               * (fs[i] - fs[i - 1]) for i in range(1, len(fs)))
    return fc, math.sqrt(2.0 * area) / (2.0 * math.pi * F_CARRIER)


F = grid(2, 8, 6001)
base_fc, base = best_jitter(100.0, 1e-16, 1.0, F)
print(f"the lab's design           : fc {base_fc / 1e3:8.1f} kHz  {base * 1e12:.5f} ps")
for label, args in (("half the divide ratio", (50.0, 1e-16, 1.0)),
                    ("10 dB quieter VCO    ", (100.0, 1e-16, 0.1)),
                    ("10 dB quieter ref    ", (100.0, 1e-17, 1.0))):
    fc, j = best_jitter(*args, F)
    print(f"  {label}: fc {fc / 1e3:8.1f} kHz  {j * 1e12:.5f} ps"
          f"  {20 * math.log10(j / base):+6.2f} dB")
```

Ten decibels off the VCO buys $4.98$ dB of jitter. Ten decibels off the reference buys
$5.06$ dB. Halving the divide ratio buys $3.04$ dB. Those are three very different
prices for what look like comparable engineering efforts: the VCO and the crystal are
both fourth-root levers, so a $10$ dB improvement in either is halved on the way to
jitter, while $N$ is a square-root lever and a factor of two in it is worth a full
$3$ dB. $N$ is the cheapest decibel in the design, and it is the reason the next module
exists — an integer-N synthesiser cannot lower $N$ without coarsening its channel grid
by the same factor.

## The mistake: widening the loop to suppress the VCO

The loop corrects VCO noise inside its bandwidth, VCO noise is what the datasheet
complains about, and so a wider loop looks like a free improvement. At $10$ MHz the
jitter is $0.36150$ ps against $0.16569$ at the optimum — a factor of $2.18$, or
$6.8$ dB worse.

The mirror belief loses by almost exactly the same amount. Reference noise is multiplied
by $N^2$, and $40$ dB of multiplication is alarming enough that keeping the loop narrow
feels prudent. At $100$ kHz the jitter is $0.37331$ ps: a factor of $2.25$, $7.0$ dB
worse. Two opposite pieces of advice, both confidently argued, both wrong by the same
$7$ dB — which is what $H_{ref}/N + H_{vco} = 1$ looks like when it is priced. Neither
source can be suppressed except by passing more of the other.

Both are tempting because each is *locally* true. Widening the loop really does reduce
the VCO's contribution, monotonically, everywhere; narrowing it really does reduce the
reference's. What neither argument does is integrate. The sandbox, *The loop as a filter
for noise*, is the place to watch it happen: raise $K$ to see the $20\log_{10}N$ plateau
lift, then move the corner and watch the area under the curve refuse to go down.

## The unit on the axis, and the band under the integral

Two conventions in this course are load-bearing and neither is stated in the code.

The first is what the density means. The lab's `rms_jitter` computes
$\sigma_t = \sqrt{2\int S\,df}\,/\,2\pi f_c$, and that factor of two is correct exactly
when $S$ is the *single-sideband* density $\mathcal{L}(f)$ — the quantity a phase-noise
analyser plots in dBc/Hz, one sideband's worth. If the same array were read as the
one-sided PSD of $\phi$ itself, the variance would be $\int S\,df$ with no factor of two
and every jitter number in the course would be $\sqrt2$ smaller.

```python
import math

N, S_REF, K, F_CARRIER, FC = 100.0, 1e-16, 1.0, 2.4e9, 1e6


def grid(lo_dec, hi_dec, n):
    return [10.0 ** (lo_dec + (hi_dec - lo_dec) * i / (n - 1)) for i in range(n)]


def area_over(fs):
    def d(f):
        return ((N * FC) ** 2 * S_REF + K) / (f * f + FC * FC)
    return sum(0.5 * (d(fs[i]) + d(fs[i - 1])) * (fs[i] - fs[i - 1])
               for i in range(1, len(fs)))


a_lab = area_over(grid(2, 8, 6001))
a_cap = area_over(grid(3, math.log10(2e7), 6001))
for name, a in (("100 Hz to 100 MHz, the lab   ", a_lab),
                ("  1 kHz to  20 MHz, capstone ", a_cap)):
    print(f"{name}: {math.sqrt(2.0 * a) / (2 * math.pi * F_CARRIER) * 1e12:.5f} ps"
          f"   ({math.degrees(math.sqrt(2.0 * a)):.4f} deg RMS)")
print(f"the same integral read as S_phi : "
      f"{math.sqrt(a_lab) / (2 * math.pi * F_CARRIER) * 1e12:.5f} ps"
      f"   (a factor of {math.sqrt(2.0):.4f})")
```

$0.16569$ ps against $0.11716$ ps for the same spectrum, and the difference is entirely
which convention the reader assumes. The course uses $\mathcal{L}(f)$ throughout — the
lab's factor of two, the capstone's modulator density, and the $-160$ dBc/Hz reading of
$S_{ref} = 10^{-16}$ all agree on it — so the numbers hang together; the label
"rad²/Hz" in the docstrings belongs to the other reading of the same array. When a
jitter figure crosses a team boundary, the factor of $\sqrt2$ is where it goes wrong.

The second convention is the integration band. The lab integrates $100$ Hz to $100$ MHz
and the capstone $1$ kHz to $20$ MHz, and on *this* spectrum they agree to $1.3\%$
because a $1/f^2$ tail contributes very little at either end. That agreement is a
property of the spectrum and not a general fact: the next module adds a noise term that
*rises* with offset frequency, and there the upper limit decides the answer. An RMS
jitter without a band attached is not a number, the way a noise figure without a source
impedance is not a number.

## Where the model stops holding

$T(s) = \omega_c/s$ has no loop-filter zero, so it cannot show the peaking a real loop
has near its bandwidth. The capstone uses the exact second-order transfers, and there
$|H_{ref}|$ reaches $73.49$ at $f = f_n$ with $\zeta = 0.707$ against a divide ratio of
$60$ — $1.76$ dB of gain *above* $N$ that the single-pole model draws as $-3$ dB. Drop
$\zeta$ and the peak grows into a visible bump in the measured spectrum, which is what
the sandbox's third prompt is pointing at.

The model has no divider, phase-detector or charge-pump noise at all. In a real
integer-N part those add a floor at the phase detector that behaves like extra
$S_{ref}$, and in a fractional-N part the modulator adds something much larger and
differently shaped; the derivation unit's closing says so plainly, and the optimum moves
by more than a decade once it is included.

Finally, the VCO here is pure $1/f^2$. Real oscillators have a $1/f^3$ region close in,
where device flicker noise is upconverted by the tuning nonlinearity, and a flat far-out
floor from the buffer. The $1/f^3$ region sits inside the loop bandwidth where the loop
suppresses it, which is a good reason to prefer a wider loop than this model recommends
— and one more term to add before the answer is a design rather than an illustration.
'''
            }],
            "sandbox": {
                "title": "The loop as a filter for noise",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 30, "zeta": 0.7, "K": 10},
                "brief": r'''
Read the magnitude plot as the path from reference phase noise to output phase
noise. $K$ stands in for the divide ratio $N$, and the corner is the loop bandwidth.

The VCO sees the complement of this curve: whatever this plot passes, the VCO path
rejects, and the two always add to one.
''',
                "notice": [
                    "Raise $K$ from 1 to 10. The in-band plateau lifts by 20 dB — that is $20\\log_{10}N$, the reason a synthesiser with a large divide ratio has a poor in-band floor.",
                    "Move the corner right. More of the reference noise gets through, but the region where the loop is suppressing the VCO grows with it. That trade is the whole bandwidth decision.",
                    "Drop $\\zeta$ to 0.2 and look at the peak just below the corner. In a real synthesiser that peak is a visible bump in the measured phase noise, and it comes entirely from the loop filter resistor being too small.",
                ],
            },
            "derive": {
                "title": "Noise transfer functions and the optimum bandwidth",
                "minutes": 15,
                "vars": ["s", "N", "omega", "omega_c", "S_ref", "k", "f"],
                "brief": r'''
Approximate the open-loop gain by a single integrator, $T(s) = \omega_c / s$, where
$\omega_c$ is the unity-gain frequency — the loop bandwidth. It is a crude model of
the second-order loop and it gets every asymptote right.

Reference phase noise enters ahead of the divider, so it reaches the output as
$N\,T/(1+T)$. VCO phase noise is injected at the output itself, so it reaches the
output as $1/(1+T)$.
''',
                "steps": [
                    {
                        "prompt": "Substitute $T = \\omega_c/s$ into $N\\,T/(1+T)$ and simplify. Write the transfer from reference phase to output phase.",
                        "answer": "\\frac{N \\omega_c}{s + \\omega_c}",
                        "hint": "Multiply numerator and denominator by $s$ to clear the inner fraction.",
                        "deconstruct": [
                            "$\\frac{N\\omega_c/s}{1 + \\omega_c/s}$ — multiply top and bottom by $s$.",
                            "That leaves $N\\omega_c$ over $s + \\omega_c$: a single-pole low-pass with DC gain $N$.",
                        ],
                    },
                    {
                        "prompt": "Do the same for the VCO path, $1/(1+T)$.",
                        "answer": "\\frac{s}{s + \\omega_c}",
                        "hint": "Same trick — clear the fraction inside the denominator.",
                        "deconstruct": [
                            "$\\frac{1}{1 + \\omega_c/s}$ — multiply top and bottom by $s$.",
                            "The result is a high-pass: zero at DC, unity far above $\\omega_c$.",
                        ],
                    },
                    {
                        "prompt": "Put $s = j\\omega$ in that high-pass and take the magnitude for $\\omega \\ll \\omega_c$. Write the result.",
                        "answer": "\\frac{\\omega}{\\omega_c}",
                        "hint": "When $\\omega$ is far below $\\omega_c$, the denominator is essentially $\\omega_c$.",
                        "deconstruct": [
                            "The magnitude is $\\omega/\\sqrt{\\omega^2 + \\omega_c^2}$.",
                            "For $\\omega \\ll \\omega_c$ the root is approximately $\\omega_c$.",
                        ],
                    },
                    {
                        "prompt": "In band, the reference transfer is flat at $N$. Phase noise is a power spectral density, so write the factor by which the reference phase noise density is multiplied at the output.",
                        "answer": "N^2",
                        "placeholder": "N^{2}",
                        "hint": "Power scales as the square of a voltage-like transfer function.",
                        "deconstruct": [
                            "The amplitude transfer is $N$.",
                            "A density in $\\text{rad}^2/\\text{Hz}$ therefore scales by $N^2$ — that is $20\\log_{10}N$ in dB.",
                        ],
                    },
                    {
                        "prompt": "The in-band floor is $N^2 S_{ref}$, flat. The free-running VCO contributes $k/f^2$, and inside the loop bandwidth it is suppressed to roughly $k/\\omega_c^2$. Write the offset frequency at which the two curves cross.",
                        "answer": "\\sqrt{\\frac{k}{N^2 S_{ref}}}",
                        "placeholder": "\\sqrt{\\frac{k}{N^{2} S_{ref}}}",
                        "hint": "Set $N^2 S_{ref} = k/f^2$ and solve for $f$.",
                        "deconstruct": [
                            "$N^2 S_{ref} f^2 = k$.",
                            "So $f^2 = k / N^2 S_{ref}$, and take the positive root.",
                        ],
                    },
                ],
                "closing": r'''
That crossover is not merely where the curves meet: integrate the total over all
offsets and the integral is minimised at exactly the same frequency. Setting the loop
bandwidth to the crossover is therefore not a rule of thumb but the answer to a
minimisation, and the lab reproduces it numerically.

The model has one honest omission. Nothing here accounts for noise the divider itself
adds, and in a fractional-N synthesiser that term is large enough to move the optimum
down by a decade. That is the next module.
''',
            },
            "quiz": {
                "title": "A low-pass one way, a high-pass the other",
                "minutes": 7,
                "questions": [
                    {
                        "q": "How does reference noise reach the output?",
                        "opts": [
                            "Multiplied by $N$, through a low-pass",
                            "Multiplied by $N$, through a high-pass",
                            "Unchanged, through a low-pass",
                            "Divided by $N$",
                        ],
                        "a": 0,
                        "why": r"""
The loop forces the divided output to track the reference, so any reference phase noise is
multiplied by the divide ratio on the way back up — $20\log_{10}N$ decibels of it, which
for $N = 1000$ is 60 dB. Inside the loop bandwidth the loop follows it faithfully, so it
passes; outside, the loop cannot respond and it is filtered. That multiplication is the
strongest argument for keeping $N$ small, and the reason fractional-N exists.
""",
                    },
                    {
                        "q": "And VCO noise?",
                        "opts": [
                            "Through a high-pass — the loop corrects it inside the bandwidth",
                            "Through a low-pass",
                            "Unfiltered",
                            "Multiplied by $N$",
                        ],
                        "a": 0,
                        "why": r"""
The VCO's own noise is an error the loop can see and correct, so within the loop bandwidth
it is suppressed by the loop gain and outside it the VCO runs free. The two paths are
therefore complementary, which is the next question and the whole basis of choosing a
bandwidth.
""",
                    },
                    {
                        "q": "The reference path's transfer function $L(s)$ and the VCO path's sum to what?",
                        "opts": ["1, at every frequency", "0", "$N$", "The loop gain"],
                        "a": 0,
                        "why": r"""
$L(s) + (1 - L(s)) = 1$ identically — there is no bandwidth at which both noise sources
are suppressed, because suppressing one necessarily passes the other. That is not a
limitation of any particular design; it is structural, and it is why a synthesiser's
phase-noise plot has a characteristic shoulder right at the loop bandwidth.
""",
                    },
                    {
                        "q": "You widen the loop bandwidth. What happens?",
                        "opts": [
                            "Less VCO noise, more reference and divider noise",
                            "Less of both",
                            "More of both",
                            "More VCO noise, less reference noise",
                        ],
                        "a": 0,
                        "why": r"""
The loop corrects the VCO over a wider range and simultaneously tracks the reference over
that same wider range. Wider also means faster settling, which matters for a frequency-
hopping radio, so the choice is rarely made on noise alone.
""",
                    },
                    {
                        "q": "Where is the optimum loop bandwidth, for phase noise alone?",
                        "opts": [
                            "Where the two contributions cross",
                            "As wide as stability allows",
                            "As narrow as possible",
                            "At the reference frequency",
                        ],
                        "a": 0,
                        "why": r"""
Below the crossing the VCO dominates and widening helps; above it the multiplied reference
dominates and widening hurts. Putting the bandwidth at the crossover minimises the
integrated noise, and it is the one place the two curves can be traded evenly. Stability
puts a hard ceiling on top of that — roughly a tenth of the reference frequency — and
sometimes the ceiling arrives first, in which case the answer is a quieter VCO rather than
a wider loop.
""",
                    },
                ],
            },
            "lab": {
                "title": "Shape the noise and find the best bandwidth",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
Build the two transfer functions, add up the contributions, and search for the
bandwidth that minimises the integral.

`ref_shape(f, fc, n_div)` returns the magnitude $|N\omega_c/(s+\omega_c)|$ at offset
`f`, which in terms of ordinary frequencies is `n_div*fc/sqrt(f**2 + fc**2)`.

`vco_shape(f, fc)` returns `f/sqrt(f**2 + fc**2)`.

`output_pn(f, fc, n_div, s_ref, k_vco)` returns the total output phase noise density
in rad²/Hz:

```text
ref_shape**2 * s_ref  +  vco_shape**2 * (k_vco / f**2)
```

`rms_jitter(f, s, f_carrier)` integrates `s` over `f` with the trapezoidal rule —
write the sum yourself, `0.5*(s[1:]+s[:-1])*diff(f)`, rather than reaching for a
NumPy helper whose name has changed between versions — and returns
`sqrt(2*integral)/(2*pi*f_carrier)`.

`best_bandwidth(f, n_div, s_ref, k_vco, candidates)` evaluates the integral for every
candidate bandwidth and returns the one with the smallest total.

All four take `f` as a NumPy array and should return arrays where that makes sense.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def ref_shape(f, fc, n_div):
    """Magnitude of the reference-to-output phase transfer at offset f."""
    f = np.asarray(f, dtype=float)
    # TODO: n_div * fc / sqrt(f**2 + fc**2)
    return np.zeros_like(f)


def vco_shape(f, fc):
    """Magnitude of the VCO-to-output phase transfer at offset f."""
    f = np.asarray(f, dtype=float)
    # TODO: the complement of the low-pass above
    return np.zeros_like(f)


def output_pn(f, fc, n_div, s_ref, k_vco):
    """Total output phase noise density, rad^2/Hz."""
    f = np.asarray(f, dtype=float)
    # TODO: shape each source by the square of its transfer and add them
    return np.zeros_like(f)


def rms_jitter(f, s, f_carrier):
    """Integrate the density and convert to seconds RMS."""
    f = np.asarray(f, dtype=float)
    s = np.asarray(s, dtype=float)
    # TODO: trapezoidal integral, then sqrt(2*integral)/(2*pi*f_carrier)
    return 0.0


def best_bandwidth(f, n_div, s_ref, k_vco, candidates):
    """Return the candidate bandwidth with the smallest integrated phase noise."""
    # TODO
    return 0.0


if __name__ == "__main__":
    f = np.logspace(2, 8, 6001)
    fc = best_bandwidth(f, 100.0, 1e-16, 1.0, np.logspace(4, 8, 401))
    print("best loop bandwidth:", round(fc / 1e3, 2), "kHz")
    print("jitter there:", rms_jitter(f, output_pn(f, fc, 100.0, 1e-16, 1.0), 2.4e9))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def ref_shape(f, fc, n_div):
    """Magnitude of the reference-to-output phase transfer at offset f."""
    f = np.asarray(f, dtype=float)
    return n_div * fc / np.sqrt(f * f + fc * fc)


def vco_shape(f, fc):
    """Magnitude of the VCO-to-output phase transfer at offset f."""
    f = np.asarray(f, dtype=float)
    return f / np.sqrt(f * f + fc * fc)


def output_pn(f, fc, n_div, s_ref, k_vco):
    """Total output phase noise density, rad^2/Hz."""
    f = np.asarray(f, dtype=float)
    ref = ref_shape(f, fc, n_div) ** 2 * s_ref
    vco = vco_shape(f, fc) ** 2 * (k_vco / (f * f))
    return ref + vco


def rms_jitter(f, s, f_carrier):
    """Integrate the density and convert to seconds RMS."""
    f = np.asarray(f, dtype=float)
    s = np.asarray(s, dtype=float)
    area = float(np.sum(0.5 * (s[1:] + s[:-1]) * np.diff(f)))
    return float(np.sqrt(2.0 * area) / (2.0 * np.pi * f_carrier))


def best_bandwidth(f, n_div, s_ref, k_vco, candidates):
    """Return the candidate bandwidth with the smallest integrated phase noise."""
    best = None
    best_val = None
    for fc in np.asarray(candidates, dtype=float):
        s = output_pn(f, fc, n_div, s_ref, k_vco)
        val = float(np.sum(0.5 * (s[1:] + s[:-1]) * np.diff(f)))
        if best_val is None or val < best_val:
            best_val = val
            best = fc
    return float(best)


if __name__ == "__main__":
    f = np.logspace(2, 8, 6001)
    fc = best_bandwidth(f, 100.0, 1e-16, 1.0, np.logspace(4, 8, 401))
    print("best loop bandwidth:", round(fc / 1e3, 2), "kHz")
    print("jitter there:", rms_jitter(f, output_pn(f, fc, 100.0, 1e-16, 1.0), 2.4e9))
'''}],
                "hints": [
                    "Both shapes share the same denominator `sqrt(f**2 + fc**2)`; only the numerator differs.",
                    "`vco_shape**2 * (k_vco/f**2)` simplifies to `k_vco/(f**2 + fc**2)` — a useful check on your algebra, though either form passes.",
                    "The trapezoidal sum is `np.sum(0.5*(s[1:]+s[:-1])*np.diff(f))`; on a log-spaced grid the spacing is not constant, so the `diff` matters.",
                    "`best_bandwidth` can compare the integrals directly — the square root and the carrier scaling are monotonic and cannot change which candidate wins.",
                ],
                "tests": [
                    {"name": "the reference path is flat at N in band", "code": r'''
import numpy as np
_a = ref_shape(np.array([1e3]), 1e6, 100.0)[0]
assert abs(_a - 100.0) < 1e-3, \
    f"far below the loop bandwidth the reference is multiplied by N = 100, got {_a:.4f}"
_b = ref_shape(np.array([1e6]), 1e6, 100.0)[0]
assert abs(_b - 100.0 / np.sqrt(2.0)) < 1e-6, \
    f"at the bandwidth itself the transfer is down 3 dB, so 70.711; got {_b:.4f}"
'''},
                    {"name": "the VCO path is the complement of it", "code": r'''
import numpy as np
_lo = vco_shape(np.array([1e5]), 1e6)[0]
_at = vco_shape(np.array([1e6]), 1e6)[0]
_hi = vco_shape(np.array([1e9]), 1e6)[0]
assert abs(_lo - 0.09950371902099893) < 1e-9, \
    f"a decade inside the loop the VCO is suppressed to about f/fc = 0.0995, got {_lo:.6f}"
assert abs(_at - 1.0 / np.sqrt(2.0)) < 1e-9, f"at fc the VCO path is also 3 dB down, got {_at:.6f}"
assert abs(_hi - 1.0) < 1e-6, \
    f"far outside the loop bandwidth the VCO is untouched, so the transfer is 1; got {_hi:.6f}"
'''},
                    {"name": "in-band noise is the reference multiplied by N squared", "code": r'''
import numpy as np
_s = output_pn(np.array([1e3]), 1e6, 100.0, 1e-16, 0.0)[0]
assert abs(_s - 1e-12) < 1e-14, \
    f"with no VCO noise the in-band floor is N^2 * s_ref = 1e-12 rad^2/Hz, got {_s:.3e}"
'''},
                    {"name": "far outside the loop the VCO is on its own", "code": r'''
import numpy as np
_s = output_pn(np.array([1e8]), 1e6, 100.0, 0.0, 1.0)[0]
assert abs(_s - 1e-16) < 1e-18, \
    f"at 100 MHz offset the output should be the free-running k/f^2 = 1e-16, got {_s:.3e}"
'''},
                    {"name": "jitter integrates a flat spectrum correctly", "code": r'''
import numpy as np
_f = np.linspace(1e3, 1e6, 200001)
_s = np.full_like(_f, 1e-14)
_j = rms_jitter(_f, _s, 1e9)
assert abs(_j - 2.2496651135079577e-14) < 1e-18, \
    (f"a flat 1e-14 rad^2/Hz across 999 kHz on a 1 GHz carrier gives 22.5 fs RMS; "
     f"got {_j:.4e} — check the factor of 2 and the 2*pi")
'''},
                    {"name": "the best bandwidth is the crossover", "code": r'''
import numpy as np
_f = np.logspace(2, 8, 6001)
_fc = best_bandwidth(_f, 100.0, 1e-16, 1.0, np.logspace(4, 8, 401))
assert abs(_fc - 1e6) < 3e4, \
    (f"the analytic crossover is sqrt(k/(N^2*s_ref)) = 1.0 MHz; the search returned "
     f"{_fc/1e3:.1f} kHz")
'''},
                    {"name": "moving away from the optimum costs jitter both ways", "code": r'''
import numpy as np
_f = np.logspace(2, 8, 6001)
_best = rms_jitter(_f, output_pn(_f, 1e6, 100.0, 1e-16, 1.0), 2.4e9)
_narrow = rms_jitter(_f, output_pn(_f, 1e5, 100.0, 1e-16, 1.0), 2.4e9)
_wide = rms_jitter(_f, output_pn(_f, 1e7, 100.0, 1e-16, 1.0), 2.4e9)
assert _best < _narrow and _best < _wide, \
    (f"1 MHz should beat both 100 kHz and 10 MHz: {_best:.3e} against "
     f"{_narrow:.3e} and {_wide:.3e}")
assert abs(_best - 1.6569077355436886e-13) < 1e-16, \
    f"expected 0.166 ps RMS at the optimum, got {_best:.4e}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Fractional-N and the noise it brings",
            "summary": "Divide by 100 most of the time and 101 occasionally, and the average is fractional. The error that makes it work is a spectrum you then have to filter.",
            "concepts": [
                "An accumulator of $m$ bits fed a constant $K$ overflows at an average rate $K/2^m$, and each overflow swallows one extra VCO cycle.",
                "Average divide ratio $N + K/2^m$, channel resolution $f_{ref}/2^m$ — resolution is now independent of the reference frequency.",
                "The instantaneous divide ratio is still an integer, so the phase error is a sawtooth, and its cumulative value never exceeds one VCO cycle.",
                "That bounded accumulation is first-order noise shaping: the divide error is the first difference of a bounded sequence, so its spectrum rises with frequency.",
                "A first-order accumulator produces tones, not noise. The period is $2^m/\\gcd(K, 2^m)$, and a short period is a large fractional spur close to the carrier.",
                "Higher-order MASH modulators trade tones for more shaped noise, which the loop must then filter — the reason a fractional-N loop is narrower than an integer-N one.",
            ],
            "read": [{
                "title": "Thirty-nine kilohertz of resolution, and the loop it costs",
                "minutes": 18,
                "body": r'''
The capstone's synthesiser: $2.4$ GHz out, a $40$ MHz crystal reference, so the integer
part of the divide ratio is $60$. A ten-bit accumulator sets the fractional part, which
puts the channels $40\ \text{MHz}/2^{10} = 39.0625$ kHz apart.

There is another way to get $39.0625$ kHz channels, and it is worth pricing before the
mechanism is explained. An integer-N loop steps in units of its reference, so it would
need a $39.0625$ kHz reference and a divide ratio of $2.4\times10^9/39062.5 = 61\,440$.
The previous module showed the in-band floor is $N^2S_{ref}$; going from $N = 60$ to
$N = 61\,440$ is $20\log_{10}(1024) = 60.2$ dB of extra multiplication, on top of a
reference so slow the loop bandwidth would have to sit in the kilohertz.

So fractional-N is not a refinement. It is the only way to have both a fast reference
and a fine grid. What it charges for that is the subject of this module, and the bill
arrives as a loop bandwidth: the capstone's optimum comes out at $21.13$ kHz where the
previous module's crossover argument would have said $1.67$ MHz, and the settling time
follows — $22.2\ \mu\text{s}$ instead of $0.28$.

## The accumulator is a rate multiplier

The divider counts VCO cycles and cannot count a fraction of one. What it can do is
count $N$ sometimes and $N+1$ other times.

Load an $m$-bit accumulator with $K$ on every reference cycle. It advances by $K$ and
wraps at $2^m$, so over $2^m$ cycles it wraps exactly $K$ times: the overflow rate is
$K/2^m$. Wire each overflow to the divider's modulus control and the divider spends a
fraction $K/2^m$ of its cycles at $N+1$ and the rest at $N$. The average is

$$\bar N = N + \frac{K}{2^m}, \qquad
  f_{out} = f_{ref}\left(N + \frac{K}{2^m}\right)$$

and stepping $K$ by one moves the output by $f_{ref}/2^m$, which is the channel
resolution — a quantity that no longer has anything to do with how fast the reference
runs. That is the whole promise, and the fill-in-the-blanks unit *Dividing by a number
that is not an integer* is four holes on exactly these two lines.

```python
import math

F_REF, N_INT, M, F_OUT = 40e6, 60, 10, 2.4e9


def accumulator(k, m, steps):
    """The lab's accumulator: add k, carry out and subtract on overflow."""
    mod = 1 << m
    acc = 0
    out = []
    for _ in range(steps):
        acc += k
        carry = 1 if acc >= mod else 0
        if carry:
            acc -= mod
        out.append(carry)
    return out


K = 397
seq = [N_INT + c for c in accumulator(K, M, 1 << M)]
mean = sum(seq) / len(seq)
run, peak = 0.0, 0.0
for n in seq:
    run += n - mean
    peak = max(peak, abs(run))
print(f"average divide ratio  : {mean!r}   wanted {N_INT + K / (1 << M)!r}")
print(f"peak phase error      : {peak!r} VCO cycles")
print(f"channel step f_ref/2^m: {F_REF / (1 << M) / 1e3:.4f} kHz")
n_integer = F_OUT / (F_REF / (1 << M))
print(f"integer-N would need N: {n_integer:.0f}, a floor "
      f"{20 * math.log10(n_integer / N_INT):.2f} dB above this one")
```

The average is $60.3876953125$ and the wanted value is $60.3876953125$ — the same float,
because $397/1024$ is exact in binary and the arithmetic is integer throughout. The lab,
*A fractional-N accumulator and its spurs*, asserts that equality to $10^{-12}$ for the
same reason.

## Bounded is the same statement as shaped

The second line of that output is the important one. Each reference cycle the divider is
wrong by either $-K/2^m$ or $1 - K/2^m$ counts, and those errors accumulate into phase.
The running sum peaks at $0.9990234375$ VCO cycles — which is $1023/1024$, one LSB short
of a single cycle — and returns to zero after a full period.

It is bounded because the accumulator's own contents are the running sum, scaled: the
hardware that decides when to carry is the same register that holds the accrued error,
and a register that wraps at $2^m$ cannot hold more than $2^m - 1$. So the phase error
of a first-order fractional-N divider is bounded by one VCO cycle by construction, not
by luck, and no amount of running it changes that.

Now turn the boundedness into a spectrum. If the cumulative error $E[n]$ is bounded,
then the per-cycle divide error is $e[n] = E[n] - E[n-1]$: a first difference of a
bounded sequence. Differencing has the transfer $1 - z^{-1}$, whose magnitude at offset
$f$ is

$$\left|1 - e^{-j2\pi f/f_{ref}}\right| = 2\left|\sin\frac{\pi f}{f_{ref}}\right|
   \;\approx\; \frac{2\pi f}{f_{ref}} \quad (f \ll f_{ref})$$

rising linearly with frequency. That is first-order noise shaping, and it arrived
without anyone designing it — it is a consequence of the error being held in a register
rather than thrown away. The derivation unit *Resolution, and the shape of the
quantisation noise* takes it one step further: an $L$-th order modulator differences
$L$ times, and once the loop's own $\omega_c/\omega$ roll-off is applied the output
noise amplitude above the bandwidth goes as $\omega_c\,\omega^{L-1}$.

## A plain accumulator makes lines, not noise

Shaped is not the same as random, and this is where the first-order scheme fails.

The accumulator is a finite-state machine with period $2^m/\gcd(K, 2^m)$, so its carry
sequence is strictly periodic and its spectrum is a set of lines. The fundamental sits
at $\min(K,\,2^m-K)\cdot f_{ref}/2^m$, and how much of it survives depends entirely on
where the loop's own low-pass has got to by then.

```python
import math

F_REF, M, FN, ZETA = 40e6, 10, 21134.890398366475, 0.707


def loop_lowpass(f):
    """|H_ref/N| for the capstone's loop: unity in band, rolling off past f_n."""
    wn = 2.0 * math.pi * FN
    s = complex(0.0, 2.0 * math.pi * f)
    return abs((2.0 * ZETA * wn * s + wn * wn) / (s * s + 2.0 * ZETA * wn * s + wn * wn))


print(f"loop bandwidth (natural frequency) : {FN / 1e3:.2f} kHz")
for k in (1, 3, 256, 397, 512):
    line = min(k, (1 << M) - k) * F_REF / (1 << M)
    print(f"  K = {k:4d}: fundamental line at {line / 1e3:10.2f} kHz, "
          f"passed at {20 * math.log10(loop_lowpass(line)):+7.2f} dB")
```

For the lab's $K = 397$ the line sits at $15\,507.81$ kHz and the loop takes $54.30$ dB
off it; $K = 256$, the fraction $1/4$, lands at $10$ MHz and loses $50.49$ dB even
though it carries half the error power on its own; and $K = 512$, the fraction one half,
puts everything at $f_{ref}/2$ where it is furthest from harm. The trouble is at the
other end. $K = 3$ puts its fundamental at $117.19$ kHz and the loop removes only
$11.80$ dB of it, and $K = 1$ puts one at $39.06$ kHz where the loop takes off
$2.09$ dB — which is to say, nothing. **Channels whose fractional part is close to a
whole number are the ones with close-in spurs**, and they are exactly the channels a
frequency plan cannot avoid.

## The mistake: delta-sigma removes the error

The sentence people carry away is that a delta-sigma modulator "gets rid of" the
fractional spurs. It does not remove anything. It makes the error *bigger* and scatters
it, and the scattering is what is worth having.

```python
import cmath
import math


def accumulator(k, m, steps):
    mod = 1 << m
    acc = 0
    out = []
    for _ in range(steps):
        acc += k
        c = 1 if acc >= mod else 0
        if c:
            acc -= mod
        out.append(c)
    return out


def mash11(k, m, steps):
    """MASH 1-1: a second accumulator fed the first one's remainder, differenced."""
    mod = 1 << m
    a1 = a2 = 0
    prev = 0
    out = []
    for _ in range(steps):
        a1 += k
        c1 = 1 if a1 >= mod else 0
        if c1:
            a1 -= mod
        a2 += a1
        c2 = 1 if a2 >= mod else 0
        if c2:
            a2 -= mod
        out.append(c1 + c2 - prev)
        prev = c2
    return out


def line_spectrum(seq):
    n = len(seq)
    mean = sum(seq) / n
    x = [v - mean for v in seq]
    return [abs(sum(x[i] * cmath.exp(-2j * math.pi * b * i / n) for i in range(n)) / n) ** 2
            for b in range(n // 2 + 1)]


for name, s in (("plain accumulator", accumulator(397, 10, 1024)),
                ("MASH 1-1         ", mash11(397, 10, 1024))):
    mean = sum(s) / len(s)
    var = sum((v - mean) ** 2 for v in s) / len(s)
    p = line_spectrum(s)
    worst = max(range(1, len(p)), key=lambda i: p[i])
    print(f"{name}: divide offsets {sorted(set(s))}  mean {mean:.10f}")
    print(f"                   error power {var:.6f}, biggest line at "
          f"{worst / 1024 * 40e6 / 1e6:6.3f} MHz holding "
          f"{p[worst] / sum(p[1:]) * 100:5.1f}% of it")
```

Both produce the same average, $0.3876953125$, to the last digit — the modulator has not
changed the frequency by a hertz. What has changed is everything else. The plain
accumulator swings the divider between two values and carries $0.237388$ of error power,
$75.2\%$ of it in one line. The MASH 1-1 swings it over four values, $-1$ to $+2$, and
carries $0.508872$ — **more than twice the error power** — with its largest line holding
$2.2\%$.

The trade is a factor of $2.14$ more error in exchange for a factor of $34$ less
concentration, and it is a good trade because a spur and noise of the same power are not
equally harmful: a spur reciprocally mixes an interferer straight onto the wanted
channel at one specific offset, and no averaging helps. The mistake is tempting because
the modulator genuinely does make the measured spectrum look clean, and because the
audio-converter version of the same circuit is usually described as "noise shaping" with
the emphasis on shaping. The extra error is real, it is the price, and the next section
is where the bill is presented.

## Priced: the loop the modulator forces

The capstone models the modulator with Riley's result — the quantiser's phase step
spread over the reference band, differenced $L-1$ times, since converting a divide-count
error into output phase integrates once and consumes one of the $L$ differences.

```python
import math

TWO_PI = 2.0 * math.pi
F_REF, N_DIV, F_OUT, S_REF, K_VCO, ORDER = 40e6, 60.0, 2.4e9, 1e-16, 1.0, 2


def ds_psd(f):
    """The capstone's synth.py, verbatim in scalar form."""
    return (TWO_PI ** 2 / (12.0 * F_REF)) * (2.0 * math.sin(math.pi * f / F_REF)) ** (2 * (ORDER - 1))


def terms(f, wn):
    s = complex(0.0, TWO_PI * f)
    den = s * s + 2.0 * 0.707 * wn * s + wn * wn
    h_ref = abs(N_DIV * (2.0 * 0.707 * wn * s + wn * wn) / den)
    h_vco = abs(s * s / den)
    return (h_ref ** 2 * S_REF, h_vco ** 2 * (K_VCO / (f * f)),
            (h_ref / N_DIV) ** 2 * ds_psd(f))


def grid(a, b, n):
    return [10.0 ** (a + (b - a) * i / (n - 1)) for i in range(n)]


FS = grid(3, math.log10(2e7), 4001)
print(f"N^2 S_ref, the in-band reference floor : {N_DIV ** 2 * S_REF:.4e}")
for f in (1e4, 21134.89, 1e5, 1.6666667e6):
    print(f"  modulator at {f / 1e3:9.2f} kHz : {ds_psd(f):.4e}"
          f"  ({10 * math.log10(ds_psd(f) / (N_DIV ** 2 * S_REF)):+6.2f} dB above it)")
for fn in (21134.890398366475, 1.6666666666666667e6):
    wn = TWO_PI * fn
    parts = [0.0, 0.0, 0.0]
    prev = terms(FS[0], wn)
    for i in range(1, len(FS)):
        cur = terms(FS[i], wn)
        for j in range(3):
            parts[j] += 0.5 * (cur[j] + prev[j]) * (FS[i] - FS[i - 1])
        prev = cur
    total = sum(parts)
    j = math.sqrt(2.0 * total) / (TWO_PI * F_OUT)
    print(f"fn {fn / 1e3:9.2f} kHz : {j * 1e12:8.4f} ps   "
          f"ref {parts[0] / total * 100:5.2f}%  vco {parts[1] / total * 100:5.2f}%  "
          f"modulator {parts[2] / total * 100:6.2f}%")
```

The modulator's density crosses the multiplied reference floor at about $13$ kHz, is
$4.01$ dB above it at the chosen $21.13$ kHz, and is $41.92$ dB above it at $1.67$ MHz
— the bandwidth the previous module's crossover argument recommends. Widen the loop to
there and the jitter is $37.84$ ps against $0.84$: forty-five times worse, $33$ dB, and
the split says why. At $21.13$ kHz the budget is $65.18\%$ VCO, $34.79\%$ modulator and
$0.03\%$ reference. At $1.67$ MHz it is $100.00\%$ modulator, to two decimals.

Read that $0.03\%$ carefully. The reference — the source the whole of the previous
module was balanced against — is now irrelevant, and the optimum is set by a completely
different pair. The crossover formula $\sqrt{k/N^2S_{ref}}$ has not become wrong; it has
become the answer to a question with a missing term. The sandbox, *Settling after a
channel hop*, is what that costs in time: $\omega_n$ smaller by a factor of $79$ means
settling longer by the same factor, $22.2\ \mu\text{s}$ against $0.28$, which for a
hopping radio is often the binding constraint rather than the jitter.

## Where it stops holding

The quantisation density has no $m$ in it. That is deliberate and correct — the
instantaneous error is one divide count whatever the accumulator's width, so extra bits
buy resolution and no extra noise — but it means the model is silent about spurs, which
depend on $K$ and $2^m$ through the period. A MASH still produces tones for some $K$,
particularly the simple fractions, and real parts dither the least significant bit to
break them up at the cost of a little more noise.

The order is a trap in both directions. With the loop's single roll-off, the output
noise amplitude goes as $\omega_c\omega^{L-1}$ above the bandwidth: for the MASH 1-1
here that is flat, which is why the integration band's upper limit matters and why the
capstone stops at $f_{ref}/2 = 20$ MHz, the modulator's own Nyquist frequency. Take
$L = 3$ and the output noise *rises* above the bandwidth, which the two-pole filter this
course derived cannot contain at all — hence the extra poles every real fractional-N
loop filter carries, and hence a MASH-3 part that measures worse with a wide loop than
the same part measured narrow.

Finally, the whole treatment is linear. It assumes the phase–frequency detector sees
error small enough to stay in its linear range, and a MASH swinging the divider over
four counts produces instantaneous phase excursions large enough to test that. Charge
pump mismatch and dead zone then fold the shaped noise back down to low frequencies as
spurs the linear model cannot predict, which is why a fractional-N synthesiser's
measured close-in spectrum is usually worse than its simulation and why so much design
effort goes into the pump rather than the modulator.
'''
            }],
            "quiz": {
                "title": "The average is fractional; the divider is not",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A plain accumulator is replaced with a MASH 1-1 modulator, the fraction unchanged. What happens to the total power in the divide error?",
                        "opts": [
                            "It rises — the divider now takes four values rather than two",
                            "It is unchanged, and only its distribution in frequency moves",
                            "It falls, because the error stops accumulating between overflows",
                            "It goes to zero: the divide ratio itself becomes fractional",
                        ],
                        "a": 0,
                        "whys": [
                            r"On $K = 397$, $m = 10$ the plain accumulator swings between $N$ and $N+1$ and carries $0.237388$ of error power; the MASH 1-1 swings from $N-1$ to $N+2$ and carries $0.508872$ — a factor of $2.14$ more. What it buys is concentration: the biggest line falls from $75.2\%$ of the error power to $2.2\%$.",
                            r"The usual summary, and close enough to be worth stating precisely: the modulator does not merely redistribute, it adds. A wider swing of divide values is a larger instantaneous error, and the measurement says $0.508872$ against $0.237388$.",
                            r"The error still accumulates — that is what makes the shaping first-order in the plain case and higher-order in the MASH. What changes is the sequence of integers chosen, not whether a register is holding the remainder.",
                            r"Every divider in the loop still divides by a whole number on every single reference cycle. Only the average over many cycles is fractional, and that is true of the plain accumulator too.",
                        ],
                        "why": r'''
A MASH 1-1 uses divide offsets $-1$ through $+2$ where the plain accumulator uses $0$ and
$+1$, so its instantaneous error is larger and its total error power is $0.508872$
against $0.237388$ — more than double. The average divide ratio is identical to the last
digit, $0.3876953125$ in both. What the modulator earns its place with is that its
biggest spectral line holds $2.2\%$ of the error power instead of $75.2\%$: a spur of a
given power is far more harmful than the same power spread out, because it mixes an
interferer onto the wanted channel at one fixed offset.
''',
                    },
                    {
                        "q": "Why is the loop bandwidth of a fractional-N synthesiser typically far narrower than that of an integer-N one built on the same reference?",
                        "opts": [
                            "The modulator's noise climbs with offset and has to be filtered",
                            "The reference has to be slower, which lowers the stability ceiling",
                            "The divide ratio is larger, and $\\omega_n$ falls as $1/\\sqrt{N}$",
                            "The accumulator inserts a delay that consumes the phase margin",
                        ],
                        "a": 0,
                        "whys": [
                            r"Quantisation noise is shaped upward by the modulator, so the loop has to close before it becomes large. On the capstone's design it sits $4.01$ dB above the multiplied reference at $21.13$ kHz and $41.92$ dB above it at $1.67$ MHz, and moving the bandwidth there takes the jitter from $0.84$ ps to $37.84$ ps.",
                            r"Backwards, and it inverts the whole point of the technique: fractional-N exists so the reference can stay *fast* while the channel grid stays fine. The capstone runs a $40$ MHz reference for $39$ kHz channels.",
                            r"$N$ is smaller in a fractional-N design, not larger — $60$ here against the $61\,440$ an integer-N loop would need for the same grid. That reduction is one of the technique's main attractions.",
                            r"The accumulator runs at the reference rate and its latency is a reference cycle or two, which is well inside a loop bandwidth three orders of magnitude below $f_{ref}$. Margin is not where this is decided.",
                        ],
                        "why": r'''
The modulator adds a noise term whose density rises with offset frequency, so it is small
close in and large further out — the opposite shape from everything else in the budget.
The loop passes whatever is inside its bandwidth, so the bandwidth must close before that
term dominates. On the capstone's synthesiser the modulator is $4.01$ dB above the
multiplied reference at the chosen $21.13$ kHz and $41.92$ dB above it at $1.67$ MHz,
and widening the loop to the latter costs a factor of $45$ in RMS jitter.
''',
                    },
                    {
                        "q": "The crossover rule of the previous module puts the best bandwidth for this synthesiser at 1.67 MHz. The capstone's search returns 21 kHz. What accounts for the difference?",
                        "opts": [
                            "A third noise source the rule omits, 42 dB up at 1.67 MHz",
                            "The exact second-order transfers, which peak near the bandwidth",
                            "A different carrier, rescaling every jitter figure",
                            "The narrower integration band, 1 kHz to 20 MHz rather than wider",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\sqrt{k/N^2S_{ref}}$ balances the VCO against the multiplied reference and knows nothing about a modulator. Add one and the budget at $1.67$ MHz becomes $100.00\%$ modulator to two decimal places, while at $21.13$ kHz it is $65.18\%$ VCO, $34.79\%$ modulator and $0.03\%$ reference.",
                            r"The peaking is real — $|H_{ref}|$ reaches $73.49$ against $N = 60$ at $\zeta = 0.707$ — and it is worth about a decibel. It cannot move an optimum by a factor of seventy-nine.",
                            r"Jitter is phase variance divided by $2\pi f_c$, so the carrier scales every candidate bandwidth by the same factor and cannot change which one wins.",
                            r"The band does matter here, because the modulator's contribution is flat above the loop bandwidth rather than falling. It changes the numbers by a few per cent, not the location of a minimum.",
                        ],
                        "why": r'''
The crossover formula is the answer to a two-source problem: multiplied reference against
free-running VCO. A fractional-N loop has a third source, and at $1.67$ MHz it is
$41.92$ dB above the reference floor, so the budget there is $100.00\%$ modulator to two
decimals and the jitter is $37.84$ ps against $0.84$ at the true optimum. At $21.13$ kHz
the split is $65.18\%$ VCO, $34.79\%$ modulator, $0.03\%$ reference — the reference, which
the old rule was balancing, has stopped mattering entirely.
''',
                    },
                    {
                        "q": "For a first-order accumulator with $m = 10$ on a 40 MHz reference, which channels carry their fractional spur closest to the carrier?",
                        "opts": [
                            "Those whose fractional part is nearly a whole number",
                            "Those with a fractional part of one half, $K = 2^{m-1}$",
                            "Those whose $K$ shares no common factor with $2^m$ at all",
                            "Those at the centre of the VCO's tuning range",
                        ],
                        "a": 0,
                        "whys": [
                            r"The fundamental line sits at $\min(K,\,2^m-K)f_{ref}/2^m$, so $K = 3$ puts one at $117.19$ kHz, which the $21$ kHz loop attenuates by only $11.80$ dB, and $K = 1$ puts one at $39.06$ kHz, attenuated by $2.09$ dB. The lab's $K = 397$ puts its line at $15.5$ MHz, where the loop takes off $54.30$ dB.",
                            r"$K = 512$ is the fraction one half, which alternates every cycle and puts the whole error at $f_{ref}/2 = 20$ MHz — the furthest out it can possibly be, and the easiest case rather than the worst.",
                            r"An odd $K$ gives the longest possible period, which spreads the energy over the most lines. The line that matters is the *lowest* one, and its position depends on how near $K$ is to $0$ or $2^m$, not on the factorisation.",
                            r"The VCO's tuning range sets $K_{vco}$ and the tuning-voltage headroom; it has no bearing on where the accumulator's period puts a line.",
                        ],
                        "why": r'''
The carry sequence is periodic with period $2^m/\gcd(K, 2^m)$ and its fundamental line
lands at $\min(K,\,2^m-K)\cdot f_{ref}/2^m$. That is $15.5$ MHz for the lab's $K = 397$
and $10$ MHz for $K = 256$, where the capstone's loop removes $54.30$ dB and $50.49$ dB
respectively — but $3/1024$ puts a line at $117.19$ kHz, attenuated by $11.80$ dB, and
$1/1024$ puts one at $39.06$ kHz, attenuated by $2.09$ dB. Fractional parts near a whole
number are the difficult channels, which is awkward because a frequency plan cannot
avoid them.
''',
                    },
                    {
                        "q": "A plain first-order accumulator's cumulative phase error peaks at 0.9990234375 VCO cycles and never exceeds one. Why is it bounded?",
                        "opts": [
                            "The register holding the running sum wraps at $2^m$",
                            "The loop corrects it before it can grow larger",
                            "The divide ratio is never more than one count from its average",
                            "Each overflow removes exactly the error the previous one made",
                        ],
                        "a": 0,
                        "whys": [
                            r"The accumulator's contents *are* the running sum of the divide error, scaled by $2^m$, and a register that wraps cannot hold more than $2^m - 1$. The peak of $0.9990234375$ is $1023/1024$: one LSB short of a full cycle, by construction rather than by luck.",
                            r"The loop does eventually absorb the error, but the bound holds with the loop open and would hold if the loop were removed. It is a property of the arithmetic, not of any feedback.",
                            r"True of the instantaneous error and irrelevant to the cumulative one — a per-cycle error bounded by one count could still accumulate without limit if it kept the same sign, which is exactly what happens with a $\pm$ dithered divider.",
                            r"The overflow removes $2^m$ from the register, not the previous cycle's error. Overflows come at irregular intervals set by $K$, and the error between them is what the running sum keeps track of.",
                        ],
                        "why": r'''
The hardware that decides when to carry is the same register that holds the accrued
error. The accumulator contents equal the cumulative divide error times $2^m$, and a
register that wraps at $2^m$ cannot hold more than $2^m - 1$ — so the phase error is
bounded by one VCO cycle by construction. The lab measures $0.9990234375$, exactly
$1023/1024$. This is also the reason the shaping is first-order: a sequence whose running
sum is bounded is the first difference of a bounded sequence, and differencing has the
magnitude $2|\sin(\pi f/f_{ref})|$, which rises with frequency.
''',
                    },
                    {
                        "q": "The capstone integrates its jitter from 1 kHz to 20 MHz. Why does the upper limit deserve more care here than in the integer-N budget of the previous module?",
                        "opts": [
                            "Above the bandwidth the modulator's density is flat, not falling",
                            "The VCO's $1/f^2$ noise stops falling once the loop lets it through",
                            "The reference multiplication by $N^2$ applies at every offset alike",
                            "A trapezoidal rule loses accuracy on a coarse logarithmic grid",
                        ],
                        "a": 0,
                        "whys": [
                            r"First-order phase shaping rises as $f$ and the loop rolls off as $1/f$, so their product is flat: every extra octave of integration band adds proportionally to the variance. The previous module's spectrum fell as $1/f^2$ out there, which is why its band mattered by only $1.3\%$.",
                            r"The VCO's contribution is $1/f^2$ once the loop stops filtering it, so it keeps falling and its tail converges. It is the term whose upper limit matters least.",
                            r"$N^2$ multiplies the reference in band only; outside the loop bandwidth $H_{ref}$ rolls off and the reference contributes $0.03\%$ of this budget in any case.",
                            r"The grid has 4001 points over four decades, which resolves everything here. Changing the limit changes the answer because it changes the *integral*, not because it changes the accuracy of the rule.",
                        ],
                        "why": r'''
The modulator's phase noise is shaped upward as $f$ and the loop rolls it off as $1/f$,
so above the loop bandwidth their product is essentially flat — and the integral of a flat
density grows in proportion to the band. The previous module's spectrum fell as $1/f^2$
out there, so its two candidate bands agreed to $1.3\%$. The capstone stops at
$f_{ref}/2 = 20$ MHz, which is not an arbitrary choice: it is the modulator's own Nyquist
frequency, above which its spectrum is an alias of what lies below.
''',
                    },
                ],
            },
            "sandbox": {
                "title": "Settling after a channel hop",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 0.6, "wn": 8},
                "brief": r'''
The same second-order step response, now read as a channel hop: the divide ratio
changes and the output frequency has to settle inside a tolerance window.

Fractional-N exists so that the hop can be small without making the reference small.
The cost is quantisation noise, and filtering that noise pulls $\omega_n$ to the
left — so read this picture as the price of the previous module's decision.
''',
                "notice": [
                    "Halve $\\omega_n$, as filtering quantisation noise forces you to. The settling time doubles: narrowing the loop to clean up the modulator directly costs hop time.",
                    "At $\\zeta = 0.6$ the response overshoots about 9%. If the settling mask is tighter than that, the loop re-enters the window only after the first ring — the peak, not the average, is what fails.",
                    "Push $\\zeta$ to 1.4. The overshoot is gone but the whole response is slower, which is why a synthesiser that must hop fast sits near 0.7 and relies on a clean modulator instead.",
                ],
            },
            "derive": {
                "title": "Resolution, and the shape of the quantisation noise",
                "minutes": 14,
                "vars": ["N", "K", "m", "L", "f", "f_ref", "f_out", "omega", "omega_c"],
                "brief": r'''
An $m$-bit accumulator is loaded with $K$ every reference cycle. Whenever it
overflows, the divider is told to divide by $N+1$ instead of $N$ for that cycle.

Work out what that does to the output frequency, to the channel spacing, and to the
spectrum of the error it leaves behind.
''',
                "steps": [
                    {
                        "prompt": "The accumulator overflows on a fraction $K/2^m$ of the reference cycles. Write the average divide ratio.",
                        "answer": "N + \\frac{K}{2^m}",
                        "hint": "Average the two integers with weights $1 - K/2^m$ and $K/2^m$.",
                        "deconstruct": [
                            "The divider spends a fraction $K/2^m$ of cycles at $N+1$ and the rest at $N$.",
                            "The weighted mean is $N + K/2^m$.",
                        ],
                    },
                    {
                        "prompt": "Increment $K$ by one. Write the resulting change in output frequency, given $f_{out} = f_{ref}\\left(N + \\frac{K}{2^m}\\right)$.",
                        "answer": "\\frac{f_{ref}}{2^m}",
                        "hint": "Only the fractional term changes, and it changes by $1/2^m$.",
                        "deconstruct": [
                            "$\\Delta(K/2^m) = 1/2^m$.",
                            "Multiplying by $f_{ref}$ gives the channel step.",
                        ],
                    },
                    {
                        "prompt": "The divide error is the first difference of the accumulator contents, so its spectrum carries a factor $\\left|1 - e^{-j 2\\pi f/f_{ref}}\\right|$. Write that magnitude for $f \\ll f_{ref}$.",
                        "answer": "\\frac{2 \\pi f}{f_{ref}}",
                        "hint": "For a small angle $\\theta$, $\\left|1 - e^{-j\\theta}\\right| \\approx \\theta$.",
                        "deconstruct": [
                            "Exactly, the magnitude is $2\\left|\\sin(\\pi f/f_{ref})\\right|$.",
                            "For a small argument the sine is its own argument, leaving $2\\pi f/f_{ref}$.",
                        ],
                    },
                    {
                        "prompt": "An $L$-th order modulator applies that difference $L$ times. Write the amplitude shaping factor at low offsets.",
                        "answer": "\\left( \\frac{2 \\pi f}{f_{ref}} \\right)^{L}",
                        "hint": "Applying the same filter $L$ times multiplies the magnitudes.",
                        "deconstruct": [
                            "One difference contributes $2\\pi f/f_{ref}$.",
                            "$L$ of them in cascade contribute that factor raised to the $L$.",
                        ],
                    },
                    {
                        "prompt": "That noise reaches the output through the loop's low-pass, which above $\\omega_c$ falls as $\\omega_c/\\omega$. Write the frequency dependence of the output noise amplitude above the loop bandwidth, in terms of $\\omega$, $\\omega_c$ and $L$.",
                        "given": "Below the bandwidth the output noise amplitude follows $\\omega^L$.",
                        "answer": "\\omega_c \\omega^{L-1}",
                        "hint": "Multiply the shaping $\\omega^L$ by the roll-off $\\omega_c/\\omega$.",
                        "deconstruct": [
                            "The shaping gives $\\omega^L$ and the loop gives $\\omega_c/\\omega$.",
                            "Their product is $\\omega_c\\,\\omega^{L-1}$.",
                        ],
                    },
                ],
                "closing": r'''
Read the last answer for $L = 1$: the output noise is flat above the loop bandwidth,
and only the finite width of the band keeps the integral finite. For $L = 2$ it still
*rises*, and a loop with a single roll-off cannot contain it at all — which is why
every real fractional-N loop filter carries extra poles beyond the two this course
has derived, and why a MASH-3 synthesiser with a wide loop measures worse than the
same part with a narrow one.

The lab builds the first-order case exactly, and measures the bounded phase error
that makes the shaping true.
''',
            },
            "blanks": {
                "title": "Dividing by a number that is not an integer",
                "minutes": 8,
                "caption": "fracn.py — an accumulator, and the error it creates",
                "lang": "python",
                "brief": r"""
The divider can only ever divide by a whole number. Alternate between two of them in the
right proportion and the *average* is fractional — which solves the resolution problem
and creates a spur problem. Fill in both halves.
""",
                "listing": """# An m-bit accumulator fed a constant K on every reference cycle
# overflows at an average rate of ___ ,
# and each overflow bumps the divider from N to N+1.

# Average divide ratio    N + K/2**m
# Channel resolution      f_ref / ___

# But the INSTANTANEOUS ratio is still an integer, so the phase error
# builds and resets: it is a ___ ,
# and its harmonics are the fractional spurs.

# Replacing the plain accumulator with a delta-sigma modulator ___ .
""",
                "blanks": [
                    {
                        "prompt": "How often does an m-bit accumulator fed K overflow?",
                        "hole": "?",
                        "opts": ["K / 2**m", "2**m / K", "K * 2**m", "1 / K"],
                        "a": 0,
                        "why": "It advances by $K$ each cycle and wraps at $2^m$, so it overflows $K$ times every $2^m$ cycles. That fraction is the whole mechanism — the accumulator is a rate multiplier and nothing more.",
                        "whys": [
                            "It advances by $K$ each cycle and wraps at $2^m$, so it overflows $K$ times every $2^m$ cycles. That fraction is the whole mechanism — the accumulator is a rate multiplier and nothing more.",
                            "Inverted: this is the number of cycles *between* overflows, not the rate.",
                            "A product would exceed one for any sensible $K$, meaning more than one overflow per cycle.",
                            "The accumulator size has to appear; without it the answer does not depend on the resolution at all.",
                        ],
                    },
                    {
                        "prompt": "So how fine can the channels be?",
                        "hole": "?",
                        "opts": ["2 ** m", "K", "m", "2 ** K"],
                        "a": 0,
                        "why": "$f_{ref}/2^m$, and here is the point of the whole technique: resolution has been decoupled from the reference frequency. An integer-N synthesiser needing 100 kHz channels must run a 100 kHz reference and multiply its noise by a huge $N$; fractional-N gets the same channels from a 10 MHz reference, with a hundredfold smaller $N$ and 40 dB less multiplied reference noise.",
                        "whys": [
                            "$f_{ref}/2^m$, and here is the point of the whole technique: resolution has been decoupled from the reference frequency. An integer-N synthesiser needing 100 kHz channels must run a 100 kHz reference and multiply its noise by a huge $N$; fractional-N gets the same channels from a 10 MHz reference, with a hundredfold smaller $N$ and 40 dB less multiplied reference noise.",
                            "$K$ selects which channel, not how finely they are spaced.",
                            "The bit count, not the modulus — off by a factor of $2^m/m$.",
                            "Not the accumulator's modulus.",
                        ],
                    },
                    {
                        "prompt": "The phase error builds up and snaps back. What shape is that?",
                        "hole": "?",
                        "opts": ["a sawtooth", "a sinusoid", "white noise", "a square wave"],
                        "a": 0,
                        "why": "The instantaneous divide ratio is wrong in the same direction until the accumulator overflows, so the phase error ramps and then resets — a sawtooth at the overflow rate. Its harmonics are the fractional spurs, and they are deterministic, which is what makes them so much more objectionable than an equivalent amount of noise.",
                        "whys": [
                            "The instantaneous divide ratio is wrong in the same direction until the accumulator overflows, so the phase error ramps and then resets — a sawtooth at the overflow rate. Its harmonics are the fractional spurs, and they are deterministic, which is what makes them so much more objectionable than an equivalent amount of noise.",
                            "A sinusoid would produce a single clean tone; the sawtooth's harmonic series is what makes the spur pattern so hard to plan around.",
                            "It would be far less troublesome if it were noise — that is precisely what delta-sigma turns it into.",
                            "The error accumulates gradually rather than jumping between two levels.",
                        ],
                    },
                    {
                        "prompt": "And what does a delta-sigma modulator do about it?",
                        "hole": "?",
                        "opts": [
                            "shapes the error to high frequency, where the loop filters it",
                            "removes the error entirely",
                            "reduces the average error to zero",
                            "makes the divide ratio non-integer",
                        ],
                        "a": 0,
                        "why": "It randomises the sequence of integer divides so the error stops being periodic, and shapes its spectrum so most of the power lands well above the loop bandwidth, where the loop filter removes it. The total error is not reduced — it is moved somewhere harmless. That is the same bargain as in an audio converter, which is why the same modulator appears in both.",
                        "whys": [
                            "It randomises the sequence of integer divides so the error stops being periodic, and shapes its spectrum so most of the power lands well above the loop bandwidth, where the loop filter removes it. The total error is not reduced — it is moved somewhere harmless. That is the same bargain as in an audio converter, which is why the same modulator appears in both.",
                            "The instantaneous error is still there and is in fact larger, since the modulator uses a range of divide values rather than two.",
                            "The plain accumulator already has zero average error — that was never the problem. The problem is its spectrum.",
                            "The divider still divides by integers. Nothing changes that; only the sequence of them changes.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A fractional-N accumulator and its spurs",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
Build the modulator itself, in integers, and measure what it does.

`accumulator(k, m, steps)` runs an `m`-bit accumulator: each step add `k`, and if the
result reaches `2**m`, subtract `2**m` and emit a carry of 1, otherwise emit 0.
Return the list of carries. Keep it in Python integers — this is exact arithmetic and
floating point would hide the point.

`divide_sequence(n_int, k, m, steps)` returns `n_int + carry` for each step.

`cumulative_error(seq, k, m)` returns the running sum of `seq - (n_int + k/2**m)` as
a NumPy array, where `n_int` is `seq[0]` rounded down to the lower of the two divide
ratios — simply use `min(seq)`. This is the phase error, in VCO cycles.

`sequence_period(seq)` returns the smallest `p` dividing `len(seq)` such that
`seq[i] == seq[i % p]` for every `i`.

`error_spectrum(seq)` removes the mean, takes `np.fft.rfft`, divides by the length,
and returns the squared magnitude — the power in each bin.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def accumulator(k, m, steps):
    """Run an m-bit accumulator fed k each cycle. Return the list of carry bits."""
    mod = 1 << int(m)
    acc = 0
    out = []
    # TODO: add k, test against mod, subtract on overflow, record the carry.
    return out


def divide_sequence(n_int, k, m, steps):
    """The instantaneous divide ratio each reference cycle."""
    # TODO
    return []


def cumulative_error(seq, k, m):
    """Running sum of the divide error, in VCO cycles."""
    seq = np.asarray(seq, dtype=float)
    # TODO: subtract the average ratio, then cumulative-sum.
    return np.zeros_like(seq)


def sequence_period(seq):
    """Smallest p dividing len(seq) with seq[i] == seq[i % p] for all i."""
    # TODO
    return len(seq)


def error_spectrum(seq):
    """Power in each rfft bin of the mean-removed sequence."""
    x = np.asarray(seq, dtype=float)
    # TODO
    return np.zeros(len(x) // 2 + 1)


if __name__ == "__main__":
    seq = divide_sequence(100, 397, 10, 1024)
    print("average divide ratio:", np.mean(seq), "wanted", 100 + 397 / 1024)
    print("peak phase error, VCO cycles:", round(float(np.max(np.abs(
        cumulative_error(seq, 397, 10)))), 6))
    print("period:", sequence_period(seq))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def accumulator(k, m, steps):
    """Run an m-bit accumulator fed k each cycle. Return the list of carry bits."""
    mod = 1 << int(m)
    acc = 0
    out = []
    for _ in range(int(steps)):
        acc = acc + int(k)
        carry = 1 if acc >= mod else 0
        if carry:
            acc = acc - mod
        out.append(carry)
    return out


def divide_sequence(n_int, k, m, steps):
    """The instantaneous divide ratio each reference cycle."""
    return [int(n_int) + c for c in accumulator(k, m, steps)]


def cumulative_error(seq, k, m):
    """Running sum of the divide error, in VCO cycles."""
    seq = np.asarray(seq, dtype=float)
    n_int = float(np.min(seq))
    mean = n_int + float(k) / float(1 << int(m))
    return np.cumsum(seq - mean)


def sequence_period(seq):
    """Smallest p dividing len(seq) with seq[i] == seq[i % p] for all i."""
    n = len(seq)
    for p in range(1, n + 1):
        if n % p:
            continue
        if all(seq[i] == seq[i % p] for i in range(n)):
            return p
    return n


def error_spectrum(seq):
    """Power in each rfft bin of the mean-removed sequence."""
    x = np.asarray(seq, dtype=float)
    x = x - x.mean()
    spec = np.fft.rfft(x) / len(x)
    return np.abs(spec) ** 2


if __name__ == "__main__":
    seq = divide_sequence(100, 397, 10, 1024)
    print("average divide ratio:", np.mean(seq), "wanted", 100 + 397 / 1024)
    print("peak phase error, VCO cycles:", round(float(np.max(np.abs(
        cumulative_error(seq, 397, 10)))), 6))
    print("period:", sequence_period(seq))
'''}],
                "hints": [
                    "The carry is `1 if acc >= mod else 0`, and the subtraction happens only when it is 1 — that leftover is the phase error the loop still has to absorb.",
                    "`cumulative_error` wants `np.cumsum`, not a Python loop; the whole point is that the running sum stays bounded.",
                    "`sequence_period` only needs to test divisors of the length, so `if n % p: continue` before the expensive check.",
                    "In `error_spectrum`, dividing the FFT by `len(x)` is what makes a tone of amplitude `a` show up with power `(a/2)**2`.",
                ],
                "tests": [
                    {"name": "the accumulator overflows exactly K times per period", "code": r'''
_c = accumulator(397, 10, 1024)
assert len(_c) == 1024, f"expected 1024 carries, got {len(_c)}"
assert set(_c) <= {0, 1}, "a carry is one bit: the accumulator can only ever swallow one cycle"
assert sum(_c) == 397, \
    f"over one full period of 2^10 cycles the accumulator must overflow exactly K = 397 times, got {sum(_c)}"
'''},
                    {"name": "the average divide ratio is exactly the fraction asked for", "code": r'''
import numpy as np
_seq = divide_sequence(100, 397, 10, 1024)
assert set(_seq) == {100, 101}, \
    f"the instantaneous ratio is only ever N or N+1, got {sorted(set(_seq))}"
_avg = float(np.mean(_seq))
assert abs(_avg - (100 + 397 / 1024)) < 1e-12, \
    f"the average must be N + K/2^m = 100.3876953125 exactly, got {_avg!r}"
'''},
                    {"name": "the phase error never exceeds one VCO cycle", "code": r'''
import numpy as np
_seq = divide_sequence(100, 397, 10, 1024)
_e = cumulative_error(_seq, 397, 10)
_peak = float(np.max(np.abs(_e)))
assert abs(_peak - 0.9990234375) < 1e-9, \
    (f"the accumulator holds the error, so the running sum peaks just under one cycle "
     f"(0.99902); got {_peak:.6f}")
assert abs(float(_e[-1])) < 1e-9, \
    f"over a whole period the error must return to zero, got {float(_e[-1]):.3e}"
'''},
                    {"name": "a fraction that shares factors with 2^m repeats early", "code": r'''
_short = divide_sequence(100, 256, 10, 1024)
assert sequence_period(_short) == 4, \
    ("K = 256 with m = 10 is the fraction 1/4, so the pattern repeats every 4 cycles "
     f"and puts a spur at f_ref/4; got a period of {sequence_period(_short)}")
_long = divide_sequence(100, 397, 10, 1024)
assert sequence_period(_long) == 1024, \
    (f"K = 397 is odd, so gcd(K, 2^m) = 1 and the period is the full 1024; "
     f"got {sequence_period(_long)}")
'''},
                    {"name": "a short period puts its energy in one bin", "code": r'''
import numpy as np
_p = error_spectrum(divide_sequence(100, 256, 10, 1024))
_worst = int(np.argmax(_p))
assert _worst == 256, \
    (f"a period-4 pattern in a 1024-point record is a tone at bin 1024/4 = 256, "
     f"got bin {_worst}")
assert abs(float(_p[_worst]) - 0.0625) < 1e-9, \
    f"that spur carries (1/4)^2 = 0.0625 of the power, got {float(_p[_worst]):.6f}"
'''},
                    {"name": "the error energy is pushed to high frequencies", "code": r'''
import numpy as np
_p = error_spectrum(divide_sequence(100, 397, 10, 1024))
_n = len(_p)
_lo = float(np.sum(_p[1:_n // 10]))
_hi = float(np.sum(_p[-(_n // 10):]))
assert _hi > 20.0 * _lo, \
    (f"first-order shaping should leave far more energy near f_ref/2 than near DC: "
     f"got {_hi:.3e} high against {_lo:.3e} low, a ratio of {_hi/_lo:.1f}")
'''},
                    {"name": "resolution is the reference divided by two to the m", "code": r'''
import numpy as np
_a = float(np.mean(divide_sequence(100, 397, 10, 1024)))
_b = float(np.mean(divide_sequence(100, 398, 10, 1024)))
_step = (_b - _a) * 40e6
assert abs(_step - 40e6 / 1024) < 1e-6, \
    (f"one LSB of K moves the output by f_ref/2^m = 39.0625 kHz on a 40 MHz reference; "
     f"got {_step/1e3:.4f} kHz")
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Size the loop filter of a 2.4 GHz fractional-N synthesiser",
        "runtime": "python",
        "minutes": 130,
        "brief": r'''
A 2.4 GHz fractional-N synthesiser on a 40 MHz reference, so the integer part of the
divide ratio is 60. The charge pump delivers 1 mA, the VCO tunes at 40 MHz/V, the
reference contributes a flat $10^{-16}$ rad²/Hz at the phase detector, the
free-running VCO contributes $1/f^2$ rad²/Hz, and a second-order MASH modulator sets
the fractional part.

`synth.py` holds those constants and the quantisation-noise density of the
modulator. Do not edit it.

Your job is the loop filter, and the number that justifies it.

1. `loop_filter(icp, kvco, n_div, wn, zeta)` — invert the module-2 expressions and
   return `(r, c)` for a requested natural frequency and damping.
2. `loop_params(icp, kvco, n_div, r, c)` — the forward direction, so the two can be
   round-tripped against each other.
3. `transfer_magnitudes(f, wn, zeta, n_div)` — the *exact* second-order transfers,
   not the single-pole approximation of module 3:

```text
H_ref(s) = n_div * (2*zeta*wn*s + wn**2) / (s**2 + 2*zeta*wn*s + wn**2)
H_vco(s) = s**2 / (s**2 + 2*zeta*wn*s + wn**2)
```

   with `s = 2j*pi*f`. Return the two magnitude arrays.
4. `output_phase_noise(f, wn, zeta, n_div)` — reference, VCO and modulator summed.
   The modulator noise enters where the reference does, so it is shaped by
   `H_ref/n_div`, which is unity in band.
5. `rms_jitter(f, s, f_carrier)` — trapezoidal integral, then
   `sqrt(2*area)/(2*pi*f_carrier)`.
6. `choose_bandwidth(f, candidates, zeta, n_div)` — return the candidate natural
   frequency in hertz with the smallest RMS jitter.

## Suggested order

Get `loop_filter` and `loop_params` agreeing first: they are inverses and the check
says so. Then the transfers, which have closed-form values at DC and at infinity you
can verify by hand. Only then integrate.

The result you should be able to defend in the comment at the top of `main.py`: the
optimum here is roughly a decade below the crossover module 3 predicted, because the
modulator adds noise exactly where the loop is still passing it.
''',
        "deliverables": [
            "`loop_filter` and `loop_params` as exact inverses of each other, returning component values in ohms and farads.",
            "`transfer_magnitudes` giving the exact second-order reference and VCO transfers, including the zero contributed by the loop filter resistor.",
            "`output_phase_noise` summing all three contributions, with the modulator noise shaped by the normalised low-pass rather than by `H_ref` itself.",
            "`rms_jitter` and `choose_bandwidth`, the second returning the natural frequency that minimises the first over the integration band.",
            "A comment at the top of `main.py` naming the natural frequency and damping you chose, the R and C they imply, and the jitter number that justifies the choice.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, and no synthesiser or filter package.",
            "Do not edit `synth.py`; the checks read its constants and would then be measuring a different design.",
            "`transfer_magnitudes` must use the exact second-order forms. The single-pole approximation is off by more than 3 dB near the bandwidth and will fail the peaking check.",
            "Integrate over the band `synth.F_LO_INT` to `synth.F_HI_INT` only. Extending it changes every jitter number and makes the comparisons meaningless.",
        ],
        "rubric": [
            {"criterion": "Component sizing", "weight": 20,
             "evidence": "loop_filter and loop_params round-trip to within 1e-9 on at least two different specifications, and the returned R and C are physically sensible values."},
            {"criterion": "Exact loop transfers", "weight": 25,
             "evidence": "H_ref equals N at DC and rolls off as one over f far out, H_vco is unity far out and falls as f squared in band, and the peaking near the bandwidth matches the closed form."},
            {"criterion": "Noise budget", "weight": 25,
             "evidence": "All three contributions appear with the right shaping, the in-band floor matches N squared times the reference density, and the modulator term rises with offset frequency."},
            {"criterion": "Bandwidth decision", "weight": 20,
             "evidence": "choose_bandwidth returns the minimum of the integrated jitter over the supplied candidates, and that jitter beats a bandwidth a decade either side of it."},
            {"criterion": "Design defence", "weight": 10,
             "evidence": "The comment at the top of main.py states the chosen wn, zeta, R, C and jitter, and explains why the answer sits below the module-3 crossover."},
        ],
        "hints": [
            "Inverting module 2: `c = icp*kvco/(2*pi*n_div*wn**2)`, and then `r = 2*zeta/(wn*c)` since `zeta = 0.5*r*wn*c`.",
            "Build `s = 2j*np.pi*f` once and reuse it; `np.abs` of the complex ratio gives the magnitude directly, with no algebra to get wrong.",
            "`H_ref/n_div` is the normalised low-pass — unity at DC. Multiply the modulator density by the square of it, not by the square of `H_ref`.",
            "`choose_bandwidth` is a loop over the candidates calling your own `rms_jitter`; nothing cleverer is needed, and a grid of a few hundred points resolves the minimum well.",
        ],
        "files": [
            {"name": "synth.py", "ro": True, "content": r'''
"""The synthesiser specification. Do not edit — the checks rely on these numbers."""
import numpy as np

TWO_PI = 2.0 * np.pi

F_REF = 40e6          # reference frequency, Hz
N_DIV = 60.0          # integer part of the divide ratio
F_OUT = 2.4e9         # carrier, Hz
I_CP = 1e-3           # charge pump current, A
K_VCO = TWO_PI * 40e6 # VCO sensitivity, rad/s per volt

S_REF = 1e-16         # reference phase noise at the detector, rad^2/Hz, flat
K_VCO_NOISE = 1.0     # free-running VCO noise is K_VCO_NOISE / f^2, rad^2/Hz
DS_ORDER = 2          # MASH 1-1 modulator

F_LO_INT = 1e3        # integrate the jitter from here
F_HI_INT = 20e6       # to here, half the reference


def ds_psd(f):
    """Modulator quantisation noise referred to the output, rad^2/Hz, unfiltered.

    Riley's result for an order-L MASH: the quantiser contributes a phase step of
    2*pi/f_ref spread over the reference band, differenced L-1 times.
    """
    f = np.asarray(f, dtype=float)
    shaping = (2.0 * np.sin(np.pi * f / F_REF)) ** (2 * (DS_ORDER - 1))
    return (TWO_PI ** 2 / (12.0 * F_REF)) * shaping
'''},
            {"name": "main.py", "content": r'''
import numpy as np
import synth

# Chosen design:
#   wn   -> TODO Hz, and why
#   zeta -> TODO, and why
#   R, C -> TODO
#   integrated jitter -> TODO


def loop_filter(icp, kvco, n_div, wn, zeta):
    """Return (r, c) giving the requested natural frequency and damping."""
    # TODO: invert wn = sqrt(icp*kvco/(2*pi*n_div*c)) and zeta = 0.5*r*wn*c.
    return 0.0, 0.0


def loop_params(icp, kvco, n_div, r, c):
    """Return (wn, zeta) for a series R-C loop filter."""
    # TODO
    return 0.0, 0.0


def transfer_magnitudes(f, wn, zeta, n_div):
    """Return (|H_ref|, |H_vco|) at the offset frequencies f."""
    f = np.asarray(f, dtype=float)
    # TODO: s = 2j*pi*f, then the two exact second-order transfers.
    return np.zeros_like(f), np.zeros_like(f)


def output_phase_noise(f, wn, zeta, n_div):
    """Total output phase noise density in rad^2/Hz: reference, VCO, modulator."""
    f = np.asarray(f, dtype=float)
    # TODO
    return np.zeros_like(f)


def rms_jitter(f, s, f_carrier):
    """Trapezoidal integral of the density, converted to seconds RMS."""
    # TODO
    return 0.0


def choose_bandwidth(f, candidates, zeta, n_div):
    """Return the candidate natural frequency in Hz with the least jitter."""
    # TODO
    return 0.0


if __name__ == "__main__":
    f = np.logspace(3, np.log10(synth.F_HI_INT), 4001)
    fn = choose_bandwidth(f, np.logspace(3.5, 7, 141), 0.707, synth.N_DIV)
    print("chosen natural frequency:", round(fn / 1e3, 2), "kHz")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
import synth

# Chosen design:
#   wn   -> 21.1 kHz. The module-3 crossover for this reference and VCO is 1.67 MHz,
#           but the MASH-2 modulator adds noise that the loop passes below its own
#           bandwidth, so the integral is minimised nearly two decades lower.
#   zeta -> 0.707. Enough damping that the noise peak near wn is under 1 dB, without
#           the extra settling time a higher value would cost.
#   R, C -> 282 ohm, 37.8 nF at that natural frequency. The capacitor is large
#           because the loop is slow; on silicon that is an off-chip part.
#   integrated jitter -> 0.84 ps RMS from 1 kHz to 20 MHz.


def loop_filter(icp, kvco, n_div, wn, zeta):
    """Return (r, c) giving the requested natural frequency and damping."""
    c = icp * kvco / (2.0 * np.pi * n_div * wn * wn)
    r = 2.0 * zeta / (wn * c)
    return float(r), float(c)


def loop_params(icp, kvco, n_div, r, c):
    """Return (wn, zeta) for a series R-C loop filter."""
    wn = float(np.sqrt(icp * kvco / (2.0 * np.pi * n_div * c)))
    zeta = float(0.5 * r * wn * c)
    return wn, zeta


def transfer_magnitudes(f, wn, zeta, n_div):
    """Return (|H_ref|, |H_vco|) at the offset frequencies f."""
    f = np.asarray(f, dtype=float)
    s = 2j * np.pi * f
    den = s * s + 2.0 * zeta * wn * s + wn * wn
    h_ref = n_div * (2.0 * zeta * wn * s + wn * wn) / den
    h_vco = (s * s) / den
    return np.abs(h_ref), np.abs(h_vco)


def output_phase_noise(f, wn, zeta, n_div):
    """Total output phase noise density in rad^2/Hz: reference, VCO, modulator."""
    f = np.asarray(f, dtype=float)
    h_ref, h_vco = transfer_magnitudes(f, wn, zeta, n_div)
    low = h_ref / n_div
    ref = h_ref ** 2 * synth.S_REF
    vco = h_vco ** 2 * (synth.K_VCO_NOISE / (f * f))
    mod = low ** 2 * synth.ds_psd(f)
    return ref + vco + mod


def rms_jitter(f, s, f_carrier):
    """Trapezoidal integral of the density, converted to seconds RMS."""
    f = np.asarray(f, dtype=float)
    s = np.asarray(s, dtype=float)
    area = float(np.sum(0.5 * (s[1:] + s[:-1]) * np.diff(f)))
    return float(np.sqrt(2.0 * area) / (2.0 * np.pi * f_carrier))


def choose_bandwidth(f, candidates, zeta, n_div):
    """Return the candidate natural frequency in Hz with the least jitter."""
    best = None
    best_val = None
    for fn in np.asarray(candidates, dtype=float):
        s = output_phase_noise(f, 2.0 * np.pi * fn, zeta, n_div)
        val = rms_jitter(f, s, synth.F_OUT)
        if best_val is None or val < best_val:
            best_val = val
            best = fn
    return float(best)


if __name__ == "__main__":
    f = np.logspace(3, np.log10(synth.F_HI_INT), 4001)
    fn = choose_bandwidth(f, np.logspace(3.5, 7, 141), 0.707, synth.N_DIV)
    wn = 2.0 * np.pi * fn
    r, c = loop_filter(synth.I_CP, synth.K_VCO, synth.N_DIV, wn, 0.707)
    print("chosen natural frequency:", round(fn / 1e3, 2), "kHz")
    print("R =", round(r, 1), "ohm   C =", round(c * 1e9, 2), "nF")
    print("jitter:", rms_jitter(f, output_phase_noise(f, wn, 0.707, synth.N_DIV),
                                synth.F_OUT))
'''},
        ],
        "tests": [
            {"name": "the filter and the parameters are inverses", "code": r'''
import numpy as np
import synth
for _fn, _z in ((1e5, 0.707), (2e4, 1.2)):
    _wn = 2.0 * np.pi * _fn
    _r, _c = loop_filter(synth.I_CP, synth.K_VCO, synth.N_DIV, _wn, _z)
    _wn2, _z2 = loop_params(synth.I_CP, synth.K_VCO, synth.N_DIV, _r, _c)
    assert abs(_wn2 - _wn) / _wn < 1e-9, \
        f"asked for wn = {_wn:.1f} rad/s, the components give back {_wn2:.1f}"
    assert abs(_z2 - _z) < 1e-9, f"asked for zeta = {_z}, got back {_z2}"
'''},
            {"name": "the sized components are the expected values", "code": r'''
import numpy as np
import synth
_r, _c = loop_filter(synth.I_CP, synth.K_VCO, synth.N_DIV, 2.0 * np.pi * 1e5, 0.707)
assert abs(_c - 1.6886863940389632e-09) < 1e-13, \
    f"C = icp*kvco/(2*pi*N*wn^2) should be 1.6887 nF at 100 kHz, got {_c*1e9:.4f} nF"
assert abs(_r - 1332.66360365279) < 1e-6, \
    f"R = 2*zeta/(wn*C) should be 1332.7 ohm, got {_r:.1f} ohm"
'''},
            {"name": "the loop transfers have the right asymptotes", "code": r'''
import numpy as np
import synth
_f = np.array([1e2, 1e5, 1e8])
_hr, _hv = transfer_magnitudes(_f, 2.0 * np.pi * 1e5, 0.707, synth.N_DIV)
assert abs(_hr[0] - synth.N_DIV) < 1e-3, \
    f"at DC the reference is multiplied by N = 60, got {_hr[0]:.4f}"
assert abs(_hv[0] - 1e-6) < 1e-9, \
    f"in band the VCO transfer falls as (f/fn)^2, so 1e-6 at fn/1000; got {_hv[0]:.3e}"
assert abs(_hv[2] - 1.0) < 1e-4, \
    f"far outside the loop the VCO is untouched, got {_hv[2]:.6f}"
assert _hr[1] > synth.N_DIV, \
    (f"the loop filter zero makes |H_ref| peak above N near the bandwidth: "
     f"expected more than 60 at fn, got {_hr[1]:.2f}")
'''},
            {"name": "the exact transfer peaks by the amount the zero implies", "code": r'''
import numpy as np
import synth
_hr, _hv = transfer_magnitudes(np.array([1e5]), 2.0 * np.pi * 1e5, 0.707, synth.N_DIV)
assert abs(_hr[0] - 73.48839203612446) < 1e-6, \
    (f"at f = fn with zeta = 0.707 the exact |H_ref| is 73.488, not 60 and not 42.4 — "
     f"got {_hr[0]:.4f}. The single-pole approximation does not have this peak.")
assert abs(_hv[0] - 0.7072135785292428) < 1e-9, \
    f"at f = fn the VCO transfer is 0.70721, got {_hv[0]:.6f}"
'''},
            {"name": "all three noise contributions are present and correctly shaped", "code": r'''
import numpy as np
import synth
_wn = 2.0 * np.pi * 1e5
_lo = output_phase_noise(np.array([1e3]), _wn, 0.707, synth.N_DIV)[0]
assert abs(_lo - 3.7210175881760306e-13) < 1e-15, \
    (f"at 1 kHz the output is dominated by N^2 * S_ref = 3.6e-13 rad^2/Hz; "
     f"got {_lo:.4e}")
_a = output_phase_noise(np.array([1e5]), _wn, 0.707, synth.N_DIV)[0]
_b = output_phase_noise(np.array([1e4]), _wn, 0.707, synth.N_DIV)[0]
assert _a > 10.0 * _b, \
    (f"the modulator noise rises steeply across the loop bandwidth: expected the "
     f"density at 100 kHz to dwarf the one at 10 kHz, got {_a:.3e} against {_b:.3e}")
'''},
            {"name": "jitter integrates a flat spectrum correctly", "code": r'''
import numpy as np
_f = np.linspace(1e3, 1e6, 200001)
_s = np.full_like(_f, 1e-14)
_j = rms_jitter(_f, _s, 1e9)
assert abs(_j - 2.2496651135079577e-14) < 1e-18, \
    (f"a flat 1e-14 rad^2/Hz across 999 kHz on a 1 GHz carrier is 22.5 fs RMS; "
     f"got {_j:.4e} — check the factor of 2 and the 2*pi")
'''},
            {"name": "the chosen bandwidth is the minimum of the jitter curve", "code": r'''
import numpy as np
import synth
_f = np.logspace(3, np.log10(synth.F_HI_INT), 4001)
_c = np.logspace(3.5, 7, 141)
_fn = choose_bandwidth(_f, _c, 0.707, synth.N_DIV)
assert abs(_fn - 21134.890398366475) < 2e3, \
    (f"the minimum over this grid sits at 21.1 kHz, far below the module-3 crossover "
     f"of 1.67 MHz because of the modulator; got {_fn/1e3:.2f} kHz")
_best = rms_jitter(_f, output_phase_noise(_f, 2 * np.pi * _fn, 0.707, synth.N_DIV), synth.F_OUT)
assert abs(_best - 8.417457123358949e-13) < 1e-15, \
    f"expected 0.84 ps RMS at the optimum, got {_best*1e12:.3f} ps"
'''},
            {"name": "a decade either side of the optimum is worse", "code": r'''
import numpy as np
import synth
_f = np.logspace(3, np.log10(synth.F_HI_INT), 4001)
_fn = 21134.890398366475
_best = rms_jitter(_f, output_phase_noise(_f, 2 * np.pi * _fn, 0.707, synth.N_DIV), synth.F_OUT)
_wide = rms_jitter(_f, output_phase_noise(_f, 2 * np.pi * _fn * 10, 0.707, synth.N_DIV), synth.F_OUT)
_narrow = rms_jitter(_f, output_phase_noise(_f, 2 * np.pi * _fn / 10, 0.707, synth.N_DIV), synth.F_OUT)
assert _best < _wide and _best < _narrow, \
    (f"the optimum must beat both neighbours: {_best:.3e} against {_wide:.3e} wide "
     f"and {_narrow:.3e} narrow")
assert _wide > 3.0 * _best, \
    "widening by a decade lets the modulator noise straight through and should cost several times the jitter"
'''},
        ],
    },
}
