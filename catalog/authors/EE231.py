"""EE231 — Transforms and Linear Algebra.

A second-year course. It assumes EE111: complex numbers, phasors, differentiation and
integration, and a first sight of simultaneous equations as a matrix. It also assumes
EE102-level AC circuit analysis — impedance, the divider rule applied to impedances,
inductors, and the corner frequency of an RC. Both are first-year courses; nothing
above them is used.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * every expected number in this file was produced by running the code or the
    circuit solver, never assumed
  * build checks are JavaScript against the circuit API and measure what the
    circuit does, so an equally correct alternative topology passes
"""

COURSE = {
    "id": "EE231",
    "title": "Transforms and Linear Algebra",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE111"],
    "stack": ["Python", "NumPy", "SymPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◈",
    "summary": (
        "Phasors answer one question — what a circuit does to a sinusoid that has been "
        "running forever. The Laplace transform answers all the others: what happens at "
        "the instant a switch closes, how fast the answer arrives, whether it rings on "
        "the way. It does so by turning calculus into algebra, and the algebra it "
        "produces is linear algebra. This course develops both halves together, and ends "
        "by pulling a circuit model out of measured data with least squares."
    ),
    "outcomes": [
        "Transform a signal or a circuit into the s-domain, solve there, and interpret the answer back in time.",
        "Find the poles and zeros of a transfer function and predict the shape of the response from their positions alone.",
        "Split a rational transfer function into partial fractions and invert it term by term.",
        "Write a resistor network as a matrix equation, say what that matrix means as a linear map, and solve it.",
        "Compute eigenvalues and connect them to the poles of the same system written as a transfer function.",
        "Fit a model to measured data by least squares, and judge from the residuals whether the model was the right one.",
    ],
    "assessment": (
        "Four quizzes, two circuits designed and measured in the schematic editor, two "
        "guided derivations checked symbolically, four Python labs checked by execution, "
        "and a capstone that identifies an unknown second-order circuit from its measured "
        "step response."
    ),
    "reading": [
        "*Fundamentals of Electric Circuits*, Alexander & Sadiku — chapters 15 and 16 for the Laplace treatment of circuits.",
        "*Introduction to Linear Algebra*, Strang — chapters 1 to 4 and 6, for maps, least squares and eigenvalues in that order.",
        "*Signals and Systems*, Oppenheim & Willsky — chapter 9, for the transform on its own terms.",
        "MIT OCW 18.06, Strang's lectures, freely available — lecture 15 is the least squares one.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The Laplace transform",
            "summary": "One integral turns differentiation into multiplication by s, and a differential equation into ordinary algebra.",
            "concepts": [
                "The Laplace transform of $f(t)$ is $F(s) = \\int_0^{\\infty} f(t)e^{-st}\\,dt$, with $s = \\sigma + j\\omega$ a complex number. The lower limit is 0: the transform knows nothing about the past.",
                "$s$ is a generalised frequency. Setting $\\sigma = 0$ recovers the Fourier transform, which is why phasors are the special case of this that you already know.",
                "The transform is **linear**: $\\mathcal{L}\\{af + bg\\} = aF + bG$. Every technique in the course rests on that one property.",
                "Differentiation becomes multiplication: $\\mathcal{L}\\{f'\\} = sF(s) - f(0)$. The initial condition is not an afterthought — it is carried inside the algebra.",
                "Integration becomes division: $\\mathcal{L}\\{\\int_0^t f\\} = F(s)/s$. A unit step is the integral of an impulse, so $\\mathcal{L}\\{1\\} = 1/s$.",
                "The standard pairs worth knowing by heart: $1 \\leftrightarrow 1/s$, $e^{-at} \\leftrightarrow 1/(s+a)$, $\\sin\\omega t \\leftrightarrow \\omega/(s^2+\\omega^2)$, $\\cos\\omega t \\leftrightarrow s/(s^2+\\omega^2)$, $te^{-at} \\leftrightarrow 1/(s+a)^2$.",
                "Components have s-domain impedances: $Z_R = R$, $Z_L = sL$, $Z_C = 1/(sC)$. Every series and parallel rule from EE101 works unchanged with these, and now covers switch-on as well as steady state.",
                "The final value theorem, $\\lim_{t\\to\\infty} f(t) = \\lim_{s\\to 0} sF(s)$, is only valid when the response actually settles — apply it to an oscillator and it returns a confident wrong answer.",
            ],
            "sandbox": {
                "title": "Where the poles are, and what the circuit does",
                "visualiser": "pole-step",
                "minutes": 9,
                "initial": {"zeta": 0.5, "wn": 4},
                "brief": r'''
Solving a circuit with Laplace gives a fraction in $s$. The roots of its denominator
are called the **poles**, and they are the whole story: from their positions alone you
can say whether the response overshoots, how long it rings and how quickly it settles,
without ever inverting the transform.

The left-hand plot is the complex $s$-plane, with $\sigma$ across and $j\omega$ up.
The two dots are the poles of a standard second-order system

$$H(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

whose roots sit at $s = -\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}$. The right-hand
plot is the step response those two poles produce, with a dashed line at the final
value of 1.

Move the sliders and watch the two pictures move together. This pairing is the single
most useful mental image in the rest of the degree.
''',
                "notice": [
                    "It opens at $\\zeta = 0.5$, $\\omega_n = 4$. Both poles sit at a real part of $-2$, one above the horizontal axis and one the same distance below it, and the plot labels the height $\\omega_d = 3.46$. On the right the curve climbs past the dashed line to about 1.16, dips below, and settles. The readout underneath reports 16.3% overshoot and settling in about 2 s.",
                    "Drag $\\zeta$ down to 0. The two dots slide onto the vertical axis, at $\\pm j4$, and the step response never settles at all — it swings between 0 and 2 for as long as the plot runs. The real part of a pole *is* the decay rate, so with no real part there is no decay.",
                    "Now take $\\zeta$ up to 1.6. The dots change colour, drop onto the horizontal axis, and the label changes to 'both poles real'. They separate, one drifting in towards about $-1.4$ and the other out to about $-11.4$. The response no longer overshoots — and it is so sluggish that by the right-hand edge of the plot it has only reached about 0.92, still short of the dashed line. That near pole is what makes it slow.",
                    "Put $\\zeta$ back to 0.5 and drag $\\omega_n$ from 4 up to 12. The pair slides outwards along the same straight ray, keeping its angle of 60° from the negative real axis. The step curve keeps its exact shape while the numbers along the time axis shrink by a factor of three: the angle sets the shape, the distance from the origin sets the speed.",
                ],
            },
            "derive": {
                "title": "An RC circuit solved in the s-domain",
                "minutes": 14,
                "vars": ["s", "R", "C", "t", "A", "B", "V_in", "V_c", "tau"],
                "brief": r'''
A resistor $R$ in series with a capacitor $C$, with the output taken across the
capacitor and a 1 V step applied at $t = 0$.

In EE111 this needed a first-order differential equation, an integrating factor and a
constant of integration. Here it needs the divider rule you already know from EE101,
applied to impedances that happen to contain $s$. Use $Z_R = R$ and $Z_C = 1/(sC)$.
''',
                "steps": [
                    {
                        "prompt": "Apply the divider rule with impedances. Write $V_c(s)$ as a multiple of $V_{in}(s)$, in terms of $s$, $R$, $C$ and $V_{in}$.",
                        "given": "The divider is $V_c = V_{in} \\, Z_C / (Z_R + Z_C)$, with $Z_C = 1/(sC)$.",
                        "answer": "\\frac{V_in}{1 + sRC}",
                        "hint": "Put $1/(sC)$ over $R + 1/(sC)$, then multiply top and bottom by $sC$ to clear the inner fraction.",
                        "deconstruct": [
                            "The ratio is $\\dfrac{1/(sC)}{R + 1/(sC)}$.",
                            "Multiplying top and bottom by $sC$ gives $\\dfrac{1}{sRC + 1}$.",
                            "That whole thing multiplies $V_{in}$.",
                        ],
                    },
                    {
                        "prompt": "The input is a 1 V step, so $V_{in}(s) = 1/s$. Substitute it and write $V_c(s)$ in terms of $s$, $R$ and $C$ only.",
                        "answer": "\\frac{1}{s(1 + sRC)}",
                        "hint": "You are multiplying the previous answer by $1/s$. Nothing cancels.",
                        "deconstruct": [
                            "The step contributes a factor $1/s$.",
                            "So the circuit's own fraction picks up an extra pole at $s = 0$, which is the input's pole, not the circuit's.",
                        ],
                    },
                    {
                        "prompt": "Split it: $V_c(s) = \\dfrac{A}{s} + \\dfrac{B}{1 + sRC}$. Multiply both sides by $s$, then set $s = 0$. What is $A$?",
                        "answer": "1",
                        "hint": "Multiplying by $s$ leaves $\\dfrac{1}{1+sRC}$ on the left. Now put $s = 0$ into that.",
                        "deconstruct": [
                            "$s \\cdot V_c(s) = \\dfrac{1}{1+sRC}$, and the second term picks up a factor $s$ which kills it at $s=0$.",
                            "At $s = 0$ the surviving expression is $1/1$.",
                        ],
                    },
                    {
                        "prompt": "Now multiply both sides by $(1 + sRC)$ and set $s = -1/(RC)$, which is where that factor vanishes. What is $B$?",
                        "answer": "-RC",
                        "hint": "The left-hand side becomes $1/s$. Evaluate it at $s = -1/(RC)$.",
                        "deconstruct": [
                            "$(1+sRC)\\,V_c(s) = \\dfrac{1}{s}$, and the $A/s$ term picks up the factor $(1+sRC)$, which is zero at this $s$.",
                            "So $B = 1/s$ evaluated at $s = -1/(RC)$, which is $-RC$.",
                        ],
                    },
                    {
                        "prompt": "The second term is now $\\dfrac{-RC}{1 + sRC}$. Divide top and bottom by $RC$ so it reads $\\dfrac{-1}{s + a}$, and write $a$ in terms of $R$ and $C$.",
                        "answer": "\\frac{1}{RC}",
                        "hint": "Dividing $1 + sRC$ by $RC$ gives $s + 1/(RC)$.",
                        "deconstruct": [
                            "$\\dfrac{-RC}{1+sRC} = \\dfrac{-RC/(RC)}{(1+sRC)/(RC)} = \\dfrac{-1}{s + 1/(RC)}$.",
                            "So the pole sits at $s = -1/(RC)$ and $a = 1/(RC)$.",
                        ],
                    },
                    {
                        "prompt": "Using $1/s \\to 1$ and $1/(s+a) \\to e^{-at}$, the answer is $v_c(t) = 1 - e^{-t/\\tau}$. Write the time constant $\\tau$ in terms of $R$ and $C$.",
                        "answer": "R C",
                        "hint": "$\\tau = 1/a$, and you have just written $a$.",
                        "deconstruct": [
                            "The pole is at $-1/(RC)$, so the decaying exponential is $e^{-t/(RC)}$.",
                            "Comparing with $e^{-t/\\tau}$ gives $\\tau = RC$.",
                        ],
                    },
                ],
                "closing": r'''
Six lines of algebra and no calculus at all. Notice where each piece came from: the
pole at $s = 0$ was the *input's*, and it produced the constant 1 that the output
settles at. The pole at $-1/(RC)$ was the *circuit's*, and it produced the decaying
exponential. That separation — input poles give the steady part, circuit poles give
the transient — holds for every linear circuit you will ever meet.
''',
            },
            "lab": {
                "title": "Computing the transform, rather than looking it up",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
A table of transforms is easy to distrust because nothing in it looks computed. So
compute it. The Laplace transform is a definite integral, and a definite integral is a
sum you can evaluate numerically.

- `laplace(f, s, tmax, n)` approximates $\int_0^{t_{max}} f(t)e^{-st}\,dt$ by the
  trapezium rule on `n` evenly spaced samples between 0 and `tmax`, and returns the
  result. `s` may be complex, and then so is the answer. `f` is a function that takes
  a NumPy array of times and returns an array of values.
- `rc_step_voltage(R, C, t)` returns the capacitor voltage of a series RC driven by a
  1 V step — the closed form you derived a moment ago. `t` may be an array.
- `settling_time(R, C, frac)` returns the time at which that voltage first reaches
  `frac` of its final value.

## The trapezium rule, in two lines

With samples $y_0 \dots y_{n-1}$ spaced $h$ apart, the trapezium estimate of the
integral is

```text
h * (sum(y) - 0.5 * (y[0] + y[-1]))
```

which is the plain sum with the two end samples counted half. Build the array `y` as
`f(t) * np.exp(-s * t)` and that line finishes the function.

`tmax` is finite but the integral is not, so the answer is only right when the
integrand has decayed to nothing by `tmax`. Every call in the checks has been given a
`tmax` where it has. This is worth remembering: the transform of something that does
not decay — a pure sinusoid, a step — does not converge for real $s \le 0$, and the
region of $s$ where it does converge is exactly the half-plane to the right of the
rightmost pole.
''',
                "files": [{"name": "main.py", "content": r'''
"""The Laplace transform as an integral you can actually evaluate."""

import numpy as np


def laplace(f, s, tmax=40.0, n=200001):
    """Trapezium-rule estimate of the integral of f(t) exp(-s t) from 0 to tmax."""
    # TODO: build the time grid with np.linspace, form y = f(t) * np.exp(-s * t),
    #       and return h * (sum(y) - 0.5 * (y[0] + y[-1])).
    return 0.0


def rc_step_voltage(R, C, t):
    """Capacitor voltage of a series RC driven by a 1 V step at t = 0."""
    # TODO: 1 - exp(-t / RC).
    return 0.0


def settling_time(R, C, frac):
    """Time at which the capacitor first reaches `frac` of its final value."""
    # TODO: solve frac = 1 - exp(-t / RC) for t.
    return 0.0


if __name__ == "__main__":
    print("L{1} at s=2 should be 0.5:", laplace(lambda t: np.ones_like(t), 2.0))
    print("L{exp(-3t)} at s=1 should be 0.25:", laplace(lambda t: np.exp(-3 * t), 1.0))
    print("a 1 k with 1 uF reaches 63.2% after", settling_time(1000.0, 1e-6, 0.632), "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The Laplace transform as an integral you can actually evaluate.

Every number quoted in the checks was produced by running this file:
    L{1}(2)        -> 0.5000000067   (exact 0.5)
    L{exp(-3t)}(1) -> 0.2500000133   (exact 0.25)
    L{cos 2t}(1)   -> 0.2000000033   (exact 0.2)
    L{exp(-t)}(1+2j) -> 0.2500000067 - 0.2499999933j, which is 1/(2+2j) to 7e-9
"""

import numpy as np


def laplace(f, s, tmax=40.0, n=200001):
    """Trapezium-rule estimate of the integral of f(t) exp(-s t) from 0 to tmax."""
    t = np.linspace(0.0, tmax, n)
    h = t[1] - t[0]
    y = f(t) * np.exp(-s * t)
    return h * (np.sum(y) - 0.5 * (y[0] + y[-1]))


def rc_step_voltage(R, C, t):
    """Capacitor voltage of a series RC driven by a 1 V step at t = 0."""
    return 1.0 - np.exp(-np.asarray(t, dtype=float) / (R * C))


def settling_time(R, C, frac):
    """Time at which the capacitor first reaches `frac` of its final value."""
    return -R * C * np.log(1.0 - frac)


if __name__ == "__main__":
    print("L{1} at s=2 should be 0.5:", laplace(lambda t: np.ones_like(t), 2.0))
    print("L{exp(-3t)} at s=1 should be 0.25:", laplace(lambda t: np.exp(-3 * t), 1.0))
    print("a 1 k with 1 uF reaches 63.2% after", settling_time(1000.0, 1e-6, 0.632), "s")
'''}],
                "hints": [
                    "`t = np.linspace(0.0, tmax, n)` and `h = t[1] - t[0]`. Do not compute `h` as `tmax / n` — with `n` samples there are only `n - 1` gaps.",
                    "`y = f(t) * np.exp(-s * t)` works unchanged for complex `s`, because NumPy promotes the array to complex on its own.",
                    "`rc_step_voltage` is the closed form from the derivation: `1 - np.exp(-t / (R * C))`. Wrap `t` with `np.asarray(t, dtype=float)` so it works for a single number and for an array.",
                    "For `settling_time`, rearrange $\\text{frac} = 1 - e^{-t/RC}$ to $t = -RC\\ln(1-\\text{frac})$.",
                    "If a transform comes out far too small, check `tmax`: the integrand must have decayed to nothing by then, or you have integrated only part of it.",
                ],
                "tests": [
                    {"name": "the transform of a constant is 1/s", "code": r'''
got = laplace(lambda t: np.ones_like(t), 2.0)
assert abs(got - 0.5) < 1e-6, f"L{{1}} at s=2 is 1/2 = 0.5, got {got}"
got = laplace(lambda t: np.ones_like(t), 5.0)
assert abs(got - 0.2) < 1e-6, f"L{{1}} at s=5 is 1/5 = 0.2, got {got}"
'''},
                    {"name": "the transform of a decaying exponential is 1/(s+a)", "code": r'''
got = laplace(lambda t: np.exp(-3.0 * t), 1.0)
assert abs(got - 0.25) < 1e-6, f"L{{exp(-3t)}} at s=1 is 1/4 = 0.25, got {got}"
got = laplace(lambda t: np.exp(-0.5 * t), 2.0)
assert abs(got - 0.4) < 1e-6, f"L{{exp(-t/2)}} at s=2 is 1/2.5 = 0.4, got {got}"
'''},
                    {"name": "the sine and cosine pairs come out right", "code": r'''
got = laplace(lambda t: np.cos(2.0 * t), 1.0)
assert abs(got - 0.2) < 1e-6, f"L{{cos 2t}} at s=1 is 1/(1+4) = 0.2, got {got}"
got = laplace(lambda t: np.sin(3.0 * t), 2.0)
assert abs(got - 3.0 / 13.0) < 1e-6, \
    f"L{{sin 3t}} at s=2 is 3/(4+9) = 0.23077, got {got}"
'''},
                    {"name": "a complex s gives a complex answer", "code": r'''
got = laplace(lambda t: np.exp(-t), 1.0 + 2.0j)
want = 1.0 / (2.0 + 2.0j)
assert abs(got - want) < 1e-6, \
    f"L{{exp(-t)}} at s=1+2j is 1/(2+2j) = {want}, got {got}"
assert abs(got.imag + 0.25) < 1e-6, \
    "the imaginary part should be -0.25; a real answer means exp(-s*t) was never complex"
'''},
                    {"name": "the RC step response and its time constant", "code": r'''
v = rc_step_voltage(1000.0, 1e-6, 1e-3)
assert abs(v - 0.6321205588285577) < 1e-9, \
    f"after one time constant the capacitor is at 1 - 1/e = 0.63212, got {v}"
tt = settling_time(1000.0, 1e-6, 0.99)
assert abs(tt - 0.004605170185988091) < 1e-9, \
    f"99% takes RC*ln(100) = 4.6052 ms, got {tt} s"
assert abs(settling_time(1000.0, 1e-6, 0.6321205588285577) - 1e-3) < 1e-12, \
    "63.2% must come back as exactly one time constant"
'''},
                    {"name": "transforming the step response recovers 1/(s(1+sRC))", "code": r'''
s = 2000.0
got = laplace(lambda t: rc_step_voltage(1000.0, 1e-6, t), s, tmax=0.05, n=200001)
want = 1.0 / (s * (1.0 + s * 1e-3))
assert abs(got - want) < 1e-9, \
    f"the transform of the step response should be 1/(s(1+sRC)) = {want}, got {got}"
'''},
                ],
            },
            "quiz": {
                "title": "The transform, its rules and its poles",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The Laplace transform of $f(t)$ is defined as:",
                        "opts": [
                            "$\\int_0^{\\infty} f(t)e^{st}\\,dt$",
                            "$\\int_{-\\infty}^{\\infty} f(t)e^{-j\\omega t}\\,dt$",
                            "$\\int_0^{\\infty} f(t)e^{-st}\\,dt$",
                            "$\\sum_{n=0}^{\\infty} f(nT)z^{-n}$",
                        ],
                        "a": 2,
                        "why": r'''
The kernel is $e^{-st}$, with a minus sign, and the integral runs from 0, not from
$-\infty$. The version with $e^{+st}$ has the sign wrong, and with it the convergence: it makes the
integral diverge for every ordinary signal. The integral from $-\infty$ with kernel
$e^{-j\omega t}$ is the **Fourier** transform,
which is this one restricted to $s = j\omega$ — a genuinely useful thing to notice
rather than a trap, because it is why phasors are a special case of what you are
learning. The sum in powers of $z^{-n}$ is the z-transform, for sampled signals.
''',
                    },
                    {
                        "q": "With $F(s) = \\mathcal{L}\\{f(t)\\}$, the transform of $\\dfrac{df}{dt}$ is:",
                        "opts": ["$sF(s) - f(0)$", "$sF(s)$", "$F(s)/s$", "$sF(s) + f(0)$"],
                        "a": 0,
                        "why": r'''
$sF(s) - f(0)$. The $-f(0)$ falls out of integrating by parts, and dropping it is the
single most common error in the whole subject — it silently assumes every capacitor
starts empty and every inductor starts with no current. When a question says
"the capacitor is initially charged to 2 V", that 2 V enters the algebra through
exactly this term and nowhere else. $F(s)/s$ is the *integration* rule.
''',
                    },
                    {
                        "q": "A 1 V step is applied at $t=0$ to a series RC with the output taken across the capacitor. What is $V_c(s)$?",
                        "opts": [
                            "$\\dfrac{1}{1+sRC}$",
                            "$\\dfrac{s}{1+sRC}$",
                            "$\\dfrac{RC}{1+sRC}$",
                            "$\\dfrac{1}{s(1+sRC)}$",
                        ],
                        "a": 3,
                        "why": r'''
Two factors multiply: the circuit's transfer function $1/(1+sRC)$ and the input's own
transform $1/s$. $1/(1+sRC)$ on its own is the transfer function — which is what you get by forgetting
that the step also has to be transformed. That distinction matters: the
transfer function belongs to the circuit and never changes, while the $1/s$ belongs to
the signal you chose to apply.
''',
                    },
                    {
                        "q": "Four systems have the pole pairs below. Which one's response takes longest to die away?",
                        "opts": [
                            "$-5 \\pm j50$",
                            "$-0.5 \\pm j2$",
                            "$-20$ (twice)",
                            "$-3 \\pm j100$",
                        ],
                        "a": 1,
                        "why": r'''
Decay is governed by the **real part** alone: the envelope is $e^{\sigma t}$, so the
pole closest to the imaginary axis, here $\sigma = -0.5$, lingers longest. The
imaginary part sets how fast the response *oscillates*, not how fast it dies, which is why $-3 \pm j100$ — the most dramatic-looking pair, ringing at 100 rad/s —
actually settles six times faster than $-0.5 \pm j2$. Distance from the imaginary axis is speed; height
above it is ringing.
''',
                    },
                    {
                        "q": "The final value theorem gives $\\lim_{t\\to\\infty} f(t) = \\lim_{s\\to 0} sF(s)$. For $F(s) = \\dfrac{10}{s(s+4)}$, what is the final value?",
                        "opts": ["0", "10", "2.5", "40"],
                        "a": 2,
                        "why": r'''
$sF(s) = 10/(s+4)$, and at $s = 0$ that is $10/4 = 2.5$. Cancelling the $s$ first is
the whole technique. A warning that costs marks every year: the theorem is only valid
when the response really does settle, which means every pole of $sF(s)$ must have a
negative real part. Apply it to $F(s) = \omega/(s^2+\omega^2)$, a sine that never
settles, and it returns 0 with complete confidence.
''',
                    },
                    {
                        "q": "Applying the transform to a linear differential equation with constant coefficients turns it into:",
                        "opts": [
                            "an algebraic equation in $s$",
                            "a difference equation in $n$",
                            "a nonlinear equation",
                            "an integral equation",
                        ],
                        "a": 0,
                        "why": r'''
That is the entire point of the exercise. Each derivative becomes a factor of $s$, so
an $n$-th order differential equation becomes an $n$-th degree polynomial equation —
which you solve by rearranging, exactly as in school algebra, and then invert. The
price is that you must be able to get back: that is what partial fractions, in the
next module, are for. Difference equations and the z-transform belong to sampled
systems, which arrive in a later course.
''',
                    },
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Poles, zeros and partial fractions",
            "summary": "A transfer function is a fraction. Its roots on top and bottom decide everything, and splitting it apart puts the answer back into the time domain.",
            "concepts": [
                "A **transfer function** $H(s) = V_{out}(s)/V_{in}(s)$ is a ratio of polynomials in $s$, determined entirely by the circuit and not at all by the input.",
                "The roots of the denominator are the **poles**; the roots of the numerator are the **zeros**. A pole is a value of $s$ at which $H$ blows up, a zero one at which it vanishes.",
                "Each pole $p_i$ contributes a term $k_i e^{p_i t}$ to the response. The system is stable exactly when every pole has a negative real part.",
                "Complex poles always arrive in conjugate pairs for a real circuit, and a pair $\\sigma \\pm j\\omega_d$ contributes a decaying oscillation $e^{\\sigma t}\\sin(\\omega_d t + \\phi)$, never a complex voltage.",
                "**Partial fractions**: for distinct poles, $H(s) = \\sum_i \\dfrac{k_i}{s - p_i}$, and the residue is $k_i = \\dfrac{N(p_i)}{D'(p_i)}$ — the numerator over the derivative of the denominator, both evaluated at the pole.",
                "A repeated pole needs an extra term: $1/(s+a)^2$ inverts to $te^{-at}$, not to a plain exponential.",
                "The standard second-order form $H(s) = \\dfrac{K\\omega_n^2}{s^2 + 2\\zeta\\omega_n s + \\omega_n^2}$ has poles at $-\\zeta\\omega_n \\pm j\\omega_n\\sqrt{1-\\zeta^2}$: $\\omega_n$ is their distance from the origin and $\\zeta$ is the cosine of their angle from the negative real axis.",
                "On a Bode plot each pole bends the gain down by 20 dB/decade and the phase by 90°; at $\\omega = \\omega_n$ a second-order pole pair gives a gain of exactly $K/(2\\zeta)$ and a phase of exactly $-90°$, whatever the damping.",
            ],
            "sandbox": {
                "title": "The same poles, seen in frequency",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 20, "zeta": 0.25, "K": 1},
                "brief": r'''
Module 1 looked at poles through the step response. This is the same pole pair seen
the other way, by sweeping a sinusoid across frequency and recording what comes out.

The upper plot is $20\log_{10}|H(j\omega)|$ in decibels; the lower is the phase in
degrees. Both use a logarithmic frequency axis, which is why a factor of ten always
occupies the same width. The dashed line on the upper plot marks 0 dB — output equal
to input — and the dashed line on the lower marks $-90°$. The amber dot marks the
gain at $\omega = \omega_n$.

The sliders are the same $\omega_n$ and $\zeta$ as before, plus a gain $K$ that
multiplies the whole response.
''',
                "notice": [
                    "It opens at $\\omega_n = 20$, $\\zeta = 0.25$, $K = 1$. The gain is flat at 0 dB across the left of the plot, bulges up to about $+6.3$ dB just before $\\omega = 20$, then falls away steeply. The amber dot sits at $+6.0$ dB, which is $K/(2\\zeta) = 2$ expressed in decibels — the resonant *peak* and the value *at* $\\omega_n$ are close but not identical.",
                    "Read the lower plot. The phase leaves 0° on the far left and crosses the dashed $-90°$ line exactly at $\\omega = 20$, then flattens out at $-180°$ on the right. That final $-180°$ is the fingerprint of two poles; a single pole can never get past $-90°$.",
                    "Raise $\\zeta$ to 1. The bulge vanishes completely and the amber dot drops to $-6.0$ dB, which is $1/(2 \\times 1)$ in decibels. The phase still passes through $-90°$ at $\\omega = 20$, but the whole swing from 0° to $-180°$ is now spread over far more of the frequency axis — the crossing sits in the same place, the approach to it is gentler.",
                    "Put $\\zeta$ back to 0.25 and read the roll-off on the upper plot: about $-40$ dB at $\\omega = 200$, and the curve reaches the bottom of the frame, $-80$ dB, at $\\omega = 2000$. Two decades, 80 dB — that is 40 dB per decade, which is what two poles do. Now drag $K$ up to 10 and the whole gain curve lifts by 20 dB while the phase curve does not move at all.",
                ],
            },
            "derive": {
                "title": "From R, L and C to $\\omega_n$ and $\\zeta$",
                "minutes": 14,
                "vars": ["s", "R", "L", "C", "omega_n", "zeta", "K", "V_in", "V_out"],
                "brief": r'''
A resistor, an inductor and a capacitor all in series across a source, with the output
taken across the capacitor. This is the circuit you are about to build.

The aim is to get from the three component values to the two numbers that actually
describe the behaviour — $\omega_n$ and $\zeta$ — so that a design specification
written in those terms can be turned into parts.

Use $Z_R = R$, $Z_L = sL$ and $Z_C = 1/(sC)$, and remember that in series the same
current flows through all three, so the ordinary divider rule applies.
''',
                "steps": [
                    {
                        "prompt": "Write $H(s) = V_{out}/V_{in}$ as an impedance divider, leaving $Z_C$ as $1/(sC)$ for now.",
                        "answer": "\\frac{\\frac{1}{sC}}{R + sL + \\frac{1}{sC}}",
                        "hint": "The output impedance goes on top, the total series impedance on the bottom.",
                        "deconstruct": [
                            "In series the three impedances add: $Z_{total} = R + sL + 1/(sC)$.",
                            "The output is across $C$ alone, so the ratio is $Z_C/Z_{total}$.",
                        ],
                    },
                    {
                        "prompt": "Multiply top and bottom by $sC$ to clear the inner fraction, and write $H(s)$ as a single ratio of polynomials in $s$.",
                        "answer": "\\frac{1}{s^2 LC + sRC + 1}",
                        "hint": "$sC \\times 1/(sC) = 1$ on top; on the bottom every term picks up a factor $sC$.",
                        "deconstruct": [
                            "Top: $sC \\cdot \\dfrac{1}{sC} = 1$.",
                            "Bottom: $sC(R + sL + 1/(sC)) = sRC + s^2LC + 1$.",
                        ],
                    },
                    {
                        "prompt": "Divide top and bottom by $LC$ to reach the standard form $\\dfrac{K\\omega_n^2}{s^2 + 2\\zeta\\omega_n s + \\omega_n^2}$. Comparing the constant terms gives $\\omega_n^2 = 1/(LC)$. Write $\\omega_n$ itself.",
                        "answer": "\\frac{1}{\\sqrt{LC}}",
                        "hint": "Take the positive square root of $1/(LC)$.",
                        "deconstruct": [
                            "After dividing through, the constant term of the denominator is $1/(LC)$.",
                            "The standard form calls that constant term $\\omega_n^2$.",
                        ],
                    },
                    {
                        "prompt": "Comparing the $s$ coefficients gives $2\\zeta\\omega_n = R/L$. Substitute your $\\omega_n$ and write $\\zeta$ in terms of $R$, $L$ and $C$.",
                        "answer": "\\frac{R}{2}\\sqrt{\\frac{C}{L}}",
                        "hint": "$\\zeta = \\dfrac{R}{2L\\omega_n} = \\dfrac{R\\sqrt{LC}}{2L}$, and $\\sqrt{LC}/L = \\sqrt{C/L}$.",
                        "deconstruct": [
                            "From $2\\zeta\\omega_n = R/L$, $\\zeta = \\dfrac{R}{2L\\omega_n}$.",
                            "Substituting $\\omega_n = 1/\\sqrt{LC}$ gives $\\zeta = \\dfrac{R\\sqrt{LC}}{2L}$.",
                            "And $\\dfrac{\\sqrt{LC}}{L} = \\sqrt{\\dfrac{C}{L}}$.",
                        ],
                    },
                    {
                        "prompt": "Now design. With $L = 0.1$ H and $C = 2.5\\ \\mu$F, $\\omega_n$ comes to 2000 rad/s. What resistance, in ohms, gives $\\zeta = 0.25$?",
                        "answer": "100",
                        "hint": "Rearrange to $R = 2\\zeta\\sqrt{L/C}$, then put the numbers in. $\\sqrt{0.1/2.5\\times10^{-6}} = 200$.",
                        "deconstruct": [
                            "$\\zeta = \\dfrac{R}{2}\\sqrt{\\dfrac{C}{L}}$ rearranges to $R = 2\\zeta\\sqrt{\\dfrac{L}{C}}$.",
                            "$L/C = 0.1/2.5\\times10^{-6} = 40000$, whose square root is 200.",
                            "So $R = 2 \\times 0.25 \\times 200$.",
                        ],
                    },
                ],
                "closing": r'''
Two things are worth keeping. First, $\zeta$ depends on the *ratio* $C/L$, so you can
slide both up together without changing the shape of the response — only its speed.
Second, $\sqrt{L/C}$ has units of ohms and is called the characteristic impedance of
the pair; damping is just the resistance measured against it. Those numbers, 0.1 H,
2.5 µF and 100 Ω, are the ones the build exercise asks you to reach.
''',
            },
            "build": {
                "title": "Placing a pole pair with real components",
                "minutes": 26,
                "brief": r'''
Build a second-order low-pass filter whose poles sit exactly where you want them.

The specification, in the language of module 1:

- a **natural frequency** $\omega_n = 2000$ rad/s, which is 318.3 Hz
- a **damping ratio** $\zeta = 0.25$
- a **gain of 1** well below the corner, so the filter passes low frequencies untouched

The first two of those put the poles at $s = -500 \pm j1936$; the third fixes the
height of the response, not where the poles sit.

## What is on the canvas

A 1 V source, its ground, and a 0.1 H inductor already wired to the source's positive
terminal. Add a resistor, a capacitor, a second ground and a probe to finish a series
RLC with the **output taken across the capacitor**. Set the two values you add so that
the specification is met. Two relations give both, $\omega_n = 1/\sqrt{LC}$ and
$\zeta = \tfrac{R}{2}\sqrt{C/L}$; the guided derivation in this module builds them from
the divider rule if you want to see where they come from before using them.

The source is set to 1 V because the checks read the probe voltage directly and treat
it as the gain — leave it at 1 V, or every gain measurement comes out scaled.

## How this is measured

The checks sweep the finished circuit and read three things off it, none of which
cares how you laid the drawing out:

- the gain at 1 Hz, far below the corner, which must be 1
- the **phase** at 318.3 Hz, which must be $-90°$ — a second-order pole pair passes
  through exactly $-90°$ at $\omega_n$ whatever the damping, so this measurement pins
  $\omega_n$ on its own
- the **gain** at 318.3 Hz, which must be $1/(2\zeta) = 2$ — and that pins $\zeta$

A fourth check reads the gain a decade and two decades above the corner and confirms
they differ by a factor of 100. That is the 40 dB/decade of two poles; a plain RC
would give a factor of 10 and fail.

Changing the inductor is allowed. Any $L$, $R$ and $C$ that put the poles in the right
place will pass — but with $L$ fixed at 0.1 H there is exactly one answer, and it is
the one you computed in the derivation.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.1},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.1},
                        {"id": "p3", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 100},
                        {"id": "p4", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 2.5e-6},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 10},
                        {"id": "p6", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [13, 5]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 8], "b": [13, 10]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 1 V source drives the filter", "code": r'''
c.assert(c.count('V') === 1,
  'Use exactly one voltage source, so that "the gain" means one thing. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 1, 0.001,
  'the source amplitude — the checks read the probe voltage as the gain, so the input must be 1 V');
'''},
                    {"name": "low frequencies pass through untouched", "code": r'''
c.close(c.gain(1), 1.0, 0.02,
  'the gain at 1 Hz, far below the corner — a passive low-pass should hand the input straight over');
'''},
                    {"name": "the phase is -90 degrees at 318.3 Hz, so the natural frequency is 2000 rad/s", "code": r'''
const ph = c.phase(318.30988618379064);
c.assert(Math.abs(ph + 90) <= 3,
  'A second-order pole pair passes through exactly -90 degrees at its natural frequency. ' +
  'At 318.3 Hz this circuit is at ' + ph.toFixed(1) + ' degrees, so its natural frequency is not 2000 rad/s.');
'''},
                    {"name": "the gain at that frequency is 2, so the damping ratio is 0.25", "code": r'''
c.close(c.gain(318.30988618379064), 2.0, 0.04,
  'the gain at the natural frequency, which for this form is 1/(2*zeta)');
'''},
                    {"name": "the roll-off is 40 dB per decade, so there really are two poles", "code": r'''
const a = c.gain(3183.0988618379064);
const b = c.gain(31830.988618379065);
c.assert(b > 0, 'The response died to nothing; check the output is taken across the capacitor.');
c.close(a / b, 100, 0.05,
  'the ratio of the gains one and two decades above the corner — two poles give 100, a single RC only 10');
'''},
                ],
                "hints": [
                    "The order round the loop is source, inductor, resistor, capacitor, ground, with the probe on the node between the resistor and the capacitor.",
                    "$\\omega_n = 1/\\sqrt{LC}$. With $L = 0.1$ H and $\\omega_n = 2000$ rad/s, $C = 1/(\\omega_n^2 L) = 2.5\\ \\mu$F. Type `2.5u` in the value box.",
                    "$\\zeta = \\dfrac{R}{2}\\sqrt{C/L}$. With those values $\\sqrt{C/L} = 0.005$, so $\\zeta = 0.0025R$ and $\\zeta = 0.25$ needs $R = 100$ Ω.",
                    "If the phase check passes but the gain at the corner is too small, $\\omega_n$ is right and the resistor is too large — the damping is what the resistor sets.",
                    "If the low-frequency gain is not 1, the probe is probably on the wrong node. Across the capacitor the inductor is a short and the capacitor an open at DC, so the whole input appears at the output.",
                ],
            },
            "lab": {
                "title": "Partial fractions by residue, and the response they give",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
A transfer function arrives as two coefficient lists, highest power first, exactly as
`numpy.roots` and `numpy.polyval` expect. `[1.0, 4.0, 3.0]` means $s^2 + 4s + 3$.

Write four functions.

- `poles(den)` returns the roots of the denominator.
- `residues(num, den)` returns the residue at each pole, in the same order as `poles`
  returns them. For distinct poles the residue is
  $k_i = N(p_i)/D'(p_i)$ — numerator over the *derivative* of the denominator, both
  evaluated at the pole. `np.polyder` differentiates a coefficient list.
- `impulse_response(num, den, t)` returns $\sum_i k_i e^{p_i t}$ evaluated on the array
  `t`, as **real** numbers.
- `dc_gain(num, den)` returns $H(0)$.

## Why the answer is real

The poles of a real circuit come in conjugate pairs, and so do their residues. Add the
two terms of a pair and the imaginary parts cancel exactly, leaving a decaying
sinusoid. Numerically they cancel to about $10^{-16}$ rather than to zero, so take
`.real` at the end — and if you find yourself taking `abs()` instead, stop: that would
turn a legitimate negative voltage into a positive one.

The residue formula only holds for **distinct** poles. Repeated poles need an extra
term in $te^{-at}$, and the formula divides by zero if you try it, which at least
fails loudly.
''',
                "files": [{"name": "main.py", "content": r'''
"""Partial fractions by the residue formula, and the time response they encode."""

import numpy as np


def poles(den):
    """Roots of the denominator polynomial, highest power first."""
    # TODO: np.roots does this in one call.
    return np.array([])


def residues(num, den):
    """Residue at each pole, in the same order as poles(den)."""
    # TODO: for each pole p, np.polyval(num, p) / np.polyval(np.polyder(den), p).
    return np.array([])


def impulse_response(num, den, t):
    """Sum of k_i exp(p_i t) over the poles, returned as real numbers."""
    # TODO: accumulate into a complex array, then return its .real part.
    return np.zeros(np.asarray(t, dtype=float).shape)


def dc_gain(num, den):
    """H(0) — the gain the system settles to."""
    # TODO: evaluate both polynomials at s = 0.
    return 0.0


if __name__ == "__main__":
    num, den = [6.0], [1.0, 4.0, 3.0]
    print("poles:", poles(den))
    print("residues:", residues(num, den))
    print("h(0.5):", impulse_response(num, den, np.array([0.5])))
    print("dc gain:", dc_gain(num, den))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Partial fractions by the residue formula, and the time response they encode.

Verified by running this file:
    6/((s+1)(s+3)) -> poles -3, -1 with residues -3, +3, so h(t) = 3e^-t - 3e^-3t
    h(0.5) = 1.1502014986926108, which is 3*exp(-0.5) - 3*exp(-1.5) exactly
    4/(s^2+2s+5) -> poles -1 +/- 2j, residues -/+ j, so h(t) = 2 e^-t sin 2t
    h(0.5) = 1.0207559030891455 = 2*exp(-0.5)*sin(1)
"""

import numpy as np


def poles(den):
    """Roots of the denominator polynomial, highest power first."""
    return np.roots(den)


def residues(num, den):
    """Residue at each pole, in the same order as poles(den)."""
    dden = np.polyder(den)
    return np.array([np.polyval(num, p) / np.polyval(dden, p) for p in poles(den)])


def impulse_response(num, den, t):
    """Sum of k_i exp(p_i t) over the poles, returned as real numbers."""
    t = np.asarray(t, dtype=float)
    y = np.zeros(t.shape, dtype=complex)
    for k, p in zip(residues(num, den), poles(den)):
        y = y + k * np.exp(p * t)
    return y.real


def dc_gain(num, den):
    """H(0) — the gain the system settles to."""
    return np.polyval(num, 0.0) / np.polyval(den, 0.0)


if __name__ == "__main__":
    num, den = [6.0], [1.0, 4.0, 3.0]
    print("poles:", poles(den))
    print("residues:", residues(num, den))
    print("h(0.5):", impulse_response(num, den, np.array([0.5])))
    print("dc gain:", dc_gain(num, den))
'''}],
                "hints": [
                    "`poles` is `np.roots(den)` and nothing else.",
                    "`np.polyder(den)` returns the coefficient list of $D'(s)$; then `np.polyval(dden, p)` evaluates it at the pole. A list comprehension over the poles gives the residues in one line.",
                    "In `impulse_response`, start with `y = np.zeros(t.shape, dtype=complex)` — starting with a real array silently discards every imaginary part as you add to it.",
                    "`dc_gain` is `np.polyval(num, 0.0) / np.polyval(den, 0.0)`, which for a plain coefficient list is just the last entry of each.",
                    "A useful self-check: when the numerator's degree is at least two below the denominator's, the impulse response must start at exactly 0, because the residues sum to zero.",
                ],
                "tests": [
                    {"name": "a single real pole", "code": r'''
p = poles([1.0, 2.0])
assert len(p) == 1, f"s + 2 has one root, got {len(p)}"
assert abs(p[0] + 2.0) < 1e-12, f"the root of s + 2 is -2, got {p[0]}"
k = residues([1.0], [1.0, 2.0])
assert abs(k[0] - 1.0) < 1e-12, f"1/(s+2) has residue 1, got {k[0]}"
'''},
                    {"name": "two real poles, and residues that cancel at t = 0", "code": r'''
num, den = [6.0], [1.0, 4.0, 3.0]
p = np.sort(np.real(poles(den)))
assert abs(p[0] + 3.0) < 1e-9 and abs(p[1] + 1.0) < 1e-9, \
    f"s^2+4s+3 factorises as (s+1)(s+3), got roots {p}"
k = residues(num, den)
assert abs(np.sum(k)) < 1e-9, \
    f"with the numerator two degrees below, the residues must sum to 0, got {np.sum(k)}"
h0 = impulse_response(num, den, np.array([0.0]))[0]
assert abs(h0) < 1e-9, f"h(0) must therefore be 0, got {h0}"
'''},
                    {"name": "the impulse response matches the closed form", "code": r'''
got = impulse_response([6.0], [1.0, 4.0, 3.0], np.array([0.5]))[0]
want = 3.0 * np.exp(-0.5) - 3.0 * np.exp(-1.5)
assert abs(got - want) < 1e-9, \
    f"h(t) = 3exp(-t) - 3exp(-3t), so h(0.5) = {want}, got {got}"
got2 = impulse_response([6.0], [1.0, 4.0, 3.0], np.array([0.0, 0.5, 2.0]))
assert got2.shape == (3,), f"an array of times must give an array of values, got shape {got2.shape}"
'''},
                    {"name": "a complex pair gives a real decaying sinusoid", "code": r'''
num, den = [4.0], [1.0, 2.0, 5.0]
p = poles(den)
assert abs(abs(p[0].imag) - 2.0) < 1e-9, \
    f"s^2+2s+5 has roots -1 +/- 2j, got {p}"
got = impulse_response(num, den, np.array([0.5]))[0]
want = 2.0 * np.exp(-0.5) * np.sin(1.0)
assert abs(got - want) < 1e-9, \
    f"this pair gives h(t) = 2 exp(-t) sin(2t), so h(0.5) = {want}, got {got}"
assert np.imag(got) == 0.0 or isinstance(got, float) or got.imag == 0.0, \
    "the answer must be real, not a complex number with a tiny imaginary part"
'''},
                    {"name": "the DC gain, and the transform read back out of the response", "code": r'''
assert abs(dc_gain([6.0], [1.0, 4.0, 3.0]) - 2.0) < 1e-12, "6/3 = 2"
assert abs(dc_gain([1.0], [2.5e-07, 0.00025, 1.0]) - 1.0) < 1e-12, \
    "the RLC filter of the build exercise has a DC gain of 1"
t = np.linspace(0.0, 30.0, 300001)
y = impulse_response([6.0], [1.0, 4.0, 3.0], t) * np.exp(-2.0 * t)
h = t[1] - t[0]
area = h * (np.sum(y) - 0.5 * (y[0] + y[-1]))
assert abs(area - 0.4) < 1e-6, \
    f"transforming h(t) back at s=2 must return H(2) = 6/15 = 0.4, got {area}"
'''},
                ],
            },
            "quiz": {
                "title": "Reading a transfer function",
                "minutes": 9,
                "questions": [
                    {
                        "q": "$H(s) = \\dfrac{s+2}{(s+1)(s+5)}$. Its zeros and poles are:",
                        "opts": [
                            "a zero at $-1$ and $-5$, a pole at $-2$",
                            "a zero at $-2$, poles at $-1$ and $-5$",
                            "a zero at $+2$, poles at $+1$ and $+5$",
                            "poles at $-2$ and $-1$, a zero at $-5$",
                        ],
                        "a": 1,
                        "why": r'''
Zeros come from the **numerator**, poles from the **denominator**, and each is the
value of $s$ that makes its own factor vanish — so $s+2$ gives a zero at $-2$, not at
$+2$. Reading $s+2$ as a zero at $+2$ is the sign error that catches everyone once: the root
of $s + a$ is $-a$. Getting the zeros and poles the wrong way round inverts the
system: it would rise with frequency instead of falling.
''',
                    },
                    {
                        "q": "A system has poles at $-1$ and $-20$. Which term dominates the late part of the step response?",
                        "opts": [
                            "the $e^{-20t}$ term, because 20 is the larger number",
                            "both equally, because both poles are real",
                            "neither — the zero decides",
                            "the $e^{-t}$ term",
                        ],
                        "a": 3,
                        "why": r'''
$e^{-20t}$ has fallen to under a thousandth of its starting value by $t = 0.35$, while
$e^{-t}$ is still at 70% then. The **slow** pole — the one closest to the imaginary
axis — is the one still visible when everything else has gone, and it is what a
designer means by "the dominant pole". Reaching for the bigger number is the reflex worth unlearning: in the s-plane it is distance from the *imaginary axis*
that sets the speed, so the pole nearest that axis is the slow one and therefore the
one that matters. (Distance from the origin is a different measurement, and a pair like
$-1 \pm j100$ is far from the origin while still decaying slowly.)
''',
                    },
                    {
                        "q": "In $\\dfrac{6}{(s+1)(s+3)} = \\dfrac{A}{s+1} + \\dfrac{B}{s+3}$, what is $A$?",
                        "opts": ["3", "6", "$-3$", "2"],
                        "a": 0,
                        "why": r'''
Cover up the $(s+1)$ factor and evaluate what is left at $s = -1$: $6/(-1+3) = 3$.
(The residue formula $N(p)/D'(p)$ says the same thing: $D' = 2s+4$, which is 2 at
$s=-1$, and $6/2 = 3$.) $-3$ is the residue at the *other* pole — the two must sum to
zero here, because the numerator is two degrees below the denominator, and that is a
free check on your arithmetic.
''',
                    },
                    {
                        "q": "What does $\\dfrac{1}{(s+a)^2}$ invert to?",
                        "opts": ["$e^{-at}$", "$2e^{-at}$", "$te^{-at}$", "$\\tfrac{1}{2}t^2e^{-at}$"],
                        "a": 2,
                        "why": r'''
$te^{-at}$. A repeated pole is the one case the simple residue formula cannot handle —
it would divide by $D'(p)$, which is zero at a repeated root. Physically the extra
factor of $t$ is why a critically damped circuit rises more slowly at first than the
plain exponential you might expect: the response is a product of a rising ramp and a
falling exponential. The $\tfrac{1}{2}t^2$ form belongs to a pole repeated three times.
''',
                    },
                    {
                        "q": "For $H(s) = \\dfrac{K\\omega_n^2}{s^2+2\\zeta\\omega_n s + \\omega_n^2}$, what is $|H(j\\omega_n)|$?",
                        "opts": ["$K$", "$K/\\sqrt{2}$", "$2\\zeta K$", "$K/(2\\zeta)$"],
                        "a": 3,
                        "why": r'''
At $s = j\omega_n$ the terms $s^2$ and $\omega_n^2$ cancel exactly, leaving only
$2\zeta\omega_n \cdot j\omega_n$ on the bottom, so $|H| = K/(2\zeta)$ and the phase is
exactly $-90°$. $K/\sqrt{2}$ is the tempting one: $\omega_n$ is *not* the $-3$ dB point
unless $\zeta$ happens to be $1/\sqrt{2}$. With $\zeta = 0.25$ the gain there is 2 —
a gain of *two*, above the input, from a circuit containing nothing but a resistor, an
inductor and a capacitor.
''',
                    },
                    {
                        "q": "Where are the poles of a system with $\\omega_n = 2000$ rad/s and $\\zeta = 0.25$?",
                        "opts": [
                            "$-2000 \\pm j500$",
                            "$-500 \\pm j1936$",
                            "$-500 \\pm j2000$",
                            "$\\pm j2000$",
                        ],
                        "a": 1,
                        "why": r'''
The real part is $-\zeta\omega_n = -500$ and the imaginary part is
$\omega_n\sqrt{1-\zeta^2} = 2000\sqrt{0.9375} = 1936$. $-500 \pm j2000$ is the common slip of using $\omega_n$ itself as the imaginary
part — an easy mistake to forgive, since at
$\zeta = 0.25$ the difference is only 3%, but one that grows fast as the damping does.
A useful check: the poles must be exactly $\omega_n = 2000$ from the origin, and
$\sqrt{500^2 + 1936^2} = 2000$.
''',
                    },
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Matrices, linear maps and networks",
            "summary": "A matrix is not a table of numbers. It is what a linear map does to the basis vectors, and a resistor network is one.",
            "concepts": [
                "A map $T$ is **linear** when $T(av + bw) = aT(v) + bT(w)$. That single property is what makes superposition legal in circuits, and it is the only thing matrices describe.",
                "$Av$ is a **combination of the columns of $A$**, weighted by the entries of $v$. Reading a matrix–vector product column-wise rather than row-wise makes most of linear algebra obvious.",
                "The $j$-th column of the matrix of $T$ is $T(e_j)$, the image of the $j$-th basis vector. Feed a map the basis vectors one at a time and you have built its matrix.",
                "Matrix multiplication is composition: $ABv$ means do $B$, then do $A$. That is why it is associative and why it is not commutative.",
                "Nodal analysis writes KCL once per unknown node: $Gv = i$, where $v$ holds the node voltages and $i$ the currents injected from outside.",
                "$G$ is built by inspection. A resistor between nodes $a$ and $b$ adds its conductance $1/R$ to $G_{aa}$ and $G_{bb}$, and subtracts it from $G_{ab}$ and $G_{ba}$. Ground gets no row and no column, because its voltage is already known.",
                "$G$ is symmetric because a resistor conducts the same both ways, and it is diagonally dominant, which is why the equations are numerically well behaved.",
                "A node fixed by an ideal voltage source has its KCL row replaced by a single 1 and its known voltage on the right-hand side. A singular $G$ almost always means some node has no resistive path to ground.",
            ],
            "build": {
                "title": "A matched 600 Ω attenuator",
                "minutes": 28,
                "brief": r'''
Two specifications at once, which is what makes this a linear-systems problem rather
than an arithmetic one.

A 10 V source drives a network of resistors, which drives a 600 Ω load. The load and
its ground are already on the canvas, with the probe on it. Add resistors between the
source and the load so that:

- the **load voltage is exactly 5.00 V**, and
- the **source sees a resistance of 600 Ω**, so it delivers 16.67 mA.

Either condition alone is easy. Together they are not: a single 600 Ω resistor in
series gives 5 V at the load, but the source then sees 1200 Ω and delivers only
8.33 mA. Satisfying one specification breaks the other, and you have to solve for both
together.

## What is being measured

- the probe voltage, which must be 5.00 V
- the current out of the source, which must be $10/600 = 16.67$ mA. Since the source
  is ideal and sits at a fixed 10 V, that current *is* the input resistance: measuring
  16.67 mA is measuring 600 Ω, with nothing else needed.
- that the 600 Ω load is still running from the probed node to ground. A network that
  meets both numbers with the load disconnected has met neither, because the load is
  half of what determines them.

## Where to start

Two unknowns, two conditions. Call the resistor you put in series $R_s$ and the one
you put across the load $R_p$. Write down what the input resistance is in terms of
them, write down what fraction of 10 V reaches the load, set both equal to their
targets, and solve the pair.

More than one topology works. A series resistor and a shunt across the load is the
smallest answer; the symmetric three-resistor arrangement used in telephone practice —
a series resistor, a shunt to ground, and a second series resistor — also works, and
the checks accept either, because they measure the circuit rather than compare it to a
picture.

This part has a name. It is a 6 dB pad, matched to 600 Ω, and 600 Ω attenuators like
it sat in every audio and telephone rack for most of a century.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p5", "kind": "R", "x": 13, "y": 7, "rot": 1, "value": 600},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 10},
                        {"id": "p7", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 8], "b": [13, 10]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 200},
                        {"id": "p3", "kind": "R", "x": 7, "y": 7, "rot": 1, "value": 800},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 10},
                        {"id": "p8", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 200},
                        {"id": "p5", "kind": "R", "x": 13, "y": 7, "rot": 1, "value": 600},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 10},
                        {"id": "p7", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [7, 6]},
                        {"a": [7, 8], "b": [7, 10]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [13, 5]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 8], "b": [13, 10]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 10 V source drives the network", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 10, 0.001, 'the supply voltage');
'''},
                    {"name": "the 600 Ω load is still across the probed node", "code": r'''
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 600) <= 6 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'The 600 Ohm load must run from the probed node to ground. Both specifications ' +
   'depend on it being connected, so a design that meets them with the load removed ' +
   'has not met them at all.');
