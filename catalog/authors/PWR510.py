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
        "A hard-switched bridge dumps the whole energy stored in its own device "
        "capacitance, half of C times V squared, into the channel on every transition, "
        "and that bill grows with frequency. A resonant "
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
            "read": [
                {
                    "title": "The square wave you drive with, and the sinusoid you get back",
                    "minutes": 14,
                    "body": r'''
Put a differential probe on the midpoint of a 400 V half-bridge and a current probe on
the wire leaving it. The tank is a 60 µH inductor in series with a 33 nF capacitor;
behind it sit a transformer, a full-bridge rectifier and a capacitor holding 48 V across
the load. Run the two gates in complementary halves at 113 kHz and put both traces on
the screen at once.

They do not look like they belong to the same circuit. The voltage is a square: pinned
at 400 V for half a cycle, at 0 V for the other half, transitions a few tens of
nanoseconds wide, nothing interesting in between. The current is a sinusoid. Not roughly
a sinusoid — you can drop a cursor on the peak and find it within a per cent of where a
sine of the same fundamental would put it, cycle after cycle.

The same wire carries both, so nothing was filtered out on the way. Either the drive was
nearly sinusoidal to begin with, or the tank did something to it. The first is easy to
check, and it is false.

## The drive is not remotely a sinusoid

About its own average the midpoint alternates between $+V_{in}/2$ and $-V_{in}/2$, which
here is $\pm 200$ V. A square wave of amplitude $A$ has the Fourier series

$$\frac{4A}{\pi}\left(\sin\theta + \tfrac{1}{3}\sin 3\theta + \tfrac{1}{5}\sin 5\theta + \dots\right)$$

and no even terms at all, because half a period later the waveform is exactly its own
negative. The derive unit *What the first-harmonic approximation replaces the converter
with* starts from this one series and applies it on both sides of the transformer.

With $A = 200$ V the fundamental has a peak of $4A/\pi = 254.6$ V and an RMS of
$\sqrt{2}V_{in}/\pi = 180.06$ V. The square's own RMS is the full 200 V, so the
fundamental holds $(180.06/200)^2 = 0.811$ of the mean square, and that fraction is
$8/\pi^2$ — the same constant that turns up later in $R_{ac} = 8n^2R_L/\pi^2$, and for
the same reason: it is what is left when a square is replaced by its first harmonic.

The other 19 per cent is not rounding. The third harmonic on its own has a peak of
84.9 V. Whatever makes the current sinusoidal, it is not that the drive nearly was.

## What the tank does with them

The tank is linear, so take the harmonics one at a time and superpose. At the $k$th the
series branch has impedance

$$Z(k) = R_{ac} + j\left(k\omega_r L_r - \frac{1}{k\omega_r C_r}\right)
       = R_{ac} + jZ_0\left(k - \frac{1}{k}\right)$$

with $Z_0 = \sqrt{L_r/C_r}$. The bracket vanishes only at $k = 1$: there the inductive
and capacitive reactances cancel exactly and the drive sees nothing but $R_{ac}$. At
every other harmonic the bracket is not small — $k - 1/k$ is $8/3$ at the third and
$4.8$ at the fifth — and it is multiplied by $Z_0$, which for a 60 µH and 33 nF tank is
$42.64\ \Omega$.

Give the converter a real load: 48 V at 13.5 A through a transformer with
$n = V_{in}/(2V_o) = 4.167$, so $R_L = 3.556\ \Omega$ and $R_{ac} = 50.0\ \Omega$. The
loaded quality factor is then $Q = Z_0/R_{ac} = 0.852$, and the rest is arithmetic.

```python
import math

V_in = 400.0        # bus, volts
V_out = 48.0        # output, volts
L_r = 60e-6         # resonant inductor, henries
C_r = 33e-9         # resonant capacitor, farads
n = V_in / (2.0 * V_out)       # turns ratio that puts unity gain at resonance
R_L = 3.5556                   # load resistance: 48 V at 13.5 A
R_ac = 8.0 * n * n * R_L / math.pi ** 2

f_r = 1.0 / (2.0 * math.pi * math.sqrt(L_r * C_r))
Z_0 = math.sqrt(L_r / C_r)
Q = Z_0 / R_ac
print("f_r %.1f kHz   Z_0 %.2f ohm   n %.3f   R_ac %.1f ohm   Q %.3f"
      % (f_r / 1e3, Z_0, n, R_ac, Q))

V1 = 2.0 * V_in / math.pi       # peak of the driving fundamental, volts
I1 = V1 / R_ac                  # at resonance the tank is nothing but R_ac
harm = 0.0
for k in (1, 3, 5, 7, 9, 11, 13):
    Zk = math.hypot(R_ac, Z_0 * (k - 1.0 / k))
    Ik = (V1 / k) / Zk
    if k > 1:
        harm += (Ik / I1) ** 2
    print("h%-3d drive %6.1f V   |Z| %6.1f ohm   %5.3f A   %5.2f%% of h1"
          % (k, V1 / k, Zk, Ik, 100.0 * Ik / I1))
print("distortion: %.1f%% of the current, %.1f%% of the power"
      % (100.0 * math.sqrt(harm), 100.0 * harm))
print("delivering %.0f W at %.1f A dc" % (0.5 * V1 * I1, 2.0 * n * I1 / math.pi))
```

It prints a 113.1 kHz resonance, a 5.089 A fundamental, and a third harmonic of 0.683 A
— 13.4 per cent of the fundamental. The fifth is 4.75 per cent, the seventh 2.41 per
cent, and the sum in quadrature of everything above the first comes to 14.6 per cent of
the fundamental current. The last line confirms the operating point is real: 648 W out
at 13.5 A of dc output current, which is what a fundamental of 5.089 A peak delivers
through a 4.167:1 transformer and a full-bridge rectifier.

## Thirteen per cent of the current, two per cent of the power

Fourteen per cent distortion is not nothing, and it is much more than the eye finds in
that current trace. Look at the last line of the loop again, though: the harmonic
*power* is 2.1 per cent, because power goes as the square of the current and
$0.134^2 = 0.018$.

That is the real justification for keeping only the fundamental, and it is worth stating
in the form that survives scrutiny. The claim is not that the harmonics are absent — the
tank passes $1/\sqrt{1 + Q^2(k - 1/k)^2}$, which at $Q = 0.852$ and $k = 3$ is $0.403$,
so 40 per cent of the third harmonic gets through. The claim is that what does get
through carries a couple of per cent of the power and averages to almost nothing at the
rectifier, so a model that tracks power flow — which is what a gain curve is — is
accurate to a few per cent while being wrong about the waveform by fifteen.

## The mistake, and why it is tempting

The usual story is that a resonant tank is a sharp filter, so the harmonics are rejected
and only the fundamental survives. It is a satisfying picture and it is the wrong one.
At the $Q$ a converter actually runs — $0.85$ here, $0.4$ at the capstone's full load —
the tank is a mediocre filter. The capstone tank passes $0.63$ of what it is given at
three times resonance. A tank sharp enough to genuinely reject the third harmonic would
need a $Q$ of ten or more, which is $Z_0 = 10R_{ac}$ — and at resonance the current is
$V_1/R_{ac}$, so the inductor and the capacitor would each stand $QV_1$, ten times the
voltage appearing across the load. Every component in the tank has to be rated for it and
the magnetics grow to match. Worse, $Q$ is set by the load rather than chosen: a tank at
$Q = 10$ at full load sits at $Q = 1$ at a tenth of the load, so the selectivity you paid
for evaporates at exactly the operating point where the harmonics are largest.

The picture is tempting because it explains the trace on the screen, and because filter
courses teach $Q$ as selectivity. In a converter $Q$ is a *load* variable — the sandbox
*Reading a tank off a Bode plot* makes that concrete, since its damping slider
$\zeta = 1/(2Q) = R_{ac}/(2Z_0)$ is nothing but the load resistance in disguise. The
harmonics are attenuated somewhat and detuned a lot, and squaring 0.134 does the rest.

## Where it stops holding

The approximation degrades exactly where the tank stops detuning: at low $Q$, which is
light load.

```python
import math

for Q in (0.853, 0.4, 0.1):
    third = (1.0 / 3.0) / math.sqrt(1.0 + (Q * (3.0 - 1.0 / 3.0)) ** 2)
    print("Q = %.3f  ->  third harmonic %4.1f%% of the fundamental" % (Q, 100.0 * third))
```

At $Q = 0.853$ the third harmonic is 13.4 per cent of the fundamental, at $Q = 0.4$ it
is 22.8 per cent, and at $Q = 0.1$ it is 32.2 per cent. Follow that limit to its end: as
$Q \to 0$ the reactances stop mattering beside $R_{ac}$, every harmonic passes at its
full drive amplitude, and the tank current becomes the square wave divided by $R_{ac}$.
There is nothing sinusoidal left to approximate. This is the opposite of the intuition a
filter course leaves you with, and it is the reason a converter that regulates well at
full load can behave in ways the model did not predict when the load is removed.

The second boundary is the one that catches designs. Well below resonance the rectifier
stops conducting continuously: the tank current falls to zero for part of each half
cycle, the diodes go out of conduction, and the assumption that the rectifier presents a
square voltage in phase with the current — the assumption the whole $8n^2R_L/\pi^2$
substitution rests on — is no longer true. First-harmonic analysis is at its best within
roughly twenty per cent of resonance under moderate to heavy load, and it grows
optimistic as you move below the gain peak or unload the converter. Predicted peak gains
of an LLC are routinely 10 to 20 per cent above what a time-domain simulation gives, in
the direction that costs you: the model promises boost you will not have. Every design in
this course therefore carries margin on the boost budget, and the capstone specification
never asks for more than $1.14$.

## What you are about to build

The derive unit turns the Fourier series above into $R_{ac} = 8n^2R_L/\pi^2$ and leaves
the converter as three numbers. The build exercise *The tank the first-harmonic
approximation leaves behind* then asks you to place a real $L_r$ and $C_r$ on the canvas
for $f_r = 100$ kHz and $Q = 3$ into $R_{ac} = 12.57\ \Omega$ — note that $Q = 3$ is far
more selective than the 0.85 traced above, which is why its checks can pin the gain at
$1.2f_r$ to 0.673. The lab *Characterise a series-resonant tank* then writes the six
functions the rest of the course calls, on this same 60 µH and 33 nF tank, and its last
test sweeps $x$ from 0.3 to 3.0 to prove what the algebra already implies: the gain never
exceeds one. That is the wall module 2 goes looking for a way around.
''',
                },
            ],
            "quiz": {
                "title": "One harmonic, and what happened to the rest",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The bridge drives the tank with a third harmonic a third the size of the fundamental, yet the tank current looks sinusoidal on a scope. What is doing the work?",
                        "opts": [
                            "Away from resonance the two reactances stop cancelling, so the branch impedance grows",
                            "The output capacitor shunts the harmonics away before they ever reach the resonant branch",
                            "A square wave of exactly 50 per cent duty ratio carries no third harmonic at all",
                            "The rectifier diodes commutate too slowly to follow anything above the fundamental",
                        ],
                        "a": 0,
                        "why": r'''
At the fundamental the inductive and capacitive reactances cancel and the drive sees only
$R_{ac} = 50\ \Omega$; at the third the bracket $Z_0(k - 1/k)$ is $113.7\ \Omega$ and the
magnitude climbs to $124\ \Omega$. A drive three times smaller into an impedance two and a
half times larger is 13 per cent of the current, and squaring that is why the harmonic
power is only 2 per cent. The output capacitor is on the far side of the rectifier and
cannot reach the resonant branch. A 50 per cent square has no *even* harmonics, but its
odd ones are exactly the $1/k$ series this module opens with. And diode commutation is
fast enough to be modelled as instantaneous here — it is the tank impedance, not the
rectifier, that shapes the current.
''',
                    },
                    {
                        "q": "Why does the tank see $8n^2R_L/\\pi^2$ rather than the $n^2R_L$ a transformer alone would give?",
                        "opts": [
                            "Matching the power a sinusoid delivers to what the dc load draws costs that factor",
                            "The transformer's leakage inductance drops part of the voltage ahead of the rectifier bridge",
                            "It is the attenuation the output capacitor gives at twice the switching frequency",
                            "Two rectifier devices conduct at once, so their forward drops halve the resistance",
                        ],
                        "a": 0,
                        "why": r'''
The substitution is a power-equivalence, not a circuit identity. The rectifier presents a
square voltage of $\pm V_o$ whose fundamental peaks at $4V_o/\pi$, while the sinusoidal
current of peak $I_p$ averages to $2I_p/\pi$ through the diodes; the ratio of those two
fundamentals is $8/\pi^2 \approx 0.811$ times $V_o/I_o$, and the $n^2$ is the ordinary
referral on top. Leakage inductance is real but it belongs in $L_r$, not in the load
term. The output capacitor changes the ripple, not the equivalent resistance. Forward
drops are a loss term for module 4 and do not scale the resistance the tank sees.
''',
                    },
                    {
                        "q": "The first-harmonic approximation is at its worst at light load. What is the mechanism?",
                        "opts": [
                            "Light load is small $Q$, and a low-$Q$ tank barely detunes the harmonics at all",
                            "Light load is large $Q$, and a sharper tank rings on harmonics it was never driven at",
                            "Light load raises the switching frequency until every harmonic is above resonance",
                            "Light load lets the diode forward drop dominate, so no tank current is defined",
                        ],
                        "a": 0,
                        "why": r'''
$Q = Z_0/R_{ac}$, and a lighter load is a *larger* $R_{ac}$, so $Q$ falls. The harmonic
attenuation $1/\sqrt{1 + Q^2(k-1/k)^2}$ then tends to 1 for every $k$: at $Q = 0.1$ the
third harmonic is already 32 per cent of the fundamental, and in the limit the tank
current is the square wave over $R_{ac}$. Reading $Q$ as selectivity gets the direction
exactly backwards, which is the tempting error here. Frequency does rise at light load in
a real controller, but that is the loop responding, not the mechanism. And the diode drop
matters to efficiency, not to whether the current is a sinusoid.
''',
                    },
                    {
                        "q": "The third harmonic reaches 13 per cent of the tank current. What share of the power does it carry?",
                        "opts": [
                            "Roughly 2 per cent, since dissipation follows the square of the current",
                            "Roughly 13 per cent, the same share, because it meets the same $R_{ac}$",
                            "Roughly 4 per cent, a third of the current share, in the ratio of harmonic numbers",
                            "None whatever, because current at a harmonic frequency is purely reactive",
                        ],
                        "a": 0,
                        "why": r'''
$0.134^2 = 0.018$, and adding the fifth, seventh and the rest in quadrature brings the
total above the fundamental to 2.1 per cent. That squaring is the whole reason a model
that is 15 per cent wrong about the waveform is 2 per cent wrong about the power. Meeting
the same $R_{ac}$ is true and is not the point: $P = \tfrac{1}{2}I^2R_{ac}$ still squares
the current. Scaling the share by $1/k$ confuses the drive amplitude with the power it
carries. And the harmonic current is emphatically not reactive — it flows through
$R_{ac}$ and dissipates there, which is exactly why it can be counted this way.
''',
                    },
                    {
                        "q": "You have an LLC gain curve computed by first-harmonic analysis. Where should you trust it least?",
                        "opts": [
                            "At the peak, below resonance and lightly loaded, where the rectifier goes discontinuous",
                            "Exactly at resonance, where the cancelling reactances make the expression degenerate",
                            "Above resonance at full load, where the current lags the bridge voltage and the $Q$ is highest",
                            "At high line, because the derivation assumed a fixed input voltage throughout",
                        ],
                        "a": 0,
                        "why": r'''
Below resonance the tank current can fall to zero before the half cycle ends, the diodes
stop conducting continuously, and the equivalent resistance the whole substitution rests
on no longer describes the rectifier. Predicted peak gains come out 10 to 20 per cent
optimistic there, which is the direction that costs you a design. Resonance is where the
model is at its best, not its worst — the reactances cancelling is what makes the gain
exactly 1. Above resonance at full load is the well-behaved region the controller is
steered into deliberately. And nothing in the derivation fixes $V_{in}$: it enters only
as a scale factor on the drive.
''',
                    },
                    {
                        "q": "The build exercise asks for $f_r = 100$ kHz and $Q = 3$ into $R_{ac} = 12.57\\ \\Omega$. What do those two specifications pin down first?",
                        "opts": [
                            "$Z_0 = QR_{ac} = 37.7\\ \\Omega$, which $f_r$ then splits into $L_r$ and $C_r$",
                            "$L_r$, which follows from the resonant frequency by itself once $Q$ is known",
                            "$C_r$, since the capacitor sets the resonance and $Q$ merely trims the shape",
                            "Neither: two specifications cannot fix two components without a third constraint",
                        ],
                        "a": 0,
                        "why": r'''
The two tank numbers are $\sqrt{L_rC_r} = 1/(2\pi f_r)$ and $\sqrt{L_r/C_r} = Z_0 = QR_{ac}$,
which is $3 \times 12.57 = 37.7\ \Omega$. Multiply them for $L_r = 60\ \mu$H, divide for
$C_r = 42.2$ nF. Neither component is fixed on its own by either specification: $f_r$
constrains only the product and $Q$ only the ratio, which is why naming $L_r$ or $C_r$
first has nothing to compute from. Two equations in two unknowns is exactly enough here,
so no third constraint is wanted — what makes it work is that the equations are in the
product and the ratio rather than in the components themselves.
''',
                    },
                ],
            },
            "title": "The tank, and the one harmonic that matters",
            "summary": "A square wave drives the bridge, but a selective tank only responds to its fundamental. That single approximation turns a switching circuit into a phasor problem.",
            "concepts": [
                "The half-bridge output is a square wave between the rails; its fundamental has peak amplitude $2V_{in}/\\pi$ and no even harmonics at all.",
                "The tank is a filter, but a soft one at converter loads: the capstone tank ($L_n = 5$, $Q = 0.4$) still passes $0.63$ at $3f_r$ against $1$ at $f_r$, and the drive's third harmonic starts at a third of the fundamental, so it survives at about a fifth of it. Keeping only the fundamental is a working approximation, not a rigorous one.",
                "The rectifier and its output capacitor are replaced by an equivalent resistance $R_{ac} = 8n^2R_L/\\pi^2$, chosen so the fundamental sees the same power flow.",
                "The tank has two numbers: $\\omega_r = 1/\\sqrt{L_rC_r}$ and $Z_0 = \\sqrt{L_r/C_r}$. Load enters only through $Q = Z_0/R_{ac}$.",
                "First-harmonic approximation is at its worst far from resonance and at *light* load, because light load is small $Q$: at $Q = 0.85$ the third harmonic is $13$ per cent of the fundamental in the tank current, at $Q = 0.1$ it is $32$ per cent, and by $Q \\to 0$ the current has stopped being a sinusoid and is following the square wave.",
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

So the damping slider is the load, and it runs the way round you may not expect:
$\zeta = 1/(2Q) = R_{ac}/(2Z_0)$, so more damping is a *larger* $R_{ac}$, which is a
*lighter* load. It opens at $\zeta = 0.1$, which is $Q = 5$ and $R_{ac} = Z_0/5$: a
heavily loaded tank.
''',
                "notice": [
                    "The amber dot marks the gain at the corner, and it always reads $K/(2\\zeta)$ — which is $QK$. At the opening $\\zeta = 0.1$ that is $5$, or $14.0$ dB. So the capacitor voltage is $Q$ times the driving fundamental at resonance. That resonant rise is the only place a tank's boost can come from — a series-resonant converter never gets at it, because it takes its output across the load rather than across a reactance, but an LLC takes its output across $L_m$ and does.",
                    "Drag $\\zeta$ up to $0.8$. The peak is gone entirely, and the amber dot has fallen to $-4.1$ dB, below the dashed 0 dB line. Above $\\zeta = 0.707$ the magnitude falls monotonically from DC, so this tank — which is at $Q = 0.625$, a *lighter* load than the opening — has no resonant rise at all. In a series-loaded tank the load resistance is the damping, so it is light load that flattens the peak, not heavy.",
                    "Watch the low-frequency end while you sweep $\\zeta$. It does not move: every curve in the family leaves the same $20\\log_{10}K$ asymptote. Frequency control has no authority down there: whatever the damping, the curve has already settled onto $K$ long before the axis runs out.",
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
                        "hint": "The series has $4A/\\pi$ in front of the fundamental sine. Substitute the half-rail amplitude.",
                        "deconstruct": [
                            "The fundamental term is $(4A/\\pi)\\sin\\theta$, so its peak is $4A/\\pi$.",
                            "With $A = V_{in}/2$ that is $4V_{in}/(2\\pi)$.",
                        ],
                    },
                    {
                        "prompt": "The tank sees a sinusoid, so what matters for power is its RMS value. Write the RMS of that fundamental.",
                        "answer": "\\frac{\\sqrt{2} V_{in}}{\\pi}",
                        "hint": "Divide a peak by $\\sqrt{2}$ to get the RMS of a sinusoid.",
                        "deconstruct": [
                            "RMS of a sinusoid is peak over $\\sqrt{2}$.",
                            "$\\frac{2V_{in}}{\\pi\\sqrt{2}}$ is the same number written with the root on the other side.",
                        ],
                    },
                    {
                        "prompt": "Now the output side. The tank current arriving at the rectifier is a sinusoid of peak $I_p$, and the rectifier passes its magnitude to the load. The average of a full-wave rectified sinusoid is $2I_p/\\pi$, and that average is the DC output current $I_o$. Write $I_p$ in terms of $I_o$.",
                        "answer": "\\frac{\\pi I_o}{2}",
                        "hint": "Set $2I_p/\\pi = I_o$ and solve for $I_p$.",
                        "deconstruct": [
                            "The capacitor holds the output voltage, so all the rectified current goes to the load on average.",
                            "Rearranging $I_o = 2I_p/\\pi$ gives $I_p$.",
                        ],
                    },
                    {
                        "prompt": "Because the output capacitor holds $V_o$ steady and the diodes commutate with the current, the voltage the tank sees at the rectifier input is itself a square wave alternating between $+V_o$ and $-V_o$. Write the peak amplitude of its fundamental.",
                        "answer": "\\frac{4 V_o}{\\pi}",
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
stops filtering — deep into discontinuous conduction, or at very low $Q$, where
$R_{ac}$ swamps the reactance, the current follows the square drive rather than a
sinusoid, and the third harmonic is no longer negligible. Every gain curve in this course is accurate to a few per cent near
resonance and worth checking against a simulation anywhere else.
''',
            },
            "build": {
                "title": "The tank the first-harmonic approximation leaves behind",
                "minutes": 26,
                "brief": r"""
Strip the first-harmonic approximation of everything it replaces and this is what is
left: a sinusoidal source, a series $L$ and $C$, and a resistor standing in for the
rectifier and the load. It is an ordinary linear circuit, which is the entire point —
that is what the approximation was *for*.

## What is on the canvas

The 1 V source is the fundamental of the half-bridge square wave. The 12.57 Ω resistor
is $R_{ac}$, the equivalent resistance the rectifier and load present to the tank.

## What to add

The resonant inductor and the resonant capacitor, in series between the source and the
load, sized for

$$f_r = 100\ \text{kHz}, \qquad Q = 3$$

Two specifications, two components. From
$$f_r = \frac{1}{2\pi\sqrt{L_rC_r}}, \qquad Q = \frac{1}{R_{ac}}\sqrt{\frac{L_r}{C_r}}$$
you get $\sqrt{L_rC_r}$ from the first and $\sqrt{L_r/C_r}$ from the second, and
multiplying and dividing those two recovers $L_r$ and $C_r$ separately. Put the probe
on the load.

## What the checks measure

- **At resonance the tank disappears.** The inductive and capacitive reactances are
  equal and opposite, they cancel exactly, and the source sees only $R_{ac}$ — so the
  gain is 1. That is why a series-resonant converter run at $f_r$ has unity gain
  whatever $Q$ is, and it is the fixed point every gain curve in this course passes
  through.
- **Off resonance, $Q$ decides how fast it falls.** At $1.2f_r$ the gain must be
  $1/\sqrt{1 + Q^2(x - 1/x)^2} = 0.673$. That single number pins $Q$, and with $f_r$
  already fixed it pins both components.
- **It can only buck.** The gain never exceeds 1 at any frequency. This is the whole
  reason the LLC of the next module exists: one extra inductor buys gains above unity
  and a converter that still regulates at light load.
- **Below resonance the current leads.** The tank is net capacitive there, which is
  the region a designer avoids, because leading current is the opposite of what zero-
  voltage switching needs.
""",
                "start": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "rac", "kind": "R", "x": 14, "y": 7, "rot": 1, "value": 12.57},
                        {"id": "g1", "kind": "GND", "x": 14, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 14, "y": 5},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]},
                        {"a": [14, 5], "b": [14, 6]},
                        {"a": [14, 8], "b": [14, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "lr", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 60.0e-6},
                        {"id": "cr", "kind": "C", "x": 10, "y": 5, "rot": 0, "value": 42.2e-9},
                        {"id": "rac", "kind": "R", "x": 14, "y": 7, "rot": 1, "value": 12.57},
                        {"id": "g1", "kind": "GND", "x": 14, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 14, "y": 5},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]},
                        {"a": [2, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [14, 5]},
                        {"a": [14, 5], "b": [14, 6]},
                        {"a": [14, 8], "b": [14, 9]},
                    ],
                },
                "checks": [
                    {
                        "name": "one L and one C, in series with the load",
                        "code": r"""
c.assert(c.count('L') === 1, 'One resonant inductor; there are ' + c.count('L') + '.');
c.assert(c.count('C') === 1, 'One resonant capacitor; there are ' + c.count('C') + '.');
c.assert(c.vout() < 0.01,
  'At DC the series capacitor blocks everything, so the load should sit at 0 V. It ' +
  'reads ' + c.fmt(c.vout(), 'V') + ', which means there is a DC path around the ' +
  'capacitor — the two components are probably in parallel rather than in series.');
""",
                    },
                    {
                        "name": "unity gain at 100 kHz, where the reactances cancel",
                        "code": r"""
c.close(c.gain(100e3), 1.0, 0.04,
  'the gain at the resonant frequency. There the inductor and the capacitor cancel ' +
  'exactly and the source sees only R_ac, so all of it appears across the load. A ' +
  'gain below 1 here means the resonance is not at 100 kHz — check sqrt(L*C)');
""",
                    },
                    {
                        "name": "Q = 3: the gain at 120 kHz is 0.673",
                        "code": r"""
c.close(c.gain(120e3), 0.6727, 0.06,
  'the gain at 1.2 times resonance. With M = 1/sqrt(1 + Q^2 (x - 1/x)^2) this is 0.673 ' +
  'for Q = 3. A gain closer to 1 means Q is too low — the tank is not selective ' +
  'enough; a much smaller one means Q is too high');
c.close(c.gain(80e3), 0.5952, 0.07,
  'the same test below resonance, at 0.8 f_r. The curve is not symmetric in frequency ' +
  'and this side falls faster, which is worth seeing once');
""",
                    },
                    {
                        "name": "it can only buck — and below resonance the current leads",
                        "code": r"""
[40e3, 70e3, 100e3, 130e3, 200e3, 400e3].forEach(function (f) {
  const g = c.gain(f);
  c.assert(g <= 1.02,
    'The gain reaches ' + g.toFixed(3) + ' at ' + c.fmt(f, 'Hz') + '. A series-resonant ' +
    'tank driven into a resistive load cannot exceed unity at any frequency — if it ' +
    'does, the load is not across the resistor or the components are not in series.');
});
c.assert(c.phase(80e3) > 5,
  'Below resonance the tank is net capacitive and the load voltage should lead the ' +
  'source. The phase reads ' + c.phase(80e3).toFixed(1) + ' degrees. This is the ' +
  'region a designer stays out of, because leading current is exactly what ' +
  'zero-voltage switching cannot use.');
""",
                    },
                ],
                "hints": [
                    "$\\sqrt{L_rC_r} = 1/(2\\pi f_r)$ and $\\sqrt{L_r/C_r} = QR_{ac}$. Multiply the two to get $L_r$; divide to get $C_r$.",
                    "$QR_{ac} = 3 \\times 12.57 = 37.7\\ \\Omega$ — the tank's own characteristic impedance, and a number worth recognising on sight.",
                    "Series means the load current flows through both of them. If either one has a wire to ground on both sides, it is in parallel and the DC check will say so.",
                ],
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
    f"Q = Z0/Rac should be 0.852803, got {_q} — a heavier load is a smaller Rac and so a larger Q"
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
            "read": [
                {
                    "title": "The ceiling at unity, and the one inductor that breaks it",
                    "minutes": 15,
                    "body": r'''
Take the series-resonant converter of module 1 and put it behind a mains rectifier and a
bulk capacitor, which is where converters like it actually live. The specification says
the output must hold through a 20 ms dropout — one missing mains cycle — and during that
20 ms nothing is charging the bulk capacitor, so the 400 V bus decays. By the end of it
the bridge is running from 350 V.

Watch the output on a scope while the mains is interrupted. The bus falls, the controller
sweeps the switching frequency down towards resonance looking for more gain, reaches
resonance, and stops. The output has gone from 48 V to 42 V and it stays there until the
mains returns. The loop is not broken and the controller is not misbehaving; it swept its
lever to the end of its travel and the gain it wanted was not there.

## The ceiling is structural, not a limit of the algebra

The derive unit *The series-resonant gain, and inverting it* ends with
$M = 1/\sqrt{1 + Q^2(x - 1/x)^2}$ and the observation that $M \le 1$. It is worth seeing
why before the algebra, because the algebraic reason — the denominator is a root of one
plus something non-negative — explains nothing you could have used at the whiteboard.

The circuit reason is this. The tank is a series reactance $jZ_0(x - 1/x)$ feeding a
resistor $R_{ac}$, and the output is taken across the resistor:

$$M = \frac{R_{ac}}{\left|R_{ac} + jZ_0\left(x - \frac{1}{x}\right)\right|}$$

The numerator is one of the two legs of a right triangle whose hypotenuse is the
denominator. A leg is never longer than the hypotenuse. That is the whole ceiling, and it
survives any amount of $Q$ or clever frequency control, because it is a statement about
where the probe is: **across the resistor**.

The sandbox *Reading a tank off a Bode plot* shows what is being given up. Its amber
corner marker reads $K/(2\zeta) = Q$ — the resonant rise, a real voltage magnification of
$Q$ at the resonant frequency. That rise exists in a series tank, but it appears across
the inductor and across the capacitor, in equal and opposite amounts that cancel to
nothing across the pair. A series-resonant converter puts its output where the rise is
not.

## Move the probe onto a reactance

So take the output across a reactance instead. Put an inductance $L_m$ in parallel with
$R_{ac}$ and probe that parallel combination. The divider is now

$$M = \left|\frac{Z_p}{Z_p + Z_s}\right|, \qquad
Z_s = jZ_0\left(x - \frac{1}{x}\right), \qquad
Z_p = \frac{j\omega L_m R_{ac}}{R_{ac} + j\omega L_m}$$

and the ceiling argument no longer applies, for a reason you can read straight off the
expression. $Z_p$ has a positive imaginary part, because it is a lossy inductor. Below
resonance $Z_s$ has a *negative* imaginary part. So in the sum $Z_p + Z_s$ the two
imaginary parts subtract, the denominator can be smaller than the numerator, and $M$
exceeds one. Boost in an LLC is not a resonance trick layered on top of the divider; it
is one reactance partly cancelling another inside the denominator of the same divider
that used to be bounded.

In an offline supply $L_m$ costs nothing, because it is the transformer's own magnetising
inductance. It was always there. What changes is that it stops being a parasitic to be
minimised and becomes a component with a value in the specification — and, as module 3
will show, a hard upper bound.

Grinding the divider into normalised form gives, with $L_n = L_m/L_r$,

$$M(x) = \frac{L_n x^2}{\sqrt{\left((L_n+1)x^2 - 1\right)^2 + \left(QL_nx(x^2-1)\right)^2}}$$

which is the formula the lab *Draw the LLC gain family* asks you to write. It is worth
one check against the circuit it came from rather than trusting the transcription.

```python
import math

V_in, V_out, I_out = 400.0, 12.0, 20.0     # nominal bus, output, full load
f_r, Ln, Q = 100e3, 5.0, 0.4               # the specification

n = V_in / (2.0 * V_out)                   # unity gain at resonance sets this
R_ac = 8.0 * n * n * (V_out / I_out) / math.pi ** 2
Z_0 = Q * R_ac
w_r = 2.0 * math.pi * f_r
L_r, C_r = Z_0 / w_r, 1.0 / (Z_0 * w_r)
L_m = Ln * L_r
print("n = %.3f   R_ac = %.1f ohm   Z_0 = %.1f ohm" % (n, R_ac, Z_0))
print("L_r = %.1f uH   C_r = %.2f nF   L_m = %.0f uH" % (L_r * 1e6, C_r * 1e9, L_m * 1e6))

# The closed form, checked against the divider it came from.
def from_components(x):
    w = x * w_r
    Z_s = 1j * w * L_r + 1.0 / (1j * w * C_r)
    Z_m = 1j * w * L_m
    Z_p = Z_m * R_ac / (Z_m + R_ac)
    return abs(Z_p / (Z_p + Z_s))

def closed_form(x, Ln=Ln, Q=Q):
    a = (Ln + 1.0) * x * x - 1.0
    b = Q * Ln * x * (x * x - 1.0)
    return Ln * x * x / math.hypot(a, b)

for x in (0.60, 0.85, 1.00, 1.20, 1.60):
    print("x = %.2f   components %.6f   formula %.6f" % (x, from_components(x), closed_form(x)))
```

It prints $n = 16.667$, $R_{ac} = 135.1\ \Omega$, $Z_0 = 54.0\ \Omega$, and a tank of
$L_r = 86.0\ \mu$H, $C_r = 29.45$ nF, $L_m = 430\ \mu$H. Those are the capstone's numbers,
and the 430 µH is the same magnetising inductance the module 3 lab budgets its dead time
around. The five comparison lines agree to all six printed digits — at $x = 0.60$ both
give 1.293852, at $x = 1.20$ both give 0.933533 — so the normalised formula is the
circuit, not a summary of it.

## Why the crossing at $x = 1$ is the design anchor

Look at the divider once more at $x = 1$. There $Z_s = jZ_0(1 - 1) = 0$: the series
branch is a short. The divider is $Z_p/(Z_p + 0)$, which is 1, and nothing about $L_m$,
$R_{ac}$ or the load appears anywhere in that argument. Every curve in the family passes
through exactly unity at resonance, whatever the load.

That single fixed point is what makes LLC design tractable. Put the nominal line at
resonance, demand $M = 1$ there, and the turns ratio follows by inspection: a half-bridge
presents $V_{in}/2$ to the tank and a full-bridge rectifier presents $V_o$ to the
secondary, so $n = V_{in}/(2V_o) = 400/24 = 16.667$. The required gain at any other bus
voltage is then $2nV_o/V_{in} = 400/V_{in}$.

```python
import math

f_r, Ln = 100e3, 5.0
V_out, n = 12.0, 16.6667

def gain(x, Q):
    a = (Ln + 1.0) * x * x - 1.0
    b = Q * Ln * x * (x * x - 1.0)
    return Ln * x * x / math.hypot(a, b)

def peak(Q):
    x0 = 1.001 / math.sqrt(1.0 + Ln)
    xs = [x0 + i * (2.0 - x0) / 20000 for i in range(20001)]
    xp = max(xs, key=lambda t: gain(t, Q))
    return xp, gain(xp, Q)

def operating_x(target, Q):
    lo, hi = peak(Q)[0], 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if gain(mid, Q) > target else (lo, mid)
    return 0.5 * (lo + hi)

print("second resonance at %.1f kHz" % (f_r / math.sqrt(1.0 + Ln) / 1e3))
for Q in (0.4, 0.8, 1.5):
    xp, mp = peak(Q)
    print("Q = %.1f   peak gain %.3f at %.1f kHz" % (Q, mp, xp * f_r / 1e3))
for V in (350.0, 400.0, 420.0):
    M = 2.0 * n * V_out / V
    x = operating_x(M, 0.4)
    print("bus %.0f V  needs M = %.3f  ->  %.1f kHz" % (V, M, x * f_r / 1e3))
```

The dropout that started this reading now has an answer. At 350 V the tank must deliver
$M = 1.143$, and it does so at 74.8 kHz; at the 420 V top of the bus it needs 0.952 and
runs at 113.6 kHz. The converter sweeps 74.8 kHz to 113.6 kHz and holds 12 V across the
whole bus range, which the series-resonant version could not do at any frequency.

## The mistake: spending the whole peak

The same run prints a peak gain of 1.388 at 49.3 kHz for $Q = 0.4$. Against a requirement
of 1.143 that reads like 21 per cent of headroom, and the tempting conclusion is that the
design could be pushed — a wider line range, a smaller bulk capacitor, a longer dropout.

Read the other two lines first. At $Q = 0.8$ the peak has fallen to 1.044, and at
$Q = 1.5$ it is 1.010. The boost budget is not a property of the tank; it is a property of
the tank *at a load*, and it collapses as the load gets heavier. A converter asked to
ride out a dropout while also charging an output capacitor, restarting into a discharged
load, or supplying a motor's inrush is at high $Q$ and low line simultaneously, and that
is the corner where the peak has all but disappeared. This is why the low-line, full-load
point is the one that sizes the tank, and why the capstone rubric checks the gain at all
three line voltages rather than at nominal.

There is a second reason not to spend the peak, and it is the one that costs hardware.
The peak is the boundary of the inductive region. To its right the tank current lags the
bridge voltage and module 3's zero-voltage switching works; to its left the tank is
capacitive, the current leads, and the bridge turns on into a conducting body diode with
its reverse recovery still in progress. Half-bridges do not usually survive that. A
controller that chases gain by pushing frequency down does not stop at the peak — past it
the gain *falls* as the frequency falls, so the loop sees too little output, pushes lower
still, and drives itself into the capacitive region. Frequency control below the peak is
positive feedback. The margin between 1.143 and 1.388 is not spare gain to be spent; it
is the distance from a latch-up.

## Where the curve stops being true

Three boundaries, in the order they bite.

Module 1's boundary applies to this whole family: first-harmonic analysis is optimistic
below resonance, and the peak is the most optimistic point on the curve. A measured peak
10 to 20 per cent under 1.388 is unremarkable, which eats most of the headroom the
paragraph above told you not to spend anyway.

At the other end, the family has a floor. As $x \to \infty$ the unloaded gain tends to
$L_n/(1+L_n) = 0.833$, not to zero, so no amount of frequency can push the output below
83 per cent of its resonant value when the load is light. On this 400 V design the
highest bus needs 0.952, comfortably above the floor; on a design whose bus could reach
480 V the requirement would be 0.833 exactly, and the converter would be unregulatable at
no load. That is why light-load burst mode exists, and it is a specification decision
made here, at the gain curve, not a firmware detail added later.

Finally, $L_n$ is a ratio of two inductances, and $L_m$ is a gapped ferrite that drifts
with temperature and falls as the core approaches saturation. A tank designed with no
margin on $L_n$ is a tank whose peak moves in service.

## What you are about to build

The sandbox *How load reshapes a resonant curve* sweeps the damping across the family and
gives you the three things to watch — the low-frequency end, the corner and the tail — and
the warning that the load axis runs the opposite way in the series tank it draws. The
derive unit inverts the series-resonant gain for $Q$, which is the same manoeuvre in an
easier algebra. The lab *Draw the LLC gain family* then asks for five functions: the gain,
the second resonance $1/\sqrt{1+L_n}$ at 40.8 kHz, the $Q \to 0$ envelope, the peak on a
prescribed grid, and the bisection that turns a required gain into a frequency. That last
one is exactly the calculation that produced 74.8 kHz above, and the capstone calls it at
three line voltages without changing a line.
''',
                },
            ],
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
lighter load than the last pass, since $\zeta$ rises with $R_{ac}$. The point of this
pass is not the shape of one curve but the shape of the *family*: what a controller can
and cannot reach by moving frequency alone.

