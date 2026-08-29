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
                        "placeholder": "2 a p + q - \\frac{p^2 b^2}{r}",
                        "hint": "$A^\\top P + P A$ becomes $ap + pa = 2ap$. The middle term $P B R^{-1} B^\\top P$ becomes $p b (1/r) b p$.",
                        "deconstruct": [
                            "The two linear terms collapse to $2ap$.",
                            "The quadratic term is $p^2 b^2 / r$, and it enters with a minus sign.",
                        ],
                    },
                    {
                        "prompt": "The gain is $K = R^{-1}B^\\top P$. Write $k$ in terms of $b$, $p$ and $r$.",
                        "answer": "\\frac{b p}{r}",
                        "placeholder": "\\frac{b p}{r}",
                        "hint": "Read the matrix formula one factor at a time: $R^{-1}$ is $1/r$, $B^\\top$ is $b$, $P$ is $p$.",
                        "deconstruct": [
                            "$R^{-1} = 1/r$.",
                            "Multiply by $b$ and then by $p$.",
                        ],
                    },
                    {
                        "prompt": "Under $u = -kx$ the closed loop is $\\dot{x} = (a - bk)x$. Write that pole in terms of $a$, $b$, $p$ and $r$.",
                        "answer": "a - \\frac{b^2 p}{r}",
                        "placeholder": "a - \\frac{b^2 p}{r}",
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
                        "placeholder": "-\\sqrt{a^2 + \\frac{q b^2}{r}}",
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
                        "placeholder": "\\frac{a b p}{r + b^2 p}",
                        "hint": "The derivative is $2ru + 2bp(ax + bu)$. Collect the $u$ terms on one side.",
                        "deconstruct": [
                            "Setting the derivative to zero: $ru + bp(ax + bu) = 0$, so $u(r + b^2 p) = -abpx$.",
                            "That is $u = -kx$ with $k$ the ratio you were asked for.",
                        ],
                    },
                    {
                        "prompt": "Write the closed-loop factor $a - bk$ using the same symbols.",
                        "answer": "\\frac{a r}{r + b^2 p}",
                        "placeholder": "\\frac{a r}{r + b^2 p}",
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
                        "placeholder": "q + \\frac{a^2 r p}{r + b^2 p}",
                        "hint": "$rk^2 = \\frac{a^2b^2rp^2}{(r+b^2p)^2}$ and $p(a-bk)^2 = \\frac{a^2r^2p}{(r+b^2p)^2}$. Add them and factor $a^2rp$ out of the numerator.",
                        "deconstruct": [
                            "The two numerators are $a^2 b^2 r p^2$ and $a^2 r^2 p$, which sum to $a^2 r p (b^2 p + r)$.",
                            "One factor of $(r + b^2 p)$ cancels against the denominator.",
                        ],
                    },
                    {
                        "prompt": "Switch the control off by setting $b = 0$, so the recursion is just $p_{new} = q + a^2 p$. Write the value $p$ settles at.",
                        "answer": "\\frac{q}{1 - a^2}",
                        "placeholder": "\\frac{q}{1 - a^2}",
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
                        "placeholder": "(1 - k)^2 p + k^2 r",
                        "hint": "Scaling a random variable by $c$ multiplies its variance by $c^2$, and the cross term vanishes by independence.",
                        "deconstruct": [
                            "$\\text{Var}((1-k)e) = (1-k)^2 p$.",
                            "$\\text{Var}(-kv) = k^2 r$, and there is no cross term.",
                        ],
                    },
                    {
                        "prompt": "Differentiate that with respect to $k$, set it to zero, and write the minimising $k$.",
                        "answer": "\\frac{p}{p + r}",
                        "placeholder": "\\frac{p}{p + r}",
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
                        "placeholder": "\\frac{p r}{p + r}",
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
                        "placeholder": "\\frac{q}{2} + \\frac{1}{2}\\sqrt{q^2 + 4 q r}",
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
                        "placeholder": "K e - K x",
                        "hint": "Substitute and distribute the minus sign across both terms.",
                        "deconstruct": [
                            "$u = -K(x - e)$.",
                            "Distribute: one term in $x$, one in $e$.",
                        ],
                    },
                    {
                        "prompt": "Put that into $\\dot{x} = Ax + Bu$ (leave the noise out for now) and write $\\dot{x}$ in terms of $A$, $B$, $K$, $x$ and $e$.",
                        "answer": "A x - B K x + B K e",
                        "placeholder": "A x - B K x + B K e",
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
                        "placeholder": "A - LC",
                        "hint": "The $Bu$ terms are identical in the two equations and cancel, whatever $u$ happens to be.",
                        "deconstruct": [
                            "Plant minus estimator: $\\dot{e} = Ax - A\\hat{x} - LCx + LC\\hat{x} + w - Lv$.",
                            "Group the $x$ and $\\hat{x}$ terms; both give the same matrix acting on $e$.",
                        ],
                    },
                    {
                        "prompt": "The two blocks are decoupled one way, so the poles are the union and the noise cannot move them — it only sets the size of the residual motion. For a scalar mode $\\dot{z} = \\mu z + n$ driven by white noise of intensity $s$, the stationary variance satisfies $2\\mu\\sigma^2 + s = 0$. Write $\\sigma^2$.",
                        "answer": "-\\frac{s}{2 \\mu}",
                        "placeholder": "-\\frac{s}{2 \\mu}",
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
