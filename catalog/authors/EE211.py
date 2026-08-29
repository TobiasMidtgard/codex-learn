"""EE211 — Signals and Systems.

A second-year course. It assumes the first year of the programme and nothing more:
DC and AC circuit analysis, phasors and impedance, complex numbers and calculus,
Boolean algebra, elementary Python, and fields. Everything above that line is built
here.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number in a test or a notice was produced by running the code,
    the circuit solver or the visualiser, never assumed
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it with the reference drawing
"""

COURSE = {
    "id": "EE211",
    "title": "Signals and Systems",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE102", "EE111"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◊",
    "summary": (
        "First year taught you to analyse a circuit at one frequency at a time. This "
        "course replaces that with a single description that covers every frequency at "
        "once. Two assumptions — linearity and time invariance — are enough to prove "
        "that a system's response to one impulse determines its response to everything, "
        "and that the awkward integral joining the two becomes an ordinary multiplication "
        "once both signals are written as spectra. Along the way the course settles what "
        "a spectrum actually is for a periodic signal and for an aperiodic one, and what "
        "sampling does to it, which is the point at which a signal stops being electrical "
        "and starts being a list of numbers."
    ),
    "outcomes": [
        "Decide whether a given system is linear, whether it is time invariant, and say which test it fails.",
        "Convolve two signals by hand and in code, and explain why the impulse response is a complete description of an LTI system.",
        "Compute the Fourier coefficients of a periodic signal, read its line spectrum, and relate the rate at which the harmonics decay to the smoothness of the waveform.",
        "Predict the frequency a sampled component will appear at, choose a sample rate that avoids aliasing, and specify the analogue filter that has to come first.",
        "Write the transfer function of a circuit from its impedances, read its Bode plot, and use $Y = HX$ instead of solving a differential equation.",
    ],
    "assessment": (
        "Four quizzes, two circuits designed and measured in the schematic editor, one "
        "guided derivation, two Python labs checked by execution, and a capstone that "
        "builds a working spectrum analyser and uses it to demonstrate the convolution "
        "theorem on a signal it has sampled itself."
    ),
    "reading": [
        "*Signals and Systems*, Oppenheim, Willsky & Nawab — chapters 1 to 4, which is this course in its canonical order.",
        "*The Scientist and Engineer's Guide to Digital Signal Processing*, Smith — free online, and unusually good on what a spectrum looks like in practice.",
        "*The Art of Electronics*, Horowitz & Hill — appendix on Fourier and the section on filters, for the engineering rather than the mathematics.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Linearity, time invariance and the impulse response",
            "summary": "Two assumptions, and everything a system will ever do collapses into one list of numbers.",
            "concepts": [
                "A **system** is a rule that turns one signal into another: $y = S\\{x\\}$. An amplifier, a filter, a length of cable and a control loop are all systems in this sense.",
                "A system is **linear** when scaling the input scales the output by the same factor, and when the response to a sum of inputs is the sum of the responses: $S\\{a x_1 + b x_2\\} = a\\,S\\{x_1\\} + b\\,S\\{x_2\\}$.",
                "A straight-line graph is not the test. $y = 2x + 3$ plots as a straight line and is **not** linear, because doubling $x$ does not double $y$. Squaring, rectifying and clipping fail as well.",
                "A system is **time invariant** when delaying the input only delays the output: if $x(t) \\to y(t)$ then $x(t - t_0) \\to y(t - t_0)$, with the same shape. A circuit whose component values are being changed as it runs is not.",
                "**LTI** means both. Every resistor, capacitor and inductor network from EE102 is LTI, provided nothing saturates and no switch moves.",
                "The **unit impulse** $\\delta[n]$ is 1 at $n = 0$ and zero everywhere else; in continuous time $\\delta(t)$ is the limit of a pulse of unit area as it becomes infinitely narrow. The output it produces is the **impulse response** $h$.",
                "Any signal is a sum of shifted, scaled impulses: $x[n] = \\sum_k x[k]\\,\\delta[n-k]$. Time invariance says each of those impulses produces $h$, shifted; linearity says the outputs add. So $y[n] = \\sum_k x[k]\\,h[n-k]$ — the **convolution** $y = x * h$.",
                "That is the central result of the module: for an LTI system, $h$ is a complete description. Measure it once and you can predict the response to anything.",
                "Convolution is commutative and associative, so two systems in cascade have impulse response $h_1 * h_2$ and the order they are wired in does not matter. Two finite responses of $N$ and $M$ samples convolve to $N + M - 1$ samples.",
                "A system is **causal** when $h[n] = 0$ for $n < 0$: no output before the input arrives. It is **BIBO stable** when $\\sum_n |h[n]|$ is finite, and that sum is exactly the largest output an input bounded by 1 can produce.",
            ],
            "quiz": {
                "title": "Which systems are LTI, and what follows",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Which of these systems is linear but **not** time invariant?",
                        "opts": [
                            "$y(t) = x(t)\\cos(2\\pi f_0 t)$ — the input multiplied by a fixed sinusoid",
                            "$y(t) = x(t)^2$ — the input through a square-law detector",
                            "$y(t) = x(t - 3)$ — the input delayed by three seconds",
                            "$y(t) = |x(t)|$ — the input through a full-wave rectifier",
                        ],
                        "a": 0,
                        "why": r'''
Multiplying by a sinusoid is linear — scale the input and the output scales, add two
inputs and the outputs add — but it is not time invariant, because the sinusoid is
fixed to the clock rather than to the signal. Delay the input by a quarter of the
sinusoid's period and the output is not simply delayed; it is a different waveform.
That is the mixer, the one useful non-time-invariant circuit in the whole of radio.
Squaring and taking a modulus both fail linearity; a pure delay is LTI.
''',
                    },
                    {
                        "q": "An amplifier is measured as $y = 2x + 3$: a gain of two with a 3 V offset. Is it linear?",
                        "opts": [
                            "yes — its input–output graph is a straight line",
                            "yes, provided the offset is small compared with the signal",
                            "no — the response to zero input is not zero, so scaling fails",
                            "no — the offset means it fails time invariance as well as linearity",
                        ],
                        "a": 2,
                        "why": r'''
No. Put in $x = 0$ and you get 3 V out; put in twice any input and you do not get twice
the output. "Linear" in this course is the algebraic property, not the shape of the
graph, and the two part company exactly here — the technical name for $2x + 3$ is
*affine*. Answering "it fails time invariance as well" is wrong for a different reason worth
being clear about: this amplifier *is* time invariant, because delaying the input delays $2x + 3$ by the same amount. The
two tests are independent and a system can fail either one alone. The practical fix is
the one every instrumentation engineer uses: subtract the offset first, and what is left
is genuinely linear and can be treated with everything in this course.
''',
                    },
                    {
                        "q": "An LTI system has impulse response $h = \\{1, 1, 1\\}$ for $n = 0, 1, 2$. The input is $x = \\{1, 2\\}$. What is the output?",
                        "opts": ["$\\{1, 2, 1\\}$", "$\\{1, 2, 3, 2\\}$", "$\\{2, 3, 3, 1\\}$", "$\\{1, 3, 3, 2\\}$"],
                        "a": 3,
                        "why": r'''
Convolve: the input is one impulse of height 1 at $n = 0$ and one of height 2 at
$n = 1$, so the output is $h$ plus $2h$ delayed by one sample —
$\{1,1,1\} + \{0,2,2,2\} = \{1,3,3,2\}$. Four samples, as $2 + 3 - 1 = 4$ requires.
The answer $\{2,3,3,1\}$ is the same numbers convolved the wrong way round in the index,
which is worth guarding against: line the two sequences up and slide one past the other
rather than trusting the arithmetic in your head.
''',
                    },
                    {
                        "q": "A 5-sample signal is fed through an LTI system whose impulse response is 8 samples long. How many samples does the output have?",
                        "opts": ["5", "8", "12", "40"],
                        "a": 2,
                        "why": r'''
$5 + 8 - 1 = 12$. The first output sample appears when the first input sample meets the
first sample of $h$, and the last when the last input sample meets the last of $h$;
count the positions and you get $N + M - 1$. The answer 40 multiplies the lengths, which
counts the multiplications the convolution performs rather than the samples it produces
— a useful number, but a different one.
''',
                    },
                    {
                        "q": "Why does knowing $h$ alone let you predict an LTI system's response to *any* input?",
                        "opts": [
                            "because $h$ contains the system's gain and its bandwidth, and nothing else matters",
                            "because every input can be written as a sum of shifted impulses, and LTI forces the output to be the same sum of shifted copies of $h$",
                            "because $h$ is measured with the largest possible input, so smaller ones are covered",
                            "it does not — a second measurement with a step input is always needed",
                        ],
                        "a": 1,
                        "why": r'''
The decomposition is the whole argument. Write $x[n] = \sum_k x[k]\delta[n-k]$: that is
an identity, true of any signal. Time invariance says the impulse at $k$ produces
$h[n-k]$; linearity says the pieces add with the same weights $x[k]$. Convolution is
what is left. Note what is *not* assumed — nothing about the size of the input, which
is why saturation is fatal: an amplifier that clips is no longer linear and its measured
$h$ stops predicting anything.
''',
                    },
                    {
                        "q": "Two systems have impulse responses $h_1[n] = (0.5)^n$ and $h_2[n] = (1.1)^n$ for $n \\ge 0$. Which is BIBO stable?",
                        "opts": [
                            "both, because both responses are finite at every sample",
                            "neither, because both go on forever",
                            "$h_1$ only",
                            "$h_2$ only, because it is the one that grows",
                        ],
                        "a": 2,
                        "why": r'''
Stability is about the **sum** $\sum|h[n]|$, not about any individual sample.
$\sum (0.5)^n = 2$, finite, so $h_1$ is stable — and that 2 is a real number you can
use: no input bounded by 1 V can ever produce more than 2 V out. $\sum (1.1)^n$
diverges, so a bounded input can drive $h_2$'s output arbitrarily large. Every sample of
$h_2$ is finite, which is exactly the trap in "both, because both responses are finite at every
sample": an infinite sum of finite terms
is what instability looks like.
''',
                    },
                ],
            },
            "lab": {
                "title": "Convolution, and the gain hiding in an impulse response",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Three functions. Together they take an LTI system apart.

- `convolve(x, h)` returns the output of a system with impulse response `h` when the
  input is `x`. The result has `len(x) + len(h) - 1` samples. Write the double loop
  — `y[i + j] += x[i] * h[j]` — rather than reaching for a library, because the index
  arithmetic is the thing worth owning.
- `iir_impulse_response(a, n)` returns the first `n` samples of the impulse response
  of the recursive system $y[n] = a\,y[n-1] + x[n]$. Drive it with the impulse
  $x = 1, 0, 0, \dots$ and record $y$ at each step. You should recover $a^n$, which is
  a good check that the recursion is written correctly.
- `bibo_gain(h)` returns $\sum_n |h[n]|$ — the largest output an input bounded by 1
  can ever produce.

Plain lists throughout; NumPy is not needed and not wanted here.
''',
                "files": [{"name": "main.py", "content": r'''
"""Convolution: an LTI system's whole behaviour, from one list of numbers."""


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`.

    The result has len(x) + len(h) - 1 samples.
    """
    # TODO: make a list of zeros of the right length, then accumulate
    #       y[i + j] += x[i] * h[j] over every pair of indices.
    return []


def iir_impulse_response(a, n):
    """First `n` samples of h for the system y[k] = a*y[k-1] + x[k]."""
    # TODO: run the recursion with x = 1 at k = 0 and x = 0 afterwards,
    #       appending y at every step. Start from y = 0.
    return []


def bibo_gain(h):
    """The largest output an input bounded by 1 can produce: the sum of |h|."""
    # TODO: one sum of absolute values.
    return 0.0


if __name__ == "__main__":
    print("{1,2} through {1,1,1}:", convolve([1.0, 2.0], [1.0, 1.0, 1.0]))
    h = iir_impulse_response(0.5, 6)
    print("impulse response of y = 0.5 y[-1] + x:", h)
    print("its gain from a bounded input:", bibo_gain(iir_impulse_response(0.5, 60)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Convolution: an LTI system's whole behaviour, from one list of numbers.

Checked against hand-worked examples: {1,2} * {1,1,1} = {1,3,3,2}, and the
recursion y[k] = 0.5 y[k-1] + x[k] gives h = 1, 0.5, 0.25, ... whose absolute
sum tends to 1/(1 - 0.5) = 2.
"""


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`.

    The result has len(x) + len(h) - 1 samples.
    """
    y = [0.0] * (len(x) + len(h) - 1)
    for i, xv in enumerate(x):
        for j, hv in enumerate(h):
            y[i + j] += xv * hv
    return y


def iir_impulse_response(a, n):
    """First `n` samples of h for the system y[k] = a*y[k-1] + x[k]."""
    h = []
    y = 0.0
    for k in range(n):
        x = 1.0 if k == 0 else 0.0
        y = a * y + x
        h.append(y)
    return h


def bibo_gain(h):
    """The largest output an input bounded by 1 can produce: the sum of |h|."""
    return sum(abs(v) for v in h)


if __name__ == "__main__":
    print("{1,2} through {1,1,1}:", convolve([1.0, 2.0], [1.0, 1.0, 1.0]))
    h = iir_impulse_response(0.5, 6)
    print("impulse response of y = 0.5 y[-1] + x:", h)
    print("its gain from a bounded input:", bibo_gain(iir_impulse_response(0.5, 60)))
'''}],
                "hints": [
                    "`convolve` needs its output list allocated *before* the loops, because the inner statement adds into a slot rather than appending to the end.",
                    "In `iir_impulse_response` the state is one number. Set `y = 0.0` before the loop, and inside it compute `y = a * y + x` with `x` equal to 1 only on the first pass.",
                    "If your impulse response comes out as $1, 1, 1, \\dots$ you are feeding in a step rather than an impulse: the input is 1 at $k = 0$ **and zero at every later step**.",
                    "`bibo_gain` is `sum(abs(v) for v in h)`. For $h[n] = a^n$ it should come out near $1/(1-a)$ once `n` is large enough.",
                ],
                "tests": [
                    {"name": "a two-sample input through a three-sample response", "code": r'''
y = convolve([1.0, 2.0], [1.0, 1.0, 1.0])
assert len(y) == 4, f"2 + 3 - 1 is 4 samples, got {len(y)}"
assert all(abs(a - b) < 1e-12 for a, b in zip(y, [1.0, 3.0, 3.0, 2.0])), \
    f"expected [1, 3, 3, 2], got {y}"
'''},
                    {"name": "convolution is commutative", "code": r'''
a = convolve([1.0, 2.0, 3.0], [1.0, -1.0, 4.0])
b = convolve([1.0, -1.0, 4.0], [1.0, 2.0, 3.0])
want = [1.0, 1.0, 5.0, 5.0, 12.0]
assert len(a) == 5 and len(b) == 5, \
    f"3 + 3 - 1 is 5 samples either way round, got {len(a)} and {len(b)}"
assert all(abs(v - w) < 1e-12 for v, w in zip(a, want)), f"expected {want}, got {a}"
assert all(abs(v - w) < 1e-12 for v, w in zip(a, b)), \
    f"x * h and h * x must agree: {a} against {b}"
'''},
                    {"name": "the recursion's impulse response is a geometric decay", "code": r'''
h = iir_impulse_response(0.5, 6)
assert len(h) == 6, f"asked for 6 samples, got {len(h)}"
want = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
assert all(abs(a - b) < 1e-12 for a, b in zip(h, want)), \
    f"h[k] should be 0.5**k, so {want}; got {h}"
'''},
                    {"name": "a step through that system settles at 2", "code": r'''
h = iir_impulse_response(0.5, 10)
y = convolve([1.0] * 10, h)
assert abs(y[9] - 1.998046875) < 1e-9, \
    f"ten samples of step in, the output is the sum of the first ten h, 1.998046875, got {y[9]}"
assert y[0] == 1.0, f"the first output sample is just h[0], got {y[0]}"
'''},
                    {"name": "the sum of |h| is the worst-case gain", "code": r'''
g = bibo_gain([1.0, -2.0, 3.0])
assert abs(g - 6.0) < 1e-12, f"|1| + |-2| + |3| is 6, got {g}"
slow = bibo_gain(iir_impulse_response(0.8, 200))
assert abs(slow - 5.0) < 1e-6, \
    f"sum of 0.8**n tends to 1/(1 - 0.8) = 5, got {slow}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "The Fourier series and the spectrum of a periodic signal",
            "summary": "A repeating waveform is a sum of sinusoids at multiples of one frequency, and the list of their sizes is its spectrum.",
            "concepts": [
                "A signal is **periodic** with period $T$ when $x(t + T) = x(t)$ for all $t$. Its **fundamental frequency** is $f_0 = 1/T$, and $\\omega_0 = 2\\pi/T$.",
                "Fourier's claim: any such signal (with mild conditions that every real waveform satisfies) is a sum of sinusoids at $f_0$ and its integer multiples — the **harmonics**. Nothing at any other frequency ever appears.",
                "Trigonometric form: $x(t) = \\frac{a_0}{2} + \\sum_{n=1}^{\\infty}\\left[a_n\\cos(n\\omega_0 t) + b_n\\sin(n\\omega_0 t)\\right]$, where $a_0/2$ is the mean value of the signal.",
                "**Analysis**: $a_n = \\frac{2}{T}\\int_T x(t)\\cos(n\\omega_0 t)\\,dt$ and $b_n = \\frac{2}{T}\\int_T x(t)\\sin(n\\omega_0 t)\\,dt$. These work because harmonics are **orthogonal**: over a whole period, the product of two different harmonics integrates to zero, so the integral picks out one coefficient and discards the rest.",
                "Complex form, which is the one used from module 3 onwards: $c_n = \\frac{1}{T}\\int_T x(t)e^{-jn\\omega_0 t}\\,dt$ and $x(t) = \\sum_{n=-\\infty}^{\\infty} c_n e^{jn\\omega_0 t}$. For a real signal $c_{-n} = c_n^{*}$, so the negative frequencies carry no new information — they are the bookkeeping that keeps the sum real.",
                "The **line spectrum** plots $|c_n|$ against frequency. A periodic signal's spectrum is a set of isolated lines at $0, f_0, 2f_0, \\dots$ and is exactly zero in between.",
                "Symmetry saves work. A signal odd about $t = 0$ has only sine terms; an even one has only cosine terms; one with half-wave symmetry has only odd harmonics.",
                "The square wave of amplitude $A$, odd about the origin, has $b_n = 4A/(n\\pi)$ for odd $n$ and nothing else. Its harmonics decay as $1/n$.",
                "Smoothness sets the decay rate. A jump in the signal gives coefficients falling as $1/n$; a kink — continuous but with a jump in the slope, like a triangle wave — gives $1/n^2$. Sharp edges are expensive in bandwidth, and that is a statement about every digital signal ever transmitted.",
                "Truncating the series at $N$ harmonics overshoots each jump by about 9% of the jump height, however large $N$ is. Adding harmonics narrows the ripple but never shrinks it: this is the **Gibbs phenomenon**.",
                "**Parseval's theorem**: the mean square of the signal equals $\\left(\\frac{a_0}{2}\\right)^2 + \\sum_n \\frac{a_n^2 + b_n^2}{2}$. Power adds across harmonics even though amplitudes do not, which is why a spectrum is usually drawn as power.",
            ],
            "quiz": {
                "title": "Harmonics, symmetry and decay",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A periodic signal has a period of 2 ms. Which frequencies may appear in its spectrum?",
                        "opts": [
                            "any frequency from 0 to 500 Hz",
                            "500 Hz only",
                            "0, 500, 1000, 1500 Hz and so on",
                            "any frequency above 500 Hz",
                        ],
                        "a": 2,
                        "why": r'''
$f_0 = 1/T = 500$ Hz, and a periodic signal contains only the fundamental, its integer
multiples, and a possible DC term. The spectrum is a picket fence of lines, not a
continuous band — that is what makes it a *series* rather than a transform. "Any frequency from 0 to 500 Hz" is the answer for an aperiodic signal, which is
module 3, and the difference between the
two pictures is the single most useful thing to keep straight in this course.
''',
                    },
                    {
                        "q": "A signal is even about $t = 0$, that is $x(-t) = x(t)$. What does its Fourier series contain?",
                        "opts": [
                            "cosine terms only (plus a possible DC term)",
                            "sine terms only",
                            "odd harmonics only",
                            "no useful simplification follows from evenness",
                        ],
                        "a": 0,
                        "why": r'''
Cosine is even and sine is odd, so an even signal can be built entirely from cosines;
formally, $b_n$ integrates an even function against an odd one over a symmetric interval
and gets zero every time. This is worth exploiting before touching an integral, because
it halves the work. Answering "odd harmonics only" confuses two different symmetries: *half-wave* symmetry,
$x(t + T/2) = -x(t)$, is the one that kills the even harmonics, and the square wave has
both properties at once.
''',
                    },
                    {
                        "q": "A square wave and a triangle wave have the same period and the same amplitude. How do their harmonics compare?",
                        "opts": [
                            "identical, because they contain the same frequencies",
                            "the triangle's decay faster, because its waveform has no jump",
                            "the square's decay faster, because it spends its time at two fixed levels",
                            "neither decays — both series go on with equal terms forever",
                        ],
                        "a": 1,
                        "why": r'''
The square wave jumps, so its coefficients fall only as $1/n$; the triangle is continuous
and only its slope jumps, so its coefficients fall as $1/n^2$. Both contain the same set
of frequencies — odd multiples of $f_0$ — which is what makes "identical, because they contain the same frequencies"
tempting, but
containing a frequency and containing much of it are different things. The rule
generalises: each extra derivative that stays continuous buys another factor of $1/n$.
''',
                    },
                    {
                        "q": "You reconstruct a square wave from its first 99 harmonics and then from its first 999. What happens to the overshoot at each jump?",
                        "opts": [
                            "it halves each time the harmonic count is multiplied by ten",
                            "it disappears entirely once enough harmonics are included",
                            "it grows, because more harmonics means more ripple",
                            "it stays at about 9% of the jump, but is squeezed into a narrower region",
                        ],
                        "a": 3,
                        "why": r'''
This is Gibbs. The overshoot converges to about 8.95% of the jump height and stays there
no matter how many terms are added; what does shrink is its width, so the *energy* in the
ripple goes to zero even though its height does not. For a square wave running between
$-1$ and $+1$ the jump is 2, so the partial sum peaks near 1.179 — a number you will
compute in this module's lab. It is not a numerical error and it cannot be tuned away.
''',
                    },
                    {
                        "q": "A signal has just two harmonics, of amplitudes 3 V and 4 V. What is its RMS value?",
                        "opts": ["$7/\\sqrt{2}$ V", "5 V", "$5/\\sqrt{2}$ V", "7 V"],
                        "a": 2,
                        "why": r'''
By Parseval the mean squares add: $\frac{3^2}{2} + \frac{4^2}{2} = 12.5$, so the RMS is
$\sqrt{12.5} = 5/\sqrt{2} \approx 3.54$ V. Amplitudes never add unless the components are
at the same frequency and in phase, which harmonics by definition are not. Note also what
is *absent* from the calculation: the phases of the two harmonics. Change them and the
waveform looks completely different while its RMS value does not move at all.
''',
                    },
                    {
                        "q": "Why does multiplying $x(t)$ by $\\cos(n\\omega_0 t)$ and integrating over one period return $a_n$ and nothing else?",
                        "opts": [
                            "because the integral of any product over a period is zero unless the two factors are identical",
                            "because harmonics are orthogonal: over a whole period, any two different harmonics multiply to something that integrates to zero",
                            "because the cosine is normalised to unit area",
                            "because the higher harmonics are too small to matter",
                        ],
                        "a": 1,
                        "why": r'''
Orthogonality is the mechanism, and it is worth seeing once: $\cos(m\omega_0 t)\cos(n\omega_0 t)$
expands to half the sum of two cosines at frequencies $(m-n)\omega_0$ and $(m+n)\omega_0$,
and any whole number of cycles of a cosine integrates to zero — unless $m = n$, when the
first term becomes a constant $1/2$. That surviving constant is where the factor $2/T$ in
the analysis formula comes from. "The integral of any product over a period is zero unless the two factors are
identical" is too strong: many different products integrate to something non-zero; it is the harmonic relationship that makes them vanish.
''',
                    },
                ],
            },
            "lab": {
                "title": "Building a square wave out of sines",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
The square wave, from its coefficients to its spectrum to the Gibbs overshoot. NumPy is
imported for you; work with arrays rather than loops where you can.

The signal is a square wave of amplitude 1, odd about $t = 0$, with a fundamental of
1 Hz. Its coefficients are $b_n = 4/(n\pi)$ for odd $n$ and zero for even $n$.

- `square_coeffs(N)` returns a NumPy array of the first `N` coefficients,
  $b_1$ through $b_N$, including the zeros at the even harmonics.
- `synthesise(coeffs, t)` returns $\sum_n b_n \sin(2\pi n t)$ evaluated at every time in
  the array `t`, where `coeffs[0]` is $b_1$. The fundamental is 1 Hz, so harmonic $n$ is
  at $n$ Hz.
- `mean_square(coeffs)` returns the mean square value of that sum, which by Parseval is
  $\sum_n b_n^2/2$. For the exact square wave of amplitude 1 the answer is 1, and your
  partial sums should climb towards it.

Keeping the even coefficients as explicit zeros costs nothing and keeps the index
arithmetic honest: `coeffs[n - 1]` is always $b_n$.
''',
                "files": [{"name": "main.py", "content": r'''
"""The Fourier series of a square wave, term by term."""

import numpy as np


def square_coeffs(N):
    """First N sine coefficients of a unit-amplitude square wave, b_1 .. b_N."""
    # TODO: b_n = 4 / (n * pi) for odd n, and 0 for even n.
    #       np.arange(1, N + 1) and np.where make this one expression.
    return np.zeros(N)


def synthesise(coeffs, t):
    """Sum of b_n sin(2 pi n t) over the given coefficients, evaluated at t."""
    # TODO: accumulate one harmonic at a time; coeffs[i] is b_(i+1).
    return np.zeros_like(np.asarray(t, dtype=float))


def mean_square(coeffs):
    """Mean square value of that sum, by Parseval: the sum of b_n^2 / 2."""
    # TODO: one sum, then a division by two. Return a float.
    return 0.0


if __name__ == "__main__":
    b = square_coeffs(9)
    print("b_1 .. b_9:", np.round(b, 6))
    t = np.linspace(0.0, 1.0, 9)
    print("nine harmonics over one period:", np.round(synthesise(b, t), 4))
    print("mean square with 9 harmonics:", mean_square(b))
    print("mean square with 99:", mean_square(square_coeffs(99)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The Fourier series of a square wave, term by term.

Numbers checked by running this file: b_1 = 1.2732395447351628 = 4/pi, the mean
square with 99 harmonics is 0.9959472877303109, and the partial sum with 99
harmonics peaks at 1.1790130793104294 near the jump — the Gibbs overshoot, about
9% of the jump height of 2.
"""

import numpy as np


def square_coeffs(N):
    """First N sine coefficients of a unit-amplitude square wave, b_1 .. b_N."""
    n = np.arange(1, N + 1)
    return np.where(n % 2 == 1, 4.0 / (n * np.pi), 0.0)


def synthesise(coeffs, t):
    """Sum of b_n sin(2 pi n t) over the given coefficients, evaluated at t."""
    t = np.asarray(t, dtype=float)
    out = np.zeros_like(t)
    for i, b in enumerate(coeffs):
        out = out + b * np.sin(2.0 * np.pi * (i + 1) * t)
    return out


def mean_square(coeffs):
    """Mean square value of that sum, by Parseval: the sum of b_n^2 / 2."""
    c = np.asarray(coeffs, dtype=float)
    return float(np.sum(c * c) / 2.0)


if __name__ == "__main__":
    b = square_coeffs(9)
    print("b_1 .. b_9:", np.round(b, 6))
    t = np.linspace(0.0, 1.0, 9)
    print("nine harmonics over one period:", np.round(synthesise(b, t), 4))
    print("mean square with 9 harmonics:", mean_square(b))
    print("mean square with 99:", mean_square(square_coeffs(99)))
'''}],
                "hints": [
                    "`np.arange(1, N + 1)` gives the harmonic numbers. `np.where(n % 2 == 1, 4.0 / (n * np.pi), 0.0)` then selects between the odd-harmonic value and zero without a loop.",
                    "In `synthesise`, `enumerate(coeffs)` gives `i` starting at 0, so the harmonic number is `i + 1`. Build the answer by adding one array to another; do not assign into `t`.",
                    "`mean_square` is `float(np.sum(c * c) / 2.0)`. If it comes out near 0.5 rather than near 1, the division by two has been applied twice.",
                    "To see Gibbs, evaluate `synthesise(square_coeffs(99), np.linspace(0, 0.5, 4001))` and take the maximum. It is close to 1.179, and it does not fall when you use more harmonics.",
                ],
                "tests": [
                    {"name": "the first five coefficients", "code": r'''
import numpy as np
b = square_coeffs(5)
assert len(b) == 5, f"asked for 5 coefficients, got {len(b)}"
want = [1.2732395447351628, 0.0, 0.4244131815783876, 0.0, 0.25464790894703254]
for k, (got, exp) in enumerate(zip(np.asarray(b, dtype=float), want), start=1):
    assert abs(got - exp) < 1e-12, f"b_{k} should be {exp}, got {got}"
'''},
                    {"name": "odd harmonics only, all the way up", "code": r'''
import numpy as np
b = np.asarray(square_coeffs(20), dtype=float)
for n in range(1, 21):
    if n % 2 == 0:
        assert abs(b[n - 1]) < 1e-15, f"b_{n} must be zero for an even harmonic, got {b[n - 1]}"
    else:
        assert abs(b[n - 1] - 4.0 / (n * np.pi)) < 1e-12, \
            f"b_{n} should be 4/({n}*pi), got {b[n - 1]}"
'''},
                    {"name": "one, three and five harmonics at the quarter period", "code": r'''
import numpy as np
t = np.array([0.25])
assert abs(float(synthesise(square_coeffs(1), t)[0]) - 1.2732395447351628) < 1e-9, \
    "one harmonic at t = 0.25 is just 4/pi"
assert abs(float(synthesise(square_coeffs(3), t)[0]) - 0.8488263631567752) < 1e-9, \
    "three harmonics give 4/pi (1 - 1/3)"
assert abs(float(synthesise(square_coeffs(5), t)[0]) - 1.1034742721038078) < 1e-9, \
    "five harmonics give 4/pi (1 - 1/3 + 1/5)"
'''},
                    {"name": "the Gibbs overshoot is there and does not go away", "code": r'''
import numpy as np
t = np.linspace(0.0, 0.5, 4001)
peak_99 = float(np.max(synthesise(square_coeffs(99), t)))
assert abs(peak_99 - 1.1790130793104294) < 1e-6, \
    f"99 harmonics should peak at about 1.17901, got {peak_99}"
peak_21 = float(np.max(synthesise(square_coeffs(21), t)))
assert peak_21 > 1.17, f"21 harmonics already overshoot to about 1.18, got {peak_21}"
assert abs(peak_99 - peak_21) < 0.01, \
    f"the overshoot must not shrink with more harmonics: {peak_21} then {peak_99}"
'''},
                    {"name": "Parseval: the power climbs towards 1", "code": r'''
p1 = mean_square(square_coeffs(1))
p9 = mean_square(square_coeffs(9))
p99 = mean_square(square_coeffs(99))
assert abs(p1 - 0.8105694691387023) < 1e-12, \
    f"the fundamental alone carries 8/pi^2 = 0.81057 of the power, got {p1}"
assert p1 < p9 < p99 < 1.0, f"partial sums must climb towards 1: {p1}, {p9}, {p99}"
assert abs(p99 - 0.9959472877303109) < 1e-12, \
    f"99 harmonics account for 0.99595 of the power, got {p99}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "The Fourier transform, sampling and Nyquist",
            "summary": "Let the period go to infinity and the lines become a continuum; then take samples, and the continuum starts repeating.",
            "concepts": [
                "Take a periodic signal and stretch its period. The harmonics at $n f_0$ crowd closer together as $f_0 = 1/T$ shrinks, and in the limit $T \\to \\infty$ — an aperiodic signal — the lines merge into a continuous function of frequency.",
                "That function is the **Fourier transform**: $X(f) = \\int_{-\\infty}^{\\infty} x(t)e^{-j2\\pi f t}\\,dt$, with the inverse $x(t) = \\int_{-\\infty}^{\\infty} X(f)e^{j2\\pi f t}\\,df$.",
                "$X(f)$ is complex: $|X(f)|$ is the magnitude spectrum and $\\angle X(f)$ the phase spectrum. For a real signal $X(-f) = X(f)^{*}$, so the magnitude is symmetric about zero and only positive frequencies are ever plotted.",
                "Compressing a signal in time stretches its spectrum in frequency, and vice versa: $x(at)$ transforms to $\\frac{1}{|a|}X(f/a)$. A short pulse is a wide spectrum; there is no such thing as a fast signal in a narrow band.",
                "The standard pair to memorise: a rectangular pulse of width $\\tau$ has transform $\\tau\\,\\mathrm{sinc}(f\\tau)$, whose first null sits at $f = 1/\\tau$. Halve the pulse width and the spectrum doubles in width.",
                "**Sampling** every $T_s$ seconds is, mathematically, multiplication by a train of impulses. That train has a spectrum which is itself a train of impulses spaced $f_s = 1/T_s$ apart, and multiplying in time convolves in frequency — so the signal's spectrum is **copied to every multiple of $f_s$**.",
                "If the signal contains anything above $f_s/2$, neighbouring copies overlap. The overlap is **aliasing**, and it is a permanent loss: after the samples exist there is no operation, analogue or digital, that can separate the two contributions.",
                "**Nyquist**: to represent a signal band-limited to $B$ you need $f_s > 2B$, strictly. At exactly $f_s = 2B$ the samples of a sinusoid at $B$ can all land on the zero crossings and record nothing at all.",
                "Where does a component land? A tone at $f$ appears in the sampled data at $f_a$, obtained by reducing $f$ modulo $f_s$ and then folding anything above $f_s/2$ back down: $f_a = f_s - (f \\bmod f_s)$ when that remainder exceeds $f_s/2$.",
                "The **anti-alias filter** therefore has to be analogue and has to come before the converter. Choosing it is a trade: a low corner protects the stopband but eats into the top of the wanted band, and a first-order filter usually cannot do both at once.",
                "Coming back out, the ideal reconstruction is a sum of sinc functions, one per sample. A real DAC holds each sample for $T_s$ instead, which multiplies the reconstructed spectrum by a $\\mathrm{sinc}(f/f_s)$ droop — about 3.9 dB down at the band edge if the band runs to $f_s/2$.",
            ],
            "sandbox": {
                "title": "What sampling does to a sine, and where the alias lands",
                "visualiser": "spectrum",
                "minutes": 10,
                "initial": {"fsig": 30, "fs": 200},
                "brief": r'''
Two panels, one signal. The **top** panel shows 100 ms of time: the faint grey curve is
the true continuous signal, the coloured dots are the samples taken at the chosen rate,
and — when the two disagree — an amber curve is drawn at the frequency the sampled data
will be read back as: the *other* sinusoid those same samples describe equally well.

Read the amber curve for its frequency rather than its sign. It is always drawn as
$\sin(2\pi f_a t)$, and folding a tone down through $f_s/2$ inverts the phase, so for a
folded tone the dots sit on the amber curve's mirror image rather than on the curve
itself. The frequency — which is the point — is right either way.

The **bottom** panel is the frequency axis, from 0 to 260 Hz. The dashed purple line
marks $f_s/2$, the Nyquist limit. The grey spike is the true signal frequency; the amber
spike, when it appears, is where the sampled data will claim the signal was.

Two sliders: the signal frequency, and the sample rate.
''',
                "notice": [
                    "It opens at 30 Hz sampled at 200 Hz, and there is no amber anywhere — neither a curve in the top panel nor a spike in the bottom one. The grey spike at 30 Hz sits well to the left of the dashed line at 100 Hz, and the dots, one every 5 ms, trace the grey curve without ambiguity.",
                    "Leave the rate at 200 Hz and drag the signal up to 230 Hz. The grey spike moves to the right of the dashed line, and an amber spike appears at 30 Hz: $230 - 200$, the remainder after reducing modulo the sample rate. In the top panel the amber curve is a slow 30 Hz wave, and every sample dot lies on it *and* on the fast grey curve at the same time. That is the whole of aliasing — the dots cannot tell you which curve they came from.",
                    "Now try 170 Hz, which reaches the same place by folding rather than by wrapping: $200 - 170$ is 30 again, and the amber spike does not move. The top panel does change, though. The dots now trace the amber curve *upside down*, because folding down through $f_s/2$ reverses the phase while the visualiser draws every alias with the same fixed phase. The frequency is what the picture is telling you; the sign is not.",
                    "Now set the signal to exactly 100 Hz, half the sample rate. Every dot sits on the zero line, because a sample every half period lands on a zero crossing each time; the grey curve is plainly not zero. The caption below still reports that nothing is lost, because it compares the folded frequency with the true one and here they agree — and the picture is the reason the sampling condition is written $f_s > 2B$ with a strict inequality rather than $f_s \\ge 2B$.",
                    "Put the signal back to 30 Hz and drag the sample rate down to 50 Hz. The dashed line moves left to 25 Hz, the 30 Hz spike is now to the right of it, and the alias appears at 20 Hz. Only six dots remain in the 100 ms window. Nothing about the signal changed: aliasing is a property of the pair, not of the signal alone.",
                ],
            },
            "quiz": {
                "title": "Spectra, sampling and where the tone went",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A rectangular pulse 1 ms wide is shortened to 0.25 ms. What happens to its spectrum?",
                        "opts": [
                            "it becomes four times narrower, with the first null moving from 1 kHz to 250 Hz",
                            "it becomes four times wider, with the first null moving from 1 kHz to 4 kHz",
                            "it is unchanged, because the pulse shape is the same",
                            "it shifts up by 3 kHz without changing shape",
                        ],
                        "a": 1,
                        "why": r'''
A pulse of width $\tau$ transforms to $\tau\,\mathrm{sinc}(f\tau)$, whose first null is at
$1/\tau$: 1 kHz becomes 4 kHz. Narrow in time is wide in frequency, always, and the
product of the two widths cannot be reduced below a fixed limit. This is why a fast
digital edge radiates over a huge span of frequencies, and why deliberately slowing
edges is the first thing tried when a board fails an emissions test.
''',
                    },
                    {
                        "q": "A 1.7 kHz sinusoid is sampled at 1 kSa/s. At what frequency will it appear in the sampled data?",
                        "opts": ["0.7 kHz", "1.7 kHz", "0.3 kHz", "0.5 kHz"],
                        "a": 2,
                        "why": r'''
Reduce modulo the sample rate: $1.7 \bmod 1 = 0.7$ kHz. That is above $f_s/2 = 0.5$ kHz,
so it folds: $1 - 0.7 = 0.3$ kHz. The answer 0.7 kHz is the common slip — stopping after
the modulo and forgetting the fold — and it is worth checking your arithmetic against the
rule that the result must always land between 0 and $f_s/2$. Nothing above 500 Hz can
appear in data sampled at 1 kSa/s, because there is nowhere for it to be.
''',
                    },
                    {
                        "q": "An anti-alias filter is placed after the ADC, in software, instead of before it. What does it achieve?",
                        "opts": [
                            "the same thing, provided the digital filter is sharper than the analogue one would have been",
                            "the same thing, but only if the sample rate is at least four times the bandwidth",
                            "nothing useful — the aliased content is already sitting on top of the signal and cannot be separated from it",
                            "it works, but adds a delay of one sample period",
                        ],
                        "a": 2,
                        "why": r'''
Nothing useful. Once the samples exist, the aliased component occupies exactly the same
frequency as genuine signal content at that frequency; no filter of any kind, however
sharp, can distinguish two things that are identical. This is the single most important
practical consequence in the module: the anti-alias filter is analogue, it comes first,
and it is one of the few parts of a signal chain where a mistake is unrecoverable rather
than merely inconvenient.
''',
                    },
                    {
                        "q": "A signal occupies DC to 4 kHz and must be sampled. Which statement is correct?",
                        "opts": [
                            "8 kSa/s is the theoretical minimum, and any real system uses a rate above it to leave room for a real filter",
                            "8 kSa/s is sufficient in principle and comfortable in practice",
                            "4 kSa/s suffices, because that matches the highest frequency present",
                            "16 kSa/s is the theoretical minimum, at four samples per cycle",
                        ],
                        "a": 0,
                        "why": r'''
The Nyquist rate is $2B = 8$ kSa/s, but it is a limit rather than a working choice: it
assumes a brick-wall filter with zero transition width, which does not exist. Real
designs sample at some multiple — 44.1 kSa/s for a 20 kHz audio band is the familiar
example, leaving over 2 kHz of transition band for the analogue filter to roll off in.
Calling 8 kSa/s *comfortable* is the textbook answer that forgets the filter has to
exist, and it is the reason so many first designs alias.
''',
                    },
                    {
                        "q": "Why does sampling copy the spectrum to every multiple of $f_s$?",
                        "opts": [
                            "because the sampler generates harmonics of its own clock, and each one carries a copy of the signal with it",
                            "because quantisation noise spreads evenly across every frequency the converter is able to represent",
                            "because the samples are discrete, and any discrete signal has a periodic spectrum by construction",
                            "because sampling multiplies by an impulse train, and multiplication in time is convolution in frequency",
                        ],
                        "a": 3,
                        "why": r'''
The mechanism is the one this course keeps returning to: multiplication in one domain is
convolution in the other. The impulse train's spectrum is another impulse train spaced
$f_s$ apart, and convolving a spectrum with an impulse at $kf_s$ simply moves a copy
there. "Any discrete signal has a periodic spectrum by construction" states a true fact —
the spectrum of a sampled signal is periodic — but offers it as its own explanation. Note that none of this involves quantisation: aliasing
happens even with a converter of infinite resolution.
''',
                    },
                    {
                        "q": "A converter samples at 20 kSa/s. Interference at 19 kHz reaches its input. Where does it end up?",
                        "opts": ["at 19 kHz, harmlessly outside the band", "at 1 kHz, in the middle of the wanted band", "at 10 kHz, exactly on the Nyquist line", "it is rejected automatically, because it is above $f_s/2$"],
                        "a": 1,
                        "why": r'''
$19 \bmod 20 = 19$ kHz, which exceeds $f_s/2 = 10$ kHz, so it folds to $20 - 19 = 1$ kHz
and lands squarely in the wanted band. Nothing is rejected automatically — that is the belief behind "rejected automatically, because it is above $f_s/2$", and
it is exactly backwards: frequencies above $f_s/2$ are not
discarded by the sampler, they are *relocated* by it. Interference close to a multiple of
the sample rate is the worst case, because it folds to a low frequency where the wanted
signal usually lives.
''',
                    },
                ],
            },
            "build": {
                "title": "The filter that has to come first",
                "minutes": 25,
                "brief": r'''
A converter on your board samples at **20 kSa/s**. The signal you care about occupies
**DC to 2 kHz**. Everything from 10 kHz upwards — $f_s/2$ and above — will fold down
into the sampled band and cannot be removed afterwards, so it has to be attenuated
*before* the converter.

Design the analogue filter that goes there. Drive it from the 1 V source on the canvas,
put the probe on its output, and meet both of these:

1. **Keep the band.** At 2 kHz the output must be at least $1/\sqrt{2}$ of its
   low-frequency value — no more than 3 dB of loss at the top of the wanted band.
2. **Kill what folds.** At 10 kHz the output must be down to **a third** of its
   low-frequency value or less, and it must keep falling above that.

The filter must also pass low frequencies essentially untouched: a network that
attenuates everything equally satisfies neither requirement in spirit and fails the
first check.

## Working out the window

For a single-pole low-pass with corner $f_c$, the amplitude ratio is
$1/\sqrt{1 + (f/f_c)^2}$. Requirement 1 puts a **lower** bound on $f_c$ and requirement 2
puts an **upper** one. Write both out before drawing anything; the design is any $f_c$
inside the window, and $f_c = 2.5$ kHz sits comfortably in the middle.

It is worth noticing how narrow that window is. Ask for a factor of ten at 10 kHz
instead of a factor of three and the two bounds cross — no single-pole filter can do it,
whatever values you choose. That is what module 4's second pole is for.

## Drawing it

Place parts from the toolbar and wire them with two clicks. Values accept `10n`, `6.4k`
and `1e-8` alike. The checks measure the response; any pair of values that meets both
requirements passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 5, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 6366},
                        {"id": "p3", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 4], "b": [11, 4]},
                    ],
                },
                "checks": [
                    {"name": "the wanted band arrives at the probe essentially untouched", "code": r'''
c.assert(c.count('V') === 1, 'Drive the filter from exactly one source; found ' + c.count('V') + '.');
const vs = c.values('V')[0];
const dc = c.gain(10);
c.assert(dc > 0.98 * vs,
  'At 10 Hz the probe sees ' + (dc / vs * 100).toFixed(1) + '% of the source voltage. ' +
  'An anti-alias filter must pass the wanted band, not divide it down.');
'''},
                    {"name": "at 2 kHz the loss is no more than 3 dB", "code": r'''
const ref = c.gain(10);
const r = c.gain(2000) / ref;
c.assert(r >= 0.70,
  'At 2 kHz the output is ' + (r * 100).toFixed(1) + '% of its low-frequency value; the ' +
  'top of the wanted band may lose no more than 3 dB, so this needs at least 70.7%. ' +
  'Your corner frequency is too low.');
'''},
                    {"name": "at 10 kHz what would fold is down to a third", "code": r'''
const ref = c.gain(10);
const r = c.gain(10000) / ref;
c.assert(r <= 0.34,
  'At 10 kHz the output is still ' + (r * 100).toFixed(1) + '% of its low-frequency ' +
  'value, and everything there folds into the sampled band. It must be 33% or less, ' +
  'so this corner frequency is too high.');
'''},
                    {"name": "and it goes on falling above the Nyquist frequency", "code": r'''
const ref = c.gain(10);
const a = c.gain(10000) / ref;
const b = c.gain(100000) / ref;
c.assert(b < a, 'The response must keep falling above 10 kHz, not level off or rise: ' +
  (a * 100).toFixed(1) + '% at 10 kHz against ' + (b * 100).toFixed(1) + '% at 100 kHz.');
c.assert(b < 0.05, 'A decade above the Nyquist frequency the response should be well ' +
  'under 5% of the passband; measured ' + (b * 100).toFixed(2) + '%.');
'''},
                ],
                "hints": [
                    "Requirement 1: $1/\\sqrt{1 + (2000/f_c)^2} \\ge 1/\\sqrt{2}$ gives $f_c \\ge 2$ kHz.",
                    "Requirement 2: $1/\\sqrt{1 + (10000/f_c)^2} \\le 1/3$ gives $1 + (10000/f_c)^2 \\ge 9$, so $f_c \\le 10000/\\sqrt{8} \\approx 3.54$ kHz.",
                    "Pick $f_c = 2.5$ kHz, choose a round capacitor — 10 nF — and let $R = 1/(2\\pi f_c C)$ decide the resistor. That comes to about 6.37 kΩ.",
                    "The resistor goes in series from the source, the capacitor from the output node down to ground, and the probe sits on the node between them. Without a ground symbol nothing can be measured at all.",
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "The transfer function: convolution becomes multiplication",
            "summary": "Send a complex exponential into an LTI system and it comes back scaled. That one fact turns the hardest operation in module 1 into a product.",
            "concepts": [
                "Feed $e^{j\\omega t}$ into an LTI system and the output is $H(j\\omega)\\,e^{j\\omega t}$ — the same function, scaled by a complex number. Complex exponentials are the **eigenfunctions** of every LTI system, and no other family of signals has this property.",
                "That scale factor is the **transfer function**, and substituting into the convolution integral identifies it: $H(j\\omega) = \\int h(\\tau)e^{-j\\omega\\tau}\\,d\\tau$, the Fourier transform of the impulse response.",
                "Hence the **convolution theorem**: $y = h * x$ in time becomes $Y(j\\omega) = H(j\\omega)X(j\\omega)$ in frequency. The awkward operation of module 1 becomes a multiplication, one frequency at a time, and this is the reason engineers work in the frequency domain at all.",
                "$|H|$ scales each component and $\\angle H$ shifts it. Watch the sign: a **lag**, $\\angle H = -\\phi$, is a *delay* of $\\phi/\\omega$ seconds, so the delay is $-\\angle H/\\omega$. A system whose phase falls linearly with frequency therefore delays every component by the same time and does not distort the waveform; one whose phase bends does.",
                "For a circuit, $H(j\\omega)$ needs no new theory at all — it is the impedance divider from EE102 with $Z_R = R$, $Z_C = 1/(j\\omega C)$ and $Z_L = j\\omega L$.",
                "The RC low-pass has $H = \\frac{1}{1 + j\\omega RC}$: one pole, a corner at $\\omega = 1/RC$, a magnitude falling at 20 dB per decade beyond it, and exactly $-45^\\circ$ of phase at the corner.",
                "A series RLC with the output across the capacitor has $H = \\frac{1}{1 - \\omega^2 LC + j\\omega RC}$: two poles, a magnitude falling at 40 dB per decade, and $-90^\\circ$ at $\\omega_n$. Written in standard form the two parameters are $\\omega_n = 1/\\sqrt{LC}$ and $\\zeta = \\frac{R}{2}\\sqrt{C/L}$.",
                "$\\zeta$ decides the shape. Below about 0.707 the magnitude peaks before falling; at $\\zeta = 1/\\sqrt{2}$ the response is as flat as a two-pole filter can be and the $-3$ dB point coincides with $\\omega_n$; above that the corner softens and moves down.",
                "A **Bode plot** uses decibels against log frequency, which turns products into sums: cascade two systems and their dB curves add, as do their phase curves. That is the whole reason for the logarithmic axes.",
                "A periodic input passes through line by line: harmonic $n$ comes out multiplied by $H(jn\\omega_0)$. A square wave through a low-pass filter loses its high harmonics first, which is why it comes out with rounded corners — the same statement as module 2's remark that edges cost bandwidth.",
            ],
            "sandbox": {
                "title": "Reading a second-order transfer function off its Bode plot",
                "visualiser": "bode",
                "minutes": 10,
                "initial": {"wn": 20, "zeta": 0.7, "K": 1},
                "brief": r'''
The system on display is $H(j\omega) = \dfrac{K}{1 - (\omega/\omega_n)^2 + j2\zeta(\omega/\omega_n)}$
— the standard second-order low-pass, and the transfer function of the series RLC you are
about to design.

The **top** panel is $20\log_{10}|H|$ in decibels against $\omega$ on a logarithmic axis
from 0.1 to 2000 rad/s; the dashed line marks 0 dB and the amber dot marks the response
exactly at $\omega = \omega_n$. The **bottom** panel is the phase in degrees, with its
dashed line at $-90^\circ$.

Three sliders: the corner $\omega_n$, the damping $\zeta$, and the gain $K$.
''',
                "notice": [
                    "It opens at $\\omega_n = 20$, $\\zeta = 0.7$, $K = 1$. The magnitude is flat at 0 dB across the left of the plot, and the amber dot sits about 2.9 dB below that flat line — $20\\log_{10}(1/1.4)$, which is as near the $-3$ dB point as makes no difference. At this damping the corner and the half-power frequency are the same thing.",
                    "Drag $\\zeta$ down to 0.1. A peak grows just before the corner and the amber dot climbs to about $+14$ dB, since it tracks $20\\log_{10}(K/2\\zeta)$. The caption reports the true peak, marginally higher again, because the maximum sits a little below $\\omega_n$ rather than exactly on it. Take $\\zeta$ up to 1.5 instead and the peak is gone, the dot drops to $-9.5$ dB, and the curve rounds off long before the corner.",
                    "Whatever you do to $\\zeta$, the phase curve crosses its dashed $-90^\\circ$ line at exactly $\\omega = \\omega_n$. That is worth trusting: the magnitude corner moves with damping, the phase crossing does not, which makes it the reliable way to read $\\omega_n$ off a measurement.",
                    "Now move $K$ from 1 to 10. The whole magnitude curve lifts by 20 dB and its shape is untouched — and the phase panel does not move at all. Gain and dynamics are independent; $K$ is what a divider or an amplifier in front of the filter would change.",
                    "Put $K$ back to 1 and $\\zeta$ back to 0.7, then read the slope past the corner. At $\\omega = 200$, ten times $\\omega_n$, the magnitude is $-40$ dB; at $\\omega = 2000$, the right-hand edge, it has reached $-80$ dB, which is the bottom of the frame. Forty decibels per decade, twice the slope of the single-pole filter from EE102, because there are two poles rather than one. Leave $K$ at 10 by mistake and both readings are 20 dB higher — the slope is the same, which is the point of the previous paragraph.",
                ],
            },
            "quiz": {
                "title": "Transfer functions, and what they replace",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Why is $e^{j\\omega t}$ singled out as the signal to test an LTI system with?",
                        "opts": [
                            "because it is the only signal for which the convolution integral converges",
                            "because it comes out of an LTI system unchanged except for a complex scale factor, so the system's whole effect is one number per frequency",
                            "because real circuits are driven by sinusoids in practice",
                            "because its Fourier transform is the simplest to compute",
                        ],
                        "a": 1,
                        "why": r'''
It is an eigenfunction: in goes $e^{j\omega t}$, out comes $H(j\omega)e^{j\omega t}$, the
same shape at the same frequency. No other family of inputs behaves this way, and it is
what reduces a convolution to a multiplication. "Real circuits are driven by sinusoids in practice" is true and beside the point:
sinusoids are convenient in the laboratory, but the mathematical privilege belongs to the
complex exponential, of which a sinusoid is a sum of two.
''',
                    },
                    {
                        "q": "A signal with spectrum $X$ is fed through a system with impulse response $h$. Which pair of statements is correct?",
                        "opts": [
                            "$y = h * x$ in time, and $Y = H * X$ in frequency",
                            "$y = hx$ in time, and $Y = HX$ in frequency",
                            "$y = h * x$ in time, and $Y = HX$ in frequency",
                            "$y = hx$ in time, and $Y = H * X$ in frequency",
                        ],
                        "a": 2,
                        "why": r'''
Convolution in one domain is multiplication in the other, and the direction matters:
filtering convolves in time and multiplies in frequency. The pairing runs the other way
too, and module 3 used it — sampling *multiplies* in time by an impulse train, which
*convolves* the spectrum with an impulse train and so copies it. One theorem, two
readings.
''',
                    },
                    {
                        "q": "An RC low-pass has a corner at 1 kHz. What is the phase of its output at 1 kHz, and what is its magnitude a decade above?",
                        "opts": [
                            "$-90^\\circ$, and a tenth",
                            "$-45^\\circ$, and a tenth",
                            "$-45^\\circ$, and a hundredth",
                            "$-45^\\circ$, and a half",
                        ],
                        "a": 1,
                        "why": r'''
At the corner of a single pole, $\omega RC = 1$, so $H = 1/(1 + j)$: magnitude
$1/\sqrt{2}$ and phase $-45^\circ$. A decade past the corner the $j\omega RC$ term
dominates and the magnitude is one tenth — 20 dB per decade, one pole. The answer
$-90^\circ$ belongs to a *second*-order filter at its corner, or to a first-order one far
above it, where the phase asymptotes to $-90^\circ$ without ever quite arriving.
''',
                    },
                    {
                        "q": "A series RLC low-pass is built with $\\zeta = 0.3$. What does its magnitude response look like?",
                        "opts": [
                            "flat, then falling at 20 dB per decade",
                            "flat all the way, because $\\zeta$ only affects phase",
                            "monotonically falling with a soft corner well below $\\omega_n$",
                            "flat, then peaking above the low-frequency level near $\\omega_n$, then falling at 40 dB per decade",
                        ],
                        "a": 3,
                        "why": r'''
Any $\zeta$ below $1/\sqrt{2} \approx 0.707$ gives a peak, and at $\zeta = 0.3$ it is
about $1/(2\zeta\sqrt{1-\zeta^2}) = 1.75$, or $+4.9$ dB above the flat region. Beyond it
the two poles give 40 dB per decade. A monotonic fall with a soft corner describes the *over*damped case, $\zeta > 1$
— the two errors are mirror images, and the sandbox is the fastest way to stop confusing
them.
''',
                    },
                    {
                        "q": "A 1 kHz square wave is passed through a low-pass filter with a corner at 1.5 kHz. What comes out?",
                        "opts": [
                            "a square wave of reduced amplitude but the same shape",
                            "a rounded waveform: the fundamental survives nearly intact while the third, fifth and higher harmonics are progressively attenuated",
                            "nothing, since a square wave contains no 1 kHz component",
                            "a triangle wave, because the filter integrates",
                        ],
                        "a": 1,
                        "why": r'''
The filter multiplies the line spectrum harmonic by harmonic. The 1 kHz fundamental sits
below the corner and gets through; the third harmonic at 3 kHz is already a factor of
$1/\sqrt{1+4} = 0.45$ down, the fifth more so, and it is those harmonics that build the
sharp corners. Losing them rounds the edges. Note what the filter cannot do: it never
introduces a frequency the input did not contain, which is the defining privilege of a
linear system.
''',
                    },
                    {
                        "q": "Two filters are cascaded, the second not loading the first. On a Bode plot, how do their responses combine?",
                        "opts": [
                            "the decibel curves add, and so do the phase curves",
                            "the decibel curves multiply",
                            "the decibel curves add, but the phases must be combined as a vector sum",
                            "only the lower of the two corner frequencies has any effect",
                        ],
                        "a": 0,
                        "why": r'''
Cascading multiplies the transfer functions, $H = H_1H_2$; taking the logarithm turns
that product into a sum of decibels, and the argument of a product is the sum of the
arguments, so the phases add too. This is the entire justification for the logarithmic
axes: it lets a designer sketch a complicated response by adding simple pieces. The
caveat is in the question — "not loading the first" — because a second stage that draws
current changes the first stage's response, and then $H \ne H_1H_2$.
''',
                    },
                ],
            },
            "derive": {
                "title": "Where $\\omega_n$ and $\\zeta$ come from",
                "minutes": 14,
                "vars": ["omega", "L", "C", "R", "j", "omega_n", "zeta", "H"],
                "brief": r'''
A resistor, an inductor and a capacitor in series across a source, with the output taken
across the capacitor. This is the circuit you are about to build, and the aim is to get
from three component values to the two numbers — $\omega_n$ and $\zeta$ — that the Bode
plot is drawn from.

No new theory is needed. It is the impedance divider from EE102, written out and tidied.
''',
                "steps": [
                    {
                        "prompt": "Write the impedance of the capacitor at angular frequency $\\omega$.",
                        "answer": "\\frac{1}{j\\omega C}",
                        "hint": "The current through a capacitor is $C\\,dv/dt$, and differentiating $e^{j\\omega t}$ multiplies by $j\\omega$.",
                        "deconstruct": [
                            "$i = C\\frac{dv}{dt}$ becomes $I = j\\omega C V$ for a complex exponential.",
                            "Impedance is $V/I$, so it is the reciprocal of $j\\omega C$.",
                        ],
                    },
                    {
                        "prompt": "The three parts carry the same current, so this is an impedance divider. Write $H = V_{out}/V_{in}$ as the capacitor's impedance over the total, without simplifying.",
                        "given": "The three impedances are $R$, $j\\omega L$ and the one you just wrote.",
                        "answer": "\\frac{\\frac{1}{j\\omega C}}{R + j\\omega L + \\frac{1}{j\\omega C}}",
                        "hint": "Exactly the resistive divider of EE101 with impedances in place of resistances: the part you measure across goes on top, the whole series chain underneath.",
                        "deconstruct": [
                            "In a series chain the same current flows, so voltages split in proportion to impedance.",
                            "The output is across the capacitor, so its impedance is the numerator.",
                        ],
                    },
                    {
                        "prompt": "Multiply top and bottom by $j\\omega C$ and write the tidied $H$.",
                        "answer": "\\frac{1}{1 - \\omega^{2} L C + j \\omega R C}",
                        "hint": "The numerator becomes 1. In the denominator, $j\\omega L \\cdot j\\omega C = j^2\\omega^2 LC = -\\omega^2 LC$.",
                        "deconstruct": [
                            "$\\frac{1}{j\\omega C}\\cdot j\\omega C = 1$, which clears the fraction on top.",
                            "$R\\cdot j\\omega C = j\\omega RC$, and $j\\omega L\\cdot j\\omega C = -\\omega^2 LC$ because $j^2 = -1$.",
                        ],
                    },
                    {
                        "prompt": "The standard form is $H = \\dfrac{1}{1 - (\\omega/\\omega_n)^2 + j2\\zeta(\\omega/\\omega_n)}$. Matching the $\\omega^2$ terms, write $\\omega_n$ in terms of $L$ and $C$.",
                        "answer": "\\frac{1}{\\sqrt{L C}}",
                        "hint": "You need $\\omega^2/\\omega_n^2 = \\omega^2 LC$, so $\\omega_n^2 = 1/(LC)$.",
                        "deconstruct": [
                            "Compare $(\\omega/\\omega_n)^2$ with $\\omega^2 LC$: they must be equal for all $\\omega$.",
                            "So $1/\\omega_n^2 = LC$, and take the positive square root.",
                        ],
                    },
                    {
                        "prompt": "Now match the imaginary terms and write $\\zeta$ in terms of $R$, $L$ and $C$.",
                        "given": "You need $2\\zeta\\,\\omega/\\omega_n = \\omega R C$, with $\\omega_n = 1/\\sqrt{LC}$.",
                        "answer": "\\frac{R}{2}\\sqrt{\\frac{C}{L}}",
                        "hint": "The $\\omega$ cancels, leaving $2\\zeta = RC\\omega_n = RC/\\sqrt{LC}$. Simplify $C/\\sqrt{LC}$.",
                        "deconstruct": [
                            "Divide both sides by $\\omega$: $2\\zeta/\\omega_n = RC$, so $2\\zeta = RC\\omega_n$.",
                            "Substitute $\\omega_n = 1/\\sqrt{LC}$: $2\\zeta = RC/\\sqrt{LC} = R\\sqrt{C/L}$.",
                        ],
                    },
                ],
                "closing": r'''
Two component-value formulas, and every feature of the Bode plot follows from them.
Notice that $\zeta$ depends on $R$ but $\omega_n$ does not: you can move the corner with
$L$ and $C$ and then set the damping with the resistor alone, without disturbing it.

For the maximally flat design, $\zeta = 1/\sqrt{2}$ gives $R = \sqrt{2L/C}$ — a number
you will now type into the schematic editor.
''',
            },
            "build": {
                "title": "Two poles, and the decade that pays for them",
                "minutes": 30,
                "brief": r'''
The single-pole filter of module 3 could not reach a factor of ten at ten times the band
edge. This one can reach a factor of a hundred, because it has two poles.

Build a **series RLC low-pass** — resistor and inductor in series from the source, output
taken across a capacitor to ground — with the following measured behaviour. A 1 µF
capacitor and a ground are already on the canvas; connect the source to it through the
two parts that are missing, and put the probe on the output node. You may change the
capacitor if you prefer; only the measurements count.

1. **Unity at DC.** At 1 Hz the output must be within 2% of the input.
2. **Corner at 1 kHz.** The frequency at which the output falls to $1/\sqrt{2}$ of its
   low-frequency value must be 1 kHz, within 5%.
3. **Flat below it.** Nowhere between 10 Hz and 900 Hz may the response rise more than
   2% above its low-frequency value. No resonant peak.
4. **Forty decibels per decade.** At 10 kHz the output must be about **one hundredth** of
   its low-frequency value, within 25%.
5. **Ninety degrees at the corner.** The output must lag the input by $90^\circ$ at
   1 kHz, within about six degrees.

## What the requirements are really saying

The derivation gives $\omega_n = 1/\sqrt{LC}$ and $\zeta = \frac{R}{2}\sqrt{C/L}$.
Requirement 5 pins $\omega_n$, because the phase passes through $-90^\circ$ at
$\omega = \omega_n$ for **any** damping. Requirement 2 then says the $-3$ dB point sits at
$\omega_n$ as well, and that happens at exactly one value of $\zeta$. Requirements 3 and 4
are the same statement seen from two other directions, and a design that satisfies 2 and 5
will satisfy them.

So: choose $L$ from $\omega_n = 2\pi \times 1000$ and the capacitor you are using, then
choose $R$ from the damping. Round numbers are not expected — type what the algebra gives.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p4", "kind": "OUT", "x": 15, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p4", "kind": "OUT", "x": 15, "y": 4},
                        {"id": "p5", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 225.0790790392765},
                        {"id": "p6", "kind": "L", "x": 10, "y": 4, "rot": 0, "value": 0.025330295910584444},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [11, 4], "b": [13, 4]},
                    ],
                },
                "checks": [
                    {"name": "one source, and the output follows it at DC", "code": r'''
c.assert(c.count('V') === 1, 'Drive the filter from exactly one source; found ' + c.count('V') + '.');
const vs = c.values('V')[0];
const dc = c.gain(1);
c.close(dc, vs, 0.02,
  'the output at 1 Hz — at low frequency the inductor is a short and the capacitor an ' +
  'open, so the whole input should appear at the probe');
'''},
                    {"name": "the corner is at 1 kHz", "code": r'''
c.close(c.corner(10, 1e6), 1000, 0.05,
  'the frequency where the output falls to 1/sqrt(2) of its low-frequency value');
'''},
                    {"name": "the passband is flat — no resonant peak", "code": r'''
const ref = c.gain(10);
const vs = c.values('V')[0];
c.assert(ref > 0.5 * vs,
  'At 10 Hz the probe reads ' + (ref / vs * 100).toFixed(1) + '% of the source voltage. ' +
  'Almost nothing is reaching the output node, so there is no passband to measure — ' +
  'check that the source is wired through to it.');
let worst = 0, at = 0;
for (let i = 0; i <= 30; i++) {
  const f = Math.pow(10, 1 + i / 30 * Math.log10(90));
  const r = c.gain(f) / ref;
  if (r > worst) { worst = r; at = f; }
}
c.assert(worst <= 1.02,
  'The response peaks to ' + worst.toFixed(3) + ' times its low-frequency value near ' +
  at.toFixed(0) + ' Hz. That is a resonance: the damping is too low, so the resistor is ' +
  'too small.');
'''},
                    {"name": "two poles: a hundredfold cut a decade past the corner", "code": r'''
const ref = c.gain(10);
const r = c.gain(10000) / ref;
c.close(r, 0.01, 0.25,
  'the response at 10 kHz relative to the passband — two poles give 40 dB per decade, ' +
  'so ten times past a 1 kHz corner should be about one hundredth');
'''},
                    {"name": "the output lags by 90 degrees at the corner", "code": r'''
c.close(c.phase(1000), -90, 0.07,
  'the phase at 1 kHz — it passes through -90 degrees exactly at omega_n, so this ' +
  'measures whether your natural frequency is where you meant it to be');
'''},
                ],
                "hints": [
                    "$\\omega_n = 2\\pi \\times 1000 = 6283.2$ rad/s. With $C = 1$ µF, $L = 1/(\\omega_n^2 C)$, which comes to about 25.3 mH.",
                    "Requirements 2 and 3 together mean the maximally flat case, $\\zeta = 1/\\sqrt{2}$. From the derivation, $R = 2\\zeta\\sqrt{L/C} = \\sqrt{2L/C}$.",
                    "With $L = 25.33$ mH and $C = 1$ µF that gives $R \\approx 225$ Ω. Type `25.33m` for the inductor and `225` for the resistor.",
                    "If the passband check reports a peak, the resistance is too low — damping rises with $R$. If the corner is in the wrong place, it is $L$ or $C$ that needs changing, not $R$.",
                    "Order does not matter: resistor then inductor, or inductor then resistor, gives the same series impedance. What does matter is that the output is taken across the capacitor and the probe sits on that node.",
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A spectrum analyser, and the convolution theorem measured on its output",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Build the instrument this course has been describing, then use it to check the course's
central claim on data it produced itself.

Five functions, each small. Together they take a list of samples and tell you what
frequencies are in it, predict where an out-of-band tone will land, and demonstrate that
convolving two signals in time multiplies their spectra.

- `dft(x)` — the discrete Fourier transform from the definition,
  $X[k] = \sum_{n=0}^{N-1} x[n]\,e^{-j2\pi kn/N}$, returned as a list of `complex` of the
  same length as `x`. Write the sum out; the point is to know what the answer means.
- `amplitude_spectrum(x, fs)` — return `(freqs, amps)`, the single-sided spectrum.
  `freqs[k]` is $k f_s/N$ for $k = 0 \dots N/2$, and `amps[k]` is scaled so that a
  sinusoid of amplitude $A$ reads $A$: divide $|X[k]|$ by $N$, then double every bin
  except DC and, when $N$ is even, the one at $f_s/2$.
- `alias_of(f, fs)` — the frequency a tone at `f` will appear at after sampling at `fs`:
  reduce modulo `fs`, then fold anything above `fs/2` back down.
- `convolve(x, h)` — as in module 1, returning `len(x) + len(h) - 1` samples.
- `response_at(h, f, fs)` — the transfer function of an FIR filter with impulse response
  `h`, evaluated at frequency `f`, as a `complex`:
  $H = \sum_n h[n]\,e^{-j2\pi f n/f_s}$.

The last two are what make the demonstration possible: filter a sinusoid by convolution,
measure the amplitude of the result with your own analyser, and compare it with
$|H|$ computed directly. If the convolution theorem is true they agree to the last digit
your arithmetic can carry.

`cmath.exp` handles complex exponentials; `numpy` is available and useful for generating
test signals, but `numpy.fft` is not the exercise.
''',
        "deliverables": [
            "`dft` computing the transform from its definition, agreeing with hand-worked four-point cases.",
            "`amplitude_spectrum` returning frequencies in hertz and amplitudes scaled so a 3 V sinusoid reads 3 V.",
            "`alias_of` predicting the observed frequency of any tone, in band or out of it, including the folding above $f_s/2$.",
            "`convolve` and `response_at`, and a demonstration in `__main__` that filtering by convolution and multiplying spectra give the same answer.",
        ],
        "constraints": [
            "NumPy and the standard library only. `numpy.fft` defeats the purpose of the first deliverable, so write the sum yourself.",
            "`dft` must return a sequence of `complex` of the same length as its input, not magnitudes.",
            "Amplitudes are single-sided and scaled to volts: a 3 V sinusoid in the middle of the band must read 3.0, not 1.5 and not $3N/2$.",
            "`alias_of` must return a value between 0 and `fs/2` for every input, including frequencies well above the sample rate.",
        ],
        "rubric": [
            {"criterion": "The transform is the definition, not a library call",
             "weight": 25,
             "evidence": "`dft` implements the sum over n of x[n] exp(-2 pi j k n / N) and reproduces the four-point cases [1,2,3,4] -> [10, -2+2j, -2, -2-2j] and delta -> all ones."},
            {"criterion": "The spectrum is scaled and labelled correctly",
             "weight": 25,
             "evidence": "`amplitude_spectrum` returns frequencies in hertz with spacing fs/N, and a two-tone test signal of 3 V at 50 Hz and 1 V at 120 Hz reads 3.0 and 1.0 in the right bins with nothing elsewhere."},
            {"criterion": "Aliasing is predicted before it is measured",
             "weight": 20,
             "evidence": "`alias_of` folds correctly for tones below, at and far above the Nyquist frequency, and its prediction for a 1.7 kHz tone sampled at 1 kSa/s matches the peak the analyser actually finds."},
            {"criterion": "The convolution theorem is demonstrated, not asserted",
             "weight": 30,
             "evidence": "The DFT of a convolution equals the product of the zero-padded DFTs to numerical precision, and the amplitude the analyser measures at the output of an FIR filter matches |response_at| at that frequency."},
        ],
        "files": [
            {"name": "main.py", "content": r'''
"""A spectrum analyser, written from the definitions.

Fill in the five functions. Every one of them is a few lines; the difficulty is
entirely in getting the indices and the scaling right.
"""

import cmath
import math

import numpy as np


def dft(x):
    """Discrete Fourier transform: X[k] = sum_n x[n] exp(-2 pi j k n / N).

    Returns a list of `complex`, the same length as `x`.
    """
    # TODO: two loops, or one loop over k with a sum inside.
    return []


def amplitude_spectrum(x, fs):
    """Single-sided amplitude spectrum of `x` sampled at `fs`.

    Returns (freqs, amps) where freqs[k] = k * fs / N for k = 0 .. N // 2, and
    amps[k] is scaled so a sinusoid of amplitude A reads A.
    """
    # TODO: call dft, keep the first N // 2 + 1 bins, divide by N, and double
    #       every bin except DC and (for even N) the one at fs / 2.
    return [], []


def alias_of(f, fs):
    """The frequency a tone at `f` appears at once sampled at `fs`."""
    # TODO: reduce modulo fs, then fold anything above fs / 2 back down.
    return 0.0


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`."""
    # TODO: as in module 1 — len(x) + len(h) - 1 samples.
    return []


def response_at(h, f, fs):
    """Transfer function of the FIR filter `h` at frequency `f`, as a complex."""
    # TODO: sum h[n] * cmath.exp(-2j * pi * f * n / fs) over n.
    return 0j


if __name__ == "__main__":
    fs = 1000.0
    n = np.arange(200)

    x = list(3.0 * np.sin(2 * np.pi * 50 * n / fs) + np.cos(2 * np.pi * 120 * n / fs))
    freqs, amps = amplitude_spectrum(x, fs)
    if amps:
        peaks = [(f, a) for f, a in zip(freqs, amps) if a > 0.1]
        print("peaks found:", [(round(f, 1), round(a, 3)) for f, a in peaks])

    print("1.7 kHz sampled at 1 kSa/s should appear at", alias_of(1700.0, fs), "Hz")

    h = [0.25] * 4
    y = convolve(list(np.cos(2 * np.pi * 100 * n / fs)), h)
    print("moving average at 100 Hz:", abs(response_at(h, 100.0, fs)))
'''}
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A spectrum analyser, written from the definitions.

Every number quoted below came out of running this file.

    dft([1, 2, 3, 4])                 -> [10, -2+2j, -2, -2-2j]
    two tones, 3 V at 50 Hz and 1 V at 120 Hz, 200 samples at 1 kSa/s
                                      -> 3.000 in bin 10, 1.000 in bin 24,
                                         nothing above 1.3e-14 anywhere else
    alias_of(1700, 1000)              -> 300.0, and the analyser finds its peak there
    a 4-point moving average at 100 Hz -> |H| = 0.7694208842938134, and the measured
                                         amplitude of the filtered sinusoid agrees to
                                         within 1e-12
"""

import cmath
import math

import numpy as np


def dft(x):
    """Discrete Fourier transform: X[k] = sum_n x[n] exp(-2 pi j k n / N).

    Returns a list of `complex`, the same length as `x`.
    """
    N = len(x)
    out = []
    for k in range(N):
        total = 0j
        for n, xn in enumerate(x):
            total += xn * cmath.exp(-2j * math.pi * k * n / N)
        out.append(total)
    return out


def amplitude_spectrum(x, fs):
    """Single-sided amplitude spectrum of `x` sampled at `fs`.

    Returns (freqs, amps) where freqs[k] = k * fs / N for k = 0 .. N // 2, and
    amps[k] is scaled so a sinusoid of amplitude A reads A.
    """
    N = len(x)
    X = dft(x)
    half = N // 2
    freqs = [k * fs / N for k in range(half + 1)]
    amps = []
    for k in range(half + 1):
        m = abs(X[k]) / N
        at_nyquist = (N % 2 == 0) and (k == half)
        if k != 0 and not at_nyquist:
            m *= 2.0
        amps.append(m)
    return freqs, amps


def alias_of(f, fs):
    """The frequency a tone at `f` appears at once sampled at `fs`."""
    fa = f % fs
    if fa > fs / 2.0:
        fa = fs - fa
    return fa


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`."""
    y = [0.0] * (len(x) + len(h) - 1)
    for i, xv in enumerate(x):
        for j, hv in enumerate(h):
            y[i + j] += xv * hv
    return y


def response_at(h, f, fs):
    """Transfer function of the FIR filter `h` at frequency `f`, as a complex."""
    total = 0j
    for n, hn in enumerate(h):
        total += hn * cmath.exp(-2j * math.pi * f * n / fs)
    return total


if __name__ == "__main__":
    fs = 1000.0
    n = np.arange(200)

    x = list(3.0 * np.sin(2 * np.pi * 50 * n / fs) + np.cos(2 * np.pi * 120 * n / fs))
    freqs, amps = amplitude_spectrum(x, fs)
    if amps:
        peaks = [(f, a) for f, a in zip(freqs, amps) if a > 0.1]
        print("peaks found:", [(round(f, 1), round(a, 3)) for f, a in peaks])

    print("1.7 kHz sampled at 1 kSa/s should appear at", alias_of(1700.0, fs), "Hz")

    h = [0.25] * 4
    y = convolve(list(np.cos(2 * np.pi * 100 * n / fs)), h)
    print("moving average at 100 Hz:", abs(response_at(h, 100.0, fs)))
'''}
        ],
        "hints": [
            "`dft` is two nested loops. Accumulate into a `0j` so the sum stays complex even when every sample is real.",
            "The scaling in `amplitude_spectrum` is the part everyone gets wrong. Divide by `N` first; then double, because a real sinusoid puts half its amplitude in the positive-frequency bin and half in the negative one you are discarding. DC has no partner, and neither does the bin at $f_s/2$ when `N` is even.",
            "`alias_of` is two lines: `fa = f % fs`, then fold if `fa > fs / 2`. Check it against the module 3 sandbox — 170 Hz sampled at 200 Hz must come back as 30.",
            "For the convolution theorem, both sequences have to be the same length as the result before transforming: pad `x` and `h` with zeros out to `len(x) + len(h) - 1`, then compare `dft` of the convolution with the elementwise product.",
            "To measure the amplitude at the output of a filter, throw away the first `len(h) - 1` samples — that is the transient — and analyse a block containing a whole number of cycles, or the energy leaks into neighbouring bins.",
        ],
        "tests": [
            {"name": "the transform matches hand-worked four-point cases", "code": r'''
X = dft([1.0, 2.0, 3.0, 4.0])
assert len(X) == 4, f"the DFT has as many bins as samples, got {len(X)}"
want = [10 + 0j, -2 + 2j, -2 + 0j, -2 - 2j]
for k, (got, exp) in enumerate(zip(X, want)):
    assert abs(complex(got) - exp) < 1e-9, f"X[{k}] should be {exp}, got {got}"
D = dft([1.0, 0.0, 0.0, 0.0])
assert all(abs(complex(v) - 1) < 1e-12 for v in D), \
    f"an impulse transforms to all ones, got {D}"
'''},
            {"name": "a two-tone signal reads back in volts", "code": r'''
import numpy as np
fs = 1000.0
n = np.arange(200)
x = list(3.0 * np.sin(2 * np.pi * 50 * n / fs) + 1.0 * np.cos(2 * np.pi * 120 * n / fs))
freqs, amps = amplitude_spectrum(x, fs)
assert len(freqs) == 101, f"200 samples give bins 0..100, so 101 of them; got {len(freqs)}"
assert abs(freqs[1] - 5.0) < 1e-12, f"the bin spacing is fs/N = 5 Hz, got {freqs[1]}"
assert abs(freqs[10] - 50.0) < 1e-12, f"bin 10 should be 50 Hz, got {freqs[10]}"
assert abs(amps[10] - 3.0) < 1e-9, f"the 3 V tone must read 3.0, got {amps[10]}"
assert abs(amps[24] - 1.0) < 1e-9, f"the 1 V tone must read 1.0, got {amps[24]}"
rest = max(amps[k] for k in range(len(amps)) if k not in (10, 24))
assert rest < 1e-9, f"nothing else should be present, but a bin holds {rest}"
'''},
            {"name": "the folding rule, in band and far out of it", "code": r'''
cases = [(30.0, 200.0, 30.0), (170.0, 200.0, 30.0), (100.0, 200.0, 100.0),
         (250.0, 200.0, 50.0), (400.0, 200.0, 0.0), (1700.0, 1000.0, 300.0),
         (600.0, 1000.0, 400.0)]
for f, fs, want in cases:
    got = alias_of(f, fs)
    assert abs(got - want) < 1e-9, f"{f} Hz sampled at {fs} should appear at {want}, got {got}"
    assert -1e-9 <= got <= fs / 2 + 1e-9, f"an alias must land in 0..fs/2, got {got}"
'''},
            {"name": "the analyser sees the alias the rule predicted", "code": r'''
import numpy as np
fs = 1000.0
n = np.arange(200)
x = list(np.sin(2 * np.pi * 1700 * n / fs))
freqs, amps = amplitude_spectrum(x, fs)
peak = max(range(len(amps)), key=lambda k: amps[k])
assert abs(freqs[peak] - alias_of(1700.0, fs)) < 1e-9, \
    f"the peak is at {freqs[peak]} Hz but alias_of predicted {alias_of(1700.0, fs)}"
assert abs(amps[peak] - 1.0) < 1e-9, \
    f"aliasing moves a tone without shrinking it, so the peak should read 1.0, got {amps[peak]}"
'''},
            {"name": "convolution in time is multiplication in frequency", "code": r'''
x = [1.0, -2.0, 3.0, 0.5]
h = [0.5, 0.25, -1.0]
y = convolve(x, h)
assert len(y) == 6, f"4 + 3 - 1 is 6 samples, got {len(y)}"
want = [0.5, -0.75, 0.0, 3.0, -2.875, -0.5]
assert all(abs(a - b) < 1e-12 for a, b in zip(y, want)), f"expected {want}, got {y}"
L = len(y)
X = dft(x + [0.0] * (L - len(x)))
H = dft(h + [0.0] * (L - len(h)))
Y = dft(y)
err = max(abs(complex(Y[k]) - complex(X[k]) * complex(H[k])) for k in range(L))
assert err < 1e-9, f"DFT(x * h) should equal DFT(x) DFT(h); largest disagreement {err}"
'''},
            {"name": "the measured filter response matches the computed one", "code": r'''
import numpy as np
fs = 1000.0
h = [0.25] * 4
assert abs(response_at(h, 0.0, fs) - 1.0) < 1e-12, \
    f"a four-point average has unity gain at DC, got {response_at(h, 0.0, fs)}"
assert abs(response_at(h, 250.0, fs)) < 1e-12, \
    f"it puts a null at fs/4 = 250 Hz, got {abs(response_at(h, 250.0, fs))}"
predicted = abs(response_at(h, 100.0, fs))
assert abs(predicted - 0.7694208842938134) < 1e-9, \
    f"|H| at 100 Hz should be 0.76942, got {predicted}"
n = np.arange(400)
y = convolve(list(np.cos(2 * np.pi * 100 * n / fs)), h)
block = y[3:303]
freqs, amps = amplitude_spectrum(block, fs)
k = amps.index(max(amps))
assert abs(freqs[k] - 100.0) < 1e-9, f"the output is still at 100 Hz, measured {freqs[k]}"
assert abs(amps[k] - predicted) < 1e-9, \
    f"measured amplitude {amps[k]} against computed |H| {predicted}"
'''},
        ],
    },
}
