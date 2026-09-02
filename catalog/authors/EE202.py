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
The transistor appears in this course two ways, and the difference is deliberate.

In the linear build exercises it appears the way it appears in an engineer's
notebook: as a current source at DC, and as a current source in parallel with r_o
for small signals. That is not a workaround, it is the model, and it is what every
hand calculation in this subject actually does.

The schematic solver is NOT linear-only, and four places in this file said it was.
src/circuit.js carries a SPICE level-1 MOSFET — cut-off, triode, saturation, a
source/drain swap and (1 + lambda*V_DS) — and an Ebers-Moll bipolar, both solved by
the Newton-Raphson loop the diode already used. The exercises whose titles say
"with the device left in" therefore put the real thing on the canvas, and their
checks read it through c.device() rather than inferring it from node voltages.
Those devices carry the course numbers exactly:

    NMOS   value = k = 2e-3    vth = 1.0    lambda = 1/45   (V_A = 45 V)
    NPN    value = I_S = 1e-14 bf = 100     br = 1

Where the notebook model and the device disagree, the disagreement is the lesson
and both numbers are stated. The hand bias design says 1.000 mA and the device
settles at 1.0202 mA; the gap is the lambda that every hand calculation drops.

Module 9 introduces one bipolar device, and it is kept at the same operating point
for the same reason:

    I_C = 1 mA    V_T = 25 mV    beta = 100    V_A = 45 V

