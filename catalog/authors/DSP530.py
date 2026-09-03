"""DSP530 — Fixed-Point and Embedded DSP.

Written to the same rules as CTRL510:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; no scipy, no control or DSP libraries
  * seed every RNG, and every expected value here was produced by running the code

Every number in a test was measured, not assumed. The three that matter most —
the q^2/12 noise floor, the pole migration of an expanded direct form, and the
6-LSB zero-input limit cycle of the capstone filter — were computed before the
checks that assert them were written.
"""

COURSE = {
    "id": "DSP530",
    "title": "Fixed-Point and Embedded DSP",
    "band": 3,
    "level": "Expert",
    "prereqs": ["DSP510"],
    "stack": ["Python", "NumPy"],
    "credits": 12,
    "hours": 150,
    "icon": "◊",
    "summary": (
        "A filter that is correct in double precision can be useless in a 16-bit part. "
        "The coefficients move, the accumulator overflows, the rounding you cannot avoid "
        "feeds back through the poles, and a filter with no input refuses to go quiet. "
        "This course treats finite word length as a design variable rather than an "
        "annoyance: how many bits, where the binary point goes, which structure to "
        "implement, and what each choice costs in signal-to-noise and in stability."
    ),
    "outcomes": [
        "Read and write Q(m.f) formats, and predict the resolution, range and overflow behaviour of an arithmetic chain before running it.",
        "Predict a quantiser's noise floor from its step size, and derive the signal-to-noise ratio of a full-scale sine in B bits.",
        "Scale a filter so that it cannot overflow, and explain what that scaling costs in dynamic range.",
        "Choose between a cascade of biquads and an expanded direct form on the basis of pole sensitivity, and defend the choice numerically.",
        "Predict the deadband of a recursive filter and say which rounding rule removes its zero-input limit cycle.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that implements a fourth-order Butterworth filter in Q15 and defends every word length in it.",
    "reading": [
        "*Discrete-Time Signal Processing*, Oppenheim & Schafer — chapter 6, structures and finite word-length effects.",
        "*Digital Signal Processing*, Ifeachor & Jervis — the implementation chapters, for scaling in practice.",
        "*Handbook of Floating-Point Arithmetic*, Muller et al. — chapter 2, for what rounding actually promises.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Q formats and the quantisation floor",
            "summary": "A fixed-point number is an integer with a promise about where the point is. The promise costs resolution, and the resolution has a measurable noise power.",
            "concepts": [
                "Q(m.f) notation: `m` integer bits, `f` fractional bits, one sign bit, and a step of $2^{-f}$ between adjacent codes.",
                "The range is asymmetric — two's complement has one more negative code than positive, so the top of the range is $2^m - 2^{-f}$, never $2^m$.",
                "Multiplying Q(m.f) by Q(m.f) gives Q(2m+1.2f): the product needs a full-width accumulator and has a redundant sign bit.",
                "Rounding error is bounded by $q/2$ and behaves, for a busy signal, like white noise of power $q^2/12$.",
                "Truncation is not rounding: it has a DC bias of $-q/2$ for two's complement, which a recursive filter will integrate.",
            ],
            "read": [
                {
                    "title": "Ninety-eight decibels, and where they came from",
                    "minutes": 16,
                    "body": r'''
On the bench: a 16-bit codec, a generator putting a full-scale 1 kHz sine into it, and an
analyser on the digital output. The tone reads 0 dBFS and there is a floor 98 dB beneath
it. Turn the generator down by 40 dB. The tone follows it down; the floor does not move.

The second measurement is the one worth staring at. A floor that ignores the signal is
not arriving from the analogue front end, where thermal noise and signal scale together
and the ratio between them is fixed. It is being manufactured inside the converter, at a
level set by the word length and by nothing else whatever.

```python
import math


def quantise(x, frac_bits):
    """Round x onto the grid of a format with this many fractional bits."""
    q = 2.0 ** -frac_bits
    return round(x / q) * q


def measure(amplitude, frac_bits, count=40000):
    """Mean-square error and signal-to-noise ratio for a quantised sine."""
    sig2 = 0.0
    err2 = 0.0
    for n in range(count):
        x = amplitude * math.sin(2.0 * math.pi * 0.0123456 * n)
        e = quantise(x, frac_bits) - x
        sig2 += x * x
        err2 += e * e
    return err2 / count, 10.0 * math.log10(sig2 / err2)


q = 2.0 ** -15
for amp in (1.0, 0.01):
    power, snr = measure(amp, 15)
    print(f"amplitude {amp:<6} noise power {power:.4e}   SNR {snr:6.2f} dB")
print(f"q*q/12 for q = 2**-15        {q * q / 12:.4e}")
print(f"6.02 * 16 + 1.76             {6.02 * 16 + 1.76:6.2f} dB")
```

```text
amplitude 1.0    noise power 7.7185e-11   SNR  98.11 dB
amplitude 0.01   noise power 7.9027e-11   SNR  58.01 dB
q*q/12 for q = 2**-15        7.7610e-11
6.02 * 16 + 1.76              98.08 dB
```

A hundredfold drop in amplitude, and the noise power moved by half a percent. Forty
decibels came off the ratio because forty decibels came off the numerator.

## Where 98 comes from

The converter carries 16 bits across a span running from $-1$ to $+1$, so the codes are
$q = 2/2^{16} = 2^{-15}$ apart. Rounding to nearest can never move a value further than
half that, so every error lies in $\left(-\frac{q}{2}, \frac{q}{2}\right)$. When the
signal moves by many codes between one sample and the next — 2541 of them at the steepest
part of the full-scale sine above — there is no reason for it to favour any part of that
interval over any other, and the errors spread across it evenly. The mean square of a value
uniform on an interval of width $q$ centred on zero is $q^2/12$, which is
$7.761\times10^{-11}$ here against a measured $7.7185\times10^{-11}$.

A full-scale sine has mean square $\frac{1}{2}$, so the ratio is
$\frac{1/2}{q^{2}/12} = \frac{6}{q^{2}} = 6\cdot 2^{30}$, which is 98.09 dB. The derive
unit *The signal-to-noise ratio of a B-bit converter* runs that argument in symbols and
arrives at $\frac{3}{2}\cdot 2^{2B}$; the measurement above is the same statement with
the numbers filled in.

The 58 dB reading is the same formula with the signal 40 dB down, and it is the reason
headroom is expensive. Every decibel of range left unused at the input is a decibel of
converter thrown away, because the floor beneath it will not come down to meet you.

## The point is a promise, and it costs nothing to move

Nothing in a stored word says where the binary point sits. A 16-bit code of $-30521$ is
$-30521$, and it becomes a number by agreement: Q(m.f) means $m$ integer bits, $f$
fractional bits, one sign bit, and a value of code $\times 2^{-f}$.

The choice is real, and one coefficient of the capstone's Butterworth filter shows why.

```python
A1 = -1.86286416          # a denominator coefficient of the capstone's filter


def store(x, int_bits, frac_bits):
    """What a signed Q(int_bits.frac_bits) word ends up holding: code, then value."""
    lo = -(2 ** int_bits)
    hi = 2 ** int_bits - 2.0 ** -frac_bits
    clamped = min(max(x, lo), hi)
    code = round(clamped * 2 ** frac_bits)
    return code, code / 2 ** frac_bits


for m, f in ((0, 15), (1, 14), (2, 13)):
    code, held = store(A1, m, f)
    print(f"Q{m}.{f}   code {code:>7d}   holds {held:+.10f}   off by {abs(held - A1):.3e}")

print()
a_code, a_held = store(A1, 1, 14)
y_code, y_held = store(0.6, 1, 14)
product = a_code * y_code
print("a1 as an integer      ", a_code)
print("y  as an integer      ", y_code)
print("their integer product ", product, f"({product.bit_length()} magnitude bits)")
print("read back as Q3.28    ", product / 2 ** 28)
print("the same in doubles   ", a_held * y_held)
print("rounded into Q1.14    ", round(product / 2 ** 14) / 2 ** 14)
print("the corner case       ", (-2 ** 15) * (-2 ** 15) / 2 ** 28)
```

```text
Q0.15   code  -32768   holds -1.0000000000   off by 8.629e-01
Q1.14   code  -30521   holds -1.8628540039   off by 1.016e-05
Q2.13   code  -15261   holds -1.8629150391   off by 5.088e-05

a1 as an integer       -30521
y  as an integer       9830
their integer product  -300021430 (29 magnitude bits)
read back as Q3.28     -1.1176669225096703
the same in doubles    -1.1176669225096703
rounded into Q1.14     -1.11767578125
the corner case        4.0
```

Q0.15 reaches only to $1 - 2^{-15}$, so $-1.86286416$ arrives at the rail and is stored
as $-1.0$: an error of 0.86. That is not a rounded coefficient, it is a different filter.
The pair still sits at radius 0.9415 — the radius is set by $a_2$, which was untouched —
but its angle moves from 0.1462 rad to 1.0109, so the resonance leaves $0.0233\,f_s$ and
arrives at $0.1609\,f_s$, a factor of seven. Q1.14 reaches to $-2$ and holds the number
to $1.0\times10^{-5}$. Q2.13 also holds it, five times worse, because the extra integer
bit bought range nobody was going to use and was paid for out of the fractional bits.

That is the whole rule, and it follows from the two numbers rather than from anybody's
authority: take the smallest $m$ whose range covers the largest magnitude the variable
will ever hold, and spend every remaining bit on $f$.

The multiply is the same reasoning applied twice. The stored integers are exactly
$-30521$ and $9830$, and their integer product $-300021430$ is exact — no arithmetic has
been lost. What has changed is the promise: each factor was scaled by $2^{-14}$, so the
product is scaled by $2^{-28}$, and the word holding it is Q3.28. Three integer bits and
not two, because the one product a pair of Q1.14 words can reach that a Q2.28 word cannot
is $(-2)\times(-2) = +4$, printed on the last line. Every other product in the format
stays below 4, which is why that top bit is redundant almost always and why DSP parts
offer a fractional multiply mode that shifts the product left by one to reclaim it.

Rounding the full-width product back down gives $-1.11767578125$ against the exact
$-1.1176669225$, an error of $8.9\times10^{-6}$ — inside the half-LSB of $3.05\times10^{-5}$
that Q1.14 promises, as it has to be.

## The mistake: treating truncation as rounding with a different tie-break

Dropping the low bits of a word is free — it is a shift, and on some parts it is not even
that, because the result is already in the high half of the register. Rounding costs an
add before the shift. And the error is under one LSB either way. The reasoning is
appealing enough that truncation is what a first fixed-point port almost always does.

```python
import math


def q_round(x, frac_bits):
    """Round to nearest — what a converter and a well-written DSP routine do."""
    q = 2.0 ** -frac_bits
    return round(x / q) * q


def q_trunc(x, frac_bits):
    """Drop the low bits of a two's complement word: a floor towards minus infinity."""
    q = 2.0 ** -frac_bits
    return math.floor(x / q) * q


def stats(rule, frac_bits, count=40000):
    """Mean and mean square of the error this rule makes on a busy sine."""
    total = 0.0
    square = 0.0
    for n in range(count):
        x = 0.9 * math.sin(2.0 * math.pi * 0.0123456 * n)
        e = rule(x, frac_bits) - x
        total += e
        square += e * e
    return total / count, square / count


q = 2.0 ** -10
for name, rule in (("round to nearest", q_round), ("truncate        ", q_trunc)):
    mean, power = stats(rule, 10)
    print(f"{name}  mean {mean / q:+.4f} q   mean square {power / (q * q):.4f} q^2")
print(f"predicted        round {1 / 12:.4f} q^2      truncate {1 / 12 + 1 / 4:.4f} q^2")
print(f"truncating costs {10 * math.log10((1 / 12 + 1 / 4) / (1 / 12)):.2f} dB")
```

```text
round to nearest  mean -0.0074 q   mean square 0.0844 q^2
truncate          mean -0.4957 q   mean square 0.3282 q^2
predicted        round 0.0833 q^2      truncate 0.3333 q^2
truncating costs 6.02 dB
```

Truncating a two's complement word discards the fraction, which is a floor towards
$-\infty$ rather than a move towards zero, so the error lands in $(-q, 0]$ instead of
$\left(-\frac{q}{2}, \frac{q}{2}\right)$. The interval is the same width, so the variance
is the same $q^{2}/12$ — but it is no longer centred, and mean square is variance plus
the square of the mean: $\frac{q^{2}}{12} + \frac{q^{2}}{4} = \frac{q^{2}}{3}$. Four
times the power, which the derive unit's six-decibels-per-bit converts into exactly one
bit. A 16-bit part that truncates is a 15-bit part with a marketing department.

The mean is the more dangerous half of that measurement, because $-0.4957q$ is not noise.
It is a DC offset, and in a recursive structure it is fed back and accumulated: a
first-order section with $a = 0.99$ multiplies a steady bias by $\frac{1}{1-a} = 100$, so
half an LSB at the multiplier arrives at the output as 50 LSBs of offset. Module 4 takes
that mechanism apart.

## Where the model stops holding

Two assumptions carried $q^{2}/12$ here: that the error is spread evenly across a step,
and that it has nothing to do with the signal. Both need the signal to move by several
codes between samples, and both fail when it does not.

```python
import math

q = 2.0 ** -10


def quantise(x):
    return round(x / q) * q


def error_power(amplitude, count=40000):
    """Mean square of the rounding error on a sine of this amplitude."""
    total = 0.0
    for n in range(count):
        x = amplitude * math.sin(2.0 * math.pi * 0.0123456 * n)
        e = quantise(x) - x
        total += e * e
    return total / count


codes = [round(quantise(1.6 * q * math.sin(2.0 * math.pi * 0.0123456 * n)) / q)
         for n in range(20)]
print("a 1.6 LSB sine, in codes:", codes)
for amp in (0.9, 8.0 * q, 1.6 * q):
    print(f"amplitude {amp / q:8.2f} LSB   error power {error_power(amp) / (q * q):.4f} q^2")
print(f"the uniform model says                {1 / 12:.4f} q^2")
```

```text
a 1.6 LSB sine, in codes: [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2]
amplitude   921.60 LSB   error power 0.0844 q^2
amplitude     8.00 LSB   error power 0.0764 q^2
amplitude     1.60 LSB   error power 0.1124 q^2
the uniform model says                0.0833 q^2
```

At 921 LSBs the model is right to half a percent. At 8 LSBs it is still usable. At 1.6
LSBs the output is a three-level staircase locked to the input's own period, the error
power is 35% high, and — far more important than the power — the error is now periodic.
Periodic error is harmonic distortion, which lands in a few places and is audible well
below a hiss of the same power. That is the regime dither exists for: adding a controlled
half-LSB of noise before the quantiser makes the error random again, raising the floor a
little in exchange for removing the tones from it.

The same failure has a second face. Quantise a constant and the error is a constant; no
amount of averaging removes it, and $q^{2}/12$ describes none of it.

## What you are about to build

The lab *A Q-format quantiser and its noise floor* is the five primitives everything
later in this course sits on: `q_step` for the value of one LSB, `quantise` for the snap
onto the grid, `saturate` for the asymmetric two's complement range whose top is
$2^{m} - q$ and never $2^{m}$, `to_fixed` applying them in the order a converter does,
and `noise_power` so a measured floor can be held against the theory rather than trusted.
One of its checks measures a busy signal's floor and insists it is within 5% of
$q^{2}/12$; the last one measures a full-scale sine's ratio and insists it reaches
$\frac{3}{2}\cdot 2^{2B}$. Both are the numbers above, asserted rather than admired.

The sandbox *The other axis of discretisation* is the time axis, in the same room. It is
worth a few minutes precisely because it is the other half of the same act: sampling
misplaces energy in frequency and quantisation misplaces it in amplitude, and in both
cases what has been misplaced becomes indistinguishable from signal the moment it lands.
''',
                },
            ],
            "sandbox": {
                "title": "The other axis of discretisation",
                "visualiser": "spectrum",
                "minutes": 8,
                "initial": {"fsig": 30, "fs": 200},
                "brief": r'''
Digitising a signal discretises two axes. This sandbox is the time axis: samples at
a finite rate, and the aliases that appear when the rate is too low. Fixed-point
arithmetic is the amplitude axis, and it is the one the rest of this course is
about.

They are worth seeing side by side because both take energy that belonged in one
place and put it somewhere else, and in both cases the misplaced energy is
indistinguishable from signal once it has arrived.
''',
                "notice": [
                    "Raise the signal frequency past half the sample rate. The samples stop describing the wave you drew and start describing a slower one that fits them exactly as well — nothing downstream can tell the two apart.",
                    "Set the sample rate to precisely twice the signal frequency. Two points per period is the boundary of the theorem, not a working margin: the samples land on the same two phases forever.",
                    "Sweep the sample rate and watch where the alias lands. It folds about each multiple of half the rate — a single, predictable destination. Quantisation noise, by contrast, spreads across the whole band at once, which is why it is described by a power rather than a frequency.",
                ],
            },
            "derive": {
                "title": "The signal-to-noise ratio of a B-bit converter",
                "minutes": 14,
                "vars": ["B", "q", "X_m", "P_e", "P_x", "sigma_e"],
                "brief": r'''
A signed fixed-point word of $B$ bits in total covers the full-scale span from
$-X_m$ up to just below $+X_m$, dividing it into $2^B$ equal steps of width $q$.

Quantise a full-scale sine — amplitude $X_m$ — and work out how far the signal sits
above the error it picks up. Assume rounding to nearest, and assume the error is
uniformly distributed across one step, which holds whenever the signal moves by
several codes between samples.
''',
                "steps": [
                    {
                        "prompt": "Write the step size $q$ in terms of $X_m$ and $B$.",
                        "answer": "\\frac{2 X_m}{2^{B}}",
                        "hint": "The span is $2X_m$ wide and there are $2^B$ steps across it.",
                        "deconstruct": [
                            "The full-scale span runs from $-X_m$ to $+X_m$, a width of $2X_m$.",
                            "Divide that width by the number of steps, $2^B$.",
                        ],
                    },
                    {
                        "prompt": "The rounding error is uniform on $\\left(-\\frac{q}{2}, \\frac{q}{2}\\right)$. Write its mean square, $P_e$.",
                        "answer": "\\frac{q^{2}}{12}",
                        "hint": "The variance of a uniform distribution on an interval of width $w$ is $w^2/12$.",
                        "deconstruct": [
                            "The interval has width $q$, and the distribution is centred on zero, so the mean square is the variance.",
                            "For a uniform distribution of width $w$ that variance is $w^{2}/12$.",
                        ],
                    },
                    {
                        "prompt": "Write the mean square $P_x$ of a full-scale sine of amplitude $X_m$.",
                        "answer": "\\frac{X_m^{2}}{2}",
                        "hint": "The average of $\\sin^2$ over a whole number of cycles is one half.",
                        "deconstruct": [
                            "The instantaneous power is $X_m^2$ times the square of the sine.",
                            "Averaged over a period, the square of the sine is $1/2$.",
                        ],
                    },
                    {
                        "prompt": "Form the ratio $P_x / P_e$ and substitute your expression for $q$. Write the result in terms of $B$ alone.",
                        "given": "You have $P_x = \\frac{X_m^{2}}{2}$, $P_e = \\frac{q^{2}}{12}$ and $q = \\frac{2X_m}{2^{B}}$.",
                        "answer": "\\frac{3}{2}\\cdot 2^{2B}",
                        "hint": "Substitute $q$ into $P_e$ first: the $X_m^2$ then cancels against the one in $P_x$.",
                        "deconstruct": [
                            "$P_e = \\frac{1}{12}\\cdot\\frac{4X_m^{2}}{2^{2B}} = \\frac{X_m^{2}}{3\\cdot 2^{2B}}$.",
                            "Dividing $P_x$ by that cancels $X_m^{2}$ and leaves $\\frac{3}{2}\\cdot 2^{2B}$.",
                        ],
                    },
                ],
                "closing": r'''
Every extra bit multiplies the ratio by four, which is the familiar "six decibels per
bit", and the constant $3/2$ contributes the further 1.76 dB in the usual figure
$6.02B + 1.76$. That constant is not headroom the sine earns: a full-scale square
wave, whose mean square is $X_m^{2}$ rather than $X_m^{2}/2$, reaches $3 \cdot 2^{2B}$
instead. The sine's crest factor costs 3 dB against that, and 1.76 dB is what is left.

Two assumptions carried the argument and both are routinely violated in practice: that
the error is uniform, and that it is independent of the signal. A quiet, slow signal
breaks both, and the error becomes a periodic distortion you can hear rather than a
noise floor you can ignore. That is the failure mode dither exists to fix.
''',
            },
            "quiz": {
                "title": "An integer with a promise about the point",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What is the step size of a Q(m.f) number?",
                        "opts": ["$2^{-f}$", "$2^{-m}$", "$2^{f}$", "$1/(m+f)$"],
                        "a": 0,
                        "why": r"""
The fractional bits set the resolution and the integer bits set the range — two
independent choices out of a fixed total, which is the entire design decision in fixed
point. Q1.14 resolves $6.1\times10^{-5}$ and saturates just past 2; Q7.8 resolves
$3.9\times10^{-3}$ and reaches 128. Same 16 bits, four hundred times the difference in
resolution.
""",
                    },
                    {
                        "q": "You multiply a Q(m.f) number by another Q(m.f) number. What does the product need?",
                        "opts": [
                            "Q(2m+1 . 2f) — a full-width accumulator",
                            "Q(m.f) — the same format",
                            "Q(m . 2f)",
                            "Q(2m . f)",
                        ],
                        "a": 0,
                        "why": r"""
The fractional bits add and the integer bits add, plus one for the sign interaction. Two
Q1.14 values need Q3.28, which is why a 16×16 multiplier feeds a 32-bit (or 40-bit)
accumulator. Truncating back to Q(m.f) after *every* multiply, rather than accumulating
full width and rounding once at the end, is the most common way to lose 20 dB of SNR in
an FIR filter without noticing.
""",
                    },
                    {
                        "q": "Why is the range of a two's complement fixed-point number asymmetric?",
                        "opts": [
                            "There is one more negative code than positive",
                            "The sign bit is not counted",
                            "Rounding always goes down",
                            "It is not — the asymmetry is a myth",
                        ],
                        "a": 0,
                        "why": r"""
Q1.14 runs from $-2$ to $+2 - 2^{-14}$: the most negative value has no positive
counterpart. Which means negating the most negative number overflows — a real and
frequently shipped bug, since `-x` looks incapable of failing. Saturating negation, or
simply never using the extreme code, is the standard defence.
""",
                    },
                    {
                        "q": "For a quantiser of step $q$, what is the noise power?",
                        "opts": ["$q^2/12$", "$q^2/4$", "$q/2$", "$q^2$"],
                        "a": 0,
                        "why": r"""
The variance of a uniform distribution over one step. It rests on assumptions worth
stating — that the error is uniform, white, and uncorrelated with the signal — and they
fail exactly when the signal is small or periodic, which is when the error becomes an
audible tone rather than a hiss. That failure is what dither is for, and it is the same
mechanism behind the limit cycles in module 4.
""",
                    },
                    {
                        "q": "What does one extra bit of word length buy?",
                        "opts": ["About 6 dB of signal-to-noise ratio", "About 3 dB", "About 10 dB", "A factor of two in bandwidth"],
                        "a": 0,
                        "why": r"""
$20\log_{10}2 = 6.02$ dB, because the step halves and the noise *power* falls by four.
It is the most useful conversion factor in the subject: 16 bits is about 98 dB of
dynamic range, 24 bits about 146 dB, and any claim of a 20-bit converter with a 130 dB
floor can be sanity-checked in one line.
""",
                    },
                ],
            },
            "lab": {
                "title": "A Q-format quantiser and its noise floor",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Build the primitives everything later in the course sits on.

`q_step(frac_bits)` returns the value of one least significant bit: the spacing
between adjacent codes in a format with that many fractional bits.

`quantise(x, frac_bits)` snaps `x` to the nearest multiple of that step, with no
range limit at all. It must work on a scalar and on a numpy array.

`saturate(x, int_bits, frac_bits)` clamps to the representable range of a signed
Q(int_bits.frac_bits) word:

```text
lowest  = -2**int_bits
highest =  2**int_bits - q_step(frac_bits)
```

The range is asymmetric on purpose — that is what two's complement gives you, and
pretending otherwise is how off-by-one-LSB bugs get written.

`to_fixed(x, int_bits, frac_bits)` applies the two in the order a real converter
does: quantise first, then clamp.

`noise_power(x, frac_bits)` returns the mean square of `quantise(x) - x`, so you can
compare a measured floor against the $q^2/12$ you just derived.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def q_step(frac_bits):
    """The value of one LSB in a format with `frac_bits` fractional bits."""
    # TODO: one line, and it is a power of two.
    return 1.0


def quantise(x, frac_bits):
    """Snap x to the nearest multiple of the step. No range limit here."""
    x = np.asarray(x, dtype=float)
    # TODO: divide by the step, round to nearest, multiply back.
    return x


def saturate(x, int_bits, frac_bits):
    """Clamp to the representable range of a signed Q(int_bits.frac_bits) word."""
    x = np.asarray(x, dtype=float)
    # TODO: the top of the range is one LSB below the power of two.
    return x


def to_fixed(x, int_bits, frac_bits):
    """Quantise, then clamp — the order a converter applies them in."""
    # TODO
    return np.asarray(x, dtype=float)


def noise_power(x, frac_bits):
    """Mean square of the quantisation error on x."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print("one LSB of Q1.15:", q_step(15))
    print("0.1 in Q1.15:", float(quantise(0.1, 15)))
    print("3.7 clamped into Q1.15:", float(to_fixed(3.7, 1, 15)))
    rng = np.random.default_rng(20250829)
    signal = rng.uniform(-0.9, 0.9, 200000)
    print("measured floor:", noise_power(signal, 10))
    print("q^2/12       :", q_step(10) ** 2 / 12)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def q_step(frac_bits):
    """The value of one LSB in a format with `frac_bits` fractional bits."""
    return 2.0 ** (-frac_bits)


def quantise(x, frac_bits):
    """Snap x to the nearest multiple of the step. No range limit here."""
    q = q_step(frac_bits)
    return np.round(np.asarray(x, dtype=float) / q) * q


def saturate(x, int_bits, frac_bits):
    """Clamp to the representable range of a signed Q(int_bits.frac_bits) word."""
    q = q_step(frac_bits)
    lo = -(2.0 ** int_bits)
    hi = 2.0 ** int_bits - q
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def to_fixed(x, int_bits, frac_bits):
    """Quantise, then clamp — the order a converter applies them in."""
    return saturate(quantise(x, frac_bits), int_bits, frac_bits)


def noise_power(x, frac_bits):
    """Mean square of the quantisation error on x."""
    x = np.asarray(x, dtype=float)
    e = quantise(x, frac_bits) - x
    return float(np.mean(e * e))


if __name__ == "__main__":
    print("one LSB of Q1.15:", q_step(15))
    print("0.1 in Q1.15:", float(quantise(0.1, 15)))
    print("3.7 clamped into Q1.15:", float(to_fixed(3.7, 1, 15)))
    rng = np.random.default_rng(20250829)
    signal = rng.uniform(-0.9, 0.9, 200000)
    print("measured floor:", noise_power(signal, 10))
    print("q^2/12       :", q_step(10) ** 2 / 12)
'''}],
                "hints": [
                    "`2.0 ** (-frac_bits)` is the whole of `q_step` — keep it a float, or Python integer division will surprise you.",
                    "`np.round` rounds halves to even, which is what a well-behaved converter does and what keeps the error mean at zero.",
                    "`np.clip(x, lo, hi)` does the saturation, and `hi` is `2**int_bits - q`, not `2**int_bits`.",
                    "In `noise_power`, subtract *before* squaring, and use `np.mean` rather than a sum divided by a length you might get wrong.",
                ],
                "tests": [
                    {"name": "one LSB is the right power of two", "code": r'''
assert abs(q_step(15) - 3.0517578125e-05) < 1e-18, \
    f"Q1.15 has a step of 2**-15 = 3.0517578125e-05, got {q_step(15)}"
assert abs(q_step(0) - 1.0) < 1e-15, \
    f"with no fractional bits the step is 1, got {q_step(0)}"
'''},
                    {"name": "quantising lands on the grid and nowhere else", "code": r'''
_q = q_step(15)
_v = float(quantise(0.1, 15))
assert abs(_v - 0.100006103515625) < 1e-15, \
    f"0.1 is not representable in Q1.15; the nearest code is 0.100006103515625, got {_v}"
assert abs(_v / _q - round(_v / _q)) < 1e-9, \
    "the result must be an exact integer multiple of one LSB"
assert abs(_v - 0.1) <= _q / 2 + 1e-18, \
    "rounding to nearest can never be more than half an LSB away"
'''},
                    {"name": "quantise works elementwise on an array", "code": r'''
import numpy as np
_a = quantise(np.array([0.0, 0.3, -0.3, 0.9]), 3)
assert _a.shape == (4,), f"the shape should survive, got {_a.shape}"
assert abs(float(_a[1]) - 0.25) < 1e-15, \
    f"with 3 fractional bits the step is 0.125, so 0.3 becomes 0.25, got {float(_a[1])}"
assert abs(float(_a[2]) + 0.25) < 1e-15, "negative values round symmetrically"
'''},
                    {"name": "the fixed-point range is asymmetric", "code": r'''
_hi = float(to_fixed(3.7, 1, 15))
_lo = float(to_fixed(-9.0, 1, 15))
assert abs(_hi - 1.999969482421875) < 1e-15, \
    f"Q1.15 stops one LSB below 2, at 1.999969482421875, got {_hi}"
assert abs(_lo + 2.0) < 1e-15, \
    f"two's complement reaches -2 exactly, got {_lo} — the range is not symmetric"
'''},
                    {"name": "the measured noise floor is q squared over twelve", "code": r'''
import numpy as np
_rng = np.random.default_rng(20250829)
_x = _rng.uniform(-0.9, 0.9, 200000)
_meas = noise_power(_x, 10)
_theory = q_step(10) ** 2 / 12
assert abs(_meas / _theory - 1.0) < 0.05, \
    f"a busy signal should sit on the uniform-error floor: measured {_meas:.4e}, q^2/12 = {_theory:.4e}"
'''},
                    {"name": "a full-scale sine sits three halves times four to the B above the floor", "code": r'''
import numpy as np
_n = np.arange(40000)
_x = 0.999 * np.sin(2 * np.pi * 0.0123456 * _n)
_snr = 0.5 * 0.999 ** 2 / noise_power(_x, 10)
_theory = 1.5 * 2.0 ** (2 * 11)
assert abs(_snr / _theory - 1.0) < 0.05, \
    f"11 bits total (sign plus 10 fractional) predicts {_theory:.4e}, measured {_snr:.4e}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Coefficient quantisation and where the poles move",
            "summary": "Storing a coefficient to finite precision moves the poles. How far depends entirely on the structure you chose.",
            "concepts": [
                "A coefficient stored in Q(m.f) can only take values on a grid of spacing $2^{-f}$; the poles it implies therefore also live on a grid.",
                "For a direct-form denominator the pole grid is not uniform — it thins out near $z = \\pm 1$, exactly where narrow-band filters put their poles.",
                "Pole sensitivity to a coefficient goes as the reciprocal of the distance between poles, so clustered poles are the dangerous case.",
                "A cascade of second-order sections quantises each pole pair against its own two coefficients, so no pole is sensitive to any other section.",
                "Expanding a cascade into one high-order direct form is algebraically identical and numerically indefensible above about fourth order.",
            ],
            "read": [
                {
                    "title": "The same filter twice, and one of them is an integrator",
                    "minutes": 17,
                    "body": r'''
The capstone's filter is a fourth-order Butterworth low-pass at $f_c/f_s = 0.05$, and it
arrives as two second-order sections. Multiply their denominators together and there is
one quartic instead,
$1 - 3.58719\,z^{-1} + 4.84465222\,z^{-2} - 2.91826783\,z^{-3} + 0.66131735\,z^{-4}$.
The algebra is exact and the two forms are the same transfer function, with every pole in
the same place. Store the coefficients in a word with eight fractional bits — the only
thing that changes — and look again.

```python
import cmath

SECTIONS = [[1.0, -1.86286416, 0.88637718],
            [1.0, -1.72432584, 0.74609023]]


def quad_roots(a):
    """The two roots of a[0] z^2 + a[1] z + a[2]."""
    disc = cmath.sqrt(a[1] * a[1] - 4.0 * a[0] * a[2])
    return [(-a[1] + disc) / (2.0 * a[0]), (-a[1] - disc) / (2.0 * a[0])]


def roots_of(poly, rounds=400):
    """Durand-Kerner from fixed starting points: deterministic, no library."""
    c = [v / poly[0] for v in poly]
    n = len(c) - 1
    z = [(0.4 + 0.9j) ** k for k in range(n)]
    for _ in range(rounds):
        for i in range(n):
            num = 0j
            for v in c:
                num = num * z[i] + v
            den = 1.0 + 0j
            for j in range(n):
                if j != i:
                    den *= z[i] - z[j]
            z[i] -= num / den
    return z


def convolve(f, g):
    out = [0.0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] += a * b
    return out


def quantise(poly, frac_bits):
    """Round every stored coefficient; the leading 1 is structural, not stored."""
    q = 2.0 ** -frac_bits
    out = [round(v / q) * q for v in poly]
    out[0] = 1.0
    return out


quartic = convolve(SECTIONS[0], SECTIONS[1])
exact = [abs(r) for a in SECTIONS for r in quad_roots(a)]
print("exact radii, either way :", [round(v, 6) for v in sorted(exact)])
print("as one quartic          :", [round(v, 6) for v in sorted(abs(z) for z in roots_of(quartic))])
print()
casc = [abs(r) for a in SECTIONS for r in quad_roots(quantise(a, 8))]
dire = [abs(z) for z in roots_of(quantise(quartic, 8))]
print("8-bit coefficients, cascade :", [round(v, 6) for v in sorted(casc)])
print("8-bit coefficients, direct  :", [round(v, 6) for v in sorted(dire)])
```

```text
exact radii, either way : [0.863765, 0.863765, 0.941476, 0.941476]
as one quartic          : [0.863765, 0.863765, 0.941476, 0.941476]

8-bit coefficients, cascade : [0.863767, 0.863767, 0.941657, 0.941657]
8-bit coefficients, direct  : [0.742907, 0.942662, 0.942662, 1.0]
```

The cascade's poles moved in the sixth decimal place. The quartic's inner conjugate pair
has come apart into two real poles, one at 0.7429 and one sitting at exactly $z = 1$. The
filter that was a low-pass now contains an integrator, and it will accumulate whatever DC
offset the arithmetic hands it, without bound and without an input.

## The number that decided it

A denominator written as a polynomial in $z$ factors as $A(z) = \prod_i (z - p_i)$, so
its value at $z = 1$ is $\prod_i (1 - p_i)$ — and evaluating the polynomial at $z = 1$ is
the same as adding up its coefficients. Two ways of computing one quantity, and the
second one is what the stored word length gets to round.

```python
import cmath

SECTIONS = [[1.0, -1.86286416, 0.88637718],
            [1.0, -1.72432584, 0.74609023]]


def quad_roots(a):
    disc = cmath.sqrt(a[1] * a[1] - 4.0 * a[0] * a[2])
    return [(-a[1] + disc) / (2.0 * a[0]), (-a[1] - disc) / (2.0 * a[0])]


def convolve(f, g):
    out = [0.0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] += a * b
    return out


def quantise(poly, frac_bits):
    q = 2.0 ** -frac_bits
    out = [round(v / q) * q for v in poly]
    out[0] = 1.0
    return out


quartic = convolve(SECTIONS[0], SECTIONS[1])
poles = [r for a in SECTIONS for r in quad_roots(a)]
product = 1.0
for p in poles:
    product *= abs(1.0 - p)
print("A(1) as a sum of coefficients :", sum(quartic))
print("A(1) as the product of 1 - p  :", product)
for k, a in enumerate(SECTIONS, 1):
    print(f"section {k}: A(1) = {sum(a):.8f}")
print()
print(" f     grid step    quartic A(1) after rounding")
for f in range(6, 13):
    print(f"{f:2d}   {2.0 ** -f:.4e}    {sum(quantise(quartic, f)):+.8f}")
```

```text
A(1) as a sum of coefficients : 0.000511746537357638
A(1) as the product of 1 - p  : 0.000511746537357799
section 1: A(1) = 0.02351302
section 2: A(1) = 0.02176439

 f     grid step    quartic A(1) after rounding
 6   1.5625e-02    -0.01562500
 7   7.8125e-03    +0.00000000
 8   3.9062e-03    +0.00000000
 9   1.9531e-03    +0.00000000
10   9.7656e-04    +0.00097656
11   4.8828e-04    +0.00000000
12   2.4414e-04    +0.00073242
```

Every pole of a narrow low-pass is near $z = 1$, so every factor $1 - p_i$ is small, and
$A(1)$ is the product of four small numbers: $5.12\times10^{-4}$. The sum of the stored
coefficients lands on the grid, and when the grid step is larger than $A(1)$ the nearest
grid point is zero. A denominator whose coefficients sum to zero has $A(1) = 0$, which
is a root at exactly $z = 1$ — the pole in the first listing, arrived at by arithmetic
rather than by accident.

Each section on its own has $A(1)$ around $2.2\times10^{-2}$, forty-odd times larger,
because it is the product of two small factors rather than four. A grid of $2^{-9}$ is
nowhere near it. That is what the cascade buys, in one number.

## Why one stored coefficient reaches every pole

The derive unit *How far a pole moves when you round a coefficient* does the quadratic
case: hold $a_1$, perturb $a_2$, and $\frac{dp_1}{da_2} = -\frac{1}{p_1 - p_2}$. The same
two lines work at any order. Write the monic denominator as
$A(p) = p^{n} + a_1p^{n-1} + \dots + a_n$, and differentiate $A(p_i) = 0$ with respect to
one stored coefficient $a_k$:

$$A'(p_i)\,\frac{\partial p_i}{\partial a_k} + p_i^{\,n-k} = 0
\qquad\Longrightarrow\qquad
\frac{\partial p_i}{\partial a_k} = -\frac{p_i^{\,n-k}}{\prod_{j \neq i}\left(p_i - p_j\right)}$$

because differentiating $\prod_j (p - p_j)$ and evaluating at $p_i$ leaves only the term
in which the $(p - p_i)$ factor was the one differentiated. With $n = 2$ and $k = 2$ the
numerator is 1 and the product has one factor, which is the derive unit's answer.

The denominator is the whole story. In a biquad it is one distance, from a pole to its
own conjugate. In the quartic it is three distances multiplied together, and each of them
is under 0.3.

```python
import cmath

SECTIONS = [[1.0, -1.86286416, 0.88637718],
            [1.0, -1.72432584, 0.74609023]]


def quad_roots(a):
    disc = cmath.sqrt(a[1] * a[1] - 4.0 * a[0] * a[2])
    return [(-a[1] + disc) / (2.0 * a[0]), (-a[1] - disc) / (2.0 * a[0])]


def roots_of(poly, rounds=400):
    c = [v / poly[0] for v in poly]
    n = len(c) - 1
    z = [(0.4 + 0.9j) ** k for k in range(n)]
    for _ in range(rounds):
        for i in range(n):
            num = 0j
            for v in c:
                num = num * z[i] + v
            den = 1.0 + 0j
            for j in range(n):
                if j != i:
                    den *= z[i] - z[j]
            z[i] -= num / den
    return z


def convolve(f, g):
    out = [0.0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] += a * b
    return out


def separation(target, others):
    """The product of the distances from one pole to all the others."""
    out = 1.0
    for p in others:
        out *= abs(target - p)
    return out


quartic = convolve(SECTIONS[0], SECTIONS[1])
p1 = quad_roots(SECTIONS[0])[0]
all_poles = [r for a in SECTIONS for r in quad_roots(a)]
neighbours = [p for p in all_poles if abs(p - p1) > 1e-12]

in_biquad = separation(p1, [p1.conjugate()])
in_quartic = separation(p1, neighbours)
print(f"p1 = {p1:.6f}")
print(f"distance to its conjugate      {in_biquad:.6f}")
for p in neighbours:
    print(f"  |p1 - ({p:.6f})| = {abs(p1 - p):.6f}")
print(f"product over three neighbours  {in_quartic:.6f}")
print(f"ratio                          {in_biquad / in_quartic:.1f}")

print()
step = 2.0 ** -14
bumped = list(SECTIONS[0])
bumped[2] += step
moved = min(quad_roots(bumped), key=lambda z: abs(z - p1))
print(f"one LSB onto the biquad's a2:  pole moves {abs(moved - p1):.6e}")
print(f"                    predicted            {step / in_biquad:.6e}")
bq = list(quartic)
bq[4] += step
mq = min(roots_of(bq), key=lambda z: abs(z - p1))
print(f"one LSB onto the quartic's a4: pole moves {abs(mq - p1):.6e}")
print(f"                    predicted            {step / in_quartic:.6e}")
```

```text
p1 = 0.931432+0.137155j
distance to its conjugate      0.274310
  |p1 - (0.931432-0.137155j)| = 0.274310
  |p1 - (0.862163+0.052586j)| = 0.109316
  |p1 - (0.862163-0.052586j)| = 0.201990
product over three neighbours  0.006057
ratio                          45.3

one LSB onto the biquad's a2:  pole moves 2.223243e-04
                    predicted            2.225045e-04
one LSB onto the quartic's a4: pole moves 9.885182e-03
                    predicted            1.007683e-02
```

The conjugate distance appears twice: on its own, and as the first of the three
neighbours, because in the quartic that 0.274 is one factor among three. Multiplying it
by 0.109 and 0.202 divides the sensitivity denominator by 45.3.

The second half of the listing measures the prediction. Add one whole LSB of a 14-bit
grid to the biquad's $a_2$ and the pole moves $2.223\times10^{-4}$, against a predicted
$2^{-14}/0.2743 = 2.225\times10^{-4}$. Add the same one LSB to the quartic's constant
term and it moves $9.885\times10^{-3}$, against a predicted $2^{-14}/0.006057 =
1.008\times10^{-2}$. The formula is right to under a percent in the first case and to two
percent in the second, and the ratio between the two measured shifts is 44.5 where the
separation product said 45.3.

## The mistake: paying for the structure in bits

The tempting response to a filter whose poles have moved is to store the coefficients
more precisely. It is the fix that needs no redesign, it is measurable, and it always
helps a little. Here is what it buys.

```python
import cmath

SECTIONS = [[1.0, -1.86286416, 0.88637718],
            [1.0, -1.72432584, 0.74609023]]


def quad_roots(a):
    disc = cmath.sqrt(a[1] * a[1] - 4.0 * a[0] * a[2])
    return [(-a[1] + disc) / (2.0 * a[0]), (-a[1] - disc) / (2.0 * a[0])]


def roots_of(poly, rounds=400):
    c = [v / poly[0] for v in poly]
    n = len(c) - 1
    z = [(0.4 + 0.9j) ** k for k in range(n)]
    for _ in range(rounds):
        for i in range(n):
            num = 0j
            for v in c:
                num = num * z[i] + v
            den = 1.0 + 0j
            for j in range(n):
                if j != i:
                    den *= z[i] - z[j]
            z[i] -= num / den
    return z


def convolve(f, g):
    out = [0.0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] += a * b
    return out


def quantise(poly, frac_bits):
    q = 2.0 ** -frac_bits
    out = [round(v / q) * q for v in poly]
    out[0] = 1.0
    return out


def worst_shift(exact, got):
    """Largest distance from an exact pole to its nearest survivor."""
    return max(min(abs(g - p) for g in got) for p in exact)


quartic = convolve(SECTIONS[0], SECTIONS[1])
exact = [r for a in SECTIONS for r in quad_roots(a)]
print(" f    cascade shift   direct shift   direct radius")
for f in (6, 8, 9, 11, 13, 16, 17):
    casc = [r for a in SECTIONS for r in quad_roots(quantise(a, f))]
    dire = roots_of(quantise(quartic, f))
    print(f"{f:2d}     {worst_shift(exact, casc):.3e}      {worst_shift(exact, dire):.3e}"
          f"       {max(abs(z) for z in dire):.6f}")
```

```text
 f    cascade shift   direct shift   direct radius
 6     5.460e-02      2.656e-01       1.280175
 8     1.231e-02      1.303e-01       1.000000
 9     2.348e-03      6.974e-02       1.000000
11     1.688e-03      9.675e-02       1.000000
13     2.909e-04      2.930e-02       0.955208
16     8.578e-05      3.260e-03       0.940399
17     2.325e-05      3.250e-04       0.941404
```

Read the sixth row against the fourth. The expanded quartic with eleven fractional bits
moves a pole by $9.7\times10^{-2}$ and puts one on the unit circle. The cascade with
**six** — the coarsest storage in the table, a seven-bit word — moves a pole by
$5.5\times10^{-2}$ and stays stable. Five extra bits on every coefficient, and the wrong
structure is behind the crudest version of the right one. To match the cascade at nine
bits, $2.3\times10^{-3}$, the quartic needs seventeen: eight bits per coefficient, spent
to arrive where the other structure already was for free.

The direct radius column carries the second half of the argument, and it is not
monotonic. Six, eight, nine and eleven bits all give a pole at or outside the unit
circle; ten bits does not. Adding a bit to a badly conditioned polynomial moves the
poles somewhere else, and whether that somewhere is inside the circle is not a question
the word length answers.

## Where this stops holding

The sensitivity formula is a first derivative, so it describes a coefficient nudge and
not a coefficient move. At six fractional bits the quartic's grid step is $1.56\times
10^{-2}$, and dividing that by the separation product predicts a pole shift of 2.58 —
against a measured 0.266. The prediction is an order of magnitude out, because by then
the poles have moved far enough that the separations in the denominator are no longer
the ones that were measured. The formula tells you which structure to fear; it does not
tell you where a badly quantised filter's poles end up.

A cascade is not a guarantee either. The protection is the distance from a pole to its
own conjugate, $2r\sin\theta$, and a section can be narrow enough for that to vanish on
its own: at $r = 0.999$ and $\theta = 0.02$ the separation is 0.040, and the lab's fourth
check has exactly that pair reaching the unit circle at eight coefficient bits with no
other section anywhere near it. The cascade removes the coupling between sections and
leaves each section's own conditioning where it found it.

Nor does any of it speak to which zero pair goes with which pole pair, or in what order
the sections run. Those choices change the overflow behaviour and the noise gain a great
deal and change this analysis not at all — module 3 is where they are decided. And an FIR
filter has no poles, so none of the argument reaches one; rounding its taps moves its
zeros and lifts its stopband floor, a specification failure rather than a stability one.

## What you are about to build

The lab *Cascade against expanded direct form* measures the table above from both ends.
`biquad_den(r, theta)` builds `[1, -2*r*cos(theta), r*r]`, `quantise_den` rounds a
denominator onto the grid and puts the structural leading 1 back, `poles` takes the roots,
and `max_pole_shift(ref, got)` pairs each reference pole with its **nearest** survivor —
by distance, never by index, because a root finder promises no ordering and an
index-matched comparison of a pair that swapped is a large number with no meaning.
`shift_pair` then does the whole experiment: quantise each section separately, convolve
and quantise the expanded polynomial, and return both shifts.

Its fourth check is the narrow single section above; its fifth insists the expanded form
is more than five times worse at the same word length. The sandbox *Pole radius, decay,
and how little it takes to move it* is where to build the intuition for why: take $\theta$
towards zero at $r = 0.99$ and watch the two poles converge, which is the separation in
the denominator going to zero in front of you.
''',
                },
            ],
            "quiz": {
                "title": "Where a rounded coefficient sends the poles",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The same eighth-order narrowband filter is stable as four biquads and unstable as one expanded denominator, at identical coefficient word lengths. What accounts for the difference?",
                        "opts": [
                            "In the expanded form a pole's sensitivity is divided by its distance to all seven others, several of them small",
                            "The expanded form stores nine coefficients rather than twelve, so each of them has to carry more of the filter",
                            "A biquad's coefficients are smaller in magnitude, so the same grid rounds them with a smaller relative error",
                            "The cascade evaluates its arithmetic in a wider accumulator, so every intermediate result is held to more precision",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\partial p_i/\partial a_k$ carries $\prod_{j \neq i}(p_i - p_j)$ underneath it. A biquad contributes one factor, $2r\sin\theta$; an eighth-order polynomial contributes seven, and their product is tiny.",
                            r"The count is real and it is the wrong quantity. Twelve stored numbers rounded independently is not worse than nine — what matters is how far a pole travels per unit of coefficient error, which is the separation product, not the tally.",
                            r"Magnitude does not enter the sensitivity at all. A denominator coefficient of a narrow biquad is close to $-2$, larger than most of the quartic's, and the biquad is the robust one.",
                            r"Accumulator width is an arithmetic decision and this failure happens before any arithmetic runs: the poles have already moved when the coefficients are stored, with the filter switched off.",
                        ],
                        "why": r"""
The pole sensitivity to any stored coefficient is
$-p_i^{\,n-k}\big/\prod_{j \neq i}(p_i - p_j)$, and the denominator is a product over
every *other* pole in the same polynomial. Splitting into biquads leaves each pole with
one neighbour instead of seven, so the denominator is a single distance rather than a
product of small ones. For the fourth-order filter in the reading that ratio is 45; at
eighth order it is far larger, and it is the whole reason shipped IIR filters are
cascades.
""",
                    },
                    {
                        "q": "A fourth-order low-pass has denominator coefficients summing to $5.1\\times10^{-4}$. They are rounded onto a grid of step $2^{-8} = 3.9\\times10^{-3}$. What is the risk that creates?",
                        "opts": [
                            "The leading coefficient is no longer exactly 1, so the filter's overall gain changes",
                            "The sum can round to exactly zero, which places a pole at exactly $z = 1$",
                            "The sum can round to exactly one, which places a pole at the origin",
                            "None: the sum of the coefficients is a derived quantity, not one of the stored words",
                        ],
                        "a": 1,
                        "whys": [
                            r"The leading coefficient is structural — it is a 1 in the difference equation, not a number anybody stores — so it survives any rounding. Everything after it is what moves.",
                            r"$A(1)$ is the coefficient sum, and a coefficient sum of zero is a root at $z = 1$.",
                            r"A root at the origin would need the constant term to vanish, which is a different coefficient and a harmless one — a pole at $z = 0$ is a pure delay.",
                            r"The sum is not stored, but each term in it is, and the sum of numbers on a grid of step $\delta$ is itself on that grid. When $\delta$ exceeds the sum, the nearest available value is zero.",
                        ],
                        "why": r"""
$A(1)$ is both the sum of the coefficients and $\prod_i(1 - p_i)$, so for a narrow
low-pass — every pole near $z = 1$ — it is a product of small numbers, here
$5.1\times10^{-4}$. The rounded coefficients sum to a multiple of the grid step, and the
multiple nearest $5.1\times10^{-4}$ on a grid of $3.9\times10^{-3}$ is zero. A
denominator with $A(1) = 0$ has a root at exactly $z = 1$: the low-pass has acquired an
integrator, and this is not a rare corner — it happens at 7, 8, 9 and 11 fractional bits
for the reading's filter.
""",
                    },
                    {
                        "q": "Two poles of a section are moved closer and closer together, with their radii held fixed. What happens to each pole's sensitivity to a stored coefficient?",
                        "opts": [
                            "It is unchanged, because sensitivity is set by the radius, which has not moved",
                            "It falls to zero, because two coincident poles move together and the pair cannot come apart",
                            "It grows without bound, because their separation sits in the denominator of the derivative",
                            "It falls, because the two poles now share the displacement that one coefficient error causes",
                        ],
                        "a": 2,
                        "whys": [
                            r"The radius sets how long the response rings, not how far a rounded coefficient moves the pole. A pair at $r = 0.5$ with a tiny angle is as ill-conditioned as one at $r = 0.99$ with the same angle.",
                            r"They do move together, and that is the failure rather than the protection: a repeated root splits under perturbation like a square root, so an error $\epsilon$ moves each pole by order $\sqrt{\epsilon}$ — worse than linear, not better.",
                            r"$1/(p_1 - p_2)$ has no upper bound as the difference goes to zero.",
                            r"Nothing is shared. Each pole gets the full displacement the derivative predicts, and the derivative is larger for both of them at once.",
                        ],
                        "why": r"""
The derivative is $-1/(p_1 - p_2)$ for a quadratic, so the separation is underneath and
shrinking it makes the sensitivity grow without limit. For a conjugate pair the
separation is $2r\sin\theta$, which is why a narrow section is the dangerous one: at
$r = 0.999$ and $\theta = 0.02$ it is 0.040, and half a step of an eight-bit grid is
enough to push that pair onto the unit circle. Coincident poles are worse still — the
linear formula breaks down and the split goes as the square root of the perturbation.
""",
                    },
                    {
                        "q": "An expanded quartic denominator still has a pole outside the unit circle with eleven fractional bits of coefficient storage. Which response actually fixes the filter?",
                        "opts": [
                            "Raise the sample rate, so the poles are no longer bunched up close to $z = 1$",
                            "Factor the polynomial back into second-order sections and round each one separately",
                            "Double the coefficient word length, storing every one in twenty-two fractional bits instead of eleven",
                            "Round the coefficients towards zero rather than to nearest, so no radius can grow",
                        ],
                        "a": 1,
                        "whys": [
                            r"Raising the sample rate moves every pole *towards* $z = 1$, not away from it: the same analogue filter at twice the rate has poles half as far from the point where the grid is thinnest. It makes this worse in exactly the way it appears to help.",
                            r"It changes the sensitivity denominators from a product of small distances into one distance each, which is the quantity that was wrong.",
                            r"It works, at a price nobody would pay: the reading's quartic needs seventeen fractional bits to match a cascade at nine, so the bits are being spent to buy back a structure decision that costs nothing to make correctly.",
                            r"Rounding towards zero shrinks each *coefficient*, which is not the same as shrinking each pole radius — $a_2$ is a product of the radii and $a_1$ is not, so the two move in different directions and the radius can still grow.",
                        ],
                        "why": r"""
The problem is the conditioning of the polynomial, and only the structure changes that.
Splitting into biquads replaces a sensitivity denominator that is a product of three
small distances with one distance per section, which is the 45-fold difference measured
in the reading. Extra bits do help — seventeen fractional bits gets the quartic to where
a cascade sits at nine — but that is eight bits per coefficient bought to avoid a
factorisation that is free, and the pole radius does not even fall monotonically with
word length along the way.
""",
                    },
                    {
                        "q": "The sensitivity formula predicts a pole shift of 2.58 for a quartic at six coefficient bits, and the shift measured on the rounded filter is 0.266. What has gone wrong?",
                        "opts": [
                            "The formula is a derivative, and at that step size the poles move far enough to change the separations it used",
                            "Rounding at six bits behaves as truncation, so the error is a whole step rather than the half step the bound assumes",
                            "The formula holds only for real, distinct poles, and these are two conjugate pairs",
                            "The measurement matches each exact pole with its nearest survivor, and nearest-neighbour pairing understates a large shift",
                        ],
                        "a": 0,
                        "whys": [
                            r"A shift of 2.58 in a plane where every pole started inside the unit circle is a prediction well outside the region the linearisation was taken in.",
                            r"Rounding is rounding at any word length — the same `round` call, the same half-step bound. Six bits makes the step large; it does not change the rule applied to it.",
                            r"The derivation never needed the poles to be real: $A'(p_i) = \prod_{j\neq i}(p_i - p_j)$ holds over the complex numbers, and the reading's 14-bit check on a conjugate pair matched it to under a percent.",
                            r"Nearest-neighbour pairing can understate a shift, and here it is the honest choice: a root finder returns no ordering, so index pairing would report distances between poles that were never meant to correspond. It is also not a factor of ten.",
                        ],
                        "why": r"""
$\partial p_i/\partial a_k$ is evaluated at the *unperturbed* poles, so it describes the
first infinitesimal step away from them. At fourteen fractional bits, where one LSB is
$6.1\times10^{-5}$, it matches the measurement to under a percent. At six bits the step
is $1.56\times10^{-2}$, the poles rearrange completely — a conjugate pair becoming two
real poles, among other things — and the separations in the denominator are no longer
the ones the formula used. It tells you which structure to fear, not where a badly
quantised filter ends up.
""",
                    },
                    {
                        "q": "One section of a cascade has its poles at radius 0.999 and angle 0.02 radians. Rounded to eight coefficient bits, that pair lands on the unit circle even though every other section is untouched. Why does the cascade not protect it?",
                        "opts": [
                            "Earlier sections have already scaled the signal down, so it reaches this one with fewer significant bits left",
                            "Its coefficients exceed one in magnitude, so an integer bit is spent on range and the grid it lands on is coarser",
                            "Its own two poles are 0.040 apart, and inside a biquad that single distance is the entire sensitivity denominator",
                            "A cascade only decouples sections whose poles are real, and a conjugate pair shares its coefficients with its partner",
                        ],
                        "a": 2,
                        "whys": [
                            r"Signal scaling changes the data path and this failure is in the coefficient path: the poles have moved before a single sample arrives, and they would have moved in a section running on its own.",
                            r"Tempting and half true — $a_1 = -2r\cos\theta$ is about $-2$ here, so the format does need an integer bit. But the comparison in the reading holds the fractional bits fixed at eight for both structures, and the well-separated section survives them.",
                            r"$2r\sin\theta = 2 \times 0.999 \times \sin 0.02 = 0.040$, and half an eight-bit step divided by that is $7.6\times10^{-3}$ — enough to cross from $r = 0.999$.",
                            r"The decoupling has nothing to do with realness. A biquad holds a conjugate pair precisely so that each section owns one pair, and the pair's two members are exactly the neighbours whose separation the formula uses.",
                        ],
                        "why": r"""
Cascading removes a pole's sensitivity to the *other sections'* poles; it does nothing
about its sensitivity to its own conjugate. That separation is $2r\sin\theta$, here
$0.040$, so a half-step of $2^{-9}$ predicts a movement of $7.6\times10^{-3}$ — against
a margin to the unit circle of only $10^{-3}$. The lab's fourth check is this exact pair
at this exact word length. The remedy is more coefficient bits for that section, or a
structure that stores $r$ and $\theta$ rather than $a_1$ and $a_2$, such as the coupled
form.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "Pole radius, decay, and how little it takes to move it",
                "visualiser": "z-plane",
                "minutes": 8,
                "initial": {"r": 0.95, "th": 0.3},
                "brief": r'''
A conjugate pole pair at radius $r$ and angle $\theta$, and the impulse response it
produces. Coefficient quantisation is nothing more than a small, involuntary nudge to
this radius and this angle — so it is worth knowing how much of a nudge matters.
''',
                "notice": [
                    "Take $r$ from 0.95 up past 1.0. Below one the response decays; above one it grows without limit. The whole of stability is that one crossing, and rounding a coefficient is a step of unknown direction towards it.",
                    "Hold $r$ at 0.99 and take $\\theta$ towards zero. The response becomes a long, slow ring — and the two poles converge on each other. That convergence is precisely the condition under which the sensitivity formula derived below blows up.",
                    "Compare $r = 0.5$ with $r = 0.99$. The impulse response length changes by two orders of magnitude for a coefficient change of about 0.5, which tells you how much resolution the radius deserves relative to everything else in the filter.",
                ],
            },
            "derive": {
                "title": "How far a pole moves when you round a coefficient",
                "minutes": 15,
                "vars": ["p", "p_1", "p_2", "a_1", "a_2", "delta", "r", "theta"],
                "brief": r'''
A second-order section has the denominator $1 + a_1 z^{-1} + a_2 z^{-2}$, whose poles
$p_1$ and $p_2$ are the roots of

$$p^{2} + a_1 p + a_2$$

Summing and multiplying the roots gives $a_1 = -\left(p_1 + p_2\right)$ and $a_2$ as
the product. Now perturb $a_2$ alone — the situation when a coefficient is rounded to
its stored grid — and find out how far $p_1$ travels.
''',
                "steps": [
                    {
                        "prompt": "Write $a_2$ in terms of the two poles.",
                        "answer": "p_1 p_2",
                        "hint": "For a monic quadratic the constant term is the product of the roots.",
                        "deconstruct": [
                            "$p^{2} + a_1 p + a_2$ factors as $\\left(p - p_1\\right)\\left(p - p_2\\right)$.",
                            "Multiplying that out, the constant term is $p_1 p_2$.",
                        ],
                    },
                    {
                        "prompt": "Hold $a_1$ fixed and differentiate $p^{2} + a_1 p + a_2 = 0$ implicitly with respect to $a_2$. Write the derivative of $p_1$ with respect to $a_2$, in terms of $p_1$ and $a_1$.",
                        "answer": "-\\frac{1}{2 p_1 + a_1}",
                        "hint": "Differentiating term by term gives $2p_1 \\frac{dp_1}{da_2} + a_1 \\frac{dp_1}{da_2} + 1 = 0$.",
                        "deconstruct": [
                            "The first two terms each carry a factor $\\frac{dp_1}{da_2}$; the last term differentiates to 1.",
                            "Collect the factor and divide: $\\frac{dp_1}{da_2} = \\frac{-1}{2p_1 + a_1}$.",
                        ],
                    },
                    {
                        "prompt": "Substitute $a_1 = -\\left(p_1 + p_2\\right)$ and simplify. Write the derivative in terms of the two poles alone.",
                        "answer": "-\\frac{1}{p_1 - p_2}",
                        "hint": "$2p_1 - p_1 - p_2$ collapses to a single difference.",
                        "deconstruct": [
                            "The denominator becomes $2p_1 - \\left(p_1 + p_2\\right)$.",
                            "That is $p_1 - p_2$: the separation of the two poles.",
                        ],
                    },
                    {
                        "prompt": "Rounding $a_2$ onto a grid of spacing $\\delta$ moves it by at most $\\frac{\\delta}{2}$. Taking $p_1 > p_2$ and both real, write the resulting bound on how far $p_1$ moves.",
                        "answer": "\\frac{\\delta}{2\\left(p_1 - p_2\\right)}",
                        "hint": "Multiply the worst-case coefficient error by the magnitude of the sensitivity you just found.",
                        "deconstruct": [
                            "The coefficient moves by at most $\\delta/2$.",
                            "Multiply that by $\\frac{1}{p_1 - p_2}$, the magnitude of the derivative.",
                        ],
                    },
                ],
                "closing": r'''
The separation $p_1 - p_2$ sits in the denominator, and that single fact decides the
whole structure question. In one biquad the two poles are a conjugate pair, well
separated unless the filter is very narrow. Expand four biquads into one eighth-order
denominator and every pole becomes sensitive to every coefficient, with all the
pairwise separations — several of which are small — in the denominators.

The lab measures exactly that, and the ratio is not subtle.
''',
            },
            "blanks": {
                "title": "Where a quantised coefficient puts the poles",
                "minutes": 9,
                "caption": "coeffs.py — the grid, and why direct form sits badly on it",
                "lang": "python",
                "brief": r"""
Storing a coefficient to finite precision moves the poles. How far it moves them is not a
property of the filter — it is a property of the *structure* you chose to realise it in,
and that is the whole content of this module.
""",
                "listing": """# A coefficient stored in Q(m.f) can only land on a grid of spacing ___ .

# For a direct-form denominator  1 - a1*z**-1 - a2*z**-2 , the reachable
# POLE positions that grid produces are ___ .

# The sensitivity of a pole to a coefficient goes as the reciprocal of
# ___ ,

# so poles that are clustered together are ___ .

# The standard structural fix is ___ .
""",
                "blanks": [
                    {
                        "prompt": "The coefficient grid.",
                        "hole": "?",
                        "opts": ["2 ** -f", "2 ** -m", "2 ** f", "1 / f"],
                        "a": 0,
                        "why": "Uniform, in the *coefficient* domain, at the resolution of the format. Everything interesting follows from the fact that a uniform grid in coefficients is not a uniform grid in poles.",
                        "whys": [
                            "Uniform, in the *coefficient* domain, at the resolution of the format. Everything interesting follows from the fact that a uniform grid in coefficients is not a uniform grid in poles.",
                            "The integer bits set the range, not the step.",
                            "That is a large number; the step is a small one.",
                            "Not a power of two, so it does not describe a binary format at all.",
                        ],
                    },
                    {
                        "prompt": "What does that uniform grid look like in the z-plane?",
                        "hole": "?",
                        "opts": [
                            "not uniform -- the reachable poles thin out near z = +/-1",
                            "a uniform grid, at the same spacing",
                            "points on the unit circle only",
                            "only real values",
                        ],
                        "a": 0,
                        "why": "The map from $(a_1, a_2)$ to pole positions is non-linear, and it stretches badly near $z = \\pm1$. Which is precisely where the poles of a narrowband low-pass sit — so the filters that most need accuracy are the ones the direct form serves worst, and a high-order narrowband design can go unstable purely from rounding.",
                        "whys": [
                            "The map from $(a_1, a_2)$ to pole positions is non-linear, and it stretches badly near $z = \\pm1$. Which is precisely where the poles of a narrowband low-pass sit — so the filters that most need accuracy are the ones the direct form serves worst, and a high-order narrowband design can go unstable purely from rounding.",
                            "If it were uniform there would be no structure problem to solve — and the coupled-form realisation, which achieves very nearly a uniform pole grid, would offer no advantage.",
                            "Poles are not confined to the unit circle; a stable filter's poles are strictly inside it.",
                            "Complex conjugate pairs are exactly what a second-order section is usually for.",
                        ],
                    },
                    {
                        "prompt": "Sensitivity goes as the reciprocal of what?",
                        "hole": "?",
                        "opts": [
                            "the distance from that pole to the other poles",
                            "the filter order",
                            "the sample rate",
                            "the coefficient's own value",
                        ],
                        "a": 0,
                        "why": "The classical result: $\\partial p_i/\\partial a_k$ carries $\\prod_{j \\neq i}(p_i - p_j)$ in its denominator. Poles far apart are individually robust; poles crowded together are not, and the crowding is what a high-order direct-form design creates.",
                        "whys": [
                            "The classical result: $\\partial p_i/\\partial a_k$ carries $\\prod_{j \\neq i}(p_i - p_j)$ in its denominator. Poles far apart are individually robust; poles crowded together are not, and the crowding is what a high-order direct-form design creates.",
                            "Order matters only through its effect on how crowded the poles become — it is the mechanism, not the measure.",
                            "The sample rate does not appear in the sensitivity, though raising it does push poles toward $z = 1$ and make crowding worse.",
                            "The coefficient's magnitude is not what governs it.",
                        ],
                    },
                    {
                        "prompt": "So clustered poles are what?",
                        "hole": "?",
                        "opts": ["the most sensitive", "the least sensitive", "unaffected", "always stable"],
                        "a": 0,
                        "why": "Most sensitive, by a wide margin. A tenth-order elliptic filter realised as one direct-form section can be unusable at 16 bits and perfectly fine at 24 — and the same filter as five second-order sections is fine at 16.",
                        "whys": [
                            "Most sensitive, by a wide margin. A tenth-order elliptic filter realised as one direct-form section can be unusable at 16 bits and perfectly fine at 24 — and the same filter as five second-order sections is fine at 16.",
                            "Backwards: the small differences in the denominator make the derivative large, not small.",
                            "Sensitivity is exactly what changes.",
                            "Rounding can and does push a marginally stable pole outside the unit circle.",
                        ],
                    },
                    {
                        "prompt": "And the fix?",
                        "hole": "?",
                        "opts": [
                            "cascade second-order sections",
                            "raise the sample rate",
                            "use more taps",
                            "use saturating arithmetic",
                        ],
                        "a": 0,
                        "why": "Break the filter into biquads, each holding one conjugate pair. Each section's poles are then far from *its own* other poles, so the sensitivity denominators stay large, and a coefficient error perturbs one pair rather than the whole polynomial. It is why essentially every shipped IIR filter is a cascade of second-order sections.",
                        "whys": [
                            "Break the filter into biquads, each holding one conjugate pair. Each section's poles are then far from *its own* other poles, so the sensitivity denominators stay large, and a coefficient error perturbs one pair rather than the whole polynomial. It is why essentially every shipped IIR filter is a cascade of second-order sections.",
                            "Raising the sample rate crowds the poles toward $z = 1$ and makes the problem worse, not better.",
                            "More taps is an FIR remedy; this is a pole problem, and FIR filters have none.",
                            "Saturation deals with overflow, which is module 3 and a different failure entirely.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Cascade against expanded direct form",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
Measure the pole migration that coefficient rounding causes, in both structures.

`biquad_den(r, theta)` returns the three-element denominator
`[1, -2*r*cos(theta), r*r]` for a conjugate pole pair at radius `r` and angle
`theta`.

`quantise_den(den, frac_bits)` rounds every coefficient onto a grid of spacing
$2^{-f}$ and returns a new array. The leading coefficient is a structural 1, not a
stored number, so force it back to exactly 1.0 afterwards.

`poles(den)` returns the complex roots — `np.roots` does the work.

`max_pole_shift(ref, got)` pairs each reference pole with its nearest survivor in
`got` and returns the largest of those distances. Nearest-neighbour matching, not
index matching: `np.roots` gives no ordering guarantee.

`shift_pair(sections, frac_bits)` takes a list of `(r, theta)` pairs and returns the
tuple `(cascade_shift, direct_shift)`:

- **cascade** — quantise each section's denominator separately, take the roots of
  each, and pool them.
- **direct** — convolve the exact denominators into one long polynomial *first*,
  quantise that, and take its roots.

Same filter, same word length, two structures.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def biquad_den(r, theta):
    """Denominator [1, -2 r cos(theta), r^2] for a conjugate pole pair."""
    # TODO
    return np.array([1.0, 0.0, 0.0])


def quantise_den(den, frac_bits):
    """Round every coefficient onto the 2**-frac_bits grid; keep the leading 1."""
    den = np.asarray(den, dtype=float)
    # TODO
    return den.copy()


def poles(den):
    """The complex roots of the denominator polynomial."""
    # TODO
    return np.zeros(2, dtype=complex)


def max_pole_shift(ref, got):
    """Largest distance from a reference pole to its nearest survivor."""
    # TODO: nearest neighbour, not index-by-index.
    return 0.0


def shift_pair(sections, frac_bits):
    """Return (cascade_shift, direct_shift) for a list of (r, theta) sections."""
    # TODO: quantise each section separately, then quantise the convolved
    # polynomial, and compare both against the exact poles.
    return 0.0, 0.0


if __name__ == "__main__":
    narrow = [(0.99, 0.05), (0.99, 0.08)]
    c, d = shift_pair(narrow, 10)
    print("10-bit coefficients, two narrow sections")
    print("  cascade shift:", c)
    print("  direct  shift:", d)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def biquad_den(r, theta):
    """Denominator [1, -2 r cos(theta), r^2] for a conjugate pole pair."""
    return np.array([1.0, -2.0 * r * np.cos(theta), r * r])


def quantise_den(den, frac_bits):
    """Round every coefficient onto the 2**-frac_bits grid; keep the leading 1."""
    q = 2.0 ** (-frac_bits)
    out = np.round(np.asarray(den, dtype=float) / q) * q
    out[0] = 1.0
    return out


def poles(den):
    """The complex roots of the denominator polynomial."""
    return np.roots(np.asarray(den, dtype=float))


def max_pole_shift(ref, got):
    """Largest distance from a reference pole to its nearest survivor."""
    ref = np.asarray(ref)
    got = np.asarray(got)
    worst = 0.0
    for p in ref:
        worst = max(worst, float(np.min(np.abs(got - p))))
    return worst


def shift_pair(sections, frac_bits):
    """Return (cascade_shift, direct_shift) for a list of (r, theta) sections."""
    dens = [biquad_den(r, th) for r, th in sections]
    exact = np.concatenate([poles(d) for d in dens])

    cascade = np.concatenate([poles(quantise_den(d, frac_bits)) for d in dens])

    full = dens[0]
    for d in dens[1:]:
        full = np.convolve(full, d)
    direct = poles(quantise_den(full, frac_bits))

    return max_pole_shift(exact, cascade), max_pole_shift(exact, direct)


if __name__ == "__main__":
    narrow = [(0.99, 0.05), (0.99, 0.08)]
    c, d = shift_pair(narrow, 10)
    print("10-bit coefficients, two narrow sections")
    print("  cascade shift:", c)
    print("  direct  shift:", d)
'''}],
                "hints": [
                    "`np.cos` takes radians, and `theta` is already in radians — no conversion anywhere.",
                    "In `quantise_den`, round the whole array in one expression, then set element 0 back to 1.0.",
                    "For `max_pole_shift`, loop over the reference poles and take `np.min(np.abs(got - p))` for each; `abs` of a complex difference is the distance in the plane.",
                    "`np.convolve` multiplies two polynomials given as coefficient arrays — that is exactly what expanding a cascade into a direct form is.",
                ],
                "tests": [
                    {"name": "the denominator has the poles it was asked for", "code": r'''
import numpy as np
_d = biquad_den(0.9, 0.4)
assert _d.shape == (3,), f"a second-order denominator has three coefficients, got {_d.shape}"
assert abs(_d[0] - 1.0) < 1e-15, "the leading coefficient is 1 by construction"
_p = poles(_d)
assert abs(float(np.max(np.abs(_p))) - 0.9) < 1e-9, \
    f"both poles should sit at radius 0.9, got {np.abs(_p).tolist()}"
assert abs(float(np.max(np.abs(np.angle(_p)))) - 0.4) < 1e-9, \
    f"the pole angle should be 0.4 rad, got {np.angle(_p).tolist()}"
'''},
                    {"name": "quantising rounds the coefficients but not the leading one", "code": r'''
import numpy as np
_q = quantise_den(biquad_den(0.99, 0.05), 8)
assert abs(_q[0] - 1.0) < 1e-15, "the leading 1 is structural and must stay exactly 1.0"
assert abs(_q[1] + 1.9765625) < 1e-12, \
    f"-1.9775255 rounds to -1.9765625 on a 2**-8 grid, got {_q[1]}"
assert abs(_q[2] - 0.98046875) < 1e-12, \
    f"0.9801 rounds to 0.98046875 on a 2**-8 grid, got {_q[2]}"
'''},
                    {"name": "pole shift is measured by nearest neighbour", "code": r'''
_s = max_pole_shift([0.5 + 0j, -0.5 + 0j], [-0.52 + 0j, 0.51 + 0j])
assert abs(_s - 0.02) < 1e-9, \
    f"expected 0.02 (the worse of 0.01 and 0.02); got {_s} — did you match by index instead of by distance?"
'''},
                    {"name": "eight-bit coefficients put a narrow pole on the unit circle", "code": r'''
import numpy as np
_exact = biquad_den(0.999, 0.02)
assert float(np.max(np.abs(poles(_exact)))) < 0.9991, "the exact design is stable at r = 0.999"
_r = float(np.max(np.abs(poles(quantise_den(_exact, 8)))))
assert _r >= 0.9999, \
    f"rounded to 2**-8 this pole pair reaches the unit circle; expected radius >= 0.9999, got {_r}"
'''},
                    {"name": "the cascade holds its poles and the direct form does not", "code": r'''
_c, _d = shift_pair([(0.99, 0.05), (0.99, 0.08)], 10)
assert _c > 0.0, "with 10-bit coefficients even the cascade moves its poles a little"
assert _c < 0.01, f"the cascade shift should stay near 3.5e-3, got {_c}"
assert _d > 5 * _c, \
    f"expanding the same filter into one quartic denominator should be far worse: cascade {_c:.3e}, direct {_d:.3e}"
'''},
                    {"name": "more coefficient bits help the cascade steadily", "code": r'''
_c10, _d10 = shift_pair([(0.98, 0.1), (0.97, 0.14)], 10)
_c14, _d14 = shift_pair([(0.98, 0.1), (0.97, 0.14)], 14)
assert _c14 < _c10, \
    f"four more bits must shrink the cascade shift: {_c14:.3e} at 14 bits vs {_c10:.3e} at 10"
assert _c14 < _d14 / 5, \
    f"at 14 bits the cascade should still be far ahead: cascade {_c14:.3e}, direct {_d14:.3e}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Overflow, saturation and scaling",
            "summary": "An accumulator that wraps turns the largest positive number into the largest negative one. Deciding that this cannot happen is a design step, not an afterthought.",
            "concepts": [
                "Two's complement addition wraps modulo $2^{m+1}$: the sample after full scale is full-scale negative, and the error is the whole range.",
                "Saturating arithmetic clamps instead, so the error is bounded by the amount of the overload rather than by the range.",
                "Wraparound has one genuine virtue: a sum of wrapping intermediates is correct provided the *final* result is in range, which is why some accumulators are allowed to wrap.",
                "The $L_1$ bound $\\sum |h[k]|$ is the smallest input scaling that makes overflow impossible for any bounded input.",
                "Scaling to the $L_1$ bound is pessimistic for real signals and costs dynamic range directly — guard bits in the accumulator buy the same safety without it.",
            ],
            "read": [
                {
                    "title": "The safe arithmetic gets the wrong answer",
                    "minutes": 17,
                    "body": r'''
Three taps of 0.6, a square wave of amplitude 0.9, and a word whose range runs from $-1$
to $1 - 2^{-15}$. Every number going in is comfortably inside that range. Here is what
comes out around sample 22, computed three ways: with no limit at all, with a two's
complement accumulator that rolls over, and with one that clamps.

```python
import math

TAPS = [0.6, 0.6, 0.6]


def square(n):
    """The lab's input: a 0.9 square wave, well inside a range of [-1, 1)."""
    s = math.sin(2.0 * math.pi * 0.02 * n)
    return 0.9 * (1.0 if s > 0 else -1.0 if s < 0 else 0.0)


def wrap(v, int_bits=0):
    """Fold into [-2**m, 2**m) the way two's complement addition does."""
    half = 2.0 ** int_bits
    return (v + half) % (2.0 * half) - half


def saturate(v, int_bits=0, frac_bits=15):
    """Clamp to the representable range instead."""
    return min(max(v, -(2.0 ** int_bits)), 2.0 ** int_bits - 2.0 ** -frac_bits)


def run(mode):
    out = []
    for n in range(60):
        acc = sum(TAPS[k] * square(n - k) for k in range(3) if n - k >= 0)
        if mode == "wrap":
            acc = wrap(acc)
        elif mode == "saturate":
            acc = saturate(acc)
        out.append(acc)
    return out


exact = run("none")
wrapped = run("wrap")
clamped = run("saturate")
print(" n    input     exact     wrapped   saturated")
for n in range(22, 30):
    print(f"{n:3d}   {square(n):+.2f}   {exact[n]:+.5f}   {wrapped[n]:+.5f}   {clamped[n]:+.5f}")
print()
print("worst-case gain, sum of |taps|:", sum(abs(t) for t in TAPS))
print("reference peak               :", max(abs(v) for v in exact))
print("largest wrap error           :", max(abs(a - b) for a, b in zip(wrapped, exact)))
print("largest saturation error     :", max(abs(a - b) for a, b in zip(clamped, exact)))
```

```text
 n    input     exact     wrapped   saturated
 22   +0.90   +1.62000   -0.38000   +0.99997
 23   +0.90   +1.62000   -0.38000   +0.99997
 24   +0.90   +1.62000   -0.38000   +0.99997
 25   -0.90   +0.54000   +0.54000   +0.54000
 26   -0.90   -0.54000   -0.54000   -0.54000
 27   -0.90   -1.62000   +0.38000   -1.00000
 28   -0.90   -1.62000   +0.38000   -1.00000
 29   -0.90   -1.62000   +0.38000   -1.00000

worst-case gain, sum of |taps|: 1.7999999999999998
reference peak               : 1.62
largest wrap error           : 2.0
largest saturation error     : 0.6200305175781251
```

Three inputs of $+0.9$ in a row and the accumulator wants 1.62. Rolling over, it hands
back $-0.38$: not a distorted version of $+1.62$ but a value of the opposite sign, and
the same again at 27 with the signs reversed. Clamping, it hands back $+0.99997$, which
is at least on the right side of zero and out by the amount of the overload.

## Why one error is 2.0 and the other is 0.62

Two's complement addition is arithmetic modulo $2^{m+1}$, the width of the whole range,
with the result taken in the half-open window $\left[-2^{m}, 2^{m}\right)$. So a value
$v$ that leaves the window comes back as $v - 2^{m+1}$ if it left the top, and
$v + 2^{m+1}$ if it left the bottom. The error is not related to how far $v$ went; it is
the span itself. With $m = 0$ the span is 2.0, and 2.0 is what the measurement reports —
to the last digit, for every overflowing sample, whether the overload was one LSB or one
hundred.

Clamping replaces $v$ with the nearest representable value, so the error is
$v - \left(2^{m} - q\right)$: the overshoot and nothing else. Here $1.62 - 0.99997 =
0.62003$, which is again what the measurement reports. A small overload gives a small
error, and the error grows continuously with the overload rather than jumping to the
full span at the first code past the rail.

That is the whole argument for saturation at an output, and it is worth stating in the
terms the ear uses rather than the terms the norm uses. Saturation is soft clipping: it
adds harmonics that arrive with the signal and stop when it does. Rolling over inserts a
discontinuity of the entire range into a smooth waveform, and a discontinuity has energy
at frequencies the signal never contained — which then fold about half the sample rate
exactly as the alias in the sandbox *Where the energy goes when something folds* does.
One sounds like a loud passage; the other sounds like a fault.

## The mistake: clamping can only help

The reasonable next step is to apply the clamp everywhere, on the grounds that a value
which cannot leave the range cannot do damage. This is where fixed-point arithmetic stops
behaving the way ordinary arithmetic does.

An FIR accumulator adds its products one at a time. Some of those running totals can
leave the range while the final sum comes back inside it. Take taps $[0.9, -0.8, 0.9]$
and a window of $[+0.9, -0.9, -0.9]$: the products are $0.81$, $0.72$ and $-0.81$, the
running totals are $0.81$, $1.53$ and $0.72$, and the answer, $0.72$, is representable.

```python
import random

TAPS = [0.9, -0.8, 0.9]


def wrap(v):
    return (v + 1.0) % 2.0 - 1.0


def saturate(v):
    return min(max(v, -1.0), 1.0 - 2.0 ** -15)


def accumulate(window, limiter):
    """Add the products one at a time, applying the limiter to each running total."""
    acc = 0.0
    for tap, x in zip(TAPS, window):
        acc = limiter(acc + tap * x)
    return acc


rng = random.Random(11)
seq = [0.9 if rng.random() < 0.5 else -0.9 for _ in range(4000)]
worst_wrap = 0.0
worst_sat = 0.0
overflowed = 0
for n in range(2, len(seq)):
    window = [seq[n], seq[n - 1], seq[n - 2]]
    exact = sum(t * x for t, x in zip(TAPS, window))
    if abs(exact) >= 1.0:
        continue                      # the result itself does not fit; nothing to ask
    partials = [sum(TAPS[k] * window[k] for k in range(j + 1)) for j in range(3)]
    if max(abs(p) for p in partials) < 1.0:
        continue                      # nothing overflowed on the way, either
    overflowed += 1
    worst_wrap = max(worst_wrap, abs(accumulate(window, wrap) - exact))
    worst_sat = max(worst_sat, abs(accumulate(window, saturate) - exact))

print("windows whose total fits but whose running sum did not:", overflowed)
print("largest error, wrapping accumulator  :", worst_wrap)
print("largest error, saturating accumulator:", worst_sat)

window = [0.9, -0.9, -0.9]
print()
print("one of them, step by step")
print("  products      ", [round(t * x, 4) for t, x in zip(TAPS, window)])
print("  running total ", [round(sum(TAPS[k] * window[k] for k in range(j + 1)), 4)
                           for j in range(3)])
print("  exact         ", round(sum(t * x for t, x in zip(TAPS, window)), 6))
print("  wrapping      ", round(accumulate(window, wrap), 6))
print("  saturating    ", round(accumulate(window, saturate), 6))
```

```text
windows whose total fits but whose running sum did not: 991
largest error, wrapping accumulator  : 1.1102230246251565e-16
largest error, saturating accumulator: 0.5300305175781251

one of them, step by step
  products       [0.81, 0.72, -0.81]
  running total  [0.81, 1.53, 0.72]
  exact          0.72
  wrapping       0.72
  saturating     0.189969
```

On 991 of the 3998 windows — a quarter of them — the running sum leaves the range and the
answer does not. On every one of those, the accumulator with **no overflow protection at
all**, the one that rolls over and does nothing about it, returns the exact answer to
within $1.1\times10^{-16}$ of floating-point dust. The accumulator that was defended
returns 0.190 where the truth is 0.720, and it is wrong by 0.530 — a quarter of the whole
range. The defence is the defect.

The reason is that addition modulo $2^{m+1}$ is closed and associative: rolling over is
not an approximation of the sum, it is the exact sum expressed in a different
representative of the same residue class, so a value that leaves the range and comes back
carries its excess with it and cancels it. Clamping is not modular. It discards the
excess at the moment of clamping, and nothing later can recover a number that was thrown
away.

This is why a DSP part offers both and why the choice is made per stage rather than per
program: the intermediate sums of an FIR are allowed to roam, and the value written out
at the end is clamped.

## How much headroom to buy, and what it costs

The derive unit *Scaling a three-tap filter so it cannot overflow* finds the largest safe
input scaling for positive taps: the reciprocal of the tap sum. With signs allowed, the
same argument gives $\frac{1}{\sum_k \left|h_k\right|}$, because the worst input is the
one whose sign at each lag matches the sign of the tap it meets. That sum is the $L_1$
gain, and it is not a bound anyone chose to be careful with — it is attained.

```python
import cmath
import math
import random


def lowpass(taps=21, fc=0.15):
    """A windowed-sinc low-pass, built here so the numbers can be checked."""
    mid = (taps - 1) / 2.0
    h = []
    for n in range(taps):
        k = n - mid
        ideal = 2.0 * fc if k == 0.0 else math.sin(2.0 * math.pi * fc * k) / (math.pi * k)
        h.append(ideal * (0.54 - 0.46 * math.cos(2.0 * math.pi * n / (taps - 1))))
    return h


def peak_gain(h, points=4000):
    """The largest magnitude of the frequency response, on a fine grid."""
    best = 0.0
    for i in range(points + 1):
        w = math.pi * i / points
        s = sum(c * cmath.exp(-1j * w * k) for k, c in enumerate(h))
        best = max(best, abs(s))
    return best


def peak_out(h, x):
    return max(abs(sum(h[k] * x[n - k] for k in range(len(h)) if n - k >= 0))
               for n in range(len(x)))


h = lowpass()
l1 = sum(abs(c) for c in h)
l2 = math.sqrt(sum(c * c for c in h))
print(f"L1 gain, sum of |h|      {l1:.4f}   costs {20 * math.log10(l1):5.2f} dB to scale out")
print(f"peak |H(w)|              {peak_gain(h):.4f}   costs {20 * math.log10(peak_gain(h)):5.2f} dB")
print(f"L2 gain, sqrt(sum h^2)   {l2:.4f}")
print()
adversary = [(1.0 if c >= 0 else -1.0) for c in reversed(h)] * 4
rng = random.Random(5)
noise = [1.0 if rng.random() < 0.5 else -1.0 for _ in range(4000)]
tone = [math.sin(2.0 * math.pi * 0.05 * n) for n in range(4000)]
print(f"peak out, the sign pattern of h   {peak_out(h, adversary):.4f}")
print(f"peak out, random plus/minus one   {peak_out(h, noise):.4f}")
print(f"peak out, a full-scale sine       {peak_out(h, tone):.4f}")
```

```text
L1 gain, sum of |h|      1.3162   costs  2.39 dB to scale out
peak |H(w)|              1.0015   costs  0.01 dB
L2 gain, sqrt(sum h^2)   0.5110

peak out, the sign pattern of h   1.3162
peak out, random plus/minus one   1.2670
peak out, a full-scale sine       1.0074
```

The adversarial input reaches 1.3162 exactly, which is what "attained" means. What is
worth noticing is the second line: a random full-scale binary sequence, chosen by a coin
and not by an adversary, reaches 1.2670 — 96% of the bound. For a broadband signal at
full scale the $L_1$ bound is close to the truth, and calling it pessimistic is a way of
being wrong about a quarter of a bit.

The sine is the other case. A single tone in the passband peaks at 1.0074, because a
sinusoid is scaled by $\left|H(\omega)\right|$ and by nothing else, and the largest that
gets is 1.0015. Scaling to the $L_1$ bound to protect a narrowband signal gives away
2.38 dB for an input that cannot occur.

There is a third option, and it is why DSP parts have 40-bit accumulators on 16-bit data
paths. Instead of scaling the signal down by $\frac{1}{L_1}$, widen the accumulator by
$\left\lceil \log_2 L_1 \right\rceil$ guard bits. Here $\log_2 1.3162 = 0.396$, so one
guard bit removes every overflow at a cost of one bit of register width and zero decibels
of signal. Eight guard bits cover an $L_1$ gain up to 256, which is more than a
several-hundred-tap filter needs.

## Where this stops holding

Saturation makes the filter nonlinear. Superposition is gone the moment anything clamps,
so a measured response to one input says nothing about another, and the frequency response
stops being a description of the system. In a recursive filter it does something worse:
a clamped value is fed back, and an overflow can sustain itself as a full-scale
oscillation that persists after the input has gone. That is an overflow limit cycle, and
it is a different animal from the granular limit cycles of module 4 — those are a few
LSBs, this one is the whole range.

The modular argument has a sharp edge too. Intermediates may roll over only while nothing
downstream *reads* one as a value. That holds for the running sum of an FIR, which is
discarded once the output is taken. It fails completely in the recursive structures of
module 4, where the intermediate is the state, is stored, and is read back on the next
sample: there, a roll-over is a genuine and permanent error, which is why the capstone
limits every stored word and not only the output.

Finally, all of this assumes the filter is fixed. An adaptive filter's taps change, so
$\sum|h|$ changes with them, and a scaling chosen at design time is a scaling chosen for
coefficients the filter no longer has.

## What you are about to build

The lab *Wraparound, saturation and the $L_1$ bound* is the three pieces above with the
numbers turned into checks. `wrap(v, int_bits)` is the fold — the modulus taken on
$v + 2^{m}$ and shifted back, which is the one-line form of the two's complement
behaviour derived here. `saturate` is the clamp with the same asymmetric top,
$2^{m} - q$, that module 1 built. `l1_gain(b)` is the tap sum, and its check insists that
$[0.5, -0.5]$ gives 1.0 rather than 0.0, because the signs of the taps do not cancel when
the input is free to flip with them. `fir(x, b, mode, ...)` runs the filter with a
full-precision accumulator and applies the limiter to the output sample alone.

Its fifth check is the first listing of this reading: a wrap error of exactly 2.0 against
a saturation error of 0.62. Its sixth scales the input by $1/1.8$ and insists the peak
comes out at 0.9 and that nothing clips at all — the derive unit's result, measured.
''',
                },
            ],
            "sandbox": {
                "title": "Where the energy goes when something folds",
                "visualiser": "spectrum",
                "minutes": 7,
                "initial": {"fsig": 170, "fs": 200},
                "brief": r'''
This is the same sandbox as module 1, opened on an aliased case, and it is here for a
different reason. An overflow that wraps introduces a discontinuity into an otherwise
smooth waveform, and a discontinuity has energy at frequencies the signal never had.
Those harmonics then fold about the sample rate exactly as the alias here does.

The practical consequence is that overflow distortion does not stay near the signal.
It arrives spread across the band, at a level set by the full-scale range rather than
by the size of the overload.
''',
                "notice": [
                    "The signal is above half the sample rate, so the reconstruction is a lower frequency that the samples fit perfectly. Nothing downstream can undo it: the information is gone at the moment of sampling.",
                    "Move the signal frequency slowly upwards and watch the alias move downwards. Products of a wrapping overflow land at many frequencies at once, and each one folds by this same rule.",
                    "Raise the sample rate until the alias disappears. Oversampling buys you room against aliasing — but no amount of it protects an accumulator that wraps, because that distortion is created after the sampling, inside the arithmetic.",
                ],
            },
            "derive": {
                "title": "Scaling a three-tap filter so it cannot overflow",
                "minutes": 13,
                "vars": ["b_0", "b_1", "b_2", "X_m", "s", "q", "n", "P_e"],
                "brief": r'''
A three-tap filter with strictly positive coefficients,

$$y[n] = b_0 x[n] + b_1 x[n-1] + b_2 x[n-2]$$

is fed an input bounded by $X_m$, the full scale of the format. The output must stay
inside the same format. Work out what that costs.
''',
                "steps": [
                    {
                        "prompt": "Write the largest value $y[n]$ can reach, in terms of $X_m$ and the taps.",
                        "answer": "X_m \\left( b_0 + b_1 + b_2 \\right)",
                        "hint": "The worst case is the input that is at full scale, with the right sign, in every tap at once.",
                        "deconstruct": [
                            "Each term is at most $b_k X_m$ because the taps are positive.",
                            "The three terms reach their maxima together when the input holds at $X_m$.",
                        ],
                    },
                    {
                        "prompt": "Scale the input by a factor $s$ before the filter so that the output can never exceed $X_m$. Write the largest such $s$.",
                        "answer": "\\frac{1}{b_0 + b_1 + b_2}",
                        "hint": "Set your previous answer, with $X_m$ replaced by $s X_m$, equal to $X_m$ and solve.",
                        "deconstruct": [
                            "The bound becomes $s X_m \\left( b_0 + b_1 + b_2 \\right)$.",
                            "Requiring that to equal $X_m$ cancels $X_m$ and leaves the reciprocal of the tap sum.",
                        ],
                    },
                    {
                        "prompt": "That scaling shrinks the signal but not the quantisation floor beneath it. Write the factor by which the signal-to-noise ratio falls, in terms of the taps.",
                        "answer": "\\frac{1}{\\left( b_0 + b_1 + b_2 \\right)^{2}}",
                        "hint": "Power goes as the square of amplitude, and the noise power is unchanged by scaling the input.",
                        "deconstruct": [
                            "The signal amplitude is multiplied by $s$, so the signal power is multiplied by $s^{2}$.",
                            "$s^{2}$ is the reciprocal of the square of the tap sum.",
                        ],
                    },
                    {
                        "prompt": "Each of the three products is rounded to the data step $q$ before it is accumulated, and the three errors are independent. Write the total mean-square error at the output.",
                        "answer": "\\frac{q^{2}}{4}",
                        "hint": "Independent errors add in power, and you found the power of one of them in module 1.",
                        "deconstruct": [
                            "Each rounding contributes $\\frac{q^{2}}{12}$.",
                            "Three of them, added as powers, give $\\frac{3q^{2}}{12}$.",
                        ],
                    },
                ],
                "closing": r'''
Two costs, pulling the same way. Scaling pushes the signal down towards the floor, and
the structure raises the floor by the number of roundings in the arithmetic. Both are
avoidable with a wider accumulator: keep the products at full width, add them all, and
round once at the end. That single change removes the factor of three above and, in a
recursive filter, removes the rounding that would otherwise be fed back through the
poles — which is the subject of the next module.
''',
            },
            "quiz": {
                "title": "What happens at the top of the range",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A two's complement accumulator at full scale is incremented once more. What does it become?",
                        "opts": [
                            "The most negative value",
                            "Full scale again",
                            "Zero",
                            "An exception is raised",
                        ],
                        "a": 0,
                        "why": r"""
It wraps: the largest positive code rolls straight to the largest negative one. In audio
that is a full-scale sign inversion in a single sample — a loud click, not a gentle
distortion — and it is why an overflow that happens once every few seconds is far more
objectionable than continuous mild clipping. Nothing is raised; the hardware simply
carries on.
""",
                    },
                    {
                        "q": "What does saturating arithmetic bound the error by?",
                        "opts": [
                            "The amount by which the result exceeded the range",
                            "Half a quantisation step",
                            "The full range",
                            "Nothing — saturation is exact",
                        ],
                        "a": 0,
                        "why": r"""
Clamping gives an error equal to the overshoot, so a small overflow causes a small error
— which is the behaviour intuition expects and wrapping violently fails to provide. It
turns a catastrophic failure into a graceful one, and it is why DSP instruction sets have
saturating add as a primitive rather than leaving it to software.
""",
                    },
                    {
                        "q": "Wrapping has one genuine advantage over saturation. What is it?",
                        "opts": [
                            "A sum of wrapping intermediates is correct as long as the final total is in range",
                            "It is faster",
                            "It produces less quantisation noise",
                            "It cannot cause limit cycles",
                        ],
                        "a": 0,
                        "why": r"""
Modular arithmetic is associative, so intermediate overflows cancel: an accumulator that
wraps three times and comes back is exactly right, while a saturating one has clamped and
lost the information permanently. That is why FIR accumulators are often left to wrap
while the *output* stage saturates — the intermediate sum is allowed to roam, and only
the final value has to be representable.
""",
                    },
                    {
                        "q": "You scale a signal down before an accumulator. What have you traded?",
                        "opts": [
                            "Resolution, for headroom",
                            "Bandwidth, for headroom",
                            "Speed, for accuracy",
                            "Nothing — scaling is free",
                        ],
                        "a": 0,
                        "why": r"""
Shifting right buys room at the top and throws away bits at the bottom, so the signal
sits further above the noise floor of the range and closer to the noise floor of the
quantiser. Every fixed-point design is this one negotiation, repeated at each stage, and
it is why scaling analysis is done with a norm bound rather than by trying a few inputs.
""",
                    },
                    {
                        "q": "For an audio output stage, which failure is worse?",
                        "opts": [
                            "Wrapping, because a sign inversion is a click",
                            "Saturating, because it distorts",
                            "They sound identical",
                            "Neither is audible below full scale",
                        ],
                        "a": 0,
                        "why": r"""
Saturation is soft clipping — harmonic distortion, unpleasant but continuous with what
came before. Wrapping is a discontinuity of the full range, which is broadband and
sounds like a fault rather than like overload. Where the *arithmetic* wants wrapping,
as in the intermediate sums above, and the *output* wants saturation, is a distinction
worth designing around explicitly.
""",
                    },
                ],
            },
            "lab": {
                "title": "Wraparound, saturation and the L1 bound",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Implement both overflow behaviours and measure the difference.

`wrap(v, int_bits)` folds `v` into $[-2^{m}, 2^{m})$ the way two's complement
addition does. The one-line form is

```text
((v + 2**int_bits) mod 2**(int_bits+1)) - 2**int_bits
```

and `np.mod` already gives the non-negative remainder that this needs.

`saturate(v, int_bits, frac_bits)` clamps instead, to
$[-2^{m},\ 2^{m} - q]$, as in module 1.

`l1_gain(b)` returns the sum of the absolute tap values — the worst-case gain of the
filter, and the reciprocal of the safe input scaling.

`fir(x, b, mode, int_bits, frac_bits)` runs the filter over `x`, using a
full-precision accumulator and applying the overflow behaviour named by `mode` to the
output sample only. `mode` is one of `"none"`, `"wrap"` or `"saturate"`; `"none"` is
the floating-point reference the other two are judged against.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def wrap(v, int_bits):
    """Fold v into [-2**int_bits, 2**int_bits) the way two's complement does."""
    v = np.asarray(v, dtype=float)
    # TODO: add half the span, take the modulus, subtract it back.
    return v


def saturate(v, int_bits, frac_bits):
    """Clamp v to the representable range of Q(int_bits.frac_bits)."""
    v = np.asarray(v, dtype=float)
    # TODO
    return v


def l1_gain(b):
    """Worst-case gain of the filter: the sum of the absolute taps."""
    # TODO
    return 0.0


def fir(x, b, mode="none", int_bits=0, frac_bits=15):
    """Run the filter, applying `mode` to each output sample."""
    x = np.asarray(x, dtype=float)
    b = np.asarray(b, dtype=float)
    out = np.zeros_like(x)
    # TODO: accumulate at full precision, then limit the result.
    return out


if __name__ == "__main__":
    n = np.arange(400)
    x = 0.9 * np.sign(np.sin(2 * np.pi * 0.02 * n))
    taps = [0.6, 0.6, 0.6]
    ref = fir(x, taps)
    print("worst-case gain:", l1_gain(taps))
    print("reference peak :", float(np.max(np.abs(ref))))
    print("wrap error     :", float(np.max(np.abs(fir(x, taps, "wrap") - ref))))
    print("saturate error :", float(np.max(np.abs(fir(x, taps, "saturate") - ref))))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def wrap(v, int_bits):
    """Fold v into [-2**int_bits, 2**int_bits) the way two's complement does."""
    half = 2.0 ** int_bits
    return np.mod(np.asarray(v, dtype=float) + half, 2.0 * half) - half


def saturate(v, int_bits, frac_bits):
    """Clamp v to the representable range of Q(int_bits.frac_bits)."""
    q = 2.0 ** (-frac_bits)
    return np.clip(np.asarray(v, dtype=float), -(2.0 ** int_bits), 2.0 ** int_bits - q)


def l1_gain(b):
    """Worst-case gain of the filter: the sum of the absolute taps."""
    return float(np.sum(np.abs(np.asarray(b, dtype=float))))


def fir(x, b, mode="none", int_bits=0, frac_bits=15):
    """Run the filter, applying `mode` to each output sample."""
    x = np.asarray(x, dtype=float)
    b = np.asarray(b, dtype=float)
    out = np.zeros_like(x)
    for n in range(len(x)):
        acc = 0.0
        for k in range(len(b)):
            if n - k >= 0:
                acc += b[k] * x[n - k]
        if mode == "wrap":
            acc = float(wrap(acc, int_bits))
        elif mode == "saturate":
            acc = float(saturate(acc, int_bits, frac_bits))
        out[n] = acc
    return out


if __name__ == "__main__":
    n = np.arange(400)
    x = 0.9 * np.sign(np.sin(2 * np.pi * 0.02 * n))
    taps = [0.6, 0.6, 0.6]
    ref = fir(x, taps)
    print("worst-case gain:", l1_gain(taps))
    print("reference peak :", float(np.max(np.abs(ref))))
    print("wrap error     :", float(np.max(np.abs(fir(x, taps, "wrap") - ref))))
    print("saturate error :", float(np.max(np.abs(fir(x, taps, "saturate") - ref))))
'''}],
                "hints": [
                    "`np.mod` returns a non-negative remainder for a positive modulus, which is what makes the one-line wrap work; Python's `%` on floats agrees with it.",
                    "`wrap` needs no `frac_bits` — folding the range is independent of the resolution inside it.",
                    "In `fir`, guard the history index with `if n - k >= 0` so the filter starts from rest rather than reading off the end of the array.",
                    "Apply the limiter to `acc` after the whole sum, not to each product; that is what a full-precision accumulator means.",
                ],
                "tests": [
                    {"name": "wrapping folds the range the way two's complement does", "code": r'''
assert abs(float(wrap(1.8, 0)) + 0.2) < 1e-12, \
    f"in a range of [-1, 1), 1.8 wraps to -0.2, got {float(wrap(1.8, 0))} — a small overload becomes a large negative number"
assert abs(float(wrap(-1.2, 0)) - 0.8) < 1e-12, \
    f"-1.2 wraps to +0.8, got {float(wrap(-1.2, 0))}"
assert abs(float(wrap(0.5, 0)) - 0.5) < 1e-12, \
    "a value already inside the range must be left alone"
'''},
                    {"name": "saturation stops one LSB below full scale", "code": r'''
assert abs(float(saturate(1.8, 0, 15)) - 0.999969482421875) < 1e-15, \
    f"Q0.15 clamps at 1 - 2**-15 = 0.999969482421875, got {float(saturate(1.8, 0, 15))}"
assert abs(float(saturate(-3.0, 0, 15)) + 1.0) < 1e-15, \
    f"the negative rail is -1 exactly, got {float(saturate(-3.0, 0, 15))}"
'''},
                    {"name": "the L1 gain is the worst-case gain", "code": r'''
assert abs(l1_gain([0.6, 0.6, 0.6]) - 1.8) < 1e-9, \
    f"three taps of 0.6 give a worst-case gain of 1.8, got {l1_gain([0.6, 0.6, 0.6])}"
assert abs(l1_gain([0.5, -0.5]) - 1.0) < 1e-12, \
    "the signs do not cancel — a worst-case input flips with the tap"
'''},
                    {"name": "the reference filter overflows this input", "code": r'''
import numpy as np
_n = np.arange(400)
_x = 0.9 * np.sign(np.sin(2 * np.pi * 0.02 * _n))
_ref = fir(_x, [0.6, 0.6, 0.6])
assert abs(float(np.max(_ref)) - 1.62) < 1e-9, \
    f"0.9 through a gain of 1.8 peaks at 1.62, got {float(np.max(_ref))} — check the accumulator and the history guard"
'''},
                    {"name": "wraparound is far worse than saturation on the same overload", "code": r'''
import numpy as np
_n = np.arange(400)
_x = 0.9 * np.sign(np.sin(2 * np.pi * 0.02 * _n))
_ref = fir(_x, [0.6, 0.6, 0.6])
_we = float(np.max(np.abs(fir(_x, [0.6, 0.6, 0.6], "wrap") - _ref)))
_se = float(np.max(np.abs(fir(_x, [0.6, 0.6, 0.6], "saturate") - _ref)))
assert abs(_we - 2.0) < 1e-9, \
    f"a wrap error spans the whole range: expected 2.0, got {_we}"
assert abs(_se - 0.6200305175781251) < 1e-6, \
    f"a saturation error is only the size of the overload: expected about 0.62, got {_se}"
assert _we > 3 * _se, "wraparound must come out worse, or the two modes have been swapped"
'''},
                    {"name": "scaling by the L1 gain removes the overflow entirely", "code": r'''
import numpy as np
_n = np.arange(400)
_x = 0.9 * np.sign(np.sin(2 * np.pi * 0.02 * _n))
_taps = [0.6, 0.6, 0.6]
_g = l1_gain(_taps)
assert _g > 0.0, f"l1_gain must return the tap sum, not {_g}"
_xs = _x / _g
_ref = fir(_xs, _taps)
_peak = float(np.max(np.abs(_ref)))
assert abs(_peak - 0.9) < 1e-9, \
    f"scaled by 1/1.8 the peak is exactly the input amplitude, 0.9; got {_peak}"
assert _peak <= 1.0 + 1e-12, \
    f"scaled by 1/1.8 the output cannot leave the range, got a peak of {_peak}"
_err = float(np.max(np.abs(fir(_xs, _taps, "saturate") - _ref)))
assert _err < 1e-9, \
    f"nothing should clip once the input is scaled, but the saturating run differs by {_err}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Limit cycles and the deadband",
            "summary": "Remove the input from a stable recursive filter and it should go silent. Quantised, it often will not.",
            "concepts": [
                "In a recursive structure the rounding error is fed back through the poles, so it is not a floor added at the output — it is a signal the filter reacts to.",
                "A granular limit cycle is a small, self-sustaining oscillation: the shrink per step falls below half an LSB and rounding restores it exactly.",
                "The deadband $\\frac{q}{2\\left(1 - |a|\\right)}$ bounds the amplitude, and it grows without limit as the pole approaches the unit circle.",
                "A negative pole gives an alternating cycle at half the sample rate; a positive pole gives a stuck DC offset. Both are audible in the wrong product.",
                "Magnitude truncation always moves towards zero, so it cannot sustain a granular cycle — at the price of a signal-dependent bias.",
            ],
            "read": [
                {
                    "title": "Fifty codes that will not go away",
                    "minutes": 17,
                    "body": r'''
An exponential smoother on an embedded part, the most ordinary recursive filter there is:
$y[n] = a\,y[n-1] + (1-a)\,x[n]$ with $a = 0.99$, its state held in a 16-bit word. The
sensor reads 0.5 for two thousand samples and then the sensor is unplugged and the input
is exactly zero. The filter is stable, the input is gone, and the output should follow it
down.

```python
Q = 2.0 ** -15
A = 0.99


def smooth(x, quantised):
    """y[n] = a*y[n-1] + (1-a)*x[n], with the stored state rounded when asked."""
    y = 0.0
    out = []
    for v in x:
        y = A * y + (1.0 - A) * v
        if quantised:
            y = round(y / Q) * Q
        out.append(y)
    return out


signal = [0.5] * 2000 + [0.0] * 4000
fixed = smooth(signal, True)
ideal = smooth(signal, False)
print("after the input is removed, in LSBs of a 16-bit word")
print(" sample   fixed point   double precision")
for n in (2000, 2200, 2600, 3000, 4000, 5999):
    print(f"  {n:5d}   {fixed[n] / Q:11.2f}   {ideal[n] / Q:16.6f}")
print()
print("last 8 fixed-point samples, in LSBs:", [round(v / Q, 3) for v in fixed[-8:]])
print("they are all identical            :", len(set(fixed[-8:])) == 1)
print("predicted deadband, q/(2*(1-a))   :", 1.0 / (2.0 * (1.0 - A)), "LSB")
```

```text
after the input is removed, in LSBs of a 16-bit word
 sample   fixed point   double precision
   2000      16171.00       16220.159970
   2200       2168.00        2173.171759
   2600         50.00          39.009635
   3000         50.00           0.700245
   4000         50.00           0.000030
   5999         50.00           0.000000

last 8 fixed-point samples, in LSBs: [50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
they are all identical            : True
predicted deadband, q/(2*(1-a))   : 49.99999999999996 LSB
```

The two runs track each other down through four decades and then part company. In double
precision the output is at $3\times10^{-5}$ LSB by sample 4000 and gone by 5999. In the
16-bit word it stops at 50 LSB, exactly, and stays there for as long as the part is
powered. Not decaying slowly — stopped. The last eight samples are the same number.

## The value has found a place to stand

Once the input has gone, the recursion is $y \leftarrow Q(a\,y)$ and nothing else. In one
step the value would shrink by $y(1-a)$, and the quantiser then moves it by up to $q/2$.
When the shrink is the smaller of the two, rounding returns the number it started from,
and the sequence has reached a fixed point of the *quantised* recursion that is not a
fixed point of the ideal one. Setting $y(1-a) = q/2$ gives the largest such $y$, which is
the derive unit *The deadband of a first-order section* and its answer
$\frac{q}{2\left(1-|a|\right)}$. At $a = 0.99$ that is $50q$, and $50q$ is where the
measurement stopped.

The lab's own case is small enough to read by hand. Eight fractional bits, $a = 0.8$, and
a start of 20 LSB, under three rounding rules that people reach for interchangeably.

```python
import math

Q = 2.0 ** -8


def to_nearest(v):
    return round(v / Q) * Q


def towards_minus_infinity(v):
    return math.floor(v / Q) * Q


def towards_zero(v):
    return math.trunc(v / Q) * Q


def zero_input(a, y0, rule, steps=30):
    """y <- rule(a*y), recording each value before it is stepped."""
    y = y0
    out = []
    for _ in range(steps):
        out.append(y)
        y = rule(a * y)
    return out


RULES = [("round to nearest    ", to_nearest),
         ("floor, towards -inf ", towards_minus_infinity),
         ("truncate towards 0  ", towards_zero)]
for start in (20, -20):
    print(f"starting at {start:+3d} LSB, a = 0.8, one LSB = 1/256")
    for name, rule in RULES:
        seq = [round(v / Q) for v in zero_input(0.8, start * Q, rule)]
        print(f"  {name} {seq[:12]} ... settles at {seq[-1]:+d}")
    print()
print("deadband q/(2*(1-0.8)) =", 1.0 / (2.0 * 0.2), "LSB")
```

```text
starting at +20 LSB, a = 0.8, one LSB = 1/256
  round to nearest     [20, 16, 13, 10, 8, 6, 5, 4, 3, 2, 2, 2] ... settles at +2
  floor, towards -inf  [20, 16, 12, 9, 7, 5, 4, 3, 2, 1, 0, 0] ... settles at +0
  truncate towards 0   [20, 16, 12, 9, 7, 5, 4, 3, 2, 1, 0, 0] ... settles at +0

starting at -20 LSB, a = 0.8, one LSB = 1/256
  round to nearest     [-20, -16, -13, -10, -8, -6, -5, -4, -3, -2, -2, -2] ... settles at -2
  floor, towards -inf  [-20, -16, -13, -11, -9, -8, -7, -6, -5, -4, -4, -4] ... settles at -4
  truncate towards 0   [-20, -16, -12, -9, -7, -5, -4, -3, -2, -1, 0, 0] ... settles at +0

deadband q/(2*(1-0.8)) = 2.5 LSB
```

Follow the rounded row to its end. At 3 LSB the product is 2.4, which rounds to 2. At 2
LSB the product is 1.6, which rounds back to 2. The shrink is 0.4 LSB, the quantiser's
reach is 0.5, and 0.4 is the smaller of the two — so the value cannot get past itself.
Two is inside the predicted 2.5, as it has to be.

The three rules do not agree, and the disagreement is the point. Truncating towards zero
takes the magnitude down by at least the fraction it discards and never puts anything
back, so it reaches exact zero from either sign, on step 10. Flooring is not the same
operation: it moves towards $-\infty$, so it kills the cycle above zero and manufactures
a worse one below, locking at $-4$ LSB where round-to-nearest had settled at $-2$. A
right shift on a two's complement register is a floor, and reaching for one as "the cheap
truncation" swaps a symmetric two-LSB cycle for a permanent negative offset twice its
size.

## The mistake: a quantiser can only be wrong by half a step

Half an LSB is what rounding promises, and for an FIR filter the promise is kept: each
error appears in one output sample and is gone. Carrying that intuition into a recursive
structure is the error this module exists to correct, and it is a comfortable one to
carry, because the arithmetic really is the same arithmetic.

```python
import math


def settle(a, frac_bits, rule, y0=0.5, steps=60000):
    """Run y <- rule(a*y) from y0 until it stops moving, and report where."""
    q = 2.0 ** -frac_bits
    y = round(y0 / q) * q
    for _ in range(steps):
        nxt = rule(a * y / q) * q
        if nxt == y:
            return y
        y = nxt
    return y


def nearest(t):
    return round(t)


def to_zero(t):
    return math.trunc(t)


q15 = 2.0 ** -15
print("15 fractional bits, rounding to nearest")
print("   a      settles at    q/(2(1-a))     as dBFS")
for a in (0.5, 0.8, 0.9, 0.99, 0.999):
    v = settle(a, 15, nearest)
    band = 1.0 / (2.0 * (1.0 - a))
    db = 20.0 * math.log10(abs(v)) if v else float("-inf")
    print(f" {a:6.3f}   {abs(v) / q15:8.1f} LSB   {band:8.1f} LSB   {db:8.2f}")

print()
print("the same filter at a = 0.99, two ways")
rounded16 = settle(0.99, 15, nearest)
cut9 = settle(0.99, 8, to_zero)
print(f"  16-bit word, round to nearest      {abs(rounded16):.8f} "
      f"= {20 * math.log10(abs(rounded16)):.2f} dBFS")
print(f"   9-bit word, truncate towards zero {abs(cut9):.8f} = silence")
print(f"  a 16-bit converter's own floor is  {10 * math.log10(q15 * q15 / 12):.2f} dB, "
      "spread over the whole band")
```

```text
15 fractional bits, rounding to nearest
   a      settles at    q/(2(1-a))     as dBFS
  0.500        0.0 LSB        1.0 LSB       -inf
  0.800        2.0 LSB        2.5 LSB     -84.29
  0.900        4.0 LSB        5.0 LSB     -78.27
  0.990       50.0 LSB       50.0 LSB     -56.33
  0.999      500.0 LSB      500.0 LSB     -36.33

the same filter at a = 0.99, two ways
  16-bit word, round to nearest      0.00152588 = -56.33 dBFS
   9-bit word, truncate towards zero 0.00000000 = silence
  a 16-bit converter's own floor is  -101.10 dB, spread over the whole band
```

Fifty LSBs is a hundred times the half-LSB the quantiser promised, and 500 is a thousand
times. Worse, the comparison the word length was bought on is the last line: the whole
quantisation floor of a 16-bit word is $q^{2}/12$, which is $-101.10$ dB, spread across
the band. The stuck offset at $a = 0.99$ carries $-56.33$ dB — 44.8 dB more power than
the entire floor the sixteen bits were chosen to deliver, and it is at one place in the
spectrum rather than spread over it. Sixteen bits bought a floor and the structure put a
tone on top of it.

Then the comparison that should settle the argument. The same section in a **nine-bit**
word, with the cruder and cheaper rounding rule — truncation towards zero — produces
exactly zero. Not a smaller cycle: none. Seven fewer bits of state, an operation that
costs less than round-to-nearest, and a filter that goes quiet where the careful 16-bit
version does not. More resolution is not the axis this failure lives on.

## Where this stops holding

The deadband is a bound and it should be read as one. At $a = 0.8$ it allows 2.5 LSB and
the filter settles at 2; at $a = 0.5$ it allows 1.0 and the filter reaches exact zero.
The formula says where a cycle cannot be, not where it will be, and at high $|a|$ the two
coincide because the grid is fine relative to the band — 50.0 against 50.0, 500.0
against 500.0 — while at low $|a|$ there is a whole LSB of slack.

The $a = 0.5$ row is decided by the tie-break, which is worth knowing before it decides
something less convenient. The state arrives at 1 LSB, the product is exactly 0.5 LSB,
and Python's `round` — like a well-designed converter — breaks that tie to even and
returns 0. A round-half-away-from-zero rule would return 1 and lock there forever. At the
amplitudes where limit cycles live, the tie-break is not a detail.

Everything above is first order. A second-order section has zero-input cycles the
argument does not reach: their amplitude bound involves $a_2$ as well and is larger, and
the cycle can be a genuine oscillation with a period unrelated to $2$ samples, rather
than a stuck value or an alternation. The capstone's fourth-order cascade is where that
shows up, and its check allows a tail of up to 64 LSBs against a first-order intuition of
a handful.

Magnitude truncation buys the silence at a price. Its error is no longer zero-mean: it
always moves towards zero, so it shrinks whatever is present by an amount that depends on
what is present. That is signal-dependent distortion rather than noise, and on a
low-level signal it is audible in its own way. Nor does it touch the overflow limit
cycles of module 3, which are sustained by a clamp rather than by rounding and run at
full scale rather than at a few LSBs.

Last, none of this is visible with an input. A filter whose state is re-excited every
sample never sits in its deadband, so the fault does not appear on the bench with a
signal generator connected. It appears in the gaps: the pause between words, the moment
after a burst, the sensor that was unplugged.

## What you are about to build

The lab *Find the limit cycle, then remove it* builds the four pieces above. `q_round`
and `q_trunc` differ in one call, and the second must truncate towards zero rather than
floor — the $-4$ LSB row is what happens when it does not. `zero_input(a, y0, frac_bits,
steps, mode)` runs $y \leftarrow Q(ay)$ and records each value **before** stepping, so the
first entry is the $y_0$ you handed it. `deadband(a, frac_bits)` is
$\frac{q}{2\left(1-|a|\right)}$ with the absolute value, because a pole at $-0.8$ holds a
cycle of the same amplitude as one at $+0.8$ and only differs in flipping sign every
sample.

Its checks are the numbers above: the settle at 2 LSB from a start of 20, the same settle
from a start of 100 because the deadband belongs to the pole and not to the excitation,
the alternating sign for a negative pole, and truncation reaching zero on step 10. The
blanks unit *The filter that will not go quiet* asks for the same four facts in the order
the argument makes them, and the sandbox *A decay that has to stop somewhere* is where to
watch the per-step shrink get small: hold the angle at zero and take the radius from 0.5
to 0.98, and what is shrinking is the quantity that has to beat half an LSB.
''',
                },
            ],
            "quiz": {
                "title": "A filter with nothing to filter",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A stable first-order section runs on into silence in a 16-bit word and its output stops at 50 LSB instead of reaching zero. What holds it there?",
                        "opts": [
                            "The input was not exactly zero, and a residual offset is being amplified by the feedback path",
                            "The state word has run out of bits, and 50 LSB is the smallest value that format can represent",
                            "Its coefficient rounded to a value slightly above one, so the section is no longer a stable one",
                            "The shrink per step has fallen below half an LSB, so rounding hands back the code it was given",
                        ],
                        "a": 3,
                        "whys": [
                            r"A reasonable first suspicion, and the measurement rules it out: the same code path in double precision, with the same input, reaches $3\times10^{-5}$ LSB. The input is identical; only the rounding differs.",
                            r"One LSB is the smallest non-zero value the format holds, and 50 of them are 50 available codes above it. Nothing about the format prevents the state from passing through 49, 48 and so on down to zero.",
                            r"Then the output would grow rather than sit still. A coefficient above one gives an exponential ramp to the rail; this sequence is bit-for-bit constant.",
                            r"$y(1-a) = 50q \times 0.01 = 0.5q$, and rounding covers exactly that.",
                        ],
                        "why": r"""
With the input gone the recursion is $y \leftarrow Q(a\,y)$. The ideal step would shrink
the value by $y\left(1-a\right)$, and the quantiser can move it by up to $q/2$ in the
other direction. At $y = 50q$ and $a = 0.99$ the shrink is exactly $0.5q$, so rounding
restores it in full and the state is a fixed point of the quantised recursion that is not
one of the ideal recursion. Setting those two quantities equal is where
$\frac{q}{2\left(1-|a|\right)}$ comes from, and it gives 50 LSB for this pole.
""",
                    },
                    {
                        "q": "Two DC blockers run in the same 16-bit arithmetic, one with its pole at $a = 0.9$ and one at $a = 0.999$. How do their zero-input tails compare?",
                        "opts": [
                            "The tail at $a = 0.999$ sits about a hundred times higher, because the deadband goes as $1/(1-|a|)$",
                            "The two are the same size, because the deadband is set by the quantisation step and by nothing else",
                            "The tail at $a = 0.999$ is smaller, because a pole nearer the unit circle decays more gently",
                            "The tail at $a = 0.999$ alternates at half the sample rate while the other one holds a DC value",
                        ],
                        "a": 0,
                        "whys": [
                            r"$1/(2 \times 0.001)$ against $1/(2 \times 0.1)$: 500 LSB against 5, and the measured settling points are 500 and 4.",
                            r"The step is the numerator and the pole is in the denominator. If the step alone decided it, every filter in a given word length would have the same tail, and a DC blocker at $a = 0.9999$ would be as quiet as one at $a = 0.5$.",
                            r"Gentle decay is the mechanism, and it points the other way: a smaller shrink per step is beaten by half an LSB sooner, so the value stops sooner and higher up.",
                            r"Both poles are positive, so both hold a steady value. Alternation at half the sample rate is what a *negative* pole produces, and its amplitude bound is the same $q/(2(1-|a|))$.",
                        ],
                        "why": r"""
The deadband is $\frac{q}{2\left(1-|a|\right)}$, so what matters is the distance from the
pole to the unit circle. At $a = 0.9$ that distance is 0.1 and the bound is 5 LSB; at
$a = 0.999$ it is 0.001 and the bound is 500 LSB, a hundredfold. In a 16-bit word 500 LSB
is $-36$ dBFS of output from a filter with no input — which is why a narrowband section
is the one to check, and why raising the sample rate, which pushes poles towards
$z = 1$, makes this worse rather than better.
""",
                    },
                    {
                        "q": "An FIR filter of the same length, rounding every stored value to the same grid, does not produce a zero-input tail at all. What is the difference?",
                        "opts": [
                            "Its taps are all below one in magnitude, so a rounding error cannot be scaled up anywhere in the filter",
                            "A rounding error enters one output sample and is discarded; no path returns it to the filter's state",
                            "It is written with a full-precision accumulator, so the arithmetic rounds once instead of once per tap",
                            "Its error is bounded by half an LSB per tap, and the taps of a low-pass sum to less than one",
                        ],
                        "a": 1,
                        "whys": [
                            r"Tap magnitude is not what does it. Give an FIR filter taps of 8 and it still has no zero-input tail, because after the input stops the delay line empties and the output is a sum of zeros.",
                            r"Once the delay line has flushed, an FIR filter's output is a sum over stored *inputs*, all of which are zero.",
                            r"A wide accumulator does reduce the noise, and it is orthogonal to this: a recursive filter with a full-precision accumulator still rounds the value it stores as state, and that stored value is what circulates.",
                            r"The taps of a unit-gain low-pass sum to one, not less, and the bound is about error size rather than about persistence. A one-LSB error that never returns is harmless however large the taps are.",
                        ],
                        "why": r"""
The state of an FIR filter is the last $N$ *inputs*, not its own past outputs. Stop the
input and the delay line flushes; after $N$ samples the filter is summing zeros and its
output is zero, whatever rounding did on the way. In a recursive filter the rounded value
is the state, so the error made at step $n$ is fed back through the pole and becomes part
of the signal the filter reacts to. That is the whole structural difference, and it is
why $q^2/12$ describes an FIR filter's error as a floor added at the output and describes
a recursive filter's error as an input it cannot tell from the real one.
""",
                    },
                    {
                        "q": "The same first-order section is run two ways: a 16-bit state rounded to nearest, and a 9-bit state truncated towards zero. The 9-bit version reaches exact silence and the 16-bit one sticks at 50 LSB. Why?",
                        "opts": [
                            "Its coarser grid makes the value decay faster, so it passes through the deadband before it can lock",
                            "Its deadband is smaller, because a wider quantisation step puts the bound lower for the same pole",
                            "Truncation towards zero can only shrink the magnitude, and no rounding step is ever able to restore it",
                            "The two end up equally quiet in the end; the extra bits change how large the tail is rather than whether there is one",
                        ],
                        "a": 2,
                        "whys": [
                            r"A coarse grid does not speed up a geometric decay — the multiply is the same multiply. It changes what happens at the bottom of it, and if the rule were round-to-nearest the 9-bit version would lock too, at 6 LSB of its own coarser step.",
                            r"Backwards: $q$ is in the numerator, so a wider step gives a *larger* deadband in absolute terms. At 9 bits and $a = 0.99$ it is $50 \times 2^{-8}$, which is 64 times the 16-bit value.",
                            r"Every step either shrinks the magnitude by at least the fraction discarded, or leaves it, and the value cannot rise.",
                            r"They are not equally quiet: one is a hard zero, held forever, and the other is a constant $1.5\times10^{-3}$. That is a difference in kind and not in size.",
                        ],
                        "why": r"""
Rounding to nearest can move a value away from zero, and that is exactly what sustains
the cycle: the shrink of $0.5q$ is undone by a rounding step of $0.5q$. Truncation
towards zero has no such move available — its error always points inwards — so the
magnitude is non-increasing at every step and strictly decreasing until it reaches zero.
The word length is not the axis this failure lives on: fewer bits and a cheaper rule beat
more bits and a careful one. What magnitude truncation costs is elsewhere, in a
signal-dependent bias that is distortion rather than noise.
""",
                    },
                    {
                        "q": "Round-to-nearest is replaced by a right shift on the two's complement state word, which floors towards $-\\infty$. What happens to the zero-input behaviour?",
                        "opts": [
                            "Nothing changes: flooring and rounding differ only on values that are already exact multiples of the step",
                            "Cycles above zero die out, and the state instead locks at a small negative value it can never leave",
                            "Both signs die out, because any form of truncation discards part of the magnitude at every step",
                            "Cycles grow in both directions, because flooring can displace a value by a whole step rather than half of one",
                        ],
                        "a": 1,
                        "whys": [
                            r"They differ on every value that is not already on the grid, which after a multiply by 0.8 is almost all of them — the two traces from $+20$ LSB part company at the third sample.",
                            r"Flooring always moves towards $-\infty$, which shrinks a positive value and grows a negative one.",
                            r"That describes truncation towards *zero*, which is a different operation. `math.floor(-1.6)` is $-2.0$ while `math.trunc(-1.6)` is $-1.0$, and only the second moves inwards from both sides.",
                            r"The displacement is under a whole step, which is true and is not the mechanism. The asymmetry is: from $+20$ LSB the floored run reaches exact zero, so it certainly has not grown in that direction.",
                        ],
                        "why": r"""
A right shift is a floor, and a floor is not magnitude truncation. From $+20$ LSB at
$a = 0.8$ it reaches zero on step 10, which looks like a fix. From $-20$ LSB it locks at
$-4$ LSB — twice the amplitude round-to-nearest had settled at, and a permanent DC offset
rather than a symmetric cycle. This is the cheapest mistake in the module to make, since
a shift is what a compiler emits for a divide by a power of two, and the check that
catches it is the one asserting `q_trunc(-1.6 LSB)` is $-1$ LSB rather than $-2$.
""",
                    },
                    {
                        "q": "The deadband formula allows 2.5 LSB at $a = 0.8$ and the filter settles at exactly 2; it allows 1.0 LSB at $a = 0.5$ and the filter reaches exact zero. What should be read into that?",
                        "opts": [
                            "It gives the amplitude of the first step after the input stops, rather than of the settled value",
                            "It is an upper bound on where a sustained cycle can sit, not a prediction of where one will sit",
                            "It applies to negative poles, where the cycle alternates, and overstates the case for positive ones",
                            "It breaks down below $a = 0.8$, where a linear model of the rounding error stops describing it",
                        ],
                        "a": 1,
                        "whys": [
                            r"The first step after the input stops is wherever the decay had reached, which depends entirely on how loud the signal was — the bound depends on the pole and the step size and on nothing about the excitation.",
                            r"It answers the question of where the shrink can be beaten, so anything outside it must keep decaying.",
                            r"The sign of the pole changes only whether the cycle holds or alternates; the bound carries $|a|$ and is the same for $+0.8$ and $-0.8$, as the lab's second check asserts.",
                            r"Nothing breaks down. At high $|a|$ the settling point lands on the bound exactly — 50.0 against 50.0, 500.0 against 500.0 — and the slack at low $|a|$ is the grid being coarse relative to a small bound, not a failure of the argument.",
                        ],
                        "why": r"""
The derivation asks where the per-step shrink $y\left(1-|a|\right)$ can be undone by a
rounding step of at most $q/2$, so it marks the largest $y$ at which a cycle is
*possible*. Above it every value must keep falling. Inside it the state has to land on an
actual grid point, and which one depends on the trajectory and on the tie-break: at
$a = 0.8$ the reachable point below 2.5 LSB is 2, and at $a = 0.5$ the bound is 1.0 LSB
and the only grid point strictly inside it is zero. At $a = 0.99$ and above the grid is
fine compared with the bound and the two agree to the digit.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "A decay that has to stop somewhere",
                "visualiser": "z-plane",
                "minutes": 7,
                "initial": {"r": 0.92, "th": 0},
                "brief": r'''
Open with the angle at zero: a single real pole, and an impulse response that is a
pure geometric decay. In exact arithmetic that decay reaches zero only in the limit.
On a grid of step $q$ it cannot — at some point the shrink per step is smaller than
half an LSB, rounding puts the value back where it was, and the response stops
falling.

Where it stops is the deadband, and the derivation below gives it exactly.
''',
                "notice": [
                    "With the angle at zero, raise the radius from 0.5 to 0.98. The per-step shrink gets smaller and smaller; the deadband is set by the point at which that shrink drops below half an LSB, so it grows with the radius exactly as the formula says.",
                    "Take the angle to near $\\pi$ with the radius around 0.9. The response alternates in sign every sample — that is the shape a negative-coefficient limit cycle takes, and it lands at half the sample rate where nothing downstream expects signal.",
                    "Set the radius to 0.5. The response is essentially over in eight samples, and the deadband would be one LSB. Fast poles are not the problem; the long, narrow-band ones are.",
                ],
            },
            "derive": {
                "title": "The deadband of a first-order section",
                "minutes": 12,
                "vars": ["a", "q", "Y", "y", "n"],
                "brief": r'''
Take the simplest recursive filter there is, with its input removed and its product
rounded to the nearest multiple of $q$ before it is stored:

$$y[n] = \text{round}\left( a\, y[n-1] \right)$$

with $0 < a < 1$. Find the largest magnitude $Y$ at which the value can sit forever
instead of decaying to zero.
''',
                "steps": [
                    {
                        "prompt": "Write the largest amount by which rounding to the nearest multiple of $q$ can change a value.",
                        "answer": "\\frac{q}{2}",
                        "hint": "The grid points are $q$ apart, and nearest-neighbour rounding never has to travel more than halfway.",
                        "deconstruct": [
                            "Any value lies between two adjacent grid points, $q$ apart.",
                            "The nearer of the two is at most half that distance away.",
                        ],
                    },
                    {
                        "prompt": "Before rounding, a stored value of magnitude $Y$ becomes $aY$. Write the amount by which it shrank.",
                        "answer": "Y\\left(1 - a\\right)",
                        "hint": "Subtract the new magnitude from the old one and factor.",
                        "deconstruct": [
                            "The shrink is $Y - aY$.",
                            "Factoring $Y$ out gives $Y\\left(1-a\\right)$.",
                        ],
                    },
                    {
                        "prompt": "The value stays put whenever rounding can undo that shrink entirely. Set the shrink equal to the largest rounding step and solve for $Y$: write the edge of the deadband.",
                        "given": "The shrink is $Y\\left(1-a\\right)$ and rounding can move a value by at most $\\frac{q}{2}$.",
                        "answer": "\\frac{q}{2\\left(1 - a\\right)}",
                        "hint": "Divide both sides by $1 - a$.",
                        "deconstruct": [
                            "$Y\\left(1-a\\right) = \\frac{q}{2}$.",
                            "Divide through by $\\left(1-a\\right)$.",
                        ],
                    },
                    {
                        "prompt": "Evaluate that edge for $a = 0.8$, as a multiple of $q$.",
                        "answer": "\\frac{5}{2}",
                        "hint": "Put $a = 0.8$ into $\\frac{1}{2\\left(1-a\\right)}$.",
                        "deconstruct": [
                            "$1 - a = 0.2$, so the denominator is $0.4$.",
                            "$\\frac{1}{0.4}$ is $\\frac{5}{2}$.",
                        ],
                    },
                ],
                "closing": r'''
Two and a half LSBs sounds harmless, and at $a = 0.8$ it is. Put the pole at
$a = 0.999$ — an ordinary narrow-band section — and the same formula gives 500 LSBs, a
sustained tone at roughly $-36$ dBFS in a 16-bit word, produced by a filter with no
input.

Nothing in the derivation depended on the value being large or small, which is the
point: the deadband is a property of the pole and the word length, not of the signal
that happened to excite it.
''',
            },
            "blanks": {
                "title": "The filter that will not go quiet",
                "minutes": 8,
                "caption": "deadband.py — an oscillation with no input at all",
                "lang": "python",
                "brief": r"""
Take the input away from a stable recursive filter and it should decay to silence.
Quantised, it frequently does not — it settles into a small, permanent oscillation that
no amount of waiting removes. Fill in why.
""",
                "listing": """# First-order section:   y[n] = Q( a * y[n-1] )     with |a| < 1

# In a RECURSIVE structure the rounding error is ___ ,
# so unlike an FIR filter it does not simply add a noise floor.

# A limit cycle survives when the shrink per step is smaller than
# ___ ,
# because the rounding then puts the value straight back where it was.

# The amplitude is bounded by the deadband
#     q / (2 * (1 - ___ ))
# which grows without bound as the pole approaches ___ .
""",
                "blanks": [
                    {
                        "prompt": "What makes a recursive filter different from an FIR one here?",
                        "hole": "?",
                        "opts": [
                            "the rounding error is fed back through the poles",
                            "the rounding error is filtered out",
                            "there is no rounding error",
                            "the error is independent of the coefficients",
                        ],
                        "a": 0,
                        "why": "The error made at step $n$ becomes part of the state and is amplified by the same feedback that shapes the signal. In an FIR filter each rounding error appears once and leaves; here it circulates, and near an under-damped pole it circulates with almost no attenuation.",
                        "whys": [
                            "The error made at step $n$ becomes part of the state and is amplified by the same feedback that shapes the signal. In an FIR filter each rounding error appears once and leaves; here it circulates, and near an under-damped pole it circulates with almost no attenuation.",
                            "The opposite: the feedback path is what sustains it. If it were filtered out there would be no limit cycle.",
                            "Rounding is unavoidable at every multiply — that is what fixed point means.",
                            "It depends on them strongly, which is exactly what the deadband formula quantifies.",
                        ],
                    },
                    {
                        "prompt": "When does the value fail to shrink?",
                        "hole": "?",
                        "opts": [
                            "the quantisation step",
                            "the coefficient a",
                            "the sample rate",
                            "the filter order",
                        ],
                        "a": 0,
                        "why": "If $|ay| $ differs from $|y|$ by less than half a step, rounding returns the same number and the state is stuck — a fixed point of the *quantised* recursion that is not a fixed point of the ideal one. The filter has, in effect, found a place to stand.",
                        "whys": [
                            "If $|ay| $ differs from $|y|$ by less than half a step, rounding returns the same number and the state is stuck — a fixed point of the *quantised* recursion that is not a fixed point of the ideal one. The filter has, in effect, found a place to stand.",
                            "$a$ governs how fast it shrinks; the step is the threshold that shrink has to beat.",
                            "The sample rate does not enter the recursion.",
                            "This is a first-order section; the order is not the mechanism.",
                        ],
                    },
                    {
                        "prompt": "Complete the deadband bound.",
                        "hole": "?",
                        "opts": ["abs(a)", "a", "1 - a", "q"],
                        "a": 0,
                        "why": "$q/(2(1-|a|))$. The magnitude, because the bound is the same for a pole at $+0.99$ and one at $-0.99$ — the second oscillates every sample instead of drifting, but it is just as stuck.",
                        "whys": [
                            "$q/(2(1-|a|))$. The magnitude, because the bound is the same for a pole at $+0.99$ and one at $-0.99$ — the second oscillates every sample instead of drifting, but it is just as stuck.",
                            "Without the magnitude a negative pole gives $1 - a > 1$ and a bound *smaller* than the quantisation step, which cannot be right.",
                            "This inverts the dependence: the deadband would shrink as the pole approached the unit circle.",
                            "The step is already the numerator; using it twice has the wrong dimensions.",
                        ],
                    },
                    {
                        "prompt": "Where does the deadband blow up?",
                        "hole": "?",
                        "opts": ["the unit circle", "the origin", "z = 0", "the imaginary axis"],
                        "a": 0,
                        "why": "As $|a| \\to 1$ the denominator goes to zero and the bound diverges — which is the practical warning: a very narrowband filter, which is exactly a filter with poles near the unit circle, can hold a limit cycle far larger than one quantisation step. A DC-blocker at $a = 0.9999$ in 16-bit arithmetic has a deadband of thousands of codes.",
                        "whys": [
                            "As $|a| \\to 1$ the denominator goes to zero and the bound diverges — which is the practical warning: a very narrowband filter, which is exactly a filter with poles near the unit circle, can hold a limit cycle far larger than one quantisation step. A DC-blocker at $a = 0.9999$ in 16-bit arithmetic has a deadband of thousands of codes.",
                            "Near the origin the pole is heavily damped and the deadband is at its smallest — about half a step.",
                            "$z = 0$ is a point in the same well-behaved region, not where the bound diverges.",
                            "The relevant boundary in the z-plane is the unit circle; the imaginary axis is the s-plane's.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Find the limit cycle, then remove it",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
`q_round(v, frac_bits)` rounds a scalar to the nearest multiple of the step.

`q_trunc(v, frac_bits)` truncates a scalar *towards zero* instead — magnitude
truncation, not floor. `np.trunc` does this; `np.floor` does not, and the difference
is the whole point of the last check.

`zero_input(a, y0, frac_bits, steps, mode)` runs $y \leftarrow Q(a y)$ from `y0` for
`steps` iterations and returns the list of values, recording each value *before*
stepping so that the first entry is `y0`. `mode` is `"round"` or `"truncate"`.

`deadband(a, frac_bits)` returns $\frac{q}{2\left(1 - |a|\right)}$ — the bound you
derived, with the absolute value so it covers negative poles too.

The checks use `frac_bits = 8`, so one LSB is $1/256$ and the sequences are short
enough to read by hand if you want to.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def q_round(v, frac_bits):
    """Round a scalar to the nearest multiple of the step."""
    # TODO
    return float(v)


def q_trunc(v, frac_bits):
    """Truncate a scalar towards zero onto the step grid."""
    # TODO: np.trunc, not np.floor — the difference matters for negatives.
    return float(v)


def zero_input(a, y0, frac_bits, steps, mode="round"):
    """Run y <- Q(a*y) from y0, recording each value before it is stepped."""
    y = float(y0)
    out = []
    # TODO
    return out


def deadband(a, frac_bits):
    """The amplitude below which a rounded decay can sustain itself."""
    # TODO
    return 0.0


if __name__ == "__main__":
    q = 2.0 ** -8
    seq = zero_input(0.8, 20 * q, 8, 40)
    print("rounded, in LSBs:", [round(v / q, 1) for v in seq[:14]])
    print("settles at      :", seq[-1] / q if seq else None, "LSB")
    print("deadband        :", deadband(0.8, 8) / q, "LSB")
    cut = zero_input(0.8, 20 * q, 8, 40, "truncate")
    print("truncated ends at:", cut[-1] if cut else None)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def q_round(v, frac_bits):
    """Round a scalar to the nearest multiple of the step."""
    q = 2.0 ** (-frac_bits)
    return float(np.round(np.asarray(v, dtype=float) / q) * q)


def q_trunc(v, frac_bits):
    """Truncate a scalar towards zero onto the step grid."""
    q = 2.0 ** (-frac_bits)
    return float(np.trunc(np.asarray(v, dtype=float) / q) * q)


def zero_input(a, y0, frac_bits, steps, mode="round"):
    """Run y <- Q(a*y) from y0, recording each value before it is stepped."""
    y = float(y0)
    out = []
    for _ in range(steps):
        out.append(y)
        if mode == "truncate":
            y = q_trunc(a * y, frac_bits)
        else:
            y = q_round(a * y, frac_bits)
    return out


def deadband(a, frac_bits):
    """The amplitude below which a rounded decay can sustain itself."""
    q = 2.0 ** (-frac_bits)
    return q / (2.0 * (1.0 - abs(a)))


if __name__ == "__main__":
    q = 2.0 ** -8
    seq = zero_input(0.8, 20 * q, 8, 40)
    print("rounded, in LSBs:", [round(v / q, 1) for v in seq[:14]])
    print("settles at      :", seq[-1] / q if seq else None, "LSB")
    print("deadband        :", deadband(0.8, 8) / q, "LSB")
    cut = zero_input(0.8, 20 * q, 8, 40, "truncate")
    print("truncated ends at:", cut[-1] if cut else None)
'''}],
                "hints": [
                    "`q_round` and `q_trunc` differ in one function call; write one and copy it.",
                    "`np.trunc(-1.6)` is `-1.0` while `np.floor(-1.6)` is `-2.0` — only the first is magnitude truncation, and only the first kills the limit cycle.",
                    "In `zero_input`, append first and step second, or your first recorded value will already have been quantised once.",
                    "`deadband` needs `abs(a)`: a pole at -0.8 sustains a cycle of exactly the same amplitude as one at +0.8.",
                ],
                "tests": [
                    {"name": "rounding and truncation differ on the same value", "code": r'''
_q = 2.0 ** -8
assert abs(q_round(1.6 * _q, 8) - 2.0 * _q) < 1e-15, \
    f"1.6 LSB rounds up to 2 LSB, got {q_round(1.6 * _q, 8) / _q} LSB"
assert abs(q_trunc(1.6 * _q, 8) - 1.0 * _q) < 1e-15, \
    f"1.6 LSB truncates down to 1 LSB, got {q_trunc(1.6 * _q, 8) / _q} LSB"
assert abs(q_trunc(-1.6 * _q, 8) + 1.0 * _q) < 1e-15, \
    "magnitude truncation moves towards zero, so -1.6 LSB becomes -1 LSB, not -2"
'''},
                    {"name": "the deadband matches the derivation", "code": r'''
_q = 2.0 ** -8
assert abs(deadband(0.8, 8) / _q - 2.5) < 1e-9, \
    f"q/(2*(1-0.8)) is 2.5 LSB, got {deadband(0.8, 8) / _q}"
assert abs(deadband(-0.8, 8) - deadband(0.8, 8)) < 1e-18, \
    "a negative pole has the same deadband — take the absolute value of a"
assert deadband(0.99, 8) > 10 * deadband(0.8, 8), \
    "the deadband grows without limit as the pole approaches the unit circle"
'''},
                    {"name": "the sequence starts where it was put", "code": r'''
_q = 2.0 ** -8
_s = zero_input(0.8, 20 * _q, 8, 40)
assert len(_s) == 40, f"expected 40 recorded values, got {len(_s)}"
assert abs(_s[0] - 20 * _q) < 1e-15, \
    f"record the value before stepping, so the first entry is y0 = 20 LSB, got {_s[0] / _q} LSB"
'''},
                    {"name": "rounding leaves a cycle sitting inside the deadband", "code": r'''
_q = 2.0 ** -8
_s = zero_input(0.8, 20 * _q, 8, 40)
assert abs(_s[-1] - 2.0 * _q) < 1e-15, \
    f"this decay locks at 2 LSB and stays there; got {_s[-1] / _q} LSB"
assert _s[-1] == _s[-2], "once locked, consecutive values are identical — that is the limit cycle"
assert abs(_s[-1]) <= deadband(0.8, 8) + 1e-15, \
    "the sustained amplitude must sit inside the deadband your formula predicts"
'''},
                    {"name": "a bigger start still ends in the same cycle", "code": r'''
_q = 2.0 ** -8
_s = zero_input(0.8, 100 * _q, 8, 60)
assert abs(_s[-1] - 2.0 * _q) < 1e-15, \
    f"the deadband is a property of the pole, not of where you started; got {_s[-1] / _q} LSB"
'''},
                    {"name": "a negative pole alternates instead of sticking", "code": r'''
_q = 2.0 ** -8
_s = zero_input(-0.8, 20 * _q, 8, 40)
assert abs(abs(_s[-1]) - 2.0 * _q) < 1e-15, \
    f"the amplitude is the same 2 LSB, got {abs(_s[-1]) / _q}"
assert _s[-1] * _s[-2] < 0, \
    "with a negative pole the cycle flips sign every sample — a tone at half the sample rate"
'''},
                    {"name": "magnitude truncation removes the cycle", "code": r'''
_q = 2.0 ** -8
_s = zero_input(0.8, 20 * _q, 8, 40, "truncate")
assert _s[-1] == 0.0, \
    f"truncating towards zero can only ever shrink the value, so it must reach 0; got {_s[-1] / _q} LSB"
assert _s.index(0.0) == 10, \
    f"from 20 LSB at a = 0.8 it reaches zero on step 10; got {_s.index(0.0)} — check that you truncate rather than floor"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A fourth-order Butterworth in Q15, and a defence of every word length in it",
        "runtime": "python",
        "minutes": 150,
        "brief": r'''
`spec.py` holds a fourth-order Butterworth low-pass at $f_c/f_s = 0.05$, already
factored into two second-order sections, together with a double-precision cascade to
judge your work against. Its poles sit at radius 0.9415 and 0.8638 — ordinary for a
narrow-band design, and quite far enough from the unit circle to be interesting.

Implement it in fixed point and then answer, with numbers, four questions a reviewer
will ask.

1. **How many coefficient bits?** Quantise the section coefficients onto a
   $2^{-f}$ grid and look at where the poles end up. Then do the same to the expanded
   quartic denominator, and compare.
2. **How many data bits?** Round every stored value to the data grid and measure the
   signal-to-noise ratio against the double-precision reference.
3. **What happens on overload?** Drive it past full scale with saturating arithmetic
   and again with wrapping arithmetic, and measure both.
4. **What does it do when the input stops?** Run it into silence and look at the tail.

## The functions

- `q_round(v, frac_bits)` — round onto the grid; must work on scalars and arrays.
- `limit(v, int_bits, frac_bits, mode)` — `"saturate"` clamps, `"wrap"` folds.
- `quantise_sections(sections, coef_frac_bits)` — round every coefficient of every
  section, leaving each `a[0]` at exactly 1.0.
- `max_pole_radius(sections)` — the largest pole magnitude across all sections.
- `direct_denominator(sections)` — the sections' denominators convolved into one
  polynomial, which is what an expanded direct form would store.
- `fixed_cascade(x, sections, coef_frac_bits, data_frac_bits, mode, int_bits)` — the
  filter itself.
- `snr_db(ref, got)` — ten times the base-ten logarithm of the ratio of the mean
  square of `ref` to the mean square of `got - ref`.

## The structure to implement

Each section is a transposed direct form II, which is the standard fixed-point choice
because it needs only two state words and they hold values of the same order as the
signal:

```text
y[n] = b0*x[n] + w1
w1   = b1*x[n] - a1*y[n] + w2
w2   = b2*x[n] - a2*y[n]
```

Round each of those three results to the data grid and pass each through `limit`
before storing it. Feed the output of section one into section two.

## Suggested order

Write `q_round` and `limit` first and check them against module 1 and module 3. Then
`quantise_sections` and the pole work, which needs no simulation at all. Leave
`fixed_cascade` until last; by then you will know which word lengths to expect it to
survive.
''',
        "deliverables": [
            "`q_round`, `limit` and `quantise_sections`, working on scalars and arrays, with the leading denominator coefficient of every section left exactly 1.0.",
            "`max_pole_radius` and `direct_denominator`, used together to show at what coefficient word length the expanded direct form becomes unstable while the cascade does not.",
            "`fixed_cascade` implementing the transposed direct form II above, with rounding and limiting on all three stored results, and the sections in series.",
            "`snr_db`, and a measurement of the filter's signal-to-noise ratio at two data word lengths that differ by at least four bits.",
            "A comment block at the top of `main.py` stating the coefficient word length, the data word length and the overflow mode you would ship, each justified by one of your own measured numbers.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, and no DSP or filter-design library.",
            "`spec.py` is read only; the coefficients and the reference cascade come from it unchanged.",
            "Every value stored in a state word must be rounded to the data grid and limited. Keeping full precision in the states is the one shortcut that would make all of this look easy and none of it true.",
            "The accumulator itself may hold full precision — round once per stored result, not once per product.",
        ],
        "rubric": [
            {"criterion": "Fixed-point primitives", "weight": 20,
             "evidence": "Rounding lands on the grid for scalars and arrays, saturation stops one LSB below full scale, and wrapping folds the range as two's complement addition does."},
            {"criterion": "Coefficient word length", "weight": 25,
             "evidence": "Quantised section poles stay within a few thousandths of the exact radii, and the expanded quartic denominator at the same word length is shown to reach the unit circle while the cascade does not."},
            {"criterion": "Data word length and noise", "weight": 25,
             "evidence": "The fixed-point cascade tracks the double-precision reference, and the measured signal-to-noise ratio improves by at least twenty decibels when the data word grows by six bits."},
            {"criterion": "Overload and quiescent behaviour", "weight": 30,
             "evidence": "Saturating arithmetic bounds the error to the size of the overload while wrapping does not, and the zero-input tail settles into a limit cycle of a few LSBs rather than growing."},
        ],
        "hints": [
            "`np.round(v / q) * q` is the whole of `q_round`, and it already works on arrays; keep `float()` conversions out of it and put them at the call site.",
            "`limit` can dispatch on `mode` with a single `if`; `np.clip` for saturation and the `np.mod` fold from module 3 for wrapping.",
            "`direct_denominator` is `np.convolve` applied across the sections' `a` arrays, starting from `np.array([1.0])`.",
            "In `fixed_cascade`, compute `y` first, then `w1`, then `w2`, and be careful to use the *new* `y` in the `w1` and `w2` updates — that is what makes it the transposed form.",
            "Quantise the coefficients once, before the sample loop. Doing it inside the loop is both slow and a misreading of what a stored coefficient is.",
        ],
        "files": [
            {"name": "spec.py", "ro": True, "content": r'''
"""The filter under test. Do not edit — the checks rely on these numbers.

A fourth-order Butterworth low-pass at fc/fs = 0.05, designed by the bilinear
transform and factored into two second-order sections, each normalised to unit
gain at DC.
"""
import numpy as np

SECTIONS = [
    (np.array([0.00587826, 0.01175651, 0.00587826]),
     np.array([1.0, -1.86286416, 0.88637718])),
    (np.array([0.00544110, 0.01088220, 0.00544110]),
     np.array([1.0, -1.72432584, 0.74609023])),
]


def float_cascade(x, sections):
    """The double-precision reference: transposed direct form II, no quantisation."""
    y = np.asarray(x, dtype=float).copy()
    for b, a in sections:
        out = np.zeros_like(y)
        w1 = 0.0
        w2 = 0.0
        for n in range(len(y)):
            acc = b[0] * y[n] + w1
            w1 = b[1] * y[n] - a[1] * acc + w2
            w2 = b[2] * y[n] - a[2] * acc
            out[n] = acc
        y = out
    return y


def test_signal(count=1200):
    """A two-tone input: one tone in the passband, one well outside it."""
    n = np.arange(count)
    return 0.5 * np.sin(2 * np.pi * 0.02 * n) + 0.25 * np.sin(2 * np.pi * 0.3 * n)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from spec import SECTIONS, float_cascade, test_signal

# Word lengths I would ship:
#   coefficients -> TODO bits, because ...
#   data         -> TODO bits, because ...
#   overflow     -> TODO, because ...


def q_round(v, frac_bits):
    """Round onto the 2**-frac_bits grid. Scalars and arrays alike."""
    # TODO
    return np.asarray(v, dtype=float)


def limit(v, int_bits, frac_bits, mode="saturate"):
    """Apply the overflow behaviour: 'saturate' clamps, 'wrap' folds."""
    # TODO
    return np.asarray(v, dtype=float)


def quantise_sections(sections, coef_frac_bits):
    """Round every coefficient; leave each a[0] at exactly 1.0."""
    # TODO
    return list(sections)


def max_pole_radius(sections):
    """Largest pole magnitude across all sections."""
    # TODO
    return 0.0


def direct_denominator(sections):
    """The sections' denominators convolved into one polynomial."""
    # TODO
    return np.array([1.0])


def fixed_cascade(x, sections, coef_frac_bits, data_frac_bits,
                  mode="saturate", int_bits=0):
    """Transposed direct form II per section, quantised and limited throughout."""
    # TODO
    return np.zeros_like(np.asarray(x, dtype=float))


def snr_db(ref, got):
    """Signal power over error power, in decibels."""
    # TODO
    return 0.0


if __name__ == "__main__":
    x = test_signal()
    ref = float_cascade(x, SECTIONS)
    print("exact pole radius  :", max_pole_radius(SECTIONS))
    print("cascade at 8 bits  :", max_pole_radius(quantise_sections(SECTIONS, 8)))
    got = fixed_cascade(x, SECTIONS, 14, 14)
    print("SNR at 14 data bits:", snr_db(ref, got), "dB")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from spec import SECTIONS, float_cascade, test_signal

# Word lengths I would ship:
#   coefficients -> 14 fractional bits (Q1.14). At 8 bits the expanded quartic
#                   denominator reaches radius 1.0 and the filter is no longer
#                   stable, while the cascade at the same 8 bits moves its worst
#                   pole only from 0.94148 to 0.94166. The cascade is therefore
#                   not the binding constraint; 14 bits is chosen because it
#                   holds every section pole to within 1.4e-5 of its exact
#                   radius, which puts the coefficient error an order of
#                   magnitude below the data-rounding error at the same word
#                   length.
#   data         -> 14 fractional bits. Measured SNR against the double-precision
#                   reference is 22.2 dB at 8 bits and 56.1 dB at 14, and above
#                   14 the coefficient error, not the data rounding, sets the
#                   floor — so more data bits buy nothing without more
#                   coefficient bits.
#   overflow     -> saturate. On a square-wave overload the peak error is 0.32
#                   saturating and 1.60 wrapping: wrapping turns an overload
#                   into a full-scale sign inversion.


def q_round(v, frac_bits):
    """Round onto the 2**-frac_bits grid. Scalars and arrays alike."""
    q = 2.0 ** (-frac_bits)
    return np.round(np.asarray(v, dtype=float) / q) * q


def limit(v, int_bits, frac_bits, mode="saturate"):
    """Apply the overflow behaviour: 'saturate' clamps, 'wrap' folds."""
    v = np.asarray(v, dtype=float)
    half = 2.0 ** int_bits
    if mode == "wrap":
        return np.mod(v + half, 2.0 * half) - half
    return np.clip(v, -half, half - 2.0 ** (-frac_bits))


def quantise_sections(sections, coef_frac_bits):
    """Round every coefficient; leave each a[0] at exactly 1.0."""
    out = []
    for b, a in sections:
        qb = q_round(b, coef_frac_bits)
        qa = q_round(a, coef_frac_bits)
        qa = np.asarray(qa, dtype=float).copy()
        qa[0] = 1.0
        out.append((qb, qa))
    return out


def max_pole_radius(sections):
    """Largest pole magnitude across all sections."""
    worst = 0.0
    for b, a in sections:
        r = np.abs(np.roots(np.asarray(a, dtype=float)))
        worst = max(worst, float(np.max(r)))
    return worst


def direct_denominator(sections):
    """The sections' denominators convolved into one polynomial."""
    d = np.array([1.0])
    for b, a in sections:
        d = np.convolve(d, np.asarray(a, dtype=float))
    return d


def fixed_cascade(x, sections, coef_frac_bits, data_frac_bits,
                  mode="saturate", int_bits=0):
    """Transposed direct form II per section, quantised and limited throughout."""
    qs = quantise_sections(sections, coef_frac_bits)
    y = np.asarray(x, dtype=float).copy()
    for b, a in qs:
        out = np.zeros_like(y)
        w1 = 0.0
        w2 = 0.0
        for n in range(len(y)):
            acc = float(limit(q_round(b[0] * y[n] + w1, data_frac_bits),
                              int_bits, data_frac_bits, mode))
            w1 = float(limit(q_round(b[1] * y[n] - a[1] * acc + w2, data_frac_bits),
                             int_bits, data_frac_bits, mode))
            w2 = float(limit(q_round(b[2] * y[n] - a[2] * acc, data_frac_bits),
                             int_bits, data_frac_bits, mode))
            out[n] = acc
        y = out
    return y


def snr_db(ref, got):
    """Signal power over error power, in decibels."""
    ref = np.asarray(ref, dtype=float)
    got = np.asarray(got, dtype=float)
    err = got - ref
    pe = float(np.mean(err * err))
    if pe <= 0.0:
        return float("inf")
    return float(10.0 * np.log10(float(np.mean(ref * ref)) / pe))


if __name__ == "__main__":
    x = test_signal()
    ref = float_cascade(x, SECTIONS)
    print("exact pole radius  :", max_pole_radius(SECTIONS))
    print("cascade at 8 bits  :", max_pole_radius(quantise_sections(SECTIONS, 8)))
    got = fixed_cascade(x, SECTIONS, 14, 14)
    print("SNR at 14 data bits:", snr_db(ref, got), "dB")
'''},
        ],
        "tests": [
            {"name": "the fixed-point primitives round and clamp correctly", "code": r'''
import numpy as np
assert abs(float(q_round(0.1, 15)) - 0.100006103515625) < 1e-15, \
    f"0.1 on a 2**-15 grid is 0.100006103515625, got {float(q_round(0.1, 15))}"
_arr = q_round(np.array([0.3, -0.3]), 3)
assert abs(float(_arr[0]) - 0.25) < 1e-15 and abs(float(_arr[1]) + 0.25) < 1e-15, \
    "q_round must work elementwise on an array as well as on a scalar"
assert abs(float(limit(1.8, 0, 15, "saturate")) - 0.999969482421875) < 1e-15, \
    "saturation stops one LSB below full scale, at 1 - 2**-15"
assert abs(float(limit(1.8, 0, 15, "wrap")) + 0.2) < 1e-12, \
    "wrapping folds 1.8 to -0.2 — an overload becomes a large negative number"
'''},
            {"name": "quantised coefficients stay on the grid with the leading one intact", "code": r'''
import numpy as np
from spec import SECTIONS
_qs = quantise_sections(SECTIONS, 14)
assert len(_qs) == 2, f"there are two sections, got {len(_qs)}"
_q = 2.0 ** -14
for _b, _a in _qs:
    assert abs(_a[0] - 1.0) < 1e-15, "each a[0] is structural and must stay exactly 1.0"
    for _c in list(_b) + list(_a):
        assert abs(_c / _q - round(_c / _q)) < 1e-6, \
            f"every stored coefficient must be an exact multiple of one LSB; {_c} is not"
assert abs(float(np.max(np.abs(SECTIONS[0][1] - _qs[0][1]))) - 0.0) > 0.0, \
    "at 14 bits the coefficients really do move — if nothing changed, the rounding is not happening"
'''},
            {"name": "eight-bit coefficients destroy the direct form but not the cascade", "code": r'''
import numpy as np
from spec import SECTIONS
_exact = max_pole_radius(SECTIONS)
assert abs(_exact - 0.9414760644859751) < 1e-9, \
    f"the outer section sits at radius 0.94147606, got {_exact}"
_casc = max_pole_radius(quantise_sections(SECTIONS, 8))
assert _casc < 0.95, \
    f"quantised section by section, the poles barely move: expected about 0.9417, got {_casc}"
_d = direct_denominator(SECTIONS)
assert len(_d) == 5, f"two quadratics convolve to a quartic with five coefficients, got {len(_d)}"
_qd = q_round(_d, 8)
_qd = np.asarray(_qd, dtype=float).copy()
_qd[0] = 1.0
_rd = float(np.max(np.abs(np.roots(_qd))))
assert _rd >= 0.999, \
    f"the same filter expanded into one quartic reaches the unit circle at 8 bits; expected >= 0.999, got {_rd}"
'''},
            {"name": "the fixed-point filter tracks the reference and improves with data bits", "code": r'''
import numpy as np
from spec import SECTIONS, float_cascade, test_signal
_x = test_signal()
_ref = float_cascade(_x, SECTIONS)
_lo = snr_db(_ref, fixed_cascade(_x, SECTIONS, 14, 8))
_hi = snr_db(_ref, fixed_cascade(_x, SECTIONS, 14, 14))
assert _lo > 15.0, f"even at 8 data bits the filter should be recognisable: got {_lo:.1f} dB"
assert _hi > 45.0, f"at 14 data bits expect about 56 dB, got {_hi:.1f} dB"
assert _hi - _lo > 20.0, \
    f"six more data bits must buy well over 20 dB: {_lo:.1f} dB at 8 bits, {_hi:.1f} dB at 14"
'''},
            {"name": "saturation degrades gracefully where wraparound does not", "code": r'''
import numpy as np
from spec import SECTIONS, float_cascade
_n = np.arange(1200)
_x = 0.98 * np.sign(np.sin(2 * np.pi * 0.01 * _n))
_ref = float_cascade(_x, SECTIONS)
assert float(np.max(np.abs(_ref))) > 1.0, \
    "this input is meant to drive the filter past full scale; the reference should exceed 1.0"
_sat = fixed_cascade(_x, SECTIONS, 14, 15, "saturate")
_wrp = fixed_cascade(_x, SECTIONS, 14, 15, "wrap")
_se = float(np.max(np.abs(_sat - _ref)))
_we = float(np.max(np.abs(_wrp - _ref)))
assert _se < 0.5, f"saturating, the error is only the size of the overload: expected about 0.32, got {_se:.3f}"
assert _we > 3 * _se, \
    f"wrapping should be several times worse: saturate {_se:.3f}, wrap {_we:.3f}"
assert float(np.max(np.abs(_sat))) <= 1.0, "a saturating output can never leave the range"
'''},
            {"name": "the tail after the input stops is a small locked limit cycle", "code": r'''
import numpy as np
from spec import SECTIONS, float_cascade
_burst = np.zeros(2000)
_burst[:200] = 0.8 * np.sin(2 * np.pi * 0.03 * np.arange(200))
_got = fixed_cascade(_burst, SECTIONS, 14, 15)
_ref = float_cascade(_burst, SECTIONS)
assert float(np.max(np.abs(_ref[1000:]))) < 1e-12, \
    "in double precision the tail is gone by sample 1000"
_tail = _got[1000:]
_peak = float(np.max(np.abs(_tail))) * 2.0 ** 15
assert _peak > 0.0, \
    "quantised, the tail does not reach zero — if it did, the states are not being rounded"
assert _peak < 64.0, \
    f"the limit cycle must stay small and bounded: expected about 6 LSB, got {_peak:.0f} LSB"
assert abs(_tail[-1] - _tail[-2]) < 1e-15, \
    "by the end the cycle has locked, so consecutive samples are identical"
'''},
        ],
    },
}
