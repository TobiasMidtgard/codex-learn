"""EMAG520 — S-Parameters and Impedance Matching.

Authored to the same rules as CTRL510:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

All four sandboxes use the `smith` visualiser. Its reference plane is nailed to
Z0 = 50 ohm, its three controls are the load resistance (2 to 300 ohm), the load
reactance (-200 to +200 ohm) and a length of lossless line (0 to 0.5 wavelengths,
in steps of 0.005). It draws a full impedance chart -- constant-resistance circles
and constant-reactance arcs, both at 0.2, 0.5, 1, 2 and 5 -- and it labels none of
them; the only text the draw function writes is "centre = 50 ohm". Its readout is a
function of the load alone, not of the line length, and it prints the magnitude to
three decimals, the VSWR to two and the return loss to one. Every notice below was
checked against those facts.
"""

COURSE = {
    "id": "EMAG520",
    "title": "S-Parameters and Impedance Matching",
    "band": 5,
    "level": "Advanced",
    "prereqs": ["EMAG510"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◎",
    "summary": (
        "Above a few hundred megahertz you cannot measure a voltage at a terminal pair, "
        "so the impedance description of a network stops being usable and the scattering "
        "description takes over. This course builds the reflection coefficient from the "
        "travelling waves on a line, turns it into the scattering matrix, and then spends "
        "the rest of its time on the one problem the matrix exists to state: making a "
        "load look like the line that feeds it, and finding out what that costs in "
        "bandwidth."
    ),
    "outcomes": [
        "Compute the reflection coefficient, VSWR and return loss of a load, and move all three along a length of lossless line.",
        "Read and write a scattering matrix, and use reciprocity and unitarity to tell what a measured matrix cannot be.",
        "Design a quarter-wave transformer and a single-stub match, and verify each by construction rather than by chart-reading.",
        "Quantify the bandwidth of a match and show that it is bought with sections, not with cleverness.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that matches one load four ways and measures the bandwidth of each.",
    "reading": [
        "*Microwave Engineering*, Pozar — chapters 2, 4 and 5 are the whole of this course.",
        "*Foundations for Microwave Engineering*, Collin — for the multi-section transformer derived properly.",
        "Bode's and Fano's original papers, for the gain–bandwidth bound the last module only states.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Reflection, VSWR and the line as a rotation",
            "summary": "One number describes a load on a line. A length of that line moves the number in a circle and never shrinks it.",
            "concepts": [
                "A wave going forward and a wave coming back: the reflection coefficient is the ratio of the two at a chosen plane.",
                "$\\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$ is a bilinear map, so it takes the right half of the impedance plane onto the unit disc.",
                "VSWR is the envelope of the interference pattern, not a property of the load on its own.",
                "Return loss in dB is the same statement again, in the units a spectrum analyser prints.",
                "A lossless line multiplies $\\Gamma$ by $e^{-2j\\beta l}$: the phase changes, the magnitude never does.",
            ],
            "sandbox": {
                "title": "Where a load sits, and where a line takes it",
                "visualiser": "smith",
                "minutes": 8,
                "initial": {"rl": 100, "xl": 60, "len": 0},
                "brief": r'''
The chart is the unit disc of $\Gamma$, with the reference impedance fixed at 50 Ω.
The centre is $\Gamma = 0$; the rim is total reflection. The circles are constant
normalised resistance and constant normalised reactance.

The grey dot is the load itself. The dashed purple circle is the set of all points
with the same $|\Gamma|$. The bright dot is what you see after `line length`
wavelengths of lossless 50 Ω line, and it can only ever move along that dashed
circle.
''',
                "notice": [
                    "Set load R to 50 and load X to 0. Both dots collapse onto the centre and the dashed circle shrinks to nothing: $|\\Gamma| = 0$, VSWR 1:1. The centre is the only point at which a 50 Ω system has nothing to fix.",
                    "Set R = 100, X = 0, then walk line length from 0 to 0.5. The grey dot never moves, the bright dot goes round exactly once, and the readout holds at $|\\Gamma| = 0.333$, VSWR 2:1 the whole way. Half a wavelength of lossless line is one full turn and no improvement.",
                    "Stop at line length 0.25 with R = 100, X = 0. The bright dot is diametrically opposite the load, on the real axis at $\\Gamma = -1/3$, which reads as 25 Ω. A quarter wave has turned a 2:1 step up into a 2:1 step down.",
                    "Now set R = 50 and raise X to 200. The dot rides the $r = 1$ circle out towards the rim, and the readout reaches $|\\Gamma| = 0.894$, VSWR 17.94:1. A perfect resistance with a reactance on it is still a bad load.",
                ],
            },
            "derive": {
                "title": "From the load impedance to the standing wave",
                "minutes": 14,
                "vars": ["Z_L", "Z_0", "Gamma", "rho", "S", "V_0", "z", "beta", "l"],
                "brief": r'''
On a lossless line of characteristic impedance $Z_0$, with the load at $z = 0$ and
the generator at negative $z$, the total voltage and current are

$$V(z) = V_0\left(e^{-j\beta z} + \Gamma e^{+j\beta z}\right), \qquad
I(z) = \frac{V_0}{Z_0}\left(e^{-j\beta z} - \Gamma e^{+j\beta z}\right)$$

Everything in this module falls out of imposing one boundary condition on those two
lines, then taking magnitudes.

Write $\rho$ for $|\Gamma|$ and $S$ for the voltage standing-wave ratio.
''',
                "steps": [
                    {
                        "prompt": "At the load, $z = 0$, the ratio $V/I$ must be $Z_L$. Put $z = 0$ into both expressions and write $Z_L$ in terms of $Z_0$ and $\\Gamma$.",
                        "answer": "Z_0 \\frac{1 + \\Gamma}{1 - \\Gamma}",
                        "placeholder": "Z_0 \\frac{1 + \\Gamma}{1 - \\Gamma}",
                        "hint": "Every exponential becomes 1, so the voltage is $V_0(1+\\Gamma)$ and the current is $(V_0/Z_0)(1-\\Gamma)$.",
                        "deconstruct": [
                            "$V(0) = V_0(1 + \\Gamma)$ and $I(0) = (V_0/Z_0)(1 - \\Gamma)$.",
                            "Divide the first by the second; $V_0$ cancels and $Z_0$ comes up into the numerator.",
                        ],
                    },
                    {
                        "prompt": "Solve that for $\\Gamma$. Write it in terms of $Z_L$ and $Z_0$.",
                        "answer": "\\frac{Z_L - Z_0}{Z_L + Z_0}",
                        "placeholder": "\\frac{Z_L - Z_0}{Z_L + Z_0}",
                        "hint": "Cross-multiply, collect the two $\\Gamma$ terms on one side, and factor.",
                        "deconstruct": [
                            "$Z_L(1 - \\Gamma) = Z_0(1 + \\Gamma)$.",
                            "So $Z_L - Z_0 = \\Gamma(Z_L + Z_0)$, and one division finishes it.",
                        ],
                    },
                    {
                        "prompt": "Away from the load the two travelling waves interfere. Their magnitudes add where they are in phase and subtract where they are out of phase, so $|V|$ runs between $|V_0|(1+\\rho)$ and $|V_0|(1-\\rho)$. The standing-wave ratio is the ratio of those two. Write $S$ in terms of $\\rho$.",
                        "answer": "\\frac{1 + \\rho}{1 - \\rho}",
                        "placeholder": "\\frac{1 + \\rho}{1 - \\rho}",
                        "hint": "It is just maximum over minimum. $|V_0|$ divides out.",
                        "deconstruct": [
                            "$|V|_{\\max} = |V_0|(1 + \\rho)$ and $|V|_{\\min} = |V_0|(1 - \\rho)$.",
                            "The ratio is independent of how hard the generator is driving.",
                        ],
                    },
                    {
                        "prompt": "A slotted line measures $S$, not $\\rho$. Invert the last result and write $\\rho$ in terms of $S$.",
                        "answer": "\\frac{S - 1}{S + 1}",
                        "placeholder": "\\frac{S - 1}{S + 1}",
                        "hint": "The same algebra as step 2, with $S$ playing the part $Z_L/Z_0$ played there.",
                        "deconstruct": [
                            "$S(1 - \\rho) = 1 + \\rho$.",
                            "So $S - 1 = \\rho(S + 1)$.",
                        ],
                    },
                    {
                        "prompt": "A fraction $\\rho^2$ of the incident power is reflected, so a fraction $1 - \\rho^2$ reaches the load. Substitute the previous answer and write the delivered fraction in terms of $S$ alone.",
                        "answer": "\\frac{4S}{(S+1)^2}",
                        "placeholder": "\\frac{4S}{(S+1)^2}",
                        "hint": "$1 - \\rho^2 = (1-\\rho)(1+\\rho)$, and each bracket is easy once $\\rho = (S-1)/(S+1)$ is in place.",
                        "deconstruct": [
                            "$1 - \\rho = 2/(S+1)$ and $1 + \\rho = 2S/(S+1)$.",
                            "Multiplying the two gives $4S/(S+1)^2$.",
                        ],
                    },
                ],
                "closing": r'''
Check the last result against a number you already know: $S = 2$ gives $8/9$, so a
2:1 mismatch throws away a ninth of the incident power. That is $10\log_{10}(9/8)$,
or 0.51 dB — a shade *over* half a decibel, and small enough that 2:1 is tolerated
almost everywhere, which is why the *phase* of the
reflection — the thing $S$ has thrown away — is usually the part that hurts.
''',
            },
            "lab": {
                "title": "Reflection, VSWR and a length of line",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Four functions, all on a lossless 50 Ω system.

`gamma(zl, z0)` returns the complex reflection coefficient of a load.

`vswr(g)` returns the standing-wave ratio from a reflection coefficient. Return
`float("inf")` when $|\Gamma| \ge 1$, since the minimum of the envelope is zero.

`return_loss_db(g)` returns $-20\log_{10}|\Gamma|$, and `float("inf")` for a perfect
match.

`input_impedance(zl, z0, beta_l)` returns the impedance seen `beta_l` radians back
down the line from the load. Do **not** use the $\tan$ form of the line equation: it
is singular at a quarter wave, which is exactly the case you care about. Rotate the
reflection coefficient instead —

```text
g_in = gamma(zl, z0) * exp(-2j * beta_l)
z_in = z0 * (1 + g_in) / (1 - g_in)
```

— which is the same formula and has no singularity except at a genuine open circuit.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def gamma(zl, z0=50.0):
    """Voltage reflection coefficient of load `zl` on a line of impedance `z0`."""
    # TODO: the bilinear map from impedance to the unit disc.
    return 0j


def vswr(g):
    """Standing-wave ratio from a reflection coefficient; inf when |g| >= 1."""
    # TODO: maximum of the envelope over minimum.
    return 0.0


def return_loss_db(g):
    """How far below the incident wave the reflected one sits, in dB."""
    # TODO: inf when there is no reflection at all.
    return 0.0


def input_impedance(zl, z0, beta_l):
    """Impedance seen `beta_l` radians back down a lossless line from the load."""
    # TODO: rotate gamma, then map back to impedance.
    return 0j


if __name__ == "__main__":
    g = gamma(100.0, 50.0)
    print("gamma  =", g)
    print("VSWR   =", vswr(g))
    print("RL     =", return_loss_db(g), "dB")
    print("quarter-wave view of 100 ohm:", input_impedance(100.0, 50.0, np.pi / 2))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def gamma(zl, z0=50.0):
    """Voltage reflection coefficient of load `zl` on a line of impedance `z0`."""
    zl = complex(zl)
    return complex((zl - z0) / (zl + z0))


def vswr(g):
    """Standing-wave ratio from a reflection coefficient; inf when |g| >= 1."""
    m = abs(g)
    if m >= 1.0:
        return float("inf")
    return float((1.0 + m) / (1.0 - m))


def return_loss_db(g):
    """How far below the incident wave the reflected one sits, in dB."""
    m = abs(g)
    if m <= 0.0:
        return float("inf")
    return float(-20.0 * np.log10(m))


def input_impedance(zl, z0, beta_l):
    """Impedance seen `beta_l` radians back down a lossless line from the load."""
    g = gamma(zl, z0) * np.exp(-2j * beta_l)
    return complex(z0 * (1.0 + g) / (1.0 - g))


if __name__ == "__main__":
    g = gamma(100.0, 50.0)
    print("gamma  =", g)
    print("VSWR   =", vswr(g))
    print("RL     =", return_loss_db(g), "dB")
    print("quarter-wave view of 100 ohm:", input_impedance(100.0, 50.0, np.pi / 2))
'''}],
                "hints": [
                    "`complex(zl)` first, so an integer load does not silently do integer arithmetic.",
                    "`vswr` must depend on `abs(g)` only — a reflection coefficient of $-1/3$ and one of $+1/3$ produce the same standing wave.",
                    "`np.log10` of a magnitude, times $-20$. Guard the zero case before you take the logarithm.",
                    "In `input_impedance` the rotation is $e^{-2j\\beta l}$, not $e^{-j\\beta l}$: the wave travels the length twice.",
                ],
                "tests": [
                    {"name": "a two-to-one mismatch reflects a third of the wave", "code": r'''
_g = gamma(100.0, 50.0)
assert abs(_g - (1.0 / 3.0)) < 1e-12, \
    f"(100 - 50)/(100 + 50) is 1/3, got {_g}"
assert abs(gamma(50.0, 50.0)) < 1e-15, \
    "a load equal to the line impedance must reflect nothing at all"
'''},
                    {"name": "a short inverts the wave and an open returns it", "code": r'''
assert abs(gamma(0.0, 50.0) + 1.0) < 1e-12, \
    "a short circuit holds the voltage at zero, so the reflection is -1"
assert abs(gamma(1e12, 50.0) - 1.0) < 1e-6, \
    "an open circuit holds the current at zero, so the reflection is +1"
'''},
                    {"name": "a reactive load returns everything, rotated", "code": r'''
_g = gamma(30.0 + 40.0j, 50.0)
assert abs(_g - 0.5j) < 1e-12, \
    f"30 + j40 on a 50 ohm line gives exactly j0.5, got {_g}"
assert abs(abs(gamma(50.0j, 50.0)) - 1.0) < 1e-12, \
    "a pure reactance dissipates nothing, so it must reflect the whole wave"
'''},
                    {"name": "VSWR reads the magnitude and nothing else", "code": r'''
import math
assert abs(vswr(1.0 / 3.0) - 2.0) < 1e-12, \
    f"|Gamma| = 1/3 is a 2:1 standing wave, got {vswr(1.0 / 3.0)}"
assert abs(vswr(-1.0 / 3.0) - 2.0) < 1e-12, \
    "the envelope cannot know the sign of Gamma, only its size"
assert abs(vswr(0.0) - 1.0) < 1e-15, \
    "a matched line carries no standing wave, so the ratio is 1"
assert math.isinf(vswr(1.0)), \
    "total reflection drives the envelope minimum to zero, so VSWR is infinite"
'''},
                    {"name": "return loss is the same fact in decibels", "code": r'''
import math
assert abs(return_loss_db(1.0 / 3.0) - 9.542425094393248) < 1e-9, \
    f"-20*log10(1/3) is 9.5424 dB, got {return_loss_db(1.0 / 3.0)}"
assert abs(return_loss_db(0.1) - 20.0) < 1e-9, \
    "|Gamma| = 0.1 is exactly 20 dB return loss"
assert math.isinf(return_loss_db(0.0)), \
    "nothing comes back from a perfect match, so the return loss is unbounded"
'''},
                    {"name": "a quarter wave inverts the load about Z0", "code": r'''
import numpy as np
_z = input_impedance(100.0, 50.0, np.pi / 2)
assert abs(_z - 25.0) < 1e-9, \
    f"Z0^2/ZL = 2500/100 = 25 ohm, got {_z}"
_z = input_impedance(200.0, 50.0, np.pi / 2)
assert abs(_z - 12.5) < 1e-9, \
    f"Z0^2/ZL = 2500/200 = 12.5 ohm, got {_z}"
'''},
                    {"name": "an eighth-wave shorted stub is a pure inductance", "code": r'''
import numpy as np
_z = input_impedance(0.0, 50.0, 2.0 * np.pi * 0.125)
assert abs(_z - 50.0j) < 1e-9, \
    f"an eighth wave of shorted 50 ohm line is +j50, got {_z}"
_z = input_impedance(30.0 + 40.0j, 50.0, np.pi)
assert abs(_z - (30.0 + 40.0j)) < 1e-9, \
    f"half a wavelength returns the load unchanged, got {_z}"
'''},
                    {"name": "line length moves the mismatch and never shrinks it", "code": r'''
_zl = 30.0 + 40.0j
_ref = abs(gamma(_zl, 50.0))
assert abs(_ref - 0.5) < 1e-12, \
    f"check gamma first: 30 + j40 gives |Gamma| = 0.5, got {_ref}"
for _bl in (0.3, 1.1, 2.7, 4.0):
    _m = abs(gamma(input_impedance(_zl, 50.0, _bl), 50.0))
    assert abs(_m - _ref) < 1e-9, \
        f"a lossless line cannot change |Gamma|: got {_m} after beta*l = {_bl}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "The scattering matrix",
            "summary": "At microwave frequencies you can measure a travelling wave and not a terminal voltage. The matrix that relates the waves is the one instruments actually report.",
            "concepts": [
                "Incident and reflected wave amplitudes $a_i$, $b_i$, and $b = Sa$ as the definition.",
                "$S_{ij}$ is measured with every other port terminated in $Z_0$ — the terminations are part of the definition, not an experimental convenience.",
                "Reciprocity makes $S$ symmetric; a ferrite or an active device breaks it.",
                "Losslessness makes $S$ unitary, so $S^\\dagger S = I$ — a constraint that rules out most matrices someone hands you.",
                "$\\Gamma_{in} = S_{11} + S_{12}S_{21}\\Gamma_L/(1 - S_{22}\\Gamma_L)$: what a mismatched load does to the input.",
            ],
            "sandbox": {
                "title": "S11 of a one-port, read three ways",
                "visualiser": "smith",
                "minutes": 7,
                "initial": {"rl": 25, "xl": 0, "len": 0},
                "brief": r'''
A one-port has a one-by-one scattering matrix, and its single entry is the
reflection coefficient of the previous module. So the chart *is* a plot of $S_{11}$,
and the readout underneath is the three ways an instrument would report the same
complex number: magnitude, VSWR, and return loss in dB.

Leave the line length at zero for this one and move only the load.
''',
                "notice": [
                    "R = 25, X = 0 puts the dot on the real axis at $\\Gamma = -1/3$. Change R to 100 and it jumps to $+1/3$, the opposite side of the centre on the same circle. Both read $|S_{11}| = 0.333$, VSWR 2:1, return loss 9.5 dB — halving and doubling the resistance cost identical reflected power.",
                    "Drag R down to its minimum of 2 Ω with X = 0. The dot sits almost on the rim: $|S_{11}| = 0.923$, VSWR 25:1, return loss 0.7 dB. Eighty-five per cent of the incident power comes straight back out of the port.",
                    "Set R = 50 and X = 1 — a perfect resistor with one ohm of stray reactance on it. The dot is barely off centre and the return loss reads 40 dB. That is a good connector; 20 dB is a mediocre one, and the difference is nine ohms of reactance.",
                ],
            },
            "derive": {
                "title": "What a mismatched load does to the input",
                "minutes": 14,
                "vars": ["S_11", "S_12", "S_21", "S_22", "Gamma_L", "Gamma_in",
                         "a_1", "a_2", "b_1", "b_2", "rho"],
                "brief": r'''
A two-port is defined by

$$b_1 = S_{11}a_1 + S_{12}a_2, \qquad b_2 = S_{21}a_1 + S_{22}a_2$$

Terminate port 2 in a load whose reflection coefficient is $\Gamma_L$. The wave
$b_2$ leaves the two-port, hits the load, and comes back as $a_2$.

Find $\Gamma_{in} = b_1/a_1$.
''',
                "steps": [
                    {
                        "prompt": "The load reflects whatever arrives at it. Write $a_2$ in terms of $\\Gamma_L$ and $b_2$.",
                        "answer": "\\Gamma_L b_2",
                        "placeholder": "\\Gamma_L b_2",
                        "hint": "From the two-port's point of view $b_2$ is outgoing and $a_2$ is incoming; the load turns one into the other.",
                        "deconstruct": [
                            "A reflection coefficient is by definition reflected over incident, at the plane where it is quoted.",
                            "At the load plane the incident wave is $b_2$ and the reflected one is $a_2$.",
                        ],
                    },
                    {
                        "prompt": "Substitute that into the equation for $b_2$ and solve for $b_2$ in terms of $a_1$.",
                        "given": "Start from $b_2 = S_{21}a_1 + S_{22}a_2$.",
                        "answer": "\\frac{S_21 a_1}{1 - S_22 \\Gamma_L}",
                        "placeholder": "\\frac{S_21 a_1}{1 - S_22 \\Gamma_L}",
                        "hint": "$b_2$ appears on both sides once you substitute; collect it.",
                        "deconstruct": [
                            "$b_2 = S_{21}a_1 + S_{22}\\Gamma_L b_2$.",
                            "So $b_2(1 - S_{22}\\Gamma_L) = S_{21}a_1$.",
                        ],
                    },
                    {
                        "prompt": "Now put $a_2 = \\Gamma_L b_2$ into the equation for $b_1$ and divide by $a_1$. Write $\\Gamma_{in}$.",
                        "answer": "S_11 + \\frac{S_12 S_21 \\Gamma_L}{1 - S_22 \\Gamma_L}",
                        "placeholder": "S_11 + \\frac{S_12 S_21 \\Gamma_L}{1 - S_22 \\Gamma_L}",
                        "hint": "$b_1 = S_{11}a_1 + S_{12}\\Gamma_L b_2$, and you already have $b_2$ in terms of $a_1$.",
                        "deconstruct": [
                            "Substituting gives $b_1 = S_{11}a_1 + S_{12}\\Gamma_L S_{21}a_1/(1 - S_{22}\\Gamma_L)$.",
                            "Dividing through by $a_1$ leaves no wave amplitudes at all.",
                        ],
                    },
                    {
                        "prompt": "Put a short circuit on port 2, so $\\Gamma_L = -1$. Write $\\Gamma_{in}$ for that case.",
                        "answer": "S_11 - \\frac{S_12 S_21}{1 + S_22}",
                        "placeholder": "S_11 - \\frac{S_12 S_21}{1 + S_22}",
                        "hint": "Substitute $-1$ everywhere $\\Gamma_L$ appears, and watch the sign in the denominator.",
                        "deconstruct": [
                            "The numerator picks up the factor $-1$.",
                            "The denominator becomes $1 - S_{22}(-1) = 1 + S_{22}$.",
                        ],
                    },
                    {
                        "prompt": "Now suppose the two-port is lossless and reciprocal, and write $\\rho$ for $|S_{11}|$. Unitarity says the two columns have unit length. Write $|S_{21}|^2$ in terms of $\\rho$.",
                        "answer": "1 - \\rho^2",
                        "placeholder": "1 - \\rho^2",
                        "hint": "Whatever fraction of the incident power does not come back must leave by the other port.",
                        "deconstruct": [
                            "The first column of $S^\\dagger S = I$ gives $|S_{11}|^2 + |S_{21}|^2 = 1$.",
                            "So $|S_{21}|^2 = 1 - \\rho^2$.",
                        ],
                    },
                ],
                "closing": r'''
The last two results are worth holding together. $S_{11}$ alone tells you the input
reflection *only* when port 2 is terminated in $Z_0$; the moment a real load is on
the output, the whole matrix is involved. And a lossless two-port cannot be made
better at transmitting without being made better at not reflecting — there is only
one unit of power, and unitarity spends it.
''',
            },
            "lab": {
                "title": "Build and interrogate scattering matrices",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Five short functions.

`s_series(z, z0)` returns the 2×2 matrix of a series impedance `z` bridging two
lines of impedance `z0`:

```text
S11 = S22 = z / (z + 2*z0)        S21 = S12 = 2*z0 / (z + 2*z0)
```

`s_shunt(y, z0)` does the same for a shunt admittance `y` across the line:

```text
S11 = S22 = -y*z0 / (y*z0 + 2)    S21 = S12 = 2 / (y*z0 + 2)
```

`is_reciprocal(S, tol)` returns whether $S$ equals its own transpose.

`is_lossless(S, tol)` returns whether $S^\dagger S = I$. In NumPy, `S.conj().T @ S`.

`gamma_in(S, gl)` returns the input reflection coefficient with a load `gl` on
port 2 — the expression you derived.

Return the matrices as complex NumPy arrays and the predicates as plain `bool`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def s_series(z, z0=50.0):
    """S-matrix of a series impedance bridging two lines of impedance z0."""
    # TODO: two distinct entries, placed symmetrically.
    return np.zeros((2, 2), dtype=complex)


def s_shunt(y, z0=50.0):
    """S-matrix of a shunt admittance across a line of impedance z0."""
    # TODO: same shape, opposite sign on the reflection.
    return np.zeros((2, 2), dtype=complex)


def is_reciprocal(S, tol=1e-9):
    """True when S is its own transpose."""
    # TODO
    return False


def is_lossless(S, tol=1e-9):
    """True when S is unitary, so no power is absorbed."""
    # TODO
    return False


def gamma_in(S, gl):
    """Input reflection coefficient with a load of reflection gl on port 2."""
    # TODO: S11 plus what leaks back through S12 and S21.
    return 0j


if __name__ == "__main__":
    S = s_series(50.0j, 50.0)
    print("S =", np.round(S, 4).tolist())
    print("reciprocal:", is_reciprocal(S), " lossless:", is_lossless(S))
    print("gamma_in with a shorted output:", gamma_in(S, -1.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def s_series(z, z0=50.0):
    """S-matrix of a series impedance bridging two lines of impedance z0."""
    z = complex(z)
    den = z + 2.0 * z0
    s11 = z / den
    s21 = 2.0 * z0 / den
    return np.array([[s11, s21], [s21, s11]], dtype=complex)


def s_shunt(y, z0=50.0):
    """S-matrix of a shunt admittance across a line of impedance z0."""
    y = complex(y)
    den = y * z0 + 2.0
    s11 = -y * z0 / den
    s21 = 2.0 / den
    return np.array([[s11, s21], [s21, s11]], dtype=complex)


def is_reciprocal(S, tol=1e-9):
    """True when S is its own transpose."""
    S = np.asarray(S, dtype=complex)
    return bool(np.max(np.abs(S - S.T)) <= tol)


def is_lossless(S, tol=1e-9):
    """True when S is unitary, so no power is absorbed."""
    S = np.asarray(S, dtype=complex)
    n = S.shape[0]
    return bool(np.max(np.abs(S.conj().T @ S - np.eye(n))) <= tol)


def gamma_in(S, gl):
    """Input reflection coefficient with a load of reflection gl on port 2."""
    S = np.asarray(S, dtype=complex)
    return complex(S[0, 0] + S[0, 1] * S[1, 0] * gl / (1.0 - S[1, 1] * gl))


if __name__ == "__main__":
    S = s_series(50.0j, 50.0)
    print("S =", np.round(S, 4).tolist())
    print("reciprocal:", is_reciprocal(S), " lossless:", is_lossless(S))
    print("gamma_in with a shorted output:", gamma_in(S, -1.0))
'''}],
                "hints": [
                    "Both matrices are symmetric with only two distinct numbers in them, so compute the two and place them.",
                    "`np.max(np.abs(...))` reduces a matrix difference to one number you can compare against `tol`.",
                    "Unitary means $S^\\dagger S = I$ — conjugate *and* transpose, so `S.conj().T`, not `S.T`.",
                    "`gamma_in` is a single expression; the only trap is the sign in the denominator, which is $1 - S_{22}\\Gamma_L$.",
                ],
                "tests": [
                    {"name": "no series element is a through connection", "code": r'''
_S = s_series(0.0, 50.0)
assert _S.shape == (2, 2), f"a two-port has a 2x2 matrix, got {_S.shape}"
assert abs(_S[0, 0]) < 1e-12, \
    "with nothing in the way there is nothing to reflect, so S11 must be 0"
assert abs(_S[1, 0] - 1.0) < 1e-12, \
    f"a through connection passes the wave untouched, so S21 must be 1, got {_S[1, 0]}"
_B = s_series(1e9, 50.0)
assert abs(_B[0, 0] - 1.0) < 1e-6, \
    f"a huge series impedance is an open circuit, so S11 must approach +1, got {_B[0, 0]}"
assert abs(_B[1, 0]) < 1e-6, \
    f"and nothing crosses an open circuit, so S21 must approach 0, got {_B[1, 0]}"
'''},
                    {"name": "a 50 ohm series resistor splits the wave two ways", "code": r'''
_S = s_series(50.0, 50.0)
assert abs(_S[0, 0] - 1.0 / 3.0) < 1e-12, \
    f"S11 = z/(z + 2*z0) = 50/150, got {_S[0, 0]}"
assert abs(_S[1, 0] - 2.0 / 3.0) < 1e-12, \
    f"S21 = 2*z0/(z + 2*z0) = 100/150, got {_S[1, 0]}"
'''},
                    {"name": "a shunt element reflects with the opposite sign", "code": r'''
_S = s_shunt(1.0 / 50.0, 50.0)
assert abs(_S[0, 0] + 1.0 / 3.0) < 1e-12, \
    f"a shunt 50 ohm pulls the node down, so S11 is -1/3 and not +1/3; got {_S[0, 0]}"
assert abs(_S[1, 0] - 2.0 / 3.0) < 1e-12, \
    f"S21 = 2/(y*z0 + 2) = 2/3, got {_S[1, 0]}"
_S = s_shunt(0.0, 50.0)
assert abs(_S[1, 0] - 1.0) < 1e-12, \
    "an admittance of zero is not there at all, so the port must be a through path"
'''},
                    {"name": "reciprocity and losslessness are different questions", "code": r'''
_r = s_series(50.0, 50.0)
_x = s_series(50.0j, 50.0)
assert is_reciprocal(_r), \
    "a passive series element is reciprocal whatever it dissipates"
assert is_reciprocal(_x), \
    "a reactance is reciprocal too — reciprocity is about symmetry, not about loss"
assert not is_lossless(_r), \
    "a 50 ohm series resistor absorbs 4/9 of the incident power, so S cannot be unitary"
assert is_lossless(_x), \
    "a pure reactance dissipates nothing, so |S11|^2 + |S21|^2 must come to exactly 1"
'''},
                    {"name": "a gyrator is lossless without being reciprocal", "code": r'''
import numpy as np
_G = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
assert is_lossless(_G), \
    "the gyrator's matrix is unitary, so it loses no power at all"
assert not is_reciprocal(_G), \
    "S12 = +1 while S21 = -1, so the matrix is not symmetric and the device is not reciprocal"
'''},
                    {"name": "the load reaches back through the two-port", "code": r'''
import numpy as np
_T = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
assert abs(gamma_in(_T, 0.5) - 0.5) < 1e-12, \
    f"a through connection shows the load's own reflection unchanged, got {gamma_in(_T, 0.5)}"
_X = s_series(50.0j, 50.0)
assert abs(gamma_in(_X, -1.0) - 1.0j) < 1e-12, \
    f"a shorted j50 series element is just j50 on a 50 ohm line, so Gamma = +j; got {gamma_in(_X, -1.0)}"
'''},
                    {"name": "S11 is the input reflection only when port 2 is matched", "code": r'''
_X = s_series(50.0j, 50.0)
assert abs(gamma_in(_X, 0.0) - _X[0, 0]) < 1e-12, \
    "with Gamma_L = 0 the correction term vanishes and Gamma_in collapses to S11"
assert abs(gamma_in(_X, 0.5) - _X[0, 0]) > 0.1, \
    "with a mismatched load it must not: the load leaks back through S12*S21"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Quarter-wave transformers and stub matching",
            "summary": "Two ways to move a load to the centre of the chart: change the line's impedance, or add a reactance at the right place.",
            "concepts": [
                "The quarter-wave transformer $Z_1 = \\sqrt{Z_0 Z_L}$, and why it only works for a real load.",
                "A line section is an impedance inverter at a quarter wave: $Z_{in} = Z_1^2/Z_L$.",
                "Single-stub matching in two moves — a length of line to fix the real part, a reactance to cancel the rest.",
                "A shorted stub of length $l$ presents a pure reactance, and its length is the design variable.",
                "The double-stub tuner, and the forbidden region it pays for having its spacing fixed.",
            ],
            "sandbox": {
                "title": "Rotating onto the unity-resistance circle",
                "visualiser": "smith",
                "minutes": 9,
                "initial": {"rl": 95, "xl": 0, "len": 0},
                "brief": r'''
Single-stub matching is two moves. First a length of line rotates the load until its
*resistance* is right; then one reactance cancels what is left.

This is an impedance chart, so it shows the series form of that construction
directly: rotate until the bright dot lands on the constant-resistance circle for
$r = 1$ — nothing here is labelled, so find it as the one interior circle that
passes through the centre — and the impedance there is $50 + jX$ for some $X$ you
then cancel.
''',
                "notice": [
                    "Leave R = 95, X = 0 and raise line length to 0.100. The bright dot lands on the $r = 1$ circle. The readout is unchanged — $|\\Gamma| = 0.310$, VSWR 1.90:1 — but the impedance at that plane is $50 - j33\\ \\Omega$. The line fixed the resistance and could not touch the mismatch.",
                    "That residual normalised reactance is $-0.653$. Its magnitude is what the closed form $x = (S-1)/\\sqrt{S}$ predicts from the VSWR of 1.90 in the readout: $0.9/1.378 = 0.653$. Rotating clockwise simply reaches the negative-reactance crossing first; the other one is at length 0.400.",
                    "Set R = 200, X = 0, line length 0.25. The dot lands at 12.5 Ω — the quarter-wave inverse of 200 Ω through a 50 Ω line. A quarter-wave *transformer* is the same rotation performed on a line of $\\sqrt{50 \\times 200} = 100\\ \\Omega$, which this chart cannot draw: its centre is nailed to 50 Ω.",
                    "Push the load to R = 2, X = 0 — a 25:1 mismatch — and raise the length to 0.220. The dot has crawled round near the rim and just crossed $r = 1$, at about $55 + j251\\ \\Omega$. The closed form says $(S-1)/\\sqrt{S} = 24/5 = 4.8$, or 240 Ω. A severe mismatch does not need a long line; it needs an enormous cancelling reactance.",
                ],
            },
            "derive": {
                "title": "The transformer and the stub",
                "minutes": 16,
                "vars": ["Z_0", "Z_1", "Z_L", "Z_in", "rho", "S", "x", "R_L", "beta", "l"],
                "brief": r'''
The input impedance of a lossless line of length $l$ terminated in $Z_L$ is

$$Z_{in} = Z_1\,\frac{Z_L + jZ_1\tan\beta l}{Z_1 + jZ_L\tan\beta l}$$

where $Z_1$ is the characteristic impedance of that section. Everything in this
module comes from two special cases of it: $\beta l = \pi/2$, and the point at which
the normalised resistance has become 1.
''',
                "steps": [
                    {
                        "prompt": "At $\\beta l = \\pi/2$ the tangent runs to infinity. Divide numerator and denominator by $\\tan\\beta l$ and take the limit. Write $Z_{in}$ in terms of $Z_1$ and $Z_L$.",
                        "answer": "\\frac{Z_1^2}{Z_L}",
                        "placeholder": "\\frac{Z_1^{2}}{Z_L}",
                        "hint": "After dividing, the surviving terms are $jZ_1$ on top and $jZ_L$ underneath.",
                        "deconstruct": [
                            "Dividing gives $Z_1(Z_L/\\tan\\beta l + jZ_1)/(Z_1/\\tan\\beta l + jZ_L)$.",
                            "As the tangent grows without bound the two fractions vanish and the $j$ cancels.",
                        ],
                    },
                    {
                        "prompt": "You want that quarter-wave section to make a real load $Z_L$ look like $Z_0$. Set $Z_{in} = Z_0$ and write the section impedance $Z_1$.",
                        "answer": "\\sqrt{Z_0 Z_L}",
                        "placeholder": "\\sqrt{Z_0 Z_L}",
                        "hint": "One line of algebra from the previous answer; the square root is the point of the whole device.",
                        "deconstruct": [
                            "$Z_1^2/Z_L = Z_0$, so $Z_1^2 = Z_0 Z_L$.",
                            "The section impedance is the geometric mean of the two it joins.",
                        ],
                    },
                    {
                        "prompt": "A 200 Ω antenna is to be fed from a 50 Ω line. Write the characteristic impedance of the quarter-wave section, in ohms.",
                        "answer": "100",
                        "placeholder": "100",
                        "hint": "Put the numbers into the previous answer.",
                        "deconstruct": [
                            "$\\sqrt{50 \\times 200} = \\sqrt{10000}$.",
                            "Note that it is the geometric mean, 100 Ω, and not the arithmetic mean, 125 Ω.",
                        ],
                    },
                    {
                        "prompt": "Now the stub. A length of line rotates $\\Gamma$ without changing $\\rho = |\\Gamma|$; stop where the normalised impedance is $z = 1 + jx$. There $\\Gamma = jx/(2 + jx)$, so $\\rho^2 = x^2/(4 + x^2)$. Solve for $x$ and take the positive root.",
                        "answer": "\\frac{2\\rho}{\\sqrt{1 - \\rho^2}}",
                        "placeholder": "\\frac{2\\rho}{\\sqrt{1 - \\rho^{2}}}",
                        "hint": "Cross-multiply first: $\\rho^2(4 + x^2) = x^2$, then collect the $x^2$ terms.",
                        "deconstruct": [
                            "$4\\rho^2 = x^2(1 - \\rho^2)$.",
                            "So $x^2 = 4\\rho^2/(1-\\rho^2)$, and the square root of that is the answer.",
                        ],
                    },
                    {
                        "prompt": "A slotted line gives you $S$, not $\\rho$. Substitute $\\rho = (S-1)/(S+1)$ into the last answer and simplify. Write $x$ in terms of $S$.",
                        "answer": "\\frac{S - 1}{\\sqrt{S}}",
                        "placeholder": "\\frac{S - 1}{\\sqrt{S}}",
                        "hint": "$1 - \\rho^2$ collapses to $4S/(S+1)^2$, which you derived in module 1.",
                        "deconstruct": [
                            "$\\sqrt{1 - \\rho^2} = 2\\sqrt{S}/(S+1)$.",
                            "So $x = \\frac{2(S-1)}{S+1} \\cdot \\frac{S+1}{2\\sqrt{S}}$, and the $(S+1)$ factors cancel.",
                        ],
                    },
                ],
                "closing": r'''
The last result is the whole stub design in one line: measure the standing-wave
ratio, and the reactance you must cancel is $(S-1)/\sqrt{S}$ in normalised units.
For $S = 1.9$ that is $0.653$ — the number the sandbox showed you before any of this
was derived.

The stub design that follows in the lab is the shunt version of the same argument,
carried out in admittance because a shunt element adds susceptances.
''',
            },
            "lab": {
                "title": "Design a quarter-wave transformer and a single-stub match",
                "runtime": "python",
                "minutes": 38,
                "brief": r'''
Five functions. Everything is on a lossless system and all lengths are in
wavelengths.

`quarter_wave_z(z0, rl)` returns the section impedance for a real load.

`load_gamma(zl, z0)` is module 1's reflection coefficient again.

`single_stub(zl, z0)` returns `(d, b)`: the distance from the load to the stub, and
the **normalised susceptance** a shunt stub must add there. Method:

1. Let $\rho = |\Gamma_L|$ and $\theta = \arg\Gamma_L$.
2. The normalised admittance has unit real part exactly where $\mathrm{Re}\,\Gamma = -\rho^2$,
   which is at the two angles $\phi = \pm\arccos(-\rho)$.
3. Rotating by $d$ wavelengths takes $\Gamma$ to $\Gamma e^{-4\pi jd}$, so
   $d = ((\theta - \phi)/4\pi) \bmod 0.5$. Take the smaller of the two.
4. At that plane $y = (1 - \Gamma)/(1 + \Gamma)$, and the stub must supply
   `b = -y.imag`.

`short_stub_length(b)` returns the length of a short-circuited stub that presents
susceptance `b`. A shorted stub has $y = -j\cot(2\pi l)$, so `atan2(-1, b)/(2*pi)`
taken modulo 0.5 is the answer.

`matched_gamma(zl, z0, d, b)` rotates the load by `d`, adds `1j*b` in parallel, and
returns the resulting reflection coefficient — which should be zero when the design
is right, and is the only honest way to check the other functions.

A matched load is the degenerate case: return `(0.0, 0.0)` from `single_stub`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def quarter_wave_z(z0, rl):
    """Characteristic impedance of a quarter-wave section joining z0 to a real rl."""
    # TODO: the geometric mean.
    return 0.0


def load_gamma(zl, z0):
    """Reflection coefficient of zl on a line of impedance z0."""
    # TODO
    return 0j


def single_stub(zl, z0):
    """Return (d, b): stub distance in wavelengths, and the susceptance it adds."""
    # TODO: rotate to unit conductance, then read off what is left over.
    return (0.0, 0.0)


def short_stub_length(b):
    """Length in wavelengths of a shorted stub presenting susceptance b."""
    # TODO: invert y = -j*cot(2*pi*l).
    return 0.0


def matched_gamma(zl, z0, d, b):
    """Reflection coefficient after d wavelengths of line and a shunt jb."""
    # TODO: rotate, convert to admittance, add jb, convert back.
    return 0j


if __name__ == "__main__":
    print("quarter-wave section for 200 ohm:", quarter_wave_z(50.0, 200.0))
    d, b = single_stub(100.0, 50.0)
    print("stub at d =", round(d, 6), "wavelengths, needs b =", round(b, 6))
    print("shorted stub length:", round(short_stub_length(b), 6))
    print("residual |Gamma|:", abs(matched_gamma(100.0, 50.0, d, b)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def quarter_wave_z(z0, rl):
    """Characteristic impedance of a quarter-wave section joining z0 to a real rl."""
    return float(np.sqrt(z0 * rl))


def load_gamma(zl, z0):
    """Reflection coefficient of zl on a line of impedance z0."""
    zl = complex(zl)
    return complex((zl - z0) / (zl + z0))


def single_stub(zl, z0):
    """Return (d, b): stub distance in wavelengths, and the susceptance it adds."""
    g = load_gamma(zl, z0)
    rho = abs(g)
    if rho < 1e-14:
        return (0.0, 0.0)
    theta = float(np.angle(g))
    phi = float(np.arccos(-rho))
    cands = sorted(((theta - p) / (4.0 * np.pi)) % 0.5 for p in (phi, -phi))
    d = float(cands[0])
    gd = g * np.exp(-4j * np.pi * d)
    y = (1.0 - gd) / (1.0 + gd)
    return (d, float(-y.imag))


def short_stub_length(b):
    """Length in wavelengths of a shorted stub presenting susceptance b."""
    return float((np.arctan2(-1.0, b) / (2.0 * np.pi)) % 0.5)


def matched_gamma(zl, z0, d, b):
    """Reflection coefficient after d wavelengths of line and a shunt jb."""
    g = load_gamma(zl, z0) * np.exp(-4j * np.pi * d)
    y = (1.0 - g) / (1.0 + g) + 1j * b
    return complex((1.0 - y) / (1.0 + y))


if __name__ == "__main__":
    print("quarter-wave section for 200 ohm:", quarter_wave_z(50.0, 200.0))
    d, b = single_stub(100.0, 50.0)
    print("stub at d =", round(d, 6), "wavelengths, needs b =", round(b, 6))
    print("shorted stub length:", round(short_stub_length(b), 6))
    print("residual |Gamma|:", abs(matched_gamma(100.0, 50.0, d, b)))
'''}],
                "hints": [
                    "`np.angle` gives $\\theta$ in $(-\\pi, \\pi]$, which is what the modulo arithmetic expects.",
                    "Python's `%` on a negative float already returns a non-negative result, so `x % 0.5` needs no extra correction.",
                    "Two candidate distances come out of $\\pm\\arccos(-\\rho)$; the design wants the nearer stub, so sort and take the first.",
                    "Do not try to verify the match by eye. `matched_gamma` is the check, and it should return something of order $10^{-16}$.",
                ],
                "tests": [
                    {"name": "the transformer section is a geometric mean", "code": r'''
assert abs(quarter_wave_z(50.0, 100.0) - 70.71067811865476) < 1e-9, \
    f"sqrt(50*100) is 70.71 ohm, got {quarter_wave_z(50.0, 100.0)}"
assert abs(quarter_wave_z(50.0, 200.0) - 100.0) < 1e-9, \
    f"sqrt(50*200) is 100 ohm, not the arithmetic mean 125; got {quarter_wave_z(50.0, 200.0)}"
assert abs(quarter_wave_z(50.0, 50.0) - 50.0) < 1e-9, \
    "a load already equal to the line needs a section of the same impedance"
'''},
                    {"name": "the classic 100 ohm stub design", "code": r'''
_d, _b = single_stub(100.0, 50.0)
assert abs(_d - 0.1520433619923482) < 1e-6, \
    f"the textbook answer for a 100 ohm load is d = 0.15204 wavelengths, got {_d}"
assert abs(_b + 0.7071067811865476) < 1e-6, \
    f"at that plane y = 1 + j0.7071, so the stub must add -0.7071; got {_b}"
'''},
                    {"name": "the stub actually completes the match", "code": r'''
for _zl in (100.0, 25.0, 30.0 + 40.0j, 25.0 - 60.0j, 200.0 - 30.0j):
    _d, _b = single_stub(_zl, 50.0)
    assert 0.0 <= _d < 0.5, \
        f"the stub distance belongs in [0, 0.5) wavelengths, got {_d} for {_zl}"
    _res = abs(matched_gamma(_zl, 50.0, _d, _b))
    assert _res < 1e-9, \
        f"{_zl} should be matched exactly, but |Gamma| came out {_res}"
    _spoilt = abs(matched_gamma(_zl, 50.0, _d, _b + 0.4))
    assert _spoilt > 0.15, \
        f"check matched_gamma: a susceptance 0.4 out must spoil the match, got {_spoilt}"
'''},
                    {"name": "a shorted stub of that length gives that susceptance", "code": r'''
import numpy as np
assert abs(short_stub_length(1.0) - 0.375) < 1e-12, \
    f"y = -j*cot(2*pi*l), so b = +1 needs 0.375 wavelengths, got {short_stub_length(1.0)}"
assert abs(short_stub_length(-1.0) - 0.125) < 1e-12, \
    f"b = -1 needs 0.125 wavelengths, got {short_stub_length(-1.0)}"
for _b in (0.65, -2.3, 1.0, -0.7071067811865476):
    _l = short_stub_length(_b)
    assert 0.0 <= _l < 0.5, f"a stub length belongs in [0, 0.5), got {_l}"
    _y = -1.0 / np.tan(2.0 * np.pi * _l)
    assert abs(_y - _b) < 1e-9, \
        f"a shorted stub {_l} long presents b = {_y}, not the {_b} that was asked for"
'''},
                    {"name": "a matched load asks for nothing", "code": r'''
_d, _b = single_stub(50.0, 50.0)
assert abs(_b) < 1e-9, \
    f"there is no susceptance to cancel on a matched load, got {_b}"
assert abs(matched_gamma(50.0, 50.0, _d, _b)) < 1e-12, \
    "a matched load with no stub is still matched"
assert abs(load_gamma(100.0, 50.0) - 1.0 / 3.0) < 1e-12, \
    f"check load_gamma: 100 ohm on a 50 ohm line reflects 1/3, got {load_gamma(100.0, 50.0)}"
_d, _b = single_stub(25.0, 50.0)
assert abs(_d - 0.09795663800765181) < 1e-9, \
    f"25 ohm wants the stub 0.097957 wavelengths out, got {_d}"
assert abs(_b - 0.7071067811865476) < 1e-9, \
    f"25 ohm mirrors the 100 ohm case, so the stub must add +0.7071 there, got {_b}"
'''},
                    {"name": "a complex load, designed end to end", "code": r'''
import numpy as np
_zl = 25.0 - 60.0j
_d, _b = single_stub(_zl, 50.0)
_l = short_stub_length(_b)
assert abs(_d - 0.08143106936382863) < 1e-6, \
    f"expected the stub 0.081431 wavelengths from the load, got {_d}"
assert abs(_l - 0.07928616762051444) < 1e-6, \
    f"expected a shorted stub 0.079286 wavelengths long, got {_l}"
_physical_b = -1.0 / np.tan(2.0 * np.pi * _l)
assert abs(matched_gamma(_zl, 50.0, _d, _physical_b)) < 1e-7, \
    "the physical stub must do exactly the job the ideal susceptance did"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Bandwidth, and the price of a match",
            "summary": "Every match is exact at one frequency. How far either side it survives is decided before you start.",
            "concepts": [
                "A match is a null in $|\\Gamma(f)|$, and the question is only how sharp the null is.",
                "The node $Q$ of a two-element match is $\\sqrt{R_L/R_0 - 1}$, and the fractional bandwidth is about $1/Q$.",
                "A quarter-wave transformer is a single-section match with a bandwidth that falls as the impedance step grows.",
                "Multi-section transformers: binomial for a maximally flat response, Chebyshev for equal ripple across a wider band.",
                "The Bode–Fano limit: the integral of $\\ln(1/|\\Gamma|)$ over all frequency is bounded by the load's own $RC$, so bandwidth is a budget and not an engineering choice.",
            ],
            "sandbox": {
                "title": "Sweeping length is sweeping frequency",
                "visualiser": "smith",
                "minutes": 8,
                "initial": {"rl": 200, "xl": 0, "len": 0},
                "brief": r'''
A piece of line has a fixed physical length, so it is a different fraction of a
wavelength at every frequency. Reading the `line length` slider as a frequency sweep
is therefore literally correct, and it makes the central fact of this module visible:
a line changes the *phase* of a mismatch across the band and never its size.

Anything that actually narrows a band has to come from the elements you add.
''',
                "notice": [
                    "R = 200, X = 0 reads $|\\Gamma| = 0.6$, VSWR 4:1. Change R to 75 and it reads $|\\Gamma| = 0.2$, VSWR 1.5:1. The first load reflects nine times the power of the second, and it is that ratio, not the ohms, that the matching network has to buy its way out of.",
                    "Leave R = 200 and sweep line length across the whole slider. The bright dot makes exactly one circuit at constant radius, since the rotation angle is $4\\pi$ times the length in wavelengths. Read that as frequency: the whole slider is dc up to the frequency at which the line is half a wavelength, and one octave inside it — quarter wave to half wave — is only half a turn. Either way the mismatch has moved and improved by nothing.",
                    "Set R = 50, X = 1: the readout is 40 dB return loss. Now set X = 10 — still a perfect 50 Ω resistor, still a small reactance — and it falls to 20 dB. A match is a knife edge in reactance, and holding that edge across a band is the entire problem of this module.",
                ],
            },
            "derive": {
                "title": "Node Q, and where the bandwidth goes",
                "minutes": 14,
                "vars": ["R", "X", "G", "Q", "R_p", "R_0", "R_L", "Y"],
                "brief": r'''
The cheapest match between two unequal resistances is an L-section: one series
reactance and one shunt reactance. Its bandwidth is set by a single number, and this
derivation extracts that number without ever choosing an inductor or a capacitor.

Start with a series combination of a resistance $R$ and a reactance $X$, and ask what
parallel combination looks the same at one frequency.
''',
                "steps": [
                    {
                        "prompt": "The admittance of the series pair is $Y = 1/(R + jX)$. Multiply above and below by the conjugate and write its real part $G$ in terms of $R$ and $X$.",
                        "answer": "\\frac{R}{R^2 + X^2}",
                        "placeholder": "\\frac{R}{R^{2} + X^{2}}",
                        "hint": "The conjugate of $R + jX$ is $R - jX$, and the product of the two is real.",
                        "deconstruct": [
                            "$Y = (R - jX)/((R + jX)(R - jX)) = (R - jX)/(R^2 + X^2)$.",
                            "The real part is the term without the $j$.",
                        ],
                    },
                    {
                        "prompt": "Define the node quality factor $Q = X/R$. The equivalent parallel resistance is $R_p = 1/G$. Write $R_p$ in terms of $R$ and $Q$.",
                        "answer": "R (1 + Q^2)",
                        "placeholder": "R(1 + Q^{2})",
                        "hint": "Take $R^2$ out of the bracket $R^2 + X^2$ before dividing.",
                        "deconstruct": [
                            "$R_p = (R^2 + X^2)/R = R(1 + X^2/R^2)$.",
                            "And $X/R$ is what $Q$ was defined to be.",
                        ],
                    },
                    {
                        "prompt": "An L-section matching $R_0$ to a larger $R_L$ works by making $R_0$ look like $R_L$ through exactly that transformation, so $R_L = R_0(1 + Q^2)$. Write $Q$ in terms of $R_L$ and $R_0$.",
                        "answer": "\\sqrt{\\frac{R_L}{R_0} - 1}",
                        "placeholder": "\\sqrt{\\frac{R_L}{R_0} - 1}",
                        "hint": "Divide both sides by $R_0$ first, then subtract 1.",
                        "deconstruct": [
                            "$R_L/R_0 = 1 + Q^2$.",
                            "So $Q^2 = R_L/R_0 - 1$.",
                        ],
                    },
                    {
                        "prompt": "A transistor with a 50 Ω generator needs to see an 800 Ω load resistance. Write the node $Q$ of the L-section that does it.",
                        "answer": "\\sqrt{15}",
                        "placeholder": "\\sqrt{15}",
                        "hint": "Put the two numbers into the previous answer; $800/50$ is a whole number.",
                        "deconstruct": [
                            "$R_L/R_0 = 16$.",
                            "So $Q = \\sqrt{16 - 1}$, which is about 3.87.",
                        ],
                    },
                    {
                        "prompt": "A singly-loaded resonance has fractional bandwidth $1/Q$. Write the fractional bandwidth of the L-section in terms of $R_L$ and $R_0$.",
                        "answer": "\\frac{1}{\\sqrt{\\frac{R_L}{R_0} - 1}}",
                        "placeholder": "\\frac{1}{\\sqrt{\\frac{R_L}{R_0} - 1}}",
                        "hint": "Just the reciprocal of the answer two steps ago.",
                        "deconstruct": [
                            "Bandwidth is $1/Q$ and $Q = \\sqrt{R_L/R_0 - 1}$.",
                            "For the 16:1 case above that is about 26 per cent.",
                        ],
                    },
                ],
                "closing": r'''
Read the last result carefully: the bandwidth of the cheapest possible match is fixed
entirely by the *ratio* of the two resistances. No choice of components changes it,
because no choice of components was ever made. Widening the band means adding
sections — a second L-section transforming through an intermediate resistance, or the
multi-section transformer of the lab — and each section costs length, loss and money.

The Bode–Fano bound says the same thing for reactive loads and says it as an
inequality that no network of any complexity can beat.
''',
            },
            "lab": {
                "title": "Measure what a match costs in bandwidth",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
Three functions. All frequencies are relative: `r = f/f0`, where $f_0$ is the
frequency at which every section is a quarter wave.

`binomial_sections(z0, rl, n)` returns the `n` section impedances of a binomial
(maximally flat) transformer, ordered from the `z0` end to the load. The design rule
is

```text
ln(Z[k+1] / Z[k]) = 2**(-n) * C(n, k) * ln(rl / z0)
```

with `Z[0] = z0` and `C(n, k)` the binomial coefficient (`math.comb`). For `n = 1`
this must reproduce $\sqrt{Z_0 Z_L}$.

`cascade_gamma(z0, sections, rl, r)` returns $|\Gamma|$ looking into the cascade at
relative frequency `r`. Work backwards from the load: for each section, take the
reflection coefficient of what you have so far *against that section's* impedance,
rotate it by `exp(-2j*theta)` with `theta = (pi/2)*r`, and convert back to an
impedance. Finish with the reflection of the result against `z0`.

`fractional_bandwidth(z0, sections, rl, gmax)` returns $(f_2 - f_1)/f_0$, where $f_1$
and $f_2$ are the two frequencies either side of `r = 1` at which $|\Gamma|$ first
reaches `gmax`. Bisect: the response exceeds `gmax` at both `r = 1e-6` and `r = 2`
for every case here, and is below it at `r = 1`, so each half has a clean bracket.
Sixty or so halvings are ample.
''',
                "files": [{"name": "main.py", "content": r'''
import math

import numpy as np


def binomial_sections(z0, rl, n):
    """Impedances of an n-section binomial quarter-wave transformer, load last."""
    # TODO: step the impedance up by exp(2**-n * C(n,k) * ln(rl/z0)) each time.
    return []


def cascade_gamma(z0, sections, rl, r):
    """|Gamma| into the cascade at relative frequency r = f/f0."""
    # TODO: fold the load back through each section in turn, then reflect on z0.
    return 0.0


def fractional_bandwidth(z0, sections, rl, gmax):
    """Fractional bandwidth over which |Gamma| stays at or below gmax."""
    # TODO: bisect for the band edge on each side of r = 1.
    return 0.0


if __name__ == "__main__":
    for n in (1, 2, 3):
        s = binomial_sections(50.0, 100.0, n)
        print(n, "section(s):", [round(v, 4) for v in s],
              " |Gamma| at f0:", round(cascade_gamma(50.0, s, 100.0, 1.0), 12),
              " BW:", round(fractional_bandwidth(50.0, s, 100.0, 0.1), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

import numpy as np


def binomial_sections(z0, rl, n):
    """Impedances of an n-section binomial quarter-wave transformer, load last."""
    total = math.log(rl / z0)
    z = float(z0)
    out = []
    for k in range(n):
        z = z * math.exp(2.0 ** (-n) * math.comb(n, k) * total)
        out.append(z)
    return out


def cascade_gamma(z0, sections, rl, r):
    """|Gamma| into the cascade at relative frequency r = f/f0."""
    theta = (math.pi / 2.0) * r
    z = complex(rl)
    for zs in reversed(list(sections)):
        g = (z - zs) / (z + zs) * np.exp(-2j * theta)
        z = zs * (1.0 + g) / (1.0 - g)
    return float(abs((z - z0) / (z + z0)))


def fractional_bandwidth(z0, sections, rl, gmax):
    """Fractional bandwidth over which |Gamma| stays at or below gmax."""
    def excess(r):
        return cascade_gamma(z0, sections, rl, r) - gmax

    def edge(outside, inside):
        f_out = excess(outside)
        for _ in range(120):
            mid = 0.5 * (outside + inside)
            f_mid = excess(mid)
            if (f_mid < 0.0) == (f_out < 0.0):
                outside, f_out = mid, f_mid
            else:
                inside = mid
        return 0.5 * (outside + inside)

    lo = edge(1e-6, 1.0)
    hi = edge(2.0, 1.0)
    return float(hi - lo)


if __name__ == "__main__":
    for n in (1, 2, 3):
        s = binomial_sections(50.0, 100.0, n)
        print(n, "section(s):", [round(v, 4) for v in s],
              " |Gamma| at f0:", round(cascade_gamma(50.0, s, 100.0, 1.0), 12),
              " BW:", round(fractional_bandwidth(50.0, s, 100.0, 0.1), 6))
'''}],
                "hints": [
                    "`math.comb(n, k)` gives the binomial coefficient directly; there is no need to build Pascal's triangle.",
                    "In `binomial_sections`, keep a running impedance and multiply it by the exponential each step — the recurrence is on ratios, not on absolute values.",
                    "`cascade_gamma` must iterate over the sections in *reverse*: the folding starts at the load and ends at the generator.",
                    "In the bisection, keep the endpoint that is on the same side of `gmax` as the starting outside point; that is what makes the loop converge on the crossing rather than wandering.",
                ],
                "tests": [
                    {"name": "one section is the quarter-wave transformer again", "code": r'''
_s = binomial_sections(50.0, 100.0, 1)
assert len(_s) == 1, f"one section means one impedance, got {len(_s)}"
assert abs(_s[0] - 70.71067811865476) < 1e-8, \
    f"a single binomial section must be sqrt(50*100) = 70.7107, got {_s[0]}"
'''},
                    {"name": "two sections split the step and stay monotonic", "code": r'''
_s = binomial_sections(50.0, 100.0, 2)
assert len(_s) == 2, f"expected two impedances, got {len(_s)}"
assert abs(_s[0] - 59.46035575013605) < 1e-8, \
    f"the first section should be 50 * 2**0.25 = 59.4604, got {_s[0]}"
assert abs(_s[1] - 84.08964152537145) < 1e-8, \
    f"the second should be 50 * 2**0.75 = 84.0896, got {_s[1]}"
assert 50.0 < _s[0] < _s[1] < 100.0, \
    "the sections must climb steadily from the line impedance to the load"
'''},
                    {"name": "matched at the design frequency, bare at dc", "code": r'''
for _n, _half in ((1, 0.24253562503633297), (2, 0.17407765595569785),
                  (3, 0.1242598254121419)):
    _s = binomial_sections(50.0, 100.0, _n)
    assert len(_s) == _n, f"{_n} sections means {_n} impedances, got {len(_s)}"
    _g = cascade_gamma(50.0, _s, 100.0, 1.0)
    assert _g < 1e-9, \
        f"{_n} binomial section(s) must give a perfect match at f0, got |Gamma| = {_g}"
    _off = cascade_gamma(50.0, _s, 100.0, 0.5)
    assert abs(_off - _half) < 1e-9, \
        f"at half the design frequency {_n} section(s) leave |Gamma| = {_half}, got {_off}"
_s2 = binomial_sections(50.0, 100.0, 2)
assert abs(cascade_gamma(50.0, _s2, 100.0, 0.0) - 1.0 / 3.0) < 1e-9, \
    "at zero frequency every section has zero length, so the bare 2:1 load shows through at 1/3"
'''},
                    {"name": "the response is symmetric about the design frequency", "code": r'''
_s = binomial_sections(50.0, 100.0, 1)
for _r, _want in ((0.3, 0.30046251958961323), (0.6, 0.2034664115336352),
                  (0.9, 0.05522353650670177)):
    _a = cascade_gamma(50.0, _s, 100.0, _r)
    assert abs(_a - _want) < 1e-9, \
        f"one section at r = {_r} leaves |Gamma| = {_want}, got {_a}"
    _b = cascade_gamma(50.0, _s, 100.0, 2.0 - _r)
    assert abs(_a - _b) < 1e-9, \
        f"quarter-wave responses mirror about r = 1: {_a} at {_r} against {_b} at {2.0 - _r}"
assert abs(cascade_gamma(50.0, _s, 100.0, 0.5) - 0.242535625036333) < 1e-9, \
    f"at half the design frequency a single section leaves |Gamma| = 0.24254, got {cascade_gamma(50.0, _s, 100.0, 0.5)}"
'''},
                    {"name": "the bandwidth matches the closed form", "code": r'''
import math
_s = binomial_sections(50.0, 100.0, 1)
_bw = fractional_bandwidth(50.0, _s, 100.0, 0.2)
_closed = 2.0 - (4.0 / math.pi) * math.acos(
    0.2 / math.sqrt(1.0 - 0.04) * 2.0 * math.sqrt(50.0 * 100.0) / 50.0)
assert abs(_closed - 0.7836531040612147) < 1e-9, \
    "the closed form itself should come to 0.78365 here"
assert abs(_bw - _closed) < 1e-6, \
    f"your bisection gives {_bw}, the closed form gives {_closed}"
'''},
                    {"name": "sections buy bandwidth", "code": r'''
_bws = [fractional_bandwidth(50.0, binomial_sections(50.0, 100.0, _n), 100.0, 0.1)
        for _n in (1, 2, 3)]
assert abs(_bws[0] - 0.36700168449596315) < 1e-6, \
    f"one section holds |Gamma| < 0.1 over 36.7 per cent of f0, got {_bws[0]}"
assert abs(_bws[1] - 0.7159938529980001) < 1e-6, \
    f"two sections should reach 71.6 per cent, got {_bws[1]}"
assert _bws[0] < _bws[1] < _bws[2], \
    f"each extra section must widen the band, got {_bws}"
'''},
                    {"name": "a bigger step costs bandwidth", "code": r'''
_narrow = fractional_bandwidth(50.0, binomial_sections(50.0, 200.0, 1), 200.0, 0.1)
_wide = fractional_bandwidth(50.0, binomial_sections(50.0, 100.0, 1), 100.0, 0.1)
assert abs(_narrow - 0.1711353385858121) < 1e-6, \
    f"a 4:1 step gives only 17.1 per cent with one section, got {_narrow}"
assert _narrow < _wide, \
    "the larger impedance step must give the narrower band, not the wider one"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Match one load four ways and price each in bandwidth",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
A 200 Ω antenna feed on a 50 Ω system: a 4:1 step, $|\Gamma| = 0.6$, VSWR 4:1. Four
networks will match it perfectly at the design frequency $f_0$, and they differ only
in how quickly they stop working either side of it.

Build all four and measure them:

1. a short-circuited shunt stub at the right distance from the load;
2. a single quarter-wave transformer;
3. a two-section binomial transformer;
4. a three-section binomial transformer.

Everything is expressed against a relative frequency `r = f/f0`. A physical length
that is $d$ wavelengths at $f_0$ is $dr$ wavelengths at $f$, which is the only piece
of frequency dependence in the whole problem.

## Suggested order

The checks are ordered so they light up as you build. `gamma` and `vswr` first;
then the stub design, which reuses module 3 unchanged; then the transformers, which
reuse module 4 unchanged; then the generic `fractional_bandwidth`, which is checked
against a synthetic V-shaped response whose answer you can work out on paper before
you trust it on a real one.

The last check is the point of the course: the exact match with the fewest parts has
the narrowest band, and each section you add widens it.

## The stub response away from f0

At relative frequency `r`, the line to the stub is `d*r` wavelengths and the stub
itself is `ell*r` wavelengths. So

```text
g   = gamma(rl, z0) * exp(-4j*pi*d*r)
y   = (1 - g)/(1 + g) + (-1j / tan(2*pi*ell*r))
out = abs((1 - y)/(1 + y))
```

The stub's susceptance drifts with frequency at the same time as the line rotates,
and the two drifts do not cancel. That is the whole reason a stub match is narrow.
''',
        "deliverables": [
            "`gamma(z, z0)` and `vswr(g)`, reproducing module 1 exactly, with `vswr` returning `float('inf')` on a total reflection.",
            "`stub_design(rl, z0)` returning `(d, ell)` in wavelengths at $f_0$: the distance from the load to a short-circuited shunt stub, and that stub's length.",
            "`stub_gamma(rl, z0, d, ell, r)` returning $|\\Gamma|$ of the stub network at relative frequency `r`, with both lengths scaling as `r`.",
            "`binomial_sections(z0, rl, n)` and `cascade_gamma(z0, sections, rl, r)` for the multi-section transformers.",
            "`fractional_bandwidth(response, gmax)` taking a **callable** of `r` and returning the width of the band around `r = 1` over which the response stays at or below `gmax`.",
            "A short comment at the top of `main.py` giving the four measured bandwidths and one sentence on why they come out in that order.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, no RF toolbox.",
            "`fractional_bandwidth` must take the response as a function, not as a set of transformer sections, or the stub network cannot be measured with the same code.",
            "Bisect for the band edges rather than scanning on a grid; the checks compare against values good to six decimal places.",
            "Every network must be exact at `r = 1`. A design that is merely close there is a design with a bug in it, not an approximation.",
        ],
        "rubric": [
            {"criterion": "Reflection and standing-wave basics", "weight": 15,
             "evidence": "`gamma` and `vswr` return the right values for a matched load, a 4:1 load and a total reflection, including the infinite case."},
            {"criterion": "Stub design and its response", "weight": 30,
             "evidence": "`stub_design` places the stub and sizes it so that `stub_gamma` is below 1e-9 at the design frequency, and moving either length spoils the match."},
            {"criterion": "Multi-section transformers", "weight": 30,
             "evidence": "Binomial section impedances match the closed form for one, two and three sections, and every cascade is exact at f0 while showing the bare load at dc."},
            {"criterion": "Bandwidth measurement", "weight": 25,
             "evidence": "`fractional_bandwidth` recovers the known answer for a synthetic response and orders the four real networks correctly by band width."},
        ],
        "hints": [
            "`stub_design` is `single_stub` from module 3 followed by `short_stub_length`; nothing new is needed.",
            "A shorted stub `ell` wavelengths long has normalised admittance `-1j/tan(2*pi*ell)`. At relative frequency `r` that becomes `-1j/tan(2*pi*ell*r)`.",
            "Write `fractional_bandwidth(response, gmax)` so that `response` is any callable of `r`; then pass it a one-line lambda for each of the four networks.",
            "Both brackets are clean for every network here: the response is above `gmax` at `r = 1e-6` and at `r = 2`, and below it at `r = 1`.",
            "If a bandwidth comes out as zero, check that your bisection keeps the endpoint on the *outside* of the band, not the one nearest `r = 1`.",
        ],
        "files": [
            {"name": "spec.py", "ro": True, "content": r'''
"""The system this capstone matches. Do not edit — the checks rely on these numbers."""

Z0 = 50.0          # ohm, the feed line
R_LOAD = 200.0     # ohm, the antenna feed resistance at f0
GAMMA_MAX = 0.1    # the band edge: |Gamma| = 0.1 is 20 dB return loss
'''},
            {"name": "main.py", "content": r'''
import math

import numpy as np

from spec import Z0, R_LOAD, GAMMA_MAX

# Measured fractional bandwidths at |Gamma| <= 0.1:
#   stub            -> TODO
#   1-section       -> TODO
#   2-section       -> TODO
#   3-section       -> TODO
# Why they come out in that order: TODO


def gamma(z, z0):
    """Reflection coefficient of impedance z on a line of impedance z0."""
    # TODO
    return 0j


def vswr(g):
    """Standing-wave ratio; inf when |g| >= 1."""
    # TODO
    return 0.0


def stub_design(rl, z0):
    """Return (d, ell) in wavelengths: stub distance, and shorted stub length."""
    # TODO: rotate to unit conductance, then size a shorted stub for what is left.
    return (0.0, 0.0)


def stub_gamma(rl, z0, d, ell, r):
    """|Gamma| of the stub network at relative frequency r = f/f0."""
    # TODO: both lengths scale with r.
    return 0.0


def binomial_sections(z0, rl, n):
    """Impedances of an n-section binomial quarter-wave transformer, load last."""
    # TODO
    return []


def cascade_gamma(z0, sections, rl, r):
    """|Gamma| into the cascade at relative frequency r = f/f0."""
    # TODO
    return 0.0


def fractional_bandwidth(response, gmax):
    """Width of the band around r = 1 over which `response(r)` stays <= gmax."""
    # TODO: bisect once on each side of r = 1.
    return 0.0


if __name__ == "__main__":
    print("load:", R_LOAD, "ohm, |Gamma| =", abs(gamma(R_LOAD, Z0)),
          " VSWR =", vswr(gamma(R_LOAD, Z0)))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import math

import numpy as np

from spec import Z0, R_LOAD, GAMMA_MAX

# Measured fractional bandwidths at |Gamma| <= 0.1:
#   stub            -> 0.073016
#   1-section       -> 0.171135
#   2-section       -> 0.477184
#   3-section       -> 0.678982
# Why they come out in that order: every one of these is exact at f0, so the
# ranking is decided entirely by how many independent reflections are available
# to cancel each other away from f0. The stub has one cancellation and both of
# its lengths drift the wrong way at once, so it is the narrowest. Each extra
# quarter-wave section adds another interface whose reflection can be traded
# against the others, and the binomial weighting spends that freedom on
# flatness at f0 rather than on ripple.


def gamma(z, z0):
    """Reflection coefficient of impedance z on a line of impedance z0."""
    z = complex(z)
    return complex((z - z0) / (z + z0))


def vswr(g):
    """Standing-wave ratio; inf when |g| >= 1."""
    m = abs(g)
    if m >= 1.0:
        return float("inf")
    return float((1.0 + m) / (1.0 - m))


def stub_design(rl, z0):
    """Return (d, ell) in wavelengths: stub distance, and shorted stub length."""
    g = gamma(rl, z0)
    rho = abs(g)
    if rho < 1e-14:
        return (0.0, 0.0)
    theta = float(np.angle(g))
    phi = float(np.arccos(-rho))
    cands = sorted(((theta - p) / (4.0 * np.pi)) % 0.5 for p in (phi, -phi))
    d = float(cands[0])
    gd = g * np.exp(-4j * np.pi * d)
    y = (1.0 - gd) / (1.0 + gd)
    b = float(-y.imag)
    ell = float((np.arctan2(-1.0, b) / (2.0 * np.pi)) % 0.5)
    return (d, ell)


def stub_gamma(rl, z0, d, ell, r):
    """|Gamma| of the stub network at relative frequency r = f/f0."""
    g = gamma(rl, z0) * np.exp(-4j * np.pi * d * r)
    y = (1.0 - g) / (1.0 + g) + (-1j / np.tan(2.0 * np.pi * ell * r))
    return float(abs((1.0 - y) / (1.0 + y)))


def binomial_sections(z0, rl, n):
    """Impedances of an n-section binomial quarter-wave transformer, load last."""
    total = math.log(rl / z0)
    z = float(z0)
    out = []
    for k in range(n):
        z = z * math.exp(2.0 ** (-n) * math.comb(n, k) * total)
        out.append(z)
    return out


def cascade_gamma(z0, sections, rl, r):
    """|Gamma| into the cascade at relative frequency r = f/f0."""
    theta = (math.pi / 2.0) * r
    z = complex(rl)
    for zs in reversed(list(sections)):
        g = (z - zs) / (z + zs) * np.exp(-2j * theta)
        z = zs * (1.0 + g) / (1.0 - g)
    return float(abs((z - z0) / (z + z0)))


def fractional_bandwidth(response, gmax):
    """Width of the band around r = 1 over which `response(r)` stays <= gmax."""
    def excess(r):
        return response(r) - gmax

    def edge(outside, inside):
        f_out = excess(outside)
        for _ in range(120):
            mid = 0.5 * (outside + inside)
            f_mid = excess(mid)
            if (f_mid < 0.0) == (f_out < 0.0):
                outside, f_out = mid, f_mid
            else:
                inside = mid
        return 0.5 * (outside + inside)

    return float(edge(2.0, 1.0) - edge(1e-6, 1.0))


if __name__ == "__main__":
    print("load:", R_LOAD, "ohm, |Gamma| =", abs(gamma(R_LOAD, Z0)),
          " VSWR =", vswr(gamma(R_LOAD, Z0)))
    d, ell = stub_design(R_LOAD, Z0)
    print("stub: d =", round(d, 6), " ell =", round(ell, 6),
          " BW =", round(fractional_bandwidth(
              lambda r: stub_gamma(R_LOAD, Z0, d, ell, r), GAMMA_MAX), 6))
    for n in (1, 2, 3):
        s = binomial_sections(Z0, R_LOAD, n)
        print(n, "section(s):", [round(v, 4) for v in s],
              " BW =", round(fractional_bandwidth(
                  lambda r, s=s: cascade_gamma(Z0, s, R_LOAD, r), GAMMA_MAX), 6))
'''},
        ],
        "tests": [
            {"name": "the raw load is a four to one mismatch", "code": r'''
from spec import Z0, R_LOAD
_g = gamma(R_LOAD, Z0)
assert abs(_g - 0.6) < 1e-12, \
    f"(200 - 50)/(200 + 50) is 0.6, got {_g}"
assert abs(vswr(_g) - 4.0) < 1e-12, \
    f"|Gamma| = 0.6 is a 4:1 standing wave, got {vswr(_g)}"
assert abs(vswr(gamma(Z0, Z0)) - 1.0) < 1e-12, \
    "a load equal to the line has no standing wave, so VSWR is 1"
import math
assert math.isinf(vswr(gamma(0.0, Z0))), \
    "a short reflects everything, so the envelope minimum is zero and VSWR is infinite"
'''},
            {"name": "the stub lands the match exactly at f0", "code": r'''
from spec import Z0, R_LOAD
_d, _ell = stub_design(R_LOAD, Z0)
assert abs(_d - 0.17620819117478337) < 1e-7, \
    f"the stub belongs 0.176208 wavelengths from the load, got {_d}"
assert abs(_ell - 0.09358352090549937) < 1e-7, \
    f"the shorted stub should be 0.093584 wavelengths long, got {_ell}"
_at_f0 = stub_gamma(R_LOAD, Z0, _d, _ell, 1.0)
assert _at_f0 < 1e-9, \
    f"the design must be exact at f0, not merely close; got |Gamma| = {_at_f0}"
assert stub_gamma(R_LOAD, Z0, _d + 0.05, _ell, 1.0) > 0.3, \
    "moving the stub 0.05 wavelengths must wreck the match, or stub_gamma ignores d"
assert stub_gamma(R_LOAD, Z0, _d, _ell + 0.05, 1.0) > 0.2, \
    "lengthening the stub 0.05 wavelengths must wreck it too, or stub_gamma ignores ell"
'''},
            {"name": "the binomial sections match the closed form", "code": r'''
from spec import Z0, R_LOAD
_s1 = binomial_sections(Z0, R_LOAD, 1)
assert len(_s1) == 1 and abs(_s1[0] - 100.0) < 1e-8, \
    f"a single section is sqrt(50*200) = 100 ohm, got {_s1}"
_s2 = binomial_sections(Z0, R_LOAD, 2)
assert len(_s2) == 2, f"expected two impedances, got {len(_s2)}"
assert abs(_s2[0] - 70.71067811865474) < 1e-7 and abs(_s2[1] - 141.42135623730948) < 1e-7, \
    f"two sections are 70.7107 and 141.4214 ohm, got {_s2}"
_s3 = binomial_sections(Z0, R_LOAD, 3)
assert len(_s3) == 3, f"expected three impedances, got {len(_s3)}"
assert abs(_s3[0] - 59.46035575013605) < 1e-7, f"first of three should be 59.4604, got {_s3[0]}"
assert abs(_s3[1] - 100.0) < 1e-7, f"the middle of three should be 100.0, got {_s3[1]}"
assert abs(_s3[2] - 168.1792830507429) < 1e-7, f"last of three should be 168.1793, got {_s3[2]}"
'''},
            {"name": "every transformer is exact at f0 and bare at dc", "code": r'''
from spec import Z0, R_LOAD
for _n, _half in ((1, 0.4685212856658181), (2, 0.3511234415883917),
                  (3, 0.2579800958418455)):
    _s = binomial_sections(Z0, R_LOAD, _n)
    assert len(_s) == _n, f"{_n} sections means {_n} impedances, got {len(_s)}"
    _g = cascade_gamma(Z0, _s, R_LOAD, 1.0)
    assert _g < 1e-9, \
        f"{_n} section(s) must be exact at f0, got |Gamma| = {_g}"
    _off = cascade_gamma(Z0, _s, R_LOAD, 0.5)
    assert abs(_off - _half) < 1e-9, \
        f"at half the design frequency {_n} section(s) leave |Gamma| = {_half}, got {_off}"
    _dc = cascade_gamma(Z0, _s, R_LOAD, 0.0)
    assert abs(_dc - 0.6) < 1e-9, \
        f"at r = 0 every section has zero length, so the bare 0.6 must show through; got {_dc}"
assert abs(cascade_gamma(Z0, binomial_sections(Z0, R_LOAD, 1), R_LOAD, 2.0) - 0.6) < 1e-9, \
    "at twice the design frequency each section is a half wave and transforms nothing"
'''},
            {"name": "the bandwidth finder recovers a known answer", "code": r'''
_v = lambda r: 2.0 * abs(r - 1.0)
_bw = fractional_bandwidth(_v, 0.3)
assert abs(_bw - 0.3) < 1e-6, \
    f"|Gamma| = 2|r-1| reaches 0.3 at r = 0.85 and r = 1.15, so the width is 0.3; got {_bw}"
assert abs(fractional_bandwidth(_v, 0.6) - 0.6) < 1e-6, \
    f"the same shape at gmax = 0.6 gives 0.6, got {fractional_bandwidth(_v, 0.6)}"
assert abs(fractional_bandwidth(_v, 0.1) - 0.1) < 1e-6, \
    "and 0.1 at gmax = 0.1 — the finder must scale, not return a constant"
'''},
            {"name": "the price of the match, in order", "code": r'''
from spec import Z0, R_LOAD, GAMMA_MAX
_d, _ell = stub_design(R_LOAD, Z0)
_bw_stub = fractional_bandwidth(lambda r: stub_gamma(R_LOAD, Z0, _d, _ell, r), GAMMA_MAX)
_bw = [fractional_bandwidth(
           lambda r, _s=binomial_sections(Z0, R_LOAD, _n): cascade_gamma(Z0, _s, R_LOAD, r),
           GAMMA_MAX)
       for _n in (1, 2, 3)]
assert abs(_bw_stub - 0.0730156493924825) < 1e-6, \
    f"the stub holds 20 dB over 7.30 per cent of f0, got {_bw_stub}"
assert abs(_bw[0] - 0.1711353385858121) < 1e-6, \
    f"one quarter-wave section gives 17.11 per cent, got {_bw[0]}"
assert abs(_bw[1] - 0.47718359825224255) < 1e-6, \
    f"two sections give 47.72 per cent, got {_bw[1]}"
assert abs(_bw[2] - 0.6789816135710758) < 1e-6, \
    f"three sections give 67.90 per cent, got {_bw[2]}"
assert _bw_stub < _bw[0] < _bw[1] < _bw[2], \
    f"the ordering is the point of the exercise: got stub {_bw_stub} against {_bw}"
'''},
        ],
    },
}
