"""EMAG510 — Guided Waves and Waveguides.

Same authoring rules as CTRL510, which is the template for this file:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

The sandbox notices in this file were written against the actual draw functions in
src/studio.js. Every number quoted in a notice — a readout, a decibel level, a
degree — was evaluated from that code before it was written down.
"""

COURSE = {
    "id": "EMAG510",
    "title": "Guided Waves and Waveguides",
    "band": 5,
    "level": "Advanced",
    "prereqs": [],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◎",
    "summary": (
        "A signal on a wire is a wave. Once the wire is long compared with a wavelength "
        "there is no such thing as the voltage on it, only the voltage at a place and a "
        "time. This course builds that picture from the telegrapher equations, uses it to "
        "decide what a mismatched load does to a line, and then follows the same wave "
        "equation into a hollow metal pipe — where it produces cutoff, dispersion, and two "
        "velocities that are not equal to each other."
    ),
    "outcomes": [
        "Derive the telegrapher equations and read characteristic impedance and phase velocity straight off the per-unit-length parameters.",
        "Compute reflection coefficient, VSWR and input impedance for a terminated line, and design a quarter-wave transformer.",
        "Find the cutoff frequency of any TE or TM mode in a rectangular guide and identify the single-mode band.",
        "Separate phase velocity from group velocity, and predict how far a pulse spreads over a given run of guide.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that propagates a pulse through a length of rectangular guide and measures the delay and the spreading it suffers.",
    "reading": [
        "*Microwave Engineering*, Pozar — chapters 2 and 3 cover almost all of this course.",
        "*Fields and Waves in Communication Electronics*, Ramo, Whinnery & Van Duzer — for the separation of variables done slowly.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The telegrapher equations and the lossless line",
            "summary": "Two coupled first-order equations in z and t. Everything a line does is in them.",
            "concepts": [
                "A line has inductance and capacitance *per unit length*, and no single lumped value of either.",
                "$\\partial V/\\partial z = -L\\,\\partial I/\\partial t$ and $\\partial I/\\partial z = -C\\,\\partial V/\\partial t$: KVL and KCL applied to a slice of length $dz$.",
                "Eliminating one variable gives the wave equation, whose speed is $1/\\sqrt{LC}$.",
                "Characteristic impedance $Z_0 = \\sqrt{L/C}$ is a ratio carried by a travelling wave, not a resistance you can measure with an ohmmeter.",
                "A ladder of discrete LC sections is a low-pass filter with a real cutoff; a line is the limit as the sections become infinitesimal and that cutoff goes to infinity.",
            ],
            "read": [
                {
                    "title": "Thirty metres of coax, and the two numbers hiding in it",
                    "minutes": 15,
                    "body": r'''
A 30.0 m reel of RG-58 is lying on the bench with nothing connected to its far end.
A pulse generator with a 50 Ω source resistance drives one end with a 1 V step, and
a scope tees onto that same end and watches. The trace does something a lumped
circuit has no room for: it rises to 0.50 V, sits flat there for 303 ns, and then
steps up to 1.00 V and stays.

Three facts are on that screen and the whole module is in them.

**The 0.50 V.** The generator's 50 Ω is in series with whatever it is driving, so a
half-amplitude step means the load is drawing exactly the current a 50 Ω resistor
would draw. The far end of the reel is open — it ends in air — and the copper's own
resistance is under a tenth of an ohm. For 303 ns the open-ended reel is a 50 Ω
resistor.

**The 303 ns.** Nothing about the generator changed at that instant. What changed is
that news of the open end came back. The step had to travel 30 m to the end and 30 m
back before the near end could learn there was an end at all.

**The final 1.00 V.** In the steady state an open circuit carries no current, so no
voltage is dropped across the source resistance and the whole 1 V appears at the
input. The line ends up doing what an open circuit is supposed to do — 303 ns later
than a lumped picture would have it.

## A slice of line, and what KVL says about it

The reel has inductance because current in it makes a magnetic field, and
capacitance because the inner conductor and the braid are separated conductors at
different potentials. Neither is a lumped value. Cut the reel in half and each half
has half as much of both, which is the definition of a quantity that is *per unit
length*: an inductance $L$ in henries per metre and a capacitance $C$ in farads per
metre.

Take a slice of length $dz$ at position $z$. Its series inductance is $L\,dz$ and its
shunt capacitance is $C\,dz$. KVL round the slice says the voltage drop across it is
the inductive drop:

$$V(z + dz) - V(z) = -L\,dz\,\frac{\partial I}{\partial t}
\quad\Longrightarrow\quad
\frac{\partial V}{\partial z} = -L\,\frac{\partial I}{\partial t}$$

KCL at the far node of the slice says the current that fails to come out the other
side went into charging the shunt capacitance:

$$\frac{\partial I}{\partial z} = -C\,\frac{\partial V}{\partial t}$$

Those are the telegrapher equations, and the derivation *From a slice of line to a
wave* walks the algebra that follows. Differentiate the first with respect to $z$,
the second with respect to $t$, and subtract to eliminate $I$:

$$\frac{\partial^2 V}{\partial z^2} = LC\,\frac{\partial^2 V}{\partial t^2}$$

That is the wave equation. Any function of the form $V = f(t - z/v_p)$ satisfies it
provided $1/v_p^2 = LC$, which fixes

$$v_p = \frac{1}{\sqrt{LC}}$$

Now put such a wave back into the first telegrapher equation. With
$V = f(t - z/v_p)$ the left-hand side is $\partial V/\partial z = -f'/v_p$, and with
$I = g(t - z/v_p)$ the right-hand side is $-L\,\partial I/\partial t = -L g'$. Equate
them: $f' = L v_p\, g'$, and integrating,

$$\frac{V}{I} = L v_p = \frac{L}{\sqrt{LC}} = \sqrt{\frac{L}{C}} \equiv Z_0$$

The ratio of voltage to current in a single travelling wave is a constant fixed by
the cross-section of the cable. That constant is the 50 Ω the scope saw. Note what
never entered the derivation: the length of the reel. $Z_0$ and $v_p$ exist before
anyone decides how much cable to cut.

## Reading the reel backwards

The bench measured $Z_0$ and $v_p$; the model wants $L$ and $C$. Multiply and divide:
$Z_0 v_p = \sqrt{L/C}\cdot 1/\sqrt{LC} = 1/C$ and $Z_0/v_p = L$. Two lines of algebra
turn a scope trace into the two per-metre constants of the cable.

```python
import math

# 30.0 m of RG-58 with the far end left open. The step comes back 303 ns later,
# and until it does the generator sees nothing but the line.
length, round_trip, z0 = 30.0, 303e-9, 50.0

v_p = 2 * length / round_trip
L = z0 / v_p
C = 1.0 / (z0 * v_p)

print(f"v_p = {v_p:.4e} m/s = {v_p / 2.99792458e8:.3f} c")
print(f"L   = {L * 1e9:.1f} nH/m")
print(f"C   = {C * 1e12:.1f} pF/m")
print(f"and back again: sqrt(L/C) = {math.sqrt(L / C):.1f} ohm, "
      f"1/sqrt(LC) = {1 / math.sqrt(L * C):.4e} m/s")
```

It prints a phase velocity of $1.9802\times10^8$ m/s — 0.661 of the speed of light —
and then 252.5 nH/m and 101.0 pF/m. Open an RG-58 datasheet and it will quote about
101 pF per metre and a velocity factor of 0.66. The scope trace and the datasheet are
the same two numbers written in different units, and the last line of the block does
the round trip to prove no information was lost on the way.

The velocity factor is not a free parameter either. For a coaxial line
$v_p = c/\sqrt{\varepsilon_r}$, and solid polyethylene has $\varepsilon_r \approx
2.3$, whose square root is 1.52. That is where 0.66 comes from, and it is why every
solid-polyethylene cable in the catalogue — 50 Ω, 75 Ω, thin, thick — has the same
velocity factor while their impedances differ. Geometry sets $Z_0$; the dielectric
sets $v_p$.

## The mistake: reaching for an ohmmeter

The most common thing done to a 50 Ω cable is to put a meter across it and be
surprised. With the far end open the meter reads megohms; with the far end shorted it
reads the 0.1 Ω of the copper. Neither reading is anywhere near 50.

The reason it is tempting is that $Z_0$ is quoted in ohms and it genuinely is a ratio
of volts to amps — the scope measured it. But it is the ratio carried by *one
travelling wave*, and an ohmmeter does not launch one. An ohmmeter applies a steady
voltage and waits, and waiting is exactly what destroys the measurement: the far end
answers, the answer arrives, and from then on the meter is reading the far end rather
than the line. On the trace above, the 50 Ω was on the screen for 303 ns and then
went away. A time-domain reflectometer is an ohmmeter that has learnt to look before
the answer gets back.

The same idea, run the other way, is the point of the *A line, made of eight
components* build exercise. Terminate the far end in $\sqrt{L/C}$ and the wave
arriving there finds a load that draws exactly the current more line would have
drawn. Nothing comes back, ever, and the near end reads $Z_0$ not for 303 ns but
permanently. Matching is the art of making a finite line indistinguishable from an
infinite one.

## Four sections, and a real line

A computer cannot take the limit $dz \to 0$, so a simulation chops the line into
sections of finite $L_s$ and $C_s$ and leapfrogs them. That is what the lab
*Simulate a line as a ladder of LC sections* asks for; here is the same scheme in
twenty lines, with the lab's own default ladder.

```python
import math

Ls, Cs, N = 1.0, 0.25, 20        # per section, in the lab's own units
dt, steps = 0.01, 4000

v = [0.0] * (N + 1)              # node voltages
i = [0.0] * N                    # branch currents, i[k] from node k to node k+1
far = []
for _ in range(steps):
    v[0] = 1.0                   # an ideal 1 V step, held from t = 0
    far.append(v[N])
    for k in range(N):
        i[k] += (dt / Ls) * (v[k] - v[k + 1])
    for k in range(1, N):
        v[k] += (dt / Cs) * (i[k - 1] - i[k])
    v[N] += (dt / Cs) * i[N - 1]

arrival = next(n for n, y in enumerate(far) if y > 0.5) * dt
print(f"one section: Z0 = {math.sqrt(Ls / Cs):.1f}, delay = {math.sqrt(Ls * Cs):.2f}")
print(f"{N} sections predict {N * math.sqrt(Ls * Cs):.1f}; the far end crosses "
      f"0.5 V at t = {arrival:.2f}")
print(f"peak at the open far end: {max(far):.2f} V")
```

It reports $Z_0 = 2.0$, a per-section delay of 0.50, a predicted transit of 10.0, a
measured crossing at 10.01 — and a peak of 2.42 V at the open end. Two of those
numbers deserve attention.

The doubling is real physics. An open end forces the current to zero, which can only
happen if a reflected wave of equal amplitude cancels the incident current, and the
voltages of two such waves add. The far end goes to twice the incident amplitude,
which is the same $\Gamma = +1$ that put the reel's near end at 1.00 V after 303 ns.
Module 2 is about what happens when the end is neither open nor matched.

The 0.42 above that is not physics. A ladder of discrete sections is a low-pass
filter with a cutoff at $2/\sqrt{L_s C_s}$, and a step pushed through a filter with a
sharp corner rings. That is why the lab's test accepts a peak anywhere between 1.9
and 2.6 rather than demanding 2.0: the overshoot belongs to the model, not to the
line. The sandbox *One LC section, and why a line is not one* is the same defect
isolated to a single section, where a light termination puts a 20 dB peak on the
response of something that is meant to be flat. Halve $L_s$ and $C_s$ and double $N$
and the cutoff doubles while the total delay stays put; the ringing shrinks and the
model creeps toward the line it is impersonating.

## Where the lossless line stops holding

Everything above dropped the series resistance $R$ and the shunt conductance $G$. A
real line has both, and their effects appear in this order as a cable gets longer or
a signal gets faster.

Attenuation first. RG-58 loses roughly 0.5 dB per 10 m at 100 MHz, so the 30 m reel
takes about 1.5 dB out of a signal each way — invisible on a step trace, ruinous on a
100 m run.

Then dispersion. $R$ is dominated by the skin effect and grows as $\sqrt{f}$, which
makes the attenuation frequency-dependent and therefore smears edges: the reel that
returned a clean step at 303 ns returns a rounded one at 300 m.

Then $Z_0$ itself. The full result is $Z_0 = \sqrt{(R + j\omega L)/(G + j\omega C)}$,
which collapses to $\sqrt{L/C}$ only when $\omega L \gg R$. At 1 kHz on a long
telephone pair that condition fails badly and $Z_0$ is complex and frequency
dependent — which is the regime the telegrapher equations were actually invented for,
and the reason Heaviside's loading coils worked.

Above a few megahertz on a metre or a hundred of coax, none of that matters and
$Z_0 = \sqrt{L/C}$ with $v_p = 1/\sqrt{LC}$ is accurate to a percent or better. That
is the model the rest of this course is built on.
''',
                },
            ],
            "quiz": {
                "title": "What the scope was measuring for 303 nanoseconds",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A 1 V step from a generator with a 50 Ω source resistance is applied to a long cable whose far end is open. The near end sits at 0.50 V for the whole time before the reflection returns. What did that plateau measure?",
                        "opts": [
                            "The characteristic impedance of the cable, which is 50 Ω",
                            "The series resistance of the copper, which is 50 Ω",
                            "The open circuit at the far end of the cable",
                            "Nothing about the cable; a scope always halves the amplitude it is shown",
                        ],
                        "a": 0,
                        "whys": [
                            r"Half the source behind a 50 Ω resistance means the load is drawing what a 50 Ω resistor draws, and for that whole window the only thing connected is the line.",
                            r"You have found a real 50 Ω in the wrong component: 30 m of RG-58 has under a tenth of an ohm of series copper, and a resistance that large would make the trace sag along the cable instead of holding flat.",
                            r"This is the answer the far end will give, and it has not given it yet — the plateau *ends* at the moment the far end's reply arrives, and everything before that is the line speaking for itself.",
                            r"A scope does load the node, and a 1 MΩ probe across a 50 Ω source shifts the reading by about five parts in a hundred thousand rather than by a factor of two.",
                        ],
                        "why": r"""
A half-amplitude step behind a 50 Ω source means the load is drawing the current a
50 Ω resistor would draw, and for the whole round-trip time the only thing connected
is the cable — so the cable is the 50 Ω, and $Z_0 = \sqrt{L/C}$ is what was measured.
The copper is not the answer: its series resistance is under a tenth of an ohm, and
if it were 50 Ω the trace would decay along the line rather than stay flat. The far
end is not the answer either, and that is the whole surprise — the far end's reply
has not arrived yet, and until it does the near end cannot know an end exists. A
scope loading the node would be a genuine measurement error, but a 1 MΩ probe across
a 50 Ω source changes the reading by 0.005%.
""",
                    },
                    {
                        "q": "A cable is redesigned so that both $L$ and $C$ per metre are doubled. What happens to $Z_0$ and to $v_p$?",
                        "opts": [
                            "$Z_0$ is unchanged and $v_p$ halves",
                            "$Z_0$ doubles and $v_p$ is unchanged",
                            "Both of them double",
                            "$Z_0$ halves and $v_p$ doubles",
                        ],
                        "a": 0,
                        "whys": [
                            r"$Z_0$ is a ratio and survives the doubling untouched; $v_p$ is built on the product, which quadruples, so the speed falls by two.",
                            r"More inductance does raise $Z_0$ when $C$ is held still, and that reflex is the whole trap here — $C$ doubled as well, and the ratio the two of them sit in did not move.",
                            r"Nothing here can rise. A line that is heavier in both quantities is a slower line, and the product sits in the denominator of $v_p = 1/\sqrt{LC}$.",
                            r"Both formulae are inverted at once, which usually comes from misremembering $Z_0$ as $\sqrt{C/L}$ and $v_p$ as $\sqrt{LC}$ rather than its reciprocal.",
                        ],
                        "why": r"""
$Z_0 = \sqrt{L/C}$ depends on the *ratio*, which doubling both leaves alone, while
$v_p = 1/\sqrt{LC}$ depends on the *product*, which doubling both multiplies by four —
so the velocity falls by a factor of two. The tempting answer is that a bigger $L$
means a bigger impedance, and it does when $C$ is held fixed; here it is not.
Splitting the two formulae by what they depend on is the most useful thing to carry
away from them: one is a ratio, one is a product, and every cable design trade runs
along that split. Dielectric loading is exactly this move — filling the line with
$\varepsilon_r = 2.3$ multiplies $C$ alone, dropping $v_p$ by 1.52 and $Z_0$ with it.
""",
                    },
                    {
                        "q": "Why does a 100 m reel of RG-58 have the same 50 Ω characteristic impedance as a 2 m patch lead cut from it?",
                        "opts": [
                            "Length never enters the derivation; $Z_0$ comes from $L$ and $C$ per metre",
                            "It does not — a longer line has a proportionally higher $Z_0$",
                            "Both reels are terminated in 50 Ω instruments at each end",
                            "Because the total $L$ and the total $C$ both scale with the length and cancel",
                        ],
                        "a": 0,
                        "whys": [
                            r"The algebra ran on a slice of length $dz$ and never mentioned how much cable there was, so $Z_0$ is a property of the cross-section.",
                            r"This confuses $Z_0$ with the total series inductance or the total shunt capacitance, both of which genuinely do grow with length — but neither of those is the quantity a travelling wave sees.",
                            r"Terminations are the one thing that cannot be responsible: an unterminated reel lying in its box has the same $Z_0$, which is exactly what the open-ended trace demonstrated.",
                            r"Right conclusion by the wrong route, and the route matters — there is no total to cancel in a derivation done on an infinitesimal slice, which is why the argument survives on a line that is 3 m at one end and 300 m at the other.",
                        ],
                        "why": r"""
$Z_0 = \sqrt{L/C}$ is built from two per-metre quantities and the algebra that
produced it never mentioned how much cable there is, so $Z_0$ is a property of the
cross-section: the conductor diameters and the dielectric between them. Cancelling
totals gets the right answer for the wrong reason — the totals do scale together and
their ratio is unchanged, but the derivation ran on a slice of length $dz$ and had no
total to cancel, which is why the argument still works for a line that is 3 m at one
end and 300 m at the other. Terminations have nothing to do with it: $Z_0$ exists
before either end is connected, and an unterminated line has it too.
""",
                    },
                    {
                        "q": "The same open-ended 30 m reel is measured again, but the generator now drives a much slower step, with a rise time of 10 µs. What does the near end show?",
                        "opts": [
                            "A single rise to 1 V; the 303 ns round trip is buried inside the edge",
                            "The same 0.5 V plateau, held for 303 ns before it rises",
                            "A 0.5 V plateau lasting 10 µs, since the plateau follows the rise time",
                            "Nothing at all, because a slow edge cannot propagate on a line",
                        ],
                        "a": 0,
                        "whys": [
                            r"The reflection still returns at 303 ns, but the source has moved by well under a percent of its swing by then, so what reaches the screen is one smooth rise.",
                            r"The round trip really is unchanged, and that is what makes this tempting — the trap is assuming it stays *visible*, when the feature it creates is a thirtieth of a percent of the width of the edge hiding it.",
                            r"The plateau lasts as long as it takes the wave to go and come back, and neither the length of the cable nor the speed on it knows anything about how fast the generator switches.",
                            r"Slow signals propagate perfectly well: a mains cable at 50 Hz is a transmission line too, with a round trip that is invisible for precisely the reason above.",
                        ],
                        "why": r"""
The round trip is still 303 ns, but the source takes 10 µs to change, so the
reflection is back and the line is in its steady state long before the edge has
finished rising. The plateau is still there in principle and is invisible in
practice: what the scope draws is one smooth rise to 1 V, the answer a lumped-circuit
picture would have given. This is the actual criterion for when transmission-line
behaviour matters — not the length of the line but the length compared with the
rise time. A 30 m reel is a transmission line to a 1 ns edge and a lumped capacitor
of about 3 nF to a 10 µs one, and the same cable is both on the same afternoon.
""",
                    },
                    {
                        "q": "In the ladder simulation the far end is open, and its voltage peaks at 2.42 V for a 1 V step. Which part of that is the model rather than the physics?",
                        "opts": [
                            "The 0.42 of overshoot, which is the discrete ladder ringing at its cutoff",
                            "The whole 2.42 V, since a passive line cannot exceed its input",
                            "None of it; a lossless open-ended line doubles and then rings",
                            "The doubling, which appears only because the source resistance here is zero",
                        ],
                        "a": 0,
                        "whys": [
                            r"A chain of finite $L_s$ and $C_s$ is a low-pass filter with a corner at $2/\sqrt{L_sC_s}$, and a step pushed through a corner overshoots before it settles.",
                            r"The instinct that a passive network cannot exceed its input is sound about power and wrong about voltage: the doubled voltage arrives with zero current beside it, so no extra energy appears anywhere.",
                            r"The doubling is physics and the ringing is not — a real line has no cutoff to ring at, which is precisely what taking $dz \to 0$ removes from the model.",
                            r"The source resistance decides how much of the step is launched, not what the far end does with it once it arrives; an open end reflects with $\Gamma = +1$ whatever is driving the other end.",
                        ],
                        "why": r"""
The doubling to 2 V is real: an open end forces the current to zero, so the reflected
wave must cancel the incident current, and cancelling in current means adding in
voltage. The extra 0.42 is the ladder. A chain of discrete $L_s$ and $C_s$ is a
low-pass filter with a cutoff at $2/\sqrt{L_sC_s}$, and a step through a filter with
a corner rings — which is why the lab accepts any peak between 1.9 and 2.6 rather
than demanding 2.0. Exceeding the input is not the giveaway it looks like: a passive
network can double a step without generating energy, because the doubled voltage
comes with zero current and so carries no extra power. Halve the section values,
double the count, and the overshoot shrinks while the doubling stays exactly where it
is.
""",
                    },
                    {
                        "q": "The open far end of the 30 m reel is replaced with a 50 Ω terminator. What does the near-end trace do?",
                        "opts": [
                            "It rises to 0.5 V and stays there, with nothing arriving at 303 ns",
                            "It rises to 0.5 V and then falls to 0 V at 303 ns",
                            "It rises to 1 V immediately, because a matched line presents no divider",
                            "It rises to 0.5 V and climbs to 1 V at 303 ns, as before",
                        ],
                        "a": 0,
                        "whys": [
                            r"A matched load draws precisely the current that more line would have drawn, so there is nothing to reflect and no event to wait for.",
                            r"That is what a *short* does: its reflection inverts, and the returning wave cancels the outgoing one at the near end. A resistor equal to $Z_0$ is the one termination that reflects neither way.",
                            r"The divider is formed by the source resistance and the line's own $Z_0$, and it is there from the first instant whether or not the far end is matched.",
                            r"This carries the open-circuit trace over unchanged, which is the reflex worth breaking — making the 303 ns event disappear is the entire point of fitting the terminator.",
                        ],
                        "why": r"""
The wave reaching a 50 Ω terminator finds a load drawing exactly the current more
line would have drawn, so there is nothing to reflect and no event at 303 ns at all —
the near end holds 0.5 V for as long as the source does. The trace that falls to zero
is what a *short* gives, where the reflection inverts and cancels; the trace that
climbs to 1 V is the open circuit that was measured first. An immediate rise to 1 V
never happens with a 50 Ω source into a 50 Ω line, matched or not, because the source
resistance and the line form a divider from the first instant. That flat 0.5 V is
what the build exercise is checking when it asks for a flat response from 1 to 8 MHz.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "One LC section, and why a line is not one",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 0.7, "K": 1},
                "brief": r'''
A transmission line is usually drawn as a ladder of series inductors and shunt
capacitors. Cut one section out of that ladder and terminate it, and you get an
ordinary second-order low-pass: a corner at $\omega_n = 1/\sqrt{LC}$, a damping set by
the termination, and a gain $K$.

That is what these two plots show. The point of the sandbox is what the single
section gets *wrong* about a line — a real line is the limit in which each section
carries an infinitesimal $L$ and $C$, so its corner runs off to infinity and the flat
region is all there is.
''',
                "notice": [
                    "Take $\\zeta$ down to 0.05. The amber dot on the corner reads $20\\log_{10}(K/2\\zeta) = 20$ dB, twenty above the low-frequency gain. One lightly loaded section resonates; a line, which is a cascade of infinitely many infinitesimal ones, does not.",
                    "Now drag $\\zeta$ from 0.05 all the way to 1.5 and watch the phase plot. The curve crosses the dashed $-90°$ line at the corner every single time — the damping changes how abruptly it gets there and nothing else.",
                    "Raise $\\omega_n$ from 20 to 200. Both curves slide one decade to the right with their shapes untouched, because the corner is the only frequency scale the section has. Making $L$ and $C$ per section smaller is exactly this move, and a line is where it ends up.",
                ],
            },
            "derive": {
                "title": "From a slice of line to a wave",
                "minutes": 14,
                "vars": ["L", "C", "R", "G", "Z_0", "v_p", "z", "t", "omega", "d"],
                "brief": r'''
Take a slice of line of length $dz$. Its series inductance is $L\,dz$ and its shunt
capacitance is $C\,dz$, where $L$ and $C$ are per-unit-length quantities. KVL round
the slice and KCL at its far node give the telegrapher equations for a lossless line:

$$\frac{\partial V}{\partial z} = -L\frac{\partial I}{\partial t}, \qquad
  \frac{\partial I}{\partial z} = -C\frac{\partial V}{\partial t}$$

Everything below follows from those two.
''',
                "steps": [
                    {
                        "prompt": "Differentiate the first equation with respect to $z$ and the second with respect to $t$, then eliminate $I$. You get $\\partial^2 V/\\partial z^2 = \\kappa\\,\\partial^2 V/\\partial t^2$. Write the constant $\\kappa$.",
                        "answer": "L C",
                        "hint": "Each equation contributes one factor. Nothing else in the pair can carry units.",
                        "deconstruct": [
                            "$\\partial^2 V/\\partial z^2 = -L\\,\\partial^2 I/\\partial z \\partial t$.",
                            "Substituting $\\partial I/\\partial z = -C\\,\\partial V/\\partial t$ turns the right-hand side into $LC\\,\\partial^2 V/\\partial t^2$.",
                        ],
                    },
                    {
                        "prompt": "The wave equation $\\partial^2 V/\\partial z^2 = (1/v_p^2)\\,\\partial^2 V/\\partial t^2$ has solutions $V(z \\mp v_p t)$. Write the phase velocity $v_p$ in terms of $L$ and $C$.",
                        "given": "You just found that the constant in front of the time derivative is $LC$.",
                        "answer": "\\frac{1}{\\sqrt{L C}}",
                        "hint": "Match the two forms of the same equation: $1/v_p^2 = LC$.",
                        "deconstruct": [
                            "Comparing coefficients, $1/v_p^2 = LC$.",
                            "So $v_p^2 = 1/(LC)$, and the speed is its positive square root.",
                        ],
                    },
                    {
                        "prompt": "For a wave travelling in $+z$ only, substitute $V = f(t - z/v_p)$ into the first telegrapher equation and you find $V/I$ is a constant. Write that characteristic impedance $Z_0$ in terms of $L$ and $C$.",
                        "answer": "\\sqrt{\\frac{L}{C}}",
                        "hint": "It has units of ohms, so $L$ must be over $C$, and $v_p$ has already used up the product.",
                        "deconstruct": [
                            "With $V = f(t - z/v_p)$, $\\partial V/\\partial z = -(1/v_p)f'$ and $\\partial I/\\partial t = g'$ where $I = g(t - z/v_p)$.",
                            "The first equation then gives $f'/v_p = L g'$, so $V/I = L v_p = L/\\sqrt{LC} = \\sqrt{L/C}$.",
                        ],
                    },
                    {
                        "prompt": "In practice you measure $Z_0$ and $v_p$ and want the line parameters back. Write $C$ in terms of $Z_0$ and $v_p$.",
                        "answer": "\\frac{1}{Z_0 v_p}",
                        "hint": "Multiply $Z_0$ by $v_p$ and see which parameter cancels.",
                        "deconstruct": [
                            "$Z_0 v_p = \\sqrt{L/C}\\cdot 1/\\sqrt{LC} = 1/C$.",
                            "So $C = 1/(Z_0 v_p)$, and by the same trick $L = Z_0/v_p$.",
                        ],
                    },
                ],
                "closing": r'''
Two per-unit-length numbers, two derived ones, and a change of variables between
them. Note what never appeared: the length of the line. A line has a characteristic
impedance and a velocity before you have decided how long it is, which is why $Z_0$
is a property of the cross-section alone.
''',
            },
            "build": {
                "title": "A line, made of eight components",
                "minutes": 26,
                "brief": r"""
The derivation treats $L$ and $C$ as *per unit length* and takes a limit. A real
simulation cannot take that limit, so it chops the line into sections — and four
sections is already enough to behave like a line over a useful band.

## What is on the canvas

A 1 V source behind a 100 Ω source resistance, then four identical sections of
**1 µH series inductance and 100 pF shunt capacitance**. The far end is open, which
means the line is unterminated and every wave that reaches the end comes straight back.

## What to add

One resistor from the far end to ground, and the probe on that node.

The value is the one number this module is about. A section has $L = 1$ µH and
$C = 100$ pF, so

$$Z_0 = \sqrt{L/C}$$

and a line terminated in its own characteristic impedance cannot tell the difference
between the resistor and more line. Nothing comes back.

## What the checks measure

- At DC the inductors are wire and the capacitors are gaps, so the whole thing is your
  resistor and the 100 Ω source resistance in series: the probe must read exactly half
  the source. That pins the value.
- The one that matters: the response must be **flat** from 1 MHz to 8 MHz. A line
  terminated in anything else builds standing waves, and the standing waves put peaks
  and nulls in that band. Flatness is not a coincidence of the value — it *is* the
  matched condition.
- The phase at 2 MHz gives the delay. Each section is $\sqrt{LC} = 10$ ns, so four of
  them are 40 ns, and 40 ns at 2 MHz is $-28.8°$. That number is the line's length
  expressed the only way a network analyser can see it.

## Where the model stops

Push the frequency up and the ladder stops behaving like a line: a real line passes
everything, but four lumped sections have a cutoff near $1/(\pi\sqrt{LC}) = 32$ MHz
and fall apart above it. The checks stay well below that on purpose. If you want the
model good to a higher frequency, the fix is more sections of smaller $L$ and $C$ —
which is the limit the derivation took, approached one step at a time.
""",
                "start": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "rs", "kind": "R", "x": 4, "y": 5, "rot": 0, "value": 100},
                        {"id": "l1", "kind": "L", "x": 7, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c1", "kind": "C", "x": 8, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g1", "kind": "GND", "x": 8, "y": 9},
                        {"id": "l2", "kind": "L", "x": 11, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c2", "kind": "C", "x": 12, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g2", "kind": "GND", "x": 12, "y": 9},
                        {"id": "l3", "kind": "L", "x": 15, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c3", "kind": "C", "x": 16, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g3", "kind": "GND", "x": 16, "y": 9},
                        {"id": "l4", "kind": "L", "x": 19, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c4", "kind": "C", "x": 20, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g4", "kind": "GND", "x": 20, "y": 9},
                        {"id": "g5", "kind": "GND", "x": 23, "y": 9},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]}, {"a": [2, 5], "b": [3, 5]},
                        {"a": [5, 5], "b": [6, 5]},
                        {"a": [8, 5], "b": [8, 6]}, {"a": [8, 8], "b": [8, 9]},
                        {"a": [8, 5], "b": [10, 5]},
                        {"a": [12, 5], "b": [12, 6]}, {"a": [12, 8], "b": [12, 9]},
                        {"a": [12, 5], "b": [14, 5]},
                        {"a": [16, 5], "b": [16, 6]}, {"a": [16, 8], "b": [16, 9]},
                        {"a": [16, 5], "b": [18, 5]},
                        {"a": [20, 5], "b": [20, 6]}, {"a": [20, 8], "b": [20, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "rs", "kind": "R", "x": 4, "y": 5, "rot": 0, "value": 100},
                        {"id": "l1", "kind": "L", "x": 7, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c1", "kind": "C", "x": 8, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g1", "kind": "GND", "x": 8, "y": 9},
                        {"id": "l2", "kind": "L", "x": 11, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c2", "kind": "C", "x": 12, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g2", "kind": "GND", "x": 12, "y": 9},
                        {"id": "l3", "kind": "L", "x": 15, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c3", "kind": "C", "x": 16, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g3", "kind": "GND", "x": 16, "y": 9},
                        {"id": "l4", "kind": "L", "x": 19, "y": 5, "rot": 0, "value": 1e-6},
                        {"id": "c4", "kind": "C", "x": 20, "y": 7, "rot": 1, "value": 100e-12},
                        {"id": "g4", "kind": "GND", "x": 20, "y": 9},
                        {"id": "rl", "kind": "R", "x": 23, "y": 7, "rot": 1, "value": 100},
                        {"id": "g5", "kind": "GND", "x": 23, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 23, "y": 5},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]}, {"a": [2, 5], "b": [3, 5]},
                        {"a": [5, 5], "b": [6, 5]},
                        {"a": [8, 5], "b": [8, 6]}, {"a": [8, 8], "b": [8, 9]},
                        {"a": [8, 5], "b": [10, 5]},
                        {"a": [12, 5], "b": [12, 6]}, {"a": [12, 8], "b": [12, 9]},
                        {"a": [12, 5], "b": [14, 5]},
                        {"a": [16, 5], "b": [16, 6]}, {"a": [16, 8], "b": [16, 9]},
                        {"a": [16, 5], "b": [18, 5]},
                        {"a": [20, 5], "b": [20, 6]}, {"a": [20, 8], "b": [20, 9]},
                        {"a": [20, 5], "b": [23, 5]}, {"a": [23, 5], "b": [23, 6]},
                        {"a": [23, 8], "b": [23, 9]},
                    ],
                },
                "checks": [
                    {
                        "name": "one terminating resistor, and the DC divider it makes",
                        "code": r"""
c.assert(c.count('R') === 2,
  'There should be two resistors: the 100 ohm source resistance already on the canvas ' +
  'and the one you add at the far end. There are ' + c.count('R') + '.');
c.close(c.vout(), 0.5, 0.02,
  'the probed node at DC. At DC every inductor is a wire and every capacitor is an ' +
  'open circuit, so the source resistance and your terminator form a plain divider. ' +
  'Half the source means the two are equal');
""",
                    },
                    {
                        "name": "flat from 1 MHz to 8 MHz — no standing waves",
                        "code": r"""
const fs = [1e6, 2e6, 4e6, 6e6, 8e6];
const g = fs.map(function (f) { return c.gain(f); });
let lo = g[0], hi = g[0];
for (let i = 1; i < g.length; i++) { if (g[i] < lo) lo = g[i]; if (g[i] > hi) hi = g[i]; }
c.assert(hi / lo < 1.10,
  'The response varies from ' + c.fmt(lo, 'V') + ' to ' + c.fmt(hi, 'V') + ' across ' +
  '1-8 MHz, a ripple of ' + ((hi / lo - 1) * 100).toFixed(0) + '%. That ripple is a ' +
  'standing wave: part of every wave is coming back off the far end and interfering ' +
  'with the wave still going out. Terminate in sqrt(L/C) and there is nothing to ' +
  'come back.');
c.close(g[2], 0.5, 0.06, 'the level at 4 MHz, which for a matched line is the same 0.5 as at DC');
""",
                    },
                    {
                        "name": "four sections of 10 ns each: -28.8 degrees at 2 MHz",
                        "code": r"""
const ph = c.phase(2e6);
c.close(ph, -28.8, 0.15,
  'the phase at 2 MHz. Each section delays by sqrt(L*C) = 10 ns, so four sections are ' +
  '40 ns, and 40 ns at 2 MHz is 0.08 of a cycle: -28.8 degrees. A phase near zero ' +
  'means the sections are not in series; a much larger one means the line is longer ' +
  'than four sections');
""",
                    },
                    {
                        "name": "the delay is proportional to frequency, as a line's must be",
                        "code": r"""
const p1 = c.phase(1e6), p2 = c.phase(2e6), p3 = c.phase(3e6);
c.close(p2 / p1, 2.0, 0.08,
  'the ratio of phase at 2 MHz to phase at 1 MHz. A delay gives phase proportional ' +
  'to frequency, so doubling the frequency must double the phase');
c.close(p3 / p1, 3.0, 0.10,
  'the same test at 3 MHz. Departure from a straight line here is dispersion — the ' +
  'ladder is not a real line and starts to show it as the frequency climbs toward ' +
  'the section cutoff');
""",
                    },
                ],
                "hints": [
                    "$Z_0 = \\sqrt{L/C}$ with $L = 1\\ \\mu$H and $C = 100$ pF. Do the division before the square root and the numbers stay friendly.",
                    "The far end of the line is the right-hand end of the fourth inductor, at the same node as the fourth shunt capacitor.",
                    "The probe goes on that same node — it is the load voltage you are measuring, not the voltage across anything else.",
                ],
            },
            "lab": {
                "title": "Simulate a line as a ladder of LC sections",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Four functions.

`characteristic_impedance(Ls, Cs)` and `section_delay(Ls, Cs)` return $\sqrt{L_s/C_s}$
and $\sqrt{L_s C_s}$ for one section of the ladder.

`ladder_cutoff(Ls, Cs)` returns $2/\sqrt{L_s C_s}$ in radians per second. That is the
frequency above which a constant-k LC ladder stops propagating altogether — take it
as given here; it is the discrete artefact that a real line does not have.

`simulate(Ls, Cs, N, dt, steps, v_in)` leapfrogs the ladder. There are `N + 1` node
voltages `v[0..N]` and `N` branch currents `i[0..N-1]`, where `i[k]` flows from node
`k` to node `k+1`. Node 0 is held at `v_in` by an ideal source and node `N` is open.
Each step, in this order:

```text
v[0] = v_in
record v[N]
i[k]  += (dt / Ls) * (v[k] - v[k+1])          for every k
v[k]  += (dt / Cs) * (i[k-1] - i[k])          for k = 1 .. N-1
v[N]  += (dt / Cs) * i[N-1]
```

Return the recorded `v[N]` values as a list of floats. Write the current and voltage
updates as whole-array numpy operations rather than Python loops if you can.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def characteristic_impedance(Ls, Cs):
    """Return sqrt(Ls / Cs), the impedance a travelling wave sees."""
    # TODO
    return 0.0


def section_delay(Ls, Cs):
    """Return sqrt(Ls * Cs), the time one section takes to pass the wave on."""
    # TODO
    return 0.0


def ladder_cutoff(Ls, Cs):
    """Return 2 / sqrt(Ls * Cs) rad/s, above which the ladder stops propagating."""
    # TODO
    return 0.0


def simulate(Ls, Cs, N, dt, steps, v_in):
    """Leapfrog the ladder and return the far-end voltage at every step."""
    v = np.zeros(N + 1)
    i = np.zeros(N)
    out = []
    # TODO: hold node 0 at v_in, record v[N], then advance the currents and voltages.
    return out


if __name__ == "__main__":
    Ls, Cs = 1.0, 0.25
    print("Z0 =", characteristic_impedance(Ls, Cs))
    print("delay per section =", section_delay(Ls, Cs))
    print("cutoff =", ladder_cutoff(Ls, Cs), "rad/s")
    ys = simulate(Ls, Cs, 20, 0.01, 4000, 1.0)
    if ys:
        print("peak far-end voltage:", round(max(ys), 4))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def characteristic_impedance(Ls, Cs):
    """Return sqrt(Ls / Cs), the impedance a travelling wave sees."""
    return float(np.sqrt(Ls / Cs))


def section_delay(Ls, Cs):
    """Return sqrt(Ls * Cs), the time one section takes to pass the wave on."""
    return float(np.sqrt(Ls * Cs))


def ladder_cutoff(Ls, Cs):
    """Return 2 / sqrt(Ls * Cs) rad/s, above which the ladder stops propagating."""
    return 2.0 / float(np.sqrt(Ls * Cs))


def simulate(Ls, Cs, N, dt, steps, v_in):
    """Leapfrog the ladder and return the far-end voltage at every step."""
    v = np.zeros(N + 1)
    i = np.zeros(N)
    out = []
    for _ in range(steps):
        v[0] = v_in
        out.append(float(v[N]))
        i += (dt / Ls) * (v[:-1] - v[1:])
        v[1:N] += (dt / Cs) * (i[:N - 1] - i[1:])
        v[N] += (dt / Cs) * i[N - 1]
    return out


if __name__ == "__main__":
    Ls, Cs = 1.0, 0.25
    print("Z0 =", characteristic_impedance(Ls, Cs))
    print("delay per section =", section_delay(Ls, Cs))
    print("cutoff =", ladder_cutoff(Ls, Cs), "rad/s")
    ys = simulate(Ls, Cs, 20, 0.01, 4000, 1.0)
    if ys:
        print("peak far-end voltage:", round(max(ys), 4))
'''}],
                "hints": [
                    "`np.sqrt` on two Python floats returns a numpy scalar; wrap it in `float()` so the checks compare cleanly.",
                    "`v[:-1] - v[1:]` is the voltage across every inductor at once, and it already has length `N`.",
                    "Record `v[N]` *before* the updates, so the first sample is the far end at rest.",
                    "The far end is open, so its capacitor is charged by `i[N-1]` alone with nothing draining it — that is why it gets its own line.",
                ],
                "tests": [
                    {"name": "characteristic impedance is the root of the L to C ratio", "code": r'''
_z = characteristic_impedance(1.0, 0.25)
assert abs(_z - 2.0) < 1e-12, f"sqrt(1.0/0.25) is 2.0, got {_z}"
_z50 = characteristic_impedance(1e-6, 400e-12)
assert abs(_z50 - 50.0) < 1e-9, \
    f"1 uH and 400 pF per section is a 50 ohm line, got {_z50}"
'''},
                    {"name": "one section delays by the root of the L C product", "code": r'''
_d = section_delay(1.0, 0.25)
assert abs(_d - 0.5) < 1e-12, f"sqrt(1.0*0.25) is 0.5, got {_d}"
assert abs(section_delay(4.0, 4.0) - 4.0) < 1e-12, \
    "the delay is the square root of the product, not the product"
'''},
                    {"name": "the ladder cutoff is two over the section delay", "code": r'''
_wc = ladder_cutoff(1.0, 0.25)
assert abs(_wc - 4.0) < 1e-12, f"2/sqrt(1.0*0.25) is 4.0 rad/s, got {_wc}"
_prod = ladder_cutoff(1e-6, 400e-12) * section_delay(1e-6, 400e-12)
assert abs(_prod - 2.0) < 1e-9, \
    f"cutoff times section delay is exactly 2 for any Ls and Cs, got {_prod}"
'''},
                    {"name": "the far end stays quiet until the wave gets there", "code": r'''
_ys = simulate(1.0, 0.25, 20, 0.01, 4000, 1.0)
assert len(_ys) == 4000, f"expected one sample per step, got {len(_ys)}"
assert abs(_ys[0]) < 1e-12, f"the far end starts at rest, got {_ys[0]}"
assert abs(_ys[500]) < 1e-6, \
    f"at t=5 the wave is only half way down 20 sections, so v[N] should still be ~0, got {_ys[500]}"
assert max(_ys[:900]) < 0.1, \
    "nothing should reach the far end before roughly N*sqrt(Ls*Cs) = 10"
'''},
                    {"name": "the step arrives one section delay per section", "code": r'''
import numpy as np
_ys = np.array(simulate(1.0, 0.25, 20, 0.01, 4000, 1.0))
assert _ys.max() > 0.5, "the step never arrived at all"
_t = int(np.argmax(_ys > 0.5)) * 0.01
assert abs(_t - 10.0) < 0.2, \
    f"20 sections at 0.5 each means arrival near t=10, got t={_t}"
'''},
                    {"name": "an open far end doubles the incident step", "code": r'''
_ys = simulate(1.0, 0.25, 20, 0.01, 4000, 1.0)
_peak = max(_ys)
assert 1.9 < _peak < 2.6, \
    f"an open circuit reflects with Gamma=+1, so v[N] should peak near 2, got {_peak:.4f}"
'''},
                    {"name": "a heavier line delivers the step later", "code": r'''
import numpy as np
_fast = np.array(simulate(1.0, 0.25, 20, 0.01, 4000, 1.0))
_slow = np.array(simulate(1.0, 1.00, 20, 0.01, 4000, 1.0))
assert _slow.max() > 0.5, "the slower line never delivered the step inside 4000 steps"
_tf = int(np.argmax(_fast > 0.5)) * 0.01
_ts = int(np.argmax(_slow > 0.5)) * 0.01
assert abs(_ts - 20.0) < 0.4, f"quadrupling Cs doubles the delay to about 20, got {_ts}"
assert _ts > _tf * 1.8, \
    f"more capacitance per section means a slower wave: {_ts} should be about twice {_tf}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Reflection, VSWR and matching",
            "summary": "A load that is not Z0 sends part of the wave back. Where that reflection sits depends on where you stand.",
            "concepts": [
                "The reflection coefficient $\\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$ comes from one boundary condition at the load.",
                "Standing waves: the incident and reflected waves interfere, and the ratio of the envelope's maximum to its minimum is the VSWR.",
                "Return loss $-20\\log_{10}|\\Gamma|$ is the same statement in decibels, and $|\\Gamma|^2$ is the fraction of power sent back.",
                "Input impedance rotates with distance: $Z_{in} = Z_0(Z_L + jZ_0\\tan\\beta d)/(Z_0 + jZ_L\\tan\\beta d)$, with period $\\lambda/2$.",
                "A quarter-wave section of impedance $\\sqrt{Z_0 Z_L}$ matches a real load, and only at the one frequency where it is a quarter wave.",
            ],
            "read": [
                {
                    "title": "A probe sliding down a slotted line, and what it finds",
                    "minutes": 16,
                    "body": r'''
On the bench is a 50 Ω air-dielectric slotted line: a rigid coaxial section with a
narrow slot milled along the outer conductor, and a crystal detector on a carriage
that slides down the slot with a millimetre scale beside it. A signal generator drives
one end at 1.5 GHz. The far end is an unknown load — a patch antenna on a short pigtail.

Wind the carriage from one end to the other and the detector does not read a constant
level. It reads a pattern, fixed in space, that does not move while you watch it. Three numbers
come off the scale. The envelope rises to **148 mV** at its peaks and falls to
**51.5 mV** at its troughs; adjacent troughs are **99.9 mm** apart; and the first
trough is **57.9 mm** back from the plane where the load is connected.

That pattern should be unsettling. A wave that goes one way has a constant amplitude
everywhere; there is nothing for it to interfere with. A pattern nailed to the metal
means two waves, going opposite ways.

## Where the second wave comes from

At the load plane the total voltage is the sum of the incident and reflected waves and
the total current is their difference over $Z_0$ — a difference, because the reflected
wave carries its current backwards:

$$V = V_i + V_r, \qquad I = \frac{V_i - V_r}{Z_0}$$

The load imposes one condition, $V/I = Z_L$. Substituting and collecting the two
amplitudes on opposite sides gives $V_i(Z_L - Z_0) = V_r(Z_L + Z_0)$, so

$$\Gamma \equiv \frac{V_r}{V_i} = \frac{Z_L - Z_0}{Z_L + Z_0}$$

One boundary condition, one line of algebra, and everything else in this module
follows from it. The derivation *The reflection coefficient and the quarter-wave
transformer* runs the same steps as a sequence you complete yourself. Two special
cases are worth fixing now: $Z_L = Z_0$ gives $\Gamma = 0$ and there is no second
wave at all, and $Z_L = \infty$ gives $\Gamma = +1$, the total in-phase reflection
that put the far end of module 1's open reel at twice the incident voltage.

## Why the pattern stands still

A distance $d$ back from the load, the incident wave has advanced in phase by $\beta d$
and the reflected wave has retreated by the same amount, so

$$V(d) = V_i\left(e^{j\beta d} + \Gamma e^{-j\beta d}\right),
\qquad |V(d)| = |V_i|\,\bigl|1 + \Gamma e^{-2j\beta d}\bigr|$$

As $d$ increases, $\Gamma e^{-2j\beta d}$ walks around a circle of radius $|\Gamma|$
centred on the origin. The magnitude being measured is the distance from the point
$-1$ to that walking point, so it swings between $1 + |\Gamma|$ and $1 - |\Gamma|$
times $|V_i|$ and then repeats. Two things fall out at once.

The ratio of the envelope's peak to its trough carries no $|V_i|$ in it:

$$s = \frac{1 + |\Gamma|}{1 - |\Gamma|}$$

and the pattern repeats when $2\beta d$ has advanced by $2\pi$, which is every half
wavelength. That is the second measurement above: troughs 99.9 mm apart means
$\lambda = 199.8$ mm, and $c/\lambda$ is 1.5004 GHz. The slotted line measures the
generator's frequency as a side effect of measuring anything else.

Run the ratio backwards, $|\Gamma| = (s - 1)/(s + 1)$, and the phase from the position
of the trough — a trough is where $\Gamma e^{-2j\beta d}$ points at $-1$, so
$\theta - 2\beta d = -\pi$ — and the load itself comes back out.

```python
import cmath
import math

z0 = 50.0
v_max, v_min = 148e-3, 51.5e-3   # probe envelope, in volts
lam = 0.1998                     # twice the spacing of adjacent minima, in metres
d_min = 0.0579                   # first minimum, measured back from the load plane

s = v_max / v_min
mag = (s - 1.0) / (s + 1.0)
theta = 2.0 * (2.0 * math.pi / lam) * d_min - math.pi
gamma = cmath.rect(mag, theta)
z_l = z0 * (1.0 + gamma) / (1.0 - gamma)

print(f"VSWR    = {s:.3f} : 1")
print(f"|Gamma| = {mag:.4f} at {math.degrees(theta):.1f} degrees")
print(f"Z_L     = {z_l.real:.1f} + {z_l.imag:.1f}j ohm")
```

A VSWR of 2.874, a reflection coefficient of 0.4837 at 28.6°, and a load of
$99.5 + j60.2\ \Omega$. Three readings off a millimetre scale and a diode, and the
complex impedance of an antenna at 1.5 GHz drops out. Nothing in that chain needed a
network analyser, and this is how it was done for forty years. Take the load to be
$100 + j60\ \Omega$ — the last digit of each reading is not worth more than that — and
carry it through the rest of the module.

## What the mismatch actually costs

```python
import cmath
import math

C_LIGHT = 2.99792458e8
z0, z_l, f0 = 50.0, complex(100.0, 60.0), 1.5e9


def z_in(zl, zc, bl):
    """Impedance seen bl radians of lossless line back from zl on a zc line."""
    t = cmath.tan(bl)
    return zc * (zl + 1j * zc * t) / (zc + 1j * zl * t)


g = (z_l - z0) / (z_l + z0)
s = (1 + abs(g)) / (1 - abs(g))
print(f"|Gamma| = {abs(g):.4f}, VSWR = {s:.4f} : 1, "
      f"return loss = {-20 * math.log10(abs(g)):.2f} dB")
print(f"reflected {abs(g) ** 2 * 100:.1f}% of the power, "
      f"delivered {(1 - abs(g) ** 2) * 100:.1f}%")

lam0 = C_LIGHT / f0
d = lam0 * (cmath.phase(g) + math.pi) / (4 * math.pi)
z_min = z_in(z_l, z0, 2 * math.pi * d / lam0)
z1 = math.sqrt(z0 * z_min.real)
print(f"voltage minimum {d * 1e3:.2f} mm back: Z = {z_min.real:.2f} "
      f"{z_min.imag:+.2f}j, against Z0/s = {z0 / s:.2f}")
print(f"the quarter-wave section there must be {z1:.2f} ohm")

for f in (1.35e9, 1.50e9, 1.65e9):
    lam = C_LIGHT / f
    seen = z_in(z_in(z_l, z0, 2 * math.pi * d / lam), z1,
                2 * math.pi * (lam0 / 4) / lam)
    gg = (seen - z0) / (seen + z0)
    print(f"  {f / 1e9:.2f} GHz: |Gamma| = {abs(gg):.4f}, "
          f"VSWR = {(1 + abs(gg)) / (1 - abs(gg)):.3f} : 1")
```

The first two lines are the ones to argue with. $|\Gamma| = 0.4834$, a VSWR of
2.8718:1, a return loss of 6.31 dB — and **23.4% of the power reflected, 76.6%
delivered**.

## The mistake: reading a VSWR as a power loss

A standing wave ratio of nearly three to one sounds ruinous, and the word *loss* in
*return loss* does nothing to help. Both readings are wrong, and they are wrong in
opposite directions.

The VSWR is a ratio of *voltages*, and power goes as voltage squared, so the fraction
of power turned back is $|\Gamma|^2 = 0.234$ rather than anything like $1/2.87$. The
antenna still receives 76.6% of what the generator offered it, which is 1.16 dB of
mismatch loss. Chasing a 2.87:1 VSWR down to 1.5:1 buys back about 1.0 dB — worth
having, rarely worth a redesign, and routinely mistaken for the difference between a
working link and a dead one.

Return loss runs the other way from its name. It is $-20\log_{10}|\Gamma|$, a
*positive* number that gets *larger* as the match gets *better*: 6.31 dB here is
mediocre, 20 dB means $|\Gamma| = 0.1$ and is good, and a perfect match has infinite
return loss because nothing at all comes back. The tell that someone has the sense of
it backwards is a specification asking for "return loss less than 10 dB".

## Where you stand changes what you see

$|\Gamma|$ belongs to the load. Slide the reference plane back along lossless line and
the reflection coefficient rotates — $\Gamma(d) = \Gamma e^{-2j\beta d}$ — but its
magnitude does not move, so the VSWR and the return loss are the same wherever you
measure them. The impedance, on the other hand, changes completely, and repeats every
half wavelength because the phase term carries a factor of two. That is the whole
content of the sandbox *A load, and where a length of line puts it*: sweep its length
control across the full range and the marker makes one revolution of a circle whose
radius is fixed, while the readout underneath never changes.

The consequence people miss is that adding line cannot improve a match. It moves the
impedance around a circle of constant radius; only a lossy line shrinks the circle,
and it does that by throwing the signal away.

## Matching at the voltage minimum

The quarter-wave transformer follows from the input-impedance formula by taking
$\beta d \to \pi/2$, where $\tan\beta d$ grows without bound; divide top and bottom by
the tangent and the terms without one vanish, leaving $Z_{in} = Z_0^2/Z_L$. Run that
backwards and a section of impedance $Z_1$ turns $Z_L$ into $Z_1^2/Z_L$, so setting
$Z_1 = \sqrt{Z_0Z_L}$ makes the load look like $Z_0$.

It matches a *real* load, and $100 + j60$ is not real. But the standing-wave pattern
has already handed over a plane where the impedance is real: at a voltage minimum
$\Gamma e^{-2j\beta d}$ points at $-1$, so
$Z = Z_0(1 - |\Gamma|)/(1 + |\Gamma|) = Z_0/s$, a pure resistance. The block prints
17.41 Ω with an imaginary part that rounds to zero, sitting exactly on $50/2.8718$,
57.85 mm back from the load. A quarter-wave section of $\sqrt{50 \times 17.41} =
29.50\ \Omega$ inserted at that plane matches the antenna to the line, and the sweep
at the end confirms $|\Gamma| = 0.0000$ at 1.5 GHz.

That is the design the lab *Reflection, standing waves and a quarter-wave match*
builds function by function: `reflection`, `vswr`, `return_loss`, `input_impedance`
and `quarter_wave` are the five pieces used above, and one of its tests performs the
same check the last loop performs here — push the load through its own quarter-wave
section and confirm that what comes out reflects nothing.

## Where it stops holding

**Bandwidth.** The sweep is the answer to that, and it is not flattering: 10% away
from the design frequency, in either direction, $|\Gamma|$ has climbed from zero to
0.2968 and the VSWR to 1.844:1. A quarter-wave section is a quarter wave at one
frequency. Broadband matching is the art of buying that back, usually with several
sections whose impedances step gradually instead of once.

**Losing sight of a bad match.** On lossy line $|\Gamma|$ measured at the input is the
load's value attenuated by *twice* the one-way loss, because the reflection makes the
trip in both directions. Ten metres of cable with 3 dB of loss will report a VSWR of
3:1 for a load that is a dead short — an infinite VSWR reading as a mediocre one. A
match measured at the shack end of a long feeder is a measurement of the feeder.

**A load that moves.** The sweep above holds $Z_L$ fixed while the frequency changes,
which no antenna does. A real load drifts as well, and the two effects can either
cancel or compound; the ±10% figure is an optimistic bound, not a prediction.

**One mode, one plane.** All of this assumes a single TEM wave and a load that is a
lumped impedance at one identifiable plane. Change the connector and the phase of
$\Gamma$ moves, though its magnitude does not. Module 3 removes the first assumption
entirely: in a hollow guide there is no TEM wave to be had.
''',
                },
            ],
            "sandbox": {
                "title": "A load, and where a length of line puts it",
                "visualiser": "smith",
                "minutes": 9,
                "initial": {"rl": 100, "xl": 60, "len": 0},
                "brief": r'''
The Smith chart is the complex $\Gamma$ plane with the impedance grid drawn on top of
it. The centre is a perfect match — here the chart is normalised to 50 Ω, so the
centre is 50 Ω exactly. The grey dot is the load. The coloured dot is what you see
after `len` wavelengths of lossless line, and the dashed circle is the path it takes.
''',
                "notice": [
                    "Set $R$ to 50 and $X$ to 0. Both dots collapse onto the centre, the dashed circle shrinks to a point, and the readout gives $|\\Gamma| = 0.000$ with a VSWR of 1.00:1. Now sweep the line length over its whole range: nothing moves at all. A matched load looks identical from every distance.",
                    "Set $R = 100$ and $X = 0$. The load sits on the real axis at $\\Gamma = +1/3$. Take the line length to 0.25 λ and the marker travels exactly half way round the circle to $\\Gamma = -1/3$, landing on the leftmost point of the drawn $r = 0.5$ circle — 25 Ω. A quarter wave turned 100 Ω into $50^2/100$.",
                    "Back to $R = 100$, $X = 60$, and sweep the length from 0 to 0.5 λ. The marker makes one complete revolution and returns to the load, but the readout underneath never changes: $|\\Gamma| = 0.483$, VSWR 2.87:1, throughout. Those belong to the load, and lossless line cannot touch them.",
                ],
            },
            "derive": {
                "title": "The reflection coefficient and the quarter-wave transformer",
                "minutes": 14,
                "vars": ["Z_L", "Z_0", "Z_1", "Z_in", "Gamma", "V_i", "V_r", "s", "d", "beta"],
                "brief": r'''
A line of impedance $Z_0$ ends in a load $Z_L$. Just to the left of the load the total
voltage is the sum of an incident and a reflected wave, and the total current is their
difference divided by $Z_0$, because the reflected wave travels the other way:

$$V = V_i + V_r, \qquad I = \frac{V_i - V_r}{Z_0}$$

The load imposes one condition: $V/I = Z_L$.
''',
                "steps": [
                    {
                        "prompt": "Impose $V/I = Z_L$ and solve for $\\Gamma = V_r/V_i$. Write $\\Gamma$ in terms of $Z_L$ and $Z_0$.",
                        "answer": "\\frac{Z_L - Z_0}{Z_L + Z_0}",
                        "hint": "Write $Z_L = Z_0 (V_i + V_r)/(V_i - V_r)$, then divide top and bottom by $V_i$ and solve.",
                        "deconstruct": [
                            "$Z_L(V_i - V_r)/Z_0 = V_i + V_r$.",
                            "Collect: $V_i(Z_L - Z_0) = V_r(Z_L + Z_0)$.",
                            "Divide to get the ratio.",
                        ],
                    },
                    {
                        "prompt": "Along the line the two waves interfere. Where they add the envelope reaches $|V_i|(1 + |\\Gamma|)$ and where they cancel it drops to $|V_i|(1 - |\\Gamma|)$. Write the standing wave ratio $s$ for a real $\\Gamma$ between 0 and 1.",
                        "answer": "\\frac{1 + \\Gamma}{1 - \\Gamma}",
                        "hint": "It is a ratio of the two envelope values, and $|V_i|$ cancels.",
                        "deconstruct": [
                            "The maximum is $|V_i|(1 + \\Gamma)$ and the minimum is $|V_i|(1 - \\Gamma)$.",
                            "Their ratio drops $|V_i|$ entirely.",
                        ],
                    },
                    {
                        "prompt": "Power in a travelling wave goes as the square of its amplitude. Write the fraction of incident power that comes back, in terms of $\\Gamma$.",
                        "answer": "\\Gamma^2",
                        "placeholder": "\\Gamma^{2}",
                        "hint": "The reflected amplitude is $\\Gamma$ times the incident one, and power is amplitude squared.",
                        "deconstruct": [
                            "$P_r/P_i = |V_r|^2/|V_i|^2$.",
                            "And $V_r = \\Gamma V_i$, so the ratio is $\\Gamma^2$ for real $\\Gamma$.",
                        ],
                    },
                    {
                        "prompt": "The input impedance a distance $d$ from the load is $Z_{in} = Z_0(Z_L + jZ_0\\tan\\beta d)/(Z_0 + jZ_L\\tan\\beta d)$. Let $\\beta d \\to \\pi/2$, so $\\tan\\beta d \\to \\infty$. Write the limiting $Z_{in}$.",
                        "given": "A quarter wavelength means $\\beta d = (2\\pi/\\lambda)(\\lambda/4) = \\pi/2$.",
                        "answer": "\\frac{Z_0^2}{Z_L}",
                        "placeholder": "\\frac{Z_0^{2}}{Z_L}",
                        "hint": "Divide top and bottom by $\\tan\\beta d$ before taking the limit; the terms without a tangent go to zero.",
                        "deconstruct": [
                            "Dividing through: $Z_{in} = Z_0(Z_L/\\tan\\beta d + jZ_0)/(Z_0/\\tan\\beta d + jZ_L)$.",
                            "As the tangent grows without bound both leading terms vanish, leaving $Z_0 \\cdot jZ_0/(jZ_L)$.",
                        ],
                    },
                    {
                        "prompt": "Now use that backwards. You want a quarter-wave section of unknown impedance $Z_1$ to make a real load $Z_L$ look like $Z_0$. Write $Z_1$.",
                        "answer": "\\sqrt{Z_0 Z_L}",
                        "hint": "The section transforms $Z_L$ into $Z_1^2/Z_L$, and you want that to equal $Z_0$.",
                        "deconstruct": [
                            "Set $Z_1^2/Z_L = Z_0$.",
                            "So $Z_1^2 = Z_0 Z_L$, and $Z_1$ is the geometric mean of the two.",
                        ],
                    },
                ],
                "closing": r'''
The quarter-wave transformer is the cheapest matching network there is and the least
forgiving: it is a quarter wave at one frequency only. Everything else in matching is
an attempt to buy bandwidth back, usually by cascading sections whose impedances step
gradually rather than jumping once.
''',
            },
            "quiz": {
                "title": "What comes back, and how loudly",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A 50 Ω line is terminated in 100 Ω. What is the reflection coefficient?",
                        "opts": ["$+1/3$", "$+1/2$", "$+2/3$", "$-1/3$"],
                        "a": 0,
                        "why": r"""
$\Gamma = (Z_L - Z_0)/(Z_L + Z_0) = 50/150 = 1/3$. It is positive because the load is
*larger* than the line, which means the reflected voltage adds at the load rather than
subtracting — an open circuit is the extreme case at $\Gamma = +1$. A third of the
voltage comes back, so a ninth of the power does: mismatch is far more forgiving in
power than the voltage figure suggests, which is why return loss is quoted in dB.
""",
                    },
                    {
                        "q": "With $|\\Gamma| = 1/3$, what is the VSWR?",
                        "opts": ["2.0", "1.33", "3.0", "1.5"],
                        "a": 0,
                        "why": r"""
$\text{VSWR} = (1+|\Gamma|)/(1-|\Gamma|) = (4/3)/(2/3) = 2$. The standing-wave ratio is
the peak of the interference pattern over its trough, and it is measurable with nothing
but a probe on a slotted line — which is how this was done before network analysers.
Two useful anchors: $|\Gamma| = 1/3$ is a VSWR of 2, and a perfect match is a VSWR of
exactly 1, never 0.
""",
                    },
                    {
                        "q": "A line is left open at the far end. What is $\\Gamma$ there?",
                        "opts": ["$+1$", "$-1$", "$0$", "Undefined, because no current flows"],
                        "a": 0,
                        "why": r"""
$+1$: everything comes back, in phase, and the voltage at the open end doubles while
the current is forced to zero. A *short* is the mirror image at $\Gamma = -1$, where
the voltage cancels and the current doubles. Both reflect all the power, differing only
in sign — which is why a quarter-wavelength of line turns one into the other, and why a
shorted stub is a usable open circuit if you cut it to the right length.
""",
                    },
                    {
                        "q": "A quarter-wave transformer matches a 50 Ω line to a 200 Ω load. What impedance must the quarter-wave section have?",
                        "opts": ["100 Ω", "125 Ω", "150 Ω", "250 Ω"],
                        "a": 0,
                        "why": r"""
The geometric mean: $Z_1 = \sqrt{Z_0Z_L} = \sqrt{50 \times 200} = 100\ \Omega$. The
arithmetic mean, 125 Ω, is the natural guess and is wrong — a quarter-wave line inverts
impedance about its own $Z_1$, so it is multiplication that has to balance, not
addition. The catch is in the name: it is a quarter wave at exactly one frequency, and
the match degrades either side of it. That narrowness is why real matching networks
cascade several sections.
""",
                    },
                    {
                        "q": "What is the return loss for $|\\Gamma| = 1/3$?",
                        "opts": ["About 9.5 dB", "About 3 dB", "About 20 dB", "About 0.5 dB"],
                        "a": 0,
                        "why": r"""
$-20\log_{10}(1/3) = 9.54$ dB. Return loss is a *positive* number that gets bigger as
the match gets better, which is the opposite of the intuition its name suggests — 20 dB
return loss means $|\Gamma| = 0.1$ and is a good match; 3 dB means most of the power is
coming back. Worth memorising as a ladder: 6 dB is $|\Gamma| = 0.5$, 14 dB is 0.2, 20 dB
is 0.1.
""",
                    },
                ],
            },
            "lab": {
                "title": "Reflection, standing waves and a quarter-wave match",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Five functions, all of which accept complex impedances.

- `reflection(zl, z0)` returns $\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$ as a complex number.
- `vswr(g)` returns $(1 + |\Gamma|)/(1 - |\Gamma|)$, and `float("inf")` when $|\Gamma| \ge 1$.
- `return_loss(g)` returns $-20\log_{10}|\Gamma|$ in dB, and `float("inf")` when $\Gamma$ is zero.
- `input_impedance(zl, z0, bl)` returns $Z_0(Z_L + jZ_0\tan\beta d)/(Z_0 + jZ_L\tan\beta d)$
  where `bl` is the electrical length $\beta d$ in radians.
- `quarter_wave(zl, z0)` returns the real section impedance $\sqrt{Z_0 Z_L}$.

Use Python's built-in `complex` and `1j`; `np.tan` and `np.log10` do the rest. Do not
special-case $\beta d = \pi/2$ — `np.tan` returns a very large finite number there and
the formula handles it correctly to well within the tolerances used here.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def reflection(zl, z0):
    """Return the complex reflection coefficient of load zl on a line of z0."""
    # TODO
    return 0.0


def vswr(g):
    """Return the voltage standing wave ratio for a reflection coefficient g."""
    # TODO: infinite when |g| reaches 1.
    return 0.0


def return_loss(g):
    """Return -20*log10(|g|) in dB, infinite for a perfect match."""
    # TODO
    return 0.0


def input_impedance(zl, z0, bl):
    """Return the impedance seen bl radians of lossless line back from zl."""
    # TODO
    return 0.0


def quarter_wave(zl, z0):
    """Return the section impedance that matches a real zl to a real z0."""
    # TODO
    return 0.0


if __name__ == "__main__":
    g = reflection(100.0, 50.0)
    print("Gamma =", g)
    print("VSWR =", vswr(g))
    print("return loss =", return_loss(g), "dB")
    print("quarter wave back:", input_impedance(100.0, 50.0, np.pi / 2))
    print("matching section for 200 ohm:", quarter_wave(200.0, 50.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def reflection(zl, z0):
    """Return the complex reflection coefficient of load zl on a line of z0."""
    zl = complex(zl)
    z0 = complex(z0)
    return (zl - z0) / (zl + z0)


def vswr(g):
    """Return the voltage standing wave ratio for a reflection coefficient g."""
    m = abs(complex(g))
    if m >= 1.0:
        return float("inf")
    return (1.0 + m) / (1.0 - m)


def return_loss(g):
    """Return -20*log10(|g|) in dB, infinite for a perfect match."""
    m = abs(complex(g))
    if m == 0.0:
        return float("inf")
    return float(-20.0 * np.log10(m))


def input_impedance(zl, z0, bl):
    """Return the impedance seen bl radians of lossless line back from zl."""
    zl = complex(zl)
    z0 = complex(z0)
    t = float(np.tan(bl))
    return z0 * (zl + 1j * z0 * t) / (z0 + 1j * zl * t)


def quarter_wave(zl, z0):
    """Return the section impedance that matches a real zl to a real z0."""
    return float(np.sqrt(float(z0) * float(zl)))


if __name__ == "__main__":
    g = reflection(100.0, 50.0)
    print("Gamma =", g)
    print("VSWR =", vswr(g))
    print("return loss =", return_loss(g), "dB")
    print("quarter wave back:", input_impedance(100.0, 50.0, np.pi / 2))
    print("matching section for 200 ohm:", quarter_wave(200.0, 50.0))
'''}],
                "hints": [
                    "Coerce both impedances with `complex()` first, or an integer argument will do integer division somewhere you did not expect.",
                    "`abs()` of a Python complex is its magnitude — you do not need numpy for that part.",
                    "`vswr` and `return_loss` take $\\Gamma$ itself, not an impedance, so they never need $Z_0$.",
                    "`np.tan(np.pi/2)` is about $1.6\\times10^{16}$, which is large enough that the general formula lands on $Z_0^2/Z_L$ to twelve digits.",
                ],
                "tests": [
                    {"name": "a doubled load reflects one third", "code": r'''
_g = reflection(100.0, 50.0)
assert abs(_g - (1.0 / 3.0)) < 1e-12, f"(100-50)/(100+50) is 1/3, got {_g}"
assert abs(reflection(50.0, 50.0)) < 1e-15, "a matched load reflects nothing"
assert abs(reflection(0.0, 50.0) + 1.0) < 1e-15, \
    "a short circuit inverts the wave, so Gamma is -1, not +1"
'''},
                    {"name": "standing wave ratio follows the reflection", "code": r'''
_s = vswr(1.0 / 3.0)
assert abs(_s - 2.0) < 1e-12, f"|Gamma| = 1/3 gives a VSWR of 2.00, got {_s}"
assert abs(vswr(0.0) - 1.0) < 1e-15, "no reflection means a flat line: VSWR is 1, not 0"
import math
assert math.isinf(vswr(-1.0)), "a total reflection gives an infinite VSWR"
'''},
                    {"name": "return loss is the reflection in decibels", "code": r'''
_rl = return_loss(0.1)
assert abs(_rl - 20.0) < 1e-12, f"|Gamma| = 0.1 is 20 dB of return loss, got {_rl}"
_rl3 = return_loss(1.0 / 3.0)
assert abs(_rl3 - 9.542425094393248) < 1e-9, \
    f"a VSWR of 2 is 9.54 dB of return loss, got {_rl3}"
'''},
                    {"name": "a quarter wave inverts the load about Z0", "code": r'''
import numpy as np
_z = input_impedance(100.0, 50.0, np.pi / 2)
assert abs(_z - 25.0) < 1e-6, f"50^2/100 is 25 ohm, got {_z}"
_zs = input_impedance(0.0, 50.0, np.pi / 2)
assert abs(_zs) > 1e6, "a quarter wave turns a short into an open, not into a short"
'''},
                    {"name": "a half wave gives the load straight back", "code": r'''
import numpy as np
_z = input_impedance(100.0 + 60.0j, 50.0, np.pi)
assert abs(_z - (100.0 + 60.0j)) < 1e-6, \
    f"the transformation repeats every half wavelength, so this is the load, got {_z}"
_z8 = input_impedance(100.0, 50.0, np.pi / 4)
assert abs(_z8 - (40.0 - 30.0j)) < 1e-9, \
    f"an eighth wave back from 100 ohm on a 50 ohm line is 40 - 30j, got {_z8}"
'''},
                    {"name": "the matching section is the geometric mean", "code": r'''
import numpy as np
_z1 = quarter_wave(200.0, 50.0)
assert abs(_z1 - 100.0) < 1e-12, f"sqrt(50*200) is 100 ohm, got {_z1}"
_seen = input_impedance(200.0, _z1, np.pi / 2)
assert abs(_seen - 50.0) < 1e-6, \
    f"through its own quarter wave the 200 ohm load should look like 50 ohm, got {_seen}"
assert abs(reflection(_seen, 50.0)) < 1e-8, "and therefore reflect nothing"
'''},
                    {"name": "a reactive load is handled too", "code": r'''
_g = reflection(100.0 + 60.0j, 50.0)
assert abs(abs(_g) - 0.48344231827156525) < 1e-12, \
    f"|Gamma| for 100 + 60j on 50 ohm is 0.4834, got {abs(_g)}"
assert abs(vswr(_g) - 2.8717844506887853) < 1e-9, \
    f"that is a VSWR of 2.87, got {vswr(_g)}"
assert abs(_g.imag) > 0.2, "a reactive load gives a complex Gamma, not a real one"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "TE and TM modes in a rectangular guide",
            "summary": "Close the conductor round the wave and the boundary conditions quantise it. Below cutoff, nothing propagates.",
            "concepts": [
                "A hollow guide has no second conductor, so it cannot carry a TEM wave: every mode has a longitudinal field component.",
                "Separation of variables plus $E_t = 0$ on the walls forces $k_x = m\\pi/a$ and $k_y = n\\pi/b$.",
                "Cutoff is where the transverse wavenumber uses up the whole of $k = \\omega/c$: $f_c = (c/2)\\sqrt{(m/a)^2 + (n/b)^2}$.",
                "Below cutoff $\\beta$ is imaginary: the mode does not travel, it decays, and no length of guide makes it propagate.",
                "With $a$ the broad wall, TE$_{10}$ has the lowest cutoff of all, and the usable band runs from it to the next mode up — for a guide with $a > 2b$ that is TE$_{20}$, at exactly twice the frequency.",
            ],
            "read": [
                {
                    "title": "Three hundred millimetres of brass, and the frequency it refuses",
                    "minutes": 16,
                    "body": r'''
A 300 mm length of WR-90 is bolted between a sweeper and a power meter. It is a brass
tube with a rectangular hole through it, 22.86 mm by 10.16 mm, flanged at both ends,
and there is nothing inside it but air. No centre conductor, no dielectric, no
components.

At 10 GHz the meter reads the sweeper's output to within a couple of tenths of a dB.
Wind the frequency down and it stays there: 9 GHz, 8 GHz, 7 GHz, all the same. At
6.5 GHz the reading has fallen 47 dB. At 6.0 GHz there is nothing left at all — 144 dB
down, far below anything the meter can see, and taking the sweeper's power up by 10 dB
moves the reading by 10 dB and changes nothing else.

Somewhere between 7 GHz and 6 GHz the pipe stopped being a pipe. That edge is at
6.557 GHz, it is set entirely by the 22.86 mm dimension, and this module is about
where it comes from.

## The pipe has no answer at low frequency, and that is a theorem

Start with why a hollow guide cannot behave like a coaxial cable. A TEM wave is one
with no field component along the direction of travel. Put that into the Helmholtz
equation and the longitudinal wavenumber is the whole of $k$, so the transverse part
of the Laplacian acting on the transverse field is zero: the field in the
cross-section satisfies the two-dimensional Laplace equation, exactly as an
electrostatic field would.

Now apply the boundary. The wall is a perfect conductor, so it is an equipotential,
and it is the *entire* boundary of the region — one closed curve, one potential value.
Laplace's equation with the same constant on the whole boundary has one solution: that
constant everywhere, and therefore zero field. Coax escapes this because it has two
boundaries, inner and outer, which can sit at different potentials and support a
gradient between them. A hollow pipe has one, and so there is no TEM wave to be had at
any frequency.

Whatever propagates in the pipe must therefore have a longitudinal component — $H_z$
for a TE mode, $E_z$ for a TM mode — and that is what forces the whole of the rest of
this module. A mode with structure across the guide is a mode with a transverse
wavenumber, and a transverse wavenumber has to be paid for out of $k$.

## What the walls allow

Separating variables in the cross-section gives transverse dependence built from
sines and cosines in $x$ and $y$, with

$$k_x^2 + k_y^2 + \beta^2 = k^2 = \frac{\omega^2}{c^2}$$

For the TE$_{10}$ mode the only electric field is $E_y = E_0 \sin(k_x x)$, pointing
across the short dimension and varying across the long one. The tangential electric
field must vanish on a perfect conductor, so $E_y$ has to be zero at $x = 0$ and at
$x = a$. A sine handles the first wall for nothing. The second wall is a condition:
$\sin k_x a = 0$ demands $k_x a = m\pi$, so

$$k_x = \frac{m\pi}{a}, \qquad k_y = \frac{n\pi}{b}$$

with the same argument run in $y$. This is the whole of the quantisation, and it is
why the indices pair the way they do — $m$ with $a$, $n$ with $b$. The fill-in
exercise *Where a guide's cutoff comes from* assembles this chain hole by hole, and
the pairing is the first hole in it because swapping the two is the mistake that
predicts TE$_{01}$ where every datasheet says TE$_{10}$.

## Cutoff is where the transverse part uses up everything

The transverse wavenumber is $k_c = \sqrt{k_x^2 + k_y^2}$, fixed by the geometry and
the mode indices alone — it does not depend on frequency. What is left over goes along
the axis:

$$\beta = \sqrt{\frac{\omega^2}{c^2} - k_c^2}$$

Lower the frequency and $k$ shrinks while $k_c$ stays where it is. At the frequency
where $k = k_c$ there is nothing left for $\beta$, and below it the bracket is
negative. That frequency is the cutoff. Writing $\omega_c = 2\pi f_c$ and
$k_c^2 = (m\pi/a)^2 + (n\pi/b)^2$, the $\pi$ and the $2\pi$ leave

$$f_c = \frac{c}{2}\sqrt{\left(\frac{m}{a}\right)^2 + \left(\frac{n}{b}\right)^2}$$

and for TE$_{10}$, with $n = 0$, this collapses to $f_c = c/2a$. Put it in words worth
keeping: **a guide passes nothing whose free-space half-wavelength will not fit across
its wide dimension.** At 6.557 GHz the free-space wavelength is 45.72 mm, and half of
that is 22.86 mm, which is the width of WR-90 to the micron.

The derivation *Where the cutoff frequency comes from* is these four steps as an
exercise. Here is the resulting table for the guide on the bench.

```python
import math

C_LIGHT = 2.99792458e8
a, b = 0.02286, 0.01016          # WR-90 inner dimensions, in metres


def cutoff(m, n):
    """(c/2) * sqrt((m/a)^2 + (n/b)^2), in hertz."""
    return 0.5 * C_LIGHT * math.hypot(m / a, n / b)


rows = sorted((cutoff(m, n), m, n)
              for m in range(4) for n in range(4) if (m, n) != (0, 0))
for fc, m, n in rows[:6]:
    print(f"({m},{n}): {fc / 1e9:7.3f} GHz")
print(f"single-mode band: {rows[0][0] / 1e9:.3f} to {rows[1][0] / 1e9:.3f} GHz")
```

TE$_{10}$ at 6.557 GHz, TE$_{20}$ at 13.114, TE$_{01}$ at 14.754, TE$_{11}$ at 16.145.
Between the first two there is exactly one mode the guide will carry, and a guide
carrying one mode is a guide whose behaviour can be predicted; two modes travel at
different speeds and interfere at the far end according to how long the run is.

Note which mode closes the band. TE$_{20}$ arrives at twice TE$_{10}$ because it uses
the same wide wall with two half-cycles across it. TE$_{01}$ is higher still, at
$c/2b$, because $b$ is the *smaller* dimension. That ordering is the reason a standard
guide is built with $a$ a little more than $2b$: it puts TE$_{20}$ below TE$_{01}$ and
makes the single-mode band as close to an octave as the geometry allows. The lab
*Mode table, cutoff and the single-mode band* builds this table and then searches it
for the next *distinct* cutoff — distinct, because a square guide has TE$_{10}$ and
TE$_{01}$ at the same frequency, and a degenerate partner is not a band edge.

## Above cutoff: two plane waves, bouncing

There is a second way to read $\beta = \sqrt{k^2 - k_c^2}$, and it is the one that
makes module 4 obvious in advance. Pythagoras on $k$, $k_c$ and $\beta$ says the mode
is a plane wave whose propagation vector makes an angle $\theta$ with the guide axis,
with $\sin\theta = k_c/k = f_c/f$ and $\beta = k\cos\theta$. The mode is two such plane
waves, each travelling at exactly $c$, zig-zagging between the broad walls and adding
up to a field that satisfies the boundary conditions.

```python
import math

C_LIGHT = 2.99792458e8
fc = 6.5571403762e9              # TE10 in WR-90
NP_TO_DB = 20.0 / math.log(10.0)

f = 10e9
beta = 2 * math.pi * f / C_LIGHT * math.sqrt(1 - (fc / f) ** 2)
print(f"10 GHz: beta = {beta:.3f} rad/m, lambda_g = {2 * math.pi / beta * 1e3:.2f} mm"
      f", against lambda_0 = {C_LIGHT / f * 1e3:.2f} mm")
print(f"        the bounce angle to the axis is {math.degrees(math.asin(fc / f)):.1f} deg")

for f in (6.5e9, 6.0e9, 4.0e9):
    alpha = 2 * math.pi * fc / C_LIGHT * math.sqrt(1 - (f / fc) ** 2)
    print(f"{f / 1e9:4.1f} GHz: alpha = {alpha:6.2f} Np/m = {alpha * NP_TO_DB:6.1f} dB/m"
          f", so 300 mm is {alpha * 0.3 * NP_TO_DB:6.1f} dB down")
```

At 10 GHz, $\beta = 158.238$ rad/m and the guide wavelength $2\pi/\beta$ is 39.71 mm
against a free-space wavelength of 29.98 mm. The guide wavelength is *longer*, which
surprises people who expect a confined wave to be squeezed. It is the zig-zag: the
plane waves are running at 41.0° to the axis, so one full cycle of their phase covers
less axial distance than it would going straight — $\beta = k\cos\theta < k$, and
$2\pi/\beta > 2\pi/k$ follows. Everything a guide does that free space does not comes
from that angle, which shrinks to zero at high frequency and opens to 90° at cutoff.

## Below cutoff: a mirror, not a sponge

Below $f_c$ the bracket under the root is negative, $\beta$ is imaginary, and
$e^{-j\beta z}$ becomes a real decaying exponential $e^{-\alpha z}$ with

$$\alpha = \frac{2\pi f_c}{c}\sqrt{1 - \left(\frac{f}{f_c}\right)^2}$$

The block prints 18.10 Np/m at 6.5 GHz, 55.44 at 6.0 and 108.90 at 4.0 — which over
the 300 mm on the bench is 47.2 dB, 144.5 dB and 283.8 dB. Those are the readings the
power meter gave, and the cliff between 7 and 6 GHz is now a number rather than a
mystery.

**Here is the mistake, and it is nearly universal.** Those figures are in dB per
metre, which is the unit cable loss is quoted in, so they get read as loss — as though
the guide were absorbing the signal and getting warm. It is not. Read the derivation
again: the walls were taken to be *perfect* conductors throughout, and a perfect
conductor dissipates nothing. There is nowhere for the energy to go.

What actually happens is that the guide reflects it. An evanescent field stores energy
in one half of the cycle and gives it back in the other, which at the input plane
looks like an almost purely reactive load: the power goes back to the source. The
sandbox *A reactive load is a mirror, and so is a guide below cutoff* is that
statement made visible — a load of $2 + j200\ \Omega$ sits on the rim of the chart at
$|\Gamma| = 0.995$ with a VSWR of 425:1, and no length of lossless line moves it
inward.

Three consequences follow, and each is a question people get wrong. More power does
not push through, because the reflection scales with it. The rejection depends
exponentially on the *length* of the below-cutoff section, so a below-cutoff attenuator
is calibrated by how far the pickup probe is withdrawn, and it is one of the most
accurate attenuators ever built precisely because the exponent is set by a dimension
rather than by a material. And a microwave oven, at 2.45 GHz with a 122 mm wavelength,
leaks nothing through a door screen of 2 mm holes: every hole is a guide whose cutoff
is far above the frequency, and the screen is a mirror the whole way across.

## Where it stops holding

**The walls are not perfect.** Copper WR-90 loses about 0.1 dB per metre at 10 GHz,
which is negligible over a bench link and matters over a tower run. That loss is a
separate mechanism from the cutoff rejection above, and it exists on both sides of
$f_c$.

**The mode is not alone.** A bend, an iris, a step or a badly seated flange excites
higher-order modes. Below their cutoffs they decay away within a few centimetres and
do no harm; above them they propagate, and the far end sees two modes with different
delays. That is what makes the *practical* band narrower than the theoretical one:
WR-90 is sold for 8.2 to 12.4 GHz, which is $1.25 f_c$ at the bottom for dispersion
margin, and $0.95$ of the TE$_{20}$ cutoff at the top for mode margin.

**The pipe is not always empty.** Fill it with a dielectric of relative permittivity
$\varepsilon_r$ and every wavenumber scales, so every cutoff drops by
$\sqrt{\varepsilon_r}$. That is how a guide can be made physically smaller for a given
band, and it is also why a length of guide that has taken on moisture no longer cuts
off where its datasheet says.

**Cutoff is an edge, not a wall.** The transition is smooth. At 6.5 GHz, a hair below
cutoff, 300 mm of guide still passes about one part in fifty thousand of the power,
and a 30 mm plug of the same guide would pass 58% of the voltage. The cliff on the
bench is as steep as it is because the guide is long.
''',
                },
            ],
            "quiz": {
                "title": "Cutoff, and what a pipe does with what it refuses",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why can a hollow rectangular guide not carry a TEM wave at any frequency?",
                        "opts": [
                            "One conductor means one equipotential, and Laplace then forces the field to zero",
                            "The wave would have to travel at exactly $c$, which a guide never permits at any frequency",
                            "The perfectly conducting walls short out any field tangential to them, so no mode can exist",
                            "TEM needs a dielectric to travel in, and the inside of the guide is air",
                        ],
                        "a": 0,
                        "whys": [
                            r"A TEM field obeys the two-dimensional Laplace equation across the cross-section, and Laplace with one constant on the whole boundary has exactly one solution: that constant.",
                            r"The speed is a consequence rather than a cause, and putting it this way begs the question — a TEM wave in a hollow pipe would indeed travel at $c$, but it has been excluded long before its speed is computed.",
                            r"This condition is true and proves far too much: it applies to TE$_{10}$ as well, and TE$_{10}$ exists in every X-band bench in the world, so it cannot be what rules TEM out.",
                            r"Air is an excellent TEM medium — open-wire feeder and air-spaced coax both carry it — so what the pipe is missing is the second conductor, not the filling.",
                        ],
                        "why": r"""
A TEM wave has no longitudinal component, which forces the transverse field to satisfy
the two-dimensional Laplace equation in the cross-section. The boundary is one closed
perfectly conducting curve at one potential, and Laplace with a constant on the whole
boundary has exactly one solution: that constant, and therefore zero field. Coax
escapes because two conductors can sit at two potentials. The tangential-field
condition is real but proves too much as stated — it is satisfied happily by TE$_{10}$
and every other guided mode, which is why those exist. Speed is a consequence rather
than a cause, and air is a perfectly good TEM medium, as any open-wire feeder shows.
""",
                    },
                    {
                        "q": "WR-90 is 22.86 mm by 10.16 mm, with TE$_{10}$ cutting off at 6.557 GHz. Which mode closes the single-mode band, and where?",
                        "opts": [
                            "TE$_{20}$, at 13.114 GHz — twice TE$_{10}$, on the same wide wall",
                            "TE$_{01}$, at 14.754 GHz — the other index of the dominant pair",
                            "TE$_{11}$, at 16.145 GHz — the first mode with structure in both axes",
                            "TM$_{10}$, at 6.557 GHz — the TM twin of the dominant mode",
                        ],
                        "a": 0,
                        "whys": [
                            r"Two half-cycles across the same 22.86 mm wall doubles the cutoff, and 13.114 GHz is the lowest frequency above TE$_{10}$ at which anything else can travel.",
                            r"The frequency quoted is right for that mode, but $n$ pairs with the *narrow* wall, so $c/2b$ lands above TE$_{20}$ rather than below it — which is exactly why guide is built with $a$ a little over $2b$.",
                            r"Also a correct value, and it is the third cutoff up rather than the second, so the single-mode band has already closed by the time this mode appears.",
                            r"This mode does not exist. A TM mode needs both indices non-zero, because a zero index leaves it with no fields at all, so the lowest TM mode in this guide is TM$_{11}$ at 16.145 GHz.",
                        ],
                        "why": r"""
Ordering the cutoffs gives 6.557, 13.114, 14.754, 16.145 GHz for TE$_{10}$, TE$_{20}$,
TE$_{01}$ and TE$_{11}$, so the band closes at TE$_{20}$. TE$_{01}$ is the tempting
answer because $m$ and $n$ look symmetric, but they are not: $n$ pairs with the
*narrow* dimension, and $c/2b$ is therefore higher than $c/2a$. That is exactly why
standard guide is built with $a$ a little over $2b$ — it drops TE$_{20}$ below
TE$_{01}$ and stretches the usable band toward an octave. TM$_{10}$ does not exist at
all: a TM mode with a zero index has no fields left, so the lowest TM mode in this
guide is TM$_{11}$, up at 16.145 GHz alongside TE$_{11}$.
""",
                    },
                    {
                        "q": "A 300 mm length of WR-90 is driven at 4 GHz and attenuates the signal by 284 dB. Where does that energy go?",
                        "opts": [
                            "Back to the source; the guide reflects almost all of it",
                            "Into the walls, which is why a below-cutoff guide runs warm",
                            "Into the evanescent field, which stores it permanently",
                            "It radiates out of the far end as an unguided spherical wave",
                        ],
                        "a": 0,
                        "whys": [
                            r"Nothing was dissipated because nothing could be — the walls were taken as perfect from the first line — so the only place left for the power is back where it came from.",
                            r"The units invite this: Np/m and dB/m are how cable loss is quoted, and the word attenuation is shared. But the derivation never gave the walls any resistance with which to warm up.",
                            r"An evanescent field does store energy, and it hands every joule of it back within the same cycle; a store that only ever filled would need the field to grow without limit.",
                            r"Nothing arrives at the far end to radiate, which is what the 284 dB measurement says. A guide below cutoff is a mirror at its input rather than an aperture at its output.",
                        ],
                        "why": r"""
The derivation assumed perfect conductors from the first line, so there is nowhere for
energy to be dissipated — and yet nothing comes out the far end. It goes back. An
evanescent field stores energy in one part of the cycle and returns it in the next, so
the input plane looks like a nearly pure reactance and the guide is a mirror. Reading
Np/m or dB/m as heating is the tempting error, because those are the units cable loss
is quoted in and the word "attenuation" is shared; but the sandbox's below-cutoff load
sits at $|\Gamma| = 0.995$, which is a reflection, not an absorption. Permanent storage
would violate energy conservation in the steady state, and nothing reaches the far end
to radiate.
""",
                    },
                    {
                        "q": "A guide is redesigned with its height $b$ doubled and its width $a$ left alone. What happens to the TE$_{10}$ cutoff?",
                        "opts": [
                            "Nothing at all: the height $b$ does not appear in $f_c = c/2a$",
                            "It halves, since doubling a dimension halves the frequency it sets",
                            "It falls by $\\sqrt{2}$, because the cross-sectional area has doubled",
                            "It rises, because the mode now has more room to spread across",
                        ],
                        "a": 0,
                        "whys": [
                            r"With $n = 0$ the $(n/b)^2$ term vanishes, so the dominant mode's cutoff rests on the wide wall alone.",
                            r"The rule is right and applied to the wrong mode: doubling $b$ does halve TE$_{01}$, from 14.754 to 7.377 GHz, which wrecks the single-mode band without moving its lower edge at all.",
                            r"Cutoff is not set by area. Two guides of equal area and different aspect ratios cut off at different frequencies, which is why a datasheet quotes both dimensions rather than one number.",
                            r"Larger dimensions always lower a cutoff and never raise one: more room across means a longer wavelength fits, and a longer wavelength is a lower frequency.",
                        ],
                        "why": r"""
With $n = 0$ the term $(n/b)^2$ vanishes and the cutoff is $c/2a$, in which $b$ does
not appear — so the dominant mode's band edge is untouched. That is a genuinely useful
degree of freedom: guide height can be chosen for power handling or for a lower
attenuation without moving the band. What doubling $b$ does move is TE$_{01}$, which
halves from 14.754 to 7.377 GHz and lands *below* TE$_{20}$, wrecking the single-mode
band in the process. The halving answer is right about the mode that $b$ actually
sets and wrong about which mode was asked for, which is the whole trap.
""",
                    },
                    {
                        "q": "At 10 GHz the guide wavelength in WR-90 is 39.71 mm while the free-space wavelength is 29.98 mm. Why is the confined wave's wavelength longer?",
                        "opts": [
                            "The axial wavenumber is $k\\cos\\theta$, so $\\beta < k$ and $2\\pi/\\beta > 2\\pi/k$",
                            "The wave is slowed by the walls, and a slower wave has a longer wavelength",
                            "The guide is dispersive, and dispersion always stretches a wavelength",
                            "The field is spread over the whole cross-section, and that stretches it lengthways too",
                        ],
                        "a": 0,
                        "whys": [
                            r"The two plane waves run at 41.0° to the axis, so one cycle of their phase covers more axial distance than it would head-on.",
                            r"A slower wave at a fixed frequency has a *shorter* wavelength, so this reasoning points the opposite way to its own conclusion — and what moves along the axis here outruns $c$ rather than lagging it.",
                            r"This names the phenomenon instead of explaining it: dispersion is $\beta$ failing to be proportional to $\omega$, which is why the ratio 39.71/29.98 changes with frequency rather than why it exceeds one.",
                            r"Transverse and axial structure are carried by separate wavenumbers that add in quadrature, so spreading the field across the guide does not stretch anything lengthways on its own.",
                        ],
                        "why": r"""
The mode is two plane waves zig-zagging at $\theta = 41.0°$ to the axis, each moving at
exactly $c$. Their phase advances along the axis by $k\cos\theta$ per metre rather than
$k$, so the axial period is longer. Being slowed is the natural picture and it points
the wrong way: what travels at 39.71 mm per cycle along the axis is the phase pattern,
and it is moving *faster* than light, not slower — which is module 4's subject. Calling
it dispersion names the right phenomenon without explaining it: dispersion is
$\beta(\omega)$ failing to be proportional to $\omega$, and it is the reason the ratio
39.71/29.98 changes with frequency rather than the reason it exceeds one.
""",
                    },
                    {
                        "q": "The same guide is filled with a lossless dielectric of relative permittivity 2.25. What happens to the TE$_{10}$ cutoff frequency?",
                        "opts": [
                            "It falls by a factor of 1.5, to 4.371 GHz",
                            "It is unchanged, since cutoff is set by the geometry alone",
                            "It falls by a factor of 2.25, to 2.914 GHz",
                            "It rises by a factor of 1.5, to 9.836 GHz",
                        ],
                        "a": 0,
                        "whys": [
                            r"The width still has to hold half a wavelength, and the wavelength in the medium has shrunk by $\sqrt{2.25} = 1.5$.",
                            r"The formula $c/2a$ does look purely geometric, and the trap is the $c$ inside it: that is the speed in whatever fills the guide, not the speed in vacuum.",
                            r"Permittivity reaches every wave quantity through its square root, because it sits under one in the speed; using 2.25 where 1.5 belongs applies the correction one square root too many times.",
                            r"Slowing the wave inside lets a *lower* frequency fit half a wavelength across the same width, so the cutoff must fall — filling a guide is done precisely to fit a given band into a smaller pipe.",
                        ],
                        "why": r"""
The cutoff condition is that the guide's *width* holds half a wavelength, and it is
the wavelength in the medium that matters. Wavelength shrinks by $\sqrt{\varepsilon_r}
= 1.5$, so the same 22.86 mm now holds half a wavelength at a frequency 1.5 times
lower: 4.371 GHz. Believing that geometry alone sets it is the tempting error, and it
comes from the shape of $f_c = c/2a$, in which $c$ looks like a constant — but $c$
there is the speed in the filling medium, not in vacuum. Using 2.25 instead of its
square root is the other common slip: permittivity enters every wave quantity through
its root, because it sits under one in the speed.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "A reactive load is a mirror, and so is a guide below cutoff",
                "visualiser": "smith",
                "minutes": 8,
                "initial": {"rl": 2, "xl": 200, "len": 0},
                "brief": r'''
Read this chart as the mouth of a waveguide seen from its feed. The centre is the
feed impedance, and $R + jX$ is what the guide presents.

Above cutoff a mode's wave impedance is real, and power crosses into the guide. Below
cutoff the mode is evanescent: it stores energy and returns it, which on this chart is
a load with almost no resistive part at all.
''',
                "notice": [
                    "Start where it opens, $R = 2$, $X = 200$. The marker sits almost on the rim and the readout gives $|\\Gamma| = 0.995$, a VSWR of 425.04:1, and a return loss the readout rounds to 0.0 dB. Practically everything sent in comes straight back — that is a guide driven below its cutoff.",
                    "Now set $R = 75$ and $X = 0$, a purely real load like a mode well above cutoff. $|\\Gamma|$ drops to 0.200, VSWR to 1.50:1, return loss climbs to 14.0 dB. The same pipe is a component or a mirror depending only on which side of $f_c$ you drive it.",
                    "Go back to the reactive load and sweep the line length across its full range. The marker runs right round the rim on a dashed circle that nearly fills the chart, and never once moves inward. No length of lossless guide converts a reflection into a transfer of power.",
                ],
            },
            "derive": {
                "title": "Where the cutoff frequency comes from",
                "minutes": 15,
                "vars": ["a", "b", "c", "m", "n", "f", "f_c", "k_c", "k_x", "k_y", "omega", "beta"],
                "brief": r'''
Inside a rectangular guide of width $a$ and height $b$ the fields satisfy the
Helmholtz equation. Separating variables gives a transverse dependence built from
$\sin k_x x$ and $\cos k_y y$ terms, with

$$k_x^2 + k_y^2 + \beta^2 = k^2 = \frac{\omega^2}{c^2}$$

The walls are perfect conductors, so the tangential electric field vanishes on all
four of them.
''',
                "steps": [
                    {
                        "prompt": "For the TE$_{m0}$ family the transverse field goes as $\\sin k_x x$, which must vanish at both $x = 0$ and $x = a$. Write $k_x$ in terms of the integer $m$ and the width $a$.",
                        "answer": "\\frac{m \\pi}{a}",
                        "hint": "A sine vanishes at zero automatically. The second wall says $k_x a$ must be a whole number of half-cycles.",
                        "deconstruct": [
                            "$\\sin k_x a = 0$ requires $k_x a = m\\pi$ for integer $m$.",
                            "Divide by $a$.",
                        ],
                    },
                    {
                        "prompt": "The same argument in $y$ gives $k_y = n\\pi/b$. Write the transverse wavenumber $k_c = \\sqrt{k_x^2 + k_y^2}$ in terms of $m$, $n$, $a$ and $b$.",
                        "answer": "\\sqrt{\\frac{m^2 \\pi^2}{a^2} + \\frac{n^2 \\pi^2}{b^2}}",
                        "placeholder": "\\sqrt{\\frac{m^{2}\\pi^{2}}{a^{2}} + \\frac{n^{2}\\pi^{2}}{b^{2}}}",
                        "hint": "Substitute both quantised wavenumbers into the Pythagorean sum and leave it under the root.",
                        "deconstruct": [
                            "$k_x^2 = m^2\\pi^2/a^2$ and $k_y^2 = n^2\\pi^2/b^2$.",
                            "Add them and take the root.",
                        ],
                    },
                    {
                        "prompt": "Cutoff is where $\\beta = 0$, so the whole of $k$ is used up transversely: $\\omega_c/c = k_c$. For TE$_{10}$, with $m = 1$ and $n = 0$, write the cutoff frequency $f_c$ in terms of $c$ and $a$.",
                        "given": "Remember $\\omega = 2\\pi f$.",
                        "answer": "\\frac{c}{2 a}",
                        "hint": "With $n = 0$ the transverse wavenumber is just $\\pi/a$. Divide out the $2\\pi$ that turns $\\omega$ into $f$.",
                        "deconstruct": [
                            "$2\\pi f_c/c = \\pi/a$.",
                            "So $f_c = c/(2a)$ — the width is exactly half a free-space wavelength at cutoff.",
                        ],
                    },
                    {
                        "prompt": "Above cutoff the longitudinal wavenumber is what is left over. Write $\\beta$ in terms of $\\omega$, $c$ and $k_c$.",
                        "answer": "\\sqrt{\\frac{\\omega^2}{c^2} - k_c^2}",
                        "placeholder": "\\sqrt{\\frac{\\omega^{2}}{c^{2}} - k_c^{2}}",
                        "hint": "Rearrange the separation relation $k_c^2 + \\beta^2 = \\omega^2/c^2$.",
                        "deconstruct": [
                            "$\\beta^2 = \\omega^2/c^2 - k_c^2$.",
                            "Take the positive root. Below cutoff the bracket is negative, $\\beta$ is imaginary, and the mode decays instead of travelling.",
                        ],
                    },
                ],
                "closing": r'''
Notice that $\beta < \omega/c$ always, because $k_c$ takes a share of $k$ and only what
is left over goes along the axis. Two consequences, and they point opposite ways. The
guide wavelength $2\pi/\beta$ is *longer* than the free-space one, and since the phase
advances by less than $\omega/c$ radians per metre the phase pattern sweeps along the
axis *faster* than light. The energy does not: it follows the zig-zag and crawls. The
next module separates the two and puts numbers on both.
''',
            },
            "blanks": {
                "title": "Where a guide's cutoff comes from",
                "minutes": 9,
                "caption": "the TE_mn cutoff, assembled from the boundary conditions",
                "lang": "text",
                "brief": r"""
A hollow guide has one conductor, so it cannot support TEM and every mode it does carry
has a cutoff. Fill in the chain from the wall boundary conditions to the number on the
datasheet.

The guide is rectangular with inner dimensions $a \times b$ and $a > b$.
""",
                "listing": """Tangential E must vanish on the walls, which quantises the
transverse wavenumbers:

        k_x = ___                  k_y = n*pi/b

Cutoff is where the transverse wavenumber has used up the whole
of k = omega/c, leaving nothing for propagation along z:

        f_c(m,n) = ___ * sqrt( (m/a)^2 + (n/b)^2 )

With a > b the lowest of these is the mode ___ ,

        f_c = c / ___

Below its cutoff beta is imaginary, and the field ___ .
""",
                "blanks": [
                    {
                        "prompt": "The x-direction has width a and mode number m.",
                        "hole": "?",
                        "opts": ["m*pi/a", "m*pi/b", "pi/(m*a)", "m*a/pi"],
                        "a": 0,
                        "why": "Half a wavelength must fit across the guide an integer number of times, which is exactly $k_x a = m\\pi$. Pairing $m$ with $a$ and $n$ with $b$ is the whole of the index convention, and it is why the wide dimension carries the low-order mode.",
                        "whys": [
                            "Half a wavelength must fit across the guide an integer number of times, which is exactly $k_x a = m\\pi$. Pairing $m$ with $a$ and $n$ with $b$ is the whole of the index convention, and it is why the wide dimension carries the low-order mode.",
                            "Pairs $m$ with the wrong dimension. Swapping them swaps which mode is dominant, and predicts $TE_{01}$ where every datasheet says $TE_{10}$.",
                            "Inverted: a *wider* guide would then have a larger $k_x$ and a higher cutoff, which is backwards — a bigger box is easier to propagate in, not harder.",
                            "The dimensions are wrong; a wavenumber has units of one over length, and this has units of length.",
                        ],
                    },
                    {
                        "prompt": "Turn a transverse wavenumber into a frequency.",
                        "hole": "?",
                        "opts": ["c/2", "c", "2*c", "1/(2*c)"],
                        "a": 0,
                        "why": "From $k_c = \\omega_c/c$ with $k_c^2 = (m\\pi/a)^2 + (n\\pi/b)^2$, the $\\pi$ and the $2\\pi$ in $\\omega = 2\\pi f$ leave a factor of $c/2$. It is the same $c/2$ that makes a half-wavelength resonator's frequency $c/2\\ell$.",
                        "whys": [
                            "From $k_c = \\omega_c/c$ with $k_c^2 = (m\\pi/a)^2 + (n\\pi/b)^2$, the $\\pi$ and the $2\\pi$ in $\\omega = 2\\pi f$ leave a factor of $c/2$. It is the same $c/2$ that makes a half-wavelength resonator's frequency $c/2\\ell$.",
                            "A factor of two high, which would put every guide's cutoff at twice its real value — and predict that WR-90 starts at 13 GHz rather than 6.56 GHz.",
                            "Four times too high. The $2\\pi$ from angular frequency divides here, it does not multiply.",
                            "Dimensionally upside down: this gives a frequency that falls as the speed of light rises.",
                        ],
                    },
                    {
                        "prompt": "With a > b, which indices give the lowest cutoff?",
                        "hole": "?",
                        "opts": ["TE_10", "TE_11", "TM_11", "TE_01"],
                        "a": 0,
                        "why": "Put $m = 1, n = 0$ and only the $1/a$ term survives — and $a$ is the *larger* dimension, so it gives the smallest frequency. $TE_{10}$ is the dominant mode of every standard rectangular guide, and the single-mode band runs from its cutoff up to the next mode's.",
                        "whys": [
                            "Put $m = 1, n = 0$ and only the $1/a$ term survives — and $a$ is the *larger* dimension, so it gives the smallest frequency. $TE_{10}$ is the dominant mode of every standard rectangular guide, and the single-mode band runs from its cutoff up to the next mode's.",
                            "Both indices non-zero, so both terms contribute and the cutoff is higher than either alone. It is a real mode, just not the first one.",
                            "TM modes need both indices non-zero — $TM_{10}$ does not exist, because a TM mode with a zero index has no fields at all. So the lowest TM mode is already above several TE modes.",
                            "Uses $b$, the narrow dimension, so its cutoff is *higher*, not lower. For the usual $a = 2b$ it is exactly twice $TE_{10}$'s, which is what sets the top of the single-mode band.",
                        ],
                    },
                    {
                        "prompt": "Put m=1, n=0 into the formula above.",
                        "hole": "?",
                        "opts": ["2*a", "a", "2*b", "a + b"],
                        "a": 0,
                        "why": "$f_c = (c/2)(1/a) = c/2a$: the guide cuts off when the free-space wavelength reaches twice the wide dimension. That is the sentence worth carrying away — a guide passes nothing whose half-wavelength will not fit across it.",
                        "whys": [
                            "$f_c = (c/2)(1/a) = c/2a$: the guide cuts off when the free-space wavelength reaches twice the wide dimension. That is the sentence worth carrying away — a guide passes nothing whose half-wavelength will not fit across it.",
                            "Drops the factor of two, doubling every cutoff frequency you compute.",
                            "The narrow dimension does not appear in $TE_{10}$'s cutoff at all — which is why guide height can be chosen for power handling without moving the band.",
                            "Cutoff comes from one dimension for this mode, not from a combination of both.",
                        ],
                    },
                    {
                        "prompt": "Below cutoff, beta is imaginary. What does the field do?",
                        "hole": "?",
                        "opts": [
                            "decays exponentially without carrying power",
                            "propagates, but attenuated by the walls",
                            "reflects with a 90 degree phase shift",
                            "travels faster than light",
                        ],
                        "a": 0,
                        "why": "$e^{-j\\beta z}$ with imaginary $\\beta$ becomes a real decaying exponential — an evanescent field. It stores energy and returns it; it transports none, and a guide below cutoff is a near-perfect mirror rather than an absorber. This is why a microwave oven door with holes far smaller than 12 cm leaks nothing.",
                        "whys": [
                            "$e^{-j\\beta z}$ with imaginary $\\beta$ becomes a real decaying exponential — an evanescent field. It stores energy and returns it; it transports none, and a guide below cutoff is a near-perfect mirror rather than an absorber. This is why a microwave oven door with holes far smaller than 12 cm leaks nothing.",
                            "Wall loss is a separate, much smaller effect that exists above cutoff too. Below cutoff the decay happens in a *perfect* conductor, where there is no loss at all — so it is not dissipation.",
                            "There is a reflection, and for a lossless guide it is total, but the description of the field inside is the decaying exponential rather than a phase shift.",
                            "That describes phase velocity *above* cutoff, which is the subject of the next module and carries no information.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Mode table, cutoff and the single-mode band",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Work in SI throughout, with `C_LIGHT` as given in the starter.

- `cutoff(a, b, m, n)` returns $(c/2)\sqrt{(m/a)^2 + (n/b)^2}$ in hertz. The mode with
  $m = n = 0$ does not exist in a hollow guide; return `float("inf")` for it.
- `mode_table(a, b, mmax, nmax)` returns a list of `(fc, m, n)` tuples for every
  $0 \le m \le m_{max}$ and $0 \le n \le n_{max}$ except $(0, 0)$, sorted by `fc`.
- `single_mode_band(a, b)` returns `(f_lo, f_hi)`, the cutoff of the dominant mode and
  the cutoff of the next *distinct* one. Search up to $m, n \le 3$. Two modes count as
  distinct when their cutoffs differ by more than one part in $10^{12}$, so that a
  square guide's degenerate pair is not mistaken for a band edge.
- `beta(f, fc)` returns $(2\pi f/c)\sqrt{1 - (f_c/f)^2}$ above cutoff, and `0.0` at or
  below it.
- `alpha(f, fc)` returns $(2\pi f_c/c)\sqrt{1 - (f/f_c)^2}$ nepers per metre below
  cutoff, and `0.0` at or above it.
- `guide_wavelength(f, fc)` returns $2\pi/\beta$, or `float("inf")` below cutoff.

The default guide in `main.py` is WR-90: 22.86 mm by 10.16 mm, the standard X-band
part.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90 = (0.02286, 0.01016)


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode in an a-by-b guide."""
    # TODO: the (0, 0) mode does not exist.
    return 0.0


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    # TODO
    return []


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    # TODO
    return (0.0, 0.0)


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    # TODO
    return 0.0


def alpha(f, fc):
    """Evanescent decay in nepers/m below cutoff, zero at or above it."""
    # TODO
    return 0.0


def guide_wavelength(f, fc):
    """2*pi/beta in metres, infinite at or below cutoff."""
    # TODO
    return 0.0


if __name__ == "__main__":
    a, b = WR90
    for fc, m, n in mode_table(a, b, 2, 2)[:4]:
        print(f"TE{m}{n}: {fc / 1e9:.3f} GHz")
    print("band:", tuple(round(f / 1e9, 3) for f in single_mode_band(a, b)), "GHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90 = (0.02286, 0.01016)


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode in an a-by-b guide."""
    if m == 0 and n == 0:
        return float("inf")
    return 0.5 * C_LIGHT * float(np.sqrt((m / a) ** 2 + (n / b) ** 2))


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    rows = []
    for m in range(mmax + 1):
        for n in range(nmax + 1):
            if m == 0 and n == 0:
                continue
            rows.append((cutoff(a, b, m, n), m, n))
    rows.sort()
    return rows


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    rows = mode_table(a, b, 3, 3)
    lo = rows[0][0]
    for fc, _m, _n in rows:
        if fc > lo * (1.0 + 1e-12):
            return (lo, fc)
    return (lo, float("inf"))


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    if f <= fc:
        return 0.0
    return 2.0 * np.pi * f / C_LIGHT * float(np.sqrt(1.0 - (fc / f) ** 2))


def alpha(f, fc):
    """Evanescent decay in nepers/m below cutoff, zero at or above it."""
    if f >= fc:
        return 0.0
    return 2.0 * np.pi * fc / C_LIGHT * float(np.sqrt(1.0 - (f / fc) ** 2))


def guide_wavelength(f, fc):
    """2*pi/beta in metres, infinite at or below cutoff."""
    b = beta(f, fc)
    if b <= 0.0:
        return float("inf")
    return 2.0 * np.pi / b


if __name__ == "__main__":
    a, b = WR90
    for fc, m, n in mode_table(a, b, 2, 2)[:4]:
        print(f"TE{m}{n}: {fc / 1e9:.3f} GHz")
    print("band:", tuple(round(f / 1e9, 3) for f in single_mode_band(a, b)), "GHz")
'''}],
                "hints": [
                    "`rows.sort()` on a list of tuples sorts by the first element, which is exactly the cutoff ordering you want.",
                    "For a guide with $a > b$ the dominant mode is always TE$_{10}$, so `rows[0]` is it — but write the search anyway, because a square guide breaks the assumption.",
                    "`beta` and `alpha` are the same square root with the arguments swapped; each is zero wherever the other is real.",
                    "Guide wavelength comes out *longer* than free space, not shorter. If yours is shorter, you have the ratio $f_c/f$ upside down.",
                ],
                "tests": [
                    {"name": "the dominant cutoff of WR-90 is 6.557 GHz", "code": r'''
_fc = cutoff(0.02286, 0.01016, 1, 0)
assert abs(_fc - 6.5571403762e9) < 1e3, \
    f"c/(2a) with a = 22.86 mm is 6.5571 GHz, got {_fc / 1e9:.4f} GHz"
assert cutoff(0.02286, 0.01016, 0, 0) == float("inf"), \
    "there is no TE00 mode in a hollow guide"
'''},
                    {"name": "the second and third modes sit where they should", "code": r'''
_a, _b = 0.02286, 0.01016
assert abs(cutoff(_a, _b, 2, 0) - 1.3114280752e10) < 1e3, \
    "TE20 has exactly twice the cutoff of TE10"
assert abs(cutoff(_a, _b, 0, 1) - 1.4753565846e10) < 1e3, \
    "TE01 is set by the height b, so c/(2b) = 14.75 GHz"
'''},
                    {"name": "the mode table is complete and ordered", "code": r'''
_t = mode_table(0.02286, 0.01016, 2, 2)
assert len(_t) == 8, f"3 by 3 modes minus the (0,0) that does not exist is 8, got {len(_t)}"
assert [(m, n) for _f, m, n in _t[:3]] == [(1, 0), (2, 0), (0, 1)], \
    f"the first three should be TE10, TE20, TE01, got {[(m, n) for _f, m, n in _t[:3]]}"
assert all(_t[i][0] <= _t[i + 1][0] for i in range(len(_t) - 1)), \
    "the table must come back sorted by cutoff"
'''},
                    {"name": "the single-mode band runs from TE10 to TE20", "code": r'''
_lo, _hi = single_mode_band(0.02286, 0.01016)
assert abs(_lo - 6.5571403762e9) < 1e3, f"the band starts at the TE10 cutoff, got {_lo}"
assert abs(_hi - 1.3114280752e10) < 1e3, f"and ends where TE20 appears, got {_hi}"
assert _hi > _lo, "the upper edge must be above the lower one"
'''},
                    {"name": "a square guide has a degenerate pair, not a band edge", "code": r'''
_lo, _hi = single_mode_band(0.02, 0.02)
assert abs(cutoff(0.02, 0.02, 1, 0) - cutoff(0.02, 0.02, 0, 1)) < 1.0, \
    "in a square guide TE10 and TE01 are degenerate"
assert _hi > _lo * 1.2, \
    f"the degenerate partner is not a band edge, so f_hi should be well above f_lo, got {_lo} and {_hi}"
'''},
                    {"name": "the axial wavenumber is below the free-space one", "code": r'''
_fc = 6.5571403762e9
_b = beta(10e9, _fc)
assert abs(_b - 158.2382563130) < 1e-6, f"beta at 10 GHz should be 158.24 rad/m, got {_b}"
assert _b < 2 * 3.141592653589793 * 10e9 / 2.99792458e8, \
    "beta must be below the free-space wavenumber, since k_c takes a share of k"
assert beta(5e9, _fc) == 0.0, "nothing propagates below cutoff"
'''},
                    {"name": "below cutoff the mode decays instead", "code": r'''
_fc = 6.5571403762e9
_al = alpha(4e9, _fc)
assert abs(_al - 108.8954160181) < 1e-6, \
    f"at 4 GHz the decay should be 108.9 Np/m, got {_al}"
assert alpha(10e9, _fc) == 0.0, "above cutoff there is no evanescent decay"
assert alpha(1e9, _fc) > _al, "the further below cutoff, the faster the decay"
'''},
                    {"name": "the guide wavelength is longer than free space", "code": r'''
_fc = 6.5571403762e9
_lg = guide_wavelength(10e9, _fc)
assert abs(_lg - 0.03970711921111) < 1e-9, \
    f"2*pi/beta at 10 GHz is 39.71 mm, got {_lg * 1e3:.3f} mm"
assert _lg > 2.99792458e8 / 10e9, \
    "the guide wavelength exceeds the 29.98 mm free-space wavelength at the same frequency"
assert guide_wavelength(5e9, _fc) == float("inf"), \
    "below cutoff there is no wavelength along the guide at all"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Dispersion, phase velocity and group velocity",
            "summary": "In a guide the two velocities are different, one is faster than light, and only the other carries anything.",
            "concepts": [
                "$\\beta(\\omega)$ is not proportional to $\\omega$ in a guide, and that is the whole definition of dispersion.",
                "Phase velocity $\\omega/\\beta$ exceeds $c$ at every frequency in the band, not only near cutoff, and grows without bound as cutoff is approached; it carries no information, and violates nothing.",
                "Group velocity $d\\omega/d\\beta$ is the speed of the envelope and stays below $c$ at every frequency.",
                "$v_p v_g = c^2$ exactly, for every hollow guide and every mode.",
                "Different frequencies in one pulse arrive at different times, so a wide-band pulse spreads — and the spreading grows with length and with proximity to cutoff.",
            ],
            "read": [
                {
                    "title": "Two metres of guide that answers the same question twice",
                    "minutes": 17,
                    "body": r'''
Two metres of WR-90 runs between the ports of a vector network analyser at 10 GHz.
It is the same guide as the last module: 22.86 by 10.16 mm, cutting off at 6.557 GHz,
carrying nothing but TE$_{10}$. Ask it how long a signal takes to cross, and it
answers twice, with two different numbers.

Read the transmission phase and unwrap it: $\phi = -\beta\ell = -316.48$ radians, which
a readout that keeps only one turn shows as $-133°$. Divide its magnitude by
$\omega = 2\pi \times 10^{10}$ and the delay is **5.0369 ns**. That corresponds to a speed of $2/5.0369\ \text{ns} =
3.97\times10^8$ m/s, which is $1.32c$.

Now modulate the carrier with a short envelope and watch the envelope come out the
far end on a fast detector. It arrives **8.8360 ns** after it went in — a speed of
$2.26\times10^8$ m/s, or $0.755c$.

Same guide, same frequency, same two metres. One number says the signal crossed at
1.32 times the speed of light; the other, measured on the same afternoon with a pulse
you can see, says it took three-quarters of that speed and 75% longer. Both
measurements are correct. They are answers to different questions, and this module is
about telling the questions apart.

## One curve, a chord and a tangent

Module 3 left the dispersion relation for any hollow-guide mode:

$$\beta(\omega) = \frac{\sqrt{\omega^2 - \omega_c^2}}{c}$$

Plot $\omega$ against $\beta$ and it is a hyperbola: it starts at $\beta = 0$ when
$\omega = \omega_c$, rises steeply, and settles asymptotically onto the straight line
$\omega = c\beta$ at high frequency. That single curve holds both answers, and they
are two different lines drawn on it.

The **chord** from the origin to the operating point has slope $\omega/\beta$. That is
the phase velocity: how fast a point of constant phase moves along the axis.

The **tangent** at the operating point has slope $d\omega/d\beta$. That is the group
velocity: how fast a bump in the envelope moves.

On a line whose $\beta$ *is* proportional to $\omega$ — module 1's coax, where
$\beta = \omega\sqrt{LC}$ — the curve is a straight line through the origin, chord and
tangent coincide, and there is one velocity. In a guide the curve bends away from the
origin, the chord is steeper than the tangent everywhere, and the two numbers part
company. **That bend is the definition of dispersion**, and everything else in this
module is a consequence of it.

The algebra is two derivatives, worked step by step in *Two velocities from one
dispersion relation*. Writing $\omega_c/\omega = f_c/f$ throughout:

$$v_p = \frac{\omega}{\beta} = \frac{c}{\sqrt{1 - (f_c/f)^2}}, \qquad
v_g = \frac{d\omega}{d\beta} = c\sqrt{1 - (f_c/f)^2}$$

The second comes from differentiating $\beta$ and inverting: $d\beta/d\omega =
\omega/(c\sqrt{\omega^2 - \omega_c^2})$, and $v_g$ is its reciprocal. Multiply the two
velocities and the roots cancel:

$$v_pv_g = c^2$$

exactly, at every frequency, for every mode of every hollow guide. One is above $c$ by
the same factor the other is below it.

```python
import math

C_LIGHT = 2.99792458e8
fc, f, length = 6.5571403762e9, 10e9, 2.0      # WR-90 TE10, X band, 2 m of guide

root = math.sqrt(1.0 - (fc / f) ** 2)
v_p, v_g = C_LIGHT / root, C_LIGHT * root
beta = 2 * math.pi * f / C_LIGHT * root

print(f"bounce angle to the axis  {math.degrees(math.asin(fc / f)):.2f} deg")
print(f"v_p = {v_p:.4e} m/s = {v_p / C_LIGHT:.4f} c")
print(f"v_g = {v_g:.4e} m/s = {v_g / C_LIGHT:.4f} c")
print(f"v_p * v_g / c^2 = {v_p * v_g / C_LIGHT ** 2:.12f}")
print(f"beta * length = {beta * length:.2f} rad, or "
      f"{math.degrees(beta * length) % 360:.1f} deg wrapped into one turn")
print(f"phase delay over {length:.0f} m = {length / v_p * 1e9:.4f} ns")
print(f"group delay over {length:.0f} m = {length / v_g * 1e9:.4f} ns")
```

It reproduces the bench: 1.3245$c$ and 0.7550$c$, a product that is 1.000000000000 in
units of $c^2$, and the two delays of 5.0369 ns and 8.8360 ns that started the module.

## Nothing is violated, and here is exactly why

A phase velocity of $1.32c$ at 10 GHz is not an artefact and not a near-cutoff
curiosity. It is above $c$ at *every* frequency the guide propagates, growing without
bound as $f \to f_c$ and approaching $c$ from above only as $f \to \infty$. Treat that
as a physical fact to be understood rather than a number to be apologised for.

The clean way to see it is the zig-zag from the last module. The TE$_{10}$ mode is two
plane waves bouncing between the broad walls, each travelling at exactly $c$, with
their propagation vectors at $\theta = 40.97°$ to the axis at this frequency. Take one
wavefront — a plane perpendicular to one of those vectors — and ask where it crosses
the guide axis. That crossing point slides forward at $c/\cos\theta$, because the
wavefront advances at $c$ along its own normal and the axis is at an angle to it. At
$\theta = 40.97°$, $1/\cos\theta = 1.3245$, and there is the phase velocity, geometry
and nothing else.

Nothing rides that crossing point. It is the same object as the intersection of a
closing pair of scissors, which can be made to run down the blades faster than either
blade moves, or the spot of a laser swept across a distant wall. No matter, no energy
and no message travels along the axis at $1.32c$; two plane waves travel at $c$ in a
direction that is not the axis, and their intersection with the axis is a geometrical
consequence.

Turn it around for the group velocity: the energy is carried by those same plane waves
at $c$, but along the zig-zag, so its *axial* progress is $c\cos\theta = 0.755c$. The
factor is $\cos\theta$ for the energy and $1/\cos\theta$ for the phase, which is why
their product is $c^2$ and why the excess of one is precisely the deficit of the other.

There is a second, independent reason the superluminal phase velocity carries nothing.
A pure sinusoid has no beginning. It extends from $t = -\infty$ and is entirely
predictable; a receiver watching it learns nothing at 3 pm that it did not know at
2 pm. To send information you must change something — start it, stop it, modulate it —
and any change creates an envelope, and the envelope moves at $v_g$. The instant you
make the wave capable of carrying a message you have made it travel below $c$.

## The mistake: timing a link with the phase

The most expensive error in this module is using the wrong delay, and it is tempting
for a specific reason. Everywhere before this course, $\omega/\beta$ and $d\omega/d\beta$
were the same number. On the coax of module 1, both are $1/\sqrt{LC}$. On a string,
both are $\sqrt{T/\mu}$. Ten years of writing "velocity $= \omega/\beta$" costs nothing
until the day it meets a curve that is not a straight line through the origin, and then
it is wrong by a factor of 1.754.

Here that error predicts the pulse arriving at 5.04 ns when it actually arrives at
8.84 ns: 3.80 ns late, which at the speed of light is 1.14 m of range error. In a
radar, that is a target misplaced by more than a metre. In a phased array fed through
guide, path lengths trimmed to be equal in *guide wavelengths* are equal in phase at
one frequency and unequal in delay at all of them, which is exactly why a
phase-trimmed array squints as the frequency moves and a true-time-delay array does
not.

The reciprocal is worth keeping straight too. $d\beta/d\omega$ is the group *delay per
metre*, in seconds per metre; $d\omega/d\beta$ is the group *velocity*, in metres per
second. A network analyser's group-delay trace reports the first, as $-d\phi/d\omega$
over the whole run. The sandbox *Phase slope is group delay* is that idea on the
plainest system that has a bending phase: a flat gain change moves the magnitude
curve bodily and does not move the phase at all, because delay lives in the slope of
the phase and nowhere else.

## What dispersion does to a pulse

If different frequencies travel at different group velocities, a pulse containing many
frequencies cannot stay the shape it started as. The components that left together
arrive apart, and the pulse comes out wider than it went in.

```python
import math

C_LIGHT = 2.99792458e8
fc = 6.5571403762e9


def beta(f):
    return 2 * math.pi * f / C_LIGHT * math.sqrt(1 - (fc / f) ** 2)


def group_delay(f, length):
    return length / (C_LIGHT * math.sqrt(1 - (fc / f) ** 2))


f, df = 10e9, 1e3
numeric = 2 * math.pi * (2 * df) / (beta(f + df) - beta(f - df))
closed = C_LIGHT * math.sqrt(1 - (fc / f) ** 2)
print(f"d(omega)/d(beta) by central difference = {numeric:.6e} m/s")
print(f"the closed form                        = {closed:.6e} m/s")
print(f"agreeing to {abs(numeric - closed) / closed:.2e} of themselves")

for lo, hi, ell in ((9.9e9, 10.1e9, 10.0), (8e9, 12e9, 10.0), (8e9, 12e9, 100.0),
                    (7e9, 7.2e9, 10.0)):
    spread = abs(group_delay(lo, ell) - group_delay(hi, ell))
    print(f"{lo / 1e9:4.1f} to {hi / 1e9:4.1f} GHz over {ell:5.1f} m: "
          f"{spread * 1e9:8.3f} ns of spread")
```

The first half is the check the lab *Measure the two velocities, and the delay spread
they cause* asks you to build: `group_velocity_numeric` differences $\beta$ either side
of the operating point and must reproduce the closed form, which it does to three parts
in $10^{11}$. It is an algebra check with teeth — differentiate $\beta$ wrongly and the
two numbers part company in the third digit.

The second half is the engineering. A 2% band at mid-band smears by 0.667 ns over 10 m.
The full 8–12 GHz band smears by 18.398 ns over the same 10 m, and by 183.980 ns over
100 m — the spread is exactly proportional to length, since every delay is. And the
last line is the one to sit with: a 200 MHz band at 7 GHz, a mere 7% above cutoff,
smears by 14.534 ns over 10 m. A band twenty times narrower, sitting near the edge,
does nearly as much damage as the whole of X band does in the middle. Dispersion is
not about how wide your signal is; it is about how far along the bend of the curve you
are sitting.

The capstone *Push a pulse through a waveguide and measure what it costs* replaces this
two-point estimate with the honest calculation: every frequency bin of a real burst
gets its own $e^{-j\beta\ell}$, and the arrival time and the width are measured off the
waveform that comes out.

## Where it stops holding

**Near cutoff, a two-point spread is an underestimate.** The delay-spread figures above
difference the group delay at two band edges, which assumes the delay varies roughly
linearly between them. Near cutoff it does not: $d^2\beta/d\omega^2$ grows without
bound, the pulse acquires a chirp, and it does not merely widen — it changes shape,
with the low frequencies trailing far behind. The two-point number is a lower bound on
the trouble.

**The group velocity is a narrow-band idea.** It is the first term of a Taylor
expansion of $\beta(\omega)$ about the carrier. Over a band wide enough for the second
term to matter, "the envelope travels at $v_g$" stops being a complete description of
what happens, and only the full transfer function tells you the answer.

**Group velocity is not always the signal velocity.** In hollow guide above cutoff,
$v_g$ is also the energy transport velocity and stays under $c$, so the two agree. In a
medium with resonant absorption, $v_g$ can exceed $c$ or go negative while nothing
causal is violated at all, because it has stopped describing anything that moves. What
never changes, in any medium, is the *front* velocity: the very first disturbance to
arrive after a signal is switched on travels at exactly $c$. That is the statement
relativity actually constrains, and it holds here whatever $v_p$ and $v_g$ are doing.

**The walls and the fill are ideal.** Copper losses add a frequency-dependent
attenuation on top of all of this, and any dielectric inside brings its own dispersion
to add to the guide's. In a hollow copper guide over a few metres, neither changes the
numbers above by anything you could measure.
''',
                },
            ],
            "sandbox": {
                "title": "Phase slope is group delay",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 0.15, "K": 1},
                "brief": r'''
Group delay is $-d\phi/d\omega$: the steeper the phase curve, the longer the envelope
is held up. A guide near cutoff has a phase that bends sharply with frequency, and
that bend is what spreads a pulse.

This second-order section is the simplest system with a phase that bends. Read the
bottom plot as a dispersion curve.
''',
                "notice": [
                    "With $\\zeta = 0.15$ the phase goes from about $-11°$ at $\\omega_n/2$ to about $-169°$ at $2\\omega_n$ — almost the whole 180° inside a factor of four in frequency. Set $\\zeta = 1.5$ and over exactly the same span it moves only from about $-63°$ to about $-117°$. Both curves still run the full 180° between zero and infinite frequency; what changes is how much of it they spend near the corner, and it is that slope which sets the delay.",
                    "Look at the magnitude plot far above the corner. With $\\omega_n = 20$ it reads about $-40$ dB at $\\omega = 200$ and about $-80$ dB at $\\omega = 2000$: 40 dB per decade, which is the two-pole roll-off. A guide below cutoff rejects by a different mechanism entirely — its attenuation is exponential in the *length* of guide rather than a power law in frequency, so the rejection is set by how far you go rather than by how far past a corner you are.",
                    "Raise $K$ from 1 to 10. The magnitude curve lifts bodily by 20 dB and the phase curve does not move at all. Flat gain delays nothing; only a frequency-dependent *phase* does.",
                ],
            },
            "derive": {
                "title": "Two velocities from one dispersion relation",
                "minutes": 15,
                "vars": ["omega", "omega_c", "c", "v_p", "v_g", "beta", "d", "t_g", "lambda_g", "f"],
                "brief": r'''
From the last module, the dispersion relation of any hollow-guide mode is

$$\beta(\omega) = \frac{\sqrt{\omega^2 - \omega_c^2}}{c}$$

where $\omega_c = 2\pi f_c$. Everything about how a pulse travels is in the shape of
that curve.
''',
                "steps": [
                    {
                        "prompt": "Phase velocity is $v_p = \\omega/\\beta$. Write it in terms of $\\omega$, $\\omega_c$ and $c$.",
                        "answer": "\\frac{c \\omega}{\\sqrt{\\omega^2 - \\omega_c^2}}",
                        "placeholder": "\\frac{c\\omega}{\\sqrt{\\omega^{2} - \\omega_c^{2}}}",
                        "hint": "Divide $\\omega$ by the whole expression for $\\beta$; the $c$ in the denominator of $\\beta$ moves up to the numerator.",
                        "deconstruct": [
                            "$v_p = \\omega \\div \\left(\\sqrt{\\omega^2 - \\omega_c^2}/c\\right)$.",
                            "Dividing by a fraction multiplies by its reciprocal.",
                        ],
                    },
                    {
                        "prompt": "Differentiate $\\beta$ with respect to $\\omega$. Write $d\\beta/d\\omega$.",
                        "answer": "\\frac{\\omega}{c \\sqrt{\\omega^2 - \\omega_c^2}}",
                        "placeholder": "\\frac{\\omega}{c\\sqrt{\\omega^{2} - \\omega_c^{2}}}",
                        "hint": "Chain rule on $\\sqrt{u}$ with $u = \\omega^2 - \\omega_c^2$: the derivative is $u'/(2\\sqrt{u})$, and $u' = 2\\omega$.",
                        "deconstruct": [
                            "$\\frac{d}{d\\omega}\\sqrt{\\omega^2 - \\omega_c^2} = \\frac{2\\omega}{2\\sqrt{\\omega^2 - \\omega_c^2}}$.",
                            "The constant $1/c$ carries through unchanged.",
                        ],
                    },
                    {
                        "prompt": "Group velocity is $v_g = d\\omega/d\\beta$, the reciprocal of what you just wrote. Write $v_g$.",
                        "answer": "\\frac{c \\sqrt{\\omega^2 - \\omega_c^2}}{\\omega}",
                        "placeholder": "\\frac{c\\sqrt{\\omega^{2} - \\omega_c^{2}}}{\\omega}",
                        "hint": "Turn the previous answer upside down.",
                        "deconstruct": [
                            "$v_g = 1 \\div \\frac{\\omega}{c\\sqrt{\\omega^2 - \\omega_c^2}}$.",
                            "Which is the same fraction inverted.",
                        ],
                    },
                    {
                        "prompt": "Multiply the two velocities together. Write $v_p v_g$.",
                        "answer": "c^2",
                        "placeholder": "c^{2}",
                        "hint": "The two square roots cancel, and so does $\\omega$.",
                        "deconstruct": [
                            "$v_p v_g = \\frac{c\\omega}{\\sqrt{\\cdot}}\\cdot\\frac{c\\sqrt{\\cdot}}{\\omega}$.",
                            "Everything but the two factors of $c$ cancels, and the result does not depend on frequency at all.",
                        ],
                    },
                    {
                        "prompt": "The guide wavelength is $\\lambda_g = 2\\pi/\\beta$. Write it in terms of $\\omega$, $\\omega_c$ and $c$.",
                        "answer": "\\frac{2 \\pi c}{\\sqrt{\\omega^2 - \\omega_c^2}}",
                        "placeholder": "\\frac{2\\pi c}{\\sqrt{\\omega^{2} - \\omega_c^{2}}}",
                        "hint": "Substitute the dispersion relation into $2\\pi/\\beta$ and tidy.",
                        "deconstruct": [
                            "$\\lambda_g = 2\\pi \\div \\frac{\\sqrt{\\omega^2 - \\omega_c^2}}{c}$.",
                            "As $\\omega$ approaches $\\omega_c$ the denominator goes to zero and $\\lambda_g$ grows without limit.",
                        ],
                    },
                ],
                "closing": r'''
$v_p v_g = c^2$ says the two velocities sit either side of $c$ and move apart together.
Near cutoff the phase pattern sweeps along the axis arbitrarily fast while the energy
barely crawls. Nothing overtakes light, because the phase pattern is not a thing that
can carry a message — only the envelope is, and it moves at $v_g$.
''',
            },
            "quiz": {
                "title": "Two velocities, and which one is real",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In a guide above cutoff, $v_p = \\omega/\\beta$ is greater than $c$ at every frequency in the band. What does that mean?",
                        "opts": [
                            "Nothing is violated — no energy or information moves at the phase velocity",
                            "The guide must be lossy for this to be possible",
                            "It only happens close to cutoff and can be ignored",
                            "The calculation has a sign error",
                        ],
                        "a": 0,
                        "why": r"""
Phase velocity is the speed of a point of constant phase on an infinite, unmodulated
sinusoid — and an infinite sinusoid carries no information, because it has already been
going forever. Nothing is transmitted by it. The moment you modulate the wave to send
something, the envelope moves at the group velocity, which stays below $c$. It is
superluminal at *every* frequency in the band, not just near cutoff, and the effect is
perfectly real in a lossless guide.
""",
                    },
                    {
                        "q": "Which velocity is the speed of a pulse envelope?",
                        "opts": ["$d\\omega/d\\beta$", "$\\omega/\\beta$", "$\\beta/\\omega$", "$d\\beta/d\\omega$"],
                        "a": 0,
                        "why": r"""
The group velocity is the *slope* of the dispersion curve, not a ratio of its
coordinates. That distinction is the whole content of this module: $\omega/\beta$ is a
chord from the origin and $d\omega/d\beta$ is a tangent, and in a guide they differ.
Its reciprocal $d\beta/d\omega$ is the group *delay* per unit length, which is what a
network analyser actually reports.
""",
                    },
                    {
                        "q": "For a hollow rectangular guide, what is $v_pv_g$?",
                        "opts": ["$c^2$", "$c$", "$c^2/2$", "It depends on the mode"],
                        "a": 0,
                        "why": r"""
Exactly $c^2$, for every mode of a hollow guide. It falls out of
$\beta^2 = (\omega/c)^2 - k_c^2$ in two lines and it is the cleanest sanity check in the
subject: if the phase velocity is $1.5c$ then the group velocity is $c/1.5$, and the
excess of one is precisely the deficit of the other. It also makes the superluminal
phase velocity feel less alarming — the two are locked together, and their geometric
mean is always $c$.
""",
                    },
                    {
                        "q": "As the frequency falls towards cutoff, what happens to the group velocity?",
                        "opts": ["It goes to zero", "It goes to $c$", "It goes to infinity", "It is unchanged"],
                        "a": 0,
                        "why": r"""
It stalls. At cutoff the wave is bouncing straight across the guide with no forward
component at all, so the energy makes no progress and $v_g \to 0$ while $v_p \to \infty$
— their product still $c^2$. This is why the usable band of a guide starts comfortably
*above* cutoff, typically at $1.25f_c$: right at the edge the delay becomes enormous and
violently frequency-dependent.
""",
                    },
                    {
                        "q": "A short pulse is sent down a dispersive guide. What happens to it?",
                        "opts": [
                            "It spreads out, because its frequency components arrive at different times",
                            "It attenuates but keeps its shape",
                            "It arrives unchanged if the guide is lossless",
                            "It splits into two pulses",
                        ],
                        "a": 0,
                        "why": r"""
Dispersion spreads pulses. A short pulse is wide in frequency, and in a guide each of
those frequencies has its own $v_g$, so the components that started together arrive
apart. Losslessness does not help at all — no energy is lost, it is redistributed in
time, which is exactly why a lossless fibre still limits bit rate. The delay *spread*
is the quantity the lab computes, and it is what sets how close together two symbols
may be sent.
""",
                    },
                ],
            },
            "lab": {
                "title": "Measure the two velocities, and the delay spread they cause",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Six functions, all in SI, all above cutoff unless stated.

- `beta(f, fc)` returns $(2\pi f/c)\sqrt{1 - (f_c/f)^2}$, or `0.0` at or below cutoff.
- `phase_velocity(f, fc)` returns $c/\sqrt{1 - (f_c/f)^2}$, or `float("inf")` at or
  below cutoff.
- `group_velocity(f, fc)` returns $c\sqrt{1 - (f_c/f)^2}$, or `0.0` at or below cutoff.
- `group_velocity_numeric(f, fc, df)` estimates $d\omega/d\beta$ by a central
  difference: $2\pi \cdot 2 \cdot df$ divided by $\beta(f + df) - \beta(f - df)$.
  Return `float("inf")` if that denominator comes out as zero, so a half-finished
  `beta` gives a wrong answer rather than a crash.
- `group_delay(f, fc, length)` returns `length / group_velocity(f, fc)`.
- `delay_spread(f_lo, f_hi, fc, length)` returns the absolute difference between the
  group delays at the two band edges. That number is the pulse smearing a run of guide
  imposes on a signal occupying that band.

The point of `group_velocity_numeric` is to check your own algebra: it should agree
with the closed form to about ten significant figures.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90_FC = 6.5571403762e9


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    # TODO
    return 0.0


def phase_velocity(f, fc):
    """Speed of the phase pattern along the axis, in m/s."""
    # TODO
    return 0.0


def group_velocity(f, fc):
    """Speed of the envelope along the axis, in m/s."""
    # TODO
    return 0.0


def group_velocity_numeric(f, fc, df):
    """Central-difference estimate of d(omega)/d(beta) at f."""
    # TODO: guard against a zero denominator.
    return 0.0


def group_delay(f, fc, length):
    """Time for the envelope to cross `length` metres of guide."""
    # TODO
    return 0.0


def delay_spread(f_lo, f_hi, fc, length):
    """How much later the low edge of a band arrives than the high edge."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print("vp at 10 GHz:", phase_velocity(10e9, WR90_FC))
    print("vg at 10 GHz:", group_velocity(10e9, WR90_FC))
    print("spread 8-12 GHz over 10 m:", delay_spread(8e9, 12e9, WR90_FC, 10.0), "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90_FC = 6.5571403762e9


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    if f <= fc:
        return 0.0
    return 2.0 * np.pi * f / C_LIGHT * float(np.sqrt(1.0 - (fc / f) ** 2))


def phase_velocity(f, fc):
    """Speed of the phase pattern along the axis, in m/s."""
    if f <= fc:
        return float("inf")
    return C_LIGHT / float(np.sqrt(1.0 - (fc / f) ** 2))


def group_velocity(f, fc):
    """Speed of the envelope along the axis, in m/s."""
    if f <= fc:
        return 0.0
    return C_LIGHT * float(np.sqrt(1.0 - (fc / f) ** 2))


def group_velocity_numeric(f, fc, df):
    """Central-difference estimate of d(omega)/d(beta) at f."""
    db = beta(f + df, fc) - beta(f - df, fc)
    if db == 0.0:
        return float("inf")
    return 2.0 * np.pi * (2.0 * df) / db


def group_delay(f, fc, length):
    """Time for the envelope to cross `length` metres of guide."""
    vg = group_velocity(f, fc)
    if vg <= 0.0:
        return float("inf")
    return length / vg


def delay_spread(f_lo, f_hi, fc, length):
    """How much later the low edge of a band arrives than the high edge."""
    return abs(group_delay(f_lo, fc, length) - group_delay(f_hi, fc, length))


if __name__ == "__main__":
    print("vp at 10 GHz:", phase_velocity(10e9, WR90_FC))
    print("vg at 10 GHz:", group_velocity(10e9, WR90_FC))
    print("spread 8-12 GHz over 10 m:", delay_spread(8e9, 12e9, WR90_FC, 10.0), "s")
'''}],
                "hints": [
                    "Write the factor $\\sqrt{1 - (f_c/f)^2}$ once and reuse it — the phase velocity divides by it and the group velocity multiplies by it.",
                    "`group_velocity_numeric` needs `df` small compared with `f` but not so small that the two betas round to the same float. With `f` at 10 GHz, `df` of 1 kHz gives about ten good digits.",
                    "A group velocity of zero would make `group_delay` divide by zero, so return infinity there instead.",
                    "`delay_spread` should be positive: the *lower* frequency is the slower one, because it sits nearer cutoff.",
                ],
                "tests": [
                    {"name": "the phase pattern outruns light", "code": r'''
_vp = phase_velocity(10e9, 6.5571403762e9)
assert abs(_vp - 3.9707119211e8) < 1e2, \
    f"c over sqrt(1 - (6.557/10)^2) is 3.9707e8 m/s, got {_vp:.6e}"
assert _vp > 2.99792458e8, \
    "the phase velocity in a guide is always above c, which is allowed because it carries nothing"
'''},
                    {"name": "the envelope does not", "code": r'''
_vg = group_velocity(10e9, 6.5571403762e9)
assert abs(_vg - 2.2634610533e8) < 1e2, \
    f"c times sqrt(1 - (6.557/10)^2) is 2.2635e8 m/s, got {_vg:.6e}"
assert _vg < 2.99792458e8, "the group velocity must stay below c"
assert group_velocity(6.0e9, 6.5571403762e9) == 0.0, \
    "below cutoff nothing travels, so the group velocity is zero"
'''},
                    {"name": "the product of the two velocities is c squared", "code": r'''
_fc = 6.5571403762e9
for _f in (7e9, 10e9, 12e9, 40e9):
    _p = phase_velocity(_f, _fc) * group_velocity(_f, _fc)
    assert abs(_p / (2.99792458e8 ** 2) - 1.0) < 1e-12, \
        f"vp*vg should equal c^2 at every frequency; at {_f / 1e9} GHz it was {_p:.6e}"
'''},
                    {"name": "the numeric derivative agrees with the algebra", "code": r'''
_fc = 6.5571403762e9
_num = group_velocity_numeric(10e9, _fc, 1e3)
_ana = group_velocity(10e9, _fc)
assert _ana > 0.0, "group_velocity must be finished before this check means anything"
assert abs(_num - _ana) / _ana < 1e-8, \
    f"the central difference should reproduce the closed form: {_num:.10e} against {_ana:.10e}"
assert abs(_num - 2.2634610534e8) < 1e2, \
    f"and it should land on 2.2635e8 m/s, got {_num:.6e}"
'''},
                    {"name": "beta is what the derivative is taken of", "code": r'''
_fc = 6.5571403762e9
_b = beta(10e9, _fc)
assert abs(_b - 158.2382563130) < 1e-6, f"beta at 10 GHz is 158.24 rad/m, got {_b}"
assert beta(6e9, _fc) == 0.0, "there is no real beta below cutoff"
assert beta(12e9, _fc) > _b, "beta rises with frequency, and faster than linearly near cutoff"
'''},
                    {"name": "delay grows as cutoff is approached", "code": r'''
_fc = 6.5571403762e9
_t10 = group_delay(10e9, _fc, 10.0)
assert abs(_t10 - 4.41801284e-8) < 1e-14, \
    f"10 m at 2.2635e8 m/s takes 44.18 ns, got {_t10 * 1e9:.4f} ns"
assert group_delay(7e9, _fc, 10.0) > 2.0 * _t10, \
    "at 7 GHz, just above cutoff, the same 10 m should take more than twice as long"
'''},
                    {"name": "a wide band smears across a long run", "code": r'''
_fc = 6.5571403762e9
_s = delay_spread(8e9, 12e9, _fc, 10.0)
assert abs(_s - 1.839803e-8) < 1e-13, \
    f"8 to 12 GHz over 10 m spreads by 18.40 ns, got {_s * 1e9:.4f} ns"
assert _s > 0.0, "the two edges of the band do not arrive together"
assert abs(delay_spread(8e9, 12e9, _fc, 1.0) * 10.0 - _s) < 1e-15, \
    "the spread is proportional to length, so ten times the guide is ten times the smear"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Push a pulse through a waveguide and measure what it costs",
        "runtime": "python",
        "minutes": 115,
        "brief": r'''
Everything so far has been a formula. This is the formula applied to a signal.

You are given a probe waveform in `guide.py`: a Gaussian-envelope burst at a carrier
you choose, sampled at 80 GS/s over 4096 samples, plus a small seeded noise floor so
the numbers are not suspiciously clean. Build the machinery that carries it down a run
of WR-90 and then measure the two things a link designer actually cares about — when
it arrives, and how much wider it is when it does.

Build:

1. `mode_table(a, b, mmax, nmax)` and `single_mode_band(a, b)`, as in module 3, so you
   can state which band the guide is usable over before you use it.
2. `transfer(freqs, fc, length)` — the complex frequency response of `length` metres
   of guide, as a numpy array the same shape as `freqs`. Above cutoff it is
   $e^{-j\beta \ell}$ with $\beta = (2\pi f/c)\sqrt{1 - (f_c/f)^2}$; at or below cutoff
   it is the real attenuation $e^{-\alpha \ell}$ with
   $\alpha = (2\pi f_c/c)\sqrt{1 - (f/f_c)^2}$.
3. `propagate(x, fs, fc, length)` — real signal in, real signal out, via
   `np.fft.rfft`, a multiply by `transfer` evaluated at `np.fft.rfftfreq`, and
   `np.fft.irfft` with `n=x.size`.
4. `energy_centroid(x, fs)` and `rms_width(x, fs)` — the mean and the standard
   deviation of time under the weight $x^2$.

## Suggested order

Get `transfer` right first and check it by hand at a single frequency: its magnitude
must be exactly 1 above cutoff, because a lossless guide moves energy without taking
any. Then `propagate` is four lines, and the two measurement functions are three each.

## The one trap

The FFT convolves circularly. The probe sits 5 ns into a 51.2 ns window, so anything
delayed by more than about 45 ns wraps round to the start and your centroid becomes
nonsense. Keep the runs short enough that it does not — a few metres of WR-90 at 10 GHz
delays by a few nanoseconds per metre, so this is a real constraint, not a hypothetical.
''',
        "deliverables": [
            "`mode_table` and `single_mode_band`, giving the usable band of the guide before any signal is sent down it.",
            "`transfer(freqs, fc, length)` returning a complex numpy array: unit magnitude above cutoff, real exponential decay below it.",
            "`propagate(x, fs, fc, length)` moving a real waveform through the guide by rfft, multiply, irfft — no loops over samples.",
            "`energy_centroid` and `rms_width`, both weighted by $x^2$, used to measure arrival time and pulse width.",
            "A comment at the top of `main.py` naming the carrier and the run length you chose, and the group delay you expect at that carrier.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy and no signal-processing package.",
            "`transfer` must be vectorised over the frequency array; no Python loop over bins.",
            "The magnitude of the response above cutoff must be exactly 1 to floating-point precision. A guide with perfect walls is lossless.",
            "Do not divide by `f` without guarding the zero-frequency bin, which `np.fft.rfftfreq` always includes.",
            "Keep the run short enough that the delayed pulse stays inside the 51.2 ns window.",
        ],
        "rubric": [
            {"criterion": "Mode analysis", "weight": 20,
             "evidence": "The mode table is complete and sorted, and the single-mode band of WR-90 comes out as 6.557 to 13.114 GHz including the degenerate case of a square guide."},
            {"criterion": "Transfer function", "weight": 30,
             "evidence": "Magnitude is exactly 1 above cutoff and matches the analytic exponential below it, with the zero-frequency bin handled rather than producing a NaN."},
            {"criterion": "Propagation", "weight": 30,
             "evidence": "A burst propagated through the guide is delayed by the group delay to within one per cent, energy is conserved above cutoff, and two runs in series equal one run of the combined length."},
            {"criterion": "Measurement", "weight": 20,
             "evidence": "The centroid and RMS width are computed under an energy weighting and show the pulse widening monotonically with the length of guide it has crossed."},
        ],
        "hints": [
            "`np.fft.rfftfreq(n, 1.0/fs)` gives the frequencies of the bins `np.fft.rfft` returns, in the same order and length.",
            "Build the propagating and the evanescent branches separately with a boolean mask, and substitute a safe dummy frequency into the branch you are about to discard so no division by zero ever happens.",
            "`np.exp(-1j * b * length)` has magnitude 1 for real `b`, which is the lossless condition you are asked to preserve exactly.",
            "For the centroid, the time axis is `np.arange(x.size) / fs` and the weight is `x * x`. Both measurement functions are the same two lines with a different final step.",
            "Check `propagate(x, fs, fc, 0.0)` returns the input back: at zero length the transfer function is all ones and the round trip through the FFT should be exact to about 1e-15.",
        ],
        "files": [
            {"name": "guide.py", "ro": True, "content": r'''
"""The guide, the sampling setup and the probe waveform. Do not edit."""
import numpy as np

C_LIGHT = 2.99792458e8
WR90 = (0.02286, 0.01016)   # a, b in metres — standard X-band guide
FS = 80e9                   # sampling rate, samples per second
NSAMP = 4096                # 51.2 ns of record


def probe(f0, seed=11, fs=FS, n=NSAMP, t0=5e-9, width=0.4e-9):
    """A Gaussian burst at carrier f0, sitting t0 into the record, plus noise.

    The noise is small (1e-4 RMS against a unit envelope) and seeded, so every run
    of the checks sees exactly the same waveform.
    """
    t = np.arange(n) / fs
    envelope = np.exp(-((t - t0) ** 2) / (2.0 * width * width))
    rng = np.random.default_rng(seed)
    return envelope * np.cos(2.0 * np.pi * f0 * t) + 1e-4 * rng.standard_normal(n)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from guide import C_LIGHT, WR90, FS, NSAMP, probe

# Link chosen:
#   carrier      -> TODO, and why it sits inside the single-mode band
#   run length   -> TODO
#   expected group delay at that carrier -> TODO


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode; infinite for (0, 0)."""
    # TODO
    return 0.0


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    # TODO
    return []


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    # TODO
    return (0.0, 0.0)


def transfer(freqs, fc, length):
    """Complex response of `length` metres of guide at each frequency in `freqs`."""
    # TODO: propagating above cutoff, evanescent at or below it.
    return np.zeros(np.asarray(freqs, dtype=float).shape, dtype=complex)


def propagate(x, fs, fc, length):
    """Send a real waveform through the guide and return what comes out."""
    # TODO: rfft, multiply by transfer at rfftfreq, irfft back.
    return np.zeros(np.asarray(x, dtype=float).shape)


def energy_centroid(x, fs):
    """Mean arrival time of the energy in x, in seconds."""
    # TODO
    return 0.0


def rms_width(x, fs):
    """Standard deviation of arrival time, weighted by energy, in seconds."""
    # TODO
    return 0.0


if __name__ == "__main__":
    a, b = WR90
    lo, hi = single_mode_band(a, b)
    print(f"single-mode band: {lo / 1e9:.3f} to {hi / 1e9:.3f} GHz")
    x = probe(10e9)
    y = propagate(x, FS, lo, 2.0)
    print("delay:", (energy_centroid(y, FS) - energy_centroid(x, FS)) * 1e9, "ns")
    print("width in:", rms_width(x, FS) * 1e12, "ps")
    print("width out:", rms_width(y, FS) * 1e12, "ps")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from guide import C_LIGHT, WR90, FS, NSAMP, probe

# Link chosen:
#   carrier      -> 10 GHz, comfortably inside the 6.557-13.114 GHz single-mode band
#                   of WR-90 and far enough above cutoff that vg is a sane 0.755 c
#   run length   -> 2 m, which delays the burst by 8.8 ns and leaves the pulse well
#                   inside the 51.2 ns record instead of wrapping round it
#   expected group delay at that carrier -> 2 / (c * sqrt(1 - (6.5571/10)^2))
#                                        =  8.836 ns


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode; infinite for (0, 0)."""
    if m == 0 and n == 0:
        return float("inf")
    return 0.5 * C_LIGHT * float(np.sqrt((m / a) ** 2 + (n / b) ** 2))


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    rows = []
    for m in range(mmax + 1):
        for n in range(nmax + 1):
            if m == 0 and n == 0:
                continue
            rows.append((cutoff(a, b, m, n), m, n))
    rows.sort()
    return rows


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    rows = mode_table(a, b, 3, 3)
    lo = rows[0][0]
    for fc, _m, _n in rows:
        if fc > lo * (1.0 + 1e-12):
            return (lo, fc)
    return (lo, float("inf"))


def transfer(freqs, fc, length):
    """Complex response of `length` metres of guide at each frequency in `freqs`."""
    f = np.asarray(freqs, dtype=float)
    H = np.zeros(f.shape, dtype=complex)
    above = f > fc

    # substitute a harmless frequency into the branch that is about to be discarded,
    # so neither the division nor the square root ever sees an invalid argument
    fa = np.where(above, f, 2.0 * fc)
    b = 2.0 * np.pi * fa / C_LIGHT * np.sqrt(np.maximum(1.0 - (fc / fa) ** 2, 0.0))
    H[above] = np.exp(-1j * b[above] * length)

    fb = np.where(above, 0.0, f)
    al = 2.0 * np.pi * fc / C_LIGHT * np.sqrt(np.maximum(1.0 - (fb / fc) ** 2, 0.0))
    H[~above] = np.exp(-al[~above] * length)
    return H


def propagate(x, fs, fc, length):
    """Send a real waveform through the guide and return what comes out."""
    x = np.asarray(x, dtype=float)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(x.size, 1.0 / fs)
    return np.fft.irfft(X * transfer(f, fc, length), n=x.size)


def energy_centroid(x, fs):
    """Mean arrival time of the energy in x, in seconds."""
    x = np.asarray(x, dtype=float)
    w = x * x
    total = float(w.sum())
    if total <= 0.0:
        return 0.0
    t = np.arange(x.size) / fs
    return float((t * w).sum() / total)


def rms_width(x, fs):
    """Standard deviation of arrival time, weighted by energy, in seconds."""
    x = np.asarray(x, dtype=float)
    w = x * x
    total = float(w.sum())
    if total <= 0.0:
        return 0.0
    t = np.arange(x.size) / fs
    mu = (t * w).sum() / total
    return float(np.sqrt((((t - mu) ** 2) * w).sum() / total))


if __name__ == "__main__":
    a, b = WR90
    lo, hi = single_mode_band(a, b)
    print(f"single-mode band: {lo / 1e9:.3f} to {hi / 1e9:.3f} GHz")
    x = probe(10e9)
    y = propagate(x, FS, lo, 2.0)
    print("delay:", (energy_centroid(y, FS) - energy_centroid(x, FS)) * 1e9, "ns")
    print("width in:", rms_width(x, FS) * 1e12, "ps")
    print("width out:", rms_width(y, FS) * 1e12, "ps")
'''},
        ],
        "tests": [
            {"name": "the usable band of WR-90 is found before anything is sent", "code": r'''
from guide import WR90
_lo, _hi = single_mode_band(*WR90)
assert abs(_lo - 6.5571403762e9) < 1e3, \
    f"the band opens at the TE10 cutoff of 6.5571 GHz, got {_lo / 1e9:.4f} GHz"
assert abs(_hi - 1.3114280752e10) < 1e3, \
    f"and closes where TE20 arrives at 13.114 GHz, got {_hi / 1e9:.4f} GHz"
_t = mode_table(*WR90, 2, 2)
assert [(m, n) for _f, m, n in _t[:3]] == [(1, 0), (2, 0), (0, 1)], \
    f"the three lowest modes are TE10, TE20, TE01 in that order, got {[(m, n) for _f, m, n in _t[:3]]}"
'''},
            {"name": "a lossless guide passes what it passes without loss", "code": r'''
import numpy as np
_fc = 6.5571403762e9
_H = transfer(np.array([7e9, 10e9, 12e9, 30e9]), _fc, 2.0)
assert _H.shape == (4,), f"transfer should be shaped like its input, got {_H.shape}"
for _h, _f in zip(_H, [7e9, 10e9, 12e9, 30e9]):
    assert abs(abs(_h) - 1.0) < 1e-12, \
        f"above cutoff the magnitude must be exactly 1; at {_f / 1e9} GHz it was {abs(_h)}"
assert abs(_H[1] - np.exp(-1j * 158.2382563130 * 2.0)) < 1e-6, \
    "the phase must be -beta*length, with beta = 158.238 rad/m at 10 GHz"
'''},
            {"name": "below cutoff the guide is a wall, and DC is handled", "code": r'''
import numpy as np
_fc = 6.5571403762e9
_H = transfer(np.array([0.0, 4e9]), _fc, 0.05)
assert np.all(np.isfinite(_H)), \
    "the zero-frequency bin must not produce a NaN — guard the division by f"
assert abs(_H[1].imag) < 1e-15, "an evanescent mode has no phase progression, only decay"
assert abs(abs(_H[1]) - 0.0043188298) < 1e-8, \
    f"5 cm at 4 GHz should attenuate to 0.00432, got {abs(_H[1]):.7f}"
assert abs(abs(_H[0]) - 0.0010370501) < 1e-8, \
    f"and DC, furthest below cutoff, to 0.00104, got {abs(_H[0]):.7f}"
'''},
            {"name": "zero length changes nothing", "code": r'''
import numpy as np
from guide import FS, probe
_x = probe(10e9)
_y = propagate(_x, FS, 6.5571403762e9, 0.0)
assert np.asarray(_y).shape == _x.shape, f"the output must match the input length, got {np.asarray(_y).shape}"
assert np.abs(np.asarray(_y) - _x).max() < 1e-12, \
    "with no guide at all, rfft then irfft should hand the waveform straight back"
'''},
            {"name": "the burst arrives at the group velocity", "code": r'''
import numpy as np
from guide import FS, probe, C_LIGHT
_fc = 6.5571403762e9
_x = probe(10e9)
_y = propagate(_x, FS, _fc, 2.0)
_t_in = energy_centroid(_x, FS)
_t_out = energy_centroid(_y, FS)
assert abs(_t_in - 5.0e-9) < 5e-11, \
    f"the probe sits 5 ns into the record, so its centroid should be there, got {_t_in * 1e9:.4f} ns"
_vg = C_LIGHT * np.sqrt(1.0 - (_fc / 10e9) ** 2)
_want = 2.0 / _vg
_got = _t_out - _t_in
assert abs(_got - _want) / _want < 0.01, \
    f"2 m at vg = 2.263e8 m/s is 8.836 ns of delay, measured {_got * 1e9:.4f} ns"
'''},
            {"name": "no energy is lost inside the band", "code": r'''
import numpy as np
from guide import FS, probe
_x = np.asarray(probe(10e9), dtype=float)
_y = np.asarray(propagate(_x, FS, 6.5571403762e9, 2.0), dtype=float)
_ein = float((_x * _x).sum())
_eout = float((_y * _y).sum())
assert _ein > 1.0, "the probe should carry real energy before anything is propagated"
assert abs(_eout / _ein - 1.0) < 1e-3, \
    f"a lossless guide conserves energy above cutoff: in {_ein:.4f}, out {_eout:.4f}"
'''},
            {"name": "the pulse widens the further it goes", "code": r'''
import numpy as np
from guide import FS, probe
_fc = 6.5571403762e9
_x = probe(10e9)
_w0 = rms_width(_x, FS)
_w1 = rms_width(propagate(_x, FS, _fc, 1.0), FS)
_w3 = rms_width(propagate(_x, FS, _fc, 3.0), FS)
assert abs(_w0 - 2.8441955603e-10) < 1e-13, \
    f"the undisturbed burst is 284.4 ps wide by this measure, got {_w0 * 1e12:.2f} ps"
assert _w1 > _w0, f"one metre should already widen it: {_w1 * 1e12:.2f} against {_w0 * 1e12:.2f} ps"
assert _w3 > _w1 * 1.2, \
    f"three metres should widen it substantially more: {_w3 * 1e12:.2f} against {_w1 * 1e12:.2f} ps"
'''},
            {"name": "two runs in series equal one long run", "code": r'''
import numpy as np
from guide import FS, probe
_fc = 6.5571403762e9
_x = probe(10e9)
_one = np.asarray(propagate(_x, FS, _fc, 2.0), dtype=float)
_two = np.asarray(propagate(propagate(_x, FS, _fc, 1.0), FS, _fc, 1.0), dtype=float)
assert np.abs(_one).max() > 0.1, "the propagated burst should not be empty"
assert np.abs(_one - _two).max() < 1e-6, \
    "a guide is linear and time-invariant, so 1 m twice must equal 2 m once"
'''},
            {"name": "driving below cutoff gets almost nothing through", "code": r'''
import numpy as np
from guide import FS, probe
_fc = 6.5571403762e9
_x = np.asarray(probe(4e9), dtype=float)
_y = np.asarray(propagate(_x, FS, _fc, 0.05), dtype=float)
_ratio = float((_y * _y).sum()) / float((_x * _x).sum())
assert _ratio < 1e-4, \
    f"5 cm of guide below cutoff should reject the burst, but {_ratio:.3e} of the energy got through"
assert _ratio > 1e-7, \
    "some energy must survive: the probe's noise floor is broadband and part of it lies above cutoff"
'''},
        ],
    },
}
