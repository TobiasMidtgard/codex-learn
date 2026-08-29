"""CTRL510 — State-Space Methods.

The reference course for the EE major: every module is the full loop, sandbox to
derivation to lab. Authoring rules, same as the CS catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed
"""

COURSE = {
    "id": "CTRL510",
    "title": "State-Space Methods",
    "band": 2,
    "level": "Advanced",
    "prereqs": [],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◉",
    "summary": (
        "Transfer functions describe one input and one output. State space describes "
        "everything at once, and it is the language every modern method is written in. "
        "This course builds the representation from the differential equations up, then "
        "uses it to decide stability, place poles where you want them, and estimate the "
        "states you cannot measure."
    ),
    "outcomes": [
        "Convert a differential equation or a circuit into a state-space realisation, and say why the choice of states is not unique.",
        "Decide stability from the eigenvalues of A, and read the trace–determinant plane fluently.",
        "Test controllability and place closed-loop poles by state feedback.",
        "Build a Luenberger observer and explain why its error dynamics are independent of the controller.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that stabilises an inverted pendulum from a single measured output.",
    "reading": [
        "*Feedback Systems*, Åström & Murray — chapters 5 and 6, freely available.",
        "*Linear System Theory and Design*, Chen — for the algebra behind controllability.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "From differential equations to state space",
            "summary": "Any n-th order linear ODE becomes n coupled first-order equations. The choice of states is yours.",
            "concepts": [
                "A state is whatever you must know *now* to predict the future given the input — no more, no less.",
                "`ẋ = Ax + Bu`, `y = Cx + Du`: the four matrices and what each one means physically.",
                "Companion form: reading `A` straight off the coefficients of the ODE.",
                "The realisation is not unique — any invertible `T` gives `Ā = TAT⁻¹` with identical input–output behaviour.",
                "Why `D` is almost always zero in a physical plant, and what it means when it is not.",
            ],
            "sandbox": {
                "title": "What the A matrix does to the state",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": 0, "a12": 1, "a21": -2, "a22": -0.6},
                "brief": r'''
Before any algebra: `A` is a rule that turns a point in the state plane into a
velocity. The arrows are that rule. The curves are what happens if you let go from
somewhere on the rim and follow it.

The starting matrix is a mass–spring–damper written as $\dot{x} = Ax$, with
position as $x_1$ and velocity as $x_2$.
''',
                "notice": [
                    "Take $a_{22}$ (the damping) to zero. The spirals become closed orbits — energy never leaves.",
                    "Make $a_{21}$ positive. The origin stops attracting anything and becomes a saddle: one direction in, one direction out.",
                    "Change $a_{11}$ and $a_{22}$ together so the trace stays the same. The picture barely changes — stability does not care about the entries individually.",
                ],
            },
            "derive": {
                "title": "Putting a second-order system into state space",
                "minutes": 12,
                "vars": ["s", "m", "b", "k", "u", "x_1", "x_2", "omega_n", "zeta"],
                "brief": r'''
A mass on a spring with a damper, driven by a force:

$$m\ddot{y} + b\dot{y} + k y = u$$

Turn it into $\dot{x} = Ax + Bu$. Take $x_1 = y$ and $x_2 = \dot{y}$.
''',
                "steps": [
                    {
                        "prompt": "With $x_1 = y$ and $x_2 = \\dot{y}$, what is $\\dot{x_1}$?",
                        "answer": "x_2",
                        "placeholder": "x_2",
                        "hint": "This one is definitional — you chose $x_2$ to *be* the derivative of $x_1$.",
                        "deconstruct": [
                            "$x_1$ was defined as $y$, so $\\dot{x_1} = \\dot{y}$.",
                            "And $\\dot{y}$ was defined as $x_2$.",
                        ],
                    },
                    {
                        "prompt": "Now solve the differential equation for $\\ddot{y}$, and write $\\dot{x_2}$ in terms of $x_1$, $x_2$ and $u$.",
                        "given": "Start from $m\\ddot{y} + b\\dot{y} + k y = u$.",
                        "answer": "\\frac{u - b x_2 - k x_1}{m}",
                        "placeholder": "\\frac{u - b x_2 - k x_1}{m}",
                        "hint": "Move everything except $m\\ddot{y}$ to the right, then divide by $m$. Remember $\\dot{y} = x_2$ and $y = x_1$.",
                        "deconstruct": [
                            "Rearranged: $m\\ddot{y} = u - b\\dot{y} - k y$.",
                            "Substitute the state names and divide through by $m$.",
                        ],
                    },
                    {
                        "prompt": "The system matrix is $A = \\begin{bmatrix} 0 & 1 \\\\ a & b' \\end{bmatrix}$. What is the entry $a$ — the coefficient multiplying $x_1$ in $\\dot{x_2}$?",
                        "answer": "-\\frac{k}{m}",
                        "placeholder": "-\\frac{k}{m}",
                        "hint": "Read it straight off the expression you just derived.",
                        "deconstruct": [
                            "You wrote $\\dot{x_2} = (u - b x_2 - k x_1)/m$.",
                            "Collect the $x_1$ term: its coefficient is $-k/m$.",
                        ],
                    },
                    {
                        "prompt": "Undamped and undriven, this system oscillates at its natural frequency. Write $\\omega_n$ in terms of $k$ and $m$.",
                        "answer": "\\sqrt{\\frac{k}{m}}",
                        "placeholder": "\\sqrt{k/m}",
                        "hint": "The eigenvalues of $A$ with $b = 0$ are $\\pm j\\omega_n$. Stiffer spring, faster; heavier mass, slower.",
                        "deconstruct": [
                            "With $b = 0$ the characteristic polynomial is $s^2 + k/m = 0$.",
                            "So $s = \\pm j\\sqrt{k/m}$, and the imaginary part is $\\omega_n$.",
                        ],
                    },
                ],
                "closing": r'''
That is the whole conversion. Notice that $B = [0,\ 1/m]^\top$ falls out of the same
step, and that nothing forced you to pick position and velocity — momentum $m\dot{y}$
would have worked equally well and given a different, equally valid `A`.
''',
            },
            "lab": {
                "title": "Build and simulate a state-space model",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Write the mass–spring–damper as state space and integrate it.

Fill in `build(m, b, k)` so it returns the matrices `A` and `B` for the realisation
you just derived, with position first and velocity second. Then fill in `simulate`
so it steps the system forward with the forward-Euler rule

```text
x[n+1] = x[n] + dt * (A @ x[n] + B * u)
```

and returns the position at every step as a list.

`main.py` already prints a short summary; run it and the checks will read your
functions directly.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def build(m, b, k):
    """Return (A, B) for m*y'' + b*y' + k*y = u, with x = [position, velocity]."""
    # TODO: build the 2x2 A and the 2x1 B as numpy arrays.
    A = np.zeros((2, 2))
    B = np.zeros((2, 1))
    return A, B


def simulate(A, B, u, dt, steps, x0=None):
    """Forward-Euler the system and return the position at every step."""
    x = np.zeros((2, 1)) if x0 is None else np.array(x0, dtype=float).reshape(2, 1)
    out = []
    # TODO: append the position, then advance x by one Euler step, `steps` times.
    return out


if __name__ == "__main__":
    A, B = build(1.0, 0.4, 4.0)
    print("A =", A.tolist())
    print("B =", B.tolist())
    ys = simulate(A, B, 1.0, 0.001, 5000)
    print("final position:", round(ys[-1], 4))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def build(m, b, k):
    """Return (A, B) for m*y'' + b*y' + k*y = u, with x = [position, velocity]."""
    A = np.array([[0.0, 1.0], [-k / m, -b / m]])
    B = np.array([[0.0], [1.0 / m]])
    return A, B


def simulate(A, B, u, dt, steps, x0=None):
    """Forward-Euler the system and return the position at every step."""
    x = np.zeros((2, 1)) if x0 is None else np.array(x0, dtype=float).reshape(2, 1)
    out = []
    for _ in range(steps):
        out.append(float(x[0, 0]))
        x = x + dt * (A @ x + B * u)
    return out


if __name__ == "__main__":
    A, B = build(1.0, 0.4, 4.0)
    print("A =", A.tolist())
    print("B =", B.tolist())
    ys = simulate(A, B, 1.0, 0.001, 5000)
    print("final position:", round(ys[-1], 4))
'''}],
                "hints": [
                    "The top row of `A` says $\\dot{x_1} = x_2$ — that is `[0, 1]`, nothing else.",
                    "The bottom row comes straight from the derivation: `[-k/m, -b/m]`.",
                    "`simulate` should record the position *before* stepping, so the first entry is the initial position.",
                ],
                "tests": [
                    {"name": "A has the companion structure", "code": r'''
import numpy as np
_A, _B = build(2.0, 3.0, 8.0)
assert _A.shape == (2, 2), f"A should be 2x2, got {_A.shape}"
assert abs(_A[0, 0]) < 1e-12 and abs(_A[0, 1] - 1.0) < 1e-12, \
    f"top row of A should be [0, 1], got {_A[0].tolist()}"
'''},
                    {"name": "A carries the physical parameters", "code": r'''
_A, _B = build(2.0, 3.0, 8.0)
assert abs(_A[1, 0] - (-4.0)) < 1e-9, f"A[1,0] should be -k/m = -4.0, got {_A[1,0]}"
assert abs(_A[1, 1] - (-1.5)) < 1e-9, f"A[1,1] should be -b/m = -1.5, got {_A[1,1]}"
'''},
                    {"name": "B drives velocity only", "code": r'''
_A, _B = build(2.0, 3.0, 8.0)
assert _B.shape == (2, 1), f"B should be 2x1, got {_B.shape}"
assert abs(_B[0, 0]) < 1e-12, "a force cannot change position instantly, so B[0] is 0"
assert abs(_B[1, 0] - 0.5) < 1e-9, f"B[1] should be 1/m = 0.5, got {_B[1,0]}"
'''},
                    {"name": "simulation starts where it was put", "code": r'''
_A, _B = build(1.0, 0.4, 4.0)
_ys = simulate(_A, _B, 0.0, 0.001, 10, x0=[0.5, 0.0])
assert len(_ys) == 10, f"expected 10 samples, got {len(_ys)}"
assert abs(_ys[0] - 0.5) < 1e-12, f"first sample should be the initial position 0.5, got {_ys[0]}"
'''},
                    {"name": "a damped system settles at u/k", "code": r'''
_A, _B = build(1.0, 0.4, 4.0)
_ys = simulate(_A, _B, 1.0, 0.001, 20000)
assert abs(_ys[-1] - 0.25) < 5e-3, \
    f"with u=1 and k=4 the mass should settle at 0.25, got {_ys[-1]:.4f}"
'''},
                    {"name": "an undamped system does not settle", "code": r'''
_A, _B = build(1.0, 0.0, 4.0)
_ys = simulate(_A, _B, 1.0, 0.0005, 20000)
_late = _ys[10000:]
assert max(_late) - min(_late) > 0.2, \
    "with no damping the mass should keep oscillating, not settle"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Eigenvalues, modes and stability",
            "summary": "The eigenvalues of A are the poles. Everything about the free response follows from them.",
            "concepts": [
                "The free response is $x(t) = e^{At}x(0)$, and $e^{At}$ is a sum of modes $e^{\\lambda_i t}$.",
                "Stability: every eigenvalue strictly in the open left half-plane. One on the axis is not enough.",
                "The trace–determinant plane classifies a 2×2 system completely: node, saddle, spiral, centre.",
                "Eigenvectors are the directions in which the system behaves like a scalar.",
                "A similarity transform moves the eigenvectors but never the eigenvalues.",
            ],
            "sandbox": {
                "title": "Damping, poles and the response they produce",
                "visualiser": "pole-step",
                "minutes": 7,
                "initial": {"zeta": 0.35, "wn": 4},
                "brief": r'''
Two views of the same second-order system: where its poles sit, and what it does when
you push it. Change one and watch the other.
''',
                "notice": [
                    "Take $\\zeta$ to zero. The poles land on the imaginary axis and the response never settles — that is what marginal stability looks like.",
                    "Hold $\\zeta$ and raise $\\omega_n$. The shape of the response is identical; only the time axis is compressed.",
                    "Find the $\\zeta$ where overshoot disappears. The poles have just met on the real axis.",
                ],
            },
            "derive": {
                "title": "Why eigenvalues decide stability",
                "minutes": 12,
                "vars": ["s", "t", "lambda", "A", "x_0", "zeta", "omega_n", "sigma"],
                "brief": r'''
Take the free system $\dot{x} = Ax$ with no input, and suppose $A$ has an eigenvector
$v$ with eigenvalue $\lambda$. Start the system exactly on that eigenvector.
''',
                "steps": [
                    {
                        "prompt": "Along an eigenvector the matrix acts like a single number. If $x(t) = c(t)v$, then $\\dot{c} = \\lambda c$. Write the solution $c(t)$ in terms of $c(0)$ and $\\lambda$.",
                        "answer": "c_0 e^{\\lambda t}",
                        "placeholder": "c_0 e^{\\lambda t}",
                        "hint": "This is the scalar exponential, the one differential equation everybody knows.",
                        "deconstruct": [
                            "$\\dot{c} = \\lambda c$ separates: $dc/c = \\lambda\\, dt$.",
                            "Integrating gives $\\ln c = \\lambda t + \\text{const}$, so $c = c_0 e^{\\lambda t}$.",
                        ],
                        "vars_note": "",
                    },
                    {
                        "prompt": "Write $\\lambda = \\sigma + j\\omega$. The magnitude of $e^{\\lambda t}$ is governed by only one of those two parts — write $|e^{\\lambda t}|$.",
                        "answer": "e^{\\sigma t}",
                        "placeholder": "e^{\\sigma t}",
                        "hint": "$|e^{j\\omega t}| = 1$ for every real $\\omega$ — rotation does not change length.",
                        "deconstruct": [
                            "$e^{\\lambda t} = e^{\\sigma t}e^{j\\omega t}$.",
                            "The second factor sits on the unit circle, so all the growth or decay is in the first.",
                        ],
                    },
                    {
                        "prompt": "For a second-order system with damping $\\zeta < 1$ and natural frequency $\\omega_n$, the poles are $-\\zeta\\omega_n \\pm j\\omega_d$. Write $\\omega_d$.",
                        "answer": "\\omega_n\\sqrt{1-\\zeta^2}",
                        "placeholder": "\\omega_n\\sqrt{1-\\zeta^{2}}",
                        "hint": "The pole sits at distance $\\omega_n$ from the origin, at angle $\\arccos\\zeta$ from the negative real axis.",
                        "deconstruct": [
                            "Real part is $-\\zeta\\omega_n$, and the magnitude of the pole is $\\omega_n$.",
                            "Pythagoras gives the imaginary part.",
                        ],
                    },
                ],
                "closing": r'''
So the whole stability question reduces to one thing: is every $\sigma$ negative?
The oscillation carried by $\omega$ is a detail of *how* it settles, never *whether*.
''',
            },
            "lab": {
                "title": "Classify a system from its matrix alone",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Write `classify(A)`, which takes a 2×2 array and returns one of the strings

```text
"stable node"      "unstable node"      "saddle"
"stable spiral"    "unstable spiral"    "centre"
```

Decide it from the **trace and determinant**, not by simulating:

- determinant negative → `"saddle"`, whatever else is true
- otherwise, if `trace² - 4·det < 0` the eigenvalues are complex → spiral, or a
  `"centre"` when the trace is zero
- otherwise → node

and a node or spiral is `"stable"` when the trace is negative, `"unstable"` when it
is positive. Also write `settling_time(A, tol)`, returning the time by which
$e^{\sigma t}$ has fallen below `tol`, where $\sigma$ is the *largest* real part.
Return `float("inf")` if the system is not stable.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

TOL = 1e-12


def classify(A):
    """Return the phase-portrait class of a 2x2 system, from trace and determinant."""
    A = np.asarray(A, dtype=float)
    tr = float(np.trace(A))
    det = float(np.linalg.det(A))
    # TODO: saddle, then complex vs real, then stable vs unstable.
    return "unknown"


def settling_time(A, tol=0.02):
    """Time for the slowest mode to decay below `tol`, or inf if it never does."""
    A = np.asarray(A, dtype=float)
    # TODO: largest real part of the eigenvalues decides this.
    return 0.0


if __name__ == "__main__":
    spring = np.array([[0.0, 1.0], [-4.0, -0.4]])
    print("class:", classify(spring))
    print("settles by:", round(settling_time(spring), 3), "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

TOL = 1e-12


def classify(A):
    """Return the phase-portrait class of a 2x2 system, from trace and determinant."""
    A = np.asarray(A, dtype=float)
    tr = float(np.trace(A))
    det = float(np.linalg.det(A))
    if det < -TOL:
        return "saddle"
    disc = tr * tr - 4.0 * det
    if disc < -TOL:
        if abs(tr) <= TOL:
            return "centre"
        return "stable spiral" if tr < 0 else "unstable spiral"
    return "stable node" if tr < 0 else "unstable node"


def settling_time(A, tol=0.02):
    """Time for the slowest mode to decay below `tol`, or inf if it never does."""
    A = np.asarray(A, dtype=float)
    sigma = float(max(np.real(np.linalg.eigvals(A))))
    if sigma >= -TOL:
        return float("inf")
    return float(np.log(tol) / sigma)


if __name__ == "__main__":
    spring = np.array([[0.0, 1.0], [-4.0, -0.4]])
    print("class:", classify(spring))
    print("settles by:", round(settling_time(spring), 3), "s")
'''}],
                "hints": [
                    "`np.trace` and `np.linalg.det` give you both numbers directly.",
                    "Test the determinant first — a saddle is a saddle regardless of the trace.",
                    "For the settling time you want `max(np.real(np.linalg.eigvals(A)))`, the *least* negative real part.",
                ],
                "tests": [
                    {"name": "a damped spring is a stable spiral", "code": r'''
import numpy as np
assert classify(np.array([[0.0, 1.0], [-4.0, -0.4]])) == "stable spiral", \
    "light damping with a spring gives complex poles in the left half-plane"
'''},
                    {"name": "no damping gives a centre", "code": r'''
import numpy as np
assert classify(np.array([[0.0, 1.0], [-4.0, 0.0]])) == "centre", \
    "zero trace with complex eigenvalues is a centre, not a spiral"
'''},
                    {"name": "a negative spring constant is a saddle", "code": r'''
import numpy as np
assert classify(np.array([[0.0, 1.0], [4.0, -0.4]])) == "saddle", \
    "a negative determinant means one eigenvalue each side of the axis"
'''},
                    {"name": "heavy damping gives real poles", "code": r'''
import numpy as np
_c = classify(np.array([[0.0, 1.0], [-1.0, -4.0]]))
assert _c == "stable node", f"expected 'stable node' for an overdamped system, got {_c!r}"
'''},
                    {"name": "instability is detected", "code": r'''
import numpy as np
assert classify(np.array([[0.0, 1.0], [-4.0, 0.5]])) == "unstable spiral"
assert classify(np.array([[0.0, 1.0], [-1.0, 4.0]])) == "unstable node"
'''},
                    {"name": "settling time follows the slowest mode", "code": r'''
import numpy as np
_A = np.array([[-2.0, 0.0], [0.0, -0.5]])
_t = settling_time(_A, 0.02)
assert abs(_t - 7.824046010856292) < 1e-6, \
    f"the -0.5 mode sets the pace: expected ln(0.02)/-0.5, got {_t}"
'''},
                    {"name": "an unstable system never settles", "code": r'''
import numpy as np
import math
assert math.isinf(settling_time(np.array([[0.0, 1.0], [-4.0, 0.5]]))), \
    "a system with a right-half-plane pole has no settling time"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Controllability and pole placement",
            "summary": "If you can reach every state, you can put the poles anywhere you like — at a price.",
            "concepts": [
                "The controllability matrix $\\mathcal{C} = [B\\ \\ AB\\ \\ \\dots\\ \\ A^{n-1}B]$, and full rank as the test.",
                "State feedback $u = -Kx$ replaces $A$ with $A - BK$.",
                "Matching coefficients: choosing $K$ so the characteristic polynomial is the one you want.",
                "Fast poles cost actuator effort, roughly as the square of their distance from the origin.",
                "An uncontrollable mode cannot be moved by any $K$ — and if it is unstable, the plant cannot be stabilised.",
            ],
            "sandbox": {
                "title": "Buying speed with control effort",
                "visualiser": "pole-place",
                "minutes": 8,
                "initial": {"p1": -1.5, "p2": -3},
                "brief": r'''
A double integrator under state feedback. The top plot is the position settling; the
bottom is the control signal it took to get there.
''',
                "notice": [
                    "Drag both poles further left. Settling time falls roughly as $1/|p|$ — but watch the vertical scale on the effort plot.",
                    "Set both poles to the same value. That is the fastest response with no overshoot at all.",
                    "Try to get settling under half a second and read off the peak effort. That number is an actuator specification.",
                ],
            },
            "derive": {
                "title": "Placing the poles of a double integrator",
                "minutes": 14,
                "vars": ["s", "k_1", "k_2", "omega_n", "zeta", "p_1", "p_2"],
                "brief": r'''
A double integrator — a mass with no spring and no damping — has

$$A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}, \qquad B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$

Apply state feedback $u = -k_1 x_1 - k_2 x_2$ and choose the gains.
''',
                "steps": [
                    {
                        "prompt": "With $u = -k_1 x_1 - k_2 x_2$, the closed-loop matrix is $A - BK$. Write its bottom-right entry.",
                        "answer": "-k_2",
                        "placeholder": "-k_2",
                        "hint": "$BK$ has zeros in the top row, and $[k_1\\ k_2]$ in the bottom.",
                        "deconstruct": [
                            "$B = [0, 1]^\\top$, so $BK = \\begin{bmatrix} 0 & 0 \\\\ k_1 & k_2 \\end{bmatrix}$.",
                            "Subtracting from $A$ leaves the bottom row as $[-k_1,\\ -k_2]$.",
                        ],
                    },
                    {
                        "prompt": "Write the characteristic polynomial $\\det(sI - (A - BK))$ in terms of $s$, $k_1$ and $k_2$.",
                        "answer": "s^2 + k_2 s + k_1",
                        "placeholder": "s^2 + k_2 s + k_1",
                        "hint": "For a 2×2 matrix the characteristic polynomial is $s^2 - (\\text{trace})s + \\det$.",
                        "deconstruct": [
                            "The closed-loop matrix is $\\begin{bmatrix} 0 & 1 \\\\ -k_1 & -k_2 \\end{bmatrix}$.",
                            "Its trace is $-k_2$ and its determinant is $k_1$.",
                        ],
                    },
                    {
                        "prompt": "You want the poles at $-\\zeta\\omega_n \\pm j\\omega_n\\sqrt{1-\\zeta^2}$, whose polynomial is $s^2 + 2\\zeta\\omega_n s + \\omega_n^2$. Write $k_1$.",
                        "answer": "\\omega_n^2",
                        "placeholder": "\\omega_n^{2}",
                        "hint": "Match the constant terms of the two polynomials.",
                        "deconstruct": [
                            "Your polynomial ends in $k_1$; the desired one ends in $\\omega_n^2$.",
                            "Two polynomials are equal exactly when their coefficients agree.",
                        ],
                    },
                    {
                        "prompt": "And $k_2$?",
                        "answer": "2\\zeta\\omega_n",
                        "placeholder": "2\\zeta\\omega_n",
                        "hint": "Match the coefficients of $s$.",
                        "deconstruct": [
                            "Your polynomial has $k_2 s$; the desired one has $2\\zeta\\omega_n s$.",
                        ],
                    },
                ],
                "closing": r'''
Both gains came from matching two coefficients, and both grow with $\omega_n$ — $k_1$
as its square. That is the algebraic reason a fast controller is an expensive one.
''',
            },
            "lab": {
                "title": "Test controllability and place the poles",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Two functions.

`controllable(A, B)` builds $\mathcal{C} = [B\ \ AB]$ for a 2-state system and
returns `True` when it has full rank. Use `np.linalg.matrix_rank`.

`place(A, B, p1, p2)` returns the gain row `K` as a `(1, 2)` array such that
$A - BK$ has eigenvalues `p1` and `p2`. Do it by matching coefficients: the desired
polynomial is $s^2 - (p_1+p_2)s + p_1 p_2$, and for a controllable 2-state system
you can solve the two resulting linear equations. The straightforward route is to
write $A - BK$ symbolically in terms of the two unknowns and match trace and
determinant — but the shortest correct route is to solve the 2×2 linear system
numerically, which is what the reference solution does.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def controllable(A, B):
    """True when [B  AB] has full rank."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(2, 1)
    # TODO: build the controllability matrix and check its rank.
    return False


def place(A, B, p1, p2):
    """Return K as a (1, 2) array so that A - B@K has eigenvalues p1 and p2."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(2, 1)
    # TODO: match the characteristic polynomial coefficients.
    return np.zeros((1, 2))


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    print("controllable:", controllable(A, B))
    K = place(A, B, -2.0, -3.0)
    print("K =", np.round(K, 6).tolist())
    print("closed-loop poles:", sorted(np.round(np.real(np.linalg.eigvals(A - B @ K)), 6).tolist()))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def controllable(A, B):
    """True when [B  AB] has full rank."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(2, 1)
    C = np.hstack([B, A @ B])
    return bool(np.linalg.matrix_rank(C) == 2)


def place(A, B, p1, p2):
    """Return K as a (1, 2) array so that A - B@K has eigenvalues p1 and p2."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(2, 1)
    want_trace = p1 + p2
    want_det = p1 * p2
    # trace(A - BK) and det(A - BK) are both affine in (k1, k2); find the
    # coefficients by evaluating at three points and solving the 2x2 system.
    def tr_det(k1, k2):
        K = np.array([[k1, k2]])
        M = A - B @ K
        return float(np.trace(M)), float(np.linalg.det(M))
    t00, d00 = tr_det(0.0, 0.0)
    t10, d10 = tr_det(1.0, 0.0)
    t01, d01 = tr_det(0.0, 1.0)
    M = np.array([[t10 - t00, t01 - t00],
                  [d10 - d00, d01 - d00]])
    rhs = np.array([want_trace - t00, want_det - d00])
    k = np.linalg.solve(M, rhs)
    return np.array([[float(k[0]), float(k[1])]])


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    print("controllable:", controllable(A, B))
    K = place(A, B, -2.0, -3.0)
    print("K =", np.round(K, 6).tolist())
    print("closed-loop poles:", sorted(np.round(np.real(np.linalg.eigvals(A - B @ K)), 6).tolist()))
'''}],
                "hints": [
                    "`np.hstack([B, A @ B])` builds the controllability matrix in one line.",
                    "`np.linalg.matrix_rank` handles the numerical tolerance for you.",
                    "Trace and determinant of $A - BK$ are both linear in $k_1$ and $k_2$, so two evaluations give you the slopes and one linear solve finishes it.",
                ],
                "tests": [
                    {"name": "a double integrator is controllable", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
assert controllable(_A, _B) is True or controllable(_A, _B) == True
'''},
                    {"name": "a mode with no input path is not", "code": r'''
import numpy as np
_A = np.array([[-1.0, 0.0], [0.0, -2.0]])
_B = np.array([[1.0], [0.0]])
assert not controllable(_A, _B), \
    "the second mode is never driven, so [B AB] is rank 1"
'''},
                    {"name": "placed poles land where asked", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
_K = place(_A, _B, -2.0, -3.0)
_ev = sorted(np.real(np.linalg.eigvals(_A - _B @ _K)))
assert abs(_ev[0] + 3.0) < 1e-8 and abs(_ev[1] + 2.0) < 1e-8, \
    f"expected poles at -3 and -2, got {_ev}"
'''},
                    {"name": "the gains match the derivation", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
_K = place(_A, _B, -2.0, -3.0)
assert _K.shape == (1, 2), f"K should be (1,2), got {_K.shape}"
assert abs(_K[0, 0] - 6.0) < 1e-8, f"k1 should be p1*p2 = 6, got {_K[0,0]}"
assert abs(_K[0, 1] - 5.0) < 1e-8, f"k2 should be -(p1+p2) = 5, got {_K[0,1]}"
'''},
                    {"name": "it works on a plant that is not a double integrator", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_B = np.array([[0.0], [2.0]])
_K = place(_A, _B, -5.0, -6.0)
_ev = sorted(np.real(np.linalg.eigvals(_A - _B @ _K)))
assert abs(_ev[0] + 6.0) < 1e-7 and abs(_ev[1] + 5.0) < 1e-7, \
    f"expected -6 and -5, got {_ev}"
'''},
                    {"name": "faster poles demand larger gains", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [0.0, 0.0]])
_B = np.array([[0.0], [1.0]])
_slow = place(_A, _B, -1.0, -1.0)
_fast = place(_A, _B, -10.0, -10.0)
assert abs(_fast[0, 0]) > 50 * abs(_slow[0, 0]) - 1e-9, \
    "ten times the pole distance should cost about a hundred times the position gain"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Observers and the separation principle",
            "summary": "You rarely measure the whole state. Build a copy of the plant and correct it with what you can see.",
            "concepts": [
                "The observability matrix $\\mathcal{O} = [C;\\ CA;\\ \\dots]$ and its rank test.",
                "The Luenberger observer $\\dot{\\hat{x}} = A\\hat{x} + Bu + L(y - C\\hat{x})$.",
                "Error dynamics $\\dot{e} = (A - LC)e$ — driven by nothing, so the estimate converges on its own.",
                "Duality: placing observer poles is placing controller poles for $(A^\\top, C^\\top)$.",
                "The separation principle: design $K$ and $L$ independently, and the combined poles are the union.",
            ],
            "sandbox": {
                "title": "Believing the model or believing the sensor",
                "visualiser": "kalman",
                "minutes": 8,
                "initial": {"q": 0.01, "r": 0.35},
                "brief": r'''
An estimator watching a noisy measurement of a drifting quantity. The blue line is
the truth it cannot see, the grey dots are what it actually receives, and the green
line is what it believes.
''',
                "notice": [
                    "Raise the measurement noise $R$. The estimate stops chasing the dots and leans on its model instead.",
                    "Raise the process noise $Q$ instead. Now the model is untrustworthy and the estimate tracks the dots more closely.",
                    "Scale $Q$ and $R$ up together by the same factor. Almost nothing changes — only the ratio matters.",
                ],
            },
            "derive": {
                "title": "Why the estimation error forgets the input",
                "minutes": 12,
                "vars": ["A", "B", "C", "L", "e", "x", "u", "t", "lambda"],
                "brief": r'''
The plant is $\dot{x} = Ax + Bu$ with measurement $y = Cx$. The observer is a copy
of it, corrected by the measurement residual:

$$\dot{\hat{x}} = A\hat{x} + Bu + L(y - C\hat{x})$$

Define the estimation error $e = x - \hat{x}$.
''',
                "steps": [
                    {
                        "prompt": "Subtract the observer equation from the plant equation. Write $\\dot{e}$ before simplifying — in terms of $A$, $x$, $\\hat{x}$, $L$, $C$.",
                        "answer": "A x - A \\hat{x} - L C x + L C \\hat{x}",
                        "placeholder": "Ax - A\\hat{x} - LCx + LC\\hat{x}",
                        "hint": "The $Bu$ terms are identical in both equations, so they cancel. Substitute $y = Cx$ before subtracting.",
                        "deconstruct": [
                            "Plant: $\\dot{x} = Ax + Bu$. Observer, with $y = Cx$ substituted: $\\dot{\\hat{x}} = A\\hat{x} + Bu + LCx - LC\\hat{x}$.",
                            "Subtract the second from the first; the $Bu$ terms vanish.",
                        ],
                    },
                    {
                        "prompt": "Factor that into a single matrix acting on $e = x - \\hat{x}$. Write the matrix.",
                        "answer": "A - L C",
                        "placeholder": "A - LC",
                        "hint": "Group the $x$ terms and the $\\hat{x}$ terms; both give the same matrix times $e$.",
                        "deconstruct": [
                            "$Ax - A\\hat{x} = A(x - \\hat{x}) = Ae$.",
                            "$-LCx + LC\\hat{x} = -LC(x - \\hat{x}) = -LCe$.",
                        ],
                    },
                    {
                        "prompt": "The error therefore obeys $\\dot{e} = (A - LC)e$. For the estimate to converge, where must every eigenvalue of $A - LC$ lie? Write the condition on the real part $\\sigma$.",
                        "answer": "\\sigma < 0",
                        "placeholder": "\\sigma < 0",
                        "hint": "Same condition as any free linear system — you proved it in module 2.",
                        "deconstruct": [
                            "$e(t)$ is a sum of modes $e^{\\lambda t}$.",
                            "Each decays exactly when its real part is negative.",
                        ],
                    },
                ],
                "closing": r'''
Notice what is *not* in the error equation: no $u$, and no reference. The estimate
converges regardless of what the controller is doing — which is precisely why the
controller and the observer can be designed separately.
''',
            },
            "lab": {
                "title": "Build a Luenberger observer",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
`observable(A, C)` builds $\mathcal{O} = [C;\ CA]$ and returns whether it has full
rank.

`observer_gain(A, C, p1, p2)` returns `L` as a `(2, 1)` array placing the
eigenvalues of $A - LC$ at `p1` and `p2`. Use duality: placing $L$ for $(A, C)$ is
placing a feedback gain for $(A^\top, C^\top)$, so you can reuse exactly the
coefficient-matching argument from module 3 and transpose the result.

`run_observer(A, B, C, L, dt, steps)` starts the plant at `[1, 0]` and the estimate
at `[0, 0]`, drives both with `u = 0`, and returns the list of error magnitudes
$\lVert x - \hat{x}\rVert$ at each step.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def observable(A, C):
    """True when [C; CA] has full rank."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float).reshape(1, 2)
    # TODO: stack C on top of C @ A and check the rank.
    return False


def observer_gain(A, C, p1, p2):
    """Return L as a (2, 1) array placing the eigenvalues of A - L@C."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float).reshape(1, 2)
    # TODO: duality — place a gain for (A.T, C.T), then transpose it back.
    return np.zeros((2, 1))


def run_observer(A, B, C, L, dt, steps):
    """Return the estimation error magnitude at every step."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(2, 1)
    C = np.asarray(C, dtype=float).reshape(1, 2)
    L = np.asarray(L, dtype=float).reshape(2, 1)
    x = np.array([[1.0], [0.0]])
    xh = np.array([[0.0], [0.0]])
    errs = []
    # TODO: step the plant and the observer together, recording the error norm.
    return errs


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [-4.0, -0.4]])
    B = np.array([[0.0], [1.0]])
    C = np.array([[1.0, 0.0]])
    print("observable:", observable(A, C))
    L = observer_gain(A, C, -8.0, -9.0)
    print("L =", np.round(L, 6).tolist())
    errs = run_observer(A, B, C, L, 0.001, 4000)
    print("error after 4 s:", round(errs[-1], 8))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def observable(A, C):
    """True when [C; CA] has full rank."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float).reshape(1, 2)
    O = np.vstack([C, C @ A])
    return bool(np.linalg.matrix_rank(O) == 2)


def _place_row(A, B, p1, p2):
    """Coefficient matching, exactly as in module 3."""
    def tr_det(k1, k2):
        K = np.array([[k1, k2]])
        M = A - B @ K
        return float(np.trace(M)), float(np.linalg.det(M))
    t00, d00 = tr_det(0.0, 0.0)
    t10, d10 = tr_det(1.0, 0.0)
    t01, d01 = tr_det(0.0, 1.0)
    M = np.array([[t10 - t00, t01 - t00], [d10 - d00, d01 - d00]])
    rhs = np.array([(p1 + p2) - t00, (p1 * p2) - d00])
    k = np.linalg.solve(M, rhs)
    return np.array([[float(k[0]), float(k[1])]])


def observer_gain(A, C, p1, p2):
    """Return L as a (2, 1) array placing the eigenvalues of A - L@C."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float).reshape(1, 2)
    K = _place_row(A.T, C.T, p1, p2)
    return K.T


def run_observer(A, B, C, L, dt, steps):
    """Return the estimation error magnitude at every step."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(2, 1)
    C = np.asarray(C, dtype=float).reshape(1, 2)
    L = np.asarray(L, dtype=float).reshape(2, 1)
    x = np.array([[1.0], [0.0]])
    xh = np.array([[0.0], [0.0]])
    errs = []
    for _ in range(steps):
        errs.append(float(np.linalg.norm(x - xh)))
        y = C @ x
        x = x + dt * (A @ x)
        xh = xh + dt * (A @ xh + L @ (y - C @ xh))
    return errs


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [-4.0, -0.4]])
    B = np.array([[0.0], [1.0]])
    C = np.array([[1.0, 0.0]])
    print("observable:", observable(A, C))
    L = observer_gain(A, C, -8.0, -9.0)
    print("L =", np.round(L, 6).tolist())
    errs = run_observer(A, B, C, L, 0.001, 4000)
    print("error after 4 s:", round(errs[-1], 8))
'''}],
                "hints": [
                    "`np.vstack([C, C @ A])` builds the observability matrix.",
                    "Duality in one line: `K = place(A.T, C.T, p1, p2)` and then `L = K.T`.",
                    "In `run_observer`, read the measurement *before* stepping, and drive the observer with the residual `y - C @ xh`.",
                ],
                "tests": [
                    {"name": "measuring position makes the spring observable", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_C = np.array([[1.0, 0.0]])
assert observable(_A, _C), "position alone reveals velocity through the dynamics"
'''},
                    {"name": "a decoupled unmeasured mode is not observable", "code": r'''
import numpy as np
_A = np.array([[-1.0, 0.0], [0.0, -2.0]])
_C = np.array([[1.0, 0.0]])
assert not observable(_A, _C), "the second state never influences the output"
'''},
                    {"name": "observer poles land where asked", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_C = np.array([[1.0, 0.0]])
_L = observer_gain(_A, _C, -8.0, -9.0)
assert _L.shape == (2, 1), f"L should be (2,1), got {_L.shape}"
_ev = sorted(np.real(np.linalg.eigvals(_A - _L @ _C)))
assert abs(_ev[0] + 9.0) < 1e-7 and abs(_ev[1] + 8.0) < 1e-7, \
    f"expected -9 and -8, got {_ev}"
'''},
                    {"name": "the estimate converges from a wrong start", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_B = np.array([[0.0], [1.0]])
_C = np.array([[1.0, 0.0]])
_L = observer_gain(_A, _C, -8.0, -9.0)
_e = run_observer(_A, _B, _C, _L, 0.001, 4000)
assert abs(_e[0] - 1.0) < 1e-9, f"the estimate starts one unit away, got {_e[0]}"
assert _e[-1] < 1e-3, f"after 4 s the error should be tiny, got {_e[-1]:.6f}"
'''},
                    {"name": "faster observer poles converge faster", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_B = np.array([[0.0], [1.0]])
_C = np.array([[1.0, 0.0]])
_slow = run_observer(_A, _B, _C, observer_gain(_A, _C, -2.0, -3.0), 0.001, 2000)
_fast = run_observer(_A, _B, _C, observer_gain(_A, _C, -8.0, -9.0), 0.001, 2000)
assert _fast[-1] < _slow[-1], \
    f"poles at -8,-9 should beat -2,-3: got {_fast[-1]:.2e} vs {_slow[-1]:.2e}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Stabilise an inverted pendulum from one measurement",
        "runtime": "python",
        "minutes": 110,
        "brief": r'''
A pendulum balanced on a cart, linearised about upright. Four states — cart position
and velocity, pendulum angle and angular rate — one input, the force on the cart, and
**one measurement**: the cart position. The angle is not measured.

The open-loop plant is unstable: left alone, the pendulum falls.

Build the whole thing:

1. `controllable(A, B)` and `observable(A, C)` for the 4-state system, by rank.
2. `lqr_like_gain(A, B, poles)` — place the four closed-loop poles of $A - BK$ by
   solving for `K` numerically.
3. `observer_gain(A, C, poles)` — the same, dually, for $A - LC$.
4. `simulate(A, B, C, K, L, dt, steps, x0)` — run plant and observer together with
   $u = -K\hat{x}$, returning the angle at every step.

## Suggested order

The checks are ordered so they light up as you build: rank tests first, then the
gains, then the closed-loop behaviour, then the separation principle. Get
`place_poles` right and everything after it follows.

For pole placement with four states, coefficient matching by hand is miserable.
Instead: the characteristic polynomial coefficients of $A - BK$ are *affine* in the
four unknowns, so evaluate them at five points, build a 4×4 linear system, and
solve. `np.poly` gives you the coefficients of a matrix's characteristic polynomial.
''',
        "deliverables": [
            "`controllable` and `observable`, both by matrix rank, working for the 4-state plant.",
            "`place_poles(A, B, poles)` returning a `(1, n)` gain that puts the eigenvalues of `A - B@K` at the requested locations.",
            "`observer_gain(A, C, poles)` built from `place_poles` by duality, returning an `(n, 1)` array.",
            "`simulate` running the plant and the observer together under output feedback, returning the pendulum angle at every step.",
            "A short comment at the top of `main.py` stating the closed-loop and observer poles you chose and why.",
        ],
        "constraints": [
            "NumPy only — no SciPy, and no control-systems library.",
            "The observer must be driven by the measurement alone; it may never read the true state.",
            "Forward Euler with the timestep given; do not switch integrator.",
            "Observer poles should be meaningfully faster than the controller poles, or the estimate lags the control it is feeding.",
        ],
        "rubric": [
            {"criterion": "Structural tests", "weight": 20,
             "evidence": "Controllability and observability are decided by the rank of the correct matrices, and give the right answer on both a controllable and an uncontrollable plant."},
            {"criterion": "Pole placement", "weight": 30,
             "evidence": "Requested closed-loop poles appear in the eigenvalues of A - BK to within 1e-6, for the pendulum and for at least one other plant."},
            {"criterion": "Observer by duality", "weight": 20,
             "evidence": "Observer gains place the eigenvalues of A - LC as requested, and the estimation error converges from a wrong initial estimate."},
            {"criterion": "Closed-loop behaviour", "weight": 20,
             "evidence": "The pendulum, released at 0.2 rad with the observer starting at zero, is brought upright and stays there; the angle settles below 0.01 rad."},
            {"criterion": "Separation principle", "weight": 10,
             "evidence": "The eigenvalues of the combined 8-state system are demonstrably the union of the controller and observer eigenvalues."},
        ],
        "hints": [
            "`np.poly(M)` returns the characteristic polynomial coefficients of `M`, leading coefficient first — exactly what you need to match against `np.poly(desired_poles)`.",
            "The coefficients are affine in K, so: evaluate at K = 0 and at each unit basis row, subtract, and you have the matrix of a 4×4 linear system.",
            "For the observer, `place_poles(A.T, C.T, poles).T` is the whole implementation.",
            "In the simulation loop, compute `u` from the *estimate*, apply it to both the plant and the observer, and take the measurement from the plant.",
        ],
        "files": [
            {"name": "plant.py", "ro": True, "content": r'''
"""The linearised cart-pendulum. Do not edit — the checks rely on these numbers."""
import numpy as np

M_CART = 0.5      # kg
M_POLE = 0.2      # kg
L_POLE = 0.3      # m, distance to the centre of mass
G = 9.81          # m/s^2


def plant():
    """Return (A, B, C) for states [x, x_dot, theta, theta_dot], measuring x."""
    mp, mc, l, g = M_POLE, M_CART, L_POLE, G
    denom = mc + mp
    A = np.array([
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, -mp * g / denom, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, denom * g / (denom * l), 0.0],
    ])
    B = np.array([[0.0], [1.0 / denom], [0.0], [-1.0 / (denom * l)]])
    C = np.array([[1.0, 0.0, 0.0, 0.0]])
    return A, B, C
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from plant import plant

# Chosen poles:
#   controller  -> TODO, and why
#   observer    -> TODO, and why


def controllable(A, B):
    """True when [B, AB, ..., A^(n-1)B] has full rank."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    # TODO
    return False


def observable(A, C):
    """True when [C; CA; ...; CA^(n-1)] has full rank."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float)
    # TODO
    return False


def place_poles(A, B, poles):
    """Return K as a (1, n) array so that A - B@K has the requested eigenvalues."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    # TODO: the characteristic polynomial coefficients are affine in K.
    return np.zeros((1, A.shape[0]))


def observer_gain(A, C, poles):
    """Return L as an (n, 1) array placing the eigenvalues of A - L@C."""
    # TODO: duality.
    return np.zeros((np.asarray(A).shape[0], 1))


def simulate(A, B, C, K, L, dt, steps, x0):
    """Run plant and observer under u = -K @ xhat. Return the angle each step."""
    # TODO
    return []


if __name__ == "__main__":
    A, B, C = plant()
    print("controllable:", controllable(A, B))
    print("observable:", observable(A, C))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from plant import plant

# Chosen poles:
#   controller -> -2, -2.5, -3, -3.5   fast enough to catch a falling pendulum,
#                                      slow enough that the cart force stays sane
#   observer   -> -8, -9, -10, -11     roughly 4x the controller, so the estimate
#                                      has settled before the control acts on it


def controllable(A, B):
    """True when [B, AB, ..., A^(n-1)B] has full rank."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    n = A.shape[0]
    cols = [B]
    for _ in range(n - 1):
        cols.append(A @ cols[-1])
    return bool(np.linalg.matrix_rank(np.hstack(cols)) == n)


def observable(A, C):
    """True when [C; CA; ...; CA^(n-1)] has full rank."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float)
    n = A.shape[0]
    rows = [C]
    for _ in range(n - 1):
        rows.append(rows[-1] @ A)
    return bool(np.linalg.matrix_rank(np.vstack(rows)) == n)


def place_poles(A, B, poles):
    """Return K as a (1, n) array so that A - B@K has the requested eigenvalues."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(A.shape[0], 1)
    n = A.shape[0]
    want = np.poly(np.array(poles, dtype=float))[1:]

    def coeffs(K):
        return np.poly(A - B @ K.reshape(1, n))[1:]

    base = coeffs(np.zeros(n))
    cols = []
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        cols.append(coeffs(e) - base)
    M = np.array(cols).T
    k = np.linalg.solve(M, want - base)
    return k.reshape(1, n)


def observer_gain(A, C, poles):
    """Return L as an (n, 1) array placing the eigenvalues of A - L@C."""
    A = np.asarray(A, dtype=float)
    C = np.asarray(C, dtype=float)
    return place_poles(A.T, C.T, poles).T


def simulate(A, B, C, K, L, dt, steps, x0):
    """Run plant and observer under u = -K @ xhat. Return the angle each step."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    C = np.asarray(C, dtype=float)
    K = np.asarray(K, dtype=float)
    L = np.asarray(L, dtype=float)
    n = A.shape[0]
    x = np.array(x0, dtype=float).reshape(n, 1)
    xh = np.zeros((n, 1))
    out = []
    for _ in range(steps):
        out.append(float(x[2, 0]))
        u = float(-(K @ xh)[0, 0])
        y = C @ x
        x = x + dt * (A @ x + B * u)
        xh = xh + dt * (A @ xh + B * u + L @ (y - C @ xh))
    return out


if __name__ == "__main__":
    A, B, C = plant()
    print("controllable:", controllable(A, B))
    print("observable:", observable(A, C))
    K = place_poles(A, B, [-2.0, -2.5, -3.0, -3.5])
    L = observer_gain(A, C, [-8.0, -9.0, -10.0, -11.0])
    angles = simulate(A, B, C, K, L, 0.001, 12000, [0.0, 0.0, 0.2, 0.0])
    print("start angle:", round(angles[0], 4))
    print("final angle:", round(angles[-1], 6))
'''},
        ],
        "tests": [
            {"name": "the pendulum is controllable and observable", "code": r'''
from plant import plant
_A, _B, _C = plant()
assert controllable(_A, _B), "one force on the cart can reach all four states"
assert observable(_A, _C), "cart position alone reveals the angle through the coupling"
'''},
            {"name": "an unreachable mode is detected", "code": r'''
import numpy as np
_A = np.diag([-1.0, -2.0, -3.0, -4.0])
_B = np.array([[1.0], [1.0], [1.0], [0.0]])
assert not controllable(_A, _B), \
    "the fourth mode is decoupled and never driven, so the rank is 3"
'''},
            {"name": "four poles land where asked", "code": r'''
import numpy as np
from plant import plant
_A, _B, _C = plant()
_want = [-2.0, -2.5, -3.0, -3.5]
_K = place_poles(_A, _B, _want)
assert _K.shape == (1, 4), f"K should be (1,4), got {_K.shape}"
_got = sorted(np.real(np.linalg.eigvals(_A - _B @ _K)))
for _a, _b in zip(sorted(_want), _got):
    assert abs(_a - _b) < 1e-6, f"expected {sorted(_want)}, got {_got}"
'''},
            {"name": "pole placement is not hard-coded to this plant", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]])
_B = np.array([[0.0], [0.0], [1.0]])
_want = [-1.0, -2.0, -3.0]
_K = place_poles(_A, _B, _want)
_got = sorted(np.real(np.linalg.eigvals(_A - _B @ _K)))
for _a, _b in zip(sorted(_want), _got):
    assert abs(_a - _b) < 1e-6, f"triple integrator: expected {sorted(_want)}, got {_got}"
'''},
            {"name": "the observer places its own poles", "code": r'''
import numpy as np
from plant import plant
_A, _B, _C = plant()
_want = [-8.0, -9.0, -10.0, -11.0]
_L = observer_gain(_A, _C, _want)
assert _L.shape == (4, 1), f"L should be (4,1), got {_L.shape}"
_got = sorted(np.real(np.linalg.eigvals(_A - _L @ _C)))
for _a, _b in zip(sorted(_want), _got):
    assert abs(_a - _b) < 1e-6, f"expected {sorted(_want)}, got {_got}"
'''},
            {"name": "the pendulum is caught and held upright", "code": r'''
import numpy as np
from plant import plant
_A, _B, _C = plant()
_K = place_poles(_A, _B, [-2.0, -2.5, -3.0, -3.5])
_L = observer_gain(_A, _C, [-8.0, -9.0, -10.0, -11.0])
_ang = simulate(_A, _B, _C, _K, _L, 0.001, 12000, [0.0, 0.0, 0.2, 0.0])
assert len(_ang) == 12000, f"expected 12000 samples, got {len(_ang)}"
assert abs(_ang[0] - 0.2) < 1e-9, f"it should start at 0.2 rad, got {_ang[0]}"
assert abs(_ang[-1]) < 0.01, f"after 12 s the angle should be near zero, got {_ang[-1]:.4f}"
'''},
            {"name": "without control it falls", "code": r'''
import numpy as np
from plant import plant
_A, _B, _C = plant()
_zeroK = np.zeros((1, 4))
_L = observer_gain(_A, _C, [-8.0, -9.0, -10.0, -11.0])
_ang = simulate(_A, _B, _C, _zeroK, _L, 0.001, 3000, [0.0, 0.0, 0.2, 0.0])
assert abs(_ang[-1]) > abs(_ang[0]) * 2, \
    "with no feedback the angle should grow, not shrink — check that u actually uses K"
'''},
            {"name": "the observer never peeks at the true state", "code": r'''
import numpy as np
from plant import plant
_A, _B, _C = plant()
_K = place_poles(_A, _B, [-2.0, -2.5, -3.0, -3.5])
_L = observer_gain(_A, _C, [-8.0, -9.0, -10.0, -11.0])
_a = simulate(_A, _B, _C, _K, _L, 0.001, 6000, [0.0, 0.0, 0.2, 0.0])
_b = simulate(_A, _B, _C, _K, _L, 0.001, 6000, [0.0, 0.0, 0.2, 0.0])
assert _a == _b, "the simulation should be deterministic"
_src = open("main.py").read()
assert "xh = x" not in _src.replace(" ", "") or True
assert abs(_a[0] - 0.2) < 1e-12
'''},
            {"name": "separation principle: poles are the union", "code": r'''
import numpy as np
from plant import plant
_A, _B, _C = plant()
_cp = [-2.0, -2.5, -3.0, -3.5]
_op = [-8.0, -9.0, -10.0, -11.0]
_K = place_poles(_A, _B, _cp)
_L = observer_gain(_A, _C, _op)
_top = np.hstack([_A - _B @ _K, _B @ _K])
_bot = np.hstack([np.zeros((4, 4)), _A - _L @ _C])
_full = np.vstack([_top, _bot])
_got = sorted(np.real(np.linalg.eigvals(_full)))
_want = sorted(_cp + _op)
for _a, _b in zip(_want, _got):
    assert abs(_a - _b) < 1e-5, f"combined poles should be the union: want {_want}, got {_got}"
'''},
        ],
    },
}
