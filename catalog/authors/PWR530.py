"""PWR530 — Magnetics and Thermal Design.

Authoring rules, the same as CTRL510:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

Every numeric assertion below was produced by running the reference solution, not
by hand. The sandbox notices were written against the draw functions in
src/studio.js: the `switching` visualiser rings at 1/(2*pi*sqrt(LC)) and turns
green when the dead time covers a quarter period, and the `bode` visualiser is a
second-order low-pass whose corner sits at wn with magnitude K/(2*zeta).
"""

COURSE = {
    "id": "PWR530",
    "title": "Magnetics and Thermal Design",
    "band": 4,
    "level": "Advanced",
    "prereqs": ["PWR510"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◐",
    "summary": (
        "A converter's switching cell is a schematic; its transformer and its heatsink "
        "are the parts that decide whether the thing works. This course treats magnetics "
        "as a loss budget rather than an inductance value: core loss from the Steinmetz "
        "relation, copper loss from Dowell's skin and proximity analysis, a core chosen "
        "by area product, and a temperature rise computed from a thermal resistance "
        "network. The four fit together, and none of them can be settled alone."
    ),
    "outcomes": [
        "Predict core loss from a Steinmetz fit, and say which of frequency and flux density is the dangerous one in a given design change.",
        "Compute skin depth and Dowell's ac resistance factor, and choose a conductor thickness knowing that thicker is not always better.",
        "Size a transformer by area product, and explain why the core area cancels out of the derivation.",
        "Build a junction-to-ambient thermal network, find the power a device may dissipate, and identify when loss and temperature form a runaway loop.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that sizes, winds and thermally verifies a 500 VA transformer across a frequency sweep.",
    "reading": [
        "*Transformer and Inductor Design Handbook*, McLyman — for the area-product tables.",
        "*Fundamentals of Power Electronics*, Erickson & Maksimović — chapters 13 and 14.",
        "Dowell, P.L., 'Effects of eddy currents in transformer windings', Proc. IEE 113(8), 1966.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Core loss and the Steinmetz relation",
            "summary": "Core loss is an empirical power law in frequency and flux density. Knowing which exponent bites decides every design move.",
            "concepts": [
                "Faraday's law fixes the flux swing from the applied volt-seconds: $B_m = \\frac{V}{4 f N A_e}$ for a square wave.",
                "The Steinmetz relation $P_v = k f^\\alpha B_m^\\beta$ is a *fit*, valid only over the range it was measured on.",
                "Typical ferrite values are $\\alpha \\approx 1.4$ and $\\beta \\approx 2.5$ — the flux exponent is the larger one, which is why halving $B_m$ beats halving $f$.",
                "At fixed applied volts and turns, raising $f$ *lowers* core loss: $B_m \\propto \\frac{1}{f}$, so the $B_m^\\beta$ factor falls as $f^{-\\beta}$, and $\\beta > \\alpha$ leaves $P_v \\propto f^{\\alpha-\\beta}$.",
                "Fitting $k$, $\\alpha$ and $\\beta$ is linear least squares once you take logarithms of all three axes.",
            ],
            "sandbox": {
                "title": "The waveform the core actually sees",
                "visualiser": "switching",
                "minutes": 8,
                "initial": {"ls": 30, "coss": 150, "dead": 0},
                "brief": r'''
Before any loss algebra, look at what a switching cell puts across a winding. The
amber or green trace is the drain voltage, the blue one is the switch current, and
the window is 600 ns around a single turn-on.

Steinmetz coefficients are fitted on a clean sinusoid at a stated frequency. The
excitation here is not that, and the difference is the reason a first core-loss
estimate is usually optimistic.
''',
                "notice": [
                    "Start with the dead time at zero. $V_{ds}$ holds at the rail for the first 100 ns, then drops to 0.9 and rings about zero at 75 MHz, while the blue current has already stepped to full scale. The overlap is turn-on loss; the ring is excitation at a frequency your Steinmetz fit never saw.",
                    "Raise the dead time to 5 ns. The trace turns green: the tank now walks $V_{ds}$ down a cosine quarter-cycle to zero and holds it there, and the current ramps in over 60 ns instead of stepping. That quarter-cycle takes $\\frac{\\pi}{2}\\sqrt{LC} = 3.3$ ns at 30 nH and 150 pF, which is why 5 ns is enough.",
                    "Take the loop inductance to 80 nH and $C_{oss}$ to 600 pF. The ring falls to 23 MHz and the quarter-cycle stretches to 10.9 ns, so 5 ns no longer covers it and the trace goes back to amber. Only the product $LC$ sets both numbers: 20 nH with 300 pF draws exactly the same curve as 40 nH with 150 pF.",
                ],
            },
            "derive": {
                "title": "Where the frequency exponent really goes",
                "minutes": 14,
                "vars": ["V_pk", "N", "A_e", "f", "B_m", "V", "alpha", "beta", "k", "P_v"],
                "brief": r'''
A winding of $N$ turns sits on a core of effective cross-section $A_e$. Core loss
per unit volume follows the Steinmetz relation

$$P_v = k f^{\alpha} B_m^{\beta}$$

with $\alpha \approx 1.4$ and $\beta \approx 2.5$ for a power ferrite. The question
this derivation settles is what happens to $P_v$ when you raise the switching
frequency — which is not what the $f^{\alpha}$ suggests.
''',
                "steps": [
                    {
                        "prompt": "First, Faraday. The flux density is sinusoidal, $B(t) = B_m \\sin(2\\pi f t)$. Write the peak induced voltage $V_{pk}$ in terms of $N$, $A_e$, $f$ and $B_m$.",
                        "answer": "2\\pi f N A_e B_m",
                        "hint": "$V = N A_e \\frac{dB}{dt}$, and differentiating a sine brings down a factor $2\\pi f$.",
                        "deconstruct": [
                            "The flux linkage is $N A_e B(t)$.",
                            "Its derivative is $N A_e B_m (2\\pi f)\\cos(2\\pi f t)$, whose peak is the cosine's peak of 1.",
                        ],
                    },
                    {
                        "prompt": "Now the real case. The winding is driven by a square wave of amplitude $V$ at frequency $f$: $+V$ for half a period, then $-V$. The flux ramps linearly, and over the positive half it travels the full swing $2 B_m$. Write $B_m$ in terms of $V$, $N$, $A_e$ and $f$.",
                        "given": "Half a period is $\\frac{1}{2f}$.",
                        "answer": "\\frac{V}{4 f N A_e}",
                        "hint": "With a constant applied voltage, $\\Delta B = \\frac{V \\Delta t}{N A_e}$. Set that equal to $2 B_m$.",
                        "deconstruct": [
                            "$\\Delta B = \\frac{V}{N A_e} \\cdot \\frac{1}{2f}$ over the positive half period.",
                            "That travel is $2 B_m$, so $B_m$ is half of it.",
                        ],
                    },
                    {
                        "prompt": "Substitute that $B_m$ into $P_v = k f^{\\alpha} B_m^{\\beta}$, holding $V$, $N$ and $A_e$ fixed. Write the resulting exponent of $f$.",
                        "answer": "\\alpha - \\beta",
                        "hint": "$B_m$ carries a factor $\\frac{1}{f}$, and it is raised to the power $\\beta$.",
                        "deconstruct": [
                            "$B_m^{\\beta}$ contributes $f^{-\\beta}$.",
                            "Multiplying by the explicit $f^{\\alpha}$ gives $f^{\\alpha-\\beta}$.",
                        ],
                    },
                    {
                        "prompt": "You double the switching frequency with the same applied voltage and the same turns. Write the factor by which $P_v$ changes, in terms of $\\alpha$ and $\\beta$.",
                        "answer": "2^{\\alpha - \\beta}",
                        "hint": "You already have the exponent. Doubling $f$ multiplies $f^{p}$ by $2^{p}$.",
                        "deconstruct": [
                            "$P_v$ depends on frequency only through $f^{\\alpha-\\beta}$.",
                            "With $\\alpha = 1.4$ and $\\beta = 2.5$ that exponent is negative, so the factor is less than one.",
                        ],
                    },
                    {
                        "prompt": "Back at the original frequency, you instead double the number of turns, keeping $V$ and $f$ fixed. Write the factor by which $P_v$ changes, in terms of $\\beta$.",
                        "answer": "2^{-\\beta}",
                        "hint": "$B_m$ carries a factor $\\frac{1}{N}$ and nothing else in $P_v$ depends on $N$.",
                        "deconstruct": [
                            "Doubling $N$ halves $B_m$.",
                            "Halving $B_m$ multiplies $B_m^{\\beta}$ by $2^{-\\beta}$.",
                        ],
                    },
                ],
                "closing": r'''
Both moves cut core loss sharply, and neither is free. Raising $f$ hands the bill to
the switching cell and to the winding, which is module 2. Adding turns raises the dc
resistance in direct proportion and the window fills up, which is module 3. The
Steinmetz relation on its own will always tell you to run fast with few volts per
turn; the rest of the course is the reason you do not.
''',
            },
            "quiz": {
                "title": "A power law with two exponents",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Faraday fixes the flux swing from the applied volt-seconds. At a fixed applied voltage, doubling the switching frequency does what to $B_m$?",
                        "opts": ["Halves it", "Doubles it", "Leaves it unchanged", "Quadruples it"],
                        "a": 0,
                        "why": r"""
$B_m = V/(K_f fNA_e)$ — the same voltage applied for half as long puts half the flux
into the core. This is the mechanism behind every "run it faster and it gets smaller"
argument in power electronics, and it is why frequency and core size trade against each
other at all.
""",
                    },
                    {
                        "q": "With $P_v = kf^{\\alpha}B_m^{\\beta}$ and $\\alpha \\approx 1.4$, doubling the frequency at *constant* flux density multiplies the core loss by:",
                        "opts": ["About 2.6", "Exactly 2", "About 1.4", "About 4"],
                        "a": 0,
                        "why": r"""
$2^{1.4} = 2.64$. Taken alone this looks like an argument against raising the frequency —
and it is the wrong comparison, because holding $B_m$ constant while raising $f$ means
you deliberately kept the core the same size. The honest comparison is the next question.
""",
                    },
                    {
                        "q": "Now double the frequency with the same volt-seconds, so $B_m$ halves too. What happens to the core loss?",
                        "opts": [
                            "It falls, to about 0.47 of what it was",
                            "It rises, by about 2.6",
                            "It is unchanged",
                            "It falls to about 0.18",
                        ],
                        "a": 0,
                        "why": r"""
$2^{1.4} \times 0.5^{2.5} = 2.64 \times 0.177 = 0.47$. The flux exponent is the larger of
the two and it is working in your favour, so switching faster *reduces* core loss for the
same core — which is the actual reason converters moved from 20 kHz to hundreds. It is
also why $\beta$, not $\alpha$, is the number to look up carefully: it is the one doing
most of the work.
""",
                    },
                    {
                        "q": "What kind of relation is Steinmetz?",
                        "opts": [
                            "An empirical fit, valid only over the range it was fitted on",
                            "A derivation from Maxwell's equations",
                            "An exact result for ferrites",
                            "A worst-case bound",
                        ],
                        "a": 0,
                        "why": r"""
A curve fit to measured data, with $k$, $\alpha$ and $\beta$ extracted over a stated
frequency and flux range — and extrapolating outside that range is not conservative, it is
simply unsupported. It also assumes sinusoidal excitation, which a converter does not
provide; the iGSE and its relatives exist to correct for exactly that, and the correction
is not small for a square wave.
""",
                    },
                    {
                        "q": "You must halve the core loss and can change only one variable. Which gives it to you with the smallest change?",
                        "opts": [
                            "$B_m$, because $\\beta$ is the larger exponent",
                            "$f$, because $\\alpha$ is smaller",
                            "$k$, by choosing a different material",
                            "The core volume",
                        ],
                        "a": 0,
                        "why": r"""
With $\beta = 2.5$, a 24% reduction in $B_m$ halves the loss; with $\alpha = 1.4$ it would
take a 39% reduction in frequency. The larger exponent is the more powerful lever, which
is why adding turns — which lowers $B_m$ directly — is the first thing to try when a core
runs hot. Changing material is often the right answer in practice and is not a change of
*variable*, and the volume enters as a multiplier rather than through an exponent.
""",
                    },
                ],
            },
            "lab": {
                "title": "Predict and fit core loss",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Four functions.

`flux_density(V, N, Ae, f)` returns the peak flux density for square-wave
excitation, $B_m = \frac{V}{4 f N A_e}$, in tesla.

`loss_density(k, alpha, beta, f, Bm)` returns $k f^{\alpha} B_m^{\beta}$ in W/m³.

`core_loss(k, alpha, beta, f, Bm, Ve)` multiplies that by the effective core volume
`Ve` in m³ and returns watts.

`fit_steinmetz(f, Bm, Pv)` takes three equal-length sequences of measurements and
returns the tuple `(k, alpha, beta)`. Take logarithms of all three and the relation
becomes linear:

```text
ln(Pv) = ln(k) + alpha * ln(f) + beta * ln(Bm)
```

so build the design matrix `[1, ln f, ln Bm]` and hand it to `np.linalg.lstsq`.
Remember to exponentiate the intercept before returning `k`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def flux_density(V, N, Ae, f):
    """Peak flux density in tesla for a square wave of amplitude V at frequency f."""
    # TODO: Faraday over half a period.
    return 0.0


def loss_density(k, alpha, beta, f, Bm):
    """Steinmetz volumetric core loss in W/m^3."""
    # TODO
    return 0.0


def core_loss(k, alpha, beta, f, Bm, Ve):
    """Total core loss in watts for an effective core volume Ve in m^3."""
    # TODO
    return 0.0


def fit_steinmetz(f, Bm, Pv):
    """Least-squares fit of (k, alpha, beta) on log axes."""
    # TODO: build [1, ln f, ln Bm] and solve for the three coefficients.
    return (0.0, 0.0, 0.0)


if __name__ == "__main__":
    Bm = flux_density(48.0, 12, 97e-6, 100e3)
    print("Bm =", round(Bm, 6), "T")
    print("Pv =", round(loss_density(1.5, 1.4, 2.5, 100e3, 0.1), 2), "W/m^3")
    print("P  =", round(core_loss(1.5, 1.4, 2.5, 100e3, 0.1, 7.64e-6), 4), "W")
    print("fit:", fit_steinmetz([50e3, 100e3], [0.1, 0.1], [1.0, 2.0]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def flux_density(V, N, Ae, f):
    """Peak flux density in tesla for a square wave of amplitude V at frequency f."""
    return float(V) / (4.0 * float(f) * float(N) * float(Ae))


def loss_density(k, alpha, beta, f, Bm):
    """Steinmetz volumetric core loss in W/m^3."""
    return float(k) * float(f) ** float(alpha) * float(Bm) ** float(beta)


def core_loss(k, alpha, beta, f, Bm, Ve):
    """Total core loss in watts for an effective core volume Ve in m^3."""
    return loss_density(k, alpha, beta, f, Bm) * float(Ve)


def fit_steinmetz(f, Bm, Pv):
    """Least-squares fit of (k, alpha, beta) on log axes."""
    f = np.asarray(f, dtype=float)
    Bm = np.asarray(Bm, dtype=float)
    Pv = np.asarray(Pv, dtype=float)
    A = np.column_stack([np.ones_like(f), np.log(f), np.log(Bm)])
    sol = np.linalg.lstsq(A, np.log(Pv), rcond=None)[0]
    return (float(np.exp(sol[0])), float(sol[1]), float(sol[2]))


if __name__ == "__main__":
    Bm = flux_density(48.0, 12, 97e-6, 100e3)
    print("Bm =", round(Bm, 6), "T")
    print("Pv =", round(loss_density(1.5, 1.4, 2.5, 100e3, 0.1), 2), "W/m^3")
    print("P  =", round(core_loss(1.5, 1.4, 2.5, 100e3, 0.1, 7.64e-6), 4), "W")
    print("fit:", fit_steinmetz([50e3, 100e3], [0.1, 0.1], [1.0, 2.0]))
'''}],
                "hints": [
                    "`flux_density` is one line: the 4 in the denominator is two halves of the period and two halves of the swing.",
                    "Python's `**` accepts fractional exponents directly, so `f ** alpha` is all that $f^{\\alpha}$ needs.",
                    "`np.column_stack([np.ones_like(f), np.log(f), np.log(Bm)])` is the design matrix; `np.linalg.lstsq(A, np.log(Pv), rcond=None)[0]` is the coefficient vector.",
                ],
                "tests": [
                    {"name": "the flux swing follows the applied volt-seconds", "code": r'''
_b = flux_density(48.0, 12, 97e-6, 100e3)
assert abs(_b - 0.10309278350515463) < 1e-12, \
    f"48 V on 12 turns of 97 mm^2 at 100 kHz gives 0.1031 T, got {_b}"
'''},
                    {"name": "doubling the frequency halves the flux density", "code": r'''
_b1 = flux_density(48.0, 12, 97e-6, 100e3)
_b2 = flux_density(48.0, 12, 97e-6, 200e3)
assert _b1 > 0.0, "flux density must be positive before the ratio means anything"
assert abs(_b2 / _b1 - 0.5) < 1e-12, \
    f"the same volts for half as long is half the flux swing, got a ratio of {_b2 / _b1}"
'''},
                    {"name": "Steinmetz loss density has the right magnitude", "code": r'''
_p = loss_density(1.5, 1.4, 2.5, 100e3, 0.1)
assert abs(_p - 47434.16490252565) < 1e-6, \
    f"k=1.5, alpha=1.4, beta=2.5 at 100 kHz and 0.1 T gives 47434 W/m^3, got {_p}"
'''},
                    {"name": "at fixed flux the frequency exponent is alpha", "code": r'''
_p1 = loss_density(1.5, 1.4, 2.5, 100e3, 0.1)
_p2 = loss_density(1.5, 1.4, 2.5, 200e3, 0.1)
assert _p1 > 0.0, "loss density must be positive before the ratio means anything"
assert abs(_p2 / _p1 - 2.639015821545593) < 1e-9, \
    f"holding Bm fixed, doubling f should cost 2**1.4 = 2.639, got {_p2 / _p1}"
'''},
                    {"name": "total loss is loss density times volume", "code": r'''
_p = core_loss(1.5, 1.4, 2.5, 100e3, 0.1, 7.64e-6)
assert abs(_p - 0.36239701985529593) < 1e-12, \
    f"an ETD34 core of 7640 mm^3 should dissipate 0.3624 W here, got {_p}"
_q = core_loss(1.5, 1.4, 2.5, 100e3, 0.1, 15.28e-6)
assert abs(_q - 2.0 * _p) < 1e-12, "twice the core volume is twice the loss"
'''},
                    {"name": "an exact data set recovers its own coefficients", "code": r'''
import numpy as np
_f = np.array([50e3, 50e3, 50e3, 100e3, 100e3, 100e3,
               200e3, 200e3, 200e3, 400e3, 400e3, 400e3])
_b = np.array([0.05, 0.1, 0.2] * 4)
_p = 1.5 * _f ** 1.4 * _b ** 2.5
_k, _a, _be = fit_steinmetz(_f, _b, _p)
assert abs(_k - 1.5) < 1e-8, f"k should come back as 1.5, got {_k}"
assert abs(_a - 1.4) < 1e-8, f"alpha should come back as 1.4, got {_a}"
assert abs(_be - 2.5) < 1e-8, f"beta should come back as 2.5, got {_be}"
'''},
                    {"name": "the fit survives five per cent scatter", "code": r'''
import numpy as np
_f = np.array([50e3, 50e3, 50e3, 100e3, 100e3, 100e3,
               200e3, 200e3, 200e3, 400e3, 400e3, 400e3])
_b = np.array([0.05, 0.1, 0.2] * 4)
_p = 1.5 * _f ** 1.4 * _b ** 2.5
_rng = np.random.default_rng(7)
_noisy = _p * np.exp(_rng.normal(0.0, 0.05, size=_p.shape))
_k, _a, _be = fit_steinmetz(_f, _b, _noisy)
assert abs(_a - 1.4) < 0.03, f"the exponents are robust to scatter: alpha came out {_a}"
assert abs(_be - 2.5) < 0.03, f"the exponents are robust to scatter: beta came out {_be}"
assert 1.0 < _k < 2.0, \
    f"the intercept is the fragile one, but it should still bracket 1.5; got {_k}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Skin and proximity effect",
            "summary": "Above a few tens of kilohertz a conductor stops using its own middle, and its neighbours make that worse.",
            "concepts": [
                "Skin depth $\\delta = \\sqrt{\\frac{\\rho}{\\pi f \\mu}}$: 0.21 mm in copper at 100 kHz, and it falls only as $\\sqrt{f}$.",
                "Dowell's normalised thickness $\\Delta = \\frac{h}{\\delta}$ is where frequency enters: at a fixed layer count the whole ac factor is a function of $\\Delta$ alone.",
                "The proximity term scales as $m^2$ in the layer count, but it vanishes as $\\Delta^4$ in thin foil. At $\\Delta = 1$ it first overtakes the skin term at four layers; only in the thick limit does it do so from two layers up.",
                "For thick conductors $\\frac{R_{ac}}{R_{dc}} \\to \\Delta \\frac{2m^2+1}{3}$, so $R_{ac}$ itself grows only as $\\sqrt{f}$ — but from a much higher floor.",
                "There is an optimum thickness, not a maximum: past $\\Delta \\approx 1$ the extra copper carries no current and only couples to its neighbours.",
            ],
            "sandbox": {
                "title": "Reading a power law off log axes",
                "visualiser": "bode",
                "minutes": 7,
                "initial": {"wn": 20, "zeta": 0.7, "K": 1},
                "brief": r'''
This is a second-order low-pass, not a winding. It is here as a ruler: the frequency
laws in this module are straight lines on log–log axes, and the only skill needed to
check one is counting decades of slope.

The magnitude plot is dB against $\omega$ on a log axis, the phase plot below it is
degrees, and the amber dot marks the corner.
''',
                "notice": [
                    "Set $\\zeta$ to 1.5 and follow the magnitude above the corner. It falls 40 dB per decade — a hundredfold in amplitude for a tenfold in frequency, which is a power law of exponent $-2$. Skin-limited resistance rises as $\\sqrt{f}$, which on the same axes would be a straight line of $+10$ dB per decade.",
                    "With $\\omega_n = 20$ and $K = 1$ the curve starts at 0 dB on the left and reaches the bottom of the frame at $-80$ dB at $\\omega = 2000$. That is exactly two decades past the corner at 40 dB each. Count decades, never hertz.",
                    "Drop $\\zeta$ to 0.05. A 20 dB peak appears just below the corner and the phase dives through $-90°$ towards $-180°$. A winding's $R_{ac}(f)$ is monotonic and cannot do this, so a measured impedance that peaks is resonating with the interwinding capacitance, not showing you proximity effect.",
                ],
            },
            "derive": {
                "title": "From skin depth to Dowell's layer factor",
                "minutes": 14,
                "vars": ["delta", "rho", "mu", "f", "h", "Delta", "R_ac", "R_dc", "m", "p"],
                "brief": r'''
A plane wave entering a conductor decays as $e^{-x/\delta}$, with

$$\delta = \sqrt{\frac{2\rho}{\omega\mu}}$$

where $\rho$ is resistivity and $\mu$ the permeability. Dowell's analysis takes that
result, applies it to a foil of thickness $h$ in a winding of $m$ layers, and gives

$$\frac{R_{ac}}{R_{dc}} = \Delta\left[\frac{\sinh 2\Delta + \sin 2\Delta}{\cosh 2\Delta - \cos 2\Delta} + \frac{2(m^2-1)}{3}\cdot\frac{\sinh \Delta - \sin \Delta}{\cosh \Delta + \cos \Delta}\right], \qquad \Delta = \frac{h}{\delta}$$

You will not derive that here. You will find out what it says.
''',
                "steps": [
                    {
                        "prompt": "Substitute $\\omega = 2\\pi f$ into the skin depth. Write $\\delta$ in terms of $\\rho$, $f$ and $\\mu$.",
                        "answer": "\\sqrt{\\frac{\\rho}{\\pi f \\mu}}",
                        "hint": "The 2 in the numerator and the 2 in $2\\pi f$ cancel.",
                        "deconstruct": [
                            "$\\frac{2\\rho}{\\omega\\mu} = \\frac{2\\rho}{2\\pi f \\mu}$.",
                            "Cancel the twos and take the root.",
                        ],
                    },
                    {
                        "prompt": "Write the factor by which $\\delta$ changes when the frequency goes up by a hundred.",
                        "answer": "\\frac{1}{10}",
                        "hint": "$\\delta$ depends on $f$ only through $\\frac{1}{\\sqrt{f}}$.",
                        "deconstruct": [
                            "$\\delta \\propto f^{-1/2}$.",
                            "A hundredfold in $f$ is a tenfold the other way in $\\delta$.",
                        ],
                    },
                    {
                        "prompt": "For $\\Delta \\gg 1$ the bracket's first term tends to 1 and the second to $\\frac{2(m^2-1)}{3}$. Take the single-layer case $m = 1$ and write $\\frac{R_{ac}}{R_{dc}}$ for a thick foil, in terms of $h$ and $\\delta$.",
                        "answer": "\\frac{h}{\\delta}",
                        "hint": "With $m = 1$ the proximity term vanishes and the bracket is just 1, leaving the $\\Delta$ that multiplies it.",
                        "deconstruct": [
                            "$\\frac{R_{ac}}{R_{dc}} \\to \\Delta \\cdot 1 = \\Delta$.",
                            "And $\\Delta$ was defined as $\\frac{h}{\\delta}$. Physically: only one skin depth of a foil $h$ thick is carrying anything.",
                        ],
                    },
                    {
                        "prompt": "Keeping $\\Delta \\gg 1$ but letting $m$ be general, the whole factor becomes $\\Delta\\frac{2m^2+1}{3}$. Write the ratio of a four-layer winding's ac resistance to a one-layer winding's, at the same $\\Delta$ and the same $R_{dc}$.",
                        "answer": "11",
                        "hint": "Evaluate $\\frac{2m^2+1}{3}$ at $m = 4$ and at $m = 1$, and divide.",
                        "deconstruct": [
                            "At $m = 4$: $\\frac{2 \\cdot 16 + 1}{3} = 11$.",
                            "At $m = 1$: $\\frac{2 + 1}{3} = 1$.",
                        ],
                    },
                    {
                        "prompt": "Hold the foil thickness $h$ and the layer count $m$ fixed and raise the frequency, staying in the thick regime. Then $R_{ac} \\propto f^{p}$. Write $p$.",
                        "answer": "\\frac{1}{2}",
                        "hint": "$R_{dc}$ does not depend on frequency at all, and $\\Delta = \\frac{h}{\\delta}$ carries all of it.",
                        "deconstruct": [
                            "$\\delta \\propto f^{-1/2}$, so $\\Delta \\propto f^{1/2}$.",
                            "$R_{ac} = R_{dc} \\Delta \\frac{2m^2+1}{3}$, and only $\\Delta$ moves.",
                        ],
                    },
                ],
                "closing": r'''
The frequency dependence is mild — $\sqrt{f}$, not $f$ or $f^2$ — but the layer count
is not, and $m$ is something you choose. The lab that follows finds the thickness
that minimises $R_{ac}$ rather than $\frac{R_{ac}}{R_{dc}}$, and the answer is never
"as thick as it fits".
''',
            },
            "blanks": {
                "title": "The conductor stops using its own middle",
                "minutes": 8,
                "caption": "skin.py — depth, normalised thickness, and the layer count",
                "lang": "python",
                "brief": r"""
Above a few tens of kilohertz a wire's DC resistance stops being the number that matters,
and its neighbours make things worse than the wire alone would. Fill in the chain from
material constants to a winding decision.
""",
                "listing": """delta = sqrt(rho / (pi * f * mu))

# In copper this is 0.21 mm at ___ ,
# and it falls as the square root of frequency.

# Dowell's normalised thickness -- the only place frequency enters his curves:
Delta = ___

# The proximity term scales as ___ in the number of layers,
# but it vanishes as ___ .

# So for a many-layer winding the standard remedy is ___ .
""",
                "blanks": [
                    {
                        "prompt": "The anchor value worth memorising.",
                        "hole": "?",
                        "opts": ["100 kHz", "1 kHz", "10 MHz", "50 Hz"],
                        "a": 0,
                        "why": "0.21 mm at 100 kHz in copper, and the square-root scaling gets you everywhere else: 0.66 mm at 10 kHz, 0.066 mm at 10 MHz. One anchor plus one exponent replaces the formula in practice.",
                        "whys": [
                            "0.21 mm at 100 kHz in copper, and the square-root scaling gets you everywhere else: 0.66 mm at 10 kHz, 0.066 mm at 10 MHz. One anchor plus one exponent replaces the formula in practice.",
                            "At 1 kHz the skin depth is about 2.1 mm, larger than most conductors, which is why mains-frequency magnetics can ignore the effect entirely.",
                            "At 10 MHz it is around 21 micrometres, thinner than most foils and the reason RF windings look nothing like power ones.",
                            "At 50 Hz it is nearly 10 mm, which is why it matters only in busbars and very large machines.",
                        ],
                    },
                    {
                        "prompt": "Dowell normalises the conductor against the skin depth.",
                        "hole": "?",
                        "opts": ["h / delta", "delta / h", "h * delta", "h**2 / delta"],
                        "a": 0,
                        "why": "Layer thickness over skin depth — a dimensionless number, which is why Dowell's curves are universal and one chart covers every material and frequency. Everything about the winding's AC behaviour is a function of $\\Delta$ and the layer count, and of nothing else.",
                        "whys": [
                            "Layer thickness over skin depth — a dimensionless number, which is why Dowell's curves are universal and one chart covers every material and frequency. Everything about the winding's AC behaviour is a function of $\\Delta$ and the layer count, and of nothing else.",
                            "Inverted, so a thick conductor at high frequency would score *low* and appear harmless — exactly the wrong way round.",
                            "A product has dimensions of area and is not what the curves are plotted against.",
                            "Not dimensionless, so it cannot be the universal parameter.",
                        ],
                    },
                    {
                        "prompt": "How does the proximity term grow with layers?",
                        "hole": "?",
                        "opts": ["m ** 2", "m", "sqrt(m)", "it does not"],
                        "a": 0,
                        "why": "Quadratically. Each layer sits in the field of every layer before it, so the field builds across the winding and the induced eddy currents build with it — which is why a five-layer winding can dissipate far more than five times a single layer's AC loss. It is the dominant surprise in transformer design.",
                        "whys": [
                            "Quadratically. Each layer sits in the field of every layer before it, so the field builds across the winding and the induced eddy currents build with it — which is why a five-layer winding can dissipate far more than five times a single layer's AC loss. It is the dominant surprise in transformer design.",
                            "Linear growth would be unremarkable — it would just mean more copper. The whole problem is that it is worse than proportional.",
                            "A square root would mean layers get progressively cheaper, which is the opposite of what is measured.",
                            "It grows sharply; a single-layer winding and a ten-layer one of the same total copper behave completely differently at high frequency.",
                        ],
                    },
                    {
                        "prompt": "But the term vanishes in which limit?",
                        "hole": "?",
                        "opts": [
                            "Delta -> 0, thin layers compared with the skin depth",
                            "Delta -> infinity, thick layers",
                            "m -> infinity",
                            "f -> infinity",
                        ],
                        "a": 0,
                        "why": "A layer much thinner than the skin depth cannot support a meaningful circulating current, so the proximity term goes away however many layers there are. This is the entire justification for foil and for litz wire: make each conductor thin enough and the $m^2$ has nothing to act on.",
                        "whys": [
                            "A layer much thinner than the skin depth cannot support a meaningful circulating current, so the proximity term goes away however many layers there are. This is the entire justification for foil and for litz wire: make each conductor thin enough and the $m^2$ has nothing to act on.",
                            "Thick layers are the bad case — that is where the eddy currents have room to circulate.",
                            "More layers make it worse, not better.",
                            "Rising frequency shrinks the skin depth and raises $\\Delta$ for a fixed conductor, which makes it worse.",
                        ],
                    },
                    {
                        "prompt": "So what is done to a many-layer winding?",
                        "hole": "?",
                        "opts": [
                            "interleave primary and secondary to halve the peak field",
                            "add more turns",
                            "use a thicker conductor",
                            "raise the switching frequency",
                        ],
                        "a": 0,
                        "why": "Splitting the primary either side of the secondary makes the field build up and back down twice instead of once, so the peak MMF halves and the loss — which goes as its square — falls by about four. It costs an extra winding operation and a little more interwinding capacitance, and it is the single most effective change available.",
                        "whys": [
                            "Splitting the primary either side of the secondary makes the field build up and back down twice instead of once, so the peak MMF halves and the loss — which goes as its square — falls by about four. It costs an extra winding operation and a little more interwinding capacitance, and it is the single most effective change available.",
                            "More turns means more layers, which is what the $m^2$ punishes.",
                            "A thicker conductor raises $\\Delta$ and can increase AC resistance even as it lowers the DC value — the classic case where adding copper makes a winding hotter.",
                            "Higher frequency shrinks the skin depth and makes the problem worse.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Dowell's factor and the optimum foil",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Three functions.

`skin_depth(rho, f, mu_r=1.0)` returns $\sqrt{\frac{\rho}{\pi f \mu_r \mu_0}}$ in
metres, with `MU0` already defined for you.

`dowell(h, delta, m)` returns Dowell's ac resistance factor for a foil of thickness
`h`, skin depth `delta` and `m` layers. With $\Delta = \frac{h}{\delta}$,

```text
F = D*(sinh(2D) + sin(2D))/(cosh(2D) - cos(2D))
  + D*(2*(m*m - 1)/3)*(sinh(D) - sin(D))/(cosh(D) + cos(D))
```

`optimal_delta(m)` returns the $\Delta$ that minimises the *ac resistance itself*,
not the ratio. The foil width is fixed by the window, so thickening the foil raises
its cross-section in proportion to $\Delta$ and drops the dc resistance as
$\frac{1}{\Delta}$; the quantity to minimise is therefore $\frac{F(\Delta)}{\Delta}$.
Scan `np.linspace(0.05, 5.0, 4951)` — a grid of exactly 0.001 — and return the
value of $\Delta$ at the minimum.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

MU0 = 4e-7 * np.pi
RHO_CU = 1.724e-8      # ohm.m, annealed copper at 20 C


def skin_depth(rho, f, mu_r=1.0):
    """Skin depth in metres."""
    # TODO
    return 0.0


def dowell(h, delta, m):
    """Dowell's ratio of ac to dc resistance for m layers of foil thickness h."""
    # TODO: build Delta = h/delta, then the skin term plus the proximity term.
    return 0.0


def optimal_delta(m):
    """The Delta minimising ac resistance, found on a grid of 0.001 from 0.05 to 5."""
    # TODO: minimise dowell(D, 1.0, m) / D over np.linspace(0.05, 5.0, 4951).
    return 0.0


if __name__ == "__main__":
    d = skin_depth(RHO_CU, 100e3)
    print("skin depth at 100 kHz:", round(d * 1e6, 2), "um")
    print("F_R for 4 layers at Delta = 1:", round(dowell(1.0, 1.0, 4), 4))
    for m in (1, 2, 4):
        print("optimal Delta for", m, "layers:", round(optimal_delta(m), 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

MU0 = 4e-7 * np.pi
RHO_CU = 1.724e-8      # ohm.m, annealed copper at 20 C


def skin_depth(rho, f, mu_r=1.0):
    """Skin depth in metres."""
    return float(np.sqrt(rho / (np.pi * f * mu_r * MU0)))


def dowell(h, delta, m):
    """Dowell's ratio of ac to dc resistance for m layers of foil thickness h."""
    d = float(h) / float(delta)
    skin = d * (np.sinh(2.0 * d) + np.sin(2.0 * d)) / (np.cosh(2.0 * d) - np.cos(2.0 * d))
    prox = d * (2.0 * (m * m - 1.0) / 3.0) * (np.sinh(d) - np.sin(d)) / (np.cosh(d) + np.cos(d))
    return float(skin + prox)


def optimal_delta(m):
    """The Delta minimising ac resistance, found on a grid of 0.001 from 0.05 to 5."""
    grid = np.linspace(0.05, 5.0, 4951)
    cost = np.array([dowell(x, 1.0, m) for x in grid]) / grid
    return float(grid[int(np.argmin(cost))])


if __name__ == "__main__":
    d = skin_depth(RHO_CU, 100e3)
    print("skin depth at 100 kHz:", round(d * 1e6, 2), "um")
    print("F_R for 4 layers at Delta = 1:", round(dowell(1.0, 1.0, 4), 4))
    for m in (1, 2, 4):
        print("optimal Delta for", m, "layers:", round(optimal_delta(m), 3))
'''}],
                "hints": [
                    "`np.sinh`, `np.cosh`, `np.sin` and `np.cos` are all you need — no special functions appear in Dowell's result.",
                    "At very small $\\Delta$ both the numerator and the denominator of the skin term go to zero; the ratio still tends to $\\frac{1}{\\Delta}$, so the product tends to 1. Do not add a special case for it.",
                    "`optimal_delta` can call `dowell(x, 1.0, m)` directly: setting the skin depth to 1 makes the thickness argument *be* $\\Delta$.",
                ],
                "tests": [
                    {"name": "skin depth in copper at 100 kHz is a fifth of a millimetre", "code": r'''
_d = skin_depth(RHO_CU, 100e3)
assert abs(_d - 0.00020897231909955822) < 1e-15, \
    f"copper at 100 kHz has a skin depth of 209 um, got {_d}"
'''},
                    {"name": "skin depth falls as the square root of frequency", "code": r'''
_d1 = skin_depth(RHO_CU, 100e3)
_d2 = skin_depth(RHO_CU, 1e6)
assert _d1 > 0.0, "skin depth must be positive before the ratio means anything"
assert abs(_d1 / _d2 - 10.0 ** 0.5) < 1e-9, \
    f"a decade of frequency should shrink delta by sqrt(10), got {_d1 / _d2}"
'''},
                    {"name": "a thin conductor has no ac penalty at all", "code": r'''
_f = dowell(1e-5, 2e-4, 6)
assert abs(_f - 1.0000248611048452) < 1e-9, \
    f"at Delta = 0.05 the factor should be a hair above 1, got {_f}"
assert _f > 1.0, "Dowell's factor is never below 1 — eddy currents only add loss"
'''},
                    {"name": "the small-Delta series is reproduced", "code": r'''
_f = dowell(0.1, 1.0, 3)
_series = 1.0 + (5 * 9 - 1) * 0.1 ** 4 / 45.0
assert abs(_f - 1.0000977773841273) < 1e-12, \
    f"expected 1.00009778 for m=3 at Delta=0.1, got {_f}"
assert abs(_f - _series) < 1e-8, \
    f"the expansion 1 + (5m^2-1)*Delta^4/45 should match here: {_f} vs {_series}"
'''},
                    {"name": "the thick-conductor asymptote is the layer law", "code": r'''
_f = dowell(20.0, 1.0, 4)
assert abs(_f - 219.9999989108639) < 1e-6, \
    f"expected 220 for m=4 at Delta=20, got {_f}"
assert abs(_f - 20.0 * (2 * 16 + 1) / 3.0) < 1e-4, \
    "for large Delta the factor is Delta*(2m^2+1)/3, which is 220 here"
'''},
                    {"name": "proximity effect dominates once there are layers", "code": r'''
_one = dowell(1.0, 1.0, 1)
_four = dowell(1.0, 1.0, 4)
assert abs(_one - 1.0856357047503276) < 1e-9, f"m=1 at Delta=1 is 1.0856, got {_one}"
assert abs(_four - 2.6875025642650545) < 1e-9, f"m=4 at Delta=1 is 2.6875, got {_four}"
assert _four > 2.4 * _one, \
    "four layers cost far more than one at the same thickness — that is the proximity term"
'''},
                    {"name": "the optimum thickness shrinks as layers are added", "code": r'''
_o1 = optimal_delta(1)
_o2 = optimal_delta(2)
_o4 = optimal_delta(4)
assert abs(_o1 - 1.571) < 1e-6, f"a single layer optimises at Delta = 1.571, got {_o1}"
assert abs(_o2 - 0.961) < 1e-6, f"two layers optimise at Delta = 0.961, got {_o2}"
assert abs(_o4 - 0.663) < 1e-6, f"four layers optimise at Delta = 0.663, got {_o4}"
assert _o1 > _o2 > _o4, "more layers always means thinner copper, never thicker"
'''},
                    {"name": "the optimum always lands near a factor of four thirds", "code": r'''
for _m, _want in ((1, 1.4408463383158308), (2, 1.3482469614002408),
                  (4, 1.3365858410343097)):
    _f = dowell(optimal_delta(_m), 1.0, _m)
    assert abs(_f - _want) < 1e-6, \
        f"F_R at the optimum for m={_m} should be {_want}, got {_f}"
    assert 1.3 < _f < 1.5, \
        "the optimum always sits near F_R = 4/3, whatever the layer count"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Sizing a transformer by area product",
            "summary": "One number, the product of core area and window area, decides which core can carry a given VA at a given frequency.",
            "concepts": [
                "The window must hold the copper: $K_u A_w = \\frac{N I}{J}$, where $K_u$ is the fraction of the window that is actually conductor.",
                "The core must hold the flux: $N = \\frac{V}{K_f f B_m A_e}$, with $K_f = 4$ for a square wave and $4.44$ for a sinusoid.",
                "Multiplying the two, $A_e$ cancels and $A_p = A_w A_e = \\frac{V I}{K_f f B_m J K_u}$.",
                "Catalogues list $A_p$ for exactly this reason: it is the one geometric figure of merit that does not depend on the winding.",
                "$A_p \\propto \\frac{1}{f}$ is the whole argument for high-frequency conversion, and modules 1, 2 and 4 are the reasons it stops working.",
            ],
            "sandbox": {
                "title": "What buys you the higher frequency",
                "visualiser": "switching",
                "minutes": 8,
                "initial": {"ls": 30, "coss": 150, "dead": 5},
                "brief": r'''
The area product falls as $\frac{1}{f}$, so a smaller core is always one frequency
doubling away. What stops you is the switching cell, and this is the picture of it.

You open at 30 nH of loop inductance, 150 pF of device capacitance and 5 ns of dead
time.
''',
                "notice": [
                    "The trace opens green: the quarter-cycle swing takes 3.3 ns and the 5 ns of dead time covers it, so $V_{ds}$ is already at zero 3.3 ns in, while the blue current — which takes 60 ns to reach full scale — is still under a tenth of it. There is no $\\frac{1}{2}CV^2$ turn-on loss, and that is the licence to raise $f$ and halve the area product.",
                    "Set the dead time back to 0. The trace turns amber, $V_{ds}$ steps to 0.9 and rings about zero, and the current is already at full scale. That loss returns once per cycle, so it grows in direct proportion to $f$ — the term that eventually cancels the shrinking core.",
                    "Leave the dead time at 5 ns and raise $C_{oss}$ to 600 pF. The ring drops to 37.5 MHz and the quarter-cycle stretches to 6.7 ns, which 5 ns no longer covers, so the trace reverts to amber. Fitting a bigger device to cut conduction loss can cost you the soft switching that made the small core possible.",
                ],
            },
            "derive": {
                "title": "Why the core area cancels",
                "minutes": 13,
                "vars": ["A_p", "A_w", "A_e", "K_u", "K_f", "J", "f", "B_m", "V", "N", "I"],
                "brief": r'''
A transformer has two independent geometric constraints. The window has to hold the
copper, and the core has to hold the flux. Each on its own involves both the
winding and the core; together they do not.

Take a winding of $N$ turns carrying rms current $I$ at current density $J$, in a
window of area $A_w$ whose usable copper fraction is $K_u$.
''',
                "steps": [
                    {
                        "prompt": "Each turn needs a conductor cross-section $\\frac{I}{J}$, and only the fraction $K_u$ of the window is copper. Write $A_w$ in terms of $N$, $I$, $J$ and $K_u$.",
                        "answer": "\\frac{N I}{J K_u}",
                        "hint": "The copper area is $N \\frac{I}{J}$, and that equals $K_u A_w$.",
                        "deconstruct": [
                            "Total copper in the window: $N \\cdot \\frac{I}{J}$.",
                            "That fills a fraction $K_u$ of $A_w$, so divide by $K_u$.",
                        ],
                    },
                    {
                        "prompt": "From module 1, square-wave excitation gives $B_m = \\frac{V}{4 f N A_e}$. Solve that for $N$.",
                        "answer": "\\frac{V}{4 f A_e B_m}",
                        "hint": "Multiply both sides by $N$ and divide by $B_m$.",
                        "deconstruct": [
                            "$B_m N = \\frac{V}{4 f A_e}$.",
                            "Divide through by $B_m$.",
                        ],
                    },
                    {
                        "prompt": "Form the area product $A_p = A_w A_e$ by substituting that $N$ into your expression for $A_w$. Write $A_p$ in terms of $V$, $I$, $f$, $B_m$, $J$ and $K_u$.",
                        "answer": "\\frac{V I}{4 f B_m J K_u}",
                        "hint": "$A_w$ now carries a $\\frac{1}{A_e}$, and you are multiplying by $A_e$.",
                        "deconstruct": [
                            "$A_w = \\frac{I}{J K_u} \\cdot \\frac{V}{4 f A_e B_m}$.",
                            "Multiplying by $A_e$ removes the only $A_e$ in sight.",
                        ],
                    },
                    {
                        "prompt": "Two designs handle the same $V I$ at the same $B_m$, $J$ and $K_u$, one at $f$ and the other at $4f$. Write the ratio of the second design's area product to the first's.",
                        "answer": "\\frac{1}{4}",
                        "hint": "$A_p$ depends on frequency only through $\\frac{1}{f}$.",
                        "deconstruct": [
                            "Every other symbol in $A_p$ is held fixed.",
                            "Four times the frequency is a quarter of the area product.",
                        ],
                    },
                    {
                        "prompt": "A sinusoid instead of a square wave replaces the 4 by $4.44$, and other waveforms have their own constant. Writing that constant as $K_f$, rewrite $A_p$.",
                        "answer": "\\frac{V I}{K_f f B_m J K_u}",
                        "hint": "The 4 came from Faraday and nothing else; replace it in place.",
                        "deconstruct": [
                            "The waveform constant entered only through $B_m = \\frac{V}{K_f f N A_e}$.",
                            "It travels through the substitution untouched.",
                        ],
                    },
                ],
                "closing": r'''
Nothing in $A_p$ knows what the core looks like — only how much VA it must pass, how
hard you are willing to push the flux, and how hard you are willing to push the
copper. That is why catalogues tabulate it, and why the first line of a magnetics
design is a division rather than a simulation.

What the formula does *not* contain is loss. $J$ and $B_m$ are stand-ins for a
thermal limit, and setting them honestly is module 4.
''',
            },
            "quiz": {
                "title": "One number that picks the core",
                "minutes": 7,
                "questions": [
                    {
                        "q": "The area product is $A_p = A_wA_e$. What does it come out proportional to?",
                        "opts": [
                            "$VI/(K_ffB_mJK_u)$",
                            "$VIfB_m$",
                            "$V/(fB_m)$",
                            "$I/(JK_u)$",
                        ],
                        "a": 0,
                        "why": r"""
Two constraints multiplied together. The window must hold the copper,
$K_uA_w = NI/J$; the core must hold the flux, $N = V/(K_ffB_mA_e)$. Multiply them and
$N$ cancels, leaving one number that depends on the *requirement* and not on the number
of turns — which is what makes it a selection criterion rather than a design.
""",
                    },
                    {
                        "q": "What does raising the frequency do to the core you need?",
                        "opts": [
                            "Shrinks it, since $A_p$ goes as $1/f$",
                            "Enlarges it",
                            "Leaves it unchanged",
                            "Shrinks it as $1/f^2$",
                        ],
                        "a": 0,
                        "why": r"""
This is the whole economic argument for high-frequency conversion, in one relation: ten
times the frequency, a tenth of the area product. It is limited in practice by the two
previous modules — core loss and winding loss both rise with frequency — so the real
optimum sits where shrinking the core stops paying for the loss it adds.
""",
                    },
                    {
                        "q": "What is $K_f$ for a square-wave excitation?",
                        "opts": ["4", "4.44", "2", "$\\pi$"],
                        "a": 0,
                        "why": r"""
Exactly 4 for a square wave and $4.44 = 2\pi/\sqrt{2}$ for a sinusoid — the difference is
just the form factor of the waveform whose volt-seconds you are integrating. Only 10%,
but it is 10% in a core-selection calculation where the next size up is often a factor of
two, so it is worth getting right rather than approximating.
""",
                    },
                    {
                        "q": "The window utilisation factor $K_u$ is typically what?",
                        "opts": ["0.3 to 0.4", "0.9 to 0.95", "0.6 to 0.7", "1.0 by definition"],
                        "a": 0,
                        "why": r"""
Round wires do not tessellate, insulation takes space, bobbins have walls, and safety
creepage distances eat the ends — so under half the window ends up as conductor, and 0.4
is optimistic for a multi-winding design. Assuming a value near 1 is the fastest route to
choosing a core the winding does not physically fit into, which is discovered late and
expensively.
""",
                    },
                    {
                        "q": "$A_p$ has units of length to the fourth. What does that imply?",
                        "opts": [
                            "Doubling every linear dimension multiplies the power capability by sixteen",
                            "By eight",
                            "By four",
                            "By two",
                        ],
                        "a": 0,
                        "why": r"""
$A_w$ and $A_e$ are each areas, so the product goes as $L^4$ and a modest increase in size
buys a great deal of capability. Which cuts both ways: cores come in discrete sizes, and
being 20% over on $A_p$ frequently means stepping up to a core with twice what you need.
It is also why cooling gets harder as designs grow, since the loss scales with volume,
$L^3$, and the surface available to shed it only as $L^2$.
""",
                    },
                ],
            },
            "lab": {
                "title": "Choose a core and count the cost",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
`CORES` is already defined: a list of dictionaries with `name`, `Ae`, `Aw`, `Ve` and
`MLT` (mean length of turn), all in SI units.

`area_product(VA, f, Bm, J, Ku, Kf=4.0)` returns
$A_p = \frac{VA}{K_f f B_m J K_u}$ in m⁴.

`select_core(cores, Ap)` returns the dictionary of the **smallest** core whose
$A_e A_w$ is at least `Ap`, or `None` when no core in the list is big enough.
Smallest means smallest $A_e A_w$.

`turns(V, f, Bm, Ae, Kf=4.0)` returns $\lceil \frac{V}{K_f f B_m A_e} \rceil$ as an
`int` — you cannot wind a fraction of a turn, and rounding down would push the core
past the flux you asked for.

`losses(core, N, I, J, f, Bm)` returns the dictionary
`{"copper": ..., "core": ..., "total": ...}` in watts, using

```text
copper = RHO_CU * N * core["MLT"] * J * I
core   = K_STEIN * f**ALPHA * Bm**BETA * core["Ve"]
```

The copper expression is just $I^2 R$ with $R = \frac{\rho N \cdot \text{MLT}}{I/J}$;
write it out once and see that the $I^2$ collapses.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import numpy as np

RHO_CU = 1.724e-8
K_STEIN, ALPHA, BETA = 1.5, 1.4, 2.5

CORES = [
    {"name": "EFD20", "Ae": 31e-6, "Aw": 22e-6, "Ve": 1460e-9, "MLT": 0.039},
    {"name": "ETD29", "Ae": 76e-6, "Aw": 90e-6, "Ve": 5470e-9, "MLT": 0.053},
    {"name": "ETD34", "Ae": 97e-6, "Aw": 123e-6, "Ve": 7640e-9, "MLT": 0.060},
    {"name": "ETD44", "Ae": 173e-6, "Aw": 214e-6, "Ve": 17800e-9, "MLT": 0.078},
    {"name": "E55", "Ae": 354e-6, "Aw": 250e-6, "Ve": 43900e-9, "MLT": 0.116},
]


def area_product(VA, f, Bm, J, Ku, Kf=4.0):
    """Required window-area times core-area product, in m^4."""
    # TODO
    return 0.0


def select_core(cores, Ap):
    """The smallest core with Ae*Aw >= Ap, or None."""
    # TODO
    return None


def turns(V, f, Bm, Ae, Kf=4.0):
    """Primary turns, rounded up."""
    # TODO
    return 0


def losses(core, N, I, J, f, Bm):
    """Copper, core and total loss in watts."""
    # TODO
    return {"copper": 0.0, "core": 0.0, "total": 0.0}


if __name__ == "__main__":
    ap = area_product(500.0, 100e3, 0.1, 4e6, 0.4)
    core = select_core(CORES, ap)
    print("Ap needed:", ap, "m^4")
    print("core:", core["name"] if core else None)
    if core:
        N = turns(48.0, 100e3, 0.1, core["Ae"])
        print("turns:", N)
        print("losses:", losses(core, N, 500.0 / 48.0, 4e6, 100e3, 0.1))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import numpy as np

RHO_CU = 1.724e-8
K_STEIN, ALPHA, BETA = 1.5, 1.4, 2.5

CORES = [
    {"name": "EFD20", "Ae": 31e-6, "Aw": 22e-6, "Ve": 1460e-9, "MLT": 0.039},
    {"name": "ETD29", "Ae": 76e-6, "Aw": 90e-6, "Ve": 5470e-9, "MLT": 0.053},
    {"name": "ETD34", "Ae": 97e-6, "Aw": 123e-6, "Ve": 7640e-9, "MLT": 0.060},
    {"name": "ETD44", "Ae": 173e-6, "Aw": 214e-6, "Ve": 17800e-9, "MLT": 0.078},
    {"name": "E55", "Ae": 354e-6, "Aw": 250e-6, "Ve": 43900e-9, "MLT": 0.116},
]


def area_product(VA, f, Bm, J, Ku, Kf=4.0):
    """Required window-area times core-area product, in m^4."""
    return float(VA) / (float(Kf) * float(f) * float(Bm) * float(J) * float(Ku))


def select_core(cores, Ap):
    """The smallest core with Ae*Aw >= Ap, or None."""
    big = [c for c in cores if c["Ae"] * c["Aw"] >= Ap]
    if not big:
        return None
    return min(big, key=lambda c: c["Ae"] * c["Aw"])


def turns(V, f, Bm, Ae, Kf=4.0):
    """Primary turns, rounded up."""
    return int(math.ceil(float(V) / (float(Kf) * float(f) * float(Bm) * float(Ae))))


def losses(core, N, I, J, f, Bm):
    """Copper, core and total loss in watts."""
    cu = RHO_CU * N * core["MLT"] * J * I
    fe = K_STEIN * f ** ALPHA * Bm ** BETA * core["Ve"]
    return {"copper": float(cu), "core": float(fe), "total": float(cu + fe)}


if __name__ == "__main__":
    ap = area_product(500.0, 100e3, 0.1, 4e6, 0.4)
    core = select_core(CORES, ap)
    print("Ap needed:", ap, "m^4")
    print("core:", core["name"] if core else None)
    if core:
        N = turns(48.0, 100e3, 0.1, core["Ae"])
        print("turns:", N)
        print("losses:", losses(core, N, 500.0 / 48.0, 4e6, 100e3, 0.1))
'''}],
                "hints": [
                    "`select_core` is a filter followed by a `min` with `key=lambda c: c['Ae'] * c['Aw']`. Return the dictionary itself, not the name.",
                    "`math.ceil` returns an int in Python 3, but wrap it in `int(...)` anyway so the type is unambiguous.",
                    "In `losses`, the copper term already has the $I^2$ folded in: $I^2 \\frac{\\rho N\\,\\text{MLT}}{I/J} = \\rho N\\,\\text{MLT}\\,J I$.",
                ],
                "tests": [
                    {"name": "the area product formula matches the derivation", "code": r'''
_ap = area_product(500.0, 100e3, 0.1, 4e6, 0.4)
assert abs(_ap - 7.8125e-09) < 1e-18, \
    f"500 VA at 100 kHz, 0.1 T, 4 A/mm^2 and Ku = 0.4 needs 7.8125e-9 m^4, got {_ap}"
'''},
                    {"name": "the area product is inverse in frequency", "code": r'''
_a1 = area_product(500.0, 100e3, 0.1, 4e6, 0.4)
_a4 = area_product(500.0, 400e3, 0.1, 4e6, 0.4)
assert _a1 > 0.0, "the area product must be positive before the ratio means anything"
assert abs(_a4 / _a1 - 0.25) < 1e-12, \
    f"four times the frequency should be a quarter of the area product, got {_a4 / _a1}"
'''},
                    {"name": "raising frequency walks down the core list", "code": r'''
_want = {50e3: "ETD44", 100e3: "ETD34", 200e3: "ETD29", 400e3: "ETD29"}
for _f, _name in _want.items():
    _c = select_core(CORES, area_product(500.0, _f, 0.1, 4e6, 0.4))
    assert _c is not None, f"a core should have been found at {_f/1e3:.0f} kHz"
    assert _c["name"] == _name, \
        f"at {_f/1e3:.0f} kHz expected {_name}, got {_c['name']}"
'''},
                    {"name": "an impossible requirement returns nothing", "code": r'''
_c = select_core(CORES, area_product(20000.0, 100e3, 0.1, 4e6, 0.4))
assert _c is None, \
    "20 kVA at 100 kHz needs 3.1e-7 m^4, past the largest core here — return None, not the biggest"
_c2 = select_core(CORES, area_product(5000.0, 100e3, 0.1, 4e6, 0.4))
assert _c2 is not None and _c2["name"] == "E55", \
    f"5 kVA should just fit the E55, got {_c2}"
'''},
                    {"name": "turns are rounded up, never down", "code": r'''
_n = turns(48.0, 100e3, 0.1, 97e-6)
assert _n == 13, f"48/(4*1e5*0.1*97e-6) is 12.37, so 13 turns; got {_n}"
assert isinstance(_n, int), f"turns must be a whole number, got {type(_n).__name__}"
_n2 = turns(48.0, 100e3, 0.1, 194e-6)
assert _n2 == 7, f"twice the core area needs 6.19 turns, so 7; got {_n2}"
'''},
                    {"name": "the loss split is computed, not guessed", "code": r'''
_c = select_core(CORES, area_product(500.0, 100e3, 0.1, 4e6, 0.4))
_L = losses(_c, 13, 500.0 / 48.0, 4e6, 100e3, 0.1)
assert abs(_L["copper"] - 0.5603) < 1e-9, f"copper loss should be 0.5603 W, got {_L['copper']}"
assert abs(_L["core"] - 0.36239701985529593) < 1e-9, \
    f"core loss should be 0.36240 W, got {_L['core']}"
assert abs(_L["total"] - 0.9226970198552959) < 1e-9, \
    f"total should be 0.9227 W, got {_L['total']}"
'''},
                    {"name": "the balance tips from copper to core with frequency", "code": r'''
_lo = select_core(CORES, area_product(500.0, 50e3, 0.1, 4e6, 0.4))
_hi = select_core(CORES, area_product(500.0, 400e3, 0.1, 4e6, 0.4))
_a = losses(_lo, turns(48.0, 50e3, 0.1, _lo["Ae"]), 500.0 / 48.0, 4e6, 50e3, 0.1)
_b = losses(_hi, turns(48.0, 400e3, 0.1, _hi["Ae"]), 500.0 / 48.0, 4e6, 400e3, 0.1)
assert _a["copper"] > _a["core"], \
    f"at 50 kHz copper should dominate: {_a['copper']:.3f} vs {_a['core']:.3f}"
assert _b["core"] > _b["copper"], \
    f"at 400 kHz core loss should dominate: {_b['core']:.3f} vs {_b['copper']:.3f}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Thermal resistance from junction to ambient",
            "summary": "Loss is only a number until it becomes a temperature. The network that turns one into the other is a resistor divider with a feedback path.",
            "concepts": [
                "$\\Delta T = P R_{th}$ is Ohm's law with power for current and temperature for voltage; series and parallel combine identically.",
                "The junction-to-ambient path is $R_{jc} + R_{cs} + R_{sa}$, and only the last of those is shared when several devices sit on one sink.",
                "Transient thermal impedance $Z_{th}(t) = \\sum_i R_i (1 - e^{-t/\\tau_i})$: a short pulse sees far less than the steady-state resistance.",
                "A Foster ladder of positive $R$ and $C$ has only real poles. A fit that produces an overshoot has been fitted to measurement noise.",
                "A power ferrite's loss curve has a minimum near 100 °C; run it above that and core loss rises with temperature, so $P$ and $T_j$ form a loop. Past a critical $R_{ja}$ the steady solution disappears entirely.",
            ],
            "sandbox": {
                "title": "A heatsink as a low-pass filter",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 2, "zeta": 1.5, "K": 20},
                "brief": r'''
Power in, temperature rise out. That is a transfer function, and this is a ruler for
reading one rather than a model of a heatsink: the Foster ladder of the lab is a sum
of first-order terms and rolls off at 20 dB per decade, while the curve drawn here is
a textbook second order and rolls off at 40. Take the plateau and the corner from it,
not the slope.

Read the magnitude in dB as thermal impedance: the flat level on the left is the
steady-state $R_{th}$ in K/W, and the roll-off on the right is why a short pulse of
power does not raise the junction the way a steady one does.
''',
                "notice": [
                    "Read the flat level first. With $K = 20$ it sits at 26 dB, which is a thermal resistance of 20 K/W — the number a steady dissipation multiplies. Everything to the left of the corner is slow enough that the whole stack has reached equilibrium.",
                    "The amber dot marks the corner, at $\\frac{K}{2\\zeta}$. With $K = 20$ and $\\zeta = 1.5$ that is 6.7 K/W, which is 9.5 dB below the flat level, and the two poles are real, sitting at $0.38\\,\\omega_n$ and $2.62\\,\\omega_n$. Where the corner falls is the number to carry away: a pulse much shorter than the slowest time constant sees far less than the steady-state resistance.",
                    "Take $\\zeta$ down to 0.05. The magnitude peaks 20 dB above the plateau — 46 dB, so the tip runs off the top of a frame that stops at 40 — just below $\\omega_n$, and the phase dives through $-90°$ towards $-180°$. A ladder of positive thermal resistances and capacitances can never do that — its poles are always real — so a Foster fit that comes back underdamped has been fitted to noise, not to heat.",
                ],
            },
            "derive": {
                "title": "Sharing a heatsink, and losing control of it",
                "minutes": 14,
                "vars": ["T_j", "T_a", "T_max", "P", "P_0", "R_jc", "R_cs", "R_sa", "R_ja", "n", "a"],
                "brief": r'''
Three resistances in series carry the heat from a junction to the air: junction to
case $R_{jc}$, case to sink $R_{cs}$ through the interface material, and sink to
ambient $R_{sa}$. Ambient is at $T_a$.

The last two steps replace the fixed dissipation with one that depends on its own
temperature, which is what a ferrite actually does.
''',
                "steps": [
                    {
                        "prompt": "One device dissipating $P$. Write the junction temperature $T_j$ in terms of $T_a$, $P$, $R_{jc}$, $R_{cs}$ and $R_{sa}$.",
                        "answer": "T_a + P \\left( R_{jc} + R_{cs} + R_{sa} \\right)",
                        "placeholder": "T_a + P(R_{jc} + R_{cs} + R_{sa})",
                        "hint": "Series resistances add, and the same power flows through all three.",
                        "deconstruct": [
                            "The total junction-to-ambient resistance is the sum of the three.",
                            "Temperature rise above ambient is that sum times the power.",
                        ],
                    },
                    {
                        "prompt": "Now $n$ identical devices share one heatsink, each dissipating $P$. The first two resistances are private to each device; the sink-to-ambient path carries all $n P$. Write $T_j$ for one of them.",
                        "answer": "T_a + P \\left( R_{jc} + R_{cs} \\right) + n P R_{sa}",
                        "placeholder": "T_a + P(R_{jc} + R_{cs}) + n P R_{sa}",
                        "hint": "Walk the path from ambient inwards: the sink first, at the full $n P$, then one device's private path at $P$.",
                        "deconstruct": [
                            "The sink sits at $T_a + n P R_{sa}$.",
                            "One device's junction is a further $P(R_{jc} + R_{cs})$ above that.",
                        ],
                    },
                    {
                        "prompt": "The junction must stay below $T_{max}$. Write the largest $P$ one device may dissipate, still with $n$ of them on the sink.",
                        "answer": "\\frac{T_{max} - T_a}{R_{jc} + R_{cs} + n R_{sa}}",
                        "hint": "Set $T_j = T_{max}$ in the previous answer and collect the $P$ terms.",
                        "deconstruct": [
                            "$T_{max} - T_a = P(R_{jc} + R_{cs}) + n P R_{sa}$.",
                            "Factor out $P$ and divide.",
                        ],
                    },
                    {
                        "prompt": "Now let the dissipation itself depend on temperature: $P = P_0 \\left(1 + a (T_j - T_a)\\right)$ with $a > 0$, and collapse the whole path to a single $R_{ja}$ carrying one device. Substituting $T_j - T_a = P R_{ja}$, solve for $P$.",
                        "given": "You are solving one linear equation in $P$; $P$ appears on both sides.",
                        "answer": "\\frac{P_0}{1 - a P_0 R_{ja}}",
                        "hint": "Expand to $P = P_0 + a P_0 R_{ja} P$, move both $P$ terms to the left, then factor.",
                        "deconstruct": [
                            "$P = P_0 + P_0 a P R_{ja}$.",
                            "$P\\left(1 - a P_0 R_{ja}\\right) = P_0$.",
                        ],
                    },
                    {
                        "prompt": "That denominator can reach zero. Write the largest $R_{ja}$ for which a steady solution exists at all, in terms of $a$ and $P_0$.",
                        "answer": "\\frac{1}{a P_0}",
                        "hint": "Set the denominator to zero and solve for $R_{ja}$.",
                        "deconstruct": [
                            "$1 - a P_0 R_{ja} = 0$.",
                            "Beyond that value the loop gain exceeds one and the temperature has nowhere to settle.",
                        ],
                    },
                ],
                "closing": r'''
The last two steps are why a magnetics design is never finished at the loss
calculation. A core that dissipates 2 W at 25 °C and has $a = 0.004$ per kelvin will
run away at $R_{ja} = 125$ K/W — a figure a small ungapped core in still air can
easily reach. The margin you need is not on the loss; it is on the thermal
resistance.
''',
            },
            "build": {
                "title": "A thermal network really is a circuit",
                "minutes": 26,
                "brief": r"""
$\Delta T = PR_{th}$ is Ohm's law with different labels, and the correspondence is not a
teaching analogy — it is how thermal simulation is actually done, because once you accept
it you get a solver, a transient response and a frequency domain for free.

| thermal | electrical |
|---|---|
| power dissipated, W | current, A |
| temperature rise, K | voltage, V |
| thermal resistance, K/W | resistance, Ω |
| thermal capacitance, J/K | capacitance, F |

## What is on the canvas

A **25 A current source**, which is 25 W of dissipation, and three capacitors already
placed — the thermal masses of the die, the case and the heatsink. The probe is on the
junction node, so the voltage it reads is the junction's rise above ambient, in kelvin.
Ground is ambient.

## What to add

The three resistances of the junction-to-ambient path, in series from the junction node
down to ambient:

| | K/W |
|---|---|
| $R_{jc}$, junction to case | 0.5 |
| $R_{cs}$, case to sink, through the thermal interface | 0.2 |
| $R_{sa}$, sink to ambient | choose it |

Size $R_{sa}$ so that the junction settles **67.5 K** above ambient. With $T_{amb} = 40$ °C
that puts the junction at 107.5 °C — inside a 125 °C limit, with the margin a real design
keeps.

## What the checks measure

- The steady-state rise, which is $P$ times the sum of the three.
- The **shape** of the warm-up, and this is the part worth building it for. The die and
  the case have time constants of milliseconds; the heatsink's is tens of seconds. So a
  short burst of dissipation is limited by $R_{jc} + R_{cs}$ alone and the junction
  barely notices the heatsink is there — while a sustained load is governed almost
  entirely by $R_{sa}$, which is 74% of the total.
- Which means the same part survives a pulse it could never survive continuously, and
  the transient thermal impedance curve on a datasheet exists precisely to quantify that.

## The trap

Only $R_{sa}$ is yours to choose. $R_{jc}$ is fixed by the package and $R_{cs}$ by the
interface material — and the standard mistake is to buy a heatsink twice as good and
expect the junction temperature to halve. It does not: 0.7 K/W of the path is untouchable,
so halving $R_{sa}$ from 2.0 to 1.0 takes the rise from 67.5 K to 42.5 K, not to 34 K.
""",
                "start": {
                    "parts": [
                        {"id": "p", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 25},
                        {"id": "ga", "kind": "GND", "x": 3, "y": 4},
                        {"id": "cj", "kind": "C", "x": 6, "y": 9, "rot": 1, "value": 0.002},
                        {"id": "gb", "kind": "GND", "x": 6, "y": 11},
                        {"id": "cc", "kind": "C", "x": 12, "y": 9, "rot": 1, "value": 0.05},
                        {"id": "gc", "kind": "GND", "x": 12, "y": 11},
                        {"id": "cs", "kind": "C", "x": 18, "y": 9, "rot": 1, "value": 20},
                        {"id": "gd", "kind": "GND", "x": 18, "y": 11},
                        {"id": "ge", "kind": "GND", "x": 21, "y": 11},
                        {"id": "out", "kind": "OUT", "x": 4, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [6, 7]},
                        {"a": [6, 7], "b": [6, 8]},
                        {"a": [6, 10], "b": [6, 11]},
                        {"a": [12, 7], "b": [12, 8]},
                        {"a": [12, 10], "b": [12, 11]},
                        {"a": [18, 7], "b": [18, 8]},
                        {"a": [18, 10], "b": [18, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 25},
                        {"id": "ga", "kind": "GND", "x": 3, "y": 4},
                        {"id": "cj", "kind": "C", "x": 6, "y": 9, "rot": 1, "value": 0.002},
                        {"id": "gb", "kind": "GND", "x": 6, "y": 11},
                        {"id": "rjc", "kind": "R", "x": 9, "y": 7, "rot": 0, "value": 0.5},
                        {"id": "cc", "kind": "C", "x": 12, "y": 9, "rot": 1, "value": 0.05},
                        {"id": "gc", "kind": "GND", "x": 12, "y": 11},
                        {"id": "rcs", "kind": "R", "x": 15, "y": 7, "rot": 0, "value": 0.2},
                        {"id": "cs", "kind": "C", "x": 18, "y": 9, "rot": 1, "value": 20},
                        {"id": "gd", "kind": "GND", "x": 18, "y": 11},
                        {"id": "rsa", "kind": "R", "x": 21, "y": 9, "rot": 1, "value": 2.0},
                        {"id": "ge", "kind": "GND", "x": 21, "y": 11},
                        {"id": "out", "kind": "OUT", "x": 4, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [6, 7]},
                        {"a": [6, 7], "b": [6, 8]},
                        {"a": [6, 10], "b": [6, 11]},
                        {"a": [6, 7], "b": [8, 7]},
                        {"a": [10, 7], "b": [14, 7]},
                        {"a": [12, 7], "b": [12, 8]},
                        {"a": [12, 10], "b": [12, 11]},
                        {"a": [16, 7], "b": [21, 7]},
                        {"a": [18, 7], "b": [18, 8]},
                        {"a": [18, 10], "b": [18, 11]},
                        {"a": [21, 7], "b": [21, 8]},
                        {"a": [21, 10], "b": [21, 11]},
                    ],
                },
                "checks": [
                    {
                        "name": "three resistances in the path, settling 67.5 K above ambient",
                        "code": r"""
c.assert(c.count('R') === 3,
  'The junction-to-ambient path has three resistances: R_jc, R_cs and R_sa. There are ' +
  c.count('R') + '.');
c.close(c.vout(), 67.5, 0.03,
  'the steady-state junction rise in kelvin. It is 25 W times the sum of the three ' +
  'resistances, so the sum must be 2.7 K/W and R_sa must be 2.0. Too low a rise means ' +
  'the heatsink chosen is better (and more expensive) than the specification asked for');
""",
                    },
                    {
                        "name": "a short burst does not reach the heatsink",
                        "code": r"""
const s = c.step(0.05);                 /* 50 ms, far shorter than the sink's constant */
const at50ms = s.v[s.v.length - 1];
c.close(at50ms, 17.6, 0.10,
  'the junction rise after 50 ms. The die and case masses have settled by now but the ' +
  'heatsink has barely begun to warm, so the rise is set by R_jc + R_cs alone: about ' +
  '25 W x 0.7 K/W. This is why a part survives a pulse that would destroy it ' +
  'continuously');
c.assert(at50ms < 0.4 * c.vout(),
  'After 50 ms the junction has already reached ' + at50ms.toFixed(1) + ' K of its ' +
  'final ' + c.vout().toFixed(1) + ' K. That is far too fast — it means the ' +
  'heatsink thermal mass is not in the path, so the model has no long time constant ' +
  'and will badly under-predict how hot a sustained load gets.');
""",
                    },
                    {
                        "name": "the heatsink is the slow term, and the dominant one",
                        "code": r"""
const s = c.step(200);                  /* 200 s: several sink time constants */
const settled = s.v[s.v.length - 1];
c.close(settled, 67.5, 0.05,
  'the rise after 200 seconds, which must have converged on the DC answer');
const half = s.v[Math.floor(s.v.length / 8)];   /* about 25 s in */
c.assert(half > 0.4 * settled && half < 0.95 * settled,
  'At around 25 seconds the junction is at ' + half.toFixed(1) + ' K against a final ' +
  settled.toFixed(1) + ' K. The heatsink time constant is R_sa * C_s = 40 s, so it ' +
  'should be well on its way and not yet there. A value outside that range means the ' +
  'sink resistance or its thermal mass is not what the specification asked for.');
""",
                    },
                    {
                        "name": "0.7 K/W of the path is not yours to improve",
                        "code": r"""
/* The DC answer is 25*(Rjc + Rcs + Rsa). The transient at 50 ms isolates the first
   two, so the difference tells us what the heatsink is contributing. */
const s = c.step(0.05);
const fast = s.v[s.v.length - 1];
const total = c.vout();
const sinkShare = (total - fast) / total;
c.close(sinkShare, 0.74, 0.10,
  'the fraction of the steady-state rise contributed by the heatsink. R_sa is 2.0 of ' +
  'the 2.7 K/W total, so it is 74% of the problem and the package is the other 26%. ' +
  'That ratio is what decides whether a better heatsink is worth buying');
""",
                    },
                ],
                "hints": [
                    "The three resistances are in series, from the junction node down to ground. Ground is ambient temperature — the reference everything is measured against.",
                    "$R_{sa} = 67.5/25 - 0.5 - 0.2$. The division comes first.",
                    "Each capacitor is already connected between its node and ambient; you are wiring the resistors *between* those nodes, so the chain reads junction, case, sink, ambient.",
                ],
            },
            "lab": {
                "title": "Junction temperature, steady and transient",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Four functions.

`junction_temp(Ta, P, Rjc, Rcs, Rsa, n=1)` returns
$T_a + P(R_{jc} + R_{cs}) + n P R_{sa}$.

`max_power(Tmax, Ta, Rjc, Rcs, Rsa, n=1)` inverts it.

`foster_zth(t, R, tau)` takes an array of times and two equal-length sequences, and
returns the array $\sum_i R_i \left(1 - e^{-t/\tau_i}\right)$. Use NumPy so the
whole time array comes back at once.

`steady_power(P0, a, Rja)` returns $\frac{P_0}{1 - a P_0 R_{ja}}$, and returns
`float("inf")` when the denominator is zero or negative — there is no steady
solution there, and returning a negative power would be worse than useless.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def junction_temp(Ta, P, Rjc, Rcs, Rsa, n=1):
    """Junction temperature with n devices sharing the sink-to-ambient path."""
    # TODO
    return 0.0


def max_power(Tmax, Ta, Rjc, Rcs, Rsa, n=1):
    """Largest per-device dissipation that keeps the junction below Tmax."""
    # TODO
    return 0.0


def foster_zth(t, R, tau):
    """Transient thermal impedance of a Foster ladder, evaluated at every t."""
    t = np.asarray(t, dtype=float)
    # TODO: sum R_i * (1 - exp(-t/tau_i)) over the ladder.
    return np.zeros_like(t)


def steady_power(P0, a, Rja):
    """Self-heated steady dissipation, or inf when no steady state exists."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print("Tj  =", junction_temp(40.0, 12.5, 0.45, 0.25, 1.8), "C")
    print("Tj4 =", junction_temp(40.0, 12.5, 0.45, 0.25, 1.8, 4), "C")
    print("Pmax=", max_power(125.0, 40.0, 0.45, 0.25, 1.8), "W")
    print("Zth =", foster_zth(np.array([0.001, 0.1, 10.0]), [0.05, 0.3, 1.2],
                              [0.001, 0.02, 0.5]))
    print("P   =", steady_power(2.0, 0.004, 60.0), "W")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def junction_temp(Ta, P, Rjc, Rcs, Rsa, n=1):
    """Junction temperature with n devices sharing the sink-to-ambient path."""
    return float(Ta) + float(P) * (float(Rjc) + float(Rcs)) + float(n) * float(P) * float(Rsa)


def max_power(Tmax, Ta, Rjc, Rcs, Rsa, n=1):
    """Largest per-device dissipation that keeps the junction below Tmax."""
    total = float(Rjc) + float(Rcs) + float(n) * float(Rsa)
    return (float(Tmax) - float(Ta)) / total


def foster_zth(t, R, tau):
    """Transient thermal impedance of a Foster ladder, evaluated at every t."""
    t = np.asarray(t, dtype=float)
    out = np.zeros_like(t)
    for Ri, ti in zip(R, tau):
        out = out + float(Ri) * (1.0 - np.exp(-t / float(ti)))
    return out


def steady_power(P0, a, Rja):
    """Self-heated steady dissipation, or inf when no steady state exists."""
    denom = 1.0 - float(a) * float(P0) * float(Rja)
    if denom <= 0.0:
        return float("inf")
    return float(P0) / denom


if __name__ == "__main__":
    print("Tj  =", junction_temp(40.0, 12.5, 0.45, 0.25, 1.8), "C")
    print("Tj4 =", junction_temp(40.0, 12.5, 0.45, 0.25, 1.8, 4), "C")
    print("Pmax=", max_power(125.0, 40.0, 0.45, 0.25, 1.8), "W")
    print("Zth =", foster_zth(np.array([0.001, 0.1, 10.0]), [0.05, 0.3, 1.2],
                              [0.001, 0.02, 0.5]))
    print("P   =", steady_power(2.0, 0.004, 60.0), "W")
'''}],
                "hints": [
                    "In `junction_temp` the sink term is the only one multiplied by `n`; the other two belong to one device alone.",
                    "`foster_zth` is a loop over the ladder that accumulates into an array — `out = out + ...` rather than `out += ...` keeps the dtype honest if `t` came in as integers.",
                    "In `steady_power`, test the denominator before dividing. A negative result would look like a plausible answer and is physically meaningless.",
                ],
                "tests": [
                    {"name": "one device on its own sink", "code": r'''
_t = junction_temp(40.0, 12.5, 0.45, 0.25, 1.8)
assert abs(_t - 71.25) < 1e-9, \
    f"12.5 W through 2.5 K/W above 40 C ambient is 71.25 C, got {_t}"
'''},
                    {"name": "four devices heat their shared sink four times over", "code": r'''
_t1 = junction_temp(40.0, 12.5, 0.45, 0.25, 1.8)
_t4 = junction_temp(40.0, 12.5, 0.45, 0.25, 1.8, 4)
assert abs(_t4 - 138.75) < 1e-9, f"four devices give 138.75 C, got {_t4}"
assert _t4 > _t1, "sharing a sink can only make each junction hotter, never cooler"
assert abs((_t4 - _t1) - 3 * 12.5 * 1.8) < 1e-9, \
    "the extra rise is the other three devices' power through the sink resistance alone"
'''},
                    {"name": "the power budget shrinks as the sink is shared", "code": r'''
_p1 = max_power(125.0, 40.0, 0.45, 0.25, 1.8)
_p4 = max_power(125.0, 40.0, 0.45, 0.25, 1.8, 4)
assert abs(_p1 - 34.0) < 1e-9, f"85 K over 2.5 K/W is 34 W, got {_p1}"
assert abs(_p4 - 10.759493670886075) < 1e-9, \
    f"with four sharing, each may dissipate 10.76 W, got {_p4}"
'''},
                    {"name": "max_power and junction_temp are inverses", "code": r'''
_p = max_power(125.0, 40.0, 0.45, 0.25, 1.8, 3)
assert _p > 0.0, "the allowed power must be positive"
assert abs(junction_temp(40.0, _p, 0.45, 0.25, 1.8, 3) - 125.0) < 1e-9, \
    "feeding the maximum power back in should land exactly on the temperature limit"
'''},
                    {"name": "a Foster ladder starts at zero and ends at the sum of its resistances", "code": r'''
import numpy as np
_z = foster_zth(np.array([0.0, 10.0]), [0.05, 0.3, 1.2], [0.001, 0.02, 0.5])
assert abs(float(_z[0])) < 1e-15, "at t = 0 nothing has warmed up yet"
assert abs(float(_z[1]) - 1.55) < 1e-6, \
    f"after twenty of the slowest time constants it should reach 1.55 K/W, got {_z[1]}"
'''},
                    {"name": "a short pulse sees a small fraction of the steady resistance", "code": r'''
import numpy as np
_z = foster_zth(np.array([0.001, 0.01, 0.1, 1.0]), [0.05, 0.3, 1.2], [0.001, 0.02, 0.5])
_want = [0.04863480219041398, 0.19180012412161557,
         0.5655017122066961, 1.387597660116065]
for _got, _exp in zip(_z, _want):
    assert abs(float(_got) - _exp) < 1e-12, f"expected {_want}, got {list(_z)}"
assert float(_z[0]) < 0.05 * 1.55, \
    "a 1 ms pulse should see under a twentieth of the steady-state 1.55 K/W"
'''},
                    {"name": "self-heating inflates the dissipation", "code": r'''
_p = steady_power(2.0, 0.004, 60.0)
assert abs(_p - 3.846153846153846) < 1e-9, \
    f"2 W with a = 0.004 through 60 K/W settles at 3.846 W, got {_p}"
assert _p > 2.0, "positive temperature coefficient can only raise the settled power"
'''},
                    {"name": "past the critical resistance there is no steady state", "code": r'''
import math
assert math.isinf(steady_power(2.0, 0.004, 130.0)), \
    "1/(a*P0) is 125 K/W here, so 130 K/W runs away and must return inf"
assert math.isinf(steady_power(2.0, 0.004, 125.0)), \
    "exactly at the critical resistance the denominator is zero — still no solution"
assert not math.isinf(steady_power(2.0, 0.004, 124.0)), \
    "just below the critical resistance a finite, if large, solution still exists"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Size, wind and cool a 500 VA transformer",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
A 48 V, 500 VA transformer for a square-wave converter. You choose the switching
frequency; everything else is fixed by the specification.

The chain is the one this course has been building:

1. `area_product` and `select_core` pick the smallest core that can pass the VA.
2. The turns follow from the flux, and the copper area per turn from the current
   density.
3. The copper is **foil**, so the conductor width is the core's usable window
   height `bw` and its thickness is whatever is left: $h = \frac{A_{cu}}{b_w}$.
   With foil, each turn is its own layer, so the layer count is $N$ — unless the
   winding is interleaved, in which case each half sees $\lceil \frac{N}{2} \rceil$.
4. Dowell's factor multiplies the dc copper loss.
5. Core loss comes from the Steinmetz relation.
6. Temperature rise is $\Delta T = P_{total} R_{th}$ with
   $R_{th} = \frac{1}{h_{conv} A_s}$ and $h_{conv} = 10$ W/m²K.

`cores.py` holds the geometry, the material constants and `H_CONV`. Do not edit it.

## What to write

`evaluate(spec, cores)` runs one frequency end to end and returns a dictionary with
exactly these keys:

```text
f        the frequency it was evaluated at
core     the core's name, a string
N        turns, an int, rounded up
Ap       required area product, m^4
h        foil thickness, m
delta    skin depth, m
m        layer count used for Dowell
FR       Dowell's factor
P_dc     copper loss ignoring eddy currents, W
P_cu     copper loss including them, W
P_fe     core loss, W
P_total  the sum, W
R_th     thermal resistance, K/W
dT       temperature rise, K
```

It returns `None` when no core in the list is large enough.

`choose_design(spec, cores, freqs)` evaluates every frequency in `freqs`, discards
any design whose `dT` exceeds `spec["dT_max"]`, and returns the survivor sitting on
the **smallest** core — smallest by $A_e A_w$, ties broken by the lower frequency.
It returns `None` when nothing survives. The point of the sweep is that the highest
frequency is not the answer: the area product shrinks with $f$, but proximity loss
and core loss do not.

## Suggested order

Write `area_product`, `select_core` and `dowell` first — the first three checks use
nothing else. `evaluate` then assembles them, and `choose_design` is a loop over
`evaluate`.
''',
        "deliverables": [
            "`area_product(VA, f, Bm, J, Ku, Kf)` and `select_core(cores, Ap)`, returning the core dictionary or `None`, exactly as in module 3.",
            "`dowell(h, delta, m)`, Dowell's ac resistance factor, correct in both the thin and the thick limit.",
            "`evaluate(spec, cores)` returning the full fourteen-key design dictionary described above, or `None` when no core fits.",
            "`choose_design(spec, cores, freqs)` returning the smallest-core design that meets `spec['dT_max']`, or `None`.",
            "A comment at the top of `main.py` naming the frequency your sweep chose, the core it landed on, and what interleaving was worth in kelvin.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy and no magnetics package.",
            "`cores.py` is read-only; every geometric number must come from it.",
            "The copper cross-section per turn is `I / J` and the foil width is the core's `bw`; do not invent a different winding geometry.",
            "Interleaving changes only the layer count passed to Dowell, and it changes it to `ceil(N / 2)`.",
            "`select_core` returns the smallest sufficient core, not the first one in the list that happens to fit.",
        ],
        "rubric": [
            {"criterion": "Sizing and core selection", "weight": 20,
             "evidence": "The area product matches the closed form to twelve digits, the smallest sufficient core is returned rather than the first, and an impossible requirement returns None instead of the largest core."},
            {"criterion": "Dowell's factor", "weight": 25,
             "evidence": "The ac resistance factor reproduces the small-Delta series to eight digits and the thick-conductor asymptote Delta*(2m^2+1)/3, and is never below one."},
            {"criterion": "Loss and temperature assembly", "weight": 30,
             "evidence": "evaluate returns every key with the computed value, including the 100 kHz ETD34 case at 54.28 K uninterleaved and 29.95 K interleaved, and the loss split reverses between 50 kHz and 400 kHz."},
            {"criterion": "The frequency sweep", "weight": 15,
             "evidence": "choose_design returns the ETD44 at 50 kHz without interleaving and the ETD34 at 100 kHz with it, and returns None when the temperature limit cannot be met at any frequency."},
            {"criterion": "Design judgement recorded", "weight": 10,
             "evidence": "The comment at the top of main.py states the chosen frequency, the core and the kelvin that interleaving bought, rather than repeating the specification back."},
        ],
        "hints": [
            "`evaluate` is bookkeeping, not cleverness: compute `Ap`, select the core, bail out with `None` if there is none, then walk the six numbered steps in the brief in order.",
            "`P_dc` is $I^2 R_{dc}$ with $R_{dc} = \\frac{\\rho N \\cdot \\text{MLT}}{A_{cu}}$, and `P_cu` is `FR * P_dc`. Keep both — the ratio is the whole story of module 2.",
            "`math.ceil(N / 2)` is the interleaved layer count; note that it is the *layer count*, not the turns, and the dc resistance still uses all `N` turns.",
            "In `choose_design`, `min(survivors, key=lambda d: (core_ap(d), d['f']))` gives the smallest core with the frequency as a tie-break, once you have a way to look a core's area product up from its name.",
        ],
        "files": [
            {"name": "cores.py", "ro": True, "content": r'''
"""Core geometry, material data and cooling constant. Do not edit — the checks
rely on these numbers.

Ae   effective core cross-section, m^2
Aw   window area, m^2
Ve   effective core volume, m^3
MLT  mean length of turn, m
As   exposed surface area for convection, m^2
bw   usable window height, i.e. the widest foil that fits, m
"""

RHO_CU = 1.724e-8            # ohm.m, annealed copper at 20 C
MU0 = 1.2566370614359173e-06  # H/m

# P_v [W/m^3] = K_STEIN * f**ALPHA * Bm**BETA, with f in Hz and Bm in tesla
K_STEIN = 1.5
ALPHA = 1.4
BETA = 2.5

H_CONV = 10.0                # W/m^2K, natural convection

CORES = [
    {"name": "EFD20", "Ae": 31e-6, "Aw": 22e-6, "Ve": 1460e-9,
     "MLT": 0.039, "As": 1.9e-3, "bw": 0.011},
    {"name": "ETD29", "Ae": 76e-6, "Aw": 90e-6, "Ve": 5470e-9,
     "MLT": 0.053, "As": 3.6e-3, "bw": 0.018},
    {"name": "ETD34", "Ae": 97e-6, "Aw": 123e-6, "Ve": 7640e-9,
     "MLT": 0.060, "As": 4.6e-3, "bw": 0.020},
    {"name": "ETD44", "Ae": 173e-6, "Aw": 214e-6, "Ve": 17800e-9,
     "MLT": 0.078, "As": 7.8e-3, "bw": 0.028},
    {"name": "E55", "Ae": 354e-6, "Aw": 250e-6, "Ve": 43900e-9,
     "MLT": 0.116, "As": 1.30e-2, "bw": 0.034},
]

SPEC = {
    "VA": 500.0,
    "V": 48.0,
    "Bm": 0.1,
    "J": 4e6,
    "Ku": 0.4,
    "Kf": 4.0,
    "dT_max": 40.0,
    "interleave": False,
    "f": 100e3,
}

FREQS = [50e3, 100e3, 150e3, 200e3, 300e3, 400e3]
'''},
            {"name": "main.py", "content": r'''
import math
import numpy as np
from cores import (CORES, SPEC, FREQS, RHO_CU, MU0,
                   K_STEIN, ALPHA, BETA, H_CONV)

# Design record:
#   chosen frequency -> TODO
#   chosen core      -> TODO
#   interleaving was worth -> TODO kelvin


def area_product(VA, f, Bm, J, Ku, Kf=4.0):
    """Required Ae*Aw in m^4."""
    # TODO
    return 0.0


def select_core(cores, Ap):
    """The smallest core with Ae*Aw >= Ap, or None."""
    # TODO
    return None


def skin_depth(f, rho=RHO_CU, mu=MU0):
    """Skin depth in metres."""
    # TODO
    return 0.0


def dowell(h, delta, m):
    """Dowell's ratio of ac to dc resistance."""
    # TODO
    return 0.0


def evaluate(spec, cores):
    """Run one frequency end to end. Returns the design dict, or None."""
    # TODO: area product, core, turns, foil, Dowell, losses, temperature.
    return None


def choose_design(spec, cores, freqs):
    """The smallest-core design meeting spec['dT_max'], or None."""
    # TODO
    return None


if __name__ == "__main__":
    d = evaluate(dict(SPEC), CORES)
    print("at 100 kHz:", d)
    best = choose_design(dict(SPEC, interleave=True), CORES, FREQS)
    print("chosen:", best)
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import math
import numpy as np
from cores import (CORES, SPEC, FREQS, RHO_CU, MU0,
                   K_STEIN, ALPHA, BETA, H_CONV)

# Design record:
#   chosen frequency -> 100 kHz. The sweep's 50 kHz entry is cooler but needs an
#                       ETD44; 150 kHz and above all breach the 40 K limit because
#                       the core list bottoms out at the ETD29, whose smaller
#                       surface pushes R_th to 27.8 K/W against the ETD34's 21.7,
#                       while Dowell's factor keeps climbing. Copper still
#                       dominates at 150 and 200 kHz; core loss only takes over
#                       by 300 kHz.
#   chosen core      -> ETD34, at 29.95 K rise against a 40 K budget.
#   interleaving was worth -> 24.33 K at 100 kHz (54.28 K down to 29.95 K), and it
#                       is what makes the smaller core possible at all.


def area_product(VA, f, Bm, J, Ku, Kf=4.0):
    """Required Ae*Aw in m^4."""
    return float(VA) / (float(Kf) * float(f) * float(Bm) * float(J) * float(Ku))


def select_core(cores, Ap):
    """The smallest core with Ae*Aw >= Ap, or None."""
    big = [c for c in cores if c["Ae"] * c["Aw"] >= Ap]
    if not big:
        return None
    return min(big, key=lambda c: c["Ae"] * c["Aw"])


def skin_depth(f, rho=RHO_CU, mu=MU0):
    """Skin depth in metres."""
    return float(np.sqrt(rho / (np.pi * float(f) * mu)))


def dowell(h, delta, m):
    """Dowell's ratio of ac to dc resistance."""
    d = float(h) / float(delta)
    skin = d * (np.sinh(2.0 * d) + np.sin(2.0 * d)) / (np.cosh(2.0 * d) - np.cos(2.0 * d))
    prox = d * (2.0 * (m * m - 1.0) / 3.0) * (np.sinh(d) - np.sin(d)) / (np.cosh(d) + np.cos(d))
    return float(skin + prox)


def evaluate(spec, cores):
    """Run one frequency end to end. Returns the design dict, or None."""
    VA = float(spec["VA"])
    V = float(spec["V"])
    f = float(spec["f"])
    Bm = float(spec["Bm"])
    J = float(spec["J"])
    Ku = float(spec["Ku"])
    Kf = float(spec.get("Kf", 4.0))

    Ap = area_product(VA, f, Bm, J, Ku, Kf)
    core = select_core(cores, Ap)
    if core is None:
        return None

    N = int(math.ceil(V / (Kf * f * Bm * core["Ae"])))
    I = VA / V
    Acu = I / J
    h = Acu / core["bw"]
    delta = skin_depth(f)
    m = int(math.ceil(N / 2)) if spec.get("interleave") else N
    FR = dowell(h, delta, m)

    R_dc = RHO_CU * N * core["MLT"] / Acu
    P_dc = I * I * R_dc
    P_cu = FR * P_dc
    P_fe = K_STEIN * f ** ALPHA * Bm ** BETA * core["Ve"]
    P_total = P_cu + P_fe
    R_th = 1.0 / (H_CONV * core["As"])

    return {"f": f, "core": core["name"], "N": N, "Ap": Ap, "h": h,
            "delta": delta, "m": m, "FR": FR, "P_dc": P_dc, "P_cu": P_cu,
            "P_fe": P_fe, "P_total": P_total, "R_th": R_th,
            "dT": P_total * R_th}


def choose_design(spec, cores, freqs):
    """The smallest-core design meeting spec['dT_max'], or None."""
    ap_of = {c["name"]: c["Ae"] * c["Aw"] for c in cores}
    limit = float(spec["dT_max"])
    survivors = []
    for f in freqs:
        d = evaluate(dict(spec, f=f), cores)
        if d is not None and d["dT"] <= limit:
            survivors.append(d)
    if not survivors:
        return None
    return min(survivors, key=lambda d: (ap_of[d["core"]], d["f"]))


if __name__ == "__main__":
    d = evaluate(dict(SPEC), CORES)
    print("at 100 kHz:", d)
    best = choose_design(dict(SPEC, interleave=True), CORES, FREQS)
    print("chosen:", best)
'''},
        ],
        "tests": [
            {"name": "the area product and the core selection agree with module 3", "code": r'''
from cores import CORES
_ap = area_product(500.0, 100e3, 0.1, 4e6, 0.4)
assert abs(_ap - 7.8125e-09) < 1e-18, f"expected 7.8125e-9 m^4, got {_ap}"
_c = select_core(CORES, _ap)
assert _c is not None and _c["name"] == "ETD34", \
    f"the smallest sufficient core here is the ETD34, got {_c}"
_c2 = select_core(CORES, area_product(20000.0, 100e3, 0.1, 4e6, 0.4))
assert _c2 is None, "nothing in the list passes 20 kVA — return None, not the E55"
'''},
            {"name": "Dowell's factor is right in both limits", "code": r'''
_thin = dowell(1e-5, 2e-4, 6)
assert abs(_thin - 1.0000248611048452) < 1e-9, \
    f"at Delta = 0.05 with 6 layers the factor is 1.0000249, got {_thin}"
assert _thin > 1.0, "eddy currents only ever add loss, so the factor never falls below 1"
_thick = dowell(20.0, 1.0, 4)
assert abs(_thick - 219.9999989108639) < 1e-6, \
    f"at Delta = 20 with 4 layers the factor is 220, got {_thick}"
_series = dowell(0.1, 1.0, 3)
assert abs(_series - (1.0 + (5 * 9 - 1) * 0.1 ** 4 / 45.0)) < 1e-8, \
    f"the small-Delta expansion 1 + (5m^2-1)Delta^4/45 should hold, got {_series}"
'''},
            {"name": "the skin depth used by the design is copper's", "code": r'''
_d = skin_depth(100e3)
assert abs(_d - 0.00020897231909955822) < 1e-15, \
    f"copper at 100 kHz has a skin depth of 209 um, got {_d}"
_d4 = skin_depth(400e3)
assert _d > 0.0, "skin depth must be positive before the ratio means anything"
assert abs(_d / _d4 - 2.0) < 1e-9, \
    f"four times the frequency halves the skin depth, got a ratio of {_d / _d4}"
'''},
            {"name": "the 100 kHz design is assembled correctly", "code": r'''
from cores import CORES, SPEC
_d = evaluate(dict(SPEC), CORES)
assert _d is not None, "an ETD34 fits this specification, so evaluate must not return None"
assert _d["core"] == "ETD34", f"expected the ETD34, got {_d['core']}"
assert _d["N"] == 13, f"48 V on 97 mm^2 at 0.1 T and 100 kHz needs 13 turns, got {_d['N']}"
assert _d["m"] == 13, "without interleaving every foil turn is its own layer"
assert abs(_d["h"] - 0.00013020833333333333) < 1e-15, \
    f"2.604 mm^2 of copper across a 20 mm window is 130 um of foil, got {_d['h']}"
assert abs(_d["FR"] - 3.809890523665972) < 1e-9, f"Dowell's factor here is 3.8099, got {_d['FR']}"
assert abs(_d["P_dc"] - 0.5602999999999999) < 1e-9, f"dc copper loss is 0.5603 W, got {_d['P_dc']}"
assert abs(_d["P_fe"] - 0.36239701985529593) < 1e-9, f"core loss is 0.3624 W, got {_d['P_fe']}"
assert abs(_d["dT"] - 54.28431913620305) < 1e-6, \
    f"this design runs 54.28 K above ambient, got {_d['dT']}"
'''},
            {"name": "interleaving halves the layers and the temperature rise falls", "code": r'''
from cores import CORES, SPEC
_plain = evaluate(dict(SPEC), CORES)
_split = evaluate(dict(SPEC, interleave=True), CORES)
assert _split["m"] == 7, f"ceil(13/2) is 7 layers per half, got {_split['m']}"
assert _split["core"] == _plain["core"] and _split["N"] == _plain["N"], \
    "interleaving changes the layer count only, not the core or the turns"
assert abs(_split["FR"] - 1.8123414147102004) < 1e-9, \
    f"Dowell's factor falls to 1.8123, got {_split['FR']}"
assert abs(_split["dT"] - 29.953302489509156) < 1e-6, \
    f"the rise falls to 29.95 K, got {_split['dT']}"
assert abs(_plain["dT"] - _split["dT"] - 24.331016646693894) < 1e-6, \
    "interleaving is worth 24.33 K here — that is the number the header comment wants"
'''},
            {"name": "the loss balance reverses across the sweep", "code": r'''
from cores import CORES, SPEC
_lo = evaluate(dict(SPEC, f=50e3, interleave=True), CORES)
_hi = evaluate(dict(SPEC, f=400e3, interleave=True), CORES)
assert _lo["core"] == "ETD44" and _hi["core"] == "ETD29", \
    f"the core should shrink with frequency: got {_lo['core']} and {_hi['core']}"
assert _lo["P_cu"] > _lo["P_fe"], \
    f"at 50 kHz copper dominates: {_lo['P_cu']:.3f} W against {_lo['P_fe']:.3f} W"
assert _hi["P_fe"] > _hi["P_cu"], \
    f"at 400 kHz core loss dominates: {_hi['P_fe']:.3f} W against {_hi['P_cu']:.3f} W"
assert abs(_lo["dT"] - 14.693139954901747) < 1e-6, f"50 kHz gives 14.69 K, got {_lo['dT']}"
assert abs(_hi["dT"] - 60.15209204786856) < 1e-6, f"400 kHz gives 60.15 K, got {_hi['dT']}"
'''},
            {"name": "the sweep picks the smallest core that stays cool enough", "code": r'''
from cores import CORES, SPEC, FREQS
_plain = choose_design(dict(SPEC), CORES, FREQS)
assert _plain is not None, "50 kHz meets 40 K even without interleaving"
assert _plain["core"] == "ETD44" and abs(_plain["f"] - 50e3) < 1e-6, \
    f"without interleaving only 50 kHz survives, on the ETD44; got {_plain['core']} at {_plain['f']}"
_split = choose_design(dict(SPEC, interleave=True), CORES, FREQS)
assert _split is not None, "interleaving should let a smaller core through"
assert _split["core"] == "ETD34" and abs(_split["f"] - 100e3) < 1e-6, \
    f"interleaved, the ETD34 at 100 kHz is the smallest survivor; got {_split['core']} at {_split['f']}"
assert _split["dT"] <= 40.0, f"the survivor must meet the limit, got {_split['dT']}"
'''},
            {"name": "an unreachable temperature limit returns nothing", "code": r'''
from cores import CORES, SPEC, FREQS
_none = choose_design(dict(SPEC, interleave=True, dT_max=5.0), CORES, FREQS)
assert _none is None, \
    "no frequency in the sweep gets under a 5 K rise — return None rather than the coolest"
_some = choose_design(dict(SPEC, interleave=True, dT_max=20.0), CORES, FREQS)
assert _some is not None and _some["core"] == "ETD44", \
    f"a 20 K budget forces the big core back: got {_some}"
'''},
        ],
    },
}