'''},
                    {"name": "the load receives 5.00 V", "code": r'''
c.close(c.vout(), 5.0, 0.01,
  'the voltage at the load — half the supply, which is 6 dB of attenuation');
'''},
                    {"name": "the source sees 600 Ω, so it delivers 16.67 mA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
const rin = 10.0 / i;
c.close(i, 10.0 / 600.0, 0.02,
  'the current out of the 10 V source, which is 10/600 = 16.67 mA when the input ' +
  'resistance is 600 Ohm — this circuit presents ' +
  (i > 0 ? rin.toFixed(0) + ' Ohm' : 'an open circuit'));
'''},
                ],
                "hints": [
                    "Take the series-plus-shunt answer first. With $R_s$ in series and $R_p$ across the 600 Ω load, the load node sees $R_p$ in parallel with 600; call that $X$.",
                    "The input resistance is $R_s + X$ and it must be 600. The load voltage is $10X/(R_s+X)$ and it must be 5, so $X$ is exactly half the total: $X = 300$ and therefore $R_s = 300$.",
                    "Then solve $1/300 = 1/R_p + 1/600$ for $R_p$, which gives 600 Ω. So a 300 Ω series resistor and a 600 Ω shunt resistor across the load.",
                    "For the symmetric three-resistor version instead, use 200 Ω in series, 800 Ω to ground, then 200 Ω in series into the load. Check it: $600 + 200 = 800$, in parallel with 800 gives 400, plus 200 gives 600.",
                    "If the voltage is right but the current is wrong, you have solved one equation and not the other — a plain 600 Ω series resistor is exactly that failure.",
                ],
            },
            "lab": {
                "title": "Building a matrix out of a map, and a network out of a matrix",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
This lab makes one claim concrete: **a matrix is what a linear map does to the basis
vectors, and nothing else**. Once you believe that, you never have to remember how to
assemble a conductance matrix again, because you can always recover it by asking the
circuit what it does.

- `as_matrix(f, n)` takes a linear function `f` from $\mathbb{R}^n$ to $\mathbb{R}^n$
  and returns its $n\times n$ matrix. Apply `f` to each standard basis vector in turn
  and stack the results as **columns**.
- `injected(v, resistors, n)` is a physical map. Given the node voltages `v` for nodes
  $1 \dots n$ (ground is node 0 and always 0 V), it returns the current that must be
  injected at each node from outside to hold those voltages. Each resistor `(a, b, R)`
  carries $(v_a - v_b)/R$ from `a` to `b`; that current leaves node `a` and arrives at
  node `b`, so add it to entry `a` and subtract it from entry `b`, skipping node 0.
- `solve_network(n, resistors, fixed)` solves the circuit. Build the matrix with
  `as_matrix`, replace the row of each node in `fixed` with a 1 on its diagonal and the
  known voltage on the right, solve with `np.linalg.solve`, and return the voltages
  with 0.0 prepended for ground.

The pleasing part is the third check: `injected` *is* a linear map, so running it
through `as_matrix` hands you the conductance matrix $G$ — the one the textbook builds
by the stamping rule — without you ever writing the stamping rule down.

## On indexing

Nodes are numbered from 1, arrays from 0, so node `k` lives at index `k - 1`. Ground is
node 0 and has no entry at all: `if a:` is false exactly when `a` is 0, which is the
whole guard you need.
''',
                "files": [{"name": "main.py", "content": r'''
"""A matrix is what a linear map does to the basis vectors."""

import numpy as np


def as_matrix(f, n):
    """The n-by-n matrix of the linear map f, built column by column."""
    # TODO: for each j, apply f to the j-th standard basis vector; those are the columns.
    return np.zeros((n, n))


def injected(v, resistors, n):
    """Currents that must be injected at nodes 1..n to hold the voltages v."""
    # TODO: prepend 0.0 for ground, then for each (a, b, R) add (v[a]-v[b])/R
    #       to entry a and subtract it from entry b, skipping node 0.
    return np.zeros(n)


def solve_network(n, resistors, fixed):
    """Node voltages, with 0.0 first for ground. `fixed` is {node: volts}."""
    # TODO: build G with as_matrix, replace the fixed rows, and solve.
    return np.zeros(n + 1)


if __name__ == "__main__":
    pad = [(1, 2, 200.0), (2, 0, 800.0), (2, 3, 200.0), (3, 0, 600.0)]
    v = solve_network(3, pad, {1: 10.0})
    print("node voltages:", v)
    print("supply current:", injected(v[1:], pad, 3)[0], "A")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""A matrix is what a linear map does to the basis vectors.

Verified by running this file on the attenuator from the build exercise:
    node voltages [0, 10, 6.666666666666667, 5.0]
    supply current 0.016666666666666666 A, so the input resistance is exactly 600 ohms
"""

import numpy as np


def as_matrix(f, n):
    """The n-by-n matrix of the linear map f, built column by column."""
    cols = []
    for j in range(n):
        e = np.zeros(n)
        e[j] = 1.0
        cols.append(np.asarray(f(e), dtype=float))
    return np.column_stack(cols)


def injected(v, resistors, n):
    """Currents that must be injected at nodes 1..n to hold the voltages v."""
    out = np.zeros(n)
    volts = np.concatenate(([0.0], np.asarray(v, dtype=float)))
    for (a, b, R) in resistors:
        cur = (volts[a] - volts[b]) / R
        if a:
            out[a - 1] += cur
        if b:
            out[b - 1] -= cur
    return out


def solve_network(n, resistors, fixed):
    """Node voltages, with 0.0 first for ground. `fixed` is {node: volts}."""
    G = as_matrix(lambda v: injected(v, resistors, n), n)
    rhs = np.zeros(n)
    for node, volts in fixed.items():
        G[node - 1, :] = 0.0
        G[node - 1, node - 1] = 1.0
        rhs[node - 1] = float(volts)
    return np.concatenate(([0.0], np.linalg.solve(G, rhs)))


if __name__ == "__main__":
    pad = [(1, 2, 200.0), (2, 0, 800.0), (2, 3, 200.0), (3, 0, 600.0)]
    v = solve_network(3, pad, {1: 10.0})
    print("node voltages:", v)
    print("supply current:", injected(v[1:], pad, 3)[0], "A")
'''}],
                "hints": [
                    "In `as_matrix`, make `e = np.zeros(n)` fresh inside the loop and set `e[j] = 1.0`. Reusing one array and clearing it works too, but a fresh one is harder to get wrong.",
                    "`np.column_stack(cols)` assembles a list of vectors as columns. `np.array(cols)` would stack them as *rows*, which gives you the transpose — for a symmetric $G$ the tests would still pass, so check it on the rotation instead.",
                    "In `injected`, `volts = np.concatenate(([0.0], v))` puts ground at index 0 so that `volts[a]` reads naturally for any node number including 0.",
                    "`if a:` is False only when `a == 0`, which is exactly the ground case you want to skip. Write both guards, one for each end of the resistor.",
                    "In `solve_network`, replace the fixed rows *after* building `G`, never before — the stamping has to see the whole network first.",
                ],
                "tests": [
                    {"name": "the matrix of a rotation", "code": r'''
M = as_matrix(lambda v: np.array([-v[1], v[0]]), 2)
assert M.shape == (2, 2), f"expected a 2x2 matrix, got shape {M.shape}"
want = np.array([[0.0, -1.0], [1.0, 0.0]])
assert np.allclose(M, want), \
    f"a quarter turn anticlockwise has matrix [[0,-1],[1,0]], got\n{M}\n" \
    "(if you got its transpose, the images were stacked as rows instead of columns)"
'''},
                    {"name": "injected currents obey Ohm's law", "code": r'''
i = injected([12.0], [(1, 0, 3000.0)], 1)
assert abs(i[0] - 0.004) < 1e-12, \
    f"holding one node at 12 V through 3 k to ground needs 4 mA injected, got {i[0]}"
i2 = injected([9.0, 3.0], [(1, 2, 20000.0), (2, 0, 10000.0)], 2)
assert abs(i2[0] - 0.0003) < 1e-12, f"node 1 injects (9-3)/20k = 300 uA, got {i2[0]}"
assert abs(i2[1] - 0.0) < 1e-12, \
    f"node 2 is in balance here: 300 uA in through 20k, 300 uA out through 10k, got {i2[1]}"
'''},
                    {"name": "the map recovers the conductance matrix", "code": r'''
res = [(1, 2, 20000.0), (2, 0, 10000.0)]
G = as_matrix(lambda v: injected(v, res, 2), 2)
want = np.array([[5e-05, -5e-05], [-5e-05, 1.5e-04]])
assert np.allclose(G, want), \
    f"the conductance matrix should be\n{want}\ngot\n{G}"
assert np.allclose(G, G.T), "a resistor network always gives a symmetric matrix"
'''},
                    {"name": "the attenuator from the build exercise", "code": r'''
pad = [(1, 2, 200.0), (2, 0, 800.0), (2, 3, 200.0), (3, 0, 600.0)]
v = solve_network(3, pad, {1: 10.0})
assert len(v) == 4, f"three unknown nodes plus ground is four voltages, got {len(v)}"
assert abs(v[0]) < 1e-12, "node 0 is ground and must be exactly 0 V"
assert abs(v[1] - 10.0) < 1e-9, f"node 1 is held at 10 V by the source, got {v[1]}"
assert abs(v[2] - 6.666666666666667) < 1e-9, f"the middle node sits at 6.667 V, got {v[2]}"
assert abs(v[3] - 5.0) < 1e-9, f"the load must see 5.00 V, got {v[3]}"
isup = injected(v[1:], pad, 3)[0]
assert abs(isup - 0.016666666666666666) < 1e-12, \
    f"10 V into 600 ohms is 16.667 mA, got {isup} A"
'''},
                    {"name": "a ladder, and KCL at every free node", "code": r'''
lad = [(1, 2, 1000.0), (2, 0, 1000.0), (2, 3, 1000.0), (3, 0, 1000.0)]
v = solve_network(3, lad, {1: 10.0})
assert abs(v[2] - 4.0) < 1e-9, f"node 2 should sit at 4 V, got {v[2]}"
assert abs(v[3] - 2.0) < 1e-9, f"node 3 should sit at 2 V, got {v[3]}"
i = injected(v[1:], lad, 3)
assert abs(i[1]) < 1e-12 and abs(i[2]) < 1e-12, \
    f"nothing is injected at nodes 2 and 3, so KCL must balance there; got {i}"
assert abs(i[0] - 0.006) < 1e-12, f"the supply delivers 6 mA, got {i[0]}"
'''},
                ],
            },
            "quiz": {
                "title": "Maps, matrices and node equations",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The clearest way to read the product $Av$ is:",
                        "opts": [
                            "as a lookup in a table of numbers",
                            "as a rotation of $v$, always",
                            "as a system of equations with no meaning on its own",
                            "as a combination of the columns of $A$, weighted by the entries of $v$",

                        ],
                        "a": 3,
                        "why": r'''
$Av = v_1a_1 + v_2a_2 + \dots$, where $a_j$ is the $j$-th column. Every later idea gets
easier from this reading: the column space is the set of reachable outputs, a singular
matrix is one whose columns fail to span, and the matrix of a composition is the second
map applied to the first one's columns. Rotations are one particular family of linear
maps, not what matrices are.
''',
                    },
                    {
                        "q": "How do you find the $j$-th column of the matrix of a linear map $T$?",
                        "opts": [
                            "apply $T$ to the vector of all ones",
                            "compute $T(e_j)$, the image of the $j$-th basis vector",
                            "take the $j$-th row of the inverse",
                            "take the $j$-th eigenvector",
                        ],
                        "a": 1,
                        "why": r'''
$Ae_j$ selects column $j$ exactly, so if $A$ is to represent $T$ then column $j$ must
be $T(e_j)$. This is the entire recipe for turning a map into a matrix, and it is what
the lab does. Applying $T$ to the vector of all ones discards the information: it gives one
vector, the sum of all the columns, from which the individual columns cannot be
recovered.
''',
                    },
                    {
                        "q": "Nodal analysis of a resistor network with $n$ unknown node voltages produces:",
                        "opts": [
                            "$n$ nonlinear equations",
                            "one equation for each resistor",
                            "$n$ linear equations, one per node, each of them KCL at that node",
                            "$n$ linear equations, one per loop, each of them KVL round that loop",
                        ],
                        "a": 2,
                        "why": r'''
One unknown per node, one equation per node, and each equation says that the currents
leaving that node sum to zero — Kirchhoff's current law. They are linear because Ohm's
law is. The loop-based alternative, one KVL equation per loop, is mesh analysis, which is a real method
but a different one, with one unknown per loop instead. Counting equations against
unknowns before starting is the cheapest way to catch a mistake in the setup.
''',
                    },
                    {
                        "q": "Why is the conductance matrix $G$ symmetric?",
                        "opts": [
                            "because a resistor conducts equally in both directions, so what it contributes to $G_{ab}$ it also contributes to $G_{ba}$",
                            "because every network is a ladder",
                            "because the supply is ideal",
                            "because conductance is a positive number",
                        ],
                        "a": 0,
                        "why": r'''
The stamping rule subtracts the same $1/R$ from $G_{ab}$ and from $G_{ba}$, and it does
so because the component itself has no preferred direction. Symmetry is therefore a
statement about the physics, and it is worth using: it halves the work of writing the
matrix down, and it fails the moment you add a component that *does* have a direction,
such as a transistor or a dependent source.
''',
                    },
                    {
                        "q": "Your solver reports that $G$ is singular. The most likely cause is:",
                        "opts": [
                            "too many resistors in the network",
                            "resistor values that are too large",
                            "a negative resistor value",
                            "a node with no resistive path to ground, so nothing determines its voltage",
                        ],
                        "a": 3,
                        "why": r'''
A floating node — one connected only through capacitors, or left dangling, or attached
to a section that is itself isolated — has no equation that pins it, so infinitely many
voltage vectors satisfy the system and the matrix has no inverse. It is the same
failure the schematic editor reports as "under-determined". Very large resistances make
the matrix badly *conditioned*, which is a numerical accuracy problem, not the same
thing as singular.
''',
                    },
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Eigenvalues and least squares",
            "summary": "The directions a matrix leaves alone are its poles in disguise; and when there are more measurements than unknowns, the best you can do is minimise what is left over.",
            "concepts": [
                "$Av = \\lambda v$ with $v \\ne 0$ says the map leaves the *direction* of $v$ alone and only stretches it. $\\lambda$ is the eigenvalue and $v$ the eigenvector.",
                "The eigenvalues are the roots of $\\det(A - \\lambda I) = 0$. For a $2\\times2$ matrix that polynomial is $\\lambda^2 - (\\text{trace})\\lambda + \\det$, which is often quicker than expanding.",
                "Write a circuit as $\\dot{x} = Ax$ and the eigenvalues of $A$ are exactly the poles of its transfer function. The same numbers, reached from two directions.",
                "So the stability rule is the same rule: every eigenvalue must have a strictly negative real part. Negative *magnitude* is not the test, and complex eigenvalues are ordinary.",
                "With more measurements than unknowns, $Ac = y$ generally has no solution. **Least squares** picks the $c$ that minimises $\\|Ac - y\\|^2$.",
                "The minimum occurs when the residual is perpendicular to every column of $A$, which is $A^\\top(Ac - y) = 0$, giving the **normal equations** $A^\\top A c = A^\\top y$.",
                "Fitting a polynomial is least squares with $A_{ij} = x_i^j$. Fitting an exponential decay is least squares on $\\ln v$, which turns $Ae^{-t/\\tau}$ into a straight line of slope $-1/\\tau$.",
                "The residuals are the diagnosis. Scatter about zero means noise, and the fit is as good as the data allows. A smooth trend in the residuals means the *model* is wrong, and no amount of extra data will fix it.",
            ],
            "lab": {
                "title": "Fitting a model to measurements",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Five short functions: two about eigenvalues, three about least squares.

- `design_matrix(x, deg)` returns the matrix whose column $j$ is $x^j$, for
  $j = 0 \dots \text{deg}$. Its first column is therefore all ones.
- `least_squares(A, y)` solves the normal equations $A^\top A c = A^\top y$ with
  `np.linalg.solve` and returns `c`.
- `fit_poly(x, y, deg)` puts the two together and returns the coefficients in
  **ascending** powers, so `[2.0, 3.0]` means $2 + 3x$.
- `time_constant(t, v)` fits a decaying exponential $v = Ae^{-t/\tau}$ by fitting a
  straight line to $\ln v$ and returns $\tau$. The slope of that line is $-1/\tau$.
- `eigenvalues(A)` returns the eigenvalues of `A` from `np.linalg.eigvals`, sorted by
  real part, smallest first.

## Why the normal equations and not the inverse

`A` is tall — more rows than columns — so it has no inverse and `np.linalg.solve(A, y)`
will refuse it outright. $A^\top A$, on the other hand, is square and (for independent
columns) invertible, and solving with it gives the vector that minimises the sum of the
squared residuals. That is the whole of least squares in one line of code and one line
of geometry: make the residual perpendicular to everything the columns of $A$ can
reach.

Use `np.linalg.solve` on the normal equations rather than forming an inverse. The two
are mathematically identical and the first is both faster and better behaved.
''',
                "files": [{"name": "main.py", "content": r'''
"""Eigenvalues, and fitting a model to more data than it has parameters."""

import numpy as np


def design_matrix(x, deg):
    """Matrix whose column j is x**j, for j = 0..deg."""
    # TODO: np.column_stack over a list comprehension of powers.
    return np.zeros((len(x), deg + 1))


def least_squares(A, y):
    """Solve the normal equations A^T A c = A^T y and return c."""
    # TODO: form both sides with the transpose, then np.linalg.solve.
    return np.zeros(np.asarray(A).shape[1])


def fit_poly(x, y, deg):
    """Least-squares polynomial coefficients, ascending powers."""
    # TODO: design_matrix, then least_squares.
    return np.zeros(deg + 1)


def time_constant(t, v):
    """Time constant of v = A exp(-t / tau), by fitting a line to log(v)."""
    # TODO: fit a straight line to np.log(v); the slope is -1/tau.
    return 0.0


def eigenvalues(A):
    """Eigenvalues of A, sorted by real part, smallest first."""
    # TODO: np.linalg.eigvals, then sort with np.argsort on the real parts.
    return np.array([])


if __name__ == "__main__":
    x = np.array([0.0, 1.0, 2.0, 3.0])
    print("fit of 2 + 3x:", fit_poly(x, 2.0 + 3.0 * x, 1))
    print("poles of the RLC as a state matrix:", eigenvalues([[0.0, 1.0], [-4e6, -1000.0]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Eigenvalues, and fitting a model to more data than it has parameters.

Verified by running this file:
    fit_poly on exact data for 2 + 3x returns [2. 3.]
    the state matrix [[0,1],[-4e6,-1000]] has eigenvalues -500 +/- 1936.4916731j,
    which are precisely the poles of the RLC filter built in module 2
"""

import numpy as np


def design_matrix(x, deg):
    """Matrix whose column j is x**j, for j = 0..deg."""
    x = np.asarray(x, dtype=float)
    return np.column_stack([x ** j for j in range(deg + 1)])


def least_squares(A, y):
    """Solve the normal equations A^T A c = A^T y and return c."""
    A = np.asarray(A, dtype=float)
    y = np.asarray(y, dtype=float)
    return np.linalg.solve(A.T @ A, A.T @ y)


def fit_poly(x, y, deg):
    """Least-squares polynomial coefficients, ascending powers."""
    return least_squares(design_matrix(x, deg), y)


def time_constant(t, v):
    """Time constant of v = A exp(-t / tau), by fitting a line to log(v)."""
    coeffs = fit_poly(t, np.log(np.asarray(v, dtype=float)), 1)
    return -1.0 / coeffs[1]


def eigenvalues(A):
    """Eigenvalues of A, sorted by real part, smallest first."""
    w = np.linalg.eigvals(np.asarray(A, dtype=float))
    return w[np.argsort(w.real)]


if __name__ == "__main__":
    x = np.array([0.0, 1.0, 2.0, 3.0])
    print("fit of 2 + 3x:", fit_poly(x, 2.0 + 3.0 * x, 1))
    print("poles of the RLC as a state matrix:", eigenvalues([[0.0, 1.0], [-4e6, -1000.0]]))
'''}],
                "hints": [
                    "`design_matrix` is `np.column_stack([x ** j for j in range(deg + 1)])` once `x` is a float array. Column 0 comes out as all ones because anything to the power 0 is 1.",
                    "In `least_squares`, `A.T @ A` and `A.T @ y` are the two sides; hand both to `np.linalg.solve`. Never call `np.linalg.inv`.",
                    "`time_constant` fits `np.log(v)` against `t` with `deg=1`. The result is `[ln A, -1/tau]`, so return `-1.0 / coeffs[1]`.",
                    "For `eigenvalues`, `np.argsort(w.real)` gives the order and `w[order]` applies it. Sorting the complex numbers directly is an error in NumPy, which is why the sort is on the real parts.",
                    "If a fit comes back wildly wrong, print `design_matrix(x, deg)` and look at it. A common slip is building the columns in descending powers, which returns the coefficients in the reverse order to the one the checks expect.",
                ],
                "tests": [
                    {"name": "the design matrix has a column of ones first", "code": r'''
A = design_matrix([0.0, 1.0, 2.0], 1)
want = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
assert A.shape == (3, 2), f"three points and degree 1 gives a 3x2 matrix, got {A.shape}"
assert np.allclose(A, want), f"expected\n{want}\ngot\n{A}"
B = design_matrix([2.0, 3.0], 2)
assert np.allclose(B, np.array([[1.0, 2.0, 4.0], [1.0, 3.0, 9.0]])), \
    f"columns must be x^0, x^1, x^2 in that order, got\n{B}"
'''},
                    {"name": "an exact fit is recovered exactly", "code": r'''
x = np.array([0.0, 1.0, 2.0, 3.0])
c = fit_poly(x, 2.0 + 3.0 * x, 1)
assert abs(c[0] - 2.0) < 1e-9 and abs(c[1] - 3.0) < 1e-9, \
    f"y = 2 + 3x should give [2, 3] in ascending order, got {c}"
q = fit_poly(np.array([-2.0, -1.0, 0.0, 1.0, 2.0]), np.array([4.0, 1.0, 0.0, 1.0, 4.0]), 2)
assert np.allclose(q, [0.0, 0.0, 1.0], atol=1e-9), \
    f"y = x^2 should give [0, 0, 1], got {q}"
'''},
                    {"name": "least squares balances errors it cannot remove", "code": r'''
x = np.array([0.0, 1.0, 2.0, 3.0])
y = 2.0 + 3.0 * x + np.array([1.0, -1.0, -1.0, 1.0])
c = fit_poly(x, y, 1)
assert abs(c[0] - 2.0) < 1e-9 and abs(c[1] - 3.0) < 1e-9, \
    f"these errors are balanced, so the fit should still be [2, 3], got {c}"
r = y - design_matrix(x, 1) @ c
assert abs(np.sum(r)) < 1e-9, f"the residual must be perpendicular to the ones column, got sum {np.sum(r)}"
assert abs(float(x @ r)) < 1e-9, f"and perpendicular to the x column, got {float(x @ r)}"
'''},
                    {"name": "a time constant out of measured decay", "code": r'''
t = np.array([0.0, 1e-3, 2e-3, 3e-3])
tau = time_constant(t, 5.0 * np.exp(-t / 0.002))
assert abs(tau - 0.002) < 1e-9, f"this data decays with tau = 2 ms, got {tau}"
t2 = np.linspace(0.0, 0.05, 11)
tau2 = time_constant(t2, 12.0 * np.exp(-t2 / 0.01))
assert abs(tau2 - 0.01) < 1e-9, f"and this one with tau = 10 ms, got {tau2}"
'''},
                    {"name": "eigenvalues, and the poles they turn out to be", "code": r'''
w = eigenvalues([[0.0, 1.0], [-3.0, -4.0]])
assert len(w) == 2, f"a 2x2 matrix has two eigenvalues, got {len(w)}"
assert abs(w[0].real + 3.0) < 1e-9 and abs(w[1].real + 1.0) < 1e-9, \
    f"lambda^2 + 4 lambda + 3 has roots -3 and -1, sorted that way, got {w}"
z = eigenvalues([[0.0, 1.0], [-4e6, -1000.0]])
assert abs(z[0].real + 500.0) < 1e-6, \
    f"the real part should be -zeta*wn = -500, got {z[0].real}"
assert abs(abs(z[0].imag) - 1936.4916731037085) < 1e-6, \
    f"the imaginary part should be wn*sqrt(1-zeta^2) = 1936.49, got {abs(z[0].imag)}"
'''},
                ],
            },
            "quiz": {
                "title": "Eigenvalues, fits and residuals",
                "minutes": 8,
                "questions": [
                    {
                        "q": "$Av = \\lambda v$ with $v \\ne 0$ says that:",
                        "opts": [
                            "the map leaves the direction of $v$ alone and only scales it",
                            "$v$ is in the null space of $A$",
                            "$A$ must be diagonal",
                            "$\\lambda$ is the determinant of $A$",
                        ],
                        "a": 0,
                        "why": r'''
An eigenvector is a direction the map does not turn. Everything else is consequence:
along that direction the matrix behaves like a single number, which is why writing a
system in its eigenvector coordinates decouples it into independent first-order pieces.
"$v$ is in the null space of $A$" is the special case $\lambda = 0$, not the
definition. The determinant is the
*product* of all the eigenvalues, and the trace is their sum.
''',
                    },
                    {
                        "q": "What are the eigenvalues of $A = \\begin{bmatrix}0 & 1\\\\ -3 & -4\\end{bmatrix}$?",
                        "opts": ["0 and $-4$", "$-2$ and $-2$", "$-1$ and $-3$", "1 and 3"],
                        "a": 2,
                        "why": r'''
The characteristic polynomial is $\lambda^2 - (\text{trace})\lambda + \det =
\lambda^2 + 4\lambda + 3$, whose roots are $-1$ and $-3$. Answering 0 and $-4$ reads the diagonal straight off, which is correct only for a
triangular matrix and wrong here. Notice what
this matrix is: the companion form of $\ddot{y}+4\dot{y}+3y=0$, and its eigenvalues are
exactly the poles of $1/(s^2+4s+3)$ from module 2.
''',
                    },
                    {
                        "q": "For $\\dot{x} = Ax$, the state returns to zero from every starting point exactly when:",
                        "opts": [
                            "every eigenvalue is negative in magnitude",
                            "every eigenvalue has a strictly negative real part",
                            "the trace of $A$ is zero",
                            "$A$ is invertible",
                        ],
                        "a": 1,
                        "why": r'''
Each eigenvalue contributes $e^{\lambda t}$, whose size is $e^{(\text{Re}\lambda)t}$,
so only the real part decides decay. "Negative in magnitude" is not even well formed — a magnitude is never negative, and eigenvalues are routinely complex. An invertible $A$ merely has no
zero eigenvalue, which does not stop the others sitting in the right half-plane; an
undamped oscillator has purely imaginary eigenvalues, a zero trace, and never settles.
''',
                    },
                    {
                        "q": "Least squares fits $Ac \\approx y$ when $A$ is tall by:",
                        "opts": [
                            "inverting $A$",
                            "minimising the largest single error",
                            "choosing $c$ to make the residual as large as possible",
                            "minimising the sum of the squared residuals, which gives $A^\\top A c = A^\\top y$",
                        ],
                        "a": 3,
                        "why": r'''
A tall $A$ has no inverse, which is precisely why the problem needs a different idea.
Minimising $\|Ac-y\|^2$ is a smooth problem with a closed-form answer: differentiate,
set to zero, and out come the normal equations. Geometrically, it projects $y$ onto the
column space of $A$ and leaves the residual perpendicular to it. Minimising the largest single error is a real and useful alternative criterion — but it is a different
method with no such formula.
''',
                    },
                    {
                        "q": "You fit a straight line to 50 measured (I, V) pairs. The residuals are small, but plotted against I they trace a smooth curve rather than scattering about zero. What does that tell you?",
                        "opts": [
                            "the model is wrong — a straight line cannot describe this data, and the mismatch is systematic rather than random",
                            "the measurements are too noisy",
                            "the fit is as good as it can be",
                            "the normal equations were solved incorrectly",
                        ],
                        "a": 0,
                        "why": r'''
Structure in the residuals is the signature of a missing term. Noise scatters; a real
physical effect the model omits — a component heating up, a diode drop, a small
nonlinearity — leaves a smooth pattern behind. Collecting more data will shrink the
random part and leave the pattern exactly where it is. Always plot the residuals: the
fitted parameters cannot tell you that the model itself was the wrong shape, and the
sum of squares alone cannot either.
''',
                    },
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Identify an unknown circuit from its measured step response",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Everything in this course pointing in one direction: someone hands you a black box and
a measurement, and you have to say what is inside it.

The box contains a series RLC low-pass — the circuit you built in module 2 — but with
unknown component values. The measurement is its step response, sampled at even
intervals. You have to recover $\omega_n$ and $\zeta$ from those samples, turn them
into component values, and state where the poles are.

## The idea that makes it a linear problem

The response satisfies

$$\ddot{y} + 2\zeta\omega_n\dot{y} + \omega_n^2 y = \omega_n^2 u$$

with $u = 1$ after the switch closes. Write $e = y - 1$, the error from the final
value, and the driving term disappears:

$$\ddot{e} + a\dot{e} + b e = 0, \qquad a = 2\zeta\omega_n,\quad b = \omega_n^2$$

Estimate $\dot{e}$ and $\ddot{e}$ from the samples by central differences,

```text
edot[i]  = (e[i+1] - e[i-1]) / (2h)
eddot[i] = (e[i+1] - 2 e[i] + e[i-1]) / h**2
```

and every interior sample then gives you one equation in the two unknowns $a$ and $b$:

$$\begin{bmatrix}\dot{e}_i & e_i\end{bmatrix}\begin{bmatrix}a\\b\end{bmatrix} = -\ddot{e}_i$$

Thousands of samples, two unknowns. That is a tall system with no exact solution, and
least squares is exactly the tool for it. Then $\omega_n = \sqrt{b}$ and
$\zeta = a/(2\omega_n)$.

## What you are given

`bench.py` is read-only and simulates the box. `bench.simulate(wn, zeta, t)` integrates
the differential equation with a fourth-order Runge–Kutta step and returns the samples
a measurement would produce. It is deliberately a *different* method from the closed
form you will write, so when the two agree that agreement means something.

## Suggested order

Get `rlc_model` and `component_values` working first — they are two lines each and they
let you check that your algebra from module 2 is right. Then `poles`, then
`step_samples`, and check it against `bench.simulate`; if those two disagree the fault
is in your closed form, not in the identification. Leave `identify` until last, and
test it on data you generated yourself with known values before trusting it on
anything else.

Only the standard library and NumPy. No `scipy`, no fitting library — the point is that
you can do this with a matrix and a solve.
''',
        "deliverables": [
            "`rlc_model(R, L, C)`, returning the pair $(\\omega_n, \\zeta)$ for a series RLC with the output across the capacitor, from the relations derived in module 2.",
            "`component_values(wn, zeta, L)`, the inverse design step: given the two behavioural numbers and a chosen inductor, return the resistance and capacitance that produce them.",
            "`poles(wn, zeta)`, returning the two complex poles $-\\zeta\\omega_n \\pm j\\omega_n\\sqrt{1-\\zeta^2}$ as a NumPy array.",
            "`step_samples(wn, zeta, t)`, the closed-form underdamped step response evaluated on an array of times, agreeing with the independent Runge–Kutta simulation in `bench.py` to better than $10^{-6}$.",
            "`identify(t, y)`, recovering $(\\omega_n, \\zeta)$ from uniformly sampled step-response data by central differences and a least-squares solve of the normal equations, to within 0.5% on clean data.",
        ],
        "constraints": [
            "NumPy and the standard library only. No scipy, no curve-fitting package, and no polynomial-fitting helper such as `numpy.polyfit` — build the design matrix and solve the normal equations yourself.",
            "Do not edit `bench.py`. It stands in for the instrument, and a solution that changes the instrument to suit the answer has proved nothing.",
            "`identify` may assume the samples are evenly spaced and that the step was applied at $t = 0$, but not that it already knows $\\omega_n$ or $\\zeta$ — no constants from the checks may appear in it.",
            "`step_samples` need only handle the underdamped case $0 < \\zeta < 1$.",
            "Every function must work for any values in range, not only the ones the checks happen to use.",
        ],
        "rubric": [
            {"criterion": "Model and inverse design", "weight": 20,
             "evidence": "rlc_model and component_values are exact inverses of each other, and reproduce the 100 Ω, 0.1 H, 2.5 µF filter from module 2 in both directions."},
            {"criterion": "Closed-form response", "weight": 25,
             "evidence": "step_samples matches the independent Runge–Kutta simulation across the whole record, and reproduces the textbook overshoot and time to peak for the damping used."},
            {"criterion": "Identification by least squares", "weight": 35,
             "evidence": "identify recovers ωn and ζ to within 0.5% on at least three different systems and two different sample spacings, using central differences and a solve of the normal equations rather than a fitting library."},
            {"criterion": "Poles and the round trip", "weight": 20,
             "evidence": "poles returns the correct conjugate pair, and identifying a simulated record then converting back through component_values returns the component values the record was generated from."},
        ],
        "hints": [
            "`component_values` is $C = 1/(\\omega_n^2 L)$ and $R = 2\\zeta\\sqrt{L/C}$. Compute $C$ first, then use it.",
            "In `step_samples`, let `wd = wn * np.sqrt(1 - zeta**2)`; the response is $1 - e^{-\\zeta\\omega_n t}\\left(\\cos\\omega_d t + \\frac{\\zeta}{\\sqrt{1-\\zeta^2}}\\sin\\omega_d t\\right)$.",
            "Central differences are only defined at interior samples, so all three arrays in `identify` must be trimmed to the same length: `e[1:-1]` pairs with differences built from `e[2:]` and `e[:-2]`.",
            "Build `A = np.column_stack([edot, e[1:-1]])` and solve `A.T @ A c = A.T @ (-eddot)`. Then `wn = np.sqrt(c[1])` and `zeta = c[0] / (2 * wn)`.",
            "If `identify` returns a plausible ωn but a ζ that is out by a factor of two, check whether you divided by $2\\omega_n$ or by $\\omega_n$ — the fitted coefficient is $2\\zeta\\omega_n$, not $\\zeta\\omega_n$.",
            "If it returns nonsense, print the first few entries of `edot` and `eddot`. The usual cause is dividing by `h` where the second difference needs `h**2`.",
        ],
        "files": [
            {"name": "bench.py", "ro": True, "content": r'''
"""The instrument. Do not edit.

`simulate` integrates

    y'' + 2 zeta wn y' + wn^2 y = wn^2,     y(0) = 0,  y'(0) = 0

with a fourth-order Runge-Kutta step and returns the samples an oscilloscope would
record. It is deliberately a different method from the closed form you are asked to
write, so that agreement between the two is evidence rather than a tautology.
"""

import numpy as np


def simulate(wn, zeta, t):
    """Step response sampled at the times in `t`, by RK4 on the state equations."""
    t = np.asarray(t, dtype=float)
    y = np.zeros(t.shape)
    state = np.array([0.0, 0.0])

    def deriv(s):
        return np.array([s[1], wn * wn * (1.0 - s[0]) - 2.0 * zeta * wn * s[1]])

    for k in range(1, len(t)):
        h = t[k] - t[k - 1]
        k1 = deriv(state)
        k2 = deriv(state + 0.5 * h * k1)
        k3 = deriv(state + 0.5 * h * k2)
        k4 = deriv(state + h * k3)
        state = state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        y[k] = state[0]
    return y
'''},
            {"name": "main.py", "content": r'''
"""Identify an unknown series RLC from its measured step response."""

import numpy as np

import bench


def rlc_model(R, L, C):
    """Return (wn, zeta) for a series RLC with the output taken across C."""
    # TODO: wn = 1/sqrt(LC), zeta = (R/2) sqrt(C/L).
    return (0.0, 0.0)


def component_values(wn, zeta, L):
    """Return (R, C) that give this wn and zeta with the chosen inductor L."""
    # TODO: C from wn and L first, then R from zeta and the ratio L/C.
    return (0.0, 0.0)


def poles(wn, zeta):
    """The two closed-loop poles, as a NumPy array of complex numbers."""
    # TODO: -zeta*wn +/- j*wn*sqrt(1 - zeta**2).
    return np.array([])


def step_samples(wn, zeta, t):
    """Closed-form underdamped step response, evaluated on the array t."""
    # TODO: 1 - exp(-zeta wn t) (cos(wd t) + zeta/sqrt(1-zeta^2) sin(wd t)).
    return np.zeros(np.asarray(t, dtype=float).shape)


def identify(t, y):
    """Recover (wn, zeta) from evenly sampled step-response data."""
    # TODO: e = y - 1; central differences for edot and eddot; then least squares
    #       on [edot, e] c = -eddot, and read wn and zeta out of c.
    return (0.0, 0.0)


if __name__ == "__main__":
    t = np.linspace(0.0, 0.02, 4001)
    measured = bench.simulate(2000.0, 0.25, t)
    print("identified (wn, zeta):", identify(t, measured))
    print("poles:", poles(2000.0, 0.25))
    print("R, C for L = 0.1 H:", component_values(2000.0, 0.25, 0.1))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""Identify an unknown series RLC from its measured step response.

Verified by running this file:
    identify on bench.simulate(2000, 0.25) over 0..20 ms with 4001 samples returns
    wn = 1999.9895832701584, zeta = 0.25000078118388036 — five parts per million
    out on wn and three on zeta.
    The closed form and the Runge-Kutta simulation agree to 2.0e-13 over the record.
    component_values(2000, 0.25, 0.1) gives exactly (100.0, 2.5e-06).
"""

import numpy as np

import bench


def rlc_model(R, L, C):
    """Return (wn, zeta) for a series RLC with the output taken across C."""
    wn = 1.0 / np.sqrt(L * C)
    zeta = 0.5 * R * np.sqrt(C / L)
    return (wn, zeta)


def component_values(wn, zeta, L):
    """Return (R, C) that give this wn and zeta with the chosen inductor L."""
    C = 1.0 / (wn * wn * L)
    R = 2.0 * zeta * np.sqrt(L / C)
    return (R, C)


def poles(wn, zeta):
    """The two closed-loop poles, as a NumPy array of complex numbers."""
    wd = wn * np.sqrt(1.0 - zeta * zeta)
    return np.array([complex(-zeta * wn, wd), complex(-zeta * wn, -wd)])


def step_samples(wn, zeta, t):
    """Closed-form underdamped step response, evaluated on the array t."""
    t = np.asarray(t, dtype=float)
    root = np.sqrt(1.0 - zeta * zeta)
    wd = wn * root
    envelope = np.exp(-zeta * wn * t)
    return 1.0 - envelope * (np.cos(wd * t) + (zeta / root) * np.sin(wd * t))


def identify(t, y):
    """Recover (wn, zeta) from evenly sampled step-response data."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    h = t[1] - t[0]
    e = y - 1.0

    edot = (e[2:] - e[:-2]) / (2.0 * h)
    eddot = (e[2:] - 2.0 * e[1:-1] + e[:-2]) / (h * h)

    A = np.column_stack([edot, e[1:-1]])
    rhs = -eddot
    c = np.linalg.solve(A.T @ A, A.T @ rhs)

    wn = np.sqrt(c[1])
    zeta = c[0] / (2.0 * wn)
    return (wn, zeta)


if __name__ == "__main__":
    t = np.linspace(0.0, 0.02, 4001)
    measured = bench.simulate(2000.0, 0.25, t)
    print("identified (wn, zeta):", identify(t, measured))
    print("poles:", poles(2000.0, 0.25))
    print("R, C for L = 0.1 H:", component_values(2000.0, 0.25, 0.1))
'''},
        ],
        "tests": [
            {"name": "the model and its inverse agree with module 2", "code": r'''
wn, zeta = rlc_model(100.0, 0.1, 2.5e-6)
assert abs(wn - 2000.0) < 1e-6, f"1/sqrt(0.1 * 2.5e-6) is 2000 rad/s, got {wn}"
assert abs(zeta - 0.25) < 1e-9, f"(R/2) sqrt(C/L) is 0.25 here, got {zeta}"
R, C = component_values(2000.0, 0.25, 0.1)
assert abs(R - 100.0) < 1e-6, f"the design step should return R = 100 ohms, got {R}"
assert abs(C - 2.5e-6) < 1e-12, f"and C = 2.5 uF, got {C}"
w2, z2 = rlc_model(R, 0.1, C)
assert abs(w2 - 2000.0) < 1e-6 and abs(z2 - 0.25) < 1e-9, \
    f"the two functions must be exact inverses; round trip gave ({w2}, {z2})"
'''},
            {"name": "the poles sit where the pole picture says", "code": r'''
p = poles(2000.0, 0.25)
assert len(p) == 2, f"a second-order system has two poles, got {len(p)}"
assert abs(p[0].real + 500.0) < 1e-9, f"the real part is -zeta*wn = -500, got {p[0].real}"
assert abs(abs(p[0].imag) - 1936.4916731037085) < 1e-6, \
    f"the imaginary part is wn*sqrt(1-zeta^2) = 1936.4917, got {abs(p[0].imag)}"
assert abs(p[0].imag + p[1].imag) < 1e-9, "the pair must be conjugate"
assert abs(abs(p[0]) - 2000.0) < 1e-9, \
    f"both poles are exactly wn from the origin, got {abs(p[0])}"
'''},
            {"name": "the closed form agrees with the instrument", "code": r'''
t = np.linspace(0.0, 0.01, 10001)
mine = step_samples(2000.0, 0.25, t)
theirs = bench.simulate(2000.0, 0.25, t)
err = float(np.max(np.abs(mine - theirs)))
assert err < 1e-6, \
    f"the closed form and the Runge-Kutta simulation must agree; largest gap {err}"
t2 = np.linspace(0.0, 0.05, 5001)
err2 = float(np.max(np.abs(step_samples(800.0, 0.6, t2) - bench.simulate(800.0, 0.6, t2))))
assert err2 < 1e-6, f"and again for a different, better damped system; largest gap {err2}"
'''},
            {"name": "the response has the overshoot the damping predicts", "code": r'''
t = np.linspace(0.0, 0.05, 50001)
y = step_samples(2000.0, 0.25, t)
assert abs(y[0]) < 1e-12, f"the response starts at 0, got {y[0]}"
assert abs(y[-1] - 1.0) < 1e-6, f"and settles at 1, got {y[-1]}"
want_peak = 1.0 + np.exp(-np.pi * 0.25 / np.sqrt(1.0 - 0.0625))
assert abs(float(np.max(y)) - want_peak) < 1e-4, \
    f"the overshoot should be exp(-pi zeta / sqrt(1-zeta^2)), peaking at {want_peak}, got {np.max(y)}"
t_peak = t[int(np.argmax(y))]
assert abs(t_peak - np.pi / 1936.4916731037085) < 2e-6, \
    f"the peak should arrive at pi/wd = 1.6223 ms, got {t_peak} s"
'''},
            {"name": "identification recovers the system it was given", "code": r'''
t = np.linspace(0.0, 0.02, 4001)
wn, zeta = identify(t, bench.simulate(2000.0, 0.25, t))
assert abs(wn - 2000.0) / 2000.0 < 0.005, f"expected wn near 2000 rad/s, got {wn}"
assert abs(zeta - 0.25) / 0.25 < 0.005, f"expected zeta near 0.25, got {zeta}"
'''},
            {"name": "it works on other systems and other sample spacings", "code": r'''
t2 = np.linspace(0.0, 0.03, 6001)
w2, z2 = identify(t2, bench.simulate(800.0, 0.6, t2))
assert abs(w2 - 800.0) / 800.0 < 0.005, f"expected wn near 800 rad/s, got {w2}"
assert abs(z2 - 0.6) / 0.6 < 0.005, f"expected zeta near 0.6, got {z2}"
t3 = np.linspace(0.0, 0.02, 1001)
assert abs((t3[1] - t3[0]) - 2e-05) < 1e-12, "this record is sampled every 20 us"
w3, z3 = identify(t3, bench.simulate(1500.0, 0.1, t3))
assert abs(w3 - 1500.0) / 1500.0 < 0.005, \
    f"expected wn near 1500 rad/s on the coarser 20 us grid, got {w3}"
assert abs(z3 - 0.1) / 0.1 < 0.005, \
    f"expected zeta near 0.1 on the coarser 20 us grid, got {z3}"
'''},
            {"name": "the whole round trip, from record back to components", "code": r'''
t = np.linspace(0.0, 0.02, 4001)
record = bench.simulate(2000.0, 0.25, t)
wn, zeta = identify(t, record)
R, C = component_values(wn, zeta, 0.1)
assert abs(R - 100.0) / 100.0 < 0.01, f"the box should come back as a 100 ohm resistor, got {R}"
assert abs(C - 2.5e-6) / 2.5e-6 < 0.01, f"and a 2.5 uF capacitor, got {C}"
p = poles(wn, zeta)
assert abs(p[0].real + 500.0) < 5.0, f"with poles near -500 +/- j1936, got {p[0]}"
'''},
        ],
    },
}