Keep in mind which tank this is. The load sits in series here, so it is the damping,
and the peak grows as the load gets heavier. The LLC gain curve in the concepts above
carries its load in parallel with $L_m$ and does the reverse. What transfers between
them is the shape of the family, not the direction of the load axis.

Sweep $\zeta$ slowly from one end to the other and watch three separate things: the
low-frequency end, the corner, and the high-frequency tail.
''',
                "notice": [
                    "The corner marker traces $K/(2\\zeta)$ as you sweep, which with the opening $K = 1$ is exactly $Q$. Every bit of the load dependence of this tank lives in one number.",
                    "At $\\zeta = 0.05$ the corner marker reads $20.0$ dB and at $\\zeta = 1.5$ it reads $-9.5$ dB. That is a 30 dB swing in the gain available at the corner, across the full span of the slider. The controller is not asked to deliver 30 dB — the capstone only ever needs $0.95$ to $1.14$ — but it does have to hold that narrow output while the curve underneath it moves this far.",
                    "The tail is indistinguishable across the whole decade and a half of it the axis shows above the corner. At ten times the corner the magnitude is $-39.9$ dB for $\\zeta = 0.05$ and $-40.3$ dB for $\\zeta = 1.5$: the $-40$ dB per decade asymptote does not care about damping. Far above resonance you have gain authority but almost no load sensitivity.",
                    "The low-frequency end is the mirror image. Every curve leaves the same flat $20\\log_{10}K$ line, so far below resonance frequency buys you nothing at any load. A series-resonant converter meets the same wall at the other end of its own axis: at no load $Q \\to 0$, its gain sits at 1 for every frequency, and the controller can run the frequency up as far as it likes without pulling the output down. The LLC's extra inductor is the fix, and the next lab draws it.",
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
                        "hint": "An inductor contributes $+\\omega L$ and a capacitor $-1/(\\omega C)$ to the reactance.",
                        "deconstruct": [
                            "$Z_L = j\\omega L_r$ and $Z_C = 1/(j\\omega C_r) = -j/(\\omega C_r)$.",
                            "Adding them and taking the coefficient of $j$ gives the reactance.",
                        ],
                    },
                    {
                        "prompt": "Write the $\\omega_r$ at which that reactance is zero.",
                        "answer": "\\frac{1}{\\sqrt{L_r C_r}}",
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
            "quiz": {
                "title": "Why one inductor turns SRC into LLC",
                "minutes": 7,
                "questions": [
                    {
                        "q": "For the series-resonant gain $M(x) = 1/\\sqrt{1 + Q^2(x - 1/x)^2}$, what is the largest value $M$ can take?",
                        "opts": ["1, reached at $x = 1$", "$Q$, reached at $x = 1$", "Unbounded as $Q$ grows", "$1/Q$"],
                        "a": 0,
                        "why": r"""
The bracket $(x - 1/x)$ is zero only at $x = 1$, and everywhere else it makes the
denominator larger than 1. So the gain peaks at exactly unity, at resonance, whatever
$Q$ is — an SRC can only buck. That single algebraic fact is the reason the topology
cannot hold up its output when the input sags, and the reason the next paragraph of
this module exists.
""",
                    },
                    {
                        "q": "At light load, $Q$ falls towards zero. What happens to the SRC gain curve?",
                        "opts": [
                            "It flattens towards 1 everywhere, so frequency stops controlling the output",
                            "It becomes sharper, so control gets easier",
                            "It inverts",
                            "It is unchanged — $Q$ only affects efficiency",
                        ],
                        "a": 0,
                        "why": r"""
With $Q \to 0$ the $Q^2$ term vanishes and $M \to 1$ at *every* frequency. The
controller's only lever — frequency — stops doing anything, and the converter loses
regulation exactly when the load is lightest. Sweeping frequency to the limit does not
help, which is why unloaded SRCs are notorious for running away to their frequency
clamp.
""",
                    },
                    {
                        "q": "What does LLC add to the series-resonant tank?",
                        "opts": [
                            "A magnetising inductance in parallel with the load",
                            "A second capacitor in series with the load",
                            "A resistor to damp the tank",
                            "A second switching bridge",
                        ],
                        "a": 0,
                        "why": r"""
One inductance across the load — usually not an added component at all, but the
transformer's own magnetising inductance, which was always there and is now being
designed rather than minimised. That is the appeal: the topology gets a second
resonance and gain above unity out of a parasitic it already had.
""",
                    },
                    {
                        "q": "Where does the LLC's ability to exceed unity gain come from?",
                        "opts": [
                            "A second, lower resonance formed by $L_r + L_m$ with $C_r$",
                            "The rectifier's forward drop",
                            "Operating above the series resonance",
                            "The output capacitor",
                        ],
                        "a": 0,
                        "why": r"""
There are two resonances. The upper one, $1/(2\pi\sqrt{L_rC_r})$, is where the tank
behaves like the SRC and the gain is 1. The lower one, $1/(2\pi\sqrt{(L_r+L_m)C_r})$,
appears when the load is light enough that $L_m$ is not shorted out by it, and near it
the gain rises above unity. The converter is *boosting* between the two, which is what
lets it hold the output up through a dropout. Running above the series resonance does
the opposite — that region always bucks.
""",
                    },
                    {
                        "q": "As the LLC's load is removed entirely, where does the gain peak move?",
                        "opts": [
                            "Down towards $1/(2\\pi\\sqrt{(L_r+L_m)C_r})$",
                            "Up towards $1/(2\\pi\\sqrt{L_rC_r})$",
                            "It stays fixed at the series resonance",
                            "It disappears",
                        ],
                        "a": 0,
                        "why": r"""
At no load nothing damps $L_m$, so it is fully in the resonance and the peak sits at the
*lower* frequency, where it is also very tall and very sharp. As load is applied the
reflected resistance progressively shorts $L_m$ out and the peak slides up towards the
series resonance while flattening. That whole family of curves — one per load — is what
the lab draws, and reading a design off it is what LLC design *is*.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "Two hundred nanocoulombs, and the window you have to move them in",
                    "minutes": 15,
                    "body": r'''
