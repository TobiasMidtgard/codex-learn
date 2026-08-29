"""EE111 — Mathematics for Electrical Engineering.

A first-year course. It assumes school mathematics and nothing else: no prior
circuits, no prior programming beyond arithmetic. Every term is defined where it
first appears.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed; scipy is not
  * every expected number here was produced by running the code or the solver
"""

COURSE = {
    "id": "EE111",
    "title": "Mathematics for Electrical Engineering",
    "band": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python", "SymPy"],
    "credits": 10,
    "hours": 120,
    "icon": "◈",
    "summary": (
        "Electrical engineering is written in five pieces of mathematics: complex "
        "numbers, the exponential function, differentiation, integration, and "
        "simultaneous equations. This course teaches those five from the beginning "
        "and shows, in a working circuit simulator, what each one is for. Nothing is "
        "assumed beyond school algebra and trigonometry."
    ),
    "outcomes": [
        "Add, multiply, conjugate and divide complex numbers, and place them on the Argand plane.",
        "State Euler's identity and use a phasor to add sinusoids of the same frequency.",
        "Differentiate and integrate the exponentials and sinusoids that circuits produce, and apply i = C dv/dt.",
        "Solve a first-order differential equation, and recognise the time constant in a measured response.",
        "Write a set of simultaneous equations as a matrix and solve it.",
    ],
    "assessment": (
        "Four quizzes, three circuits drawn and measured in the schematic editor, four "
        "small Python labs, and a capstone that computes an RC network four different ways."
    ),
    "reading": [
        "*Engineering Mathematics*, Stroud — parts 1 and 2, for the algebra at exactly this level.",
        "*Mathematical Methods for Physics and Engineering*, Riley, Hobson & Bence — chapter 3 for complex numbers.",
        "*The Art of Electronics*, Horowitz & Hill — chapter 1, where complex impedance is put to work, once module 2 is done.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Complex numbers and the Argand plane",
            "summary": "A number with two parts, drawn as a point on a plane. Multiplying by j turns that point a quarter of the way round.",
            "concepts": [
                "The symbol $j$ is defined by one rule and one rule only: $j^2 = -1$. Engineers write $j$ rather than $i$ because $i$ is already the current.",
                "A complex number is $a + jb$: $a$ is the **real part**, $b$ is the **imaginary part**. Both are ordinary real numbers.",
                "The **Argand plane** draws $a + jb$ as the point $(a, b)$ — real part across, imaginary part up. Addition is then exactly vector addition.",
                "The **modulus** $|a + jb| = \\sqrt{a^2 + b^2}$ is the distance from the origin; the **argument** is the angle from the positive real axis, found with $\\arctan$ of $b/a$ in the right quadrant.",
                "The **conjugate** of $a + jb$ is $a - jb$: the same point reflected in the real axis. Multiplying a number by its own conjugate gives $a^2 + b^2$, a real number — which is how division is done.",
                "Multiplying by $j$ rotates a point a quarter turn anticlockwise and changes nothing else. That single fact is why complex numbers describe alternating current.",
            ],
            "sandbox": {
                "title": "Multiplying by j, drawn as motion",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": 0, "a12": -1, "a21": 1, "a22": 0},
                "brief": r'''
Take the horizontal axis to be the real part of a complex number and the vertical
axis to be the imaginary part. That is the Argand plane.

The four sliders set a matrix that turns a point into a velocity. The short strokes
point along that velocity — they are all drawn the same length, so they show the
direction and not the speed — and the coloured curves are the paths that follow it
from eight starting points around a circle.

The matrix it opens with is $\begin{bmatrix} 0 & -1 \\ 1 & 0\end{bmatrix}$, which
sends the point $(a, b)$ to $(-b, a)$ — and $(-b, a)$ is exactly $j$ times $a + jb$.
So the picture on screen is what "multiply by $j$" does, applied over and over.
''',
                "notice": [
                    "The eight curves are circles about the origin. Multiplying by $j$ never changes the modulus, only the angle — so a point can only ever go round. (The drawing steps forward in small jumps, so the circles creep outwards by about a tenth of their radius over the run; that is the drawing's arithmetic, not the mathematics.)",
                    "Set $a_{11}$ and $a_{22}$ both to $-0.3$ and leave the other two alone. The circles become inward spirals, and the readout under the plot changes to *stable spiral*. Rotation plus shrinking is what a decaying oscillation looks like — hold on to this picture, it returns in module 2.",
                    "Now set $a_{11}$ and $a_{22}$ both to $+0.3$. The spirals run outwards instead, past the edge of the plot and off the panel, where the drawing gives up on each curve in turn. Same rotation, opposite growth.",
                    "Set $a_{12}$ to $+1$ so both off-diagonal entries are $+1$. The readout says *saddle*: the paths no longer go round at all. Rotation needed that minus sign — one entry, and the whole character of the picture changes.",
                ],
            },
            "quiz": {
                "title": "Does the definition hold up",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is $j^2$?",
                        "opts": ["$1$", "$j$", "$-1$", "$0$"],
                        "a": 2,
                        "why": (
                            "This is the definition, not a result: $j$ is *introduced* as a thing whose square is $-1$, "
                            "because no real number has that property. Everything else about complex numbers follows "
                            "from ordinary algebra plus this one substitution. A common slip is $j^2 = j$, which would "
                            "make $j$ equal to 0 or 1 and leave nothing new."
                        ),
                    },
                    {
                        "q": "What is $(3 + 4j) + (1 - 2j)$?",
                        "opts": ["$4 + 6j$", "$4 + 2j$", "$4 - 8j$", "$3 - 8j$"],
                        "a": 1,
                        "why": (
                            "Add the real parts and add the imaginary parts, separately: $3 + 1 = 4$ and $4 + (-2) = 2$. "
                            "Nothing multiplies, so $j^2$ never appears. On the Argand plane this is the parallelogram "
                            "rule — the same addition you would do with two arrows."
                        ),
                    },
                    {
                        "q": "What is $|3 + 4j|$, the modulus?",
                        "opts": ["$7$", "$25$", "$12$", "$5$"],
                        "a": 3,
                        "why": (
                            "The modulus is the distance from the origin to the point $(3, 4)$, so it is Pythagoras: "
                            "$\\sqrt{3^2 + 4^2} = \\sqrt{25} = 5$. Two frequent errors are adding the parts to get 7, "
                            "and stopping at $3^2 + 4^2 = 25$ without taking the square root."
                        ),
                    },
                    {
                        "q": "What is the conjugate of $2 - 5j$?",
                        "opts": ["$-2 + 5j$", "$2 + 5j$", "$-2 - 5j$", "$5 - 2j$"],
                        "a": 1,
                        "why": (
                            "Conjugating flips the sign of the imaginary part and leaves the real part alone: the point "
                            "is reflected in the horizontal axis. It does not negate the whole number, and it does not "
                            "swap the two parts over."
                        ),
                    },
                    {
                        "q": "On the Argand plane, what does multiplying a number by $j$ do to it?",
                        "opts": [
                            "Doubles its distance from the origin",
                            "Reflects it in the real axis",
                            "Turns it a quarter turn anticlockwise about the origin",
                            "Moves it one unit upwards",
                        ],
                        "a": 2,
                        "why": (
                            "Check it on a case: $j(a + jb) = ja + j^2 b = -b + ja$, so $(a, b)$ becomes $(-b, a)$. "
                            "Draw those two points and the angle between them is 90 degrees, with the distance from the "
                            "origin unchanged. Reflection in the real axis is conjugation, a different operation; and "
                            "*adding* $j$, not multiplying, is what moves a point one unit up."
                        ),
                    },
                    {
                        "q": "What is $(2 + 3j)(2 - 3j)$?",
                        "opts": ["$4 - 9j$", "$4 + 9j$", "$13j$", "$13$"],
                        "a": 3,
                        "why": (
                            "Expand: $4 - 6j + 6j - 9j^2$. The two middle terms cancel, and $-9j^2 = +9$, leaving $13$ "
                            "with no imaginary part at all. A number times its own conjugate is always real and equal "
                            "to the modulus squared — which is exactly why you multiply top and bottom by the "
                            "conjugate when dividing."
                        ),
                    },
                ],
            },
            "lab": {
                "title": "Complex arithmetic, built from nothing",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Python has complex numbers built in. You are going to write them yourself once, so
that nothing about them is magic afterwards.

A complex number here is an ordinary pair of floats: the tuple `(a, b)` means
$a + jb$. Fill in the six functions in `main.py`:

- `add(x, y)` and `mul(x, y)` — the arithmetic. For `mul`, expand the brackets and
  replace $j^2$ with $-1$.
- `conj(x)` — flip the sign of the imaginary part.
- `modulus(x)` — the distance from the origin.
- `argument(x)` — the angle from the positive real axis, in radians. Use
  `math.atan2(b, a)`, which gets the quadrant right; `math.atan(b / a)` does not.
- `divide(x, y)` — multiply top and bottom by the conjugate of the bottom, so the
  bottom becomes the real number $|y|^2$, then divide both parts by it. Raise
  `ZeroDivisionError` if the bottom is $0 + 0j$.

`main.py` prints a few results when you run it; the checks call your functions.
''',
                "files": [{"name": "main.py", "content": r'''
import math

# A complex number is the tuple (real_part, imaginary_part).
# So (3.0, 4.0) means 3 + 4j.


def add(x, y):
    """(a + jb) + (c + jd). Add the two parts separately."""
    # TODO
    return (0.0, 0.0)


def mul(x, y):
    """(a + jb)(c + jd). Expand, then replace j*j with -1."""
    # TODO
    return (0.0, 0.0)


def conj(x):
    """a + jb  ->  a - jb."""
    # TODO
    return (0.0, 0.0)


def modulus(x):
    """The distance from the origin to the point (a, b)."""
    # TODO
    return 0.0


def argument(x):
    """The angle in radians from the positive real axis. Use math.atan2."""
    # TODO
    return 0.0


def divide(x, y):
    """x / y, by multiplying top and bottom by the conjugate of y."""
    # TODO
    return (0.0, 0.0)


if __name__ == "__main__":
    print("j * j        =", mul((0.0, 1.0), (0.0, 1.0)))
    print("(3+4j) sum   =", add((3.0, 4.0), (1.0, -2.0)))
    print("|3+4j|       =", modulus((3.0, 4.0)))
    print("arg(0+2j)    =", round(argument((0.0, 2.0)), 6), "rad")
    print("1 / j        =", divide((1.0, 0.0), (0.0, 1.0)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

# A complex number is the tuple (real_part, imaginary_part).
# So (3.0, 4.0) means 3 + 4j.


def add(x, y):
    """(a + jb) + (c + jd). Add the two parts separately."""
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    """(a + jb)(c + jd). Expand, then replace j*j with -1."""
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c)


def conj(x):
    """a + jb  ->  a - jb."""
    return (x[0], -x[1])


def modulus(x):
    """The distance from the origin to the point (a, b)."""
    return math.hypot(x[0], x[1])


def argument(x):
    """The angle in radians from the positive real axis. Use math.atan2."""
    return math.atan2(x[1], x[0])


def divide(x, y):
    """x / y, by multiplying top and bottom by the conjugate of y."""
    bottom = y[0] * y[0] + y[1] * y[1]
    if bottom == 0.0:
        raise ZeroDivisionError("cannot divide by 0 + 0j")
    top = mul(x, conj(y))
    return (top[0] / bottom, top[1] / bottom)


if __name__ == "__main__":
    print("j * j        =", mul((0.0, 1.0), (0.0, 1.0)))
    print("(3+4j) sum   =", add((3.0, 4.0), (1.0, -2.0)))
    print("|3+4j|       =", modulus((3.0, 4.0)))
    print("arg(0+2j)    =", round(argument((0.0, 2.0)), 6), "rad")
    print("1 / j        =", divide((1.0, 0.0), (0.0, 1.0)))
'''}],
                "hints": [
                    "For `mul`, write the four products out on paper first: $ac + jad + jbc + j^2bd$. Only the last one changes sign.",
                    "`math.hypot(a, b)` is $\\sqrt{a^2 + b^2}$ and avoids overflow; `math.atan2(b, a)` takes the parts in that order — imaginary first.",
                    "For `divide`, you already have `mul` and `conj`. Multiply the top by `conj(y)`, work out $|y|^2$ as `y[0]**2 + y[1]**2`, and divide each part of the result by it.",
                ],
                "tests": [
                    {"name": "j squared is minus one", "code": r'''
_r = mul((0.0, 1.0), (0.0, 1.0))
assert abs(_r[0] - (-1.0)) < 1e-12 and abs(_r[1]) < 1e-12, \
    f"j*j should be (-1, 0), got {_r}"
'''},
                    {"name": "addition works part by part", "code": r'''
_r = add((3.0, 4.0), (1.0, -2.0))
assert abs(_r[0] - 4.0) < 1e-12 and abs(_r[1] - 2.0) < 1e-12, \
    f"(3+4j) + (1-2j) should be (4, 2), got {_r}"
'''},
                    {"name": "multiplication is not part by part", "code": r'''
_r = mul((3.0, 4.0), (1.0, -2.0))
assert abs(_r[0] - 11.0) < 1e-12 and abs(_r[1] - (-2.0)) < 1e-12, \
    f"(3+4j)(1-2j) should be (11, -2), got {_r} — expand all four products"
'''},
                    {"name": "modulus is Pythagoras", "code": r'''
assert abs(modulus((3.0, 4.0)) - 5.0) < 1e-12, \
    f"|3+4j| should be 5, got {modulus((3.0, 4.0))}"
assert abs(modulus((-3.0, -4.0)) - 5.0) < 1e-12, \
    "the modulus is a distance and can never be negative"
'''},
                    {"name": "argument gets the quadrant right", "code": r'''
import math
assert abs(argument((0.0, 2.0)) - math.pi / 2) < 1e-12, \
    "0 + 2j sits straight up, at pi/2"
_a = argument((-1.0, 1.0))
assert abs(_a - 3 * math.pi / 4) < 1e-12, \
    f"-1 + j is in the second quadrant, at 3pi/4, got {_a} — atan alone cannot see this"
'''},
                    {"name": "a number times its conjugate is real", "code": r'''
_r = mul((3.0, 4.0), conj((3.0, 4.0)))
assert abs(_r[1]) < 1e-12, f"the imaginary part should vanish, got {_r}"
assert abs(_r[0] - 25.0) < 1e-12, f"it should equal |3+4j|^2 = 25, got {_r[0]}"
'''},
                    {"name": "division by j turns the other way", "code": r'''
_r = divide((1.0, 0.0), (0.0, 1.0))
assert abs(_r[0]) < 1e-12 and abs(_r[1] - (-1.0)) < 1e-12, \
    f"1/j should be (0, -1), got {_r} — dividing by j is a quarter turn clockwise"
'''},
                    {"name": "dividing by zero is refused", "code": r'''
try:
    divide((1.0, 2.0), (0.0, 0.0))
except ZeroDivisionError:
    pass
else:
    raise AssertionError("dividing by 0 + 0j should raise ZeroDivisionError")
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Euler's identity and the phasor",
            "summary": "One equation ties the exponential to the sine and cosine, and turns trigonometry into arithmetic.",
            "concepts": [
                "**Euler's identity**: $e^{j\\theta} = \\cos\\theta + j\\sin\\theta$. Read it as a point on the unit circle at angle $\\theta$.",
                "It follows that $|e^{j\\theta}| = 1$ for every real $\\theta$: a pure imaginary exponent rotates and never stretches.",
                "Running it backwards gives $\\cos\\theta = \\frac{e^{j\\theta} + e^{-j\\theta}}{2}$ and $\\sin\\theta = \\frac{e^{j\\theta} - e^{-j\\theta}}{2j}$.",
                "A **phasor** is a complex number carrying the amplitude and the phase of a sinusoid: $A\\cos(\\omega t + \\phi)$ is written $A e^{j\\phi}$, and the $\\omega t$ is left implied because every signal in the circuit shares it.",
                "Two sinusoids of the *same frequency* add by adding their phasors — ordinary complex addition, no trigonometric identities.",
                "A general exponent $\\sigma + j\\omega$ gives $e^{\\sigma t}e^{j\\omega t}$: a rotation at rate $\\omega$ scaled by a growth or decay $e^{\\sigma t}$. Negative $\\sigma$ means the oscillation dies away.",
            ],
            "sandbox": {
                "title": "A complex exponent, seen as a response",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 0.2, "wn": 4},
                "brief": r'''
The left panel is the complex plane again, and the two dots are the exponents that
this system's response is built from. The right panel is that response: what the
output does after the input is switched on at time zero, with the dashed line
marking where it eventually settles.

The two sliders move the dots. $\zeta$ (zeta) controls how far to the left they sit
— that is the real part $\sigma$, the decay. $\omega_n$ controls how far they are
from the origin overall.
''',
                "notice": [
                    "Drag $\\zeta$ down to 0. The dots land exactly on the vertical axis, so the exponent is purely imaginary, and the response oscillates between 0 and 2 forever without ever settling. A purely imaginary exponent rotates and never decays — that is $|e^{j\\theta}| = 1$, drawn.",
                    "Put $\\zeta$ back to about 0.2 and watch the response wobble in and stop. The dots are now at $\\sigma \\approx -0.8$ with an imaginary part near $\\pm 3.9$: the rotation is still there, but it is multiplied by a shrinking $e^{\\sigma t}$.",
                    "Push $\\zeta$ up to 1. The caption under the left panel changes from $\\omega_d$ to *both poles real*, the two dots meet on the horizontal axis, and the response climbs to the dashed line without crossing it. No imaginary part means no rotation, so nothing can overshoot.",
                    "Hold $\\zeta$ and double $\\omega_n$ from 4 to 8. The shape of the response is identical; only the numbers on the time axis halve. The angle of the dots, not their distance, sets the character.",
                ],
            },
            "quiz": {
                "title": "Euler, phase and amplitude",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is $e^{j\\pi}$?",
                        "opts": ["$1$", "$-1$", "$j$", "$\\pi$"],
                        "a": 1,
                        "why": (
                            "Put $\\theta = \\pi$ into $e^{j\\theta} = \\cos\\theta + j\\sin\\theta$: "
                            "$\\cos\\pi = -1$ and $\\sin\\pi = 0$, so the answer is $-1 + 0j$. Geometrically you have "
                            "gone half way round the unit circle from $+1$, which lands you on $-1$."
                        ),
                    },
                    {
                        "q": "For a real angle $\\theta$, what is $|e^{j\\theta}|$?",
                        "opts": ["$e^{\\theta}$", "$\\theta$", "$1$, always", "It depends on $\\theta$ in a complicated way"],
                        "a": 2,
                        "why": (
                            "$|e^{j\\theta}|^2 = \\cos^2\\theta + \\sin^2\\theta = 1$, for every $\\theta$. The "
                            "tempting wrong answer is $e^{\\theta}$ — that is the size of $e^{\\theta}$ with a *real* "
                            "exponent. A real exponent stretches; an imaginary one rotates. Keeping those two apart is "
                            "most of what this module is for."
                        ),
                    },
                    {
                        "q": "Which expression equals $\\cos\\theta$?",
                        "opts": [
                            "$\\frac{e^{j\\theta} - e^{-j\\theta}}{2}$",
                            "$\\frac{e^{j\\theta} + e^{-j\\theta}}{2}$",
                            "$\\frac{e^{j\\theta} + e^{-j\\theta}}{2j}$",
                            "$\\frac{e^{j\\theta}}{2}$",
                        ],
                        "a": 1,
                        "why": (
                            "Write $e^{j\\theta} = \\cos\\theta + j\\sin\\theta$ and $e^{-j\\theta} = \\cos\\theta - j\\sin\\theta$, "
                            "then add them: the sines cancel and you get $2\\cos\\theta$. Subtracting instead leaves "
                            "$2j\\sin\\theta$, which is why the *sine* formula is the one carrying the $2j$ on the bottom."
                        ),
                    },
                    {
                        "q": "The signal $5\\cos(\\omega t + 30^\\circ)$ is written as a phasor. What is it?",
                        "opts": [
                            "Amplitude 30, angle $5^\\circ$",
                            "Amplitude 5, angle $-30^\\circ$",
                            "Amplitude 5, angle $30^\\circ$",
                            "Amplitude $5\\omega$, angle $30^\\circ$",
                        ],
                        "a": 2,
                        "why": (
                            "A phasor keeps the two things that vary from signal to signal — the amplitude and the "
                            "phase — and drops the $\\omega t$, because every signal in a circuit driven at one "
                            "frequency shares it. So $5\\cos(\\omega t + 30^\\circ)$ becomes $5e^{j30^\\circ}$. The "
                            "sign is kept as written: a *positive* angle inside the cosine means the signal leads."
                        ),
                    },
                    {
                        "q": "A quantity behaves as $e^{(-2 + 10j)t}$. What does it do as $t$ increases?",
                        "opts": [
                            "Oscillates while growing without limit",
                            "Oscillates forever at constant amplitude",
                            "Falls straight to zero without oscillating",
                            "Oscillates while shrinking towards zero",
                        ],
                        "a": 3,
                        "why": (
                            "Split it: $e^{-2t} \\cdot e^{j10t}$. The second factor has modulus 1 and only rotates, "
                            "at 10 radians per second. The first is a real decaying exponential, and it is the whole "
                            "of the shrinking. Sign of the real part decides shrink or grow; the imaginary part "
                            "decides only how fast it goes round."
                        ),
                    },
                    {
                        "q": "Two sinusoids of the same frequency, amplitudes 3 and 4, with the second lagging the first by exactly $90^\\circ$. What is the amplitude of their sum?",
                        "opts": ["7", "5", "1", "12"],
                        "a": 1,
                        "why": (
                            "As phasors they are $3$ and $-4j$, which are at right angles on the Argand plane, so the "
                            "sum has modulus $\\sqrt{3^2 + 4^2} = 5$. Amplitudes only add to 7 when the two signals are "
                            "exactly in phase, and only subtract to 1 when they are exactly opposed. This is the whole "
                            "reason for phasors: the geometry does the trigonometry for you."
                        ),
                    },
                ],
            },
            "build": {
                "title": "A filter that lags by 45 degrees",
                "minutes": 22,
                "brief": r'''
Time to draw a circuit.

A **resistor** (R) resists current: the current through it is the voltage across it
divided by its resistance, at every instant. A **capacitor** (C) does not pass a
steady current at all, but it does pass a changing one, and the faster the change
the more easily it passes. That difference is enough to make a *filter*: something
that lets slow signals through and holds fast ones back.

Build a circuit with these properties, driven by the voltage source that is already
on the canvas, and put the probe on the output:

1. It passes low frequencies and blocks high ones.
2. Its **corner frequency** — the frequency at which the output has fallen to
   $1/\sqrt{2}$ of its low-frequency size — is **1 kHz**.
3. At that corner frequency the output **lags the input by 45 degrees**.

The third property is the one that needs module 2. The output is the input
multiplied by a complex number, and at the corner that complex number has an angle
of $-45^\circ$. You are drawing Euler's identity.

Any pair of values with the right product will pass: the checks measure the circuit,
they do not compare it with a drawing.

**How to use the editor.** Pick a part from the toolbar and click the grid to place
it; pick *Wire* and click twice to run a wire; pick *Probe* and click the node you
are calling the output. *Select* a part to change its value. The corner frequency
of a resistor and a capacitor together is $f_c = \dfrac{1}{2\pi RC}$.
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
                        {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1592},
                        {"id": "p2", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 9, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "low frequencies get through and high ones do not", "code": r'''
const low = c.gain(10);
const high = c.gain(100000);
c.assert(low > 1e-6, "nothing at all reaches the probe at 10 Hz — check the wiring and where the probe sits");
c.assert(high < low / 10, "at 100 kHz the output is " + c.fmt(high, "V") + " against " +
  c.fmt(low, "V") + " at 10 Hz; a low-pass filter should have cut it by far more than that");
'''},
                    {"name": "the corner frequency is 1 kHz", "code": r'''
c.close(c.corner(10, 1e6), 1000, 0.05, "the frequency where the output is 1/sqrt(2) of its low-frequency value");
'''},
                    {"name": "the output lags the input by 45 degrees at the corner", "code": r'''
c.close(c.phase(1000), -45, 0.15, "the phase of the output at 1 kHz");
'''},
                    {"name": "ten times past the corner it is ten times smaller", "code": r'''
const ratio = c.gain(10000) / c.gain(10);
c.close(ratio, 0.0995, 0.2, "the size at 10 kHz relative to the flat region");
'''},
                ],
                "hints": [
                    "Two parts are enough. The source drives the first one, the two of them meet at a node, and the second goes on down to ground. The probe belongs on the node between them.",
                    "Rearrange $f_c = 1/(2\\pi RC)$ to get the product you need: $RC = 1/(2\\pi \\times 1000) \\approx 1.59\\times10^{-4}$. Pick a round capacitor value first — 100 nF, say — and let the resistor take whatever value that forces.",
                    "You can type values as `100n`, `1.6k` or `1e-7`; the editor understands all three.",
                    "Nothing is measurable until there is a ground and a probe. Ground is what all the voltages are measured against, and the probe says which node the checks should look at.",
                ],
            },
            "lab": {
                "title": "Adding sinusoids without trigonometry",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
The circuit you just drew multiplies its input by a complex number. This lab
computes that number, and uses phasors to add sinusoids.

Python writes the imaginary unit as `j` attached to a number: `3+4j` is a complex
number, `abs(z)` is its modulus, and `cmath.phase(z)` is its argument in radians.

Fill in four functions:

- `phasor(amp, phase_deg)` — return the complex number of amplitude `amp` at angle
  `phase_deg` degrees.
- `to_polar(z)` — return the pair `(amplitude, phase_in_degrees)`.
- `add_sinusoids(a1, p1, a2, p2)` — add two sinusoids *of the same frequency* given
  as amplitude and phase in degrees, and return the sum in the same form.
- `rc_gain(R, C, f)` — return the complex number the resistor–capacitor filter
  multiplies its input by at frequency `f` hertz:

$$G = \frac{1}{1 + j\,2\pi f R C}$$

At the corner frequency $f_c = 1/(2\pi RC)$ the bottom becomes $1 + j$, and you
should find that `abs(rc_gain(...))` is $1/\sqrt{2}$ and the phase is exactly
$-45^\circ$ — the two numbers your circuit was measured against.
''',
                "files": [{"name": "main.py", "content": r'''
import cmath
import math


def phasor(amp, phase_deg):
    """The complex number with this amplitude and this phase (in degrees)."""
    # TODO: amp * e^(j * angle in radians)
    return 0j


def to_polar(z):
    """Return (amplitude, phase in degrees) for the complex number z."""
    # TODO: abs(z) and cmath.phase(z), converted to degrees
    return (0.0, 0.0)


def add_sinusoids(a1, p1, a2, p2):
    """Add two same-frequency sinusoids given as amplitude and phase in degrees."""
    # TODO: turn both into phasors, add, convert back
    return (0.0, 0.0)


def rc_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C) of a resistor-capacitor filter."""
    # TODO
    return 0j


if __name__ == "__main__":
    print("3 at 0 deg plus 4 at 90 deg ->", add_sinusoids(3.0, 0.0, 4.0, 90.0))
    R, C = 1592.0, 1e-7
    fc = 1.0 / (2.0 * math.pi * R * C)
    print("corner frequency:", round(fc, 2), "Hz")
    print("gain at the corner:", to_polar(rc_gain(R, C, fc)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import cmath
import math


def phasor(amp, phase_deg):
    """The complex number with this amplitude and this phase (in degrees)."""
    return amp * cmath.exp(1j * math.radians(phase_deg))


def to_polar(z):
    """Return (amplitude, phase in degrees) for the complex number z."""
    return (abs(z), math.degrees(cmath.phase(z)))


def add_sinusoids(a1, p1, a2, p2):
    """Add two same-frequency sinusoids given as amplitude and phase in degrees."""
    return to_polar(phasor(a1, p1) + phasor(a2, p2))


def rc_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C) of a resistor-capacitor filter."""
    return 1.0 / (1.0 + 1j * 2.0 * math.pi * f * R * C)


if __name__ == "__main__":
    print("3 at 0 deg plus 4 at 90 deg ->", add_sinusoids(3.0, 0.0, 4.0, 90.0))
    R, C = 1592.0, 1e-7
    fc = 1.0 / (2.0 * math.pi * R * C)
    print("corner frequency:", round(fc, 2), "Hz")
    print("gain at the corner:", to_polar(rc_gain(R, C, fc)))
'''}],
                "hints": [
                    "`cmath.exp(1j * x)` is $e^{jx}$ with `x` in radians, and `math.radians` converts degrees for you.",
                    "`to_polar` and `phasor` are inverses of each other. Write them first and check that `to_polar(phasor(2, 30))` gives back `(2, 30)`.",
                    "In `rc_gain` the whole of $2\\pi f R C$ multiplies `1j`, so the bottom is `1 + 1j * 2 * math.pi * f * R * C`. Bracket the whole of that before dividing: `1 / (1 + ...)`. Writing `1 / 1 + 1j * ...` divides by the 1 alone and leaves the rest untouched.",
                ],
                "tests": [
                    {"name": "a phasor at 90 degrees is j", "code": r'''
_z = phasor(1.0, 90.0)
assert abs(_z - 1j) < 1e-12, f"1 at 90 degrees should be j, got {_z}"
_z2 = phasor(2.0, 0.0)
assert abs(_z2 - 2.0) < 1e-12, f"2 at 0 degrees should be 2, got {_z2}"
'''},
                    {"name": "polar and back is the identity", "code": r'''
_a, _p = to_polar(phasor(3.0, -37.0))
assert abs(_a - 3.0) < 1e-9, f"amplitude should come back as 3, got {_a}"
assert abs(_p - (-37.0)) < 1e-9, f"phase should come back as -37 degrees, got {_p}"
'''},
                    {"name": "3 and 4 at right angles make 5", "code": r'''
_a, _p = add_sinusoids(3.0, 0.0, 4.0, 90.0)
assert abs(_a - 5.0) < 1e-9, f"the amplitude should be 5, not 7, got {_a}"
assert abs(_p - 53.13010235415598) < 1e-6, f"the phase should be 53.13 degrees, got {_p}"
'''},
                    {"name": "in phase they add, opposed they cancel", "code": r'''
_a, _p = add_sinusoids(1.0, 0.0, 1.0, 0.0)
assert abs(_a - 2.0) < 1e-9, f"two equal signals in phase add to amplitude 2, got {_a}"
_a, _p = add_sinusoids(1.0, 0.0, 1.0, 180.0)
assert _a < 1e-9, f"two equal signals half a cycle apart cancel exactly, got amplitude {_a}"
'''},
                    {"name": "the gain is 1 at zero frequency", "code": r'''
_g = rc_gain(1000.0, 1e-6, 0.0)
assert abs(_g - 1.0) < 1e-12, f"with nothing changing the filter passes everything, got {_g}"
'''},
                    {"name": "at the corner the gain is 1/sqrt(2) at -45 degrees", "code": r'''
import math
_R, _C = 1592.0, 1e-7
_fc = 1.0 / (2.0 * math.pi * _R * _C)
_amp, _ph = to_polar(rc_gain(_R, _C, _fc))
assert abs(_amp - 0.7071067811865475) < 1e-9, f"the amplitude should be 1/sqrt(2), got {_amp}"
assert abs(_ph - (-45.0)) < 1e-9, f"the phase should be exactly -45 degrees, got {_ph}"
'''},
                    {"name": "ten times past the corner the gain is a tenth", "code": r'''
import math
_R, _C = 1592.0, 1e-7
_fc = 1.0 / (2.0 * math.pi * _R * _C)
_amp, _ph = to_polar(rc_gain(_R, _C, 10.0 * _fc))
assert abs(_amp - 0.09950371902099893) < 1e-9, f"expected about 0.0995, got {_amp}"
assert _ph < -80.0, f"the phase should be heading for -90 degrees, got {_ph}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Differentiating and integrating what circuits produce",
            "summary": "Two operations, and only a handful of functions to apply them to — because circuits only make exponentials and sinusoids.",
            "concepts": [
                "A **derivative** $\\frac{dv}{dt}$ is the slope of a graph of $v$ against $t$: how fast the quantity is changing right now, in volts per second.",
                "An **integral** $\\int i\\,dt$ is the area under the graph so far: how much has accumulated, in this case charge in coulombs.",
                "The exponential is the one function that reproduces itself when differentiated: $\\frac{d}{dt}e^{at} = a\\,e^{at}$, the same function again times a constant. Nothing but a multiple of $e^{at}$ behaves this way, which is why it is everywhere in circuits.",
                "$\\frac{d}{dt}\\sin(\\omega t) = \\omega\\cos(\\omega t)$ and $\\frac{d}{dt}\\cos(\\omega t) = -\\omega\\sin(\\omega t)$. The $\\omega$ appearing out front is the chain rule, and it is the reason fast signals produce big currents.",
                "The **capacitor law** is $i = C\\frac{dv}{dt}$: the current into a capacitor is proportional to how fast its voltage is changing, not to the voltage itself.",
                "Turn that around and the capacitor is an integrator: $v = \\frac{1}{C}\\int i\\,dt$. Push a constant current in and the voltage climbs in a straight line.",
                "The **inductor law** is the mirror image: $v = L\\frac{di}{dt}$. A sudden change of current through an inductor would need an infinite voltage, so current through an inductor cannot jump.",
            ],
            "sandbox": {
                "title": "Exponentials, added together",
                "visualiser": "pole-step",
                "minutes": 7,
                "initial": {"zeta": 1.4, "wn": 3},
                "brief": r'''
The same two panels as in module 2, but this time both dots sit on the horizontal
axis, so both exponents are ordinary real numbers and there is no rotation at all.
The response on the right is a sum of two decaying exponentials, and it is the
commonest shape in the whole subject.
''',
                "notice": [
                    "The caption under the left panel reads *both poles real*, and the two dots are far apart: one close to the origin, near $-1.3$, and one much further left, near $-7.1$. The far one has died away almost immediately; the near one is what you are watching for the rest of the plot.",
                    "The curve rises towards the dashed line and never crosses it. With no imaginary part there is nothing to rotate, so nothing can overshoot — a sum of decaying exponentials can only approach its final value from one side.",
                    "Push $\\zeta$ up to 1.6. The near dot creeps closer to the origin, from about $-1.26$ to about $-1.05$, and the curve now ends further short of the dashed line than it did — about 92% of the way up instead of 97%. The slowest exponential always sets the pace.",
                    "Now drag $\\zeta$ down to 0.7. The two dots change colour, lift off the horizontal axis, and the caption becomes $\\omega_d$; the response overshoots the dashed line by about 5% before settling back on it. That is the moment the exponents become complex and module 2's rotation comes back.",
                ],
            },
            "quiz": {
                "title": "Slopes, areas, and what a capacitor does",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is $\\frac{d}{dt}e^{at}$, where $a$ is a constant?",
                        "opts": ["$e^{at}$", "$t\\,e^{at}$", "$a\\,e^{at}$", "$a\\,e^{a}$"],
                        "a": 2,
                        "why": (
                            "The exponential comes back unchanged apart from a factor of $a$ from the chain rule. "
                            "Answering $e^{at}$ is the standard slip — that is only right when $a = 1$. The factor "
                            "matters: it is what makes a fast-decaying exponential also a steeply-sloping one."
                        ),
                    },
                    {
                        "q": "A capacitor has a perfectly steady voltage across it. What current flows into it?",
                        "opts": ["A steady current proportional to the voltage", "None", "An infinite current", "A current proportional to $C$ alone"],
                        "a": 1,
                        "why": (
                            "$i = C\\frac{dv}{dt}$, and a steady voltage has $\\frac{dv}{dt} = 0$, so the current is "
                            "zero however large the voltage is. This is what people mean when they say a capacitor "
                            "*blocks DC*. Confusing it with a resistor, where current is proportional to voltage, is "
                            "the mistake to avoid: for a capacitor it is proportional to the *rate of change*."
                        ),
                    },
                    {
                        "q": "What is $\\frac{d}{dt}\\sin(\\omega t)$?",
                        "opts": ["$\\cos(\\omega t)$", "$-\\omega\\cos(\\omega t)$", "$\\omega\\sin(\\omega t)$", "$\\omega\\cos(\\omega t)$"],
                        "a": 3,
                        "why": (
                            "The sine differentiates to the cosine, and the chain rule brings out the $\\omega$ from "
                            "inside the bracket. Dropping that $\\omega$ is the usual error, and it is not a small "
                            "one: it says a signal at 1 MHz changes no faster than a signal at 1 Hz. The minus sign "
                            "belongs to the derivative of the *cosine*, not the sine."
                        ),
                    },
                    {
                        "q": "A steady current $I$ flows into a capacitor $C$ for a time $T$, starting from zero volts. What is the final voltage?",
                        "opts": [
                            "$ICT$",
                            "$IT$",
                            "$\\frac{IT}{C}$",
                            "$\\frac{I}{CT}$",
                        ],
                        "a": 2,
                        "why": (
                            "Integrating the capacitor law: $v = \\frac{1}{C}\\int_0^T I\\,dt = \\frac{IT}{C}$. The "
                            "integral of a constant is the constant times the elapsed time — the area of a rectangle. "
                            "Note the shape of the answer: bigger capacitor, *smaller* voltage for the same charge, "
                            "because $C$ is on the bottom."
                        ),
                    },
                    {
                        "q": "Why can the current through an inductor not change instantly?",
                        "opts": [
                            "Because inductors have resistance",
                            "Because $v = L\\frac{di}{dt}$, and an instant change would demand an infinite voltage",
                            "Because the current has to go somewhere first",
                            "It can — inductors respond instantly",
                        ],
                        "a": 1,
                        "why": (
                            "An instantaneous jump in current means $\\frac{di}{dt}$ is infinite, and $v = L\\frac{di}{dt}$ "
                            "then demands an infinite voltage, which no real source can supply. So inductor current is "
                            "continuous. The mirror statement holds for capacitors: their *voltage* cannot jump, because "
                            "that would need infinite current."
                        ),
                    },
                    {
                        "q": "You plot current against time and measure the area under the curve. What physical quantity have you measured?",
                        "opts": ["Charge, in coulombs", "Energy, in joules", "Power, in watts", "Voltage, in volts"],
                        "a": 0,
                        "why": (
                            "Current is charge per second, so current multiplied by time is charge — and the area under "
                            "the curve is exactly that product, accumulated over an interval where the current varies. "
                            "Energy would need the area under a *power* curve, and power is voltage times current, not "
                            "current alone."
                        ),
                    },
                ],
            },
            "build": {
                "title": "Integration you can watch",
                "minutes": 20,
                "brief": r'''
There is a capacitor on the canvas already, with a probe on its top plate and its
bottom plate grounded. Nothing is driving it, so the probe reads a flat zero.

Add a **current source** — the part marked `I` — and wire it so that a steady
current flows into that capacitor. A current source pushes a fixed number of amps
around the loop regardless of what voltage that takes, which is the electrical way
of saying "the input is a constant".

The capacitor then integrates that constant. Get the values right and the probe
voltage must **climb in a straight line at exactly 1 volt per millisecond**, so it
reads 1 V after 1 ms, 2 V after 2 ms, and is still climbing at the same rate at
3 ms. Straight, not curved: this is the integral of a constant.

From $i = C\dfrac{dv}{dt}$, a constant current $I$ gives a slope of
$\dfrac{dv}{dt} = \dfrac{I}{C}$, so it is the *ratio* you have to get right. Any
current and capacitance with that ratio will pass.

To run it yourself, choose **Transient** in the analysis panel, set *Stop after* to
`3m`, and press Solve.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "C", "x": 3, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 3, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 3], "b": [3, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "C", "x": 3, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 3, "y": 3},
                        {"id": "p3", "kind": "I", "x": 4, "y": 4, "rot": 0, "value": 1e-3},
                        {"id": "p4", "kind": "GND", "x": 5, "y": 6},
                    ],
                    "wires": [
                        {"a": [3, 3], "b": [3, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [5, 4], "b": [5, 6]},
                    ],
                },
                "checks": [
                    {"name": "the probe starts at zero and rises", "code": r'''
const s = c.step(3e-3);
c.assert(Math.abs(s.v[0]) < 0.02, "an uncharged capacitor starts at 0 V, but the probe begins at " +
  c.fmt(s.v[0], "V"));
c.assert(s.v[s.v.length - 1] > 0.5, "after 3 ms the probe reads " + c.fmt(s.v[s.v.length - 1], "V") +
  "; it should have climbed to about 3 V. If it went downwards, the current is flowing the wrong way.");
'''},
                    {"name": "one millisecond in, it reads 1 volt", "code": r'''
const s = c.step(3e-3);
let k = 0;
for (let i = 1; i < s.t.length; i++) {
  if (Math.abs(s.t[i] - 1e-3) < Math.abs(s.t[k] - 1e-3)) k = i;
}
c.close(s.v[k], 1.0, 0.05, "the probe voltage after 1 ms");
'''},
                    {"name": "two milliseconds in, it reads 2 volts", "code": r'''
const s = c.step(3e-3);
let k = 0;
for (let i = 1; i < s.t.length; i++) {
  if (Math.abs(s.t[i] - 2e-3) < Math.abs(s.t[k] - 2e-3)) k = i;
}
c.close(s.v[k], 2.0, 0.05, "the probe voltage after 2 ms — twice the time, twice the voltage");
'''},
                    {"name": "the climb does not flatten off", "code": r'''
const s = c.step(3e-3);
const n = s.t.length - 1;
const m = Math.round(n * 2 / 3);
const slope = (s.v[n] - s.v[m]) / (s.t[n] - s.t[m]);
c.close(slope, 1000, 0.05, "the slope over the last millisecond, in volts per second");
'''},
                ],
                "hints": [
                    "One millisecond is $10^{-3}$ s, so 1 volt per millisecond is a slope of 1000 volts per second. You need $I/C = 1000$.",
                    "With the capacitor left at 1 µF, that means a current of 1 mA. Type it as `1m` in the value box.",
                    "The current source needs a complete loop: one end on the capacitor's top node, the other end down to a ground of its own.",
                    "If the voltage ramps downwards instead of upwards, the source is pushing current the other way round. Rotate it, or swap which of its two ends you grounded.",
                ],
            },
            "lab": {
                "title": "Slopes and areas from samples",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
The circuit you just built did the integration in hardware. Now do both operations
in software, on lists of measured samples — which is what an oscilloscope, or any
simulator, actually has to work with.

`cap_current(times, volts, C)` returns the current into a capacitor at each sample,
using $i = C\frac{dv}{dt}$. Estimate the slope with a **central difference**: at
sample $k$ in the middle of the list,

$$\frac{dv}{dt} \approx \frac{v_{k+1} - v_{k-1}}{t_{k+1} - t_{k-1}}$$

At the two ends there is no neighbour on one side, so use the one-sided difference
with the sample that does exist.

`cap_voltage(times, currents, C)` goes the other way: $v = \frac{1}{C}\int i\,dt$,
starting from 0 V, using the **trapezoid rule**. Each step adds the area of a
trapezoid of width $t_k - t_{k-1}$ and average height $(i_k + i_{k-1})/2$, then
divides by $C$. Return a list the same length as `times`, beginning with `0.0`.

Both rules are exact when the thing they are applied to is a straight line, which
is why the checks start there.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def cap_current(times, volts, C):
    """Return i = C dv/dt at every sample: central differences inside, one-sided at the ends."""
    # TODO: build a list the same length as `times`.
    return []


def cap_voltage(times, currents, C):
    """Return v = (1/C) * integral of i dt at every sample, starting from 0 V."""
    # TODO: trapezoid rule, accumulating as you go. First entry is 0.0.
    return []


if __name__ == "__main__":
    ts = [k * 1e-5 for k in range(101)]
    vs = [1000.0 * t for t in ts]          # a 1 V per ms ramp, as in the circuit
    C = 1e-6
    i = cap_current(ts, vs, C)
    print("current into the capacitor:", i[:3], "...")
    back = cap_voltage(ts, i, C)
    print("integrated back to:", round(back[-1], 6), "V after", ts[-1], "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def cap_current(times, volts, C):
    """Return i = C dv/dt at every sample: central differences inside, one-sided at the ends."""
    n = len(times)
    out = []
    for k in range(n):
        if k == 0:
            slope = (volts[1] - volts[0]) / (times[1] - times[0])
        elif k == n - 1:
            slope = (volts[n - 1] - volts[n - 2]) / (times[n - 1] - times[n - 2])
        else:
            slope = (volts[k + 1] - volts[k - 1]) / (times[k + 1] - times[k - 1])
        out.append(C * slope)
    return out


def cap_voltage(times, currents, C):
    """Return v = (1/C) * integral of i dt at every sample, starting from 0 V."""
    out = [0.0]
    for k in range(1, len(times)):
        h = times[k] - times[k - 1]
        area = h * (currents[k] + currents[k - 1]) / 2.0
        out.append(out[-1] + area / C)
    return out


if __name__ == "__main__":
    ts = [k * 1e-5 for k in range(101)]
    vs = [1000.0 * t for t in ts]          # a 1 V per ms ramp, as in the circuit
    C = 1e-6
    i = cap_current(ts, vs, C)
    print("current into the capacitor:", i[:3], "...")
    back = cap_voltage(ts, i, C)
    print("integrated back to:", round(back[-1], 6), "V after", ts[-1], "s")
'''}],
                "hints": [
                    "Handle the three cases in order: `k == 0`, `k == n - 1`, and everything in between. The central difference spans *two* steps, so its denominator is `times[k+1] - times[k-1]`, not one step.",
                    "Do not forget to multiply the slope by `C`. The units only work out as amps if you do.",
                    "In `cap_voltage`, start the output list as `[0.0]` and append one entry per gap between samples. The list then ends up the same length as `times`.",
                    "Check yourself on the ramp before running anything else: a straight line of slope 1000 V/s through a 1 µF capacitor must give exactly 1 mA at every single sample, ends included.",
                ],
                "tests": [
                    {"name": "a straight ramp gives a constant current", "code": r'''
_ts = [k * 1e-5 for k in range(101)]
_vs = [1000.0 * t for t in _ts]
_i = cap_current(_ts, _vs, 1e-6)
assert len(_i) == len(_ts), f"expected {len(_ts)} samples of current, got {len(_i)}"
for _k, _val in enumerate(_i):
    assert abs(_val - 1e-3) < 1e-12, \
        f"sample {_k} should be 1 mA everywhere on a straight ramp, got {_val}"
'''},
                    {"name": "the ends are handled too", "code": r'''
_ts = [0.0, 1e-5, 2e-5, 3e-5]
_vs = [0.0, 2.0, 4.0, 6.0]
_i = cap_current(_ts, _vs, 2e-6)
assert abs(_i[0] - 0.4) < 1e-12, f"first sample should use a one-sided slope: 2e-6 * 2e5 = 0.4 A, got {_i[0]}"
assert abs(_i[-1] - 0.4) < 1e-12, f"last sample should do the same, got {_i[-1]}"
'''},
                    {"name": "a sinusoid gives the chain rule back", "code": r'''
import math
_w = 2.0 * math.pi * 50.0
_ts = [k * 1e-5 for k in range(2001)]
_vs = [math.sin(_w * t) for t in _ts]
_i = cap_current(_ts, _vs, 1e-6)
_want = 1e-6 * _w
assert abs(_i[0] - _want) < 1e-9, \
    f"at t=0 the slope is w*cos(0) = {_w:.4f}, so i should be {_want:.6e}, got {_i[0]:.6e}"
assert abs(max(_i) - _want) < 1e-9, \
    f"the peak current should be C*w = {_want:.6e}, got {max(_i):.6e}"
'''},
                    {"name": "a constant current integrates to a ramp", "code": r'''
_ts = [k * 1e-5 for k in range(101)]
_is = [1e-3] * len(_ts)
_v = cap_voltage(_ts, _is, 1e-6)
assert len(_v) == len(_ts), f"expected {len(_ts)} samples of voltage, got {len(_v)}"
assert abs(_v[0]) < 1e-15, f"it must start from 0 V, got {_v[0]}"
assert abs(_v[-1] - 1.0) < 1e-12, \
    f"1 mA into 1 uF for 1 ms is exactly 1 V, got {_v[-1]}"
assert abs(_v[50] - 0.5) < 1e-12, f"halfway through it should be at 0.5 V, got {_v[50]}"
'''},
                    {"name": "a rising current integrates to a curve", "code": r'''
_ts = [k * 1e-5 for k in range(101)]
_is = [1.0 * t for t in _ts]
_v = cap_voltage(_ts, _is, 1e-6)
assert abs(_v[-1] - 0.5) < 1e-12, \
    f"the area under a triangle of height 1e-3 and width 1e-3 is 5e-7 C, so 0.5 V, got {_v[-1]}"
'''},
                    {"name": "differentiating then integrating returns the original", "code": r'''
import math
_ts = [k * 1e-5 for k in range(501)]
_vs = [3.0 * math.sin(2.0 * math.pi * 50.0 * t) for t in _ts]
_back = cap_voltage(_ts, cap_current(_ts, _vs, 1e-6), 1e-6)
for _k in range(0, len(_ts), 25):
    assert abs(_back[_k] - _vs[_k]) < 2e-3, \
        f"at sample {_k} the round trip gave {_back[_k]:.6f} against the original {_vs[_k]:.6f}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "First-order equations, and equations solved all at once",
            "summary": "One equation that involves a rate of change, and several equations that must hold simultaneously. Circuits produce both.",
            "concepts": [
                "A **differential equation** is an equation containing a derivative. A resistor and a capacitor in series across a source obey $\\frac{dv}{dt} = \\frac{V_s - v}{RC}$: the rate of change depends on how far you still have to go.",
                "Its solution, starting from $v(0) = 0$, is $v(t) = V_s\\left(1 - e^{-t/RC}\\right)$. You do not have to take that on trust: differentiate it, put both sides of the equation side by side, and they agree.",
                "The product $RC$ has units of seconds and is called the **time constant**, written $\\tau$. After one $\\tau$ the response has covered $1 - e^{-1} = 63.2\\%$ of the distance; after five, 99.3%.",
                "An inductor and a resistor give the same equation with $\\tau = L/R$. One resistor and one energy store always produce a first-order equation, whichever store it is.",
                "A network of resistors instead gives **simultaneous equations**: one current-balance equation per node, all of which must hold at once.",
                "Those equations are written as a matrix: $G\\mathbf{v} = \\mathbf{i}$, where each diagonal entry of $G$ is the sum of the conductances at that node and each off-diagonal entry is minus the conductance joining two nodes.",
                "A 2×2 system is solved by the **determinant**: $\\det = a_{11}a_{22} - a_{12}a_{21}$, and there is a single answer exactly when that determinant is not zero.",
            ],
            "sandbox": {
                "title": "Two equations at once, coupled or not",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": -1, "a12": 0, "a21": 0, "a22": -2},
                "brief": r'''
The four sliders are the four entries of a 2×2 matrix, and the matrix says how fast
each of two quantities changes in terms of both of them. Take $x_1$ to be a voltage
somewhere in a circuit and $x_2$ to be a voltage somewhere else.

It opens with both off-diagonal entries at zero, which means the two quantities do
not affect each other at all: $\dot{x_1} = -x_1$ and $\dot{x_2} = -2x_2$, two
separate first-order equations, each with the exponential solution from this
module.
''',
                "notice": [
                    "Every arrow points inwards and every curve ends at the origin: both exponentials decay. The readout underneath says *stable node*, and gives $\\text{trace} = -3$, $\\det = 2$.",
                    "The curves flatten onto the horizontal axis before they arrive. $x_2$ decays twice as fast as $x_1$, so the vertical part of the motion is over first and the slow coordinate finishes the journey alone. The slowest time constant always wins in the end.",
                    "Set $a_{12}$ to 1. The two equations are now coupled — $x_2$ feeds into $\\dot{x_1}$ — and the curves visibly lean over. But the trace and determinant in the readout do not move at all, and it is still a stable node: coupling changed the paths without changing the two decay rates.",
                    "Put $a_{12}$ back to 0 and raise $a_{11}$ to $+0.5$. The determinant goes negative, the readout changes to *saddle*, and the curves run away along the horizontal axis. One positive rate is enough to ruin the whole system, however well behaved the other one is.",
                ],
            },
            "quiz": {
                "title": "Time constants and determinants",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A resistor and capacitor charge a node from a step of $V_s$ volts. After exactly one time constant, how far has the output got?",
                        "opts": ["Exactly half way", "About 37% of the way", "About 63% of the way to $V_s$", "All the way"],
                        "a": 2,
                        "why": (
                            "$v(\\tau) = V_s(1 - e^{-1}) = 0.632\\,V_s$. The 37% figure is the very same number seen "
                            "from the other side — it is the fraction *remaining*, $e^{-1}$ — and mixing the two up "
                            "is the classic error. Half way happens a little earlier, at $0.693\\tau$."
                        ),
                    },
                    {
                        "q": "You double the resistance and halve the capacitance. What happens to the time constant $\\tau = RC$?",
                        "opts": ["It doubles", "It stays the same", "It halves", "It is quartered"],
                        "a": 1,
                        "why": (
                            "$\\tau$ depends only on the *product*: $(2R)(C/2) = RC$. This is why a build check on a "
                            "time constant cannot ask for particular values of $R$ and $C$ — infinitely many pairs "
                            "give the same behaviour, and the circuit does not know which pair you chose."
                        ),
                    },
                    {
                        "q": "Which function solves $\\frac{dv}{dt} = \\frac{V_s - v}{\\tau}$ with $v(0) = 0$?",
                        "opts": [
                            "$V_s e^{-t/\\tau}$",
                            "$V_s\\frac{t}{\\tau}$",
                            "$V_s\\left(1 - e^{-t/\\tau}\\right)$",
                            "$V_s\\left(1 + e^{-t/\\tau}\\right)$",
                        ],
                        "a": 2,
                        "why": (
                            "Test the candidates at $t = 0$ and at $t = \\infty$: the answer must start at 0 and finish "
                            "at $V_s$. Only $V_s(1 - e^{-t/\\tau})$ does both. $V_s e^{-t/\\tau}$ is the *decaying* solution, which "
                            "answers a different question — a charged capacitor emptying itself — and the straight "
                            "line would need a constant current, not a resistor."
                        ),
                    },
                    {
                        "q": "You write the node equations of a resistor network as $G\\mathbf{v} = \\mathbf{i}$. What sits on the diagonal of $G$?",
                        "opts": [
                            "The resistance of the largest resistor at that node",
                            "The voltage at that node",
                            "Always 1",
                            "The sum of all the conductances touching that node",
                        ],
                        "a": 3,
                        "why": (
                            "Each row is a current balance at one node. The node's own voltage appears once for every "
                            "component attached to it, so the coefficients add up: the diagonal entry is $\\sum 1/R$ "
                            "over everything touching the node. Conductances, not resistances — that is why the "
                            "matrix is built from $1/R$ throughout, and why the off-diagonal entries are negative."
                        ),
                    },
                    {
                        "q": "A 2×2 system of simultaneous equations has no single answer when the determinant is:",
                        "opts": ["Zero", "One", "Negative", "Very large"],
                        "a": 0,
                        "why": (
                            "The determinant divides the answer, so a determinant of zero means there is no single "
                            "answer to divide out — the two equations are either the same equation twice, or they "
                            "contradict each other. A negative determinant is perfectly ordinary and just means the "
                            "solution comes out with the signs the algebra gives it."
                        ),
                    },
                    {
                        "q": "Multiply an ohm by a farad. What unit do you get?",
                        "opts": ["A hertz", "A second", "A volt", "An amp"],
                        "a": 1,
                        "why": (
                            "Ohms times farads is seconds, which is why $\\tau = RC$ is a time at all. It is worth "
                            "checking this the long way once: an ohm is volts per amp and a farad is coulombs per "
                            "volt, so the product is coulombs per amp, and an amp is coulombs per second. A useful "
                            "habit — if the units of a formula are wrong, the formula is wrong."
                        ),
                    },
                ],
            },
            "build": {
                "title": "A circuit with a time constant of one millisecond",
                "minutes": 22,
                "brief": r'''
The canvas has a 5 V source, a ground, and a probe sitting straight on the source,
so the probe jumps to 5 V the instant the supply appears. Put something between them
that makes the rise take time.

Build a circuit driven by that 5 V source whose probe voltage:

1. starts at **0 V**,
2. rises to **5 V** and stays there,
3. passes 63% of the way — that is 3.16 V — after exactly **1 millisecond**,
4. and is 95% of the way there at 3 ms, because the rise is exponential rather than
   a straight climb.

You need one resistor and one energy store. It can be a capacitor, with
$\tau = RC$; it can equally be an **inductor** (the part marked `L`), with
$\tau = L/R$. Either gives the same differential equation and the same curve, which
is the point of the module — and only one of the two is drawn in the reference
answer, so pick whichever you can reason about.

To see the response, choose **Transient**, set *Stop after* to `5m` and press Solve.

An inductor resists changes in current, so with an inductor in series the current
starts at zero and builds up; put the probe where the growing current shows as a
growing voltage.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
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
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.1},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 100},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 9, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "the output starts at zero, not at the supply", "code": r'''
const s = c.step(6e-3);
c.assert(Math.abs(s.v[0]) < 0.05, "at the instant the supply appears the probe already reads " +
  c.fmt(s.v[0], "V") + "; there is nothing between the source and the probe to slow it down");
'''},
                    {"name": "it settles at the full 5 volts", "code": r'''
const s = c.step(2e-2);
c.close(s.v[s.v.length - 1], 5.0, 0.02, "the settled output voltage");
'''},
                    {"name": "it is 63% of the way there after 1 ms", "code": r'''
const s = c.step(6e-3);
let k = -1;
for (let i = 0; i < s.v.length; i++) {
  if (s.v[i] >= 0.632 * 5.0) { k = i; break; }
}
c.assert(k >= 0, "the output never reaches 3.16 V within 6 ms — the time constant is far too long");
c.close(s.t[k], 1e-3, 0.1, "the time taken to reach 63% of the supply");
'''},
                    {"name": "the rise is exponential, not a straight line", "code": r'''
const s = c.step(6e-3);
let k = 0;
for (let i = 1; i < s.t.length; i++) {
  if (Math.abs(s.t[i] - 3e-3) < Math.abs(s.t[k] - 3e-3)) k = i;
}
c.close(s.v[k], 4.7515, 0.04, "the output at 3 ms, which should be 95% of the way there");
'''},
                ],
                "hints": [
                    "For the inductor route: $\\tau = L/R$, and you need $\\tau = 1$ ms. Choose the resistor first — 100 Ω, say — and the inductance follows as $L = \\tau R$. Type it as `100m`.",
                    "For the capacitor route: $\\tau = RC$, so a 1 kΩ resistor with a 1 µF capacitor gives exactly 1 ms.",
                    "The probe must go on the node between the two parts, not on the source. On the source there is nothing to measure.",
                    "Both parts need somewhere to send their current: the second one should end at a ground.",
                    "If the response is over almost instantly, your time constant is too small by a factor you can read straight off the plot — the time axis is labelled.",
                ],
            },
            "lab": {
                "title": "Solving a network all at once",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
A resistor network does not have one equation with one unknown; it has one equation
per node, and they all have to hold at the same time. This lab writes and solves
such a pair.

`solve2(a11, a12, a21, a22, b1, b2)` solves

$$a_{11}x_1 + a_{12}x_2 = b_1, \qquad a_{21}x_1 + a_{22}x_2 = b_2$$

by determinants. Work out $\det = a_{11}a_{22} - a_{12}a_{21}$ first. If it is zero
there is no single answer, so raise `ValueError`. Otherwise

$$x_1 = \frac{b_1 a_{22} - a_{12} b_2}{\det}, \qquad x_2 = \frac{a_{11} b_2 - b_1 a_{21}}{\det}$$

`ladder(vs, r1, r2, r3)` uses it on a real circuit: a source `vs` feeds `r1` into
node 1, `r2` joins node 1 to node 2, and `r3` takes node 2 down to ground. Balancing
the currents at each node gives

$$\begin{bmatrix} \frac{1}{r_1} + \frac{1}{r_2} & -\frac{1}{r_2} \\ -\frac{1}{r_2} & \frac{1}{r_2} + \frac{1}{r_3} \end{bmatrix}\begin{bmatrix} v_1 \\ v_2 \end{bmatrix} = \begin{bmatrix} \frac{v_s}{r_1} \\ 0 \end{bmatrix}$$

Build those six numbers and hand them to `solve2`. Notice the pattern: the sum of
the conductances on the diagonal, minus the shared conductance off it, and the
source appearing only in the row of the node it feeds.
''',
                "files": [{"name": "main.py", "content": r'''
def solve2(a11, a12, a21, a22, b1, b2):
    """Solve two simultaneous equations by determinants.

    Raise ValueError when the determinant is zero.
    """
    # TODO: determinant first, then the two answers.
    return (0.0, 0.0)


def ladder(vs, r1, r2, r3):
    """Node voltages of  vs -[r1]- node1 -[r2]- node2 -[r3]- ground."""
    # TODO: build the four matrix entries and the two right-hand sides,
    # then call solve2.
    return (0.0, 0.0)


if __name__ == "__main__":
    print("solve2:", solve2(2.0, 1.0, 1.0, 3.0, 5.0, 10.0))
    print("ladder, three equal resistors:", ladder(3.0, 1000.0, 1000.0, 1000.0))
    print("ladder, 1k 2k 3k from 9 V:", ladder(9.0, 1000.0, 2000.0, 3000.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def solve2(a11, a12, a21, a22, b1, b2):
    """Solve two simultaneous equations by determinants.

    Raise ValueError when the determinant is zero.
    """
    det = a11 * a22 - a12 * a21
    if abs(det) < 1e-15:
        raise ValueError("the determinant is zero: these two equations do not fix a single answer")
    x1 = (b1 * a22 - a12 * b2) / det
    x2 = (a11 * b2 - b1 * a21) / det
    return (x1, x2)


def ladder(vs, r1, r2, r3):
    """Node voltages of  vs -[r1]- node1 -[r2]- node2 -[r3]- ground."""
    g11 = 1.0 / r1 + 1.0 / r2
    g12 = -1.0 / r2
    g21 = -1.0 / r2
    g22 = 1.0 / r2 + 1.0 / r3
    return solve2(g11, g12, g21, g22, vs / r1, 0.0)


if __name__ == "__main__":
    print("solve2:", solve2(2.0, 1.0, 1.0, 3.0, 5.0, 10.0))
    print("ladder, three equal resistors:", ladder(3.0, 1000.0, 1000.0, 1000.0))
    print("ladder, 1k 2k 3k from 9 V:", ladder(9.0, 1000.0, 2000.0, 3000.0))
'''}],
                "hints": [
                    "Compute the determinant once and store it. You need it twice, and testing it for zero before dividing is what stops the function crashing on a badly posed network.",
                    "Compare floating-point numbers against a small tolerance rather than exactly: `abs(det) < 1e-15`.",
                    "In `ladder`, everything is a conductance — $1/r$ — never a resistance. If your answers come out enormous, that is the reason.",
                    "Sanity-check the three-equal-resistor case by hand: the same current flows through all three, so the voltages must be two thirds and one third of the source.",
                ],
                "tests": [
                    {"name": "a small system comes out right", "code": r'''
_x1, _x2 = solve2(2.0, 1.0, 1.0, 3.0, 5.0, 10.0)
assert abs(_x1 - 1.0) < 1e-12 and abs(_x2 - 3.0) < 1e-12, \
    f"expected (1, 3), got ({_x1}, {_x2})"
'''},
                    {"name": "the answers really satisfy both equations", "code": r'''
_a = (3.0, -2.0, 4.0, 5.0)
_b = (7.0, -1.0)
_x1, _x2 = solve2(_a[0], _a[1], _a[2], _a[3], _b[0], _b[1])
assert abs(_a[0] * _x1 + _a[1] * _x2 - _b[0]) < 1e-9, "the first equation is not satisfied"
assert abs(_a[2] * _x1 + _a[3] * _x2 - _b[1]) < 1e-9, "the second equation is not satisfied"
'''},
                    {"name": "a zero determinant is refused", "code": r'''
try:
    solve2(1.0, 2.0, 2.0, 4.0, 1.0, 2.0)
except ValueError:
    pass
else:
    raise AssertionError("the second equation is just twice the first, so ValueError was expected")
'''},
                    {"name": "three equal resistors divide evenly", "code": r'''
_v1, _v2 = ladder(3.0, 1000.0, 1000.0, 1000.0)
assert abs(_v1 - 2.0) < 1e-9, f"node 1 should sit at two thirds of 3 V, got {_v1}"
assert abs(_v2 - 1.0) < 1e-9, f"node 2 should sit at one third of 3 V, got {_v2}"
'''},
                    {"name": "unequal resistors divide in proportion", "code": r'''
_v1, _v2 = ladder(9.0, 1000.0, 2000.0, 3000.0)
assert abs(_v1 - 7.5) < 1e-9, f"expected 7.5 V at node 1, got {_v1}"
assert abs(_v2 - 4.5) < 1e-9, f"expected 4.5 V at node 2, got {_v2}"
'''},
                    {"name": "a big resistor to ground draws almost nothing", "code": r'''
_v1, _v2 = ladder(10.0, 1000.0, 1000.0, 1e9)
assert abs(_v1 - 10.0) < 1e-3, f"with almost no current there is almost no drop across r1, got {_v1}"
assert abs(_v2 - 10.0) < 1e-3, f"and none across r2 either, got {_v2}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "One RC network, computed four ways",
        "runtime": "python",
        "minutes": 130,
        "brief": r'''
Everything in this course points at the same small circuit: a source, a resistor,
and a capacitor. You now know four different ways to say what it does, one from
each module, and they must all agree.

Build a single file that computes all four and checks them against each other.

## The circuit

A source $V_s$ drives a resistor $R$, which feeds a node; a capacitor $C$ takes that
node down to ground. The node is the output.

## The four descriptions

1. **As simultaneous equations.** At DC the capacitor passes nothing, so the circuit
   is resistive and a network of resistors becomes a matrix. Write a general solver
   `solve_nodes(G, b)` for an $n \times n$ system, by Gaussian elimination with
   partial pivoting — that is, at each column, swap the row with the largest entry
   into place before dividing, so you never divide by something tiny.

2. **As a complex number.** At a frequency $f$ the output is the input multiplied by
   $G(f) = 1/(1 + j2\pi fRC)$. Its modulus is the size of the output and its
   argument is the phase shift.

3. **As a differential equation, solved numerically.** $\frac{dv}{dt} = (V_s - v)/RC$
   stepped forward in small increments of `dt` from $v = 0$.

4. **As a differential equation, solved on paper.** $v(t) = V_s(1 - e^{-t/RC})$ —
   and confirmed with SymPy, by substituting it back into the equation and asking
   whether what is left over is zero.

## Suggested order

`solve_nodes` first, because it is the only one with any real bookkeeping in it, and
the checks for it do not depend on anything else. Then the two one-line functions in
the frequency domain. Then the two step responses, which is where the numbers have
to start agreeing with each other.

The last function, `satisfies_ode`, is where SymPy earns its place: it does the
differentiation symbolically, so you find out whether your closed form is right
rather than whether it happens to match at the points you sampled.
''',
        "deliverables": [
            "`solve_nodes(G, b)` — Gaussian elimination with partial pivoting on an n x n system, returning the list of node voltages, and raising `ValueError` on a singular matrix.",
            "`lowpass_gain(R, C, f)` and `corner_frequency(R, C)` — the complex gain at a frequency, and the frequency at which its modulus falls to $1/\\sqrt{2}$.",
            "`step_euler(vs, R, C, dt, steps)` — the differential equation stepped forward numerically from 0 V, returning `steps + 1` samples.",
            "`analytic_step(vs, R, C, t)` — the closed-form solution at a single time.",
            "`satisfies_ode(vs, R, C)` — substitute the closed form back into the differential equation with SymPy and return whether the remainder is exactly zero.",
        ],
        "constraints": [
            "The standard library, NumPy and SymPy only. No SciPy, and no circuit-simulation library.",
            "`solve_nodes` must work for any size of system, not just 2 x 2 — the checks use a three-node ladder as well as a two-node one.",
            "Use partial pivoting, not plain elimination: a zero in a pivot position must be swapped away rather than divided by.",
            "`step_euler` must start from 0 V and return a list of length `steps + 1`, so that sample `k` is the voltage at time `k * dt`.",
            "`satisfies_ode` must do the differentiation symbolically. Sampling the two sides at a few times and comparing is not the same claim.",
        ],
        "rubric": [
            {"criterion": "The linear solver", "weight": 30,
             "evidence": "solve_nodes returns the correct node voltages for both a two-node and a three-node resistive ladder, pivots rather than dividing by a zero, and raises ValueError when the matrix is singular."},
            {"criterion": "The frequency description", "weight": 25,
             "evidence": "lowpass_gain has modulus 1 at zero frequency and modulus 1/sqrt(2) with a phase of exactly -45 degrees at the frequency returned by corner_frequency."},
            {"criterion": "The two step responses agree", "weight": 25,
             "evidence": "step_euler starts at zero, has the right length, and tracks analytic_step to within a fraction of a percent once the step size is small; both settle at the supply voltage."},
            {"criterion": "The symbolic confirmation", "weight": 20,
             "evidence": "satisfies_ode returns True for several different values of vs, R and C, and gets there by differentiating the closed form symbolically and simplifying the remainder to zero, rather than by sampling both sides at a few times and comparing."},
        ],
        "hints": [
            "For `solve_nodes`, copy `G` into a working matrix with `b` appended as an extra column. Reduce that one array and the answers are left in the last column.",
            "Partial pivoting is one line: before dividing by `M[col][col]`, find the row at or below `col` whose entry in that column has the largest absolute value, and swap it up.",
            "`corner_frequency` is $1/(2\\pi RC)$. Do not compute it by searching the response — you know it in closed form.",
            "For `step_euler`, one step is `v = v + dt * (vs - v) / (R * C)`. Append after stepping, and put the initial `0.0` in before the loop starts.",
            "In `satisfies_ode`, build the symbol with `t = sympy.symbols('t', positive=True)`, form the expression, and test `sympy.simplify(sympy.diff(v, t) - (vs - v) / (R * C)) == 0`.",
        ],
        "files": [
            {"name": "main.py", "content": r'''
import math
import sympy as sp


def solve_nodes(G, b):
    """Solve G x = b by Gaussian elimination with partial pivoting.

    G is a list of n rows, each a list of n floats; b is a list of n floats.
    Return the list of n answers. Raise ValueError if G is singular.
    """
    # TODO
    return []


def lowpass_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C)."""
    # TODO
    return 0j


def corner_frequency(R, C):
    """The frequency at which the modulus of the gain is 1/sqrt(2)."""
    # TODO
    return 0.0


def step_euler(vs, R, C, dt, steps):
    """Step dv/dt = (vs - v) / (R*C) forward from 0 V. Return steps + 1 samples."""
    # TODO
    return []


def analytic_step(vs, R, C, t):
    """The closed-form solution at time t, starting from 0 V."""
    # TODO
    return 0.0


def satisfies_ode(vs, R, C):
    """True if the closed form satisfies dv/dt = (vs - v)/(R*C), checked symbolically."""
    # TODO
    return False


if __name__ == "__main__":
    G = [[0.0015, -0.0005], [-0.0005, 0.0008333333333333334]]
    b = [0.009, 0.0]
    print("node voltages:", solve_nodes(G, b))
    R, C = 1000.0, 1e-6
    print("corner frequency:", round(corner_frequency(R, C), 3), "Hz")
    print("gain there:", lowpass_gain(R, C, corner_frequency(R, C)))
    tau = R * C
    ys = step_euler(5.0, R, C, tau / 2000.0, 6000)
    print("numerical at 3 tau:", round(ys[-1], 6))
    print("analytic  at 3 tau:", round(analytic_step(5.0, R, C, 3.0 * tau), 6))
    print("closed form satisfies the equation:", satisfies_ode(5.0, R, C))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import math
import sympy as sp


def solve_nodes(G, b):
    """Solve G x = b by Gaussian elimination with partial pivoting.

    G is a list of n rows, each a list of n floats; b is a list of n floats.
    Return the list of n answers. Raise ValueError if G is singular.
    """
    n = len(b)
    M = [list(G[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        piv = col
        for r in range(col + 1, n):
            if abs(M[r][col]) > abs(M[piv][col]):
                piv = r
        if abs(M[piv][col]) < 1e-15:
            raise ValueError("the network does not fix a single set of voltages")
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        for cc in range(col, n + 1):
            M[col][cc] /= d
        for r in range(n):
            if r == col:
                continue
            f = M[r][col]
            if f == 0.0:
                continue
            for cc in range(col, n + 1):
                M[r][cc] -= f * M[col][cc]
    return [M[i][n] for i in range(n)]


def lowpass_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C)."""
    return 1.0 / (1.0 + 1j * 2.0 * math.pi * f * R * C)


def corner_frequency(R, C):
    """The frequency at which the modulus of the gain is 1/sqrt(2)."""
    return 1.0 / (2.0 * math.pi * R * C)


def step_euler(vs, R, C, dt, steps):
    """Step dv/dt = (vs - v) / (R*C) forward from 0 V. Return steps + 1 samples."""
    tau = R * C
    v = 0.0
    out = [0.0]
    for _ in range(steps):
        v = v + dt * (vs - v) / tau
        out.append(v)
    return out


def analytic_step(vs, R, C, t):
    """The closed-form solution at time t, starting from 0 V."""
    return vs * (1.0 - math.exp(-t / (R * C)))


def satisfies_ode(vs, R, C):
    """True if the closed form satisfies dv/dt = (vs - v)/(R*C), checked symbolically."""
    t = sp.symbols("t", positive=True)
    v = vs * (1 - sp.exp(-t / (R * C)))
    remainder = sp.simplify(sp.diff(v, t) - (vs - v) / (R * C))
    return remainder == 0


if __name__ == "__main__":
    G = [[0.0015, -0.0005], [-0.0005, 0.0008333333333333334]]
    b = [0.009, 0.0]
    print("node voltages:", solve_nodes(G, b))
    R, C = 1000.0, 1e-6
    print("corner frequency:", round(corner_frequency(R, C), 3), "Hz")
    print("gain there:", lowpass_gain(R, C, corner_frequency(R, C)))
    tau = R * C
    ys = step_euler(5.0, R, C, tau / 2000.0, 6000)
    print("numerical at 3 tau:", round(ys[-1], 6))
    print("analytic  at 3 tau:", round(analytic_step(5.0, R, C, 3.0 * tau), 6))
    print("closed form satisfies the equation:", satisfies_ode(5.0, R, C))
'''},
        ],
        "tests": [
            {"name": "a two-node ladder solves correctly", "code": r'''
_G = [[0.0015, -0.0005], [-0.0005, 1.0 / 2000.0 + 1.0 / 3000.0]]
_b = [0.009, 0.0]
_v = solve_nodes(_G, _b)
assert len(_v) == 2, f"expected 2 node voltages, got {len(_v)}"
assert abs(_v[0] - 7.5) < 1e-9, f"node 1 should be 7.5 V, got {_v[0]}"
assert abs(_v[1] - 4.5) < 1e-9, f"node 2 should be 4.5 V, got {_v[1]}"
'''},
            {"name": "a three-node ladder solves correctly", "code": r'''
_g = 1.0 / 1000.0
_G = [[2 * _g, -_g, 0.0], [-_g, 2 * _g, -_g], [0.0, -_g, 2 * _g]]
_b = [4.0 * _g, 0.0, 0.0]
_v = solve_nodes(_G, _b)
for _k, _want in enumerate([3.0, 2.0, 1.0]):
    assert abs(_v[_k] - _want) < 1e-9, f"node {_k + 1} should be {_want} V, got {_v[_k]}"
'''},
            {"name": "pivoting handles a zero in the way", "code": r'''
_G = [[0.0, 2.0], [1.0, 1.0]]
_b = [4.0, 3.0]
_v = solve_nodes(_G, _b)
assert abs(_v[0] - 1.0) < 1e-9 and abs(_v[1] - 2.0) < 1e-9, \
    f"expected (1, 2), got {_v} — the first pivot is zero and must be swapped away"
'''},
            {"name": "a singular matrix is refused", "code": r'''
try:
    solve_nodes([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])
except ValueError:
    pass
else:
    raise AssertionError("the second row is twice the first, so ValueError was expected")
'''},
            {"name": "the gain is right at zero frequency and at the corner", "code": r'''
import math
_R, _C = 1000.0, 1e-6
assert abs(lowpass_gain(_R, _C, 0.0) - 1.0) < 1e-12, "at DC the filter passes everything"
_fc = corner_frequency(_R, _C)
assert abs(_fc - 159.15494309189535) < 1e-6, f"expected about 159.15 Hz, got {_fc}"
_g = lowpass_gain(_R, _C, _fc)
assert abs(abs(_g) - 0.7071067811865475) < 1e-9, f"the modulus should be 1/sqrt(2), got {abs(_g)}"
assert abs(math.degrees(math.atan2(_g.imag, _g.real)) - (-45.0)) < 1e-9, \
    "the phase at the corner should be exactly -45 degrees"
'''},
            {"name": "the numerical and analytic step responses agree", "code": r'''
_R, _C, _vs = 1000.0, 1e-6, 5.0
_tau = _R * _C
_dt = _tau / 2000.0
_ys = step_euler(_vs, _R, _C, _dt, 6000)
assert len(_ys) == 6001, f"expected 6001 samples, got {len(_ys)}"
assert abs(_ys[0]) < 1e-15, f"it must start from 0 V, got {_ys[0]}"
_want = analytic_step(_vs, _R, _C, 3.0 * _tau)
assert abs(_want - 4.751064658160680) < 1e-9, \
    f"the closed form at 3 tau should be 4.7510647, got {_want}"
assert abs(_ys[-1] - _want) < 1e-3, \
    f"numerical {_ys[-1]:.6f} against analytic {_want:.6f} — these should agree closely"
'''},
            {"name": "the response settles at the supply", "code": r'''
_R, _C, _vs = 1000.0, 1e-6, 5.0
_tau = _R * _C
_ys = step_euler(_vs, _R, _C, _tau / 1000.0, 20000)
assert abs(_ys[-1] - _vs) < 1e-6, f"after 20 time constants it should be at {_vs} V, got {_ys[-1]}"
assert abs(analytic_step(_vs, _R, _C, 0.0)) < 1e-15, "the closed form must give 0 at t = 0"
'''},
            {"name": "SymPy confirms the closed form", "code": r'''
assert satisfies_ode(5.0, 1000.0, 1e-6) is True, \
    "substituting the closed form into the equation should leave exactly zero"
assert satisfies_ode(2.0, 4700.0, 2.2e-7) is True, \
    "it should hold for any values, not just the ones you tried first"
'''},
        ],
    },
}
