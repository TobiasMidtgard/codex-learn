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
