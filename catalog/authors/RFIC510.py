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
            "read": [
                {
                    "title": "Every parameter in the model is a slope you can measure",
                    "minutes": 14,
                    "body": r'''
A test chip, one NMOS transistor, $20\ \mu\text{m}$ wide and $0.5\ \mu\text{m}$ long. The
gate sits $200$ mV above threshold, the drain at $1.0$ V, and the ammeter in the drain
lead reads $172.8\ \mu\text{A}$. Nothing on the bench is moving. That single reading is
the operating point, and on its own it says almost nothing about what this device will
do to a signal.

So move something. Raise the gate by 10 mV and read the ammeter again; then do it
properly, with 5 mV either side of the bias.

```python
MU_COX, LAMBDA, W_OVER_L = 200e-6, 0.08, 40.0


def drain_current(V_ov, V_DS=1.0):
    return 0.5 * MU_COX * W_OVER_L * V_ov ** 2 * (1.0 + LAMBDA * V_DS)


I0 = drain_current(0.200)
forward = (drain_current(0.210) - I0) / 0.010
central = (drain_current(0.205) - drain_current(0.195)) / 0.010
print(f"I_D at a 200 mV overdrive : {I0 * 1e6:.3f} uA")
print(f"forward slope over +10 mV : {forward * 1e3:.4f} mS")
print(f"central slope over +-5 mV : {central * 1e3:.4f} mS")
print(f"k_n V_ov (1 + lambda V_DS): {MU_COX * W_OVER_L * 0.200 * 1.08 * 1e3:.4f} mS")
```

The two measured slopes are $1.7712$ mS and $1.7280$ mS. They disagree in the third
digit, and that disagreement is the whole of this module.

## Where the disagreement comes from

Write $k_n = \mu C_{ox}(W/L)$, so $I_D = \tfrac{1}{2}k_n V_{ov}^2(1 + \lambda V_{DS})$,
and take the difference over a step $\Delta$ in the overdrive:

$$I_D(V_{ov} + \Delta) - I_D(V_{ov}) = \tfrac{1}{2}k_n(1 + \lambda V_{DS})
\left[2V_{ov}\Delta + \Delta^2\right]$$

Divide by $\Delta$ and the measured ratio is
$k_n(1 + \lambda V_{DS})\left(V_{ov} + \Delta/2\right)$. It depends on how hard you
pushed. Push by $+10$ mV from a $200$ mV overdrive and the answer comes out
$\Delta/(2V_{ov}) = 2.5\%$ high, which is exactly the $1.7712$ against $1.7280$ above.

Two things follow. The first is the definition: the number that does not depend on
$\Delta$ is the limit, $g_m = k_n V_{ov}(1 + \lambda V_{DS}) = 1.728$ mS, and every
parameter in the hybrid-pi model is a limit of this kind — a partial derivative of the
device equation evaluated at one bias point, which is what a first-order Taylor
expansion is made of. The second is a measurement technique: the error term
$k_n(1+\lambda V_{DS})\Delta/2$ is odd in $\Delta$, so averaging a step up with a step
down cancels it, and for a quadratic it cancels it exactly. That is why the central
difference above returns $1.7280$ mS to every digit shown, and it is why this module's
lab, *Small-signal parameters from the bias point*, checks your analytic `gm` against a
central difference of your own `drain_current` and demands agreement to better than a
part in a million. A dropped $(1 + \lambda V_{DS})$ factor cannot hide from that test.

## How small "small signal" has to be

The same second-order term sets the honest limit on the model. Put a cosine of
amplitude $a$ on top of the overdrive and expand:

$$\left(V_{ov} + a\cos\omega t\right)^2 = V_{ov}^2 + \frac{a^2}{2}
+ 2V_{ov}a\cos\omega t + \frac{a^2}{2}\cos 2\omega t$$

The third term is the signal the model predicts, with amplitude $g_m a$. The fourth is
a second harmonic the model does not contain at all, and the ratio of the two is
$a/(4V_{ov})$. On a $200$ mV overdrive, a $20$ mV amplitude gives $2.5\%$ second
harmonic, about $-32$ dBc. "Small" is therefore not a number of millivolts; it is a
fraction of the overdrive, and a device biased at $100$ mV of overdrive to buy
efficiency is twice as easy to distort as this one.

## Three ways to write the same slope

A bias circuit sets a current, not an overdrive, so $g_m$ gets rewritten to suit
whichever quantity you actually know. Eliminating $k_n$ between $g_m$ and $I_D$ gives
$2I_D/V_{ov}$; eliminating $V_{ov}$ instead gives $\sqrt{2k_nI_D}$. They are the same
slope, and on the bench they do not quite agree.

```python
MU_COX, LAMBDA, W_OVER_L = 200e-6, 0.08, 40.0
V_ov, V_DS = 0.200, 1.0

I_D = 0.5 * MU_COX * W_OVER_L * V_ov ** 2 * (1.0 + LAMBDA * V_DS)
g_m = MU_COX * W_OVER_L * V_ov * (1.0 + LAMBDA * V_DS)
r_o = 1.0 / (LAMBDA * 0.5 * MU_COX * W_OVER_L * V_ov ** 2)

print(f"g_m as 2 I_D / V_ov      : {2 * I_D / V_ov * 1e3:.4f} mS")
print(f"g_m as sqrt(2 k_n I_D)   : {(2 * MU_COX * W_OVER_L * I_D) ** 0.5 * 1e3:.4f} mS")
print(f"r_o from the V_DS slope  : {r_o / 1e3:.3f} kohm")
print(f"r_o as 1 / (lambda I_D)  : {1.0 / (LAMBDA * I_D) / 1e3:.3f} kohm")
print(f"g_m r_o                  : {g_m * r_o:.1f}")
print(f"2 / (lambda V_ov)        : {2.0 / (LAMBDA * V_ov):.1f}")
print(f"g_m / I_D                : {g_m / I_D:.2f} 1/V")
```

$2I_D/V_{ov}$ returns $1.7280$ mS, agreeing to every digit, because the channel-length
modulation factor sits in $I_D$ and in $g_m$ alike and cancels in the ratio.
$\sqrt{2k_nI_D}$ returns $1.6628$ mS, low by $3.9\%$, because that route recovers
$V_{ov}$ from a current that carries the factor while $g_m = k_nV_{ov}$ leaves it
outside: the discrepancy is $\sqrt{1.08} = 1.039$ and nothing else. The lab's check on
`gm_from_current` allows the two forms six per cent of daylight for that reason, and
the tolerance is a statement about the model rather than about your arithmetic.

## The other axis of the same surface

$r_o$ is the same exercise along $V_{DS}$. Only the bracket depends on drain voltage,
so $\partial I_D/\partial V_{DS} = \tfrac{1}{2}k_nV_{ov}^2\lambda$, which is
$0.08 \times 160\ \mu\text{A} = 12.8\ \mu\text{S}$, and $r_o = 78.125$ k$\Omega$.
Notice which current appears there: $160\ \mu\text{A}$, the current with the
$(1+\lambda V_{DS})$ factor stripped off, not the $172.8\ \mu\text{A}$ the ammeter
reads. Feed the measured current into the remembered form $1/(\lambda I_D)$ and you
get $72.338$ k$\Omega$, eight per cent low.

Both numbers live in this course, and it is worth knowing why. Exactly,
$\partial I_D/\partial V_{DS} = \lambda I_D/(1+\lambda V_{DS})$, so
$r_o = (1+\lambda V_{DS})/(\lambda I_D)$. The module lab takes that derivative and gets
$78.125$ k$\Omega$; the capstone's `device.py` defines $r_o = 1/(\lambda I_D)$ from the
specified bias current and gets $72.338$ k$\Omega$. The second is the first with
$\lambda V_{DS} \ll 1$ assumed, and at $V_{DS} = 1$ V with $\lambda = 0.08$ that
assumption is worth $8\%$. Note also what the exact derivative does *not* contain:
$V_{DS}$ has vanished from it, so in this model $r_o$ is flat with drain voltage, which
is what the lab's fourth test insists on.

## What the two slopes buy together

Multiply them. $g_mr_o = 1.728\ \text{mS} \times 78.125\ \text{k}\Omega = 135.0$, and
the current has disappeared from the product: $g_m$ climbs as $\sqrt{I_D}$ while $r_o$
falls as $1/I_D$. Algebraically the product is $2(1+\lambda V_{DS})/(\lambda V_{ov})$,
which is the familiar $2/(\lambda V_{ov}) = 125$ carrying the same $8\%$ correction as
before. The intrinsic gain is fixed by the overdrive and by the channel length through
$\lambda \propto 1/L$, and by nothing else — which the lab checks by quadrupling $W/L$
and requiring the gain not to move, even though the current and $g_m$ both quadrupled
and $r_o$ quartered.

The last line of that block, $g_m/I_D = 10\ \text{V}^{-1}$, is the same fact stated as
a budget. It equals $2/V_{ov}$ exactly, so it is bought by lowering the overdrive, and
module 3 will show that $f_T \propto V_{ov}$ — every volt of overdrive you give back to
buy transconductance per amp is taken out of speed.

## The mistake, and why it is tempting

The first is writing $g_m = I_D/V_{GS}$. With $V_{TH} = 0.5$ V the gate sits at
$0.7$ V, and that ratio gives $247\ \mu\text{S}$, seven times too small. It is tempting
because a DC operating point is what a datasheet hands you and dividing is what one
does to DC data, but $V_{GS}$ contains the threshold voltage, which carries no signal
and produces no gain. The device responds to changes, and only the slope survives.

The second is believing that more current buys gain. It buys $g_m$, and every stage
that has to drive a capacitor wants $g_m$. But at fixed geometry a larger current is a
larger overdrive, so $g_m$ rises as $\sqrt{I_D}$ while $r_o$ falls as $1/I_D$: take
this device from $172.8\ \mu\text{A}$ to $691.2\ \mu\text{A}$ and the overdrive doubles
to $0.4$ V, so the intrinsic gain halves to $67.5$. Four times the power, half the
gain. Gain from a single device is bought with geometry, and that is the fact the
cascode of module 4 exists to work around.

## Where the model stops holding

The square law is a long-channel approximation and it fails from both ends. Push the
overdrive up on a short device and the carriers reach their saturation velocity: $I_D$
turns linear in $V_{ov}$, $g_m$ flattens out near $WC_{ox}v_{sat}$, and the promised
$\sqrt{I_D}$ growth stops arriving. Pull the overdrive down toward zero and the device
slides into weak inversion, where the current is exponential rather than quadratic and
$g_m/I_D$ tops out around $25$ to $30\ \text{V}^{-1}$ at room temperature — while
$2/V_{ov}$ predicts it growing without bound. $\lambda$ is not a constant either; it
varies with $V_{DS}$ and with length, and quoting it to two digits is optimistic.

None of that spoils the exercise, because the model is doing a different job: it turns
a curved surface into a slope you can compute with, and every number in the next three
modules is that slope divided by a capacitance. The sandbox for this module, *Gain,
corner frequency, and the fact that they are not yet linked*, gives you a gain slider
and a corner slider that move independently. That independence is a fiction. Module 2
removes it with a single $6$ fF capacitor.
''',
                },
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
                        "hint": "Divide the current equation by the transconductance equation and see what survives.",
                        "deconstruct": [
                            "From the current equation, $k_n = 2I_D/V_{ov}^2$.",
                            "Substitute that into $g_m = k_n V_{ov}$ and one power of $V_{ov}$ cancels.",
                        ],
                    },
                    {
                        "prompt": "Now eliminate $V_{ov}$ instead, and write $g_m$ in terms of $k_n$ and $I_D$.",
                        "answer": "\\sqrt{2 k_n I_D}",
                        "hint": "Solve the current equation for $V_{ov}$ first, then substitute into $g_m = k_n V_{ov}$.",
                        "deconstruct": [
                            "$V_{ov} = \\sqrt{2 I_D / k_n}$.",
                            "$g_m = k_n \\sqrt{2 I_D/k_n} = \\sqrt{2 k_n I_D}$ — transconductance grows only as the square root of current.",
                        ],
                    },
                    {
                        "prompt": "Put $\\lambda$ back. The output resistance is $r_o = \\left(\\partial I_D/\\partial V_{DS}\\right)^{-1}$. Differentiate, then write $r_o$ in terms of $\\lambda$ and $I_D$, treating $\\lambda V_{DS} \\ll 1$ so that the current at the bias point is $I_D$.",
                        "answer": "\\frac{1}{\\lambda I_D}",
                        "hint": "Only the bracket depends on $V_{DS}$, and its derivative is just $\\lambda$.",
                        "deconstruct": [
                            "$\\partial I_D/\\partial V_{DS} = \\tfrac{1}{2}k_n V_{ov}^2 \\lambda$, and $\\tfrac{1}{2}k_n V_{ov}^2$ is the current itself.",
                            "So the conductance is $\\lambda I_D$ and the resistance is its reciprocal.",
                        ],
                    },
                    {
                        "prompt": "The intrinsic gain is $A_0 = g_m r_o$. Combine the second and fourth results and write $A_0$ in terms of $\\lambda$ and $V_{ov}$ only.",
                        "answer": "\\frac{2}{\\lambda V_{ov}}",
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
            "quiz": {
                "title": "Every parameter in the model is a slope",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What is $g_m$, precisely?",
                        "opts": [
                            "$\\partial I_D/\\partial V_{GS}$ at the operating point",
                            "$I_D/V_{GS}$ at the operating point",
                            "$\\partial I_D/\\partial V_{DS}$",
                            "The reciprocal of the channel resistance",
                        ],
                        "a": 0,
                        "why": r"""
A derivative, not a ratio. $I_D/V_{GS}$ would include the threshold voltage, which
carries no signal and contributes no gain — the device responds to *changes* about the
bias point, and the slope there is the only thing the small-signal model keeps.
$\partial I_D/\partial V_{DS}$ is the output conductance $1/r_o$, a different slope on
a different axis of the same surface.
""",
                    },
                    {
                        "q": "At a fixed drain current, how do you get more $g_m$ out of a device?",
                        "opts": [
                            "Make it wider, so the same current flows at a smaller overdrive",
                            "Make it narrower",
                            "Raise $V_{DS}$",
                            "You cannot — $g_m = 2I_D/V_{ov}$ depends only on the current",
                        ],
                        "a": 0,
                        "why": r"""
$g_m = \sqrt{2kI_D}$ says it plainly: at fixed current, more $k$ (a wider device) means
more $g_m$. Read the other way, $g_m = 2I_D/V_{ov}$, the wider device reaches the same
current at a lower overdrive, and a lower overdrive at the same current *is* a higher
$g_m$. The two forms are the same statement and neither is a licence to ignore the
device — the third form's $V_{ov}$ is not a free parameter, it is set by the geometry
you chose.
""",
                    },
                    {
                        "q": "In the standard model, what is $r_o$?",
                        "opts": ["$1/(\\lambda I_D)$", "$\\lambda I_D$", "$V_{ov}/I_D$", "$1/g_m$"],
                        "a": 0,
                        "why": r"""
Channel-length modulation makes $I_D$ creep up with $V_{DS}$ by a factor
$(1 + \lambda V_{DS})$, and the slope of that is $\lambda I_D$ — so the resistance is its
reciprocal. Note the consequence: $r_o$ *falls* as you bias harder, which is why current
and gain pull against each other. $1/g_m$ is the resistance looking into a source, an
entirely different port.
""",
                    },
                    {
                        "q": "The intrinsic gain $g_mr_o$ works out to $2/(\\lambda V_{ov})$. What does that tell you?",
                        "opts": [
                            "It does not depend on the drain current at all",
                            "It rises with current",
                            "It falls as the square of the current",
                            "It depends only on the width",
                        ],
                        "a": 0,
                        "why": r"""
The current cancels: $g_m$ rises as $\sqrt{I_D}$ and $r_o$ falls as $1/I_D$, so the
product depends only on the overdrive and on $\lambda$ — which is to say on the *channel
length*, since $\lambda \propto 1/L$. This is the most useful single fact in analog
design on a given process: you cannot buy gain from a single device with current, only
with geometry, and that is why the cascode in module 4 exists.
""",
                    },
                    {
                        "q": "What is small-signal analysis, mathematically?",
                        "opts": [
                            "A first-order Taylor expansion of the device equations about the bias point",
                            "An exact solution restricted to small currents",
                            "An averaging of the device equations over a cycle",
                            "A change of units",
                        ],
                        "a": 0,
                        "why": r"""
Every parameter in the hybrid-pi model is a partial derivative evaluated at one point,
which is exactly what a first-order Taylor expansion is. Two consequences follow and
both matter: the model is *linear*, which is what makes superposition and phasors legal;
and it is only valid for excursions small enough that the second-order term stays
negligible, which is what "small-signal" means and where distortion comes from when it
does not.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "Six femtofarads, and where the bandwidth went",
                    "minutes": 15,
                    "body": r'''
Take the device from module 1 — $g_m = 1.728$ mS at $172.8\ \mu\text{A}$ — and make an
amplifier out of it. The gate is driven from the previous stage through
$R_S = 5$ k$\Omega$, the drain has $R_L = 10$ k$\Omega$ to the supply, and the DC gain
measures $-17.28$, which is $g_mR_L$ to three digits.

Now the capacitances. There are two of them and both are on the data sheet:
$C_{gs} = 57.3$ fF from the inversion layer under the gate, and $C_{gd} = 6.0$ fF from
the sliver of gate metal that overlaps the drain diffusion. Add them, put the total on
the gate node, and the input $RC$ gives a corner at
$1/(2\pi \times 5\,\text{k}\Omega \times 63.3\,\text{fF}) = 503$ MHz.

The stage measures $182$ MHz. Nearly two thirds of the bandwidth is missing, and there
is nothing else in the circuit to blame.

## The two ends of a capacitor do not have to agree

Follow the small capacitor. One terminal is the gate; the other is the drain. Wiggle
the gate up by $1$ mV and the drain does not stay where it was — it moves *down* by
$17.28$ mV, because that is what the stage is for. So the voltage across $C_{gd}$
changes by $1 + 17.28 = 18.28$ mV while the gate itself moved $1$ mV.

Current follows voltage across the capacitor, not voltage at one end of it. At
frequency $\omega$ that terminal draws

$$i = j\omega C_{gd}\left(v_{in} - v_{out}\right)
   = j\omega C_{gd}\left(1 + A_v\right)v_{in}$$

with $A_v = g_mR_L$ written as a positive number. Divide by $v_{in}$ and the source
driving the gate cannot tell this apart from a plain capacitor to ground of value
$C_{gd}(1 + A_v)$. Nothing about the component changed. The voltage across it did.

For this stage that is $6.0\ \text{fF} \times 18.28 = 109.7$ fF, from a capacitor
that a data sheet reports as a tenth of $C_{gs}$.

## The number the input node actually sees

$C_{gs}$ has its far end at the source terminal, which is grounded, so it is not
multiplied and contributes its own $57.3$ fF. The gate therefore carries
$C_{in} = C_{gs} + C_{gd}(1 + A_v)$, and the pole is $1/(2\pi R_SC_{in})$.

```python
import math

g_m, R_S, R_L = 1.728e-3, 5e3, 10e3
C_gs, C_gd = 57.3e-15, 6.0e-15
A_v = g_m * R_L


def stage_gain(f):
    """Exact v_out / v_s of the common-source stage, by Cramer's rule."""
    s = 2j * math.pi * f
    a, b = 1.0 / R_S + s * (C_gs + C_gd), -s * C_gd
    c, d = g_m - s * C_gd, 1.0 / R_L + s * C_gd
    return -c * (1.0 / R_S) / (a * d - b * c)


def corner(gain, lo=1e3, hi=1e13):
    """The -3 dB frequency, bisected on log f so no formula is assumed."""
    target = abs(gain(0.0)) / math.sqrt(2.0)
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        lo, hi = (mid, hi) if abs(gain(mid)) > target else (lo, mid)
    return math.sqrt(lo * hi)


C_in = C_gs + C_gd * (1.0 + A_v)
print(f"DC gain                     : {stage_gain(0.0).real:.2f}")
print(f"C_gs + C_gd                 : {(C_gs + C_gd) * 1e15:.2f} fF")
print(f"C_gs + C_gd (1 + A_v)       : {C_in * 1e15:.2f} fF")
print(f"corner from C_gs + C_gd     : {1 / (2 * math.pi * R_S * (C_gs + C_gd)) / 1e6:.1f} MHz")
print(f"corner from the Miller C_in : {1 / (2 * math.pi * R_S * C_in) / 1e6:.1f} MHz")
print(f"corner from the exact solve : {corner(stage_gain) / 1e6:.1f} MHz")
```

$166.98$ fF against the $63.30$ fF of the naive sum, $190.6$ MHz against $502.9$ MHz,
and an exact two-node solution that lands at $181.7$ MHz. The missing two thirds of the
bandwidth is accounted for, by one capacitor and the gain standing behind it.

## Why the estimate is nine megahertz optimistic

The Miller number is $190.6$ MHz and the exact answer is $181.7$ MHz, so the estimate
overstates the bandwidth by $4.9\%$. The reason is worth chasing down, because chasing
it produces a second estimate that is better than either.

Count time constants instead of poles. A capacitor's contribution to the delay of a
circuit is its value times the resistance it charges through with every other capacitor
removed, and those contributions add. $C_{gs}$ charges through $R_S$ alone. $C_{gd}$
charges through $R_S$ *and* $R_L$, with the transistor's own feedback in between, and
working that resistance out gives $R_S + R_L + g_mR_SR_L$ — which is
$R_S(1 + g_mR_L)$, the Miller term, plus a leftover $R_L$ that the Miller estimate never
counted.

```python
import math

R_S, R_L = 5e3, 10e3
C_gs, C_gd = 57.3e-15, 6.0e-15
A_v = 1.728e-3 * R_L

tau_gate = R_S * (C_gs + C_gd * (1.0 + A_v))
tau_drain = R_L * C_gd
print(f"the gate node, as the Miller estimate counts it : {tau_gate * 1e12:6.1f} ps")
print(f"the drain-side term the estimate leaves out     : {tau_drain * 1e12:6.1f} ps")
print(f"the two together                                : {(tau_gate + tau_drain) * 1e12:6.1f} ps")
print(f"1 / 2 pi times that sum                         : "
      f"{1 / (2 * math.pi * (tau_gate + tau_drain)) / 1e6:6.1f} MHz")
```

$834.9$ ps against a term of $60.0$ ps that was thrown away, and the sum puts the corner
at $177.8$ MHz. So the exact answer, $181.7$ MHz, is bracketed: the Miller estimate is
$4.9\%$ high because it left a time constant out, and the sum of time constants is
$2.1\%$ low because the sum equals $\sum 1/\left|p_i\right|$ over *all* the poles, and
charging the second pole's delay against the first understates the dominant one. The
lab, *Miller estimate against an exact nodal solution*, asserts the first half of that
directly: the Miller bandwidth comes out above the exact one, and the two agree within
about ten per cent while the poles remain far apart.

There is a second, softer approximation underneath both. The multiplication assumed
$v_{out} = -A_vv_{in}$ at every frequency, and at the corner the gain has already
dropped, so the far end of $C_{gd}$ swings less than $A_v$ times the near end and the
true multiplied capacitance is under $109.7$ fF. That effect is real and runs the other
way, and it is much the smaller of the two here.

## The bridging capacitor also feeds forward

At DC the transistor pulls current out of the drain node and $C_{gd}$ carries nothing.
At high enough frequency the gate signal leaks straight through $C_{gd}$ into the drain
in the opposite phase, and where $\omega C_{gd}v_{in}$ equals $g_mv_{in}$ the two
cancel and the output is null. That is a zero at $s = +g_m/C_{gd}$, in the *right* half
plane: $1.728\ \text{mS} / (2\pi \times 6\ \text{fF}) = 45.8$ GHz for this device. Ten
times the device's own $f_T$, so it does no harm to the magnitude response here, but it
subtracts phase like a pole while adding gain like a zero, and in a feedback loop that
combination is what eats the phase margin nobody budgeted for. The Miller estimate has
no way to produce it: a lumped capacitance to ground has no path from input to output.

## What the trade actually is

Folklore says gain-bandwidth product is constant, so raising the load resistance buys
gain at exactly the price of bandwidth. Test it. Raise $R_L$ from $10$ k$\Omega$ to
$50$ k$\Omega$: the gain goes from $17.28$ to $86.4$ and the exact bandwidth from
$181.7$ MHz to $50.0$ MHz, so the product goes from $3.14$ GHz to $4.32$ GHz. It
improved by nearly forty per cent.

The reason is in $C_{in}$. Only the $C_{gd}(1+A_v)$ part scales with gain; $C_{gs}$ sits
there unchanged, and at low gain it is most of the capacitance. As $A_v$ grows the
Miller term swamps it and the product approaches
$A_v/(2\pi R_SC_{gd}(1+A_v)) \to 1/(2\pi R_SC_{gd}) = 5.31$ GHz. So the invariant is
real, it is a *ceiling* rather than a constant, and it is set by the source resistance
and the overlap capacitance — two things that have nothing to do with the load
resistor you were reaching for.

## The mistake, and why it is tempting

The mistake is adding the capacitances: $57.3 + 6.0 = 63.3$ fF, corner at $503$ MHz,
a stage that measures $182$ MHz. It is tempting for three separate reasons, and they
reinforce each other. Every other capacitance in the circuit does add that way.
$6$ fF next to $57$ fF looks like a rounding error, so the instinct is to neglect it
rather than to multiply it. And the number a data sheet gives you for the input, $C_{iss}$,
really is $C_{gs} + C_{gd}$ — measured with the drain held at AC ground, which is the
one condition under which the multiplication does not happen and is never the condition
your amplifier operates under.

The companion mistake is trying to fix it by shrinking the device. Halving $W$ halves
$C_{gs}$ and $C_{gd}$ together, but at fixed current it also cuts $g_m$ by $\sqrt{2}$,
so the gain falls and the pole moves by less than the factor of two you paid for.

## Where the picture stops holding

Miller's theorem as used here is exact only for a frequency-independent gain across the
bridging element. It is a good estimate while the input pole is well below the output
pole, and it degrades as they close on each other; the module's sandbox, *What raising
the gain does to the corner*, lets you separate and merge two poles and watch the single
break become two. When the drain node is loaded so heavily that the output pole comes
down to meet the input pole, the response near the corner is set by both and the
single-pole estimate stops meaning anything, however carefully you computed $C_{in}$.

The lab builds both routes side by side — `miller_bandwidth` from the formula and
`exact_bandwidth` from a bisection on the two-node solution — so the gap between them
is something you measure rather than something you are told. Module 4 removes the gap
entirely by removing its cause: hold the drain of the input device still, and there is
nothing left for $C_{gd}$ to multiply.
''',
                },
            ],
            "quiz": {
                "title": "The small capacitor and the gain standing behind it",
                "minutes": 8,
                "questions": [
                    {
                        "q": "$C_{gd}$ is roughly a tenth of $C_{gs}$ in this device. Why does it cost more bandwidth?",
                        "opts": [
                            "Its far end swings the opposite way, so it draws far more current than its value suggests",
                            "It sits nearer to the drain terminal, where the signal in a common-source stage is largest",
                            "Overlap capacitance is lossier than channel capacitance once the frequency is high",
                            "It creates the right-half-plane zero, and that zero is what sets the stage's corner",
                        ],
                        "a": 0,
                        "whys": [
                            "A 1 mV wiggle at the gate moves the drain 17.28 mV the other way, so 18.28 mV appears across a capacitor whose near end moved 1 mV — and current follows the voltage across it.",
                            "Position on the die changes nothing. What matters is that its two terminals are the input and the output, so the swing across it is the sum of both, not the swing at either.",
                            "Both capacitances are essentially lossless here, and loss is not what moves a pole. The pole moved because the input node is drawing more current at the same voltage.",
                            "The zero is real and sits at $g_m/(2\\pi C_{gd})$, which is 45.8 GHz for this device — two hundred times the measured corner. It shapes phase, not bandwidth.",
                        ],
                        "why": r"""
The capacitor is unchanged; the voltage across it is not. With a gain of 17.28 the two
terminals move in opposite directions, so a 1 mV gate wiggle puts 18.28 mV across
$C_{gd}$ and it draws 18.28 times the current a grounded 6 fF would. From the gate it
is indistinguishable from a 109.7 fF capacitor to ground, which is nearly twice
$C_{gs}$. The size of a capacitor is only half of what determines its current.
""",
                    },
                    {
                        "q": "With $C_{gs} = 57.3$ fF, $C_{gd} = 6.0$ fF and a gain magnitude of 17.28, what capacitance does the source resistance drive?",
                        "opts": [
                            "About 110 fF: the bridging capacitor after multiplication, which now dominates",
                            "About 63 fF: the two gate capacitances of the device added together",
                            "About 167 fF: $C_{gs}$ unchanged, plus the 6 fF counted 18.28 times over",
                            "About 1.09 pF: both gate capacitances multiplied by the stage gain",
                        ],
                        "a": 2,
                        "whys": [
                            "The Miller term alone, correctly multiplied, but with $C_{gs}$ dropped. It is by far the larger contribution, and leaving out the other 57.3 fF still overstates the corner by a third.",
                            "This is the sum a data sheet quotes as $C_{iss}$, measured with the drain at AC ground. Under that condition there is no multiplication — and no amplifier runs under it.",
                            "$57.3 + 6.0 \\times 18.28 = 166.98$ fF, and the source resistance sees every femtofarad of it.",
                            "Multiplies $C_{gs}$ as well. Its far end is the source terminal, which is grounded and does not move, so there is no extra swing across it to multiply.",
                        ],
                        "why": r"""
$C_{in} = C_{gs} + C_{gd}(1 + A_v) = 57.3 + 6.0 \times 18.28 = 166.98$ fF. Only the
bridging capacitor is multiplied, because only its far end moves; $C_{gs}$ has its far
end on the grounded source terminal and contributes its own value. With
$R_S = 5\ \text{k}\Omega$ that gives a corner near 190 MHz rather than the 503 MHz the
plain sum predicts.
""",
                    },
                    {
                        "q": "The Miller estimate gives 190.6 MHz and the exact two-node solution gives 181.7 MHz. Which way does the estimate err, and why?",
                        "opts": [
                            "Optimistic: it folds $C_{gd}$ onto the gate and drops the drain-side time constant",
                            "Pessimistic: near the corner the gain has dropped, so less capacitance is multiplied",
                            "Neither: the estimate is exact, and the 9 MHz gap is the bisection's tolerance",
                            "Optimistic: the right-half-plane zero lifts the magnitude that the estimate omits",
                        ],
                        "a": 0,
                        "whys": [
                            "$C_{gd}$ charges through $R_S + R_L + g_mR_SR_L$, and the Miller form counts only the first and third of those — the missing $R_LC_{gd}$ is 60 ps out of 895 ps.",
                            "This effect is genuine and it does run the other way — the multiplication really is smaller near the corner than the DC gain suggests. It is much the weaker of the two, and the net error is still optimism.",
                            "The bisection converges to a part in $10^{12}$ over 200 halvings; 9 MHz out of 182 is five per cent, which is a modelling gap rather than a numerical one.",
                            "The zero does lift the magnitude, but at 45.8 GHz it is far too remote to move a corner near 182 MHz, and the estimate's optimism has a much nearer source.",
                        ],
                        "why": r"""
Count time constants rather than poles. $C_{gd}$ charges through
$R_S + R_L + g_mR_SR_L$; the Miller form gathers $R_S(1 + g_mR_L)$ onto the gate and
drops the leftover $R_L$, which is 60 ps of the 895 ps total. An estimate that discards
delay always promises bandwidth the circuit does not have. A second approximation runs
the other way — the gain has fallen by the corner, so rather less than 109.7 fF is
really being multiplied — and it is the smaller of the two. The lab asserts the net
ordering: the Miller bandwidth above the exact one, and the two within ten per cent
while the poles stay apart.
""",
                    },
                    {
                        "q": "Raising $R_L$ from 10 k$\\Omega$ to 50 k$\\Omega$ takes the gain from 17.28 to 86.4 and the bandwidth from 181.7 MHz to 50.0 MHz. The product rose from 3.14 GHz to 4.32 GHz. Why did it not hold constant?",
                        "opts": [
                            "The output pole moved outward as $R_L$ rose and gave back some of the bandwidth",
                            "Only the Miller part of $C_{in}$ scales with gain, and $C_{gs}$ weighs less as it grows",
                            "A two-pole response has no gain-bandwidth product, so the two numbers cannot be compared",
                            "The right-half-plane zero contributes gain, and it contributes more at high gain",
                        ],
                        "a": 1,
                        "whys": [
                            "Raising $R_L$ moves the output pole the wrong way — down, not out. The bandwidth improvement has to come from the input node, and it comes from $C_{gs}$ losing its share of $C_{in}$.",
                            "$A_v/(2\\pi R_S(C_{gs} + C_{gd}(1+A_v)))$ rises with $A_v$ toward the ceiling $1/(2\\pi R_SC_{gd}) = 5.31$ GHz, and $C_{gs}$ is what keeps it below that.",
                            "The product is defined for any response; it is being read here as the gain times the measured $-3$ dB point, which both stages have. What is in question is whether it is invariant, and it is not.",
                            "The zero sits at $g_m/(2\\pi C_{gd})$, which depends on neither $R_L$ nor the gain. It is in the same place in both stages and cannot explain a difference between them.",
                        ],
                        "why": r"""
The product is $A_v/(2\pi R_SC_{in})$ with
$C_{in} = C_{gs} + C_{gd}(1 + A_v)$. If $C_{gs}$ were absent the $A_v$ would cancel
against $(1+A_v)$ and the product would be a constant $1/(2\pi R_SC_{gd}) = 5.31$ GHz.
$C_{gs}$ is not absent, and at low gain it is most of $C_{in}$, so the product starts
well below that ceiling and climbs toward it as the Miller term takes over. The
invariant is a limit that high-gain stages approach, not a conservation law, and what
sets it is the source resistance and the overlap capacitance rather than the load
resistor being adjusted.
""",
                    },
                    {
                        "q": "Seen from the drain looking back, what does the same 6 fF $C_{gd}$ contribute?",
                        "opts": [
                            "About 6.35 fF, because the gain from the drain back to the gate is only $-1/A_v$",
                            "About 110 fF, by symmetry: a bridging capacitor is multiplied at both of its ends",
                            "Exactly 6 fF, because Miller's theorem describes the input node and nothing else",
                            "About 104 fF, the multiplied value less the 6 fF already counted at the input",
                        ],
                        "a": 0,
                        "whys": [
                            "The theorem applied at the far end gives $C_{gd}(1 + 1/A_v)$, and $1/17.28$ is a four per cent correction rather than a multiplication.",
                            "The theorem is not symmetric, and the asymmetry is its practical point: the bridging capacitor is ruinous at the input and nearly free at the output.",
                            "The theorem applies at both ends; the factor at the output end happens to be close to 1, which is not the same as being exactly 1.",
                            "There is no bookkeeping in which multiplied charge is split between the two nodes. Each node is loaded by the swing it sees across the capacitor, computed independently.",
                        ],
                        "why": r"""
Standing at the drain, the far end of $C_{gd}$ is the gate, and the gain from drain
back to gate is $-1/A_v$. The factor is therefore $1 + 1/17.28 = 1.058$, giving
6.35 fF. That asymmetry is the useful half of the theorem: the same component is worth
110 fF at one end and 6.35 fF at the other, which is why bandwidth work on a
common-source stage concentrates almost entirely on the gate node.
""",
                    },
                    {
                        "q": "Which change removes the multiplication itself, rather than working around its cost?",
                        "opts": [
                            "Drive the gate from a stiffer source, so that the pole rises for any input capacitance",
                            "Lower $R_L$ until the gain is small enough that the multiplier is close to one",
                            "Halve the width of the device, which halves both of its gate capacitances",
                            "Keep the drain of the input device from moving, and develop the gain further along",
                        ],
                        "a": 3,
                        "whys": [
                            "A stiffer source raises the pole for any $C_{in}$ and is worth doing, but $C_{in}$ is still 167 fF and the multiplication is untouched. It treats the symptom.",
                            "This works and it is the wrong trade: the multiplication is removed by removing the gain that caused it, which is the thing the stage was built to provide.",
                            "Both capacitances halve, but at fixed current $g_m$ falls by $\\sqrt{2}$ as well, so the gain drops and the pole improves by less than the factor paid for.",
                            "The multiplier is $1 + |A|$ where $A$ is the gain across that capacitor alone. Hold the drain still and $|A|$ falls to about one, whatever the stage as a whole is doing.",
                        ],
                        "why": r"""
The multiplier is $1 + |A|$ where $A$ is the gain measured across the bridging
capacitor, not the gain of the stage. Stack a common-gate device on top and the input
transistor's drain drives about $1/g_{m2}$ instead of $R_L$; the gain across
$C_{gd1}$ collapses to roughly one while the stage keeps developing its full gain at
the upper device's drain. That is the cascode of module 4, and it is the only one of
these that keeps the gain and removes the cause. The others trade gain away, shrink the
device, or improve the pole while leaving 167 fF on the gate.
""",
                    },
                ],
            },
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
                        "hint": "Subtracting a negative number adds. The two ends of the capacitor move in opposite directions, so the voltage across it is larger than the input swing.",
                        "deconstruct": [
                            "$v_{in} - v_{out} = v_{in} - (-A_v v_{in}) = v_{in}(1 + A_v)$.",
                            "Multiply by the admittance $s C_{gd}$.",
                        ],
                    },
                    {
                        "prompt": "Divide that current by $v_{in}$ to get the admittance the input sees, then read off the equivalent grounded capacitance $C_M$ in terms of $C_{gd}$ and $A_v$.",
                        "answer": "C_{gd} \\left(1 + A_v\\right)",
                        "hint": "An admittance of the form $sC$ is a capacitor of value $C$.",
                        "deconstruct": [
                            "The admittance is $s C_{gd}(1 + A_v)$.",
                            "Comparing with $sC$ gives $C = C_{gd}(1 + A_v)$.",
                        ],
                    },
                    {
                        "prompt": "$C_{gs}$ already sits from gate to ground and is not multiplied. Write the total input capacitance $C_{in}$.",
                        "answer": "C_{gs} + C_{gd} \\left(1 + A_v\\right)",
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
            "blanks": {
                "title": "Miller, in one line each",
                "minutes": 9,
                "caption": "miller.py — what a bridging capacitor looks like from each side",
                "lang": "python",
                "brief": r"""
Miller's theorem replaces one awkward bridging capacitor with two grounded ones, and
the whole of a common-source stage's bandwidth problem is in the size of the first.

The stage has voltage gain $-A_v$ from gate to drain, and $C_{gd}$ bridges the two.
""",
                "listing": """# Miller's theorem: a bridging Z across a gain of -Av looks, from the input,
# like an impedance Z/(1 + Av) to ground -- which for a capacitor means

C_in_from_Cgd  = C_gd * (1 + ___)

# and from the output side, where the far end is the input,

C_out_from_Cgd = C_gd * (1 + ___)

# so the pole the source resistance sees sits at

f_in = 1 / (2 * pi * R_sig * (C_gs + ___))

# and the multiplication is worst in a stage with ___ .
""",
                "blanks": [
                    {
                        "prompt": "The input side sees the far end swinging the other way, and harder.",
                        "hole": "?",
                        "opts": ["Av", "1 / Av", "Av ** 2", "0"],
                        "a": 0,
                        "why": "A 1 V wiggle at the gate puts $-A_v$ volts at the drain, so the voltage *across* $C_{gd}$ is $1 + A_v$ volts and it draws $(1+A_v)$ times the current a grounded $C_{gd}$ would. That is the whole of the Miller effect: the capacitor is not bigger, the voltage across it is.",
                        "whys": [
                            "A 1 V wiggle at the gate puts $-A_v$ volts at the drain, so the voltage *across* $C_{gd}$ is $1 + A_v$ volts and it draws $(1+A_v)$ times the current a grounded $C_{gd}$ would. That is the whole of the Miller effect: the capacitor is not bigger, the voltage across it is.",
                            "That is the *output* side's factor. Using it at the input makes the multiplication into a division and predicts that high-gain stages are the fastest — the opposite of what every measurement shows.",
                            "The factor is linear in the gain, not quadratic. A stage with a gain of 20 multiplies $C_{gd}$ by 21, not by 400.",
                            "This would say a bridging capacitor is no different from a grounded one, which is precisely the assumption the theorem exists to correct.",
                        ],
                    },
                    {
                        "prompt": "Now stand at the drain and look back.",
                        "hole": "?",
                        "opts": ["1 / Av", "Av", "2", "0"],
                        "a": 0,
                        "why": "From the output the gain to the far end is $-1/A_v$, so the factor is $1 + 1/A_v$ — barely more than 1 for any real gain. The asymmetry is the useful part: $C_{gd}$ is devastating at the input and nearly irrelevant at the output, which is why bandwidth work concentrates entirely on the input node.",
                        "whys": [
                            "From the output the gain to the far end is $-1/A_v$, so the factor is $1 + 1/A_v$ — barely more than 1 for any real gain. The asymmetry is the useful part: $C_{gd}$ is devastating at the input and nearly irrelevant at the output, which is why bandwidth work concentrates entirely on the input node.",
                            "Applies the input factor to the output as well, which would double-count the multiplication and predict an output pole far lower than the measured one.",
                            "There is no factor of two here; the theorem is not symmetric, and that asymmetry is its main practical consequence.",
                            "Would remove $C_{gd}$ from the output entirely. Its contribution there is small but it is not nothing.",
                        ],
                    },
                    {
                        "prompt": "What loads the input node, besides C_gs?",
                        "hole": "?",
                        "opts": ["C_gd * (1 + Av)", "C_gd", "C_gs", "C_gd / Av"],
                        "a": 0,
                        "why": "The Miller-multiplied $C_{gd}$, and in a high-gain stage it dominates $C_{gs}$ outright even though $C_{gd}$ is by far the smaller capacitor. That is the sentence to carry away: the small one does the damage, because the gain is standing behind it.",
                        "whys": [
                            "The Miller-multiplied $C_{gd}$, and in a high-gain stage it dominates $C_{gs}$ outright even though $C_{gd}$ is by far the smaller capacitor. That is the sentence to carry away: the small one does the damage, because the gain is standing behind it.",
                            "The raw value, unmultiplied. This is the estimate that makes a stage look ten times faster than it measures, and it is the most common bandwidth error in a first design.",
                            "$C_{gs}$ is already in the expression; adding it twice does not account for the bridging capacitor at all.",
                            "Divides where it should multiply, which would make high-gain stages the fastest ones.",
                        ],
                    },
                    {
                        "prompt": "When does the multiplication hurt most?",
                        "hole": "?",
                        "opts": ["high gain", "low gain", "a small C_gd", "a small source resistance"],
                        "a": 0,
                        "why": "The factor is $1 + A_v$, so the more gain the stage has, the more of its own bandwidth it destroys. Gain and bandwidth are in direct conflict through a single capacitor — and the cascode in module 4 is the answer: it keeps the gain but stops the input device from swinging its own drain, so there is nothing left to multiply.",
                        "whys": [
                            "The factor is $1 + A_v$, so the more gain the stage has, the more of its own bandwidth it destroys. Gain and bandwidth are in direct conflict through a single capacitor — and the cascode in module 4 is the answer: it keeps the gain but stops the input device from swinging its own drain, so there is nothing left to multiply.",
                            "At a gain of 1 the factor is only 2, which is nearly harmless. Low-gain stages barely suffer from Miller at all, which is why a source follower is fast.",
                            "A small $C_{gd}$ helps; the problem is that the multiplication can make even a small one dominant.",
                            "A small $R_{sig}$ also helps — it raises the pole for any capacitance. The multiplication itself does not depend on it.",
                        ],
                    },
                ],
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
            "read": [
                {
                    "title": "Two figures of merit, and the amplifiers they do not describe",
                    "minutes": 17,
                    "body": r'''
The same device is on the probe station: $20\ \mu\text{m}$ by $0.5\ \mu\text{m}$,
biased at $172.8\ \mu\text{A}$, $g_m = 1.728$ mS. The drain is taken to small-signal
ground through a bias tee, a small current is forced into the gate, and the current
coming out of the drain is measured against it. That ratio is $h_{21}$, and the sweep
reads $43.4$ at $100$ MHz, $21.7$ at $200$ MHz, $10.9$ at $400$ MHz. Every doubling of
frequency halves it.

Draw that line out to where it crosses one and it crosses at $4.34$ GHz. Write that
number in the process document and it becomes "a $4.3$ GHz device", and from there it
becomes, in a design review, an argument that a $1$ GHz amplifier ought to be
comfortable. The stage this course builds out of this device has $6$ MHz of bandwidth.

Neither number is wrong. They are answers to different questions, and this module is
about the distance between them.

## Where the straight line comes from

The measurement has the drain at AC ground, so the transistor's own drain voltage never
moves and there is no $C_{gd}$ multiplication and no voltage gain to speak of. The gate
draws no DC current at all, so every bit of the forced input current goes into charging
the two gate capacitances:

$$i_{in} = j\omega\left(C_{gs} + C_{gd}\right)v_{gs}, \qquad i_{out} = g_mv_{gs}$$

Divide, and $v_{gs}$ disappears:

$$\left|h_{21}\right| = \frac{g_m}{\omega\left(C_{gs} + C_{gd}\right)}$$

That is the straight line. It falls as $1/f$ because the numerator is a constant of the
bias point and the denominator is a capacitive admittance, and nothing else in the
expression has any frequency in it. Set it to one and the crossing is

$$f_T = \frac{g_m}{2\pi\left(C_{gs} + C_{gd}\right)}$$

which is transconductance divided by the charge that has to be moved to obtain it.

```python
import math

g_m, C_gs, C_gd = 1.728e-3, 57.3e-15, 6.0e-15


def h21(f):
    """Short-circuit current gain, keeping the feed-forward through C_gd."""
    s = 2j * math.pi * f
    return (g_m - s * C_gd) / (s * (C_gs + C_gd))


for f in (1e8, 2e8, 4e8):
    print(f"|h21| at {f / 1e6:4.0f} MHz      : {abs(h21(f)):7.3f}")
f_T = g_m / (2 * math.pi * (C_gs + C_gd))
print(f"g_m/(2 pi (Cgs + Cgd)) : {f_T / 1e9:7.4f} GHz")
print(f"|h21| at that frequency: {abs(h21(f_T)):7.4f}")
```

The last line is worth a moment. At the frequency the formula calls $f_T$, the current
gain is $1.0045$ rather than $1$. The formula dropped the current that feeds *forward*
through $C_{gd}$ into the drain, which subtracts from the output current and therefore
delays the crossing; keeping it gives
$f_T = g_m/\left(2\pi\sqrt{C_{gs}(C_{gs}+2C_{gd})}\right) = 4.3644$ GHz, half a per cent
higher. The lab, *Measure f_T the way the definition says*, has you find the crossing by
bisecting on your own `h21` rather than trusting the closed form, and then asserts the
ordering: the measured $f_T$ is above the formula's, and with a fat $20$ fF $C_{gd}$ the
gap grows to three and a half per cent.

## What $f_T$ is made of

Substitute the long-channel expressions $g_m = \mu C_{ox}(W/L)V_{ov}$ and
$C_{gs} = \tfrac{2}{3}WLC_{ox}$ and watch what survives. $W$ cancels, $C_{ox}$ cancels,
and one factor of $L$ comes from each:

$$f_T = \frac{g_m}{2\pi C_{gs}} = \frac{3\mu V_{ov}}{4\pi L^2}$$

With $\mu = 200\ \mu\text{A/V}^2 / 8.6\ \text{mF/m}^2 = 0.0233\ \text{m}^2/\text{Vs}$
and $L = 0.5\ \mu\text{m}$ that is $4.44$ GHz, which agrees with $g_m/(2\pi C_{gs})$ on
the same device to every digit — the difference from the $4.34$ GHz above is $C_{gd}$
being counted and the channel-length modulation factor being kept.

Read the expression rather than memorising it. Width is absent: a wider device has more
$g_m$ and exactly proportionally more capacitance, which is why the lab's scaling test
doubles every capacitance and requires $f_T$ to halve. Current is absent too, except
through $V_{ov}$: at fixed geometry $f_T \propto V_{ov} \propto \sqrt{I_D}$, so four
times the current buys twice the speed and — from module 1 — halves the intrinsic gain
along the way. Length appears squared, which is why the industry spent thirty years on
it.

## The two assumptions, and what they cost

Everything above holds under two conditions that the measurement imposed. The drain was
shorted, so there was no load, no voltage swing at the output, and no Miller
multiplication. And the gate was driven from a current source, so the source resistance
was zero and the gate capacitance formed a pole with nothing.

An amplifier violates both. It has a load, because a load is what the gain is developed
across; and it is driven from the output impedance of whatever came before it. Put the
numbers from this course's own labs against $f_T$:

```python
import math

g_m, C_gs, C_gd = 1.728e-3, 57.3e-15, 6.0e-15
f_T = g_m / (2 * math.pi * (C_gs + C_gd))

# each of these is a -3 dB point from an exact nodal solve, on this same device,
# in this course's own labs
stages = [
    ("common source, 5k source, 10k load", 181.75e6),
    ("common source, 50k source, 100k load", 6.045e6),
    ("cascode, 50k source, 100k load", 37.76e6),
]
print(f"f_T = {f_T / 1e9:.3f} GHz")
for name, f in stages:
    print(f"  {name:36s} {f / 1e6:7.2f} MHz   f_T /{f_T / f:7.1f}")
```

A factor of $24$ in the friendliest case, $719$ in the case the capstone specification
is written around, and $115$ for a cascode built from the same two transistors. A real
design does not sit a little below $f_T$; it sits one to three orders of magnitude
below, and which order depends on the source resistance and the load, neither of which
$f_T$ knows anything about.

That does not make $f_T$ useless — it makes it a *device* number. It is the largest
transconductance-per-capacitance the device can offer, so it ranks two devices, or two
bias points of one device, and it says how much room a circuit-level idea has to work
in. The build exercise in this module, *The small-signal model is a circuit — so build
it*, makes the shape of the comparison concrete: a $2$ mA/V source into a $1$ pF load
has a gain-bandwidth product of $g_m/(2\pi C_L) = 318$ MHz, in which the load resistor
has cancelled out. Identical algebra to $f_T$, a different capacitance, and a number
fourteen times smaller — because a $1$ pF load is fifteen times the device's own gate
capacitance. $f_T$ is that same expression evaluated with the smallest capacitance the
device can possibly be asked to drive: its own.

## Why a second figure of merit exists

At $f_T$ the current gain is one, and a current gain of one is not by itself worth
anything. What a receiver's first stage sells is *power* gain, and power gain can still
exceed one at frequencies where current gain does not, because a lossless matching
network is allowed to trade current for voltage.

Power gain also brings in something $f_T$ ignores completely. The gate is not an ideal
capacitor: it is a resistive sheet, and the current charging $C_{gs}$ has to flow
through that resistance, dissipating power that never reaches the output. Call it
$R_g$. Working the input dissipation against the power the device can deliver gives the
unilateral power gain, and the standard result is

$$U(f) = \frac{f_T}{16\pi R_gC_{gd}f^2} = \left(\frac{f_{max}}{f}\right)^2,
\qquad f_{max} = \sqrt{\frac{f_T}{16\pi R_gC_{gd}}}$$

which is the expression the derivation unit, *The transit frequency and the maximum
oscillation frequency*, converts from radians to hertz step by step. Power gain falls
as $1/f^2$, twenty decibels per decade, and reaches unity at $f_{max}$ — above which
the device cannot be made to oscillate, whatever is wrapped around it.

```python
import math

g_m, C_gs, C_gd = 1.728e-3, 57.3e-15, 6.0e-15
f_T = g_m / (2 * math.pi * (C_gs + C_gd))
for R_g in (200.0, 20.0):
    f_max = math.sqrt(f_T / (16 * math.pi * R_g * C_gd))
    print(f"R_g = {R_g:5.1f} ohm -> f_max = {f_max / 1e9:6.3f} GHz, "
          f"U at 1 GHz = {(f_max / 1e9) ** 2:6.1f}")
```

With a $200\ \Omega$ gate, $f_{max} = 8.487$ GHz — above $f_T$, which is normal and not
a contradiction: between the two frequencies the device has lost its current gain and
kept its power gain. At $1$ GHz the same device offers at most $72$ times the power it
is fed, $18.6$ dB, and that is the ceiling with perfect matching and perfect
neutralisation, before any of it is spent on bandwidth, noise or linearity.

Now change nothing but the drawing. Split the same $20\ \mu\text{m}$ of width into ten
$2\ \mu\text{m}$ fingers and contact each gate at both ends: $N$ fingers in parallel cut
the gate resistance by roughly $N^2$, and the second contact by about four again, so
$200\ \Omega$ becomes $20\ \Omega$. $f_{max}$ goes to $26.8$ GHz and $U$ at $1$ GHz to
$720$. The device is the same, the bias is the same, and $f_T$ has not moved by a
hertz, because there is no resistance anywhere in $g_m/(2\pi(C_{gs}+C_{gd}))$. The lab
makes the same point arithmetically: ten times $R_g$ costs a factor of $\sqrt{10}$ in
$f_{max}$.

## The mistake, and why it is tempting

The mistake is treating $f_T$ as the speed of the circuit rather than of the device —
and its sharpest form is the belief that a stage's gain-bandwidth product is $f_T$, so
that a gain of ten leaves $434$ MHz on the table. On this device with a $50$ k$\Omega$
source, gain ten arrives with about $6$ MHz.

It is tempting for good reasons. $f_T$ is the only number in the process document with
units of hertz. It is a genuine measurement, not a fudge. And there is a real
inequality lurking underneath — $g_m$ over the capacitance the transconductance must
drive does bound what any single stage can do — which makes the folklore feel like
physics. What ruins it is that the capacitance in a circuit is never the device's own
gate capacitance. It is that capacitance multiplied by the Miller factor of module 2,
sitting against a source resistance that is not zero, and $518$ fF against
$50\ \text{k}\Omega$ is $6$ MHz however fast the transistor is.

The companion mistake is choosing devices by $f_T$ alone. Two transistors with
identical $f_T$ can differ by a factor of three in $f_{max}$ on layout, and by more than
that in a Miller-limited stage on their $C_{gd}$, which appears in neither figure of
merit with any weight.

## Where these numbers stop holding

The long-channel scaling $f_T \propto \mu V_{ov}/L^2$ dies with velocity saturation. In
a short-channel device the carriers stop accelerating, $g_m$ tends to $WC_{ox}v_{sat}$,
and $f_T$ tends to $v_{sat}/(2\pi L)$ — first power of $L$, not the second, and no
longer improving with overdrive. Real devices also show $f_T$ *peaking* against current
density and falling beyond it, as mobility degradation and series resistance in the
source and drain take over; the model here is monotonic in $I_D$, which no measured
device is.

Both figures also assume the hybrid-pi model is the whole device. The extrapolation
from a measured $h_{21}$ includes the drain-bulk capacitance, the source and drain
series resistances and the substrate network, none of which are in the two-capacitor
model, so a measured $f_T$ generally comes in below the one computed from $g_m$ and the
gate capacitances. And $U(f)$ assumes unilateralisation — that the reverse path through
$C_{gd}$ has been cancelled by a network you have not built. $f_{max}$ is the frequency
at which a device you do not have would stop oscillating.

The sandbox for this module, *How far away the second pole has to be*, is where the
consequence shows up as a shape: a device pole too close to the amplifier's own pole
rings, and pushing it out past critical damping stops helping. That distance is what
$f_T$ buys you, and what module 4 spends a second transistor to stop wasting.
''',
                },
            ],
            "quiz": {
                "title": "What the two frequencies measure, and what they leave out",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A device with $f_T = 4.34$ GHz is used in a common-source stage. What does $f_T$ tell you about that stage's $-3$ dB bandwidth?",
                        "opts": [
                            "It is the bandwidth of the stage itself, since both of them are set by the same capacitances",
                            "It is the bandwidth the stage reaches once its own voltage gain is divided out of it",
                            "It is a hard ceiling the stage approaches as its load resistance is made small enough",
                            "Very little on its own: it was measured with the drain shorted and the gate current-driven",
                        ],
                        "a": 3,
                        "whys": [
                            "The same capacitances appear in both, but against entirely different resistances and multiplied by an entirely different gain — 4.34 GHz against roughly 6 MHz on the same device.",
                            "This is the gain-bandwidth folklore, and it fails by two orders of magnitude here — a gain of ten would predict 434 MHz where the stage delivers about 6 MHz.",
                            "Shrinking the load does raise the corner, but toward $1/(2\\pi R_SC_{in})$ with the Miller term still in $C_{in}$, and the gain vanishes on the way. The ceiling is set by the source resistance, not by $f_T$.",
                            "Both conditions of the measurement are broken by any amplifier: it has a load, and it is driven from a real source impedance.",
                        ],
                        "why": r"""
$f_T$ is a property of the device at a bias point, measured under two conditions no
amplifier meets: the drain shorted, so there is no load and no Miller multiplication,
and the gate current-driven, so there is no source resistance to form a pole with. Put
the same device in the stage the capstone is written around and the corner is 6 MHz,
$719$ times below $f_T$; loosen the source resistance to $5\ \text{k}\Omega$ and it is
$182$ MHz, still $24$ times below. $f_T$ ranks devices and bias points, and it bounds
what a circuit-level idea has to work with. It is not the bandwidth of anything you
will build.
""",
                    },
                    {
                        "q": "A sweep reads $\\left|h_{21}\\right| = 43.4$ at 100 MHz. What is $f_T$, and why can it be had from one point?",
                        "opts": [
                            "About 4.3 GHz, because $\\left|h_{21}\\right|$ falls as $1/f$, so unity is 43.4 times up",
                            "About 434 MHz, because the current gain falls by a decade for each decade of frequency",
                            "About 2.2 GHz, because the current gain is down by half once the drain is loaded",
                            "It cannot be had from one point, because the roll-off rate is a property of the device",
                        ],
                        "a": 0,
                        "whys": [
                            "$\\left|h_{21}\\right| = g_m/(\\omega(C_{gs}+C_{gd}))$ has frequency in one place and to one power, so one measured point fixes the whole line.",
                            "Reads the 20 dB/decade slope as though the gain fell tenfold per decade of gain rather than per decade of frequency; the two are the same slope stated wrongly, and it lands a factor of ten low.",
                            "There is no factor of two here, and no load either — the drain is at AC ground throughout the measurement, which is what makes the roll-off a clean $1/f$.",
                            "The roll-off rate is not a free parameter: a transconductance against a capacitive admittance can only give $1/f$, which is why one point and a slope are enough.",
                        ],
                        "why": r"""
The short-circuit current gain is $g_m$ over a capacitive admittance, so it falls as
$1/f$ with no other frequency dependence anywhere in it. One measured point therefore
fixes the entire line: $43.4$ at $100$ MHz puts unity at $43.4 \times 100$ MHz, which
is $4.34$ GHz. That is how the number is obtained in practice, because at $4.34$ GHz
the pads, the package and the probes contribute more than the device does. $f_T$ is an
extrapolation, and describing it as a measured frequency overstates what was measured.
""",
                    },
                    {
                        "q": "The device does 4.34 GHz. The common-source stage built from it, driven from 50 k$\\Omega$ into a 100 k$\\Omega$ load, does 6.0 MHz. Where did the factor of 719 go?",
                        "opts": [
                            "Into the bias point, which is chosen for gain rather than for a high transit frequency",
                            "Into the drain node, where the 100 k$\\Omega$ load works against the load capacitance",
                            "Into a gate node driven from 50 k$\\Omega$ into 518 fF of Miller-multiplied capacitance",
                            "Into the 5 fF load capacitance, which is what the transconductance has to drive",
                        ],
                        "a": 2,
                        "whys": [
                            "The bias is the same one $f_T$ was quoted at — the same $g_m$, the same capacitances. Nothing about the device changed between the two numbers.",
                            "The output node is real but fast: $43.9\\ \\text{k}\\Omega$ against 11 fF puts that pole at about 330 MHz, fifty times above the corner being explained.",
                            "$1/(2\\pi \\times 50\\,\\text{k}\\Omega \\times 518\\,\\text{fF})$ is 6.1 MHz, which accounts for the measured corner within two per cent.",
                            "5 fF against the output resistance is a pole in the hundreds of megahertz. The capacitance that matters is at the gate, and Miller has made it a hundred times larger.",
                        ],
                        "why": r"""
The Miller-multiplied input capacitance is
$C_{gs} + C_{gd}(1 + 75.8) = 518$ fF, and against a $50\ \text{k}\Omega$ source that is
a pole at $6.1$ MHz — the whole of the measured $6.045$ MHz, to two per cent. Both
things $f_T$ assumed away are in that one number: the load that lets the drain swing,
which is what multiplies $C_{gd}$, and the source resistance, which is what turns a
capacitance into a pole. The output node contributes a pole near $330$ MHz and is not
the constraint.
""",
                    },
                    {
                        "q": "Splitting a device into ten fingers contacted at both ends drops $R_g$ from 200 $\\Omega$ to 20 $\\Omega$. Which figure of merit moves?",
                        "opts": [
                            "$f_{max}$, from 8.5 GHz to 26.8 GHz; $f_T$ contains no resistance and does not move",
                            "Both, since $f_{max}$ is built on $f_T$ and anything that changes one must change the other",
                            "$f_T$, because narrow fingers have less gate area and therefore a smaller $C_{gs}$",
                            "Neither, because both are properties of the process and the bias rather than the drawing",
                        ],
                        "a": 0,
                        "whys": [
                            "$f_{max} = \\sqrt{f_T/(16\\pi R_gC_{gd})}$ improves as $1/\\sqrt{R_g}$, while $g_m/(2\\pi(C_{gs}+C_{gd}))$ has no resistance in it at all.",
                            "$f_{max}$ is built on $f_T$, but the dependence runs one way: $R_g$ enters $f_{max}$ and appears nowhere in $f_T$, so this change moves one and not the other.",
                            "Ten fingers of one tenth the width have exactly the same total area and the same $C_{gs}$. What fingering changes is how far the gate current has to travel through the polysilicon.",
                            "Layout is precisely what this changes. Two devices identical in process and bias can differ by three times in $f_{max}$ on the drawing alone, which is why $f_{max}$ is a layout figure of merit.",
                        ],
                        "why": r"""
$f_T = g_m/(2\pi(C_{gs}+C_{gd}))$ has no resistance in it anywhere, so no amount of
redrawing moves it. $f_{max} = \sqrt{f_T/(16\pi R_gC_{gd})}$ falls as $\sqrt{R_g}$, so
a tenfold cut in gate resistance buys a factor of $\sqrt{10}$ — from $8.5$ GHz to
$26.8$ GHz, with the unilateral power gain at 1 GHz going from 72 to 720. Same device,
same bias, same current: this is the cheapest speed in the whole subject, and it is
invisible to the one number most often quoted.
""",
                    },
                    {
                        "q": "For this device $f_{max} = 8.5$ GHz sits above $f_T = 4.3$ GHz. How can that be?",
                        "opts": [
                            "The matching networks assumed in the $f_{max}$ measurement supply the extra gain themselves",
                            "They measure different gains: current gain reaches one at $f_T$, power gain at $f_{max}$",
                            "It cannot be: $f_{max}$ is an upper bound, so a value above $f_T$ means an arithmetic slip",
                            "$f_{max}$ leaves out $C_{gs}$, which is what makes it exceed the transit frequency",
                        ],
                        "a": 1,
                        "whys": [
                            "A matching network is lossless and supplies no gain — it transforms impedance so that the gain the device has can be delivered. Believing otherwise makes every passive network a free amplifier.",
                            "Between the two frequencies the device has lost its current gain and kept its power gain, which a lossless network can trade back into voltage.",
                            "$f_{max}$ bounds oscillation, not $f_T$. The two are independent enough that either ordering occurs in practice, and which one you get depends mostly on the gate resistance.",
                            "$C_{gs}$ is in $f_{max}$ through $f_T$, which sits inside the square root. What $f_{max}$ adds is $R_g$, and lowering that is what pushes it above $f_T$ here.",
                        ],
                        "why": r"""
The two numbers answer different questions. $f_T$ is where the short-circuit *current*
gain reaches one; $f_{max}$ is where the *power* gain does. Above $f_T$ the device
returns less current than it is given and can still return more power, because a
lossless matching network is free to trade current for voltage, and $f_{max}$ is the
frequency at which no network can do it any longer. With a low gate resistance
$f_{max}$ commonly lands two or three times above $f_T$; with a badly drawn wide device
it lands below. Neither ordering is a mistake.
""",
                    },
                    {
                        "q": "At fixed geometry, the bias current is raised from 172.8 $\\mu$A to 691.2 $\\mu$A. What happens to $f_T$ and to the intrinsic gain?",
                        "opts": [
                            "$f_T$ doubles and the intrinsic gain halves, since $V_{ov}$ has doubled to 0.4 V",
                            "$f_T$ quadruples with the current, and the intrinsic gain is unaffected by bias",
                            "$f_T$ doubles and the intrinsic gain doubles, because $g_m$ has doubled as well",
                            "$f_T$ quadruples and the intrinsic gain halves, because $r_o$ has fallen fourfold",
                        ],
                        "a": 0,
                        "whys": [
                            "$f_T \\propto V_{ov} \\propto \\sqrt{I_D}$ and $g_mr_o = 2(1+\\lambda V_{DS})/(\\lambda V_{ov})$, so both follow the overdrive and in opposite directions.",
                            "Takes $f_T$ as proportional to current rather than to $g_m$; $g_m$ itself grows only as $\\sqrt{I_D}$ at fixed geometry, so four times the current is twice the speed.",
                            "$g_m$ has indeed doubled, but $r_o$ has fallen fourfold at the same time, and their product carries the net factor of one half rather than two.",
                            "The right direction for the gain and the wrong law for $f_T$: $g_m$ is what $f_T$ follows, and it rises as the square root of the current, not with it.",
                        ],
                        "why": r"""
Four times the current at fixed geometry is twice the overdrive: $0.2$ V to $0.4$ V.
$g_m = 2I_D/V_{ov}$ therefore doubles and so does $f_T$, from $4.34$ GHz to
$8.69$ GHz, since the capacitances have not changed. The intrinsic gain is
$2(1+\lambda V_{DS})/(\lambda V_{ov})$, which halves from $135$ to $67.5$. Four times
the power for twice the speed and half the gain is the trade in one line, and it is why
$g_m/I_D$ is treated as a currency rather than a preference.
""",
                    },
                ],
            },
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
                        "hint": "$|s| = \\omega$ on the imaginary axis, and $v_{gs}$ cancels.",
                        "deconstruct": [
                            "$i_{out}/i_{in} = g_m / \\left(s(C_{gs}+C_{gd})\\right)$.",
                            "Take magnitudes with $s = j\\omega$.",
                        ],
                    },
                    {
                        "prompt": "Set that magnitude to one and solve for the transit frequency $\\omega_T$ in rad/s.",
                        "answer": "\\frac{g_m}{C_{gs} + C_{gd}}",
                        "hint": "Multiply both sides by the denominator and read off $\\omega$.",
                        "deconstruct": [
                            "$g_m = \\omega_T (C_{gs}+C_{gd})$.",
                            "Divide through by the total capacitance.",
                        ],
                    },
                    {
                        "prompt": "Write the same thing in hertz as $f_T$.",
                        "answer": "\\frac{g_m}{2 \\pi \\left( C_{gs} + C_{gd} \\right)}",
                        "hint": "$f = \\omega/(2\\pi)$.",
                        "deconstruct": [
                            "Divide $\\omega_T$ by $2\\pi$.",
                        ],
                    },
                    {
                        "prompt": "Now substitute the long-channel expressions $g_m = \\mu C_{ox}(W/L)V_{ov}$ and $C_{gs} = \\tfrac{2}{3}WLC_{ox}$, and neglect $C_{gd}$ entirely. Write $f_T$ in terms of $\\mu$, $V_{ov}$ and $L$.",
                        "given": "Use $f_T = g_m/\\left(2\\pi C_{gs}\\right)$ with those two substitutions.",
                        "answer": "\\frac{3 \\mu V_{ov}}{4 \\pi L^{2}}",
                        "hint": "$W$ and $C_{ox}$ appear once on the top and once on the bottom, so both cancel. What is left is one $L$ from $g_m$ and one from $C_{gs}$.",
                        "deconstruct": [
                            "$\\frac{g_m}{C_{gs}} = \\frac{\\mu C_{ox}(W/L)V_{ov}}{\\tfrac{2}{3}WLC_{ox}} = \\frac{3\\mu V_{ov}}{2L^2}$.",
                            "Divide by $2\\pi$ to reach hertz.",
                        ],
                    },
                    {
                        "prompt": "The standard result for the maximum oscillation frequency is $\\omega_{max} = \\sqrt{\\omega_T/\\left(8 R_g C_{gd}\\right)}$. Convert both frequencies to hertz and write $f_{max}$ in terms of $f_T$, $R_g$ and $C_{gd}$.",
                        "answer": "\\sqrt{\\frac{f_T}{16 \\pi R_g C_{gd}}}",
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
            "build": {
                "title": "The small-signal model is a circuit — so build it",
                "minutes": 24,
                "brief": r"""
Everything in this module is drawn as a schematic in the textbook and then solved as
algebra. Here it is a schematic you can actually measure, because the hybrid-pi output
network contains nothing a linear solver cannot handle.

## What the current source is

The canvas has a **2 mA current source**, and it is not a bias current. It is
$g_mv_{gs}$ with $g_m = 2$ mA/V and a 1 V signal on the gate — the controlled source of
the model, frozen at one input amplitude so that the number the probe reads *is* the
voltage gain. That is the one liberty taken here, and it is the standard one: with the
input held at 1 V, a controlled source and an independent source are indistinguishable.

## What to add

The output resistance and the load capacitance, in parallel with the source, so the
stage has

$$A_0 = 9.1, \qquad f_{3dB} = 35\ \text{MHz}$$

$A_0 = g_mR_{out}$ gives you the resistance; $f_{3dB} = 1/(2\pi R_{out}C_L)$ then gives
you the capacitance. Probe the output node.

## What the checks measure

- The DC gain, which is just $I \times R_{out}$ with the capacitor an open circuit.
- The $-3$ dB corner, found by measurement rather than by formula.
- **The product**, and this is the module's whole point: $A_0 \times f_{3dB}$ comes out
  at 318 MHz, and $R_{out}$ has cancelled out of it. Well above the pole the gain is
  $g_m/(2\pi fC_L)$ — the resistor has stopped mattering entirely, and what is left is
  the device's transconductance against the capacitance it has to drive.

## And what it does not promise

318 MHz is $g_m/2\pi C_L$ for *this* load. It is not $f_T$, which is measured with the
output shorted and the capacitance being the device's own $C_{gs} + C_{gd}$ rather than
whatever you hung on the drain. The two expressions look identical and describe
different things — which is the distinction the rest of this module is built around.
""",
                "start": {
                    "parts": [
                        {"id": "i", "kind": "I", "x": 3, "y": 7, "rot": 1, "value": 0.002},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 10},
                        {"id": "g2", "kind": "GND", "x": 15, "y": 10},
                        {"id": "out", "kind": "OUT", "x": 18, "y": 6},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "i", "kind": "I", "x": 3, "y": 7, "rot": 1, "value": 0.002},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                        {"id": "ro", "kind": "R", "x": 9, "y": 8, "rot": 1, "value": 4545},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 10},
                        {"id": "cl", "kind": "C", "x": 15, "y": 8, "rot": 1, "value": 1.0e-12},
                        {"id": "g2", "kind": "GND", "x": 15, "y": 10},
                        {"id": "out", "kind": "OUT", "x": 18, "y": 6},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [9, 6]},
                        {"a": [9, 6], "b": [9, 7]},
                        {"a": [9, 9], "b": [9, 10]},
                        {"a": [9, 6], "b": [15, 6]},
                        {"a": [15, 6], "b": [15, 7]},
                        {"a": [15, 9], "b": [15, 10]},
                        {"a": [15, 6], "b": [18, 6]},
                    ],
                },
                "checks": [
                    {
                        "name": "one resistor and one capacitor, giving a gain of 9.1",
                        "code": r"""
c.assert(c.count('R') === 1, 'One output resistance; there are ' + c.count('R') + '.');
c.assert(c.count('C') === 1, 'One load capacitance; there are ' + c.count('C') + '.');
c.close(Math.abs(c.vout()), 9.09, 0.04,
  'the output at DC. The capacitor is an open circuit there, so the 2 mA flows ' +
  'entirely through your resistor and the node sits at I * R_out. A gain of 9.1 needs ' +
  'R_out = 9.1 / 2 mA');
""",
                    },
                    {
                        "name": "the -3 dB corner is at 35 MHz",
                        "code": r"""
const fc = c.corner(1e3, 1e10);
c.close(fc, 35.0e6, 0.06,
  'the measured -3 dB frequency. It is 1/(2*pi*R_out*C_L), so with R_out already fixed ' +
  'by the gain check, this is entirely a statement about C_L. Too high a corner means ' +
  'the capacitor is too small');
""",
                    },
                    {
                        "name": "the product is 318 MHz, and the resistor is not in it",
                        "code": r"""
const fc = c.corner(1e3, 1e10);
c.close(Math.abs(c.vout()) * fc, 318.3e6, 0.08,
  'gain times bandwidth. Multiply A0 = g_m*R_out by f_3dB = 1/(2*pi*R_out*C_L) and ' +
  'R_out cancels, leaving g_m/(2*pi*C_L). This is the number that does not move when ' +
  'you trade gain for bandwidth');
""",
                    },
                    {
                        "name": "far above the pole, only g_m and C_L are left",
                        "code": r"""
c.close(c.gain(1e9), 0.3183, 0.06,
  'the gain at 1 GHz, nearly thirty times past the corner. There the capacitor is ' +
  'far stiffer than the resistor and carries essentially all the current, so the ' +
  'output is g_m/(2*pi*f*C_L) = 2 mA/V / (2*pi * 1 GHz * 1 pF) and the resistor has ' +
  'dropped out of the answer entirely');
c.assert(c.gain(1e9) < c.gain(1e8),
  'The response must still be falling at 1 GHz. If it is not, there is a second path ' +
  'to the output that is not rolling off.');
""",
                    },
                ],
                "hints": [
                    "$R_{out} = A_0/g_m = 9.1 / (2\\ \\text{mA/V})$. The answer is a few kilohms.",
                    "Then $C_L = 1/(2\\pi R_{out}f_{3dB})$, which comes out very close to a round 1 pF.",
                    "Both components go from the output node to ground, in parallel with the current source — not in series with anything.",
                ],
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
            "read": [
                {
                    "title": "One more transistor, six times the bandwidth",
                    "minutes": 16,
                    "body": r'''
Two amplifiers on the same die, built from the same two transistors, biased at the same
$172.8\ \mu\text{A}$, driven from the same $50$ k$\Omega$ source and loaded by the same
$100$ k$\Omega$. The first is the common-source stage of module 2 with the second device
used as nothing at all. Its gain is $75.8$ and its bandwidth is $6.04$ MHz.

The second stacks that second device on top of the first: source on the input
transistor's drain, gate tied to a fixed bias, drain to the load. Its gain is $170.0$
and its bandwidth is $37.8$ MHz.

More than twice the gain and six times the bandwidth, out of the same silicon, the same
current and the same supply, for one wire moved. Both numbers come from the module's
lab, *Common-source against cascode, by nodal analysis*, which solves each circuit
exactly rather than estimating it. This reading is about where the six came from, and
about the two situations in which it does not arrive.

## The node in the middle

The upper device has its gate held at a fixed voltage, so for small signals that gate
is ground. The input device no longer drives the load; it drives whatever resistance
appears at the *source* of the upper device.

Push a test voltage $v_x$ into that source. The upper transistor's gate-source voltage
is $0 - v_x$, so it pulls a drain current $-g_{m2}v_x$; its own $r_{o2}$ carries
$(v_x - v_{out})/r_{o2}$; and $v_{out}$ is what the load makes of the total. Solving that
loop gives

$$R_x = \frac{R_L + r_{o2}}{1 + g_{m2}r_{o2}}$$

The load has been divided down by the upper device's intrinsic gain before it reaches
the source. When $R_L$ is modest this collapses to $1/g_{m2}$, and the usual statement
is that a cascode presents $1/g_{m2}$ to the device below it. Keep the exact form for a
moment, because the numbers matter here.

```python
import math

g_m, r_o = 1.728e-3, 78125.0
C_gs, C_gd = 57.3e-15, 6.0e-15
R_S, R_L = 50e3, 100e3

A_cs = g_m * (R_L * r_o / (R_L + r_o))
C_in_cs = C_gs + C_gd * (1.0 + A_cs)
R_x = (R_L + r_o) / (1.0 + g_m * r_o)
C_in_ca = C_gs + C_gd * (1.0 + g_m * R_x)
R_out = 2.0 * r_o + g_m * r_o * r_o

print(f"common source : gain {A_cs:6.2f}   C_in {C_in_cs * 1e15:6.1f} fF   "
      f"input pole {1 / (2 * math.pi * R_S * C_in_cs) / 1e6:5.1f} MHz")
print(f"cascode       : gain {g_m * R_out * R_L / (R_out + R_L):6.2f}   "
      f"C_in {C_in_ca * 1e15:6.1f} fF   "
      f"input pole {1 / (2 * math.pi * R_S * C_in_ca) / 1e6:5.1f} MHz")
print(f"into the source of the upper device : {R_x:9.1f} ohm")
print(f"output resistance of the cascode    : {R_out / 1e6:9.3f} Mohm")
print(f"pole at the intermediate node       : {g_m / (2 * math.pi * (C_gs + C_gd)) / 1e9:9.3f} GHz")
```

$R_x$ is $1310\ \Omega$: the $579\ \Omega$ of $1/g_{m2}$ plus $R_L/(g_{m2}r_{o2})$,
which is $100\ \text{k}\Omega/135 = 741\ \Omega$ and not negligible. The gain from the
input gate to that node is $g_{m1}R_x = 2.26$, against $75.8$ when the same device drove
the load directly.

## What that does to the input

Module 2's result was that $C_{gd}$ arrives at the gate multiplied by $1 + |A|$, where
$A$ is the gain measured *across that capacitor* — from the gate to the drain of the
input device, not from the gate to the output. In the common-source stage those are the
same node and the factor is $76.8$. In the cascode they are different nodes, and the
factor is $3.26$.

$$C_{in} = C_{gs} + C_{gd}\left(1 + \frac{g_{m1}}{g_{m2}}\right) \approx C_{gs} + 2C_{gd}$$

The block gives $518.0$ fF for the common-source stage and $76.9$ fF for the cascode, a
factor of $6.7$. Against a $50$ k$\Omega$ source those are single-pole estimates of
$6.1$ MHz and $41.4$ MHz, and the exact solutions are $6.04$ MHz and $37.8$ MHz. The
common-source estimate is within two per cent; the cascode's is ten per cent
optimistic, for the same reason module 2's was — with the input pole pushed out that
far, the pole at the output is no longer remote enough to ignore.

The gain rose at the same time, and by a separate mechanism. Looking *into* the drain
of the upper device, the $r_{o1}$ below it acts as source degeneration and the
resistance becomes $r_{o1} + r_{o2} + g_{m2}r_{o1}r_{o2}$, which the block reports as
$10.7$ M$\Omega$. That is two orders of magnitude above the $78$ k$\Omega$ of a single
device, so the $100$ k$\Omega$ load — which used to be shunted down to $43.9$ k$\Omega$
by $r_o$ — now sees almost nothing in parallel with it and keeps $99.1$ k$\Omega$. The
gain estimate is $171.2$ against the exact $170.0$.

Both improvements come from one structural change, and it is worth stating in one
sentence: the input device no longer sees its own output swing. Its drain barely moves,
so there is nothing for $C_{gd1}$ to multiply; and its $r_{o1}$ is no longer across the
output node, so there is nothing to shunt the gain away.

## What it costs

Headroom, first and most seriously. The two devices are in series and each needs its
own $V_{DSsat}$ — at a $200$ mV overdrive apiece that is $400$ mV of the supply gone
before the load resistor or the output swing has been given anything. On a $1.2$ V rail
that is a third of everything, which is why the cascode is common in a $3.3$ V analogue
block and contentious in a low-voltage one.

Second, a new pole. The intermediate node carries $C_{gs2}$ and $C_{gd1}$, about
$63$ fF, and it is driven from $1/g_{m2}$, so it sits near
$g_{m2}/\left(2\pi C_x\right)$. The block prints that as $4.345$ GHz, and the number
should look familiar: it is the $f_T$ of module 3, the same $g_m$ over the same
capacitance. The extra pole a cascode adds lands at the device's own transit frequency,
which is why it is harmless in any design that was not already running at the device's
limit — and why it stops being harmless if the upper device is made small to save area,
because $g_{m2}$ falls and the pole comes down with it. The sandbox for this module,
*The corner after the Miller penalty is removed*, shows the shape of that: hold the
corner and drop the damping, and a peak appears at the corner.

Third, the upper device contributes noise and area, and its gate needs a bias that is
stable enough not to modulate the intermediate node.

## Where the six disappears

Drive the same two circuits from a $100\ \Omega$ source instead of $50$ k$\Omega$ and
the ordering reverses: the common-source stage measures $301$ MHz and the cascode
$140$ MHz. The lab asserts that inversion, and the ratio it requires is $0.46$.

Two things happened. With a stiff source there was never a Miller problem to solve — a
$518$ fF gate driven from $100\ \Omega$ is a pole at $3$ GHz, nowhere near the answer.
And the cascode's own gain increase works against it here: the resistance at the output
node went from $43.9$ k$\Omega$ to $99.1$ k$\Omega$, so the output pole, which is now
the one that matters, moved down by that same factor. Gain and bandwidth traded exactly
as they always do; the cascode gave back in bandwidth what it took in gain.

The general statement is the useful one. A cascode does not make anything faster. It
removes a penalty that exists only when the *input* node is the bottleneck, and it pays
for that removal with headroom and with a higher output impedance that a
capacitively-loaded output node will notice. When the source is stiff and the load is
capacitive, it is the wrong tool.

The same caution applies at the other end. $R_x$ was $1310\ \Omega$ rather than
$579\ \Omega$ because $R_L/(g_{m2}r_{o2})$ was not small, and in a real amplifier $R_L$
is often another cascode acting as a current source, with megohms rather than
$100$ k$\Omega$. Then $R_L/(g_{m2}r_{o2})$ dominates $R_x$, the gain across $C_{gd1}$
climbs back up, and some of the Miller multiplication returns. The existing quiz in this
module asks exactly that question; the point of it is that $1/g_{m2}$ is a limiting case
and not a law.

## The mistake, and why it is tempting

The mistake is saying that a cascode makes the transistor faster. It is tempting because
the evidence looks overwhelming: the same devices, the same current, six times the
bandwidth *and* twice the gain, which no other bandwidth trick offers. Every other route
— a smaller load resistor, a wider device, a stiffer source — gives something back.

But $f_T = g_m/(2\pi(C_{gs}+C_{gd}))$ contains nothing about what the drain is connected
to. Neither transistor's $f_T$ changed by a hertz. What changed is that a circuit-level
penalty, invented by the topology and not by the physics, was removed. Keeping the two
apart is what stops the next mistake: reaching for a cascode in a stage that is already
output-pole limited, and paying $400$ mV of headroom for the $140$ MHz above instead of
the $301$ MHz that was already there.

The gain-bandwidth products make the same point from the other side. Common-source:
$75.8 \times 6.04\ \text{MHz} = 458$ MHz. Cascode: $170 \times 37.8\ \text{MHz} =
6.42$ GHz, fourteen times higher, which the lab checks as a ratio above ten. A number
that moves by fourteen was never a property of the device.

## Where the model stops holding

Everything above used $g_{m2}r_{o2} \gg 1$ and treated the bias on the upper gate as a
perfect small-signal ground. On a short-channel device $g_mr_o$ can be ten rather than
$135$, and then $R_x$ is a much larger fraction of $R_L$ and the Miller factor is
several rather than two. The output resistance $g_{m2}r_{o1}r_{o2}$ is likewise a
long-channel promise; in a modern process the boost from stacking is real but far
smaller than the square of an intrinsic gain suggests.

The two-transistor nodal model in the lab also has no body effect in it. The upper
device's source is not at the substrate potential, so its threshold rises with $v_x$ and
$g_{mb}$ adds to $g_{m2}$ — which helps, lowering $R_x$ and improving the very thing
this module is about, and which is left out here so the arithmetic stays checkable by
hand.

The capstone puts all of it to work: `size_for_spec` walks a list of candidate currents
and widths, builds the cascode for each, and returns the cheapest that meets a gain and
a bandwidth at once. The trade it is searching against is the one in this module — a
wider device raises $g_m$ and the gain, and raises $C_{gs}$ and costs bandwidth — and
the answer is not the fastest device or the highest-gain device but the smallest one
that clears both lines.
''',
                },
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
                        "hint": "A common-source gain magnitude is $g_m$ times whatever resistance the drain sees.",
                        "deconstruct": [
                            "$|A_1| = g_{m1} \\cdot R_{drain}$.",
                            "Here $R_{drain} = 1/g_{m2}$.",
                        ],
                    },
                    {
                        "prompt": "Apply Miller to $C_{gd1}$ using that gain. Write the total input capacitance $C_{in}$ in terms of $C_{gs1}$, $C_{gd1}$, $g_{m1}$ and $g_{m2}$.",
                        "answer": "C_{gs1} + C_{gd1} \\left(1 + \\frac{g_{m1}}{g_{m2}}\\right)",
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
                        "hint": "Expand the bracket in the given expression and collect the three terms.",
                        "deconstruct": [
                            "$r_{o2}(1 + g_{m2}r_{o1}) = r_{o2} + g_{m2}r_{o1}r_{o2}$.",
                            "Add the remaining $r_{o1}$.",
                        ],
                    },
                    {
                        "prompt": "One term dominates when $g_{m2}r_{o1} \\gg 1$. Write the approximation.",
                        "answer": "g_{m2} r_{o1} r_{o2}",
                        "hint": "Compare the third term with the first two: it is larger by the intrinsic gain of M2.",
                        "deconstruct": [
                            "$g_{m2}r_{o1}r_{o2}$ exceeds $r_{o2}$ by the factor $g_{m2}r_{o1}$, which is of order 100.",
                            "Drop the two small terms.",
                        ],
                    },
                    {
                        "prompt": "If the external load is much larger than $R_{out}$, the stage gain is $-g_{m1}R_{out}$. Write the magnitude of that gain in terms of $g_{m1}$, $g_{m2}$, $r_{o1}$ and $r_{o2}$.",
                        "answer": "g_{m1} g_{m2} r_{o1} r_{o2}",
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
            "quiz": {
                "title": "What stacking a device buys, and what it costs",
                "minutes": 7,
                "questions": [
                    {
                        "q": "How does a cascode defeat the Miller effect?",
                        "opts": [
                            "It holds the input device's drain nearly still, so the gain across $C_{gd}$ is about $-1$",
                            "It removes $C_{gd}$ from the input device",
                            "It lowers the stage's overall gain",
                            "It adds a zero that cancels the input pole",
                        ],
                        "a": 0,
                        "why": r"""
The upper device presents a low resistance — about $1/g_{m2}$ — at its source, so the
input device's drain barely moves however hard the stage is driving. The Miller factor
across $C_{gd1}$ collapses from $1 + A_v$ to roughly 2. The capacitor is still there and
so is the gain; what has changed is where the gain is *developed*, which is now at the
cascode's drain instead.
""",
                    },
                    {
                        "q": "Looking into the source of the upper device, with a load $R_L$ on its drain, the resistance is about:",
                        "opts": [
                            "$\\left(R_L/(g_{m2}r_{o2})\\right) + 1/g_{m2}$",
                            "$g_{m2}r_{o2}R_L$",
                            "$r_{o2}$",
                            "$R_L$",
                        ],
                        "a": 0,
                        "why": r"""
The load is divided down by the device's own intrinsic gain before it appears at the
source, and $1/g_{m2}$ is added on top. For a modest $R_L$ the first term is negligible
and the answer is just $1/g_{m2}$ — which is the low resistance that kills the Miller
effect. The catch is that with a very large $R_L$, as in a cascode current-source load,
the first term stops being negligible and some of the Miller multiplication comes back.
$g_{m2}r_{o2}R_L$ is the resistance looking into the *drain*, the other direction.
""",
                    },
                    {
                        "q": "What is the output resistance of a cascode?",
                        "opts": [
                            "About $g_{m2}r_{o2}r_{o1}$",
                            "About $r_{o1} + r_{o2}$",
                            "About $r_{o1}r_{o2}/(r_{o1}+r_{o2})$",
                            "About $r_{o2}$",
                        ],
                        "a": 0,
                        "why": r"""
The upper device's own intrinsic gain multiplies the lower one's output resistance — a
factor of tens, so a cascode's output resistance is one to two orders above a single
device's. That is the *other* reason cascodes are everywhere: not only bandwidth, but
a much better current source and much higher achievable gain. Adding them in series
would be a modest improvement; the multiplication is what makes it worth the stack.
""",
                    },
                    {
                        "q": "What does the cascode cost?",
                        "opts": [
                            "Voltage headroom — a second device's worth of $V_{DSsat}$",
                            "Current, since it needs its own bias tail",
                            "Gain",
                            "Input capacitance",
                        ],
                        "a": 0,
                        "why": r"""
Headroom, and on a modern low-voltage process that is the binding constraint. The two
devices are in series and each needs its own $V_{DSsat}$ before the signal has anywhere
to swing. It costs no extra current — the same current flows through both, which is
exactly why the topology is efficient — and it *raises* gain rather than lowering it.
""",
                    },
                    {
                        "q": "Does the cascode raise the $f_T$ of the input device?",
                        "opts": [
                            "No — $f_T$ describes the device alone, and the device has not changed",
                            "Yes, by the cascode's intrinsic gain",
                            "Yes, by a factor of two",
                            "Only if the upper device is wider",
                        ],
                        "a": 0,
                        "why": r"""
$f_T = g_m/(2\pi(C_{gs}+C_{gd}))$ is measured with the output shorted, and there is
nothing in it about what the drain is connected to. The cascode changes the *circuit's*
bandwidth, which was never $f_T$ in the first place — and that is the distinction module
3 spent its time on. A figure of merit for the device is not a promise about the
amplifier.
""",
                    },
                ],
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