Two boards on the bench, built from the same layout, the same 400 V bus, the same 430 µH
magnetising inductance and the same 250 pF devices, both delivering 240 W at 100 kHz. The
only difference is one line in the gate-driver configuration: one board has 300 ns of dead
time between the two gates, the other has 100 ns.

A power analyser reads 247.1 W into the first and 247.8 W into the second for the same
240 W out. Seven hundred milliwatts, bought with nothing but a change of two hundred
nanoseconds in gate timing. Put a differential probe on the drain of the device that is
about to turn on and the reason is on the screen: on the 300 ns board the trace has
reached zero and flattened before the gate rises, and on the 100 ns board the gate rises
with about 170 V still standing on it.

Seven hundred milliwatts is the mild version of this failure. Move the same converter's
operating point a few kilohertz to the wrong side of its gain peak and the device turns on
at the full 400 V, which costs 4.0 W. This reading is about both numbers: where they come
from, and how to know before the board exists which one you are going to get.

## The four watts

Each MOSFET has an output capacitance $C_{oss}$ between drain and source, and while the
device is off with the full rail across it, that capacitance holds

$$E = \tfrac{1}{2}C_{oss}V_{in}^2 = \tfrac{1}{2}\times 250\ \text{pF}\times (400\ \text{V})^2 = 20\ \mu\text{J}$$

