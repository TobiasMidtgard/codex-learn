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
            "read": [
                {
                    "title": "Four millivolts from a resistor connected to nothing",
                    "minutes": 15,
                    "body": r'''
A 1 k$\Omega$ metal-film resistor is lying on the bench with its two leads pushed into
the input terminals of a low-noise preamplifier — voltage gain 1000, band 10 Hz to
1 MHz — and the preamplifier drives an oscilloscope. Nothing else is attached to the
resistor. There is no supply, no current through it, no signal source anywhere on the
bench. The scope shows $4.0$ mV r.m.s. of grass, and waiting does not make it go away.

Four things move that number and nothing else does. Drop the resistor into liquid
nitrogen and the grass falls to $2.1$ mV. Swap it for a 4 k$\Omega$ part at room
temperature and it rises to $8.0$ mV. Narrow the preamplifier to 250 kHz and it halves
to $2.0$ mV. Reverse the leads, shine a lamp on it, come back an hour later: no change
at all.

## What those four readings fix on their own

Read them as ratios. Cooling from $290$ K to $77$ K is a factor of $3.766$ in
temperature and $1.941$ in volts, and $\sqrt{3.766} = 1.941$. Four times the resistance
is twice the volts. A quarter of the bandwidth is half the volts. Every one of the three
is a square-root dependence in voltage, which is a linear one in mean square:

$$\overline{v_n^2} = \alpha\,T R B$$

with a single constant $\alpha$ carrying all of the physics. Nothing in the four
readings can tell you what $\alpha$ is, because every measurement was of the same
resistor at the same time. Something outside the bench has to fix it.

Take the resistor and put a capacitor $C$ across it, with the pair sealed in an oven at
temperature $T$ and nothing else connected. Equipartition applies to the capacitor,
because its stored energy $\tfrac{1}{2}Cv_C^2$ is one quadratic degree of freedom, and
in equilibrium a quadratic degree of freedom holds $\tfrac{1}{2}k_BT$:

$$\tfrac{1}{2}C\,\overline{v_C^2} = \tfrac{1}{2}k_BT
\qquad\Longrightarrow\qquad \overline{v_C^2} = \frac{k_BT}{C}$$

That statement has no resistance in it. Now compute the same quantity the other way. The
only source in the oven is the resistor, and the $RC$ pair is a one-pole low-pass whose
equivalent noise bandwidth is $1/(4RC)$ — the result module 4 derives, in which the
$\pi$ of the Lorentzian integral cancels the $\pi$ in $f_0 = 1/(2\pi RC)$. A flat
density $\alpha TR$ passed through that bandwidth arrives as

$$\overline{v_C^2} = \alpha T R \cdot \frac{1}{4RC} = \frac{\alpha T}{4C}$$

The resistance has cancelled, which it had to, since the equipartition answer contains
none. Setting the two equal gives $\alpha = 4k_B$, and the $4$ is not decoration: it is
the $4$ in $1/(4RC)$, arriving from the shape of a first-order roll-off. So

$$\overline{v_n^2} = 4k_BTRB, \qquad S_v = 4k_BTR \ \text{V}^2/\text{Hz}$$

and the bench readings come back exactly.

```python
import math

K_B = 1.380649e-23


def density(R, T=290.0):
    """Open-circuit thermal noise density of R, in V per root hertz."""
    return math.sqrt(4.0 * K_B * T * R)


def scope_rms(R, T, B, gain=1000.0):
    """What the flat density reads on the scope after a gain of 1000."""
    return density(R, T) * math.sqrt(B) * gain


bench = [("1k, 290 K, 1 MHz", 1e3, 290.0, 1e6),
         ("1k,  77 K, 1 MHz", 1e3, 77.0, 1e6),
         ("4k, 290 K, 1 MHz", 4e3, 290.0, 1e6),
         ("1k, 290 K, 250 kHz", 1e3, 290.0, 2.5e5)]
for name, R, T, B in bench:
    print(f"{name:19s} {density(R, T) * 1e9:6.3f} nV/rtHz "
          f"-> {scope_rms(R, T, B) * 1e3:6.3f} mV rms")
```

## Volts per root hertz, and the six decibels that go missing

$S_v$ is a power density in V$^2$/Hz. What a datasheet prints is its square root, in
V/$\sqrt{\text{Hz}}$, and the conversion between the two is where most noise arithmetic
comes apart. A kilohm at room temperature is $4.002$ nV/$\sqrt{\text{Hz}}$, which is
worth carrying around, because every other resistance is that number scaled by
$\sqrt{R/1\,\text{k}\Omega}$: a hundredfold rise in resistance is tenfold in
nV/$\sqrt{\text{Hz}}$, not a hundredfold. This module's sandbox, *The flat floor a
resistor sets*, has the same warning in its second note — moving the floor from $4$ to
$8$ nV/$\sqrt{\text{Hz}}$ is going from 1 k$\Omega$ to 4 k$\Omega$, and moving it from
$8$ to $16$ is $6$ dB of voltage, not $3$.

Uncorrelated sources add in *power*, never in volts, and the practical shape of that
rule is worth having ready. A contributor a third the size of the dominant one raises
the total by $\sqrt{1 + 1/9} = 5.4\%$, which is rarely worth an engineering afternoon.
Two equal contributors give $\sqrt{2}$, not $2$. And "the biggest one wins" is a
reasonable first estimate and a poor habit, because it is wrong by $41\%$ exactly when
the decision is close enough to matter.

## A resistor that carries no signal current, and the trap it sets

Here is the circuit this course keeps coming back to: the input of a low-noise
amplifier. An antenna or a filter presents $R_s = 50\ \Omega$; the gate of the input
device has to be held at a d.c. bias, so a resistor $R_B$ runs from the gate to a bias
rail that is an a.c. ground. The gate itself draws no current, so $R_B$ carries no
signal current whatever. It is tempting to conclude that it therefore cannot matter,
and equally tempting — once someone points out that a 10 k$\Omega$ resistor makes
$12.655$ nV/$\sqrt{\text{Hz}}$ against the source's $0.895$ — to conclude that it
ruins everything. Both are wrong, and the second is wrong by twenty-three decibels.

Work it out with the equivalent-resistance rule from the derivation unit, *From the
open-circuit voltage to available noise power*. The resistance seen at the gate is
$R_s \parallel R_B$, so the noise density there is $\sqrt{4k_BT(R_s\parallel R_B)}$. But
the signal at the gate is not the source's signal either: the same two resistors divide
it by $R_B/(R_s + R_B)$. Referring the noise back to the source means dividing by that
same transfer, and the algebra is short:

$$\overline{v_{in}^2} = 4k_BT\,\frac{R_sR_B}{R_s+R_B}\cdot
\left(\frac{R_s+R_B}{R_B}\right)^2 = 4k_BTR_s\left(1 + \frac{R_s}{R_B}\right)$$

The bias resistor's entire effect is the factor $1 + R_s/R_B$. That is a noise factor,
in the sense module 3 makes precise, and with $R_s = 50\ \Omega$ and $R_B = 10$
k$\Omega$ it is $1.005$ — two hundredths of a decibel.

```python
import math

K_B, T = 1.380649e-23, 290.0
FOUR_KT = 4.0 * K_B * T
R_S = 50.0


def gate_density(R_B):
    """Density at the gate node: the parallel resistance, not either resistor."""
    return math.sqrt(FOUR_KT * R_S * R_B / (R_S + R_B))


def input_referred(R_B):
    """The same noise, divided by the signal transfer from source to gate."""
    return gate_density(R_B) * (R_S + R_B) / R_B


source = math.sqrt(FOUR_KT * R_S)
print(f"50 ohm source alone : {source * 1e9:7.4f} nV/rtHz")
print(f"10 k on its own     : {math.sqrt(FOUR_KT * 1e4) * 1e9:7.4f} nV/rtHz")
naive = (math.sqrt(FOUR_KT * 1e4) / source) ** 2
print(f"naive: 10 k adds {naive:5.1f}x the source power "
      f"-> {10 * math.log10(1.0 + naive):5.2f} dB")
for R_B in (200.0, 1e3, 1e4, 1e5):
    F = (input_referred(R_B) / source) ** 2
    print(f"R_B = {R_B:8.0f} ohm  gate {gate_density(R_B) * 1e9:6.4f}  "
          f"referred {input_referred(R_B) * 1e9:6.4f} nV/rtHz  "
          f"F = {F:7.5f} = {10 * math.log10(F):6.4f} dB")
```

The naive route reads the 10 k$\Omega$ resistor's own density, squares the ratio to the
source's, and reports that the bias resistor contributes two hundred times the source's
noise power — a $23.03$ dB noise figure from a bias network. The honest answer is
$0.0217$ dB, a factor of two hundred out in power and a design killed on paper for no
reason.

The mistake is tempting for a good reason: the 10 k$\Omega$ resistor's density really is
fourteen times the source's, and in a *series* path a source fourteen times larger
really would dominate. What breaks the analogy is that this resistor is across the path
rather than in it. Its own open-circuit voltage never appears anywhere, because it is
loaded by $R_s$; what appears is the voltage of the parallel combination, which is
smaller than either. And the divider that shrinks the noise shrinks the signal in step,
which is why the answer depends only on the ratio $R_s/R_B$ and not on $R_B$ alone.

The contrast makes the rule usable. Put the same 50 $\Omega$ *in series* with the source
instead and the noise factor is $1 + R_{series}/R_s = 2$, or $3.01$ dB. Identical part,
identical physics, opposite consequence: a shunt resistor at a high-impedance node wants
to be as large as the bias circuit will tolerate, a series resistor in the signal path
wants to be as small as possible, and the parallel rule is what separates them. Drop
$R_B$ to $200\ \Omega$ and the penalty is back to $0.97$ dB, which for a front end with
a $2$ dB budget is half the budget spent on a bias resistor.

## The number every radio quotes against

The derivation unit's second step shows that the power a resistor delivers to a matched
load is $k_BTB$, with the resistance cancelling out. That cancellation is what lets a
noise figure be a property of a component rather than of a measurement setup, and it
gives radio its one universal constant:

$$k_BT_0 = 1.380649\times10^{-23}\times290 = 4.004\times10^{-21}\ \text{W/Hz}
= -173.98\ \text{dBm/Hz}$$

quoted as $-174$. Everything on the noise side of a link budget is that number plus
$10\log_{10}B$ plus the noise figure. For the anti-alias filter the capstone puts at the
end of its chain, $B = 15.625$ MHz contributes $71.94$ dB, so the floor is
$-102.04$ dBm before a single stage has been named — which is where module 4 picks the
argument up.

## Where the flat floor stops being flat

The flat density is the low-frequency limit of a Planck expression,
$S_v = 4R\,hf/\left(e^{hf/k_BT}-1\right)$, and the approximation is good while
$hf \ll k_BT$. At $290$ K the two are equal at $k_BT/h = 6.04$ THz, and the density is
still within one per cent of flat at $121$ GHz — far above anything in this course, but
not above every measurement, and the correction is real for cryogenic millimetre-wave
receivers where $T$ is $20$ K rather than $290$.

Two conditions matter more in practice. The first is that the equivalent-resistance rule
holds for a network at *one* temperature. A $290$ K terminator in parallel with a $20$ K
cryogenic load is not a resistor at any temperature at all; the two contributions have to
be computed and added as powers, each with its own $T$. The second is that $4k_BTR$ is
an *equilibrium* result. Force current through a real resistor and it produces excess
noise on top, $1/f$ in shape and worst in carbon composition parts — which is module 2,
and which is why that module opens with a device carrying current rather than one lying
in a drawer. A MOSFET channel in saturation is the extreme case: it is a resistance that
is nowhere near equilibrium, and its noise is $4k_BT\gamma g_{d0}$ with $\gamma$ well
above the $1/2$ the equilibrium argument would give.

The last limit is the one that costs the most money. $S_v$ is a density; it says nothing
until a bandwidth has been named, and the bandwidth is not the one on the datasheet.

The lab for this module, *Thermal noise of a resistive network*, is the four ideas above
as four functions. Its fourth test is the one to watch: it asserts that
1 k$\Omega \parallel$ 1 k$\Omega$ is *quieter* than 1 k$\Omega$ alone, which fails at
once for anyone who added two densities instead of taking the equivalent resistance —
the same slip as the 23 dB bias network, in three lines instead of a design review. Its
last test draws two hundred thousand samples and demands their standard deviation match
the r.m.s. you predicted to within two per cent, which is the point at which the
arithmetic stops being a formula and starts being a thing on a scope.
''',
                },
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
            "read": [
                {
                    "title": "Thirty-four nanovolts at a kilohertz, two and a half at ten megahertz",
                    "minutes": 17,
                    "body": r'''
The device from RFIC510 is back on the probe station: NMOS, $20\ \mu\text{m}$ wide,
$0.5\ \mu\text{m}$ long, gate $200$ mV above threshold, drain current
$172.8\ \mu\text{A}$, $g_m = 1.728$ mS. This time the drain feeds a low-noise
transimpedance front end and a spectrum analyser, and the trace is divided by $g_m$ so
that everything is quoted as a voltage at the gate. Three readings off that trace:

```text
    1 kHz    34.190 nV/rtHz
  100 kHz     4.220 nV/rtHz
   10 MHz     2.509 nV/rtHz
```

The top of the band is flat — take another reading at $20$ MHz and it does not move.
The bottom is not flat, and it is thirteen times higher. Nothing in module 1 predicts
that. A resistor's density has no frequency in it at all, and this device is drawing
current, which is the difference.

## The flat part is the channel, referred to the gate

In saturation the channel is a resistive medium carrying current, and its thermal noise
appears as a current source between drain and source with density
$\overline{i_d^2} = 4k_BT\gamma g_{d0}$, where $g_{d0}$ is the channel conductance at
zero drain bias and $\gamma$ is a fudge that accounts for the channel being pinched
rather than uniform. For a long device in saturation $g_{d0} = g_m$ and $\gamma = 2/3$.

A current at the drain is not comparable with a signal at the gate, so refer it back the
way module 3 will make a habit: a gate voltage $v_g$ produces a drain current $g_mv_g$,
so a drain current $i_d$ is equivalent to a gate voltage $i_d/g_m$. Dividing the density
by $g_m^2$:

$$S_{th} = \frac{4k_BT\gamma g_m}{g_m^2} = \frac{4k_BT\gamma}{g_m}$$

which for $\gamma = 2/3$ and $g_m = 1.728$ mS is $6.179\times10^{-18}$ V$^2$/Hz, or
$2.486$ nV/$\sqrt{\text{Hz}}$. The $10$ MHz reading is $2.509$, one per cent above it.
Read the shape of that expression before its value: it is $4k_BTR$ from module 1 with
$R$ replaced by $\gamma/g_m$, so the whole of low-noise amplifier design is the fight to
make $1/g_m$ small, and $g_m$ costs current.

## The sloped part, and the slope you cannot read off the plot

The first move most people make is to take the ratio of the two low readings. Between
$1$ kHz and $100$ kHz the density falls by $34.190/4.220 = 8.10$ over two decades. A
$1/f$ power spectrum is $1/\sqrt{f}$ in density, so two decades should give exactly
$10$. Eight is not ten, and the temptation is to write down an exponent of $0.9$ and
call it a fitted slope.

It is not a slope of the mechanism. Both readings contain the flat floor, which is not
negligible at $100$ kHz. Powers are what add, so subtract the floor in power before
taking any ratio at all.

```python
import math

K_B, T, GAMMA = 1.380649e-23, 290.0, 2.0 / 3.0
G_M, C_OX_WL, K_F = 1.728e-3, 8.6e-14, 1.0e-25

s_th = 4.0 * K_B * T * GAMMA / G_M
f_c = K_F / (C_OX_WL * s_th)
print(f"gate-referred thermal floor : {math.sqrt(s_th) * 1e9:6.3f} nV/rtHz")
print(f"corner frequency            : {f_c / 1e3:6.1f} kHz")
for f in (1e3, 1e5, 1e7):
    total = s_th * (1.0 + f_c / f)
    print(f"  {f:9.0f} Hz  total {math.sqrt(total) * 1e9:7.3f} nV/rtHz   "
          f"floor removed {total - s_th:.4e} V^2/Hz")
print("flicker power, 1 kHz against 100 kHz:",
      round((s_th * f_c / 1e3) / (s_th * f_c / 1e5), 1))
print("total density, same two decades    :",
      round(math.sqrt(s_th * (1 + f_c / 1e3)) / math.sqrt(s_th * (1 + f_c / 1e5)), 3))
```

With the floor removed the two flicker powers stand in the ratio $100.0$ over two
decades, which is an exponent of exactly one. The $8.102$ was the floor filling in from
underneath, and anybody who fits a straight line to log-log data within a decade of the
corner will report a mechanism that does not exist. This is why the module's lab, *Fit a
corner frequency to a measured spectrum*, fits $d^2 = a + b/f$ rather than fitting a
slope: in that form the two mechanisms are two separate coefficients, and neither one
contaminates the other.

## Where the $1/f$ comes from, and what the corner is made of

The mechanism is trapping. The oxide interface carries defects that capture a channel
carrier, hold it and release it. One trap with time constant $\tau$ gives a Lorentzian,
flat below $1/\tau$ and falling as $1/f^2$ above. A real interface holds a population of
them at different depths, and because capture time depends exponentially on depth, a
uniform spread in depth becomes a $1/\tau$ spread in time constants — and Lorentzians
summed over such a spread give $1/f$ across many decades, which is why the law holds so
absurdly far. Referred to the gate, the accepted form is

$$S_{fl}(f) = \frac{K_f}{C_{ox}WL\,f}$$

with the gate area in the denominator, because a larger gate averages over more traps
and each one moves a smaller fraction of the total charge. For this device
$C_{ox}WL = 8.6\times10^{-3}\times20\times10^{-6}\times0.5\times10^{-6} = 86$ fF — and
note in passing that $\tfrac{2}{3}$ of that is $57.3$ fF, which is exactly the $C_{gs}$
RFIC510 spent two modules on. With $K_f = 1.0\times10^{-25}$ V$^2$F the corner, from
setting the two densities equal, lands at

$$f_c = \frac{K_fg_m}{4k_BT\gamma\,C_{ox}WL} = 188.2\ \text{kHz}$$

## The logarithm, and why patience stops paying

Integrate the total density over a band. The thermal part contributes
$S_{th}(f_2-f_1)$, linear in bandwidth as module 1 said it would be. The flicker part
contributes $S_{th}f_c\ln(f_2/f_1)$, which depends on the *ratio* of the band edges and
not on their difference at all. Every decade contributes the same $S_{th}f_c\ln 10$,
whether it is the decade from $100$ kHz to $1$ MHz or the one from $0.001$ Hz to
$0.01$ Hz.

```python
import math

K_B, T, GAMMA = 1.380649e-23, 290.0, 2.0 / 3.0
G_M, C_OX_WL, K_F = 1.728e-3, 8.6e-14, 1.0e-25
s_th = 4.0 * K_B * T * GAMMA / G_M
f_c = K_F / (C_OX_WL * s_th)


def rms(f1, f2):
    """Total r.m.s. volts between two frequencies, both mechanisms."""
    return math.sqrt(s_th * ((f2 - f1) + f_c * math.log(f2 / f1)))


print(f"0.1 Hz to  10 Hz : {rms(0.1, 10.0) * 1e6:7.4f} uV rms")
print(f" 10 Hz to  1 kHz : {rms(10.0, 1e3) * 1e6:7.4f} uV rms")
print(f"thermal only over the first band : {math.sqrt(s_th * 9.9) * 1e9:6.3f} nV rms")
print(f"one decade on its own            : "
      f"{math.sqrt(s_th * f_c * math.log(10.0)) * 1e6:7.4f} uV rms")
print(f"0.1 Hz to 1 kHz  : {rms(0.1, 1e3) * 1e6:7.4f} uV rms  "
      f"({rms(0.1, 1e3) / rms(10.0, 1e3):.3f}x the 10 Hz start)")
print(f"chopped to 1 MHz, same 9.9 Hz    : "
      f"{math.sqrt(s_th * (1 + f_c / 1e6) * 9.9) * 1e9:6.3f} nV rms")
```

Two bands, both two decades wide, one of them a hundred times narrower in hertz than the
other: $2.3141$ $\mu$V against $2.3154$ $\mu$V. They are the same number to three
figures, and that single comparison is the whole character of $1/f$ noise. Against it,
the thermal contribution over the first band is $7.8$ nanovolts — the flicker noise is
$296$ times larger, and a designer who budgeted $4k_BT\gamma/g_m$ over $9.9$ Hz would be
wrong by nearly fifty decibels.

Now do the thing every measurement instinct says to do: average for a hundred times
longer. The top of the band is set by an output filter and does not move; the bottom
goes from $10$ Hz to $0.1$ Hz, because a longer record is sensitive to slower drift.
The r.m.s. goes from $2.3154$ to $3.2735$ $\mu$V — worse by $41\%$, where white
noise would have promised a factor of ten better. That is the fact the module's blanks
unit, *The corner, and why waiting stops helping*, ends on, and it is the reason
chopping exists: the last line of the block moves the signal to $1$ MHz, where the
density is $2.71$ nV/$\sqrt{\text{Hz}}$, and the same $9.9$ Hz of final bandwidth now
costs $8.5$ nV instead of $2.31\ \mu$V. Two hundred and seventy times better, $48.7$ dB,
bought with a modulator and a demodulator rather than with a bigger transistor.

## Fitting the two coefficients, and what the lab's tolerance is really about

The lab has you recover $(n_{th}, f_c)$ from a measured curve by least squares on $d^2$.
Two things about that are worth doing by hand once.

```python
import math

K_B, T, GAMMA = 1.380649e-23, 290.0, 2.0 / 3.0
G_M, C_OX_WL, K_F = 1.728e-3, 8.6e-14, 1.0e-25
s_th = 4.0 * K_B * T * GAMMA / G_M
f_c = K_F / (C_OX_WL * s_th)


def line_fit(xs, ys):
    """Least squares y = a + b x, by the normal equations."""
    n = float(len(xs))
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    det = n * sxx - sx * sx
    return (sy * sxx - sx * sxy) / det, (n * sxy - sx * sy) / det


def band(lo, hi, n=201):
    return [lo * (hi / lo) ** (i / (n - 1.0)) for i in range(n)]


def measured(f, i, ripple):
    """The true curve, with an alternating +-ripple standing in for scatter."""
    return math.sqrt(s_th * (1.0 + f_c / f)) * (1.0 + ripple * (1 if i % 2 else -1))


for lo, hi in ((1e2, 1e7), (5e4, 5e5)):
    fs = band(lo, hi)
    for ripple in (0.0, 0.01):
        a, b = line_fit([1.0 / f for f in fs],
                        [measured(f, i, ripple) ** 2 for i, f in enumerate(fs)])
        print(f"d^2 fit {lo:8.0f}-{hi:8.0f} Hz, +-{ripple * 100:3.0f}% : "
              f"nth {math.sqrt(a) * 1e9:6.3f} nV/rtHz   fc {b / a / 1e3:7.1f} kHz")
fs = band(1e2, 1e7)
a, b = line_fit([1.0 / f for f in fs], [measured(f, i, 0.0) for i, f in enumerate(fs)])
print(f"d fit (not d^2), clean data      : "
      f"nth {a * 1e9:6.3f} nV/rtHz   fc {b / a / 1e3:7.1f} kHz")
```

The last line is the mistake, and it is a tempting one because the density is the thing
the instrument displays. Regressing $d$ on $1/f$ instead of $d^2$ reports a floor of
$8.479$ nV/$\sqrt{\text{Hz}}$ and a corner of $1.5$ kHz from data that came from a floor
of $2.486$ and a corner of $188$ kHz — a floor three and a half times too high and a
corner a hundred and twenty times too low, on perfect data. Only the *power* is linear in
$1/f$; $\sqrt{a + b/f}$ is linear in nothing.

The other lines are more surprising. Clean data recovers the truth from any band, because
the model is exact. Add a $\pm1\%$ scatter and the five-decade fit returns $2.626$
nV/$\sqrt{\text{Hz}}$ and $168$ kHz while the half-decade fit around the corner returns
$2.486$ and $188.0$ — the *wider* sweep is the worse estimate. The reason is leverage:
$d^2$ at $100$ Hz is nearly two thousand times $d^2$ at $10$ MHz, so an unweighted least
squares is almost entirely a fit to the bottom two decades. The lab's noisy test allows
the floor ten per cent and the corner twenty; that tolerance is a statement about
leverage, not about sloppy arithmetic.

## The mistake, and why it is tempting

The corner frequency is the one flicker number on a datasheet, and it gets used as a
figure of merit for how noisy a device is at low frequency. It is not one. It is a
*ratio* of two independent quantities, and it moves when either of them moves.

```python
import math

K_B, T, GAMMA = 1.380649e-23, 290.0, 2.0 / 3.0
C_OX_WL, K_F = 8.6e-14, 1.0e-25
for g_m, label in ((1.728e-3, "as biased "), (3.456e-3, "4x current")):
    s_th = 4.0 * K_B * T * GAMMA / g_m
    f_c = K_F / (C_OX_WL * s_th)
    at_1hz = math.sqrt(s_th + K_F / (C_OX_WL * 1.0))
    print(f"{label}  g_m {g_m * 1e3:5.3f} mS   floor {math.sqrt(s_th) * 1e9:5.3f} "
          f"nV/rtHz   f_c {f_c / 1e3:6.1f} kHz   at 1 Hz {at_1hz * 1e6:6.4f} uV/rtHz")
```

Quadruple the bias current at fixed geometry. The overdrive doubles, $g_m$ doubles, the
thermal floor drops by $\sqrt{2}$ — and the corner *doubles*, to $376$ kHz. By the
datasheet metric the device has become twice as flicker-noisy. The gate-referred density
at $1$ Hz is $1.0783\ \mu$V/$\sqrt{\text{Hz}}$ before and after, identical to five
figures, because $K_f/(C_{ox}WLf)$ contains no bias at all. Nothing about the flicker
noise changed; the yardstick moved.

It is tempting for the same reason $f_T$ was tempting in RFIC510: the corner is a real
measurement, it is the only frequency in the noise section of the datasheet, and at a
*fixed* bias it does track the flicker level faithfully. What it cannot do is compare two
operating points, or two devices at different currents. The quantity that compares them
is $K_f/(C_{ox}WL)$ — flicker noise at one hertz — and the corner is that quantity
divided by a thermal floor that the designer is separately trying to lower.

The lever that does work is area. The module's derivation,
*Locating the corner of a MOS transistor*, has you double $W$ and $L$ with $g_m$ held
constant: four times the area, a corner at $47.0$ kHz, and the integrated noise from
$0.1$ to $10$ Hz falls from $2.314$ to $1.157\ \mu$V — exactly half, because the flicker
power fell by four and it was already $99.99\%$ of the total. Four times the area for
$6$ dB, and the area is paid for by whatever has to drive the gate capacitance.

## Where the model stops holding

The exponent is not exactly one. Measured devices come in between about $0.8$ and $1.3$,
and a spectrum fitted as $1/f$ over five decades can be wrong by a factor of two at the
ends.

More sharply, the ensemble itself can fail. Shrink the gate far enough and the trap
population is not a population — it is three traps, or one. The drain current then jumps
between discrete levels at random times: random telegraph signal noise, whose spectrum is
a single Lorentzian. No spectral density describes it usefully, because what a circuit
meets is a step of a definite size at an unpredictable moment. This is why the flicker
model is a large-device model, and why a precision input pair is enormous for two reasons
rather than one.

$K_f$ is not a constant either. It varies with bias and with oxide processing, and by
roughly an order of magnitude between NMOS and PMOS in the same process — PMOS the quiet
one, which is why so many low-frequency input stages are p-type despite the mobility
penalty. The model's divergence as $f\to0$ describes a measurement that never ends; every
real record has a finite length, and the low band edge is its reciprocal.

The sandbox for this module, *Where the two mechanisms cross*, is where the two terms can
be moved independently and watched. Its first note is the one to take seriously: at the
corner the curve sits $3$ dB above the floor, not $6$, because equal *powers* is
$\sqrt{2}$ in volts. Get that factor wrong and every corner you fit will be in the wrong
place.
''',
                },
            ],
            "quiz": {
                "title": "Reading a spectrum that is not flat",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A gate-referred density falls from $34.19$ to $4.22$ nV/$\\sqrt{\\text{Hz}}$ between 1 kHz and 100 kHz — a factor of $8.10$ over two decades, where a $1/f$ power spectrum predicts exactly $10$. What does the shortfall tell you about the mechanism?",
                        "opts": [
                            "Nothing: the floor is in both readings, and removing it in power restores the exponent",
                            "The exponent is 0.9 rather than 1, which is inside the range real devices are known to show",
                            "The two mechanisms have started to interfere, so their densities no longer add in power",
                            "The measurement is compressed at 1 kHz, so the low reading is an instrument artefact",
                        ],
                        "a": 0,
                        "whys": [
                            r"Subtract $S_{th} = 6.179\times10^{-18}$ from each squared reading and the remaining powers stand at exactly $100.0$ to one.",
                            r"A defensible reading, and the reason this trap catches people: exponents near $0.9$ are real and get published. But here the generating model has an exponent of exactly 1, and the shortfall is entirely the floor filling in — at 100 kHz the flat term is already a third of the total power. Fit a slope near the corner and you will invent a mechanism.",
                            r"Trapping and channel thermal noise are physically independent processes, so their power densities add with no cross term at any frequency. If they interfered, the whole $\sqrt{1 + f_c/f}$ model — and the corner itself — would be meaningless.",
                            r"Nothing is compressed: $34$ nV/$\sqrt{\text{Hz}}$ is a perfectly ordinary reading for a small device at 1 kHz, and the same shortfall appears in noiseless synthetic data generated from the model.",
                        ],
                        "why": r'''
Both readings contain the flat term as well as the sloped one, and powers are what add.
Subtracting $S_{th}$ from each squared density leaves flicker powers in the ratio
$100.0$ over two decades, which is an exponent of exactly one. The floor contributes
$0.5\%$ of the power at 1 kHz and $35\%$ at 100 kHz, so it drags the apparent slope down
near the corner and nowhere else. This is exactly why the lab fits $d^2 = a + b/f$
instead of fitting a slope: in that form the two mechanisms are two coefficients and
neither one contaminates the other.
''',
                    },
                    {
                        "q": "At fixed geometry the bias current is quadrupled, so the overdrive and $g_m$ both double. What happens to the corner frequency and to the gate-referred density at 1 Hz?",
                        "opts": [
                            "Both fall: more transconductance means less noise referred to the gate at every frequency",
                            "The corner doubles, and the 1 Hz density is unchanged to five figures",
                            "The corner doubles, and the 1 Hz density doubles with it",
                            "The corner halves, because the flicker term is being divided by a larger $g_m$",
                        ],
                        "a": 1,
                        "whys": [
                            r"Half right. The thermal floor does fall, by $\sqrt{2}$ in volts, and above the corner the device is genuinely quieter. Below the corner nothing moves, because the flicker expression $K_f/(C_{ox}WLf)$ has no $g_m$ in it — and the corner, being the crossing of a falling floor with an unmoved slope, goes up.",
                            r"$f_c \propto g_m$, and $K_f/(C_{ox}WLf)$ contains no bias term at all.",
                            r"The first half is right and the second is the trap. If the flicker density tracked the corner, the corner would be a fair measure of flicker noise — but $1.0783\ \mu$V/$\sqrt{\text{Hz}}$ at 1 Hz before is $1.0783$ after, to five figures.",
                            r"This inverts the dependence. $f_c = K_fg_m/(4k_BT\gamma C_{ox}WL)$ has $g_m$ in the numerator, because raising it lowers the floor that flicker is being compared against and the crossing moves up in frequency.",
                        ],
                        "why": r'''
The corner is a ratio of two independent quantities. Flicker noise referred to the gate
is $K_f/(C_{ox}WLf)$ — geometry and process, no bias. The thermal floor is
$4k_BT\gamma/g_m$ — bias, no geometry. Doubling $g_m$ halves the floor in power and so
doubles the frequency at which the two cross, while leaving the flicker density
untouched at every frequency. By the datasheet metric the device has become twice as
flicker-noisy; in absolute terms its low-frequency noise did not move and its
high-frequency noise improved. This is why $K_f/(C_{ox}WL)$, not $f_c$, is what compares
two operating points.
''',
                    },
                    {
                        "q": "A d.c. measurement observes 10 Hz to 1 kHz. The record length is increased a hundredfold, which lowers the bottom of the band to 0.1 Hz and leaves the top where it is. What happens to the r.m.s. noise on this device?",
                        "opts": [
                            "It falls tenfold, as the square root of the hundredfold increase in averaging time",
                            "It is unchanged, because the added band is far below the corner and contributes nothing",
                            "It rises by about 40 per cent, because the new decades cost as much as the first two",
                            "It falls, but by rather less than tenfold, because flicker noise averages more slowly",
                        ],
                        "a": 2,
                        "whys": [
                            r"This is the white-noise answer, and it is right for thermal noise and wrong here. $\sqrt{T}$ averaging assumes every hertz carries the same power; below the corner every *decade* does, and opening the band downward hands back as much as it removes.",
                            r"Backwards about where the power is. Far below the corner is precisely where the power is densest: $\int df/f$ makes the decade from 0.1 to 1 Hz worth as much as the decade from 100 to 1000 Hz, even though it is a thousandth of the width in hertz.",
                            r"$2.3154\ \mu$V becomes $3.2735\ \mu$V — the two new decades add the same $S_{th}f_c\ln 10$ each as the two already there.",
                            r"Averaging does not slow down; it stops working and reverses. The total mean square grows as $\ln(f_2/f_1)$, so it increases without bound as the record lengthens, which is why slow drift cannot be averaged out of an amplifier at all.",
                        ],
                        "why": r'''
The flicker contribution to the mean square is $S_{th}f_c\ln(f_2/f_1)$, so it depends on
the ratio of the band edges. Two decades of band carry $2S_{th}f_c\ln 10$ whatever
frequencies they sit at; the original 10 Hz to 1 kHz gave $2.3154\ \mu$V and adding 0.1
to 10 Hz gives $3.2735\ \mu$V, a factor of $\sqrt{2}$. Patience buys nothing, which is
the whole argument for chopping: move the signal up to 1 MHz and the same 9.9 Hz of
final bandwidth costs $8.5$ nV instead of $2.3\ \mu$V.
''',
                    },
                    {
                        "q": "Chopping modulates the signal to 1 MHz at the input and demodulates it after the amplifier. Why does this device end up $48$ dB quieter?",
                        "opts": [
                            "The modulation cancels the trapping process, since the carriers are released before they can be caught",
                            "The chopper narrows the final bandwidth, and less bandwidth means less total noise",
                            "The amplifier's own noise stays where it is while the signal moves to where the density is flat",
                            "The flicker noise averages to zero over a chopping period, since it has no d.c. component",
                        ],
                        "a": 2,
                        "whys": [
                            r"The traps know nothing about the chopper. Capture and emission are set by the oxide and the bias, and a modulator in the signal path changes neither — which is the point: the noise is left exactly where it was.",
                            r"The final bandwidth is 9.9 Hz either way in this comparison, so bandwidth explains none of the improvement. What changed is the density inside that bandwidth: $2.71$ nV/$\sqrt{\text{Hz}}$ at 1 MHz against decades of $1/f$ at d.c.",
                            r"The signal ends up in a 9.9 Hz band around 1 MHz where the density is $2.71$ nV/$\sqrt{\text{Hz}}$, near the thermal floor.",
                            r"Flicker noise has no d.c. component in the sense of a mean, but that is not what averaging removes — its power is concentrated at low frequencies, which is exactly where a slow average is most sensitive. If it averaged away, chopping would be unnecessary.",
                        ],
                        "why": r'''
Nothing about the device changes. The signal is moved to a frequency where the
amplifier's input-referred density is $2.71$ nV/$\sqrt{\text{Hz}}$ rather than tens of
nanovolts, amplified there, and brought back down; the amplifier's own $1/f$ noise stays
at low frequency and is moved *up* by the output demodulator, away from the recovered
signal. The same $9.9$ Hz of final bandwidth then costs $8.5$ nV instead of
$2.31\ \mu$V, a factor of $271$. The price is a modulator, a demodulator, and residual
offset from charge injection at the switches.
''',
                    },
                    {
                        "q": "$W$ and $L$ are both doubled and the bias is adjusted to hold $g_m$ where it was. What does that buy on this device?",
                        "opts": [
                            "The corner falls to a quarter and the noise integrated from 0.1 to 10 Hz halves",
                            "The corner falls to a half, since only one dimension affects trapping",
                            "The corner is unchanged, because the thermal floor it is measured against did not move",
                            "The corner falls to a quarter and the integrated low-frequency noise falls with it",
                        ],
                        "a": 0,
                        "whys": [
                            r"Four times the area is a quarter of the flicker power, and $188.2$ kHz becomes $47.0$ kHz.",
                            r"Only the product $WL$ appears in $K_f/(C_{ox}WLf)$, so the gate *area* is what counts and there is nothing special about either dimension on its own. Doubling both is four times the area, not two.",
                            r"The floor is indeed unchanged — that was the point of holding $g_m$ fixed — but the corner is where the floor meets the flicker term, and the flicker term dropped by four. A crossing moves if either curve moves.",
                            r"The first half is right, and this is the plausible way to get the second half wrong. The corner falls by four and the flicker *power* falls by four, but r.m.s. voltage is the square root of power: $2.314\ \mu$V becomes $1.157\ \mu$V, a factor of two, not four.",
                        ],
                        "why": r'''
Flicker density goes as $1/WL$, so four times the area is a quarter of the flicker power
at every frequency and a corner at $47.0$ kHz. The band from 0.1 to 10 Hz is
$99.99\%$ flicker, so its mean square falls by very nearly four and its r.m.s. by two:
$2.314\ \mu$V becomes $1.157\ \mu$V. Six decibels for four times the area, and the area
is paid for in gate capacitance that the previous stage has to drive — which is the
trade the derivation unit closes on, and the reason low-frequency input devices are
enormous compared with anything in a digital gate.
''',
                    },
                    {
                        "q": "A very small device shows its drain current jumping between two discrete levels at random times, instead of the smooth $1/f$ spectrum the model predicts. What has happened?",
                        "opts": [
                            "The device has slid into weak inversion, where the current is exponential in $V_{GS}$",
                            "The gate is small enough that one trap dominates, and $1/f$ was an average over many",
                            "Thermal noise in the channel is being rectified by the device's own non-linearity",
                            "The measurement is aliasing, and a faster sampler would recover the expected spectrum",
                        ],
                        "a": 1,
                        "whys": [
                            r"Weak inversion changes how $g_m$ depends on current and caps $g_m/I_D$ near $30\ \text{V}^{-1}$; it does not make the current jump between two levels. A device can be in weak inversion and show a perfectly smooth spectrum.",
                            r"One trap is a Lorentzian and a two-level switch; $1/f$ needs a $1/\tau$-distributed population of them.",
                            r"Rectification of thermal noise would show as a small shift in the mean, not as discrete switching between two levels with dwell times of milliseconds to seconds. Thermal noise is also Gaussian and continuous, which a two-level signal is not.",
                            r"Aliasing folds high-frequency content down; it does not manufacture two discrete current levels. Sampling faster leaves the telegraph signal exactly where it is, which is how it was identified in the first place.",
                        ],
                        "why": r'''
The $1/f$ law is an ensemble result: many traps with time constants spread as $1/\tau$,
whose Lorentzians sum to a straight line on log-log axes. Shrink the gate and the
population becomes a handful, then one, and what remains is that one trap's Lorentzian —
a random telegraph signal, discrete in amplitude and unpredictable in time. A spectral
density describes it badly, because what a circuit meets is a step of a definite size at
an unknown moment rather than a fluctuation of a known variance. This is where the
flicker model stops holding, and it is the second reason precision input devices are
large: not only to lower $K_f/(C_{ox}WL)$, but to keep the ensemble an ensemble.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "A 1.4 dB amplifier in a 2 dB receiver, and where the rest went",
                    "minutes": 17,
                    "body": r'''
Four lines from the capstone's `chain.py`, which is a perfectly ordinary front-end
specification:

```text
    LNA          NF 1.4 dB    gain 16 dB
    mixer        NF 9.0 dB    gain  5 dB
    IF amp       NF 4.5 dB    gain 22 dB
    ADC driver   NF 14.0 dB   gain  0 dB
```

The system budget is $2.0$ dB. The LNA is the part everyone argued about, it came in at
$1.4$ dB, and the minutes of the design review record $0.6$ dB of margin. The cascade
noise figure of that chain is $1.960$ dB. There is $0.04$ dB of margin, and one more
decibel of insertion loss anywhere in front of the LNA would sink the receiver.

## What the 1.4 dB is a statement about

Start with the amplifier rather than with the definition. A common-source device is
driven from a source resistance $R_s$; the gate draws no current, so the source's
thermal noise $4k_BTR_s$ appears at the gate in full and produces a drain current of
density $g_m^2\cdot4k_BTR_s$. The device's own channel noise, from module 2, is a drain
current of density $4k_BT\gamma g_m$. Both are currents at the same node, they are
uncorrelated, so their powers add — and the ratio of the total to the part that came
from the source is the noise factor:

$$F = \frac{g_m^2\,4k_BTR_s + 4k_BT\gamma g_m}{g_m^2\,4k_BTR_s}
= 1 + \frac{\gamma}{g_mR_s}$$

That is `chain.py`'s LNA model, and it took four lines and no new ideas. Read what is in
it. There is no gain: $g_m$ cancelled out of the ratio, which is why noise figure is a
property of a two-port and not of what follows it. There is a source resistance, which
means a noise figure quoted without one is not a number. And $T$ cancelled too — but only
because the *same* $T$ appeared in both terms, and the convention that fixes it is
$T_0 = 290$ K by definition, not by measurement of anything.

## The device from the prerequisite course, priced

RFIC510 spent four modules on one transistor: $20\ \mu\text{m}$ by $0.5\ \mu\text{m}$,
$172.8\ \mu\text{A}$, $g_m = 1.728$ mS. Put it in a 50 $\Omega$ system.

```python
import math

GAMMA, R_S, GM_COEFF, SUPPLY = 2.0 / 3.0, 50.0, 0.5, 1.8


def nf_db(g_m, r_s=R_S):
    """Noise figure of the common-source stage, in dB."""
    return 10.0 * math.log10(1.0 + GAMMA / (g_m * r_s))


def gm_for(target_db):
    """The transconductance that reaches a target noise figure on 50 ohm."""
    return GAMMA / ((10.0 ** (target_db / 10.0) - 1.0) * R_S)


print(f"the RFIC510 device, g_m = 1.728 mS : {nf_db(1.728e-3):6.3f} dB")
for target in (3.0, 2.0, 1.4, 1.0):
    g_m = gm_for(target)
    i = (g_m / GM_COEFF) ** 2
    print(f"  NF {target:4.1f} dB needs g_m {g_m * 1e3:6.2f} mS -> "
          f"{i * 1e3:6.3f} mA, {i * SUPPLY * 1e3:6.2f} mW")
print(f"the last 0.4 dB, from 1.4 to 1.0   : "
      f"{((gm_for(1.0) / GM_COEFF) ** 2 - (gm_for(1.4) / GM_COEFF) ** 2) * SUPPLY * 1e3:6.2f} mW")
print(f"the same 35.05 mS device on 200 ohm: {nf_db(gm_for(1.4), 200.0):6.3f} dB")
```

The device the whole prerequisite course was built around is a $9.40$ dB amplifier. To
reach $1.4$ dB it needs $35.05$ mS, twenty times the transconductance, and in the
capstone's own device model $g_m = 0.5\sqrt{I}$ that costs $4.915$ mA and $8.85$ mW.
Nothing has gone wrong; the two courses were asking different questions. $f_T$ wanted
$g_m$ per unit of capacitance and got a good answer at $172.8\ \mu\text{A}$. Noise figure
wants $g_m$ per unit of *source conductance*, and $1/(35\ \text{mS})$ is $28.5\ \Omega$,
a number that has to be comparable with $50\ \Omega$ before the ratio $\gamma/(g_mR_s)$
is small.

The last line of that block prices the thing people expect to be linear. Since
$F - 1 = \gamma/(g_mR_s)$ and $g_m \propto \sqrt{I}$, the current goes as
$1/(F-1)^2$. Going from $3.0$ dB to $2.0$ dB costs $1.36$ mA; going from $1.4$ dB to
$1.0$ dB costs $5.69$ mA and $10.25$ mW, which is more than the whole amplifier drew
before. Every decibel is more expensive than the one before it, quadratically, and that
is the sentence the capstone asks you to write at the top of `main.py`.

## Where the other 0.56 dB comes from

Friis, which the module's derivation unit *Friis, from the definition of noise factor*
builds line by line, says each stage's excess $F_i - 1$ is divided by all the gain in
front of it. Run it over the four stages and print the four terms rather than the total.

```python
import math

FRONT_END = [("LNA", 1.4, 16.0), ("mixer", 9.0, 5.0),
             ("IF amp", 4.5, 22.0), ("ADC driver", 14.0, 0.0)]


def lin(db_value):
    return 10.0 ** (db_value / 10.0)


def cascade(stages):
    """Friis: returns the total noise factor and the per-stage excesses."""
    F, G, terms = 1.0, 1.0, []
    for name, nf, gain in stages:
        excess = (lin(nf) - 1.0) / G
        terms.append((name, excess))
        F += excess
        G *= lin(gain)
    return F, terms


F, terms = cascade(FRONT_END)
print(f"cascade noise figure : {10 * math.log10(F):.4f} dB")
for name, excess in terms:
    print(f"  {name:11s} contributes {excess:.6f} of F, "
          f"{excess / (F - 1.0) * 100:5.1f}% of the excess")
print(f"equivalent noise temperature : {290.0 * (F - 1.0):.1f} K "
      f"(the LNA alone: {290.0 * (lin(1.4) - 1.0):.1f} K)")
for g1 in (16.0, 20.0, 24.0):
    F2, _ = cascade([("LNA", 1.4, g1)] + FRONT_END[1:])
    print(f"  with {g1:4.1f} dB of LNA gain : {10 * math.log10(F2):.4f} dB")
loss = lin(2.0)
print(f"a 2 dB filter ahead of it    : {10 * math.log10(loss * F):.4f} dB")
```

The excess over unity is $0.5704$, and the LNA owns two-thirds of it. Of the remaining
third, the mixer owns $92\%$ — because $9$ dB of noise figure divided by $16$ dB of gain
is still $0.174$, while the IF amplifier's $4.5$ dB, seen through $21$ dB of gain, has
shrunk to $0.014$ and the ADC driver's dreadful $14$ dB to $0.0012$. The chain is two
stages long as far as noise is concerned, and everything after the mixer is decoration.

That tells you where to spend. Four more decibels of LNA gain takes the cascade from
$1.960$ to $1.632$ dB — a third of a decibel, bought with gain rather than with the
quadratic current the LNA's own noise figure would have cost. Four more after that buys
only $0.14$ dB, because by then the mixer has stopped mattering and what is left is the
LNA's own $1.4$ dB, which no amount of gain behind it can touch. This is the sandbox for
this module, *The gain that decides whether the next stage matters*, in numbers: raising
$K$ divides everything downstream, and at the top of the band where the curve has rolled
off, $G_1$ is small and the whole chain reappears.

The last line is the one that decides projects. A passive lossy element at $T_0$ is a
resistor network, so terminated it delivers exactly $k_BT_0B$ — its output noise is the
same as its input noise, whatever the loss. With $S_o = S_i/L$ and $N_o = N_i$, its noise
factor is $L$ and its gain is $1/L$; substitute into Friis and the cascade becomes
$L + (F-1)L = LF$. In decibels that is exact addition: $2.000 + 1.960 = 3.960$. Front-end
filter loss is not approximately a decibel for a decibel, it is precisely one, and there
is no gain in front of it to divide the penalty down.

## The mistake, and why it is tempting

Friis divides $F_2 - 1$ by the gain, not $F_2$. The minus one looks like a small
correction and is the entire content of the formula.

```python
import math

FRONT_END = [("LNA", 1.4, 16.0), ("mixer", 9.0, 5.0),
             ("IF amp", 4.5, 22.0), ("ADC driver", 14.0, 0.0)]


def lin(db_value):
    return 10.0 ** (db_value / 10.0)


def cascade(stages, drop_minus_one=False):
    """Friis; with drop_minus_one, every stage after the first divides F rather
    than F - 1, which is the error this block is about."""
    F, G = 1.0, 1.0
    for i, (_, nf, gain) in enumerate(stages):
        sub = 0.0 if (drop_minus_one and i > 0) else 1.0
        F += (lin(nf) - sub) / G
        G *= lin(gain)
    return 10.0 * math.log10(F)


G1 = lin(16.0)
for nf2 in (9.0, 4.5, 1.0):
    F2 = lin(nf2)
    print(f"second stage at {nf2:4.1f} dB : (F2-1)/G1 = {(F2 - 1.0) / G1:.6f}, "
          f"F2/G1 = {F2 / G1:.6f}, a factor of {F2 / (F2 - 1.0):.2f} too big")
print(f"the whole chain, correctly        : {cascade(FRONT_END):.4f} dB")
print(f"the same chain, minus one dropped : "
      f"{cascade(FRONT_END, drop_minus_one=True):.4f} dB")
```

For the mixer the error is $14\%$; for a *quiet* second stage it is a factor of five,
because $F_2 - 1$ is small while $F_2$ is close to one. Across the whole chain it turns
$1.960$ dB into $2.051$ dB, which is small enough to survive a review and large enough to
fail a $2.0$ dB budget on a receiver that actually meets it.

It is tempting because $F$ is habitually spoken of as "the noise the stage adds", and if
that were so then dividing it by the preceding gain would be right. $F$ is not that: it
is the total noise at the stage's output referred to its input, and it already counts the
source noise once. The first stage has counted that source noise already. Subtracting one
removes the double count, and it is the reason a chain of noiseless stages gives $F = 1$
rather than $F = n$.

The related trap is the one at the top of this reading: quoting a component's noise
figure as the system's. It is tempting because the LNA is where the money and the
argument went, and because the LNA genuinely does dominate — two-thirds of the excess.
Two-thirds is not all of it, and the remaining third is $0.56$ dB, which was the whole
of the supposed margin.

## Kelvin, and when decibels stop being the right unit

$F = 1 + T_e/T_0$ defines an equivalent input noise temperature, and the derivation unit
converts the whole cascade into it. The chain above is $165.4$ K; the LNA alone is
$110.3$ K. The conversion is worth having because the noise figure of a good amplifier
compresses into an unreadable range. Half a decibel is $35.4$ K and four tenths is
$28.0$ K — a $26\%$ difference in what an antenna would actually see, hidden inside
$0.1$ dB.

It matters more when the source is not at $290$ K. Point a dish at cold sky, which
contributes about $20$ K, and put the $1.4$ dB LNA behind it: the system temperature is
$130$ K, of which the sky is $15\%$. The noise *figure* has silently assumed a $290$ K
source that is not there, and the ratio it reports — output SNR against an input SNR
computed for a room-temperature antenna — describes a measurement nobody made. Radio
astronomy quotes kelvin for this reason, and so does satellite work.

## Where the model stops holding

$F = 1 + \gamma/(g_mR_s)$ is missing three things, and each one bites at a different
place.

It has no gate-induced noise. The channel's fluctuations couple back through the gate
oxide into a gate current whose density rises as $f^2$, correlated with the drain noise.
Below about a tenth of $f_T$ it is negligible; above that it sets a floor the expression
above cannot see, and it is the reason a real low-noise design has an optimum source
impedance rather than improving without bound as $R_s$ rises. That unbounded improvement
is visible in the last line of the first block: the same $35.05$ mS device reads $0.39$
dB on a $200\ \Omega$ source. The model believes it; a measurement would not.

$\gamma$ is a long-channel $2/3$ here, and short-channel devices measure between $1$ and
$2$. At $\gamma = 1.5$ the same $1.4$ dB target needs $24.9$ mA rather than $4.9$ — five
times the current for a parameter that is quoted with one significant figure and rarely
measured.

Friis itself assumes *available* power gain and stages that do not load one another. If
stage two's input impedance changes what stage one delivers, or if reflections between
them make their noise contributions correlated, the terms stop adding. It also assumes
every stage is characterised at the source impedance it actually sees, which for anything
after the first stage is generally not $50\ \Omega$.

The module's lab, *Cascade a receiver and find the ordering that wins*, is where the
consequences become mechanical. It accumulates $F$ and $G$ linearly and converts once at
the end — the classic error is converting in the middle — and its last test hands you
three stages and asks for the ordering with the lowest cascade figure. On the capstone's
four stages the answer is LNA, IF amplifier, mixer, ADC driver, which is $1.548$ dB
against the $1.960$ dB of the specified order: swapping the mixer with the amplifier
behind it is worth four tenths of a decibel, and costs nothing at all.
''',
                },
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
            "read": [
                {
                    "title": "Fifteen point six megahertz out of a ten megahertz filter",
                    "minutes": 17,
                    "body": r'''
The last thing in the capstone's receiver is an anti-alias filter: one resistor of
2 k$\Omega$, one capacitor of 8 pF, probed across the capacitor. Its corner is

$$f_{3dB} = \frac{1}{2\pi RC} = \frac{1}{2\pi\times2000\times8\times10^{-12}}
= 9.947\ \text{MHz}$$

and the noise budget in the design file was written against that number: a $1.960$ dB
front end from a 50 $\Omega$ source over $9.947$ MHz comes to $3.537\ \mu$V r.m.s. at
the input, and a sensitivity of $-92.04$ dBm at 10 dB of required signal-to-noise ratio.

Both numbers are wrong, in the direction that loses the contract. The bandwidth that
matters is $15.625$ MHz, the input-referred noise is $4.433\ \mu$V, and the sensitivity
is $-90.08$ dBm. The receiver is $1.96$ dB worse than the file says — which is, to two
decimal places, the entire noise figure of the front end that module 3 spent nine
milliwatts buying.

## The bandwidth a noise measurement actually sees

A filter does not delete anything above its corner; it attenuates. Noise arrives at
every frequency, so the output noise power is the input density multiplied by the whole
area under the squared response:

$$\overline{v_o^2} = S_v\int_0^{\infty}\left|H(f)\right|^2df$$

Define an equivalent noise bandwidth as the width of the brick wall that would pass the
same power at the response's own peak gain:

$$B_n = \frac{1}{\left|H\right|^2_{max}}\int_0^{\infty}\left|H(f)\right|^2df$$

For one pole, $|H|^2 = 1/(1+(f/f_0)^2)$, whose peak is 1 at d.c., and the integral is an
arctangent:

$$\int_0^{X}\frac{df}{1+(f/f_0)^2} = f_0\arctan\!\left(\frac{X}{f_0}\right)
\ \longrightarrow\ \frac{\pi}{2}f_0$$

so $B_n = \tfrac{\pi}{2}f_{3dB}$, larger than the corner by $57\%$ in power. The
arctangent is worth pausing on, because it says exactly where the extra came from.
Evaluate it at $X = f_0$ and you get $\pi/4$ — precisely half the total. Half of a
single-pole filter's noise power arrives from frequencies above its own corner, and the
one decade from $f_0$ to $10f_0$ contributes $\arctan 10 - \arctan 1 = 0.6857$ of the
$1.5708$, which is $44\%$. A response falling at 20 dB per decade is not falling fast
enough to stop mattering.

```python
import math

K_B, T0, R_S = 1.380649e-23, 290.0, 50.0
R, C, NF_DB = 2.0e3, 8.0e-12, 1.9602


def h2(f, r, c):
    """|H(f)|^2 of the one-pole anti-alias filter."""
    return 1.0 / (1.0 + (f * 2.0 * math.pi * r * c) ** 2)


def log_grid(lo, hi, n):
    return [lo * (hi / lo) ** (i / (n - 1.0)) for i in range(n)]


def noise_bandwidth(fs, ys):
    """Trapezium area under a sampled power response, over its peak."""
    area = sum((fs[i + 1] - fs[i]) * 0.5 * (ys[i + 1] + ys[i])
               for i in range(len(fs) - 1))
    return area / max(ys)


fs = log_grid(1e2, 1e12, 40001)
bn = noise_bandwidth(fs, [h2(f, R, C) for f in fs])
f3 = 1.0 / (2.0 * math.pi * R * C)
print(f"corner            : {f3 / 1e6:8.4f} MHz")
print(f"integrated B_n    : {bn / 1e6:8.4f} MHz   (1/(4RC) = "
      f"{1.0 / (4.0 * R * C) / 1e6:.4f} MHz)")
print(f"ratio             : {bn / f3:8.4f}   (pi/2 = {math.pi / 2:.4f})")
F = 10.0 ** (NF_DB / 10.0)
for label, b in (("over the corner ", f3), ("over B_n        ", bn)):
    v = math.sqrt(4.0 * K_B * T0 * R_S * F * b)
    sens = 10.0 * math.log10(K_B * T0 * b * 1000.0) + NF_DB + 10.0
    print(f"  {label}: {v * 1e6:7.4f} uV rms   sensitivity {sens:8.3f} dBm")
print(f"the penalty for stopping at the corner: "
      f"{10 * math.log10(math.pi / 2):.4f} dB")
```

The module's build exercise, *Let the check do the integral*, is this block run against a
circuit you drew rather than a formula: its third check sweeps the schematic at four
thousand frequencies and integrates $|H|^2$ with the app's own solver, and its fourth
insists the ratio come out near $\pi/2$. The closed form $1/(4RC)$ that the derivation
unit reaches — where the $\pi$ from the arctangent cancels the $\pi$ in $f_0$ — is the
same number from the other side.

## What another pole is worth

For an $n$-pole Butterworth, $|H|^2 = 1/(1+(f/f_0)^{2n})$, and the same integral has a
closed form:

$$\frac{B_n}{f_{3dB}} = \frac{\pi/(2n)}{\sin\!\left(\pi/(2n)\right)}$$

which is $x/\sin x$ with $x = \pi/(2n)$. Since $\sin x < x$ for every $x > 0$, the ratio
is greater than one for every finite order and falls toward one as the order rises — a
real filter's noise bandwidth is always the wider number, and a brick wall is the limit
it approaches from above rather than a case it can reach.

```python
import math


def log_grid(lo, hi, n):
    return [lo * (hi / lo) ** (i / (n - 1.0)) for i in range(n)]


def noise_bandwidth(fs, ys):
    area = sum((fs[i + 1] - fs[i]) * 0.5 * (ys[i + 1] + ys[i])
               for i in range(len(fs) - 1))
    return area / max(ys)


fs = log_grid(1e2, 1e12, 40001)
previous = None
for n in (1, 2, 3, 4):
    ratio = noise_bandwidth(fs, [1.0 / (1.0 + (f / 1e6) ** (2 * n)) for f in fs]) / 1e6
    closed = (math.pi / (2 * n)) / math.sin(math.pi / (2 * n))
    gain = "" if previous is None else \
        f"   this pole is worth {10 * math.log10(previous / ratio):5.3f} dB"
    print(f"n = {n}: B_n/f_3dB numeric {ratio:.5f}, closed form {closed:.5f}{gain}")
    previous = ratio
```

The second pole is worth $1.51$ dB of noise power and the third only $0.26$. That is a
pricing rule for filter order that has nothing to do with stop-band rejection: past two
poles you are no longer buying noise performance, and whatever the third pole is for,
noise is not it.

## The peak in the denominator, and the trap in it

$B_n$ is normalised by $|H|^2_{max}$, not by $|H(0)|^2$, and for a filter with a resonant
peak the two are different numbers. This module's sandbox, *How much noise a filter shape
lets through*, is where it shows up: take $\zeta$ from $0.5$ down to $0.1$ on a two-pole
response and $B_n/f_{3dB}$ collapses, apparently making the filter quiet.

```python
import math

for zeta in (0.7071, 0.5, 0.1):
    def h2(u, z=zeta):
        return 1.0 / ((1.0 - u * u) ** 2 + (2.0 * z * u) ** 2)

    us = [1e-4 * (1e8) ** (i / 60000.0) for i in range(60001)]
    area = sum((us[i + 1] - us[i]) * 0.5 * (h2(us[i + 1]) + h2(us[i]))
               for i in range(len(us) - 1))
    peak = 1.0 / (4 * zeta ** 2 * (1 - zeta ** 2)) if zeta < 0.70710678 else 1.0

    def crossing(target, lo, hi):
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if h2(mid) > target else (lo, mid)
        return 0.5 * (lo + hi)

    f3_dc = crossing(0.5, 1e-3, 50.0)
    f3_peak = crossing(peak / 2.0, 1.0 + 1e-9, 50.0)
    print(f"zeta {zeta:6.4f}: area/f_n {area:7.4f}  peak {peak:8.4f}  "
          f"B_n/f_n {area / peak:6.4f}")
    print(f"            against f_3dB from d.c. ({f3_dc:6.4f}): "
          f"{area / peak / f3_dc:6.4f}   from the peak ({f3_peak:6.4f}): "
          f"{area / peak / f3_peak:6.4f}")
```

Two things fall out. The first is a definition trap: for a peaked response, "the 3 dB
point" is ambiguous, and the two readings give different answers. Measured 3 dB down from
the d.c. value, $\zeta = 0.1$ gives $B_n = 0.202f_{3dB}$; measured 3 dB down from the
peak — which is what a cursor on the plot does, and what the sandbox's first note
reports — it gives $0.286$. Quote either, but say which.

The second is the substance, and it inverts the apparent conclusion. Look at the raw
areas rather than the ratios: $1.111f_n$ at $\zeta = 0.7071$ and $7.854f_n$ at
$\zeta = 0.1$. The lightly damped filter passes *seven times* the noise power, $8.5$ dB
more. It scores well on $B_n$ only because the peak it is divided by grew faster than the
area did. That normalisation is the right one when the signal sits at the peak, as it
does in a tuned amplifier; if the signal is at baseband where the gain is 1, the number
that governs the output signal-to-noise ratio is the bare area, and the resonant filter
is the loud one. A figure of merit whose denominator is a gain the signal never sees is
not a figure of merit.

## The capacitor is the whole specification

Put $B_n = 1/(4RC)$ against the resistor's own density and watch what survives:

$$\overline{v_o^2} = 4k_BTR\cdot\frac{1}{4RC} = \frac{k_BT}{C}$$

The resistance has cancelled — a larger resistor is noisier per hertz and passes
proportionally fewer of them, in exact compensation. Nothing about the switch or the
source impedance changes the noise on a sampled node; only the capacitor does, and it
does so as $1/\sqrt{C}$.

```python
import math

K_B, T0 = 1.380649e-23, 290.0
for C in (1e-12, 4e-12, 12.9e-12):
    print(f"  {C * 1e12:5.1f} pF holds {math.sqrt(K_B * T0 / C) * 1e6:7.3f} uV rms")
for bits in (12, 14, 16):
    lsb = 1.0 / 2 ** bits
    q = lsb / math.sqrt(12.0)
    print(f"  {bits}-bit on 1 V full scale: LSB {lsb * 1e6:7.2f} uV, "
          f"quantisation {q * 1e6:6.3f} uV, needs C >= "
          f"{K_B * T0 / q ** 2 * 1e12:8.3f} pF")
```

The r.m.s. is the square root of the mean square, so halving the noise costs four times
the capacitance. Setting $\sqrt{k_BT/C}$ equal to the quantisation noise of an $n$-bit
converter, $V_{FS}/(2^n\sqrt{12})$, gives $C = 12k_BT\,2^{2n}/V_{FS}^2$ — four times the
capacitance per extra bit, sixteen times per two. On a 1 V full scale that is $0.81$ pF
at twelve bits, $12.9$ pF at fourteen and $206$ pF at sixteen, before a single circuit
consideration has been applied.

The current follows. To settle four times the capacitance in the same time, the driver
needs four times the transconductance; at a fixed $g_m/I_D$ — which is what holding the
overdrive constant means, in RFIC510's currency — that is four times the current, which
is the trade the concepts list states. Hold the *geometry* fixed instead and raise the
current, and the square law gives $g_m \propto \sqrt{I}$, so the same four times the
transconductance costs sixteen. Which factor applies depends entirely on whether the
device is allowed to grow, and quoting one without naming the assumption is how a power
budget goes wrong by a factor of four.

## The mistake, and why it is tempting

Budgeting noise at the $-3$ dB point is the most common arithmetic error in this course's
subject, and it is tempting for three good reasons. The corner *is* the signal bandwidth,
so it is the right number for everything except noise. The filter was specified by its
corner, so it is the number written on the schematic. And every other bandwidth in the
project — loop bandwidth, video bandwidth, channel bandwidth — is a $-3$ dB number, so
the habit is reinforced everywhere else it is applied.

What breaks it is that the signal has a band edge and noise does not. Half of the output
noise power of a one-pole filter comes from above its corner, and the arctangent says so
exactly. The cost is $10\log_{10}(\pi/2) = 1.96$ dB of noise power and $25\%$ in r.m.s.
volts — enough to turn a receiver that meets its sensitivity into one that does not, and
small enough that nobody notices it in a review.

The companion mistake is the one the previous section dismantles: reading a small
$B_n/f_{3dB}$ as a quiet filter without asking what the denominator is.

## Where this stops holding

$B_n$ collapses a whole response into one number on the assumption that the noise
reaching the filter is *white*. It is not, below the flicker corner of module 2: there
the density is $S_{th}(1 + f_c/f)$ and the output mean square is
$S_{th}\left[B_n + f_c\!\int|H|^2\,df/f\right]$, whose second term the noise bandwidth
knows nothing about. For a baseband channel with a low corner this matters; for the
capstone's $15.6$ MHz anti-alias filter it does not.

$k_BT/C$ assumes the sampling switch is on long enough for the node to reach equilibrium
— a few time constants — and that the switch resistance is linear over the signal swing.
Sample faster than that and the stored noise is less than $k_BT/C$, but so is the settled
signal, and the ratio is worse rather than better. It also assumes one sample. Correlated
double sampling takes two and subtracts them, which cancels the low-frequency part of the
noise and, for uncorrelated samples, doubles the thermal part: the result is
$2k_BT/C$ in the white limit and much less than $k_BT/C$ where the noise is slow.

The module's lab, *Noise bandwidth by integration, and kT/C*, closes the loop on all of
this. Its last test computes the sampled noise two ways — once as $\sqrt{k_BT/C}$ and
once the long way, as the resistor's density times $\sqrt{B_n}$ — and demands the two
agree while $R$ is changed by a factor of a hundred. If your answer moves when $R$ moves,
one of the two square roots is in the wrong place.
''',
                },
            ],
            "quiz": {
                "title": "The area under the curve, not the point on it",
                "minutes": 8,
                "questions": [
                    {
                        "q": "For a one-pole low-pass, what fraction of the total output noise power arrives from frequencies above the $-3$ dB corner?",
                        "opts": [
                            "About a tenth, since the response is already down 3 dB there and still falling",
                            "Exactly half: the area is an arctangent, and $\\arctan(1)$ is half of $\\pi/2$",
                            "About a third, which is the $57\\%$ excess expressed as a share of the total",
                            "Almost none, because $|H|^2$ falls at 40 dB per decade above the corner",
                        ],
                        "a": 1,
                        "whys": [
                            r"Being 3 dB down means the density is halved at that one frequency, not that the whole region beyond is negligible — and the region beyond is infinitely wide, which is what makes it add up.",
                            r"$\int_0^{f_0} = f_0\arctan(1) = \pi f_0/4$, against a total of $\pi f_0/2$.",
                            r"The arithmetic behind this is real but misassigned: $B_n$ exceeds $f_{3dB}$ by $57\%$, and $0.5708/1.5708 = 36\%$ is the share of $B_n$ that lies beyond the corner *in excess of the corner's own width*. The share of the noise power is the arctangent, and it is a half.",
                            r"$|H|^2$ does fall at 40 dB per decade, and it is still not enough. The single decade from $f_0$ to $10f_0$ carries $44\%$ of the total power on its own; only above $10f_0$ does the contribution become small, at $6\%$.",
                        ],
                        "why": r'''
$\int_0^{X}|H|^2df = f_0\arctan(X/f_0)$, so the area up to the corner is
$f_0\arctan(1) = \pi f_0/4$ and the total is $\pi f_0/2$. Half the noise power of a
single-pole filter comes from its stop band, and $44\%$ of the total comes from the one
decade immediately above the corner. This is the whole content of $B_n = \frac{\pi}{2}
f_{3dB}$: not a correction factor to be remembered, but a statement that a 20 dB per
decade roll-off is a poor way to stop noise.
''',
                    },
                    {
                        "q": "Butterworth filters of order 1, 2 and 3 have $B_n/f_{3dB}$ of $1.571$, $1.111$ and $1.047$. Can a real filter get below 1?",
                        "opts": [
                            "Yes, once the roll-off is steep enough that the stop band contributes less than the pass band loses",
                            "Yes, but only for an elliptic response, whose stop-band zeros remove the tail entirely",
                            "No: the ratio is $x/\\sin x$ with $x = \\pi/(2n)$, which exceeds 1 at every finite order $n$",
                            "No, because noise bandwidth is defined as an area and an area cannot be smaller than its base",
                        ],
                        "a": 2,
                        "whys": [
                            r"There is nothing to lose in the pass band: $|H|^2$ is at most 1 there for every Butterworth order, and a brick wall of width $f_{3dB}$ is the best that shape can do. A steeper skirt approaches that limit without passing it.",
                            r"Elliptic filters have finite-frequency zeros, but between them the response comes back up to the ripple floor rather than to nothing, and the pass band ripples below 1 as well. The ratio gets close to 1 and stays above it.",
                            r"$\sin x < x$ for every $x > 0$, so the ratio exceeds 1 at every order and tends to 1 as $n$ grows.",
                            r"An area can be anything relative to its base — that is what the peaked two-pole case shows, where $B_n$ comes out well under $f_{3dB}$ because the response rises far above 1 inside the band. The Butterworth bound comes from the pass band being flat at 1, not from geometry.",
                        ],
                        "why": r'''
$B_n/f_{3dB} = (\pi/2n)/\sin(\pi/2n)$, and $\sin x < x$ for all $x>0$, so the ratio is
above 1 for every finite $n$ and approaches 1 from above. Physically: a Butterworth pass
band is flat at unity and its stop band is not zero, so it passes everything a brick wall
of the same corner would pass, and then some. What order buys is the size of that
surplus, and it runs out quickly — the second pole is worth $1.51$ dB of noise power, the
third $0.26$ dB. A ratio below 1 requires a response that peaks *above* its own
normalising gain, which a monotonic filter never does.
''',
                    },
                    {
                        "q": "A two-pole response with $\\zeta = 0.1$ has $B_n = 0.20f_{3dB}$, against $1.11$ for the Butterworth case. Is it the quieter filter?",
                        "opts": [
                            "Yes: it passes a fifth of the noise bandwidth, so a fifth of the noise power",
                            "Yes for narrowband noise and no for wideband, since it is the shape of the tail that differs",
                            "Only if the signal sits at the resonant peak; a baseband signal sees seven times the power",
                            "No: $|H|^2$ peaks at 25 times its d.c. value, so it is 25 times noisier throughout",
                        ],
                        "a": 2,
                        "whys": [
                            r"This reads $B_n$ as though its denominator were fixed. It is not: $B_n$ is an area divided by the peak, and here $|H|^2$ peaks at $25\times$ its d.c. value, so a small ratio is being produced by a large denominator rather than a small area.",
                            r"The distinction between narrowband and wideband noise is not the issue — the input density is flat in both comparisons. What differs is which gain the output noise is being measured against, and that is a property of where the signal is, not of the noise.",
                            r"The raw areas are $7.854f_n$ against $1.111f_n$: the resonant filter passes $8.5$ dB more power for the same d.c. gain.",
                            r"$|H|^2$ does peak at 25 times its d.c. value, but only near $f_n$; at low frequency the two responses are both close to 1, so a blanket factor of 25 overstates it. The correct factor on the integrated power is seven.",
                        ],
                        "why": r'''
$B_n$ divides the area under $|H|^2$ by the response's *peak*, which is the right
normalisation when the signal is also at the peak — a tuned amplifier, for instance. The
raw areas here are $7.854f_n$ for $\zeta = 0.1$ and $1.111f_n$ for $\zeta = 0.7071$, so
for a signal at baseband, where both responses have a gain of 1, the resonant filter
delivers seven times the noise power. Its small $B_n$ comes from a peak the signal never
uses. Any figure of merit with a gain in its denominator is a claim about where the
signal sits.
''',
                    },
                    {
                        "q": "The sampled noise on a capacitor is $\\sqrt{k_BT/C}$, with no resistance in it. What does that say about choosing a lower-resistance sampling switch?",
                        "opts": [
                            "It lowers the noise density, so it lowers the sampled noise in proportion",
                            "It has no effect on the sampled noise: the density falls and the bandwidth rises together",
                            "It raises the sampled noise, because a wider bandwidth admits more of the spectrum",
                            "It lowers the sampled noise only until the switch resistance is below the source resistance",
                        ],
                        "a": 1,
                        "whys": [
                            r"The density does fall, as $\sqrt{R}$ — and the noise bandwidth $1/(4RC)$ rises as $1/R$ at the same time. Mean square is density squared times bandwidth, so $4k_BTR \times 1/(4RC)$ leaves $k_BT/C$ with the $R$ gone.",
                            r"$4k_BTR$ falls as $R$ and $1/(4RC)$ rises as $1/R$; the product has no $R$ left in it.",
                            r"Half right and it lands on the wrong side. The bandwidth does rise as $R$ falls, but the density falls by exactly the compensating factor, so the sampled noise is unchanged rather than worse. A smaller switch does settle faster, which is the reason to want one.",
                            r"There is no such threshold. The cancellation is exact for every value of $R$, which is why $k_BT/C$ is quoted as a property of the capacitor and never of the switch that charges it.",
                        ],
                        "why": r'''
A smaller switch resistance lowers the density as $\sqrt{R}$ and raises the noise
bandwidth as $1/R$, and the two effects cancel exactly:
$4k_BTR \times 1/(4RC) = k_BT/C$. This is why the sampled noise is a specification of the
capacitor alone. A lower-resistance switch is still worth having — it settles faster and
distorts less — but it buys no noise at all, and the lab's last test changes $R$ by a
factor of a hundred and requires the answer not to move.
''',
                    },
                    {
                        "q": "A sample-and-hold must have its $k_BT/C$ noise halved. What does that cost, and why?",
                        "opts": [
                            "Twice the capacitance, since noise voltage and capacitance are inversely related",
                            "Four times the capacitance: the mean square goes as $1/C$, and volts are its root",
                            "Four times the capacitance and four times the area, because $C$ scales with area",
                            "Twice the capacitance and twice the current, so that the settling time is preserved",
                        ],
                        "a": 1,
                        "whys": [
                            r"This treats $\sqrt{k_BT/C}$ as though it were $k_BT/C$. The mean square is inversely proportional to $C$; the r.m.s. voltage goes as $1/\sqrt{C}$, so halving it needs a factor of four.",
                            r"$\overline{v^2} = k_BT/C$, so a quarter of the mean square is half the r.m.s., and that is $4C$.",
                            r"The capacitance factor is right and the reasoning attached to it is not: capacitor area is a consequence of the required $C$, not a second independent cost, and the expensive part of the four times is the current needed to drive it at the same speed.",
                            r"Two errors that partly hide each other. The capacitance factor is four rather than two, and the current then follows the capacitance — at a fixed $g_m/I_D$ that is four times the current, not two.",
                        ],
                        "why": r'''
$\overline{v^2} = k_BT/C$, so halving the r.m.s. voltage means quartering the mean square,
which means four times the capacitance. That factor of four then propagates: settling the
larger capacitor in the same time needs four times the transconductance, and at a fixed
$g_m/I_D$ that is four times the current. Each further factor of two in noise costs four
in capacitance and four in power, which is the quadratic wall that makes precision
converters expensive — and why an extra two bits of resolution costs sixteen times the
sampling capacitor, taking a 1 V converter from $0.81$ pF at twelve bits to $12.9$ pF at
fourteen.
''',
                    },
                    {
                        "q": "A noise budget was computed over the anti-alias filter's $9.947$ MHz corner instead of its $15.625$ MHz noise bandwidth. How wrong is the resulting sensitivity, and in which direction?",
                        "opts": [
                            "Optimistic by $4.0$ dB, since the bandwidth is out by a factor of $\\pi/2$ in volts",
                            "Pessimistic by $1.96$ dB: the corner overstates the noise the filter admits",
                            "Optimistic by $1.96$ dB, which is $10\\log_{10}(\\pi/2)$ and $25\\%$ in r.m.s. volts",
                            "Correct to within a tenth of a decibel, since the tail beyond the corner is attenuated",
                        ],
                        "a": 2,
                        "whys": [
                            r"The $\pi/2$ is a ratio of powers, not of volts: $10\log_{10}(\pi/2) = 1.96$ dB, and the error in r.m.s. volts is $\sqrt{\pi/2} = 1.25$. Reading $\pi/2$ as a voltage ratio doubles the decibels.",
                            r"The direction is inverted. The corner is the *narrower* bandwidth, so budgeting against it counts less noise than the filter really admits and reports a receiver that is better than it is.",
                            r"$B_n/f_{3dB} = \pi/2$, so the power is understated by $1.96$ dB and the r.m.s. by $\sqrt{\pi/2} = 1.25$.",
                            r"The tail is attenuated and still carries half the noise power, which the arctangent gives exactly. Attenuated is not removed, and an infinite band of gently attenuated noise adds to a great deal.",
                        ],
                        "why": r'''
The corner is the narrower number, so the budget counted less noise than the filter
admits: the error is optimistic, which is the dangerous direction. In power it is
$10\log_{10}(\pi/2) = 1.96$ dB, and in r.m.s. volts $\sqrt{\pi/2} = 1.25$, taking
$3.537\ \mu$V to $4.433\ \mu$V and the sensitivity from a claimed $-92.04$ dBm to an
actual $-90.08$ dBm. On this receiver that $1.96$ dB happens to equal the entire cascade
noise figure the front end was designed to achieve, so the arithmetic slip is worth
exactly as much as the LNA.
''',
                    },
                ],
            },
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
