"""PWR510 — Resonant Converters.

Same authoring contract as CTRL510, which is the reference course:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

The two sandboxes are `bode` and `switching`. Both notices sets describe what
those draw functions in src/studio.js actually put on the canvas at the stated
parameter values, not what a textbook figure would show. The `switching`
waveform in particular is a model, and the notices say so.
"""

COURSE = {
    "id": "PWR510",
    "title": "Resonant Converters",
    "band": 4,
    "level": "Advanced",
    "prereqs": [],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◐",
    "summary": (
        "A hard-switched bridge dissipates half the energy stored in its own device "
        "capacitance on every transition, and that bill grows with frequency. A resonant "
        "converter arranges for the voltage to be zero at the moment the device turns on, "
        "which is why offline supplies run at hundreds of kilohertz instead of tens. "
        "This course builds the series-resonant and LLC tanks from the first-harmonic "
        "approximation, derives the gain curve that the controller actually steers, fixes "
        "the dead-time condition that makes zero-voltage switching happen, and then "
        "accounts honestly for where the remaining loss goes."
    ),
    "outcomes": [
        "Reduce a switching converter to a linear tank driven by one sinusoid, and say where that approximation stops being true.",
        "Derive the series-resonant and LLC gain curves, and read a required gain range off a line and load specification.",
        "Size the magnetising inductance and the dead time so that zero-voltage switching holds across the whole operating range.",
        "Build a loss budget that separates conduction, core, gate and switching terms, and explain why light load is the hard case.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that designs a 240 W LLC half-bridge and proves it closes on gain, on ZVS and on efficiency.",
    "reading": [
        "*Fundamentals of Power Electronics*, Erickson & Maksimović — chapter 19 on resonant conversion.",
        "*Resonant Power Converters*, Kazimierczuk & Czarkowski — for the tank algebra in full.",
        "Steigerwald, 'A comparison of half-bridge resonant converter topologies', IEEE Trans. Power Electronics, 1988.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The tank, and the one harmonic that matters",
            "summary": "A square wave drives the bridge, but a selective tank only responds to its fundamental. That single approximation turns a switching circuit into a phasor problem.",
            "concepts": [
                "The half-bridge output is a square wave between the rails; its fundamental has peak amplitude $2V_{in}/\\pi$ and no even harmonics at all.",
                "A tank with any useful selectivity attenuates the third harmonic by roughly an order of magnitude, so keeping only the fundamental is not a wild simplification.",
                "The rectifier and its output capacitor are replaced by an equivalent resistance $R_{ac} = 8n^2R_L/\\pi^2$, chosen so the fundamental sees the same power flow.",
                "The tank has two numbers: $\\omega_r = 1/\\sqrt{L_rC_r}$ and $Z_0 = \\sqrt{L_r/C_r}$. Load enters only through $Q = Z_0/R_{ac}$.",
                "First-harmonic approximation is at its worst far from resonance and at heavy load, where the tank current stops looking sinusoidal.",
            ],
            "sandbox": {
                "title": "Reading a tank off a Bode plot",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 50, "zeta": 0.1, "K": 1},
                "brief": r'''
The curve on screen is a second-order lowpass, $K/(1 - x^2 + j2\zeta x)$ with
$x = \omega/\omega_n$. That is not a stand-in for a resonant tank — it *is* one. Drive a
series $L_r$–$C_r$–$R_{ac}$ chain with a voltage source and take the output across the
capacitor and you get exactly this expression, with $\omega_n = \omega_r$ and
$\zeta = 1/(2Q)$.

So the damping slider is the load. It opens at $\zeta = 0.1$, which is $Q = 5$: a
lightly loaded tank.
''',
                "notice": [
                    "The amber dot marks the gain at the corner, and it always reads $K/(2\\zeta)$ — which is $QK$. At the opening $\\zeta = 0.1$ that is $5$, or $14.0$ dB. The tank multiplies the driving fundamental by $Q$ at resonance, and that is the whole reason a resonant converter can boost.",
                    "Drag $\\zeta$ up to $0.8$. The peak is gone entirely, and the amber dot has fallen to $-4.1$ dB, below the dashed 0 dB line. Above $\\zeta = 0.707$ the magnitude falls monotonically from DC, so a heavily loaded tank has no resonant rise at all.",
                    "Watch the low-frequency end while you sweep $\\zeta$. It does not move: every curve in the family leaves the same $20\\log_{10}K$ asymptote. Frequency control has no authority down there, which is the light-load regulation problem in one picture.",
                    "The phase plot is the switching test in disguise. The tank input impedance angle is $-(90^\\circ + \\varphi)$, where $\\varphi$ is the plotted phase. At the corner $\\varphi = -90^\\circ$ exactly, whatever the damping, so the tank is purely resistive there; anywhere the phase is *below* $-90^\\circ$ the tank looks inductive and the bridge can switch at zero volts. Check one: at $\\zeta = 0.5$ and one octave above the corner the phase reads $-146.3^\\circ$, so the impedance angle is $+56.3^\\circ$.",
                ],
            },
            "derive": {
                "title": "What the first-harmonic approximation replaces the converter with",
                "minutes": 14,
                "vars": ["V_in", "V_o", "I_p", "I_o", "R_L", "R_ac", "n", "Z_0", "Q"],
                "brief": r'''
The half-bridge midpoint swings between the two rails, so relative to its own average
it is a square wave alternating between $+V_{in}/2$ and $-V_{in}/2$. On the other side
of the transformer a full-bridge rectifier feeds a large output capacitor held at
$V_o$.

The Fourier series of a square wave alternating between $+A$ and $-A$ is

$$\frac{4A}{\pi}\left(\sin\theta + \frac{1}{3}\sin 3\theta + \frac{1}{5}\sin 5\theta + \dots\right)$$

Everything below follows from that one series and from conservation of power.
''',
                "steps": [
                    {
                        "prompt": "Take $A = V_{in}/2$. Write the peak amplitude of the fundamental of the bridge voltage.",
                        "answer": "\\frac{2 V_{in}}{\\pi}",
                        "placeholder": "\\frac{2 V_{in}}{\\pi}",
                        "hint": "The series has $4A/\\pi$ in front of the fundamental sine. Substitute the half-rail amplitude.",
                        "deconstruct": [
                            "The fundamental term is $(4A/\\pi)\\sin\\theta$, so its peak is $4A/\\pi$.",
                            "With $A = V_{in}/2$ that is $4V_{in}/(2\\pi)$.",
                        ],
                    },
                    {
                        "prompt": "The tank sees a sinusoid, so what matters for power is its RMS value. Write the RMS of that fundamental.",
                        "answer": "\\frac{\\sqrt{2} V_{in}}{\\pi}",
                        "placeholder": "\\frac{\\sqrt{2} V_{in}}{\\pi}",
                        "hint": "Divide a peak by $\\sqrt{2}$ to get the RMS of a sinusoid.",
                        "deconstruct": [
                            "RMS of a sinusoid is peak over $\\sqrt{2}$.",
                            "$\\frac{2V_{in}}{\\pi\\sqrt{2}}$ is the same number written with the root on the other side.",
                        ],
                    },
                    {
                        "prompt": "Now the output side. The tank current arriving at the rectifier is a sinusoid of peak $I_p$, and the rectifier passes its magnitude to the load. The average of a full-wave rectified sinusoid is $2I_p/\\pi$, and that average is the DC output current $I_o$. Write $I_p$ in terms of $I_o$.",
                        "answer": "\\frac{\\pi I_o}{2}",
                        "placeholder": "\\frac{\\pi I_o}{2}",
                        "hint": "Set $2I_p/\\pi = I_o$ and solve for $I_p$.",
                        "deconstruct": [
                            "The capacitor holds the output voltage, so all the rectified current goes to the load on average.",
                            "Rearranging $I_o = 2I_p/\\pi$ gives $I_p$.",
                        ],
                    },
                    {
                        "prompt": "Because the output capacitor holds $V_o$ steady and the diodes commutate with the current, the voltage the tank sees at the rectifier input is itself a square wave alternating between $+V_o$ and $-V_o$. Write the peak amplitude of its fundamental.",
                        "answer": "\\frac{4 V_o}{\\pi}",
                        "placeholder": "\\frac{4 V_o}{\\pi}",
                        "hint": "Same Fourier series as step one, now with $A = V_o$.",
                        "deconstruct": [
                            "The rectifier input voltage is $\\pm V_o$ in phase with the current.",
                            "So its fundamental peak is $4A/\\pi$ with $A = V_o$.",
                        ],
                    },
                    {
                        "prompt": "That fundamental voltage and the fundamental current are in phase, so the rectifier plus load looks to the tank like a resistance $R_{ac}$ equal to their ratio. Using $V_o = I_o R_L$, write $R_{ac}$ in terms of $R_L$ alone.",
                        "given": "You have the fundamental voltage $4V_o/\\pi$ and the current peak $I_p = \\pi I_o/2$.",
                        "answer": "\\frac{8 R_L}{\\pi^2}",
                        "placeholder": "\\frac{8 R_L}{\\pi^{2}}",
                        "hint": "Divide the voltage amplitude by the current amplitude, then replace $V_o/I_o$ by $R_L$.",
                        "deconstruct": [
                            "$R_{ac} = \\frac{4V_o/\\pi}{\\pi I_o/2}$.",
                            "That is $\\frac{4V_o}{\\pi}\\cdot\\frac{2}{\\pi I_o} = \\frac{8}{\\pi^2}\\cdot\\frac{V_o}{I_o}$.",
                        ],
                    },
                    {
                        "prompt": "A transformer of turns ratio $n$ (primary to secondary) sits between the tank and the rectifier, and impedance referred through it scales by $n^2$. Write the $R_{ac}$ the tank actually sees.",
                        "answer": "\\frac{8 n^2 R_L}{\\pi^2}",
                        "placeholder": "\\frac{8 n^{2} R_L}{\\pi^{2}}",
                        "hint": "Referring a resistance from secondary to primary multiplies it by the square of the turns ratio.",
                        "deconstruct": [
                            "Voltage scales by $n$ and current by $1/n$, so resistance scales by $n^2$.",
                            "Apply that to the $8R_L/\\pi^2$ you just derived.",
                        ],
                    },
                ],
                "closing": r'''
The whole converter is now three numbers: a driving RMS voltage $\sqrt{2}V_{in}/\pi$, a
linear tank, and a load resistance $8n^2R_L/\pi^2$. The factor $8/\pi^2 \approx 0.811$ is
the only trace left of the rectifier.

The approximation earns its keep because the tank is a filter. It fails where the tank
stops filtering — deep into discontinuous conduction, or at very low $Q$, where the
current is closer to triangular than sinusoidal and the third harmonic is no longer
negligible. Every gain curve in this course is accurate to a few per cent near
resonance and worth checking against a simulation anywhere else.
''',
            },
            "lab": {
                "title": "Characterise a series-resonant tank",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Six small functions, all of them one line once you have the algebra.

- `resonance(Lr, Cr)` — the resonant frequency in **hertz**, not radians per second.
- `char_impedance(Lr, Cr)` — $Z_0 = \sqrt{L_r/C_r}$ in ohms.
- `r_ac(n, RL)` — the equivalent AC load resistance you derived, referred through the
  transformer.
- `quality(Lr, Cr, Rac)` — the loaded quality factor $Q = Z_0/R_{ac}$.
- `fundamental_rms(Vin)` — the RMS of the fundamental of a half-bridge square wave
  whose midpoint swings between $0$ and `Vin`.
- `src_gain(fs, Lr, Cr, Rac)` — the first-harmonic voltage gain of the series-resonant
  tank at switching frequency `fs`:

```text
M(x) = 1 / sqrt(1 + Q^2 (x - 1/x)^2),   x = fs / fr
```

`main.py` prints a summary for a 60 µH, 33 nF tank. Run it and read the numbers before
you look at the checks.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def resonance(Lr, Cr):
    """Series resonant frequency in Hz."""
    # TODO: 1 / (2 pi sqrt(Lr Cr)).
    return 0.0


def char_impedance(Lr, Cr):
    """Characteristic impedance sqrt(Lr / Cr), in ohms."""
    # TODO
    return 0.0


def r_ac(n, RL):
    """Equivalent AC load resistance seen by the tank, primary referred."""
    # TODO: 8 n^2 RL / pi^2.
    return 0.0


def quality(Lr, Cr, Rac):
    """Loaded quality factor Z0 / Rac."""
    # TODO
    return 0.0


def fundamental_rms(Vin):
    """RMS of the fundamental of a half-bridge square wave of rail voltage Vin."""
    # TODO: the midpoint swings +-Vin/2 about its average.
    return 0.0


def src_gain(fs, Lr, Cr, Rac):
    """First-harmonic voltage gain of a series-resonant tank at frequency fs."""
    # TODO: x = fs / fr, then 1 / sqrt(1 + Q^2 (x - 1/x)^2).
    return 0.0


if __name__ == "__main__":
    Lr, Cr = 60e-6, 33e-9
    fr = resonance(Lr, Cr)
    print("fr   =", round(fr, 3), "Hz")
    print("Z0   =", round(char_impedance(Lr, Cr), 4), "ohm")
    print("Rac  =", round(r_ac(16.0, 0.6), 4), "ohm")
    print("Q    =", round(quality(Lr, Cr, 50.0), 6))
    print("V1   =", round(fundamental_rms(400.0), 4), "V rms")
    print("gain at fr    =", round(src_gain(fr, Lr, Cr, 50.0), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def resonance(Lr, Cr):
    """Series resonant frequency in Hz."""
    return float(1.0 / (2.0 * np.pi * np.sqrt(Lr * Cr)))


def char_impedance(Lr, Cr):
    """Characteristic impedance sqrt(Lr / Cr), in ohms."""
    return float(np.sqrt(Lr / Cr))


def r_ac(n, RL):
    """Equivalent AC load resistance seen by the tank, primary referred."""
    return float(8.0 * n * n * RL / (np.pi * np.pi))


def quality(Lr, Cr, Rac):
    """Loaded quality factor Z0 / Rac."""
    return float(char_impedance(Lr, Cr) / Rac)


def fundamental_rms(Vin):
    """RMS of the fundamental of a half-bridge square wave of rail voltage Vin."""
    return float(np.sqrt(2.0) * Vin / np.pi)


def src_gain(fs, Lr, Cr, Rac):
    """First-harmonic voltage gain of a series-resonant tank at frequency fs."""
    x = fs / resonance(Lr, Cr)
    Q = quality(Lr, Cr, Rac)
    return float(1.0 / np.sqrt(1.0 + (Q * (x - 1.0 / x)) ** 2))


if __name__ == "__main__":
    Lr, Cr = 60e-6, 33e-9
    fr = resonance(Lr, Cr)
    print("fr   =", round(fr, 3), "Hz")
    print("Z0   =", round(char_impedance(Lr, Cr), 4), "ohm")
    print("Rac  =", round(r_ac(16.0, 0.6), 4), "ohm")
    print("Q    =", round(quality(Lr, Cr, 50.0), 6))
    print("V1   =", round(fundamental_rms(400.0), 4), "V rms")
    print("gain at fr    =", round(src_gain(fr, Lr, Cr, 50.0), 6))
'''}],
                "hints": [
                    "`resonance` is in hertz, so the $2\\pi$ goes in the denominator: `1 / (2 * np.pi * np.sqrt(Lr * Cr))`.",
                    "The midpoint of a half-bridge swings the full rail, but about its own average it is $\\pm V_{in}/2$ — that is the amplitude the Fourier series wants.",
                    "In `src_gain`, work out `x` and `Q` first and the last line is a direct transcription of the formula.",
                ],
                "tests": [
                    {"name": "the resonant frequency is in hertz, not radians per second", "code": r'''
_fr = resonance(60e-6, 33e-9)
assert abs(_fr - 113106.49292909501) < 1e-6, \
    f"expected 113106.4929 Hz for 60 uH and 33 nF, got {_fr} — a factor of 2*pi out means you returned rad/s"
'''},
                    {"name": "the characteristic impedance is the ratio the tank is built around", "code": r'''
_z = char_impedance(60e-6, 33e-9)
assert abs(_z - 42.640143271122085) < 1e-9, \
    f"Z0 = sqrt(Lr/Cr) should be 42.6401 ohm, got {_z}"
'''},
                    {"name": "the rectifier costs the load a factor of 8 over pi squared", "code": r'''
_r1 = r_ac(1.0, 1.0)
assert abs(_r1 - 0.8105694691387022) < 1e-12, \
    f"with n=1 and RL=1 the tank should see 8/pi^2 = 0.81057 ohm, got {_r1} — a square wave is not a sinusoid"
_r2 = r_ac(16.0, 0.6)
assert abs(_r2 - 124.50347045970466) < 1e-9, \
    f"the turns ratio enters squared: expected 124.5035 ohm, got {_r2}"
'''},
                    {"name": "Q is the ratio of the two tank numbers", "code": r'''
_q = quality(60e-6, 33e-9, 50.0)
assert abs(_q - 0.8528028654224417) < 1e-12, \
    f"Q = Z0/Rac should be 0.852803, got {_q} — heavier load means smaller Q, not larger"
'''},
                    {"name": "the driving fundamental is smaller than the rail", "code": r'''
_v = fundamental_rms(400.0)
assert abs(_v - 180.06326323142122) < 1e-9, \
    f"sqrt(2)*400/pi = 180.0633 V rms, got {_v}"
assert _v < 400.0, "only part of the square wave lands in the fundamental"
'''},
                    {"name": "the tank passes everything at resonance", "code": r'''
_fr = resonance(60e-6, 33e-9)
_g = src_gain(_fr, 60e-6, 33e-9, 50.0)
assert abs(_g - 1.0) < 1e-12, \
    f"at x=1 the reactances cancel and the gain is exactly 1, got {_g}"
'''},
                    {"name": "the gain falls off either side of resonance", "code": r'''
_fr = resonance(60e-6, 33e-9)
_hi = src_gain(1.3 * _fr, 60e-6, 33e-9, 50.0)
_lo = src_gain(0.7 * _fr, 60e-6, 33e-9, 50.0)
assert abs(_hi - 0.911018757309723) < 1e-9, f"expected 0.911019 at x=1.3, got {_hi}"
assert abs(_lo - 0.8493972049135455) < 1e-9, f"expected 0.849397 at x=0.7, got {_lo}"
'''},
                    {"name": "a series-resonant tank can never boost", "code": r'''
import numpy as np
_fr = resonance(60e-6, 33e-9)
_xs = np.linspace(0.3, 3.0, 271)
_gs = [src_gain(float(x) * _fr, 60e-6, 33e-9, 50.0) for x in _xs]
assert max(_gs) <= 1.0 + 1e-12, "M(x) = 1/sqrt(1 + ...) can never exceed 1"
assert abs(max(_gs) - 1.0) < 1e-6, \
    f"the maximum over the sweep should reach 1 at resonance, got {max(_gs)}"
_sym = src_gain(1.5 * _fr, 60e-6, 33e-9, 50.0) - src_gain(_fr / 1.5, 60e-6, 33e-9, 50.0)
assert abs(_sym) < 1e-12, \
    "x and 1/x give the same gain because the reactance term is squared"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "The gain curve, and why LLC exists",
            "summary": "A series-resonant tank can only buck, and it loses control at light load. Adding one inductor fixes both problems and creates a family of curves.",
            "concepts": [
                "The SRC gain $M(x) = 1/\\sqrt{1 + Q^2(x - 1/x)^2}$ is at most 1, so an SRC cannot boost, and at no load $Q \\to 0$ flattens it to 1 everywhere.",
                "LLC puts a magnetising inductance $L_m$ across the load, giving a second resonance $f_{r2} = 1/(2\\pi\\sqrt{(L_r+L_m)C_r})$ below the first.",
                "The LLC gain is $M = L_n x^2 / \\sqrt{((L_n+1)x^2 - 1)^2 + (QL_nx(x^2-1))^2}$ with $L_n = L_m/L_r$, and it equals exactly 1 at $x = 1$ for every $L_n$ and every $Q$.",
                "That load-independent crossing is the design anchor: put the nominal line at resonance and the transformer turns ratio is fixed by inspection.",
                "Below resonance the curve peaks; the peak is the boost budget, and it shrinks as $Q$ rises, so the low-line and full-load corner is the one that sizes the tank.",
                "Above resonance the gain is monotonically decreasing in $x$, which is what makes frequency control well behaved there.",
            ],
            "sandbox": {
                "title": "How load reshapes a resonant curve",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 50, "zeta": 0.5, "K": 1},
                "brief": r'''
The same tank as the last sandbox, opened at $\zeta = 0.5$, which is $Q = 1$ — a
loaded tank rather than an idle one. The point of this pass is not the shape of one
curve but the shape of the *family*: what a controller can and cannot reach by moving
frequency alone.

Sweep $\zeta$ slowly from one end to the other and watch three separate things: the
low-frequency end, the corner, and the high-frequency tail.
''',
                "notice": [
                    "The corner marker traces $K/(2\\zeta)$ as you sweep, and that is exactly $Q$. Every bit of the load dependence of this tank lives in one number.",
                    "At $\\zeta = 0.05$ the corner marker reads $20.0$ dB and at $\\zeta = 1.5$ it reads $-9.5$ dB. That is a 30 dB swing in resonant gain across the load range, and a frequency-mode controller has to cover all of it.",
                    "Two decades of the tail are indistinguishable. At ten times the corner the magnitude is $-39.9$ dB for $\\zeta = 0.05$ and $-40.3$ dB for $\\zeta = 1.5$: the $-40$ dB per decade asymptote does not care about damping. Far above resonance you have gain authority but almost no load sensitivity.",
                    "The low-frequency end is the mirror image and the more dangerous one. Every curve leaves the same flat $20\\log_{10}K$ line, so far below resonance frequency buys you nothing at any load. A series-resonant converter that has to regulate down to no load runs out of range here; the LLC's extra inductor is the fix, and the next lab draws it.",
                ],
            },
            "derive": {
                "title": "The series-resonant gain, and inverting it",
                "minutes": 15,
                "vars": ["omega", "omega_r", "L_r", "C_r", "Z_0", "Q", "x", "M", "R_ac"],
                "brief": r'''
The tank is $L_r$ and $C_r$ in series with $R_{ac}$, driven by the fundamental of the
bridge voltage, with the output taken across $R_{ac}$. Everything here is one voltage
divider; the work is in choosing the right variables so the answer is readable.
''',
                "steps": [
                    {
                        "prompt": "Write the reactance of the series $L_r$–$C_r$ branch at angular frequency $\\omega$ — the imaginary part of its impedance, in terms of $\\omega$, $L_r$ and $C_r$.",
                        "answer": "\\omega L_r - \\frac{1}{\\omega C_r}",
                        "placeholder": "\\omega L_r - \\frac{1}{\\omega C_r}",
                        "hint": "An inductor contributes $+\\omega L$ and a capacitor $-1/(\\omega C)$ to the reactance.",
                        "deconstruct": [
                            "$Z_L = j\\omega L_r$ and $Z_C = 1/(j\\omega C_r) = -j/(\\omega C_r)$.",
                            "Adding them and taking the coefficient of $j$ gives the reactance.",
                        ],
                    },
                    {
                        "prompt": "Write the $\\omega_r$ at which that reactance is zero.",
                        "answer": "\\frac{1}{\\sqrt{L_r C_r}}",
                        "placeholder": "\\frac{1}{\\sqrt{L_r C_r}}",
                        "hint": "Set the two terms equal and solve for $\\omega$.",
                        "deconstruct": [
                            "$\\omega L_r = 1/(\\omega C_r)$ gives $\\omega^2 = 1/(L_rC_r)$.",
                            "Take the positive root.",
                        ],
                    },
                    {
                        "prompt": "Now normalise. With $Z_0 = \\sqrt{L_r/C_r}$ and $x = \\omega/\\omega_r$, rewrite that same reactance using only $Z_0$ and $x$.",
                        "given": "Note that $\\omega_r L_r = Z_0$ and $1/(\\omega_r C_r) = Z_0$ as well — that is what makes $Z_0$ the natural unit.",
                        "answer": "Z_0 \\left( x - \\frac{1}{x} \\right)",
                        "placeholder": "Z_0 \\left( x - \\frac{1}{x} \\right)",
                        "hint": "Substitute $\\omega = x\\omega_r$ into both terms and factor $Z_0$ out.",
                        "deconstruct": [
                            "$\\omega L_r = x\\,\\omega_r L_r = xZ_0$.",
                            "$1/(\\omega C_r) = 1/(x\\,\\omega_r C_r) = Z_0/x$.",
                        ],
                    },
                    {
                        "prompt": "The output is taken across $R_{ac}$, so the gain magnitude is $R_{ac}$ divided by the magnitude of the total series impedance. With $Q = Z_0/R_{ac}$, write the gain $M$ in terms of $Q$ and $x$ only.",
                        "answer": "\\frac{1}{\\sqrt{1 + Q^2 \\left( x - \\frac{1}{x} \\right)^2}}",
                        "placeholder": "\\frac{1}{\\sqrt{1 + Q^{2} \\left( x - \\frac{1}{x} \\right)^{2}}}",
                        "hint": "Divide numerator and denominator by $R_{ac}$; the reactance term becomes $Z_0/R_{ac}$ times $(x - 1/x)$.",
                        "deconstruct": [
                            "$M = R_{ac}/\\sqrt{R_{ac}^2 + Z_0^2(x - 1/x)^2}$.",
                            "Divide top and bottom by $R_{ac}$ and the ratio $Z_0/R_{ac}$ appears as $Q$.",
                        ],
                    },
                    {
                        "prompt": "A controller needs the inverse: given a target gain $M$ and an operating point above resonance, what $Q$ would put the tank there? Solve for $Q$ in terms of $M$ and $x$, taking $x > 1$ so that $x - 1/x$ is positive.",
                        "answer": "\\frac{\\sqrt{\\frac{1}{M^2} - 1}}{x - \\frac{1}{x}}",
                        "placeholder": "\\frac{\\sqrt{\\frac{1}{M^{2}} - 1}}{x - \\frac{1}{x}}",
                        "hint": "Square both sides, then isolate the $Q^2$ term before taking the root.",
                        "deconstruct": [
                            "$M^2\\left(1 + Q^2(x-1/x)^2\\right) = 1$.",
                            "So $Q^2(x-1/x)^2 = 1/M^2 - 1$.",
                            "Take the positive root of both sides and divide.",
                        ],
                    },
                ],
                "closing": r'''
Two things are worth carrying forward. First, $M \le 1$ always, because the denominator
is a square root of one plus something non-negative — a series-resonant converter is a
buck-only topology and cannot ride out a low line.

Second, $M$ depends on $x$ and $1/x$ symmetrically, so the curve is identical at $x$
and $1/x$. Frequency control therefore has two solutions for every target gain, and
only one of them puts the tank on the inductive side where the bridge can switch at
zero volts. Module 3 is about which side that is.
''',
            },
            "lab": {
                "title": "Draw the LLC gain family",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
The LLC tank puts $L_m$ in parallel with $R_{ac}$, ahead of the series $L_r$–$C_r$
branch. Working the divider through gives, with $L_n = L_m/L_r$ and $x = f_s/f_r$,

```text
M(x) = Ln x^2 / sqrt( ((Ln + 1) x^2 - 1)^2 + (Q Ln x (x^2 - 1))^2 )
```

Write five functions.

- `llc_gain(x, Ln, Q)` — the formula above. Accept a scalar or a NumPy array for `x`
  and return the same shape; using `np.sqrt` throughout is enough to get that free.
- `second_resonance(Ln)` — the normalised lower resonance $f_{r2}/f_r$, which is
  $1/\sqrt{1 + L_n}$.
- `no_load_gain(x, Ln)` — the $Q \to 0$ limit, $L_nx^2/((1+L_n)x^2 - 1)$. This is the
  envelope the whole family sits under.
- `peak_gain(Ln, Q)` — return `(x_peak, M_peak)`, found by evaluating `llc_gain` on
  `np.linspace(second_resonance(Ln) * 1.001, 2.0, 20001)` and taking the largest. Use
  that grid exactly; the checks compare against it.
- `operating_x(Ln, Q, target)` — the frequency ratio that delivers `target` gain, found
  by **bisection** on the branch that runs from the peak upwards, where the gain
  decreases monotonically. Bracket on `[x_peak, 5.0]` and run 200 halvings.

Do not reach for a root finder; there is no SciPy here, and bisection on a monotone
branch is four lines.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def llc_gain(x, Ln, Q):
    """First-harmonic voltage gain of an LLC tank at frequency ratio x."""
    # TODO: Ln x^2 / sqrt( ((Ln+1) x^2 - 1)^2 + (Q Ln x (x^2 - 1))^2 ).
    return 0.0


def second_resonance(Ln):
    """The lower resonance fr2 / fr, where Lr and Lm resonate with Cr together."""
    # TODO
    return 0.0


def no_load_gain(x, Ln):
    """The Q -> 0 envelope of the gain family."""
    # TODO
    return 0.0


def peak_gain(Ln, Q):
    """Return (x_peak, M_peak) on the prescribed grid."""
    # TODO: np.linspace(second_resonance(Ln) * 1.001, 2.0, 20001), then argmax.
    return 0.0, 0.0


def operating_x(Ln, Q, target):
    """Bisect for the x above the peak that delivers `target` gain."""
    # TODO: bracket [x_peak, 5.0]; the gain decreases across it.
    return 0.0


if __name__ == "__main__":
    print("gain at resonance:", llc_gain(1.0, 5.0, 0.4))
    print("fr2/fr for Ln=5  :", round(second_resonance(5.0), 6))
    print("peak (Ln=5,Q=0.4):", peak_gain(5.0, 0.4))
    print("x for M=0.9      :", round(operating_x(5.0, 0.4, 0.9), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def llc_gain(x, Ln, Q):
    """First-harmonic voltage gain of an LLC tank at frequency ratio x."""
    x = np.asarray(x, dtype=float)
    num = Ln * x * x
    a = (Ln + 1.0) * x * x - 1.0
    b = Q * Ln * x * (x * x - 1.0)
    return num / np.sqrt(a * a + b * b)


def second_resonance(Ln):
    """The lower resonance fr2 / fr, where Lr and Lm resonate with Cr together."""
    return float(1.0 / np.sqrt(1.0 + Ln))


def no_load_gain(x, Ln):
    """The Q -> 0 envelope of the gain family."""
    x = np.asarray(x, dtype=float)
    return Ln * x * x / ((1.0 + Ln) * x * x - 1.0)


def peak_gain(Ln, Q):
    """Return (x_peak, M_peak) on the prescribed grid."""
    xs = np.linspace(second_resonance(Ln) * 1.001, 2.0, 20001)
    ms = llc_gain(xs, Ln, Q)
    i = int(np.argmax(ms))
    return float(xs[i]), float(ms[i])


def operating_x(Ln, Q, target):
    """Bisect for the x above the peak that delivers `target` gain."""
    lo = peak_gain(Ln, Q)[0]
    hi = 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if float(llc_gain(mid, Ln, Q)) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    print("gain at resonance:", llc_gain(1.0, 5.0, 0.4))
    print("fr2/fr for Ln=5  :", round(second_resonance(5.0), 6))
    print("peak (Ln=5,Q=0.4):", peak_gain(5.0, 0.4))
    print("x for M=0.9      :", round(operating_x(5.0, 0.4, 0.9), 6))
'''}],
                "hints": [
                    "Start `llc_gain` with `x = np.asarray(x, dtype=float)` and the whole function works for scalars and arrays alike.",
                    "`peak_gain` is `np.argmax` over the grid the brief names — do not invent your own grid, or the expected peak will differ in the sixth decimal.",
                    "For `operating_x`, remember which way the gain runs: it *decreases* as `x` rises above the peak, so keep `lo` on the high-gain side.",
                ],
                "tests": [
                    {"name": "the tank gain is exactly one at resonance for every load", "code": r'''
for _Ln, _Q in ((2.0, 0.1), (5.0, 0.4), (9.0, 2.0)):
    _g = float(llc_gain(1.0, _Ln, _Q))
    assert abs(_g - 1.0) < 1e-12, \
        f"at x=1 the series branch vanishes and M is 1 regardless of Ln and Q; got {_g} for Ln={_Ln}, Q={_Q}"
'''},
                    {"name": "the gain formula matches a hand-computed point", "code": r'''
_a = float(llc_gain(1.2, 5.0, 0.4))
assert abs(_a - 0.9335331128683328) < 1e-12, f"expected 0.933533 at x=1.2, got {_a}"
_b = float(llc_gain(0.85, 5.0, 0.4))
assert abs(_b - 1.072531236218735) < 1e-12, f"expected 1.072531 at x=0.85, got {_b}"
_c = float(llc_gain(2.0, 5.0, 0.4))
assert abs(_c - 0.7709433444916998) < 1e-12, f"expected 0.770943 at x=2.0, got {_c}"
'''},
                    {"name": "the lower resonance sits where Lr and Lm act together", "code": r'''
_x2 = second_resonance(5.0)
assert abs(_x2 - 0.4082482904638631) < 1e-12, \
    f"fr2/fr = 1/sqrt(1+Ln) = 0.408248 for Ln=5, got {_x2}"
assert second_resonance(0.0) == 1.0, \
    "with no magnetising inductance the two resonances coincide"
assert second_resonance(9.0) < second_resonance(3.0), \
    "a larger Lm pushes the lower resonance further down"
'''},
                    {"name": "the no-load envelope diverges at the lower resonance", "code": r'''
import numpy as np
_x2 = second_resonance(5.0)
assert abs(float(no_load_gain(1.0, 5.0)) - 1.0) < 1e-12, \
    "the envelope also passes through unity at x=1"
_near = float(no_load_gain(_x2 * 1.0005, 5.0))
assert _near > 200.0, \
    f"just above fr2 the unloaded gain should blow up, got {_near} — an unloaded LLC is uncontrollable there"
_far = float(no_load_gain(1.2, 5.0))
assert abs(_far - 0.9424083769633509) < 1e-12, f"expected 0.942408 at x=1.2, got {_far}"
'''},
                    {"name": "loading the tank pulls the curve down under its envelope", "code": r'''
for _x in (0.7, 0.85, 1.2, 1.8):
    _loaded = float(llc_gain(_x, 5.0, 0.4))
    _env = float(no_load_gain(_x, 5.0))
    assert _loaded < _env, \
        f"at x={_x} the loaded gain {_loaded} should sit below the Q->0 envelope {_env}"
'''},
                    {"name": "the peak is the boost budget and it shrinks with load", "code": r'''
_xp, _mp = peak_gain(5.0, 0.4)
assert abs(_xp - 0.4927590406811607) < 1e-12, f"peak should be at x=0.492759, got {_xp}"
assert abs(_mp - 1.3875368302361561) < 1e-12, f"peak gain should be 1.387537, got {_mp}"
assert _mp > 1.0, "an LLC can boost, unlike a series-resonant tank"
_, _heavy = peak_gain(5.0, 1.5)
assert abs(_heavy - 1.0097125798260875) < 1e-12, f"expected 1.009713 at Q=1.5, got {_heavy}"
assert _heavy < _mp, "heavier load leaves less boost headroom"
'''},
                    {"name": "the gain decreases monotonically above resonance", "code": r'''
import numpy as np
_xs = np.linspace(1.0, 5.0, 2001)
_gs = [float(llc_gain(float(x), 5.0, 0.4)) for x in _xs]
assert all(_gs[i] > _gs[i + 1] for i in range(len(_gs) - 1)), \
    "above resonance the curve must fall with frequency, or a frequency controller has no single answer"
assert abs(_gs[0] - 1.0) < 1e-12, "the sweep should start from unity gain at x=1"
'''},
                    {"name": "bisection lands on the frequency that gives the asked-for gain", "code": r'''
for _target in (0.95, 0.9, 0.8, 0.6):
    _x = operating_x(5.0, 0.4, _target)
    assert _x > 1.0, f"a gain below 1 must be reached above resonance, got x={_x}"
    _got = float(llc_gain(_x, 5.0, 0.4))
    assert abs(_got - _target) < 1e-9, \
        f"asked for {_target}, the returned x={_x} gives {_got}"
_x09 = operating_x(5.0, 0.4, 0.9)
assert abs(_x09 - 1.3294898262328445) < 1e-9, f"expected x=1.329490 for M=0.9, got {_x09}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Zero-voltage switching and the dead-time condition",
            "summary": "The whole point of the topology is that the drain is already at zero when the gate goes high. That is not automatic; it is a charge budget you have to meet.",
            "concepts": [
                "Hard turn-on dissipates $\\tfrac{1}{2}C_{oss}V_{in}^2$ inside the device, twice per cycle in a half-bridge, so the loss scales with frequency and kills the whole reason for going resonant.",
                "During the dead time the tank current must move the bridge midpoint from one rail to the other, which means delivering $2C_{oss}V_{in}$ of charge.",
                "In an LLC that current is the magnetising current, which is triangular and peaks at $V_{in}T_s/(8L_m)$ — it is deliberately *not* zero at the switching instant.",
                "Combining the two gives $L_m \\le t_d T_s/(16C_{oss})$, and $V_{in}$ cancels: the ZVS condition is a statement about the tank and the dead time, not about the line.",
                "The tank must also be operating on the inductive side, above the gain peak, so the current lags the bridge voltage and flows in the right direction during the dead time.",
                "Dead time longer than the swing needs is wasted conduction time, and eventually lets the midpoint drift back down.",
            ],
            "sandbox": {
                "title": "What a transition actually looks like",
                "visualiser": "switching",
                "minutes": 9,
                "initial": {"ls": 60, "coss": 400, "dead": 0},
                "brief": r'''
A single turn-on transition, drawn as a model rather than a simulation. The trace
labelled $V_{ds}$ is the drain voltage of the device about to turn on; the blue trace
is the current in it. The panel underneath does the arithmetic: it reports the ring
frequency $1/(2\pi\sqrt{LC})$ and the quarter-period $\tfrac{\pi}{2}\sqrt{LC}$ that the
parasitic tank needs to swing the drain to zero.

It opens at zero dead time — the device is gated on the instant the other one turns
off.
''',
                "notice": [
                    "At zero dead time the trace is amber. The drain voltage collapses discontinuously and then rings, and the blue current steps to full scale in the same instant. That overlap of a large voltage and a large current is the switching loss, and the panel names its cause: the device turns on into a charged capacitance.",
                    "Raise the dead time in its 5 ns steps. The panel says this tank needs about 8 ns to swing the drain down; at 10 ns the trace turns green and changes shape completely — $V_{ds}$ is now a clean quarter-cosine that reaches zero and stays there, and the current ramps over about 60 ns instead of stepping. That is what turning on at zero volts looks like.",
                    "Now push the dead time on to 200 ns. Nothing on the plot changes at all — once $V_{ds}$ has reached zero the drawn waveform stops depending on the dead time. In the model the extra time is simply invisible; in a real bridge it is conduction time you paid for and did not use, and eventually the midpoint starts to drift back.",
                    "Halve $C_{oss}$ to 200 pF and read the swing time: it falls to about 5 ns, not 4. The requirement goes as $\\sqrt{LC}$, so a device with half the output capacitance buys you about 30 per cent of the dead time, not 50 per cent.",
                ],
            },
            "derive": {
                "title": "Sizing the magnetising inductance for ZVS",
                "minutes": 15,
                "vars": ["C_oss", "V_in", "I_d", "I_m", "L_m", "T_s", "t_d", "f_s"],
                "brief": r'''
Between one device turning off and the other turning on there is a dead time $t_d$ in
which neither is conducting. During that window the bridge midpoint has to travel from
one rail to the other, driven only by whatever current the tank happens to be carrying.

Take $C_{oss}$ as the effective output capacitance of one device, and note that the
midpoint sees two of them: one charging as the other discharges.
''',
                "steps": [
                    {
                        "prompt": "Write the total charge that must be moved to swing the midpoint through the full rail voltage $V_{in}$.",
                        "answer": "2 C_{oss} V_{in}",
                        "placeholder": "2 C_{oss} V_{in}",
                        "hint": "One capacitor goes from $0$ to $V_{in}$ and the other from $V_{in}$ to $0$; both cost $C_{oss}V_{in}$.",
                        "deconstruct": [
                            "Charge on a capacitor changing by $\\Delta V$ is $C\\,\\Delta V$.",
                            "Two devices each swing the full rail, so the charges add.",
                        ],
                    },
                    {
                        "prompt": "Suppose the tank current is roughly constant at $I_d$ across the dead time. Write the shortest dead time that can deliver that charge.",
                        "answer": "\\frac{2 C_{oss} V_{in}}{I_d}",
                        "placeholder": "\\frac{2 C_{oss} V_{in}}{I_d}",
                        "hint": "Constant current for a time $t$ delivers charge $I t$.",
                        "deconstruct": [
                            "Charge delivered is $I_d t_d$.",
                            "Set that equal to the charge required and solve for $t_d$.",
                        ],
                    },
                    {
                        "prompt": "Now find that current. In an LLC at resonance the voltage across $L_m$ is clamped at half the rail, $V_{in}/2$, for each half-period $T_s/2$. The magnetising current is therefore a symmetric triangle. Write its peak value $I_m$.",
                        "given": "A constant voltage $V$ across an inductance $L$ for a time $\\Delta t$ changes its current by $V\\Delta t/L$.",
                        "answer": "\\frac{V_{in} T_s}{8 L_m}",
                        "placeholder": "\\frac{V_{in} T_s}{8 L_m}",
                        "hint": "The half-period gives the peak-to-peak swing; the peak is half of that because the triangle is symmetric about zero.",
                        "deconstruct": [
                            "Over $T_s/2$ the current changes by $(V_{in}/2)(T_s/2)/L_m = V_{in}T_s/(4L_m)$.",
                            "That is the peak-to-peak ripple, and the waveform is symmetric about zero.",
                        ],
                    },
                    {
                        "prompt": "Zero-voltage switching holds when the magnetising current is at least the current the charge budget demands. Set $I_m$ equal to that demand and solve for the largest magnetising inductance that still works.",
                        "answer": "\\frac{t_d T_s}{16 C_{oss}}",
                        "placeholder": "\\frac{t_d T_s}{16 C_{oss}}",
                        "hint": "Equate $V_{in}T_s/(8L_m)$ with $2C_{oss}V_{in}/t_d$ and notice what cancels.",
                        "deconstruct": [
                            "$\\frac{V_{in}T_s}{8L_m} = \\frac{2C_{oss}V_{in}}{t_d}$.",
                            "$V_{in}$ appears on both sides and cancels.",
                            "Rearranging leaves $L_m = \\frac{t_dT_s}{16C_{oss}}$.",
                        ],
                    },
                    {
                        "prompt": "Suppose the condition fails and the device turns on hard. Each transition dumps $\\tfrac{1}{2}C_{oss}V_{in}^2$, and a half-bridge does two of them per switching cycle. Write the average power lost, in terms of $C_{oss}$, $V_{in}$ and $f_s$.",
                        "answer": "C_{oss} V_{in}^2 f_s",
                        "placeholder": "C_{oss} V_{in}^{2} f_s",
                        "hint": "Energy per event times events per second.",
                        "deconstruct": [
                            "Two transitions per cycle at $\\tfrac{1}{2}C_{oss}V_{in}^2$ each is $C_{oss}V_{in}^2$ per cycle.",
                            "Multiply by $f_s$ cycles per second.",
                        ],
                    },
                ],
                "closing": r'''
The result $L_m \le t_dT_s/(16C_{oss})$ is the one to remember, and the reason is that
$V_{in}$ dropped out. Both the charge you must move and the current you have to move it
with are proportional to the rail, so the condition is independent of line voltage — it
depends only on the dead time, the switching period and the device.

That is a strong statement, and it comes with the fine print you should expect. $T_s$
is not constant in a frequency-controlled converter, so the binding case is the highest
switching frequency, which is the *high* line. And the whole argument assumes the
magnetising current is flowing in the direction that helps, which is only true on the
inductive side of the gain curve. Sitting below the peak, the current leads and the
transition happens the wrong way round.
''',
            },
            "lab": {
                "title": "Close the zero-voltage switching budget",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Six functions, each a direct transcription of the derivation.

- `swing_time(Lloop, Coss)` — the parasitic quarter-period $\tfrac{\pi}{2}\sqrt{LC}$
  the sandbox reports, in seconds.
- `min_dead_time(Coss, Vin, Id)` — the dead time needed at a constant current `Id`.
- `magnetising_peak(Vin, fs, Lm)` — the peak of the triangular magnetising current.
  Careful with the period: $T_s = 1/f_s$.
- `max_lm(td, fs, Coss)` — the largest magnetising inductance that still achieves ZVS.
  If `Vin` appears in your expression, go back to the derivation.
- `zvs_ok(Vin, fs, Lm, Coss, td)` — `True` when the available magnetising current can
  move the required charge in the dead time. Compare charges, not currents, so the
  boundary case is exact.
- `hard_switching_loss(Coss, Vin, fs)` — the average power a half-bridge burns when
  the condition fails.

`main.py` runs a 400 V, 100 kHz half-bridge with a 430 µH magnetising inductance,
250 pF of device capacitance and 300 ns of dead time. That design closes; the checks
also try one that does not.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def swing_time(Lloop, Coss):
    """Quarter period of the parasitic loop, in seconds."""
    # TODO: (pi/2) * sqrt(L * C).
    return 0.0


def min_dead_time(Coss, Vin, Id):
    """Shortest dead time that moves the midpoint at a constant current Id."""
    # TODO
    return 0.0


def magnetising_peak(Vin, fs, Lm):
    """Peak of the triangular magnetising current, in amps."""
    # TODO: Vin * Ts / (8 Lm), with Ts = 1 / fs.
    return 0.0


def max_lm(td, fs, Coss):
    """Largest magnetising inductance that still achieves ZVS."""
    # TODO: the line voltage cancels out of this one.
    return 0.0


def zvs_ok(Vin, fs, Lm, Coss, td):
    """True when the magnetising current can swing the node inside the dead time."""
    # TODO: compare delivered charge with required charge.
    return False


def hard_switching_loss(Coss, Vin, fs):
    """Average power lost when the transition is hard, in watts."""
    # TODO
    return 0.0


if __name__ == "__main__":
    Vin, fs, Lm, Coss, td = 400.0, 100e3, 430e-6, 250e-12, 300e-9
    print("swing time  :", swing_time(40e-9, Coss), "s")
    print("Im peak     :", round(magnetising_peak(Vin, fs, Lm), 6), "A")
    print("Lm limit    :", max_lm(td, fs, Coss), "H")
    print("ZVS holds   :", zvs_ok(Vin, fs, Lm, Coss, td))
    print("cost if not :", hard_switching_loss(Coss, Vin, fs), "W")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def swing_time(Lloop, Coss):
    """Quarter period of the parasitic loop, in seconds."""
    return float((np.pi / 2.0) * np.sqrt(Lloop * Coss))


def min_dead_time(Coss, Vin, Id):
    """Shortest dead time that moves the midpoint at a constant current Id."""
    return float(2.0 * Coss * Vin / Id)


def magnetising_peak(Vin, fs, Lm):
    """Peak of the triangular magnetising current, in amps."""
    return float(Vin / (8.0 * Lm * fs))


def max_lm(td, fs, Coss):
    """Largest magnetising inductance that still achieves ZVS."""
    return float(td / (16.0 * Coss * fs))


def zvs_ok(Vin, fs, Lm, Coss, td):
    """True when the magnetising current can swing the node inside the dead time."""
    delivered = magnetising_peak(Vin, fs, Lm) * td
    required = 2.0 * Coss * Vin
    return bool(delivered >= required)


def hard_switching_loss(Coss, Vin, fs):
    """Average power lost when the transition is hard, in watts."""
    return float(Coss * Vin * Vin * fs)


if __name__ == "__main__":
    Vin, fs, Lm, Coss, td = 400.0, 100e3, 430e-6, 250e-12, 300e-9
    print("swing time  :", swing_time(40e-9, Coss), "s")
    print("Im peak     :", round(magnetising_peak(Vin, fs, Lm), 6), "A")
    print("Lm limit    :", max_lm(td, fs, Coss), "H")
    print("ZVS holds   :", zvs_ok(Vin, fs, Lm, Coss, td))
    print("cost if not :", hard_switching_loss(Coss, Vin, fs), "W")
'''}],
                "hints": [
                    "`magnetising_peak` needs $T_s = 1/f_s$, so the $f_s$ ends up in the denominator alongside $L_m$.",
                    "In `max_lm` the rail voltage cancels — if yours still has `Vin` in it, re-do the last algebraic step.",
                    "Write `zvs_ok` as `Im * td >= 2 * Coss * Vin`. Comparing charges makes the boundary case land exactly on `True`.",
                ],
                "tests": [
                    {"name": "the swing time matches the quarter period the sandbox draws", "code": r'''
_t = swing_time(40e-9, 250e-12)
assert abs(_t - 4.967294132898051e-09) < 1e-18, \
    f"(pi/2)*sqrt(40nH * 250pF) is 4.9673 ns, got {_t}"
_t2 = swing_time(60e-9, 400e-12)
assert abs(_t2 - 7.695298980971183e-09) < 1e-18, f"expected 7.6953 ns, got {_t2}"
assert abs(swing_time(160e-9, 250e-12) / _t - 2.0) < 1e-12, \
    "the swing time goes as the square root of L, so four times L doubles it"
'''},
                    {"name": "the dead time follows from a charge budget", "code": r'''
_td = min_dead_time(250e-12, 400.0, 1.0)
assert abs(_td - 2.0e-07) < 1e-15, \
    f"2 * 250pF * 400V / 1A is 200 ns, got {_td} — remember there are two devices on the node"
assert abs(min_dead_time(250e-12, 400.0, 2.0) - 1.0e-07) < 1e-15, \
    "twice the current should halve the time"
'''},
                    {"name": "the magnetising current is triangular, not sinusoidal", "code": r'''
_i = magnetising_peak(400.0, 100e3, 430e-6)
assert abs(_i - 1.1627906976744187) < 1e-12, \
    f"Vin*Ts/(8*Lm) = 1.162791 A, got {_i} — check whether you used the period or the frequency"
assert abs(magnetising_peak(400.0, 200e3, 430e-6) - _i / 2.0) < 1e-12, \
    "doubling the frequency halves the volt-second product and so halves the peak"
assert abs(magnetising_peak(400.0, 100e3, 750e-6) - 0.6666666666666666) < 1e-12, \
    "a larger Lm gives less magnetising current, which is exactly the ZVS trade-off"
'''},
                    {"name": "the inductance limit does not depend on the line voltage", "code": r'''
_lm = max_lm(300e-9, 100e3, 250e-12)
assert abs(_lm - 7.5e-4) < 1e-12, f"td/(16*Coss*fs) = 750 uH, got {_lm}"
assert abs(max_lm(150e-9, 100e3, 250e-12) - 3.75e-4) < 1e-12, \
    "halving the dead time halves the allowed magnetising inductance"
_boundary = max_lm(300e-9, 100e3, 250e-12)
assert zvs_ok(400.0, 100e3, _boundary, 250e-12, 300e-9), \
    "at exactly the limit the budget balances, so ZVS should still be reported as met"
assert zvs_ok(150.0, 100e3, _boundary, 250e-12, 300e-9), \
    "the same limit must hold at a different rail voltage, because Vin cancels"
'''},
                    {"name": "the worked design passes and an over-sized Lm fails", "code": r'''
assert zvs_ok(400.0, 100e3, 430e-6, 250e-12, 300e-9) is True, \
    "430 uH is comfortably under the 750 uH limit, so this design should switch softly"
assert zvs_ok(400.0, 100e3, 900e-6, 250e-12, 300e-9) is False, \
    "900 uH starves the transition of current, so this one must be reported as failing"
assert zvs_ok(400.0, 100e3, 430e-6, 250e-12, 100e-9) is False, \
    "the same tank with only 100 ns of dead time no longer has time to swing"
'''},
                    {"name": "hard switching costs what the derivation says", "code": r'''
_p = hard_switching_loss(250e-12, 400.0, 100e3)
assert abs(_p - 4.0) < 1e-12, \
    f"Coss*Vin^2*fs = 4.0 W, got {_p} — two transitions of 1/2 C V^2 per cycle"
assert abs(hard_switching_loss(250e-12, 400.0, 200e3) - 8.0) < 1e-12, \
    "the loss is linear in frequency, which is why hard switching caps the frequency"
assert abs(hard_switching_loss(250e-12, 800.0, 100e3) - 16.0) < 1e-12, \
    "the loss is quadratic in voltage, which is why offline supplies care so much"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Where the efficiency actually goes",
            "summary": "Zero-voltage switching does not delete loss, it relocates it. A budget with four honest terms tells you more than any single figure of merit.",
            "concepts": [
                "The primary current is the load-carrying sinusoid plus the triangular magnetising current, and at resonance those two are in quadrature, so their RMS values add in quadrature.",
                "A symmetric triangle of peak $I_m$ has RMS $I_m/\\sqrt{3}$; a sinusoid of peak $I_p$ has RMS $I_p/\\sqrt{2}$.",
                "The magnetising current delivers no power to the load but is paid for in full through $R_{ds(on)}$ and the winding resistance. ZVS is bought with it.",
                "The secondary usually dominates at low output voltage: rectifying 20 A costs far more than switching 400 V, and the sinusoidal shape adds a $\\pi/(2\\sqrt{2}) \\approx 1.111$ form-factor penalty over a rectangular waveform of the same average.",
                "Core loss follows Steinmetz, $P = kf_s^{\\alpha}B^{\\beta}$, and at a fixed applied volt-second the flux swing goes as $1/f_s$, so the net dependence is $f_s^{\\alpha-\\beta}$ — usually a negative exponent.",
                "Efficiency is worst at light load, because the circulating current, the core loss and the gate loss are all essentially constant while the output power is not.",
            ],
            "sandbox": {
                "title": "The loss the transition either does or does not cost",
                "visualiser": "switching",
                "minutes": 8,
                "initial": {"ls": 40, "coss": 250, "dead": 0},
                "brief": r'''
The same model as module 3, now set to a 40 nH loop with a 250 pF device — plausible
numbers for a 400 V half-bridge running a few hundred watts. Read it this time with a
loss budget in mind rather than a waveform.
''',
                "notice": [
                    "At the opening dead time of zero, the panel spells out the mechanism: the energy $\\tfrac{1}{2}CV^2$ is dissipated every cycle. Put the numbers in — 250 pF at 400 V is 20 µJ per transition, two transitions per cycle, 100 kHz — and that is 4.0 W thrown away before any current has flowed to the load.",
                    "Step the dead time to 5 ns. The panel now says the swing takes about 5 ns and the trace turns green: that entire 4.0 W term is gone, and the blue current ramps rather than steps. This is the whole economic case for the topology.",
                    "What the plot does not show is the bill. The current that swung the node is the magnetising current, and it circulates through the device on-resistance and the primary winding for the entire cycle whether the converter is delivering 240 W or 20 W. Soft switching moves loss out of the transition and into conduction; it does not remove it.",
                    "Drag the loop inductance down to its minimum of 1 nH and read the ring frequency: 318 MHz. The swing time falls to about 1 ns, so a tight layout makes ZVS cheap in dead time — but that same number is the frequency your board has to survive on any transition that does go hard. The loss is at 100 kHz; the electromagnetic interference is three orders of magnitude above it.",
                ],
            },
            "derive": {
                "title": "The price of circulating current",
                "minutes": 14,
                "vars": ["I_p", "I_m", "R_ds", "f_s", "alpha", "beta", "B", "P_v", "k"],
                "brief": r'''
At resonance the primary carries two things at once: an approximately sinusoidal
current of peak $I_p$ that is in phase with the bridge voltage and actually delivers
the output power, and a triangular magnetising current of peak $I_m$ that lags it by a
quarter cycle and delivers nothing.

Because they are in quadrature, their mean squares add. That is the whole basis of
what follows.
''',
                "steps": [
                    {
                        "prompt": "Write the RMS value of a symmetric triangular waveform of peak value $I_m$.",
                        "answer": "\\frac{I_m}{\\sqrt{3}}",
                        "placeholder": "\\frac{I_m}{\\sqrt{3}}",
                        "hint": "Over a rising ramp from $-I_m$ to $+I_m$ the mean square works out to $I_m^2/3$.",
                        "deconstruct": [
                            "Take one quarter period rising linearly from $0$ to $I_m$.",
                            "The mean of $(I_m t/T)^2$ over that quarter is $I_m^2/3$.",
                            "The RMS is the square root of that.",
                        ],
                    },
                    {
                        "prompt": "The sinusoidal component has RMS $I_p/\\sqrt{2}$. Write the total RMS of the primary current, given that the two components are in quadrature.",
                        "answer": "\\sqrt{\\frac{I_p^2}{2} + \\frac{I_m^2}{3}}",
                        "placeholder": "\\sqrt{\\frac{I_p^{2}}{2} + \\frac{I_m^{2}}{3}}",
                        "hint": "Quadrature means the cross term averages to zero, so the mean squares simply add.",
                        "deconstruct": [
                            "Mean square of the sinusoid is $I_p^2/2$.",
                            "Mean square of the triangle is $I_m^2/3$.",
                            "Add them and take the root.",
                        ],
                    },
                    {
                        "prompt": "Exactly one of the two half-bridge devices conducts the primary current at any instant, so the pair together dissipate $R_{ds}$ times the mean square of that current. Write the total primary switch conduction loss.",
                        "answer": "R_{ds} \\left( \\frac{I_p^2}{2} + \\frac{I_m^2}{3} \\right)",
                        "placeholder": "R_{ds} \\left( \\frac{I_p^{2}}{2} + \\frac{I_m^{2}}{3} \\right)",
                        "hint": "You already have the mean square; the loss is just $R$ times it.",
                        "deconstruct": [
                            "Conduction loss is $R\\,I_{rms}^2$.",
                            "Squaring the previous answer removes the root.",
                        ],
                    },
                    {
                        "prompt": "What fraction of that loss is doing no useful work at all? Write the ratio of the magnetising contribution to the total.",
                        "answer": "\\frac{2 I_m^2}{3 I_p^2 + 2 I_m^2}",
                        "placeholder": "\\frac{2 I_m^{2}}{3 I_p^{2} + 2 I_m^{2}}",
                        "hint": "Take the ratio of the two mean-square terms to their sum, then clear the fractions by multiplying top and bottom by 6.",
                        "deconstruct": [
                            "The ratio is $\\frac{I_m^2/3}{I_p^2/2 + I_m^2/3}$.",
                            "Multiply numerator and denominator by 6.",
                        ],
                    },
                    {
                        "prompt": "Core loss density follows Steinmetz, $P_v = k f_s^{\\alpha} B^{\\beta}$. For a fixed applied volt-second the peak flux density goes as $B \\propto 1/f_s$. Substituting that, write how $P_v$ scales with $f_s$ — as a power of $f_s$.",
                        "answer": "f_s^{\\alpha - \\beta}",
                        "placeholder": "f_s^{\\alpha - \\beta}",
                        "hint": "Replace $B$ by $1/f_s$ and collect the exponents; the constants do not matter here.",
                        "deconstruct": [
                            "$B^{\\beta}$ becomes proportional to $f_s^{-\\beta}$.",
                            "Multiplying by $f_s^{\\alpha}$ adds the exponents.",
                        ],
                    },
                ],
                "closing": r'''
Two results, both slightly counter-intuitive.

The circulating-current fraction is not a small correction. With the worked numbers in
the lab it is about 20 per cent of the primary conduction loss at full load, and around
86 per cent at a fifth of full load — because $I_p$ shrinks with the load and $I_m$ does
not. That is the mechanism behind the light-load efficiency drop, and no amount of
better silicon fixes it; only a larger $L_m$ does, which trades directly against the
ZVS condition of module 3.

The Steinmetz exponent is negative for most ferrites — $\alpha \approx 1.5$ against
$\beta \approx 2.5$ gives $f_s^{-1}$ — so raising the switching frequency at a fixed
applied voltage actually *reduces* core loss. Frequency is limited by switching loss,
by gate drive and by the physical size you are willing to give the magnetics, not by
the core material.
''',
            },
            "lab": {
                "title": "Build an honest loss budget",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Six functions, then one number that means something.

- `primary_rms(Ip, Im)` — the quadrature sum you derived.
- `conduction_loss(Ip, Im, Rds, Rw)` — the primary conduction loss through the switch
  on-resistance and the winding resistance together, which both see the same RMS.
- `secondary_loss(Iout, Rsr)` — the output rectifier. The secondary current is the
  rectified sinusoid, so its RMS is $\pi/(2\sqrt{2})$ times the DC output current, and
  a full-bridge rectifier puts **two** devices in the path at all times.
- `core_loss(k, alpha, beta, fs, B, Ve)` — Steinmetz density times core volume.
- `switching_loss(Coss, Vin, fs, zvs)` — zero when `zvs` is true, and the module 3
  expression when it is not.
- `efficiency(Pout, losses)` — `losses` is any iterable of watts; return
  $P_{out}/(P_{out} + \sum P_{loss})$.

`main.py` budgets a 240 W converter at full load and at a fifth of it. The interesting
number is not the full-load efficiency; it is the difference between the two.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def primary_rms(Ip, Im):
    """RMS of a sinusoid of peak Ip in quadrature with a triangle of peak Im."""
    # TODO: sqrt(Ip^2 / 2 + Im^2 / 3).
    return 0.0


def conduction_loss(Ip, Im, Rds, Rw):
    """Primary-side conduction loss through switch and winding resistance."""
    # TODO
    return 0.0


def secondary_loss(Iout, Rsr):
    """Rectifier conduction loss, two devices in the path."""
    # TODO: the secondary RMS is pi / (2 sqrt(2)) times the DC output current.
    return 0.0


def core_loss(k, alpha, beta, fs, B, Ve):
    """Steinmetz core loss for a core of volume Ve, in watts."""
    # TODO: k * fs**alpha * B**beta * Ve.
    return 0.0


def switching_loss(Coss, Vin, fs, zvs):
    """Turn-on loss of a half-bridge: nothing if the transition is soft."""
    # TODO
    return 0.0


def efficiency(Pout, losses):
    """Output power over input power, given an iterable of loss terms."""
    # TODO
    return 0.0


if __name__ == "__main__":
    Im = 1.1627906976744187          # magnetising peak, fixed by the tank
    for Iout in (20.0, 4.0):
        Pout = 12.0 * Iout
        Ip = np.pi * Pout / 400.0
        terms = [
            conduction_loss(Ip, Im, 0.15, 0.25),
            secondary_loss(Iout, 0.005),
            core_loss(3.2, 1.46, 2.75, 100e3, 0.1, 11.5e-6),
            switching_loss(250e-12, 400.0, 100e3, True),
        ]
        print(round(Pout, 1), "W ->", [round(t, 4) for t in terms],
              "eta =", round(efficiency(Pout, terms), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def primary_rms(Ip, Im):
    """RMS of a sinusoid of peak Ip in quadrature with a triangle of peak Im."""
    return float(np.sqrt(Ip * Ip / 2.0 + Im * Im / 3.0))


def conduction_loss(Ip, Im, Rds, Rw):
    """Primary-side conduction loss through switch and winding resistance."""
    return float((Rds + Rw) * primary_rms(Ip, Im) ** 2)


def secondary_loss(Iout, Rsr):
    """Rectifier conduction loss, two devices in the path."""
    Isec = (np.pi / (2.0 * np.sqrt(2.0))) * Iout
    return float(2.0 * Rsr * Isec * Isec)


def core_loss(k, alpha, beta, fs, B, Ve):
    """Steinmetz core loss for a core of volume Ve, in watts."""
    return float(k * (fs ** alpha) * (B ** beta) * Ve)


def switching_loss(Coss, Vin, fs, zvs):
    """Turn-on loss of a half-bridge: nothing if the transition is soft."""
    if zvs:
        return 0.0
    return float(Coss * Vin * Vin * fs)


def efficiency(Pout, losses):
    """Output power over input power, given an iterable of loss terms."""
    total = float(sum(losses))
    return float(Pout / (Pout + total))


if __name__ == "__main__":
    Im = 1.1627906976744187          # magnetising peak, fixed by the tank
    for Iout in (20.0, 4.0):
        Pout = 12.0 * Iout
        Ip = np.pi * Pout / 400.0
        terms = [
            conduction_loss(Ip, Im, 0.15, 0.25),
            secondary_loss(Iout, 0.005),
            core_loss(3.2, 1.46, 2.75, 100e3, 0.1, 11.5e-6),
            switching_loss(250e-12, 400.0, 100e3, True),
        ]
        print(round(Pout, 1), "W ->", [round(t, 4) for t in terms],
              "eta =", round(efficiency(Pout, terms), 6))
'''}],
                "hints": [
                    "`conduction_loss` is $(R_{ds}+R_w)$ times the *square* of `primary_rms` — do not take the root twice.",
                    "In `secondary_loss` the factor is $\\pi/(2\\sqrt{2}) \\approx 1.1107$, and it multiplies the DC output current before squaring.",
                    "`efficiency` should call `sum(losses)` once; passing it a list of four terms is the intended use.",
                ],
                "tests": [
                    {"name": "the two current components add in quadrature", "code": r'''
_r = primary_rms(2.0, 1.2)
assert abs(_r - 1.5748015748023623) < 1e-12, \
    f"sqrt(4/2 + 1.44/3) = 1.574802, got {_r} — a triangle is not a sinusoid"
assert abs(primary_rms(2.0, 0.0) - 1.4142135623730951) < 1e-12, \
    "with no magnetising current the answer is just the sinusoid RMS Ip/sqrt(2)"
assert abs(primary_rms(0.0, 2.0) - 1.1547005383792517) < 1e-12, \
    "with no load current the answer is the triangle RMS Im/sqrt(3)"
'''},
                    {"name": "conduction loss uses the mean square, not the RMS", "code": r'''
_p = conduction_loss(2.0, 1.2, 0.15, 0.25)
assert abs(_p - 0.992) < 1e-12, \
    f"(0.15+0.25) * (4/2 + 1.44/3) = 0.992 W, got {_p}"
assert abs(conduction_loss(4.0, 1.2, 0.15, 0.25) - 3.392) < 1e-12, \
    "doubling the load current roughly quadruples this term, so it dominates at full load"
'''},
                    {"name": "the secondary pays a form-factor penalty", "code": r'''
_s = secondary_loss(20.0, 0.005)
assert abs(_s - 4.934802200544679) < 1e-12, \
    f"2 * 5 mohm * (1.1107 * 20 A)^2 = 4.9348 W, got {_s} — check the pi/(2 sqrt 2) factor and the two devices"
_naive = 2.0 * 0.005 * 20.0 ** 2
assert _s > _naive, \
    "a rectified sinusoid has a higher RMS than a rectangle of the same average, so this must exceed 4.0 W"
assert abs(secondary_loss(4.0, 0.005) - 0.19739208802178718) < 1e-12, \
    "at a fifth of the current this term falls by a factor of 25"
'''},
                    {"name": "core loss follows Steinmetz and falls with frequency", "code": r'''
_c = core_loss(3.2, 1.46, 2.75, 100e3, 0.1, 11.5e-6)
assert abs(_c - 1.3057132723795573) < 1e-9, f"expected 1.305713 W, got {_c}"
_double = core_loss(3.2, 1.46, 2.75, 200e3, 0.05, 11.5e-6)
assert abs(_double - 0.5339727866827284) < 1e-9, f"expected 0.533973 W, got {_double}"
assert _double < _c, \
    "doubling fs at fixed volt-seconds halves B, and with beta above alpha the core loss falls"
'''},
                    {"name": "soft switching removes a term that hard switching does not", "code": r'''
_hard = switching_loss(250e-12, 400.0, 100e3, False)
assert abs(_hard - 4.0) < 1e-12, f"a hard transition costs Coss*Vin^2*fs = 4.0 W, got {_hard}"
_soft = switching_loss(250e-12, 400.0, 100e3, True)
assert _soft == 0.0, f"with ZVS this term is zero, got {_soft}"
assert _hard > _soft, "the whole design effort of module 3 exists to make this difference"
'''},
                    {"name": "the full-load budget reproduces the worked efficiency", "code": r'''
import numpy as np
_Im = 1.1627906976744187
_Ip = float(np.pi * 240.0 / 400.0)
_terms = [
    conduction_loss(_Ip, _Im, 0.15, 0.25),
    secondary_loss(20.0, 0.005),
    core_loss(3.2, 1.46, 2.75, 100e3, 0.1, 11.5e-6),
    switching_loss(250e-12, 400.0, 100e3, True),
]
assert abs(_terms[0] - 0.8908891444248553) < 1e-9, f"conduction term should be 0.890889 W, got {_terms[0]}"
_eta = efficiency(240.0, _terms)
assert abs(_eta - 0.9711432683822959) < 1e-9, f"expected 0.971143, got {_eta}"
assert 0.0 < _eta < 1.0, "an efficiency outside (0, 1) means the losses went into the wrong place"
'''},
                    {"name": "light load is the harder case, and the circulating current is why", "code": r'''
import numpy as np
_Im = 1.1627906976744187
def _budget(Iout):
    Pout = 12.0 * Iout
    Ip = float(np.pi * Pout / 400.0)
    return Pout, Ip, [
        conduction_loss(Ip, _Im, 0.15, 0.25),
        secondary_loss(Iout, 0.005),
        core_loss(3.2, 1.46, 2.75, 100e3, 0.1, 11.5e-6),
        switching_loss(250e-12, 400.0, 100e3, True),
    ]
_Pf, _Ipf, _tf = _budget(20.0)
_Pl, _Ipl, _tl = _budget(4.0)
_ef, _el = efficiency(_Pf, _tf), efficiency(_Pl, _tl)
assert abs(_el - 0.96556537497873) < 1e-9, f"expected 0.965565 at a fifth of load, got {_el}"
assert _el < _ef, "light-load efficiency must come out lower, not higher"
_frac_full = 2 * _Im ** 2 / (3 * _Ipf ** 2 + 2 * _Im ** 2)
_frac_light = 2 * _Im ** 2 / (3 * _Ipl ** 2 + 2 * _Im ** 2)
assert abs(_frac_full - 0.20235696963487648) < 1e-9, f"expected 0.202357 at full load, got {_frac_full}"
assert _frac_light > 0.8, \
    f"at light load almost all the primary conduction loss is circulating current; got {_frac_light}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Design a 240 W LLC half-bridge",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
One converter, designed end to end and then proved to close on all three of the things
that can sink it: gain range, zero-voltage switching, and efficiency.

The specification is fixed in `spec.py`, which you must not edit. In summary: a 400 V
nominal bus that may sag to 350 V or rise to 420 V, feeding 12 V at up to 20 A through
a half-bridge LLC with a full-bridge secondary rectifier. The tank resonates at
100 kHz, the inductance ratio is $L_n = L_m/L_r = 5$, and the loaded quality factor at
full load is to be 0.4.

## What to build

Ten functions in `main.py`, in this order. Each one is short, and each one is used by
the ones after it.

1. `turns_ratio()` — anchor the design at the nominal line with the tank at resonance,
   where the gain is exactly 1. A half-bridge presents $V_{in}/2$ to the tank and a
   full-bridge rectifier presents $V_o$ to the secondary, so $n = V_{in,nom}/(2V_o)$.
2. `r_ac(Iout)` — the reflected load, using the load resistance at that output current.
3. `tank()` — return `(Lr, Cr, Lm)`. You know $\omega_r$, and you know
   $Z_0 = Q_{full}R_{ac}$ at full load; two equations, two unknowns, then
   $L_m = L_nL_r$.
4. `gain(x, Ln, Q)` — the LLC gain from module 2, array-friendly.
5. `peak_gain(Ln, Q)` — `(x_peak, M_peak)` on `np.linspace(1/sqrt(1+Ln) * 1.001, 2.0,
   20001)`, exactly as in module 2.
6. `required_gain(Vin)` — what the tank must deliver at that line voltage to hold the
   output. It is $2nV_o/V_{in}$.
7. `operating_x(Vin)` — bisect on `[x_peak, 5.0]` for the frequency ratio that meets
   the requirement, using `Ln` and `Q_FULL` from the spec.
8. `zvs_margin(Vin)` — the ratio of delivered charge to required charge during the dead
   time, at the operating frequency for that line. Above 1 means ZVS holds. Remember
   that the switching frequency, and hence the magnetising current, changes with line.
9. `losses(Iout, Vin)` — a dict with exactly the keys `"conduction"`, `"secondary"`,
   `"core"` and `"gate"`, in watts. Gate loss is $2Q_gV_gf_s$.
10. `efficiency(Iout, Vin)` — output power over input power.

## Suggested order

Get `turns_ratio`, `r_ac` and `tank` right first and check the resonant frequency and
$Q$ come back out of `Lr`, `Cr` — that closes the loop on your algebra before anything
depends on it. Then the gain functions, which you already wrote in module 2. ZVS and
the budget come last and are almost free once the operating frequency is available.

The primary load-carrying current peak is $I_p = \pi P_{out}/V_{in}$, which follows
from equating $P_{out}$ to the product of the fundamental RMS voltage and current at
resonance. Use that; do not re-derive it in the loop.
''',
        "deliverables": [
            "`turns_ratio`, `r_ac` and `tank` returning a tank whose resonant frequency and loaded Q reproduce the specification to within one part in a million.",
            "`gain`, `peak_gain`, `required_gain` and `operating_x`, with the operating frequency found by bisection and verified to deliver the requested gain.",
            "`zvs_margin`, reporting the ratio of delivered to required charge at the operating point for a given line voltage, correct at both line extremes.",
            "`losses` returning the four named terms in watts, and `efficiency` combining them with the output power.",
            "A short comment at the top of `main.py` recording the tank values you computed, the frequency range the converter has to sweep, and the worst-case ZVS margin.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, and no root finder beyond the bisection you write yourself.",
            "`spec.py` is read-only. Every constant must come from it; nothing may be hard-coded in `main.py`.",
            "`peak_gain` must use the grid the brief specifies, so that the expected peak matches to twelve decimal places.",
            "First-harmonic approximation throughout. Do not attempt a time-domain simulation; the point is that the phasor model closes.",
        ],
        "rubric": [
            {"criterion": "Tank synthesis", "weight": 25,
             "evidence": "The returned Lr, Cr and Lm reproduce the specified resonant frequency, the specified loaded Q at full load and the specified inductance ratio, each to within one part in a million."},
            {"criterion": "Gain range", "weight": 25,
             "evidence": "The gain is exactly one at resonance for every Ln and Q, the peak gain matches the reference grid search, and the bisected operating frequency delivers the required gain at all three line voltages."},
            {"criterion": "Zero-voltage switching", "weight": 25,
             "evidence": "The ZVS margin exceeds one at low, nominal and high line, is correctly worst at high line where the switching frequency is highest, and drops below one when the magnetising inductance is tripled."},
            {"criterion": "Loss budget", "weight": 15,
             "evidence": "The four loss terms are named, individually correct against the worked values, and combine into a full-load efficiency that matches the reference to nine decimal places."},
            {"criterion": "Light-load behaviour", "weight": 10,
             "evidence": "Efficiency at a fifth of full load is computed and is demonstrably lower than at full load, for the right reason: the circulating and fixed terms do not shrink with the output."},
        ],
        "hints": [
            "From $\\omega_r = 1/\\sqrt{L_rC_r}$ and $Z_0 = \\sqrt{L_r/C_r}$ you get $L_r = Z_0/\\omega_r$ and $C_r = 1/(Z_0\\omega_r)$ directly — no simultaneous equations needed.",
            "`required_gain(spec.V_IN_NOM)` must come out as exactly 1.0 if your turns ratio is right; check that before going further.",
            "In `zvs_margin`, compute `fs = operating_x(Vin) * spec.F_R` first, then the magnetising peak at that frequency, then `Im * T_DEAD / (2 * C_OSS * Vin)`.",
            "The rail voltage cancels out of the ZVS *limit* but not out of the margin at a fixed tank, because the operating frequency moves with line. High line is the binding case.",
        ],
        "files": [
            {"name": "spec.py", "ro": True, "content": r'''
"""The design specification. Do not edit — the checks rely on these numbers."""

# --- output
V_OUT = 12.0           # V
I_OUT_MAX = 20.0       # A, so 240 W

# --- input bus
V_IN_NOM = 400.0       # V
V_IN_MIN = 350.0       # V
V_IN_MAX = 420.0       # V

# --- tank
F_R = 100e3            # Hz, series resonance
LN = 5.0               # Lm / Lr
Q_FULL = 0.4           # loaded quality factor at full load

# --- devices and timing
C_OSS = 250e-12        # F, effective output capacitance of one primary device
T_DEAD = 300e-9        # s
R_DS = 0.15            # ohm, primary switch on-resistance
R_W = 0.25             # ohm, primary winding resistance
R_SR = 0.005           # ohm, one secondary rectifier
Q_G = 60e-9            # C, primary gate charge
V_G = 12.0             # V, gate drive rail

# --- magnetics
K_C = 3.2              # Steinmetz coefficient, SI units
ALPHA = 1.46
BETA = 2.75
B_PK = 0.1             # T, peak flux density
V_E = 11.5e-6          # m^3, effective core volume
'''},
            {"name": "main.py", "content": r'''
import numpy as np
import spec

# Design record:
#   Lr, Cr, Lm  -> TODO
#   frequency range for 350..420 V -> TODO
#   worst-case ZVS margin -> TODO


def turns_ratio():
    """Primary-to-secondary turns ratio, anchored at nominal line and resonance."""
    # TODO
    return 0.0


def r_ac(Iout):
    """Load resistance reflected to the primary through rectifier and transformer."""
    # TODO: 8 n^2 RL / pi^2, with RL = V_OUT / Iout.
    return 0.0


def tank():
    """Return (Lr, Cr, Lm) in henries and farads."""
    # TODO: Z0 = Q_FULL * r_ac(I_OUT_MAX), then Lr = Z0/wr and Cr = 1/(Z0 wr).
    return 0.0, 0.0, 0.0


def gain(x, Ln, Q):
    """LLC first-harmonic voltage gain at frequency ratio x."""
    # TODO
    return 0.0


def peak_gain(Ln, Q):
    """Return (x_peak, M_peak) on the prescribed grid."""
    # TODO
    return 0.0, 0.0


def required_gain(Vin):
    """Tank gain needed to hold the output at this line voltage."""
    # TODO
    return 0.0


def operating_x(Vin):
    """Frequency ratio the controller settles at, by bisection."""
    # TODO
    return 0.0


def zvs_margin(Vin):
    """Delivered charge over required charge during the dead time."""
    # TODO
    return 0.0


def losses(Iout, Vin):
    """Loss terms in watts, keyed conduction / secondary / core / gate."""
    # TODO
    return {}


def efficiency(Iout, Vin):
    """Output power over input power."""
    # TODO
    return 0.0


if __name__ == "__main__":
    Lr, Cr, Lm = tank()
    print("n  =", round(turns_ratio(), 4))
    print("Lr =", Lr, " Cr =", Cr, " Lm =", Lm)
    for V in (spec.V_IN_MIN, spec.V_IN_NOM, spec.V_IN_MAX):
        print(f"  Vin={V:6.1f}  M={required_gain(V):.5f}"
              f"  x={operating_x(V):.5f}  zvs={zvs_margin(V):.3f}")
    print("eta full  =", round(efficiency(spec.I_OUT_MAX, spec.V_IN_NOM), 6))
    print("eta 1/5   =", round(efficiency(spec.I_OUT_MAX / 5.0, spec.V_IN_NOM), 6))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
import spec

# Design record:
#   Lr = 86.00 uH, Cr = 29.45 nF, Lm = 430.0 uH  (Z0 = 54.04 ohm, Rac = 135.09 ohm)
#   frequency range for 350..420 V -> 74.82 kHz to 113.60 kHz
#   worst-case ZVS margin -> 1.535 at high line, where fs is highest


def turns_ratio():
    """Primary-to-secondary turns ratio, anchored at nominal line and resonance."""
    return float(spec.V_IN_NOM / (2.0 * spec.V_OUT))


def r_ac(Iout):
    """Load resistance reflected to the primary through rectifier and transformer."""
    n = turns_ratio()
    RL = spec.V_OUT / Iout
    return float(8.0 * n * n * RL / (np.pi * np.pi))


def tank():
    """Return (Lr, Cr, Lm) in henries and farads."""
    Z0 = spec.Q_FULL * r_ac(spec.I_OUT_MAX)
    wr = 2.0 * np.pi * spec.F_R
    Lr = Z0 / wr
    Cr = 1.0 / (Z0 * wr)
    return float(Lr), float(Cr), float(spec.LN * Lr)


def gain(x, Ln, Q):
    """LLC first-harmonic voltage gain at frequency ratio x."""
    x = np.asarray(x, dtype=float)
    num = Ln * x * x
    a = (Ln + 1.0) * x * x - 1.0
    b = Q * Ln * x * (x * x - 1.0)
    return num / np.sqrt(a * a + b * b)


def peak_gain(Ln, Q):
    """Return (x_peak, M_peak) on the prescribed grid."""
    x2 = 1.0 / np.sqrt(1.0 + Ln)
    xs = np.linspace(x2 * 1.001, 2.0, 20001)
    ms = gain(xs, Ln, Q)
    i = int(np.argmax(ms))
    return float(xs[i]), float(ms[i])


def required_gain(Vin):
    """Tank gain needed to hold the output at this line voltage."""
    return float(2.0 * turns_ratio() * spec.V_OUT / Vin)


def operating_x(Vin):
    """Frequency ratio the controller settles at, by bisection."""
    target = required_gain(Vin)
    lo = peak_gain(spec.LN, spec.Q_FULL)[0]
    hi = 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if float(gain(mid, spec.LN, spec.Q_FULL)) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def zvs_margin(Vin):
    """Delivered charge over required charge during the dead time."""
    _, _, Lm = tank()
    fs = operating_x(Vin) * spec.F_R
    Im = Vin / (8.0 * Lm * fs)
    return float(Im * spec.T_DEAD / (2.0 * spec.C_OSS * Vin))


def losses(Iout, Vin):
    """Loss terms in watts, keyed conduction / secondary / core / gate."""
    _, _, Lm = tank()
    fs = operating_x(Vin) * spec.F_R
    Pout = spec.V_OUT * Iout
    Ip = np.pi * Pout / Vin
    Im = Vin / (8.0 * Lm * fs)
    mean_sq = Ip * Ip / 2.0 + Im * Im / 3.0
    Isec = (np.pi / (2.0 * np.sqrt(2.0))) * Iout
    return {
        "conduction": float((spec.R_DS + spec.R_W) * mean_sq),
        "secondary": float(2.0 * spec.R_SR * Isec * Isec),
        "core": float(spec.K_C * (fs ** spec.ALPHA) * (spec.B_PK ** spec.BETA) * spec.V_E),
        "gate": float(2.0 * spec.Q_G * spec.V_G * fs),
    }


def efficiency(Iout, Vin):
    """Output power over input power."""
    Pout = spec.V_OUT * Iout
    total = sum(losses(Iout, Vin).values())
    return float(Pout / (Pout + total))


if __name__ == "__main__":
    Lr, Cr, Lm = tank()
    print("n  =", round(turns_ratio(), 4))
    print("Lr =", Lr, " Cr =", Cr, " Lm =", Lm)
    for V in (spec.V_IN_MIN, spec.V_IN_NOM, spec.V_IN_MAX):
        print(f"  Vin={V:6.1f}  M={required_gain(V):.5f}"
              f"  x={operating_x(V):.5f}  zvs={zvs_margin(V):.3f}")
    print("eta full  =", round(efficiency(spec.I_OUT_MAX, spec.V_IN_NOM), 6))
    print("eta 1/5   =", round(efficiency(spec.I_OUT_MAX / 5.0, spec.V_IN_NOM), 6))
'''},
        ],
        "tests": [
            {"name": "the turns ratio and reflected load follow from the specification", "code": r'''
import spec
_n = turns_ratio()
assert abs(_n - 16.666666666666668) < 1e-9, \
    f"n = V_IN_NOM / (2 * V_OUT) = 16.6667, got {_n} — a half-bridge presents half the rail to the tank"
_r = r_ac(spec.I_OUT_MAX)
assert abs(_r - 135.09491152311705) < 1e-6, \
    f"the tank should see 135.0949 ohm at full load, got {_r} — check the 8/pi^2 rectifier factor"
assert r_ac(spec.I_OUT_MAX / 5.0) > _r, \
    "a lighter load reflects a larger resistance, which is what lowers Q"
'''},
            {"name": "the synthesised tank reproduces its own specification", "code": r'''
import numpy as np, spec
_Lr, _Cr, _Lm = tank()
assert _Lr > 0 and _Cr > 0 and _Lm > 0, "all three tank elements must be positive"
_fr = 1.0 / (2.0 * np.pi * np.sqrt(_Lr * _Cr))
assert abs(_fr / spec.F_R - 1.0) < 1e-9, \
    f"1/(2 pi sqrt(Lr Cr)) should give back F_R = 100 kHz, got {_fr}"
_Z0 = np.sqrt(_Lr / _Cr)
assert abs(_Z0 / r_ac(spec.I_OUT_MAX) - spec.Q_FULL) < 1e-9, \
    f"Z0/Rac should give back Q_FULL = 0.4, got {_Z0 / r_ac(spec.I_OUT_MAX)}"
assert abs(_Lm / _Lr - spec.LN) < 1e-9, f"Lm/Lr should be LN = 5, got {_Lm / _Lr}"
assert abs(_Lr - 8.600409182186532e-05) < 1e-15, f"expected Lr = 86.004 uH, got {_Lr}"
'''},
            {"name": "the gain is pinned to one at resonance whatever the load", "code": r'''
for _Q in (0.1, 0.4, 1.0, 3.0):
    _g = float(gain(1.0, 5.0, _Q))
    assert abs(_g - 1.0) < 1e-12, \
        f"the load-independent crossing at x=1 is what fixes the turns ratio; got {_g} at Q={_Q}"
assert abs(float(gain(1.2, 5.0, 0.4)) - 0.9335331128683328) < 1e-12, \
    "the gain formula does not match the reference at x=1.2"
'''},
            {"name": "the peak gain covers the low-line requirement with margin", "code": r'''
import spec
_xp, _mp = peak_gain(spec.LN, spec.Q_FULL)
assert abs(_xp - 0.4927590406811607) < 1e-12, f"expected the peak at x=0.492759, got {_xp}"
assert abs(_mp - 1.3875368302361561) < 1e-12, f"expected a peak gain of 1.387537, got {_mp}"
_need = required_gain(spec.V_IN_MIN)
assert abs(_need - 1.1428571428571428) < 1e-12, f"350 V needs a gain of 1.142857, got {_need}"
assert _mp > _need, \
    "the tank cannot hold the output at low line if its peak gain is below what low line demands"
'''},
            {"name": "the operating frequency delivers the gain it was asked for", "code": r'''
import spec
assert abs(required_gain(spec.V_IN_NOM) - 1.0) < 1e-12, \
    "at nominal line the design sits at resonance, so the required gain is exactly 1"
for _V in (spec.V_IN_MIN, spec.V_IN_NOM, spec.V_IN_MAX):
    _x = operating_x(_V)
    _got = float(gain(_x, spec.LN, spec.Q_FULL))
    assert abs(_got - required_gain(_V)) < 1e-9, \
        f"at {_V} V the bisection returned x={_x}, which gives {_got} not {required_gain(_V)}"
assert abs(operating_x(spec.V_IN_NOM) - 1.0) < 1e-6, \
    f"nominal line must land on resonance, got x={operating_x(spec.V_IN_NOM)}"
assert operating_x(spec.V_IN_MIN) < 1.0 < operating_x(spec.V_IN_MAX), \
    "low line has to boost, so it runs below resonance; high line has to buck and runs above"
assert abs(operating_x(spec.V_IN_MAX) - 1.1359563532024364) < 1e-9, \
    f"expected x=1.135956 at 420 V, got {operating_x(spec.V_IN_MAX)}"
'''},
            {"name": "zero-voltage switching holds across the whole line range", "code": r'''
import spec
_m = {V: zvs_margin(V) for V in (spec.V_IN_MIN, spec.V_IN_NOM, spec.V_IN_MAX)}
for _V, _v in _m.items():
    assert _v > 1.0, f"ZVS fails at {_V} V with a margin of {_v}"
assert abs(_m[spec.V_IN_MAX] - 1.5353609831486645) < 1e-6, \
    f"expected a high-line margin of 1.53536, got {_m[spec.V_IN_MAX]}"
assert abs(_m[spec.V_IN_MIN] - 2.3309355277888884) < 1e-6, \
    f"expected a low-line margin of 2.33094, got {_m[spec.V_IN_MIN]}"
assert _m[spec.V_IN_MAX] < _m[spec.V_IN_MIN], \
    "high line runs at the highest frequency and so has the least magnetising current — it is the binding case"
'''},
            {"name": "the loss budget names four terms and each one is right", "code": r'''
import spec
_L = losses(spec.I_OUT_MAX, spec.V_IN_NOM)
assert set(_L) == {"conduction", "secondary", "core", "gate"}, \
    f"losses() must return exactly those four keys, got {sorted(_L)}"
assert abs(_L["conduction"] - 0.8908719906738032) < 1e-6, f"conduction should be 0.890872 W, got {_L['conduction']}"
assert abs(_L["secondary"] - 4.934802200544679) < 1e-6, f"secondary should be 4.934802 W, got {_L['secondary']}"
assert abs(_L["core"] - 1.305713272379557) < 1e-6, f"core should be 1.305713 W, got {_L['core']}"
assert abs(_L["gate"] - 0.144) < 1e-9, f"gate should be 0.144 W, got {_L['gate']}"
assert _L["secondary"] > _L["conduction"], \
    "at 12 V and 20 A the secondary dominates — rectifying the current costs more than switching the voltage"
'''},
            {"name": "efficiency is computed and light load is the worse case", "code": r'''
import spec
_ef = efficiency(spec.I_OUT_MAX, spec.V_IN_NOM)
assert abs(_ef - 0.9705777936970412) < 1e-9, f"expected 0.970578 at full load, got {_ef}"
_el = efficiency(spec.I_OUT_MAX / 5.0, spec.V_IN_NOM)
assert abs(_el - 0.9627768352703711) < 1e-9, f"expected 0.962777 at a fifth of load, got {_el}"
assert _el < _ef, \
    "the circulating, core and gate terms do not shrink with the load, so light load must be less efficient"
'''},
        ],
    },
}