When the gate goes high with 400 V still on the drain, the channel becomes a short across
that capacitance. The stored energy has exactly one place to go: it is dissipated in the
channel, in the few nanoseconds the drain takes to collapse. No inductance and no
snubber changes this, because the loss is not in the switching *transition* — it is the
capacitor's own energy, and shorting a charged capacitor dissipates all of it whatever
the path.

A half-bridge does that twice per switching cycle, once in each device, so the average
power is $C_{oss}V_{in}^2f_s = 250\ \text{pF} \times 160{,}000 \times 100\ \text{kHz} =
4.0$ W. That is the second of the two numbers from the opening. Note what it does *not*
contain: the load. A hard-switched bridge burns those four watts delivering 240 W and
burns the same four watts delivering 20 W, and the term grows linearly with frequency,
which is why hard switching puts a ceiling on $f_s$ that no better silicon lifts.

The first number follows from the same expression. If the node has been dragged part of
the way down before the gate rises, only the voltage still standing on the drain gets
dumped, so the loss falls as the square of what is left: $C_{oss}V_{rem}^2f_s$. At 167 V
remaining that is 0.70 W, which is where the seven hundred milliwatts came from.

## Turn it into a charge problem

The alternative is to move the drain voltage to zero *before* the gate rises, using
current from the tank rather than the channel. During the dead time neither device is
conducting, and the bridge midpoint is free to be dragged by whatever current is flowing.

