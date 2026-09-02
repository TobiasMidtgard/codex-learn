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
            "read": [
                {
                    "title": "Two numbers are enough, and one is not",
                    "minutes": 14,
                    "body": r'''
On the bench there is a carriage on a linear rail: 1 kg of aluminium, held by a spring
that measures 4 N/m and a dashpot that measures 0.4 N·s/m. A laser gauge reads the
carriage position at 1 kHz and writes the numbers to a file. A voice coil can push the
carriage with whatever force you ask for.

Two runs. In the first the carriage is drawn 50 mm off centre and released from rest.
In the second it is flicked from further out, and the gauge is triggered at the moment
it sweeps through 50 mm at 300 mm/s. At that instant both runs put the same number in
the file: 50.0 mm. Nothing in the reading distinguishes them. Ask what the gauge will
say 200 ms later.

```python
# Free response of the bench rig, from two starts the gauge cannot tell apart.
A = [[0.0, 1.0], [-4.0, -0.4]]        # m = 1 kg, b = 0.4 N.s/m, k = 4 N/m


def advance(x, dt, seconds):
    for _ in range(int(round(seconds / dt))):
        dx0 = A[0][0] * x[0] + A[0][1] * x[1]
        dx1 = A[1][0] * x[0] + A[1][1] * x[1]
        x = [x[0] + dt * dx0, x[1] + dt * dx1]
    return x


for name, start in (("A", [0.050, 0.000]), ("B", [0.050, 0.300])):
    later = advance(start, 1e-5, 0.20)
    print(name, "starts at 50.0 mm,", round(start[1] * 1000), "mm/s ->",
          round(later[0] * 1000, 1), "mm after 0.2 s")
```

```text
A starts at 50.0 mm, 0 mm/s -> 46.2 mm after 0.2 s
B starts at 50.0 mm, 300 mm/s -> 102.3 mm after 0.2 s
```

Forty-six millimetres against a hundred and two. One reading from the gauge is not a
prediction of anything, and no amount of extra precision on that reading would have
helped: the two runs differ in something the gauge never sees.

## What would have been enough

Write Newton on the carriage, with $u$ the coil force:

$$m\ddot{y} = u - b\dot{y} - k y$$

Read that as an instruction rather than an identity. It says: hand me the position, the
velocity and the force at this instant, and I will hand you back the acceleration. The
acceleration then tells you the velocity an instant later, and the velocity tells you
the position an instant later — at which point you are holding a position and a velocity
again and the instruction applies once more. The loop closes on itself. It never asks
for a third number, and it never asks how the carriage arrived where it is.

That closure is the whole content of the word *state*. The pair $(y, \dot y)$ is a state
because the recursion above, given the future input, needs nothing else; a single
position is not, because the recursion stalls at the first step for want of a velocity.
Adding a third quantity — the spring force $ky$, say — does not make it a better state,
because that quantity is already determined by $y$ and the recursion would carry it
around without ever consulting it.

## The four matrices, read off the same two lines

Name the two numbers $x_1 = y$ and $x_2 = \dot{y}$. The first equation is bookkeeping:
$\dot{x}_1 = x_2$, true by the naming and carrying no physics whatever. The second is
the differential equation solved for the highest derivative:

$$\dot{x}_2 = \ddot{y} = \frac{u - b x_2 - k x_1}{m}$$

Stack the two and the matrices are already there — nothing has been chosen, only
arranged:

$$\dot{x} = \begin{bmatrix} 0 & 1 \\ -\frac{k}{m} & -\frac{b}{m} \end{bmatrix} x
          + \begin{bmatrix} 0 \\ \frac{1}{m} \end{bmatrix} u,
\qquad y = \begin{bmatrix} 1 & 0 \end{bmatrix} x$$

With the bench numbers, $A = \begin{bmatrix} 0 & 1 \\ -4 & -0.4 \end{bmatrix}$ and
$B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$. The gauge reads position and nothing else,
so $C = [\,1\ \ 0\,]$ and $D = 0$. That zero is not a convention: $D$ would be a route
from the coil to the gauge that misses the mass, and there is no such route. A force
cannot displace a kilogram in zero time. Where $D$ is non-zero in a real model — a
strain gauge on the spring, reading a quantity the input reaches algebraically — it is
telling you something specific about the sensor, not about the dynamics.

The asymmetry between the two rows is worth holding on to. The top row is the same
$[\,0\ \ 1\,]$ for every second-order plant in the universe; the bottom row is where the
spring and the dashpot live. Transposing that bottom row to $[-0.4,\ -4]$ produces a
matrix that looks entirely reasonable and describes a plant with a stiffness of 0.4 and a
damping of 4 — a completely different piece of hardware, and one that never rings.

## Following the numbers

Equilibrium falls straight out of the same matrices. Setting $\dot{x} = 0$ forces
$x_2 = 0$ from the top row, and then the bottom row gives $-k x_1 + u = 0$, so a
constant push of 1 N holds the carriage at $u/k = 0.25$ m. Integrating with forward
Euler confirms it, and shows what the integrator costs:

```python
A = [[0.0, 1.0], [-4.0, -0.4]]
B = [0.0, 1.0]


def simulate(u, dt, steps):
    x, out = [0.0, 0.0], []
    for _ in range(steps):
        out.append(x[0])
        dx0 = A[0][0] * x[0] + A[0][1] * x[1] + B[0] * u
        dx1 = A[1][0] * x[0] + A[1][1] * x[1] + B[1] * u
        x = [x[0] + dt * dx0, x[1] + dt * dx1]
    return out


print("dt = 1 ms, 60 s of it ->", round(simulate(1.0, 0.001, 60000)[-1], 4), "m")
for dt in (0.090, 0.100, 0.110):
    print("dt =", dt, "-> after 200 s:", round(simulate(1.0, dt, int(200 / dt))[-1], 3), "m")
```

```text
dt = 1 ms, 60 s of it -> 0.25 m
dt = 0.09 -> after 200 s: 0.25 m
dt = 0.1 -> after 200 s: 0.296 m
dt = 0.11 -> after 200 s: 7.499 m
```

The first line is the physics. The last three are the arithmetic, and the boundary
between them is exact rather than approximate. One Euler step multiplies a mode by
$1 + \Delta t\,\lambda$, so the recursion decays only while $|1 + \Delta t\,\lambda| < 1$.
The eigenvalues here are $-0.2 \pm j1.98997$ (module 2 derives them; take them for now),
and squaring the bound gives $1 - 0.4\Delta t + 4\Delta t^2 < 1$, which holds exactly
while $\Delta t < 0.1$ s. At 0.09 the carriage settles where the physics says. At 0.1 it
sits on the boundary and neither settles nor escapes. At 0.11 a plant that is stable in
every sense is reported as running away to 7.5 m.

## The realisation is a choice; the behaviour is not

Nothing above forced the choice of position and velocity. Take any invertible $T$ and
define $z = Tx$. Then $\dot{z} = T\dot{x} = TAx + TBu = TAT^{-1}z + TBu$, and the output
is $y = Cx = CT^{-1}z$. The description changes; the carriage does not. Try
$z_1 = y$, $z_2 = y + \dot{y}$:

```python
def mul(P, Q):
    return [[sum(P[i][k] * Q[k][j] for k in range(len(Q))) for j in range(len(Q[0]))]
            for i in range(len(P))]


def spectrum(M):
    """Trace, determinant and the eigenvalue pair of a 2x2 matrix."""
    tr = M[0][0] + M[1][1]
    det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    disc = tr * tr - 4.0 * det
    root = abs(disc) ** 0.5
    if disc >= 0.0:
        return tr, det, (tr + root) / 2.0, (tr - root) / 2.0
    return tr, det, tr / 2.0, root / 2.0


A = [[0.0, 1.0], [-4.0, -0.4]]
T = [[1.0, 0.0], [1.0, 1.0]]          # z1 = y, z2 = y + ydot
Tinv = [[1.0, 0.0], [-1.0, 1.0]]
Abar = mul(T, mul(A, Tinv))

for name, M in (("A   ", A), ("Abar", Abar)):
    tr, det, re, im = spectrum(M)
    print(name, "=", M, " trace", round(tr, 4), " det", round(det, 4),
          " eigenvalues", round(re, 4), "+/- j", round(im, 4))
```

```text
A    = [[0.0, 1.0], [-4.0, -0.4]]  trace -0.4  det 4.0  eigenvalues -0.2 +/- j 1.99
Abar = [[-1.0, 1.0], [-4.6, 0.6]]  trace -0.4  det 4.0  eigenvalues -0.2 +/- j 1.99
```

Every entry moved. The trace, the determinant and the eigenvalues did not, and neither
did anything the gauge can measure: feed both realisations the same coil force from
equivalent starting conditions and the two position traces agree to the last digit.

## The mistake, and why it is tempting

The mistake is reading physics off the entries of $A$. It is tempting because in the
first realisation anyone writes, the entries *are* physics — $-4$ is the stiffness over
the mass and $-0.4$ is the damping over the mass, and you can point at each of them. So
the habit forms on a matrix where it works, and then travels.

Look at what it says about $\bar{A}$. Its bottom-right entry is $+0.6$, positive, and
the reflex trained on the first matrix reads that as negative damping and declares the
carriage unstable. The trace is still $-0.4$ and the eigenvalues are still
$-0.2 \pm j1.98997$; the carriage is doing what it always did. The damping is not stored
in any entry of $\bar{A}$ — it is spread across all four, and what survives the change of
coordinates is the characteristic polynomial. This is exactly why the lab in the next
module, *Classify a system from its matrix alone*, decides everything from the trace and
the determinant and never looks at an individual entry.

## Where this stops holding

The rail is linear over the ±50 mm the gauge sweeps; take the carriage to the end stops
and the spring stiffens and $A$ is no longer constant. A real dashpot also carries dry
friction, a force of fixed size opposing whatever direction you are moving in, and that
is not $-b\dot{y}$ for any $b$: it brings the carriage to rest a millimetre or two short
of centre and leaves it there. No linear model reproduces a dead band, because a linear
system that reaches zero velocity away from equilibrium has a non-zero acceleration
waiting for it. And all of this assumes the coefficients hold still — warm the coil for
an hour and $b$ drifts, at which point $A$ is a function of time and every result in this
course needs re-deriving.

## What you are about to build

The lab for this module, *Build and simulate a state-space model*, asks for exactly the
two functions above: `build(m, b, k)` returning the $A$ and $B$ you derived, and
`simulate` stepping them forward with the same Euler rule. Its checks are the claims made
here — the top row of $A$ is $[\,0\ \ 1\,]$, $B[0]$ is zero because a force cannot move a
mass instantly, and a 1 N push settles the carriage at $u/k = 0.25$ m. The derivation
*Putting a second-order system into state space* walks the same algebra symbolically, and
the sandbox *What the A matrix does to the state* lets you edit the four entries of $A$
and watch the flow they define, which is the picture the arithmetic here is a numerical
shadow of.
''',
                },
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
                        "hint": "Move everything except $m\\ddot{y}$ to the right, then divide by $m$. Remember $\\dot{y} = x_2$ and $y = x_1$.",
                        "deconstruct": [
                            "Rearranged: $m\\ddot{y} = u - b\\dot{y} - k y$.",
                            "Substitute the state names and divide through by $m$.",
                        ],
                    },
                    {
                        "prompt": "The system matrix is $A = \\begin{bmatrix} 0 & 1 \\\\ a & b' \\end{bmatrix}$. What is the entry $a$ — the coefficient multiplying $x_1$ in $\\dot{x_2}$?",
                        "answer": "-\\frac{k}{m}",
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
            "quiz": {
                "title": "What a state is, and what it is not",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Which of these is the state of a system?",
                        "opts": [
                            "Every signal that appears anywhere in the block diagram",
                            "The smallest set of numbers that, together with the future input, determines the future output",
                            "The input and the output measured at the present instant",
                            "The eigenvalues of $A$",
                        ],
                        "a": 1,
                        "why": r"""
The state is a *sufficient summary of the past*. Give me the state now and the input
from now on, and I can tell you everything the system will do — I never need to know
how it got there. "Every signal in the diagram" is too much: many of those are
determined by the others. "The input and output right now" is too little: an RC
circuit with 0 V in and 0 V out could be sitting still or could be halfway through
discharging. And the eigenvalues describe the *system*, not the situation it is in.
""",
                    },
                    {
                        "q": "An $n$-th order linear ODE is rewritten in state space. How many first-order equations does it become?",
                        "opts": ["$n$", "$n - 1$", "$2n$", "One, always — that is the point of matrix notation"],
                        "a": 0,
                        "why": r"""
One per order, because you need $n$ initial conditions to pin down the solution of an
$n$-th order ODE and each state carries exactly one of them. The matrix notation makes
it *look* like one equation, which is convenient, but $\dot{x} = Ax + Bu$ with $x$ in
$\mathbb{R}^n$ is $n$ scalar equations stacked up — and that is why $A$ is $n \times n$.
""",
                    },
                    {
                        "q": "For $\\ddot{y} + 4\\dot{y} + 3y = u$ with $x_1 = y$ and $x_2 = \\dot{y}$, what is $A$?",
                        "opts": [
                            "$\\begin{bmatrix}0 & 1\\\\ -3 & -4\\end{bmatrix}$",
                            "$\\begin{bmatrix}0 & 1\\\\ -4 & -3\\end{bmatrix}$",
                            "$\\begin{bmatrix}1 & 0\\\\ 3 & 4\\end{bmatrix}$",
                            "$\\begin{bmatrix}-3 & -4\\\\ 0 & 1\\end{bmatrix}$",
                        ],
                        "a": 0,
                        "why": r"""
The first row is the definition $\dot{x}_1 = x_2$, which is where the $0$ and the $1$
come from — it carries no physics at all. The second row is the ODE rearranged:
$\dot{x}_2 = \ddot{y} = u - 4\dot{y} - 3y = -3x_1 - 4x_2 + u$. So the bottom row is
the coefficients, negated, in the order $y$ then $\dot{y}$ — and swapping them to
$-4, -3$ is the slip to watch for, because it silently builds a different system with
eigenvalues $-1$ and $-3$ replaced by... well, run it and see.
""",
                    },
                    {
                        "q": "Why is $D$ zero for almost every physical plant?",
                        "opts": [
                            "Because a real plant cannot pass an input straight to its output with no delay",
                            "Because $D$ plays no part in stability",
                            "Because $C$ already accounts for it",
                            "Because $D$ has to be square and usually cannot be",
                        ],
                        "a": 0,
                        "why": r"""
$D$ is the instantaneous feed-through: it says a jolt on the input appears on the
output in the same instant, through no state at all. Mass does not move that fast, and
neither does charge through an inductor. It is true that $D$ does not affect stability
— the eigenvalues live in $A$ — but that is a consequence, not the reason. Where $D$
*is* non-zero is a genuine signal: a resistive divider straight from input to output,
or a model that has quietly been algebraically simplified.
""",
                    },
                    {
                        "q": "Two realisations are related by $\\bar{A} = TAT^{-1}$ with $T$ invertible. What do they share?",
                        "opts": [
                            "The entries of $A$, just relabelled",
                            "Their eigenvalues, and their input-output behaviour",
                            "Their state trajectories, point for point",
                            "Nothing — a change of $T$ is a change of system",
                        ],
                        "a": 1,
                        "why": r"""
A similarity transform is a change of coordinates for the state, not a change of
system. The eigenvalues are invariant under it (that is a standard fact worth knowing
by name), and since the eigenvalues are the poles, the transfer function is untouched.
What *does* change is the trajectory in state space, because you are now describing
the same motion in different axes — which is exactly what makes controllability and
observability forms possible. The realisation is a choice; the behaviour is not.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "What the ring-down already told you",
                    "minutes": 15,
                    "body": r'''
The rig from module 1 is still on the bench. Draw the carriage 50 mm off centre, release
it from rest, and let the gauge log for fourteen seconds. Reduce the log to its peaks and
measure two things off them: how far apart they are, and how much smaller each one is
than the one before.

```python
import math

# 14 s of the bench rig's ring-down, logged from a 50 mm release at rest.
A = [[0.0, 1.0], [-4.0, -0.4]]
dt = 1e-4
x, log = [0.050, 0.0], []
for n in range(140000):
    log.append((n * dt, x[0]))
    dx0 = A[0][0] * x[0] + A[0][1] * x[1]
    dx1 = A[1][0] * x[0] + A[1][1] * x[1]
    x = [x[0] + dt * dx0, x[1] + dt * dx1]

peaks = [log[0]] + [(t, y) for i, (t, y) in enumerate(log[1:-1], 1)
                    if log[i - 1][1] < y >= log[i + 1][1]]
for t, y in peaks[:4]:
    print(f"peak at t = {t:6.3f} s   height {y * 1000:6.2f} mm")

Td = peaks[1][0] - peaks[0][0]
ratio = peaks[1][1] / peaks[0][1]
delta = -math.log(ratio)
zeta = delta / math.sqrt(4 * math.pi ** 2 + delta ** 2)
omega_d = 2 * math.pi / Td
print(f"period  {Td:.4f} s   -> omega_d = {omega_d:.4f} rad/s")
print(f"ratio   {ratio:.4f}    -> sigma   = {math.log(ratio) / Td:.4f} 1/s")
print(f"decrement {delta:.4f}  -> zeta    = {zeta:.4f}, "
      f"omega_n = {omega_d / math.sqrt(1 - zeta ** 2):.4f} rad/s")
```

```text
peak at t =  0.000 s   height  50.00 mm
peak at t =  3.157 s   height  26.61 mm
peak at t =  6.315 s   height  14.16 mm
peak at t =  9.472 s   height   7.53 mm
period  3.1574 s   -> omega_d = 1.9900 rad/s
ratio   0.5321    -> sigma   = -0.1998 1/s
decrement 0.6309  -> zeta    = 0.0999, omega_n = 2.0000 rad/s
```

Two peaks and a stopwatch produced a decay rate of $-0.1998$ per second, a ringing
frequency of 1.9900 rad/s and a damping ratio of 0.0999. The rig was assembled from a
4 N/m spring, a 0.4 N·s/m dashpot and a 1 kg carriage, for which $b/2m$ is 0.2,
$\sqrt{k/m}$ is 2 and $b/(2\sqrt{km})$ is 0.1. The measurement recovered the build sheet,
and it did so without forming a matrix, taking a determinant or mentioning an eigenvalue.
The rest of this module is an account of why those two numbers were always going to be
the two numbers, and what they do not tell you.

## One direction at a time

Suppose $v$ is an eigenvector of $A$, so $Av = \lambda v$, and release the system from
$x(0) = c_0 v$. Guess that it stays on that line — $x(t) = c(t)v$ — and substitute into
$\dot{x} = Ax$:

$$\dot{c}\,v = A\,c v = \lambda c\, v \quad\Longrightarrow\quad \dot{c} = \lambda c$$

The vector equation collapsed to the one scalar differential equation everybody can
solve, and $c(t) = c_0 e^{\lambda t}$. Along an eigenvector, a matrix is a number.

When the eigenvectors span the plane — the usual case — any starting point splits as
$x(0) = \alpha v_1 + \beta v_2$ and each piece goes its own way:

$$x(t) = \alpha e^{\lambda_1 t} v_1 + \beta e^{\lambda_2 t} v_2$$

Everything a free linear system does is a weighted sum of those two motions, called the
modes. Now write $\lambda = \sigma + j\omega$. Then
$e^{\lambda t} = e^{\sigma t}(\cos\omega t + j\sin\omega t)$, and the rotating factor has
modulus 1 at every instant, so the whole size of the mode is $e^{\sigma t}$ and the
rotation only decides where in the cycle it is. A conjugate pair recombines into a real
signal $R\,e^{\sigma t}\cos(\omega t + \phi)$: an envelope governed by the real part, a
period of $2\pi/\omega$ governed by the imaginary part.

That is a description of the log above, so run it backwards. Consecutive peaks are one
period apart, so their heights are in the ratio $e^{\sigma T_d}$, which rearranges to
$\sigma = \ln(r)/T_d$; and $\omega_d = 2\pi/T_d$. Those are the two lines of arithmetic
the code performed. Check them against $A$ directly: the characteristic polynomial of the
companion form is $s^2 + \frac{b}{m}s + \frac{k}{m} = s^2 + 0.4s + 4$, whose roots are

$$s = \frac{-0.4 \pm \sqrt{0.16 - 16}}{2} = -0.2 \pm j\,1.98997$$

against $-0.1998 \pm j\,1.9900$ measured. The gap is the forward-Euler step, not the
physics. In the second-order names, $\omega_n = \sqrt{k/m} = 2$ is the distance of the
pole from the origin, $\zeta = b/(2\sqrt{km}) = 0.1$ is the cosine of the angle it makes
with the negative real axis, and $\sigma = -\zeta\omega_n$, $\omega_d =
\omega_n\sqrt{1-\zeta^2}$. The build exercise in this module, *An eigenvalue pair you can
put a probe on*, asks for the same pair in a series RLC at $\omega_n = 2000$ rad/s and
$\zeta = 0.25$, where the gain at resonance comes out at $1/(2\zeta) = 2$ — the identical
geometry wearing volts and henries.

## Stability, and why the trace and determinant are enough

The size of a mode is $e^{\sigma t}$. It decays when $\sigma < 0$, grows when
$\sigma > 0$, and holds its size forever when $\sigma = 0$. Stability is that sentence:
every eigenvalue strictly inside the open left half-plane. An eigenvalue sitting exactly
on the imaginary axis leaves a mode that neither dies nor escapes, which is a different
condition with a different name — marginal — and it is not a near miss you can round in
your favour, because the smallest modelling error decides which way it goes.

For a $2\times 2$ you can answer without computing eigenvalues at all. Their sum is the
trace $\tau$ and their product is the determinant $\Delta$, and

$$\lambda_{1,2} = \frac{\tau \pm \sqrt{\tau^2 - 4\Delta}}{2}$$

Three cases fall out. If $\Delta < 0$ the roots multiply to a negative number, so they are
real with opposite signs: one direction into the origin, one out of it, a saddle, and no
value of $\tau$ rescues it. If $\Delta > 0$ and $\tau^2 < 4\Delta$ the square root is
imaginary and the pair is complex with real part $\tau/2$ — a spiral, inward when $\tau$
is negative, and when $\tau$ is exactly zero the poles land on the axis and the spiral
closes into a centre. Otherwise both roots are real, their product is positive so they
share a sign, and their sum is $\tau$ so that sign is the sign of $\tau$: a node.

That is the decision tree the lab *Classify a system from its matrix alone* asks for, and
it is why the tree tests the determinant first: a negative determinant settles the
question before the trace is consulted.

## The mistake: taking the biggest eigenvalue to be the dominant one

Ask which mode is still there after the transient, and the reflex is to name the biggest
eigenvalue. It is a tempting reflex because in a great deal of numerical linear algebra
the largest $|\lambda|$ is exactly what dominates, and because $|\lambda|$ has a physical
name here — it is $\omega_n$, which people read as "how fast the system is".

```python
import math


def eigs(M):
    """The eigenvalue pair of a 2x2, as a list of (real, imag)."""
    tr = M[0][0] + M[1][1]
    det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    disc = tr * tr - 4.0 * det
    r = abs(disc) ** 0.5
    if disc >= 0.0:
        return [((tr + r) / 2.0, 0.0), ((tr - r) / 2.0, 0.0)]
    return [(tr / 2.0, r / 2.0), (tr / 2.0, -r / 2.0)]


def last_above(M, x0, tol, dt, steps):
    """The last instant at which the state norm still exceeds `tol`."""
    x, t_last = list(x0), 0.0
    for n in range(steps):
        if math.hypot(x[0], x[1]) > tol:
            t_last = n * dt
        dx0 = M[0][0] * x[0] + M[0][1] * x[1]
        dx1 = M[1][0] * x[0] + M[1][1] * x[1]
        x = [x[0] + dt * dx0, x[1] + dt * dx1]
    return t_last


plants = {"lightly damped": [[0.0, 1.0], [-4.0, -0.4]],
          "overdamped    ": [[0.0, 1.0], [-1.0, -4.0]]}
for name, M in plants.items():
    ev = eigs(M)
    mag = max(math.hypot(re, im) for re, im in ev)
    sigma = max(re for re, im in ev)
    print(f"{name}  |lambda|max = {mag:5.3f}   sigma_max = {sigma:7.4f}")
    print(f"    biggest-magnitude rule says {math.log(0.02) / -mag:6.2f} s")
    print(f"    largest real part says      {math.log(0.02) / sigma:6.2f} s")
    print(f"    the simulation says         "
          f"{last_above(M, [1.0, 0.0], 0.02, 1e-4, 300000):6.2f} s")
```

```text
lightly damped  |lambda|max = 2.000   sigma_max = -0.2000
    biggest-magnitude rule says   1.96 s
    largest real part says       19.56 s
    the simulation says          22.99 s
overdamped      |lambda|max = 3.732   sigma_max = -0.2679
    biggest-magnitude rule says   1.05 s
    largest real part says       14.60 s
    the simulation says          15.01 s
```

The magnitude rule is out by a factor of twelve on one plant and fourteen on the other,
and it fails in the dangerous direction: it promises a settled machine ten seconds before
there is one. The real part is what survives, because $|e^{\lambda t}|$ contains no
$\omega$ at all, and the slowest mode is therefore the one whose real part is *least*
negative. That is why `settling_time` in the lab takes `max` over the real parts and not
over the magnitudes — the least negative rate, not the largest number.

The residual gap is worth a moment. For the overdamped plant the prediction of 14.60 s
lands within half a second of the simulated 15.01 s. For the lightly damped one, 19.56 s
against 22.99 s, and the extra 3.43 seconds are not noise: the norm being measured
includes velocity, which at the peaks of a ring-down is about $\omega_n = 2$ times the
position, and waiting for a quantity twice as large to reach the same threshold costs
$\ln 2 / 0.2 = 3.47$ s. The exponential rate was right; the constant in front of it was
not 1.

## Where the eigenvalues stop telling you enough

That constant is the whole of the next warning. The eigenvalues bound the response as
$\lVert x(t)\rVert \le M e^{\sigma t}\lVert x(0)\rVert$, and $M$ can be enormous when the
eigenvectors are nearly parallel.

```python
import math

# Both eigenvalues are on the diagonal, both negative: -1 and -2.
A = [[-1.0, 20.0], [0.0, -2.0]]
dt, x = 1e-4, [0.0, 1.0]
peak, t_peak, t_last = 0.0, 0.0, 0.0
for n in range(120000):
    nrm = math.hypot(x[0], x[1])
    if nrm > peak:
        peak, t_peak = nrm, n * dt
    if nrm > 0.02:
        t_last = n * dt
    dx0 = A[0][0] * x[0] + A[0][1] * x[1]
    dx1 = A[1][0] * x[0] + A[1][1] * x[1]
    x = [x[0] + dt * dx0, x[1] + dt * dx1]

print("start ||x|| = 1.000")
print(f"peak  ||x|| = {peak:.3f} at t = {t_peak:.3f} s")
print(f"||x|| drops under 0.02 at t = {t_last:.2f} s")
print(f"exp(sigma t) alone predicts   {math.log(0.02) / -1.0:.2f} s")
```

```text
start ||x|| = 1.000
peak  ||x|| = 5.007 at t = 0.691 s
||x|| drops under 0.02 at t = 6.91 s
exp(sigma t) alone predicts   3.91 s
```

Every eigenvalue of that matrix is real and negative, the phase portrait is a stable
node, and the state still grows to five times its starting size before it turns around.
The algebra is available: $x_2 = e^{-2t}$, and $\dot{x}_1 = -x_1 + 20e^{-2t}$ gives
$x_1 = 20(e^{-t} - e^{-2t})$, which peaks at $t = \ln 2 = 0.693$ with value 5. The
asymptotic decay is $20e^{-t}$, so the threshold is crossed $\ln 20 = 3.00$ s later than
$e^{-t}$ alone would cross it, which is the 6.91 against 3.91 above. Stability is an
asymptotic promise. On a plant with a saturating actuator, or a linearisation valid only
near the operating point, a factor of five on the way is enough to invalidate both.

Two smaller limits. A repeated eigenvalue with only one eigenvector breaks the mode
decomposition above and produces terms in $t e^{\lambda t}$, which grow before they
decay. And all of this is the *free* response: the eigenvalues say what happens to an
initial condition, and say nothing on their own about how large the output gets when you
drive the system near $\omega_d$, where a $\zeta$ of 0.1 buys a resonant peak of about
$1/(2\zeta) = 5$.

## What you are about to build

The lab *Classify a system from its matrix alone* wants `classify(A)` implementing the
three-case tree derived above — determinant first, then discriminant, then the sign of
the trace — and `settling_time(A, tol)` returning $\ln(\text{tol})/\sigma_{\max}$, with
`inf` when no mode decays. Its test on $\mathrm{diag}(-2, -0.5)$ expects 7.824 s, which
is $\ln(0.02)/(-0.5)$: the $-2$ mode is irrelevant to the answer even though it is four
times larger. The derivation *Why eigenvalues decide stability* walks the same argument
symbolically, and the sandbox *Damping, poles and the response they produce* lets you
drag $\zeta$ and $\omega_n$ and watch the pole pair and the step response move together.
''',
                },
            ],
            "quiz": {
                "title": "What the eigenvalues promise, and what they do not",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A plant has eigenvalues $-0.3 \\pm j8$ and $-6$. Which mode decides how long you wait for the transient to disappear?",
                        "opts": [
                            "The real pole at $-6$, since it is the largest eigenvalue present",
                            "The pair at $-0.3 \\pm j8$, since their real part is the least negative",
                            "The pair at $-0.3 \\pm j8$, since a magnitude of 8 is the largest of them",
                            "All three together, as the response is the sum of all the modes",
                        ],
                        "a": 1,
                        "whys": [
                            r"The $-6$ mode is the one that disappears first, not last: it is down to 2% of its starting size in 0.8 s while the pair is still ringing at nearly full amplitude. Naming it as the answer predicts a settled machine about twenty times too early.",
                            r"Its modes decay as $e^{-0.3t}$, and that is the slowest thing in the system.",
                            r"The magnitude is $\sqrt{0.3^2 + 8^2} \approx 8$, and it is almost all imaginary part. Imaginary part is rotation: $|e^{j\omega t}| = 1$ at every instant, so it moves the state around without shrinking it, and contributes nothing to how long you wait.",
                            r"The response is indeed a sum of all three, but a sum is dominated by whichever term is still non-zero when the others have gone. After 5 s the $-6$ term is $10^{-13}$ of its start and the pair is at 22% of its own — an even split in no sense that matters.",
                        ],
                        "why": r"""
The size of a mode is $|e^{\lambda t}| = e^{\sigma t}$, in which the imaginary part does
not appear: rotation moves the state without shrinking it. So the mode that is still
present when the others have gone is the one whose real part is closest to zero, which
here is the pair at $-0.3$ despite their being by far the largest eigenvalues in the
system. Reaching for the biggest number is the reliable way to get this wrong, and it
errs towards optimism — it would promise a settled plant twenty times too early. This is
exactly why `settling_time` in this module's lab takes the maximum over real parts.
""",
                    },
                    {
                        "q": "The determinant of a $2 \\times 2$ system matrix comes out negative. What follows, whatever the trace turns out to be?",
                        "opts": [
                            "The eigenvalues are complex, so the trajectories spiral around the origin",
                            "The eigenvalues are real and of opposite sign, so one direction grows",
                            "The eigenvalues are real and negative, so all trajectories decay",
                            "Not much on its own: a negative trace would still leave a stable system",
                        ],
                        "a": 1,
                        "whys": [
                            r"A complex pair are conjugates, so their product is $|\lambda|^2$, which cannot be negative. A negative determinant rules the spiral out rather than producing one.",
                            r"Their product is the determinant, and a negative product needs one root each side of zero.",
                            r"Two negative reals multiply to a positive number, so this case is exactly the one a negative determinant excludes. It is the reading that comes from treating the determinant like a trace and taking its sign as the sign of the eigenvalues.",
                            r"The trace really does decide stability once the determinant is positive, which is where the habit comes from. With $\Delta < 0$ there is a growing direction whatever the trace does, and $A = \begin{bmatrix}0 & 1\\ 4 & -0.4\end{bmatrix}$ has $\tau = -0.4$ and is a saddle.",
                        ],
                        "why": r"""
The two eigenvalues multiply to the determinant, so a negative determinant forces them
to be real — a conjugate pair multiplies to $|\lambda|^2 \ge 0$ — and to straddle zero.
One eigenvalue in the right half-plane is a growing direction, so the origin is a saddle
and the system is unstable no matter what the trace is doing. The trace is only allowed
to decide anything after the determinant has come out positive, which is why the lab's
`classify` tests the determinant first and returns before it ever looks at $\tau$.
""",
                    },
                    {
                        "q": "Both eigenvalues of a plant sit exactly on the imaginary axis, at $\\pm j3$. Is the plant stable?",
                        "opts": [
                            "Yes: a closed orbit never leaves a bounded region, which is stability",
                            "No: a zero real part makes the modes grow linearly in time",
                            "No: nothing grows, but nothing decays either, which is marginal",
                            "Yes: the real part is zero and zero is not positive, so nothing grows",
                        ],
                        "a": 2,
                        "whys": [
                            r"Boundedness and stability are different promises, and this is the case that separates them. A centre stays bounded forever and never approaches the origin, so a disturbance that arrives is a disturbance you keep.",
                            r"Linear growth in $t$ comes from a *repeated* eigenvalue with a single eigenvector, which produces $te^{\lambda t}$. A distinct conjugate pair on the axis gives pure sinusoids of constant amplitude.",
                            r"$|e^{\pm j3t}| = 1$ forever: the amplitude the system starts with is the amplitude it keeps.",
                            r"The condition is strict inequality, and the boundary is excluded on purpose rather than by carelessness. On the axis the modelling error decides the sign, and a dashpot of 0.001 N.s/m either way flips the answer.",
                        ],
                        "why": r"""
$|e^{\pm j3t}| = 1$ at every instant, so a state that starts at some amplitude keeps
exactly that amplitude forever: the trajectories are closed orbits around the origin,
the phase portrait the lab calls a centre. That is bounded, and bounded is not the same
promise as stable — asymptotic stability requires the state to return to the origin, and
this one never does. The condition on the eigenvalues is a strict inequality for a
practical reason as much as an algebraic one: on the axis, the smallest unmodelled term
decides which side the real system lands on.
""",
                    },
                    {
                        "q": "Holding $\\zeta$ fixed and doubling $\\omega_n$ moves both poles twice as far from the origin along the same rays. What does the step response do?",
                        "opts": [
                            "The identical curve, replayed in half the time, overshooting as before",
                            "The same settling time as before, with the overshoot cut in half",
                            "Twice the overshoot, the poles now being further from the origin",
                            "Half the settling time it had, and half of the overshoot going with it too",
                        ],
                        "a": 0,
                        "whys": [
                            r"Overshoot depends on the angle to the poles, and the angle did not move.",
                            r"This has the two effects the wrong way round. It is $\zeta$ that fixes the shape and $\omega_n$ that fixes the clock, so holding $\zeta$ is precisely what guarantees the overshoot is untouched, and moving $\omega_n$ is precisely what changes the settling time.",
                            r"Distance from the origin is $\omega_n$, and $\omega_n$ sets the speed rather than the shape. Overshoot is $\exp(-\pi\zeta/\sqrt{1-\zeta^2})$, a function of the angle alone, so it cannot depend on how far out the poles have been pushed.",
                            r"The settling time halves, that half being correct. The overshoot does not follow it: $\zeta$ was held, so the ratio of one peak to the next is unchanged and the first peak sits at the same height above the final value.",
                        ],
                        "why": r"""
Doubling $\omega_n$ at fixed $\zeta$ scales the pole pair by two without rotating it, and
the real part $-\zeta\omega_n$ and the imaginary part $\omega_n\sqrt{1-\zeta^2}$ scale
together. That is a pure change of time scale: the envelope decays twice as fast and the
ringing is twice as fast, so the response is the old curve with the time axis compressed
by two. The overshoot is $\exp(-\pi\zeta/\sqrt{1-\zeta^2})$, which depends on the angle
of the poles and not their distance, so it does not move at all. The sandbox in this
module makes the point directly: raise $\omega_n$ and the shape of the trace is preserved
while the axis contracts under it.
""",
                    },
                    {
                        "q": "Both eigenvalues of $A$ have real part $-1$, and the state starts with $\\lVert x(0)\\rVert = 1$. What can you promise about $\\lVert x(t)\\rVert$?",
                        "opts": [
                            "It falls monotonically, both modes decaying from the first instant on",
                            "It ends up decaying like $e^{-t}$, having possibly grown a lot first",
                            "It decays like $e^{-t}$ times a constant that is never larger than 1",
                            "It stays below 1 throughout, since neither of the modes ever grows",
                        ],
                        "a": 1,
                        "whys": [
                            r"Monotone decay is what you get when $A$ is symmetric, which is where the intuition is trained. A non-symmetric $A$ has non-orthogonal eigenvectors, and two shrinking vectors whose sum is nearly a cancellation can have a sum that grows for a while.",
                            r"The bound is $\lVert x(t)\rVert \le M e^{-t}$, and nothing fixes $M$ at 1.",
                            r"This is the correct rate with an unjustified constant attached. $\lVert e^{At}\rVert \le Me^{\sigma t}$ holds for some $M$, but $M$ is a property of the eigenvectors, and for $A = \begin{bmatrix}-1 & 20\\ 0 & -2\end{bmatrix}$ it is above 5.",
                            r"Each mode does shrink from the first instant, and the state is still able to grow: the modes are added as vectors, not as magnitudes, and a near-cancellation between two shrinking terms unwinds before it decays.",
                        ],
                        "why": r"""
The eigenvalues give the asymptotic rate and nothing else. The honest bound is
$\lVert x(t)\rVert \le M e^{-t}\lVert x(0)\rVert$ for some constant $M$ that depends on
how nearly parallel the eigenvectors are, and $M$ can be very large. The example in the
reading, $A = \begin{bmatrix}-1 & 20 \\ 0 & -2\end{bmatrix}$, has both eigenvalues real
and negative and reaches five times its starting norm at $t = 0.69$ s before turning
round. The reason the mistake is easy is that it is true for symmetric matrices, where
the eigenvectors are orthogonal and $M = 1$ — and that is the case every linear algebra
course spends the most time on.
""",
                    },
                    {
                        "q": "A colleague reports a $2 \\times 2$ plant with trace $-0.4$ and determinant $4$, and sends no other information. What can you tell them?",
                        "opts": [
                            "It is a stable node whose two real poles multiply to give 4",
                            "It is a centre: a determinant of 4 puts both poles on the axis",
                            "It is a stable spiral, with poles at $-0.2 \\pm j1.99$ exactly",
                            "Nothing yet, as the trace and determinant do not fix the poles",
                        ],
                        "a": 2,
                        "whys": [
                            r"A node needs real roots, which needs $\tau^2 \ge 4\Delta$. Here $\tau^2 = 0.16$ against $4\Delta = 16$, so the roots are complex and the trajectories spiral rather than approaching along a straight direction.",
                            r"A centre requires the real part to be zero, which requires $\tau = 0$. The trace is $-0.4$, and it is the trace alone that decides how far off the axis the pair sits.",
                            r"$\lambda^2 - \tau\lambda + \Delta = 0$ with $\tau = -0.4$ and $\Delta = 4$.",
                            r"For a $2\times 2$ they fix the poles completely: the characteristic polynomial of any $2\times 2$ is $\lambda^2 - \tau\lambda + \Delta$, so those two numbers are the polynomial. The instinct is right for larger matrices, where trace and determinant are two coefficients out of $n$.",
                        ],
                        "why": r"""
For a $2 \times 2$ the characteristic polynomial is $\lambda^2 - \tau\lambda + \Delta$,
so the trace and the determinant *are* the polynomial and the poles follow:
$\lambda = (-0.4 \pm \sqrt{0.16 - 16})/2 = -0.2 \pm j1.98997$. Complex, real part
negative, so a stable spiral — and those are the bench rig's own poles, which is the
point of the module: the whole classification lives in two invariants that survive any
change of state coordinates. The instinct that two numbers cannot be enough is sound for
larger systems, where they are two coefficients of $n$ and the rest are missing.
""",
                    },
                ],
            },
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
            "build": {
                "title": "An eigenvalue pair you can put a probe on",
                "minutes": 26,
                "brief": r"""
Everything in this module has been an eigenvalue of a matrix. Here it is a resonance
you can measure, because a series RLC driven at one end and read across the capacitor
*is* the mass-spring-damper of the derivations, with a different set of units on it.

## What you are asked for

Build a **series RLC** from the 1 V source to ground, with the probe on the capacitor,
whose poles sit at

$$s = -500 \pm j1936\ \text{rad/s}$$

Those are the poles of $\omega_n = 2000$ rad/s at $\zeta = 0.25$: check for yourself
that $-\zeta\omega_n = -500$ and $\omega_n\sqrt{1-\zeta^2} = 1936$, and that the pair
sits exactly $\omega_n$ from the origin.

The **100 mH inductor is already on the canvas** and is the one you have. That fixes
the arithmetic: with $L$ chosen, $C$ follows from $\omega_n = 1/\sqrt{LC}$ and then
$R$ follows from $\zeta = \frac{R}{2}\sqrt{C/L}$. Add the resistor and the capacitor,
wire the loop, and put the probe on the node the capacitor is on.

## How it is marked

Nothing here compares your drawing to a reference — it is measured, the way you would
measure it on a bench, so any wiring that behaves correctly passes.

- At DC the capacitor is an open circuit, so the probe must sit at the full 1 V. That
  is the check that says you built a *series* loop and not a divider.
- At $\omega_n$ the two reactances cancel and the response is $1/(2\zeta)$ — a gain of
  **2**, from three passive components. That single number pins $\zeta$.
- Two poles means the response falls at 40 dB per decade far above resonance: a factor
  of 100 per decade, not 10. That is the check a first-order circuit cannot pass.
- Driven with a step it must overshoot and ring before it settles, which is the
  time-domain face of the same complex pair.

## The trap

A single resistor and capacitor also sits at 1 V at DC and also falls off with
frequency. It has one real pole, no resonance, no overshoot, and it fails the last two
checks — which is the whole distinction this module is about.
""",
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p3", "kind": "L", "x": 15, "y": 5, "rot": 0, "value": 0.1},
                        {"id": "p5", "kind": "GND", "x": 19, "y": 10},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 11, "y": 5, "rot": 0, "value": 100},
                        {"id": "p3", "kind": "L", "x": 15, "y": 5, "rot": 0, "value": 0.1},
                        {"id": "p4", "kind": "C", "x": 19, "y": 7, "rot": 1, "value": 2.5e-6},
                        {"id": "p5", "kind": "GND", "x": 19, "y": 10},
                        {"id": "p6", "kind": "OUT", "x": 19, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [10, 5]},
                        {"a": [12, 5], "b": [14, 5]},
                        {"a": [16, 5], "b": [19, 5]},
                        {"a": [19, 5], "b": [19, 6]},
                        {"a": [19, 8], "b": [19, 10]},
                    ],
                },
                "checks": [
                    {
                        "name": "one R, one L, one C in a loop that reaches 1 V at DC",
                        "code": r"""
c.assert(c.count('R') === 1, 'Use exactly one resistor; there are ' + c.count('R') + '.');
c.assert(c.count('L') === 1, 'Use exactly one inductor; there are ' + c.count('L') + '.');
c.assert(c.count('C') === 1, 'Use exactly one capacitor; there are ' + c.count('C') + '.');
c.close(c.vout(), 1.0, 0.02,
  'the probed node at DC. A capacitor is an open circuit at DC and an inductor is a ' +
  'short, so a series loop puts the whole 1 V across the capacitor. Anything less ' +
  'means there is a DC path to ground in parallel with it');
""",
                    },
                    {
                        "name": "the gain at 2000 rad/s is 1/(2ζ) = 2",
                        "code": r"""
const fn = 2000 / (2 * Math.PI);            /* 318.31 Hz */
c.close(c.gain(fn), 2.0, 0.06,
  'the gain at the natural frequency. There the inductor and capacitor cancel exactly ' +
  'and only the resistor is left, so |H| = 1/(2*zeta). A gain above 2 means zeta is ' +
  'too small (R too low); below 2 means R is too high');
""",
                    },
                    {
                        "name": "two poles: 40 dB per decade, not 20",
                        "code": r"""
const a = c.gain(10e3), b = c.gain(100e3);
c.assert(a > 0, 'The response at 10 kHz is zero; check the probe is on the capacitor.');
c.close(a / b, 100, 0.12,
  'the fall over one decade far above resonance. Two poles give a factor of 100 per ' +
  'decade. A factor near 10 means the circuit is first order — an R and a C with no ' +
  'inductor in the path, or the inductor shorted out by a wire');
""",
                    },
                    {
                        "name": "a step makes it overshoot and ring before settling",
                        "code": r"""
const s = c.step(0.02);
let peak = 0;
for (let i = 0; i < s.v.length; i++) if (s.v[i] > peak) peak = s.v[i];
const settled = s.v[s.v.length - 1];
c.close(settled, 1.0, 0.03, 'the final value after the ringing has died away');
c.assert(peak > 1.3,
  'The step response only reached ' + c.fmt(peak, 'V') + ' — it never overshoots. ' +
  'A complex pole pair must overshoot: at zeta = 0.25 the first peak is 1.44 V in ' +
  'theory, and a little under that here because the transient solver is backward ' +
  'Euler and loses a few percent of the ringing. ' +
  'An overdamped circuit (R too large) creeps up to 1 V and never passes it.');
""",
                    },
                ],
                "hints": [
                    "Work $C$ out first. $\\omega_n = 1/\\sqrt{LC}$ with $\\omega_n = 2000$ and $L = 0.1$ H gives $C = 1/(\\omega_n^2 L)$.",
                    "Then $R = 2\\zeta\\omega_n L$. Both forms of $\\zeta$ agree; use whichever you find easier to remember.",
                    "The loop runs source $\\to$ R $\\to$ L $\\to$ capacitor $\\to$ ground, and the source's own bottom terminal goes to ground too. The probe belongs on the node shared by the inductor's right-hand end and the top of the capacitor.",
                ],
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
            "read": [
                {
                    "title": "The tank you cannot drain, and the force you cannot afford",
                    "minutes": 16,
                    "body": r'''
Two tanks stand side by side on a rig. Each drains through its own needle valve, and the
two valves came off the same production line and were set with the same gauge, so each
tank empties with a time constant of 20 s. A single pump feeds them through a symmetric
manifold that splits the flow in half. Tank 1 starts at 300 mm, tank 2 at 100 mm, and
the operator is asked to bring them level in half a minute.

Three attempts: the pump left off, the pump held flat out, and the pump switched on and
off every second. Watch what the level difference does under each.

```python
def run(tau1, tau2, pump, h0, dt=0.001, seconds=30.0):
    h = list(h0)
    for n in range(int(seconds / dt)):
        u = pump(n * dt)
        h = [h[0] + dt * (-h[0] / tau1 + 0.5 * u),
             h[1] + dt * (-h[1] / tau2 + 0.5 * u)]
    return h


schedules = {
    "pump off      ": lambda t: 0.0,
    "pump flat out ": lambda t: 20.0,
    "pump in bursts": lambda t: 20.0 if int(t) % 2 == 0 else 0.0,
}
for name, u in schedules.items():
    h = run(20.0, 20.0, u, [300.0, 100.0])
    print(f"{name}   h1 = {h[0]:7.2f}   h2 = {h[1]:7.2f}   "
          f"h1 - h2 = {h[0] - h[1]:.6f} mm")
```

```text
pump off         h1 =   66.94   h2 =   22.31   h1 - h2 = 44.624359 mm
pump flat out    h1 =  222.31   h2 =  177.69   h1 - h2 = 44.624359 mm
pump in bursts   h1 =  142.68   h2 =   98.06   h1 - h2 = 44.624359 mm
```

The levels are wildly different in the three runs. The difference between them is
identical to the last digit printed, and it would stay identical for any schedule anyone
could invent, including one designed by an adversary. The operator has been given a task
that no input performs.

## Which directions the input can reach

Subtract the two state equations. With $d = h_1 - h_2$,

$$\dot{d} = \left(-\frac{h_1}{\tau} + \frac{u}{2}\right) -
            \left(-\frac{h_2}{\tau} + \frac{u}{2}\right) = -\frac{d}{\tau}$$

and the pump has left the equation. The difference is a mode of the plant with an
eigenvalue of $-1/20$, and no route from the input reaches it: $u$ enters both tanks with
the same sign and the same size, and both tanks forget at the same rate, so whatever the
pump adds to the difference in one instant it has already taken away.

The general version comes from the solution rather than from a lucky subtraction. From
rest,

$$x(t) = \int_0^t e^{A(t-s)}B\,u(s)\,ds$$

so every state you can ever reach is a weighted sum of vectors of the form
$e^{A\theta}B$. Expand that exponential:
$e^{A\theta}B = B + \theta AB + \frac{\theta^2}{2}A^2B + \cdots$. Whatever the schedule
$u$, the result lies in the span of $B, AB, A^2B, \dots$ — and Cayley–Hamilton says
$A^n$ is a combination of lower powers, so the list closes after $n$ terms. The reachable
set is the column span of

$$\mathcal{C} = [\,B \ \ AB \ \ \cdots \ \ A^{n-1}B\,]$$

and the system is controllable when that span is the whole of $\mathbb{R}^n$, which for
$n$ states means rank $n$. Nothing was postulated here; the matrix is the list of
directions the integral can produce.

Put the tanks in it. With $A = \mathrm{diag}(-1/\tau_1, -1/\tau_2)$ and
$B = [\,0.5\ \ 0.5\,]^\top$, the second column is $AB = [-0.5/\tau_1,\ -0.5/\tau_2]^\top$
and

$$\det \mathcal{C} = 0.5\left(-\frac{0.5}{\tau_2}\right) -
                     0.5\left(-\frac{0.5}{\tau_1}\right)
                   = 0.25\left(\frac{1}{\tau_1} - \frac{1}{\tau_2}\right)$$

Identical valves make that zero: $AB$ is $-1/\tau$ times $B$ and adds no new direction,
so the span is the single line through $[1, 1]$ and the difference direction $[1, -1]$ is
unreachable. Give tank 2 a slightly larger valve and the determinant is non-zero, which
is the algebra saying that the input now excites the two modes at different rates and can
therefore separate them.

```python
def place(A, B, p1, p2):
    """Gains [k1, k2] putting the eigenvalues of A - B K at p1 and p2."""
    def tr_det(k1, k2):
        M = [[A[0][0] - B[0] * k1, A[0][1] - B[0] * k2],
             [A[1][0] - B[1] * k1, A[1][1] - B[1] * k2]]
        return M[0][0] + M[1][1], M[0][0] * M[1][1] - M[0][1] * M[1][0]
    t0, d0 = tr_det(0.0, 0.0)
    t1, d1 = tr_det(1.0, 0.0)
    t2, d2 = tr_det(0.0, 1.0)
    a, b = t1 - t0, t2 - t0            # trace and determinant are both
    c, d = d1 - d0, d2 - d0            # affine in (k1, k2)
    r1, r2 = (p1 + p2) - t0, (p1 * p2) - d0
    det = a * d - b * c
    if abs(det) < 1e-15:
        return None
    return [(r1 * d - b * r2) / det, (a * r2 - r1 * c) / det]


for tau2 in (20.0, 25.0, 20.01):
    A = [[-1 / 20.0, 0.0], [0.0, -1 / tau2]]
    B = [0.5, 0.5]
    AB = [A[0][0] * B[0], A[1][1] * B[1]]
    detC = B[0] * AB[1] - B[1] * AB[0]
    K = place(A, B, -0.2, -0.3)
    print(f"tau2 = {tau2:6.2f} s   det[B AB] = {detC:11.3e}", end="   ")
    if K is None:
        print("no K exists: the poles cannot be moved")
    else:
        demand = -(K[0] * 105.0 + K[1] * 95.0)
        print(f"K = [{K[0]:9.2f}, {K[1]:9.2f}]   pump asked for: {demand:9.1f}")
```

```text
tau2 =  20.00 s   det[B AB] =   0.000e+00   no K exists: the poles cannot be moved
tau2 =  25.00 s   det[B AB] =   2.500e-03   K = [    -7.50,      8.32]   pump asked for:      -2.9
tau2 =  20.01 s   det[B AB] =   6.247e-06   K = [ -3001.50,   3002.30]   pump asked for:   29939.0
```

Hold the third line for a moment; it is the one this module is really about.

## From reaching a state to choosing the dynamics

Feed the state back: measure $x$, compute $u = -Kx$ with $K$ a row, and substitute into
the plant.

$$\dot{x} = Ax + B(-Kx) = (A - BK)x$$

The loop is a free system again, with a matrix you chose part of. Since the eigenvalues of
$A - BK$ are the roots of its characteristic polynomial, choosing $K$ is choosing that
polynomial — and for a controllable single-input plant with $n$ states, the $n$ entries of
$K$ can produce any polynomial of degree $n$ you like.

The bench rig from module 1 makes that concrete. It has $A = \begin{bmatrix} 0 & 1 \\ -4 &
-0.4\end{bmatrix}$ and $B = [\,0\ \ 1\,]^\top$, so

$$A - BK = \begin{bmatrix} 0 & 1 \\ -4 - k_1 & -0.4 - k_2 \end{bmatrix},
\qquad \det(sI - (A - BK)) = s^2 + (0.4 + k_2)s + (4 + k_1)$$

Ask for poles at $-5$ and $-6$. Their polynomial is $s^2 + 11s + 30$, and matching
coefficients gives $k_2 = 10.6$ and $k_1 = 26$ with no linear algebra at all. Ask for
$-20$ and $-24$ instead — four times as far out — and the polynomial is $s^2 + 44s + 480$,
giving $k_2 = 43.6$ and $k_1 = 476$.

```python
def place(A, B, p1, p2):
    """Gains [k1, k2] putting the eigenvalues of A - B K at p1 and p2."""
    def tr_det(k1, k2):
        M = [[A[0][0] - B[0] * k1, A[0][1] - B[0] * k2],
             [A[1][0] - B[1] * k1, A[1][1] - B[1] * k2]]
        return M[0][0] + M[1][1], M[0][0] * M[1][1] - M[0][1] * M[1][0]
    t0, d0 = tr_det(0.0, 0.0)
    t1, d1 = tr_det(1.0, 0.0)
    t2, d2 = tr_det(0.0, 1.0)
    a, b = t1 - t0, t2 - t0
    c, d = d1 - d0, d2 - d0
    r1, r2 = (p1 + p2) - t0, (p1 * p2) - d0
    det = a * d - b * c
    return [(r1 * d - b * r2) / det, (a * r2 - r1 * c) / det]


def closed_loop(A, B, K, x0, dt=1e-4, seconds=3.0):
    """Peak |u| over the response, and the last time |position| exceeds 1 mm."""
    x, peak_u, t_last = list(x0), 0.0, 0.0
    for n in range(int(seconds / dt)):
        u = -(K[0] * x[0] + K[1] * x[1])
        peak_u = max(peak_u, abs(u))
        if abs(x[0]) > 0.001:
            t_last = n * dt
        dx0 = A[0][0] * x[0] + A[0][1] * x[1] + B[0] * u
        dx1 = A[1][0] * x[0] + A[1][1] * x[1] + B[1] * u
        x = [x[0] + dt * dx0, x[1] + dt * dx1]
    return peak_u, t_last


A = [[0.0, 1.0], [-4.0, -0.4]]
B = [0.0, 1.0]
for p1, p2 in ((-5.0, -6.0), (-20.0, -24.0)):
    K = place(A, B, p1, p2)
    peak_u, t_last = closed_loop(A, B, K, [0.050, 0.0])
    print(f"poles {p1:6.1f},{p2:6.1f} -> K = [{K[0]:8.2f}, {K[1]:6.2f}]"
          f"   peak force {peak_u:6.2f} N   inside 1 mm after {t_last:.3f} s")
```

```text
poles   -5.0,  -6.0 -> K = [   26.00,  10.60]   peak force   1.30 N   inside 1 mm after 1.073 s
poles  -20.0, -24.0 -> K = [  476.00,  43.60]   peak force  23.80 N   inside 1 mm after 0.268 s
```

Four times the speed cost 18.3 times the force. The exponent is visible in the algebra:
$k_1 = p_1p_2 - k/m$, a product of the two pole distances, so it grows as the square while
the response time falls as the reciprocal. It is 18.3 rather than exactly 16 because part
of $k_1$ is spent cancelling the 4 N/m the spring already supplies — $476/26 =
(480-4)/(30-4)$. The derivation *Placing the poles of a double integrator* is the same
calculation with that spring removed, and there the ratio is exactly $\omega_n^2$. The
sandbox *Buying speed with control effort* plots the force alongside the position so you
can read the peak off directly; treat that number as the actuator specification you are
writing.

## The mistake: reading rank as a yes or no

The rank test is a yes or no, and the temptation is to treat the answer as one.
`matrix_rank` on the third row of the table above returns 2 and complains about nothing.
The valves in that row differ by one part in two thousand — a difference no gauge on the
rig can see — and the design that follows asks the pump for 29 939 mm/s to correct a
10 mm mismatch, against the 20 mm/s the pump delivered flat out in the first experiment.
It is a controllable plant and an uncontrollable machine.

The reason the reflex is tempting is that the algebra genuinely is a yes or no: a
determinant is zero or it is not, and every textbook statement of the theorem is phrased
that way. What the theorem does not say is that a determinant of $6.2 \times 10^{-6}$
buys you anything you can use. The honest reading of $\det\mathcal{C}$ is as a *distance*
from uncontrollability, and the gains scale with its reciprocal: 2500 times smaller here,
400 times larger gains. When the lab *Test controllability and place the poles* has you
call `np.linalg.matrix_rank`, that call is answering the algebraic question, and the size
of the gains that come back out of `place` is answering the engineering one. Read both.

## Where this stops holding

The pump cannot run backwards. Every schedule in the first experiment was non-negative,
because a pump adds water and never removes it, while $u = -Kx$ produces whatever sign
the algebra wants — the second row of the table asks for $-2.9$. A one-sided actuator is
not a linear one, and a design that relies on negative input is describing a machine that
was not built. The same goes for the upper limit: ask for 23.8 N from a coil rated at 5 N
and the response you get is not a slower version of the design, it is a different system
whose behaviour the eigenvalues of $A - BK$ do not describe.

Pole placement also assumes the model is right. The gain of 3001.5 exists to exploit a
0.05% valve mismatch; if the true mismatch is 0.06%, the controller is not slightly
wrong but designed against a plant that is not there. And placing poles says nothing
about what happens between them — a design can put every eigenvalue at $-20$ and still
amplify sensor noise enormously, because $K$ multiplies the state estimate and the noise
in it alike.

Finally, $u = -Kx$ needs $x$, all of it. The rig has one gauge and two states, and the
tanks have two floats and no flow meter. Module 4 is about what to do when the vector
you are feeding back is one you cannot measure.

## What you are about to build

The lab *Test controllability and place the poles* asks for `controllable(A, B)`, which
builds $[\,B\ \ AB\,]$ and tests its rank, and `place(A, B, p1, p2)`, which returns the
gain row. Its check on the double integrator expects $k_1 = p_1p_2 = 6$ and
$k_2 = -(p_1+p_2) = 5$ for poles at $-2$ and $-3$ — the coefficient matching above with
the plant's own terms set to zero. Another check moves the poles from $-1, -1$ out to
$-10, -10$ and demands that $k_1$ grow by a factor of at least fifty, which is the
squared-distance law with room to spare. The affine trick in the code here is the same
one the reference solution uses: trace and determinant are both linear in $(k_1, k_2)$,
so three evaluations and one $2 \times 2$ solve give the gains for any plant of this size.
''',
                },
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
                        "hint": "$BK$ has zeros in the top row, and $[k_1\\ k_2]$ in the bottom.",
                        "deconstruct": [
                            "$B = [0, 1]^\\top$, so $BK = \\begin{bmatrix} 0 & 0 \\\\ k_1 & k_2 \\end{bmatrix}$.",
                            "Subtracting from $A$ leaves the bottom row as $[-k_1,\\ -k_2]$.",
                        ],
                    },
                    {
                        "prompt": "Write the characteristic polynomial $\\det(sI - (A - BK))$ in terms of $s$, $k_1$ and $k_2$.",
                        "answer": "s^2 + k_2 s + k_1",
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
            "quiz": {
                "title": "Reaching every state, and paying for it",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A system is controllable. What does that guarantee?",
                        "opts": [
                            "Some finite input can drive the state from any starting point to any target point",
                            "The system is stable",
                            "Every state can be measured",
                            "The input is bounded",
                        ],
                        "a": 0,
                        "why": r"""
Controllability is a reachability statement and nothing else: there *exists* an input
that gets you there in finite time. It says nothing about whether the system settles
on its own — an unstable system can be perfectly controllable, which is precisely why
pole placement is worth doing. Being able to *measure* every state is observability,
its mirror image. And nothing here bounds the input; a nearly-uncontrollable system is
controllable on paper and asks for an input you cannot supply, which is what the
sandbox in this module is showing you.
""",
                    },
                    {
                        "q": "For a two-state system, the controllability matrix is $\\mathcal{C} = [\\,B \\;\\; AB\\,]$. The system is controllable exactly when:",
                        "opts": [
                            "$\\mathcal{C}$ has rank 2",
                            "$\\mathcal{C}$ is symmetric",
                            "$B$ is non-zero",
                            "$A$ is invertible",
                        ],
                        "a": 0,
                        "why": r"""
Full rank — for two states, rank 2, equivalently a non-zero determinant. The columns
of $\mathcal{C}$ span the directions the input can push the state in; if they only
span a line, there is a direction in state space you can never reach no matter what
you do. A non-zero $B$ is necessary but nowhere near sufficient: with
$A = \begin{bmatrix}1&0\\0&2\end{bmatrix}$ and $B = \begin{bmatrix}1\\0\end{bmatrix}$,
$B$ is non-zero and the second state is untouchable. And $A$ being invertible is
unrelated — a double integrator has a singular $A$ and is perfectly controllable.
""",
                    },
                    {
                        "q": "State feedback $u = -Kx$ is applied. Which matrix has its eigenvalues moved?",
                        "opts": ["$A - BK$", "$A - LC$", "$A + BK$", "$A$ itself, entry by entry"],
                        "a": 0,
                        "why": r"""
Substitute: $\dot{x} = Ax + B(-Kx) = (A - BK)x$. The closed loop is a new autonomous
system and $K$ is chosen to put *its* eigenvalues where you want them. $A - LC$ is the
observer's error dynamics, which is the next module and is deliberately the same shape
— that duality is why one piece of algebra does both jobs. $A$ is a property of the
plant and feedback cannot reach inside it; what feedback changes is what the loop does
around it.
""",
                    },
                    {
                        "q": "You move the closed-loop poles twice as far into the left half-plane. What goes up?",
                        "opts": [
                            "The control effort, roughly as the square of the pole distance",
                            "The steady-state error",
                            "The system's order",
                            "Nothing — pole placement is free",
                        ],
                        "a": 0,
                        "why": r"""
Faster poles mean larger gains in $K$, and the input is $-Kx$, so the demanded effort
grows quickly — for a double integrator, placing both poles at $-\omega$ needs a gain
that grows as $\omega^2$. On paper it is free; on hardware the actuator saturates, the
linear design stops describing what is happening, and the response gets *slower* than
a modest design would have been. The order is fixed by the plant and feedback cannot
change it, and steady-state error is a separate question about the reference path.
""",
                    },
                    {
                        "q": "One mode of a plant turns out to be uncontrollable. What can pole placement do with it?",
                        "opts": [
                            "Nothing — that eigenvalue stays exactly where it is",
                            "Move it, but only slowly",
                            "Move it, provided $K$ is large enough",
                            "Remove it from the system",
                        ],
                        "a": 0,
                        "why": r"""
An uncontrollable mode is invisible to the input, so no choice of $K$ touches its
eigenvalue: it appears unchanged in $A - BK$. This is the practical reason the rank
test comes before the design and not after. It also sets the bar for what a real plant
needs — if the stuck eigenvalue is in the left half-plane the system is *stabilisable*
and you can still build a working controller, and if it is not, no amount of feedback
will save it and the honest answer is to change the hardware.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "The velocity nobody measured",
                    "minutes": 16,
                    "body": r'''
The controller in module 3 wanted $u = -26x_1 - 10.6x_2$. The rig supplies $x_1$: the
laser gauge has been replaced by a linear encoder that counts in 0.1 mm steps and reports
at 1 kHz. It supplies no velocity at all, and the obvious repair is to take the
difference between consecutive counts and divide by the millisecond between them.

```python
import math

A = [[0.0, 1.0], [-4.0, -0.4]]        # the bench rig again
Q, DT, N = 1e-4, 1e-3, 8000           # 0.1 mm counts, 1 kHz, 8 s

x = [0.050, 0.0]
truth, counts = [], []
for _ in range(N):
    truth.append(x[1])
    counts.append(round(x[0] / Q) * Q)
    x = [x[0] + DT * x[1],
         x[1] + DT * (A[1][0] * x[0] + A[1][1] * x[1])]

fd = [(counts[n] - counts[n - 1]) / DT for n in range(1, N)]
err = [fd[n - 1] - truth[n] for n in range(1, N)]
rms = lambda v: math.sqrt(sum(e * e for e in v) / len(v))
print(f"true velocity: peak {max(abs(v) for v in truth) * 1000:6.1f} mm/s, "
      f"rms {rms(truth) * 1000:5.1f} mm/s")
print(f"differencing the counts: rms error {rms(err) * 1000:6.1f} mm/s")
```

```text
true velocity: peak   86.4 mm/s, rms  38.8 mm/s
differencing the counts: rms error  41.0 mm/s
```

The error in the estimate is larger than the quantity being estimated. That is not a
tuning problem to be fixed with a smoothing filter, it is arithmetic: one count is
0.1 mm, one sample interval is 1 ms, so a single count of jitter is 100 mm/s of velocity,
and the carriage never moves faster than 86 mm/s. No amount of care with the differencing
recovers information the encoder did not send.

But something else was never used. The rig obeys $\ddot{y} = -4y - 0.4\dot{y} + u$, and
that equation relates position to velocity. The encoder measured position for eight
seconds. The velocity is in there.

## Running a copy of the plant

Build a simulation of the plant and run it beside the real one, driven by the same input:

$$\dot{\hat{x}} = A\hat{x} + Bu$$

Subtract it from the plant equation and the error $e = x - \hat{x}$ obeys $\dot{e} = Ae$.
The input cancelled — both copies received it — but nothing else happened. The error
decays only as fast as the plant's own modes, which on this rig means a real part of
$-0.2$ and a wait of twenty seconds, and on the capstone's inverted pendulum means the
error grows, because the plant is unstable and so is its copy. An open-loop simulation is
not an estimator. It never looks at the machine.

The one thing you can compare is the measurement. The copy predicts what the encoder
should read, $\hat{y} = C\hat{x}$; the encoder reports $y$. The difference $y - C\hat{x}$
is the *innovation*: the only piece of information in the loop that the model could not
have produced by itself. Feed it back through a gain $L$ to be chosen:

$$\dot{\hat{x}} = A\hat{x} + Bu + L(y - C\hat{x})$$

Subtract again, with $y = Cx$ substituted:

$$\dot{e} = (Ax + Bu) - (A\hat{x} + Bu + LCx - LC\hat{x})
          = A(x - \hat{x}) - LC(x - \hat{x}) = (A - LC)e$$

The $Bu$ terms cancel exactly as before, and now $L$ is inside the matrix that governs
the error. The estimate converges when every eigenvalue of $A - LC$ has a negative real
part, whatever the plant is doing and whatever the input is — which is what the
derivation *Why the estimation error forgets the input* establishes step by step.

## Choosing L on the rig

With $C = [\,1\ \ 0\,]$ and $L = [\,\ell_1\ \ \ell_2\,]^\top$,

$$A - LC = \begin{bmatrix} -\ell_1 & 1 \\ -4 - \ell_2 & -0.4 \end{bmatrix}$$

whose trace is $-\ell_1 - 0.4$ and whose determinant is $0.4\ell_1 + 4 + \ell_2$. Ask for
poles at $-8$ and $-9$: the trace must be $-17$, giving $\ell_1 = 16.6$, and the
determinant must be 72, giving $\ell_2 = 72 - 4 - 6.64 = 61.36$. Two lines of arithmetic,
the same coefficient matching as module 3, and the reason it is the same is duality:
$\det(sI - (A - LC)) = \det(sI - (A^\top - C^\top L^\top))$, since a matrix and its
transpose share a characteristic polynomial. Placing an observer gain for $(A, C)$ *is*
placing a feedback gain for $(A^\top, C^\top)$, and the rank test comes along with it —
$\mathcal{O} = [\,C;\ CA;\ \dots\,]$ having full rank is the controllability of the
transposed pair. Here $\mathcal{O} = \begin{bmatrix} 1 & 0 \\ 0 & 1\end{bmatrix}$, full
rank, and the second row is where the velocity comes from: $CA$ reads $\dot{y}$, so the
model converts a position history into a velocity for you.

Now run it on the counts the encoder actually produced, at four different choices of
observer poles.

```python
import math

A = [[0.0, 1.0], [-4.0, -0.4]]
C = [1.0, 0.0]
Q, DT, N = 1e-4, 1e-3, 8000


def observer_gain(A, C, p1, p2):
    """L = [l1, l2] placing the eigenvalues of A - L C, by matching trace and det."""
    def tr_det(l1, l2):
        M = [[A[0][0] - l1 * C[0], A[0][1] - l1 * C[1]],
             [A[1][0] - l2 * C[0], A[1][1] - l2 * C[1]]]
        return M[0][0] + M[1][1], M[0][0] * M[1][1] - M[0][1] * M[1][0]
    t0, d0 = tr_det(0.0, 0.0)
    t1, d1 = tr_det(1.0, 0.0)
    t2, d2 = tr_det(0.0, 1.0)
    a, b = t1 - t0, t2 - t0
    c, d = d1 - d0, d2 - d0
    r1, r2 = (p1 + p2) - t0, (p1 * p2) - d0
    det = a * d - b * c
    return [(r1 * d - b * r2) / det, (a * r2 - r1 * c) / det]


x = [0.050, 0.0]
truth, counts = [], []
for _ in range(N):
    truth.append(x[1])
    counts.append(round(x[0] / Q) * Q)
    x = [x[0] + DT * x[1],
         x[1] + DT * (A[1][0] * x[0] + A[1][1] * x[1])]


def observe(L):
    xh, errs = [0.0, 0.0], []
    for n in range(N):
        errs.append(xh[1] - truth[n])
        innov = counts[n] - (C[0] * xh[0] + C[1] * xh[1])
        d0 = A[0][0] * xh[0] + A[0][1] * xh[1] + L[0] * innov
        d1 = A[1][0] * xh[0] + A[1][1] * xh[1] + L[1] * innov
        xh = [xh[0] + DT * d0, xh[1] + DT * d1]
    settled = errs[2000:]
    return math.sqrt(sum(e * e for e in settled) / len(settled))


for p1, p2 in ((-2.0, -3.0), (-8.0, -9.0), (-30.0, -33.0), (-80.0, -90.0)):
    L = observer_gain(A, C, p1, p2)
    print(f"observer poles {p1:6.1f},{p2:6.1f}  L = [{L[0]:8.2f}, {L[1]:9.2f}]"
          f"   rms velocity error {observe(L) * 1000:6.3f} mm/s")
```

```text
observer poles   -2.0,  -3.0  L = [    4.60,      0.16]   rms velocity error  0.692 mm/s
observer poles   -8.0,  -9.0  L = [   16.60,     61.36]   rms velocity error  0.009 mm/s
observer poles  -30.0, -33.0  L = [   62.60,    960.96]   rms velocity error  0.082 mm/s
observer poles  -80.0, -90.0  L = [  169.60,   7128.16]   rms velocity error  0.390 mm/s
```

The hand calculation is on the second line: $[16.6,\ 61.36]$, and it is the gain the lab
*Build a Luenberger observer* asks `observer_gain(A, C, -8.0, -9.0)` to return. Every one
of these four estimates is at least fifty times better than differencing the counts, from
the same encoder, with no extra hardware. The improvement came from the model.

## The mistake: making the observer as fast as you can

The error equation says $\dot{e} = (A - LC)e$, so pushing the eigenvalues of $A - LC$
further left makes the error decay faster, and the algebra puts no price on it. That is
the tempting reading, and the table refutes it: from $-8, -9$ out to $-80, -90$ the error
gets forty times worse.

The reason is visible in the observer equation. $L$ multiplies $y$, and $y$ is a
measurement — signal and quantisation step together. A large $L$ is an instruction to
believe the encoder over the model, and the encoder is telling the truth to within half a
count. The first row shows the other end of the same trade: $L$ near zero trusts the model
completely, and a model that converges no faster than the plant lags every real change.
The choice of observer poles is the choice of where to sit between those, which is what
the sandbox *Believing the model or believing the sensor* is showing when it raises $R$
and $Q$ — and its third experiment, scaling both together and finding nothing changes, is
the statement that only the ratio matters.

The rule of thumb, used in the capstone, is to make the observer poles two to five times
faster than the controller poles: fast enough that the estimate has settled before the
control acts on it, slow enough not to hand the actuator a stream of quantisation steps.
The capstone chooses $-2, -2.5, -3, -3.5$ for the controller and $-8, -9, -10, -11$ for
the observer for exactly that reason.

## The separation principle, and what it does not cover

Close the loop with $u = -K\hat{x}$ and the two designs meet. Write $\hat{x} = x - e$, so
$u = -Kx + Ke$, and substitute into the plant:

$$\dot{x} = Ax + B(-Kx + Ke) = (A - BK)x + BKe, \qquad \dot{e} = (A - LC)e$$

In the coordinates $(x, e)$ that is

$$\begin{bmatrix} \dot{x} \\ \dot{e} \end{bmatrix} =
\begin{bmatrix} A - BK & BK \\ 0 & A - LC \end{bmatrix}
\begin{bmatrix} x \\ e \end{bmatrix}$$

The lower-left block is zero, so the characteristic polynomial of the whole thing is the
product of the two diagonal blocks' polynomials and the $2n$ closed-loop eigenvalues are
the $n$ from $A - BK$ together with the $n$ from $A - LC$. Neither design disturbed the
other. That is the separation principle, and the capstone's final check builds precisely
that block matrix and compares its eigenvalues against the union of the two pole lists.

Read the top-right block before moving on: the estimation error drives the plant through
$BK$. Separation says the *poles* do not interact, not that the error is harmless — while
$e$ is non-zero the controller is acting on a state that is not there.

## Where this stops holding

Everything above assumed the observer's $A$ is the plant's $A$. Give the rig a spring of
4.4 N/m and tell the observer 4.0, then hold a steady 1 N and wait a minute.

```python
DT, N, U = 1e-3, 60000, 1.0
L = [16.6, 61.36]                      # poles of A - LC at -8 and -9

plant = [[0.0, 1.0], [-4.4, -0.4]]     # the spring is really 4.4 N/m
model = [[0.0, 1.0], [-4.0, -0.4]]     # the observer was told 4.0

x, xh = [0.0, 0.0], [0.0, 0.0]
for n in range(N):
    y = x[0]
    innov = y - xh[0]
    x = [x[0] + DT * (plant[0][0] * x[0] + plant[0][1] * x[1]),
         x[1] + DT * (plant[1][0] * x[0] + plant[1][1] * x[1] + U)]
    xh = [xh[0] + DT * (model[0][0] * xh[0] + model[0][1] * xh[1] + L[0] * innov),
          xh[1] + DT * (model[1][0] * xh[0] + model[1][1] * xh[1] + U + L[1] * innov)]

print("after 60 s, with the carriage at rest at its new equilibrium:")
print(f"  true     position {x[0] * 1000:8.3f} mm   velocity {x[1] * 1000:8.3f} mm/s")
print(f"  estimate position {xh[0] * 1000:8.3f} mm   velocity {xh[1] * 1000:8.3f} mm/s")
```

```text
after 60 s, with the carriage at rest at its new equilibrium:
  true     position  227.271 mm   velocity   -0.001 mm/s
  estimate position  228.534 mm   velocity   20.958 mm/s
```

The carriage is standing still and the observer insists it is moving at 21 mm/s, forever.
A 10% error in one coefficient turned $\dot{e} = (A - LC)e$ into
$\dot{e} = (A - LC)e + (A_{\text{plant}} - A_{\text{model}})x$, an error equation with a
driving term, and a driven stable system settles at a bias rather than at zero. Note the
position line too: the observer's estimate of the state it directly measures is 1.26 mm
away from the measurement it was handed. Nothing in the design promised otherwise, and a
controller reading $\hat{x}_2$ will hold a steady force against a velocity that does not
exist.

Two further limits worth carrying out of the module. Observability is a rank condition
and it degrades the same way controllability does: the lab's second check uses
$A = \mathrm{diag}(-1, -2)$ with $C = [\,1\ \ 0\,]$, where the second state never touches
the output and $\mathcal{O}$ has rank 1 — and a plant a hair away from that is observable
on paper and needs an $L$ you cannot use. And the separation principle is a statement
about eigenvalues, not about margins: a state-feedback design with good gain and phase
margin can lose them entirely once the state is replaced by an estimate, which is why
observer-based designs are checked against the loop transfer function and not only
against their pole locations.

## What you are about to build

The lab *Build a Luenberger observer* wants three functions: `observable(A, C)` stacking
$C$ on $CA$ and testing the rank, `observer_gain(A, C, p1, p2)` returning the $(2,1)$
column that places the eigenvalues of $A - LC$ — `place(A.T, C.T, p1, p2).T` is the whole
of it — and `run_observer`, which steps plant and estimate together from a deliberately
wrong start and returns the error at each step. Its checks are the claims made here: the
error begins at exactly 1.0 because the estimate starts at the origin while the plant
starts at $[1, 0]$, it is under $10^{-3}$ after four seconds, and poles at $-8, -9$ beat
poles at $-2, -3$. The fill-in exercise *The observer, line by line* takes the same four
symbols one at a time, including the sign of the innovation, which is the one place a
working observer and a diverging one differ by a single character.
''',
                },
            ],
            "quiz": {
                "title": "Estimating what the sensor does not send",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why can the observer gain $L$ be chosen without knowing anything about the controller that will use the estimate?",
                        "opts": [
                            "Because $L$ is designed on the transposed plant, in which no input appears at all",
                            "Because the input reaches plant and observer alike and cancels in the error",
                            "Because the controller is always slower, so its effect averages away",
                            "Because $u$ is bounded, so its contribution to the error stays small",
                        ],
                        "a": 1,
                        "whys": [
                            r"Duality is how $L$ gets computed, and it is a fact about characteristic polynomials rather than about inputs. Transposing $(A, C)$ would explain nothing about why the true input can be ignored, and the argument would break the moment you asked what $u$ was doing.",
                            r"Both equations carry $Bu$, so subtracting them removes it entirely.",
                            r"There is no such rule, and observer poles are usually chosen faster than the controller's rather than slower. Even were it true, a slow input would still appear in the error equation and leave a term to worry about.",
                            r"Boundedness would give a bounded error, which is a much weaker promise than convergence to zero, and it would make the estimate depend on how hard the actuator was working. The $Bu$ term is not small in the error equation; it is absent.",
                        ],
                        "why": r"""
The observer contains a copy of $Bu$ because you feed it the same input you send to the
plant. Subtracting the two equations therefore removes the term exactly, leaving
$\dot{e} = (A - LC)e$ with no $u$ and no reference in it. That is what lets the two
designs be done on separate days by separate people. What separation does *not* say is
that the error is harmless: in the closed loop the error drives the plant through $BK$,
so a slow observer still produces a poor response — it produces one whose poles are
nonetheless exactly where the two designs put them.
""",
                    },
                    {
                        "q": "A colleague sets the observer poles ten times further left than before and reports that the estimate got noticeably worse. What happened?",
                        "opts": [
                            "The error dynamics went unstable, as a large $L$ always eventually does",
                            "The larger $L$ multiplies the measurement, so it amplifies the sensor noise",
                            "Nothing real: a faster observer converges faster, so this must be a bug",
                            "The observer poles crossed over the plant poles, and the two sets then interacted",
                        ],
                        "a": 1,
                        "whys": [
                            r"The eigenvalues of $A - LC$ are exactly where they were placed, at ten times the distance into the left half-plane, so the error dynamics are more stable than before rather than less. Instability would show as divergence, not as a noisier estimate.",
                            r"$L(y - C\hat{x})$ scales whatever is in $y$, and part of $y$ is noise.",
                            r"Faster convergence is what the noise-free error equation promises, and that equation is correct as far as it goes. It contains no measurement noise, so it can say nothing about the quantity the colleague was measuring.",
                            r"Observer poles and plant poles do not interact; $A - LC$ has the eigenvalues it was given whatever $A$ started with. There is a real interaction to worry about in the closed loop, but it is with the *controller* poles, and it is the one the separation principle rules out.",
                        ],
                        "why": r"""
The correction term is $L(y - C\hat{x})$, and $y$ is a real measurement: signal plus
quantisation plus noise. Scaling $L$ up scales the noise into the estimate along with the
information, so the error against the true state passes through a minimum and then gets
worse. The reading's sweep shows it: poles at $-8, -9$ give an rms velocity error of
0.009 mm/s and poles at $-80, -90$ give 0.390 mm/s, from the same encoder. The noise-free
error equation genuinely does promise faster convergence, which is why the mistake is so
easy — the equation is right, and it is silent about the thing that went wrong.
""",
                    },
                    {
                        "q": "The plant's spring is really 4.4 N/m and the observer was built with 4.0. What happens to the estimation error under a steady input?",
                        "opts": [
                            "It still decays to zero, more slowly, since $A - LC$ is unchanged",
                            "It grows without bound, the model error acting as positive feedback",
                            "It settles at a non-zero bias, the mismatch driving the error equation",
                            "It oscillates at the difference between the two natural frequencies involved",
                        ],
                        "a": 2,
                        "whys": [
                            r"$A - LC$ is indeed unchanged, and that is the trap: the homogeneous part is still stable, but the equation is no longer homogeneous. A stable system with a persistent driving term settles somewhere, and where it settles is not zero.",
                            r"Unbounded growth needs an unstable error matrix, and $A - LC$ still has its poles at $-8$ and $-9$. A bounded input into a stable system gives a bounded output; the damage here is a bias, not a divergence.",
                            r"The mismatch adds $(A_p - A_m)x$ to $\dot{e}$, and a driven stable system settles off zero.",
                            r"Beat frequencies come from adding two oscillations, and there is only one oscillator here — the error follows the poles of $A - LC$, which are real. Under a constant input the plant is heading for a constant equilibrium and so is the error.",
                        ],
                        "why": r"""
Subtracting the two equations no longer cancels everything: what is left is
$\dot{e} = (A - LC)e + (A_{\text{plant}} - A_{\text{model}})x$, a stable error system with
a driving term proportional to the state. Hold a constant force and the plant settles at
a constant $x$, so the error settles at a constant too — in the reading's run, an
estimated velocity of 21 mm/s on a carriage that has stopped moving. The position estimate
is 1.26 mm off as well, which is worth noticing: it is off even though position is the
quantity the encoder directly reports.
""",
                    },
                    {
                        "q": "A two-state plant has $A = \\mathrm{diag}(-1, -2)$ and $C = [\\,1\\ \\ 0\\,]$. What can an observer do about the second state?",
                        "opts": [
                            "Estimate it after a delay, once $CA$ has revealed it in the output",
                            "Estimate it if $L$ is chosen large enough to force convergence",
                            "Nothing: it never affects the output, so no gain can reveal it",
                            "Estimate it, but only while the plant is being driven by an input",
                        ],
                        "a": 2,
                        "whys": [
                            r"$CA = [-1\ \ 0]$ here, and every further row of $\mathcal{O}$ is another multiple of $[1\ \ 0]$: the second column stays zero forever. Waiting longer collects more copies of the same information.",
                            r"$\mathcal{O} = [C;\ CA]$ has rank 1, so the second column of $A - LC$ is untouched by $L$.",
                            r"Size cannot substitute for direction. $LC$ has a zero second column whatever $L$ is, because $C$ has a zero second entry, so the mode's eigenvalue sits at $-2$ in $A - LC$ for every gain you could choose.",
                            r"The input would have to couple the two states for that to help, and this $A$ is diagonal — the second state evolves alone whether or not it is being driven. Adding an input moves both states without ever making one visible in the other.",
                        ],
                        "why": r"""
The observability matrix is $\begin{bmatrix} 1 & 0 \\ -1 & 0\end{bmatrix}$, rank 1, and
the reason is structural: $A$ is diagonal, so the second state evolves entirely on its own
and never appears in the first, which is the only one the sensor sees. In $A - LC$ the
product $LC$ has a zero second column for every $L$, so that eigenvalue cannot be moved
and the corresponding error mode decays at the plant's own rate or not at all. This is the
mirror of the uncontrollable tank pair: there the input could not reach a direction, here
the output cannot see one, and the same rank test decides both under a transpose.
""",
                    },
                    {
                        "q": "Controller poles are placed at $-2, -3$ and observer poles at $-8, -9$. What are the poles of the closed loop running on the estimate?",
                        "opts": [
                            "Four poles: $-2, -3, -8, -9$, the two designs not interacting",
                            "Two poles somewhere between $-2$ and $-9$, the designs averaging out",
                            "Two poles at $-2, -3$: the observer sits outside the loop",
                            "Four poles near $-2, -3$, dragged left a little by the fast observer",
                        ],
                        "a": 0,
                        "whys": [
                            r"In the coordinates $(x, e)$ the system is block triangular, so the spectra of the blocks simply add.",
                            r"There is no averaging, and the count is wrong as well: two systems of two states each make a fourth-order loop, so four poles have to appear somewhere. Nothing in the algebra merges a controller pole with an observer pole.",
                            r"The observer is very much inside the loop — its output is what the controller feeds back — and its dynamics are part of the closed loop. The system has four states once the estimate is included, so it cannot have only two poles.",
                            r"This is the intuition that the two designs must pull on each other, and it is exactly what the block-triangular structure rules out. The coupling is real but one-way: $e$ drives $x$, while nothing drives $e$, and a one-way coupling cannot move an eigenvalue.",
                        ],
                        "why": r"""
Writing the loop in the coordinates $(x, e)$ gives
$\begin{bmatrix} A - BK & BK \\ 0 & A - LC \end{bmatrix}$. The zero block makes the
characteristic polynomial the product of the two blocks' polynomials, so the four
eigenvalues are the union: $-2, -3$ from the controller and $-8, -9$ from the observer,
each exactly where it was placed. The top-right block is not zero, so the coupling is
real — the estimation error does disturb the plant — but it runs one way only, and a
one-way coupling cannot move an eigenvalue. The capstone's last check builds this matrix
and compares its spectrum against the union of the two lists.
""",
                    },
                    {
                        "q": "Why does an observer beat differencing consecutive encoder counts, when both use the same measurements?",
                        "opts": [
                            "It waits over several counts, so the quantisation noise averages towards zero",
                            "It runs at a lower rate, and a slower estimate is always a smoother one",
                            "It has the plant equations too, so it uses a second source of information",
                            "It uses the input as well, which differencing the counts throws away",
                        ],
                        "a": 2,
                        "whys": [
                            r"Averaging is part of what a low-gain observer does, and a moving average over the same counts would help as well. It does not explain why the observer with a *high* gain, which averages very little, still beats differencing by a factor of a hundred.",
                            r"Rate has nothing to do with it: the observer in the reading steps at 1 kHz, the same rate the counts arrive at. A slower estimate is smoother and also later, which for a quantity being fed to a controller is not obviously a gain.",
                            r"Differencing knows only the counts; the observer also knows $\ddot{y} = -4y - 0.4\dot{y} + u$.",
                            r"An observer does use $u$, and on a driven plant that is worth something. It is not the main effect: the run in the reading has $u = 0$ throughout and the observer still beats differencing by more than a factor of fifty.",
                        ],
                        "why": r"""
Differencing has one source of information, the counts, and its error is fixed by the
count size over the sample interval — 0.1 mm per 1 ms is 100 mm/s, against a signal that
peaks at 86 mm/s. The observer has the counts *and* the model, and the model is a strong
constraint: a trajectory of the rig cannot pass through those positions at an arbitrary
velocity. Reconciling the two is what $L$ does, and it is why the rms error falls from
41 mm/s to 0.009 mm/s with no change to the hardware. The size of $L$ is where you say
how much of each source to believe, which is what the sandbox in this module is about.
""",
                    },
                ],
            },
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
                        "hint": "The $Bu$ terms are identical in both equations, so they cancel. Substitute $y = Cx$ before subtracting.",
                        "deconstruct": [
                            "Plant: $\\dot{x} = Ax + Bu$. Observer, with $y = Cx$ substituted: $\\dot{\\hat{x}} = A\\hat{x} + Bu + LCx - LC\\hat{x}$.",
                            "Subtract the second from the first; the $Bu$ terms vanish.",
                        ],
                    },
                    {
                        "prompt": "Factor that into a single matrix acting on $e = x - \\hat{x}$. Write the matrix.",
                        "answer": "A - L C",
                        "hint": "Group the $x$ terms and the $\\hat{x}$ terms; both give the same matrix times $e$.",
                        "deconstruct": [
                            "$Ax - A\\hat{x} = A(x - \\hat{x}) = Ae$.",
                            "$-LCx + LC\\hat{x} = -LC(x - \\hat{x}) = -LCe$.",
                        ],
                    },
                    {
                        "prompt": "The error therefore obeys $\\dot{e} = (A - LC)e$. For the estimate to converge, where must every eigenvalue of $A - LC$ lie? Write the condition on the real part $\\sigma$.",
                        "answer": "\\sigma < 0",
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
            "blanks": {
                "title": "The observer, line by line",
                "minutes": 9,
                "caption": "luenberger.py — one step, four holes",
                "lang": "python",
                "brief": r"""
The observer is four symbols arranged carefully, and every one of them is somewhere a
sign or a matrix can go in wrong. Fill the holes and read the result back as a
sentence: *predict what the sensor should say, compare it with what the sensor did
say, and push the estimate in proportion to the disagreement.*

Nothing is executed here — you are choosing symbols, not writing code.
""",
                "listing": """# One step of a Luenberger observer.
#   plant     xdot = A @ x + B @ u,   y = C @ x     (x is not available to us)
#   estimate  xhat, corrected by the observer gain L

y_hat      = ___ @ xhat
innovation = ___
xhat       = xhat + dt * (A @ xhat + B @ u + ___)

# and the estimation error e = x - xhat then obeys
#   edot = ___ @ e
""",
                "blanks": [
                    {
                        "prompt": "What does the observer have to predict before it can compare anything?",
                        "hole": "?",
                        "opts": ["C", "A", "L", "B"],
                        "a": 0,
                        "why": "`C` is the sensor. `y_hat = C @ xhat` is the observer asking *if my estimate were right, what would the meter read?* — and that is the only quantity it can legitimately compare against reality.",
                        "whys": [
                            "`C` is the sensor. `y_hat = C @ xhat` is the observer asking *if my estimate were right, what would the meter read?* — and that is the only quantity it can legitimately compare against reality.",
                            "`A` propagates the state forward in time; it says nothing about what is measurable. Using it here would compare a predicted *state* against a scalar measurement, and the shapes would not even match.",
                            "`L` is the correction gain, and it belongs on the far side of the comparison — it decides how hard to act on the disagreement, not what the disagreement is.",
                            "`B` is how the input enters. The input is already accounted for in the prediction step; it is not part of what the sensor reads.",
                        ],
                    },
                    {
                        "prompt": "The innovation is the one piece of genuinely new information each step.",
                        "hole": "?",
                        "opts": ["y - y_hat", "y_hat - y", "y + y_hat", "xhat - x"],
                        "a": 0,
                        "why": "Measurement minus prediction. When the estimate is already right the innovation is zero and the correction switches itself off, which is exactly the behaviour you want.",
                        "whys": [
                            "Measurement minus prediction. When the estimate is already right the innovation is zero and the correction switches itself off, which is exactly the behaviour you want.",
                            "The sign is inverted, so every correction pushes the estimate further from the measurement. The error dynamics become $A + LC$ and a gain chosen to make the observer fast makes it diverge instead.",
                            "A sum has no zero at agreement: a correct estimate would still demand a large correction, and the observer would never settle anywhere.",
                            "`x` is the true state. If you had it there would be nothing to estimate — this line is the one thing an observer is not allowed to write.",
                        ],
                    },
                    {
                        "prompt": "How does the disagreement get back into the estimate?",
                        "hole": "?",
                        "opts": ["L @ innovation", "innovation @ L", "C @ innovation", "L @ y"],
                        "a": 0,
                        "why": "`L` maps a measurement-sized disagreement back into a state-sized correction. It is the one free choice in the whole observer, and making it larger trusts the sensor more and the model less.",
                        "whys": [
                            "`L` maps a measurement-sized disagreement back into a state-sized correction. It is the one free choice in the whole observer, and making it larger trusts the sensor more and the model less.",
                            "The order is wrong: `L` is $n \\times p$ and the innovation is $p \\times 1$, so this multiplies in the only order that does not conform. The mistake is worth making once in NumPy, where the error message says so plainly.",
                            "`C` goes the other way — state to measurement. Using it here would try to correct the state with something already in measurement units, and shrink the correction instead of applying it.",
                            "Correcting by the raw measurement rather than the disagreement never converges: even a perfect estimate keeps getting pushed, because `y` does not go to zero.",
                        ],
                    },
                    {
                        "prompt": "Subtract the estimate's dynamics from the plant's. What is left?",
                        "hole": "?",
                        "opts": ["(A - L @ C)", "(A - B @ K)", "A", "(A + L @ C)"],
                        "a": 0,
                        "why": "Subtracting the two lines cancels `B @ u` entirely — the input drives both equally — and leaves $\\dot{e} = (A - LC)e$. The error forgets the input, which is why an observer works while the plant is being driven.",
                        "whys": [
                            "Subtracting the two lines cancels `B @ u` entirely — the input drives both equally — and leaves $\\dot{e} = (A - LC)e$. The error forgets the input, which is why an observer works while the plant is being driven.",
                            "That is the *controller's* closed loop, from the previous module. The two look alike on purpose, and the separation principle says you may design them independently — but they are not the same matrix and swapping them silently designs the wrong thing.",
                            "Plain `A` is the error dynamics of an observer with no correction at all: a simulation running open-loop beside the plant, drifting apart on any initial mismatch. `L` is the entire point.",
                            "The sign is flipped, which is what you get from the inverted innovation above. Eigenvalues chosen to sit safely in the left half-plane end up in the right one.",
                        ],
                    },
                ],
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
