"""CTRL530 — Non-Linear and Sliding-Mode Control.

Follows CTRL510 exactly. Authoring rules, unchanged:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

Two notes specific to this course, both learned the hard way from the checker:

  * `lambda` is the natural symbol for a sliding-surface slope and a Python
    keyword. MathCheck rewrites it to `lambda_` before handing it to SymPy, so
    `vars` must list *both* spellings, or the symbol is split letter by letter and
    every answer containing it is compared against nonsense. Module 4 lists both.
  * SymPy compares without sign assumptions, so a symbol moved across a square root
    is not recognised: x_0/sqrt(1 + 2 x_0^2 t) and 1/sqrt(1/x_0^2 + 2t) are equal
    only for x_0 > 0, and the checker will not grant that. Answers here keep the
    symbols they divide by out of the radicand, and where a root is unavoidable
    (M1 step 3) the hint asks for a single root rather than a ratio of two.
"""

COURSE = {
    "id": "CTRL530",
    "title": "Non-Linear and Sliding-Mode Control",
    "band": 2,
    "level": "Expert",
    "prereqs": ["CTRL510"],
    "stack": ["Python", "NumPy"],
    "credits": 12,
    "hours": 150,
    "icon": "◉",
    "summary": (
        "Every plant worth controlling is non-linear somewhere, and the linear machinery "
        "of CTRL510 works only in the neighbourhood where you pretended otherwise. This "
        "course takes the pretence away. It builds the local theory and marks its edge, "
        "proves stability with Lyapunov functions rather than eigenvalues, meets the "
        "behaviour that has no linear counterpart at all, and finishes with a controller "
        "that treats the non-linearity as a bounded disturbance and switches hard enough "
        "to beat it."
    ),
    "outcomes": [
        "Locate the equilibria of a non-linear system, linearise at each, and state precisely when the linearisation decides nothing.",
        "Certify stability with a Lyapunov function, and use LaSalle when the derivative is only negative semi-definite.",
        "Recognise a limit cycle as an isolated closed orbit, and explain why no linear field has one.",
        "Design a sliding-mode controller with a reaching-time guarantee, and price the boundary layer that removes its chatter.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that holds an uncertain pendulum upright with a switching law and measures what the boundary layer costs.",
    "reading": [
        "*Applied Nonlinear Control*, Slotine & Li — chapters 3 and 7 are the direct source for modules 2 and 4.",
        "*Nonlinear Systems*, Khalil — Lyapunov theory and LaSalle done carefully.",
        "*Sliding Mode Control in Electro-Mechanical Systems*, Utkin, Guldner & Shi — chatter treated as an engineering problem rather than an embarrassment.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Equilibria, linearisation and when it lies",
            "summary": "Freeze the system where it stands still, take the Jacobian, read off the local behaviour — except in the one case where the Jacobian says nothing at all.",
            "concepts": [
                "An equilibrium is a root of $f(x) = 0$. A non-linear system may have none, one, or infinitely many, and they need not resemble one another.",
                "The linearisation is the Jacobian $A = \\partial f/\\partial x$ evaluated *at* an equilibrium — a different matrix at each one.",
                "Hartman–Grobman: where no eigenvalue lies on the imaginary axis, the non-linear flow near the equilibrium is a continuous deformation of the linear one.",
                "*Hyperbolic* is the entire condition. One eigenvalue on the axis and the linearisation decides nothing; the terms you discarded now settle the question.",
                "The conclusion is local, and nothing inside the linearisation tells you how far it reaches.",
            ],
            "sandbox": {
                "title": "One pendulum, two equilibria, two different matrices",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": 0, "a12": 1, "a21": 3, "a22": -0.3},
                "brief": r'''
A pendulum has two equilibria: hanging down and standing up. It is one system, but
the linearisation is a different matrix at each, and the two matrices do not look
alike.

What is drawn is the **upright** one, with $x_1$ the angle from vertical and $x_2$
the angular rate. Gravity pulls the pendulum *away* from upright, so the $a_{21}$
entry is positive — the opposite sign to every spring in CTRL510.
''',
                "notice": [
                    "With $a_{21} > 0$ the origin is a saddle. Exactly two trajectories arrive at it and everything else leaves. That is why balancing a pole needs continuous correction rather than a good initial push.",
                    "Drag $a_{21}$ to $-3$: now you are linearising at the hanging equilibrium instead. The saddle becomes a stable spiral, and the only thing bringing it in is the damping in $a_{22}$.",
                    "Keep $a_{21}$ negative and set $a_{22}$ to exactly zero. The eigenvalues land on the imaginary axis and the orbits close. This is the one picture you may not trust: the linearisation is non-hyperbolic, and the discarded terms — a little dry friction, a little air — decide what really happens.",
                ],
            },
            "derive": {
                "title": "Linearising a pendulum, and one system where it lies",
                "minutes": 15,
                "vars": ["x", "x_1", "x_2", "x_0", "b", "c", "g", "l", "t", "y", "V"],
                "brief": r'''
The damped pendulum, with $x_1$ the angle from *hanging* and $x_2 = \dot{x_1}$:

$$\dot{x_1} = x_2, \qquad \dot{x_2} = -\frac{g}{l}\sin x_1 - b\, x_2$$

Its equilibria are $x_2 = 0$ together with $\sin x_1 = 0$, so $x_1 = 0$ (hanging)
and $x_1 = \pi$ (upright). The linearisation is the Jacobian

$$A = \begin{bmatrix} 0 & 1 \\ \partial f_2/\partial x_1 & \partial f_2/\partial x_2 \end{bmatrix}$$

evaluated at whichever equilibrium you care about. Only the bottom-left entry moves.
''',
                "steps": [
                    {
                        "prompt": "Differentiate $f_2 = -\\frac{g}{l}\\sin x_1 - b x_2$ with respect to $x_1$ and evaluate it at the hanging equilibrium $x_1 = 0$.",
                        "answer": "-\\frac{g}{l}",
                        "hint": "The derivative of $\\sin x_1$ is $\\cos x_1$, and $\\cos 0 = 1$.",
                        "deconstruct": [
                            "$\\partial f_2/\\partial x_1 = -\\frac{g}{l}\\cos x_1$.",
                            "At $x_1 = 0$ the cosine is $1$.",
                        ],
                    },
                    {
                        "prompt": "Now the same entry at the upright equilibrium $x_1 = \\pi$.",
                        "answer": "\\frac{g}{l}",
                        "hint": "$\\cos \\pi = -1$, and that single sign is the whole difference between the two equilibria.",
                        "deconstruct": [
                            "The same expression $-\\frac{g}{l}\\cos x_1$ is evaluated at $x_1 = \\pi$.",
                            "$\\cos \\pi = -1$, so the two minus signs cancel.",
                        ],
                    },
                    {
                        "prompt": "Set $b = 0$. The upright Jacobian is then $\\begin{bmatrix} 0 & 1 \\\\ g/l & 0 \\end{bmatrix}$, whose eigenvalues are real and opposite in sign. Write the positive one.",
                        "answer": "\\sqrt{\\frac{g}{l}}",
                        "hint": "The characteristic polynomial is $s^2 - g/l$. Keep the answer as one square root rather than a ratio of two.",
                        "deconstruct": [
                            "Trace is $0$ and determinant is $-g/l$, so the polynomial is $s^2 - g/l = 0$.",
                            "The roots are $\\pm\\sqrt{g/l}$, and the positive one is the rate at which the pendulum falls away from vertical.",
                        ],
                    },
                    {
                        "prompt": "Now a system where all of this fails. Take the scalar $\\dot{x} = -x^3$. Write its linearisation at the origin — that is, $\\mathrm{d}f/\\mathrm{d}x$ evaluated at $x = 0$.",
                        "answer": "0",
                        "hint": "$\\mathrm{d}(-x^3)/\\mathrm{d}x = -3x^2$, and you are asked for its value at $x = 0$.",
                        "deconstruct": [
                            "The derivative of $-x^3$ is $-3x^2$.",
                            "At $x = 0$ that is $0$, so the linearised system is $\\dot{x} = 0$ and predicts nothing at all.",
                        ],
                    },
                    {
                        "prompt": "Solve the true system. The substitution $y = x^{-2}$ turns $\\dot{x} = -x^3$ into $\\dot{y} = 2$. Write $y(t)$ in terms of $x_0 = x(0)$ and $t$.",
                        "given": "Check the substitution first: $\\dot{y} = -2x^{-3}\\dot{x} = -2x^{-3}(-x^3) = 2$.",
                        "answer": "\\frac{1}{x_0^2} + 2 t",
                        "hint": "$\\dot{y} = 2$ is a straight line in $t$. Its intercept is $y(0)$, which is $x_0^{-2}$.",
                        "deconstruct": [
                            "Integrating $\\dot{y} = 2$ gives $y(t) = y(0) + 2t$.",
                            "And $y(0) = x(0)^{-2} = 1/x_0^2$.",
                        ],
                    },
                ],
                "closing": r'''
Undo the substitution and $x(t) = x_0/\sqrt{1 + 2x_0^2 t}$. The origin *is* asymptotically
stable, and the linearisation had no way of knowing: it returned zero and left the
question open.

Notice how the state decays. Not $e^{-\alpha t}$ but $t^{-1/2}$ — so slow that two
starts a factor of five apart end up within two per cent of each other. A linear
system cannot decay that way, which is exactly why the linear machinery could not
predict it.
''',
            },
            "quiz": {
                "title": "When the linearisation is telling the truth",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What is an equilibrium of $\\dot{x} = f(x)$?",
                        "opts": ["A root of $f(x) = 0$", "A point where $x = 0$", "A closed orbit", "A point where $f$ is not differentiable"],
                        "a": 0,
                        "why": r"""
Where the vector field vanishes, the state stops moving. The origin is only an
equilibrium if $f(0) = 0$, which is a modelling choice rather than a fact — most systems
are written with the coordinates shifted so that the operating point sits at zero, and
forgetting that shift is how a correct analysis gets applied at the wrong place.
""",
                    },
                    {
                        "q": "The Jacobian $\\partial f/\\partial x$ is evaluated where?",
                        "opts": [
                            "At the equilibrium being examined",
                            "At the origin, always",
                            "Averaged over the state space",
                            "At the initial condition",
                        ],
                        "a": 0,
                        "why": r"""
*At* the equilibrium, and a system with several equilibria has a different Jacobian —
and possibly a completely different character — at each. A pendulum is a spiral at the
bottom and a saddle at the top, from one $f$. Evaluating at the origin out of habit
gives an answer about a point you were not asking about.
""",
                    },
                    {
                        "q": "Hartman–Grobman says the linearisation describes the local behaviour under what condition?",
                        "opts": [
                            "No eigenvalue lies on the imaginary axis",
                            "All eigenvalues are real",
                            "The system is second order",
                            "The non-linearity is small",
                        ],
                        "a": 0,
                        "why": r"""
Hyperbolicity. Away from the imaginary axis the non-linear flow is a continuous
deformation of the linear one, so stability, instability and the saddle structure all
carry across. It is a strong result and it has one exact gap — the imaginary axis —
which is precisely where the interesting behaviour of this course lives. The size of the
non-linearity is irrelevant.
""",
                    },
                    {
                        "q": "The Jacobian has a purely imaginary pair. What may you conclude?",
                        "opts": [
                            "Nothing — the non-linear terms decide, and they can go either way",
                            "The system is stable",
                            "The system is unstable",
                            "There is a limit cycle",
                        ],
                        "a": 0,
                        "why": r"""
This is the one case linearisation cannot answer, and the classic demonstration is
$\dot{x} = -y + ax(x^2+y^2)$, $\dot{y} = x + ay(x^2+y^2)$: identical linearisation for
every $a$, and the origin is attracting for $a<0$, repelling for $a>0$ and a centre at
$a=0$. That is exactly why Lyapunov's direct method exists — it needs no linearisation
and works here.
""",
                    },
                    {
                        "q": "How many equilibria can a non-linear system have?",
                        "opts": [
                            "Any number, including none and infinitely many",
                            "Exactly one",
                            "At most one per state",
                            "Always an odd number",
                        ],
                        "a": 0,
                        "why": r"""
$\dot{x} = 1 + x^2$ has none; a pendulum has infinitely many, one per full turn. That is
the first genuine departure from linear systems, where $Ax = 0$ has either the origin
alone or a whole subspace. It also means "the" equilibrium is a phrase to be suspicious
of, and that a global claim needs more than a local argument.
""",
                    },
                ],
            },
            "lab": {
                "title": "Linearise anything, and know when not to believe it",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Three functions. Two vector fields are already written for you.

`jacobian(f, x0, h)` returns the Jacobian of the field `f` at `x0` by **central
differences**: column `j` is

```text
(f(x0 + h*e_j) - f(x0 - h*e_j)) / (2*h)
```

Central differences, not forward — the error is $O(h^2)$ rather than $O(h)$, and the
checks are tight enough to notice.

`verdict(J, tol)` reads the eigenvalues of `J` and returns one of

```text
"asymptotically stable"    "unstable"    "inconclusive"
```

Let $m$ be the largest real part. Return `"asymptotically stable"` when $m < -tol$,
`"unstable"` when $m > tol$, and `"inconclusive"` otherwise — that last case is the
non-hyperbolic one, where the linearisation genuinely has nothing to say.

`flow(f, x0, dt, steps)` forward-Eulers the field and returns the **final state** as
a numpy array.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

G_OVER_L = 19.62          # g/l for a 0.5 m pendulum, in 1/s^2


def pendulum(x, b=0.2):
    """theta'' = -(g/l) sin(theta) - b theta'.  States are [theta, theta_dot]."""
    x = np.asarray(x, dtype=float)
    return np.array([x[1], -G_OVER_L * np.sin(x[0]) - b * x[1]])


def cubic(x):
    """The scalar system x' = -x**3, written as a one-dimensional field."""
    x = np.asarray(x, dtype=float)
    return np.array([-x[0] ** 3])


def jacobian(f, x0, h=1e-5):
    """Central-difference Jacobian of the field f at x0."""
    x0 = np.asarray(x0, dtype=float)
    n = x0.size
    # TODO: perturb one coordinate at a time, forwards and backwards.
    return np.zeros((n, n))


def verdict(J, tol=1e-8):
    """What the linearisation J is entitled to conclude about the equilibrium."""
    J = np.asarray(J, dtype=float)
    # TODO: largest real part of the eigenvalues, then the three cases.
    return "unknown"


def flow(f, x0, dt, steps):
    """Forward-Euler the field and return the final state."""
    x = np.array(x0, dtype=float)
    # TODO: step x forward `steps` times.
    return x


if __name__ == "__main__":
    for name, point in (("hanging", [0.0, 0.0]), ("upright", [np.pi, 0.0])):
        J = jacobian(pendulum, point)
        print(f"{name}: J = {np.round(J, 4).tolist()}  ->  {verdict(J)}")
    print("cubic at 0:", verdict(jacobian(cubic, [0.0])))
    print("cubic from x=1 after 20 s:", np.round(flow(cubic, [1.0], 1e-3, 20000), 6).tolist())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

G_OVER_L = 19.62          # g/l for a 0.5 m pendulum, in 1/s^2


def pendulum(x, b=0.2):
    """theta'' = -(g/l) sin(theta) - b theta'.  States are [theta, theta_dot]."""
    x = np.asarray(x, dtype=float)
    return np.array([x[1], -G_OVER_L * np.sin(x[0]) - b * x[1]])


def cubic(x):
    """The scalar system x' = -x**3, written as a one-dimensional field."""
    x = np.asarray(x, dtype=float)
    return np.array([-x[0] ** 3])


def jacobian(f, x0, h=1e-5):
    """Central-difference Jacobian of the field f at x0."""
    x0 = np.asarray(x0, dtype=float)
    n = x0.size
    f0 = np.asarray(f(x0), dtype=float)
    J = np.zeros((f0.size, n))
    for j in range(n):
        e = np.zeros(n)
        e[j] = h
        forward = np.asarray(f(x0 + e), dtype=float)
        back = np.asarray(f(x0 - e), dtype=float)
        J[:, j] = (forward - back) / (2.0 * h)
    return J


def verdict(J, tol=1e-8):
    """What the linearisation J is entitled to conclude about the equilibrium."""
    J = np.asarray(J, dtype=float)
    m = float(np.max(np.real(np.linalg.eigvals(J))))
    if m < -tol:
        return "asymptotically stable"
    if m > tol:
        return "unstable"
    return "inconclusive"


def flow(f, x0, dt, steps):
    """Forward-Euler the field and return the final state."""
    x = np.array(x0, dtype=float)
    for _ in range(steps):
        x = x + dt * np.asarray(f(x), dtype=float)
    return x


if __name__ == "__main__":
    for name, point in (("hanging", [0.0, 0.0]), ("upright", [np.pi, 0.0])):
        J = jacobian(pendulum, point)
        print(f"{name}: J = {np.round(J, 4).tolist()}  ->  {verdict(J)}")
    print("cubic at 0:", verdict(jacobian(cubic, [0.0])))
    print("cubic from x=1 after 20 s:", np.round(flow(cubic, [1.0], 1e-3, 20000), 6).tolist())
'''}],
                "hints": [
                    "Build the perturbation vector with `e = np.zeros(n); e[j] = h` — do not mutate `x0` itself, or later columns are taken at the wrong point.",
                    "`np.linalg.eigvals` returns complex numbers even for a real matrix; wrap it in `np.real` before taking the maximum.",
                    "The three cases in `verdict` must be tested in the order stable, unstable, inconclusive — `inconclusive` is what is left when neither strict inequality holds, not a case of its own.",
                    "`flow` needs no history, only the final state, so a single accumulating variable is enough.",
                ],
                "tests": [
                    {"name": "the Jacobian of a linear field is the matrix itself", "code": r'''
import numpy as np
_A = np.array([[-1.0, 2.0], [0.5, -3.0]])
_J = jacobian(lambda x: _A @ x, [1.0, -2.0])
assert _J.shape == (2, 2), f"the Jacobian of a 2-state field is 2x2, got {_J.shape}"
assert np.abs(_J - _A).max() < 1e-8, \
    f"for f(x) = Ax the Jacobian is A everywhere; got {_J.tolist()} instead of {_A.tolist()}"
'''},
                    {"name": "the hanging pendulum linearises to a damped spring", "code": r'''
import numpy as np
_J = jacobian(pendulum, [0.0, 0.0])
assert abs(_J[0, 0]) < 1e-8 and abs(_J[0, 1] - 1.0) < 1e-8, \
    f"the top row is d(x2)/dx = [0, 1] whatever the plant; got {_J[0].tolist()}"
assert abs(_J[1, 0] + 19.62) < 1e-6, \
    f"at the hanging equilibrium cos(0) = 1, so the entry is -g/l = -19.62; got {_J[1,0]}"
assert abs(_J[1, 1] + 0.2) < 1e-8, f"the damping entry is -b = -0.2; got {_J[1,1]}"
'''},
                    {"name": "the upright pendulum linearises to a saddle", "code": r'''
import numpy as np
_J = jacobian(pendulum, [np.pi, 0.0])
assert abs(_J[1, 0] - 19.62) < 1e-6, \
    f"at x1 = pi the cosine flips sign, so the entry is +g/l = +19.62; got {_J[1,0]}"
assert np.linalg.det(_J) < 0, \
    "a positive bottom-left entry makes the determinant negative — that is the saddle"
'''},
                    {"name": "the Jacobian is right for a genuinely non-linear field", "code": r'''
import numpy as np
def _g(x):
    return np.array([x[0] * x[1], np.sin(x[0]) + x[1] ** 2])
_J = jacobian(_g, [1.0, 2.0])
_want = np.array([[2.0, 1.0], [np.cos(1.0), 4.0]])
assert np.abs(_J - _want).max() < 1e-6, \
    f"expected [[x2, x1], [cos x1, 2 x2]] = {np.round(_want, 6).tolist()}, got {np.round(_J, 6).tolist()}"
'''},
                    {"name": "the verdict follows the eigenvalues", "code": r'''
import numpy as np
_hang = verdict(jacobian(pendulum, [0.0, 0.0]))
assert _hang == "asymptotically stable", \
    f"a damped pendulum hanging down settles; got {_hang!r}"
_up = verdict(jacobian(pendulum, [np.pi, 0.0]))
assert _up == "unstable", \
    f"one eigenvalue of a saddle is in the right half-plane, so the equilibrium is unstable; got {_up!r}"
'''},
                    {"name": "an undamped pendulum is the case linearisation cannot decide", "code": r'''
import numpy as np
_J = jacobian(lambda x: pendulum(x, 0.0), [0.0, 0.0])
_ev = np.linalg.eigvals(_J)
assert abs(float(np.max(np.real(_ev)))) < 1e-8, "with b = 0 the eigenvalues are purely imaginary"
_v = verdict(_J)
assert _v == "inconclusive", \
    f"eigenvalues on the imaginary axis are non-hyperbolic: the linearisation decides nothing, so the answer is 'inconclusive', not a guess. Got {_v!r}"
'''},
                    {"name": "the cubic is stable and the linearisation cannot see it", "code": r'''
import numpy as np
_J = jacobian(cubic, [0.0])
assert _J.shape == (1, 1), f"a one-state field has a 1x1 Jacobian, got {_J.shape}"
assert abs(_J[0, 0]) < 1e-8, f"d(-x**3)/dx is -3x**2, which vanishes at the origin; got {_J[0,0]}"
assert verdict(_J) == "inconclusive", \
    "a zero linearisation is the definition of non-hyperbolic — reporting stability here would be a claim the Jacobian does not support"
_end = flow(cubic, [1.0], 1e-3, 20000)
assert abs(float(_end[0]) - 0.156163) < 1e-4, \
    f"x' = -x**3 from x = 1 reaches about 0.1562 after 20 s; got {float(_end[0]):.6f}"
'''},
                    {"name": "the cubic decays algebraically, not exponentially", "code": r'''
import numpy as np
_a = float(flow(cubic, [1.0], 1e-3, 20000)[0])
_b = float(flow(cubic, [5.0], 1e-3, 20000)[0])
assert 0.9 < _b / _a < 1.1, \
    f"two starts a factor of five apart end within a few per cent of each other ({_a:.5f} vs {_b:.5f}) — an exponential decay would have preserved the ratio of 5. Check that flow returns the final state, not the first."
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Lyapunov's direct method",
            "summary": "Find a scalar that falls along every trajectory and stability is proved, without solving anything and without linearising.",
            "concepts": [
                "$V$ positive definite with $V(0) = 0$, and $\\dot{V} = \\nabla V \\cdot f$ negative definite, gives asymptotic stability — globally, if $V$ is also radially unbounded.",
                "$\\dot{V}$ is taken *along the trajectories*, so the vector field enters the argument without ever being integrated.",
                "Negative *semi*-definite $\\dot{V}$ gives stability only. LaSalle recovers the asymptotic part when the largest invariant set inside $\\{\\dot{V} = 0\\}$ is the origin alone.",
                "For a linear system $V = x^\\top P x$ works exactly when $A^\\top P + PA = -Q$ has a positive definite solution $P$, for some — equivalently every — positive definite $Q$.",
                "Failing to find a $V$ proves nothing whatsoever. The condition is sufficient, never necessary, and a badly chosen $V$ fails on stable systems.",
            ],
            "sandbox": {
                "title": "Does every trajectory cross the circles inwards",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": -0.3, "a12": 1, "a21": -2, "a22": -0.3},
                "brief": r'''
Picture the level sets of $V = x_1^2 + x_2^2$ — concentric circles about the origin.
$\dot{V} < 0$ means every trajectory crosses every circle *inwards*, and if that
holds everywhere, the origin attracts everything.

The whole method is in that sentence. You never solve for $x(t)$; you only ask which
way the trajectories cut the level sets.
''',
                "notice": [
                    "As drawn, every trajectory spirals inwards across every circle, so $V = x_1^2 + x_2^2$ is a valid Lyapunov function and $\\dot{V} < 0$ away from the origin.",
                    "Set $a_{11}$ and $a_{22}$ both to zero. The orbits become the circles themselves: $\\dot{V} = 0$ everywhere, so $V$ still proves stability but no longer proves *asymptotic* stability. That distinction is the entire content of LaSalle.",
                    "Now set $a_{12} = 3$ and $a_{21} = -0.2$, keeping $a_{11} = a_{22} = -0.3$. The origin still attracts everything, but trajectories starting near the diagonal bulge *outwards* across the circles first. The circle was the wrong $V$; the right one is a stretched ellipse, and the next lab computes it.",
                ],
            },
            "derive": {
                "title": "Proving stability without solving",
                "minutes": 14,
                "vars": ["V", "x_1", "x_2", "k", "b", "c", "g", "l", "t"],
                "brief": r'''
A unit mass on a spring with damping, written as a field:

$$\dot{x_1} = x_2, \qquad \dot{x_2} = -k x_1 - b x_2 \qquad (k > 0,\ b > 0)$$

Take the obvious candidate — the energy:

$$V = \tfrac{1}{2}k x_1^2 + \tfrac{1}{2}x_2^2$$

and compute $\dot{V} = \dfrac{\partial V}{\partial x_1}\dot{x_1} + \dfrac{\partial V}{\partial x_2}\dot{x_2}$.
''',
                "steps": [
                    {
                        "prompt": "Start with the two partial derivatives. Write $\\partial V/\\partial x_1$.",
                        "answer": "k x_1",
                        "hint": "Differentiate $\\tfrac{1}{2}k x_1^2$ and treat $x_2$ as a constant.",
                        "deconstruct": [
                            "The $x_2$ term does not involve $x_1$, so it contributes nothing.",
                            "$\\mathrm{d}(\\tfrac{1}{2}k x_1^2)/\\mathrm{d}x_1 = k x_1$.",
                        ],
                    },
                    {
                        "prompt": "Now assemble $\\dot{V}$ and simplify it as far as it will go.",
                        "given": "$\\partial V/\\partial x_2 = x_2$, and the field is $\\dot{x_1} = x_2$, $\\dot{x_2} = -k x_1 - b x_2$.",
                        "answer": "-b x_2^2",
                        "hint": "Two terms carry $k x_1 x_2$ with opposite signs. Everything the spring stores, it gives back.",
                        "deconstruct": [
                            "$\\dot{V} = (k x_1)(x_2) + (x_2)(-k x_1 - b x_2)$.",
                            "Expand: $k x_1 x_2 - k x_1 x_2 - b x_2^2$, and the first two cancel.",
                        ],
                    },
                    {
                        "prompt": "$\\dot{V} = -b x_2^2$ vanishes on the whole line $x_2 = 0$, not just at the origin — so it is negative *semi*-definite and asymptotic stability is not yet proved. On that line, write $\\dot{x_2}$.",
                        "answer": "-k x_1",
                        "hint": "Put $x_2 = 0$ into $\\dot{x_2} = -k x_1 - b x_2$ and see what is left.",
                        "deconstruct": [
                            "The damping term $-b x_2$ is zero on this line.",
                            "What remains is the spring force, $-k x_1$.",
                        ],
                    },
                    {
                        "prompt": "Now the same $V$ idea on a genuinely non-linear plant: the pendulum $\\dot{x_1} = x_2$, $\\dot{x_2} = -\\frac{g}{l}\\sin x_1 - c\\, x_2$, with the true energy $V = \\frac{g}{l}(1 - \\cos x_1) + \\tfrac{1}{2}x_2^2$. Write $\\dot{V}$.",
                        "answer": "-c x_2^2",
                        "hint": "$\\partial V/\\partial x_1 = \\frac{g}{l}\\sin x_1$. The same cancellation happens, and the sine never survives it.",
                        "deconstruct": [
                            "$\\dot{V} = \\left(\\frac{g}{l}\\sin x_1\\right)(x_2) + (x_2)\\left(-\\frac{g}{l}\\sin x_1 - c x_2\\right)$.",
                            "The two sine terms cancel exactly, leaving $-c x_2^2$.",
                        ],
                    },
                ],
                "closing": r'''
Step 3 is LaSalle in miniature. On the line $x_2 = 0$ the state is not standing still
unless $x_1 = 0$ too — $\dot{x_2} = -k x_1$ pushes it straight off the line again. So
the *largest invariant set* inside $\{\dot{V} = 0\}$ is the origin alone, and a
semi-definite $\dot{V}$ still delivers asymptotic stability.

Step 4 is the reason the method matters. The linear system and the pendulum gave the
same answer, $\dot{V} = -(\text{damping})x_2^2$, and the pendulum was never
linearised, never restricted to small angles, and never solved. Lyapunov's method does
not care that $\sin x_1$ is not $x_1$.
''',
            },
            "blanks": {
                "title": "Lyapunov, without solving anything",
                "minutes": 9,
                "caption": "the direct method, condition by condition",
                "lang": "text",
                "brief": r"""
The remarkable thing about the direct method is what it does not require: no solution, no
linearisation, no eigenvalues. Find one scalar that falls, and stability is proved. Fill
in the conditions it has to satisfy.
""",
                "listing": """A candidate V(x), with V(0) = 0.

  V(x) > 0 for every x != 0            --  V must be ___

  Vdot = ___                           --  the rate along the trajectories,
                                           which is where f enters the argument

If Vdot is negative DEFINITE, the origin is ___ .

If Vdot is only negative SEMI-definite, you may conclude ___ ,

and ___ recovers the stronger result
by examining where the trajectories can remain with Vdot = 0.
""",
                "blanks": [
                    {
                        "prompt": "What must V itself be?",
                        "hole": "?",
                        "opts": ["positive definite", "negative definite", "bounded", "linear"],
                        "a": 0,
                        "why": "Positive everywhere except at the origin, where it is zero — an energy-like quantity, so that 'V is decreasing' means 'the state is heading home'. Without positive definiteness a falling V says nothing about where the state is going.",
                        "whys": [
                            "Positive everywhere except at the origin, where it is zero — an energy-like quantity, so that 'V is decreasing' means 'the state is heading home'. Without positive definiteness a falling V says nothing about where the state is going.",
                            "A negative definite $V$ would be unbounded below and a decreasing one would prove nothing at all.",
                            "Boundedness is not enough on its own — a bounded function that never approaches zero cannot certify convergence to the origin.",
                            "Linearity would restrict the method to exactly the systems it was invented to avoid needing.",
                        ],
                    },
                    {
                        "prompt": "The derivative is taken along the trajectories.",
                        "hole": "?",
                        "opts": ["grad(V) . f(x)", "grad(V)", "f(x)", "the partial derivative of V with respect to time"],
                        "a": 0,
                        "why": "The chain rule: $\\dot{V} = \\nabla V \\cdot \\dot{x} = \\nabla V \\cdot f(x)$. This is the step where the dynamics enter — without $f$ you are differentiating a function of position with no knowledge of how position changes, and the whole argument is empty.",
                        "whys": [
                            "The chain rule: $\\dot{V} = \\nabla V \\cdot \\dot{x} = \\nabla V \\cdot f(x)$. This is the step where the dynamics enter — without $f$ you are differentiating a function of position with no knowledge of how position changes, and the whole argument is empty.",
                            "The gradient alone is a vector, not a rate, and it says nothing about which way the state is actually moving.",
                            "The vector field alone is also a vector, and it is not a rate of change of $V$.",
                            "$V$ has no explicit time dependence — all of its variation comes through $x(t)$, which is exactly why the chain rule is needed.",
                        ],
                    },
                    {
                        "prompt": "Negative definite Vdot gives what?",
                        "hole": "?",
                        "opts": [
                            "asymptotic stability",
                            "stability, but possibly without convergence",
                            "instability",
                            "a guaranteed limit cycle",
                        ],
                        "a": 0,
                        "why": "$V$ strictly decreases everywhere except the origin, so it is squeezed down to zero and the state with it. Note this is a *local* conclusion unless $V$ is also radially unbounded — a technicality that matters, because a $V$ that flattens out far away leaves room for trajectories to escape.",
                        "whys": [
                            "$V$ strictly decreases everywhere except the origin, so it is squeezed down to zero and the state with it. Note this is a *local* conclusion unless $V$ is also radially unbounded — a technicality that matters, because a $V$ that flattens out far away leaves room for trajectories to escape.",
                            "That is the weaker semi-definite case, which is the next blank. Strict decrease gives the stronger conclusion.",
                            "A decreasing energy is the opposite of instability.",
                            "Limit cycles are excluded by this, not implied — a trajectory on a closed orbit would return $V$ to its starting value.",
                        ],
                    },
                    {
                        "prompt": "And if Vdot is only negative semi-definite?",
                        "hole": "?",
                        "opts": [
                            "stability only, with no promise of convergence",
                            "asymptotic stability anyway",
                            "instability",
                            "nothing whatsoever",
                        ],
                        "a": 0,
                        "why": "$V$ never grows, so the state stays near the origin — but it might settle on a level set and circle there forever. An undamped pendulum is exactly this case: energy is conserved, $\\dot{V} = 0$ everywhere, and it is stable without ever converging.",
                        "whys": [
                            "$V$ never grows, so the state stays near the origin — but it might settle on a level set and circle there forever. An undamped pendulum is exactly this case: energy is conserved, $\\dot{V} = 0$ everywhere, and it is stable without ever converging.",
                            "That claim needs strict decrease, or LaSalle's extra argument. Asserting it from a semi-definite $\\dot{V}$ is the most common error in a Lyapunov proof.",
                            "A non-increasing energy cannot certify instability.",
                            "Stability itself is a real and useful conclusion — a bounded response is often all that was needed.",
                        ],
                    },
                    {
                        "prompt": "What recovers asymptotic stability from a semi-definite Vdot?",
                        "hole": "?",
                        "opts": [
                            "LaSalle's invariance principle",
                            "Hartman-Grobman",
                            "linearising at the origin",
                            "the reaching condition",
                        ],
                        "a": 0,
                        "why": "LaSalle asks where a trajectory could *stay* while $\\dot{V} = 0$, and if the only such invariant set is the origin, convergence follows. It rescues the very common situation where a natural energy function has damping that vanishes on a surface — which is most mechanical systems, and why the method is worth knowing rather than reaching for a cleverer $V$.",
                        "whys": [
                            "LaSalle asks where a trajectory could *stay* while $\\dot{V} = 0$, and if the only such invariant set is the origin, convergence follows. It rescues the very common situation where a natural energy function has damping that vanishes on a surface — which is most mechanical systems, and why the method is worth knowing rather than reaching for a cleverer $V$.",
                            "Hartman-Grobman is about linearisation and needs hyperbolicity — precisely the assumption Lyapunov's method was chosen to avoid.",
                            "Linearising abandons the whole approach, and in the marginal cases where it is most needed it cannot decide.",
                            "The reaching condition belongs to sliding mode in module 4; it is a design requirement rather than an analysis tool.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Solve the Lyapunov equation and use what it gives you",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
For $\dot{x} = Ax$ and $V = x^\top P x$, the derivative along trajectories is
$\dot{V} = x^\top (A^\top P + PA) x$. Choosing $Q$ and solving

$$A^\top P + PA = -Q$$

turns the search for a Lyapunov function into a linear solve. Three functions.

`is_pos_def(M)` returns `True` when the symmetric part of `M` has all eigenvalues
strictly positive. Use `np.linalg.eigvalsh`, which is for symmetric matrices and
returns real values in ascending order.

`lyap(A, Q)` solves the equation above for `P`. The trick is that the unknown is a
matrix and the equation is linear in it, so flatten it. With **column-major** `vec`,
$\mathrm{vec}(AXB) = (B^\top \otimes A)\,\mathrm{vec}(X)$, so

```text
vec(A.T @ P + P @ A) = (kron(I, A.T) + kron(A.T, I)) @ vec(P)
```

Build that matrix with `np.kron`, solve against `-Q` flattened the same way, and
reshape. NumPy flattens row-major by default, so pass `order="F"` to both
`.flatten()` and `.reshape()`.

`v_trace(A, P, x0, dt, steps)` forward-Eulers $\dot{x} = Ax$ from `x0` and returns
the list of $V = x^\top P x$ values, one per step, recorded **before** each step.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def is_pos_def(M):
    """True when the symmetric part of M has strictly positive eigenvalues."""
    M = np.asarray(M, dtype=float)
    # TODO: symmetrise, then check the eigenvalues.
    return False


def lyap(A, Q):
    """Solve A.T @ P + P @ A = -Q for P."""
    A = np.asarray(A, dtype=float)
    Q = np.asarray(Q, dtype=float)
    n = A.shape[0]
    # TODO: build the Kronecker system, solve it, reshape column-major.
    return np.zeros((n, n))


def v_trace(A, P, x0, dt, steps):
    """V = x.T @ P @ x at every step of a forward-Euler run from x0."""
    A = np.asarray(A, dtype=float)
    P = np.asarray(P, dtype=float)
    x = np.array(x0, dtype=float).reshape(-1, 1)
    out = []
    # TODO: record V, then advance x, `steps` times.
    return out


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [-4.0, -0.4]])
    P = lyap(A, np.eye(2))
    print("P =", np.round(P, 6).tolist())
    print("residual:", float(np.abs(A.T @ P + P @ A + np.eye(2)).max()))
    print("positive definite:", is_pos_def(P))
    vs = v_trace(A, P, [1.0, 0.0], 0.001, 20000)
    print("V fell from", round(vs[0], 6), "to", round(vs[-1], 8))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def is_pos_def(M):
    """True when the symmetric part of M has strictly positive eigenvalues."""
    M = np.asarray(M, dtype=float)
    S = 0.5 * (M + M.T)
    return bool(np.all(np.linalg.eigvalsh(S) > 1e-12))


def lyap(A, Q):
    """Solve A.T @ P + P @ A = -Q for P."""
    A = np.asarray(A, dtype=float)
    Q = np.asarray(Q, dtype=float)
    n = A.shape[0]
    I = np.eye(n)
    M = np.kron(I, A.T) + np.kron(A.T, I)
    p = np.linalg.solve(M, -Q.flatten(order="F"))
    return p.reshape((n, n), order="F")


def v_trace(A, P, x0, dt, steps):
    """V = x.T @ P @ x at every step of a forward-Euler run from x0."""
    A = np.asarray(A, dtype=float)
    P = np.asarray(P, dtype=float)
    x = np.array(x0, dtype=float).reshape(-1, 1)
    out = []
    for _ in range(steps):
        out.append(float((x.T @ P @ x)[0, 0]))
        x = x + dt * (A @ x)
    return out


if __name__ == "__main__":
    A = np.array([[0.0, 1.0], [-4.0, -0.4]])
    P = lyap(A, np.eye(2))
    print("P =", np.round(P, 6).tolist())
    print("residual:", float(np.abs(A.T @ P + P @ A + np.eye(2)).max()))
    print("positive definite:", is_pos_def(P))
    vs = v_trace(A, P, [1.0, 0.0], 0.001, 20000)
    print("V fell from", round(vs[0], 6), "to", round(vs[-1], 8))
'''}],
                "hints": [
                    "`np.linalg.eigvalsh` assumes symmetry and returns real eigenvalues; `np.linalg.eigvals` does not and returns complex ones. For a definiteness test you want the first.",
                    "The two Kronecker products are not interchangeable: `np.kron(I, A.T)` handles the $A^\\top P$ term and `np.kron(A.T, I)` the $PA$ term.",
                    "Every flatten and every reshape in `lyap` needs `order=\"F\"`. Mixing the two conventions gives a matrix that is wrong but not obviously wrong — check the residual, not the shape.",
                    "`v_trace` records before stepping, so the first entry is $V$ at `x0` and the list has exactly `steps` entries.",
                ],
                "tests": [
                    {"name": "P actually solves the Lyapunov equation", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_Q = np.eye(2)
_P = lyap(_A, _Q)
assert _P.shape == (2, 2), f"P has the shape of A, got {_P.shape}"
_res = float(np.abs(_A.T @ _P + _P @ _A + _Q).max())
assert _res < 1e-9, \
    f"A.T @ P + P @ A + Q should be zero, largest entry is {_res:.3e} — the usual cause is a row-major flatten where a column-major one was needed"
'''},
                    {"name": "P is symmetric, as any P defining a quadratic form must be", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_P = lyap(_A, np.eye(2))
assert np.abs(_P - _P.T).max() < 1e-10, \
    f"x.T P x only sees the symmetric part of P, and the Lyapunov solution is symmetric; got {_P.tolist()}"
assert abs(_P[0, 0] - 6.3) < 1e-9 and abs(_P[1, 1] - 1.5625) < 1e-9, \
    f"expected P = [[6.3, 0.125], [0.125, 1.5625]], got {np.round(_P, 6).tolist()}"
'''},
                    {"name": "a stable A gives a positive definite certificate", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_P = lyap(_A, np.eye(2))
assert is_pos_def(_P), \
    "for a stable A the solution is positive definite, which is what makes V a valid Lyapunov function"
_A3 = np.array([[-1.0, 2.0], [0.0, -3.0]])
_P3 = lyap(_A3, np.eye(2))
assert is_pos_def(_P3), f"this A is stable too, so P should be positive definite; got {_P3.tolist()}"
assert float(np.abs(_A3.T @ _P3 + _P3 @ _A3 + np.eye(2)).max()) < 1e-9
'''},
                    {"name": "an unstable A gives a solution that certifies nothing", "code": r'''
import numpy as np
_A = np.array([[1.0, 0.0], [0.0, 2.0]])
_P = lyap(_A, np.eye(2))
assert not is_pos_def(_P), \
    f"the linear solve still returns a P here, but it is not positive definite, so it is not a Lyapunov function — that is how the method reports instability, not by failing. Got {_P.tolist()}"
assert abs(_P[0, 0] + 0.5) < 1e-9, f"2*P[0,0] = -1 gives P[0,0] = -0.5, got {_P[0,0]}"
'''},
                    {"name": "is_pos_def rejects the indefinite and the merely semi-definite", "code": r'''
import numpy as np
assert not is_pos_def(np.array([[1.0, 0.0], [0.0, -1.0]])), \
    "one negative eigenvalue is enough to disqualify a matrix"
assert not is_pos_def(np.array([[1.0, 0.0], [0.0, 0.0]])), \
    "positive *semi*-definite is not positive definite — V must be strictly positive away from the origin"
assert is_pos_def(np.array([[2.0, 1.0], [1.0, 2.0]])), \
    "eigenvalues 1 and 3 are both positive, so this one qualifies"
'''},
                    {"name": "it works beyond two states", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [-6.0, -11.0, -6.0]])
_P = lyap(_A, np.eye(3))
assert _P.shape == (3, 3), f"expected a 3x3 P, got {_P.shape} — nothing in the method is specific to n = 2"
assert float(np.abs(_A.T @ _P + _P @ _A + np.eye(3)).max()) < 1e-9
assert is_pos_def(_P), "poles at -1, -2, -3 are stable, so P is positive definite"
'''},
                    {"name": "V really does fall along the trajectory", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_P = lyap(_A, np.eye(2))
_vs = v_trace(_A, _P, [1.0, 0.0], 0.001, 20000)
assert len(_vs) == 20000, f"one V per step, recorded before stepping: expected 20000, got {len(_vs)}"
assert abs(_vs[0] - 6.3) < 1e-9, f"V at x0 = [1, 0] is P[0,0] = 6.3, got {_vs[0]}"
_rises = [n for n in range(len(_vs) - 1) if _vs[n + 1] > _vs[n] + 1e-15]
assert not _rises, \
    f"V is supposed to fall at every single step, and it rose first at step {_rises[0] if _rises else -1} — an oscillating V means the quadratic form, not the trajectory, is wrong"
assert _vs[-1] < 1e-2, f"after 20 s V should be near zero, got {_vs[-1]:.6f}"
'''},
                    {"name": "V decays at least as fast as the certificate promises", "code": r'''
import numpy as np
_A = np.array([[0.0, 1.0], [-4.0, -0.4]])
_Q = np.eye(2)
_P = lyap(_A, _Q)
_vs = v_trace(_A, _P, [1.0, 0.0], 0.001, 20000)
_alpha = float(np.min(np.linalg.eigvalsh(_Q)) / np.max(np.linalg.eigvalsh(_P)))
assert abs(_alpha - 0.1586471620866259) < 1e-9, \
    f"the guaranteed rate is lambda_min(Q)/lambda_max(P); expected 0.15865, got {_alpha}"
_worst = max(_vs[n] / (_vs[0] * np.exp(-_alpha * n * 0.001)) for n in range(0, 20000, 20))
assert _worst < 1.001, \
    f"the bound V(t) <= V(0) exp(-alpha t) is exceeded by a factor {_worst:.6f} — the certificate is not merely decorative, it is a rate"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Phase-plane behaviour and limit cycles",
            "summary": "An isolated closed orbit is something no linear system can produce, and it is the most common thing a non-linear one does.",
            "concepts": [
                "Nullclines — the curves where each component of $\\dot{x}$ changes sign — carve the plane into regions with a known flow direction.",
                "A limit cycle is an *isolated* periodic orbit: its neighbours spiral onto it or away from it, and there is no other closed orbit nearby.",
                "A linear system's closed orbits, when it has any, form a continuum. Perturb the trace and all of them vanish at once, which is why they are not limit cycles.",
                "Bendixson: if $\\nabla\\!\\cdot f$ has one strict sign throughout a simply connected region, no closed orbit lies wholly inside it.",
                "Poincaré–Bendixson: a trajectory that stays inside a bounded planar region containing no equilibrium must approach a closed orbit. This is a two-dimensional theorem and has no analogue in three.",
            ],
            "sandbox": {
                "title": "Hunting for a closed orbit in a linear field",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": 0, "a12": 1, "a21": -2, "a22": 0},
                "brief": r'''
Before the non-linear case, establish what the linear case cannot do. The matrix
here has zero trace and positive determinant — a centre, the only linear system with
periodic solutions at all.

The question to hold in mind is not "is there a closed orbit" but "is there an
*isolated* one".
''',
                "notice": [
                    "Every trajectory drawn is a closed orbit, and so is the one through any other point you might have picked. There is a closed orbit through *every* point, so not one of them is isolated, and not one of them is a limit cycle.",
                    "Nudge $a_{22}$ to $-0.05$. All the orbits open at once and spiral in together. A continuum of cycles is destroyed by an arbitrarily small change; a limit cycle survives one, which is the practical difference between the two.",
                    "Try every combination of the four sliders. Nothing produces a single closed curve with trajectories approaching it from inside *and* outside. A linear field cannot do it at any setting, which is precisely why the lab needs a non-linear one.",
                ],
            },
            "derive": {
                "title": "Where van der Pol's cycle comes from",
                "minutes": 15,
                "vars": ["mu", "x_1", "x_2", "V", "a", "t", "r"],
                "brief": r'''
The van der Pol oscillator, with $\mu > 0$:

$$\dot{x_1} = x_2, \qquad \dot{x_2} = \mu\left(1 - x_1^2\right)x_2 - x_1$$

Read the damping term. For $|x_1| < 1$ its coefficient is positive, so the system is
*negatively* damped and small motions grow. For $|x_1| > 1$ it is ordinary damping and
large motions shrink. Something has to happen in between.
''',
                "steps": [
                    {
                        "prompt": "Bendixson's criterion needs the divergence of the field, $\\partial f_1/\\partial x_1 + \\partial f_2/\\partial x_2$. Write it.",
                        "answer": "\\mu\\left(1 - x_1^2\\right)",
                        "hint": "$f_1 = x_2$ does not involve $x_1$ at all, so the first term is zero.",
                        "deconstruct": [
                            "$\\partial f_1/\\partial x_1 = \\partial (x_2)/\\partial x_1 = 0$.",
                            "$\\partial f_2/\\partial x_2 = \\mu(1 - x_1^2)$, since $x_2$ appears linearly there.",
                        ],
                    },
                    {
                        "prompt": "Bendixson says a region on which the divergence keeps one strict sign contains no closed orbit. Write the value of $|x_1|$ at which the divergence changes sign — the boundary any closed orbit is obliged to cross.",
                        "answer": "1",
                        "hint": "The divergence is $\\mu(1 - x_1^2)$, and $\\mu > 0$, so the sign is decided by $1 - x_1^2$.",
                        "deconstruct": [
                            "$1 - x_1^2 = 0$ when $x_1^2 = 1$.",
                            "So the divergence is positive for $|x_1| < 1$ and negative for $|x_1| > 1$, and no cycle can fit inside either strip alone.",
                        ],
                    },
                    {
                        "prompt": "Now the energy argument. With $V = \\tfrac{1}{2}\\left(x_1^2 + x_2^2\\right)$, write $\\dot{V} = x_1\\dot{x_1} + x_2\\dot{x_2}$, simplified.",
                        "answer": "\\mu\\left(1 - x_1^2\\right)x_2^2",
                        "hint": "The $x_1 x_2$ terms cancel, exactly as they did for the spring in module 2.",
                        "deconstruct": [
                            "$\\dot{V} = x_1 x_2 + x_2\\left(\\mu(1 - x_1^2)x_2 - x_1\\right)$.",
                            "Expand: $x_1 x_2 + \\mu(1 - x_1^2)x_2^2 - x_1 x_2$, and the outer pair cancels.",
                        ],
                    },
                    {
                        "prompt": "For small $\\mu$ the cycle is nearly a circle of radius $a$, so put $x_1 = a\\cos t$ and $x_2 = -a\\sin t$. On the cycle the energy neither grows nor decays, so the average of $\\dot{V}$ over one period is zero. Write $a$.",
                        "given": "Over a full period, the average of $\\sin^2 t$ is $\\tfrac{1}{2}$ and the average of $\\cos^2 t\\,\\sin^2 t$ is $\\tfrac{1}{8}$.",
                        "answer": "2",
                        "hint": "Substitute and average term by term: $\\tfrac{1}{2}a^2 - \\tfrac{1}{8}a^4 = 0$. Then divide out the root at $a = 0$.",
                        "deconstruct": [
                            "$\\dot{V} = \\mu(1 - a^2\\cos^2 t)a^2\\sin^2 t$, whose average is $\\mu\\left(\\tfrac{1}{2}a^2 - \\tfrac{1}{8}a^4\\right)$.",
                            "Setting that to zero and discarding $a = 0$ leaves $a^2 = 4$.",
                        ],
                    },
                ],
                "closing": r'''
Two independent arguments, one conclusion. Bendixson says any closed orbit must
straddle $|x_1| = 1$; the energy balance says it settles at radius $2$ when $\mu$ is
small. Neither argument solved the differential equation, and neither has a linear
counterpart — a linear system has no amplitude at which pumping and damping balance,
which is why its cycles come in continuous families or not at all.

The amplitude $2$ is the small-$\mu$ answer. The lab measures the true one, and you
will find it drifts upward as $\mu$ grows and the orbit stops being a circle.
''',
            },
            "quiz": {
                "title": "An orbit no linear system can produce",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What is a nullcline?",
                        "opts": [
                            "A curve where one component of $\\dot{x}$ is zero",
                            "A curve where the whole vector field vanishes",
                            "A trajectory that returns to its start",
                            "The boundary of the region of attraction",
                        ],
                        "a": 0,
                        "why": r"""
One component at a time. Where the $x_1$-nullcline runs, motion is purely vertical;
where the $x_2$-nullcline runs, purely horizontal; and where they *cross*, both are zero
and you have an equilibrium. Sketching the two curves carves the plane into regions with
a known sign pattern, which is how you get the qualitative picture without solving
anything.
""",
                    },
                    {
                        "q": "What makes a limit cycle a limit cycle rather than just a closed orbit?",
                        "opts": [
                            "It is isolated — nearby trajectories spiral onto it or away from it",
                            "It is circular",
                            "It is stable",
                            "It encloses an equilibrium",
                        ],
                        "a": 0,
                        "why": r"""
Isolation. A limit cycle has a neighbourhood containing no other closed orbit, so its
neighbours must approach it or leave it — they cannot simply sit beside it. That is
precisely what makes it a robust, physically observable object: an oscillator settles
onto the same amplitude regardless of how it was started, which is what you want from a
clock and cannot get from a linear circuit.
""",
                    },
                    {
                        "q": "Can a linear system have a limit cycle?",
                        "opts": [
                            "No — when it has closed orbits at all they form a continuum",
                            "Yes, if the eigenvalues are purely imaginary",
                            "Yes, if it is at least third order",
                            "Only if it is time-varying",
                        ],
                        "a": 0,
                        "why": r"""
A linear centre gives a nested family of closed orbits, one through every point — nothing
isolated, and the amplitude is whatever the initial condition happened to be. That is why
a purely imaginary pair is such a fragile way to build an oscillator: the amplitude is
unset, and the tiniest modelling error turns the family into a slow spiral in or out. A
real oscillator is non-linear on purpose.
""",
                    },
                    {
                        "q": "You perturb a linear centre slightly. What happens to its closed orbits?",
                        "opts": [
                            "They all become spirals, in or out",
                            "They survive unchanged",
                            "They collapse to a single limit cycle",
                            "They become saddles",
                        ],
                        "a": 0,
                        "why": r"""
The eigenvalues move off the imaginary axis and every orbit becomes a spiral. The whole
family is destroyed at once, which is another way of saying a centre is structurally
unstable — and the reason Hartman–Grobman has to exclude the imaginary axis. A limit
cycle, by contrast, survives small perturbation, which is what makes it worth building a
design around.
""",
                    },
                    {
                        "q": "A stable limit cycle in the plane attracts trajectories from where?",
                        "opts": [
                            "Both inside and outside it",
                            "Outside only",
                            "Inside only",
                            "Only from points on the cycle itself",
                        ],
                        "a": 0,
                        "why": r"""
Both sides — which, in the plane, forces something to be inside it: by the
Poincaré–Bendixson theorem a closed orbit must enclose at least one equilibrium, and for
the cycle to be attracting from within, that equilibrium is typically an unstable focus.
Energy is being pumped in near the centre and dissipated at large amplitude, and the
cycle sits where the two balance. That is a Van der Pol oscillator described in one
sentence.
""",
                    },
                ],
            },
            "lab": {
                "title": "Find the limit cycle and prove it is isolated",
                "runtime": "python",
                "minutes": 38,
                "brief": r'''
Forward Euler is not good enough here. A limit cycle is a closed curve, and Euler's
error accumulates in a direction that either inflates or deflates it — you would be
measuring the integrator, not the oscillator. So this lab uses **RK4**.

`rk4_step(f, x, mu, dt)` advances one step:

```text
k1 = f(x, mu)
k2 = f(x + dt/2 * k1, mu)
k3 = f(x + dt/2 * k2, mu)
k4 = f(x + dt   * k3, mu)
return x + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
```

`integrate(mu, x0, dt, steps)` returns a `(steps + 1, 2)` array whose first row is
`x0` and whose remaining rows are the successive states.

`period(traj, dt)` measures the period from the **second half** of the trajectory, so
the transient is excluded. Find every index `n` where `x1` crosses zero going upward
(`traj[n, 0] < 0 <= traj[n+1, 0]`), refine each crossing by linear interpolation to
`(n + frac) * dt` with `frac = -x1[n] / (x1[n+1] - x1[n])`, and return the mean gap
between successive crossings. Return `float("nan")` if there are fewer than two.

`vdp` and `amplitude` are written for you.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def vdp(x, mu):
    """The van der Pol field: x1' = x2, x2' = mu (1 - x1**2) x2 - x1."""
    x = np.asarray(x, dtype=float)
    return np.array([x[1], mu * (1.0 - x[0] ** 2) * x[1] - x[0]])


def amplitude(traj):
    """Peak |x1| over the second half of the trajectory."""
    traj = np.asarray(traj, dtype=float)
    tail = traj[len(traj) // 2:]
    return float(np.max(np.abs(tail[:, 0])))


def rk4_step(f, x, mu, dt):
    """One classical fourth-order Runge-Kutta step."""
    # TODO: four slopes, then the weighted average.
    return np.asarray(x, dtype=float)


def integrate(mu, x0, dt, steps):
    """Return a (steps + 1, 2) array of states, starting at x0."""
    x = np.array(x0, dtype=float)
    out = np.zeros((steps + 1, 2))
    out[0] = x
    # TODO: fill the remaining rows with rk4_step.
    return out


def period(traj, dt):
    """Mean time between upward zero crossings of x1, over the second half."""
    traj = np.asarray(traj, dtype=float)
    tail = traj[len(traj) // 2:]
    x = tail[:, 0]
    # TODO: collect interpolated crossing times, then average the gaps.
    return float("nan")


if __name__ == "__main__":
    for mu in (0.0, 1.0, 2.0):
        traj = integrate(mu, [0.1, 0.0], 0.002, 20000)
        print(f"mu = {mu}:  amplitude {amplitude(traj):.6f}   period {period(traj, 0.002):.6f}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def vdp(x, mu):
    """The van der Pol field: x1' = x2, x2' = mu (1 - x1**2) x2 - x1."""
    x = np.asarray(x, dtype=float)
    return np.array([x[1], mu * (1.0 - x[0] ** 2) * x[1] - x[0]])


def amplitude(traj):
    """Peak |x1| over the second half of the trajectory."""
    traj = np.asarray(traj, dtype=float)
    tail = traj[len(traj) // 2:]
    return float(np.max(np.abs(tail[:, 0])))


def rk4_step(f, x, mu, dt):
    """One classical fourth-order Runge-Kutta step."""
    x = np.asarray(x, dtype=float)
    k1 = f(x, mu)
    k2 = f(x + 0.5 * dt * k1, mu)
    k3 = f(x + 0.5 * dt * k2, mu)
    k4 = f(x + dt * k3, mu)
    return x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def integrate(mu, x0, dt, steps):
    """Return a (steps + 1, 2) array of states, starting at x0."""
    x = np.array(x0, dtype=float)
    out = np.zeros((steps + 1, 2))
    out[0] = x
    for n in range(steps):
        x = rk4_step(vdp, x, mu, dt)
        out[n + 1] = x
    return out


def period(traj, dt):
    """Mean time between upward zero crossings of x1, over the second half."""
    traj = np.asarray(traj, dtype=float)
    tail = traj[len(traj) // 2:]
    x = tail[:, 0]
    times = []
    for n in range(len(x) - 1):
        if x[n] < 0.0 <= x[n + 1]:
            frac = -x[n] / (x[n + 1] - x[n])
            times.append((n + frac) * dt)
    if len(times) < 2:
        return float("nan")
    return float(np.mean(np.diff(times)))


if __name__ == "__main__":
    for mu in (0.0, 1.0, 2.0):
        traj = integrate(mu, [0.1, 0.0], 0.002, 20000)
        print(f"mu = {mu}:  amplitude {amplitude(traj):.6f}   period {period(traj, 0.002):.6f}")
'''}],
                "hints": [
                    "In `rk4_step`, `k2` and `k3` use a *half* step and `k4` a full one; the weights are `1, 2, 2, 1` over six. Getting the halves wrong drops the method to second order and the amplitude drifts by a per cent or so.",
                    "`integrate` should hand `vdp` to `rk4_step` as an argument rather than calling it directly, so the same stepper can be pointed at another field later.",
                    "The upward-crossing test is `x[n] < 0 <= x[n+1]`. Using `<=` on both sides double-counts a sample that lands exactly on zero.",
                    "`np.diff` on the list of crossing times gives the gaps; the mean of those is the period.",
                ],
                "tests": [
                    {"name": "RK4 reproduces a known solution", "code": r'''
import numpy as np
_traj = integrate(0.0, [1.0, 0.0], 0.002, 5000)
assert _traj.shape == (5001, 2), f"expected (steps + 1, 2) = (5001, 2), got {_traj.shape}"
assert abs(_traj[0, 0] - 1.0) < 1e-15, "the first row is x0 itself, unchanged"
_t = 5000 * 0.002
_err = max(abs(_traj[-1, 0] - np.cos(_t)), abs(_traj[-1, 1] + np.sin(_t)))
assert _err < 1e-8, \
    f"with mu = 0 the field is the harmonic oscillator and the answer is (cos t, -sin t); off by {_err:.3e}. A first- or second-order stepper cannot reach this accuracy"
'''},
                    {"name": "the period of the harmonic oscillator is 2 pi", "code": r'''
import numpy as np
_traj = integrate(0.0, [1.0, 0.0], 0.002, 20000)
_T = period(_traj, 0.002)
assert abs(_T - 2 * np.pi) < 1e-4, \
    f"expected 2 pi = {2 * np.pi:.6f}, got {_T:.6f} — if this is out by a factor of two you are counting crossings in both directions"
'''},
                    {"name": "a linear centre has no isolated orbit", "code": r'''
import numpy as np
_big = amplitude(integrate(0.0, [1.0, 0.0], 0.002, 20000))
_small = amplitude(integrate(0.0, [0.4, 0.0], 0.002, 20000))
assert abs(_big - 1.0) < 1e-6 and abs(_small - 0.4) < 1e-6, \
    f"each start keeps its own amplitude ({_big:.6f} and {_small:.6f}) — the closed orbits form a continuum, so none of them is a limit cycle"
'''},
                    {"name": "van der Pol converges to one amplitude from anywhere", "code": r'''
import numpy as np
_inside = amplitude(integrate(1.0, [0.1, 0.0], 0.002, 20000))
_outside = amplitude(integrate(1.0, [3.0, 0.0], 0.002, 20000))
assert abs(_inside - _outside) < 1e-4, \
    f"a start 30 times smaller must end on the same orbit: got {_inside:.6f} from inside and {_outside:.6f} from outside. That agreement is what makes the cycle isolated"
assert abs(_inside - 2.008620) < 5e-4, \
    f"the mu = 1 cycle has amplitude about 2.00862, not the small-mu prediction of exactly 2; got {_inside:.6f}"
'''},
                    {"name": "the period is not 2 pi once mu is nonzero", "code": r'''
import numpy as np
_T = period(integrate(1.0, [0.1, 0.0], 0.002, 20000), 0.002)
assert abs(_T - 6.663287) < 2e-3, \
    f"the mu = 1 period is about 6.66329; got {_T:.6f}"
assert _T > 2 * np.pi, \
    "the non-linear damping slows the oscillator down, so its period exceeds the linear 2 pi"
'''},
                    {"name": "a larger mu distorts the cycle further", "code": r'''
import numpy as np
_a = amplitude(integrate(2.0, [0.1, 0.0], 0.002, 20000))
_T = period(integrate(2.0, [0.1, 0.0], 0.002, 20000), 0.002)
assert abs(_a - 2.019891) < 5e-4, f"the mu = 2 amplitude is about 2.01989, got {_a:.6f}"
assert abs(_T - 7.629875) < 5e-3, f"the mu = 2 period is about 7.62987, got {_T:.6f}"
assert _T > 6.663287, \
    "the period keeps growing with mu as the orbit turns into the slow-fast relaxation shape"
'''},
                    {"name": "the small-mu amplitude really is 2", "code": r'''
import numpy as np
_on = amplitude(integrate(0.05, [2.0, 0.0], 0.002, 20000))
assert abs(_on - 2.0) < 1e-3, \
    f"at mu = 0.05 the circle of radius 2 is very nearly invariant: start on it and the amplitude should not move, got {_on:.6f}"
_to = amplitude(integrate(0.05, [1.9, 0.0], 0.002, 40000))
assert abs(_to - 2.0) < 5e-3, \
    f"and it attracts: from 1.9 the amplitude should climb to within a few thousandths of 2 over 80 s, got {_to:.6f}. Convergence takes a time of order 1/mu, so a short run here proves nothing"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Sliding-mode control and the boundary layer",
            "summary": "Choose a surface on which the error dies the way you want, then switch hard enough to force the state onto it and hold it there whatever the plant does.",
            "concepts": [
                "The sliding surface $s = \\dot{e} + \\lambda e$. On $s = 0$ the error obeys the first-order equation *you* chose, and the plant has stopped mattering.",
                "The reaching condition $s\\dot{s} \\le -\\eta|s|$. With $V = \\tfrac{1}{2}s^2$ this is $\\dot{V} \\le -\\eta\\sqrt{2V}$, which reaches zero in **finite** time, not asymptotically.",
                "Matched uncertainty: anything entering through the same channel as $u$ can be dominated by a switching gain that exceeds its bound. Unmatched uncertainty cannot.",
                "The gain must beat the *bound*, not the nominal value. Under-gain and the surface is never reached, and no amount of patience fixes it.",
                "Chatter: infinite switching frequency is an artefact of an idealised model, and a real actuator pays for it in heat and wear. The boundary layer replaces $\\mathrm{sgn}$ with a saturation and buys smoothness with a band of error.",
            ],
            "sandbox": {
                "title": "Reaching, sliding, and the price of not chattering",
                "visualiser": "sliding-mode",
                "minutes": 10,
                "initial": {"lam": 2, "eta": 2.5, "bl": 0},
                "brief": r'''
The purple line is the sliding surface $s = \dot{x} + \lambda x = 0$. Four
trajectories start at the corners.

Each one has two distinct phases. First it runs at the surface from wherever it
began — the *reaching* phase, governed by $\eta$. Then it travels along the surface
towards the origin — the *sliding* phase, governed by $\lambda$ and by nothing else.
''',
                "notice": [
                    "Follow one trajectory to the line and then along it. On the line the motion obeys $\\dot{x} = -\\lambda x$: first order, and set by your choice of slope rather than by the plant.",
                    "Raise $\\eta$. The reaching phase gets shorter and straighter, because $|\\dot{s}| \\ge \\eta$ is the entire guarantee and the reaching time is at most $|s(0)|/\\eta$. Then look closely at what the trajectory does *on* the line: it is not travelling along it but crossing it, over and over.",
                    "Now lift $\\phi$ off zero. The crossing disappears and the trajectories settle into the band between the two faint lines. That band is the price: the state no longer reaches the surface, only its neighbourhood, and the steady error is proportional to $\\phi$.",
                ],
            },
            "derive": {
                "title": "The reaching law, the reaching time, and what the layer costs",
                "minutes": 18,
                "vars": ["s", "s_0", "x_0", "x_1", "x_2", "u", "lambda", "lambda_",
                         "eta", "phi", "t", "V", "t_r", "e"],
                "brief": r'''
A double integrator, $\dot{x_1} = x_2$ and $\dot{x_2} = u$, and the surface

$$s = x_2 + \lambda x_1 \qquad (\lambda > 0)$$

The plan is in two halves: force $s$ to zero in finite time, and then note that
$s = 0$ *is* the closed-loop specification, because $s = 0$ reads
$\dot{x_1} = -\lambda x_1$.
''',
                "steps": [
                    {
                        "prompt": "Differentiate $s = x_2 + \\lambda x_1$ along the trajectories. Write $\\dot{s}$ in terms of $u$, $\\lambda$ and $x_2$.",
                        "answer": "u + \\lambda x_2",
                        "hint": "$\\dot{x_2} = u$ and $\\dot{x_1} = x_2$. Substitute both.",
                        "deconstruct": [
                            "$\\dot{s} = \\dot{x_2} + \\lambda\\dot{x_1}$.",
                            "The first is $u$ and the second is $\\lambda x_2$.",
                        ],
                    },
                    {
                        "prompt": "You want the reaching law $\\dot{s} = -\\eta\\,\\mathrm{sgn}(s)$. Take the branch where $s > 0$, so $\\mathrm{sgn}(s) = 1$, and solve for $u$.",
                        "answer": "-\\eta - \\lambda x_2",
                        "hint": "Set the expression from step 1 equal to $-\\eta$ and make $u$ the subject.",
                        "deconstruct": [
                            "$u + \\lambda x_2 = -\\eta$.",
                            "So $u = -\\eta - \\lambda x_2$. The second term is the *equivalent control* that cancels the known dynamics; the first is the switching part that does the work.",
                        ],
                    },
                    {
                        "prompt": "Take $V = \\tfrac{1}{2}s^2$ as a Lyapunov function for the reaching phase. Still on the branch $s > 0$, write $\\dot{V} = s\\dot{s}$ in terms of $\\eta$ and $s$.",
                        "answer": "-\\eta s",
                        "hint": "You arranged $\\dot{s} = -\\eta$ on this branch, so multiply by $s$.",
                        "deconstruct": [
                            "$\\dot{V} = s\\dot{s}$ by the chain rule on $\\tfrac{1}{2}s^2$.",
                            "With $\\dot{s} = -\\eta$ this is $-\\eta s$, which is strictly negative because $s > 0$ on this branch.",
                        ],
                    },
                    {
                        "prompt": "On this branch $s$ falls at the constant rate $\\eta$ — not proportionally to $s$, but at a fixed rate. Starting from $s(0) = s_0 > 0$, write the time $t_r$ at which $s$ first reaches zero.",
                        "answer": "\\frac{s_0}{\\eta}",
                        "hint": "Constant rate: distance over speed. Nothing exponential appears anywhere.",
                        "deconstruct": [
                            "$\\dot{s} = -\\eta$ integrates to $s(t) = s_0 - \\eta t$.",
                            "That hits zero at $t = s_0/\\eta$, and this is the crucial difference from linear feedback — the surface is reached exactly, in finite time.",
                        ],
                    },
                    {
                        "prompt": "After $t_r$ the state is on the surface and stays there, so $s = 0$ and the motion obeys $\\dot{x_1} = -\\lambda x_1$. Write $x_1(t)$ in terms of $x_0$, $\\lambda$ and $t$.",
                        "answer": "x_0 e^{-\\lambda t}",
                        "hint": "A first-order linear equation, with $\\lambda$ the decay rate you chose when you drew the surface.",
                        "deconstruct": [
                            "$\\dot{x_1} = -\\lambda x_1$ is the scalar exponential.",
                            "Its solution through $x_1(0) = x_0$ is $x_0 e^{-\\lambda t}$, and notice the plant no longer appears.",
                        ],
                    },
                    {
                        "prompt": "The boundary layer replaces $\\mathrm{sgn}(s)$ by $s/\\phi$ while $|s| < \\phi$, so inside the layer the law becomes $\\dot{s} = -\\frac{\\eta}{\\phi}s$. Write the time constant of $s$ there.",
                        "answer": "\\frac{\\phi}{\\eta}",
                        "hint": "For $\\dot{s} = -\\alpha s$ the time constant is $1/\\alpha$. Here $\\alpha = \\eta/\\phi$.",
                        "deconstruct": [
                            "Inside the layer the dynamics are linear: $\\dot{s} = -(\\eta/\\phi)s$.",
                            "The time constant is the reciprocal of the rate, so $\\phi/\\eta$.",
                        ],
                    },
                ],
                "closing": r'''
Compare the last two steps and the trade is exact. Outside the layer $s$ falls at a
constant rate and arrives at zero in finite time. Inside it, $s$ decays exponentially
and never arrives at all — it converges to whatever value balances the disturbance,
which for a disturbance bounded by $D$ and a switching gain $k$ is $|s| \to D\phi/k$.

Take $\phi$ to zero and the exactness returns along with the chatter. There is no
setting at which you get both, and choosing $\phi$ is choosing how much error to
accept in exchange for an actuator that survives the week.
''',
            },
            "blanks": {
                "title": "The surface, the reaching law, and the price of chattering",
                "minutes": 9,
                "caption": "sliding.py — a controller in four decisions",
                "lang": "python",
                "brief": r"""
Sliding mode is two ideas bolted together: choose a surface on which the error behaves
the way you want, then switch hard enough to force the state onto it and keep it there.
Fill in both halves, and the cost the method charges.
""",
                "listing": """# The sliding surface, with lambda > 0:
s = ___

# On s = 0 the error obeys  edot = -lambda*e, a first-order decay of
# time constant ___ .
# Note the ORDER has dropped: a second-order plant now behaves first-order.

# The reaching condition, with eta > 0:
s * sdot <= ___

# With V = s**2/2 this is Vdot <= -eta*sqrt(2V), which drives s to zero
# in ___ -- not asymptotically.

# Replacing sign(s) with a saturation of width phi buys ___ .
""",
                "blanks": [
                    {
                        "prompt": "The surface itself.",
                        "hole": "?",
                        "opts": ["edot + lam * e", "e + lam * edot", "lam * e", "edot - lam * e"],
                        "a": 0,
                        "why": "$s = \\dot{e} + \\lambda e$. Setting it to zero *is* the differential equation $\\dot{e} = -\\lambda e$, so the surface is not an arbitrary choice — it is the error dynamics you want, written as an algebraic constraint. Pick $\\lambda$ and you have picked the closed-loop time constant before designing any control at all.",
                        "whys": [
                            "$s = \\dot{e} + \\lambda e$. Setting it to zero *is* the differential equation $\\dot{e} = -\\lambda e$, so the surface is not an arbitrary choice — it is the error dynamics you want, written as an algebraic constraint. Pick $\\lambda$ and you have picked the closed-loop time constant before designing any control at all.",
                            "Swapping the terms gives $\\dot{e} = -e/\\lambda$ on the surface, which inverts what $\\lambda$ means and makes a large $\\lambda$ slow rather than fast.",
                            "Without $\\dot{e}$ the surface constrains the error but not its rate, and reaching it says nothing about how the error then behaves.",
                            "The minus sign makes the surface dynamics $\\dot{e} = +\\lambda e$ — the error grows exponentially once you are on it, which is exactly backwards.",
                        ],
                    },
                    {
                        "prompt": "edot = -lambda*e decays how fast?",
                        "hole": "?",
                        "opts": ["1 / lam", "lam", "2 / lam", "lam ** 2"],
                        "a": 0,
                        "why": "$1/\\lambda$, the usual first-order time constant. So $\\lambda$ is the one performance knob and it is chosen directly, in seconds — a considerably more comfortable design parameter than a set of pole locations.",
                        "whys": [
                            "$1/\\lambda$, the usual first-order time constant. So $\\lambda$ is the one performance knob and it is chosen directly, in seconds — a considerably more comfortable design parameter than a set of pole locations.",
                            "$\\lambda$ is a rate, in reciprocal seconds; the time constant is its inverse.",
                            "The factor of two belongs to no standard first-order form.",
                            "Squaring gives neither a time nor a rate.",
                        ],
                    },
                    {
                        "prompt": "How hard must you push toward the surface?",
                        "hole": "?",
                        "opts": ["-eta * abs(s)", "0", "-eta * s", "eta * abs(s)"],
                        "a": 0,
                        "why": "$s\\dot{s} \\le -\\eta|s|$. The $|s|$ is what makes reaching happen in *finite* time — the push does not fade away as $s$ shrinks, so the state arrives rather than merely approaching. That is the property the whole method is built on, and it is why the control has to switch discontinuously.",
                        "whys": [
                            "$s\\dot{s} \\le -\\eta|s|$. The $|s|$ is what makes reaching happen in *finite* time — the push does not fade away as $s$ shrinks, so the state arrives rather than merely approaching. That is the property the whole method is built on, and it is why the control has to switch discontinuously.",
                            "Merely non-increasing lets the state hover at a fixed distance from the surface forever.",
                            "$-\\eta s$ is not sign-definite: for negative $s$ it demands $s\\dot{s} \\le$ a positive number, which is no constraint at all in that half.",
                            "The sign is inverted, which requires the state to move *away* from the surface.",
                        ],
                    },
                    {
                        "prompt": "So the state reaches the surface how?",
                        "hole": "?",
                        "opts": [
                            "in finite time",
                            "asymptotically, never exactly",
                            "in exactly one time constant",
                            "only if the initial error is small",
                        ],
                        "a": 0,
                        "why": "Finite time, bounded by $|s(0)|/\\eta$ — after which the error obeys $\\dot{e} = -\\lambda e$ exactly, and any matched uncertainty is completely rejected. That combination of finite-time reaching and total insensitivity to matched disturbance is what people mean when they call sliding mode robust.",
                        "whys": [
                            "Finite time, bounded by $|s(0)|/\\eta$ — after which the error obeys $\\dot{e} = -\\lambda e$ exactly, and any matched uncertainty is completely rejected. That combination of finite-time reaching and total insensitivity to matched disturbance is what people mean when they call sliding mode robust.",
                            "That is what a continuous law gives. The discontinuity is precisely what buys arrival in finite time — and precisely what causes the chattering in the next blank.",
                            "The reaching time depends on the initial distance and on $\\eta$; there is no single time constant for it.",
                            "The condition is global for any $s(0)$, provided the control authority is there to satisfy it.",
                        ],
                    },
                    {
                        "prompt": "And what does the boundary layer trade?",
                        "hole": "?",
                        "opts": [
                            "chattering, for a bounded steady-state error",
                            "robustness, for speed",
                            "bandwidth, for accuracy",
                            "nothing -- it is a free improvement",
                        ],
                        "a": 0,
                        "why": "Inside the layer the control is continuous, so the infinitely fast switching stops — and so does the exact rejection of disturbance, leaving an error proportional to $\\phi$. Real hardware forces this trade whether or not you design it: no actuator switches infinitely fast, and unmodelled dynamics turn ideal sliding into buzzing anyway. Choosing $\\phi$ deliberately is better than discovering it.",
                        "whys": [
                            "Inside the layer the control is continuous, so the infinitely fast switching stops — and so does the exact rejection of disturbance, leaving an error proportional to $\\phi$. Real hardware forces this trade whether or not you design it: no actuator switches infinitely fast, and unmodelled dynamics turn ideal sliding into buzzing anyway. Choosing $\\phi$ deliberately is better than discovering it.",
                            "Speed on the surface is set by $\\lambda$ and the boundary layer does not change it.",
                            "The trade is about steady-state accuracy against actuator wear, not bandwidth.",
                            "It is emphatically not free: the exactness of the sliding motion is what is being given up.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Sliding-mode control of a disturbed double integrator",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
The plant is $\dot{x_1} = x_2$, $\dot{x_2} = u + d(t)$ with an unknown disturbance
$d(t) = A\sin 3t$. You are not told $A$; you are told only that $|d| \le D$. Four
functions.

`sat(v, phi)` is the switching function. With `phi <= 0` return the hard sign of `v`
(`+1`, `-1`, or `0`); otherwise return `v / phi` clipped to $[-1, 1]$.

`surface(x, lam)` returns $s = x_2 + \lambda x_1$.

`control(x, lam, eta, dbound, phi)` returns

```text
u = -lam * x2 - (dbound + eta) * sat(s, phi)
```

The first term cancels the known part of $\dot{s}$; the second must dominate the
disturbance, which is why the gain is `dbound + eta` and not `eta`.

`run(x0, lam, eta, dbound, phi, dt, steps, d_amp)` forward-Eulers the closed loop and
returns three arrays `(xs, ss, us)` of lengths `steps`. At each step, in this order:
compute `u` from the current state, record the state, `s` and `u`, then advance with
$d = $ `d_amp * sin(3 t)` where `t = n * dt`.

`chatter` and `reach_time` are written for you.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def chatter(us):
    """Mean absolute change in u from one step to the next."""
    return float(np.mean(np.abs(np.diff(np.asarray(us, dtype=float)))))


def reach_time(ss, dt):
    """Time of the first sign change in s, or inf if it never changes."""
    ss = np.asarray(ss, dtype=float)
    for n in range(len(ss) - 1):
        if ss[n] * ss[n + 1] <= 0.0:
            return n * dt
    return float("inf")


def sat(v, phi):
    """Hard sign when phi <= 0, otherwise v/phi clipped to [-1, 1]."""
    # TODO
    return 0.0


def surface(x, lam):
    """The sliding variable s = x2 + lam * x1."""
    # TODO
    return 0.0


def control(x, lam, eta, dbound, phi):
    """Equivalent control plus a switching term that dominates the disturbance."""
    # TODO
    return 0.0


def run(x0, lam, eta, dbound, phi, dt, steps, d_amp):
    """Forward-Euler the closed loop. Returns (xs, ss, us)."""
    x = np.array(x0, dtype=float)
    xs = np.zeros((steps, 2))
    ss = np.zeros(steps)
    us = np.zeros(steps)
    # TODO: control, record, then step with the disturbance.
    return xs, ss, us


if __name__ == "__main__":
    for phi in (0.0, 0.05):
        xs, ss, us = run([1.0, 0.0], 4.0, 2.0, 2.0, phi, 0.0005, 12000, 2.0)
        print(f"phi = {phi}:  reached at {reach_time(ss, 0.0005):.4f} s,"
              f"  final x1 = {xs[-1, 0]:+.6f},  chatter = {chatter(us):.6f}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def chatter(us):
    """Mean absolute change in u from one step to the next."""
    return float(np.mean(np.abs(np.diff(np.asarray(us, dtype=float)))))


def reach_time(ss, dt):
    """Time of the first sign change in s, or inf if it never changes."""
    ss = np.asarray(ss, dtype=float)
    for n in range(len(ss) - 1):
        if ss[n] * ss[n + 1] <= 0.0:
            return n * dt
    return float("inf")


def sat(v, phi):
    """Hard sign when phi <= 0, otherwise v/phi clipped to [-1, 1]."""
    if phi <= 0.0:
        return float(np.sign(v))
    return float(max(-1.0, min(1.0, v / phi)))


def surface(x, lam):
    """The sliding variable s = x2 + lam * x1."""
    x = np.asarray(x, dtype=float)
    return float(x[1] + lam * x[0])


def control(x, lam, eta, dbound, phi):
    """Equivalent control plus a switching term that dominates the disturbance."""
    x = np.asarray(x, dtype=float)
    s = surface(x, lam)
    return float(-lam * x[1] - (dbound + eta) * sat(s, phi))


def run(x0, lam, eta, dbound, phi, dt, steps, d_amp):
    """Forward-Euler the closed loop. Returns (xs, ss, us)."""
    x = np.array(x0, dtype=float)
    xs = np.zeros((steps, 2))
    ss = np.zeros(steps)
    us = np.zeros(steps)
    for n in range(steps):
        t = n * dt
        u = control(x, lam, eta, dbound, phi)
        xs[n] = x
        ss[n] = surface(x, lam)
        us[n] = u
        d = d_amp * np.sin(3.0 * t)
        x = x + dt * np.array([x[1], u + d])
    return xs, ss, us


if __name__ == "__main__":
    for phi in (0.0, 0.05):
        xs, ss, us = run([1.0, 0.0], 4.0, 2.0, 2.0, phi, 0.0005, 12000, 2.0)
        print(f"phi = {phi}:  reached at {reach_time(ss, 0.0005):.4f} s,"
              f"  final x1 = {xs[-1, 0]:+.6f},  chatter = {chatter(us):.6f}")
'''}],
                "hints": [
                    "`np.sign(0.0)` is `0.0`, which is the right answer on the surface — do not replace it with `+1`.",
                    "`control` must call `surface`, not recompute $s$ inline, or the two can drift apart when you change the surface later.",
                    "Order matters inside `run`: the control is a function of the state *before* the step, so compute `u` first, record, then advance. Recording after the step shifts every array by one sample and quietly changes the measured reaching time.",
                    "The switching gain is `dbound + eta`. Using `eta` alone leaves nothing to beat the disturbance with, and the surface is never reached.",
                ],
                "tests": [
                    {"name": "sat switches hard with no layer and ramps inside one", "code": r'''
assert sat(0.5, 0.0) == 1.0 and sat(-0.5, 0.0) == -1.0, \
    "with phi = 0 the function is the sign of its argument, whatever the magnitude"
assert sat(0.0, 0.0) == 0.0, "sgn(0) is 0 — on the surface there is no direction to switch towards"
assert abs(sat(0.01, 0.05) - 0.2) < 1e-12, \
    f"inside the layer the output is v/phi = 0.01/0.05 = 0.2, got {sat(0.01, 0.05)}"
assert sat(1.0, 0.05) == 1.0 and sat(-1.0, 0.05) == -1.0, \
    "outside the layer the saturation is back to full switching"
'''},
                    {"name": "the surface and the control have the signs they should", "code": r'''
assert abs(surface([1.0, -2.0], 4.0) - 2.0) < 1e-12, \
    f"s = x2 + lam*x1 = -2 + 4 = 2, got {surface([1.0, -2.0], 4.0)}"
assert abs(surface([0.0, 0.0], 4.0)) < 1e-12, "the origin is on every surface through it"
_u = control([1.0, 0.0], 4.0, 2.0, 2.0, 0.0)
assert abs(_u + 4.0) < 1e-12, \
    f"with s = +4 the switching term is -(2 + 2)*1 = -4 and the equivalent control is -4*0 = 0, so u = -4; got {_u}"
assert abs(control([-1.0, 0.0], 4.0, 2.0, 2.0, 0.0) - 4.0) < 1e-12, \
    "the control must oppose the sign of s, or the state is driven away from the surface"
'''},
                    {"name": "the surface is reached in finite time, inside the guarantee", "code": r'''
import numpy as np
_xs, _ss, _us = run([1.0, 0.0], 4.0, 2.0, 2.0, 0.0, 0.0005, 12000, 2.0)
assert _xs.shape == (12000, 2) and _ss.shape == (12000,) and _us.shape == (12000,), \
    f"expected 12000 samples of each, got {_xs.shape}, {_ss.shape}, {_us.shape}"
assert abs(_ss[0] - 4.0) < 1e-12, f"s(0) = 0 + 4*1 = 4, got {_ss[0]}"
_tr = reach_time(_ss, 0.0005)
assert _tr < 2.0 + 1e-9, \
    f"the guarantee is t_r <= |s0|/eta = 4/2 = 2 s, and it was not met: {_tr}. The usual cause is a switching gain of eta instead of dbound + eta"
assert _tr > 0.5, \
    f"reaching at {_tr} s is faster than the plant can move — check that u is applied to the plant rather than the surface being zeroed by hand"
'''},
                    {"name": "sliding is invariant to the disturbance", "code": r'''
import numpy as np
_finals = []
for _d in (0.0, 2.0, -2.0):
    _xs, _ss, _us = run([1.0, 0.0], 4.0, 2.0, 2.0, 0.0, 0.0005, 12000, _d)
    _tail = _xs[int(12000 * 0.8):, 0]
    _finals.append(float(np.max(np.abs(_tail))))
assert max(_finals) < 1e-3, \
    f"once on the surface the motion is x1' = -lam x1 and the disturbance has no way in; peak |x1| over the last fifth was {max(_finals):.6f} for disturbances of 0, +2 and -2"
'''},
                    {"name": "the boundary layer removes the chatter", "code": r'''
import numpy as np
_, _, _hard = run([1.0, 0.0], 4.0, 2.0, 2.0, 0.0, 0.0005, 12000, 2.0)
_, _, _soft = run([1.0, 0.0], 4.0, 2.0, 2.0, 0.05, 0.0005, 12000, 2.0)
_ch, _cs = chatter(_hard), chatter(_soft)
assert _ch > 1.0, \
    f"with phi = 0 the control flips between +4 and -4 every step, so the mean step change should be of order 4; got {_ch:.6f}"
assert _cs < 0.02, f"inside a boundary layer u is continuous and barely moves; got {_cs:.6f}"
assert _ch / _cs > 100.0, \
    f"the layer should cut the chatter by orders of magnitude, not a few per cent; the ratio was {_ch / _cs:.1f}"
'''},
                    {"name": "and charges for it in accuracy", "code": r'''
import numpy as np
_tail = slice(int(12000 * 0.8), 12000)
_, _sh, _ = run([1.0, 0.0], 4.0, 2.0, 2.0, 0.0, 0.0005, 12000, 2.0)
_, _ss, _ = run([1.0, 0.0], 4.0, 2.0, 2.0, 0.05, 0.0005, 12000, 2.0)
_hard = float(np.max(np.abs(_sh[_tail])))
_soft = float(np.max(np.abs(_ss[_tail])))
assert abs(_soft - 0.025) < 3e-3, \
    f"in the layer s settles where the switching balances the disturbance: |s| -> D*phi/(D+eta) = 2*0.05/4 = 0.025; got {_soft:.6f}"
assert _soft > 5.0 * _hard, \
    f"the layer trades exactness for smoothness, so |s| must be larger with it than without: {_soft:.6f} against {_hard:.6f}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Hold an uncertain pendulum upright with a switching law",
        "runtime": "python",
        "minutes": 130,
        "brief": r'''
A pendulum, standing up, with a torque you control. Written about the upright
position:

$$\ddot{\theta} = \frac{g}{l}\sin\theta - b\dot{\theta} + d(t) + u$$

Everything on the right except $u$ is hidden from you. `plant.py` holds it, and your
controller may not call it. What you *are* given is a bound on each piece:
$g/l = 19.62$ exactly, the damping satisfies $0 \le b \le 0.30$, and the disturbance
satisfies $|d| \le 4$.

The open loop is a saddle — released at any angle, the pendulum falls. Build the
controller that catches it, and then measure what it cost.

## What to build

1. **The analysis.** `jacobian` and `verdict` from module 1, applied to the
   uncontrolled plant at both equilibria. This is where you find out that upright is
   unstable and hanging is not.
2. **The bound.** `gain_bound(x)` returns the smallest number you can honestly claim
   dominates $|f|$, where $f$ is everything in $\ddot{\theta}$ except $u$. It is a
   function of the state, because the damping term grows with $|x_2|$.
3. **The law.** `sat`, `surface` and `control` from module 4, with the switching gain
   `gain_bound(x) + eta` rather than a constant.
4. **The run.** `simulate` closes the loop over `plant.step` and returns the states,
   the sliding variable and the control at every step.

## Suggested order

The checks are ordered so they light up as you build: the linearisation first, then
the bound, then the reaching phase, then the closed loop, then the boundary layer.
Everything after step 2 depends on `gain_bound` being right, so get that one exactly
right before moving on — an under-gained switching term fails silently, by never
reaching the surface at all, rather than loudly.

Record the state, `s` and `u` **before** each step, exactly as in the module 4 lab,
so the arrays line up with the times `n * dt`.
''',
        "deliverables": [
            "`jacobian(f, x0, h)` and `verdict(J, tol)`, applied to the uncontrolled plant, showing that the upright equilibrium is unstable and the damped hanging one is not.",
            "`gain_bound(x)` returning a bound on the unmodelled term that holds for every admissible damping and every admissible disturbance, and is a function of the state rather than a constant guess.",
            "`sat`, `surface` and `control` implementing $u = -\\lambda x_2 - (\\text{gain\\_bound}(x) + \\eta)\\,\\mathrm{sat}(s/\\phi)$.",
            "`simulate(x0, lam, eta, phi, dt, steps, d_amp, b)` closing the loop over `plant.step` and returning `(xs, ss, us)`.",
            "A comment at the top of `main.py` naming the $\\lambda$, $\\eta$ and $\\phi$ you chose, and what each one bought.",
        ],
        "constraints": [
            "NumPy only — no SciPy, and no control-systems library.",
            "The controller may not call `f_unknown` or read the disturbance. Its only inputs are the state and the bounds you were given.",
            "Forward Euler through `plant.step`, with the timestep the checks use; do not switch integrator.",
            "The switching gain must dominate the *bound*, not the nominal value. A gain tuned until it happens to work for one disturbance is not a design.",
            "Record state, surface and control before each step, so sample `n` corresponds to time `n * dt`.",
        ],
        "rubric": [
            {"criterion": "Linearisation and its limits", "weight": 20,
             "evidence": "The numerical Jacobian matches the analytic one at both equilibria, and the verdict is unstable upright, asymptotically stable hanging, and inconclusive when the damping is removed."},
            {"criterion": "An honest uncertainty bound", "weight": 25,
             "evidence": "gain_bound dominates the true unmodelled term at every point of a state and time grid, for every admissible damping, and grows with the state rather than being a constant fitted to one run."},
            {"criterion": "Reaching and regulation", "weight": 30,
             "evidence": "The surface is reached within the guaranteed time, and the angle is held within a milliradian of upright for disturbances at both signs of the bound and for damping at both ends of its range."},
            {"criterion": "The boundary-layer trade, measured", "weight": 25,
             "evidence": "Chatter falls by orders of magnitude when the layer is opened, and the resulting steady sliding error matches the predicted band rather than merely being small."},
        ],
        "hints": [
            "`gain_bound(x)` is `G_OVER_L + B_NOMINAL * abs(x[1]) + D_BOUND`. Every term is there for a reason: gravity is worst at the horizontal, damping grows with speed, and the disturbance is flat.",
            "The switching gain is `gain_bound(x) + eta`, so it changes at every step. That is the point — a constant gain large enough for fast motion is wastefully large when the pendulum is nearly still.",
            "The equivalent-control term is `-lam * x[1]`, and it is *not* an attempt to cancel gravity. You are not allowed to know gravity; you dominate it instead.",
            "For the reaching check, remember that the guarantee is $t_r \\le |s(0)|/\\eta$, which is loose. With a gain of about 25 against a surface value of 1.6, reaching takes well under a tenth of a second.",
            "If the angle drifts instead of settling, print `s` rather than `theta`. A surface that never reaches zero means the gain is too small; a surface that reaches zero while the angle drifts means `surface` has the wrong sign on $\\lambda$.",
        ],
        "files": [
            {"name": "plant.py", "ro": True, "content": r'''
"""The uncertain pendulum, written about upright. Do not edit, and do not import
f_unknown into your controller — the checks assume you never saw it."""
import numpy as np

G_OVER_L = 19.62      # g/l for a 0.5 m pendulum, exactly known
B_NOMINAL = 0.30      # the damping is somewhere in [0, B_NOMINAL]
D_BOUND = 4.0         # |d(t)| never exceeds this


def f_unknown(x, t, d_amp=0.0, b=B_NOMINAL):
    """Everything in theta'' except the control torque."""
    x = np.asarray(x, dtype=float)
    return float(G_OVER_L * np.sin(x[0]) - b * x[1] + d_amp * np.sin(3.0 * t))


def step(x, u, t, dt, d_amp=0.0, b=B_NOMINAL):
    """One forward-Euler step of theta'' = f_unknown + u."""
    x = np.asarray(x, dtype=float)
    return x + dt * np.array([x[1], f_unknown(x, t, d_amp, b) + u])
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from plant import G_OVER_L, B_NOMINAL, D_BOUND, step, f_unknown

# Chosen gains:
#   lam = TODO, and what it bought
#   eta = TODO, and what it bought
#   phi = TODO, and what it bought


def jacobian(f, x0, h=1e-5):
    """Central-difference Jacobian of the field f at x0."""
    x0 = np.asarray(x0, dtype=float)
    n = x0.size
    # TODO
    return np.zeros((n, n))


def verdict(J, tol=1e-8):
    """asymptotically stable / unstable / inconclusive."""
    # TODO
    return "unknown"


def gain_bound(x):
    """A bound on |f| that holds for every admissible damping and disturbance."""
    # TODO
    return 0.0


def sat(v, phi):
    """Hard sign when phi <= 0, otherwise v/phi clipped to [-1, 1]."""
    # TODO
    return 0.0


def surface(x, lam):
    """s = x2 + lam * x1."""
    # TODO
    return 0.0


def control(x, lam, eta, phi):
    """Equivalent control plus a switching term that dominates gain_bound(x)."""
    # TODO
    return 0.0


def simulate(x0, lam, eta, phi, dt, steps, d_amp=0.0, b=B_NOMINAL):
    """Close the loop over plant.step. Returns (xs, ss, us)."""
    x = np.array(x0, dtype=float)
    xs = np.zeros((steps, 2))
    ss = np.zeros(steps)
    us = np.zeros(steps)
    # TODO: control, record, then step.
    return xs, ss, us


def chatter(us):
    """Mean absolute change in u from one step to the next."""
    return float(np.mean(np.abs(np.diff(np.asarray(us, dtype=float)))))


def reach_time(ss, dt, tol=0.05):
    """First time |s| falls to tol or below, or inf."""
    ss = np.asarray(ss, dtype=float)
    for n in range(len(ss)):
        if abs(ss[n]) <= tol:
            return n * dt
    return float("inf")


if __name__ == "__main__":
    up = jacobian(lambda x: np.array([x[1], f_unknown(x, 0.0)]), [0.0, 0.0])
    print("upright:", np.round(up, 4).tolist(), "->", verdict(up))
    xs, ss, us = simulate([0.4, 0.0], 4.0, 2.0, 0.0, 0.0005, 8000, 4.0)
    print("reached at", reach_time(ss, 0.0005), "s")
    print("final angle:", xs[-1, 0] if len(xs) else None)
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from plant import G_OVER_L, B_NOMINAL, D_BOUND, step, f_unknown

# Chosen gains:
#   lam = 4.0   the sliding dynamics are x1' = -4 x1, so a 0.25 s time constant.
#               Faster would need a surface the actuator cannot follow during reaching.
#   eta = 2.0   the margin above the bound. It sets the reaching guarantee
#               t_r <= |s0|/eta = 0.4 s for s0 = 1.6, and the real one is far shorter.
#   phi = 0.15  chosen so the predicted band D*phi/k = 4*0.15/25.6 = 0.023 in s
#               leaves under 6 mrad of angle, in exchange for losing the chatter.


def jacobian(f, x0, h=1e-5):
    """Central-difference Jacobian of the field f at x0."""
    x0 = np.asarray(x0, dtype=float)
    n = x0.size
    f0 = np.asarray(f(x0), dtype=float)
    J = np.zeros((f0.size, n))
    for j in range(n):
        e = np.zeros(n)
        e[j] = h
        J[:, j] = (np.asarray(f(x0 + e), dtype=float)
                   - np.asarray(f(x0 - e), dtype=float)) / (2.0 * h)
    return J


def verdict(J, tol=1e-8):
    """asymptotically stable / unstable / inconclusive."""
    J = np.asarray(J, dtype=float)
    m = float(np.max(np.real(np.linalg.eigvals(J))))
    if m < -tol:
        return "asymptotically stable"
    if m > tol:
        return "unstable"
    return "inconclusive"


def gain_bound(x):
    """A bound on |f| that holds for every admissible damping and disturbance."""
    x = np.asarray(x, dtype=float)
    return float(G_OVER_L + B_NOMINAL * abs(x[1]) + D_BOUND)


def sat(v, phi):
    """Hard sign when phi <= 0, otherwise v/phi clipped to [-1, 1]."""
    if phi <= 0.0:
        return float(np.sign(v))
    return float(max(-1.0, min(1.0, v / phi)))


def surface(x, lam):
    """s = x2 + lam * x1."""
    x = np.asarray(x, dtype=float)
    return float(x[1] + lam * x[0])


def control(x, lam, eta, phi):
    """Equivalent control plus a switching term that dominates gain_bound(x)."""
    x = np.asarray(x, dtype=float)
    s = surface(x, lam)
    return float(-lam * x[1] - (gain_bound(x) + eta) * sat(s, phi))


def simulate(x0, lam, eta, phi, dt, steps, d_amp=0.0, b=B_NOMINAL):
    """Close the loop over plant.step. Returns (xs, ss, us)."""
    x = np.array(x0, dtype=float)
    xs = np.zeros((steps, 2))
    ss = np.zeros(steps)
    us = np.zeros(steps)
    for n in range(steps):
        t = n * dt
        u = control(x, lam, eta, phi)
        xs[n] = x
        ss[n] = surface(x, lam)
        us[n] = u
        x = step(x, u, t, dt, d_amp, b)
    return xs, ss, us


def chatter(us):
    """Mean absolute change in u from one step to the next."""
    return float(np.mean(np.abs(np.diff(np.asarray(us, dtype=float)))))


def reach_time(ss, dt, tol=0.05):
    """First time |s| falls to tol or below, or inf."""
    ss = np.asarray(ss, dtype=float)
    for n in range(len(ss)):
        if abs(ss[n]) <= tol:
            return n * dt
    return float("inf")


if __name__ == "__main__":
    up = jacobian(lambda x: np.array([x[1], f_unknown(x, 0.0)]), [0.0, 0.0])
    print("upright:", np.round(up, 4).tolist(), "->", verdict(up))
    xs, ss, us = simulate([0.4, 0.0], 4.0, 2.0, 0.0, 0.0005, 8000, 4.0)
    print("reached at", reach_time(ss, 0.0005), "s")
    print("final angle:", xs[-1, 0] if len(xs) else None)
'''},
        ],
        "tests": [
            {"name": "the linearisation says upright is a saddle and hanging is not", "code": r'''
import numpy as np
from plant import f_unknown
_field = lambda x: np.array([x[1], f_unknown(x, 0.0)])
_up = jacobian(_field, [0.0, 0.0])
assert abs(_up[0, 1] - 1.0) < 1e-8 and abs(_up[0, 0]) < 1e-8, \
    f"the top row is always [0, 1] for a mechanical system in these states; got {_up[0].tolist()}"
assert abs(_up[1, 0] - 19.62) < 1e-6, \
    f"written about upright the gravity term is +g/l = +19.62, got {_up[1,0]}"
assert verdict(_up) == "unstable", \
    f"a positive bottom-left entry gives a saddle, so the equilibrium is unstable; got {verdict(_up)!r}"
_down = jacobian(_field, [np.pi, 0.0])
assert verdict(_down) == "asymptotically stable", \
    f"pi from upright is hanging down, and with damping it settles; got {verdict(_down)!r}"
_undamped = jacobian(lambda x: np.array([x[1], f_unknown(x, 0.0, 0.0, 0.0)]), [np.pi, 0.0])
assert verdict(_undamped) == "inconclusive", \
    f"remove the damping and the eigenvalues sit on the imaginary axis, where the linearisation decides nothing; got {verdict(_undamped)!r}"
'''},
            {"name": "the uncertainty bound actually bounds the uncertainty", "code": r'''
import numpy as np
from plant import f_unknown, B_NOMINAL, D_BOUND
_worst = -1e9
_where = None
for _x1 in np.linspace(-np.pi, np.pi, 21):
    for _x2 in np.linspace(-12.0, 12.0, 21):
        for _t in np.linspace(0.0, 4.0, 11):
            for _b in (0.0, B_NOMINAL):
                for _d in (D_BOUND, -D_BOUND):
                    _gap = abs(f_unknown([_x1, _x2], _t, _d, _b)) - gain_bound([_x1, _x2])
                    if _gap > _worst:
                        _worst, _where = _gap, (_x1, _x2, _t, _b, _d)
assert _worst <= 1e-9, \
    f"|f| exceeded gain_bound by {_worst:.4f} at state/time/damping/disturbance {_where} — a switching gain that does not dominate the disturbance never reaches the surface, so this bound has to hold everywhere, not on average"
assert gain_bound([0.0, 0.0]) >= 23.62 - 1e-9, \
    f"at rest the bound must still cover gravity (19.62) plus the disturbance (4); got {gain_bound([0.0, 0.0])}"
assert gain_bound([0.0, 10.0]) > gain_bound([0.0, 0.0]) + 1e-9, \
    "the damping term grows with speed, so the bound cannot be a constant"
'''},
            {"name": "the surface is reached inside its guarantee", "code": r'''
import numpy as np
_xs, _ss, _us = simulate([0.4, 0.0], 4.0, 2.0, 0.0, 0.0005, 8000, 4.0)
assert _xs.shape == (8000, 2) and _ss.shape == (8000,) and _us.shape == (8000,), \
    f"expected 8000 samples of each, got {_xs.shape}, {_ss.shape}, {_us.shape}"
assert abs(_xs[0, 0] - 0.4) < 1e-12, f"sample 0 is the state before the first step, got {_xs[0].tolist()}"
assert abs(_ss[0] - 1.6) < 1e-12, f"s(0) = 0 + 4*0.4 = 1.6, got {_ss[0]}"
_tr = reach_time(_ss, 0.0005)
assert _tr <= 1.6 / 2.0 + 1e-9, \
    f"the guarantee is t_r <= |s0|/eta = 0.8 s and it was missed ({_tr}) — check the switching gain uses gain_bound(x) + eta"
assert _tr < 0.2, \
    f"with a gain near 25 against s0 = 1.6, reaching should take under 0.1 s; got {_tr}"
'''},
            {"name": "the pendulum is held upright whatever the plant does", "code": r'''
import numpy as np
from plant import B_NOMINAL, D_BOUND
_peaks = {}
for _d in (0.0, D_BOUND, -D_BOUND):
    for _b in (0.0, B_NOMINAL):
        _xs, _ss, _us = simulate([0.4, 0.0], 4.0, 2.0, 0.0, 0.0005, 8000, _d, _b)
        _peaks[(_d, _b)] = float(np.max(np.abs(_xs[6400:, 0])))
_worst = max(_peaks.values())
assert _worst < 2e-3, \
    f"over the last fifth of the run the angle should stay inside a couple of milliradians for every admissible plant; the worst was {_worst:.6f} at (d, b) = {max(_peaks, key=_peaks.get)}"
assert max(_peaks.values()) / max(min(_peaks.values()), 1e-12) < 10.0, \
    f"the disturbance should barely change the result — that invariance is the whole reason to slide; got {_peaks}"
'''},
            {"name": "without the switching term it falls", "code": r'''
import numpy as np
from plant import step
_x = np.array([0.05, 0.0])
for _n in range(4000):
    _x = step(_x, 0.0, _n * 0.0005, 0.0005)
assert abs(_x[0]) > 1.0, \
    f"left alone the pendulum should be well past horizontal after 2 s, and it only reached {_x[0]:.4f} — if this fails the plant has been edited"
_xs, _ss, _us = simulate([0.05, 0.0], 4.0, 2.0, 0.0, 0.0005, 4000, 0.0)
assert abs(_xs[-1, 0]) < 1e-3, \
    f"from the same start the closed loop should hold it, and it drifted to {_xs[-1, 0]:.4f}"
'''},
            {"name": "the boundary layer removes the chatter", "code": r'''
import numpy as np
_, _, _hard = simulate([0.4, 0.0], 4.0, 2.0, 0.0, 0.0005, 8000, 4.0)
_, _, _soft = simulate([0.4, 0.0], 4.0, 2.0, 0.15, 0.0005, 8000, 4.0)
_ch, _cs = chatter(_hard), chatter(_soft)
assert _ch > 10.0, \
    f"with no layer the torque flips across roughly 50 units every step, so the mean change should be large; got {_ch:.4f}"
assert _cs < 0.05, f"inside the layer the torque is continuous; got {_cs:.6f}"
assert _ch / _cs > 1000.0, \
    f"the layer should cut the chatter by orders of magnitude; the ratio was {_ch / _cs:.1f}"
assert float(np.max(np.abs(_soft))) < 26.0, \
    "the peak torque inside the layer is just gain_bound + eta, about 25.6 — a larger peak means the switching term is being applied at full amplitude"
'''},
            {"name": "and the layer costs exactly what it should", "code": r'''
import numpy as np
_xs, _ss, _us = simulate([0.4, 0.0], 4.0, 2.0, 0.15, 0.0005, 8000, 4.0)
_s_band = float(np.max(np.abs(_ss[6400:])))
_predicted = 4.0 * 0.15 / (19.62 + 4.0 + 2.0)
assert abs(_s_band - _predicted) < 3e-3, \
    f"in the layer s settles where the switching balances the disturbance: D*phi/(gain_bound + eta) = {_predicted:.5f}; measured {_s_band:.5f}"
_theta = float(np.max(np.abs(_xs[6400:, 0])))
assert 1e-3 < _theta < 1e-2, \
    f"that band in s leaves an angle of roughly s/lam, a few milliradians; got {_theta:.6f}"
_xh, _sh, _ = simulate([0.4, 0.0], 4.0, 2.0, 0.0, 0.0005, 8000, 4.0)
assert _theta > 3.0 * float(np.max(np.abs(_xh[6400:, 0]))), \
    "the layer is a trade, not a free improvement: the angle must be measurably worse than with hard switching"
'''},
            {"name": "the run is deterministic", "code": r'''
import numpy as np
_a = simulate([0.4, 0.0], 4.0, 2.0, 0.15, 0.0005, 2000, 4.0)
_b = simulate([0.4, 0.0], 4.0, 2.0, 0.15, 0.0005, 2000, 4.0)
for _x, _y, _name in zip(_a, _b, ("xs", "ss", "us")):
    assert np.array_equal(np.asarray(_x), np.asarray(_y)), \
        f"{_name} differed between two identical runs — nothing here may be random, and the disturbance is a function of t alone"
'''},
        ],
    },
}
