"""EE202 — Transistor Amplifiers.

Second year. It assumes the first-year circuits sequence — DC and AC analysis,
phasors and impedance, complex numbers and calculus, Boolean algebra, basic Python
and fields — and nothing above that. The MOSFET itself is introduced here as a
terminal behaviour; the physics that produces that behaviour belongs to EE201.

Authoring rules, as for every course module:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; this course needs only `math`
  * every expected number was produced by running the code, not assumed
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it to the reference drawing

One device runs through the whole course, so that every number can be checked
against every other:

    k = 2 mA/V^2      V_th = 1.0 V      V_A = 45 V

biased at I_D = 1 mA, which gives V_ov = 1.0 V, g_m = 2 mA/V and r_o = 45 kΩ.
The schematic solver has no transistors — it is linear only — so the transistor
appears in the two build exercises the way it appears in an engineer's notebook:
as a current source at DC, and as a current source in parallel with r_o for small
signals. That is not a workaround, it is the model.
"""

COURSE = {
    "id": "EE202",
    "title": "Transistor Amplifiers",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE201"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◈",
    "summary": (
        "A transistor turns a small voltage into a proportional current, and a resistor "
        "turns that current back into a larger voltage. That sentence is the whole of "
        "amplification, and this course makes every quantity in it concrete: the square "
        "law that sets the drain current, the bias network that holds the device at a "
        "sensible operating point, the small-signal model that linearises it, and the "
        "single capacitor that decides how much bandwidth the gain costs you. By the end "
        "you can design a common-source stage from a supply voltage and a gain "
        "requirement, and say in advance what it will and will not do."
    ),
    "outcomes": [
        "Place a MOSFET in cut-off, triode or saturation from its terminal voltages, and compute its drain current in each.",
        "Compute transconductance and output resistance at an operating point, in all three equivalent forms, and say which form to reach for when.",
        "Design a four-resistor bias network for a stated drain current, source voltage and drain voltage, and check it leaves the device in saturation with headroom.",
        "Draw the small-signal equivalent of a common-source stage and compute its gain, input resistance and output resistance, loaded and unloaded.",
        "Predict the -3 dB bandwidth of a stage from its output resistance and load capacitance, and explain why raising the gain lowers the bandwidth by the same factor.",
    ],
    "assessment": (
        "Four quizzes, one guided derivation, two circuits drawn and measured in the "
        "schematic editor, three short Python labs checked by execution, and a capstone "
        "that designs a common-source stage end to end and then analyses what it built."
    ),
    "reading": [
        "*Microelectronic Circuits*, Sedra & Smith — chapters 5 and 7, the reference text for this material.",
        "*The Art of Electronics*, Horowitz & Hill — chapter 3, for the practitioner's view of biasing.",
        "*Analysis and Design of Analog Integrated Circuits*, Gray & Meyer — chapter 3, for where this goes next.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The MOSFET in saturation",
            "summary": "One equation, three regions, and the derivative that makes amplification possible.",
            "concepts": [
                "The MOSFET is used here as a three-terminal device: gate, drain and source. The gate sits on an insulating oxide, so at DC **no current flows into it at all** — a fact that removes a whole class of loading calculations from biasing.",
                "An n-channel device conducts once the gate-source voltage passes a threshold $V_{th}$. What matters afterwards is the excess, the **overdrive** $V_{ov} = V_{GS} - V_{th}$.",
                "Three regions. Cut-off, $V_{GS} < V_{th}$: no drain current. Triode, $V_{DS} < V_{ov}$: $I_D = k(V_{ov}V_{DS} - V_{DS}^2/2)$, and the device behaves like a resistor. Saturation, $V_{DS} \\ge V_{ov}$: $I_D = \\tfrac{1}{2}kV_{ov}^2$, and the device behaves like a current source.",
                "$k = k'(W/L)$ is the device transconductance parameter, in A/V². It bundles the process and the drawn width and length into one number. Throughout this course $k = 2$ mA/V² and $V_{th} = 1.0$ V.",
                "In saturation $I_D$ depends on $V_{GS}$ and almost not at all on $V_{DS}$. Amplification lives entirely in that first dependence, and the second one being weak is what makes the drain a useful place to hang a resistor.",
                "**Transconductance** is the slope of that dependence: $g_m = \\partial I_D/\\partial V_{GS} = kV_{ov} = 2I_D/V_{ov} = \\sqrt{2kI_D}$. Three ways of writing one number, in amps per volt — siemens. At $I_D = 1$ mA this device gives $g_m = 2$ mA/V.",
                "The weak residual dependence on $V_{DS}$ is **channel-length modulation**: $I_D = \\tfrac{1}{2}kV_{ov}^2(1 + \\lambda V_{DS})$. Its consequence is a finite output resistance $r_o = 1/(\\lambda I_D) = V_A/I_D$. With $V_A = 45$ V and $I_D = 1$ mA, $r_o = 45$ kΩ.",
                "$g_m r_o$ is the **intrinsic gain**: the most this device can deliver in a common-source stage, whatever you hang on the drain. Here it is 90.",
            ],
            "quiz": {
                "title": "Regions, the square law and the slope",
                "minutes": 9,
                "questions": [
                    {
                        "q": "An n-channel MOSFET has $V_{th} = 1.0$ V. Its gate sits at 2.5 V above the source and its drain at 0.8 V above the source. Which region is it in?",
                        "opts": ["cut-off", "saturation", "triode", "it cannot be decided without $k$"],
                        "a": 2,
                        "why": r'''
The overdrive is $V_{ov} = 2.5 - 1.0 = 1.5$ V, and $V_{DS} = 0.8$ V is *below* that, so
the device is in triode. The common error is to look only at $V_{GS} > V_{th}$, see that
the device is on, and call it saturation — but being on and being saturated are
different tests. Saturation needs $V_{DS} \ge V_{ov}$ as well, and $k$ never enters
either test.
''',
                    },
                    {
                        "q": "The same device ($k = 2$ mA/V², $V_{th} = 1.0$ V) is biased with $V_{GS} = 2.0$ V and $V_{DS} = 5$ V. What is $I_D$?",
                        "opts": ["1.0 mA", "2.0 mA", "4.0 mA", "0.5 mA"],
                        "a": 0,
                        "why": r'''
$V_{ov} = 1.0$ V and $V_{DS}$ is comfortably above it, so the square law applies:
$I_D = \tfrac{1}{2}kV_{ov}^2 = \tfrac{1}{2}(2\text{ mA/V}^2)(1.0)^2 = 1.0$ mA. Answering
2.0 mA is forgetting the factor of one half — worth fixing now, because it propagates
straight into $g_m$ and from there into every gain in the course. This 1 mA operating
point is the one every later module uses.
''',
                    },
                    {
                        "q": "The gate voltage on that device is raised until $V_{ov}$ doubles, from 1.0 V to 2.0 V. What happens to $I_D$ and to $g_m$?",
                        "opts": [
                            "both double",
                            "$I_D$ doubles, $g_m$ quadruples",
                            "$I_D$ quadruples, $g_m$ stays put",
                            "$I_D$ quadruples, $g_m$ doubles",
                        ],
                        "a": 3,
                        "why": r'''
$I_D \propto V_{ov}^2$, so it goes up four times; $g_m = kV_{ov}$ is linear in the
overdrive, so it only doubles. That mismatch is the central economic fact of analogue
design: transconductance is bought with current, but at a rate that gets worse the
harder you push. Writing $g_m = \sqrt{2kI_D}$ says the same thing — four times the
current buys twice the $g_m$.
''',
                    },
                    {
                        "q": "Two devices are biased at the same $I_D = 1$ mA. Device A has $k = 2$ mA/V²; device B is ten times wider, so $k = 20$ mA/V². Which has the larger $g_m$?",
                        "opts": [
                            "device A, because a narrow device is more efficient",
                            "device B",
                            "they are identical, because $g_m$ depends only on $I_D$",
                            "it depends on $V_{DS}$",
                        ],
                        "a": 1,
                        "why": r'''
$g_m = \sqrt{2kI_D}$, so at equal current the wider device wins by $\sqrt{10} \approx 3.2$
times. Read the other way, $g_m = 2I_D/V_{ov}$: device B reaches 1 mA at an overdrive
of only 0.316 V rather than 1.0 V, and a smaller overdrive for the same current is
exactly what a larger $g_m$ means. "Identical, because $g_m$ depends only on $I_D$" is the common misreading — $g_m$
depends on the current *and* on the device.
''',
                    },
                    {
                        "q": "$r_o = V_A/I_D$ with $V_A = 45$ V. A designer halves the bias current to 0.5 mA. What happens to the intrinsic gain $g_m r_o$?",
                        "opts": [
                            "it halves",
                            "it is unchanged",
                            "it rises by a factor of about 1.41",
                            "it falls by a factor of about 1.41",
                        ],
                        "a": 2,
                        "why": r'''
$r_o$ doubles to 90 kΩ, while $g_m = \sqrt{2kI_D}$ falls only by $\sqrt{2}$, to 1.414
mA/V. The product therefore *rises* by $\sqrt{2}$, from 90 to 127. Low current is good
for gain and bad for speed, which is the trade module 4 makes quantitative. Answering
"unchanged" assumes the two effects cancel exactly; they do not, because one is linear
in current and the other is a square root.
''',
                    },
                    {
                        "q": "Why does the DC gate current being zero matter for the bias divider you are about to design?",
                        "opts": [
                            "the divider's output voltage is its unloaded value, so the simple ratio formula is exact",
                            "the divider can be left out entirely",
                            "the divider dissipates no power",
                            "it does not matter; the gate loads the divider like any other input",
                        ],
                        "a": 0,
                        "why": r'''
A voltage divider only sags when something draws current from its output, and the gate
draws none. So $V_G = V_{DD}R_2/(R_1+R_2)$ exactly, and the megohm resistors that would
be useless anywhere else are perfectly usable here. The divider still draws its own
current from the supply, which is why it still costs power — and why the build exercise
puts a budget on it.
''',
                    },
                ],
            },
            "derive": {
                "title": "Where $g_m$ comes from, and its three faces",
                "minutes": 12,
                "vars": ["I_D", "V_GS", "V_th", "V_ov", "k", "g_m"],
                "brief": r'''
The whole of small-signal analysis rests on one derivative. Start from the saturation
square law

$$I_D = \tfrac{1}{2}k V_{ov}^{2}$$

and work out how much the drain current moves when the gate moves. Then write the
answer three ways, because in practice you know a different one of $V_{ov}$, $k$ and
$I_D$ on different days.
''',
                "steps": [
                    {
                        "prompt": "The overdrive is what the gate has to spare above the threshold. Write $V_{ov}$ in terms of $V_{GS}$ and $V_{th}$.",
                        "answer": "V_{GS} - V_{th}",
                        "hint": "It is a definition, not a result: the gate-source voltage minus the threshold.",
                        "deconstruct": [
                            "Below $V_{th}$ the channel does not exist and no current flows.",
                            "Everything above $V_{th}$ is what drives the current, so subtract the threshold off.",
                        ],
                    },
                    {
                        "prompt": "Substitute that into the square law. Write $I_D$ in terms of $k$, $V_{GS}$ and $V_{th}$.",
                        "given": "Start from $I_D = \\tfrac{1}{2}k V_{ov}^{2}$.",
                        "answer": "\\frac{k}{2}(V_{GS} - V_{th})^{2}",
                        "hint": "Replace $V_{ov}$ with the expression you just wrote, and keep the whole bracket squared.",
                        "deconstruct": [
                            "The square applies to the entire overdrive, not just to $V_{GS}$.",
                            "$\\tfrac{1}{2}k$ can equally be written $k/2$; both are accepted.",
                        ],
                    },
                    {
                        "prompt": "Transconductance is $g_m = \\partial I_D / \\partial V_{GS}$. Differentiate that expression and write $g_m$ in terms of $k$ and $V_{ov}$.",
                        "answer": "k V_{ov}",
                        "hint": "The chain rule on $(V_{GS}-V_{th})^2$ brings down a 2, which cancels the one half. The inner derivative is 1.",
                        "deconstruct": [
                            "$\\frac{d}{dV_{GS}}\\left[\\frac{k}{2}(V_{GS}-V_{th})^2\\right] = \\frac{k}{2}\\cdot 2(V_{GS}-V_{th})$.",
                            "And $V_{GS}-V_{th}$ is the overdrive.",
                        ],
                    },
                    {
                        "prompt": "In a working amplifier you set the current, not the overdrive. Use $I_D = \\tfrac{1}{2}kV_{ov}^{2}$ to eliminate $k$, and write $g_m$ in terms of $I_D$ and $V_{ov}$.",
                        "answer": "\\frac{2 I_D}{V_{ov}}",
                        "hint": "Rearrange the square law for $k$, then substitute into $g_m = kV_{ov}$.",
                        "deconstruct": [
                            "From the square law, $k = 2I_D/V_{ov}^{2}$.",
                            "Multiply by $V_{ov}$ and one power of the overdrive cancels.",
                        ],
                    },
                    {
                        "prompt": "Now eliminate the overdrive instead, and write $g_m$ in terms of $k$ and $I_D$.",
                        "answer": "\\sqrt{2 k I_D}",
                        "hint": "The square law gives $V_{ov} = \\sqrt{2I_D/k}$. Put that into $g_m = kV_{ov}$ and tidy the roots.",
                        "deconstruct": [
                            "$g_m = k\\sqrt{2I_D/k}$.",
                            "Take the $k$ inside the root: $\\sqrt{k^2 \\cdot 2I_D/k} = \\sqrt{2kI_D}$.",
                        ],
                    },
                ],
                "closing": r'''
Three expressions, one quantity. The middle one, $g_m = 2I_D/V_{ov}$, is the one to
carry around: it says that for a fixed current, transconductance is bought by lowering
the overdrive — that is, by making the device wider. The last one says that for a fixed
device, transconductance only grows as the square root of the current you spend. Both
statements are about to become design constraints rather than algebra.
''',
            },
            "lab": {
                "title": "The device, as four functions",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
Write the device model down once, correctly, and every later module can call it.

- `region(v_gs, v_ds)` returns the string `'cut-off'`, `'triode'` or `'saturation'`.
  The boundary case $V_{DS} = V_{ov}$ counts as saturation.
- `drain_current(v_gs, v_ds)` returns $I_D$ in amperes, using whichever expression the
  region calls for. Call `region` rather than repeating its tests.
- `transconductance(i_d)` returns $g_m$ in siemens at that drain current.
- `output_resistance(i_d)` returns $r_o$ in ohms at that drain current.

The device constants are already defined at the top of the file, and every function
takes them as defaults so a test can override one. The three expressions you need are:

```text
cut-off      I_D = 0
triode       I_D = k (V_ov V_DS - V_DS^2 / 2)
saturation   I_D = k V_ov^2 / 2
```

`transconductance` may use any of the three forms from the derivation; they agree.
''',
                "files": [{"name": "main.py", "content": r'''
"""The MOSFET, as a terminal model: which region, how much current, and the slope."""

import math

K = 2e-3      # device transconductance parameter, A/V^2
V_TH = 1.0    # threshold voltage, V
V_A = 45.0    # Early voltage, V


def region(v_gs, v_ds, v_th=V_TH):
    """'cut-off', 'triode' or 'saturation' for these terminal voltages."""
    # TODO: below threshold there is no channel at all.
    # TODO: otherwise compare V_DS with the overdrive.
    return ""


def drain_current(v_gs, v_ds, k=K, v_th=V_TH):
    """Drain current in amperes for these terminal voltages."""
    # TODO: ask region() which expression applies, then use it.
    return 0.0


def transconductance(i_d, k=K):
    """Small-signal transconductance in siemens at this drain current."""
    # TODO: g_m = sqrt(2 k I_D).
    return 0.0


def output_resistance(i_d, v_a=V_A):
    """Small-signal output resistance in ohms at this drain current."""
    # TODO: r_o = V_A / I_D.
    return 0.0


if __name__ == "__main__":
    print("at V_GS = 2.0 V, V_DS = 5 V:", region(2.0, 5.0))
    i = drain_current(2.0, 5.0)
    print("drain current:", i, "A")
    print("g_m:", transconductance(i), "S")
    print("r_o:", output_resistance(i), "ohms")
    print("intrinsic gain:", transconductance(i) * output_resistance(i))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The MOSFET, as a terminal model: which region, how much current, and the slope."""

import math

K = 2e-3      # device transconductance parameter, A/V^2
V_TH = 1.0    # threshold voltage, V
V_A = 45.0    # Early voltage, V


def region(v_gs, v_ds, v_th=V_TH):
    """'cut-off', 'triode' or 'saturation' for these terminal voltages."""
    v_ov = v_gs - v_th
    if v_ov <= 0.0:
        return "cut-off"
    if v_ds < v_ov:
        return "triode"
    return "saturation"


def drain_current(v_gs, v_ds, k=K, v_th=V_TH):
    """Drain current in amperes for these terminal voltages."""
    where = region(v_gs, v_ds, v_th)
    v_ov = v_gs - v_th
    if where == "cut-off":
        return 0.0
    if where == "triode":
        return k * (v_ov * v_ds - v_ds * v_ds / 2.0)
    return k * v_ov * v_ov / 2.0


def transconductance(i_d, k=K):
    """Small-signal transconductance in siemens at this drain current."""
    return math.sqrt(2.0 * k * i_d)


def output_resistance(i_d, v_a=V_A):
    """Small-signal output resistance in ohms at this drain current."""
    return v_a / i_d


if __name__ == "__main__":
    print("at V_GS = 2.0 V, V_DS = 5 V:", region(2.0, 5.0))
    i = drain_current(2.0, 5.0)
    print("drain current:", i, "A")
    print("g_m:", transconductance(i), "S")
    print("r_o:", output_resistance(i), "ohms")
    print("intrinsic gain:", transconductance(i) * output_resistance(i))
'''}],
                "hints": [
                    "`region` is two comparisons in order: first `v_gs - v_th <= 0`, then `v_ds < v_ov`. Anything that survives both is saturation.",
                    "Write the overdrive into a local variable in every function that needs it. Nearly every mistake in this lab is $V_{GS}$ used where $V_{ov}$ was meant.",
                    "The triode expression is `k * (v_ov * v_ds - v_ds ** 2 / 2)`. Check it against saturation at the boundary $V_{DS} = V_{ov}$: both give $kV_{ov}^2/2$, which is why the curve has no kink there.",
                    "`transconductance` is `math.sqrt(2 * k * i_d)`. If you would rather write $kV_{ov}$, recover the overdrive first with `math.sqrt(2 * i_d / k)` — the two agree to the last bit.",
                ],
                "tests": [
                    {"name": "the three regions are told apart", "code": r'''
assert region(0.5, 5.0) == "cut-off", f"0.5 V is below the 1.0 V threshold, got {region(0.5, 5.0)!r}"
assert region(2.0, 0.5) == "triode", \
    f"overdrive 1.0 V, V_DS only 0.5 V, so triode, got {region(2.0, 0.5)!r}"
assert region(2.0, 5.0) == "saturation", \
    f"overdrive 1.0 V, V_DS 5 V, so saturation, got {region(2.0, 5.0)!r}"
assert region(2.0, 1.0) == "saturation", \
    f"V_DS exactly equal to the overdrive counts as saturation, got {region(2.0, 1.0)!r}"
'''},
                    {"name": "the square law gives the 1 mA operating point", "code": r'''
i = drain_current(2.0, 5.0)
assert abs(i - 1e-3) < 1e-12, f"half of 2 mA/V^2 times 1.0 V squared is 1.0 mA, got {i}"
j = drain_current(2.5, 5.0)
assert abs(j - 2.25e-3) < 1e-12, f"an overdrive of 1.5 V gives 2.25 mA, got {j}"
'''},
                    {"name": "in saturation the drain voltage hardly matters", "code": r'''
a = drain_current(2.0, 3.0)
b = drain_current(2.0, 8.0)
assert abs(a - 1e-3) < 1e-12, f"expected 1.0 mA at V_DS = 3 V, got {a}"
assert abs(a - b) < 1e-15, \
    "this model has no channel-length modulation, so I_D must not move with V_DS at all"
assert drain_current(0.9, 5.0) == 0.0, "below threshold the current is exactly zero"
'''},
                    {"name": "triode is a different equation, and it joins on smoothly", "code": r'''
t = drain_current(2.0, 0.5)
assert abs(t - 7.5e-4) < 1e-12, \
    f"2 mA/V^2 times (1.0*0.5 - 0.125) is 0.75 mA, got {t}"
assert t < drain_current(2.0, 5.0), "triode current must be below the saturation value"
edge_lo = drain_current(2.0, 0.999999)
edge_hi = drain_current(2.0, 1.000001)
assert abs(edge_lo - edge_hi) < 1e-8, \
    f"the two expressions must agree at V_DS = V_ov, got {edge_lo} and {edge_hi}"
'''},
                    {"name": "transconductance grows as the square root of current", "code": r'''
g = transconductance(1e-3)
assert abs(g - 2e-3) < 1e-12, f"sqrt(2 * 2e-3 * 1e-3) is 2 mA/V, got {g}"
g4 = transconductance(4e-3)
assert abs(g4 - 4e-3) < 1e-12, f"four times the current is twice the g_m, got {g4}"
v_ov = (2 * 1e-3 / 2e-3) ** 0.5
assert abs(g - 2 * 1e-3 / v_ov) < 1e-12, "g_m = 2 I_D / V_ov must agree with sqrt(2 k I_D)"
'''},
                    {"name": "output resistance falls as current rises", "code": r'''
r = output_resistance(1e-3)
assert abs(r - 45000.0) < 1e-6, f"45 V over 1 mA is 45 kilohms, got {r}"
assert abs(output_resistance(2e-3) - 22500.0) < 1e-6, "twice the current, half the r_o"
intrinsic = transconductance(1e-3) * output_resistance(1e-3)
assert abs(intrinsic - 90.0) < 1e-9, f"the intrinsic gain here is 90, got {intrinsic}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Biasing and the operating point",
            "summary": "Before a transistor can amplify anything it has to be held, steadily, in the right place.",
            "concepts": [
                "An amplifier needs a **DC operating point**: a drain current and a set of terminal voltages that put the device in saturation, with room left over for the signal to swing in both directions.",
                "The operating point is not preliminary housekeeping. $g_m = 2I_D/V_{ov}$, so the bias current *is* the gain setting; get the bias wrong and no amount of small-signal algebra will rescue the stage.",
                "The standard arrangement is **four-resistor bias**: $R_1$ and $R_2$ divide the supply down to the gate, $R_S$ sits between source and ground, $R_D$ between drain and supply.",
                "Because the gate takes no DC current, $V_G = V_{DD}R_2/(R_1+R_2)$ exactly, however large $R_1$ and $R_2$ are. Their size is limited by noise and by leakage, not by loading.",
                "$R_S$ provides **negative feedback at DC**: if $I_D$ drifts up, $V_S = I_DR_S$ rises, $V_{GS} = V_G - V_S$ falls, and the current is pulled back down. This is what makes a bias point survive a device whose $k$ and $V_{th}$ vary from part to part.",
                "Finding the operating point means solving two equations at once: $V_{GS} = V_G - I_DR_S$ and $I_D = \\tfrac{1}{2}k(V_{GS}-V_{th})^2$. Substituting gives a quadratic in $I_D$; the root with $V_{GS} > V_{th}$ is the physical one and the other is an artefact of squaring.",
                "**Headroom**: $V_{DS}$ must remain above $V_{ov}$ at the *bottom* of the output swing, not merely at the quiescent point, or the device slides into triode and the waveform flattens on one side.",
                "$R_D$ sets both the DC drop $I_DR_D$ and, in the next module, the gain. A larger $R_D$ buys gain and spends headroom, and that is the first of the course's several irreducible compromises.",
            ],
            "quiz": {
                "title": "Holding the operating point still",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A gate divider is built from $R_1 = 500$ kΩ and $R_2 = 250$ kΩ across a 12 V supply. What is $V_G$?",
                        "opts": ["8.0 V", "4.0 V", "6.0 V", "it depends on the drain current"],
                        "a": 1,
                        "why": r'''
$V_G = 12 \times 250/750 = 4.0$ V. The gate draws no current, so this is exact — no
loading correction, and no dependence on anything else in the circuit. Answering 8.0 V
is the classic slip of putting $R_1$ in the numerator; the numerator is always the
resistor the output is measured across, which here is the 250 kΩ one.
''',
                    },
                    {
                        "q": "That gate sits at 4.0 V, the source resistor is 2 kΩ, and the drain current settles at 1.0 mA. What is $V_{GS}$?",
                        "opts": ["4.0 V", "1.0 V", "6.0 V", "2.0 V"],
                        "a": 3,
                        "why": r'''
The source is lifted to $V_S = I_DR_S = 1\text{ mA}\times 2\text{ k}\Omega = 2.0$ V, and
$V_{GS} = V_G - V_S = 4.0 - 2.0 = 2.0$ V. Forgetting that lift, and using $V_G$ itself as
$V_{GS}$, is the single most common bias error — and it is the one that source
degeneration exists to exploit, because that lift is exactly the feedback path.
''',
                    },
                    {
                        "q": "Two circuits are biased at 1.0 mA with the same device. Circuit A has no source resistor and a gate held at 2.0 V; circuit B has $R_S = 2$ kΩ and a gate at 4.0 V. A batch of transistors arrives with $V_{th}$ 0.2 V higher than nominal. What happens?",
                        "opts": [
                            "A falls to 0.64 mA while B falls only to 0.92 mA",
                            "both fall to 0.64 mA, because it is the same device",
                            "A is unaffected; B falls",
                            "both are unaffected, because $V_{th}$ does not appear in the square law",
                        ],
                        "a": 0,
                        "why": r'''
In A the overdrive drops straight from 1.0 V to 0.8 V, and current goes as the square:
$1.0 \times 0.8^2 = 0.64$ mA, a 36% collapse. In B the source resistor fights back — as
the current falls, $V_S$ falls, which restores some overdrive — and the current only
reaches 0.920 mA, a drop of 8.0%. Same device, same nominal bias, four and a half times
less sensitivity. This is the whole argument for $R_S$, and you will reproduce both
numbers in the lab.
''',
                    },
                    {
                        "q": "In a four-resistor bias, which resistor has no effect at all on the drain current (in the ideal saturation model used here)?",
                        "opts": ["$R_1$", "$R_2$", "$R_D$", "$R_S$"],
                        "a": 2,
                        "why": r'''
$R_D$. The drain current is set by the gate-source loop — $V_G$, $R_S$ and the device —
and in saturation $I_D$ does not depend on $V_{DS}$. $R_D$ therefore only decides where
the drain voltage lands, and hence how much headroom and how much gain you get. The one
caveat is the obvious one: make $R_D$ large enough to drag the drain below $V_S+V_{ov}$
and the device leaves saturation, at which point this reasoning stops applying.
''',
                    },
                    {
                        "q": "$V_{DD} = 12$ V, $I_D = 1$ mA, $V_S = 2$ V, $V_{ov} = 1$ V. What is the largest $R_D$ that still leaves the device in saturation at the quiescent point?",
                        "opts": ["5 kΩ", "9 kΩ", "12 kΩ", "10 kΩ"],
                        "a": 1,
                        "why": r'''
Saturation needs $V_D \ge V_S + V_{ov} = 3$ V, so the drop across $R_D$ can be at most
$12 - 3 = 9$ V, giving $R_D \le 9$ kΩ. Note this is the limit at the *quiescent* point
with no signal — leave any room for the output to swing downwards and the usable
maximum is considerably smaller. Answering 12 kΩ ignores the source lift and the
overdrive together.
''',
                    },
                    {
                        "q": "Why is the quadratic for $I_D$ solved with the root that gives $V_{GS} > V_{th}$, rather than the other one?",
                        "opts": [
                            "the other root is always negative",
                            "either root works; the choice is a convention",
                            "the other root is larger, and larger currents are unphysical",
                            "the other root implies an overdrive below zero, where the square law does not apply",
                        ],
                        "a": 3,
                        "why": r'''
Squaring the relation $I_D = \tfrac{1}{2}k(V_G - I_DR_S - V_{th})^2$ throws away the sign
of the bracket, so the algebra happily returns a solution in which $V_{GS}$ has fallen
*below* threshold — where the real device is cut off and the equation you solved is not
the one that applies. For the worked circuit the roots are 1.00 mA and 2.25 mA, and the
second implies $V_{GS} = -0.5$ V. Always substitute a root back and check it satisfies
the assumption you made to get it.
''',
                    },
                ],
            },
            "build": {
                "title": "A four-resistor bias for 1 mA",
                "minutes": 28,
                "brief": r'''
Bias the course device — $k = 2$ mA/V², $V_{th} = 1.0$ V — at **1.00 mA** from a 12 V
supply.

The schematic solver is linear and has no transistors in it. That is not an obstacle
here, because at the operating point the transistor's drain-source path *is* a current
source: 1 mA flows in at the drain and out at the source, and no equation in a bias
calculation asks it for anything else. The canvas therefore opens with a 1 mA current
source already placed, standing in for the device, with its **+ pin as the drain**.

Your job is to surround it with the four resistors.

## The specification

- the source terminal sits at **2.00 V** above ground,
- $V_{GS}$ is **2.00 V**, which is what this device needs for 1.00 mA,
- the drain sits at **7.00 V**, leaving 5 V across the device,
- the divider draws between **10 µA and 50 µA** from the supply — enough to be
  insensitive to leakage, little enough not to dominate the supply current.

Put the probe on the **gate** node, so the checks can read $V_G$.

## How to work it out

Take the four resistors in turn and each one is a single division. $R_S$ follows from
the source voltage and the current through it. $R_D$ follows from the drop the supply
has to lose to reach 7 V. The gate voltage follows from $V_{GS}$ and the source
voltage — remember the gate sits *above* the source. Then choose the divider's total
resistance from the current budget, and split it in the ratio $V_G : V_{DD}$.

Nothing here is graded on layout. Any drawing that produces these voltages and stays
inside the current budget passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "I", "x": 13, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 11},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [13, 2]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "I", "x": 13, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p4", "kind": "R", "x": 7, "y": 3, "rot": 1, "value": 500000},
                        {"id": "p5", "kind": "R", "x": 7, "y": 6, "rot": 1, "value": 250000},
                        {"id": "p6", "kind": "GND", "x": 7, "y": 9},
                        {"id": "p7", "kind": "OUT", "x": 9, "y": 5},
                        {"id": "p8", "kind": "R", "x": 13, "y": 3, "rot": 1, "value": 5000},
                        {"id": "p9", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 2000},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [13, 2]},
                        {"a": [7, 4], "b": [7, 5]},
                        {"a": [7, 7], "b": [7, 9]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [13, 7], "b": [13, 8]},
                        {"a": [13, 10], "b": [13, 11]},
                    ],
                },
                "checks": [
                    {"name": "the supply feeds the transistor's 1 mA through a drain resistor", "code": r'''
c.assert(c.count('V') === 1, 'Exactly one supply — the 12 V rail. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
c.assert(c.count('I') === 1,
  'One current source, standing in for the transistor at its operating point. Found ' + c.count('I') + '.');
c.close(c.values('I')[0], 1e-3, 0.01, 'the drain current the current source represents');
/* the two parts above come with the canvas; this is the first thing the learner has to
   draw. Until R_D joins the rail to the drain the supply delivers nothing at all, so
   asserting that it carries at least the drain current is a real measurement rather
   than a restatement of what is already on the screen. */
const cur = c.dc().currents;
const isup = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(isup >= 1e-3 * 0.99,
  'The 1 mA has to reach the drain from the supply, through R_D. The supply is ' +
  'delivering only ' + (isup * 1e6).toFixed(1) + ' µA, so the drain branch is not ' +
  'connected to the rail.');
'''},
                    {"name": "the gate sits 2.00 V above the source", "code": r'''
const q = c.net.parts.filter(function (p) { return p.kind === 'I'; })[0];
c.assert(q, 'The current source standing in for the transistor has gone missing.');
const v = c.dc().v;
const vd = v[q.n1], vs = v[q.n2];
c.assert(vd > vs,
  'The current source is upside down: its + pin is the drain and must end up above the ' +
  'source pin. Measured ' + vd.toFixed(2) + ' V at the + pin and ' + vs.toFixed(2) +
  ' V at the other.');
c.close(c.vout() - vs, 2.0, 0.02,
  'V_GS — the probed gate node minus the source node. The gate divider has to allow for ' +
  'the source sitting 2 V up');
'''},
                    {"name": "the source is at 2.00 V and the drain at 7.00 V", "code": r'''
const q = c.net.parts.filter(function (p) { return p.kind === 'I'; })[0];
const v = c.dc().v;
c.close(v[q.n2], 2.0, 0.02, 'the source voltage, which is I_D times R_S');
c.close(v[q.n1], 7.0, 0.02, 'the drain voltage, which is 12 V minus I_D times R_D');
c.assert(v[q.n1] - v[q.n2] >= 1.0,
  'V_DS must stay above the 1 V overdrive or the device is not in saturation; measured ' +
  (v[q.n1] - v[q.n2]).toFixed(2) + ' V.');
'''},
                    {"name": "the divider draws between 10 µA and 50 µA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1,
  'The supply current has to mean one thing, so this exercise wants exactly one part ' +
  'carrying a solved-for current — the 12 V source. Found ' + ids.length + '.');
const isup = Math.abs(cur[ids[0]]);
/* the supply feeds the drain branch (1 mA, fixed by the current source) and the
   divider, so whatever is left over is the divider's own current */
const idiv = isup - 1e-3;
c.assert(idiv >= 10e-6 * 0.98,
  'The divider must carry at least 10 µA; this one carries ' + (idiv * 1e6).toFixed(1) +
  ' µA, which leaves it at the mercy of leakage.');
c.assert(idiv <= 50e-6 * 1.02,
  'The divider may draw at most 50 µA; this one draws ' + (idiv * 1e6).toFixed(1) + ' µA.');
'''},
                ],
                "hints": [
                    "$R_S = V_S/I_D = 2.0/0.001 = 2$ kΩ. Draw it from the current source's lower pin down to a ground symbol.",
                    "$R_D$ has to drop $12 - 7 = 5$ V while carrying the same 1 mA, so it is 5 kΩ. It goes from the supply rail down to the current source's + pin.",
                    "The gate must sit at $V_S + V_{GS} = 2.0 + 2.0 = 4.0$ V. That is one third of the supply, so the divider splits 2:1 with the larger resistor on top.",
                    "Pick the divider total from the budget: 12 V across 750 kΩ draws 16 µA, comfortably inside 10–50 µA. Splitting 750 kΩ in the ratio 2:1 gives 500 kΩ on top and 250 kΩ below.",
                    "Put the probe on the node between the two divider resistors, not on the supply rail — the checks read $V_{GS}$ as the probe voltage minus the source voltage.",
                ],
            },
            "lab": {
                "title": "Designing a bias point, and checking it holds",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Two directions through the same circuit: design, then analysis.

- `design_bias(vdd, i_d, v_s, v_d, i_div)` returns the tuple `(r_d, r_s, r1, r2)` for a
  four-resistor bias that puts `i_d` through the device with the source at `v_s`, the
  drain at `v_d`, and `i_div` flowing in the divider.
- `bias_point(vdd, r_d, r_s, r1, r2)` goes the other way: given the four resistors, work
  out what the circuit actually does, and return `(i_d, v_gs, v_s, v_d)`.
- `saturated(v_gs, v_ds)` returns `True` when those terminal voltages leave the device
  in saturation.

`design_bias` is four divisions and a ratio. The order that works is: $R_S$ from $V_S$
and $I_D$; $R_D$ from the supply drop; $V_{ov} = \sqrt{2I_D/k}$ and then
$V_G = V_S + V_{th} + V_{ov}$; finally the divider total from $V_{DD}/I_{div}$, split so
that $R_2/(R_1+R_2) = V_G/V_{DD}$.

`bias_point` is the harder one, because $I_D$ and $V_{GS}$ each depend on the other.
Substituting $V_{GS} = V_G - I_DR_S$ into the square law gives

```text
(k Rs^2 / 2) I^2  -  (k Rs (Vg - Vth) + 1) I  +  (k (Vg - Vth)^2 / 2)  =  0
```

Solve it with the quadratic formula and keep the root whose $V_{GS}$ is above
threshold. Guard the case $R_S = 0$ separately: the quadratic degenerates, and the
answer is just the square law at $V_{GS} = V_G$.
''',
                "files": [{"name": "main.py", "content": r'''
"""Four-resistor bias: design it, then find out what it really does."""

import math

K = 2e-3      # A/V^2
V_TH = 1.0    # V


def design_bias(vdd, i_d, v_s, v_d, i_div, k=K, v_th=V_TH):
    """Return (r_d, r_s, r1, r2) for the bias network this specification asks for."""
    # TODO: r_s from v_s and i_d; r_d from the supply drop and i_d.
    # TODO: v_g = v_s + v_th + sqrt(2 i_d / k), then split vdd / i_div in that ratio.
    return (0.0, 0.0, 0.0, 0.0)


def bias_point(vdd, r_d, r_s, r1, r2, k=K, v_th=V_TH):
    """Return (i_d, v_gs, v_s, v_d) actually produced by these four resistors."""
    # TODO: v_g is the unloaded divider output — the gate draws no current.
    # TODO: solve the quadratic for i_d and keep the root with v_gs above threshold.
    return (0.0, 0.0, 0.0, 0.0)


def saturated(v_gs, v_ds, v_th=V_TH):
    """True when these terminal voltages leave the device in saturation."""
    # TODO: compare v_ds with the overdrive, and check the device is on at all.
    return False


if __name__ == "__main__":
    r_d, r_s, r1, r2 = design_bias(12.0, 1e-3, 2.0, 7.0, 16e-6)
    print("designed:", r_d, r_s, r1, r2)
    i_d, v_gs, v_s, v_d = bias_point(12.0, r_d, r_s, r1, r2)
    print("built:", i_d, "A,  V_GS", v_gs, "V,  V_S", v_s, "V,  V_D", v_d, "V")
    print("in saturation?", saturated(v_gs, v_d - v_s))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Four-resistor bias: design it, then find out what it really does."""

import math

K = 2e-3      # A/V^2
V_TH = 1.0    # V


def design_bias(vdd, i_d, v_s, v_d, i_div, k=K, v_th=V_TH):
    """Return (r_d, r_s, r1, r2) for the bias network this specification asks for."""
    r_s = v_s / i_d
    r_d = (vdd - v_d) / i_d
    v_ov = math.sqrt(2.0 * i_d / k)
    v_g = v_s + v_th + v_ov
    total = vdd / i_div
    r2 = total * v_g / vdd
    r1 = total - r2
    return (r_d, r_s, r1, r2)


def bias_point(vdd, r_d, r_s, r1, r2, k=K, v_th=V_TH):
    """Return (i_d, v_gs, v_s, v_d) actually produced by these four resistors."""
    v_g = vdd * r2 / (r1 + r2)
    excess = v_g - v_th

    if r_s == 0.0:
        i_d = 0.0 if excess <= 0.0 else 0.5 * k * excess * excess
    else:
        a = 0.5 * k * r_s * r_s
        b = -(k * r_s * excess + 1.0)
        c = 0.5 * k * excess * excess
        disc = b * b - 4.0 * a * c
        root = math.sqrt(max(disc, 0.0))
        candidates = [(-b - root) / (2.0 * a), (-b + root) / (2.0 * a)]
        physical = [x for x in candidates if x >= 0.0 and v_g - x * r_s > v_th]
        i_d = min(physical) if physical else 0.0

    v_s = i_d * r_s
    return (i_d, v_g - v_s, v_s, vdd - i_d * r_d)


def saturated(v_gs, v_ds, v_th=V_TH):
    """True when these terminal voltages leave the device in saturation."""
    v_ov = v_gs - v_th
    return v_ov > 0.0 and v_ds >= v_ov


if __name__ == "__main__":
    r_d, r_s, r1, r2 = design_bias(12.0, 1e-3, 2.0, 7.0, 16e-6)
    print("designed:", r_d, r_s, r1, r2)
    i_d, v_gs, v_s, v_d = bias_point(12.0, r_d, r_s, r1, r2)
    print("built:", i_d, "A,  V_GS", v_gs, "V,  V_S", v_s, "V,  V_D", v_d, "V")
    print("in saturation?", saturated(v_gs, v_d - v_s))
'''}],
                "hints": [
                    "In `design_bias`, `total = vdd / i_div` is the divider's whole resistance, and `r2 = total * v_g / vdd` is the share of it that has to sit below the gate. `r1` is whatever is left.",
                    "The gate voltage in `design_bias` is `v_s + v_th + v_ov`, not `v_th + v_ov`. The source is not at ground, and forgetting that is the error the build exercise is built around.",
                    "In `bias_point`, compute `excess = v_g - v_th` once and use it in all three quadratic coefficients — `a = 0.5*k*r_s**2`, `b = -(k*r_s*excess + 1)`, `c = 0.5*k*excess**2`.",
                    "Both roots come back positive here, so filter them by `v_g - i*r_s > v_th` and take the smaller survivor. For the worked circuit the roots are 1.00 mA and 2.25 mA, and the second implies a gate-source voltage of −0.5 V.",
                    "`saturated` needs two conditions, not one: the device must be on (`v_gs > v_th`) *and* `v_ds >= v_gs - v_th`.",
                ],
                "tests": [
                    {"name": "the design reproduces the circuit from the build exercise", "code": r'''
r_d, r_s, r1, r2 = design_bias(12.0, 1e-3, 2.0, 7.0, 16e-6)
assert abs(r_s - 2000.0) < 1e-6, f"2.0 V at 1 mA is 2 kilohms, got {r_s}"
assert abs(r_d - 5000.0) < 1e-6, f"a 5 V drop at 1 mA is 5 kilohms, got {r_d}"
assert abs(r1 - 500000.0) < 1e-3, f"expected 500 k on top, got {r1}"
assert abs(r2 - 250000.0) < 1e-3, f"expected 250 k below, got {r2}"
'''},
                    {"name": "analysing that design gives back what was asked for", "code": r'''
r_d, r_s, r1, r2 = design_bias(12.0, 1e-3, 2.0, 7.0, 16e-6)
i_d, v_gs, v_s, v_d = bias_point(12.0, r_d, r_s, r1, r2)
assert abs(i_d - 1e-3) < 1e-9, f"the design asked for 1.00 mA, the circuit gives {i_d}"
assert abs(v_gs - 2.0) < 1e-6, f"expected V_GS of 2.00 V, got {v_gs}"
assert abs(v_s - 2.0) < 1e-6, f"expected the source at 2.00 V, got {v_s}"
assert abs(v_d - 7.0) < 1e-6, f"expected the drain at 7.00 V, got {v_d}"
'''},
                    {"name": "it works on a different supply too", "code": r'''
r_d, r_s, r1, r2 = design_bias(9.0, 1e-3, 1.0, 6.0, 15e-6)
assert abs(r_s - 1000.0) < 1e-6, f"1.0 V at 1 mA is 1 kilohm, got {r_s}"
assert abs(r_d - 3000.0) < 1e-6, f"a 3 V drop at 1 mA is 3 kilohms, got {r_d}"
i_d, v_gs, v_s, v_d = bias_point(9.0, r_d, r_s, r1, r2)
assert abs(i_d - 1e-3) < 1e-9, f"expected 1.00 mA from the 9 V design, got {i_d}"
assert abs(v_d - 6.0) < 1e-6, f"expected the drain at 6.00 V, got {v_d}"
'''},
                    {"name": "the quadratic keeps the physical root", "code": r'''
i_d, v_gs, v_s, v_d = bias_point(12.0, 5000.0, 2000.0, 500e3, 250e3)
assert abs(i_d - 1e-3) < 1e-9, \
    f"the roots are 1.00 mA and 2.25 mA; only the first keeps V_GS above threshold, got {i_d}"
assert v_gs > 1.0, f"the chosen root must leave the device on, and V_GS came out {v_gs}"
'''},
                    {"name": "the source resistor is what holds the current still", "code": r'''
nominal = bias_point(12.0, 5000.0, 2000.0, 500e3, 250e3)[0]
shifted = bias_point(12.0, 5000.0, 2000.0, 500e3, 250e3, v_th=1.2)[0]
assert abs(nominal - 1e-3) < 1e-9, f"expected 1.00 mA nominally, got {nominal}"
assert abs(shifted - 9.203306688776089e-4) < 1e-9, \
    f"with a 0.2 V threshold shift the degenerated circuit gives 0.9203 mA, got {shifted}"
bare = bias_point(12.0, 5000.0, 0.0, 500e3, 100e3)[0]
bare_shift = bias_point(12.0, 5000.0, 0.0, 500e3, 100e3, v_th=1.2)[0]
assert abs(bare - 1e-3) < 1e-9, f"the undegenerated circuit is also 1.00 mA nominally, got {bare}"
assert abs(bare_shift - 6.4e-4) < 1e-9, \
    f"without R_S the same shift takes it to 0.64 mA, got {bare_shift}"
assert abs(shifted - nominal) / nominal < 0.10, "degenerated: less than 10% drift"
assert abs(bare_shift - bare) / bare > 0.30, "undegenerated: more than 30% drift"
'''},
                    {"name": "the saturation test needs both conditions", "code": r'''
assert saturated(2.0, 5.0) is True, "overdrive 1 V, V_DS 5 V: saturated"
assert saturated(2.0, 1.0) is True, "V_DS exactly at the overdrive still counts"
assert saturated(2.0, 0.5) is False, "V_DS below the overdrive is triode, not saturation"
assert saturated(0.5, 5.0) is False, "below threshold the device is off, not saturated"
i_d, v_gs, v_s, v_d = bias_point(12.0, 10000.0, 2000.0, 500e3, 250e3)
assert not saturated(v_gs, v_d - v_s), \
    "with R_D at 10 k the drain lands on the source voltage, which is not saturation"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "The small-signal model and common-source gain",
            "summary": "Linearise about the operating point and the transistor becomes two components.",
            "concepts": [
                "**Small-signal analysis** splits every voltage and current into a DC operating point plus a small deviation, then keeps only the terms that are linear in the deviation. The bias problem and the signal problem separate completely, and each becomes easy.",
                "The linearised device is two components and nothing else: a voltage-controlled current source $i_d = g_mv_{gs}$ from drain to source, in parallel with a resistor $r_o$.",
                "In the small-signal circuit **every DC supply is a short to ground**. A fixed voltage carries no signal, so $V_{DD}$ is signal ground and $R_D$ runs from the drain to ground, in parallel with $r_o$.",
                "Common-source gain, with the source held at signal ground: $A_v = -g_m(r_o \\parallel R_D \\parallel R_L)$. For this stage at 1 mA with $R_D = 5$ kΩ that is $-2\\text{ mA/V}\\times 4.5\\text{ k}\\Omega = -9.0$.",
                "The minus sign is physical, not bookkeeping: more gate voltage means more drain current, and more current through $R_D$ means a *lower* drain voltage. A common-source stage always inverts.",
                "The output resistance looking into the drain is $r_o \\parallel R_D$. Push $R_D$ to infinity — replace it with a current source — and the gain approaches the intrinsic gain $g_mr_o = 90$, which is the ceiling for one device at this current.",
                "The input resistance is $R_1 \\parallel R_2$, here 167 kΩ. The gate itself takes nothing, but the bias divider is still hanging on the input, and a source with any output resistance of its own will divide against it.",
                "Leaving $R_S$ unbypassed changes the gain to approximately $-g_mR_D/(1+g_mR_S)$ — here $-2.0$, against the $-g_mR_D = -10$ the same approximation gives with $R_S$ bypassed. Five times less gain, and what it buys is a gain of about $-R_D/R_S$ that barely depends on $g_m$, and therefore barely on the device. That trade is the seed of feedback.",
                "The model is a linearisation, and it is accurate only while the signal is small compared with the overdrive. Push a 1 V peak into a stage biased with $V_{ov} = 1$ V and the square law's curvature shows up as distortion.",
            ],
            "sandbox": {
                "title": "The gain is where the curve ends up",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 1.6, "wn": 4},
                "brief": r'''
This module computes one number: how far the drain moves for a given movement of the
gate. What it does not compute is *when* the drain gets there. Step the input and the
output does not jump — it slides, and this sandbox is a picture of that slide.

The right-hand plot is the response to a step input, scaled so the final value is 1.
The left-hand plot shows where the poles of that response sit in the complex plane.
The circuit as this module draws it has no capacitors in it at all, so it has no poles
and settles instantly. Built out of real components it has two: a slow one at the drain
and a faster one at the gate. That is the **overdamped** end of this picture — two real
poles, no overshoot, one of them much slower than the other — and module 4 puts a
number on the slow one and treats the fast one as a correction.

The sliders are the two standard parameters of a second-order response, $\zeta$
(damping) and $\omega_n$. They are not amplifier parameters — module 4 connects the
two — so for now read the shapes rather than the numbers.
''',
                "notice": [
                    "At the opening values, $\\zeta = 1.6$ and $\\omega_n = 4$, the left-hand plot shows two amber dots on the horizontal axis, at about −1.4 and −11.4, and the caption reads 'both poles real'. The right-hand curve rises smoothly onto the dashed line at 1 with no overshoot at all. That dashed line is the gain this module computes; everything else on the screen is module 4's problem.",
                    "The two dots are eight times apart. The one near the origin is the **dominant** pole and it is the one deciding the shape — a stage with one slow node and one fast node settles as if the fast node were not there. That is the assumption behind every hand calculation of bandwidth you will do.",
                    "Push $\\omega_n$ up to 12 with $\\zeta$ still at 1.6. The faster pole slides off the left edge of the plot entirely, the dominant one moves out to about −4.2, and the curve keeps exactly the same shape — only the numbers on the time axis shrink, from 1.9 s of plot to 0.6 s. Three times the pole frequency, three times the speed.",
                    "Put $\\omega_n$ back to 4 and bring $\\zeta$ down to 0.35. The dots leave the real axis, become a complex pair, and the readout reports 30.9% overshoot with settling in 2.86 s. A single common-source stage on its own cannot do this — it needs a second energy store and some feedback around both — but it is exactly what happens when an amplifier like this one is put inside a feedback loop, which is a later course.",
                    "Set $\\zeta$ to exactly 1.00 and the two dots land on top of each other at −4, and the readout says 'Critically damped: the fastest approach with no overshoot at all'. To the left of that value you gain speed and pay in ringing; to the right you gain nothing and lose speed.",
                ],
            },
            "quiz": {
                "title": "Reading the small-signal circuit",
                "minutes": 9,
                "questions": [
                    {
                        "q": "In the small-signal equivalent circuit of a common-source stage, what happens to the $V_{DD}$ rail?",
                        "opts": [
                            "it stays as a voltage source in the drawing",
                            "it is replaced by an open circuit",
                            "it becomes a current source of value $I_D$",
                            "it becomes a short to ground",
                        ],
                        "a": 3,
                        "why": r'''
A short to ground. Small-signal analysis asks only about *changes*, and a DC supply by
definition does not change — the small-signal voltage on it is zero, which is what
being connected to signal ground means. So $R_D$, drawn from the drain to $V_{DD}$,
appears in the small-signal circuit as a resistor from the drain to ground, sitting in
parallel with $r_o$. Answering "open circuit" is the usual confusion with what happens
to a *capacitor* at DC.
''',
                    },
                    {
                        "q": "This stage has $g_m = 2$ mA/V, $r_o = 45$ kΩ and $R_D = 5$ kΩ, with the source at signal ground. What is the unloaded voltage gain?",
                        "opts": ["−10.0", "−9.0", "−90", "+9.0"],
                        "a": 1,
                        "why": r'''
$A_v = -g_m(r_o \parallel R_D) = -2\text{ mA/V}\times 4.5\text{ k}\Omega = -9.0$. Answering
−10.0 is forgetting $r_o$, which costs 10% here; answering −90 is using $r_o$ alone and
forgetting $R_D$, which would be right only if the drain load were an ideal current
source. And the sign is not decoration: this stage inverts.
''',
                    },
                    {
                        "q": "A load of 45 kΩ is now connected to the drain through a large coupling capacitor. What happens to the gain?",
                        "opts": [
                            "nothing, because the capacitor blocks the load",
                            "it rises in magnitude, because there is more resistance at the drain",
                            "it falls in magnitude, to about −8.2",
                            "it falls to zero",
                        ],
                        "a": 2,
                        "why": r'''
The capacitor blocks DC but is a short at signal frequencies, so the load appears in
parallel with $r_o$ and $R_D$: $45\text{k}\parallel 5\text{k}\parallel 45\text{k} = 4.09$
kΩ, and the gain falls from −9.0 to −8.18. Every extra resistance connected in parallel
*reduces* the total, and gain at the drain is proportional to that total — which is why
a common-source stage feeding anything low-impedance loses most of its gain, and why
buffers exist.
''',
                    },
                    {
                        "q": "What sets the input resistance of this stage?",
                        "opts": [
                            "$R_1 \\parallel R_2$, the bias divider",
                            "infinity, because the gate draws no current",
                            "$r_o \\parallel R_D$",
                            "$1/g_m$",
                        ],
                        "a": 0,
                        "why": r'''
The gate itself does draw no current, so the *device* contributes nothing to the input
admittance — but the bias divider is still connected to that node, and to a signal
source it looks like $R_1 \parallel R_2$, which is 167 kΩ here. This is a good example of
a specification set entirely by the components you added rather than by the device you
chose, and it is why bias dividers in high-impedance stages are made of megohms.
''',
                    },
                    {
                        "q": "The 2 kΩ source resistor is left unbypassed, so it appears in the small-signal circuit. Taking $r_o$ as infinite, what does the gain become?",
                        "opts": ["−9.0, unchanged", "−0.4", "−4.5", "−2.0"],
                        "a": 3,
                        "why": r'''
$A_v \approx -g_mR_D/(1+g_mR_S) = -10/(1+4) = -2.0$. The stage has given away a factor of
five of gain. What it bought is a gain of approximately $-R_D/R_S$ whenever $g_mR_S \gg
1$ — a ratio of two resistors, which barely depends on the transistor at all. Trading
raw gain for a predictable, device-independent gain is the central bargain of feedback,
and this is its simplest instance.
''',
                    },
                    {
                        "q": "Why does the small-signal model stop being accurate for large signals?",
                        "opts": [
                            "because $r_o$ changes with frequency",
                            "because it is a linearisation of a square law, valid only while the signal is small compared with the overdrive",
                            "because the supply cannot deliver enough current",
                            "because $g_m$ is negative for large signals",
                        ],
                        "a": 1,
                        "why": r'''
$g_m$ is the *slope* of the $I_D$–$V_{GS}$ curve at one point, and that curve is a
parabola. A signal that moves the gate appreciably compared with the 1 V overdrive
visits parts of the parabola with a different slope, so the gain is not the same on the
two half-cycles, and the output is distorted. Amplitude limits and supply headroom
matter too — but they cut the signal off rather than bend it, and they are a different
failure with a different-looking waveform.
''',
                    },
                ],
            },
            "lab": {
                "title": "Small-signal parameters and the gain they give",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
The small-signal circuit is mostly parallel resistances, so write that once and reuse
it.

- `parallel(*ohms)` returns the resistance of any number of resistors in parallel.
- `small_signal(i_d)` returns `(gm, ro)` for the course device at that drain current.
- `cs_gain(gm, ro, r_d, r_load=None)` returns the common-source voltage gain, **signed**.
  `r_load=None` means nothing is connected to the output.
- `stage_resistances(ro, r_d, r1, r2)` returns `(r_in, r_out)` for the whole stage.
- `degenerated_gain(gm, r_d, r_s)` returns the gain with the source resistor left
  unbypassed, using the $-g_mR_D/(1+g_mR_S)$ approximation that ignores $r_o$.

Use the conductance form in `parallel` so it works for one resistor or five. Every
other function is then one line built on it.
''',
                "files": [{"name": "main.py", "content": r'''
"""The small-signal common-source stage: parameters, gain, and the two impedances."""

import math

K = 2e-3      # A/V^2
V_A = 45.0    # V


def parallel(*ohms):
    """Resistance of any number of resistors sharing the same two nodes."""
    # TODO: add the conductances, then invert the sum.
    return 0.0


def small_signal(i_d, k=K, v_a=V_A):
    """Return (gm, ro) for the course device at this drain current."""
    # TODO: gm = sqrt(2 k I_D); ro = V_A / I_D.
    return (0.0, 0.0)


def cs_gain(gm, ro, r_d, r_load=None):
    """Signed voltage gain of a common-source stage with the source at signal ground."""
    # TODO: -gm times whatever resistance the drain sees.
    return 0.0


def stage_resistances(ro, r_d, r1, r2):
    """Return (r_in, r_out) for the stage: what the source sees, what the load sees."""
    # TODO: the gate takes no current, but the bias divider is still there.
    return (0.0, 0.0)


def degenerated_gain(gm, r_d, r_s):
    """Gain with the source resistor unbypassed, ignoring ro."""
    # TODO: -gm r_d / (1 + gm r_s).
    return 0.0


if __name__ == "__main__":
    gm, ro = small_signal(1e-3)
    print("gm", gm, "S,  ro", ro, "ohms,  intrinsic gain", gm * ro)
    print("unloaded gain:", cs_gain(gm, ro, 5000.0))
    print("with a 45k load:", cs_gain(gm, ro, 5000.0, 45000.0))
    print("r_in, r_out:", stage_resistances(ro, 5000.0, 500e3, 250e3))
    print("source resistor unbypassed:", degenerated_gain(gm, 5000.0, 2000.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The small-signal common-source stage: parameters, gain, and the two impedances."""

import math

K = 2e-3      # A/V^2
V_A = 45.0    # V


def parallel(*ohms):
    """Resistance of any number of resistors sharing the same two nodes."""
    return 1.0 / sum(1.0 / r for r in ohms)


def small_signal(i_d, k=K, v_a=V_A):
    """Return (gm, ro) for the course device at this drain current."""
    return (math.sqrt(2.0 * k * i_d), v_a / i_d)


def cs_gain(gm, ro, r_d, r_load=None):
    """Signed voltage gain of a common-source stage with the source at signal ground."""
    if r_load is None:
        return -gm * parallel(ro, r_d)
    return -gm * parallel(ro, r_d, r_load)


def stage_resistances(ro, r_d, r1, r2):
    """Return (r_in, r_out) for the stage: what the source sees, what the load sees."""
    return (parallel(r1, r2), parallel(ro, r_d))


def degenerated_gain(gm, r_d, r_s):
    """Gain with the source resistor unbypassed, ignoring ro."""
    return -gm * r_d / (1.0 + gm * r_s)


if __name__ == "__main__":
    gm, ro = small_signal(1e-3)
    print("gm", gm, "S,  ro", ro, "ohms,  intrinsic gain", gm * ro)
    print("unloaded gain:", cs_gain(gm, ro, 5000.0))
    print("with a 45k load:", cs_gain(gm, ro, 5000.0, 45000.0))
    print("r_in, r_out:", stage_resistances(ro, 5000.0, 500e3, 250e3))
    print("source resistor unbypassed:", degenerated_gain(gm, 5000.0, 2000.0))
'''}],
                "hints": [
                    "`parallel` is `1.0 / sum(1.0 / r for r in ohms)`. With one argument it returns that argument, which is what makes the rest of the file short.",
                    "`cs_gain` needs the `r_load=None` case handled separately — `parallel(ro, r_d, None)` would raise. An `if` is fine, or build the list of resistances first and drop the `None`.",
                    "A useful self-check on `cs_gain`: the answer must be negative, and its magnitude must never exceed $g_mr_o = 90$, whatever $R_D$ you pass.",
                    "`stage_resistances` returns the pair in the order (input, output). The input resistance has nothing to do with the transistor; the output resistance has nothing to do with the divider.",
                ],
                "tests": [
                    {"name": "parallel handles one, two and three resistors", "code": r'''
assert abs(parallel(1000.0) - 1000.0) < 1e-9, "one resistor in parallel with nothing is itself"
p = parallel(5000.0, 45000.0)
assert abs(p - 4500.0) < 1e-9, f"5k and 45k in parallel is 4.5k, got {p}"
q = parallel(45000.0, 5000.0, 45000.0)
assert abs(q - 4090.90909090909) < 1e-6, f"expected about 4090.9 ohms, got {q}"
assert q < 5000.0, "a parallel total must be below the smallest part"
'''},
                    {"name": "the operating point fixes gm and ro", "code": r'''
gm, ro = small_signal(1e-3)
assert abs(gm - 2e-3) < 1e-12, f"expected 2 mA/V at 1 mA, got {gm}"
assert abs(ro - 45000.0) < 1e-6, f"expected 45 kilohms at 1 mA, got {ro}"
gm4, ro4 = small_signal(4e-3)
assert abs(gm4 - 4e-3) < 1e-12, f"four times the current is twice the gm, got {gm4}"
assert abs(ro4 - 11250.0) < 1e-6, f"four times the current is a quarter of the ro, got {ro4}"
'''},
                    {"name": "the unloaded gain is minus nine", "code": r'''
gm, ro = small_signal(1e-3)
a = cs_gain(gm, ro, 5000.0)
assert a < 0, f"a common-source stage inverts, so the gain is negative; got {a}"
assert abs(a + 9.0) < 1e-9, f"-2 mA/V times 4.5 k is -9.0, got {a}"
'''},
                    {"name": "a load pulls the gain down", "code": r'''
gm, ro = small_signal(1e-3)
loaded = cs_gain(gm, ro, 5000.0, 45000.0)
assert abs(loaded + 8.18181818181818) < 1e-7, f"expected about -8.182, got {loaded}"
assert abs(loaded) < abs(cs_gain(gm, ro, 5000.0)), "loading can only reduce the gain"
'''},
                    {"name": "the intrinsic gain is the ceiling", "code": r'''
gm, ro = small_signal(1e-3)
huge = cs_gain(gm, ro, 1e12)
assert abs(huge + 90.0) < 0.01, \
    f"with an ideal current-source load the gain approaches -gm*ro = -90, got {huge}"
assert abs(cs_gain(gm, ro, 5000.0)) < 90.0, "no choice of R_D can beat the intrinsic gain"
'''},
                    {"name": "the two stage resistances come from different places", "code": r'''
gm, ro = small_signal(1e-3)
r_in, r_out = stage_resistances(ro, 5000.0, 500e3, 250e3)
assert abs(r_in - 166666.66666666666) < 1e-6, f"500k in parallel with 250k, got {r_in}"
assert abs(r_out - 4500.0) < 1e-9, f"45k in parallel with 5k, got {r_out}"
'''},
                    {"name": "degeneration trades gain for predictability", "code": r'''
gm, _ = small_signal(1e-3)
d = degenerated_gain(gm, 5000.0, 2000.0)
assert abs(d + 2.0) < 1e-9, f"-10 over (1 + 4) is -2.0, got {d}"
assert abs(degenerated_gain(gm, 5000.0, 0.0) + 10.0) < 1e-9, \
    "with no source resistor the approximation collapses to -gm*R_D"
strong = degenerated_gain(gm, 5000.0, 20000.0)
assert abs(strong + 5000.0 / 20000.0) < 0.02, \
    f"with gm*R_S well above 1 the gain approaches -R_D/R_S = -0.25, got {strong}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Bandwidth and the gain you pay for it",
            "summary": "One capacitor at the drain, and the gain you just designed acquires an expiry date.",
            "concepts": [
                "Every node has capacitance to ground — the next stage's gate, the device's own drain capacitance, the wiring. At the drain, that total $C_L$ works against the output resistance $R_{out} = r_o \\parallel R_D$ and forms a single-pole low-pass filter.",
                "The gain therefore becomes frequency dependent: $|A(f)| = A_0/\\sqrt{1+(f/f_{3dB})^2}$ with $f_{3dB} = 1/(2\\pi R_{out}C_L)$.",
                "Below the corner the gain is flat at $A_0$; at the corner it is 3 dB down; above it the gain falls at **20 dB per decade** — a factor of ten in gain for every factor of ten in frequency. One pole, one slope.",
                "The **gain-bandwidth product** is what happens when you multiply the two: $A_0f_{3dB} = g_mR_{out}\\times 1/(2\\pi R_{out}C_L) = g_m/(2\\pi C_L)$. $R_{out}$ cancels.",
                "That cancellation is the whole point. Changing $R_D$ moves gain and bandwidth in opposite directions by the same factor; it does not buy you any more of the product. For this stage at 1 mA with $C_L = 354$ pF, the product is fixed at 900 kHz.",
                "To move the product you must change the device or the capacitance: raise $g_m$, or lower $C_L$. And $g_m = \\sqrt{2kI_D}$, so doubling the bias current buys only $\\sqrt{2}$ of bandwidth while doubling the power — the second irreducible compromise of the course.",
                "In the time domain the same pole is an exponential settling with $\\tau = R_{out}C_L = 1/(2\\pi f_{3dB})$. The 10–90% rise time is $2.2\\tau$, which is the familiar $0.35/f_{3dB}$.",
                "A real stage has more than one pole — the input network makes another — and the design habit worth forming now is to identify the **dominant** one, the slowest, and treat the rest as a correction.",
            ],
            "sandbox": {
                "title": "Gain, bandwidth, and the line between them",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 20, "zeta": 0.71, "K": 10},
                "brief": r'''
The top plot is gain in decibels against frequency, the bottom is phase, and both axes
of frequency are logarithmic. A gain $G$ in decibels is $20\log_{10}G$, so a gain of 10
is 20 dB and a gain of 100 is 40 dB.

This visualiser draws a *second*-order response, with the corner at $\omega_n$ and a
damping $\zeta$. Leave $\zeta$ at 0.71 and the corner is the −3 dB point to within half
a percent, which is exactly the reading you want. The stage in this module has only one
pole, so its slope above the corner is half as steep as what you see here — the last
thing to notice below makes that difference visible.

$K$ is the low-frequency gain. Work the two sliders $K$ and $\omega_n$ against each
other and watch what stays put.
''',
                "notice": [
                    "At the opening values the top plot is flat at 20 dB out to about $\\omega = 5$, and the amber dot marking the corner sits at 17 dB — three decibels below the flat part. That is the definition of the −3 dB bandwidth, drawn.",
                    "Take $K$ from 10 up to 20 and the whole magnitude curve lifts by 6 dB, to 26 dB, without the corner moving at all. Gain and bandwidth are independent *sliders here* — and that is precisely what a real stage cannot do, because in a real stage the same $g_m$ appears in both.",
                    "Leave $K$ at 20 and drag the corner $\\omega_n$ from 20 down to 5. The flat part stays at 26 dB and the whole roll-off slides a factor of four to the left. In the amplifier this is what a larger $R_D$, or a larger load capacitance, does to you.",
                    "Put $\\omega_n$ back to 20 and look at the lower plot. The phase is near 0° at low frequency, passes through exactly −90° at the corner whatever $\\zeta$ is, and heads for −180° far above it. Note the phase bends long before the gain does: at $\\omega = 2$, a decade below the corner, the magnitude is still flat to within a hundredth of a decibel while the phase has already reached −8°.",
                    "One decade above the corner, at $\\omega = 200$ with $\\omega_n = 20$, the magnitude has fallen 40 dB below the flat part — because this picture has two poles. The single-pole output network of this module falls only 20 dB per decade, so read the *shape* here and halve the slope.",
                ],
            },
            "quiz": {
                "title": "What a pole costs",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A stage has $R_{out} = 4.5$ kΩ and a load capacitance of 354 pF. What is its −3 dB bandwidth?",
                        "opts": ["100 kHz", "628 kHz", "16 kHz", "1.6 MHz"],
                        "a": 0,
                        "why": r'''
$f_{3dB} = 1/(2\pi R_{out}C_L) = 1/(2\pi \times 4500 \times 354\text{ pF}) = 100$ kHz. The
answer 628 kHz is $1/(R_{out}C_L)$ without the $2\pi$ — that is the corner in radians per
second, $\omega_{3dB}$, and mixing the two up is worth a factor of 6.28 in any
specification you quote. Keep hertz and radians per second visibly apart in your
working.
''',
                    },
                    {
                        "q": "That stage has a gain of 9.0. The designer doubles $R_D$ to raise the gain. Roughly what happens to gain and bandwidth?",
                        "opts": [
                            "gain doubles, bandwidth unchanged",
                            "both roughly double",
                            "gain roughly doubles, bandwidth roughly halves",
                            "gain unchanged, bandwidth halves",
                        ],
                        "a": 2,
                        "why": r'''
$R_{out}$ appears in the gain as a multiplier and in the bandwidth as a divisor, so
raising it lifts one and lowers the other by the same factor — their product is
untouched. ("Roughly", because $r_o$ in parallel means $R_{out}$ does not quite double
when $R_D$ does.) A designer who needs both more gain and more bandwidth cannot get
them from $R_D$; the only ways out are a bigger $g_m$ or a smaller $C_L$.
''',
                    },
                    {
                        "q": "The gain-bandwidth product of this single-pole stage is:",
                        "opts": [
                            "$1/(2\\pi R_{out}C_L)$",
                            "$g_m/(2\\pi C_L)$",
                            "$g_mR_{out}$",
                            "$g_mr_o$",
                        ],
                        "a": 1,
                        "why": r'''
Multiply $A_0 = g_mR_{out}$ by $f_{3dB} = 1/(2\pi R_{out}C_L)$ and $R_{out}$ cancels,
leaving $g_m/(2\pi C_L)$. $1/(2\pi R_{out}C_L)$ is the bandwidth alone and $g_mR_{out}$ the gain alone —
the point of the product is precisely that it contains neither $R_D$ nor $r_o$. For this
stage: $2\text{ mA/V}/(2\pi\times 354\text{ pF}) = 900$ kHz, which is $9.0\times 100$ kHz,
as it must be.
''',
                    },
                    {
                        "q": "A specification demands twice the gain-bandwidth product from the same device and the same load capacitance. What has to change?",
                        "opts": [
                            "double $R_D$",
                            "halve $R_D$",
                            "double the supply voltage",
                            "raise the bias current by a factor of four",
                        ],
                        "a": 3,
                        "why": r'''
The product is $g_m/(2\pi C_L)$, and with the device and $C_L$ fixed the only handle is
$g_m = \sqrt{2kI_D}$ — which grows as the *square root* of current, so four times the
current for twice the product. Four times the power for one doubling is a poor exchange
rate, and it is why the alternative answers in real design are a wider device or a
lighter load rather than more current. Changing $R_D$ moves gain and bandwidth in
opposite directions and cannot move their product at all.
''',
                    },
                    {
                        "q": "The same stage is used to pass a step rather than a sine. Its bandwidth is 100 kHz. Roughly how long does the output take to go from 10% to 90%?",
                        "opts": ["10 µs", "1.6 µs", "3.5 µs", "0.35 µs"],
                        "a": 2,
                        "why": r'''
$t_r \approx 0.35/f_{3dB} = 0.35/10^5 = 3.5$ µs. It comes from the same pole seen in the
time domain: $\tau = 1/(2\pi f_{3dB}) = 1.59$ µs, and a 10–90% transition on an exponential
takes $2.2\tau$. The answer 1.6 µs is $\tau$ itself, which is the time to reach 63%, not
90%. One pole, two languages, one number underneath.
''',
                    },
                ],
            },
            "build": {
                "title": "The output pole, drawn and measured",
                "minutes": 30,
                "brief": r'''
Here is the small-signal circuit itself, on the canvas, with real numbers in it.

The stage from module 2 is biased at 1 mA, so $g_m = 2$ mA/V and $r_o = 45$ kΩ. Drive
it with a test signal of **10 mV** at the gate. The transistor's contribution to the
small-signal circuit is then a current source of $g_mv_{gs} = 2\text{ mA/V}\times
10\text{ mV} = 20$ µA, and that source is already on the canvas, with its **+ pin at the
drain** so that it pulls current out of the drain node — which is why this stage
inverts.

Everything else at the drain is yours to draw. Remember that in a small-signal circuit
the supply rail is signal ground, so both $R_D$ and $r_o$ run from the drain node to
ground, in parallel.

## What the finished circuit must do

- $r_o$ = 45 kΩ, the transistor's own output resistance, connected from the drain to
  ground. It is part of the device, not an optional extra, and leaving it out is the
  most common way to overestimate a gain.
- a low-frequency gain of **9.0**, so the probed drain node reads 90 mV of amplitude
  for the 10 mV of input the current source represents,
- a −3 dB bandwidth of **100 kHz**, set by a capacitor from the drain to ground,
- a single pole, so the gain falls by a factor of ten per decade above the corner.

## Working it out

The gain fixes the resistance at the drain: $|A_0| = g_mR_{out}$. From $R_{out}$ and the
45 kΩ that is already spoken for, $R_D$ follows. Then the bandwidth fixes the capacitor
through $f_{3dB} = 1/(2\pi R_{out}C_L)$. Type the capacitor value with a suffix — `354p`
is understood, and so is `3.54e-10`.

The checks measure gain, phase, corner frequency and slope. Any drawing that produces
them passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "I", "x": 3, "y": 3, "rot": 1, "value": 2e-05},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "OUT", "x": 5, "y": 2},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [5, 2]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "I", "x": 3, "y": 3, "rot": 1, "value": 2e-05},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "OUT", "x": 5, "y": 2},
                        {"id": "p3", "kind": "R", "x": 7, "y": 3, "rot": 1, "value": 45000},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 6},
                        {"id": "p5", "kind": "R", "x": 11, "y": 3, "rot": 1, "value": 5000},
                        {"id": "p6", "kind": "GND", "x": 11, "y": 6},
                        {"id": "p7", "kind": "C", "x": 15, "y": 3, "rot": 1, "value": 3.5367765131532294e-10},
                        {"id": "p8", "kind": "GND", "x": 15, "y": 6},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [15, 2]},
                        {"a": [7, 4], "b": [7, 6]},
                        {"a": [11, 4], "b": [11, 6]},
                        {"a": [15, 4], "b": [15, 6]},
                    ],
                },
                "checks": [
                    {"name": "the transistor's current source and its output resistance are both there", "code": r'''
c.assert(c.count('I') === 1,
  'One current source: the g_m v_gs generator. Found ' + c.count('I') + '.');
c.close(c.values('I')[0], 20e-6, 0.01,
  'the small-signal drain current, g_m times the 10 mV test input');
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 45000) <= 900 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'r_o = 45 kΩ belongs to the transistor and must run from the probed drain node to ' +
   'ground. A 45 kΩ resistor sitting somewhere else in the drawing is not the same circuit.');
'''},
                    {"name": "the low-frequency gain is 9.0, and inverting", "code": r'''
const g = c.gain(1000);
c.close(g, 0.09, 0.02,
  'the output amplitude well below the corner — 10 mV in at a gain of 9 is 90 mV out');
const ph = Math.abs(c.phase(1000));
c.assert(ph > 170,
  'A common-source stage inverts, so the output should be about 180° out of phase with ' +
  'the input. Measured ' + c.phase(1000).toFixed(1) + '°, which suggests the current ' +
  'source is the wrong way up.');
'''},
                    {"name": "the bandwidth is 100 kHz", "code": r'''
const f = c.corner(100, 1e9);
c.close(f, 1e5, 0.05,
  'the -3 dB bandwidth, where the gain has fallen to 1/sqrt(2) of its low-frequency value');
'''},
                    {"name": "one pole, so 20 dB per decade above the corner", "code": r'''
const a = c.gain(1e6);
const b = c.gain(1e7);
const slope = a / b;
c.assert(slope > 8.5 && slope < 11.5,
  'Above the corner a single pole loses a factor of ten of gain per decade. Between ' +
  '1 MHz and 10 MHz this circuit loses a factor of ' + slope.toFixed(2) +
  ', which is not one pole.');
'''},
                ],
                "hints": [
                    "A gain of 9.0 from $g_m = 2$ mA/V needs $R_{out} = 9.0/0.002 = 4.5$ kΩ at the drain.",
                    "That 4.5 kΩ is $r_o \\parallel R_D$ with $r_o = 45$ kΩ, so $1/R_D = 1/4500 - 1/45000$ and $R_D = 5$ kΩ.",
                    "Then $C_L = 1/(2\\pi R_{out}f_{3dB}) = 1/(2\\pi \\times 4500 \\times 10^5) = 354$ pF. Type it as `354p`.",
                    "All three components go from the drain node to ground, in parallel with one another. Give each its own ground symbol rather than drawing a long return wire — every ground symbol is the same node.",
                    "If the gain comes out at 0.9 V rather than 90 mV, the drain node is seeing 45 kΩ alone: $R_D$ is missing, or is not actually connected to ground.",
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A common-source design tool",
        "runtime": "python",
        "minutes": 150,
        "brief": r'''
Everything in this course has been one calculation at a time. A working engineer needs
them joined up: a supply voltage and a specification go in, a set of resistors comes
out, and then the same tool says what that set of resistors will actually do — including
the ways it fails.

You are going to write that tool. It is not long. What it demands is that the bias
model, the small-signal model and the frequency response agree with each other, because
the checks feed the output of each stage into the next.

## The device, as data

A device is a dict, so the tool is not tied to the one this course has used:

```text
DEV = {"k": 2e-3, "v_th": 1.0, "v_a": 45.0}
```

A bias network is a dict too: `{"r_d": ..., "r_s": ..., "r1": ..., "r2": ...}`.

## What you are building, in `main.py`

1. `parallel(*ohms)` — the resistance of any number of parallel resistors.
2. `design_bias(dev, vdd, i_d, v_s, v_d, i_div)` — return the bias dict that meets the
   specification, exactly as in module 2.
3. `operating_point(dev, vdd, r)` — return a dict with keys `i_d`, `v_gs`, `v_ov`,
   `v_s`, `v_d`, `v_ds` and `saturated`, found by solving the bias quadratic.
   **`operating_point` computes the current by assuming saturation, then reports
   whether that assumption survived.** Say so honestly in the `saturated` flag rather
   than silently returning a number from the wrong region — a design tool that lies
   about its own domain of validity is worse than no tool.
4. `small_signal(dev, op)` — return `{"gm": ..., "ro": ...}` at that operating point.
5. `response(dev, vdd, r, r_load, c_load)` — return a dict with `av` (signed voltage
   gain, including $r_o$ and any load resistance), `r_out`, `f_3db` and `gbw`. Take
   `r_load=None` to mean an unloaded output.

   Be careful about which resistance goes where. `r_out` is the stage's own output
   resistance, $r_o \parallel R_D$, and the load is not part of it. But $C_L$ hangs on
   the drain node next to *everything* connected there, load included, so the pole is
   set by the total: $f_{3dB} = 1/(2\pi (r_o \parallel R_D \parallel R_L) C_L)$. Hanging
   a load on the output costs gain and buys back exactly that much bandwidth. The
   gain-bandwidth product is $|A_v|f_{3dB}$, and if your other numbers are right it will
   come out equal to $g_m/(2\pi C_L)$ **whatever you connect to the drain** — which is a
   check you should run on yourself before running the tests.

## Suggested order

`parallel` first, then `design_bias`, which is pure arithmetic. `operating_point` is
the only piece with any subtlety in it — the quadratic, the root selection, and the
$R_S = 0$ special case. Once those two agree with each other, the last two functions
are a handful of lines each.

## What good work looks like here

The tests check numbers. What they cannot check is whether the tool is honest about the
region it is in, so the `saturated` flag is worth more attention than its two lines
suggest. A design that comes back with `saturated: False` has not failed the tool; it
has been correctly reported as a design that does not work.
''',
        "deliverables": [
            "`design_bias`, turning a specification — supply, drain current, source and drain voltages, divider current — into the four resistor values, with the gate voltage derived from the overdrive the device needs.",
            "`operating_point`, solving the bias quadratic for the actual drain current and terminal voltages of a given network, choosing the root that keeps $V_{GS}$ above threshold, and handling $R_S = 0$ without dividing by zero.",
            "The `saturated` flag, computed from $V_{DS}$ against $V_{ov}$ and reported honestly even when it contradicts the assumption the current was computed under.",
            "`small_signal` and the signed gain in `response`, including $r_o$ and any external load, so that the gain never exceeds the intrinsic gain of the device.",
            "`f_3db` and `gbw` in `response`, taking the pole from the total resistance at the drain node — the load included, even though the load is not part of `r_out` — together with a comment in `main.py` recording one design you tried where raising $R_D$ moved the gain and the bandwidth in opposite directions by the same factor.",
        ],
        "constraints": [
            "The standard library only — `math` is all this needs. No NumPy, and nothing that solves circuits for you.",
            "The device parameters must come from the `dev` dict passed in, never from module-level constants. The tests pass a second device with different numbers.",
            "`operating_point` must solve the quadratic. Do not iterate to a fixed point, and do not special-case the values that appear in the tests.",
            "Every returned voltage is in volts, every current in amperes, every resistance in ohms and every frequency in hertz. No millis, no kilos.",
            "`response` must include $r_o$ in the drain resistance. A gain magnitude larger than $g_mr_o$ is a sign it has been left out.",
        ],
        "rubric": [
            {"criterion": "Bias design and analysis", "weight": 30,
             "evidence": "design_bias and operating_point are exact inverses of each other: feeding a designed network back through the analysis returns the requested drain current, source voltage and drain voltage, on more than one supply rail."},
            {"criterion": "Region honesty", "weight": 20,
             "evidence": "The saturation flag is computed from V_DS against the overdrive and correctly reports False for a network whose drain has been pulled down into triode, rather than returning a confident current from the wrong equation."},
            {"criterion": "Small-signal correctness", "weight": 25,
             "evidence": "gm and ro follow the operating point, the gain is signed and inverting, includes ro and any load, and never exceeds the intrinsic gain gm*ro for any choice of drain resistance."},
            {"criterion": "Frequency response and the trade", "weight": 25,
             "evidence": "f_3db follows from the total resistance at the drain node and the load capacitance, and the gain-bandwidth product comes out equal to gm/(2*pi*C_L) both for two different drain resistances and with a load hung on the output — demonstrating the cancellation rather than asserting it."},
        ],
        "hints": [
            "Keep `operating_point` free of small-signal ideas and `small_signal` free of bias ideas. The only thing that crosses between them is `i_d`.",
            "The quadratic coefficients, with `excess = v_g - v_th`: `a = 0.5*k*r_s**2`, `b = -(k*r_s*excess + 1)`, `c = 0.5*k*excess**2`. Filter the two roots by `v_g - i*r_s > v_th` and take the smaller survivor.",
            "For `r_s == 0` the quadratic has no `a` term at all. Return the plain square law at `v_gs = v_g`, and return zero current if the gate is below threshold.",
            "In `response`, build `r_out = parallel(ro, r_d)` and then a second resistance that also folds in `r_load` when it is not `None`. `r_out` is the resistance the *load* would see, so the load itself is not part of it; the second one is what both the gain and the pole are computed from.",
            "A fast self-check before running the tests: `abs(av) * f_3db` must come out the same number for any two drain resistances *and* with a load connected, and that number must equal `gm / (2 * pi * c_load)`. If the loaded product comes out low, `f_3db` is using `r_out` where it should be using the loaded resistance.",
        ],
        "files": [
            {"name": "main.py", "content": r'''
"""A common-source design tool: specification in, resistors out, behaviour back.

Gain and bandwidth traded against each other:
    TODO: record one pair of designs, differing only in R_D, and their gains,
    bandwidths and gain-bandwidth products.
"""

import math

DEV = {"k": 2e-3, "v_th": 1.0, "v_a": 45.0}


def parallel(*ohms):
    """Resistance of any number of resistors sharing the same two nodes."""
    # TODO: add the conductances, then invert.
    return 0.0


def design_bias(dev, vdd, i_d, v_s, v_d, i_div):
    """Return {'r_d', 'r_s', 'r1', 'r2'} meeting this specification."""
    # TODO: r_s and r_d from Ohm's law; v_g from v_s, v_th and the overdrive.
    # TODO: split vdd / i_div between r1 and r2 in the ratio v_g : vdd.
    return {"r_d": 0.0, "r_s": 0.0, "r1": 0.0, "r2": 0.0}


def operating_point(dev, vdd, r):
    """Return the DC operating point of this bias network.

    Keys: i_d, v_gs, v_ov, v_s, v_d, v_ds, saturated.
    """
    # TODO: v_g is the unloaded divider output.
    # TODO: solve the bias quadratic, keeping the root with v_gs above threshold.
    # TODO: report saturated honestly, from v_ds against the overdrive.
    return {"i_d": 0.0, "v_gs": 0.0, "v_ov": 0.0, "v_s": 0.0, "v_d": 0.0,
            "v_ds": 0.0, "saturated": False}


def small_signal(dev, op):
    """Return {'gm', 'ro'} at this operating point."""
    # TODO: gm = sqrt(2 k I_D), ro = V_A / I_D.
    return {"gm": 0.0, "ro": 0.0}


def response(dev, vdd, r, r_load, c_load):
    """Return {'av', 'r_out', 'f_3db', 'gbw'} for this stage."""
    # TODO: work out the operating point, then gm and ro, then the drain resistance.
    # TODO: r_out excludes r_load, but the gain and the pole both include it.
    # TODO: av is negative; f_3db = 1 / (2 pi R C_L) on that loaded R; gbw = |av| * f_3db.
    return {"av": 0.0, "r_out": 0.0, "f_3db": 0.0, "gbw": 0.0}


if __name__ == "__main__":
    r = design_bias(DEV, 12.0, 1e-3, 2.0, 7.0, 16e-6)
    print("designed:", r)
    op = operating_point(DEV, 12.0, r)
    print("operating point:", op)
    print("small signal:", small_signal(DEV, op))
    print("response:", response(DEV, 12.0, r, None, 3.5367765131532294e-10))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A common-source design tool: specification in, resistors out, behaviour back.

Gain and bandwidth traded against each other:
    The 12 V design below has R_D = 5 kΩ, giving R_out = 4.5 kΩ, a gain of -9.00
    and a bandwidth of 100.0 kHz with C_L = 354 pF. Doubling R_D to 10 kΩ gives
    R_out = 8.18 kΩ, a gain of -16.36 and a bandwidth of 55.0 kHz. The gain rose
    by 1.818 and the bandwidth fell by the same 1.818, and both designs report a
    gain-bandwidth product of 900.0 kHz, which is g_m / (2 pi C_L).
"""

import math

DEV = {"k": 2e-3, "v_th": 1.0, "v_a": 45.0}


def parallel(*ohms):
    """Resistance of any number of resistors sharing the same two nodes."""
    return 1.0 / sum(1.0 / x for x in ohms)


def design_bias(dev, vdd, i_d, v_s, v_d, i_div):
    """Return {'r_d', 'r_s', 'r1', 'r2'} meeting this specification."""
    v_ov = math.sqrt(2.0 * i_d / dev["k"])
    v_g = v_s + dev["v_th"] + v_ov
    total = vdd / i_div
    r2 = total * v_g / vdd
    return {"r_d": (vdd - v_d) / i_d, "r_s": v_s / i_d, "r1": total - r2, "r2": r2}


def operating_point(dev, vdd, r):
    """Return the DC operating point of this bias network.

    Keys: i_d, v_gs, v_ov, v_s, v_d, v_ds, saturated.
    """
    k, v_th = dev["k"], dev["v_th"]
    r_s, r_d = r["r_s"], r["r_d"]
    v_g = vdd * r["r2"] / (r["r1"] + r["r2"])
    excess = v_g - v_th

    if excess <= 0.0:
        i_d = 0.0
    elif r_s == 0.0:
        i_d = 0.5 * k * excess * excess
    else:
        a = 0.5 * k * r_s * r_s
        b = -(k * r_s * excess + 1.0)
        c = 0.5 * k * excess * excess
        root = math.sqrt(max(b * b - 4.0 * a * c, 0.0))
        candidates = [(-b - root) / (2.0 * a), (-b + root) / (2.0 * a)]
        physical = [x for x in candidates if x >= 0.0 and v_g - x * r_s > v_th]
        i_d = min(physical) if physical else 0.0

    v_s = i_d * r_s
    v_gs = v_g - v_s
    v_ov = v_gs - v_th
    v_d = vdd - i_d * r_d
    v_ds = v_d - v_s
    return {"i_d": i_d, "v_gs": v_gs, "v_ov": v_ov, "v_s": v_s, "v_d": v_d,
            "v_ds": v_ds, "saturated": v_ov > 0.0 and v_ds >= v_ov}


def small_signal(dev, op):
    """Return {'gm', 'ro'} at this operating point."""
    i_d = op["i_d"]
    if i_d <= 0.0:
        return {"gm": 0.0, "ro": float("inf")}
    return {"gm": math.sqrt(2.0 * dev["k"] * i_d), "ro": dev["v_a"] / i_d}


def response(dev, vdd, r, r_load, c_load):
    """Return {'av', 'r_out', 'f_3db', 'gbw'} for this stage."""
    op = operating_point(dev, vdd, r)
    ss = small_signal(dev, op)
    # the stage's own output resistance: what a load would see looking back in
    r_out = parallel(ss["ro"], r["r_d"])
    # what the gain and the pole actually see: everything hanging on the drain node
    r_signal = r_out if r_load is None else parallel(r_out, r_load)
    av = -ss["gm"] * r_signal
    f_3db = 1.0 / (2.0 * math.pi * r_signal * c_load)
    return {"av": av, "r_out": r_out, "f_3db": f_3db, "gbw": abs(av) * f_3db}


if __name__ == "__main__":
    r = design_bias(DEV, 12.0, 1e-3, 2.0, 7.0, 16e-6)
    print("designed:", r)
    op = operating_point(DEV, 12.0, r)
    print("operating point:", op)
    print("small signal:", small_signal(DEV, op))
    print("response:", response(DEV, 12.0, r, None, 3.5367765131532294e-10))
'''},
        ],
        "tests": [
            {"name": "the design meets its own specification", "code": r'''
r = design_bias(DEV, 12.0, 1e-3, 2.0, 7.0, 16e-6)
assert abs(r["r_s"] - 2000.0) < 1e-6, f"expected R_S of 2 k, got {r['r_s']}"
assert abs(r["r_d"] - 5000.0) < 1e-6, f"expected R_D of 5 k, got {r['r_d']}"
assert abs(r["r1"] - 500000.0) < 1e-3, f"expected 500 k on top, got {r['r1']}"
assert abs(r["r2"] - 250000.0) < 1e-3, f"expected 250 k below, got {r['r2']}"
assert abs(12.0 / (r["r1"] + r["r2"]) - 16e-6) < 1e-12, "the divider must draw the 16 uA asked for"
'''},
            {"name": "analysis inverts design, on two different supplies", "code": r'''
r = design_bias(DEV, 12.0, 1e-3, 2.0, 7.0, 16e-6)
op = operating_point(DEV, 12.0, r)
assert abs(op["i_d"] - 1e-3) < 1e-9, f"expected 1.00 mA back, got {op['i_d']}"
assert abs(op["v_s"] - 2.0) < 1e-6, f"expected the source at 2.00 V, got {op['v_s']}"
assert abs(op["v_d"] - 7.0) < 1e-6, f"expected the drain at 7.00 V, got {op['v_d']}"
assert abs(op["v_gs"] - 2.0) < 1e-6, f"expected V_GS of 2.00 V, got {op['v_gs']}"
assert abs(op["v_ov"] - 1.0) < 1e-6, f"expected an overdrive of 1.00 V, got {op['v_ov']}"
assert op["saturated"] is True, "5 V of V_DS against a 1 V overdrive is saturation"

r9 = design_bias(DEV, 9.0, 1e-3, 1.0, 6.0, 15e-6)
op9 = operating_point(DEV, 9.0, r9)
assert abs(op9["i_d"] - 1e-3) < 1e-9, f"expected 1.00 mA from the 9 V design, got {op9['i_d']}"
assert abs(op9["v_d"] - 6.0) < 1e-6, f"expected the drain at 6.00 V, got {op9['v_d']}"
assert abs(op9["v_ds"] - 5.0) < 1e-6, f"expected V_DS of 5.00 V, got {op9['v_ds']}"
'''},
            {"name": "a second device, with different numbers", "code": r'''
wide = {"k": 20e-3, "v_th": 0.7, "v_a": 20.0}
r = design_bias(wide, 5.0, 2e-3, 0.5, 3.0, 25e-6)
assert abs(r["r_s"] - 250.0) < 1e-6, f"0.5 V at 2 mA is 250 ohms, got {r['r_s']}"
assert abs(r["r_d"] - 1000.0) < 1e-6, f"a 2 V drop at 2 mA is 1 k, got {r['r_d']}"
op = operating_point(wide, 5.0, r)
assert abs(op["i_d"] - 2e-3) < 1e-9, f"expected 2.00 mA back, got {op['i_d']}"
assert abs(op["v_ov"] - 0.4472135954999579) < 1e-9, \
    f"sqrt(2*2e-3/20e-3) is 0.4472 V of overdrive, got {op['v_ov']}"
assert op["saturated"] is True, "2.5 V of V_DS against 0.45 V of overdrive is saturation"
ss = small_signal(wide, op)
assert abs(ss["gm"] - 8.94427190999916e-3) < 1e-9, f"expected 8.94 mA/V, got {ss['gm']}"
assert abs(ss["ro"] - 10000.0) < 1e-6, f"20 V over 2 mA is 10 k, got {ss['ro']}"
'''},
            {"name": "the tool admits when the device has left saturation", "code": r'''
bad = {"r_d": 10000.0, "r_s": 2000.0, "r1": 500e3, "r2": 250e3}
op = operating_point(DEV, 12.0, bad)
assert abs(op["i_d"] - 1e-3) < 1e-9, \
    f"R_D does not change the current in saturation, so it is still 1 mA, got {op['i_d']}"
assert abs(op["v_ds"]) < 1e-6, f"10 k at 1 mA drags the drain onto the source, got V_DS = {op['v_ds']}"
assert op["saturated"] is False, \
    "V_DS of 0 V against a 1 V overdrive is not saturation, whatever the quadratic returned"
off = {"r_d": 5000.0, "r_s": 2000.0, "r1": 1400e3, "r2": 100e3}
op_off = operating_point(DEV, 12.0, off)
assert op_off["i_d"] == 0.0, \
    f"a gate at 0.8 V is below the 1.0 V threshold, so the device is off, got {op_off['i_d']}"
assert op_off["saturated"] is False, "a device that is off is not in saturation"
'''},
            {"name": "the small-signal gain is signed, loaded and capped", "code": r'''
r = design_bias(DEV, 12.0, 1e-3, 2.0, 7.0, 16e-6)
c_l = 3.5367765131532294e-10
res = response(DEV, 12.0, r, None, c_l)
assert res["av"] < 0, f"a common-source stage inverts; got {res['av']}"
assert abs(res["av"] + 9.0) < 1e-6, f"expected a gain of -9.00, got {res['av']}"
assert abs(res["r_out"] - 4500.0) < 1e-6, f"45 k in parallel with 5 k is 4.5 k, got {res['r_out']}"
loaded = response(DEV, 12.0, r, 45000.0, c_l)
assert abs(loaded["av"] + 8.18181818181818) < 1e-6, \
    f"a 45 k load takes the gain to -8.18, got {loaded['av']}"
assert abs(loaded["r_out"] - 4500.0) < 1e-6, \
    "the stage's output resistance is what the load sees, so the load is not part of it"
assert abs(loaded["f_3db"] - 110000.0) < 1.0, \
    ("C_L sees the load too, so 45k||5k||45k = 4.091 k widens the corner to 110.0 kHz. "
     f"Got {loaded['f_3db']} — this is r_out being used where the loaded resistance belongs")
op = operating_point(DEV, 12.0, r)
ss = small_signal(DEV, op)
assert abs(res["av"]) < ss["gm"] * ss["ro"], "no gain may exceed the intrinsic gain"
'''},
            {"name": "bandwidth follows the output resistance", "code": r'''
r = design_bias(DEV, 12.0, 1e-3, 2.0, 7.0, 16e-6)
c_l = 3.5367765131532294e-10
res = response(DEV, 12.0, r, None, c_l)
assert abs(res["f_3db"] - 1e5) < 1.0, f"expected 100.0 kHz, got {res['f_3db']}"
assert abs(res["gbw"] - 9e5) < 10.0, f"9.0 times 100 kHz is 900 kHz, got {res['gbw']}"
half = dict(r)
half["r_d"] = 2500.0
res_half = response(DEV, 12.0, half, None, c_l)
assert res_half["f_3db"] > res["f_3db"], "a smaller R_D must widen the bandwidth"
assert abs(res_half["av"]) < abs(res["av"]), "and cost gain"
'''},
            {"name": "the gain-bandwidth product does not move with R_D", "code": r'''
import math as _m
r = design_bias(DEV, 12.0, 1e-3, 2.0, 7.0, 16e-6)
c_l = 3.5367765131532294e-10
op = operating_point(DEV, 12.0, r)
gm = small_signal(DEV, op)["gm"]
assert gm > 1e-4, f"the operating point must give a real transconductance, got {gm}"
expected = gm / (2 * _m.pi * c_l)
for r_d in (2500.0, 5000.0, 10000.0, 20000.0):
    trial = dict(r)
    trial["r_d"] = r_d
    out = response(DEV, 12.0, trial, None, c_l)
    assert abs(out["gbw"] - expected) < 1.0, \
        f"with R_D = {r_d} the product came out {out['gbw']}, not {expected}"
big = dict(r)
big["r_d"] = 10000.0
a = response(DEV, 12.0, r, None, c_l)
b = response(DEV, 12.0, big, None, c_l)
gain_ratio = abs(b["av"]) / abs(a["av"])
bw_ratio = a["f_3db"] / b["f_3db"]
assert abs(gain_ratio - bw_ratio) < 1e-9, \
    f"gain rose by {gain_ratio} and bandwidth fell by {bw_ratio}; they must match"
for r_l in (45000.0, 4500.0, 1000.0):
    out = response(DEV, 12.0, r, r_l, c_l)
    assert abs(out["gbw"] - expected) < 1.0, \
        (f"with a {r_l} ohm load the product came out {out['gbw']}, not {expected}. "
         "A load takes gain and gives back the same factor of bandwidth, because C_L "
         "sees it too — the product cannot notice it at all")
'''},
        ],
    },
}