giving g_m = 40 mA/V, r_pi = 2.5 kΩ, r_o = 45 kΩ and an intrinsic gain of 1800, so
that every bipolar number in that module can be read against the MOSFET number
directly above it.
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
        "single capacitor that decides how much bandwidth the gain costs you. From there "
        "it opens out: how much signal the stage will take before it clips or distorts, "
        "what the coupling and bypass capacitors do at the bottom of the band, the two "
        "other ways to wire the same device, what a transistor is worth as a load, the "
        "bipolar version of all of it, the differential pair every op-amp starts with, "
        "and what it costs to drive a real load at the end of the chain. By the end you "
        "can design a common-source stage from a supply voltage and a gain requirement, "
        "and say in advance what it will and will not do."
    ),
    "outcomes": [
        "Place a MOSFET in cut-off, triode or saturation from its terminal voltages, and compute its drain current in each.",
        "Compute transconductance and output resistance at an operating point, in all three equivalent forms, and say which form to reach for when.",
        "Design a four-resistor bias network for a stated drain current, source voltage and drain voltage, and check it leaves the device in saturation with headroom.",
        "Say why the source resistor is there at all: quantify a bias network's immunity to device spread as the loop gain 1 + g_m R_S, and reject a design that reaches the target current with none of it.",
        "Check the notebook model against the device — derive the square law from the channel charge, know that k is mu*C_ox*W/L, and say which of the model's assumptions the number in front of you is relying on.",
        "Draw the small-signal equivalent of a common-source stage and compute its gain, input resistance and output resistance, loaded and unloaded.",
        "Predict the -3 dB bandwidth of a stage from its output resistance and load capacitance, and explain why raising the gain lowers the bandwidth by the same factor.",
        "Place the quiescent drain voltage for maximum symmetric swing, and decide whether clipping or square-law distortion is the limit a given specification runs into first.",
        "Size coupling and bypass capacitors from the resistance each one works against, and identify which of the three low-frequency corners actually sets f_L.",
        "Choose between common-source, common-drain and common-gate from the input and output impedances a situation demands, and compute the gain and the two impedances of each.",
        "Explain what a current mirror copies and how well, and compute the gain and bandwidth of an actively loaded stage from the two output resistances at its drain.",
        "Work in bipolar terms — g_m = I_C/V_T, r_pi = beta/g_m, an intrinsic gain of V_A/V_T — and say where a base current forces a bias design to differ from a MOSFET one.",
        "Analyse a differential pair: the half-circuit gain, the common-mode gain set by the tail resistance, the CMRR they imply, and the input at which the pair fully steers.",
        "Size a class-A output stage from the current its load demands, and account for its efficiency and for the fact that it runs hottest with no signal at all.",
    ],
    "assessment": (
        "Eleven quizzes and six guided derivations; six circuits drawn and measured in "
        "the schematic editor; five short Python labs checked by execution; a symbol "
        "drill, a fill-the-holes listing, a numeric question and a slider target where "
        "the material calls for them; and a capstone that designs a common-source stage "
        "end to end and then analyses what it built."
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
                "The square law is not a postulate. It comes out of one integral along the channel, and the factor of $\\tfrac{1}{2}$ in it is the average of a channel charge that ramps from full at the source to nothing at the drain. The reading in this module does that integral, and gives $k = \\mu C_{ox}(W/L)$ three named parts instead of one measured number.",
            ],
            "read": {
                "title": "Where the square law comes from, and where it stops",
                "minutes": 14,
                "body": r'''
EE201 spends ten modules on one device and never mentions this one. It gives you a
junction, a depletion region, a built-in potential, and drift and diffusion as the two
ways a carrier moves — and then this course opens by announcing
$I_D = \tfrac{1}{2}kV_{ov}^{2}$ as though it had been established somewhere. It has
not been, here or anywhere before here. This reading is the missing rung. Everything it
uses is EE201's: the electrostatics of module 1, the parallel-plate capacitor of module
7, and the drift equation of module 5.

## A capacitor with silicon for a bottom plate

Take a slab of p-type silicon. Grow a thin insulating oxide on it — call it $t_{ox}$
thick — and put a conducting gate on top. That is a capacitor, and its lower plate
happens to be a semiconductor. Everything the MOSFET does follows from what a
semiconductor does when you charge it.

Put the gate slightly positive. The mobile charge in p-type silicon is holes, so they
are pushed down away from the surface, leaving behind the fixed negative acceptor ions
they had been neutralising. A layer with no mobile carriers in it: that is the same
depletion region EE201 built at the pn junction, made here by a voltage on a plate
instead of by two dopings meeting.

Push harder. Once the surface has run out of holes to repel, the only charge left to
attract is electrons, and the field pulls them out of the bulk to the underside of the
oxide. At some gate voltage the surface stops being p-type and becomes n-type — an
**inversion layer**, a skin of electrons on top of p-type silicon. The gate voltage at
which that happens is the **threshold**, $V_{th}$. Two heavily doped n-type wells sunk
into the slab either side of the gate — the source and the drain — now have a conducting
n-channel between them that did not exist a moment ago.

That is the whole device. A gate that cannot pass current because there is an insulator
under it, and a channel whose existence and thickness the gate controls electrostatically.

## The channel charge, in coulombs

Above threshold the oxide is an ordinary parallel-plate capacitor, so use the ordinary
formula. Per unit area of gate,

$$C_{ox} = \frac{\varepsilon_{ox}}{t_{ox}}$$

and every volt of gate drive above the threshold puts $C_{ox}$ coulombs per square metre
into the channel:

$$|Q_n| = C_{ox}\,(V_{GS} - V_{th}) = C_{ox}V_{ov}$$

The overdrive appears here, in its first honest role: not "the excess above threshold"
as a definition, but **the part of the gate voltage that is actually buying channel
charge**. Everything up to $V_{th}$ went on emptying the surface of holes and is spent.

Numbers, so this is a quantity and not a symbol. Silicon dioxide has
$\varepsilon_{ox} = 3.9\varepsilon_0 = 3.45\times10^{-11}$ F/m. A 10 nm oxide therefore
gives

$$C_{ox} = \frac{3.45\times10^{-11}}{10\times10^{-9}} = 3.45\times10^{-3}\,\mathrm{F/m^2}
= 3.45\,\mathrm{fF/\mu m^2}$$

and at one volt of overdrive the channel holds 3.45 femtocoulombs under every square
micron of gate — about 21 500 electrons. Not many. That is why the gate has to be close.

## One integral, and the triode equation falls out

Now put a voltage $V_{DS}$ between drain and source and ask what current flows.

Here is the one subtlety in the whole derivation, and it is worth slowing down for.
Walk along the channel from the source to the drain, at position $y$. The channel is
resistive, so it drops voltage as it carries current: the local channel potential $V(y)$
runs from $0$ at the source to $V_{DS}$ at the drain. But the gate is one piece of metal
at one potential. So the voltage *across the oxide* is not $V_{GS}$ everywhere — it is
$V_{GS} - V(y)$, and it is smallest at the drain end. **The channel is thickest at the
source and thinnest at the drain**, and the local charge is

$$|Q_n(y)| = C_{ox}\left(V_{ov} - V(y)\right)$$

Now EE201's drift equation, which for a sheet of charge $Q_n$ in a channel of width $W$
moving at $v = \mu E$ reads $I_D = W|Q_n|\mu E$, with the field along the channel being
$E = dV/dy$:

$$I_D = W\mu C_{ox}\left(V_{ov} - V(y)\right)\frac{dV}{dy}$$

$I_D$ is the same at every point — nothing leaks out of the channel, because the gate
insulator sees to that. So separate and integrate over the length $L$:

$$I_D\int_0^{L}dy = W\mu C_{ox}\int_0^{V_{DS}}\left(V_{ov} - V\right)\,dV$$

$$I_D = \mu C_{ox}\frac{W}{L}\left(V_{ov}V_{DS} - \frac{V_{DS}^{2}}{2}\right)$$

That is the triode expression from this module's concept list, and it arrived rather
than being announced. Comparing it with the form used throughout the course identifies
the constant that has so far been a single measured number:

$$k = \mu C_{ox}\frac{W}{L} \qquad\text{and}\qquad k' = \mu C_{ox}$$

Put this course's device in: with $\mu = 400\,\mathrm{cm^2/V\,s} = 0.04\,\mathrm{m^2/V\,s}$
and the 10 nm oxide above, $k' = 0.04 \times 3.45\times10^{-3} = 138\,\mathrm{\mu A/V^2}$,
and $k = 2$ mA/V² needs

$$\frac{W}{L} = \frac{2\times10^{-3}}{138\times10^{-6}} = 14.5$$

The course device is a channel about fourteen and a half times wider than it is long.
$W/L$ is the one thing in $k$ a designer chooses; $\mu$ and $C_{ox}$ arrive from the
foundry. When module 1's quiz says device B is "ten times wider", that is $W/L$ going
from 14.5 to 145, and nothing else changing.

## Pinch-off, and where the one-half comes from

Look again at the local charge, $C_{ox}(V_{ov} - V(y))$, at the drain end where
$V(y) = V_{DS}$. As $V_{DS}$ rises, the drain end of the channel gets thinner. At
$V_{DS} = V_{ov}$ it reaches **zero**: the gate no longer has any drive left over at
that end, and the channel closes at the drain. This is **pinch-off**, and it is the
boundary the region test in this module is testing for.

Past that point the integral above cannot be continued — it would ask for a negative
channel charge, which is not a thing. What actually happens is that the channel ends
slightly short of the drain, and the extra $V_{DS} - V_{ov}$ drops across the small
depleted gap, which carriers cross at whatever speed the field gives them. The current
stops growing. Its value is the value the triode expression had reached at the corner,
so put $V_{DS} = V_{ov}$ into it:

$$I_D = \mu C_{ox}\frac{W}{L}\left(V_{ov}^{2} - \frac{V_{ov}^{2}}{2}\right)
      = \frac{1}{2}k V_{ov}^{2}$$

**There is the factor of one half**, and it is not a fudge. It is the average of a
channel charge that falls linearly from $C_{ox}V_{ov}$ at the source to zero at the
drain: the mean of a ramp is half its peak. Anyone who writes $I_D = kV_{ov}^2$ has
priced the channel as though it were as thick at the drain as at the source. The quiz
in this module marks that error; this is the reason it is an error.

## Channel-length modulation, in one sentence

Raise $V_{DS}$ further and the pinched-off gap at the drain grows, by some $\Delta L$.
The part of the channel still carrying by drift is now $L - \Delta L$ long, and
$I_D \propto 1/(L-\Delta L)$, so the current creeps up. Expanding to first order gives
the $(1 + \lambda V_{DS})$ factor, with $\lambda \approx (\Delta L/L)/V_{DS}$.

Two consequences worth carrying. First, $\lambda$ is inversely proportional to $L$ — the
same $\Delta L$ is a smaller fraction of a longer channel — so $V_A = 1/\lambda$ is a
property of the *length* rather than of the process alone, and analogue designers reach
for long devices when they want output resistance. Second, this is a small correction and
every hand bias calculation drops it. The build exercise in module 2 that leaves the
device in shows exactly what dropping it costs: a design worked out for 1.000 mA settles
at 1.0202 mA, 2.02% high, and every voltage in the stage moves with it.

## Where this stops being true

Three places, and the first is not a footnote.

**Velocity saturation.** The integral assumed $v = \mu E$ — carriers going faster in
proportion to the field. Silicon stops obeying that above roughly $4\times10^{6}$ V/m,
where drift velocity flattens off near $10^{5}$ m/s. This course's device is long: with
$L \approx 10\,\mu$m and 5 V across the channel the field is $5\times10^{5}$ V/m, safely
under. A modern 0.1 µm channel with 1 V on it sits at $10^{7}$ V/m, well over — and there
$I_D$ becomes *linear* in $V_{ov}$, not square, and $g_m \approx WC_{ox}v_{sat}$ stops
depending on the overdrive at all. Every gain expression in this course still works;
the substitution $g_m = kV_{ov}$ that feeds them does not. The square law is the physics
of a long device, and it is taught first because it is the one you can derive.

**Sub-threshold conduction.** Below $V_{th}$ the current is not zero. It is exponential
in $V_{GS}$ — the same Boltzmann factor that gave EE201 its diode — falling by a decade
for every 60 to 90 mV. The floor is $V_T\ln 10 = 59.5$ mV at 300 K, which is the same
59.5 mV per decade the diode obeys, because it is the same statistics. "Cut-off means no
current" is a modelling convenience, and it is the wrong one for anything that has to
hold a charge for a second or run off a battery for a year.

**The body effect.** $V_{th}$ was treated as a constant. It is not: it rises when the
source is held above the substrate, because a larger surface depletion charge has to be
paid for before inversion starts. Module 2's four-resistor bias puts the source at 2 V
above ground and therefore does exactly this. The shift is a fraction of a volt, this
course ignores it, and you should know it is being ignored rather than absent.

## What to carry out of here

$k$ is $\mu C_{ox}W/L$, and only the last factor is yours. The overdrive is the gate
voltage that bought channel charge. The one-half is an average over a tapering channel.
Pinch-off is the drain end of that channel closing, which is why saturation begins
exactly at $V_{DS} = V_{ov}$ and not at some other number. And the square law is a
long-channel result — true of the device this course uses, false of the device in the
processor running it.
''',
            },
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
            "build": {
                "title": "The device itself, and the line that finds its operating point",
                "minutes": 24,
                "brief": r'''
Every other build exercise in this course replaces the transistor with a current source,
because that is what a bias calculation does. This one does not. The canvas carries a
real n-channel MOSFET — $k = 2$ mA/V², $V_{th} = 1.0$ V, $\lambda = 1/45$ — and the
solver runs the square law on it, region test and all, the same way it runs the diode
equation in EE201.

There is one circuit worth building before any amplifier, and it is the one that answers
*how do you get a chosen current through a device whose current you do not control
directly*. You control $V_{GS}$. The current follows from it, squared. So the question
is really: what value of $V_{GS}$ will this device settle at?

## What to build

A **diode-connected** MOSFET: the gate wired to the drain, so $V_{GS} = V_{DS}$ always,
and one resistor from the 12 V rail down to that node. The source goes to ground and the
probe is already on the drain.

Make the device carry **1.00 mA**.

## The two equations, and why neither is enough on its own

The device says
$$I_D = \tfrac{1}{2}kV_{ov}^{2}\,(1+\lambda V_{DS}),\qquad V_{ov}=V_{GS}-V_{th}$$
and the resistor says
$$I_D = \frac{V_{DD}-V_D}{R}$$
The second is EE201's **load line**, moved from a diode to a transistor without changing
a symbol in it. Two curves, one unknown node voltage, and the operating point is where
they cross. That is the whole method, and it is the reason this exercise comes before
biasing rather than after: module 2 designs a network to *put* the crossing somewhere,
and you cannot place a crossing you have not seen.

Work it the way you would on paper. Aim for 1 mA. The square law at 1 mA wants
$V_{ov}=\sqrt{2I_D/k}=1.00$ V, so $V_{GS}=2.00$ V, so the drain node sits at 2.00 V —
and the resistor is left holding $12-2=10$ V at 1 mA.

**The tempting wrong answer is 12 kΩ**, from dividing the whole supply by the target
current. That treats the transistor as a wire. Notice what it does *not* give you: build
it and the device carries **842 µA**, not the 1000 the arithmetic predicted and not the
1200 that 12 V across 10 kΩ would be. Both of those numbers come from assuming the answer
in order to compute it. The load line does not assume; it finds where two curves cross,
and the crossing moved when the resistor did.

## Why a diode connection guarantees saturation

Tying the gate to the drain makes $V_{DS}=V_{GS}$, and
$V_{DS}-V_{ov}=V_{GS}-(V_{GS}-V_{th})=V_{th}$. So a diode-connected MOSFET sits exactly
one threshold inside the saturation boundary, always, at every current — you cannot bias
it into triode by accident. One of the checks measures that 1.000 V and it is the same
1.000 V as the device's $V_{th}$, which is not a coincidence but the algebra above.

Nothing is graded on layout. Any drawing that puts the device at this operating point
passes.
''',
                "start": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 6},
                        {"id": "q", "kind": "NMOS", "x": 9, "y": 6, "rot": 1,
                         "value": 2e-3, "vth": 1.0, "lambda": 0.022222222222222223},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 8},
                        {"id": "out", "kind": "OUT", "x": 7, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [9, 2]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 5], "b": [7, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 6},
                        {"id": "r", "kind": "R", "x": 9, "y": 3, "rot": 1, "value": 10000},
                        {"id": "q", "kind": "NMOS", "x": 9, "y": 6, "rot": 1,
                         "value": 2e-3, "vth": 1.0, "lambda": 0.022222222222222223},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 8},
                        {"id": "out", "kind": "OUT", "x": 7, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [9, 2]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 5], "b": [7, 5]},
                        {"a": [10, 6], "b": [10, 5]},
                        {"a": [10, 5], "b": [9, 5]},
                    ],
                },
                "checks": [
                    {"name": "one resistor, one supply, and the gate tied to the drain", "code": r'''
c.assert(c.count('NMOS') === 1,
  'This exercise wants exactly one MOSFET — the one on the canvas. Found ' + c.count('NMOS') + '.');
c.assert(c.count('V') === 1,
  'One supply, the 12 V rail. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
c.assert(c.count('R') === 1,
  'One resistor sets the current. Found ' + c.count('R') + ' — if there are none yet, that ' +
  'is the part of the circuit this exercise is about.');
const d = c.device('q');
const vd = d.v[0], vs = d.v[1], vg = d.v[2];
c.assert(Math.abs(vs) < 1e-4,
  'The source belongs at ground, so that V_GS and V_DS are both read against the same ' +
  'point. It is sitting at ' + vs.toFixed(3) + ' V.');
c.assert(Math.abs(vg - vd) < 1e-3,
  'Diode-connected means the gate wired to the drain. The gate is at ' + vg.toFixed(3) +
  ' V and the drain at ' + vd.toFixed(3) + ' V. A gate left floating reads near zero and ' +
  'the device stays in cut-off, which is what a drain sitting at the full 12 V is telling you.');
'''},
                    {"name": "the device carries 1.00 mA", "code": r'''
const d = c.device('q');
const id = d.i[0];
c.assert(id > 1e-9,
  'No drain current at all. Below threshold the channel does not exist, so check the gate ' +
  'is really tied to the drain and that the resistor reaches the supply rail.');
/* The hint follows the reading, and it says what the resistor DOES rather than what a
   wrong calculation predicts. Sizing R as 12 V / 1 mA = 12 kOhm is the tempting error,
   and it does not give 1200 uA — it gives 842, because the current the transistor
   settles at is not the current the mistaken arithmetic assumed. */
const hint = id < 0.96e-3
  ? ' Too low. 842 uA is the reading from a 12 kOhm resistor, which is 12 V divided by ' +
    'the target current — the transistor treated as a wire. It is not a wire: it keeps ' +
    'about 2 V for itself, so the resistor only ever gets the remaining 10 V and needs ' +
    'to be 10 kOhm, not 12.'
  : ' Too high: the resistor is smaller than the 10 kOhm the load line asks for, so it ' +
    'drops less and the device is pushed to a larger overdrive. 8 kOhm gives 1239 uA.';
c.assert(Math.abs(id - 1.0e-3) <= 0.035e-3,
  'The device should carry 1.00 mA; it is carrying ' + (id * 1e6).toFixed(1) + ' uA.' + hint);
'''},
                    {"name": "the square law reproduces the current from the overdrive", "code": r'''
/* The device parameters are the ones the canvas hands out and the ones the brief quotes.
   Evaluating the model at the overdrive the LEARNER'S circuit produced, and comparing it
   with the current that circuit actually carries, is the check that this is a transistor
   being solved rather than a resistor being divided. */
const K = 2e-3, VTH = 1.0, LAM = 1 / 45;
const d = c.device('q');
const vd = d.v[0], vs = d.v[1], vg = d.v[2], id = d.i[0];
const vov = vg - vs - VTH, vds = vd - vs;
c.assert(vov > 0,
  'The overdrive is ' + vov.toFixed(3) + ' V, so V_GS has not reached the 1.0 V threshold ' +
  'and there is no channel to carry anything.');
const predicted = 0.5 * K * vov * vov * (1 + LAM * vds);
c.close(id, predicted, 0.01,
  'the saturation square law evaluated at the overdrive this circuit settled on (' +
  vov.toFixed(4) + ' V), against the current the circuit actually carries');
'''},
                    {"name": "a diode connection sits exactly one threshold inside saturation", "code": r'''
const VTH = 1.0;
const d = c.device('q');
const vd = d.v[0], vs = d.v[1], vg = d.v[2];
const vov = vg - vs - VTH, vds = vd - vs;
c.assert(vds >= vov,
  'V_DS is ' + vds.toFixed(3) + ' V against an overdrive of ' + vov.toFixed(3) + ' V, so the ' +
  'device is in triode, not saturation — which a diode-connected device cannot be.');
c.close(vds - vov, VTH, 0.02,
  'V_DS minus the overdrive. Tying the gate to the drain makes V_DS = V_GS, and ' +
  'V_GS - V_ov is the threshold itself, so this margin should come out at the device V_th ' +
  'of 1.000 V whatever current you chose');
'''},
                ],
                "hints": [
                    "Start from the current, not the resistor. At $I_D = 1$ mA the square law needs $V_{ov} = \\sqrt{2I_D/k} = \\sqrt{2\\times10^{-3}/2\\times10^{-3}} = 1.00$ V.",
                    "So $V_{GS} = V_{th} + V_{ov} = 2.00$ V — and because the gate is tied to the drain, that is also the drain voltage.",
                    "The resistor is left with $12 - 2 = 10$ V at 1 mA, so it is 10 kΩ. Draw it from the rail at the top down to the drain.",
                    "The gate connection is the second thing to draw and the one people forget: run a wire from the gate pin round to the drain node. Until it is there the gate floats, $V_{GS}$ reads about zero, and the drain sits at the full 12 V with no current flowing.",
                    "The solver will show 1.002 mA rather than 1.000 mA. That 0.2% is $\\lambda$: the channel-length modulation term the hand calculation dropped. The check allows 3.5%, so it is not what is failing if something is.",
                ],
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
                "That immunity has a number, and it is the only figure of merit a bias network has. Differentiating the operating point with respect to $k$ gives $\\frac{k}{I_D}\\frac{\\partial I_D}{\\partial k} = \\frac{1}{1+g_mR_S}$: a fractional error in the device arrives at the current divided by the degeneration's loop gain. This design has $g_mR_S \\approx 4.25$, so a 50% spread in $k$ shows up as 7% in $I_D$. Ground the source instead and the divisor is 1 — the same 1 mA, and 43%.",
                "The second build in this module puts a real MOSFET in place of the current source and measures both. Worth knowing before you get there: a bias worked out by hand for 1.000 mA settles at **1.0202 mA**, because the hand calculation drops $(1+\\lambda V_{DS})$ and the device does not.",
                "Finding the operating point means solving two equations at once: $V_{GS} = V_G - I_DR_S$ and $I_D = \\tfrac{1}{2}k(V_{GS}-V_{th})^2$. Substituting gives a quadratic in $I_D$; the root with $V_{GS} > V_{th}$ is the physical one and the other is an artefact of squaring.",
                "**Headroom**: $V_{DS}$ must remain above $V_{ov}$ at the *bottom* of the output swing, not merely at the quiescent point, or the device slides into triode and the waveform flattens on one side.",
                "$R_D$ sets both the DC drop $I_DR_D$ and, in the next module, the gain. A larger $R_D$ buys gain and spends headroom, and that is the first of the course's several irreducible compromises.",
            ],
            "read": [{
                "title": "Two volts on the gate, and the transistor that disagreed",
                "minutes": 14,
                "body": r'''
Wire the course device the way module 1 left it: source to ground, drain through 5 kΩ to
a 12 V rail, and the gate taken straight to a bench supply set to 2.000 V. Module 1 says
this gives 1.00 mA, and it does. The meter in the drain lead reads 1.00 mA and the drain
sits at 7.00 V. (Both to three figures; the small correction that separates the ideal
square law from the real device is a section away, and it is not what this page is about.)

Now unsolder the transistor and fit the next one out of the same tube. Same part number,
same reel, same afternoon. The drain now reads 8.80 V, and the meter reads 0.64 mA.

Nothing in the circuit changed. What changed is that the second device has a threshold
of 1.2 V rather than 1.0 V, which is inside its data sheet, and the overdrive therefore
fell from 1.000 V to 0.800 V. The current follows the square of the overdrive:
$0.8^2 = 0.64$, so 1.00 mA became 0.64 mA, and a third of the drain current walked out
of the circuit because of two tenths of a volt nobody controls.

That is the problem this module exists to solve, and it is worth being clear that it is
not a problem about *reaching* 1 mA. Reaching 1 mA is one turn of a bench supply. The
problem is staying there.

## Where the feedback comes from

Watch what makes the collapse possible: the gate is held at a fixed voltage, so
$V_{GS}$ is fixed, so nothing in the circuit can react when the device changes. The
current is whatever the device says it is.

Break that by refusing to hold $V_{GS}$ directly. Put a resistor $R_S$ between the source
and ground, and hold the *gate* at a fixed $V_G$ instead. Now

$$V_{GS} = V_G - I_D R_S$$

and the current appears on the right-hand side of its own governing equation. Suppose the
device turns out weak and $I_D$ starts to fall. Then $I_DR_S$ falls, so $V_{GS}$ rises, so
the overdrive rises, so $I_D$ rises. The circuit pushes back. It is negative feedback,
built out of one resistor and Kirchhoff's voltage law, and it is doing its work at DC
before any signal has arrived.

Nothing has been announced here that was not read off the drawing. The whole of
four-resistor biasing is that one substitution, plus a divider to make $V_G$ and a drain
resistor to turn the current into a voltage.

## Solving the loop, with real numbers

Take the design this module's builds and lab all use: $V_{DD} = 12$ V, and the aim is
$I_D = 1.00$ mA with the source at $V_S = 2.00$ V and the drain at $V_D = 7.00$ V.

Going forwards, it is four divisions. $R_S = V_S/I_D = 2.00/1\text{ mA} = 2$ kΩ. $R_D$
has to lose $12 - 7 = 5$ V at the same current, so it is 5 kΩ. The device needs
$V_{ov} = \sqrt{2I_D/k} = 1.00$ V, so $V_{GS} = 2.00$ V, so the gate must sit at
$V_S + V_{GS} = 4.00$ V — one third of the supply. Choose the divider from a current
budget rather than a voltage one: 16 µA through 750 kΩ, split 500 kΩ over 250 kΩ.

Going backwards is harder, and it is the direction that tells you whether the design
works. Substituting $V_{GS} = V_G - I_DR_S$ into $I_D = \tfrac{1}{2}k(V_{GS}-V_{th})^2$
gives a quadratic in $I_D$:

$$\tfrac{1}{2}kR_S^2\,I_D^2 \;-\; \left(kR_S(V_G-V_{th}) + 1\right)I_D \;+\;
\tfrac{1}{2}k(V_G-V_{th})^2 \;=\; 0$$

```python
import math

K, V_TH = 2e-3, 1.0                 # A/V^2 and V, the course device
V_DD, R_S, R1, R2 = 12.0, 2000.0, 500e3, 250e3

v_g = V_DD * R2 / (R1 + R2)
e = v_g - V_TH
a = 0.5 * K * R_S ** 2
b = -(K * R_S * e + 1.0)
c = 0.5 * K * e * e
root = math.sqrt(b * b - 4 * a * c)
roots = [(-b - root) / (2 * a), (-b + root) / (2 * a)]

print(f"V_G = {v_g:.2f} V")
for i_d in roots:
    print(f"  I_D = {i_d * 1e3:.2f} mA  ->  V_GS = {v_g - i_d * R_S:+.2f} V")
```

That prints a gate at 4.00 V and two roots, 1.00 mA and 2.25 mA. Only one of them is a
circuit. Substitute the second back and $V_{GS}$ comes out at $-0.50$ V, which is below
threshold, where there is no channel and the equation that was solved does not describe
anything. The extra root is an artefact of squaring: the algebra lost the sign of the
bracket, and it handed back the solution in which the bracket is negative. Every root of
a bias quadratic has to be substituted back and checked against the assumption that
produced it. The lab in this module, **Designing a bias point, and checking it holds**,
enforces exactly that filter, and its `bias_point` function is the code above with the
guard written in.

## What the source resistor is actually worth

The feedback argument is qualitative so far, and biasing does not need another
qualitative argument. It needs a number.

Differentiate the fixed point with respect to $k$ and the result collapses to one
expression:

$$\frac{k}{I_D}\frac{\partial I_D}{\partial k} = \frac{1}{1 + g_mR_S}$$

Read the left-hand side as "a fractional error in the device, arriving as a fractional
error in the current". The right-hand side says it arrives divided by $1 + g_mR_S$ — the
loop gain of the degeneration, and the only figure of merit a bias network has. With
$g_m = 2$ mA/V and $R_S = 2$ kΩ that divisor is 5.

Here is the same claim measured rather than argued, on two circuits that both hit 1.00 mA
on paper: the four-resistor design above, and a divider taken straight to the gate with
the source grounded.

```python
import math

K, V_TH = 2e-3, 1.0

def solve(k, v_th, v_g, r_s):
    """Drain current of a source-degenerated bias, physical root only."""
    if r_s == 0.0:
        return 0.5 * k * (v_g - v_th) ** 2
    e = v_g - v_th
    a, b, c = 0.5 * k * r_s ** 2, -(k * r_s * e + 1.0), 0.5 * k * e * e
    return (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)

for name, v_g, r_s in (("R_S = 2 k ", 4.0, 2000.0), ("no R_S    ", 2.0, 0.0)):
    base = solve(K, V_TH, v_g, r_s)
    hi_k = solve(1.5 * K, V_TH, v_g, r_s)
    hi_vt = solve(K, 1.2, v_g, r_s)
    print(f"{name} {base * 1e3:.3f} mA    k +50% -> {100 * (hi_k - base) / base:+6.1f} %"
          f"    V_th +0.2 V -> {100 * (hi_vt - base) / base:+6.1f} %")
```

Both start at 1.000 mA. A 50% spread in $k$ moves the degenerated design by 7.6% and the
bare one by the full 50%. The 0.2 V threshold shift that opened this reading — the second
transistor out of the tube — moves the degenerated design by 8.0% and the bare one by
36.0%, which is the 0.64 mA measured at the top of the page.

Same device, same nominal current, four and a half times less sensitivity. That is what
$R_S$ buys, and it is why a bias network is never judged on whether it hits its target.

## The mistake, and why it is so easy to make

The error that shows up most often is writing $V_{GS} = V_G$: taking the divider output
as the gate-source voltage and forgetting that the source is no longer at ground. With
$V_G = 4.00$ V it predicts $V_{ov} = 3.00$ V and $I_D = 9$ mA, nine times the real answer,
and the mistake is invisible because 9 mA is a perfectly plausible number.

It is tempting because it was true five minutes ago. In module 1's diode-connected build
the source *was* at ground, so $V_{GS}$ and $V_G$ were the same node and no distinction
was needed. The moment $R_S$ appears they are two different voltages separated by
$I_DR_S$ — and that separation is not an inconvenience, it is the feedback path. The 2 V
you have to remember to subtract is the entire mechanism the previous section measured.

The build exercise **A four-resistor bias for 1 mA** is arranged so this cannot be
skipped: it checks the gate node minus the source node, not the gate node alone.

## Where this model stops

Three places, in rising order of how much they will bother you.

**The divider is unloaded, and only because of the gate.** $V_G = V_{DD}R_2/(R_1+R_2)$
is exact here because the gate draws no DC current at all, which is what licenses 500 kΩ
and 250 kΩ. That licence is specific to a MOSFET. Module 9 puts a bipolar base on the end
of this identical divider and watches the midpoint fall from 4.00 V to 2.49 V.

**Channel-length modulation is dropped.** The hand model uses $I_D = \tfrac{1}{2}kV_{ov}^2$;
the device obeys $I_D = \tfrac{1}{2}kV_{ov}^2(1+\lambda V_{DS})$. With $V_{DS}$ near 4.9 V
and $\lambda = 1/45$ that factor is about 1.11, an 11% push on the current — of which the
degeneration absorbs all but 2%. A design worked out for 1.000 mA settles at **1.0202 mA**.
The build **The same bias, with the device left in** puts a real MOSFET on the canvas and
shows you that number, and the reason its checks accept a band from 980 to 1060 µA rather
than demanding 1000 is that the band is where the physics is.

**The threshold is not a constant.** $V_{th}$ rises when the source sits above the
substrate, which this design does by 2 V — the body effect module 1 named and this course
ignores. It is a fraction of a volt, it always makes the device harder to turn on, and it
is being ignored rather than being absent.

## What to carry forward

The bias point is not preparation for the interesting part. $g_m = 2I_D/V_{ov}$, so the
current chosen here *is* the gain setting of module 3, and $R_D$ chosen here is the other
half of it. A stage whose bias moves by 36% has a gain that moves by 18%, and no amount
of small-signal algebra downstream will find that out for you.
''',
            }],
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
            "build": [{
                "title": "A four-resistor bias for 1 mA",
                "minutes": 28,
                "brief": r'''
Bias the course device — $k = 2$ mA/V², $V_{th} = 1.0$ V — at **1.00 mA** from a 12 V
supply.

This exercise works in the notebook model: at the operating point the transistor's
drain-source path *is* a current source — 1 mA flows in at the drain and out at the
source, and no equation in a bias calculation asks it for anything else. The canvas
therefore opens with a 1 mA current source already placed, standing in for the device,
with its **+ pin as the drain**.

Build it that way first, because it is how the design is done on paper and the algebra
is clearer with the device's own feedback taken out of it. Then do the next exercise,
which is the same specification with a real MOSFET in the socket. The solver carries
one — module 1's build already used it — and the difference between the two is worth
having: with a current source the drain current is *stipulated*, so no mistake you can
make in the divider will move it, and the one quantity a bias network exists to control
is the one thing this drawing cannot get wrong.

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
            }, {
                "title": "The same bias, with the device left in",
                "minutes": 30,
                "brief": r'''
Same supply, same specification, same four resistors. The current source is gone and
there is a real MOSFET in its place — $k = 2$ mA/V², $V_{th} = 1.0$ V, $\lambda = 1/45$,
the course device — with the drain at the top pin, the source at the bottom and the gate
sticking out to the right. Nothing tells it to carry 1 mA. It carries whatever the
network and the square law agree on, and your job is to make them agree on 1 mA.

## Why this is a different exercise and not the same one drawn again

In the previous build the drain current was **stipulated**. You could have put the gate
divider anywhere — 1 V, 8 V, upside down — and 1.00 mA would still have flowed, because
an ideal current source passes its value whatever is asked of it. The one quantity the
entire bias network exists to control was the one quantity that drawing could not get
wrong.

Here it can. $V_G$ sets $V_{GS}$, $V_{GS}$ sets $I_D$ through the square law, and $I_D$
sets $V_S$ through $R_S$ — which changes $V_{GS}$ again. The circuit finds its own fixed
point and the solver has to iterate to it, exactly as it does for a diode.

## The specification

Unchanged from the previous exercise, so the arithmetic carries straight over:

- the source terminal sits at **2.00 V** above ground,
- $V_{GS}$ is **2.00 V**, which is what the hand model says this device needs for 1.00 mA,
- the drain sits at **7.00 V**, leaving 5 V across the device,
- the divider draws between **10 µA and 50 µA** from the supply.

Put the probe on the **drain**, which is the output of the stage you are about to build
in module 3.

## What the solver will actually show you, and why

Your hand design will say 1.000 mA. The device settles at **1.0202 mA**, 2.02% high, and
every voltage moves with it: the source lands at 2.0404 V rather than 2.000, the drain at
6.8990 rather than 7.000, and $V_{GS}$ comes out at 1.9596 V rather than 2.000.

That is $\lambda$. The hand model uses $I_D = \tfrac{1}{2}kV_{ov}^2$; the device adds
$(1+\lambda V_{DS})$, and with $V_{DS}$ near 4.86 V and $\lambda = 1/45$ that factor is
1.108 — an 11% push on the current, of which the negative feedback through $R_S$ absorbs
all but 2%. **That absorption is the entire point of the exercise**, and the checks below
allow for the 2% rather than pretending it is not there.

## The requirement the previous exercise could not state

A bias network is not judged on hitting 1 mA. Any network hits 1 mA if you tune it. It is
judged on **still** being near 1 mA when the device is not the one on the data sheet —
and $k$ and $V_{th}$ vary by tens of percent across a wafer, a reel and a temperature
range.

Differentiate the fixed point $I_D = \tfrac{k}{2}(V_G - I_DR_S - V_{th})^2$ with respect
to $k$ and the algebra collapses to one number:

$$\frac{k}{I_D}\,\frac{\partial I_D}{\partial k} = \frac{1}{1+g_mR_S}$$

A fractional error in $k$ arrives at the current divided by $1+g_mR_S$. That factor is
the **loop gain of the degeneration**, and it is the only thing standing between a device
tolerance and a bias error. With $g_m \approx 2.13$ mA/V and $R_S = 2$ kΩ it is 5.25, so
this design divides device spread by more than five, and a check below measures it on
your circuit and requires it to be at least four.

Here is what that buys. Both designs below were worked out by hand for exactly 1.000 mA;
both were then solved with the real device, and then solved again with the device
changed underneath them:

```text
                            hand    device    k +50%    V_th -0.2 V
  four-resistor, R_S = 2k  1.000   1.020 mA   +7.1 %      +7.7 %
  gate bias, no R_S        1.000   1.140 mA  +42.9 %     +37.9 %
```

The second row is a divider straight to the gate with the source grounded — one resistor
fewer, and a design that hits its target on paper. Look at what it does with an error.
The $\lambda$ the hand calculation dropped arrives as 14% rather than 2%; a 50% spread
in $k$ arrives as 43% rather than 7%. The degeneration did not remove those errors, it
divided them, and $1+g_mR_S$ is the divisor.

A check below measures that divisor. The gate-biased design fails it — and, because the
source sits at ground rather than 2 V, it fails the voltage check too. What it does
**not** fail is the first check: it is a properly saturated MOSFET carrying about a
milliamp. That is the trap worth seeing. A bias network can be right about the operating
point and wrong about everything that matters, and the previous exercise, with a current
source stipulating the current, has no way of telling you so.

Nothing is graded on layout.
''',
                "start": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 6},
                        {"id": "q", "kind": "NMOS", "x": 8, "y": 6, "rot": 1,
                         "value": 2e-3, "vth": 1.0, "lambda": 0.022222222222222223},
                        {"id": "g1", "kind": "GND", "x": 8, "y": 11},
                        {"id": "out", "kind": "OUT", "x": 6, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [12, 2]},
                        {"a": [8, 5], "b": [6, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 6},
                        {"id": "rd", "kind": "R", "x": 8, "y": 3, "rot": 1, "value": 5000},
                        {"id": "q", "kind": "NMOS", "x": 8, "y": 6, "rot": 1,
                         "value": 2e-3, "vth": 1.0, "lambda": 0.022222222222222223},
                        {"id": "rs", "kind": "R", "x": 8, "y": 9, "rot": 1, "value": 2000},
                        {"id": "g1", "kind": "GND", "x": 8, "y": 11},
                        {"id": "r1", "kind": "R", "x": 12, "y": 3, "rot": 1, "value": 500000},
                        {"id": "r2", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 250000},
                        {"id": "g2", "kind": "GND", "x": 12, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 6, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [12, 2]},
                        {"a": [8, 4], "b": [8, 5]},
                        {"a": [8, 7], "b": [8, 8]},
                        {"a": [8, 10], "b": [8, 11]},
                        {"a": [12, 4], "b": [12, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [9, 6], "b": [9, 5]},
                        {"a": [9, 5], "b": [12, 5]},
                        {"a": [8, 5], "b": [6, 5]},
                    ],
                },
                "checks": [
                    {"name": "the device is powered, the right way up, and in saturation", "code": r'''
c.assert(c.count('NMOS') === 1,
  'One MOSFET, the one on the canvas. Found ' + c.count('NMOS') + '.');
c.assert(c.count('V') === 1, 'One supply — the 12 V rail. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
const d = c.device('q');
const vd = d.v[0], vs = d.v[1], vg = d.v[2];
const vov = vg - vs - 1.0, vds = vd - vs;
/* Orientation first, and phrased so it cannot fire on a circuit that is merely
   unfinished: an untouched canvas leaves every terminal at the same potential, and
   telling someone their device is upside down when they have not wired it yet sends
   them to fix the one thing that is right. */
c.assert(!(vs - vd > 0.1),
  'The source is sitting ' + (vs - vd).toFixed(2) + ' V above the drain, so the device is ' +
  'in upside down. Its drain is the TOP pin and belongs towards the supply; turning it ' +
  'also moves the gate pin to the other side of the body.');
c.assert(vov > 0,
  'The overdrive is ' + vov.toFixed(3) + ' V, so the gate has not reached the 1.0 V ' +
  'threshold and no channel exists. Check the divider actually reaches the gate pin — ' +
  'on a device drawn upright that is the pin sticking out to the right of the body.');
c.assert(vds >= vov,
  'V_DS is ' + vds.toFixed(3) + ' V against an overdrive of ' + vov.toFixed(3) + ' V, so the ' +
  'device has dropped into triode. There it is a resistor, not a current source, and no ' +
  'small-signal number in module 3 will apply to it.');
'''},
                    {"name": "the drain current came out at 1 mA, and nothing told it to", "code": r'''
const d = c.device('q');
const id = d.i[0];
c.assert(id > 1e-9, 'No drain current at all — the device is in cut-off.');
c.assert(id >= 0.98e-3 && id <= 1.06e-3,
  'The drain current is ' + (id * 1e6).toFixed(1) + ' uA. It should land between 980 and ' +
  '1060 uA: the hand design targets 1000, and the lambda term the hand design drops ' +
  'carries it to about 1020. Nothing in this circuit sets the current directly — it is ' +
  'the square law and the network agreeing, so a current far from target means V_G or ' +
  'R_S is wrong, not that a source value needs changing.');
'''},
                    {"name": "the source is at 2.0 V, the drain near 7.0 V, and the divider is in budget", "code": r'''
const d = c.device('q');
const vd = d.v[0], vs = d.v[1], id = d.i[0];
c.assert(vs >= 1.95 && vs <= 2.10,
  'The source should sit at 2.00 V (the device settles nearer 2.04). Measured ' +
  vs.toFixed(3) + ' V — that is I_D through R_S, so it pins R_S at about 2 kOhm.');
c.assert(vd >= 6.80 && vd <= 7.05,
  'The drain should sit at 7.00 V (the device settles nearer 6.90). Measured ' +
  vd.toFixed(3) + ' V — that is 12 V minus I_D through R_D, so it pins R_D at about 5 kOhm.');
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1,
  'The supply current has to mean one thing, so this exercise wants exactly one part ' +
  'carrying a solved-for current — the 12 V source. Found ' + ids.length + '.');
/* the supply feeds the drain branch and the divider; the gate itself draws nothing at
   all, so whatever the supply delivers beyond the drain current is the divider's */
const idiv = Math.abs(cur[ids[0]]) - id;
c.assert(idiv >= 10e-6 * 0.98,
  'The divider must carry at least 10 uA; it carries ' + (idiv * 1e6).toFixed(1) +
  ' uA, which leaves the gate at the mercy of leakage.');
c.assert(idiv <= 50e-6 * 1.02,
  'The divider may draw at most 50 uA; it draws ' + (idiv * 1e6).toFixed(1) + ' uA.');
'''},
                    {"name": "the bias is at least four times stiffer than the device it holds", "code": r'''
/* Everything here is measured on the learner's own circuit. The only imported number is
   the data-sheet threshold, which is what a data sheet is for.
     g_m  = 2 I_D / V_ov   — exact for the square law, and it already carries the lambda
                             correction because I_D is the current actually flowing
     R_S  = V_S / I_D      — the gate draws nothing, so every electron in the source
                             terminal came through R_S and no measurement of R_S is needed
   A gate-biased stage with the source grounded gives V_S = 0, hence R_S = 0, hence a
   stiffness of exactly 1: it hits the target current and fails here, which is the whole
   distinction this exercise exists to draw. */
const VTH = 1.0;
const d = c.device('q');
const vs = d.v[1], vg = d.v[2], id = d.i[0];
const vov = vg - vs - VTH;
c.assert(vov > 0, 'No overdrive, so there is no operating point to be stiff about.');
const gm = 2 * id / vov;
const rs = vs / id;
const loop = 1 + gm * rs;
c.assert(rs > 1,
  'The source sits at ' + (vs * 1e3).toFixed(1) + ' mV, so there is essentially no source ' +
  'resistor. A divider straight to the gate does reach 1 mA, and a 50% spread in k then ' +
  'arrives at the drain current as a 43% error. The four-resistor network exists to stop ' +
  'that, and it needs R_S to do it.');
c.assert(loop >= 4,
  'The degeneration loop gain 1 + g_m*R_S is ' + loop.toFixed(2) + ', so a fractional ' +
  'error in k reaches I_D divided by only that much. This design needs at least 4; the ' +
  'specification\'s 2 V at the source with g_m near 2.1 mA/V gives about 5.25. Measured ' +
  'g_m = ' + (gm * 1e3).toFixed(3) + ' mA/V and R_S = ' + (rs / 1e3).toFixed(3) + ' kOhm.');
'''},
                ],
                "hints": [
                    "The arithmetic is the previous exercise's, unchanged: $R_S = 2$ kΩ, $R_D = 5$ kΩ, and a 750 kΩ divider split 500 kΩ over 250 kΩ to put the gate at 4.00 V.",
                    "The gate is the pin on the **right** of the device, one cell out from the body. Run the divider's midpoint across to it — the drain pin is directly above the body, so a wire straight across at the drain's height will short the gate to the drain and make a diode-connected device instead.",
                    "The drain is the **top** pin and the source the bottom one. Upside down, the solver still answers — the square law is written to swap drain and source when the drain goes below the source — but $V_{DS}$ comes out negative and the saturation check fails.",
                    "The probe goes on the **drain** this time, not the gate: this node is the output of the amplifier module 3 builds out of exactly this bias.",
                    "If the current is right but the stiffness check fails, the source resistor is missing or too small. Grounding the source and moving the divider to suit gives the same 1 mA and none of the immunity; that is the design this check is written to reject.",
                ],
            }],
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
            "read": [{
                "title": "The transistor as two components, and the number that falls out",
                "minutes": 14,
                "body": r'''
Take the stage module 2 biased — 12 V rail, 5 kΩ at the drain, source at 2.00 V held
there by a bypass capacitor so that it cannot move at signal frequencies — and do
something crude to it. Turn the gate supply up by 50 mV, from 2.000 V to 2.050 V, and
write down the drain voltage. Then turn it down to 1.950 V and write that down too.

```text
   V_GS         V_ov        I_D          V_D
  1.950 V      0.950 V     0.9025 mA    7.4875 V
  2.000 V      1.000 V     1.0000 mA    7.0000 V
  2.050 V      1.050 V     1.1025 mA    6.4875 V
```

The drain moved 1.0000 V for 100 mV at the gate, and it moved the *other way*. There is
the amplifier: a gain of $-10$, obtained with a voltmeter and no theory at all. Everything
below is an attempt to get that number without turning the knob, and then to find out what
the knob-turning was hiding.

## Splitting one variable into two

The obstacle to computing that slope on paper is that $I_D = \tfrac{1}{2}k(V_{GS}-V_{th})^2$
is not linear, and a parabola has a different slope everywhere. The way out is to stop
asking about the whole curve and ask only about a small neighbourhood of one point.

Write every quantity as a resting value plus a deviation: $v_{GS} = V_{GS} + v_{gs}$,
$i_D = I_D + i_d$, and expand the drain current as a function of the two terminal
voltages it depends on, to first order in the deviations:

$$i_d \;=\; \frac{\partial I_D}{\partial V_{GS}}\,v_{gs} \;+\;
\frac{\partial I_D}{\partial V_{DS}}\,v_{ds}$$

Both derivatives are already known. Module 1 differentiated the square law and got the
first: $g_m = kV_{ov} = 2I_D/V_{ov} = \sqrt{2kI_D}$. The second comes from the
$(1+\lambda V_{DS})$ factor and is a *conductance*, so it is written as the reciprocal of
a resistance, $1/r_o$ with $r_o = V_A/I_D$. So

$$i_d \;=\; g_m v_{gs} \;+\; \frac{v_{ds}}{r_o}$$

and now read that expression as a drawing rather than an equation. The first term is a
current between drain and source, controlled by a voltage elsewhere in the circuit: a
**voltage-controlled current source**. The second is a current between drain and source
proportional to the voltage between drain and source: an ordinary **resistor**, of value
$r_o$, in parallel with it. That is the whole small-signal model. Two components, and
neither of them was chosen — both fell out of one Taylor expansion.

At this course's operating point, $I_D = 1$ mA with $V_{ov} = 1$ V and $V_A = 45$ V:
$g_m = 2$ mA/V and $r_o = 45$ kΩ.

## The supply rail is a piece of wire

One more step is needed before the model can be used, and it is the step that trips
people. In the small-signal circuit, **every DC source becomes a short to ground**.

The reason is in the definition rather than in any convention. Small-signal analysis only
ever talks about deviations, and a 12 V supply has a deviation of zero — it is 12 V now
and 12 V in a microsecond. A node whose signal voltage is identically zero is signal
ground, whatever its DC potential. So $R_D$, drawn on the schematic from the drain up to
$V_{DD}$, appears in the small-signal circuit as a resistor from the drain **to ground**,
sitting in parallel with $r_o$. The same argument turns the bias divider's $R_1$, which
goes to the rail, into a resistor from the gate to ground alongside $R_2$.

Now the gain is one line. All of $g_mv_{gs}$ flows out of the drain node into whatever
resistance is there, and $v_{gs} = v_{in}$ because the source is held at signal ground by
its bypass capacitor:

$$A_v = \frac{v_{out}}{v_{in}} = -g_m\,(r_o \parallel R_D \parallel R_L)$$

The minus sign is physical. More gate voltage makes more drain current, more drain
current makes a bigger drop across $R_D$, and a bigger drop leaves the drain *lower*. A
common-source stage inverts, and it is not a bookkeeping artefact you may drop when it is
inconvenient — module 7 has a configuration with the same gain magnitude and no inversion,
and module 10 has a circuit whose whole behaviour depends on the two signs being opposite.

## The stage, in numbers

```python
def parallel(*ohms):
    return 1.0 / sum(1.0 / r for r in ohms)

gm, ro, r_d = 2e-3, 45e3, 5e3
print(f"unloaded             A_v = {-gm * parallel(ro, r_d):+.3f}")
print(f"45 k load            A_v = {-gm * parallel(ro, r_d, 45e3):+.3f}")
print(f"600 ohm load         A_v = {-gm * parallel(ro, r_d, 600.0):+.3f}")
print(f"ideal current load   A_v = {-gm * parallel(ro, 1e12):+.1f}")
print(f"R_S = 2 k unbypassed A_v = {-gm * r_d / (1 + gm * 2000.0):+.3f}")
```

Five numbers, and each is a different lesson.

**$-9.000$ unloaded.** $r_o$ and $R_D$ in parallel are 4.5 kΩ, not the 5 kΩ that is drawn
on the schematic. The transistor's own output resistance is at that node whether anyone
draws it or not, and it costs 10% here.

**$-8.182$ into 45 kΩ.** Hanging a load on the drain adds a third resistance in parallel,
and a parallel total can only fall. Gain at a drain is proportional to the resistance
there, so loading a common-source stage always costs gain.

**$-1.059$ into 600 Ω.** The same stage driving something genuinely low-impedance keeps
about a ninth of its gain. This is not a small correction; it is the stage failing at its
job, and it is why module 7 exists.

**$-90.0$ into an ideal current source.** Push $R_D$ to infinity and the drain sees $r_o$
alone. $g_mr_o$ is the **intrinsic gain**, and it is a ceiling: no choice of load can
beat it, because $r_o$ is in parallel with every candidate. Module 8 gets to within a
factor of two of it.

**$-2.000$ with $R_S$ left unbypassed.** Remove the bypass capacitor and the source is no
longer at signal ground; the same feedback that stabilised the bias now acts on the
signal, and the gain becomes about $-g_mR_D/(1+g_mR_S)$. A factor of five thrown away.
What it buys is that when $g_mR_S \gg 1$ the expression tends to $-R_D/R_S$ — a ratio of
two resistors, with the transistor almost absent from it. Trading raw gain for a gain that
does not depend on the device is the central bargain of feedback, and this is its smallest
instance.

The lab **Small-signal parameters and the gain they give** is these five calculations
written as five functions, with `parallel` doing the work in all of them.

## The mistake, and why it is tempting

The commonest error is quoting $-g_mR_D = -10$ and stopping. It is tempting for a reason
that is hard to argue with: $R_D$ is a component somebody chose and soldered in, and
$r_o$ is not. Nothing on the schematic reminds you it is there.

The measurement at the top of this reading makes the same error, and that is why it was
put there. A DC sweep of the pure square law gives exactly $-10$, because in the pure
square law $I_D$ does not depend on $V_{DS}$ at all — which is the same statement as
$r_o = \infty$. Put $\lambda$ back and repeat the sweep numerically:

```python
K, V_TH, LAMBDA = 2e-3, 1.0, 1.0 / 45.0
V_DD, V_S, R_D = 12.0, 2.0, 5000.0

def drain_voltage(v_gs, lam):
    """Solve the drain node against the load line, by bisection."""
    v_ov = v_gs - V_TH
    lo, hi = V_S, V_DD
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        i_d = 0.5 * K * v_ov ** 2 * (1.0 + lam * (mid - V_S))
        if V_DD - i_d * R_D > mid:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

for lam, label in ((0.0, "lambda = 0   "), (LAMBDA, "lambda = 1/45")):
    a = drain_voltage(2.001, lam)
    b = drain_voltage(1.999, lam)
    print(f"{label}   dV_D/dV_GS = {(a - b) / 0.002:+.3f}")
```

$-10.000$ with $\lambda$ switched off, $-9.900$ with it on. The slope moved the moment
the device acquired a finite output resistance, which is the whole content of the claim
that $r_o$ belongs at the drain node. It lands at $-9.9$ rather than $-9.0$ because
$\lambda$ also lifts the operating current above 1 mA and $g_m$ with it — a correction of
the same size and the same origin as the 2% the module 2 build exercise measured, and one
that every hand calculation in this subject drops on purpose.

## Where the model stops

**When the signal is not small.** Everything above is the first term of a Taylor series,
and the neglected term is the square. Drive this stage with a gate amplitude comparable
to the 1 V overdrive and the two half-cycles no longer have the same gain. Module 5 puts
a number on it: 100 mV of drive is already 2.5% of second harmonic.

**When there is a capacitor anywhere.** This model has no frequency in it, so it predicts
the same gain at 10 Hz and 10 GHz. Module 4 supplies the capacitance at the drain that
sets the top of the band, and module 6 the coupling and bypass capacitors that set the
bottom.

**$r_o$ is a linearisation too.** $V_A$ is an extrapolated intercept, not a physical
constant; a real device's output curves are not straight and $r_o$ varies with $V_{DS}$
by tens of percent. Quoting a gain of $-9.00$ to three figures is arithmetic, not
prediction. The sandbox **The gain is where the curve ends up** is a useful corrective
here: the number this module computes is where the output eventually settles, and it says
nothing at all about the journey.
''',
            }],
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
            "read": [{
                "title": "The capacitor nobody drew, and the product it fixes",
                "minutes": 13,
                "body": r'''
The stage from module 3 has a gain of 9.0 and no capacitors in it whatsoever. Put a
signal generator on its gate, set 10 mV of amplitude, and sweep the frequency while
watching the drain on a scope.

```text
      1 kHz     89.99 mV
     10 kHz     89.55 mV
     30 kHz     86.20 mV
    100 kHz     63.61 mV
    300 kHz     28.44 mV
      1 MHz      8.95 mV
     10 MHz      0.90 mV
```

Something is filtering the signal, and there is nothing on the schematic that could. By a
megahertz the stage has lost ninety per cent of what it had, and between 1 MHz and 10 MHz
it loses a further factor of ten — one decade of gain for one decade of frequency, which
is the signature of a single pole.

## The capacitance is real, it is only unlabelled

Every node in a circuit has capacitance to ground, and the drain node has three
contributions. The gate of whatever comes next is a plate on an oxide, which is what a
MOSFET gate is. The device's own drain has a reverse-biased junction to the substrate,
and a reverse-biased junction is a depletion capacitance. And the copper going from one
to the other is a conductor near a ground plane. None of these is drawn because none of
them was bought, and together they are a capacitor $C_L$ from the drain to ground. For
this stage take $C_L = 354$ pF, which is a generous number chosen to put the effect
somewhere convenient.

Now redo module 3's calculation with that capacitor present. The transistor still delivers
$g_mv_{gs}$ into the drain node; what has changed is the impedance there. $R_{out}$ and
$C_L$ are in parallel, so

$$Z(s) = \frac{R_{out}\cdot \dfrac{1}{sC_L}}{R_{out} + \dfrac{1}{sC_L}}
       = \frac{R_{out}}{1 + sR_{out}C_L}$$

and the gain, which was $-g_mR_{out}$, becomes

$$A(s) = \frac{-g_mR_{out}}{1 + sR_{out}C_L}$$

At $s = j\omega$ the magnitude is $A_0/\sqrt{1 + (\omega R_{out}C_L)^2}$, which is
$A_0/\sqrt{2}$ — three decibels down — when $\omega R_{out}C_L = 1$. Converting to hertz,

$$f_{3\mathrm{dB}} = \frac{1}{2\pi R_{out}C_L}$$

Nothing was assumed about amplifiers to get that; it is one impedance divided by another.
The transistor's only role was to be a current source, which is what makes the result apply
to any current driven into any resistance and capacitance in parallel.

## The product that will not move

Multiply the two things you now have. The gain is $A_0 = g_mR_{out}$ and the bandwidth is
$1/(2\pi R_{out}C_L)$, so

$$A_0 \times f_{3\mathrm{dB}} \;=\; g_mR_{out}\cdot\frac{1}{2\pi R_{out}C_L}
\;=\; \frac{g_m}{2\pi C_L}$$

$R_{out}$ has cancelled. It appears in the gain as a multiplier and in the bandwidth as a
divisor, so anything done to it moves the two in opposite directions by the same factor
and leaves their product where it was. Watch that happen on the actual numbers:

```python
import math

GM, RO, C_L = 2e-3, 45e3, 354e-12
for r_d in (5e3, 20e3, 45e3, 1e9):
    r_out = 1.0 / (1.0 / RO + 1.0 / r_d)
    a0 = GM * r_out
    f3 = 1.0 / (2 * math.pi * r_out * C_L)
    print(f"R_D = {r_d / 1e3:8.1f} k   A_0 = {a0:6.2f}   f_3dB = {f3 / 1e3:7.2f} kHz"
          f"   product = {a0 * f3 / 1e3:.1f} kHz")
tau = 4500.0 * C_L
print(f"tau = {tau * 1e6:.3f} us   10-90% rise = {tau * math.log(9.0) * 1e6:.3f} us")
```

Four drain resistors from 5 kΩ to effectively infinite. The gain runs from 9.00 to 90.00,
the bandwidth from 99.91 kHz down to 9.99 kHz, and the product sits at 899.2 kHz in every
row. (899 rather than 900 because 354 pF is the rounded value; the 353.7 pF that the build
exercise carries lands the corner on exactly 100.0 kHz.)

So a designer who wants more gain from this stage can have it, at an exactly proportional
price in bandwidth, and the transaction is closed. To move the product itself there are
two handles and no others: raise $g_m$, or lower $C_L$. And $g_m = \sqrt{2kI_D}$, so
doubling the product by spending current means **quadrupling** the current. Four times the
power for one doubling is a poor rate of exchange, and it is why real designs reach first
for a wider device or a lighter load.

## The same pole, told in time

The last line of that program prints $\tau = 1.593$ µs and a 10–90% rise time of 3.500 µs.
Neither is a new fact; both are the same pole read in the time domain.

A step into a single-pole network gives $v(t) = V_f(1 - e^{-t/\tau})$ with
$\tau = R_{out}C_L$. It reaches 10% at $t = \tau\ln(1/0.9) = 0.105\tau$ and 90% at
$\tau\ln 10 = 2.303\tau$, so the transition takes $\tau\ln 9 = 2.197\tau$ — the familiar
factor of 2.2. And since $\tau = 1/(2\pi f_{3\mathrm{dB}})$,

$$t_r = \frac{2.197}{2\pi f_{3\mathrm{dB}}} = \frac{0.35}{f_{3\mathrm{dB}}}$$

which for 100 kHz is 3.5 µs. A bandwidth specification and a rise-time specification are
the same specification in different clothes, and being able to move between them without
looking anything up is worth more than either formula.

## The mistake, and why it is tempting

Quoting $1/(R_{out}C_L)$ as the bandwidth. For this stage that is 628 kHz rather than
100 kHz: a factor of $2\pi$, wrong by more than six times, in a number that will end up on
a data sheet.

It is tempting because the algebra hands it to you. The pole falls out of the analysis as
$\omega = 1/(R_{out}C_L)$, in radians per second, and radians per second is the natural
unit for everything on the way there — $s$, $j\omega$, the impedance of a capacitor. Hertz
only enters at the last line, and it enters by division. The habit worth forming is to
write the unit next to every corner frequency you compute, every time, so that a
radian-per-second answer cannot silently become a hertz one.

The build exercise **The output pole, drawn and measured** is the check on this: it asks
for a corner at 100 kHz, and a circuit designed around 628 krad/s misses it by the same
factor of $2\pi$.

## Where this stops holding

**There is more than one pole.** The input network — the signal source's resistance
working against the bias divider and the gate's own capacitance — makes a second one. The
habit this module is teaching is to find the **dominant** pole, the slowest, and treat the
rest as a correction; that is what the sandbox **Gain, bandwidth, and the line between
them** is showing when it draws two real poles a factor of eight apart and the response
takes its shape from the slower one. The habit fails when two poles land close together,
which is when a stage starts to overshoot.

**The worst capacitance is not to ground.** A real MOSFET has a capacitance $C_{gd}$ from
gate to drain, and that one is connected between the input and the output of an inverting
amplifier. The input has to charge it not through the input swing but through the input
swing *plus* the output swing, so it loads the source as though it were
$(1+|A_v|)C_{gd}$ — for this stage, ten times its actual value. This is the Miller effect,
it is usually the real bandwidth limit in a common-source stage, and lumping everything
into one $C_L$ at the drain hides it. What survives is the shape of the answer: a
dominant pole, a 20 dB per decade slope, and a product that resists being improved.

**Above a few hundred megahertz there are no lumped components.** Wire inductance,
transmission-line behaviour and the transistor's own transit time all arrive, and the
picture of "one node, one capacitance to ground" stops describing anything. The number
that replaces $g_m/(2\pi C_L)$ there is the device's $f_T$, and it belongs to a later
course.
''',
            }],
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
        # ---- M5 -----------------------------------------------------------
        {
            "title": "Swing, clipping and distortion",
            "summary": "Two different ceilings sit above the stage you just designed, and the lower one is rarely the one being watched.",
            "concepts": [
                "Module 3 computed a gain and said nothing at all about how large a signal that gain applies to. Two independent ceilings sit above it. **Clipping** is geometric: the drain runs out of room. **Distortion** is the curvature of the square law showing through. They have different cures and they produce different-looking waveforms.",
                "Upward, the drain cannot pass $V_{DD}$ — that is the point where the drain current has fallen to zero and the device is off. The positive margin is $V_{DD} - V_D$.",
                "Downward, the drain must stay above $V_S + V_{ov}$ or the device slides into triode. The negative margin is $V_D - V_S - V_{ov}$. That is the quick version, using the quiescent overdrive; the honest condition is $v_{DS} \\ge v_{GS} - V_{th}$ at every *instant*, and on the downward half-cycle the gate is being driven up, so the real limit arrives slightly earlier than the estimate says.",
                "The two margins are equal when $V_D = (V_{DD} + V_S + V_{ov})/2$ — the midpoint of the drain's allowed range. For this stage on 12 V with $V_S = 2$ V and $V_{ov} = 1$ V that is 7.50 V, which needs $R_D = 4.5$ kΩ and gives ±4.5 V of swing.",
                "Every volt of source lift bought for bias stability costs half a volt of peak swing, because it is taken off one end of a range whose midpoint then moves by half of it. That is the price of the negative feedback module 2 put in.",
                "Distortion comes from the square itself. Put $v_{gs} = \\hat{V}\\cos\\omega t$ into $I_D = \\tfrac{1}{2}k(V_{ov} + v_{gs})^2$ and the cross term gives a fundamental of $kV_{ov}\\hat{V}$ while the $v_{gs}^2$ term gives a second harmonic of $\\tfrac{1}{4}k\\hat{V}^2$. Their ratio is $\\mathrm{HD}_2 = \\hat{V}/(4V_{ov})$: the input amplitude measured in overdrives, divided by four.",
                "The same squared term also raises the *average* drain current by $\\tfrac{1}{4}k\\hat{V}^2$. A large signal shifts the operating point it is sitting on — 0.2 V of drive takes this stage from 1.00 mA to 1.02 mA.",
                "Which ceiling binds here is not close. Clipping allows 4.5 V of peak at the drain. One per cent second-harmonic distortion allows $\\hat{V} = 40$ mV, which at a gain of 9 is 0.36 V at the drain — more than ten times sooner. Raising the supply does nothing about that; raising the overdrive does, and the overdrive is bought with current.",
                "An unbypassed source resistor cuts distortion by roughly the same $(1 + g_mR_S)$ by which it cuts gain. The 2 kΩ of module 2 takes $\\mathrm{HD}_2$ at 0.1 V of drive from 2.5% to about 0.5%, and the gain from −10 to −2. Linearity, like gain accuracy, is something feedback buys with gain.",
            ],
            "read": [{
                "title": "The waveform that went crooked before it went flat",
                "minutes": 14,
                "body": r'''
Put module 3's stage on the bench — 12 V rail, 5 kΩ at the drain, source held at 2.00 V
by its bypass capacitor, gate resting at 2.000 V — and hang a signal generator on the
gate and an oscilloscope, AC-coupled, on the drain. Wind the generator up and write down
how far the trace goes above its own average, and how far below.

```text
   gate drive       up from mean     down from mean
     25 mV            0.2484 V          0.2516 V
    100 mV            0.9750 V          1.0250 V
    300 mV            2.7750 V          3.2250 V
```

Nothing in that table is clipping. The drain never gets near the 12 V rail, and on the
top two rows it stays more than two and a half volts above the floor at which the device
would slide into triode. No ceiling has been met.

And yet the two halves of the wave are not the same size. At 25 mV they differ by one
part in eighty and no scope on earth will show it. At 300 mV the downward excursion is
sixteen per cent larger than the upward one and the asymmetry is obvious across the room.
The stage is failing at its job well before it runs out of room, and the failure has
nothing to do with room.

## Two ceilings, not one

Two independent limits sit above this stage, and they are different enough in kind to be
worth naming before either is calculated. **Clipping** is geometric: the drain has a
range it may live in, and when the signal drives it to an end of that range the waveform
flattens. It depends on the supply and the bias point and on nothing about the device's
curve. **Distortion** is the curve itself: module 3 took one derivative of the square law
and threw the rest away, and the discarded term did not stop existing because it was
inconvenient. The first is easy to compute and is rarely the one that binds. The second
is what the table is showing.

## Where the crookedness comes from

Drive the gate with $v_{gs} = \hat{V}\cos\theta$ and put it into the square law without
linearising anything:

$$i_D = \tfrac{1}{2}k\left(V_{ov} + \hat{V}\cos\theta\right)^{2}
     = \tfrac{1}{2}k\left(V_{ov}^{2} + 2V_{ov}\hat{V}\cos\theta
       + \hat{V}^{2}\cos^{2}\theta\right)$$

The first two terms are the bias current and the signal module 3 already knows about.
The third is the one that was dropped, and the way to read it is the identity
$\cos^{2}\theta = \tfrac{1}{2}(1 + \cos 2\theta)$, which turns a squared cosine into a
constant plus a cosine at twice the frequency. Collecting:

$$i_D = \left(\tfrac{1}{2}kV_{ov}^{2} + \tfrac{1}{4}k\hat{V}^{2}\right)
      \;+\; kV_{ov}\hat{V}\cos\theta
      \;+\; \tfrac{1}{4}k\hat{V}^{2}\cos 2\theta$$

A constant, a term at the input frequency, and a term at twice it. Three terms, and each
is a fact about the bench. The fundamental has amplitude
$kV_{ov}\hat{V} = g_m\hat{V}$, which is module 3's gain and nothing new. The second
harmonic is a component at twice the input frequency that was not in the input at all —
the amplifier has manufactured it. And the DC term has grown: the average drain current
is no longer the 1.00 mA it was biased at, because the square of a symmetric wobble is
not symmetric.

Divide the second harmonic by the fundamental and every device constant cancels:

$$\mathrm{HD}_2 = \frac{\tfrac{1}{4}k\hat{V}^{2}}{kV_{ov}\hat{V}}
                = \frac{\hat{V}}{4V_{ov}}$$

The distortion is the drive amplitude expressed as a fraction of the overdrive, divided
by four. Nothing else enters — not $R_D$, not the supply, not $r_o$.

## The table, explained

Now go back to the measurements. At $\theta = 0$ the fundamental and the second harmonic
are both at their positive peaks, so the current deviation is
$g_m\hat{V} + \tfrac{1}{4}k\hat{V}^2$; at $\theta = \pi$ the fundamental has reversed but
the second harmonic has not, so it is $g_m\hat{V} - \tfrac{1}{4}k\hat{V}^2$. The two
peaks differ by twice the harmonic, which as a fraction of the average peak is
$2\,\mathrm{HD}_2$.

```python
import math

K, V_OV = 2e-3, 1.0                  # the course device at V_GS = 2.00 V
V_DD, V_S, R_D = 12.0, 2.0, 5000.0

def drain(v_hat, theta):
    """Instantaneous drain voltage, straight from the square law."""
    i_d = 0.5 * K * (V_OV + v_hat * math.cos(theta)) ** 2
    return V_DD - i_d * R_D

for v_hat in (0.025, 0.1, 0.3):
    low, high = drain(v_hat, 0.0), drain(v_hat, math.pi)
    mean = V_DD - R_D * 0.5 * K * (V_OV ** 2 + 0.5 * v_hat ** 2)
    up, down = high - mean, mean - low
    print(f"{v_hat * 1e3:5.1f} mV in   +{up:.4f} V  -{down:.4f} V"
          f"   lopsided by {100 * (down - up) / (0.5 * (down + up)):5.2f} %"
          f"   2 HD2 = {100 * v_hat / (2 * V_OV):5.2f} %")
```

The three rows reproduce the bench table exactly, and the last two columns agree to the
digit: 1.25%, 5.00% and 15.00%. The lopsidedness you can see on a scope *is* twice the
second-harmonic distortion — a spectrum-analyser quantity, readable with a ruler.

One line in that program is worth pausing on. The mean drain voltage is not 7.000 V; it is
$V_{DD} - R_D\left(\tfrac{1}{2}kV_{ov}^2 + \tfrac{1}{4}k\hat{V}^2\right)$, so at 300 mV of
drive the average current has risen to 1.045 mA and the average drain has fallen to
6.775 V. A large signal moves the operating point it is sitting on. The lab **Both
ceilings, measured** picks that up as a quantity in its own right: its `harmonics`
function returns the DC term beside the two amplitudes, and at 0.2 V of drive it reads
1.020 mA against the 1.000 the stage was biased at.

## The other ceiling, the one you can draw

Clipping needs no calculus, only the two ends of the drain's allowed range. Upward, the
drain cannot pass the supply: the margin is $V_{DD} - V_D$. Downward, it must stay above
$V_S + V_{ov}$ or the device leaves saturation and the gain collapses: the margin is
$V_D - V_S - V_{ov}$. For this stage that is 5 V of room up and $7 - 2 - 1 = 4$ V down, so
a symmetric sine is limited to 4 V peak by the tighter side.

Which immediately says where the drain ought to have been put. Set the two margins equal
and $V_D = (V_{DD} + V_S + V_{ov})/2 = 7.50$ V, which at 1 mA needs $R_D = 4.5$ kΩ and
gives ±4.5 V. That is the whole content of this module's derivation, **Where to put the
drain, and what it is worth**, and of the build **Bias for the largest symmetric swing**,
which draws it and measures both margins.

Two consequences follow from that midpoint and are worth carrying. Every volt of source
lift bought in module 2 for bias stability costs half a volt of peak swing, because it is
taken off one end of a range whose midpoint then moves by half of it — the negative
feedback was not free. And $R_D$ has now been fixed by a swing requirement, which means
the gain has been fixed too: moving from 5 kΩ to 4.5 kΩ takes the gain from 9.00 to 8.18.
Swing and gain stopped being independent choices the moment the drain voltage was pinned.

## Which ceiling binds

```python
K, V_OV, GM, RO = 2e-3, 1.0, 2e-3, 45e3
V_DD, V_S, I_D = 12.0, 2.0, 1e-3

for r_d in (5000.0, 4500.0):
    v_d = V_DD - I_D * r_d
    clip = min(V_DD - v_d, v_d - V_S - V_OV)
    gain = GM * (RO * r_d) / (RO + r_d)
    hd1 = 4.0 * V_OV * 0.01                      # gate amplitude for 1% HD2
    print(f"R_D = {r_d / 1e3:.1f} k   V_D = {v_d:.2f} V   gain {gain:.2f}"
          f"   clipping at {clip:.2f} V peak"
          f"   1% distortion at {hd1 * gain:.3f} V peak"
          f"   ratio {clip / (hd1 * gain):.1f}")
```

Module 3's stage clips at 4.00 V of peak output and reaches one per cent of second
harmonic at 0.360 V — eleven times sooner. Re-centred for maximum swing it clips at
4.50 V and reaches one per cent at 0.327 V, fourteen times sooner: the re-centring bought
half a volt of a ceiling that was never going to be reached.

Nor does the gap close by improving the supply. Raising $V_{DD}$ moves the clipping limit
and leaves $\hat{V}/(4V_{ov})$ exactly where it was. The one handle on distortion in that
expression is the overdrive, and $V_{ov} = \sqrt{2I_D/k}$, so halving the distortion means
quadrupling the bias current — module 4's square root, in a different costume.

## The mistake, and why it is tempting

The error is quoting the clipping headroom as the amplifier's maximum output. It is a
respectable number, it is exact, and this module has spent a section deriving it.

Watch what it claims. At the re-centred bias, 4.50 V of output needs 550 mV at the gate,
which is $\mathrm{HD}_2 = 0.55/4 = 13.8\%$. Nobody ships that. Worse, the stage never gets
there: saturation is the *instantaneous* condition $v_{DS} \ge v_{GS} - V_{th}$, and on the
half-cycle that drives the drain down, the gate is being driven up, so the floor rises with
the signal. Solving that condition rather than the resting one puts the real onset of
clipping at 384 mV of drive, not 550 mV.

The reason it is tempting is that clipping is the failure you can see. A flattened peak is
unmistakable on a scope; two per cent of second harmonic is a wave that looks perfectly
sinusoidal and measures 2% on an analyser you probably have not connected. The habit worth
forming is to compute $\hat{V}/(4V_{ov})$ at the specified output level *first*, and to
treat the headroom calculation as the check that the design will not embarrass itself,
rather than as the specification.

## Where this stops holding

**A pure square law has no third harmonic.** Every number here came from squaring, and
squaring a cosine produces exactly one extra frequency. A real device has curvature the
square law does not describe — mobility falling with gate field, velocity saturation — and
that curvature makes odd harmonics. A measured spectrum with a visible third harmonic is
not an arithmetic failure; it is the device disagreeing with module 1's model, and
$\mathrm{HD}_2 = \hat{V}/(4V_{ov})$ has nothing to say about it.

**Symmetry cancels all of this.** The second harmonic is an *even* distortion: it comes
from a term in $v_{gs}^2$, which does not change sign when the input does. Two of these
stages driven in antiphase therefore produce second harmonics that are identical rather
than opposite, and the difference between their drains carries none of it. That is the
differential pair of module 10, and even-harmonic cancellation is one of the reasons every
precision amplifier starts with one.

**Degeneration changes the formula.** $\mathrm{HD}_2 = \hat{V}/(4V_{ov})$ assumes the
source is at signal ground. Remove module 2's bypass capacitor and the source resistor
feeds back against the distortion exactly as it fed back against device spread, dividing it
by roughly $1 + g_mR_S$: at 100 mV of drive, 2.5% becomes about 0.5%. It divides the gain
by the same factor, from 9 to about 2. Linearity, like bias accuracy, is bought with gain,
and that trade is what the whole subject of feedback is for.

## What to carry forward

Two ceilings, and in a single-ended square-law stage the invisible one is more than ten
times lower. Clipping is fixed by moving the drain to the midpoint of its range.
Distortion is fixed only by current, by symmetry, or by feedback — and when the two are in
conflict, remember which of them the customer will hear.
''',
            }],
            "quiz": {
                "title": "How much signal the stage will actually take",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The stage from module 2 sits with $V_{DD} = 12$ V, $V_D = 7$ V, $V_S = 2$ V and $V_{ov} = 1$ V. What is the largest *symmetric* output swing it can produce?",
                        "opts": ["5 V peak", "4 V peak", "4.5 V peak", "9 V peak"],
                        "a": 1,
                        "why": r'''
Upward there are $12 - 7 = 5$ V of room; downward there are $7 - 2 - 1 = 4$ V. A
symmetric sine is limited by the smaller of the two, so 4 V peak. Quoting 5 V uses only
the margin to the supply and ignores that the device leaves saturation first on the
other half-cycle; quoting 9 V adds the two margins as though the waveform only ever
went one way.
''',
                    },
                    {
                        "q": "Where should the drain of that stage sit for the largest symmetric swing, and what $R_D$ puts it there at 1 mA?",
                        "opts": [
                            "7.5 V, from $R_D = 4.5$ kΩ",
                            "6.0 V, from $R_D = 6$ kΩ",
                            "9.5 V, from $R_D = 2.5$ kΩ",
                            "7.0 V, from $R_D = 5$ kΩ",
                        ],
                        "a": 0,
                        "why": r'''
The drain may live anywhere between $V_S + V_{ov} = 3$ V and $V_{DD} = 12$ V, and the
midpoint of that range is 7.5 V. At 1 mA the drop across $R_D$ is then 4.5 V, so
$R_D = 4.5$ kΩ and the swing is ±4.5 V. Leaving the drain at the 7.0 V module 2
designed costs half a volt on the tighter side, which is the price of having asked for
a round drain voltage rather than a symmetric one.
''',
                    },
                    {
                        "q": "The same stage is driven with a gate signal of 100 mV amplitude. What second-harmonic distortion does the square law produce?",
                        "opts": ["0.25%", "10%", "5%", "2.5%"],
                        "a": 3,
                        "why": r'''
$\mathrm{HD}_2 = \hat{V}/(4V_{ov}) = 0.1/4 = 0.025$, so 2.5%. The useful way to hold
that formula is that the distortion is a quarter of the drive expressed as a fraction
of the overdrive — a tenth of an overdrive in gives 2.5% of second harmonic out. 10%
would be $\hat{V}/V_{ov}$ with the factor of four dropped, and it is worth keeping,
because it is the difference between a design that meets a specification and one that
misses it fourfold.
''',
                    },
                    {
                        "q": "At a fixed *input* amplitude, which change halves the second-harmonic distortion?",
                        "opts": [
                            "doubling the overdrive",
                            "doubling $R_D$",
                            "halving $R_D$",
                            "adding a bypass capacitor across $R_S$",
                        ],
                        "a": 0,
                        "why": r'''
$\mathrm{HD}_2 = \hat{V}/(4V_{ov})$ contains neither $R_D$ nor anything else at the
drain, because the distortion is created in the gate-to-current relation and $R_D$ only
turns the resulting current into a voltage — it scales the fundamental and the harmonic
equally. Doubling the overdrive does halve it, and costs four times the bias current
since $V_{ov} = \sqrt{2I_D/k}$. Bypassing $R_S$ goes the wrong way entirely: it removes
the local feedback that was linearising the stage.
''',
                    },
                    {
                        "q": "This stage has a gain of 9 and 4.5 V of symmetric headroom. A specification asks for 1 V peak at the drain. What actually limits the design?",
                        "opts": [
                            "the negative half clips on the triode boundary",
                            "distortion — the second harmonic is already about 2.8%",
                            "the positive half clips on the supply rail",
                            "nothing; 1 V is comfortably inside every limit",
                        ],
                        "a": 1,
                        "why": r'''
1 V at the drain needs 111 mV at the gate, which is $\mathrm{HD}_2 = 0.111/4 = 2.8\%$.
The clipping limits are four and a half times further away and never come into it. This
is the usual state of affairs in a single-ended square-law stage: the rails are
generous and the curvature is not, so headroom calculations tell you what the amplifier
cannot do and distortion calculations tell you what it will not do *well*.
''',
                    },
                    {
                        "q": "Why is $V_D > V_S + V_{ov}$, with the quiescent overdrive, slightly optimistic as a clipping limit?",
                        "opts": [
                            "because $r_o$ falls at large signals",
                            "because the supply sags under load",
                            "because on the half-cycle that pulls the drain down the gate is being driven up, so the instantaneous overdrive is larger than the quiescent one",
                            "because the source voltage rises with the signal",
                        ],
                        "a": 2,
                        "why": r'''
Saturation is $v_{DS} \ge v_{GS} - V_{th}$ instant by instant, not against the resting
overdrive. The stage inverts, so the moment the drain is at its lowest the gate is at
its highest and the overdrive it must clear has grown by exactly the input amplitude.
With $\hat{V} = 0.1$ V that moves the boundary up by 0.1 V — small, but always in the
direction that makes the estimate flattering rather than safe.
''',
                    },
                ],
            },
            "build": {
                "title": "Bias for the largest symmetric swing",
                "minutes": 26,
                "brief": r'''
Module 2 asked for a drain at 7 V because 7 V is a tidy number. This time the drain
voltage is not given to you: it is whatever makes the output swing the same distance
in both directions.

As in module 2's first build, the device appears here as the 1 mA current source it is
at its operating point, with its **+ pin as the drain**. That is the right model for
this question: placing the quiescent drain voltage is a statement about how far the
output can move before it meets a ceiling, and both ceilings are set by the network
around the device rather than by the device's own curve. The probe is already on the
drain node, because that is the output.

## The specification

- the drain current is **1.00 mA** from a **12 V** supply, both already on the canvas,
- the source sits at **2.00 V**, the same lift module 2 used for bias stability,
- the overdrive is **1.00 V**, so the drain may not go below $V_S + V_{ov}$,
- the quiescent drain voltage is chosen so that the room above it and the room below it
  are **equal**.

Two resistors is the whole drawing. No gate network is needed here — the gate voltage
is module 2's problem and this exercise is about where the drain sits.

## Working it out

The drain's allowed range runs from $V_S + V_{ov}$ at the bottom to $V_{DD}$ at the top.
Put the quiescent point at the middle of that range, then let Ohm's law give you the
two resistors from the currents and voltages you now know.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "I", "x": 13, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 12},
                        {"id": "p4", "kind": "OUT", "x": 16, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [13, 2]},
                        {"a": [13, 5], "b": [16, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "I", "x": 13, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 12},
                        {"id": "p4", "kind": "OUT", "x": 16, "y": 5},
                        {"id": "p5", "kind": "R", "x": 13, "y": 3, "rot": 1, "value": 4500},
                        {"id": "p6", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 2000},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [13, 2]},
                        {"a": [13, 5], "b": [16, 5]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [13, 7], "b": [13, 8]},
                        {"a": [13, 10], "b": [13, 12]},
                    ],
                },
                "checks": [
                    {"name": "the supply reaches the drain through a resistor", "code": r'''
c.assert(c.count('V') === 1, 'Exactly one supply — the 12 V rail. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
c.assert(c.count('I') === 1,
  'One current source, standing in for the transistor at its operating point. Found ' +
  c.count('I') + '.');
c.close(c.values('I')[0], 1e-3, 0.01, 'the drain current the current source represents');
/* until a drain resistor joins the rail to the drain the supply delivers nothing, so
   this measures the drawing rather than restating what came with the canvas */
const cur = c.dc().currents;
const isup = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(isup >= 1e-3 * 0.99,
  'The 1 mA has to reach the drain from the rail through R_D. The supply is delivering ' +
  (isup * 1e6).toFixed(1) + ' µA, so the drain branch is not connected to the rail.');
'''},
                    {"name": "the source is lifted to 2.00 V", "code": r'''
const q = c.net.parts.filter(function (p) { return p.kind === 'I'; })[0];
c.assert(q, 'The current source standing in for the transistor has gone missing.');
const v = c.dc().v;
c.assert(v[q.n1] > v[q.n2],
  'The current source is upside down: its + pin is the drain and has to end up above the ' +
  'source pin. Measured ' + v[q.n1].toFixed(2) + ' V at the + pin and ' + v[q.n2].toFixed(2) +
  ' V at the other.');
c.close(v[q.n2], 2.0, 0.02, 'the source voltage, which is I_D through R_S');
'''},
                    {"name": "the drain sits at the middle of its allowed range", "code": r'''
c.close(c.vout(), 7.5, 0.01,
  'the probed drain voltage — halfway between V_S + V_ov and the supply');
'''},
                    {"name": "the two margins are equal, and each is 4.5 V", "code": r'''
const q = c.net.parts.filter(function (p) { return p.kind === 'I'; })[0];
const v = c.dc().v;
const vdd = c.values('V')[0];
const up = vdd - v[q.n1];
const down = v[q.n1] - v[q.n2] - 1.0;
c.assert(Math.abs(up - down) <= 0.12,
  'The swing is lopsided: ' + up.toFixed(2) + ' V of room upward and ' + down.toFixed(2) +
  ' V downward. Equal margins are what maximum symmetric swing means.');
c.assert(Math.min(up, down) >= 4.4,
  'Both margins should reach 4.5 V. The smaller one here is ' +
  Math.min(up, down).toFixed(2) + ' V.');
'''},
                ],
                "hints": [
                    "The drain may sit anywhere from $V_S + V_{ov} = 3$ V up to the 12 V rail. Symmetric swing means the middle of that: 7.5 V.",
                    "$R_S = V_S/I_D = 2.0/0.001 = 2$ kΩ, from the current source's lower pin down to a ground symbol.",
                    "$R_D$ has to drop $12 - 7.5 = 4.5$ V at 1 mA, so it is 4.5 kΩ, from the rail down to the current source's + pin. Type it as `4.5k`.",
                    "If the drain comes out at 12 V and the checks complain that no current is flowing, the drain resistor is drawn but not actually touching the rail — the wire has to land on the pin, not near it.",
                ],
            },
            "derive": {
                "title": "Where to put the drain, and what it is worth",
                "minutes": 11,
                "vars": ["V_DD", "V_D", "V_S", "V_ov", "I_D", "R_D"],
                "brief": r'''
The drain has a ceiling and a floor. The ceiling is the supply, because that is where
the device has stopped conducting altogether. The floor is the edge of saturation,
$V_S + V_{ov}$, because below it the square law stops applying and the gain collapses.

Everything in this derivation follows from putting the quiescent drain voltage at the
right place between those two, and it ends with a formula for $R_D$ you can use without
thinking about it again.
''',
                "steps": [
                    {
                        "prompt": "Write the room the drain has above it — the distance from its quiescent value to the ceiling.",
                        "answer": "V_{DD} - V_D",
                        "hint": "The ceiling is the supply rail itself. Subtract where the drain rests from where it may go.",
                        "deconstruct": [
                            "As the signal drives the drain current down, the drop across $R_D$ shrinks and the drain rises.",
                            "It stops rising when the current reaches zero and the whole supply appears at the drain.",
                        ],
                    },
                    {
                        "prompt": "Now the room below. The floor is the edge of saturation, one overdrive above the source. Write the downward margin.",
                        "answer": "V_D - V_S - V_{ov}",
                        "hint": "The floor is at $V_S + V_{ov}$; the margin is the quiescent drain voltage minus that.",
                        "deconstruct": [
                            "Saturation needs $V_{DS} \\ge V_{ov}$, and $V_{DS} = V_D - V_S$.",
                            "So the lowest usable drain voltage is $V_S + V_{ov}$.",
                        ],
                    },
                    {
                        "prompt": "A symmetric sine is limited by the smaller margin, so the best place for the drain makes them equal. Set the two expressions equal and solve for $V_D$.",
                        "answer": "\\frac{V_{DD} + V_S + V_{ov}}{2}",
                        "hint": "Collect the two $V_D$ terms on one side; everything else is the sum of the ceiling and the floor.",
                        "deconstruct": [
                            "$V_{DD} - V_D = V_D - V_S - V_{ov}$ gives $2V_D = V_{DD} + V_S + V_{ov}$.",
                            "Which is just the midpoint of the range between the floor and the ceiling.",
                        ],
                    },
                    {
                        "prompt": "Put that back into either margin. Write the peak swing available.",
                        "answer": "\\frac{V_{DD} - V_S - V_{ov}}{2}",
                        "hint": "Substitute into $V_{DD} - V_D$ and put the result over a common denominator.",
                        "deconstruct": [
                            "$V_{DD} - \\tfrac{1}{2}(V_{DD} + V_S + V_{ov}) = \\tfrac{1}{2}(V_{DD} - V_S - V_{ov})$.",
                            "Half the width of the allowed range, which is what a midpoint always gives.",
                        ],
                    },
                    {
                        "prompt": "The drain resistor drops $V_{DD} - V_D$ at $I_D$. Write $R_D$ in terms of $V_{DD}$, $V_S$, $V_{ov}$ and $I_D$.",
                        "answer": "\\frac{V_{DD} - V_S - V_{ov}}{2 I_D}",
                        "hint": "You have just written that drop: it is the peak swing. Divide it by the current.",
                        "deconstruct": [
                            "$R_D = (V_{DD} - V_D)/I_D$ and $V_{DD} - V_D$ is the peak swing from the previous step.",
                            "So the drop across $R_D$ at the best bias point is exactly the swing you get.",
                        ],
                    },
                ],
                "closing": r'''
Read the last line back as a design rule: **at maximum symmetric swing, the drain
resistor drops exactly as many volts as the output is allowed to swing.** For the
course stage that is 4.5 V of drop for 4.5 V of peak, and it also fixes the gain, since
$R_D$ and $g_m$ are all a gain needs. Swing, headroom and gain stop being three
independent choices at that point — which is the honest situation, and worth meeting
before a specification forces it on you.
''',
            },
            "lab": {
                "title": "Both ceilings, measured",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Clipping is arithmetic and you have just derived it. Distortion is not something to
take on trust, so measure it.

- `swing_limits(vdd, i_d, r_d, r_s, v_ov)` returns `(v_d, up, down)`: the quiescent
  drain voltage and the two margins, in volts.
- `best_drain_resistor(vdd, i_d, r_s, v_ov)` returns the $R_D$ that makes the margins
  equal.
- `harmonics(v_ov, amp, k, n)` samples the drain current
  $i_D = \tfrac{1}{2}k(V_{ov} + \hat{V}\cos\theta)^2$ over one period at `n` points and
  returns `(dc, fundamental, second)` in amperes. The mean is the DC term; the
  amplitude of the $m$-th harmonic is $\tfrac{2}{n}\sum_j i_j\cos(m\theta_j)$.
- `hd2(v_ov, amp, k)` returns the second-harmonic distortion as a fraction, **measured
  with `harmonics`** rather than from the formula. The point of the exercise is to
  watch the measurement land on $\hat{V}/(4V_{ov})$ without having been told to.

Nothing here needs NumPy; a loop over `n` samples is fast enough and shows what the
sum is doing.
''',
                "files": [{"name": "main.py", "content": r'''
"""How much signal the stage will take, and what it does to it on the way through."""

import math

K = 2e-3      # A/V^2
V_TH = 1.0    # V


def swing_limits(vdd, i_d, r_d, r_s, v_ov):
    """Return (v_d, up, down) in volts for this bias network."""
    # TODO: the drain sits at vdd - i_d * r_d and the source at i_d * r_s.
    # TODO: up is the room to the supply; down is the room to V_S + V_ov.
    return (0.0, 0.0, 0.0)


def best_drain_resistor(vdd, i_d, r_s, v_ov):
    """The drain resistor that makes the two margins equal."""
    # TODO: straight from the derivation.
    return 0.0


def harmonics(v_ov, amp, k=K, n=4096):
    """Return (dc, fundamental, second) amplitudes of the drain current, in amperes."""
    # TODO: sample i_D = k (v_ov + amp cos(theta))^2 / 2 at n points over one period.
    # TODO: dc is the mean; harmonic m has amplitude (2/n) * sum(i * cos(m theta)).
    return (0.0, 0.0, 0.0)


def hd2(v_ov, amp, k=K):
    """Second-harmonic distortion as a fraction of the fundamental, measured."""
    # TODO: call harmonics() and divide. Do not use the closed form here.
    return 0.0


if __name__ == "__main__":
    print("margins with R_D = 5 k:", swing_limits(12.0, 1e-3, 5000.0, 2000.0, 1.0))
    r_d = best_drain_resistor(12.0, 1e-3, 2000.0, 1.0)
    print("best R_D:", r_d, "ohms")
    print("margins with it:", swing_limits(12.0, 1e-3, r_d, 2000.0, 1.0))
    print("harmonics at 0.2 V of drive:", harmonics(1.0, 0.2))
    print("HD2 measured:", hd2(1.0, 0.2), " formula:", 0.2 / 4.0)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""How much signal the stage will take, and what it does to it on the way through."""

import math

K = 2e-3      # A/V^2
V_TH = 1.0    # V


def swing_limits(vdd, i_d, r_d, r_s, v_ov):
    """Return (v_d, up, down) in volts for this bias network."""
    v_s = i_d * r_s
    v_d = vdd - i_d * r_d
    return (v_d, vdd - v_d, v_d - v_s - v_ov)


def best_drain_resistor(vdd, i_d, r_s, v_ov):
    """The drain resistor that makes the two margins equal."""
    return (vdd - i_d * r_s - v_ov) / (2.0 * i_d)


def harmonics(v_ov, amp, k=K, n=4096):
    """Return (dc, fundamental, second) amplitudes of the drain current, in amperes."""
    total = 0.0
    first = 0.0
    second = 0.0
    for j in range(n):
        theta = 2.0 * math.pi * j / n
        i = 0.5 * k * (v_ov + amp * math.cos(theta)) ** 2
        total += i
        first += i * math.cos(theta)
        second += i * math.cos(2.0 * theta)
    return (total / n, 2.0 * first / n, 2.0 * second / n)


def hd2(v_ov, amp, k=K):
    """Second-harmonic distortion as a fraction of the fundamental, measured."""
    _, fundamental, second = harmonics(v_ov, amp, k)
    return second / fundamental


if __name__ == "__main__":
    print("margins with R_D = 5 k:", swing_limits(12.0, 1e-3, 5000.0, 2000.0, 1.0))
    r_d = best_drain_resistor(12.0, 1e-3, 2000.0, 1.0)
    print("best R_D:", r_d, "ohms")
    print("margins with it:", swing_limits(12.0, 1e-3, r_d, 2000.0, 1.0))
    print("harmonics at 0.2 V of drive:", harmonics(1.0, 0.2))
    print("HD2 measured:", hd2(1.0, 0.2), " formula:", 0.2 / 4.0)
'''}],
                "hints": [
                    "`swing_limits` is three subtractions. Compute the source voltage first and keep it in a local variable — the downward margin needs it and the upward one does not.",
                    "`best_drain_resistor` is `(vdd - i_d * r_s - v_ov) / (2 * i_d)`. Check it against the numbers by hand once: 12 V, 1 mA, 2 kΩ and 1 V of overdrive give 4.5 kΩ.",
                    "In `harmonics`, accumulate three running sums in one loop over `theta = 2 * math.pi * j / n`. The DC term is the plain mean, so it does *not* get the factor of two that the harmonic amplitudes do.",
                    "If the fundamental comes out at half what you expect, the factor of `2/n` has been applied to the DC term as well; if the second harmonic comes out at zero, `cos(2 * theta)` has probably become `2 * cos(theta)`.",
                ],
                "tests": [
                    {"name": "the margins are what the arithmetic says", "code": r'''
v_d, up, down = swing_limits(12.0, 1e-3, 5000.0, 2000.0, 1.0)
assert abs(v_d - 7.0) < 1e-9, f"12 V less 1 mA through 5 k is 7.00 V, got {v_d}"
assert abs(up - 5.0) < 1e-9, f"the drain can rise 5 V to reach the supply, got {up}"
assert abs(down - 4.0) < 1e-9, f"7 - 2 - 1 leaves 4 V before triode, got {down}"
'''},
                    {"name": "the best drain resistor makes them equal", "code": r'''
r_d = best_drain_resistor(12.0, 1e-3, 2000.0, 1.0)
assert abs(r_d - 4500.0) < 1e-6, f"(12 - 2 - 1) over 2 mA is 4.5 k, got {r_d}"
v_d, up, down = swing_limits(12.0, 1e-3, r_d, 2000.0, 1.0)
assert abs(v_d - 7.5) < 1e-9, f"expected the drain at 7.50 V, got {v_d}"
assert abs(up - down) < 1e-9, f"the two margins must match; got {up} and {down}"
assert abs(up - 4.5) < 1e-9, f"expected 4.5 V of peak swing, got {up}"
'''},
                    {"name": "a volt of source lift costs half a volt of swing", "code": r'''
a = swing_limits(12.0, 1e-3, best_drain_resistor(12.0, 1e-3, 2000.0, 1.0), 2000.0, 1.0)[1]
b = swing_limits(12.0, 1e-3, best_drain_resistor(12.0, 1e-3, 3000.0, 1.0), 3000.0, 1.0)[1]
assert abs(a - 4.5) < 1e-9, f"expected 4.5 V of peak with the source at 2 V, got {a}"
assert abs(b - 4.0) < 1e-9, f"lifting the source to 3 V leaves 4.0 V, got {b}"
'''},
                    {"name": "the harmonics land where the square law puts them", "code": r'''
dc, fundamental, second = harmonics(1.0, 0.2)
assert abs(dc - 1.02e-3) < 1e-9, \
    f"the mean current is 1.020 mA, not the 1.000 mA it was biased at; got {dc}"
assert abs(fundamental - 4e-4) < 1e-9, f"k V_ov amp is 0.400 mA, got {fundamental}"
assert abs(second - 2e-5) < 1e-9, f"k amp^2 / 4 is 0.020 mA, got {second}"
'''},
                    {"name": "the measurement agrees with the formula it is meant to confirm", "code": r'''
for amp in (0.05, 0.1, 0.2, 0.4):
    m = hd2(1.0, amp)
    assert abs(m - amp / 4.0) < 1e-6, \
        f"at {amp} V of drive the measurement gives {m} and the formula {amp / 4.0}"
assert abs(hd2(2.0, 0.2) - 0.025) < 1e-6, \
    f"twice the overdrive is half the distortion, so 2.5%, got {hd2(2.0, 0.2)}"
'''},
                    {"name": "distortion binds long before the rails do", "code": r'''
r_d = best_drain_resistor(12.0, 1e-3, 2000.0, 1.0)
peak = swing_limits(12.0, 1e-3, r_d, 2000.0, 1.0)[1]
drive = 0.04                     # the gate amplitude that gives 1% second harmonic
assert abs(hd2(1.0, drive) - 0.01) < 1e-6, \
    f"expected 1% at 40 mV of drive, got {hd2(1.0, drive)}"
assert drive * 9.0 < peak / 10.0, (
    "at a gain of 9 that is 0.36 V at the drain, against the 4.5 V clipping allows: "
    "the curvature binds more than ten times sooner than the rails")
'''},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Coupling, bypassing and the low-frequency end",
            "summary": "Module 4 found the top of the band. The capacitors that let a signal in and out find the bottom of it.",
            "concepts": [
                "A stage has to be connected to something at each end without either connection disturbing the operating point that module 2 worked so hard to set. A **coupling capacitor** in series does that and nothing else: an open circuit at DC, a short well above its corner.",
                "Every coupling capacitor sees the resistance on both sides of it in series with itself, and the three make a **high-pass**. At the input that resistance is $R_{sig} + (R_1\\parallel R_2)$; at the output it is $(r_o\\parallel R_D) + R_L$. Each contributes a corner at $1/(2\\pi RC)$.",
                "For the course stage: $R_1\\parallel R_2 = 167$ kΩ, so 47 nF puts the input corner at 20.3 Hz. At the output, $4.5\\,\\text{k}\\Omega + 45\\,\\text{k}\\Omega = 49.5$ kΩ, so 470 nF puts that corner at 6.8 Hz. Big resistances make coupling capacitors small, which is one more reason the gate drawing no current is worth something.",
                "The **bypass capacitor** across $R_S$ is a different animal. It is not in series with the signal; it removes the degeneration. Well above its corner it shorts $R_S$ and the gain is $-g_mR_D$; at DC it is not there and the gain is $-g_mR_D/(1+g_mR_S)$. So it produces a **pole and a zero**, not just a pole.",
                "The zero sits at $1/(2\\pi R_SC_S)$ and the pole at $(1+g_mR_S)/(2\\pi R_SC_S)$. Their ratio is exactly $1+g_mR_S$ — the same factor by which the degeneration cut the gain. The gain climbs between them and is flat outside them, which is what a pole-zero pair separated by a factor of five looks like on a Bode plot.",
                "That factor is why $C_S$ is the largest capacitor on the board. To put its pole at 20 Hz with $R_S = 2$ kΩ and $g_mR_S = 4$ takes $C_S = 5/(2\\pi\\times 2000\\times 20) \\approx 20$ µF — four hundred times the 47 nF at the input, because it is working against 2 kΩ, divided again by five.",
                "**Midband** is the window where every coupling and bypass capacitor is already a short and every parasitic capacitance is still an open. Module 3's gain is the midband gain; module 4's corner is the top of the window and these corners are the bottom.",
                "$f_L$ is set by the **highest** of the three corners, not by their sum: the one still rolling off when the others have finished. The usual design habit is to put one corner where $f_L$ belongs and push the other two a decade below it, so that only one thing is happening at the bottom of the band.",
                "A high-pass shifts phase the opposite way from a low-pass: the output **leads**, by 45° at the corner and approaching 90° well below it. Where a DC path between stages is acceptable, leaving the capacitors out is better in every respect but one — the two stages' operating points are then locked together, and any DC offset at the input is amplified along with the signal.",
            ],
            "read": [{
                "title": "Three capacitors, four hundred to one, and the corner none of them set",
                "minutes": 14,
                "body": r'''
The stage from module 2 is biased and working: gate at 4.00 V, source at 2.00 V, drain at
7.00 V, 1 mA in the drain lead. Now connect a signal generator to the gate so that it can
amplify something.

The drain goes to 12.00 V and stays there. The meter in the drain lead reads zero.

Nothing is broken. A bench generator's output is a low-impedance source referred to
*ground*, so wiring it to the gate has connected the gate to 0 V through 50 Ω. The
divider that was holding the gate at 4.00 V cannot fight that. With $V_G = 0$ and the
source still trying to sit at 2 V, $V_{GS}$ is negative, the channel is gone, and the
carefully designed operating point of module 2 lasted exactly as long as it took to plug
something in.

The fix is a capacitor in series with the signal, and every capacitor in this module is
there for that reason: to let a signal past while refusing to let anything move the DC.
What the fix costs is the bottom of the band, and the arithmetic of that cost is
surprisingly rich.

## What a series capacitor does, from the divider

Put $C_1$ between the generator and the gate. At DC a capacitor passes nothing, so the
divider is undisturbed and the bias is exactly what module 2 designed. At signal
frequencies the capacitor and the resistance at the gate form a divider, and the output is
taken across the resistance:

$$H(s) = \frac{R}{R + \dfrac{1}{sC}} = \frac{sRC}{1 + sRC}$$

Read the two ends of that. At high frequency $sRC$ is large and the ratio approaches one:
the capacitor is a wire. At low frequency it approaches $sRC$, which is proportional to
frequency, so the response falls at 20 dB per decade going down — module 4's slope, in a
mirror. And in between, $|H| = 1/\sqrt{2}$ when $\omega RC = 1$, so

$$f = \frac{1}{2\pi RC}$$

The one thing to be careful about is which $R$. The capacitor's current has to flow
through everything in its loop, so the resistance it works against is what is on *both*
sides of it, in series. At the input that is the generator's own resistance plus the bias
divider, and to a signal both legs of the divider go to ground, because the supply rail is
signal ground. So $R = R_{sig} + (R_1\parallel R_2)$, and with a bench generator's 50 Ω
against 167 kΩ the generator contributes nothing. This is exactly the network the build
**The input coupling network, and where it stops passing** asks you to draw, and its
commonest failure is putting the two divider resistors anywhere but in parallel.

## Three capacitors, three resistances

A working stage needs three. $C_1$ couples the generator in. $C_2$ couples the drain to
whatever comes next — here a 45 kΩ load — and works against $(r_o\parallel R_D) + R_L$.
And $C_S$ sits across the source resistor, not in series with anything, to hide $R_S$ from
the signal so that the gain is $-g_mR_D$ rather than $-g_mR_D/(1+g_mR_S)$.

```python
import math

GM, R_S = 2e-3, 2000.0
R_IN = 1.0 / (1.0 / 500e3 + 1.0 / 250e3)          # the divider, both legs to signal ground
R_OUT = 1.0 / (1.0 / 45e3 + 1.0 / 5e3) + 45e3     # (r_o || R_D) in series with the load

for name, c, r, boost in (("input coupling  47 nF ", 47e-9, R_IN, 1.0),
                          ("output coupling 470 nF", 470e-9, R_OUT, 1.0),
                          ("source bypass   20 uF ", 20e-6, R_S, 1.0 + GM * R_S)):
    f = boost / (2.0 * math.pi * r * c)
    print(f"{name}  works against {r / 1e3:6.1f} k   ->  corner {f:6.2f} Hz")
print(f"largest capacitor / smallest = {20e-6 / 47e-9:.0f} to 1")
```

Corners at 20.32 Hz, 6.84 Hz and 19.89 Hz, from capacitors spanning 426 to 1 in value.
That spread is not perversity, it is the resistances: 167 kΩ, 49.5 kΩ and 2 kΩ. A
capacitor working against a large resistance can be small, which is one more thing the
gate drawing no DC current pays for. The bypass capacitor has only 2 kΩ to work with and
is penalised accordingly — and there is a second factor in its line that needs explaining.

## The odd one out

The `boost` term in that program is $1 + g_mR_S$, and the bypass capacitor is the only one
that gets it. The reason is that $C_S$ is not in series with the signal path at all; it
cannot block the signal, only change how much degeneration the signal sees. So the gain
has a finite value at *both* ends of the transition — $-g_mR_D/(1+g_mR_S)$ below,
$-g_mR_D$ above — and a network that goes from one finite value to another finite value
has a zero as well as a pole.

Substituting $Z_S = R_S\parallel(1/sC_S)$ into the degenerated gain gives

$$A_v(s) = \frac{-g_mR_D\left(1 + sR_SC_S\right)}{1 + g_mR_S + sR_SC_S}$$

whose zero is at $1/(R_SC_S)$ and whose pole is at $(1+g_mR_S)/(R_SC_S)$ — the same time
constant, pushed up by exactly the factor by which the degeneration had reduced the gain.
The derivation **The pole and the zero a bypass capacitor brings with it** walks that
algebra step by step; what matters here is the consequence. The gain climbs by a factor of
five between 3.98 Hz and 19.89 Hz, and it is the pole at the top of that climb, not the
zero at the bottom, that the capacitor has to be sized for.

## Where the band actually stops

Three corners: 20.32 Hz, 19.89 Hz and 6.84 Hz. The usual rule is that $f_L$ is set by the
highest of them, because coming down in frequency that is the one that starts the
roll-off. Test the rule on this parts list.

```python
import cmath
import math

GM, R_S, CS = 2e-3, 2000.0, 20e-6
R_IN, C1 = 1.0 / (1.0 / 500e3 + 1.0 / 250e3), 47e-9
R_OUT, C2 = 1.0 / (1.0 / 45e3 + 1.0 / 5e3) + 45e3, 470e-9

def response(f):
    """Gain relative to midband: three networks in cascade."""
    s = 2j * math.pi * f
    return ((s * R_IN * C1 / (1 + s * R_IN * C1))
            * (s * R_OUT * C2 / (1 + s * R_OUT * C2))
            * ((1 + s * R_S * CS) / (1 + GM * R_S + s * R_S * CS)))

for f in (1.0, 3.0, 7.0, 20.0, 35.0, 100.0, 1000.0):
    h = response(f)
    print(f"{f:7.1f} Hz   {abs(h):.4f}  {20 * math.log10(abs(h)):+6.2f} dB"
          f"   phase {math.degrees(cmath.phase(h)):+6.1f} deg")

lo, hi = 1.0, 1000.0
for _ in range(60):
    mid = math.sqrt(lo * hi)
    if abs(response(mid)) < 0.7071067811865476:
        lo = mid
    else:
        hi = mid
print(f"overall -3 dB at {math.sqrt(lo * hi):.1f} Hz")
```

The answer is **32.0 Hz**, and no capacitor in the circuit has a corner anywhere near it.
At 20 Hz, where the two highest corners sit almost on top of each other, the stage is
already 6.4 dB down rather than 3 — each of them is taking its own 3 dB there, and the
6.84 Hz corner is contributing a fraction of a decibel besides. The "highest corner" rule
is a lower bound: corners that land together push $f_L$ half again above either of them.

Which turns the rule into a design habit rather than a formula. Choose one corner to be
$f_L$, and push the other two a decade below it, so that only one thing is happening at
the bottom of the band and the answer is the number you chose. Here that means keeping the
47 nF at the input and taking $C_S$ to 200 µF — an unattractive part, and the reason a
designer who can leave $R_S$ unbypassed and accept a gain of 2 often does.

The phase column is worth a glance too. It is measured relative to midband, so the stage's
own 180° of inversion is not in it. A high-pass *leads*: about +98° at 20 Hz with three
networks contributing, heading for +270° at the bottom. That is the opposite direction
from module 4's lag at the top of the band, and a stage that has to sit inside a feedback
loop has to have both accounted for.

## The mistake, and why it is tempting

Sizing the bypass capacitor from $1/(2\pi R_SC_S)$ — the zero — instead of from the pole.
It is the same formula that is correct for every other capacitor in the circuit, and it is
tempting for a very physical reason: $C_S$ is soldered directly across $R_S$ and nothing
else is touching it, so $R_S$ looks like the resistance it must work against.

Follow it through. Asking for 20 Hz gives $C_S = 1/(2\pi\times 2000\times 20) = 4$ µF, a
fifth of the right answer and a much nicer part. That capacitor puts the zero at 19.9 Hz
and the pole at 99.5 Hz, so the bypass network's own $-3$ dB point is at **95.4 Hz**, and at
the 20 Hz that was asked for it is 11.1 dB down instead of 3. Nearly five times the
frequency, eight decibels of error, and a Bode plot that is still climbing through the two
lowest octaves anyone will listen to.

The check that catches it costs nothing: after sizing any capacitor, ask what the gain is
at DC. For a coupling capacitor it is zero, and a single pole is the whole story. For a
bypass capacitor it is $-g_mR_D/(1+g_mR_S)$, which is not zero, and a network that ends
somewhere finite has a zero in it.

## Where this stops holding

**The corners interact.** Everything above treated each network as independent, which is
sound here only because the resistance each capacitor works against is set by the others
being either open or short. Cascade two stages with the interstage capacitor working into
a low input resistance and the loading is real, and the corners have to be solved together
rather than listed.

**A 20 µF part is an electrolytic, and an electrolytic is not a capacitor.** It is
polarised, so it depends on the 2 V of DC bias across $R_S$ being the right way round; it
has a few ohms of series resistance; and its tolerance is commonly $-20\%$ to $+80\%$. A
part 20% low moves the bypass pole from 19.9 Hz to 24.9 Hz, which on this parts list moves
$f_L$ with it. Corner frequencies at the bottom of the band are quoted to three figures in
textbooks and are worth one in practice.

**None of it is necessary.** Direct coupling — no capacitors at all — is flat to DC, and
that is what an instrumentation amplifier or anything inside a feedback loop needs. The
price is that the first stage's drain voltage becomes the second stage's gate voltage, so
the two bias designs are one design, and a millivolt of DC offset at the input arrives at
the output multiplied by the gain. Module 10's differential pair is the standard answer to
that, and it is direct-coupled for exactly this reason.

## What to carry forward

Every capacitor has a resistance it works against, and finding that resistance is the
whole problem — the formula never changes. In series with the signal, the resistance is
what sits on both sides. Across a source resistor, it is $R_S$, and the answer then gets
multiplied by $1 + g_mR_S$ because the network has a zero as well as a pole. And $f_L$ is
a property of all three corners together, not of the largest capacitor, which was chosen
by the smallest resistance and has nothing to do with it.
''',
            }],
            "quiz": {
                "title": "Where the band stops at the bottom",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The stage is fed through a 47 nF coupling capacitor into the 500 kΩ / 250 kΩ bias divider, from a source whose own resistance is negligible. Where is the input corner?",
                        "opts": ["6.8 Hz", "128 Hz", "20 Hz", "13.5 Hz"],
                        "a": 2,
                        "why": r'''
The capacitor works against $R_1 \parallel R_2 = 167$ kΩ, so
$f = 1/(2\pi \times 166.7\text{ k}\Omega \times 47\text{ nF}) = 20.3$ Hz. Using 500 kΩ
alone gives 6.8 Hz and 250 kΩ alone gives 13.5 Hz — both wrong, because to a signal the
two resistors are in parallel: one goes to ground and the other goes to $V_{DD}$, which
is the same thing at signal frequencies. 128 Hz is $1/(RC)$ with the $2\pi$ left out.
''',
                    },
                    {
                        "q": "Why is the source bypass capacitor typically hundreds of times larger than the coupling capacitors in the same circuit?",
                        "opts": [
                            "it works against $R_S$, which is small, and its pole is pushed up by a further factor of $1+g_mR_S$",
                            "it has to store the entire DC bias current",
                            "electrolytic capacitors are only made in large values",
                            "it works against $R_1 \\parallel R_2$, which is large",
                        ],
                        "a": 0,
                        "why": r'''
Two effects multiply. $R_S$ is 2 kΩ against the input network's 167 kΩ, which is
already a factor of 80; and the bypass pole sits at $(1+g_mR_S)/(R_SC_S)$ rather than
$1/(R_SC_S)$, so a further factor of 5 of capacitance is needed to drag it back down.
80 times 5 is the 400 between 47 nF and 20 µF. Nothing about it is to do with storing
bias current — no DC flows through a capacitor at all.
''',
                    },
                    {
                        "q": "Ignoring $r_o$, this stage has $g_mR_D = 10$ and $g_mR_S = 4$. What does the magnitude of the gain do as the frequency falls through the bypass capacitor's pole and zero?",
                        "opts": [
                            "it stays at 10 and then falls to zero at DC",
                            "it falls from 10 to 2 and stays there",
                            "it rises from 2 to 10",
                            "it falls from 10 to 0.4",
                        ],
                        "a": 1,
                        "why": r'''
Above the pole the capacitor is a short, $R_S$ is out of the circuit and the gain is
$g_mR_D = 10$. Below the zero the capacitor has gone and the full degeneration is back:
$g_mR_D/(1+g_mR_S) = 10/5 = 2$. Between them the response slides by that factor of 5.
It does not fall to zero at DC — a bypass capacitor is not in series with the signal,
so it cannot block it; it only stops hiding $R_S$.
''',
                    },
                    {
                        "q": "At the input coupling corner, what is the phase of the output relative to its midband value?",
                        "opts": ["−45°", "+90°", "0°", "+45°"],
                        "a": 3,
                        "why": r'''
A single high-pass has a transfer function $j\omega RC/(1+j\omega RC)$, which at
$\omega RC = 1$ is $j/(1+j)$: magnitude $1/\sqrt{2}$ and phase $+45°$. The output
*leads*, which is the opposite of what a low-pass does at its corner, and it approaches
$+90°$ far below. The phase in a real stage is the sum of all of it — this lead at the
bottom, the inversion in the middle, and module 4's lag at the top.
''',
                    },
                    {
                        "q": "A stage has an input corner at 20 Hz, an output corner at 6.8 Hz and a bypass corner at 80 Hz. What is $f_L$?",
                        "opts": [
                            "about 107 Hz, the sum of the three",
                            "about 6.8 Hz, the lowest",
                            "about 80 Hz, the highest",
                            "about 27 Hz, the geometric mean",
                        ],
                        "a": 2,
                        "why": r'''
Roughly 80 Hz. Coming down in frequency, the first corner reached is the one that
starts the roll-off, and by the time the others arrive the response is already falling —
they steepen it but do not decide where it began. So $f_L$ is set by the highest corner,
and the practical consequence is that making the *other* two capacitors bigger buys
nothing at all until the dominant one has been dealt with.
''',
                    },
                    {
                        "q": "A designer removes every coupling capacitor and connects the stages directly. What is gained and what is lost?",
                        "opts": [
                            "the response is flat to DC, but the stages' operating points are now coupled and any input offset is amplified with the signal",
                            "nothing is gained; the response is unchanged",
                            "the bandwidth at the top improves as well",
                            "the gain rises, because the capacitors were attenuating the signal",
                        ],
                        "a": 0,
                        "why": r'''
Direct coupling removes the entire low-frequency roll-off — the amplifier works down to
DC, which is exactly what an instrumentation amplifier needs. The cost is that the
first stage's drain voltage is now the second stage's gate voltage, so the two bias
designs are one design; and a millivolt of DC offset at the input becomes a
gain-times-millivolt offset at the output, which is a large fraction of the swing.
Coupling capacitors are not attenuating anything in midband, and they have nothing to
do with the top of the band.
''',
                    },
                ],
            },
            "build": {
                "title": "The input coupling network, and where it stops passing",
                "minutes": 26,
                "brief": r'''
This is the small-signal input of the stage from module 2, drawn as a signal sees it.

The gate divider is 500 kΩ from the supply and 250 kΩ to ground — and to a signal
those are **both** resistors to ground, because the supply rail is signal ground. The
source is a 1 V test generator, so whatever the probe reads is the transfer directly.

## What to draw

- the 1 V source is already on the canvas,
- a **coupling capacitor in series** between the source and the gate node — in series,
  not to ground, or the network becomes a low-pass and blocks the wrong end of the band,
- the two divider resistors, **both** from the gate node to ground,
- a probe on the gate node.

## What it must do

- pass the signal essentially untouched at 2 kHz, with a phase shift of a degree or two,
- pass almost nothing at 1 Hz, with the output leading by more than 60°,
- have its **−3 dB corner at 20 Hz**: the amplitude there is $1/\sqrt{2}$ of the
  midband amplitude.

## Working it out

The capacitor sees the two divider resistors in parallel. Put that resistance and the
20 Hz corner into $f = 1/(2\pi RC)$ and solve for $C$; the arithmetic gives 47.7 nF and
the nearest standard value, 47 nF, lands at 20.3 Hz. Type it as `47n`.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 8]},
                        {"a": [3, 4], "b": [3, 2]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 8},
                        {"id": "p2", "kind": "C", "x": 7, "y": 3, "rot": 1, "value": 4.7e-08},
                        {"id": "p3", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 500000},
                        {"id": "p4", "kind": "GND", "x": 11, "y": 11},
                        {"id": "p5", "kind": "R", "x": 15, "y": 8, "rot": 1, "value": 250000},
                        {"id": "p6", "kind": "GND", "x": 15, "y": 11},
                        {"id": "p7", "kind": "OUT", "x": 13, "y": 6},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 8]},
                        {"a": [3, 4], "b": [3, 2]},
                        {"a": [3, 2], "b": [7, 2]},
                        {"a": [7, 4], "b": [7, 6]},
                        {"a": [7, 6], "b": [15, 6]},
                        {"a": [11, 6], "b": [11, 7]},
                        {"a": [15, 6], "b": [15, 7]},
                        {"a": [11, 9], "b": [11, 11]},
                        {"a": [15, 9], "b": [15, 11]},
                    ],
                },
                "checks": [
                    {"name": "the source reaches the gate through a capacitor, not into one", "code": r'''
c.assert(c.count('V') === 1, 'One signal source. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 1, 0.001, 'the test signal amplitude');
c.assert(c.count('C') === 1,
  'Exactly one capacitor — the coupling capacitor. Found ' + c.count('C') + '.');
const cap = c.net.parts.filter(function (p) { return p.kind === 'C'; })[0];
c.assert(cap.n1 !== 0 && cap.n2 !== 0,
  'A coupling capacitor goes in series with the signal, from the source to the gate node. ' +
  'This one has an end on ground, which makes it a low-pass and blocks the wrong half ' +
  'of the spectrum.');
'''},
                    {"name": "both halves of the divider hang on the gate node", "code": r'''
const out = c.outNode();
const legs = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(legs.length === 2,
  'The divider is two resistors, and in the small-signal circuit BOTH run from the gate ' +
  'node to ground, because V_DD is signal ground. Found ' + legs.length +
  ' resistor(s) between the probed node and ground.');
const cond = legs.reduce(function (s, p) { return s + 1 / p.value; }, 0);
c.close(1 / cond, 166666.7, 0.03,
  'R1 in parallel with R2, which is the resistance the coupling capacitor works against');
'''},
                    {"name": "in midband the capacitor is invisible", "code": r'''
c.close(c.gain(2000), 1.0, 0.02,
  'the amplitude at the gate at 2 kHz — well above the corner, the network should pass ' +
  'the whole 1 V');
c.assert(Math.abs(c.phase(2000)) < 5,
  'Well above the corner the coupling capacitor should shift the phase by a degree or ' +
  'two. Measured ' + c.phase(2000).toFixed(1) + '°.');
'''},
                    {"name": "it is a high-pass: the bottom of the band is blocked, and the phase leads", "code": r'''
const mid = c.gain(2000);
c.assert(c.gain(1) < 0.1 * mid,
  'At 1 Hz almost nothing should get through — that is what a coupling capacitor is for. ' +
  'This network is passing ' + (100 * c.gain(1) / mid).toFixed(1) + '% of its midband value.');
c.assert(c.phase(1) > 60,
  'A high-pass leads, approaching +90° far below the corner. Measured ' +
  c.phase(1).toFixed(1) + '°, which is what a low-pass would give — check which way round ' +
  'the capacitor and the resistors are.');
'''},
                    {"name": "the corner is at 20 Hz", "code": r'''
const ratio = c.gain(20) / c.gain(2000);
c.close(ratio, 0.7071, 0.03,
  'the amplitude at 20 Hz as a fraction of midband — at the -3 dB corner it is 1/sqrt(2)');
'''},
                ],
                "hints": [
                    "The two divider resistors are in parallel as far as the signal is concerned: $500\\,\\text{k} \\parallel 250\\,\\text{k} = 167$ kΩ. Draw each of them from the gate node to its own ground symbol.",
                    "$C = 1/(2\\pi Rf) = 1/(2\\pi \\times 166667 \\times 20) = 47.7$ nF. Type `47n` — the nearest standard value, and it lands the corner at 20.3 Hz, inside the tolerance.",
                    "The capacitor goes *between* two nodes that are both live: the source's top terminal and the gate node. If either end of it is on a ground symbol, it is a decoupling capacitor rather than a coupling one, and it will do the opposite of what is wanted.",
                    "If the phase at 1 Hz comes out near −90° rather than +90°, the capacitor and the resistors have been swapped: the resistors go to ground and the capacitor goes in the signal path.",
                ],
            },
            "derive": {
                "title": "The pole and the zero a bypass capacitor brings with it",
                "minutes": 12,
                "vars": ["g_m", "R_D", "R_S", "C_S", "s", "A_v", "Z_S"],
                "brief": r'''
A coupling capacitor gives a pole and nothing else. The bypass capacitor across $R_S$
gives a pole *and* a zero, and the reason is worth seeing rather than memorising: the
capacitor does not interrupt the signal path, it changes the amount of degeneration,
and the gain has a different finite value at each end of the transition.

Start from the degenerated gain with the source impedance left general,

$$A_v = \frac{-g_mR_D}{1 + g_mZ_S}$$

and put the parallel pair into it.
''',
                "steps": [
                    {
                        "prompt": "Write the impedance of $R_S$ in parallel with $C_S$, as a function of $s$.",
                        "answer": "\\frac{R_S}{1 + s R_S C_S}",
                        "hint": "Product over sum, with $1/(sC_S)$ for the capacitor. Multiply numerator and denominator by $sC_S$ to clear the compound fraction.",
                        "deconstruct": [
                            "$Z_S = R_S \\cdot \\frac{1}{sC_S} \\big/ \\left(R_S + \\frac{1}{sC_S}\\right)$.",
                            "Multiplying top and bottom by $sC_S$ leaves $R_S/(1 + sR_SC_S)$.",
                        ],
                    },
                    {
                        "prompt": "Substitute that into $A_v = -g_mR_D/(1 + g_mZ_S)$ and tidy it into a single ratio of polynomials in $s$.",
                        "given": "The denominator will need a common factor of $1 + sR_SC_S$ before it can be inverted.",
                        "answer": "\\frac{-g_m R_D (1 + s R_S C_S)}{1 + g_m R_S + s R_S C_S}",
                        "hint": "$1 + g_mR_S/(1+sR_SC_S)$ becomes $(1 + sR_SC_S + g_mR_S)/(1+sR_SC_S)$; dividing by that multiplies the top by $1+sR_SC_S$.",
                        "deconstruct": [
                            "Put the 1 over the same denominator: $\\frac{1 + sR_SC_S + g_mR_S}{1 + sR_SC_S}$.",
                            "Dividing by a fraction multiplies by its reciprocal, which lifts $1 + sR_SC_S$ into the numerator.",
                        ],
                    },
                    {
                        "prompt": "The zero is the frequency at which the numerator vanishes. Write it as a positive frequency in rad/s.",
                        "answer": "\\frac{1}{R_S C_S}",
                        "hint": "Set $1 + sR_SC_S = 0$ and quote the magnitude of the root.",
                        "deconstruct": [
                            "$s = -1/(R_SC_S)$, so the zero sits at that distance from the origin.",
                            "It is the plain time constant of $R_S$ and $C_S$, with no $g_m$ in it at all.",
                        ],
                    },
                    {
                        "prompt": "And the pole, from the denominator.",
                        "answer": "\\frac{1 + g_m R_S}{R_S C_S}",
                        "hint": "Set $1 + g_mR_S + sR_SC_S = 0$ and divide through by $R_SC_S$.",
                        "deconstruct": [
                            "$s = -(1 + g_mR_S)/(R_SC_S)$.",
                            "Read it as the same time constant, but working against $R_S \\parallel (1/g_m)$ rather than $R_S$ alone.",
                        ],
                    },
                    {
                        "prompt": "Write the ratio of the pole frequency to the zero frequency.",
                        "answer": "1 + g_m R_S",
                        "hint": "Divide one by the other; $R_SC_S$ cancels.",
                        "deconstruct": [
                            "Both frequencies carry the same $1/(R_SC_S)$.",
                            "What is left is the factor by which degeneration reduced the gain in the first place.",
                        ],
                    },
                ],
                "closing": r'''
The gain climbs by $1 + g_mR_S$ between the zero and the pole, and the two are separated
by exactly that factor — which is why the transition looks the same on every Bode plot
of a degenerated stage regardless of the numbers. Two consequences worth keeping. The
capacitor must be sized against the **pole**, not the zero, or the response is still
climbing at the frequency you meant to be flat at. And with $g_mR_S = 4$ the pole is
five times the zero, so $C_S$ has to be five times what a naive $1/(2\pi R_SC_S)$
calculation suggests — which is where most of the 20 µF comes from.
''',
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "The source follower and the common-gate stage",
            "summary": "The same device wired two other ways, neither of which is trying to give you voltage gain.",
            "concepts": [
                "One device, three ways to wire it. The signal goes in at one terminal, comes out at another, and the third is common to both — which is what the three names mean. Everything else in analogue electronics is these three in combination.",
                "**Common-drain**, always called the **source follower**: in at the gate, out at the source. The source sits one $V_{GS}$ below the gate and follows it, so $A_v = g_mR_L/(1+g_mR_L)$, which is always less than one and never inverts.",
                "The point of it is not gain. Looking back into the source terminal, the stage has an output resistance of $1/g_m$ — 500 Ω at 1 mA, against the common-source stage's 4.5 kΩ. What the follower buys is the ability to drive something without the gain collapsing.",
                "And it is bought with current: $1/g_m = 1/\\sqrt{2kI_D}$, so halving the output resistance costs four times the bias current. A follower that has to look like 50 Ω is an expensive object.",
                "The follower's bandwidth into a load capacitance is $1/(2\\pi (1/g_m) C_L) = g_m/(2\\pi C_L)$ — which is precisely the **gain-bandwidth product** of a common-source stage built from the same device with the same $C_L$. The follower is module 4's bargain taken to its limit: all of the product spent on speed, none of it on gain. For this device with $C_L = 354$ pF that is 900 kHz at a gain of one, against 100 kHz at a gain of nine.",
                "**Common-gate**: in at the source, out at the drain, gate held at a fixed voltage. The gain is $+g_m(r_o\\parallel R_D)$ — the same magnitude as common-source, and *not* inverting.",
                "Its input resistance is about $1/g_m$, and the low value is the reason to use it. When what arrives is a current rather than a voltage — a photodiode, a coaxial line that has to be terminated, the drain of another transistor — you want an input that does not let the node's voltage move. The common-gate stage takes current in at a low impedance and delivers it to a high one, which is what a current buffer is.",
                "In one line each: common-source gives voltage gain and inverts; common-drain gives current gain, a gain of about one, and a low output resistance; common-gate gives voltage gain without inverting, and a low input resistance. Choosing between them is choosing which impedance you need at which end.",
            ],
            "read": [{
                "title": "The 600-ohm load that ate the gain, and the terminal that gives it back",
                "minutes": 14,
                "body": r'''
The stage from module 3 measures a gain of 9.0 on the bench with nothing on its output.
Connect the thing it was built for — a 600 Ω line input, a small loudspeaker, the input of
a piece of test gear — and measure again.

```text
   load on the drain        measured gain
   open circuit                  9.00
   45 kohm                       8.18
   4.5 kohm                      4.50
   600 ohm                       1.06
```

Nine has become one. Nothing in the amplifier changed; the load did. And the instinct that
follows — the stage is short of gain, so add gain — is wrong in a way that is worth
several pages, because the amplifier is not short of gain. It is delivering its gain at
the wrong impedance.

## Why the drain cannot help

Module 3's derivation says where the trouble is. The transistor is a current source of
$g_mv_{gs}$, and the gain is that current times whatever resistance sits at the drain node.
Everything at that node is in parallel, so adding a load can only *reduce* the resistance,
and 600 Ω in parallel with 4.5 kΩ is 529 Ω. The output resistance of a common-source stage
is $r_o \parallel R_D = 4.5$ kΩ, and a source of 4.5 kΩ driving 600 Ω keeps an eighth of
what it had. That is not a defect in the design; it is what 4.5 kΩ means.

So the question is whether the transistor has anywhere else to put its output. It has
three terminals; module 3 used the gate as the input, the drain as the output and the
source as the terminal common to both. There are two other assignments, and this module is
about what they are good for.

## Take the output at the source

Leave the input at the gate and take the output at the *source*. Put the load there, run
the drain straight to the supply — signal ground — and work through the small-signal
circuit.

The gate is driven by $v_{in}$ and the source now sits at $v_{out}$, so the controlling
voltage is no longer the input:

$$v_{gs} = v_{in} - v_{out}$$

The device's small-signal drain current is $g_mv_{gs} = g_m(v_{in} - v_{out})$, and with
the drain at signal ground all of that current arrives at the source node and flows out
through $R_L$. So

$$v_{out} = g_m\left(v_{in} - v_{out}\right)R_L$$

which is one equation in one unknown rather than something to be read off. Gathering the
$v_{out}$ terms:

$$A_v = \frac{v_{out}}{v_{in}} = \frac{g_mR_L}{1 + g_mR_L}$$

That is always less than one and never inverts. Which sounds like a bad trade until you
ask the other question. Set $v_{in} = 0$, drive the source node with a test voltage $v$,
and $v_{gs} = -v$, so the device pulls $g_mv$ out of the test source: the resistance
looking back into the source terminal is $v/(g_mv) = 1/g_m$. At 1 mA that is **500 Ω**,
against the drain's 4.5 kΩ, from the same device at the same current.

Read the gain expression again with that in hand and it stops being a formula. $g_mR_L/(1
+ g_mR_L)$ is $R_L/(R_L + 1/g_m)$: a plain voltage divider between $1/g_m$ and the load.
The follower is a voltage source equal to its input, sitting behind $1/g_m$ — a Thévenin
picture, and the one the derivation **The follower, from its own small-signal circuit**
ends on. Everything else about a follower follows from it.

## What that is worth, and what it costs

```python
import math

K, GM, RO, R_D, R_L = 2e-3, 2e-3, 45e3, 5e3, 600.0

r_out_cs = RO * R_D / (RO + R_D)
a_cs = GM * r_out_cs
print(f"common-source: R_out = {r_out_cs:.0f} ohm   A = {a_cs:.3f} unloaded,"
      f" {GM / (1 / RO + 1 / R_D + 1 / R_L):.3f} into {R_L:.0f} ohm")
for i_d in (1e-3, 11.1e-3, 56.25e-3):
    gm = math.sqrt(2 * K * i_d)
    a_f = R_L / (R_L + 1 / gm)
    print(f"follower at {i_d * 1e3:6.2f} mA:  1/gm = {1 / gm:6.1f} ohm"
          f"   A_follower = {a_f:.3f}   cascade = {a_cs * a_f:.3f}")
```

The follower's input is a gate, so it takes nothing from the stage in front of it and that
stage keeps its full 9.00. Put a 1 mA follower after it and the pair delivers 4.91 into
600 Ω, against 1.06 for the direct connection. Take the follower to 11.1 mA and it delivers
7.20; to 56.25 mA and it delivers 8.10.

Those currents are the whole story of the follower. $1/g_m = 1/\sqrt{2kI_D}$, so halving
the output resistance costs *four times* the bias current — the same square root that
module 4 met buying bandwidth and module 5 met buying linearity. Going from 0.545 to 0.900
of the signal took fifty-six times the current. A follower asked to look like 50 Ω is an
expensive object, and module 11 is about paying for one.

There is a second thing a low output resistance buys, and the sandbox **The same product,
spent two different ways** is where to see it. A follower driving a load capacitance $C_L$
has a corner at $1/(2\pi(1/g_m)C_L) = g_m/(2\pi C_L)$ — which is exactly the
gain-bandwidth product of a common-source stage built from the same device with the same
$C_L$. For this device with 354 pF that is 900 kHz at a gain of one, against 100 kHz at a
gain of nine. The follower does not beat module 4's rule; it obeys it exactly, and spends
the entire product on speed.

## The third assignment

Input at the gate, output at the drain: common-source. Input at the gate, output at the
source: common-drain, the follower. That leaves input at the *source*, output at the drain,
gate held at a fixed voltage — the **common-gate** stage.

Its analysis is two lines, because the gate at signal ground means $v_{gs} = -v_{in}$
directly. So $i_d = -g_mv_{in}$, that current is drawn through the drain resistance, and

$$A_v = +g_m\left(r_o \parallel R_D\right)$$

Same magnitude as common-source, and **no inversion** — because driving the source up
reduces $V_{GS}$, which reduces the drain current, which lets the drain rise. And the
input, being the source terminal, has the resistance the last section computed: about
$1/g_m$, 500 Ω.

A 500 Ω input looks like a defect until you ask what is arriving. A photodiode delivers a
current. A terminated coaxial line has to see 50 Ω or it reflects. The drain of another
transistor is a current source. In all three cases the thing to do with the signal is to
accept the current without letting the node's voltage move, and a low input resistance is
precisely a node whose voltage does not move. The common-gate stage takes current in at a
low impedance and hands it out at a high one, which is what a current buffer is.

## The mistake, and why it is tempting

Answering a loading problem with more gain. The measurement says 1.06 where the
specification says 9, the shortfall is in gain, and a common-source stage is a machine for
producing gain — so add another one.

```python
GM, RO, R_D = 2e-3, 45e3, 5e3

def cs_gain(r_load):
    return GM / (1 / RO + 1 / R_D + 1 / r_load)

a1 = GM * RO * R_D / (RO + R_D)
for r_load in (600.0, 300.0):
    print(f"load {r_load:5.0f} ohm   two common-source stages {a1 * cs_gain(r_load):5.2f}"
          f"   one stage + an 11 mA follower {a1 * r_load / (r_load + 150.08):5.2f}")
```

It works, on the bench, into that load: 9.53 against the follower's 7.20. And then someone
plugs in a 300 Ω load instead and the two-stage amplifier falls to 5.06 — it has lost 47%
of its gain — while the amplifier with the follower on the end falls to 6.00, losing 17%,
and is now the better of the two. The second common-source stage bought a number, not a
property. Its output resistance is still 4.5 kΩ, so its gain is still a function of what
anyone chooses to hang on it, and along the way it has cost a stage's worth of noise, power
and bandwidth.

The temptation is real because the symptom genuinely is a small number where a large one
was wanted. The habit worth forming is to ask, before adding anything, what the *output
resistance* of the existing stage is and how it compares with the load. When the load is
smaller, the problem is impedance and no amount of gain will fix it.

## Where this stops holding

**$r_o$ was dropped from the follower.** It sits in parallel with $R_L$, which with a few
hundred ohms against 45 kΩ costs well under a per cent. Drive a genuinely high-impedance
load and it is the whole story: with an ideal current-source bias and no load at all the
follower's gain is $g_mr_o/(1+g_mr_o) = 90/91 = 0.989$, not 1. A follower never quite
reaches one, and the reason it does not is $r_o$.

**The body effect makes it worse.** A follower's source moves with the signal, so if the
body is tied to ground — as it is in most discrete parts — then $V_{SB}$ moves too and the
threshold moves with it. That is a second controlled source, $g_{mb}v_{bs}$, sitting in
exactly the same place as the first: the gain becomes $g_mR_L/(1+(g_m+g_{mb})R_L)$ and the
output resistance $1/(g_m+g_{mb})$. With the usual $g_{mb} \approx 0.2g_m$ the follower's
ceiling is not 1.0 but about 0.83, however large the load. Module 1 flagged the body effect
as something this course ignores; this is the place where ignoring it costs a fifth of the
answer.

**Common-gate's input resistance depends on the drain.** $1/g_m$ assumed the drain was held
at a fixed voltage. The honest expression is $(R_D + r_o)/(1 + g_mr_o)$, which with
$R_D = 5$ kΩ gives 549 Ω — 10% above $1/g_m$, and ignorable. Give the same stage the
active load of module 8, $R_D = 45$ kΩ, and it gives 989 Ω, nearly twice $1/g_m$. The
input resistance of a common-gate stage is not a property of the device alone, and a
circuit that was terminating a line correctly can stop doing so because someone improved
its load.

## What to carry forward

One device, three assignments, and the difference between them is which impedance appears
at which end. Common-source: high in, 4.5 kΩ out, gain 9, inverting. Common-drain: high in,
500 Ω out, gain a shade under one, not inverting. Common-gate: 500 Ω in, high out, gain 9,
not inverting. Nothing here changes what the device can do — every one of these numbers is
built from the same $g_m$ and $r_o$ at the same 1 mA — and choosing between them is
choosing where to spend that, not how much of it you have.
''',
            }],
            "sandbox": {
                "title": "The same product, spent two different ways",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"K": 1, "wn": 200, "zeta": 0.71},
                "brief": r'''
The top plot is magnitude in decibels against frequency, the bottom is phase, and both
frequency axes are logarithmic. $K$ is the low-frequency gain and $\omega_n$ is the
corner; with $\zeta$ left at 0.71 that corner is the −3 dB point to within half a
percent, which is the reading you want.

The picture opens on a **source follower**: a gain of one, and a corner an order of
magnitude further out than anything module 4 managed. Nothing here is a second-order
circuit — a follower and a common-source stage each have one pole, so the slope above
the corner is half as steep as what this visualiser draws — but the *positions* are
honest, and it is the positions this module is about.

Work $K$ and $\omega_n$ against each other and watch what refuses to change.
''',
                "notice": [
                    "At the opening values the magnitude curve is flat at 0 dB across most of the plot, and the amber corner marker sits at −3 dB at $\\omega = 200$. A gain of one is 0 dB: the follower hands back exactly what it was given, and the whole of what the device can do has gone into how quickly it hands it back.",
                    "Now set $K$ to 9 and $\\omega_n$ to 22 — the common-source stage of module 4, near enough. The flat part lifts to 19 dB and the corner slides a decade to the left. Multiply the two settings out in absolute terms rather than decibels: $1 \\times 200$ and $9 \\times 22$ are the same number, and that number is $g_m/(2\\pi C_L)$.",
                    "Push it to the other extreme: $K = 20$ with $\\omega_n = 10$. The flat part is 26 dB and the corner is at 10 — the product is still 200. There is a straight line's worth of settings here, and a real device lets you slide along it and nowhere else.",
                    "Put $\\omega_n$ back to 200 and read the lower plot. The phase passes through exactly −90° at the corner whatever $\\zeta$ is, and it has begun to bend long before the magnitude has: at $\\omega = 20$, a decade below the corner, the magnitude is still flat while the phase has already moved several degrees. That gap is why an amplifier inside a feedback loop can be in trouble at frequencies where its gain still looks perfectly healthy.",
                    "Note what this picture cannot show you: the follower's real gain is $g_mR_L/(1+g_mR_L)$, which is just *under* one, and how far under depends on the load. Set $K$ to 0.7 to see a follower driving 1 kΩ at $g_m = 2$ mA/V — the corner does not move, because the same $1/g_m$ sets both.",
                ],
            },
            "quiz": {
                "title": "Which terminal is doing what",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A source follower biased at 1 mA ($g_m = 2$ mA/V) drives a 1 kΩ load. What is its voltage gain?",
                        "opts": ["2.0", "0.5", "0.667", "1.0"],
                        "a": 2,
                        "why": r'''
$A_v = g_mR_L/(1+g_mR_L) = 2/(1+2) = 0.667$. Read the formula as a divider between the
follower's own output resistance $1/g_m = 500$ Ω and the 1 kΩ load, because that is
exactly what it is: 1000/1500. A gain of one is what a follower approaches when the
load is much larger than $1/g_m$, and it never exceeds one — a value above one would
mean the source moving further than the gate that is dragging it.
''',
                    },
                    {
                        "q": "What is the output resistance of that follower, looking back into the source terminal?",
                        "opts": ["500 Ω", "45 kΩ", "2 kΩ", "4.5 kΩ"],
                        "a": 0,
                        "why": r'''
$1/g_m = 1/0.002 = 500$ Ω. It is not $r_o$: $r_o$ is what you see looking into the
*drain*, and 45 kΩ is what the common-source stage of module 3 offered its load. The
whole reason a follower is put on the end of a signal chain is that 500 Ω is nine times
lower than the 4.5 kΩ a common-source stage would present, and it is the same device at
the same current.
''',
                    },
                    {
                        "q": "That follower is asked for a gain of 0.95 into the same 1 kΩ. Roughly what bias current does it need?",
                        "opts": ["about 4 mA", "about 90 mA", "about 19 mA", "about 2 mA"],
                        "a": 1,
                        "why": r'''
0.95 needs $g_mR_L = 19$, so $g_m = 19$ mA/V, and $I_D = g_m^2/(2k) = (0.019)^2/0.004
= 90$ mA. Ninety times the bias current for a gain that has gone from 0.667 to 0.95.
This is the square-root law biting hard: transconductance is bought with current at a
worsening rate, and a follower asked for a very low output resistance is one of the
places in analogue design where the bill is enormous.
''',
                    },
                    {
                        "q": "A common-gate stage takes its input at the source. What is its input resistance, and why is a low value the point?",
                        "opts": [
                            "about $1/g_m$, so the node's voltage barely moves and the stage accepts a current cleanly",
                            "about $r_o$, so it does not load the source",
                            "infinite, because the gate takes no current",
                            "about $R_D$, so it matches the drain",
                        ],
                        "a": 0,
                        "why": r'''
About $1/g_m$ — 500 Ω here. It is low on purpose: a photodiode, a terminated coaxial
line or the drain of another transistor delivers a *current*, and the way to accept a
current faithfully is to give it a node whose voltage does not move. The infinite input
resistance belongs to the common-source and common-drain stages, where the signal
arrives at the gate.
''',
                    },
                    {
                        "q": "Which of the three configurations inverts?",
                        "opts": [
                            "common-source and common-gate, but not common-drain",
                            "common-source only",
                            "all three",
                            "common-drain only",
                        ],
                        "a": 1,
                        "why": r'''
Only common-source. In it, more gate voltage means more drain current, more drop across
$R_D$ and therefore a lower drain — the 180° of module 3. In common-gate, the input at
the source *reduces* $V_{GS}$ when it goes up, so the drain current falls and the drain
rises: same magnitude, no inversion. And the follower's output tracks its input by
definition. Sign is not decoration; it decides whether a feedback loop settles or runs
away.
''',
                    },
                    {
                        "q": "The same device and the same 354 pF of load capacitance are used in a common-source stage and in a follower. How do the bandwidths compare?",
                        "opts": [
                            "100 kHz and 900 kHz — the follower's bandwidth equals the common-source stage's gain-bandwidth product",
                            "both 100 kHz, since the capacitance is the same",
                            "100 kHz and 11 kHz — the follower is slower",
                            "900 kHz each",
                        ],
                        "a": 0,
                        "why": r'''
The corner is $1/(2\pi RC_L)$ with $R$ the resistance at the output node. For the
common-source stage $R = r_o \parallel R_D = 4.5$ kΩ, giving 100 kHz at a gain of nine.
For the follower $R = 1/g_m = 500$ Ω, giving 900 kHz at a gain of about one. Nine times
the bandwidth for a ninth of the gain: the same $g_m/(2\pi C_L)$, spent differently.
Nothing about the follower breaks module 4's rule — it obeys it exactly.
''',
                    },
                ],
            },
            "derive": {
                "title": "The follower, from its own small-signal circuit",
                "minutes": 12,
                "vars": ["g_m", "R_L", "v_in", "v_out", "v_gs", "i_d", "A_v", "r_o"],
                "brief": r'''
The common-source result was easy because the source was held at signal ground: $v_{gs}$
was simply the input. Here the source is the output, so $v_{gs}$ depends on the answer,
and the algebra has to be closed rather than read off.

Take $r_o$ as large enough to ignore — with $R_L$ of a few kilohms against 45 kΩ that
costs a few percent — and work in the small-signal circuit: a controlled current source
$g_mv_{gs}$ from drain to source, the drain at signal ground, and $R_L$ from the source
node to ground.
''',
                "steps": [
                    {
                        "prompt": "The gate is driven by $v_{in}$ and the source sits at $v_{out}$. Write $v_{gs}$.",
                        "answer": "v_{in} - v_{out}",
                        "hint": "It is the definition: the gate voltage minus the source voltage, both measured as small-signal quantities.",
                        "deconstruct": [
                            "In the common-source stage the source was at signal ground, so $v_{gs}$ was just $v_{in}$.",
                            "Here it is not, and that difference is the whole of the feedback in a follower.",
                        ],
                    },
                    {
                        "prompt": "The device's small-signal drain current is $g_mv_{gs}$. Write $i_d$ in terms of $v_{in}$ and $v_{out}$.",
                        "answer": "g_m (v_{in} - v_{out})",
                        "hint": "Substitute the previous line into $i_d = g_mv_{gs}$; keep the bracket.",
                        "deconstruct": [
                            "$g_m$ multiplies the whole gate-source voltage, not just the input.",
                            "Notice the current already depends on the output — that is why this needs solving rather than evaluating.",
                        ],
                    },
                    {
                        "prompt": "That current flows out of the source terminal into $R_L$. Write $v_{out}$ in terms of $v_{in}$, $v_{out}$, $g_m$ and $R_L$.",
                        "answer": "g_m (v_{in} - v_{out}) R_L",
                        "hint": "Ohm's law on $R_L$: the output voltage is the current through it times its resistance.",
                        "deconstruct": [
                            "The drain is at signal ground, so all of $i_d$ arrives at the source node.",
                            "$v_{out} = i_dR_L$, with $i_d$ from the previous step.",
                        ],
                    },
                    {
                        "prompt": "Solve that for the voltage gain $A_v = v_{out}/v_{in}$.",
                        "answer": "\\frac{g_m R_L}{1 + g_m R_L}",
                        "hint": "Expand the bracket, gather the $v_{out}$ terms on the left, then divide.",
                        "deconstruct": [
                            "$v_{out}(1 + g_mR_L) = g_mR_Lv_{in}$.",
                            "Divide both sides by $v_{in}(1+g_mR_L)$.",
                        ],
                    },
                    {
                        "prompt": "For the output resistance, set $v_{in} = 0$ and drive the source node with a test voltage $v$. The current flowing *into* the node from the test source is $-i_d$. Write $R_{out} = v/(-i_d)$ in terms of $g_m$.",
                        "answer": "\\frac{1}{g_m}",
                        "hint": "With the gate grounded, $v_{gs} = -v$, so $i_d = -g_mv$ and the test source is supplying $g_mv$.",
                        "deconstruct": [
                            "$v_{gs} = 0 - v = -v$, so $i_d = -g_mv$: the device is pulling current *out* of the test source.",
                            "$R_{out} = v/(g_mv) = 1/g_m$, and $R_L$ does not appear because it was in parallel with the test source, not part of the device.",
                        ],
                    },
                ],
                "closing": r'''
Read the gain as a divider and the follower stops being a special case: it is a voltage
source of $v_{in}$ behind a resistance of $1/g_m$, and $R_L/(R_L + 1/g_m)$ is what any
divider does. That Thévenin picture is the one to carry — it makes the loaded gain
obvious, it makes the bandwidth into a capacitive load obvious, and it is the model the
output-stage module works with directly. Including $r_o$ changes $R_L$ to
$R_L \parallel r_o$ and moves nothing else, which is why it is usually left out of the
first pass.
''',
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Current mirrors and the active load",
            "summary": "A resistor at the drain is asked to be large and to drop nothing. A transistor can do both.",
            "concepts": [
                "The drain resistor has two incompatible jobs. The gain wants it large, because $A_v = -g_mR_D$; the headroom wants it small, because everything it drops is swing that no longer exists. At 1 mA a 45 kΩ drain resistor would need 45 V across it, and the supply is 12 V.",
                "A current source breaks the link. Ideally it has infinite small-signal resistance and needs only about one overdrive of DC across it, so it can be large *and* cheap in volts. That is the entire argument for an **active load**.",
                "The **current mirror** is how a current source gets built out of transistors. Two matched devices share a gate-source voltage. The reference device has its gate tied to its drain — which forces $V_{DS} = V_{GS}$, and since $V_{GS} > V_{ov}$ always, that device is guaranteed to be in saturation — and it develops whatever $V_{GS}$ the reference current demands. The output device sees the same $V_{GS}$ and carries the same current.",
                "The ratio is geometry, not resistance: $I_{out}/I_{ref} = (W/L)_2/(W/L)_1$. Currents are multiplied and divided by drawing devices wider or narrower, and geometry ratios on one die match far better than resistor values do.",
                "Tying gate to drain has a small-signal consequence worth knowing on its own. The diode-connected device is not a current source at all: driving its terminals with $v$ produces $g_mv$ from the controlled source and $v/r_o$ through $r_o$, so it looks like $1/(g_m + 1/r_o) \\approx 1/g_m$ — 500 Ω here, not 45 kΩ. One wire turns the best current source in the circuit into the worst.",
                "The *output* device keeps its $r_o$, and that is the honest resistance of a real current source: $r_o = V_A/I_D = 45$ kΩ at 1 mA. A current source is only as stiff as the Early voltage of the device making it.",
                "With an active load the drain sees $r_o$ of the amplifier in parallel with $r_o$ of the load: 22.5 kΩ. The gain is $g_m \\times 22.5\\,\\text{k}\\Omega = 45$ — half the intrinsic gain of 90, five times what the 5 kΩ resistor gave, and it hands back 5 V of headroom while doing it.",
                "What it does not do is move the gain-bandwidth product. With the same $C_L = 354$ pF the corner falls from 100 kHz to 20 kHz, and $45 \\times 20\\text{ kHz} = 900$ kHz, the same number as module 4. An active load converts *headroom* into gain, not bandwidth into gain.",
                "Matching decides whether any of this works. A threshold mismatch $\\Delta V_{th}$ between the two mirror devices gives a fractional current error of $2\\Delta V_{th}/V_{ov}$ — 5 mV of mismatch at a 1 V overdrive is 1%. A larger overdrive makes a mirror more accurate and costs voltage, which is the same trade in yet another costume.",
            ],
            "read": [{
                "title": "The resistor that needed forty-five volts, and the transistor that needed one",
                "minutes": 14,
                "body": r'''
Module 3 left a promise unkept. It computed the gain of a common-source stage as
$-g_m(r_o\parallel R_D)$, observed that pushing $R_D$ up drives the answer towards the
intrinsic gain $g_mr_o = 90$, and moved on. So take the promise seriously and turn $R_D$
up, on a bench with a 12 V supply and the course's 1 mA operating point.

```python
GM, RO, V_DD, V_FLOOR, I_D = 2e-3, 45e3, 12.0, 3.0, 1e-3

for r_d in (5e3, 9e3, 20e3, 45e3):
    a0 = GM * RO * r_d / (RO + r_d)
    v_d = V_DD - I_D * r_d
    room = f"{v_d - V_FLOOR:.1f} V of swing left" if v_d >= V_FLOOR else "impossible"
    print(f"R_D = {r_d / 1e3:4.1f} k   gain {a0:5.2f}   drain at {v_d:+6.1f} V   {room}")
```

The 20 kΩ resistor would put the drain at $-8$ V and the 45 kΩ one at $-33$ V, on a supply
whose lowest rail is ground. Neither circuit exists. The largest resistor this stage can
actually take is 9 kΩ, which lands the drain exactly on the triode boundary at
$V_S + V_{ov} = 3$ V, gives a gain of 15, and leaves the amplifier with **no output swing
at all**. Ask for any usable swing and the gain comes back down towards 9.

That is the whole problem of this module, and it is worth stating as a property of the
component rather than as bad luck. A resistor's small-signal resistance and its DC voltage
drop are the same choice: $V = IR$ decides both, from the same $R$ and the same $I$. The
gain wants $R$ large. The headroom wants $IR$ small. There is no resistor that does both,
and the drain node is where a 10-credit subject's worth of compromise lives.

## What is actually wanted

Write down the component the drain would like, in terms of its $I$–$V$ curve rather than
its name. It has to carry 1 mA — the bias current has to get through it. It has to do that
with only a volt or so across it, because the volts are needed elsewhere. And it has to
have a very shallow slope, because the small-signal resistance at that node *is* the
reciprocal of that slope: $R = dV/dI$.

A component that passes a fixed current, almost regardless of the voltage across it, with a
small voltage across it. That is not an exotic request. It is a MOSFET in saturation, which
is the thing this whole course has been describing since module 1 — $I_D$ set by $V_{GS}$,
almost independent of $V_{DS}$, and needing only $V_{DS} \ge V_{ov}$ to stay there. The
drain resistor should be another transistor.

## Getting a transistor to carry the current you want

The load device needs a gate voltage that makes it carry exactly 1 mA. Solving the square
law backwards gives $V_{ov} = 1$ V and so $V_{GS} = 2$ V, but that number is a function of
$k$ and $V_{th}$, and module 2 spent a whole reading on how little those can be trusted.
Applying 2.000 V from a bench supply reproduces module 2's opening disaster exactly.

The way out is not to compute the voltage but to *measure* it, on a device that is
guaranteed to be identical. Force the reference current through one transistor and let it
find whatever $V_{GS}$ it needs — which is what tying its gate to its drain does, because
then the gate voltage is free to move until the current balances. Take that voltage to a
second, matched device, and the second device carries the same current, because two devices
with the same $V_{GS}$, the same $V_{th}$ and the same $k$ have the same $I_D$. That pair is
the **current mirror**.

Tying gate to drain has a second consequence, and it is the one that makes the arrangement
safe. It forces $V_{DS} = V_{GS}$, and saturation needs only $V_{DS} \ge V_{GS} - V_{th}$,
so a diode-connected device is in saturation whenever it is conducting at all. The
reference can never accidentally fall into triode.

The copy does not have to be one-to-one. Both devices sit at the same overdrive, and
$I_D = \tfrac{1}{2}k'(W/L)V_{ov}^2$, so

$$\frac{I_{out}}{I_{ref}} = \frac{(W/L)_2}{(W/L)_1}$$

Currents are multiplied and divided by drawing devices wider or narrower. That matters
because a ratio of drawn dimensions on one die tracks across temperature and process in a
way that a ratio of two resistor values never does — the same argument module 1 made about
$W/L$ being the one part of $k$ a designer chooses.

## One wire, and 45 kΩ becomes 500 Ω

Here is the part that catches people, and it is worth doing rather than asserting. Drive
the diode-connected reference device's terminals with a small signal $v$. Its gate moves
with its drain, so $v_{gs} = v$, and two currents flow: $g_mv$ from the controlled source
and $v/r_o$ through the output resistance. The conductance is $g_m + 1/r_o$, so

$$R = \frac{1}{g_m + 1/r_o} = \frac{1}{2\text{ mA/V} + 1/45\text{ k}\Omega} = 494\ \Omega$$

The best current source in the circuit and the worst load in the circuit are the same
silicon at the same current, and one wire is the entire difference. The *output* device,
whose gate is held still by the reference, keeps its $r_o = V_A/I_D = 45$ kΩ, and 45 kΩ is
what an honest current source is worth. Not infinity: channel-length modulation, introduced
in module 1 as a small correction, arrives here as the design limit.

## The stage, rebuilt

```python
import math

K, GM, RO, C_L = 2e-3, 2e-3, 45e3, 354e-12

for name, r_load, volts in (("5 k resistor", 5e3, 5.0),
                            ("9 k resistor", 9e3, 9.0),
                            ("mirror load ", RO, 1.0)):
    r_out = RO * r_load / (RO + r_load)
    a0 = GM * r_out
    f3 = 1.0 / (2 * math.pi * r_out * C_L)
    print(f"{name}   R_out {r_out / 1e3:5.2f} k   A_0 {a0:5.2f}   f_3dB {f3 / 1e3:6.2f} kHz"
          f"   product {a0 * f3 / 1e3:.1f} kHz   DC drop {volts:4.1f} V")
print()
for dv in (0.001, 0.005, 0.200):
    err = 100.0 * ((1.0 - dv) ** 2 - 1.0)
    print(f"threshold mismatch {dv * 1e3:5.1f} mV  ->  current error {err:+6.2f} %"
          f"   (the rule -2 dVth/V_ov gives {-200.0 * dv:+6.2f} %)")
```

A gain of **45** from a load that takes one volt, against 9 from a load that takes five and
15 from a load that takes nine and leaves nothing over. It is half the intrinsic gain of
90, and it is exactly half because two identical resistances now sit at that node — the
amplifier's own $r_o$ and the load's. No load can beat $g_mr_o$, because $r_o$ is in
parallel with every candidate. This is what the build **Swap the drain resistor for a
current source** asks for, and it changes one component value to get it.

The third and fourth columns are the price. The corner falls from 99.9 kHz to 20.0 kHz, and
the product sits at 899.2 kHz in every row — module 4's number, unmoved. An active load
converts *headroom* into gain. It does not convert bandwidth into gain, and nothing in this
module gets you a bigger $g_m/(2\pi C_L)$. The fill-the-holes exercise **The active-loaded
stage, in five numbers** is that arithmetic on one page, and the last two holes are the
prize and the price side by side.

The mismatch lines are the mirror's own accuracy. Both devices sit at the same $V_{GS}$, so
a threshold difference $\Delta V_{th}$ moves the output device's overdrive by that much, and
because the current goes as the square, a fractional change in overdrive arrives *doubled*
in the current: $\Delta I/I \approx -2\Delta V_{th}/V_{ov}$. The program's exact squares
agree with that rule to two decimal places at 1 mV and 5 mV, and diverge at 200 mV, which
is where a linearisation should diverge. Note the cure and its cost: a larger overdrive
shrinks the fraction, and overdrive is voltage you no longer have for swing.

## The mistake, and why it is tempting

Diode-connecting both devices. The mirror is sold on matching, "matched" is heard as
"wired the same", and the reference device is visibly working — it is in saturation, it is
carrying exactly the right current, and copying it feels like the conservative choice.

The result is a 494 Ω resistor at the drain instead of a 45 kΩ current source, so the stage
delivers $g_m(45\text{ k}\Omega \parallel 494\ \Omega) = 0.98$. An amplifier with a gain
below one, built from a device with an intrinsic gain of 90, and every component in it
correct.

What the error misses is that the two devices have different jobs. The reference device's
job is to *develop* a gate voltage, which is why its gate has to be free to move, which is
why it is diode-connected. The output device's job is to *use* that voltage, which requires
its gate to be held still — and a gate held still is what makes a drain look like $r_o$ at
all. The build's checks are written to catch a near neighbour of this: if the gain comes
back as 90 rather than 45, the wrong resistor was replaced and the drain is seeing $r_o$
alone.

## Where this stops holding

**The two devices only match if their drains do.** Equal $V_{GS}$ gives equal current only
in a model with no channel-length modulation — and this whole module exists because there is
some. The reference device sits at $V_{DS} = V_{GS} = 2$ V; the output device sits at
whatever the amplifier's drain happens to be, say 7 V. The ratio of the two
$(1+\lambda V_{DS})$ factors is $1.156/1.044 = 1.106$, so a mirror whose devices are
*perfectly* matched still copies 1 mA as 1.11 mA. That 11% is the largest error in the
whole arrangement, it is systematic rather than random, and removing it is what a cascode
mirror is for.

**The DC operating point is no longer defined.** With a 5 kΩ resistor, a 10% error in the
bias current moved the drain by $0.1\text{ mA} \times 5\text{ k}\Omega = 0.5$ V. With the
active load the same error moves it by $0.1\text{ mA} \times 22.5\text{ k}\Omega = 2.25$ V,
because gain and DC sensitivity are the same number: both are the resistance at that node.
Two current sources facing each other cannot agree on a voltage between them, and a real
actively loaded stage never sits open-loop — it lives inside a feedback loop, or beside a
common-mode feedback circuit, that tells its output where to be. Module 10's pair is the
usual host.

**Two transistors out of the same tube are not matched.** The 5 mV of threshold difference
that gives 1% is a figure for two devices drawn side by side on one die. Module 2 opened
with the real spread between two discrete parts from the same reel: 0.2 V, which this
module's arithmetic turns into a 36% current error. Mirrors are an integrated-circuit
technique. On a breadboard, use a resistor and accept the gain of 9, or buy a matched pair
in one package and inherit somebody else's die.

## What to carry forward

The drain resistor was doing two jobs with one number, and a transistor separates them: its
slope and its voltage drop are set by different things. That buys a factor of five in gain
here and hands back four volts while doing it. It buys nothing at all in bandwidth. And it
brings two new dependencies — on matching and on the two drains sitting at comparable
voltages — that a resistor never had.
''',
            }],
            "quiz": {
                "title": "Mirrors, and what a transistor load is worth",
                "minutes": 9,
                "questions": [
                    {
                        "q": "What does tying a MOSFET's gate to its drain do?",
                        "opts": [
                            "it turns the device off",
                            "it makes $V_{DS} = V_{GS}$, so the device is always in saturation, and it behaves as a two-terminal resistor of about $1/g_m$",
                            "it puts the device in triode, where it behaves as a resistor of $1/(kV_{ov})$",
                            "it has no small-signal effect; the device is still a current source of $r_o$",
                        ],
                        "a": 1,
                        "why": r'''
Two things at once. Because $V_{DS} = V_{GS}$ and saturation needs only
$V_{DS} \ge V_{GS} - V_{th}$, a diode-connected device is in saturation whenever it is
conducting at all — which is what makes it a reliable reference. And to a small signal
it is a resistor of $1/(g_m + 1/r_o) \approx 1/g_m$, because the gate now moves with the
drain: 500 Ω at 1 mA, not the 45 kΩ the same device offers with its gate held still.
''',
                    },
                    {
                        "q": "A mirror's reference device has $W/L = 10$ and carries 0.2 mA. The output device has $W/L = 40$. What does it carry?",
                        "opts": ["0.05 mA", "0.2 mA", "0.8 mA", "2.0 mA"],
                        "a": 2,
                        "why": r'''
0.8 mA. Both devices sit at the same $V_{GS}$, so both have the same overdrive, and
$I_D = \tfrac{1}{2}k'(W/L)V_{ov}^2$ scales straight with $W/L$: four times the width is
four times the current. This is why a bias distribution network on a chip is a row of
mirrors with different widths rather than a row of resistors — the ratio depends on
drawn dimensions, which track each other across temperature and process in a way that
absolute values never do.
''',
                    },
                    {
                        "q": "The output device of a mirror runs at 1 mA and has $V_A = 45$ V. What is the small-signal output resistance of that 'current source'?",
                        "opts": ["45 kΩ", "500 Ω", "infinite", "22.5 kΩ"],
                        "a": 0,
                        "why": r'''
$r_o = V_A/I_D = 45$ kΩ. The infinite answer is the ideal-current-source idealisation,
and the whole reason channel-length modulation was introduced in module 1 is that this
is where it shows up as a design limit. 500 Ω is what the *reference* device of the same
mirror looks like, because its gate is tied to its drain; the two devices are identical
silicon and differ by one wire.
''',
                    },
                    {
                        "q": "A common-source stage at 1 mA ($g_m = 2$ mA/V, $r_o = 45$ kΩ) is given an active load whose own $r_o$ is also 45 kΩ. What is the gain?",
                        "opts": ["−90", "−9", "−180", "−45"],
                        "a": 3,
                        "why": r'''
The drain sees $45\text{k} \parallel 45\text{k} = 22.5$ kΩ, so $A_v = -2\text{ mA/V}
\times 22.5\text{ k}\Omega = -45$: half the intrinsic gain of 90, because there are now
two identical resistances at that node instead of one. Answering −90 forgets that the
load device has an output resistance too; −9 is the 5 kΩ resistor from module 3, which
is exactly what has just been replaced.
''',
                    },
                    {
                        "q": "That change took the gain from 9 to 45 with the same device, the same current and the same 354 pF of load capacitance. What happened to the bandwidth?",
                        "opts": [
                            "it fell from 100 kHz to 20 kHz, leaving the gain-bandwidth product at 900 kHz",
                            "it stayed at 100 kHz",
                            "it rose to 500 kHz",
                            "it fell to 2 kHz",
                        ],
                        "a": 0,
                        "why": r'''
The corner is $1/(2\pi R_{out}C_L)$ and $R_{out}$ went from 4.5 kΩ to 22.5 kΩ, a factor
of five — so 100 kHz becomes 20 kHz and $45 \times 20\text{ kHz}$ is the same 900 kHz
module 4 measured. The active load did not cheat the product; it bought gain with
headroom, which is a resource module 4's resistor could not spend. Getting more product
still needs a bigger $g_m$ or a smaller $C_L$.
''',
                    },
                    {
                        "q": "The two devices of a mirror differ by 5 mV in threshold voltage, at an overdrive of 1 V. What current error does that give?",
                        "opts": ["0.5%", "1%", "5 mV", "0.25%"],
                        "a": 1,
                        "why": r'''
The current goes as the square of the overdrive, so a fractional change in overdrive
appears doubled in the current: $\Delta I/I = 2\Delta V_{th}/V_{ov} = 2 \times
0.005/1 = 1\%$. Answering 0.5% is the un-doubled version, and forgetting the factor of
two is exactly the sort of error that makes a mirror look twice as good on paper as it
is on silicon. Note the cure: a larger overdrive shrinks the fraction, at the price of
the voltage it takes to sustain it.
''',
                    },
                ],
            },
            "build": {
                "title": "Swap the drain resistor for a current source",
                "minutes": 24,
                "brief": r'''
The canvas opens with the finished circuit from module 4: the transistor's
$g_mv_{gs} = 20$ µA generator for a 10 mV input, its own $r_o$ of 45 kΩ, the 5 kΩ drain
resistor, and the 354 pF of load capacitance. It measures a gain of 9 and a corner at
100 kHz, as it should.

Your job is one component. Replace the 5 kΩ drain resistor with the small-signal
equivalent of a **current-source load** — which is the output device of a mirror, and
therefore its own $r_o$, 45 kΩ, from the drain node to ground.

## What the finished circuit must do

- $r_o$ of the amplifying device, 45 kΩ, still there from the probed drain node to
  ground,
- nothing small left at that node: no resistance below 20 kΩ anywhere on the drain,
- a low-frequency gain of **45**, so the probed node reads 450 mV for the 10 mV the
  current source stands for,
- a corner at **20 kHz**,
- and therefore a gain-bandwidth product still equal to **900 kHz**, which the checks
  measure rather than assume.

## Why it works

Nothing in the drawing changed except one value, and the gain went up fivefold. The
resistor was giving 5 kΩ and taking 5 V of headroom to do it; the transistor gives 45 kΩ
and takes about one overdrive. That is the entire argument, and it is worth watching the
corner move at the same time so that the price is visible next to the prize.
''',
                "start": {
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
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "I", "x": 3, "y": 3, "rot": 1, "value": 2e-05},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "OUT", "x": 5, "y": 2},
                        {"id": "p3", "kind": "R", "x": 7, "y": 3, "rot": 1, "value": 45000},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 6},
                        {"id": "p5", "kind": "R", "x": 11, "y": 3, "rot": 1, "value": 45000},
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
                    {"name": "the amplifying device still has its own output resistance", "code": r'''
c.assert(c.count('I') === 1,
  'One current source: the g_m v_gs generator. Found ' + c.count('I') + '.');
c.close(c.values('I')[0], 20e-6, 0.01,
  'the small-signal drain current, g_m times the 10 mV test input');
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 45000) <= 900 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'r_o = 45 kΩ belongs to the amplifying device and stays where it was, from the ' +
   'probed drain node to ground. Replacing it rather than the 5 kΩ is the one wrong ' +
   'component to change.');
'''},
                    {"name": "nothing small is left hanging on the drain", "code": r'''
const out = c.outNode();
const legs = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(legs.length >= 2,
  'Two resistances belong at the drain now: r_o of the amplifier and r_o of the load ' +
  'device. Found ' + legs.length + '.');
const smallest = Math.min.apply(null, legs.map(function (p) { return p.value; }));
c.assert(smallest >= 20000,
  'Something on the drain is only ' + c.fmt(smallest, 'Ω') + '. A current-source load ' +
  'is a transistor r_o, tens of kilohms; a resistor of a few kilohms is the thing being ' +
  'replaced, and while it is there it sets the node resistance on its own.');
'''},
                    {"name": "the low-frequency gain is 45, and still inverting", "code": r'''
c.close(c.gain(100), 0.45, 0.02,
  'the output amplitude well below the corner — 10 mV in at a gain of 45 is 450 mV out');
c.assert(Math.abs(c.phase(100)) > 170,
  'A common-source stage inverts whatever is used as its load. Measured ' +
  c.phase(100).toFixed(1) + '°.');
'''},
                    {"name": "the corner has moved to 20 kHz", "code": r'''
const f = c.corner(10, 1e9);
c.close(f, 2e4, 0.05,
  'the -3 dB corner — five times the drain resistance is a fifth of the bandwidth');
'''},
                    {"name": "the gain-bandwidth product has not moved at all", "code": r'''
const a = c.gain(10) / 0.01;
const f = c.corner(10, 1e9);
c.close(a * f, 9e5, 0.03,
  'the gain-bandwidth product, which module 4 measured as 900 kHz on the same device ' +
  'with the same load capacitance');
'''},
                ],
                "hints": [
                    "Only one number changes. The 5 kΩ resistor becomes 45 kΩ — the output resistance of the load device, which runs at the same 1 mA and has the same 45 V of Early voltage.",
                    "A gain of 45 from $g_m = 2$ mA/V needs 22.5 kΩ at the drain, and $45\\,\\text{k} \\parallel 45\\,\\text{k}$ is exactly that.",
                    "The capacitor does not change: $C_L$ is what the next stage and the wiring present, and it has no idea what kind of load is hanging beside it. Only the resistance it works against changed.",
                    "If the gain comes out at 90 rather than 45, the 5 kΩ has been deleted instead of replaced and the drain is seeing $r_o$ alone.",
                ],
            },
            "blanks": {
                "title": "The active-loaded stage, in five numbers",
                "minutes": 9,
                "caption": "the same stage as module 3, with a transistor where the resistor was",
                "lang": "text",
                "brief": r'''
Everything about the active load is in the arithmetic of the change: what happens at
the drain node, what the gain becomes, what the bandwidth becomes, what their product
does, and what the load costs in volts.

Fill the five holes and read the last two back together. One of them is the reason the
technique is used at all, and the other is the reason it is not magic.
''',
                "listing": """# Module 3's stage, with the 5 kΩ drain resistor replaced by a current-source load.
#   amplifier:  g_m = 2 mA/V   r_o = 45 kΩ   I_D = 1 mA   C_L = 354 pF
#   load:       a mirror output device, also at 1 mA, so also r_o = 45 kΩ

R_drain    =  45 kΩ ___ 45 kΩ                =  22.5 kΩ
A_v        =  -g_m * R_drain                 =  ___
f_3dB      =  1 / (2 * pi * R_drain * C_L)   =  ___
|A_v| * f_3dB                                =  ___
DC volts the load takes to do its job        =  ___
""",
                "blanks": [
                    {
                        "prompt": "The amplifier's own output resistance and the load's, both at the same node.",
                        "hole": "?",
                        "opts": ["in series with", "in parallel with", "minus", "plus"],
                        "a": 1,
                        "why": "Both run from the drain node to signal ground — $r_o$ of the amplifier from drain to source, and $r_o$ of the load device from drain to the supply, which is signal ground. Two resistances between the same pair of nodes are in parallel, and $45\\,\\text{k} \\parallel 45\\,\\text{k} = 22.5$ kΩ.",
                        "whys": [
                            "Series would need the signal current to flow through one and then the other, which would mean the drain node sitting between them. It does not: both have one end on the drain.",
                            "Both run from the drain node to signal ground — $r_o$ of the amplifier from drain to source, and $r_o$ of the load device from drain to the supply, which is signal ground. Two resistances between the same pair of nodes are in parallel, and $45\\,\\text{k} \\parallel 45\\,\\text{k} = 22.5$ kΩ.",
                            "Subtracting resistances has no physical meaning here, and it would give zero for two equal ones — a short circuit at the drain, which would leave no gain at all.",
                            "Adding would give 90 kΩ and a gain of 180, which is twice the intrinsic gain of the device. Nothing you hang on the drain can beat $g_mr_o$; a result above it is a sign the parallel rule went in upside down.",
                        ],
                    },
                    {
                        "prompt": "Transconductance times the resistance at the drain, with the sign the stage actually has.",
                        "hole": "?",
                        "opts": ["-9", "-45", "-90", "-4.5"],
                        "a": 1,
                        "why": "$-2\\,\\text{mA/V} \\times 22.5\\,\\text{k}\\Omega = -45$. Five times module 3's −9, and exactly half the intrinsic gain of 90 — which is what two equal resistances at one node always give.",
                        "whys": [
                            "That is module 3's answer, from the 5 kΩ resistor that has just been removed. If the gain has not moved, the new load is not in the circuit yet.",
                            "$-2\\,\\text{mA/V} \\times 22.5\\,\\text{k}\\Omega = -45$. Five times module 3's −9, and exactly half the intrinsic gain of 90 — which is what two equal resistances at one node always give.",
                            "−90 is $g_mr_o$, the intrinsic gain, and it needs a load with *infinite* output resistance. A real mirror output device brings its own 45 kΩ, and that halves the answer.",
                            "−4.5 would need 2.25 kΩ at the drain, which is less than the resistor that was there before. The change made the node resistance larger, not smaller.",
                        ],
                    },
                    {
                        "prompt": "The corner, from the same drain resistance and the unchanged 354 pF.",
                        "hole": "?",
                        "opts": ["100 kHz", "4.5 kHz", "20 kHz", "900 kHz"],
                        "a": 2,
                        "why": "$1/(2\\pi \\times 22.5\\,\\text{k}\\Omega \\times 354\\,\\text{pF}) = 20$ kHz. The resistance went up by five, so the corner came down by five, from module 4's 100 kHz.",
                    },
                    {
                        "prompt": "Multiply the last two together.",
                        "hole": "?",
                        "opts": ["180 kHz", "20 kHz", "4.5 MHz", "900 kHz"],
                        "a": 3,
                        "why": "$45 \\times 20\\,\\text{kHz} = 900$ kHz — the same product module 4 measured with a resistor load, because the product is $g_m/(2\\pi C_L)$ and neither of those changed. The drain resistance cancels out of it, whatever is providing that resistance.",
                    },
                    {
                        "prompt": "The DC price of the load: how much of the supply does a current-source load take across itself, compared with the 5 V the resistor took?",
                        "hole": "?",
                        "opts": ["5 V, as the resistor did", "one overdrive, about 1 V", "nothing at all", "the whole 12 V supply"],
                        "a": 1,
                        "why": "A transistor stays in saturation as long as it has about $V_{ov}$ across it — roughly a volt here. The resistor needed 5 V to deliver 5 kΩ at 1 mA, and would have needed 45 V to deliver 45 kΩ. That is the whole trade: four volts of headroom handed back and five times the gain, from the same current.",
                        "whys": [
                            "That is what the resistor cost, and it is the number being escaped. A resistor's drop and its resistance are the same choice; a transistor's are not.",
                            "A transistor stays in saturation as long as it has about $V_{ov}$ across it — roughly a volt here. The resistor needed 5 V to deliver 5 kΩ at 1 mA, and would have needed 45 V to deliver 45 kΩ. That is the whole trade: four volts of headroom handed back and five times the gain, from the same current.",
                            "Nothing at all would mean the load device sitting with zero volts across it, which puts it in triode, where it is a small resistor rather than a current source and the gain collapses.",
                            "The whole supply would leave zero for the amplifying device, which then has no headroom of its own. The two devices share the rail, and the point of an active load is that it asks for a very small share.",
                        ],
                    },
                ],
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "The bipolar transistor as an amplifier",
            "summary": "The same job done by an exponential instead of a square law, and a base terminal that will not stop drawing current.",
            "concepts": [
                "Two junctions, three terminals: emitter, base, collector. In the **forward-active** region the base-emitter junction is forward biased and the base-collector junction reverse biased, and the collector current is $I_C = I_Se^{V_{BE}/V_T}$ — the diode equation of EE201, now controlling a current that leaves by a third terminal.",
                "$V_T = kT/q$, the thermal voltage: 25.9 mV at 300 K, and 25 mV in every hand calculation including this course's. A decade of collector current costs $V_T\\ln 10$ of $V_{BE}$ — 58 mV at 25 mV, which is where the familiar '60 mV per decade' comes from. $V_{BE}$ is around 0.7 V and is never the number to design against.",
                "The base takes current: $I_B = I_C/\\beta$, with $\\beta$ around 100 and specified as a range rather than a value. This is the single largest practical difference from the MOSFET, whose gate takes none, and it is why a bipolar bias divider has to be much stiffer than module 2's. The build exercise in this module measures that: module 2's 500 kΩ over 250 kΩ, perfectly good with a gate on the end of it, loses **1.51 V** at its midpoint the moment a base is connected instead, and the collector current lands at 0.91 mA instead of 1.02.",
                "$g_m = I_C/V_T$. Notice what is missing: no $k$, no $W/L$, no geometry at all. At 1 mA a bipolar device gives 40 mA/V against this course's MOSFET at 2 mA/V — twenty times, from the same current, because an exponential is a much steeper function than a parabola.",
                "The input is no longer infinite. $r_\\pi = \\beta/g_m = \\beta V_T/I_C$, which at 1 mA and $\\beta = 100$ is 2.5 kΩ. Put that in parallel with module 2's 167 kΩ divider and the stage's input resistance is 2.46 kΩ: the divider has become irrelevant and the device decides.",
                "$r_o = V_A/I_C$, exactly as before — 45 kΩ at 1 mA. The Early effect is the bipolar original; channel-length modulation was named after it.",
                "The intrinsic gain is therefore $g_mr_o = V_A/V_T$ — 1800 here, and **independent of the bias current**, because $g_m$ rises and $r_o$ falls in exact proportion. A MOSFET's intrinsic gain moves with current and is 90 at 1 mA. Twenty times more gain per device is why bipolar transistors are still chosen for the front end of a precision amplifier.",
                "The common-emitter stage is the common-source stage with the names changed: $A_v = -g_m(r_o\\parallel R_C)$, which with $R_C = 5$ kΩ is $-40\\text{ mA/V}\\times 4.5\\text{ k}\\Omega = -180$. Everything module 3 established about small-signal analysis transfers unaltered; only the two parameter formulas are different.",
                "$V_{BE}$ falls by about 2 mV for every kelvin of temperature rise, which at first sight wrecks any bias. It does not, for the same reason module 2's emitter resistor existed: the emitter current is set by $(V_B - V_{BE})/R_E$, and with 2 V across $R_E$ a 2 mV drift is one part in a thousand per kelvin. Bias a bipolar stage against $V_{BE}$ and it is hopeless; bias it against a voltage large compared with $V_{BE}$'s drift and it is fine.",
            ],
            "read": [{
                "title": "The divider that was fine until a base was wired to it",
                "minutes": 15,
                "body": r'''
Take module 2's board exactly as it stands — 12 V rail, 500 kΩ over 250 kΩ to the gate,
2 kΩ at the source, 5 kΩ at the drain — and unsolder the MOSFET. Put an NPN bipolar
transistor in its place: collector where the drain was, emitter where the source was, base
where the gate was. Nothing else changes.

The divider's midpoint, which read 4.000 V with the MOSFET in and reads 4.000 V with the
socket empty, now reads **2.487 V**. The current that was 1.02 mA is 0.91 mA. And the
voltage gain, which was 9, is **160**.

Both halves of that are worth having. The device is nearly twenty times better at the job
this course exists to do, and the bias network that took module 2 a whole reading to design
has been knocked a volt and a half off its design point by the mere act of connecting the
device to it. This module is about both, and they have the same cause.

## The base is not a gate

A MOSFET's gate sits on an insulator, so at DC it takes nothing, and a whole class of
loading calculations disappeared from module 2 as a result. A bipolar transistor has no
insulator anywhere in it. It is two pn junctions sharing a middle layer, and in the
**forward-active** region — base-emitter forward biased, base-collector reverse biased —
the emitter injects carriers into the thin base and almost all of them are swept onward
into the collector. Almost all. A small fraction recombines on the way across, and the
base terminal has to supply the current that does:

$$I_B = \frac{I_C}{\beta}$$

with $\beta$ around 100. That is the entire practical difference between the two devices,
and it is enough to invalidate a bias network. Module 2's divider is a 4.00 V source behind
a Thévenin resistance of $500\text{k}\parallel 250\text{k} = 167$ kΩ. Draw 10 µA out of
that and it sags by 1.7 V; the loop settles at a slightly smaller current, so the sag lands
at 1.51 V. The megohm resistors that were free with a gate on the end of them are a
catastrophe with a base.

What the base *does* give back is in the other junction. Instead of the square law, the
collector current obeys the diode equation of EE201:

$$I_C = I_S e^{V_{BE}/V_T}, \qquad V_T = \frac{kT}{q}$$

$V_T$ is 25.9 mV at 300 K and 25 mV in every hand calculation, this course's included.
Differentiate — which is what module 1 did to get $g_m$ from the square law, and what the
derivation **Three bipolar parameters from one exponential** does step by step here — and
because the derivative of an exponential is itself,

$$g_m = \frac{\partial I_C}{\partial V_{BE}} = \frac{I_S e^{V_{BE}/V_T}}{V_T}
      = \frac{I_C}{V_T}$$

Look at what is missing. No $k$, no $W/L$, no geometry: two bipolar transistors of wildly
different die area at the same collector current have the same transconductance. At 1 mA
that is 40 mA/V against this course's MOSFET at 2 mA/V, and the factor of twenty is the
factor of twenty in the opening measurement. An exponential is a much steeper function than
a parabola.

Two more parameters come off the same relation. The input is no longer infinite:
$r_\pi = \beta/g_m = \beta V_T/I_C$, which at 1 mA and $\beta = 100$ is 2.5 kΩ. And
$r_o = V_A/I_C$ exactly as before — the Early effect is the bipolar original, and
channel-length modulation was named after it. Multiply the first and the last and the
current cancels:

$$g_mr_o = \frac{I_C}{V_T}\cdot\frac{V_A}{I_C} = \frac{V_A}{V_T} = \frac{45}{0.025} = 1800$$

The intrinsic gain of a bipolar transistor does not depend on how hard it is biased. The
MOSFET's does — module 1 worked out that halving $I_D$ takes $g_mr_o$ from 90 to 127 — and
that structural difference is why a precision amplifier's front end is still often bipolar.

## Fixing the divider

The rule that falls out of $I_B = I_C/\beta$ is that the divider has to carry a current
large compared with the base current, so that the base is a small load on it. Ten times is
the working number.

```python
import math

V_T = 1.380649e-23 * 300.0 / 1.602176634e-19        # kT/q at 300 K, 25.85 mV
I_S, V_A = 1e-14, 45.0
V_CC, R_E, R_C = 12.0, 2000.0, 5000.0

def collector_current(r1, r2, beta):
    """Solve the base loop of a four-resistor bipolar bias for I_C, by bisection."""
    v_th, r_th = V_CC * r2 / (r1 + r2), r1 * r2 / (r1 + r2)
    lo, hi = 1e-12, 1e-1
    for _ in range(200):
        i_c = math.sqrt(lo * hi)
        loop = (v_th - (i_c / beta) * r_th - V_T * math.log(i_c / I_S)
                - i_c * (beta + 1.0) / beta * R_E)
        if loop > 0.0:
            lo = i_c
        else:
            hi = i_c
    i_c = math.sqrt(lo * hi)
    return i_c, v_th, v_th - (i_c / beta) * r_th

for name, r1, r2 in (("500k/250k, module 2's", 500e3, 250e3),
                     ("75k/24k              ", 75e3, 24e3)):
    i_c, v_open, v_loaded = collector_current(r1, r2, 100.0)
    lo = collector_current(r1, r2, 50.0)[0]
    hi = collector_current(r1, r2, 300.0)[0]
    gm, r_o = i_c / V_T, V_A / i_c
    print(f"{name}  V_B {v_open:.3f} V open -> {v_loaded:.3f} V loaded   I_C {i_c * 1e3:.4f} mA"
          f"   gain {-gm * r_o * R_C / (r_o + R_C):.0f}"
          f"   beta 50..300: {100 * (lo / i_c - 1):+.1f}% to {100 * (hi / i_c - 1):+.1f}%")
```

The 75 kΩ / 24 kΩ divider carries about 124 µA against a base current of 10 µA, and it sags
by 186 mV rather than 1513. The collector current lands at 1.0236 mA against a design
target of 1.000, and the gain at 178.

The last column is why any of this matters, and it is not the sag. $\beta$ is not 100. The
data sheet says "50 to 300", it moves with current and with temperature, and no two parts
from the same reel agree. On the stiff divider, taking $\beta$ from 50 to 300 moves the
collector current by $-8.3\%$ to $+6.4\%$ — because the divider holds $V_B$ nearly fixed
whatever the base takes, and the emitter resistor then does the work, exactly as it did for
the MOSFET in module 2 and for exactly the same reason. On module 2's divider the same
spread gives $-31\%$ to $+44\%$: there, $\beta$ is setting the bias, and $\beta$ is the one
parameter on the data sheet you are least entitled to rely on. That comparison is what the
build **Biasing a bipolar stage, with the base drawing what it draws** puts on the canvas
with a real Ebers-Moll device, and its final check measures the ratio of divider current to
base current rather than trusting the drawing.

## The mistake, and why it is tempting

Setting the bias by applying a voltage to the base. Everybody knows $V_{BE}$ is 0.7 V, so
put 0.7 V on the base, ground the emitter, and the transistor is biased.

```python
import math

V_T = 1.380649e-23 * 300.0 / 1.602176634e-19        # kT/q at 300 K
I_S = 1e-14

print(f"V_T = {V_T * 1e3:.2f} mV, so a decade of current costs {V_T * math.log(10) * 1e3:.1f} mV")
print(f"1.000 mA needs V_BE = {V_T * math.log(1e-3 / I_S) * 1e3:.1f} mV")
for v_be in (0.600, 0.650, 0.700):
    print(f"  a base held at {v_be:.3f} V draws {I_S * math.exp(v_be / V_T) * 1e3:8.3f} mA")
```

The device wanted 654.8 mV for a milliamp. The famous 0.7 V gives **5.75 mA**, and 0.6 V
gives 0.12 mA. Fifty millivolts either side of the right answer is a factor of about seven
in the collector current, because a decade costs only 59.5 mV — the 58 mV that
$V_T\ln 10$ gives at the hand-calculation value of 25 mV, and about 60 mV at the
temperature the bench is actually at.

It is tempting because 0.7 V is quoted as though it were a property of silicon, like the
1.12 eV band gap, rather than the value one particular junction happens to sit at when one
particular current is passing. It is not a constant, it is a readout. And it is the
readout of an exponential, so the number you want it to be and the number it is are never
more than a hundred millivolts apart no matter how badly wrong the current is — which is
exactly why the error survives inspection.

The cure is module 2's, unchanged: never let a device parameter set the operating point.
Put a resistor in the emitter, hold the base with a divider stiff enough not to care about
$\beta$, and the current becomes $(V_B - V_{BE})/R_E$ — a subtraction in which $V_{BE}$ is
a small, roughly known correction rather than the whole answer.

## Where this stops holding

**"Saturation" means the opposite thing here.** A MOSFET in saturation is the device doing
its job. A *bipolar* transistor in saturation has both junctions forward biased, $V_{CE}$
collapsed to about 0.2 V, and $\beta$ gone — it is the region a switch wants and an
amplifier must avoid. Forward-active is the amplifying region, and it needs a volt or so of
$V_{CE}$ to stay in. The build's checks refuse a design with $V_{CE}$ under 1 V for this
reason, and the word is a genuine trap: the same syllable names the good region for one
device and the useless one for the other.

**The exponential runs out at both ends.** $I_C = I_Se^{V_{BE}/V_T}$ is excellent over
perhaps six decades in the middle of a small-signal device's range. Above a few
milliamps, high-level injection and the ohmic resistance of the base and emitter start
absorbing part of the applied voltage, so the slope flattens and $g_m = I_C/V_T$ becomes an
overestimate. Below a microamp, recombination in the base-emitter depletion region adds a
current with a different exponent. Neither matters at this course's 1 mA, and both matter
to anyone designing at the ends of the range.

**Temperature moves all three parameters at once.** $V_{BE}$ falls by about 2 mV per
kelvin, $\beta$ rises, and $I_S$ climbs steeply. The emitter resistor absorbs all of it for
the same reason it absorbed $\beta$: with 2 V across $R_E$, a 2 mV drift is one part in a
thousand per kelvin, or 3% over a thirty-degree rise. Shrink $V_E$ to 200 mV to recover some
output swing — a perfectly reasonable-looking trade — and the same drift becomes 1% per
kelvin, and the design that passed on a cold bench fails in a warm rack.

## What to carry forward

Everything module 3 established about small-signal analysis transfers without a word
changed; only two parameter formulas are different, and both come out of one exponential.
$g_m = I_C/V_T$ has no device in it, so bipolar transconductance is bought with current
alone at a fixed rate rather than with a square root. $r_\pi = \beta V_T/I_C$ is the bill
for that, and it is what turns a bias divider that was free into one that has to be
designed. And $g_mr_o = V_A/V_T$ is fixed by the process and the temperature and by nothing
a designer does — the cleanest single figure of merit a transistor technology has, 1800
here against the MOSFET's 90.
''',
            }],
            "quiz": {
                "title": "An exponential instead of a parabola",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A bipolar transistor runs at $I_C = 1$ mA. Taking $V_T = 25$ mV, what is $g_m$?",
                        "opts": ["25 mA/V", "40 mA/V", "2 mA/V", "1 mA/V"],
                        "a": 1,
                        "why": r'''
$g_m = I_C/V_T = 1\text{ mA}/25\text{ mV} = 40$ mA/V. There is no device parameter in
that expression at all — two bipolar transistors of wildly different sizes at the same
collector current have the same transconductance, which is not remotely true of
MOSFETs. 2 mA/V is what this course's MOSFET gives at the same 1 mA, and the factor of
twenty between them is the reason to reach for a bipolar front end.
''',
                    },
                    {
                        "q": "That device has $V_A = 45$ V. What is its intrinsic gain $g_mr_o$, and how does it change if the bias current is halved?",
                        "opts": [
                            "1800, and it is unchanged",
                            "1800, and it rises to 2545",
                            "90, and it is unchanged",
                            "180, and it halves",
                        ],
                        "a": 0,
                        "why": r'''
$g_mr_o = (I_C/V_T)(V_A/I_C) = V_A/V_T = 45/0.025 = 1800$, and the current cancels
completely — halving it doubles $r_o$ and halves $g_m$. That is a real structural
difference from the MOSFET, where $g_m$ falls only as $\sqrt{I_D}$ so the intrinsic
gain *rises* at low current, as module 1 worked out. 90 is that MOSFET's figure at
1 mA.
''',
                    },
                    {
                        "q": "With $\\beta = 100$ at 1 mA, what is $r_\\pi$?",
                        "opts": ["100 Ω", "2.5 kΩ", "45 kΩ", "25 Ω"],
                        "a": 1,
                        "why": r'''
$r_\pi = \beta/g_m = 100/0.04 = 2.5$ kΩ. This is the price of the base current: a
bipolar common-emitter stage has an input resistance of a few kilohms, so hanging it on
module 2's 167 kΩ divider gives $167\text{k}\parallel 2.5\text{k} = 2.46$ kΩ and the
divider might as well not be there. A MOSFET stage's input resistance is whatever the
divider is; a bipolar stage's is whatever the device is.
''',
                    },
                    {
                        "q": "Module 2's divider is 500 kΩ / 250 kΩ and draws 16 µA. A bipolar device at 1 mA with $\\beta = 100$ is hung on it. What happens?",
                        "opts": [
                            "nothing; 10 µA is small compared with the 16 µA the divider carries",
                            "the base current pulls the gate voltage up",
                            "the divider is far too soft: 10 µA of base current across its 167 kΩ Thévenin resistance costs about 1.7 V, and the bias is destroyed",
                            "the divider draws more current from the supply, but its output voltage is unchanged",
                        ],
                        "a": 2,
                        "why": r'''
$I_B = I_C/\beta = 10$ µA, and the divider looks like a 4 V source behind
$500\text{k}\parallel 250\text{k} = 167$ kΩ. Ten microamps out of that is 1.7 V of sag —
most of the 2 V that was meant to sit across the emitter resistor. The working rule is
that the divider current should be at least ten times the base current, which here means
100 µA or more and resistors ten times smaller. The MOSFET's megohm divider was a
luxury paid for by the gate oxide.
''',
                    },
                    {
                        "q": "A bipolar common-emitter stage runs at 1 mA with $R_C = 5$ kΩ and $V_A = 45$ V. What is its voltage gain?",
                        "opts": ["−9", "−200", "−180", "−1800"],
                        "a": 2,
                        "why": r'''
$A_v = -g_m(r_o\parallel R_C) = -40\text{ mA/V}\times(45\text{k}\parallel 5\text{k}) =
-40\text{ mA/V}\times 4.5\text{ k}\Omega = -180$. Answering −200 leaves $r_o$ out, which
costs 10% here just as it did in module 3; −1800 is the intrinsic gain, which needs an
ideal current source at the collector rather than a 5 kΩ resistor. Exactly twenty times
module 3's −9, on the same resistor at the same current, which is the $g_m$ ratio and
nothing else.
''',
                    },
                    {
                        "q": "How much does $V_{BE}$ have to change to move the collector current by a factor of ten?",
                        "opts": ["about 58 mV", "about 0.7 V", "about 700 mV per decade", "about 2 mV"],
                        "a": 0,
                        "why": r'''
$\Delta V_{BE} = V_T\ln 10 = 25\text{ mV}\times 2.303 = 58$ mV — and about 60 mV at the
25.9 mV that room temperature really gives. That steepness is both the attraction and
the danger: it is where the large $g_m$ comes from, and it is why nothing may be biased
by applying a fixed voltage to the base and hoping. 0.7 V is roughly the whole $V_{BE}$,
not the change in it; 2 mV is the per-kelvin temperature drift.
''',
                    },
                    {
                        "q": "Why does a 2 mV/K drift in $V_{BE}$ not ruin a well-designed bipolar bias?",
                        "opts": [
                            "because the emitter current is set by $(V_B - V_{BE})/R_E$, and with 2 V across $R_E$ a 2 mV shift is a tenth of a per cent",
                            "because $\\beta$ rises with temperature and cancels it",
                            "because the drift is too slow to matter",
                            "because $V_{BE}$ does not appear anywhere in the bias equations",
                        ],
                        "a": 0,
                        "why": r'''
The emitter resistor turns the bias into a subtraction between a large number and
$V_{BE}$, so a drift in $V_{BE}$ appears in the answer divided by how large that
subtraction is. Two volts across $R_E$ against 2 mV/K is 0.1% per kelvin, or 3% over a
thirty-degree rise, which most designs will accept. Shrink $V_E$ to 200 mV to gain some
swing and the same drift becomes 1% per kelvin. The argument is exactly module 2's, with
$V_{BE}$ in the role $V_{th}$ played.
''',
                    },
                ],
            },
            "match": {
                "title": "The four symbols this module needs",
                "minutes": 6,
                "brief": r'''
The MOSFET was introduced as three terminals and an equation, and its symbol never had
to be read carefully. Bipolar circuits are different: the entire distinction between an
NPN and a PNP — which way the supply goes, which way the signal swings, which one goes
at the top of an output stage — is one arrow, and getting it backwards produces a
circuit that cannot possibly work and often looks fine on the page.

Two of these four are not transistors at all, and both are here because they turn up
inside every bipolar amplifier: the base-emitter junction that behaves exactly like one
of them, and the idealisation the collector behaves exactly like.
''',
                "prompt": "Pick a label, then tap the symbol it belongs to.",
                "labels": ["NPN transistor", "PNP transistor", "Diode", "Ideal current source", "Battery"],
                "items": [
                    {"sym": "NPN", "a": 0, "why": "An NPN. The arrow is always on the emitter, and here it points *outward* — read it as the direction conventional current leaves the device. Collector current flows in at the top, base current in at the side, and the sum comes out of the emitter."},
                    {"sym": "PNP", "a": 1, "why": "A PNP: the same drawing with the emitter arrow pointing *inward*. Current now flows into the emitter and out of the collector and base, so it works with its emitter at the more positive end — which is why PNP devices sit at the top of a supply rail and NPN devices at the bottom."},
                    {"sym": "D", "a": 2, "why": "A diode — triangle into a bar, current one way only. It is here because the base-emitter junction *is* one: $I_C = I_Se^{V_{BE}/V_T}$ is the diode equation, and the 0.7 V and the 60 mV per decade are the diode's numbers, met in EE201."},
                    {"sym": "I", "a": 3, "why": "An ideal current source: a fixed current whatever the voltage across it. It is the idealisation of a transistor collector in the forward-active region — the thing $r_o = V_A/I_C$ measures the failure of, and the thing an active load is trying to be."},
                ],
            },
            "derive": {
                "title": "Three bipolar parameters from one exponential",
                "minutes": 12,
                "vars": ["I_C", "I_S", "V_BE", "V_T", "g_m", "beta", "r_o", "V_A", "I_B"],
                "brief": r'''
Module 1 got $g_m$ by differentiating a square law. Here the same operation is applied
to an exponential, and because the derivative of an exponential is itself, the answer
comes out startlingly simple — and free of every device parameter.

Start from the forward-active relation

$$I_C = I_S e^{V_{BE}/V_T}$$

with $I_S$ a device constant and $V_T = kT/q$ the thermal voltage.
''',
                "steps": [
                    {
                        "prompt": "Differentiate with respect to $V_{BE}$. Write $g_m$ in terms of $I_S$, $V_{BE}$ and $V_T$.",
                        "answer": "\\frac{I_S}{V_T} e^{V_{BE}/V_T}",
                        "hint": "The chain rule on $e^{u}$ with $u = V_{BE}/V_T$ brings down $1/V_T$ and leaves the exponential alone.",
                        "deconstruct": [
                            "$\\frac{d}{dx}e^{ax} = a e^{ax}$, and here $a = 1/V_T$.",
                            "$I_S$ is a constant and comes along for the ride.",
                        ],
                    },
                    {
                        "prompt": "The exponential together with $I_S$ is the collector current itself. Write $g_m$ in terms of $I_C$ and $V_T$.",
                        "answer": "\\frac{I_C}{V_T}",
                        "hint": "Substitute $I_S e^{V_{BE}/V_T} = I_C$ into what you just wrote.",
                        "deconstruct": [
                            "The derivative of an exponential is proportional to the exponential, which is proportional to $I_C$.",
                            "Every device constant has vanished; only the current and the temperature are left.",
                        ],
                    },
                    {
                        "prompt": "The base current is $I_B = I_C/\\beta$, and the input resistance is $r_\\pi = \\partial V_{BE}/\\partial I_B$. Write it in terms of $\\beta$ and $g_m$.",
                        "answer": "\\frac{\\beta}{g_m}",
                        "hint": "Differentiate $I_B = I_C/\\beta$ with respect to $V_{BE}$ to get $g_m/\\beta$, then take the reciprocal.",
                        "deconstruct": [
                            "$\\partial I_B/\\partial V_{BE} = (1/\\beta)\\,\\partial I_C/\\partial V_{BE} = g_m/\\beta$.",
                            "Resistance is the reciprocal of that slope.",
                        ],
                    },
                    {
                        "prompt": "Now substitute $g_m$. Write $r_\\pi$ in terms of $\\beta$, $V_T$ and $I_C$.",
                        "answer": "\\frac{\\beta V_T}{I_C}",
                        "hint": "Dividing by $I_C/V_T$ is multiplying by $V_T/I_C$.",
                        "deconstruct": [
                            "$r_\\pi = \\beta \\big/ (I_C/V_T)$.",
                            "So the input resistance falls as the current rises — a stage biased harder is a heavier load on whatever drives it.",
                        ],
                    },
                    {
                        "prompt": "With $r_o = V_A/I_C$, write the intrinsic gain $g_mr_o$.",
                        "answer": "\\frac{V_A}{V_T}",
                        "hint": "Multiply the two expressions and watch $I_C$ cancel.",
                        "deconstruct": [
                            "$g_mr_o = (I_C/V_T)(V_A/I_C)$.",
                            "$I_C$ appears once on top and once underneath, so the product depends only on the device's Early voltage and the temperature.",
                        ],
                    },
                ],
                "closing": r'''
Three results and one thing to notice about each. $g_m = I_C/V_T$ has no device
parameter in it, so bipolar transconductance is bought with current alone and at a
fixed exchange rate — no square roots, no widths. $r_\pi = \beta V_T/I_C$ is the bill
for that: the base draws current, and the harder the stage is biased the more heavily it
loads its source. And $g_mr_o = V_A/V_T$ is fixed by the process and the temperature and
by nothing the designer does, which makes it the cleanest single figure of merit for a
transistor technology there is — 1800 here, against 90 for the MOSFET of module 1 at
1 mA.
''',
            },
            "build": {
                "title": "Biasing a bipolar stage, with the base drawing what it draws",
                "minutes": 30,
                "brief": r'''
The concept list above claims that a bipolar bias divider "has to be much stiffer than
module 2's". This exercise is where that claim is cashed, because it is not a claim you
can test with a current source standing in for the device — an ideal current source has
no base and asks the divider for nothing.

The canvas carries a real **NPN**: $I_S = 10^{-14}$ A, $\beta_F = 100$, solved by the
same Ebers-Moll equations the diode of EE201 obeys. Collector at the top pin, emitter at
the bottom, base sticking out to the right. Give it a 12 V rail and four resistors.

## The specification

The same operating point as the MOSFET, deliberately, so the two can be read against
each other:

- $I_C = $ **1.00 mA**,
- the emitter sits at **2.00 V**,
- the collector at **7.00 V**,
- and the divider carries **at least ten times the base current**.

Probe the collector.

## Two things are different, and only one of them is obvious

$V_{BE}$ is not a design variable. It is roughly 0.65 V at a milliamp and it moves by
60 mV per decade of current, so you compute $V_B = V_E + V_{BE}$ using 0.65 and accept
that the answer is approximate. That is the obvious difference and it is the small one.

The large one is the fourth bullet. **The base draws $I_C/\beta \approx 10$ µA**, and it
draws it out of the divider's midpoint, where it behaves as a load on a Thévenin source
of resistance $R_1\parallel R_2$. Module 2's divider was 500 kΩ over 250 kΩ, giving
$R_{th} = 167$ kΩ, and it was perfectly good — because a gate on the end of it drew
nothing at all. Wire a base to that same divider instead and the midpoint falls from
4.00 V to **2.49 V**: a 1.51 V collapse, and the stage is nowhere near where it was
designed to be.

So size the divider from the base current, not from a power budget. Ten times $I_B$ is
100 µA, so $R_1 + R_2 \approx 12\,\mathrm{V}/100\,\mathrm{\mu A} \approx 120$ kΩ — and
120 kΩ, not the 750 kΩ that served module 2, is what "stiff" means once a terminal
starts drawing current.

## What the solver will show

With $R_C = 5$ kΩ, $R_E = 2$ kΩ and a 75 kΩ / 24 kΩ divider:

```text
  I_C   1.0236 mA      V_B   2.7230 V      V_BE   0.6554 V
  I_B     10.24 uA     V_E   2.0676 V      V_CE   4.8146 V
  I_E   1.0338 mA      V_C   6.8822 V      beta     100.0
  divider current 123.7 uA, which is 12.1 times the base current
```

The divider still sags — from an unloaded 2.9091 V to 2.7230 V, **186 mV** across its
18.2 kΩ Thévenin resistance — and that sag is why the collector current lands at 1.02 mA
rather than at the 1.00 the arithmetic asked for. It is a sag you can absorb. The same
divider ratio at ten times the resistance (750 kΩ / 240 kΩ) sags 1074 mV instead, and
the collector current falls to **0.59 mA** — 42% low, from a network that is correct in
every ratio and wrong only in its impedance.

## And the reason it matters is not the sag

$\beta$ is not 100. It is "50 to 300" on the data sheet, it varies with current and
temperature, and no two devices from the same reel agree. Watch what the two dividers do
about that:

```text
                          beta = 50    beta = 100    beta = 300
  75k / 24k    (stiff)     -8.3 %       1.024 mA      +6.4 %
  750k / 240k  (weak)     -32.1 %       0.591 mA     +46.3 %
```

A stiff divider holds $V_B$ nearly fixed whatever the base takes, and then the emitter
resistor does the rest of the work — exactly as it did for the MOSFET in module 2, and
for exactly the same reason. A weak one lets $\beta$ set the bias, and $\beta$ is the
one device parameter you are least entitled to rely on.

Nothing is graded on layout.
''',
                "start": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 6},
                        {"id": "q", "kind": "NPN", "x": 8, "y": 6, "rot": 1,
                         "value": 1e-14, "bf": 100, "br": 1},
                        {"id": "g1", "kind": "GND", "x": 8, "y": 11},
                        {"id": "out", "kind": "OUT", "x": 6, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [12, 2]},
                        {"a": [8, 5], "b": [6, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 6},
                        {"id": "rc", "kind": "R", "x": 8, "y": 3, "rot": 1, "value": 5000},
                        {"id": "q", "kind": "NPN", "x": 8, "y": 6, "rot": 1,
                         "value": 1e-14, "bf": 100, "br": 1},
                        {"id": "re", "kind": "R", "x": 8, "y": 9, "rot": 1, "value": 2000},
                        {"id": "g1", "kind": "GND", "x": 8, "y": 11},
                        {"id": "r1", "kind": "R", "x": 12, "y": 3, "rot": 1, "value": 75000},
                        {"id": "r2", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 24000},
                        {"id": "g2", "kind": "GND", "x": 12, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 6, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [12, 2]},
                        {"a": [8, 4], "b": [8, 5]},
                        {"a": [8, 7], "b": [8, 8]},
                        {"a": [8, 10], "b": [8, 11]},
                        {"a": [12, 4], "b": [12, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [9, 6], "b": [9, 5]},
                        {"a": [9, 5], "b": [12, 5]},
                        {"a": [8, 5], "b": [6, 5]},
                    ],
                },
                "checks": [
                    {"name": "one NPN, the right way up, and in forward-active", "code": r'''
c.assert(c.count('NPN') === 1,
  'One bipolar transistor, the one on the canvas. Found ' + c.count('NPN') + '.');
c.assert(c.count('V') === 1, 'One supply — the 12 V rail. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
const d = c.device('q');
const vc = d.v[0], ve = d.v[1], vb = d.v[2];
c.assert(!(ve - vc > 0.1),
  'The emitter is sitting ' + (ve - vc).toFixed(2) + ' V above the collector, so the device ' +
  'is in upside down. Its collector is the TOP pin and belongs towards the supply.');
const vbe = vb - ve, vce = vc - ve;
c.assert(vbe > 0.45,
  'V_BE is ' + vbe.toFixed(3) + ' V, so the base-emitter junction is barely on and almost ' +
  'nothing is flowing. A base left unconnected reads near zero here — the divider has to ' +
  'reach the base pin, which is the pin sticking out to the right of the body.');
c.assert(vbe < 0.80,
  'V_BE is ' + vbe.toFixed(3) + ' V. An exponential does not go much past 0.75 V without ' +
  'the current being enormous, so this is a base being driven far too hard — usually a ' +
  'missing emitter resistor.');
c.assert(vce >= 1.0,
  'V_CE is ' + vce.toFixed(3) + ' V, so the collector junction has come forward-biased and ' +
  'the device is in saturation — the bipolar name for the region where it stops being a ' +
  'current source. It needs a volt of headroom at the very least, and this design leaves it ' +
  'nearly five.');
'''},
                    {"name": "the collector carries 1.00 mA", "code": r'''
const d = c.device('q');
const ic = d.i[0];
c.assert(ic > 1e-9, 'No collector current at all — the base-emitter junction is not conducting.');
/* The diagnosis is attached to the measurement rather than recited whatever it is: a
   hint about a weak divider printed underneath a reading of 2.4 mA sends the reader to
   look at the one part of the circuit that is not the problem. */
const diagnosis = ic < 0.8e-3
  ? ' Well under target is the signature of a divider built at module 2 impedances: the ' +
    'ratio is right, the resistance is several times too high, and the base current pulls ' +
    'the midpoint down. The same ratio at 750k/240k lands at 591 uA.'
  : (ic > 1.5e-3
    ? ' Far over target usually means there is no emitter resistor, or it is far too small. ' +
      'Without one the base voltage sets V_BE directly, and V_BE is an exponential — a ' +
      'tenth of a volt of error is a factor of about fifty in current.'
    : ' A little out means V_B is slightly off: the divider ratio, or the 0.65 V assumed ' +
      'for V_BE against the 0.655 the device actually settles at.');
c.assert(ic >= 0.95e-3 && ic <= 1.09e-3,
  'The collector current is ' + (ic * 1e6).toFixed(1) + ' uA and should land between 950 and ' +
  '1090 — the design targets 1000 and the real V_BE carries it to about 1024.' + diagnosis);
'''},
                    {"name": "the emitter is at 2.0 V and the collector near 7.0 V", "code": r'''
const d = c.device('q');
const vc = d.v[0], ve = d.v[1], ie = -d.i[1];
c.assert(ve >= 1.95 && ve <= 2.15,
  'The emitter should sit at 2.00 V; measured ' + ve.toFixed(3) + ' V. It is I_E through ' +
  'R_E, and note that I_E is the collector current PLUS the base current, so R_E = ' +
  'V_E/I_E is very slightly under 2 kOhm rather than exactly it.');
c.assert(vc >= 6.75 && vc <= 7.10,
  'The collector should sit at 7.00 V; measured ' + vc.toFixed(3) + ' V. That is 12 V minus ' +
  'I_C through R_C, which pins R_C near 5 kOhm.');
c.close(ve / ie, 2000, 0.06,
  'R_E as the circuit reveals it — the emitter voltage divided by the emitter current');
'''},
                    {"name": "the divider carries at least ten times the base current", "code": r'''
/* The whole reason this exercise exists. Everything is measured: the base current comes
   off the device's third terminal, and the divider current is whatever the supply is
   delivering beyond the collector branch. A gate would make the first of these zero and
   the check vacuous, which is exactly why module 2 has no check like it. */
const d = c.device('q');
const ic = d.i[0], ib = d.i[2];
c.assert(ib > 1e-9,
  'The base is drawing no current, so either it is not connected or the device is off. ' +
  'A bipolar base always draws current; that is the premise of this module.');
const beta = ic / ib;
c.assert(beta > 80 && beta < 130,
  'The measured current gain I_C/I_B is ' + beta.toFixed(1) + ', and the device on the canvas ' +
  'has beta_F = 100. A value well below that means the device has been driven into ' +
  'saturation, where the collector junction starts taking base current of its own.');
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1,
  'The supply current has to mean one thing, so this exercise wants exactly one part ' +
  'carrying a solved-for current — the 12 V source. Found ' + ids.length + '.');
const idiv = Math.abs(cur[ids[0]]) - ic;
c.assert(idiv >= 10 * ib,
  'The divider carries ' + (idiv * 1e6).toFixed(1) + ' uA against a base current of ' +
  (ib * 1e6).toFixed(2) + ' uA — a ratio of ' + (idiv / ib).toFixed(2) + ', and this design ' +
  'needs at least 10. Below that the base is no longer a small load on the divider, the ' +
  'midpoint moves with beta, and beta is the one parameter on the data sheet quoted as a ' +
  'range rather than a number.');
c.assert(idiv <= 400e-6,
  'The divider draws ' + (idiv * 1e6).toFixed(1) + ' uA, which is more current than the ' +
  'stage it is biasing. Stiff is not the same as free: ten times the base current is the ' +
  'rule, not as much as possible.');
'''},
                ],
                "hints": [
                    "$I_E = I_C + I_B = 1.00 + 0.01 = 1.01$ mA, so $R_E = 2.00/1.01\\text{ mA} \\approx 2$ kΩ. Using $I_C$ instead of $I_E$ here is a 1% error and does not matter; using $\\beta$ where you meant $\\beta+1$ never does.",
                    "$R_C$ drops $12 - 7 = 5$ V at 1 mA, so it is 5 kΩ — the same value as the MOSFET stage's $R_D$, for the same reason.",
                    "$V_B = V_E + V_{BE} \\approx 2.00 + 0.65 = 2.65$ V. This is the one number in the design you cannot compute exactly, because $V_{BE}$ depends on the current you are still solving for.",
                    "Now the divider. $I_B = I_C/\\beta = 10$ µA, so aim the divider at 100 µA and above: $R_1 + R_2 \\approx 120$ kΩ. Split it for 2.65 V out of 12 V and allow a little extra, because the base current will pull the midpoint down by a couple of hundred millivolts — 75 kΩ over 24 kΩ works and lands 1.02 mA.",
                    "If the current comes out near 0.59 mA, the divider ratio is right and its resistance is ten times too high. That is module 2's divider, and it worked there because a gate draws nothing.",
                ],
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "The differential pair",
            "summary": "Two of everything, arranged so that the amplifier can tell a signal from the interference sitting on top of it.",
            "concepts": [
                "Two matched devices with their sources tied together and fed by a single **tail current source** $I_{SS}$. The pair amplifies the *difference* between its two inputs and, if it is built well, almost nothing of what they have in common.",
                "At balance each side carries $I_{SS}/2$. With $I_{SS} = 2$ mA each device sits at the 1 mA operating point this course has used throughout: $V_{ov} = 1$ V, $g_m = 2$ mA/V, $r_o = 45$ kΩ. Everything from module 1 applies to each half unchanged.",
                "For a purely **differential** input the tail node does not move: whatever current one side gains the other loses, so the total through the tail is constant and the node is a *virtual ground*. Each half is then a common-source stage driven by $v_{id}/2$, which is what the **differential half-circuit** means.",
                "So the gain taken from one drain is $A_d = -g_mR_D/2$, and taken between the two drains it is $-g_mR_D$. With $R_D = 4$ kΩ those are −4 and −8.",
                "For a **common-mode** input both gates move together, the tail node follows them, and each half becomes a degenerated common-source stage. The two halves share the tail resistance, so each half sees twice it: $A_{cm} = -R_D/(2R_{SS} + 1/g_m)$.",
                "**CMRR** is the ratio of the two, and from a single-ended output it works out to $g_mR_{SS} + 1/2$. Note what is not in it: $R_D$ cancels. Common-mode rejection cannot be bought with the load — only with transconductance and with the stiffness of the tail.",
                "Which is the entire argument for the tail being a current source. A 2 kΩ tail resistor on a 12 V rail already drops 4 V and gives $\\mathrm{CMRR} = 4.5$, or 13 dB, which is worthless. A tail *device* at 2 mA has $r_o = V_A/I = 22.5$ kΩ and gives 45.5, or 33 dB, while dropping only its overdrive. Getting far beyond that means raising the tail's output resistance further, which is what a cascode is for and a later course's business.",
                "Large signal: solving the two square laws against $i_1 + i_2 = I_{SS}$ gives $i_1 - i_2 = kv_{id}\\sqrt{I_{SS}/k - v_{id}^2/4}$. Its slope at the origin is exactly $g_m$, and it reaches **full steering** — the whole tail current in one device and none in the other — at $v_{id} = \\sqrt{2}V_{ov} = 1.41$ V. Past that the pair has stopped being an amplifier and become a comparator.",
                "The linear range is a small fraction of that. At $v_{id} = 0.2$ V the exact difference is 0.398 mA against the small-signal 0.400 mA — half a per cent low. Keep the differential input well under one overdrive and the pair behaves; drive it near the steering point and it does not.",
                "Whatever the two halves fail to match appears as an **input offset voltage**, and nothing downstream can remove it — a later stage amplifies the offset exactly as faithfully as the signal. A threshold mismatch appears directly; a $k$ mismatch appears as $(V_{ov}/2)(\\Delta k/k)$. This is where the matching effort in a chip layout goes, and it is why the pair is the input stage of essentially every operational amplifier ever made.",
            ],
            "read": [{
                "title": "One millivolt of signal, fifty of hum, and the amplifier that cannot tell",
                "minutes": 15,
                "body": r'''
A strain gauge at the far end of a rack produces 1 mV. Run a cable from it to the
common-source stage of module 3 and measure the drain.

There is 450 mV of 50 Hz mains hum on it, and 9 mV of signal underneath.

Nothing is faulty. The gauge's ground and the amplifier's ground are two different screws
on two different chassis, with a metre of steel and other people's return currents between
them, and they sit about 50 millivolts apart at mains frequency. The amplifier's input is
the voltage between its gate and *its* ground, and its ground is the thing that moved. It
amplified the 50 mV exactly as faithfully as the 1 mV, because from where it stands the two
are the same kind of thing.

Filtering will not help: the interference is at 50 Hz and so is a good deal of what the
gauge is measuring. Shielding helps and never enough. The problem is structural, and it is
that the amplifier has one input and the situation has two interesting voltages in it.

## Two inputs, one tail

Give it two. Bring both the gauge's signal wire and the gauge's own ground back as
separate wires, put a transistor on each, and arrange for the output to depend on the
*difference* between them. The hum is common to the pair — it moves both wires together —
and the signal is not.

The arrangement that does it is two matched devices with their sources tied together and
the shared node fed by a single current source $I_{SS}$. That one wire between the sources
is what makes it a pair rather than two unrelated stages, and it buys a constraint that
holds no matter what the gates do:

$$i_1 + i_2 = I_{SS}$$

With $I_{SS} = 2$ mA each side rests at 1 mA, which is this course's operating point:
$V_{ov} = 1$ V, $g_m = 2$ mA/V, $r_o = 45$ kΩ. Everything from module 1 applies to each
half unchanged. The build **Bias a pair, and check it is balanced** draws exactly this — a
2 mA tail, 4 kΩ at each drain, both drains resting at 8.00 V — and its central check is
that the two drains rest at the *same* voltage, because a pair that is lopsided with no
input has an error before any signal arrives.

## The differential half-circuit

Drive the two gates in opposite directions: $+v_{id}/2$ on one, $-v_{id}/2$ on the other.
By symmetry whatever current one device gains, the other loses. But the sum is pinned at
$I_{SS}$, so the current through the tail cannot change, so the voltage on the tail node
cannot change either. It is a **virtual ground**: nothing holds it there, the symmetry
does.

That is the whole trick, because a source held at signal ground is precisely module 3's
common-source stage. Each half is an ordinary stage driven by $v_{id}/2$, so from one
drain

$$A_d = -\frac{g_mR_D}{2} = -\frac{2\text{ mA/V}\times 4\text{ k}\Omega}{2} = -4$$

and between the two drains it is $-g_mR_D = -8$, because the other drain is moving the
opposite way by the same amount. Both are right answers to different questions, and quoting
one where the other is meant is a factor-of-two error that survives all the way to a
specification.

## The common-mode half-circuit

Now drive both gates the same way, by $v_{ic}$ — which is what the hum does. Symmetry now
says both currents move the *same* way, so their sum changes, so the tail current changes,
so the tail node has to move. It is no longer a virtual ground and each half is a
degenerated common-source stage.

The only question is how much degeneration, and there is a clean way to see it. Split the
tail resistance $R_{SS}$ into two resistors of $2R_{SS}$ each, in parallel. Nothing about
the circuit has changed — two $2R_{SS}$ in parallel are $R_{SS}$ — but now one of them
belongs to each side, and each half-circuit is a stage degenerated by $2R_{SS}$:

$$A_{cm} = -\frac{R_D}{2R_{SS} + 1/g_m}$$

That factor of two is what the numeric question **What gets through in common mode?** is
asking about, and using $R_{SS}$ alone overstates the leakage by nearly a factor of two.

Divide the two gains and the pair's figure of merit falls out:

$$\mathrm{CMRR} = \frac{|A_d|}{|A_{cm}|}
  = \frac{g_mR_D}{2}\cdot\frac{2R_{SS} + 1/g_m}{R_D} = g_mR_{SS} + \frac{1}{2}$$

$R_D$ has cancelled. Common-mode rejection depends on the transconductance of the devices
and the stiffness of the tail, and on nothing else — which is worth internalising, because
"more gain" is the first instinct when a common-mode specification is missed, and it is
precisely the change that cannot help.

## What the pair is actually worth

```python
import math

GM, R_D = 2e-3, 4000.0
SIGNAL, HUM = 1e-3, 50e-3          # 1 mV of signal, 50 mV of mains on the ground

print(f"one common-source stage    A 9.00           "
      f"          signal {9.0 * SIGNAL * 1e3:5.2f} mV, hum {9.0 * HUM * 1e3:6.2f} mV")
for name, r_ss in (("pair, 2 k tail resistor   ", 2000.0),
                   ("pair, 22.5 k current tail ", 22500.0)):
    a_d = GM * R_D / 2.0
    a_cm = R_D / (2.0 * r_ss + 1.0 / GM)
    print(f"{name} A_d {a_d:4.2f}  A_cm {a_cm:6.4f}  CMRR {a_d / a_cm:5.1f}"
          f" ({20 * math.log10(a_d / a_cm):4.1f} dB)  signal {a_d * SIGNAL * 1e3:5.2f} mV,"
          f" hum {a_cm * HUM * 1e3:6.2f} mV")
```

A 2 kΩ tail resistor gives a CMRR of 4.5 — 13 dB — and leaves 44 mV of hum over 4 mV of
signal. That is barely an improvement on the single stage, and it cost two transistors. The
tail resistor is the problem: at 2 mA it already drops 4 V of a 12 V supply, and making it
larger to raise $g_mR_{SS}$ means dropping more.

Replace it with a current source and the two requirements separate, exactly as they did for
the drain resistor in module 8. A tail *device* at 2 mA has $r_o = V_A/I = 22.5$ kΩ and
needs only its overdrive across it, so the CMRR rises to 45.5, or 33 dB, without costing a
volt. The hum falls to 4.4 mV, comparable at last with the 4 mV of signal.

Comparable, not gone. 33 dB is not a specification anyone would ship, and that is an honest
place to arrive: the pair as drawn here is not yet an instrumentation amplifier.

## Taking the output between the drains

What finishes the job is not taking the output from one drain at all. In common mode both
drains move together, so the *difference* between them does not move: to first order a
differential output has no common-mode gain, and what is left is only whatever the two
sides fail to match. If the drain resistors differ by a fraction $\varepsilon$, the
common-mode difference between the drains is $\varepsilon R_D/(2R_{SS} + 1/g_m)$ against a
differential gain of $g_mR_D$, so

$$\mathrm{CMRR}_{\text{diff}} = \frac{1}{\varepsilon}\left(2g_mR_{SS} + 1\right)$$

With 1% loads and the 2 kΩ tail that is 900, or 59 dB; with the current-source tail, 9100,
or 79 dB. The rejection has become a matching problem rather than a tail problem, which is
why an operational amplifier's input pair is drawn symmetrically, laid out symmetrically,
and given a differential output.

## How much difference it will take

The half-circuit is a linearisation, and the pair has a large-signal behaviour underneath
it. Solving the two square laws against $i_1 + i_2 = I_{SS}$ gives

$$i_1 - i_2 = k\,v_{id}\sqrt{\frac{I_{SS}}{k} - \frac{v_{id}^2}{4}}$$

```python
import math

K, I_SS = 2e-3, 2e-3

def split(v_id):
    """Exact division of the tail current between the two devices."""
    edge = math.sqrt(2.0 * I_SS / K)
    if abs(v_id) >= edge:
        return (I_SS, 0.0) if v_id > 0 else (0.0, I_SS)
    diff = K * v_id * math.sqrt(I_SS / K - v_id * v_id / 4.0)
    return ((I_SS + diff) / 2.0, (I_SS - diff) / 2.0)

gm = math.sqrt(K * I_SS)
print(f"full steering at {math.sqrt(2.0 * I_SS / K):.4f} V,  g_m per side {gm * 1e3:.2f} mA/V")
for v_id in (0.01, 0.1, 0.2, 0.5, 1.0):
    i1, i2 = split(v_id)
    exact, linear = i1 - i2, gm * v_id
    print(f"  v_id {v_id:4.2f} V   exact {exact * 1e3:7.4f} mA   tangent {linear * 1e3:6.4f} mA"
          f"   {100 * (exact / linear - 1):+6.2f} %")
```

The slope at the origin is exactly $g_m$, which is the half-circuit confirming itself. The
departure from that tangent is 0.13% at 100 mV, 0.5% at 200 mV and 13% at a volt, and at
$v_{id} = \sqrt{2}V_{ov} = 1.414$ V one device has the entire tail current and the other has
none. Past that the output stops responding to the input at all: the pair has become a
comparator. The lab **Steering the tail current** builds that function and checks the slope
and the clamps.

## The mistake, and why it is tempting

Treating the tail current source as ideal. It is drawn as a circle with an arrow and no
resistance beside it; and — worse — the differential analysis, which is the analysis you do
first and the one that makes the pair look wonderful, is *correct* to ignore it. The tail
node is a virtual ground for a differential input, so its resistance genuinely does not
appear in $A_d$. A designer can compute the gain, the bandwidth, the swing and the
operating point of a differential pair without ever needing to know what the tail is made
of.

And the one number the tail decides is the one the pair exists for. With an ideal tail the
CMRR is infinite and there is no common-mode budget in the design at all; with the real
thing at 2 mA it is 45.5, and the hum in the opening measurement comes out the same size as
the signal. The parameter that sets the headline specification is invisible in every
calculation that made the circuit look good.

The habit is to write the tail's $r_o = V_A/I_{SS}$ down at the same moment the tail
current is chosen, before any of the pleasant algebra starts.

## Where this stops holding

**Symmetry is an assumption, and mismatch is what it costs.** Every result above used two
identical devices. Whatever they fail to match appears as an **input offset voltage**: a
threshold difference appears directly, and a $k$ difference appears as
$(V_{ov}/2)(\Delta k/k)$. Nothing downstream removes it, because an input-referred offset is
indistinguishable from a real input — 3 mV of offset into a following stage of gain 100 is
300 mV at the output, and it drifts with temperature besides. This is where the matching
effort in a chip layout goes, and it is why input offset voltage is the first line of an
operational amplifier's data sheet.

**The inputs cannot go anywhere they like.** The tail device needs about an overdrive across
it, and each amplifying device needs $V_{DS} \ge V_{ov}$. On the build's circuit — tail node
at 4.00 V, drains at 8.00 V, $V_{GS} = 2$ V per side — that puts the common-mode input range
at roughly 3 V to 9 V on a 12 V supply. Drive both gates below the bottom of it and the tail
device slides into triode, its output resistance collapses, and the rejection this whole
reading is about goes with it. A common-mode specification that is met at mid-rail and
tested nowhere else is not met.

**The linear range is a small fraction of the steering range.** The pair steers fully at
1.414 V and is already half a per cent from its tangent at 0.2 V. Everything computed with
$A_d = -g_mR_D/2$ assumes the input is well inside that, and the departure is not a
correction that can be applied afterwards — it is distortion, and the difference is that it
depends on the signal.

## What to carry forward

One current source shared between two devices, and two symmetric drives the same circuit
treats completely differently: one leaves the tail node still and one does not. The
differential gain is a common-source stage's, halved. The common-mode gain is a degenerated
stage's, with the tail counted twice. Their ratio contains no load resistance, so rejection
is bought with transconductance and with the stiffness of the tail and with nothing else.
''',
            }],
            "quiz": {
                "title": "Difference, common mode and the tail",
                "minutes": 9,
                "questions": [
                    {
                        "q": "Both gates of a balanced pair are driven with equal and opposite signals. What does the tail node do?",
                        "opts": [
                            "it moves with the average of the two inputs",
                            "it stays put — whatever current one side takes, the other gives back",
                            "it moves by half the differential input",
                            "it is undefined without knowing $R_{SS}$",
                        ],
                        "a": 1,
                        "why": r'''
The two drain currents move in opposite directions by equal amounts, so their sum — the
current in the tail — does not change, and neither does the voltage on the tail
resistance. That is what makes it a *virtual* ground: nothing holds it there, the
symmetry does. It is also what licenses the half-circuit, in which one side is analysed
alone as an ordinary common-source stage with its source grounded.
''',
                    },
                    {
                        "q": "A pair runs at $I_{SS} = 2$ mA with $R_D = 4$ kΩ on each side, so each device has $g_m = 2$ mA/V. What is the gain from the differential input to *one* drain?",
                        "opts": ["−8", "−4", "−2", "−16"],
                        "a": 1,
                        "why": r'''
Each gate moves by half the differential input, so one drain sees $-g_mR_D/2 = -4$.
Between the two drains the answer is $-g_mR_D = -8$, because the second drain is moving
the opposite way by the same amount. Both are correct answers to different questions,
and quoting one where the other is meant is a factor-of-two error that survives all the
way to a specification.
''',
                    },
                    {
                        "q": "That pair uses a 2 kΩ tail resistor. Replacing it with a current source whose output resistance is 22.5 kΩ does what to the CMRR?",
                        "opts": [
                            "takes it from 4.5 to 45.5, about 13 dB to 33 dB",
                            "leaves it unchanged, since the DC current is the same",
                            "takes it from 4.5 to 9.0",
                            "makes it infinite",
                        ],
                        "a": 0,
                        "why": r'''
$\mathrm{CMRR} = g_mR_{SS} + 1/2$, so 2 mA/V against 2 kΩ gives 4.5 and against 22.5 kΩ
gives 45.5 — 13 dB becoming 33 dB. Not infinite: a real current source is a transistor
with $r_o = V_A/I$, and at 2 mA that is 22.5 kΩ, not infinity. The DC current being
identical is exactly the point — the tail's *small-signal* resistance is what rejection
depends on, and a resistor and a current source that pass the same DC differ completely
there.
''',
                    },
                    {
                        "q": "A designer doubles $R_D$ on both sides to get more differential gain. What happens to the CMRR?",
                        "opts": [
                            "it doubles as well",
                            "it halves",
                            "it is unchanged, because $R_D$ cancels out of the ratio",
                            "it improves by 6 dB",
                        ],
                        "a": 2,
                        "why": r'''
$R_D$ multiplies the differential gain and the common-mode gain equally, so the ratio
does not notice it: $\mathrm{CMRR} = g_mR_{SS} + 1/2$ contains no load resistance at
all. Rejection comes from two places and two only — the transconductance of the devices
and the stiffness of the tail. This is worth internalising, because "more gain" is the
first instinct when a common-mode specification is missed, and it is precisely the
change that cannot help.
''',
                    },
                    {
                        "q": "With $I_{SS} = 2$ mA, $k = 2$ mA/V² and therefore $V_{ov} = 1$ V per side, at what differential input does one device take the entire tail current?",
                        "opts": ["1.00 V", "0.50 V", "1.41 V", "2.00 V"],
                        "a": 2,
                        "why": r'''
$v_{id} = \sqrt{2}V_{ov} = 1.41$ V. Beyond it the pair is fully steered and the output
stops responding to the input at all — a comparator, not an amplifier. Worth holding
alongside it: the *linear* range is far smaller. At 0.2 V, a seventh of the way, the
difference current is already half a per cent below what the small-signal model
predicts, and the departure grows quickly after that.
''',
                    },
                    {
                        "q": "Two devices in a pair differ slightly, giving the stage a 3 mV input offset. What can a following stage of gain 100 do about it?",
                        "opts": [
                            "nothing — it amplifies the offset to 300 mV along with the signal",
                            "divide it by 100, since offsets refer to the output",
                            "remove it, if it is AC-coupled to the pair's output",
                            "cancel it, since a second stage has an offset of its own",
                        ],
                        "a": 0,
                        "why": r'''
An input-referred offset is indistinguishable from a real input, so every stage after it
treats it as signal: 3 mV becomes 300 mV. This is why the matching effort in a layout
goes into the input pair and almost nowhere else, and why input offset voltage is the
first line of an operational amplifier's data sheet. AC coupling does remove a *static*
offset from the output, at the price of the whole DC response — and it does nothing for
the offset's drift with temperature.
''',
                    },
                ],
            },
            "build": {
                "title": "Bias a pair, and check it is balanced",
                "minutes": 26,
                "brief": r'''
Two devices, at their operating points, are two current sources — so the canvas opens
with a pair of 1 mA sources already sharing a lower node. That shared node is the tail,
and it is the only thing making this a pair rather than two unrelated stages.

The probe is on the left drain.

## The specification

- a **12 V** supply, already drawn,
- each side carries **1.00 mA**, so the tail carries 2.00 mA,
- the tail node sits at **4.00 V**,
- both drains sit at **8.00 V**, and at the *same* voltage as each other,
- so each device has 4 V of $V_{DS}$ against its 1 V overdrive.

Three resistors, and two of them are equal.

## Why the tail voltage is specified

A tail resistor is the cheap way to define that node, and this exercise draws it that
way because the schematic solver needs a resistance there to have a defined voltage at
all. Work out what CMRR 2 kΩ implies once the drawing passes — $g_mR_{SS} + 1/2$ with
$g_m = 2$ mA/V — and the reason every real pair uses a current source instead will not
need arguing.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "I", "x": 9, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p3", "kind": "I", "x": 15, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 12},
                        {"id": "p5", "kind": "OUT", "x": 6, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [15, 2]},
                        {"a": [6, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [12, 7]},
                        {"a": [12, 7], "b": [15, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 6},
                        {"id": "p2", "kind": "I", "x": 9, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p3", "kind": "I", "x": 15, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 12},
                        {"id": "p5", "kind": "OUT", "x": 6, "y": 5},
                        {"id": "p6", "kind": "R", "x": 9, "y": 3, "rot": 1, "value": 4000},
                        {"id": "p7", "kind": "R", "x": 15, "y": 3, "rot": 1, "value": 4000},
                        {"id": "p8", "kind": "R", "x": 12, "y": 8, "rot": 1, "value": 2000},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [15, 2]},
                        {"a": [6, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [12, 7]},
                        {"a": [12, 7], "b": [15, 7]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [15, 4], "b": [15, 5]},
                        {"a": [12, 9], "b": [12, 12]},
                    ],
                },
                "checks": [
                    {"name": "two sides, one supply, and a shared tail", "code": r'''
c.assert(c.count('V') === 1, 'One supply — the 12 V rail. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
c.assert(c.count('I') === 2,
  'Two current sources, one for each device of the pair. Found ' + c.count('I') + '.');
const qs = c.net.parts.filter(function (p) { return p.kind === 'I'; });
c.close(qs[0].value, 1e-3, 0.01, 'the current in one side of the pair');
c.close(qs[1].value, 1e-3, 0.01, 'the current in the other side');
c.assert(qs[0].n2 === qs[1].n2,
  'The two sources must share their lower node. That shared node is the tail, and it is ' +
  'the only thing that makes this a pair rather than two unrelated common-source stages.');
'''},
                    {"name": "the tail carries the whole 2 mA and sits at 4.00 V", "code": r'''
const qs = c.net.parts.filter(function (p) { return p.kind === 'I'; });
const v = c.dc().v;
c.close(v[qs[0].n2], 4.0, 0.02,
  'the tail node voltage — 2 mA through R_SS, so it reads the tail resistor directly');
'''},
                    {"name": "the two drains are balanced, and both at 8.00 V", "code": r'''
const qs = c.net.parts.filter(function (p) { return p.kind === 'I'; });
const v = c.dc().v;
const a = v[qs[0].n1], b = v[qs[1].n1];
c.assert(Math.abs(a - b) < 0.01,
  'The two drains have to rest at the same voltage: a pair that is unbalanced with no ' +
  'input has an offset before any signal arrives. Measured ' + a.toFixed(3) + ' V and ' +
  b.toFixed(3) + ' V, so the two drain resistors are not equal.');
c.close(c.vout(), 8.0, 0.01, 'the probed drain voltage');
'''},
                    {"name": "each device keeps room to work in", "code": r'''
const qs = c.net.parts.filter(function (p) { return p.kind === 'I'; });
const v = c.dc().v;
c.assert(v[qs[0].n1] > v[qs[0].n2],
  'The current sources are upside down: the + pin is the drain and belongs above the tail.');
const vds = v[qs[0].n1] - v[qs[0].n2];
c.assert(vds >= 3.0,
  'Each device needs V_DS comfortably above its 1 V overdrive — the common-mode input ' +
  'has to be able to move without pushing a side into triode. Measured ' +
  vds.toFixed(2) + ' V.');
'''},
                ],
                "hints": [
                    "The tail carries both currents: 2 mA. For 4.00 V at that node, $R_{SS} = 4.0/0.002 = 2$ kΩ, drawn from the shared node down to the ground symbol.",
                    "Each drain resistor carries only its own side's 1 mA and has to drop $12 - 8 = 4$ V, so each is 4 kΩ. They must be equal, or the pair is unbalanced at rest.",
                    "Draw the rail across the top and take both drain resistors from it. The two drains are separate nodes — joining them would short the output the pair exists to produce.",
                    "If one drain reads 8 V and the other 12 V, the second drain resistor is not touching the rail; if the tail reads 2 V, the tail resistor is carrying one side's current only, which means the two sources are not actually sharing a node.",
                ],
            },
            "numeric": {
                "title": "What gets through in common mode?",
                "minutes": 8,
                "brief": r'''
The differential gain of this pair is straightforward: each gate moves by half the
input, so one drain sees $-g_mR_D/2 = -4.0$. The interesting number is the other one —
what happens when both inputs move *together*, which is what interference, ground shift
and supply noise all look like.

In common mode the tail node is no longer still. It rises and falls with the inputs, and
each half of the pair becomes a degenerated common-source stage. The subtlety is how
much degeneration: the two halves share one tail resistor, so each half, considered
alone, sees twice its value.
''',
                "prompt": "What is the magnitude of the gain from a common-mode input to the probed drain?",
                "note": "Both gates driven with the same signal. Four significant figures is more than enough.",
                "diagram": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 3, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 6},
                        {"id": "q1", "kind": "I", "x": 9, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "q2", "kind": "I", "x": 15, "y": 6, "rot": 1, "value": 0.001},
                        {"id": "rd1", "kind": "R", "x": 9, "y": 3, "rot": 1, "value": 4000},
                        {"id": "rd2", "kind": "R", "x": 15, "y": 3, "rot": 1, "value": 4000},
                        {"id": "rss", "kind": "R", "x": 12, "y": 8, "rot": 1, "value": 2000},
                        {"id": "g1", "kind": "GND", "x": 12, "y": 12},
                        {"id": "out", "kind": "OUT", "x": 6, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 4], "b": [3, 6]},
                        {"a": [3, 2], "b": [15, 2]},
                        {"a": [6, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [12, 7]},
                        {"a": [12, 7], "b": [15, 7]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [15, 4], "b": [15, 5]},
                        {"a": [12, 9], "b": [12, 12]},
                    ],
                },
                "check": r'''
/* The drawing is the bias point — each device is standing in as its own DC drain
   current — so the two resistances the common-mode gain depends on are read back out
   of the solved operating point rather than copied off the page. R_D is what the
   probed drain drops from the rail at that side's current; R_SS is where the tail
   node sits while it carries both of them. */
const v = c.dc().v;
const dev = c.net.parts.filter(function (p) { return p.kind === 'I'; });
const sup = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
c.assert(sup, 'there is no supply rail to measure the drain drop against');

const out = c.outNode();
const probed = dev.filter(function (p) { return p.n1 === out; })[0];
c.assert(probed, 'the probe is not on a drain, so there is no half-circuit to take the gain of');

const tail = probed.n2;
const itail = dev.reduce(function (s, p) { return s + (p.n2 === tail ? p.value : 0); }, 0);
const rd = (v[sup.n1] - v[out]) / probed.value;
const rss = v[tail] / itail;

/* g_m is not on the schematic; it is the device — k = 2 mA/V^2 — at whatever drain
   current the drawing biases it to, so re-biasing the pair re-derives it rather than
   quietly keeping 2 mA/V. */
const gm = Math.sqrt(2 * 2e-3 * probed.value);

/* the whole point of the question: each half is degenerated by TWICE the shared tail */
return rd / (2 * rss + 1 / gm);
''',
                "given": [
                    {"label": "g_m, each device", "value": "2.00 mA/V"},
                    {"label": "R_D, each side", "value": "4.00 kΩ"},
                    {"label": "Tail resistance R_SS", "value": "2.00 kΩ"},
                    {"label": "Differential gain to this drain", "value": "−4.00"},
                ],
                "aside": "Each half is degenerated by 2 R_SS, not by R_SS — split the tail resistor "
                         "into two parallel halves of 2 R_SS each and one goes to each side, which is "
                         "the standard trick for turning a shared component into a half-circuit.",
                "answer": 0.8889,
                "tol": 0.01,
                "unit": "V/V",
                "hint": "A degenerated common-source stage has $|A| = R_D/(R_{source} + 1/g_m)$. "
                        "Here $R_{source}$ is $2R_{SS} = 4$ kΩ and $1/g_m$ is 500 Ω.",
                "wrong": "Check whether the tail resistance went in once or twice. Each half-circuit "
                         "sees 2 R_SS; using R_SS alone gives 1.60 and overstates the leakage by "
                         "nearly a factor of two.",
                "why": "$|A_{cm}| = R_D/(2R_{SS} + 1/g_m) = 4000/(4000 + 500) = 0.889$. Put that "
                       "against the differential gain of 4.00 and the CMRR is 4.5, or 13.1 dB — "
                       "a pair that passes almost a quarter of any interference sitting on both "
                       "inputs. The general result is $\\mathrm{CMRR} = g_mR_{SS} + 1/2$, so the "
                       "only cure is a stiffer tail: a current source at 2 mA offers "
                       "$r_o = 22.5$ kΩ and lifts the figure to 45.5, or 33 dB, without "
                       "costing a single extra volt of headroom.",
            },
            "lab": {
                "title": "Steering the tail current",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
The small-signal picture of a pair is two half-circuits and a ratio. The large-signal
picture has to be solved, and it is worth solving once so that the linear range stops
being a rule of thumb.

- `full_steering(i_ss, k)` returns the differential input at which one device takes the
  whole tail current: $\sqrt{2I_{SS}/k}$.
- `tail_split(v_id, i_ss, k)` returns `(i1, i2)` in amperes. Inside the steering range
  the exact solution of the two square laws against $i_1 + i_2 = I_{SS}$ is

  ```text
  i1 - i2 = k * v_id * sqrt(i_ss / k  -  v_id**2 / 4)
  ```

  and the sum is $I_{SS}$, which is two equations for the two currents. Outside the
  range, clamp: all of the current in one side and none in the other.
- `stage_gains(gm, r_d, r_ss)` returns `(a_d, a_cm, cmrr)` for a single-ended output —
  the first two signed and negative, the third a positive ratio.

Check yourself before running the tests: the slope of `tail_split` at the origin has to
come out as $g_m$, and `cmrr` has to equal $g_mR_{SS} + 1/2$ without that formula ever
being written down.
''',
                "files": [{"name": "main.py", "content": r'''
"""The differential pair: how the tail current divides, and what gets rejected."""

import math

K = 2e-3      # A/V^2, each device


def full_steering(i_ss, k=K):
    """The differential input at which one side takes the entire tail current."""
    # TODO: sqrt(2 i_ss / k).
    return 0.0


def tail_split(v_id, i_ss=2e-3, k=K):
    """Return (i1, i2) in amperes for this differential input."""
    # TODO: clamp outside the steering range, both signs.
    # TODO: inside it, the difference is k v_id sqrt(i_ss/k - v_id^2/4) and the sum is i_ss.
    return (0.0, 0.0)


def stage_gains(gm, r_d, r_ss):
    """Return (a_d, a_cm, cmrr) for a single-ended output."""
    # TODO: a_d = -gm r_d / 2, because each gate moves by half the differential input.
    # TODO: a_cm = -r_d / (2 r_ss + 1/gm) — each half is degenerated by TWICE the tail.
    # TODO: cmrr is the magnitude of their ratio.
    return (0.0, 0.0, 0.0)


if __name__ == "__main__":
    print("full steering at:", full_steering(2e-3), "V")
    for v in (0.0, 0.1, 0.5, 1.0, 1.5):
        i1, i2 = tail_split(v)
        print(f"  v_id = {v:4.1f} V -> {i1 * 1e3:6.3f} mA / {i2 * 1e3:6.3f} mA")
    print("resistor tail: ", stage_gains(2e-3, 4000.0, 2000.0))
    print("current-source tail:", stage_gains(2e-3, 4000.0, 22500.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The differential pair: how the tail current divides, and what gets rejected."""

import math

K = 2e-3      # A/V^2, each device


def full_steering(i_ss, k=K):
    """The differential input at which one side takes the entire tail current."""
    return math.sqrt(2.0 * i_ss / k)


def tail_split(v_id, i_ss=2e-3, k=K):
    """Return (i1, i2) in amperes for this differential input."""
    edge = full_steering(i_ss, k)
    if v_id >= edge:
        return (i_ss, 0.0)
    if v_id <= -edge:
        return (0.0, i_ss)
    diff = k * v_id * math.sqrt(i_ss / k - v_id * v_id / 4.0)
    return ((i_ss + diff) / 2.0, (i_ss - diff) / 2.0)


def stage_gains(gm, r_d, r_ss):
    """Return (a_d, a_cm, cmrr) for a single-ended output."""
    a_d = -gm * r_d / 2.0
    a_cm = -r_d / (2.0 * r_ss + 1.0 / gm)
    return (a_d, a_cm, abs(a_d / a_cm))


if __name__ == "__main__":
    print("full steering at:", full_steering(2e-3), "V")
    for v in (0.0, 0.1, 0.5, 1.0, 1.5):
        i1, i2 = tail_split(v)
        print(f"  v_id = {v:4.1f} V -> {i1 * 1e3:6.3f} mA / {i2 * 1e3:6.3f} mA")
    print("resistor tail: ", stage_gains(2e-3, 4000.0, 2000.0))
    print("current-source tail:", stage_gains(2e-3, 4000.0, 22500.0))
'''}],
                "hints": [
                    "`full_steering` is `math.sqrt(2 * i_ss / k)`. With the course numbers it is $\\sqrt{2}$ volts, because $\\sqrt{I_{SS}/k}$ is the per-side overdrive and that is 1 V here.",
                    "In `tail_split`, handle both clamps before touching the square root — outside the range the expression under it goes negative and `math.sqrt` raises rather than returning something wrong, which is at least honest.",
                    "Given the difference and the sum, each current is `(sum ± difference) / 2`. Keep the sign of `v_id` in `diff` rather than taking an absolute value, or the pair will steer the same way for both polarities.",
                    "In `stage_gains` the common trap is `2 * r_ss`. The tail resistor is shared, so each half-circuit sees twice it; using `r_ss` alone makes the common-mode gain look nearly twice as large as it is.",
                ],
                "tests": [
                    {"name": "the steering point is where the square laws say", "code": r'''
edge = full_steering(2e-3)
assert abs(edge - 1.4142135623730951) < 1e-12, \
    f"sqrt(2 * 2e-3 / 2e-3) is sqrt(2), got {edge}"
assert abs(full_steering(2e-3, 8e-3) - 0.7071067811865476) < 1e-12, \
    "a device four times wider halves the steering voltage"
'''},
                    {"name": "at balance the current divides evenly, and it always sums to the tail", "code": r'''
i1, i2 = tail_split(0.0)
assert abs(i1 - 1e-3) < 1e-15 and abs(i2 - 1e-3) < 1e-15, \
    f"with no input each side takes half of 2 mA, got {i1} and {i2}"
for v in (-1.0, -0.3, 0.0, 0.25, 0.9, 1.3):
    a, b = tail_split(v)
    assert abs(a + b - 2e-3) < 1e-15, f"at v_id = {v} the two currents sum to {a + b}, not 2 mA"
    assert a >= 0.0 and b >= 0.0, f"at v_id = {v} a current came out negative: {a}, {b}"
'''},
                    {"name": "the slope at the origin is the transconductance", "code": r'''
a, b = tail_split(0.001)
slope = (a - b) / 0.001
assert abs(slope - 2e-3) < 1e-8, \
    f"the difference current should start off at g_m = 2 mA/V per volt, got {slope}"
'''},
                    {"name": "beyond the steering point one side is off", "code": r'''
assert tail_split(1.5) == (2e-3, 0.0), f"1.5 V is past sqrt(2), got {tail_split(1.5)}"
assert tail_split(-1.5) == (0.0, 2e-3), f"and the other way round, got {tail_split(-1.5)}"
near = tail_split(1.41)
assert near[1] > 0.0, "just inside the steering point the far side still carries something"
assert near[1] < 2e-6, f"but not much: expected under 2 uA, got {near[1]}"
'''},
                    {"name": "the small-signal model is already 0.5% out at a fifth of an overdrive", "code": r'''
a, b = tail_split(0.2)
exact = a - b
linear = 2e-3 * 0.2
assert abs(exact - 3.9799497484264805e-4) < 1e-12, \
    f"expected 0.39799 mA of difference current, got {exact}"
assert exact < linear, "the square-law pair is always a little softer than its tangent"
assert 0.004 < (linear - exact) / linear < 0.006, \
    f"expected about half a per cent low, got {(linear - exact) / linear}"
'''},
                    {"name": "rejection depends on the tail and not on the load", "code": r'''
a_d, a_cm, cmrr = stage_gains(2e-3, 4000.0, 2000.0)
assert abs(a_d + 4.0) < 1e-12, f"-g_m R_D / 2 is -4.00, got {a_d}"
assert abs(a_cm + 0.8888888888888888) < 1e-12, \
    f"-4000 / (4000 + 500) is -0.8889, got {a_cm}"
assert abs(cmrr - 4.5) < 1e-12, f"a 2 k tail gives a CMRR of 4.5, got {cmrr}"
assert abs(stage_gains(2e-3, 10000.0, 2000.0)[2] - 4.5) < 1e-12, \
    "R_D cancels out of the CMRR entirely, so changing it must not move the answer"
assert abs(stage_gains(2e-3, 4000.0, 22500.0)[2] - 45.5) < 1e-12, \
    "a current-source tail of 22.5 k should give 45.5"
'''},
                ],
            },
        },

        # ---- M11 ----------------------------------------------------------
        {
            "title": "Output stages and the current you have to deliver",
            "summary": "At the end of the chain the question stops being how much gain and becomes how many milliamps, and how much heat.",
            "concepts": [
                "Every stage so far has driven either nothing at all or a resistor chosen because it was convenient. An **output stage** drives whatever the application hands it — a few hundred ohms, a transducer, a length of cable — and at that point the design question is not gain. It is current, and the heat that comes with it.",
                "The natural output stage is a source follower, because $1/g_m$ is the lowest output resistance a single device offers. Module 7's result is the whole design equation: the loaded gain is the divider $R_L/(R_L + 1/g_m)$, so a required fraction of the signal fixes $1/g_m$, and $1/g_m$ fixes the bias current through $g_m = \\sqrt{2kI_D}$.",
                "That chain is brutal, because it runs through a square. Keeping 90% of the signal into 1 kΩ needs $1/g_m \\le 111$ Ω, so $g_m \\ge 9$ mA/V, so $I_D \\ge 20$ mA — twenty times everything this course has done so far, for one specification about a load.",
                "**Class A** means the device conducts for the whole cycle. Bias the follower with a tail current source $I_Q$: the device current is $I_Q + v_{out}/R_L$, which reaches zero on the negative half when $v_{out} = -I_QR_L$. That is a hard ceiling — the peak output into $R_L$ can never exceed $I_QR_L$, however generous the supply is.",
                "So a class-A stage's bias current is set by the *largest* signal it must ever deliver, and it draws that current continuously whether or not the signal is there.",
                "Efficiency follows. With $\\pm V_{DD}$ rails the supplies deliver $2V_{DD}I_Q$ at all times; at the very best — full swing, with $I_Q$ sized exactly for it — the load receives $V_{DD}^2/(2R_L)$, and the ratio is **25%**. Three quarters of the power is heat in the devices, at best.",
                "And the dissipation is **largest with no signal at all**: the supply power is fixed and the load is taking none of it. A class-A output stage runs hottest doing nothing, which is the opposite of every intuition from digital electronics.",
                "**Class B** push-pull fixes the economics: an n-channel device sources the positive half, a p-channel device sinks the negative half, and the quiescent current is zero. The best efficiency rises to $\\pi/4 = 78.5\\%$ and the idle dissipation falls to nothing. What it introduces is **crossover distortion** — near zero output neither device has enough gate drive to conduct, so the waveform has a flat step through the crossing, and it is worst for small signals, which is exactly where it is most audible.",
                "**Class AB** is what almost everything actually uses: bias the pair with a small quiescent current so both are conducting near the crossing, then let each take its own half. Nearly all of class B's efficiency and very little of its distortion — at the price of a bias network that has to track the devices' temperature, because a quiescent current that depends exponentially or quadratically on a bias voltage will run away if that voltage does not fall as the devices warm.",
                "Two sizing rules fall out of the above and are worth carrying. A class-A heatsink is sized from the **idle** condition; a class-AB heatsink is sized from the **loudest** condition. Getting that backwards is a design that passes the bench and fails the customer.",
            ],
            "read": [{
                "title": "Ninety per cent into a kilohm, and the twenty milliamps it costs",
                "minutes": 15,
                "body": r'''
Every stage in this course so far has driven either nothing at all or a resistor chosen
because it was convenient. Here is a real specification instead, one line long, of the kind
that arrives written on somebody else's document:

```text
   The output shall deliver at least 90% of the signal into a 1 kilohm load.
```

Not a word about gain. Module 7 already gave the tool for it: a source follower is a
voltage source equal to its input sitting behind $1/g_m$, so what reaches the load is the
divider $R_L/(R_L + 1/g_m)$. Setting that to 0.9 gives $1/g_m = 111$ Ω, and $g_m$ is bought
with current through $g_m = \sqrt{2kI_D}$, which rearranges to $I_D = g_m^2/2k$.

```python
K, R_L = 2e-3, 1000.0

for fraction in (0.5, 0.667, 0.9, 0.95, 0.99):
    r_out = R_L * (1.0 - fraction) / fraction        # the 1/g_m this loaded gain needs
    gm = 1.0 / r_out
    print(f"deliver {fraction * 100:5.1f} % of the signal:  1/gm {r_out:6.1f} ohm"
          f"   g_m {gm * 1e3:6.2f} mA/V   bias current {gm * gm / (2.0 * K) * 1e3:8.2f} mA")
```

**20.25 mA.** Twenty times the current every other stage in this course runs at, for one
sentence about a load, with no gain asked for and none delivered. Two thirds of the signal
was free — that is the 1 mA follower of module 7. Nine tenths costs twenty milliamps.
Ninety-nine hundredths costs two and a half amps.

The square is what does it. Halving $1/g_m$ needs twice the $g_m$ and therefore four times
the current, and the last few per cent of a divider ratio are the expensive ones. This is
the chain the slider exercise **Deliver the signal into a real load, and count the cost**
puts under your hands: R1 is $1/g_m$, and every notch you drag it down is a bias current
rising as $1/R_1^2$.

## A second current requirement, from a different direction

The 20.25 mA came from an impedance. There is another constraint on the same current, and
it comes from the swing.

Bias the follower with a tail current source $I_Q$ from the output node to the negative
rail. At any instant the output device carries the tail current plus whatever the load is
taking:

$$i_D = I_Q + \frac{v_{out}}{R_L}$$

On the positive half-cycle that is more current, which the device can supply. On the
negative half-cycle it is less, and it reaches **zero** when $v_{out} = -I_QR_L$. Below
that the tail source is asking for more current than the load and the device between them
can jointly supply, so the device turns off and the waveform stops. **Class A** is the name
for the arrangement in which that does not happen — the device conducts for the whole cycle
— and it requires

$$I_Q \ge \frac{V_p}{R_L}$$

Notice what is absent: the supply voltage. This limit is about current, and a bigger rail
does not move it. For a 4 V peak into 1 kΩ it demands 4 mA, which is comfortably inside the
20.25 mA the impedance requirement already forced. Take the load down to 100 Ω and the two
swap places dramatically — 90% then needs $1/g_m = 11.1$ Ω and over two amps — so the habit
is to compute both and take the larger, rather than assuming which one binds.

## Where the power goes

The tail source draws $I_Q$ from the negative rail at all times, and on average the same
$I_Q$ comes out of the positive one. So on $\pm V_{DD}$ rails the supplies deliver
$2V_{DD}I_Q$ — a fixed number, with no signal in it anywhere.

```python
import math

V_DD, R_L, I_Q = 12.0, 1000.0, 20.25e-3

p_supply = 2.0 * V_DD * I_Q
print(f"class A draws {p_supply * 1e3:.1f} mW from the rails at every instant")
for v_p in (0.0, 3.0, 6.0, 12.0):
    p_load = v_p * v_p / (2.0 * R_L)
    print(f"   peak {v_p:5.2f} V   load {p_load * 1e3:5.1f} mW"
          f"   devices {(p_supply - p_load) * 1e3:6.1f} mW"
          f"   efficiency {100 * p_load / p_supply:5.2f} %")

print("class B, same rails and load, no quiescent current:")
for v_p in (3.0, 2.0 * V_DD / math.pi, 12.0):
    p_load = v_p * v_p / (2.0 * R_L)
    p_sup = 2.0 * V_DD * v_p / (math.pi * R_L)
    print(f"   peak {v_p:5.2f} V   load {p_load * 1e3:5.1f} mW"
          f"   devices {(p_sup - p_load) * 1e3:6.1f} mW"
          f"   efficiency {100 * p_load / p_sup:5.2f} %")
```

Read the class-A block downwards and one column never changes: the supply always delivers
486 mW. The load takes $V_p^2/2R_L$, and the devices dissipate the difference — so the
devices are hottest when the load is taking **nothing**. A class-A output stage runs at its
maximum temperature with no signal at all, which inverts every instinct carried over from
digital electronics, where a circuit doing nothing is a circuit costing nothing.

The efficiency column tops out at 14.8%, not the 25% the derivation **Why class A stops at
a quarter** arrives at, and the gap is worth understanding rather than explaining away. The
25% assumes $I_Q$ sized *exactly* for full swing, $I_Q = V_{DD}/R_L = 12$ mA. Here $I_Q$ is
20.25 mA, because it was set by the impedance requirement instead, and every extra milliamp
is pure heat. Even the 25% is a ceiling met only at full output: at a quarter of full swing
the numerator falls by sixteen and the denominator does not move at all.

## Two devices instead of one

The waste has one cause: a single device has to source current on one half-cycle and *sink*
it on the other, and the only way it can sink is by being biased above the current it will
ever have to sink. Use two devices instead. An n-channel device sources the positive half
from the top rail; a p-channel device sinks the negative half to the bottom rail; each rests
at zero current. That is **class B**, and the second block prices it.

At full output it delivers 78.5% — $\pi/4$, which is what the same integral gives when the
supply current follows the signal instead of standing still. At idle it dissipates nothing.
Against class A's 486 mW of permanent heat, its worst case is 29 mW.

What it introduces is **crossover distortion**. With zero quiescent current, each device
needs its threshold's worth of gate drive before it conducts at all, so there is a band
around zero output where neither is on and the output does not follow the input. The
waveform acquires a flat step through the crossing. The severity of that step does not
scale with the signal, so as a *fraction* it is worst for small signals — the exact reverse
of module 5's square-law distortion, which grows with drive, and much more offensive to
listen to for that reason.

**Class AB** is what almost everything actually uses: bias the pair with a small but
non-zero quiescent current so that both devices are conducting through the crossing, then
let each take its own half. Nearly all of class B's efficiency, because that current is
small compared with the peaks, and very little of its distortion.

## The mistake, and why it is tempting

Sizing an output stage's heatsink from the loudest condition.

It is the correct rule for almost everything else in the amplifier. The supply, the devices'
current rating, the load, the clipping margin, the distortion, and the thermal design of a
class-B or class-AB stage are all worst at full output, so the test plan says "drive it to
full output and measure everything", and that test passes. The class-A stage above
dissipates 414 mW at full output and **486 mW with the input disconnected** — 17% more, in
the one condition that has no line in the test plan, and the condition the amplifier will
spend most of its service life in.

The reason the rule inverts is in the first column of the block above. Class A's supply
power does not depend on the signal, so the device dissipation is a fixed number minus the
load power, and subtracting more leaves less. Once that sentence is in hand the rule needs
no memorising: **a class-A heatsink is sized from idle, a class-AB heatsink from a signal.**
Getting it backwards is a design that passes on the bench and fails in the field, slowly,
in someone else's building.

## Where this stops holding

**Class B's worst case is not full output either.** Its device dissipation is
$2V_{DD}V_p/(\pi R_L) - V_p^2/(2R_L)$, which is a downward parabola in $V_p$ and peaks at
$V_p = 2V_{DD}/\pi$, about two thirds of the rail. The block shows it: 29.2 mW at 7.64 V
against 19.7 mW at 12 V, half again as much heat at two thirds of the output. And at that
point the efficiency is exactly 50%, so the devices are dissipating precisely what the load
receives. "Size it from the loudest condition" is a first approximation for class AB;
the honest worst case is a signal about two thirds of full swing.

**$g_m$ moves through the cycle.** The follower's output resistance is $1/g_m$, and
$g_m = \sqrt{2kI_D}$ depends on the instantaneous drain current, which in class A swings
from $I_Q + V_p/R_L$ down to nearly zero. So $1/g_m$ is not a constant, the divider ratio is
not a constant, and the follower has a distortion of its own that module 5's
$\hat{V}/(4V_{ov})$ was not written to describe. It falls as the bias current rises, which
is one more thing the 20 mA was buying.

**Temperature closes a loop.** Everything above assumed the operating point stays where it
was put. In an output stage it does not: a class-AB quiescent current depends steeply on the
bias voltage, the devices' threshold falls as they warm, so unless the bias voltage falls
with them the idle current climbs, which warms them further, which raises it again. That is
positive feedback with a thermal time constant, and it is why every class-AB output stage
has its bias element bolted to the same heatsink as the output devices, rather than sitting
on the board where it belongs electrically.

## What to carry forward

At the end of the chain the questions change. Not how much gain, but how many milliamps —
and there are two independent current requirements, one from the output impedance the load
demands and one from the peak the swing demands. Not how much power, but where it goes: a
class-A stage's supply draw does not know whether there is a signal, so the heat is largest
when the output is smallest. And the fix for both is two devices instead of one, which
costs nothing but a bias network that has to follow the temperature of the things it is
biasing.
''',
            }],
            "tune": {
                "title": "Deliver the signal into a real load, and count the cost",
                "minutes": 10,
                "brief": r'''
Module 7 established that a source follower, looked at from its output, is a voltage
source equal to its input sitting behind a resistance of $1/g_m$. Hang a load on it and
what the load receives is a plain divider — which is exactly the model on the screen.

Read the two sliders as the two things they are:

- **R1** is the follower's own output resistance, $1/g_m$. It is not a component you
  buy; it is what the bias current gives you, through $I_Q = 1/(2kR_1^2)$ with
  $k = 2$ mA/V². R1 = 500 Ω is the 1 mA this course has used all along; R1 = 200 Ω is
  6.25 mA; R1 = 100 Ω is 25 mA.
- **R2** is the load.

The input is 1 V, so **Vout reads as the fraction of the signal that survives**, and
**I total is the signal current the stage has to deliver**. Both matter: a follower can
only deliver current up to its own bias, so the current reading is also a statement
about $I_Q$.
''',
                "prompt": "Deliver at least 0.900 V of a 1 V signal into the load \u2014 and make it a load that actually draws 0.400 mA or more.",
                "note": "Either constraint alone is easy. Together they say: keep almost all of the signal, into something low-impedance. Both must hold at once.",
                "model": "divider",
                "initial": {"r1": 2200, "r2": 4700},
                "constants": {"vin": 1},
                "plotKey": "vout",
                "constraints": [
                    {"k": "vout", "label": "Vout \u2265 0.900 V of the 1 V input", "min": 0.90},
                    {"k": "i", "label": "I \u2265 0.400 mA into the load", "min": 0.40},
                ],
            },
            "quiz": {
                "title": "Current, efficiency and heat",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A source follower biased by a 1 mA tail current source drives a 1 kΩ load. What is the largest negative peak it can produce before the device cuts off?",
                        "opts": ["12 V, set by the supply", "1 V", "0.5 V", "2 V"],
                        "a": 1,
                        "why": r'''
The device current is $I_Q + v_{out}/R_L$, and it reaches zero at
$v_{out} = -I_QR_L = -1\text{ mA}\times 1\text{ k}\Omega = -1$ V. Below that the tail
source is asking for more current than the load and the device between them can supply,
so the device turns off and the waveform stops. Notice the supply never entered the
calculation: this limit is about current, and a bigger rail does not move it.
''',
                    },
                    {
                        "q": "A follower must deliver 90% of its input into a 1 kΩ load. Roughly what bias current does that need, with $k = 2$ mA/V²?",
                        "opts": ["about 1 mA", "about 2 mA", "about 20 mA", "about 111 mA"],
                        "a": 2,
                        "why": r'''
$R_L/(R_L + 1/g_m) = 0.9$ needs $1/g_m = 111$ Ω, so $g_m = 9$ mA/V and
$I_D = g_m^2/(2k) = (0.009)^2/0.004 = 20$ mA. The square is what makes it expensive:
asking for nine tenths rather than two thirds of the signal moved the current from about
1 mA to about 20 mA. 111 is the output resistance in ohms, not a current — a useful
number, but not this one.
''',
                    },
                    {
                        "q": "What is the best efficiency a class-A output stage can reach, with a current-source bias and $\\pm V_{DD}$ supplies?",
                        "opts": ["50%", "25%", "78.5%", "100%"],
                        "a": 1,
                        "why": r'''
25%. The supplies deliver $2V_{DD}I_Q$ constantly; at full swing the load receives
$V_{DD}^2/(2R_L)$, and with $I_Q$ sized exactly for that swing ($I_Q = V_{DD}/R_L$) the
ratio is one quarter. 78.5% is $\pi/4$, which belongs to class B. And the 25% is a
*ceiling* reached only at full swing — at a tenth of full swing the efficiency is a
hundredth of it, because the load power goes as the square while the supply power does
not move at all.
''',
                    },
                    {
                        "q": "When does the device in a class-A output stage dissipate the most power?",
                        "opts": [
                            "at full output swing",
                            "with no signal at all",
                            "at half of full swing",
                            "it is constant, whatever the signal",
                        ],
                        "a": 1,
                        "why": r'''
With no signal. The supply delivers a fixed $2V_{DD}I_Q$ regardless, and whatever the
load does not take is dissipated in the device — so the device is hottest when the load
is taking nothing. The heatsink for a class-A stage is therefore sized from the idle
condition, which is the opposite of the digital instinct that a circuit doing nothing is
a circuit costing nothing.
''',
                    },
                    {
                        "q": "Where does crossover distortion in a class-B stage come from?",
                        "opts": [
                            "the two devices conducting at the same time near zero output",
                            "the supply sagging at high output",
                            "neither device having enough gate drive to conduct while the output passes through zero",
                            "the load capacitance at the output node",
                        ],
                        "a": 2,
                        "why": r'''
With zero quiescent current, each device needs its threshold's worth of drive before it
conducts at all, so there is a band around zero output where neither is on and the
output does not follow the input. The waveform gets a flat step through the crossing.
Its severity does not scale with signal size, so it is proportionally *worst* for small
signals — the reverse of the square-law distortion of module 5, and much more offensive
to listen to for exactly that reason.
''',
                    },
                    {
                        "q": "What does class AB change, and what does it cost?",
                        "opts": [
                            "a small quiescent current keeps both devices conducting through the crossing; the cost is a bias network that must track the devices' temperature",
                            "it doubles the supply voltage, at the cost of efficiency",
                            "it removes the second device, at the cost of swing",
                            "it adds feedback around the output stage, at the cost of bandwidth",
                        ],
                        "a": 0,
                        "why": r'''
Class AB idles at a small but non-zero current, so neither device fully turns off near
the crossing and the flat step disappears; the efficiency is barely worse than class B
because that current is small compared with the peaks. The catch is thermal: the
quiescent current depends steeply on the bias voltage, the devices' threshold falls as
they warm, and unless the bias voltage falls with them the idle current climbs, which
warms them further. Every class-AB output stage therefore has a bias element bolted to
the same heatsink as the output devices.
''',
                    },
                ],
            },
            "derive": {
                "title": "Why class A stops at a quarter",
                "minutes": 11,
                "vars": ["V_p", "R_L", "V_DD", "I_Q", "P_L", "P_S"],
                "brief": r'''
The 25% is quoted everywhere and it is worth four lines of algebra rather than trust,
because the derivation shows exactly which assumptions it rests on — full swing, and a
bias current sized for that swing and no larger.

Take a class-A follower between $+V_{DD}$ and $-V_{DD}$, biased by a tail current source
$I_Q$, driving $R_L$ to ground with a sinusoidal output of peak $V_p$.
''',
                "steps": [
                    {
                        "prompt": "Write the average power delivered to $R_L$ by a sinusoid of peak $V_p$.",
                        "answer": "\\frac{V_p^{2}}{2 R_L}",
                        "hint": "The RMS value of a sinusoid is its peak over $\\sqrt{2}$, and power is RMS squared over resistance.",
                        "deconstruct": [
                            "$V_{rms} = V_p/\\sqrt{2}$.",
                            "$P = V_{rms}^2/R_L$, and squaring the $\\sqrt{2}$ gives the 2 underneath.",
                        ],
                    },
                    {
                        "prompt": "The tail source draws $I_Q$ from the negative rail at all times, and the same $I_Q$ comes on average out of the positive rail. Write the total average power taken from the two supplies.",
                        "answer": "2 V_{DD} I_Q",
                        "hint": "Each rail is at $V_{DD}$ from ground and passes $I_Q$; there are two of them.",
                        "deconstruct": [
                            "Each supply contributes $V_{DD}I_Q$.",
                            "Nothing in that expression depends on the signal — which is the fact the whole result turns on.",
                        ],
                    },
                    {
                        "prompt": "Divide one by the other. Write the efficiency in terms of $V_p$, $R_L$, $V_{DD}$ and $I_Q$.",
                        "answer": "\\frac{V_p^{2}}{4 V_{DD} I_Q R_L}",
                        "hint": "Dividing by $2V_{DD}I_Q$ multiplies the existing 2 in the denominator up to 4.",
                        "deconstruct": [
                            "$\\left(\\frac{V_p^2}{2R_L}\\right) \\big/ \\left(2V_{DD}I_Q\\right)$.",
                            "The two denominators multiply together.",
                        ],
                    },
                    {
                        "prompt": "The best case is full swing, $V_p = V_{DD}$, with the bias sized exactly to deliver it, $I_Q = V_{DD}/R_L$. Substitute both and write the efficiency.",
                        "answer": "\\frac{1}{4}",
                        "hint": "The substitution leaves $V_{DD}^2$ over $4V_{DD}^2$; $R_L$ cancels against the $R_L$ inside $I_Q$.",
                        "deconstruct": [
                            "The denominator becomes $4V_{DD}(V_{DD}/R_L)R_L = 4V_{DD}^2$.",
                            "The numerator is $V_{DD}^2$, so the whole thing is one quarter.",
                        ],
                    },
                ],
                "closing": r'''
Two things the derivation makes plain that the bare number hides. First, 25% is a
*ceiling*, met only at full swing: back the output off to a tenth of the rail and the
numerator falls by a hundred while the denominator does not move at all, so the
efficiency is a quarter of one per cent. Real signals spend most of their time far below
their peaks, which is why a class-A amplifier's average efficiency is dreadful even by
its own standard. Second, the whole argument rests on the supply current being constant,
and that is the thing class B changes: let the current follow the signal and the same
calculation gives $\pi/4$ instead — at the price of the two devices having to hand over
to each other cleanly, which is the rest of this module's problem.
''',
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
