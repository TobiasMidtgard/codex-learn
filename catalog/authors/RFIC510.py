"""RFIC510 — High-Frequency Transistor Models.

Same authoring rules as CTRL510:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

The device model used throughout is a deliberately simple long-channel one:
square-law current, a linear channel-length-modulation term, C_gs from the
inversion charge and C_gd from the gate-drain overlap. It is not a compact model
anyone would tape out with, and it is exactly enough to make g_m, r_o, the Miller
effect, f_T and the cascode fall out of arithmetic a student can check by hand.
"""

COURSE = {
    "id": "RFIC510",
    "title": "High-Frequency Transistor Models",
    "band": 1,
    "level": "Advanced",
    "prereqs": [],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◈",
    "summary": (
        "A transistor at DC is a controlled current source. A transistor at 5 GHz is a "
        "controlled current source wrapped in three capacitors, and the capacitors decide "
        "almost everything you care about. This course builds the small-signal hybrid-pi "
        "model from the bias point up, adds C_gs and C_gd, shows why C_gd costs far more "
        "than its picofarads suggest, defines f_T and f_max honestly, and ends with the "
        "one topology that exists purely to defeat the problem: the cascode."
    ),
    "outcomes": [
        "Derive g_m and r_o from the drain-current equation and read the intrinsic gain g_m r_o off the bias point alone.",
        "Predict the input capacitance of a common-source stage using the Miller approximation, and say when the approximation stops being trustworthy.",
        "Define f_T and f_max from measurable quantities and compute both from device parameters.",
        "Explain, with numbers, what a cascode buys and what it costs.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that sizes a cascode stage against a simultaneous gain and bandwidth specification.",
    "reading": [
        "*Design of Analog CMOS Integrated Circuits*, Razavi — chapters 6 and 9.",
        "*Analysis and Design of Analog Integrated Circuits*, Gray, Hurst, Lewis & Meyer — chapter 7 for the frequency response.",
        "*The Design of CMOS Radio-Frequency Integrated Circuits*, Lee — chapter 8 for f_T, f_max and what they do not tell you.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Small-signal parameters at the operating point",
            "summary": "The hybrid-pi model is a first-order Taylor expansion of the device equations about a bias point. Every parameter in it is a slope.",
            "concepts": [
                "Small-signal analysis is linearisation: `g_m` is $\\partial I_D/\\partial V_{GS}$ and $1/r_o$ is $\\partial I_D/\\partial V_{DS}$, both evaluated at the bias point.",
                "Square law in saturation: $I_D = \\tfrac{1}{2}\\mu C_{ox}(W/L)V_{ov}^2(1 + \\lambda V_{DS})$, with $V_{ov} = V_{GS} - V_{TH}$.",
                "Three equivalent forms of the same $g_m$: $k_n V_{ov}$, $2I_D/V_{ov}$, and $\\sqrt{2 k_n I_D}$ — each is the convenient one for a different design question.",
                "The intrinsic gain $g_m r_o = 2/(\\lambda V_{ov})$ depends on overdrive and channel length, and not at all on current. Burning more current does not buy gain here.",
                "`g_m/I_D` is the currency of analogue design: it is fixed by $V_{ov}$ alone, and it trades directly against speed.",
                "The model is only valid for signals small enough that the second-order term is negligible — a few tens of millivolts on a 200 mV overdrive.",
            ],
            "sandbox": {
                "title": "Gain, corner frequency, and the fact that they are not yet linked",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 1.2, "K": 12},
                "brief": r'''
A two-pole amplifier response. The flat region on the left is the midband gain — the
$g_m r_o$ of this module. The corner is where the capacitors of the next module
start to matter.

Right now the two are separate sliders. That is the fiction this course spends the
next three modules dismantling.
''',
                "notice": [
                    "Raise $K$ alone. The whole magnitude curve lifts and the corner does not move — gain and bandwidth look independent. In a real stage raising the gain drags the corner down with it, which is the Miller effect of module 2.",
                    "Set $\\zeta$ to 1.5. The poles are now real and well separated, and the slope breaks twice: $-20$ dB/decade after the first, $-40$ after the second. That is exactly a common-source stage with an input pole and an output pole.",
                    "Set $\\zeta$ to 0.1. The peak appears and the phase falls through $-90^\\circ$ almost vertically. A device model that predicts this peak where the real amplifier has none is a model missing a parasitic.",
                ],
            },
            "derive": {
                "title": "Transconductance and output resistance from the square law",
                "minutes": 14,
                "vars": ["I_D", "V_GS", "V_TH", "V_ov", "V_DS", "k_n", "lambda", "g_m", "r_o", "A_0"],
                "brief": r'''
Write $k_n = \mu C_{ox}(W/L)$ so the drain current in saturation is

$$I_D = \frac{1}{2} k_n V_{ov}^2 \left(1 + \lambda V_{DS}\right), \qquad V_{ov} = V_{GS} - V_{TH}$$

Everything in the hybrid-pi model is a partial derivative of that one expression.
''',
                "steps": [
                    {
                        "prompt": "Ignore channel-length modulation for a moment ($\\lambda = 0$). Differentiate $I_D$ with respect to $V_{GS}$ to get $g_m$, in terms of $k_n$ and $V_{ov}$.",
                        "answer": "k_n V_{ov}",
                        "placeholder": "k_n V_{ov}",
                        "hint": "$V_{TH}$ is a constant, so $\\partial V_{ov}/\\partial V_{GS} = 1$ and the chain rule is trivial.",
                        "deconstruct": [
                            "$I_D = \\tfrac{1}{2}k_n V_{ov}^2$ and $V_{ov} = V_{GS} - V_{TH}$.",
                            "So $\\partial I_D/\\partial V_{GS} = k_n V_{ov} \\cdot 1$.",
                        ],
                    },
                    {
                        "prompt": "A bias circuit sets a current, not an overdrive. Eliminate $k_n$ using $I_D = \\tfrac{1}{2}k_n V_{ov}^2$ and write $g_m$ in terms of $I_D$ and $V_{ov}$.",
                        "given": "You have $g_m = k_n V_{ov}$ and $I_D = \\tfrac{1}{2} k_n V_{ov}^2$.",
                        "answer": "\\frac{2 I_D}{V_{ov}}",
                        "placeholder": "\\frac{2 I_D}{V_{ov}}",
                        "hint": "Divide the current equation by the transconductance equation and see what survives.",
                        "deconstruct": [
                            "From the current equation, $k_n = 2I_D/V_{ov}^2$.",
                            "Substitute that into $g_m = k_n V_{ov}$ and one power of $V_{ov}$ cancels.",
                        ],
                    },
                    {
                        "prompt": "Now eliminate $V_{ov}$ instead, and write $g_m$ in terms of $k_n$ and $I_D$.",
                        "answer": "\\sqrt{2 k_n I_D}",
                        "placeholder": "\\sqrt{2 k_n I_D}",
                        "hint": "Solve the current equation for $V_{ov}$ first, then substitute into $g_m = k_n V_{ov}$.",
                        "deconstruct": [
                            "$V_{ov} = \\sqrt{2 I_D / k_n}$.",
                            "$g_m = k_n \\sqrt{2 I_D/k_n} = \\sqrt{2 k_n I_D}$ — transconductance grows only as the square root of current.",
                        ],
                    },
                    {
                        "prompt": "Put $\\lambda$ back. The output resistance is $r_o = \\left(\\partial I_D/\\partial V_{DS}\\right)^{-1}$. Differentiate, then write $r_o$ in terms of $\\lambda$ and $I_D$, treating $\\lambda V_{DS} \\ll 1$ so that the current at the bias point is $I_D$.",
                        "answer": "\\frac{1}{\\lambda I_D}",
                        "placeholder": "\\frac{1}{\\lambda I_D}",
                        "hint": "Only the bracket depends on $V_{DS}$, and its derivative is just $\\lambda$.",
                        "deconstruct": [
                            "$\\partial I_D/\\partial V_{DS} = \\tfrac{1}{2}k_n V_{ov}^2 \\lambda$, and $\\tfrac{1}{2}k_n V_{ov}^2$ is the current itself.",
                            "So the conductance is $\\lambda I_D$ and the resistance is its reciprocal.",
                        ],
                    },
                    {
                        "prompt": "The intrinsic gain is $A_0 = g_m r_o$. Combine the second and fourth results and write $A_0$ in terms of $\\lambda$ and $V_{ov}$ only.",
                        "answer": "\\frac{2}{\\lambda V_{ov}}",
                        "placeholder": "\\frac{2}{\\lambda V_{ov}}",
                        "hint": "Multiply $2I_D/V_{ov}$ by $1/(\\lambda I_D)$ and watch the current disappear.",
                        "deconstruct": [
                            "$A_0 = \\frac{2 I_D}{V_{ov}} \\cdot \\frac{1}{\\lambda I_D}$.",
                            "$I_D$ cancels top and bottom.",
                        ],
                    },
                ],
                "closing": r'''
The last line is the one worth remembering: the maximum gain a single device can
provide is set by its overdrive and its channel length, and current does not appear.
A designer who wants more gain must lower $V_{ov}$ or lengthen the device — and both
of those cost speed, which is what module 3 quantifies.
''',
            },
            "lab": {
                "title": "Small-signal parameters from the bias point",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Implement the square-law device and the three slopes taken from it.

```text
I_D  = 0.5 * MU_COX * (W/L) * V_ov**2 * (1 + LAMBDA * V_DS)
g_m  = dI_D/dV_GS   evaluated at the bias point
r_o  = (dI_D/dV_DS)**-1
```

`MU_COX` and `LAMBDA` are module constants; the width-to-length ratio arrives as the
argument `W_over_L`, so `MU_COX * W_over_L` is the $k_n$ of the derivation.

Five functions:

- `drain_current(V_ov, W_over_L, V_DS)` — the equation above.
- `gm(V_ov, W_over_L, V_DS)` — the exact derivative, so the $(1 + \lambda V_{DS})$
  factor stays in.
- `ro(V_ov, W_over_L, V_DS)` — the reciprocal of the exact $V_{DS}$ derivative.
- `intrinsic_gain(V_ov, W_over_L, V_DS)` — the product of the two.
- `gm_from_current(I_D, W_over_L)` — the $\sqrt{2 k_n I_D}$ form, which is what you
  use when the bias current is what you know.

The checks compare your analytic derivatives against a central difference of your own
`drain_current`, so the two must agree to better than a part in a million.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

MU_COX = 200e-6   # A/V^2, mobility times oxide capacitance per unit area
LAMBDA = 0.08     # 1/V, channel-length modulation coefficient


def drain_current(V_ov, W_over_L, V_DS):
    """Saturation drain current, square law with channel-length modulation."""
    # TODO: 0.5 * MU_COX * W_over_L * V_ov**2 * (1 + LAMBDA * V_DS)
    return 0.0


def gm(V_ov, W_over_L, V_DS):
    """Transconductance dI_D/dV_GS at the operating point."""
    # TODO: differentiate drain_current with respect to V_ov.
    return 0.0


def ro(V_ov, W_over_L, V_DS):
    """Small-signal output resistance, the reciprocal of dI_D/dV_DS."""
    # TODO: only the (1 + LAMBDA * V_DS) bracket depends on V_DS.
    return 0.0


def intrinsic_gain(V_ov, W_over_L, V_DS):
    """The largest voltage gain this one device can produce, g_m * r_o."""
    # TODO
    return 0.0


def gm_from_current(I_D, W_over_L):
    """Transconductance written in terms of the bias current instead."""
    # TODO: sqrt(2 * k_n * I_D), with k_n = MU_COX * W_over_L.
    return 0.0


if __name__ == "__main__":
    V_ov, WL, V_DS = 0.2, 40.0, 1.0
    print("I_D  =", round(drain_current(V_ov, WL, V_DS) * 1e6, 3), "uA")
    print("g_m  =", round(gm(V_ov, WL, V_DS) * 1e3, 4), "mS")
    print("r_o  =", round(ro(V_ov, WL, V_DS) / 1e3, 3), "kohm")
    print("A_0  =", round(intrinsic_gain(V_ov, WL, V_DS), 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

MU_COX = 200e-6   # A/V^2, mobility times oxide capacitance per unit area
LAMBDA = 0.08     # 1/V, channel-length modulation coefficient


def drain_current(V_ov, W_over_L, V_DS):
    """Saturation drain current, square law with channel-length modulation."""
    return 0.5 * MU_COX * W_over_L * V_ov ** 2 * (1.0 + LAMBDA * V_DS)


def gm(V_ov, W_over_L, V_DS):
    """Transconductance dI_D/dV_GS at the operating point."""
    return MU_COX * W_over_L * V_ov * (1.0 + LAMBDA * V_DS)


def ro(V_ov, W_over_L, V_DS):
    """Small-signal output resistance, the reciprocal of dI_D/dV_DS."""
    return 1.0 / (LAMBDA * 0.5 * MU_COX * W_over_L * V_ov ** 2)


def intrinsic_gain(V_ov, W_over_L, V_DS):
    """The largest voltage gain this one device can produce, g_m * r_o."""
    return gm(V_ov, W_over_L, V_DS) * ro(V_ov, W_over_L, V_DS)


def gm_from_current(I_D, W_over_L):
    """Transconductance written in terms of the bias current instead."""
    return float(np.sqrt(2.0 * MU_COX * W_over_L * I_D))


if __name__ == "__main__":
    V_ov, WL, V_DS = 0.2, 40.0, 1.0
    print("I_D  =", round(drain_current(V_ov, WL, V_DS) * 1e6, 3), "uA")
    print("g_m  =", round(gm(V_ov, WL, V_DS) * 1e3, 4), "mS")
    print("r_o  =", round(ro(V_ov, WL, V_DS) / 1e3, 3), "kohm")
    print("A_0  =", round(intrinsic_gain(V_ov, WL, V_DS), 3))
'''}],
                "hints": [
                    "`V_ov ** 2` is the only place the overdrive appears squared — everywhere else it is first order.",
                    "For `ro`, differentiate only the bracket: $\\partial I_D/\\partial V_{DS} = \\tfrac{1}{2}k_n V_{ov}^2\\lambda$, which has no $V_{DS}$ left in it.",
                    "`gm_from_current` is not allowed to call `gm` — it must reach the same number by the square-root route.",
                ],
                "tests": [
                    {"name": "the drain current follows the square law", "code": r'''
_i = drain_current(0.2, 40.0, 1.0)
assert abs(_i - 1.728e-4) < 1e-9, \
    f"0.5*200e-6*40*0.04*1.08 is 172.8 uA, got {_i*1e6:.3f} uA"
_j = drain_current(0.4, 40.0, 1.0)
assert abs(_j / _i - 4.0) < 1e-9, \
    "doubling the overdrive should quadruple the current — check the square"
'''},
                    {"name": "transconductance matches a numerical derivative", "code": r'''
_h = 1e-7
_num = (drain_current(0.2 + _h, 40.0, 1.0) - drain_current(0.2 - _h, 40.0, 1.0)) / (2 * _h)
_ana = gm(0.2, 40.0, 1.0)
assert abs(_ana - _num) < 1e-9 * max(1.0, abs(_num)) + 1e-9, \
    f"g_m is the slope of your own drain_current: analytic {_ana:.6e}, numerical {_num:.6e}"
assert abs(_ana - 1.728e-3) < 1e-9, f"expected 1.728 mS, got {_ana*1e3:.4f} mS"
'''},
                    {"name": "output resistance matches a numerical derivative", "code": r'''
_h = 1e-4
_g = (drain_current(0.2, 40.0, 1.0 + _h) - drain_current(0.2, 40.0, 1.0 - _h)) / (2 * _h)
_num = 1.0 / _g
_ana = ro(0.2, 40.0, 1.0)
assert abs(_ana / _num - 1.0) < 1e-6, \
    f"r_o is the reciprocal slope of your own drain_current: analytic {_ana:.6e}, numerical {_num:.6e}"
assert abs(_ana - 78125.0) < 1e-3, f"expected 78.125 kohm, got {_ana/1e3:.3f} kohm"
'''},
                    {"name": "output resistance does not move with the drain voltage", "code": r'''
_a = ro(0.2, 40.0, 1.0)
_b = ro(0.2, 40.0, 2.0)
assert abs(_a - _b) < 1e-6, \
    "in this model dI_D/dV_DS has no V_DS in it, so r_o is flat with drain voltage — you kept a (1+lambda*V_DS) factor"
'''},
                    {"name": "intrinsic gain is set by overdrive alone", "code": r'''
_a = intrinsic_gain(0.2, 40.0, 1.0)
assert abs(_a - 135.0) < 1e-6, f"g_m*r_o should be 135.0 here, got {_a:.4f}"
_b = intrinsic_gain(0.2, 160.0, 1.0)
assert abs(_a - _b) < 1e-6, \
    "quadrupling W/L quadruples both the current and g_m and quarters r_o — the gain must not move"
_c = intrinsic_gain(0.4, 40.0, 1.0)
assert abs(_c - _a / 2.0) < 1e-6, \
    f"doubling the overdrive should halve the intrinsic gain, got {_c:.4f} against {_a:.4f}"
'''},
                    {"name": "the current form of g_m agrees with the overdrive form", "code": r'''
_i = drain_current(0.2, 40.0, 1.0)
_a = gm_from_current(_i, 40.0)
_b = gm(0.2, 40.0, 1.0)
assert abs(_a - 1.6627687752661226e-3) < 1e-9, \
    f"sqrt(2*200e-6*40*172.8e-6) is 1.6628 mS, got {_a*1e3:.4f} mS"
assert abs(_a / _b - 1.0) < 0.06, \
    "the two forms differ only by the channel-length-modulation factor, a few per cent"
'''},
                    {"name": "g_m grows only as the square root of current", "code": r'''
_a = gm_from_current(1.0e-4, 40.0)
_b = gm_from_current(4.0e-4, 40.0)
assert abs(_b / _a - 2.0) < 1e-9, \
    f"four times the current should give twice the g_m, got a ratio of {_b/_a:.4f}"
'''},
                    {"name": "a second operating point checks nothing was hard-coded", "code": r'''
assert abs(drain_current(0.3, 20.0, 0.8) - 1.9152e-4) < 1e-9, \
    f"expected 191.52 uA, got {drain_current(0.3, 20.0, 0.8)*1e6:.3f} uA"
assert abs(gm(0.3, 20.0, 0.8) - 1.2768e-3) < 1e-9, \
    f"expected 1.2768 mS, got {gm(0.3, 20.0, 0.8)*1e3:.4f} mS"
assert abs(ro(0.3, 20.0, 0.8) - 69444.44444444444) < 1e-3, \
    f"expected 69.444 kohm, got {ro(0.3, 20.0, 0.8)/1e3:.3f} kohm"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "C_gs, C_gd and the Miller effect",
            "summary": "Two capacitors are added to the model. One of them is small and does most of the damage.",
            "concepts": [
                "In saturation the inversion charge gives $C_{gs} \\approx \\tfrac{2}{3}WLC_{ox}$ plus overlap; $C_{gd}$ is overlap only, and is typically five to ten times smaller.",
                "$C_{gd}$ bridges input and output, so it sees the full voltage swing of both ends. That is what makes it expensive.",
                "Miller's theorem: a bridging impedance $Z$ across a gain of $-A_v$ behaves, seen from the input, like $Z/(1 + A_v)$ to ground — a capacitor is therefore multiplied by $(1 + A_v)$.",
                "$C_{in} = C_{gs} + C_{gd}(1 + A_v)$, and with $A_v = g_m R_L$ the input pole is $1/(2\\pi R_S C_{in})$.",
                "Gain and bandwidth are now coupled: raising $R_L$ raises $A_v$ and lowers the input pole almost proportionally, so the gain-bandwidth product barely moves.",
                "The same bridging capacitor feeds signal forward and creates a right-half-plane zero at $g_m/C_{gd}$ — far away in a good device, but it is the reason the phase keeps falling.",
                "Miller is an approximation: it assumes the output follows the input with a constant gain, which stops being true near and above the corner.",
            ],
            "sandbox": {
                "title": "What raising the gain does to the corner",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 8, "zeta": 1.4, "K": 16},
                "brief": r'''
The same two-pole response, now read as a common-source stage: the plateau is
$g_m R_L$, the first break is the Miller-loaded input pole, and the second is the
output pole.

Move the sliders as though they were coupled. In a real stage they are: raising $K$
by a factor of two roughly halves the corner, because $C_{gd}(1 + A_v)$ has doubled.
''',
                "notice": [
                    "Raise $K$ from 16 to 20 and then drag $\\omega_n$ down by the same ratio. The high-frequency part of the magnitude curve lands almost exactly where it was. That invariant is the gain-bandwidth product, and it is the whole reason Miller multiplication matters.",
                    "Set $\\zeta$ to 1.5 and watch the two breakpoints separate. The lower one is the input pole set by $R_S C_{in}$; only when they are well apart is the single-pole Miller estimate any good.",
                    "Push $\\omega_n$ to 200 with $K$ left at 16. The phase at any fixed frequency below the corner improves. Buying bandwidth by shrinking $C_{gd}$ buys phase margin at the same time.",
                ],
            },
            "derive": {
                "title": "Miller multiplication and the input pole",
                "minutes": 14,
                "vars": ["A_v", "C_gd", "C_gs", "C_M", "C_in", "g_m", "R_S", "R_L", "s", "v_in", "v_out", "f_H"],
                "brief": r'''
A common-source stage. The gate is driven through a source resistance $R_S$, and the
small-signal voltage gain from gate to drain is $-A_v$, so $v_{out} = -A_v v_{in}$
with $A_v = g_m R_L$ positive.

The gate-drain capacitor $C_{gd}$ is connected between those two nodes. Work out what
the input sees.
''',
                "steps": [
                    {
                        "prompt": "The current drawn from the input node through $C_{gd}$ is $s C_{gd}\\left(v_{in} - v_{out}\\right)$. Substitute $v_{out} = -A_v v_{in}$ and write that current in terms of $v_{in}$.",
                        "answer": "s C_{gd} \\left(1 + A_v\\right) v_{in}",
                        "placeholder": "s C_{gd} \\left(1 + A_v\\right) v_{in}",
                        "hint": "Subtracting a negative number adds. The two ends of the capacitor move in opposite directions, so the voltage across it is larger than the input swing.",
                        "deconstruct": [
                            "$v_{in} - v_{out} = v_{in} - (-A_v v_{in}) = v_{in}(1 + A_v)$.",
                            "Multiply by the admittance $s C_{gd}$.",
                        ],
                    },
                    {
                        "prompt": "Divide that current by $v_{in}$ to get the admittance the input sees, then read off the equivalent grounded capacitance $C_M$ in terms of $C_{gd}$ and $A_v$.",
                        "answer": "C_{gd} \\left(1 + A_v\\right)",
                        "placeholder": "C_{gd} \\left(1 + A_v\\right)",
                        "hint": "An admittance of the form $sC$ is a capacitor of value $C$.",
                        "deconstruct": [
                            "The admittance is $s C_{gd}(1 + A_v)$.",
                            "Comparing with $sC$ gives $C = C_{gd}(1 + A_v)$.",
                        ],
                    },
                    {
                        "prompt": "$C_{gs}$ already sits from gate to ground and is not multiplied. Write the total input capacitance $C_{in}$.",
                        "answer": "C_{gs} + C_{gd} \\left(1 + A_v\\right)",
                        "placeholder": "C_{gs} + C_{gd} \\left(1 + A_v\\right)",
                        "hint": "Two capacitors from the same node to ground add.",
                        "deconstruct": [
                            "$C_{gs}$ contributes its own value, unmultiplied, because both of its terminals do not move relative to each other in the way $C_{gd}$'s do.",
                            "$C_{gd}$ contributes the Miller capacitance from the previous step.",
                        ],
                    },
                    {
                        "prompt": "The input node is a single-pole RC with source resistance $R_S$. Write the $-3$ dB frequency $f_H$ in hertz, in terms of $R_S$, $C_{gs}$, $C_{gd}$ and $A_v$.",
                        "answer": "\\frac{1}{2 \\pi R_S \\left( C_{gs} + C_{gd} \\left(1 + A_v\\right) \\right)}",
                        "placeholder": "\\frac{1}{2 \\pi R_S \\left(C_{gs} + C_{gd}(1 + A_v)\\right)}",
                        "hint": "A first-order RC corner is at $1/(2\\pi RC)$; substitute the $C_{in}$ you just wrote.",
                        "deconstruct": [
                            "The pole is at $\\omega_H = 1/(R_S C_{in})$.",
                            "Divide by $2\\pi$ to get hertz, and expand $C_{in}$.",
                        ],
                    },
                    {
                        "prompt": "At high enough frequency the current fed forward through $C_{gd}$ cancels the current $g_m v_{in}$ pulled by the transistor, and the output is zero. Set $s C_{gd} v_{in} = g_m v_{in}$ and write the zero location $s$.",
                        "answer": "\\frac{g_m}{C_{gd}}",
                        "placeholder": "\\frac{g_m}{C_{gd}}",
                        "hint": "This is a positive value of $s$ — the zero is in the right half-plane, which subtracts phase like a pole while adding gain like a zero.",
                        "deconstruct": [
                            "Cancel $v_{in}$ from both sides: $s C_{gd} = g_m$.",
                            "So $s = g_m/C_{gd}$, positive and therefore in the right half-plane.",
                        ],
                    },
                ],
                "closing": r'''
Two facts to carry forward. First, $C_{gd}$ enters the input capacitance multiplied by
the gain, so a 6 fF overlap capacitor can look like 110 fF. Second, the estimate above
assumes $v_{out} = -A_v v_{in}$ at *every* frequency, which is false near the corner —
the lab measures exactly how wrong that makes the answer.
''',
            },
            "lab": {
                "title": "Miller estimate against an exact nodal solution",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Build the common-source stage twice: once with the Miller approximation, once by
solving the nodal equations exactly, and compare.

The circuit has two nodes. Node 1 is the gate, driven from `vs` through `Rs`, with
`Cgs` to ground and `Cgd` to node 2. Node 2 is the drain, with `RL` to ground and the
controlled current `gm * v1` flowing out of it. With $s = j2\pi f$ the nodal
admittance matrix is

```text
[ 1/Rs + s*(Cgs + Cgd)      -s*Cgd            ] [v1]   [vs/Rs]
[ gm - s*Cgd                 1/RL + s*Cgd     ] [v2] = [  0   ]
```

Write four functions:

- `miller_cap(Cgd, Av)` — the multiplied capacitance $C_{gd}(1 + A_v)$.
- `input_cap(Cgs, Cgd, Av)` — the total $C_{in}$.
- `stage_gain(f, gm, RL, Rs, Cgs, Cgd)` — solve the 2x2 complex system with `vs = 1`
  and return `v2` as a Python `complex`.
- `miller_bandwidth(gm, RL, Rs, Cgs, Cgd)` — the single-pole estimate
  $1/(2\pi R_S C_{in})$ with $A_v = g_m R_L$.
- `exact_bandwidth(gm, RL, Rs, Cgs, Cgd)` — bisect on $\log f$ until
  $|v_2(f)| = |v_2(0)|/\sqrt{2}$.

For the bisection, 1 Hz to $10^{13}$ Hz with a hundred halvings is plenty and costs
nothing.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def miller_cap(Cgd, Av):
    """The grounded capacitance an input node sees in place of a bridging Cgd."""
    # TODO
    return 0.0


def input_cap(Cgs, Cgd, Av):
    """Total capacitance at the gate under the Miller approximation."""
    # TODO
    return 0.0


def stage_gain(f, gm, RL, Rs, Cgs, Cgd):
    """Exact v2/vs of the common-source stage at frequency f, as a complex number."""
    s = 2j * np.pi * f
    # TODO: build the 2x2 complex admittance matrix, drive it with vs = 1, solve.
    return 0j


def miller_bandwidth(gm, RL, Rs, Cgs, Cgd):
    """Single-pole estimate of the -3 dB frequency, in hertz."""
    # TODO: Av = gm * RL, then 1 / (2*pi*Rs*Cin).
    return 0.0


def exact_bandwidth(gm, RL, Rs, Cgs, Cgd, lo=1.0, hi=1e13):
    """Frequency where |stage_gain| has fallen to |stage_gain(0)| / sqrt(2)."""
    # TODO: bisect on the logarithm of frequency.
    return 0.0


if __name__ == "__main__":
    gm, RL, Rs = 1.728e-3, 10e3, 5e3
    Cgs, Cgd = 57.3e-15, 6.0e-15
    print("DC gain      :", round(stage_gain(0.0, gm, RL, Rs, Cgs, Cgd).real, 4))
    print("C_in         :", round(input_cap(Cgs, Cgd, gm * RL) * 1e15, 2), "fF")
    print("Miller f_H   :", round(miller_bandwidth(gm, RL, Rs, Cgs, Cgd) / 1e6, 2), "MHz")
    print("exact f_H    :", round(exact_bandwidth(gm, RL, Rs, Cgs, Cgd) / 1e6, 2), "MHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def miller_cap(Cgd, Av):
    """The grounded capacitance an input node sees in place of a bridging Cgd."""
    return Cgd * (1.0 + Av)


def input_cap(Cgs, Cgd, Av):
    """Total capacitance at the gate under the Miller approximation."""
    return Cgs + miller_cap(Cgd, Av)


def stage_gain(f, gm, RL, Rs, Cgs, Cgd):
    """Exact v2/vs of the common-source stage at frequency f, as a complex number."""
    s = 2j * np.pi * f
    Y = np.array([
        [1.0 / Rs + s * (Cgs + Cgd), -s * Cgd],
        [gm - s * Cgd, 1.0 / RL + s * Cgd],
    ], dtype=complex)
    rhs = np.array([1.0 / Rs, 0.0], dtype=complex)
    return complex(np.linalg.solve(Y, rhs)[1])


def miller_bandwidth(gm, RL, Rs, Cgs, Cgd):
    """Single-pole estimate of the -3 dB frequency, in hertz."""
    Cin = input_cap(Cgs, Cgd, gm * RL)
    return 1.0 / (2.0 * np.pi * Rs * Cin)


def exact_bandwidth(gm, RL, Rs, Cgs, Cgd, lo=1.0, hi=1e13):
    """Frequency where |stage_gain| has fallen to |stage_gain(0)| / sqrt(2)."""
    target = abs(stage_gain(0.0, gm, RL, Rs, Cgs, Cgd)) / np.sqrt(2.0)
    for _ in range(120):
        mid = np.sqrt(lo * hi)
        if abs(stage_gain(mid, gm, RL, Rs, Cgs, Cgd)) > target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


if __name__ == "__main__":
    gm, RL, Rs = 1.728e-3, 10e3, 5e3
    Cgs, Cgd = 57.3e-15, 6.0e-15
    print("DC gain      :", round(stage_gain(0.0, gm, RL, Rs, Cgs, Cgd).real, 4))
    print("C_in         :", round(input_cap(Cgs, Cgd, gm * RL) * 1e15, 2), "fF")
    print("Miller f_H   :", round(miller_bandwidth(gm, RL, Rs, Cgs, Cgd) / 1e6, 2), "MHz")
    print("exact f_H    :", round(exact_bandwidth(gm, RL, Rs, Cgs, Cgd) / 1e6, 2), "MHz")
'''}],
                "hints": [
                    "`np.linalg.solve` works on complex matrices as long as you build them with `dtype=complex`.",
                    "At `f = 0` the matrix is real and the gain must come out as exactly $-g_m R_L$ — check that before trusting anything at high frequency.",
                    "Bisect on the geometric mean, `mid = np.sqrt(lo*hi)`, not the arithmetic one: the answer spans decades.",
                ],
                "tests": [
                    {"name": "Miller multiplication scales with the gain", "code": r'''
assert abs(miller_cap(6e-15, 17.28) - 1.0968e-13) < 1e-18, \
    f"6 fF across a gain of 17.28 looks like 109.68 fF, got {miller_cap(6e-15,17.28)*1e15:.3f} fF"
assert abs(miller_cap(6e-15, 0.0) - 6e-15) < 1e-20, \
    "with no gain the bridging capacitor is worth exactly its own value, not zero"
assert abs(input_cap(57.3e-15, 6e-15, 17.28) - 1.6698e-13) < 1e-18, \
    "C_gs adds unmultiplied on top of the Miller capacitance"
'''},
                    {"name": "the DC gain is minus g_m R_L", "code": r'''
_g = stage_gain(0.0, 1.728e-3, 10e3, 5e3, 57.3e-15, 6.0e-15)
assert abs(_g.real + 17.28) < 1e-6 and abs(_g.imag) < 1e-9, \
    f"at DC the capacitors vanish and the gain is -g_m*R_L = -17.28, got {_g}"
_g2 = stage_gain(0.0, 1.728e-3, 50e3, 5e3, 57.3e-15, 6.0e-15)
assert abs(_g2.real + 86.4) < 1e-6, f"with RL = 50k the DC gain is -86.4, got {_g2.real:.4f}"
'''},
                    {"name": "the source resistance does not change the DC gain", "code": r'''
_a = stage_gain(0.0, 1.728e-3, 10e3, 5e3, 57.3e-15, 6.0e-15)
_b = stage_gain(0.0, 1.728e-3, 10e3, 500e3, 57.3e-15, 6.0e-15)
assert abs(_a - _b) < 1e-9, \
    "no current flows into a capacitive gate at DC, so Rs drops nothing — you have loaded the input resistively"
'''},
                    {"name": "the Miller estimate lands where the algebra says", "code": r'''
_f = miller_bandwidth(1.728e-3, 10e3, 5e3, 57.3e-15, 6.0e-15)
assert abs(_f - 190627551.91267857) < 1e3, \
    f"1/(2*pi*5k*166.98fF) is 190.63 MHz, got {_f/1e6:.3f} MHz"
'''},
                    {"name": "the exact bandwidth is a genuine -3 dB point", "code": r'''
import numpy as np
_args = (1.728e-3, 10e3, 5e3, 57.3e-15, 6.0e-15)
_f = exact_bandwidth(*_args)
_ratio = abs(stage_gain(_f, *_args)) / abs(stage_gain(0.0, *_args))
assert abs(_ratio - 1.0 / np.sqrt(2.0)) < 1e-4, \
    f"the gain at your reported bandwidth is {_ratio:.5f} of the DC gain, not 0.70711"
assert abs(_f / 181748721.23416194 - 1.0) < 0.02, \
    f"expected about 181.7 MHz, got {_f/1e6:.3f} MHz"
'''},
                    {"name": "Miller is optimistic but close while the poles are apart", "code": r'''
_args = (1.728e-3, 10e3, 5e3, 57.3e-15, 6.0e-15)
_m = miller_bandwidth(*_args)
_e = exact_bandwidth(*_args)
assert _m > _e, \
    "Miller ignores the output pole, so it always predicts a slightly wider band than the exact solution"
assert abs(_m / _e - 1.0) < 0.10, \
    f"the two should agree within about 5 per cent here, got {_m/_e:.4f}"
'''},
                    {"name": "raising the gain eats the bandwidth", "code": r'''
_lo = exact_bandwidth(1.728e-3, 10e3, 5e3, 57.3e-15, 6.0e-15)
_hi = exact_bandwidth(1.728e-3, 50e3, 5e3, 57.3e-15, 6.0e-15)
assert _hi < _lo, "five times the load resistance means five times the Miller capacitance"
assert abs(_hi / 50021827.30152913 - 1.0) < 0.02, \
    f"with RL = 50k expect about 50.0 MHz, got {_hi/1e6:.3f} MHz"
assert 2.5 < _lo / _hi < 4.5, \
    f"the bandwidth should fall by roughly the gain ratio, got a factor of {_lo/_hi:.3f}"
'''},
                    {"name": "removing C_gd removes the problem", "code": r'''
_with = exact_bandwidth(1.728e-3, 10e3, 5e3, 57.3e-15, 6.0e-15)
_without = exact_bandwidth(1.728e-3, 10e3, 5e3, 57.3e-15, 0.0)
assert _without > 3.0 * _with, \
    f"a 6 fF capacitor is costing two thirds of the bandwidth: {_with/1e6:.1f} MHz against {_without/1e6:.1f} MHz"
assert abs(_without / 555514635.5738056 - 1.0) < 0.02, \
    f"with Cgd = 0 the corner is 1/(2*pi*Rs*Cgs) = 555.5 MHz, got {_without/1e6:.1f} MHz"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "f_T, f_max and what they do not promise",
            "summary": "Two figures of merit that describe the device alone. Neither is the bandwidth of any amplifier you will build with it.",
            "concepts": [
                "$f_T$ is defined by a measurement: short the drain to small-signal ground and find the frequency at which the short-circuit current gain magnitude falls to one.",
                "$f_T = g_m/\\left(2\\pi(C_{gs}+C_{gd})\\right)$ — transconductance divided by the charge you must move to obtain it.",
                "For a long-channel device this collapses to $3\\mu V_{ov}/(4\\pi L^2)$: speed comes from short channels and high overdrive, and the length term dominates.",
                "The exact answer keeps the feed-forward term and gives $g_m/\\left(2\\pi\\sqrt{C_{gs}(C_{gs}+2C_{gd})}\\right)$ — a few per cent above the usual formula.",
                "$f_{max}$ is where the *power* gain reaches one, and unlike $f_T$ it depends on the gate resistance: $f_{max} = \\sqrt{f_T/(16\\pi R_g C_{gd})}$.",
                "Layout changes $f_{max}$ and not $f_T$. Splitting a wide device into fingers contacted at both ends cuts $R_g$ and buys speed for free.",
                "A stage built from a 5 GHz device does not have 5 GHz of bandwidth. $f_T$ assumes a shorted output and no source resistance; both assumptions are violated in every real circuit.",
            ],
            "sandbox": {
                "title": "How far away the second pole has to be",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 0.5, "wn": 6},
                "brief": r'''
Step response and pole locations for a two-pole amplifier. Read the poles as the
input pole of module 2 and a second pole set by the device — the one that scales with
$f_T$.

A device with a higher $f_T$ pushes its own pole further out, which for a fixed
input pole shows up here as higher $\zeta$.
''',
                "notice": [
                    "Take $\\zeta$ to 0.3. The response overshoots and rings. That is what a second pole sitting too close to the first does, and it is why a slow device cannot simply be used in a fast loop.",
                    "Take $\\zeta$ to 1.0 and then to 1.6. Overshoot disappears entirely at $\\zeta = 1$ and settling gets slower after it — pushing the device pole further out past the critical point stops helping.",
                    "Hold $\\zeta$ and raise $\\omega_n$ from 2 to 12. The curve keeps its exact shape and only the time axis compresses. Scaling every capacitance down by the same factor does precisely this, which is what a process shrink delivers.",
                ],
            },
            "derive": {
                "title": "The transit frequency and the maximum oscillation frequency",
                "minutes": 15,
                "vars": ["g_m", "C_gs", "C_gd", "omega", "omega_T", "f_T", "f_max", "mu", "C_ox", "V_ov", "W", "L", "R_g", "v_gs"],
                "brief": r'''
Short the drain to small-signal ground and drive the gate with a current. All of that
current flows into $C_{gs}$ and $C_{gd}$, because the gate itself draws none:

$$i_{in} = s\left(C_{gs} + C_{gd}\right) v_{gs}, \qquad i_{out} = g_m v_{gs}$$

taking the feed-forward through $C_{gd}$ as negligible for now.
''',
                "steps": [
                    {
                        "prompt": "Form the short-circuit current gain magnitude $\\left|i_{out}/i_{in}\\right|$ at frequency $\\omega$, in terms of $g_m$, $\\omega$, $C_{gs}$ and $C_{gd}$.",
                        "answer": "\\frac{g_m}{\\omega \\left( C_{gs} + C_{gd} \\right)}",
                        "placeholder": "\\frac{g_m}{\\omega \\left(C_{gs} + C_{gd}\\right)}",
                        "hint": "$|s| = \\omega$ on the imaginary axis, and $v_{gs}$ cancels.",
                        "deconstruct": [
                            "$i_{out}/i_{in} = g_m / \\left(s(C_{gs}+C_{gd})\\right)$.",
                            "Take magnitudes with $s = j\\omega$.",
                        ],
                    },
                    {
                        "prompt": "Set that magnitude to one and solve for the transit frequency $\\omega_T$ in rad/s.",
                        "answer": "\\frac{g_m}{C_{gs} + C_{gd}}",
                        "placeholder": "\\frac{g_m}{C_{gs} + C_{gd}}",
                        "hint": "Multiply both sides by the denominator and read off $\\omega$.",
                        "deconstruct": [
                            "$g_m = \\omega_T (C_{gs}+C_{gd})$.",
                            "Divide through by the total capacitance.",
                        ],
                    },
                    {
                        "prompt": "Write the same thing in hertz as $f_T$.",
                        "answer": "\\frac{g_m}{2 \\pi \\left( C_{gs} + C_{gd} \\right)}",
                        "placeholder": "\\frac{g_m}{2 \\pi \\left(C_{gs} + C_{gd}\\right)}",
                        "hint": "$f = \\omega/(2\\pi)$.",
                        "deconstruct": [
                            "Divide $\\omega_T$ by $2\\pi$.",
                        ],
                    },
                    {
                        "prompt": "Now substitute the long-channel expressions $g_m = \\mu C_{ox}(W/L)V_{ov}$ and $C_{gs} = \\tfrac{2}{3}WLC_{ox}$, and neglect $C_{gd}$ entirely. Write $f_T$ in terms of $\\mu$, $V_{ov}$ and $L$.",
                        "given": "Use $f_T = g_m/\\left(2\\pi C_{gs}\\right)$ with those two substitutions.",
                        "answer": "\\frac{3 \\mu V_{ov}}{4 \\pi L^{2}}",
                        "placeholder": "\\frac{3 \\mu V_{ov}}{4 \\pi L^{2}}",
                        "hint": "$W$ and $C_{ox}$ appear once on the top and once on the bottom, so both cancel. What is left is one $L$ from $g_m$ and one from $C_{gs}$.",
                        "deconstruct": [
                            "$\\frac{g_m}{C_{gs}} = \\frac{\\mu C_{ox}(W/L)V_{ov}}{\\tfrac{2}{3}WLC_{ox}} = \\frac{3\\mu V_{ov}}{2L^2}$.",
                            "Divide by $2\\pi$ to reach hertz.",
                        ],
                    },
                    {
                        "prompt": "The standard result for the maximum oscillation frequency is $\\omega_{max} = \\sqrt{\\omega_T/\\left(8 R_g C_{gd}\\right)}$. Convert both frequencies to hertz and write $f_{max}$ in terms of $f_T$, $R_g$ and $C_{gd}$.",
                        "answer": "\\sqrt{\\frac{f_T}{16 \\pi R_g C_{gd}}}",
                        "placeholder": "\\sqrt{\\frac{f_T}{16 \\pi R_g C_{gd}}}",
                        "hint": "Substitute $\\omega_T = 2\\pi f_T$, then divide the whole square root by $2\\pi$ — which means dividing what is inside it by $4\\pi^2$.",
                        "deconstruct": [
                            "$\\omega_{max} = \\sqrt{2\\pi f_T/(8R_gC_{gd})}$, so $f_{max} = \\frac{1}{2\\pi}\\sqrt{\\frac{2\\pi f_T}{8R_gC_{gd}}}$.",
                            "Pull the $1/(2\\pi)$ inside as $1/(4\\pi^2)$: the $2\\pi$ on top cancels one of them and $8 \\cdot 2\\pi = 16\\pi$ is left underneath.",
                        ],
                    },
                ],
                "closing": r'''
$f_T$ is a property of the device and its bias, nothing more. $f_{max}$ additionally
knows about the layout through $R_g$, which is why two devices with identical $f_T$
can differ by a factor of two in $f_{max}$. Neither number is the bandwidth of an
amplifier: both assume conditions no amplifier operates under.
''',
            },
            "lab": {
                "title": "Measure f_T the way the definition says",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Rather than trusting the formula, find $f_T$ by doing what the definition describes.

With the drain shorted, and now keeping the feed-forward current through $C_{gd}$,

```text
i_in  = s * (Cgs + Cgd) * vgs
i_out = gm * vgs - s * Cgd * vgs
h21   = i_out / i_in = (gm - s*Cgd) / (s*(Cgs + Cgd))
```

Write:

- `h21(f, gm, Cgs, Cgd)` — the complex short-circuit current gain at frequency `f`.
- `ft_simple(gm, Cgs, Cgd)` — the textbook $g_m/\left(2\pi(C_{gs}+C_{gd})\right)$.
- `ft_numeric(gm, Cgs, Cgd)` — bisect on $\log f$ for the frequency where
  $|h_{21}| = 1$ exactly, using your own `h21`.
- `f_max(ft, Rg, Cgd)` — the expression you derived.

The two $f_T$ values will not be identical, and the difference is the point of the
exercise: the feed-forward term subtracts from the output current but adds to nothing
in the input current, so the true unity-gain frequency is a little *higher* than the
formula claims.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def h21(f, gm, Cgs, Cgd):
    """Short-circuit current gain of the hybrid-pi model, as a complex number."""
    s = 2j * np.pi * f
    # TODO: (gm - s*Cgd) / (s*(Cgs + Cgd))
    return 0j


def ft_simple(gm, Cgs, Cgd):
    """The usual closed form for the transit frequency, in hertz."""
    # TODO
    return 0.0


def ft_numeric(gm, Cgs, Cgd, lo=1e3, hi=1e15):
    """Frequency where |h21| is exactly 1, found by bisection on log f."""
    # TODO: |h21| falls with frequency, so bisect.
    return 0.0


def f_max(ft, Rg, Cgd):
    """Maximum oscillation frequency, in hertz."""
    # TODO: sqrt(ft / (16*pi*Rg*Cgd))
    return 0.0


if __name__ == "__main__":
    gm, Cgs, Cgd = 1.728e-3, 57.3e-15, 6.0e-15
    print("f_T (formula) :", round(ft_simple(gm, Cgs, Cgd) / 1e9, 4), "GHz")
    print("f_T (measured):", round(ft_numeric(gm, Cgs, Cgd) / 1e9, 4), "GHz")
    print("f_max (Rg=200):", round(f_max(ft_simple(gm, Cgs, Cgd), 200.0, Cgd) / 1e9, 4), "GHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def h21(f, gm, Cgs, Cgd):
    """Short-circuit current gain of the hybrid-pi model, as a complex number."""
    s = 2j * np.pi * f
    return complex((gm - s * Cgd) / (s * (Cgs + Cgd)))


def ft_simple(gm, Cgs, Cgd):
    """The usual closed form for the transit frequency, in hertz."""
    return gm / (2.0 * np.pi * (Cgs + Cgd))


def ft_numeric(gm, Cgs, Cgd, lo=1e3, hi=1e15):
    """Frequency where |h21| is exactly 1, found by bisection on log f."""
    for _ in range(150):
        mid = np.sqrt(lo * hi)
        if abs(h21(mid, gm, Cgs, Cgd)) > 1.0:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


def f_max(ft, Rg, Cgd):
    """Maximum oscillation frequency, in hertz."""
    return float(np.sqrt(ft / (16.0 * np.pi * Rg * Cgd)))


if __name__ == "__main__":
    gm, Cgs, Cgd = 1.728e-3, 57.3e-15, 6.0e-15
    print("f_T (formula) :", round(ft_simple(gm, Cgs, Cgd) / 1e9, 4), "GHz")
    print("f_T (measured):", round(ft_numeric(gm, Cgs, Cgd) / 1e9, 4), "GHz")
    print("f_max (Rg=200):", round(f_max(ft_simple(gm, Cgs, Cgd), 200.0, Cgd) / 1e9, 4), "GHz")
'''}],
                "hints": [
                    "In Python `2j * np.pi * f` is already the complex $s$; do not multiply by `1j` again.",
                    "`abs()` of a Python complex is its magnitude, which is all the bisection needs.",
                    "Bisect geometrically — `mid = np.sqrt(lo*hi)` — because the bracket spans twelve decades.",
                ],
                "tests": [
                    {"name": "the current gain falls as one over frequency", "code": r'''
_a = abs(h21(1e7, 1.728e-3, 57.3e-15, 6.0e-15))
_b = abs(h21(2e7, 1.728e-3, 57.3e-15, 6.0e-15))
assert _a > 100, f"well below f_T the current gain should be large, got {_a:.2f}"
assert abs(_a / _b - 2.0) < 1e-3, \
    f"a single pole at the origin means doubling f halves |h21|, got a ratio of {_a/_b:.4f}"
'''},
                    {"name": "the closed form matches the definition", "code": r'''
import numpy as np
_f = ft_simple(1.728e-3, 57.3e-15, 6.0e-15)
assert abs(_f - 4344703659.759796) < 1e4, \
    f"g_m/(2*pi*63.3fF) is 4.3447 GHz, got {_f/1e9:.4f} GHz"
'''},
                    {"name": "the measured f_T really has unity current gain", "code": r'''
_args = (1.728e-3, 57.3e-15, 6.0e-15)
_f = ft_numeric(*_args)
_m = abs(h21(_f, *_args))
assert abs(_m - 1.0) < 1e-6, \
    f"|h21| at your reported f_T is {_m:.8f}, and the definition demands exactly 1"
'''},
                    {"name": "feed-forward pushes the true f_T slightly higher", "code": r'''
_args = (1.728e-3, 57.3e-15, 6.0e-15)
assert ft_numeric(*_args) > ft_simple(*_args), \
    "the -s*Cgd term shrinks |i_out| more slowly than the formula assumes, so unity gain arrives later"
assert abs(ft_numeric(*_args) / 4364353716.6456995 - 1.0) < 1e-4, \
    f"expected 4.3644 GHz, got {ft_numeric(*_args)/1e9:.4f} GHz"
'''},
                    {"name": "a large C_gd makes the difference visible", "code": r'''
_args = (1.728e-3, 57.3e-15, 20.0e-15)
_s = ft_simple(*_args)
_n = ft_numeric(*_args)
assert abs(_s - 3557823307.4100275) < 1e4, f"formula: expected 3.5578 GHz, got {_s/1e9:.4f} GHz"
assert abs(_n - 3683241019.853346) < 1e4, f"measured: expected 3.6832 GHz, got {_n/1e9:.4f} GHz"
assert 1.02 < _n / _s < 1.06, \
    f"with C_gd this large the two definitions differ by about 3.5 per cent, got {_n/_s:.4f}"
'''},
                    {"name": "f_T scales the way the physics says", "code": r'''
_a = ft_simple(1.728e-3, 57.3e-15, 6.0e-15)
_b = ft_simple(2 * 1.728e-3, 57.3e-15, 6.0e-15)
assert abs(_b / _a - 2.0) < 1e-9, "f_T is proportional to g_m at fixed capacitance"
_c = ft_simple(1.728e-3, 2 * 57.3e-15, 2 * 6.0e-15)
assert abs(_c / _a - 0.5) < 1e-9, \
    "doubling every capacitance halves f_T — a wider device gains g_m and capacitance together, which is why width does not buy speed"
'''},
                    {"name": "f_max depends on the gate resistance", "code": r'''
_ft = ft_simple(1.728e-3, 57.3e-15, 6.0e-15)
_a = f_max(_ft, 200.0, 6.0e-15)
assert abs(_a - 8487006390.409767) < 1e4, \
    f"sqrt(4.3447e9 / (16*pi*200*6e-15)) is 8.487 GHz, got {_a/1e9:.4f} GHz"
_b = f_max(_ft, 2000.0, 6.0e-15)
assert abs(_a / _b - np.sqrt(10.0)) < 1e-6, \
    "ten times the gate resistance costs a factor of sqrt(10) in f_max — this is what finger layout buys"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Why the cascode exists",
            "summary": "Stop the input device from swinging its own drain, and the Miller effect has nothing to multiply.",
            "concepts": [
                "A cascode stacks a common-gate device on the common-source device, so the drain of the input transistor drives a low impedance instead of the load.",
                "The resistance looking into the source of the upper device is $\\left(R_L + r_{o2}\\right)/\\left(1 + g_{m2}r_{o2}\\right)$, close to $1/g_{m2}$ when the load is modest.",
                "The gain from gate to the intermediate node is therefore about $-g_{m1}/g_{m2}$, of order one, so $C_{gd1}$ is multiplied by two rather than by the full stage gain.",
                "The output resistance rises to $r_{o1} + r_{o2} + g_{m2}r_{o1}r_{o2}$, so the stage gains voltage gain at the same time as bandwidth.",
                "The price: one $V_{DSsat}$ of headroom, a new pole at the intermediate node near $g_{m2}/\\left(2\\pi C_x\\right)$, and a second device's noise and area.",
                "A cascode does not raise $f_T$. It removes a circuit-level penalty; the device is exactly as fast as it was.",
            ],
            "sandbox": {
                "title": "The corner after the Miller penalty is removed",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 120, "zeta": 1.0, "K": 14},
                "brief": r'''
Same two-pole picture, now representing a cascode: the plateau is higher than a
common-source stage using the same devices, and the corner is roughly six times
further out.

Compare against module 2 by hand: set $\omega_n$ to 8 with $K$ at 16 for the
common-source case, then back to 120 with $K$ at 14 for the cascode.
''',
                "notice": [
                    "Switch between $\\omega_n = 8$ and $\\omega_n = 120$ at similar $K$. The magnitude at 200 rad/s differs by more than 20 dB. That gap is the whole argument for spending a second transistor.",
                    "With $\\omega_n$ at 120, drop $\\zeta$ to 0.3. A peak appears near the corner. In a cascode this is what the intermediate-node pole does when the upper device is made too small: $g_{m2}$ falls, $g_{m2}/C_x$ falls with it, and the second pole closes in.",
                    "Raise $K$ from 14 to 20 with $\\omega_n$ fixed at 120. Nothing happens to the corner. That independence is precisely what the cascode restores and what the common-source stage never had.",
                ],
            },
            "derive": {
                "title": "Input capacitance and output resistance of a cascode",
                "minutes": 14,
                "vars": ["g_m1", "g_m2", "r_o1", "r_o2", "C_gs1", "C_gd1", "C_in", "R_out", "A_1", "A_v", "R_L"],
                "brief": r'''
Device M1 is common-source, driven at its gate. Its drain connects to the source of
M2, whose gate is held at a fixed bias and is therefore a small-signal ground. The
load hangs on the drain of M2.

Take $g_{m2}r_{o2} \gg 1$ throughout, and treat the resistance looking into the source
of M2 as $1/g_{m2}$.
''',
                "steps": [
                    {
                        "prompt": "M1 drives a resistance of $1/g_{m2}$ at its drain. Write the magnitude of the gain $A_1$ from the input gate to that intermediate node, in terms of $g_{m1}$ and $g_{m2}$.",
                        "answer": "\\frac{g_{m1}}{g_{m2}}",
                        "placeholder": "\\frac{g_{m1}}{g_{m2}}",
                        "hint": "A common-source gain magnitude is $g_m$ times whatever resistance the drain sees.",
                        "deconstruct": [
                            "$|A_1| = g_{m1} \\cdot R_{drain}$.",
                            "Here $R_{drain} = 1/g_{m2}$.",
                        ],
                    },
                    {
                        "prompt": "Apply Miller to $C_{gd1}$ using that gain. Write the total input capacitance $C_{in}$ in terms of $C_{gs1}$, $C_{gd1}$, $g_{m1}$ and $g_{m2}$.",
                        "answer": "C_{gs1} + C_{gd1} \\left(1 + \\frac{g_{m1}}{g_{m2}}\\right)",
                        "placeholder": "C_{gs1} + C_{gd1} \\left(1 + \\frac{g_{m1}}{g_{m2}}\\right)",
                        "hint": "The Miller factor is still $1 + |A_1|$; only the value of $|A_1|$ has changed.",
                        "deconstruct": [
                            "From module 2, $C_{in} = C_{gs} + C_{gd}(1 + |A|)$ where $A$ is the gain across the bridging capacitor.",
                            "Substitute $|A_1| = g_{m1}/g_{m2}$, which is about 1 for matched devices instead of tens.",
                        ],
                    },
                    {
                        "prompt": "Now the output. Looking into the drain of M2, the source degeneration provided by $r_{o1}$ boosts the resistance. Write $R_{out}$ exactly, in terms of $r_{o1}$, $r_{o2}$ and $g_{m2}$.",
                        "given": "The standard degenerated-device result is $R_{out} = r_{o2}\\left(1 + g_{m2}r_{o1}\\right) + r_{o1}$.",
                        "answer": "r_{o1} + r_{o2} + g_{m2} r_{o1} r_{o2}",
                        "placeholder": "r_{o1} + r_{o2} + g_{m2} r_{o1} r_{o2}",
                        "hint": "Expand the bracket in the given expression and collect the three terms.",
                        "deconstruct": [
                            "$r_{o2}(1 + g_{m2}r_{o1}) = r_{o2} + g_{m2}r_{o1}r_{o2}$.",
                            "Add the remaining $r_{o1}$.",
                        ],
                    },
                    {
                        "prompt": "One term dominates when $g_{m2}r_{o1} \\gg 1$. Write the approximation.",
                        "answer": "g_{m2} r_{o1} r_{o2}",
                        "placeholder": "g_{m2} r_{o1} r_{o2}",
                        "hint": "Compare the third term with the first two: it is larger by the intrinsic gain of M2.",
                        "deconstruct": [
                            "$g_{m2}r_{o1}r_{o2}$ exceeds $r_{o2}$ by the factor $g_{m2}r_{o1}$, which is of order 100.",
                            "Drop the two small terms.",
                        ],
                    },
                    {
                        "prompt": "If the external load is much larger than $R_{out}$, the stage gain is $-g_{m1}R_{out}$. Write the magnitude of that gain in terms of $g_{m1}$, $g_{m2}$, $r_{o1}$ and $r_{o2}$.",
                        "answer": "g_{m1} g_{m2} r_{o1} r_{o2}",
                        "placeholder": "g_{m1} g_{m2} r_{o1} r_{o2}",
                        "hint": "Multiply the previous answer by $g_{m1}$.",
                        "deconstruct": [
                            "$|A_v| = g_{m1} \\cdot g_{m2}r_{o1}r_{o2}$.",
                            "This is the product of the two intrinsic gains, which is why the cascode is the standard way to reach gains of several hundred from a single stage.",
                        ],
                    },
                ],
                "closing": r'''
Read the two results together. The input capacitance dropped from
$C_{gs}+C_{gd}(1+g_mR_L)$ to roughly $C_{gs}+2C_{gd}$, and the available gain rose
from $g_mr_o$ to $(g_mr_o)^2$. Both improvements come from the same structural change:
the input device no longer sees its own output swing.
''',
            },
            "lab": {
                "title": "Common-source against cascode, by nodal analysis",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
Solve both topologies exactly and compare them on the same devices.

The common-source stage is module 2's circuit with $r_o$ and a load capacitance added
at the output node:

```text
[ 1/Rs + s*(Cgs+Cgd)   -s*Cgd                          ] [v1]   [1/Rs]
[ gm - s*Cgd            1/RL + 1/ro + s*(Cgd + CL)     ] [v2] = [  0 ]
```

The cascode has three nodes: `v1` the input gate, `vx` the drain of M1 and source of
M2, `v2` the output. Both devices are identical, with the same `gm`, `ro`, `Cgs` and
`Cgd`. At node `vx` sit `Cgd` (bridging from `v1`) and the `Cgs` of M2; the current
`gm*v1 + vx/ro` leaves it into M1, and the current `-gm*vx + (v2-vx)/ro` arrives from
M2. Collecting terms:

```text
[ 1/Rs + s*(Cgs+Cgd)   -s*Cgd                     0                          ] [v1]   [1/Rs]
[ gm - s*Cgd            s*(Cgd+Cgs) + 2/ro + gm   -1/ro                      ] [vx] = [  0 ]
[ 0                    -gm - 1/ro                 1/RL + 1/ro + s*(Cgd+CL)   ] [v2]   [  0 ]
```

Write `cs_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL)` and
`cascode_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL)`, both returning a `complex`, plus a
generic `bandwidth(gain_of_f)` that takes a one-argument function of frequency and
returns its $-3$ dB point, and `miller_input_cap(Cgs, Cgd, A1)`.

`bandwidth` taking a function is deliberate: you will call it as
`bandwidth(lambda f: cs_gain(f, *args))` and reuse it unchanged in the capstone.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def miller_input_cap(Cgs, Cgd, A1):
    """Total gate capacitance when the bridging cap sees a gain magnitude A1."""
    # TODO
    return 0.0


def cs_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the common-source stage, as a complex number."""
    s = 2j * np.pi * f
    # TODO: build the 2x2 matrix from the brief and solve it.
    return 0j


def cascode_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the cascode stage, as a complex number."""
    s = 2j * np.pi * f
    # TODO: build the 3x3 matrix from the brief and solve it; return v2.
    return 0j


def bandwidth(gain_of_f, lo=1.0, hi=1e13):
    """-3 dB frequency of any function that maps frequency to a complex gain."""
    # TODO: bisect on log f against |gain_of_f(0)| / sqrt(2).
    return 0.0


if __name__ == "__main__":
    p = dict(gm=1.728e-3, ro=78125.0, Rs=50e3, RL=100e3,
             Cgs=57.3e-15, Cgd=6.0e-15, CL=5.0e-15)
    cs = lambda f: cs_gain(f, **p)
    ca = lambda f: cascode_gain(f, **p)
    print("CS      gain", round(cs(0.0).real, 3), " bw", round(bandwidth(cs) / 1e6, 3), "MHz")
    print("cascode gain", round(ca(0.0).real, 3), " bw", round(bandwidth(ca) / 1e6, 3), "MHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def miller_input_cap(Cgs, Cgd, A1):
    """Total gate capacitance when the bridging cap sees a gain magnitude A1."""
    return Cgs + Cgd * (1.0 + A1)


def cs_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the common-source stage, as a complex number."""
    s = 2j * np.pi * f
    Y = np.array([
        [1.0 / Rs + s * (Cgs + Cgd), -s * Cgd],
        [gm - s * Cgd, 1.0 / RL + 1.0 / ro + s * (Cgd + CL)],
    ], dtype=complex)
    rhs = np.array([1.0 / Rs, 0.0], dtype=complex)
    return complex(np.linalg.solve(Y, rhs)[1])


def cascode_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the cascode stage, as a complex number."""
    s = 2j * np.pi * f
    Y = np.array([
        [1.0 / Rs + s * (Cgs + Cgd), -s * Cgd, 0.0],
        [gm - s * Cgd, s * (Cgd + Cgs) + 2.0 / ro + gm, -1.0 / ro],
        [0.0, -gm - 1.0 / ro, 1.0 / RL + 1.0 / ro + s * (Cgd + CL)],
    ], dtype=complex)
    rhs = np.array([1.0 / Rs, 0.0, 0.0], dtype=complex)
    return complex(np.linalg.solve(Y, rhs)[2])


def bandwidth(gain_of_f, lo=1.0, hi=1e13):
    """-3 dB frequency of any function that maps frequency to a complex gain."""
    target = abs(gain_of_f(0.0)) / np.sqrt(2.0)
    for _ in range(120):
        mid = np.sqrt(lo * hi)
        if abs(gain_of_f(mid)) > target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


if __name__ == "__main__":
    p = dict(gm=1.728e-3, ro=78125.0, Rs=50e3, RL=100e3,
             Cgs=57.3e-15, Cgd=6.0e-15, CL=5.0e-15)
    cs = lambda f: cs_gain(f, **p)
    ca = lambda f: cascode_gain(f, **p)
    print("CS      gain", round(cs(0.0).real, 3), " bw", round(bandwidth(cs) / 1e6, 3), "MHz")
    print("cascode gain", round(ca(0.0).real, 3), " bw", round(bandwidth(ca) / 1e6, 3), "MHz")
'''}],
                "hints": [
                    "Copy the matrices out of the brief entry by entry before trying to understand them; then check the DC gain of the common-source stage against $-g_m(R_L \\parallel r_o)$, which you can do in your head.",
                    "The `-gm - 1/ro` in the bottom row is M2's drain current written as a function of `vx`, because M2's gate-source voltage is $0 - v_x$.",
                    "`bandwidth` must call `gain_of_f(0.0)` first to establish the reference — do not assume a DC gain.",
                ],
                "tests": [
                    {"name": "the common-source DC gain is minus g_m times the parallel load", "code": r'''
_g = cs_gain(0.0, 1.728e-3, 78125.0, 50e3, 100e3, 57.3e-15, 6.0e-15, 5.0e-15)
assert abs(_g.real + 75.78947368421053) < 1e-6, \
    f"-g_m*(RL||ro) = -1.728e-3*43.86k = -75.789, got {_g.real:.5f}"
assert abs(_g.imag) < 1e-9, "at DC the answer must be purely real"
'''},
                    {"name": "the cascode gains voltage gain from the boosted output resistance", "code": r'''
_a = cs_gain(0.0, 1.728e-3, 78125.0, 50e3, 100e3, 57.3e-15, 6.0e-15, 5.0e-15).real
_b = cascode_gain(0.0, 1.728e-3, 78125.0, 50e3, 100e3, 57.3e-15, 6.0e-15, 5.0e-15).real
assert abs(_b + 169.95082441423202) < 1e-5, \
    f"expected a cascode DC gain of -169.951, got {_b:.5f}"
assert _b / _a > 2.0, \
    f"R_out rises to about g_m*ro*ro so the 100k load now dominates: expected more than twice the gain, got {_b/_a:.3f}"
'''},
                    {"name": "the reported bandwidth really is the -3 dB point", "code": r'''
import numpy as np
_p = dict(gm=1.728e-3, ro=78125.0, Rs=50e3, RL=100e3, Cgs=57.3e-15, Cgd=6.0e-15, CL=5.0e-15)
_fn = lambda f: cs_gain(f, **_p)
_f = bandwidth(_fn)
_r = abs(_fn(_f)) / abs(_fn(0.0))
assert abs(_r - 1.0 / np.sqrt(2.0)) < 1e-4, \
    f"the gain at your reported bandwidth is {_r:.5f} of the DC gain, not 0.70711"
'''},
                    {"name": "the common-source stage is Miller limited", "code": r'''
_p = dict(gm=1.728e-3, ro=78125.0, Rs=50e3, RL=100e3, Cgs=57.3e-15, Cgd=6.0e-15, CL=5.0e-15)
_f = bandwidth(lambda f: cs_gain(f, **_p))
assert abs(_f / 6044757.835835356 - 1.0) < 0.03, \
    f"expected about 6.04 MHz, got {_f/1e6:.4f} MHz"
_cin = miller_input_cap(57.3e-15, 6.0e-15, 75.789)
assert abs(_cin - 5.18034e-13) < 1e-17, \
    f"C_in should be about 518 fF, dominated by the Miller term, got {_cin*1e15:.2f} fF"
'''},
                    {"name": "the cascode is six times faster on the same devices", "code": r'''
_p = dict(gm=1.728e-3, ro=78125.0, Rs=50e3, RL=100e3, Cgs=57.3e-15, Cgd=6.0e-15, CL=5.0e-15)
_cs = bandwidth(lambda f: cs_gain(f, **_p))
_ca = bandwidth(lambda f: cascode_gain(f, **_p))
assert abs(_ca / 37755780.5442543 - 1.0) < 0.03, \
    f"expected about 37.76 MHz for the cascode, got {_ca/1e6:.4f} MHz"
assert _ca / _cs > 5.0, \
    f"removing the Miller multiplication should buy roughly a factor of six, got {_ca/_cs:.3f}"
'''},
                    {"name": "the gain-bandwidth product improves too", "code": r'''
_p = dict(gm=1.728e-3, ro=78125.0, Rs=50e3, RL=100e3, Cgs=57.3e-15, Cgd=6.0e-15, CL=5.0e-15)
_gbw_cs = abs(cs_gain(0.0, **_p)) * bandwidth(lambda f: cs_gain(f, **_p))
_gbw_ca = abs(cascode_gain(0.0, **_p)) * bandwidth(lambda f: cascode_gain(f, **_p))
assert _gbw_ca / _gbw_cs > 10.0, \
    f"gain and bandwidth both improved, so the product should rise about fourteenfold, got {_gbw_ca/_gbw_cs:.2f}"
'''},
                    {"name": "the cascode loses when the source is stiff", "code": r'''
_p = dict(gm=1.728e-3, ro=78125.0, Rs=100.0, RL=100e3, Cgs=57.3e-15, Cgd=6.0e-15, CL=5.0e-15)
_cs = bandwidth(lambda f: cs_gain(f, **_p))
_ca = bandwidth(lambda f: cascode_gain(f, **_p))
assert _ca < _cs, \
    f"with a 100 ohm source there is no Miller pole left to remove, and the cascode's boosted output resistance makes the output pole slower instead: expected the cascode to be the narrower of the two, got {_ca/1e6:.1f} MHz against {_cs/1e6:.1f} MHz"
assert abs(_ca / _cs - 0.46441667381083573) < 0.05, \
    f"expected the cascode to come in at about 0.46 of the common-source bandwidth here, got {_ca/_cs:.4f}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Size a cascode stage against a gain and bandwidth specification",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
Everything in one place. A read-only `device.py` supplies the process constants; you
build the small-signal model, both topologies, and a search that picks the cheapest
device that meets a specification.

The device model, all in SI units with `W` and `L` in metres:

```text
lam  = LAMBDA_L * 1e-6 / L          channel-length modulation, worse for short L
gm   = sqrt(2 * MU_COX * (W/L) * I_D)
ro   = 1 / (lam * I_D)
Cgs  = (2/3) * W * L * COX
Cgd  = CGDO * W
```

The circuit is the one from module 4, driven from a source resistance `Rs` and loaded
by `RL` in parallel with `CL`.

## Suggested order

Build `small_signal` first and check it against the numbers in the checks; nothing
downstream can be right until it is. Then `ft`. Then the two gain functions — verify
each at DC before touching frequency. Then `bandwidth`. `size_for_spec` is a loop over
candidates once the rest works.

## The search

`size_for_spec(candidates, L, Rs, RL, CL, min_gain, min_bw)` receives a list of
`(I_D, W)` pairs. Return the pair that meets **both** the DC cascode gain magnitude
and the cascode bandwidth requirements while drawing the least current — breaking a
tie on current by the smaller width — or `None` if no candidate qualifies. The point
of returning the smallest current is that this is a power budget, and the trade is
real: a wider device raises `gm` and therefore the gain, but raises `Cgs` too and
therefore costs bandwidth.
''',
        "deliverables": [
            "`small_signal(I_D, W, L)` returning a dict with keys `gm`, `ro`, `Cgs`, `Cgd`, matching the model in the brief exactly.",
            "`ft(I_D, W, L)` returning the transit frequency in hertz from those parameters.",
            "`cs_gain` and `cascode_gain`, both exact nodal solutions returning a `complex`, correct at DC and at frequency.",
            "`bandwidth(gain_of_f)` returning the -3 dB frequency of any complex gain function, found numerically rather than from a formula.",
            "`size_for_spec` returning the lowest-current `(I_D, W)` pair meeting a simultaneous gain and bandwidth specification, or `None`.",
            "A comment at the top of `main.py` naming the winning candidate and saying which of the two constraints was the binding one.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, no circuit simulator, no symbolic solver.",
            "The gain functions must solve the nodal system; a hard-coded transfer function that happens to match at DC will fail the frequency checks.",
            "`bandwidth` must locate the -3 dB point numerically from the gain function it is handed, so it works on both topologies without being told which is which.",
            "`size_for_spec` must evaluate every candidate; do not assume the ordering of the list you are given.",
            "Keep all quantities in SI units. Widths and lengths arrive in metres, currents in amperes, capacitances in farads.",
        ],
        "rubric": [
            {"criterion": "Small-signal model", "weight": 20,
             "evidence": "small_signal reproduces gm, ro, Cgs and Cgd to better than a part in a thousand at two different operating points, and the scaling with current and width is correct."},
            {"criterion": "Transit frequency", "weight": 15,
             "evidence": "ft matches gm divided by two pi times the total gate capacitance, and rises as the square root of bias current at fixed geometry."},
            {"criterion": "Exact frequency response", "weight": 30,
             "evidence": "Both gain functions give the correct DC values and the correct complex value at a frequency near the corner, for the common-source and the cascode topology."},
            {"criterion": "Bandwidth extraction", "weight": 20,
             "evidence": "bandwidth returns a frequency at which the gain magnitude is one over root two of its DC value, for either topology, without being told the topology."},
            {"criterion": "Specification search", "weight": 15,
             "evidence": "size_for_spec returns the lowest-current qualifying candidate for a satisfiable specification and None for an unsatisfiable one."},
        ],
        "hints": [
            "`small_signal` returning a dict means every downstream function can take `**dev` or index the keys; pick one and stay with it.",
            "Check `cs_gain` at DC against $-g_m(R_L \\parallel r_o)$ by hand before believing anything at frequency — one wrong sign in the matrix is invisible until then.",
            "`bandwidth` should bisect on the geometric mean of the bracket; the answers here span from a few megahertz to hundreds.",
            "For `size_for_spec`, build the qualifying list first, then `min` it on `(I_D, W)` as a tuple — that gives the tie-break for free.",
        ],
        "files": [
            {"name": "device.py", "ro": True, "content": r'''
"""Process constants. Do not edit — the checks depend on these numbers."""

MU_COX = 200e-6     # A/V^2   mobility times oxide capacitance per unit area
COX = 8.6e-3        # F/m^2   oxide capacitance per unit area
CGDO = 0.30e-9      # F/m     gate-drain overlap capacitance per unit width
LAMBDA_L = 0.04     # 1/V     channel-length modulation at L = 1 um


def lam(L):
    """Channel-length modulation coefficient for a device of length L metres."""
    return LAMBDA_L * 1e-6 / L
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from device import MU_COX, COX, CGDO, lam

# Winning candidate: TODO
# Binding constraint:  TODO


def small_signal(I_D, W, L):
    """Return {'gm', 'ro', 'Cgs', 'Cgd'} for a device at this bias and geometry."""
    # TODO: the five lines in the brief.
    return {"gm": 0.0, "ro": 0.0, "Cgs": 0.0, "Cgd": 0.0}


def ft(I_D, W, L):
    """Transit frequency in hertz."""
    # TODO: gm / (2*pi*(Cgs + Cgd))
    return 0.0


def cs_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the common-source stage, as a complex number."""
    s = 2j * np.pi * f
    # TODO
    return 0j


def cascode_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the cascode stage, as a complex number."""
    s = 2j * np.pi * f
    # TODO
    return 0j


def bandwidth(gain_of_f, lo=1.0, hi=1e13):
    """-3 dB frequency of any function mapping frequency to a complex gain."""
    # TODO
    return 0.0


def size_for_spec(candidates, L, Rs, RL, CL, min_gain, min_bw):
    """Lowest-current (I_D, W) meeting both constraints in a cascode, else None."""
    # TODO
    return None


if __name__ == "__main__":
    dev = small_signal(200e-6, 20e-6, 0.5e-6)
    print("device:", {k: float(f"{v:.6g}") for k, v in dev.items()})
    print("f_T   :", round(ft(200e-6, 20e-6, 0.5e-6) / 1e9, 4), "GHz")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from device import MU_COX, COX, CGDO, lam

# Winning candidate: I_D = 200 uA, W = 20 um at L = 0.5 um.
# Binding constraint:  gain. Every cheaper candidate that met the 30 MHz bandwidth
# fell short of a gain of 150; the 40 um devices clear the gain easily but their
# C_gs drags the bandwidth down to about 20 MHz.


def small_signal(I_D, W, L):
    """Return {'gm', 'ro', 'Cgs', 'Cgd'} for a device at this bias and geometry."""
    return {
        "gm": float(np.sqrt(2.0 * MU_COX * (W / L) * I_D)),
        "ro": float(1.0 / (lam(L) * I_D)),
        "Cgs": float((2.0 / 3.0) * W * L * COX),
        "Cgd": float(CGDO * W),
    }


def ft(I_D, W, L):
    """Transit frequency in hertz."""
    d = small_signal(I_D, W, L)
    return d["gm"] / (2.0 * np.pi * (d["Cgs"] + d["Cgd"]))


def cs_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the common-source stage, as a complex number."""
    s = 2j * np.pi * f
    Y = np.array([
        [1.0 / Rs + s * (Cgs + Cgd), -s * Cgd],
        [gm - s * Cgd, 1.0 / RL + 1.0 / ro + s * (Cgd + CL)],
    ], dtype=complex)
    rhs = np.array([1.0 / Rs, 0.0], dtype=complex)
    return complex(np.linalg.solve(Y, rhs)[1])


def cascode_gain(f, gm, ro, Rs, RL, Cgs, Cgd, CL):
    """Exact v2/vs of the cascode stage, as a complex number."""
    s = 2j * np.pi * f
    Y = np.array([
        [1.0 / Rs + s * (Cgs + Cgd), -s * Cgd, 0.0],
        [gm - s * Cgd, s * (Cgd + Cgs) + 2.0 / ro + gm, -1.0 / ro],
        [0.0, -gm - 1.0 / ro, 1.0 / RL + 1.0 / ro + s * (Cgd + CL)],
    ], dtype=complex)
    rhs = np.array([1.0 / Rs, 0.0, 0.0], dtype=complex)
    return complex(np.linalg.solve(Y, rhs)[2])


def bandwidth(gain_of_f, lo=1.0, hi=1e13):
    """-3 dB frequency of any function mapping frequency to a complex gain."""
    target = abs(gain_of_f(0.0)) / np.sqrt(2.0)
    for _ in range(120):
        mid = np.sqrt(lo * hi)
        if abs(gain_of_f(mid)) > target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


def size_for_spec(candidates, L, Rs, RL, CL, min_gain, min_bw):
    """Lowest-current (I_D, W) meeting both constraints in a cascode, else None."""
    good = []
    for I_D, W in candidates:
        d = small_signal(I_D, W, L)
        fn = (lambda f, d=d: cascode_gain(f, d["gm"], d["ro"], Rs, RL,
                                          d["Cgs"], d["Cgd"], CL))
        if abs(fn(0.0)) < min_gain:
            continue
        if bandwidth(fn) < min_bw:
            continue
        good.append((I_D, W))
    if not good:
        return None
    return min(good)


if __name__ == "__main__":
    dev = small_signal(200e-6, 20e-6, 0.5e-6)
    print("device:", {k: float(f"{v:.6g}") for k, v in dev.items()})
    print("f_T   :", round(ft(200e-6, 20e-6, 0.5e-6) / 1e9, 4), "GHz")
    cands = [(i * 1e-6, w * 1e-6) for i in (50, 100, 200, 400) for w in (10, 20, 40)]
    print("choice:", size_for_spec(cands, 0.5e-6, 50e3, 100e3, 5e-15, 150.0, 30e6))
'''},
        ],
        "tests": [
            {"name": "the small-signal parameters match the model", "code": r'''
_d = small_signal(172.8e-6, 20e-6, 0.5e-6)
assert abs(_d["gm"] - 1.6627687752661224e-3) < 1e-9, \
    f"sqrt(2*200e-6*40*172.8e-6) is 1.6628 mS, got {_d['gm']*1e3:.4f} mS"
assert abs(_d["ro"] - 72337.96296296296) < 1e-3, \
    f"lam(0.5 um) is 0.08, so ro = 1/(0.08*172.8uA) = 72.338 kohm, got {_d['ro']/1e3:.3f} kohm"
assert abs(_d["Cgs"] - 5.733333333333333e-14) < 1e-19, \
    f"(2/3)*20u*0.5u*8.6m is 57.33 fF, got {_d['Cgs']*1e15:.3f} fF"
assert abs(_d["Cgd"] - 6.0e-15) < 1e-20, \
    f"CGDO*W is 6 fF, got {_d['Cgd']*1e15:.3f} fF"
'''},
            {"name": "the parameters scale the way the physics says", "code": r'''
_a = small_signal(100e-6, 20e-6, 0.5e-6)
_b = small_signal(400e-6, 20e-6, 0.5e-6)
assert abs(_b["gm"] / _a["gm"] - 2.0) < 1e-9, \
    f"four times the current is twice the g_m, got a ratio of {_b['gm']/_a['gm']:.4f}"
assert abs(_b["ro"] / _a["ro"] - 0.25) < 1e-9, \
    "r_o falls as 1/I_D, so four times the current quarters it"
_c = small_signal(100e-6, 40e-6, 0.5e-6)
assert abs(_c["Cgs"] / _a["Cgs"] - 2.0) < 1e-9, \
    "C_gs is proportional to the gate area, so doubling W doubles it"
assert abs(_a["gm"] * _a["ro"] - 158.11388300841895) < 1e-5, \
    f"g_m*r_o at 100 uA is 158.114, got {_a['gm']*_a['ro']:.5f}"
assert abs(_a["gm"] * _a["ro"] / (_b["gm"] * _b["ro"]) - 2.0) < 1e-6, \
    "intrinsic gain falls as 1/sqrt(I_D) in this model, so four times the current halves it"
'''},
            {"name": "the transit frequency follows g_m over total gate capacitance", "code": r'''
import numpy as np
_f = ft(172.8e-6, 20e-6, 0.5e-6)
assert abs(_f - 4178492681.091477) < 1e5, \
    f"expected 4.1785 GHz, got {_f/1e9:.4f} GHz"
_a = ft(100e-6, 20e-6, 0.5e-6)
_b = ft(400e-6, 20e-6, 0.5e-6)
assert abs(_b / _a - 2.0) < 1e-6, \
    f"at fixed geometry only g_m moves, so f_T should follow sqrt(I_D), got a ratio of {_b/_a:.4f}"
'''},
            {"name": "both topologies are right at DC", "code": r'''
_d = small_signal(172.8e-6, 20e-6, 0.5e-6)
_args = (_d["gm"], _d["ro"], 50e3, 100e3, _d["Cgs"], _d["Cgd"], 5e-15)
_cs = cs_gain(0.0, *_args)
_ca = cascode_gain(0.0, *_args)
assert abs(_cs.real + 69.79385389800714) < 1e-5, \
    f"-g_m*(RL||ro) is -69.794 here, got {_cs.real:.5f}"
assert abs(_ca.real + 163.0735283340902) < 1e-4, \
    f"the cascode should reach -163.074, got {_ca.real:.5f}"
assert abs(_cs.imag) < 1e-9 and abs(_ca.imag) < 1e-9, \
    "at DC the admittance matrix is real, so the gain cannot have an imaginary part"
'''},
            {"name": "the gain functions are right off DC as well", "code": r'''
_d = small_signal(172.8e-6, 20e-6, 0.5e-6)
_args = (_d["gm"], _d["ro"], 50e3, 100e3, _d["Cgs"], _d["Cgd"], 5e-15)
_g = cs_gain(6.4934e6, *_args)
assert abs(abs(_g) / abs(cs_gain(0.0, *_args)) - 0.70711) < 2e-3, \
    f"6.4934 MHz is the common-source corner, so the magnitude there should be 0.707 of DC, got {abs(_g)/abs(cs_gain(0.0,*_args)):.5f}"
assert _g.imag != 0.0, \
    "away from DC the response is complex — you are ignoring s somewhere in the matrix"
'''},
            {"name": "bandwidth finds the -3 dB point of whatever it is given", "code": r'''
import numpy as np
_d = small_signal(172.8e-6, 20e-6, 0.5e-6)
_args = (_d["gm"], _d["ro"], 50e3, 100e3, _d["Cgs"], _d["Cgd"], 5e-15)
for _name, _fn in (("common-source", lambda f: cs_gain(f, *_args)),
                   ("cascode", lambda f: cascode_gain(f, *_args))):
    _f = bandwidth(_fn)
    _r = abs(_fn(_f)) / abs(_fn(0.0))
    assert abs(_r - 1.0 / np.sqrt(2.0)) < 1e-4, \
        f"{_name}: the gain at your reported bandwidth is {_r:.5f} of DC, not 0.70711"
'''},
            {"name": "the cascode is much faster on the same device", "code": r'''
_d = small_signal(172.8e-6, 20e-6, 0.5e-6)
_args = (_d["gm"], _d["ro"], 50e3, 100e3, _d["Cgs"], _d["Cgd"], 5e-15)
_cs = bandwidth(lambda f: cs_gain(f, *_args))
_ca = bandwidth(lambda f: cascode_gain(f, *_args))
assert abs(_cs / 6493442.969612937 - 1.0) < 0.03, \
    f"expected about 6.49 MHz for the common-source stage, got {_cs/1e6:.4f} MHz"
assert abs(_ca / 37445813.456821695 - 1.0) < 0.03, \
    f"expected about 37.45 MHz for the cascode, got {_ca/1e6:.4f} MHz"
assert _ca / _cs > 5.0, \
    f"with a 50 kohm source the Miller pole dominates, so the cascode should win by about six, got {_ca/_cs:.3f}"
'''},
            {"name": "the search picks the cheapest device that qualifies", "code": r'''
_c = [(i * 1e-6, w * 1e-6) for i in (50, 100, 200, 400) for w in (10, 20, 40)]
_pick = size_for_spec(_c, 0.5e-6, 50e3, 100e3, 5e-15, 150.0, 30e6)
assert _pick is not None, "a gain of 150 with 30 MHz is satisfiable — 200 uA at 20 um does it"
assert abs(_pick[0] - 200e-6) < 1e-12 and abs(_pick[1] - 20e-6) < 1e-12, \
    f"expected (200 uA, 20 um): the 40 um devices have too much C_gs and the 10 um ones too little g_m, got {_pick}"
'''},
            {"name": "an unsatisfiable specification returns nothing", "code": r'''
_c = [(i * 1e-6, w * 1e-6) for i in (50, 100, 200, 400) for w in (10, 20, 40)]
assert size_for_spec(_c, 0.5e-6, 50e3, 100e3, 5e-15, 400.0, 60e6) is None, \
    "no candidate reaches a gain of 400 and 60 MHz at once — the trade forbids it, so return None rather than the least bad option"
_easy = size_for_spec(_c, 0.5e-6, 50e3, 100e3, 5e-15, 50.0, 10e6)
assert _easy is not None and abs(_easy[0] - 50e-6) < 1e-12 and abs(_easy[1] - 10e-6) < 1e-12, \
    f"with a loose specification the cheapest candidate in the list should win, got {_easy}"
'''},
        ],
    },
}