Two capacitances sit on that node: the one in the device turning off, which must charge
from 0 to $V_{in}$, and the one in the device about to turn on, which must discharge from
$V_{in}$ to 0. Each costs $C_{oss}V_{in}$, so the transition needs

$$Q = 2C_{oss}V_{in} = 2 \times 250\ \text{pF} \times 400\ \text{V} = 200\ \text{nC}$$

The derive unit *Sizing the magnetising inductance for ZVS* walks this same budget, and
the blanks exercise *The charge budget that ZVS really is* makes you assemble it line by
line. It is worth being exact about which capacitance goes in here: anything else across
the bridge midpoint adds to $Q$. A snubber capacitor fitted to slow the edge and quieten
the board makes zero-voltage switching *harder*, not easier, because it enlarges the
charge the tank has to move in the same window.

## The current that has to move it

At the instant one device stops conducting, what is flowing in the primary? At resonance
the primary current is the load-carrying sinusoid plus the triangular magnetising
current, and the sinusoid is in phase with the bridge voltage — so at the end of a half
cycle it passes through zero. All that is left is the magnetising current, and it is at
its peak exactly then. That is the coincidence the topology is built on: the current
available for the transition is at a maximum at the moment the transition happens, and it
does not shrink when the load is removed, because it never depended on the load.

Across $L_m$ sits $V_{in}/2$ for each half period $T_s/2$, so the current ramps by
$(V_{in}/2)(T_s/2)/L_m$ peak to peak, and the triangle is symmetric about zero:

$$I_m = \frac{V_{in}T_s}{8L_m} = \frac{400}{8 \times 430\ \mu\text{H} \times 100\ \text{kHz}} = 1.163\ \text{A}$$

Two hundred nanocoulombs at 1.163 A takes 172 ns. Three hundred nanoseconds of dead time
is enough, with 74 per cent to spare. One hundred nanoseconds delivers 116 nC, which is
58 per cent of the swing, so 167 V is still standing on the drain when the gate rises —
and $C_{oss} \times 167^2 \times 100$ kHz is the 0.70 W the analyser saw.

## The line voltages, and which one is binding

Setting $I_mt_d = 2C_{oss}V_{in}$ and solving gives the module's headline result,
$L_m \le t_dT_s/(16C_{oss})$ — 750 µH here — with $V_{in}$ cancelled out of both sides.
It cancels because the charge to be moved and the current available to move it are both
proportional to the rail. That is a genuinely useful invariance, and it is also the thing
that most often gets over-read, so run the budget at the three line voltages of module 2
with the switching frequency its bisection put alongside each one.

```python
import math

C_oss = 250e-12       # F, one device
L_m = 430e-6          # H, the tank of module 2
t_d = 300e-9          # s, the dead time on the board

# bus voltage and the switching frequency module 2's bisection puts with it
points = [(350.0, 74.8e3), (400.0, 100.0e3), (420.0, 113.6e3)]
for V_in, f_s in points:
    Q_need = 2.0 * C_oss * V_in                  # both devices, full rail
    I_m = V_in / (8.0 * L_m * f_s)               # peak of the triangle
    t_need = Q_need / I_m
    print("%.0f V at %5.1f kHz:  %5.1f nC needs %.4f A for %5.1f ns  "
          "-> margin %.2f" % (V_in, f_s / 1e3, Q_need * 1e9, I_m, t_need * 1e9,
                              t_d / t_need))

# the second board: the same tank, the dead time cut to 100 ns
I_m = 400.0 / (8.0 * L_m * 100e3)
left = 400.0 - I_m * 100e-9 / (2.0 * C_oss)
print("100 ns leaves %.0f V on the drain, costing %.2f W" % (left, C_oss * left ** 2 * 100e3))
print("L_m limit at 100 kHz: %.0f uH" % (t_d / (16.0 * C_oss * 100e3) * 1e6))
print("hard turn-on would cost %.1f W" % (C_oss * 400.0 ** 2 * 100e3))
print("parasitic swing (40 nH): %.1f ns" % ((math.pi / 2) * math.sqrt(40e-9 * C_oss) * 1e9))
```

At 350 V the transition needs 128.7 ns and the margin is 2.33. At 400 V it needs 172.0 ns
and the margin is 1.74. At 420 V it needs 195.4 ns and the margin has fallen to 1.54. The
rail did cancel — but $T_s$ did not, and in a frequency-controlled converter $T_s$ moves
with the line. High line runs fastest, the volt-second product across $L_m$ per half cycle
is smallest there, and the magnetising current comes out at 1.075 A instead of 1.163 A
while the charge to be moved has grown to 210 nC. Both terms move the wrong way at once.
The invariance is real and it is about the *form* of the condition, not about the
operating point: write $L_m \le t_dT_s/(16C_{oss})$ and you still have to ask which $T_s$.

