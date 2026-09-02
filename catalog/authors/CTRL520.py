"""CTRL520 — Optimal Estimation and Control.

Second unit of the control track. CTRL510 left the learner able to place poles and
build a Luenberger observer; this one replaces the guessing with a cost functional
and a noise model, and shows that the two problems are the same problem twice.

Authoring rules, unchanged from CTRL510:

  * every multi-line body is r'''...''' opening on a newline, never the double-quote
    form — the code samples contain docstrings that would close the block early
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

One trap worth recording, found by running the answers through the checker's own
latexToPy: a \\sqrt inside a \\frac argument does not resolve, because the fraction
pass runs before the radical pass and its {...} groups cannot nest. Every answer
below is written so no radical sits inside a fraction — \\frac{q}{2} +
\\frac{1}{2}\\sqrt{...} rather than \\frac{q + \\sqrt{...}}{2}. A fraction inside a
radical is fine and is used freely.
"""

COURSE = {
    "id": "CTRL520",
    "title": "Optimal Estimation and Control",
    "band": 2,
    "level": "Expert",
    "prereqs": ["CTRL510"],
    "stack": ["Python", "NumPy"],
    "credits": 12,
    "hours": 150,
    "icon": "◉",
    "summary": (
        "Pole placement asks you where you want the poles. It is a fair question with no "
        "good answer, because the honest reply is a trade — faster response against more "
        "actuator effort, tighter tracking against more amplified sensor noise. This course "
        "replaces the question with a cost functional and a noise model, and lets a matrix "
        "equation return the gain. The same equation, transposed, returns the estimator, and "
        "the two designs turn out not to interfere."
    ),
    "outcomes": [
        "Write a quadratic cost for a plant and say what the entries of Q and R actually price.",
        "Solve the algebraic Riccati equation numerically and prove the solution by its residual, not by trusting a library.",
        "Derive the Kalman gain as the variance-minimising correction, and recognise it as the LQR problem transposed.",
        "Assemble an LQG loop, and demonstrate that its closed-loop poles are the union of the two designs.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that regulates an unmeasured load through a flexible shaft using nothing but a noisy motor encoder.",
    "reading": [
        "*Linear Optimal Control Systems*, Kwakernaak & Sivan — the standard treatment of LQ and the Riccati equation.",
        "*Optimal State Estimation*, Simon — chapters 5 to 7, for the filter and its covariance.",
        "*Feedback Systems*, Åström & Murray — chapter 7, for the separation argument in a page.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The cost functional and the trade it prices",
            "summary": "Stop choosing poles. Choose what an error is worth and what effort costs, and let the algebra choose the poles.",
            "concepts": [
                "The infinite-horizon cost $J = \\int_0^\\infty (x^\\top Q x + u^\\top R u)\\,dt$, and why it is quadratic rather than anything else.",
                "$Q$ prices deviation, $R$ prices effort — and only their *ratio* affects the answer.",
                "$Q \\succeq 0$ and $R \\succ 0$: an error may be free, an actuator never is.",
                "The optimal law is a constant state feedback $u = -Kx$, with $K = R^{-1}B^\\top P$, and $P$ the solution of a matrix quadratic.",
                "The value function is $J^\\star(x_0) = x_0^\\top P x_0$ — $P$ is not a step towards the answer, it *is* the answer.",
            ],
            "read": [
                {
                    "title": "The pole pair nobody could justify",
                    "minutes": 15,
                    "body": r'''
On the bench is a positioning stage: 1 kg of tool carriage on air bearings, with no
spring and no friction worth putting in a model, pushed by a voice coil whose amplifier
clips at 8 N. The plant is $\ddot{y} = u$ with $u$ in newtons — a double integrator, and
nothing in CTRL510 has any trouble with it. The specification is one line: move the stage
10 mm, and be inside 2% of the target within a quarter of a second.

Place both closed-loop poles at $-p$. With
$A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$ and
$B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$, the characteristic polynomial of $A - BK$ is
$\lambda^2 + K_2\lambda + K_1$; matching it against $(\lambda + p)^2$ gives
$K = [\,p^2\ \ 2p\,]$. So the coil is asked for $p^2 x_0$ newtons at the instant the move
begins. Four candidates, run against the plant:

```python
X0 = 0.010          # a 10 mm move, in metres


def stage(k1, k2, dt=1e-5, seconds=1.2):
    """1 kg carriage, u = -k1*x - k2*v. Returns (2% settling time, peak force)."""
    x, v, t = X0, 0.0, 0.0
    peak, settle = 0.0, None
    while t < seconds:
        u = -k1 * x - k2 * v
        peak = max(peak, abs(u))
        if abs(x) > 0.02 * X0:
            settle = None
        elif settle is None:
            settle = t
        x, v = x + dt * v, v + dt * u
        t += dt
    return settle, peak


print("    p   settle     peak    5.834/p   p^2*x0")
for p in (10.0, 15.0, 23.2, 29.0):
    s, f = stage(p * p, 2.0 * p)
    print(f"{p:5.1f}  {s:5.3f} s  {f:5.2f} N    {5.834 / p:6.3f}   {p * p * X0:6.2f}")
```

```text
    p   settle     peak    5.834/p   p^2*x0
 10.0  0.583 s   1.00 N     0.583     1.00
 15.0  0.389 s   2.25 N     0.389     2.25
 23.2  0.251 s   5.38 N     0.251     5.38
 29.0  0.201 s   8.41 N     0.201     8.41
```

The last two columns are not fitted to the first two; they are the closed form, and the
simulation lands on them. The free response from rest is $x(t) = x_0 e^{-pt}(1 + pt)$,
whose 2% crossing is the root of $e^{-s}(1+s) = 0.02$ at $s = 5.834$, and whose opening
demand is $-Kx(0) = -p^2 x_0$. Settling therefore goes as $1/p$ and effort as $p^2$,
which is to say effort goes as the inverse *square* of the settling time. The
quarter-second specification is met at $p = 23.2$ for 5.38 N of the coil's 8. Ask for
0.20 s and the amplifier clips.

Now the question the method cannot answer. There is 2.6 N of headroom at $p = 23.2$.
Move to $p = 26$ and the stage settles in 0.224 s for 6.76 N; to $p = 28$ and it settles
in 0.208 s for 7.84 N with nothing left over for a disturbance. Every one of these meets
the written specification, and pole placement prefers none of them, because you were the
one who supplied the poles. That is not a defect in the technique. It is the technique
being asked an underspecified question: the requirement was never "settle in 0.25 s", it
was *settle as fast as is worth the force it takes*, and the word "worth" carries the
entire design.

## What a price has to look like

Suppose you are willing to say what a millimetre of error is worth against a newton of
force. Then a whole trajectory can be scored and the lowest score wins, with nobody
choosing a pole. What can that score be?

It has to accumulate over time, because a stage 1 mm off for a second is worse than one
1 mm off for a millisecond, so it is $J = \int_0^\infty \ell(x, u)\,dt$ for some running
penalty. That penalty must be zero at the target with the actuator quiet and positive
everywhere else, or the optimiser will find somewhere cheaper to sit than the target. It
must be even in each argument: 1 mm short costs what 1 mm long costs, and pushing left
costs what pushing right costs. And it should be smooth, because a corner in the penalty
puts a corner in the control law.

Expand any $\ell$ meeting those conditions about the origin. The constant term vanishes
because $\ell(0,0) = 0$; the linear terms vanish because $\ell$ is even; the first
surviving terms are quadratic. Keeping them and dropping the rest leaves

$$\ell(x, u) = x^\top Q x + u^\top R u$$

with $Q$ and $R$ symmetric, since the antisymmetric part of a matrix contributes nothing
to a quadratic form and can be discarded without changing a single value of $\ell$. The
quadratic penalty is not the only one that meets the four conditions. It is the leading
term of every one of them, and it is the one for which the minimising law over a linear
plant comes out linear and constant rather than needing a fresh optimisation at every
instant.

## Two weights, one degree of freedom

$Q$ prices deviation and $R$ prices action, in units chosen so that $x^\top Q x$ and
$u^\top R u$ are the same currency. Which raises the question of what happens when the
currency is changed. Multiply both by $\alpha > 0$: every trajectory scales by $\alpha$,
the ordering of trajectories is untouched, and so the minimiser is untouched. There is
one degree of freedom in the pair, not two, and it is the ratio. An afternoon spent
sweeping $Q$ and $R$ independently is an afternoon spent sweeping a grid over a curve.

The asymmetry between the two is sharper than it looks. $Q \succeq 0$ is permitted: an
internal state nobody cares about, priced at zero, is an honest statement about the
requirement. $R \succ 0$ is required, and one dimension shows why. Put $r = 0$ into the
scalar problem and the state cost can be pushed towards zero by a gain made larger and
larger, with the effort term charging nothing for it. The infimum of $J$ is approached
and never attained: for every finite gain there is a better one, so there is no optimal
control at all. A free actuator is not a cheap actuator, it is an actuator with no
optimum.

## The same stage, priced instead of placed

Solving the matrix equation is module 2's work, but its answer for this plant is short
enough to write down. With $Q = \text{diag}(q, 0)$ and $R = r$, the three entries of the
symmetric $P$ satisfy $p_2^2 = qr$, $p_1 = p_2p_3/r$ and $p_3^2 = 2rp_2$, giving
$K = R^{-1}B^\top P = \left[\sqrt{q/r},\ \sqrt{2}\,(q/r)^{1/4}\right]$. Both closed-loop
poles then sit at radius $\omega_n = (q/r)^{1/4}$ with damping ratio
$\zeta = K_2 / 2\omega_n = \sqrt{2}/2$, whatever the weights are. Every LQR design on a
double integrator has a damping ratio of 0.707; the ratio $q/r$ moves the poles along a
ray at 45° and nothing moves them off it. That is one reason the sandbox *What the
weights are actually buying* is worth dragging: the pairs it lets you reach that are not
on that ray are pairs no cost functional would ever return.

Pick $q/r = 320\,000$, which puts $\omega_n$ at 23.8, and race it against the hand-placed
$p = 23.2$ that met the specification:

```python
import math

X0 = 0.010
Q, R = 320000.0, 1.0        # one newton-squared of effort buys 320000 metre-squared of error


def run(k1, k2, dt=1e-5, seconds=1.5):
    x, v, t = X0, 0.0, 0.0
    peak, settle, J, effort = 0.0, None, 0.0, 0.0
    while t < seconds:
        u = -k1 * x - k2 * v
        peak = max(peak, abs(u))
        J += (Q * x * x + R * u * u) * dt
        effort += R * u * u * dt
        if abs(x) > 0.02 * X0:
            settle = None
        elif settle is None:
            settle = t
        x, v = x + dt * v, v + dt * u
        t += dt
    return settle, peak, J, effort


ratio = Q / R
designs = (("LQR ", (math.sqrt(ratio), math.sqrt(2.0) * ratio ** 0.25)),
           ("hand", (23.2 ** 2, 2 * 23.2)))
for name, (k1, k2) in designs:
    s, f, J, e = run(k1, k2)
    print(f"{name}  K = [{k1:7.2f}, {k2:6.2f}]  settle {s:.3f} s  peak {f:.2f} N"
          f"  J {J:.4f}  effort {e:.4f}")

p2 = math.sqrt(Q * R)
p3 = math.sqrt(2.0) * R ** 0.75 * Q ** 0.25
print("value function x0^T P x0 =", round(p2 * p3 / R * X0 * X0, 4))
```

```text
LQR   K = [ 565.69,  33.64]  settle 0.251 s  peak 5.66 N  J 1.9031  effort 0.4758
hand  K = [ 538.24,  46.40]  settle 0.251 s  peak 5.38 N  J 2.0365  effort 0.3123
value function x0^T P x0 = 1.9027
```

Both settle in 0.251 s. The optimal design has the **larger** peak force and the
**larger** effort integral — 0.476 against 0.312, more than half again — and it wins
anyway, because it spends that effort buying a state integral of 1.427 against the hand
design's 1.724. And the cost of the optimal run, 1.9031 from a Riemann sum over a
forward-Euler trajectory, agrees with $x_0^\top P x_0 = 1.9027$ computed from the matrix
alone, without simulating anything. $P$ is not scaffolding on the way to $K$. It is the
cost of the entire remaining future from a state, which is why the design can be
evaluated before it is run.

## The mistake, and why it is tempting

The mistake is choosing $R$ from the actuator rating — reasoning that the coil clips at
8 N, so $R$ should be set to keep the demand under 8 N. It is tempting because $R$ is
the only quantity in the problem with the units of the actuator, and because turning it
up genuinely does reduce the demand, so the first experiment appears to confirm the
theory.

What the run above shows is that the connection does not hold in the direction that
matters. $R$ prices $\int u^2\,dt$; it says nothing whatever about $\max_t |u|$. The
optimal design here draws a higher peak than the design it beat, and it is free to,
because peak force is not in the cost function. Raise $R$ until the peak falls under a
limit and you have not imposed a constraint, you have bought a different trajectory whose
peak happens to be smaller — on this initial condition. Double $x_0$ and the demand
doubles with it, because the law is linear and the weight is not a limiter. A saturation
limit is a constraint, and a constraint is a different problem: model-predictive control
exists more or less because of this sentence.

## Where this stops holding

The cost functional runs to infinity, so every claim above is about a plant that is left
alone to settle. It contains no reference, so tracking a moving target needs the
formulation extended; it contains no integrator, so a constant load disturbance leaves a
constant offset that LQR will price and tolerate rather than remove. The quadratic form
charges a 10 mm error one hundred times a 1 mm error, which is the right relative price
for a positioning stage and the wrong one for a sensor that occasionally reports a
spike. And the linear plant is a linearisation: once the coil saturates, the loop that
runs is not the loop that was designed, and the guaranteed margins of the unsaturated
design are guarantees about something else.

## What you are about to build

The lab for this module, *Price the trade between error and effort*, is the scalar case
end to end: `riccati_scalar` for the positive root of $2ap + q - p^2b^2/r = 0$, `gain`
for $k = bp/r$, `closed_pole`, and `cost`, which forward-Eulers the closed loop and
accumulates $\int (qx^2 + ru^2)\,dt$ as a Riemann sum. The derivation *The scalar LQR,
end to end* gets the same results symbolically. Here they are with the lab plant, so the
numbers the checks compare against are visible in advance:

```python
import math


def riccati(a, b, q, r):
    """The positive root of 2*a*p + q - p*p*b*b/r = 0."""
    return (a * r + math.sqrt(a * a * r * r + q * r * b * b)) / (b * b)


def cost(a, b, k, q, r, x0, dt=1e-4, steps=200000):
    x, J = x0, 0.0
    for _ in range(steps):
        u = -k * x
        J += (q * x * x + r * u * u) * dt
        x += dt * (a * x + b * u)
    return J


a, b, q, r, x0 = -0.5, 1.5, 2.0, 0.5, 1.3
p = riccati(a, b, q, r)
k = b * p / r
print("p =", round(p, 6), "  k =", round(k, 6), "  pole =", round(a - b * k, 6))
print("p * x0^2   =", round(p * x0 * x0, 4))
for label, g in (("J at k    ", k), ("J at 1.4 k", 1.4 * k), ("J at 0.6 k", 0.6 * k)):
    print(label, "=", round(cost(a, b, g, q, r, x0), 4))
print("k after scaling q and r by 10 =", round(b * riccati(a, b, 10 * q, 10 * r) / (10 * r), 6))
print("pole after scaling q/r by 100 =", round(a - b * b * riccati(a, b, 100 * q, r) / r, 4))
```

```text
p = 0.564751   k = 1.694254   pole = -3.041381
p * x0^2   = 0.9544
J at k     = 0.9546
J at 1.4 k = 1.0025
J at 0.6 k = 1.0504
k after scaling q and r by 10 = 1.694254
pole after scaling q/r by 100 = -30.0042
```

Moving the gain 40% either way costs more, and asymmetrically: a minimum is flat near its
bottom, which is why an LQR design survives being shipped with a rounded gain. Scaling
both weights by ten returns the identical float. And the last line is the shape of the
whole trade — eliminating $p$ gives $\lambda = -\sqrt{a^2 + qb^2/r}$, so a hundredfold
rise in price buys a tenfold rise in speed, and on the double integrator, where the pole
radius is the fourth root, it buys rather less than that.
''',
                },
            ],
            "sandbox": {
                "title": "What the weights are actually buying",
                "visualiser": "pole-place",
                "minutes": 8,
                "initial": {"p1": -1, "p2": -1},
                "brief": r'''
A double integrator under state feedback, with the poles placed by hand. The top plot
is the position settling from $x = 1$; the bottom is the effort it took.

For this plant, equal poles at $-p$ give $K = [p^2,\ 2p]$, so the initial demand on the
actuator is exactly $p^2$. Watch that number as you drag.
''',
                "notice": [
                    "Both poles at $-1$ gives $K = [1,\\ 2]$ and a peak effort of 1. LQR on this same plant with $Q = I$ and $R = 1$ lands at $-0.87 \\pm 0.5j$ — the same neighbourhood, reached without you choosing anything.",
                    "Drag both poles to $-4$. Settling is four times faster and the peak effort is sixteen times larger, because it is $p^2$. That squaring is the reason $R$ multiplies $u^2$ rather than $|u|$.",
                    "Put one pole at $-0.2$ and the other at $-10$. The slow pole sets the settling time on its own, so every unit of effort spent on the fast one buys nothing. No cost functional would ever return this pair.",
                ],
            },
            "derive": {
                "title": "The scalar LQR, end to end",
                "minutes": 16,
                "vars": ["a", "b", "p", "q", "r", "k", "x", "u", "t", "J"],
                "brief": r'''
One state, one input:

$$\dot{x} = a x + b u, \qquad J = \int_0^\infty \left(q x^2 + r u^2\right) dt$$

with $q \ge 0$ and $r > 0$. The matrix Riccati equation

$$A^\top P + P A - P B R^{-1} B^\top P + Q = 0$$

collapses here to a scalar quadratic in $p$. Solve it, read off the gain, and then find
out what the closed loop does — the last answer is the point of the whole module.
''',
                "steps": [
                    {
                        "prompt": "Write out the scalar Riccati equation: the expression in $a$, $b$, $p$, $q$ and $r$ that must equal zero.",
                        "given": "In one dimension every matrix is a number, so $A^\\top P$ and $P A$ are the same thing.",
                        "answer": "2 a p + q - \\frac{p^2 b^2}{r}",
                        "hint": "$A^\\top P + P A$ becomes $ap + pa = 2ap$. The middle term $P B R^{-1} B^\\top P$ becomes $p b (1/r) b p$.",
                        "deconstruct": [
                            "The two linear terms collapse to $2ap$.",
                            "The quadratic term is $p^2 b^2 / r$, and it enters with a minus sign.",
                        ],
                    },
                    {
                        "prompt": "The gain is $K = R^{-1}B^\\top P$. Write $k$ in terms of $b$, $p$ and $r$.",
                        "answer": "\\frac{b p}{r}",
                        "hint": "Read the matrix formula one factor at a time: $R^{-1}$ is $1/r$, $B^\\top$ is $b$, $P$ is $p$.",
                        "deconstruct": [
                            "$R^{-1} = 1/r$.",
                            "Multiply by $b$ and then by $p$.",
                        ],
                    },
                    {
                        "prompt": "Under $u = -kx$ the closed loop is $\\dot{x} = (a - bk)x$. Write that pole in terms of $a$, $b$, $p$ and $r$.",
                        "answer": "a - \\frac{b^2 p}{r}",
                        "hint": "Substitute the $k$ you just wrote into $a - bk$.",
                        "deconstruct": [
                            "$bk = b \\cdot bp/r$.",
                            "So $a - bk = a - b^2 p / r$.",
                        ],
                    },
                    {
                        "prompt": "Now eliminate $p$ between the last two results and write the closed-loop pole using only $a$, $b$, $q$ and $r$.",
                        "given": "Call the pole $\\lambda$. From the previous step $b^2 p / r = a - \\lambda$, so $p = r(a - \\lambda)/b^2$.",
                        "answer": "-\\sqrt{a^2 + \\frac{q b^2}{r}}",
                        "hint": "Substituting into the Riccati equation and writing $d = a - \\lambda$ gives $d^2 - 2ad - qb^2/r = 0$. Take the root that leaves $\\lambda$ negative.",
                        "deconstruct": [
                            "Substituting $p = r(a-\\lambda)/b^2$ into $2ap + q - p^2b^2/r = 0$ and multiplying by $b^2/r$ gives $2a(a-\\lambda) + qb^2/r - (a-\\lambda)^2 = 0$.",
                            "With $d = a - \\lambda$ that is $d^2 - 2ad - qb^2/r = 0$, so $d = a \\pm \\sqrt{a^2 + qb^2/r}$; only the upper sign makes $\\lambda = a - d$ negative.",
                        ],
                    },
                ],
                "closing": r'''
Read that last line carefully, because three things fall out of it at once.

The pole is negative for **every** $a$, including a plant that was running away — LQR
stabilises anything it can reach. It depends on $q$ and $r$ only through the ratio
$q/r$, so there are not two knobs here, there is one. And as $q/r$ grows the pole goes
out like the square root, which is why buying a factor of ten in speed costs a factor
of a hundred in weight.
''',
            },
            "quiz": {
                "title": "Pricing an error against an effort",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In $J = \\int_0^\\infty (x^\\top Qx + u^\\top Ru)\\,dt$, what does $R$ price?",
                        "opts": ["Control effort", "State deviation", "Measurement noise", "The settling time"],
                        "a": 0,
                        "why": r"""
$R$ multiplies $u$, so it is the price of *acting*. Raise it and the optimal controller
becomes reluctant, moves the poles closer to the imaginary axis and lets errors persist
longer. $Q$ prices the deviation itself. Measurement noise does not appear here at all —
that is the estimation problem, with its own pair of weights, in module 3.
""",
                    },
                    {
                        "q": "Why must $R \\succ 0$ while $Q \\succeq 0$ is enough?",
                        "opts": [
                            "A free actuator would let the optimal gain grow without bound",
                            "$R$ has to be invertible for the matrix dimensions to work",
                            "$Q$ is always diagonal in practice",
                            "It is a convention with no consequence",
                        ],
                        "a": 0,
                        "why": r"""
If some direction of $u$ costs nothing, the optimiser will use an infinite amount of it
— the cost has no minimum and the gain runs away. A *state* may legitimately be free:
you often do not care about an internal variable at all, and $Q$ is allowed to be
singular. Invertibility is indeed needed for $R^{-1}$ in the Riccati equation, but that
is the symptom, not the reason: the equation asks for the inverse precisely because
zero cost is meaningless.
""",
                    },
                    {
                        "q": "You double both $Q$ and $R$. What happens to the optimal gain $K$?",
                        "opts": [
                            "Nothing — only the ratio matters",
                            "It doubles",
                            "It halves",
                            "It scales by $\\sqrt{2}$",
                        ],
                        "a": 0,
                        "why": r"""
$P$ doubles and $K = R^{-1}B^\top P$ has the factor cancel, so the controller is
unchanged. That is worth knowing before you start tuning: there is one fewer knob than
there appear to be, and sweeping a single scalar $\rho$ in $Q$ versus $\rho R$ traces
the whole family. It also means the units of $J$ are arbitrary — its *value* is not
meaningful, only its minimiser.
""",
                    },
                    {
                        "q": "What has LQR replaced, compared with the previous course?",
                        "opts": [
                            "Choosing pole locations directly — you choose weights and the algebra chooses the poles",
                            "The need for state feedback",
                            "The need for a model of the plant",
                            "The stability requirement",
                        ],
                        "a": 0,
                        "why": r"""
Pole placement asks you to name $n$ complex numbers, which for anything above second
order is a guess dressed up as a specification. LQR asks a question you can actually
answer — what is a unit of error worth against a unit of effort — and derives the poles
from it. It is still full state feedback and it still needs the model; what has changed
is where the engineering judgement is applied.
""",
                    },
                    {
                        "q": "What robustness does an LQR loop come with, for free?",
                        "opts": [
                            "Infinite gain margin and at least 60° of phase margin",
                            "Guaranteed rejection of any disturbance",
                            "Immunity to modelling error in $A$",
                            "None — LQR says nothing about margins",
                        ],
                        "a": 0,
                        "why": r"""
A remarkable result: any LQR state-feedback loop tolerates arbitrary gain increase, a
halving of the gain, and 60° of phase lag, whatever weights you picked. It is one of the
strongest guarantees in control — and it is worth knowing precisely because it evaporates
the moment you put an observer in the loop, which is what makes module 4's LQG story more
delicate than the separation principle alone suggests.
""",
                    },
                ],
            },
            "lab": {
                "title": "Price the trade between error and effort",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Implement the scalar result you just derived, then check it against a simulation that
knows nothing about Riccati equations.

- `riccati_scalar(a, b, q, r)` — the positive root of $2ap + q - p^2b^2/r = 0$.
- `gain(a, b, q, r)` — the feedback gain $k = bp/r$.
- `closed_pole(a, b, q, r)` — the resulting pole $a - bk$.
- `cost(a, b, k, q, r, x0, dt, steps)` — forward-Euler the closed loop from `x0` under
  `u = -k*x`, accumulating $\int (qx^2 + ru^2)\,dt$ as a Riemann sum:

```text
u = -k * x
J += (q*x*x + r*u*u) * dt
x += dt * (a*x + b*u)
```

  Accumulate the running cost **before** stepping, so the sum starts at `x0`.

The interesting check is the last one: the cost of the optimal gain should come out
equal to $p\,x_0^2$, and any other gain should cost more.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def riccati_scalar(a, b, q, r):
    """Positive root p of 2*a*p + q - p**2 * b**2 / r = 0."""
    # TODO: it is a quadratic in p. Rearrange to p**2 - (2*a*r/b**2)*p - q*r/b**2 = 0
    # and take the root that is positive.
    return 0.0


def gain(a, b, q, r):
    """The optimal feedback gain k = b*p/r."""
    # TODO
    return 0.0


def closed_pole(a, b, q, r):
    """The closed-loop pole a - b*k."""
    # TODO
    return 0.0


def cost(a, b, k, q, r, x0, dt, steps):
    """Forward-Euler the closed loop and return the accumulated quadratic cost."""
    x = float(x0)
    J = 0.0
    # TODO: for each step, form u = -k*x, add (q*x*x + r*u*u)*dt to J, then advance x.
    return J


if __name__ == "__main__":
    print("p     =", round(riccati_scalar(1.0, 1.0, 1.0, 1.0), 6), "(expect 1 + sqrt(2))")
    print("k     =", round(gain(1.0, 1.0, 1.0, 1.0), 6))
    print("pole  =", round(closed_pole(1.0, 1.0, 1.0, 1.0), 6), "(expect -sqrt(2))")
    k = gain(-0.5, 1.5, 2.0, 0.5)
    print("J     =", round(cost(-0.5, 1.5, k, 2.0, 0.5, 1.3, 0.001, 20000), 6))
    print("p*x0^2=", round(riccati_scalar(-0.5, 1.5, 2.0, 0.5) * 1.3 ** 2, 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def riccati_scalar(a, b, q, r):
    """Positive root p of 2*a*p + q - p**2 * b**2 / r = 0."""
    return (a * r + np.sqrt(a * a * r * r + q * r * b * b)) / (b * b)


def gain(a, b, q, r):
    """The optimal feedback gain k = b*p/r."""
    return b * riccati_scalar(a, b, q, r) / r


def closed_pole(a, b, q, r):
    """The closed-loop pole a - b*k."""
    return a - b * gain(a, b, q, r)


def cost(a, b, k, q, r, x0, dt, steps):
    """Forward-Euler the closed loop and return the accumulated quadratic cost."""
    x = float(x0)
    J = 0.0
    for _ in range(steps):
        u = -k * x
        J += (q * x * x + r * u * u) * dt
        x = x + dt * (a * x + b * u)
    return J


if __name__ == "__main__":
    print("p     =", round(riccati_scalar(1.0, 1.0, 1.0, 1.0), 6), "(expect 1 + sqrt(2))")
    print("k     =", round(gain(1.0, 1.0, 1.0, 1.0), 6))
    print("pole  =", round(closed_pole(1.0, 1.0, 1.0, 1.0), 6), "(expect -sqrt(2))")
    k = gain(-0.5, 1.5, 2.0, 0.5)
    print("J     =", round(cost(-0.5, 1.5, k, 2.0, 0.5, 1.3, 0.001, 20000), 6))
    print("p*x0^2=", round(riccati_scalar(-0.5, 1.5, 2.0, 0.5) * 1.3 ** 2, 6))
'''}],
                "hints": [
                    "Multiply the Riccati equation by $-r/b^2$ first: it becomes $p^2 - (2ar/b^2)p - qr/b^2 = 0$, an ordinary quadratic.",
                    "The quadratic formula gives $p = (ar \\pm \\sqrt{a^2r^2 + qrb^2})/b^2$; the square root is always at least $|a|r$, so the plus sign is the positive root.",
                    "`closed_pole` should not repeat any algebra — call `gain` and return `a - b*k`.",
                    "In `cost`, record before you step. Adding the cost after the Euler update silently drops the contribution of the initial state.",
                ],
                "tests": [
                    {"name": "the root really solves the Riccati equation", "code": r'''
for _a, _b, _q, _r in [(1.0, 1.0, 1.0, 1.0), (-0.5, 1.5, 2.0, 0.5), (2.0, 0.8, 3.0, 0.2)]:
    _p = riccati_scalar(_a, _b, _q, _r)
    _res = 2 * _a * _p + _q - _p * _p * _b * _b / _r
    assert abs(_res) < 1e-9, \
        f"2*a*p + q - p^2 b^2/r should vanish at the solution; for a={_a} it is {_res:.6g}"
    assert _p > 0, f"the cost-to-go cannot be negative, but p came out {_p}"
'''},
                    {"name": "the gain is b times p over r", "code": r'''
import numpy as np
_p = riccati_scalar(1.0, 1.0, 1.0, 1.0)
assert abs(_p - (1.0 + np.sqrt(2.0))) < 1e-9, f"expected 1 + sqrt(2) = 2.414214, got {_p}"
_k = gain(-0.5, 1.5, 2.0, 0.5)
_want = 1.5 * riccati_scalar(-0.5, 1.5, 2.0, 0.5) / 0.5
assert abs(_k - _want) < 1e-9, \
    f"K = R^-1 B^T P means k = b*p/r; expected {_want:.6f}, got {_k:.6f}"
'''},
                    {"name": "the closed loop is stable even when the plant is not", "code": r'''
import numpy as np
_pole = closed_pole(2.0, 1.0, 1.0, 1.0)
assert abs(_pole - (-np.sqrt(5.0))) < 1e-9, \
    f"with a=2, b=1, q=1, r=1 the pole is -sqrt(a^2 + q b^2/r) = -2.236068, got {_pole:.6f}"
assert closed_pole(5.0, 1.0, 0.001, 1.0) < 0, \
    "LQR stabilises any reachable plant, however unstable and however light the weight"
'''},
                    {"name": "only the ratio of q to r matters", "code": r'''
_k1 = gain(-0.5, 2.0, 1.0, 1.0)
_k2 = gain(-0.5, 2.0, 10.0, 10.0)
assert abs(_k1 - 0.7807764064044151) < 1e-9, f"expected k = 0.780776, got {_k1}"
assert abs(_k1 - _k2) < 1e-12, \
    f"scaling q and r together must leave the gain alone; got {_k1:.6f} then {_k2:.6f}"
assert abs(gain(0.0, 1.0, 1.0, 0.01) - 10.0) < 1e-9, \
    "with a = 0 the gain is sqrt(q/r), so q/r = 100 gives exactly 10"
'''},
                    {"name": "the optimal cost is p times x0 squared", "code": r'''
_a, _b, _q, _r, _x0 = -0.5, 1.5, 2.0, 0.5, 1.3
_k = gain(_a, _b, _q, _r)
_J = cost(_a, _b, _k, _q, _r, _x0, 0.001, 20000)
_want = riccati_scalar(_a, _b, _q, _r) * _x0 * _x0
assert _J > 0, "the cost of a non-zero initial state cannot be zero — is the loop accumulating?"
assert abs(_J - _want) / _want < 0.01, \
    f"the value function is J* = p*x0^2 = {_want:.6f}; the simulation gave {_J:.6f}"
'''},
                    {"name": "moving the gain either way costs more", "code": r'''
_a, _b, _q, _r, _x0 = -0.5, 1.5, 2.0, 0.5, 1.3
_k = gain(_a, _b, _q, _r)
_J = cost(_a, _b, _k, _q, _r, _x0, 0.001, 20000)
_hi = cost(_a, _b, _k * 1.4, _q, _r, _x0, 0.001, 20000)
_lo = cost(_a, _b, _k * 0.6, _q, _r, _x0, 0.001, 20000)
assert _J < _hi * 0.99, f"a 40% larger gain should cost more, but {_J:.6f} vs {_hi:.6f}"
assert _J < _lo * 0.99, f"a 40% smaller gain should cost more, but {_J:.6f} vs {_lo:.6f}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Solving the Riccati equation by iteration",
            "summary": "A matrix quadratic has no formula. It does have a differential equation that runs into it, and that is enough.",
            "concepts": [
                "The finite-horizon problem gives a *differential* Riccati equation; the infinite-horizon gain is its steady state.",
                "Running the Riccati equation in time-to-go turns the algebraic problem into an initial-value problem starting at $P = 0$.",
                "The residual $A^\\top P + P A - P B R^{-1} B^\\top P + Q$ is the only acceptable proof that a solver worked.",
                "The stabilising solution is the symmetric positive-semidefinite one; the quadratic has others, and they are useless.",
                "Existence needs $(A, B)$ stabilisable and $(A, Q^{1/2})$ detectable — a mode that is neither reachable nor penalised is invisible to the cost.",
            ],
            "read": [
                {
                    "title": "Two matrices satisfy it, and one of them falls over",
                    "minutes": 16,
                    "body": r'''
The stage from module 1 is small enough to solve by hand, so start there. With
$A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$,
$B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$, $Q = I$ and $R = 1$, write
$P = \begin{bmatrix} p_1 & p_2 \\ p_2 & p_3 \end{bmatrix}$ and expand
$A^\top P + PA - PBR^{-1}B^\top P + Q = 0$ entry by entry. The three distinct entries
give three equations:

$$-p_2^2 + 1 = 0, \qquad p_1 - p_2 p_3 = 0, \qquad 2p_2 - p_3^2 + 1 = 0$$

The first hands you $p_2$, the third then hands you $p_3$, and the second hands you
$p_1$. Take $p_2 = 1$, so $p_3^2 = 3$ and $p_3 = \sqrt{3}$, and $p_1 = \sqrt{3}$. Then
$K = R^{-1}B^\top P = [\,1\ \ \sqrt{3}\,]$, and $A - BK$ has characteristic polynomial
$\lambda^2 + \sqrt{3}\lambda + 1$ with roots at $-0.866 \pm 0.5j$ — which is the pair the
sandbox *Where the Riccati solution puts the poles* reports, and a pair no amount of
dragging two real sliders will ever produce.

Now look again at the first equation. It says $p_2^2 = 1$, and it does not say which
root. And the third says $p_3^2 = 2p_2 + 1$, which for $p_2 = 1$ leaves $p_3 = \pm\sqrt{3}$.
So there is a second real symmetric matrix satisfying every one of the three equations,
and it is worth meeting:

```python
import math

A = [[0.0, 1.0], [0.0, 0.0]]          # the stage of module 1, still a double integrator
B = [[0.0], [1.0]]
Q = [[1.0, 0.0], [0.0, 1.0]]
R = 1.0


def mul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))]
            for i in range(len(X))]


def tr(X):
    return [list(row) for row in zip(*X)]


def residual(P):
    """A^T P + P A - P B R^-1 B^T P + Q, term for term."""
    quad = mul(mul(mul(P, B), [[1.0 / R]]), mul(tr(B), P))
    left, right = mul(tr(A), P), mul(P, A)
    return [[left[i][j] + right[i][j] - quad[i][j] + Q[i][j] for j in range(2)]
            for i in range(2)]


def poles(M):
    """Eigenvalues of a 2x2, from its trace and determinant."""
    t = M[0][0] + M[1][1]
    d = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    disc = t * t - 4.0 * d
    if disc >= 0.0:
        return [(t + math.sqrt(disc)) / 2.0, (t - math.sqrt(disc)) / 2.0]
    return [complex(t / 2.0, math.sqrt(-disc) / 2.0),
            complex(t / 2.0, -math.sqrt(-disc) / 2.0)]


s3 = math.sqrt(3.0)
for name, P in (("p3 = +sqrt(3)", [[s3, 1.0], [1.0, s3]]),
                ("p3 = -sqrt(3)", [[-s3, 1.0], [1.0, -s3]])):
    K = [P[1][0] / R, P[1][1] / R]                       # R^-1 B^T P
    cl = [[A[i][j] - B[i][0] * K[j] for j in range(2)] for i in range(2)]
    nrm = max(abs(v) for row in residual(P) for v in row)
    print(name, " K =", [round(v, 6) for v in K],
          " residual", f"{nrm:.1e}",
          " poles", [complex(round(z.real, 4), round(z.imag, 4)) for z in poles(cl)])
```

```text
p3 = +sqrt(3)  K = [1.0, 1.732051]  residual 4.4e-16  poles [(-0.866+0.5j), (-0.866-0.5j)]
p3 = -sqrt(3)  K = [1.0, -1.732051]  residual 4.4e-16  poles [(0.866+0.5j), (0.866-0.5j)]
```

Both residuals are zero to machine precision. One gain stabilises the stage and the other
drives it off the rail with the poles mirrored into the right half-plane. So a vanishing
residual is a necessary condition and not a sufficient one, and the extra condition is
the one the cost interpretation supplies: $x^\top P x$ is the price of the future from
state $x$, and a price cannot be negative. $\begin{bmatrix} \sqrt{3} & 1 \\ 1 & \sqrt{3}\end{bmatrix}$
has trace $2\sqrt{3}$ and determinant 2, so it is positive definite; its twin has the
same determinant and trace $-2\sqrt{3}$, so it is negative definite and is not a cost
at all.

That was the case with three unknowns. The capstone drives a load through a flexible
shaft with four states, so $P$ has ten distinct entries and the equations are quadratic
in all of them. There is no formula, the number of symmetric real solutions grows
combinatorially, and a Newton iteration needs a starting point already in the right
basin. Something else is needed.

## Running into the answer

The something else is already in this course. The derivation *One step of the recursion,
in one dimension* minimises $qx^2 + ru^2 + p(ax+bu)^2$ over $u$ and reads off the value
of $p$ one step further back. In matrix form, one step of that recursion is

$$P_k = Q_d + A_d^\top P_{k+1} A_d -
        A_d^\top P_{k+1} B_d\left(R_d + B_d^\top P_{k+1} B_d\right)^{-1} B_d^\top P_{k+1} A_d$$

Now let the step be a short interval $\Delta$ of continuous time. Over that interval
$A_d = I + A\Delta$, $B_d = B\Delta$, and the running cost accumulated is
$(x^\top Qx + u^\top Ru)\Delta$, so $Q_d = Q\Delta$ and $R_d = R\Delta$. Substitute, and
keep terms to first order in $\Delta$:

$$A_d^\top P A_d = P + \Delta\left(A^\top P + P A\right) + O(\Delta^2)$$

$$R_d + B_d^\top P B_d = \Delta R + \Delta^2 B^\top P B
  \;\Longrightarrow\; \left(\cdot\right)^{-1} = \frac{1}{\Delta}R^{-1} + O(1)$$

The correction term is then
$\left(\Delta P B\right)\left(\frac{1}{\Delta}R^{-1}\right)\left(\Delta B^\top P\right)
= \Delta\,P B R^{-1} B^\top P + O(\Delta^2)$, and everything assembles into

$$P_k = P_{k+1} + \Delta\left(A^\top P + PA - PBR^{-1}B^\top P + Q\right) + O(\Delta^2)$$

$P_k$ is one step further from the horizon than $P_{k+1}$, so writing $\tau$ for the time
remaining and dividing by $\Delta$,

$$\frac{dP}{d\tau} = A^\top P + PA - PBR^{-1}B^\top P + Q$$

Look at what the right-hand side is. It is the residual — the very expression that has to
end at zero. The quantity being integrated and the quantity being tested are the same
object, which is why `solve_care` and `care_residual` in the lab *Solve the algebraic
Riccati equation, and prove it* are one function called from the other rather than two
separate pieces of algebra.

## Why zero is the right place to start, and where it lands

$P(0) = 0$ is not an arbitrary seed. It is the finite-horizon problem with no terminal
cost: with no time remaining there is no future to pay for. Then $x^\top P(\tau)x$ is the
optimal cost over a window of length $\tau$, which is non-negative for every $\tau$; and
it is non-decreasing in $\tau$, because a longer window contains the shorter one plus
more non-negative running cost. A non-decreasing family of positive-semidefinite
matrices, bounded above, converges — and its limit is positive semidefinite. The
trajectory never leaves the cone, so it cannot arrive at the negative-definite twin.
Choosing the root is not a decision made after the fact; it is a consequence of where
the integration started.

```python
A = [[0.0, 1.0], [0.0, 0.0]]
B = [[0.0], [1.0]]
Q = [[1.0, 0.0], [0.0, 1.0]]
Rinv = [[1.0]]


def mul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))]
            for i in range(len(X))]


def tr(X):
    return [list(row) for row in zip(*X)]


def residual(P):
    quad = mul(mul(mul(P, B), Rinv), mul(tr(B), P))
    left, right = mul(tr(A), P), mul(P, A)
    return [[left[i][j] + right[i][j] - quad[i][j] + Q[i][j] for j in range(2)]
            for i in range(2)]


def norm(M):
    return max(abs(v) for row in M for v in row)


print("integrating in time-to-go from P = 0, dt = 0.002")
P = [[0.0, 0.0], [0.0, 0.0]]
for k in range(1, 10001):
    D = residual(P)
    P = [[P[i][j] + 0.002 * D[i][j] for j in range(2)] for i in range(2)]
    if k in (100, 500, 2500, 10000):
        print(f"  tau {k * 0.002:6.2f}   P11 {P[0][0]:.6f}  P12 {P[0][1]:.6f}"
              f"  P22 {P[1][1]:.6f}   K [{P[1][0]:.6f}, {P[1][1]:.6f}]"
              f"   residual {norm(residual(P)):.2e}")

print()
print("stopping when the step change falls below 1e-5:")
for dt in (0.002, 0.0005, 0.0001):
    P, tau = [[0.0, 0.0], [0.0, 0.0]], 0.0
    while True:
        D = residual(P)
        if dt * norm(D) < 1e-5:
            break
        P = [[P[i][j] + dt * D[i][j] for j in range(2)] for i in range(2)]
        tau += dt
    print(f"  dt {dt:<8} stopped at tau {tau:7.3f}   K2 {P[1][1]:.6f}"
          f"   residual {norm(residual(P)):.2e}")
```

```text
integrating in time-to-go from P = 0, dt = 0.002
  tau   0.20   P11 0.199985  P12 0.019607  P22 0.199946   K [0.019607, 0.199946]   residual 1.00e+00
  tau   1.00   P11 0.965097  P12 0.389263  P22 0.964580   K [0.389263, 0.964580]   residual 8.48e-01
  tau   5.00   P11 1.730865  P12 0.998974  P22 1.730867   K [0.998974, 1.730867]   residual 2.05e-03
  tau  20.00   P11 1.732051  P12 1.000000  P22 1.732051   K [1.000000, 1.732051]   residual 5.51e-14

stopping when the step change falls below 1e-5:
  dt 0.002    stopped at tau   4.486   K2 1.729165   residual 4.99e-03
  dt 0.0005   stopped at tau   3.686   K2 1.720443   residual 2.00e-02
  dt 0.0001   stopped at tau   2.729   K2 1.672546   residual 1.00e-01
```

The top block arrives at $\begin{bmatrix} \sqrt{3} & 1 \\ 1 & \sqrt{3}\end{bmatrix}$ to
six decimals with a residual of $5.5\times10^{-14}$. The rows above the last one are not
failed attempts: at $\tau = 1$ the gain $[\,0.389\ \ 0.965\,]$ is the optimal gain for a
one-second window, and it is smaller than the infinite-horizon gain because a controller
with one second left has less future error to prevent and therefore less reason to spend.
The gain schedule of a finite-horizon design is this trajectory read backwards.

## The mistake, and why it is tempting

The bottom block is the mistake. Stopping when $P$ stops changing looks like the natural
convergence test, and it is what every fixed-point iteration anyone has written uses,
because in those the step *is* the update. Here the step is $\Delta$ times the residual —
the residual scaled by a number you chose — so shrinking $\Delta$ shrinks the step
without improving the answer by one digit. The three runs use the same tolerance of
$10^{-5}$ and stop earlier and earlier as the step gets finer, and the gain drifts from
1.7292 to 1.6725 against a true value of 1.7321, while the residual grows by a factor of
twenty. The test that looks the most careful gives the worst answer, and it reports
success every time.

Substituting $P$ back into the algebraic equation costs one extra evaluation of a
function you already have, and it is the only test that examines the answer rather than
the process. That is what the fill-in unit *The Riccati equation, term by term* is asking
about, and what the lab's second check enforces.

## Where this stops holding

The iteration converges when the problem has a solution, and it has one when two
conditions hold. Both are visible in a plant with two uncoupled modes, one growing and
one decaying, with an actuator that reaches the decaying one only:

```python
A = [[1.0, 0.0], [0.0, -1.0]]         # a growing mode and a decaying one, uncoupled
B = [[0.0], [1.0]]                    # the actuator reaches the decaying one only
Rinv = [[1.0]]


def mul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))]
            for i in range(len(X))]


def tr(X):
    return [list(row) for row in zip(*X)]


def residual(Q, P):
    quad = mul(mul(mul(P, B), Rinv), mul(tr(B), P))
    left, right = mul(tr(A), P), mul(P, A)
    return [[left[i][j] + right[i][j] - quad[i][j] + Q[i][j] for j in range(2)]
            for i in range(2)]


def integrate(Q, dt=0.001, steps=8000, report=()):
    P = [[0.0, 0.0], [0.0, 0.0]]
    for k in range(1, steps + 1):
        D = residual(Q, P)
        P = [[P[i][j] + dt * D[i][j] for j in range(2)] for i in range(2)]
        if k in report:
            print(f"    tau {k * dt:5.1f}   P11 {P[0][0]:12.3f}   P22 {P[1][1]:.6f}")
    return P


print("Q = I  (the unreachable mode is priced):")
integrate([[1.0, 0.0], [0.0, 1.0]], report={2000, 4000, 6000, 8000})

print("Q = diag(0, 1)  (the unreachable mode is free):")
P = integrate([[0.0, 0.0], [0.0, 1.0]], report={2000, 8000})
K = [P[1][0], P[1][1]]
cl = [[A[i][j] - B[i][0] * K[j] for j in range(2)] for i in range(2)]
print("    K =", [round(v, 6) for v in K])
print("    closed loop diag:", [round(cl[0][0], 6), round(cl[1][1], 6)])
```

```text
Q = I  (the unreachable mode is priced):
    tau   2.0   P11       26.690   P22 0.412532
    tau   4.0   P11     1478.118   P22 0.414208
    tau   6.0   P11    80407.487   P22 0.414214
    tau   8.0   P11  4372624.708   P22 0.414214
Q = diag(0, 1)  (the unreachable mode is free):
    tau   2.0   P11        0.000   P22 0.412532
    tau   8.0   P11        0.000   P22 0.414214
    K = [0.0, 0.414214]
    closed loop diag: [1.0, -1.414214]
```

The first failure is loud. An unstable mode the actuator cannot reach, and which the cost
does price, has an infinite cost-to-go, and $P_{11}$ grows like $e^{2\tau}$ saying so.
Stabilisability of $(A, B)$ is the condition, and a violated one announces itself in the
first few seconds of integration.

The second failure is silent, and it is the one to be afraid of. Price that same
unreachable mode at zero and the iteration converges in a few seconds to
$P = \text{diag}(0,\ \sqrt{2}-1)$: symmetric, positive semidefinite, residual at machine
precision, every box ticked. The gain it returns leaves the growing mode untouched, and
the closed-loop plant still has a pole at $+1$. Detectability of $(A, Q^{1/2})$ is the
condition, and nothing about the converged matrix reveals its absence — which is why the
labs test the eigenvalues of `A - B @ K` separately from the residual, and why a $Q$ with
a zero on the diagonal deserves a moment of thought about what is now invisible to the
cost.

One numerical caveat sits on top of both. Forward Euler on the Riccati equation is
forward Euler, with the step limit module 1 of CTRL510 derived: it is stable only while
$\Delta$ is small against the fastest mode of the transient. On a stiff plant — the
capstone's shaft resonance, for one — the iteration diverges for reasons that have
nothing to do with the plant being uncontrollable, and the fix is a smaller step and more
of them, which is what the lab hint tells you to reach for first.
''',
                },
            ],
            "quiz": {
                "title": "Integrating into a solution, and knowing you arrived",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A colleague solves the algebraic Riccati equation with a Newton iteration and shows you a symmetric $P$ whose residual is $3 \\times 10^{-15}$. What has been established?",
                        "opts": [
                            "That $P$ solves the equation, and separately that the gain it produces is optimal",
                            "That $P$ solves the equation, but not that the gain it produces stabilises the plant",
                            "That $P$ is the unique symmetric solution, since a quadratic equation admits two roots",
                            "Nothing at all, because the residual is computed from the same $P$ being tested",
                        ],
                        "a": 1,
                        "whys": [
                            r"Solving the equation is genuinely established. Optimality is a second claim resting on $P \succeq 0$, and the double integrator has a second real symmetric solution with the same residual whose gain mirrors every pole into the right half-plane.",
                            r"A residual of $3 \times 10^{-15}$ is a statement about the equation, not about which root you landed on.",
                            r"A matrix quadratic has more than one symmetric real root in general — the double integrator with $Q = I$ has two, differing in the sign of $p_3$ — and only one of them is a cost.",
                            r"The residual is a real test: it substitutes the candidate into the definition of the problem and asks whether it vanishes. What it cannot do is tell you which of the roots you found.",
                        ],
                        "why": r"""
The double integrator with $Q = I$, $R = 1$ has two real symmetric solutions,
$\pm\begin{bmatrix} \sqrt{3} & 1 \\ 1 & \sqrt{3}\end{bmatrix}$ up to the sign of the
diagonal, and both have a residual at machine precision. One puts the closed-loop poles
at $-0.866 \pm 0.5j$ and the other at $+0.866 \pm 0.5j$. The condition that separates
them is $P \succeq 0$, which comes from the cost interpretation rather than from the
equation: $x^\top P x$ is the price of the future, and a price is not negative. Check
the residual, then check the eigenvalues of $P$, then check the eigenvalues of $A - BK$.
""",
                    },
                    {
                        "q": "Why does integrating $dP/d\\tau$ forward from $P = 0$ land on the stabilising root rather than the other one?",
                        "opts": [
                            "Forward Euler is only stable near the stabilising root, so the other one repels it",
                            "$P(\\tau)$ is the optimal cost over a window of length $\\tau$, so it stays semidefinite",
                            "The other root is not reachable because it is not symmetric, and $P$ stays symmetric",
                            "Starting from zero happens to be much closer to that root, so the iteration converges there first",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is something to this — the anti-stable root is repelling for this flow — but the reason the flow never approaches it is where the flow starts and what the trajectory means, not a property of the discretisation. Halving the step changes nothing about which root is reached.",
                            r"$P(0) = 0$ is the horizon with no terminal cost, and a cost cannot go negative.",
                            r"The other root is perfectly symmetric. For the double integrator it is $-\begin{bmatrix} \sqrt{3} & -1 \\ -1 & \sqrt{3}\end{bmatrix}$, and symmetry is no help in telling the two apart.",
                            r"Distance to a root is not what decides it. The trajectory is confined to the positive-semidefinite cone by what $P(\tau)$ means, and the other root sits outside that cone at any distance.",
                        ],
                        "why": r"""
$P(0) = 0$ is the finite-horizon problem with no terminal cost, so $x^\top P(\tau)x$ is
the optimal cost over a window of $\tau$ seconds — non-negative for every $\tau$, and
non-decreasing in $\tau$ because a longer window adds non-negative running cost to a
shorter one. A non-decreasing family of positive-semidefinite matrices that is bounded
above converges, and its limit is positive semidefinite. The negative-definite twin lies
outside the cone the trajectory is confined to, so it is unreachable from this start —
the root is chosen by the initial condition, not selected afterwards.
""",
                    },
                    {
                        "q": "A solver stops when the change in $P$ over one step falls below $10^{-6}$. Halving `dt` and rerunning, what happens to the answer?",
                        "opts": [
                            "It improves, because a smaller step integrates the differential equation more accurately",
                            "It is unchanged, since the stopping rule is about $P$ rather than about the step size",
                            "It gets worse, because the step is `dt` times the residual and the rule now fires sooner",
                            "It diverges, because forward Euler needs a step above a minimum to make progress",
                        ],
                        "a": 2,
                        "whys": [
                            r"Accuracy per step does improve, which is exactly what makes this tempting. But the run terminates earlier in $\tau$, and stopping short of the fixed point costs far more than the truncation error saved.",
                            r"The rule is about the step, and the step carries a factor of `dt`.",
                            r"Halving `dt` halves the step for the same residual, so the tolerance is met at twice the residual, further from the solution.",
                            r"Forward Euler has an upper step limit, not a lower one. Smaller steps here are stable and accurate per step; the defect is entirely in when the loop decides to stop.",
                        ],
                        "why": r"""
The update is `P += dt * residual(P)`, so a step-change test is a residual test scaled by
a number you chose. With a tolerance of $10^{-5}$ on the double integrator the run stops
at $\tau = 4.49$ with `dt = 0.002` and a residual of $5 \times 10^{-3}$, and at
$\tau = 2.73$ with `dt = 0.0001` and a residual of $10^{-1}$ — a gain of 1.6725 against
a true 1.7321. The finer integration gives the worse answer and reports success. Test
the residual of the algebraic equation, which is a property of the candidate and not of
the integrator.
""",
                    },
                    {
                        "q": "A plant has an unstable mode that the actuator cannot reach, and $Q$ prices that mode. What does the iteration do?",
                        "opts": [
                            "It converges, but to a $P$ that is indefinite rather than semidefinite",
                            "It converges to the right answer, and the resulting closed loop keeps the unstable pole",
                            "It converges more slowly than usual, and the residual settles at a small non-zero floor",
                            "The entries of $P$ along that mode grow without bound, so nothing converges",
                        ],
                        "a": 3,
                        "whys": [
                            r"Indefiniteness is what the *other* root of a solvable problem looks like. Here there is no finite solution to converge to at all, of any definiteness.",
                            r"That is the description of a *detectability* failure, where the mode is unreachable and also unpriced. Priced, it costs an unbounded amount and the iteration cannot settle.",
                            r"There is no floor. A mode that grows and is charged for accumulates cost exponentially, so the residual does not approach any small value and the entries run off to infinity.",
                            r"An unstable mode nothing can act on, integrated against a positive price, has an infinite cost-to-go — and $P_{11}$ grows like $e^{2\tau}$ reporting it.",
                        ],
                        "why": r"""
Stabilisability of $(A, B)$ is what fails. With $A = \text{diag}(1, -1)$, $B$ reaching
the decaying mode alone and $Q = I$, the run gives $P_{11}$ of 26.7 at $\tau = 2$, 1478
at $\tau = 4$ and $4.4 \times 10^6$ at $\tau = 8$ — the cost of holding a mode that grows
and cannot be touched. This is the benign failure, because it is impossible to miss. The
dangerous one is the same plant with that mode priced at zero, where the iteration
converges to a tidy positive-semidefinite matrix and hands back a gain that leaves the
pole at $+1$ exactly where it was.
""",
                    },
                    {
                        "q": "Partway through the integration, at $\\tau = 1$, the running value of $K$ is $[\\,0.389\\ \\ 0.965\\,]$ while the limit is $[\\,1\\ \\ 1.732\\,]$. What is that intermediate gain?",
                        "opts": [
                            "The optimal gain for a problem with one second of horizon remaining",
                            "An unconverged iterate with no meaning until the residual vanishes",
                            "The optimal gain for a plant whose time constants are one second long",
                            "The gain that would result from weights one second of integration smaller",
                        ],
                        "a": 0,
                        "whys": [
                            r"$P(\tau)$ solves the finite-horizon problem with $\tau$ left to run, so the gain read off it is the one that problem asks for.",
                            r"Every iterate is the exact answer to a shorter-horizon problem, which is what makes the whole method a trajectory between meaningful states rather than a numerical search through meaningless ones.",
                            r"The plant is a double integrator and has no time constant at all; both its poles are at the origin. The second in question is a property of the horizon being considered, not of the hardware.",
                            r"The weights are fixed throughout the run and never enter the iteration except as the constant $Q$ and $R$. What changes along the trajectory is the horizon, and the gain grows as it lengthens.",
                        ],
                        "why": r"""
Integrating in time-to-go means $P(\tau)$ is the cost-to-go with $\tau$ seconds left, so
every iterate along the way answers a real question. The intermediate gain is smaller
than the limit for a reason worth keeping: a controller with one second left has less
future error to prevent, so it has less reason to spend on effort now. Read the whole
trajectory backwards and it is the time-varying gain schedule of the finite-horizon
design; run it far enough that it stops moving and it is the constant infinite-horizon
gain.
""",
                    },
                    {
                        "q": "The Riccati iteration on the capstone's flexible-shaft plant diverges within a few hundred steps. Which explanation should be tested first?",
                        "opts": [
                            "The shaft resonance is fast enough that the Euler step exceeds its stability limit",
                            "The plant is not stabilisable, so no finite solution to the Riccati equation exists",
                            "$R$ is too small, so the quadratic term overwhelms the linear ones",
                            "$P$ has lost its symmetry, and an asymmetric iterate cannot converge",
                        ],
                        "a": 0,
                        "whys": [
                            r"Diverging within a few hundred steps is the signature of an integrator whose step is too large for the fastest mode present, and the four-state shaft model carries an 11 rad/s resonance.",
                            r"Worth ruling out, and cheap to: form the controllability matrix, or watch which entries grow. A stabilisability failure grows the cost of one mode over seconds, while an Euler instability blows up the whole matrix in a few hundred steps whatever the plant is.",
                            r"A small $R$ makes the gain large and the transient fast, which does tighten the step limit — so this is the same defect seen through the weights rather than through the integrator, and the fix is still the step.",
                            r"Symmetry is preserved exactly by the update, since every term of the residual is symmetric when $P$ is. An asymmetric iterate means a dropped transpose in the residual, and that shows up as a wrong answer rather than as divergence.",
                        ],
                        "why": r"""
The differential Riccati equation is integrated with forward Euler, and forward Euler has
the step limit CTRL510 derived: it is stable only while $\Delta$ is small against the
fastest mode of the transient. A shaft resonance near 11 rad/s, and a transient made
faster still by a small $R$, put that limit well below a step chosen for a slower plant.
Halve the step and double the count before suspecting the model. If the residual then
falls to machine precision the diagnosis is confirmed, and if one mode of $P$ instead
grows steadily over seconds while the rest settle, the problem is the plant rather than
the arithmetic.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "Where the Riccati solution puts the poles",
                "visualiser": "pole-place",
                "minutes": 7,
                "initial": {"p1": -1, "p2": -9.9},
                "brief": r'''
The same double integrator, still placed by hand — but now compare each pair you dial
in against what the Riccati equation returns for a given $R$, with $Q = I$ throughout.

The visualiser reports $K = [p_1 p_2,\ -(p_1+p_2)]$. The lab will compute the LQR gains
for the same plant; these are the ones to compare against.
''',
                "notice": [
                    "The opening pair, $-1$ and $-9.9$, gives $K = [9.90,\\ 10.90]$. That is within a percent of the $[10.00,\\ 10.95]$ the Riccati equation returns for $R = 0.01$ — so cheap control really does split the poles this far apart.",
                    "Now try to reach settling under 2 s with a peak effort under 4. It cannot be done: equal poles at $-p$ demand exactly $p^2$, and 2 s needs $p$ near 3. The Riccati equation is the machine that finds the best available compromise instead of you hunting for it.",
                    "Every pair you can drag here is real, but at $R = 1$ the Riccati equation returns $-0.87 \\pm 0.5j$, which these two sliders cannot express. Placing poles and minimising a cost are genuinely different searches, and only one of them scales past two states.",
                ],
            },
            "derive": {
                "title": "One step of the recursion, in one dimension",
                "minutes": 15,
                "vars": ["a", "b", "p", "q", "r", "k", "x", "u", "P", "Q", "R", "K"],
                "brief": r'''
Take the discrete-time version, where the recursion is easiest to see. The plant is
$x_{n+1} = a x_n + b u_n$, and suppose the cost of every future step from state $x$ is
already known to be $p x^2$. Then the best you can do from one step earlier is

$$\min_u \left[\, q x^2 + r u^2 + p\,(a x + b u)^2 \,\right]$$

Do that minimisation, and the coefficient of $x^2$ that comes out is the value of $p$
one step further back. Iterating that map is the whole algorithm.
''',
                "steps": [
                    {
                        "prompt": "Differentiate the bracket with respect to $u$, set it to zero, and write the gain $k$ for which $u = -kx$. Give it in terms of $a$, $b$, $p$ and $r$.",
                        "answer": "\\frac{a b p}{r + b^2 p}",
                        "hint": "The derivative is $2ru + 2bp(ax + bu)$. Collect the $u$ terms on one side.",
                        "deconstruct": [
                            "Setting the derivative to zero: $ru + bp(ax + bu) = 0$, so $u(r + b^2 p) = -abpx$.",
                            "That is $u = -kx$ with $k$ the ratio you were asked for.",
                        ],
                    },
                    {
                        "prompt": "Write the closed-loop factor $a - bk$ using the same symbols.",
                        "answer": "\\frac{a r}{r + b^2 p}",
                        "hint": "Put $a$ over the common denominator $r + b^2p$ before subtracting.",
                        "deconstruct": [
                            "$a - bk = a - \\frac{ab^2p}{r + b^2p} = \\frac{a(r + b^2p) - ab^2p}{r + b^2p}$.",
                            "The $ab^2p$ terms cancel in the numerator.",
                        ],
                    },
                    {
                        "prompt": "The new value is $q + rk^2 + p(a - bk)^2$. Substitute and simplify it to two terms.",
                        "given": "Both squares share the denominator $(r + b^2p)^2$, and their numerators add to $a^2 r p (b^2 p + r)$.",
                        "answer": "q + \\frac{a^2 r p}{r + b^2 p}",
                        "hint": "$rk^2 = \\frac{a^2b^2rp^2}{(r+b^2p)^2}$ and $p(a-bk)^2 = \\frac{a^2r^2p}{(r+b^2p)^2}$. Add them and factor $a^2rp$ out of the numerator.",
                        "deconstruct": [
                            "The two numerators are $a^2 b^2 r p^2$ and $a^2 r^2 p$, which sum to $a^2 r p (b^2 p + r)$.",
                            "One factor of $(r + b^2 p)$ cancels against the denominator.",
                        ],
                    },
                    {
                        "prompt": "Switch the control off by setting $b = 0$, so the recursion is just $p_{new} = q + a^2 p$. Write the value $p$ settles at.",
                        "answer": "\\frac{q}{1 - a^2}",
                        "hint": "A fixed point is a $p$ that the map returns unchanged. Set $p = q + a^2 p$ and solve.",
                        "deconstruct": [
                            "$p - a^2 p = q$.",
                            "Factor and divide.",
                        ],
                    },
                ],
                "closing": r'''
The last answer is the warning label. With no control the recursion converges only when
$|a| < 1$ — an unstable mode accumulates infinite cost, exactly as it should. Turn the
control back on and the $b^2p$ in the denominator grows with $p$, which is what pulls
the recursion back down to a finite fixed point even for an unstable plant.

The continuous-time version behaves the same way. The lab integrates

$$\frac{dP}{d\tau} = A^\top P + P A - P B R^{-1} B^\top P + Q$$

forward in time-to-go $\tau$ from $P = 0$, and stops when it stops moving. That is not
an approximation to the algebraic solution; it is a trajectory that lands on it.
''',
            },
            "blanks": {
                "title": "The Riccati equation, term by term",
                "minutes": 9,
                "caption": "lqr.py — the quadratic that has no formula",
                "lang": "python",
                "brief": r"""
A matrix quadratic cannot be solved the way a scalar one can, so it is solved by running
into it. Fill the four holes and the whole method is on one screen.
""",
                "listing": """# The algebraic Riccati equation:
#
#     A.T @ P + P @ A - ___ + Q = 0
#
# No closed form. Integrate in time-to-go until it stops moving:
#
#     Pdot = A.T @ P + P @ A - P @ B @ inv(R) @ B.T @ P + Q
#     P    = P + dt * Pdot
#
# The optimal gain that falls out is
#
#     K = ___
#
# Stop when the ___ is below tolerance,
# and check that the P you converged on is ___ .
""",
                "blanks": [
                    {
                        "prompt": "The term that makes it quadratic.",
                        "hole": "?",
                        "opts": [
                            "P @ B @ inv(R) @ B.T @ P",
                            "P @ B @ R @ B.T @ P",
                            "B @ inv(R) @ B.T",
                            "P @ P",
                        ],
                        "a": 0,
                        "why": "$P$ appears on both sides of $BR^{-1}B^\\top$, which is what makes this a quadratic rather than a Lyapunov equation. The $R^{-1}$ is the price of effort entering *inversely*: expensive control means a small term, which means less of the stabilising correction.",
                        "whys": [
                            "$P$ appears on both sides of $BR^{-1}B^\\top$, which is what makes this a quadratic rather than a Lyapunov equation. The $R^{-1}$ is the price of effort entering *inversely*: expensive control means a small term, which means less of the stabilising correction.",
                            "$R$ rather than $R^{-1}$ inverts the meaning of the weight: raising the price of control would then make the controller more aggressive, not less.",
                            "Without the two $P$ factors this is linear in $P$ — a Lyapunov equation, which does have a closed-form solution and answers a different question.",
                            "Quadratic in $P$, but with no $B$ in it the input never enters, so the answer would not depend on what the actuator can do.",
                        ],
                    },
                    {
                        "prompt": "From P to the gain.",
                        "hole": "?",
                        "opts": ["inv(R) @ B.T @ P", "inv(R) @ B @ P", "R @ B.T @ P", "P @ B @ inv(R)"],
                        "a": 0,
                        "why": "$K = R^{-1}B^\\top P$, and $u = -Kx$. Check the shapes: $P$ is $n \\times n$, $B^\\top$ is $m \\times n$, $R^{-1}$ is $m \\times m$, so $K$ is $m \\times n$ and $Kx$ is an input. Any other ordering fails to conform.",
                        "whys": [
                            "$K = R^{-1}B^\\top P$, and $u = -Kx$. Check the shapes: $P$ is $n \\times n$, $B^\\top$ is $m \\times n$, $R^{-1}$ is $m \\times m$, so $K$ is $m \\times n$ and $Kx$ is an input. Any other ordering fails to conform.",
                            "$B$ rather than $B^\\top$: the dimensions do not conform unless the system happens to be square, and where they do the result is not the minimiser.",
                            "Multiplying by $R$ instead of its inverse makes the gain grow with the price of control, which is backwards.",
                            "The factors are in an order that does not produce an $m \\times n$ matrix, so $Kx$ is not an input vector.",
                        ],
                    },
                    {
                        "prompt": "How do you know it has actually converged?",
                        "hole": "?",
                        "opts": [
                            "residual of the algebraic equation",
                            "change in P over the last step",
                            "number of iterations completed",
                            "sign of the eigenvalues of P",
                        ],
                        "a": 0,
                        "why": "Substitute your $P$ back into $A^\\top P + PA - PBR^{-1}B^\\top P + Q$ and look at the norm. That is the only test that checks the answer rather than the process — a small step change proves the iteration has slowed down, which it also does when it stalls short of the solution or when `dt` is too small.",
                        "whys": [
                            "Substitute your $P$ back into $A^\\top P + PA - PBR^{-1}B^\\top P + Q$ and look at the norm. That is the only test that checks the answer rather than the process — a small step change proves the iteration has slowed down, which it also does when it stalls short of the solution or when `dt` is too small.",
                            "A tempting proxy and a genuinely misleading one: halve `dt` and the step change halves too, with no improvement in the answer at all. It measures your integrator, not your solution.",
                            "A fixed iteration count is a hope, not a test. It gives no signal when the problem is badly conditioned and the run needed ten times longer.",
                            "$P$ being positive semi-definite is necessary but nowhere near sufficient — plenty of wrong matrices are.",
                        ],
                    },
                    {
                        "prompt": "What must the converged P look like?",
                        "hole": "?",
                        "opts": [
                            "symmetric and positive semi-definite",
                            "skew-symmetric",
                            "diagonal",
                            "orthogonal",
                        ],
                        "a": 0,
                        "why": "$x^\\top Px$ is the cost-to-go from state $x$, and a cost cannot be negative — so $P \\succeq 0$, and only its symmetric part contributes to the quadratic form anyway. A visibly asymmetric result after integration means a transpose has been dropped somewhere.",
                        "whys": [
                            "$x^\\top Px$ is the cost-to-go from state $x$, and a cost cannot be negative — so $P \\succeq 0$, and only its symmetric part contributes to the quadratic form anyway. A visibly asymmetric result after integration means a transpose has been dropped somewhere.",
                            "A skew-symmetric matrix gives $x^\\top Px = 0$ for every $x$, so the cost-to-go would be zero from everywhere.",
                            "Diagonal only in special cases. Off-diagonal entries are how the cost couples the states, and a plant with any cross-coupling produces them.",
                            "Orthogonality is unrelated to the cost interpretation and is not implied by the equation.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Solve the algebraic Riccati equation, and prove it",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
Three functions, and no library allowed to do the hard one for you.

- `care_residual(A, B, Q, R, P)` returns the matrix
  $A^\top P + P A - P B R^{-1} B^\top P + Q$. This is the definition of the problem and
  also the only honest test of an answer.
- `solve_care(A, B, Q, R, dt, steps)` starts at $P = 0$ and repeatedly applies
  `P = P + dt * care_residual(...)`, returning the final `P`. Defaults `dt=0.002`,
  `steps=10000` are enough for every plant here.
- `lqr(A, B, Q, R)` returns the pair `(K, P)` with $K = R^{-1}B^\top P$, shaped `(1, n)`
  and `(n, n)`.

Use `np.linalg.inv` on `R`; it is 1×1 in every case here but write it as a matrix
inverse anyway, because that is what the formula says.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def care_residual(A, B, Q, R, P):
    """A.T @ P + P @ A - P @ B @ inv(R) @ B.T @ P + Q."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)
    P = np.asarray(P, dtype=float)
    # TODO: four terms, in the order written above.
    return np.zeros_like(Q)


def solve_care(A, B, Q, R, dt=0.002, steps=10000):
    """Run the differential Riccati equation in time-to-go from P = 0."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    P = np.zeros((n, n))
    # TODO: `steps` times, P = P + dt * care_residual(A, B, Q, R, P)
    return P


def lqr(A, B, Q, R):
    """Return (K, P): the optimal gain row and the cost matrix behind it."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    # TODO: solve for P, then K = inv(R) @ B.T @ P
    return np.zeros((1, n)), np.zeros((n, n))


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    K, P = lqr(A, B, np.eye(2), np.array([[1.0]]))
    print("K        =", np.round(K, 6).tolist())
    print("residual =", float(np.linalg.norm(care_residual(A, B, np.eye(2), np.array([[1.0]]), P))))
    print("poles    =", np.round(np.linalg.eigvals(A - B @ K), 6).tolist())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def care_residual(A, B, Q, R, P):
    """A.T @ P + P @ A - P @ B @ inv(R) @ B.T @ P + Q."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)
    P = np.asarray(P, dtype=float)
    return A.T @ P + P @ A - P @ B @ np.linalg.inv(R) @ B.T @ P + Q


def solve_care(A, B, Q, R, dt=0.002, steps=10000):
    """Run the differential Riccati equation in time-to-go from P = 0."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    P = np.zeros((n, n))
    for _ in range(steps):
        P = P + dt * care_residual(A, B, Q, R, P)
    return P


def lqr(A, B, Q, R):
    """Return (K, P): the optimal gain row and the cost matrix behind it."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    R = np.asarray(R, dtype=float)
    P = solve_care(A, B, Q, R)
    K = np.linalg.inv(R) @ B.T @ P
    return K, P


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    K, P = lqr(A, B, np.eye(2), np.array([[1.0]]))
    print("K        =", np.round(K, 6).tolist())
    print("residual =", float(np.linalg.norm(care_residual(A, B, np.eye(2), np.array([[1.0]]), P))))
    print("poles    =", np.round(np.linalg.eigvals(A - B @ K), 6).tolist())
'''}],
                "hints": [
                    "`care_residual` is a transcription, not a derivation: `A.T @ P + P @ A - P @ B @ np.linalg.inv(R) @ B.T @ P + Q`.",
                    "Watch the transposes. `A.T @ P` and `P @ A` are different matrices, and swapping them breaks the symmetry of the answer.",
                    "`solve_care` is a loop of one line. Starting from `P = np.zeros((n, n))` is not an arbitrary choice — it is the finite-horizon problem with no terminal cost.",
                    "If the iteration diverges, the step is too large for the plant, not the method: halve `dt` and double `steps`.",
                ],
                "tests": [
                    {"name": "the residual is the Riccati expression and nothing else", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
_res = care_residual(_A, _B, np.eye(2), np.array([[1.0]]), np.eye(2))
_want = np.array([[1.0, 1.0], [1.0, 0.0]])
assert _res.shape == (2, 2), f"the residual is n x n, got {_res.shape}"
assert np.max(np.abs(_res - _want)) < 1e-12, \
    f"at P = I this plant gives [[1, 1], [1, 0]]; got {_res.tolist()} — check the transposes"
'''},
                    {"name": "the iteration drives the residual to zero", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
_P = solve_care(_A, _B, np.eye(2), np.array([[1.0]]))
_n = float(np.linalg.norm(care_residual(_A, _B, np.eye(2), np.array([[1.0]]), _P)))
assert _n < 1e-6, \
    f"a solution of the algebraic equation has zero residual; this one has norm {_n:.3e}"
'''},
                    {"name": "the solution is symmetric and positive definite", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
_P = solve_care(_A, _B, np.eye(2), np.array([[1.0]]))
assert np.max(np.abs(_P - _P.T)) < 1e-9, \
    f"P is a cost-to-go quadratic form, so it must be symmetric; got {_P.tolist()}"
_ev = np.linalg.eigvalsh(_P)
assert float(np.min(_ev)) > 0, \
    f"every non-zero state has positive cost, so P must be positive definite; eigenvalues {_ev.tolist()}"
'''},
                    {"name": "the scalar case reproduces module one", "code": r'''
import numpy as np
_P = solve_care(np.array([[1.0]]), np.array([[1.0]]), np.array([[1.0]]), np.array([[1.0]]))
assert abs(float(_P[0, 0]) - (1.0 + np.sqrt(2.0))) < 1e-6, \
    f"a=b=q=r=1 has the closed-form solution 1 + sqrt(2) = 2.414214, got {float(_P[0,0]):.6f}"
_K, _ = lqr(np.array([[-0.5]]), np.array([[1.5]]), np.array([[2.0]]), np.array([[0.5]]))
assert _K.shape == (1, 1), f"K should be (1,1) for a one-state plant, got {_K.shape}"
_pole = -0.5 - 1.5 * float(_K[0, 0])
assert abs(_pole + np.sqrt(0.25 + 2.0 * 2.25 / 0.5)) < 1e-6, \
    f"the closed-loop pole should be -sqrt(a^2 + q b^2/r) = -3.041381, got {_pole:.6f}"
'''},
                    {"name": "an unstable plant is stabilised", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [3.0, 0.2]])
_B = np.array([[0.0], [1.0]])
assert float(np.max(np.real(np.linalg.eigvals(_A)))) > 0, "this fixture is meant to be unstable"
_K, _P = lqr(_A, _B, np.eye(2), np.array([[1.0]]))
assert _K.shape == (1, 2), f"K should be (1,2), got {_K.shape}"
_cl = np.real(np.linalg.eigvals(_A - _B @ _K))
assert float(np.max(_cl)) < 0, f"the closed loop should be stable; poles came out {_cl.tolist()}"
assert abs(float(_K[0, 0]) - 6.16227766) < 1e-4, \
    f"expected k1 = 6.162278 for this plant with Q = I, R = 1; got {float(_K[0,0]):.6f}"
'''},
                    {"name": "expensive control buys a smaller gain", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
_cheap, _ = lqr(_A, _B, np.eye(2), np.array([[0.01]]))
_dear, _ = lqr(_A, _B, np.eye(2), np.array([[1.0]]))
assert abs(float(_cheap[0, 0]) - 10.0) < 1e-4, \
    f"with Q = I and R = 0.01 the position gain is 1/sqrt(R) = 10; got {float(_cheap[0,0]):.6f}"
assert abs(float(_dear[0, 0]) - 1.0) < 1e-4, \
    f"with R = 1 it is 1; got {float(_dear[0,0]):.6f}"
assert np.linalg.norm(_cheap) > 5 * np.linalg.norm(_dear), \
    "cheaper effort must produce a substantially larger gain, not a smaller one"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "The Kalman filter as the dual of LQR",
            "summary": "Choose the correction that minimises the variance of what is left. The algebra that comes out is the regulator's, transposed.",
            "concepts": [
                "The filter carries two things: an estimate, and a covariance saying how much to trust it.",
                "Predict inflates the covariance by the process noise; correct deflates it by what the measurement revealed.",
                "The gain $K = PC^\\top(CPC^\\top + R)^{-1}$ is the choice that minimises the trace of the posterior covariance.",
                "Duality: $(A, B, Q, R) \\to (A^\\top, C^\\top, W, V)$ turns the regulator Riccati equation into the estimator's.",
                "The covariance recursion runs without ever seeing a measurement — the gain schedule is known before the sensor is switched on.",
            ],
            "read": [
                {
                    "title": "The speed the sensor was too noisy to see",
                    "minutes": 16,
                    "body": r'''
A target is crossing in front of a range finder at about 1.5 m/s. The finder reports a
position ten times a second with a standard deviation of half a metre, and it reports
nothing else — no speed, no acceleration, one number per sample. The job is to know
where the target is and how fast it is going.

Two fixes suggest themselves before any theory does. Average the last ten samples, since
averaging kills noise. And take the difference of consecutive samples over the interval,
since that is what a derivative is. Both are run here on the same stream:

```python
import math
import random

DT = 0.1
SIG_V = 0.5          # the position sensor, in metres
SIG_W = 0.02         # how much the speed wanders between samples


def track(steps=300, seed=11):
    """A target at roughly constant speed, and what the sensor reports. Deterministic."""
    rng = random.Random(seed)

    def gauss():
        u1 = max(rng.random(), 1e-12)
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * rng.random())

    pos, vel = 0.0, 1.5
    truth, meas = [], []
    for _ in range(steps):
        truth.append((pos, vel))
        meas.append(pos + SIG_V * gauss())
        pos, vel = pos + DT * vel, vel + SIG_W * gauss()
    return truth, meas


def rmse(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / len(a))


truth, meas = track()
tp = [t[0] for t in truth]
tv = [t[1] for t in truth]

print("raw position rmse        :", round(rmse(meas, tp), 4))

N = 10
avg = [sum(meas[max(0, i - N + 1):i + 1]) / len(meas[max(0, i - N + 1):i + 1])
       for i in range(len(meas))]
print("10-sample average rmse   :", round(rmse(avg[N:], tp[N:]), 4))

fd = [(meas[i] - meas[i - 1]) / DT for i in range(1, len(meas))]
print("two-point velocity rmse  :", round(rmse(fd, tv[1:]), 4))
print("true speed               :", tv[0])
print("sqrt(2)*sigma_v/DT       :", round(math.sqrt(2) * SIG_V / DT, 4))
```

```text
raw position rmse        : 0.5127
10-sample average rmse   : 0.7061
two-point velocity rmse  : 7.2543
true speed               : 1.5
sqrt(2)*sigma_v/DT       : 7.0711
```

The average made the position worse. A trailing average of $N$ samples divides the noise
by $\sqrt{N}$, taking 0.51 m down to 0.16 m, but its output is centred $(N-1)/2 = 4.5$
samples behind the present, and in 0.45 s a target at 1.5 m/s has travelled 0.675 m. The
total is $\sqrt{0.675^2 + 0.16^2} = 0.69$, and the run gives 0.71. The trade was made and
lost, and it was lost by a margin the arithmetic predicted in advance.

The finite difference is worse than that. It divides a difference of two independent
noises by 0.1 s, so its standard deviation is $\sqrt{2}\,\sigma_v/\Delta t = 7.07$ m/s.
The quantity being estimated is 1.5 m/s. The estimate is not degraded; it is nearly five
times larger than the thing it is estimating, and none of that comes from the target.

## The amount of smoothing is not a constant

What both fixes have in common is a fixed amount of smoothing chosen in advance. Ten
samples, or two — a number picked once, with no reference to how good the estimate
already is. That is the defect, and once it is named the repair is forced.

Suppose that before a measurement arrives you hold an estimate $\hat{x}$ whose error
$e = x - \hat{x}$ has variance $p$. The measurement is $y = x + v$ with $\text{Var}(v) = r$,
and $v$ is independent of $e$. Correct with a blend of the two,

$$\hat{x}_{\text{new}} = \hat{x} + k\,(y - \hat{x})$$

and ask what $k$ should be, assuming nothing about it. The new error is

$$x - \hat{x}_{\text{new}} = e - k(x + v - \hat{x}) = (1-k)e - kv$$

Independence means no cross term, and scaling a random variable by $c$ scales its
variance by $c^2$, so the variance that survives is $(1-k)^2 p + k^2 r$. Differentiate
with respect to $k$ and set the result to zero:

$$-2(1-k)p + 2kr = 0 \;\Longrightarrow\; k = \frac{p}{p + r}$$

Substituting back, and using $1 - k = r/(p+r)$, the surviving variance is
$p_{\text{new}} = (1-k)p = \dfrac{pr}{p+r}$, which is the same statement as

$$\frac{1}{p_{\text{new}}} = \frac{1}{p} + \frac{1}{r}$$

Reciprocal variances add. That form settles the limits without further work: with a
perfect sensor $r \to 0$ the gain goes to 1 and the estimate becomes the measurement;
with a useless sensor $r \to \infty$ the gain goes to 0 and the estimate is untouched;
and $p_\text{new}$ is below both $p$ and $r$ for every finite pair, so a measurement can
never make you less certain, whatever its quality. This is the derivation
*The correction that minimises what is left over*, with the algebra written out — and
notice what it was not: nobody assumed the correction should be a blend of that shape.
The shape was assumed, the coefficient was derived, and the coefficient is the whole
filter.

## Closing the loop in time

One correction is not a filter. Between samples the truth moves in a way the model does
not fully capture, and that uncertainty is charged as a process variance $q$: the prior
for the next step is the posterior from this one plus $q$. Chain the two and ask for a
$p$ that a full cycle returns unchanged:

$$p = \frac{pr}{p+r} + q \;\Longrightarrow\; p(p+r) = pr + q(p+r)
    \;\Longrightarrow\; p^2 - qp - qr = 0$$

with positive root $p = \frac{q}{2} + \frac{1}{2}\sqrt{q^2 + 4qr}$. For the sandbox
*The gain the variances imply*, running at $q = 0.02$ and $r = 0.5$:

```python
import math

q, r = 0.02, 0.5          # how fast the truth wanders; how noisy the sensor is

p = 1.0                   # the prior variance before the first measurement
print(" step   prior p    gain k    posterior")
for step in range(1, 13):
    k = p / (p + r)
    post = p * r / (p + r)
    if step <= 5 or step in (8, 12):
        print(f"  {step:3d}   {p:8.6f}  {k:8.6f}  {post:9.6f}")
    p = post + q           # predict: the walk adds q before the next measurement

closed = q / 2.0 + 0.5 * math.sqrt(q * q + 4.0 * q * r)
print("closed form  p =", round(closed, 6),
      "  k =", round(closed / (closed + r), 6),
      "  posterior =", round(closed * r / (closed + r), 6))
```

```text
 step   prior p    gain k    posterior
    1   1.000000  0.666667   0.333333
    2   0.353333  0.414062   0.207031
    3   0.227031  0.312272   0.156136
    4   0.176136  0.260504   0.130252
    5   0.150252  0.231067   0.115534
    8   0.121040  0.194899   0.097450
   12   0.112547  0.183736   0.091868
closed form  p = 0.110499   k = 0.180998   posterior = 0.090499
```

The gain starts at 0.667 — an estimate that knows nothing takes the first measurement
nearly at face value — and settles on 0.181, which is the number the sandbox readout
shows for that pair of sliders. Now read the loop again and notice what is missing from
it. No measurement appears anywhere. The covariance recursion is driven by $q$, $r$ and
the model, and by nothing that any sensor reported. The entire gain schedule can be
computed, tabulated and burned into a device before the instrument is switched on, which
is a genuinely surprising property for something that is called an adaptive weighting.

## The same equations, transposed

With several states and a sensor that sees a combination of them, the blend becomes
$\hat{x} + K(y - C\hat{x})$ and the same minimisation — now of the trace of the posterior
covariance — gives

$$K = P C^\top \left(C P C^\top + R\right)^{-1}, \qquad
  P^+ = (I - KC)P, \qquad P^- \leftarrow A P A^\top + W$$

Write the steady-state version of that pair as one equation in continuous time and it is

$$A Y + Y A^\top - Y C^\top V^{-1} C Y + W = 0$$

Put it beside module 2's regulator equation, $A^\top P + PA - PBR^{-1}B^\top P + Q = 0$,
and read across: $A \to A^\top$, $B \to C^\top$, $Q \to W$, $R \to V$. The shapes agree,
because $B$ is $n \times m$ and $C^\top$ is $n \times p$, so a solver that never learns
what its arguments mean will solve either. That is not an analogy between two subjects
but one equation, which is why the lab in module 4 obtains its estimator gain from a
single call to `solve_care` with the arguments transposed.

## The tracker, filtered

Here is the two-state filter on the stream from the top of this reading: state
$[\,\text{position},\ \text{speed}\,]$, $A = \begin{bmatrix} 1 & \Delta t \\ 0 & 1\end{bmatrix}$,
$C = [\,1\ \ 0\,]$, $W = \text{diag}(10^{-6},\ 4\times10^{-4})$ and $V = 0.25$ — which is
$\sigma_v^2$, because the sensor really does have a half-metre standard deviation.

```python
import math
import random

DT = 0.1
SIG_V, SIG_W = 0.5, 0.02
W = [[1e-6, 0.0], [0.0, 4e-4]]
V = 0.25


def track(steps=300, seed=11, turn=None):
    rng = random.Random(seed)

    def gauss():
        u1 = max(rng.random(), 1e-12)
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * rng.random())

    pos, vel = 0.0, 1.5
    truth, meas = [], []
    for k in range(steps):
        if turn is not None and k == turn:
            vel = -1.0
        truth.append((pos, vel))
        meas.append(pos + SIG_V * gauss())
        pos, vel = pos + DT * vel, vel + SIG_W * gauss()
    return truth, meas


def run(meas):
    """Predict then correct. Written out for this A and C; the lab writes it as matrices."""
    x, P = [0.0, 0.0], [[1.0, 0.0], [0.0, 1.0]]
    est, sig = [], []
    for y in meas:
        x = [x[0] + DT * x[1], x[1]]                      # x <- A x
        P = [[P[0][0] + DT * (P[0][1] + P[1][0]) + DT * DT * P[1][1] + W[0][0],
              P[0][1] + DT * P[1][1]],
             [P[1][0] + DT * P[1][1], P[1][1] + W[1][1]]]  # P <- A P A^T + W
        S = P[0][0] + V                                    # S = C P C^T + V
        K = [P[0][0] / S, P[1][0] / S]                     # K = P C^T / S
        innov = y - x[0]
        x = [x[0] + K[0] * innov, x[1] + K[1] * innov]
        P = [[(1 - K[0]) * P[0][0], (1 - K[0]) * P[0][1]],
             [P[1][0] - K[1] * P[0][0], P[1][1] - K[1] * P[0][1]]]   # P <- (I - K C) P
        est.append(list(x))
        sig.append(math.sqrt(P[0][0]))
    return est, sig, P


def rmse(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / len(a))


truth, meas = track()
est, sig, P = run(meas)
print("filtered position rmse :", round(rmse([e[0] for e in est], [t[0] for t in truth]), 4))
print("filtered speed rmse    :",
      round(rmse([e[1] for e in est[100:]], [t[1] for t in truth[100:]]), 4))
print("steady position gain   :", round(P[0][0] / (P[0][0] + V), 6))
print("reported sigma at end  :", round(sig[-1], 4))

truth2, meas2 = track(turn=150)
est2, sig2, P2 = run(meas2)
print()
for k in (149, 155, 170, 200, 260):
    print(f"  step {k:3d}  reported sigma {sig2[k]:.4f}   actual error "
          f"{abs(est2[k][0] - truth2[k][0]):.4f}")
```

```text
filtered position rmse : 0.1676
filtered speed rmse    : 0.1122
steady position gain   : 0.078845
reported sigma at end  : 0.1463

  step 149  reported sigma 0.1463   actual error 0.0957
  step 155  reported sigma 0.1463   actual error 1.1801
  step 170  reported sigma 0.1463   actual error 1.9940
  step 200  reported sigma 0.1463   actual error 0.6897
  step 260  reported sigma 0.1463   actual error 0.1174
```

Position error falls from 0.513 to 0.168, a factor of three, and speed error falls to
0.112 against the finite difference's 7.25 — a factor of sixty-five, on a state the
instrument has never once reported. The speed estimate is manufactured entirely out of
the model: the filter knows that position accumulates speed, so a run of measurements
that keep landing on one side of the prediction is evidence about a quantity nobody
measured. The steady position gain here is 0.0788 rather than the scalar case's 0.181: a
model with a speed state to lean on has a better prediction to defend, so it can afford
to take each measurement less seriously.

## The mistake, and why it is tempting

The second half of that output is the mistake. At step 150 the target turns and moves off
at $-1.0$ m/s, which the constant-speed model has no room for. Twenty steps later the
estimate is 1.99 m from the truth, and the filter reports a standard deviation of 0.1463 —
the same 0.1463 it reported before the turn, and after it, and at every step of the run.
The error is thirteen sigma out and the number on the screen has not moved.

Treating $P$ as an error bar is tempting for good reasons. It has the units of one, the
filter computes and prints it, and on a target that obeys the model it is a correct one.
But the covariance recursion is a function of $A$, $C$, $W$, $V$ and the number of steps
taken, and of nothing else — the same fact noticed above when no measurement appeared in
the scalar loop, seen from the unpleasant side. $P$ is the variance the error *would*
have if the model were right and the covariances honest: a statement about your
assumptions, not about your data, and it cannot report that they were wrong.

The quantity that can is the innovation $y - C\hat{x}$, whose variance under those same
assumptions is $CPC^\top + R$. During the turn, innovations arrive many sigma out, over
and over, on the same side. Any filter that will be trusted needs that ratio watched, and
what it is watching for is not sensor failure but model failure.

## Where this stops holding

The gain derived above minimises the variance among *linear* corrections, for any
zero-mean noise with the stated covariances. It is the best estimator of any kind only
when the noise is Gaussian, which is what makes the Gaussian assumption load-bearing in
the theory and often unimportant in practice. The derivation used independence of $e$ and
$v$ at the line where the cross term was dropped, so correlated process and measurement
noise needs the cross-covariance carried through and changes the gain. The update
$(I - KC)P$ is the shortest of several equivalent forms and the least forgiving in finite
precision: it loses symmetry as entries cancel and can go indefinite, which is why the
Joseph form exists and why this module's lab checks $\lVert P - P^\top\rVert$ rather than
assuming it.

## What you are about to build

The lab *Run a Kalman filter and read its covariance* asks for the matrix form — for
`kalman_gain(P, C, R)` as $PC^\top(CPC^\top+R)^{-1}$, `predict` as
$(Ax,\ APA^\top + Q)$, `update` as the corrected pair, and `run_filter` looping them over
a seeded fixture of its own. Its checks are the claims made here rather than arithmetic:
that correcting lowers the trace and predicting raises it, that the scalar fixed point is
$\frac{q}{2} + \frac{1}{2}\sqrt{q^2+4qr} = 0.110499$ with posterior 0.090499, and that
after the transient the speed error is under 0.2 on a state no sensor supplied.
''',
                },
            ],
            "sandbox": {
                "title": "The gain the variances imply",
                "visualiser": "kalman",
                "minutes": 8,
                "initial": {"q": 0.02, "r": 0.5},
                "brief": r'''
A scalar filter watching a drifting quantity through a noisy sensor. Blue is the truth
it cannot see, grey is what arrives, green is what it believes.

This is the same random walk the derivation treats, so every number the readout shows
is one you are about to compute by hand.
''',
                "notice": [
                    "At $Q = 0.02$ and $R = 0.5$ the readout settles near $K = 0.181$. The derivation gives that exactly: the stationary prior variance is $\\frac{q}{2} + \\frac{1}{2}\\sqrt{q^2 + 4qr} = 0.110$, and $K = p/(p+r) = 0.110/0.610$.",
                    "Take $R$ to its minimum. The estimate lands on the dots and stays there: with a trustworthy sensor there is nothing the model can add.",
                    "Multiply $Q$ and $R$ by the same factor — $Q = 0.08$, $R = 2$. The picture does not change. The gain depends on the ratio alone, which is the same statement as the regulator depending only on $Q/R$.",
                ],
            },
            "derive": {
                "title": "The correction that minimises what is left over",
                "minutes": 16,
                "vars": ["p", "q", "r", "k", "y", "v", "e", "x", "P", "R", "K", "x_hat"],
                "brief": r'''
One state, measured directly. Before the measurement arrives the estimate is wrong by
$e$, with $\text{Var}(e) = p$; the measurement is $y = x + v$ with $\text{Var}(v) = r$,
independent of $e$. The correction is

$$\hat{x}_{new} = \hat{x} + k\,(y - \hat{x})$$

and the only question is what $k$ should be. Nothing here is assumed about $k$ in
advance — it falls out of minimising the variance that survives.
''',
                "steps": [
                    {
                        "prompt": "The new error is $(1-k)e - kv$. Write its variance in terms of $k$, $p$ and $r$.",
                        "given": "$e$ and $v$ are independent, so the variance of the sum is the sum of the variances.",
                        "answer": "(1 - k)^2 p + k^2 r",
                        "hint": "Scaling a random variable by $c$ multiplies its variance by $c^2$, and the cross term vanishes by independence.",
                        "deconstruct": [
                            "$\\text{Var}((1-k)e) = (1-k)^2 p$.",
                            "$\\text{Var}(-kv) = k^2 r$, and there is no cross term.",
                        ],
                    },
                    {
                        "prompt": "Differentiate that with respect to $k$, set it to zero, and write the minimising $k$.",
                        "answer": "\\frac{p}{p + r}",
                        "hint": "The derivative is $-2(1-k)p + 2kr$.",
                        "deconstruct": [
                            "Setting it to zero: $(1-k)p = kr$.",
                            "So $p = k(p + r)$.",
                        ],
                    },
                    {
                        "prompt": "Substitute that $k$ back and write the variance that survives the correction.",
                        "given": "It is worth checking the two limits afterwards: $r \\to 0$ and $r \\to \\infty$.",
                        "answer": "\\frac{p r}{p + r}",
                        "hint": "The shortest route is $(1-k)p$ with $k = p/(p+r)$, since $1 - k = r/(p+r)$.",
                        "deconstruct": [
                            "$1 - k = r/(p+r)$.",
                            "The posterior variance is $(1-k)p$, so multiply.",
                        ],
                    },
                    {
                        "prompt": "Now close the loop in time. The state is a random walk, so the next prior variance is the posterior plus $q$. Write the $p$ that is unchanged by one full predict-and-correct cycle.",
                        "given": "Write the fixed-point condition as $p = \\frac{pr}{p+r} + q$, clear the denominator, and solve the quadratic for the positive root. Enter the answer as a sum of two fractions, not one fraction with a root in its numerator.",
                        "answer": "\\frac{q}{2} + \\frac{1}{2}\\sqrt{q^2 + 4 q r}",
                        "hint": "Multiplying out gives $p^2 + pr = pr + qp + qr$, so $p^2 - qp - qr = 0$.",
                        "deconstruct": [
                            "Clearing the denominator: $p(p + r) = pr + q(p + r)$.",
                            "The $pr$ terms cancel, leaving $p^2 - qp - qr = 0$; take the positive root.",
                        ],
                    },
                ],
                "closing": r'''
Compare that with module 1. There, the closed-loop pole came from a quadratic whose
coefficients were the plant and the two weights; here, the steady covariance comes from
a quadratic whose coefficients are the plant and the two noise intensities. They are
the same equation with $B$ replaced by $C^\top$ and $A$ by $A^\top$.

That is not a coincidence or an analogy. The estimator Riccati equation

$$A Y + Y A^\top - Y C^\top V^{-1} C Y + W = 0$$

*is* the regulator equation for the transposed system, which is why the lab in the next
module gets its estimator gain by calling the solver from module 2 with the arguments
transposed, and nothing else.
''',
            },
            "quiz": {
                "title": "The filter, and the regulator it is a transpose of",
                "minutes": 7,
                "questions": [
                    {
                        "q": "The Kalman filter carries an estimate and a covariance. What does the covariance say?",
                        "opts": [
                            "How much to trust the estimate — and therefore how hard to correct it",
                            "How much noise the sensor has",
                            "How far the estimate is from the truth",
                            "How long the filter has been running",
                        ],
                        "a": 0,
                        "why": r"""
$P$ is the filter's own opinion of its uncertainty, and it is what turns a fixed
observer gain into a scheduled one: a large $P$ means "I am unsure, take the measurement
seriously", a small $P$ means "I know where I am, ignore the noise". It cannot be the
actual error — that would require knowing the truth, which is the thing being estimated.
The sensor noise is $R$, an input to the calculation rather than its state.
""",
                    },
                    {
                        "q": "What does the predict step do to the covariance?",
                        "opts": [
                            "Inflates it by the process noise",
                            "Deflates it by the measurement noise",
                            "Leaves it unchanged",
                            "Resets it",
                        ],
                        "a": 0,
                        "why": r"""
Time passing makes you less certain: $P \leftarrow APA^\top + W$, propagating the old
uncertainty through the dynamics and adding what the process noise contributed in the
interval. Correct is the opposite motion — it is the only step that ever reduces $P$.
The two alternating is the whole filter, and a filter that stops receiving measurements
has a covariance that grows without bound, which is exactly the right behaviour.
""",
                    },
                    {
                        "q": "The gain $K = PC^\\top(CPC^\\top + R)^{-1}$ is chosen to minimise what?",
                        "opts": [
                            "The trace of the covariance after the correction",
                            "The measurement residual",
                            "The control effort",
                            "The number of iterations to convergence",
                        ],
                        "a": 0,
                        "why": r"""
The trace is the total variance across all states, and the gain is the unique choice
that makes it smallest after the update — which is what "optimal" means here, and it is
optimal only under the assumptions of linearity and zero-mean noise. Minimising the
*residual* would be a different and worse objective: it would drive the estimate to
match a noisy measurement exactly, which is precisely what the filter exists to avoid.
""",
                    },
                    {
                        "q": "The measurement noise $R$ is very large. What does the filter do?",
                        "opts": [
                            "Uses a small gain and leans on the model",
                            "Uses a large gain to average the noise away",
                            "Stops updating entirely",
                            "Increases the process noise to compensate",
                        ],
                        "a": 0,
                        "why": r"""
$R$ sits in the denominator, so a noisy sensor produces a small gain and the estimate
coasts on the model between useful measurements. That is the filter's central bargain,
and reading $Q$ and $R$ as a *ratio* — which do you trust — is far more useful than
trying to identify their absolute values. It never stops updating: even a very noisy
measurement carries a little information, and the gain reflects exactly how much.
""",
                    },
                    {
                        "q": "In what sense is the filter the dual of LQR?",
                        "opts": [
                            "Its Riccati equation is the regulator's with $A \\to A^\\top$ and $B \\to C^\\top$",
                            "It minimises the same cost functional",
                            "It uses the same gain matrix",
                            "It is the inverse operation, so the two cancel",
                        ],
                        "a": 0,
                        "why": r"""
The same equation, transposed, with the noise covariances playing the roles of the
weights. That is why one solver does both jobs and why every result about one has a
mirror image in the other — controllability becomes observability, $A - BK$ becomes
$A - LC$. It is a structural correspondence, not a shared objective: the regulator
minimises a cost, the filter minimises a variance, and they happen to reduce to the
same algebra.
""",
                    },
                ],
            },
            "lab": {
                "title": "Run a Kalman filter and read its covariance",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
A target moving at roughly constant velocity, seen through a noisy position sensor.
`track_data()` is written for you and seeded, so every run gives the same numbers.

Implement the filter in matrix form, because the scalar case hides where the transposes
go:

- `kalman_gain(P, C, R)` → $PC^\top(CPC^\top + R)^{-1}$, shape `(n, m)`.
- `predict(x, P, A, Q)` → $(Ax,\ APA^\top + Q)$.
- `update(x, P, y, C, R)` → the corrected estimate $x + K(y - Cx)$ and covariance
  $(I - KC)P$.
- `run_filter(A, C, Q, R, ys, x0, P0)` → predict then update for every measurement,
  returning `(estimates, P)` where `estimates` is an array with one row per step.

The state is `[position, velocity]` and only position is measured, so the velocity
estimate is built entirely out of the model. The checks care about that.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

DT = 0.1


def track_data(steps=300, seed=5):
    """A constant-velocity target and its noisy position measurements. Seeded."""
    rng = np.random.default_rng(seed)
    x = np.array([0.0, 1.5])
    truth, meas = [], []
    for _ in range(steps):
        truth.append(x.copy())
        meas.append(x[0] + rng.normal(0.0, 0.5))
        x = np.array([x[0] + DT * x[1], x[1] + rng.normal(0.0, 0.02)])
    return np.array(truth), np.array(meas)


def kalman_gain(P, C, R):
    """P C^T (C P C^T + R)^-1."""
    P = np.asarray(P, dtype=float)
    C = np.asarray(C, dtype=float)
    R = np.asarray(R, dtype=float)
    # TODO: form the innovation covariance S = C P C.T + R, then P C.T inv(S).
    return np.zeros((P.shape[0], C.shape[0]))


def predict(x, P, A, Q):
    """Push the estimate and its covariance forward one step of the model."""
    x = np.asarray(x, dtype=float)
    P = np.asarray(P, dtype=float)
    A = np.asarray(A, dtype=float)
    Q = np.asarray(Q, dtype=float)
    # TODO: the estimate moves with A; the covariance is A P A.T + Q.
    return x, P


def update(x, P, y, C, R):
    """Correct the estimate with one measurement, and shrink the covariance."""
    x = np.asarray(x, dtype=float)
    P = np.asarray(P, dtype=float)
    C = np.asarray(C, dtype=float)
    # TODO: K = kalman_gain(...); innovation = y - C x; then x + K@innovation
    # and (I - K C) P.
    return x, P


def run_filter(A, C, Q, R, ys, x0, P0):
    """Predict then update for every measurement. Return (estimates, final P)."""
    x = np.asarray(x0, dtype=float).reshape(-1, 1)
    P = np.asarray(P0, dtype=float)
    out = []
    # TODO: for each y, predict, then update with [[float(y)]], then record x.ravel().
    return np.zeros((len(ys), x.shape[0])), P


if __name__ == "__main__":
    A = np.array([[1.0, DT], [0.0, 1.0]])
    C = np.array([[1.0, 0.0]])
    Q = np.diag([1e-6, 4e-4])
    R = np.array([[0.25]])
    truth, meas = track_data()
    est, P = run_filter(A, C, Q, R, meas, [[0.0], [0.0]], np.diag([1.0, 1.0]))
    raw = float(np.sqrt(np.mean((meas - truth[:, 0]) ** 2)))
    flt = float(np.sqrt(np.mean((est[:, 0] - truth[:, 0]) ** 2)))
    print("raw position rmse     :", round(raw, 6))
    print("filtered position rmse:", round(flt, 6))
    print("final covariance      :", np.round(P, 6).tolist())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

DT = 0.1


def track_data(steps=300, seed=5):
    """A constant-velocity target and its noisy position measurements. Seeded."""
    rng = np.random.default_rng(seed)
    x = np.array([0.0, 1.5])
    truth, meas = [], []
    for _ in range(steps):
        truth.append(x.copy())
        meas.append(x[0] + rng.normal(0.0, 0.5))
        x = np.array([x[0] + DT * x[1], x[1] + rng.normal(0.0, 0.02)])
    return np.array(truth), np.array(meas)


def kalman_gain(P, C, R):
    """P C^T (C P C^T + R)^-1."""
    P = np.asarray(P, dtype=float)
    C = np.asarray(C, dtype=float)
    R = np.asarray(R, dtype=float)
    S = C @ P @ C.T + R
    return P @ C.T @ np.linalg.inv(S)


def predict(x, P, A, Q):
    """Push the estimate and its covariance forward one step of the model."""
    x = np.asarray(x, dtype=float)
    P = np.asarray(P, dtype=float)
    A = np.asarray(A, dtype=float)
    Q = np.asarray(Q, dtype=float)
    return A @ x, A @ P @ A.T + Q


def update(x, P, y, C, R):
    """Correct the estimate with one measurement, and shrink the covariance."""
    x = np.asarray(x, dtype=float)
    P = np.asarray(P, dtype=float)
    C = np.asarray(C, dtype=float)
    K = kalman_gain(P, C, R)
    innovation = np.asarray(y, dtype=float).reshape(-1, 1) - C @ x
    x_new = x + K @ innovation
    P_new = (np.eye(P.shape[0]) - K @ C) @ P
    return x_new, P_new


def run_filter(A, C, Q, R, ys, x0, P0):
    """Predict then update for every measurement. Return (estimates, final P)."""
    x = np.asarray(x0, dtype=float).reshape(-1, 1)
    P = np.asarray(P0, dtype=float)
    out = []
    for y in ys:
        x, P = predict(x, P, A, Q)
        x, P = update(x, P, [[float(y)]], C, R)
        out.append(x.ravel().copy())
    return np.array(out), P


if __name__ == "__main__":
    A = np.array([[1.0, DT], [0.0, 1.0]])
    C = np.array([[1.0, 0.0]])
    Q = np.diag([1e-6, 4e-4])
    R = np.array([[0.25]])
    truth, meas = track_data()
    est, P = run_filter(A, C, Q, R, meas, [[0.0], [0.0]], np.diag([1.0, 1.0]))
    raw = float(np.sqrt(np.mean((meas - truth[:, 0]) ** 2)))
    flt = float(np.sqrt(np.mean((est[:, 0] - truth[:, 0]) ** 2)))
    print("raw position rmse     :", round(raw, 6))
    print("filtered position rmse:", round(flt, 6))
    print("final covariance      :", np.round(P, 6).tolist())
'''}],
                "hints": [
                    "`kalman_gain` is three matrix products and one inverse. Keep `C` as `(m, n)` and everything else follows.",
                    "In `predict`, the covariance grows: `A @ P @ A.T + Q`. Adding `Q` is what stops the filter becoming certain of a model that drifts.",
                    "In `update`, reshape the measurement to a column before subtracting, or numpy will broadcast it into a matrix and give you a silently wrong answer.",
                    "The order inside `run_filter` matters. Predict first, then correct with the measurement that belongs to the step you have just moved into.",
                ],
                "tests": [
                    {"name": "the gain weighs the prior against the sensor", "code": r'''
import numpy as np
_K = kalman_gain([[2.0]], [[1.0]], [[0.5]])
assert np.asarray(_K).shape == (1, 1), f"scalar case should give a (1,1) gain, got {np.asarray(_K).shape}"
assert abs(float(np.asarray(_K)[0, 0]) - 0.8) < 1e-12, \
    f"K = p/(p+r) = 2/2.5 = 0.8 when the prior is 2 and the sensor variance 0.5; got {float(np.asarray(_K)[0,0])}"
_K2 = kalman_gain([[2.0]], [[1.0]], [[1e6]])
assert abs(float(np.asarray(_K2)[0, 0])) < 1e-4, \
    "a sensor a million times noisier than the prior should be all but ignored"
'''},
                    {"name": "correcting shrinks the covariance", "code": r'''
import numpy as np
_P = np.array([[1.0, 0.2], [0.2, 0.5]])
_C = np.array([[1.0, 0.0]])
_R = np.array([[0.25]])
_x, _Pn = update(np.array([[0.0], [0.0]]), _P, [[1.0]], _C, _R)
_Pn = np.asarray(_Pn)
assert float(np.trace(_Pn)) < float(np.trace(_P)), \
    f"a measurement cannot make you less certain: trace went {np.trace(_P):.4f} -> {np.trace(_Pn):.4f}"
assert np.max(np.abs(_Pn - _Pn.T)) < 1e-9, \
    f"a covariance is symmetric; got {_Pn.tolist()}"
assert abs(float(np.asarray(_x)[0, 0]) - 0.8) < 1e-9, \
    f"the estimate should move 0.8 of the way to a measurement of 1.0; got {float(np.asarray(_x)[0,0]):.4f}"
'''},
                    {"name": "prediction inflates it again", "code": r'''
import numpy as np
_A = np.array([[1.0, 0.1], [0.0, 1.0]])
_Q = np.diag([1e-6, 4e-4])
_x, _P = predict(np.array([[1.0], [2.0]]), np.eye(2), _A, _Q)
_x = np.asarray(_x); _P = np.asarray(_P)
assert abs(float(_x[0, 0]) - 1.2) < 1e-12, \
    f"position 1 moving at 2 for 0.1 s reaches 1.2; got {float(_x[0,0])}"
assert float(np.trace(_P)) > 2.0, \
    "the prediction step must add Q, so the covariance grows rather than shrinking"
'''},
                    {"name": "the steady covariance matches the derivation", "code": r'''
import numpy as np
_q, _r = 0.02, 0.5
_A = np.array([[1.0]]); _C = np.array([[1.0]])
_x = np.array([[0.0]]); _P = np.array([[1.0]])
_prior = None
for _ in range(500):
    _x, _P = predict(_x, _P, _A, np.array([[_q]]))
    _prior = float(np.asarray(_P)[0, 0])
    _x, _P = update(_x, _P, [[0.0]], _C, np.array([[_r]]))
_want = _q / 2 + 0.5 * np.sqrt(_q * _q + 4 * _q * _r)
assert abs(_prior - _want) < 1e-9, \
    f"the fixed point of the covariance recursion is q/2 + sqrt(q^2+4qr)/2 = {_want:.9f}, got {_prior:.9f}"
assert abs(float(np.asarray(_P)[0, 0]) - 0.09049875621120892) < 1e-9, \
    f"the posterior at that fixed point is p*r/(p+r) = 0.090499, got {float(np.asarray(_P)[0,0]):.6f}"
'''},
                    {"name": "the filter beats the raw measurement", "code": r'''
import numpy as np
_A = np.array([[1.0, DT], [0.0, 1.0]])
_C = np.array([[1.0, 0.0]])
_truth, _meas = track_data()
_est, _P = run_filter(_A, _C, np.diag([1e-6, 4e-4]), np.array([[0.25]]),
                      _meas, [[0.0], [0.0]], np.diag([1.0, 1.0]))
_est = np.asarray(_est)
assert _est.shape == (300, 2), f"one row of estimate per measurement, so (300, 2); got {_est.shape}"
_raw = float(np.sqrt(np.mean((_meas - _truth[:, 0]) ** 2)))
_flt = float(np.sqrt(np.mean((_est[:, 0] - _truth[:, 0]) ** 2)))
assert abs(_raw - 0.48372437120120526) < 1e-9, "track_data must not be modified — the checks read its seeded output"
assert _flt < 0.5 * _raw, \
    f"filtering should more than halve the position error: raw {_raw:.4f}, filtered {_flt:.4f}"
'''},
                    {"name": "it estimates the velocity it never measures", "code": r'''
import numpy as np
_A = np.array([[1.0, DT], [0.0, 1.0]])
_C = np.array([[1.0, 0.0]])
_truth, _meas = track_data()
_est, _P = run_filter(_A, _C, np.diag([1e-6, 4e-4]), np.array([[0.25]]),
                      _meas, [[0.0], [0.0]], np.diag([1.0, 1.0]))
_est = np.asarray(_est)
_verr = float(np.sqrt(np.mean((_est[100:, 1] - _truth[100:, 1]) ** 2)))
assert _verr < 0.2, \
    f"after settling the velocity error should be well under 0.2; got {_verr:.4f} — the model, not the sensor, supplies this state"
assert float(np.asarray(_P)[1, 1]) < 0.05, \
    f"the filter should end confident about velocity; P[1,1] came out {float(np.asarray(_P)[1,1]):.5f}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "LQG, and why separation survives the noise",
            "summary": "Solve the two Riccati equations, bolt the pieces together, and find that neither design has disturbed the other.",
            "concepts": [
                "LQG is exactly two designs: $K$ from $(A, B, Q, R)$ and $L$ from $(A, C, W, V)$, connected by $u = -K\\hat{x}$.",
                "In the coordinates $(x, e)$ with $e = x - \\hat{x}$, the closed loop is block upper triangular.",
                "So the $2n$ closed-loop poles are the union of $\\text{eig}(A - BK)$ and $\\text{eig}(A - LC)$ — exactly, not approximately.",
                "The noise sets the size of the residual motion, not the location of any pole.",
                "What separation does *not* give you: LQG has no guaranteed gain margin, unlike full-state LQR.",
            ],
            "read": [
                {
                    "title": "Four poles, and both designers got what they asked for",
                    "minutes": 16,
                    "body": r'''
The rig is a rod balanced upright on a driven pivot, linearised about vertical:
$\ddot{\theta} = 4\theta - 0.2\dot{\theta} + u$, with $u$ the motor torque. Its open-loop
eigenvalues are $+1.9025$ and $-2.1025$, so left alone it falls with a time constant of
0.53 s. An encoder reads the angle; nothing measures the rate.

Two designs are made independently, neither designer speaking to the other. One solves
the regulator problem with $Q = \text{diag}(2, 0)$ and $R = 0.05$, assuming the whole
state is available. The other solves the estimator problem with
$W = \text{diag}(10^{-3}, 2\times10^{-2})$ and $V = 10^{-3}$, assuming there is no
controller at all. The pieces are then bolted together, with the regulator fed
$\hat{x}$:

```python
import math

A = [[0.0, 1.0], [4.0, -0.2]]         # falls over: an eigenvalue at +1.9025
B = [[0.0], [1.0]]
C = [[1.0, 0.0]]
Q = [[2.0, 0.0], [0.0, 0.0]]
R = 0.05
W = [[0.001, 0.0], [0.0, 0.02]]
V = 0.001


def mul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))]
            for i in range(len(X))]


def tr(X):
    return [list(row) for row in zip(*X)]


def care(A, B, Q, r, dt=0.0005, steps=60000):
    """Integrate dP/dtau = A^T P + P A - P B r^-1 B^T P + Q from P = 0."""
    n = len(A)
    P = [[0.0] * n for _ in range(n)]
    At, Bt = tr(A), tr(B)
    for _ in range(steps):
        quad = mul(mul(mul(P, B), [[1.0 / r]]), mul(Bt, P))
        left, right = mul(At, P), mul(P, A)
        P = [[P[i][j] + dt * (left[i][j] + right[i][j] - quad[i][j] + Q[i][j])
              for j in range(n)] for i in range(n)]
    return P


def eig2(M):
    t = M[0][0] + M[1][1]
    d = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    disc = t * t - 4.0 * d
    if disc >= 0.0:
        return [complex((t + math.sqrt(disc)) / 2.0), complex((t - math.sqrt(disc)) / 2.0)]
    return [complex(t / 2.0, math.sqrt(-disc) / 2.0),
            complex(t / 2.0, -math.sqrt(-disc) / 2.0)]


P = care(A, B, Q, R)
K = [[P[1][0] / R, P[1][1] / R]]                      # R^-1 B^T P
Y = care(tr(A), tr(C), W, V)                          # the dual problem
L = mul(mul(Y, tr(C)), [[1.0 / V]])                   # Y C^T V^-1

print("K =", [round(v, 6) for v in K[0]])
print("L =", [round(row[0], 6) for row in L])

ABK = [[A[i][j] - B[i][0] * K[0][j] for j in range(2)] for i in range(2)]
ALC = [[A[i][j] - L[i][0] * C[0][j] for j in range(2)] for i in range(2)]
print("regulator poles       :", [complex(round(z.real, 4), round(z.imag, 4)) for z in eig2(ABK)])
print("estimator poles       :", [complex(round(z.real, 4), round(z.imag, 4)) for z in eig2(ALC)])
```

```text
K = [11.483315, 4.596523]
L = [4.387664, 9.1258]
regulator poles       : [(-2.3983+1.3159j), (-2.3983-1.3159j)]
estimator poles       : [(-2.2938+0.8612j), (-2.2938-0.8612j)]
```

Four poles between the two designs, and no reason yet to think the assembled loop has any
of them. The regulator was designed for a state it will not receive; the estimator was
designed for a plant now driven by a controller reacting to the estimator's own mistakes.
Anyone who has connected two subsystems tuned apart expects an interaction term. Measure
the assembled loop.

```python
K = [[11.483315, 4.596523]]           # the regulator of the previous block
L = [[4.387664], [9.125800]]          # and its estimator
A = [[0.0, 1.0], [4.0, -0.2]]
B = [[0.0], [1.0]]
C = [[1.0, 0.0]]


def mul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))]
            for i in range(len(X))]


def charpoly(M):
    """Faddeev-LeVerrier: coefficients of det(lambda I - M), leading 1 first."""
    n = len(M)
    coef, N = [1.0], [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for k in range(1, n + 1):
        AN = mul(M, N)
        c = -sum(AN[i][i] for i in range(n)) / k
        coef.append(c)
        N = [[AN[i][j] + (c if i == j else 0.0) for j in range(n)] for i in range(n)]
    return coef


BK = mul(B, K)
LC = mul(L, C)
ABK = [[A[i][j] - BK[i][j] for j in range(2)] for i in range(2)]
ALC = [[A[i][j] - LC[i][j] for j in range(2)] for i in range(2)]

big = [ABK[0] + BK[0], ABK[1] + BK[1],
       [0.0, 0.0] + ALC[0], [0.0, 0.0] + ALC[1]]

p = charpoly(big)
a = charpoly(ABK)
b = charpoly(ALC)
prod = [0.0] * 5
for i, ai in enumerate(a):
    for j, bj in enumerate(b):
        prod[i + j] += ai * bj

print("closed loop char poly :", [round(v, 8) for v in p])
print("product of the blocks :", [round(v, 8) for v in prod])
print("largest disagreement  :", max(abs(x - y) for x, y in zip(p, prod)))


def quartic_stable(c):
    """Routh-Hurwitz for lambda^4 + a1 l^3 + a2 l^2 + a3 l + a4."""
    _, a1, a2, a3, a4 = c
    return a1 > 0 and a3 > 0 and a4 > 0 and a1 * a2 * a3 > a3 * a3 + a1 * a1 * a4


def lqg_stable(beta):
    """Plant input scaled by beta; the estimator still believes B."""
    top = [[A[i][j] for j in range(2)] + [-beta * BK[i][j] for j in range(2)]
           for i in range(2)]
    bot = [[LC[i][j] for j in range(2)] + [A[i][j] - BK[i][j] - LC[i][j] for j in range(2)]
           for i in range(2)]
    return quartic_stable(charpoly(top + bot))


def edge(fn, lo, hi):
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if fn(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


print()
print("LQG loop stable for beta in ( %.4f , %.4f )"
      % (edge(lqg_stable, 0.0, 1.0), edge(lambda z: not lqg_stable(z), 1.0, 40.0)))
```

```text
closed loop char poly : [1.0, 9.384187, 35.49148369, 63.12605868, 44.92483039]
product of the blocks : [1.0, 9.384187, 35.49148369, 63.12605868, 44.92483039]
largest disagreement  : 7.105427357601002e-15

LQG loop stable for beta in ( 0.7703 , 2.3537 )
```

The first three lines are the result: the quartic of the assembled four-state loop is the
product of the two quadratics, coefficient by coefficient, to seven parts in $10^{15}$.
Not close — equal. Both designers got the poles they asked for, and neither disturbed the
other.

## Why the interaction term is missing

Write the loop in the coordinates $(x, e)$ with $e = x - \hat{x}$, the change of variable
the derivation *The closed loop in error coordinates* walks through. Since
$\hat{x} = x - e$, the control is

$$u = -K\hat{x} = -K(x - e) = -Kx + Ke$$

so the plant becomes $\dot{x} = (A - BK)x + BKe$. Now subtract the estimator,
$\dot{\hat{x}} = A\hat{x} + Bu + L(Cx - C\hat{x})$, from the plant,
$\dot{x} = Ax + Bu$:

$$\dot{e} = A(x - \hat{x}) - LC(x - \hat{x}) = (A - LC)\,e$$

The $Bu$ terms are identical in the two equations and cancel, whatever $u$ happens to be.
That single cancellation is the entire theorem, and it depends on one thing worth naming:
both equations carry the same $B$ and the same $u$. Stacked,

$$\begin{bmatrix} \dot{x} \\ \dot{e} \end{bmatrix} =
\begin{bmatrix} A - BK & BK \\ 0 & A - LC \end{bmatrix}
\begin{bmatrix} x \\ e \end{bmatrix}$$

Expand $\det(\lambda I - M)$ for a block upper-triangular $M$ and it factors into
$\det(\lambda I - (A-BK))\,\det(\lambda I - (A-LC))$, because the zero block leaves no
term in the expansion that mixes the two. Multiplying the quadratics in the code above is
that identity being evaluated, and the agreement to $10^{-15}$ is arithmetic confirming
algebra.

Note which zero matters. The $BK$ block in the top right is not zero and does not need to
be: a block upper-triangular matrix has the union of its diagonal blocks' spectra whatever
sits above the diagonal. The load-bearing zero is the bottom-left one, and in words it
says that the plant state does not appear in the error dynamics — the estimator's mistakes
are its own business, uninfluenced by where the rod is or what the controller does about
it.

## What separation does not buy

The $BK$ block being non-zero has a consequence the poles do not show: it is the route by
which estimation error becomes a disturbance on the plant. Hold $K$ fixed, vary the sensor
variance the estimator assumed, and compute the stationary covariance from
$M\Sigma + \Sigma M^\top + S = 0$ — the matrix version of the derivation's last step,
where a scalar mode driven by intensity $s$ settles at $\sigma^2 = -s/2\mu$:

```python
import math

A = [[0.0, 1.0], [4.0, -0.2]]
B = [[0.0], [1.0]]
C = [[1.0, 0.0]]
K = [[11.483315, 4.596523]]           # the regulator, unchanged throughout
W = [[0.001, 0.0], [0.0, 0.02]]       # what the disturbance really is
V_TRUE = 0.001                        # what the sensor really is

DESIGNS = (("V assumed 1e-5", [[13.868718], [46.170667]]),
           ("V assumed 1e-3", [[4.387664], [9.125800]]),
           ("V assumed 0.5 ", [[3.806496], [7.243708]]))


def mul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))]
            for i in range(len(X))]


def tr(X):
    return [list(row) for row in zip(*X)]


def lyapunov(M, S, dt=0.0005, steps=40000):
    """Integrate dSigma/dt = M Sigma + Sigma M^T + S from zero to its steady state."""
    n = len(M)
    Sig = [[0.0] * n for _ in range(n)]
    Mt = tr(M)
    for _ in range(steps):
        a, b = mul(M, Sig), mul(Sig, Mt)
        Sig = [[Sig[i][j] + dt * (a[i][j] + b[i][j] + S[i][j]) for j in range(n)]
               for i in range(n)]
    return Sig


BK = mul(B, K)
for name, L in DESIGNS:
    LC = mul(L, C)
    ABK = [[A[i][j] - BK[i][j] for j in range(2)] for i in range(2)]
    ALC = [[A[i][j] - LC[i][j] for j in range(2)] for i in range(2)]
    M = [ABK[0] + BK[0], ABK[1] + BK[1], [0.0, 0.0] + ALC[0], [0.0, 0.0] + ALC[1]]
    LVL = mul(mul(L, [[V_TRUE]]), tr(L))
    S = [[W[0][0], W[0][1], W[0][0], W[0][1]],
         [W[1][0], W[1][1], W[1][0], W[1][1]],
         [W[0][0], W[0][1], W[0][0] + LVL[0][0], W[0][1] + LVL[0][1]],
         [W[1][0], W[1][1], W[1][0] + LVL[1][0], W[1][1] + LVL[1][1]]]
    Sig = lyapunov(M, S)
    cov_u = [[Sig[i][j] - Sig[i][j + 2] - Sig[j][i + 2] + Sig[i + 2][j + 2]
              for j in range(2)] for i in range(2)]      # u = -K(x - e)
    var_u = mul(mul(K, cov_u), tr(K))[0][0]
    print(f"{name}   rms angle {math.sqrt(Sig[0][0]):.5f}   rms torque {math.sqrt(var_u):.4f}"
          f"   mean cost {2.0 * Sig[0][0] + 0.05 * var_u:.5f}")
```

```text
V assumed 1e-5   rms angle 0.09198   rms torque 2.3153   mean cost 0.28496
V assumed 1e-3   rms angle 0.13811   rms torque 1.1922   mean cost 0.10922
V assumed 0.5    rms angle 0.15670   rms torque 1.1406   mean cost 0.11415
```

All three loops have the regulator poles at $-2.3983 \pm 1.3159j$, because $K$ never
changed. The rod is held twice as tightly by one of them as by another, and the torque
varies by a factor of two. Separation is a statement about pole locations and not about
achieved performance: the poles say where the modes are, the noise intensities say how
hard those modes are shaken, and the second question is not answered by the first. The
design whose assumed $V$ matches the sensor wins on the quantity LQG actually minimises,
$E[x^\top Qx + u^\top Ru]$, at 0.109 — but it does not win on angle. The estimator that
believes the sensor a hundred times better than it is holds the rod tightest, at twice
the torque, and pays for that in the currency module 1 set up.

## The mistake, and why it is tempting

The bottom of the second block is the mistake. Multiply the torque actually delivered by a
factor $\beta$ — a re-scaled amplifier, a heavier rod, a linearisation error — while the
estimator continues to believe the $B$ it was given. Under full-state feedback the answer
is available in closed form:
$A - \beta BK = \begin{bmatrix} 0 & 1 \\ 4 - \beta k_1 & -0.2 - \beta k_2\end{bmatrix}$
has trace $-0.2 - \beta k_2$, negative for every $\beta > 0$, and determinant
$\beta k_1 - 4$, positive once $\beta > 4/11.4833 = 0.3483$. Stable from there upwards
with no upper limit at all — the module 1 margin guarantee, proved on this plant in two
lines. With the same $K$, the same $L$, and the four poles that separation placed exactly
where both designers asked, the LQG loop is stable only for $\beta$ between 0.770 and
2.354. A gain 2.4 times too large tips it over.

The mistake is expecting the guarantee to travel, and it is tempting for a structural
reason: separation is *exact* for the poles, so it feels as though it ought to be exact
for everything the poles imply. It is tempting also because the infinite gain margin gets
quoted as a property of LQ design rather than of full-state feedback, which is what it
is. Doyle settled the question in 1978: there are no guaranteed margins for LQG, and no
bound can be stated in terms of $Q$, $R$, $W$ and $V$. The response is not to abandon the
method but to check — recover the loop transfer with LQG/LTR, or measure the margins of
the design you have, as the sweep above does.

## Where this stops holding

Every line of the derivation used the same $A$, $B$ and $u$ in both equations, so it
fails wherever that is not true.

Actuator saturation is the sharpest. The estimator is driven by the $u$ the controller
*commanded*, the plant by the torque the motor *delivered*; once they differ the $Bu$
terms no longer cancel, $\dot{e}$ picks up a term in the difference, and the error
dynamics stop being autonomous. The estimate drifts while the actuator is pinned, which is
the observer form of integrator windup — and the standard repair, feeding the estimator
the clipped output rather than the demand, is that cancellation restored rather than a
heuristic.

Model mismatch does the same more quietly. If the estimator carries an $\hat{A}$ and
$\hat{B}$ differing from the plant, the bottom-left block stops being zero, the matrix
stops being triangular, and the two pole sets genuinely mix; the $\beta$ sweep above is
the smallest instance of that. The rod is also a linearisation, and at 30° from upright
the $\sin\theta$ replaced by $\theta$ is 13% smaller — a $\beta$ of 0.87 by another name.

## What you are about to build

The lab *Close the LQG loop on an unstable plant* assembles what this reading measured.
`estimator_gain(A, C, W, V)` is one call to the module 2 solver with the arguments
transposed, then $L = YC^\top V^{-1}$; its check is $L_1 = 4.387664$, the number in the
first block above. `combined_poles(A, B, C, K, L)` builds the $2n \times 2n$ matrix and
compares its four eigenvalues against the union of the two designs to $10^{-8}$.
`simulate` runs plant and estimator together with seeded noise, and the last check changes
$R$ and confirms that no estimator pole moved. The fill-in unit *Why separation survives*
is the block matrix with its zero left out, and the sandbox *The estimator half of the
loop* is the second half of this reading with the sliders exposed: nothing there moves a
regulator pole, and everything there changes the error the regulator is left holding.
''',
                },
            ],
            "quiz": {
                "title": "What separation gives, and what it withholds",
                "minutes": 8,
                "questions": [
                    {
                        "q": "In the closed loop written as $\\begin{bmatrix} A - BK & BK \\\\ 0 & A - LC \\end{bmatrix}$, which entry carries the separation result, and what does it assert?",
                        "opts": [
                            "The top-right $BK$: the controller reacts to the estimate, so the two designs share a term",
                            "The bottom-left zero: the plant state does not appear in the error dynamics at all",
                            "The top-left $A - BK$: the regulator was designed as if the state were measured",
                            "The bottom-right $A - LC$: the estimator was designed as though there were no controller",
                        ],
                        "a": 1,
                        "whys": [
                            r"That block is real and non-zero, and it is how estimation error disturbs the plant. But a block upper-triangular matrix has the union of its diagonal blocks' eigenvalues whatever sits above the diagonal, so this entry cannot be what makes the spectra separate.",
                            r"A block triangular matrix has the union of its diagonal blocks' spectra, and the zero is what makes it triangular.",
                            r"That block is where the regulator design ends up, and the fact that its eigenvalues survive is the conclusion rather than the reason. Put anything non-zero underneath it and those eigenvalues stop surviving.",
                            r"Likewise the destination rather than the mechanism: the estimator poles appear here, and they appear in the closed loop only because the block beneath the other diagonal entry vanishes.",
                        ],
                        "why": r"""
The determinant of a block upper-triangular matrix factors into the determinants of its
diagonal blocks, so the four eigenvalues are exactly the union of $\text{eig}(A-BK)$ and
$\text{eig}(A-LC)$. The zero is what makes it triangular, and the reason the zero is there
is that the $Bu$ terms in the plant and the estimator are identical and cancel when one is
subtracted from the other — whatever $u$ happens to be. Anything that breaks that
cancellation, saturation or a mismatched model, fills the block in and mixes the two pole
sets.
""",
                    },
                    {
                        "q": "You drop $R$ from 1.0 to 0.005 in an LQG design, leaving $W$ and $V$ alone. What moves?",
                        "opts": [
                            "Both pole sets, since a faster regulator drives the estimator harder and so shifts its poles too",
                            "Only the estimator poles, because a larger $K$ feeds more signal into the error dynamics",
                            "Only the regulator poles; the estimator poles are a function of $A$, $C$, $W$ and $V$ alone",
                            "Neither pole set, since scaling the cost weights leaves the optimal design unchanged",
                        ],
                        "a": 2,
                        "whys": [
                            r"This is the intuition separation exists to overturn. A faster regulator does move the plant about more energetically, and the error dynamics are still governed by $A - LC$ and know nothing about it.",
                            r"$K$ appears nowhere in $\dot{e} = (A - LC)e$.",
                            r"The estimator Riccati equation contains no $B$, no $Q$ and no $R$, so nothing about the regulator can reach it.",
                            r"Scaling $Q$ and $R$ *together* leaves the design alone, which is module 1's ratio invariance. Changing $R$ on its own changes the ratio, and the regulator poles move a long way.",
                        ],
                        "why": r"""
$L$ comes from $AY + YA^\top - YC^\top V^{-1}CY + W = 0$, an equation in which neither $B$
nor $Q$ nor $R$ appears, so no choice of cost weights can move an estimator pole. The
regulator poles move a great deal: dropping $R$ by a factor of 200 pushes them
substantially further left. This is the check the module lab ends on, and it is worth
running in a design review, because a wired-up implementation in which changing $R$ does
shift the estimator poles has a genuine defect in it.
""",
                    },
                    {
                        "q": "Three LQG designs share one $K$ and differ only in the $V$ their estimators assumed. Their closed loops give rms angles of 0.092, 0.138 and 0.157. Does that contradict separation?",
                        "opts": [
                            "Yes — identical regulator poles must give identical closed-loop behaviour under the same noise",
                            "No — separation fixes where the poles are, and the noise fixes how hard those modes are driven",
                            "No — the regulator poles are only approximately equal, and the differences accumulate over a long run",
                            "Yes — a correct implementation would give the same variance whenever $Q$ and $R$ are unchanged",
                        ],
                        "a": 1,
                        "whys": [
                            r"Poles govern the free response and say nothing about the size of a forced one. Two loops with identical poles driven by different disturbance intensities settle at different variances, and nothing about that is inconsistent.",
                            r"A mode at $\mu$ driven by intensity $s$ settles at $\sigma^2 = -s/2\mu$; separation fixes $\mu$ and leaves $s$ open.",
                            r"The regulator poles are equal to machine precision, since $K$ is the same matrix in all three loops. The difference in variance is a real effect and not an accumulation of round-off.",
                            r"$Q$ and $R$ fix $K$ and therefore the regulator poles. The variance the loop settles at also depends on $L$, on the true noise, and on the estimation error the $BK$ block delivers to the plant.",
                        ],
                        "why": r"""
Separation is a statement about eigenvalues. The stationary covariance solves
$M\Sigma + \Sigma M^\top + S = 0$, and $S$ carries $W$ and $LVL^\top$ — so changing $L$
changes the driving intensity even with $M$'s spectrum pinned. In the scalar case the
whole story is $\sigma^2 = -s/2\mu$: separation settles $\mu$ and leaves $s$ entirely
open. A slower estimator hands the regulator a larger error through the top-right $BK$
block, and the regulator pays for it in torque.
""",
                    },
                    {
                        "q": "Under full-state LQR the loop tolerates any input-gain factor above 0.348. With the same $K$ driven by an estimator, it goes unstable at 2.354. What accounts for that?",
                        "opts": [
                            "The estimator has added lag, which always costs phase margin in proportion to $L$",
                            "The LQR margin guarantee is a property of feeding back the state, and estimating it forfeits it",
                            "The estimator poles were placed too slowly, and a faster $L$ would restore the infinite margin",
                            "The gain perturbation violates an assumption of the Riccati equation, whose solution is no longer valid",
                        ],
                        "a": 1,
                        "whys": [
                            r"Lag is a fair description of the mechanism and the wrong claim about the result. The loss is not proportional to anything in general: Doyle constructed LQG designs whose margin can be made arbitrarily small with the weights held fixed.",
                            r"The guarantee is proved for $u = -Kx$; replace $x$ with $\hat{x}$ and the proof no longer applies.",
                            r"A faster estimator usually helps, and it recovers nothing that can be guaranteed in advance. LQG/LTR pushes the loop transfer towards the full-state one in the limit, and that limit is a design technique rather than a theorem about margins.",
                            r"The Riccati solution is unaffected — it was computed from the nominal $A$, $B$, $Q$ and $R$, and remains the exact solution of that problem. What the perturbation changes is the plant the design meets, not the design.",
                        ],
                        "why": r"""
The infinite gain margin and 60° of phase margin are theorems about the return difference
of $u = -Kx$, and the state is the thing being fed back. Once $u = -K\hat{x}$ the loop
transfer is a different function and the proof no longer applies. Doyle showed in 1978
that no margin at all can be guaranteed from $Q$, $R$, $W$ and $V$ — the guarantee is not
merely weakened, it is gone. Separation continues to hold exactly, and its holding is
precisely what makes the loss surprising: the poles are where both designers asked for
them and the design is fragile anyway.
""",
                    },
                    {
                        "q": "The motor saturates and delivers less torque than the controller commanded. What does that do to the separation argument?",
                        "opts": [
                            "Nothing, since the estimator is a linear filter and saturation acts only on the plant input",
                            "It moves the estimator poles, because the effective $B$ that the plant experiences has shrunk",
                            "It makes $A - BK$ unstable, since the regulator can no longer deliver the effort its gain assumes",
                            "The plant and the estimator now see different inputs, so the terms that cancelled no longer do",
                        ],
                        "a": 3,
                        "whys": [
                            r"Saturation acts on the plant input and the estimator is driven by the *commanded* input, which is exactly the problem: the two equations stop sharing a term, and the subtraction that produced $\dot{e} = (A-LC)e$ is no longer available.",
                            r"$A - LC$ contains no $B$, so no change in the actuator can move an estimator pole.",
                            r"$A - BK$ is a matrix built from the design and does not change when the hardware clips. What changes is that the loop being run is no longer the linear loop that matrix describes.",
                            r"$\dot{e}$ picks up $B(u_\text{cmd} - u_\text{del})$, so the error dynamics are no longer autonomous.",
                        ],
                        "why": r"""
The cancellation needs the plant and the estimator to carry the same $Bu$. Under
saturation the plant gets $B\,\text{sat}(u)$ while the estimator gets $Bu$, so
$\dot{e} = (A - LC)e + B\,(u - \text{sat}(u))$ — driven, not autonomous, and driven hardest
exactly when the actuator is pinned and the estimate matters most. The estimate then
drifts, which is the observer form of integrator windup. The standard repair is to feed
the estimator the delivered torque rather than the demand, and that is not a heuristic: it
restores the cancellation the theorem rests on.
""",
                    },
                    {
                        "q": "A rule of thumb says to place the estimator poles several times faster than the regulator poles. Given that the two designs do not interact, where does that rule come from?",
                        "opts": [
                            "A slow estimate reaches the regulator as a disturbance through the $BK$ block",
                            "A slow estimator would otherwise drag the regulator poles towards it",
                            "The union of the two pole sets is dominated by whichever set is slower overall",
                            "A fast estimator is less sensitive to the process noise the plant is subjected to",
                        ],
                        "a": 0,
                        "whys": [
                            r"The transient the regulator is fighting is $BKe(t)$, and $e$ decays at the estimator poles, so a slow estimator keeps feeding it for longer.",
                            r"This is the thing separation rules out. No choice of $L$ moves a regulator pole, and the rule of thumb is about the size of a transient rather than the position of any root.",
                            r"True of the closed-loop response, and it does not on its own recommend a *ratio*: it would recommend making the estimator merely a little faster. The reason for a factor of several is that the error is a disturbance the regulator must reject while it lasts.",
                            r"A fast estimator is in fact *more* sensitive to noise, since a large $L$ multiplies the measurement noise on its way into the estimate. The rule trades that noise against transient error, which is why it names a factor rather than saying to go as fast as possible.",
                        ],
                        "why": r"""
The top-right block is $BK$, so the plant equation is $\dot{x} = (A-BK)x + BKe$ and the
estimation error is a disturbance entering the regulator loop. It decays at the estimator
poles, so an estimator only as fast as the regulator leaves that disturbance present
throughout the interval in which the regulator is doing its work. Make the error decay
several times faster and the regulator spends most of its transient acting on a state it
essentially knows. The rule is about the size and duration of a forced response and not
about the location of any pole, which is why it can coexist with the separation theorem
rather than contradicting it — and the factor is finite because a faster $L$ admits more
sensor noise.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "The estimator half of the loop",
                "visualiser": "kalman",
                "minutes": 7,
                "initial": {"q": 0.005, "r": 0.05},
                "brief": r'''
The estimator from an LQG loop, on its own. The regulator is not shown here, and that
is the point: nothing you do to these two sliders can move a regulator pole.

What the sliders do move is the error the regulator is left holding.
''',
                "notice": [
                    "The opening pair gives a steady gain near $0.270$. Push $R$ up to $2$ and it falls to about $0.049$, and the estimate visibly lags. The regulator poles are unchanged by this; the residual error it has to work against is not.",
                    "Set $Q$ to its maximum and $R$ to its minimum. The gain goes to almost $1$, the estimate becomes the measurement, and the loop degenerates into raw output feedback with no filtering left in it.",
                    "Go the other way — $Q$ at its minimum, $R$ at its maximum. The estimate becomes a pure model prediction that ignores the sensor. Both extremes are stable and both are bad, which is the argument for choosing $W$ and $V$ from measured noise rather than by taste.",
                ],
            },
            "derive": {
                "title": "The closed loop in error coordinates",
                "minutes": 14,
                "vars": ["A", "B", "C", "K", "L", "P", "Q", "R", "x", "e", "u", "w", "v", "s", "mu"],
                "brief": r'''
The plant is $\dot{x} = Ax + Bu + w$ with $y = Cx + v$; the estimator is
$\dot{\hat{x}} = A\hat{x} + Bu + L(y - C\hat{x})$; the control is $u = -K\hat{x}$.

Change coordinates from $(x, \hat{x})$ to $(x, e)$ with $e = x - \hat{x}$, and the whole
argument becomes visible in three lines.
''',
                "steps": [
                    {
                        "prompt": "Since $\\hat{x} = x - e$, rewrite the control $u = -K\\hat{x}$ in terms of $K$, $x$ and $e$.",
                        "answer": "K e - K x",
                        "hint": "Substitute and distribute the minus sign across both terms.",
                        "deconstruct": [
                            "$u = -K(x - e)$.",
                            "Distribute: one term in $x$, one in $e$.",
                        ],
                    },
                    {
                        "prompt": "Put that into $\\dot{x} = Ax + Bu$ (leave the noise out for now) and write $\\dot{x}$ in terms of $A$, $B$, $K$, $x$ and $e$.",
                        "answer": "A x - B K x + B K e",
                        "hint": "$B$ multiplies both terms of $u$.",
                        "deconstruct": [
                            "$Bu = -BKx + BKe$.",
                            "Add $Ax$.",
                        ],
                    },
                    {
                        "prompt": "Subtracting the estimator from the plant gives $\\dot{e} = M e + w - Lv$ for some matrix $M$. Write $M$.",
                        "given": "This is the CTRL510 result, and it is worth noticing what changed: the noise terms are new, the matrix is not.",
                        "answer": "A - L C",
                        "hint": "The $Bu$ terms are identical in the two equations and cancel, whatever $u$ happens to be.",
                        "deconstruct": [
                            "Plant minus estimator: $\\dot{e} = Ax - A\\hat{x} - LCx + LC\\hat{x} + w - Lv$.",
                            "Group the $x$ and $\\hat{x}$ terms; both give the same matrix acting on $e$.",
                        ],
                    },
                    {
                        "prompt": "The two blocks are decoupled one way, so the poles are the union and the noise cannot move them — it only sets the size of the residual motion. For a scalar mode $\\dot{z} = \\mu z + n$ driven by white noise of intensity $s$, the stationary variance satisfies $2\\mu\\sigma^2 + s = 0$. Write $\\sigma^2$.",
                        "answer": "-\\frac{s}{2 \\mu}",
                        "hint": "Solve the one-line algebraic Lyapunov equation. The minus sign is what makes the answer positive, because $\\mu$ is negative for a stable mode.",
                        "deconstruct": [
                            "$2\\mu\\sigma^2 = -s$.",
                            "Divide by $2\\mu$.",
                        ],
                    },
                ],
                "closing": r'''
Stack the two equations:

$$\begin{bmatrix} \dot{x} \\ \dot{e} \end{bmatrix} =
\begin{bmatrix} A - BK & BK \\ 0 & A - LC \end{bmatrix}
\begin{bmatrix} x \\ e \end{bmatrix} + \text{noise}$$

The zero block is the whole theorem. A block upper-triangular matrix has the union of
its diagonal blocks' eigenvalues, so the $2n$ poles are those of $A - BK$ together with
those of $A - LC$, and the noise appears only as an additive term. Choosing $K$ cannot
move an estimator pole and choosing $L$ cannot move a regulator pole.

The last step is the part people forget. Separation says the *poles* are unaffected. It
does not say the performance is: the residual variance goes as $s/2|\mu|$, so a slow
estimator leaves a large error for a fast regulator to keep reacting to, and the control
effort pays for it.
''',
            },
            "blanks": {
                "title": "Why separation survives",
                "minutes": 8,
                "caption": "lqg.py — two designs that turn out not to interfere",
                "lang": "python",
                "brief": r"""
LQG is not a third design. It is the regulator and the estimator, bolted together — and
the reason that is allowed is one structural fact about a matrix. Fill it in.
""",
                "listing": """K = lqr(A, B, Q, R)          # regulator, from the cost weights
L = lqe(A, C, W, V)          # estimator, from the noise covariances

# Write the closed loop in the coordinates (x, e) with e = x - xhat:
#
#     [[ A - B @ K ,   ___      ],
#      [     0     ,  A - L @ C ]]
#
# The zero block makes this ___ ,
# so its 2n eigenvalues are exactly the union of
#
#     eig(A - B @ K)   and   eig( ___ )
#
# which is why the two designs ___ .
""",
                "blanks": [
                    {
                        "prompt": "The estimation error feeds the plant through the controller.",
                        "hole": "?",
                        "opts": ["B @ K", "0", "-L @ C", "A"],
                        "a": 0,
                        "why": "The controller acts on $\\hat{x} = x - e$, so $u = -K(x - e)$ and the $+BKe$ term lands in the top-right block. It is non-zero and it matters — a bad estimate really does disturb the plant. What saves the design is only that the coupling is one-way.",
                        "whys": [
                            "The controller acts on $\\hat{x} = x - e$, so $u = -K(x - e)$ and the $+BKe$ term lands in the top-right block. It is non-zero and it matters — a bad estimate really does disturb the plant. What saves the design is only that the coupling is one-way.",
                            "If this block were zero the two halves would be completely decoupled, which is stronger than what is true: the estimation error does reach the plant, it just does not come back.",
                            "This is the estimator's own dynamics, which belongs on the diagonal rather than in the coupling block.",
                            "$A$ appears on both diagonal blocks, modified; it is not the coupling term.",
                        ],
                    },
                    {
                        "prompt": "One block is zero. What does that make the matrix?",
                        "hole": "?",
                        "opts": ["block upper triangular", "block diagonal", "block lower triangular", "symmetric"],
                        "a": 0,
                        "why": "The zero is in the bottom-left, so the matrix is upper triangular in blocks — and the eigenvalues of a block triangular matrix are the union of the blocks' own. The zero is the load-bearing part: the *plant* state does not appear in the error dynamics, which is the content of the previous module's result that the error forgets the input.",
                        "whys": [
                            "The zero is in the bottom-left, so the matrix is upper triangular in blocks — and the eigenvalues of a block triangular matrix are the union of the blocks' own. The zero is the load-bearing part: the *plant* state does not appear in the error dynamics, which is the content of the previous module's result that the error forgets the input.",
                            "Block diagonal would need the coupling term to vanish too. It does not — the estimation error genuinely perturbs the plant.",
                            "The zero block is below the diagonal, not above it, which is what makes this upper rather than lower.",
                            "The two diagonal blocks are different matrices entirely, so there is no symmetry here.",
                        ],
                    },
                    {
                        "prompt": "The second set of eigenvalues.",
                        "hole": "?",
                        "opts": ["A - L @ C", "A - B @ K", "A", "A + L @ C"],
                        "a": 0,
                        "why": "The observer's error dynamics, designed entirely from $(A, C, W, V)$ and untouched by the choice of $K$. A useful design rule falls straight out: make the observer poles a few times faster than the regulator's, so the estimate has settled before the controller needs it.",
                        "whys": [
                            "The observer's error dynamics, designed entirely from $(A, C, W, V)$ and untouched by the choice of $K$. A useful design rule falls straight out: make the observer poles a few times faster than the regulator's, so the estimate has settled before the controller needs it.",
                            "That is the first set, already listed. The point of the result is that the two sets are *different* and independent.",
                            "Plain $A$ is the open-loop plant, which appears nowhere in the closed loop.",
                            "The sign is flipped, which would place the error poles by mirroring them into the right half-plane.",
                        ],
                    },
                    {
                        "prompt": "So what is the practical consequence?",
                        "hole": "?",
                        "opts": [
                            "they may be designed independently",
                            "they must be designed together",
                            "they must use the same weights",
                            "they cancel each other out",
                        ],
                        "a": 0,
                        "why": "Design $K$ as if you had every state; design $L$ as if there were no controller; bolt them together and the closed-loop poles are exactly what each design asked for. Worth one caveat the algebra does not show: the guaranteed LQR margins from module 1 do not survive this, which is why LQG designs get checked for robustness rather than assumed to have it.",
                        "whys": [
                            "Design $K$ as if you had every state; design $L$ as if there were no controller; bolt them together and the closed-loop poles are exactly what each design asked for. Worth one caveat the algebra does not show: the guaranteed LQR margins from module 1 do not survive this, which is why LQG designs get checked for robustness rather than assumed to have it.",
                            "The whole result is that you need not — which is what makes the method tractable, since a joint optimisation over both would be far harder.",
                            "The cost weights and the noise covariances describe different things and are chosen from different evidence. They are unrelated.",
                            "They do not cancel; both sets of poles are present in the closed loop, and both must be stable.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Close the LQG loop on an unstable plant",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
The plant is an inverted-pendulum-like second-order system,
$\ddot{x} = 4x - 0.2\dot{x} + u$, so it falls over if left alone. Position is measured
and corrupted; velocity is not measured at all.

`care.py` gives you `solve_care` and `lqr` from module 2, unchanged and read-only. Write
the rest in `main.py`:

- `estimator_gain(A, C, W, V)` — solve the *dual* problem and return `L`, shape `(n, 1)`.
  One call to `solve_care` with the arguments transposed, then $L = YC^\top V^{-1}$.
- `combined_poles(A, B, C, K, L)` — build the $2n \times 2n$ matrix from the derivation
  and return its eigenvalues, sorted by real part.
- `simulate(A, B, C, K, L, dt, steps, W, V, seed, x0)` — run plant and estimator
  together with $u = -K\hat{x}$, returning `(positions, efforts)` as lists.

For the simulation, treat `W` and `V` as diagonal noise intensities and draw with

```text
rng   = np.random.default_rng(seed)
sig_w = np.sqrt(np.diag(W) * dt).reshape(n, 1)
sig_v = float(np.sqrt(V[0, 0] / dt))
```

Each step: compute `u` from the estimate, take the measurement `C @ x` plus
`sig_v * rng.normal()`, record, then advance the plant with
`+ sig_w * rng.normal(size=(n, 1))` and the estimator with the residual. Draw the
measurement noise before the process noise, or the seeded numbers will not match.
''',
                "files": [
                    {"name": "care.py", "ro": True, "content": r'''
"""The Riccati solver from module 2. Read-only — the checks depend on it."""
import numpy as np


def care_residual(A, B, Q, R, P):
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)
    P = np.asarray(P, dtype=float)
    return A.T @ P + P @ A - P @ B @ np.linalg.inv(R) @ B.T @ P + Q


def solve_care(A, B, Q, R, dt=0.002, steps=10000):
    A = np.asarray(A, dtype=float)
    P = np.zeros((A.shape[0], A.shape[0]))
    for _ in range(steps):
        P = P + dt * care_residual(A, B, Q, R, P)
    return P


def lqr(A, B, Q, R):
    B = np.asarray(B, dtype=float)
    R = np.asarray(R, dtype=float)
    P = solve_care(A, B, Q, R)
    return np.linalg.inv(R) @ B.T @ P, P
'''},
                    {"name": "main.py", "content": r'''
import numpy as np
from care import solve_care, lqr

A = np.array([[0.0, 1.0], [4.0, -0.2]])
B = np.array([[0.0], [1.0]])
C = np.array([[1.0, 0.0]])
Q = np.diag([2.0, 0.0])
R = np.array([[0.05]])
W = np.diag([0.001, 0.02])
V = np.array([[0.001]])


def estimator_gain(A, C, W, V):
    """L placing the estimator, from the dual Riccati equation. Shape (n, 1)."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float)
    V = np.asarray(V, dtype=float)
    # TODO: Y = solve_care(A.T, C.T, W, V), then L = Y @ C.T @ inv(V).
    return np.zeros((A.shape[0], 1))


def combined_poles(A, B, C, K, L):
    """Eigenvalues of [[A-BK, BK], [0, A-LC]], sorted by real part."""
    A = np.asarray(A, dtype=float)
    # TODO: build the two block rows with np.hstack, stack them, take eigvals,
    # and sort by real part.
    return np.zeros(2 * A.shape[0], dtype=complex)


def simulate(A, B, C, K, L, dt, steps, W, V, seed, x0):
    """Plant and estimator together under u = -K @ xhat. Return (positions, efforts)."""
    rng = np.random.default_rng(seed)
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)
    n = A.shape[0]
    x = np.array(x0, dtype=float).reshape(n, 1)
    xh = np.zeros((n, 1))
    sig_w = np.sqrt(np.diag(np.asarray(W, dtype=float)) * dt).reshape(n, 1)
    sig_v = float(np.sqrt(np.asarray(V, dtype=float)[0, 0] / dt))
    positions, efforts = [], []
    # TODO: the loop described in the brief.
    return positions, efforts


if __name__ == "__main__":
    K, P = lqr(A, B, Q, R)
    L = estimator_gain(A, C, W, V)
    print("K =", np.round(K, 6).tolist())
    print("L =", np.round(np.asarray(L).ravel(), 6).tolist())
    print("combined poles:", np.round(combined_poles(A, B, C, K, L), 5).tolist())
    pos, eff = simulate(A, B, C, K, L, 0.001, 10000, W, V, 4, [1.0, 0.0])
    if pos:
        tail = np.array(pos[5000:])
        print("rms position over the last 5 s:", round(float(np.sqrt(np.mean(tail ** 2))), 6))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np
from care import solve_care, lqr

A = np.array([[0.0, 1.0], [4.0, -0.2]])
B = np.array([[0.0], [1.0]])
C = np.array([[1.0, 0.0]])
Q = np.diag([2.0, 0.0])
R = np.array([[0.05]])
W = np.diag([0.001, 0.02])
V = np.array([[0.001]])


def estimator_gain(A, C, W, V):
    """L placing the estimator, from the dual Riccati equation. Shape (n, 1)."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float)
    V = np.asarray(V, dtype=float)
    Y = solve_care(A.T, C.T, W, V)
    return Y @ C.T @ np.linalg.inv(V)


def combined_poles(A, B, C, K, L):
    """Eigenvalues of [[A-BK, BK], [0, A-LC]], sorted by real part."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)
    n = A.shape[0]
    top = np.hstack([A - B @ K, B @ K])
    bot = np.hstack([np.zeros((n, n)), A - L @ C])
    ev = np.linalg.eigvals(np.vstack([top, bot]))
    return ev[np.argsort(np.real(ev))]


def simulate(A, B, C, K, L, dt, steps, W, V, seed, x0):
    """Plant and estimator together under u = -K @ xhat. Return (positions, efforts)."""
    rng = np.random.default_rng(seed)
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)
    n = A.shape[0]
    x = np.array(x0, dtype=float).reshape(n, 1)
    xh = np.zeros((n, 1))
    sig_w = np.sqrt(np.diag(np.asarray(W, dtype=float)) * dt).reshape(n, 1)
    sig_v = float(np.sqrt(np.asarray(V, dtype=float)[0, 0] / dt))
    positions, efforts = [], []
    for _ in range(steps):
        u = float(-(K @ xh)[0, 0])
        y = float((C @ x)[0, 0]) + sig_v * rng.normal()
        positions.append(float(x[0, 0]))
        efforts.append(u)
        x = x + dt * (A @ x + B * u) + sig_w * rng.normal(size=(n, 1))
        xh = xh + dt * (A @ xh + B * u + L @ (np.array([[y]]) - C @ xh))
    return positions, efforts


if __name__ == "__main__":
    K, P = lqr(A, B, Q, R)
    L = estimator_gain(A, C, W, V)
    print("K =", np.round(K, 6).tolist())
    print("L =", np.round(np.asarray(L).ravel(), 6).tolist())
    print("combined poles:", np.round(combined_poles(A, B, C, K, L), 5).tolist())
    pos, eff = simulate(A, B, C, K, L, 0.001, 10000, W, V, 4, [1.0, 0.0])
    if pos:
        tail = np.array(pos[5000:])
        print("rms position over the last 5 s:", round(float(np.sqrt(np.mean(tail ** 2))), 6))
'''}],
                "hints": [
                    "`estimator_gain` is two lines. `solve_care(A.T, C.T, W, V)` is the whole dual trick — the solver never learns it is doing estimation.",
                    "Do not transpose the result of `solve_care` before forming `L`. $Y$ is already symmetric, and $L = YC^\\top V^{-1}$ comes out `(n, 1)` on its own.",
                    "For `combined_poles`, the bottom-left block is zeros with the same shape as `A`. Getting that block wrong is the one way to make the separation check fail.",
                    "Draw the measurement noise before the process noise. Two calls to the same generator in the other order give a different, equally valid but non-matching run.",
                ],
                "tests": [
                    {"name": "the estimator gain comes from the dual equation", "code": r'''
import numpy as np
from care import care_residual
_L = np.asarray(estimator_gain(A, C, W, V), dtype=float)
assert _L.shape == (2, 1), f"L should be (n, 1) = (2, 1), got {_L.shape}"
_ev = np.real(np.linalg.eigvals(A - _L @ C))
assert float(np.max(_ev)) < 0, \
    f"the error dynamics A - LC must be stable; poles came out {_ev.tolist()}"
assert abs(float(_L[0, 0]) - 4.387664) < 1e-3, \
    f"expected L[0] near 4.387664 for this plant and noise model, got {float(_L[0,0]):.6f}"
'''},
                    {"name": "the closed-loop poles are the union of the two designs", "code": r'''
import numpy as np
_K, _P = lqr(A, B, Q, R)
_L = np.asarray(estimator_gain(A, C, W, V), dtype=float)
_got = np.asarray(combined_poles(A, B, C, _K, _L))
assert _got.shape == (4,), f"a 2-state plant gives 4 closed-loop poles, got shape {_got.shape}"
_ctrl = np.linalg.eigvals(A - B @ _K)
_est = np.linalg.eigvals(A - _L @ C)
_want = np.concatenate([_ctrl, _est])
_want = _want[np.argsort(np.real(_want))]
assert np.max(np.abs(np.sort_complex(_got) - np.sort_complex(_want))) < 1e-8, \
    f"separation says the poles are exactly the union; wanted {np.round(_want,5).tolist()}, got {np.round(_got,5).tolist()}"
'''},
                    {"name": "the loop catches the plant when there is no noise", "code": r'''
import numpy as np
_K, _P = lqr(A, B, Q, R)
_L = estimator_gain(A, C, W, V)
_pos, _eff = simulate(A, B, C, _K, _L, 0.001, 10000, np.zeros((2, 2)), np.zeros((1, 1)), 4, [1.0, 0.0])
assert len(_pos) == 10000, f"expected one sample per step, got {len(_pos)}"
assert abs(_pos[0] - 1.0) < 1e-12, f"the run starts at the initial position 1.0, got {_pos[0]}"
assert abs(_pos[-1]) < 1e-3, \
    f"with no noise the position must be driven to zero; after 10 s it is {_pos[-1]:.6f}"
'''},
                    {"name": "with feedback off the plant runs away", "code": r'''
import numpy as np
_L = estimator_gain(A, C, W, V)
_pos, _eff = simulate(A, B, C, np.zeros((1, 2)), _L, 0.001, 3000, W, V, 4, [1.0, 0.0])
assert abs(_pos[-1]) > 20.0, \
    f"with K = 0 this open-loop plant should diverge; after 3 s it is only at {_pos[-1]:.4f} — is u actually being applied?"
assert max(abs(e) for e in _eff) < 1e-12, "a zero gain must produce zero effort"
'''},
                    {"name": "the noisy loop stays bounded and repeats exactly", "code": r'''
import numpy as np
_K, _P = lqr(A, B, Q, R)
_L = estimator_gain(A, C, W, V)
_p1, _e1 = simulate(A, B, C, _K, _L, 0.001, 10000, W, V, 4, [1.0, 0.0])
_tail = np.array(_p1[5000:])
_rms = float(np.sqrt(np.mean(_tail ** 2)))
assert _rms < 0.6, \
    f"the regulator should hold the position near zero against this noise; rms over the last 5 s is {_rms:.4f}"
assert _rms > 0.01, \
    "with process and measurement noise present the position cannot sit exactly at zero — is the noise being drawn?"
_p2, _e2 = simulate(A, B, C, _K, _L, 0.001, 2000, W, V, 4, [1.0, 0.0])
_p3, _e3 = simulate(A, B, C, _K, _L, 0.001, 2000, W, V, 4, [1.0, 0.0])
assert _p2 == _p3, "the same seed must give the same run, or nothing here is reproducible"
'''},
                    {"name": "cheaper control moves the regulator poles only", "code": r'''
import numpy as np
_L = estimator_gain(A, C, W, V)
_est_before = sorted(np.real(np.linalg.eigvals(A - _L @ C)))
_Kd, _ = lqr(A, B, Q, np.array([[1.0]]))
_Kc, _ = lqr(A, B, Q, np.array([[0.005]]))
_slow = float(np.max(np.real(np.linalg.eigvals(A - B @ _Kd))))
_fast = float(np.max(np.real(np.linalg.eigvals(A - B @ _Kc))))
assert _fast < _slow - 0.5, \
    f"dropping R from 1 to 0.005 should push the regulator poles left; got {_fast:.4f} vs {_slow:.4f}"
_est_after = sorted(np.real(np.linalg.eigvals(A - _L @ C)))
assert max(abs(_a - _b) for _a, _b in zip(_est_before, _est_after)) < 1e-12, \
    "changing R must not move an estimator pole — that is the separation principle"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Regulate an unmeasured load through a flexible shaft",
        "runtime": "python",
        "minutes": 130,
        "brief": r'''
A motor drives a load through a shaft that is not rigid. Four states — motor angle and
speed, load angle and speed — one input, the motor torque, and one measurement, the
motor encoder. **The load angle you are asked to regulate is never measured**, and the
resonance between the two inertias sits at about 11 rad/s, so a controller that ignores
it will happily excite it.

Build the whole loop from the plant matrices upward.

1. `solve_care(A, B, Q, R)` — the Riccati solver from module 2, written again here. No
   library shortcut, and the checks read its residual.
2. `lqr(A, B, Q, R)` → `(K, P)`, the regulator.
3. `estimator_gain(A, C, W, V)` → `L`, from the dual equation.
4. `combined_poles(A, B, C, K, L)` — the $8 \times 8$ eigenvalues.
5. `simulate(...)` — plant and estimator together with seeded noise, returning the load
   angle and the torque at every step.

## Suggested order

Get `solve_care` right first and check it by its residual; everything downstream is a
transcription once that works. Then `lqr`, then `estimator_gain` (it is the same solver
with transposed arguments), then the assembly.

## Choosing the weights

The checks fix $Q$, $R$, $W$ and $V$ so that the numbers are reproducible, but the
comment you are asked to write should say what you would have chosen and why. The
supplied $Q = \text{diag}(1, 0, 20, 0)$ prices the load angle twenty times the motor
angle and does not price either speed at all; $R = 0.2$ is what stops the torque
demand from chasing the resonance.
''',
        "deliverables": [
            "`solve_care` and `lqr` in `main.py`, with the algebraic residual driven below 1e-6 on the four-state plant.",
            "`estimator_gain(A, C, W, V)` obtained from the same solver with transposed arguments, returning an `(n, 1)` array that makes `A - L@C` stable.",
            "`combined_poles(A, B, C, K, L)` returning the eight eigenvalues of the block system, sorted by real part.",
            "`simulate(...)` running plant and estimator under output feedback with seeded noise, returning `(load_angles, torques)`.",
            "A comment at the top of `main.py` naming the regulator and estimator pole sets your design produced, and one sentence on which entry of `Q` you would change first if the load overshot.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, and no control-systems package.",
            "The estimator may read the measurement and the applied torque, and nothing else. It must never touch the true state.",
            "Forward Euler at the timestep given; do not substitute a better integrator, because the seeded expectations depend on this one.",
            "Seed every random draw. A check that cannot be repeated is not a check.",
            "Draw the measurement noise before the process noise at each step, so the seeded stream matches.",
        ],
        "rubric": [
            {"criterion": "The Riccati solver is correct and proved", "weight": 30,
             "evidence": "solve_care drives the algebraic residual below 1e-6 on the four-state plant and on a one-state case whose closed form is known, and returns a symmetric positive-definite P."},
            {"criterion": "Estimator by duality", "weight": 25,
             "evidence": "estimator_gain calls the same solver with transposed arguments, returns an (n, 1) gain, and the resulting A - LC has every eigenvalue strictly in the left half-plane."},
            {"criterion": "Separation demonstrated", "weight": 20,
             "evidence": "The eight eigenvalues of the block system agree with the union of the regulator and estimator eigenvalues to within 1e-6, and changing R leaves the estimator poles untouched."},
            {"criterion": "The loop regulates the unmeasured load", "weight": 25,
             "evidence": "Released at 0.3 rad with the estimator starting at zero, the load angle is driven below 0.05 rad and stays there under noise, while the open-loop run does not."},
        ],
        "hints": [
            "`solve_care` is the same six lines as module 2. If it diverges on this plant, the resonance is faster than your timestep: halve `dt` and double `steps`.",
            "`estimator_gain` is `solve_care(A.T, C.T, W, V)` followed by `Y @ C.T @ np.linalg.inv(V)`. There is no second algorithm to write.",
            "`np.diag(W)` pulls the diagonal out of a matrix; `np.sqrt(np.diag(W) * dt).reshape(n, 1)` is the per-state noise scale for one Euler step.",
            "In the loop: compute `u` from the estimate, then the noisy measurement, then record, then advance the plant, then advance the estimator with the residual `y - C @ xh`.",
            "If the separation check fails but both gains look right, print the block matrix. The bottom-left block must be exactly `np.zeros((n, n))`.",
        ],
        "files": [
            {"name": "drive.py", "ro": True, "content": r'''
"""A motor driving a load through a compliant shaft. Read-only.

States are [motor angle, motor speed, load angle, load speed]; the input is motor
torque and the only measurement is the motor angle. The load angle, which is what
anyone actually cares about, is on the far side of the spring.
"""
import numpy as np

J_MOTOR = 0.05    # kg m^2
J_LOAD = 0.10     # kg m^2
K_SHAFT = 4.0     # N m / rad
D_SHAFT = 0.02    # N m s / rad


def drive():
    """Return (A, B, C) for the four-state flexible drive."""
    jm, jl, ks, d = J_MOTOR, J_LOAD, K_SHAFT, D_SHAFT
    A = np.array([
        [0.0, 1.0, 0.0, 0.0],
        [-ks / jm, -d / jm, ks / jm, d / jm],
        [0.0, 0.0, 0.0, 1.0],
        [ks / jl, d / jl, -ks / jl, -d / jl],
    ])
    B = np.array([[0.0], [1.0 / jm], [0.0], [0.0]])
    C = np.array([[1.0, 0.0, 0.0, 0.0]])
    return A, B, C


def weights():
    """The cost and noise models the checks are written against."""
    Q = np.diag([1.0, 0.0, 20.0, 0.0])
    R = np.array([[0.2]])
    W = np.diag([1e-4, 1e-2, 1e-4, 1e-2])
    V = np.array([[1e-5]])
    return Q, R, W, V
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from drive import drive, weights

# Design notes:
#   regulator poles -> TODO, and what set them
#   estimator poles -> TODO, and why they sit where they do
#   if the load overshot I would raise TODO first, because TODO


def care_residual(A, B, Q, R, P):
    """A.T @ P + P @ A - P @ B @ inv(R) @ B.T @ P + Q."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)
    P = np.asarray(P, dtype=float)
    # TODO
    return np.zeros_like(Q)


def solve_care(A, B, Q, R, dt=0.002, steps=10000):
    """Integrate the differential Riccati equation in time-to-go from P = 0."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    P = np.zeros((n, n))
    # TODO
    return P


def lqr(A, B, Q, R):
    """Return (K, P) with K = inv(R) @ B.T @ P, shape (1, n)."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    # TODO
    return np.zeros((1, n)), np.zeros((n, n))


def estimator_gain(A, C, W, V):
    """L from the dual Riccati equation, shape (n, 1)."""
    A = np.asarray(A, dtype=float)
    # TODO
    return np.zeros((A.shape[0], 1))


def combined_poles(A, B, C, K, L):
    """Eigenvalues of [[A-BK, BK], [0, A-LC]], sorted by real part."""
    A = np.asarray(A, dtype=float)
    # TODO
    return np.zeros(2 * A.shape[0], dtype=complex)


def simulate(A, B, C, K, L, dt, steps, W, V, seed, x0):
    """Plant and estimator under u = -K @ xhat. Return (load_angles, torques)."""
    rng = np.random.default_rng(seed)
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)
    n = A.shape[0]
    x = np.array(x0, dtype=float).reshape(n, 1)
    xh = np.zeros((n, 1))
    sig_w = np.sqrt(np.diag(np.asarray(W, dtype=float)) * dt).reshape(n, 1)
    sig_v = float(np.sqrt(np.asarray(V, dtype=float)[0, 0] / dt))
    angles, torques = [], []
    # TODO: u from the estimate; y = C @ x plus sig_v * rng.normal(); record the
    # load angle (index 2) and u; advance the plant with sig_w * rng.normal(size=(n,1));
    # advance the estimator with the residual.
    return angles, torques


if __name__ == "__main__":
    A, B, C = drive()
    Q, R, W, V = weights()
    K, P = lqr(A, B, Q, R)
    L = estimator_gain(A, C, W, V)
    print("K =", np.round(K, 5).tolist())
    print("L =", np.round(np.asarray(L).ravel(), 5).tolist())
    print("residual =", float(np.linalg.norm(care_residual(A, B, Q, R, P))))
    angles, torques = simulate(A, B, C, K, L, 0.001, 8000, W, V, 11, [0.0, 0.0, 0.3, 0.0])
    if angles:
        print("load angle at 8 s :", round(angles[-1], 6))
        print("peak torque       :", round(max(abs(t) for t in torques), 6))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from drive import drive, weights

# Design notes:
#   regulator poles -> -2.46 +/- 11.89j and -5.97 +/- 4.47j. The first pair is the
#     shaft resonance, now damped rather than moved; the second is the rigid-body
#     mode that Q's load-angle weight of 20 pulled in. R = 0.2 is what keeps the
#     peak torque under 1 N m.
#   estimator poles -> -1.93 +/- 11.06j and -3.62 +/- 3.06j. Set by V = 1e-5, an
#     encoder far quieter than the torque disturbance, so the filter leans on the
#     measurement and still damps the resonance it has to infer.
#   if the load overshot I would raise Q[3, 3] first, because the load *speed* is
#     currently unpriced, so nothing in the cost objects to arriving fast and ringing.


def care_residual(A, B, Q, R, P):
    """A.T @ P + P @ A - P @ B @ inv(R) @ B.T @ P + Q."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    Q = np.asarray(Q, dtype=float)
    R = np.asarray(R, dtype=float)
    P = np.asarray(P, dtype=float)
    return A.T @ P + P @ A - P @ B @ np.linalg.inv(R) @ B.T @ P + Q


def solve_care(A, B, Q, R, dt=0.002, steps=10000):
    """Integrate the differential Riccati equation in time-to-go from P = 0."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    P = np.zeros((n, n))
    for _ in range(steps):
        P = P + dt * care_residual(A, B, Q, R, P)
    return P


def lqr(A, B, Q, R):
    """Return (K, P) with K = inv(R) @ B.T @ P, shape (1, n)."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    R = np.asarray(R, dtype=float)
    P = solve_care(A, B, Q, R)
    return np.linalg.inv(R) @ B.T @ P, P


def estimator_gain(A, C, W, V):
    """L from the dual Riccati equation, shape (n, 1)."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float)
    V = np.asarray(V, dtype=float)
    Y = solve_care(A.T, C.T, W, V)
    return Y @ C.T @ np.linalg.inv(V)


def combined_poles(A, B, C, K, L):
    """Eigenvalues of [[A-BK, BK], [0, A-LC]], sorted by real part."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)
    n = A.shape[0]
    top = np.hstack([A - B @ K, B @ K])
    bot = np.hstack([np.zeros((n, n)), A - L @ C])
    ev = np.linalg.eigvals(np.vstack([top, bot]))
    return ev[np.argsort(np.real(ev))]


def simulate(A, B, C, K, L, dt, steps, W, V, seed, x0):
    """Plant and estimator under u = -K @ xhat. Return (load_angles, torques)."""
    rng = np.random.default_rng(seed)
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)
    n = A.shape[0]
    x = np.array(x0, dtype=float).reshape(n, 1)
    xh = np.zeros((n, 1))
    sig_w = np.sqrt(np.diag(np.asarray(W, dtype=float)) * dt).reshape(n, 1)
    sig_v = float(np.sqrt(np.asarray(V, dtype=float)[0, 0] / dt))
    angles, torques = [], []
    for _ in range(steps):
        u = float(-(K @ xh)[0, 0])
        y = float((C @ x)[0, 0]) + sig_v * rng.normal()
        angles.append(float(x[2, 0]))
        torques.append(u)
        x = x + dt * (A @ x + B * u) + sig_w * rng.normal(size=(n, 1))
        xh = xh + dt * (A @ xh + B * u + L @ (np.array([[y]]) - C @ xh))
    return angles, torques


if __name__ == "__main__":
    A, B, C = drive()
    Q, R, W, V = weights()
    K, P = lqr(A, B, Q, R)
    L = estimator_gain(A, C, W, V)
    print("K =", np.round(K, 5).tolist())
    print("L =", np.round(np.asarray(L).ravel(), 5).tolist())
    print("residual =", float(np.linalg.norm(care_residual(A, B, Q, R, P))))
    angles, torques = simulate(A, B, C, K, L, 0.001, 8000, W, V, 11, [0.0, 0.0, 0.3, 0.0])
    if angles:
        print("load angle at 8 s :", round(angles[-1], 6))
        print("peak torque       :", round(max(abs(t) for t in torques), 6))
'''},
        ],
        "tests": [
            {"name": "the Riccati solver leaves no residual on the four-state plant", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
_P = solve_care(_A, _B, _Q, _R)
assert _P.shape == (4, 4), f"P is n x n = (4, 4), got {_P.shape}"
_n = float(np.linalg.norm(care_residual(_A, _B, _Q, _R, _P)))
assert _n < 1e-6, f"the algebraic residual must vanish at the solution; its norm is {_n:.3e}"
assert np.max(np.abs(_P - _P.T)) < 1e-9, "the cost-to-go matrix must be symmetric"
assert float(np.min(np.linalg.eigvalsh(_P))) > 0, \
    "every non-zero state costs something, so P must be positive definite"
'''},
            {"name": "the solver agrees with the closed form in one dimension", "code": r'''
import numpy as np
_P = solve_care(np.array([[1.0]]), np.array([[1.0]]), np.array([[1.0]]), np.array([[1.0]]))
assert abs(float(_P[0, 0]) - (1.0 + np.sqrt(2.0))) < 1e-6, \
    f"a = b = q = r = 1 gives p = 1 + sqrt(2) = 2.414214 exactly; got {float(_P[0,0]):.6f}"
_K, _ = lqr(np.array([[2.0]]), np.array([[1.0]]), np.array([[1.0]]), np.array([[1.0]]))
_pole = 2.0 - float(_K[0, 0])
assert abs(_pole + np.sqrt(5.0)) < 1e-6, \
    f"an unstable scalar plant closes at -sqrt(a^2 + q b^2/r) = -2.236068; got {_pole:.6f}"
'''},
            {"name": "the regulator stabilises a plant that has a free rigid-body mode", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
assert float(np.max(np.real(np.linalg.eigvals(_A)))) > -1e-9, \
    "this drive has a double integrator in it; the fixture is meant to be non-asymptotic"
_K, _P = lqr(_A, _B, _Q, _R)
assert _K.shape == (1, 4), f"K should be (1, 4), got {_K.shape}"
_cl = np.real(np.linalg.eigvals(_A - _B @ _K))
assert float(np.max(_cl)) < -1.0, \
    f"every regulator pole should be comfortably in the left half-plane; got {np.round(_cl,4).tolist()}"
'''},
            {"name": "the estimator is the same solver with transposed arguments", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
_L = np.asarray(estimator_gain(_A, _C, _W, _V), dtype=float)
assert _L.shape == (4, 1), f"L should be (n, 1) = (4, 1), got {_L.shape}"
_Y = solve_care(_A.T, _C.T, _W, _V)
_n = float(np.linalg.norm(care_residual(_A.T, _C.T, _W, _V, _Y)))
assert _n < 1e-6, f"the dual equation must also be solved, not approximated; residual {_n:.3e}"
_ev = np.real(np.linalg.eigvals(_A - _L @ _C))
assert float(np.max(_ev)) < 0, \
    f"A - LC must be stable or the estimate never converges; got {np.round(_ev,4).tolist()}"
'''},
            {"name": "the eight closed-loop poles are the union of the two designs", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
_K, _P = lqr(_A, _B, _Q, _R)
_L = np.asarray(estimator_gain(_A, _C, _W, _V), dtype=float)
_got = np.asarray(combined_poles(_A, _B, _C, _K, _L))
assert _got.shape == (8,), f"four states plus four errors is eight poles; got shape {_got.shape}"
_want = np.concatenate([np.linalg.eigvals(_A - _B @ _K), np.linalg.eigvals(_A - _L @ _C)])
assert np.max(np.abs(np.sort_complex(_got) - np.sort_complex(_want))) < 1e-6, \
    "the block matrix is upper triangular, so its spectrum is exactly the union — check the zero block"
'''},
            {"name": "changing the effort weight leaves the estimator alone", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
_L = np.asarray(estimator_gain(_A, _C, _W, _V), dtype=float)
_before = sorted(np.real(np.linalg.eigvals(_A - _L @ _C)))
_Kd, _ = lqr(_A, _B, _Q, np.array([[2.0]]))
_Kc, _ = lqr(_A, _B, _Q, np.array([[0.02]]))
assert np.linalg.norm(_Kc) > 2.0 * np.linalg.norm(_Kd), \
    f"a hundred-fold cheaper torque should buy a much larger gain; |K| went {np.linalg.norm(_Kd):.3f} -> {np.linalg.norm(_Kc):.3f}"
_after = sorted(np.real(np.linalg.eigvals(_A - _L @ _C)))
assert max(abs(_a - _b) for _a, _b in zip(_before, _after)) < 1e-12, \
    "R belongs to the regulator only; if the estimator poles moved, the two designs are coupled somewhere"
'''},
            {"name": "the unmeasured load is brought home", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
_K, _P = lqr(_A, _B, _Q, _R)
_L = estimator_gain(_A, _C, _W, _V)
_ang, _tau = simulate(_A, _B, _C, _K, _L, 0.001, 8000, _W, _V, 11, [0.0, 0.0, 0.3, 0.0])
assert len(_ang) == 8000, f"expected one sample per step, got {len(_ang)}"
assert abs(_ang[0] - 0.3) < 1e-12, f"the run starts at 0.3 rad, got {_ang[0]}"
_tail = max(abs(a) for a in _ang[4000:])
assert _tail < 0.05, \
    f"the load angle should be held below 0.05 rad after 4 s; the worst of the tail is {_tail:.4f}"
assert max(abs(t) for t in _tau) < 5.0, \
    f"peak torque of {max(abs(t) for t in _tau):.3f} N m is far more than this design should need"
'''},
            {"name": "without the regulator the load does not settle", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
_L = estimator_gain(_A, _C, _W, _V)
_ang, _tau = simulate(_A, _B, _C, np.zeros((1, 4)), _L, 0.001, 8000, _W, _V, 11, [0.0, 0.0, 0.3, 0.0])
_tail = max(abs(a) for a in _ang[4000:])
assert _tail > 0.2, \
    f"with K = 0 the shaft should still be ringing at 0.3 rad amplitude; the tail is only {_tail:.4f} — is u reaching the plant?"
assert max(abs(t) for t in _tau) < 1e-12, "a zero gain must command zero torque"
'''},
            {"name": "the run is reproducible and the estimator never peeks", "code": r'''
import numpy as np
from drive import drive, weights
_A, _B, _C = drive()
_Q, _R, _W, _V = weights()
_K, _P = lqr(_A, _B, _Q, _R)
_L = estimator_gain(_A, _C, _W, _V)
_a1, _t1 = simulate(_A, _B, _C, _K, _L, 0.001, 2000, _W, _V, 11, [0.0, 0.0, 0.3, 0.0])
_a2, _t2 = simulate(_A, _B, _C, _K, _L, 0.001, 2000, _W, _V, 11, [0.0, 0.0, 0.3, 0.0])
assert _a1 == _a2 and _t1 == _t2, "the same seed must reproduce the run exactly"
_a3, _t3 = simulate(_A, _B, _C, _K, _L, 0.001, 2000, _W, _V, 12, [0.0, 0.0, 0.3, 0.0])
assert _a1 != _a3, "a different seed must give a different noise realisation"
_clean, _ = simulate(_A, _B, _C, _K, _L, 0.001, 8000, np.zeros((4, 4)), np.zeros((1, 1)),
                     11, [0.0, 0.0, 0.3, 0.0])
assert abs(_clean[-1]) < 1e-3, \
    f"with the noise switched off the load must reach zero; it is at {_clean[-1]:.6f} — an estimator reading the true state would also pass everything above, this is the check that does not"
'''},
        ],
    },
}
