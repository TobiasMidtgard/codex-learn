"""RFIC520 — Noise in Analog Circuits.

Authored against the CTRL510 template. The rules that matter here:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; no scipy, no DSP or RF libraries
  * seed every RNG, and every expected value in a check was computed by running
    the reference solution, never assumed
"""

COURSE = {
    "id": "RFIC520",
    "title": "Noise in Analog Circuits",
    "band": 1,
    "level": "Advanced",
    "prereqs": ["RFIC510"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◈",
    "summary": (
        "Every resistor you put in a signal path adds noise you cannot design away, and "
        "every transistor adds more. This course treats noise the way a designer has to: "
        "as a spectral density you integrate over a bandwidth you chose, referred back to "
        "the input where the signal is, and traded against the current you are willing to "
        "burn. Thermal noise first, then flicker, then the cascade, then the bandwidth."
    ),
    "outcomes": [
        "Compute the thermal noise density of a resistive network and the r.m.s. voltage it produces over a stated bandwidth.",
        "Separate flicker from thermal noise in a measured spectrum, and locate the corner frequency from data rather than from a datasheet.",
        "Refer the noise of a whole cascade back to its input, and use Friis to say which stage actually matters.",
        "Compute equivalent noise bandwidth numerically, and quantify the noise, power and bandwidth trade for a front end.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that produces a complete noise budget for a receiver front end and prices its noise figure in milliwatts.",
    "reading": [
        "*Noise in Solid State Devices and Circuits*, Van der Ziel — for the physics behind the two mechanisms.",
        "*The Design of CMOS Radio-Frequency Integrated Circuits*, Lee — chapters 11 and 12.",
        "Friis, *Noise Figures of Radio Receivers*, Proc. IRE 1944 — three pages, still the whole story.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Thermal noise and spectral density",
            "summary": "A resistor is a noise source whose strength depends on temperature and resistance and on nothing else.",
            "concepts": [
                "Thermal noise is the equilibrium fluctuation of carriers: it exists with no current flowing and no bias applied.",
                "The one-sided voltage density of a resistor is $S_v = 4k_BTR$, in V²/Hz, flat to frequencies far above any circuit you will build.",
                "Density in V/√Hz is the square root of that. Densities add in *power*, so uncorrelated sources add as squares, never as sums.",
                "Available noise power is $k_BTB$ — independent of $R$, which is why noise figure can be a property of a two-port alone.",
                "A resistive network's noise is the noise of its equivalent resistance seen at the terminals of interest.",
            ],
            "sandbox": {
                "title": "The flat floor a resistor sets",
                "visualiser": "noise-corner",
                "minutes": 8,
                "initial": {"fc": 100, "nth": 8},
                "brief": r'''
The curve is an input-referred voltage noise density against frequency, drawn on log
axes. The corner has deliberately been pushed down to 100 Hz so that almost the whole
plot is the thermal part — a flat floor.

Flat means the noise has no memory of frequency. Every hertz of bandwidth you accept
brings the same contribution as every other hertz.
''',
                "notice": [
                    "Move the thermal floor from 8 to 16 nV/√Hz. The whole curve rises by 6 dB, because doubling a voltage density is 6 dB, not 3 — this is the single most common slip in noise arithmetic.",
                    "A floor of 4 nV/√Hz is about what a 1 kΩ resistor gives at room temperature. Set it there, then set it to 8 — that is a 4 kΩ resistor, because density goes as $\\sqrt{R}$, not as $R$.",
                    "Push the corner up to 100 kHz and back down. Above the corner nothing moves at all: the thermal floor is set by resistance and temperature and is untouched by whatever the flicker mechanism is doing.",
                ],
            },
            "derive": {
                "title": "From the open-circuit voltage to available noise power",
                "minutes": 12,
                "vars": ["k_B", "T", "R", "B", "R_1", "R_2", "S_v", "P_n"],
                "brief": r'''
A resistor $R$ at temperature $T$ behaves as a noiseless resistor in series with a
voltage source whose mean-square open-circuit value in a bandwidth $B$ is

$$\overline{v_n^2} = 4k_BTRB$$

Everything else in this course is bookkeeping on top of that one statement. Start by
asking what a load actually receives.
''',
                "steps": [
                    {
                        "prompt": "Connect a noiseless load of the same value $R$. The two resistances divide the source voltage in half. Write the mean-square voltage that appears across the load.",
                        "given": "The open-circuit mean-square voltage is $4k_BTRB$.",
                        "answer": "k_B T R B",
                        "hint": "Half the voltage is a quarter of the mean square — the divider acts on the amplitude, and mean square is amplitude squared.",
                        "deconstruct": [
                            "The divider gives $v_{load} = v_n / 2$.",
                            "Squaring and averaging: $\\overline{v_{load}^2} = \\overline{v_n^2}/4 = k_BTRB$.",
                        ],
                    },
                    {
                        "prompt": "That voltage sits across the load resistance $R$. Write the average power $P_n$ delivered to the load.",
                        "answer": "k_B T B",
                        "hint": "Average power into a resistance is the mean-square voltage divided by that resistance.",
                        "deconstruct": [
                            "$P_n = \\overline{v_{load}^2} / R$.",
                            "Substituting $k_BTRB$ makes the $R$ cancel.",
                        ],
                    },
                    {
                        "prompt": "Spectral density is mean square per hertz. Write the one-sided voltage spectral density $S_v$ of the resistor, in V²/Hz.",
                        "answer": "4 k_B T R",
                        "hint": "The bandwidth $B$ appeared only as a multiplier, so removing it leaves the density.",
                        "deconstruct": [
                            "$\\overline{v_n^2} = 4k_BTRB$ is linear in $B$, which is what 'flat' means.",
                            "Divide by $B$ and the density is what remains.",
                        ],
                    },
                    {
                        "prompt": "Two resistors $R_1$ and $R_2$ are connected in parallel. Their noise sources are independent. Write the mean-square open-circuit voltage across the pair, in bandwidth $B$.",
                        "answer": "4 k_B T B \\frac{R_1 R_2}{R_1 + R_2}",
                        "hint": "You do not have to add two sources. A resistive network at one temperature has the noise of the resistance you measure at its terminals.",
                        "deconstruct": [
                            "The resistance seen across the pair is $R_1R_2/(R_1+R_2)$.",
                            "Put that in place of $R$ in $4k_BTRB$.",
                        ],
                    },
                ],
                "closing": r'''
Two results worth keeping apart. The *voltage* depends on $R$ — bigger resistor, more
noise volts. The *available power* does not, which is why an antenna, a cable and a
50 Ω terminator all deliver the same $k_BTB$, and why noise figure can be quoted for a
component without naming the source impedance.
''',
            },
            "quiz": {
                "title": "A resistor, and the noise it makes for free",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What is the one-sided thermal noise voltage density of a resistor?",
                        "opts": ["$4k_BTR$ in V²/Hz", "$2k_BTR$ in V²/Hz", "$k_BT/R$ in V²/Hz", "$4k_BTR^2$ in V²/Hz"],
                        "a": 0,
                        "why": r"""
$S_v = 4k_BTR$, and the density in V/√Hz is its square root — for 1 kΩ at room
temperature, about 4 nV/√Hz, which is worth memorising as an anchor. Notice what is
*not* in it: no current, no voltage, no frequency. Thermal noise is flat to frequencies
far beyond any circuit you will build, and it is present in an unpowered resistor
sitting in a drawer.
""",
                    },
                    {
                        "q": "Does a resistor need current flowing through it to generate thermal noise?",
                        "opts": [
                            "No — it is an equilibrium fluctuation and exists with no bias at all",
                            "Yes, the noise is proportional to the current",
                            "Yes, but only above the flicker corner",
                            "Only if the resistor is non-linear",
                        ],
                        "a": 0,
                        "why": r"""
None at all. Thermal noise is the carriers jostling about at temperature $T$, and it
would be there in a resistor connected to nothing. That is exactly what distinguishes it
from flicker noise in the next module, which is a *non*-equilibrium effect and does need
current — and from shot noise, which needs a current crossing a barrier. Three
mechanisms, three different dependences, and telling them apart is most of noise
analysis.
""",
                    },
                    {
                        "q": "You double the resistance. What happens to the noise voltage density in V/√Hz?",
                        "opts": [
                            "It rises by $\\sqrt{2}$",
                            "It doubles",
                            "It quadruples",
                            "It is unchanged",
                        ],
                        "a": 0,
                        "why": r"""
The *power* density goes as $R$, so the voltage density goes as $\sqrt{R}$. This is the
reason noise arguments are almost always easier in V²/Hz: powers add, and the square
roots only come out at the end. It also explains why raising a bias resistor to save
current costs less noise than the intuition suggests — a hundredfold increase in $R$ is
only tenfold in nV/√Hz.
""",
                    },
                    {
                        "q": "Two uncorrelated noise sources reach the same node. How do they combine?",
                        "opts": [
                            "Their power densities add",
                            "Their voltage densities add",
                            "The larger one wins and the other is ignored",
                            "They partly cancel",
                        ],
                        "a": 0,
                        "why": r"""
Powers add for uncorrelated sources, so the voltages add in quadrature. A practical
consequence worth internalising: a source 3× smaller than the dominant one adds about 5%
to the total, which is usually not worth engineering away. It also means "the larger one
wins" is a decent approximation and a poor habit — when two contributions are comparable
the quadrature sum is 1.41× either, not 2×.
""",
                    },
                    {
                        "q": "What is $k_BT$ at 290 K, expressed as an available noise power density?",
                        "opts": ["−174 dBm/Hz", "−114 dBm/Hz", "−204 dBm/Hz", "−90 dBm/Hz"],
                        "a": 0,
                        "why": r"""
$-174$ dBm/Hz is the reference every noise figure in radio is quoted against, and it is
worth knowing cold: the noise floor of a 1 MHz channel is $-174 + 60 = -114$ dBm, and a
receiver with a 3 dB noise figure has a floor of $-111$ dBm. That chain — floor plus
bandwidth in dB plus noise figure — is the entire link budget on the noise side, and
$-114$ dBm/MHz is the other number people carry around.
""",
                    },
                ],
            },
            "lab": {
                "title": "Thermal noise of a resistive network",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Four small functions, and one simulation that checks the arithmetic against samples.

- `thermal_density(R, T)` — the open-circuit noise density of `R` in V/√Hz, that is
  $\sqrt{4k_BTR}$.
- `parallel_density(R1, R2, T)` — the same, for two resistors in parallel. Use the
  equivalent resistance; do not add the two densities.
- `rms_over_band(density, B)` — the r.m.s. volts a flat density produces in a
  bandwidth `B`.
- `sample_noise(R, B, n, seed, T)` — `n` Gaussian samples whose standard deviation is
  exactly that r.m.s. value. Use `np.random.default_rng(seed)` so the checks are
  reproducible.

Boltzmann's constant is already defined as `K_B`. Everything is in SI: ohms, kelvin,
hertz, volts.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

K_B = 1.380649e-23   # J/K


def thermal_density(R, T=290.0):
    """Open-circuit thermal noise density of R, in V/sqrt(Hz)."""
    # TODO: sqrt(4 * K_B * T * R)
    return 0.0


def parallel_density(R1, R2, T=290.0):
    """Noise density across R1 in parallel with R2, in V/sqrt(Hz)."""
    # TODO: use the equivalent resistance, not the sum of two densities.
    return 0.0


def rms_over_band(density, B):
    """RMS volts produced by a flat density over a bandwidth B."""
    # TODO: a flat density integrates to density**2 * B.
    return 0.0


def sample_noise(R, B, n, seed, T=290.0):
    """n samples of band-limited thermal noise from R, in volts."""
    rng = np.random.default_rng(seed)
    # TODO: normal samples with the standard deviation you computed above.
    return np.zeros(n)


if __name__ == "__main__":
    print("1 kohm at 290 K:", round(thermal_density(1000.0) * 1e9, 3), "nV/rtHz")
    print("over 1 MHz     :", round(rms_over_band(thermal_density(1000.0), 1e6) * 1e6, 3), "uV rms")
    print("1k || 1k       :", round(parallel_density(1000.0, 1000.0) * 1e9, 3), "nV/rtHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

K_B = 1.380649e-23   # J/K


def thermal_density(R, T=290.0):
    """Open-circuit thermal noise density of R, in V/sqrt(Hz)."""
    return float(np.sqrt(4.0 * K_B * T * R))


def parallel_density(R1, R2, T=290.0):
    """Noise density across R1 in parallel with R2, in V/sqrt(Hz)."""
    return thermal_density(R1 * R2 / (R1 + R2), T)


def rms_over_band(density, B):
    """RMS volts produced by a flat density over a bandwidth B."""
    return float(density * np.sqrt(B))


def sample_noise(R, B, n, seed, T=290.0):
    """n samples of band-limited thermal noise from R, in volts."""
    rng = np.random.default_rng(seed)
    sigma = rms_over_band(thermal_density(R, T), B)
    return rng.normal(0.0, sigma, n)


if __name__ == "__main__":
    print("1 kohm at 290 K:", round(thermal_density(1000.0) * 1e9, 3), "nV/rtHz")
    print("over 1 MHz     :", round(rms_over_band(thermal_density(1000.0), 1e6) * 1e6, 3), "uV rms")
    print("1k || 1k       :", round(parallel_density(1000.0, 1000.0) * 1e9, 3), "nV/rtHz")
'''}],
                "hints": [
                    "`np.sqrt(4.0 * K_B * T * R)` is the whole of `thermal_density`.",
                    "For the parallel pair, compute `R1 * R2 / (R1 + R2)` first and hand it to `thermal_density`.",
                    "`rng.normal(0.0, sigma, n)` gives you `n` samples with standard deviation `sigma`.",
                ],
                "tests": [
                    {"name": "a kilohm at room temperature is about four nanovolts per root hertz", "code": r'''
_d = thermal_density(1000.0, 290.0)
assert abs(_d - 4.001940579269013e-09) < 1e-12, \
    f"sqrt(4*k*290*1000) is 4.002 nV/rtHz; you returned {_d:.4e} V/rtHz"
'''},
                    {"name": "density grows as the square root of resistance", "code": r'''
_a = thermal_density(1000.0, 290.0)
_b = thermal_density(4000.0, 290.0)
assert abs(_b / _a - 2.0) < 1e-9, \
    f"four times the resistance is twice the density, not four times: ratio was {_b/_a:.4f}"
'''},
                    {"name": "cooling the resistor lowers its noise", "code": r'''
import numpy as np
_warm = thermal_density(1000.0, 290.0)
_cold = thermal_density(1000.0, 77.0)
assert abs(_cold - 2.062134554290772e-09) < 1e-12, \
    f"at 77 K the same 1 kohm gives 2.062 nV/rtHz; you returned {_cold:.4e}"
assert abs(_warm / _cold - np.sqrt(290.0 / 77.0)) < 1e-9, \
    "the ratio should be sqrt(T1/T2) — noise voltage follows the square root of temperature"
'''},
                    {"name": "parallel resistors are quieter than either one alone", "code": r'''
_p = parallel_density(1000.0, 1000.0, 290.0)
assert abs(_p - 2.829799321506739e-09) < 1e-12, \
    f"1k || 1k is 500 ohm, so 2.830 nV/rtHz; you returned {_p:.4e}"
assert _p < thermal_density(1000.0, 290.0), \
    "adding a resistor in parallel lowers the terminal resistance, so it lowers the noise — you have probably summed two densities instead"
'''},
                    {"name": "an unequal parallel pair follows the equivalent resistance", "code": r'''
_p = parallel_density(1000.0, 3000.0, 290.0)
assert abs(_p - 3.465782206082777e-09) < 1e-12, \
    f"1k || 3k is 750 ohm, so 3.466 nV/rtHz; you returned {_p:.4e}"
'''},
                    {"name": "a flat density integrates to a root-bandwidth r.m.s.", "code": r'''
_v = rms_over_band(4.001940579269013e-09, 1e6)
assert abs(_v - 4.001940579269012e-06) < 1e-12, \
    f"4.002 nV/rtHz over 1 MHz is 4.002 uV rms; you returned {_v:.4e} V"
assert abs(rms_over_band(1e-9, 4e6) / rms_over_band(1e-9, 1e6) - 2.0) < 1e-9, \
    "four times the bandwidth is twice the r.m.s. voltage, because power is what adds"
'''},
                    {"name": "the samples really have the predicted spread", "code": r'''
import numpy as np
_s = sample_noise(1000.0, 1e6, 200000, 7, 290.0)
assert len(_s) == 200000, f"expected 200000 samples, got {len(_s)}"
_want = rms_over_band(thermal_density(1000.0, 290.0), 1e6)
assert abs(float(np.std(_s)) / _want - 1.0) < 0.02, \
    f"the sample standard deviation should match the predicted r.m.s. {_want:.4e}, got {float(np.std(_s)):.4e}"
assert abs(float(np.mean(_s))) < 0.05 * _want, \
    "thermal noise has zero mean; a non-zero mean means you have added an offset somewhere"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Flicker noise and the corner frequency",
            "summary": "Below the corner the spectrum is not flat, and integrating for longer stops helping.",
            "concepts": [
                "Flicker noise is a surface and trapping effect, not an equilibrium one: it needs current, and it scales with the inverse of device area.",
                "The gate-referred model $S_{fl}(f) = \\frac{K_f}{C_{ox}WLf}$ — one over frequency, one over area.",
                "The corner $f_c$ is where the two mechanisms are equal, so the total density there is $\\sqrt{2}$ times the floor, not twice it.",
                "Integrating $1/f$ gives a logarithm: the mean square between two frequencies depends only on their *ratio*.",
                "Chopping and correlated double sampling exist because the logarithm is so unforgiving — you move the signal above the corner instead of fighting the noise.",
            ],
            "sandbox": {
                "title": "Where the two mechanisms cross",
                "visualiser": "noise-corner",
                "minutes": 8,
                "initial": {"fc": 20000, "nth": 5},
                "brief": r'''
The same axes as the first module, but now the corner is inside the plot. To the left
of the dashed marker the density falls as $1/\sqrt{f}$ — that is $1/f$ in power. To the
right it is flat.

The total density drawn here is $n_{th}\sqrt{1 + f_c/f}$: the two mechanisms are
independent, so their powers add and their densities add in quadrature.
''',
                "notice": [
                    "Read the curve exactly at the dashed corner line. It sits about 3 dB above the floor, not 6 — at $f_c$ the two contributions are equal in *power*, so the density is $\\sqrt{2}$ times the floor.",
                    "Take the corner from 20 kHz down to 1 kHz. The flat part does not move at all: the corner is a property of the device, and the floor is a property of its transconductance.",
                    "Raise the thermal floor while leaving the corner slider alone. The plotted corner marker stays put, but for a real device it would not — raising $g_m$ lowers the thermal floor and pushes the true corner up.",
                    "A decade below the corner the density is about 3.3 times the floor, so the *power* there is eleven times it. That factor of roughly ten per decade is why d.c.-coupled measurements are so expensive.",
                ],
            },
            "derive": {
                "title": "Locating the corner of a MOS transistor",
                "minutes": 13,
                "vars": ["f", "f_c", "K_f", "C_ox", "W", "L", "g_m", "k_B", "T", "gamma"],
                "brief": r'''
For a MOS transistor, both noise mechanisms are conventionally referred to the gate as
voltage densities. The thermal channel noise is

$$S_{th} = \frac{4k_BT\gamma}{g_m}$$

and the flicker noise is

$$S_{fl}(f) = \frac{K_f}{C_{ox}WLf}$$

both in V²/Hz. The corner frequency is where they are equal.
''',
                "steps": [
                    {
                        "prompt": "Set the two densities equal and solve for the corner frequency. Write $f_c$.",
                        "answer": "\\frac{K_f g_m}{4 k_B T \\gamma C_{ox} W L}",
                        "hint": "Put $f = f_c$ in the flicker expression, set it equal to the thermal one, then cross-multiply.",
                        "deconstruct": [
                            "$\\frac{K_f}{C_{ox}WLf_c} = \\frac{4k_BT\\gamma}{g_m}$.",
                            "Multiply both sides by $f_c$ and by $\\frac{g_m}{4k_BT\\gamma}$.",
                        ],
                    },
                    {
                        "prompt": "The two contributions are independent, so their power densities add. Write the total density $S(f)$ as a multiple of the thermal density — that is, write $S(f)/S_{th}$ in terms of $f$ and $f_c$.",
                        "answer": "1 + \\frac{f_c}{f}",
                        "hint": "By the definition of the corner, $S_{fl}(f) = S_{th} \\cdot f_c / f$.",
                        "deconstruct": [
                            "$S_{fl}(f_c) = S_{th}$, and $S_{fl}$ goes as $1/f$, so $S_{fl}(f) = S_{th}f_c/f$.",
                            "Add the thermal part and divide the whole thing by $S_{th}$.",
                        ],
                    },
                    {
                        "prompt": "The device is redrawn with both $W$ and $L$ doubled, and the bias adjusted so that $g_m$ is unchanged. By what factor is $f_c$ multiplied?",
                        "answer": "\\frac{1}{4}",
                        "hint": "Only the product $WL$ appears in the corner expression, and it is in the denominator.",
                        "deconstruct": [
                            "Doubling $W$ and $L$ multiplies the gate area $WL$ by four.",
                            "$f_c$ is inversely proportional to $WL$, so it falls by the same factor.",
                        ],
                    },
                    {
                        "prompt": "At $f = f_c$ exactly, the total *voltage* density is what multiple of the thermal voltage density?",
                        "answer": "\\sqrt{2}",
                        "hint": "Equal powers means the total power is twice the thermal power. Voltage density is the square root of power density.",
                        "deconstruct": [
                            "From the ratio you derived, $S(f_c)/S_{th} = 2$.",
                            "Take the square root to get back to V/√Hz.",
                        ],
                    },
                ],
                "closing": r'''
Two levers, and they cost different things. Area buys you a lower corner and costs
capacitance, which the previous stage has to drive. Transconductance buys you a lower
thermal floor and costs current — which also pushes the corner *up*, because the floor
it is measured against has just dropped. Neither lever moves one number in isolation.
''',
            },
            "blanks": {
                "title": "The corner, and why waiting stops helping",
                "minutes": 8,
                "caption": "flicker.py — one over f, one over area",
                "lang": "python",
                "brief": r"""
Below the flicker corner the spectrum is no longer flat, and one of the most reliable
instincts in measurement — average for longer — stops paying. Fill in why.
""",
                "listing": """# Gate-referred flicker density of a MOSFET:
#
#     S_fl(f) = K_f / (C_ox * W * L * ___ )
#
# The corner is where flicker equals the thermal contribution,
# which for a MOSFET referred to the gate is
#
#     S_th = ___
#
# Making the device physically larger moves the corner ___ .
#
# And averaging for longer stops helping below the corner because
# ___ .
""",
                "blanks": [
                    {
                        "prompt": "The defining dependence.",
                        "hole": "?",
                        "opts": ["f", "f ** 2", "sqrt(f)", "1"],
                        "a": 0,
                        "why": "One over $f$ — hence the name. It means the density is unbounded as $f \\to 0$, which sounds alarming and is not, because what any real measurement sees is the *integral* over a band, and $\\int df/f$ grows only logarithmically.",
                        "whys": [
                            "One over $f$ — hence the name. It means the density is unbounded as $f \\to 0$, which sounds alarming and is not, because what any real measurement sees is the *integral* over a band, and $\\int df/f$ grows only logarithmically.",
                            "$1/f^2$ is random-walk noise, a different and much more violent process. Real devices show slopes near 1, sometimes 0.9 or 1.2, but not 2.",
                            "A gentler slope than any measured device shows, and it would make flicker negligible far sooner than it is.",
                            "A constant is white noise, which is the thermal term this one is being compared against.",
                        ],
                    },
                    {
                        "prompt": "What is the flat floor it is being compared with?",
                        "hole": "?",
                        "opts": [
                            "4 * k * T * gamma / g_m",
                            "4 * k * T * R",
                            "K_f / (C_ox * W * L)",
                            "0",
                        ],
                        "a": 0,
                        "why": "A MOSFET's channel thermal noise referred back to the gate is $4k_BT\\gamma/g_m$, with $\\gamma$ around 2/3 for a long device. Referring it to the gate is what makes the comparison fair — both terms are then voltages at the same node, and the frequency where they cross is the corner.",
                        "whys": [
                            "A MOSFET's channel thermal noise referred back to the gate is $4k_BT\\gamma/g_m$, with $\\gamma$ around 2/3 for a long device. Referring it to the gate is what makes the comparison fair — both terms are then voltages at the same node, and the frequency where they cross is the corner.",
                            "That is a resistor's noise. The channel is a resistor of sorts, but it is not in equilibrium and the gate-referred form carries $1/g_m$ rather than $R$.",
                            "That is the flicker term with the $1/f$ removed, so comparing it against flicker would just give $f = 1$ Hz regardless of the device.",
                            "Zero would put the corner at infinity and make flicker the only noise at every frequency.",
                        ],
                    },
                    {
                        "prompt": "W and L both go up. Which way does the corner move?",
                        "hole": "?",
                        "opts": ["down in frequency", "up in frequency", "not at all", "down, but only if L is fixed"],
                        "a": 0,
                        "why": "Flicker density falls as $1/WL$, so a bigger device has less of it and the crossing with the flat thermal floor happens lower. This is the standard fix and it is expensive: area, and the capacitance that comes with it. It is why input devices in low-frequency analog are enormous compared with anything in a digital gate.",
                        "whys": [
                            "Flicker density falls as $1/WL$, so a bigger device has less of it and the crossing with the flat thermal floor happens lower. This is the standard fix and it is expensive: area, and the capacitance that comes with it. It is why input devices in low-frequency analog are enormous compared with anything in a digital gate.",
                            "Backwards: a larger gate averages over more trapping sites, which reduces flicker rather than increasing it.",
                            "$W$ and $L$ appear explicitly in the denominator of the flicker term, so the corner certainly moves.",
                            "Both dimensions appear as a product, so the area is what matters and there is nothing special about fixing $L$.",
                        ],
                    },
                    {
                        "prompt": "Why does a longer average stop paying?",
                        "hole": "?",
                        "opts": [
                            "every decade below the corner contributes the same noise power",
                            "the noise is white there, so it never averages down",
                            "the signal falls at the same rate",
                            "the corner itself moves during the measurement",
                        ],
                        "a": 0,
                        "why": "$\\int_{f}^{10f} df/f = \\ln 10$ whatever $f$ is — equal power per decade. Averaging longer opens the band downward by decades and each one hands back as much noise as the last, so the total creeps up logarithmically instead of falling. This is why slow drift cannot be averaged away, and why chopping and correlated double sampling exist: they move the signal up above the corner instead.",
                        "whys": [
                            "$\\int_{f}^{10f} df/f = \\ln 10$ whatever $f$ is — equal power per decade. Averaging longer opens the band downward by decades and each one hands back as much noise as the last, so the total creeps up logarithmically instead of falling. This is why slow drift cannot be averaged away, and why chopping and correlated double sampling exist: they move the signal up above the corner instead.",
                            "It is the opposite of white — white noise is exactly the case where averaging *does* work, falling as the square root of the time.",
                            "The signal is a DC quantity and does not fall with frequency; if it did, no measurement technique would help.",
                            "The corner is a property of the device and the bias, not of how long you look.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Fit a corner frequency to a measured spectrum",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
You are handed a measured noise density and asked for the two numbers that describe
it. Model the density as

```text
d(f) = nth * sqrt(1 + fc / f)
```

- `density(f, nth, fc)` evaluates that model. It must accept a numpy array of
  frequencies and return an array.
- `fit_corner(f, d)` recovers `(nth, fc)` from data. The trick is that the *squared*
  density is linear in $1/f$: $d^2 = a + b/f$ with $a = n_{th}^2$ and $b = a f_c$. Build
  the two-column design matrix `[ones, 1/f]`, solve with `np.linalg.lstsq`, then
  convert back.
- `integrated_rms(nth, fc, f1, f2)` returns the r.m.s. volts between two frequencies.
  The thermal part contributes $n_{th}^2(f_2-f_1)$ and the flicker part contributes
  $n_{th}^2 f_c \ln(f_2/f_1)$.
- `flicker_fraction(nth, fc, f1, f2)` returns the share of the *mean square* that comes
  from the flicker term. It should be near one well below the corner and near zero well
  above it.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def density(f, nth, fc):
    """Total voltage noise density at each frequency in f, in V/sqrt(Hz)."""
    f = np.asarray(f, dtype=float)
    # TODO: nth * sqrt(1 + fc / f)
    return np.zeros_like(f)


def fit_corner(f, d):
    """Recover (nth, fc) from a measured density curve by least squares on d**2."""
    f = np.asarray(f, dtype=float)
    d = np.asarray(d, dtype=float)
    # TODO: d**2 = a + b/f is linear. Build [ones, 1/f], solve, then
    # nth = sqrt(a) and fc = b / a.
    return 0.0, 0.0


def integrated_rms(nth, fc, f1, f2):
    """RMS volts of the total density between f1 and f2."""
    # TODO: thermal part is nth**2 * (f2 - f1); flicker part is nth**2 * fc * ln(f2/f1).
    return 0.0


def flicker_fraction(nth, fc, f1, f2):
    """Share of the mean-square noise between f1 and f2 that is flicker noise."""
    # TODO: flicker mean square over total mean square.
    return 0.0


if __name__ == "__main__":
    f = np.logspace(1, 7, 400)
    d = density(f, 8e-9, 1e4)
    print("fitted:", fit_corner(f, d))
    print("1 Hz to 10 Hz  :", integrated_rms(8e-9, 1e4, 1.0, 10.0))
    print("100 kHz to 1 MHz:", integrated_rms(8e-9, 1e4, 1e5, 1e6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def density(f, nth, fc):
    """Total voltage noise density at each frequency in f, in V/sqrt(Hz)."""
    f = np.asarray(f, dtype=float)
    return nth * np.sqrt(1.0 + fc / f)


def fit_corner(f, d):
    """Recover (nth, fc) from a measured density curve by least squares on d**2."""
    f = np.asarray(f, dtype=float)
    d = np.asarray(d, dtype=float)
    A = np.column_stack([np.ones_like(f), 1.0 / f])
    a, b = np.linalg.lstsq(A, d ** 2, rcond=None)[0]
    return float(np.sqrt(a)), float(b / a)


def integrated_rms(nth, fc, f1, f2):
    """RMS volts of the total density between f1 and f2."""
    ms = nth ** 2 * ((f2 - f1) + fc * np.log(f2 / f1))
    return float(np.sqrt(ms))


def flicker_fraction(nth, fc, f1, f2):
    """Share of the mean-square noise between f1 and f2 that is flicker noise."""
    ms_flicker = fc * np.log(f2 / f1)
    ms_thermal = f2 - f1
    return float(ms_flicker / (ms_flicker + ms_thermal))


if __name__ == "__main__":
    f = np.logspace(1, 7, 400)
    d = density(f, 8e-9, 1e4)
    print("fitted:", fit_corner(f, d))
    print("1 Hz to 10 Hz  :", integrated_rms(8e-9, 1e4, 1.0, 10.0))
    print("100 kHz to 1 MHz:", integrated_rms(8e-9, 1e4, 1e5, 1e6))
'''}],
                "hints": [
                    "`nth * np.sqrt(1.0 + fc / f)` works elementwise once `f` is an array.",
                    "`np.column_stack([np.ones_like(f), 1.0 / f])` builds the design matrix; `np.linalg.lstsq(A, d**2, rcond=None)[0]` returns `[a, b]`.",
                    "The corner falls straight out of the fit as `b / a` — the ratio of the $1/f$ coefficient to the flat one.",
                    "`np.log` is the natural logarithm. Using `np.log10` here gives an answer 2.3 times too small in mean square.",
                ],
                "tests": [
                    {"name": "the density is root two times the floor at the corner", "code": r'''
import numpy as np
_r = float(density(1e4, 8e-9, 1e4)) / 8e-9
assert abs(_r - 1.4142135623730951) < 1e-9, \
    f"equal powers means sqrt(2) in voltage density, not 2; you got a ratio of {_r:.4f}"
'''},
                    {"name": "the density is an array in and an array out", "code": r'''
import numpy as np
_f = np.logspace(1, 7, 400)
_d = density(_f, 8e-9, 1e4)
assert np.asarray(_d).shape == (400,), f"expected 400 values back, got shape {np.asarray(_d).shape}"
assert _d[0] > _d[-1], "the density must fall with frequency; if it is flat you have dropped the fc/f term"
assert abs(float(_d[-1]) / 8e-9 - 1.0) < 0.01, \
    "ten megahertz is far above the corner, so the density there should be the thermal floor"
'''},
                    {"name": "the fit recovers a clean curve exactly", "code": r'''
import numpy as np
_f = np.logspace(1, 7, 400)
_d = density(_f, 8e-9, 1e4)
_nth, _fc = fit_corner(_f, _d)
assert abs(_nth - 8e-9) < 1e-11, f"the flat coefficient is nth**2, so nth should be 8.0 nV/rtHz; got {_nth:.4e}"
assert abs(_fc - 1e4) < 5.0, f"the corner is b/a = 10000 Hz; got {_fc:.1f} Hz"
'''},
                    {"name": "the fit survives one per cent measurement noise", "code": r'''
import numpy as np
_f = np.logspace(1, 7, 400)
_rng = np.random.default_rng(3)
_d = density(_f, 8e-9, 1e4) * (1.0 + 0.01 * _rng.standard_normal(_f.size))
_nth, _fc = fit_corner(_f, _d)
assert abs(_nth / 8e-9 - 1.0) < 0.10, \
    f"a one per cent scatter should not move the floor by more than ten per cent; got {_nth:.4e}"
assert abs(_fc / 1e4 - 1.0) < 0.20, \
    f"the corner is the least well determined number in the fit, but it should stay within twenty per cent; got {_fc:.1f} Hz"
'''},
                    {"name": "well above the corner the answer is the flat one", "code": r'''
import numpy as np
_v = integrated_rms(8e-9, 1e4, 1e5, 1e6)
assert abs(_v - 7.685938749399204e-06) < 1e-11, \
    f"expected 7.686 uV rms between 100 kHz and 1 MHz; got {_v:.4e} V"
_flat = 8e-9 * np.sqrt(9e5)
assert _v / _flat < 1.02, \
    "this band is ten decades above nothing but one decade above the corner, so flicker should add only about one per cent"
'''},
                    {"name": "a decade at the bottom of the spectrum is nearly all flicker", "code": r'''
_v = integrated_rms(8e-9, 1e4, 1.0, 10.0)
assert abs(_v - 1.2141789240125153e-06) < 1e-12, \
    f"expected 1.214 uV rms between 1 Hz and 10 Hz; got {_v:.4e} V"
_frac = flicker_fraction(8e-9, 1e4, 1.0, 10.0)
assert _frac > 0.99, \
    f"nine hertz of thermal noise is nothing against four decades below the corner; expected a flicker share above 0.99, got {_frac:.4f}"
'''},
                    {"name": "the flicker share collapses above the corner", "code": r'''
_frac = flicker_fraction(8e-9, 1e4, 1e5, 1e6)
assert abs(_frac - 0.02494605205990939) < 1e-9, \
    f"between 100 kHz and 1 MHz flicker is about 2.5 per cent of the mean square; got {_frac:.4f}"
'''},
                    {"name": "extending the band upward costs more than extending it downward", "code": r'''
_up = integrated_rms(8e-9, 1e4, 1e5, 2e6) / integrated_rms(8e-9, 1e4, 1e5, 1e6)
_down = integrated_rms(8e-9, 1e4, 10.0, 1e6) / integrated_rms(8e-9, 1e4, 100.0, 1e6)
assert 1.40 < _up < 1.50, \
    f"doubling the top of the band should raise the r.m.s. by roughly sqrt(2); got {_up:.4f}"
assert _down < 1.05, \
    f"a whole extra decade at the bottom adds only a logarithm, so under five per cent; got {_down:.4f}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Input-referred noise, noise figure and the Friis cascade",
            "summary": "Divide everything by the gain in front of it, and the first stage turns out to be the only one you can afford to get wrong.",
            "concepts": [
                "Noise referred to the input is the only fair comparison: output noise alone says nothing without the gain.",
                "Noise factor $F$ is the ratio of input signal-to-noise to output signal-to-noise; noise figure is $10\\log_{10}F$ in dB.",
                "Friis: $F = F_1 + \\frac{F_2-1}{G_1} + \\frac{F_3-1}{G_1G_2} + \\dots$, with every $F$ and $G$ in linear power terms.",
                "Equivalent noise temperature $T_e = T_0(F-1)$ — the same statement, in the units satellite and radio-astronomy work uses.",
                "Ordering matters: a low-noise, high-gain stage first can rescue a cascade that is otherwise dominated by a lossy mixer.",
            ],
            "sandbox": {
                "title": "The gain that decides whether the next stage matters",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 0.7, "K": 10},
                "brief": r'''
This is the magnitude and phase of a first stage, not a noise plot. Read it as the
$G_1$ in the Friis formula, plotted against frequency.

Everything the second stage contributes gets divided by whatever this curve is doing at
that frequency. Where the curve is high, the rest of the chain is invisible. Where it
has rolled off, the rest of the chain is all you have.
''',
                "notice": [
                    "Raise $K$ from 10 to 20. In the flat region the second stage's contribution to $F$ is halved, because $(F_2-1)/G_1$ is now divided by twice as much.",
                    "Look at the magnitude one decade above the corner. This response falls at 40 dB per decade, so $G_1$ there is ten thousand times smaller and the second stage is ten thousand times more important — this is why an amplifier's noise figure degrades at the top of its band.",
                    "Set $\\zeta$ to 0.1 and find the peak. A resonant gain peak makes the second stage locally negligible, and then the noise figure gets sharply worse either side of it.",
                    "Drop $K$ to 1. With no gain in the first stage, Friis collapses to $F_1 + F_2 - 1$ and the second stage contributes in full — the argument for putting the LNA first, in one slider.",
                ],
            },
            "derive": {
                "title": "Friis, from the definition of noise factor",
                "minutes": 14,
                "vars": ["F", "F_1", "F_2", "G", "G_1", "N_i", "N_a", "T_e", "T_e1", "T_e2", "T_0"],
                "brief": r'''
A two-port has available power gain $G$ and adds its own noise power $N_a$ at the
output. Its input carries signal power $S_i$ and noise power $N_i$, where $N_i$ is the
noise of a source at the reference temperature.

Noise factor is defined as

$$F = \frac{S_i/N_i}{S_o/N_o}$$

Everything below follows from that line and from $N_o = GN_i + N_a$.
''',
                "steps": [
                    {
                        "prompt": "The output signal is $S_o = GS_i$ and the output noise is $N_o = GN_i + N_a$. Substitute both into the definition and write $F$ in terms of $G$, $N_i$ and $N_a$.",
                        "answer": "1 + \\frac{N_a}{G N_i}",
                        "hint": "The signal powers cancel completely, which is the point: $F$ is a property of the two-port, not of what you put through it.",
                        "deconstruct": [
                            "$F = \\frac{S_i}{N_i}\\cdot\\frac{N_o}{S_o} = \\frac{S_i(GN_i+N_a)}{N_iGS_i}$.",
                            "Cancel $S_i$ and split the fraction into two terms.",
                        ],
                    },
                    {
                        "prompt": "Now cascade two such stages. The second stage's own added noise, referred back to the input of the first, is divided by $G_1$. Write the cascade noise factor $F$ in terms of $F_1$, $F_2$ and $G_1$.",
                        "given": "From the previous step, stage two on its own contributes an input-referred excess of $F_2 - 1$ relative to $N_i$.",
                        "answer": "F_1 + \\frac{F_2 - 1}{G_1}",
                        "hint": "Excess noise factors add once each has been divided by all the gain that precedes it. The first stage has no gain in front of it.",
                        "deconstruct": [
                            "Stage one contributes $F_1$, which already includes the source noise.",
                            "Stage two contributes an excess $F_2 - 1$, seen through $G_1$ of gain.",
                        ],
                    },
                    {
                        "prompt": "The same information is often carried as an equivalent noise temperature, defined by $F = 1 + T_e/T_0$. Write $T_e$ in terms of $F$ and $T_0$.",
                        "answer": "T_0 \\left( F - 1 \\right)",
                        "placeholder": "T_0 (F - 1)",
                        "hint": "Rearrange the defining relation — one subtraction and one multiplication.",
                        "deconstruct": [
                            "$F - 1 = T_e/T_0$.",
                            "Multiply both sides by $T_0$.",
                        ],
                    },
                    {
                        "prompt": "Rewrite the two-stage cascade in temperatures. Write the cascade $T_e$ in terms of $T_{e1}$, $T_{e2}$ and $G_1$.",
                        "answer": "T_{e1} + \\frac{T_{e2}}{G_1}",
                        "hint": "Substitute $F_i = 1 + T_{ei}/T_0$ into the Friis expression; every stray 1 cancels.",
                        "deconstruct": [
                            "$F = 1 + T_{e1}/T_0 + \\frac{(1 + T_{e2}/T_0) - 1}{G_1}$.",
                            "The $-1$ removes the extra unity, leaving $T_e/T_0 = T_{e1}/T_0 + T_{e2}/(T_0G_1)$.",
                        ],
                    },
                ],
                "closing": r'''
The temperature form is the cleaner one: no stray ones, and excess temperatures divide
by preceding gain in the obvious way. It is also the form that makes the design rule
unavoidable. A 20 dB first stage divides everything behind it by a hundred, so a mixer
with a 9 dB noise figure can sit behind a 1.4 dB LNA and cost you only a few tenths of
a decibel — but put the same mixer first, and nothing downstream can ever repair it.
''',
            },
            "quiz": {
                "title": "Friis, and why only the first stage matters",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why is noise always referred to the input?",
                        "opts": [
                            "Output noise alone says nothing until you know the gain that produced it",
                            "Because the input impedance is known",
                            "Because noise is generated only at the input",
                            "It is a convention with no technical content",
                        ],
                        "a": 0,
                        "why": r"""
An amplifier with 100 dB of gain has enormous output noise and may be exquisitely quiet;
one with 0 dB has almost none and may be dreadful. Dividing by the gain removes the
question of how much amplification happened and leaves the only thing that matters: how
much noise the stage added, in the same units as the signal it was handed. Noise is
generated throughout the circuit — referring it to the input is a bookkeeping choice
that makes comparison possible.
""",
                    },
                    {
                        "q": "What is the noise factor $F$ of a perfectly noiseless amplifier?",
                        "opts": ["1, which is 0 dB", "0, which is $-\\infty$ dB", "$\\infty$", "It depends on the gain"],
                        "a": 0,
                        "why": r"""
$F$ is the ratio of input SNR to output SNR, so a stage that adds nothing leaves the SNR
alone and scores exactly 1. It can never be less than 1 — an amplifier cannot improve the
signal-to-noise ratio of what it is given, because it amplifies the source's own noise
along with the signal. A quoted noise figure below 0 dB is a measurement error, not a
breakthrough.
""",
                    },
                    {
                        "q": "In $F = F_1 + \\frac{F_2-1}{G_1} + \\dots$, what divides the second stage's contribution?",
                        "opts": [
                            "The first stage's available gain",
                            "The first stage's noise factor",
                            "The total gain of the chain",
                            "The bandwidth",
                        ],
                        "a": 0,
                        "why": r"""
$G_1$, and that division is the whole content of Friis. By the time the signal reaches
stage 2 it has been amplified, so stage 2's own noise is measured against a much larger
signal and matters proportionally less. With 20 dB in the first stage, the second's
excess noise is divided by 100 — which is why the front end gets the expensive
low-noise device and the rest of the chain does not.
""",
                    },
                    {
                        "q": "An LNA with 10 dB gain and 1 dB noise figure feeds a mixer with a 10 dB noise figure. What is the cascade noise figure, roughly?",
                        "opts": ["About 3.3 dB", "About 1 dB", "About 5.5 dB", "About 11 dB"],
                        "a": 0,
                        "why": r"""
In linear terms: $F_1 = 1.26$, $F_2 = 10$, $G_1 = 10$, so
$F = 1.26 + 9/10 = 2.16$, which is 3.3 dB. Two things are worth noticing. The mixer's
dreadful 10 dB has been reduced to a 2 dB penalty by the LNA in front of it — and it is
still the *larger* of the two contributions, because 10 dB of gain is not much. Push the
LNA to 20 dB and the cascade drops to about 1.6 dB.
""",
                    },
                    {
                        "q": "A colleague proposes putting a lossy filter before the LNA. What does Friis say?",
                        "opts": [
                            "Its loss adds to the system noise figure almost decibel for decibel",
                            "It has no effect, since it is passive",
                            "It helps, by rejecting out-of-band noise",
                            "It only matters if it is narrower than the signal",
                        ],
                        "a": 0,
                        "why": r"""
A passive lossy element at the front has a noise factor equal to its loss and a gain
equal to its inverse, so 2 dB of insertion loss is 2 dB straight onto the system figure —
with no amplification in front of it to divide the penalty down. This is the single most
consequential practical reading of Friis, and it is why front-end filter loss is fought
over so hard. The filter may still be necessary for other reasons; it is simply never
free.
""",
                    },
                ],
            },
            "lab": {
                "title": "Cascade a receiver and find the ordering that wins",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Stages are described as `(nf_db, gain_db)` pairs, both in power decibels.

- `db_to_lin(x)` and `lin_to_db(x)` — the $10^{x/10}$ conversions. Everything in Friis
  happens in linear power; converting at the wrong moment is the classic error here.
- `friis(stages)` returns `(nf_db_total, gain_db_total)` for a list of stages, in that
  order. Accumulate `F` and `G` in linear terms and convert once at the end.
- `noise_temperature(nf_db, T0)` returns $T_0(F-1)$ in kelvin.
- `input_referred_density(output_density, gain_db)` divides an output V/√Hz by the
  *voltage* gain. The decibels are power decibels, so the voltage gain is the square
  root of the linear power gain.
- `best_order(stages)` returns the ordering with the lowest cascade noise figure, as a
  list. With a handful of stages, `itertools.permutations` is entirely adequate.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np
from itertools import permutations


def db_to_lin(x):
    """Power decibels to a linear power ratio."""
    # TODO
    return 1.0


def lin_to_db(x):
    """Linear power ratio to power decibels."""
    # TODO
    return 0.0


def friis(stages):
    """Cascade noise figure and gain, both in dB, for stages in the given order."""
    # TODO: accumulate F and G linearly, then convert.
    return 0.0, 0.0


def noise_temperature(nf_db, T0=290.0):
    """Equivalent noise temperature in kelvin."""
    # TODO
    return 0.0


def input_referred_density(output_density, gain_db):
    """Refer an output voltage density back to the input, in V/sqrt(Hz)."""
    # TODO: divide by the voltage gain, not the power gain.
    return 0.0


def best_order(stages):
    """The ordering of stages with the lowest cascade noise figure."""
    # TODO
    return list(stages)


if __name__ == "__main__":
    chain = [(1.5, 20.0), (8.0, 10.0), (12.0, 25.0)]
    print("as given:", friis(chain))
    print("best    :", best_order(chain))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np
from itertools import permutations


def db_to_lin(x):
    """Power decibels to a linear power ratio."""
    return 10.0 ** (float(x) / 10.0)


def lin_to_db(x):
    """Linear power ratio to power decibels."""
    return float(10.0 * np.log10(x))


def friis(stages):
    """Cascade noise figure and gain, both in dB, for stages in the given order."""
    F = 1.0
    G = 1.0
    for nf_db, g_db in stages:
        F += (db_to_lin(nf_db) - 1.0) / G
        G *= db_to_lin(g_db)
    return lin_to_db(F), lin_to_db(G)


def noise_temperature(nf_db, T0=290.0):
    """Equivalent noise temperature in kelvin."""
    return float(T0 * (db_to_lin(nf_db) - 1.0))


def input_referred_density(output_density, gain_db):
    """Refer an output voltage density back to the input, in V/sqrt(Hz)."""
    return float(output_density / np.sqrt(db_to_lin(gain_db)))


def best_order(stages):
    """The ordering of stages with the lowest cascade noise figure."""
    return list(min(permutations(stages), key=lambda p: friis(list(p))[0]))


if __name__ == "__main__":
    chain = [(1.5, 20.0), (8.0, 10.0), (12.0, 25.0)]
    print("as given:", friis(chain))
    print("best    :", best_order(chain))
'''}],
                "hints": [
                    "`db_to_lin` is `10.0 ** (x / 10.0)` and `lin_to_db` is `10.0 * np.log10(x)` — power decibels throughout, so the factor is ten, not twenty.",
                    "In the Friis loop, add `(F_stage - 1) / G` *before* multiplying `G` by this stage's gain: the excess is divided by the gain that precedes it, not including it.",
                    "A power gain of 20 dB is a linear power ratio of 100 and a voltage gain of 10.",
                    "`min(permutations(stages), key=...)` does the ordering search in one line.",
                ],
                "tests": [
                    {"name": "the decibel conversions are power decibels and invert each other", "code": r'''
assert abs(db_to_lin(20.0) - 100.0) < 1e-9, \
    f"20 power-dB is a linear ratio of 100, not 10; you returned {db_to_lin(20.0)}"
assert abs(db_to_lin(3.0) - 1.9952623149688795) < 1e-9, \
    f"3 dB is 1.995 in power; you returned {db_to_lin(3.0)}"
assert abs(lin_to_db(db_to_lin(7.3)) - 7.3) < 1e-9, "the two conversions must be inverses"
'''},
                    {"name": "a single stage cascades to itself", "code": r'''
_nf, _g = friis([(3.0, 12.0)])
assert abs(_nf - 3.0) < 1e-9, f"one stage on its own has its own noise figure; got {_nf}"
assert abs(_g - 12.0) < 1e-9, f"one stage on its own has its own gain; got {_g}"
'''},
                    {"name": "a three stage receiver gives the Friis answer", "code": r'''
_nf, _g = friis([(1.5, 20.0), (8.0, 10.0), (12.0, 25.0)])
assert abs(_nf - 1.7040319341193924) < 1e-9, \
    f"expected a cascade noise figure of 1.704 dB; got {_nf:.4f} dB — check that you divide each excess by the gain in front of it"
assert abs(_g - 55.0) < 1e-9, f"gains in dB simply add: 20 + 10 + 25 = 55; got {_g}"
'''},
                    {"name": "the first stage dominates and the second barely registers", "code": r'''
_base = friis([(1.5, 20.0), (8.0, 10.0), (12.0, 25.0)])[0]
_worse2 = friis([(1.5, 20.0), (11.0, 10.0), (12.0, 25.0)])[0]
_worse1 = friis([(2.0, 20.0), (8.0, 10.0), (12.0, 25.0)])[0]
assert abs(_worse2 - _base) < 0.25, \
    f"three whole dB added to stage two should cost under 0.25 dB overall; got {_worse2 - _base:.3f} dB"
assert (_worse1 - _base) > 0.4, \
    f"half a dB on stage one should cost more than three dB on stage two; got {_worse1 - _base:.3f} dB"
'''},
                    {"name": "noise temperature matches the noise figure", "code": r'''
_t = noise_temperature(3.0, 290.0)
assert abs(_t - 288.62607134097505) < 1e-6, \
    f"T0*(F-1) with F = 1.995 gives 288.6 K; got {_t:.3f} K"
assert abs(noise_temperature(0.0, 290.0)) < 1e-9, \
    "a noiseless two-port has F = 1, so an equivalent noise temperature of zero"
'''},
                    {"name": "referring to the input divides by voltage gain", "code": r'''
_d = input_referred_density(1e-6, 20.0)
assert abs(_d - 1e-7) < 1e-12, \
    f"20 power-dB is a voltage gain of 10, so 1 uV/rtHz out is 100 nV/rtHz in; got {_d:.4e}"
'''},
                    {"name": "putting the quiet high-gain stage first wins", "code": r'''
_stages = [(6.0, 3.0), (2.0, 15.0), (10.0, 20.0)]
_as_given = friis(_stages)[0]
_best = best_order(_stages)
assert list(_best[0]) == [2.0, 15.0] or tuple(_best[0]) == (2.0, 15.0), \
    f"the 2 dB, 15 dB stage belongs at the front; your ordering starts with {_best[0]}"
assert abs(friis(_best)[0] - 2.605014949923054) < 1e-9, \
    f"the best ordering gives 2.605 dB; got {friis(_best)[0]:.4f} dB"
assert friis(_best)[0] < _as_given - 3.0, \
    f"reordering should save nearly 4 dB here; as given was {_as_given:.3f} dB"
'''},
                    {"name": "ordering never changes the total gain", "code": r'''
_stages = [(6.0, 3.0), (2.0, 15.0), (10.0, 20.0)]
assert abs(friis(best_order(_stages))[1] - friis(_stages)[1]) < 1e-9, \
    "gain in dB adds, so it is the same whatever the order — only the noise figure moves"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Noise bandwidth and the noise-power-bandwidth trade",
            "summary": "Noise does not stop at the 3 dB point. The number that matters is the area under the squared response.",
            "concepts": [
                "Equivalent noise bandwidth is $B_n = \\frac{1}{|H|^2_{max}}\\int_0^\\infty |H(f)|^2\\,df$ — the brick wall that would pass the same noise power.",
                "For one pole, $B_n = \\frac{\\pi}{2}f_{3dB}$: fifty-seven per cent more noise power than the 3 dB number suggests.",
                "Sharper filters converge on $B_n = f_{3dB}$ from above — $\\frac{\\pi}{2}$, then 1.111, then 1.047, for one, two and three Butterworth poles. Normalising by the peak rather than by the d.c. value pulls a resonant response the other way: at $\\zeta = 0.1$ a two-pole low-pass has $B_n = 0.29f_{3dB}$.",
                "The sampled noise on a capacitor is $\\sqrt{k_BT/C}$ — the resistance cancels, which is why kT/C is a capacitor specification and not a resistor one.",
                "Halving the r.m.s. noise costs four times the capacitance, and driving four times the capacitance at the same speed costs about four times the current.",
            ],
            "sandbox": {
                "title": "How much noise a filter shape lets through",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 0.5, "K": 1},
                "brief": r'''
Noise bandwidth is the area under $|H|^2$, so read the magnitude plot as an area rather
than as a curve. The 3 dB point tells you where the curve crosses a line; the noise
bandwidth tells you what is underneath it, including the whole tail.
''',
                "notice": [
                    "Take $\\zeta$ from 0.5 down to 0.1. The 3 dB frequency barely moves, but the resonant peak rises far faster than the area beneath it, and $B_n$ is the ratio of the two: it falls from about $1.0f_{3dB}$ to about $0.29f_{3dB}$. A peak makes a filter quiet only by the yardstick it is measured against.",
                    "Take $\\zeta$ up to 1.5. The response becomes two well-separated real poles and the absolute area collapses, but $f_{3dB}$ collapses faster, so $B_n/f_{3dB}$ climbs to about 1.4 — further from the brick wall than the Butterworth case, not closer.",
                    "Change $K$ alone. The area under $|H|^2$ scales with $K^2$, but noise bandwidth does not change at all — it is defined relative to the peak, so a gain change moves the noise and the signal together.",
                    "Slide $\\omega_n$ from 20 to 40. Every bit of area doubles, so the noise power doubles and the r.m.s. noise rises by $\\sqrt{2}$. That is the bandwidth half of the trade, in one slider.",
                ],
            },
            "derive": {
                "title": "The noise bandwidth of one pole, and where kT/C comes from",
                "minutes": 13,
                "vars": ["f", "f_0", "B_n", "R", "C", "k_B", "T"],
                "brief": r'''
An RC low-pass has

$$|H(f)|^2 = \frac{1}{1 + \left( f/f_0 \right)^2}, \qquad f_0 = \frac{1}{2\pi RC}$$

and its equivalent noise bandwidth is the area underneath, since the peak value is one:

$$B_n = \int_0^{\infty} |H(f)|^2\,df$$

You are given the value of that integral; the interesting part is what it turns into.
''',
                "steps": [
                    {
                        "prompt": "Using the given integral, write $B_n$ in terms of $f_0$.",
                        "given": "$\\int_0^{\\infty} \\frac{df}{1 + \\left( f/f_0 \\right)^2} = \\frac{\\pi}{2} f_0$.",
                        "answer": "\\frac{\\pi}{2} f_0",
                        "hint": "The peak of $|H|^2$ is one, so no normalisation is needed and the integral is the answer.",
                        "deconstruct": [
                            "$B_n$ is defined as the integral divided by the peak of $|H|^2$.",
                            "That peak is one at $f = 0$, so $B_n$ is the integral itself.",
                        ],
                    },
                    {
                        "prompt": "Substitute $f_0 = \\frac{1}{2\\pi RC}$ and write $B_n$ in terms of $R$ and $C$ alone.",
                        "answer": "\\frac{1}{4 R C}",
                        "hint": "The $\\pi$ from the integral and the $\\pi$ in $f_0$ cancel exactly. That cancellation is the whole reason kT/C is such a clean result.",
                        "deconstruct": [
                            "$B_n = \\frac{\\pi}{2}\\cdot\\frac{1}{2\\pi RC}$.",
                            "The $\\pi$ cancels and $2 \\times 2 = 4$ stays in the denominator.",
                        ],
                    },
                    {
                        "prompt": "The resistor's density is $4k_BTR$ in V²/Hz, and the filter passes $B_n$ of it. Write the total mean-square output noise voltage.",
                        "answer": "\\frac{k_B T}{C}",
                        "hint": "Multiply the density by the noise bandwidth you just derived, and watch what happens to $R$.",
                        "deconstruct": [
                            "$\\overline{v_o^2} = 4k_BTR \\cdot \\frac{1}{4RC}$.",
                            "The 4 and the $R$ both cancel.",
                        ],
                    },
                    {
                        "prompt": "A designer holds $T$ fixed and multiplies $C$ by four. By what factor is the r.m.s. output noise voltage multiplied?",
                        "answer": "\\frac{1}{2}",
                        "hint": "The mean square goes as $1/C$, and r.m.s. is its square root.",
                        "deconstruct": [
                            "Mean square is $k_BT/C$, so four times the capacitance is a quarter of the mean square.",
                            "The square root of a quarter is a half.",
                        ],
                    },
                ],
                "closing": r'''
The resistance vanished, which is the surprising part: you cannot make a sampled node
quieter by choosing a better switch. Only the capacitor sets the noise, and it sets it
as $1/\sqrt{C}$ — so each further factor of two in noise costs four times the
capacitance, and roughly four times the current to drive it at the same settling speed.
That quadratic wall is the reason precision converters are expensive.
''',
            },
            "build": {
                "title": "Let the check do the integral",
                "minutes": 24,
                "brief": r"""
Equivalent noise bandwidth is defined by an integral:

$$B_n = \frac{1}{|H|^2_{max}}\int_0^{\infty}|H(f)|^2\,df$$

which is a rectangle of the same area as the whole squared response. Nothing about that
definition mentions the $-3$ dB point, and the number it produces is not the $-3$ dB
point — a fact that is easy to nod at and hard to believe until you have watched the
area accumulate past the corner.

## What to build

A one-pole RC low-pass with $f_{3dB} = 1.00$ MHz, probed across the capacitor. The
**1 kΩ resistor is on the canvas**; choose the capacitor.

## What the checks do

The third check evaluates $|H(f)|$ at four thousand frequencies out to 400 MHz and
trapezoidally integrates $|H|^2$. It is doing the definition, numerically, on the
circuit you drew. Then it compares the answer with $\tfrac{\pi}{2}f_{3dB}$.

The result is $1.571$ MHz — **fifty-seven per cent more noise power** than a designer
who stopped at the corner frequency would have budgeted for. That surplus is entirely
in the tail: past the corner the response is falling at 20 dB per decade, which is not
nearly fast enough to stop contributing.

## Why $\pi/2$, and why only here

$\int_0^{\infty}\frac{df}{1+(f/f_c)^2} = \frac{\pi}{2}f_c$ — the integral of a
Lorentzian, and the $\pi$ arrives from $\arctan$. It is specific to one pole. Two poles
bring the ratio down to about 1.11, and a brick wall would give exactly 1. Sharper
filters converge on $B_n = f_{3dB}$ from above, and never from below: the noise
bandwidth of a real filter is always the wider number.
""",
                "start": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "r", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 1000},
                        {"id": "g1", "kind": "GND", "x": 10, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 10, "y": 5},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]},
                        {"a": [2, 5], "b": [5, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "r", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 1000},
                        {"id": "c", "kind": "C", "x": 10, "y": 7, "rot": 1, "value": 159.155e-12},
                        {"id": "g1", "kind": "GND", "x": 10, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 10, "y": 5},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]},
                        {"a": [2, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [10, 5]},
                        {"a": [10, 5], "b": [10, 6]},
                        {"a": [10, 8], "b": [10, 9]},
                    ],
                },
                "checks": [
                    {
                        "name": "one pole, unity gain at DC",
                        "code": r"""
c.assert(c.count('R') === 1, 'One resistor; there are ' + c.count('R') + '.');
c.assert(c.count('C') === 1, 'One capacitor; there are ' + c.count('C') + '.');
c.assert(c.count('L') === 0, 'No inductors — this is deliberately a single-pole filter.');
c.close(c.vout(), 1.0, 0.01,
  'the output at DC. The capacitor draws no current there, so no voltage is dropped ' +
  'across the resistor and the whole source appears at the probe');
""",
                    },
                    {
                        "name": "the corner is at 1.00 MHz",
                        "code": r"""
const f3 = c.corner(1e3, 1e9);
c.close(f3, 1.0e6, 0.03,
  'the measured -3 dB frequency. With R fixed at 1 kohm this is a statement about C ' +
  'alone: C = 1/(2*pi*R*f_3dB)');
""",
                    },
                    {
                        "name": "the integral of |H|^2 comes to 1.571 MHz",
                        "code": r"""
/* the definition, evaluated on the circuit you drew */
const hmax = c.vout();
const N = 4000, fmax = 400e6, df = fmax / N;
let area = 0, prev = hmax * hmax;
for (let i = 1; i <= N; i++) {
  const g = c.gain(i * df);
  const cur = g * g;
  area += 0.5 * (prev + cur) * df;
  prev = cur;
}
const bn = area / (hmax * hmax);
c.close(bn, 1.5708e6, 0.04,
  'the equivalent noise bandwidth, integrated numerically out to 400 MHz. For one ' +
  'pole it is (pi/2) * f_3dB. If this comes out near f_3dB itself the response is ' +
  'falling far faster than one pole, which means there is a second reactance in there');
""",
                    },
                    {
                        "name": "and it is 57% more than the corner frequency",
                        "code": r"""
const f3 = c.corner(1e3, 1e9);
const hmax = c.vout();
const N = 2000, fmax = 400e6, df = fmax / N;
let area = 0, prev = hmax * hmax;
for (let i = 1; i <= N; i++) {
  const g = c.gain(i * df);
  const cur = g * g;
  area += 0.5 * (prev + cur) * df;
  prev = cur;
}
const ratio = (area / (hmax * hmax)) / f3;
c.close(ratio, Math.PI / 2, 0.05,
  'the ratio B_n / f_3dB. This is the number worth carrying away: budgeting noise at ' +
  'the corner frequency understates the power by a factor of pi/2, and the missing ' +
  '57% is all in the tail above the corner');
c.assert(ratio > 1.4,
  'B_n came out at ' + ratio.toFixed(3) + ' times f_3dB. For a single pole it must be ' +
  'noticeably greater than 1 — the response past the corner falls at only 20 dB per ' +
  'decade and keeps contributing area for decades.');
""",
                    },
                ],
                "hints": [
                    "$C = 1/(2\\pi R f_{3dB})$ with $R = 1$ kΩ and $f_{3dB} = 1$ MHz. The answer is about 159 pF, and the 159 is $10^6/2\\pi$ — a number worth recognising.",
                    "The capacitor goes from the output node to ground, not in series with the resistor.",
                    "The probe belongs on the node between the resistor and the capacitor, which is the filter's output.",
                ],
            },
            "lab": {
                "title": "Noise bandwidth by integration, and kT/C",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Compute noise bandwidth numerically for any response, then confirm the closed forms.

- `trapz_area(x, y)` — the trapezium rule over a possibly non-uniform grid. Write it
  out with `np.diff`; do not reach for a library routine.
- `noise_bandwidth(f, h2)` — the area under `h2` divided by its maximum value. `h2` is
  $|H(f)|^2$, a power response, already squared.
- `rc_h2(f, R, C)` — the one-pole response $\frac{1}{1+(f/f_0)^2}$ with
  $f_0 = \frac{1}{2\pi RC}$.
- `rc_noise_bandwidth(R, C)` — the closed form $\frac{1}{4RC}$.
- `ktc_rms(C, T)` — $\sqrt{k_BT/C}$.
- `output_rms(R, C, T)` — the r.m.s. output noise computed the long way, as the
  resistor's density times the square root of the noise bandwidth. It must agree with
  `ktc_rms` and must not depend on `R` at all.

The checks integrate on a log-spaced grid spanning nine decades, so the truncation
error is well under a tenth of a per cent.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

K_B = 1.380649e-23   # J/K


def trapz_area(x, y):
    """Trapezium-rule area under y(x) on a possibly non-uniform grid."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    # TODO: sum of np.diff(x) times the average of adjacent y values.
    return 0.0


def noise_bandwidth(f, h2):
    """Equivalent noise bandwidth of a power response |H|^2 sampled on f."""
    # TODO: area under h2, divided by the peak of h2.
    return 0.0


def rc_h2(f, R, C):
    """|H(f)|^2 of a one-pole RC low-pass."""
    f = np.asarray(f, dtype=float)
    # TODO: f0 = 1 / (2 pi R C), then 1 / (1 + (f/f0)**2).
    return np.zeros_like(f)


def rc_noise_bandwidth(R, C):
    """Closed-form noise bandwidth of the one-pole RC, in Hz."""
    # TODO
    return 0.0


def ktc_rms(C, T=290.0):
    """RMS sampled noise voltage on a capacitor, in volts."""
    # TODO
    return 0.0


def output_rms(R, C, T=290.0):
    """RMS output noise the long way: resistor density times sqrt(noise bandwidth)."""
    # TODO
    return 0.0


if __name__ == "__main__":
    R, C = 1e4, 1e-10
    f0 = 1.0 / (2.0 * np.pi * R * C)
    grid = np.logspace(np.log10(f0) - 4, np.log10(f0) + 5, 200001)
    print("f0        :", round(f0, 1), "Hz")
    print("Bn numeric:", round(noise_bandwidth(grid, rc_h2(grid, R, C)), 1), "Hz")
    print("Bn closed :", round(rc_noise_bandwidth(R, C), 1), "Hz")
    print("kT/C on 1 pF:", round(ktc_rms(1e-12) * 1e6, 2), "uV rms")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

K_B = 1.380649e-23   # J/K


def trapz_area(x, y):
    """Trapezium-rule area under y(x) on a possibly non-uniform grid."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return float(np.sum(np.diff(x) * 0.5 * (y[1:] + y[:-1])))


def noise_bandwidth(f, h2):
    """Equivalent noise bandwidth of a power response |H|^2 sampled on f."""
    h2 = np.asarray(h2, dtype=float)
    return trapz_area(f, h2) / float(np.max(h2))


def rc_h2(f, R, C):
    """|H(f)|^2 of a one-pole RC low-pass."""
    f = np.asarray(f, dtype=float)
    f0 = 1.0 / (2.0 * np.pi * R * C)
    return 1.0 / (1.0 + (f / f0) ** 2)


def rc_noise_bandwidth(R, C):
    """Closed-form noise bandwidth of the one-pole RC, in Hz."""
    return float(1.0 / (4.0 * R * C))


def ktc_rms(C, T=290.0):
    """RMS sampled noise voltage on a capacitor, in volts."""
    return float(np.sqrt(K_B * T / C))


def output_rms(R, C, T=290.0):
    """RMS output noise the long way: resistor density times sqrt(noise bandwidth)."""
    density = np.sqrt(4.0 * K_B * T * R)
    return float(density * np.sqrt(rc_noise_bandwidth(R, C)))


if __name__ == "__main__":
    R, C = 1e4, 1e-10
    f0 = 1.0 / (2.0 * np.pi * R * C)
    grid = np.logspace(np.log10(f0) - 4, np.log10(f0) + 5, 200001)
    print("f0        :", round(f0, 1), "Hz")
    print("Bn numeric:", round(noise_bandwidth(grid, rc_h2(grid, R, C)), 1), "Hz")
    print("Bn closed :", round(rc_noise_bandwidth(R, C), 1), "Hz")
    print("kT/C on 1 pF:", round(ktc_rms(1e-12) * 1e6, 2), "uV rms")
'''}],
                "hints": [
                    "`np.sum(np.diff(x) * 0.5 * (y[1:] + y[:-1]))` is the trapezium rule for a non-uniform grid, in one expression.",
                    "Dividing by `np.max(h2)` is what makes noise bandwidth independent of gain.",
                    "`rc_noise_bandwidth` is `1 / (4 * R * C)` — the two factors of $\\pi$ have already cancelled, so there is no $\\pi$ in the answer.",
                    "In `output_rms`, the $R$ must cancel: if your answer changes when you change $R$, you have squared or rooted the wrong thing.",
                ],
                "tests": [
                    {"name": "the trapezium rule integrates a straight line exactly", "code": r'''
import numpy as np
_x = np.linspace(0.0, 2.0, 5)
assert abs(trapz_area(_x, _x) - 2.0) < 1e-12, \
    f"the area under y = x from 0 to 2 is 2; got {trapz_area(_x, _x)}"
_xn = np.array([0.0, 0.5, 3.0])
assert abs(trapz_area(_xn, 2.0 * _xn) - 9.0) < 1e-12, \
    f"the rule must handle unequal spacing: expected 9.0, got {trapz_area(_xn, 2.0 * _xn)}"
'''},
                    {"name": "the numeric noise bandwidth matches one over four RC", "code": r'''
import numpy as np
_R, _C = 1e4, 1e-10
_f0 = 1.0 / (2.0 * np.pi * _R * _C)
_grid = np.logspace(np.log10(_f0) - 4, np.log10(_f0) + 5, 200001)
_bn = noise_bandwidth(_grid, rc_h2(_grid, _R, _C))
assert abs(_bn / 250000.0 - 1.0) < 0.005, \
    f"1/(4RC) is 250 kHz here; the integral gave {_bn:.1f} Hz — check that you divide by the peak of |H|^2"
assert abs(rc_noise_bandwidth(_R, _C) - 250000.0) < 1e-6, \
    f"the closed form is 1/(4RC) = 250000 Hz; got {rc_noise_bandwidth(_R, _C)}"
'''},
                    {"name": "one pole passes pi over two times its three decibel bandwidth", "code": r'''
import numpy as np
_R, _C = 1e4, 1e-10
_f0 = 1.0 / (2.0 * np.pi * _R * _C)
_grid = np.logspace(np.log10(_f0) - 4, np.log10(_f0) + 5, 200001)
_ratio = noise_bandwidth(_grid, rc_h2(_grid, _R, _C)) / _f0
assert abs(_ratio - np.pi / 2) < 0.005, \
    f"the ratio should be pi/2 = 1.5708, not 1 — the tail beyond the corner carries real noise; got {_ratio:.4f}"
'''},
                    {"name": "a sharper filter has a noise bandwidth closer to its corner", "code": r'''
import numpy as np
_f0 = 1e5
_grid = np.logspace(np.log10(_f0) - 4, np.log10(_f0) + 5, 200001)
_second = 1.0 / (1.0 + (_grid / _f0) ** 4)
_ratio = noise_bandwidth(_grid, _second) / _f0
assert abs(_ratio - 1.1107) < 0.01, \
    f"a two-pole Butterworth gives Bn = 1.111 f_3dB, tighter than the one-pole 1.571; got {_ratio:.4f}"
'''},
                    {"name": "gain does not change noise bandwidth", "code": r'''
import numpy as np
_f0 = 1e5
_grid = np.logspace(np.log10(_f0) - 4, np.log10(_f0) + 5, 20001)
_h2 = 1.0 / (1.0 + (_grid / _f0) ** 2)
_a = noise_bandwidth(_grid, _h2)
_b = noise_bandwidth(_grid, 400.0 * _h2)
assert abs(_a / _b - 1.0) < 1e-9, \
    "noise bandwidth is normalised by the peak, so a 26 dB gain change must leave it untouched"
'''},
                    {"name": "sampled noise on a capacitor is root kT over C", "code": r'''
_v = ktc_rms(1e-12, 290.0)
assert abs(_v - 6.327623645571851e-05) < 1e-10, \
    f"1 pF at 290 K holds 63.3 uV rms; got {_v:.4e} V"
assert abs(ktc_rms(1e-12) / ktc_rms(1e-11) - 10.0 ** 0.5) < 1e-9, \
    "ten times the capacitance is sqrt(10) less noise, not ten times less"
'''},
                    {"name": "the resistance cancels out of the sampled noise", "code": r'''
_a = output_rms(1e3, 1e-12, 290.0)
_b = output_rms(1e5, 1e-12, 290.0)
assert abs(_a - 6.327623645571851e-05) < 1e-10, \
    f"the long route must give the same 63.3 uV as kT/C; got {_a:.4e} V"
assert abs(_a / _b - 1.0) < 1e-9, \
    f"a hundredfold change in R must not move the answer: {_a:.4e} against {_b:.4e} — a bigger resistor is noisier per hertz but passes proportionally fewer of them"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A noise budget for a receiver front end, priced in milliwatts",
        "runtime": "python",
        "minutes": 115,
        "brief": r'''
A four-stage receiver front end — LNA, mixer, IF amplifier, ADC driver — fed from a
50 Ω source and closed off by a one-pole anti-alias filter. The stage noise figures and
gains are fixed in `chain.py`, along with the filter and the transconductor model. You
are to produce the budget an analogue designer would actually be asked for, and then
put a price on it.

Build:

1. `cascade(stages)` — Friis over a list of `(name, nf_db, gain_db)` tuples, returning
   `(nf_db, gain_db)`. Note the three-element tuples: read the last two entries so the
   same function serves the ordering search.
2. `noise_bandwidth(f, h2)` — the area under a sampled $|H|^2$, divided by its peak.
3. `input_referred_rms(nf_db, bn, rs, T)` — the total input-referred r.m.s. noise
   voltage, $\sqrt{4k_BT R_s F B_n}$.
4. `sensitivity_dbm(nf_db, bn, snr_db)` — the minimum detectable signal,
   $10\log_{10}(k_BT_0B_n \times 1000) + NF + SNR$.
5. `best_order(stages)` — the stage ordering with the lowest cascade noise figure.
6. `current_for_nf(target_nf_db)` and `power_for_nf(target_nf_db)` — the LNA bias
   current and supply power needed to hit a noise figure, using
   $F = 1 + \frac{\gamma}{g_m R_s}$ with $g_m = k\sqrt{I}$.
7. `budget(stages, f, r, c, snr_db)` — one dict tying it together, with keys
   `nf_db`, `gain_db`, `bn_hz`, `in_rms_v`, `sens_dbm`.
8. A short comment at the top of `main.py` recording the budget your code produces and
   what it would cost to take the noise figure down by 0.4 dB.

## Suggested order

The checks are ordered to light up as you build: conversions and Friis first, then the
bandwidth integral, then the two derived figures of merit, then the trade. `cascade`
and `noise_bandwidth` are the only two things everything else depends on.
''',
        "deliverables": [
            "`cascade` and `best_order`, computing Friis over three-element stage tuples and finding the ordering with the lowest cascade noise figure.",
            "`noise_bandwidth` by numerical integration of a sampled power response, agreeing with $\\frac{1}{4RC}$ for the supplied one-pole filter.",
            "`input_referred_rms` and `sensitivity_dbm`, both derived from the cascade noise figure and the noise bandwidth rather than from any single stage.",
            "`current_for_nf` and `power_for_nf`, inverting the transconductor noise model to price a noise figure in amps and watts.",
            "`budget` returning the five headline numbers as a dict, and a comment at the top of `main.py` quoting them and the cost of a 0.4 dB improvement.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy and no RF toolbox.",
            "Do not edit `chain.py`; the checks depend on the numbers in it.",
            "Every decibel in this problem is a power decibel. Convert to linear power before any Friis arithmetic and back only at the end.",
            "`noise_bandwidth` must integrate whatever grid it is handed; it may not special-case the one-pole shape.",
        ],
        "rubric": [
            {"criterion": "Cascade and ordering", "weight": 30,
             "evidence": "Friis is accumulated in linear power with each excess divided by the gain preceding it, giving the right figure for the supplied chain and for a reordered one, and the ordering search finds the minimum."},
            {"criterion": "Noise bandwidth", "weight": 20,
             "evidence": "The integral of the sampled power response, normalised by its peak, reproduces 1/(4RC) for the anti-alias filter to within half a per cent and is not hard-coded to that shape."},
            {"criterion": "Figures of merit", "weight": 25,
             "evidence": "Input-referred r.m.s. noise and sensitivity in dBm follow from the cascade noise figure and the noise bandwidth together, and move correctly when either one is changed."},
            {"criterion": "Noise against power", "weight": 15,
             "evidence": "The transconductor model is inverted correctly, so that a demanded noise figure returns a bias current that reproduces it, and a smaller excess noise factor costs quadratically more current."},
            {"criterion": "The budget itself", "weight": 10,
             "evidence": "The budget dict carries all five headline numbers with the right units, and the comment at the top of main.py states them and the cost of a 0.4 dB improvement."},
        ],
        "hints": [
            "`cascade` should read `stage[-2]` and `stage[-1]`, so it works whether or not the tuple carries a name.",
            "In the Friis loop, add `(F_stage - 1) / G` before updating `G` — the excess is divided by the gain in front of the stage, not including it.",
            "Sensitivity in dBm: `10 * np.log10(K_B * T0 * bn * 1000.0)` is the thermal floor, about -102 dBm for this filter; the noise figure and the required SNR simply add to it.",
            "`current_for_nf` inverts $F = 1 + \\gamma/(g_mR_s)$: solve for `gm`, then `I = (gm / GM_COEFF) ** 2`. The square is where the quadratic cost comes from.",
            "`best_order` is `min(permutations(stages), key=lambda p: cascade(list(p))[0])` — twenty-four orderings is nothing.",
        ],
        "files": [
            {"name": "chain.py", "ro": True, "content": r'''
"""Fixed data for the receiver front end. Do not edit — the checks rely on it."""
import numpy as np

K_B = 1.380649e-23     # J/K
T0 = 290.0             # K, the reference temperature for noise figure
R_SOURCE = 50.0        # ohm
GAMMA = 2.0 / 3.0      # channel thermal noise factor of the LNA device
GM_COEFF = 0.5         # g_m = GM_COEFF * sqrt(I_bias), in S per sqrt(A)
SUPPLY = 1.8           # V

# (name, noise figure dB, available power gain dB)
FRONT_END = [
    ("LNA", 1.4, 16.0),
    ("mixer", 9.0, 5.0),
    ("IF amp", 4.5, 22.0),
    ("ADC driver", 14.0, 0.0),
]

FILTER_R = 2.0e3       # ohm
FILTER_C = 8.0e-12     # F


def rc_h2(f, r, c):
    """|H(f)|^2 of the one-pole anti-alias filter, on the given frequency grid."""
    f0 = 1.0 / (2.0 * np.pi * r * c)
    return 1.0 / (1.0 + (np.asarray(f, dtype=float) / f0) ** 2)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from itertools import permutations
from chain import (K_B, T0, R_SOURCE, GAMMA, GM_COEFF, SUPPLY,
                   FRONT_END, FILTER_R, FILTER_C, rc_h2)

# Budget produced by this code:
#   cascade noise figure -> TODO dB
#   noise bandwidth      -> TODO Hz
#   input-referred noise -> TODO V rms
#   sensitivity at 10 dB SNR -> TODO dBm
#   cost of 0.4 dB less noise figure -> TODO mW


def db_to_lin(x):
    """Power decibels to a linear power ratio."""
    # TODO
    return 1.0


def lin_to_db(x):
    """Linear power ratio to power decibels."""
    # TODO
    return 0.0


def cascade(stages):
    """Friis over (name, nf_db, gain_db) tuples. Return (nf_db, gain_db)."""
    # TODO: read stage[-2] and stage[-1]; accumulate F and G linearly.
    return 0.0, 0.0


def noise_bandwidth(f, h2):
    """Area under the sampled power response, divided by its peak, in Hz."""
    # TODO: trapezium rule on a possibly non-uniform grid.
    return 0.0


def input_referred_rms(nf_db, bn, rs=R_SOURCE, T=T0):
    """Total input-referred r.m.s. noise voltage, in volts."""
    # TODO: sqrt(4 * K_B * T * rs * F * bn)
    return 0.0


def sensitivity_dbm(nf_db, bn, snr_db):
    """Minimum detectable signal power, in dBm."""
    # TODO: thermal floor in dBm, plus noise figure, plus required SNR.
    return 0.0


def best_order(stages):
    """The stage ordering with the lowest cascade noise figure."""
    # TODO
    return list(stages)


def lna_noise_factor(i_bias):
    """Linear noise factor of the LNA at a given bias current."""
    # TODO: gm = GM_COEFF * sqrt(i_bias), then 1 + GAMMA / (gm * R_SOURCE).
    return 1.0


def current_for_nf(target_nf_db):
    """Bias current in amps needed to reach a target LNA noise figure."""
    # TODO: invert lna_noise_factor.
    return 0.0


def power_for_nf(target_nf_db):
    """Supply power in watts needed to reach a target LNA noise figure."""
    # TODO
    return 0.0


def budget(stages, f, r, c, snr_db=10.0):
    """The five headline numbers, as a dict."""
    # TODO: keys nf_db, gain_db, bn_hz, in_rms_v, sens_dbm.
    return {}


if __name__ == "__main__":
    grid = np.logspace(2, 12, 200001)
    b = budget(FRONT_END, grid, FILTER_R, FILTER_C, 10.0)
    for k in ("nf_db", "gain_db", "bn_hz", "in_rms_v", "sens_dbm"):
        print(f"{k:>10}: {b.get(k)}")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from itertools import permutations
from chain import (K_B, T0, R_SOURCE, GAMMA, GM_COEFF, SUPPLY,
                   FRONT_END, FILTER_R, FILTER_C, rc_h2)

# Budget produced by this code:
#   cascade noise figure -> 1.960 dB (the LNA's 1.4 dB plus 0.56 dB of everything else)
#   noise bandwidth      -> 15.625 MHz, which is 1.571 times the 9.95 MHz corner
#   input-referred noise -> 4.433 uV rms over that bandwidth from a 50 ohm source
#   sensitivity at 10 dB SNR -> -90.08 dBm
#   cost of 0.4 dB less noise figure -> the LNA bias goes from 4.91 mA to 10.61 mA,
#   which is 10.2 mW more on a 1.8 V supply for 0.4 dB of sensitivity


def db_to_lin(x):
    """Power decibels to a linear power ratio."""
    return 10.0 ** (float(x) / 10.0)


def lin_to_db(x):
    """Linear power ratio to power decibels."""
    return float(10.0 * np.log10(x))


def cascade(stages):
    """Friis over (name, nf_db, gain_db) tuples. Return (nf_db, gain_db)."""
    F = 1.0
    G = 1.0
    for stage in stages:
        nf_db, g_db = stage[-2], stage[-1]
        F += (db_to_lin(nf_db) - 1.0) / G
        G *= db_to_lin(g_db)
    return lin_to_db(F), lin_to_db(G)


def noise_bandwidth(f, h2):
    """Area under the sampled power response, divided by its peak, in Hz."""
    f = np.asarray(f, dtype=float)
    h2 = np.asarray(h2, dtype=float)
    area = float(np.sum(np.diff(f) * 0.5 * (h2[1:] + h2[:-1])))
    return area / float(np.max(h2))


def input_referred_rms(nf_db, bn, rs=R_SOURCE, T=T0):
    """Total input-referred r.m.s. noise voltage, in volts."""
    return float(np.sqrt(4.0 * K_B * T * rs * db_to_lin(nf_db) * bn))


def sensitivity_dbm(nf_db, bn, snr_db):
    """Minimum detectable signal power, in dBm."""
    floor = 10.0 * np.log10(K_B * T0 * bn * 1000.0)
    return float(floor + nf_db + snr_db)


def best_order(stages):
    """The stage ordering with the lowest cascade noise figure."""
    return list(min(permutations(stages), key=lambda p: cascade(list(p))[0]))


def lna_noise_factor(i_bias):
    """Linear noise factor of the LNA at a given bias current."""
    gm = GM_COEFF * np.sqrt(float(i_bias))
    return float(1.0 + GAMMA / (gm * R_SOURCE))


def current_for_nf(target_nf_db):
    """Bias current in amps needed to reach a target LNA noise figure."""
    F = db_to_lin(target_nf_db)
    gm = GAMMA / ((F - 1.0) * R_SOURCE)
    return float((gm / GM_COEFF) ** 2)


def power_for_nf(target_nf_db):
    """Supply power in watts needed to reach a target LNA noise figure."""
    return float(SUPPLY * current_for_nf(target_nf_db))


def budget(stages, f, r, c, snr_db=10.0):
    """The five headline numbers, as a dict."""
    nf_db, gain_db = cascade(stages)
    bn = noise_bandwidth(f, rc_h2(f, r, c))
    return {
        "nf_db": nf_db,
        "gain_db": gain_db,
        "bn_hz": bn,
        "in_rms_v": input_referred_rms(nf_db, bn),
        "sens_dbm": sensitivity_dbm(nf_db, bn, snr_db),
    }


if __name__ == "__main__":
    grid = np.logspace(2, 12, 200001)
    b = budget(FRONT_END, grid, FILTER_R, FILTER_C, 10.0)
    for k in ("nf_db", "gain_db", "bn_hz", "in_rms_v", "sens_dbm"):
        print(f"{k:>10}: {b.get(k)}")
'''},
        ],
        "tests": [
            {"name": "the supplied front end has the Friis noise figure and gain", "code": r'''
from chain import FRONT_END
_nf, _g = cascade(FRONT_END)
assert abs(_nf - 1.9602255626417047) < 1e-8, \
    f"expected 1.960 dB for this chain; got {_nf:.4f} dB — check that each excess is divided by the gain preceding it"
assert abs(_g - 43.0) < 1e-8, \
    f"gains in dB add: 16 + 5 + 22 + 0 = 43; got {_g:.4f} dB"
'''},
            {"name": "putting the LNA second wrecks the chain", "code": r'''
from chain import FRONT_END
_swapped = [FRONT_END[1], FRONT_END[0], FRONT_END[2], FRONT_END[3]]
_nf = cascade(_swapped)[0]
assert abs(_nf - 9.07369603566844) < 1e-8, \
    f"with the mixer first the cascade is 9.074 dB; got {_nf:.4f} dB"
assert _nf > cascade(FRONT_END)[0] + 7.0, \
    "nothing downstream can repair a noisy first stage — this ordering should cost over 7 dB"
'''},
            {"name": "the ordering search finds the quiet arrangement", "code": r'''
from chain import FRONT_END
_best = best_order(FRONT_END)
assert _best[0][0] == "LNA", f"the LNA belongs at the front; your ordering starts with {_best[0][0]!r}"
assert abs(cascade(_best)[0] - 1.5484048344625099) < 1e-8, \
    f"the best of the twenty-four orderings gives 1.548 dB; got {cascade(_best)[0]:.4f} dB"
assert len(_best) == 4, f"an ordering must keep all four stages, got {len(_best)}"
'''},
            {"name": "the anti-alias filter sets a 15.6 megahertz noise bandwidth", "code": r'''
import numpy as np
from chain import FILTER_R, FILTER_C, rc_h2
_grid = np.logspace(2, 12, 200001)
_bn = noise_bandwidth(_grid, rc_h2(_grid, FILTER_R, FILTER_C))
assert abs(_bn / 15625000.0 - 1.0) < 0.005, \
    f"1/(4RC) is 15.625 MHz for this filter; the integral gave {_bn:.0f} Hz"
assert _bn > 1.5 * (1.0 / (2.0 * np.pi * FILTER_R * FILTER_C)), \
    "noise bandwidth is pi/2 times the 3 dB corner, not equal to it — the tail carries real noise"
'''},
            {"name": "noise bandwidth is not hard-coded to the one-pole shape", "code": r'''
import numpy as np
_f0 = 1e6
_grid = np.logspace(2, 12, 200001)
_flat = np.where(_grid <= _f0, 1.0, 0.0)
_bn = noise_bandwidth(_grid, _flat)
assert abs(_bn / _f0 - 1.0) < 0.01, \
    f"a brick wall of width 1 MHz has a noise bandwidth of 1 MHz; got {_bn:.0f} Hz"
_second = 1.0 / (1.0 + (_grid / _f0) ** 4)
assert abs(noise_bandwidth(_grid, _second) / _f0 - 1.1107) < 0.02, \
    "a two-pole Butterworth gives 1.111 times its corner; your function is assuming a single pole"
'''},
            {"name": "the input-referred noise and the sensitivity agree with the budget", "code": r'''
_bn = 15625000.0
_nf = 1.9602255626417047
_v = input_referred_rms(_nf, _bn)
assert abs(_v - 4.432787671194234e-06) < 1e-10, \
    f"sqrt(4kT*50*F*Bn) is 4.433 uV rms here; got {_v:.4e} V"
assert abs(input_referred_rms(0.0, _bn) - 3.5372491518834235e-06) < 1e-10, \
    "with F = 1 only the source resistor contributes, giving 3.537 uV rms"
_s = sensitivity_dbm(_nf, _bn, 10.0)
assert abs(_s - (-90.07676137142528)) < 1e-8, \
    f"expected -90.08 dBm at 10 dB SNR; got {_s:.4f} dBm"
assert abs(sensitivity_dbm(0.0, _bn, 0.0) - (-102.03698693406699)) < 1e-8, \
    "the bare thermal floor in this bandwidth is -102.04 dBm; check the factor of 1000 that turns watts into milliwatts"
'''},
            {"name": "halving the bandwidth buys three decibels of sensitivity", "code": r'''
import numpy as np
_nf = 2.0
_a = sensitivity_dbm(_nf, 15625000.0, 10.0)
_b = sensitivity_dbm(_nf, 7812500.0, 10.0)
assert abs((_a - _b) - 3.010299956639812) < 1e-8, \
    f"halving Bn should improve sensitivity by exactly 3.01 dB; got {_a - _b:.4f} dB"
assert abs(input_referred_rms(_nf, 7812500.0) / input_referred_rms(_nf, 15625000.0) - 0.7071067811865476) < 1e-9, \
    "half the bandwidth is 1/sqrt(2) of the r.m.s. voltage, because noise power is what halves"
'''},
            {"name": "a demanded noise figure returns a current that reproduces it", "code": r'''
import numpy as np
_i = current_for_nf(1.4)
assert abs(_i - 0.004914647550898715) < 1e-9, \
    f"1.4 dB from this device needs 4.915 mA; got {_i * 1000.0:.3f} mA"
_back = 10.0 * np.log10(lna_noise_factor(_i))
assert abs(_back - 1.4) < 1e-8, \
    f"feeding your own current back through lna_noise_factor must return 1.4 dB; got {_back:.4f} dB"
assert abs(power_for_nf(1.4) - 0.008846365591617687) < 1e-9, \
    f"at 1.8 V that is 8.85 mW; got {power_for_nf(1.4) * 1000.0:.3f} mW"
'''},
            {"name": "each further decibel of noise figure costs quadratically", "code": r'''
_i2 = current_for_nf(2.0)
_i1 = current_for_nf(1.0)
assert _i1 > 5.0 * _i2, \
    f"going from 2.0 dB to 1.0 dB should cost more than five times the current; got {_i1 / _i2:.2f} times"
assert abs(_i1 - 0.010606891180419494) < 1e-9, \
    f"1.0 dB needs 10.607 mA; got {_i1 * 1000.0:.3f} mA"
assert abs(power_for_nf(1.0) - power_for_nf(1.4) - 0.0102460385331374) < 1e-9, \
    "the last 0.4 dB costs about 10.2 mW, which is the number the budget comment has to quote"
'''},
            {"name": "the budget dict carries all five headline numbers", "code": r'''
import numpy as np
from chain import FRONT_END, FILTER_R, FILTER_C
_grid = np.logspace(2, 12, 200001)
_b = budget(FRONT_END, _grid, FILTER_R, FILTER_C, 10.0)
for _k in ("nf_db", "gain_db", "bn_hz", "in_rms_v", "sens_dbm"):
    assert _k in _b, f"the budget is missing the key {_k!r}"
assert abs(_b["nf_db"] - 1.9602255626417047) < 1e-8, f"nf_db should be 1.960, got {_b['nf_db']}"
assert abs(_b["bn_hz"] / 15625000.0 - 1.0) < 0.005, f"bn_hz should be about 15.625 MHz, got {_b['bn_hz']}"
assert abs(_b["in_rms_v"] / 4.432787671194234e-06 - 1.0) < 0.005, \
    f"in_rms_v should be about 4.433 uV, got {_b['in_rms_v']}"
assert abs(_b["sens_dbm"] - (-90.07676137142528)) < 0.05, \
    f"sens_dbm should be about -90.08 dBm, got {_b['sens_dbm']}"
assert _b["in_rms_v"] < 1e-3, \
    "in_rms_v is a voltage in volts, not microvolts — the whole budget is in SI units"
'''},
        ],
    },
}