The block also reproduces the two boards from the opening — 167 V left on the drain at
100 ns, costing 0.70 W — and the 750 µH ceiling on $L_m$ that the derivation gives at
100 kHz. Its last line puts the transition in proportion. The parasitic loop — 40 nH of layout
inductance with the same 250 pF — rings with a quarter period of 5.0 ns, which is what the
sandbox *What a transition actually looks like* reports and draws. The charge budget needs
172 ns, thirty-four times longer. The dead time in a resonant converter is not set by how
fast the node *can* move; it is set by how little current there is to move it with.

## The mistake, and why it is tempting

The mistake is checking zero-voltage switching at nominal line and stopping. It is
tempting for two good reasons and one bad one. The good reasons: nominal is where the
tank was synthesised, where the gain is exactly 1 and where every other number in the
design was computed. The bad one: the derivation *told you* the rail cancels, and it is
an easy step from "the condition does not contain $V_{in}$" to "the condition does not
depend on the operating point". A design verified only at 400 V has a margin of 1.74 on
paper and 1.54 where it actually has to hold, and that difference is what a 20 per cent
tolerance on $L_m$ and a hot core eat for lunch.

The related mistake in the other direction is treating dead time as shoot-through
protection to be minimised. In a hard-switched bridge that instinct is right and dead time
is dead loss. Here it is a design variable with a floor set by the charge budget and a
ceiling set by conduction: raising the 300 ns to 900 ns buys nothing at all, because the
node reached zero at 172 ns and sat there, while nine hundred nanoseconds out of a ten
microsecond period is nine per cent of the cycle spent transferring no power, and
eventually the magnetising current — still ramping — begins to pull the midpoint back
down again.

## Where the model stops holding

The weakest assumption is that $C_{oss}$ is a number. It is not; it is a strong function
of drain voltage, and in a superjunction device it can fall by more than an order of
magnitude between 25 V and 400 V. A datasheet quoting 1500 pF at 25 V and 90 pF at 400 V
is describing the same part, and neither figure belongs in the charge budget. What belongs
there is the charge itself: $Q_{oss}$ at the rail, integrated over the sweep, usually
published directly or as a charge-equivalent capacitance $C_{o(tr)} = Q_{oss}/V_{in}$.
Substituting the small-signal value at either end of the range gets the answer wrong by a
factor, in the direction that depends on which end you picked.

The second assumption is that the magnetising current is the only current, which is exact
only at resonance. Above resonance the load current has not returned to zero when the
transition starts and it adds to the available charge, so operation above $f_r$ has extra
margin the model does not credit it with. Below resonance it can subtract.

Third, and most consequential, the charge budget is a magnitude condition and says nothing
about sign. Current flowing the wrong way through the node drives the midpoint *away* from
the rail it should be heading for. The tank must be inductive — operating to the right of
the gain peak from module 2 — so the current lags the bridge voltage and is still flowing
in the direction of the previous half cycle when the devices open. A design that closes
the charge budget with margin and sits below the peak hard-switches anyway, and does it
into a conducting body diode, which is worse than hard-switching a discharged node.
Zero-voltage switching is two conditions, and this module's arithmetic settles only one of
them.

Finally, the midpoint carries more than two $C_{oss}$: transformer interwinding
capacitance and the reflected capacitance of the secondary rectifier are on that node too.
They are usually a minor addition, and they are always an addition, never a subtraction.

## What you are about to build

The sandbox draws a single transition and reports the ring frequency and the quarter
period, and stepping its dead time from 0 to 10 ns turns the trace from amber to green —
that colour change is the entire economic case for the topology. The derive unit closes
the algebra above, ending on the observation about $V_{in}$ that this reading then tests
at three line voltages. The blanks exercise assembles the inequality from four fragments.
The lab *Close the zero-voltage switching budget* then asks for six functions, including a
`zvs_ok` that must compare *charges* rather than currents so the boundary case lands
exactly on `True`, and it checks the 430 µH design against the 750 µH limit, a 900 µH tank
that fails, and the same tank with 100 ns of dead time — the second board from the top of
this reading.
''',
                },
            ],
            "quiz": {
                "title": "The charge, the current and the window",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The condition $L_m \\le t_dT_s/(16C_{oss})$ contains no $V_{in}$ at all. Why not?",
                        "opts": [
                            "The charge to be moved and the current that moves it both scale with the rail",
                            "The rail divides out only at resonance, where $L_m$ sees exactly half of it",
                            "It was cancelled when the two device capacitances were summed into one $C_{oss}$",
                            "It never entered: the magnetising current is fixed by the core, not by the input",
                        ],
                        "a": 0,
                        "why": r'''
The transition needs $2C_{oss}V_{in}$ of charge and the magnetising peak is
$V_{in}T_s/(8L_m)$; set one against the other and $V_{in}$ appears on both sides. The
clamping of $L_m$ to $V_{in}/2$ is what makes the current proportional to the rail, so it
is part of the reason rather than a restriction on it — the cancellation is not something
that happens only at resonance. Summing the two capacitances produced the factor of two in
the charge and touched no voltage. And the magnetising current is emphatically set by the
input: it is $V_{in}/2$ across $L_m$ for half a period, which is why it scales with the
line at fixed frequency.
''',
                    },
                    {
                        "q": "A frequency-controlled LLC runs 74.8 kHz at 350 V and 113.6 kHz at 420 V. Which line voltage is the hard case for ZVS?",
                        "opts": [
                            "High line, where the period is shortest so the magnetising current is smallest",
                            "Low line, where the smaller rail leaves less energy in the tank to move the node",
                            "Nominal line, since the tank was synthesised there and the rest is a perturbation",
                            "None: the rail cancels, so every operating point is exactly as hard",
                        ],
                        "a": 0,
                        "why": r'''
$I_m = V_{in}T_s/(8L_m)$, so the current follows the volt-second product per half cycle.
At 420 V and 113.6 kHz that product is smaller than at 400 V and 100 kHz, and the charge
required has grown to 210 nC, so the margin falls from 1.74 to 1.54. Low line is the
easiest point, not the hardest — the current rises to 1.36 A while only 175 nC is needed.
Nominal is where the design was done and is exactly why the check gets skipped. And the
rail cancelling is a statement about the *form* of the inequality; $T_s$ survives it, and
$T_s$ is what the controller moves.
''',
                    },
                    {
                        "q": "Which current actually swings the bridge midpoint during the dead time?",
                        "opts": [
                            "The magnetising current, which sits at its peak the moment the devices open",
                            "The whole primary current, sinusoid and triangle together, since both flow there",
                            "The output filter inductor current, reflected back through the transformer",
                            "Reverse-recovery charge from the body diode as the device turns off",
                        ],
                        "a": 0,
                        "why": r'''
At resonance the load-carrying sinusoid is in phase with the bridge voltage, so it passes
through zero exactly when the half cycle ends, and the triangle is at its peak there. What
is left is $I_m$, and its independence from load is what makes ZVS hold at 20 W as well as
at 240 W. Counting the sinusoid too would credit the transition with current that is not
there at that instant, which is the error that makes a light-load failure look impossible
on paper. An LLC has no output filter inductor — the secondary feeds a capacitor
directly. And reverse recovery is a consequence of getting this wrong, not a source of
charge to rely on.
''',
                    },
                    {
                        "q": "Your budget says the node needs 172 ns and the dead time is already 300 ns. What does raising it to 900 ns achieve?",
                        "opts": [
                            "Nothing for the transition, and it costs conduction time the cycle needed",
                            "Proportionally more margin, since delivered charge grows with the time allowed",
                            "A slower and softer edge, which lowers the interference the transition radiates",
                            "Insurance against shoot-through when a hot driver turns off slowly",
                        ],
                        "a": 0,
                        "why": r'''
The drain reaches zero at 172 ns and stays there; the extra 728 ns changes nothing about
the transition, which is what the sandbox shows when its dead-time slider passes the swing
time and the trace stops responding. What it does change is the ledger: 900 ns out of a
10 µs period is nine per cent of the cycle transferring no power, and the magnetising
current keeps ramping and eventually drags the midpoint back. Delivered charge does grow
with time, but only until the node arrives — after that there is nowhere left to put it.
The edge shape is set by the current and the capacitance, not by how long you wait. And
shoot-through protection is real but is measured in tens of nanoseconds, not hundreds.
''',
                    },
                    {
                        "q": "A datasheet gives $C_{oss}$ as 1500 pF at 25 V and 90 pF at 400 V. Which value belongs in the charge budget?",
                        "opts": [
                            "Neither: what the budget wants is $Q_{oss}$ at the rail, divided by the rail",
                            "The 400 V value, because that is the voltage the device stands off when off",
                            "The 25 V value, since most of the sweep happens down where the node is low",
                            "The average of the two, because the node traverses the whole range between them",
                        ],
                        "a": 0,
                        "why": r'''
$C_{oss}$ is a small-signal slope at one bias, and the budget is about charge, so what is
wanted is $Q_{oss} = \int C_{oss}\,dV$ across the rail — published directly on most
datasheets, or as the charge-equivalent $C_{o(tr)} = Q_{oss}/V_{in}$. Taking the 400 V
figure understates the charge badly, because the capacitance is enormous over the low-
voltage part of the sweep. Taking the 25 V figure overstates it for the mirror-image
reason, and while that error is at least in the safe direction it sizes $L_m$ far smaller
than it needs to be and pays for it in circulating current. An average of two
small-signal values is not an integral of anything.
''',
                    },
                    {
                        "q": "The charge budget closes with 50 per cent margin, yet the bridge still turns on hard. What is the likely cause?",
                        "opts": [
                            "The tank is below the gain peak, so the current leads and moves the node the wrong way",
                            "The magnetising inductance came out under its design value, giving too much current",
                            "The dead time exceeds the swing time, so the midpoint arrives before the gate rises",
                            "The switching frequency is above resonance, where the tank current lags the bridge voltage",
                        ],
                        "a": 0,
                        "why": r'''
