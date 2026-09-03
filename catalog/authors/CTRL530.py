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
            "read": [
                {
                    "title": "The same block, measured twice, with two different answers",
                    "minutes": 14,
                    "body": r'''
A kilogram of aluminium sits on ceramic standoffs in still air at 20 °C. It is painted
matt black, it presents about 600 cm² of surface, and a cartridge heater is buried in
it. A thermocouple reads its temperature into a logger.

Two step tests are run on it, months apart, by two engineers who never compare notes.
The first sets the heater to 20 W, waits until the reading stops moving — it settles at
70 °C — then nudges the heater to 21 W and times how long the block takes to cover 63%
of the move it is going to make. The answer comes back at a little under half an hour.
The second engineer does the identical thing at 200 W, where the block sits at 246 °C,
nudges to 201 W, and gets under nine minutes.

Same block, same paint, same air, the same 1 W step. One of them writes 1800 s in the
commissioning file and the other writes 520 s, and neither of them made a mistake.

```python
C = 900.0          # J/K, one kilogram of aluminium
K = 3.0618e-9      # emissivity * sigma * area, in W/K^4
T_AMB = 293.0      # K, the still air around it


def net_power(T, P):
    """Watts into the block: the heater, less what the surface radiates away."""
    return P - K * (T ** 4 - T_AMB ** 4)


def equilibrium(P, lo=293.0, hi=2000.0):
    """Bisect for the temperature at which the net power is zero."""
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if net_power(mid, P) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def step_test(P, dP, dt=0.05):
    """Settle at P, add dP, and time the first 63.2% of the move."""
    T0, T1 = equilibrium(P), equilibrium(P + dP)
    target = T0 + 0.632 * (T1 - T0)
    T, t = T0, 0.0
    while T < target:
        T += dt * net_power(T, P + dP) / C
        t += dt
    return t


for P in (20.0, 200.0):
    Te = equilibrium(P)
    print(f"{P:5.0f} W settles at {Te:6.1f} K "
          f"({Te - 273.15:5.1f} C);  C/(4kT^3) = {C / (4.0 * K * Te ** 3):6.1f} s")
    for dP in (1.0, 0.1):
        print(f"        a +{dP:.1f} W step takes {step_test(P, dP):6.1f} s "
              f"to cover 63.2% of its move")
```

```text
   20 W settles at  343.4 K ( 70.2 C);  C/(4kT^3) = 1815.1 s
        a +1.0 W step takes 1792.9 s to cover 63.2% of its move
        a +0.1 W step takes 1812.3 s to cover 63.2% of its move
  200 W settles at  519.2 K (246.1 C);  C/(4kT^3) =  524.9 s
        a +1.0 W step takes  523.6 s to cover 63.2% of its move
        a +0.1 W step takes  524.7 s to cover 63.2% of its move
```

Two numbers in that output have not been explained yet, and they are the ones that
matter: 1815.1 and 524.9. They were computed from a formula rather than measured, and
each sits a fraction of a per cent from the corresponding measurement — closer, in both
cases, when the step is made smaller. That convergence is the whole subject of this
module in one line.

## The matrix that changes when you move

The block obeys one equation and it is not linear:

$$C\dot{T} = P - k\left(T^4 - T_a^4\right)$$

An *equilibrium* is a state at which the right-hand side vanishes, which is to say a
root of $f = 0$ rather than a point where the state itself is zero. Put $\dot{T} = 0$
and the heater power is exactly the radiated power: $P = k(T_e^4 - T_a^4)$. At 20 W that
gives $T_e = 343.4$ K and at 200 W it gives 519.2 K, which is what `equilibrium` bisects
for above.

Now ask what happens a little away from one of those points. Write $T = T_e + \delta$,
substitute, and expand the fourth power:

$$C\dot{\delta} = P - k\left((T_e + \delta)^4 - T_a^4\right)
                = \underbrace{P - k(T_e^4 - T_a^4)}_{=\,0}
                  - k\left(4T_e^3\delta + 6T_e^2\delta^2 + \dots\right)$$

The constant term is zero by the definition of $T_e$ — that is what an equilibrium buys
you, and it is why the expansion is taken *there* and nowhere else. Discard the
$\delta^2$ term and what is left is linear:

$$C\dot{\delta} = -4kT_e^3\,\delta \qquad\Longrightarrow\qquad
\tau = \frac{C}{4kT_e^3}$$

Nothing was announced. The $4T_e^3$ is the derivative of $T^4$, and it carries the
operating point with it because a derivative is evaluated somewhere. Put the two numbers
in: at 343.4 K, $4kT_e^3 = 0.4959$ W/K and $\tau = 900/0.4959 = 1815$ s; at 519.2 K it
is 1.7154 W/K and $\tau = 525$ s. The ratio of the two time constants is 3.46, and
$(519.2/343.4)^3$ is 3.456. The two commissioning files disagree by the cube of the
ratio of the absolute temperatures, and the disagreement was in the physics all along.

The general statement is the same calculation with more indices. For $\dot{x} = f(x)$
the linearisation at an equilibrium $x_e$ is the Jacobian

$$A = \left.\frac{\partial f}{\partial x}\right|_{x = x_e}$$

and $\dot{\delta} = A\delta$ for the deviation $\delta = x - x_e$. Every tool from
CTRL510 then applies to $A$ — eigenvalues, controllability, pole placement, the
observer, the whole apparatus — with the one restriction that the answers are about
$\delta$, near $x_e$, and about nothing else.

## Two equilibria, and a matrix for each

The block has one equilibrium, so it is a gentle example. A pendulum has two in every
turn, and they could hardly be less alike. With $x_1$ the angle from hanging and
$x_2 = \dot{x_1}$, and $g/l = 19.62\ \mathrm{s^{-2}}$ for a half-metre arm:

```python
import math

G_OVER_L = 19.62          # a 0.5 m pendulum, in 1/s^2
B = 0.2                   # the damping


def jac_pendulum(theta):
    """d/dx of [x2, -(g/l) sin x1 - b x2], evaluated at (theta, 0)."""
    return [[0.0, 1.0], [-G_OVER_L * math.cos(theta), -B]]


def eigenvalues(M):
    """The pair of a 2x2, as (real, imag) tuples."""
    tr = M[0][0] + M[1][1]
    det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
    disc = tr * tr - 4.0 * det
    r = abs(disc) ** 0.5
    if disc >= 0.0:
        return [((tr + r) / 2.0, 0.0), ((tr - r) / 2.0, 0.0)]
    return [(tr / 2.0, r / 2.0), (tr / 2.0, -r / 2.0)]


for name, theta in (("hanging", 0.0), ("upright", math.pi)):
    J = jac_pendulum(theta)
    ev = eigenvalues(J)
    print(f"{name}: J = {J}")
    print("         eigenvalues " +
          ", ".join(f"{re:+.4f}{im:+.4f}j" for re, im in ev) +
          f"   largest real part {max(re for re, im in ev):+.4f}")
```

```text
hanging: J = [[0.0, 1.0], [-19.62, -0.2]]
         eigenvalues -0.1000+4.4283j, -0.1000-4.4283j   largest real part -0.1000
upright: J = [[0.0, 1.0], [19.62, -0.2]]
         eigenvalues +4.3306+0.0000j, -4.5306+0.0000j   largest real part +4.3306
```

One entry moved, because $\cos 0 = 1$ and $\cos\pi = -1$, and the character of the
system moved with it: a lightly damped spiral at the bottom, a saddle at the top. The
saddle has a positive real eigenvalue of $+4.33$, so a milliradian of tilt becomes a
radian in $\ln(1000)/4.33 = 1.6$ s. This is why balancing a broom needs a hand that
keeps moving, and it is the picture the sandbox *One pendulum, two equilibria, two
different matrices* draws: set $a_{21}$ positive for the top, negative for the bottom,
and watch one field turn into the other.

## The mistake, and why it is tempting

The mistake is to speak of *the* linearisation of a plant, and to carry one $A$ around
as though it described the machine. It is tempting because in CTRL510 that was true.
There, $A$ came from the hardware and held still, and a sentence like "the plant has a
time constant of 1815 s" was a complete statement about a piece of equipment.

Here it is not, and the block shows exactly how it fails. A controller tuned on the 20 W
model, with an integrator sized for a 1815 s lag, is driving a plant that responds 3.5
times faster when the process runs hot — and a loop tuned for a lag it does not have
overshoots and then hunts. The failure does not look like a modelling error, either. It
looks like the plant drifted, because the same controller behaved differently on a
Tuesday.

The correct sentence names the point: *at 70 °C* the block has a time constant of 1815
s. Anything else needs re-linearising, and the useful habit is to write $A(x_e)$ rather
than $A$ until the coordinates are pinned down.

## The one case where the Jacobian says nothing

Hartman–Grobman is the theorem that licenses all of this: where no eigenvalue of $A$
lies on the imaginary axis, the non-linear flow near $x_e$ is a continuous deformation
of the linear one. Stability, instability and the saddle structure all carry across
unchanged. The condition has a name — *hyperbolic* — and it is the entire condition. Not
"the non-linearity is small", not "the system is second order". One eigenvalue on the
axis and the theorem withdraws.

What it withdraws is worth seeing, because the withdrawal is total rather than partial.
Three scalar fields, each with derivative exactly zero at the origin, so each with the
identical linearisation $\dot{\delta} = 0$:

```python
def escape(f, x0, dt, seconds):
    """Euler the scalar field f from x0 and report where it ends up."""
    x, n = x0, int(seconds / dt)
    for _ in range(n):
        x += dt * f(x)
        if abs(x) > 1e6:
            return None
    return x


fields = (("-x**3", lambda x: -x ** 3),
          ("+x**3", lambda x: +x ** 3),
          (" x**2", lambda x: x ** 2))
for label, f in fields:
    ends = []
    for x0 in (0.5, -0.5):
        end = escape(f, x0, 1e-4, 40.0)
        ends.append("blew up" if end is None else f"{end:+.5f}")
    print(f"xdot = {label}:  f'(0) = 0.0   from +0.5 -> {ends[0]:>9}"
          f"   from -0.5 -> {ends[1]:>9}")
```

```text
xdot = -x**3:  f'(0) = 0.0   from +0.5 ->  +0.10911   from -0.5 ->  -0.10911
xdot = +x**3:  f'(0) = 0.0   from +0.5 ->   blew up   from -0.5 ->   blew up
xdot =  x**2:  f'(0) = 0.0   from +0.5 ->   blew up   from -0.5 ->  -0.02381
```

Asymptotically stable, unstable, and stable from one side while unstable from the other.
Three different answers from one Jacobian, and the Jacobian was not wrong about any of
them — it never made a claim. The derivation *Linearising a pendulum, and one system
where it lies* takes the first of these all the way to a closed form, and the decay it
finds is $x_0/\sqrt{1 + 2x_0^2t}$: an algebraic decay, not an exponential one, which no
linear system produces and no linear model could have predicted.

## Where this stops holding

Two limits, and the second is the one that bites.

The conclusion is *local*, and the linearisation contains no measure of how local. The
Jacobian at the block's 70 °C point is as valid at 70.001 °C as at 200 °C by its own
lights; it is the discarded $6kT_e^2\delta^2$ term that decides, and reading its size
means going back to the non-linear equation. Estimating a region of attraction is what
module 2 does with Lyapunov functions, and it is a genuinely different technique rather
than a refinement of this one.

And the conclusion is about the *deviation*. A linearisation that reports "asymptotically
stable" is promising that small deviations shrink, which is compatible with the state
leaving for good if the deviation is not small. The undamped pendulum is the cleanest
warning: set $b = 0$ and the hanging eigenvalues are $\pm 4.43j$, purely imaginary, and
the linearisation returns to saying nothing. Whether a real pendulum with dry friction in
the pivot settles or creeps is decided entirely by terms that were discarded on the first
line.

## What you are about to build

The lab *Linearise anything, and know when not to believe it* asks for the numerical
version of everything above: `jacobian(f, x0, h)` by central differences, and
`verdict(J, tol)` returning `"asymptotically stable"`, `"unstable"` or `"inconclusive"`
from the largest real part. That third string is the point of the whole lab. Its tests
check that the hanging pendulum comes back stable, the upright one unstable, and the
undamped one and the cubic both `"inconclusive"` — and the last test runs $\dot{x} =
-x^3$ from $x = 1$ and from $x = 5$ and asserts the two land within a few per cent of
each other, which no exponential decay does. Reporting stability for the cubic would be
a true statement the Jacobian does not support, and a gate that accepted it would be
teaching the habit this module exists to break.
''',
                },
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
            "read": [
                {
                    "title": "The fault that lasted forty milliseconds too long",
                    "minutes": 15,
                    "body": r'''
A 588 MVA turbo-alternator is running into a transmission line, delivering 0.8 of its
rated power. Its rotor angle — how far the machine's magnetic axis leads the grid's —
sits at 26.4°, and it has been there all afternoon. An inertia constant of 3 s, a
50 Hz system and a line that can carry 1.8 per unit at most.

A three-phase fault appears on the line. While it is on, the machine can export nothing,
so the turbine's 0.8 pu keeps arriving and the rotor accelerates. The protection clears
the fault and the line comes back. Two recorders, on two different occasions, catch a
fault cleared at 220 ms and one cleared at 260 ms.

```python
import math

M = 2 * 3.0 / (2 * math.pi * 50.0)   # 2H/ws, for H = 3 s at 50 Hz
PM = 0.8                             # mechanical power in, per unit
PMAX = 1.8                           # the most the line can carry
D = 0.02                             # damping, per unit
D0 = math.asin(PM / PMAX)            # the angle the machine runs at


def run(clear_at, seconds=8.0, dt=1e-5):
    """Fault at t = 0 with the line open, restored at `clear_at`."""
    delta, omega, peak, late = D0, 0.0, D0, []
    for n in range(int(seconds / dt)):
        pmax = 0.0 if n * dt < clear_at else PMAX
        acc = (PM - pmax * math.sin(delta) - D * omega) / M
        delta, omega = delta + dt * omega, omega + dt * acc
        peak = max(peak, delta)
        if n * dt > seconds - 1.0:
            late.append(delta)
    return math.degrees(peak), math.degrees(min(late)), math.degrees(max(late))


print(f"the machine runs at {math.degrees(D0):.2f} deg")
for tc in (0.220, 0.260):
    peak, lo, hi = run(tc)
    print(f"  cleared at {tc * 1000:.0f} ms: peak {peak:7.1f} deg,"
          f"  over the last second {lo:8.1f} to {hi:8.1f} deg")

# The linearisation at the operating angle. It is the same in both runs.
a21 = -PMAX * math.cos(D0) / M
a22 = -D / M
print(f"A = [[0, 1], [{a21:.3f}, {a22:.4f}]]  ->  eigenvalues "
      f"{a22 / 2:.4f} +/- {math.sqrt(-4 * a21 - a22 * a22) / 2:.4f}j")
```

```text
the machine runs at 26.39 deg
  cleared at 220 ms: peak   115.1 deg,  over the last second     24.2 to     28.2 deg
  cleared at 260 ms: peak 15870.7 deg,  over the last second  13578.8 to  15870.7 deg
A = [[0, 1], [-84.428, -1.0472]]  ->  eigenvalues -0.5236 +/- 9.1735j
```

Forty milliseconds, two turbine revolutions apart, and the outcomes are not on the same
scale. The first swings to 115°, comes back, and rings down towards 26.4° again. The
second passes 15 870° and is still climbing: the rotor has slipped forty-four poles and
the machine is being disconnected by its own protection.

## The question the eigenvalues cannot be asked

The last line of that output is the whole difficulty. The linearisation at the operating
angle is $-0.52 \pm 9.17j$ — a 1.46 Hz oscillation decaying with a time constant of
1.9 s — and it is *the same matrix in both runs*, because both runs return to the same
operating point on the same line with the same everything. Module 1's machinery is
working perfectly and answering a question nobody asked: does a small enough deviation
decay? Yes. Both times.

What is being asked is how large a deviation the machine survives, and the linearisation
contains no such number. There is nothing to compute. The Jacobian is the first term of a
series and has thrown away the very terms that make $\sin\delta$ turn over at 90° and
start helping the fault instead of opposing it.

Lyapunov's method answers it without solving the differential equation and without
linearising anything.

## A scalar that only falls

Take the machine's own energy, in the frame that rotates with the grid. Kinetic energy
of the rotor is $\tfrac{1}{2}M\omega^2$ with $\omega = \dot{\delta}$. Potential energy
is the net work done in getting from $\delta_0$ to $\delta$: the turbine puts in
$P_m(\delta - \delta_0)$ and the line takes out
$\int_{\delta_0}^{\delta} P_{max}\sin\sigma\,\mathrm{d}\sigma$. Subtract:

$$V(\delta, \omega) = \tfrac{1}{2}M\omega^2 - P_m(\delta - \delta_0)
                      - P_{max}\left(\cos\delta - \cos\delta_0\right)$$

That is a construction, not a guess. Check the two conditions on it. It is zero at the
operating point by inspection. Is it positive nearby? Its gradient in $\delta$ is
$-P_m + P_{max}\sin\delta$, which vanishes at $\delta_0$ precisely because $\delta_0$ is
the equilibrium, and its second derivative there is $P_{max}\cos\delta_0 = 1.612 > 0$.
So $V$ has a strict minimum at the operating point, which is what positive definite
means locally.

Now differentiate along the trajectories — the step where the dynamics enter, and the
only step where they do:

$$\dot{V} = \frac{\partial V}{\partial \delta}\dot{\delta}
          + \frac{\partial V}{\partial \omega}\dot{\omega}
          = \left(P_{max}\sin\delta - P_m\right)\omega + M\omega\dot{\omega}$$

Substitute the swing equation, $M\dot{\omega} = P_m - P_{max}\sin\delta - D\omega$:

$$\dot{V} = \left(P_{max}\sin\delta - P_m\right)\omega
          + \omega\left(P_m - P_{max}\sin\delta - D\omega\right) = -D\omega^2$$

Every term carrying $\sin\delta$ cancelled. Nothing was linearised, no small-angle
approximation was taken, and the result holds at 26° and at 115° alike. The same
cancellation happens for the pendulum in the derivation *Proving stability without
solving*, and for the spring before it — the pattern is that the conservative part of a
mechanical system moves energy between two terms of $V$ and can never change the total,
so what survives is exactly the dissipation.

## Semi-definite is not a failure

$\dot{V} = -D\omega^2$ is not negative definite. It vanishes on the whole line
$\omega = 0$, not at one point, so the strict-decrease argument stops short: $V$ never
grows, the state stays inside whatever level set it started in, and that is stability
without any promise of convergence.

LaSalle finishes it. Ask where a trajectory could *remain* while $\dot{V} = 0$. It would
have to keep $\omega = 0$, and therefore $\dot{\omega} = 0$, and the swing equation then
forces $P_{max}\sin\delta = P_m$ — which happens at $\delta_0$ and at $\pi - \delta_0$
and nowhere between. So inside any region around the operating point that excludes the
other root, the largest invariant set in $\{\dot{V} = 0\}$ is the operating point alone,
and the machine converges to it. A trajectory that reaches $\omega = 0$ anywhere else is
immediately pushed off that line by an acceleration that is not zero.

This is the ordinary case rather than the exotic one, because damping in a mechanical
system almost always acts on velocity and velocity almost always passes through zero.
Reaching for a cleverer $V$ when the natural one gives a semi-definite derivative is
usually wasted effort; LaSalle is the tool the situation calls for.

## Where the boundary actually is

$V$ never grows, so a trajectory cannot leave the level set it starts in. The rotor
angle is therefore trapped — unless the level set it starts in is open at one end.

The other equilibrium, $\delta_u = \pi - \delta_0 = 153.6°$, is a saddle, and $V$ there
is a local maximum along the $\delta$ axis. It is the ridge of the potential well. If
the machine is inside the well when the line comes back, $V$ can only fall and it slides
to the bottom. If it is over the ridge, $V$ still falls and it slides down the far side,
which is 360° away.

```python
import math

M = 2 * 3.0 / (2 * math.pi * 50.0)
PM, PMAX, D = 0.8, 1.8, 0.02
D0 = math.asin(PM / PMAX)


def V(delta, omega):
    """Kinetic energy, less the net work done getting to this angle."""
    return (0.5 * M * omega ** 2 - PM * (delta - D0)
            - PMAX * (math.cos(delta) - math.cos(D0)))


def clearing_state(clear_at, dt=1e-6):
    """Angle and speed at the instant the fault is cleared."""
    delta, omega = D0, 0.0
    for _ in range(int(clear_at / dt)):
        delta, omega = delta + dt * omega, omega + dt * (PM - D * omega) / M
    return delta, omega


d_u = math.pi - D0                       # the other root of PM = PMAX sin(delta)
v_cr = V(d_u, 0.0)
print(f"the ridge sits at {math.degrees(d_u):.2f} deg, and V there is {v_cr:.4f}")
for tc in (0.220, 0.260):
    d, w = clearing_state(tc)
    print(f"  cleared at {tc * 1000:.0f} ms: angle {math.degrees(d):6.2f} deg, "
          f"V = {V(d, w):.4f}  ->  {'over' if V(d, w) > v_cr else 'under'} the ridge")

# The largest angle the machine may be at when the line comes back.
d_cr = math.acos(math.cos(D0) - v_cr / PMAX)
print(f"critical angle {math.degrees(d_cr):.2f} deg, reached at "
      f"{math.sqrt(2 * M * (d_cr - D0) / PM) * 1000:.1f} ms")
```

```text
the ridge sits at 153.61 deg, and V there is 1.4485
  cleared at 220 ms: angle  80.25 deg, V = 1.2025  ->  under the ridge
  cleared at 260 ms: angle 100.62 deg, V = 1.7757  ->  over the ridge
critical angle 84.77 deg, reached at 220.6 ms
```

One number, 1.4485, separates the two recordings — and it was obtained by evaluating a
formula at a saddle point, with no simulation of the fault at all. Simulating the real
machine and bisecting on the clearing time puts the true boundary at 244.9 ms. The
energy criterion says 220.6 ms: conservative by 11%, and conservative is the direction a
sufficient condition is supposed to err in. The gap is the damping, which was ignored in
the closed form and which removes a little energy during the swing out.

The protection engineer sets the relay from the 220.6 ms figure, and does so knowing it
is pessimistic, because the alternative is a number obtained by simulating every fault
location on every line in every configuration.

## The mistake, and why it is tempting

The mistake is reading a failed $V$ as an unstable system. The condition is sufficient
and never necessary, and the usual first candidate fails on systems that are perfectly
stable. Take the sum of squares — the circles the sandbox *Does every trajectory cross
the circles inwards* draws — and try it on this machine's own linearisation.

```python
import math

# The swing equation linearised at the operating angle, from the reading above.
A = [[0.0, 1.0], [-84.4278, -1.04719]]


def vdot(P, x):
    """d/dt of x.T P x along xdot = Ax, computed entry by entry."""
    f = [A[0][0] * x[0] + A[0][1] * x[1], A[1][0] * x[0] + A[1][1] * x[1]]
    grad = [2 * (P[0][0] * x[0] + P[0][1] * x[1]),
            2 * (P[1][0] * x[0] + P[1][1] * x[1])]
    return grad[0] * f[0] + grad[1] * f[1]


def lyap_2x2(A):
    """Solve A.T P + P A = -I for the symmetric P, by hand."""
    a, b = A[1][0], A[1][1]              # the field is [[0, 1], [a, b]]
    p2 = -1.0 / (2.0 * a)
    p3 = (-1.0 - 2.0 * p2) / (2.0 * b)
    p1 = -b * p2 - a * p3
    return [[p1, p2], [p2, p3]]


circle = [[1.0, 0.0], [0.0, 1.0]]
r = 0.5 ** 0.5
print("V = x1^2 + x2^2, the circle:")
for x in ([r, r], [r, -r]):
    print(f"   at ({x[0]:+.4f}, {x[1]:+.4f})  Vdot = {vdot(circle, x):+9.4f}")

P = lyap_2x2(A)
print(f"V = x.T P x with P = [[{P[0][0]:.4f}, {P[0][1]:.6f}], "
      f"[{P[1][0]:.6f}, {P[1][1]:.4f}]]:")
for x in ([r, r], [r, -r]):
    print(f"   at ({x[0]:+.4f}, {x[1]:+.4f})  Vdot = {vdot(P, x):+9.4f}")
print(f"   the level sets are ellipses {math.sqrt(P[0][0] / P[1][1]):.2f} "
      f"times wider in x2 than in x1")
```

```text
V = x1^2 + x2^2, the circle:
   at (+0.7071, +0.7071)  Vdot =  -84.4750
   at (+0.7071, -0.7071)  Vdot =  +82.3806
V = x.T P x with P = [[40.7953, 0.005922], [0.005922, 0.4831]]:
   at (+0.7071, +0.7071)  Vdot =   -1.0000
   at (+0.7071, -0.7071)  Vdot =   -1.0000
   the level sets are ellipses 9.19 times wider in x2 than in x1
```

On the circle, $\dot{V}$ is $+82.4$ in one direction. A trajectory through that point is
moving *outwards*, and anyone who tried the circle and stopped there would report a
stable machine as unproved. The circle is not wrong about the system; it is the wrong
shape. An angle in radians and a speed in radians per second are not comparable
quantities, and the sum of their squares treats them as though they were.

The right shape falls out of a linear solve. For $\dot{x} = Ax$ and $V = x^\top Px$,
$\dot{V} = x^\top(A^\top P + PA)x$, so demanding $\dot{V} = -x^\top Qx$ means solving
$A^\top P + PA = -Q$ — a *linear* equation in the entries of $P$, which is why the
search for a Lyapunov function stops being a search at all. The $P$ above is stretched
9.19 times in the speed direction, and 9.19 is $\omega_n$, the natural frequency: the
ellipse is exactly as elongated as the orbit it has to contain.

## Where this stops holding

Three limits, in increasing order of how much trouble they cause.

The estimate is conservative. The sublevel set $\{V < 1.4485\}$ is contained in the
region of attraction, not equal to it, and the 220.6 ms against 244.9 ms above is that
gap made numerical. A tighter $V$ tightens the estimate; no $V$ delivers the true
boundary.

The certificate's *rate* can be far looser than its verdict. From $A^\top P + PA = -Q$
the bound is $V(t) \le V(0)e^{-\alpha t}$ with $\alpha = \lambda_{\min}(Q)/\lambda_{\max}(P)$,
which here is $1/40.795 = 0.0245$ — against a true decay of $2 \times 0.5236 = 1.047$,
a factor of forty-three. The verdict is exact and the rate is a bound, and an
ill-conditioned $P$ makes it a weak one.

And the energy function itself is a privilege of a particular model. The classical swing
equation above has no transfer conductance — no resistive path that dissipates power as
a function of angle. Put resistance into the network and the exact $V$ stops existing;
the whole transient-energy literature is about what to use instead. Lyapunov's theorem
still holds. Finding the function is where the work is, and there is no procedure that
always produces one.

## What you are about to build

The lab *Solve the Lyapunov equation and use what it gives you* takes the linear
specialisation and makes it computational: `lyap(A, Q)` flattens $A^\top P + PA = -Q$
into a Kronecker system and solves it, `is_pos_def(M)` checks the certificate, and
`v_trace` follows $V$ down a real trajectory. One of its tests hands `lyap` an
*unstable* $A$ and asserts that the solve still returns a matrix — one that is not
positive definite. That is how the method reports instability: not by failing, but by
handing back something that is not a Lyapunov function. Its final test checks the decay
bound $\alpha = \lambda_{\min}(Q)/\lambda_{\max}(P)$ derived above, on a plant where it
comes to 0.1586. The fill-in *Lyapunov, without solving anything* walks the conditions
one at a time, and the sandbox lets you set $a_{11}$ and $a_{22}$ to zero and watch
$\dot{V}$ go to zero with them — stability with no convergence, which is where LaSalle
starts.
''',
                },
            ],
            "quiz": {
                "title": "Certifying stability without a solution",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Along a trajectory of $\\dot{x} = f(x)$, what is $\\dot{V}$ for a scalar $V(x)$?",
                        "opts": [
                            "$\\partial V/\\partial t$, the explicit time derivative of $V$",
                            "$\\nabla V$, the gradient of $V$ at the current state",
                            "$\\nabla V \\cdot f(x)$, the gradient contracted with the field",
                            "$f(x)$ itself, scaled by the current value of $V$ at that point",
                        ],
                        "a": 2,
                        "whys": [
                            r"$V$ here is a function of the state alone and carries no explicit $t$, so that derivative is zero. All of its variation arrives through $x(t)$, which is exactly the dependence the chain rule is needed for.",
                            r"The gradient is a vector and points uphill in state space; a rate of change is a scalar. Without contracting it against something that says how the state is moving, the field never appears and the conclusion could not be about this system.",
                            r"The chain rule on $V(x(t))$, and it is the only step at which the dynamics enter the argument. Nothing is integrated, which is why the method never needs a solution.",
                            r"Scaling the field by $V$ gives a vector with the wrong units and no relation to how fast $V$ changes. It also drops $\nabla V$, so the shape of $V$ stops mattering.",
                        ],
                        "why": r"""
$\dot{V} = \nabla V \cdot \dot{x} = \nabla V \cdot f(x)$, by the chain rule. This is
where $f$ enters and the only place it does — which is the whole economy of the method,
because the vector field is used without ever being integrated. For the generator in the
reading, $\nabla V = (P_{max}\sin\delta - P_m,\ M\omega)$ and contracting it with the
swing equation makes every $\sin\delta$ cancel, leaving $-D\omega^2$ at any angle, small
or not.
""",
                    },
                    {
                        "q": "A natural energy $V$ gives $\\dot{V} = -D\\omega^2$, which vanishes on the whole line $\\omega = 0$. What follows directly?",
                        "opts": [
                            "Asymptotic stability, since $\\dot{V}$ is never positive anywhere",
                            "Stability, with the convergence still to be argued separately",
                            "Nothing at all, because $\\dot{V}$ is not negative definite",
                            "Instability, since $V$ can stop falling away from the origin",
                        ],
                        "a": 1,
                        "whys": [
                            r"Never positive is not the same as strictly negative. An undamped pendulum has $\dot{V} = 0$ everywhere and orbits forever without approaching anything, so the semi-definite case genuinely does contain non-convergent systems.",
                            r"$V$ is non-increasing, so a trajectory cannot leave the level set it began in — a real conclusion, and often the one that was wanted. Convergence needs LaSalle, or a different $V$.",
                            r"Too pessimistic, and it throws away the useful half. Boundedness of the state is precisely what a non-increasing $V$ delivers, and for many designs that is the specification.",
                            r"A quantity that never grows cannot certify escape. Instability needs its own argument — a $V$ that increases along trajectories near the equilibrium, which is a different theorem.",
                        ],
                        "why": r"""
Non-increasing $V$ traps the state inside its starting level set: that is stability, and
it is a real result rather than a consolation prize. What it does not give is
convergence, because the trajectory might settle onto a level set and circle there. The
repair is LaSalle: ask where a trajectory could *stay* with $\dot{V} = 0$. On
$\omega = 0$ the machine has $M\dot{\omega} = P_m - P_{max}\sin\delta$, which is zero
only at the two equilibria, so anywhere else it is pushed straight off the line and
cannot remain.
""",
                    },
                    {
                        "q": "You try $V = x_1^2 + x_2^2$ on a plant and find $\\dot{V} > 0$ somewhere. What have you established?",
                        "opts": [
                            "The plant is unstable, since a trajectory moves away from the origin",
                            "The plant is stable but not asymptotically, as on a closed orbit",
                            "The plant has a limit cycle passing through that point",
                            "Nothing about the plant — that candidate failed, and another may not",
                        ],
                        "a": 3,
                        "whys": [
                            r"The state does move outward across *that circle* at that point, which is what makes the reading appealing — but crossing one level set outwards says nothing about where the trajectory goes, and it may cross back and converge.",
                            r"Closed orbits give $\dot{V} = 0$ around the loop, not a positive value. A strictly positive $\dot{V}$ somewhere is compatible with convergence, with divergence, and with a cycle.",
                            r"Nothing here is periodic. A single sign of $\dot{V}$ at a single point constrains neither the existence of a closed orbit nor its location.",
                            r"The condition is sufficient and never necessary. The reading's own generator is provably stable and the circle reports $\dot{V} = +82.4$ on it, because an angle and an angular rate are not comparable quantities to add in squares.",
                        ],
                        "why": r"""
A failed candidate is a failed candidate. Lyapunov's theorem gives one direction only: a
$V$ that works proves stability, and no $V$ found proves nothing. The reading makes this
concrete — the circle gives $\dot{V} = +82.4$ at one point on a machine whose
eigenvalues are $-0.52 \pm 9.17j$, and the ellipse that comes out of
$A^\top P + PA = -I$ gives $\dot{V} = -1$ at the same point. The circle was the wrong
shape, not evidence.
""",
                    },
                    {
                        "q": "Why is a Lyapunov estimate of a region of attraction always conservative?",
                        "opts": [
                            "Numerical integration of $\\dot{V}$ accumulates error over the run",
                            "$V$ is only defined near the equilibrium, so it cannot reach further",
                            "It reports a sublevel set inside the true region, not the region",
                            "It assumes the linearisation holds over the whole set",
                        ],
                        "a": 2,
                        "whys": [
                            r"Nothing is integrated. The whole appeal of the direct method is that $\dot{V}$ is evaluated algebraically from $\nabla V$ and $f$, so there is no run over which error could accumulate.",
                            r"$V$ in the reading is defined for every angle, and it is evaluated at the saddle 127° away from the operating point. Its domain is not the limitation.",
                            r"What the argument delivers is a set the state cannot leave, and the largest such sublevel set fits inside the true basin rather than filling it. A better $V$ enlarges the estimate; none of them attains it.",
                            r"It assumes the opposite. The generator's $\dot{V} = -D\omega^2$ was derived from the full $\sin\delta$ with no approximation, which is why it is trusted at 115° where a linearisation would be meaningless.",
                        ],
                        "why": r"""
The argument certifies a *sublevel set*: since $V$ cannot increase, a state inside
$\{V < c\}$ stays inside it, and the largest usable $c$ is the value of $V$ at the
nearest point where the argument breaks — the saddle, for the generator. The true basin
is bounded by the saddle's stable manifold, a curve no level set of $V$ follows exactly,
so the inscribed set is strictly smaller. In the reading that gap is 220.6 ms against a
true 244.9 ms, and the error is in the safe direction: the relay is set early.
""",
                    },
                    {
                        "q": "For $\\dot{x} = Ax$, why does taking $V = x^\\top Px$ turn the search for a Lyapunov function into a solve?",
                        "opts": [
                            "The eigenvectors of $A$ can be read straight off the entries of $P$",
                            "$\\dot{V} = x^\\top(A^\\top P + PA)x$, which is linear in the unknown $P$",
                            "Every stable $A$ has $P = I$ as a certificate, so nothing is searched for",
                            "A quadratic $V$ makes $\\dot{V}$ quadratic, hence automatically negative",
                        ],
                        "a": 1,
                        "whys": [
                            r"$P$ and $A$ share no eigenvectors in general, and the solve is done to avoid an eigen-decomposition rather than to produce one.",
                            r"Setting that equal to $-x^\top Qx$ leaves $A^\top P + PA = -Q$, whose unknown appears once and to the first power. A search over functions collapses into one linear system.",
                            r"The reading's own machine refutes this: $P = I$ is the circle, and it gives $\dot{V} = +82.4$ at a point on a stable plant. Identity works for some $A$ and fails for many.",
                            r"A quadratic form is negative only if its matrix is negative definite, which is a condition to be arranged rather than a consequence of the degree. $x^\top x$ is quadratic and positive everywhere.",
                        ],
                        "why": r"""
$\dot{V} = \dot{x}^\top Px + x^\top P\dot{x} = x^\top(A^\top P + PA)x$, so requiring
$\dot{V} = -x^\top Qx$ for a chosen positive definite $Q$ gives $A^\top P + PA = -Q$.
The unknown $P$ enters once and linearly, so vectorising turns it into $n^2$ equations
in $n^2$ unknowns — the Kronecker system the lab builds. That the answer exists and is
positive definite for every stable $A$ and every positive definite $Q$ is the converse
theorem, and it is why a failed quadratic on a *linear* plant means the plant is
unstable, while a failed quadratic on a non-linear one means nothing.
""",
                    },
                    {
                        "q": "The generator's $\\dot{V} = -D\\omega^2$ was derived with no small-angle approximation. What made the $\\sin\\delta$ terms cancel?",
                        "opts": [
                            "The angles stayed small enough for $\\sin\\delta$ to equal $\\delta$",
                            "The damping term dominates the restoring term at every angle",
                            "The sine was expanded and the higher-order terms were discarded",
                            "$V$ was built as the work integral of the same force in the field",
                        ],
                        "a": 3,
                        "whys": [
                            r"The peak angle in the surviving run is 115°, where $\sin\delta$ is 0.906 and $\delta$ is 2.007 — not remotely equal. If the derivation had needed that, it could not have been used for the fault at all.",
                            r"It does not: $D\omega$ is 0.02 per unit of speed against a restoring term reaching 1.8. The damping is what *survives* the cancellation, not what overwhelms it.",
                            r"Nothing was expanded and nothing was discarded. A truncated sine would have left a residue growing with angle, and the result would not hold at 115°.",
                            r"$\partial V/\partial \delta$ is $P_{max}\sin\delta - P_m$ by construction, and $M\dot{\omega}$ contains the same expression negated. Conservative forces move energy between the two terms of $V$ and cannot change the total.",
                        ],
                        "why": r"""
The potential half of $V$ is $-P_m(\delta - \delta_0) - P_{max}(\cos\delta -
\cos\delta_0)$, whose $\delta$-derivative is $P_{max}\sin\delta - P_m$ — the negative of
the conservative part of the swing equation, because that is how the integral was
constructed. Contracting the gradient with the field therefore pairs each conservative
term with itself and subtracts. This is a general pattern rather than an accident of
this plant: energy built from the field cancels against the field, and only the
dissipative terms survive into $\dot{V}$. The same cancellation is worked twice in
*Proving stability without solving*, once for a spring and once for a pendulum.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Two oscillator boards, and only one of them keeps its amplitude",
                    "minutes": 14,
                    "body": r'''
Two oscillator boards sit on the bench, built around identical 1 kHz LC tanks. Each has
a JFET stage feeding energy back into the tank to make up the loss in the coil.

Board A has the feedback trimmed with a multiturn pot until the loop gain reads exactly
one at the operating point, so the negative resistance the stage presents cancels the
tank's loss precisely. Board B does no trimming: its stage is deliberately non-linear,
presenting a strong negative conductance for small signals that fades and reverses as
the swing grows.

Each board is kicked twice, once with a 0.1 V pulse and once with a 3.0 V pulse, and the
envelope is read off the scope after it has stopped changing. Normalise time to the
tank's own frequency and both boards are the same pair of equations with one parameter
between them.

```python
def vdp(x, mu):
    """x1' = x2,  x2' = mu (1 - x1^2) x2 - x1.  mu = 0 is the linear board."""
    return [x[1], mu * (1.0 - x[0] ** 2) * x[1] - x[0]]


def rk4(f, x, mu, dt, steps):
    """Classical fourth-order Runge-Kutta, the stepper the lab asks for."""
    for _ in range(steps):
        k1 = f(x, mu)
        k2 = f([x[i] + 0.5 * dt * k1[i] for i in range(2)], mu)
        k3 = f([x[i] + 0.5 * dt * k2[i] for i in range(2)], mu)
        k4 = f([x[i] + dt * k3[i] for i in range(2)], mu)
        x = [x[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
             for i in range(2)]
        yield x


def settled_amplitude(mu, x0, dt=0.002, steps=20000):
    """Peak |x1| over the second half of the run, once the transient is gone."""
    peak = 0.0
    for n, x in enumerate(rk4(vdp, list(x0), mu, dt, steps)):
        if n >= steps // 2:
            peak = max(peak, abs(x[0]))
    return peak


for mu, label in ((0.0, "linear board  "), (1.0, "van der Pol   ")):
    small = settled_amplitude(mu, [0.1, 0.0])
    big = settled_amplitude(mu, [3.0, 0.0])
    print(f"{label} kicked to 0.1 -> {small:.5f}   kicked to 3.0 -> {big:.5f}")
```

```text
linear board   kicked to 0.1 -> 0.10000   kicked to 3.0 -> 3.00000
van der Pol    kicked to 0.1 -> 2.00862   kicked to 3.0 -> 2.00862
```

Board A remembers its kick forever. Board B forgets it entirely: a start thirty times
smaller ends on the same orbit to five figures. Nothing in CTRL510 or CTRL520 produces
the second row, and the reason is not that the analysis there was incomplete.

## What the linear board is actually doing

Board A is a *centre*: trace zero, determinant positive, eigenvalues on the imaginary
axis. It does have closed orbits, and that is what makes it tempting to call it an
oscillator. But there is a closed orbit through every point of the plane, one for each
amplitude, nested like the rings of a tree. None of them is isolated. None has a
neighbourhood free of other closed orbits, so no trajectory can be said to approach any
particular one — the amplitude is a free constant fixed by whatever the kick happened to
be, which is exactly the first row of the output.

Worse, the family is held together by an equality that no hardware maintains.

```python
def linear_board(x, eps):
    """The tank with the feedback trimmed eps away from exact cancellation."""
    return [x[1], -x[0] + eps * x[1]]


def rk4(f, x, p, dt, steps):
    for _ in range(steps):
        k1 = f(x, p)
        k2 = f([x[i] + 0.5 * dt * k1[i] for i in range(2)], p)
        k3 = f([x[i] + 0.5 * dt * k2[i] for i in range(2)], p)
        k4 = f([x[i] + dt * k3[i] for i in range(2)], p)
        x = [x[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
             for i in range(2)]
        yield x


def after(eps, seconds, dt=0.002):
    peak = 0.0
    steps = int(seconds / dt)
    for n, x in enumerate(rk4(linear_board, [1.0, 0.0], eps, dt, steps)):
        if n >= steps - int(6.3 / dt):
            peak = max(peak, abs(x[0]))
    return peak


print("the trimmed tank, starting at amplitude 1.000")
for eps in (0.0, -0.002, 0.002):
    print(f"  feedback error {eps:+.3f}:  after 60 s {after(eps, 60.0):8.4f}"
          f"   after 300 s {after(eps, 300.0):10.4f}")
```

```text
the trimmed tank, starting at amplitude 1.000
  feedback error +0.000:  after 60 s   1.0000   after 300 s     1.0000
  feedback error -0.002:  after 60 s   0.9450   after 300 s     0.7443
  feedback error +0.002:  after 60 s   1.0615   after 300 s     1.3478
```

Two parts in a thousand of trim error, which is less than the tempco of the pot, and the
amplitude has moved a quarter of the way to zero or a third of the way to the rail in
five minutes — and it keeps going, because nothing stops it. The whole family of orbits
is destroyed by an arbitrarily small perturbation, which is what *structurally unstable*
means. The sandbox *Hunting for a closed orbit in a linear field* is the same experiment
with a slider: nudge $a_{22}$ off zero and every orbit opens at once.

So board A is not an oscillator that needs better trimming. It is an oscillator that
cannot be trimmed, because the property being asked for does not survive in any
neighbourhood of the setting that provides it.

## Reading the plane instead of solving it

Board B has no such equality to maintain, and it can be understood without solving
anything. Two tools do most of the work in the plane.

The *nullclines* are the curves where one component of $\dot{x}$ vanishes. Here
$\dot{x_1} = x_2$ is zero on the horizontal axis, so trajectories cross that axis
vertically; and $\dot{x_2} = 0$ on the curve $x_2 = x_1/(\mu(1 - x_1^2))$, crossed
horizontally. They meet only at the origin, which is therefore the only equilibrium.
Linearise there and the Jacobian is $\begin{bmatrix} 0 & 1 \\ -1 & \mu \end{bmatrix}$,
with trace $\mu > 0$: an unstable focus. Everything near the origin is leaving.

The *divergence* decides where a closed orbit can live:

$$\nabla\!\cdot f = \frac{\partial f_1}{\partial x_1} + \frac{\partial f_2}{\partial x_2}
                  = 0 + \mu\left(1 - x_1^2\right)$$

Bendixson's criterion says that on a simply connected region where this keeps one strict
sign, no closed orbit fits entirely inside. The sign changes at $|x_1| = 1$ and nowhere
else, so a closed orbit is obliged to straddle that pair of vertical lines. It cannot
hide in the middle strip, where the field is expanding areas, and it cannot stay outside,
where the field is contracting them. That single observation already places the orbit
before any energy argument is made, and it is what the derivation *Where van der Pol's
cycle comes from* establishes in its first two steps.

Notice what the divergence *is*, physically: with $|x_1| < 1$ the damping coefficient is
negative, so the stage is pumping; beyond $|x_1| = 1$ it is positive and the stage is
absorbing. A trajectory that swings past 1 spends part of each cycle being fed and part
being drained.

## Where the amplitude is set

That balance is the amplitude. Take $V = \tfrac{1}{2}(x_1^2 + x_2^2)$, contract its
gradient with the field the way module 2 did, and the $x_1x_2$ terms cancel:

$$\dot{V} = x_1\dot{x_1} + x_2\dot{x_2} = \mu\left(1 - x_1^2\right)x_2^2$$

On a closed orbit $V$ returns to where it started, so the integral of $\dot{V}$ around
the loop is zero. For small $\mu$ the orbit is nearly the circle $x_1 = a\cos t$,
$x_2 = -a\sin t$, and averaging over a period with $\langle\sin^2\rangle = \tfrac{1}{2}$
and $\langle\cos^2\sin^2\rangle = \tfrac{1}{8}$ gives
$\mu(\tfrac{1}{2}a^2 - \tfrac{1}{8}a^4) = 0$, whose non-zero root is $a = 2$.

```python
import math


def vdp(x, mu):
    return [x[1], mu * (1.0 - x[0] ** 2) * x[1] - x[0]]


def trajectory(mu, x0, dt, steps):
    """RK4 the field and return every state, the start included."""
    x, out = list(x0), [list(x0)]
    for _ in range(steps):
        k1 = vdp(x, mu)
        k2 = vdp([x[i] + 0.5 * dt * k1[i] for i in range(2)], mu)
        k3 = vdp([x[i] + 0.5 * dt * k2[i] for i in range(2)], mu)
        k4 = vdp([x[i] + dt * k3[i] for i in range(2)], mu)
        x = [x[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
             for i in range(2)]
        out.append(x)
    return out


def period(traj, dt):
    """Mean gap between upward zero crossings of x1, over the second half."""
    tail, times = traj[len(traj) // 2:], []
    for n in range(len(tail) - 1):
        if tail[n][0] < 0.0 <= tail[n + 1][0]:
            frac = -tail[n][0] / (tail[n + 1][0] - tail[n][0])
            times.append((n + frac) * dt)
    return sum(b - a for a, b in zip(times, times[1:])) / (len(times) - 1)


DT = 0.002
print(f"the small-mu prediction is amplitude 2 and period {2 * math.pi:.5f}")
for mu, steps in ((0.05, 160000), (1.0, 40000), (2.0, 40000)):
    traj = trajectory(mu, [0.1, 0.0], DT, steps)
    amp = max(abs(x[0]) for x in traj[len(traj) // 2:])
    print(f"  mu = {mu:<5} amplitude {amp:.5f}   period {period(traj, DT):.5f}")

# Where the energy comes from and where it goes, over one settled cycle.
traj = trajectory(1.0, [0.1, 0.0], DT, 40000)
cycle = traj[-int(period(traj, DT) / DT):]
pump = sum((1.0 - x[0] ** 2) * x[1] ** 2 * DT for x in cycle if abs(x[0]) < 1.0)
drain = sum((1.0 - x[0] ** 2) * x[1] ** 2 * DT for x in cycle if abs(x[0]) >= 1.0)
print(f"one cycle at mu = 1: pumped in {pump:+.4f}, dissipated {drain:+.4f}, "
      f"net {pump + drain:+.4f}")
```

```text
the small-mu prediction is amplitude 2 and period 6.28319
  mu = 0.05  amplitude 1.99997   period 6.28411
  mu = 1.0   amplitude 2.00862   period 6.66329
  mu = 2.0   amplitude 2.01989   period 7.62987
one cycle at mu = 1: pumped in +5.6625, dissipated -5.6615, net +0.0010
```

At $\mu = 0.05$ the prediction is right to five figures, in amplitude and period both. As
$\mu$ grows the amplitude drifts up a per cent and the period a fifth, because the orbit
stops being a circle and the averaging that produced $a = 2$ stops being valid. And the
last line is the mechanism, measured: 5.6625 units of energy fed in while the swing is
inside $|x_1| < 1$, 5.6615 taken back out beyond it, and a net of one part in five
thousand — which is the integration error, not a real imbalance. The orbit sits exactly
where the pumping and the damping cancel over a cycle, and that is one number rather than
a family, which is why it is isolated.

## The mistake, and why it is tempting

The mistake is treating a closed orbit as a limit cycle. It is tempting because the scope
trace looks identical — a steady sinusoid at a fixed amplitude — and because the linear
centre is the first oscillator anyone analyses, so the word *oscillator* gets attached to
the wrong picture early.

The difference is not visible in one trace. It shows in a second trace from a different
start: two runs on board B land on the same orbit, two runs on board A do not. It also
shows in what a design can promise. A limit cycle has an amplitude that is a property of
the circuit and is recovered after a disturbance; a centre has an amplitude that is a
property of the last thing that happened to it, and no amount of component tolerance
buys it back. Hewlett's audio oscillator earned its patent for putting a lamp in the
feedback path precisely to convert the second into the first.

There is a smaller version of the same error in reading $a = 2$ as the answer. It is the
$\mu \to 0$ limit and the table above shows it drifting immediately.

## Where this stops holding

Two limits, and the second is a change of subject rather than a caveat.

Bendixson gives a *negative* result — where no cycle can be — and never produces one. The
positive statement is Poincaré–Bendixson: a trajectory confined to a bounded region of the
plane containing no equilibrium must approach a closed orbit. Its proof needs a trapping
region, and constructing one is work: for van der Pol it means finding an annulus that
the flow enters from both sides, with an unstable focus excluded at the centre.

And that theorem is planar. It rests on the Jordan curve theorem — a closed curve in the
plane separates inside from outside, so a trajectory cannot get past its own earlier
path. In three dimensions there is no such obstruction, a trajectory can pass over itself,
and a bounded non-repeating trajectory becomes possible: the Lorenz and Rössler systems
are bounded, have no stable equilibrium and no periodic orbit, and never repeat. Nothing
in this module's toolkit detects that, and no amount of care with nullclines in a
projection of a three-dimensional flow will.

## What you are about to build

The lab *Find the limit cycle and prove it is isolated* asks for `rk4_step`, `integrate`
and `period` — the three routines above — and its checks are the claims made here. Forward
Euler is refused on purpose: its error accumulates in a direction that inflates or
deflates a closed orbit, so it would measure the integrator rather than the oscillator,
and the harmonic-oscillator check at $\mu = 0$ demands agreement with $(\cos t, -\sin t)$
to $10^{-8}$, which nothing of lower order reaches. Its central test starts van der Pol at
0.1 and at 3.0 and asserts the two amplitudes agree to $10^{-4}$: that agreement is what
isolation *means*, expressed as an assertion. The last test runs $\mu = 0.05$ from 1.9 over
80 s and warns that convergence takes a time of order $1/\mu$ — the reason the table above
gives the smallest $\mu$ four times the run of the others.
''',
                },
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
            "read": [
                {
                    "title": "The gust the pointing loop could not be tuned against",
                    "minutes": 15,
                    "body": r'''
A 3 m dish on an alt-azimuth mount. The elevation axis carries 40 kg·m² of inertia and is
driven directly by a torque motor. The site survey says the wind can put up to 80 N·m of
gust torque on the structure, in bursts of a few radians per second, and gives no more
detail than that — a bound, and nothing about the shape. The pointing specification is
1 mrad.

The obvious loop is a PD on the elevation error. Place both closed-loop poles at $-p$ and
sweep $p$ against the worst gust the survey allows.

```python
import math

J = 40.0        # kg m^2, the elevation axis
D_TORQUE = 80.0                 # N m, the worst gust the site survey allows
D = D_TORQUE / J                # 2.0 rad/s^2, the same bound in acceleration


def pd_run(wn, dt=0.0005, steps=12000, w_gust=3.0):
    """Both poles at -wn, released 1 rad off target into the worst gust."""
    x = [1.0, 0.0]
    late = []
    for n in range(steps):
        t = n * dt
        u = -wn * wn * x[0] - 2.0 * wn * x[1]
        d = D * math.sin(w_gust * t)
        x = [x[0] + dt * x[1], x[1] + dt * (u + d)]
        if n > steps * 4 // 5:
            late.append(abs(x[0]))
    return max(late)


print("gust of 80 N.m at 3 rad/s on a 40 kg.m^2 axis; the spec is 1 mrad")
for wn in (4.0, 12.0, 45.0):
    err = pd_run(wn)
    print(f"  PD with both poles at -{wn:<5} peak error {err * 1e3:8.3f} mrad"
          f"   predicted {D / abs(complex(wn * wn - 9.0, 2 * wn * 3.0)) * 1e3:8.3f}")
```

```text
gust of 80 N.m at 3 rad/s on a 40 kg.m^2 axis; the spec is 1 mrad
  PD with both poles at -4.0   peak error   80.058 mrad   predicted   80.000
  PD with both poles at -12.0  peak error   13.077 mrad   predicted   13.072
  PD with both poles at -45.0  peak error    0.983 mrad   predicted    0.983
```

The measurements land on the frequency-response prediction $|d|/|(j\omega)^2 + 2p(j\omega)
+ p^2|$ to three figures, which is reassuring and also the problem: the only way through
is $p = 45$ rad/s, a 7 Hz loop. The first structural mode of a dish this size is usually
somewhere between 5 and 15 Hz, so the tuning that meets the specification is the tuning
that drives the loop straight into the structure. Rebalancing $Q$ and $R$ the way CTRL520
does moves the poles around inside the same constraint; it does not change the fact that
a linear loop rejects a disturbance only in proportion to its gain there.

## Choosing the error dynamics first

Sliding mode inverts the order of the design. Rather than choosing a controller and then
measuring the error dynamics that result, write down the error dynamics wanted and make
them a constraint. Define

$$s = \dot{e} + \lambda e \qquad (\lambda > 0)$$

The set $s = 0$ is not an arbitrary line in the plane. Read it as an equation and it says
$\dot{e} = -\lambda e$: a first-order decay with time constant $1/\lambda$, chosen in
seconds before any control law exists. Take $\lambda = 4$ and the error settles with the
same 0.25 s timescale as the $p = 4$ PD above.

Two things are already true and neither has been earned yet. The plant does not appear in
$s = 0$ — the constraint describes the error and says nothing about inertia, friction or
wind. And the order has dropped: a second-order axis constrained to a line in its own
phase plane has one degree of freedom left.

The design problem is now a single question: how do you make the state get to that line,
and stay on it?

## Making the state arrive

Take $V = \tfrac{1}{2}s^2$, which is positive definite in $s$ and is the module 2
machinery applied to one variable. Ask for a decrease that does not fade:

$$\dot{V} = s\dot{s} \le -\eta|s| \qquad (\eta > 0)$$

The right-hand side is the whole of the design. Compare it with the linear alternative
$s\dot{s} \le -\eta s^2$, which is also a perfectly good Lyapunov decrease and gives
$s \to 0$ exponentially, arriving never. With $-\eta|s|$, dividing through by $|s|$ gives
$\frac{\mathrm{d}}{\mathrm{d}t}|s| \le -\eta$: $|s|$ falls at a rate bounded away from
zero however small it becomes, so it hits zero at a time

$$t_r \le \frac{|s(0)|}{\eta}$$

and stays there. Finite arrival is what the absolute value buys, and it costs a control
that is discontinuous at $s = 0$, because a continuous law cannot deliver a non-vanishing
push arbitrarily close to the surface.

For the dish, $\dot{s} = \ddot{e} + \lambda\dot{e} = u + d + \lambda\dot{e}$ with $u$ the
commanded angular acceleration. Taking $u = -\lambda\dot{e} - k\,\mathrm{sgn}(s)$ leaves
$\dot{s} = d - k\,\mathrm{sgn}(s)$, so $s\dot{s} = ds - k|s| \le (D - k)|s|$ using only
$|d| \le D$. Setting $k = D + \eta$ gives $s\dot{s} \le -\eta|s|$ exactly. The derivation
*The reaching law, the reaching time, and what the layer costs* runs the same argument one
branch at a time and reaches the same $t_r = s_0/\eta$.

The gain is set against the *bound*, not against any particular gust. Nothing here needed
to know that the wind was a sinusoid at 3 rad/s.

## Why the disturbance disappears

```python
import math

LAM, ETA, D = 4.0, 2.0, 2.0      # surface slope, margin, and the gust bound
DT, STEPS = 0.0005, 12000


def sat(v, phi):
    """Hard sign when phi is zero, otherwise a ramp of width phi, clipped."""
    if phi <= 0.0:
        return (v > 0.0) - (v < 0.0)
    return max(-1.0, min(1.0, v / phi))


def run(phi, d_amp, x0=(1.0, 0.0)):
    """Closed loop, forward Euler. Returns the states, the surface and the torque."""
    x, xs, ss, us = list(x0), [], [], []
    for n in range(STEPS):
        t = n * DT
        s = x[1] + LAM * x[0]
        u = -LAM * x[1] - (D + ETA) * sat(s, phi)
        xs.append(list(x))
        ss.append(s)
        us.append(u)
        d = d_amp * math.sin(3.0 * t)
        x = [x[0] + DT * x[1], x[1] + DT * (u + d)]
    return xs, ss, us


def first_crossing(ss):
    for n in range(len(ss) - 1):
        if ss[n] * ss[n + 1] <= 0.0:
            return n * DT
    return float("inf")


xs, ss, us = run(0.0, D)
print(f"s(0) = {ss[0]:.1f}, so the guarantee is t_r <= |s0|/eta = {abs(ss[0]) / ETA:.1f} s")
print(f"  the surface is actually reached at {first_crossing(ss):.4f} s")
for d_amp in (0.0, D, -D):
    xs, ss, us = run(0.0, d_amp)
    tail = xs[STEPS * 4 // 5:]
    print(f"  gust {d_amp:+.1f} rad/s^2: peak error over the last second "
          f"{max(abs(x[0]) for x in tail) * 1e6:7.3f} microrad")
```

```text
s(0) = 4.0, so the guarantee is t_r <= |s0|/eta = 2.0 s
  the surface is actually reached at 1.2905 s
  gust +0.0 rad/s^2: peak error over the last second 250.250 microrad
  gust +2.0 rad/s^2: peak error over the last second 209.385 microrad
  gust -2.0 rad/s^2: peak error over the last second 209.387 microrad
```

Two hundred microradians, against eighty thousand from the PD with the same 0.25 s error
timescale. And the three rows barely differ: turning the worst gust on, and then reversing
it, changes the answer by less than a fifth — and in the direction of making it slightly
*better*, which is a sign that what is left is not the wind at all.

The reason the wind vanishes is worth stating precisely. On the surface, $s$ is held at
zero, so $\dot{s} = 0$, so $u + d + \lambda\dot{e} = 0$ at every instant. The control is
switching fast enough that its average — the *equivalent control* — is whatever it has to
be to satisfy that, and that average therefore contains $-d$ exactly. The disturbance is
being cancelled by a law that was never told what it was. What made this possible is that
$d$ enters through the same channel as $u$: both are torques on the same axis, so
anything $d$ can do to $\dot{s}$, $u$ can undo. That is the meaning of *matched*.

## What it costs

```python
import math

LAM, ETA, D = 4.0, 2.0, 2.0
DT, STEPS, J = 0.0005, 12000, 40.0


def sat(v, phi):
    if phi <= 0.0:
        return (v > 0.0) - (v < 0.0)
    return max(-1.0, min(1.0, v / phi))


def run(phi, d_amp=D):
    x, xs, ss, us = [1.0, 0.0], [], [], []
    for n in range(STEPS):
        s = x[1] + LAM * x[0]
        u = -LAM * x[1] - (D + ETA) * sat(s, phi)
        xs.append(list(x))
        ss.append(s)
        us.append(u)
        d = d_amp * math.sin(3.0 * n * DT)
        x = [x[0] + DT * x[1], x[1] + DT * (u + d)]
    return xs, ss, us


print("phi     torque step   band in s   predicted   pointing error")
for phi in (0.0, 0.005, 0.05):
    xs, ss, us = run(phi)
    step = sum(abs(b - a) for a, b in zip(us, us[1:])) / (len(us) - 1)
    tail = slice(STEPS * 4 // 5, STEPS)
    band = max(abs(v) for v in ss[tail])
    err = max(abs(x[0]) for x in xs[tail])
    predicted = D * phi / (D + ETA)
    print(f"{phi:<6}  {step * J:9.4f} Nm  {band:10.6f}  {predicted:10.6f}  "
          f"{err * 1e6:9.1f} urad")
```

```text
phi     torque step   band in s   predicted   pointing error
0.0      167.8513 Nm    0.002975    0.000000      209.4 urad
0.005      0.0979 Nm    0.002500    0.002500      500.3 urad
0.05       0.0957 Nm    0.024983    0.025000     4998.5 urad
```

The first row is a motor being commanded to change its torque by 168 N·m every 0.5 ms,
for as long as the dish is pointing. That is not a control signal, it is a heater and a
gearbox-wear schedule, and the physical drive would not follow it in any case.

Replacing $\mathrm{sgn}(s)$ with $s/\phi$ inside a band of width $\phi$ makes the law
continuous there. The dynamics inside become $\dot{s} = d - ks/\phi$, which settles where
the two balance: $|s| \to D\phi/k$, and the middle two columns confirm it to four decimal
places. The pointing error follows at roughly $|s|/\lambda$.

That is a complete design. With $\phi = 0.005$ the torque activity drops by a factor of
1700 and the pointing error is 0.5 mrad, inside the 1 mrad specification. With
$\phi = 0.05$ it is 5 mrad and the dish misses. $\phi$ is the dial between an actuator
that survives and an error budget that closes, and the sandbox *Reaching, sliding, and the
price of not chattering* is that dial: lift $\phi$ off zero and the trajectories stop
crossing the surface and settle into the band between the faint lines.

## The mistake, and why it is tempting

The mistake is sizing the switching gain against the disturbance you expect rather than
the bound you were given. It is tempting because every other loop in the building is
tuned that way — you run the machine, you look at the error, you raise the gain until it
is small enough — and because a gain of $D + \eta$ looks wastefully large on a calm day.

It fails in a way that does not announce itself. With $k < D$ there is a region where
$d$ overcomes the switching term, $s\dot{s}$ goes positive, and the state never reaches
the surface at all. Nothing oscillates, nothing saturates, no alarm trips: the loop looks
like a slightly sluggish PD, because that is what it has become. And it works perfectly
for months, until the gust that the survey was written for arrives. The lab's reaching
test names this failure directly — the message on a missed reaching time reads *the usual
cause is a switching gain of eta instead of dbound + eta*.

The related error is raising $\eta$ to fix a steady error inside a boundary layer. From
$|s| \to D\phi/k$, raising $\eta$ raises $k$ and does shrink the band — but $\phi$ divides
it directly and $k$ only through a sum that already contains $D$. Going from $\eta = 2$ to
$\eta = 20$ buys a factor of 5.5; going from $\phi = 0.05$ to $\phi = 0.005$ buys a factor
of 10 and costs nothing but switching activity.

## Where this stops holding

Three limits, in the order they arrive on real hardware.

*Ideal sliding needs infinite switching frequency, and no implementation has one.* Even
with $\phi = 0$ the first row above shows a band of 0.0030 in $s$ — because between
samples nothing switches, and $s$ drifts by about $k\,\Delta t = 4 \times 0.0005$. Halving
the sample interval halves it, exactly. A digital sliding-mode controller therefore always
has a boundary layer; the choice is whether you set its width or the sample clock does.

*Unmatched uncertainty is not rejected at all.* The whole argument turned on $d$ entering
alongside $u$. A flexible mode between the motor and the dish surface does not: the torque
reaches the reflector through the structure, and no gain on $u$ can cancel a disturbance
the input cannot reach. Worse, a hard-switching law excites exactly such modes, which is
one of the reasons chatter is a structural problem and not only a thermal one.

*The surface must have relative degree one with respect to the input.* $s = \dot{e} +
\lambda e$ works because $u$ appears in $\dot{s}$. Put an actuator lag between the command
and the torque and it does not; the switching then acts through a first-order filter, the
sign arrives late, and the ideal sliding motion is replaced by a limit cycle around the
surface — module 3's subject, arriving uninvited.

## What you are about to build

The lab *Sliding-mode control of a disturbed double integrator* is this reading with the
inertia normalised away: `sat`, `surface`, `control` and `run`, on
$\dot{x_1} = x_2$, $\dot{x_2} = u + d(t)$ with $|d| \le D$ and the amplitude withheld from
you. Its numbers are the ones above — $\lambda = 4$, $\eta = 2$, $D = 2$, $s(0) = 4$, a
guarantee of 2 s and an actual reaching time near 1.29 s. One test runs the loop at
$d = 0$, $+2$ and $-2$ and asserts the peak excursion stays under $10^{-3}$ in all three,
which is invariance stated as an assertion; another asserts the chatter ratio between
$\phi = 0$ and $\phi = 0.05$ exceeds 100; and the last checks that the steady band is
$D\phi/(D + \eta) = 0.025$ rather than merely small, because a band that happens to be
small is not evidence that you understand what set it. The fill-in *The surface, the
reaching law, and the price of chattering* walks the four decisions in order, and the
sandbox draws all of it moving.
''',
                },
            ],
            "quiz": {
                "title": "Switching hard enough, and paying for it",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why is the reaching condition $s\\dot{s} \\le -\\eta|s|$ rather than $s\\dot{s} \\le -\\eta s^2$?",
                        "opts": [
                            "The $s^2$ form is not sign-definite, so it constrains only $s > 0$",
                            "A push that does not fade as $s$ shrinks brings arrival in finite time",
                            "Only the modulus form makes $V = \\tfrac{1}{2}s^2$ decrease along the motion",
                            "The modulus keeps the control continuous as the state crosses $s = 0$",
                        ],
                        "a": 1,
                        "whys": [
                            r"$s^2$ is positive for either sign of $s$, so $-\eta s^2$ is a perfectly good decrease on both branches. It is not defective — it is merely slower in the one way that matters.",
                            r"Divide by $|s|$ and the condition reads $\mathrm{d}|s|/\mathrm{d}t \le -\eta$: a rate bounded away from zero no matter how close the state gets, so $|s|$ runs out at $t_r \le |s(0)|/\eta$.",
                            r"Both forms make $V$ decrease. The difference is the *shape* of the decrease near zero, which decides whether the state arrives or merely approaches.",
                            r"The opposite is true and it is the price of the method. A non-vanishing push arbitrarily close to the surface cannot come from a continuous law, which is why the control has to switch.",
                        ],
                        "why": r"""
$s\dot{s} \le -\eta s^2$ gives $\dot{V} \le -2\eta V$ and therefore exponential decay:
$s$ shrinks forever and reaches zero never. Dividing $s\dot{s} \le -\eta|s|$ by $|s|$
instead gives $\mathrm{d}|s|/\mathrm{d}t \le -\eta$, a rate that does not soften as the
surface approaches, so $|s|$ is exhausted at $t_r \le |s(0)|/\eta$ — two seconds for the
dish, reached in 1.29. Everything the method claims rests on arriving rather than
approaching, because only on the surface is the disturbance annihilated exactly.
""",
                    },
                    {
                        "q": "The gust bound is $D = 2$ and you set the switching gain to $\\eta = 2$, omitting $D$. What is the symptom?",
                        "opts": [
                            "Chattering doubles in amplitude while the surface is still reached",
                            "The surface is still reached, but after $|s_0|/\\eta$ rather than sooner",
                            "The loop behaves like a sluggish PD and the surface is never reached",
                            "Sliding is unaffected, since the equivalent control absorbs the gust",
                        ],
                        "a": 2,
                        "whys": [
                            r"Chatter amplitude is set by the switching gain, and a smaller gain gives a smaller one. The failure is not noisy, which is exactly what makes it easy to miss.",
                            r"$|s_0|/\eta$ is the guarantee that has been lost, not a slower version of it. The bound was derived from $s\dot{s} \le -\eta|s|$, and that inequality no longer holds anywhere the gust opposes the switching.",
                            r"With $k = 2$ and $|d| \le 2$ there are instants where $\dot{s}$ has the wrong sign, so $s$ stalls short of zero and the state never gets the invariance property.",
                            r"The equivalent control only exists once the state is *on* the surface, which is the thing that has stopped happening. It is a consequence of sliding, not a mechanism that produces it.",
                        ],
                        "why": r"""
The reaching argument needs $s\dot{s} = ds - k|s| \le (D - k)|s|$ to be negative, which
requires $k > D$. At $k = D$ the gust can cancel the switching term exactly, $s$ stops
falling short of zero, and the state settles somewhere off the surface, where the
disturbance is not rejected at all. Nothing rings and nothing saturates — the closed loop
degrades quietly into an ordinary proportional loop on the error rate, which is why the
lab's reaching test spells out that the usual cause of a missed reaching time is a gain
of `eta` instead of `dbound + eta`.
""",
                    },
                    {
                        "q": "While sliding, the error obeys $\\dot{e} = -\\lambda e$ whatever the plant is. What makes that so?",
                        "opts": [
                            "The equivalent control inverts an identified model of the plant",
                            "Holding $s$ at zero *is* that equation, since $s = \\dot{e} + \\lambda e$",
                            "The closed-loop poles have been placed at $-\\lambda$ by the switching gain",
                            "The switching term cancels the plant dynamics term by term",
                        ],
                        "a": 1,
                        "whys": [
                            r"No model is inverted and none is available — the dish's gust torque is known only by a bound. What the equivalent control does is take whatever value $\dot{s} = 0$ requires, which needs no identification.",
                            r"The surface was written down as the differential equation wanted, rearranged into an algebraic constraint. Enforcing the constraint enforces the equation, and the plant never enters either one.",
                            r"Pole placement needs a model and gives a linear closed loop. Here the order has *dropped* to one, which no state feedback on a second-order plant does.",
                            r"Cancellation term by term would require knowing the terms. The switching term dominates them instead, which is a different and much weaker requirement.",
                        ],
                        "why": r"""
$s = \dot{e} + \lambda e$ and $s = 0$ are the same statement, so a controller that holds
$s$ at zero has enforced $\dot{e} = -\lambda e$ by construction. This is why the design
order is inverted relative to CTRL510 and CTRL520: the error dynamics are chosen first,
in seconds, and the control law is then whatever forces the constraint. The plant appears
only in the sizing of the switching gain, and only through a bound.
""",
                    },
                    {
                        "q": "A gust torque on the elevation axis is rejected; a flexible mode between motor and reflector is not. What separates them?",
                        "opts": [
                            "The flexible mode is faster than the switching, so it averages away",
                            "Unmatched terms are always small enough to sit below the switching gain",
                            "Only a disturbance in the input channel can be dominated by the input",
                            "A second-order surface would be needed, since the mode adds two states",
                        ],
                        "a": 2,
                        "whys": [
                            r"Averaging is what makes the *equivalent control* meaningful, and it does not remove anything the input cannot reach. A fast unmatched mode is if anything worse, because hard switching excites it.",
                            r"Size is not the criterion and this gets the logic backwards — a large matched disturbance is rejected completely while an arbitrarily small unmatched one is not rejected at all.",
                            r"$\dot{s} = u + d + \lambda\dot{e}$: because $u$ and $d$ enter the same sum, whatever $d$ does to $\dot{s}$ the gain on $u$ can undo. A term that reaches the output another way is untouched.",
                            r"Adding states to the surface is a real technique and it does not repair this. The mode remains outside the input channel however the surface is written.",
                        ],
                        "why": r"""
The reaching argument is one line: $\dot{s} = u + d + \lambda\dot{e}$, and $u$ can
dominate $d$ because they are added together. That is the whole of what *matched* means,
and it is a structural property rather than a question of magnitude. A flexible mode
carries torque to the reflector through the structure, so it changes the pointing without
appearing in that sum, and no switching gain touches it. It is also the reason chatter is
a structural problem: a discontinuous command has energy at every frequency, including
the mode's.
""",
                    },
                    {
                        "q": "Inside a boundary layer of width $\\phi$ the switching term becomes $ks/\\phi$. What sets the steady $|s|$?",
                        "opts": [
                            "The width $\\phi$ itself, since $s$ may wander anywhere inside the band",
                            "Zero, because the layer changes the control shape and not the dynamics",
                            "The reaching margin $\\eta$, which is what the layer is trading away here",
                            "The value at which $ks/\\phi$ balances the disturbance, namely $D\\phi/k$",
                        ],
                        "a": 3,
                        "whys": [
                            r"$\phi$ is the ceiling rather than the answer, and the gap matters: with the dish's numbers the band is $D\phi/k = \phi/2$, so half of the layer is never used.",
                            r"The dynamics change completely. Outside, $s$ falls at a fixed rate and arrives; inside, $\dot{s} = d - ks/\phi$ is a first-order lag driven by the disturbance, and a driven lag has a non-zero steady value.",
                            r"$\eta$ enters only through $k = D + \eta$, so raising it from 2 to 20 shrinks the band by 5.5 while $\phi$ divides it directly. The trade the layer makes is chatter against error, not margin against error.",
                            r"$\dot{s} = 0$ requires $ks/\phi = d$, and with $|d| \le D$ that is $|s| \le D\phi/k$ — 0.0025 for the dish, which is what the run measures to four decimals.",
                        ],
                        "why": r"""
Inside the layer the law is linear: $\dot{s} = d - ks/\phi$. Setting $\dot{s} = 0$ gives
$s = d\phi/k$, so the surface variable settles wherever the ramped control balances the
present disturbance, bounded by $D\phi/k$. For the dish that is
$2 \times 0.005/4 = 0.0025$, measured as 0.002500, and the pointing error follows at
roughly $|s|/\lambda$. The exact rejection is gone because the control is no longer free
to take any value the constraint demands — inside the band it is pinned to $ks/\phi$, and
$s$ has to move away from zero to generate the torque the gust requires.
""",
                    },
                    {
                        "q": "With $\\phi = 0$ on a 2 kHz digital controller the pointing error is 209 µrad, and it halves when the sample interval halves. What is that residual?",
                        "opts": [
                            "Gust leaking through the surface, since rejection is never perfect",
                            "An unavoidable layer, as wide as $s$ drifts between two samples",
                            "Euler error in the plant simulation rather than in the loop",
                            "The tail of the reaching transient, still decaying at the end of the run",
                        ],
                        "a": 1,
                        "whys": [
                            r"The run with the gust switched off has the *larger* error of the three, so what is left cannot be the gust. Reversing the gust changes the figure by under a fifth, in both directions.",
                            r"Nothing switches between samples, so $s$ runs on at up to $k$ for a full interval before the sign is re-evaluated: a band of about $k\,\Delta t$, and halving $\Delta t$ halves it.",
                            r"The plant's own discretisation error is second order in $\Delta t$ near a smooth trajectory, and it would not scale linearly. It is also common to the PD run, which shows no such floor.",
                            r"The surface is reached at 1.29 s and the figure is taken over the last second of a 6 s run, four seconds later. A decaying transient would also shrink as the run lengthened, and it does not.",
                        ],
                        "why": r"""
Ideal sliding needs the control to switch the instant $s$ changes sign, which a sampled
implementation cannot do: between ticks the sign is frozen, $s$ carries on at up to
$k = 4$, and it overshoots by about $k\,\Delta t = 0.002$ before being turned around. That
is a boundary layer nobody asked for, and the linear scaling with $\Delta t$ is its
signature — 411, 209, 104 and 49 µrad at 1, 0.5, 0.25 and 0.125 ms. The design lesson is
that $\phi = 0$ is unavailable in practice, so the choice is whether the width is set
deliberately or inherited from the sample clock.
""",
                    },
                ],
            },
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
