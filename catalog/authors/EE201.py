"""EE201 — Semiconductor Devices and Diodes.

A second-year course. It assumes the first year: DC and AC circuit analysis,
phasors and impedance, complex numbers and calculus, Boolean algebra, basic
Python, and fields. It assumes nothing above that — no prior device physics, no
prior transistors, no prior semiconductor vocabulary.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number here was produced by running the code, not assumed
  * sandbox notices were written after reading the visualiser's source in
    src/studio.js, and describe what that code actually draws at those values
  * build checks measure what the circuit does; the schematic editor is linear,
    so every diode appears as its piecewise-linear equivalent, which is the
    modelling idea the module is teaching anyway
"""

COURSE = {
    "id": "EE201",
    "title": "Semiconductor Devices and Diodes",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE102"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◈",
    "summary": (
        "Every component in the first year was linear: double the voltage and the current "
        "doubled. The diode is the first one that is not, and almost everything interesting "
        "in electronics follows from that. This course builds the diode from the crystal up "
        "— what doping does, why a junction develops a voltage across it with nothing "
        "attached, and where the exponential in the diode equation comes from — and then "
        "puts it to work turning alternating current into a usable supply rail. By the end "
        "you can size a rectifier and its reservoir capacitor to a stated ripple, design a "
        "Zener regulator that survives its worst case, and say precisely why a diode with "
        "0.7 V across it and 10 mA through it is not a 70 Ω resistor."
    ),
    "outcomes": [
        "Explain what doping does to silicon, and calculate the built-in potential and depletion width of a pn junction from the doping levels.",
        "Use the Shockley diode equation quantitatively: find the current from the voltage, the voltage from the current, and the 60 mV per decade slope that connects them.",
        "Find a diode's operating point by the load-line method and by numerical solution, replace it with a piecewise-linear model when a hand calculation needs one, and measure the real device beside the model to find where the straight line stops being the curve.",
        "Distinguish a diode's static resistance from its dynamic resistance, and say which one governs which measurement.",
        "Design a full-wave rectifier and reservoir capacitor to meet a stated ripple, and account for the diode drops, the peak inverse voltage and the peak repetitive current.",
        "Design a Zener shunt regulator that holds its output across the full range of line and load, and compute its line regulation from the dynamic resistance.",
        "Compute a junction's capacitance at any reverse bias from its zero-bias value and its grading exponent, and size a varactor-tuned circuit and its bias network against the tuning range and the loaded Q at the same time.",
        "Design the diode circuits that shape a waveform rather than rectify it — clippers, clamps, peak detectors and multipliers — including how flat a clipped level really is and how far a clamp droops between clamping instants.",
        "Predict from the charge-control model how long a conducting diode goes on conducting after it is reversed, and damp the resonance that the resulting snap excites in the surrounding loop.",
        "Say what a Schottky diode, an LED and a photodiode each change about the pn junction and what each change costs, and size the circuit around each one accordingly.",
    ],
    "assessment": (
        "Ten quizzes, four guided derivations, seven circuits drawn and measured in the "
        "schematic editor and eight Python labs checked by execution — and, because "
        "not all of this subject is code, two intuition sandboxes, two fill-the-blanks "
        "listings, a schematic-symbol drill and a numeric design problem. The capstone "
        "designs a complete unregulated-plus-regulated supply and then proves it by "
        "time-stepped simulation."
    ),
    "reading": [
        "*The Art of Electronics*, Horowitz & Hill — chapter 1, sections 1.6 to 1.8, on diodes and power supplies.",
        "*Microelectronic Circuits*, Sedra & Smith — chapter 4, for the diode equation and every model built on it.",
        "*Semiconductor Physics and Devices*, Neamen — chapters 4 to 7, for the physics behind the built-in potential.",
        "Any manufacturer's 1N4148 and 1N4007 data sheets, side by side. The difference between them is the whole of module 3.",
        "*Physics of Semiconductor Devices*, Sze & Ng — chapters 2, 3 and 13, for junction capacitance, the metal-semiconductor barrier and photodetectors.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Doping, the pn junction and the built-in potential",
            "summary": "Where the diode's asymmetry comes from: two pieces of silicon that are different, and the voltage that appears where they meet.",
            "concepts": [
                "Pure silicon at room temperature has equal numbers of mobile electrons and holes, both about $n_i = 1.0\\times10^{16}$ m$^{-3}$. Silicon has about $5\\times10^{28}$ atoms per cubic metre, so that is one carrier per $5\\times10^{12}$ atoms, which is why pure silicon is a poor conductor.",
                "**Doping** replaces a few silicon atoms with impurities. A group-V donor (phosphorus, arsenic) contributes a spare electron and makes **n-type** material; a group-III acceptor (boron) contributes a spare hole and makes **p-type**.",
                "Doping levels are of order $10^{21}$ to $10^{24}$ m$^{-3}$ — still under one atom in a thousand, yet enough to raise the conductivity by many orders of magnitude. Doping is a control knob with an enormous range.",
                "The **law of mass action** holds in any doped semiconductor in equilibrium: $np = n_i^2$, whatever the doping. Raising one carrier population suppresses the other in exact proportion.",
                "So in n-type material with $N_d$ donors, $n \\approx N_d$ and $p \\approx n_i^2/N_d$. Electrons are the **majority** carriers and holes the **minority** carriers; in p-type it is the other way round.",
                "Join p to n and the concentration gradient drives **diffusion**: holes cross into the n-side, electrons into the p-side. Each departure leaves behind a fixed, charged dopant ion.",
                "Those exposed ions build an electric field that opposes further diffusion. Equilibrium is reached when the **drift** current the field produces exactly cancels the diffusion current — not when the currents are zero, but when they are equal and opposite.",
                "The region stripped of mobile carriers is the **depletion region**, and the voltage across it is the **built-in potential** $V_{bi} = V_T \\ln(N_a N_d / n_i^2)$, typically 0.6 to 0.9 V in silicon.",
                "The **thermal voltage** $V_T = kT/q$ is 25.85 mV at 300 K. It is not a fitted constant; it is the thermal energy per carrier expressed in volts, and it sets the scale of every exponential in this course.",
                "You cannot measure $V_{bi}$ with a voltmeter. The contact potentials at the two probe junctions cancel it exactly — if they did not, a diode in a drawer would be a battery, and thermodynamics forbids that.",
            ],
            "read": [
                {
                    "title": "Two cubes of silicon, and the volt that appears where they meet",
                    "minutes": 15,
                    "body": r'''
Two cubes of silicon, a centimetre on a side, sitting on a bench. An ohmmeter across the
first one reads 341 k$\Omega$. The same meter across the second reads 0.46 $\Omega$.

Both are silicon. Neither has been heated, strained or damaged. The difference is that
somebody replaced one atom in five million of the second cube with phosphorus, and that
one change moved its resistance by a factor of seven hundred thousand. Almost nothing else
in engineering has a control knob with that range on it, and this course exists because
the knob can be turned in one part of a crystal and left alone in the part beside it.

## Why the first cube conducts so badly

Silicon has about $5\times10^{28}$ atoms per cubic metre, each sharing its four outer
electrons with its neighbours. An electron sitting in a bond carries no current. The
lattice is vibrating, though, and now and then a vibration is violent enough to break one
bond. That leaves two mobile things behind: the freed **electron**, and the vacancy where
it used to be, which the surrounding bonds pass along like an empty seat down a row. The
vacancy moves, carries current, and behaves in every measurement like a positive carrier.
It is called a **hole**.

Bonds break in pairs, so pure silicon holds exactly as many holes as electrons, and the
count at 300 K is $n_i = 1.0\times10^{16}$ m$^{-3}$. Set that against $5\times10^{28}$
atoms and it is one mobile carrier per five million million atoms. A material with one
charge carrier per $5\times10^{12}$ atoms is barely a conductor, and 341 k$\Omega$ across
a centimetre cube is what that looks like on a meter.

## Doping, and the two things it does not do

Replace one silicon atom with phosphorus, which brings five outer electrons instead of
four. Four of them go into the bonds the silicon atom would have made. The fifth has
nothing to bond to, is held to its parent only weakly, and at room temperature has long
since wandered off into the crystal. One phosphorus atom, one extra mobile electron, and
no hole to go with it. That is **n-type** silicon, and phosphorus is a **donor**. Boron
has three outer electrons and does the mirror image: it leaves one bond short, which is a
hole, and makes **p-type** silicon from an **acceptor**.

Two things did not happen, and the picture goes wrong early if they are assumed.

The material did not become charged. The phosphorus atom that gave up its electron is now
a fixed positive ion in the lattice, and the electron it gave up is still inside the same
piece of silicon. Add up the charge in any lump of n-type material big enough to see and
it comes to zero. The name says which carrier is mobile in quantity; it says nothing about
net charge.

And the dopants did not move. They are substituted into the crystal at the temperature of
a furnace and they stay exactly where they were put for the life of the device. Everything
from here on is carriers moving through a fixed background of charged, immobile ions.

## Raising one carrier population suppresses the other

There is a second effect of doping that is less obvious than the first and matters more.

Carriers are being generated all the time, by the same bond-breaking as before. The rate
depends on the temperature and on how many bonds there are to break, and doping changes
neither: call it $G(T)$. Carriers also disappear all the time, and disappearing needs an
electron to *meet* a hole, so the recombination rate is proportional to the product of the
two populations, $r\,np$. In equilibrium the two rates are equal:

$$G(T) = r\,np \qquad\Longrightarrow\qquad np = \frac{G(T)}{r} = \text{a constant at a given temperature}$$

Pure silicon is one solution of that equation with $n = p = n_i$, which fixes the constant.
So in any silicon at equilibrium, doped or not,

$$np = n_i^2$$

This is the **law of mass action**, and it says that the two populations are on a seesaw.
Push electrons up by a factor of a million and holes go down by a factor of a million,
because every extra electron makes it that much more likely that a hole meets one and
vanishes.

```python
n_i = 1.0e16
for n_d in (1e21, 1e22, 1e23):
    p = n_i * n_i / n_d
    print("N_d = %6.0e   n = %6.0e   p = %6.0e   n/p = %5.0e"
          % (n_d, n_d, p, n_d / p))
```

```text
N_d =  1e+21   n =  1e+21   p =  1e+11   n/p = 1e+10
N_d =  1e+22   n =  1e+22   p =  1e+10   n/p = 1e+12
N_d =  1e+23   n =  1e+23   p =  1e+09   n/p = 1e+14
```

Electrons are now the **majority** carriers and holes the **minority** carriers, and in
p-type material it is the other way round. The minority population looks negligible and is
not: module 2's reverse saturation current is carried entirely by minority carriers, and
module 5 computes it from the numbers in that last column.

## What happens where p meets n

Now the arrangement the whole course is about. One crystal, p-type on the left, n-type on
the right, with the doping switching over a few atomic spacings. Nothing is connected to
it.

The hole concentration on the left is $10^{23}$ m$^{-3}$ and on the right it is
$10^{9}$ m$^{-3}$ — fourteen orders of magnitude down over a few nanometres. A gradient
like that drives **diffusion**, the same way a drop of ink spreads through still water:
no force is needed, only the fact that random motion moves more carriers out of a crowded
region than into it. Holes cross into the n-side, electrons cross into the p-side.

Each departure exposes something. A hole leaving the p-side strands the acceptor ion that
supplied it, which is negative and fixed. An electron leaving the n-side strands a donor
ion, which is positive and fixed. So a layer of negative charge builds on the p-side of
the boundary and a layer of positive charge on the n-side, and between them is an electric
field pointing from n to p — which pushes holes back towards the p-side and electrons back
towards the n-side, against the diffusion that created it.

That field grows until it stops the net flow. The stripped layer is the **depletion
region**, and the voltage across it is the **built-in potential** $V_{bi}$.

Note carefully what equilibrium means here, because it is the point the quiz below leans
on. Diffusion has not stopped. Drift has not stopped. Both are large, and they are equal
and opposite, so the *net* current is exactly zero. A junction with a genuine net current
in it and nothing connected would be delivering power from nowhere.

## How big is the voltage

Setting the two currents equal is the derivation, and this module's derivation unit, **The
built-in potential, from mass action and Boltzmann**, walks it in four steps. The short
version: a population of carriers in equilibrium across a potential difference is thinner
on the high-potential side by the Boltzmann factor $e^{-V/V_T}$, where $V_T = kT/q$ is the
thermal energy per carrier expressed in volts. Holes are $10^{14}$ times thinner on the
n-side, so

$$e^{V_{bi}/V_T} = \frac{p_p}{p_n} = \frac{N_aN_d}{n_i^2}
\qquad\Longrightarrow\qquad V_{bi} = V_T\ln\!\left(\frac{N_aN_d}{n_i^2}\right)$$

That exponential arrived from thermal statistics, not from anything about the junction —
which is worth holding on to, because the same factor comes back in module 2 as the
exponential of the diode equation.

## A junction, in numbers

$10^{23}$ m$^{-3}$ either side, at 300 K. This is the first two functions of the lab,
**The junction, from the doping upwards**:

```python
import math

K = 1.380649e-23                        # J/K
Q = 1.602176634e-19                     # C
EPS_SI = 11.7 * 8.8541878128e-12        # F/m

n_i = 1.0e16                            # intrinsic carriers, m^-3
n_a = n_d = 1.0e23                      # acceptors and donors, m^-3

v_t = K * 300.0 / Q
v_bi = v_t * math.log(n_a * n_d / (n_i * n_i))
w = math.sqrt(2.0 * EPS_SI * v_bi / Q * (1.0 / n_a + 1.0 / n_d))

print("V_T   = %.3f mV" % (1000.0 * v_t))
print("V_bi  = %.4f V" % v_bi)
print("W     = %.1f nm" % (1e9 * w))
print("E_max = %.1f MV/m" % (2.0 * v_bi / w / 1e6))
```

```text
V_T   = 25.852 mV
V_bi  = 0.8334 V
W     = 146.8 nm
E_max = 11.4 MV/m
```

Two of those numbers deserve a second look. The depletion region is 147 nm wide — about
five hundred atoms — so the entire device is happening in a layer far thinner than the
silicon it sits in. And the field inside it is 11 MV/m with nothing connected, roughly a
third of the field at which silicon breaks down. A junction is a violent place at rest.

The logarithm is also why doping is a crude lever on $V_{bi}$. Multiplying both dopings by
ten multiplies the argument by a hundred and adds only $V_T\ln 100 = 119$ mV, so the whole
usable range of doping fits inside a ladder of equal steps: 0.595 V at $10^{21}$ m$^{-3}$,
0.714 V at $10^{22}$, 0.833 V at $10^{23}$, 0.952 V at $10^{24}$.

## Pulling it apart

Apply $V_R$ volts in reverse — n-side positive — and the applied voltage adds to the
built-in one rather than opposing it. The junction now supports $V_{bi}+V_R$, and to hold
more voltage it has to expose more ionised dopant, so the depletion region widens. Because
the charge exposed grows with the width and the voltage grows with the charge times the
width again, the width goes as the square root of the voltage:

```python
import math

Q = 1.602176634e-19
EPS_SI = 11.7 * 8.8541878128e-12
V_BI = 0.833370010652644


def width(n_a, n_d, v):
    return math.sqrt(2.0 * EPS_SI * v / Q * (1.0 / n_a + 1.0 / n_d))


w0 = width(1e23, 1e23, V_BI)
for v_r in (0.0, 1.0, 5.0, 20.0):
    w = width(1e23, 1e23, V_BI + v_r)
    print("V_R = %4.1f V   junction holds %6.3f V   W = %6.1f nm   W/W0 = %.3f"
          % (v_r, V_BI + v_r, 1e9 * w, w / w0))
```

```text
V_R =  0.0 V   junction holds  0.833 V   W =  146.8 nm   W/W0 = 1.000
V_R =  1.0 V   junction holds  1.833 V   W =  217.8 nm   W/W0 = 1.483
V_R =  5.0 V   junction holds  5.833 V   W =  388.4 nm   W/W0 = 2.646
V_R = 20.0 V   junction holds 20.833 V   W =  734.0 nm   W/W0 = 5.000
```

Five volts of reverse bias multiplies the width by 2.646, not by 6, and the reason the
first volt is worth so much more than the fifteenth is that $V_{bi}$ is already in the sum
before you apply anything. Forward bias does the opposite: it subtracts, the region
narrows, the barrier drops, and carriers start crossing in quantity. That is module 2.

Two more consequences run through the rest of the course. A widening slab of insulator
between two conductors is a capacitor whose value you can steer with a voltage, which is
module 7. And the two dopings enter as $1/N_a + 1/N_d$, so the *lightly* doped side
dominates the sum — which is why real diodes are made with one side doped far more heavily
than the other, and why almost all the depletion region sits on the light side.

## The mistake people actually make

Reaching for a voltmeter. The built-in potential is real, it is 0.83 V, and it is doing
all the work in the device — so it is natural to expect it across the terminals. It reads
zero, every time.

The reason is the contacts. To reach a diode you have to put metal on silicon at each end,
and each of those is itself a junction with its own contact potential. Go all the way
round the loop — meter, wire, metal-to-p, p-to-n, n-to-metal, wire, meter — and the
potentials cancel to the last millivolt. They have to. A diode reading 0.83 V into a meter
would drive current round that loop forever, and thermodynamics does not allow a device
that delivers power at one uniform temperature.

The general lesson is worth more than the special case: an internal potential is not a
terminal voltage. What you can measure at the pins is what is left after every junction in
the loop has had its say.

The other common slip is quieter — reading "n-type" as "negatively charged". It leads
directly to expecting an electric field around a doped wafer, or expecting two doped
regions to attract each other. Both pieces are neutral. What is not neutral is the thin
layer either side of the boundary once diffusion has moved some carriers across, and that
layer is the entire device.

## Where this stops holding

The mass-action law assumes the carrier populations are dilute enough to ignore each
other, and above about $10^{25}$ m$^{-3}$ they are not: the material becomes **degenerate**
and both $np = n_i^2$ and the Boltzmann factor stop being right. The formula gives fair
warning of its own limit. At $N_a = N_d = 2.6\times10^{25}$ m$^{-3}$ it returns
$V_{bi} = 1.12$ V, which is silicon's band gap in volts — and a built-in potential larger
than the band gap is not a thing that exists.

The abrupt junction — doping that switches from $N_a$ to $N_d$ at a plane — is a
convenience. Real profiles are graded over a distance, diffused or implanted, and the
grading changes how the width and the capacitance depend on voltage. Module 7 makes that
exponent a design parameter rather than a fixed $1/2$.

The depletion approximation says the region is swept perfectly clean and the neutral
regions are perfectly undisturbed, with a sharp boundary between them. The truth is a
transition a few nanometres deep at each edge, which matters for a 147 nm region rather
less than the arithmetic above suggests it might, and matters a great deal in a modern
transistor whose whole channel is that size.

And every number here is at 300 K. $n_i$ is not a constant of silicon but a steep function
of temperature, and it sits squared in the denominator of the logarithm, so $V_{bi}$ falls
as the junction warms. Module 6 does that properly, and the same effect is why a diode's
forward drop falls by about 2 mV per kelvin.
''',
                },
            ],
            "quiz": {
                "title": "Doping, mass action and the junction",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Silicon is doped with $10^{22}$ m$^{-3}$ donors. Taking $n_i = 1.0\\times10^{16}$ m$^{-3}$, what is the equilibrium hole concentration?",
                        "opts": [
                            "$10^{22}$ m$^{-3}$",
                            "$10^{16}$ m$^{-3}$",
                            "$10^{10}$ m$^{-3}$",
                            "zero — there are no holes in n-type material",
                        ],
                        "a": 2,
                        "why": r'''
Mass action: $np = n_i^2$, so $p = n_i^2/n = (10^{16})^2/10^{22} = 10^{10}$ m$^{-3}$.
The tempting answer is "zero — there are no holes in n-type material". n-type
material still has holes; it has a million
times *fewer* than pure silicon, not none. Those surviving minority carriers are what
carries the reverse saturation current of a diode, so a number that looks negligible
here turns out to be the whole of $I_S$ in module 2.
''',
                    },
                    {
                        "q": "What actually happens at the moment two doped regions are joined, before equilibrium is reached?",
                        "opts": [
                            "carriers diffuse across the junction, leaving behind charged dopant ions that build an opposing field",
                            "the two materials exchange dopant atoms until the doping is uniform",
                            "an external voltage must be applied before anything moves",
                            "nothing moves, because both pieces of silicon are electrically neutral",
                        ],
                        "a": 0,
                        "why": r'''
Both pieces are neutral, but neutrality is not equilibrium: the concentration gradient
is enormous, and carriers diffuse down it. Each hole that leaves the p-side strands a
negatively charged acceptor ion, and each electron that leaves the n-side strands a
positive donor ion. Those fixed ions are the depletion region, and the field between
them grows until it stops any further net flow. Dopant atoms themselves never move —
they are substituted into the crystal lattice and stay where they were put.
''',
                    },
                    {
                        "q": "In equilibrium, with nothing connected, what is the net current across a pn junction?",
                        "opts": [
                            "the diffusion current, flowing p to n",
                            "the drift current, flowing n to p",
                            "a small leakage current set by $I_S$",
                            "exactly zero, because drift and diffusion cancel",
                        ],
                        "a": 3,
                        "why": r'''
Exactly zero — but not because nothing is happening. Both a diffusion current and a
drift current flow, and they are equal and opposite. That is the substance of
equilibrium here, and it is what makes the algebra work: setting the two expressions
equal is precisely how the built-in potential is derived, which you will do in the
derivation below. A junction with a genuine net current in it would be dissipating
power with no source, which is impossible.
''',
                    },
                    {
                        "q": "A junction has $V_{bi} = 0.83$ V. You connect a voltmeter across the diode's two terminals. What does it read?",
                        "opts": [
                            "0.83 V",
                            "0 V",
                            "0.415 V, half the built-in potential",
                            "0.83 V, but only while the diode is warm",
                        ],
                        "a": 1,
                        "why": r'''
Zero. The built-in potential is real and it is essential to how the device works, but
it is not available at the terminals: the metal-to-silicon contacts at each end
develop their own contact potentials, and going all the way round the loop they cancel
$V_{bi}$ exactly. They must — a diode that read 0.83 V on a meter would deliver
current into the meter forever, which is a perpetual motion machine. The lesson is
general: an internal potential is not the same thing as a terminal voltage.
''',
                    },
                    {
                        "q": "Both sides of a junction are doped ten times more heavily. What happens to the built-in potential?",
                        "opts": [
                            "it is multiplied by ten",
                            "it is multiplied by a hundred",
                            "it increases by about 119 mV",
                            "it is unchanged, because the ratio of the two dopings is the same",
                        ],
                        "a": 2,
                        "why": r'''
$V_{bi} = V_T\ln(N_aN_d/n_i^2)$, and the logarithm turns the factor of 100 in the
product into an addition: $V_T\ln(100) = 0.02585 \times 4.605 = 0.119$ V. Doping is a
crude lever on $V_{bi}$ — a hundredfold change in the doping product buys about a
tenth of a volt. Answering "unchanged, because the ratio is the same" confuses this with the divider
rule from EE101: the built-in potential depends on the *product* of the two dopings, not their ratio.
''',
                    },
                    {
                        "q": "You apply 5 V of reverse bias to a junction whose built-in potential is 0.83 V. What happens to the depletion region?",
                        "opts": [
                            "it widens, because the total junction voltage rises from 0.83 V to 5.83 V",
                            "it narrows, because the applied field opposes the built-in field",
                            "it is unaffected — the depletion width depends only on the doping",
                            "it collapses, and the diode conducts",
                        ],
                        "a": 0,
                        "why": r'''
Reverse bias adds to the built-in potential rather than opposing it, so the junction
now supports 5.83 V and must expose more ionised dopant to do it. The width goes as
$\sqrt{V}$, so 5.83/0.83 is a factor of seven in voltage and $\sqrt{7} = 2.65$ in
width — you compute exactly this in the lab below. "It narrows, because the applied field opposes the built-in field" describes
*forward* bias, which does narrow the region and is why forward current flows at all. A widening
depletion region also means less capacitance, which is the whole basis of the varactor
diode used to tune radios.
''',
                    },
                ],
            },
            "derive": {
                "title": "The built-in potential, from mass action and Boltzmann",
                "minutes": 14,
                "vars": ["V_T", "N_a", "N_d", "n_i", "k", "T", "q", "p_p", "p_n", "V_bi"],
                "brief": r'''
The formula $V_{bi} = V_T\ln(N_aN_d/n_i^2)$ looks like something to memorise. It is
four short steps from two facts you already have.

The first fact is **mass action**: in equilibrium, $np = n_i^2$ everywhere, whatever
the local doping. The second is the **Boltzmann relation**: when a population of
carriers sits in equilibrium across a potential difference, the concentration on the
high-potential side is smaller by the factor $e^{-V/V_T}$. Holes are repelled by the
positive n-side, so there are fewer of them there.

Write $p_p$ for the hole concentration on the p-side and $p_n$ for the hole
concentration on the n-side.
''',
                "steps": [
                    {
                        "prompt": "The p-side is doped with $N_a$ acceptors per cubic metre, and at room temperature essentially every one of them has accepted an electron and left a hole. Write the equilibrium hole concentration $p_p$ in terms of the doping.",
                        "answer": "N_a",
                        "hint": "Holes are the majority carriers on the p-side, and each acceptor contributes exactly one.",
                        "deconstruct": [
                            "Each ionised acceptor leaves behind one mobile hole.",
                            "There are $N_a$ acceptors per cubic metre, so there are $N_a$ holes per cubic metre.",
                        ],
                    },
                    {
                        "prompt": "On the n-side the electron concentration is $N_d$. Use mass action, $np = n_i^2$, to write the hole concentration $p_n$ there in terms of $N_d$ and $n_i$.",
                        "given": "Mass action holds in equilibrium at every point: $np = n_i^2$.",
                        "answer": "\\frac{n_i^2}{N_d}",
                        "hint": "Put $n = N_d$ into $np = n_i^2$ and solve for $p$.",
                        "deconstruct": [
                            "Electrons are the majority carriers on the n-side, so $n = N_d$.",
                            "Then $N_d\\,p_n = n_i^2$, and dividing gives $p_n$.",
                        ],
                    },
                    {
                        "prompt": "The Boltzmann relation for holes across the junction is $p_n = p_p\\,e^{-V_{bi}/V_T}$. Rearrange it to give the ratio $p_p/p_n$.",
                        "given": "$p_n = p_p\\,e^{-V_{bi}/V_T}$",
                        "answer": "exp(\\frac{V_bi}{V_T})",
                        "placeholder": "exp(V_bi/V_T)",
                        "hint": "Divide both sides by $p_n$ and by the exponential; a negative exponent inverts when it moves across.",
                        "deconstruct": [
                            "Divide both sides by $p_p$: $p_n/p_p = e^{-V_{bi}/V_T}$.",
                            "Take the reciprocal of both sides, and $e^{-x}$ becomes $e^{+x}$.",
                        ],
                    },
                    {
                        "prompt": "Now substitute the two concentrations from steps 1 and 2 into that ratio. What does $p_p/p_n$ equal, in terms of $N_a$, $N_d$ and $n_i$?",
                        "answer": "\\frac{N_a N_d}{n_i^2}",
                        "hint": "Dividing by a fraction multiplies by its reciprocal: $N_a \\div (n_i^2/N_d)$.",
                        "deconstruct": [
                            "$p_p = N_a$ and $p_n = n_i^2/N_d$.",
                            "So $p_p/p_n = N_a \\times N_d/n_i^2$.",
                        ],
                    },
                    {
                        "prompt": "One loose end. The thermal voltage is not a fitted constant — write $V_T$ in terms of Boltzmann's constant $k$, the absolute temperature $T$ and the electronic charge $q$.",
                        "answer": "\\frac{k T}{q}",
                        "hint": "$kT$ is an energy in joules; dividing an energy by a charge gives a voltage.",
                        "deconstruct": [
                            "$kT$ is the characteristic thermal energy per particle, in joules.",
                            "A volt is a joule per coulomb, so divide by the charge $q$ on one carrier.",
                        ],
                    },
                ],
                "closing": r'''
Taking the natural logarithm of step 4 finishes it:

$$V_{bi} = V_T \ln\!\left(\frac{N_aN_d}{n_i^2}\right)$$

Two things are worth keeping. First, the exponential arrived from Boltzmann, not from
the junction — it is a statement about carriers in a potential, and the same factor
will reappear in module 2 as the exponential of the diode equation. The device is not
exponential because of anything clever in its construction; it is exponential because
that is what a thermal population does in a field.

Second, the logarithm is why device engineers get so little for so much. With
$N_a = N_d = 10^{23}$ m$^{-3}$ and $n_i = 1.0\times10^{16}$ m$^{-3}$ at 300 K, the
argument is $10^{14}$ and $V_{bi} = 0.833$ V. Dropping both dopings to
$10^{21}$ m$^{-3}$ — a factor of a hundred each — gives only 0.595 V.
''',
            },
            "lab": {
                "title": "The junction, from the doping upwards",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Three functions that turn the physics of this module into numbers.

- `thermal_voltage(kelvin)` returns $V_T = kT/q$ in volts.
- `built_in_potential(n_a, n_d, n_i, kelvin)` returns
  $V_{bi} = V_T\ln(N_aN_d/n_i^2)$ in volts.
- `depletion_width(n_a, n_d, v_junction)` returns the total width of the depletion
  region in metres, from the standard abrupt-junction result

```text
W = sqrt( 2 * eps * v_junction / q * (1/n_a + 1/n_d) )
```

where `v_junction` is the *total* voltage the junction is supporting. With nothing
connected that is $V_{bi}$; under $V_R$ volts of reverse bias it is $V_{bi} + V_R$.

The constants `K_BOLTZMANN`, `Q_ELECTRON` and `EPS_SILICON` are defined for you.
Everything is in SI units throughout: metres, not centimetres, and cubic metres, not
cubic centimetres. Most textbooks use cm$^{-3}$, so a concentration you look up
elsewhere will need multiplying by $10^6$ before it comes in here.
''',
                "files": [{"name": "main.py", "content": r'''
"""The pn junction in equilibrium, computed from the doping."""

import math

K_BOLTZMANN = 1.380649e-23              # J/K
Q_ELECTRON = 1.602176634e-19            # C
EPS_SILICON = 11.7 * 8.8541878128e-12   # F/m, the permittivity of silicon


def thermal_voltage(kelvin):
    """Thermal voltage kT/q, in volts."""
    # TODO: one multiplication and one division.
    return 0.0


def built_in_potential(n_a, n_d, n_i, kelvin):
    """Built-in potential of an abrupt pn junction, in volts."""
    # TODO: V_T times the natural log of (n_a * n_d) / n_i squared.
    return 0.0


def depletion_width(n_a, n_d, v_junction):
    """Total depletion width in metres for a junction supporting v_junction volts."""
    # TODO: the square root given in the brief.
    return 0.0


if __name__ == "__main__":
    vt = thermal_voltage(300.0)
    print("thermal voltage at 300 K:", vt, "V")
    vbi = built_in_potential(1e23, 1e23, 1e16, 300.0)
    print("built-in potential:", vbi, "V")
    print("depletion width, unbiased:", depletion_width(1e23, 1e23, vbi), "m")
    print("depletion width, 5 V reverse:", depletion_width(1e23, 1e23, vbi + 5.0), "m")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The pn junction in equilibrium, computed from the doping."""

import math

K_BOLTZMANN = 1.380649e-23              # J/K
Q_ELECTRON = 1.602176634e-19            # C
EPS_SILICON = 11.7 * 8.8541878128e-12   # F/m, the permittivity of silicon


def thermal_voltage(kelvin):
    """Thermal voltage kT/q, in volts."""
    return K_BOLTZMANN * kelvin / Q_ELECTRON


def built_in_potential(n_a, n_d, n_i, kelvin):
    """Built-in potential of an abrupt pn junction, in volts."""
    return thermal_voltage(kelvin) * math.log(n_a * n_d / (n_i * n_i))


def depletion_width(n_a, n_d, v_junction):
    """Total depletion width in metres for a junction supporting v_junction volts."""
    return math.sqrt(2.0 * EPS_SILICON * v_junction / Q_ELECTRON
                     * (1.0 / n_a + 1.0 / n_d))


if __name__ == "__main__":
    vt = thermal_voltage(300.0)
    print("thermal voltage at 300 K:", vt, "V")
    vbi = built_in_potential(1e23, 1e23, 1e16, 300.0)
    print("built-in potential:", vbi, "V")
    print("depletion width, unbiased:", depletion_width(1e23, 1e23, vbi), "m")
    print("depletion width, 5 V reverse:", depletion_width(1e23, 1e23, vbi + 5.0), "m")
'''}],
                "hints": [
                    "`thermal_voltage` is `K_BOLTZMANN * kelvin / Q_ELECTRON`. At 300 K it must come out near 0.0259 V; if you get 4.14e-21 you have forgotten to divide by the charge and are still holding an energy.",
                    "`built_in_potential` should call `thermal_voltage` rather than repeat it. `math.log` in Python is the natural logarithm — `math.log10` is the base-ten one, and using it here gives an answer 2.3 times too small.",
                    "In `depletion_width`, keep the whole expression inside one `math.sqrt`. The result is of order $10^{-7}$ m, which is a tenth of a micrometre — if you get something near 1, the reciprocals of the dopings have gone in the wrong way up.",
                    "The two dopings enter as $1/N_a + 1/N_d$, so the *lightly* doped side dominates the sum and therefore the width. That is why real diodes are made with one side doped far more heavily than the other.",
                ],
                "tests": [
                    {"name": "the thermal voltage is 25.85 mV at 300 K", "code": r'''
vt = thermal_voltage(300.0)
assert abs(vt - 0.025851999786435535) < 1e-12, \
    f"kT/q at 300 K is 0.0258520 V, got {vt}"
'''},
                    {"name": "it scales with absolute temperature", "code": r'''
cold = thermal_voltage(233.15)
hot = thermal_voltage(400.0)
assert abs(cold - 0.020091312500691485) < 1e-12, f"at -40 C expected 0.0200913 V, got {cold}"
assert abs(hot - 0.034469333048580714) < 1e-12, f"at 400 K expected 0.0344693 V, got {hot}"
assert abs(hot / cold - 400.0 / 233.15) < 1e-9, \
    "V_T is proportional to absolute temperature, so the ratio must be the ratio of the kelvins"
'''},
                    {"name": "the built-in potential of a symmetric junction", "code": r'''
v = built_in_potential(1e23, 1e23, 1e16, 300.0)
assert abs(v - 0.833370010652644) < 1e-9, \
    f"1e23 either side with n_i = 1e16 at 300 K gives 0.833370 V, got {v}"
'''},
                    {"name": "only the product of the dopings matters, and lighter doping means less", "code": r'''
a = built_in_potential(2e23, 5e21, 1e16, 300.0)
assert abs(a - 0.7738435813203123) < 1e-9, f"expected 0.7738436 V, got {a}"
light = built_in_potential(1e21, 1e21, 1e16, 300.0)
assert abs(light - 0.5952642933233172) < 1e-9, f"expected 0.5952643 V, got {light}"
same = built_in_potential(5e23, 2e22, 1e16, 300.0)
assert abs(same - built_in_potential(1e23, 1e23, 1e16, 300.0)) < 1e-12, \
    "1e23*1e23 and 5e23*2e22 are the same product, so the two must agree exactly"
'''},
                    {"name": "the depletion region is a fraction of a micrometre", "code": r'''
vbi = built_in_potential(1e23, 1e23, 1e16, 300.0)
w = depletion_width(1e23, 1e23, vbi)
assert abs(w - 1.4681182204947003e-07) < 1e-15, \
    f"expected 1.4681e-07 m (0.147 um), got {w}"
'''},
                    {"name": "reverse bias widens it as the square root of the voltage", "code": r'''
vbi = built_in_potential(1e23, 1e23, 1e16, 300.0)
w0 = depletion_width(1e23, 1e23, vbi)
w5 = depletion_width(1e23, 1e23, vbi + 5.0)
assert abs(w5 - 3.8842024415833636e-07) < 1e-15, f"expected 3.8842e-07 m, got {w5}"
ratio = w5 / w0
assert abs(ratio - ((vbi + 5.0) / vbi) ** 0.5) < 1e-9, \
    f"the width must go as sqrt(V), so the ratio should be sqrt(5.833/0.833) = 2.6457, got {ratio}"
'''},
                    {"name": "the lightly doped side sets the width", "code": r'''
va = built_in_potential(2e23, 5e21, 1e16, 300.0)
wa = depletion_width(2e23, 5e21, va)
assert abs(wa - 4.5292951227117876e-07) < 1e-15, f"expected 4.5293e-07 m, got {wa}"
assert wa > depletion_width(1e23, 1e23, va), \
    "the asymmetric junction is wider at the same voltage, because 1/N is dominated by the light side"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "The diode equation, the load line and dynamic resistance",
            "summary": "One exponential, and the two quite different resistances it implies at any given operating point.",
            "concepts": [
                "Forward bias lowers the barrier the diffusing carriers must climb, and the Boltzmann factor turns that into the **Shockley equation** $I = I_S\\left(e^{V/nV_T} - 1\\right)$.",
                "$I_S$ is the **reverse saturation current**, set by the minority carrier populations — typically $10^{-15}$ to $10^{-12}$ A for a small-signal silicon diode. $n$ is the **ideality factor**, between 1 and 2, and is 1 for an ideal junction.",
                "In reverse bias the exponential vanishes and $I \\to -I_S$: a current that does not depend on the applied voltage at all, which is what *saturation* means here.",
                "Forward, beyond about $4V_T \\approx 100$ mV, the $-1$ is negligible and $I \\approx I_S e^{V/nV_T}$. Inverting it gives $V = nV_T\\ln(I/I_S)$.",
                "That logarithm is the origin of the **60 mV per decade** rule: every tenfold increase in current costs $nV_T\\ln 10 = 59.5$ mV at 300 K, for $n = 1$. Ten times the current, one more small step in voltage.",
                "So there is no such thing as *the* forward drop. The familiar 0.7 V is simply where a small-signal silicon diode happens to sit at a few milliamps, and it moves by 60 mV for every decade you move away.",
                "A diode in series with a resistor and a supply cannot be solved by algebra: $I$ appears inside an exponential and outside it. The **load line** solves it graphically — plot $I = (V_S - V)/R$ on the diode's own curve, and the operating point is where they cross.",
                "Numerically, the same intersection is found by bisection or by Newton's method in a few iterations. Every circuit simulator does exactly this at every node, at every time step.",
                "**Static resistance** $V/I$ and **dynamic resistance** $r_d = dV/dI = nV_T/I$ are different numbers for a diode, and they answer different questions. At 10 mA a 1N4148 has a static resistance of about 70 Ω and a dynamic resistance of 2.59 Ω.",
                "Static resistance answers 'how much current at this voltage'. Dynamic resistance answers 'how much does the voltage move if the current wobbles'. Confusing them is the most expensive mistake in this course.",
                "The **piecewise-linear model** replaces the diode by a fixed voltage $V_{D0}$ in series with $r_d$ — the tangent to the exponential at the chosen operating point. It is exact at that point and useful for a decade either side.",
                "How far either side is a number rather than a feeling, and the second build measures it against the device. Two decades below the tangent point the real drop has fallen by $nV_T\\ln 100 = 119$ mV; the tangent says 26 mV and the static resistance says 689 mV. A model you have never taken outside its range is a model whose range you do not know.",
            ],
            "read": [
                {
                    "title": "Where 0.7 volts comes from, and why it is not 0.7 volts",
                    "minutes": 13,
                    "body": r'''
Put a diode, a resistor and a 5 V supply in series and measure across the diode. The
meter says 0.70 V. Change the resistor from 430 $\Omega$ to 100 $\Omega$ — more than
four times the current — and measure again. It says 0.73 V. Change it to 43 k$\Omega$,
a hundredth of the original current, and it says 0.58 V.

Three measurements, three answers, and the spread is 150 mV across a current range of
more than four hundred to one. That is the entire behaviour of a diode in one paragraph:
the voltage is *nearly* constant, and the small amount by which it is not is the most
useful thing about the device.

## Where the exponential comes from

Module 1 left the junction in equilibrium, with a built-in potential $V_{bi}$ holding
back a diffusion current that exactly cancels the drift current. Nothing flows, because
the two flows are equal and opposite.

Now put $V$ across the junction, forward. The applied voltage subtracts from the barrier,
so carriers now face a hill of height $q(V_{bi} - V)$ instead of $qV_{bi}$. The
population of carriers with enough thermal energy to climb a hill of height $E$ is
proportional to $e^{-E/kT}$ — that is Boltzmann's result, and it is the only physics
this course borrows. So the diffusion current, which was in balance, is multiplied by

$$\frac{e^{-q(V_{bi}-V)/kT}}{e^{-qV_{bi}/kT}} = e^{qV/kT} = e^{V/V_T}$$

The drift current is unchanged: it depends on how many minority carriers wander into the
depletion region and get swept across, and that number is set by the doping, not by the
barrier. Call that unchanged current $I_S$. The net current is what diffusion now
delivers minus what drift takes back:

$$I = I_S e^{V/V_T} - I_S = I_S\left(e^{V/V_T} - 1\right)$$

The $-1$ is not a correction bolted on. It is the drift current that was there all along,
and it is why the equation gets reverse bias right for free: make $V$ negative by a few
$V_T$ and the exponential collapses, leaving $I = -I_S$, a current that does not care how
hard you pull. That is what *saturation* means.

The ideality factor $n$, which turns $V_T$ into $nV_T$, is the one fitted quantity. It
absorbs recombination inside the depletion region, which the derivation above ignores. It
is 1 for an ideal junction and up to 2 when that recombination dominates.

## Inverting it, and the 60 mV that follows

Beyond about $4V_T \approx 100$ mV the $-1$ is a part in fifty and can go:

$$I \approx I_S e^{V/nV_T} \qquad\Longleftrightarrow\qquad V = nV_T\ln\frac{I}{I_S}$$

Now ask what a *factor of ten* in current costs in volts. Logarithms turn the ratio into
a difference:

$$V_2 - V_1 = nV_T\ln\frac{I_2}{I_1} = nV_T\ln 10 = 1 \times 0.025852 \times 2.302585
= 0.059526\ \text{V}$$

Sixty millivolts per decade, and notice what dropped out: $I_S$ cancelled. The slope is
the same for every silicon diode ever made, cheap or expensive, big or small. What $I_S$
sets is *where* the curve sits, not how steeply it rises.

That single number explains the three measurements at the top. Take the small-signal
diode this module's lab uses, $I_S = 2.0\times10^{-14}$ A with $n = 1$ at 300 K:

```text
current      V = V_T ln(I/I_S)       relative to 10 mA
   100 uA          0.5773 V              -2 decades, -119 mV
     1 mA          0.6369 V              -1 decade,   -60 mV
    10 mA          0.6964 V               reference
   100 mA          0.7559 V              +1 decade,   +60 mV
      1 A          0.8154 V              +2 decades, +119 mV
```

Four decades of current — a factor of ten thousand — fit inside 240 mV. *That* is why
"0.7 V" works as a rule of thumb, and it is also exactly why it is not a constant. A
resistor asked to carry ten thousand times the current would need ten thousand times the
voltage.

## Two resistances, and the ratio between them

At 10 mA the diode has 0.6964 V across it, so $V/I = 69.6\ \Omega$. Wire a 69.6 $\Omega$
resistor in its place and the DC voltmeter cannot tell the difference. That number is the
**static resistance**, and it answers exactly one question: how much current flows at this
voltage.

Ask a different question — the load wobbles by 1 mA, how far does the voltage move? —
and differentiate instead:

$$r_d = \frac{dV}{dI} = \frac{d}{dI}\left(nV_T\ln\frac{I}{I_S}\right) = \frac{nV_T}{I}$$

$I_S$ cancels again. At 10 mA, $r_d = 0.025852/0.010 = 2.585\ \Omega$: twenty-seven times
smaller than the static resistance. A 1 mA wobble moves the diode by 2.6 mV, not by 70 mV.

The factor of twenty-seven is not a coincidence, and it is worth deriving because it is
the whole reason the next two modules work:

$$\frac{R_{static}}{r_d} = \frac{V/I}{nV_T/I} = \frac{V}{nV_T} = \ln\frac{I}{I_S}$$

The two resistances differ by the logarithm itself — $0.6964/0.025852 = 26.9$ here. Any
device sitting many thermal voltages up an exponential has this property, and no resistor
has it at all, because for a resistor $V = IR$ makes both definitions give $R$. When
module 4 asks why a Zener regulates and a resistor cannot, this ratio is the answer.

## Worked example: solving a circuit the algebra will not solve

5 V, 430 $\Omega$, the diode above. Kirchhoff gives

$$5 = 430\,I + V_T\ln\frac{I}{I_S}$$

and there is no rearranging that isolates $I$: it sits both multiplied by 430 and inside
a logarithm. So iterate. Guess a diode voltage, ask the *resistor* what current that
implies, then ask the *diode* what voltage that current implies, and go round again:

```text
V0 = 0.7000 V     ->  I0 = (5 - 0.7000)/430   = 10.0000 mA
                  ->  V1 = V_T ln(I0/I_S)     =  0.696398 V
V1 = 0.696398 V   ->  I1 = (5 - 0.696398)/430 = 10.008377 mA
                  ->  V2 = V_T ln(I1/I_S)     =  0.696420 V
V2 = 0.696420 V   ->  I2 = (5 - 0.696420)/430 = 10.008327 mA
                  ->  V3 = 0.696420 V         (unchanged to six figures)
```

Two passes. It converges that fast because of the ratio just derived: an error in the
current is divided by 27 on its way to becoming an error in the voltage, so each pass
kills most of what the last one left. The lab, **Solving the diode equation, both ways
round**, does it without needing a good first guess at all: 200 halvings of the interval
between 0 V and the supply, returning 0.6964194 V and 10.008327 mA — the same answer.

Check the honesty of the 0.7 V assumption against it. Assuming 0.7 V flat gives 10.000 mA
against a true 10.008 mA: an error of 0.08%, invisible. Now do the same at 43 k$\Omega$,
where the true current is near 100 $\mu$A: assuming 0.7 V predicts $(5-0.7)/43000 =
100.0\ \mu$A, while the diode actually sits at 0.578 V and passes 102.8 $\mu$A — nearly
3% out, and all of the error in the diode's drop rather than the resistor's. The rule of
thumb degrades exactly where the logarithm says it should.

## The tangent, and why a linear solver can now cope

Take the tangent to the curve at 10 mA. It passes through (0.6964 V, 10 mA) with slope
$1/r_d$, so extended back to zero current it meets the voltage axis at

$$V_{D0} = 0.6964 - 0.010 \times 2.585 = 0.6705\ \text{V}$$

A 0.6705 V source in series with 2.585 $\Omega$. That is the **piecewise-linear model**,
and it is the object you build in the schematic editor next. It is not an approximation
to the diode everywhere — it is the diode's behaviour *at one operating point*, extended
by a straight line. At 10 mA it is exact in both value and slope. At 1 mA the real diode
sits at 0.6369 V and the model says $0.6705 + 0.001\times2.585 = 0.6731$ V, 36 mV high.
At 100 mA the model says 0.929 V against a true 0.756 V.

## The mistake people actually make

Quoting one resistance for the diode. It is tempting because every component in the first
year had one, and because at the operating point the static resistance is not wrong — it
reproduces the DC voltage and the DC current perfectly. The first build, **A diode a
linear solver can swallow**, is constructed entirely around this: a single 69.6 $\Omega$
resistor passes its first three checks, and is caught only by how fast a capacitor
charges through it, because
charging depends on the *incremental* resistance and that is 2.585 $\Omega$, not
69.6 $\Omega$. Twenty-seven times wrong, in a measurement no voltmeter would show you.

The second mistake is subtler and follows from the first: reading "0.7 V" as a property
of silicon rather than as a reading taken at an unstated current. It is a property of
silicon *at a few milliamps*. Quote the current with it and it becomes a real number;
quote it alone and it is a superstition that happens to work over three decades.

## Where this stops holding

- **At high current the exponential is not what limits you.** Past a few hundred
  milliamps the bulk resistance of the neutral silicon and the bond wires — a few tens of
  milliohms — starts to dominate, and the curve straightens out. The equation above says
  1 A costs 0.815 V; a real 1 A diode measures nearer 1.0 V, and the extra is $IR$ in
  ordinary resistive material, not junction physics.
- **At very low current the ideality factor drifts towards 2.** Recombination inside the
  depletion region has a different voltage dependence from diffusion, and below a
  microamp or so it takes over. A single $n$ fitted at 10 mA will not extrapolate down
  six decades.
- **Every number here is at 300 K.** $V_T$ is proportional to absolute temperature and
  $I_S$ roughly quadruples every 10 K, and the second effect wins: at a fixed current the
  forward voltage *falls* by about 2 mV per kelvin. Module 6 does that properly, and it
  is the reason a diode characterised on a cold bench misbehaves in a warm enclosure.
- **The $-1$ matters again in reverse.** Everything after the inversion assumed forward
  bias beyond $4V_T$. Below that — and in the whole reverse region — you need the full
  Shockley form, which is why the lab keeps the $+1$ and the $-1$ in its two functions
  even though they are invisible at 10 mA.
''',
                },
            ],
            "quiz": {
                "title": "The exponential, and the two resistances",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A silicon diode drops 0.65 V at 1 mA, with $n = 1$ at 300 K. Roughly what does it drop at 10 mA?",
                        "opts": ["0.65 V", "0.71 V", "1.30 V", "6.5 V"],
                        "a": 1,
                        "why": r'''
About 0.71 V. A decade of current costs $V_T\ln 10 = 59.5$ mV, so 0.65 + 0.06 = 0.71 V.
The answer 1.30 V treats the diode as ohmic — ten times the current for ten times the
voltage — which is exactly what a diode does not do. That is the whole point: a
tenfold change in current barely moves the voltage, which is what makes a diode useful
as a reference and useless as a resistor.
''',
                    },
                    {
                        "q": "In the reverse direction, an ideal diode's current is:",
                        "opts": [
                            "proportional to the reverse voltage",
                            "proportional to the square root of the reverse voltage",
                            "exponential in the reverse voltage",
                            "essentially $-I_S$, independent of the reverse voltage",
                        ],
                        "a": 3,
                        "why": r'''
With $V$ negative and larger than a few $V_T$, $e^{V/nV_T}$ is negligible and the
equation collapses to $I = -I_S$. The current saturates: doubling the reverse voltage
does not double it. Physically, $I_S$ is set by how fast minority carriers are
generated near the junction, and once the field is strong enough to sweep every one of
them across, making it stronger changes nothing. (Real diodes show some extra
surface leakage that does creep up with voltage, and eventually break down entirely —
which module 4 turns into a feature.)
''',
                    },
                    {
                        "q": "A 5 V supply drives a 430 Ω resistor in series with a diode. Which method finds the operating point?",
                        "opts": [
                            "draw $I = (5 - V)/430$ on the diode's I–V curve and read off where the two cross",
                            "divide 5 V by 430 Ω",
                            "solve $5 = IR + nV_T\\ln(I/I_S)$ algebraically for $I$",
                            "assume the diode drops 0.7 V, since it always does",
                        ],
                        "a": 0,
                        "why": r'''
The load line. Solving $5 = IR + nV_T\ln(I/I_S)$ for $I$ is the right equation but it
has no closed-form solution —
$I$ appears both linearly and inside a logarithm, so it needs a numerical method
(which is what the lab below writes). Dividing 5 V by 430 Ω forgets the diode entirely. Assuming a flat 0.7 V is a first
estimate, not an answer: it gives 10.0 mA where the true value is 10.008 mA
here, which is close, but the same assumption at 100 µA or 1 A is out by a long way.
''',
                    },
                    {
                        "q": "At 10 mA a diode drops 0.696 V. Its static resistance is 69.6 Ω. What is its dynamic resistance at that current, with $n = 1$ at 300 K?",
                        "opts": ["69.6 Ω", "34.8 Ω", "2.59 Ω", "0 Ω — an ideal diode has none"],
                        "a": 2,
                        "why": r'''
$r_d = nV_T/I = 0.025852/0.01 = 2.59$ Ω, twenty-seven times smaller than the static
resistance. Both numbers are correct and neither is *the* resistance of the diode: the
static value tells you the DC drop, the dynamic value tells you how much that drop
moves when the current changes. A 1 mA wobble on top of the 10 mA moves the diode
voltage by 2.6 mV, not by 70 mV. Answering 69.6 Ω here is the error that makes people
expect a shunt regulator to be far worse than it is.
''',
                    },
                    {
                        "q": "Two identical diodes are connected in parallel and the pair is fed 20 mA in total. Compared with one diode carrying 20 mA, the forward drop of the pair is:",
                        "opts": [
                            "twice as large",
                            "half as large",
                            "the same",
                            "smaller by about 18 mV",
                        ],
                        "a": 3,
                        "why": r'''
Each diode carries 10 mA rather than 20 mA, which is half the current — and half is
$\log_{10}2 = 0.301$ of a decade, so the drop falls by $0.301 \times 59.5 = 17.9$ mV.
Answering "the same" ignores the split; answering "half" applies the resistor rule to
a device that does not obey it. In practice diodes are rarely paralleled precisely
because of this exponential: a 20 mV mismatch between two supposedly identical parts
sends twice the current down one of them.
''',
                    },
                    {
                        "q": "You replace a diode with its piecewise-linear model, $V_{D0}$ in series with $r_d$, taken as the tangent at 10 mA. Where is the model exact?",
                        "opts": [
                            "everywhere, since the model is linear",
                            "at 10 mA and nowhere else, though it stays useful for a decade either side",
                            "only in reverse bias",
                            "only above 100 mA",
                        ],
                        "a": 1,
                        "why": r'''
A tangent touches the curve at one point. At 10 mA the model reproduces both the
voltage and the slope exactly; move far from there and the straight line and the
exponential diverge, since one of them curves and the other does not. Between about
1 mA and 100 mA the error stays small enough to design with, and that is what makes
the model worth having: it turns a circuit no linear solver can touch into one it
solves instantly. You build exactly this model in the schematic editor next.
''',
                    },
                ],
            },
            "build": [{
                "title": "A diode a linear solver can swallow",
                "minutes": 28,
                "brief": r'''
A piecewise-linear equivalent is how a diode enters a calculation you intend to finish
by hand: replace the curve by the straight line tangent to it at the current you expect,
and the algebra stops needing an iteration. That is the exercise. You are going to build
the equivalent and measure two things that prove it is doing the diode's job rather than
a resistor's.

The editor will also solve the diode itself — it carries a Newton-Raphson loop for
exactly that, and the next exercise uses it. Building the model first is not a way round
a limitation of the tool. It is what every data sheet, every hand calculation and every
estimate in this subject actually does, and knowing where it stops being true is worth
more than knowing the equation.

## The device

A small-signal silicon diode with $I_S = 2.0\times10^{-14}$ A and $n = 1$, at 300 K
where $V_T = 25.852$ mV. At 10 mA it drops

$$V_D = nV_T\ln\!\left(1 + \frac{I}{I_S}\right) = 0.6964\ \text{V},
\qquad r_d = \frac{nV_T}{I} = 2.585\ \Omega$$

The tangent to the curve at that point passes through $V_D$ at 10 mA with slope
$r_d$, so it meets the voltage axis at $V_{D0} = 0.6964 - 0.010\times2.585 = 0.6705$ V.
The model is therefore a **0.6705 V source in series with 2.585 Ω**.

## What to build

The canvas gives you a 5 V supply, a 100 µF capacitor from the output node to ground,
and a probe on that node. Nothing works yet, because that node has no DC path anywhere.
Add:

- a series resistor from the 5 V rail to the output node, sized so that **10 mA** flows,
- the diode model — the 0.6705 V source and the 2.585 Ω resistor in series — from the
  output node down to ground, with the source's **+ terminal facing the output**.

Leave the capacitor alone; it is there for the last check.

## The trap, and why the last check exists

At the operating point the diode's static resistance is $0.6964/0.010 = 69.6\ \Omega$.
A single 69.6 Ω resistor in place of the whole model gives the *same* DC voltage and
the *same* DC current, and it passes the first three checks. It is wrong, and the
capacitor is what catches it. The capacitor charges through whatever incremental
resistance it sees, which for the real model is $r_d$ in parallel with your series
resistor — about 2.57 Ω, a time constant of 0.26 ms. For the 69.6 Ω impostor it is
about 60 Ω, a time constant of 6 ms, twenty-three times slower.

A diode is not a resistor, and this is the measurement that says so.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p6", "kind": "C", "x": 17, "y": 9, "rot": 1, "value": 100e-6},
                        {"id": "p7", "kind": "GND", "x": 17, "y": 11},
                        {"id": "p8", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [11, 8], "b": [17, 8]},
                        {"a": [17, 10], "b": [17, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 430},
                        {"id": "p3", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 2.5852},
                        {"id": "p4", "kind": "V", "x": 13, "y": 11, "rot": 1, "value": 0.6705},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 13},
                        {"id": "p6", "kind": "C", "x": 17, "y": 9, "rot": 1, "value": 100e-6},
                        {"id": "p7", "kind": "GND", "x": 17, "y": 11},
                        {"id": "p8", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [17, 8]},
                        {"a": [13, 12], "b": [13, 13]},
                        {"a": [17, 10], "b": [17, 11]},
                    ],
                },
                "checks": [
                    {"name": "the 5 V supply delivers 10 mA", "code": r'''
const sources = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const supply = sources.filter(function (p) { return Math.abs(p.value - 5) < 0.5; });
c.assert(supply.length === 1,
  'Exactly one 5 V supply, so that "the supply current" means one thing. Found ' +
  supply.length + ' source(s) near 5 V.');
const i = Math.abs(c.dc().currents[supply[0].id]);
c.close(i, 0.010, 0.03,
  'the current out of the 5 V supply — size the series resistor from (5 - 0.6964)/0.010');
'''},
                    {"name": "the diode model sits at 0.696 V", "code": r'''
c.close(c.vout(), 0.6964, 0.015,
  'the voltage at the probed node. At 10 mA this diode drops 0.6964 V, so that is what ' +
  'the top of the model must sit at; check the offset source is the right way up');
'''},
                    {"name": "the power splits 43 mW in the resistor, 7 mW in the diode", "code": r'''
const sources = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 5) < 0.5; });
const i = Math.abs(c.dc().currents[sources[0].id]);
const v = c.vout();
c.close(v * i, 0.006969, 0.06, 'the power in the diode branch (its voltage times the current)');
c.close((5 - v) * i, 0.04307, 0.06, 'the power in the series resistor');
'''},
                    {"name": "the capacitor charges with a 0.26 ms time constant, not 6 ms", "code": r'''
const s = c.step(1.0e-3);
const settled = s.v[s.v.length - 1];
const target = c.vout();
c.assert(target > 0.05, 'The probed node should settle near 0.7 V; it is at ' + c.fmt(target, 'V') + '.');
const frac = settled / target;
c.assert(frac > 0.90,
  'After 1 ms the node has only reached ' + (100 * frac).toFixed(1) + '% of its final value. ' +
  'With the real diode model the incremental resistance is about 2.6 ohms and 1 ms is nearly ' +
  'four time constants, so it should be past 97%. A single resistor of the diode\'s static ' +
  'resistance gives the same DC answer but charges twenty-three times more slowly, which is ' +
  'what this check is looking for.');
'''},
                ],
                "hints": [
                    "The series resistor carries the same 10 mA and drops the rest of the supply: $(5 - 0.6964)/0.010 = 430.4\\ \\Omega$. Type `430` — the checks allow 3% on the current.",
                    "Build the model as a chain: output node, down through the 2.585 Ω resistor, then down through the 0.6705 V source, then to ground. Order does not matter electrically, but the polarity does.",
                    "For a vertical source the **+ terminal is the top pin**. The offset battery must push the output node upwards, so its + must face the output, not ground.",
                    "Type small values plainly: `2.585` for the resistor and `0.6705` for the source. The editor also understands `430` and `100u`.",
                    "If the last check fails but the first three pass, you have almost certainly used one resistor for the whole diode. Look at what the capacitor is charging through.",
                ],
            }, {
                "title": "The diode itself, and the decade it lives in",
                "minutes": 24,
                "brief": r'''
The last exercise replaced the diode by a straight line. This one puts the diode back,
because the editor solves it directly: a non-linear part is stamped as the tangent to
its own curve at a guess, the circuit is solved, and the answer becomes the next guess.
That loop is Newton-Raphson, and it converges in a handful of passes. Nothing on this
canvas stands in for anything.

## What to build

Two independent branches off the same **5 V** rail, each a resistor in series with a
**real diode** down to ground. Both diodes are already placed, with
$I_S = 2.0\times10^{-14}$ A and $n = 1$ — the same device module 2 has been about. Both
are missing their series resistor, so nothing is conducting yet.

Size the two resistors so that

- the left branch carries **0.1 mA**, and
- the right branch carries **10 mA**,

which is two decades apart. Then read the forward drop of each.

## What you are measuring

Because $V_D = nV_T\ln(1 + I/I_S)$, a **ratio** of currents becomes a **difference** of
voltages:

$$V_2 - V_1 = nV_T\ln\!\left(\frac{I_2}{I_1}\right) = 0.025852 \times \ln 100
= 119.05\,\text{mV}$$

That is this module's 60 mV per decade, spent twice. The last check asks for it to
within 8%.

## Why this is not the last exercise again

The three descriptions of this diode barely disagree at 10 mA, which is why the previous
exercise needed a capacitor to tell them apart at all. Ask the same question two decades
down and they separate immediately:

```text
                       0.1 mA       10 mA      change
  the real device      0.5773 V    0.6964 V    119.05 mV
  the tangent model    0.6708 V    0.6964 V     25.59 mV
  a 69.64 ohm resistor 0.0070 V    0.6964 V    689.44 mV
```

The tangent is exact where it was taken and understates the change by a factor of 4.7
two decades away. The static resistance is out by 5.8 the other way. Neither is wrong as
such — a tangent is a local statement and nothing promised otherwise — but a model whose
error you have never measured is a model whose range you do not know, and this is the
measurement.

## The trap

It is tempting to size the quiet branch as $5/0.0001 = 50\,\text{k}\Omega$, ignoring the
drop. That gives 88 µA, 12% low, and the check refuses it. At 0.1 mA the diode still
keeps 0.577 V, which is 11.5% of the supply: the drop matters most as a *fraction*
exactly where it is smallest in volts.
''',
                "start": {"parts": [
                    {"id": "p0", "kind": "V",   "x": 3,  "y": 6,  "rot": 1, "value": 5},
                    {"id": "p1", "kind": "GND", "x": 3,  "y": 9},
                    {"id": "p2", "kind": "D",   "x": 9,  "y": 10, "rot": 1, "value": 2e-14, "n": 1},
                    {"id": "p3", "kind": "GND", "x": 9,  "y": 12},
                    {"id": "p4", "kind": "D",   "x": 15, "y": 10, "rot": 1, "value": 2e-14, "n": 1},
                    {"id": "p5", "kind": "GND", "x": 15, "y": 12},
                    {"id": "p6", "kind": "OUT", "x": 9,  "y": 9},
                ], "wires": [
                    {"a": [3, 7],   "b": [3, 9]},
                    {"a": [9, 11],  "b": [9, 12]},
                    {"a": [15, 11], "b": [15, 12]},
                ]},
                "solution": {"parts": [
                    {"id": "p0", "kind": "V",   "x": 3,  "y": 6,  "rot": 1, "value": 5},
                    {"id": "p1", "kind": "GND", "x": 3,  "y": 9},
                    {"id": "p7", "kind": "R",   "x": 9,  "y": 6,  "rot": 1, "value": 44200},
                    {"id": "p2", "kind": "D",   "x": 9,  "y": 10, "rot": 1, "value": 2e-14, "n": 1},
                    {"id": "p3", "kind": "GND", "x": 9,  "y": 12},
                    {"id": "p8", "kind": "R",   "x": 15, "y": 6,  "rot": 1, "value": 430},
                    {"id": "p4", "kind": "D",   "x": 15, "y": 10, "rot": 1, "value": 2e-14, "n": 1},
                    {"id": "p5", "kind": "GND", "x": 15, "y": 12},
                    {"id": "p6", "kind": "OUT", "x": 9,  "y": 9},
                ], "wires": [
                    {"a": [3, 7],   "b": [3, 9]},
                    {"a": [3, 5],   "b": [9, 5]},
                    {"a": [9, 5],   "b": [15, 5]},
                    {"a": [9, 7],   "b": [9, 9]},
                    {"a": [15, 7],  "b": [15, 9]},
                    {"a": [9, 11],  "b": [9, 12]},
                    {"a": [15, 11], "b": [15, 12]},
                ]},
                "checks": [
                    {"name": "two real diodes, and nothing standing in for them", "code": r'''
c.assert(c.count('D') === 2,
  'This exercise wants two actual diodes on the canvas; found ' + c.count('D') + '. A ' +
  'voltage source and a resistor in series is the model you built last time, and the ' +
  'whole point here is to measure the thing that model was standing in for.');
c.assert(c.count('V') === 1,
  'Exactly one voltage source, the 5 V rail; found ' + c.count('V') + '. A second source ' +
  'is a piecewise-linear model creeping back in.');
'''},
                    {"name": "the quiet branch settles at 0.1 mA", "code": r'''
const ds = c.net.placed.filter(function (p) { return p.kind === 'D'; });
c.assert(ds.length === 2, 'Two diodes have to be on the canvas before the currents mean anything.');
const i = ds.map(function (p) { return Math.abs(c.device(p.id).i[0]); })
            .sort(function (a, b) { return a - b; });
c.close(i[0], 1e-4, 0.06,
  'The lower of the two diode currents. Remember that the diode keeps 0.577 V of the ' +
  '5 V for itself even here');
'''},
                    {"name": "the loud branch settles at 10 mA, two decades up", "code": r'''
const ds = c.net.placed.filter(function (p) { return p.kind === 'D'; });
c.assert(ds.length === 2, 'Two diodes have to be on the canvas before the currents mean anything.');
const i = ds.map(function (p) { return Math.abs(c.device(p.id).i[0]); })
            .sort(function (a, b) { return a - b; });
c.close(i[1], 1e-2, 0.06, 'The upper of the two diode currents');
const ratio = i[1] / i[0];
c.assert(ratio > 50 && ratio < 200,
  'The two branches have to sit two decades apart; this pair is a factor of ' +
  ratio.toFixed(1) + '.');
'''},
                    {"name": "the forward drop moves by 119 mV, not by 26 and not by 689", "code": r'''
const ds = c.net.placed.filter(function (p) { return p.kind === 'D'; });
c.assert(ds.length === 2, 'Two diodes have to be on the canvas before the drops mean anything.');
const m = ds.map(function (p) {
  const d = c.device(p.id);
  return { i: Math.abs(d.i[0]), v: d.v[0] - d.v[1] };
}).sort(function (a, b) { return a.i - b.i; });
const dv = (m[1].v - m[0].v) * 1000;
c.close(dv, 119.05, 0.08,
  'The difference between the two forward drops, in mV. This is n*VT*ln(100), a ' +
  'property of the device rather than of the resistors you chose');
'''},
                ],
                "hints": [
                    "For the 10 mA branch the diode drops $0.025852\\ln(1 + 0.01/2\\times10^{-14}) = 0.6964$ V, so the resistor takes $5 - 0.6964 = 4.3036$ V and has to be $430.4\\,\\Omega$. Type `430`.",
                    "For the 0.1 mA branch the drop is $0.5773$ V, so the resistor takes $4.4227$ V and has to be $44.2\\,\\text{k}\\Omega$. Type `44.2k` — the editor reads engineering notation.",
                    "Both diodes point the same way: anode at the top, on the resistor's side, cathode to ground. A diode drawn upside down blocks, and its branch then sits at the full 5 V with no current in it.",
                    "The two branches share the rail and the ground and nothing else. If they share the node above the diodes as well, you have built module 10's mistake eight modules early.",
                    "If the last check fails while both current checks pass, look at whether both diodes really are diodes. A `D` and a `V`+`R` pair can be made to carry the same current, and cannot possibly show the same 119 mV.",
                ],
            }],
            "lab": {
                "title": "Solving the diode equation, both ways round",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
The Shockley equation, its inverse, its slope, and the numerical solve that a
simulator does for you.

- `diode_current(v, i_s, n, v_t)` returns $I_S\left(e^{V/nV_T} - 1\right)$.
- `diode_voltage(i, i_s, n, v_t)` returns $nV_T\ln(1 + I/I_S)$, the inverse.
- `dynamic_resistance(i, n, v_t)` returns $nV_T/I$.
- `operating_point(v_s, r_s, i_s, n, v_t)` returns the tuple `(v_d, i_d)` where the
  diode curve crosses the load line $I = (V_S - V)/R_S$.

For the last one, use **bisection**. The diode voltage is somewhere between 0 and
`v_s`. At the true answer the diode current equals the load-line current; below it the
diode wants less current than the resistor offers, above it more. So:

```text
lo, hi = 0.0, v_s
repeat 200 times:
    mid = (lo + hi) / 2
    if diode_current(mid) > (v_s - mid) / r_s:   hi = mid
    else:                                        lo = mid
```

200 halvings of a 5 V interval takes you far below floating-point resolution, so there
is no need to be clever about a stopping rule. Return `(v, (v_s - v) / r_s)`.

Keep the `+1` and the `-1` in the two exponential expressions. They cost nothing and
they keep the functions correct in reverse bias and at very small currents, where
dropping them gives a logarithm of zero.
''',
                "files": [{"name": "main.py", "content": r'''
"""The Shockley diode equation, forwards, backwards and solved on a load line."""

import math


def diode_current(v, i_s, n, v_t):
    """Shockley: the current through a diode with `v` volts across it."""
    # TODO: i_s * (exp(v / (n * v_t)) - 1).
    return 0.0


def diode_voltage(i, i_s, n, v_t):
    """The inverse: the voltage across a diode carrying `i` amps."""
    # TODO: n * v_t * log(1 + i / i_s).
    return 0.0


def dynamic_resistance(i, n, v_t):
    """Small-signal resistance dV/dI at a bias current of `i` amps."""
    # TODO: differentiate the line above, or just remember n*v_t/i.
    return 0.0


def operating_point(v_s, r_s, i_s, n, v_t):
    """Bisect for the (v_d, i_d) where the diode meets the load line."""
    lo, hi = 0.0, v_s
    # TODO: 200 halvings, then return (v, (v_s - v) / r_s).
    return (0.0, 0.0)


if __name__ == "__main__":
    vt = 0.025851999786435535
    i_s = 2.0e-14
    print("current at 0.7 V:", diode_current(0.7, i_s, 1.0, vt), "A")
    print("voltage at 10 mA:", diode_voltage(0.01, i_s, 1.0, vt), "V")
    print("a decade costs:",
          diode_voltage(0.01, i_s, 1.0, vt) - diode_voltage(0.001, i_s, 1.0, vt), "V")
    v, i = operating_point(5.0, 430.0, i_s, 1.0, vt)
    print("5 V through 430 ohms:", v, "V at", i, "A")
    print("static resistance:", v / i if i else 0.0,
          "dynamic resistance:", dynamic_resistance(i, 1.0, vt) if i else 0.0)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The Shockley diode equation, forwards, backwards and solved on a load line."""

import math


def diode_current(v, i_s, n, v_t):
    """Shockley: the current through a diode with `v` volts across it."""
    return i_s * (math.exp(v / (n * v_t)) - 1.0)


def diode_voltage(i, i_s, n, v_t):
    """The inverse: the voltage across a diode carrying `i` amps."""
    return n * v_t * math.log(1.0 + i / i_s)


def dynamic_resistance(i, n, v_t):
    """Small-signal resistance dV/dI at a bias current of `i` amps."""
    return n * v_t / i


def operating_point(v_s, r_s, i_s, n, v_t):
    """Bisect for the (v_d, i_d) where the diode meets the load line."""
    lo, hi = 0.0, v_s
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if diode_current(mid, i_s, n, v_t) > (v_s - mid) / r_s:
            hi = mid
        else:
            lo = mid
    v = 0.5 * (lo + hi)
    return (v, (v_s - v) / r_s)


if __name__ == "__main__":
    vt = 0.025851999786435535
    i_s = 2.0e-14
    print("current at 0.7 V:", diode_current(0.7, i_s, 1.0, vt), "A")
    print("voltage at 10 mA:", diode_voltage(0.01, i_s, 1.0, vt), "V")
    print("a decade costs:",
          diode_voltage(0.01, i_s, 1.0, vt) - diode_voltage(0.001, i_s, 1.0, vt), "V")
    v, i = operating_point(5.0, 430.0, i_s, 1.0, vt)
    print("5 V through 430 ohms:", v, "V at", i, "A")
    print("static resistance:", v / i if i else 0.0,
          "dynamic resistance:", dynamic_resistance(i, 1.0, vt) if i else 0.0)
'''}],
                "hints": [
                    "`math.exp` and `math.log` are the two you need. `math.log(x)` is the natural logarithm; there is no need to pass a base.",
                    "In `diode_voltage`, write `1.0 + i / i_s` rather than `i / i_s`. For forward currents the difference is invisible, but it keeps the function finite at $i = 0$.",
                    "`dynamic_resistance` is one division. If it looks too simple to be worth a function, notice that it is the derivative of `diode_voltage` — differentiating $nV_T\\ln(I/I_S)$ with respect to $I$ gives $nV_T/I$, and every $I_S$ cancels.",
                    "In `operating_point`, the loop body is exactly the four lines in the brief. Do the halving 200 times unconditionally; the interval shrinks by $2^{200}$, so nothing is left to converge.",
                    "If bisection returns `v_s` or 0, the comparison is the wrong way round. When the diode's current *exceeds* the load line's, the guess is too high, so bring `hi` down.",
                ],
                "tests": [
                    {"name": "the forward current at 0.7 V", "code": r'''
vt = 0.025851999786435535
i = diode_current(0.7, 2.0e-14, 1.0, vt)
assert abs(i - 0.011495091382073667) < 1e-12, f"expected 0.0114951 A, got {i}"
'''},
                    {"name": "reverse bias saturates at -I_S", "code": r'''
vt = 0.025851999786435535
i = diode_current(-0.5, 2.0e-14, 1.0, vt)
assert abs(i + 2.0e-14) < 1e-20, f"expected about -2e-14 A, got {i}"
j = diode_current(-5.0, 2.0e-14, 1.0, vt)
assert abs(j - i) < 1e-22, \
    f"ten times the reverse voltage must give the same current: {i} vs {j}"
assert abs(diode_current(0.0, 2.0e-14, 1.0, vt)) < 1e-24, "zero volts must give zero current"
'''},
                    {"name": "the inverse agrees with the forward equation", "code": r'''
vt = 0.025851999786435535
v = diode_voltage(0.01, 2.0e-14, 1.0, vt)
assert abs(v - 0.6963979112242282) < 1e-12, f"expected 0.6963979 V at 10 mA, got {v}"
back = diode_current(v, 2.0e-14, 1.0, vt)
assert abs(back - 0.01) < 1e-12, f"round-tripping 10 mA should give 10 mA, got {back}"
'''},
                    {"name": "a decade of current costs 59.5 mV", "code": r'''
vt = 0.025851999786435535
step = (diode_voltage(0.01, 2.0e-14, 1.0, vt)
        - diode_voltage(0.001, 2.0e-14, 1.0, vt))
assert abs(step - 0.05952642933186636) < 1e-9, f"expected 0.0595264 V per decade, got {step}"
big = (diode_voltage(0.1, 2.0e-14, 1.0, vt)
       - diode_voltage(0.01, 2.0e-14, 1.0, vt))
assert abs(big - step) < 1e-6, \
    f"every decade costs the same: {step} then {big}"
'''},
                    {"name": "static and dynamic resistance are twenty-seven times apart", "code": r'''
vt = 0.025851999786435535
rd = dynamic_resistance(0.01, 1.0, vt)
assert abs(rd - 2.5851999786435536) < 1e-12, f"expected 2.5852 ohms at 10 mA, got {rd}"
assert abs(dynamic_resistance(0.001, 1.0, vt) - 25.851999786435535) < 1e-9, \
    "a tenth of the current is ten times the dynamic resistance"
static = diode_voltage(0.01, 2.0e-14, 1.0, vt) / 0.01
assert abs(static / rd - 26.93) < 0.05, \
    f"the static resistance should be about 27 times the dynamic one, got {static / rd}"
'''},
                    {"name": "the load line, solved", "code": r'''
vt = 0.025851999786435535
v, i = operating_point(5.0, 430.0, 2.0e-14, 1.0, vt)
assert abs(v - 0.6964194289924417) < 1e-9, f"expected 0.6964194 V, got {v}"
assert abs(i - 0.010008326909319902) < 1e-12, f"expected 0.0100083 A, got {i}"
assert abs(diode_current(v, 2.0e-14, 1.0, vt) - i) < 1e-9, \
    "at the operating point the diode current and the load-line current must be the same number"
'''},
                    {"name": "it works on other supplies, and on a non-ideal diode", "code": r'''
vt = 0.025851999786435535
v, i = operating_point(12.0, 1000.0, 2.0e-14, 1.0, vt)
assert abs(v - 0.6995584914972504) < 1e-9, f"expected 0.6995585 V, got {v}"
assert abs(i - 0.01130044150850275) < 1e-12, f"expected 0.0113004 A, got {i}"
v2, i2 = operating_point(5.0, 100.0, 2.0e-14, 1.0, vt)
assert abs(v2 - 0.7339014004034561) < 1e-9, f"expected 0.7339014 V, got {v2}"
assert v2 > v, "more current means more volts, even though only a little more"
v3, i3 = operating_point(5.0, 430.0, 2.0e-14, 2.0, vt)
assert abs(v3 - 1.383840561056358) < 1e-9, \
    f"an ideality factor of 2 roughly doubles the drop; expected 1.3838406 V, got {v3}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Rectifiers, the reservoir capacitor and ripple",
            "summary": "The diode's one-way behaviour, put to work: mains in, a rough DC rail out, and an arithmetic of ripple.",
            "concepts": [
                "A **half-wave rectifier** is one diode in series with the load: it passes the positive half-cycles and blocks the negative ones. The output ripples at the mains frequency and is idle for half of every cycle.",
                "A **full-wave bridge** uses four diodes so that both half-cycles reach the load in the same direction. The ripple frequency is twice the mains frequency — 100 Hz from 50 Hz mains — and two diodes are in series with the load at all times, so the drop is $2V_D$, not $V_D$.",
                "The **peak inverse voltage** (PIV) is the largest reverse voltage a diode must withstand. For a bridge it is about $V_{peak}$; for a half-wave rectifier with a reservoir capacitor it is about $2V_{peak}$, because the capacitor holds the cathode up while the input swings negative.",
                "A **reservoir capacitor** across the output turns the rectified humps into a nearly steady voltage. It charges to the peak while the diodes conduct and discharges into the load while they do not.",
                "Between peaks the capacitor supplies the whole load current, and it can only do that by falling: $-C\\,dV/dt = I_{load}$, so $dV/dt$ is negative and its size is set by the load. Over one ripple period that gives the working approximation $V_{ripple} \\approx I_{load}/(f_{ripple}C)$.",
                "That formula assumes the capacitor discharges for the *whole* ripple period. It never does — the diodes conduct near each peak — so it always overestimates. How much depends on how wide that conduction window is: about five per cent when the ripple is a small fraction of the rail, ten to twenty per cent for an ordinary design, and more still when the ripple is large. It errs on the safe side either way, which is what makes it a usable design tool.",
                "Doubling the capacitance halves the ripple; doubling the load current doubles it; going from half-wave to full-wave halves it, because the gaps between peaks are half as long.",
                "The price of a large reservoir is a short, tall **peak repetitive current**. All the charge the load takes over a whole period must be replaced during the few degrees of conduction near each peak, so a 70 mA load can demand amps through the diodes.",
                "Real diodes do not stop conducting instantly when the current reverses. **Reverse recovery** sweeps the stored minority charge out, and the loop inductance and junction capacitance then ring at tens of megahertz — the source of most of a supply's radiated noise.",
                "A rectifier output is not a supply. It has ripple, it moves with the mains and with the load, and it needs either a filter, a regulator or both. Module 4 supplies the regulator.",
            ],
            "read": [
                {
                    "title": "Sizing a reservoir, and the ten per cent the formula gives back",
                    "minutes": 14,
                    "body": r'''
A transformer secondary labelled 12 V, a bridge, a capacitor, and a load that wants about
70 mA at something near 15 V. Four components, and every one of them is chosen by an
argument you can do on paper. This unit does that design from the label on the
transformer to the part number of the diode, and then checks it against the time-stepped
simulation you write in the lab, **Ripple, predicted and measured**.

## What the capacitor sees, before the capacitor is there

A bridge does one thing: it makes both half-cycles come out the same way up. With no
capacitor, the output is $|V_{peak}\sin\omega t|$ less the drops of the two diodes that
are conducting at that instant — a train of humps, touching zero twice per mains cycle.

Two consequences follow immediately, and both catch people out.

**The peak is not the label.** A transformer's rating is RMS. $12\ \text{V RMS}$ means
$12\sqrt{2} = 16.97$ V peak, and it is the peak the capacitor charges towards. Take off
two diode drops at roughly 0.7 V each and the rail sits near

$$V_{rail} = 16.97 - 1.4 = 15.6\ \text{V}$$

which is 30% above the number printed on the transformer. Designing a 12 V circuit around
a 12 V transformer and discovering 15.6 V is the classic first mistake in a linear supply,
and it is always in the direction that damages something.

**The humps arrive at twice the mains frequency.** 50 Hz in, 100 Hz out. That factor of
two is worth two extra diodes on its own, and the next section says why.

## Deriving the ripple, rather than quoting it

Add the reservoir. Near each peak the input is above the capacitor and the diodes
conduct, topping it up. Once the input falls away, the diodes go open and the capacitor is
alone with the load. The only equation for a capacitor is

$$I = C\frac{dV}{dt}$$

The load draws $I_{load}$ *out*, so $-C\,dV/dt = I_{load}$, giving a fall of
$dV/dt = -I_{load}/C$. If the load is roughly constant, that slope is constant, so the
voltage falls in a straight line, and over a time $t$ it falls by

$$\Delta V = \frac{I_{load}}{C}\,t$$

Now the assumption that makes this a design rule instead of a description: take $t$ to be
the whole ripple period $T_r = 1/f_r$. Then

$$\boxed{V_{ripple} \approx \frac{I_{load}}{f_r C}}$$

Every property in the concept list falls straight out of that fraction. Double $C$ and the
ripple halves. Double the load and it doubles. Go from half-wave to full-wave and $f_r$
doubles from 50 Hz to 100 Hz, so the ripple halves — the capacitor only has to coast for
10 ms instead of 20 ms.

## Worked example, all the way through

**Specification.** 12 V RMS at 50 Hz, full-wave bridge, load 220 $\Omega$, ripple no
worse than 0.7 V peak-to-peak.

**1. The rail.** $16.97 - 1.4 = 15.6$ V at the top of the ripple, as above.

**2. The load current.** The rail is not flat, so use its mean, which will land a little
below the peak — call it 15.3 V for now and check later. $I_{load} = 15.3/220 =
69.5\ \text{mA}$.

**3. The capacitor.** Rearranged, $C = I_{load}/(f_r V_{ripple})$:

$$C = \frac{0.0695}{100 \times 0.7} = 993\ \mu\text{F} \;\longrightarrow\; 1000\ \mu\text{F}$$

**4. What the formula now predicts.** $0.0695/(100 \times 1000\times10^{-6}) = 0.695$ V.

**5. What actually happens.** The lab steps this exact circuit forward in time and
measures the tail: peak 15.600 V, trough 14.968 V, so 0.632 V of ripple, with a mean of
15.291 V. The mean vindicates the guess in step 2 — 15.291/220 = 69.5 mA, which is what
was assumed.

So the formula said 0.695 V and the circuit delivered 0.632 V. It over-predicted by 9.9%.

## Where that ten per cent comes from

The concept list says the formula "always overestimates" and puts the error at about ten
per cent for an ordinary design. Here is the argument behind the number, because a design
rule you cannot bound is a design rule you cannot trust.

The formula charged the capacitor for discharging over the *whole* 10 ms. It does not.
It discharges only from the moment the falling input lets go of it to the moment the next
rising hump catches it up again. Find that instant: the capacitor is at 14.968 V, and the
input reaches that value when

$$17.0\,|\sin\theta| - 1.4 = 14.968 \quad\Longrightarrow\quad
|\sin\theta| = \frac{16.368}{17.0} = 0.9628 \quad\Longrightarrow\quad \theta = 74.4^\circ$$

The next peak is at $90^\circ$. So the diodes conduct for $90 - 74.4 = 15.6^\circ$ of the
mains cycle, which at 50 Hz is 0.87 ms, and the capacitor is on its own for the other
9.13 ms of the 10 ms period. Scaling the prediction by the time that actually elapsed:

$$0.695 \times \frac{9.13}{10} = 0.634\ \text{V}$$

against 0.632 V measured. The whole of the discrepancy was the conduction window, and the
last two millivolts are the discharge being very slightly curved rather than straight —
the load current falls as the rail falls, so the real slope eases off as it goes.

That is also the answer to "how big is the error in general". It is the fraction of the
period the diodes conduct, and that fraction grows as the ripple grows, because a deeper
trough is caught earlier on the rising edge. Small ripple, small error. It is always in
the safe direction: you get less ripple than you budgeted for.

## What the capacitor costs

All the charge the load takes over a full 10 ms has to be pushed back in during that
0.87 ms window. Charge does not care how it is delivered:

$$Q = I_{load}T_r = 0.0695 \times 0.010 = 695\ \mu\text{C}$$
$$\bar{I}_{diode,\,conducting} = \frac{695\times10^{-6}}{0.87\times10^{-3}} = 0.80\ \text{A}$$

Eleven and a half times the DC load current, on average, while conducting — and the
instantaneous peak is higher still, since the current is a spike rather than a
rectangle. A 70 mA supply is asking its diodes for the best part of an amp.

This is the part of the design that gets worse when you improve the ripple. Ask for
0.1 V instead of 0.7 V and you need seven times the capacitance; the trough rises to
15.5 V, the input catches it at $\theta = 83.8^\circ$, and the window narrows to 0.35 ms —
so the same 695 $\mu$C now goes in through a window two fifths as wide, and the conducting
current is over 2 A. Nothing in $I/(f_rC)$ warns you about this. It is the reason a
rectifier diode is specified by its surge rating as much as by its average one, and the
reason the quiz's example, with a comfortable 3 ms window, belongs to a design with
several volts of ripple rather than a fraction of one.

## Choosing the diodes

Three numbers, all now in hand:

- **Average forward current.** 69.5 mA through the load; each of the two diode pairs in a
  bridge carries it on alternate half-cycles, so about 35 mA each. Trivial for any part.
- **Peak repetitive current.** 0.8 A average during conduction, peaking higher. This is
  what actually sizes the diode.
- **Peak inverse voltage.** For a bridge, the non-conducting diodes are clamped by the
  conducting pair, so each sees about $V_{peak} = 17$ V. A 1N4001 at 50 V is enough with
  margin to spare; the ubiquitous 1N4007 at 1000 V costs the same and removes the
  question.

Note the asymmetry with the half-wave case. There, the capacitor holds the cathode at
$+V_{peak}$ while the transformer swings to $-V_{peak}$, and the diode sees the sum —
$2V_{peak}$, 34 V here. Sizing a half-wave rectifier's diode for $V_{peak}$ is a
destroyed part on the first switch-on.

## The mistake people actually make

Believing the rail. Everything above computes a *steady-state* number, and the moment the
supply is switched on there is no steady state: the capacitor is at 0 V, the diodes see
the full peak across a discharged capacitor, and the only thing limiting the current is
the transformer's own winding resistance and leakage inductance. That inrush is orders of
magnitude above the 0.8 A computed here, lasts a few cycles, and is why supplies of any
size have a thermistor or a resistor in series at switch-on.

The tempting error is arithmetic rather than conceptual: subtracting the diode drops from
the RMS voltage instead of the peak. It gives 10.6 V here rather than 15.6 V, it looks
like exactly the same calculation, and it is wrong by five volts.

## Where this stops holding

- **The rail is not a fixed voltage.** It rides on the mains, which is specified to
  something like $\pm10\%$, so a 15.6 V rail is really 14 V to 17.2 V before the ripple is
  added. Every number above moves with it. That range is the input specification for the
  regulator in module 4, and it is why that module designs for a corner rather than a
  value.
- **A real reservoir capacitor has resistance.** The ESR of an electrolytic — tens of
  milliohms — multiplies the 0.8 A charging spike into an extra tens of millivolts of
  ripple that this model does not contain, and dissipates real power inside the capacitor,
  which is the usual reason they fail.
- **The straight-line discharge is an approximation to an exponential.** With
  $R_LC = 0.22$ s against a 10 ms period, the exponential is straight to well within the
  accuracy of anything else here. Load the same capacitor to 1 k$\Omega$ and it stays
  straight; load it to 22 $\Omega$ and it does not, and the formula's error grows with it.
- **None of this is regulation.** The rail moves with the mains, with the load, and with
  temperature, and it still has hundreds of millivolts of 100 Hz on it. It is a raw
  supply, and it is the input to the next module, not an output.
''',
                },
            ],
            "sandbox": {
                "title": "What happens the instant a diode stops conducting",
                "visualiser": "switching",
                "minutes": 10,
                "initial": {"ls": 30, "coss": 150, "dead": 0},
                "brief": r'''
The arithmetic of ripple treats a diode as a switch that opens the moment the current
tries to reverse. It does not. The junction has capacitance, the wiring loop has
inductance, and between them they hold a resonant circuit that gets kicked hard every
time the device turns off.

This visualiser plots one such turn-off. The **upper trace** is the voltage across the
switching device, normalised so that 1 means the full off-state voltage and 0 means
fully conducting. The **lower, blue trace** is the current through it, also normalised
to 1. The horizontal axis is 600 nanoseconds. Both traces are flat for the first
100 ns; the transition happens there.

The three sliders are the loop inductance in nanohenries, the device capacitance in
picofarads, and a **dead time** in nanoseconds — a delay before the device is allowed
to take up current. Leave the dead time at zero for the first four readings; that is
the rectifier case, where nothing waits for anything.
''',
                "notice": [
                    "At the opening values — 30 nH and 150 pF — the voltage trace is amber and, at 100 ns, drops and then oscillates about zero, decaying to nothing by roughly 250 ns. The note beside the plot gives 75.0 MHz for that oscillation, which is $1/2\\pi\\sqrt{LC}$ with those two numbers, and one cycle of it is about 13 ns wide on the axis.",
                    "The blue current trace, over the same instant, goes straight from 0 to 1 with no slope at all and then stays there. Voltage and current are therefore both large at 100 ns, which is exactly the overlap that turns into heat in the device.",
                    "Drag the device capacitance from 150 pF to its maximum of 600 pF, leaving the inductance at 30 nH. The note now reads 37.5 MHz — exactly half, because four times the capacitance halves $1/\\sqrt{LC}$ — and the cycles on the plot visibly stretch to about 27 ns. Multiplying the capacitance did not remove the ringing; it only slowed it down.",
                    "Put the capacitance back to 150 pF and take the loop inductance from 30 nH to 80 nH. The frequency falls to 45.9 MHz and, more usefully, the oscillation now takes noticeably longer to die away. Loop inductance is the one term here you control with layout rather than with a part number.",
                    "Put the inductance back to 30 nH before this reading, or it will not work: the note then reads 3 ns for the swing, against 5 ns at 80 nH. Now push the dead time from 0 to 5 ns. Five nanoseconds covers a 3 ns swing, so the voltage trace changes colour, becomes a single smooth quarter-cosine from 1 down to 0 in those 3 ns, and stops ringing altogether, while the current trace stops jumping and ramps up over about 60 ns instead. The voltage is at zero long before the current is anywhere near 1, so the two barely overlap. That is what a switching converter buys with dead time — and what an ordinary mains rectifier, which has no controller to wait for anything, does not get.",
                    "Leave the dead time at 5 ns and drag the inductance back up to 80 nH. The trace reverts to amber and rings again. The note still rounds to 5 ns, but the swing at 80 nH is really 5.44 ns, and 5 ns of dead time does not cover it. Dead time is not a fixed number of nanoseconds; it has to be re-earned every time the layout changes.",
                ],
            },
            "quiz": {
                "title": "Rectifiers, ripple and what the capacitor costs",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A transformer secondary delivers 12 V RMS at 50 Hz into a bridge rectifier with a large reservoir capacitor. Roughly what DC voltage appears across the capacitor at light load?",
                        "opts": ["12 V", "10.6 V", "8.5 V", "15.6 V"],
                        "a": 3,
                        "why": r'''
The capacitor charges towards the **peak**, not the RMS value:
$12\sqrt{2} = 16.97$ V, less two diode drops for a bridge, giving about 15.6 V.
Answering 12 V is the single most common error in power supply design, and it is
always in the direction that surprises you — the rail is 30% higher than the label on
the transformer. Answering 10.6 V subtracts the drops from the RMS value instead of
from the peak.
''',
                    },
                    {
                        "q": "The same supply now draws 50 mA from a 1000 µF reservoir. Estimate the peak-to-peak ripple.",
                        "opts": ["1.0 V", "0.5 V", "0.05 V", "5.0 V"],
                        "a": 1,
                        "why": r'''
$V_{ripple} \approx I/(f_{ripple}C) = 0.05/(100 \times 1000\times10^{-6}) = 0.5$ V.
The trap is the 1.0 V answer, which uses $f = 50$ Hz. A **bridge** delivers a hump
every half cycle, so the ripple frequency is 100 Hz and the capacitor only has to
coast for 10 ms, not 20 ms. Half-wave would indeed give 1.0 V from the same capacitor,
which is the practical reason bridges are worth their two extra diodes.
''',
                    },
                    {
                        "q": "You are unhappy with 0.5 V of ripple and want 0.1 V. What do you do?",
                        "opts": [
                            "use diodes with a lower forward drop",
                            "double the reservoir capacitor to 2200 µF",
                            "multiply the reservoir capacitor by about five, to 4700 µF",
                            "raise the transformer voltage",
                        ],
                        "a": 2,
                        "why": r'''
Ripple is inversely proportional to capacitance, so a fivefold reduction in ripple
wants a fivefold increase in capacitance. The nearest standard value is 4700 µF, which
lands the ripple at $0.5/4.7 = 0.106$ V — near enough, and the honest way to design
with the E-series is to accept that last few per cent rather than chase it. Neither
the diode drop nor the transformer voltage
appears anywhere in $I/(f C)$ — they set where the rail *sits*, not how much it
*wiggles*. And note what the fivefold capacitor costs: the conduction angle narrows
and the peak repetitive current through the diodes goes up sharply.
''',
                    },
                    {
                        "q": "Why does the simple formula $V_{ripple} = I/(f_{ripple}C)$ always predict slightly more ripple than a simulation shows?",
                        "opts": [
                            "it assumes the capacitor discharges for the whole ripple period, when in fact the diodes conduct for part of it",
                            "it ignores the diode forward drops",
                            "it assumes the load is constant when in fact it varies",
                            "it uses the peak voltage where it should use the RMS value",
                        ],
                        "a": 0,
                        "why": r'''
The capacitor only coasts between the point where the input falls below it and the
point on the next hump where the input catches it up again — which is less than a full
ripple period. The formula assumes the whole period, so it always errs on the
pessimistic side — by about ten per cent for the design in the lab below, and by more
when the ripple is a larger fraction of the rail and the diodes therefore conduct for
longer. That is a good property for a design rule: you get slightly less ripple than
you budgeted for. The lab below measures both numbers and compares them.
''',
                    },
                    {
                        "q": "A supply draws 70 mA average from a bridge and reservoir, and the diodes conduct for about 3 ms out of each 10 ms ripple period. Roughly what average current flows through a diode pair while it conducts?",
                        "opts": ["70 mA", "230 mA", "23 mA", "700 mA"],
                        "a": 1,
                        "why": r'''
All the charge the load takes over the whole 10 ms has to be replaced in that 3 ms
window, so the conducting current is larger by roughly $10/3$:
$70 \times 3.33 \approx 230$ mA average during conduction, with an instantaneous peak
higher still. This is why rectifier diodes are rated for a surge current far above
their average rating, and why a big reservoir capacitor is not a free improvement —
it narrows the conduction window and pushes that peak higher.
''',
                    },
                    {
                        "q": "In a half-wave rectifier with a reservoir capacitor, what is the peak inverse voltage the diode must survive?",
                        "opts": [
                            "about $V_{peak}$",
                            "about $V_{peak}/2$",
                            "about $V_{peak}/\\sqrt{2}$",
                            "about $2V_{peak}$",
                        ],
                        "a": 3,
                        "why": r'''
About twice the peak. The capacitor holds the cathode near $+V_{peak}$ while the
transformer swings down to $-V_{peak}$, so the diode sees the sum across it. Sizing
it for $V_{peak}$ is the classic way to destroy a rectifier the first time it is
switched on with no load. A bridge does not have this problem: its non-conducting
diodes are clamped by the conducting pair, and the PIV is about $V_{peak}$.
''',
                    },
                ],
            },
            "lab": {
                "title": "Ripple, predicted and measured",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Two design formulas and one simulation, so you can see how far the formulas are from
the truth and in which direction.

- `reservoir_ripple(i_load, f_ripple, c)` returns the peak-to-peak ripple predicted by
  $I/(f_{ripple}C)$, in volts.
- `capacitor_for_ripple(i_load, f_ripple, v_ripple)` is the same relation solved for
  the capacitance you need, in farads.
- `simulate(v_peak, f_mains, c, r_load, v_drop_total, cycles, per_cycle)` steps a
  full-wave rectifier and reservoir forward in time and returns the output voltage at
  every sample, as a list.
- `measured_ripple(samples, per_cycle)` returns the peak-to-peak spread of the **last
  `per_cycle` samples** — one whole mains cycle, well after the start-up transient.

## The simulation model

Time step `dt = 1 / (f_mains * per_cycle)`; run for `cycles * per_cycle` samples,
starting from an output of 0 V. At sample `k`, with `t = k * dt`:

```text
v_rect = v_peak * abs(sin(2*pi*f_mains*t)) - v_drop_total
if v_rect > v:            # the diodes conduct and the capacitor follows the input
    v = v_rect
else:                     # they are off, and the load discharges the capacitor
    v -= (v / r_load) * dt / c
record v
```

The `abs` is the whole of the full-wave bridge: it folds the negative half-cycles up
into positive ones. `v_drop_total` is the sum of the drops of the diodes in series
with the load at any instant — 1.4 V for a bridge, 0.7 V for a half-wave rectifier.
The discharge line is $C\,dV = -I\,dt$ with $I = v/R$, applied one step at a time.

Use a plain loop. The model is sequential — each sample depends on the one before —
so vectorising it is not straightforward, and clarity is worth more here than speed.
''',
                "files": [{"name": "main.py", "content": r'''
"""Rectifier ripple: the design formula, and what actually happens."""

import math


def reservoir_ripple(i_load, f_ripple, c):
    """Peak-to-peak ripple in volts, from the standard I/(fC) estimate."""
    # TODO: one division.
    return 0.0


def capacitor_for_ripple(i_load, f_ripple, v_ripple):
    """Capacitance in farads needed to hold the ripple to v_ripple volts."""
    # TODO: the same relation, solved for C.
    return 0.0


def simulate(v_peak, f_mains, c, r_load, v_drop_total, cycles, per_cycle):
    """Step a full-wave rectifier and reservoir; return every output sample."""
    dt = 1.0 / (f_mains * per_cycle)
    v = 0.0
    out = []
    # TODO: the loop from the brief, appending v every step.
    return out


def measured_ripple(samples, per_cycle):
    """Peak-to-peak spread of the last per_cycle samples."""
    # TODO: slice the tail, then max minus min.
    return 0.0


if __name__ == "__main__":
    print("predicted ripple:", reservoir_ripple(0.05, 100.0, 1000e-6), "V")
    print("C for 0.5 V at 50 mA:", capacitor_for_ripple(0.05, 100.0, 0.5), "F")
    s = simulate(17.0, 50.0, 1000e-6, 220.0, 1.4, 10, 2000)
    if s:
        tail = s[-2000:]
        mean = sum(tail) / len(tail)
        print("mean output:", mean, "V")
        print("measured ripple:", measured_ripple(s, 2000), "V")
        print("formula would say:", reservoir_ripple(mean / 220.0, 100.0, 1000e-6), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Rectifier ripple: the design formula, and what actually happens."""

import math


def reservoir_ripple(i_load, f_ripple, c):
    """Peak-to-peak ripple in volts, from the standard I/(fC) estimate."""
    return i_load / (f_ripple * c)


def capacitor_for_ripple(i_load, f_ripple, v_ripple):
    """Capacitance in farads needed to hold the ripple to v_ripple volts."""
    return i_load / (f_ripple * v_ripple)


def simulate(v_peak, f_mains, c, r_load, v_drop_total, cycles, per_cycle):
    """Step a full-wave rectifier and reservoir; return every output sample."""
    dt = 1.0 / (f_mains * per_cycle)
    v = 0.0
    out = []
    for k in range(cycles * per_cycle):
        t = k * dt
        v_rect = v_peak * abs(math.sin(2.0 * math.pi * f_mains * t)) - v_drop_total
        if v_rect > v:
            v = v_rect
        else:
            v -= (v / r_load) * dt / c
        out.append(v)
    return out


def measured_ripple(samples, per_cycle):
    """Peak-to-peak spread of the last per_cycle samples."""
    tail = samples[-per_cycle:]
    return max(tail) - min(tail)


if __name__ == "__main__":
    print("predicted ripple:", reservoir_ripple(0.05, 100.0, 1000e-6), "V")
    print("C for 0.5 V at 50 mA:", capacitor_for_ripple(0.05, 100.0, 0.5), "F")
    s = simulate(17.0, 50.0, 1000e-6, 220.0, 1.4, 10, 2000)
    if s:
        tail = s[-2000:]
        mean = sum(tail) / len(tail)
        print("mean output:", mean, "V")
        print("measured ripple:", measured_ripple(s, 2000), "V")
        print("formula would say:", reservoir_ripple(mean / 220.0, 100.0, 1000e-6), "V")
'''}],
                "hints": [
                    "`reservoir_ripple` is `i_load / (f_ripple * c)`, and `capacitor_for_ripple` is `i_load / (f_ripple * v_ripple)`. Watch the brackets: `i_load / f_ripple * c` multiplies where it should divide.",
                    "In `simulate`, build the list with `out.append(v)` at the **end** of each step, after `v` has been updated. Appending first shifts every sample by one step and moves the measured ripple slightly.",
                    "The discharge step is `v -= (v / r_load) * dt / c`. The current is taken at the start of the step, which is forward Euler — with 2000 samples per cycle the error is far below the ripple you are measuring.",
                    "`measured_ripple` is `max(tail) - min(tail)` where `tail = samples[-per_cycle:]`. Using the whole list instead of the tail includes the start-up ramp from 0 V and gives a wildly wrong answer.",
                    "The measured ripple should come out *below* the formula's prediction. If it comes out above, check that `abs` is around the sine — without it you have built a half-wave rectifier, whose gaps are twice as long.",
                ],
                "tests": [
                    {"name": "the design formulas invert each other", "code": r'''
v = reservoir_ripple(0.05, 100.0, 1000e-6)
assert abs(v - 0.5) < 1e-12, f"50 mA, 100 Hz, 1000 uF gives 0.5 V, got {v}"
c = capacitor_for_ripple(0.05, 100.0, 0.5)
assert abs(c - 1000e-6) < 1e-12, f"the same numbers back the other way give 1000 uF, got {c}"
assert abs(reservoir_ripple(0.10, 100.0, 1000e-6) - 1.0) < 1e-12, \
    "twice the load current is twice the ripple"
assert abs(reservoir_ripple(0.05, 50.0, 1000e-6) - 1.0) < 1e-12, \
    "half the ripple frequency is twice the ripple, which is half-wave against full-wave"
'''},
                    {"name": "the simulation runs and settles near the peak", "code": r'''
s = simulate(17.0, 50.0, 1000e-6, 220.0, 1.4, 10, 2000)
assert len(s) == 20000, f"cycles * per_cycle samples expected, got {len(s)}"
tail = s[-2000:]
assert abs(max(tail) - 15.6) < 1e-6, \
    f"the peak is 17 V less 1.4 V of bridge drops, so 15.6 V; got {max(tail)}"
assert abs(min(tail) - 14.967554528595274) < 1e-6, f"expected a trough of 14.9676 V, got {min(tail)}"
'''},
                    {"name": "the measured ripple, and how the formula compares", "code": r'''
s = simulate(17.0, 50.0, 1000e-6, 220.0, 1.4, 10, 2000)
r = measured_ripple(s, 2000)
assert abs(r - 0.6324454714047256) < 1e-6, f"expected 0.632445 V of ripple, got {r}"
mean = sum(s[-2000:]) / 2000.0
assert abs(mean - 15.291122418509982) < 1e-6, f"expected a mean of 15.2911 V, got {mean}"
predicted = reservoir_ripple(mean / 220.0, 100.0, 1000e-6)
assert predicted > r, \
    f"the formula must be the pessimistic one: it says {predicted}, the simulation says {r}"
assert 1.0 < predicted / r < 1.3, \
    f"and pessimistic by about a tenth at these values, not by a factor; ratio was {predicted / r}"
'''},
                    {"name": "more capacitance and less load both cut the ripple", "code": r'''
big = measured_ripple(simulate(17.0, 50.0, 2200e-6, 220.0, 1.4, 10, 2000), 2000)
assert abs(big - 0.3000551163785552) < 1e-6, f"2200 uF should give 0.300055 V, got {big}"
light = measured_ripple(simulate(17.0, 50.0, 1000e-6, 1000.0, 1.4, 10, 2000), 2000)
assert abs(light - 0.14858065050918867) < 1e-6, f"a 1 k load should give 0.148581 V, got {light}"
small = measured_ripple(simulate(17.0, 50.0, 470e-6, 220.0, 1.4, 10, 2000), 2000)
assert abs(small - 1.2613201973354027) < 1e-6, f"470 uF should give 1.26132 V, got {small}"
assert small > 2.0 * big, \
    "roughly a fifth of the capacitance should give roughly five times the ripple"
'''},
                    {"name": "the two diode drops of a bridge really are subtracted", "code": r'''
s = simulate(17.0, 50.0, 1000e-6, 220.0, 1.4, 10, 2000)
half = simulate(17.0, 50.0, 1000e-6, 220.0, 0.7, 10, 2000)
assert abs(max(half[-2000:]) - 16.3) < 1e-6, \
    f"with a single 0.7 V drop the peak is 16.3 V, got {max(half[-2000:])}"
assert abs(max(half[-2000:]) - max(s[-2000:]) - 0.7) < 1e-9, \
    "the difference between the two peaks must be exactly the extra diode drop"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Zener regulation, and why a diode is not a resistor",
            "summary": "Reverse breakdown made useful, and the sharpest statement of the difference between static and dynamic resistance.",
            "concepts": [
                "Pushed far enough in reverse, every junction breaks down and conducts hard. **Zener breakdown** (below about 5 V) is quantum tunnelling through a thin depletion region; **avalanche breakdown** (above about 6 V) is impact ionisation. Both are non-destructive if the current is limited.",
                "The two mechanisms have opposite temperature coefficients, which is why a 5.6 V Zener has almost none and is the value to pick when stability matters more than the number.",
                "A **Zener shunt regulator** is a series resistor $R_S$ from the raw supply and a Zener across the load. The Zener takes whatever current the load does not, and the output stays near $V_Z$.",
                "The Zener's own dynamic resistance $r_z$ — typically 5 to 30 Ω — is what limits how well it regulates. Modelled as a fixed source $V_{Z0}$ in series with $r_z$, the circuit is an ordinary linear network again.",
                "**Line regulation** is $\\Delta V_{out}/\\Delta V_{in}$, and for this circuit it is simply the divider ratio $(r_z \\parallel R_L)/(R_S + r_z \\parallel R_L)$. A larger $R_S$ regulates better against the line, and burns less — the waste is $(V_{in}-V_{out})^2/R_S$, which falls as $R_S$ rises. What a larger $R_S$ costs is current in reserve: less is left over for the load, so the regulator drops out sooner.",
                "**Load regulation** is how far the output moves between no load and full load. It is roughly $r_z\\Delta I_{load}$, because the Zener has to absorb every milliamp the load stops taking.",
                "The design constraint that decides $R_S$ is a worst case, not a typical case: the Zener must still carry its minimum current when the supply is at its **lowest** and the load at its **heaviest**. That gives $R_S \\le (V_{in,min} - V_Z)/(I_{Z,min} + I_{load,max})$.",
                "The opposite corner sets the power ratings: highest supply, lightest load, and the Zener absorbs the lot. A regulator that survives full load may still cook at no load.",
                "A shunt regulator is deliberately wasteful: it draws its full current whether the load needs it or not. That is the price of a circuit with three components and no feedback loop.",
                "Everything in this module rests on the same fact as module 2. The Zener's static resistance at 5.1 V and 20 mA is 255 Ω; its dynamic resistance is 8 Ω. The first number tells you what it costs to run; the second tells you how well it regulates. A resistor has only one number, which is exactly why a resistor cannot do this job.",
            ],
            "read": [
                {
                    "title": "Designing to the corner, not to the nominal",
                    "minutes": 13,
                    "body": r'''
Module 3 produced a rail of about 15.6 V that moves with the mains and sags under load.
Something has to turn that into a voltage a circuit can rely on. The simplest thing that
does the job has three components and no feedback loop, and understanding exactly how
well it works — and exactly where it fails — is the point of this module.

## Why breakdown is not destruction

Push a junction hard in reverse and, at some voltage, it conducts. Below about 5 V the
depletion region is thin enough that carriers **tunnel** straight through the barrier;
above about 6 V the region is wider and the mechanism is **avalanche**, where a carrier
accelerated by the field knocks another one loose, and that one knocks two more.

Neither mechanism damages anything by itself. What damages the part is the power: a diode
in breakdown has several volts across it, and if nothing limits the current then $VI$
climbs until the junction melts. Limit the current and the device sits in breakdown
indefinitely. That is the whole trick, and it is why a Zener always appears with a series
resistor.

The two mechanisms have opposite temperature coefficients — tunnelling falls with
temperature, avalanche rises — so somewhere between them the coefficient passes through
zero. It does so near 5.6 V, which is why 5.6 V parts appear in reference circuits far
more often than such an odd number should.

## The model, and why it is the same construction as module 2

A Zener's data sheet says: 5.1 V at 20 mA, dynamic resistance 8 $\Omega$. That is a point
and a slope — exactly the tangent construction from module 2, applied to the breakdown
region instead of the forward one. Extended back to zero current the tangent meets the
axis at

$$V_{Z0} = 5.1 - 0.020 \times 8 = 4.94\ \text{V}$$

so the model is a **4.94 V source in series with 8 $\Omega$**. And with the diode replaced
by a source and a resistor, the circuit is an ordinary linear network again — solvable by
the node equation you have been writing since the first year.

## Worked example: 12 V in, 5.1 V out, 470 ohm load

**The circuit.** A series resistor $R_S$ from the 12 V rail to the output node; the Zener
model from that node to ground; the load, 470 $\Omega$, across the output.

**The node equation.** Everything $R_S$ delivers is split between the Zener and the load:

$$\frac{12 - V}{R_S} = \frac{V - 4.94}{8} + \frac{V}{470}$$

**Solving with $R_S = 220\ \Omega$.** Collecting terms in $V$:

$$0.054545 - \frac{V}{220} = 0.127128\,V - 0.6175
\quad\Longrightarrow\quad 0.672045 = 0.131673\,V$$
$$V = 5.104\ \text{V}$$

**The three currents.** They must add up, and checking that they do is the cheapest error
detector in circuit design:

```text
through R_S    (12 - 5.104)/220   = 31.35 mA
into the Zener (5.104 - 4.94)/8   = 20.49 mA
into the load   5.104/470         = 10.86 mA
                                    -------
Zener + load                        31.35 mA   agrees
```

**The power.** $R_S$ dissipates $(12-5.104)\times0.03135 = 0.216$ W; the Zener dissipates
$5.104 \times 0.02049 = 0.105$ W.

This is the circuit you draw and measure in the build, **A 5.1 V rail that holds under
load** — those components, that output voltage and those three currents. The lab,
**Designing and grading a shunt regulator**, then turns the same node equation into four
design functions: the output, the Zener current, the line regulation, and the largest
series resistor the worst corner will allow.

## How well does it regulate? Two numbers, both derivable

**Line regulation.** Move the input and ask how much of that reaches the output. With the
Zener modelled as a source in series with $r_z$, the output node is driven by $R_S$ from
above and held by $r_z \parallel R_L$ from below — a plain divider, because a fixed source
contributes nothing to a *change*:

$$\frac{\Delta V_{out}}{\Delta V_{in}} = \frac{r_z \parallel R_L}{R_S + (r_z \parallel R_L)}
= \frac{7.87}{227.87} = 0.0345$$

So 2 V of input change becomes 69 mV at the output: a 12 V rail moving to 14 V takes the
output from 5.104 V to 5.173 V. Not perfect — but two volts went in and 69 millivolts
came out, which is the factor of 29 the divider promised; in relative terms a 16.7% swing
on the raw rail has become a 1.4% swing on the output.

**Load regulation.** Disconnect the load entirely. The node equation loses its last term:

$$\frac{12 - V}{220} = \frac{V - 4.94}{8} \quad\Longrightarrow\quad V = 5.188\ \text{V}$$

The output rose 84 mV when 10.86 mA of load was removed, which is an output resistance of
$0.084/0.01086 = 7.7\ \Omega$. And that number is derivable too — looking back into the
output node with the input shorted, you see $r_z$ in parallel with $R_S$:

$$r_z \parallel R_S = 8 \parallel 220 = 7.72\ \Omega$$

which matches. Note it is *not* simply $r_z$: the concept list's "roughly $r_z\Delta I$"
is the right idea, and $r_z \parallel R_S$ is the exact version. For any sane design
$R_S \gg r_z$ and the two agree to within a few per cent.

## Designing to the corner

Everything above used nominal values, and a regulator that works at nominal is not a
regulator. The rail from module 3 moves with the mains; say $\pm15\%$, so 10.2 V to
13.8 V. The load is 0 to 10.9 mA. The Zener needs at least 5 mA to stay in breakdown and
no more than 40 mA to stay cool.

**The corner that sets the largest $R_S$** is the worst of both: lowest input, heaviest
load. There $R_S$ has the least voltage to work with and the load is taking the most, so
it is where the Zener is closest to starving:

$$R_S \le \frac{V_{in,min} - V_Z}{I_{Z,min} + I_{load,max}}
= \frac{10.2 - 5.1}{0.005 + 0.0109} = 321\ \Omega$$

**The opposite corner sets the ratings**: highest input, no load, so the Zener absorbs
everything. With $R_S = 220\ \Omega$, solving the no-load node equation at 13.8 V gives
$V = 5.251$ V and $I_Z = 38.9$ mA — inside the 40 mA limit, but only just.

And now the number worth the whole section. At that same corner the series resistor
dissipates

$$\frac{(13.8 - 5.251)^2}{220} = 0.332\ \text{W}$$

against the 0.216 W it dissipates at nominal. A quarter-watt resistor comfortably passes
the nominal calculation and fails on a high-mains day. This is what "design to the corner"
buys you, and it costs one extra line of arithmetic.

Both 220 $\Omega$ and 321 $\Omega$ satisfy every constraint, which is worth noticing: this
is a design with a *window*, not an equation with a root. Larger $R_S$ regulates better
against the line (the divider ratio falls), wastes less, and runs the Zener cooler — but
leaves less current in reserve, so it drops out of regulation sooner if the load grows.

## The mistake people actually make

Two, and the first is the one this whole course keeps circling.

**Quoting the static resistance.** At the operating point the Zener carries 20.49 mA at
5.104 V, so $V/I = 249\ \Omega$. Replace the model with a plain 249 $\Omega$ resistor and
the DC solution does not move by a millivolt — same output, same currents, same power in
the same places. It is not a regulator, and the arithmetic that proves it takes one line:
remove the load. The impostor becomes a bare divider, $12 \times 249/(220+249) = 6.37$ V.
The real Zener goes to 5.19 V. Same circuit at the operating point, 1.2 V apart one step
away from it, because 249 $\Omega$ is the only number the resistor has and the Zener
answers with 8 $\Omega$.

**Designing at nominal.** Every constraint in this circuit binds at a corner, and the
corners are in opposite directions: the resistor's maximum is set by the low-line,
full-load case, and its power rating and the Zener's are set by the high-line, no-load
case. Checking the middle checks neither.

## Where this stops holding

- **A shunt regulator wastes its full current always.** It draws 31.35 mA from the raw
  rail whether the load wants 10.9 mA or nothing, because the Zener's job is to absorb the
  difference. At nominal that is $12 \times 0.03135 = 0.376$ W taken in to deliver
  0.055 W, an efficiency of 15%; the other 0.321 W is the 0.216 W in $R_S$ and the
  0.105 W in the Zener, computed above. This is the price of three components and no
  feedback, and it is why every supply above a few tens of milliamps uses a series-pass
  regulator instead.
- **$r_z$ is not a constant.** Data sheets quote it at one test current, and it rises
  sharply as the current falls — which is the real reason for the $I_{Z,min}$ constraint.
  Near the knee, regulation is far worse than 8 $\Omega$ suggests.
- **$r_z$ is at its best around 7 V.** Below about 5 V and above about 10 V the dynamic
  resistance of real parts climbs, so the 5.6 V chosen for temperature stability is not
  the same as the value chosen for the best regulation.
- **Nothing here rejects noise above the audio band.** The model is resistive, so the
  divider ratio is frequency-independent — but a real Zener generates its own noise
  (avalanche is a shot-noise process, and a Zener is a respectable noise *source*), and
  the usual fix is a capacitor across it, which is also the usual fix for the 100 Hz that
  survives from module 3.
''',
                },
            ],
            "sandbox": {
                "title": "How much filtering the ripple actually needs",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 20, "zeta": 1.5, "K": 1},
                "brief": r'''
A reservoir capacitor leaves a rail with hundreds of millivolts of ripple on it at
100 Hz. Everything downstream — a filter, a regulator, or both — is judged by how much
of that 100 Hz it removes while leaving the DC alone.

This is a Bode plot of a low-pass filter with **two energy stores** — an inductor and a
capacitor, the second-order response EE102 put in front of you: **gain in decibels on top, phase in
degrees below, against angular frequency $\omega$ on a logarithmic axis** running from
0.1 to 2000 rad/s. The five ticks on that axis are labelled 0.1, 1, 14, 168 and 2000.
The amber dot marks the corner $\omega_n$, and $\zeta$ is the damping, which falls as
the resistance in the loop falls.

Two conversions are worth having to hand. A gain of $G$ is $20\log_{10}G$ decibels, so
$-20$ dB is a factor of ten and $-60$ dB a factor of a thousand. And 100 Hz — the
ripple frequency of a bridge on 50 Hz mains — is $2\pi \times 100 = 628$ rad/s, which
on this axis sits between the ticks marked 168 and 2000.
''',
                "notice": [
                    "The gain $K$ opens at 1, and the far left of the top plot sits exactly on the dashed 0 dB line. That is the first requirement on any smoothing filter: at DC it must pass its input untouched, because the DC is the rail you are trying to deliver.",
                    "The amber dot sits at $\\omega_n = 20$ rad/s, and with $\\zeta = 1.5$ it is at $-9.5$ dB — already well below the flat region. A heavily damped second-order filter has no peak at all, and its $-3$ dB point is not at the marker but a long way to its left, near 7.5 rad/s.",
                    "Read the top curve at 628 rad/s, between the 168 and 2000 ticks. It is close to $-60$ dB, a factor of a thousand: this filter turns 500 mV of ripple into 500 µV. Below it, the phase has already reached about $-175^\\circ$, so what little ripple survives comes out inverted.",
                    "Drag $\\zeta$ down to its minimum of 0.05, leaving everything else. The amber dot leaps from $-9.5$ dB to $+20$ dB — the filter now **amplifies** by ten at its own corner. An LC smoothing filter whose resonance lands anywhere near the ripple frequency makes the ripple worse, which is why real ones are damped or placed far below it.",
                    "Put $\\zeta$ back to 1.5 and drag the corner $\\omega_n$ from 20 up to its maximum of 200. The 628 rad/s point climbs from about $-60$ dB to about $-22$ dB: ten times the corner frequency costs nearly 40 dB of rejection, because a two-store roll-off falls as the square of the frequency ratio — 40 dB per decade, the figure from EE102. Filtering is bought with big, slow components, and there is no way around it.",
                ],
            },
            "quiz": {
                "title": "Shunt regulation and its worst cases",
                "minutes": 9,
                "questions": [
                    {
                        "q": "Which corner of the operating range sets the **largest** series resistor a Zener shunt regulator may use?",
                        "opts": [
                            "lowest input voltage with the heaviest load",
                            "highest input voltage with the heaviest load",
                            "lowest input voltage with no load",
                            "highest input voltage with no load",
                        ],
                        "a": 0,
                        "why": r'''
That is the corner where the series resistor has the least voltage across it to work
with *and* the load is taking the most, so it is where the Zener is closest to running
out of current and dropping out of regulation. Sizing $R_S$ anywhere else leaves the
regulator working on the bench and failing at the bottom of the mains cycle. The
opposite corner — highest input, no load — is also a design case, but it sets the
*power ratings* rather than the resistor value.
''',
                    },
                    {
                        "q": "A 12 V rail feeds 220 Ω into a Zener modelled as 4.94 V in series with 8 Ω, with a 470 Ω load. The output is 5.104 V. If the rail moves to 14 V, roughly where does the output go?",
                        "opts": ["5.95 V", "5.30 V", "5.17 V", "5.104 V — that is what regulation means"],
                        "a": 2,
                        "why": r'''
The line regulation is the divider ratio $(r_z \parallel R_L)/(R_S + r_z \parallel R_L)$.
With $8 \parallel 470 = 7.87\ \Omega$, that is $7.87/227.87 = 0.0345$, so 2 V of input
change becomes $2 \times 0.0345 = 69$ mV of output change: 5.104 V goes to 5.173 V.
"5.104 V — that is what regulation means" is the seductive one: regulation is very
good, but it is not perfect, and
quoting a real number rather than "regulated" is what lets you decide whether it is
good enough. The 5.95 V answer is what you get if you assume the output simply scales with the
input, $5.104 \times 14/12 = 5.95$ V. That is a plain divider's behaviour, and
preventing it is the entire reason the Zener is in the circuit.
''',
                    },
                    {
                        "q": "A Zener regulator is working correctly at full load. The load is then disconnected entirely. What happens to the Zener current?",
                        "opts": [
                            "it falls to zero",
                            "it is unchanged, because the series resistor sets it",
                            "it rises slightly",
                            "it rises by the whole of the load current the Zener now has to absorb",
                        ],
                        "a": 3,
                        "why": r'''
The series resistor delivers roughly the same current whatever happens downstream,
because the output barely moves; so every milliamp the load stops taking is a
milliamp the Zener must take instead. That is the defining behaviour of a *shunt*
regulator, and it is why the no-load case sets the Zener's power rating. A 5.1 V Zener
carrying 20 mA at full load and 60 mA at no load dissipates 0.1 W and 0.31 W
respectively — a 0.4 W part is fine, a 0.25 W part is not.
''',
                    },
                    {
                        "q": "Why does a Zener regulate at all, when a resistor to ground would not?",
                        "opts": [
                            "because its resistance is much lower than the load's",
                            "because its dynamic resistance is far smaller than its static resistance, so its voltage barely moves when its current changes",
                            "because it dissipates less power than a resistor would",
                            "because it conducts in only one direction",
                        ],
                        "a": 1,
                        "why": r'''
This is module 2's lesson in its sharpest form. At 5.1 V and 20 mA the Zener's static
resistance is 255 Ω and its dynamic resistance is 8 Ω — a factor of thirty apart. A
resistor has one number for both, so a resistive divider set to 5.1 V at 20 mA has an
output impedance of tens of ohms and sags the instant the load changes. The Zener
holds because the *slope* of its characteristic is nearly vertical, not because the
characteristic passes through any particular point.
''',
                    },
                    {
                        "q": "You need a 5 V reference whose voltage drifts as little as possible with temperature. Which Zener should you specify?",
                        "opts": [
                            "3.3 V, because tunnelling is the more stable mechanism",
                            "5.6 V, because the two breakdown mechanisms have opposite temperature coefficients and roughly cancel there",
                            "12 V, because avalanche has no temperature coefficient",
                            "any of them, since a Zener voltage does not depend on temperature",
                        ],
                        "a": 1,
                        "why": r'''
Below about 5 V, breakdown is dominated by tunnelling, whose voltage *falls* with
temperature; above about 6 V, avalanche dominates and the voltage *rises*. Around
5.6 V the two effects roughly cancel, and that is why 5.6 V parts have a temperature
coefficient near zero and turn up in reference circuits far more often than their odd
value would suggest. It is also a good example of an engineering choice made for a
physical reason that has nothing to do with the number wanted.
''',
                    },
                ],
            },
            "build": {
                "title": "A 5.1 V rail that holds under load",
                "minutes": 30,
                "brief": r'''
A 12 V raw supply — the sort a bridge and reservoir produce — has to feed a load that
behaves like a **470 Ω resistor** and needs a rail near **5.1 V**. You have a 5.1 V
Zener whose data sheet quotes 5.1 V at 20 mA with a dynamic resistance of **8 Ω**, so
its piecewise-linear model is a **4.94 V source in series with 8 Ω** — the same tangent
construction as module 2, applied to the breakdown region instead of the forward one.

## The specification

- the output, **with the 470 Ω load connected**, must land between **4.98 V and 5.22 V**
- the Zener current must be between **5 mA** and **40 mA**: below 5 mA it slides out of
  breakdown and stops regulating, above 40 mA it overheats
- the whole circuit may draw no more than **40 mA** from the 12 V rail
- the series resistor must dissipate no more than **0.30 W**, so a half-watt part will do

## What to add

The canvas gives you the 12 V supply, the 470 Ω load and a probe on the load's upper
node. Add the series resistor from the 12 V rail to that node, and the Zener model —
the 4.94 V source and the 8 Ω resistor in series — from that node to ground, with the
source's **+ terminal facing the output**.

## How to choose the resistor

Work at the node. Everything the series resistor delivers is shared between the load
and the Zener:

$$\frac{12 - V}{R_S} = \frac{V - 4.94}{8} + \frac{V}{470}$$

Pick your target $V$, work out the two branch currents it implies, add them, and
divide the resistor's voltage by the total. The specification is deliberately loose
enough that a whole range of standard values works — this is a design with a window,
not an equation with one root, and knowing how wide the window is matters more than
hitting its centre.

## The trap

A design that lands at 5.104 V with 20.5 mA in the Zener puts the Zener's *static*
resistance at $5.104/0.0205 = 249\ \Omega$. Put a plain 249 Ω resistor from the output
node to ground instead of the model and the DC answer does not move by a millivolt:
same output, same currents, same power dissipated in the same places.

It is not a regulator, and one line of arithmetic says so. Work out on paper what each
version does when the load is taken away. The impostor becomes a bare divider and its
output climbs from 5.10 V to 6.37 V; the real model climbs only to 5.19 V, because
249 Ω is the only number the impostor has where the Zener answers with 8 Ω.

You cannot remove the load here — check one insists it stays — so the last check
measures the Zener branch itself instead: the current in its offset source, and the
volts $r_z$ has to account for. That is what stops the impostor passing by landing on
the right point.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p6", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 470},
                        {"id": "p7", "kind": "GND", "x": 17, "y": 11},
                        {"id": "p8", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [11, 8], "b": [17, 8]},
                        {"a": [17, 10], "b": [17, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 220},
                        {"id": "p3", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 8},
                        {"id": "p4", "kind": "V", "x": 13, "y": 11, "rot": 1, "value": 4.94},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 13},
                        {"id": "p6", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 470},
                        {"id": "p7", "kind": "GND", "x": 17, "y": 11},
                        {"id": "p8", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [17, 8]},
                        {"a": [13, 12], "b": [13, 13]},
                        {"a": [17, 10], "b": [17, 11]},
                    ],
                },
                "checks": [
                    {"name": "the load is connected and the 12 V rail is feeding it", "code": r'''
const out = c.outNode();
const load = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 470) <= 24 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(load.length === 1,
  'The 470 ohm load must run from the probed node to ground. A regulator measured ' +
  'with its load disconnected is measuring nothing, and this circuit is entirely ' +
  'about what happens when the load is there.');
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 12) < 0.5; });
c.assert(sup.length === 1,
  'Exactly one 12 V raw supply; found ' + sup.length + '.');
const isup = Math.abs(c.dc().currents[sup[0].id]);
c.assert(isup > 0.001,
  'The 12 V rail is delivering ' + c.fmt(isup, 'A') + ' — nothing. Until a series ' +
  'resistor joins the rail to the probed node, the load sits at ground and every ' +
  'other measurement here is meaningless.');
'''},
                    {"name": "the output lands between 4.98 V and 5.22 V", "code": r'''
const v = c.vout();
c.assert(v >= 4.98 * 0.999 && v <= 5.22 * 1.001,
  'The regulated rail is ' + c.fmt(v, 'V') + ', outside the 4.98 V to 5.22 V window. ' +
  'Check the offset source is the right way up and the series resistor is in the range ' +
  'the node equation asks for.');
'''},
                    {"name": "the Zener carries between 5 mA and 40 mA", "code": r'''
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 12) < 0.5; })[0];
const isup = Math.abs(c.dc().currents[sup.id]);
const v = c.vout();
const iz = isup - v / 470;
c.assert(iz >= 0.005 * 0.99,
  'The Zener is only carrying ' + c.fmt(iz, 'A') + '. Below about 5 mA it leaves the ' +
  'breakdown knee and the output starts to follow the input; make the series resistor smaller.');
c.assert(iz <= 0.040 * 1.01,
  'The Zener is carrying ' + c.fmt(iz, 'A') + ', which will overheat it. Make the series ' +
  'resistor larger so less current is wasted through the Zener.');
'''},
                    {"name": "the supply gives at most 40 mA and the resistor stays under 0.30 W", "code": r'''
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 12) < 0.5; })[0];
const isup = Math.abs(c.dc().currents[sup.id]);
const v = c.vout();
c.assert(isup > 0.001,
  'The raw supply is delivering ' + c.fmt(isup, 'A') + ', so there is no budget to ' +
  'measure yet. Connect the series resistor from the 12 V rail to the probed node.');
c.assert(isup <= 0.040 * 1.01,
  'The raw supply is being asked for ' + c.fmt(isup, 'A') + ', over the 40 mA budget.');
const p = (12 - v) * isup;
c.assert(p <= 0.30 * 1.01,
  'The series resistor is dissipating ' + c.fmt(p, 'W') + ', over the 0.30 W allowed. ' +
  'It drops about 7 V, so its power is 7 times whatever current you let through it.');
'''},
                    {"name": "the shunt branch is the Zener model, not a resistor of the same value", "code": r'''
const zs = c.net.parts.filter(function (p) {
  return p.kind === 'V' && p.value > 3.0 && p.value < 6.0;
});
c.assert(zs.length === 1,
  'Found ' + zs.length + ' offset source between 3 V and 6 V, and this circuit needs ' +
  'exactly one: the 4.94 V source of the Zener model. A plain resistor to ground can ' +
  'be picked to give the same 5.1 V at the same current — 249 ohms does it — and it ' +
  'is not a regulator, because 249 ohms is the only number it has.');
const z = zs[0];
c.close(z.value, 4.94, 0.02,
  'the offset source of the Zener model. The tangent to the breakdown curve at 5.1 V ' +
  'and 20 mA meets the axis at 5.1 - 0.020 * 8 = 4.94 V');
const iz = Math.abs(c.dc().currents[z.id]);
const v = c.vout();
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 12) < 0.5; })[0];
const shunt = Math.abs(c.dc().currents[sup.id]) - v / 470;
c.close(iz, shunt, 0.02,
  'the current in the offset source. It has to be the whole shunt current — everything ' +
  'the series resistor delivers that the load does not take — so the source must sit ' +
  'in series with r_z between the probed node and ground, not off to one side');
c.close(v - z.value, iz * 8.0, 0.05,
  'the volts left across r_z. The model says V_out = V_Z0 + r_z * I_Z, so the output ' +
  'above the 4.94 V offset must be 8 ohms times the Zener current; if it is not, the ' +
  'dynamic resistance is missing or is the wrong value');
'''},
                ],
                "hints": [
                    "Start from the target. At 5.10 V the load takes $5.10/470 = 10.9$ mA, and a Zener current of 20 mA gives 30.9 mA in total, so $R_S = (12 - 5.10)/0.0309 = 223\\ \\Omega$. The standard value 220 Ω is the obvious pick.",
                    "Check the window before you build. 180 Ω gives 5.156 V with 27 mA in the Zener; 390 Ω gives 4.999 V with 7.3 mA. Both pass. 470 Ω leaves only 4.36 mA in the Zener and fails, and 150 Ω asks the supply for 45.2 mA and fails.",
                    "For a vertical source the + terminal is the **top** pin, so the 4.94 V offset source must sit below the 8 Ω resistor with its top facing the output node.",
                    "The Zener current is not measured directly — it is what is left of the supply current after the load has taken its share. If a check complains about it, work out $I_{supply} - V_{out}/470$ by hand and see which way you need to move.",
                ],
            },
            "lab": {
                "title": "Designing and grading a shunt regulator",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
The circuit you just drew, written down so that the next one is arithmetic rather than
a drawing.

Model the Zener as `v_z0` in series with `r_z`, exactly as in the build. The node
equation for the output is then

$$V_{out} = \frac{V_S/R_S + V_{Z0}/r_z}{1/R_S + 1/r_z + 1/R_L}$$

which is nothing but the conductance form of the divider from EE101, with three
branches instead of two.

- `zener_output(v_s, r_s, v_z0, r_z, r_load)` returns that voltage.
- `zener_current(v_s, r_s, v_z0, r_z, r_load)` returns the current in the Zener,
  $(V_{out} - V_{Z0})/r_z$. It should call `zener_output` rather than repeat it.
- `line_regulation(v_lo, v_hi, r_s, v_z0, r_z, r_load)` returns
  $\Delta V_{out}/\Delta V_{in}$ over that input range — a dimensionless number, small
  is good.
- `max_series_resistor(v_s_min, v_out, i_z_min, i_load_max)` returns the largest series
  resistor that still leaves `i_z_min` in the Zener at the worst corner:
  $(V_{S,min} - V_{out})/(I_{Z,min} + I_{load,max})$.

For "no load", pass a very large resistance such as `1e12` rather than special-casing
infinity. The formula handles it correctly and the code stays one line.
''',
                "files": [{"name": "main.py", "content": r'''
"""A Zener shunt regulator, as four design functions."""


def zener_output(v_s, r_s, v_z0, r_z, r_load):
    """Regulated output voltage with the Zener modelled as v_z0 in series with r_z."""
    # TODO: the three-branch conductance divider from the brief.
    return 0.0


def zener_current(v_s, r_s, v_z0, r_z, r_load):
    """Current through the Zener, in amps."""
    # TODO: call zener_output, then (v_out - v_z0) / r_z.
    return 0.0


def line_regulation(v_lo, v_hi, r_s, v_z0, r_z, r_load):
    """Change in output per volt of change in input, dimensionless."""
    # TODO: the output at v_hi minus the output at v_lo, over the input change.
    return 0.0


def max_series_resistor(v_s_min, v_out, i_z_min, i_load_max):
    """Largest series resistor that still holds i_z_min at the worst corner."""
    # TODO: the voltage the resistor has left, over the current it must carry.
    return 0.0


if __name__ == "__main__":
    v = zener_output(12.0, 220.0, 4.94, 8.0, 470.0)
    print("output:", v, "V")
    print("zener current:", zener_current(12.0, 220.0, 4.94, 8.0, 470.0), "A")
    print("no load:", zener_output(12.0, 220.0, 4.94, 8.0, 1e12), "V")
    print("line regulation:", line_regulation(10.0, 14.0, 220.0, 4.94, 8.0, 470.0))
    print("largest R_S for 5 mA at 10 V in and 11 mA out:",
          max_series_resistor(10.0, 5.1, 0.005, 0.011), "ohms")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""A Zener shunt regulator, as four design functions."""


def zener_output(v_s, r_s, v_z0, r_z, r_load):
    """Regulated output voltage with the Zener modelled as v_z0 in series with r_z."""
    return ((v_s / r_s + v_z0 / r_z)
            / (1.0 / r_s + 1.0 / r_z + 1.0 / r_load))


def zener_current(v_s, r_s, v_z0, r_z, r_load):
    """Current through the Zener, in amps."""
    return (zener_output(v_s, r_s, v_z0, r_z, r_load) - v_z0) / r_z


def line_regulation(v_lo, v_hi, r_s, v_z0, r_z, r_load):
    """Change in output per volt of change in input, dimensionless."""
    hi = zener_output(v_hi, r_s, v_z0, r_z, r_load)
    lo = zener_output(v_lo, r_s, v_z0, r_z, r_load)
    return (hi - lo) / (v_hi - v_lo)


def max_series_resistor(v_s_min, v_out, i_z_min, i_load_max):
    """Largest series resistor that still holds i_z_min at the worst corner."""
    return (v_s_min - v_out) / (i_z_min + i_load_max)


if __name__ == "__main__":
    v = zener_output(12.0, 220.0, 4.94, 8.0, 470.0)
    print("output:", v, "V")
    print("zener current:", zener_current(12.0, 220.0, 4.94, 8.0, 470.0), "A")
    print("no load:", zener_output(12.0, 220.0, 4.94, 8.0, 1e12), "V")
    print("line regulation:", line_regulation(10.0, 14.0, 220.0, 4.94, 8.0, 470.0))
    print("largest R_S for 5 mA at 10 V in and 11 mA out:",
          max_series_resistor(10.0, 5.1, 0.005, 0.011), "ohms")
'''}],
                "hints": [
                    "`zener_output` is one expression. Put the whole numerator in brackets and the whole denominator in brackets; a missing pair here is the only way to get this wrong.",
                    "A quick sanity check on `zener_output`: with `r_s` very large the answer should approach `v_z0`, and with `r_s` very small it should approach `v_s`. Both follow from the conductance form.",
                    "`zener_current` must call `zener_output`. Writing the divider out twice means fixing it twice when you find a bracket in the wrong place.",
                    "`line_regulation` returns a ratio, not a percentage. For the numbers in `main.py` it comes out around 0.035, meaning 35 mV of output movement per volt of input movement.",
                    "`max_series_resistor` has nothing to do with the Zener model — it is a worst-case budget. The resistor has $V_{S,min} - V_{out}$ volts across it and must pass the load's largest current plus the Zener's smallest.",
                ],
                "tests": [
                    {"name": "the regulated output of the circuit you drew", "code": r'''
v = zener_output(12.0, 220.0, 4.94, 8.0, 470.0)
assert abs(v - 5.103892765332354) < 1e-9, f"expected 5.1038928 V, got {v}"
i = zener_current(12.0, 220.0, 4.94, 8.0, 470.0)
assert abs(i - 0.020486595666544205) < 1e-12, f"expected 20.4866 mA in the Zener, got {i}"
'''},
                    {"name": "the two limiting cases of the series resistor", "code": r'''
tiny = zener_output(12.0, 1e-6, 4.94, 8.0, 470.0)
assert abs(tiny - 12.0) < 1e-3, \
    f"with almost no series resistance the output must follow the input, got {tiny}"
huge = zener_output(12.0, 1e12, 4.94, 8.0, 1e12)
assert abs(huge - 4.94) < 1e-3, \
    f"starved of current and unloaded, the Zener sits at v_z0, got {huge}"
loaded = zener_output(12.0, 1e12, 4.94, 8.0, 470.0)
assert abs(loaded - 4.94 * 470.0 / 478.0) < 1e-9, \
    f"starved of current but still loaded, r_z and the load divide v_z0, got {loaded}"
'''},
                    {"name": "removing the load pushes the output up and the current into the Zener", "code": r'''
loaded = zener_output(12.0, 220.0, 4.94, 8.0, 470.0)
free = zener_output(12.0, 220.0, 4.94, 8.0, 1e12)
assert abs(free - 5.187719298205569) < 1e-9, f"expected 5.1877193 V with no load, got {free}"
assert abs(free - loaded - 0.08382653287321506) < 1e-9, \
    "the load regulation should be 83.8 mV between full load and no load"
iz_free = zener_current(12.0, 220.0, 4.94, 8.0, 1e12)
iz_loaded = zener_current(12.0, 220.0, 4.94, 8.0, 470.0)
assert abs(iz_free - 0.030964912275696088) < 1e-12, f"expected 30.96 mA with no load, got {iz_free}"
assert iz_free > iz_loaded, "the Zener must absorb whatever the load stops taking"
'''},
                    {"name": "line regulation is the divider ratio of r_z against R_S", "code": r'''
reg = line_regulation(10.0, 14.0, 220.0, 4.94, 8.0, 470.0)
assert abs(reg - 0.0345207491737054) < 1e-12, f"expected 0.03452075, got {reg}"
parallel = 8.0 * 470.0 / (8.0 + 470.0)
assert abs(reg - parallel / (220.0 + parallel)) < 1e-12, \
    "the ratio must equal (r_z || R_L) / (R_S + r_z || R_L) exactly, because the circuit is linear"
tighter = line_regulation(10.0, 14.0, 1000.0, 4.94, 8.0, 470.0)
assert tighter < reg, \
    "a larger series resistor regulates better against the line; what it costs is not power but current in reserve for the load"
'''},
                    {"name": "the worst-case resistor budget", "code": r'''
r = max_series_resistor(10.0, 5.1, 0.005, 0.011)
assert abs(r - 306.25) < 1e-9, f"(10 - 5.1) / 0.016 is 306.25 ohms, got {r}"
r2 = max_series_resistor(15.0, 5.1, 0.010, 0.050)
assert abs(r2 - 165.0) < 1e-9, f"(15 - 5.1) / 0.060 is 165 ohms, got {r2}"
assert r2 < r, "a heavier load needs a smaller series resistor, whatever the input voltage"
'''},
                    {"name": "the design survives its own worst corner", "code": r'''
r = max_series_resistor(9.0, 5.0, 0.005, 0.011)
iz = zener_current(9.0, r, 4.94, 8.0, 470.0)
assert iz >= 0.005, \
    f"a resistor sized at the worst corner must still leave at least 5 mA there, got {iz}"
top = zener_current(14.0, r, 4.94, 8.0, 1e12)
assert top > iz, "and the opposite corner, highest input with no load, must be the hot one"
assert abs(r - 250.0) < 1e-9, f"(9 - 5.0) / 0.016 is 250 ohms, got {r}"
'''},
                ],
            },
        },
        # ---- M5 -----------------------------------------------------------
        {
            "title": "Drift, diffusion, and where $I_S$ actually comes from",
            "summary": "The two ways a carrier moves, the one constant that ties them together, and the calculation that turns a doping profile into the saturation current module 2 took on trust.",
            "concepts": [
                "**Drift** is motion in a field, and it produces a *velocity* rather than an acceleration: a carrier accelerates, scatters off a lattice vibration or an ionised dopant, and starts again, so on average $v = \\mu E$. The **mobility** $\\mu$ is about 0.135 m$^2$/V·s for electrons in lightly doped silicon and 0.048 for holes, and both fall as the doping rises, because there is more to scatter off.",
                "That gives the conductivity straight away: $\\sigma = q(n\\mu_n + p\\mu_p)$. In doped material one term is astronomically larger than the other, so n-type silicon at $N_d = 10^{22}$ m$^{-3}$ has $\\sigma = 216$ S/m and a resistivity of 4.62 mΩ·m — 0.46 Ω·cm in the units a wafer is actually sold in.",
                "**Diffusion** is motion down a concentration gradient with no field at all: $J_p = -qD_p\\,dp/dx$. It is not separate physics from drift, it is the same random walk seen from a different starting condition, which is why the two coefficients cannot be independent. The **Einstein relation** $D = V_T\\mu$ says so: at 300 K the two mobilities above give $D_n = 34.9$ cm$^2$/s and $D_p = 12.4$ cm$^2$/s with no new measurement.",
                "Forward bias injects minority carriers across the junction. They diffuse away from it and recombine, surviving a lifetime $\\tau$ and therefore travelling a **diffusion length** $L = \\sqrt{D\\tau}$ — 59 µm for electrons and 35 µm for holes at $\\tau = 1$ µs. That length sets the concentration gradient, the gradient sets the current, and evaluating it gives $I_S = qAn_i^2\\left(D_p/(L_pN_d) + D_n/(L_nN_a)\\right)$.",
                "So $I_S$ is not a fitted constant, it is a consequence of the doping — and it goes the way round that surprises people. Raising $N_d$ from $10^{22}$ to $10^{23}$ m$^{-3}$ divides $I_S$ by 8.7 and therefore *raises* the forward drop at 1 mA by 56 mV, from 0.729 V to 0.785 V. Every diode's 0.7 V is a decision somebody made at a furnace.",
            ],
            "read": [
                {
                    "title": "How fast an electron actually moves, and what that has to do with 0.7 volts",
                    "minutes": 15,
                    "body": r'''
A bar of n-type silicon, 500 µm long and 100 µm square, doped with $10^{22}$ donors per
cubic metre. Force 10 mA through it and put a probe on the top: 2.31 V, so 231 $\Omega$.

Now ask a question the meter cannot answer. Those 10 milliamps are $6\times10^{16}$
electrons crossing every second. How fast is each one going?

```python
Q = 1.602176634e-19
n_d = 1.0e22            # donors per cubic metre
mu_n = 0.135            # electron mobility at that doping, m^2/V.s
length = 500e-6         # metres
area = 1.0e-8           # square metres
i = 0.010               # amps forced through the bar

sigma = Q * n_d * mu_n
r = length / (sigma * area)
v = i * r
field = v / length
drift = mu_n * field

print("sigma      = %.1f S/m" % sigma)
print("resistance = %.0f ohm" % r)
print("volts      = %.3f V" % v)
print("field      = %.0f V/m" % field)
print("drift      = %.0f m/s" % drift)
print("check J/qn = %.0f m/s" % (i / area / (Q * n_d)))
```

```text
sigma      = 216.3 S/m
resistance = 231 ohm
volts      = 2.312 V
field      = 4623 V/m
drift      = 624 m/s
check J/qn = 624 m/s
```

624 metres per second, about twice the speed of sound in air, and *steady*. That last word
is the interesting one, and everything in this module comes out of explaining it.

## Why a field gives a velocity and not an acceleration

A charge in a vacuum in a 4623 V/m field feels a constant force and accelerates without
limit. An electron in silicon has an effective mass around a quarter of the free-electron
mass, so it would reach 624 m/s in about 0.2 ps and then keep going. It does not, because
it does not get 0.2 ps of clear road. It collides — with a lattice vibration, with an
ionised dopant — and each collision throws its direction away and leaves it starting again
from the local thermal motion.

So the picture is a stop-start crawl: accelerate for a fraction of a picosecond, scatter,
accelerate again. Between collisions the field adds the same small increment of velocity
every time, and the collisions keep discarding whatever has accumulated, so the *average*
velocity settles at a value proportional to the field rather than growing:

$$v = \mu E$$

The constant $\mu$ is the **mobility**, and it is a measured property of the material at a
given doping — about 0.135 m$^2$/V·s for electrons in lightly doped silicon and 0.048 for
holes, the difference being that a hole moves by having bonds hand it along and that is a
clumsier business than an electron in the conduction band.

Everything else about **drift** follows in two lines. Current density is charge density
times velocity, $J = qnv = qn\mu E$, and the thing multiplying $E$ is by definition the
conductivity:

$$\sigma = qn\mu \qquad\Longrightarrow\qquad R = \frac{L}{\sigma A} = 231\ \Omega$$

That also settles module 1's two cubes. Doping raised $n$ by a factor of a million, and
$\sigma$ went with it — from $2.93\times10^{-4}$ S/m in pure silicon to 216 S/m here,
which is 341 k$\Omega$ against 0.46 $\Omega$ for a centimetre cube.

The build, **Measuring a wafer's resistivity without measuring its contacts**, is about
the gap between computing that 231 $\Omega$ and measuring it. The probe needle and its
contact are worth another 22 $\Omega$, so a probe on the wrong node reports 253 $\Omega$
and tells you the wafer is 9.5% more resistive than it is — stably, repeatably, and with
nothing in the arithmetic to warn you.

## The other way a carrier moves

Take the field away entirely and put a concentration gradient in instead: more holes on
the left than on the right. Nothing pushes them. But random motion moves more carriers out
of a crowded region than into it, so there is a net flow down the gradient, proportional
to how steep it is:

$$J_p = -qD_p\frac{dp}{dx}$$

This is **diffusion**, and $D_p$ is the diffusion coefficient. It looks like a second,
independent property of the material, and it is not. Drift and diffusion are the same
scattering random walk seen from two different starting conditions, and that means the two
coefficients cannot be chosen independently.

Here is the argument, and it takes four lines. Put the material in equilibrium in a
potential that varies with position, as module 1's depletion region is. Two facts hold at
once. Boltzmann says the hole concentration is $p = p_0e^{-V/V_T}$. And equilibrium says
the *net* hole current is zero everywhere — drift and diffusion cancel, which is exactly
what module 1 meant by a junction with nothing connected. So

$$qp\mu_p E - qD_p\frac{dp}{dx} = 0$$

Now differentiate the Boltzmann expression: $dp/dx = -(p/V_T)\,dV/dx$, and $E = -dV/dx$,
so $dp/dx = (p/V_T)E$. Substituting,

$$qp\mu_pE - qD_p\frac{p}{V_T}E = 0
\qquad\Longrightarrow\qquad
\boxed{D = V_T\mu}$$

Everything cancels — the concentration, the field, the charge — and what is left is the
**Einstein relation**. A mobility you measured with a voltmeter and an ammeter hands you a
diffusion coefficient you never measured, and the constant between them is the thermal
voltage yet again.

A minority carrier that has diffused away from a junction does not travel for ever: it
recombines, after an average **lifetime** $\tau$. A random walk covers a distance that goes
as the square root of the time, and $D\tau$ is the only area those two quantities can
make, so the **diffusion length** is $L = \sqrt{D\tau}$.

```python
import math

V_T = 0.025851999786435535
tau = 1.0e-6                 # minority carrier lifetime, seconds

for name, mu in (("electrons", 0.135), ("holes", 0.048)):
    d = V_T * mu
    print("%-9s  mu = %.3f m^2/V.s   D = %.3e m^2/s = %.1f cm^2/s   L = %.1f um"
          % (name, mu, d, d * 1e4, math.sqrt(d * tau) * 1e6))
```

```text
electrons  mu = 0.135 m^2/V.s   D = 3.490e-03 m^2/s = 34.9 cm^2/s   L = 59.1 um
holes      mu = 0.048 m^2/V.s   D = 1.241e-03 m^2/s = 12.4 cm^2/s   L = 35.2 um
```

Tens of micrometres. Hold that number: it is comparable with the thickness of the silicon
in a real diode, which is why the geometry of the device turns out to matter.

## Where $I_S$ comes from

Module 2 took $I_S$ off a data sheet. It is four steps from what is now in hand, and this
module's derivation, **$I_S$, from the injected minority carriers**, does them one at a
time.

Work on the n-side, where holes are the minority carriers. At equilibrium there are
$p_{n0} = n_i^2/N_d$ of them. Forward bias lowers the barrier, and the same Boltzmann
factor as always raises the concentration at the edge of the depletion region to
$p_{n0}e^{V/V_T}$ — so the **excess**, the part that was not there before, is
$p_{n0}(e^{V/V_T} - 1)$. There is the $-1$ of the Shockley equation, arriving on its own
rather than being bolted on.

Those excess holes diffuse away from the junction and recombine, and they are essentially
gone after a diffusion length. So the gradient at the edge is the excess divided by $L_p$,
and Fick turns a gradient into a current:

$$J_p = \frac{qD_p n_i^2}{L_pN_d}\left(e^{V/V_T} - 1\right)$$

The p-side does the same thing with electrons, with $D_n$, $L_n$ and $N_a$ in place of
$D_p$, $L_p$ and $N_d$. Add them, multiply by the junction area, and everything in front of
the bracket is $I_S$:

$$I_S = qAn_i^2\left(\frac{D_p}{L_pN_d} + \frac{D_n}{L_nN_a}\right)$$

```python
import math

Q = 1.602176634e-19
V_T = 0.025851999786435535

n_i = 1.0e16
area = 1.0e-8
tau = 1.0e-6
d_n, d_p = V_T * 0.135, V_T * 0.048
l_n, l_p = math.sqrt(d_n * tau), math.sqrt(d_p * tau)


def i_s(n_a, n_d):
    return Q * area * n_i * n_i * (d_p / (l_p * n_d) + d_n / (l_n * n_a))


hole_term = d_p / (l_p * 1e22)
elec_term = d_n / (l_n * 1e24)
print("hole term into the n-side  = %.3e" % hole_term)
print("electron term into p-side  = %.3e" % elec_term)
print("ratio                      = %.1f" % (hole_term / elec_term))
for n_d in (1e22, 1e23):
    s = i_s(1e24, n_d)
    print("N_d = %.0e  ->  I_S = %.4e A   V_F at 1 mA = %.4f V"
          % (n_d, s, V_T * math.log(1.0 + 1e-3 / s)))
print("ten times the doping divides I_S by %.2f"
      % (i_s(1e24, 1e22) / i_s(1e24, 1e23)))
```

```text
hole term into the n-side  = 3.523e-21
electron term into p-side  = 5.908e-23
ratio                      = 59.6
N_d = 1e+22  ->  I_S = 5.7385e-16 A   V_F at 1 mA = 0.7287 V
N_d = 1e+23  ->  I_S = 6.5904e-17 A   V_F at 1 mA = 0.7846 V
ten times the doping divides I_S by 8.71
```

$5.74\times10^{-16}$ A, from a doping profile, an area and a lifetime — squarely inside the
$10^{-15}$ to $10^{-12}$ A that module 2 quoted from a data sheet, and now with reasons
attached. This whole chain, doping to conductivity to resistance to $D$ to $L$ to $I_S$, is
the five functions of the lab, **From a doping level to a saturation current**.

Two features of that output are worth stopping on. The hole term beats the electron term
by 59.6 to one, because the p-side is doped a hundred times harder and injection into a
heavily doped region is suppressed. Real diodes are made one-sided on purpose for that
reason: almost all the current is then one carrier type, which makes the device's speed and
its recovery behaviour predictable instead of a mixture of two.

And doping the n-side ten times harder divided $I_S$ by 8.71 rather than by 10, because
only one of the two terms moved.

## The mistake people actually make

Reading that last line as a defect and expecting heavier doping to give a *better* diode.
The reasoning is that more dopant means more carriers means better conduction means less
voltage dropped — and every step of it is true of the bar at the top of this page. Applied
to the junction it is exactly backwards: ten times the doping raised the forward drop at
1 mA from 0.7287 V to 0.7846 V, by 56 mV, which is the $V_T\ln 8.71$ the numbers demand.

The reason the intuition fails is that two different currents live in the same lump of
silicon. The bar conducts by *majority* carriers, and doping supplies those directly. The
junction conducts by *minority* carriers injected across it, and mass action says that
raising the majority population suppresses the minority one in exact proportion. Doping
helps one current and hurts the other, and the diode's forward drop is set by the one it
hurts.

There is a smaller trap in the same formula, and the lab warns about it because it produces
a plausible wrong answer rather than an absurd one: $D_p$ pairs with $L_p$ and $N_d$, not
with $N_a$. The holes are injected *into* the n-side, so it is the n-side doping that
limits them. Swap the two dopings and every number still looks like a saturation current.

## Where this stops holding

The mobility is not a constant, and this module used a single value for it throughout.
Every ionised dopant is a charged obstacle, so $\mu$ falls as the doping rises — from about
0.135 m$^2$/V·s in lightly doped silicon to well under half of that at $10^{24}$ m$^{-3}$.
That is why resistivity is published as a table rather than computed from a formula, and
why each number above was quoted at the doping it belongs to.

Worse, $v = \mu E$ itself fails at high field. The drift velocity has a ceiling of about
$10^5$ m/s in silicon, where the carriers start losing energy to the lattice as fast as the
field feeds it to them. The 624 m/s in the bar is 0.6% of that, so the linear law is safe
there. Put 1 V across the 100 nm channel of a modern transistor and the field is
$10^7$ V/m, where $\mu E$ predicts more than ten times the ceiling — and the whole
proportionality has stopped meaning anything.

The $I_S$ formula assumes the neutral regions are much *longer* than a diffusion length, so
that the excess carriers really do decay away inside the device. $L_p$ came out at 35 µm,
and plenty of real diodes are thinner than that. In such a short-base device the gradient is
set by the width of the neutral region rather than by $L_p$, and $I_S$ is correspondingly
larger.

The lifetime is the softest number in the calculation. One microsecond is a plausible
figure and nothing more; real lifetimes span orders of magnitude, and module 9's fast
diodes have theirs deliberately spoiled, which raises $I_S$ and the leakage together.

Finally, this is the *ideal diffusion* saturation current, and it is not what a meter reads
in reverse. Carriers generated inside the depletion region contribute a separate leakage
that this model contains no term for; it is larger in silicon at room temperature, and it
is why module 6 has to keep two different temperature rules apart.
''',
                },
            ],
            "quiz": {
                "title": "Transport, and the saturation current it produces",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A bar of n-type silicon is doped with $10^{22}$ m$^{-3}$ donors, and at that level the electron mobility is 0.135 m$^2$/V·s. What is its resistivity?",
                        "opts": ["4.6 Ω·cm", "0.46 Ω·cm", "216 Ω·cm", "0.46 Ω·m"],
                        "a": 1,
                        "why": r'''
$\sigma = qN_d\mu_n = 1.602\times10^{-19} \times 10^{22} \times 0.135 = 216$ S/m, so
$\rho = 1/\sigma = 4.62\times10^{-3}$ Ω·m. Converting to the centimetre units the
industry still uses divides by a hundred, not multiplies: 4.62 mΩ·m is 0.462 Ω·cm.
Quoting 0.46 Ω·m instead is the standard slip and puts the answer out by a factor of a
hundred; quoting 216 Ω·cm hands back the conductivity with a resistivity's unit
attached. Half a Ω·cm is worth remembering as a landmark — it is roughly where a
power device's drift region sits.
''',
                    },
                    {
                        "q": "The hole mobility in the same silicon is 0.048 m$^2$/V·s. What is the hole diffusion coefficient at 300 K?",
                        "opts": [
                            "$1.24\\times10^{-3}$ m$^2$/s",
                            "$1.86$ m$^2$/s",
                            "$0.048$ m$^2$/s — $D$ and $\\mu$ are the same number in SI units",
                            "it cannot be found without knowing the doping",
                        ],
                        "a": 0,
                        "why": r'''
Einstein: $D = V_T\mu = 0.025852 \times 0.048 = 1.24\times10^{-3}$ m$^2$/s, which is
12.4 cm$^2$/s in the units the tables use. Dividing instead of multiplying gives
1.86 and is dimensionally impossible — $D$ is an area per second and $\mu$ is not.
The point of the relation is that drift and diffusion are the *same* scattering seen
twice, so a mobility measured with a voltmeter tells you a diffusion coefficient you
never measured. Once again the constant of proportionality is $V_T$.
''',
                    },
                    {
                        "q": "Both sides of a junction are doped ten times more heavily. What happens to $I_S$?",
                        "opts": [
                            "multiplied by ten",
                            "unchanged — the two sides scale together, so the ratio is the same",
                            "divided by a hundred",
                            "divided by ten, and the forward drop at a fixed current rises by about 59 mV",
                        ],
                        "a": 3,
                        "why": r'''
Both terms of $I_S = qAn_i^2(D_p/(L_pN_d) + D_n/(L_nN_a))$ carry a doping in the
denominator, so both are divided by ten and so is their sum. Then
$V = V_T\ln(I/I_S)$ rises by $V_T\ln 10 = 59.5$ mV at any fixed current. Answering
"unchanged, because the ratio is the same" is module 1's rule misapplied: the built-in
potential depends on the doping *product*, but $I_S$ depends on how many minority
carriers are available to inject, and heavier doping means fewer.
''',
                    },
                    {
                        "q": "Which carriers actually carry the saturation current?",
                        "opts": [
                            "the majority carriers on each side, drifting in the junction field",
                            "minority carriers injected across the junction, diffusing away from it and recombining",
                            "carriers generated at the metal contacts",
                            "the ionised dopants themselves, once the field is strong enough to move them",
                        ],
                        "a": 1,
                        "why": r'''
Minority carriers, which is why $n_i^2$ appears in $I_S$ and the doping appears
underneath it. The majority carriers are the ones that were always there; what crosses
the junction and then has somewhere to go is the small population on the other side.
Dopant atoms are substituted into the lattice and never move at any field a diode
survives. The whole exponential is a statement about how many minority carriers the
barrier lets through, which is exactly the $10^{10}$ m$^{-3}$ that looked negligible
in module 1.
''',
                    },
                    {
                        "q": "A junction has $N_a = 10^{24}$ m$^{-3}$ on the p-side and $N_d = 10^{22}$ m$^{-3}$ on the n-side. Which injection dominates $I_S$?",
                        "opts": [
                            "hole injection into the lightly doped n-side, by roughly sixty to one",
                            "electron injection into the heavily doped p-side, by roughly sixty to one",
                            "the two contribute equally, because it is one device with one current",
                            "neither — $I_S$ is fixed by the width of the depletion region",
                        ],
                        "a": 0,
                        "why": r'''
Compare the two terms: $D_p/(L_pN_d) = 3.52\times10^{-21}$ against
$D_n/(L_nN_a) = 5.91\times10^{-23}$, a ratio of 59.6. The hundredfold difference in
doping does most of it and the different diffusion constants pull back a little.
That is why real diodes are made deliberately one-sided: injection into the heavily
doped side is suppressed, so almost all the current is one carrier type, which makes
the device's speed and its recovery behaviour predictable rather than a mixture.
''',
                    },
                    {
                        "q": "The doping of a silicon bar is raised by a factor of one hundred. Does its conductivity rise by exactly one hundred?",
                        "opts": [
                            "yes, exactly one hundred times",
                            "somewhat less, because the extra ionised dopants scatter carriers and the mobility falls",
                            "somewhat more, because heavier doping also raises the mobility",
                            "not at all — conductivity is a property of silicon and not of its doping",
                        ],
                        "a": 1,
                        "why": r'''
$\sigma = qn\mu$ has two factors and only one of them was changed on purpose. Every
ionised donor is a charged obstacle, so raising the doping raises the scattering and
lowers $\mu$ — from about 0.135 m$^2$/V·s in lightly doped silicon to well under half
that at $10^{24}$ m$^{-3}$. The conductivity still rises steeply, just not
proportionally, which is why a resistivity table is a table and not a formula. Every
number in this module quotes the mobility at the doping it belongs to for exactly
this reason.
''',
                    },
                ],
            },
            "derive": {
                "title": "$I_S$, from the injected minority carriers",
                "minutes": 14,
                "vars": ["n_i", "N_a", "N_d", "V", "V_T", "q", "A", "D_p", "D_n",
                         "L_p", "L_n", "tau_p", "I_S", "p_n0", "J_p"],
                "brief": r'''
Module 2 wrote $I = I_S(e^{V/V_T} - 1)$ and left $I_S$ as a number off a data sheet.
It is not a number off a data sheet; it is four lines of algebra from the two facts
module 1 already established.

Work on the n-side, where holes are the minority carriers. In equilibrium the hole
concentration there is $p_{n0} = n_i^2/N_d$. Forward bias raises the concentration at
the edge of the depletion region by the Boltzmann factor, to
$p_n(0) = p_{n0}\,e^{V/V_T}$ — the same exponential as before, and for the same
reason.

Those extra holes then have to go somewhere. They diffuse into the neutral n-region
and recombine, and the distance they cover before they do is the diffusion length
$L_p$.
''',
                "steps": [
                    {
                        "prompt": "Write the **excess** hole concentration at the edge of the n-side — the amount by which $p_n(0)$ exceeds its equilibrium value — in terms of $n_i$, $N_d$, $V$ and $V_T$.",
                        "given": "$p_n(0) = p_{n0}e^{V/V_T}$ with $p_{n0} = n_i^2/N_d$.",
                        "answer": "\\frac{n_i^2}{N_d}(exp(\\frac{V}{V_T}) - 1)",
                        "hint": "Excess means $p_n(0) - p_{n0}$. Factor $p_{n0}$ out of the subtraction and the $-1$ appears on its own.",
                        "deconstruct": [
                            "The excess is $p_{n0}e^{V/V_T} - p_{n0}$.",
                            "Take $p_{n0}$ outside the bracket, then substitute $p_{n0} = n_i^2/N_d$.",
                            "That $-1$ is the same $-1$ as in the Shockley equation, and it arrives here rather than being bolted on.",
                        ],
                    },
                    {
                        "prompt": "The excess decays over a distance $L_p$, so the concentration gradient at the edge is the excess divided by $L_p$. Multiply by $qD_p$ to get the hole current density $J_p$ there.",
                        "given": "$J_p = qD_p \\times (\\text{excess})/L_p$",
                        "answer": "\\frac{q D_p n_i^2}{L_p N_d}(exp(\\frac{V}{V_T}) - 1)",
                        "hint": "Nothing new happens here — take the previous answer, divide it by $L_p$ and multiply it by $qD_p$.",
                        "deconstruct": [
                            "The gradient is the excess concentration over the diffusion length.",
                            "Fick's law turns a gradient into a current density by multiplying by $qD_p$.",
                            "Everything except the exponential bracket is a constant of the device.",
                        ],
                    },
                    {
                        "prompt": "The p-side does the same thing with electrons, giving a second term with $D_n$, $L_n$ and $N_a$ in place of $D_p$, $L_p$ and $N_d$. Add the two current densities, multiply by the junction area $A$, and write the whole coefficient in front of $(e^{V/V_T} - 1)$ — that coefficient is $I_S$.",
                        "answer": "q A n_i^2 (\\frac{D_p}{L_p N_d} + \\frac{D_n}{L_n N_a})",
                        "hint": "Both terms share $qAn_i^2$ and both share the same exponential bracket, so only the two fractions differ.",
                        "deconstruct": [
                            "Write the electron term by swapping every $p$ subscript for an $n$ and $N_d$ for $N_a$.",
                            "Add the two densities; the exponential bracket is common and comes out.",
                            "Multiply by the area to turn a current density into a current.",
                        ],
                    },
                    {
                        "prompt": "One loose end: the diffusion length itself. A hole diffuses with coefficient $D_p$ and survives for a lifetime $\\tau_p$. Write $L_p$.",
                        "answer": "\\sqrt{D_p \\tau_p}",
                        "hint": "A diffusing particle covers a distance that grows as the square root of the time, and $D$ has units of area per second.",
                        "deconstruct": [
                            "$D_p\\tau_p$ has units of m$^2$/s times s, which is an area.",
                            "The square root of that area is the only length the two quantities can make.",
                        ],
                    },
                ],
                "closing": r'''
Put the numbers in. With $A = 10^{-8}$ m$^2$, $N_a = 10^{24}$ m$^{-3}$,
$N_d = 10^{22}$ m$^{-3}$, $n_i = 1.0\times10^{16}$ m$^{-3}$ and $\tau = 1$ µs on both
sides:

$$I_S = 5.74\times10^{-16}\ \text{A}$$

which is squarely inside the $10^{-15}$ to $10^{-12}$ A that module 2 quoted from a
data sheet — except that now it came from a doping profile and a lifetime rather than
from a measurement.

Two things follow immediately. The first is that $I_S$ falls as the doping rises, so
the forward drop *rises*: 0.729 V at 1 mA here, 0.785 V if the n-side is doped ten
times harder. The second is that $n_i^2$ sits in front of everything, and $n_i^2$ is
the most temperature-sensitive quantity in the whole subject. That is the next module.
''',
            },
            "build": {
                "title": "Measuring a wafer's resistivity without measuring its contacts",
                "minutes": 26,
                "brief": r'''
The transport arithmetic above turns a doping level into a resistivity, and a
resistivity into the resistance of a specific piece of silicon. This is that piece of
silicon, and the measurement that gets the number right.

## The bar

A bar of n-type silicon, doped $N_d = 10^{22}$ m$^{-3}$, with $\mu_n = 0.135$
m$^2$/V·s at that doping. It is **500 µm long** with a **100 µm square** cross
section, so $A = 1\times10^{-8}$ m$^2$.

$$\sigma = qN_d\mu_n = 216\ \text{S/m}, \qquad
\rho = 4.62\ \text{m}\Omega\cdot\text{m}, \qquad
R = \frac{\rho L}{A} = 231\ \Omega$$

Its bottom face is bonded straight onto the grounded package. Current is forced in at
the top through a probe needle, and that needle plus the metal-to-silicon contact
under it is worth about **22 Ω** — not a defect, just what a pressed contact is.

## What to build

The canvas gives you a **10 mA** current source and a probe. Add:

- the **22 Ω** contact resistance, in the path the forcing current takes,
- the **231 Ω** bar, from the probed node down to ground,

and wire the probe so that it sits on the **far side of the contact**, looking at the
bar alone.

## Why the wiring is the whole exercise

A voltmeter draws no current, so no current flows in the wire that reaches it, so no
voltage is dropped along that wire or across whatever it is touching. Put the probe on
the far side of the contact and the contact is outside the measurement entirely.

Put it on the near side — the same node the current source feeds — and you measure
253 Ω instead of 231 Ω, and conclude that the wafer is 9.5% more resistive than it is.
Nothing about the arithmetic warns you: the number is stable, repeatable, and wrong.
This is why every resistivity, sheet-resistance and on-resistance measurement worth
publishing forces current on one pair of contacts and senses voltage on another.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 0.010},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 4},
                        {"id": "p2", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [11, 7], "b": [13, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 0.010},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 4},
                        {"id": "p4", "kind": "R", "x": 7, "y": 7, "rot": 0, "value": 22},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 231},
                        {"id": "p2", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [6, 7]},
                        {"a": [8, 7], "b": [13, 7]},
                        {"a": [13, 7], "b": [13, 8]},
                        {"a": [13, 10], "b": [13, 11]},
                    ],
                },
                "checks": [
                    {"name": "10 mA is forced, and the probed node sits at 2.31 V", "code": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'I'; });
c.assert(src.length === 1,
  'Exactly one current source — the 10 mA forced through the bar. Found ' + src.length + '.');
c.close(Math.abs(src[0].value), 0.010, 0.02, 'the forcing current');
c.close(c.vout(), 2.3117, 0.03,
  'the voltage at the probed node. 216 S/m over a 500 um length and a 1e-8 m^2 section ' +
  'is 231 ohms, and 10 mA through 231 ohms is 2.31 V');
'''},
                    {"name": "the contact resistance is in the forcing path, not in the sensed one", "code": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'I'; })[0];
const force = src.n1 === 0 ? src.n2 : src.n1;
const out = c.outNode();
c.assert(force !== out,
  'The probe is on the same node the current source feeds, so it is reading the ' +
  'contact resistance as well as the bar. That is a two-wire measurement, and ' +
  'avoiding it is the whole point here: move the probe to the far side of the contact.');
const v = c.dc().v;
c.close(v[force] - v[out], 0.22, 0.15,
  'the volts across the contact resistance. 10 mA through 22 ohms is 0.22 V, and it is ' +
  'sitting between the source and the bar where the voltmeter cannot see it');
'''},
                    {"name": "the bar is the resistance the doping and the geometry say it is", "code": r'''
const out = c.outNode();
const bar = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(bar.length === 1,
  'Exactly one resistor from the probed node to ground — the bar itself. Found ' +
  bar.length + '. If the contact resistance is down here instead, it is inside the ' +
  'measurement again.');
c.close(bar[0].value, 231, 0.03, 'the bar resistance from rho times L over A');
c.close(c.vout() / bar[0].value, 0.010, 0.02,
  'the current actually in the bar. All ten milliamps have to go through it and nowhere else');
'''},
                    {"name": "and the two-wire answer would have been 9.5% high", "code": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'I'; })[0];
const force = src.n1 === 0 ? src.n2 : src.n1;
const v = c.dc().v;
const fourWire = c.vout() / 0.010;
const twoWire = v[force] / 0.010;
c.close(fourWire, 231, 0.03, 'the resistance the probe reports where you put it');
c.close(twoWire, 253, 0.03,
  'the resistance a probe on the forcing node would have reported. It is not a random ' +
  'error — it is exactly the contact resistance added on, every time, repeatably');
c.assert(twoWire / fourWire > 1.05,
  'The two readings differ by only ' + ((twoWire / fourWire - 1) * 100).toFixed(1) +
  '%, which means the contact resistance you placed is too small to make the point. ' +
  'A pressed probe on silicon really is tens of ohms.');
'''},
                ],
                "hints": [
                    "$\\sigma = 1.602\\times10^{-19} \\times 10^{22} \\times 0.135 = 216$ S/m. Then $R = L/(\\sigma A) = 500\\times10^{-6}/(216 \\times 10^{-8}) = 231\\ \\Omega$. Type `231`.",
                    "Place the 22 Ω contact horizontally between the current source's lower pin and the node the probe already sits on, then run the bar vertically from that node down to the ground below it.",
                    "The current source in the canvas is drawn with its top pin grounded so that it pushes current out of its lower pin into your circuit. Leave it where it is; the exercise is what you hang off it.",
                    "If the check about the two-wire answer complains that the two readings are the same, the contact resistance has ended up somewhere that carries no current — most likely in the wire going to the probe, where by definition nothing flows.",
                ],
            },
            "lab": {
                "title": "From a doping level to a saturation current",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Five functions that walk the whole chain of this module: doping to conductivity,
conductivity to a resistance you could measure, mobility to a diffusion coefficient,
diffusion to a length, and all of it to $I_S$.

- `conductivity(n, p, mu_n, mu_p)` returns $\sigma = q(n\mu_n + p\mu_p)$ in S/m.
- `bar_resistance(sigma, length, area)` returns $L/(\sigma A)$ in ohms.
- `diffusion_coefficient(mu, v_t)` returns $D = V_T\mu$ in m$^2$/s.
- `diffusion_length(d, tau)` returns $L = \sqrt{D\tau}$ in metres.
- `saturation_current(area, n_i, n_a, n_d, d_p, l_p, d_n, l_n)` returns

```text
q * area * n_i**2 * ( d_p / (l_p * n_d)  +  d_n / (l_n * n_a) )
```

in amps. Note which doping sits under which diffusion term: the holes injected into
the n-side are limited by $N_d$, and the electrons injected into the p-side by $N_a$.
Swapping them is the one mistake here that produces a plausible-looking wrong answer.

`Q_ELECTRON` and `V_T300` are defined for you. Everything is SI throughout.
''',
                "files": [{"name": "main.py", "content": r'''
"""Transport numbers: from a doping level to a saturation current."""

import math

Q_ELECTRON = 1.602176634e-19            # C
V_T300 = 0.025851999786435535           # V, kT/q at 300 K


def conductivity(n, p, mu_n, mu_p):
    """Conductivity in S/m from both carrier populations and both mobilities."""
    # TODO: q times (n*mu_n + p*mu_p).
    return 0.0


def bar_resistance(sigma, length, area):
    """Resistance in ohms of a uniform bar of conductivity `sigma`."""
    # TODO: length over (sigma * area).
    return 0.0


def diffusion_coefficient(mu, v_t):
    """Einstein: D = V_T * mu, in m^2/s."""
    # TODO: one multiplication.
    return 0.0


def diffusion_length(d, tau):
    """How far a minority carrier gets before it recombines, in metres."""
    # TODO: the square root of D times tau.
    return 0.0


def saturation_current(area, n_i, n_a, n_d, d_p, l_p, d_n, l_n):
    """The diode's I_S, in amps, from the two injected minority populations."""
    # TODO: the expression in the brief. Watch which doping goes with which term.
    return 0.0


if __name__ == "__main__":
    n_i = 1.0e16
    mu_n, mu_p = 0.135, 0.048
    sigma = conductivity(1e22, n_i * n_i / 1e22, mu_n, mu_p)
    print("sigma:", sigma, "S/m")
    print("bar, 500 um long, 1e-8 m^2:", bar_resistance(sigma, 500e-6, 1e-8), "ohm")
    d_n = diffusion_coefficient(mu_n, V_T300)
    d_p = diffusion_coefficient(mu_p, V_T300)
    print("D_n:", d_n, " D_p:", d_p)
    l_n = diffusion_length(d_n, 1e-6)
    l_p = diffusion_length(d_p, 1e-6)
    print("L_n:", l_n, " L_p:", l_p)
    i_s = saturation_current(1e-8, n_i, 1e24, 1e22, d_p, l_p, d_n, l_n)
    print("I_S:", i_s, "A")
    if i_s > 0:
        print("V_F at 1 mA:", V_T300 * math.log(1.0 + 1e-3 / i_s), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Transport numbers: from a doping level to a saturation current."""

import math

Q_ELECTRON = 1.602176634e-19            # C
V_T300 = 0.025851999786435535           # V, kT/q at 300 K


def conductivity(n, p, mu_n, mu_p):
    """Conductivity in S/m from both carrier populations and both mobilities."""
    return Q_ELECTRON * (n * mu_n + p * mu_p)


def bar_resistance(sigma, length, area):
    """Resistance in ohms of a uniform bar of conductivity `sigma`."""
    return length / (sigma * area)


def diffusion_coefficient(mu, v_t):
    """Einstein: D = V_T * mu, in m^2/s."""
    return mu * v_t


def diffusion_length(d, tau):
    """How far a minority carrier gets before it recombines, in metres."""
    return math.sqrt(d * tau)


def saturation_current(area, n_i, n_a, n_d, d_p, l_p, d_n, l_n):
    """The diode's I_S, in amps, from the two injected minority populations."""
    return (Q_ELECTRON * area * n_i * n_i
            * (d_p / (l_p * n_d) + d_n / (l_n * n_a)))


if __name__ == "__main__":
    n_i = 1.0e16
    mu_n, mu_p = 0.135, 0.048
    sigma = conductivity(1e22, n_i * n_i / 1e22, mu_n, mu_p)
    print("sigma:", sigma, "S/m")
    print("bar, 500 um long, 1e-8 m^2:", bar_resistance(sigma, 500e-6, 1e-8), "ohm")
    d_n = diffusion_coefficient(mu_n, V_T300)
    d_p = diffusion_coefficient(mu_p, V_T300)
    print("D_n:", d_n, " D_p:", d_p)
    l_n = diffusion_length(d_n, 1e-6)
    l_p = diffusion_length(d_p, 1e-6)
    print("L_n:", l_n, " L_p:", l_p)
    i_s = saturation_current(1e-8, n_i, 1e24, 1e22, d_p, l_p, d_n, l_n)
    print("I_S:", i_s, "A")
    if i_s > 0:
        print("V_F at 1 mA:", V_T300 * math.log(1.0 + 1e-3 / i_s), "V")
'''}],
                "hints": [
                    "`conductivity` is one line, but the minority term is not decoration: pass it the real $p = n_i^2/N_d$ and watch how little it contributes. That is what *majority* means, quantitatively.",
                    "`bar_resistance` is $L/(\\sigma A)$, not $\\sigma L/A$. A quick check: 216 S/m, 500 µm and $10^{-8}$ m$^2$ must give about 231 Ω, not about 0.0043 Ω.",
                    "`diffusion_coefficient` looks too small to be a function. It is the Einstein relation, and writing it down once is how you stop yourself dividing by $V_T$ later in a hurry.",
                    "`diffusion_length` is `math.sqrt(d * tau)`. With $D_p = 1.24\\times10^{-3}$ m$^2$/s and $\\tau = 1$ µs it comes to $3.5\\times10^{-5}$ m, which is 35 µm — comparable with the thickness of the silicon, which is why the geometry of a real diode matters.",
                    "In `saturation_current`, `n_i * n_i` beats `n_i ** 2` for nothing and both are fine; what matters is the pairing. `d_p` goes with `l_p` and `n_d`; `d_n` goes with `l_n` and `n_a`. The holes are injected into the n-side, so the n-side doping limits them.",
                ],
                "tests": [
                    {"name": "the conductivity and resistivity of doped silicon", "code": r'''
n_i = 1.0e16
s = conductivity(1e22, n_i * n_i / 1e22, 0.135, 0.048)
assert abs(s - 216.2938455900769) < 1e-9, f"expected 216.294 S/m, got {s}"
assert abs(1.0 / s - 0.0046233400551544766) < 1e-12, \
    f"the resistivity should be 4.6233e-3 ohm.m, got {1.0 / s}"
pure = conductivity(n_i, n_i, 0.135, 0.048)
assert abs(pure - 0.000293198324022) < 1e-15, \
    f"undoped silicon has both carriers at n_i and comes to 2.932e-4 S/m, got {pure}"
assert s / pure > 700000.0, \
    "one dopant atom in five million should raise the conductivity by nearly a million times"
'''},
                    {"name": "the bar, and how it scales with its own geometry", "code": r'''
s = 216.2938455900769
r = bar_resistance(s, 500e-6, 1e-8)
assert abs(r - 231.16700275772382) < 1e-9, f"expected 231.167 ohm, got {r}"
assert abs(bar_resistance(s, 1000e-6, 1e-8) - 2.0 * r) < 1e-9, \
    "twice as long is twice the resistance"
assert abs(bar_resistance(s, 500e-6, 2e-8) - 0.5 * r) < 1e-9, \
    "twice the cross section is half the resistance"
'''},
                    {"name": "Einstein, and the two diffusion coefficients it gives", "code": r'''
d_n = diffusion_coefficient(0.135, V_T300)
d_p = diffusion_coefficient(0.048, V_T300)
assert abs(d_n - 0.0034900199711687973) < 1e-15, f"expected 3.49002e-3 m^2/s, got {d_n}"
assert abs(d_p - 0.0012408959897489058) < 1e-15, f"expected 1.24090e-3 m^2/s, got {d_p}"
assert abs(d_n / 0.135 - d_p / 0.048) < 1e-15, \
    "D/mu must be the same number for both carriers, because that number is V_T"
'''},
                    {"name": "the diffusion lengths are tens of micrometres", "code": r'''
l_n = diffusion_length(0.0034900199711687973, 1e-6)
l_p = diffusion_length(0.0012408959897489058, 1e-6)
assert abs(l_n - 5.9076390979551186e-05) < 1e-15, f"expected 5.9076e-05 m, got {l_n}"
assert abs(l_p - 3.5226353625501824e-05) < 1e-15, f"expected 3.5226e-05 m, got {l_p}"
long_life = diffusion_length(0.0012408959897489058, 4e-6)
assert abs(long_life - 2.0 * l_p) < 1e-15, \
    "four times the lifetime is twice the length, because the walk is a square root"
'''},
                    {"name": "the saturation current of the module 1 junction", "code": r'''
d_n, d_p = 0.0034900199711687973, 0.0012408959897489058
l_n, l_p = 5.9076390979551186e-05, 3.5226353625501824e-05
i_s = saturation_current(1e-8, 1.0e16, 1e24, 1e22, d_p, l_p, d_n, l_n)
assert abs(i_s - 5.738534881228506e-16) < 1e-24, f"expected 5.7385e-16 A, got {i_s}"
import math
v = V_T300 * math.log(1.0 + 1e-3 / i_s)
assert abs(v - 0.7286748656801748) < 1e-9, \
    f"that I_S puts the forward drop at 1 mA at 0.72867 V, got {v}"
'''},
                    {"name": "heavier doping means a smaller I_S and a larger forward drop", "code": r'''
import math
d_n, d_p = 0.0034900199711687973, 0.0012408959897489058
l_n, l_p = 5.9076390979551186e-05, 3.5226353625501824e-05
base = saturation_current(1e-8, 1.0e16, 1e24, 1e22, d_p, l_p, d_n, l_n)
heavy = saturation_current(1e-8, 1.0e16, 1e24, 1e23, d_p, l_p, d_n, l_n)
assert abs(heavy - 6.590392200464875e-17) < 1e-25, f"expected 6.5904e-17 A, got {heavy}"
assert abs(base / heavy - 8.707425456141623) < 1e-9, \
    f"ten times the n-side doping divides I_S by 8.71, not by 10, because the p-side term does not move; got {base / heavy}"
step = V_T300 * math.log(1.0 + 1e-3 / heavy) - V_T300 * math.log(1.0 + 1e-3 / base)
assert abs(step - 0.05594828168665744) < 1e-9, \
    f"the forward drop should rise by 55.9 mV, got {step * 1000} mV"
'''},
                    {"name": "the lightly doped side dominates the injection", "code": r'''
d_n, d_p = 0.0034900199711687973, 0.0012408959897489058
l_n, l_p = 5.9076390979551186e-05, 3.5226353625501824e-05
hole_only = saturation_current(1e-8, 1.0e16, 1e24, 1e22, d_p, l_p, 0.0, l_n)
both = saturation_current(1e-8, 1.0e16, 1e24, 1e22, d_p, l_p, d_n, l_n)
assert hole_only / both > 0.98, \
    "with the p-side doped a hundred times harder, hole injection into the n-side is over 98% of I_S"
sym = saturation_current(1e-8, 1.0e16, 1e23, 1e23, d_p, l_p, d_n, l_n)
assert abs(sym - 1.5108965392828552e-16) < 1e-25, f"expected 1.5109e-16 A, got {sym}"
'''},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Temperature: two coefficients pulling opposite ways",
            "summary": "Everything in the diode equation moves with temperature, and the two things that move fastest send the forward voltage down while they send the reverse current up.",
            "concepts": [
                "$n_i^2 \\propto T^3e^{-E_g/kT}$, and $I_S \\propto n_i^2$, so the ideal saturation current climbs ferociously: a factor of **4.46 for every 10 K** near 300 K. That is not the number most data sheets quote, and both numbers are right — see below.",
                "The familiar rule that **leakage doubles every 10 °C** is about a different current. Measured reverse current in a real silicon diode is dominated by carriers *generated inside the depletion region*, and that goes as $n_i$ rather than $n_i^2$ — the square root of the diffusion scaling, and $\\sqrt{4.46} = 2.11$. One mechanism, two exponents, two rules of thumb that only look contradictory.",
                "At constant **current** the forward voltage falls, because $V = V_T\\ln(I/I_S)$ and $I_S$ climbs faster than $V_T$ does. The ideal model above gives $-1.56$ mV/K at 1 mA; real diodes measure about $-2$ mV/K, the difference being the band gap's own shrinkage with temperature which the model holds fixed. The coefficient is more negative at *lower* current — $-1.76$ mV/K at 100 µA against $-1.36$ mV/K at 10 mA — which is why a diode thermometer is biased at a low, and above all a *constant*, current.",
                "Dissipation raises the junction above ambient by $T_J = T_A + \\theta_{JA}P$. A bridge delivering 1.0 A DC puts 0.5 A average through each diode, and at 0.85 V that is 0.425 W each; on a 100 K/W package in a 45 °C cabinet the junction sits at 87.5 °C. Nothing on the outside of the part is anywhere near that.",
                "Drive a diode from a **voltage** instead and the loop closes: more temperature gives more current, more current gives more power, more power gives more temperature. For the device in module 5 on 100 K/W the loop converges at 0.84 V and runs away at 0.85 V. The same feedback is why paralleled diodes need ballast resistors: at a shared voltage, the one that is 5 °C hotter takes 47% more of the current, and pulls further ahead.",
            ],
            "read": [
                {
                    "title": "Two coefficients, one sign each, and the loop that closes",
                    "minutes": 13,
                    "body": r'''
Characterise a diode on a cold bench in January and it drops 0.73 V at 1 mA. Put the same
part in a sealed enclosure in July, still at 1 mA, and it drops 0.65 V. Nothing broke.
Nothing drifted. The forward voltage of a diode is a function of two variables and you
only controlled one of them.

Everything else about a hot semiconductor gets *bigger* — the leakage, the intrinsic
carrier concentration, the thermal voltage itself. The forward drop is the one quantity
that goes the other way, and the reason is worth deriving rather than memorising, because
the derivation also tells you the size of the effect and why it depends on the current
you happened to measure at.

## Everything moves, but $I_S$ moves fastest

Two temperature-dependent quantities sit in the diode equation. The first is honest and
slow:

$$V_T = \frac{kT}{q} \qquad \frac{dV_T}{dT} = \frac{k}{q} = 86.2\ \mu\text{V/K}$$

Room temperature to boiling moves it by 6 mV. The second is not slow at all. From module
5, $I_S \propto n_i^2$ and $n_i^2 \propto T^3e^{-E_g/kT}$, so

$$\frac{I_S(T_2)}{I_S(T_1)} = \left(\frac{T_2}{T_1}\right)^{3}
\exp\!\left[\frac{E_g}{k}\left(\frac{1}{T_1} - \frac{1}{T_2}\right)\right]$$

Put in silicon's numbers for a 10 K step from 300 K. With $E_g = 1.12$ eV,
$E_g/k = 12996$ K:

```text
cube of the ratio      (310/300)^3                        = 1.1034
Boltzmann ratio        exp[12996 x (1/300 - 1/310)]
                       = exp[12996 x 1.0753e-4] = exp(1.3975) = 4.0448
product                                                    = 4.463
```

**A factor of 4.46 for every 10 K.** The cube contributes almost nothing; nearly all of it
is the exponential, which is to say nearly all of it is the band gap.

## Why the forward voltage falls, and by exactly how much

At a *fixed current*, $V = V_T\ln(I/I_S)$ with both $V_T$ and $I_S$ moving. Differentiate
properly. Take logarithms of $I = I_S(T)e^{qV/kT}$ at constant $I$:

$$0 = \frac{3}{T} + \frac{E_g}{kT^2} + \frac{q}{k}\frac{d}{dT}\!\left(\frac{V}{T}\right)$$

Expand the last derivative and multiply through by $kT^2/q$:

$$0 = 3V_T + V_{G0} + T\frac{dV}{dT} - V
\qquad\Longrightarrow\qquad
\boxed{\frac{dV}{dT} = \frac{V - V_{G0} - 3V_T}{T}}$$

where $V_{G0} = E_g/q = 1.12$ V. Everything about the temperature coefficient is in that
one line. The forward voltage falls because it sits *below* the band-gap voltage, and the
coefficient is proportional to how far below.

Try it on the device module 5 built — $I_S = 5.74\times10^{-16}$ A at 300 K, which sits a
little higher up the voltage axis than module 2's part because its $I_S$ is smaller:

```text
current    V_F at 300 K    (V_F - 1.12 - 0.0776)/300      quoted
  100 uA      0.6692 V           -1.761 mV/K              -1.76
    1 mA      0.7286 V           -1.563 mV/K              -1.56
   10 mA      0.7882 V           -1.365 mV/K              -1.36
```

The three numbers the concept list quotes, all out of one formula, and the trend explained
in a sentence: $V_{G0}$ and $3V_T$ are fixed, so the *only* thing that changes across
those rows is $V_F$ — and a smaller current means a smaller $V_F$, which means further to
fall. That is why a diode thermometer is biased at a low current, and why the bias must
be *constant*: the coefficient you calibrated is only valid at the current you calibrated
it at.

Real diodes measure nearer $-2$ mV/K. The gap is $E_g$ itself, which shrinks by about
0.25 eV per 1000 K and which this model holds fixed. The model gets the mechanism and the
trend exactly right and the magnitude about 20% light.

## The two rules for leakage that look contradictory

A data sheet says reverse leakage doubles every 10 °C. The model above says $I_S$ rises
4.46 times every 10 K. Both are right, and they are about different currents.

$I_S$ is the *diffusion* current — minority carriers that wander in from the neutral
regions — and it carries $n_i^2$. But a real reverse-biased junction has a second source:
electron-hole pairs **generated inside the depletion region itself**, which never had to
diffuse anywhere. That generation rate goes as $n_i$, not $n_i^2$, so its temperature
factor is the square root of the other one:

$$\sqrt{4.46} = 2.11 \approx 2$$

One mechanism scales as the square of the other, so their rules of thumb differ by a
square root. In silicon at room temperature the generation term is the larger of the two
by orders of magnitude, so a data sheet quotes the doubling, because that is what a meter
measures. Heat the part far enough and the $n_i^2$ term overtakes the $n_i$ term, and the
doubling rule quietly turns into a quadrupling rule.

## Worked example: where the junction of a bridge rectifier actually sits

Module 3's supply, scaled up: a bridge delivering 1.0 A DC, in a 45 $^\circ$C cabinet,
each diode in a package with $\theta_{JA} = 100$ K/W and a data-sheet drop of 0.85 V at
0.5 A, quoted at 25 $^\circ$C.

**First pass.** Each diode conducts on alternate half-cycles, so it carries 0.5 A average:

$$P = 0.5 \times 0.85 = 0.425\ \text{W}
\qquad T_J = 45 + 100\times0.425 = 87.5\ ^\circ\text{C}$$

**Second pass, because $V_F$ is not 0.85 V at 87.5 $^\circ$C.** It has fallen by about
2 mV/K over the rise above the 25 $^\circ$C it was quoted at, so the answer feeds back into
its own input. Write it as one equation and solve it once:

$$T_J = 45 + 100\times0.5\times V_F, \qquad V_F = 0.85 - 0.002\,(T_J - 25)$$
$$T_J = 45 + 50\,(0.90 - 0.002\,T_J) = 90 - 0.1\,T_J
\qquad\Longrightarrow\qquad T_J = 81.8\ ^\circ\text{C}$$

with $V_F = 0.736$ V and $P = 0.368$ W. Cooler than the first pass, and cooler is the
important word: **at constant current the thermal feedback is negative.** The loop gain is
the $-0.1$ sitting in front of $T_J$ — heating lowers the drop, which lowers the power,
which limits the heating. The circuit stabilises itself.

Note what the answer depends on. 82 $^\circ$C in a 45 $^\circ$C cabinet, against a junction
limit of typically 125 $^\circ$C, from 0.37 W in a small package. Nothing on the outside of
that part is anywhere near 82 $^\circ$C, which is why derating curves start sloping down
long before the maximum ambient.

## The same loop, with the sign reversed

Now drive the diode from a voltage source instead. At fixed $V$, differentiate
$\ln I = \ln I_S(T) + qV/kT$ with respect to $T$:

$$\frac{1}{I}\frac{dI}{dT} = \frac{3V_T + V_{G0} - V}{V_T\,T}$$

At $V = 0.85$ V and $T = 300$ K that is $(0.0776 + 1.12 - 0.85)/(0.02585\times300)
= 0.0448$ per kelvin — the current rises **4.5% for every kelvin**. The power rises with
it, and the power is what produced the kelvin. The loop gain is

$$G = \theta_{JA}\,\frac{dP}{dT} = \theta_{JA}\,P \times 0.0448$$

and the device runs away when $G \ge 1$, which on a 100 K/W package means a critical
dissipation of about $1/(100\times0.0448) = 0.22$ W. Below that the loop converges to a
finite temperature; above it there is no solution and the junction climbs until something
gives.

The lab, **The two coefficients, and the loop that runs away**, iterates that loop until
it settles or gives up, and finds the boundary between **0.84 V and 0.85 V** on this
package.
Ten millivolts is a startlingly narrow window for the difference between "warm" and
"destroyed", and the reason is module 2's exponential: 10 mV at 300 K multiplies the
current, and therefore the dissipation, and therefore the loop gain, by
$e^{0.010/0.02585} = 1.47$. One 10 mV step moves the loop gain by nearly half. There is no
gentle approach to thermal runaway.

## The mistake people actually make

Paralleling devices to share current. It is the obvious move — two diodes, half the
current each, half the heat each — and it does the opposite of what it promises.

Parallel parts share a *voltage*, not a current, and at a shared voltage the split is set
by an exponential. Suppose one runs 5 K hotter, which at $-2$ mV/K shifts its curve by
10 mV. The current ratio is $e^{0.010/0.025852} = 1.47$: the hotter one takes 47% more,
dissipates 47% more, gets hotter still, and takes more again. The feedback is positive and
it does not need a temperature difference to start — a 10 mV manufacturing spread does
just as well, as module 10's two LEDs demonstrate.

The fix is a ballast resistor in series with each device, chosen so that its drop is large
compared with 10 mV. A 10 mV offset moves the split by roughly $\Delta V/(r_d + R_b)$, so
for two diodes at 0.5 A each, where $r_d = V_T/I = 0.052\ \Omega$:

```text
no ballast          10 mV / 0.052 ohm  = 193 mA of imbalance on 500 mA   (39%)
R_b = 0.1 ohm       10 mV / 0.152 ohm  =  66 mA                          (13%)
R_b = 0.5 ohm       10 mV / 0.552 ohm  =  18 mA                          (3.6%)
```

A 0.5 $\Omega$ ballast carrying 0.5 A drops a quarter of a volt across itself and burns
$I^2R = 0.125$ W doing it, which is the price of the sharing being real — and it is
roughly a third of what the diode it is protecting dissipates.

## Where this stops holding

- **$-2$ mV/K is a linearisation.** The coefficient is itself a function of temperature and
  of current, as the boxed formula makes explicit. Over a 100 K swing, using a single
  number introduces several millivolts of error — usually irrelevant, but not in a
  thermometer, which is the one application that cares.
- **$\theta_{JA}$ is not a property of the part.** It is a property of the part, the board,
  the copper attached to it, the airflow and the neighbours. A data-sheet figure assumes a
  specified test board, and a real one can be twice as good or twice as bad.
- **The lumped thermal model has no time in it.** $T_J = T_A + \theta_{JA}P$ is the steady
  state. A surge lasting less than the junction's thermal time constant — milliseconds for
  a small die — is limited by heat capacity, not by $\theta_{JA}$, which is exactly why a
  rectifier survives module 3's switch-on inrush.
- **The runaway threshold above is for one package in one ambient.** The criterion
  $\theta_{JA}P \times d(\ln I)/dT \ge 1$ is general; the 0.84 V is not. Halve the thermal
  resistance and the threshold moves by roughly $V_T\ln 2 = 18$ mV.
''',
                },
            ],
            "quiz": {
                "title": "What the temperature does, and to which quantity",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A silicon diode drops 0.65 V at 1 mA at 25 °C. At the same 1 mA, roughly what does it drop at 85 °C?",
                        "opts": ["0.77 V", "0.65 V", "0.53 V", "0.41 V"],
                        "a": 2,
                        "why": r'''
About $-2$ mV per degree over 60 degrees is $-120$ mV, so 0.65 V becomes 0.53 V. The
sign catches people out because everything else about a hot semiconductor gets bigger:
the leakage rises, the intrinsic carrier concentration rises, $V_T$ itself rises. The
forward drop is the one that falls, and it falls because $I_S$ in the denominator of
$\ln(I/I_S)$ is growing much faster than the $V_T$ in front of the logarithm.
''',
                    },
                    {
                        "q": "A data sheet says the reverse leakage doubles every 10 °C. Module 5's model says the saturation current rises by a factor of 4.5 every 10 K. Which is right?",
                        "opts": [
                            "only one can be — the doubling is a rule of thumb and the factor of 4.5 is the truth",
                            "both, because they describe different currents: measured leakage is dominated by generation inside the depletion region, which follows $n_i$, while the ideal saturation current follows $n_i^2$",
                            "both, because one is quoted per 10 °C and the other per 10 K",
                            "neither — reverse current does not depend on temperature",
                        ],
                        "a": 1,
                        "why": r'''
Two mechanisms with two different powers of $n_i$. The diffusion current that the
Shockley equation describes carries $n_i^2$; the generation current from carriers
created inside the depletion region carries $n_i$, so its temperature factor is the
square root of the other one — and $\sqrt{4.46} = 2.11$, which is where the doubling
rule comes from. In a real silicon diode at room temperature the generation term is
the larger of the two, so a data sheet quotes what it measures. Choosing the answer
about °C and K is a trap: a ten-degree *interval* is the same size in both scales.
''',
                    },
                    {
                        "q": "A diode dissipates 0.6 W in a package with $\\theta_{JA} = 100$ K/W, in a 40 °C cabinet. Where is the junction?",
                        "opts": ["60 °C", "160 °C", "100 °C", "640 °C"],
                        "a": 2,
                        "why": r'''
$T_J = T_A + \theta_{JA}P = 40 + 100 \times 0.6 = 100$ °C. The rise is 60 degrees and
the ambient is 40, and forgetting to add the ambient — answering 60 °C — is the error
that puts a part inside its rating on paper and outside it on the bench. Note how
little power it takes: 0.6 W in a small package is most of the way to a 125 °C limit
before the cabinet has warmed up at all, which is why derating curves start sloping
downwards well below the maximum ambient.
''',
                    },
                    {
                        "q": "Two identical diodes are wired in parallel to share a load. One sits 5 °C hotter than the other. At the voltage they necessarily share, how much current does the hotter one take?",
                        "opts": [
                            "the same, since they are identical parts",
                            "about 2% more",
                            "about 10% more",
                            "about 47% more",
                        ],
                        "a": 3,
                        "why": r'''
Five degrees moves the forward characteristic by about 10 mV, and at a shared voltage
that is a current ratio of $e^{0.010/0.025852} = 1.47$. The hotter diode takes half as
much again, dissipates half as much again, and gets hotter still. Parallel diodes are
not a way to share current, they are a way to concentrate it — which is why every
practical arrangement puts a small ballast resistor in series with each one, chosen so
that its drop is large compared with 10 mV.
''',
                    },
                    {
                        "q": "Why is a diode never driven straight from a voltage source?",
                        "opts": [
                            "because the current is exponential in the voltage and rises with temperature at a fixed voltage, so dissipation and temperature drive each other with nothing to stop them",
                            "because a voltage source cannot supply enough current",
                            "because the diode would be reverse biased",
                            "because the forward voltage is not defined below 0.7 V",
                        ],
                        "a": 0,
                        "why": r'''
At a fixed current the feedback is negative: heating lowers the drop, which lowers the
power. At a fixed *voltage* it is positive: heating raises $I_S$, which raises the
current, which raises the power, which raises the temperature. Whether it settles or
not is a question of loop gain, and for the device modelled in this course on a
100 K/W package the answer changes between 0.84 V and 0.85 V. A series resistor — or
any current-limiting element at all — turns the sign of the feedback round, which is
why every diode in this course has had one.
''',
                    },
                    {
                        "q": "The $-2$ mV/K figure is always quoted at a stated current. Measured at 10 µA rather than 10 mA, the coefficient is:",
                        "opts": [
                            "less negative, about $-1.0$ mV/K",
                            "unchanged — it is a property of silicon",
                            "more negative, about $-2.0$ mV/K",
                            "positive, because low currents reverse the effect",
                        ],
                        "a": 2,
                        "why": r'''
More negative. The coefficient is set by how far the forward voltage sits *below* the
band gap, and at a smaller current it sits further below, so there is more distance to
fall. The model in this module gives $-1.36$ mV/K at 10 mA, $-1.56$ at 1 mA and
$-1.76$ at 100 µA, and the trend continues. It is not a defect: a band-gap reference
exploits exactly this by summing a $V_{BE}$ that falls with temperature and a
difference of two $V_{BE}$s that rises, and the currents at which each is taken are
part of the design.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The self-heating loop, line by line",
                "minutes": 9,
                "caption": "runaway.py — one iteration, four holes",
                "lang": "python",
                "brief": r"""
Thermal runaway is not a special mode a device enters; it is an ordinary fixed-point
iteration that sometimes fails to converge. Each pass takes a temperature, works out
what the diode does at that temperature, and works out what that does to the
temperature. Fill the four holes and the loop is the whole story.

Nothing is executed here — you are choosing expressions, not writing code.
""",
                "listing": """# Junction temperature when a diode's own dissipation warms it.
#   I_S0   saturation current at 300 K        V      the applied forward voltage
#   E_g    band gap in joules                 theta  junction-to-ambient K/W
#   k, q   Boltzmann's constant and the electronic charge

T = T_amb
repeat until T stops moving:
    V_T = ___                          # the thermal voltage AT THIS temperature
    I_S = I_S0 * (T / 300.0)**3 * exp(___)
    I   = I_S * (exp(V / V_T) - 1.0)
    P   = ___
    T   = T_amb + ___
""",
                "blanks": [
                    {
                        "prompt": "The thermal voltage is not a constant here.",
                        "hole": "?",
                        "opts": ["k * 300.0 / q", "k * T / q", "q * T / k", "k * T_amb / q"],
                        "a": 1,
                        "why": "`k * T / q`, evaluated at the current guess. Freezing it at 300 K or at ambient removes one of the two things temperature does to the diode, and the loop then converges when it should not.",
                        "whys": [
                            "Freezing $V_T$ at its 300 K value removes one of the two temperature effects. The remaining one, $I_S$, still drives the loop, so the code appears to work — it just gives the wrong threshold.",
                            "`k * T / q`, evaluated at the current guess. Both $V_T$ and $I_S$ have to be re-evaluated every pass, because both of them are what the temperature is changing.",
                            "Inverted. $kT$ is an energy and dividing it by a charge gives a voltage; dividing a charge by an energy gives something with no meaning here, and a number around $10^{22}$.",
                            "Ambient never changes during the iteration, so this is the same mistake as pinning it at 300 K with an extra step of indirection.",
                        ],
                    },
                    {
                        "prompt": "How the saturation current scales from its 300 K value up to T.",
                        "hole": "?",
                        "opts": [
                            "(E_g / k) * (1.0 / T - 1.0 / 300.0)",
                            "-E_g / (k * T)",
                            "(E_g / k) * (1.0 / 300.0 - 1.0 / T)",
                            "(E_g / k) * (T - 300.0)",
                        ],
                        "a": 2,
                        "why": "The ratio of two Boltzmann factors is $e^{-E_g/kT}/e^{-E_g/k\\cdot300}$, which is $\\exp[(E_g/k)(1/300 - 1/T)]$. For $T$ above 300 that bracket is positive, so $I_S$ grows — as it must.",
                        "whys": [
                            "The sign is inverted, so the model has the saturation current *falling* as the device heats. Every conclusion in this module then comes out backwards, including the sign of the forward temperature coefficient.",
                            "That is the absolute Boltzmann factor, not the ratio of two of them. Used here it multiplies $I_{S0}$ by about $e^{-43}$ and the current vanishes; the reference value already contains that factor at 300 K.",
                            "The ratio of two Boltzmann factors is $\\exp[(E_g/k)(1/300 - 1/T)]$, positive above 300 K, so $I_S$ grows with temperature. This is where the factor of 4.5 per 10 K comes from.",
                            "Linear in $T$ rather than in $1/T$. It gives roughly the right answer within a degree or two of 300 K and diverges wildly outside that, which is the worst kind of wrong.",
                        ],
                    },
                    {
                        "prompt": "The power the junction has to get rid of.",
                        "hole": "?",
                        "opts": ["I * I * theta", "V * I", "V * V / I", "I / V"],
                        "a": 1,
                        "why": "Volts times amps. The diode is not a resistor, so $I^2R$ and $V^2/R$ have no meaning for it — there is no single $R$ to put in them. The product of the terminal voltage and the terminal current always works.",
                        "whys": [
                            "$I^2$ times a thermal resistance mixes two unrelated quantities and does not even have units of watts.",
                            "Volts times amps, which is the definition and needs no model of the device. The $I^2R$ and $V^2/R$ forms are shortcuts that assume the two are proportional, and here they are exponentially related instead.",
                            "$V^2/R$ requires an $R$, and a diode's static and dynamic resistances are different numbers, neither of which belongs here. Module 2 is about exactly this confusion.",
                            "Not a power at all — amps over volts is a conductance. It happens to produce a small number, which is why a loop written this way looks stable and proves nothing.",
                        ],
                    },
                    {
                        "prompt": "And what that dissipation does to the junction temperature.",
                        "hole": "?",
                        "opts": ["theta * P", "P / theta", "theta / P", "theta * P / T_amb"],
                        "a": 0,
                        "why": "$\\theta$ is a rise per watt, so the rise is $\\theta P$ and the junction sits at $T_{amb} + \\theta P$. It is Ohm's law with kelvin for volts and watts for amps, which is why the same solver draws both.",
                        "whys": [
                            "$\\theta$ is kelvin per watt, so watts times $\\theta$ is kelvin. A 100 K/W package dissipating 0.425 W runs 42.5 K above whatever is around it.",
                            "Dividing by the thermal resistance makes a *better* heatsink give a *hotter* junction, which is the opposite of the whole reason to fit one.",
                            "Upside down twice over: the units come out as K/W², and doubling the dissipation would cool the part.",
                            "Ambient temperature does not scale the rise. A part dissipating 0.425 W on 100 K/W runs 42.5 K hot in a cold room and 42.5 K hot in a warm one; what changes is where that rise starts from.",
                        ],
                    },
                ],
            },
            "build": {
                "title": "A hundred nanoamps that ruins a reference",
                "minutes": 26,
                "brief": r'''
Reverse leakage is a few nanoamps at room temperature and nobody thinks about it. At
85 °C it is a hundred times that, and it is still only a hundred nanoamps — which
sounds harmless right up to the moment it meets a high-impedance node.

## The circuit

A 10 V rail has to produce a **5.00 V reference** through a two-resistor divider. A
protection diode hangs off that reference node; it is reverse biased and does nothing
except leak, and at the top of the temperature range it leaks **100 nA** out of the
node. That leakage is already on the canvas as a current source, drawn pulling current
out of the node, because that is what it does.

## The specification

- the reference must land between **4.95 V and 5.05 V** with the leak flowing
- the divider must draw no more than **25 µA** from the 10 V rail
- the two resistors must be **equal to within 2%**

## Why the last one is not pedantry

The obvious cheat is to skew the ratio upwards until the leak drags the node back to
exactly 5.000 V. It works, at one temperature. Leakage falls by a factor of about two
for every 10 °C the part cools, so a divider trimmed at 85 °C is trimmed for a leak
that has all but vanished by 25 °C, and the reference is then high by the whole amount
you compensated. The fix is not to cancel the error but to make it small, and the only
lever for that is impedance.

## The arithmetic

Superposition. The divider on its own gives $10R_2/(R_1+R_2)$. The leak on its own,
looking into a dead network, sees $R_1 \parallel R_2$ and pulls the node down by
$I_{leak}(R_1\parallel R_2)$. With equal resistors of value $R$ that is
$5.00 - 10^{-7}R/2$ volts, and the rail current is about $10/2R$. One constraint
pushes $R$ down, the other pushes it up, and the window between them is wide — which
is the useful thing to know about it.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p5", "kind": "I", "x": 17, "y": 9, "rot": 1, "value": 1e-7},
                        {"id": "p6", "kind": "GND", "x": 17, "y": 11},
                        {"id": "p7", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [11, 8], "b": [17, 8]},
                        {"a": [17, 10], "b": [17, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 500000},
                        {"id": "p3", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 500000},
                        {"id": "p4", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p5", "kind": "I", "x": 17, "y": 9, "rot": 1, "value": 1e-7},
                        {"id": "p6", "kind": "GND", "x": 17, "y": 11},
                        {"id": "p7", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [17, 8]},
                        {"a": [13, 10], "b": [13, 11]},
                        {"a": [17, 10], "b": [17, 11]},
                    ],
                },
                "checks": [
                    {"name": "one rail, two resistors, and the leak still connected", "code": r'''
const leak = c.net.parts.filter(function (p) { return p.kind === 'I'; });
c.assert(leak.length === 1,
  'Exactly one current source: the junction leakage. Found ' + leak.length +
  '. Deleting it makes the circuit pass and the reference fail on the bench.');
c.close(Math.abs(leak[0].value), 100e-9, 0.02, 'the leakage current');
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 10) < 0.5; });
c.assert(sup.length === 1, 'Exactly one 10 V rail; found ' + sup.length + '.');
c.assert(c.count('R') === 2,
  'Two resistors and only two — this is a divider with a leak hanging off it, not a ' +
  'network. Found ' + c.count('R') + '.');
'''},
                    {"name": "the reference lands between 4.95 V and 5.05 V with the leak flowing", "code": r'''
const v = c.vout();
c.assert(v >= 4.95 * 0.9995 && v <= 5.05 * 1.0005,
  'The reference is at ' + c.fmt(v, 'V') + ', outside the 4.95 V to 5.05 V window. ' +
  'The leak pulls the node down by 100 nA times the parallel combination of the two ' +
  'resistors, so bringing that combination down is the only thing that helps.');
'''},
                    {"name": "and it does it on no more than 25 microamps", "code": r'''
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 10) < 0.5; })[0];
const i = Math.abs(c.dc().currents[sup.id]);
c.assert(i > 1e-6,
  'The 10 V rail is delivering ' + c.fmt(i, 'A') + '. Until both resistors are in ' +
  'place there is no divider to measure.');
c.assert(i <= 25e-6 * 1.01,
  'The divider is drawing ' + c.fmt(i, 'A') + ', over the 25 uA budget. Every ohm you ' +
  'remove to fight the leak is current you spend permanently, and this is a reference ' +
  'that has to sit there being right for years.');
'''},
                    {"name": "the ratio is still one to one, so the leak was made small rather than cancelled", "code": r'''
const rs = c.values('R');
c.assert(rs.length === 2, 'Two resistors expected; found ' + rs.length + '.');
const hi = Math.max(rs[0], rs[1]), lo = Math.min(rs[0], rs[1]);
c.assert(hi / lo <= 1.02,
  'The two resistors are ' + c.fmt(lo, 'ohm') + ' and ' + c.fmt(hi, 'ohm') + ', a ratio ' +
  'of ' + (hi / lo).toFixed(3) + '. Skewing the ratio to cancel the leak lands the node ' +
  'on 5.000 V at one temperature and leaves it high everywhere colder, because the leak ' +
  'halves for every 10 degrees. Make the error small instead of cancelling it.');
'''},
                ],
                "hints": [
                    "Start from the two constraints. Equal resistors of value $R$ give $5.00 - 10^{-7}R/2$ volts, so 50 mV of droop is reached at $R = 1\\ \\mathrm{M}\\Omega$; and the rail current is about $10/2R$, so 25 µA is reached at $R = 200\\ \\mathrm{k}\\Omega$. Anything between works.",
                    "500 kΩ each is the comfortable middle: the node lands at 4.975 V and the rail supplies 10.05 µA. Type `500k` for each.",
                    "Lay it out exactly like the Zener regulator of module 4: the upper resistor from the rail down to the probed node, the lower one from that node down to its own ground.",
                    "If the reference comes out at 5.000 V exactly, check the ratio. Landing on the nominal value is a warning sign here, not a success — the leak is real and it has to show up somewhere.",
                ],
            },
            "lab": {
                "title": "The two coefficients, and the loop that runs away",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Four functions. The first three are the temperature model; the fourth closes the loop
and finds out whether it settles.

- `saturation_current(i_s_ref, t_ref, t)` scales $I_S$ from its value at `t_ref` to
  its value at `t`:

```text
i_s_ref * (t / t_ref)**3 * exp( (E_GAP * Q / K) * (1/t_ref - 1/t) )
```

  where `E_GAP` is in electronvolts, so multiplying by `Q` turns it into joules.

- `forward_voltage(i, i_s, t)` returns $V_T(T)\ln(1 + I/I_S)$ — and $V_T$ has to be
  computed at `t`, not at 300 K.
- `temperature_coefficient(i, i_s_ref, t_ref, t)` returns $dV_F/dT$ in volts per
  kelvin, by central difference with a step of **exactly 0.5 K**: evaluate
  `forward_voltage` at `t + 0.5` and at `t - 0.5`, each with its own scaled `i_s`, and
  divide the difference by 1.0.
- `settle(v_bias, i_s_ref, t_amb, theta, iters=200)` iterates the self-heating loop
  from the blanks exercise, starting at `t = t_amb`, doing `iters` passes:

```text
i_s = saturation_current(i_s_ref, 300.0, t)
i   = i_s * expm1(v_bias / thermal_voltage(t))
t   = t_amb + theta * v_bias * i
if t is not finite or t > 1000.0:  return float("inf")
```

  Return the temperature it converged to, or `float("inf")` if it did not. Use
  `math.expm1`, which is $e^x - 1$ computed accurately; at these arguments it makes no
  visible difference, but it is the right function for the job.

Everything is in kelvin. `K_BOLTZMANN`, `Q_ELECTRON` and `E_GAP` are given.
''',
                "files": [{"name": "main.py", "content": r'''
"""What temperature does to a diode, and the loop that closes on itself."""

import math

K_BOLTZMANN = 1.380649e-23
Q_ELECTRON = 1.602176634e-19
E_GAP = 1.12                             # eV, silicon at room temperature


def thermal_voltage(t):
    """kT/q at t kelvin, in volts."""
    return K_BOLTZMANN * t / Q_ELECTRON


def saturation_current(i_s_ref, t_ref, t):
    """I_S at t kelvin, given its value at t_ref."""
    # TODO: the cube of the temperature ratio times the Boltzmann ratio.
    return 0.0


def forward_voltage(i, i_s, t):
    """Forward drop at current i, with saturation current i_s, at t kelvin."""
    # TODO: V_T at THIS temperature, times log(1 + i/i_s).
    return 0.0


def temperature_coefficient(i, i_s_ref, t_ref, t):
    """dV_F/dT in volts per kelvin at a fixed current, by central difference."""
    # TODO: half a kelvin either side, each with its own scaled i_s.
    return 0.0


def settle(v_bias, i_s_ref, t_amb, theta, iters=200):
    """Junction temperature under self-heating, or inf if it runs away."""
    t = t_amb
    # TODO: the loop from the brief.
    return t


if __name__ == "__main__":
    i_s = 5.738534881228506e-16
    print("I_S ratio over 10 K at 300 K:", saturation_current(1.0, 300.0, 310.0))
    for t in (273.15, 300.0, 358.15):
        scaled = saturation_current(i_s, 300.0, t)
        print("  T =", t, " I_S =", scaled,
              " V_F at 1 mA =", forward_voltage(1e-3, scaled, t))
    for cur in (1e-4, 1e-3, 1e-2):
        print("  dV_F/dT at", cur, "A:", temperature_coefficient(cur, i_s, 300.0, 300.0))
    for v in (0.70, 0.84, 0.85):
        print("  bias", v, "V settles at", settle(v, i_s, 300.0, 100.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""What temperature does to a diode, and the loop that closes on itself."""

import math

K_BOLTZMANN = 1.380649e-23
Q_ELECTRON = 1.602176634e-19
E_GAP = 1.12                             # eV, silicon at room temperature


def thermal_voltage(t):
    """kT/q at t kelvin, in volts."""
    return K_BOLTZMANN * t / Q_ELECTRON


def saturation_current(i_s_ref, t_ref, t):
    """I_S at t kelvin, given its value at t_ref."""
    return (i_s_ref * (t / t_ref) ** 3
            * math.exp((E_GAP * Q_ELECTRON / K_BOLTZMANN) * (1.0 / t_ref - 1.0 / t)))


def forward_voltage(i, i_s, t):
    """Forward drop at current i, with saturation current i_s, at t kelvin."""
    return thermal_voltage(t) * math.log(1.0 + i / i_s)


def temperature_coefficient(i, i_s_ref, t_ref, t):
    """dV_F/dT in volts per kelvin at a fixed current, by central difference."""
    h = 0.5
    hi = forward_voltage(i, saturation_current(i_s_ref, t_ref, t + h), t + h)
    lo = forward_voltage(i, saturation_current(i_s_ref, t_ref, t - h), t - h)
    return (hi - lo) / (2.0 * h)


def settle(v_bias, i_s_ref, t_amb, theta, iters=200):
    """Junction temperature under self-heating, or inf if it runs away."""
    t = t_amb
    for _ in range(iters):
        i_s = saturation_current(i_s_ref, 300.0, t)
        i = i_s * math.expm1(v_bias / thermal_voltage(t))
        t = t_amb + theta * v_bias * i
        if not math.isfinite(t) or t > 1000.0:
            return float("inf")
    return t


if __name__ == "__main__":
    i_s = 5.738534881228506e-16
    print("I_S ratio over 10 K at 300 K:", saturation_current(1.0, 300.0, 310.0))
    for t in (273.15, 300.0, 358.15):
        scaled = saturation_current(i_s, 300.0, t)
        print("  T =", t, " I_S =", scaled,
              " V_F at 1 mA =", forward_voltage(1e-3, scaled, t))
    for cur in (1e-4, 1e-3, 1e-2):
        print("  dV_F/dT at", cur, "A:", temperature_coefficient(cur, i_s, 300.0, 300.0))
    for v in (0.70, 0.84, 0.85):
        print("  bias", v, "V settles at", settle(v, i_s, 300.0, 100.0))
'''}],
                "hints": [
                    "In `saturation_current`, `E_GAP * Q_ELECTRON / K_BOLTZMANN` is a temperature, and it is close to 13000 K. If you get a number near $1.4\\times10^{-42}$ the charge and the constant have swapped places.",
                    "The bracket is `1/t_ref - 1/t`, in that order. Get it the other way round and the model has diodes leaking *less* when they are hot, which is wrong in a way that every later test will notice.",
                    "`forward_voltage` must call `thermal_voltage(t)`. Using the 300 K value there is the single most common mistake in this lab and it changes the temperature coefficient by about a third.",
                    "For `temperature_coefficient` the step is exactly 0.5 K either side, so the divisor is 1.0. Both evaluations need their *own* `saturation_current` call — the whole coefficient comes from $I_S$ moving.",
                    "In `settle`, test for runaway inside the loop and return `float('inf')` immediately. Left to run, the exponential overflows and Python raises rather than returning anything.",
                ],
                "tests": [
                    {"name": "the saturation current climbs by four and a half per ten kelvin", "code": r'''
r = saturation_current(1.0, 300.0, 310.0)
assert abs(r - 4.4633644098905) < 1e-9, f"expected a ratio of 4.46336, got {r}"
assert abs(saturation_current(1.0, 300.0, 300.0) - 1.0) < 1e-12, \
    "scaling from 300 K to 300 K must change nothing"
hot = saturation_current(5.738534881228506e-16, 300.0, 398.15)
assert abs(hot / 5.831791835649743e-11 - 1.0) < 1e-9, f"expected 5.8318e-11 A at 125 C, got {hot}"
assert saturation_current(1.0, 300.0, 350.0) / 1.0 > 100.0, \
    "fifty kelvin should be worth more than two orders of magnitude"
'''},
                    {"name": "the forward voltage falls as the junction warms", "code": r'''
i_s = 5.738534881228506e-16
cold = forward_voltage(1e-3, saturation_current(i_s, 300.0, 273.15), 273.15)
room = forward_voltage(1e-3, saturation_current(i_s, 300.0, 300.0), 300.0)
hot = forward_voltage(1e-3, saturation_current(i_s, 300.0, 358.15), 358.15)
assert abs(cold - 0.7703194004172075) < 1e-9, f"expected 0.770319 V at 0 C, got {cold}"
assert abs(room - 0.7286748656801748) < 1e-9, f"expected 0.728675 V at 300 K, got {room}"
assert abs(hot - 0.6364190823514099) < 1e-9, f"expected 0.636419 V at 85 C, got {hot}"
assert cold > room > hot, "the drop must fall monotonically as the junction heats"
'''},
                    {"name": "the coefficient, and how it moves with bias current", "code": r'''
i_s = 5.738534881228506e-16
a = temperature_coefficient(1e-4, i_s, 300.0, 300.0)
b = temperature_coefficient(1e-3, i_s, 300.0, 300.0)
d = temperature_coefficient(1e-2, i_s, 300.0, 300.0)
assert abs(a - -0.0017613584236627622) < 1e-9, f"expected -1.7614 mV/K at 100 uA, got {a * 1000} mV/K"
assert abs(b - -0.0015629369925760361) < 1e-9, f"expected -1.5629 mV/K at 1 mA, got {b * 1000} mV/K"
assert abs(d - -0.0013645155614703253) < 1e-9, f"expected -1.3645 mV/K at 10 mA, got {d * 1000} mV/K"
assert a < b < d < 0.0, "all three are negative, and the smaller the current the steeper the fall"
'''},
                    {"name": "at a low bias the loop settles almost where it started", "code": r'''
i_s = 5.738534881228506e-16
t = settle(0.70, i_s, 300.0, 100.0)
assert abs(t - 300.02312201486114) < 1e-6, f"expected 300.0231 K, got {t}"
t2 = settle(0.80, i_s, 300.0, 100.0)
assert abs(t2 - 301.3530011521132) < 1e-6, f"expected 301.3530 K, got {t2}"
assert t2 > t, "more bias means more dissipation and a warmer junction"
'''},
                    {"name": "and between 0.84 V and 0.85 V it stops settling at all", "code": r'''
import math
i_s = 5.738534881228506e-16
ok = settle(0.84, i_s, 300.0, 100.0)
assert abs(ok - 309.5651800808127) < 1e-6, f"expected 309.5652 K at 0.84 V, got {ok}"
gone = settle(0.85, i_s, 300.0, 100.0)
assert math.isinf(gone), f"0.85 V on a 100 K/W package must run away; got {gone}"
assert math.isinf(settle(0.90, i_s, 300.0, 100.0)), "and so must anything above it"
'''},
                    {"name": "a better heatsink moves the threshold, it does not remove it", "code": r'''
import math
i_s = 5.738534881228506e-16
assert not math.isinf(settle(0.85, i_s, 300.0, 10.0)), \
    "ten times the heatsinking should bring 0.85 V back inside the convergent region"
cool = settle(0.85, i_s, 300.0, 10.0)
assert abs(cool - 300.9691695373529) < 1e-6, f"expected 300.9692 K on 10 K/W, got {cool}"
assert math.isinf(settle(0.95, i_s, 300.0, 10.0)), \
    "and the threshold has only moved: enough bias still runs away on any finite heatsink"
'''},
                ],
            },
        },
        # ---- M7 -----------------------------------------------------------
        {
            "title": "Reverse bias: the junction as a capacitor",
            "summary": "The region module 1 stripped of carriers is an insulator between two conductors, and its width is under your control. That is a capacitor with a voltage knob on it.",
            "concepts": [
                "Reverse bias widens the depletion region, and a depletion region is a slab with nothing mobile in it lying between two conducting regions. That is a capacitor, $C_j = \\epsilon A/W$, and it is not a parasitic bolted onto the model — it is the same electrostatics that produced the built-in potential.",
                "Module 1 had $W \\propto \\sqrt{V_{bi}+V_R}$, so $C_j = C_{j0}/(1+V_R/V_{bi})^m$ with $m = 1/2$ for an abrupt junction. For module 5's device — $10^{23}$ m$^{-3}$ either side, $A = 10^{-8}$ m$^2$ — that is $C_{j0} = 7.06$ pF at zero bias and 2.67 pF at 5 V.",
                "The exponent $m$ is a statement about the doping *profile*, not about the material: 1/2 for an abrupt step, 1/3 for a linearly graded junction, and up to 1 or 2 for a **hyperabrupt** profile grown deliberately to get more capacitance change per volt. A varactor is a diode whose doping profile was chosen for its $m$.",
                "The exponent matters because the tuning is weak. Taking an abrupt junction from 1 V to 12 V of reverse bias changes $C_j$ by 2.65, and since $f = 1/2\\pi\\sqrt{LC}$ the frequency only moves by $\\sqrt{2.65} = 1.63$. Eleven volts buys two thirds of an octave. A hyperabrupt part with $m = 2$ does the same swing in about 1.1 V, and covers the whole FM broadcast band on a 1 µH coil — 88 to 108 MHz — with 0.28 V of tuning where the abrupt junction needs 4.9 V.",
                "The same capacitance means a reverse-biased diode is not an open circuit. 2.67 pF is 596 $\\Omega$ of reactance at 100 MHz, which is a perfectly ordinary impedance — so a diode that is off at DC is merely a small capacitor at RF, and every fast circuit has to be drawn with that capacitor in it.",
                "Whatever biases the varactor appears in parallel with the tuned circuit and damps it, so the tuning voltage is fed through a resistance large enough to be invisible to the signal. The same resistance and the same $C_j$ then set how fast the tuning can move, and those two requirements pull in opposite directions.",
            ],
            "read": [
                {
                    "title": "Eleven volts of tuning, and two thirds of an octave to show for it",
                    "minutes": 15,
                    "body": r'''
A tuned circuit on the bench: a 1 µH coil, a reverse-biased diode across it, and a
laboratory supply feeding the diode through a large resistor. Turn the supply from 1 V to
12 V and the circuit's resonant frequency climbs from 72.9 MHz to 118.7 MHz.

Two things about that are worth noticing before any theory. Nothing moved — there are no
plates, no shaft, no gears, and the tuning is a voltage on a wire. And the wire carries
essentially no current: a reverse-biased junction leaks nanoamps, so the supply delivers
nothing and the frequency is set by a voltage the way a meter reading is. That is the
whole appeal of a varactor, and it is why every phase-locked loop and every synthesised
receiver built since the 1960s tunes this way.

The second thing to notice is how *little* eleven volts bought. A factor of 1.63 in
frequency is two thirds of an octave. This unit is about where the capacitance comes from,
and about why the tuning is so hard-won.

## The capacitor nobody fitted

Module 1 left a depletion region: a slab of silicon 147 nm thick, stripped of mobile
carriers, lying between two regions that are full of them. Read that description again
without the semiconductor vocabulary and it is an insulating layer between two conductors.
That is a capacitor, and it is not a parasitic anybody added — it is the same
electrostatics that produced the built-in potential in the first place.

Its value is the ordinary parallel-plate result, with the depletion width as the plate
separation:

$$C_j = \frac{\epsilon A}{W}$$

Put module 1's junction into it — $A = 10^{-8}$ m$^2$, $W_0 = 146.8$ nm, and silicon's
permittivity $11.7\epsilon_0$ — and the diode you have been studying turns out to have
about 7 pF sitting inside it at zero bias.

## Steering it

Now the part that makes it a component rather than a nuisance. Module 1 also established
that the depletion width grows as the square root of the total voltage the junction is
supporting, which under $V_R$ volts of reverse bias is $V_{bi}+V_R$. Take the ratio of the
width at $V_R$ to the width at zero and everything about the particular junction cancels:

$$\frac{W}{W_0} = \sqrt{\frac{V_{bi}+V_R}{V_{bi}}}
\qquad\Longrightarrow\qquad
C_j = \frac{\epsilon A}{W} = \frac{C_{j0}}{\sqrt{1 + V_R/V_{bi}}}$$

That is the varactor equation, and this module's derivation, **The capacitance of a
junction you are pulling apart**, walks the four steps of it. A data sheet writes it with
the exponent left general, $C_j = C_{j0}(1+V_R/V_{bi})^{-m}$, for reasons that come two
sections down.

```python
import math

EPS_SI = 11.7 * 8.8541878128e-12
AREA = 1.0e-8                   # m^2, the junction of modules 1 and 5
W0 = 1.4681182204947003e-07     # m, its depletion width with nothing applied
V_BI = 0.833370010652644        # V
L = 1.0e-6                      # H, the tank inductor

print("eps*A/W0 = %.3f pF" % (EPS_SI * AREA / W0 * 1e12))

c_j0 = 7.06e-12                 # the same number, as a data sheet would round it
for v_r in (0.0, 1.0, 5.0, 12.0):
    c_j = c_j0 / math.sqrt(1.0 + v_r / V_BI)
    f = 1.0 / (2.0 * math.pi * math.sqrt(L * c_j))
    print("V_R = %5.1f V   C_j = %.3f pF   f = %7.3f MHz" % (v_r, c_j * 1e12, f / 1e6))
```

```text
eps*A/W0 = 7.056 pF
V_R =   0.0 V   C_j = 7.060 pF   f =  59.899 MHz
V_R =   1.0 V   C_j = 4.760 pF   f =  72.949 MHz
V_R =   5.0 V   C_j = 2.668 pF   f =  97.429 MHz
V_R =  12.0 V   C_j = 1.799 pF   f = 118.657 MHz
```

There are the two frequencies from the bench at the top, and the first four rows explain
why the knob feels so uneven. The first volt of bias is worth 2.3 pF and the last seven
volts together are worth 0.87 pF, because $V_{bi}$ is already in the sum before you apply
anything: going from 4 V to 8 V of applied bias does not double the junction voltage, it
takes it from 4.83 V to 8.83 V, a factor of 1.83, and the square root cuts even that to
1.35.

## Why the tuning is weak, in one exponent

Stack the two square roots. The capacitance goes as the inverse square root of the
junction voltage, and a resonant frequency goes as the inverse square root of the
capacitance, so

$$f \propto \frac{1}{\sqrt{C_j}} \propto \left(V_{bi}+V_R\right)^{1/4}$$

The frequency of an abrupt-junction varactor tracks the **fourth root** of the voltage
across it. From 1.833 V to 12.833 V is a factor of 7.0 in junction volts, and
$7.0^{1/4} = 1.627$ — which is the 72.9 to 118.7 MHz measured at the top, to three
figures. A fourth root is a brutal thing to design against: to double the frequency you
need sixteen times the junction voltage, which from 1 V of bias means about 28 V at the
other end.

## The exponent is a doping profile

This is where $m$ earns its place in the data sheet. The square root came from module 1's
depletion width, and that width came from assuming an **abrupt** junction — doping that
switches from $N_a$ to $N_d$ at a plane. Change the profile and the exposed charge grows
differently with width, so the width grows differently with voltage, and the exponent
moves: $m = 1/2$ for the abrupt step, $1/3$ for a doping that ramps linearly through the
junction, and 1 to 2 for a **hyperabrupt** profile, grown with the doping deliberately
heaviest right at the junction and falling away from it.

That last one is worth what it costs. The lab, **The tuning curve, and reading it
backwards**, bisects for the bias that lands a 1 µH tank on a wanted frequency, and the
answer for the FM broadcast band is stark: covering 88 to 108 MHz takes 4.92 V of tuning
range with the abrupt junction and 0.28 V with an $m = 2$ part. Same coil, same band,
eighteen times less voltage.

## Worked example: the tank, all the way through

The build, **A tank tuned by a voltage**, is that circuit at one point in its range, and
it has two requirements that fight each other.

Bias the varactor at 5.00 V, so $C_j = 2.668$ pF, and with 1 µH the tank sits at 97.4 MHz,
in the middle of the FM band. The bias has to arrive through a resistor $R_b$, because a
tuning supply is a low impedance and anything low-impedance connected across a tuned
circuit damps it flat. So $R_b$ is the only free choice, and it is the whole of two quite
different specifications.

**The loaded $Q$.** At resonance the coil and the capacitor cancel, and what is left across
the node is $R_b$. For a parallel resonant circuit $Q = R/(\omega_0 L)$, and substituting
$\omega_0 = 1/\sqrt{LC_j}$:

$$Q = \frac{R_b}{\omega_0 L} = R_b\sqrt{\frac{C_j}{L}}$$

A *bigger* resistor is a sharper tank. Asking for $Q \ge 80$ puts a floor under $R_b$.

**The settling time.** To retune, the tuning voltage has to change the charge on $C_j$, and
it can only do that through $R_b$. The time constant is $\tau = R_bC_j$, and a receiver
that takes longer than a microsecond to arrive on a new station is one you can hear
settling. Asking for $\tau \le 200$ ns puts a ceiling on $R_b$.

```python
import math

L = 1.0e-6
c_j = 2.668e-12                 # farads, the varactor at 5 V of reverse bias

z0 = math.sqrt(L / c_j)
print("sqrt(L/C_j)   = %.1f ohm" % z0)
print("Q >= 80  needs  R_b >= %.2f k" % (80.0 * z0 / 1e3))
print("tau <= 200 ns   R_b <= %.2f k" % (200e-9 / c_j / 1e3))
for r_b in (56e3, 62e3, 68e3):
    print("R_b = %2.0f k   Q = %5.1f   tau = %5.1f ns"
          % (r_b / 1e3, r_b / z0, r_b * c_j * 1e9))
```

```text
sqrt(L/C_j)   = 612.2 ohm
Q >= 80  needs  R_b >= 48.98 k
tau <= 200 ns   R_b <= 74.96 k
R_b = 56 k   Q =  91.5   tau = 149.4 ns
R_b = 62 k   Q = 101.3   tau = 165.4 ns
R_b = 68 k   Q = 111.1   tau = 181.4 ns
```

Three standard values fit between the floor and the ceiling, and 62 k sits in the middle
of them. But look at what the two constraints have in common. Divide one by the other:

$$\frac{Q}{\tau} = \frac{R_b\sqrt{C_j/L}}{R_bC_j} = \frac{1}{\sqrt{LC_j}} = \omega_0
\qquad\Longrightarrow\qquad Q = \omega_0\tau = 2\pi f_0\tau$$

The loaded $Q$ and the tuning time constant are the same number in different clothes:
$Q$ is how many radians of carrier fit inside one time constant. So the design window is
not really about resistors at all. The ceiling on $\tau$ sets a ceiling on $Q$ of
$2\pi \times 97.4\ \text{MHz} \times 200\ \text{ns} = 122$, the specification asks for at
least 80, and the whole design exists in the gap between 80 and 122. Ask for a $Q$ of 150
on this tank and no resistor works — you would have to change the tank.

## A diode that is off is still a component

One more consequence of the same capacitance, and it catches people out well away from
tuning circuits. At 5 V of reverse bias this diode passes nanoamps of DC and is, for every
DC purpose, an open circuit. At 100 MHz its 2.668 pF is

$$\frac{1}{2\pi f C_j} = 596\ \Omega$$

which is an utterly ordinary impedance, on the same scale as the circuits it sits among. A
reverse-biased diode is not an open circuit; it is a small capacitor, and above a few
megahertz it has to be drawn as one. This is why an RF switch specifies its off-state
capacitance, why module 9's diode rings after it turns off, and why a photodiode's speed
in module 10 is set by a number derived here.

## The mistake people actually make

Using $C_{j0}$. It is the number printed largest on the data sheet, it is the one that
appears in the part's name, and every other capacitor anyone has ever fitted has a single
value — so it goes into the resonance formula, and the tank lands at 59.9 MHz instead of
97.4 MHz. That is not a small error at the edge of the band; it is not in the FM band or
anywhere near it. The build's checks say so in as many words.

The tempting part is that $C_{j0}$ is not wrong, it is a *boundary value*: the capacitance
at exactly zero bias, which is the one bias a varactor is never used at. A varactor's
capacitance is a function, and quoting the function's value at the one point outside its
operating range is the same error as quoting a diode's 0.7 V without saying at what
current.

## Where this stops holding

**In forward bias, none of it applies.** Set $V_R = -V_{bi}$ and the formula divides by
zero. Well before that the junction starts conducting, and a conducting diode has a
capacitance of an entirely different kind: the stored minority charge of module 9, which
behaves as $C_d = \tau/r_d$. At 10 mA with a microsecond of lifetime that is 0.39 µF —
five orders of magnitude above anything in the table above. Junction capacitance is a
reverse-bias story, and diffusion capacitance is the forward-bias one.

**A real varactor is not a lossless capacitor.** It has bulk resistance in series with the
junction, giving the device its own $Q$ of $1/(\omega r_sC_j)$, which falls as the
frequency rises. The build's tank was lossless apart from the bias resistor, which made
$R_b$ the whole of the loaded $Q$; on a real board the varactor and the coil both take
their share, and the coil is usually the worse of the two.

**$m$ is not a constant either.** A hyperabrupt profile only behaves as $m = 2$ over the
range of bias where the graded doping is what the depletion edge is moving through. Run
off the end of that profile and the exponent reverts towards 1/2, which is why a
hyperabrupt part's data sheet specifies a bias range and not only a capacitance.

**And the depletion approximation is at its weakest near zero bias**, where the region is
narrow and the few-nanometre transition at each edge is a real fraction of the width. The
formula overstates $C_{j0}$ somewhat for that reason — which matters less than it might,
since the working bias is never zero.
''',
                },
            ],
            "quiz": {
                "title": "Capacitance you can steer",
                "minutes": 10,
                "questions": [
                    {
                        "q": "An abrupt junction has $C_{j0} = 7.06$ pF and $V_{bi} = 0.833$ V. What is its capacitance at 5.0 V of reverse bias?",
                        "opts": ["7.06 pF", "2.67 pF", "1.01 pF", "42.4 pF"],
                        "a": 1,
                        "why": r'''
$C_j = C_{j0}/\sqrt{1+V_R/V_{bi}} = 7.06/\sqrt{1+6.00} = 7.06/2.646 = 2.67$ pF. The
answer 1.01 pF is the same calculation with the square root left out — dividing by
7.00 rather than by 2.646 — and that root is not decoration: it comes from the width
going as $\sqrt{V}$, which is where module 1's depletion-width formula put it. Answering
42.4 pF multiplies where the physics divides; more reverse bias means a wider gap
between the plates and therefore *less* capacitance.
''',
                    },
                    {
                        "q": "The same junction is taken from 4 V to 8 V of reverse bias. What happens to $C_j$?",
                        "opts": [
                            "it halves",
                            "it falls to about 74% of its value",
                            "it falls to a quarter",
                            "it is unchanged — the capacitance is fixed once the junction is made",
                        ],
                        "a": 1,
                        "why": r'''
$C_j(4) = 2.931$ pF and $C_j(8) = 2.168$ pF, a ratio of 0.740. Doubling the *applied*
bias did not double the total junction voltage — that went from 4.83 V to 8.83 V,
a factor of 1.83 — and then the square root cut it to 1.35. Expecting a halving
treats the relation as $1/V$ when it is $1/\sqrt{V}$, and forgets that the built-in
potential is in the sum whether you applied it or not. This diminishing return is the
central nuisance of varactor tuning: the first volt is worth far more than the eighth.
''',
                    },
                    {
                        "q": "You want to tune an oscillator over a 2:1 frequency range with an abrupt-junction varactor, starting from 1 V of reverse bias. Roughly how much bias do you need at the top?",
                        "opts": [
                            "2 V",
                            "4 V",
                            "about 28 V",
                            "it cannot be done at any voltage",
                        ],
                        "a": 2,
                        "why": r'''
2:1 in frequency is 4:1 in capacitance, and for $m = 1/2$ that is 16:1 in total
junction voltage. Starting from $0.833 + 1 = 1.833$ V you need $16 \times 1.833 =
29.3$ V across the junction, so about 28.5 V of applied reverse bias. Answering 4 V
applies the capacitance ratio directly to the voltage and skips both the square and the
square root. This is exactly why wideband VCOs use hyperabrupt varactors, or several
varactors switched in banks, rather than one abrupt junction and a large supply.
''',
                    },
                    {
                        "q": "A diode with 2.67 pF of junction capacitance is reverse biased and carrying no current. What does it look like to a 100 MHz signal?",
                        "opts": [
                            "an open circuit — it is reverse biased",
                            "about 596 $\\Omega$ of reactance",
                            "about 6 $\\Omega$ of reactance",
                            "a short circuit, because capacitors pass AC",
                        ],
                        "a": 1,
                        "why": r'''
$1/2\pi fC = 1/(2\pi \times 10^8 \times 2.67\times10^{-12}) = 596\ \Omega$, which is an
utterly ordinary impedance — the same order as the circuits it sits in. Treating a
reverse-biased diode as an open circuit is safe at DC and at audio and is wrong by the
time you reach VHF, which is why RF switches specify an off-state capacitance and why
this same capacitance sets a photodiode's speed in module 10. Neither extreme answer
survives arithmetic: a capacitor is neither an open nor a short, it is a number of ohms
that depends on the frequency you asked about.
''',
                    },
                    {
                        "q": "Why is a varactor's tuning voltage fed in through a resistor of tens of kilohms rather than straight from a low-impedance supply?",
                        "opts": [
                            "to limit the current through the varactor",
                            "to drop the supply voltage down to the tuning range",
                            "because whatever is connected to the tuned circuit loads it, and a low-impedance source would damp the resonance away",
                            "to protect the varactor against reverse breakdown",
                        ],
                        "a": 2,
                        "why": r'''
Anything joined to a tuned circuit appears across it. A tuning supply with an output
impedance of a fraction of an ohm would sit in parallel with the tank and take its
loaded $Q$ to nearly nothing; the series resistor is what keeps the supply out of the
signal path. Current limiting is not the reason — a reverse-biased varactor draws
nanoamps whatever you do — and the resistor drops no steady voltage for the same
reason, so the tuning voltage arrives at the varactor unchanged. What the resistor does
cost is speed: with $C_j$ it makes a time constant, and that sets how fast you can
retune.
''',
                    },
                    {
                        "q": "A varactor data sheet gives $C_{j0}$, $V_{bi}$ and $m$. Which physical property of the device is $m$ describing?",
                        "opts": [
                            "how the doping varies with distance through the junction",
                            "the junction area",
                            "the minority carrier lifetime",
                            "the reverse breakdown voltage",
                        ],
                        "a": 0,
                        "why": r'''
The doping profile. An abrupt step from p to n gives $m = 1/2$; a doping that ramps
linearly through the junction gives 1/3; a profile with the doping deliberately made
*heaviest* right at the junction and falling away from it — hyperabrupt — gives
$m$ near 1 or 2, and much more capacitance change per volt. Area sets $C_{j0}$ and
nothing else, since it scales the capacitance at every bias equally. The lifetime
belongs to module 9 and the breakdown to module 4; neither appears anywhere in
$C_j(V_R)$.
''',
                    },
                ],
            },
            "derive": {
                "title": "The capacitance of a junction you are pulling apart",
                "minutes": 13,
                "vars": ["C_j", "C_j0", "epsilon", "A", "W", "W_0", "V_bi", "V_R",
                         "V_1", "V_2", "q", "N_a", "N_d"],
                "brief": r'''
Two facts, both already established, and the varactor equation falls out in four steps.

The first is electrostatic: a region of width $W$ and area $A$ with no mobile charge
inside it, lying between two conducting regions, holds a capacitance. The second is
module 1's: the depletion width of an abrupt junction goes as the square root of the
total voltage the junction is supporting, which under $V_R$ volts of reverse bias is
$V_{bi} + V_R$.

Write $W_0$ for the depletion width with nothing applied, and $C_{j0}$ for the
capacitance there. $\epsilon$ is the permittivity of silicon.
''',
                "steps": [
                    {
                        "prompt": "Treat the depletion region as a parallel-plate capacitor of area $A$, thickness $W$, filled with silicon of permittivity $\\epsilon$. Write its capacitance.",
                        "answer": "\\frac{\\epsilon A}{W}",
                        "hint": "The standard parallel-plate result. Nothing about a junction changes it; only the plate separation is unusual, in that you can move it.",
                        "deconstruct": [
                            "A parallel-plate capacitor has $C = \\epsilon A/d$ for a plate separation $d$.",
                            "Here the separation is the depletion width $W$, and the two quasi-neutral regions either side are the plates.",
                        ],
                    },
                    {
                        "prompt": "Module 1 gave $W \\propto \\sqrt{V_{bi}+V_R}$, and with nothing applied the width is $W_0$. Write $W$ under $V_R$ volts of reverse bias, in terms of $W_0$, $V_{bi}$ and $V_R$.",
                        "given": "$W \\propto \\sqrt{V_{bi}+V_R}$, and $W = W_0$ when $V_R = 0$.",
                        "answer": "W_0\\sqrt{\\frac{V_bi + V_R}{V_bi}}",
                        "hint": "Take the ratio of the width at $V_R$ to the width at zero, so the constant of proportionality cancels.",
                        "deconstruct": [
                            "$W(V_R)/W_0 = \\sqrt{V_{bi}+V_R}\\,/\\,\\sqrt{V_{bi}}$, because everything else in the constant is the same junction.",
                            "One square root over another is the square root of the ratio.",
                        ],
                    },
                    {
                        "prompt": "Put that width into step 1, and use $C_{j0} = \\epsilon A/W_0$ to remove $\\epsilon$, $A$ and $W_0$ together. Write $C_j$ in terms of $C_{j0}$, $V_{bi}$ and $V_R$.",
                        "answer": "\\frac{C_j0}{\\sqrt{1 + \\frac{V_R}{V_bi}}}",
                        "hint": "Dividing by $W_0\\sqrt{\\cdots}$ is dividing by $W_0$ and then by the root, and the first of those two divisions is exactly $C_{j0}$.",
                        "deconstruct": [
                            "$C_j = \\epsilon A / \\left(W_0\\sqrt{(V_{bi}+V_R)/V_{bi}}\\right)$.",
                            "Group the $\\epsilon A/W_0$ and call it $C_{j0}$.",
                            "$(V_{bi}+V_R)/V_{bi}$ is the same thing as $1 + V_R/V_{bi}$.",
                        ],
                    },
                    {
                        "prompt": "A tuning range is a ratio, not a value. Write $C_j(V_1)/C_j(V_2)$ for two reverse biases $V_1$ and $V_2$ — the factor by which the capacitance falls as you go from $V_1$ up to $V_2$.",
                        "answer": "\\sqrt{\\frac{V_bi + V_2}{V_bi + V_1}}",
                        "hint": "Divide step 3 by itself at the two voltages; $C_{j0}$ cancels and the two roots combine into one.",
                        "deconstruct": [
                            "The ratio is $\\sqrt{1+V_2/V_{bi}}\\,/\\,\\sqrt{1+V_1/V_{bi}}$, since dividing by a fraction inverts it.",
                            "Multiply top and bottom inside the roots by $V_{bi}$.",
                        ],
                    },
                ],
                "closing": r'''
So $C_j = C_{j0}(1+V_R/V_{bi})^{-1/2}$, and the general form a data sheet quotes is
$C_j = C_{j0}(1+V_R/V_{bi})^{-m}$ with $m$ carrying the doping profile.

The ratio in step 4 is the honest way to read a varactor. Between 1 V and 12 V it is
$\sqrt{12.833/1.833} = 2.65$ in capacitance, and a resonant frequency goes as
$1/\sqrt{C}$, so the *frequency* only moves by $\sqrt{2.65} = 1.63$. Eleven volts of
tuning range bought two thirds of an octave, and there is no arrangement of an abrupt
junction that does better — the exponent is fixed by the doping profile, which was
decided in a furnace long before you chose your supply rail.

Two other consequences are worth carrying forward. Because $C_j$ falls as the bias
rises, a reverse-biased photodiode is faster than an unbiased one, which is module 10.
And because $C_j$ is still there when the diode has stopped conducting, it is half of
the resonant circuit that rings after a diode turns off, which is module 9.
''',
            },
            "build": {
                "title": "A tank tuned by a voltage",
                "minutes": 28,
                "brief": r'''
A varactor and an inductor make a tuned circuit whose frequency is set by a DC voltage
and nothing else — no moving parts, no gang capacitor. This is that circuit, at one
point in its tuning range, with the two things that have to be true at once.

## The device

The abrupt junction of module 5, used backwards: $C_{j0} = 7.06$ pF, $V_{bi} = 0.833$ V,
$m = 1/2$. It is biased at **5.00 V reverse**, so

$$C_j = \frac{7.06\ \text{pF}}{\sqrt{1 + 5.00/0.833}} = 2.67\ \text{pF}$$

and the tank inductor is **1.0 µH**. Together those resonate at 97.4 MHz, in the middle
of the FM broadcast band — which is what this stage is for.

## The canvas

The signal from the antenna is modelled as a **1 mA current source** driving the tank
node, and the probe is on that node. The inductor is already there. A current source is
an open circuit to the signal, so it does not load the tank; the *only* loss in this
idealised version is whatever you add.

Add:

- the varactor, as its junction capacitance at the stated bias, from the tank node to
  ground,
- the bias resistor, from the tank node to ground. In the real circuit it goes to the
  tuning supply, which is a short circuit as far as the signal is concerned, so it is
  drawn to ground here.

## What has to be true

- the tank must resonate at **97.4 MHz**, within about one and a half per cent
- the **loaded $Q$ must be at least 80**, or the stage passes half the band at once
- the tuning must **settle within a microsecond**, which means the bias network's time
  constant $Z_{pk}C_j$ must be **200 ns or less**

## Where the tension is

The bias resistor is the only free choice, and it is the whole of the loaded $Q$:
$Q = R_b\sqrt{C_j/L}$, so a bigger resistor is a sharper tank. It is also the whole of
the tuning time constant, $\tau = R_bC_j$, so a bigger resistor is a slower tuner. Work
out both from the numbers above before you type anything: one of them puts a floor
under $R_b$ and the other puts a ceiling on it, and the gap between them is not
enormous.

The other trap is the capacitance. Use $C_{j0}$ instead of $C_j$ at the working bias
and the tank lands at 59.9 MHz, which is not in the FM band or anywhere near it.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 1e-3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 4},
                        {"id": "p2", "kind": "L", "x": 9, "y": 9, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p8", "kind": "OUT", "x": 11, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [11, 7]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 1e-3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 4},
                        {"id": "p2", "kind": "L", "x": 9, "y": 9, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p4", "kind": "C", "x": 13, "y": 9, "rot": 1, "value": 2.67e-12},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p6", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 62000},
                        {"id": "p7", "kind": "GND", "x": 17, "y": 11},
                        {"id": "p8", "kind": "OUT", "x": 11, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [17, 7]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [13, 7], "b": [13, 8]},
                        {"a": [17, 7], "b": [17, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [13, 10], "b": [13, 11]},
                        {"a": [17, 10], "b": [17, 11]},
                    ],
                },
                "checks": [
                    {"name": "one inductor, one capacitor and one resistor across the tank node", "code": r'''
const ls = c.values('L');
c.assert(ls.length === 1,
  'The tank needs exactly one inductor, and the 1 uH one is already on the canvas. Found ' +
  ls.length + '.');
c.close(ls[0], 1.0e-6, 0.02,
  'the tank inductance. It is given, not chosen; the varactor is what does the tuning');
c.assert(c.count('C') === 1,
  'Exactly one capacitor: the varactor\'s junction capacitance at its working bias. ' +
  'Found ' + c.count('C') + '.');
c.assert(c.count('R') === 1,
  'Exactly one resistor: the bias feed. Found ' + c.count('R') + '. Any extra resistance ' +
  'across this node is extra loss, and the Q check below will find it.');
'''},
                    {"name": "it resonates at 97.4 MHz", "code": r'''
let fb = 0, gb = -1;
for (let i = 0; i <= 600; i++) {
  const f = 1e7 * Math.pow(100, i / 600);
  const g = c.gain(f);
  if (g > gb) { gb = g; fb = f; }
}
let lo = fb / 1.05, hi = fb * 1.05;
for (let k = 0; k < 80; k++) {
  const a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
  if (c.gain(a) < c.gain(b)) lo = a; else hi = b;
}
const f0 = 0.5 * (lo + hi);
c.close(f0, 97.4e6, 0.015,
  'the frequency the tank peaks at. With 1 uH it wants 2.67 pF; if you are near 60 MHz ' +
  'the zero-bias capacitance went in instead of the value at 5 V of reverse bias');
'''},
                    {"name": "the loaded Q is at least 80", "code": r'''
const L = c.values('L')[0];
let fb = 0, gb = -1;
for (let i = 0; i <= 600; i++) {
  const f = 1e7 * Math.pow(100, i / 600);
  const g = c.gain(f);
  if (g > gb) { gb = g; fb = f; }
}
let lo = fb / 1.05, hi = fb * 1.05;
for (let k = 0; k < 80; k++) {
  const a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
  if (c.gain(a) < c.gain(b)) lo = a; else hi = b;
}
const f0 = 0.5 * (lo + hi);
const zpk = c.gain(f0) / 1.0e-3;
const q = zpk / (2 * Math.PI * f0 * L);
c.assert(q >= 80 * 0.99,
  'The loaded Q is ' + q.toFixed(1) + ', below the 80 asked for. Q = R_b*sqrt(C_j/L) here, ' +
  'so the bias resistor is the only thing setting it — make it larger.');
'''},
                    {"name": "and the tuning settles in under a microsecond", "code": r'''
let fb = 0, gb = -1;
for (let i = 0; i <= 600; i++) {
  const f = 1e7 * Math.pow(100, i / 600);
  const g = c.gain(f);
  if (g > gb) { gb = g; fb = f; }
}
let lo = fb / 1.05, hi = fb * 1.05;
for (let k = 0; k < 80; k++) {
  const a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
  if (c.gain(a) < c.gain(b)) lo = a; else hi = b;
}
const f0 = 0.5 * (lo + hi);
const zpk = c.gain(f0) / 1.0e-3;
const cj = c.values('C')[0];
const tau = zpk * cj;
c.assert(tau <= 200e-9 * 1.01,
  'The bias network\'s time constant is ' + c.fmt(tau, 's') + ', over the 200 ns allowed. ' +
  'Five of those is how long the tuning takes to arrive after the voltage changes, and ' +
  'a receiver that takes longer than a microsecond to settle is a receiver you can hear ' +
  'settling. The only lever is the bias resistor, and it is the same lever as the Q.');
'''},
                ],
                "hints": [
                    "The capacitance first: $7.06/\\sqrt{1+5.00/0.833} = 7.06/2.646 = 2.67$ pF. Type `2.67p`.",
                    "Then the two bounds on the bias resistor. $Q = R_b\\sqrt{C_j/L} = R_b \\times 1.633\\times10^{-3}$, so $Q \\ge 80$ needs $R_b \\ge 49.0$ k$\\Omega$; and $\\tau = R_bC_j \\le 200$ ns needs $R_b \\le 74.9$ k$\\Omega$.",
                    "That leaves 56 k, 62 k and 68 k as the standard values inside the window. 62 k sits comfortably in the middle: $Q = 101$ and $\\tau = 165$ ns.",
                    "Both the capacitor and the resistor run from the tank node down to their own ground. The inductor is already wired that way — copy it.",
                    "If the resonance check reads about 60 MHz, the capacitance is $C_{j0}$ rather than $C_j$ at 5 V. If it reads over 1 GHz, there is no capacitor on the node at all and the scan is just running off the top of the sweep.",
                ],
            },
            "lab": {
                "title": "The tuning curve, and reading it backwards",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
A varactor data sheet gives you $C_{j0}$, $V_{bi}$ and $m$. Everything a tuner designer
wants — what frequency a given voltage produces, and what voltage a wanted frequency
needs — is four short functions away.

- `junction_capacitance(c_j0, v_bi, v_r, m)` returns $C_{j0}/(1+V_R/V_{bi})^m$ in
  farads.
- `resonant_frequency(l, c)` returns $1/2\pi\sqrt{LC}$ in hertz.
- `tank_frequency(l, c_j0, v_bi, v_r, m)` returns the resonant frequency of `l` with
  that varactor at that reverse bias. It should call the two functions above rather
  than repeat them.
- `bias_for_frequency(l, c_j0, v_bi, m, f_target, v_lo, v_hi)` returns the reverse bias
  that puts the tank on `f_target`, found by **bisection** between `v_lo` and `v_hi`.

There is no closed form for the last one worth writing — you could invert it by hand,
but the moment $m$ stops being exactly 1/2 you would have to do it again, and bisection
does not care what $m$ is. The frequency rises monotonically with the bias, so:

```text
lo, hi = v_lo, v_hi
repeat 200 times:
    mid = (lo + hi) / 2
    if tank_frequency(at mid) < f_target:  lo = mid
    else:                                  hi = mid
return (lo + hi) / 2
```

Everything is in SI units: farads, henries, hertz and volts.
''',
                "files": [{"name": "main.py", "content": r'''
"""A varactor-tuned tank, forwards and backwards."""

import math


def junction_capacitance(c_j0, v_bi, v_r, m):
    """Junction capacitance in farads at `v_r` volts of reverse bias."""
    # TODO: c_j0 divided by (1 + v_r / v_bi) raised to the power m.
    return 0.0


def resonant_frequency(l, c):
    """Resonant frequency in hertz of `l` henries with `c` farads."""
    # TODO: one over two pi root LC.
    return 0.0


def tank_frequency(l, c_j0, v_bi, v_r, m):
    """Where the tank sits with the varactor at `v_r` volts of reverse bias."""
    # TODO: call the two functions above, in the obvious order.
    return 0.0


def bias_for_frequency(l, c_j0, v_bi, m, f_target, v_lo, v_hi):
    """Reverse bias that puts the tank on f_target, by bisection."""
    lo, hi = v_lo, v_hi
    # TODO: 200 halvings, then return the midpoint.
    return 0.0


if __name__ == "__main__":
    c_j0, v_bi, m, l = 7.06e-12, 0.833, 0.5, 1.0e-6
    print("C at 0 V:", junction_capacitance(c_j0, v_bi, 0.0, m), "F")
    print("C at 5 V:", junction_capacitance(c_j0, v_bi, 5.0, m), "F")
    print("tank at 5 V:", tank_frequency(l, c_j0, v_bi, 5.0, m), "Hz")
    lo = bias_for_frequency(l, c_j0, v_bi, m, 88.0e6, 0.0, 30.0)
    hi = bias_for_frequency(l, c_j0, v_bi, m, 108.0e6, 0.0, 30.0)
    print("88 MHz needs", lo, "V and 108 MHz needs", hi, "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""A varactor-tuned tank, forwards and backwards."""

import math


def junction_capacitance(c_j0, v_bi, v_r, m):
    """Junction capacitance in farads at `v_r` volts of reverse bias."""
    return c_j0 / (1.0 + v_r / v_bi) ** m


def resonant_frequency(l, c):
    """Resonant frequency in hertz of `l` henries with `c` farads."""
    return 1.0 / (2.0 * math.pi * math.sqrt(l * c))


def tank_frequency(l, c_j0, v_bi, v_r, m):
    """Where the tank sits with the varactor at `v_r` volts of reverse bias."""
    return resonant_frequency(l, junction_capacitance(c_j0, v_bi, v_r, m))


def bias_for_frequency(l, c_j0, v_bi, m, f_target, v_lo, v_hi):
    """Reverse bias that puts the tank on f_target, by bisection."""
    lo, hi = v_lo, v_hi
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if tank_frequency(l, c_j0, v_bi, mid, m) < f_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    c_j0, v_bi, m, l = 7.06e-12, 0.833, 0.5, 1.0e-6
    print("C at 0 V:", junction_capacitance(c_j0, v_bi, 0.0, m), "F")
    print("C at 5 V:", junction_capacitance(c_j0, v_bi, 5.0, m), "F")
    print("tank at 5 V:", tank_frequency(l, c_j0, v_bi, 5.0, m), "Hz")
    lo = bias_for_frequency(l, c_j0, v_bi, m, 88.0e6, 0.0, 30.0)
    hi = bias_for_frequency(l, c_j0, v_bi, m, 108.0e6, 0.0, 30.0)
    print("88 MHz needs", lo, "V and 108 MHz needs", hi, "V")
'''}],
                "hints": [
                    "`junction_capacitance` is `c_j0 / (1.0 + v_r / v_bi) ** m`. Keep the whole bracket under the power; `1.0 + (v_r / v_bi) ** m` is a different and much flatter function.",
                    "At `v_r = 0` the divisor is $1^m = 1$ for every $m$, so the function must hand back `c_j0` exactly. That is the cheapest test you can run on it.",
                    "`resonant_frequency` is `1.0 / (2.0 * math.pi * math.sqrt(l * c))`. Put `l * c` inside the root, not `math.sqrt(l) * c`.",
                    "`tank_frequency` should be one line that calls the other two. Repeating the algebra means fixing it twice when `m` turns out not to be 1/2.",
                    "In `bias_for_frequency` the comparison runs the opposite way to a diode load line: *more* reverse bias means *less* capacitance and therefore a *higher* frequency. If the answer comes back as `v_lo` or `v_hi`, swap the two branches.",
                ],
                "tests": [
                    {"name": "the capacitance at zero bias, and at five volts", "code": r'''
c0 = junction_capacitance(7.06e-12, 0.833, 0.0, 0.5)
assert abs(c0 - 7.06e-12) < 1e-24, f"at zero bias it must be c_j0 exactly, got {c0}"
c5 = junction_capacitance(7.06e-12, 0.833, 5.0, 0.5)
assert abs(c5 - 2.6679716690809683e-12) < 1e-21, f"expected 2.66797 pF at 5 V, got {c5}"
c12 = junction_capacitance(7.06e-12, 0.833, 12.0, 0.5)
assert abs(c12 - 1.7987180989963752e-12) < 1e-21, f"expected 1.79872 pF at 12 V, got {c12}"
'''},
                    {"name": "the exponent is not hard-wired to a half", "code": r'''
graded = junction_capacitance(7.06e-12, 0.833, 5.0, 1.0 / 3.0)
assert abs(graded - 3.690249324221493e-12) < 1e-21, \
    f"a linearly graded junction at 5 V gives 3.69025 pF, got {graded}"
hyper = junction_capacitance(7.06e-12, 0.833, 5.0, 2.0)
assert abs(hyper - 1.4398284511215044e-13) < 1e-22, \
    f"a hyperabrupt m = 2 at 5 V gives 0.14398 pF, got {hyper}"
assert hyper < graded, "a larger m must always mean a steeper fall with bias"
'''},
                    {"name": "the resonance formula, on numbers you can check by hand", "code": r'''
f = resonant_frequency(1.0e-6, 100e-12)
assert abs(f - 15915494.309189534) < 1e-3, f"1 uH and 100 pF resonate at 15.9155 MHz, got {f}"
assert abs(resonant_frequency(4.0e-6, 100e-12) - f / 2.0) < 1e-3, \
    "four times the inductance must halve the frequency"
g = resonant_frequency(1.0e-6, 2.67e-12)
assert abs(g - 97401243.3888913) < 1e-3, f"expected 97.4012 MHz, got {g}"
'''},
                    {"name": "the tuning curve of the tank you drew", "code": r'''
l, c_j0, v_bi, m = 1.0e-6, 7.06e-12, 0.833, 0.5
at5 = tank_frequency(l, c_j0, v_bi, 5.0, m)
assert abs(at5 - 97438261.10179539) < 1e-3, f"expected 97.4383 MHz at 5 V, got {at5}"
at1 = tank_frequency(l, c_j0, v_bi, 1.0, m)
at12 = tank_frequency(l, c_j0, v_bi, 12.0, m)
assert abs(at1 - 72953670.44535531) < 1e-3, f"expected 72.9537 MHz at 1 V, got {at1}"
assert abs(at12 - 118669354.30791171) < 1e-3, f"expected 118.6694 MHz at 12 V, got {at12}"
assert abs(at12 / at1 - 1.6266399426304252) < 1e-9, \
    "eleven volts of tuning is worth only 1.6266 in frequency, and that is the point"
'''},
                    {"name": "bisection lands on the frequency it was asked for", "code": r'''
l, c_j0, v_bi, m = 1.0e-6, 7.06e-12, 0.833, 0.5
lo = bias_for_frequency(l, c_j0, v_bi, m, 88.0e6, 0.0, 30.0)
hi = bias_for_frequency(l, c_j0, v_bi, m, 108.0e6, 0.0, 30.0)
assert abs(lo - 3.0476508088795233) < 1e-9, f"88 MHz should need 3.04765 V, got {lo}"
assert abs(hi - 7.970774274817906) < 1e-9, f"108 MHz should need 7.97077 V, got {hi}"
assert abs(tank_frequency(l, c_j0, v_bi, lo, m) - 88.0e6) < 1.0, \
    "the bias it returned must put the tank back on 88 MHz"
assert abs(tank_frequency(l, c_j0, v_bi, hi, m) - 108.0e6) < 1.0, \
    "and on 108 MHz"
'''},
                    {"name": "a hyperabrupt varactor covers the same band in under a volt", "code": r'''
l, c_j0, v_bi = 1.0e-6, 7.06e-12, 0.833
abrupt = (bias_for_frequency(l, c_j0, v_bi, 0.5, 108.0e6, 0.0, 30.0)
          - bias_for_frequency(l, c_j0, v_bi, 0.5, 88.0e6, 0.0, 30.0))
hyper = (bias_for_frequency(l, c_j0, v_bi, 2.0, 108.0e6, 0.0, 30.0)
         - bias_for_frequency(l, c_j0, v_bi, 2.0, 88.0e6, 0.0, 30.0))
assert abs(abrupt - 4.9231234659383825) < 1e-9, \
    f"the abrupt junction needs 4.92312 V to cover 88 to 108 MHz, got {abrupt}"
assert abs(hyper - 0.2781360072872795) < 1e-9, \
    f"the m = 2 part needs 0.278136 V for the same band, got {hyper}"
assert hyper < abrupt / 10.0, \
    "and that is why hyperabrupt profiles exist, awkward doping and all"
'''},
                ],
            },
        },
        # ---- M8 -----------------------------------------------------------
        {
            "title": "Clippers, clamps and multipliers: the diode as a decision",
            "summary": "A family of circuits that use none of the diode's curve and all of its asymmetry — cutting a waveform's top off, moving its DC level, and getting more volts out than went in.",
            "concepts": [
                "Everything so far leaned on the diode's *curve*: the exponential, the slope, the tangent. These circuits use only its *decision* — conducting or not — and the constant-drop model, 0.7 V when on and an open circuit when off, is enough to design every one of them.",
                "A **shunt clipper** is a series resistor with a diode across the output. While the diode is off no current flows in the resistor, so the output follows the input exactly; once it conducts, the output is pinned near $V_F$ and the residual slope is $r_d/(R+r_d)$ — about 1% for a 1 k$\\Omega$ resistor and a 10 $\\Omega$ diode. Clipping is not flat, and how flat it is is a ratio of two resistances.",
                "Put a battery in series with that diode and the clipping level moves to $V_{bias}+V_F$; two such branches facing opposite ways make a two-sided clipper. It is the cheapest waveform limiter there is, it is what protects an input pin from an overvoltage, and it is most of what an overdriven guitar pedal does to a sine wave.",
                "A **clamper** swaps the roles: the capacitor goes in series and the diode across the output. It has memory. Over the first cycles the capacitor charges to whatever DC level puts the clamped extreme at $\\pm V_F$, and after that the whole waveform is shifted by that amount. A clipper changes the shape and leaves the DC alone; a clamper changes the DC and leaves the shape alone.",
                "That memory has to survive between clamping instants, so the load's discharge must be slow compared with one period: $R_LC \\gg T$. If it is not, the waveform sags between clamps and the restoration is incomplete — the same $I/(fC)$ droop as module 3's reservoir, in a circuit that looks nothing like a rectifier.",
                "A **peak detector** is a diode and a capacitor feeding a load: it charges to $V_{peak}-V_F$ and then droops at $I_{load}/(fC)$. Feed a peak detector from a clamper and its input already swings to $2V_{peak}-V_F$, so the output is $2V_{peak}-2V_F$ — a **voltage doubler**, built from two diodes and two capacitors and no transformer. Stack $N$ of them and you have a Cockcroft–Walton ladder at roughly $2NV_{peak}$.",
                "Notice the reversal from module 3. In a mains rectifier the 1.4 V of bridge drops is 4% of a 34 V peak and hardly worth the arithmetic. In a doubler run from a 5 V logic swing it is 1.4 V out of 10, and in a five-stage ladder it is paid five times over. That is why multipliers are built from Schottky diodes, which module 10 explains.",
            ],
            "read": [
                {
                    "title": "Using none of the curve and all of the asymmetry",
                    "minutes": 12,
                    "body": r'''
Every module so far has leaned on the *shape* of the diode's characteristic: the
exponential, its slope, the tangent taken at a chosen point. This module throws all of
that away. The circuits here need only one fact — the diode conducts one way and not the
other — and the crudest model in the course, a **constant 0.7 V when on and an open
circuit when off**, designs every one of them.

That is worth saying plainly because it changes how you should read the arithmetic. When a
clamper analysis uses 0.7 V, it is not being sloppy; it is using the only property of the
diode the circuit depends on, and the exponential would add digits without adding
understanding.

## A clipper: the flat top that is not flat

A resistor $R$ in series, a diode from the output down to a bias battery $V_B$. While the
output is below $V_B + V_F$ the diode is off, no current flows in $R$, so nothing is
dropped across it and the output follows the input exactly — a wire with a resistor in it.

Push the input past $V_B + V_F$ and the diode conducts. Now the circuit is not a wire: it
is $R$ from the input, into the diode's incremental resistance $r_d$ to a fixed voltage. A
divider. Differentiate it:

$$\frac{dV_{out}}{dV_{in}} = \frac{r_d}{R + r_d}$$

With $R = 1$ k$\Omega$ and $r_d = 10\ \Omega$ that is $10/1010 = 0.0099$. So the clipped
top is not flat; it has a residual slope of just under 1%. Take the input from 3 V to
10 V, seven volts of swing, against a clip level of 2.7 V:

```text
V_in = 3 V    V_out = 2.7 + (3 - 2.7)  x 0.0099 = 2.703 V
V_in = 10 V   V_out = 2.7 + (10 - 2.7) x 0.0099 = 2.772 V
                                        change    69 mV
```

Sixty-nine millivolts of the seven volts got through. That is what "clipping" actually
means, and the number is a ratio of two resistances — which is the only place in this
module where the diode's curve reappears at all, through $r_d$.

Two such branches facing opposite ways make a two-sided clipper. It is the cheapest
waveform limiter there is, it is what protects a logic input from an overvoltage, and it
is most of what an overdriven guitar pedal does to a sine wave.

## A clamper: the same parts, rearranged, with memory

Swap the roles — capacitor in *series*, diode across the output — and the circuit becomes
something categorically different. A clipper is memoryless: give it a voltage and it
returns a voltage. A clamper has a state, and the state is the charge on the capacitor.

Feed it a 5 V peak sine, with the diode oriented to conduct when the output tries to go
below $-V_F$. On the first few negative excursions the diode conducts and pumps charge
into the capacitor. It stops when the capacitor holds exactly the DC offset that puts the
negative extreme at $-0.7$ V. After that the diode conducts only in a brief top-up near
each trough.

Now the key step, and it is one line of bookkeeping. A series capacitor cannot change the
*shape* of anything — it adds a constant. So the peak-to-peak swing is still 10 V, and if
the bottom sits at $-0.7$ V then the top sits at

$$-0.7 + 10 = +9.3\ \text{V} \;=\; 2V_{peak} - V_F$$

Nothing was rectified, nothing was removed, and the output now swings to nearly twice the
input's peak. **A clipper changes the shape and leaves the DC alone; a clamper changes the
DC and leaves the shape alone.**

The memory has a cost. Between top-ups the capacitor is the only thing holding the shift,
and the load is draining it the whole time — which is module 3's reservoir problem
wearing different clothes, with the same equation:

$$V_{droop} \approx \frac{I_{load}}{fC}$$

So a clamper needs $R_LC \gg T$. Make the time constant comparable with the period and the
waveform visibly sags between clamps; the DC restoration becomes partial and, worse,
*signal-dependent*, which is the failure mode that ruins a video clamp. The lab,
**Clipping, clamping and the droop between clamps**, steps all three circuits through
time and measures that sag — a clipper needs no memory and is one function of its input,
while the clamper and the peak detector each carry a capacitor voltage from one sample to
the next, which is the whole difference in four lines of code.

## Worked example: a doubler, end to end

**Specification.** A 10 kHz square drive swinging to 5.0 V peak, out of a logic gate.
Wanted: a DC rail near 8.6 V at 1 mA, with less than 50 mV of droop.

**1. The topology.** A clamper, then a peak detector. The clamper lifts the drive to swing
between $-0.7$ V and $+9.3$ V, as above. The peak detector then charges to that peak less
one more diode drop:

$$V_{out} = (2V_{peak} - V_F) - V_F = 2V_{peak} - 2V_F = 10 - 1.4 = 8.6\ \text{V}$$

Two diodes, two capacitors, no transformer, and no inductor. Stack $N$ of these and you
have a Cockcroft-Walton ladder at roughly $2NV_{peak}$.

**2. The output capacitor.** Droop is $I/(fC)$, and at 10 kHz the reservoir is topped up
every 100 $\mu$s:

$$C \ge \frac{I}{f\,V_{droop}} = \frac{0.001}{10^4 \times 0.05} = 2\ \mu\text{F}$$

**3. Check the clamper's own time constant.** The load looks like $8.6/0.001 = 8.6$ k$\Omega$
and the period is 100 $\mu$s, so with the same 2 $\mu$F part:

$$R_LC = 8600 \times 2\times10^{-6} = 17.2\ \text{ms} = 172\,T$$

Comfortably $\gg T$, so the clamp holds. Note how much easier this is at 10 kHz than at
50 Hz: everything in this circuit is sized by $1/f$, and the capacitors that would be
electrolytics on a mains rectifier are ceramics here.

**4. The honest efficiency.** 8.6 V out of a possible 10.0 V. The circuit lost 14% of its
output to two diode drops.

## Why the drops matter here and did not in module 3

The forward drop is roughly 0.7 V whatever circuit it is in. What changes is what it is
0.7 V *of*:

```text
mains rectifier   2 drops out of a 34 V peak                = 4%     nobody notices
this doubler      2 drops out of a 10 V doubled swing       = 14%    annoying
5-stage ladder    10 drops out of a 50 V target             = 14%    and 7 V lost
```

Same diodes, same physics, three quite different verdicts. That reversal is the whole
argument for building multipliers out of Schottky diodes at 0.3 V instead of silicon pn
at 0.7 V, and it is what module 10 is for. Note what does *not* help: running the diodes
at a lower current to bring their drops down, because a whole decade of current buys back
only 60 mV, which is module 2's point arriving in a new context.

## The mistake people actually make

Expecting a doubler to be a power supply. It doubles the voltage, and charge is conserved
while it does so, so it necessarily **halves the available current** before any losses —
and the output impedance of a multiplier is high and rises with the number of stages,
roughly as $N^3/(fC)$ for a Cockcroft-Walton ladder. A five-stage ladder that measures its
target voltage beautifully on a meter can collapse to half of it under a load of tens of
microamps. Multipliers belong where the load is tiny and the voltage is large: photomultiplier
bias, ion pumps, electrostatics, LCD backlights.

The second mistake is reading the clamper's output as rectified. Nothing has been
rectified — the waveform is intact, it has simply moved. Put a meter set to AC across it
and you will read the same value as at the input.

## Where this stops holding

- **The constant-drop model has no dynamics.** Every circuit here assumes the diode turns
  off the instant the current tries to reverse. Module 9 is about how badly that fails: at
  10 kHz the stored charge costs a fraction of a per cent of the period, and at 1 MHz the
  same circuit built with the same diodes stops working entirely.
- **The clamper's start-up is not instantaneous.** It takes several cycles to charge the
  capacitor to its final offset, and longer if the diode's forward resistance is high. A
  clamp on a signal that changes its DC content faster than that never settles.
- **The 0.7 V is a stand-in.** The top-up current in a clamper flows in a brief spike, and
  during that spike the current is far above the milliamp scale where 0.7 V was measured —
  so the real drop is nearer 0.8 or 0.9 V. Every output above is a little optimistic, and
  the error compounds with the number of stages.
- **Leakage is now a design parameter.** These circuits hold charge on a capacitor between
  refreshes, so a diode's reverse leakage discharges the very thing the circuit exists to
  hold. It is the reason a low-drop Schottky is not automatically the right answer here:
  the same trade that buys 0.4 V of forward drop costs orders of magnitude of leakage, and
  module 10 puts numbers on it.
''',
                },
            ],
            "quiz": {
                "title": "Shaping a waveform with a decision",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A shunt clipper — 1 k$\\Omega$ in series, then a diode to a 2.0 V battery — clips at 2.7 V. The diode's dynamic resistance is 10 $\\Omega$. By how much does the clipped level rise as the input goes from 3 V to 10 V?",
                        "opts": [
                            "not at all — that is what clipping means",
                            "about 69 mV",
                            "about 700 mV",
                            "7 V, since the output follows the input",
                        ],
                        "a": 1,
                        "why": r'''
Once the diode conducts, the input drives $R$ into the diode's model and the output
rises by the divider ratio $r_d/(R+r_d) = 10/1010 = 0.0099$ of whatever the input does.
Seven volts of input becomes $7 \times 0.0099 = 69$ mV of output. A clipped level is
flat to about a per cent, not flat absolutely, and that residual slope is the reason a
clipper's flat top still carries a trace of the signal. Answering 700 mV uses
$r_d/R$ with the decimal point one place out; answering 7 V forgets that the diode is
conducting at all.
''',
                    },
                    {
                        "q": "What is the difference between a clipper and a clamper?",
                        "opts": [
                            "a clipper removes part of the waveform and leaves its DC level alone; a clamper shifts the whole waveform and leaves its shape alone",
                            "they are two names for the same circuit",
                            "a clipper needs a capacitor and a clamper does not",
                            "a clamper works on sine waves and a clipper on square waves",
                        ],
                        "a": 0,
                        "why": r'''
A clipper is memoryless: give it a voltage and it gives you a voltage, with the top or
the bottom cut off, and the average of what comes out is whatever the cutting left
behind. A clamper is the opposite in every respect: nothing is removed, the peak-to-peak
swing is unchanged, and what moves is where the whole waveform sits. The component that
makes the difference is the capacitor, and it belongs to the *clamper* — there is no
capacitor anywhere in a clipper, only resistors, diodes and whatever sets the bias
level. Both work on any waveform; neither cares what shape it is.
''',
                    },
                    {
                        "q": "A 5.0 V peak sine drives a clamper whose diode holds the output's negative extreme at $-V_F$, with $V_F = 0.7$ V. Where do the two extremes of the output sit?",
                        "opts": [
                            "$-5.0$ V and $+5.0$ V",
                            "$-0.7$ V and $+4.3$ V",
                            "$-0.7$ V and $+9.3$ V",
                            "0 V and $+10.0$ V",
                        ],
                        "a": 2,
                        "why": r'''
The capacitor charges until the trough sits at $-0.7$ V. Nothing has been removed, so
the peak-to-peak swing is still 10 V, and the positive extreme therefore lands at
$-0.7 + 10 = +9.3$ V — which is $2V_{peak}-V_F$, and is exactly why the next stage of a
voltage doubler sees nearly twice the input. Answering $-0.7$ V and $+4.3$ V keeps the
trough right but shrinks the waveform, which a clamper never does; answering $\pm 5.0$ V
is the input, unshifted.
''',
                    },
                    {
                        "q": "Why must a clamper's $R_LC$ be long compared with the period of the signal?",
                        "opts": [
                            "to keep the diode from overheating",
                            "because between clamping instants the capacitor is the only thing holding the shift, and it is discharging into the load the whole time",
                            "to filter out the harmonics the clamping generates",
                            "because a short time constant would clip the waveform instead of shifting it",
                        ],
                        "a": 1,
                        "why": r'''
The diode conducts for a small part of each cycle — just enough to top the capacitor up
at the clamped extreme. For the rest of the cycle the capacitor holds the DC shift on
its own while the load draws current out of it, and the shift decays at exactly module
3's rate, $I_{load}/(fC)$ per cycle. Make $R_LC$ comparable with the period and the
waveform visibly sags between clamps: the DC restoration is then partial and depends on
the signal, which is the failure mode that ruins a video clamp. The diode's dissipation
is negligible here and no harmonics are generated by a circuit that only shifts.
''',
                    },
                    {
                        "q": "A voltage doubler is driven from a 5.0 V peak source and uses two silicon diodes at 0.7 V each. What does it deliver at light load?",
                        "opts": ["10.0 V", "9.3 V", "8.6 V", "4.3 V"],
                        "a": 2,
                        "why": r'''
$2V_{peak}-2V_F = 10 - 1.4 = 8.6$ V. Each stage costs one drop: the clamper's diode
takes 0.7 V off the shift, and the peak detector's takes another 0.7 V off what it
captures. Answering 9.3 V pays for only one of them; answering 10.0 V is the ideal
doubler with no diodes in it at all. The gap between 10.0 and 8.6 is 14% of the output,
which is what makes this a circuit where the choice of diode matters more than the
choice of capacitor.
''',
                    },
                    {
                        "q": "Why do the forward drops matter far more in a voltage multiplier than in a mains rectifier?",
                        "opts": [
                            "because multipliers run at higher frequencies, where the drop is larger",
                            "because a multiplier's diodes carry much more current",
                            "because the drop is a fixed number of volts, so it is a large fraction of a small input swing — and an N-stage ladder pays it N times",
                            "because multipliers use the diodes in reverse breakdown",
                        ],
                        "a": 2,
                        "why": r'''
A forward drop is roughly 0.7 V whatever the circuit around it, so what changes is what
it is 0.7 V *of*. Against a 34 V mains peak two drops are 4% and nobody notices; against
a 5 V logic swing two drops are 14%, and a five-stage ladder from the same source loses
7 V of the 50 it was aiming at. The drop does not grow with frequency and it barely
grows with current — a decade of current is only 60 mV, which is module 2's whole point.
The fix is a diode with a smaller drop, and that is what a Schottky is.
''',
                    },
                ],
            },
            "match": {
                "title": "The four parts of a waveform shaper",
                "minutes": 6,
                "brief": r'''
Clippers, clamps, peak detectors and multipliers are all built from the same four
symbols in different arrangements, and the arrangement is the entire design. Before you
can read one of these circuits off a page you have to be able to say, immediately, which
element is doing which job.

Match each role to the symbol that plays it.
''',
                "prompt": "Pick a role, then tap the symbol that performs it in these circuits.",
                "labels": [
                    "Makes the decision",
                    "Holds the DC shift",
                    "Sets the clipping level",
                    "Lets the shift decay",
                    "What every level is measured from",
                ],
                "items": [
                    {"sym": "D", "a": 0, "why": "The diode. Triangle into a bar, and the bar is the cathode — the "
                     "end current comes out of. Conventional current goes in at the flat back of the "
                     "triangle and out past the bar, in the direction the triangle points; what it will "
                     "not do is go in at the cathode. Every circuit in this module is the same handful of "
                     "passives plus this one asymmetry, and removing it leaves a divider that does nothing "
                     "interesting to any waveform."},
                    {"sym": "C", "a": 1, "why": "The capacitor: two plates that never touch. In a clamper it sits in "
                     "series with the signal and its charge *is* the DC shift; in a peak detector it sits across "
                     "the output and its charge is the remembered peak. Same part, same physics, different place "
                     "in the circuit."},
                    {"sym": "BATT", "a": 2, "why": "A battery — the long bar is the positive terminal. In series with "
                     "the clipping diode it moves the threshold from $V_F$ to $V_{bias}+V_F$. In a real design it "
                     "is almost never a cell; it is a divider off the supply, or a second diode, but the symbol "
                     "tells you what it is doing."},
                    {"sym": "R", "a": 3, "why": "The resistor, drawn as a zig-zag or as a plain rectangle. Here it is "
                     "the load, and it is what makes the difference between a clamper that holds its shift and one "
                     "that sags: the product of this and the capacitance has to be long compared with a period."},
                    {"sym": "GND", "a": 4, "why": "Ground. Worth including because in these circuits it is doing real "
                     "work rather than being bookkeeping: a clamper's diode returns to it, and the clamping level "
                     "is measured from it. Move the ground and you have a different circuit."},
                ],
            },
            "blanks": {
                "title": "A two-sided clipper, and the shift a clamper settles at",
                "minutes": 9,
                "caption": "shapers.py — two functions, four holes",
                "lang": "python",
                "brief": r"""
Both of these are one line of algebra each, but the algebra is the design. The clipper's
holes are about what happens on each side of its two thresholds; the clamper's is the
steady-state offset, which is where every doubler's output voltage comes from.

Nothing is executed here — you are choosing expressions, not writing code.
""",
                "listing": """# Two waveform shapers, in their steady state.
#   V_F            the diode's forward drop while it is conducting
#   R, r_d         the series resistor and the diode's dynamic resistance
#   V_TOP, V_BOT   the two bias batteries, both quoted as positive numbers

def clip(v_in):
    # the top diode conducts
    if v_in > V_TOP + V_F:
        return (V_TOP + V_F) + (v_in - (V_TOP + V_F)) * ___
    # the bottom diode conducts
    if v_in < ___:
        return -(V_BOT + V_F) + (v_in + (V_BOT + V_F)) * (r_d / (R + r_d))
    # neither conducts, so nothing flows in R
    return ___


def clamp_offset(v_peak):
    # A clamper: C in series with the signal, diode from the output to ground
    # with its cathode at the output, so the trough is held at -V_F.
    # In the steady state, v_out = v_in + (this).
    return ___
""",
                "blanks": [
                    {
                        "prompt": "How much of the input's movement still reaches the output once the top diode is conducting.",
                        "hole": "?",
                        "opts": ["R / (R + r_d)", "r_d / (R + r_d)", "1.0", "0.0"],
                        "a": 1,
                        "why": "`r_d / (R + r_d)`. With the diode on, the input drives R into the diode's model and the output is taken across the diode, so the ratio is the diode's share of the series pair — small, which is what makes the clipping nearly flat.",
                        "whys": [
                            "That is the resistor's share of the pair, which is what appears across *R*, not across the diode. It is close to 1, so this version barely clips at all.",
                            "`r_d / (R + r_d)`. The output sits across the diode branch, so it gets the diode's share of the divider: 10/1010 for a 1 k resistor and a 10 ohm diode, or about 1%.",
                            "A slope of 1 means the output follows the input exactly, which is the *unclipped* case. Using it here makes the whole piecewise function the identity and the circuit does nothing.",
                            "A slope of zero is the ideal clipper, perfectly flat. It is a fair first approximation and it is what the constant-drop model gives, but it hides the one per cent that this line exists to expose.",
                        ],
                    },
                    {
                        "prompt": "The input below which the bottom diode takes over.",
                        "hole": "?",
                        "opts": ["-V_BOT", "V_BOT + V_F", "-(V_BOT + V_F)", "-(V_BOT - V_F)"],
                        "a": 2,
                        "why": "`-(V_BOT + V_F)`. The lower branch is the mirror image of the upper one: its battery holds the level at $-V_{BOT}$ and its diode adds another $V_F$ of drop in the direction it conducts, so the threshold sits below both.",
                        "whys": [
                            "The battery alone. It leaves out the diode's own drop, so the model starts clipping $V_F$ too early on the negative side and the two thresholds are no longer symmetric.",
                            "Positive, so this condition is met by every input the *upper* branch was supposed to handle. Both branches would then fire on the same signal and the function returns whichever it tested first.",
                            "`-(V_BOT + V_F)`. The threshold is the battery plus the drop, and the whole thing is negative because this branch handles the bottom of the waveform.",
                            "Subtracting the drop rather than adding it. This is the sign error that makes a clipper look right on a slow sine and wrong on anything with a sharp edge, because the two sides clip at levels that differ by $2V_F$.",
                        ],
                    },
                    {
                        "prompt": "What comes out when neither diode is conducting.",
                        "hole": "?",
                        "opts": ["0.0", "V_TOP + V_F", "v_in * (r_d / (R + r_d))", "v_in"],
                        "a": 3,
                        "why": "`v_in`. With both diodes off nothing is drawing current, so no current flows in R, so R drops no voltage and the output is the input. That is why the series resistor costs nothing in the pass region.",
                        "whys": [
                            "Zero output between the thresholds would be a circuit that passes only the parts of the signal it was built to remove, which is exactly backwards.",
                            "That is the upper clipping level, held all the time. It would flatten the waveform completely rather than only its extremes.",
                            "The divider ratio applies only while the diode is conducting and providing the bottom of that divider. With both diodes off there is nothing for R to divide against.",
                            "`v_in`. An open circuit at the output means no current in R, so no drop across it. The resistor is invisible until a diode turns on and gives it something to work against.",
                        ],
                    },
                    {
                        "prompt": "The DC offset a clamper settles at, once the capacitor has charged.",
                        "hole": "?",
                        "opts": ["v_peak + V_F", "v_peak - V_F", "2 * v_peak - V_F", "-v_peak + V_F"],
                        "a": 1,
                        "why": "`v_peak - V_F`. At the input's negative peak the diode holds the output at $-V_F$, so the capacitor has to be carrying $v_{peak} - V_F$ volts, and it then adds that to every other point of the waveform.",
                        "whys": [
                            "Adding the drop instead of losing it. This puts the trough at $+V_F$ rather than $-V_F$, which is the wrong side of ground and, worse, a level the diode could not have set — it clamps by conducting, and conducting means it drops volts.",
                            "`v_peak - V_F`. Set $v_{out} = -V_F$ at the moment $v_{in} = -v_{peak}$ and the offset falls straight out. It is what makes the positive extreme $2v_{peak}-V_F$, which is the whole input to a doubler's second stage.",
                            "That is the *peak* of the clamped output, not the offset that produced it. Using it here shifts the waveform twice as far and the trough ends up near $+v_{peak}$.",
                            "The right size and the wrong sign, which clamps the waveform downwards instead. It is what you get from the same circuit with the diode turned round, and it is a perfectly good negative clamper — just not this one.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Clipping, clamping and the droop between clamps",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
One memoryless function and two that have to be stepped through time, because the whole
point of a clamper is what it remembers.

- `clip(v_in, v_top, v_bot, v_f, r, r_d)` returns the two-sided clipper's output —
  exactly the piecewise function from the drill above.
- `simulate_clamper(v_peak, f_hz, c, r_load, v_f, cycles, per_cycle)` steps a clamper
  driven by a sine and returns the output at every sample, as a list.
- `simulate_peak_detector(v_peak, f_hz, c, r_load, v_f, cycles, per_cycle)` does the
  same for a peak detector.
- `cycle_stats(samples, per_cycle)` returns the tuple `(mean, peak_to_peak)` of the
  **last `per_cycle` samples** — one whole cycle, after any start-up transient.

## The two models

Both use `dt = 1 / (f_hz * per_cycle)` and run for `cycles * per_cycle` samples, with
`v_in = v_peak * sin(2*pi*f_hz*k*dt)` at sample `k`.

The clamper holds a capacitor voltage `v_c`, the difference between its input side and
its output side:

```text
v_out = v_in - v_c
if v_out < -v_f:                 # the diode conducts and pins the output
    v_out = -v_f
    v_c = v_in + v_f
else:                            # it is off, and the load discharges C
    v_c += v_out / (r_load * c) * dt
record v_out
```

The peak detector holds the output voltage itself:

```text
if v_in - v_f > v:               # the diode conducts and tops the capacitor up
    v = v_in - v_f
else:                            # it is off, and the load discharges C
    v -= v / (r_load * c) * dt
record v
```

Both discharge lines are $C\,dV = -I\,dt$ with the load current taken at the start of
the step, which is the same forward Euler as module 3. Use plain loops: each sample
depends on the one before it.
''',
                "files": [{"name": "main.py", "content": r'''
"""Clipper, clamper and peak detector — one static, two with memory."""

import math


def clip(v_in, v_top, v_bot, v_f, r, r_d):
    """Two-sided clipper output for one input voltage."""
    # TODO: the piecewise function, with slope r_d / (r + r_d) in the clipped regions.
    return 0.0


def simulate_clamper(v_peak, f_hz, c, r_load, v_f, cycles, per_cycle):
    """Step a clamper driven by a sine; return every output sample."""
    dt = 1.0 / (f_hz * per_cycle)
    v_c = 0.0
    out = []
    # TODO: the update from the brief, appending v_out every step.
    return out


def simulate_peak_detector(v_peak, f_hz, c, r_load, v_f, cycles, per_cycle):
    """Step a peak detector driven by a sine; return every output sample."""
    dt = 1.0 / (f_hz * per_cycle)
    v = 0.0
    out = []
    # TODO: the update from the brief, appending v every step.
    return out


def cycle_stats(samples, per_cycle):
    """(mean, peak-to-peak) of the last per_cycle samples."""
    # TODO: slice the tail once, then average it and take max minus min.
    return (0.0, 0.0)


if __name__ == "__main__":
    print("clip(10 V):", clip(10.0, 2.0, 3.0, 0.7, 1000.0, 10.0))
    print("clip(1 V):", clip(1.0, 2.0, 3.0, 0.7, 1000.0, 10.0))
    print("clip(-10 V):", clip(-10.0, 2.0, 3.0, 0.7, 1000.0, 10.0))
    s = simulate_clamper(5.0, 1000.0, 1e-6, 100e3, 0.7, 40, 2000)
    if s:
        print("clamper:", cycle_stats(s, 2000), "min", min(s[-2000:]), "max", max(s[-2000:]))
    p = simulate_peak_detector(5.0, 1000.0, 1e-6, 100e3, 0.7, 40, 2000)
    if p:
        print("peak detector:", cycle_stats(p, 2000))
        print("doubler would give:", 2 * 5.0 - 2 * 0.7, "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Clipper, clamper and peak detector — one static, two with memory."""

import math


def clip(v_in, v_top, v_bot, v_f, r, r_d):
    """Two-sided clipper output for one input voltage."""
    slope = r_d / (r + r_d)
    if v_in > v_top + v_f:
        return (v_top + v_f) + (v_in - (v_top + v_f)) * slope
    if v_in < -(v_bot + v_f):
        return -(v_bot + v_f) + (v_in + (v_bot + v_f)) * slope
    return v_in


def simulate_clamper(v_peak, f_hz, c, r_load, v_f, cycles, per_cycle):
    """Step a clamper driven by a sine; return every output sample."""
    dt = 1.0 / (f_hz * per_cycle)
    v_c = 0.0
    out = []
    for k in range(cycles * per_cycle):
        v_in = v_peak * math.sin(2.0 * math.pi * f_hz * k * dt)
        v_out = v_in - v_c
        if v_out < -v_f:
            v_out = -v_f
            v_c = v_in + v_f
        else:
            v_c += v_out / (r_load * c) * dt
        out.append(v_out)
    return out


def simulate_peak_detector(v_peak, f_hz, c, r_load, v_f, cycles, per_cycle):
    """Step a peak detector driven by a sine; return every output sample."""
    dt = 1.0 / (f_hz * per_cycle)
    v = 0.0
    out = []
    for k in range(cycles * per_cycle):
        v_in = v_peak * math.sin(2.0 * math.pi * f_hz * k * dt)
        if v_in - v_f > v:
            v = v_in - v_f
        else:
            v -= v / (r_load * c) * dt
        out.append(v)
    return out


def cycle_stats(samples, per_cycle):
    """(mean, peak-to-peak) of the last per_cycle samples."""
    tail = samples[-per_cycle:]
    return (sum(tail) / len(tail), max(tail) - min(tail))


if __name__ == "__main__":
    print("clip(10 V):", clip(10.0, 2.0, 3.0, 0.7, 1000.0, 10.0))
    print("clip(1 V):", clip(1.0, 2.0, 3.0, 0.7, 1000.0, 10.0))
    print("clip(-10 V):", clip(-10.0, 2.0, 3.0, 0.7, 1000.0, 10.0))
    s = simulate_clamper(5.0, 1000.0, 1e-6, 100e3, 0.7, 40, 2000)
    if s:
        print("clamper:", cycle_stats(s, 2000), "min", min(s[-2000:]), "max", max(s[-2000:]))
    p = simulate_peak_detector(5.0, 1000.0, 1e-6, 100e3, 0.7, 40, 2000)
    if p:
        print("peak detector:", cycle_stats(p, 2000))
        print("doubler would give:", 2 * 5.0 - 2 * 0.7, "V")
'''}],
                "hints": [
                    "In `clip`, work out `slope = r_d / (r + r_d)` once at the top and use it in both clipped branches. The two branches are mirror images, so if one of them is right the other is the same line with the signs flipped.",
                    "Test `clip` at an input just inside each threshold before you go further: at 2.7 V it must return 2.7 exactly, and at $-3.7$ V it must return $-3.7$ exactly. Getting a jump at the threshold means the offsets in the clipped branch do not match the condition above it.",
                    "In both simulations, append at the **end** of the step, after the update. Appending first shifts every sample by one and quietly changes both statistics.",
                    "The clamper's `v_c` is the capacitor's voltage, not the output. When the diode conducts you set both — the output to $-v_f$ and `v_c` to whatever makes that true, which is `v_in + v_f`.",
                    "`cycle_stats` must slice the tail once and work from the slice. Running the statistics over the whole list includes the start-up, where a clamper is still charging and a peak detector is still climbing from zero.",
                    "If the clamper's mean comes out near zero, the capacitor is never being charged: check the sign in `if v_out < -v_f`. A clamper that never clamps is a series capacitor, and a series capacitor passes the waveform with its DC removed.",
                ],
                "tests": [
                    {"name": "the clipper passes what it should and cuts what it should", "code": r'''
assert abs(clip(1.0, 2.0, 3.0, 0.7, 1000.0, 10.0) - 1.0) < 1e-12, "1 V is between the thresholds"
assert abs(clip(2.7, 2.0, 3.0, 0.7, 1000.0, 10.0) - 2.7) < 1e-12, "2.7 V is exactly at the top threshold"
assert abs(clip(-3.7, 2.0, 3.0, 0.7, 1000.0, 10.0) + 3.7) < 1e-12, "-3.7 V is exactly at the bottom one"
hi = clip(10.0, 2.0, 3.0, 0.7, 1000.0, 10.0)
assert abs(hi - 2.7722772277227725) < 1e-12, f"expected 2.7722772 V at 10 V in, got {hi}"
lo = clip(-10.0, 2.0, 3.0, 0.7, 1000.0, 10.0)
assert abs(lo + 3.7623762376237626) < 1e-12, f"expected -3.7623762 V at -10 V in, got {lo}"
'''},
                    {"name": "the clipped region has the slope the divider says it has", "code": r'''
a = clip(3.0, 2.0, 3.0, 0.7, 1000.0, 10.0)
b = clip(10.0, 2.0, 3.0, 0.7, 1000.0, 10.0)
assert abs((b - a) - 7.0 * 10.0 / 1010.0) < 1e-12, \
    f"seven volts in should move the clipped level by 69.3 mV, got {b - a}"
flat = clip(10.0, 2.0, 3.0, 0.7, 1000.0, 0.0)
assert abs(flat - 2.7) < 1e-12, f"with r_d = 0 the clipping is perfectly flat, got {flat}"
'''},
                    {"name": "the clamper shifts the waveform without changing its size", "code": r'''
s = simulate_clamper(5.0, 1000.0, 1e-6, 100e3, 0.7, 40, 2000)
assert len(s) == 80000, f"cycles * per_cycle samples expected, got {len(s)}"
mean, ptp = cycle_stats(s, 2000)
assert abs(mean - 4.2791636188624445) < 1e-9, f"expected a mean of 4.2791636 V, got {mean}"
assert abs(ptp - 9.978571513858414) < 1e-9, f"expected 9.9785715 V peak to peak, got {ptp}"
tail = s[-2000:]
assert abs(min(tail) + 0.7) < 1e-12, f"the trough must sit exactly at -v_f, got {min(tail)}"
assert abs(max(tail) - 9.278571513858415) < 1e-9, f"expected a peak of 9.2785715 V, got {max(tail)}"
'''},
                    {"name": "and the shift is v_peak - v_f, less whatever the load has drooped", "code": r'''
big = cycle_stats(simulate_clamper(5.0, 1000.0, 10e-6, 100e3, 0.7, 40, 2000), 2000)
assert abs(big[0] - 4.297870414768958) < 1e-9, \
    f"ten times the capacitance should give a mean of 4.2978704 V, got {big[0]}"
assert abs(big[0] - 4.3) < abs(4.2791636188624445 - 4.3), \
    "more capacitance must land closer to the ideal v_peak - v_f = 4.3 V"
heavy = cycle_stats(simulate_clamper(5.0, 1000.0, 1e-6, 10e3, 0.7, 40, 2000), 2000)
assert abs(heavy[0] - 4.108721214822937) < 1e-9, \
    f"a ten times heavier load should give 4.1087212 V, got {heavy[0]}"
assert heavy[1] < 9.978571513858414, \
    "and a heavier load also shrinks the swing, because the sag is not uniform"
'''},
                    {"name": "the peak detector holds the peak, and droops at I/(fC)", "code": r'''
p = simulate_peak_detector(5.0, 1000.0, 1e-6, 100e3, 0.7, 40, 2000)
mean, ptp = cycle_stats(p, 2000)
assert abs(mean - 4.279156445729092) < 1e-9, f"expected a mean of 4.2791564 V, got {mean}"
assert abs(ptp - 0.04189171021811955) < 1e-9, f"expected 41.89 mV of droop, got {ptp}"
assert abs(max(p[-2000:]) - 4.3) < 1e-9, f"the top must be v_peak - v_f = 4.3 V, got {max(p[-2000:])}"
predicted = (mean / 100e3) / (1000.0 * 1e-6)
assert abs(predicted / ptp - 1.0) < 0.05, \
    f"module 3's I/(fC) predicts {predicted} V of droop against the measured {ptp}"
'''},
                    {"name": "a heavier load droops the detector proportionally more", "code": r'''
light = cycle_stats(simulate_peak_detector(5.0, 1000.0, 1e-6, 100e3, 0.7, 40, 2000), 2000)
heavy = cycle_stats(simulate_peak_detector(5.0, 1000.0, 1e-6, 10e3, 0.7, 40, 2000), 2000)
assert abs(heavy[0] - 4.109126803218794) < 1e-9, f"expected a mean of 4.1091268 V, got {heavy[0]}"
assert abs(heavy[1] - 0.384317162804217) < 1e-9, f"expected 384.3 mV of droop, got {heavy[1]}"
assert heavy[1] > 8.0 * light[1], \
    "ten times the load current is very nearly ten times the droop, and the shortfall is " \
    "the mean falling too"
'''},
                ],
            },
        },
        # ---- M9 -----------------------------------------------------------
        {
            "title": "Stored charge, reverse recovery and the snap",
            "summary": "A conducting diode has charge inside it, and that charge has to come back out before the device can block anything. Everything a diode does wrong at speed follows from how long that takes.",
            "concepts": [
                "A conducting pn diode has minority carriers in transit either side of the junction. Module 5 counted them to get $I_S$; what matters here is their total, the **stored charge** $Q = I_F\\tau$. At 100 mA with $\\tau = 1$ µs that is 100 nC — a real quantity of charge sitting inside a part you were treating as a switch.",
                "That charge must leave before the junction can support any reverse voltage at all. It leaves by recombining, which takes a lifetime, or by being carried out, which takes current. Until it has gone the diode is still a short circuit **in the reverse direction**, and the reverse current is set entirely by the external circuit.",
                "The **charge-control model** is the whole story: $dQ/dt = i - Q/\\tau$. Solving it for a diode carrying $I_F$ that is suddenly reversed with $I_R$ gives the storage time $t_s = \\tau\\ln(1+I_F/I_R)$. Reversing harder always clears the charge faster, but what a decade of reverse current buys depends on where you start: from $I_R = I_F$ a factor of ten buys about seven times the speed, because the $1$ in the bracket is still the larger term; below that, with $I_R \\ll I_F$, a decade only subtracts $\\tau\\ln 10$ and the returns really do diminish.",
                "$t_{rr}$ is that storage time plus the transition in which the depletion region re-forms, and $Q_{rr}$ is the charge the external circuit had to supply during it. A **snappy** diode ends the transition abruptly, and the loop inductance turns that $di/dt$ into a voltage spike and a ring at $1/2\\pi\\sqrt{L_{loop}C_j}$; a **soft** one tapers off and does not.",
                "Fast diodes are made by deliberately spoiling the silicon — gold or platinum doping, or electron irradiation — to add recombination centres and cut $\\tau$. The price is a higher forward drop and a higher leakage, both from the same defects. A 1N4007 recovers in a few microseconds and a 1N4148 in 4 ns; they are not the same part with different labels.",
                "A Schottky has no minority carriers to store, so it has no recovery at all, only its junction capacitance. That is module 10, and it is the reason the fastest rectifier in a low-voltage supply is usually not a pn junction.",
                "When a snap cannot be avoided, the response is an RC snubber across the diode: $R_s \\approx \\sqrt{L_{loop}/C_j}$, with $C_s$ three to ten times $C_j$. It costs $C_sV^2f$ of dissipation every cycle, which is why the first fix is always a shorter loop and the snubber is what you add when the layout has run out of improvements.",
            ],
            "read": [
                {
                    "title": "The switch that goes on conducting after you turn it off",
                    "minutes": 15,
                    "body": r'''
An oscilloscope on the cathode of a rectifier in a 100 kHz converter, with a current probe
round its lead. The diode has been carrying 200 mA forward. The circuit reverses it, and
the trace does this:

the current does not go to zero. It goes *negative*, to the 2 A the rest of the circuit
can pull, and sits there for about 95 ns while the voltage across the diode stays near
zero. Then the current collapses to zero in a few nanoseconds, the voltage jumps to the
60 V rail and overshoots it by nearly thirty volts, and the node rings at 75 MHz for a
third of a microsecond.

For 95 nanoseconds the device you were treating as a switch was a short circuit in the
wrong direction. Everything a diode does wrong at speed is in that trace, and all of it
comes from one fact: a conducting diode has charge inside it.

## The charge you have been ignoring

Module 5 counted the minority carriers injected across a forward-biased junction in order
to get $I_S$ from them. What matters here is not their profile but their total. Holes are
being pushed into the n-side at a rate $I_F/q$ per second, and each one survives on
average a lifetime $\tau$ before it recombines. A population fed at a steady rate and
drained by a fixed fraction per unit time settles where the two balance, so the stored
charge is

$$Q = I_F\tau$$

At 200 mA with $\tau = 1$ µs that is 200 nC of charge sitting inside a part with two
leads. Now reverse it. The junction cannot support any reverse voltage while that charge
is still there — an excess of minority carriers at the depletion edge is precisely what
forward bias means, and a junction cannot be forward biased and reverse biased at the same
time. So the diode holds itself at nearly zero volts and conducts backwards, and how much
current flows is decided by the external circuit, not by the diode.

## How long that lasts

The **charge-control model** treats the stored charge as the whole state of the device.
Charge arrives as terminal current, and it leaves by recombination at a rate proportional
to how much is there — which is what a lifetime means. One line:

$$\frac{dQ}{dt} = i(t) - \frac{Q}{\tau}$$

Put $i = -I_R$ into it from the instant of reversal, start from $Q_0 = I_F\tau$, and solve
the first-order equation. The diode can begin to block when $Q$ reaches zero, and that
happens at

$$t_s = \tau\ln\!\left(1 + \frac{I_F}{I_R}\right)$$

This module's derivation, **How long the charge takes to come out**, does those four steps
one at a time. What is worth doing here is reading the result.

```python
import math

tau = 1.0e-6            # minority carrier lifetime, seconds
i_f = 0.200             # forward current before the reversal, amps

q0 = i_f * tau
print("stored charge Q0 = %.0f nC" % (q0 * 1e9))
for i_r in (0.02, 0.2, 2.0, 20.0):
    t_s = tau * math.log(1.0 + i_f / i_r)
    q_rr = i_r * t_s
    print("I_R = %5.2f A   t_s = %8.2f ns   Q_rr = %6.1f nC   %4.1f%% of Q0 came out of the terminals"
          % (i_r, t_s * 1e9, q_rr * 1e9, 100.0 * q_rr / q0))
```

```text
stored charge Q0 = 200 nC
I_R =  0.02 A   t_s =  2397.90 ns   Q_rr =   48.0 nC   24.0% of Q0 came out of the terminals
I_R =  0.20 A   t_s =   693.15 ns   Q_rr =  138.6 nC   69.3% of Q0 came out of the terminals
I_R =  2.00 A   t_s =    95.31 ns   Q_rr =  190.6 nC   95.3% of Q0 came out of the terminals
I_R = 20.00 A   t_s =    9.95 ns   Q_rr =  199.0 nC   99.5% of Q0 came out of the terminals
```

The middle column is the one everyone quotes: pulling harder clears the charge faster, and
the logarithm decides by how much. Between 0.2 A and 2 A, ten times the current bought
7.3 times the speed, because $I_F/I_R$ is 0.1 there and the $1$ inside the bracket is still
the dominant term. Push on to 20 A and the returns are nearly perfect — $\ln(1+x)\to x$
for small $x$, so $t_s\to\tau I_F/I_R$, inversely proportional to the reverse current. It
is at the *gentle* end that the returns genuinely diminish: reverse with 20 mA and you wait
2.4 µs, and a decade of extra current there subtracts only $\tau\ln 10$.

The right-hand column is the one nobody expects. Charge can leave by two routes — through
the terminals, or by recombining inside — and hurrying denies it the second. Pulling ten
times harder cut the *time* by seven and raised the *charge the circuit had to carry away*
from 139 nC to 191 nC. In the limit it approaches the stored charge exactly:
$Q_{rr} = I_R\tau\ln(1+I_F/I_R) \to I_F\tau = Q_0$. There is no reverse current at which
the recovery is free; the fastest turn-off is the one where the external circuit removes
every last coulomb itself.

## What that costs, and why 50 Hz never noticed

A 1N4007 in a mains rectifier recovers in about 2 µs. One mains half-cycle is 10 ms, so
the recovery is one part in five thousand of the period, and it happens while the voltage
across the diode is near zero anyway. Nobody has ever measured it in a 50 Hz supply.

The same 2 µs in a 100 kHz converter is 20% of the period. Nothing about the diode changed;
what changed is what its recovery time is a fraction *of*. Take the trace at the top:
$Q_{rr} = 191$ nC has to be pushed back through the diode while the node swings to 60 V,
once per cycle at 100 kHz. An upper bound on the energy that costs is $Q_{rr}V_R$ per
event, so

$$P \le Q_{rr}V_Rf = 191\ \text{nC} \times 60\ \text{V} \times 10^5\ \text{s}^{-1}
= 1.14\ \text{W}$$

and in practice something like half of it, because the voltage is still rising while some
of the charge comes out. Set that against the forward conduction loss of the same diode:
200 mA at 0.75 V for half the cycle is 75 mW. The switching loss is more than ten times the
conduction loss, and the forward drop — the number on the front page of the data sheet, the
number this course has spent five modules on — is beside the point.

## The snap, and the ring it excites

At the end of the storage time the current has to return to zero, and it does so quickly:
this is a **snappy** diode. Now the circuit takes over, and the two components that matter
are ones nobody fitted. The loop the current was flowing in has inductance — a few
centimetres of wiring is tens of nanohenries — and the diode, now off, is module 7's
junction capacitance.

The loop inductance was carrying 2 A and cannot stop instantly. That energy has to go
somewhere, and the only place is the junction capacitance:

$$\tfrac12 LI_R^2 = \tfrac12 C_jV^2
\qquad\Longrightarrow\qquad
V = I_R\sqrt{\frac{L}{C_j}}$$

The overshoot is the reverse current times $\sqrt{L/C_j}$, the loop's characteristic
impedance. That same square root sets everything else about the ring, which is why the
build, **Damping what the snap leaves behind**, is built around it.

```python
import math

L = 30e-9               # loop inductance, henries
C_J = 150e-12           # the diode off-state junction capacitance, farads
R = 0.5                 # loop resistance, ohms
I_R = 2.0               # amps flowing when the diode snaps off
V_RAIL = 60.0           # volts the node settles at
F_SW = 100e3            # switching frequency, hertz

z0 = math.sqrt(L / C_J)
print("ring frequency  = %.1f MHz" % (1.0 / (2.0 * math.pi * math.sqrt(L * C_J)) / 1e6))
print("z0 = sqrt(L/C)  = %.2f ohm" % z0)
print("Q  = z0 / R     = %.1f" % (z0 / R))
print("overshoot I*z0  = %.1f V on top of %.0f V" % (I_R * z0, V_RAIL))
for c_s in (470e-12, 1.5e-9, 10e-9):
    print("snubber %6.0f pF (%.1f x C_j)  costs C*V^2*f = %.2f W"
          % (c_s * 1e12, c_s / C_J, c_s * V_RAIL ** 2 * F_SW))
```

```text
ring frequency  = 75.0 MHz
z0 = sqrt(L/C)  = 14.14 ohm
Q  = z0 / R     = 28.3
overshoot I*z0  = 28.3 V on top of 60 V
snubber    470 pF (3.1 x C_j)  costs C*V^2*f = 0.17 W
snubber   1500 pF (10.0 x C_j)  costs C*V^2*f = 0.54 W
snubber  10000 pF (66.7 x C_j)  costs C*V^2*f = 3.60 W
```

88 V across a diode on a 60 V rail, and 75 MHz radiating out of every centimetre of the
loop for the 28 cycles the $Q$ allows. That resonance is where most of a switching supply's
radiated emissions come from, and it explains why the *area* of the loop around a rectifier
is a design parameter rather than a layout convenience: the loop is half of the tuned
circuit.

When the layout has run out of improvements, the answer is an RC snubber across the diode.
Both values follow from the same $\sqrt{L/C_j}$. The resistor is chosen near 14 $\Omega$
because that is the impedance at which the loop trades its energy back and forth — much
smaller is nearly a short and lets the loop ring against the snubber capacitor instead,
much larger is nearly an open and the loop rings as though the snubber were not fitted. The
capacitor is chosen at three to ten times $C_j$: less and its own voltage moves as much as
the node it is meant to hold still, more and you are paying $C_sV^2f$ every cycle for
nothing, as the last two rows show.

## The mistake people actually make

Choosing the bigger diode. Asked to rectify 200 mA at 100 kHz, almost everyone reaches for
a 1N4007 over a 1N4148: 1 A against 200 mA, 1000 V against 100 V, and it costs the same. It
is the better part by every number anyone is taught to check.

Its recovery time is a few microseconds. The 1N4148's is 4 ns. At 100 kHz the 4007 spends a
fifth of every cycle conducting backwards and gets hot enough to fail, while the part with a
fifth of the current rating works perfectly.

The trap is well laid, because $t_{rr}$ is often not on a 1N400x data sheet at all — the
part was specified for 50 Hz, where it does not matter, and the omission reads as an absence
of a problem rather than as an absence of a specification. Fast recovery is made by
deliberately spoiling the silicon, with gold, platinum or electron irradiation, to add
recombination centres and cut $\tau$; the same defects raise the forward drop and the
leakage. A fast diode is a compromised diode sold as such, and the compromise is not
visible in the current and voltage ratings.

The second mistake is what people do when they see the spike: fit a larger snubber
capacitor, on the grounds that more must be better. Going from 470 pF to 10 nF buys a
marginal improvement in a peak that was already under control, and 3.6 W instead of 0.17 W.
Snubbing is bought with watts.

## Where this stops holding

**One lifetime is one number, and recovery has a shape.** The charge-control model gives a
storage time and says nothing about how abruptly the current returns to zero afterwards.
Whether a diode is snappy or **soft** depends on the doping profile near the end of the
neutral region, and it is the difference between a ring you must snub and one you can
ignore. Data sheets express it as a softness factor, and the model above has no term for it.

**$t_s$ is not $t_{rr}$.** After the stored charge is gone, the depletion region has to
re-form and $C_j$ has to charge to the reverse voltage. That transition is extra time, it is
where the $dV/dt$ lives, and for a fast diode it can be most of the total.

**The reverse current is not really constant.** The derivation held $I_R$ fixed, which the
external circuit does only approximately: in the loop above, the current ramps at
$di/dt = V/L$, so a stiffer supply or a shorter loop reverses the diode harder and changes
$t_s$ along with everything else. The model is a good estimate and a poor simulation.

**It gets worse when hot.** Carrier lifetime rises with temperature, so the stored charge,
the storage time and $Q_{rr}$ all rise with it, and the recovery loss heats the junction
that made them rise. Data sheets quote $Q_{rr}$ at 25 $^\circ$C, and a doubling by 125
$^\circ$C is ordinary.

**And none of it applies to a Schottky.** There are no stored minority carriers to remove,
so there is no storage time at all — but the junction capacitance is still there, so a
Schottky in the same loop still rings. Module 10 is about what that costs elsewhere.
''',
                },
            ],
            "quiz": {
                "title": "How long a diode stays on after you turn it off",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A diode carrying 200 mA with $\\tau = 1$ µs is suddenly reversed by a circuit that pulls 200 mA out of it. Roughly how long before it can block any voltage?",
                        "opts": ["instantly", "about 693 ns", "about 1 µs", "about 2 µs"],
                        "a": 1,
                        "why": r'''
$t_s = \tau\ln(1+I_F/I_R) = 1\ \mu\text{s} \times \ln 2 = 693$ ns. For the whole of that
time the diode is conducting *backwards* with 200 mA through it and essentially no
voltage across it, because the stored charge is still there and a junction full of
minority carriers cannot support a field. Expecting it to block instantly is the
assumption every ideal-diode analysis makes, and it is the assumption that fails first
when a circuit is asked to run faster.
''',
                    },
                    {
                        "q": "The same diode, same 200 mA forward, but now reversed with 2 A instead of 200 mA. How much faster does the charge clear?",
                        "opts": [
                            "ten times faster, since the current is ten times larger",
                            "about seven times faster",
                            "no faster — the lifetime sets it",
                            "a hundred times faster",
                        ],
                        "a": 1,
                        "why": r'''
$\tau\ln(1+0.2/2) = \tau\ln(1.1) = 95$ ns against 693 ns, a factor of 7.3 for a factor of
10 in current. The logarithm is why it is 7.3 and not 10: at these currents $I_F/I_R$ is
0.1, so the $1$ inside the bracket is still the dominant term and taking the log of the
sum costs you part of the decade. That is not a permanent tax — push on to 20 A and
$t_s$ goes from 95 ns to 9.95 ns, very nearly the full factor of ten, because once
$I_F/I_R$ is small $\ln(1+x)\to x$ and $t_s \to \tau I_F/I_R$, inversely proportional to
the reverse current. The flattening is at the *other* end: reverse gently, with
$I_R \ll I_F$, and a decade of current only takes $\tau\ln 10$ off.
Answering "no faster" goes too
far the other way — the lifetime sets the *scale*, but how hard you pull genuinely
matters, and it is the only lever the circuit designer has once the part is chosen.
Pulling harder also costs you: the snap at the end is sharper.
''',
                    },
                    {
                        "q": "A rectifier works perfectly in a 50 Hz supply. Why does the same part fail in a 100 kHz converter?",
                        "opts": [
                            "its forward drop rises with frequency",
                            "its junction capacitance shorts it out at 100 kHz",
                            "a 2 µs recovery is a ten-thousandth of a 50 Hz cycle and a fifth of a 100 kHz one, so it now conducts backwards for a large part of every cycle",
                            "the package cannot dissipate the extra heat",
                        ],
                        "a": 2,
                        "why": r'''
Nothing about the diode changed; what changed is what its recovery time is a fraction
*of*. A 100 kHz period is 10 µs, so 2 µs of reverse conduction is 20% of every cycle
with the full supply voltage eventually appearing across a device that is passing
current the wrong way. The heat is a symptom rather than the cause — it is that
overlap that produces it, and no package fixes it. The forward drop does not depend on
frequency at all, and 150 pF at 100 kHz is 10.6 k$\Omega$, which shorts nothing that a
rectifier drives.
''',
                    },
                    {
                        "q": "What actually makes a fast recovery diode fast?",
                        "opts": [
                            "recombination centres added on purpose — gold, platinum or electron irradiation — which cut the minority carrier lifetime",
                            "a thinner depletion region, so the carriers cross it faster",
                            "heavier doping on both sides",
                            "a smaller package with less lead inductance",
                        ],
                        "a": 0,
                        "why": r'''
Silicon is deliberately made worse. Every added recombination centre gives a stored
minority carrier somewhere to disappear, which is exactly what cutting $\tau$ means, and
the same centres raise both the forward drop and the leakage — a fast diode is a
compromised diode, sold as such. The transit across the depletion region takes
picoseconds and was never the limit; the wait is for the charge stored in the *neutral*
regions either side. Package inductance matters for the ring afterwards, not for how
long the recovery lasts.
''',
                    },
                    {
                        "q": "A diode snaps off in a loop with 30 nH of inductance, and its junction capacitance is 150 pF. What frequency does the resulting ring sit at?",
                        "opts": ["75 kHz", "7.5 MHz", "75 MHz", "750 MHz"],
                        "a": 2,
                        "why": r'''
$1/2\pi\sqrt{LC} = 1/(2\pi\sqrt{30\times10^{-9} \times 150\times10^{-12}}) = 75$ MHz.
Two components nobody chose — a few centimetres of loop and the junction capacitance
module 7 derived — set a resonance in the VHF band, and the snap excites it hard. This
is where most of a supply's radiated emissions come from, and it is why the loop area
around a rectifier is a design parameter rather than a layout convenience. Getting
75 kHz means 150 pF was read as 150 µF: a factor of $10^6$ in $LC$ is a factor of
$10^3$ in frequency.
''',
                    },
                    {
                        "q": "Your snubber uses 470 pF and works. You fit 10 nF instead, on the grounds that more must be better. The node swings 60 V at 100 kHz. What have you bought?",
                        "opts": [
                            "a little more damping, and 3.6 W of dissipation instead of 0.17 W",
                            "nothing at all — the snubber capacitor does not affect anything",
                            "twice the ring frequency",
                            "half the recovery time",
                        ],
                        "a": 0,
                        "why": r'''
The snubber capacitor is charged and discharged through its resistor once per cycle, so
it dissipates $C_sV^2f$: $470\ \text{pF} \times 60^2 \times 10^5 = 0.17$ W, against
$10\ \text{nF} \times 60^2 \times 10^5 = 3.6$ W. Twenty-one times the heat for a
marginal improvement in a peak that was already under control. The recovery time is a
property of the diode and is untouched by anything you hang across it, and the ring —
what is left of it — moves *down* in frequency with more capacitance, not up. Snubbing
is bought with watts, which is why the first fix is always a shorter loop.
''',
                    },
                ],
            },
            "derive": {
                "title": "How long the charge takes to come out",
                "minutes": 13,
                "vars": ["Q", "Q_0", "I_F", "I_R", "tau", "t", "t_s"],
                "brief": r'''
The **charge-control model** treats the stored minority charge $Q$ as the state of the
device and nothing else. Charge arrives as terminal current and disappears by
recombination, and recombination removes a fixed *fraction* of what is there per unit
time — which is what a lifetime $\tau$ means. So

$$\frac{dQ}{dt} = i(t) - \frac{Q}{\tau}$$

and that single line, integrated once, is the whole of reverse recovery.

The experiment: the diode has been carrying a steady forward current $I_F$ for a long
time. At $t = 0$ the external circuit reverses and holds a steady reverse current $I_R$
through it, which in the sign convention of the equation above means $i = -I_R$.
''',
                "steps": [
                    {
                        "prompt": "Start before $t = 0$. The diode has been carrying $I_F$ for a long time, so nothing is changing. Write the stored charge $Q_0$ at that point.",
                        "given": "$dQ/dt = i - Q/\\tau$, with $dQ/dt = 0$ and $i = I_F$.",
                        "answer": "I_F \\tau",
                        "hint": "Set the derivative to zero and solve the line that is left for $Q$.",
                        "deconstruct": [
                            "In steady state $0 = I_F - Q_0/\\tau$.",
                            "Multiply through by $\\tau$.",
                            "So 100 mA held in a diode with a microsecond of lifetime is 100 nC of stored charge.",
                        ],
                    },
                    {
                        "prompt": "At $t = 0$ the current is forced to $-I_R$ and held there. Write $dQ/dt$ from that instant onwards, in terms of $I_R$, $Q$ and $\\tau$.",
                        "answer": "-I_R - \\frac{Q}{\\tau}",
                        "hint": "Put $i = -I_R$ into the model. Nothing else changes.",
                        "deconstruct": [
                            "The charge is now leaving by two routes at once.",
                            "One is the terminal current, $-I_R$; the other is recombination, $-Q/\\tau$.",
                            "Both terms are negative, which is why the charge falls faster than either mechanism alone would take it.",
                        ],
                    },
                    {
                        "prompt": "That is a first-order linear equation with a constant forcing term, so its solution is a decaying exponential about a steady value. Solve it with the initial condition from step 1, and write $Q(t)$ in terms of $I_F$, $I_R$, $\\tau$ and $t$.",
                        "given": "The general solution of $dQ/dt = -I_R - Q/\\tau$ is $Q = Ae^{-t/\\tau} - I_R\\tau$.",
                        "answer": "\\tau(I_F + I_R)exp(-\\frac{t}{\\tau}) - I_R \\tau",
                        "placeholder": "A exp(-t/tau) - ...",
                        "hint": "Put $t = 0$ into the general solution, set it equal to $Q_0$ from step 1, and solve for $A$.",
                        "deconstruct": [
                            "At $t = 0$ the general solution gives $Q(0) = A - I_R\\tau$.",
                            "Step 1 said $Q(0) = I_F\\tau$, so $A = I_F\\tau + I_R\\tau$.",
                            "Substitute $A$ back in.",
                        ],
                    },
                    {
                        "prompt": "The diode can begin to block only once the stored charge has gone. Set $Q = 0$ and solve for the time, $t_s$.",
                        "answer": "\\tau ln(1 + \\frac{I_F}{I_R})",
                        "hint": "Move the constant term across, divide out the $\\tau$, and take logarithms of both sides.",
                        "deconstruct": [
                            "$\\tau(I_F+I_R)e^{-t_s/\\tau} = I_R\\tau$, and the $\\tau$ on each side cancels.",
                            "$e^{-t_s/\\tau} = I_R/(I_F+I_R)$, so $e^{+t_s/\\tau} = (I_F+I_R)/I_R$.",
                            "Take the natural logarithm, and note that $(I_F+I_R)/I_R$ is $1 + I_F/I_R$.",
                        ],
                    },
                ],
                "closing": r'''
$$t_s = \tau\ln\!\left(1 + \frac{I_F}{I_R}\right)$$

Three things are worth taking from it.

The lifetime is the scale, and it is a property of the silicon. Nothing you do in the
circuit changes it; the only way to a shorter $t_s$ at a given ratio of currents is a
different part, made from silicon that has been deliberately spoiled.

The ratio is a logarithm, and where you sit on it decides what pulling harder is worth.
Reversing a 200 mA forward current with 200 mA gives $\tau\ln 2 = 0.69\tau$; with 2 A it
gives $\tau\ln 1.1 = 0.095\tau$ — ten times the current for seven times the speed,
because the $1$ in the bracket is still doing most of the work. Beyond that the
logarithm stops charging you: $\ln(1+x)\to x$ for small $x$, so at 20 A $t_s$ is
$0.00995\tau$ and every further decade of $I_R$ buys nearly the full decade of speed.
It is at the gentle end, $I_R \ll I_F$, that the returns genuinely diminish, a decade of
current subtracting only $\tau\ln 10$. And the harder you pull, the more abruptly the
current has to come back to zero at the end,
which is the snap that makes the ring.

And $t_s$ is not the whole of $t_{rr}$. After the charge is gone the depletion region has
to re-form and the junction capacitance has to charge to the reverse voltage; that is the
transition time, it is where the $dV/dt$ lives, and the ratio of the two is what a data
sheet calls the softness factor.
''',
            },
            "build": {
                "title": "Damping what the snap leaves behind",
                "minutes": 28,
                "brief": r'''
The recovery ends with the current going abruptly to zero. What happens next has nothing
to do with the diode's physics and everything to do with what it is wired into: the loop
inductance and the junction capacitance are a resonant circuit, and the snap kicks it.

## The circuit

This is that loop, drawn small-signal so the solver can sweep it. A source drives
**30 nH** of loop inductance and **0.5 $\Omega$** of loop resistance into the diode's
off-state junction capacitance of **150 pF**, and the probe is on the diode's node.
Those three numbers give

$$f_{ring} = \frac{1}{2\pi\sqrt{L C_j}} = 75\ \text{MHz},
\qquad Q = \frac{1}{R}\sqrt{\frac{L}{C_j}} = 28$$

so the node rings at 75 MHz, and 28 is its $Q$ — the resonant gain the sweep below
measures. A snap is a step rather than a sine, so what you would see on a probe is an
overshoot to nearly twice the off-state voltage followed by a ring that takes of order
$Q$ cycles to die away: on a 60 V node, about 120 V of overshoot and a third of a
microsecond of 75 MHz radiating out of every centimetre of the loop. Damping is
measured as $Q$ because $Q$ is what says how long it lasts.

## What to add

An **RC snubber** — a resistor in series with a capacitor — from the diode's node to
ground. Both values are yours to choose.

## What has to be true

- the peak of the response, anywhere between 1 MHz and 1 GHz, must be **no more than
  2.0 times** the drive
- the snubber capacitor must be **three to ten times** the 150 pF junction capacitance
- the snubber resistor must be within about a factor of two of the loop's
  characteristic impedance $\sqrt{L/C_j}$ — that is, between **7 $\Omega$ and 25 $\Omega$**

## Why those bounds are the design and not a formality

The characteristic impedance $\sqrt{L/C_j} = \sqrt{30\ \text{nH}/150\ \text{pF}} =
14.1\ \Omega$ is the impedance the ring circulates energy at. A resistor much smaller
than that is nearly a short and lets the loop ring against the snubber capacitor
instead; much larger and it is nearly an open and the loop rings as if it were not
there. Damping is best when the resistance matches the impedance it is damping.

The capacitor has to be large enough to hold the ring's energy without its own voltage
moving much — under about three times $C_j$ and it simply joins the resonance rather
than damping it — and small enough that you can afford $C_sV^2f$ every cycle. At 60 V
and 100 kHz that is 0.17 W for 470 pF and 3.6 W for 10 nF.

You cannot pass this by deleting the junction capacitance, and check one says so. The
ring is not a modelling artefact; it is what the part does.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                        {"id": "p2", "kind": "L", "x": 7, "y": 7, "rot": 0, "value": 30e-9},
                        {"id": "p3", "kind": "R", "x": 11, "y": 7, "rot": 0, "value": 0.5},
                        {"id": "p4", "kind": "C", "x": 15, "y": 9, "rot": 1, "value": 150e-12},
                        {"id": "p5", "kind": "GND", "x": 15, "y": 11},
                        {"id": "p9", "kind": "OUT", "x": 13, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 9], "b": [3, 10]},
                        {"a": [3, 7], "b": [6, 7]},
                        {"a": [8, 7], "b": [10, 7]},
                        {"a": [12, 7], "b": [15, 7]},
                        {"a": [15, 7], "b": [15, 8]},
                        {"a": [15, 10], "b": [15, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                        {"id": "p2", "kind": "L", "x": 7, "y": 7, "rot": 0, "value": 30e-9},
                        {"id": "p3", "kind": "R", "x": 11, "y": 7, "rot": 0, "value": 0.5},
                        {"id": "p4", "kind": "C", "x": 15, "y": 9, "rot": 1, "value": 150e-12},
                        {"id": "p5", "kind": "GND", "x": 15, "y": 11},
                        {"id": "p6", "kind": "R", "x": 19, "y": 9, "rot": 1, "value": 15},
                        {"id": "p7", "kind": "C", "x": 19, "y": 12, "rot": 1, "value": 470e-12},
                        {"id": "p8", "kind": "GND", "x": 19, "y": 14},
                        {"id": "p9", "kind": "OUT", "x": 13, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 9], "b": [3, 10]},
                        {"a": [3, 7], "b": [6, 7]},
                        {"a": [8, 7], "b": [10, 7]},
                        {"a": [12, 7], "b": [15, 7]},
                        {"a": [15, 7], "b": [15, 8]},
                        {"a": [15, 10], "b": [15, 11]},
                        {"a": [15, 7], "b": [19, 7]},
                        {"a": [19, 7], "b": [19, 8]},
                        {"a": [19, 10], "b": [19, 11]},
                        {"a": [19, 13], "b": [19, 14]},
                    ],
                },
                "checks": [
                    {"name": "the ringing loop is still intact, and a snubber has been added to it", "code": r'''
const ls = c.values('L');
c.assert(ls.length === 1 && Math.abs(ls[0] - 30e-9) <= 30e-9 * 0.03,
  'The 30 nH of loop inductance must still be there and must not be edited. It is not a ' +
  'component anyone fitted, it is the wiring, and shrinking it on the schematic is a way ' +
  'of pretending the layout is better than it is.');
const cs = c.values('C');
c.assert(cs.length === 2,
  'Two capacitors expected — the diode\'s 150 pF junction capacitance and the snubber\'s ' +
  '— and there are ' + cs.length + '. The junction capacitance is what the ring resonates ' +
  'against; deleting it removes the problem from the model and not from the board.');
const dev = cs.filter(function (v) { return Math.abs(v - 150e-12) <= 150e-12 * 0.03; });
c.assert(dev.length === 1,
  'One of the two capacitors has to be the 150 pF junction capacitance, untouched. ' +
  'Found ' + dev.length + ' at that value.');
const rs = c.values('R');
c.assert(rs.length === 2,
  'Two resistors expected — the 0.5 ohm of loop resistance and the snubber\'s — and ' +
  'there are ' + rs.length + '.');
c.assert(rs.filter(function (v) { return Math.abs(v - 0.5) <= 0.05; }).length === 1,
  'The 0.5 ohm loop resistance must still be there. Raising it damps the ring on the ' +
  'schematic, but on the board it is the diode\'s own bulk resistance plus the winding ' +
  'and the copper, and you do not get to choose it.');
'''},
                    {"name": "nothing anywhere in the sweep rings above twice the drive", "code": r'''
let peak = 0, at = 0;
for (let i = 0; i <= 800; i++) {
  const f = 1e6 * Math.pow(1000, i / 800);
  const g = c.gain(f);
  if (g > peak) { peak = g; at = f; }
}
c.assert(peak <= 2.0 * 1.01,
  'The response peaks at ' + peak.toFixed(2) + ' times the drive, at ' +
  c.fmt(at, 'Hz') + '. Undamped this loop peaks at 28; the specification is 2.0. If you ' +
  'are near 8, the snubber is a capacitor with no resistance in series and it has simply ' +
  'moved the resonance down.');
'''},
                    {"name": "the snubber capacitor is three to ten times the junction capacitance", "code": r'''
const cs = c.values('C');
const snub = cs.filter(function (v) { return Math.abs(v - 150e-12) > 150e-12 * 0.03; });
c.assert(snub.length === 1,
  'Exactly one capacitor that is not the 150 pF junction capacitance; found ' + snub.length +
  '. A snubber capacitor equal to C_j joins the resonance instead of damping it.');
const ratio = snub[0] / 150e-12;
c.assert(ratio >= 3.0 * 0.99,
  'The snubber capacitor is ' + ratio.toFixed(2) + ' times the junction capacitance. Below ' +
  'about three times, its own voltage moves as much as the node it is supposed to be ' +
  'holding still, and it becomes part of the tuned circuit rather than a damper on it.');
c.assert(ratio <= 10.0 * 1.01,
  'The snubber capacitor is ' + ratio.toFixed(2) + ' times the junction capacitance. Every ' +
  'cycle it is charged and discharged through the snubber resistor, at a cost of C*V^2*f — ' +
  '0.17 W at 470 pF and 0.54 W at ten times C_j, on a 60 V node at 100 kHz, and rising in ' +
  'proportion from there.');
'''},
                    {"name": "the snubber resistor is near the loop's characteristic impedance", "code": r'''
const rs = c.values('R');
const snub = rs.filter(function (v) { return Math.abs(v - 0.5) > 0.05; });
c.assert(snub.length === 1,
  'Exactly one resistor that is not the 0.5 ohm loop resistance; found ' + snub.length + '.');
const z0 = Math.sqrt(30e-9 / 150e-12);
c.assert(snub[0] >= 7.0 * 0.99 && snub[0] <= 25.0 * 1.01,
  'The snubber resistor is ' + c.fmt(snub[0], 'ohm') + '. The loop circulates its energy ' +
  'at sqrt(L/C_j) = ' + z0.toFixed(1) + ' ohms, and damping works best when the resistance ' +
  'is near that: much smaller is nearly a short and much larger is nearly an open, and ' +
  'both let the loop ring.');
'''},
                ],
                "hints": [
                    "Work out $\\sqrt{L/C_j}$ first: $\\sqrt{30\\times10^{-9}/150\\times10^{-12}} = \\sqrt{200} = 14.1\\ \\Omega$. The nearest standard values inside the window are 15 $\\Omega$ and 22 $\\Omega$, and both work.",
                    "Then the capacitor: three to ten times 150 pF is 450 pF to 1.5 nF. 470 pF is the obvious standard value; 1 nF also passes and damps a little harder.",
                    "Build the snubber as a chain from the diode's node: down through the resistor, down through the capacitor, then to ground. Neither part is polarised, so the order does not matter electrically — but keep it visually next to the node it is protecting, because on a real board the snubber's own loop has to be short too.",
                    "Type the values plainly: `15` for the resistor and `470p` for the capacitor. The editor understands `n` and `p` as well as bare numbers.",
                    "If the peak check reports something near 8 rather than near 1.5, there is a capacitor across the node with no resistor in series with it. That is not a snubber, it is more junction capacitance, and it moves the ring down to about 23 MHz rather than damping it.",
                ],
            },
        },
        # ---- M10 ----------------------------------------------------------
        {
            "title": "Schottky, LED and photodiode: junctions that are not silicon pn",
            "summary": "Three devices that keep the rectifying junction and change something else — the material on one side, the band gap, or the direction light goes — and what each change costs.",
            "concepts": [
                "A **Schottky** diode is a metal on lightly doped silicon. There is still a barrier and still rectification, but the current is carried across it by *majority* carriers, thermionically. Nothing is stored, so there is nothing to recover: module 9's whole problem does not arise, and only the junction capacitance is left.",
                "Its saturation current is four to six orders of magnitude larger than a pn junction's, so the same current arrives at 0.3 to 0.45 V instead of 0.7 V. Those two facts are one fact: $\\Delta V_F = V_T\\ln(I_{S2}/I_{S1})$, so saving 0.35 V of forward drop means $I_S$ larger by $e^{0.35/0.02585} = 7.6\\times10^5$ — and the reverse leakage is larger by the same factor. A Schottky is not a better diode; it is the same trade made differently, and its breakdown is lower too, typically 20 to 100 V.",
                "An **LED** is a junction in a direct-gap compound — AlGaInP, InGaN — where a recombining electron gives its energy to a photon rather than to the lattice. The photon's energy is the band gap, so $E_g[\\text{eV}] = 1240/\\lambda[\\text{nm}]$, and the forward voltage follows the *colour* rather than the semiconductor's reputation: about 1.9 V for red at 630 nm, and 2.67 V at the very least for blue at 465 nm.",
                "That is a hard floor, not a preference. No arrangement of resistors will light a blue LED from a single 1.5 V cell, which is why a blue torch has a boost converter in it and a red one does not.",
                "LEDs are current-driven for module 2's reason and paralleled at your peril for module 6's. Two nominally identical parts *modelled* as 1.85 V and 1.95 V in series with 12 $\\Omega$, sharing one resistor at 20 mA, split it 14.1 mA and 5.8 mA — 2.4:1 in brightness and in ageing. Give each its own ballast.",
                "That 2.4:1 is the straight line's answer, and the junctions themselves are worse: **6.92:1**. Two LEDs on one node are held at one voltage, so $I_A/I_B = I_{SA}/I_{SB}$ exactly — the ratio of the saturation currents, and therefore the same number whatever ballast is chosen, measured unchanged from 50 $\\Omega$ to 10 k$\\Omega$. The linearised model cannot express that at all, because it makes the ratio depend on the node voltage. The second build measures both.",
                "A **photodiode** is the same junction run backwards with light making the carriers. The photocurrent is proportional to optical power and almost independent of the reverse voltage, so the small-signal model is a current source in parallel with $C_j$ — which makes module 7's capacitance the thing that sets its speed. Its **responsivity** is $R = \\eta q\\lambda/hc$, or $\\eta\\lambda[\\mu\\text{m}]/1.24$ A/W, about 0.6 A/W for silicon at 900 nm.",
                "Reverse bias it — photoconductive mode — and $C_j$ shrinks, the response is fast and linear, and you pay in dark current. Leave it at zero volts — photovoltaic mode — and the dark current vanishes while $C_j$ is at its largest and the device is slow. Push the same curve into the fourth quadrant, delivering power rather than absorbing it, and it is a solar cell.",
            ],
            "read": [
                {
                    "title": "Three junctions, three trades, and no free improvements",
                    "minutes": 13,
                    "body": r'''
A Schottky diode drops 0.35 V where a silicon pn junction drops 0.70 V, at the same
current. It also switches with no recovery delay at all, where the pn junction needs
hundreds of nanoseconds. Read those two sentences on a data sheet and the obvious
conclusion is that the Schottky is simply the better part.

It is not. It is the *same* device with one number moved, and the arithmetic that shows
this is one line of module 2.

## The Schottky, and the price of its low drop

Replace the p-side of the junction with a metal. There is still a barrier at the
interface, still rectification — but the current across it is carried by **majority**
carriers, thermionically, over the barrier. Nothing is injected into the other side and
stored there, so there is nothing to remove when the device turns off. Module 9's entire
problem simply does not arise; only the junction capacitance is left.

The barrier is also lower, and a lower barrier means a much larger $I_S$. Now invert
module 2's equation to see exactly how much larger. At the same current:

$$\Delta V_F = V_T\ln\frac{I_{S2}}{I_{S1}}
\quad\Longrightarrow\quad
\frac{I_{S2}}{I_{S1}} = e^{\Delta V_F/V_T} = e^{0.35/0.025852} = e^{13.54} = 7.6\times10^{5}$$

Saving 350 mV of forward drop *requires* a saturation current three quarters of a million
times larger. That is not a coincidence of manufacture; it is the same equation read in
the other direction, and there is no process that gives you one without the other.

And $I_S$ is the reverse leakage. So a Schottky leaks microamps where a silicon diode
leaks nanoamps, and it always did — this is a property of the part on the day you bought
it, not a fault it develops. Its breakdown is lower too, typically 20 to 100 V against a
1N4007's 1000 V.

(The measured ratio is smaller than $7.6\times10^5$, and it is worth knowing why. Module 6
showed that a silicon diode's *measured* leakage is dominated by generation inside the
depletion region and is already far above its ideal $I_S$. So the comparison is between a
Schottky's $I_S$ and a quantity that is not the pn junction's $I_S$ at all. The direction
and the mechanism are exactly as derived; the factor is not.)

**Worked comparison.** A 1 A rectifier on a 5 V rail:

```text
                  silicon pn        Schottky
forward drop      0.75 V            0.35 V
loss at 1 A       0.75 W            0.35 W        of 5 W delivered: 15% vs 7%
reverse leakage   ~1 uA             ~200 uA       at 85 C, tens of times worse again
recovery          ~500 ns           none
```

For a 5 V supply the Schottky wins on the only number anyone is counting — half the loss.
Put the same two parts in a battery-powered circuit that idles for months and the
200 $\mu$A is a permanent drain that empties the battery while the product sits on a
shelf, and the pn junction wins. Neither is a better diode.

## The LED: the forward voltage is the colour

Silicon has an **indirect** band gap, which means an electron crossing it must trade
momentum with the lattice as well as energy. That interaction goes to heat. Silicon does
not emit light and no amount of engineering makes it.

A **direct-gap** compound — AlGaInP, InGaN — lets a recombining electron hand its whole
energy to a photon. That energy is the band gap, and photon energy and wavelength are
related by $E = hc/\lambda$, which in the units anyone actually uses is

$$E_g[\text{eV}] = \frac{1240}{\lambda[\text{nm}]}$$

An electron cannot emit a photon of energy $E_g$ unless it has fallen through at least
$E_g/q$ volts. So the forward voltage follows the **colour**, and nothing else:

```text
red      630 nm    1240/630 = 1.97 eV     ->  measures about 1.9-2.0 V
green    525 nm    1240/525 = 2.36 eV     ->  measures about 2.2-2.4 V
blue     465 nm    1240/465 = 2.67 eV     ->  measures about 3.0 V at 20 mA
```

That is a floor set by physics, not a preference of the manufacturer. No arrangement of
resistors lights a blue LED from a single 1.5 V cell — which is why a blue torch contains
a boost converter and a red one contains a resistor. The measured values sit above the
floor because the junction needs bias beyond the gap to pass useful current, and because
of series resistance.

## Worked example: why two LEDs must not share one resistor

Two nominally identical LEDs, data sheet 1.9 V typical, in parallel behind one resistor
delivering 20 mA. Model them as module 2 would: a fixed drop in series with a resistance.
Manufacturing spread puts one at 1.85 V and the other at 1.95 V, both with 12 $\Omega$.

They share a node, so they share a voltage. Write the node equation:

$$\frac{V - 1.85}{12} + \frac{V - 1.95}{12} = 0.020
\quad\Longrightarrow\quad 2V - 3.80 = 0.24
\quad\Longrightarrow\quad V = 2.02\ \text{V}$$

$$I_1 = \frac{2.02 - 1.85}{12} = 14.1\ \text{mA}
\qquad I_2 = \frac{2.02 - 1.95}{12} = 5.8\ \text{mA}$$

A 100 mV spread — entirely ordinary, and well inside any data sheet's tolerance — became
a **2.4 : 1** split in current, and therefore in brightness and in ageing rate. The one
that needs *less* voltage takes more current, gets hotter, and module 6's coefficient
moves its curve further down still. Give each LED its own ballast resistor. It costs one
component and it is not optional.

The two builds close this out by measuring the same pair of parts twice. **Two LEDs that
are meant to look the same** uses the straight-line model above and finds the 2.4 : 1
split; **The same two LEDs, with the junctions left in** puts the exponentials back and
finds 6.92 : 1, because two junctions held at one voltage divide the current in the ratio
of their saturation currents and nothing else — the same number whatever ballast you feed
them through. The linearised model cannot even express that, which is a fair warning
about how far a tangent travels.

## The photodiode: the same junction, run backwards

Reverse-bias a junction and light it. Photons absorbed in the depletion region create
electron-hole pairs, and the field that was there anyway sweeps them out. The result is a
current proportional to optical power and almost independent of the reverse voltage — a
**current source**, in parallel with the junction capacitance from module 7.

Its **responsivity** is amps out per watt in. Each photon of energy $hc/\lambda$ that is
absorbed yields, with probability $\eta$, one electron of charge $q$:

$$R = \frac{\eta q\lambda}{hc} = \frac{\eta\,\lambda[\mu\text{m}]}{1.24}\ \text{A/W}$$

Note that a *perfect* detector's responsivity rises with wavelength — longer photons carry
less energy, so a watt of them is more photons per second. Silicon's climbs to about
0.6 A/W at 900 nm and then falls off a cliff, because past 1100 nm a photon no longer has
$E_g$ and is not absorbed at all.

**Worked example.** A silicon photodiode with $R = 0.6$ A/W at 900 nm, $C_j = 20$ pF at
zero bias, receiving 10 $\mu$W, into a 100 k$\Omega$ load:

```text
photocurrent    0.6 x 10e-6            = 6 uA
signal          6e-6 x 100e3           = 0.6 V
bandwidth       1/(2 pi x 1e5 x 20e-12) = 79.6 kHz
```

Now reverse-bias it. Module 7's result — the depletion region widens, so $C_j = \epsilon
A/W$ falls — takes 20 pF to about 5 pF at 10 V, and the bandwidth rises in exact
proportion to **318 kHz**. Four times the speed, and the signal is unchanged, because the
photocurrent did not care about the bias.

That exchange is the whole of this module's design problem, **How fast a photodiode can
be, and what that costs in signal**, where a 50 pF diode and a 250 kHz requirement leave
exactly one value of load resistor and a signal of 28 mV to show for it.

What it costs is dark current. Bias is what makes leakage flow, and leakage adds shot
noise that sets the noise floor. So:

- **Photoconductive** (reverse biased): fast, linear over a wide range, noisier.
- **Photovoltaic** (zero bias): no dark current, lowest noise floor, and slow, because
  $C_j$ is at its largest.

A low-light instrument chooses the second deliberately. Push the same device into the
fourth quadrant — delivering power rather than absorbing it — and it is a solar cell.

## The mistake people actually make

Reading responsivity as an efficiency. 0.50 A/W is not "50% efficient": it is amps per
watt, its units are not dimensionless, and its value depends on the wavelength as much as
on the quality of the device. Invert the formula to get the efficiency:

$$\eta = \frac{R \times 1.24}{\lambda[\mu\text{m}]} = \frac{0.50\times1.24}{0.85} = 0.73$$

73%, not 50%. The temptation is strong because the number looks like a percentage when it
is written as 0.50, and because a figure of merit that is *nearly* an efficiency is worse
than one that could never be mistaken for one.

The broader version of the same mistake runs through all three devices in this module:
treating a specification as a virtue rather than as one end of a trade. The Schottky's
0.35 V is bought with leakage. The blue LED's brightness is bought with a forward voltage
that will not run from a cell. The photodiode's bandwidth is bought with dark current.
Each one is the same junction with a knob turned, and turning a knob moves everything
attached to it.

## Where this stops holding

- **Schottky leakage is strongly temperature dependent, and worse than silicon's.** The
  barrier is lower, so the same 10 K that quadruples a pn junction's ideal $I_S$ does more
  damage here relative to the current being measured. A Schottky that leaks 200 $\mu$A at
  25 $^\circ$C can leak milliamps at 100 $^\circ$C, and in a hot rectifier that leakage is
  itself a heat source — which is a positive feedback loop of exactly module 6's kind.
- **$E_g = 1240/\lambda$ gives the peak, not the spread.** An LED emits over a band of
  tens of nanometres, because carriers are distributed in energy by roughly $kT$ above the
  band edge. A white LED is not a band gap at all: it is a blue die with a phosphor on top,
  and its forward voltage is blue's.
- **The photodiode model has no series resistance and no amplifier.** A 100 k$\Omega$ load
  resistor is the simplest possible receiver and almost never the right one; a
  transimpedance amplifier holds the diode at a constant voltage, which removes the
  $R_LC_j$ limit entirely and replaces it with a stability problem involving the same
  $C_j$.
- **The junction capacitance is module 7's, exponent and all.** $C_j$ falls as
  $(1+V_R/V_{bi})^{-m}$, not linearly, so "four times the bias, four times the speed" is a
  coincidence of the numbers chosen above, not a rule.
''',
                },
            ],
            "quiz": {
                "title": "The same junction, changed on purpose",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A Schottky drops 0.35 V where a silicon pn junction drops 0.70 V at the same current, both with $n = 1$ at 300 K. What does that say about their saturation currents?",
                        "opts": [
                            "the Schottky's is about 760 000 times larger",
                            "the Schottky's is twice as large",
                            "the Schottky's is half as large",
                            "they are the same — the difference is in the series resistance",
                        ],
                        "a": 0,
                        "why": r'''
$V = V_T\ln(I/I_S)$, so at the same $I$ a difference of 0.35 V is a ratio of
$e^{0.35/0.025852} = e^{13.54} = 7.6\times10^5$ in $I_S$. Answering "twice as large"
applies the ratio of the voltages to $I_S$, which is the same error as expecting a diode
at twice the voltage to pass twice the current. And it is not series resistance: at
these currents a couple of tens of milliohms would account for microvolts, not for
350 mV.
''',
                    },
                    {
                        "q": "What does that enormous $I_S$ do to the Schottky's reverse leakage?",
                        "opts": [
                            "nothing — leakage and forward drop are unrelated",
                            "it raises it by the same factor, which is why Schottkys leak microamps where silicon leaks nanoamps",
                            "it lowers it, because the barrier is thinner",
                            "it raises it, but only above 100 °C",
                        ],
                        "a": 1,
                        "why": r'''
The reverse current of an ideal junction *is* $I_S$, so the same number that sets the
forward drop sets the leakage, and the two cannot be chosen independently. Microamps
instead of nanoamps sounds harmless until it meets a high-impedance node — which is
module 6's build, exactly — or until it is multiplied by a rail voltage in a battery
circuit and works out as a permanent drain. It is worse hot, but it is already there
cold: this is the trade a Schottky makes, not a defect it develops.
''',
                    },
                    {
                        "q": "An InGaN LED emits at 465 nm. What is the least forward voltage that could light it at all?",
                        "opts": ["0.7 V, like any diode", "1.5 V", "2.67 V", "3.6 V"],
                        "a": 2,
                        "why": r'''
$E_g = 1240/465 = 2.67$ eV, and an electron cannot emit a 2.67 eV photon on its way
across a junction that has dropped less than 2.67 V across it. So no series resistor,
however small, will light this LED from a single alkaline cell — the physics is in the
way, not the circuit. Measured parts sit higher still, around 3.0 V at 20 mA, once the
series resistance and the extra bias needed for useful current are included. The 0.7 V
answer is silicon's number, and silicon has an indirect gap of 1.12 eV and does not
emit light at all.
''',
                    },
                    {
                        "q": "Two nominally identical LEDs, modelled as 1.85 V and 1.95 V in series with 12 $\\Omega$ each, are wired in parallel behind one resistor that delivers 20 mA in total. How does the current split?",
                        "opts": [
                            "10 mA each, since they are the same part",
                            "about 14 mA and 6 mA, with the larger share going to the lower $V_F$",
                            "about 14 mA and 6 mA, with the larger share going to the higher $V_F$",
                            "about 18 mA and 2 mA",
                        ],
                        "a": 1,
                        "why": r'''
Both sit at the same node voltage, 2.02 V, so the currents are $(2.02-1.85)/12 = 14.1$ mA
and $(2.02-1.95)/12 = 5.8$ mA. The one that needs *less* voltage takes more current —
which is the same asymmetry as module 6's hot diode, arriving here through manufacturing
spread rather than through temperature, and then made worse by it, because the one
carrying 14 mA is also the one getting hot. A 100 mV data-sheet spread is entirely
ordinary, and it is why LEDs are ballasted individually.
''',
                    },
                    {
                        "q": "A silicon photodiode has a responsivity of 0.50 A/W at 850 nm. What quantum efficiency is that?",
                        "opts": ["50%", "73%", "100%", "42%"],
                        "a": 1,
                        "why": r'''
Responsivity is $\eta q\lambda/hc$, which in convenient units is
$\eta\lambda[\mu\text{m}]/1.24$ A/W. Inverting, $\eta = 0.50 \times 1.24/0.85 = 0.73$.
Answering 50% reads the responsivity as a percentage, which it is not — it is amps per
watt, and its value depends on the wavelength as well as on how good the device is.
Notice that the responsivity of a *perfect* detector rises with wavelength, because each
photon carries less energy and so a watt of light is more photons per second; that is
why silicon's responsivity climbs to 900 nm before the band gap cuts it off.
''',
                    },
                    {
                        "q": "Why is a photodiode usually run with a reverse bias across it rather than at zero volts?",
                        "opts": [
                            "so that it conducts",
                            "to increase the responsivity",
                            "because the wider depletion region means less $C_j$, and $C_j$ is what limits the speed",
                            "to keep the dark current down",
                        ],
                        "a": 2,
                        "why": r'''
Module 7's result, put to work: reverse bias widens the depletion region, $C_j =
\epsilon A/W$ falls, and the bandwidth into any load resistance rises in proportion. The
bias also keeps the response linear over a wide range of light levels. What it does not
do is help with the dark current — it makes that *worse*, and choosing zero bias is
exactly how a low-light instrument buys a lower noise floor by accepting a slower
detector. Responsivity is set by the quantum efficiency and the wavelength, and hardly
moves with bias at all.
''',
                    },
                ],
            },
            "numeric": {
                "title": "How fast a photodiode can be, and what that costs in signal",
                "minutes": 8,
                "brief": r'''
A photodiode with nothing but a resistor after it is the simplest optical receiver there
is, and the only design decision in it is the value of that resistor. The photocurrent
through it is your signal, so a large resistor is a large signal. The junction
capacitance is across it, so a large resistor is also a low bandwidth. Both of those are
one line of arithmetic; the interesting part is that they point in opposite directions.
''',
                "prompt": "What is the largest load resistor that still meets the bandwidth requirement?",
                "note": "Give the answer in kilohms, to two decimal places.",
                "figure": "A silicon photodiode is reverse biased, where its junction capacitance is 50 pF. "
                          "Its responsivity at 850 nm is 0.55 A/W, and 4.0 µW of light falls on it. Its "
                          "photocurrent flows into a load resistor to ground, and the voltage across that "
                          "resistor is the output. The receiver must have a bandwidth of at least 250 kHz.",
                "given": [
                    {"label": "Junction capacitance", "value": "50 pF"},
                    {"label": "Responsivity at 850 nm", "value": "0.55 A/W"},
                    {"label": "Optical power", "value": "4.0 µW"},
                    {"label": "Bandwidth required", "value": "250 kHz"},
                ],
                "aside": "The photodiode is a current source in parallel with its junction capacitance, so "
                         "what the load resistor sees is a first-order low-pass: $R$ and $C_j$, and nothing "
                         "else in the circuit.",
                "answer": 12.73,
                "tol": 0.15,
                "unit": "kΩ",
                "hint": "The corner is at $f = 1/2\\pi RC_j$. Set that equal to 250 kHz and solve for $R$; "
                        "the responsivity and the optical power do not enter this part at all.",
                "wrong": "If you got 80 k$\\Omega$, the $2\\pi$ went missing: $1/(RC)$ is a rate in radians "
                         "per second, not a frequency in hertz. If you got 12.73 $\\Omega$, the picofarads "
                         "went in as nanofarads.",
                "why": "$R = 1/(2\\pi f C_j) = 1/(2\\pi \\times 250\\times10^3 \\times 50\\times10^{-12}) = "
                       "12.73$ k$\\Omega$. Now look at what that buys: the photocurrent is "
                       "$0.55 \\times 4.0\\ \\mu\\text{W} = 2.2\\ \\mu$A, so the signal across 12.73 k$\\Omega$ "
                       "is 28 mV — small enough that the next stage's noise and offset are real "
                       "considerations. Doubling the resistor would double the signal to 56 mV and halve "
                       "the bandwidth to 125 kHz, and there is no value that gives you both. The way out "
                       "is not a better resistor but a different circuit: a transimpedance amplifier holds "
                       "the diode at a virtual earth so that $C_j$ never has to be charged by the signal, "
                       "and the trade between gain and bandwidth stops being a straight exchange. That is "
                       "the first thing EE202 builds with a transistor.",
            },
            "build": [{
                "title": "Two LEDs that are meant to look the same",
                "minutes": 26,
                "brief": r'''
An indicator with two LEDs side by side, driven from a 5 V rail, and they have to be the
same brightness. That is the whole specification, and it is enough to rule out the
circuit almost everyone draws first.

## The parts

Two nominally identical red LEDs from the same reel, modelled the way module 2 modelled
a diode — a fixed offset in series with a resistance, the tangent to the real curve near
the working current:

- **LED A**: 1.85 V in series with 12 $\Omega$
- **LED B**: 1.95 V in series with 12 $\Omega$

The 100 mV between them is not a fault. It is the ordinary bin-to-bin spread a data
sheet allows, and any two parts you pull off a reel will differ by something like it.

Both models are already on the canvas, each running down to its own ground, and both are
unconnected at the top. The 5 V rail is there and unconnected too.

## The specification

- each LED must carry between **8 mA and 12 mA**
- the two currents must be within **10%** of each other, or the difference in brightness
  shows
- the rail must supply no more than **22 mA** in total

## The circuit almost everyone draws

One resistor from the rail, feeding both LEDs in parallel. Size it for 20 mA total and
150 $\Omega$ is the answer, and it delivers exactly 19.87 mA — bang on budget. Both LEDs
then sit at the same node, 2.02 V, so LED A carries $(2.02-1.85)/12 = 14.1$ mA and LED B
carries $(2.02-1.95)/12 = 5.8$ mA. Same total current, same power out of the rail,
two-and-a-half times the brightness on one side.

Nothing in that circuit is broken. The two LEDs share a node, so they must share a
voltage, and at a shared voltage the one that needs less takes more. The only fix is to
stop them sharing.

Those two figures are what the *models* do. The junctions themselves are worse — 18.2 mA
against 2.6 mA, a ratio of 6.92 rather than 2.4 — and the next exercise builds the same
specification out of real LEDs and measures it.

## What to build

Give each LED its own ballast resistor from the 5 V rail. Choose the value from the
specification above, and note as you do it that the ballast is not overhead — it is the
component that makes the mismatch stop mattering, because the current is now set mostly
by a resistor you chose rather than by a 100 mV difference you did not.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "a1", "kind": "R", "x": 11, "y": 9, "rot": 1, "value": 12},
                        {"id": "a2", "kind": "V", "x": 11, "y": 12, "rot": 1, "value": 1.85},
                        {"id": "a3", "kind": "GND", "x": 11, "y": 14},
                        {"id": "b1", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 12},
                        {"id": "b2", "kind": "V", "x": 17, "y": 12, "rot": 1, "value": 1.95},
                        {"id": "b3", "kind": "GND", "x": 17, "y": 14},
                        {"id": "pr", "kind": "OUT", "x": 9, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 8], "b": [11, 8]},
                        {"a": [11, 10], "b": [11, 11]},
                        {"a": [11, 13], "b": [11, 14]},
                        {"a": [17, 10], "b": [17, 11]},
                        {"a": [17, 13], "b": [17, 14]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "r1", "kind": "R", "x": 11, "y": 5, "rot": 1, "value": 300},
                        {"id": "r2", "kind": "R", "x": 17, "y": 5, "rot": 1, "value": 300},
                        {"id": "a1", "kind": "R", "x": 11, "y": 9, "rot": 1, "value": 12},
                        {"id": "a2", "kind": "V", "x": 11, "y": 12, "rot": 1, "value": 1.85},
                        {"id": "a3", "kind": "GND", "x": 11, "y": 14},
                        {"id": "b1", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 12},
                        {"id": "b2", "kind": "V", "x": 17, "y": 12, "rot": 1, "value": 1.95},
                        {"id": "b3", "kind": "GND", "x": 17, "y": 14},
                        {"id": "pr", "kind": "OUT", "x": 9, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 5], "b": [9, 4]},
                        {"a": [9, 4], "b": [11, 4]},
                        {"a": [11, 4], "b": [17, 4]},
                        {"a": [11, 6], "b": [11, 8]},
                        {"a": [9, 8], "b": [11, 8]},
                        {"a": [17, 6], "b": [17, 8]},
                        {"a": [11, 10], "b": [11, 11]},
                        {"a": [11, 13], "b": [11, 14]},
                        {"a": [17, 10], "b": [17, 11]},
                        {"a": [17, 13], "b": [17, 14]},
                    ],
                },
                "checks": [
                    {"name": "both LED models are present and unedited", "code": r'''
const a = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 1.85) < 0.02; });
const b = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 1.95) < 0.02; });
c.assert(a.length === 1 && b.length === 1,
  'One 1.85 V offset and one 1.95 V offset, which are the two LEDs. Found ' + a.length +
  ' and ' + b.length + '. Editing them until they match is solving the exercise by ' +
  'assuming the parts are identical, which is the assumption that fails on a reel.');
const twelves = c.values('R').filter(function (v) { return Math.abs(v - 12) <= 0.6; });
c.assert(twelves.length === 2,
  'Each LED model needs its own 12 ohm slope resistance; found ' + twelves.length +
  ' resistors near 12 ohms.');
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 5) < 0.2; });
c.assert(sup.length === 1, 'Exactly one 5 V rail; found ' + sup.length + '.');
'''},
                    {"name": "each LED carries between 8 mA and 12 mA", "code": r'''
const d = c.dc();
const a = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 1.85) < 0.02; })[0];
const b = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 1.95) < 0.02; })[0];
const ia = Math.abs(d.currents[a.id]), ib = Math.abs(d.currents[b.id]);
c.assert(ia >= 0.008 * 0.99 && ia <= 0.012 * 1.01,
  'LED A is carrying ' + c.fmt(ia, 'A') + ', outside the 8 mA to 12 mA window.');
c.assert(ib >= 0.008 * 0.99 && ib <= 0.012 * 1.01,
  'LED B is carrying ' + c.fmt(ib, 'A') + ', outside the 8 mA to 12 mA window.');
'''},
                    {"name": "and the two are within ten per cent of each other", "code": r'''
const d = c.dc();
const a = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 1.85) < 0.02; })[0];
const b = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 1.95) < 0.02; })[0];
const ia = Math.abs(d.currents[a.id]), ib = Math.abs(d.currents[b.id]);
const hi = Math.max(ia, ib), lo = Math.min(ia, ib);
c.assert(lo > 1e-9, 'One of the LEDs is carrying nothing at all.');
c.assert(hi / lo <= 1.10 * 1.001,
  'The two LEDs are carrying ' + c.fmt(lo, 'A') + ' and ' + c.fmt(hi, 'A') + ', a ratio of ' +
  (hi / lo).toFixed(2) + '. A single shared resistor gives 2.44 here, because both LEDs ' +
  'then sit at one node voltage and the one with the lower offset takes the difference. ' +
  'Each LED needs its own path back to the rail.');
'''},
                    {"name": "the rail supplies no more than 22 mA", "code": r'''
const sup = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 5) < 0.2; })[0];
const i = Math.abs(c.dc().currents[sup.id]);
c.assert(i > 1e-4,
  'The 5 V rail is delivering ' + c.fmt(i, 'A') + '. Nothing is connected to it yet, so ' +
  'neither LED is lit and there is nothing to measure.');
c.assert(i <= 0.022 * 1.01,
  'The rail is being asked for ' + c.fmt(i, 'A') + ', over the 22 mA budget. Two LEDs at ' +
  '10 mA each is 20 mA and the budget allows a little over that, so if you are well above ' +
  'it the ballast resistors are too small.');
'''},
                ],
                "hints": [
                    "Size each ballast for about 10 mA through its own LED. For LED A: $(5 - 1.85)/(R + 12) = 0.010$ gives $R = 303\\ \\Omega$, so 300 $\\Omega$ is the standard value to reach for.",
                    "The same 300 $\\Omega$ works for both: LED A then takes 10.10 mA and LED B takes 9.78 mA, a ratio of 1.03 and a total of 19.87 mA. Trimming the two ballasts to different values to equalise them exactly is possible and pointless — the next pair off the reel will be mismatched differently.",
                    "330 $\\Omega$ also passes, at 9.21 mA and 8.92 mA. 390 $\\Omega$ does not: it drops LED B to 7.59 mA, under the 8 mA floor. 220 $\\Omega$ does not either: it asks the rail for 26.7 mA.",
                    "Lay it out as two independent columns: rail, ballast, LED model, ground, twice over. The only thing the two branches may share is the rail and the ground.",
                    "Notice what the shared-resistor version and the correct one have in common: both draw 19.87 mA from the rail and both dissipate the same total power. The mismatch costs nothing in current and everything in what the current is doing, which is why measuring the supply rail would never have found it.",
                ],
            }, {
                "title": "The same two LEDs, with the junctions left in",
                "minutes": 24,
                "brief": r'''
Same specification, same reel, same 5 V rail — and this time the two LEDs are LEDs. The
editor solves them directly, so nothing on the canvas stands in for anything.

## The parts

Two red LEDs, $n = 2$, differing only in saturation current:

- **LED A**: $I_S = 2.889\times10^{-18}$ A, which puts it at **1.850 V** at 10 mA
- **LED B**: $I_S = 4.176\times10^{-19}$ A, which puts it at **1.950 V** at 10 mA

These are the same two parts the last exercise modelled, with the spread written as the
parameter it actually comes from rather than as the drop it happens to produce at one
current.

## The specification, unchanged

- each LED carries between **8 mA and 12 mA**
- the two currents within **10%** of each other
- the rail supplies no more than **22 mA**

## What the shared resistor really does

Last time a single 150 $\Omega$ ballast split the current 14.1 mA and 5.8 mA. Build the
same circuit out of junctions and it splits **18.17 mA and 2.63 mA** — a ratio of
**6.92**, not 2.4. The linearised model understated the effect it was introduced to
demonstrate by a factor of nearly three.

The reason is worth more than the number. Two LEDs on one node are held at one voltage
$V$, and each carries $I = I_S\left(e^{V/nV_T} - 1\right)$. Divide one by the other and
the exponential cancels:

$$\frac{I_A}{I_B} = \frac{I_{SA}}{I_{SB}}
= \frac{2.889\times10^{-18}}{4.176\times10^{-19}} = 6.92$$

$V$ has gone. The split does not depend on the ballast, on the supply, or on how hard
the pair is driven — 6.92 at 50 $\Omega$, 6.92 at 10 k$\Omega$, and 6.92 at every value
between. The piecewise-linear model cannot say this: its ratio is
$(V - 1.85)/(V - 1.95)$, which moves with $V$, and that is why it gave a smaller and
ballast-dependent answer.

## What to build

Give each LED its own ballast from the rail. **300 $\Omega$** each puts LED A at
10.49 mA and LED B at 10.16 mA — a ratio of 1.032, and 20.66 mA out of the rail.

Do not adjust the two saturation currents until they agree. That is solving the exercise
by deleting its premise, and the first check refuses it.
''',
                "start": {"parts": [
                    {"id": "q0", "kind": "V",   "x": 3,  "y": 6,  "rot": 1, "value": 5},
                    {"id": "q1", "kind": "GND", "x": 3,  "y": 9},
                    {"id": "q2", "kind": "LED", "x": 13, "y": 10, "rot": 1, "value": 2.8886e-18, "n": 2},
                    {"id": "q3", "kind": "GND", "x": 13, "y": 12},
                    {"id": "q4", "kind": "LED", "x": 17, "y": 10, "rot": 1, "value": 4.1756e-19, "n": 2},
                    {"id": "q5", "kind": "GND", "x": 17, "y": 12},
                    {"id": "q6", "kind": "OUT", "x": 13, "y": 9},
                ], "wires": [
                    {"a": [3, 7],   "b": [3, 9]},
                    {"a": [13, 11], "b": [13, 12]},
                    {"a": [17, 11], "b": [17, 12]},
                ]},
                "solution": {"parts": [
                    {"id": "q0", "kind": "V",   "x": 3,  "y": 6,  "rot": 1, "value": 5},
                    {"id": "q1", "kind": "GND", "x": 3,  "y": 9},
                    {"id": "q7", "kind": "R",   "x": 13, "y": 6,  "rot": 1, "value": 300},
                    {"id": "q2", "kind": "LED", "x": 13, "y": 10, "rot": 1, "value": 2.8886e-18, "n": 2},
                    {"id": "q3", "kind": "GND", "x": 13, "y": 12},
                    {"id": "q8", "kind": "R",   "x": 17, "y": 6,  "rot": 1, "value": 300},
                    {"id": "q4", "kind": "LED", "x": 17, "y": 10, "rot": 1, "value": 4.1756e-19, "n": 2},
                    {"id": "q5", "kind": "GND", "x": 17, "y": 12},
                    {"id": "q6", "kind": "OUT", "x": 13, "y": 9},
                ], "wires": [
                    {"a": [3, 7],   "b": [3, 9]},
                    {"a": [3, 5],   "b": [13, 5]},
                    {"a": [13, 5],  "b": [17, 5]},
                    {"a": [13, 7],  "b": [13, 9]},
                    {"a": [17, 7],  "b": [17, 9]},
                    {"a": [13, 11], "b": [13, 12]},
                    {"a": [17, 11], "b": [17, 12]},
                ]},
                "checks": [
                    {"name": "two real LEDs from the same reel, unedited", "code": r'''
c.assert(c.count('LED') === 2,
  'Two LEDs, drawn as LEDs rather than modelled; found ' + c.count('LED') + '.');
const is = c.values('LED').slice().sort(function (a, b) { return a - b; });
c.assert(Math.abs(is[0] / 4.1756e-19 - 1) < 0.02 && Math.abs(is[1] / 2.8886e-18 - 1) < 0.02,
  'The two saturation currents are the reel spread, and they are what this exercise is ' +
  'about. Editing them until they match solves the problem by assuming it away.');
c.assert(c.count('V') === 1,
  'One rail and one rail only; found ' + c.count('V') + ' voltage sources.');
'''},
                    {"name": "each LED carries between 8 mA and 12 mA", "code": r'''
const ls = c.net.placed.filter(function (p) { return p.kind === 'LED'; });
c.assert(ls.length === 2, 'Both LEDs have to be on the canvas.');
ls.forEach(function (p) {
  const i = Math.abs(c.device(p.id).i[0]);
  c.assert(i >= 0.008 && i <= 0.012,
    'One LED is carrying ' + c.fmt(i, 'A') + ', outside the 8 to 12 mA the ' +
    'specification allows.');
});
'''},
                    {"name": "the two currents are within 10% of each other", "code": r'''
const ls = c.net.placed.filter(function (p) { return p.kind === 'LED'; });
c.assert(ls.length === 2, 'Both LEDs have to be on the canvas.');
const i = ls.map(function (p) { return Math.abs(c.device(p.id).i[0]); })
            .sort(function (a, b) { return a - b; });
c.assert(i[0] > 1e-6,
  'One LED is carrying essentially nothing, so the two cannot be compared. Check that ' +
  'both are the right way up and that both have a path to the rail.');
c.assert(i[1] / i[0] <= 1.10,
  'The brighter LED carries ' + (i[1] / i[0]).toFixed(2) + ' times the dimmer one. ' +
  'A shared ballast gives 6.92 here whatever its value, because at one shared voltage ' +
  'the two currents are in the ratio of the saturation currents.');
'''},
                    {"name": "the rail delivers no more than 22 mA", "code": r'''
const d = c.dc();
const v = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
c.assert(v, 'There is no voltage source in this circuit.');
const tot = Math.abs(d.currents[v.id]);
c.assert(tot <= 0.022,
  'The rail is supplying ' + c.fmt(tot, 'A') + ', over the 22 mA budget.');
'''},
                ],
                "hints": [
                    "Size each ballast from the drop you want across it: $(5 - 1.85)/0.010 = 315\\,\\Omega$ for LED A and $(5 - 1.95)/0.010 = 305\\,\\Omega$ for LED B. One 300 $\\Omega$ part does for both, and lands at 10.49 mA and 10.16 mA.",
                    "330 $\\Omega$ also passes, at 9.55 mA and 9.26 mA. 390 $\\Omega$ does not — LED B falls to 7.85 mA, under the 8 mA floor — and 220 $\\Omega$ fails twice, at 14.2 mA through LED A and 28.0 mA out of the rail.",
                    "Two independent columns: rail, ballast, LED, ground, twice over. The only things the branches may share are the rail and the ground.",
                    "Notice how little the current *ratio* moves as the ballast changes — 1.032 at 220 $\\Omega$ and 1.032 at 390 $\\Omega$. Separate ballasts do not equalise the junctions; they hand the decision to the resistor instead of the junction.",
                    "If the second check passes and the third fails, you have built the shared-ballast version. Both LEDs are lit and the rail is inside budget, which is exactly why this fault ships.",
                ],
            }],
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A whole supply: designed, then proved",
        "runtime": "python",
        "minutes": 150,
        "brief": r'''
Everything in this course has been one stage at a time. A real supply is four stages
in series, and the interesting failures happen between them: a reservoir capacitor
sized for the average load that cannot cope with the trough, a regulator that works at
the nominal mains voltage and drops out at the bottom of its tolerance, a Zener that
survives full load and cooks at no load.

You are going to design a supply to a specification, and then prove it by stepping the
whole chain forward in time and measuring what comes out — the same two-part discipline
every one of these modules has used, applied to all of them at once.

## The chain

```text
mains sinusoid  ->  bridge (2 diode drops)  ->  reservoir C  ->  R_S  ->  Zener || load
```

The bridge and reservoir are module 3. The series resistor and Zener are module 4. The
only new idea is that the reservoir's ripple is now the *input* to the regulator, so
the two stages have to be judged together.

## The specification

- transformer secondary: 17 V peak, 50 Hz
- bridge: two diodes in series with the load at all times, 0.7 V each
- output: a rail near **5.1 V** into a 470 Ω load, anywhere from 5.0 V to 5.3 V
- Zener: modelled as 4.94 V in series with 8 Ω
- output ripple: no more than **20 mV** peak to peak

The output window is wider than a nominal figure because the 8 Ω is real. On the 12 V
rail of module 4 the same $R_S$ gave 5.104 V; here the reservoir sits nearer 15.4 V, so
more current goes through the Zener and the rail climbs to about 5.22 V. Predict where
yours lands before you run anything — the shift is the 8 Ω doing exactly what module 4
said it would.

## What you are building, in `main.py`

1. `zener_output(v_c, r_s, v_z0, r_z, r_load)` — the regulator's output for a given
   reservoir voltage, exactly as in module 4.
2. `ripple_rejection(r_s, r_z, r_load)` — the fraction of the reservoir's ripple that
   reaches the output, $(r_z \parallel R_L)/(R_S + r_z \parallel R_L)$. This is the
   design tool: it tells you how much ripple the reservoir is allowed to have.
3. `design_reservoir(i_draw, f_ripple, v_ripple_allowed)` — the capacitance in farads
   that holds the *reservoir* ripple to the stated figure, from module 3's
   $C = I/(f_{ripple}V_{ripple})$.
4. `simulate_supply(v_peak, f_mains, c, r_s, v_z0, r_z, r_load, v_bridge, cycles, per_cycle)`
   — steps the whole chain and returns the tuple `(reservoir_samples, output_samples)`,
   two lists of equal length.
5. `report(reservoir, output, per_cycle, r_load)` — returns a dict with the keys
   `"v_out_mean"`, `"v_out_ripple"`, `"v_c_mean"`, `"v_c_ripple"`, `"rejection"` and
   `"p_load"`, all measured over the **last `per_cycle` samples** and all floats.
   `"rejection"` is the measured output ripple divided by the measured reservoir
   ripple, and `"p_load"` is the mean output squared over `r_load`.

## The simulation model

Time step `dt = 1 / (f_mains * per_cycle)`, starting from `v_c = 0.0`. At each step,
in this order:

```text
v_rect = v_peak * abs(sin(2*pi*f_mains*t)) - v_bridge
v_out  = zener_output(v_c, r_s, v_z0, r_z, r_load)
i_draw = (v_c - v_out) / r_s
if v_rect > v_c:  v_c = v_rect          # diodes conduct
else:             v_c -= i_draw * dt / c
record v_c and v_out
```

Note that the reservoir is not discharged by the load directly — it is discharged by
whatever the series resistor draws, and that is a smaller current than the load takes,
because the Zener is also feeding the load. Getting that wrong is the most likely
source of a disagreement between your simulation and the design formulas.

## Suggested order

Write `zener_output` and `ripple_rejection` first and check them against the module 4
numbers you already have. Then use `ripple_rejection` to work out how much reservoir
ripple 20 mV of output ripple allows, hand that to `design_reservoir`, and only then
write the simulation to see whether the answer was right. The simulation is the proof,
not the design method — if you find yourself tuning the capacitor by running it, the
design part has not been done.
''',
        "deliverables": [
            "`zener_output` and `ripple_rejection`, the two closed-form results the design rests on, agreeing with the module 4 figures to full floating-point precision.",
            "`design_reservoir`, sizing the reservoir capacitor from a permitted reservoir ripple, and a comment in `main.py` giving the capacitance your own design calls for and the reasoning that produced it.",
            "`simulate_supply`, stepping mains, bridge, reservoir, series resistor and Zener forward together and returning both node waveforms.",
            "`report`, measuring mean, ripple, rejection and load power from the final cycle of a simulation, with every figure a float.",
            "Evidence, in the same comment, that the designed capacitor meets the 20 mV output ripple specification when the simulation is run — the measured number, not an assertion that it should.",
        ],
        "constraints": [
            "The standard library only. NumPy is available but nothing here needs it, and the simulation is inherently sequential.",
            "`simulate_supply` must use the update order given in the brief, including discharging the reservoir with the series resistor's current rather than the load's.",
            "`report` must measure over the last `per_cycle` samples only. Including the start-up ramp from 0 V makes every figure meaningless.",
            "Do not special-case the test values. The functions must work for any transformer voltage, any capacitance and any load.",
            "No tuning loops. `design_reservoir` returns a capacitance from a formula; the simulation then confirms or refutes it.",
        ],
        "rubric": [
            {"criterion": "Closed-form design", "weight": 25,
             "evidence": "zener_output and ripple_rejection reproduce the module 4 results exactly, including the limiting cases of a very large and a very small series resistor, and ripple_rejection equals the parallel-combination divider ratio to machine precision."},
            {"criterion": "Reservoir sizing", "weight": 20,
             "evidence": "design_reservoir inverts the I/(fC) relation correctly, and the capacitance it returns for the stated specification is the one the candidate's comment justifies and the simulation then confirms."},
            {"criterion": "Chain simulation", "weight": 30,
             "evidence": "simulate_supply produces two waveforms of the right length whose reservoir peak equals the transformer peak less the bridge drops, whose settled means match the closed-form predictions, and which respond correctly to changes in capacitance, load and transformer voltage."},
            {"criterion": "Measurement and evidence", "weight": 25,
             "evidence": "report returns all six keys as floats measured over the final cycle only, the measured rejection agrees with the predicted rejection to within a per cent, and the candidate's comment quotes real measured numbers rather than expected ones."},
        ],
        "hints": [
            "`ripple_rejection` is `par / (r_s + par)` where `par = r_z * r_load / (r_z + r_load)`. With 8 Ω, 470 Ω and 220 Ω it comes to 0.0345.",
            "To hit 20 mV of output ripple at a rejection of 0.0345 the reservoir may ripple by 20 mV / 0.0345 = 0.58 V. The current the series resistor draws is about (15.4 − 5.2)/220 = 46 mA, so `design_reservoir(0.046, 100.0, 0.58)` gives about 790 µF, and the nearest standard value above it is 1000 µF.",
            "In `simulate_supply`, compute `v_out` from `v_c` **before** updating `v_c`, and append both afterwards. Reordering those two lines shifts everything by one sample and changes the measured ripple.",
            "`report` should slice both lists with `[-per_cycle:]` once, at the top, and work from the slices. Six separate slices of the same data is six chances to type the wrong sign.",
            "If the measured rejection does not match `ripple_rejection`, look at the discharge line. Using `v_out / r_load` there instead of `(v_c - v_out) / r_s` discharges the reservoir too slowly and quietly changes the ripple.",
            "The whole chain is linear once the diodes have decided what they are doing, so the measured rejection should agree with the predicted one to several decimal places, not just approximately. If it agrees only to within ten per cent, something is genuinely wrong rather than merely imprecise.",
        ],
        "files": [
            {"name": "main.py", "content": r'''
"""A complete unregulated-plus-regulated supply, designed and then simulated.

Design record:
    TODO: state the reservoir capacitance your design calls for, how you arrived at
    it from the 20 mV output ripple specification, and the output ripple the
    simulation actually measured.
"""

import math


def zener_output(v_c, r_s, v_z0, r_z, r_load):
    """Regulated output for a reservoir voltage of v_c."""
    # TODO: the three-branch conductance divider from module 4.
    return 0.0


def ripple_rejection(r_s, r_z, r_load):
    """Fraction of the reservoir's ripple that reaches the output."""
    # TODO: (r_z parallel r_load) / (r_s + r_z parallel r_load).
    return 0.0


def design_reservoir(i_draw, f_ripple, v_ripple_allowed):
    """Capacitance in farads that holds the reservoir ripple to the stated figure."""
    # TODO: invert I / (f * C).
    return 0.0


def simulate_supply(v_peak, f_mains, c, r_s, v_z0, r_z, r_load, v_bridge,
                    cycles, per_cycle):
    """Step the whole chain; return (reservoir_samples, output_samples)."""
    dt = 1.0 / (f_mains * per_cycle)
    v_c = 0.0
    reservoir, output = [], []
    # TODO: the update order from the brief, appending both lists every step.
    return (reservoir, output)


def report(reservoir, output, per_cycle, r_load):
    """Measure the last per_cycle samples. Returns a dict of six floats."""
    # TODO: slice both tails, then mean, peak-to-peak, rejection and load power.
    return {"v_out_mean": 0.0, "v_out_ripple": 0.0, "v_c_mean": 0.0,
            "v_c_ripple": 0.0, "rejection": 0.0, "p_load": 0.0}


if __name__ == "__main__":
    C = 1000e-6
    res, out = simulate_supply(17.0, 50.0, C, 220.0, 4.94, 8.0, 470.0, 1.4, 12, 2000)
    if res:
        r = report(res, out, 2000, 470.0)
        for key in ("v_c_mean", "v_c_ripple", "v_out_mean", "v_out_ripple",
                    "rejection", "p_load"):
            print(key, "=", r[key])
        print("predicted rejection =", ripple_rejection(220.0, 8.0, 470.0))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A complete unregulated-plus-regulated supply, designed and then simulated.

Design record:
    The regulator's ripple rejection with R_S = 220, r_z = 8 and R_L = 470 is
    0.034521, so 20 mV of output ripple permits 20e-3 / 0.034521 = 0.579 V of
    reservoir ripple. The series resistor draws about (15.4 - 5.2) / 220 = 46 mA
    from the reservoir, so design_reservoir(0.046, 100.0, 0.579) asks for 794 uF
    and the nearest standard value above that is 1000 uF.

    Simulated at 1000 uF: the reservoir settles at a mean of 15.3899 V with
    0.42814 V of ripple, and the output at a mean of 5.22091 V with 0.014780 V —
    14.8 mV, inside the 20 mV specification with room to spare. The measured
    rejection is 0.0345207, which matches the predicted 0.0345207 to seven
    figures, as it must for a linear stage.

    The rail sits at 5.221 V rather than the 5.104 V module 4 measured, and the
    reason is the 8 ohms: the reservoir is at 15.39 V instead of 12 V, so R_S
    pushes 46.2 mA rather than 31.3 mA into the node. Of that extra 14.9 mA the
    load takes 0.25 mA and the Zener absorbs the other 14.6 mA, and 8 ohms times
    14.6 mA is 0.117 V — exactly the 5.221 - 5.104 observed. Inside the 5.0 V to
    5.3 V window, and it is 8 ohms of dynamic resistance, not drift.
"""

import math


def zener_output(v_c, r_s, v_z0, r_z, r_load):
    """Regulated output for a reservoir voltage of v_c."""
    return ((v_c / r_s + v_z0 / r_z)
            / (1.0 / r_s + 1.0 / r_z + 1.0 / r_load))


def ripple_rejection(r_s, r_z, r_load):
    """Fraction of the reservoir's ripple that reaches the output."""
    par = r_z * r_load / (r_z + r_load)
    return par / (r_s + par)


def design_reservoir(i_draw, f_ripple, v_ripple_allowed):
    """Capacitance in farads that holds the reservoir ripple to the stated figure."""
    return i_draw / (f_ripple * v_ripple_allowed)


def simulate_supply(v_peak, f_mains, c, r_s, v_z0, r_z, r_load, v_bridge,
                    cycles, per_cycle):
    """Step the whole chain; return (reservoir_samples, output_samples)."""
    dt = 1.0 / (f_mains * per_cycle)
    v_c = 0.0
    reservoir, output = [], []
    for k in range(cycles * per_cycle):
        t = k * dt
        v_rect = v_peak * abs(math.sin(2.0 * math.pi * f_mains * t)) - v_bridge
        v_out = zener_output(v_c, r_s, v_z0, r_z, r_load)
        i_draw = (v_c - v_out) / r_s
        if v_rect > v_c:
            v_c = v_rect
        else:
            v_c -= i_draw * dt / c
        reservoir.append(v_c)
        output.append(v_out)
    return (reservoir, output)


def report(reservoir, output, per_cycle, r_load):
    """Measure the last per_cycle samples. Returns a dict of six floats."""
    rc = reservoir[-per_cycle:]
    ro = output[-per_cycle:]
    vc_mean = sum(rc) / len(rc)
    vo_mean = sum(ro) / len(ro)
    vc_ripple = max(rc) - min(rc)
    vo_ripple = max(ro) - min(ro)
    return {
        "v_out_mean": float(vo_mean),
        "v_out_ripple": float(vo_ripple),
        "v_c_mean": float(vc_mean),
        "v_c_ripple": float(vc_ripple),
        "rejection": float(vo_ripple / vc_ripple),
        "p_load": float(vo_mean * vo_mean / r_load),
    }


if __name__ == "__main__":
    C = 1000e-6
    res, out = simulate_supply(17.0, 50.0, C, 220.0, 4.94, 8.0, 470.0, 1.4, 12, 2000)
    if res:
        r = report(res, out, 2000, 470.0)
        for key in ("v_c_mean", "v_c_ripple", "v_out_mean", "v_out_ripple",
                    "rejection", "p_load"):
            print(key, "=", r[key])
        print("predicted rejection =", ripple_rejection(220.0, 8.0, 470.0))
'''},
        ],
        "tests": [
            {"name": "the regulator's closed form matches module 4", "code": r'''
v = zener_output(12.0, 220.0, 4.94, 8.0, 470.0)
assert abs(v - 5.103892765332354) < 1e-9, f"expected 5.1038928 V, got {v}"
assert abs(zener_output(12.0, 1e12, 4.94, 8.0, 1e12) - 4.94) < 1e-3, \
    "starved of current and unloaded, the output must sit at v_z0"
assert abs(zener_output(12.0, 1e-6, 4.94, 8.0, 470.0) - 12.0) < 1e-3, \
    "with almost no series resistance the output must follow the input"
'''},
            {"name": "ripple rejection is the parallel divider ratio", "code": r'''
rr = ripple_rejection(220.0, 8.0, 470.0)
par = 8.0 * 470.0 / 478.0
assert abs(rr - par / (220.0 + par)) < 1e-15, f"expected {par / (220.0 + par)}, got {rr}"
assert abs(rr - 0.03452074917370547) < 1e-12, f"expected 0.034520749, got {rr}"
assert ripple_rejection(1000.0, 8.0, 470.0) < rr, \
    "a larger series resistor must reject more ripple"
'''},
            {"name": "the reservoir design formula inverts I/(fC)", "code": r'''
c = design_reservoir(0.046, 100.0, 0.579)
assert abs(c - 0.046 / 57.9) < 1e-15, f"expected {0.046 / 57.9} F, got {c}"
assert abs(c - 7.944732297063903e-4) < 1e-12, f"expected 794.47 uF, got {c}"
assert abs(design_reservoir(0.05, 100.0, 0.5) - 1000e-6) < 1e-15, \
    "50 mA and 0.5 V at 100 Hz is exactly 1000 uF"
'''},
            {"name": "the chain simulates, and the reservoir peaks where it should", "code": r'''
res, out = simulate_supply(17.0, 50.0, 1000e-6, 220.0, 4.94, 8.0, 470.0, 1.4, 12, 2000)
assert len(res) == 24000 and len(out) == 24000, \
    f"expected 24000 samples in each list, got {len(res)} and {len(out)}"
tail = res[-2000:]
assert abs(max(tail) - 15.6) < 1e-6, \
    f"17 V peak less two 0.7 V drops is 15.6 V, got {max(tail)}"
assert abs(min(tail) - 15.171860231825638) < 1e-6, \
    f"expected a reservoir trough of 15.17186 V, got {min(tail)}"
'''},
            {"name": "the report measures the final cycle and meets the 20 mV specification", "code": r'''
res, out = simulate_supply(17.0, 50.0, 1000e-6, 220.0, 4.94, 8.0, 470.0, 1.4, 12, 2000)
r = report(res, out, 2000, 470.0)
for key in ("v_out_mean", "v_out_ripple", "v_c_mean", "v_c_ripple", "rejection", "p_load"):
    assert key in r, f"the report is missing the key {key!r}"
    assert isinstance(r[key], float), f"{key} should be a float, got {type(r[key])}"
assert abs(r["v_c_mean"] - 15.389864402136372) < 1e-6, f"expected 15.389864 V, got {r['v_c_mean']}"
assert abs(r["v_c_ripple"] - 0.42813977031073414) < 1e-6, f"expected 0.4281398 V, got {r['v_c_ripple']}"
assert abs(r["v_out_mean"] - 5.2209134240913775) < 1e-6, f"expected 5.2209134 V, got {r['v_out_mean']}"
assert abs(r["v_out_ripple"] - 0.014779705622185446) < 1e-9, \
    f"expected 0.01477971 V, got {r['v_out_ripple']}"
assert r["v_out_ripple"] <= 0.020, \
    f"the specification is 20 mV peak to peak; this design gives {r['v_out_ripple']}"
assert abs(r["p_load"] - 5.2209134240913775 ** 2 / 470.0) < 1e-12, \
    f"p_load should be the mean output squared over the load, got {r['p_load']}"
'''},
            {"name": "the measured rejection matches the predicted one", "code": r'''
res, out = simulate_supply(17.0, 50.0, 1000e-6, 220.0, 4.94, 8.0, 470.0, 1.4, 12, 2000)
r = report(res, out, 2000, 470.0)
predicted = ripple_rejection(220.0, 8.0, 470.0)
assert abs(predicted - 0.03452074917370547) < 1e-12, \
    f"the predicted rejection should be 0.034520749, got {predicted}"
assert abs(r["rejection"] - predicted) < 1e-6, \
    f"the stage is linear, so the measured {r['rejection']} must match the predicted {predicted}"
'''},
            {"name": "a bigger capacitor halves the ripple at both nodes", "code": r'''
res, out = simulate_supply(17.0, 50.0, 2200e-6, 220.0, 4.94, 8.0, 470.0, 1.4, 12, 2000)
r = report(res, out, 2000, 470.0)
assert abs(r["v_c_ripple"] - 0.2016645099362524) < 1e-6, \
    f"expected 0.2016645 V at the reservoir, got {r['v_c_ripple']}"
assert abs(r["v_out_ripple"] - 0.006961609964748483) < 1e-9, \
    f"expected 0.00696161 V at the output, got {r['v_out_ripple']}"
assert abs(r["v_out_mean"] - 5.224729843189422) < 1e-6, f"expected 5.2247298 V, got {r['v_out_mean']}"
assert abs(r["rejection"] - ripple_rejection(220.0, 8.0, 470.0)) < 1e-6, \
    "the rejection does not depend on the capacitor at all"
'''},
            {"name": "it works on a different transformer and a different resistor", "code": r'''
res, out = simulate_supply(24.0, 50.0, 1000e-6, 330.0, 4.94, 8.0, 470.0, 1.4, 12, 2000)
r = report(res, out, 2000, 470.0)
assert abs(max(res[-2000:]) - 22.6) < 1e-6, \
    f"24 V peak less 1.4 V is 22.6 V, got {max(res[-2000:])}"
assert abs(r["v_c_mean"] - 22.362272428188597) < 1e-6, f"expected 22.362272 V, got {r['v_c_mean']}"
assert abs(r["v_out_mean"] - 5.264867766749159) < 1e-6, f"expected 5.2648678 V, got {r['v_out_mean']}"
assert abs(r["v_out_ripple"] - 0.011261835317746716) < 1e-9, \
    f"expected 0.01126184 V, got {r['v_out_ripple']}"
assert abs(r["rejection"] - ripple_rejection(330.0, 8.0, 470.0)) < 1e-6, \
    "the measured rejection must track the larger series resistor"
'''},
        ],
    },
}