The budget is a magnitude condition and says nothing about sign. On the capacitive side of
the gain peak the current leads the bridge voltage, so at the switching instant it is
already flowing the other way and drives the midpoint away from the rail it should reach —
and the turn-on then happens into a conducting body diode with recovery under way, which
is worse than hard-switching a plain capacitance. Too *much* magnetising current only
shortens the transition. A dead time longer than the swing needs is the intended
condition, not a fault. And lagging current above resonance is precisely the region the
controller is steered into.
''',
                    },
                ],
            },
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
                    "At zero dead time the trace is amber. The drain voltage falls the whole way in under 8 ns — a near-vertical edge against the 600 ns the axis covers — and then rings on at the $32.5$ MHz the panel names, while the blue current steps to full scale in the same instant. That overlap of a large voltage and a large current is the switching loss, and the panel names its cause: the device turns on into a charged capacitance.",
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
                        "hint": "One capacitor goes from $0$ to $V_{in}$ and the other from $V_{in}$ to $0$; both cost $C_{oss}V_{in}$.",
                        "deconstruct": [
                            "Charge on a capacitor changing by $\\Delta V$ is $C\\,\\Delta V$.",
                            "Two devices each swing the full rail, so the charges add.",
                        ],
                    },
                    {
                        "prompt": "Suppose the tank current is roughly constant at $I_d$ across the dead time. Write the shortest dead time that can deliver that charge.",
                        "answer": "\\frac{2 C_{oss} V_{in}}{I_d}",
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
                        "hint": "The half-period gives the peak-to-peak swing; the peak is half of that because the triangle is symmetric about zero.",
                        "deconstruct": [
                            "Over $T_s/2$ the current changes by $(V_{in}/2)(T_s/2)/L_m = V_{in}T_s/(4L_m)$.",
                            "That is the peak-to-peak ripple, and the waveform is symmetric about zero.",
                        ],
                    },
                    {
                        "prompt": "Zero-voltage switching holds when the magnetising current is at least the current the charge budget demands. Set $I_m$ equal to that demand and solve for the largest magnetising inductance that still works.",
                        "answer": "\\frac{t_d T_s}{16 C_{oss}}",
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
            "blanks": {
                "title": "The charge budget that ZVS really is",
                "minutes": 9,
                "caption": "zvs.py — four numbers, one inequality",
                "lang": "python",
                "brief": r"""
Zero-voltage switching sounds like a property of the topology. It is not — it is an
inequality between two charges, and it either holds at your operating point or it does
not.

Assume a half-bridge at the series resonance with unity gain, so the voltage across
$L_m$ is clamped to $V_{in}/2$ for each half period.
""",
                "listing": """# The charge the transition has to move: both devices' output capacitance,
# swung across the full rail.
Q_needed = ___ * V_in

# The magnetising current is a triangle. Across L_m sits V_in/2 for half a
# period, so its peak is
I_m_peak = V_in / (___ * L_m * f_sw)

# During the dead time that current is roughly constant, and it delivers
Q_available = I_m_peak * ___

# ZVS is exactly the statement   Q_available >= Q_needed.
# Raising L_m cuts the circulating current and therefore the conduction loss,
# and it ___ .
""",
                "blanks": [
                    {
                        "prompt": "Two devices, one rail.",
                        "hole": "?",
                        "opts": ["2 * C_oss", "C_oss", "C_oss / 2", "4 * C_oss"],
                        "a": 0,
                        "why": "One device's $C_{oss}$ has to be discharged from $V_{in}$ to 0 while the other is charged from 0 to $V_{in}$, so both are moved across the full rail and the charges add. Any capacitance you deliberately add across the bridge goes in here too — and it is why adding a snubber capacitor makes ZVS harder, not easier.",
                        "whys": [
                            "One device's $C_{oss}$ has to be discharged from $V_{in}$ to 0 while the other is charged from 0 to $V_{in}$, so both are moved across the full rail and the charges add. Any capacitance you deliberately add across the bridge goes in here too — and it is why adding a snubber capacitor makes ZVS harder, not easier.",
                            "Counts only one device. The other one is charging at the same time, through the same node, and its charge has to come from somewhere too.",
                            "Half of one device, which underestimates the requirement by a factor of four and produces a design that does not switch softly on the bench.",
                            "Twice too much. There are two devices, not four — though a full bridge, with two legs, does have twice this per leg.",
                        ],
                    },
                    {
                        "prompt": "V_in/2 across L_m for half a period. What is the peak of the triangle?",
                        "hole": "?",
                        "opts": ["8", "4", "2", "16"],
                        "a": 0,
                        "why": "$\\Delta I = (V_{in}/2)(T_{sw}/2)/L_m = V_{in}/(4L_mf_{sw})$ peak-to-peak, and the triangle is symmetric about zero, so the peak is half of that: $V_{in}/(8L_mf_{sw})$.",
                        "whys": [
                            "$\\Delta I = (V_{in}/2)(T_{sw}/2)/L_m = V_{in}/(4L_mf_{sw})$ peak-to-peak, and the triangle is symmetric about zero, so the peak is half of that: $V_{in}/(8L_mf_{sw})$.",
                            "That is the peak-to-peak swing, not the peak. Forgetting that the magnetising current is symmetric about zero overestimates the available charge by exactly two, and two is the whole margin in most designs.",
                            "Uses the full rail across $L_m$ rather than half of it, and forgets the peak-to-peak factor as well.",
                            "Too small by two: this would be the peak if the current only swung one way, which a magnetising current cannot do without saturating the core.",
                        ],
                    },
                    {
                        "prompt": "How long does it have to do it in?",
                        "hole": "?",
                        "opts": ["t_dead", "T_sw", "T_sw / 2", "1 / f_sw"],
                        "a": 0,
                        "why": "The dead time, and nothing longer. Once the gate goes high the transition is over — whatever the drain voltage happens to be at that instant is what gets switched. That is why dead time is a design parameter and not just a safety margin against shoot-through.",
                        "whys": [
                            "The dead time, and nothing longer. Once the gate goes high the transition is over — whatever the drain voltage happens to be at that instant is what gets switched. That is why dead time is a design parameter and not just a safety margin against shoot-through.",
                            "A whole period is orders of magnitude longer than the window actually available, and would predict ZVS in designs that visibly hard-switch.",
                            "Half a period is the conduction interval, not the transition. The transition is the sliver between one device turning off and the other turning on.",
                            "The same as a whole period, written differently.",
                        ],
                    },
                    {
                        "prompt": "Larger L_m means less circulating current. What does it do to ZVS?",
                        "hole": "?",
                        "opts": [
                            "makes ZVS harder, because there is less current to move the charge",
                            "makes ZVS easier, because the transition is gentler",
                            "leaves ZVS unaffected",
                            "raises the series resonant frequency",
                        ],
                        "a": 0,
                        "why": "This is the central trade of LLC design. $I_{m,peak}$ is inversely proportional to $L_m$, so the same inductance that reduces the loss in module 4's budget also reduces the charge available in module 3's inequality. The design sits at the largest $L_m$ that still closes the budget, with margin — and the margin is what has to survive tolerance and temperature.",
                        "whys": [
                            "This is the central trade of LLC design. $I_{m,peak}$ is inversely proportional to $L_m$, so the same inductance that reduces the loss in module 4's budget also reduces the charge available in module 3's inequality. The design sits at the largest $L_m$ that still closes the budget, with margin — and the margin is what has to survive tolerance and temperature.",
                            "It is exactly backwards, and it is the assumption behind a converter that is efficient in simulation and hot on the bench: less circulating current is less charge to work with.",
                            "$L_m$ appears directly in $I_{m,peak}$ and therefore directly in the charge available. It is the dominant term in the whole budget.",
                            "$L_m$ sits across the load, so it moves the *lower* resonance; the series resonance is set by $L_r$ and $C_r$ and does not contain $L_m$ at all.",
                        ],
                    },
                ],
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
            "read": [
                {
                    "title": "Seven watts, and not one of them where you expected",
                    "minutes": 15,
                    "body": r'''
The converter is finished: 400 V in, 12 V out, 100 kHz, the 86 µH and 29.45 nF tank of
module 2 with its 430 µH magnetising inductance, 300 ns of dead time, and zero-voltage
switching confirmed on the bench at all three line voltages. Put a power analyser on both
ends and load it to 20 A.

It reads 247.13 W in and 240.00 W out. Seven and a bit watts of loss, 97.11 per cent.
Now turn the load down to 4 A. The output is 48.00 W, a fifth of what it was, and the
input reads 49.71 W. The loss has gone from 7.13 W to 1.71 W — a factor of 4.2, not a
factor of five — and the efficiency has fallen to 96.56 per cent.

Two questions come out of that pair of readings, and they have the same answer. Where are
the seven watts, and why did they not scale with the load?

## The four terms

Build the budget from the parts rather than from a figure of merit. The lab *Build an
honest loss budget* asks for exactly these functions, and this is the arithmetic it
checks.

**The primary carries two currents at once.** One is the load-carrying sinusoid, of peak
$I_p = \pi P_{out}/V_{in} = 1.885$ A at full load, which follows from equating the output
power to the product of the fundamental RMS voltage $\sqrt2 V_{in}/\pi$ and the
fundamental RMS current at resonance. The other is the magnetising triangle of peak
$I_m = 1.163$ A from module 3, which delivers nothing.

Their RMS values do not add. Over a quarter period the triangle rises linearly,
$i(t) = I_m t/T_4$, so its mean square is
$\frac{1}{T_4}\int_0^{T_4}I_m^2 (t/T_4)^2\,dt = I_m^2/3$ and its RMS is $I_m/\sqrt3$,
against $I_p/\sqrt2$ for the sinusoid. At resonance the load current is in phase with the
bridge voltage while the magnetising current is the integral of a square wave in phase
with it — so the triangle's harmonics are all a quarter cycle away from the sinusoid, and
every cross term in the product integrates to zero. The mean squares add:

$$I_{rms}^2 = \frac{I_p^2}{2} + \frac{I_m^2}{3} = 1.777 + 0.451 = 2.227\ \text{A}^2$$

which is 1.492 A RMS. Both devices and the primary winding see it, so the loss is
$(R_{ds} + R_w)I_{rms}^2 = 0.4 \times 2.227 = 0.891$ W.

**The secondary pays for its own waveform.** The secondary current is a rectified
sinusoid. Its average is what the load draws, $I_o = 2I_{pk}/\pi$, but its heating is set
by its RMS, $I_{pk}/\sqrt2$. The ratio of the two is

$$\frac{I_{rms}}{I_o} = \frac{I_{pk}/\sqrt2}{2I_{pk}/\pi} = \frac{\pi}{2\sqrt2} = 1.1107$$

so the same average current dissipates $1.1107^2 = 1.234$ times what a rectangular
waveform would. With two synchronous rectifiers of 5 mΩ in the path at all times,
$2R_{sr}(1.1107 \times 20)^2 = 4.935$ W, against 4.000 W for a rectangle of the same
average. Nine hundred milliwatts is the price of the sinusoidal shape.

**The core does not care about the load.** Steinmetz gives
$P = kf_s^{\alpha}B^{\beta}V_e$, and with the specification's ferrite — $k = 3.2$,
$\alpha = 1.46$, $\beta = 2.75$ — at 100 kHz, 0.1 T and 11.5 cm³ that is 1.306 W. The
flux swing is set by the volt-seconds the primary applies, not by the current the
secondary draws, so this term is the same at 20 A and at 4 A.

**The switching term is zero,** because module 3 closed the charge budget. Had it not,
$C_{oss}V_{in}^2f_s$ would add 4.000 W.

```python
import math

V_in, V_out = 400.0, 12.0
R_ds, R_w, R_sr = 0.15, 0.25, 0.005
I_m = 1.1627906976744187          # magnetising peak, fixed by the 430 uH tank
form = math.pi / (2.0 * math.sqrt(2.0))

for I_out in (20.0, 4.0):
    P_out = V_out * I_out
    I_p = math.pi * P_out / V_in                       # load-carrying peak
    ms = I_p * I_p / 2.0 + I_m * I_m / 3.0             # mean square of the primary
    terms = {
        "primary": (R_ds + R_w) * ms,
        "secondary": 2.0 * R_sr * (form * I_out) ** 2,
        "core": 3.2 * 100e3 ** 1.46 * 0.1 ** 2.75 * 11.5e-6,
        "switching": 0.0,
    }
    total = sum(terms.values())
    print("%5.0f W out:  I_p %.3f A, primary rms %.3f A" % (P_out, I_p, math.sqrt(ms)))
    for k, v in terms.items():
        print("   %-10s %6.4f W  (%4.1f%% of the loss)" % (k, v, 100.0 * v / total))
    print("   total %.4f W   eta %.4f   circulating share of primary %.1f%%"
          % (total, P_out / (P_out + total), 100.0 * (I_m * I_m / 3.0) / ms))
```

## Where the seven watts actually are

At full load the secondary is 4.935 W of 7.131 W — **69 per cent of the entire loss**. The
core is 18.3 per cent, the primary conduction 12.5 per cent, and the term that the
whole of module 3 was written to remove is nothing at all. Rectifying 20 A at 12 V costs
five and a half times more than conducting 1.5 A at 400 V, which is the general shape of
every low-voltage high-current supply: the loss is on the side with the current, and no
amount of work on the primary moves it. If this design needs to reach 98 per cent, the
lever is a third rectifier in parallel or a lower $R_{sr}$, not a better primary MOSFET.

At a fifth of the load the ranking inverts. The secondary term falls by a factor of 25
along with $I_o^2$, to 0.197 W, and the core term does not fall at all — it is 76 per cent
of the light-load budget. Add the 0.144 W of gate drive that the capstone's fifth term
counts, $2Q_gV_gf_s$, which is also constant, and roughly four fifths of the light-load
loss is independent of the output. That is the mechanism behind the efficiency curve: not
that anything got worse at light load, but that most of the budget never got better.

The last column tells the primary's own version of the same story. The circulating share
of the primary mean square is 20.2 per cent at full load and 86.4 per cent at 48 W, because
$I_p$ shrinks with the output and $I_m$ does not.

## What zero-voltage switching cost, in watts

The magnetising current is bought deliberately, so it is fair to ask the price. Its share
of the primary conduction loss is $(R_{ds}+R_w)I_m^2/3 = 0.180$ W. What it removes is
$C_{oss}V_{in}^2f_s = 4.000$ W. A hundred and eighty milliwatts to avoid four watts is a
return of better than twenty to one, and that ratio, not the efficiency figure, is the
actual argument for the topology.

It also settles the shape of the trade with module 3. Raising $L_m$ to its 750 µH ceiling
would drop $I_m$ to 0.667 A and the circulating term to 0.059 W — a saving of 0.12 W out
of 7.13, which moves the efficiency by five hundredths of a percentage point — while
spending the whole of the margin that keeps the 4.000 W away. The trade is lopsided, which is why a
design sits comfortably below the ceiling rather than against it. The instinct that a
larger $L_m$ is the route to a more efficient converter comes from thinking about the
circulating current as waste; the arithmetic says it is one of the cheapest things in the
budget.

## The mistake, and why it is tempting

The mistake is designing to, and quoting, a single efficiency number at full load. It is
tempting for the best of reasons: it is the point the specification names, the point the
thermal design has to survive, the easiest point to measure accurately, and the number
that goes on the datasheet. It is also the point at which this converter's loss budget is
least representative of how it will spend its life. A supply in a desktop machine or a
telecom shelf sits at 10 to 30 per cent load most of the time, which is why 80 PLUS and
the ErP directive weight several load points rather than one, and why the sandbox *The
loss the transition either does or does not cost* keeps returning to the fact that soft
switching relocates loss into terms that do not scale.

The second-order version of the same mistake is reading the drop from 97.11 to 96.56 per
cent as a small number. In watts of *waste* it is a rise from 2.9 per cent of the output to
3.4 per cent — and in a fanless enclosure the relevant quantity is neither, it is the
1.71 W that has to leave the box while the airflow from a loaded fan is not there.

## Where these numbers stop being true

Every resistance in the budget was taken at room temperature from a datasheet typical.
A silicon MOSFET's $R_{ds(on)}$ roughly doubles between 25 °C and 125 °C, so the 0.891 W
primary term is closer to 1.6 W on a hot board, and the 4.935 W secondary term moves the
same way. A budget built from 25 °C typicals is not conservative; it is wrong by nearly a
factor of two on the two largest terms.

The 0.25 Ω of primary winding resistance is a DC value. At 100 kHz skin and proximity
effects raise the effective AC resistance of an ordinary solid-wire winding by a factor of
two to five, which is why transformers at this frequency are wound with litz or with
interleaved foil.

The Steinmetz coefficients are a fit over a bounded range of frequency, flux and
temperature, taken under sinusoidal excitation. An LLC transformer sees neither a sinusoid
nor a fixed temperature, and extrapolating a fit is not a calculation. Treat 1.306 W as an
estimate with a wide bar on it, and note that the exponent argument still holds where the
fit does: with $B \propto 1/f_s$ at fixed volt-seconds, the density goes as
$f_s^{\alpha-\beta}$, so doubling to 200 kHz with the flux halved gives 0.534 W — core
loss falls as the frequency rises, which is the opposite of the usual intuition.

The quadrature addition is exact at resonance and only approximate away from it: off
resonance the load current acquires a phase and the cross term stops integrating to zero,
so the primary RMS is slightly higher than the formula says at 74.8 kHz and at 113.6 kHz.

Finally, the budget has four terms and a real converter has a dozen. Body-diode conduction
during the dead time, synchronous-rectifier gate drive and its own dead-time conduction,
output capacitor ESR, snubbers, the bias supply and the controller are all missing here,
and together they are commonly another half to one watt in a supply this size. A
four-term budget that lands on 97.11 per cent should be read as predicting something
closer to 96.7, and the gap is not error — it is the terms nobody wrote down.

## What you are about to build

The derive unit *The price of circulating current* takes the triangle RMS, the quadrature
sum and the Steinmetz exponent to the same conclusions this reading reaches numerically.
The sandbox reads a single transition with the loss ledger in mind rather than the
waveform, and its last note — that a 1 nH loop rings at 318 MHz — is the reminder that the
loss lives at 100 kHz while the interference lives three decades above it. The quiz *Four
honest terms* checks the two RMS constants and the quadrature rule, which are the pieces
most often mixed up. And the lab asks for the six functions that produce the table above,
ending with the light-load comparison whose whole point is the difference between the two
efficiencies rather than either one of them.
''',
                },
            ],
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
            "quiz": {
                "title": "Four honest terms",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A symmetric triangular current of peak $I_m$ has what RMS value?",
                        "opts": ["$I_m/\\sqrt{3}$", "$I_m/\\sqrt{2}$", "$I_m/2$", "$I_m$"],
                        "a": 0,
                        "why": r"""
$I_m/\sqrt{3} = 0.577I_m$. It is a different constant from the sinusoid's
$1/\sqrt{2} = 0.707$, and using the wrong one is a 22% error in current and therefore a
50% error in $I^2R$ loss — enough to turn a design that runs warm into one that does
not. The two constants are worth memorising as a pair, because a resonant converter's
primary current contains one of each.
""",
                    },
                    {
                        "q": "The primary current is the load-carrying sinusoid plus the magnetising triangle. How do they combine into an RMS figure?",
                        "opts": [
                            "In quadrature — the squares add, because one is in phase with the load and the other is not",
                            "They add directly",
                            "Only the larger of the two matters",
                            "They subtract, because the magnetising current is reactive",
                        ],
                        "a": 0,
                        "why": r"""
$I_{rms}^2 \approx I_{load,rms}^2 + I_{m,rms}^2$. The magnetising current is very nearly
in quadrature with the load component, so the squares add and the total is less than the
plain sum — which is genuinely good news, and the reason a modest magnetising current
costs less than its magnitude suggests. What it does not do is disappear: it is
resistive loss in the primary winding and the switches all the same.
""",
                    },
                    {
                        "q": "How much power does the magnetising current deliver to the load?",
                        "opts": ["None", "A share proportional to $L_m$", "All of it, at light load", "It depends on the switching frequency"],
                        "a": 0,
                        "why": r"""
None at all. It circulates between the tank and the bridge, returning every joule it
borrows — and paying $I^2R$ in the windings and the channel resistance on the way round,
twice per cycle. It is a pure cost on the loss ledger, bought deliberately because it is
what makes ZVS possible. Naming it "circulating" rather than "wasted" is not a
euphemism: it does a job, just not the job of delivering power.
""",
                    },
                    {
                        "q": "Which loss does zero-voltage switching actually eliminate?",
                        "opts": [
                            "The $\\tfrac{1}{2}C_{oss}V_{in}^2$ dumped inside the device at hard turn-on",
                            "Conduction loss in the channel",
                            "Core loss in the transformer",
                            "The diode drop in the output rectifier",
                        ],
                        "a": 0,
                        "why": r"""
Only the turn-on energy, and only that. The charge on $C_{oss}$ has to go somewhere when
the device turns on; hard-switched, it goes through the channel as heat, and at high
frequency that term dominates everything else. ZVS moves the charge *before* the gate
rises, using the magnetising current, so nothing is dumped. Conduction, core and
rectifier losses are all untouched — which is the honest framing this module insists on:
ZVS relocates loss, it does not delete it.
""",
                    },
                    {
                        "q": "You double $L_m$. What is the trade?",
                        "opts": [
                            "Less circulating current and less conduction loss, but less charge available for ZVS",
                            "Less loss everywhere, with no cost",
                            "More gain, at the price of efficiency",
                            "Nothing changes below resonance",
                        ],
                        "a": 0,
                        "why": r"""
The magnetising current halves, so its contribution to the RMS falls and the conduction
term improves. But it is that same current that has to move $2C_{oss}V_{in}$ during the
dead time, so the ZVS budget from module 3 gets tighter — and if it stops closing, the
turn-on loss you had eliminated comes back all at once, dwarfing what you saved. The
design point is the largest $L_m$ that still closes the budget with margin, which is why
these two modules have to be read together.
""",
                    },
                ],
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
   `"core"` and `"gate"`, in watts. Gate loss is $2Q_gV_gf_s$. Take `B_PK` straight
   from the spec and do not rescale it with frequency: module 4 showed the flux swing
   going as $1/f_s$, but the specification pins it at the nominal operating point, so
   the core term is exact at nominal line and approximate at the extremes. There is no
   switching term, because this design holds ZVS everywhere.
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
            "The rail voltage cancels out of the margin too, not just out of the limit: the ratio reduces to $t_d/(16L_mf_sC_{oss})$. What is left is the switching frequency, and that does move with line, so high line — the fastest point — is the binding case.",
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
