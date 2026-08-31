"""EE101 — Circuit Analysis I: Direct Current.

The first course of the EE degree. It assumes school mathematics and nothing else:
no prior circuits, no prior programming beyond arithmetic. Every term is defined
where it is first used.

Authoring rules, as for every course module:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; this course uses neither beyond `math`
  * every expected number was produced by running the code, not assumed
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it to the reference drawing
"""

COURSE = {
    "id": "EE101",
    "title": "Circuit Analysis I — Direct Current",
    "band": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "◉",
    "summary": (
        "Everything electrical starts here: what a current actually is, what a voltage "
        "actually measures, and the two conservation laws that between them decide every "
        "node voltage in every circuit you will ever draw. Direct current means nothing "
        "changes with time, which strips the subject down to arithmetic and lets the "
        "reasoning be the hard part. By the end you can look at a resistor network and "
        "say what every voltage, every current and every watt in it will be."
    ),
    "outcomes": [
        "State what charge, current, voltage, resistance and power are, in words and in units, without reaching for a formula sheet.",
        "Apply Ohm's law and the series and parallel combination rules to reduce a resistor network to a single number.",
        "Use Kirchhoff's current and voltage laws to find an unknown current or voltage in a network that does not reduce by inspection.",
        "Design a voltage divider that meets a required output voltage under a stated load and a stated current budget.",
        "Account for every watt a supply delivers, and check a solution by conservation of energy.",
        "Solve a network that does not reduce by inspection, by nodal analysis or by mesh analysis, and judge which of the two will be less work before starting.",
        "Separate the contributions of two sources by superposition, and replace any two-terminal network with its Thévenin or Norton equivalent.",
        "Account for a source's internal resistance, a cable's resistance and a component's tolerance, and state what a circuit does at its worst corner rather than only on paper.",
    ],
    "assessment": (
        "Eleven quizzes, eight circuits drawn and measured in the schematic editor, three "
        "guided derivations, two slider exercises against a stated target, six short "
        "Python labs checked by execution, and a capstone that solves an arbitrary "
        "resistor network from first principles."
    ),
    "reading": [
        "*The Art of Electronics*, Horowitz & Hill — chapter 1, sections 1.1 to 1.4.",
        "*Fundamentals of Electric Circuits*, Alexander & Sadiku — chapters 1 to 4, for many worked examples of the systematic methods.",
        "MIT OCW 6.002, first two lectures, freely available.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Charge, current and voltage",
            "summary": "Three quantities and their units. Get these right and the rest of the course is arithmetic.",
            "concepts": [
                "Charge is a property of matter, measured in coulombs (C). One electron carries $-1.602176634\\times10^{-19}$ C.",
                "Current is charge per unit time: $I = Q/t$. One ampere is one coulomb passing a point every second.",
                "Conventional current is drawn in the direction positive charge would move. In a metal the electrons actually drift the other way, and no calculation in this course notices.",
                "Voltage between two points is energy per unit charge: $V = E/Q$. One volt is one joule handed to every coulomb that makes the trip.",
                "A voltage is always *between* two points. 'The voltage at node A' is shorthand for the voltage between node A and whatever was chosen as ground.",
                "Going round a circuit, charge is never used up — energy is. A bulb returns every electron it is given, at a lower energy.",
                "Direct current (DC) means nothing changes with time: every current and every voltage is one fixed number.",
            ],
            "read": [
                {
                    "title": "What a current actually is",
                    "minutes": 13,
                    "body": r'''
A copper wire is not empty, waiting for you to close the switch. Every copper atom in
it has already handed one electron to the metal as a whole, and those electrons belong
to no particular atom any more: they rattle through the lattice at around a million
metres a second, in every direction at once. A centimetre of ordinary hookup wire
holds something like $10^{21}$ of them, and all of that is going on before anything is
connected to anything.

It is not a current, because it has no preferred direction. As much charge crosses any
plane through the wire one way as crosses it the other, and the net transfer is zero.
A current is what you get when that jostling acquires a slight bias — and *slight* is
the right word, as the drift-speed calculation below will show.

Holding that picture is worth the effort, because most of the wrong intuitions about
circuits come from the other one: the wire as an empty pipe, the battery as a
reservoir, and electricity as water waiting to be let in. The wire is not empty. It is
already full along its whole length before the switch is touched, and the battery does
not fill it — it pushes what is already there.

## Charge, and why its numbers are so awkward

Charge is a property matter has, in the way mass is. Two things separate it from mass,
and both of them matter here.

The first is that it comes in two signs. Mass only ever attracts, so it piles up.
Charge attracts and repels, so ordinary matter arranges itself into neutral lumps and
stays that way: a copper wire holds exactly as many electrons as protons and reads zero
on any instrument looking for net charge, even while it is carrying thirty amps. Bulk
matter is neutral to an extraordinary precision, and it is held there by how violently
it objects to being otherwise.

The second is that charge comes in whole multiples of one indivisible lump — the charge
carried by a single electron, $-1.602176634\times10^{-19}$ coulombs. Since 2019 that
figure has been exact by definition: the SI fixes the electron's charge and derives the
ampere from it, rather than the other way round.

Run the division and one coulomb comes to about $6.24\times10^{18}$ electrons. Both
halves of that are worth holding at once: a coulomb is an enormous pile of elementary
charges, and an entirely unremarkable everyday quantity. A torch bulb pushes one
through itself every couple of seconds.

There is a third property, and this course leans on it harder than on either of the
others: charge is conserved. Not usually, not approximately. Charge cannot be created
at a point, destroyed at a point, or used up by a component; it can only move. Two
modules from now that sentence acquires a name — Kirchhoff's current law — and an
equation to go with it. It is worth noticing in advance that it is not a new fact about
circuits. It is this old fact about charge, written down for a junction.

## Worked: how many electrons is an ordinary current?

An indicator LED runs at 20 mA for three hours. How many electrons is that?

```
I = 20 mA = 0.020 A
t = 3 h   = 3 * 3600                         = 10 800 s

charge moved      Q = I t
                    = 0.020 * 10800          = 216 C

electrons         N = Q / q
                    = 216 / 1.602e-19        = 1.35e21 electrons

in a chemist's units
                      216 / 96485 C per mol  = 2.24e-3 mol of electrons
```

Over a thousand billion billion electrons went through one small red LED while you ate
dinner, and the whole shipment weighs 1.2 micrograms.

The last line is the one worth keeping. 96 485 coulombs per mole — the charge on a
mole of electrons — is the Faraday constant, and it is the bridge between this subject
and electrochemistry: it is what says how much metal a plating bath deposits per
amp-hour. A coulomb is a colossal number of electrons and a very small amount of
chemistry.

## Current is a rate, and that is the whole of it

$$I = \frac{Q}{t}$$

Choose a plane across the wire, count the net charge that crosses it, divide by how
long you watched. One coulomb per second is one ampere. Nothing is hidden underneath
that definition, and two refinements finish it off.

The first is that $Q/t$ is an **average**. If the current was not the same throughout
the interval, this is what it averaged over that interval, in the way that 300 km in
four hours is an average speed and says nothing whatever about the traffic. The
instantaneous current is the same definition taken on a vanishing interval,
$i = \mathrm{d}q/\mathrm{d}t$. In direct current the two are the same number and the
distinction never bites — except in the section below on currents that are not steady,
which is the one place in this module where something is allowed to change.

The second is that a current has a sign, and the sign means nothing until an arrow has
been drawn. "The current in $R_3$ is 4 mA" is not a complete statement; "the current in
$R_3$ is 4 mA, downwards" is. Mark the arrow first, solve, and then read the sign off
the answer.

Past those two, essentially every remaining mistake with $I = Q/t$ is a unit. $t$ is in
**seconds**, always. Questions get asked in minutes and milliseconds precisely because
that is where the marks are.

It helps to know roughly what these numbers mean:

```
1 pA     leakage that a good instrument can just about see
1 µA     a real-time clock ticking in a device that is switched off
1 mA     a sensor idling; an indicator LED wants 5-20 mA
100 mA   a phone screen at moderate brightness
1 A      a laptop charger's output; a car sidelight
10 A     a kettle element; the wiring of a domestic ring main
100 A    a car starter motor, briefly
```

## Worked: how fast do the electrons actually go?

Take 1.5 mm² wire — a common size for mains flex — carrying 3.0 A. Copper offers about
$8.5\times10^{28}$ free electrons per cubic metre. How long does one of them take to
travel a metre?

```
n = 8.5e28 electrons per m^3         A = 1.5 mm^2 = 1.5e-6 m^2
q = 1.602e-19 C per electron         I = 3.0 A

electrons in one metre of wire  = n * A * 1 m
                                = 8.5e28 * 1.5e-6       = 1.275e23

mobile charge in that metre     = 1.275e23 * 1.602e-19  = 20 425 C

time for all of it to pass      = 20 425 C / 3.0 A      = 6 808 s

drift speed                     = 1 m / 6 808 s         = 1.47e-4 m/s
                                                        = 0.15 mm/s
```

One hour and fifty-three minutes to cross a one-metre lead. That is not a misprint and
it is not a contrived case: drift speeds in ordinary wiring are always about this size,
because the supply of carriers is so enormous that a minute bias in their motion
already amounts to amperes.

Push on the numbers and they barely move. Ten times the current — 30 A in the same
wire — gives 1.5 mm/s. The same 3 A in thinner 0.5 mm² wire gives 0.44 mm/s, three
times faster, because there is a third as much mobile charge per metre to carry it.
Nothing plausible gets the answer anywhere near a speed you would notice.

Notice the shape of that calculation: the current was divided by the mobile charge per
metre of wire, which is $nAq$. Written out, that is $v = I/(nAq)$, and building it
properly from the two definitions is what this module's derivation exercise does.

## Why the lamp lights immediately anyway

Nothing was waiting for an electron to make the journey. The wire is already full of
them along its whole length — including the ones sitting inside the filament. Closing
the switch establishes a field along the conductor at an appreciable fraction of the
speed of light, and every electron in the circuit, everywhere, begins drifting at once.
What travels quickly is the instruction. What travels slowly is the charge.

A tube packed end to end with ball bearings behaves the same way: push one in at your
end and one falls out of the far end immediately, though no individual bearing has gone
anywhere much. So does a train of goods wagons once the slack is taken up.

Put a number on it. On a one-metre lead the field is established in roughly
$1\ \text{m} / (2\times10^{8}\ \text{m/s}) \approx 5$ ns, and in five nanoseconds an
electron drifting at 0.15 mm/s has moved about $7\times10^{-13}$ m — a few thousandths
of the spacing between two copper atoms. The lamp is at full brightness long before any
electron has crossed a single atom.

## When the current is not steady

Direct current means nothing changes with time, and for the rest of this course nothing
will. It is worth seeing once what the definition does when something changes, because
reaching for the average is a habit that pays for itself.

A battery-powered sensor node wakes up, takes a reading, transmits it and goes back to
sleep. Awake it draws 42 mA, the wake lasts 18 ms, and it does this once every 2 s. In
between it draws 6 µA keeping its clock running. What empties the cell is neither the
42 mA nor the 6 µA but the average of the two, weighted by how long each one lasts —
because $Q = It$ is a statement about charge, and charge is what the cell holds a fixed
amount of.

```
one 2 s cycle:

  awake    Q1 = I t = 0.042 A * 0.018 s     = 7.560e-4 C
  asleep   Q2 = I t = 6e-6 A  * 1.982 s     = 0.119e-4 C
                                              ----------
  charge per cycle                            7.679e-4 C

  average current = Q / t
                  = 7.679e-4 C / 2.0 s      = 3.84e-4 A
                                            = 0.384 mA

  on a 1200 mAh cell:
       runtime    = 1200 mA h / 0.384 mA    = 3 125 h
                                            = 130 days
```

Two things fall out of that, and both are worth carrying forward. The sleep current,
which looks like nothing at all next to 42 mA, still contributes 1.5% of the charge per
cycle — and halving it, which is real engineering effort, would buy about one extra day
out of a hundred and thirty. Meanwhile the peak, 42 mA, appears nowhere in the runtime
at all. It matters for something else entirely: whether the cell and the wiring can
supply it without the voltage sagging, which is the subject of a later module.

## The direction nobody managed to fix in time

Conventional current is drawn in the direction positive charge would move: out of the
$+$ terminal of a source, round the external circuit, back into the $-$. In a metal the
carriers are electrons, which are negative and therefore drift the other way. The
convention is Franklin's, from the 1750s; the electron turned up in 1897; every formula
in this course was written to match the older guess.

It makes no difference to any calculation. A negative charge moving left transports
exactly the same net charge per second across a plane as a positive charge moving
right, so the two are the same current with the same sign — flipping the sign of the
carrier and flipping its direction of travel are two sign changes that cancel.

So mark a direction on the drawing before you solve, work with it, and if the answer
comes out negative it means the current runs the other way. That is information, not an
error. Assigning a reference direction and then trusting the sign is the single most
useful habit in this course: from the nodal-analysis module onwards you will routinely
assign directions to currents you could not possibly have guessed.

## The mistake people actually make

Nearly everyone, at some point, believes that a component consumes current — that
500 mA goes into a lamp and something less comes out of the other side. It is worth
understanding why that is tempting, because the reason it is tempting is the reason it
is wrong.

It is tempting because something genuinely is being used up. The battery does go flat.
The lamp does get hot. The word on the electricity bill is *consumption*, and the bill
does go up when you switch things on. All of that is true — but the thing being used up
is energy, not charge. Every coulomb that goes into the lamp comes out of the lamp, in
the same second, poorer by however many joules the lamp took off it.

One test settles it. Put an ammeter on each side of the lamp: they read the same. They
read the same for a 1 W indicator and for a 2 kW heater, and every meter in a series
chain of ten different components reads what every other one reads. If they did not,
charge would be accumulating inside something, and the field from even a microscopic
excess would be large enough to stop the current dead within microseconds. Circuits do
not do this. They cannot.

The same misconception has a second head: that the current "leaves the battery" and "is
used up before it gets back". Trace the loop. Whatever leaves one terminal arrives at
the other, in the same second, in the same amount. A cell is not a tank of current with
a level in it. It is a pump.

## Where this picture stops being true

- In a semiconductor some of the carriers are *holes*: vacancies in the bonding
  structure that move as though they were positive particles. Both signs of carrier are
  then in play, and both contribute to the same current in the same direction. EE201 is
  where that starts to matter; here, everything is metal.
- In an electrolyte, in a nerve, or inside a battery's own chemistry, the carriers are
  ions. Sodium drifting one way and chloride drifting the other are not two currents
  cancelling — they are two contributions to a single current, in the same direction.
  In a spark or a vacuum tube there is no lattice at all, and the carrier density is
  whatever the source of carriers is doing.
- $I = nAvq$ assumes one kind of carrier drifting uniformly through a uniform
  cross-section. It describes a copper wire very well and a fluorescent tube very badly.
  EE141 takes the same slug of wire further and gets resistivity out of it.
- Raise the frequency and the current stops being spread evenly across the
  cross-section, crowding towards the surface instead, so the $A$ in $nAvq$ is no longer
  the whole of the wire. Direct current never meets that; EE102 does.
''',
                },
                {
                    "title": "What a voltage actually measures",
                    "minutes": 13,
                    "body": r'''
"The voltage at node A" is a phrase everyone uses and nobody means literally. A single
point no more has a voltage than a single town has a distance. Voltage is a
relationship between *two* points, and the shorthand works only because one of the two
was agreed on in advance and then stopped being mentioned.

## A staircase, and a sack of flour

Carry a 10 kg sack up a flight of stairs and you do work on it. The sack gains
potential energy, and how much it gains depends only on the height — not on whether you
went up in one go or in three, not on which staircase you chose. Carry it back down and
you get the energy back.

Now divide that energy by the mass. For a 3 m rise,

$$\frac{E}{m} = gh = 9.81 \times 3 = 29.4\ \text{J per kg}$$

and that number describes the *staircase*, not the sack. It is the same for a 10 kg
sack and for a 2 kg one, and it lets you talk about the climb without mentioning what
is being carried up it.

Voltage is that number, with charge in place of mass. A component with 6 V across it is
a six-joules-per-coulomb staircase: every coulomb that goes down it gives up six
joules, whether they arrive at a milliamp or at an amp.

## Energy per unit charge

$$V = \frac{E}{Q}$$

Move a charge $Q$ from one point to another and some energy $E$ changes hands: the
charge either gains it or gives it up. Divide the one by the other and what is left
belongs to the two points alone. One joule handed to one coulomb is one volt.

The division is the whole point. The energy on its own depends on how much charge you
happened to move, which is a fact about your experiment rather than about the circuit.
Move twice the charge and twice the energy changes hands; the ratio does not budge.
That is what makes it a number worth writing on a schematic.

Signs are worth nailing down now, because later they cause more trouble than they
should. $V_{AB}$ means $V_A - V_B$. It is positive when a positive charge *loses*
energy going from A to B — when B is downhill of A. Swap the meter leads and you get
the same size with the other sign, which is the same physical statement told backwards.

That definition explains the two things beginners find strangest about circuits.

The first is that **a battery is not a supply of charge**. It is a supply of energy per
charge. The electrons a 9 V battery pushes into a circuit are the ones the circuit
already had; what the battery does is hand nine joules to every coulomb on its way
through, and accept an equal, discharged coulomb at the other terminal. Charge is
conserved all the way round the loop. Energy is not.

The second is what it means for a component to **"drop" a voltage**. A lamp with 6 V
across it is a place where each passing coulomb gives up six joules — as heat, as
light, as whatever that component does. Nothing is subtracted from the current. Just as
many coulombs leave the lamp as entered it, each poorer by 6 J.

## Worked: following the joules round a loop

A 9 V battery, two lamps in series, a steady 0.25 A for ten minutes. A meter says lamp
A has 6.0 V across it and lamp B has 3.0 V.

```
charge round the loop in 10 min  = I * t
                                 = 0.25 A * 600 s      =  150 C

energy the battery hands out     = Q * V
                                 = 150 C * 9.0 V       = 1350 J

energy given up in lamp A        = 150 C * 6.0 V       =  900 J
energy given up in lamp B        = 150 C * 3.0 V       =  450 J
                                                         ------
                                                         1350 J
```

The books balance, and they had to. The same 150 C made the trip; the 1350 J the
battery gave that charge is exactly the 1350 J the two lamps took back off it. Divide
by the 600 s and the battery is handing over 2.25 joules every second — a rate that
gets a name and a unit of its own in the next module.

Notice also that 6.0 and 3.0 add to 9.0. Each coulomb was given nine joules and had to
give all nine back before arriving where it started, because it ends the trip with
exactly the energy it began with. That is Kirchhoff's voltage law, two modules early,
and it is a conservation-of-energy statement rather than a new fact about circuits.

One more thing the example quietly demonstrates: the 0.25 A cancels out of the volts.
Had the current been 0.5 A, every energy in that block would double and the 6 V and the
3 V would be exactly as they were. Voltage is energy per coulomb, and a per-coulomb
quantity does not care how many coulombs there happened to be.

## Worked: why a D cell and a AAA cell both say 1.5 V

An alkaline cell works by oxidising zinc at one electrode and reducing manganese
dioxide at the other. Every time that reaction transfers one electron between them it
releases a fixed amount of energy — about $2.4\times10^{-19}$ J — fixed by the
chemistry and by nothing else.

```
energy released per electron   = 2.4e-19 J
charge carried per electron    = 1.602e-19 C

V = E / Q                      = 2.4e-19 / 1.602e-19   = 1.5 V
```

Nothing in that division mentions how big the cell is, and that is the point. Make the
electrodes fifteen times larger and each electron still gains the same
$2.4\times10^{-19}$ J, because it is still the same reaction; there are simply more
electrons available to run it. Chemistry fixes the volts, size fixes the coulombs.

```
                        AAA alkaline         D alkaline
capacity                 1200 mAh             18 000 mAh
                       = 1.2 A h            = 18 A h

charge   Q = I t       = 1.2 * 3600         = 18 * 3600
                       = 4 320 C            = 64 800 C

terminal voltage         1.5 V                1.5 V

energy   E = Q V       = 4320 * 1.5         = 64800 * 1.5
                       = 6 480 J            = 97 200 J
```

Fifteen times the energy at identical voltage. Both will run a 1.5 V torch bulb equally
brightly; the D cell will do it for fifteen times as long.

The same reasoning settles what happens when cells are combined. Four AAA cells in
series hand each coulomb 1.5 J four times over on its way through, so the stack reads
6 V and still holds 4 320 C: energy $4320 \times 6 = 25\,920$ J. Four in parallel each
carry a share of the charge, so each coulomb is handed 1.5 J once — still 1.5 V, but
now $4 \times 4320 = 17\,280$ C, and energy $17\,280 \times 1.5 = 25\,920$ J. The same
total, as it has to be: four cells hold four cells' worth of energy however they are
wired. What the wiring chooses is whether that energy arrives as volts or as coulombs.

## Ground is a choice, not a place

Because a voltage needs two points, quoting one number per node means fixing one node
as the reference and measuring everything from it. That node is called ground, and
nominating it is a decision you make, not a property the circuit has. A voltmeter has
two leads for exactly this reason: "the voltage at node A" is the reading with the
black lead on ground.

### Worked: move the ground and watch nothing happen

A 12 V supply feeds three components in a chain between its two terminals. With the
negative terminal called ground, a meter finds:

```
node        potential        across                     difference
 A (top)      12.0 V         A to B    12.0 - 8.4     =   3.6 V
 B             8.4 V         B to C     8.4 - 3.6     =   4.8 V
 C             3.6 V         C to D     3.6 - 0.0     =   3.6 V
 D (gnd)       0.0 V                                     -------
                                        sum              12.0 V
```

Now move the black lead to node C and call *that* ground. Every node voltage falls by
3.6 V:

```
node        potential        across                     difference
 A             8.4 V         A to B     8.4 - 4.8     =   3.6 V
 B             4.8 V         B to C     4.8 - 0.0     =   4.8 V
 C (gnd)       0.0 V         C to D     0.0 - (-3.6)  =   3.6 V
 D            -3.6 V                                     -------
                                        sum              12.0 V
```

Nothing physical happened. No component was touched, no current changed, every
component still takes the same joules off every coulomb as it did before. What changed
is the arbitrary constant the node voltages are quoted against, and every *difference*
is blind to it, because the constant cancels in the subtraction.

That is the entire content of "ground is a choice". It is also why a $\pm5$ V split
supply is not a special component: it is a 10 V supply with its middle node nominated
as ground, so that one end reads $+5$ V and the other $-5$ V. Negative node voltages
are not exotic — they are the same circuit read from the other end.

And it is why a bird can sit on an 11 kV overhead line unharmed. Its feet are a few
centimetres apart on the same conductor, so the difference between them is thousandths
of a volt, and thousandths of a volt is all its body is exposed to. The 11 kV is a
difference between that line and the earth, and the bird is not touching the earth.
Voltage is never a property of a place. It is always a statement about a pair.

## The mistake people actually make

There are two, and they are the same mistake wearing different hats.

The first is talking about the voltage *through* something, or asking what the voltage
of a single wire is. It is tempting because every other quantity in the subject is a
property of one object: this resistor has a resistance, this wire carries a current,
this lamp dissipates a power. Voltage is the odd one out — the only quantity in the
list that needs two arguments — and everyday language keeps sanding that corner off.
"The 5 V rail", "a 9 V battery", "the voltage at node A": every one of those phrases has
a second point buried in it that was agreed on once and then went unmentioned.

The cure is mechanical. Whenever you write a voltage down, be able to name both points.
If you cannot name the second one, you have not written a voltage.

The second is putting a voltmeter in series with a component, hoping to catch the
voltage on its way through. A voltmeter goes *across* the two points whose difference
you want, in parallel with the component, because a voltage is a statement about a pair
of points. An ammeter has to be cut into the path, because a current is a statement
about one cross-section. The two instruments look alike and the two ways of connecting
them are not interchangeable: an ammeter across a supply is a short circuit, and a
voltmeter in series stops very nearly all of the current it was meant to measure. EE221
is where the instruments themselves are treated properly.

## Where this stops being true

Everything above treats voltage as a difference in potential energy per unit charge.
That is what makes it a property of the two endpoints alone rather than of the route
taken between them: carry a coulomb from A to B the long way round and it gains or
loses exactly the same energy as it would by the short way. That path-independence is
what the word *potential* is doing, and it is what allows a single number to be written
next to a node at all.

It holds throughout this course, and it fails the moment a magnetic field starts
changing with time. Then a coulomb carried round one path gains a different amount of
energy from one carried round another, and "the voltage between two points" stops being
a single number at all: what a voltmeter reads begins to depend on where its leads were
routed. That is not a nuisance — it is the effect a transformer runs on. EE141 treats
induction properly and EE102 is where circuits start to feel it. Direct current never
meets it.

Two smaller edges, both of which this course comes back to:

- A cell's terminal voltage is not quite the joules-per-coulomb its chemistry supplies.
  That figure is the electromotive force; the terminal voltage is what survives after
  the cell's own internal resistance has taken a share, so it sags as more current is
  drawn and the 1.5 V above is really a no-load figure. The module on real sources is
  where that correction lives.
- "Voltage" and "potential difference" are used interchangeably here, and in direct
  current they are the same thing. It is only when the paragraph above starts to apply
  that the distinction earns its keep.
''',
                },
            ],
            "sandbox": {
                "title": "What 'steady' means, and when it starts",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 1.2, "wn": 3},
                "brief": r'''
Switch a supply on and the circuit does not arrive at its answer instantly. It moves
towards it, and after a while it stops moving. **Direct current analysis is the study
of that final, unmoving value** — everything in this course computes where the right
hand curve ends up, not how it got there.

Watch the **right-hand plot**. The horizontal dashed line is the final value the
circuit settles on; the solid curve is the journey. The left-hand plot is a map of
the two numbers that decide the shape of that journey, and it is the subject of a
later course — for now, notice only that the two dots move when you move the sliders.

The slider marked $\zeta$ (the Greek letter zeta) controls how the journey goes, and
$\omega_n$ controls how fast.
''',
                "notice": [
                    "Leave $\\zeta$ at 1.2. The curve climbs once, flattens onto the dashed line at 1, and stays there. That last value is the only thing a DC calculation ever asks for.",
                    "Drag $\\zeta$ down to 0.2. The curve now overshoots and rings, and the two dots on the left lift off the horizontal axis — but the curve still ends on the same dashed line at 1. The steady value does not depend on how the circuit gets there.",
                    "Put $\\zeta$ back at 1.2 and raise $\\omega_n$ from 3 to 12. The curve keeps exactly the same shape; only the numbers along the time axis shrink, because the plot rescales itself. Fast or slow, the DC answer is identical.",
                ],
            },
            "derive": {
                "title": "Where I = nAvq comes from",
                "minutes": 12,
                "vars": ["I", "Q", "t", "n", "A", "L", "v", "q"],
                "brief": r'''
A wire of cross-sectional area $A$ — an area here, not an ampere — carries a current
$I$. Inside it are $n$ mobile carriers per cubic metre, each carrying a charge $q$,
each drifting along the wire at a speed $v$.

Nothing in that list is a formula you have been handed. Everything below is built from
two definitions you already have: current is charge per unit time, and speed is
distance per unit time. Mark off a slug of the wire, of length $L$, and follow it past
a fixed plane.
''',
                "steps": [
                    {
                        "prompt": "How many mobile carriers are inside a slug of wire of length $L$? Write it in terms of $n$, $A$ and $L$.",
                        "answer": "n A L",
                        "hint": "$n$ is a count per cubic metre, so what you want first is the volume of the slug.",
                    },
                    {
                        "prompt": "Each of those carries a charge $q$. Write the total mobile charge $Q$ in the slug, in terms of $n$, $A$, $L$ and $q$.",
                        "answer": "n A L q",
                        "hint": "One more multiplication on the count you just wrote.",
                    },
                    {
                        "prompt": "The whole slug drifts at speed $v$. How long does it take all of it to cross a fixed plane through the wire? Write the time in terms of $L$ and $v$.",
                        "answer": "\\frac{L}{v}",
                        "hint": "Time is distance over speed, and the distance in question is the slug's own length \u2014 that is how far the back of it has to travel to reach where the front started.",
                    },
                    {
                        "prompt": "Current is that charge divided by that time. Put the two together and write $I$ in terms of $n$, $A$, $v$ and $q$.",
                        "answer": "n A v q",
                        "hint": "Dividing by $L/v$ is multiplying by $v/L$, and something then cancels.",
                        "deconstruct": [
                            "$I = Q/t = \\frac{nALq}{L/v} = nALq \\times \\frac{v}{L}$.",
                            "The $L$ cancels \u2014 as it had to, because the answer cannot depend on how long a slug you chose to mark off.",
                        ],
                    },
                    {
                        "prompt": "Rearrange for the drift speed: write $v$ in terms of $I$, $n$, $A$ and $q$.",
                        "answer": "\\frac{I}{n A q}",
                        "hint": "Divide both sides by everything on the right that is not $v$.",
                    },
                ],
                "closing": r'''
Now put copper into it. With $n = 8.5\times10^{28}$ carriers per cubic metre,
$A = 1.5$ mm$^2 = 1.5\times10^{-6}$ m$^2$ and $q = 1.602\times10^{-19}$ C, the product
$nAq$ is $2.04\times10^{4}$ coulombs of mobile charge per metre of wire. At $I = 3$ A
the drift speed is $3/(2.04\times10^{4}) = 1.5\times10^{-4}$ m/s — about 0.15 mm every
second, so an electron takes nearly two hours to cross a one-metre lead. The lamp
lights immediately anyway, because nothing was waiting for that electron to arrive.

Two things are worth keeping out of this. The $L$ cancelled, so the result is a
property of the wire and the current and not of where you drew your marks. And $v$
goes inversely with $A$: the same current in a thinner wire means faster drift, more
collisions per carrier per second, and more heat — which is why wire is sold by
thickness, and what the last module of this course puts numbers on.
''',
            },
            "blanks": {
                "title": "A power bank, on the back of an envelope",
                "minutes": 8,
                "caption": "milliamp-hours, coulombs and joules, one line at a time",
                "lang": "text",
                "brief": r'''
The number printed on a power bank is a **charge**, not an energy. A milliamp-hour is
one milliamp flowing for one hour, which is $0.001 \times 3600 = 3.6$ coulombs — the
definition $Q = It$ with the units left in.

That is why capacity divided by current comes out as a time directly, and why the
cell's voltage never appears until you want joules.
''',
                "listing": """a 10 000 mAh power bank, charging a phone that draws a steady 350 mA
--------------------------------------------------------------------

  capacity  = 10000 mAh                    milliamps x hours: a CHARGE
            = 10 A h
            = 10 * ___                     seconds in an hour
            = 36000 C

  runtime   = capacity / current
            = 10000 mAh / 350 mA           the mA cancel, hours survive
            = ___ h

  the cell inside sits at 3.7 V, and one volt is one joule per coulomb, so

  energy    = ___
            = 36000 * 3.7
            = 133200 J                     about 133 kJ

  and the same pack, feeding a 2 A load instead:

  runtime   = 10000 mAh / 2000 mA = ___ h
""",
                "blanks": [
                    {
                        "prompt": "An amp-hour is an amp flowing for an hour. How many coulombs is that?",
                        "hole": "?",
                        "opts": ["3600", "60", "1000", "100"],
                        "a": 0,
                        "why": "An hour is 3600 s, and $Q = It = 1 \\times 3600 = 3600$ C. The figure 60 is "
                               "the seconds in a minute, and 1000 is the milli in milliamp \u2014 already "
                               "spent on the line above, where 10000 mAh became 10 A h.",
                    },
                    {
                        "prompt": "10 000 mAh of charge, drawn at 350 mA. How many hours?",
                        "hole": "?",
                        "opts": ["3.5", "28.6", "0.35", "35"],
                        "a": 1,
                        "why": "$10000/350 = 28.6$ hours. The milliamps cancel between the top and the "
                               "bottom, and what is left is the hour from the *hour* in milliamp-hour \u2014 "
                               "which is the whole reason the unit is quoted in that awkward form. Working "
                               "the same sum in base units gives $36000\\ \\text{C} / 0.35\\ \\text{A} = "
                               "102\\,900$ s, the same answer wearing different clothes.",
                    },
                    {
                        "prompt": "Energy, from a charge and a voltage. Which line is it?",
                        "hole": "?",
                        "opts": ["Q / V", "V / Q", "Q * V", "Q * V * t"],
                        "a": 2,
                        "why": "A volt is a joule per coulomb, so coulombs times joules-per-coulomb is "
                               "joules: $E = QV$. Dividing instead gives $V/Q$, which is the definition "
                               "upside down, and multiplying by a time as well counts the hours twice \u2014 "
                               "they are already inside the charge.",
                    },
                    {
                        "prompt": "The same 10 000 mAh, at 2000 mA. How many hours?",
                        "hole": "?",
                        "opts": ["20", "0.2", "5", "50"],
                        "a": 2,
                        "why": "$10000/2000 = 5$ hours. The current is 5.7 times larger and the runtime "
                               "is 5.7 times shorter: the product of the two is fixed, because that "
                               "product is the charge the pack holds. What is *not* fixed in practice is "
                               "the capacity itself \u2014 a "
                               "cell emptied fast delivers less than one emptied slowly, and its terminal "
                               "voltage sags as it goes. The last module of this course is where that "
                               "correction lives.",
                    },
                ],
            },
            "numeric": [
                {
                    "title": "A camera flash, and the current in it",
                    "minutes": 5,
                    "brief": r'''
One rule, one unknown. The only thing this question can catch you out on is the unit
on the time, which is why it is written in milliseconds.
''',
                    "prompt": "What is the average current through the tube while it fires?",
                    "note": "Give the answer in amperes, to one decimal place.",
                    "figure": "A camera flash tube fires once. A charge of 4.50 C passes through it, and the "
                              "flash lasts 150 ms from first light to last. Nothing else about the circuit "
                              "matters here.",
                    "given": [
                        {"label": "Charge moved", "value": "4.50 C"},
                        {"label": "Duration of the flash", "value": "150 ms"},
                    ],
                    "aside": "150 ms is 0.150 s. Put every quantity into base units before dividing "
                             "anything by anything.",
                    "answer": 30.0,
                    "tol": 0.2,
                    "unit": "A",
                    "hint": "$I = Q/t$, with $t$ in seconds.",
                    "wrong": "If you got 0.03, the milliseconds went in as they were written: "
                             "$4.50/150$ is coulombs per *millisecond*, and a thousand of those are in "
                             "every second.",
                    "why": "$I = Q/t = 4.50/0.150 = 30.0$ A. Thirty amps sounds alarming for something "
                           "run off a couple of AA cells, and it is \u2014 for 150 milliseconds. The "
                           "charge itself is unremarkable: a torch bulb moves 4.5 C through its filament "
                           "in nine seconds and nobody worries. What makes the number large is that it "
                           "is delivered all at once, and *rate* is the whole content of the word "
                           "current \u2014 which is also why a flash tube is a tube of gas rather than a "
                           "piece of wire.",
                },
                {
                    "title": "The voltage across something warm",
                    "minutes": 7,
                    "brief": r'''
Two definitions, chained, and run backwards. You are given an energy and asked for a
voltage, and the charge is the stepping stone between them.
''',
                    "prompt": "What is the voltage across the resistor?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "figure": "A resistor sits in a circuit carrying a steady 250 mA. Over 40 seconds it "
                              "turns 45 J into heat, and that is the only thing that happens to the energy "
                              "arriving at it.",
                    "given": [
                        {"label": "Current through it", "value": "250 mA"},
                        {"label": "For", "value": "40.0 s"},
                        {"label": "Heat produced", "value": "45.0 J"},
                    ],
                    "aside": "Voltage is joules per coulomb, so you need the coulombs before you can "
                             "have the volts.",
                    "answer": 4.5,
                    "tol": 0.03,
                    "unit": "V",
                    "hint": "Find how much charge crossed the resistor in the 40 s first. The voltage is "
                            "the energy divided by *that*, not by the time.",
                    "wrong": "If you got 1.125, the 45 J was divided by the 40 s. That is joules per "
                             "second, which is a rate rather than a voltage; a volt is a joule per "
                             "coulomb.",
                    "why": "$Q = It = 0.250 \\times 40 = 10.0$ C crossed the resistor, and "
                           "$V = E/Q = 45/10.0 = 4.50$ V. Every coulomb that went through arrived with "
                           "4.5 J more energy than it left with, ten of them made the trip, and 45 J came "
                           "out as heat. Notice what was never needed: the resistance. The next module "
                           "supplies the missing link and makes this an 18 \u03a9 part, but the energy "
                           "bookkeeping above stands on its own and would read the same for a motor, a "
                           "lamp or a length of wire.",
                },
                {
                    "title": "One wire in, three wires out",
                    "minutes": 7,
                    "brief": r'''
Charge is not used up and it does not pile up. Whatever arrives at a junction leaves
it, in the same second, through one branch or another — so the wire feeding a junction
carries the sum of everything the branches take.

That is the only new idea here. The rest is $Q = It$ again.
''',
                    "prompt": "How much charge passes through the supply wire in 5 minutes?",
                    "note": "Give the answer in coulombs, to one decimal place.",
                    "figure": "A single supply wire reaches a junction and splits into three branches. The "
                              "branches carry a steady 120 mA, 45 mA and 8 mA respectively. Nothing "
                              "accumulates at the junction.",
                    "given": [
                        {"label": "First branch", "value": "120 mA"},
                        {"label": "Second branch", "value": "45 mA"},
                        {"label": "Third branch", "value": "8 mA"},
                        {"label": "Time", "value": "5 minutes"},
                    ],
                    "aside": "Add the branch currents before you do anything else, and keep them all in "
                             "the same unit while you do it.",
                    "answer": 51.9,
                    "tol": 0.3,
                    "unit": "C",
                    "hint": "The supply wire carries $120 + 45 + 8$ mA. Then $Q = It$, with $t$ in "
                            "seconds.",
                    "wrong": "If you got 0.865, the 5 went in as it stood \u2014 five *minutes* is 300 s. If "
                             "you got 36.0, only the largest branch was counted.",
                    "why": "The three branches take $120 + 45 + 8 = 173$ mA between them, and every "
                           "milliamp of it has to arrive along the supply wire, because charge is neither "
                           "consumed in the junction nor stored there. So $Q = It = 0.173 \\times 300 = "
                           "51.9$ C. You have just used Kirchhoff's current law two modules before it is "
                           "given that name; there is nothing more to it than the sentence *what arrives "
                           "leaves*.",
                },
                {
                    "title": "What the supply hands over in 45 seconds",
                    "minutes": 8,
                    "brief": r'''
A schematic, at last, and the smallest one there is: a supply, a lamp, and a return to
ground. An ammeter in the loop reads 0.400 A — take that as given. Where the 0.400 A
comes from is the next module's business, and the 15 Ω label is there so the drawing
is a real circuit rather than a picture of one.

Everything this question needs is the meter reading, the supply voltage, and the two
definitions.
''',
                    "prompt": "How much energy does the supply deliver in 45 seconds?",
                    "note": "Give the answer in joules, to the nearest joule.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 15},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "6.00 V"},
                        {"label": "Ammeter in the loop", "value": "0.400 A"},
                        {"label": "Time", "value": "45.0 s"},
                    ],
                    "aside": "Every coulomb leaves the supply with 6 J more than it comes back with. "
                             "Count the coulombs, then count the joules.",
                    "answer": 108.0,
                    "tol": 1.0,
                    "unit": "J",
                    # The prompt asks for energy, which is no node of this circuit. Both factors are
                    # read out of the solve — the drop across the lamp and the current through it —
                    # so a re-drawn schematic is re-measured rather than compared to a memory of it.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.kind === 'R'; })[0];
const drop = Math.abs(d.v[r.n1] - d.v[r.n2]);
return drop * (drop / r.value) * 45;
''',
                    "hint": "$Q = It$ first, using the meter reading. Then every one of those coulombs "
                            "was handed 6.00 J on its way through the supply.",
                    "wrong": "If you got 2.4, that is the joules delivered in one second rather than in "
                             "45 of them. If you got 270, the 45 s has been multiplied by the 6 V \u2014 "
                             "volts and seconds do not multiply into anything.",
                    "why": "$Q = It = 0.400 \\times 45 = 18.0$ C goes round the loop, and the supply "
                           "hands 6.00 J to each of those coulombs, so it gives up $18.0 \\times 6.00 = "
                           "108$ J. Every joule of it comes back out of the lamp as heat and light: 18 C "
                           "went in and 18 C came out, and only the energy is gone. The 15 \u03a9 is what "
                           "makes the meter read 0.400 A rather than something else \u2014 the next module "
                           "makes that link \u2014 but none of the accounting above needed it.",
                },
                {
                    "title": "How long will the cell last?",
                    "minutes": 10,
                    "brief": r'''
A 3.60 V lithium cell and the three parts of a device it powers. Each of the three
circles is a **constant-current load**: a block of the design that draws the same
current whatever else happens, which is how a current budget is drawn before anyone
knows what the circuits inside look like. Each one takes its current out of the top
rail and returns it to ground.

The cell is rated **2200 mAh**. That is a capacity, and a capacity is a charge: it is
$Q = It$ with the current in milliamps and the time in hours, so a milliamp-hour is
one milliamp flowing for one hour and nothing more mysterious than that.
''',
                    "prompt": "How many hours will the cell run this device before its charge is used up?",
                    "note": "Give the answer in hours, to one decimal place. Assume every current holds "
                            "steady to the end.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 3.6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "i1", "kind": "I", "x": 9, "y": 6, "rot": 1, "value": 0.045},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "i2", "kind": "I", "x": 15, "y": 6, "rot": 1, "value": 0.012},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "i3", "kind": "I", "x": 21, "y": 6, "rot": 1, "value": 0.0008},
                            {"id": "g3", "kind": "GND", "x": 21, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [21, 3]},
                            {"a": [9, 3], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [15, 3], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [21, 3], "b": [21, 5]},
                            {"a": [21, 7], "b": [21, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Cell", "value": "3.60 V, 2200 mAh"},
                        {"label": "Radio (I1)", "value": "45 mA"},
                        {"label": "Sensor (I2)", "value": "12 mA"},
                        {"label": "Clock (I3)", "value": "800 \u00b5A"},
                    ],
                    "aside": "One milliamp-hour is 3.6 C. You can work the whole thing in coulombs and "
                             "seconds if you prefer \u2014 the answer is the same, and the mAh route just "
                             "saves two conversions.",
                    "answer": 38.06,
                    "tol": 0.3,
                    "unit": "h",
                    # No node of this circuit is a runtime, so the check takes the battery's own
                    # branch current out of the solve — which is the sum of all three loads without
                    # any of them being named here — and divides the 2.2 A h capacity by it. The
                    # sign is negative because a delivering source carries current from - to +.
                    "check": r'''
const i = Math.abs(c.dc().currents.v1);
return 2.2 / i;
''',
                    "hint": "Add the three load currents in one unit, watching the microamps. Then the "
                            "capacity in mAh divided by the current in mA is a time in hours directly, "
                            "with no conversion at all.",
                    "wrong": "If you got 38.6, the clock was left out \u2014 0.8 mA looks like nothing, and "
                             "over a day and a half it is worth half an hour. If you got 2.6, the 800 "
                             "\u00b5A went in as 800 mA, which is the factor of a thousand this question "
                             "is really about.",
                    "why": "The three loads draw $45 + 12 + 0.8 = 57.8$ mA between them, and all of it "
                           "comes out of the cell. A capacity of 2200 mAh means 1 mA for 2200 hours, or "
                           "2200 mA for one hour, or anything else with the same product \u2014 so the "
                           "runtime is $2200/57.8 = 38.1$ hours. In base units, if you would rather: "
                           "2200 mAh is $2.2 \\times 3600 = 7920$ C, and $7920/0.0578 = 137\\,000$ s, "
                           "which is the same answer. The 3.60 V never entered the arithmetic, because "
                           "capacity is a charge and charge is what runs out; multiply the two together "
                           "and you get the energy instead, $7920 \\times 3.6 = 28.5$ kJ. Real cells do "
                           "worse than this: the terminal voltage sags as the cell empties and the usable "
                           "capacity falls as the current rises, both of which the last module of this "
                           "course puts numbers on.",
                },
            ],
            "quiz": {
                "title": "Charge, current and voltage: the definitions",
                "minutes": 8,
                "questions": [
                    {
                        "q": "One ampere is best described as:",
                        "opts": [
                            "one coulomb of charge passing a point every second",
                            "one coulomb of charge sitting on a conductor",
                            "one joule of energy delivered every second",
                            "one electron passing a point every second",
                        ],
                        "a": 0,
                        "why": r'''
Current is a *rate*: $I = Q/t$, coulombs per second. Charge *sitting* on a conductor is a quantity of charge, not a flow of it. A joule
every second is a watt, which is power. One electron per second is a flow, but it is
about $1.6\times10^{-19}$ A — a fantastically small current.
''',
                    },
                    {
                        "q": "A torch bulb draws 0.5 A for 2 minutes. How much charge passes through it?",
                        "opts": ["1 C", "60 C", "120 C", "0.25 C"],
                        "a": 1,
                        "why": r'''
$Q = It$, and $t$ must be in **seconds**: two minutes is 120 s, so
$Q = 0.5 \times 120 = 60$ C. The tempting answer 1 C comes from multiplying by 2 and
forgetting the units of time — the single most common arithmetic slip in this whole
course. When a question gives you minutes, hours or milliseconds, convert first.
''',
                    },
                    {
                        "q": "The voltage between two points in a circuit measures:",
                        "opts": [
                            "how many electrons are stored between them",
                            "the energy given to each coulomb of charge that travels between them",
                            "how fast the electrons move between them",
                            "the current that will flow between them",
                        ],
                        "a": 1,
                        "why": r'''
Voltage is energy per unit charge, $V = E/Q$, measured in joules per coulomb — and
one joule per coulomb is given the name one volt. It says nothing on its own about
how much charge moves (that is current) or how fast it drifts (which is, surprisingly,
less than a millimetre per second in a typical wire).
''',
                    },
                    {
                        "q": "A 9 V battery pushes 2 C of charge round a circuit. How much energy does it deliver?",
                        "opts": ["4.5 J", "2 J", "18 J", "11 J"],
                        "a": 2,
                        "why": r'''
Rearranging $V = E/Q$ gives $E = QV = 2 \times 9 = 18$ J. The answer 4.5 J is $V/Q$,
which is the definition upside down; it is worth writing the units out —
$\text{C} \times \text{J/C} = \text{J}$ — whenever the direction of a division is in
doubt.
''',
                    },
                    {
                        "q": "In a simple loop of battery, wire and bulb, how does the current leaving the bulb compare with the current entering it?",
                        "opts": [
                            "smaller — some current is used up making light",
                            "exactly the same",
                            "zero — the current stops at the bulb",
                            "larger — the bulb adds energy",
                        ],
                        "a": 1,
                        "why": r'''
Exactly the same. This is the single most useful correction a beginner can make:
**energy** is consumed in the bulb, **charge** is not. Every electron that goes in
comes out again, at a lower energy per electron — which is precisely what the voltage
drop across the bulb measures. Charge is conserved, and that conservation is
Kirchhoff's current law, which arrives in module 3.
''',
                    },
                    {
                        "q": "Conventional current in a copper wire is drawn from + to −, while the electrons drift from − to +. What does that mean for your calculations?",
                        "opts": [
                            "every current answer must be negated at the end",
                            "nothing, as long as you are consistent — the two descriptions give identical numbers",
                            "only the electron direction gives correct power figures",
                            "it matters for resistors but not for batteries",
                        ],
                        "a": 1,
                        "why": r'''
Nothing at all. Conventional current is a bookkeeping choice made before anyone knew
electrons existed, and every formula in this course was written to match it. Choose a
direction, mark it on the drawing, and if the arithmetic comes back negative it simply
means the real current runs the other way — which is information, not an error.
''',
                    },
                ],
            },
            "match": {
                "title": "Name every symbol on the bench",
                "minutes": 6,
                "brief": r"""
Before any of the arithmetic is worth doing, a schematic has to be readable at a
glance. These five turn up on almost every board ever made, and three of them are
distinguished from their neighbours by a single stroke — an arrow, a curve, a
second bar. Learning that stroke now saves reading a diagram backwards later.
""",
                "prompt": "Pick a label, then tap the symbol it belongs to.",
                "labels": ["Resistor", "Capacitor", "LED", "Ground", "NPN transistor"],
                "items": [
                    {"sym": "R", "a": 0, "why": "A resistor: the zig-zag is the international "
                     "symbol most of the world learned; the plain rectangle is the IEC form and "
                     "means exactly the same thing. Nothing about it is polarised, which is why "
                     "it can go either way round."},
                    {"sym": "C", "a": 1, "why": "A capacitor: two plates that never touch, which "
                     "is the whole device. Two straight bars means non-polarised; one bar curved "
                     "would mean electrolytic, and that one has a right way round."},
                    {"sym": "LED", "a": 2, "why": "An LED. It is a diode \u2014 same triangle "
                     "into a bar, same one-way behaviour \u2014 with two arrows leaving it. "
                     "Arrows pointing *away* mean it emits; pointing *in* would make it a "
                     "photodiode, which is the same silicon used backwards."},
                    {"sym": "GND", "a": 3, "why": "Ground: the node every voltage in the circuit "
                     "is quoted against. It is a choice, not a place \u2014 you nominate it, and "
                     "every reading on the schematic then means \u2018relative to here\u2019."},
                    {"sym": "NPN", "a": 4, "why": "An NPN transistor. The arrow is on the emitter "
                     "and points outward, which is the entire difference from a PNP. Read the "
                     "arrow as the direction conventional current leaves the device."},
                ],
            },
            "lab": {
                "title": "Counting charge and energy",
                "runtime": "python",
                "minutes": 20,
                "brief": r'''
Three one-line functions, so that the definitions become something you have actually
computed with.

- `charge(amps, seconds)` returns the charge in coulombs that passes in that time.
- `electrons(coulombs)` returns how many electrons that charge amounts to. The
  constant `ELEMENTARY_CHARGE` is already defined for you.
- `energy(coulombs, volts)` returns the energy in joules handed to that charge by
  that voltage.

Nothing here needs a loop or a condition. The point is the units: seconds, coulombs,
joules. If you find yourself wanting to divide where the definition multiplies, write
the units alongside the numbers and see which arrangement leaves you with the unit you
were asked for.
''',
                "files": [{"name": "main.py", "content": r'''
"""Charge, current and energy — the three definitions, as code."""

ELEMENTARY_CHARGE = 1.602176634e-19  # coulombs carried by one electron


def charge(amps, seconds):
    """Charge in coulombs that passes when `amps` flows for `seconds`."""
    # TODO: current is charge per second, so charge is current times seconds.
    return 0.0


def electrons(coulombs):
    """How many electrons make up this much charge."""
    # TODO: divide by the charge on one electron.
    return 0.0


def energy(coulombs, volts):
    """Energy in joules given to `coulombs` of charge by a voltage of `volts`."""
    # TODO: a volt is a joule per coulomb.
    return 0.0


if __name__ == "__main__":
    q = charge(0.5, 120)
    print("a 0.5 A torch for 2 minutes moves", q, "C")
    print("that is about", f"{electrons(q):.3e}", "electrons")
    print("from a 4.5 V battery that is", energy(q, 4.5), "J")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Charge, current and energy — the three definitions, as code."""

ELEMENTARY_CHARGE = 1.602176634e-19  # coulombs carried by one electron


def charge(amps, seconds):
    """Charge in coulombs that passes when `amps` flows for `seconds`."""
    return amps * seconds


def electrons(coulombs):
    """How many electrons make up this much charge."""
    return coulombs / ELEMENTARY_CHARGE


def energy(coulombs, volts):
    """Energy in joules given to `coulombs` of charge by a voltage of `volts`."""
    return coulombs * volts


if __name__ == "__main__":
    q = charge(0.5, 120)
    print("a 0.5 A torch for 2 minutes moves", q, "C")
    print("that is about", f"{electrons(q):.3e}", "electrons")
    print("from a 4.5 V battery that is", energy(q, 4.5), "J")
'''}],
                "hints": [
                    "`charge` is one multiplication. The only trap is being handed minutes when the formula wants seconds — the caller converts, not you.",
                    "`electrons` divides the total charge by the charge on one electron. One coulomb comes to about $6.24\\times10^{18}$ electrons; if your answer is not somewhere near $10^{18}$, the division has gone the wrong way round.",
                    "`energy` is also one multiplication: joules per coulomb, times coulombs.",
                ],
                "tests": [
                    {"name": "charge is current times time", "code": r'''
q = charge(0.5, 120)
assert abs(q - 60.0) < 1e-12, f"0.5 A for 120 s is 60 C, got {q}"
'''},
                    {"name": "a big current for a short time", "code": r'''
q = charge(2.0, 0.5)
assert abs(q - 1.0) < 1e-12, f"2 A for half a second is 1 C, got {q}"
'''},
                    {"name": "one coulomb is about 6.24e18 electrons", "code": r'''
n = electrons(1.0)
assert abs(n - 6.241509074460763e18) < 1e6, \
    f"1 C divided by 1.602176634e-19 C is about 6.2415e18, got {n}"
'''},
                    {"name": "energy is charge times voltage", "code": r'''
e = energy(2.0, 9.0)
assert abs(e - 18.0) < 1e-12, f"2 C through 9 V is 18 J, got {e}"
'''},
                    {"name": "the three combine on a real torch", "code": r'''
q = charge(0.06, 1800)
assert abs(q - 108.0) < 1e-9, f"60 mA for 30 minutes is 108 C, got {q}"
e = energy(q, 4.5)
assert abs(e - 486.0) < 1e-9, f"108 C from 4.5 V is 486 J, got {e}"
n = electrons(q)
assert n > 6e20, f"108 C should be well over 1e20 electrons, got {n}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Ohm's law, resistance and power",
            "summary": "One equation relating voltage and current, and one relating them to heat.",
            "concepts": [
                "Resistance relates the voltage across a component to the current through it: $V = IR$. Resistance is measured in ohms, and 1 Ω is 1 V/A.",
                "$I = V/R$ and $R = V/I$ are rearrangements of the same statement, not three separate laws.",
                "A resistor is symmetric: it has no + end, and reversing it changes nothing.",
                "Power is energy per second, measured in watts: $P = VI$, which follows directly from $V = E/Q$ and $I = Q/t$.",
                "For a resistor, substituting Ohm's law gives $P = I^2R = V^2/R$. Use whichever of the two quantities you already know.",
                "A resistor's power rating is a temperature limit, not an electrical one. Exceeding it does not change the current; it destroys the part.",
                "Real wires have a small resistance and real batteries have an internal one. In this course both are taken as zero unless a question says otherwise.",
            ],
            "read": [
                {
                    "title": "Why the current is proportional to the voltage",
                    "minutes": 14,
                    "body": r'''
An electric field inside a wire pushes on every mobile electron in it, and a push on
something free to move is an acceleration. If that were the whole story, a battery
connected across a wire would produce a current that grew without limit for as long as
it stayed connected. It plainly does not. Put 9 V across 1.5 kΩ and you get 6 mA — this
second, the next second, and every second after until something is unplugged.

What stops the acceleration is the metal itself. An electron picks up speed from the
field for something like $10^{-14}$ s, collides with a vibrating copper atom or a
lattice defect, loses whatever ordered motion it had gained, and starts over. Averaged
over an unimaginable number of these, the *ordered* part of the motion — the drift the
previous module measured at a fraction of a millimetre per second — settles at the
speed where energy taken from the field exactly balances energy dumped into the lattice
as heat. It is the terminal velocity of a raindrop, not the trajectory of a bullet.

The raindrop earns its place twice over. A drop's falling speed is not a property of
gravity; it is where gravity and the air agree, and it is the air that fixes the number.
Resistance is the air here — not something the source does, not something the current
does, but a property of the stuff the charge has to get through.

## From the collisions to the proportionality

The picture is worth taking seriously enough to get a formula out of, and the argument
is short.

Start with the push. A wire of length $L$ with a voltage $V$ across it holds a uniform
electric field of $V/L$ along its axis — volts per metre. Only those two numbers enter:
the same 9 V across a 10 cm wire pushes ten times as hard as across a metre of it.

Between collisions that field accelerates an electron, and the collisions arrive at some
average interval $\tau$. The ordered speed an electron keeps on average — its drift —
therefore comes out proportional to the push:

$$v_d = \frac{q\tau}{m}\cdot\frac{V}{L}$$

Everything on the right except $V$ and $L$ belongs to the metal: the electron's charge
and mass, and $\tau$, which is set by how hot the lattice is and how perfect the crystal
is.

The whole of Ohm's law now rests on one step, and it is worth pausing over: **$\tau$ does
not depend on $V$.** That is not true by definition — pushing harder really could make an
electron hit things more often. The reason it does not comes straight out of the previous
module's numbers. An electron in copper is already travelling at around
$1.6\times10^{6}$ m/s in a random direction, and the drift added on top is around
$10^{-4}$ m/s: about one part in $10^{10}$ of what it was doing anyway, which changes the
collision rate by nothing you could measure. Double the voltage and you have doubled a
rounding error. *That* is why the relationship comes out linear — and it is exactly where
the linearity eventually fails.

The previous module supplies the rest. A current is the mobile charge per metre of wire
times the speed it drifts at, $I = nAqv_d$, with $n$ the free electrons per cubic metre
and $A$ the cross-section. Substitute:

$$I = nAq \cdot \frac{q\tau}{m}\cdot\frac{V}{L} = \left(\frac{nq^{2}\tau}{m}\right)\frac{A}{L}\,V$$

The bracket contains nothing but properties of the material. Give it a name — $\sigma$,
the **conductivity** — and read the result off:

$$I = \frac{\sigma A}{L}\,V \qquad\Longleftrightarrow\qquad V = I\cdot\frac{L}{\sigma A}$$

which is $V = IR$, with the resistance identified as

$$R = \frac{L}{\sigma A} = \frac{\rho L}{A}$$

where $\rho = 1/\sigma$ is the **resistivity**, a number tabulated per material in
ohm-metres. Copper is $1.68\times10^{-8}\ \Omega\,$m at room temperature.

Three things fall out of that, and all three are worth keeping.

Resistance grows with length and falls with area: a resistor and a piece of wire are the
same component in different proportions, long and thin against short and fat.

The material enters through exactly one number, which is why a parts catalogue can list
resistance without listing chemistry.

And $\tau$ is the temperature-sensitive part. Heat the lattice, the atoms vibrate through
a wider arc, collisions come sooner, $\tau$ falls, $\sigma$ falls, $R$ rises. Every
temperature effect in the rest of this reading is that sentence pointed at something.

(EE141 develops resistivity properly and module 11 puts a figure on the drift with
temperature. Here it is scaffolding, so that $R$ is not a symbol that arrived from
nowhere.)

## Worked: where an ohm comes from, in millimetres

A 25 m extension lead made from the 1.5 mm² copper of the previous module, feeding a
3 kW heater. The current goes out along one conductor and back along the other, so the
copper in the path is 50 m long, not 25.

```
rho (copper, 20 C) = 1.68e-8 ohm m
A                  = 1.5 mm^2  = 1.5e-6 m^2
L                  = 25 m out + 25 m back = 50 m

R = rho * L / A
  = 1.68e-8 * 50 / 1.5e-6
  = 8.4e-7 / 1.5e-6
  = 0.56 ohm

the heater draws about 13 A, so the lead itself takes

V = I R
  = 13 * 0.56              = 7.3 V     out of 230 V, or 3.2% of it
```

Two readings of that, and you need both. 0.56 Ω is small: treating the wires as zero
ohms, which every other question in this course does, costs three per cent and is usually
the right call. And it is not zero — those 7.3 V went somewhere. Module 11 stops
pretending.

Run the same formula backwards and it explains something about the parts bin. Suppose
you wanted 1 kΩ made of copper wire 0.1 mm across:

```
A = pi * (0.05e-3)^2                    = 7.85e-9 m^2
L = R A / rho
  = 1000 * 7.85e-9 / 1.68e-8            = 467 m
```

Nearly half a kilometre of hair-thin wire for one ordinary resistor. Copper is the wrong
material by four or five orders of magnitude, which is why resistors are made of carbon
film, metal film or nichrome — materials picked for a *large* $\rho$, so that a useful
resistance fits inside a few millimetres.

## What kind of statement Ohm's law is

$$V = IR$$

The constant of proportionality is the **resistance**, measured in ohms. One ohm is one
volt per ampere, and that is the whole definition: a component with 1 Ω across it draws
one amp per volt.

It is worth being clear about the standing of this. Conservation of charge is a law of
nature. Ohm's law is not: it is an experimental fact about a particular class of
materials over a particular range of conditions. Georg Ohm established it by measurement
in the 1820s, and the derivation above sketches why metals happen to behave that way
rather than proving anything must. Look at what that sketch assumed — a fixed $\tau$, one
kind of carrier, a uniform field across a uniform cross-section — and you have a list of
the ways a real component can fail to be ohmic. Plenty do.

Calling a component **ohmic** is therefore a claim, and a testable one: that its
$V$-against-$I$ plot is a straight line through the origin. The gradient of that line
*is* $R$.

## One statement, three arrangements

$$V = IR \qquad I = \frac{V}{R} \qquad R = \frac{V}{I}$$

These are not three laws to memorise. They are one equation with each of its symbols made
the subject in turn, and which one you reach for depends only on which two quantities you
already know.

One habit is worth forming now. Electronics lives in volts, kilohms and milliamps, and
those three units are *consistent with each other*: volts divided by kilohms comes out
in milliamps exactly, with no factors of a thousand to lose. So $9\ \text{V}$ across
$4.7\ \text{k}\Omega$ is $9/4.7 = 1.9$ mA, done in your head. Convert to volts, ohms and
amps if you prefer, but convert *everything*, and never half of it.

## Worked: a panel lamp on a 12 V rail

A small indicator lamp is specified as "12 V, 150 mA". Both numbers describe the same
operating point, so between them they fix the resistance:

```
R = V / I
  = 12 V / 0.150 A
  = 80 ohm

P = V * I
  = 12 V * 0.150 A
  = 1.8 W
```

Now suppose the rail sags to 9 V. If the lamp were ohmic — if 80 Ω were a fixed
property of it — the current would fall in proportion:

```
I = V / R  =  9 / 80   = 0.1125 A   = 112.5 mA
P = V * I  =  9 * 0.1125             = 1.01 W
```

Three quarters of the voltage, three quarters of the current, and a little over half the
power, because power involves both. That last observation is the next reading's subject.

The 112.5 mA, though, is wrong, and wrong in an instructive direction. A filament lamp is
the standard **non-ohmic** component: tungsten's resistance climbs steeply with
temperature — that is $\tau$ falling — roughly by a factor of ten between cold and
running. Drop the voltage, the filament runs cooler, its resistance falls below 80 Ω and
the real current is *higher* than the proportional estimate. Rather than argue about it,
measure it.

## Worked: is this thing ohmic? Two bench sweeps

Put a variable supply across a component, step the voltage, write down the current, and
divide. If the ratio holds still, the component is ohmic and the ratio is its resistance.

```
a 220 ohm metal-film resistor

    V (V)     I (mA)     V/I (ohm)
    1.00       4.55         220
    2.00       9.09         220
    3.00      13.64         220
    4.00      18.18         220
    5.00      22.73         220

a 6 V 0.3 A torch bulb, same sweep

    V (V)     I (mA)     V/I (ohm)
    1.00       120          8.3
    2.00       175         11.4
    3.00       215         14.0
    4.00       250         16.0
    6.00       300         20.0
```

The resistor's third column is a constant, which is the entire content of "it obeys
Ohm's law": plot it and you get a straight line through the origin of gradient 220 Ω. The
bulb's third column is not constant at all. It rises by a factor of 2.4 across the sweep
and the plot bends over — each extra volt buys less extra current than the one before,
because the filament is hotter and harder to push charge through.

Notice what that does to "the resistance of the bulb". At 4.00 V the ratio $V/I$ is
16.0 Ω. But take the *gradient* there, from the two nearest points:

```
between 3.00 V and 4.00 V:

  dV / dI = (4.00 - 3.00) / (0.250 - 0.215)
          = 1.00 / 0.035
          = 28.6 ohm
```

Sixteen ohms and 28.6 ohms, at the same operating point, both correctly computed.
For an ohmic part those two numbers are equal — that is what a straight line through the
origin means. For anything else they are two different facts, and you must know which one
the question wants.

## The mistake people actually make

Sooner or later everyone divides a voltage by a current for a component that is not ohmic
and treats the answer as that component's resistance.

It is tempting for a good reason: the division always works. The calculator returns a
number, the number has units of ohms, and at the one operating point you measured it is
even correct. Nothing announces itself as wrong. What has been computed is a chord — one
point's ratio — and the mistake is not the arithmetic but the assumption that it survives
to the next voltage.

Take an LED. At its rated 20 mA it has about 2.0 V across it, and $2.0/0.020$ is
100 Ω — a true statement about that point. Drop it to 1.8 V and it draws roughly 5 mA,
so "its resistance" is now 360 Ω. At 1.6 V it is essentially open circuit. There is no
fixed resistance in there to find.

The consequence is the one every beginner meets. How do you run that LED from 5 V? Not by
treating it as 100 Ω and building a divider — that calculation has no solution, because
the 100 Ω was only true at the answer you were trying to compute. You use the LED's
*voltage* instead, which is the quantity that stays roughly put, and give the leftover to
a component that is genuinely ohmic:

```
supply                            5.00 V
LED at its rated 20 mA            2.00 V
                                  ------
left over for the resistor        3.00 V     at the same 20 mA, one loop

R = V / I
  = 3.00 / 0.020                = 150 ohm
```

The habit worth forming: before dividing a voltage by a current, ask whether the answer
is meant to survive the next question. For a resistor it does. For anything with a
junction, a filament or a temperature in it, it does not.

## Where this stops being true

- **Filament lamps.** Tungsten's resistance rises about tenfold from cold to running,
  which is why filament lamps nearly always fail at switch-on: the cold inrush current is
  many times the running current.
- **Diodes and transistors.** Current rises roughly exponentially with voltage, so "the
  resistance" is not a number at all. What replaces it is the **dynamic** or small-signal
  resistance $r = \mathrm{d}V/\mathrm{d}I$ — the gradient at the operating point rather
  than the ratio at it, exactly as the bulb sweep showed. EE201 is built on it.
- **Thermistors.** Built so that resistance tracks temperature, and used as sensors and
  as inrush limiters for exactly that reason.
- **Ordinary resistors, a little.** Even a metal-film part drifts as it warms, typically
  50 parts per million per degree. Module 11 turns that into a number that matters.
- **Very large fields.** The derivation assumed the drift was negligible next to the
  thermal speed. In a semiconductor at a few volts per micron it is not: $\tau$ starts
  depending on the field and the drift velocity saturates. In a metal you would melt the
  wire long before reaching that. At the other extreme, cool some metals far enough and
  they become superconducting — $R$ is exactly zero, not small.
- **Anything changing with time.** For a capacitor or an inductor the current depends on
  how fast the voltage is changing rather than on its value, and $V = IR$ is not repaired
  but replaced — by $V = IZ$ with a complex impedance. That is EE102, and it is why this
  course says *direct current* in its title.

None of that is a problem for what follows: every component in this course is declared
ohmic and every resistance is one fixed number. It is worth knowing that this is an
assumption you are being handed rather than a fact about the world.
''',
                },
                {
                    "title": "Power, and where the energy actually goes",
                    "minutes": 13,
                    "body": r'''
Nothing in a resistor is consumed. The same number of coulombs leave it as entered it,
and if you weigh it before and after it is identical. What a resistor takes is energy,
and what it does with that energy is turn it into heat — every joule of it, always, with
no other outcome available. A resistor is the one component in this course that cannot
store anything or give anything back.

That is a stronger statement than it sounds. A capacitor takes energy and will hand it
back later. A motor takes energy and turns most of it into motion. A battery takes energy
and puts it away chemically. A resistor is a one-way street, and the only thing at the
far end of it is a warmer room.

## The rate at which that happens

Power is energy per unit time, so it is the *rate* at which a component turns energy
into something else. Its unit is the watt: one joule per second.

You already have everything needed to write it down. A volt is a joule per coulomb, and
an amp is a coulomb per second. Multiply:

$$P = VI \qquad\text{because}\qquad \frac{\text{joules}}{\text{coulomb}} \times \frac{\text{coulombs}}{\text{second}} = \frac{\text{joules}}{\text{second}}$$

The coulombs cancel, and they cancel for a reason: the charge is not used up, so it is
never the thing being counted. $P = VI$ is true of *any* two-terminal component — a
motor, a battery, a lamp — because it is a restatement of two definitions and contains
no physics about resistors at all.

## Which way is the energy going?

$P = VI$ gives a rate but not a direction, and the two are separate questions. A battery
running a lamp and the same battery on charge show the same volts at the same terminals
and the same amps through the same wire, and they are doing opposite things.

The convention that settles it is worth adopting now, because from the nodal-analysis
module onwards you will be handed currents whose direction you did not choose. Mark a $+$
on one terminal of the component and measure the current going **into** that terminal.
Then $P = VI$ is the power the component is taking *out of* the circuit: positive means
absorbing, negative means delivering.

A resistor always comes out positive, and that is a consequence rather than a convention.
$P = I^{2}R$ is a square multiplied by a positive number, and no wiring you can devise
makes it negative. A resistor cannot deliver energy, which is why a circuit built of
nothing but resistors sits there doing nothing.

A source is the interesting case, because it can go either way. Current out of the $+$
terminal means delivering — a battery running a lamp. Current *into* the $+$ terminal
means absorbing: the same battery on charge, a motor being driven backwards as a
generator, a car braking regeneratively.

Once every component has a signed power, the accounting closes. Add them up over a
complete circuit and the total is zero — every joule a source hands out is taken by
something else in the same second. Take the loop from the previous module:

```
9 V battery, a steady 0.25 A, two lamps measuring 6.0 V and 3.0 V

  battery   P = V I = 9.0 * 0.25   = 2.25 W    delivered, so -2.25 W absorbed
  lamp A    P = V I = 6.0 * 0.25   = 1.50 W    absorbed
  lamp B    P = V I = 3.0 * 0.25   = 0.75 W    absorbed
                                     ------
  signed total                       0.00 W
```

That is not a coincidence and it is not a new law. It is the same conservation of energy
that forced the 6.0 V and the 3.0 V to add up to 9.0 V, multiplied through by the one
current in the loop. It is also the most useful check you have: solve a circuit, total
the sources' output and the resistors' consumption, and see whether they match. When they
do not, the solution is wrong, and no amount of staring at the algebra finds it as fast.

## Two substitutions, and choosing between them

For a resistor, and only for a resistor, Ohm's law lets you eliminate whichever of $V$
and $I$ you do not happen to know:

$$P = VI = (IR)I = I^2R \qquad\qquad P = VI = V\left(\frac{V}{R}\right) = \frac{V^2}{R}$$

These are the same statement three times over. Substituting into the wrong one still
gives the right answer if the arithmetic is right; the point of having all three is to
save a step, not to make a choice that can be wrong.

There is nonetheless a rule of thumb worth having:

- Components **in a row**, carrying the same current, are compared with $P = I^2R$. The
  shared $I^2$ multiplies both, so **more resistance means more heat**.
- Components **side by side**, sharing the same voltage, are compared with $P = V^2/R$.
  The shared $V^2$ divides by each, so **more resistance means less heat**.

Those two sentences point in opposite directions, and both are correct. Which applies
depends entirely on what the two components have in common, which is why "does a bigger
resistor get hotter?" has no answer until you say how it is connected. The next two
worked examples are the same pair of resistors on the same supply, wired the two ways.

## Worked: in a row, which resistor is closer to the edge?

A 330 Ω rated at 1/8 W sits in series with a 1.0 kΩ rated at 1/2 W, across a 12 V
supply. The same current passes through both — nothing else can happen in a single loop
— and the pair therefore presents 1330 Ω to the supply. (Adding them like that is the
next module's rule; take it here as the obvious statement it is.)

```
I  = 12 / 1330            = 9.023 mA        the one current in the loop

P(330)  = I^2 * 330       = 0.0269 W        26.9 mW of a 125 mW budget  = 21.5%
P(1000) = I^2 * 1000      = 0.0814 W        81.4 mW of a 500 mW budget  = 16.3%
                            --------
                            0.1083 W        and 12 V * 9.023 mA = 0.1083 W
```

The 1 kΩ dissipates **three times as much heat** as the 330 Ω, exactly as $P = I^2R$
says it must. And yet it is the 330 Ω that is closer to being destroyed, because it is
the smaller part with the smaller budget. Heat and danger are different questions, and
the second one is always a ratio against a rating.

How far can this supply be turned up? The 330 Ω sets the limit, at the current where it
reaches 125 mW:

```
I_max = sqrt(P / R) = sqrt(0.125 / 330)  = 19.46 mA
V_max = I_max * 1330                     = 25.9 V
```

At 25.9 V the 1 kΩ is dissipating 0.379 W, comfortably inside its half watt. The
limiting part is the one nearest its own rating, and finding it is the entire skill.

## Worked: the same two parts, side by side

Now wire those identical two resistors so that each one goes straight across the 12 V
supply instead. Nothing is in the way of either, so each has the whole 12 V across it,
and the shared quantity is now a voltage rather than a current.

```
P(330)  = V^2 / R = 144 / 330    = 0.4364 W    436 mW of a 125 mW budget = 349%
P(1000) = V^2 / R = 144 / 1000   = 0.1440 W    144 mW of a 500 mW budget =  29%
                                   ---------
                                   0.5804 W

check it from the supply side:

  I(330)  = 12 / 330   = 36.36 mA
  I(1000) = 12 / 1000  = 12.00 mA
                         --------
  total                   48.36 mA    and 12 * 0.04836 = 0.5804 W
```

Every conclusion has inverted. The 330 Ω is now the hotter of the two by a factor of
three rather than the cooler by a factor of three, and it is not merely close to its
rating but three and a half times past it — it will be smoking within seconds. The
largest supply voltage this arrangement survives is set by the same part:

```
V_max = sqrt(P R) = sqrt(0.125 * 330)  = 6.42 V
```

Same two components, same supply, and the safe voltage fell from 25.9 V to 6.4 V. The
resistors did not change. What changed is whether they share a current or share a
voltage, and that is the only thing $P = I^2R$ and $P = V^2/R$ are asking you to notice.

## The mistake people actually make

In $P = VI$, the $V$ and the $I$ must be measured on the *same* two terminals. Almost
everyone, at some point, takes the supply voltage and multiplies it by the current
through one resistor.

```
12 V across 100 ohm and 200 ohm in series

  I = 12 / 300                     = 0.0400 A

  wrong:  P(200) = 12 * 0.0400     = 0.480 W
  right:  V(200) = 0.0400 * 200    = 8.00 V
          P(200) = 8.00 * 0.0400   = 0.320 W

  and the 0.480 W was not nonsense - it is the power in the whole circuit:

          P(100) = 4.00 * 0.0400   = 0.160 W
          0.320 + 0.160              0.480 W
```

That is what makes it tempting. The wrong answer is not a meaningless number; it is a
real quantity belonging to something else in the same drawing, so it survives every
sanity check based on size and units. It is only wrong about *whose* power it is.

The same slip in reverse is taking a component's voltage and multiplying by the supply's
total current, which is what happens in the parallel case. If either of your two numbers
came from a different component than the other, stop and get the pair from one place.

## From watts to joules, and to the bill

A watt is a joule per second, so a component's energy over a stretch of time is $E = Pt$,
with $t$ in seconds. That one line connects this module to batteries and to bills.

```
the 60 W heating element of the numeric question, left on for 20 minutes:

  E = P t = 60 W * 1200 s              = 72 000 J     = 72 kJ

what it costs a 12 V, 40 Ah battery:

  I        = P / V = 60 / 12           = 5.0 A
  runtime  = 40 Ah / 5.0 A             = 8.0 h
  energy   = 12 V * 40 Ah              = 480 Wh       = 1.73 MJ
```

The domestic unit is the kilowatt-hour: 1 kWh is 1000 W for 3600 s, or 3.6 MJ. So the
entire car battery holds 0.48 kWh — about half a unit of electricity, which a 3 kW kettle
would get through in under ten minutes. Batteries store an unimpressive amount of energy
for their size, and it is worth having that calibration before meeting a module about
supplies.

## A rating is a temperature, not an electrical limit

A "quarter-watt resistor" is not a component that refuses to accept more than 0.25 W. It
accepts whatever the circuit gives it and obeys Ohm's law all the way to destruction. The
number is a promise from the manufacturer about how hot it will get: exceed it and the
part runs above the temperature its materials tolerate, drifts in value, discolours, and
eventually fails — sometimes open, sometimes as a short, sometimes on fire.

Because the promise is thermal, it comes with an ambient temperature attached. A film
resistor is typically rated at 70 °C surroundings and derated linearly to zero at 155 °C,
where the part would be at its limit making no heat at all:

```
a 0.25 W film resistor, inside a box sitting at 100 C:

  fraction allowed = (155 - 100) / (155 - 70)  = 55 / 85   = 0.647
  allowed power    = 0.647 * 0.25                          = 0.162 W
```

A third of the rating gone, and the schematic looks identical. The same reasoning is why
a part packed between other hot components needs more derating than the datasheet curve
gives, and why designers habitually specify a resistor rated for twice the dissipation
they calculated. It costs almost nothing and removes an entire category of failure.

## Where "all of it becomes heat" stops being true

$P = VI$ itself is safe: it follows from two definitions and holds for any two-terminal
component in this course. What does not generalise is the sentence about heat.

- **Anything that is not a resistor.** A motor turns most of its input into shaft work
  and only its winding's $I^2R$ into heat. An LED emits a fifth to a half of it as light.
  A battery on charge stores most of it chemically and wastes the rest in its own
  internal resistance — module 6's subject. $P = VI$ still gives the total rate; what
  becomes of it is the component's business.
- **Alternating current.** Instant by instant $p = vi$ still holds, but the *average*
  power is not the average voltage times the average current. It brings in RMS values and
  a power factor, and a component can then carry large currents at large voltages while
  dissipating nothing at all. EE102.
- **Self-heating.** $P = V^2/R$ uses the cold $R$. A resistor at its rated power is hot
  enough to have shifted its own value slightly, so the real dissipation differs a little
  from the calculated one. For a thermistor the shift is the whole point, and the
  feedback can run away.
- **Short pulses.** A rating is a steady-state average. A part will take many times its
  rating for a millisecond, because its own heat capacity buys time before the
  temperature arrives. Datasheets carry a separate pulse-energy curve for exactly this.
''',
                },
            ],
            "quiz": {
                "title": "Ohm's law and what it costs in heat",
                "minutes": 8,
                "questions": [
                    {
                        "q": "12 V is applied across a 3 kΩ resistor. What current flows?",
                        "opts": ["36 mA", "4 mA", "250 mA", "0.25 mA"],
                        "a": 1,
                        "why": r'''
$I = V/R = 12 / 3000 = 0.004$ A, which is 4 mA. The answer 36 mA comes from
multiplying instead of dividing, and 250 mA from dividing the resistance by the
voltage. A quick sanity check: a few volts across a few thousand ohms always gives a
few milliamps, and that pairing — volts, kilohms, milliamps — is worth memorising,
because $\text{V}/\text{k}\Omega = \text{mA}$ exactly.
''',
                    },
                    {
                        "q": "For a fixed resistor, doubling the voltage across it multiplies the power it dissipates by:",
                        "opts": ["2", "4", "1 — power does not change", "√2"],
                        "a": 1,
                        "why": r'''
Four. Doubling the voltage doubles the current as well, and $P = VI$ multiplies the
two, so the power goes up by a factor of four. The formula $P = V^2/R$ says the same
thing in one step. Answering 2 means treating the current as fixed — but the current
is not free to stay put once the voltage moves, because Ohm's law ties them together.
''',
                    },
                    {
                        "q": "A resistor is rated at 0.25 W. What is the smallest resistance you may put across a 10 V supply without exceeding that rating?",
                        "opts": ["25 Ω", "40 Ω", "400 Ω", "4 kΩ"],
                        "a": 2,
                        "why": r'''
$P = V^2/R$, so $R = V^2/P = 100/0.25 = 400$ Ω. Note the direction of the inequality:
a *smaller* resistance draws a *larger* current and burns *more* power, so 400 Ω is a
lower limit — 4 kΩ is perfectly safe here, just not the smallest safe value.
''',
                    },
                    {
                        "q": "Two resistors, 100 Ω and 400 Ω, are connected in series so the same current flows through both. Which dissipates more power?",
                        "opts": [
                            "the 100 Ω, because a lower resistance always means more heat",
                            "the 400 Ω",
                            "they dissipate the same, because the current is the same",
                            "it cannot be decided without knowing the supply voltage",
                        ],
                        "a": 1,
                        "why": r'''
With a shared current the useful form is $P = I^2R$: the same $I^2$ multiplies both, so
the larger resistance dissipates more — four times more here, whatever the supply
voltage turns out to be. The trap is answering from $P = V^2/R$, which is correct only
when the two parts share a *voltage*, which is the parallel case, not this one. Pick
the form that matches the quantity the two components have in common.
''',
                    },
                    {
                        "q": "A component obeys Ohm's law. Which statement is therefore true?",
                        "opts": [
                            "a plot of voltage against current through it is a straight line through the origin",
                            "it dissipates no power",
                            "the current through it is fixed regardless of the voltage",
                            "its resistance falls as the current rises",
                        ],
                        "a": 0,
                        "why": r'''
$V = IR$ with $R$ constant is the equation of a straight line through the origin, and
its gradient *is* the resistance. That is what obeying Ohm's law means, and it is a
property real components only approximately have: a filament lamp's resistance rises
sharply as it heats, so its line bends. Every component in this course is taken as
perfectly ohmic.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "Volts, kilohms and milliamps",
                    "minutes": 7,
                    "caption": "one law made the subject of each of its symbols, prefixes left in place",
                    "lang": "text",
                    "brief": r'''
Almost every arithmetic mistake in this subject is a factor of a thousand. The cure is
not to be careful; it is to work in units that already agree with each other.

Volts, **kilohms** and **milliamps** are such a set: a volt divided by a kilohm *is* a
milliamp, exactly, because the kilo on the bottom and the milli on the top are the same
factor of a thousand and cancel. Volts, ohms and amps are another such set. Mixing the
two is where the zeros go missing.
''',
                    "listing": """one law, three subjects, and the prefixes that make it painless
---------------------------------------------------------------

  a 4.7 kohm resistor with 9.0 V across it

    I = V / R
      = 9.0 V / 4700 ohm
      = 0.0019149 A            correct, and a nuisance to read

  the same sum with the prefixes left where they are:

    I = 9.0 V / 4.7 kohm
      = ___ mA                 volts over kilohms comes out in milliamps

  backwards: what resistance draws 25 mA from a 5.0 V supply?

    R = V / I
      = 5.0 V / 25 mA
      = ___ kohm               ... which is 200 ohm

  forwards again: the voltage a 12 mA current makes across 330 ohm

    V = I * R
      = 0.012 A * 330 ohm
      = ___ V

  and what that last resistor is costing in heat

    P = V * I
      = 3.96 V * 0.012 A
      = ___ W                  47.5 mW, safe on a quarter-watt part
""",
                    "blanks": [
                        {
                            "prompt": "9.0 V across 4.7 kΩ. How many milliamps?",
                            "hole": "?",
                            "opts": ["1.9", "0.0019", "1900", "42.3"],
                            "a": 0,
                            "why": "$9.0/4.7 = 1.9$, and because the units were volts and kilohms the "
                                   "answer is already in milliamps \u2014 it is the same 0.0019149 A as the "
                                   "line above, written without the leading zeros. The value 0.0019 is "
                                   "the answer in amps, which is right but is not what the line asks "
                                   "for; 42.3 is $9.0 \\times 4.7$, which is a multiplication where a "
                                   "division belongs.",
                        },
                        {
                            "prompt": "5.0 V at 25 mA. How many kilohms?",
                            "hole": "?",
                            "opts": ["0.20", "125", "5.0", "20"],
                            "a": 0,
                            "why": "$5.0/25 = 0.20$ k\u03a9, or 200 \u03a9. The pairing works in this "
                                   "direction too: volts divided by milliamps comes out in kilohms. The "
                                   "value 125 is $5.0 \\times 25$, and 20 would be the answer if the "
                                   "current were 0.25 mA rather than 25 mA \u2014 a factor of a hundred, "
                                   "which is the kind of slip this whole exercise exists to prevent.",
                        },
                        {
                            "prompt": "12 mA through 330 Ω. How many volts?",
                            "hole": "?",
                            "opts": ["3.96", "39.6", "27.5", "0.0364"],
                            "a": 0,
                            "why": "$0.012 \\times 330 = 3.96$ V. This line is written in amps and ohms "
                                   "rather than milliamps and kilohms, and both are fine \u2014 what is "
                                   "not fine is one of each. Milliamps times ohms would give millivolts, "
                                   "so 12 mA times 330 \u03a9 is 3960 mV, which is the same 3.96 V "
                                   "arriving by the other road. The value 27.5 is $330/12$, a division "
                                   "where Ohm's law wants a multiplication.",
                        },
                        {
                            "prompt": "3.96 V across it while 12 mA flows through it. How many watts?",
                            "hole": "?",
                            "opts": ["0.0475", "0.475", "4.75", "0.00475"],
                            "a": 0,
                            "why": "$3.96 \\times 0.012 = 0.0475$ W, which is 47.5 mW. Volts times "
                                   "amps gives watts directly; volts times *milli*amps would give "
                                   "milliwatts, and 3.96 \u00d7 12 = 47.5 mW is the same number again. "
                                   "Both routes are safe as long as you do not take one unit from each. "
                                   "You could also have reached it as $I^2R = 0.012^2 \\times 330$ "
                                   "without ever computing the 3.96 V.",
                        },
                    ],
                },
                {
                    "title": "Will the resistor survive?",
                    "minutes": 8,
                    "caption": "the same power three ways, then the voltage the part cannot take",
                    "lang": "text",
                    "brief": r'''
A power rating is a promise about temperature, so the only question it can answer is
"how much heat is this part making, and is that more than it was built to shed?"

The three forms of the power law all give the same watts. The one worth deriving is the
last line: the largest voltage a rated part may ever see, which is the form you reach
for when you are sizing a resistor rather than checking one.
''',
                    "listing": """a 220 ohm resistor, rated 0.25 W, with 6.0 V across it
------------------------------------------------------

  I  = V / R       = 6.0 / 220           = 0.02727 A      ... 27.3 mA

  P  = V * I       = 6.0 * 0.02727       = 0.1636 W
  P  = I^2 * R     = ___ * 220           = 0.1636 W       same watts, no new physics
  P  = V^2 / R     = 36 / 220            = ___ W          and once more

  0.1636 W is inside the 0.25 W rating, so the part lives. how much headroom?

  the largest voltage this part may ever see:

    P_max = V_max^2 / R    so    V_max = ___
                                       = sqrt(0.25 * 220)
                                       = 7.42 V

  so 6.0 V is fine and 8.0 V is not, and the margin is thinner than it looks:
  power follows the ___ of the voltage, so 8.0 V would mean 0.29 W.
""",
                    "blanks": [
                        {
                            "prompt": "$I^2$, with the current from the line above.",
                            "hole": "?",
                            "opts": ["0.000744", "0.02727", "0.0545", "7.44"],
                            "a": 0,
                            "why": "$0.02727^2 = 7.44\\times10^{-4}$, and $7.44\\times10^{-4} \\times 220 "
                                   "= 0.1636$ W. Squaring a number smaller than one makes it smaller, "
                                   "which is why the figure looks alarmingly tiny and the watts still "
                                   "come out the same as the line above. Leaving the current unsquared "
                                   "gives $0.02727 \\times 220 = 6.0$, which is the 6.0 V back again "
                                   "wearing the wrong unit — a useful sign that the squaring was "
                                   "skipped.",
                        },
                        {
                            "prompt": "$V^2/R$, with $V^2 = 36$.",
                            "hole": "?",
                            "opts": ["0.1636", "1.636", "6.11", "0.0164"],
                            "a": 0,
                            "why": "$36/220 = 0.1636$ W \u2014 the third route to the same number, and the "
                                   "quickest of the three when the voltage is the thing you know. The "
                                   "value 6.11 is $220/36$, the fraction upside down: more resistance "
                                   "across a fixed voltage means *less* heat, not more, because the "
                                   "current falls.",
                        },
                        {
                            "prompt": "Rearranged for the voltage, $V_{max}$ is:",
                            "hole": "?",
                            "opts": ["sqrt(P_max * R)", "P_max * R", "sqrt(P_max / R)", "P_max / R"],
                            "a": 0,
                            "why": "Multiply both sides of $P = V^2/R$ by $R$ and take the root: "
                                   "$V_{max} = \\sqrt{P_{max}R} = \\sqrt{0.25 \\times 220} = 7.42$ V. "
                                   "The expression $\\sqrt{P_{max}/R}$ is the matching limit on the "
                                   "*current*, $\\sqrt{0.25/220} = 33.7$ mA \u2014 a genuine formula, "
                                   "just not the one this line wants. Check the pair against each "
                                   "other: $7.42 \\times 0.0337 = 0.25$ W, as it must be.",
                        },
                        {
                            "prompt": "Power follows the ___ of the voltage.",
                            "hole": "?",
                            "opts": ["square", "square root", "reciprocal", "logarithm"],
                            "a": 0,
                            "why": "$P = V^2/R$, so a third more voltage is $1.33^2 = 1.78$ times the "
                                   "power: $8.0^2/220 = 0.29$ W against 0.164 W at 6.0 V. That is why "
                                   "the headroom between 6.0 V and the 7.42 V limit is smaller than the "
                                   "voltages suggest, and why designers specify a part rated for twice "
                                   "the dissipation they calculated rather than for a tenth more.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One resistor, one supply, one unknown",
                    "minutes": 4,
                    "brief": r'''
The whole of Ohm's law, used once. There is one loop, one component in it, and the
supply voltage appears across that component and nowhere else.

The only thing to be careful about is the unit, and it is asked for in milliamps
precisely so that the volts-over-kilohms shortcut is the easy road.
''',
                    "prompt": "What current flows in the loop?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 1500},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "9.00 V"},
                        {"label": "R1", "value": "1.50 k\u03a9"},
                    ],
                    "aside": "Both ground symbols are the same node \u2014 that is what ground means \u2014 "
                             "so this really is a single loop with one component in it.",
                    "answer": 6.0,
                    "tol": 0.05,
                    "unit": "mA",
                    # Read the drop and the resistance off the solve rather than restating the
                    # 9 and the 1500 that are already printed on the drawing.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.kind === 'R'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1000;
''',
                    "hint": "$I = V/R$. Volts divided by kilohms lands in milliamps with no conversion "
                            "at all.",
                    "wrong": "If you got 0.006, that is the answer in amps rather than milliamps. If you "
                             "got 13500, the two numbers were multiplied \u2014 $V = IR$ was not "
                             "rearranged before use.",
                    "why": "$I = V/R = 9.00/1500 = 0.00600$ A, which is 6.00 mA. Working in the mixed "
                           "units instead: $9.00\\ \\text{V} / 1.50\\ \\text{k}\\Omega = 6.00$ mA "
                           "directly. That resistor is turning $VI = 9.00 \\times 0.006 = 54$ mW into "
                           "heat, which any ordinary part will shrug off. Note what makes this the "
                           "easiest question in the module: the supply voltage appears across the "
                           "resistor in full, because there is nothing else in the loop to take a share "
                           "of it.",
                },
                {
                    "title": "A heater element, working backwards",
                    "minutes": 6,
                    "brief": r'''
Now the resistance is the unknown, and it is not handed to you with a current beside it.
What you get instead is a power, which means one substitution before Ohm's law can be
used at all.

No schematic here: the element is a two-terminal thing across a supply, and drawing it
would tell you nothing the sentence does not.
''',
                    "prompt": "What resistance does the element present while it is running?",
                    "note": "Give the answer in ohms, to two decimal places.",
                    "figure": "A 12.0 V vehicle accessory socket runs a small heating element. With the "
                              "element switched on and up to temperature, it is turning 60.0 W into "
                              "heat, and the socket holds 12.0 V steady while it does so.",
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "Power dissipated", "value": "60.0 W"},
                    ],
                    "aside": "Two of the three power forms involve the resistance. Pick the one whose "
                             "other quantity you already have.",
                    "answer": 2.4,
                    "tol": 0.02,
                    "unit": "\u03a9",
                    "hint": "$P = V^2/R$ is the form built from the two numbers you were given. "
                            "Rearranged, $R = V^2/P$.",
                    "wrong": "If you got 5, that is the current in amps \u2014 $P/V$ \u2014 which is the "
                             "right first step if you would rather go the long way round, but is not a "
                             "resistance. If you got 0.2, the fraction is upside down: $V/P$ has the "
                             "units of ohms per volt, which is not a thing.",
                    "why": "$R = V^2/P = 12.0^2/60.0 = 144/60.0 = 2.40\\ \\Omega$. The long way round "
                           "gives the same: $I = P/V = 60.0/12.0 = 5.00$ A, then $R = V/I = 12.0/5.00 = "
                           "2.40\\ \\Omega$. Two things are worth noticing. Five amps through 2.4 \u03a9 "
                           "is an enormous current by the standards of the rest of this course, and it "
                           "is what heating anything actually costs \u2014 power at 12 V has to come as "
                           "current, because there is no voltage to spare. And the phrase *while it is "
                           "running* is doing real work: a heating element is a coil of wire whose "
                           "resistance climbs as it warms, so the cold element is well under 2.4 \u03a9 "
                           "and the switch-on current is well over 5 A.",
                },
                {
                    "title": "Two resistors, one current, one voltage wanted",
                    "minutes": 7,
                    "brief": r'''
Two components in a row now, and only one current, because there is nowhere else for
charge to go: whatever leaves the supply passes through both parts and comes back. An
ammeter placed anywhere in the loop reads the same 40.0 mA, and that reading is given
to you here.

That single number is the bridge. Ohm's law applied to *one* resistor needs the current
through *that* resistor, and in a single loop there is only one current to have.
''',
                    "prompt": "What voltage appears across the 200 Ω resistor?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 100},
                            {"id": "r2", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 200},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 7},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 9]},
                            {"a": [11, 7], "b": [15, 7]},
                            {"a": [11, 11], "b": [11, 13]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "R1 (top)", "value": "100 \u03a9"},
                        {"label": "R2 (bottom)", "value": "200 \u03a9"},
                        {"label": "Ammeter in the loop", "value": "40.0 mA"},
                    ],
                    "aside": "The bottom of R2 is at ground, so the voltage across R2 is also the "
                             "voltage of the node the probe sits on. Those are the same number here "
                             "and will not always be.",
                    "answer": 8.0,
                    "tol": 0.05,
                    "unit": "V",
                    # The prompt names R2, so the check measures R2 — both ends taken out of the
                    # solve, so a re-drawn or re-valued schematic is re-measured rather than
                    # compared to a memory of this one.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r2'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]);
''',
                    "hint": "$V = IR$, with $I$ the meter reading and $R$ the resistor you are asked "
                            "about \u2014 not the pair of them.",
                    "wrong": "If you got 4, that is the drop across the 100 \u03a9, which is the other "
                             "resistor. If you got 12, that is the whole supply, which is what the two "
                             "of them share between them rather than what either one takes.",
                    "why": "$V = IR = 0.0400 \\times 200 = 8.00$ V. Check it against the rest of the "
                           "loop: the 100 \u03a9 takes $0.0400 \\times 100 = 4.00$ V, and $8.00 + 4.00$ "
                           "is the 12.0 V the supply put in \u2014 every joule handed to a coulomb is "
                           "handed back before it gets home. Notice also where the meter reading came "
                           "from, since you were not asked to find it: the pair present 300 \u03a9 to "
                           "the supply, and $12.0/300 = 0.0400$ A. Adding resistances in a row like "
                           "that is the next module's rule; the question was written so you would not "
                           "need it yet.",
                },
                {
                    "title": "A source that fixes the current instead",
                    "minutes": 8,
                    "brief": r'''
Every source so far has been a **voltage** source: it fixes the voltage across itself
and lets the circuit decide the current. This one is the other kind. An ideal
**current** source fixes the current through itself at 5.00 mA and produces whatever
voltage that takes — 11 V here, 11 kV if you connected it to something a thousand times
larger, and nothing at all if you short it out.

That inversion is why $P = I^2R$ is the natural form here and $P = V^2/R$ is the awkward
one: the current is the quantity you have been handed.
''',
                    "prompt": "How much power does the resistor turn into heat?",
                    "note": "Give the answer in milliwatts, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "i1", "kind": "I", "x": 3, "y": 7, "rot": 1, "value": 0.005},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 2200},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 mA, ideal"},
                        {"label": "R1", "value": "2.20 k\u03a9"},
                    ],
                    "aside": "The source and the resistor are the only two things in the loop, so all "
                             "5.00 mA goes through the resistor. Square the current before you multiply "
                             "by the resistance, not after.",
                    "answer": 55.0,
                    "tol": 0.5,
                    "unit": "mW",
                    # Power is no node of this circuit, so the check takes the drop across the
                    # resistor and its value out of the solve and squares the one over the other.
                    # Squaring also makes it blind to which way round the source is drawn, which
                    # is the physical point the question is making.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.kind === 'R'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
return drop * drop / r.value * 1000;
''',
                    "hint": "$P = I^2R$, with $I$ in amps. 5.00 mA is $5.00\\times10^{-3}$ A, and its "
                            "square is $2.50\\times10^{-5}$.",
                    "wrong": "If you got 11.0, that is the voltage across the resistor in volts rather "
                             "than the power in milliwatts \u2014 there is one more multiplication to "
                             "go. If you got 0.0550, that is the right power in the wrong unit: the "
                             "answer was asked for in milliwatts. And if you got something in the tens "
                             "of thousands, the 5 went into $I^2R$ as amps rather than milliamps, which "
                             "is a factor of $1000^2$ because the current is squared.",
                    "why": "$P = I^2R = (5.00\\times10^{-3})^2 \\times 2200 = 2.50\\times10^{-5} "
                           "\\times 2200 = 0.0550$ W, or 55.0 mW. The long way confirms it: the "
                           "resistor has $V = IR = 0.00500 \\times 2200 = 11.0$ V across it, and "
                           "$P = VI = 11.0 \\times 0.00500 = 0.0550$ W. The 11.0 V is worth dwelling "
                           "on \u2014 nobody chose it, and it is not a property of the source. Replace "
                           "the 2.2 k\u03a9 with 22 k\u03a9 and the same source produces 110 V and "
                           "dissipates ten times the power, without being adjusted. A real current "
                           "source has a ceiling called its compliance voltage, beyond which it gives "
                           "up and stops being a current source; an ideal one, which is all this course "
                           "uses, has none.",
                },
                {
                    "title": "How far can you turn the supply up?",
                    "minutes": 12,
                    "brief": r'''
A bench supply feeds two resistors in a row. It is presently set to 6.00 V and nothing
in the circuit is unhappy. The question is how far the knob can go before something is
destroyed.

Two ratings are in play and they are not the same, so there are two limits and only the
tighter of them matters. Work out which part gets there first *before* computing
anything, if you can — and be ready to be wrong, because the part that is hottest and
the part that is closest to its rating need not be the same part.

Nothing here is a node voltage. The answer is a setting on the supply.
''',
                    "prompt": "What is the highest supply voltage that keeps both resistors inside their ratings?",
                    "note": "Give the answer in volts, to two decimal places. Assume the ratings are "
                            "hard limits and that both resistances stay put.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 100},
                            {"id": "r2", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 220},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 9]},
                            {"a": [11, 11], "b": [11, 13]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, at present", "value": "6.00 V, adjustable"},
                        {"label": "R1", "value": "100 \u03a9, rated 0.25 W"},
                        {"label": "R2", "value": "220 \u03a9, rated 1.00 W"},
                    ],
                    "aside": "One loop, so one current, and both parts carry it. A part is in trouble "
                             "when its own $I^2R$ reaches its own rating \u2014 the ratings do not add "
                             "up into a budget for the pair.",
                    "answer": 16.0,
                    "tol": 0.1,
                    "unit": "V",
                    # Measure what each part is actually dissipating at the drawn supply voltage,
                    # express it as a fraction of that part's rating, and scale the supply until
                    # the worst fraction is exactly 1. Power goes as the square of the supply, so
                    # the scale factor is the square root. The ratings are the only constants
                    # restated here, and they appear in `given` rather than on the drawing.
                    "check": r'''
const d = c.dc();
const rating = { r1: 0.25, r2: 1.0 };
const vs = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0].value;
let worst = 0;
c.net.parts.forEach(function (p) {
  if (p.kind !== 'R') return;
  const drop = d.v[p.n1] - d.v[p.n2];
  const frac = (drop * drop / p.value) / rating[p.id];
  if (frac > worst) worst = frac;
});
return vs / Math.sqrt(worst);
''',
                    "hint": "Each part has a largest current it may carry: $I_{max} = \\sqrt{P/R}$ from "
                            "its own rating and its own resistance. Work both out, keep the smaller, "
                            "and ask what supply voltage produces that current in the loop.",
                    "wrong": "If you got 21.57, the 220 \u03a9 was taken as the limiting part \u2014 it "
                             "is the hotter of the two, but it has four times the budget. If you got "
                             "20.0, the two ratings were added into a 1.25 W allowance for the pair; "
                             "they cannot be spent jointly, because the parts do not reach their limits "
                             "together. If you got 5.00, the whole supply was put across the 100 "
                             "\u03a9 alone.",
                    "why": "Take each part on its own terms. The 100 \u03a9 may carry "
                           "$\\sqrt{0.25/100} = 50.0$ mA; the 220 \u03a9 may carry "
                           "$\\sqrt{1.00/220} = 67.4$ mA. The loop has one current, so the smaller "
                           "limit is the real one: 50.0 mA. The pair present 320 \u03a9 to the supply, "
                           "so that current needs $0.0500 \\times 320 = 16.0$ V.\n\n"
                           "Check the answer from the other end. At 16.0 V the 100 \u03a9 dissipates "
                           "$0.0500^2 \\times 100 = 0.250$ W \u2014 exactly its rating \u2014 and the "
                           "220 \u03a9 dissipates $0.0500^2 \\times 220 = 0.550$ W, a little over half "
                           "of what it is allowed. So the larger resistor is making more than twice "
                           "the heat and is nowhere near failing, while the smaller one is on the "
                           "edge. That is the point of the question: $P = I^2R$ decides which part is "
                           "hotter, and the *ratio to the rating* decides which part dies.\n\n"
                           "There is a second route, which is quicker once you trust it. At the drawn "
                           "6.00 V the loop carries 18.75 mA, and the 100 \u03a9 is dissipating "
                           "35.16 mW against its 250 mW \u2014 14.06% of budget. Power follows the square "
                           "of the supply, so the voltage may rise by $\\sqrt{1/0.1406} = 2.667$ times, "
                           "and $6.00 \\times 2.667 = 16.0$ V. In practice nobody runs a part at exactly "
                           "its rating: derate to half and the honest answer is about 11 V.",
                },
            ],
            "derive": {
                "title": "Three ways to write one watt",
                "minutes": 12,
                "vars": ["P", "V", "I", "R", "E", "Q", "t"],
                "brief": r'''
Nothing new is introduced below. Every line comes from three statements you already
have: power is energy per unit time, $P = E/t$; a volt is a joule per coulomb,
$V = E/Q$; an amp is a coulomb per second, $I = Q/t$. Ohm's law, $V = IR$, joins the
last two steps.

Write each answer as an expression in the symbols named, with no numbers in it.
''',
                "steps": [
                    {
                        "prompt": "Start from $P = E/t$ and substitute $E = VQ$. Write $P$ in terms of $V$ and $I$.",
                        "answer": "V I",
                        "hint": "After the substitution you have $P = VQ/t$, and $Q/t$ has a name.",
                        "deconstruct": [
                            "$P = \\dfrac{E}{t} = \\dfrac{VQ}{t} = V \\cdot \\dfrac{Q}{t}$.",
                            "$Q/t$ is the definition of current, so the bracket is simply $I$.",
                            "The coulombs cancelled \u2014 as they had to, because charge is not consumed and so is never the thing being counted.",
                        ],
                    },
                    {
                        "prompt": "That result holds for any two-terminal component. Now make it a resistor: substitute $V = IR$ into it and write $P$ in terms of $I$ and $R$.",
                        "answer": "I^{2} R",
                        "hint": "Replace the $V$ you just wrote with $IR$, and count how many $I$s you now have.",
                    },
                    {
                        "prompt": "Go back to $P = VI$ and substitute for the *current* instead. Write $P$ in terms of $V$ and $R$.",
                        "answer": "\\frac{V^{2}}{R}",
                        "hint": "Ohm's law rearranged is $I = V/R$. Put that in place of $I$.",
                    },
                    {
                        "prompt": "A resistor of resistance $R$ is rated for a maximum power $P$. Rearrange the last result to give the largest voltage $V$ that may be placed across it.",
                        "answer": "\\sqrt{P R}",
                        "hint": "Multiply both sides by $R$, then take the square root of both sides.",
                        "deconstruct": [
                            "$P = V^2/R$ becomes $PR = V^2$.",
                            "So $V = \\sqrt{PR}$, and the negative root is discarded because a limit on the magnitude is what was asked for.",
                        ],
                    },
                    {
                        "prompt": "And the largest current $I$ that same part may carry, in terms of $P$ and $R$.",
                        "answer": "\\sqrt{\\frac{P}{R}}",
                        "hint": "Do the same to $P = I^2R$: divide by $R$, then take the root.",
                    },
                ],
                "closing": r'''
Put a real part through it. A 220 Ω resistor rated at a quarter of a watt may take
$\sqrt{0.25 \times 220} = 7.42$ V across it, and may carry
$\sqrt{0.25/220} = 33.7$ mA through it. Those are not two facts. They are one fact
stated twice, and the two expressions prove it between them: multiply them and the
resistance cancels, leaving $P$; divide them and the power cancels, leaving $R$.

Two habits follow from the shape of these results.

The first is that both limits carry a square root, so **doubling a part's rating buys
you only 41% more voltage**. Heat is expensive to buy your way out of, which is why the
usual fix for a part running hot is a different circuit rather than a bigger resistor.

The second is the mirror image and matters more often: because power goes as the
*square* of the voltage, a part run at 70% of its rated voltage is at half its rated
power, and one run at half its rated voltage is at a quarter. Designers habitually size
resistors at twice the dissipation they calculated. It costs nothing and it removes an
entire class of failure.

One caution before you use $V_{max} = \sqrt{PR}$ on anything large. It assumes the power
rating is the only limit, and for high-value resistors it is not: a 10 MΩ quarter-watt
part would need 1580 V by this formula, and it will arc over long before that. Real
parts carry a separate maximum working voltage, typically a few hundred volts, and the
limit that applies is whichever is smaller.
''',
            },
            "build": {
                "title": "One resistor, one current",
                "minutes": 20,
                "brief": r'''
The canvas opens with a 12 V supply and a ground symbol, already joined. Your job is
to finish the loop so that **exactly 4 mA flows**.

What the finished circuit must do:

- one resistor, and only one, connected across the whole supply
- the current out of the supply is 4 mA
- a probe on the node at the top of the resistor, so the checks can read the voltage
  there

## How to draw it

Pick the resistor tool, place it, and wire its top pin to the supply's + terminal
(the **top** pin of a vertical source) and its bottom pin down to a second ground
symbol. Two ground symbols are one node — that is what ground means, and it saves a
long wire round the outside. Then place a probe (`OUT`) on the top node.

Click a component to edit its value. The value you need is not given: work it out
from $R = V/I$ before you type anything.

The checks measure the finished circuit. Any resistance that produces 4 mA passes,
however you lay the drawing out.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3000},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p4", "kind": "OUT", "x": 11, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 5], "b": [11, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 12 V supply and exactly one resistor", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
c.assert(c.count('R') === 1,
  'This exercise wants one resistor and nothing else, so the current has only one path to take. Found ' + c.count('R') + '.');
'''},
                    {"name": "the whole 12 V appears across the resistor", "code": r'''
c.close(c.vout(), 12, 0.005,
  'the probe voltage — it belongs on the node joining the supply + terminal to the top of the resistor');
'''},
                    {"name": "the supply pushes 4 mA round the loop", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
c.close(i, 0.004, 0.02, 'the current out of the supply');
'''},
                    {"name": "the resistor turns 48 mW into heat", "code": r'''
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
const p = c.vout() * i;
c.close(p, 0.048, 0.03, 'the power in the resistor (P = V times I)');
'''},
                ],
                "hints": [
                    "Rearrange $V = IR$ into $R = V/I$. Remember that 4 mA is 0.004 A.",
                    "12 V and 4 mA give 3 kΩ. Type `3k` into the value box — the editor understands the k, M and m suffixes.",
                    "The + terminal of a vertical source is its **top** pin. Wire that to the top of the resistor, and the bottom of the resistor to a ground symbol.",
                    "A probe reads the voltage of the node it sits on, relative to ground. Put it on the top node, not the bottom one, or it will read 0 V.",
                ],
            },
            "lab": {
                "title": "Sizing a resistor and checking it survives",
                "runtime": "python",
                "minutes": 22,
                "brief": r'''
The same three sums as the circuit you just drew, written down so they can be reused.

- `resistor_for_current(volts, amps)` returns the resistance needed to draw that
  current from that voltage.
- `power(volts, ohms)` returns the power a resistor dissipates with that voltage
  across it.
- `within_rating(volts, ohms, rating_w)` returns `True` when that resistor stays
  inside its power rating, and `False` when it would cook. A resistor exactly at its
  rating counts as acceptable.

Write `within_rating` by calling `power`, not by repeating the formula. One place for
one fact.
''',
                "files": [{"name": "main.py", "content": r'''
"""Ohm's law and power, as three reusable functions."""


def resistor_for_current(volts, amps):
    """Resistance in ohms that draws `amps` when `volts` is across it."""
    # TODO: rearrange V = I R.
    return 0.0


def power(volts, ohms):
    """Power in watts dissipated by `ohms` with `volts` across it."""
    # TODO: P = V * I, and I = V / R.
    return 0.0


def within_rating(volts, ohms, rating_w):
    """True when the resistor stays at or below its power rating."""
    # TODO: call power() and compare.
    return False


if __name__ == "__main__":
    r = resistor_for_current(12.0, 0.004)
    print("12 V at 4 mA needs", r, "ohms")
    print("which dissipates", power(12.0, r), "W")
    print("safe on a quarter-watt part?", within_rating(12.0, r, 0.25))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Ohm's law and power, as three reusable functions."""


def resistor_for_current(volts, amps):
    """Resistance in ohms that draws `amps` when `volts` is across it."""
    return volts / amps


def power(volts, ohms):
    """Power in watts dissipated by `ohms` with `volts` across it."""
    return volts * volts / ohms


def within_rating(volts, ohms, rating_w):
    """True when the resistor stays at or below its power rating."""
    return power(volts, ohms) <= rating_w


if __name__ == "__main__":
    r = resistor_for_current(12.0, 0.004)
    print("12 V at 4 mA needs", r, "ohms")
    print("which dissipates", power(12.0, r), "W")
    print("safe on a quarter-watt part?", within_rating(12.0, r, 0.25))
'''}],
                "hints": [
                    "`resistor_for_current` is `volts / amps` — nothing more.",
                    "`power` can be written as `volts * volts / ohms`, or as `volts * (volts / ohms)`, which is literally V times I.",
                    "`within_rating` should end in a comparison, and a comparison in Python is already `True` or `False` — there is no need for an `if`.",
                ],
                "tests": [
                    {"name": "12 V at 4 mA wants 3 kilohms", "code": r'''
r = resistor_for_current(12.0, 0.004)
assert abs(r - 3000.0) < 1e-9, f"12 / 0.004 is 3000 ohms, got {r}"
'''},
                    {"name": "it works for other supplies too", "code": r'''
assert abs(resistor_for_current(5.0, 0.02) - 250.0) < 1e-9, "5 V at 20 mA is 250 ohms"
assert abs(resistor_for_current(230.0, 10.0) - 23.0) < 1e-9, "230 V at 10 A is 23 ohms"
'''},
                    {"name": "the circuit you drew dissipates 48 mW", "code": r'''
p = power(12.0, 3000.0)
assert abs(p - 0.048) < 1e-12, f"12 squared over 3000 is 0.048 W, got {p}"
'''},
                    {"name": "power goes as the square of the voltage", "code": r'''
a = power(5.0, 1000.0)
b = power(10.0, 1000.0)
assert abs(a - 0.025) < 1e-12, f"5 V across 1 k is 25 mW, got {a}"
assert abs(b / a - 4.0) < 1e-9, \
    f"doubling the voltage should quadruple the power, got a ratio of {b / a}"
'''},
                    {"name": "the rating test catches an overload", "code": r'''
assert within_rating(10.0, 500.0, 0.25) is True or within_rating(10.0, 500.0, 0.25) == True, \
    "10 V across 500 ohms is 0.2 W, comfortably inside a quarter watt"
assert not within_rating(10.0, 300.0, 0.25), \
    "10 V across 300 ohms is 0.333 W, which would cook a quarter-watt part"
assert within_rating(10.0, 400.0, 0.25), \
    "exactly at the rating counts as acceptable"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Series, parallel and Kirchhoff's two laws",
            "summary": "Charge does not pile up, and energy per charge depends on the point rather than the path. Everything else follows.",
            "concepts": [
                "Kirchhoff's current law (KCL): at any node, the currents flowing in add up to the currents flowing out. It is conservation of charge, stated locally.",
                "KCL holds for any closed boundary, not only for a point: whatever current crosses into a region of a circuit must cross back out of it. A board fed by two wires returns on one exactly what it took on the other.",
                "Kirchhoff's voltage law (KVL): round any closed loop, the voltage rises equal the voltage drops. It is conservation of energy, stated locally.",
                "Two components are in **series** when the same current must pass through both: their resistances add, $R = R_1 + R_2$.",
                "Two components are in **parallel** when the same voltage appears across both: their conductances add, $1/R = 1/R_1 + 1/R_2$.",
                "Series and parallel are statements about *wiring*, so \"they share a current\" and \"they share a voltage\" hold for any components at all. Only the step that adds *resistances* needs the parts to obey Ohm's law.",
                "Conductance is the reciprocal of resistance, $G = 1/R$, measured in siemens (S). Parallel is the case where conductances add, which is the only reason the parallel rule looks upside down.",
                "For exactly two resistors in parallel the shortcut $R = R_1R_2/(R_1+R_2)$ is the same formula rearranged. Two equal resistors in parallel give half of one.",
                "Adding a resistor in parallel always *lowers* the total resistance, because it opens another path. Adding one in series always raises it.",
                "A network that reduces by repeated series and parallel steps can be collapsed to a single resistance; one that does not needs KCL and KVL written out node by node.",
            ],
            "read": [
                {
                    "title": "Same current, or same voltage",
                    "minutes": 18,
                    "body": r'''
Two components are **in series** when the only way out of one is into the other. They
are **in parallel** when both ends of one are joined to both ends of the other. Those
are statements about wiring and nothing else — nothing about what the components are,
nothing about where they sit on the page — and every rule in this module is squeezed out
of them by one question: what do the two components have in common?

## Two tests you can run on the drawing

Before any arithmetic, decide which case you are in, and decide it by following wire
rather than layout.

**The series test.** Find the node between the two components and count what touches
it. If exactly two things do — one end of each — they are in series. A third connection
anywhere on that node breaks it, however far away the third wire is drawn.

**The parallel test.** Take the two ends of each component. If one pair of ends is the
same node *and* the other pair is the same node too, they are in parallel. Both pairs:
one shared end is not enough, and one shared end mistaken for two is the commonest
false positive there is.

Neither test mentions geometry, and that is deliberate. Wire is free in a schematic: a
node stays one node however far it is stretched, so a resistor at the top of the sheet
can be in parallel with one at the bottom, and two drawn neatly side by side can be in
neither relation at all. Trace the wire; do not trust the picture.

## Series: they share a current

Put two resistors in a row and look hard at the node between them. It is a piece of
metal with two wires attached, and nothing else at all. Charge does not collect there.
There is nowhere in a wire for it to sit, and a node the size of a solder joint holds
perhaps a picofarad — so a single nanocoulomb parked on it would put
$Q/C = 10^{-9}/10^{-12} = 1000$ V across it, and it would empty itself back out through
the attached wires long before anything could measure it. Whatever arrives leaves, at
the same rate, always. The current in the first resistor *is* the current in the
second.

Everything else is Ohm's law twice. Call the shared current $I$. The first resistor
takes $IR_1$ volts, the second takes $IR_2$, and the voltage across the pair is the sum
of the two:

$$V = IR_1 + IR_2 = I(R_1 + R_2)$$

A single resistor would need $R = R_1 + R_2$ to draw that same current from that same
voltage, and nothing outside the pair can tell the two situations apart. **Series
resistances add.** Nothing in the argument used the fact that there were only two of
them, so the same reasoning gives $R = R_1 + R_2 + \dots + R_n$ for any number of
components in a row.

There is a physical picture underneath it. Module 2's $R = \rho L/A$ says resistance
grows in proportion to length, and two identical resistors in series are one resistor
of twice the length. Twice the length, twice the resistance: the series rule *is* that
geometry, arrived at from the circuit side.

## Parallel: they share a voltage

Now join both ends instead. The top of one resistor and the top of the other are the
same node; so are the two bottoms. A voltage is a property of a pair of nodes, so both
resistors have the same voltage $V$ across them — not nearly, identically, by what
"same node" means.

This time it is the currents that differ. Each branch draws $V/R$ of its own, and the
node above has to supply both:

$$I = \frac{V}{R_1} + \frac{V}{R_2} = V\left(\frac{1}{R_1} + \frac{1}{R_2}\right)$$

A single resistor drawing that current at that voltage would have
$1/R = 1/R_1 + 1/R_2$. So the *reciprocals* add, and the rule looks awkward only
because it is being quoted in the wrong currency. The natural quantity for parallel
work is **conductance**, $G = 1/R$, measured in siemens: amps per volt instead of volts
per amp. In conductance the rule is as tidy as the series one — parallel conductances
add, $G = G_1 + G_2 + \dots$ — and the reciprocals are the price of insisting on ohms.

The geometric picture is the mirror of the last one. Two identical resistors side by
side with both ends joined are one resistor of twice the cross-section, and $R = \rho L/A$
falls as $A$ grows. Twice the area, half the resistance.

For exactly two resistors it is worth doing the algebra once and keeping the result:

$$\frac{1}{R} = \frac{R_2 + R_1}{R_1R_2} \qquad\Rightarrow\qquad R = \frac{R_1R_2}{R_1 + R_2}$$

Product over sum, and it is only ever valid for two. Three branches want the
reciprocals, or two applications of the shortcut one after the other: three 3 kΩ
resistors come to 1 kΩ, whether by $1/3 + 1/3 + 1/3 = 1$ or by $3\|3 = 1.5$ kΩ followed
by $1.5\|3 = 1$ kΩ. Stretched across all three at once the shortcut gives $27/9 = 3$
kΩ, which is not merely wrong but impossible: larger than a single branch.

## Which way each rule pushes

A resistor added **in series** always raises the total: the current now has more to
squeeze through. A resistor added **in parallel** always lowers it, however large the
addition is, because a route has been opened without any route being closed. The
algebra says the same thing if you write the result as

$$R = R_1 \times \frac{R_2}{R_1 + R_2}$$

The second factor has a smaller top than bottom, so it is below one and the pair is
below $R_1$; the argument is symmetric, so the pair is below $R_2$ too. **A parallel
combination is always below the smallest resistor in it.** If yours is not, the
arithmetic is wrong, and checking costs a second.

Two bounds fall out, and both are worth using every time. A series total sits **above
the largest** part in it; a parallel total sits **below the smallest**, and never below
that smallest divided by the number of branches. So 2 kΩ, 3 kΩ and 6 kΩ in parallel
must land between $2/3 = 0.67$ kΩ and 2 kΩ — and they come to exactly 1 kΩ.

How far below depends on the mismatch. A 10 kΩ resistor with another 10 kΩ across it
becomes 5 kΩ; with 100 kΩ across it, 9.09 kΩ; with 1 MΩ across it, 9.90 kΩ. A branch a
hundred times larger moves the answer by one percent — which is why a voltmeter with a
10 MΩ input can be clipped across a 10 kΩ resistor without anyone thinking about it, and
why the same meter across a 10 MΩ resistor halves what it came to measure.

## The mistakes, and why each one is tempting

Three, roughly in the order you will meet them.

**Adding resistances that are in parallel.** Everyone does this once. It is tempting
because "total" sounds like a sum, because adding is what worked in the previous
problem, and because everywhere else in life putting two things together gives you more
rather than less. The antidote is the bound rather than more care: if the answer is not
below the smallest branch it is wrong, and you know that without re-reading a line of
your working.

**Stopping one reciprocal early.** You compute $1/2000 + 1/6000 = 0.000667$ and write
down 667 Ω. Tempting, because 0.000667 is a real number that took real work and 667 Ω
looks like a resistance. It is a conductance, in siemens, and the answer
is $1/0.000667 = 1500$ Ω. Writing the unit beside the number as you go is the cheapest
defence there is: you cannot hand in siemens to a question that asked for ohms if the
letter S is sitting there on the page.

**Calling two components parallel because they are drawn side by side**, or series
because they are drawn in a row. This one survives into professional life, because it
never feels like a guess — the drawing seems to be telling you. It is not. Run the two
tests on the wires, every time the layout is anything but a single straight chain.

## Worked: collapsing a chain, and checking it twice

A 9 V supply, a 470 Ω resistor, and two 1.0 kΩ resistors in parallel below it. Work
from the far end back towards the source, because it is the only part that is simple
yet.

```
the parallel pair - two equal resistors, so half of one:

    Rp      = (1000 * 1000) / (1000 + 1000)   = 500 ohm

the pair is now one resistor, in series with the 470:

    Rtot    = 470 + 500                       = 970 ohm

one application of Ohm's law, to the whole thing at once:

    I       = 9 / 970                         = 9.278 mA

that is the supply's current, and it is also the current in the 470,
because there is a single path from the supply down to the pair:

    V(470)  = 0.009278 * 470                  = 4.361 V
    V(pair) = 0.009278 * 500                  = 4.639 V
              ---------------------------------------
                                                9.000 V   KVL

the pair's 4.639 V sits across both branches, and across nothing else:

    I(each 1k) = 4.639 / 1000                 = 4.639 mA
    the two of them together                  = 9.278 mA  KCL
```

Two checks fell out of the last four lines for free: the drops add up to the supply, and
the branch currents add up to the supply current. Do both, every time. They cannot catch
a wrong idea about how the circuit is wired, but
they catch arithmetic, and arithmetic is what actually goes wrong.

## Worked: a ladder, and why the far end comes first

The second example has three levels rather than two, and its point is the order of
operations. A 12 V supply feeds $R_1 = 100$ Ω down to a node A. From A, $R_2 = 300$ Ω
runs to ground and $R_3 = 100$ Ω runs across to a second node B. From B, $R_4 = 400$ Ω
and $R_5 = 400$ Ω both run to ground.

You cannot start at $R_1$: it is in series with nothing until everything past node A has
become a single number, and everything past node A contains a node of its own. The only
part that is simple at the outset is the pair hanging off B.

```
work from the far end, because it is the only part that is simple yet:

    R4 || R5   = (400 * 400) / (400 + 400)     =  200 ohm

that pair is in series with R3, and the three become one branch:

    Rb         = 100 + 200                     =  300 ohm

that branch sits beside R2 - both run from node A to ground:

    Rp         = (300 * 300) / (300 + 300)     =  150 ohm

and R1 is in front of the lot:

    Rtot       = 100 + 150                     =  250 ohm
    I          = 12 / 250                      =  48.0 mA   out of the supply

now forwards again, filling in each voltage as it becomes available:

    drop(R1)   = 0.0480 * 100                  =  4.80 V
    node A     = 12 - 4.80                     =  7.20 V

    I(R2)      = 7.20 / 300                    =  24.0 mA
    I(branch)  = 7.20 / 300                    =  24.0 mA
                                                  --------
                                                  48.0 mA   KCL at A

    drop(R3)   = 0.0240 * 100                  =  2.40 V
    node B     = 7.20 - 2.40                   =  4.80 V

    I(R4)      = 4.80 / 400                    =  12.0 mA
    I(R5)      = 4.80 / 400                    =  12.0 mA
                                                  --------
                                                  24.0 mA   KCL at B
```

Two passes: inwards from the far end reducing, then outwards from the supply
distributing. Every reduction step on the way in is a step you undo on the way out, and
KCL closes at both nodes. So does the energy budget, which is the strongest check of
the three because it weights every branch by its own current and cannot be satisfied by
numbers that merely add up in the right places:

```
    supply     = 12 * 0.0480                   =  0.5760 W
    R1         = 0.0480^2 * 100                =  0.2304 W
    R2         = 0.0240^2 * 300                =  0.1728 W
    R3         = 0.0240^2 * 100                =  0.0576 W
    R4         = 0.0120^2 * 400                =  0.0576 W
    R5         = 0.0120^2 * 400                =  0.0576 W
                                                  --------
    the five resistors                         =  0.5760 W
```

Now the tempting wrong move, which the drawing invites.
$R_2$ and $R_3$ both leave node A, so surely they are in parallel? No: $R_2$'s other
end is ground, $R_3$'s other end is node B, and node B sits at 4.80 V rather than zero.
One shared end, not two. Take the shortcut anyway and you get $300\|100 = 75$ Ω, a
network that looks like $100 + 75 + 200 = 375$ Ω drawing $12/375 = 32$ mA — a third
below the truth, with nothing in the arithmetic to complain. Only the wiring test
catches that, which is why it belongs before the first multiplication.

## Where the rules stop

Not every network reduces. Draw four resistors as a diamond and a fifth across the
middle — a bridge — and no two are in series, because every junction has a third wire
leaving it, and no two are in parallel, because no pair shares both ends. The
combination rules have nothing whatever to say about it. What still applies is the pair
of laws the rules were built out of, which is the next reading, and
which module 7 turns into a routine that never needs reduction at all. (There is also a
repair: the delta-to-star transformation rewrites a triangle of three resistors as a
three-armed star that behaves identically at its terminals, which unjams a bridge. Worth
knowing the name for; not worth memorising the formula.)

The rules also assume the wire between the parts is not itself a part. "Same node"
means "same voltage, exactly", and real wire is a resistor too: 30 cm of 0.5 mm² copper
is about 10 mΩ, which is nothing beside a 1 kΩ resistor and is 50 mV when 5 A goes
through it. On a 12 V rail nobody cares. On the 1.2 V core rail of a processor, 50 mV
is four percent of the supply. Module 11 puts the wire back in.

And the rules combine *resistances*, which are single numbers only for components whose
current is proportional to their voltage. Two diodes in series do not have resistances
that add, because neither has a resistance at all until you say what current is
flowing. What survives is the layer underneath: series components share a current,
parallel components share a voltage. Those statements are about wiring, they never
mentioned Ohm's law, and they are what you reason with when the parts are diodes,
transistors or motors.
''',
                },
                {
                    "title": "Kirchhoff's two laws, and what each conserves",
                    "minutes": 18,
                    "body": r'''
Both rules in the last reading were derived rather than decreed, and both derivations
leaned on the same two statements. Those statements are Kirchhoff's laws. They are
worth stating on their own account, because they go on working where the combination
rules have nothing to say — and because every systematic method in the rest of this
course is one of the two laws, applied in a fixed order until the unknowns run out.

## KCL: charge has nowhere to pile up

**The currents arriving at any node add up to the currents leaving it.**

That is conservation of charge, stated locally. Charge being conserved overall is a law
of nature; the current law is the stronger claim that it is conserved *at every
junction separately*, and that needs the extra fact from the last reading — a node
cannot store any charge worth counting. A solder joint has perhaps a picofarad of
capacitance to the rest of the world, so holding even a nanocoulomb on it would take a
thousand volts. Below the frequencies this course works at, and most courses, a node
holds nothing at all.

So KCL is a sum that comes to zero. Pick a sign convention, apply it everywhere, and
then stop thinking about it. The usual one is **into the node counts positive**:

```
    +2.50 mA     in from the supply
    -1.20 mA     out down the first branch
    -0.75 mA     out down the second branch
    -0.55 mA     the branch you were solving for
    --------
     0.00 mA
```

The unknown came out negative, which says 0.55 mA leaves the node that way. A negative
current is not a mistake and does not need going back and fixing: it means the arrow you
drew points opposite to the flow, and every equation you wrote is still exactly right.
Guessing a direction wrongly costs nothing, which is the reason to guess quickly rather
than agonise.

## KCL is not really about points

The law is usually taught at a junction, but nothing in the argument needs the region to
be small. Draw a closed boundary anywhere you like — round two nodes, round a whole
sub-circuit, round the entire board — and the same reasoning applies: charge is not
accumulating inside the boundary, so the currents crossing into it must equal the
currents crossing out.

That generalisation earns its keep constantly. A board fed by a red wire and a black
wire must return on the black exactly what it took on the red, whatever is inside it,
which is why one meter in one lead measures the whole board's current. Two nodes can be
enclosed together and treated as one — the "supernode" module 7 uses to get past a
voltage source sitting between two unknowns. And a branch that goes nowhere carries
nothing: draw a boundary round the dangling end of an unconnected resistor, one wire
crosses it, so that current must be zero. Obvious until you meet it in a real network
and want a reason rather than a feeling.

## The mistake, and why it is tempting

**Current is used up as it goes round.** Almost everybody believes some version of this
at first, and it is a reasonable thing to believe. A bulb visibly consumes something, a
battery goes flat, and the phrase everyone uses is "power consumption". Something is
clearly being used up, so why not the current?

Because what is consumed is energy, not charge. Every electron that enters the bulb
leaves it — at a lower energy, having handed the difference to the filament. The symptom
is easy to spot in your own working: you expect less current after a resistor than
before it, in a loop with only one path. There is no such thing. One loop, one current,
everywhere in it, always.

The second mistake is quieter and does more damage. **Getting the node boundaries
wrong.** A node is not "a place where three wires meet" — it is *everything joined by
uninterrupted wire*, however far apart the pieces are drawn. Two points you took for
separate nodes turn out to be one, and the KCL equation you wrote for each is nonsense.
When a node analysis comes out wrong the algebra is rarely at fault; the node map
usually is. Number the nodes on the drawing before writing a single equation.

## KVL: a voltage belongs to a place, not to a route

**Round any closed loop, the voltage rises equal the voltage drops.**

That is conservation of energy, and the quickest way to see it is to remember what a
voltage is: the energy each coulomb gains or loses in going between two points. If every
point has a definite voltage — a definite energy per coulomb, whatever path you took to
arrive — then walking round a loop back to where you started must leave you where you
started. The net change is zero because the endpoints are the same point.

The analogy that helps is altitude. Every point on a hillside has a height, and that
height does not depend on how you walked to it, so any route back to your starting rock
has its ups and downs cancel exactly. Voltage is the electrical height, a resistor is a
slope you go down when current runs through it, and a battery is a lift that carries you
up. KVL says the obvious thing about hillsides, and it is exactly as hard to believe.

```
    +12.00 V     through the supply, a rise
     -3.30 V     across the first resistor
     -5.10 V     across the second
     -3.60 V     across the third
    ---------
      0.00 V
```

Trace the loop the other way round and every term changes sign, which changes nothing.
Trace a different loop through the same circuit and you get a different equation, just
as true.

Signs cause more trouble here than in KCL, and one habit removes almost all of it.
Choose a direction to walk the loop and stick to it. Mark the end of each resistor that
your assumed current *enters* with a plus. Then a component crossed from plus to minus
is a drop and enters the sum negative; minus to plus is a rise and enters positive. Do
not decide the sign by asking whether a component "gives" or "takes" energy — that is a
judgement, and judgements are where loops go wrong. Decide by which mark you met first.

## Worked: the laws and the rules on the same circuit

A 12 V supply feeds $R_1 = 1$ kΩ down into a node A. From A, $R_2 = 2$ kΩ and
$R_3 = 6$ kΩ both run to ground. What is the voltage at A?

Give the unknown a name, $V_a$, and write KCL at A: everything arriving through $R_1$
leaves through $R_2$ or $R_3$. Work in volts, milliamps and kilohms, which agree with
one another, so no factor of a thousand escapes.

```
        in              =            out
  (12 - Va) / 1         =      Va / 2   +   Va / 6

multiply every term by 6:

    6*(12 - Va)         =      3*Va     +   Va
       72 - 6*Va        =      4*Va
       72               =     10*Va
       Va               =      7.2 V
```

Now the same circuit by the combination rules, which had better agree:

```
  R2 || R3   = (2 * 6) / (2 + 6)    = 1.5 kohm
  total      = 1 + 1.5              = 2.5 kohm
  I(supply)  = 12 / 2.5             = 4.8 mA
  drop on R1 = 4.8 * 1              = 4.8 V
  Va         = 12 - 4.8             = 7.2 V     the same number
```

And KCL closes at A with numbers in it: $7.2/2 = 3.6$ mA and $7.2/6 = 1.2$ mA, which
add back to the 4.8 mA that arrived. KVL closes too, round the loop through $R_1$ and
$R_2$: $+12.0 - 4.8 - 7.2 = 0$. So does the energy budget, which is the check that
touches everything at once:

```
    supply   = 12.0 V * 4.80 mA          =  57.60 mW
    R1       = (4.80 mA)^2 * 1 kohm      =  23.04 mW
    R2       = (3.60 mA)^2 * 2 kohm      =  25.92 mW
    R3       = (1.20 mA)^2 * 6 kohm      =   8.64 mW
                                            --------
    the three resistors                  =  57.60 mW
```

## Worked: a circuit that does not reduce at all

The last example had two routes to the answer. This one has one, and that is the point
of it.

A 12 V supply feeds $R_1 = 2$ kΩ into node A. From A, $R_2 = 4$ kΩ runs to ground, and
$R_3 = 4$ kΩ runs across to the positive terminal of a fixed 4 V source whose negative
terminal is on the same ground. Two sources, one unknown node.

Nothing here reduces. $R_1$ and $R_3$ are not in series, because a third branch —
$R_2$ — leaves the node between them; $R_2$ is in parallel with nothing, because nothing
else runs from A to ground; and the two sources are not across the same pair of nodes,
so they cannot be combined either. Every technique from the previous reading is
unavailable. KCL is not.

Take every branch current as *leaving* A — a convention, not a prediction — and let the
signs sort themselves out:

```
  (Va - 12)/2   +   Va/4   +   (Va - 4)/4   =   0     volts, kilohms, milliamps

multiply every term by 4:

    2*(Va - 12)  +  Va  +  (Va - 4)   =  0
      2*Va - 24  +  Va  +   Va - 4    =  0
                             4*Va     =  28
                               Va     =  7.00 V
```

One equation, one unknown, and the whole circuit follows from it:

```
    I(R1)  =  (12 - 7.00) / 2   =  2.50 mA    into A from the 12 V supply
    I(R2)  =         7.00 / 4   =  1.75 mA    out of A, down to ground
    I(R3)  =  (7.00 - 4.00) / 4 =  0.75 mA    out of A, into the 4 V supply
                                    -------
    KCL at A:   2.50  =  1.75  +  0.75        closes
```

Look at what $R_3$ is doing. Node A sits at 7.00 V and the second supply at 4.00 V, so
current runs from A through $R_3$ *into* the 4 V source: that source is absorbing energy
rather than delivering it — being charged, if it is a battery. Had you assumed a source
must deliver and drawn the arrow the other way, you would have got $-0.75$ mA: the same
physical answer, from the same equation. That is what the sign convention exists for.

KVL confirms both loops. Up through the 12 V supply, along through $R_1$, down through
$R_2$ to ground: $+12.00 - 5.00 - 7.00 = 0$, where the 5.00 V is $2.50\ \text{mA}\times2\ \text{k}\Omega$.
Up through the 4 V supply, along through $R_3$ towards A — a *rise* of 3.00 V, because A
is the higher end — then down through $R_2$: $+4.00 + 3.00 - 7.00 = 0$.

The energy budget closes as well, with a term that would not exist in a one-source
circuit:

```
    12 V supply delivers   12.0 * 2.50 mA        =  30.00 mW
    R1                     (2.50 mA)^2 * 2 kohm  =  12.50 mW
    R2                     (1.75 mA)^2 * 4 kohm  =  12.25 mW
    R3                     (0.75 mA)^2 * 4 kohm  =   2.25 mW
    4 V supply absorbs     4.00 * 0.75 mA        =   3.00 mW
                                                    --------
    everything that takes energy                 =  30.00 mW
```

## How many equations you are entitled to

It is fair to worry whether writing the laws down will get you enough equations, or too
many. A circuit with $n$ nodes gives $n-1$ independent KCL equations — the last node's
is the sum of all the others and says nothing new — and $b$ branches across $n$ nodes
give $b - n + 1$ independent loops. Add them: $(n-1) + (b-n+1) = b$, exactly as many
equations as there are branch currents to find.

Count them on the circuit above. The nodes are ground, A, and the top of each supply, so
$n = 4$; the branches are two sources and three resistors, so $b = 5$. That is 3 KCL
equations and 2 KVL equations for 5 branch currents. The bookkeeping always works out,
which is why modules 7 and 8 can be routines rather than searches.

## Where the laws stop

Both laws have a boundary, and both boundaries are the same fact seen twice: the lumped
model assumes the circuit is small.

KVL fails when a changing magnetic field passes through the loop. "Every point has a
definite voltage" is then untrue, because the energy a coulomb picks up depends on the
path and not only on where it ended, and Faraday's law replaces the zero on the
right-hand side with the rate of change of flux through the loop. That is not an exotic
correction — it is what a transformer *is*. It is also why a scope probe with a long
ground lead shows ringing on a clean edge that shortens away when you shorten the lead:
the lead and the probe body enclose an area, something nearby is switching amps in
nanoseconds, and the loop is reading a voltage the circuit does not have.

KCL fails when a node can store charge, which needs the node to be large or the
frequencies high. A wavelength in air at 1 GHz is 30 cm and about half that on a circuit
board, so a 3 cm track no longer has one voltage along its length and calling it a node
is already a fiction. Push further and you get an antenna, where current flows into a
rod and apparently out of its far end into nothing. Charge is still conserved; the
return path is displacement current in the space around the rod, and the lumped model
has no symbol for it.

Past those boundaries the model is replaced by transmission-line theory first and
Maxwell's equations after that, neither of which is in this course. Everything here is
direct current, the extreme case of slow, and both laws hold exactly.

## Why you want both

The combination rules are far quicker where they apply. The laws apply everywhere. Put a
fifth resistor across the middle of a bridge and no amount of reducing will touch it,
but KCL at each node and KVL round each loop still yield as many independent equations
as there are unknowns. Turning that into a routine you can apply without thinking — one
equation per node — is module 7; one equation per loop is module 8.

One habit to start now, before either of those. Whichever route you took, check the
answer against the law you did not use. Found the node voltage by reduction? Add up the
branch currents and see that they come to the supply current. Found it by KCL? Walk one
loop and see that the drops come to the supply voltage. Then audit the power: every watt
the sources deliver has to be a watt something else takes. It costs ten seconds and
catches nearly everything.
''',
                },
            ],
            "quiz": {
                "title": "Combining resistors, and the two laws underneath",
                "minutes": 9,
                "questions": [
                    {
                        "q": "Two 10 kΩ resistors are connected in parallel. What is the resistance of the pair?",
                        "opts": ["20 kΩ", "10 kΩ", "5 kΩ", "0.1 kΩ"],
                        "a": 2,
                        "why": r'''
5 kΩ. Two equal resistors in parallel always give half of one, because you have
doubled the number of paths the current can take while leaving the voltage across each
path unchanged: twice the current for the same voltage is half the resistance.
Answering 20 kΩ is adding them, which is the *series* rule — that is the one mistake
worth drilling until it is impossible.
''',
                    },
                    {
                        "q": "A network already has some resistance. You add one more resistor in parallel with it. The total resistance:",
                        "opts": [
                            "always goes down",
                            "always goes up",
                            "stays the same",
                            "goes up or down depending on the size of the added resistor",
                        ],
                        "a": 0,
                        "why": r'''
Always down, no matter how large the added resistor is. You have given the current an
extra route without removing any of the existing ones, so for a fixed voltage more
current flows, which is by definition a lower resistance. A very large parallel
resistor lowers the total only slightly — but it does lower it. The mirror-image fact
is that a series resistor always raises the total.
''',
                    },
                    {
                        "q": "3.0 A flows into a node. Two of the three wires leaving it carry 1.2 A and 0.5 A. What does the third carry?",
                        "opts": ["1.3 A", "1.8 A", "4.7 A", "0.7 A"],
                        "a": 0,
                        "why": r'''
KCL: what goes in comes out, so $3.0 - 1.2 - 0.5 = 1.3$ A. The answer 1.8 A subtracts
only the first branch — it is worth writing the equation out in full rather than doing
it in your head, because nodes with four or five branches are ordinary. Charge cannot
accumulate at a junction; there is nowhere in a wire for it to sit.
''',
                    },
                    {
                        "q": "A 12 V supply drives three resistors in series. Two of them are measured to have 3 V and 5 V across them. What is across the third?",
                        "opts": ["12 V", "8 V", "4 V", "it depends on the resistor values"],
                        "a": 2,
                        "why": r'''
KVL: the three drops must add up to the 12 V rise the supply provides, so the third is
$12 - 3 - 5 = 4$ V. You do not need any resistor values — that is the power of KVL,
and it works round any loop you care to trace, in any circuit, always. (The values
would tell you *why* it split that way, which is the voltage divider in module 4.)
''',
                    },
                    {
                        "q": "A 100 Ω and a 10 Ω resistor are in series across a battery. Compare the current through the 10 Ω with the current through the 100 Ω.",
                        "opts": [
                            "ten times larger through the 10 Ω",
                            "exactly the same through both",
                            "ten times smaller through the 10 Ω",
                            "it depends on which one comes first in the loop",
                        ],
                        "a": 1,
                        "why": r'''
Identical. Series means there is a single path, and every electron that leaves one
resistor must enter the next — that is KCL applied to the node between them. What
differs is the *voltage* across each: ten times more across the 100 Ω, by Ohm's law.
Series shares current, parallel shares voltage, and confusing the two is the source of
most wrong answers in this module.
''',
                    },
                    {
                        "q": "You have a drawer containing only 4 kΩ resistors. Which combination gives exactly 6 kΩ?",
                        "opts": [
                            "two in series",
                            "two in parallel",
                            "one in series with two in parallel",
                            "three in parallel",
                        ],
                        "a": 2,
                        "why": r'''
Two in parallel give 2 kΩ, and putting one more in series with that pair adds 4 kΩ, for
6 kΩ in total. This is the exact network you are about to draw in the schematic
editor. For reference, the other options give 8 kΩ, 2 kΩ and 1.33 kΩ. Building an
awkward value out of identical parts is a genuine workshop skill, not just an exercise.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "Collapsing a network, one end at a time",
                    "minutes": 8,
                    "caption": "the far end first, then the chain, then Ohm's law once",
                    "lang": "text",
                    "brief": r'''
Reducing a network is not a single formula, it is an order of operations. Start at the
end furthest from the source, because that is the only part of the circuit that is
already simple enough to combine, and work back towards the supply one step at a time.

Nothing below needs Kirchhoff's laws written out. They are there anyway, in the two
lines at the bottom that check the answer.
''',
                    "listing": r'''
12 V across 1.5 kohm in series with (2.0 kohm || 6.0 kohm)
-----------------------------------------------------------

  the parallel pair first: nothing else can be combined until it
  is one number.

    1/Rp    =  1/2000 + 1/6000
            =  0.000500 + 0.000167
            =  0.000667 S           siemens - the conductance of the pair
    Rp      =  1 / 0.000667
            =  ___ ohm              below 2000, as a parallel pair must be

  the chain is now two resistors in a row, and those add

    Rtot    =  1500 + 1500          =  ___ ohm

  Ohm's law, applied once, to the whole thing

    I       =  12 / 3000            =  0.00400 A  =  4.00 mA

  KVL: the series 1.5 kohm takes I*R = 4.00 mA * 1.5 kohm = 6.00 V of
  the supply, so the node between the two halves sits at ___ V

  each branch of the pair has that voltage across it, and nothing else

    I(2.0k)   =  6.00 / 2000        =  3.00 mA
    I(6.0k)   =  6.00 / 6000        =  ___ mA
                                       --------
                                       4.00 mA   KCL closes at the node
''',
                    "blanks": [
                        {
                            "prompt": "2.0 kΩ and 6.0 kΩ in parallel. How many ohms?",
                            "hole": "?",
                            "opts": ["1500", "8000", "3000", "667"],
                            "a": 0,
                            "why": "$1/0.000667 \\approx 1500\\ \\Omega$, and the two-resistor "
                                   "shortcut gives it exactly: $(2000 \\times 6000)/8000 = 1500$. The "
                                   "value 8000 is the two resistances added, which is the series rule; "
                                   "667 is what you are left holding if you stop at the conductance, "
                                   "0.000667 S, and read its digits as ohms — the final reciprocal "
                                   "is the step that has gone missing. The check that catches all "
                                   "three: a parallel pair must come out below 2000, the smaller of "
                                   "the two.",
                        },
                        {
                            "prompt": "1500 Ω in series with the 1500 Ω pair. How many ohms?",
                            "hole": "?",
                            "opts": ["3000", "2250", "750", "1500"],
                            "a": 0,
                            "why": "In series they simply add: $1500 + 1500 = 3000\\ \\Omega$. The value "
                                   "750 is the two put in parallel again, which would be the right move "
                                   "if the second 1500 sat beside the first rather than after it. That "
                                   "distinction — beside or after — is the only thing that decides "
                                   "which rule applies, and it is a question about the drawing rather "
                                   "than about the numbers.",
                        },
                        {
                            "prompt": "12 V in, 6.00 V dropped across the series resistor. What is left at the node?",
                            "hole": "?",
                            "opts": ["6.00", "12.0", "18.0", "3.00"],
                            "a": 0,
                            "why": "KVL round the loop: $12 - 6 = 6$ V. Half the supply is dropped "
                                   "before the node because the two halves of the chain happen to be "
                                   "equal here, 1500 Ω above and 1500 Ω below. The value 18.0 comes "
                                   "from adding the drop instead of subtracting it, and it fails the "
                                   "cheapest sanity check there is: no node in a circuit driven by one "
                                   "12 V supply and containing only resistors can sit above 12 V.",
                        },
                        {
                            "prompt": "6.00 V across 6000 Ω. How many milliamps?",
                            "hole": "?",
                            "opts": ["1.00", "3.00", "0.36", "4.00"],
                            "a": 0,
                            "why": "$6.00/6000 = 0.00100$ A, or 1.00 mA — and it must be a third of the "
                                   "3.00 mA in the 2.0 kΩ, because the two have the same voltage across "
                                   "them and one has three times the resistance. Adding the two branch "
                                   "currents gives the 4.00 mA the supply delivers, which is KCL at "
                                   "that node and is the whole reason for writing the last three lines "
                                   "out.",
                        },
                    ],
                },
                {
                    "title": "The two laws, written out and then checked",
                    "minutes": 9,
                    "caption": "KCL at a named node, and the combination rules arriving at the same number",
                    "lang": "text",
                    "brief": r'''
The circuit below reduces perfectly well by the rules, so both routes are open. That is
the point: doing it both ways on a network simple enough to see through is how you
learn to trust the laws on a network that is not.

Naming the unknown node voltage and writing one equation for it is the method module 7
turns into a routine. Here it is by hand, once.
''',
                    "listing": r'''
a 10.0 V supply, one node, and three resistors
----------------------------------------------

  R1 = 1.2 kohm runs from the supply down to node A.
  R2 = 1.0 kohm and R3 = 4.0 kohm both run from A to ground.

  call the voltage at A "Va", and work in volts, milliamps and
  kilohms, so that no factor of a thousand can go missing.

    into A through R1        (10.0 - Va) / 1.2
    out of A through R2       Va / 1.0
    out of A through R3       Va / 4.0

  KCL at A says the one equals the other two:

    (10.0 - Va)/1.2   =   Va/1.0  +  Va/4.0

  multiply both sides by 12 and every fraction clears at once:

    10*(10.0 - Va)    =   12*Va  +  ___*Va
       100 - 10*Va    =   ___*Va
                 Va   =   4.00 V

  the combination rules have to agree, and do:

    R2 || R3    =  (1.0*4.0)/(1.0+4.0)   =  0.80 kohm
    total       =  1.2 + 0.80            =  2.00 kohm
    I(supply)   =  10.0 / 2.00           =  5.00 mA
    drop on R1  =  5.00 * 1.2            =  6.00 V
    Va          =  10.0 - 6.00           =  4.00 V

  KCL at A again, this time with numbers rather than symbols:

    I(R2)   =  4.00 / 1.0   =  4.00 mA
    I(R3)   =  4.00 / 4.0   =  ___ mA
                               ---------
                               5.00 mA

  and KVL round the loop that runs through R1 and R2 only:

    +10.0    -6.00    ___    =  0        volts, once round
''',
                    "blanks": [
                        {
                            "prompt": "$12 \\times \\dfrac{V_a}{4.0}$ is how many $V_a$?",
                            "hole": "?",
                            "opts": ["3", "4", "48", "0.25"],
                            "a": 0,
                            "why": "$12/4 = 3$, so that term is $3V_a$. Multiplying an equation through "
                                   "by the lowest common multiple of the denominators is worth doing "
                                   "before anything else: it removes every fraction in one move and "
                                   "leaves an equation you can rearrange without care. The value 48 is "
                                   "$12 \\times 4$, a multiplication where the 4 was in a denominator.",
                        },
                        {
                            "prompt": "$12V_a + 3V_a$ is how many $V_a$?",
                            "hole": "?",
                            "opts": ["15", "36", "9", "25"],
                            "a": 0,
                            "why": "$12 + 3 = 15$, so the right-hand side is $15V_a$ and the equation "
                                   "reads $100 - 10V_a = 15V_a$. Collecting the terms gives "
                                   "$100 = 25V_a$ and $V_a = 4.00$ V. The value 25 is that later total, "
                                   "after the $10V_a$ has been carried across from the left, so it is "
                                   "the right number one line too early.",
                        },
                        {
                            "prompt": "4.00 V across 4.0 kΩ. How many milliamps?",
                            "hole": "?",
                            "opts": ["1.00", "4.00", "16.0", "0.25"],
                            "a": 0,
                            "why": "$4.00/4.0 = 1.00$ mA, working in volts and kilohms so the answer "
                                   "lands in milliamps with nothing to convert. Together with the "
                                   "4.00 mA in the 1.0 kΩ that is 5.00 mA, exactly the supply current "
                                   "the reduction predicted — which is the point of computing it twice. "
                                   "The value 16.0 is $4.00 \\times 4.0$, Ohm's law used without being "
                                   "rearranged.",
                        },
                        {
                            "prompt": "The third term of the loop, signed, in volts.",
                            "hole": "?",
                            "opts": ["-4.00", "+4.00", "-10.0", "-16.0"],
                            "a": 0,
                            "why": "The loop is: up through the supply (+10.0), down through R1 "
                                   "(−6.00), down through R2 and back to the start. R2 has $V_a$ across "
                                   "it, which is 4.00 V, and the loop crosses it from + to −, so the "
                                   "term is −4.00 and the sum is zero. Writing +4.00 makes the loop sum "
                                   "12.0 V rather than nothing, which is the usual symptom of tracing "
                                   "one component in the opposite direction to the rest.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One rule, one number",
                    "minutes": 4,
                    "brief": r'''
The mechanical one, to get the rule under your fingers before anything is built on top
of it. Both resistors are wired between the supply's positive terminal and ground, so
both have the whole 12 V across them and neither has any say in what the other does.

There is exactly one trap here, and everybody falls into it once: resistors in parallel
do not add.
''',
                    "prompt": "What single resistance would the supply see in place of the pair?",
                    "note": "Give the answer in kilohms, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 1500},
                            {"id": "p2", "kind": "R", "x": 15, "y": 4, "rot": 1, "value": 3000},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 7},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [15, 3]},
                            {"a": [11, 5], "b": [15, 5]},
                            {"a": [13, 5], "b": [13, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "R1", "value": "1.50 k\u03a9"},
                        {"label": "R2", "value": "3.00 k\u03a9"},
                    ],
                    "aside": "Both resistors run between the same two nodes \u2014 the top rail and "
                             "ground \u2014 which is the whole definition of parallel. Neither of them "
                             "is the one the current reaches first.",
                    "answer": 1.0,
                    "tol": 0.02,
                    "unit": "k\u03a9",
                    # Nothing in the drawing is restated: the source's own value and the
                    # current the solver puts through it are both read back out of the solve,
                    # so a re-valued schematic is re-measured rather than compared to this one.
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
return src.value / Math.abs(d.currents[src.id]) / 1000;
''',
                    "hint": "Either $1/R = 1/1500 + 1/3000$, or the two-resistor shortcut "
                            "$R = R_1R_2/(R_1+R_2)$. They are the same statement.",
                    "wrong": "If you got 4.50, you added them \u2014 that is the series rule, and this "
                             "is not a series circuit. If you got 0.667, that is $1/R$ in units of "
                             "millisiemens: one more reciprocal to take.",
                    "why": r'''
$R = R_1R_2/(R_1+R_2) = (1500 \times 3000)/4500 = 1000\ \Omega$, or 1.00 kΩ. The long
way agrees: $1/1500 + 1/3000 = 0.000667 + 0.000333 = 0.001$ S, and the reciprocal of
that is 1000 Ω.

Two things are worth noticing before moving on. The first is that 1.00 kΩ is below
1.50 kΩ, the *smaller* of the two — as every parallel combination must be, because the
second resistor opens a path without closing one. The second is what the supply
actually does about it: $12/1500 = 8$ mA goes down one branch and $12/3000 = 4$ mA down
the other, 12 mA in total, and $12\ \text{V}/12\ \text{mA} = 1$ kΩ. The combination
rule is not a separate fact; it is that arithmetic, done once and remembered.
''',
                },
                {
                    "title": "The resistor whose marking has rubbed off",
                    "minutes": 5,
                    "brief": r'''
A missing component value, recovered from a measurement — which is most of what a
meter is for. Two resistors, one loop, nothing else.

No schematic for this one, because a schematic would have to print the value you are
being asked for.
''',
                    "prompt": "What is the resistance of the unmarked resistor?",
                    "note": "Give the answer in kilohms, to two decimal places.",
                    "figure": "A 9.00 V bench supply drives exactly two resistors, wired one after the "
                              "other in a single loop with nothing else in it. A meter in the loop "
                              "reads 1.50 mA. One of the two resistors is marked 2.20 k\u03a9; the "
                              "printing on the other has worn away.",
                    "given": [
                        {"label": "Supply", "value": "9.00 V"},
                        {"label": "Current in the loop", "value": "1.50 mA"},
                        {"label": "The resistor you can still read", "value": "2.20 k\u03a9"},
                    ],
                    "aside": "One loop means one current, so the meter reading belongs to both "
                             "resistors equally. That is KCL at the node between them, and it is the "
                             "only reason this question has an answer at all.",
                    "answer": 3.8,
                    "tol": 0.02,
                    "unit": "k\u03a9",
                    "hint": "The supply voltage and the loop current between them fix the resistance "
                            "of *everything in the loop*. Series resistances add, so the part you "
                            "cannot read is that total minus the part you can.",
                    "wrong": "If you got 6.00, that is the pair together and the 2.20 kΩ has not been "
                             "taken off it yet. If you got 5.70, that is the voltage across the "
                             "unmarked resistor in volts \u2014 correct, and one division short of an "
                             "answer.",
                    "why": r'''
One loop, one current, so Ohm's law applied to the whole loop gives the total:

```
Rtot = V / I  =  9.00 / 0.00150   = 6000 ohm
Rmiss = 6000 - 2200               = 3800 ohm   = 3.80 kohm
```

The other route uses KVL instead and lands in the same place. The marked resistor drops
$0.00150 \times 2200 = 3.30$ V, so the loop leaves $9.00 - 3.30 = 5.70$ V for the other
one, and $5.70/0.00150 = 3800\ \Omega$.

That the two routes agree is not luck. The series rule was *derived* from Kirchhoff's
two laws in the reading, so it cannot contradict them. What the longer route buys you
is a solution in the cases where the short one is unavailable, and those start as soon
as there is more than one loop.
''',
                },
                {
                    "title": "Three branches, and the one you were asked about",
                    "minutes": 7,
                    "brief": r'''
Now the network has two levels: one resistor carrying everything, and three sharing
what is left. The question asks about one of the three, and there is no way to it that
does not go through the whole circuit first.

The order matters. You cannot find a branch current until you know the voltage across
the branch, you cannot know that voltage until you know the drop across R1, and you
cannot know that drop until you know the current through it — which needs the three
parallel resistors reduced to one number.
''',
                    "prompt": "What current flows in R4, the 6.00 kΩ resistor?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 18},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 1000},
                            {"id": "p2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 2000},
                            {"id": "p3", "kind": "R", "x": 15, "y": 8, "rot": 1, "value": 3000},
                            {"id": "p4", "kind": "R", "x": 19, "y": 8, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 15, "y": 11},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 7], "b": [19, 7]},
                            {"a": [11, 9], "b": [19, 9]},
                            {"a": [15, 9], "b": [15, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "18.0 V"},
                        {"label": "R1, in series with the supply", "value": "1.00 k\u03a9"},
                        {"label": "R2", "value": "2.00 k\u03a9"},
                        {"label": "R3", "value": "3.00 k\u03a9"},
                        {"label": "R4", "value": "6.00 k\u03a9"},
                    ],
                    "aside": "R2, R3 and R4 all run from the same node to ground, so all three have "
                             "the same voltage across them. Find that one voltage and each branch is "
                             "a single division.",
                    "answer": 1.5,
                    "tol": 0.02,
                    "unit": "mA",
                    # The prompt names R4, so the check measures R4 — its drop and its value
                    # both taken out of the solve rather than restated from the drawing.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'p4'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1000;
''',
                    "hint": "Reduce the three parallel resistors to one number first. With R1 added "
                            "that gives the supply current; the supply current through R1 gives the "
                            "drop across it; and what the supply has left after that drop is the "
                            "voltage across all three branches at once.",
                    "wrong": "If you got 3.00, that is the current in R3. If you got 9.00, that is the "
                             "supply current \u2014 the total that then splits three ways. If you got "
                             "4.50, that is R2's share, the largest of the three, and R4 has the "
                             "largest resistance so it takes the smallest.",
                    "why": r'''
```
the three in parallel, in kilohms:

    1/Rp  =  1/2 + 1/3 + 1/6  =  3/6 + 2/6 + 1/6  =  1
    Rp    =  1.00 kohm

the chain the supply actually sees:

    Rtot  =  1.00 + 1.00                          =  2.00 kohm
    I     =  18.0 / 2.00                          =  9.00 mA

what R1 takes, and what is left for the branches:

    drop(R1) =  9.00 mA * 1.00 kohm               =  9.00 V
    node     =  18.0 - 9.00                       =  9.00 V

and 9.00 V across each branch in turn:

    I(R2) = 9.00 / 2 = 4.50 mA
    I(R3) = 9.00 / 3 = 3.00 mA
    I(R4) = 9.00 / 6 = 1.50 mA
                       -------
                       9.00 mA   which is the supply current, as KCL insists
```

1.50 mA. The last line is not decoration: it checks the answer with a law that took no
part in producing it, and it costs one addition.

Notice that the three parallel resistors came to 1.00 kΩ, below the 2.00 kΩ that was
already the smallest of them — three branches shrink a resistance harder than two do.
Notice also that R4, with three times R2's resistance, carries a third of R2's current.
Currents split in inverse proportion to resistance, which is module 5's subject and
which you have just worked out from nothing but Ohm's law and a shared voltage.
''',
                },
                {
                    "title": "The heat in the last resistor of the chain",
                    "minutes": 9,
                    "brief": r'''
Two branches this time, and one of them is itself two resistors in series. So the
reduction takes two steps rather than one, and the current you finally want is not the
supply's and not the one you meet first.

Power is asked for rather than a voltage or a current, which means one more step at the
end — and a choice about which form of the power law to use. Pick the form built from
the quantities you already have, not the one you happen to remember.
''',
                    "prompt": "How much power does R4 turn into heat?",
                    "note": "Give the answer in milliwatts, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 2000},
                            {"id": "p2", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 6000},
                            {"id": "p3", "kind": "R", "x": 17, "y": 7, "rot": 1, "value": 1000},
                            {"id": "p4", "kind": "R", "x": 17, "y": 10, "rot": 1, "value": 2000},
                            {"id": "g1", "kind": "GND", "x": 14, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 6]},
                            {"a": [11, 6], "b": [17, 6]},
                            {"a": [17, 8], "b": [17, 9]},
                            {"a": [11, 8], "b": [11, 12]},
                            {"a": [11, 12], "b": [17, 12]},
                            {"a": [17, 11], "b": [17, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "24.0 V"},
                        {"label": "R1, in series with the supply", "value": "2.00 k\u03a9"},
                        {"label": "R2, the left-hand branch", "value": "6.00 k\u03a9"},
                        {"label": "R3, upper half of the right-hand branch", "value": "1.00 k\u03a9"},
                        {"label": "R4, lower half of the right-hand branch", "value": "2.00 k\u03a9"},
                    ],
                    "aside": "R3 and R4 are in series with each other, and that pair is in parallel "
                             "with R2. Nothing at all is in parallel with R1.",
                    "answer": 32.0,
                    "tol": 0.3,
                    "unit": "mW",
                    # A power is not a node of this circuit, so the check takes the drop across
                    # R4 and R4's own value out of the solve and squares the one over the other.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'p4'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
return drop * drop / r.value * 1000;
''',
                    "hint": "Add R3 and R4 into one branch resistance; put that in parallel with R2; "
                            "add R1. That is what the supply sees. Work forwards from the supply "
                            "current to the node voltage, then back down the right-hand branch to the "
                            "current in it \u2014 and $P = I^2R$ with that current and R4's own "
                            "resistance.",
                    "wrong": "If you got 72.0, the node's 12 V has been put across R4 alone; R3 takes "
                             "4 V of it and only 8 V reaches R4. If you got 48.0, that is the whole "
                             "right-hand branch, R3 and R4 together. If you got 16.0, that is R3, "
                             "which carries the same current but has half the resistance.",
                    "why": r'''
```
the right-hand branch is two in a row, so they add:

    Rb    =  1.00 + 2.00                    =  3.00 kohm

that branch beside R2:

    Rp    =  (6.00 * 3.00) / (6.00 + 3.00)  =  2.00 kohm

and R1 in front of the pair:

    Rtot  =  2.00 + 2.00                    =  4.00 kohm
    I     =  24.0 / 4.00                    =  6.00 mA     out of the supply

forwards to the node, then back down the branch:

    drop(R1)  =  6.00 * 2.00                =  12.0 V
    node      =  24.0 - 12.0                =  12.0 V
    I(branch) =  12.0 / 3.00                =  4.00 mA
    I(R2)     =  12.0 / 6.00                =  2.00 mA
                                               -------
                                               6.00 mA     KCL at the node

and R4's own share of the heat:

    P(R4) = I^2 * R = (0.00400)^2 * 2000    =  0.0320 W    = 32.0 mW
```

32.0 mW. $P = I^2R$ was the form to reach for because the current is what the working
produced; $P = V^2/R$ gets there too, once you have noticed that R4 has
$4.00\ \text{mA} \times 2.00\ \text{k}\Omega = 8.00$ V across it rather than the node's
12.0 V.

Then audit the whole circuit, which is the habit this module is really trying to build.
R1 makes $0.006^2 \times 2000 = 72.0$ mW, R2 makes $0.002^2 \times 6000 = 24.0$ mW, R3
makes $0.004^2 \times 1000 = 16.0$ mW, and R4 makes 32.0 mW. Those come to 144 mW, and
the supply delivers $24.0\ \text{V} \times 6.00\ \text{mA} = 144$ mW. Energy is
conserved, so if your four resistors do not add up to what the supply is paying, one of
the numbers above them is wrong.
''',
                },
                {
                    "title": "How far up must the supply go?",
                    "minutes": 12,
                    "brief": r'''
The same shape of network, and the hardest version of the question. Everything you are
given is at the far end of the circuit from the thing you want, so the whole solution
runs backwards: a required *power* fixes a current, that current fixes a voltage, KCL
adds a second current to the first, and KVL carries the total back through R1 to the
supply.

The supply is adjustable and is drawn at its present setting, which is not the answer.
The answer is a number on the front panel — not a node voltage, not something you can
probe.

Read the required dissipation off the panel below, not off the drawing: the drawing
shows the circuit as it stands, and it does not yet meet the specification.
''',
                    "prompt": "What must the supply be set to so that R4 dissipates exactly 18.0 mW?",
                    "note": "Give the answer in volts, to one decimal place. Every resistance stays "
                            "where it is.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 1000},
                            {"id": "p2", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 6000},
                            {"id": "p3", "kind": "R", "x": 17, "y": 7, "rot": 1, "value": 1000},
                            {"id": "p4", "kind": "R", "x": 17, "y": 10, "rot": 1, "value": 2000},
                            {"id": "g1", "kind": "GND", "x": 14, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 6]},
                            {"a": [11, 6], "b": [17, 6]},
                            {"a": [17, 8], "b": [17, 9]},
                            {"a": [11, 8], "b": [11, 12]},
                            {"a": [11, 12], "b": [17, 12]},
                            {"a": [17, 11], "b": [17, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, at present", "value": "9.00 V, adjustable"},
                        {"label": "R1, in series with the supply", "value": "1.00 k\u03a9"},
                        {"label": "R2, the left-hand branch", "value": "6.00 k\u03a9"},
                        {"label": "R3, upper half of the right-hand branch", "value": "1.00 k\u03a9"},
                        {"label": "R4, lower half of the right-hand branch", "value": "2.00 k\u03a9"},
                        {"label": "Required dissipation in R4", "value": "18.0 mW"},
                    ],
                    "aside": "$P = I^2R$ run backwards is $I = \\sqrt{P/R}$, and that current belongs "
                             "to R3 as well, because R3 and R4 are in series. From there it is KCL at "
                             "the node and KVL through R1.",
                    "answer": 13.5,
                    "tol": 0.1,
                    "unit": "V",
                    # Solve the circuit as drawn, measure what R4 is ACTUALLY dissipating at that
                    # setting, and scale. Every resistance and the present setting come out of the
                    # solve; the only figure restated is the 18 mW, which is the question's
                    # specification rather than something printed on the drawing. Power goes as
                    # the square of the one source, so the scale factor is a square root.
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const r = c.net.parts.filter(function (p) { return p.id === 'p4'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
const now = drop * drop / r.value;
return src.value * Math.sqrt(0.018 / now);
''',
                    "hint": "Start at R4 and walk outwards. $I = \\sqrt{P/R}$ gives its current; that "
                            "current through R3 and R4 together gives the node voltage; the node "
                            "voltage across R2 gives the second branch current; KCL adds them; and "
                            "that total through R1 is the last drop to add on.",
                    "wrong": "If you got 9.00, that is the setting the circuit is drawn at, where R4 "
                             "is making 8.0 mW rather than 18.0. If you got 20.3, the supply was "
                             "scaled in proportion to the power \u2014 but power goes as the *square* "
                             "of the voltage, so the factor to apply is $\\sqrt{18.0/8.0} = 1.5$, not "
                             "$18.0/8.0$.",
                    "why": r'''
```
backwards from the specification:

    I(R4) = sqrt(P/R) = sqrt(0.0180 / 2000)  =  3.00 mA
                                                (and that is R3's current too)

up the branch to the node:

    Rb    = 1.00 + 2.00                      =  3.00 kohm
    node  = 3.00 mA * 3.00 kohm              =  9.00 V

across to the other branch, and KCL:

    I(R2) = 9.00 / 6.00                      =  1.50 mA
    I(R1) = 3.00 + 1.50                      =  4.50 mA

and KVL back through R1 to the supply:

    drop(R1) = 4.50 mA * 1.00 kohm           =  4.50 V
    supply   = 9.00 + 4.50                   =  13.5 V
```

Check it forwards, which is quicker than it looks. R2 beside the 3.00 kΩ branch is
$(6 \times 3)/9 = 2.00$ kΩ; with R1 that is 3.00 kΩ total; $13.5/3.00 = 4.50$ mA; the
node sits at $4.50 \times 2.00 = 9.00$ V; the branch takes $9.00/3.00 = 3.00$ mA; and
R4 dissipates $0.003^2 \times 2000 = 0.0180$ W. Exactly the 18.0 mW asked for.

There is a second route, and it is the one to remember. Every resistance is fixed, and
there is one source, so every current and every voltage in the circuit is *proportional*
to the supply setting — and every power is proportional to its square. Solve the circuit
once as drawn, at 9.00 V, and R4 comes out at 8.0 mW. To reach 18.0 mW you need the
powers multiplied by $18.0/8.0 = 2.25$, so the supply multiplied by $\sqrt{2.25} = 1.5$,
so $9.00 \times 1.5 = 13.5$ V. One solve and a square root instead of five steps.

That shortcut is worth being careful with. It works because the network is linear and
has exactly one source. Add a second source and it fails outright — scaling one of two
sources does not scale the answer — which is the crack that module 9 opens up into
superposition.
''',
                },
            ],
            "derive": {
                "title": "Both rules, out of both laws",
                "minutes": 12,
                "vars": ["R_1", "R_2", "R", "V", "I"],
                "brief": r'''
Nothing new is introduced below. Every line comes from Ohm's law, $V = IR$, plus one of
the two Kirchhoff laws — the current law for the parallel case, the voltage law for the
series one. The point of doing it symbolically is that the rules stop being two things
to memorise and become one thing to notice: *what do the two resistors have in common?*

Write each answer as an expression in the symbols named, with no numbers in it except
where a number is unavoidable.
''',
                "steps": [
                    {
                        "prompt": "Two resistors $R_1$ and $R_2$ sit in series, carrying the same current $I$ — KCL at the node between them leaves no alternative. Write the total voltage $V$ across the pair, in terms of $I$, $R_1$ and $R_2$.",
                        "answer": "I R_1 + I R_2",
                        "hint": "Ohm's law on each resistor separately, and KVL to say what the two drops come to.",
                        "deconstruct": [
                            "The first resistor has $IR_1$ across it and the second has $IR_2$.",
                            "KVL round the loop says the two drops together are the voltage across the pair.",
                        ],
                    },
                    {
                        "prompt": "Nothing outside the pair can tell it apart from a single resistor of $V/I$. Divide your last answer by $I$ and write that equivalent resistance in terms of $R_1$ and $R_2$.",
                        "answer": "R_1 + R_2",
                        "hint": "$I$ is a common factor of both terms, so it cancels with the one you are dividing by.",
                    },
                    {
                        "prompt": "Now wire the same two resistors in parallel, so that both have the same voltage $V$ across them. Write the total current $I$ that the pair draws, in terms of $V$, $R_1$ and $R_2$.",
                        "answer": "\\frac{V}{R_1}+\\frac{V}{R_2}",
                        "hint": "Ohm's law on each branch separately, and KCL to say what the two branch currents come to.",
                    },
                    {
                        "prompt": "Again the pair is indistinguishable from one resistor, this time of value $V/I$. Write that equivalent resistance in terms of $R_1$ and $R_2$, as a single fraction.",
                        "answer": "\\frac{R_1 R_2}{R_1 + R_2}",
                        "hint": "Take $V$ out as a common factor first. The bracket left behind is $\\frac{1}{R_1}+\\frac{1}{R_2}$, which is one fraction once you put it over a common denominator.",
                        "deconstruct": [
                            "$I = V\\left(\\frac{1}{R_1}+\\frac{1}{R_2}\\right) = V\\,\\frac{R_2+R_1}{R_1R_2}$.",
                            "So $V/I$ is the reciprocal of that bracket: $\\frac{R_1R_2}{R_1+R_2}$.",
                            "Note what was inverted and what was not \u2014 the *conductances* added, and the reciprocal was taken only at the end.",
                        ],
                    },
                    {
                        "prompt": "Three resistors, all of the same value $R$, all in parallel. Write the combined resistance in terms of $R$.",
                        "answer": "\\frac{R}{3}",
                        "hint": "Product over sum is a two-resistor shortcut and will not stretch to three. Add the three conductances instead: each is $1/R$.",
                        "deconstruct": [
                            "$1/R_p = 1/R + 1/R + 1/R = 3/R$.",
                            "So $R_p = R/3$, and $n$ equal resistors in parallel give $R/n$ by the same argument.",
                        ],
                    },
                    {
                        "prompt": "Finally the network you are about to build: one resistor of value $R$ in series with two more, also of value $R$, in parallel with each other. Write the total resistance in terms of $R$.",
                        "answer": "\\frac{3R}{2}",
                        "hint": "Do the parallel pair first \u2014 two equal resistors, so half of one \u2014 then add the series resistor to it.",
                        "deconstruct": [
                            "The pair is $R/2$ by the previous step with two branches instead of three.",
                            "In series with $R$ that is $R + R/2 = 3R/2$.",
                        ],
                    },
                ],
                "closing": r'''
Put the drawer of 4 kΩ resistors through the last result: $3 \times 4/2 = 6$ kΩ, which
is the value the build asks you to make and cannot buy. Seven values come out of a
single part number using no more than three of them — $R/3$, $R/2$, $2R/3$, $R$,
$3R/2$, $2R$ and $3R$ — and knowing which of them are reachable is a real workshop
skill rather than an exercise. ($2R/3$ is the awkward one: it is a single $R$ in
parallel with two more in series.)

Look back at the two derivations side by side. They are the same three moves in the same
order: say what the two resistors have in common, apply Ohm's law to each of them, and
apply the conservation law that the *other* quantity obeys. Series shares a current, so
KVL adds the voltages, so resistances add. Parallel shares a voltage, so KCL adds the
currents, so conductances add. There is one idea here, seen from two sides, and neither
side needs to be memorised once you can see which quantity is shared.

That symmetry is worth carrying forward, because it keeps paying. The next module
splits a voltage between two series resistors in proportion to their resistances; the
one after splits a current between two parallel resistors in inverse proportion. Same
two derivations, run one step further.
''',
            },
            "build": {
                "title": "Six kilohms from a drawer of four-kilohm resistors",
                "minutes": 25,
                "brief": r'''
You are given a 12 V supply and a stock room containing **4 kΩ resistors and nothing
else**. Build a network across that supply which

- draws exactly **2 mA** from the supply, and
- puts exactly **4 V** on the probe, measured between the probe's node and ground.

Every resistor you place must be 4 kΩ. That is the constraint that makes this
interesting: 6 kΩ is not in the drawer, so you have to make it.

## Where to start

The canvas opens with the supply, a ground, and one 4 kΩ resistor hanging from the
supply rail, with the probe on its lower end. Nothing flows yet, because that lower
end has no path to ground. Work out what has to go between the probe node and ground
so that the total is 6 kΩ, then draw it.

Think about the two numbers separately. 2 mA out of 12 V fixes the *total* resistance.
4 V at the probe fixes how that total splits between the part above the probe and the
part below it.

The checks measure the current and the probe voltage. Any arrangement of 4 kΩ parts
that produces both numbers passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [11, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                        {"id": "p4", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 4000},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 4000},
                        {"id": "p6", "kind": "GND", "x": 11, "y": 10},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [11, 7]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [13, 8]},
                        {"a": [9, 10], "b": [13, 10]},
                    ],
                },
                "checks": [
                    {"name": "every resistor came out of the 4 kΩ drawer", "code": r'''
const rs = c.values('R');
c.assert(rs.length >= 2,
  'One resistor cannot be both the series part and the parallel part. Found ' + rs.length + '.');
rs.forEach(function (r) {
  c.assert(Math.abs(r - 4000) <= 40,
    'Every resistor must be 4 kΩ — found one of ' + c.fmt(r, 'Ω') + '.');
});
'''},
                    {"name": "one 12 V supply drives the network", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
'''},
                    {"name": "the probe reads 4 V", "code": r'''
c.close(c.vout(), 4.0, 0.02,
  'the probe voltage — 8 V is dropped above it and 4 V below it');
'''},
                    {"name": "the supply delivers 2 mA, so the total is 6 kΩ", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
c.close(i, 0.002, 0.02, 'the current out of the supply');
'''},
                ],
                "hints": [
                    "12 V at 2 mA means the whole network is $12/0.002 = 6$ kΩ. You already have 4 kΩ of it in place.",
                    "So 2 kΩ has to sit between the probe node and ground — and 2 kΩ is what two 4 kΩ resistors give when they are in parallel.",
                    "In parallel means both ends joined: wire the tops of the two lower resistors together and to the probe node, and wire both bottoms together and to a ground symbol.",
                    "Check your work with the voltages before you run: 2 mA through the top 4 kΩ drops 8 V, leaving 4 V at the probe, and 2 mA through the 2 kΩ pair drops exactly that 4 V.",
                ],
            },
            "lab": {
                "title": "Combination rules and a missing current",
                "runtime": "python",
                "minutes": 24,
                "brief": r'''
Three small functions covering the whole of this module.

- `series(values)` returns the resistance of a list of resistors in series.
- `parallel(values)` returns the resistance of a list of resistors in parallel. Use
  the conductance form, $1/R = \sum 1/R_i$, so that it works for any number of them,
  not just two.
- `missing_current(into, out_of)` applies KCL at a node: given a list of the currents
  flowing **in** and a list of the currents known to flow **out**, return the current
  in the one remaining branch, taken as positive when it flows out of the node.

`sum()` will do most of the work. For `parallel`, a generator expression inside
`sum()` adds the reciprocals in one line.
''',
                "files": [{"name": "main.py", "content": r'''
"""Series, parallel, and Kirchhoff's current law."""


def series(values):
    """Total resistance of resistors carrying the same current."""
    # TODO: in series, resistances add.
    return 0.0


def parallel(values):
    """Total resistance of resistors sharing the same voltage."""
    # TODO: add the reciprocals, then take the reciprocal of the sum.
    return 0.0


def missing_current(into, out_of):
    """KCL: the current in the one branch not yet accounted for."""
    # TODO: everything that goes in must come out.
    return 0.0


if __name__ == "__main__":
    pair = parallel([4000.0, 4000.0])
    print("two 4k in parallel:", pair, "ohms")
    print("with another 4k in series:", series([4000.0, pair]), "ohms")
    print("third branch of the node:", missing_current([3.0], [1.2, 0.5]), "A")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Series, parallel, and Kirchhoff's current law."""


def series(values):
    """Total resistance of resistors carrying the same current."""
    return sum(values)


def parallel(values):
    """Total resistance of resistors sharing the same voltage."""
    return 1.0 / sum(1.0 / v for v in values)


def missing_current(into, out_of):
    """KCL: the current in the one branch not yet accounted for."""
    return sum(into) - sum(out_of)


if __name__ == "__main__":
    pair = parallel([4000.0, 4000.0])
    print("two 4k in parallel:", pair, "ohms")
    print("with another 4k in series:", series([4000.0, pair]), "ohms")
    print("third branch of the node:", missing_current([3.0], [1.2, 0.5]), "A")
'''}],
                "hints": [
                    "`series` is `sum(values)`.",
                    "`parallel` is `1.0 / sum(1.0 / v for v in values)`. Adding the reciprocals is adding the conductances.",
                    "`missing_current` is the total in minus the total out — a single subtraction of two sums.",
                    "A useful self-check: `parallel` must always return something smaller than the smallest resistor you gave it.",
                ],
                "tests": [
                    {"name": "series adds", "code": r'''
assert abs(series([4000.0, 4000.0]) - 8000.0) < 1e-9, "two 4k in series is 8k"
assert abs(series([1000.0, 2200.0, 470.0]) - 3670.0) < 1e-9, "1k + 2k2 + 470 is 3670"
'''},
                    {"name": "two equal resistors in parallel halve", "code": r'''
p = parallel([4000.0, 4000.0])
assert abs(p - 2000.0) < 1e-9, f"two 4k in parallel is 2k, got {p}"
'''},
                    {"name": "parallel works for three, and always shrinks", "code": r'''
p = parallel([1000.0, 2200.0, 470.0])
assert p < 470.0, f"a parallel total must be below the smallest part, got {p}"
assert abs(p - 279.1576673866091) < 1e-6, \
    f"1k, 2k2 and 470 in parallel is about 279.158 ohms, got {p}"
'''},
                    {"name": "the module 3 circuit comes out at 6 kilohms", "code": r'''
total = series([4000.0, parallel([4000.0, 4000.0])])
assert abs(total - 6000.0) < 1e-9, f"4k in series with 4k||4k is 6k, got {total}"
assert abs(12.0 / total - 0.002) < 1e-12, "12 V across 6k is 2 mA"
'''},
                    {"name": "KCL finds the missing branch", "code": r'''
i = missing_current([3.0], [1.2, 0.5])
assert abs(i - 1.3) < 1e-12, f"3.0 in, 1.7 accounted for, so 1.3 A left, got {i}"
j = missing_current([0.4, 0.25], [0.5])
assert abs(j - 0.15) < 1e-12, f"0.65 in, 0.5 out, so 0.15 A left, got {j}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "The voltage divider, loading and the power budget",
            "summary": "Two resistors in series split a supply in proportion — until something is connected across the output.",
            "concepts": [
                "Two resistors in series across a supply divide it in proportion to their resistances: $V_{out} = V_{in}\\,R_2/(R_1+R_2)$, with $R_2$ the one the output is taken across.",
                "The ratio depends only on the *ratio* of the two resistors. Scaling both by ten leaves the output alone and divides the current by ten.",
                "The divider formula assumes nothing is drawn from the output. Anything connected there sits in parallel with $R_2$ and pulls the output down.",
                "A *stiff* divider is one whose own current is much larger than the load current; the usual rule of thumb is at least ten times, and never less than twice.",
                "Stiffness costs heat. Every milliamp of divider current is a milliamp the supply pays for, whether a load uses it or not.",
                "Conservation of energy gives a free check on any solution: the power the supply delivers must equal the sum of the powers dissipated in every resistor.",
            ],
            "read": [
                {
                    "title": "Why two resistors split a supply in proportion",
                    "minutes": 17,
                    "body": r'''
A voltage divider is two resistors in a row across a supply, with the output taken from
the joint between them. That is the entire circuit, and there is nothing in it that was
not in the last module. What is new is that it is the first arrangement anyone actually
*designs* rather than merely analyses, and the first place where reaching for a formula
instead of the picture starts to cost you.

It is also, by a wide margin, the most-built circuit there is. Every volume control,
every battery-monitor input, every sensor whose 5 V output has to be shown to a 3.3 V
chip, every place where an approximate reference voltage is wanted and nothing precise
is at stake — all of them are this. Which is why a circuit you could already solve is
worth a reading of its own.

## The picture, before the formula

Forget for a moment that there are two components. A chain of resistance from the supply
down to ground is a chain of resistance; that it is sold as two parts with wire leads on
them is a manufacturing detail. Current has to get from the top of that chain to the
bottom, and all the way along it is being opposed.

Module 2 gave the geometry: $R = \rho L/A$, resistance in proportion to length. So a
uniform chain has its resistance spread evenly along it, and — since the same current is
pushing through every millimetre — the voltage is used up evenly along it too. A quarter
of the way down, a quarter of the supply has been spent. Touch a probe partway along and
you read whatever share of the supply the material *below* the probe still has to
account for.

That object is not a thought experiment. A potentiometer is exactly this: one track of
resistive material with a wiper sliding along it. Nothing switches and nothing steps; the
wiper voltage moves smoothly from zero to the full supply as the wiper travels, because
the fraction of the track between the wiper and the bottom moves smoothly from none of
it to all of it. A two-resistor divider is a potentiometer with the wiper soldered in one
place.

Hold on to that image. The formula below says precisely it, and someone carrying the
image cannot write the formula upside down.

## One current, and everything follows

Call the upper resistor $R_1$, the lower one $R_2$, and put $V_{in}$ across the pair.
The node between them has exactly two wires attached and nothing else, so — as long as
nothing is connected to the output — whatever current arrives through $R_1$ must leave
through $R_2$. One current, call it $I$, in both of them. That is KCL at a node with two
wires, and it is the whole derivation.

Ohm's law on the pair gives that current,

$$I = \frac{V_{in}}{R_1 + R_2}$$

and Ohm's law on the lower resistor alone gives the voltage you are measuring:

$$V_{out} = I R_2 = V_{in}\,\frac{R_2}{R_1 + R_2}$$

Read the fraction out loud as what it is: *the share of the total resistance that
belongs to the resistor you are measuring across*. A resistor holding a third of the
resistance holds a third of the voltage, because it is holding a third of the
opposition to one shared current. Put that way nothing needs memorising, and it is also
how you avoid the classic error — putting $R_1$ on top because it happens to be written
first.

Two checks that cost nothing and catch nearly everything:

- $V_{out}$ must land between 0 V and $V_{in}$. Two resistors cannot make voltage.
- $V_{out}$ must be the *larger* half when $R_2$ is the larger resistor, and the smaller
  half when it is not.

## Worked: 15 V down to something a sensor can read

A 15 V rail, and an input that must not see much more than 5 V. Try 6.8 kΩ on top and
3.3 kΩ at the bottom — both ordinary stock values.

```text
the two are in series, so they add:

    Rtot   =  6800 + 3300                    =  10100 ohm

one current, from Ohm's law on the whole chain at once:

    I      =  15 / 10100                     =  1.4851 mA

and that same current through each resistor in turn:

    V(R1)  =  1.4851 mA * 6800 ohm           =  10.099 V
    V(R2)  =  1.4851 mA * 3300 ohm           =   4.901 V
              -----------------------------------------
                                                15.000 V   KVL closes

the ratio route, in one line, and it had better agree:

    Vout   =  15 * 3300 / 10100              =   4.901 V
```

4.90 V. The two routes are the same arithmetic in a different order, and doing both on
the first few dividers you meet is how the ratio stops being a formula you trust and
becomes one you could rebuild if you forgot it.

## Worked: the same rule run backwards, which is what design is

Reading a divider takes one line. Choosing one takes three, because there are two
requirements instead of one. Say a 12.0 V rail has to give a 2.50 V reference, and the
whole thing may draw no more than 100 µA.

The ratio settles the voltage. The *size* of the chain settles the current, and nothing
about the ratio has any bearing on it. So take the two requirements one at a time, in
that order:

```text
the ratio the divider has to hit:

    Vout / Vin  =  2.50 / 12.0                    =  0.20833

the current budget fixes how big the chain must be:

    Rtot        =  12.0 / 100e-6                  =  120 kohm   (at least)

and now the ratio splits that total between the two parts:

    R2          =  0.20833 * 120000               =  25.0 kohm
    R1          =  120000 - 25000                 =  95.0 kohm
```

Neither number is a resistor anybody sells. The nearest E96 parts — the 1% series — are
24.9 kΩ and 95.3 kΩ, so fit those and find out what you actually built:

```text
    Rtot   =  95300 + 24900                       =  120.2 kohm
    I      =  12.0 / 120200                       =  99.834 uA    inside the budget

    V(R1)  =  99.834 uA * 95300 ohm               =   9.514 V
    V(R2)  =  99.834 uA * 24900 ohm               =   2.486 V
              --------------------------------------------------
                                                     12.000 V

and the powers, which had better come to what the supply hands over:

    P(R1)  =  (99.834 uA)^2 * 95300 ohm           =  0.9498 mW
    P(R2)  =  (99.834 uA)^2 * 24900 ohm           =  0.2482 mW
              --------------------------------------------------
                                                     1.1980 mW

    P(sup) =  12.0 V * 99.834 uA                  =  1.1980 mW   agrees
```

2.486 V where 2.500 V was asked for: 0.57% low, and 99.8 µA against a 100 µA budget.
Both requirements met, and the error comes from the stock values rather than from the
method.

Before chasing that 0.57%, notice what tolerance does to it. Those parts are ±1%, and
the worst corner is $R_1$ reading low while $R_2$ reads high, because both of those
push the output up. The sensitivity works out at $R_1/(R_1+R_2) = 0.793$ per unit of
error in *each* part, so the two together move the output by $2 \times 0.793 = 1.59$
times the part tolerance — 1.6% here, which is 2.446 V to 2.525 V. The stock-value
error is a third of the tolerance error, and a divider built from 1% parts is a ±1.6%
reference whatever values you pick. Chasing the last half percent with exotic values
buys nothing; module 11 is where that argument gets made properly.

## More than two: one chain, several taps

Nothing in the derivation cared that there were two resistors. Any number of them in a
row still share one current, so each still takes the share of the supply that matches
its share of the resistance — and so does any *stretch* of the chain.

A 9.00 V rail across 1.00 kΩ, then 3.30 kΩ, then 4.70 kΩ down to ground:

```text
    Rtot     =  1.00 + 3.30 + 4.70                =  9.00 kohm
    I        =  9.00 / 9000                       =  1.000 mA

each resistor's drop, from that one current:

    V(1.0k)  =  1.000 mA * 1000                   =  1.00 V
    V(3.3k)  =  1.000 mA * 3300                   =  3.30 V
    V(4.7k)  =  1.000 mA * 4700                   =  4.70 V
               ----------------------------------------------
                                                     9.00 V

the taps, read from the ground end upwards:

    lower tap  (top of the 4.7k)                  =  4.70 V
    upper tap  (top of the 3.3k)  = 4.70 + 3.30   =  8.00 V
```

Read those two taps against each other rather than against ground and the difference is
3.30 V, which is $9.00 \times 3300/9000$ — the same rule applied to the stretch between
them. That is the general statement worth carrying: **the voltage across any stretch of
a series chain is the supply times that stretch's resistance over the total.** Two
resistors is only the smallest case.

## The ratio is all that matters — and it is not all that matters

Scale both resistors by the same factor and the fraction $R_2/(R_1+R_2)$ does not move.
68 kΩ over 33 kΩ gives 4.901 V from that same 15 V rail, and so does 680 Ω over 330 Ω.
Measuring the output tells you nothing whatever about which pair is fitted.

Everything else tells you immediately. The current is $V_{in}/(R_1+R_2)$, so it scales
as $1/R$, and the power the supply hands over scales with it:

```text
    6.8k / 3.3k    ->  1.485 mA   ->  15 V * 1.485 mA  =   22.3 mW
     68k /  33k    ->  148.5 uA   ->                       2.23 mW
    680  / 330     ->  14.85 mA   ->                        223 mW
```

Three circuits with identical outputs and a hundredfold spread in what they cost to run.
That power is not optional and it is not occasional: it is drawn continuously, whether
or not anything is using the output, for as long as the supply is connected. Suppose the
15 V comes from a pack holding 5 Wh. The 680/330 divider alone empties it in
$5/0.223 = 22$ hours; the 6.8 k/3.3 k version takes 9.3 days; the 68 k/33 k version,
93 days. Same output, three products.

So there are two design decisions and they are independent. The **ratio** fixes the
voltage. The **scale** fixes the current, and therefore the heat, and therefore the
battery life. Two knobs, and that is the entire design space — which is what makes the
divider easy, and also what makes it limited.

## The mistakes, and why each one is tempting

**Putting the wrong resistor on top of the fraction.** Everybody does this, and usually
under time pressure. It is tempting because $R_1$ is written first, and because the
formula gets remembered as a *shape* — a resistor over a sum — rather than as a
sentence. The repair is the sentence: the resistor you are measuring across goes on top.
The catch is the second sanity check above: with 6.8 kΩ and 3.3 kΩ, the answer must be
below half of 15 V, so 10.1 V is not a candidate and needs no further thought.

**Believing the divider *makes* a voltage.** A meter on that tap shows 4.90 V, rock
steady, for as long as you care to watch, and it is very hard not to read that as a
4.90 V source. It is not one. Two resistors cannot make voltage; they can only decline
to use some of it. Two consequences follow immediately and both bite in practice: the
output can never exceed the rail, and it *tracks* the rail exactly. Let that 15 V sag to
14 V and the tap goes to $14 \times 3300/10100 = 4.574$ V. A 6.7% rail error is a 6.7%
reference error, in proportion, always. The third consequence — what happens when you
connect something — is the next reading.

**Designing the ratio and forgetting the scale.** Tempting because the ratio is the part
the question asks about, and the scale is the part nobody mentions. It is how a battery
product ends up with the 680/330 divider above quietly drawing 14.9 mA around the clock,
or with a 10 MΩ divider so feeble that the board's surface leakage moves it.

## Where the ratio stops being the answer

Four places, and the first is the reason for the next reading.

Every line above rested on the words *as long as nothing is connected to the output*.
That was not a modelling nicety to be waved away. The derivation needed the two
resistors to carry the same current, and the instant anything is attached to the output
node they do not.

Second, the parts have to be resistors. Put an LED where $R_2$ is and there is no ratio
at all, because the LED has no fixed resistance — it has a curve, and its "resistance"
is whatever the operating point makes it. What survives is the layer underneath: one
current through both, KVL round the loop, and the device's own curve in place of Ohm's
law for it. That is a real calculation, and it is not this one.

Third, a divider is not a regulator. It tracks its rail, it has no idea what voltage it
is producing, and it cannot correct anything. Where a genuine reference is needed —
2.500 V that stays 2.500 V while the battery falls from 12 V to 9 V — a divider is the
wrong component and a reference IC is the right one.

Fourth, at the extreme top end the resistors stop being the only paths. A 10 MΩ chain
sits in parallel with the leakage across a dusty board and the input current of whatever
is reading it, and both of those are then part of the circuit whether you drew them or
not. That is the same failure as the first one wearing a disguise, which is what the
next reading is about.
''',
                },
                {
                    "title": "What a load does to it, and what a stiff divider costs",
                    "minutes": 18,
                    "body": r'''
A divider with nothing on its output is a laboratory object. In a real circuit something
is connected — that is what the output is *for* — and the moment it is, the last
reading's derivation stops applying.

## What actually broke

Go back to the one sentence the whole thing rested on: the node between the resistors has
two wires attached, so what arrives leaves. Connect something to that node and it has
three. The current arriving down $R_1$ now splits, and KCL at the tap says

$$I_1 = I_2 + I_L$$

with $I_2$ down the lower resistor and $I_L$ into whatever you attached. Three different
currents in a circuit that had one. Every step after that first sentence — the single
$I$, the series sum, the ratio — was built on the two-wire node, so every step after it
has to be rebuilt.

That is the shape of most errors in circuit work. The formula did not stop being true;
the *situation the formula describes* stopped being the situation in front of you. The
formula has no way of telling you that.

## The load is in parallel with the lower resistor

Rebuilding it is short. Whatever you attach runs from the output node to ground. So does
$R_2$. Both ends of one are joined to both ends of the other, which is the parallel test
from module 3, passed on both pairs of ends. The bottom half of the divider is therefore
not $R_2$; it is

$$X = \frac{R_2 R_L}{R_2 + R_L}$$

and with that single number in place of $R_2$ the tap once again has two things attached
and the circuit is once again an ordinary two-resistor divider, of $R_1$ over $X$. That
substitution is the only new idea in the module; the rest is arithmetic you already have.

It also gives you the direction of the answer before any arithmetic. A parallel pair is
always smaller than either of its parts, so $X < R_2$. The bottom of the divider has
shrunk and the top has not, so **the output always falls**. Never rises. A calculation
that says a load raised a divider's output has an error in it, and no digit needs
checking to know so.

## How far it falls, in one number

Substituting and simplifying gives something more useful than a bigger formula. Start
from $V_{out} = V_{in}X/(R_1+X)$, put $X = R_2R_L/(R_2+R_L)$ in, and multiply top and
bottom by $(R_2+R_L)$:

$$V_{out} = \frac{V_{in}R_2R_L}{R_1R_2 + R_1R_L + R_2R_L}$$

which is correct and tells you nothing. Divide top and bottom by $(R_1+R_2)$ instead and
the same expression sorts itself into two factors:

$$V_{out} = \left(V_{in}\frac{R_2}{R_1+R_2}\right) \times
\frac{R_L}{R_L + R_1\!\parallel\!R_2}$$

The bracket is the unloaded output the last reading derived, untouched. Everything the
load does is in the second factor — and read what that factor is. It is *itself* a
voltage divider, between the load and a resistance of $R_1\parallel R_2$, and that
resistance is the only property of the divider it contains. Two resistors, one number:
whatever else $R_1$ and $R_2$ are doing, the amount a load pulls the output down depends
on them only through their parallel combination.

Call that number $R_{out}$. It is what the load is arguing with, and it is what "stiff"
means: a divider is stiff when $R_{out}$ is small beside the load, because then the sag
factor is close to one. The rest of this reading is a consequence of that one fraction.

## Worked: a 3.3 V tap that does not work, and then does

A 5 V rail, and a sensor that wants 3.30 V and behaves like 47 kΩ to ground.

Design it as though the sensor were not there. The ratio wanted is $3.3/5 = 0.66$, so
$R_1 = R_2 \times 0.34/0.66$: take $R_2 = 33$ kΩ, $R_1 = 17$ kΩ. Now connect the sensor:

```text
    X      =  (33k * 47k) / (33k + 47k)      =  19.39 kohm
    Vout   =  5 * 19.39 / (17 + 19.39)       =   2.66 V

the sag factor gets there in two lines and says why:

    Rout   =  (17k * 33k) / (17k + 33k)      =  11.22 kohm
    Vout   =  3.30 * 47 / (47 + 11.22)       =   2.66 V
```

2.66 V where 3.30 V was wanted. Twenty percent low, from a load that is not even a heavy
one — 47 kΩ is a high-impedance input by most standards. It went wrong because
$R_{out} = 11.2$ kΩ is a quarter of the load rather than a tenth of it. Two ways out.

**Make the divider stiffer.** Divide both resistors by ten: 1.7 kΩ and 3.3 kΩ. The ratio
has not moved, so the unloaded output is still 3.30 V, but $R_{out}$ has fallen to
1.122 kΩ and the sag factor to $47/48.122 = 0.9767$. Another factor of ten takes
$R_{out}$ to 112.2 Ω. Here are the three, with the load connected and every watt counted:

```text
    R1      R2      Rout      Vout       I(supply)    P(supply)   P(load)   to load
    ------  ------  --------  ---------  -----------  ----------  --------  -------
    17 k    33 k    11.22 k   2.664 V     137.4 uA    0.687 mW    0.151 mW   22.0 %
    1.7 k   3.3 k   1.122 k   3.223 V    1045.3 uA    5.226 mW    0.221 mW    4.2 %
    170     330     112.2     3.292 V   10046.2 uA   50.23  mW    0.231 mW    0.5 %
```

That table is the bargain, laid out. Every factor of ten buys one more decimal place of
accuracy and costs a factor of ten in current, and the share of the energy actually
reaching the load falls the whole way down the column — because the load's own
consumption barely changes while the divider's grows tenfold each time. Stiffness is
bought with heat, at a fixed and rather poor exchange rate.

**Or put the load into the design.** It is not an intruder; it is a known component with
a known value. Fix the current budget first — say 1 mA from the 5 V rail, so a 5 kΩ
chain — and work backwards:

```text
    X       =  0.66 * 5000                          =  3300 ohm
    R1      =  5000 - 3300                          =  1700 ohm

    X is R2 beside the known 47k load, so undo the parallel:

    1/R2    =  1/3300 - 1/47000                     =  0.00028175 S
    R2      =  1 / 0.00028175                       =  3549 ohm

    check it forwards:

    (3549 * 47000) / (3549 + 47000)                 =  3300 ohm
    5 * 3300 / 5000                                 =  3.300 V
```

Exactly 3.300 V, *with the load connected*, on 1.000 mA — slightly less than the
1.045 mA the second row of the table spends to reach only 3.223 V. Designing with the
load in costs nothing and is simply better. This is the calculation the build asks for,
and the only version that survives a soldering iron.

## Stiffness, and the rule of thumb

The usual rule: the divider's own current should be at least ten times the load current,
and never less than twice. In the design just made, the load draws
$3.3/47\text{k} = 70\,\mu$A while $R_2$ carries $3.3/3549 = 930\,\mu$A — thirteen to one,
comfortably stiff.

The rule is a heuristic, not a law, and the sag factor is what it stands in for. Ten to
one puts $R_{out}$ at a tenth of $R_L$ or below and so holds the sag under ten percent;
two to one puts it near a third and the sag near a quarter. If you know what error you
can accept, work backwards from the fraction instead and ignore the rule.

Now look at what stiffness bought, in full:

```text
    supply current     =  5 / 5000                 =  1.000 mA
    supply power       =  5 V * 1.000 mA           =  5.000 mW

    P(R1)   =  (1.000 mA)^2 * 1700                 =  1.700 mW
    P(R2)   =  3.300^2 / 3549                      =  3.068 mW
    P(load) =  3.300^2 / 47000                     =  0.232 mW
               ------------------------------------------
                                                      5.000 mW
```

Under five percent of the energy reaches the load; the rest heats two resistors whose
only job is to be stiff. Notice the last line too: the three dissipations add up to
what the supply delivers, to the last digit. They must — there is nowhere else for the
energy to go — and checking costs one addition.

## Worked: the specification that cannot be met

The second worked example is one where the arithmetic works and the design still fails —
the case the rule of thumb exists to catch.

A 12.0 V rail. A 2.500 V tap wanted, feeding something that behaves like 100 kΩ. The
product sleeps most of its life, so the rail may give up no more than 60 µA. Work it
through in the order the last section set out:

```text
    the load's own draw, at 2.5 V:   2.5 / 100k         =  25.0 uA
    so the chain may take:           60 - 25            =  35.0 uA
    total resistance from the rail:  12.0 / 60e-6       =  200 kohm
    the ratio, as always:            2.5 / 12.0         =  0.208333

    X       =  0.208333 * 200000                        =  41.667 kohm
    R1      =  200000 - 41667                           =  158.33 kohm

    undo the parallel to get the part you fit:

    1/R2    =  1/41667 - 1/100000  =  2.4e-5 - 1e-5     =  1.4e-5 S
    R2      =  1 / 1.4e-5                               =  71.43 kohm

    check forwards:

    X       =  (71430 * 100000) / 171430                =  41.667 kohm
    Vout    =  12.0 * 41.667 / 200.0                    =  2.500 V
```

2.500 V exactly, 60 µA exactly. Every stated requirement met. Now check the stiffness the
requirements forgot to ask for: $R_2$ carries 35 µA against the load's 25 µA, a ratio of
1.4 — below even the "never less than twice" floor. What does that cost?

Suppose the load is not a resistor but a circuit that draws less when it idles, so its
effective resistance doubles to 200 kΩ:

```text
    X       =  (71430 * 200000) / 271430                =  52.632 kohm
    Vout    =  12.0 * 52.632 / (158.33 + 52.632)        =  2.994 V
```

The reference has moved from 2.500 V to 2.994 V — 20% — because the thing it is
referencing went quiet. Nothing was miscalculated. The design met its specification and
is useless, and the sag factor said so in advance: $R_{out} = 158.33 \parallel 71.43 =
49.2$ kΩ against a 100 kΩ load is a sag factor of 0.67, and a factor that far from one is
a factor that moves when the load does.

Something has to give, and there are only three candidates. **Spend the current:** ten
to one wants 250 µA in the chain and 275 µA from the rail — four and a half times the
budget — for $R_1 = 34.5$ kΩ and $R_2 = 10.0$ kΩ, and that design holds the tap at
2.59 V when the load idles instead of letting it go to 2.99 V. Or **buffer the tap**,
with a unity-gain op-amp whose input draws nanoamps; the divider then has no load worth
the name and a 1.2 MΩ chain at 10 µA does the job. Or **stop using a divider** and fit a
reference IC, which holds its output whatever is hung on it. Which is right is an
engineering judgement — but only one you can make once the sag factor is written down.

## The mistakes, and why each one is tempting

**Designing unloaded and bolting the load on afterwards.** The commonest by a distance.
It is tempting because the divider formula is the thing you have just learned, the load
is somebody else's component, and the two feel like separate problems. They are one
problem. The load is in the circuit; put it in the calculation.

**Trusting the meter.** A meter is a load. A 1 MΩ over 1 MΩ divider on a 10 V rail should
sit at 5.000 V; clip a 10 MΩ voltmeter across the lower resistor and $R_{out} = 500$ kΩ
against a 10 MΩ load gives a sag factor of $10/10.5 = 0.952$, so it reads 4.762 V. The
meter is not faulty and the circuit is not faulty; the reading is of a circuit that only
exists while the meter is attached. It is tempting to miss because measurement feels
passive, and it is why oscilloscope probes are 10 MΩ and print the value on the barrel.

**Reading "ten times" as a law.** It is a heuristic that encodes a few percent of sag.
Some jobs tolerate 20% and some need 0.1%, and both are answered by the sag factor
rather than by the rule.

**Assuming stiffer is better.** Stiffer is more accurate and more expensive, and past
some point it is the expense that ends the project.

## Where the divider stops

A divider's output depends on its load, and no choice of $R_1$ and $R_2$ makes it not.
Stiffness only makes the dependence small, and pays for that in heat that grows the same
way. Four boundaries follow.

**Loads that change.** If the load varies while the circuit runs — a sensor waking up, a
relay pulling in — the tap moves with it, exactly as in the worked example, and nothing
inside the divider can hold it.

**Loads that are not resistances.** A transistor base or an LED has no $R_L$ to put in
the formula. What survives is KCL at the tap: the current down $R_1$ still equals the
current down $R_2$ plus the current into the device, and the device's own curve replaces
Ohm's law for it. That is a solvable problem and it is not this formula.

**Anything that needs real current.** Suppose a 12 V rail has to run a 5 V device that
draws 20 mA — so the device looks like 250 Ω. A stiff divider needs ten times that
current of its own: $R_2 = 5/200\text{ mA} = 25\,\Omega$, $R_1 = 7/220\text{ mA} =
31.8\,\Omega$, and 220 mA out of the rail. That is $12 \times 0.220 = 2.64$ W burned to
deliver $5 \times 0.020 = 0.10$ W — under 4% — with 1.54 W in $R_1$ and 1.00 W in $R_2$,
which are large parts that run hot. This is why dividers set reference voltages and bias
meter inputs and essentially never supply power; a regulator, which throws away voltage
without throwing away current, is the component for that job.

**The idea underneath outgrows the circuit.** Looking back into its output terminals, a
divider behaves exactly like a source of $V_{in}R_2/(R_1+R_2)$ behind a resistance of
$R_1 \parallel R_2$ — which is what the sag factor was telling you, since a real source
with a series resistance divides with its load in precisely that way. Module 6 meets the
same two numbers sealed inside a battery, where they are called the open-circuit voltage
and the internal resistance. Module 10 gives them their proper names and proves the
remarkable part: *every* two-terminal network of sources and resistors, however
complicated, is one voltage and one resistance to anything connected across it. The
divider is simply the smallest example, and the sag factor derived above is a special
case of a theorem you have not met yet.
''',
                },
            ],
            "tune": {
                "title": "Deliver 3.30 V, and pay under a milliamp for it",
                "minutes": 9,
                "brief": r"""
Reading a divider is arithmetic. *Designing* one is the first time two requirements
pull against each other: the ratio fixes what fraction of the rail you get, and
nothing about the ratio fixes the current — that is set by how large the two
resistors are together. Halve both and the output voltage does not move a millivolt
while the current doubles.

Two knobs, two constraints, and they are not independent.
""",
                "prompt": "Deliver 3.30 V from a 5 V rail \u2014 and draw under 1 mA doing it.",
                "note": "The dashed line is your target. Both constraints must hold at once.",
                "model": "divider",
                "initial": {"r1": 2200, "r2": 2200},
                "constants": {"vin": 5},
                "plotKey": "vout",
                "constraints": [
                    {"k": "vout", "label": "Vout = 3.30 V \u00b1 0.03", "eq": 3.30, "tol": 0.03},
                    {"k": "i", "label": "I \u2264 1.00 mA", "max": 1.0},
                ],
            },
            "sandbox": {
                "title": "A ratio, read as a gain",
                "visualiser": "bode",
                "minutes": 7,
                "initial": {"wn": 60, "zeta": 0.9, "K": 0.5},
                "brief": r'''
A divider does one thing: it multiplies its input by a fixed number smaller than one.
Engineers usually quote that number as a **gain**, and often in **decibels**, where a
gain $G$ is written as $20\log_{10}G$ dB.

The top plot here is gain in decibels; the bottom is a phase shift, which for a
resistive divider is always zero. The horizontal axis is frequency, which does not
appear anywhere in this course — a network of resistors alone behaves identically at
every frequency, so a resistive divider is the perfectly **flat** left-hand part of
this picture and nothing else. The curved right-hand part arrives in EE102, when
capacitors join in.

The slider $K$ is the gain. Leave the other two alone at first.
''',
                "notice": [
                    "$K$ opens at 0.5 — a divider that halves its input — and the flat left-hand part of the top plot sits at −6 dB. Those are two ways of saying the same thing.",
                    "Take $K$ down to 0.1 and the flat part drops to −20 dB. Every further factor of ten in the ratio costs another 20 dB, which is the whole reason decibels are used.",
                    "The bottom plot starts at 0° on the far left and stays within a few degrees of it out to about $\\omega = 3$: there the output rises and falls in step with the input, simply smaller, which is all a resistive divider ever does. Read further right and the phase bends away long before the gain visibly does — at $\\omega = 20$ the top plot still looks flat while the phase has already reached −34°.",
                    "Drag the corner $\\omega_n$ to its maximum, 200, and the flat region covers most of the plot. A purely resistive divider is the limit where the corner has gone off to infinity and only the flat part is left.",
                ],
            },
            "quiz": {
                "title": "Dividers under load",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A 9 V supply feeds 20 kΩ in series with 10 kΩ, with the output taken across the 10 kΩ. With nothing connected to the output, what is it?",
                        "opts": ["6 V", "3 V", "4.5 V", "0.3 V"],
                        "a": 1,
                        "why": r'''
$V_{out} = 9 \times 10/(20+10) = 3$ V. The 10 kΩ is one third of the total 30 kΩ, so it
gets one third of the supply. Answering 6 V means using the *upper* resistor on top of
the fraction — always put the resistance you are measuring across on top, and sanity
check the result: the output must land between 0 V and the supply, and closer to
whichever resistor is larger.
''',
                    },
                    {
                        "q": "You replace that divider's 20 kΩ and 10 kΩ with 200 kΩ and 100 kΩ. With nothing connected to the output, what changes?",
                        "opts": [
                            "the output is still 3 V, and the current falls to a tenth",
                            "the output falls to 0.3 V",
                            "the output rises to 30 V",
                            "nothing at all changes",
                        ],
                        "a": 0,
                        "why": r'''
The output depends only on the ratio, which is unchanged, so it is still 3 V. What
changes is the current: 0.3 mA becomes 0.03 mA, and the power wasted in the divider
falls by the same factor of ten. That is not a free lunch, though — the higher the
resistances, the more the output sags when a load is connected, which is the next
question.
''',
                    },
                    {
                        "q": "A divider is set up to give 3 V. You then connect a load resistor across the output, equal in value to the lower resistor. What happens to the output?",
                        "opts": [
                            "it stays at 3 V, because the divider sets the voltage",
                            "it falls, because the load is in parallel with the lower resistor",
                            "it rises, because there is now more current",
                            "it falls to zero",
                        ],
                        "a": 1,
                        "why": r'''
It falls. The load sits in parallel with the lower resistor, and a parallel pair is
always smaller than either part — here half of the lower resistor. The divider now
splits its supply between the upper resistor and a *smaller* lower one, so the output
drops. This is the single most common surprise in practical work: a divider that
measures perfectly with a meter on it collapses the moment something real is attached.
''',
                    },
                    {
                        "q": "In an unloaded divider of 20 kΩ on top and 10 kΩ below, which resistor dissipates more power?",
                        "opts": [
                            "the 10 kΩ, because more current flows through it",
                            "the 20 kΩ",
                            "the same, because they are in series",
                            "it depends on the supply voltage",
                        ],
                        "a": 1,
                        "why": r'''
They carry the same current, being in series, so $P = I^2R$ makes the larger resistance
the hotter one — twice as hot here. Choosing the 10 kΩ because more current flows through it misreads series for
parallel: the current through both is identical, which is exactly why $I^2R$ is the right form to reach for.
''',
                    },
                    {
                        "q": "A 9 V supply drives a divider drawing 0.3 mA, and the two resistors dissipate 1.8 mW and 0.9 mW. What must the supply be delivering?",
                        "opts": ["0.9 mW", "1.8 mW", "2.7 mW", "it cannot be worked out from this"],
                        "a": 2,
                        "why": r'''
2.7 mW, and there are two ways to see it. Directly: $P = VI = 9 \times 0.0003$. By
conservation: energy cannot go anywhere except into those two resistors, so the two
dissipations must add up to what the supply provides. Whenever those two numbers
disagree in your own work, there is an arithmetic error somewhere — it is the cheapest
check in circuit analysis, and it is the one the capstone is built around.
''',
                    },
                ],
            },
            "build": {
                "title": "A 3 V rail that survives its load",
                "minutes": 28,
                "brief": r'''
A 9 V battery has to supply a sensor that needs **3.00 V** and behaves, electrically,
exactly like a 100 kΩ resistor to ground. The battery is small, so the whole circuit
may draw no more than **500 µA**.

The canvas opens with the battery, the 100 kΩ load already in place, the grounds, and
a probe on the load. Add the two divider resistors so that

- the probe reads 3.00 V **with the load connected**,
- the supply delivers between 90 µA and 500 µA.

The lower bound is a design rule rather than a law. At 3.00 V the load itself takes
$3/100\text{k} = 30$ µA, and a divider carrying less than about twice its load current
sags badly when the load changes — so the divider wants 60 µA of its own, and the
supply, which carries the divider current *and* the load current, wants 90 µA. The
upper bound is the battery.

## The trap

Designing this as though the load were not there gives 20 kΩ over 10 kΩ — and measures
2.81 V, which fails. The load is in parallel with your lower resistor, and the two of
them together are what forms the bottom half of the divider. Work out what the *pair*
must come to, then work out what the lower resistor has to be so that the pair comes
to that.

Values need not be round numbers. Type them as you like — `11.1k` is understood, and
so is `11111`.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 100000},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p7", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 8], "b": [13, 8]},
                        {"a": [13, 10], "b": [13, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 20000},
                        {"id": "p3", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 11111.111111111111},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 100000},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p7", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [13, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [13, 10], "b": [13, 11]},
                    ],
                },
                "checks": [
                    {"name": "the 100 kΩ load is still across the output", "code": r'''
const rs = c.values('R');
c.assert(rs.some(function (r) { return Math.abs(r - 100000) <= 1000; }),
  'The 100 kΩ load is the problem, not an obstacle — leave it in the circuit.');
c.assert(rs.length >= 3,
  'A divider is two resistors, and with the load that makes at least three. Found ' + rs.length + '.');
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 1000 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'The 100 kΩ load must run from the probed node to ground — a load left dangling ' +
   'is no load at all, and the whole point of this exercise is what happens when it is there.');
'''},
                    {"name": "one 9 V battery drives it", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 9, 0.001, 'the supply voltage');
'''},
                    {"name": "the load sees 3.00 V", "code": r'''
c.close(c.vout(), 3.0, 0.02,
  'the voltage at the load — remember the load is in parallel with your lower resistor');
'''},
                    {"name": "the battery gives between 90 µA and 500 µA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
/* both bounds carry a rounding allowance, so a design sitting exactly on one of
   them is not failed by the last decimal place of a resistor value */
c.assert(i <= 500e-6 * 1.005,
  'The battery may not be asked for more than 500 µA; this circuit draws ' + c.fmt(i, 'A') + '.');
c.assert(i >= 90e-6 * 0.99,
  'The load takes 30 µA and the divider should carry at least twice that on its own, ' +
  'so the supply must deliver at least 90 µA; this circuit draws ' + c.fmt(i, 'A') + '.');
'''},
                ],
                "hints": [
                    "Call the parallel combination of your lower resistor and the 100 kΩ load $X$. The circuit is then an ordinary two-resistor divider of $R_{top}$ and $X$.",
                    "For 3 V out of 9 V, $X$ must be one third of the total, which means $R_{top} = 2X$.",
                    "Pick $X$ first from the current budget: the supply current is $9/(R_{top}+X) = 9/(3X)$, so $X = 10$ kΩ gives 300 µA, comfortably inside both limits.",
                    "Then solve $1/X = 1/R_{low} + 1/100\\text{k}$ for $R_{low}$. With $X = 10$ kΩ it comes to about 11.1 kΩ, and $R_{top}$ is 20 kΩ.",
                ],
            },
            "numeric": [
                {
                    "title": "What voltage appears at Vout?",
                    "minutes": 5,
                    "brief": r'''
The mechanical one first, to get the rule under your fingers. The number below falls out
of a single idea: with nothing drawing current from the output node, the *same* current
flows through both resistors, so they share the supply in proportion to their resistance.
''',
                    "prompt": "What voltage appears at Vout?",
                    "note": "No load on the output node. Two decimal places is plenty.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 2200},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 7},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 9]},
                            {"a": [11, 7], "b": [15, 7]},
                            {"a": [11, 11], "b": [11, 13]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "5.00 V"},
                        {"label": "R1 (top)", "value": "1.00 k\u03a9"},
                        {"label": "R2 (bottom)", "value": "2.20 k\u03a9"},
                        {"label": "Load", "value": "none"},
                    ],
                    "aside": "Nothing draws current from Vout, so the same current flows through both "
                             "resistors \u2014 which is the only reason the ratio rule is allowed.",
                    "answer": 3.4375,
                    "tol": 0.02,
                    "unit": "V",
                    # The prompt asks for the probed node and nothing else, so the check is
                    # the probed node and nothing else.
                    "check": "return c.vout();",
                    "hint": "The current through the pair is $5/(R_1+R_2)$. Vout is that current "
                            "through $R_2$ alone \u2014 which rearranges to $5 \\cdot R_2/(R_1+R_2)$.",
                    "wrong": "Check which resistor ends up on top of the fraction: Vout is measured "
                             "across the BOTTOM resistor, so it is $R_2$ over the sum, not $R_1$.",
                    "why": "$5 \\times 2200/3200 = 3.4375$ V. Notice it is nearer the supply than to "
                           "ground, because the larger resistor is the one you are measuring across "
                           "\u2014 more of the total voltage is dropped where there is more "
                           "resistance to drop it. Swapping the two resistors would give 1.5625 V, "
                           "and the two answers sum to the supply, as they must.",
                },
                {
                    "title": "The resistor that has not been fitted yet",
                    "minutes": 6,
                    "brief": r'''
The same rule, run backwards. You are given the supply, the output you want and one of
the two resistors, and asked for the other — which is what designing a divider actually
consists of, and which is one rearrangement away from the question before it.

No schematic for this one, because a schematic would have to print the value you are
being asked for.
''',
                    "prompt": "What must the upper resistor be?",
                    "note": "Give the answer in kilohms, to one decimal place.",
                    "figure": "A 24.0 V rail feeds two resistors in series down to ground. A logic "
                              "input sits on the joint between them and draws no current worth "
                              "speaking of. The lower resistor is already fitted and marked "
                              "3.30 k\u03a9; the upper one is an empty pair of pads, and has to be "
                              "chosen so that the joint sits at 3.60 V.",
                    "given": [
                        {"label": "Supply", "value": "24.0 V"},
                        {"label": "Lower resistor, fitted", "value": "3.30 k\u03a9"},
                        {"label": "Wanted at the joint", "value": "3.60 V"},
                        {"label": "Load on the joint", "value": "none worth counting"},
                    ],
                    "aside": "The output's share of the supply and the lower resistor's share of the "
                             "total resistance are the same number. Work that number out first and "
                             "the rest is subtraction.",
                    "answer": 18.7,
                    "tol": 0.05,
                    "unit": "k\u03a9",
                    "hint": "$3.60/24.0 = 0.150$, so the 3.30 k\u03a9 must be 15.0% of the whole "
                            "chain. That fixes the chain, and the upper resistor is what is left of "
                            "it.",
                    "wrong": "If you got 22.0, that is the whole chain and the 3.30 k\u03a9 has not "
                             "been taken off it yet. If you got 20.4, that is the voltage the upper "
                             "resistor has to drop, in volts, and it is one division short of an "
                             "answer. If you got 0.58, the two resistors have swapped places in the "
                             "fraction: 582 \u03a9 on top of 3.30 k\u03a9 would put 20.4 V on the "
                             "joint, not 3.60 \u2014 which is the *other* resistor's share, and the "
                             "reason for always checking that the answer sits on the right side of "
                             "half the supply.",
                    "why": r'''
```
the ratio the divider has to hit:

    Vout / Vin  =  3.60 / 24.0                =  0.150

so the fitted resistor is 15.0% of the chain, which fixes the chain:

    Rtot        =  3300 / 0.150               =  22000 ohm
    Rupper      =  22000 - 3300               =  18700 ohm  =  18.7 kohm
```

The current route lands in the same place and is worth doing once. The lower resistor
has 3.60 V across it, so the chain carries $3.60/3300 = 1.0909$ mA; the upper resistor
has to drop the other $24.0 - 3.60 = 20.4$ V at that current, so it is
$20.4/0.0010909 = 18700\,\Omega$.

18.7 kΩ is a real E48 value, which is luck rather than design. Had it come out at, say,
18.4 kΩ you would fit the nearest stock part and accept the error: 18 kΩ gives
$24 \times 3.3/21.3 = 3.72$ V, which is 3% high and may or may not matter. Deciding
whether it matters is what module 11 is about.
''',
                },
                {
                    "title": "The current in the resistor the load landed on",
                    "minutes": 8,
                    "brief": r'''
A load now, and a question about neither the output voltage nor the supply current. The
tap feeds three things at once: the lower divider resistor, the load, and nothing else —
so the current arriving down the top resistor splits there, and the question is about
one of the two halves.

Two steps, in this order. The load is in parallel with the lower resistor, so combine
them first and read the tap voltage off the divider that leaves. Then come back to the
lower resistor on its own.
''',
                    "prompt": "How much current flows in R2, the 6.00 k\u03a9 lower divider resistor?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 2000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                            {"id": "rl", "kind": "R", "x": 17, "y": 10, "rot": 1, "value": 3000},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 9]},
                            {"a": [11, 7], "b": [17, 7]},
                            {"a": [17, 7], "b": [17, 9]},
                            {"a": [11, 11], "b": [11, 13]},
                            {"a": [17, 11], "b": [17, 13]},
                            {"a": [14, 7], "b": [14, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "9.00 V"},
                        {"label": "R1, from the supply to the tap", "value": "2.00 k\u03a9"},
                        {"label": "R2, from the tap to ground", "value": "6.00 k\u03a9"},
                        {"label": "Load, also from the tap to ground", "value": "3.00 k\u03a9"},
                    ],
                    "aside": "R2 and the load run between the same two nodes, so they are in "
                             "parallel and share the tap voltage. Neither of them carries the "
                             "supply current.",
                    "answer": 0.75,
                    "tol": 0.02,
                    "unit": "mA",
                    # The prompt names R2, so the check measures R2: its drop and its value both
                    # come out of the solve rather than being restated from the drawing.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r2'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1000;
''',
                    "hint": "Combine R2 and the load into one resistance first. That turns the whole "
                            "thing back into a two-resistor divider and gives you the tap voltage; "
                            "R2's own current is then that voltage divided by 6.00 k\u03a9.",
                    "wrong": "If you got 2.25, that is the supply current \u2014 the total that "
                             "splits at the tap. If you got 1.50, that is the load's share of it. If "
                             "you got 1.13, the load has been ignored: an unloaded divider would sit "
                             "at 6.75 V and put 1.125 mA through R2, and the whole point of this "
                             "module is that it does not.",
                    "why": r'''
```
the load is in parallel with R2, so the bottom half is not 6.00 k:

    X      =  (6000 * 3000) / 9000            =  2.00 kohm

which leaves 2.00 k over 2.00 k - a divider that simply halves:

    Vout   =  9 * 2.00 / 4.00                 =  4.50 V

and the question is about R2 alone, which has that 4.50 V across it:

    I(R2)  =  4.50 / 6000                     =  0.750 mA

the other two currents, as a check that costs nothing:

    I(load)  =  4.50 / 3000                   =  1.500 mA
    I(supply)=  9 / 4000                      =  2.250 mA
                -------------------------------------------
                0.750 + 1.500                 =  2.250 mA   KCL at the tap
```

0.75 mA. Three currents in one small circuit and they are all different, which is
exactly the thing to take away: the supply current, the divider's own current and the
load current are three separate numbers, and a question that says "the current" without
saying which one is not yet a question.

Note what the load has done to the design. Unloaded, this divider would sit at
$9 \times 6/8 = 6.75$ V; loaded, it sits at 4.50 V. It lost a third of its output to a
load that is half the size of the resistor it landed across — which is roughly the
worst case, and roughly what "not stiff" means in numbers.
''',
                },
                {
                    "title": "Set the supply so the middle resistor makes exactly 12.5 mW",
                    "minutes": 12,
                    "brief": r'''
The full-sized version. Three resistors in a chain this time, with the load hanging on
the lower tap, and an adjustable supply that is drawn at its present setting rather than
at the answer.

Everything given is at the far end of the circuit from the thing wanted, so the solution
runs backwards: a required *power* fixes a current, that current is the whole chain's
current, and one application of Ohm's law to the whole chain gives the setting. The
quantity you are asked for is not a node voltage and cannot be probed — it is a
number on the front panel of the supply.

Read the required dissipation off the panel below, not off the drawing. The drawing
shows the circuit as it stands, and as it stands it does not meet the specification.
''',
                    "prompt": "What must the adjustable supply be set to so that R2 dissipates exactly 12.5 mW?",
                    "note": "Give the answer in volts, to one decimal place. Every resistance stays "
                            "where it is.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 9, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 12},
                            {"id": "r1", "kind": "R", "x": 11, "y": 3, "rot": 1, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 2000},
                            {"id": "r3", "kind": "R", "x": 11, "y": 11, "rot": 1, "value": 3000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 14},
                            {"id": "rl", "kind": "R", "x": 17, "y": 11, "rot": 1, "value": 6000},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 14},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 7},
                        ],
                        "wires": [
                            {"a": [3, 10], "b": [3, 12]},
                            {"a": [3, 8], "b": [3, 2]},
                            {"a": [3, 2], "b": [11, 2]},
                            {"a": [11, 4], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 10]},
                            {"a": [11, 9], "b": [17, 9]},
                            {"a": [17, 9], "b": [17, 10]},
                            {"a": [11, 12], "b": [11, 14]},
                            {"a": [17, 12], "b": [17, 14]},
                            {"a": [14, 9], "b": [14, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, at present", "value": "10.0 V, adjustable"},
                        {"label": "R1, nearest the supply", "value": "1.00 k\u03a9"},
                        {"label": "R2, the middle of the chain", "value": "2.00 k\u03a9"},
                        {"label": "R3, from the lower tap to ground", "value": "3.00 k\u03a9"},
                        {"label": "Load, also on the lower tap", "value": "6.00 k\u03a9"},
                        {"label": "Required dissipation in R2", "value": "12.5 mW"},
                    ],
                    "aside": "Only R3 has the load beside it. Replace that pair with one number and "
                             "R1, R2 and the pair are a single chain carrying a single current \u2014 "
                             "and that current is R2's.",
                    "answer": 12.5,
                    "tol": 0.1,
                    "unit": "V",
                    # Solve the circuit as drawn, measure what R2 is ACTUALLY dissipating at the
                    # setting shown, and scale. Every resistance and the present setting come out
                    # of the solve; the only figure restated is the 12.5 mW, which is the
                    # question's specification rather than something printed on the drawing.
                    # One source and a linear network, so every voltage scales with the setting
                    # and every power with its square \u2014 hence the square root.
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const r = c.net.parts.filter(function (p) { return p.id === 'r2'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
const now = drop * drop / r.value;
return src.value * Math.sqrt(0.0125 / now);
''',
                    "hint": "Reduce R3 and the load to one resistance and the circuit becomes a "
                            "single loop. Then $P = I^2R$ run backwards, $I = \\sqrt{P/R}$, gives "
                            "the current R2 needs \u2014 and that is the current everywhere in the "
                            "chain.",
                    "wrong": "If you got 10.0, that is the setting the supply is drawn at, where R2 "
                             "is making 8.00 mW rather than 12.5. If you got 15.0, the load was left "
                             "out and the chain taken as $1+2+3 = 6.00$ k\u03a9 \u2014 the load is "
                             "in parallel with R3 and drags that 3.00 k\u03a9 down to 2.00 k\u03a9. "
                             "If you got 15.6, the supply has been scaled in proportion to the power "
                             "\u2014 but power goes as the *square* of the setting, so the factor is "
                             "$\\sqrt{12.5/8.00} = 1.25$, not $12.5/8.00$.",
                    "why": r'''
```
the load first: it is in parallel with R3 and touches nothing else

    X      =  (3000 * 6000) / 9000              =  2.00 kohm

R1, R2 and X are now one chain, so one current, and it is R2's current

    Rtot   =  1.00 + 2.00 + 2.00                =  5.00 kohm

what R2 needs, from P = I^2 R run backwards

    I      =  sqrt(0.0125 / 2000)               =  2.50 mA

and Ohm's law once, applied to the whole chain

    Vsup   =  2.50 mA * 5.00 kohm               =  12.5 V
```

Forwards, as a check: at 12.5 V the chain carries $12.5/5000 = 2.50$ mA, the upper tap
sits at $12.5 - 2.50\,\text{mA} \times 1\,\text{k} = 10.0$ V, the lower tap at
$2.50\,\text{mA} \times 2.00\,\text{k} = 5.00$ V, and R2 dissipates
$0.0025^2 \times 2000 = 12.5$ mW. The lower tap's 5.00 V splits as 1.67 mA down R3 and
0.83 mA into the load, which is 2.50 mA back again.

There is a second route and it is the one to remember. Every resistance is fixed and
there is exactly one source, so every current in this circuit is *proportional* to the
setting and every power to its square. Solve it once as drawn, at 10.0 V, and R2 comes
out at 8.00 mW. To reach 12.5 mW the powers must be multiplied by 1.5625, so the setting
by $\sqrt{1.5625} = 1.25$, so $10.0 \times 1.25 = 12.5$ V. One solve and a square root
instead of four steps.

That shortcut is worth being careful with. It holds because the network is linear and
has one source; add a second and it fails outright, because scaling one of two sources
does not scale the answer. That crack is what module 9 opens up into superposition.
''',
                },
            ],
            "blanks": {
                "title": "The divider's power budget, line by line",
                "minutes": 9,
                "caption": "one loaded divider, and every milliwatt accounted for",
                "lang": "text",
                "brief": r'''
Nothing new below — the same loaded divider as before, carried through to the end.
What is new is the last two lines, where the three dissipations are added up and
compared with what the supply is handing over. They must agree. There is nowhere else
in the circuit for energy to go, and when they do not agree it is arithmetic rather
than physics that has failed.

Fill in the six holes in order; each one is one step from the ones above it.
''',
                "listing": r'''
12 V, then R1 = 3.0 kohm down to the tap, then R2 = 6.0 kohm from the
tap to ground.  A 3.0 kohm load, RL, hangs on the tap as well.
--------------------------------------------------------------------

  the load sits in parallel with R2, so the bottom half of the divider
  is not 6.0 kohm any more

    X      =  (6000 * 3000) / (6000 + 3000)
           =  ___ kohm           below 3.0 k, as a parallel pair must be

  from here it is an ordinary two-resistor divider, 3.0 kohm over X

    Rtot   =  3.0 kohm + X
    Vout   =  12 * X / Rtot                        =  ___ V

  one chain above the tap, so one current, and R1 carries all of it

    Isup   =  12 / Rtot                            =  ___ mA
    V(R1)  =  12 - Vout
    P(R1)  =  V(R1) * Isup                         =  ___ mW

  R2 and the load share Vout, and between them they split Isup

    I(R2)  =  Vout / 6000
    I(RL)  =  Vout / 3000                          =  ___ mA
    P(R2)  =  Vout * I(R2)
    P(RL)  =  Vout * I(RL)

  nothing else in this circuit dissipates anything, so those three have
  to come to exactly what the supply hands over

    P(R1) + P(R2) + P(RL)   =   12 V * Isup

  and the number that says whether the design is worth building at all:
  the share of that power reaching the load rather than warming R1 and R2

    P(RL) / (12 V * Isup)                          =  ___ %
''',
                "blanks": [
                    {
                        "prompt": "6.0 k\u03a9 and 3.0 k\u03a9 in parallel. How many kilohms?",
                        "hole": "?",
                        "opts": ["2.0", "9.0", "4.5", "3.0"],
                        "a": 0,
                        "why": "Product over sum: $(6000 \\times 3000)/9000 = 2000\\,\\Omega$. The "
                               "value 9.0 is the two added, which is the series rule and the wrong "
                               "circuit. The value 3.0 is the load on its own, as though it had "
                               "replaced R2 rather than joined it \u2014 R2 is still soldered in "
                               "place and still carrying current. The check that catches both: a "
                               "parallel pair must come out below 3.0, the smaller of the two.",
                    },
                    {
                        "prompt": "12 V across 3.0 k\u03a9 on top and 2.0 k\u03a9 below. What is the tap voltage?",
                        "hole": "?",
                        "opts": ["4.8", "8.0", "7.2", "6.0"],
                        "a": 0,
                        "why": "$12 \\times 2.0/5.0 = 4.8$ V. The value 8.0 is what this divider "
                               "would give unloaded, $12 \\times 6/9$, and the gap between the two "
                               "is the entire subject of this module. The value 7.2 is the drop "
                               "across the top resistor \u2014 correct, but it is the other half of "
                               "the supply, and the two of them add to 12.",
                    },
                    {
                        "prompt": "12 V across a 5.0 k\u03a9 chain. How many milliamps does the supply deliver?",
                        "hole": "?",
                        "opts": ["2.40", "1.33", "4.00", "2.00"],
                        "a": 0,
                        "why": "$12/5000 = 0.00240$ A. The value 1.33 is $12/9000$, the current this "
                               "divider drew before the load arrived \u2014 the load has pulled the "
                               "total resistance down and the supply current up, which is what a "
                               "load always does. The value 4.00 is $12/3000$, the top resistor "
                               "alone, as though the rest of the circuit were a short.",
                    },
                    {
                        "prompt": "7.2 V dropped across the top resistor, carrying 2.40 mA. How many milliwatts?",
                        "hole": "?",
                        "opts": ["17.28", "11.52", "28.8", "7.20"],
                        "a": 0,
                        "why": "$P = VI = 7.2 \\times 0.00240 = 0.01728$ W. Check it the other way: "
                               "$I^2R = 0.0024^2 \\times 3000 = 0.01728$ W as well. The value 11.52 "
                               "uses the tap voltage instead of the drop across the resistor "
                               "\u2014 the voltage in $P = VI$ has to be the voltage across the "
                               "part you are asking about. The value 28.8 is the whole supply's "
                               "output, which this resistor takes the largest single share of but "
                               "not all of.",
                    },
                    {
                        "prompt": "4.8 V across the 3.0 k\u03a9 load. How many milliamps?",
                        "hole": "?",
                        "opts": ["1.60", "0.80", "2.40", "4.00"],
                        "a": 0,
                        "why": "$4.8/3000 = 0.00160$ A \u2014 and it must be exactly twice R2's "
                               "0.80 mA, because the two have the same voltage across them and the "
                               "load has half the resistance. The value 2.40 is the supply current, "
                               "which is what these two add up to rather than what either carries. "
                               "The value 4.00 is $12/3000$: the load has 4.8 V across it, not the "
                               "supply's 12 V.",
                    },
                    {
                        "prompt": "The load gets 4.8 V at 1.60 mA; the supply gives 12 V at 2.40 mA. What percentage of the power reaches the load?",
                        "hole": "?",
                        "opts": ["26.7", "66.7", "40.0", "13.3"],
                        "a": 0,
                        "why": "$P_{load} = 4.8 \\times 0.00160 = 7.68$ mW against "
                               "$12 \\times 0.00240 = 28.8$ mW from the supply, so $7.68/28.8$ is "
                               "26.7%. The value 66.7 is the share of the *current* the load "
                               "takes, and 40.0 is the share of the *voltage* it sees; power is the "
                               "product of the two, and multiplying the two shares gives 26.7% "
                               "again. The value 13.3 is R2's share. Even at this generous a load "
                               "\u2014 comparable in size to the divider itself \u2014 nearly "
                               "three quarters of the energy is heating resistors, and a stiff "
                               "divider is far worse than that.",
                    },
                ],
            },
            "derive": {
                "title": "The loaded divider, once and for all",
                "minutes": 14,
                "vars": ["V_in", "V_out", "R_1", "R_2", "R_L", "X"],
                "brief": r'''
Six lines of algebra that between them replace every divider calculation in this module.
The first two are the unloaded rule; the middle two are the substitution that handles a
load; the last two turn the whole thing round so it can be designed with rather than
merely evaluated.

Nothing new is used. Ohm's law, the series rule and the parallel rule, and that is all.
Write each answer as an expression in the symbols named, with no numbers in it.
''',
                "steps": [
                    {
                        "prompt": "Nothing is connected to the output yet, so $R_1$ and $R_2$ carry the same current. Write that current in terms of $V_{in}$, $R_1$ and $R_2$.",
                        "answer": "\\frac{V_{in}}{R_1+R_2}",
                        "hint": "Series resistances add, so the pair looks like one resistor of $R_1+R_2$. Then Ohm's law once.",
                        "deconstruct": [
                            "KCL at the node between them: the node has two wires, so what arrives leaves.",
                            "One current means the pair behaves as a single resistance, and in series that is $R_1+R_2$.",
                        ],
                    },
                    {
                        "prompt": "$V_{out}$ is that current flowing through $R_2$ alone. Write $V_{out}$ in terms of $V_{in}$, $R_1$ and $R_2$.",
                        "answer": "\\frac{V_{in} R_2}{R_1+R_2}",
                        "hint": "Ohm's law on $R_2$: multiply your last answer by $R_2$.",
                    },
                    {
                        "prompt": "Now connect a load $R_L$ from the output node to ground. Write the resistance $X$ of $R_2$ and $R_L$ taken together, as a single fraction in $R_2$ and $R_L$.",
                        "answer": "\\frac{R_2 R_L}{R_2+R_L}",
                        "hint": "Both ends of $R_L$ are joined to both ends of $R_2$, so they are in parallel \u2014 product over sum.",
                        "deconstruct": [
                            "$1/X = 1/R_2 + 1/R_L$, because parallel conductances add.",
                            "Over a common denominator that is $(R_L+R_2)/(R_2R_L)$, and $X$ is its reciprocal.",
                        ],
                    },
                    {
                        "prompt": "The circuit is now an ordinary two-resistor divider of $R_1$ over $X$. Write $V_{out}$ in terms of $V_{in}$, $R_1$ and $X$.",
                        "answer": "\\frac{V_{in} X}{R_1+X}",
                        "hint": "This is the expression from the second step with $R_2$ replaced by $X$. That replacement is the only new idea in the module.",
                    },
                    {
                        "prompt": "Substitute your expression for $X$ into that and simplify, to a single fraction in $V_{in}$, $R_1$, $R_2$ and $R_L$.",
                        "answer": "\\frac{V_{in} R_2 R_L}{R_1 R_2 + R_1 R_L + R_2 R_L}",
                        "hint": "Multiply the top and the bottom of the whole thing by $(R_2+R_L)$ and every inner fraction disappears.",
                        "deconstruct": [
                            "Top: $V_{in}\\,\\frac{R_2R_L}{R_2+R_L} \\times (R_2+R_L) = V_{in}R_2R_L$.",
                            "Bottom: $\\left(R_1 + \\frac{R_2R_L}{R_2+R_L}\\right)(R_2+R_L) = R_1R_2 + R_1R_L + R_2R_L$.",
                            "The result is symmetric in $R_2$ and $R_L$, which it has to be \u2014 the circuit cannot tell which of the two resistors on the output node is 'the divider' and which is 'the load'.",
                        ],
                    },
                    {
                        "prompt": "Now turn it round to design with. Starting from $V_{out} = V_{in}X/(R_1+X)$, solve for $X$ in terms of $V_{in}$, $V_{out}$ and $R_1$.",
                        "answer": "\\frac{R_1 V_{out}}{V_{in}-V_{out}}",
                        "hint": "Multiply out, gather every term containing $X$ on one side, and take $X$ outside a bracket.",
                        "deconstruct": [
                            "$V_{out}(R_1+X) = V_{in}X$, so $V_{out}R_1 = X(V_{in}-V_{out})$.",
                            "Divide by $(V_{in}-V_{out})$, which is positive whenever the output is below the supply \u2014 that is, always.",
                        ],
                    },
                    {
                        "prompt": "Finally, recover the resistor you actually have to buy. $X$ is $R_2$ in parallel with the known load, so write $R_2$ in terms of $X$ and $R_L$.",
                        "answer": "\\frac{X R_L}{R_L-X}",
                        "hint": "$1/R_2 = 1/X - 1/R_L$. Put the right-hand side over a common denominator and invert.",
                        "deconstruct": [
                            "$1/R_2 = 1/X - 1/R_L = (R_L-X)/(XR_L)$.",
                            "So $R_2 = XR_L/(R_L-X)$ \u2014 note the *minus* sign, where undoing a parallel differs from doing one.",
                        ],
                    },
                ],
                "closing": r'''
Put the design from the reading through the last two steps. A 5 V rail, 3.30 V wanted, a
47 kΩ load, and a 1 mA current budget that fixed $R_1$ at 1.70 kΩ:

```text
    X    =  1700 * 3.3 / (5 - 3.3)              =  3300 ohm
    R2   =  3300 * 47000 / (47000 - 3300)       =  3549 ohm
```

and the fifth step confirms it in one line: $5 \times 3549 \times 47000$ over
$1700\times3549 + 1700\times47000 + 3549\times47000$ is 3.300 V.

The minus sign in the last step is where the algebra tells you something the arithmetic
would not. If $X$ comes out equal to $R_L$, the required $R_2$ is infinite: the load on
its own is already the whole bottom half of the divider, and the best you can do is fit
no $R_2$ at all. If $X$ comes out *larger* than $R_L$, the answer is negative, which is
the algebra's way of saying the specification is impossible — the load by itself already
pulls the output below the voltage you asked for, and no resistor added in parallel with
it can pull the output back up. When that happens the only fixes are a smaller $R_1$ or
a lighter load; that is the message the lab's fourth hint is repeating.

Two things worth carrying forward. The symmetry noticed in the fifth step — that the
formula cannot tell $R_2$ from $R_L$ — is the first sign of something general: what the
output node sees is one resistance to ground and one path to the supply, and it does not
care how those were built. Module 10 turns that observation into Thévenin's theorem.
And the sixth step, $X = R_1V_{out}/(V_{in}-V_{out})$, is worth keeping in its own
right; it is the fastest route from "I need this voltage" to a pair of resistors that
gives it.
''',
            },
            "lab": {
                "title": "Designing the divider you just drew",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
The algebra behind the circuit, so that the next one takes a second rather than a
sheet of paper.

- `divider_out(vin, r_top, r_bottom)` — the output with nothing connected to it.
- `loaded_out(vin, r_top, r_bottom, r_load)` — the output when `r_load` is connected
  across the bottom resistor. Combine the two lower resistors in parallel first, then
  reuse `divider_out`.
- `bottom_for(vin, vout, r_top, r_load)` — the value the bottom resistor must have so
  that the loaded output is exactly `vout`.

For the last one, work backwards. If the parallel combination of the bottom resistor
and the load is $X$, then $v_{out} = v_{in}X/(R_{top}+X)$, and solving for $X$ gives

```text
X = r_top * ratio / (1 - ratio)      where ratio = vout / vin
```

Then recover the bottom resistor from $1/X = 1/R_{bottom} + 1/R_{load}$.
''',
                "files": [{"name": "main.py", "content": r'''
"""Voltage dividers, with and without a load."""


def divider_out(vin, r_top, r_bottom):
    """Output voltage of an unloaded divider, measured across r_bottom."""
    # TODO: vin times the fraction of the total resistance that r_bottom holds.
    return 0.0


def loaded_out(vin, r_top, r_bottom, r_load):
    """Output voltage when r_load is connected across r_bottom."""
    # TODO: combine r_bottom and r_load in parallel, then call divider_out.
    return 0.0


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor that gives exactly `vout` with `r_load` connected."""
    # TODO: find the parallel value X that the divider needs, then undo the parallel.
    return 0.0


if __name__ == "__main__":
    print("unloaded 20k/10k from 9 V:", divider_out(9.0, 20000.0, 10000.0), "V")
    print("with a 100k load:", loaded_out(9.0, 20000.0, 10000.0, 100000.0), "V")
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    print("bottom resistor for a true 3 V:", rb, "ohms")
    print("check:", loaded_out(9.0, 20000.0, rb, 100000.0), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Voltage dividers, with and without a load."""


def divider_out(vin, r_top, r_bottom):
    """Output voltage of an unloaded divider, measured across r_bottom."""
    return vin * r_bottom / (r_top + r_bottom)


def loaded_out(vin, r_top, r_bottom, r_load):
    """Output voltage when r_load is connected across r_bottom."""
    pair = 1.0 / (1.0 / r_bottom + 1.0 / r_load)
    return divider_out(vin, r_top, pair)


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor that gives exactly `vout` with `r_load` connected."""
    ratio = vout / vin
    x = r_top * ratio / (1.0 - ratio)
    return 1.0 / (1.0 / x - 1.0 / r_load)


if __name__ == "__main__":
    print("unloaded 20k/10k from 9 V:", divider_out(9.0, 20000.0, 10000.0), "V")
    print("with a 100k load:", loaded_out(9.0, 20000.0, 10000.0, 100000.0), "V")
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    print("bottom resistor for a true 3 V:", rb, "ohms")
    print("check:", loaded_out(9.0, 20000.0, rb, 100000.0), "V")
'''}],
                "hints": [
                    "`divider_out` is `vin * r_bottom / (r_top + r_bottom)`. The resistance you measure across goes on top of the fraction.",
                    "`loaded_out` should not repeat the divider formula: work out the parallel pair, then hand it to `divider_out` as the new bottom resistor.",
                    "In `bottom_for`, `ratio` is `vout / vin`, and `x` is the parallel value the divider needs. Then undo the parallel with `1 / (1/x - 1/r_load)`.",
                    "If `bottom_for` returns a negative number, the output you asked for is impossible with that top resistor and that load — the load alone already pulls the output below the target.",
                ],
                "tests": [
                    {"name": "the unloaded divider splits by ratio", "code": r'''
v = divider_out(9.0, 20000.0, 10000.0)
assert abs(v - 3.0) < 1e-12, f"10k of 30k from 9 V is 3 V, got {v}"
assert abs(divider_out(9.0, 200000.0, 100000.0) - 3.0) < 1e-12, \
    "scaling both resistors by ten must not change the output"
'''},
                    {"name": "a load pulls the output down", "code": r'''
v = loaded_out(9.0, 20000.0, 10000.0, 100000.0)
assert abs(v - 2.8125) < 1e-9, \
    f"10k in parallel with 100k is 9090.9 ohms, giving 2.8125 V, got {v}"
assert v < divider_out(9.0, 20000.0, 10000.0), "the loaded output must be the lower one"
'''},
                    {"name": "a very light load barely matters", "code": r'''
v = loaded_out(9.0, 20000.0, 10000.0, 1e9)
assert abs(v - 3.0) < 1e-4, f"a 1 G-ohm load should leave the divider alone, got {v}"
'''},
                    {"name": "the design function hits the target", "code": r'''
rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
assert abs(rb - 11111.111111111111) < 1e-6, \
    f"the bottom resistor should be about 11.111 k, got {rb}"
back = loaded_out(9.0, 20000.0, rb, 100000.0)
assert abs(back - 3.0) < 1e-9, f"feeding it back should give exactly 3 V, got {back}"
'''},
                    {"name": "it also works for a different rail", "code": r'''
rb = bottom_for(5.0, 3.3, 33000.0, 100000.0)
back = loaded_out(5.0, 33000.0, rb, 100000.0)
assert abs(back - 3.3) < 1e-9, f"expected 3.3 V back, got {back}"
assert rb > 0, f"a positive resistor should be possible here, got {rb}"
'''},
                ],
            },
        },
        # ---- M5 -----------------------------------------------------------
        {
            "title": "Current division and the ladder",
            "summary": "A junction splits a current the way a series pair splits a voltage — with the fraction the other way up.",
            "concepts": [
                "At a junction the current divides between the branches, and the branch with the least resistance takes the largest share. Nothing decides this: every branch has the same voltage across it, and Ohm's law does the rest.",
                "For two resistors in parallel carrying a total current $I_t$, the current in $R_1$ is $I_1 = I_t\\,R_2/(R_1+R_2)$. The *other* resistance is on top of the fraction, which is the opposite of the voltage divider.",
                "That swap is not a quirk to memorise, and it is not that the larger share sits on top: put $R_1 = 1$ kΩ against $R_2 = 9$ kΩ and $I_1 = I_t R_2/(R_1+R_2)$ gives $R_1$ nine tenths of the current while $R_2$ is the resistance upstairs. It is the algebra. $R_1$ occurs twice — once setting the shared voltage, once dividing it to make its own current — and the two cancel. Your own resistance on top is a share of voltage; the other resistance on top is a share of current.",
                "With three or more branches, stop reaching for a formula: find the shared voltage $V = I_t\\,R_\\text{par}$, then take $V/R_k$ for each branch. It is fewer steps and it cannot come out upside down.",
                "A ladder — series resistors along a chain with shunts to ground between them — collapses from the far end back towards the source, one series step and one parallel step at a time.",
                "Two limits are worth keeping as sanity checks: a short circuit across a branch takes all of the current, and an open branch takes none of it.",
                "\"Current takes the path of least resistance\" is false as stated. Current takes every path, in inverse proportion to each one's resistance; the slogan is only true in the limit where one branch is thousands of times lower than the rest. That happens to be the case people meet when something has shorted, which is why the slogan keeps getting confirmed exactly where it works and applied where it does not.",
                "A resistor network with one source is linear in that source, so you may guess a convenient far-end current, walk inwards to the supply that guess implies, and scale every number by the ratio of the real supply to the implied one. On a ladder that is usually less work than collapsing it.",
            ],
            "read": [
                {
                    "title": "Why a junction splits the current it does",
                    "minutes": 15,
                    "body": r'''
Every powered thing has a node with several loads hanging off it. A car's fusebox is the
shape at its plainest: one thick lead arrives from the battery at a bar of copper, and a
dozen fuses leave it — headlamps, wipers, heater, radio — each feeding its own load down
to the chassis. All of those loads sit between the same bar and the same ground. The
battery supplies every one of them at once, and the current in the thick lead is whatever
they take between them.

That is a parallel connection, and module 3 said what resistance such a collection
presents. What it did not say is how the arriving current *divides* — which fuse carries
what. That is this reading, and it needs no new physics at all. The whole of it follows
from one fact about the ends of the branches.

## Nothing at the junction decides anything

Start by killing the picture most people carry without noticing. It is tempting to
imagine the junction as a place where a decision is taken: charge arrives, surveys the
routes on offer, and apportions itself sensibly between them. Nothing of the kind
happens. An electron drifting up to that copper bar carries no information about what is
down any of the branches — it is half a millimetre from the junction and the headlamp is
two metres away. Whatever fixes the split is not local to the junction, and cannot be.

What fixes it is a fact about the *ends*. Every branch is connected between the same two
nodes: the bar at the top, the chassis at the bottom. A node has one voltage. So every
branch has the same voltage across it, exactly and by construction, and each branch then
obeys Ohm's law on its own, in complete ignorance of the others. The split is not decided
at the junction; it is decided by the two nodes, and the junction merely supplies
whatever the branches turn out to want.

That is the whole physics of it. Everything below is arithmetic.

## Same voltage, so current in inverse proportion

Call the shared voltage $V$. Then

$$I_1 = \frac{V}{R_1} \qquad\text{and}\qquad I_2 = \frac{V}{R_2}$$

and dividing one by the other kills $V$, which is the only quantity you did not know:

$$\frac{I_1}{I_2} = \frac{R_2}{R_1}$$

Ten times the resistance, a tenth of the current. Put a 100 Ω and a 1.0 kΩ resistor
across a 5.00 V rail and the numbers are $5.00/100 = 50.0$ mA and $5.00/1000 = 5.00$ mA:
a ten-to-one split, 55.0 mA out of the supply altogether.

That inverse proportion *is* the rule, and it is the check to run on every split you
produce: the larger resistance must come out with the smaller current. If it has not, the
error is a line or two above.

## The phrase to stop using

"Current takes the path of least resistance" is the most-repeated sentence in this
subject and one of the least useful. In the pair just worked, the 1.0 kΩ is emphatically
not the path of least resistance and it is carrying 5.00 mA — a twentieth of an amp,
enough to light an indicator, enough to be the entire supply current of a sleeping
microcontroller. Nothing about it declined to conduct.

Current takes **every** path, in inverse proportion to the resistance of each. The slogan
is only true in the limit, when one branch is so much lower than the rest that the others
round to nothing.

It is worth naming why the slogan survives. It survives because the case where it is
nearly true is the case people meet when something has gone wrong: a solder whisker
across a resistor, a screwdriver across a terminal, a flooded connector. In those the
faulty path really is thousands of times lower than everything else, the slogan really
does predict the outcome, and so it gets confirmed exactly where it happens to work. Then
it gets applied to a 100 Ω against a 1.0 kΩ, where it is simply false.

## Conductance says it the right way up

Resistance is upside down for this job. Define **conductance**,

$$G = \frac{1}{R}$$

measured in siemens (S). One kilohm is one millisiemens, and it is worth being able to
convert without thinking:

```text
    R                G
    100 ohm    ->   10 mS
    1.0 kohm   ->    1 mS
    4.7 kohm   ->    0.213 mS
    1.0 Mohm   ->    1 uS
```

Ohm's law reads $I = GV$, so a branch's current is *directly* proportional to its
conductance, and — since parallel branches add conductance the way series ones add
resistance — the split reads as it should:

$$I_k = I_t\,\frac{G_k}{G_1 + G_2 + \cdots + G_n}$$

**A branch takes the share of the current that it holds of the total conductance.** That
is the current divider, for any number of branches, and the exact mirror of the voltage
divider, where a resistor takes the share of the voltage it holds of the total
resistance.

## Where the upside-down formula comes from

For exactly two branches you can put that back in terms of resistance. Substitute
$G_1 = 1/R_1$ and $G_2 = 1/R_2$, then multiply top and bottom by $R_1R_2$:

$$I_1 = I_t\,\frac{1/R_1}{1/R_1 + 1/R_2} = I_t\,\frac{R_2}{R_1 + R_2}$$

$R_2$ on top, in the expression for the current through $R_1$. It looks like a trap and
most people file it as one. It is not: $R_1$ occurs twice — once setting the shared
voltage, once dividing it to make its own current — and the two cancel, leaving $R_2$
upstairs.

Do not try to hold onto it as *the bigger share goes on top*, because that is false. Put
$R_1 = 1$ kΩ and $R_2 = 9$ kΩ: the formula gives $I_1 = 0.9\,I_t$, so the resistance
sitting on top is the one carrying a *ninth* of what the other one carries. What is worth
holding onto is which fraction you are building. Your own resistance on top is a share of
**voltage**; the other resistance on top is a share of **current**.

## Worked: 30 mA into three branches

30.0 mA arrives at a node. Three resistors run from it to ground: 200 Ω, 300 Ω and 600 Ω.

```text
conductances (1 mS = 1/(1 kohm), so 1/200 ohm = 5 mS):

    G1 = 1/200   =   5.000 mS
    G2 = 1/300   =   3.333 mS
    G3 = 1/600   =   1.667 mS
                     --------
    Gtot         =  10.000 mS    ->   Rpar = 1/Gtot = 100 ohm

the shared voltage is the whole current through that parallel resistance:

    V     =  30.0 mA * 100 ohm             =   3.00 V

and each branch is then Ohm's law on its own:

    I1    =  3.00 / 200                    =  15.0 mA
    I2    =  3.00 / 300                    =  10.0 mA
    I3    =  3.00 / 600                    =   5.0 mA
             ---------------------------------------
                                              30.0 mA    KCL closes
```

Three things to take from that. The branch currents add back to the 30.0 mA that arrived,
because they have nowhere else to go; that is Kirchhoff's current law, it costs one
addition, and it is the check to do every time. The 200 Ω took exactly half the current
because it holds exactly half of the 10 mS — not because it is first, or nearest, or
drawn on the left. And the parallel resistance came out at 100 Ω, below the smallest
branch, which it always must: every extra branch is another way through, so adding one
can only ever raise the conductance and lower the resistance.

The two-resistor formula agrees if you collapse the 300 Ω and 600 Ω into 200 Ω first:
$30.0 \times 200/400 = 15.0$ mA, by a longer road with one more chance to write the
fraction upside down.

## Worked: a 1 A ammeter built out of a 1 mA movement

Run the rule backwards and it becomes a design method. This is the classic instance, and
the arithmetic is still done every time somebody chooses a current-sense resistor.

A moving-coil movement reads full scale at 1.00 mA through it, and its coil measures
85.0 Ω. You want an instrument that reads full scale at 1.00 A. The movement cannot take
1.00 A — it would take a thousand times its rated current and burn out — so put a
**shunt** resistor straight across it and let the shunt carry the rest.

```text
at full scale the movement takes 1.00 mA, so the shunt takes what is left:

    I(shunt)  =  1000.00 mA - 1.00 mA          =  999.00 mA

the two branches share one voltage, and the movement is what fixes it:

    V         =  1.00 mA * 85.0 ohm            =  85.0 mV

so the shunt is Ohm's law on that voltage and that current:

    R(shunt)  =  85.0 mV / 999.00 mA           =  0.085085 ohm
```

85.1 mΩ. Check it forwards with the two-branch formula, which had better agree:

```text
    I(coil)   =  1.000 A * 0.085085 / (0.085085 + 85.0)
              =  1.000 A * 0.085085 / 85.085085          =  1.0000 mA
```

It does. And the power, which tells you what the shunt has to be built like:

```text
    P(shunt)  =  999.00 mA * 85.0 mV           =  84.915 mW
    P(coil)   =    1.00 mA * 85.0 mV           =   0.085 mW
                                                  ---------
                                                  85.000 mW  =  1.000 A * 85.0 mV
```

Look at what the inverse proportion is doing here at its most extreme. The shunt is
$85.0/0.085085 = 999$ times lower in resistance than the coil, it carries 999 times the
current, and it therefore takes 999 times the power. At 1 A that is 85 mW and any small
resistor will do. Build the same instrument for 100 A and the movement still wants its
85.0 mV, so the shunt becomes $0.0850/99.999 = 0.850$ mΩ dissipating
$0.0850 \times 100 = 8.50$ W — which is why high-current shunts are bars of alloy bolted
to a heatsink while the movement stays a few hundred turns of hair-thin wire.

Notice also which component fixed the design. Nothing about the shunt was chosen; the
movement's full-scale current and coil resistance between them fix the 85.0 mV, and the
85.0 mV plus the range you want fix everything else. That 85.0 mV has a name — the
**burden voltage** — and it is the price of measuring the current at all: inserting this
ammeter into a circuit inserts 85.1 mΩ and steals 85 mV from it. An ammeter that reads
without disturbing is the thing that does not exist.

## The mistakes, and why they are tempting

**The branch's own resistance on top.** Somebody writes $I_1 = I_t R_1/(R_1+R_2)$ and
gets every split exactly backwards. It is tempting for three reasons at once: the voltage
divider is met first and used ten times as often, its fraction has the identical *shape*,
and both versions produce a plausible number between zero and the total, so nothing looks
wrong on the page. The repair costs a second — glance at the answer and ask whether the
bigger resistor got the bigger current. If it did, it is wrong. The better repair is to
stop using the formula: shared voltage first, then Ohm's law on each branch, and there is
nothing left to invert.

**Inventing a three-branch version.** With 200 Ω, 300 Ω and 600 Ω the pattern seems to
generalise — put the *other* resistances on top, over the sum of all three:

```text
    "I1"  =  30.0 * (300+600)/1100  =  24.5 mA     the truth is 15.0 mA
    "I2"  =  30.0 * (200+600)/1100  =  21.8 mA     the truth is 10.0 mA
    "I3"  =  30.0 * (200+300)/1100  =  13.6 mA     the truth is  5.0 mA
                                        --------
                                        60.0 mA
```

Those "fractions" are $900/1100$, $800/1100$ and $500/1100$, and they add to
$2200/1100 = 2$. The method hands out twice the current that arrived, and would hand out
$n-1$ times it for $n$ branches. There is no three-resistor version of $R_2/(R_1+R_2)$
worth carrying around. With three branches or more, go through the shared voltage or
through conductances, which are the same route written two ways.

## Where it stops holding

The argument needed both branches to have the *same two nodes* at their ends. Four ways
that fails, in rough order of how often you will meet them.

**Something else in one branch.** Two resistors that merely look parallel on a crowded
schematic, but with a source, another resistor or a wire heading off somewhere in one of
them, do not share a voltage, and none of this applies. Check the ends, not the picture.
The next reading is entirely about the commonest such shape.

**The copper is not perfect.** "The same node" is a claim about a piece of metal, and at
85 mΩ it stops being true. Twenty milliohms of lead and solder-joint resistance in series
with that shunt raises the branch to 105 mΩ, so the shunt takes less and the coil takes
more: $1.000 \times 0.105085/85.105085 = 1.235$ mA where 1.000 mA was wanted, and the
instrument reads 23% high at every point on its scale. The fix is to stop pretending —
draw the wire in as a resistor, at which point the circuit is a ladder and the next
reading handles it, or bring two separate sense wires to the shunt itself so that the
leads carrying the current are not the leads carrying the measurement. That is a
four-terminal or Kelvin connection, and it is why precision shunts have four leads
instead of two.

**Branches that are not resistors.** Put two nominally identical LEDs in parallel behind
one resistor. They do share a voltage — that part still holds, and always will, because
it is only the definition of a node. But $I = V/R$ does not, because an LED has no
resistance, it has a curve. One LED with a forward voltage 50 mV below the other takes
far more than half the current, heats up, and its forward voltage falls further, so it
takes more still. That is current hogging, it ends with one dead LED and one dim one, and
it is why an array is built as strings with a resistor each. What replaces the divider
there is the same shared voltage plus each device's own $I$–$V$ curve, solved graphically
or numerically rather than in one line.

**The extremes.** Two are worth keeping as instincts. A branch of zero resistance holds
the shared voltage at zero and takes all the current — a short circuit, and why a stray
whisker of solder is fatal rather than untidy. A branch of infinite resistance takes none
— an open circuit, and what a cracked track looks like. Both are the same rule pushed to
its ends, and both are cases where "the path of least resistance" finally earns its keep.
''',
                },
                {
                    "title": "The ladder, and why you start at the far end",
                    "minutes": 16,
                    "body": r'''
A ladder is a chain: a series resistor from the supply to a node, a shunt from that node
to ground, another series resistor on to the next node, another shunt, and so on for as
many rungs as the circuit has. Nothing in it is new — series resistors and parallel
resistors, and that is all — and yet it is the first shape in this subject that will not
yield to staring at it.

It is also everywhere. The stepped attenuator in a signal generator is a ladder; so is
the R-2R network inside a digital-to-analogue converter; so is a resistor string in a
flash converter, tapped at every rung; so is a long cable, modelled as short pieces of
conductor resistance with leakage between them. So is a battery
feeding a load through a length of wire, feeding a second load through more wire. The
last of those is worth holding on to, because it is the case where a ladder appears
without anybody having designed one.

## What counts as a ladder

The shape has to be exact for the method below to work, and it is worth being able to say
what it is: **every shunt goes to ground, every series resistor goes to the next node
along, and nothing skips a rung.** Draw a line from the supply to the far end and every
component either sits on that line or hangs off it straight down.

Check the shape before you start. If it passes, the collapse below works. If it does not,
no amount of combining will help, and the last section says what to do instead.

## Why you cannot start at the supply

The instinct is to start where the energy comes from and work along, in the direction the
current goes. It does not work, and seeing exactly how it fails is what tells you where
to start instead.

Take the first node. To find its voltage you need the current in the first series
resistor. That current splits at the node between the first shunt and everything to the
right of it, and to know how it splits you need the resistance of the entire rest of the
ladder — every rung of it, right out to the end. The first step needs the last answer.

Now look at the far end. The last shunt has nothing beyond it, so what hangs off the far
node is simply that shunt's own value: nothing to combine, nothing to look up, no
dependence on anything else in the circuit. That is the one place in the whole ladder
where you can write a number down knowing nothing else, and the method is nothing more
than: start there, and walk back.

## Two moves, alternating

Collapsing a ladder uses exactly two operations, taken in turn:

1. **Series.** Whatever the ladder comes to beyond a node, plus the series resistor in
   front of it, is the two added.
2. **Parallel.** That sum sits alongside the shunt at the node, and combines with it as a
   parallel pair.

Repeat until you arrive back at the supply holding one number: the resistance the whole
ladder presents. The supply current is then Ohm's law on that, and you walk forward
again — node voltage, split the current, node voltage, split the current — using the
running totals from the way in.

Which is why you write those totals down. Every node voltage is the current arriving at
that node times the total hanging off it, and that total has already been computed on the
way in. Re-deriving them on the way out is pure waste and is where the arithmetic slips
happen.

## Worked: a two-rung ladder, both directions

A 9.00 V supply. Along the top: 2.0 kΩ to node B, then 1.0 kΩ to node C. Down to ground:
1.5 kΩ at B, 2.0 kΩ at C.

Inwards, from C:

```text
    at C, looking right: the 2.0 k shunt, alone       =  2.0 kohm
    add the 1.0 k series resistor in front of it      =  3.0 kohm
    that, alongside the 1.5 k shunt at B:
        (3.0 * 1.5) / (3.0 + 1.5)                     =  1.0 kohm   <- B's total
    add the 2.0 k series resistor in front of it      =  3.0 kohm   <- what the rail sees
```

Outwards, from the supply:

```text
    Itot  =  9.00 V / 3.0 kohm                =  3.00 mA   through the first 2.0 k
    V(B)  =  3.00 mA * 1.0 kohm               =  3.00 V    (1.0 k was B's total)
      the 1.5 k shunt at B takes 3.00/1.5k    =  2.00 mA
      so what carries on into the 1.0 k is    =  1.00 mA
    V(C)  =  3.00 V - 1.00 mA * 1.0 kohm      =  2.00 V
      and the 2.0 k shunt at C carries        =  1.00 mA   which it must, being the end
```

Notice which number did the work at node B: not the shunt's own 1.5 kΩ, but the 1.0 kΩ
that the shunt and the rest of the ladder come to *together*. That is the whole reason
for collapsing first.

## What the loading costs, in numbers

It is worth seeing how large the error is if you skip the collapse and treat the ladder
as a chain of independent dividers, each feeding the next.

The first pair on its own would put $9.00 \times 1.5/3.5 = 3.86$ V on node B. The true
answer is 3.00 V, because the rest of the ladder hangs on B and pulls it down. Carry the
mistake forward and node C comes out at $3.86 \times 2/3 = 2.57$ V against a true 2.00 V
— 29% high, and getting worse with every rung, because each rung inherits the last one's
error and adds its own.

The direction of the error is always the same, and that is worth knowing on its own. What
hangs beyond a node can only ever take current away from the shunt at it, so the node can
only ever be lower than the unloaded pair suggests. **A cascaded-divider answer is always
too high, never too low.** If your figure came out above the honest one, that is probably
why.

## Worked: three rungs, run backwards

Now a harder shape, and a method that is often less work than the one above. A 21.0 V
bench supply. Series resistors along the top, in order: 1.0 kΩ, 2.0 kΩ, 2.0 kΩ. Shunts,
in order: 5.0 kΩ, 6.0 kΩ, 4.0 kΩ. What does the far shunt carry?

You could collapse and walk out. Instead use the fact that the circuit contains one
source and nothing but resistors, so every voltage and current in it is *proportional* to
that source: double the supply and every number doubles. So guess the far-end current,
walk inwards to see what supply that guess implies, and scale.

Guess 1.00 mA in the far shunt, because it makes the arithmetic trivial:

```text
    V(C)  =  1.00 mA * 4.0 kohm                    =   4.00 V
    the 2.0 k in front of C carries that same 1.00 mA, dropping 2.00 V
    V(B)  =  4.00 + 2.00                           =   6.00 V
      the 6.0 k shunt at B takes 6.00/6.0k         =   1.00 mA
      so the 2.0 k in front of B carries 1+1       =   2.00 mA, dropping 4.00 V
    V(A)  =  6.00 + 4.00                           =  10.00 V
      the 5.0 k shunt at A takes 10.0/5.0k         =   2.00 mA
      so the 1.0 k at the top carries 2+2          =   4.00 mA, dropping 4.00 V
    supply needed                                  =  14.00 V
```

Every line of that is one application of Ohm's law or one addition at a node, and at no
point was anything unknown — which is the point of working inwards. 1.00 mA in the far
branch needs 14.0 V. The supply is 21.0 V, so scale everything by

$$\frac{21.0}{14.0} = 1.50$$

and the far shunt carries $1.00 \times 1.50 = 1.50$ mA. Every other number scales with
it: node A goes to 15.0 V, node B to 9.00 V, node C to 6.00 V, and the supply delivers
$4.00 \times 1.50 = 6.00$ mA.

Confirm it the long way, because the first few times you should:

```text
INWARDS
    4.0 k shunt at C, alone                        =  4.000 kohm
    + 2.0 k series                                 =  6.000 kohm
    alongside the 6.0 k shunt at B: (6*6)/12       =  3.000 kohm   <- B's total
    + 2.0 k series                                 =  5.000 kohm
    alongside the 5.0 k shunt at A: (5*5)/10       =  2.500 kohm   <- A's total
    + 1.0 k series                                 =  3.500 kohm   <- what the rail sees

OUTWARDS
    Itot  =  21.0 V / 3.5 kohm                     =  6.00 mA
    V(A)  =  6.00 mA * 2.5 kohm                    =  15.0 V
      the 5.0 k shunt takes 15.0/5.0k              =  3.00 mA, so 3.00 mA carries on
    V(B)  =  15.0 - 3.00 mA * 2.0 kohm             =   9.0 V
      the 6.0 k shunt takes 9.00/6.0k              =  1.50 mA, so 1.50 mA carries on
    V(C)  =   9.0 - 1.50 mA * 2.0 kohm             =   6.0 V
      and the 4.0 k shunt at C carries 6.00/4.0k   =  1.50 mA
```

Same answer, roughly twice the work, and with a parallel combination at every rung
instead of an addition. Which route to take is decided by what you are given: a supply
voltage sends you inwards then outwards, a far-end current or voltage sends you straight
inwards and stops.

## Every rung is a divider, with the right denominator

There is a way to see the ladder that makes the earlier mistake obvious. Each rung *is* a
voltage divider — the series resistor on top, and hanging below it not the shunt but
**the whole of what the node carries**, shunt and remaining ladder together. Using the
totals just computed:

```text
    rung 1:   V(A)/21.0  =  2.5 / (2.5 + 1.0)      =  0.7143
    rung 2:   V(B)/V(A)  =  3.0 / (3.0 + 2.0)      =  0.6000
    rung 3:   V(C)/V(B)  =  4.0 / (4.0 + 2.0)      =  0.6667
                                                      ------
    overall             0.7143 * 0.600 * 0.6667   =  0.2857
```

and $21.0 \times 0.2857 = 6.00$ V at node C, which is what the long route gave. The
fractions multiply, which is what "cascade" ought to mean and is perfectly legitimate —
provided each denominator is the collapsed total and not the shunt's own value.

Use the shunt's own value instead and you get $5/6$, $6/8$ and $4/6$, whose product is
0.4167, giving 8.75 V at node C against a true 6.00 V: 46% high. Same structure, one
wrong number per rung.

## Three checks, and they take seconds

- **Voltages fall on the way out.** 21.0, 15.0, 9.0, 6.0. A resistor network cannot raise
  a voltage above the node before it; one further out that came out higher is an error.
- **Currents split; they never grow.** 6.00 mA arrives at A, 3.00 mA turns down the
  shunt, 3.00 mA carries on. No series resistor can carry more than the one before it.
- **The power closes.** The supply hands over $21.0 \times 6.00 = 126$ mW. In milliamps
  and kilohms $I^2R$ lands directly in milliwatts, so the six resistors take 36.0, 45.0,
  18.0, 13.5, 4.5 and 9.0 mW — and those add to 126.0 mW, as they must.

That last one is the only check that tests every number at once, and it costs one line.
Note also what it reveals: the first series resistor and the first shunt between them
take 81 of the 126 mW. Almost two thirds of the supply's power is spent before the second
rung, because everything nearer the source carries every milliamp that everything further
out is going to need. That is generally true of ladders, and it is why the first rung is
the one that gets hot and the far end is the one that gets starved.

## The mistakes, and why they are tempting

**Cascading dividers.** Already quantified twice above, and it is by a distance the
commonest error in ladder work. It is tempting because the first two resistors *look*
like a complete divider on the page — a supply, a resistor, a resistor, a node — and
because the ladder is drawn left to right, which invites reading it left to right. The
repair is the sentence in the section above: the bottom of each rung's divider is
everything hanging off that node, not the shunt alone.

**Combining a pair that is not a pair.** Two resistors are in series only if the node
between them has nothing else attached; in parallel only if they share *both* ends. On a
ladder the series resistor and the shunt beyond it share one node and are not in series,
because the shunt is not carrying the same current. Every time a collapse gives an answer
that will not close on the power check, this is worth looking for first.

**Forgetting which total made which voltage.** On the way out, node B's voltage is the
current arriving at B times B's *collapsed* total, not times its shunt. Both numbers are
written on your page from the way in, they are both in kilohms, and picking the wrong one
produces a plausible answer. Label them.

## Where a ladder stops being a ladder

Everything here rests on the shape. Take a three-rung ladder and add one resistor from
the first node straight to the third, and the collapse has nowhere to begin: no two
components share both of their ends, and no node has only two components at it, so there
is not a single series or parallel pair anywhere in the circuit. That is a bridge, and
series-and-parallel reduction cannot touch it — not because it is hard, but because there
is no first step. A second supply part-way along the ladder does the same damage, and so
does a shunt that goes somewhere other than ground.

A non-ohmic rung breaks it differently. The shape survives, but a diode or a lamp in one
of the shunts has no resistance to combine, so there is nothing to collapse even though
the picture still looks like a ladder.

What replaces the method in each case is the same thing: a method that does not care
about shape. Nodal analysis, two modules from here, writes one equation per node and
solves them together; mesh analysis writes one per loop; and Thévenin's theorem lets you
swallow everything to the left of a node into a single source and a single resistor,
which is the ladder collapse generalised to circuits that do not collapse. All three cost
more work than this does, which is exactly why it is worth checking the shape first.

And at the other extreme, a ladder with enough rungs stops being worth counting. A metre
of cable is not four rungs or forty; it is resistance and leakage spread continuously
along its length, and the honest model is a differential equation rather than a chain of
resistors. That is a transmission line, and a later course takes it up.
''',
                },
            ],
            "quiz": {
                "title": "Splitting a current",
                "minutes": 8,
                "questions": [
                    {
                        "q": "6 mA arrives at a node where a 2 kΩ and a 4 kΩ resistor both run down to ground. What flows in the 2 kΩ?",
                        "opts": ["2 mA", "4 mA", "3 mA", "6 mA"],
                        "a": 1,
                        "why": r'''
The pair is $2\text{k}\parallel4\text{k} = 1.33$ kΩ, so the shared voltage is
$0.006 \times 1333 = 8$ V, and $8/2000 = 4$ mA. The formula says the same thing:
$I_1 = I_t R_2/(R_1+R_2) = 6 \times 4/6 = 4$ mA. Answering 2 mA is the voltage-divider
fraction applied to a current, which puts the branch's own resistance on top and gets
every current split backwards.
''',
                    },
                    {
                        "q": "Two resistors in parallel share a total current between them. Which carries more?",
                        "opts": [
                            "the larger resistance",
                            "they always carry the same",
                            "whichever one the current reaches first",
                            "the smaller resistance",
                        ],
                        "a": 3,
                        "why": r'''
They have the same voltage across them, so $I = V/R$ makes the smaller resistance carry
the larger current, in exact inverse proportion: a tenth of the resistance takes ten
times the current. There is also no such thing as reaching one first — both ends of
both resistors are joined to the same two nodes, so a parallel pair has no order to it
at all.
''',
                    },
                    {
                        "q": "12 mA divides between 1 kΩ, 2 kΩ and 2 kΩ, all in parallel. What flows in the 1 kΩ?",
                        "opts": ["4 mA", "3 mA", "6 mA", "12 mA"],
                        "a": 2,
                        "why": r'''
Find the shared voltage first. The three in parallel come to 500 Ω, so
$V = 0.012 \times 500 = 6$ V, and the branches carry $6/1000 = 6$ mA, $6/2000 = 3$ mA
and $6/2000 = 3$ mA. They add back to 12 mA, which is the check worth doing every time.
The two-resistor formula has no useful form for three branches, and trying to force one
is where the errors come from.
''',
                    },
                    {
                        "q": "A stray solder whisker bridges a 100 Ω resistor that is carrying current. What happens?",
                        "opts": [
                            "nothing measurable, because a whisker has no resistance",
                            "the resistor carries more current than before",
                            "the current everywhere else stops",
                            "almost all the current abandons the resistor and goes through the whisker",
                        ],
                        "a": 3,
                        "why": r'''
The whisker is a parallel branch of nearly zero resistance, so it takes nearly all of
the current and leaves the resistor with almost none. The rest of the circuit does not
stop — the opposite happens, since the total resistance has fallen, so more current
flows overall and something upstream may now be overloaded. That is what "shorting
something out" means, and the drawing on your screen will not show it.
''',
                    },
                    {
                        "q": "You calculate that of 10 mA arriving at a parallel pair of 1 kΩ and 9 kΩ, the 9 kΩ carries 9 mA. Without redoing the arithmetic, what is wrong?",
                        "opts": [
                            "nothing — that is right",
                            "both branches should carry the full 10 mA",
                            "the two figures belong the other way round: the larger resistance takes the smaller share",
                            "the two branches must carry 5 mA each",
                        ],
                        "a": 2,
                        "why": r'''
Current splits in inverse proportion to resistance, so the 9 kΩ takes a ninth of what
the 1 kΩ takes: 1 mA against 9 mA. Getting 9 mA in the 9 kΩ is the signature of using
$R_1/(R_1+R_2)$ — the voltage fraction — on a current. Glancing at a result
and asking whether the big resistor got the big current costs a second and catches this
every time.
''',
                    },
                ],
            },
            "build": {
                "title": "One current, three branches",
                "minutes": 24,
                "brief": r'''
The canvas opens with a 12 V supply, a 1 kΩ resistor hanging from the rail, and a probe
on the node below it. Nothing flows yet, because that node has no path to ground.

Finish it with **three** resistors from the probed node down to ground, so that

- the supply delivers exactly **6 mA**, and
- the three branches carry **1 mA, 2 mA and 3 mA** — in whichever order you like.

## The order to work in

The two requirements are not independent, and one of them has to go first. 6 mA through
the 1 kΩ already on the canvas fixes the drop across it, which fixes the voltage at the
probed node, which fixes the voltage across all three of your resistors at once —
they all sit between that node and ground. After that, each branch is a single
application of $R = V/I$.

Every value you need is a whole number of kilohms. If one of them is not, the node
voltage is wrong.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [11, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                        {"id": "p4", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 6000},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 3000},
                        {"id": "p6", "kind": "R", "x": 17, "y": 9, "rot": 1, "value": 2000},
                        {"id": "p7", "kind": "GND", "x": 13, "y": 10},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [11, 7]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [17, 8]},
                        {"a": [9, 10], "b": [17, 10]},
                    ],
                },
                "checks": [
                    {"name": "one 12 V supply, and the 1 kΩ still in series with it", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
c.assert(c.values('R').some(function (r) { return Math.abs(r - 1000) <= 10; }),
  'The 1 kΩ resistor between the rail and the probed node is part of the exercise — leave it there.');
'''},
                    {"name": "the supply delivers 6 mA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
c.close(Math.abs(cur[ids[0]]), 0.006, 0.02, 'the current out of the supply');
'''},
                    {"name": "which puts 6 V on the probed node", "code": r'''
c.close(c.vout(), 6.0, 0.02,
  'the probe voltage — 6 mA through the 1 kΩ drops 6 V, leaving 6 V for the branches');
'''},
                    {"name": "three branches, carrying 1 mA, 2 mA and 3 mA", "code": r'''
const dc = c.dc();
const out = c.outNode();
const branch = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(branch.length === 3,
  'Exactly three resistors should run from the probed node straight to ground; found ' +
  branch.length + '.');
const mA = branch.map(function (p) {
  return Math.abs(dc.v[p.n1] - dc.v[p.n2]) / p.value * 1000;
}).sort(function (a, b) { return a - b; });
[1, 2, 3].forEach(function (want, k) {
  c.close(mA[k], want, 0.02, 'the branch currents, smallest first (mA)');
});
'''},
                ],
                "hints": [
                    "Start with the supply current. 6 mA through the 1 kΩ that is already there drops $0.006 \\times 1000 = 6$ V, so the probed node sits at $12 - 6 = 6$ V.",
                    "All three of your resistors run from that node to ground, so all three have 6 V across them. Now each one is just $R = V/I$.",
                    "6 V at 1 mA is 6 kΩ, at 2 mA is 3 kΩ, at 3 mA is 2 kΩ. Their parallel combination is 1 kΩ, which is the other way of seeing that the total came to 2 kΩ.",
                    "In parallel means all three tops joined to the probed node and all three bottoms joined to ground. One ground symbol on the bottom rail is enough — every ground symbol is the same node.",
                ],
            },
            "numeric": [
                {
                    "title": "Two branches and one rule",
                    "minutes": 5,
                    "brief": r'''
The mechanical one, to get the rule under your fingers. A 12.0 V supply, a series
resistor, and then two resistors side by side from the probed node down to ground. An
ammeter in the supply lead reads 6.00 mA, and that is the current arriving at the
junction to be split.

One unknown, one rule, one line of arithmetic.
''',
                    "prompt": "How much of that current flows in the 1.0 kΩ?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 1200},
                            {"id": "r2", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 1000},
                            {"id": "r3", "kind": "R", "x": 17, "y": 10, "rot": 1, "value": 4000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 7},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 9]},
                            {"a": [11, 7], "b": [15, 7]},
                            {"a": [11, 9], "b": [17, 9]},
                            {"a": [11, 11], "b": [17, 11]},
                            {"a": [11, 11], "b": [11, 13]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "Series resistor", "value": "1.20 kΩ"},
                        {"label": "One branch", "value": "1.00 kΩ"},
                        {"label": "The other branch", "value": "4.00 kΩ"},
                        {"label": "Ammeter in the supply lead", "value": "6.00 mA"},
                    ],
                    "aside": "The two branches run between the same pair of nodes, so they hold the "
                             "same voltage. That single fact is all the divider rule uses — the "
                             "series resistor above them plays no part in the split.",
                    "answer": 4.8,
                    "tol": 0.02,
                    "unit": "mA",
                    # The prompt asks for the current in one named branch, and no node of the
                    # circuit is a current, so the check takes that resistor's own drop out of the
                    # solve and divides by its own value. Reading both off the part means a
                    # re-drawn schematic is still measured in the right place.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r2'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1000;
''',
                    "hint": "The *other* resistance goes on top: $I_1 = I_t R_2/(R_1+R_2)$, which "
                            "here is $6.00 \\times 4.00/5.00$.",
                    "wrong": "If you got 1.20, the branch's own resistance went on top — that is "
                             "the voltage fraction, and using it on a current gets every split "
                             "backwards. The 1.0 kΩ is the smaller resistance, so it must come "
                             "out with the larger share, and 1.20 mA is less than half of 6.00. If "
                             "you got 3.00, the current has been halved rather than divided.",
                    "why": r'''
```
by the rule, with the OTHER resistance on top:

    I(1.0k)  =  6.00 mA * 4.00 / (1.00 + 4.00)     =  4.80 mA
    I(4.0k)  =  6.00 mA * 1.00 / (1.00 + 4.00)     =  1.20 mA
                                                      -------
                                                      6.00 mA   KCL closes

by the shared voltage, which is the same arithmetic in a different order:

    Rpar     =  (1000 * 4000) / 5000               =   800 ohm
    V(node)  =  6.00 mA * 800 ohm                  =  4.80 V
    I(1.0k)  =  4.80 / 1000                        =  4.80 mA
```

Four fifths of the current goes down the 1.0 kΩ because it holds four fifths of the
conductance: 1.00 mS against 0.25 mS. And the 6.00 mA on the ammeter was not a gift —
the circuit fixes it. The pair comes to 800 Ω, the series resistor adds 1200 Ω, and
$12.0/2000 = 6.00$ mA.
''',
                },
                {
                    "title": "The branch that has not been fitted",
                    "minutes": 8,
                    "brief": r'''
A board part-built. A 24.0 V rail feeds a 1.00 kΩ series resistor into the probed node,
and two shunt resistors are already soldered from that node to ground: 4.00 kΩ and
12.0 kΩ. Beside them is a third pair of empty pads, which is why the drawing shows two
branches and not three.

As it stands the rail delivers 6.00 mA. The specification says the finished board must
draw exactly **8.00 mA**. What goes in the empty pads?

Adding a branch can only ever increase the current, so the direction is right; the
question is how much resistance produces exactly that much extra.
''',
                    "prompt": "What value must the third shunt resistor be?",
                    "note": "Give the answer in kilohms, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 4000},
                            {"id": "r3", "kind": "R", "x": 17, "y": 10, "rot": 1, "value": 12000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 7},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 9]},
                            {"a": [11, 7], "b": [15, 7]},
                            {"a": [11, 9], "b": [17, 9]},
                            {"a": [11, 11], "b": [17, 11]},
                            {"a": [11, 11], "b": [11, 13]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "24.0 V"},
                        {"label": "Series resistor", "value": "1.00 kΩ"},
                        {"label": "Fitted shunts", "value": "4.00 kΩ and 12.0 kΩ"},
                        {"label": "Rail current now", "value": "6.00 mA"},
                        {"label": "Rail current wanted", "value": "8.00 mA"},
                    ],
                    "aside": "Work in whole-circuit resistance first, not in branch currents. The "
                             "wanted supply current fixes the total the rail must see, the series "
                             "resistor comes off that, and what is left is what the three branches "
                             "together have to come to.",
                    "answer": 6.0,
                    "tol": 0.05,
                    "unit": "kΩ",
                    # The answer is a part that is not on the board, so there is nothing to read
                    # off directly. Everything except the 8.00 mA target comes out of the solve:
                    # the rail voltage, the rail current, and the probed node between them give
                    # the series resistor and the fitted branches' parallel value, and the missing
                    # branch is the conductance that makes up the difference.
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const V = Math.abs(d.v[src.n1] - d.v[src.n2]);
const I = Math.abs(d.currents[src.id]);
const vnode = d.v[c.outNode()];
const Rseries = (V - vnode) / I;
const Rfitted = vnode / I;
const Rwanted = V / 0.00800 - Rseries;
return 1 / (1 / Rwanted - 1 / Rfitted) / 1000;
''',
                    "hint": "$24.0/8.00\\text{ mA} = 3.00$ kΩ is what the rail must see in "
                            "total. Take off the 1.00 kΩ in series and the three branches "
                            "together have to be 2.00 kΩ. The two fitted ones already come to "
                            "3.00 kΩ.",
                    "wrong": "If you got 1.00, resistances have been subtracted — 3.00 kΩ "
                             "minus 2.00 kΩ — and that is the series rule applied to a "
                             "parallel problem. Parallel branches add conductance, so it is the "
                             "conductances that subtract. If you got 2.00, that is the total the "
                             "three branches must come to, not the one that is missing. If you got "
                             "3.00, that is what the rail must see, series resistor and all.",
                    "why": r'''
```
what the rail must see, from the current the specification asks for:

    Rtot      =  24.0 V / 8.00 mA                  =  3.00 kohm
    minus the 1.00 k series resistor
    Rpar      =  3.00 - 1.00                       =  2.00 kohm    the three branches

what the two fitted branches already come to:

    Rfitted   =  (4.00 * 12.0) / (4.00 + 12.0)     =  3.00 kohm

resistances do not subtract in parallel; conductances do:

    Gwanted   =  1 / 2000                          =  0.500 mS
    Gfitted   =  1 / 3000                          =  0.333 mS
                                                      --------
    G3        =  0.500 - 0.333                     =  0.167 mS
    R3        =  1 / 0.000167                      =  6.00 kohm
```

Check it forwards. With 6.00 kΩ fitted, the three branches come to
$1/(0.250 + 0.0833 + 0.167) = 2.00$ kΩ, the rail sees 3.00 kΩ and delivers 8.00 mA, and
the node sits at $8.00 \times 2.00 = 16.0$ V rather than the 18.0 V it sits at now. The
branch currents are then 4.00 mA, 1.33 mA and 2.67 mA, which add to 8.00 mA.

Note what adding a branch did to the two already there: they used to carry 4.50 mA and
1.50 mA, and now they carry 4.00 mA and 1.33 mA. Their share fell because the node
voltage fell — nothing in a parallel network is unaffected by what is bolted next to it,
as long as the thing feeding it has any resistance at all.
''',
                },
                {
                    "title": "How far down the ladder does the voltage get?",
                    "minutes": 9,
                    "brief": r'''
Two rungs. Along the top, 2.0 kΩ from the supply to the first node, then 2.0 kΩ from
there to the probed node. Down to ground, 6.0 kΩ at the first node and 4.0 kΩ at the
probed one.

There is no way to start at the supply: the current in the first resistor depends on how
much of it turns down the 6.0 kΩ, and that depends on what the rest of the ladder comes
to. Start at the far end, where nothing is unknown, and collapse back.
''',
                    "prompt": "What voltage does the probe read?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "value": 2000},
                            {"id": "r2", "kind": "R", "x": 7, "y": 7, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 7, "y": 10},
                            {"id": "r3", "kind": "R", "x": 10, "y": 4, "value": 2000},
                            {"id": "r4", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 4000},
                            {"id": "g2", "kind": "GND", "x": 11, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [7, 6]},
                            {"a": [7, 8], "b": [7, 10]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [11, 4], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 10]},
                            {"a": [11, 4], "b": [14, 4]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "10.0 V"},
                        {"label": "First series resistor", "value": "2.00 kΩ"},
                        {"label": "First shunt", "value": "6.00 kΩ"},
                        {"label": "Second series resistor", "value": "2.00 kΩ"},
                        {"label": "Second shunt, at the probe", "value": "4.00 kΩ"},
                    ],
                    "aside": "Write down the running total at each node as you collapse inwards. "
                             "You need those numbers again on the way out, and re-deriving them is "
                             "where the arithmetic slips happen.",
                    "answer": 4.0,
                    "tol": 0.02,
                    "unit": "V",
                    # The probe is on the node the question asks about, so the check is the probed
                    # node and nothing else.
                    "check": "return c.vout();",
                    "hint": "Collapse from the far end: 4.0 kΩ, plus the 2.0 kΩ in front "
                            "of it, is 6.0 kΩ — which sits alongside the 6.0 kΩ shunt.",
                    "wrong": "If you got 5.00, the ladder has been treated as two dividers in a row, "
                             "each ignoring the one after it: $10.0 \\times 6/8 = 7.50$ V at the "
                             "first node, then $7.50 \\times 4/6 = 5.00$ V. The second rung loads "
                             "the first, so the first node is not at 7.50 V and never was. Leaving "
                             "the 6.0 kΩ shunt out altogether — three resistors in a row, "
                             "$10.0 \\times 4/8$ — gives 5.00 V as well, which is a coincidence of "
                             "these particular values rather than the same mistake twice. If you "
                             "got 6.00, that is the first node's voltage rather than the probed "
                             "one's.",
                    "why": r'''
```
INWARDS, from the far end, where nothing is unknown

    the 4.0 k shunt at the probe, alone           =  4.0 kohm
    + the 2.0 k series resistor in front of it    =  6.0 kohm
    that alongside the 6.0 k shunt:
        (6.0 * 6.0) / (6.0 + 6.0)                 =  3.0 kohm    <- first node's total
    + the 2.0 k series resistor in front of it    =  5.0 kohm    <- what the supply sees

OUTWARDS, using the totals just written down

    Itot   =  10.0 V / 5.0 kohm                   =  2.00 mA
    V(1st) =  2.00 mA * 3.0 kohm                  =  6.00 V
      the 6.0 k shunt takes 6.00/6.0k             =  1.00 mA
      so the second rung is fed with              =  1.00 mA
    V(probe) = 6.00 V - 1.00 mA * 2.0 kohm        =  4.00 V
      and the 4.0 k shunt carries 4.00/4.0k       =  1.00 mA    which closes KCL
```

4.00 V. Compare that with 5.00 V, which is what you get by treating the two rungs as
independent dividers, and 3.86 V, which is what the first rung would give on its own if
the second were not there at all. The true answer sits between them, and it has to: the
second rung loads the first (so the first node is below 7.50 V) but does not short it
(so it is above ground).

The current is the tidiest check here. 2.00 mA arrives, 1.00 mA goes down each of the
two shunts, and the second series resistor carries the 1.00 mA that the first shunt did
not take. Every one of those numbers is forced.
''',
                },
                {
                    "title": "Power in the middle of a three-rung ladder",
                    "minutes": 11,
                    "brief": r'''
Three rungs now, from a 22.0 V bench supply, and the question is not about a node
voltage at all. It asks how much power the **middle series resistor** — the 1.0 kΩ
between the first and second nodes — turns into heat.

Nothing new is needed. Collapse the ladder to find the supply current, walk back out to
the first node, split the current there, and the part of it that carries on is the
current through the resistor in question. Then $P = I^2R$.
''',
                    "prompt": "How much power does the 1.0 kΩ series resistor dissipate?",
                    "note": "Give the answer in milliwatts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 22},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "value": 4000},
                            {"id": "r2", "kind": "R", "x": 7, "y": 7, "rot": 1, "value": 10000},
                            {"id": "g1", "kind": "GND", "x": 7, "y": 10},
                            {"id": "r3", "kind": "R", "x": 10, "y": 4, "value": 1000},
                            {"id": "r4", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 8000},
                            {"id": "g2", "kind": "GND", "x": 11, "y": 10},
                            {"id": "r5", "kind": "R", "x": 14, "y": 4, "value": 2000},
                            {"id": "r6", "kind": "R", "x": 15, "y": 7, "rot": 1, "value": 6000},
                            {"id": "g3", "kind": "GND", "x": 15, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [7, 6]},
                            {"a": [7, 8], "b": [7, 10]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [11, 4], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 10]},
                            {"a": [11, 4], "b": [13, 4]},
                            {"a": [15, 4], "b": [15, 6]},
                            {"a": [15, 8], "b": [15, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "22.0 V"},
                        {"label": "Series resistors, in order", "value": "4.00 kΩ, 1.00 kΩ, 2.00 kΩ"},
                        {"label": "Shunts, in order", "value": "10.0 kΩ, 8.00 kΩ, 6.00 kΩ"},
                        {"label": "Asked for", "value": "power in the middle series resistor"},
                    ],
                    "aside": "Milliamps squared times kilohms comes out in milliwatts, with no "
                             "powers of ten to carry. It is worth working the whole ladder in those "
                             "units for that reason alone.",
                    "answer": 4.0,
                    "tol": 0.05,
                    "unit": "mW",
                    # Power is not a node of the circuit, so the check pulls the named resistor's
                    # own drop and value out of the solve and squares one over the other. Naming
                    # the part rather than a node means a re-drawn ladder is still measured on the
                    # element the prompt asks about.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r3'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
return drop * drop / r.value * 1000;
''',
                    "hint": "The supply current is not the answer's current. Find the first node's "
                            "voltage, take off what the 10 kΩ shunt draws, and what is left is "
                            "what flows through the 1.0 kΩ.",
                    "wrong": "If you got 9.00, the supply current of 3.00 mA has been used instead "
                             "of the 2.00 mA that actually reaches this resistor — the 10 "
                             "kΩ shunt takes the rest. If you got 2.00, the current has been "
                             "multiplied by the resistance rather than squared: that is the volts "
                             "across it, one step short of a power. And if you got 0.004, the "
                             "physics is right and the unit is not — that is the answer in watts, "
                             "and milliwatts were asked for.",
                    "why": r'''
```
INWARDS

    6.0 k shunt at the far node                    =  6.000 kohm
    + 2.0 k series                                 =  8.000 kohm
    alongside the 8.0 k shunt: (8*8)/16            =  4.000 kohm   <- 2nd node total
    + 1.0 k series                                 =  5.000 kohm
    alongside the 10 k shunt: (10*5)/15            =  3.333 kohm   <- 1st node total
    + 4.0 k series                                 =  7.333 kohm   <- supply sees this

OUTWARDS

    Itot     =  22.0 / 7.333k                      =  3.00 mA
    V(1st)   =  3.00 mA * 3.333 kohm               =  10.0 V
      the 10 k shunt takes 10.0/10k                =  1.00 mA
      so the 1.0 k series resistor carries         =  2.00 mA

and the power in it, in mA^2 * kohm, which is milliwatts:

    P        =  2.00^2 * 1.00                      =  4.00 mW
```

Worth checking against the drop: 2.00 mA through 1.00 kΩ is 2.00 V, and
$P = VI = 2.00 \times 2.00 = 4.00$ mW. The rest of the ladder, if you carry on, sits at
8.00 V and 6.00 V, and the whole thing dissipates
$36.0 + 10.0 + 4.00 + 8.00 + 2.00 + 6.00 = 66.0$ mW — which is
$22.0 \times 3.00 = 66.0$ mW out of the supply. That total is the check that catches an
error anywhere in the chain, and it costs one line.

Notice how little of the supply's power reaches the far end. The first series resistor
alone takes 36.0 mW of the 66.0 mW, more than half, because it carries every milliamp
the supply delivers. That is generally true of ladders and is why the first rung is the
one that gets hot.
''',
                },
                {
                    "title": "What must the supply be turned up to?",
                    "minutes": 13,
                    "brief": r'''
The same shape as before, but the question runs the other way. The supply in the drawing
is a bench unit, currently set to 9.00 V, and it is adjustable. At that setting the
4.0 kΩ at the far end of the ladder carries 0.600 mA, and the specification wants
**exactly 1.00 mA** in it.

You could collapse the whole ladder, find how the supply current divides at each of the
three nodes, and scale. It is less work to go the other way: start at the far branch
with the current you want, and walk *inwards*, adding up currents at each node and
voltages along each series resistor, until you arrive at the supply and read off what it
has to be.
''',
                    "prompt": "What must the supply be set to for the far branch to carry 1.00 mA?",
                    "note": "Give the answer in volts, to two decimal places. The drawing shows the "
                            "supply at its present setting, not the one you are looking for.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 7, "y": 7, "rot": 1, "value": 12000},
                            {"id": "g1", "kind": "GND", "x": 7, "y": 10},
                            {"id": "r3", "kind": "R", "x": 10, "y": 4, "value": 3000},
                            {"id": "r4", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 6000},
                            {"id": "g2", "kind": "GND", "x": 11, "y": 10},
                            {"id": "r5", "kind": "R", "x": 14, "y": 4, "value": 2000},
                            {"id": "r6", "kind": "R", "x": 15, "y": 7, "rot": 1, "value": 4000},
                            {"id": "g3", "kind": "GND", "x": 15, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 18, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [7, 6]},
                            {"a": [7, 8], "b": [7, 10]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [11, 4], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 10]},
                            {"a": [11, 4], "b": [13, 4]},
                            {"a": [15, 4], "b": [15, 6]},
                            {"a": [15, 8], "b": [15, 10]},
                            {"a": [15, 4], "b": [18, 4]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, present setting", "value": "9.00 V (adjustable)"},
                        {"label": "Series resistors, in order", "value": "1.00 kΩ, 3.00 kΩ, 2.00 kΩ"},
                        {"label": "Shunts, in order", "value": "12.0 kΩ, 6.00 kΩ, 4.00 kΩ"},
                        {"label": "Far branch carries now", "value": "0.600 mA"},
                        {"label": "Far branch must carry", "value": "1.00 mA"},
                    ],
                    "aside": "Working inwards, each node adds one current and each series resistor "
                             "adds one voltage drop. Nothing is ever unknown, because you are always "
                             "one Ohm's law away from the last number you wrote down.",
                    "answer": 15.0,
                    "tol": 0.1,
                    "unit": "V",
                    # The quantity asked for is the supply setting, which is not a reading of the
                    # circuit as drawn. Every resistor network with one source is linear in that
                    # source, so the check measures the far branch at the drawn setting and scales
                    # the drawn voltage by the ratio of wanted to measured current. Only the 1.00
                    # mA target is restated from the prompt; the rest comes out of the solve.
                    "check": r'''
const d = c.dc();
const last = c.net.parts.filter(function (p) { return p.id === 'r6'; })[0];
const inow = Math.abs(d.v[last.n1] - d.v[last.n2]) / last.value;
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const vnow = Math.abs(d.v[src.n1] - d.v[src.n2]);
return vnow * 0.00100 / inow;
''',
                    "hint": "1.00 mA in the 4.0 kΩ puts 4.00 V on the far node. The 2.0 "
                            "kΩ in front of it carries that same 1.00 mA, because there is "
                            "nothing between them to take any of it.",
                    "wrong": "If you got 5.00, that is the resistance of the whole ladder in "
                             "kilohms, which is a step along the way and not the answer. If you got "
                             "3.00, that is the supply current in milliamps at the setting asked "
                             "for. If you got 9.00, that is the setting the supply is on now, which "
                             "is what the drawing shows and what the question is asking you to "
                             "change.",
                    "why": r'''
```
INWARDS from the far branch, carrying the 1.00 mA that was asked for

    V(3rd node)  =  1.00 mA * 4.0 kohm            =   4.00 V
    the 2.0 k in front carries that same 1.00 mA, dropping 2.00 V
    V(2nd node)  =  4.00 + 2.00                   =   6.00 V
      the 6.0 k shunt there takes 6.00/6.0k       =   1.00 mA
      so the 3.0 k in front carries 1.00 + 1.00   =   2.00 mA, dropping 6.00 V
    V(1st node)  =  6.00 + 6.00                   =  12.00 V
      the 12 k shunt there takes 12.0/12k         =   1.00 mA
      so the 1.0 k at the top carries 2.00 + 1.00 =   3.00 mA, dropping 3.00 V
    supply       =  12.00 + 3.00                  =  15.00 V
```

15.0 V. Every line of that is one application of Ohm's law or one addition at a node,
and at no point was anything unknown — which is the advantage of working inwards when
the far-end current is what you have been given.

The forwards route gets there too, with more effort. Collapse the ladder:
$4 + 2 = 6$, $6 \parallel 6 = 3$, $3 + 3 = 6$, $6 \parallel 12 = 4$, $4 + 1 = 5$ kΩ. At
each node the fraction of the arriving current that carries on is the shunt over the
sum, so $2/3$ at the first node and $1/2$ at the second: the far branch gets
$\tfrac{2}{3}\times\tfrac{1}{2} = \tfrac{1}{3}$ of the supply current. Wanting 1.00 mA
there means 3.00 mA from the supply, and $3.00\text{ mA} \times 5.0\text{ k}\Omega =
15.0$ V.

There is also a one-line route, and it is the reason bench work goes quickly: this
circuit contains one source and nothing but resistors, so every current in it is
proportional to that source. 0.600 mA at 9.00 V, so
$9.00 \times 1.00/0.600 = 15.0$ V. That proportionality has a name — linearity — and a
later module builds superposition on top of it.
''',
                },
            ],
            "blanks": [
                {
                    "title": "Four branches, and no formula for them",
                    "minutes": 9,
                    "caption": "one junction, four ways down, and the conductance route through it",
                    "lang": "text",
                    "brief": r'''
Four branches is where the two-resistor formula stops being any help at all, and where
people reach for it hardest. The route below never touches it: conductances, then the
one voltage they all share, then Ohm's law on each branch in turn. It is the same number
of lines whether there are two branches or twenty.

Fill the six holes in order. Each one is one step from the lines above it.
''',
                    "listing": r'''
24.0 mA arrives at one node.  Four resistors run from it down to
ground: 1.0 kohm, 2.0 kohm, 3.0 kohm and 6.0 kohm.
------------------------------------------------------------------

  there is no four-resistor version of R2/(R1+R2), and inventing one
  is where the errors come from.  Work in conductance instead:
  parallel branches ADD conductance, and 1 mS is 1/(1 kohm)

    G1  =  1/1.0k   =  1.000 mS
    G2  =  1/2.0k   =  0.500 mS
    G3  =  1/3.0k   =  ___ mS
    G4  =  1/6.0k   =  0.167 mS
                       ---------
    Gtot            =  ___ mS      ->  Rpar = 1/Gtot = ___ ohm

  every branch has the same voltage across it, and that voltage is
  the whole arriving current through the parallel combination

    V     =  24.0 mA * Rpar                        =  ___ V

  now each branch on its own, by Ohm's law

    I1    =  V / 1.0 kohm                          =  ___ mA
    I2    =  V / 2.0 kohm                          =  6.00 mA
    I3    =  V / 3.0 kohm                          =  4.00 mA
    I4    =  V / 6.0 kohm                          =  2.00 mA
             ------------------------------------------------
             and these must add back to the 24.0 mA that arrived

  a branch's share of the current is its share of the conductance,
  and nothing else about it counts

    I4 / 24.0 mA  =  G4 / Gtot  =  0.167 / 2.000   =  ___ %
''',
                    "blanks": [
                        {
                            "prompt": "The conductance of 3.0 kΩ, in millisiemens.",
                            "hole": "?",
                            "opts": ["0.333", "3.000", "0.167", "0.500"],
                            "a": 0,
                            "why": "$1/3000 = 3.33\\times10^{-4}$ S, which is 0.333 mS. The value "
                                   "3.000 is the resistance in kilohms copied across without being "
                                   "inverted, and it points the wrong way: more resistance must "
                                   "mean *less* conductance. The value 0.167 belongs to the 6.0 kΩ "
                                   "and 0.500 to the 2.0 kΩ, both of which are already on the page.",
                        },
                        {
                            "prompt": "The four conductances added, in millisiemens.",
                            "hole": "?",
                            "opts": ["2.000", "1.000", "12.00", "0.083"],
                            "a": 0,
                            "why": "$1.000 + 0.500 + 0.333 + 0.167 = 2.000$ mS. The value 1.000 is "
                                   "the largest branch on its own, which would be the answer only "
                                   "if the other three were not fitted — every extra branch adds "
                                   "conductance and can only push this number up. The value 12.00 "
                                   "is the four resistances added in kilohms, which is the series "
                                   "rule and the wrong circuit entirely.",
                        },
                        {
                            "prompt": "The parallel resistance, $1/G_\\text{tot}$, in ohms.",
                            "hole": "?",
                            "opts": ["500", "0.5", "12000", "1000"],
                            "a": 0,
                            "why": "$1/(2.000\\times10^{-3}) = 500\\ \\Omega$. The value 0.5 is that "
                                   "same reciprocal left in kilohms and then labelled ohms — a "
                                   "factor of a thousand, and the commonest slip in the whole "
                                   "method. The value 1000 is the smallest branch, and the answer "
                                   "must come out *below* it: a parallel combination is always "
                                   "smaller than its smallest part, because every branch is an "
                                   "extra way through.",
                        },
                        {
                            "prompt": "24.0 mA through 500 Ω. What voltage do the branches share?",
                            "hole": "?",
                            "opts": ["12.0", "48.0", "0.012", "24.0"],
                            "a": 0,
                            "why": "$0.0240 \\times 500 = 12.0$ V. The value 48.0 uses 2000 Ω "
                                   "instead of 500 — that is $1/G$ for one branch rather than for "
                                   "all four together. The value 0.012 is the same arithmetic with "
                                   "the 500 Ω taken as 0.5, which is kilohms wearing an ohms label.",
                        },
                        {
                            "prompt": "12.0 V across the 1.0 kΩ branch. How many milliamps?",
                            "hole": "?",
                            "opts": ["12.0", "2.0", "6.0", "24.0"],
                            "a": 0,
                            "why": "$12.0/1000 = 0.0120$ A. Half of everything that arrived goes "
                                   "down this one branch, because it holds half of the 2.000 mS. "
                                   "The value 2.0 is $24.0 \\times 1.0/12.0$ — the branch's own "
                                   "resistance over the sum of the resistances, which is the "
                                   "voltage-divider fraction used on a current, and it hands the "
                                   "smallest resistor the smallest share. The value 24.0 is the "
                                   "whole arriving current, which would need the other three "
                                   "branches to be carrying nothing.",
                        },
                        {
                            "prompt": "What percentage of the 24.0 mA goes down the 6.0 kΩ?",
                            "hole": "?",
                            "opts": ["8.33", "50.0", "16.7", "25.0"],
                            "a": 0,
                            "why": "$0.167/2.000 = 0.0833$, and $2.00/24.0$ agrees. The value 50.0 "
                                   "is this branch's share of the summed *resistances*, "
                                   "$6.0/12.0$ — the voltage-divider fraction turned on a current, "
                                   "and it awards the largest resistor the largest share, which is "
                                   "backwards. The value 16.7 is the 2.00 mA taken as a fraction of "
                                   "the 12.0 mA in the 1.0 kΩ rather than of the 24.0 mA that "
                                   "arrived. The value 25.0 would be right if the four branches "
                                   "were equal, and they are not.",
                        },
                    ],
                },
                {
                    "title": "A ladder, collapsed and then walked back out",
                    "minutes": 10,
                    "caption": "two rungs, inwards from the far end and then outwards again",
                    "lang": "text",
                    "brief": r'''
The full method on the smallest ladder worth the name. Inwards first, because the far
end is the only place with nothing beyond it; then outwards, reusing the running totals
written down on the way in. The lines are short because every one of them is a single
application of Ohm's law or a single addition at a node.

Six holes. Two of them are traps that a divider-shaped instinct walks straight into.
''',
                    "listing": r'''
15.0 V rail.  Along the top: 5.0 kohm to node B, then 2.0 kohm to
node C.  Down to ground: 5.0 kohm at B, 3.0 kohm at C.
-------------------------------------------------------------------

  INWARDS.  Start at the far end, because it is the only place in
  the circuit with nothing beyond it to know about.

    at C, looking right: the 3.0 k shunt, alone       =  3.0 kohm
    + the 2.0 k series resistor in front of it        =  ___ kohm
    that alongside B's 5.0 k shunt:
        (5.0 * 5.0) / (5.0 + 5.0)                     =  2.5 kohm
    + the 5.0 k series resistor in front of it        =  ___ kohm   <- Rtot

  OUTWARDS.  One node at a time, reusing the totals above.

    Itot   =  15.0 V / Rtot                           =  ___ mA
    V(B)   =  Itot * 2.5 kohm                         =  ___ V

  split the current at B: the shunt takes its share, the rest
  carries on down the ladder

    I(shunt at B)  =  V(B) / 5.0 kohm                 =  1.00 mA
    I(on into C)   =  Itot - 1.00 mA                  =  ___ mA
    V(C)           =  V(B) - I(on into C) * 2.0 kohm  =  ___ V

  and the check, which costs one division: the 3.0 k shunt at C
  carries V(C)/3.0k, and there is nowhere else that current can have
  come from, so it has to equal I(on into C).
''',
                    "blanks": [
                        {
                            "prompt": "3.0 kΩ with a 2.0 kΩ in series in front of it. How many kilohms?",
                            "hole": "?",
                            "opts": ["5.0", "1.2", "6.0", "1.5"],
                            "a": 0,
                            "why": "In series they add: $3.0 + 2.0 = 5.0$ kΩ. The value 1.2 is the "
                                   "parallel combination, and these two are not in parallel — they "
                                   "share one node, not two, and the same current has to pass "
                                   "through both. The value 6.0 is the product, which is only half "
                                   "of the parallel rule and is not a resistance of anything.",
                        },
                        {
                            "prompt": "2.5 kΩ with a 5.0 kΩ in series in front of it. How many kilohms does the rail see?",
                            "hole": "?",
                            "opts": ["7.5", "2.5", "1.67", "10.0"],
                            "a": 0,
                            "why": "$2.5 + 5.0 = 7.5$ kΩ, and that is the last step of the collapse "
                                   "— there is nothing left to combine. The value 1.67 treats the "
                                   "series resistor as another parallel branch. The value 10.0 adds "
                                   "the two 5.0 kΩ resistors and forgets that the 2.0 k and 3.0 k "
                                   "beyond node B are part of what the rail is driving.",
                        },
                        {
                            "prompt": "15.0 V across 7.5 kΩ. How many milliamps does the rail deliver?",
                            "hole": "?",
                            "opts": ["2.00", "6.00", "3.00", "1.00"],
                            "a": 0,
                            "why": "$15.0/7500 = 2.00$ mA. The value 6.00 divides by 2.5 kΩ, which "
                                   "is what hangs off node B rather than what the rail sees — the "
                                   "5.0 kΩ in front of it has been left out. The value 3.00 divides "
                                   "by the 5.0 kΩ series resistor alone, as though the rest of the "
                                   "ladder were a short to ground.",
                        },
                        {
                            "prompt": "2.00 mA arriving at node B, with 2.5 kΩ hanging off it. What is V(B)?",
                            "hole": "?",
                            "opts": ["5.00", "7.50", "10.0", "2.50"],
                            "a": 0,
                            "why": "$2.00\\text{ mA} \\times 2.5\\text{ k}\\Omega = 5.00$ V, and "
                                   "$15.0 - 5.00 = 10.0$ V is left across the 5.0 kΩ above it, "
                                   "which is the same answer arrived at from the other end. The "
                                   "value 7.50 is $15.0 \\times 5/10$: the top pair treated as a "
                                   "divider on its own, with the second rung ignored. It is the "
                                   "single commonest error in ladder work and it always errs high, "
                                   "because whatever hangs beyond a node can only pull that node "
                                   "down. The value 10.0 is the drop across the 5.0 kΩ, which is "
                                   "the other part of the 15.0 V.",
                        },
                        {
                            "prompt": "2.00 mA arrives at B and 1.00 mA turns down the shunt. How much carries on?",
                            "hole": "?",
                            "opts": ["1.00", "2.00", "3.00", "0.50"],
                            "a": 0,
                            "why": "$2.00 - 1.00 = 1.00$ mA. This is Kirchhoff's current law and "
                                   "nothing more: what arrives leaves, by one route or the other. "
                                   "The value 2.00 would mean the shunt carries nothing, and it has "
                                   "5.00 V across it. The value 3.00 has the two currents added "
                                   "rather than one taken from the other, which would have the "
                                   "ladder manufacturing current at a node.",
                        },
                        {
                            "prompt": "5.00 V at B, and 1.00 mA down through the 2.0 kΩ. What is V(C)?",
                            "hole": "?",
                            "opts": ["3.00", "4.50", "2.00", "5.00"],
                            "a": 0,
                            "why": "$5.00 - 1.00\\text{ mA} \\times 2.0\\text{ k}\\Omega = 3.00$ V, "
                                   "and the 3.0 kΩ shunt at C then carries $3.00/3.0\\text{k} = "
                                   "1.00$ mA, which is exactly what arrived — so the accounting "
                                   "closes. The value 4.50 comes from cascading dividers: 7.50 V at "
                                   "B, then $7.50 \\times 3/5$. Both of its numbers are wrong and "
                                   "they are wrong in the same direction. The value 2.00 is the "
                                   "drop across the 2.0 kΩ, not the voltage left at the far end.",
                        },
                    ],
                },
            ],
            "derive": {
                "title": "Where the current-divider formula comes from",
                "minutes": 11,
                "vars": ["I_t", "I_1", "I_2", "V", "R_1", "R_2"],
                "brief": r'''
A total current $I_t$ arrives at a node, divides between $R_1$ and $R_2$, and the two
branches rejoin at a second node. Both resistors therefore have the same voltage $V$
across them, and that single fact is the whole derivation — the rest is
substitution.

Find $I_1$, the current through $R_1$, in terms of $I_t$, $R_1$ and $R_2$.
''',
                "steps": [
                    {
                        "prompt": "Write $I_1$, the current through $R_1$, in terms of $V$ and $R_1$.",
                        "answer": "\\frac{V}{R_1}",
                        "hint": "Ohm's law, using the voltage the two branches share.",
                    },
                    {
                        "prompt": "Everything arriving at the node leaves through one branch or the other. Write $I_t$ in terms of $V$, $R_1$ and $R_2$.",
                        "answer": "\\frac{V}{R_1}+\\frac{V}{R_2}",
                        "hint": "That is KCL at the top node, with each branch current written by Ohm's law.",
                    },
                    {
                        "prompt": "Rearrange that for $V$, in terms of $I_t$, $R_1$ and $R_2$.",
                        "answer": "\\frac{I_t R_1 R_2}{R_1 + R_2}",
                        "hint": "Take $V$ out as a common factor, then divide by what is left. What multiplies $I_t$ should look familiar.",
                        "deconstruct": [
                            "$I_t = V\\left(\\frac{1}{R_1}+\\frac{1}{R_2}\\right)$, and the bracket is $\\frac{R_1+R_2}{R_1R_2}$.",
                            "So $V = I_t\\,\\frac{R_1R_2}{R_1+R_2}$ — the total current times the parallel resistance, which is exactly what it ought to be.",
                        ],
                    },
                    {
                        "prompt": "Substitute that back into your first line to get $I_1$ in terms of $I_t$, $R_1$ and $R_2$.",
                        "answer": "\\frac{I_t R_2}{R_1 + R_2}",
                        "hint": "Divide the expression for $V$ by $R_1$, and watch one of the two resistances cancel.",
                        "deconstruct": [
                            "$I_1 = V/R_1 = \\frac{I_t R_1 R_2}{R_1(R_1+R_2)}$.",
                            "The $R_1$ on the top cancels the one you have just divided by, and $R_2$ is what is left upstairs.",
                        ],
                    },
                ],
                "closing": r'''
$R_2$ on top, in the expression for the current through $R_1$. That is not a slip and
it is not arbitrary: $R_1$ appeared twice — once in the shared voltage and once in
Ohm's law for its own branch — and the two occurrences cancelled. Repeating the
argument for $I_2$ gives the mirror image, and adding the two together returns $I_t$,
which is worth doing once as a check that nothing has been dropped.
''',
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Real sources: internal resistance and what a cell can deliver",
            "summary": "An ideal source is a fiction with one number in it. A real one needs two, and the second explains almost everything a battery does.",
            "concepts": [
                "An ideal voltage source holds its voltage at any current at all. Taken literally that means a short circuit across it draws infinite current, which is the tell that no such thing exists.",
                "A real source is modelled as an ideal EMF $E$ in series with an internal resistance $r$. Those two numbers capture everything the source does at its terminals at DC — from outside there is nothing else to know.",
                "The terminal voltage therefore falls as more current is drawn: $V_t = E - Ir$. Open circuit, $I = 0$ and the terminals read $E$; short circuit, the current is $E/r$ and the terminals read zero.",
                "This is why a voltmeter across a flat AA still reads 1.5 V while the torch is dim. A meter draws almost no current, so it measures $E$ and never sees $r$; the lamp draws hundreds of milliamps and sees nothing else.",
                "An ideal current source is the mirror image: it holds its current at any voltage, and a real one is that ideal with a resistance in parallel.",
                "Source transformation: an EMF $E$ in series with $r$, and a current source $E/r$ in parallel with the same $r$, are indistinguishable from the terminals. Every measurement you can make gives the same answer, so you may swap one for the other whenever it makes the arithmetic easier.",
                "Internal resistance sets every practical limit a source has: how much current it can give, how far it sags when a motor starts, and how much of its stored energy goes into heating itself rather than the load.",
                "It also sets a ceiling nothing can lift: the most power a source of EMF $E$ and internal resistance $r$ can put into any load is $E^2/4r$, reached when the load equals $r$ — and at that point exactly half of what the source produces is heating the source.",
            ],
            "read": [
                {
                    "title": "Why nothing holds its voltage",
                    "minutes": 17,
                    "body": r'''
Take a torch with tired batteries into a dark room and you already know the whole of
this module. The lamp is orange rather than white. Switch it off, put a multimeter
across the cells, and the meter says 1.5 V a cell — exactly what it said when they were
new. Switch the lamp back on with the meter still connected and watch the reading fall
to 1.1 V and stay there. Nothing was replaced, nothing was adjusted, and the same two
cells now have two different voltages depending on whether anything is drawing current
from them.

Every source does this. The bench supply in the lab does it by a few millivolts, a car
battery does it by two volts while the starter turns, and a coin cell driving a radio
does it so violently that the radio resets. The ideal voltage source of the last five
modules — the one that holds its stated voltage whatever the circuit asks for — does not
exist and never did. This reading is about what to put in its place.

## Take the ideal source literally and it breaks

The fastest way to see that something is missing is to push the ideal model until it
says something absurd. An ideal 1.5 V source holds 1.5 V across its terminals for any
current at all. Join the terminals with a thick wire, so that the resistance of the
external circuit is essentially zero, and Ohm's law gives

$$I = \frac{V}{R} = \frac{1.5}{0} = \infty$$

Infinite current, infinite power, from a cell you can hold between two fingers. That
does not happen. A shorted AA gives a few amps, gets hot, and after a while gives less.
Something in the circuit is limiting the current, and since the external resistance is
as close to zero as copper can make it, the limit has to be **inside the cell**.

## What is actually inside

A cell is not a reservoir of electrons with a tap on it. It is two electrodes in an
electrolyte, and the chemistry at each electrode surface is what sets the voltage. But
for a current to flow round the external circuit, the same current has to cross from one
electrode to the other *inside* the cell, and inside there are no free electrons to carry
it. The carriers there are ions: whole atoms or molecular groups, thousands of times
heavier than an electron, shouldering their way through a liquid or a paste.

That is a lousy conductor, and it is not the only obstacle. The chemical reaction at each
electrode surface takes a finite push to run at a finite rate, so drawing more current
costs more voltage there too. Add the resistance of the metal current collectors, the
tabs, the welds and the terminals, and the cell has several quite different mechanisms
that all do the same thing: they eat some of the voltage in proportion to how much
current you take.

Every one of those is a voltage lost that grows with current. From outside the case, you
cannot tell them apart and you have no reason to want to.

## Two numbers, because a straight line has two

Here is the argument that makes the model inevitable rather than arbitrary. Forget the
chemistry and treat the cell as a sealed box with two terminals. Hang loads of various
sizes on it, and for each one write down the current $I$ you drew and the voltage $V_t$
you measured. Plot $V_t$ against $I$.

For any cell that is not being abused, that plot is a straight line, sloping down. It has
an intercept — the voltage when $I = 0$ — and it has a slope, in volts per amp, which is
to say in ohms. Two numbers fix a straight line, and a straight line is all the box does.
So a model with two numbers in it is not a simplification of the cell; it is a complete
description of everything the terminals can ever do at DC.

The two numbers get names. The intercept is the **EMF**, written $E$: the voltage the
cell would produce if nothing were connected. The slope is the **internal resistance**,
written $r$. And the equation of the line is

$$V_t = E - Ir$$

which reads: the terminals give you the EMF, less whatever gets eaten on the way out. On
a schematic that is drawn as an ideal source of $E$ in series with a resistor of $r$,
because a resistor is the only component whose voltage grows in proportion to its
current. The drawing is a picture of the equation, not a picture of the cell.

Two things about that drawing are worth saying out loud, because both trip people up.
First, the node between $E$ and $r$ does not exist. It is inside the case; there is no
point on the cell you could touch a probe to and read $E$ while current is flowing.
Second, $r$ is not a component. Nobody put it there and nobody can take it out. It is a
slope, drawn as a resistor because the drawing has to be made of something.

## The two extremes, which you can now read straight off

Set $I = 0$ in the equation and $V_t = E$. That is the open-circuit voltage, and it is why
a voltmeter — which draws a microamp or less — reads the EMF and never sees $r$ at all.
It is also why a voltmeter is nearly useless for judging a battery.

Set $V_t = 0$, which is what a short circuit forces, and $I = E/r$. That is the
**short-circuit current**, and it is the largest current the cell can produce. Not
infinite. For a fresh AA with $r$ around 0.15 Ω, about 10 A; for a car battery with $r$
around 5 mΩ, about 2500 A, which is why a spanner dropped across one glows.

## Worked: finding both numbers from two loads

This is the standard bench measurement, and it needs nothing but a resistor, a meter, and
the fact that the graph is a line. A cell of unknown age is loaded twice.

```text
    with a 3.60 ohm load:      the meter reads   1.44 V
    with a 1.20 ohm load:      the meter reads   1.20 V

each reading is a point on the line, so turn each one into a current
first, using Ohm's law on the load, which is the part you know

    I(1)   =  1.44 / 3.60                        =  0.400 A
    I(2)   =  1.20 / 1.20                        =  1.000 A

the slope of the line is then rise over run, and the rise is negative
because the voltage falls as the current grows

    r      =  (1.44 - 1.20) / (1.000 - 0.400)
           =  0.24 / 0.600                       =  0.400 ohm

and E is either reading with its own lost volts added back on

    E      =  1.44 + 0.400 * 0.400               =  1.60 V
    check  =  1.20 + 1.000 * 0.400               =  1.60 V
```

Both readings give the same EMF, which is the check that the line really was a line. The
cell is a 1.60 V EMF behind 0.400 Ω, and from those two numbers everything else follows
without touching it again. Load it with 0.600 Ω and

```text
    I      =  1.60 / (0.400 + 0.600)             =  1.600 A
    Vt     =  1.600 * 0.600                      =  0.96 V

    P(load)  =  1.600^2 * 0.600                  =  1.536 W
    P(cell)  =  1.600^2 * 0.400                  =  1.024 W
                                                    ---------
    P(EMF)   =  1.60 * 1.600                     =  2.560 W
```

The terminals have fallen to 0.96 V — from an EMF of 1.60 V — and the cell is turning
1.024 W into heat inside its own case. That is a cell being ruined, and the arithmetic
said so before anything got warm.

## Worked: why the dashboard lights dim when you crank

A car battery is the same model with the decimal points moved. Take a healthy one at
$E = 12.6$ V with $r = 10.0$ mΩ, and a starter motor that looks, while it is turning,
like 50.0 mΩ.

```text
    I      =  12.6 / (0.0100 + 0.0500)           =  210 A
    Vt     =  210 * 0.0500                       =  10.50 V
    lost inside the battery  =  210 * 0.0100     =   2.10 V

    P(starter) =  210^2 * 0.0500                 =  2205 W
    P(battery) =  210^2 * 0.0100                 =   441 W
                                                    -------
    P(EMF)     =  12.6 * 210                     =  2646 W
```

The whole car's electrical system is sitting on those terminals, and while the starter
turns they are at 10.50 V, not 12.6 V. Headlamps are close to resistive once hot, so
their power falls as the square of the voltage: a factor of $(10.50/12.6)^2 = 0.694$,
losing nearly a third. The filament's light output falls faster still, which is why the
dip is so obvious.

Now let the battery age until $r$ has risen to 50.0 mΩ. Nothing else changes — the
chemistry still makes 12.6 V, and a voltmeter across it still reads 12.6 V.

```text
    I      =  12.6 / (0.0500 + 0.0500)           =  126 A
    Vt     =  126 * 0.0500                       =   6.30 V

    P(starter) =  126^2 * 0.0500                 =  793.8 W
    P(battery) =  126^2 * 0.0500                 =  793.8 W
```

The starter now gets 793.8 W instead of 2205 W — 36% of what it had — and the battery is
heating itself just as hard as it is turning the engine. The terminals collapse to 6.30 V,
which is below what the engine management electronics need, so the dashboard goes dark
and the engine turns over slowly or not at all. Every symptom of a failing battery is in
those six lines, and the open-circuit voltage predicted none of them.

## The mistake everyone makes

**Judging a battery with a voltmeter.** It is the natural thing to do, the meter is right
there, and the reading is reassuringly close to the number printed on the case. But an
open-circuit measurement is a measurement of $E$ alone, and $E$ is the number that barely
changes: the failing car battery above reads exactly what the good one reads. What went
wrong was $r$, and $r$ is invisible unless current is flowing. A battery is tested under
load, always, and a load tester is nothing more than a big resistor and a voltmeter doing
the two-point measurement above.

The reason the mistake is so durable is that the meter is not lying. It is answering a
different question from the one being asked — "what is the EMF?" rather than "what will
this do when something needs it?" — and answering it correctly.

**Subtracting $Ir$ from the wrong voltage.** The equation is $V_t = E - Ir$, and $E$ is
the open-circuit value. Starting from a terminal voltage that has already sagged and
taking another $Ir$ off it counts the same loss twice. If the number in front of you came
off a meter with the load connected, it is $V_t$ and the subtraction has already
happened.

**Treating the terminal voltage as a property of the cell.** It is a property of the cell
*and the load together*. "The battery is at 10.5 V" is only meaningful alongside "while
delivering 210 A".

## Where the model stops holding

The whole of the above rests on that plot being a straight line, with $E$ and $r$ fixed.
Four things break it, in the order you are likely to meet them.

**$r$ is not a constant.** It rises as the cell discharges, and it rises steeply in the
cold — a lead-acid battery near freezing has roughly double the internal resistance it has
in a warm garage, and less usable charge besides, which is why cars fail to start on the
first frost rather than on the last warm day. Quote an $r$ without a temperature and a
state of charge and you have quoted almost nothing.

**$E$ is not a constant either.** It falls as the cell empties. Over a discharge it is the
slow drift; over the seconds a measurement takes, it is fixed, which is what makes the
two-point method work at all — take the two readings minutes apart and you are fitting a
line to a moving target.

**The cell has a memory.** Take the load off a flattened cell, wait ten minutes, and the
terminal voltage climbs back up on its own. Nothing in $V_t = E - Ir$ can do that: it has
no time in it. What is happening is that concentration gradients built up in the
electrolyte during the discharge are relaxing away. Modelling that needs resistors *and*
capacitors — a chain of R–C pairs across the terminals — and that is the model battery
engineers actually use. Direct current analysis is the limit of it after everything has
settled.

**Some sources are not one straight line but two.** A regulated bench supply has an
effective $r$ of a few milliohms, so it looks very nearly ideal — right up to the current
limit, where it stops holding its voltage and starts holding its current instead. Past
that knee it is a different model entirely, the one the next reading is about, and no
single value of $r$ describes both halves.

None of that makes $E$ and $r$ wrong. It makes them a *description of an operating
point*: this cell, at this temperature, at this state of charge, over this range of
currents. Within that box the two numbers tell you everything, and the rest of this module
is what you can do with them.
''',
                },
                {
                    "title": "Two forms of one source, and the ceiling on what it can deliver",
                    "minutes": 18,
                    "body": r'''
The last reading built a source out of an EMF and a series resistance. There is a second
way to build exactly the same thing, it looks nothing like the first, and no measurement
you can make at the terminals will tell them apart. That sounds like a curiosity. It is
not: it is the single most useful piece of bookkeeping in circuit analysis, and it is
what lets you put two batteries in parallel and still get an answer.

## A source that holds its current instead

Start with something that behaves the wrong way round. A solar cell in bright sun,
short-circuited, delivers a current set by how many photons are landing on it. Open its
terminals and the voltage rises to some limit and stops. Between those extremes, over a
wide range of loads, the *current* is what stays put while the voltage does as it is told
— the exact inverse of a battery.

Photodiodes do it, transistor current mirrors do it deliberately, and a bench supply does
it the moment you hit the current limit knob. So the idealisation is worth having: an
**ideal current source** pushes its stated current through whatever is connected, and
produces whatever voltage that requires. Connect 1 mA to 1 kΩ and it makes 1 V; connect
the same source to 1 MΩ and it makes 1000 V; leave it open-circuit and, taken literally,
it makes infinity — which is the same tell as a shorted ideal voltage source, and gets the
same fix. A real current source is an ideal one with a resistance **in parallel**, giving
the current somewhere else to go.

## The same line, written the other way up

Now the reason the two models are the same model. The series form obeys

$$V_t = E - Ir$$

Rearrange it for $I$, which is only algebra:

$$I = \frac{E}{r} - \frac{V_t}{r}$$

Read that as a circuit description rather than as algebra. It says: a fixed current of
$E/r$ is available, and whatever voltage appears at the terminals diverts $V_t/r$ of it
somewhere else — which is precisely a current source of $E/r$ with a resistance $r$
across it. The load gets what is left.

So the two forms are one straight line written twice, and the translation is

$$I_N = \frac{E}{r}\,, \qquad r \text{ unchanged}$$

$I_N$ is the short-circuit current, which the last reading already identified as $E/r$;
and going the other way, $E = I_N r$ is the open-circuit voltage of the parallel form,
because with the terminals open all of $I_N$ has nowhere to go but through $r$. Two points
agree, both forms are straight lines, and two points fix a line. Nothing else needs
checking.

## Worked: the same source twice

Take a 12.0 V source behind 4.00 Ω, driving a 6.00 Ω load, and then its transform.

```text
SERIES FORM: 12.0 V in series with 4.00 ohm

    I      =  12.0 / (4.00 + 6.00)               =  1.20 A
    Vt     =  1.20 * 6.00                        =  7.20 V

PARALLEL FORM: 12.0/4.00 = 3.00 A in parallel with 4.00 ohm

    Rpar   =  (4.00 * 6.00) / (4.00 + 6.00)      =  2.40 ohm
    Vt     =  3.00 * 2.40                        =  7.20 V
    I(load)=  7.20 / 6.00                        =  1.20 A
```

Identical, and they stay identical for every load you try, because both are the same line.
Change the 6.00 Ω to 24.0 Ω and the series form gives $12.0/28.0 = 0.4286$ A and 10.29 V;
the parallel form gives $4.00 \parallel 24.0 = 3.429$ Ω, times 3.00 A, which is 10.29 V
again.

## Worked: two batteries in parallel

Here is the transformation earning its keep. Two 12 V batteries are wired in parallel in a
boat, one newer than the other, feeding a load of 1.15 Ω. Battery A is 12.0 V behind
0.200 Ω; battery B is 11.0 V behind 0.200 Ω.

In the series form this is nasty: two voltage sources facing each other with resistances
between, and no two components in the circuit are in series or in parallel. Transform both
and it collapses.

```text
    battery A  ->  12.0 / 0.200  =  60.0 A  parallel with 0.200 ohm
    battery B  ->  11.0 / 0.200  =  55.0 A  parallel with 0.200 ohm

both now hang between the same two nodes, so the current sources add
and the resistances combine as a parallel pair

    I(N)   =  60.0 + 55.0                        =  115.0 A
    r      =  0.200 / 2                          =  0.100 ohm

and turning that back into a series source gives one battery that
behaves exactly like the pair

    E      =  115.0 * 0.100                      =  11.50 V
    r      =                                        0.100 ohm

now the load, which is an ordinary two-resistor problem again

    I      =  11.50 / (0.100 + 1.15)             =  9.20 A
    Vt     =  9.20 * 1.15                        =  10.58 V
```

And now the part worth pausing on. Go back to the two batteries and ask what each is
actually contributing, using $I = (E - V_t)/r$ on each:

```text
    battery A  =  (12.0 - 10.58) / 0.200         =  7.10 A
    battery B  =  (11.0 - 10.58) / 0.200         =  2.10 A
                                                    -------
                                                    9.20 A   as it must
```

The two are nominally the same battery, wired identically, with identical internal
resistances — and one is doing more than three times the work of the other. Worse, ease
the load off. As the load current falls the terminal voltage rises, and when it reaches
11.0 V — which happens at a load of 2.20 Ω, drawing 5.00 A — battery B contributes exactly
nothing. Lighten the load further and $(E_B - V_t)$ goes negative: the good battery is now
pushing current *into* the tired one. That is why paralleling mismatched batteries is a
bad idea, and the calculation above is the whole of the reason.

## The ceiling: how much can a source deliver?

A source has $E$ and $r$, both fixed. You get to choose the load $R$. How much power can
you get into it?

Two limits answer themselves. Make $R$ enormous and the terminal voltage is nearly $E$,
but the current is nearly nothing, so the power is nearly nothing. Make $R$ nearly zero
and the current is nearly $E/r$, the most there is, but the voltage across the load is
nearly nothing, so again the power is nearly nothing. Between two zeros there is a
maximum, and it is worth finding exactly where.

$$P = I^2 R = \frac{E^2 R}{(R+r)^2}$$

Differentiate with respect to $R$, using the quotient rule, and factor $(R+r)$ out of the
top:

$$\frac{dP}{dR} = E^2\,\frac{(R+r)^2 - R\cdot 2(R+r)}{(R+r)^4}
 = E^2\,\frac{(R+r) - 2R}{(R+r)^3} = E^2\,\frac{r-R}{(R+r)^3}$$

The denominator is positive for any sensible resistance, so the sign of the whole thing is
the sign of $r - R$: the power is climbing while $R < r$, falling once $R > r$, and
stationary exactly at

$$R = r\,, \qquad P_{max} = \frac{E^2 r}{(2r)^2} = \frac{E^2}{4r}$$

A source cannot be persuaded to give more than $E^2/4r$ to anything, ever. That is not a
property of the load; it is a ceiling set by the two numbers inside the source.

Put the tired car battery from the last reading through it — $E = 12.6$ V, $r = 50.0$ mΩ:

```text
   R (ohm)      I (A)      Vt (V)     P(load) (W)    efficiency
   ------------------------------------------------------------
   0.0125       201.6      2.520          508.0          20.0 %
   0.0250       168.0      4.200          705.6          33.3 %
   0.0500       126.0      6.300          793.8          50.0 %
   0.1000        84.0      8.400          705.6          66.7 %
   0.2000        50.4      10.08          508.0          80.0 %
```

The peak really is at $R = r$, and $E^2/4r = 158.76/0.200 = 793.8$ W agrees with the table.
Notice the symmetry: 0.0125 Ω and 0.200 Ω give the same power, as do 0.0250 Ω and
0.100 Ω. Loads that are the same factor either side of $r$ deliver the same power, so the
peak is a broad one — being a factor of two away from the match costs only 11%.

The efficiency column is the sting. It is $\eta = R/(R+r)$, since the same current passes
through both resistances and the power divides in proportion to them. At the matched load
it is exactly 50%: for every watt into the load, a watt heats the source.

## The mistake, and why it is tempting

**"Always match the load to the source."** It gets repeated as though it were a design
rule, and it is a design rule — for a narrow case. Match when the source's power is fixed
and pitifully small and you want as much of it as you can get: an antenna, a microphone
capsule, a photodiode, a thermocouple. There, throwing half of it away in the source is
the price of getting the other half.

Now apply it to a power station. Matching would mean building the transmission network so
that its resistance equalled the generator's, and burning half the national electricity
supply inside the generators. Nobody does this. Where power is plentiful and paid for, you
want efficiency, and efficiency says make $R$ as large as the job allows and $r$ as small
as money allows — the far right of the table, not the middle. The two targets are
different targets, and the reason they get confused is that both are called "getting the
most out of the source".

There is a cleaner way to keep them apart. Maximum power transfer is the answer to "$E$
and $r$ are fixed, what $R$?" Efficiency is the answer to "$R$ is fixed, what $r$?" — and
that question has no interior maximum at all, only $r \to 0$. Same circuit, two different
things held still.

## Where it stops holding

**Both forms need $r$ finite and non-zero.** An ideal voltage source has $r = 0$, so its
Norton current $E/r$ is infinite and it has no parallel form. An ideal current source has
$r = \infty$ and has no series form. The transformation is a statement about *real*
sources, and the two idealisations sit at its two ends where it fails.

**The equivalence is at the terminals and nowhere else.** This one catches people who
otherwise have the idea straight. Take the worked example above — 12.0 V behind 4.00 Ω
into 6.00 Ω, and its transform:

```text
    series form:    P(internal)  =  1.20^2 * 4.00        =   5.76 W
                    P(load)      =  1.20 * 7.20          =   8.64 W
                    P(source)    =  12.0 * 1.20          =  14.40 W

    parallel form:  P(internal)  =  7.20^2 / 4.00        =  12.96 W
                    P(load)      =  7.20^2 / 6.00        =   8.64 W
                    P(source)    =  7.20 * 3.00          =  21.60 W
```

The load gets 8.64 W either way, as it must. The internal resistance dissipates 5.76 W in
one form and 12.96 W in the other. Both are correct, and neither tells you how hot the
real battery gets, because the real battery is one of these and not the other. Use the
transformation to find currents and voltages in the external circuit; do not use it to
work out what is happening inside the source.

**Everything here assumes straight lines.** Superposition of the two current sources in
the parallel-batteries example, the addition of $I_N$ values, the single maximum — all of
it is linearity. A real solar panel's $V$–$I$ curve is a knee, not a line, so its maximum
power point is not at any fixed resistance and has to be hunted for continuously; that
hunt has a name, maximum power point tracking, and it is a whole subsystem in every solar
inverter. A battery near empty is not a line either.

**And this is only the two-terminal case.** Nothing above needed the source to be a
battery: any linear network with two terminals sticking out of it has an $E$ and an $r$,
whatever is inside. That generalisation is Thévenin's theorem, it turns the whole of this
reading into a tool for arbitrary circuits rather than for sources, and it is module 10.
''',
                },
            ],
            "quiz": {
                "title": "What is inside a source",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A cell reads 9.00 V with nothing connected, and 8.40 V while delivering 200 mA. What is its internal resistance?",
                        "opts": ["0.6 Ω", "42 Ω", "3 Ω", "45 Ω"],
                        "a": 2,
                        "why": r'''
The 0.60 V that went missing was dropped across $r$ by the 200 mA passing through it,
so $r = 0.6/0.2 = 3$ Ω. Answering 0.6 Ω is quoting the lost voltage as a resistance,
and 42 Ω is $8.4/0.2$, which is the *load*, not the source. Two terminal measurements
at two different currents are all it ever takes to find $r$, and it is the standard
bench method.
''',
                    },
                    {
                        "q": "A 1.5 V cell has an internal resistance of 0.25 Ω. Roughly what current flows if its terminals are shorted with a thick wire?",
                        "opts": ["6 A", "0.375 A", "infinite", "1.5 A"],
                        "a": 0,
                        "why": r'''
With the terminals joined, the only resistance left in the loop is the cell's own, so
$I = E/r = 1.5/0.25 = 6$ A. Nothing is infinite, because $r$ is not zero — that is
the practical content of internal resistance, and it is why a shorted AA gets hot
rather than exploding while a shorted car battery, whose $r$ is a few milliohms, will
happily vaporise a spanner.
''',
                    },
                    {
                        "q": "Which instrument reads a cell's EMF most nearly exactly?",
                        "opts": [
                            "an ammeter, which has almost no resistance",
                            "a voltmeter drawing a microamp, which is nearly an open circuit",
                            "either — they must agree",
                            "neither: EMF cannot be measured",
                        ],
                        "a": 1,
                        "why": r'''
$V_t = E - Ir$, so the error is $Ir$ and it vanishes as the current does. A voltmeter
drawing a microamp through, say, 3 Ω is off by three microvolts. An ammeter is the
opposite instrument: it is nearly a short circuit, so connecting one straight across a
cell measures $E/r$ and, on anything larger than a coin cell, damages both the meter
and the cell.
''',
                    },
                    {
                        "q": "A 12 V source with 4 Ω of internal resistance is redrawn as a current source in parallel with a resistance. What are the two values?",
                        "opts": ["12 A and 4 Ω", "3 A and 4 Ω", "3 A and 12 Ω", "48 A and 4 Ω"],
                        "a": 1,
                        "why": r'''
The source transformation keeps the resistance and turns the EMF into the
short-circuit current: $I_N = E/r = 12/4 = 3$ A, in parallel with the same 4 Ω. Check
it from outside: open circuit, all 3 A must go through the 4 Ω, giving 12 V, which
matches. Shorted, the 4 Ω has no voltage across it and all 3 A leaves the terminals,
which also matches. Two agreements at the two extremes are enough, because both forms
are straight lines and two points fix a line.
''',
                    },
                    {
                        "q": "A load is connected whose resistance happens to equal the source's internal resistance. What fraction of the energy taken out of the source ends up in the load?",
                        "opts": ["all of it", "three quarters", "one quarter", "half"],
                        "a": 3,
                        "why": r'''
Half. The same current passes through both resistances and they are equal, so by
$P = I^2R$ they dissipate equally: for every joule the load receives, one joule heats
the source. That is a genuinely poor efficiency, and yet it is the condition under
which the load receives the most power it ever can — the two are not the same
target, and module 10, on the matched load, pulls them apart.
''',
                    },
                ],
            },
            "match": {
                "title": "Every way a source is drawn",
                "minutes": 6,
                "brief": r"""
A schematic distinguishes an *ideal* source from a real component, and a source of
voltage from a source of current, by the marking inside the outline. These five appear
on the first page of almost every circuit you will meet, and confusing two of them
means solving a different circuit from the one on the paper.
""",
                "prompt": "Pick a label, then tap the symbol it belongs to.",
                "labels": [
                    "Switch, drawn open",
                    "Ideal current source",
                    "Diode",
                    "Ideal voltage source",
                    "Battery of two cells",
                ],
                "items": [
                    {"sym": "V", "a": 3, "why": "An ideal voltage source: a circle with a "
                     "$+$ and a $-$ marking its two terminals. It holds the voltage between "
                     "them at its stated value no matter what current the rest of the circuit "
                     "asks for — which is exactly the assumption you drop when you draw "
                     "a resistance in series with it."},
                    {"sym": "BATT", "a": 4, "why": "A battery. The long bar is the positive "
                     "terminal and the short bar the negative, and one long-short pair is one "
                     "cell: two pairs drawn here means two cells in series. The symbol says "
                     "nothing about internal resistance, which is why that has to be drawn as "
                     "a separate resistor whenever it matters."},
                    {"sym": "I", "a": 1, "why": "An ideal current source: the same circle as a "
                     "voltage source, but marked with an arrow instead of a $+$ and a $-$. It "
                     "fixes the current through itself and lets the voltage across it be "
                     "whatever the rest of the circuit demands — including, in an ideal "
                     "one left open-circuit, an impossible one."},
                    {"sym": "SW", "a": 0, "why": "A switch, drawn in the open position: the "
                     "lever is lifted clear of the second contact, and the gap is the point of "
                     "the symbol. Open means no current whatever the voltage; closed means no "
                     "voltage whatever the current. A switch is the two limiting cases of a "
                     "resistor, and nothing in between."},
                    {"sym": "D", "a": 2, "why": "A diode: a triangle pointing into a bar. "
                     "Conventional current passes in the direction the triangle points — in "
                     "at the flat back of the triangle and out past the bar — and is blocked "
                     "completely the other way. Put one in series with a battery and the "
                     "circuit survives the cell being inserted backwards, which is most of "
                     "what a diode does in a DC circuit before EE201 explains why it works."},
                ],
            },
            "blanks": [
                {
                    "title": "Where a cell's watts actually go",
                    "minutes": 9,
                    "caption": "one cell, one load, and every watt accounted for",
                    "lang": "text",
                    "brief": r'''
A single 18650 lithium cell driving a small heating element. Nothing below is new: it is
Ohm's law on a loop, then $P = I^2R$ on each of the two resistances in it, then the check
that the two dissipations come to exactly what the EMF hands over. There is nowhere else
in the loop for energy to go, so when they disagree it is the arithmetic that has failed.

The last line is the one that decides whether the cell is the right cell for the job.

Fill in the six holes in order; each one is one step from the lines above it.
''',
                    "listing": r'''
a single 18650 cell: 3.60 V of EMF behind 0.100 ohm of internal
resistance, driving a 1.700 ohm heating element
--------------------------------------------------------------------

  one loop, so one current, and the EMF is across the internal
  resistance and the element together

    Rloop  =  0.100 + 1.700                      =  1.800 ohm
    I      =  3.60 / 1.800                       =  ___ A

  the terminals are the two ends of the element, so the terminal
  voltage is Ohm's law on the element alone

    Vt     =  I * 1.700                          =  ___ V

  and the volts that never got out are the ones dropped inside

    V(r)   =  I * 0.100                          =  0.200 V
    check  =  Vt + V(r)                          =  3.60 V

  the same current passes through both resistances, so I^2 R is the
  form to reach for on each of them

    P(r)   =  I^2 * 0.100                        =  ___ W
    P(el)  =  I^2 * 1.700                        =  ___ W

  nothing else in the loop dissipates anything, so those two have to
  come to what the EMF is handing over

    P(EMF) =  3.60 * I                           =  ___ W

  and the number that says whether this cell is big enough for this
  job: the share of its output that reaches the element

    P(el) / P(EMF)                               =  ___ %
''',
                    "blanks": [
                        {
                            "prompt": "3.60 V across a 1.800 Ω loop. How many amps?",
                            "hole": "?",
                            "opts": ["2.00", "36.0", "2.12", "0.500"],
                            "a": 0,
                            "why": "$3.60/1.800 = 2.00$ A. The value 2.12 is $3.60/1.700$, which "
                                   "leaves the internal resistance out — that is the ideal-source "
                                   "answer, and the whole point of this module is the difference "
                                   "between it and 2.00. The value 0.500 has the division upside "
                                   "down, $1.800/3.60$, which would be an admittance rather than a "
                                   "current.",
                        },
                        {
                            "prompt": "2.00 A through the 1.700 Ω element. How many volts across it?",
                            "hole": "?",
                            "opts": ["3.40", "3.60", "0.850", "1.70"],
                            "a": 0,
                            "why": "$2.00 \\times 1.700 = 3.40$ V. The value 3.60 is the EMF, which "
                                   "is what the terminals would read with nothing connected — the "
                                   "200 mV of difference is exactly what this module is about. The "
                                   "value 0.850 divides where the definition multiplies.",
                        },
                        {
                            "prompt": "2.00 A through the 0.100 Ω internal resistance. How many watts?",
                            "hole": "?",
                            "opts": ["0.400", "0.200", "0.0500", "0.720"],
                            "a": 0,
                            "why": "$I^2r = 2.00^2 \\times 0.100 = 0.400$ W. The value 0.200 is the "
                                   "*voltage* dropped inside, in volts, not the power. The value "
                                   "0.720 is $3.60 \\times 0.200$, which uses the EMF where the "
                                   "voltage across the internal resistance was needed: in "
                                   "$P = VI$ the $V$ has to belong to the part you are asking about.",
                        },
                        {
                            "prompt": "2.00 A through the 1.700 Ω element. How many watts?",
                            "hole": "?",
                            "opts": ["6.80", "7.20", "3.40", "0.850"],
                            "a": 0,
                            "why": "$I^2R = 2.00^2 \\times 1.700 = 6.80$ W, and the other route "
                                   "agrees: $V_tI = 3.40 \\times 2.00 = 6.80$ W. The value 7.20 is "
                                   "what the EMF supplies, which is this plus the 0.400 W lost "
                                   "inside. The value 3.40 is the terminal voltage rather than a "
                                   "power.",
                        },
                        {
                            "prompt": "3.60 V of EMF pushing 2.00 A. How many watts leave the chemistry?",
                            "hole": "?",
                            "opts": ["7.20", "6.80", "1.80", "0.400"],
                            "a": 0,
                            "why": "$P = EI = 3.60 \\times 2.00 = 7.20$ W — and it must equal the "
                                   "$6.80 + 0.400$ already found, which is the check the whole "
                                   "ledger exists for. Choosing 6.80 uses the terminal voltage: "
                                   "that is the power leaving the *terminals*, and the difference "
                                   "between the two is precisely the 0.400 W that never got out.",
                        },
                        {
                            "prompt": "6.80 W into the element out of 7.20 W produced. What percentage?",
                            "hole": "?",
                            "opts": ["94.4", "5.6", "105.9", "47.2"],
                            "a": 0,
                            "why": "$6.80/7.20 = 0.9444$, so 94.4%. The same number comes out of "
                                   "$R/(R+r) = 1.700/1.800$ without any powers being computed at "
                                   "all, because the two resistances carry the same current and "
                                   "share the total in proportion to themselves. The value 5.6 is "
                                   "the share heating the cell, and 105.9 is the fraction inverted "
                                   "— an efficiency above 100% should stop the pen.",
                        },
                    ],
                },
                {
                    "title": "A battery, measured twice",
                    "minutes": 10,
                    "caption": "two points on a straight line, and everything that follows from them",
                    "lang": "text",
                    "brief": r'''
Neither $E$ nor $r$ can be measured directly: $E$ needs no current flowing, $r$ needs
current flowing, and no single reading gives both. What does give both is two readings at
two different currents, because $V_t = E - Ir$ is a straight line and two points fix a
line. This is the standard load-bank test, and it is the whole reason a battery is judged
under load rather than with a voltmeter.

The two readings are taken seconds apart, so that the cell itself has no time to change
between them.

Fill in the six holes in order.
''',
                    "listing": r'''
a 12 V lead-acid battery on a load bank

    reading 1:   I1 =  2.00 A,   V1 = 12.60 V
    reading 2:   I2 = 20.00 A,   V2 = 11.70 V
--------------------------------------------------------------------

  the model says Vt = E - I r, so between the two readings only the
  I r term can have changed.  the slope of the line is r

    dV     =  12.60 - 11.70                      =  0.900 V
    dI     =  20.00 - 2.00                       =  18.00 A
    r      =  dV / dI                            =  ___ ohm

  E is then either reading with its own lost volts added back on, and
  both readings must give the same answer or the line was not a line

    E      =  12.60 + 2.00 * r                   =  ___ V
    check  =  11.70 + 20.00 * r                  =  the same number

  the short-circuit current is the whole EMF across r alone.  it is
  not a measurement anybody takes; it is a number to respect

    Isc    =  E / r                              =  ___ A

  the load that takes the most power out of this battery is the one
  that matches r.  it splits the EMF evenly with the battery's own
  resistance, so the terminals sit at half the EMF

    R      =  r                                  =  0.0500 ohm
    I      =  E / (2 * r)                        =  127.0 A
    Vt     =  E / 2                              =  ___ V
    P      =  Vt * I                             =  ___ W

  and the share of the battery's output that the load receives at that
  operating point

    P / (E * I)                                  =  ___ %
''',
                    "blanks": [
                        {
                            "prompt": "0.900 V lost over an extra 18.00 A. How many ohms?",
                            "hole": "?",
                            "opts": ["0.0500", "20.0", "0.585", "0.0450"],
                            "a": 0,
                            "why": "$r = \\Delta V/\\Delta I = 0.900/18.00 = 0.0500$ Ω. The value "
                                   "20.0 has the division upside down. The value 0.585 is "
                                   "$11.70/20.00$, which is the *load* the bank was set to for the "
                                   "second reading, not the battery's own resistance — that "
                                   "confusion is the commonest way this measurement goes wrong.",
                        },
                        {
                            "prompt": "12.60 V measured while 2.00 A flowed through 0.0500 Ω. What is the EMF?",
                            "hole": "?",
                            "opts": ["12.70", "12.50", "12.60", "13.60"],
                            "a": 0,
                            "why": "$E = V_t + Ir = 12.60 + 0.100 = 12.70$ V, and the second reading "
                                   "confirms it: $11.70 + 20.00 \\times 0.0500 = 12.70$ V. The value "
                                   "12.50 subtracts the drop instead of adding it — the terminals "
                                   "are always *below* the EMF when current is leaving, so the "
                                   "correction goes upwards. The value 12.60 forgets that even a "
                                   "2 A reading is a loaded one.",
                        },
                        {
                            "prompt": "12.70 V across 0.0500 Ω and nothing else. How many amps?",
                            "hole": "?",
                            "opts": ["254", "0.635", "25.4", "20.0"],
                            "a": 0,
                            "why": "$12.70/0.0500 = 254$ A. Nothing is infinite, because $r$ is not "
                                   "zero — that is the entire practical content of internal "
                                   "resistance, and 254 A through a dropped spanner is enough to "
                                   "weld it to the terminal. The value 0.635 is $12.70 \\times "
                                   "0.0500$, a multiplication where Ohm's law divides.",
                        },
                        {
                            "prompt": "At the matched load the battery and the load are equal resistances in series. What do the terminals read?",
                            "hole": "?",
                            "opts": ["6.35", "12.70", "11.70", "3.175"],
                            "a": 0,
                            "why": "Two equal resistances in series split the EMF evenly, so "
                                   "$V_t = E/2 = 6.35$ V. This is the operating point of most "
                                   "power, and it is also the point at which a 12 V battery is "
                                   "presenting six volts to whatever is connected — which is why "
                                   "maximum power is almost never a sensible place to run "
                                   "anything. The value 12.70 is the open-circuit voltage, at the "
                                   "opposite end of the same line.",
                        },
                        {
                            "prompt": "6.35 V across the load while 127.0 A passes through it. How many watts?",
                            "hole": "?",
                            "opts": ["806", "1613", "403", "20.0"],
                            "a": 0,
                            "why": "$P = V_tI = 6.35 \\times 127.0 = 806.5$ W, and the formula "
                                   "$E^2/4r = 161.29/0.200$ agrees to the same figure. No load of "
                                   "any value can get more than this out of this battery. The value "
                                   "1613 is what the EMF is producing at that moment, half of which "
                                   "is heating the battery.",
                        },
                        {
                            "prompt": "806.5 W into the load out of 1612.9 W produced. What percentage?",
                            "hole": "?",
                            "opts": ["50.0", "100", "25.0", "80.0"],
                            "a": 0,
                            "why": "Exactly half, and it has to be: the same current passes through "
                                   "two equal resistances, so by $P = I^2R$ they dissipate equally. "
                                   "That is the price of maximum power, and it is why the matched "
                                   "load is the right target for an antenna and a terrible one for "
                                   "a power supply. Run the same battery into 0.200 Ω instead and "
                                   "the load gets 508 W — a third less — at 80% efficiency.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "What the terminals read while the lamp is on",
                    "minutes": 5,
                    "brief": r'''
The two components in the left-hand branch are both *inside the cell*: the 1.50 V is the
EMF and the 0.30 Ω is the internal resistance. There is no node between them you could
reach with a probe. The cell's actual terminals are the top rail and ground, and the
probe is sitting on one of them.

One rule, one unknown. The only thing to be careful about is which resistance the
current sees.
''',
                    "prompt": "What voltage appears at the cell's terminals with the lamp connected?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 1.5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 11},
                            {"id": "rint", "kind": "R", "x": 3, "y": 5, "rot": 1, "value": 0.3},
                            {"id": "rl", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 4.7},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 9], "b": [3, 11]},
                            {"a": [3, 7], "b": [3, 6]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [14, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 10]},
                        ],
                    },
                    "given": [
                        {"label": "EMF", "value": "1.50 V"},
                        {"label": "Internal resistance r", "value": "0.30 Ω"},
                        {"label": "Lamp", "value": "4.70 Ω"},
                    ],
                    "aside": "One loop means one current, and that current is the same in the "
                             "internal resistance as in the lamp.",
                    "answer": 1.41,
                    "tol": 0.01,
                    "unit": "V",
                    # The terminal is the probed node, so this one is a straight reading of
                    # the solve rather than anything derived from it.
                    "check": r'''
return c.vout();
''',
                    "hint": "The EMF is across the two resistances in series, so add them before "
                            "dividing. Then the terminal voltage is Ohm's law on the lamp alone.",
                    "wrong": "If you got 1.50 you have quoted the EMF, which is what the terminals "
                             "read only when nothing is connected. If you got 0.09 that is the "
                             "voltage lost inside the cell — subtract it from the EMF and you have "
                             "the answer.",
                    "why": r'''
```text
    Rloop  =  0.30 + 4.70                        =  5.00 ohm
    I      =  1.50 / 5.00                        =  0.300 A
    Vt     =  0.300 * 4.70                       =  1.41 V

    the other route, which must agree
    Vt     =  1.50 - 0.300 * 0.30  =  1.50 - 0.09  =  1.41 V
```

Ninety millivolts, six per cent of the EMF, gone before the lamp sees any of it — and
that is a healthy cell. Let the cell age until $r$ reaches 3.00 Ω and the same lamp gets
$1.50 \times 4.70/7.70 = 0.916$ V, at which point the torch is orange and a voltmeter
across the cell with the lamp switched off still reads 1.50 V.
''',
                },
                {
                    "title": "How much of a battery's power heats the battery?",
                    "minutes": 8,
                    "brief": r"""
The 12 Ω resistor in this drawing is not a component anyone soldered. It is the cell's
own internal resistance, drawn in series with the EMF because that is the only way to
put it on a schematic. There is no node between the two that you could reach with a
probe. The cell's actual terminals are the node the probe sits on and ground; the
9 V and the 12 Ω are both sealed inside.

Everything else follows from the loop having one current in it.
""",
                    "prompt": "How much power is turned into heat inside the cell?",
                    "note": "Give the answer in watts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 12},
                            {"id": "r2", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 60},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 7},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 9]},
                            {"a": [11, 7], "b": [15, 7]},
                            {"a": [11, 11], "b": [11, 13]},
                        ],
                    },
                    "given": [
                        {"label": "EMF", "value": "9.00 V"},
                        {"label": "Internal resistance r", "value": "12 Ω"},
                        {"label": "Load", "value": "60 Ω"},
                    ],
                    "aside": "One loop, so one current — and it is the same current in the "
                             "internal resistance as in the load, which is what makes $I^2r$ the "
                             "form to reach for.",
                    "answer": 0.1875,
                    "tol": 0.004,
                    "unit": "W",
                    # The internal resistance is the part drawn as r1, and no node of this
                    # circuit is its power, so the check measures the drop across it and
                    # squares that. Reading both ends out of the solve rather than assuming
                    # which node is which means a re-drawn schematic is still measured
                    # correctly rather than measured somewhere else.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r1'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
return drop * drop / r.value;
''',
                    "hint": "Find the loop current first: the EMF is across $r$ and the load in "
                            "series. Then the power in $r$ alone is $I^2 r$.",
                    "wrong": "Check whether you have used the EMF or the terminal voltage. The "
                             "9 V is across the pair; only part of it appears across the 12 Ω.",
                    "why": "$I = 9/(12+60) = 0.125$ A, so the cell wastes "
                           "$I^2r = 0.125^2 \\times 12 = 0.1875$ W in itself. The load gets "
                           "$0.125^2 \\times 60 = 0.9375$ W, and the two add to 1.125 W, which is "
                           "$9 \\times 0.125$ — the power the EMF supplies. A sixth of "
                           "everything this cell delivers is spent warming it up, and the only way "
                           "to improve that is a lighter load or a bigger cell.",
                },
                {
                    "title": "The second load comes on",
                    "minutes": 9,
                    "brief": r'''
A 12.0 V battery of internal resistance 0.50 Ω feeds two things at once: a 6.0 Ω heater
and a 3.0 Ω motor, both hanging between the same rail and the same ground. The 0.50 Ω
in the left-hand branch is inside the battery; the rail is where its terminals are.

Two loads sharing a rail means neither of them sees the EMF. Work out what the rail is
actually at before you touch either branch.
''',
                    "prompt": "How much current flows in the 6.0 Ω branch?",
                    "note": "Give the answer in amperes, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 11},
                            {"id": "rint", "kind": "R", "x": 3, "y": 5, "rot": 1, "value": 0.5},
                            {"id": "rl1", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 6},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "rl2", "kind": "R", "x": 17, "y": 6, "rot": 1, "value": 3},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 20, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 9], "b": [3, 11]},
                            {"a": [3, 7], "b": [3, 6]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [20, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [17, 3], "b": [17, 5]},
                            {"a": [17, 7], "b": [17, 9]},
                        ],
                    },
                    "given": [
                        {"label": "EMF", "value": "12.0 V"},
                        {"label": "Internal resistance r", "value": "0.50 Ω"},
                        {"label": "Heater", "value": "6.0 Ω"},
                        {"label": "Motor", "value": "3.0 Ω"},
                    ],
                    "aside": "The internal resistance carries both branch currents; each load "
                             "carries only its own. That asymmetry is the whole question.",
                    "answer": 1.6,
                    "tol": 0.02,
                    "unit": "A",
                    # No node of this circuit is a branch current, so the check reads the drop
                    # across the 6 ohm branch out of the solve and divides by its own value,
                    # taken from the netlist rather than restated here.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'rl1'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value;
''',
                    "hint": "Collapse the two loads into one resistance first. Then the circuit is "
                            "a single loop again, and the rail voltage is what that collapsed "
                            "resistance drops.",
                    "wrong": "If you got 2.00 A you divided the EMF by 6.0 Ω — but the rail is not "
                             "at 12.0 V, because the battery's own resistance is carrying 4.8 A. "
                             "If you got 4.80 A that is the total the battery delivers, which is "
                             "this branch plus the motor's.",
                    "why": r'''
```text
the two loads share a rail, so they are in parallel

    Rload  =  (6.0 * 3.0) / (6.0 + 3.0)          =  2.00 ohm

now one loop, and the internal resistance is in series with that

    I(tot) =  12.0 / (0.50 + 2.00)               =  4.80 A
    Vrail  =  4.80 * 2.00                        =  9.60 V

each branch is then Ohm's law on the rail voltage

    I(6)   =  9.60 / 6.0                         =  1.60 A
    I(3)   =  9.60 / 3.0                         =  3.20 A
                                                    -------
                                                    4.80 A   KCL closes
```

1.60 A. The number worth carrying away is the rail: 9.60 V, not 12.0 V, and it got there
because the battery's own half-ohm is carrying the *sum* of the two branch currents. That
is what makes a shared supply rail a shared problem — switch the motor off and the rail
jumps to $12.0 \times 6.0/6.5 = 11.08$ V, so the heater's current rises from 1.60 A to
1.85 A without anybody touching the heater.
''',
                },
                {
                    "title": "A source that pushes current instead",
                    "minutes": 10,
                    "brief": r'''
This is the other way of drawing a real source: an ideal **current** source of 3.00 A
with its internal resistance in **parallel** rather than in series. The 4.0 Ω is inside
the source, exactly as the series resistance was in the last few questions, and it is
there for the same reason — an ideal current source would produce whatever voltage the
load demanded, and no real one does.

The 3.00 A is what the source pushes out. It is not what the load gets, because the 4.0 Ω
is a second route to ground and it is sitting right there.
''',
                    "prompt": "How much of the source's 3.00 A reaches the 6.0 Ω load?",
                    "note": "Give the answer in amperes, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "i1", "kind": "I", "x": 4, "y": 9, "rot": 0, "value": 3},
                            {"id": "rint", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4},
                            {"id": "g0", "kind": "GND", "x": 9, "y": 11},
                            {"id": "rl", "kind": "R", "x": 15, "y": 6, "rot": 1, "value": 6},
                            {"id": "out", "kind": "OUT", "x": 18, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 9], "b": [3, 3]},
                            {"a": [3, 3], "b": [18, 3]},
                            {"a": [5, 9], "b": [9, 9]},
                            {"a": [9, 3], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [9, 9], "b": [9, 11]},
                            {"a": [15, 3], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [9, 9], "b": [15, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "3.00 A, ideal"},
                        {"label": "Internal resistance r", "value": "4.0 Ω, in parallel"},
                        {"label": "Load", "value": "6.0 Ω"},
                    ],
                    "aside": "Two resistances between the same rail and the same ground share a "
                             "voltage, and the current divides in inverse proportion to them.",
                    "answer": 1.2,
                    "tol": 0.02,
                    "unit": "A",
                    # The load current is not a node of this circuit, so the check takes the
                    # drop across the load out of the solve and divides by the load's own
                    # value. The magnitude is what the prompt asks for, so the sign convention
                    # the source is drawn with cannot change the answer.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'rl'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value;
''',
                    "hint": "All 3.00 A has to end up back at the source, and there are exactly two "
                            "ways down: through the 4.0 Ω and through the 6.0 Ω. They have the same "
                            "voltage across them.",
                    "wrong": "If you got 3.00 A you have treated the internal resistance as though "
                             "it were not there — that is the ideal source, and the 4.0 Ω is "
                             "precisely the difference. If you got 1.80 A you put the load's own "
                             "resistance on top of the fraction; in a current divider it is the "
                             "*other* branch that goes on top.",
                    "why": r'''
```text
both routes to ground share one voltage, so work that out first

    Rpar   =  (4.0 * 6.0) / (4.0 + 6.0)          =  2.40 ohm
    Vrail  =  3.00 * 2.40                        =  7.20 V

then Ohm's law on each branch

    I(load)  =  7.20 / 6.0                       =  1.20 A
    I(r)     =  7.20 / 4.0                       =  1.80 A
                                                    -------
                                                    3.00 A   KCL closes
```

Forty per cent of what the source produces reaches the load, and the rest goes straight
back through the source's own resistance. The current-divider form says the same thing in
one line: the load's share is the *other* resistance over the sum,
$3.00 \times 4.0/(4.0+6.0) = 1.20$ A.

It is worth transforming this source and re-solving, because the answer must not change.
An EMF of $I_N r = 3.00 \times 4.0 = 12.0$ V in series with the same 4.0 Ω, feeding the
same 6.0 Ω, gives $I = 12.0/10.0 = 1.20$ A and a terminal voltage of 7.20 V. Identical, as
it has to be — and notice how differently the two drawings describe the inside of the
source. In the series form the internal resistance carries 1.20 A and dissipates 5.76 W;
in the parallel form it carries 1.80 A and dissipates 12.96 W. The equivalence holds at
the terminals and stops there.
''',
                },
                {
                    "title": "Two cells in series, one of them tired",
                    "minutes": 13,
                    "brief": r'''
Two nominally identical 6.0 V cells are stacked in series to run a 9.0 Ω load. One is
fresh, with an internal resistance of 0.50 Ω; the other has been in the drawer since 2019
and measures 2.50 Ω. Both still make their full 6.0 V of EMF — that is the number that
survives, and it is why they both still test fine on a meter.

The question is not about the load. It is about what a voltmeter would read if you
clipped it across **the tired cell alone**, between the two points marked as its own
terminals: the node between the two cells, and the node on the far side of its 2.50 Ω.
Neither of those is ground, so this is a difference between two node voltages rather than
a reading of one.
''',
                    "prompt": "What voltage appears across the tired cell's own terminals?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 11, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 14},
                            {"id": "r1", "kind": "R", "x": 3, "y": 8, "rot": 1, "value": 0.5},
                            {"id": "v2", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 6},
                            {"id": "r2", "kind": "R", "x": 6, "y": 3, "value": 2.5},
                            {"id": "rl", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 9},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 12], "b": [3, 14]},
                            {"a": [3, 10], "b": [3, 9]},
                            {"a": [3, 7], "b": [3, 6]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [14, 3]},
                            {"a": [11, 3], "b": [11, 6]},
                            {"a": [11, 8], "b": [11, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Fresh cell", "value": "6.0 V EMF, r = 0.50 Ω"},
                        {"label": "Tired cell", "value": "6.0 V EMF, r = 2.50 Ω"},
                        {"label": "Load", "value": "9.0 Ω"},
                        {"label": "Tired cell's terminals", "value": "either side of its 2.50 Ω, taken as a pair with its EMF"},
                    ],
                    "aside": "Series means one current everywhere. Find it once and every voltage "
                             "in the circuit is one multiplication away.",
                    "answer": 3.5,
                    "tol": 0.02,
                    "unit": "V",
                    # The quantity asked for is a difference between two nodes, neither of them
                    # ground. Both are found from the netlist rather than named by number: the
                    # tired cell's negative terminal is v2's minus node, and its positive
                    # terminal is whichever end of r2 is not shared with v2.
                    "check": r'''
const d = c.dc();
const P = function (id) { return c.net.parts.filter(function (p) { return p.id === id; })[0]; };
const cell = P('v2'), rin = P('r2');
const term = (rin.n1 === cell.n1) ? rin.n2 : rin.n1;
return d.v[term] - d.v[cell.n2];
''',
                    "hint": "Everything is in one loop, so add all three resistances and all the "
                            "EMFs to get the current. Then the tired cell's terminal voltage is its "
                            "own EMF less its own $Ir$ — not the whole stack's.",
                    "wrong": "If you got 6.00 you have quoted the tired cell's EMF, which is what "
                             "its terminals read only with no current flowing. If you got 9.00 that "
                             "is the voltage across the load, which is the *pair* of cells' terminal "
                             "voltage. If you got 5.50 you have found the fresh cell's terminal "
                             "voltage instead — the two do add to 9.00.",
                    "why": r'''
```text
one loop, so one current, and both EMFs push the same way round it

    E(tot) =  6.0 + 6.0                          =  12.00 V
    R(tot) =  0.50 + 2.50 + 9.0                  =  12.00 ohm
    I      =  12.00 / 12.00                      =   1.00 A

each cell now loses its own Ir, and only its own

    fresh:  Vt  =  6.0 - 1.00 * 0.50             =   5.50 V
    tired:  Vt  =  6.0 - 1.00 * 2.50             =   3.50 V
                                                    -------
    across the load                              =   9.00 V   = 1.00 A * 9.0 ohm
```

3.50 V. Two cells with the same EMF, carrying the same current, sitting at wildly
different terminal voltages — because terminal voltage was never a property of a cell on
its own.

The tired cell is also dissipating $1.00^2 \times 2.50 = 2.50$ W inside itself against the
fresh one's 0.50 W, so it will be the warm one in the holder, and it will get worse
faster. And the arithmetic goes somewhere worse still if the load is reduced. With a load
$R$ the current is $12.0/(3.0+R)$, and the tired cell's terminal voltage is
$6.0 - 2.50I$, which reaches zero when $I = 2.40$ A — that is, at $R = 2.0$ Ω. Below that
the number goes negative: the fresh cell is now driving current backwards through the
tired one, charging it whether that chemistry likes it or not. This is the reason a torch
with one old cell in it does not merely run dim, and why cells are replaced as a set.
''',
                },
            ],
            "build": {
                "title": "Model the pack you just measured",
                "minutes": 24,
                "brief": r'''
A battery holder with three AA cells in it. Two measurements have been taken:

- with nothing connected, a voltmeter reads **4.50 V**,
- with a small lamp of **2.00 Ω** across it, the same meter reads **4.00 V**.

Build the two-component model of that pack — an ideal EMF in series with an internal
resistance — with the lamp connected, so that the probe on the terminals reproduces the
second reading.

## What is on the canvas

The lamp, the grounds, the probe and an ideal source are already placed. The source's
positive terminal is a **stub going nowhere**: there is a one-square gap between it and
the top rail, and the internal resistance is what belongs in that gap. Place a resistor
there, rotate it upright with `R`, and give it the value you have worked out.

## Getting the two numbers

The open-circuit reading is the EMF directly, because no current flows through $r$ when
nothing is connected, so $V_t = E$. That fixes the source at 4.50 V — it is already set,
so leave it.

For the internal resistance, work out the current first. You know the voltage across the
lamp and you know the lamp, so Ohm's law gives it, and the same current must be passing
through $r$ because the two are in series. You also know how many volts went missing
between the EMF and the terminals. A voltage and a current is a resistance.

Values need not be round numbers, and the box understands `250m` as readily as `0.25`.

The checks measure what the circuit does: the terminal voltage under load, and the power
the internal resistance is turning into heat. Any pair of components that produces both
passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 4.5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 11},
                        {"id": "p4", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 2},
                        {"id": "p5", "kind": "GND", "x": 11, "y": 10},
                        {"id": "p6", "kind": "OUT", "x": 14, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 9], "b": [3, 11]},
                        {"a": [3, 7], "b": [3, 6]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [14, 3]},
                        {"a": [11, 3], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 10]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 4.5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 11},
                        {"id": "p2", "kind": "R", "x": 3, "y": 5, "rot": 1, "value": 0.25},
                        {"id": "p4", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 2},
                        {"id": "p5", "kind": "GND", "x": 11, "y": 10},
                        {"id": "p6", "kind": "OUT", "x": 14, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 9], "b": [3, 11]},
                        {"a": [3, 7], "b": [3, 6]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [14, 3]},
                        {"a": [11, 3], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 10]},
                    ],
                },
                "checks": [
                    {"name": "one ideal source, set to the open-circuit reading", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 4.5, 0.002,
  'the EMF — with nothing connected there is no current, so no drop, and the meter reads it directly');
'''},
                    {"name": "the 2.00 Ω lamp is still across the terminals", "code": r'''
c.assert(c.count('R') === 2,
  'Two resistors and no more: the lamp, and the one resistor standing for everything ' +
  'inside the pack. Found ' + c.count('R') + '.');
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 2) <= 0.02 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'The 2.00 Ω lamp has to stay between the probed terminal and ground — it is the ' +
   'load the second reading was taken with, not an obstacle.');
'''},
                    {"name": "the terminals read 4.00 V with the lamp on", "code": r'''
c.close(c.vout(), 4.0, 0.005,
  'the terminal voltage under load — half a volt has to disappear between the EMF and here');
'''},
                    {"name": "the pack is losing 1.00 W inside itself", "code": r'''
const inner = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 2) > 0.02;
});
c.assert(inner.length === 1,
  'Exactly one resistor should stand for the internal resistance, in series between the ' +
  'source and the terminal.');
const d = c.dc();
const p = inner[0];
const drop = d.v[p.n1] - d.v[p.n2];
c.close(drop * drop / p.value, 1.0, 0.03,
  'the power lost inside the pack — 2.00 A through it, and half a volt across it');
'''},
                ],
                "hints": [
                    "The lamp has 4.00 V across it and is 2.00 Ω, so the current is $4.00/2.00 = 2.00$ A. Everything else follows from that one number.",
                    "The same 2.00 A must be flowing through the internal resistance, because the two are in series with nothing between them.",
                    "The EMF is 4.50 V and the terminals are at 4.00 V, so 0.50 V is being dropped inside. A drop of 0.50 V at 2.00 A is $0.50/2.00 = 0.25$ Ω.",
                    "Place the resistor in the gap at the top of the left branch, press `R` to stand it upright, and type `0.25`. Check before you run: 0.25 Ω and 2.00 Ω in series is 2.25 Ω, and $4.50/2.25$ is 2.00 A, which is the current you started from.",
                ],
            },
            "derive": {
                "title": "One line, two circuits, and a bench measurement",
                "minutes": 14,
                "vars": ["E", "r", "R", "I", "I_N", "V_t", "V_1", "V_2", "I_1", "I_2"],
                "brief": r'''
Everything in this module is one straight line, $V_t = E - Ir$, read in different
directions. Below it is read in three of them: forwards, to find what a load gets;
sideways, to show that a current source in parallel with $r$ is the same line and
therefore the same source; and backwards, to recover $E$ and $r$ from two readings taken
on a bench.

Nothing new is needed. Ohm's law, the series rule, the parallel rule. Write each answer as
an expression in the symbols named, with no numbers in it.
''',
                "steps": [
                    {
                        "prompt": "A source of EMF $E$ and internal resistance $r$ drives a load $R$. Everything is in one loop, so write the current in terms of $E$, $r$ and $R$.",
                        "answer": "\\frac{E}{r+R}",
                        "hint": "Series resistances add, so the loop looks like one resistance of $r+R$ with $E$ across it. Then Ohm's law once.",
                        "deconstruct": [
                            "There is one loop and therefore one current: the same $I$ passes through $r$ and through $R$.",
                            "That makes them a series pair, so they behave as a single resistance of $r+R$.",
                        ],
                    },
                    {
                        "prompt": "The terminal voltage $V_t$ is what appears across $R$. Write $V_t$ in terms of $E$, $r$ and $R$.",
                        "answer": "\\frac{E R}{r+R}",
                        "hint": "Ohm's law on $R$: multiply the last answer by $R$. Notice that the result is the voltage-divider expression, with $r$ playing the upper resistor.",
                    },
                    {
                        "prompt": "Now the other form. An ideal current source $I_N$ has a resistance $r$ across it, and the same load $R$ is connected. Write the terminal voltage this circuit produces, in terms of $I_N$, $r$ and $R$.",
                        "answer": "\\frac{I_N r R}{r+R}",
                        "hint": "All of $I_N$ has nowhere to go but into $r$ and $R$, which are in parallel. The terminal voltage is that current times that parallel resistance.",
                        "deconstruct": [
                            "$r$ and $R$ both run between the terminal node and ground, so they are in parallel: $rR/(r+R)$.",
                            "The source pushes $I_N$ through that combination, so $V_t = I_N \\times rR/(r+R)$.",
                        ],
                    },
                    {
                        "prompt": "For the two forms to be indistinguishable, those two expressions must agree for every load $R$. Write $I_N$ in terms of $E$ and $r$.",
                        "answer": "\\frac{E}{r}",
                        "hint": "Set the two expressions equal. The factor $R/(r+R)$ is common to both and cancels, whatever $R$ is, which is what makes the equality hold for all loads rather than one.",
                        "deconstruct": [
                            "$\\dfrac{ER}{r+R} = \\dfrac{I_N rR}{r+R}$, and both sides carry the same $R/(r+R)$.",
                            "Cancel it and $E = I_N r$, which is also the statement that the parallel form's open-circuit voltage is $I_N r$.",
                        ],
                    },
                    {
                        "prompt": "Now the bench. Two loaded readings are taken on one source: current $I_1$ with terminal voltage $V_1$, and current $I_2$ with terminal voltage $V_2$. Each obeys $V = E - Ir$. Eliminate $E$ and write $r$.",
                        "answer": "\\frac{V_1-V_2}{I_2-I_1}",
                        "hint": "Write the line twice, once for each reading, and subtract one from the other. $E$ appears in both and disappears.",
                        "deconstruct": [
                            "$V_1 = E - I_1r$ and $V_2 = E - I_2r$.",
                            "Subtracting: $V_1 - V_2 = (I_2 - I_1)r$, since the two $E$ terms cancel.",
                            "Divide through. The result is the slope of the line, with the sign arranged so that $r$ comes out positive when the larger current gave the smaller voltage.",
                        ],
                    },
                    {
                        "prompt": "Eliminate $r$ from the same pair instead, and write $E$ in terms of $V_1$, $V_2$, $I_1$ and $I_2$.",
                        "answer": "\\frac{V_1 I_2 - V_2 I_1}{I_2-I_1}",
                        "hint": "Multiply the first reading by $I_2$ and the second by $I_1$, then subtract: the $r$ terms match and cancel.",
                        "deconstruct": [
                            "$I_2V_1 = I_2E - I_1I_2r$ and $I_1V_2 = I_1E - I_1I_2r$.",
                            "Subtracting kills the $r$ term outright: $I_2V_1 - I_1V_2 = (I_2 - I_1)E$.",
                            "The same answer comes from substituting the previous step into $E = V_1 + I_1r$, with more algebra and more chances to slip.",
                        ],
                    },
                ],
                "closing": r'''
Put the AA cell from the first reading through the last two steps. It gave 1.44 V at
0.400 A and 1.20 V at 1.000 A:

```text
    r  =  (1.44 - 1.20) / (1.000 - 0.400)                =  0.400 ohm
    E  =  (1.44 * 1.000 - 1.20 * 0.400) / (1.000 - 0.400)
       =  (1.44 - 0.48) / 0.600                          =  1.60 V
```

which is what the arithmetic there produced the long way round.

Three things are worth carrying out of this. The second step is a voltage divider with
$r$ on top — every source under load *is* a divider, and the load is one of its two
resistors, which is why a heavy load pulls the output down for exactly the reason a small
lower resistor does. The fourth step is the source transformation, and note what the
derivation actually needed: the two forms agree for every $R$ only because the same factor
$R/(r+R)$ sits in both, so the equivalence is a statement about the terminals and carries
no promise about anything inside. And the last two steps are a complete instrument. Two
readings, four numbers, and a source you have never opened is characterised — which is the
first appearance in this course of a much larger idea, that a two-terminal box can be
replaced by a model fitted from outside it. Module 10 shows that this works for any linear
network at all, not merely for batteries.
''',
            },
        },
        # ---- M7 -----------------------------------------------------------
        {
            "title": "Nodal analysis: one equation per node",
            "summary": "The systematic method. Name every node voltage, write KCL at each of them, and hand what is left to arithmetic.",
            "concepts": [
                "Nodal analysis has one rule for choosing unknowns: nominate a node as ground, and let every other node's voltage be an unknown. There are always fewer node voltages than branch currents, which is what makes the method scale.",
                "At each unknown node, write KCL with Ohm's law already substituted in: the current leaving node $a$ towards node $b$ through a resistance $R$ is $(v_a - v_b)/R$. Add those up over every resistor touching the node and set the total to zero.",
                "A node held by a voltage source is not an unknown. Its equation is simply $v = E$, and it replaces the KCL equation that would otherwise have been written there.",
                "A current source needs no substitution at all: its current is already known, so it goes straight into the KCL sum as a number. Its own voltage is whatever the rest of the circuit makes it, and nothing in the method has to ask.",
                "A voltage source with neither end at ground is the one awkward case. Draw a surface round both of its nodes, write one KCL equation for everything crossing that surface, and add the source's own $v_a - v_b = E$ as the second equation. That pair is a **supernode**.",
                "Every equation is linear in the unknowns, so a circuit becomes a system of simultaneous equations — one per node, and always solvable as long as every node has some resistive path back to ground.",
                "In matrix form the system is $G\\mathbf{v} = \\mathbf{i}$, and for a network of resistors and independent sources it can be written down by inspection: the diagonal is the sum of conductances at a node, the off-diagonal is minus the conductance between two nodes, and the right-hand side is the current injected.",
                "The method does not care whether the network reduces by series and parallel steps, and that is the point: the work is the same either way. It is what every circuit simulator ever written does, and nothing else.",
                "The sign convention has to be consistent, not correct. Write every current as *leaving* the node; a branch really carrying current inwards comes out negative, and the arithmetic is right regardless.",
                "Every node voltage is a conductance-weighted average of whatever the branches leaving it are tied to, which is why a resistive network can never produce a voltage outside the range of its sources. It is the cheapest sanity check in the subject.",
            ],
            "read": [
                {
                    "title": "Standing at a node",
                    "minutes": 18,
                    "body": r'''
Everything so far has worked by recognition. Two resistors carrying the same current —
series, add them. Two with the same voltage across them — parallel, reciprocals. A chain
from the supply down to ground — divider, take the ratio. Six modules of that, and it
covers a great deal of real electronics.

Then one day it stops, with no warning. Draw two supplies of different voltages, each
reaching the same point through its own resistor, and a third resistor from that point to
ground. Look for two resistors in series: none, because no two carry the same current.
Look for two in parallel: none, because no two have the same voltage across them. The
toolkit is silent, and the circuit has three components in it.

That is the circuit this module opens with, and the method that solves it also solves the
next one, and the one after that, without ever needing you to spot anything. It is worth
saying at the outset what the price is. The recognition methods are fast and they give you
a feel for the circuit as you go. Nodal analysis gives you no feel at all: it is a
procedure, it produces a system of simultaneous equations, and you solve them. What you
get in exchange is that it never fails to start.

## Why node voltages, and not the currents

Kirchhoff's own way in was to name the currents. Every branch gets an arrow and a letter,
KCL at each node ties them together, KVL round each loop constrains them further, and you
solve. It works. It is also more arithmetic than necessary, and the reason is worth
seeing, because it is the whole justification for what follows.

Count the unknowns both ways for the three-component circuit above. By branch currents:
three branches, so three unknowns, and you need three independent equations to pin them
down. By node voltages: ground is 0 V by declaration, the two supply terminals are held at
known voltages by the supplies themselves, and there is exactly **one** node left whose
voltage nobody has told you. One unknown, one equation.

That gap widens fast. A network with a dozen resistors hanging off four internal nodes has
twelve branch currents and four unknown node voltages. And the reason is not a trick of
counting: it is that the branch currents are not independent of one another. Give me every
node voltage and I can hand you back every branch current with one division each, by
Ohm's law. The node voltages are the smaller, complete description; the currents are
derived quantities that were being solved for as though they were fundamental.

There is a second reason, less obvious and more important once circuits get large. A node
voltage is *shared*. Six resistors meeting at a node all see the same $v$, so naming it
once serves all six. A branch current belongs to one branch and helps with nothing else.

## Choosing the reference

A voltage is a difference between two points, always. "The voltage at node A" is
meaningless until somebody says what it is measured against, so the first move in nodal
analysis is to pick a node, call it ground, and declare its voltage to be zero.

Which node? Any of them. The physics does not change, and neither do the voltage
*differences* the circuit produces — pick a different reference and every node voltage
shifts by the same constant, which cancels out of every $v_a - v_b$ you go on to write.
Two choices save work, though. Pick the node with the most components on it, because the
equation you skip is the biggest one. And if a supply has one terminal on a common rail,
pick that rail: the supply's other terminal then becomes a node whose voltage you already
know.

In practice the decision is usually made for you: the schematic already carries ground
symbols, and they are all one node. The point of saying it out loud is that ground is a
*choice*, not a property of the circuit.

## The one equation, built out of two things you already have

Now stand on an unknown node and look outwards. Charge does not pile up there — a node is
a piece of wire, it has no capacity to store anything, and whatever arrives must leave in
the same instant. That is Kirchhoff's current law, and it is the only physical input the
method has.

Written as it stands, KCL relates currents. We want an equation in voltages, and Ohm's law
is the translator. Take a resistor $R$ running from your node, at $v$, to somewhere else at
$v_x$. The voltage across it is $v - v_x$, so the current in it is $(v - v_x)/R$, and
because we subtracted in that order, that expression is the current flowing *away* from
your node. Do that for every resistor touching the node, add them, and set the sum to zero:

$$\sum_{\text{branches}} \frac{v - v_x}{R} = 0$$

That is the whole method. One equation per unknown node, each one KCL with Ohm's law
already folded in, and no arrows drawn anywhere.

The sign convention deserves a sentence of its own, because it is where beginners lose
time. Write **every** current as leaving the node. Do not try to work out which way the
current really flows and point the arrows accordingly — you will be wrong somewhere, and
the wrongness will be silent. A branch that is really carrying current inwards simply
comes out with a negative value when you finish, which is the algebra telling you the
truth. Consistency is what is required; correctness is what you get back.

## Worked: one node, three branches

Take the circuit described at the top, with numbers on it. A 24 V supply reaches node A
through 4 kΩ. A 12 V supply reaches the same node A through another 4 kΩ. And 2 kΩ runs
from A down to ground.

Work in volts, milliamps and kilohms. Those three units are consistent with each other —
one volt across one kilohm is one milliamp — so no factor of a thousand can go missing,
and no equation in this module will need a single zero written after a decimal point.

```text
one unknown: v, the voltage at node A.  Every current below LEAVES A.

    towards the 24 V supply      (v - 24) / 4
    towards the 12 V supply      (v - 12) / 4
    down to ground               (v -  0) / 2

KCL says the three add to nothing:

    (v - 24)/4  +  (v - 12)/4  +  v/2   =  0

multiply through by 4 and every fraction clears:

    (v - 24)  +  (v - 12)  +  2v        =  0
    4v - 36                             =  0
    v                                   =  9.00 V
```

Nine volts. Now go back and collect the currents, which is one division each:

```text
    I(24 V branch)  =  (24 - 9) / 4     =  3.75 mA   into A
    I(12 V branch)  =  (12 - 9) / 4     =  0.75 mA   into A
    I(2 kohm)       =        9  / 2     =  4.50 mA   out of A
                                           --------
    in:  3.75 + 0.75                    =  4.50 mA   KCL closes
```

And because every module of this course ends with the energy accounted for, do that too:

```text
    P(4k, upper)  =  3.75^2 * 4         =   56.25 mW
    P(4k, lower)  =  0.75^2 * 4         =    2.25 mW
    P(2k)         =  4.50^2 * 2         =   40.50 mW
                                            --------
    total heat                          =   99.00 mW

    P from 24 V   =  24 * 3.75          =   90.00 mW
    P from 12 V   =  12 * 0.75          =    9.00 mW
                                            --------
    total in                            =   99.00 mW
```

Both supplies are delivering here, and the whole 99 mW comes out as heat. Notice where 9 V
sits: below 12, below 24, above 0. It could not have been anywhere else, and the closing
section of the module's derivation says why in one line.

## Worked: two nodes, and the first real simultaneous equations

One unknown was a warm-up. The method's actual shape appears at two.

A 12 V supply feeds node A through 1 kΩ. From A, 4 kΩ goes down to ground and 1 kΩ goes
across to node B. From B, 6 kΩ goes down to ground, and a second supply of 3 V reaches B
through 3 kΩ. Nothing here is in series with anything and nothing is in parallel with
anything, so there is no route in but this one.

Two unknowns, $v_A$ and $v_B$, so two equations. Stand on each node in turn and write
every current as leaving:

```text
at A:   (vA - 12)/1  +  vA/4  +  (vA - vB)/1        =  0
at B:   (vB - vA)/1  +  vB/6  +  (vB -  3)/3        =  0
```

Clear the fractions one equation at a time — multiply the first by 4 and the second by 6:

```text
    4*(vA - 12)  +  vA  +  4*(vA - vB)              =  0
    4vA - 48 + vA + 4vA - 4vB                       =  0
                              9vA  -  4vB           =  48        (1)

    6*(vB - vA)  +  vB  +  2*(vB - 3)               =  0
    6vB - 6vA + vB + 2vB - 6                        =  0
                            - 6vA  +  9vB           =  6
                            - 2vA  +  3vB           =  2         (2)
```

Two linear equations, two unknowns, and from here it is school algebra. Multiply (1) by 3
and (2) by 4 so the $v_B$ terms cancel when added:

```text
    27vA - 12vB  =  144
    -8vA + 12vB  =    8
    -------------------
     19vA        =  152        so   vA  =  8.00 V

    back into (2):   3vB  =  2 + 2*8  =  18
                      vB  =  6.00 V
```

Now every current in the circuit is one division away:

```text
    1k from the supply to A   (12 - 8)/1            =  4.00 mA   into A
    4k from A to ground              8 /4           =  2.00 mA   out of A
    1k from A to B             (8 - 6)/1            =  2.00 mA   out of A
    6k from B to ground              6 /6           =  1.00 mA   out of B
    3k from B to the 3 V             (6 - 3)/3      =  1.00 mA   out of B

    KCL at A:   4.00  =  2.00 + 2.00                            closes
    KCL at B:   2.00  =  1.00 + 1.00                            closes
```

Look at that last branch. Node B has settled at 6 V and the supply on the end of that
branch is only 3 V, so current runs *from the circuit into the supply* — it is absorbing
1 mA, the way a battery does while it is on charge. Nothing in the setup had to know that
in advance. The term $(v_B - 3)/3$ was written as a current leaving B, it came out
positive, and positive means it really is leaving. That is what the consistency rule buys.

The energy still balances, with the absorbing source counted as a load:

```text
    P(1k)  =  4^2 * 1  =  16 mW        P from the 12 V  =  12 * 4  =  48 mW
    P(4k)  =  2^2 * 4  =  16 mW        into the  3 V    =   3 * 1  =   3 mW
    P(1k)  =  2^2 * 1  =   4 mW                                       ------
    P(6k)  =  1^2 * 6  =   6 mW        net delivered    =  48 - 3  =  45 mW
    P(3k)  =  1^2 * 3  =   3 mW
                          ------
                          45 mW
```

## The mistakes that actually happen

**Writing $v/R$ when the far end is not ground.** This is the big one, and it is tempting
for a good reason: for the resistor that does go to ground, $v/R$ is correct, and it is
the term you write first. The pattern carries over to the next branch by momentum. But
$(v - 12)/4$ and $v/4$ are different currents, and the second one silently asserts that
the far end of the resistor sits at 0 V. Say the far end's voltage out loud as you write
each term — "towards the twelve-volt supply" — and the subtraction writes itself.

**Deciding which way the current flows.** Somebody looks at a branch, reasons that current
must be flowing *in* there, and writes $(12 - v)/4$ to make it positive. Now one term
measures inward current and the rest measure outward, and the equation is wrong in a way
that produces a plausible number rather than an obvious error. Write every term the same
way and let the signs come out however they come.

**Writing an equation at a node whose voltage you already know.** A node held by a supply
to ground is not an unknown. Its voltage is the supply's, full stop, and if you try to
write KCL there you will find you cannot, because you do not know the current the supply
delivers. That current is the thing you have not solved for — and you never need to, until
the very end, when KCL at that node hands it to you for free.

**Forgetting that ground gets no equation.** KCL holds at ground perfectly well; a great
deal of current flows into it. But its voltage is known, and its KCL equation turns out to
be the sum of all the others with the sign flipped. Include it and the system has one more
equation than unknowns and no unique solution. One reference node, one equation dropped.

## Where this stops

Three limits, in the order you meet them.

**A voltage source with neither end at ground.** Everything above assumed every branch
leaving a node was a resistor, so that Ohm's law could turn its current into voltages. A
voltage source has no such law — its current is whatever the circuit demands, and no
expression in $v_A$ and $v_B$ describes it. When such a source is bolted to ground the
problem disappears, because its node stops being unknown. When it floats between two
unknown nodes, you need the trick in the next reading.

**Sources that depend on other parts of the circuit.** Everything here is an *independent*
source: a fixed number. A transistor amplifier is built out of sources whose value is
proportional to a current or voltage elsewhere in the circuit, and those put unknowns on
both sides of the equation. The method survives; the matrix's tidy symmetry does not.

**Anything that is not linear.** $(v - v_x)/R$ is a straight line through the origin, which
is what makes the system linear and solvable in one pass. A diode's current depends
exponentially on its voltage. You can still write KCL at every node — a simulator does
exactly that — but the resulting equations have to be solved by guessing, linearising
about the guess, and repeating until it stops moving. That is Newton's method, and a
transient simulation runs it afresh at every one of thousands of time steps.

None of those changes the shape of the work: node voltages are still the unknowns and KCL
is still the equation. What changes is what you are allowed to substitute into the sum.
''',
                },
                {
                    "title": "When the source will not cooperate",
                    "minutes": 17,
                    "body": r'''
The last reading left one hole in the method, and named it: a voltage source with neither
terminal at ground. This reading fills that hole, deals with current sources on the way
past, and finishes with the observation that once you have done a few of these by hand you
never need to write the equations out again — the matrix can be read straight off the
drawing.

## Why a voltage source is awkward and a current source is not

Go back to what made the node equation work. Every branch leaving the node contributed a
term, and each term was the branch's current written in terms of node voltages. For a
resistor that translation is Ohm's law, and it always exists.

For an ideal voltage source there is no such translation. Ask what current flows through a
5 V source and the honest answer is: whatever the rest of the circuit asks it for. Its
current is not a function of its voltage — its voltage is fixed and its current is free.
That is precisely the property that makes it a voltage source, and precisely what stops it
being substituted into a KCL sum.

A current source has the opposite freedom, and the opposite consequence. Its current is
fixed and its voltage is free. But it is the *current* the KCL sum wants, so a current
source is not awkward at all: it is already the answer. A 3 mA source pushing current into
a node contributes exactly $-3$ to that node's sum of leaving currents, and its terminal
voltage is whatever the rest of the circuit ends up making it. Nothing has to be done
about it and nothing has to be worked out first.

That asymmetry is worth holding onto. **The hard case is the voltage source, always,
because a node equation is built out of currents.**

## The two easy positions for a voltage source

A source with one terminal on ground is not a problem either, for a reason that has
nothing to do with the paragraphs above: it removes an unknown rather than adding an
awkward term. Its free terminal is a node whose voltage you know before starting. Write
$v = E$ and cross that node off the list. It never gets a KCL equation, and its current —
the one thing you cannot express — is never needed, because you never write the equation
that would have contained it.

A source in series with a resistor, feeding a node, is the same case with one extra step
that most people skip in their heads. Strictly there is a node between the source and the
resistor, and its voltage is $E$. The node you care about is on the far side of the
resistor, and the term it contributes is $(v - E)/R$ — Ohm's law across the resistor, with
the far end at the known voltage $E$. That is the shape almost every branch in a practical
circuit has.

## The floating source, and the surface you draw round it

Now the awkward case. A source of $E$ volts sits between node $a$ and node $b$, and
neither is ground. Two unknowns, and the branch between them cannot be written as a
current.

The way out is to stop insisting on one node at a time. Kirchhoff's current law is not
really a statement about nodes; it is a statement about *any* closed surface you care to
draw in a circuit. Charge does not accumulate anywhere inside such a surface, so the total
current crossing it inwards equals the total crossing it outwards. A node is just the
smallest interesting surface.

So draw a surface that encloses **both** ends of the offending source. The source is now
entirely inside; its unpleasant current crosses no boundary and therefore appears in no
equation. What crosses the boundary is the resistors — every branch that touches $a$ or
$b$ from outside — and every one of those is Ohm's law again. One equation:

$$\sum_{\text{branches leaving } a} \frac{v_a - v_x}{R} \;+\; \sum_{\text{branches leaving } b} \frac{v_b - v_y}{R} \;=\; 0$$

That surface, with the two nodes and the source inside it, is called a **supernode**.

One equation is not enough for two unknowns, and the missing one is the piece of
information we have not used yet: the source is a 5 V source. It fixes the difference:

$$v_a - v_b = E$$

with the sign set by which end carries the $+$ mark. Two equations, two unknowns, and the
awkward case has cost exactly one line more than an ordinary node.

It is worth seeing why the count still works. The floating source did add an unknown —
its own current — but it also added a constraint, $v_a - v_b = E$. The supernode trades
them off against each other: you lose one KCL equation (two nodes now share one) and you
gain one constraint equation. The books balance, which is the sign that nothing has been
smuggled in.

## Worked: a supernode from end to end

A 20 V rail feeds node A through 2 kΩ. From A, 4 kΩ goes down to ground. Between A and B
sits a 5 V source with its $+$ terminal on the A side. From B, 2 kΩ goes down to ground.
There is no other connection: node B does not touch the rail at all.

Volts, milliamps, kilohms as before.

```text
unknowns: vA and vB.  The 5 V source floats, so A and B go inside one
surface and the source's current never appears.

  what crosses the surface, all written as LEAVING:

    from A, towards the 20 V rail      (vA - 20) / 2
    from A, down to ground             vA / 4
    from B, down to ground             vB / 2

  KCL over the surface:

    (vA - 20)/2  +  vA/4  +  vB/2       =  0            (1)

  and the source itself, + on the A side:

    vA - vB                             =  5            (2)
```

Substitute (2) as $v_A = v_B + 5$ into (1), then multiply by 4:

```text
    (vB + 5 - 20)/2  +  (vB + 5)/4  +  vB/2   =  0
    2*(vB - 15)  +  (vB + 5)  +  2*vB         =  0
    2vB - 30 + vB + 5 + 2vB                   =  0
    5vB                                       =  25
    vB  =  5.00 V     and so    vA  =  10.00 V
```

Collect the currents:

```text
    2k from the rail to A     (20 - 10)/2     =  5.00 mA   into A
    4k from A to ground             10 /4     =  2.50 mA   out of A
    2k from B to ground              5 /2     =  2.50 mA   out of B

    across the surface:   5.00  =  2.50 + 2.50            closes
```

And the current in the source itself, which the supernode equation deliberately did not
contain, comes out of ordinary KCL at A now that $v_A$ is known:

```text
    in at A from the 2k          5.00 mA
    out at A through the 4k      2.50 mA
                                 -------
    into the source at A         2.50 mA     and out at B, into the 2k
```

Current enters the source at its $+$ terminal and leaves at its $-$, which is a source
being charged: it absorbs $5 \times 2.5 = 12.5$ mW. The rail delivers
$20 \times 5.00 = 100$ mW; the three resistors take $50 + 25 + 12.5 = 87.5$ mW; and
$87.5 + 12.5 = 100$. Everything is accounted for.

## Worked: writing the matrix without writing the equations

Once the equations are cleared of fractions they always have the same shape, and after a
few circuits you can see it coming. For unknown nodes $A$ and $B$:

$$\begin{bmatrix} G_{AA} & -G_{AB} \\ -G_{AB} & G_{BB} \end{bmatrix}
\begin{bmatrix} v_A \\ v_B \end{bmatrix} = \begin{bmatrix} i_A \\ i_B \end{bmatrix}$$

with three rules, each of which is just the node equation rearranged:

- $G_{AA}$ is the sum of the conductances of **every** resistor touching node A. It is
  always positive.
- $G_{AB}$ is the conductance of the resistors joining A directly to B, and it enters with
  a minus sign in both off-diagonal positions. That symmetry is not a coincidence — the
  resistor between A and B appears in both equations, identically.
- $i_A$ is the current *injected* into A by sources: a current source pushing in counts
  positive, and a voltage source $E$ reaching A through $R$ counts as $E/R$, because that
  is the current it would push in if A were held at zero.

Try it. A 3 mA source pushes current into node A. From A, 2 kΩ runs to ground and 1 kΩ
runs across to node B. From B, 1.5 kΩ runs to ground and 3 kΩ runs to a 6 V supply.

```text
conductances, in millisiemens (one over kilohms):

    at A:   1/2 + 1/1                        =  1.5
    at B:   1/1 + 1/1.5 + 1/3                =  1 + 0.6667 + 0.3333  =  2.0
    A to B: 1/1                              =  1.0

injected currents, in milliamps:

    at A:   the current source                =  3.0
    at B:   6 V through 3 kohm  =  6/3        =  2.0

so the system is

    1.5*vA  -  1.0*vB   =  3.0
   -1.0*vA  +  2.0*vB   =  2.0
```

Solve it: from the first, $v_B = 1.5 v_A - 3$. Put that in the second:
$-v_A + 3v_A - 6 = 2$, so $v_A = 4.00$ V and $v_B = 3.00$ V.

```text
    2k   from A to ground          4 /2       =  2.00 mA  out of A
    1k   from A to B         (4 - 3)/1        =  1.00 mA  out of A
    1.5k from B to ground          3 /1.5     =  2.00 mA  out of B
    3k   from B to the 6 V   (6 - 3)/3        =  1.00 mA  into B

    KCL at A:   3.00 in  =  2.00 + 1.00                   closes
    KCL at B:   1.00 + 1.00 in  =  2.00                   closes
```

The current source is delivering $3\ \text{mA} \times 4\ \text{V} = 12$ mW — note that
nothing told us its terminal voltage in advance; it came out of the solve like everything
else. The 6 V supply delivers $6 \times 1 = 6$ mW. The resistors take
$8 + 1 + 6 + 3 = 18$ mW, and $12 + 6 = 18$.

## The mistakes that actually happen

**Using the supernode equation and forgetting the constraint.** Two unknowns, one
equation, and the system has no unique solution — but it is easy not to notice, because
the one equation you did write looks entirely reasonable. Write $v_a - v_b = E$ down
*first*, immediately after drawing the surface, and the mistake cannot happen.

**Getting the sign of the constraint backwards.** $v_a - v_b = E$ or $v_b - v_a = E$
depends only on which terminal carries the $+$. The result of getting it wrong is a
perfectly plausible set of node voltages that are simply not the circuit's. There is a
cheap check: after solving, look at whether the node you expected to be higher actually
is.

**Trying to write KCL at one end of a floating source.** People attempt it because the
node looks ordinary from the other three sides. The sum then has an unknown current in it
that appears in no other equation, and the system will not close. The moment a branch is a
source rather than a resistor, that node loses its individual equation and joins a
supernode.

**Assuming a current source has no voltage across it, or a voltage source no current
through it.** Both are the same error, and it is a natural one: the quantity that is *not*
specified feels like it ought to be zero. It is not zero, it is unknown, and it comes out
of the solve. A 3 mA source with 4 V across it is delivering 12 mW, and a circuit whose
power does not balance usually has a source whose forgotten quantity was quietly set to
nothing.

**Reading the matrix off a circuit that has a floating source in it.** The
write-it-by-inspection rules assume every branch between unknown nodes is a resistor. A
supernode row is not of that form, so it has to be written by hand. The shortcut is for
the common case, not the general one.

## Where this stops

**Dependent sources.** A source whose value is proportional to a voltage or current
elsewhere puts an unknown on the right-hand side of the equation, and moving it to the
left destroys the symmetry: $G$ stops being symmetric, and the by-inspection rules stop
applying. The equations are still linear and still solvable — the whole of transistor
small-signal analysis is this — but every term has to be written out.

**Nodes with no resistive path to ground.** Nodal analysis assumes every unknown node is
tied to the reference by *something*. Two capacitors in series across a supply, with
nothing else on the node between them, has no DC answer: the node can sit at any voltage
at all, and the solver will tell you the system is singular rather than guess. Real
circuits solve it with a large resistor to ground, and real simulators quietly add one.

**Time.** Every equation here has been algebraic because DC means nothing changes.
Introduce a capacitor and its branch current becomes $C\,\mathrm{d}v/\mathrm{d}t$; the
node equations become differential equations, and the same KCL that has been producing
arithmetic starts producing exponentials. The setup does not change at all. What changes
is what you have to solve, and that is the subject of the next course.

**Frequency.** Between those two there is a middle case that costs almost nothing. If
everything is a sinusoid at one frequency, a capacitor can be written as an admittance
$j\omega C$ and an inductor as $1/(j\omega L)$, and every equation in this module holds
unchanged with complex numbers in place of real ones. Same matrix, same rules, same
inspection shortcut. That is not a coincidence or an analogy: it is the same linear
algebra, and it is the reason this module is worth doing properly.
''',
                },
            ],
            "quiz": {
                "title": "Setting up the equations",
                "minutes": 10,
                "questions": [
                    {
                        "q": "In nodal analysis, what are the unknowns being solved for?",
                        "opts": [
                            "the current in every branch",
                            "the voltage of every node except ground",
                            "the resistance of every component",
                            "the power dissipated at each node",
                        ],
                        "a": 1,
                        "why": r'''
The node voltages, and nothing else. Branch currents are not unknowns — each one
follows from two node voltages and Ohm's law the moment the solve is finished, which
is exactly why there are fewer equations this way. A network of eight resistors can
easily have eight branch currents and only two unknown node voltages.
''',
                    },
                    {
                        "q": "A circuit has five nodes. You nominate one as ground, and one of the others is held at a fixed voltage by a supply. How many KCL equations must you write?",
                        "opts": ["five", "four", "three", "two"],
                        "a": 2,
                        "why": r'''
Three. Ground is not an unknown because you defined it as 0 V, and the supply node is
not an unknown because the supply has already answered for it — its equation is
$v = E$, written down without any thought. That leaves three genuinely unknown nodes
and three equations, which is the smallest system this circuit can be reduced to.
''',
                    },
                    {
                        "q": "Node $a$ sits at $v_a$ and node $b$ at $v_b$, joined by a resistance $R$. What is the current leaving node $a$ through that resistor?",
                        "opts": [
                            "$(v_a - v_b)/R$",
                            "$(v_b - v_a)/R$",
                            "$v_a/R$",
                            "$(v_a + v_b)/R$",
                        ],
                        "a": 0,
                        "why": r'''
Ohm's law with the voltage across the resistor written as the difference of the two
ends, and the subtraction ordered so that current flows away from the node you are
standing on when that node is the higher one. Writing $v_a/R$ instead is the error to
watch for: it silently assumes the far end is at 0 V, which is only true when the far
end really is ground.
''',
                    },
                    {
                        "q": "In a two-supply circuit, a node settles at 8 V while one of the supplies holding a branch is only 5 V. What is happening in that branch?",
                        "opts": [
                            "nothing — a 5 V supply cannot be connected to an 8 V node",
                            "current flows out of the 5 V supply into the node, as usual",
                            "current flows from the node into the 5 V supply, which is absorbing power",
                            "the node voltage must have been calculated wrongly",
                        ],
                        "a": 2,
                        "why": r'''
Current runs from the higher potential to the lower one through a resistor, so with the
node above the supply it flows *into* that supply — which is then absorbing power
rather than delivering it, exactly as a battery does while it is being charged.
Nothing about the analysis has to change to allow for this: the term
$(v - E_2)/R_2$ simply comes out positive when written as a current leaving the node.
Nodal analysis never needs to be told which way round anything is.
''',
                    },
                    {
                        "q": "Why does the ground node get no equation of its own?",
                        "opts": [
                            "because no current flows into ground",
                            "because its voltage is already known, and its KCL equation carries nothing the others do not",
                            "because ground is not really a node",
                            "because KCL does not apply to ground",
                        ],
                        "a": 1,
                        "why": r'''
Its voltage is 0 V by your own choice, so there is nothing to solve for. KCL does hold
at ground — a great deal of current flows into it — but that equation is the sum of
all the others with the sign reversed, so it adds no information and would make the
system unsolvable if included. One reference node, one equation dropped, every time.
''',
                    },
                    {
                        "q": "A 4 V source sits between two nodes, and neither of them is ground. What do you write?",
                        "opts": [
                            "KCL at each of the two nodes separately, with the source's current as a third unknown",
                            "one KCL equation over a surface enclosing both nodes, plus $v_a - v_b = 4$",
                            "nothing — the circuit cannot be solved by nodal analysis",
                            "KCL at each node, treating the source as a 0 Ω resistor",
                        ],
                        "a": 1,
                        "why": r'''
That pair is the supernode. Enclosing both ends puts the source's current entirely
inside the surface, so it crosses no boundary and appears in no equation, and every
branch that *does* cross is a resistor and yields to Ohm's law. One equation short for
two unknowns, and the source's own $v_a - v_b = 4$ makes up the difference. Treating
it as a 0 Ω resistor would force the two nodes to the same voltage, which is a
different circuit; and writing KCL separately at each node does work, but only by
carrying an extra unknown that the supernode was invented to avoid.
''',
                    },
                    {
                        "q": "A 2 mA current source pushes current into a node. What does it contribute to that node's equation, and what is the voltage across it?",
                        "opts": [
                            "a known −2 mA term; its voltage comes out of the solve like everything else",
                            "a known −2 mA term; the voltage across a current source is zero",
                            "an unknown term, because its voltage is unknown",
                            "nothing, until its terminal voltage has been worked out first",
                        ],
                        "a": 0,
                        "why": r'''
A current source is the easy case, because the node equation is a sum of currents and
a current source states one outright. Written with every current as leaving the node, a
source pushing 2 mA *in* contributes $-2$ mA and no algebra at all. Its terminal
voltage is not zero — a source with no voltage across it would deliver no power — it is
simply not specified in advance, and falls out of the finished solve along with the
node voltages.
''',
                    },
                    {
                        "q": "Every branch leaving a node ends at +12 V, at +5 V, or at ground, through a resistor, and there is nothing else in the circuit. Which value can the node voltage NOT take?",
                        "opts": ["3.9 V", "8.4 V", "11.6 V", "12.4 V"],
                        "a": 3,
                        "why": r'''
12.4 V. Rearranging the node equation shows the answer is a conductance-weighted
average of the voltages at the far ends of the branches — here 12, 5 and 0 — and an
average of a set of numbers cannot lie outside the range those numbers span. So
anything from 0 V to 12 V is reachable with the right resistors, and nothing above 12
or below 0 is reachable with any. It is the cheapest check in the subject: a resistive
network driven by these supplies can never produce a voltage outside their range, and a
result that does means an arithmetic slip, not an interesting circuit.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "Two nodes, two equations, one solve",
                    "minutes": 10,
                    "caption": "clear the fractions, eliminate, then check the whole thing by reduction",
                    "lang": "text",
                    "brief": r'''
A ladder this time, which means the answer can be had two ways — nodal, and by collapsing
the network the way module 3 did. Doing it both ways on a circuit simple enough to see
through is how you learn to trust the equations on one that is not.

Volts, milliamps and kilohms throughout. Those three are consistent with one another, so
no factor of a thousand can go missing anywhere below.
''',
                    "listing": r'''
24 V, then 4 kohm into node A; 8 kohm from A to ground;
4 kohm from A across to node B; 4 kohm from B to ground.
------------------------------------------------------------

  two unknowns, vA and vB, so two equations. Every current below
  is written as LEAVING the node it belongs to.

    at A:   (vA - 24)/4  +  vA/8  +  (vA - vB)/4   =  0
    at B:   (vB - vA)/4  +  vB/4                   =  0

  clear the fractions in the first by multiplying through by 8:

    2*(vA - 24)  +  vA  +  2*(vA - vB)             =  0
    2vA - 48 + vA + 2vA - 2vB                      =  0
              ___*vA  -  2*vB                      =  48      (1)

  and in the second by multiplying through by 4:

    (vB - vA)  +  vB                               =  0
              vA                                   =  ___*vB  (2)

  substitute (2) into (1):

    5*(2vB) - 2vB                                  =  48
    8vB                                            =  48
    vB                                             =  ___ V
    vA                                             =  12 V

  now the check, by collapsing the network from the far end:

    4k + 4k in the B branch                        =  8 kohm
    that 8k in parallel with the 8k from A         =  4 kohm
    plus the 4k from the supply                    =  8 kohm
    I(supply)  =  24 / 8                           =  3.00 mA
    drop on the first 4k  =  3.00 * 4              =  12.0 V
    vA         =  24 - 12.0                        =  12.0 V   agrees

  and the split at A, which is KCL again with numbers in it:

    I(8k to ground)   =  12 / 8                    =  ___ mA
    I(into B branch)  =  12 / 8                    =  1.50 mA
                                                      --------
                                                      3.00 mA
''',
                    "blanks": [
                        {
                            "prompt": "Gathering the $v_A$ terms of $2v_A - 48 + v_A + 2v_A - 2v_B$. What multiplies $v_A$?",
                            "hole": "?",
                            "opts": ["5", "3", "4", "2"],
                            "a": 0,
                            "why": "$2 + 1 + 2 = 5$. There is one $v_A$ term from every branch touching A, "
                                   "which is the general rule: the coefficient of a node's own voltage is "
                                   "the sum of the conductances of everything attached to it, and it is "
                                   "always positive. Getting 3 means one of the three branches was left "
                                   "out — most often the one going across to B, because it is the only "
                                   "one whose far end is not a number.",
                        },
                        {
                            "prompt": "$(v_B - v_A) + v_B = 0$. Rearranged, $v_A$ equals how many $v_B$?",
                            "hole": "?",
                            "opts": ["2", "1", "4", "0.5"],
                            "a": 0,
                            "why": "$2v_B = v_A$, so A sits at twice B. That is the two equal 4 kΩ "
                                   "resistors below B acting as a divider on whatever A happens to be: B "
                                   "gets half. Answering 0.5 is the divider read the wrong way round, and "
                                   "it fails a sanity check that costs nothing — B is further from the "
                                   "supply than A is, so B cannot be the higher of the two.",
                        },
                        {
                            "prompt": "$8v_B = 48$. What is $v_B$, in volts?",
                            "hole": "?",
                            "opts": ["6", "8", "3", "12"],
                            "a": 0,
                            "why": "$48/8 = 6.00$ V, and $v_A = 2v_B = 12.0$ V. Both land inside the range "
                                   "0 V to 24 V, as every node in a resistive network driven by a single "
                                   "24 V supply must. The value 12 is $v_A$, one line early.",
                        },
                        {
                            "prompt": "12.0 V across the 8 kΩ from A to ground. How many milliamps?",
                            "hole": "?",
                            "opts": ["1.50", "3.00", "0.67", "2.00"],
                            "a": 0,
                            "why": "$12/8 = 1.50$ mA, and the other 1.50 mA of the supply's 3.00 mA goes "
                                   "off into the B branch — which is also 8 kΩ once its two resistors are "
                                   "added, so an equal split is exactly right. Two branches of equal "
                                   "resistance across the same voltage take equal currents, and that is "
                                   "the arithmetic checking itself.",
                        },
                    ],
                },
                {
                    "title": "The supernode, line by line",
                    "minutes": 10,
                    "caption": "one surface, one constraint, and the source's current recovered at the end",
                    "lang": "text",
                    "brief": r'''
A 6 V source floating between two unknown nodes — neither of them ground — which is the
one arrangement an ordinary node equation cannot handle. The surface goes round both ends,
the source's current stays inside it, and the source's own voltage supplies the equation
that the surface cost you.

Watch the last block especially. The current through the floating source was deliberately
kept out of the equations, and it still comes back at the end, from plain KCL at one node
once the voltages are known.
''',
                    "listing": r'''
12 V rail, then 1 kohm into node A; 10 kohm from A to ground;
a 6 V source from A across to node B, + terminal on the A side;
4 kohm from B to ground.
------------------------------------------------------------------

  A and B are both unknown and the branch between them is a source,
  so neither gets an equation of its own. Draw one surface round
  both, and write what CROSSES it, every term leaving:

    from A, towards the 12 V rail      (vA - 12)/1
    from A, down to ground              vA/10
    from B, down to ground              vB/4

    (vA - 12)/1  +  vA/10  +  vB/4              =  0        (1)

  the source is inside the surface, so its current is in none of
  those terms. What it does contribute is its voltage:

    vA - vB                                     =  ___ V    (2)

  substitute vA = vB + 6 into (1) and multiply through by 20:

    20*(vB - 6)  +  2*(vB + 6)  +  ___*vB       =  0
    20vB - 120 + 2vB + 12 + 5vB                 =  0
                                          27vB  =  108
                                            vB  =  ___ V
                                            vA  =  10.0 V

  the currents, one division each:

    1k  from the rail to A    (12 - 10)/1       =  2.00 mA  into A
    10k from A to ground             10/10      =  1.00 mA  out of A
    4k  from B to ground               4/4      =  1.00 mA  out of B

    across the surface:  2.00  =  1.00 + 1.00              closes

  and now the source's own current, from KCL at A alone:

    in at A                                     =  2.00 mA
    out at A through the 10k                    =  1.00 mA
                                                   --------
    into the source at A                        =  ___ mA
''',
                    "blanks": [
                        {
                            "prompt": "The floating source is 6 V with its + terminal on the A side. What does $v_A - v_B$ equal?",
                            "hole": "?",
                            "opts": ["6", "-6", "0", "12"],
                            "a": 0,
                            "why": "$+6$ V. The $+$ terminal is the higher one by definition, and it is on "
                                   "A, so A is 6 V above B. Answering $-6$ is the single most common way "
                                   "to lose a supernode: the equations still solve, the node voltages "
                                   "still look plausible, and they are the answer to a circuit with the "
                                   "source turned round. Answering 0 treats the source as a wire, which "
                                   "is a different circuit again.",
                        },
                        {
                            "prompt": "Multiplying $v_B/4$ through by 20. What multiplies $v_B$?",
                            "hole": "?",
                            "opts": ["5", "4", "20", "80"],
                            "a": 0,
                            "why": "$20/4 = 5$. The 20 was chosen because it clears all three denominators "
                                   "at once — 1, 10 and 4 — and the term with the 4 under it is the one "
                                   "that decides it. Answering 80 multiplies by 20 instead of dividing, "
                                   "which is what happens when the 4 is read as a factor rather than a "
                                   "denominator.",
                        },
                        {
                            "prompt": "$27v_B = 108$. What is $v_B$, in volts?",
                            "hole": "?",
                            "opts": ["4", "6", "10", "3"],
                            "a": 0,
                            "why": "$108/27 = 4.00$ V, and then $v_A = v_B + 6 = 10.0$ V. Both sit between "
                                   "0 V and 12 V, which they must: the rail is the only source of energy "
                                   "in the circuit and the 6 V source only redistributes what reaches it. "
                                   "The value 10 is $v_A$, one line early.",
                        },
                        {
                            "prompt": "2.00 mA arrives at A and 1.00 mA leaves down the 10 kΩ. How much goes into the source?",
                            "hole": "?",
                            "opts": ["1.00", "3.00", "2.00", "0"],
                            "a": 0,
                            "why": "KCL at A on its own: $2.00 - 1.00 = 1.00$ mA has nowhere else to go, so "
                                   "it goes through the source — and it arrives at B in time to be the "
                                   "1.00 mA that leaves through the 4 kΩ, which is the check. This is the "
                                   "current the supernode equation was built to avoid needing, and it "
                                   "still comes back for free once the node voltages are known. Answering "
                                   "0 assumes a source carries no current, which would make it no "
                                   "different from a break in the wire.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One node, two supplies",
                    "minutes": 5,
                    "brief": r'''
The mechanical one, to get the routine under your fingers. Two supplies of different
voltages reach the same point, each through its own resistor, and there is nothing else in
the circuit.

Nothing here is in series with anything — no two resistors carry the same current — and
nothing is in parallel with anything, because no two have the same voltage across them. So
the recognition rules have nothing to say, and one node equation settles it in a line.
''',
                    "prompt": "What voltage does the probe read at node A?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 3, "value": 2000},
                            {"id": "r2", "kind": "R", "x": 14, "y": 3, "value": 1000},
                            {"id": "v2", "kind": "V", "x": 19, "y": 7, "rot": 1, "value": 3},
                            {"id": "g1", "kind": "GND", "x": 19, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [13, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [15, 3], "b": [19, 3]},
                            {"a": [19, 3], "b": [19, 6]},
                            {"a": [19, 8], "b": [19, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Left supply", "value": "12.0 V"},
                        {"label": "R1, from the left supply to A", "value": "2.00 kΩ"},
                        {"label": "R2, from A to the right supply", "value": "1.00 kΩ"},
                        {"label": "Right supply", "value": "3.00 V"},
                    ],
                    "aside": "Work in volts, milliamps and kilohms. One volt across one kilohm is one "
                             "milliamp, so the three units are consistent and no factor of a thousand "
                             "can go missing.",
                    "answer": 6.0,
                    "tol": 0.02,
                    "unit": "V",
                    # The probe decides which node is measured, so this reads the solve rather
                    # than repeating any number that appears on the drawing.
                    "check": "return c.vout();",
                    "hint": "Call the node voltage $v$ and write both currents as leaving it: "
                            "$(v-12)/2$ towards the left supply and $(v-3)/1$ towards the right one. "
                            "KCL says they add to zero.",
                    "wrong": "If you got 7.50, that is the plain average of 12 and 3 — right only if "
                             "the two resistors were equal, and they are not. If you got 9.00, the two "
                             "resistances have been swapped: the smaller resistance pulls the node "
                             "harder, and here the 1 kΩ is the branch to the 3 V supply, so the answer "
                             "has to land nearer 3 V than the midpoint of 7.50 V, not further away.",
                    "why": r'''
```
    (v - 12)/2  +  (v - 3)/1            =  0

multiply through by 2 and the fractions clear:

    (v - 12)  +  2*(v - 3)              =  0
    3v - 18                             =  0
    v                                   =  6.00 V
```

The currents follow, one division each: $(12-6)/2 = 3.00$ mA arrives from the left supply
and $(6-3)/1 = 3.00$ mA leaves into the right one, which is the same 3 mA because there is
nowhere else for it to go. The right-hand supply is *absorbing* 9 mW, exactly as a battery
does on charge, and nothing in the setup had to know that in advance.

Notice where 6 V sits. Rearranged, the node equation says

$$v = \frac{12/2 + 3/1}{1/2 + 1/1} = \frac{9}{1.5} = 6.00\ \text{V}$$

which is a weighted average of 12 and 3, with each weight the *conductance* of its branch.
The 1 kΩ branch has twice the conductance of the 2 kΩ one, so it pulls twice as hard, and
the answer lands nearer 3 V than the plain midpoint of 7.5 V. Every nodal answer you ever
produce is a weighted average of that kind, and checking that it lies between the highest
and lowest voltage attached to the node costs nothing.
''',
                },
                {
                    "title": "Three branches, and the heat in the one that goes to ground",
                    "minutes": 7,
                    "brief": r'''
The same shape with a third branch on it: two supplies reaching node A, and a resistor from
A straight down to ground. Still one unknown, still one equation — the extra branch adds a
term and nothing else.

What is asked for is a power, so there is a step after the node voltage. Pick the form of
the power law built out of the quantities you already have rather than the one you happen
to remember first.
''',
                    "prompt": "How much power does the 3.00 kΩ resistor turn into heat?",
                    "note": "Give the answer in milliwatts, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 18},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 3, "value": 6000},
                            {"id": "r3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 3000},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 9},
                            {"id": "r2", "kind": "R", "x": 19, "y": 3, "value": 2000},
                            {"id": "v2", "kind": "V", "x": 23, "y": 7, "rot": 1, "value": 12},
                            {"id": "g2", "kind": "GND", "x": 23, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 1},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [18, 3]},
                            {"a": [13, 3], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                            {"a": [11, 3], "b": [11, 1]},
                            {"a": [20, 3], "b": [23, 3]},
                            {"a": [23, 3], "b": [23, 6]},
                            {"a": [23, 8], "b": [23, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Left supply", "value": "18.0 V"},
                        {"label": "R1, from the left supply to A", "value": "6.00 kΩ"},
                        {"label": "R3, from A down to ground", "value": "3.00 kΩ"},
                        {"label": "R2, from A to the right supply", "value": "2.00 kΩ"},
                        {"label": "Right supply", "value": "12.0 V"},
                    ],
                    "aside": "Three branches leave node A and every one of them ends somewhere whose "
                             "voltage you already know — 18 V, 12 V, and 0 V. That is what makes this "
                             "a single equation rather than a system.",
                    "answer": 27.0,
                    "tol": 0.3,
                    "unit": "mW",
                    # The prompt names the resistor that runs from the probed node to ground, so
                    # the check finds it by that description and takes its drop and its value out
                    # of the solve rather than restating either.
                    "check": r'''
const d = c.dc();
const out = c.outNode();
const r = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
})[0];
const dv = d.v[r.n1] - d.v[r.n2];
return dv * dv / r.value * 1000;
''',
                    "hint": "Three terms, all written as leaving A: $(v-18)/6$, $(v-12)/2$ and $v/3$. "
                            "Multiply through by 6 to clear them, solve for $v$, and only then reach "
                            "for the power law.",
                    "wrong": "If you got 13.5, that is the heat in the 6 kΩ rather than the 3 kΩ. "
                             "If you got 81.0, the node voltage has been squared and divided by 1000 "
                             "instead of 3000 — milliwatts come out of volts squared over kilohms "
                             "directly, with no extra factor. If you got 3.00, that is the current in "
                             "milliamps, one step short.",
                    "why": r'''
```
    (v - 18)/6  +  (v - 12)/2  +  v/3    =  0

multiply through by 6:

    (v - 18)  +  3*(v - 12)  +  2*v      =  0
    v - 18 + 3v - 36 + 2v                =  0
    6v                                   =  54
    v                                    =  9.00 V
```

Then the power, using the form built from what you now have — the voltage across the
resistor and its resistance:

```
    P  =  v^2 / R  =  9.00^2 / 3.00      =  27.0 mW
```

Volts squared over kilohms lands directly in milliwatts, which is the third member of the
consistent unit family and saves the usual hunt for a factor of a thousand.

The currents are worth collecting even though nobody asked, because they check the answer
with a law that took no part in producing it:

```
    from the 18 V   (18 - 9)/6           =  1.50 mA   into A
    from the 12 V   (12 - 9)/2           =  1.50 mA   into A
    down the 3k            9 /3          =  3.00 mA   out of A
                                            --------
                                            3.00 mA   KCL closes
```

Both supplies are delivering, because 9 V is below both of them. The 18 V supply provides
27 mW and the 12 V supply 18 mW, a total of 45 mW; the three resistors take
$1.5^2 \times 6 = 13.5$, $1.5^2 \times 2 = 4.5$ and 27.0 mW, which is 45.0 mW again.
''',
                },
                {
                    "title": "Sizing the third branch",
                    "minutes": 8,
                    "brief": r'''
The same circuit shape as the last one, run backwards. The node voltage is the thing you
are told, and one of the resistors is the thing you have to find — which is how this
arithmetic is actually used, because in a real design the wanted voltage is the
specification and the components are the free variables.

No schematic for this one: a schematic would have to print the value you are being asked
for.
''',
                    "prompt": "What resistance must the third branch have?",
                    "note": "Give the answer in kilohms, to two decimal places.",
                    "figure": "A 12.0 V supply reaches node A through 2.00 kΩ. A 6.00 kΩ resistor "
                              "runs from A straight down to ground. A third branch runs from A through "
                              "an unknown resistance to the positive terminal of a 2.00 V supply, whose "
                              "negative terminal is on ground. With all three branches connected, a "
                              "high-impedance meter on A reads exactly 6.00 V.",
                    "given": [
                        {"label": "Left supply", "value": "12.0 V"},
                        {"label": "From the left supply to A", "value": "2.00 kΩ"},
                        {"label": "From A down to ground", "value": "6.00 kΩ"},
                        {"label": "Third supply", "value": "2.00 V"},
                        {"label": "Measured at A", "value": "6.00 V"},
                    ],
                    "aside": "The node equation is linear in every conductance, so an unknown resistance "
                             "is no harder than an unknown voltage — write the same three terms, put "
                             "the known $v$ into all of them, and one unknown is left standing.",
                    "answer": 2.0,
                    "tol": 0.02,
                    "unit": "kΩ",
                    "hint": "Write KCL at A with $v = 6$ substituted straight in: "
                            "$(6-12)/2 + 6/6 + (6-2)/R = 0$. Two of those three are numbers.",
                    "wrong": "If you got 4.00, the numerator $6 - 2 = 4$ has been divided by the wrong "
                             "current — the branch carries 2.00 mA, not 1.00 mA. If you got 0.50, that "
                             "is the conductance in millisiemens and needs one more reciprocal. If you "
                             "got 3.00, the far end of the new branch has been taken as ground rather "
                             "than as the 2 V supply: that is 6 V across it instead of 4 V, at the same "
                             "2.00 mA.",
                    "why": r'''
```
KCL at A, every current written as leaving, with v = 6.00 already in:

    (6 - 12)/2   +   6/6   +   (6 - 2)/R    =  0
      -3.00      +  1.00   +      4/R       =  0
                                    4/R     =  2.00
                                      R     =  2.00 kohm
```

Read the three terms back as currents and the answer is obvious in hindsight. The 12 V
supply pushes 3.00 mA into the node. The 6 kΩ takes 1.00 mA of it down to ground. The
other 2.00 mA has to go somewhere, and the only place left is the third branch — which has
4.00 V across it, since A is at 6 V and the far end is held at 2 V. Four volts at two
milliamps is two kilohms.

That last branch is running *into* its supply: the node is above 2 V, so current flows from
the circuit into the source, which absorbs $2.00 \times 2.00 = 4.00$ mW. It is worth
checking the whole budget, because a design that only balances by accident usually does not
balance:

```
    P from the 12 V   =  12 * 3.00        =  36.0 mW
    into the  2 V     =   2 * 2.00        =   4.00 mW  absorbed
    P(2k)             =  3.00^2 * 2       =  18.0 mW
    P(6k)             =  1.00^2 * 6       =   6.00 mW
    P(new 2k)         =  2.00^2 * 2       =   8.00 mW
                                             --------
    out:  4.00 + 18.0 + 6.00 + 8.00       =  36.0 mW
```

One more thing worth noticing, because it is the difference between this and a design that
works. A voltage divider from 12 V that produced 6.00 V would need the 2 kΩ and something
close to 2 kΩ below it, and it would collapse the moment anything else was hung on the
node. Here the node is held at 6 V *by three branches at once*, and the third one is doing
the opposite of what a divider's lower resistor does — it is pulling current out towards a
2 V rail rather than towards ground. Nodal analysis does not care which; it just adds up
conductances and the voltages they lead to.
''',
                },
                {
                    "title": "Two nodes and a current source",
                    "minutes": 10,
                    "brief": r'''
Two unknown node voltages now, which means two equations and a genuine simultaneous solve.
The circle with an arrow in it, hanging below node A, is a **current source**: a block that
draws the same current out of that node whatever the voltage there turns out to be, which
is how a chip's supply current is modelled long before anyone knows what is inside it.

A current source is the easy kind of source for this method. Its current is already the
quantity the node equation wants, so it goes into the sum as a plain number. What it does
not tell you is the voltage across itself — that comes out of the solve like everything
else.
''',
                    "prompt": "What voltage does the probe read at node B?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 9, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 12},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 2000},
                            {"id": "i1", "kind": "I", "x": 11, "y": 8, "rot": 1, "value": 0.002},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "r2", "kind": "R", "x": 15, "y": 6, "value": 2000},
                            {"id": "r4", "kind": "R", "x": 19, "y": 4, "rot": 1, "value": 8000},
                            {"id": "r3", "kind": "R", "x": 19, "y": 8, "rot": 1, "value": 2000},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 11},
                            {"id": "out", "kind": "OUT", "x": 22, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 10], "b": [3, 12]},
                            {"a": [3, 8], "b": [3, 2]},
                            {"a": [3, 2], "b": [19, 2]},
                            {"a": [11, 2], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 9], "b": [11, 11]},
                            {"a": [11, 6], "b": [14, 6]},
                            {"a": [16, 6], "b": [19, 6]},
                            {"a": [19, 2], "b": [19, 3]},
                            {"a": [19, 5], "b": [19, 7]},
                            {"a": [19, 9], "b": [19, 11]},
                            {"a": [19, 6], "b": [22, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Supply rail", "value": "12.0 V"},
                        {"label": "R1, rail down to A", "value": "2.00 kΩ"},
                        {"label": "Load on A", "value": "2.00 mA, constant"},
                        {"label": "R2, from A across to B", "value": "2.00 kΩ"},
                        {"label": "R4, rail down to B", "value": "8.00 kΩ"},
                        {"label": "R3, from B down to ground", "value": "2.00 kΩ"},
                    ],
                    "aside": "Both A and B are unknown, so both get an equation, and the 2 kΩ between "
                             "them appears in each — as $(v_A - v_B)/2$ in one and $(v_B - v_A)/2$ in "
                             "the other. Those two terms are the only coupling between the equations.",
                    "answer": 4.0,
                    "tol": 0.02,
                    "unit": "V",
                    "check": "return c.vout();",
                    "hint": "At A: $(v_A - 12)/2 + 2 + (v_A - v_B)/2 = 0$ — the current source's 2 mA "
                            "is drawn out of A, so it is a leaving current and enters with a plus sign. "
                            "At B: $(v_B - v_A)/2 + (v_B - 12)/8 + v_B/2 = 0$.",
                    "wrong": "If you got 6.00, that is $v_A$ rather than $v_B$ — the probe is on the "
                             "right-hand node. If you got 6.29, the current source has been given the "
                             "wrong sign: it takes current *out* of A, so written among the currents "
                             "leaving that node its term is $+2$, and flipping it lifts both node "
                             "voltages instead of pulling them down. If you got 5.14, the 2 mA has "
                             "been left out of node A's equation altogether.",
                    "why": r'''
```
at A, every current written as leaving:

    (vA - 12)/2  +  2.00  +  (vA - vB)/2    =  0      the 2 mA leaves A

at B, likewise:

    (vB - vA)/2  +  (vB - 12)/8  +  vB/2    =  0

clear the first by multiplying by 2:

    (vA - 12)  +  4.00  +  (vA - vB)        =  0
                        2vA  -  vB          =  8      (1)

and the second by multiplying by 8:

    4*(vB - vA)  +  (vB - 12)  +  4*vB      =  0
                     - 4vA  +  9vB          =  12     (2)

(1) times 2, then add to (2) to kill vA:

     4vA  -  2vB   =  16
    -4vA  +  9vB   =  12
    -------------------
             7vB   =  28        so  vB  =  4.00 V

back into (1):   2vA  =  8 + 4.00  =  12,   vA  =  6.00 V
```

Now every current, one division each, and both nodes check:

```
    R1, rail to A       (12 - 6)/2         =  3.00 mA   into A
    the load                                  2.00 mA   out of A
    R2, A to B           (6 - 4)/2         =  1.00 mA   out of A
      KCL at A:  3.00  =  2.00 + 1.00                   closes

    R4, rail to B       (12 - 4)/8         =  1.00 mA   into B
    R3, B to ground            4 /2        =  2.00 mA   out of B
      KCL at B:  1.00 + 1.00  =  2.00                   closes
```

The current source has 6.00 V across it and is drawing 2.00 mA, so it is absorbing 12.0 mW
— and nothing said what that voltage would be until the solve was finished. That is the
whole character of a current source: it fixes the current and leaves the voltage to the
circuit, which is the exact mirror of what a voltage source does.

The rail delivers $3.00 + 1.00 = 4.00$ mA at 12 V, or 48.0 mW. The load takes 12.0 mW and
the four resistors take $3^2 \times 2 = 18.0$, $1^2 \times 2 = 2.00$, $1^2 \times 8 = 8.00$
and $2^2 \times 2 = 8.00$ mW — 36.0 mW between them. $12.0 + 36.0 = 48.0$.
''',
                },
                {
                    "title": "The source that floats",
                    "minutes": 12,
                    "brief": r'''
The hardest arrangement in the module, and the only one an ordinary node equation cannot
touch. The 4 V source in the middle has neither terminal on ground: it sits between two
nodes whose voltages are both unknown, and there is no way to write its current in terms of
them, because a voltage source's current is whatever the circuit demands.

So neither of those two nodes gets an equation of its own. Draw one surface round both of
them, write KCL for everything that crosses it — all resistors, all Ohm's law — and let the
source's own 4 V supply the second equation. That pair is a supernode.

What is asked for is the current *in the source itself*, which is precisely the quantity
the supernode equation was built to avoid needing. Solve for the node voltages first; it
comes back at the end from plain KCL at one node.
''',
                    "prompt": "What current flows through the 4.00 V source?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 9, "rot": 1, "value": 15},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 12},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 3000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 4000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "v2", "kind": "V", "x": 15, "y": 6, "value": 4},
                            {"id": "r4", "kind": "R", "x": 19, "y": 4, "rot": 1, "value": 10000},
                            {"id": "r3", "kind": "R", "x": 19, "y": 8, "rot": 1, "value": 5000},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 11},
                        ],
                        "wires": [
                            {"a": [3, 10], "b": [3, 12]},
                            {"a": [3, 8], "b": [3, 2]},
                            {"a": [3, 2], "b": [19, 2]},
                            {"a": [11, 2], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 9], "b": [11, 11]},
                            {"a": [11, 6], "b": [14, 6]},
                            {"a": [16, 6], "b": [19, 6]},
                            {"a": [19, 2], "b": [19, 3]},
                            {"a": [19, 5], "b": [19, 7]},
                            {"a": [19, 9], "b": [19, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Supply rail", "value": "15.0 V"},
                        {"label": "R1, rail down to node A (left)", "value": "3.00 kΩ"},
                        {"label": "R2, from A down to ground", "value": "4.00 kΩ"},
                        {"label": "Floating source, + terminal on the B side", "value": "4.00 V"},
                        {"label": "R4, rail down to node B (right)", "value": "10.0 kΩ"},
                        {"label": "R3, from B down to ground", "value": "5.00 kΩ"},
                    ],
                    "aside": "Four branches cross the surface — two at A and two at B — and all "
                             "four are resistors with a known voltage at the far end. The fifth branch, "
                             "the source, is inside the surface and appears in no term.",
                    "answer": 1.5,
                    "tol": 0.02,
                    "unit": "mA",
                    # The floating source is the one whose two nodes are both non-zero, so the
                    # check identifies it by the property that makes it float rather than by its
                    # value. The solver's sign for a source current is positive when it absorbs;
                    # the prompt asks only how much flows.
                    "check": r'''
const d = c.dc();
const floating = c.net.parts.filter(function (p) {
  return p.kind === 'V' && p.n1 !== 0 && p.n2 !== 0;
});
c.assert(floating.length === 1, 'expected exactly one floating source');
return Math.abs(d.currents[floating[0].id]) * 1000;
''',
                    "hint": "One surface round A and B. Crossing it: $(v_A-15)/3$, $v_A/4$, "
                            "$(v_B-15)/10$ and $v_B/5$, all leaving, summing to zero. The second "
                            "equation is the source: with + on the B side, $v_B - v_A = 4$.",
                    "wrong": "If you got 0.50, that is the current in the 10 kΩ, not in the source. "
                             "If you got 2.00, that is the current in the 5 kΩ — which would be the "
                             "source's current only if B had no other branch feeding it, and it has. "
                             "If you got 3.00, that is what arrives at node A through the 3 kΩ, before "
                             "the 4 kΩ has taken its share. And if the constraint went in the wrong way "
                             "round — $v_A - v_B = 4$ describes the same source turned end for end — "
                             "every node voltage still comes out looking plausible and none of them is "
                             "this circuit's; the cheap check is whether the node you expected to be "
                             "higher actually is.",
                    "why": r'''
```
unknowns vA and vB. The 4 V source floats, so one surface goes round
both nodes and every term below is a current LEAVING that surface:

    from A, up to the 15 V rail       (vA - 15)/3
    from A, down to ground             vA/4
    from B, up to the 15 V rail       (vB - 15)/10
    from B, down to ground             vB/5

    (vA - 15)/3 + vA/4 + (vB - 15)/10 + vB/5    =  0        (1)

and the source itself, + terminal on the B side:

    vB - vA                                     =  4        (2)

put vA = vB - 4 into (1) and multiply through by 60:

    20*(vB - 19)  +  15*(vB - 4)  +  6*(vB - 15)  +  12*vB  =  0
    20vB - 380 + 15vB - 60 + 6vB - 90 + 12vB                =  0
                                                      53vB  =  530
                                                        vB  =  10.0 V
                                                        vA  =  6.00 V
```

Collect the four branch currents and the surface balances:

```
    R1, rail to A       (15 -  6)/3        =  3.00 mA   into A
    R2, A to ground            6 /4        =  1.50 mA   out of A
    R4, rail to B       (15 - 10)/10       =  0.50 mA   into B
    R3, B to ground           10 /5        =  2.00 mA   out of B

    across the surface:  3.00 + 0.50  =  1.50 + 2.00     closes
```

Now the source's own current, which no equation above contained. Stand at A alone: 3.00 mA
arrives through the 3 kΩ, 1.50 mA leaves down the 4 kΩ, and the difference has nowhere to
go but through the source.

```
    into the source at A   =  3.00 - 1.50  =  1.50 mA
```

It arrives at B just in time to make up the 2.00 mA leaving through the 5 kΩ, alongside the
0.50 mA coming down the 10 kΩ: $1.50 + 0.50 = 2.00$. That is KCL at B, and it is the check
that the whole solve is consistent.

Current enters the source at its $-$ terminal (the A side) and leaves at its $+$, which is
a source *delivering*: it puts $4.00 \times 1.50 = 6.00$ mW into the circuit. The rail
delivers $15 \times (3.00 + 0.50) = 52.5$ mW. The four resistors take
$3^2 \times 3 = 27.0$, $1.5^2 \times 4 = 9.00$, $0.5^2 \times 10 = 2.50$ and
$2^2 \times 5 = 20.0$ mW, or 58.5 mW in total — and $52.5 + 6.00 = 58.5$.

The thing to take away is the bookkeeping. The floating source added an unknown, its own
current, and it added a constraint, $v_B - v_A = 4$. The supernode traded one against the
other: two nodes gave up their separate equations and shared one, and the constraint made
up the difference. Two unknowns, two equations, and the awkward case cost exactly one line
more than an ordinary node.
''',
                },
            ],
            "build": {
                "title": "Two supplies, one node",
                "minutes": 26,
                "brief": r'''
This is the first circuit in the course that no amount of series-and-parallel reduction
will touch. The two supplies are neither in series nor in parallel; there is no pair of
resistors carrying the same current, and none sharing the same voltage. The only way in
is to name the node voltage and write KCL.

The canvas opens with a 12 V supply feeding node A through 1 kΩ, an 8 kΩ resistor from
node A down to ground, and a probe on A. Add a **5 V supply** and one more resistor
between it and node A, choosing that resistor so that

- node A sits at exactly **8.00 V**.

## Two things worth predicting first

Node A ends up *above* 5 V, so the current in your new resistor runs from the node into
the 5 V supply rather than out of it. That supply will be absorbing power, like a
battery on charge, and the checks below insist on it — if your drawing has the
polarity reversed the probe will read a negative voltage and nothing else will make
sense.

And the current out of the 12 V supply is no longer the current through the 8 kΩ. Three
branches meet at node A now, and KCL at that node is the whole of the exercise.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "value": 1000},
                        {"id": "p3", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 8000},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 6},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [9, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [9, 6], "b": [11, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "value": 1000},
                        {"id": "p3", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 8000},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 6},
                        {"id": "p6", "kind": "R", "x": 14, "y": 5, "value": 1000},
                        {"id": "p7", "kind": "V", "x": 17, "y": 6, "rot": 1, "value": 5},
                        {"id": "p8", "kind": "GND", "x": 17, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [9, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [9, 6], "b": [11, 6]},
                        {"a": [9, 5], "b": [13, 5]},
                        {"a": [15, 5], "b": [17, 5]},
                        {"a": [17, 7], "b": [17, 9]},
                    ],
                },
                "checks": [
                    {"name": "two supplies, 12 V and 5 V", "code": r'''
c.assert(c.count('V') === 2,
  'This circuit needs exactly two voltage sources; found ' + c.count('V') + '.');
const vs = c.values('V').slice().sort(function (a, b) { return a - b; });
c.close(vs[0], 5, 0.002, 'the smaller supply');
c.close(vs[1], 12, 0.002, 'the larger supply');
'''},
                    {"name": "the 8 kΩ still runs from the probed node to ground", "code": r'''
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 8000) <= 80 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'The 8 kΩ from node A to ground is part of the given circuit — leave it where it is.');
c.assert(c.count('R') >= 3,
  'Two supply branches and the 8 kΩ means at least three resistors; found ' + c.count('R') + '.');
'''},
                    {"name": "node A sits at 8.00 V", "code": r'''
c.close(c.vout(), 8.0, 0.01,
  'the probed node — check the resistor you chose for the 5 V branch');
'''},
                    {"name": "the 12 V supply delivers 4 mA", "code": r'''
const dc = c.dc();
const big = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 12) < 0.05; });
c.assert(big.length === 1, 'Exactly one 12 V supply, please.');
c.close(Math.abs(dc.currents[big[0].id]), 0.004, 0.02,
  'the current out of the 12 V supply — it is (12 - 8) V across the 1 kΩ');
'''},
                    {"name": "the 5 V supply absorbs 3 mA", "code": r'''
const dc = c.dc();
const small = c.net.parts.filter(function (p) { return p.kind === 'V' && Math.abs(p.value - 5) < 0.05; });
c.assert(small.length === 1, 'Exactly one 5 V supply, please.');
const i5 = dc.currents[small[0].id];
c.assert(i5 > 0,
  'Current should be flowing INTO the 5 V supply, because node A is above 5 V. ' +
  'A negative figure here means the supply is wired the other way round: its + terminal ' +
  'belongs on the resistor, not on ground.');
c.close(i5, 0.003, 0.02, 'the current into the 5 V supply');
'''},
                ],
                "hints": [
                    "Call the node voltage $v$ and write the three currents leaving it: $(v-12)/1000$ towards the 12 V supply, $(v-5)/R$ towards the 5 V supply, and $v/8000$ down to ground. KCL says they add to zero.",
                    "You are told $v = 8$, so substitute it: $-0.004 + 3/R + 0.001 = 0$.",
                    "That gives $3/R = 0.003$, so $R = 1$ kΩ.",
                    "Draw the 5 V supply the same way up as the 12 V one — the + terminal is the top pin of a vertical source — and give it its own ground symbol. Two ground symbols are one node, so no long wire is needed.",
                ],
            },
            "derive": {
                "title": "The node equation, written once and for all",
                "minutes": 13,
                "vars": ["v", "E_1", "E_2", "R_1", "R_2", "R_3"],
                "brief": r'''
One unknown node, at voltage $v$. Two supplies reach it: $E_1$ through $R_1$ and $E_2$
through $R_2$. A third resistor $R_3$ runs from the node down to ground. That is the
circuit you have just drawn, with letters instead of numbers.

Take every current as positive when it *leaves* the node. Then KCL is simply that the
three of them add to zero.
''',
                "steps": [
                    {
                        "prompt": "Write the current leaving the node through $R_1$, in terms of $v$, $E_1$ and $R_1$.",
                        "answer": "\\frac{v-E_1}{R_1}",
                        "hint": "Ohm's law across $R_1$. The far end of it is held at $E_1$ by the supply, and you want the current flowing away from the node.",
                    },
                    {
                        "prompt": "Now the current leaving the node through $R_3$, in terms of $v$ and $R_3$.",
                        "answer": "\\frac{v}{R_3}",
                        "hint": "The far end of $R_3$ is ground, which is 0 V — so the difference across it is the node voltage itself.",
                    },
                    {
                        "prompt": "Add the three currents, set the sum to zero, and gather the terms containing $v$. What is the coefficient multiplying $v$?",
                        "answer": "\\frac{1}{R_1}+\\frac{1}{R_2}+\\frac{1}{R_3}",
                        "hint": "Each of the three fractions contributes one $v$ over its own resistance. Conductances, in other words, and they add.",
                        "deconstruct": [
                            "The sum is $\\frac{v-E_1}{R_1} + \\frac{v-E_2}{R_2} + \\frac{v}{R_3} = 0$.",
                            "Split each fraction into its $v$ part and its constant part; the $v$ parts are $v/R_1$, $v/R_2$ and $v/R_3$.",
                        ],
                    },
                    {
                        "prompt": "Solve for $v$ in terms of the two EMFs and the three resistances.",
                        "answer": "\\frac{E_1 R_2 R_3 + E_2 R_1 R_3}{R_1 R_2 + R_1 R_3 + R_2 R_3}",
                        "hint": "Move the constant terms to the other side, then divide by the coefficient you just found. Any algebraically equal form is accepted — the conductance version is fine if you prefer it.",
                        "deconstruct": [
                            "The equation is $v\\left(\\frac{1}{R_1}+\\frac{1}{R_2}+\\frac{1}{R_3}\\right) = \\frac{E_1}{R_1}+\\frac{E_2}{R_2}$.",
                            "Divide, then multiply top and bottom by $R_1R_2R_3$ to clear the little fractions away.",
                        ],
                    },
                    {
                        "prompt": "Put the numbers in: $E_1 = 12$ V through $R_1 = 1$ kΩ, $E_2 = 5$ V through $R_2 = 1$ kΩ, and $R_3 = 8$ kΩ to ground. What is $v$, in volts?",
                        "answer": "8",
                        "hint": "Work in volts and kilohms throughout; the kilohms cancel top and bottom, so you never have to write a single zero.",
                        "deconstruct": [
                            "Top: $12 \\times 1 \\times 8 + 5 \\times 1 \\times 8 = 96 + 40 = 136$.",
                            "Bottom: $1 \\times 1 + 1 \\times 8 + 1 \\times 8 = 17$, and $136/17 = 8$.",
                        ],
                    },
                ],
                "closing": r'''
Look at what that result is. Writing $g = 1/R$ for each conductance, it says

$$v = \frac{g_1E_1 + g_2E_2 + g_3\cdot 0}{g_1+g_2+g_3}$$

— a weighted average of the voltages at the far ends of the three branches, weighted
by conductance, with ground counting as a source of 0 V like any other. That is why the
answer must always land between the highest and lowest voltage attached to the node,
and it is a check worth running on every nodal result you ever produce.
''',
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Mesh analysis: one equation per loop",
            "summary": "The same job approached from the other side: currents that circulate round loops, and KVL to pin them down.",
            "concepts": [
                "A mesh is a loop with nothing inside it — a window in the drawing. Give each mesh a current that circulates all the way round it, and choose the same direction for every one.",
                "A circulating current satisfies KCL automatically. Whatever it carries into a node it carries out again, so there is no charge accumulating anywhere and no KCL equation left to write.",
                "The equations come from KVL instead: round each mesh, the $IR$ drops add up to the source rises.",
                "A component on the boundary between two meshes carries the *difference* of the two mesh currents, because the two loops traverse it in opposite directions. A component on the outside edge carries just one mesh current.",
                "Mesh and nodal always agree; choose whichever gives fewer equations. Count the windows and count the unknown nodes, and pick the smaller number.",
                "A mesh current is bookkeeping, not something an ammeter can be put in series with. Real branch currents are recovered at the end by combining the mesh currents that pass through each branch.",
                "The number of windows in a planar drawing is $b - n + 1$: branches minus nodes plus one. That is exactly the number of independent KVL equations there are to write, which is why the count never has to be guessed.",
                "With every mesh current drawn the same way round and every source an independent voltage source, the system can be written down by inspection: the diagonal is the sum of the resistances round a mesh, the off-diagonal is minus the resistance the two meshes share, and the right-hand side is the net source rise round the loop.",
                "A current source in a branch has no $IR$ drop to write, because its voltage is whatever the rest of the circuit makes it. On an outside edge it *fixes* a mesh current and removes an unknown; on a shared branch the two meshes are merged into one **supermesh** and the source's own current supplies the missing equation.",
                "Mesh analysis needs a drawing with no crossings, because without one there are no windows. Nodal never has that problem, which is one of several reasons every circuit simulator ever written is nodal underneath.",
            ],
            "read": [
                {
                    "title": "Currents that go round in circles",
                    "minutes": 18,
                    "body": r'''
Module 7 named the points. Every junction got a voltage, KCL at each one became an
equation, and the branch currents fell out at the end — one division per resistor. It works
on anything. It is also, for some shapes of circuit, far more work than the circuit
deserves, and seeing why is the whole motivation for what follows.

Take a supply and six resistors in a single ring. Nodal names a voltage at every joint
between two resistors — five unknowns, five simultaneous equations. But you knew something
before you started that the method had no way to hear: there is one loop, so there is one
current, and it is the same in every component in the ring. Nodal threw that away by
describing the circuit point by point when the natural description was loop by loop.

Mesh analysis is the other half of the pair: it names the currents and lets the voltages
come out at the end. Neither is more correct — they are two coordinate systems on the same
circuit — and in practice the only question is which produces fewer equations.

## What a mesh current actually is

Draw the circuit flat on the page with no wires crossing. The drawing cuts the paper into
regions, the way a window frame cuts a sheet of glass: some number of enclosed panes, plus
the unbounded outside. A **mesh** is one of those panes — a loop with nothing inside it.
The outer boundary of the drawing is a loop too, but not a mesh: the rest of the circuit
is inside it.

Now the move that defines the method. Give each pane a current that runs all the way round
its border, like water circulating in a closed channel, and pick a direction — clockwise,
always, for reasons that will be obvious shortly. Call them $i_1, i_2, \dots$

That current is not a measurement of anything: you cannot break a wire, insert an ammeter
and read one off. A mesh current is a bookkeeping variable, and what an ammeter in a branch
actually reads is the sum of the mesh currents whose loops run along that branch, signed by
the direction each of them runs in.

That sounds like a step backwards — measurable branch currents replaced by unmeasurable
circulating ones. It buys two things, and they are large.

## The first thing it buys: KCL, for nothing

Stand at any node and watch one mesh current go past. Its loop arrives along one branch
and leaves along another — it has to, because the loop is closed and the node is a point on
it — so it brings in exactly as much as it takes away. Every mesh current, at every node,
does the same, for any values at all of $i_1, i_2, \dots$

Kirchhoff's current law is therefore not a constraint on the mesh currents but a property
of them: there is no KCL equation left to write anywhere in the circuit. That is exactly
dual to what nodal did, where naming a voltage at each point made KVL automatic, because
differences of node voltages round a closed loop always sum to zero.

## The second thing it buys: the right number of unknowns

How many mesh currents does a circuit have? Count the windows in the drawing. For a
connected planar drawing with $b$ branches and $n$ nodes, Euler's formula gives

$$\text{windows} = b - n + 1$$

and that number is not a coincidence. There are $b$ branch currents, and KCL supplies
$n - 1$ independent equations relating them — one per node, less one, since the last node's
equation is the sum of all the others. So the branch currents that satisfy KCL have
$b - n + 1$ degrees of freedom, and the mesh currents are a set of coordinates for exactly
that family: nothing lost, nothing redundant.

For the two-rung ladder below: five branches, four nodes, so $5 - 4 + 1 = 2$ windows.
Nodal on the same circuit has three nodes besides ground, one held by the supply, leaving
two unknowns as well — on this shape it is a tie.

## The shared branch, and why every loop goes clockwise

Two panes side by side share a border, and both of their mesh currents run along it — in
*opposite* directions, if both were drawn clockwise. The left pane's circulation goes down
the shared branch; the right pane's goes up it. So the branch carries

$$i_{\text{shared}} = i_1 - i_2$$

in the direction of the left loop; if that comes out negative it is really running the
other way, which requires no action.

That is the reason for the clockwise rule. Had you drawn one loop clockwise and its
neighbour anticlockwise, the shared branch would carry the *sum* instead, and every circuit
would need a fresh decision about which branches add and which subtract. Draw them all the
same way round and the answer is always subtraction.

A branch on the outside edge of the drawing belongs to one pane only, so it carries that
one mesh current and nothing else.

## Writing the equation

KVL round a closed loop: start anywhere, walk all the way round adding up every change in
potential, and arrive back at the potential you left. For each mesh, walking clockwise:

- a resistor on the outside edge, traversed in the direction of $i_k$, contributes a drop
  of $R\,i_k$;
- a resistor shared with mesh $j$ contributes a drop of $R\,(i_k - i_j)$, because that is
  the current in it in the direction you are walking;
- a voltage source traversed from its $-$ terminal to its $+$ terminal is a rise of $E$,
  and traversed the other way is a drop of $E$.

Gathered up, mesh $k$ gives

$$\Big(\textstyle\sum R \text{ round mesh } k\Big) i_k \;-\; \sum_{j \neq k} R_{kj}\, i_j
\;=\; \text{net source rise round mesh } k$$

where $R_{kj}$ is the resistance meshes $k$ and $j$ have in common. One equation per
window, and every coefficient can be read straight off the drawing.

## Worked: a two-rung ladder

A 12 V supply. Along the top, $R_1 = 2$ kΩ to node A. From A, $R_2 = 6$ kΩ down to ground —
that is the rung the two windows share. Also from A, $R_3 = 1$ kΩ across to node B, and
$R_4 = 2$ kΩ from B down to ground.

Two windows: the left one contains the supply, $R_1$ and $R_2$; the right one contains
$R_2$, $R_3$ and $R_4$. Both currents clockwise. Work in volts, milliamps and kilohms,
which are consistent with one another — one volt across one kilohm is one milliamp — so no
factor of a thousand can go missing anywhere.

```text
left window, walking clockwise from the bottom of the supply:

    up through the 12 V source        rise  12
    right along the top, through R1   drop   2 * i1
    down through the shared R2        drop   6 * (i1 - i2)
    back along the ground rail        nothing

    -12  +  2*i1  +  6*(i1 - i2)  =  0
                     8*i1  -  6*i2  =  12            (1)

right window, clockwise from the bottom of the shared rung:

    up through the shared R2          drop   6 * (i2 - i1)
    right along the top, through R3   drop   1 * i2
    down through R4                   drop   2 * i2

     6*(i2 - i1)  +  1*i2  +  2*i2  =  0
                    -6*i1  +  9*i2  =  0             (2)
```

Equation (2) says $9i_2 = 6i_1$, so $i_2 = \tfrac{2}{3}i_1$. Put that into (1):

```text
    8*i1  -  6*(2/3)*i1   =  12
    8*i1  -  4*i1         =  12
            4*i1          =  12        so   i1 = 3.00 mA
                                            i2 = 2.00 mA
```

Now translate back into things an ammeter could read:

```text
    R1  is on the outside edge of window 1       carries  i1        = 3.00 mA
    R2  is shared                                carries  i1 - i2   = 1.00 mA  downwards
    R3  is on the outside edge of window 2       carries  i2        = 2.00 mA
    R4  likewise                                 carries  i2        = 2.00 mA

    KCL at A:  3.00 in  =  1.00 down  +  2.00 across            closes
```

And the node voltages, which the method never asked for and hands over anyway:

```text
    drop across R1   =  3.00 * 2   =  6.00 V     so  A  =  12 - 6  =  6.00 V
    across R2        =  1.00 * 6   =  6.00 V     agrees with A
    drop across R3   =  2.00 * 1   =  2.00 V     so  B  =  6 - 2   =  4.00 V
    across R4        =  2.00 * 2   =  4.00 V     agrees with B
```

Every module of this course ends with the energy accounted for, so:

```text
    P(R1)  =  3^2 * 2  =  18 mW        P from the supply  =  12 * 3  =  36 mW
    P(R2)  =  1^2 * 6  =   6 mW
    P(R3)  =  2^2 * 1  =   4 mW
    P(R4)  =  2^2 * 2  =   8 mW
                          ------
                          36 mW
```

Note what the tempting shortcut would have done. "The shared resistor is in window 1, so
it carries $i_1$" gives 3 mA through 6 kΩ — an 18 V drop across a resistor fed from a 12 V
supply. Nonsense, but nonsense you have to notice.

## Worked: a source in each window, and one of them on charge

Now a circuit where mesh analysis has to handle a sign properly. A 10 V supply on the left,
$R_1 = 1$ kΩ along the top to node A, $R_2 = 2$ kΩ from A down to ground as the shared
rung, $R_3 = 1$ kΩ from A across to node B, and a second supply of 5 V from B down to
ground, drawn the same way up as the first — plus terminal at the top.

Walking window 2 clockwise now means walking *down* through the 5 V source, from its $+$
terminal to its $-$ terminal, which is a drop of 5 V and not a rise.

```text
left window:

    -10  +  1*i1  +  2*(i1 - i2)   =  0
                     3*i1  -  2*i2  =  10           (1)

right window, clockwise, going down through the 5 V source at the end:

     2*(i2 - i1)  +  1*i2  +  5     =  0
                    -2*i1  +  3*i2  =  -5           (2)
```

Eliminate $i_2$: multiply (1) by 3, (2) by 2, and add.

```text
     9*i1  -  6*i2  =   30
    -4*i1  +  6*i2  =  -10
    --------------------------
     5*i1           =   20        so   i1  =  4.00 mA

    back into (1):   2*i2  =  3*4 - 10  =  2
                       i2  =  1.00 mA
```

So $R_1$ carries 4.00 mA, the shared $R_2$ carries $i_1 - i_2 = 3.00$ mA downwards, and
$R_3$ carries 1.00 mA from A towards B. Node A sits at $10 - 4 \times 1 = 6.00$ V, which
checks against the shared rung: $3.00 \times 2 = 6.00$ V.

Look at that last branch. Node A is at 6 V and node B is held at 5 V, so current runs from
the circuit *into* the 5 V source: it is absorbing 1 mA, the way a battery does on charge.
Nothing in the setup had to know that in advance. The energy still
balances, with the absorbing source counted as a load:

```text
    P(R1)  =  4^2 * 1  =  16 mW        P from the 10 V  =  10 * 4  =  40 mW
    P(R2)  =  3^2 * 2  =  18 mW        into the  5 V    =   5 * 1  =   5 mW
    P(R3)  =  1^2 * 1  =   1 mW                                       ------
                          ------       net delivered    =  40 - 5  =  35 mW
                          35 mW
```

## The mistakes that actually happen

**Adding the mesh currents on the shared branch.** By a wide margin the most common, and
tempting because "two currents flow through it, so add them" is an honest reading of the
picture. It is the right instinct applied to the wrong picture: the two loops run through
that branch in opposite directions, so what the branch sees is what is left over. Both
clockwise means always subtract.

**Getting a source's sign wrong.** Walking clockwise takes you through some sources from
$-$ to $+$ and others from $+$ to $-$, and which it is depends only on how the source is
drawn, not on which way you think current flows. Say it as you walk: "entering at the minus,
so a rise". The second worked example went *down* through its right-hand source and picked
up a drop, which is why that equation has $-5$ on the right.

**Reporting a mesh current as a branch current.** $i_1 = 3.00$ mA is not the answer to
"what current flows in the shared resistor" — it is the answer to "what does the supply
deliver", because the supply sits on an outside edge. Always take the last step back to
branch currents.

**Stripping a minus sign.** If a mesh current comes out negative, the loop circulates the
other way and every formula downstream already accounts for it. Take the magnitude and the
shared branch immediately gets a difference of two numbers whose relative sign has been
destroyed, which produces a plausible wrong answer rather than an obvious one.

**Using a mesh current in $I^2R$.** Power depends on the current actually in the component.
For a shared resistor that is $(i_1 - i_2)^2 R$, and squaring hides the error: in the ladder
above, $i_1^2 R_2$ gives 54 mW against a true 6 mW, and the supply is only delivering 36 mW
in total. Checking the power balance catches this one every time.

## Where this stops

**Current sources.** Every term above was an $IR$ drop or a source of known voltage. A
current source is neither: its voltage is whatever the rest of the circuit makes it, so
there is no expression in $i_1$ and $i_2$ for the drop across it. Not fatal — it is the next
reading's subject, and it usually makes the problem *smaller* — but the method as written
cannot start.

**Drawings with crossings.** Windows only exist in a planar drawing. Five nodes with a
resistor between every pair cannot be drawn flat without one, so that circuit has no meshes
to number. Nodal does not care.

**Dependent sources.** Every source here is independent: a fixed number on the right-hand
side. A transistor model contains sources proportional to a current or voltage elsewhere,
which puts unknowns on both sides and destroys the symmetry of the coefficients. The method
survives; the by-inspection shortcut does not.

**Anything nonlinear.** $R\,(i_k - i_j)$ is a straight line, which is what makes the system
solvable in one pass. A diode is not, and a circuit containing one has to be solved by
guessing, linearising about the guess, and repeating.

**Steady DC.** Capacitors and inductors turn the $IR$ drops into integrals and derivatives
and the equations into differential ones. At a single sinusoidal frequency this costs
almost nothing — write $1/(j\omega C)$ and $j\omega L$ as impedances and every equation
above holds with complex numbers in place of real ones.
''',
                },
                {
                    "title": "The branch with no drop to write, and choosing a side",
                    "minutes": 17,
                    "body": r'''
The last reading left one gap and named it: a current source has no $IR$ drop, so there is
nothing to put in the KVL sum where it sits. This reading closes that gap, then turns to
the question the module has been circling — given a circuit, mesh or nodal? — and answers
it with a count rather than a feeling.

## Why a current source is awkward, and why it is also a gift

An ideal voltage source fixes the voltage across itself and lets the circuit decide the
current. An ideal current source fixes the current through itself and lets the circuit
decide the voltage. That is the whole of it, and it is why the two methods find opposite
things easy.

Nodal analysis wants currents to add up at a node, so a current source is the easiest
component there is: its current is already a number, and it goes straight into the KCL sum
with no substitution at all. A voltage source is nodal's awkward case, because its current
is unknown.

Mesh analysis is the mirror image. It wants voltages to add up round a loop, so a voltage
source is trivial and a current source is the awkward one — you cannot write its drop,
because nothing tells you what it is until the circuit is solved. Duality is not a slogan
here; it is the reason each method has exactly one bad case, and they are different cases.

The compensation is that a current source also *tells* you something. It fixes a current,
and currents are precisely what mesh analysis is solving for. So every current source
removes an unknown. Handled properly it makes the system smaller, not larger.

## Case one: the source is on an outside edge

If a current source sits in a branch that belongs to one window only, that window's mesh
current *is* the source current — no equation needed, no algebra, done. A 4 mA source on
the outer edge of window 2, running the same way as the clockwise circulation, means
$i_2 = 4$ mA before you write anything down. Write the KVL equations for the other windows
with $i_2$ substituted in as a known number.

A two-window circuit with a source like that has one unknown left, and it takes one line.

## Case two: the source is on a shared branch — the supermesh

Now the source is on the border between two windows, so neither mesh current is fixed on
its own. What is fixed is their difference: the branch carries $i_1 - i_2$, and the source
says what that has to be.

That is one equation. The second comes from a loop that avoids the source altogether. Take
the two windows either side of it and treat them as a single larger loop — go round the
outside of the pair, ignoring the shared branch entirely. That loop is a **supermesh**, and
KVL round it is perfectly writable, because every component on it is a resistor or a
voltage source.

Two windows, two unknowns; one supermesh equation and one constraint. The books cancel.

### Worked: a supermesh with numbers

A 12 V supply. $R_1 = 1$ kΩ along the top to node A. From A, a current source that pulls a
steady 3 mA down to ground — a load that draws 3 mA whatever voltage it finds itself at,
which is what a current-driven LED string or a transistor current sink actually behaves
like. Also from A, $R_2 = 1$ kΩ across to node B, and $R_3 = 1$ kΩ from B down to ground.

Two windows again. $i_1$ clockwise round the left, $i_2$ clockwise round the right, and the
current source is on the rung they share.

```text
the constraint the source gives, straight away:

    the shared rung carries  i1 - i2  downwards, and the source says that is 3 mA

                             i1  -  i2   =  3                    (1)

the supermesh: round the OUTSIDE of both windows, avoiding the shared rung

    up through the 12 V source        rise  12
    right along the top, through R1   drop   1 * i1
    on across the top, through R2     drop   1 * i2
    down through R3                   drop   1 * i2
    back along the ground rail

    -12  +  1*i1  +  1*i2  +  1*i2  =  0
                     i1  +  2*i2    =  12                        (2)
```

Notice that the walk changes which mesh current it is following halfway along the top: on
$R_1$, which is on window 1's outer edge, the current is $i_1$; once past the junction at A
the path is on window 2's outer edge and the current is $i_2$. That is the only subtlety in
the whole construction.

```text
substitute (1) into (2):   (i2 + 3)  +  2*i2   =  12
                                        3*i2   =   9
                                          i2   =   3.00 mA
                                          i1   =   6.00 mA
```

Now everything else follows:

```text
    R1 carries i1                 =  6.00 mA     drop  6.00 V    so A = 12 - 6 = 6.00 V
    the source carries i1 - i2    =  3.00 mA     as it must
    R2 and R3 carry i2            =  3.00 mA     drop  3.00 V each, so B = 3.00 V

    KCL at A:   6.00 in  =  3.00 into the source  +  3.00 across to B      closes
```

The one thing mesh analysis did not hand over directly is the voltage across the current
source, because that was never an unknown. It falls out at the end: the source runs from
node A to ground, so it has 6.00 V across it, and with 3 mA flowing into its upper terminal
it is *absorbing* $6 \times 3 = 18$ mW. A current source made to sit at a positive voltage
with current flowing into its high side is a load, and there is nothing strange about that
— a battery being charged at constant current is exactly this component.

The energy closes:

```text
    P(R1)  =  6^2 * 1   =  36 mW       P from the supply  =  12 * 6  =  72 mW
    P(R2)  =  3^2 * 1   =   9 mW
    P(R3)  =  3^2 * 1   =   9 mW
    into the source     =  18 mW
                           ------
                           72 mW
```

## Writing the system down without walking any loops

Once every mesh current is clockwise and every source is an independent voltage source, the
equations stop needing to be derived and can be read off the drawing:

- the coefficient of $i_k$ in equation $k$ is the sum of every resistance round mesh $k$;
- the coefficient of $i_j$ in equation $k$ is **minus** the resistance meshes $k$ and $j$
  share, and zero if they share none;
- the right-hand side of equation $k$ is the net source rise going clockwise round mesh $k$.

The matrix is symmetric, because "the resistance meshes 1 and 2 share" does not depend on
which of the two you look from. That symmetry is a free check on your arithmetic: if the
coefficient of $i_2$ in equation 1 differs from the coefficient of $i_1$ in equation 2, one
of them is wrong.

### Worked: a bridge, three windows at once

A bridge is the circuit that finally forces a systematic method. A 12 V supply across the
top and bottom rails. $R_1 = 2$ kΩ from the top rail down to node L and $R_3 = 8$ kΩ from L
to ground on the left; $R_2 = 3$ kΩ from the top rail down to node R and $R_4 = 2$ kΩ from
R to ground on the right; and $R_5 = 2$ kΩ bridging L to R across the middle.

Look for two resistors in series: none, because the bridge resistor takes a share of the
current at both L and R. Look for two in parallel: none, because no two have the same
voltage across them. Six branches, four nodes, so $6 - 4 + 1 = 3$ windows:

- window 1, the supply, $R_1$ and $R_3$;
- window 2, above the bridge: $R_1$, $R_2$ and $R_5$;
- window 3, below it: $R_3$, $R_5$ and $R_4$.

Written by inspection, in kilohms:

```text
    diagonal   mesh 1:  R1 + R3       =  2 + 8      =  10
               mesh 2:  R1 + R2 + R5  =  2 + 3 + 2  =   7
               mesh 3:  R3 + R5 + R4  =  8 + 2 + 2  =  12

    shared     1 and 2 share R1       =  2   ->  -2
               1 and 3 share R3       =  8   ->  -8
               2 and 3 share R5       =  2   ->  -2

    rises      only mesh 1 sees the supply, and clockwise it is a rise of 12

     10*i1  -   2*i2  -   8*i3  =  12
     -2*i1  +   7*i2  -   2*i3  =   0
     -8*i1  -   2*i2  +  12*i3  =   0
```

Symmetric across the diagonal, as promised. Solve it: from the second row
$7i_2 = 2i_1 + 2i_3$, and substituting that into the third,

```text
    12*i3  =  8*i1  +  2*i2  =  8*i1  +  (4*i1 + 4*i3)/7

    84*i3  =  56*i1  +  4*i1  +  4*i3
    80*i3  =  60*i1                        so  i3 = 0.75 * i1
                                               i2 = (2 + 1.5)/7 * i1 = 0.5 * i1

    first row:   10*i1  -  2*(0.5*i1)  -  8*(0.75*i1)  =  12
                 10*i1  -  1*i1  -  6*i1               =  12
                                          3*i1         =  12

                 i1 = 4.00 mA     i2 = 2.00 mA     i3 = 3.00 mA
```

Back to branch currents. $R_1$ is shared between meshes 1 and 2, so it carries
$i_1 - i_2 = 2.00$ mA downwards; $R_3$ is shared between 1 and 3 and carries
$i_1 - i_3 = 1.00$ mA; $R_2$ is on window 2's edge and carries 2.00 mA; $R_4$ is on window
3's edge and carries 3.00 mA. The bridge resistor is shared between 2 and 3 and carries
$i_3 - i_2 = 1.00$ mA from L to R.

Node voltages: $L = 12 - 2.00 \times 2 = 8.00$ V and $R = 12 - 2.00 \times 3 = 6.00$ V, and
the bridge does indeed have 2.00 V across 2 kΩ. KCL at L: 2.00 mA in from the top, 1.00 mA
down through $R_3$ and 1.00 mA across the bridge. It closes.

The supply delivers $i_1 = 4.00$ mA at 12 V, so whatever is inside that box behaves, from
the supply's point of view, like a single resistance of $12/4.00 = 3.00$ kΩ — a number no
amount of series-and-parallel arithmetic on the five resistors will produce.

## So: mesh or nodal?

Count both, and take the smaller. It really is that mechanical.

- **Mesh unknowns** = the number of windows = $b - n + 1$, minus one for every current
  source that sits on an outside edge.
- **Nodal unknowns** = the number of nodes other than ground, minus one for every voltage
  source with a terminal on ground.

For the bridge just solved: three windows against two unknown nodes (L and R — the top rail
is held by the supply). **Nodal wins**, and by a whole equation. Solving it the other way
was worth doing once to see the matrix, but two equations beats three every time, and the
nodal version comes out to $v_L = 8$, $v_R = 6$ in about a third of the writing.

For the ring of six resistors that opened the last reading: one window against five unknown
nodes. **Mesh wins** outright, and the whole problem is one line.

The pattern behind those two: long series runs with few loops favour mesh, and banks of
parallel branches hanging off a few nodes favour nodal. Real circuits are usually much more
one than the other, so the choice is rarely close.

Two smaller considerations, once the count is a tie. First, what you actually want: if the
question asks for a current, mesh gives it directly and nodal costs you a division; if it
asks for a voltage, the reverse. Second, which awkward case is present — a floating voltage
source costs nodal a supernode, a shared current source costs mesh a supermesh, and neither
is expensive, but if the circuit has three of one and none of the other, take the hint.

## The duality, in one table

Nothing in either method is a coincidence. Every line of one has a mirror in the other.

```text
    nodal                              mesh
    -------------------------------    -------------------------------
    unknowns are node voltages         unknowns are loop currents
    KVL is automatic                   KCL is automatic
    write KCL at each node             write KVL round each loop
    conductances add on the diagonal   resistances add on the diagonal
    current sources are easy           voltage sources are easy
    a floating voltage source          a shared current source
      -> supernode                       -> supermesh
    n - 1 equations                    b - n + 1 equations
```

## Where mesh analysis stops, and why simulators went the other way

**Planarity.** Windows exist only in a drawing with no crossings. Take five nodes and put a
resistor between every pair — ten resistors, nothing exotic about any of them — and the
result provably cannot be drawn flat. There are no meshes to number. The general repair is
loop analysis — pick any spanning tree, and each remaining branch closes exactly one
independent loop — which always works, and mesh analysis is a convenient special case of
it. But you have to choose the loops yourself, and the by-inspection shortcut is gone.

**Dependent sources and nonlinearity** cost mesh exactly what they cost nodal: the symmetry
of the coefficients, and the ability to solve in one pass. Neither method is worse off.

**And the practical verdict.** Every circuit simulator in existence is nodal underneath —
modified nodal analysis, the same equations of module 7 with an extra unknown for each
voltage source. Three reasons, in order of weight. A netlist is a list of components and
the node numbers they connect to, so the nodal matrix can be assembled by adding one small
stamp per component, in any order, with no global analysis of the circuit at all; finding
the windows of a drawing requires knowing the drawing, and a netlist has no drawing.
Planarity would have to be checked and would often fail. And nodal extends to capacitors,
inductors, transistors and diodes by changing what each stamp contains, and nothing else.

None of which makes mesh analysis a museum piece. On a circuit you are reading off a page
with two or three windows in it, it is very often the faster way to an answer by hand — and
the habit of counting both before starting is worth more than either method on its own.
''',
                },
            ],
            "numeric": [
                {
                    "title": "One window, and nothing to subtract",
                    "minutes": 5,
                    "brief": r'''
The mechanical one, to get the walk under your feet before there is any bookkeeping to do.
One window in the drawing, so one mesh current, so one equation — and because there is only
one loop, that mesh current is also the branch current in every component, with no
translation step at the end.

The only thing to be careful about is that there are two supplies in the loop and they are
drawn the same way up, plus terminal at the top. Walking clockwise takes you *up* through
one of them and *down* through the other.
''',
                    "prompt": "What current circulates round the loop?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 20},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 7, "y": 3, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 3, "value": 2000},
                            {"id": "r3", "kind": "R", "x": 15, "y": 3, "value": 2000},
                            {"id": "v2", "kind": "V", "x": 19, "y": 7, "rot": 1, "value": 5},
                            {"id": "g1", "kind": "GND", "x": 19, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [6, 3]},
                            {"a": [8, 3], "b": [10, 3]},
                            {"a": [12, 3], "b": [14, 3]},
                            {"a": [16, 3], "b": [19, 3]},
                            {"a": [19, 3], "b": [19, 6]},
                            {"a": [19, 8], "b": [19, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Left supply", "value": "20.0 V"},
                        {"label": "R1", "value": "1.00 kΩ"},
                        {"label": "R2", "value": "2.00 kΩ"},
                        {"label": "R3", "value": "2.00 kΩ"},
                        {"label": "Right supply", "value": "5.00 V"},
                    ],
                    "aside": "Work in volts, milliamps and kilohms. One volt across one kilohm is one "
                             "milliamp, so the three are consistent and no factor of a thousand can go "
                             "missing.",
                    "answer": 3.0,
                    "tol": 0.02,
                    "unit": "mA",
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.id === 'v1'; })[0];
return Math.abs(d.currents[src.id]) * 1000;
''',
                    "hint": "Walk clockwise from the bottom of the left supply. Up through it is a rise "
                            "of 20; the three resistors are drops of $1i$, $2i$ and $2i$; and coming "
                            "down through the right-hand supply, from its plus terminal to its minus "
                            "terminal, is a drop of 5.",
                    "wrong": "If you got 5.00, the two supplies were added — but they are drawn the "
                             "same way up, so the second one pushes back against the first and their "
                             "difference is what drives the loop. If you got 4.00, the 5 V supply was "
                             "ignored altogether. If you got 15.0, the net 15 V has not been divided "
                             "by anything yet.",
                    "why": r'''
```text
KVL clockwise round the single window:

    -20  +  1*i  +  2*i  +  2*i  +  5   =  0
                            5*i         =  15
                              i         =  3.00 mA
```

Or the same thing said physically: the two supplies face each other, so the net push round
the loop is $20 - 5 = 15$ V, and the loop's resistance is $1 + 2 + 2 = 5$ kΩ.

Check it against the node voltages the drawing implies. Starting at 20 V and losing
$3.00 \times 1 = 3$ V, then $3.00 \times 2 = 6$ V, then another 6 V, leaves
$20 - 3 - 6 - 6 = 5$ V — exactly the voltage the right-hand supply holds its terminal at,
as it must. The current runs *into* the plus terminal of the 5 V supply, so that supply is
absorbing $5 \times 3.00 = 15$ mW while the 20 V one delivers $20 \times 3.00 = 60$ mW and
the resistors turn the remaining 45 mW into heat.
''',
                },
                {
                    "title": "The rung the two windows share",
                    "minutes": 7,
                    "brief": r'''
Two windows now, so two mesh currents, and one component sitting on the boundary between
them. That component is the only thing in the circuit whose current is neither $i_1$ nor
$i_2$, and it is what the question asks about — because getting it right is the whole
difference between mesh analysis working and mesh analysis producing plausible nonsense.

Both loops clockwise, as always. Nothing here is a current source and nothing floats, so
the two KVL equations can be written straight down.
''',
                    "prompt": "What current flows in the 6.00 kΩ resistor the two windows share?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 7, "y": 3, "value": 2000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                            {"id": "r3", "kind": "R", "x": 15, "y": 3, "value": 1000},
                            {"id": "r4", "kind": "R", "x": 19, "y": 6, "rot": 1, "value": 2000},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [6, 3]},
                            {"a": [8, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 10]},
                            {"a": [11, 3], "b": [14, 3]},
                            {"a": [16, 3], "b": [19, 3]},
                            {"a": [19, 3], "b": [19, 5]},
                            {"a": [19, 7], "b": [19, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "24.0 V"},
                        {"label": "R1, along the top into node A", "value": "2.00 kΩ"},
                        {"label": "R2, the shared rung, A to ground", "value": "6.00 kΩ"},
                        {"label": "R3, along the top from A to B", "value": "1.00 kΩ"},
                        {"label": "R4, from B to ground", "value": "2.00 kΩ"},
                    ],
                    "aside": "R1 is on the outside edge of the left window and R3 and R4 are on the "
                             "outside edge of the right one, so those three carry a single mesh "
                             "current each. Only R2 is on the boundary.",
                    "answer": 2.0,
                    "tol": 0.02,
                    "unit": "mA",
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r2'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1000;
''',
                    "hint": "Left window: $-24 + 2i_1 + 6(i_1 - i_2) = 0$. Right window: "
                            "$6(i_2 - i_1) + 1i_2 + 2i_2 = 0$, which rearranges to $9i_2 = 6i_1$ and "
                            "gives $i_2$ in terms of $i_1$ with no work at all.",
                    "wrong": "If you got 10.0, the two mesh currents were added instead of "
                             "subtracted — but both loops are clockwise, so on the branch they share "
                             "they run through it in opposite directions. If you got 6.00, that is "
                             "$i_1$ on its own, which is the supply current and not this resistor's. "
                             "If you got 3.00, the right-hand rung has been left out of the circuit "
                             "altogether: $24/(2 + 6)$ is what R2 would carry if R3 and R4 were not "
                             "on the board.",
                    "why": r'''
```text
left window                 -24  +  2*i1  +  6*(i1 - i2)  =  0
                                     8*i1  -  6*i2        =  24        (1)

right window          6*(i2 - i1)  +  1*i2  +  2*i2       =  0
                                    -6*i1  +  9*i2        =   0        (2)

(2) gives  9*i2 = 6*i1, so i2 = (2/3)*i1.  Into (1):

                        8*i1  -  4*i1  =  24
                                4*i1   =  24      i1 = 6.00 mA
                                                  i2 = 4.00 mA

the shared rung carries the difference:   i1 - i2  =  2.00 mA  downwards
```

Every number in the circuit follows from that pair. R1 drops $6.00 \times 2 = 12$ V, so
node A sits at $24 - 12 = 12$ V — and 12 V across the shared 6 kΩ is indeed 2.00 mA, which
is the check worth doing every time. R3 and R4 carry $i_2 = 4.00$ mA, dropping 4 V and 8 V,
so node B is at 8 V. KCL at A: 6.00 mA in, 2.00 down the rung and 4.00 across to B.

The heat: $6^2 \times 2 + 2^2 \times 6 + 4^2 \times 1 + 4^2 \times 2 = 72 + 24 + 16 + 32 =
144$ mW, against $24 \times 6.00 = 144$ mW from the supply.
''',
                },
                {
                    "title": "The supply that is being charged",
                    "minutes": 8,
                    "brief": r'''
A source in each window now, both drawn the same way up with the plus terminal at the top.
Walking clockwise round the right-hand window therefore takes you *down* through the second
supply, from plus to minus, which is a drop and not a rise — and getting that one sign
right is most of the exercise.

The question is not about a current or a voltage but about what the second supply is doing,
which needs the branch current through it and its own terminal voltage, not the voltage at
the node feeding it.
''',
                    "prompt": "How much power does the 6.00 V supply absorb?",
                    "note": "Give the answer in milliwatts, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 15},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 7, "y": 3, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 3000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                            {"id": "r3", "kind": "R", "x": 15, "y": 3, "value": 1000},
                            {"id": "v2", "kind": "V", "x": 19, "y": 7, "rot": 1, "value": 6},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [6, 3]},
                            {"a": [8, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 10]},
                            {"a": [11, 3], "b": [14, 3]},
                            {"a": [16, 3], "b": [19, 3]},
                            {"a": [19, 3], "b": [19, 6]},
                            {"a": [19, 8], "b": [19, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Left supply", "value": "15.0 V"},
                        {"label": "R1, along the top into node A", "value": "1.00 kΩ"},
                        {"label": "R2, the shared rung, A to ground", "value": "3.00 kΩ"},
                        {"label": "R3, along the top from A to B", "value": "1.00 kΩ"},
                        {"label": "Right supply, from B to ground", "value": "6.00 V"},
                    ],
                    "aside": "R3 is on the outside edge of the right-hand window, so it carries $i_2$ "
                             "and so does the supply beyond it. Power for a source is its own "
                             "terminal voltage times the current in it — not the voltage at the far "
                             "end of the resistor feeding it.",
                    "answer": 18.0,
                    "tol": 0.2,
                    "unit": "mW",
                    # The solver's current unknown for a voltage source is positive when current
                    # enters its + terminal, so this returns a positive number only if the supply
                    # really is absorbing. A diagram redrawn so it delivered would fail the sign,
                    # not just the magnitude.
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.id === 'v2'; })[0];
return d.currents[src.id] * src.value * 1000;
''',
                    "hint": "Left window: $-15 + 1i_1 + 3(i_1 - i_2) = 0$. Right window, going down "
                            "through the 6 V supply at the end: $3(i_2 - i_1) + 1i_2 + 6 = 0$. Solve "
                            "the pair, and $i_2$ is the current in the second supply.",
                    "wrong": "If you got 36.0, $i_1$ has been used instead of $i_2$ — that is the "
                             "current the first supply delivers, and only part of it reaches the "
                             "second. If you got 27.0, the 9 V at node A has been multiplied by the "
                             "branch current, but R3 drops 3 V of that on the way and the supply only "
                             "ever sees 6 V. If you got 90.0, that is what the 15 V supply is "
                             "delivering, not what the 6 V one is taking.",
                    "why": r'''
```text
left window                 -15  +  1*i1  +  3*(i1 - i2)  =  0
                                     4*i1  -  3*i2        =  15        (1)

right window, DOWN through the 6 V supply, so +6 not -6:

                    3*(i2 - i1)  +  1*i2  +  6            =  0
                                    -3*i1  +  4*i2        =  -6        (2)

4*(1) + 3*(2):     16*i1 - 12*i2  =  60
                   -9*i1 + 12*i2  = -18
                   ---------------------
                    7*i1          =  42     i1 = 6.00 mA
                    from (1):  3*i2 = 4*6 - 15 = 9,  so  i2 = 3.00 mA
```

$i_2 = 3.00$ mA is the current in R3 and therefore in the 6 V supply, and it runs from node
A towards B, which means it enters the supply at its plus terminal. That is a source being
charged, so it absorbs

$$P = 6.00\ \text{V} \times 3.00\ \text{mA} = 18.0\ \text{mW}$$

Sanity: node A sits at $15 - 6.00 \times 1 = 9.00$ V, so the shared 3 kΩ carries
$9/3 = 3.00$ mA — which is $i_1 - i_2 = 6.00 - 3.00$, as it has to be. R3 drops
$3.00 \times 1 = 3.00$ V, putting node B at 6.00 V, which is what the second supply holds
it at. The books close: the 15 V supply delivers 90.0 mW, the resistors take
$36 + 27 + 9 = 72.0$ mW, and the 6 V supply takes the remaining 18.0 mW.
''',
                },
                {
                    "title": "A branch with no drop to write",
                    "minutes": 9,
                    "brief": r'''
The shared rung is now a current source: something that pulls a steady 2.00 mA down to
ground no matter what voltage it finds itself at. A transistor current sink and an LED
driver both behave like this, and so does a battery charger set to constant current.

Neither window can be walked on its own any more, because there is no expression for the
drop across that source — its voltage is whatever the rest of the circuit makes it, which
is precisely what the question asks for. What the source does give you is the difference
between the two mesh currents, and one loop round the outside of both windows supplies the
other equation.
''',
                    "prompt": "What voltage appears across the current source?",
                    "note": "Give the answer in volts, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 7, "y": 3, "value": 2000},
                            {"id": "i1", "kind": "I", "x": 11, "y": 6, "rot": 1, "value": 0.002},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                            {"id": "r2", "kind": "R", "x": 15, "y": 3, "value": 1000},
                            {"id": "r3", "kind": "R", "x": 19, "y": 6, "rot": 1, "value": 2000},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 1},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [6, 3]},
                            {"a": [8, 3], "b": [11, 3]},
                            {"a": [11, 1], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 10]},
                            {"a": [11, 3], "b": [14, 3]},
                            {"a": [16, 3], "b": [19, 3]},
                            {"a": [19, 3], "b": [19, 5]},
                            {"a": [19, 7], "b": [19, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "24.0 V"},
                        {"label": "R1, along the top into node A", "value": "2.00 kΩ"},
                        {"label": "Current source, the shared rung", "value": "2.00 mA, pulled down to ground"},
                        {"label": "R2, along the top from A to B", "value": "1.00 kΩ"},
                        {"label": "R3, from B to ground", "value": "2.00 kΩ"},
                    ],
                    "aside": "The supermesh walk goes up through the supply, along the top through "
                             "R1 and then R2, down through R3 and back along the ground rail — never "
                             "touching the source. It changes which mesh current it is following at "
                             "node A.",
                    "answer": 12.0,
                    "tol": 0.1,
                    "unit": "V",
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'I'; })[0];
return Math.abs(d.v[src.n1] - d.v[src.n2]);
''',
                    "hint": "The constraint is $i_1 - i_2 = 2$, because the shared rung carries the "
                            "difference and the source says what that is. The supermesh is "
                            "$-24 + 2i_1 + 1i_2 + 2i_2 = 0$. Two equations, two unknowns.",
                    "wrong": "If you got 8.00, that is node B, at the far end of R2, rather than "
                             "node A where the source sits. If you got 14.4, the source has been "
                             "treated as an open circuit and the answer is the plain divider "
                             "$24 \\times 3/5$ — but a 2 mA source is not an open circuit, and "
                             "pulling that current out of node A drags it down. If you got 4.00, "
                             "that is the drop across R2, which is the difference between the two "
                             "answers rather than either of them.",
                    "why": r'''
```text
the source fixes the difference of the two mesh currents:

    the shared rung carries i1 - i2 downwards, and the source says that is 2 mA

                              i1  -  i2   =  2                        (1)

the supermesh: clockwise round the OUTSIDE of both windows, avoiding the source

    up through the 24 V supply         rise  24
    along the top through R1           drop   2 * i1
    on along the top through R2        drop   1 * i2
    down through R3                    drop   2 * i2
    back along the ground rail

    -24  +  2*i1  +  1*i2  +  2*i2  =  0
                     2*i1  +  3*i2  =  24                             (2)

substitute (1):   2*(i2 + 2)  +  3*i2   =  24
                                 5*i2   =  20        i2 = 4.00 mA
                                                     i1 = 6.00 mA
```

The one subtlety is in that walk: which mesh current the path is following changes at node
A. Along R1 the path is on the left window's outer edge, so the current there is $i_1$;
past A it is on the right window's outer edge and the current is $i_2$. Everything else is
an ordinary KVL loop.

Now the branch currents, and the node voltages as a check on them. R1 carries
$i_1 = 6.00$ mA and drops $6.00 \times 2 = 12.0$ V, so node A sits at $24 - 12.0 = 12.0$ V.
Coming at it from the other side, R2 and R3 carry $i_2 = 4.00$ mA and drop
$4.00 \times 3 = 12.0$ V between them, putting node A at 12.0 V again. The two agree, which
is the check worth spending one line on every time — a mesh answer that is wrong is almost
never obviously wrong.

```text
    KCL at A:   6.00 mA in through R1
                2.00 mA down into the source   +   4.00 mA across to B      closes
```

So the source has **12.0 V** across it, and node B sits at $4.00 \times 2 = 8.00$ V.

Notice what the source is doing with that voltage. It sits at $+12$ V with current flowing
*into* its upper terminal, so it is absorbing $12.0 \times 2.00 = 24.0$ mW. A current source
is not obliged to deliver anything; what it does is fix a current, and the rest of the
circuit decides the rest. The supply here delivers $24 \times 6.00 = 144$ mW; the three
resistors take $36 \times 2 + 16 \times 1 + 16 \times 2 = 72 + 16 + 32 = 120$ mW, and the
source takes the other 24.0 mW.
''',
                },
                {
                    "title": "A bridge, and what the supply sees",
                    "minutes": 12,
                    "brief": r'''
The circuit that finally leaves you no choice. Look for two resistors carrying the same
current: there are none, because the bridge resistor across the middle takes a share at
both ends. Look for two with the same voltage across them: none either. Six branches, four
nodes, so $6 - 4 + 1 = 3$ windows and three mesh currents — the supply's window on the
left, the one above the bridge and the one below it.

Three simultaneous equations, and then one division. The by-inspection rule earns its keep
here: the diagonal is the sum of the resistances round each window, the off-diagonal is
minus what two windows share, and only the left-hand window sees the supply.
''',
                    "prompt": "What single resistance would draw the same current from the supply as this network does?",
                    "note": "Give the answer in kilohms, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r1", "kind": "R", "x": 8, "y": 3, "rot": 1, "value": 2000},
                            {"id": "r2", "kind": "R", "x": 16, "y": 3, "rot": 1, "value": 3000},
                            {"id": "r5", "kind": "R", "x": 12, "y": 4, "value": 2000},
                            {"id": "r3", "kind": "R", "x": 8, "y": 6, "rot": 1, "value": 8000},
                            {"id": "g1", "kind": "GND", "x": 8, "y": 9},
                            {"id": "r4", "kind": "R", "x": 16, "y": 6, "rot": 1, "value": 2000},
                            {"id": "g2", "kind": "GND", "x": 16, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 9]},
                            {"a": [3, 4], "b": [3, 2]},
                            {"a": [3, 2], "b": [8, 2]},
                            {"a": [8, 2], "b": [16, 2]},
                            {"a": [8, 4], "b": [11, 4]},
                            {"a": [13, 4], "b": [16, 4]},
                            {"a": [8, 4], "b": [8, 5]},
                            {"a": [8, 7], "b": [8, 9]},
                            {"a": [16, 4], "b": [16, 5]},
                            {"a": [16, 7], "b": [16, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, across the two rails", "value": "12.0 V"},
                        {"label": "R1, top rail down to node L", "value": "2.00 kΩ"},
                        {"label": "R3, node L down to ground", "value": "8.00 kΩ"},
                        {"label": "R2, top rail down to node R", "value": "3.00 kΩ"},
                        {"label": "R4, node R down to ground", "value": "2.00 kΩ"},
                        {"label": "R5, bridging L to R", "value": "2.00 kΩ"},
                    ],
                    "aside": "Two of the three mesh currents are worth naming before you start: "
                             "$i_1$ is the supply current, so once you have it the answer is one "
                             "division. The bridge resistor is shared between the upper and lower "
                             "windows and carries $i_3 - i_2$.",
                    "answer": 3.0,
                    "tol": 0.02,
                    "unit": "kΩ",
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const V = Math.abs(d.v[src.n1] - d.v[src.n2]);
const I = Math.abs(d.currents[src.id]);
return V / I / 1000;
''',
                    "hint": "By inspection, with everything in kilohms: "
                            "$10i_1 - 2i_2 - 8i_3 = 12$, $-2i_1 + 7i_2 - 2i_3 = 0$ and "
                            "$-8i_1 - 2i_2 + 12i_3 = 0$. The last two give $i_2$ and $i_3$ as "
                            "multiples of $i_1$, and the first then gives $i_1$ in one line.",
                    "wrong": "If you got 3.33, the bridge resistor has been ignored: 2 + 8 in one "
                             "arm and 3 + 2 in the other gives $10 \\parallel 5 = 3.33$ kΩ, and "
                             "adding a fifth path can only ever lower the resistance, so the true "
                             "answer has to be below it. If you got 2.80, the bridge has been "
                             "treated as a short instead, which is the other extreme: "
                             "$(2 \\parallel 3) + (8 \\parallel 2) = 1.20 + 1.60$. The real answer "
                             "sits between those two bounds. If you got 1.00, that is the current in "
                             "the bridge resistor in milliamps, not a resistance.",
                    "why": r'''
```text
by inspection, in kilohms, all three loops clockwise:

    mesh 1  (supply, R1, R3)     R1 + R3       =  2 + 8      =  10
    mesh 2  (R1, R2, R5)         R1 + R2 + R5  =  2 + 3 + 2  =   7
    mesh 3  (R3, R5, R4)         R3 + R5 + R4  =  8 + 2 + 2  =  12

    shared: 1&2 have R1 = 2      1&3 have R3 = 8      2&3 have R5 = 2

     10*i1  -   2*i2  -   8*i3  =  12
     -2*i1  +   7*i2  -   2*i3  =   0
     -8*i1  -   2*i2  +  12*i3  =   0
```

The matrix is symmetric about its diagonal, which is the free check that the coefficients
were read off correctly. Solve it by getting the two source-free rows in terms of $i_1$:

```text
    row 2:   7*i2  =  2*i1  +  2*i3
    row 3:  12*i3  =  8*i1  +  2*i2  =  8*i1  +  (4*i1 + 4*i3)/7

            84*i3  =  60*i1  +  4*i3
            80*i3  =  60*i1                    i3  =  0.75 * i1
                                               i2  =  (2 + 1.5)/7 * i1  =  0.5 * i1

    row 1:  10*i1  -  2*(0.5*i1)  -  8*(0.75*i1)  =  12
            10*i1  -  1*i1  -  6*i1              =  12
                                      3*i1       =  12

            i1 = 4.00 mA      i2 = 2.00 mA      i3 = 3.00 mA
```

$i_1$ is the supply current, because the supply is on the outside edge of the first window,
so the network draws 4.00 mA at 12.0 V and looks like

$$R = \frac{12.0\ \text{V}}{4.00\ \text{mA}} = 3.00\ \text{k}\Omega$$

Everything else is now available. R1 is shared between windows 1 and 2 and carries
$i_1 - i_2 = 2.00$ mA; R3 is shared between 1 and 3 and carries $i_1 - i_3 = 1.00$ mA; R2
carries $i_2 = 2.00$ mA and R4 carries $i_3 = 3.00$ mA. The bridge is shared between 2 and 3
and carries $i_3 - i_2 = 1.00$ mA, running from L towards R.

So node L sits at $12 - 2.00 \times 2 = 8.00$ V and node R at $12 - 2.00 \times 3 = 6.00$ V,
a difference of 2.00 V across the 2 kΩ bridge — 1.00 mA, as the mesh currents said. KCL at
L: 2.00 mA in from the top, 1.00 mA down through R3, 1.00 mA across the bridge.

Worth noticing what the bridge did. Unbalanced, it moved the answer from 3.33 kΩ to
3.00 kΩ. Balanced — that is, with $R_1/R_3 = R_2/R_4$ — L and R would sit at the same
voltage, the bridge would carry nothing whatever its value, and the network would collapse
back to two independent chains. That is the whole principle behind every bridge measurement
ever made: the balance point does not depend on the bridge element, so it can be found
precisely with a crude detector.
''',
                },
            ],
            "quiz": {
                "title": "Loops, and what circulates round them",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What does defining the unknowns as circulating mesh currents give you for free?",
                        "opts": [
                            "Ohm's law in every branch",
                            "Kirchhoff's current law at every node",
                            "Kirchhoff's voltage law round every loop",
                            "the power dissipated in every resistor",
                        ],
                        "a": 1,
                        "why": r'''
KCL, at every node, automatically. A current that goes all the way round a closed loop
brings into each node on that loop exactly as much as it takes away, so nothing can
accumulate anywhere and there is no current law left to enforce. That is the entire
reason the method is set up this way. KVL is what you then have to write down by hand,
one equation per mesh.
''',
                    },
                    {
                        "q": "Two neighbouring meshes share a 1 kΩ resistor. The mesh currents come out as $i_1 = 4$ mA and $i_2 = 1$ mA, both defined clockwise. What current does that resistor actually carry?",
                        "opts": ["5 mA", "4 mA", "1 mA", "3 mA"],
                        "a": 3,
                        "why": r'''
3 mA. Both loops circulate clockwise, so on the branch they share they run in opposite
directions and the resistor carries the difference, $4 - 1 = 3$ mA, in the direction of
the larger. Adding them to get 5 mA is the standard slip: it would be right only if the
two loops had been defined circulating opposite ways, which is exactly why everyone
defines them all the same way and never has to think about it again.
''',
                    },
                    {
                        "q": "One loop, containing a supply and six resistors in series. How many equations does each method need?",
                        "opts": [
                            "mesh needs six; nodal needs one",
                            "both need six",
                            "mesh needs one; nodal needs five",
                            "both need one",
                        ],
                        "a": 2,
                        "why": r'''
There is a single window, so mesh analysis has one unknown and one equation, and it is
finished. Nodal has to name a voltage at every junction between two resistors: seven
nodes in the loop, less ground, less the one the supply holds, leaves five unknowns.
This is the shape on which mesh wins outright — long series runs with few loops. A
bank of parallel branches is the mirror image, and there nodal wins by exactly as much.
''',
                    },
                    {
                        "q": "You solve the mesh equations and one of the currents comes out negative. What should you do?",
                        "opts": [
                            "redraw the circuit with that loop's arrow reversed and start again",
                            "take its magnitude and carry on",
                            "nothing — the sign says it circulates the other way, and every later formula stays correct",
                            "look for an arithmetic error, since a current cannot be negative",
                        ],
                        "a": 2,
                        "why": r'''
Nothing at all. The direction you drew was a guess, and the minus sign is the algebra
telling you the guess was wrong — that is information you were given for free, not an
error. Every subsequent expression already carries the sign, so leave it in place.
Stripping the minus is what actually causes wrong answers, because the shared branch
then gets a difference of two currents whose relative sign has been destroyed.
''',
                    },
                    {
                        "q": "Which conservation law sits under each method?",
                        "opts": [
                            "both are built on conservation of charge",
                            "mesh on KVL and energy; nodal on KCL and charge",
                            "mesh on KCL and charge; nodal on KVL and energy",
                            "both are built on Ohm's law alone",
                        ],
                        "a": 1,
                        "why": r'''
Mesh analysis writes KVL round each loop, which is conservation of energy: take a
charge all the way round and it must come back to the same energy it started with.
Nodal writes KCL at each node, which is conservation of charge. The two methods are
dual to one another all the way down — loops against nodes, voltages against
currents, resistances against conductances — and either one on its own is enough to
solve any resistive circuit.
''',
                    },
                ],
            },
            "build": {
                "title": "A two-loop ladder, finished to a specification",
                "minutes": 26,
                "brief": r'''
A ladder: a resistor along the chain, a resistor shunting to ground, then another along
and another down. Two windows in the drawing, so two mesh currents, and the second loop
loads the first — which is the whole reason this shape is worth practising.

The canvas gives you a 9 V supply, **R1 = 1.5 kΩ** along the top, and **R2 = 1 kΩ**
shunting to ground. Add the second rung — one more series resistor and one more shunt
— and a probe on the far end, so that

- the supply delivers exactly **4.00 mA**, and
- the probe reads exactly **2.00 V**.

## How the two conditions unpick

Take the supply current first, because it fixes the drop across the 1.5 kΩ and
therefore the voltage at the junction of the two loops. Once you know that junction
voltage you know the current in the 1 kΩ shunt, and KCL gives you what is left over for
the second rung. Then the second rung is a two-resistor divider carrying a current you
now know, and the 2.00 V requirement fixes how it splits.

Both new values are round numbers of kilohms.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "value": 1500},
                        {"id": "p3", "kind": "R", "x": 7, "y": 7, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [7, 6]},
                        {"a": [7, 8], "b": [7, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "value": 1500},
                        {"id": "p3", "kind": "R", "x": 7, "y": 7, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 9},
                        {"id": "p5", "kind": "R", "x": 10, "y": 5, "value": 1000},
                        {"id": "p6", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 2000},
                        {"id": "p7", "kind": "GND", "x": 11, "y": 9},
                        {"id": "p8", "kind": "OUT", "x": 13, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [7, 6]},
                        {"a": [7, 8], "b": [7, 9]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [11, 6]},
                        {"a": [11, 8], "b": [11, 9]},
                        {"a": [11, 5], "b": [13, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 9 V supply and four resistors, the given two untouched", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 9, 0.002, 'the supply voltage');
const rs = c.values('R');
c.assert(rs.length >= 4,
  'A two-rung ladder needs four resistors; found ' + rs.length + '.');
c.assert(rs.some(function (r) { return Math.abs(r - 1500) <= 15; }),
  'The 1.5 kΩ along the top is given — leave it at 1.5 kΩ.');
c.assert(rs.some(function (r) { return Math.abs(r - 1000) <= 10; }),
  'The 1 kΩ shunt is given — leave it at 1 kΩ.');
'''},
                    {"name": "the supply delivers 4.00 mA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
c.close(Math.abs(cur[ids[0]]), 0.004, 0.01, 'the current out of the supply');
'''},
                    {"name": "the junction between the two loops sits at 3.00 V", "code": r'''
const v = c.dc().v;
c.assert(v.some(function (x) { return Math.abs(x - 3.0) <= 0.03; }),
  'No node in this circuit is at 3.00 V. 4 mA through the 1.5 kΩ drops 6 V, so the ' +
  'junction of the two rungs has to sit at 9 - 6 = 3 V.');
'''},
                    {"name": "the probe reads 2.00 V", "code": r'''
c.close(c.vout(), 2.0, 0.02,
  'the probe voltage — it belongs at the far end of the second rung, not on the junction');
'''},
                ],
                "hints": [
                    "4 mA through the given 1.5 kΩ drops 6 V, so the junction between the rungs sits at $9 - 6 = 3$ V.",
                    "The 1 kΩ shunt has that 3 V across it, so it takes 3 mA. KCL at the junction leaves $4 - 3 = 1$ mA for the second rung.",
                    "1 mA flowing into the second rung, which must come out at 2.00 V after its shunt: the shunt is $2/0.001 = 2$ kΩ.",
                    "And the series resistor of the second rung drops the remaining $3 - 2 = 1$ V at 1 mA, so it is 1 kΩ. Place the probe on the node between them and the shunt.",
                ],
            },
            "blanks": {
                "title": "The two mesh equations of that ladder",
                "minutes": 9,
                "caption": "the same circuit, written as KVL round each window",
                "lang": "text",
                "brief": r"""
The circuit you have just drawn, now as equations. Mesh current $i_1$ circulates round
the left window and $i_2$ round the right one, both clockwise. Everything is in
milliamps and kilohms, so every product below is a voltage in volts.

The only thing that needs care is the resistor the two loops share.
""",
                "listing": """R1 = 1.5   along the top, from the 9 V supply to node A
R2 = 1     from node A down to ground     <-- on the boundary: both loops use it
R3 = 1     along the top, from node A to node B
R4 = 2     from node B down to ground

loop 1  (supply, R1, R2):    9 = 1.5*i1 + 1*(___)

loop 2  (R2, R3, R4):        0 = 1*(___) + 1*i2 + 2*i2

and solving the pair:        i1 = ___ mA        i2 = ___ mA
""",
                "blanks": [
                    {
                        "prompt": "Walking round loop 1, what net current does the shared resistor R2 carry?",
                        "hole": "?",
                        "opts": ["i1 - i2", "i1 + i2", "i2 - i1", "i1"],
                        "a": 0,
                        "why": "Both loops circulate clockwise, so on the branch they share they run "
                               "through it in opposite directions and it carries the difference. From "
                               "loop 1's side that is `i1 - i2`. Adding them would count a partly "
                               "cancelling pair twice over; using `i1` alone pretends the second loop is "
                               "not connected, which is the same circuit as leaving R3 and R4 off the "
                               "drawing altogether.",
                    },
                    {
                        "prompt": "Loop 2 walks the same resistor the other way. What does it see?",
                        "hole": "?",
                        "opts": ["i1 - i2", "i2 - i1", "i1 + i2", "i2"],
                        "a": 1,
                        "why": "`i2 - i1`, the exact negative of what loop 1 saw, because the two loops "
                               "traverse the shared branch in opposite directions. The sign has to flip: "
                               "if both equations used the same expression the two windows would no "
                               "longer be coupled correctly, and the pair would solve to a circuit that "
                               "is not on the page.",
                    },
                    {
                        "prompt": "Solve the two equations together. What is i1?",
                        "hole": "?",
                        "opts": ["3.6", "4", "4.5", "6"],
                        "a": 1,
                        "why": "Loop 2 reads $(i_2-i_1) + i_2 + 2i_2 = 0$, so $4i_2 = i_1$. Substituting "
                               "into loop 1: $9 = 1.5i_1 + (i_1 - i_1/4) = 2.25 i_1$, giving 4 mA. The "
                               "figure 3.6 mA is what the supply would deliver if the second rung were "
                               "not there at all — worth noticing, because it says the extra rung "
                               "*lowered* the total resistance and so raised the current, exactly as "
                               "another parallel path must.",
                    },
                    {
                        "prompt": "And i2?",
                        "hole": "?",
                        "opts": ["0.5", "2", "1", "1.5"],
                        "a": 2,
                        "why": "$i_2 = i_1/4 = 1$ mA. Since R3 and R4 are on the outside edge of the "
                               "right-hand window, they carry that mesh current and nothing else — so "
                               "1 mA through R4 = 2 kΩ puts node B at 2 V, which is the number the "
                               "schematic exercise asks you to hit. R2, being shared, carries "
                               "$i_1 - i_2 = 3$ mA, and 3 mA through 1 kΩ is the 3 V at node A.",
                    },
                ],
            },
            "derive": {
                "title": "Two windows, once and for all",
                "minutes": 13,
                "vars": ["i_1", "i_2", "E", "R_1", "R_2", "R_3"],
                "brief": r'''
The ladder from the reading, with letters instead of numbers. A source $E$ drives mesh 1
through a series resistance $R_1$; $R_2$ is the rung the two windows share; and $R_3$ is
everything else round mesh 2 added together — in the worked ladder that was the 1 kΩ along
the top plus the 2 kΩ down to ground, so $R_3 = 3$ kΩ.

Both mesh currents clockwise, $i_1$ on the left and $i_2$ on the right. Mesh 2 contains no
source at all, which is what makes the pair worth solving in general: it is the commonest
two-window shape there is.
''',
                "steps": [
                    {
                        "prompt": "Walking clockwise round mesh 1, the last thing you pass through is the shared rung. Write the voltage drop across $R_2$ in terms of the two mesh currents.",
                        "answer": "R_2 (i_1 - i_2)",
                        "placeholder": "R_2 \\cdot (\\text{something})",
                        "hint": "Both loops are clockwise, so on the branch they share they run through it in opposite directions. Walking mesh 1, the current in the direction you are walking is $i_1$ minus whatever mesh 2 is sending back the other way.",
                    },
                    {
                        "prompt": "Mesh 2 contains no source, so its KVL equation is $R_2(i_2 - i_1) + R_3 i_2 = 0$. Solve it for $i_2$ in terms of $i_1$.",
                        "answer": "\\frac{R_2 i_1}{R_2 + R_3}",
                        "hint": "Gather the two $i_2$ terms on one side. Both resistances of mesh 2 multiply $i_2$; only the shared one multiplies $i_1$.",
                        "deconstruct": [
                            "Expand: $R_2 i_2 - R_2 i_1 + R_3 i_2 = 0$.",
                            "So $i_2 (R_2 + R_3) = R_2 i_1$, and one division finishes it.",
                        ],
                    },
                    {
                        "prompt": "Mesh 1's equation is $E = R_1 i_1 + R_2(i_1 - i_2)$. Substitute what you just found and solve for $i_1$.",
                        "answer": "\\frac{E(R_2+R_3)}{R_1 R_2 + R_1 R_3 + R_2 R_3}",
                        "hint": "Put everything over $R_2 + R_3$. The $R_2^2$ term that appears when you expand $(R_1+R_2)(R_2+R_3)$ is cancelled exactly by the $-R_2^2$ coming from the substitution, which is why the denominator ends up with no squares in it.",
                        "deconstruct": [
                            "$E = i_1(R_1 + R_2) - R_2 \\cdot \\frac{R_2 i_1}{R_2+R_3}$, so $E = i_1 \\cdot \\frac{(R_1+R_2)(R_2+R_3) - R_2^2}{R_2+R_3}$.",
                            "Expand the top: $R_1R_2 + R_1R_3 + R_2^2 + R_2R_3 - R_2^2$, and the squares cancel.",
                        ],
                    },
                    {
                        "prompt": "The shared rung carries $i_1 - i_2$. Write that current in terms of $E$ and the three resistances.",
                        "answer": "\\frac{E R_3}{R_1 R_2 + R_1 R_3 + R_2 R_3}",
                        "hint": "From step 2, $i_2$ is $i_1$ scaled by $R_2/(R_2+R_3)$, so $i_1 - i_2$ is $i_1$ scaled by $R_3/(R_2+R_3)$. That factor cancels the bracket in the numerator of $i_1$.",
                        "deconstruct": [
                            "$i_1 - i_2 = i_1\\left(1 - \\frac{R_2}{R_2+R_3}\\right) = i_1 \\cdot \\frac{R_3}{R_2+R_3}$.",
                            "Multiply by the $i_1$ of the previous step and the $(R_2+R_3)$ top and bottom cancel.",
                        ],
                    },
                    {
                        "prompt": "Put the ladder's numbers in: $E = 12$ V, $R_1 = 2$ kΩ, $R_2 = 6$ kΩ and $R_3 = 3$ kΩ. What current does the shared rung carry, in milliamps?",
                        "answer": "1",
                        "hint": "Volts over kilohms comes out in milliamps directly, so the units look after themselves. The denominator is three products added.",
                        "deconstruct": [
                            "Denominator: $2 \\times 6 + 2 \\times 3 + 6 \\times 3 = 12 + 6 + 18 = 36$.",
                            "Numerator: $12 \\times 3 = 36$.",
                        ],
                    },
                ],
                "closing": r'''
Three things are worth taking away from that denominator.

It is **symmetric** in the three resistances — $R_1R_2 + R_1R_3 + R_2R_3$ treats all three
alike — and it is the same combination that came out of module 7's nodal derivation. That
is not a coincidence: with one of that module's two supplies set to zero, its circuit is
this one, and what a network does cannot depend on which set of unknowns was used to find
it.

It **behaves at the limits**. Let $R_3$ grow without bound — the right-hand window becomes
an open circuit — and

$$i_1 \to \frac{E R_3}{R_3(R_1 + R_2)} = \frac{E}{R_1 + R_2}$$

which is the single-loop answer, with the shared rung carrying all of it. Shrink $R_3$ to
zero instead — the right-hand window shorts the rung out — and $i_1 \to E/R_1$ while the
shared current goes to zero, because every electron takes the free path. Both are what the
circuit obviously does, and a formula that failed either of them would be wrong.

And it is **linear in $E$**. Double the supply and every current in the circuit doubles,
with the shape of the network unchanged. That is the property module 9 is about, and it is
the reason a circuit made of resistors and independent sources can be taken apart one
source at a time.
'''
            },
        },
        # ---- M9 -----------------------------------------------------------
        {
            "title": "Superposition and linearity",
            "summary": "With more than one source, each one's contribution can be found on its own and the results added. Voltages and currents only — never power.",
            "concepts": [
                "A circuit of resistors and fixed sources is *linear*: every node voltage and every branch current is a weighted sum of the source values, and the weights depend only on the resistors.",
                "Linearity has a second half worth as much as the first. Scale every source by $k$ and every voltage and every current in the circuit scales by $k$ as well — which is what lets you assume a convenient answer, work backwards to the source that would produce it, and then scale the whole solution to the source you actually have.",
                "Superposition follows immediately from that. Find the response to each source with all the others killed, then add the responses — the total is what the circuit does with all of them present.",
                "Killing a voltage source means replacing it with a wire, because a source of zero volts holds its two terminals at the same potential. Killing a current source means removing it and leaving the gap, because a source of zero amps is an open circuit.",
                "What is never killed is the resistance. Only the source in a branch is neutralised; every resistor stays exactly where it was, and forgetting that is the single commonest way to get a wrong answer with this method.",
                "A contribution can be negative, and it can be bigger than the total. A load hanging on a rail contributes a negative number of volts to that rail: $+12$ V from the supply and $-6$ V from the load make a node that sits at 6 V.",
                "Superposition works on voltages and on currents. It does **not** work on power: two contributions of 1 V across the same resistor make 2 V, which is four times the power of one alone, not twice.",
                "All of it rests on the components being linear. A diode, a filament lamp, a transistor, or any supply pushed into its current limit breaks the assumption, and then superposition returns a number that is not what the circuit does.",
                "It is rarely the quickest route to a number — nodal analysis usually is — but it is the only route to *how much of the answer each source is responsible for*, which is the real question whenever one of the sources is interference rather than signal.",
            ],
            "read": [
                {
                    "title": "Turn the knob, and watch everything move together",
                    "minutes": 14,
                    "body": r'''
Put any collection of resistors on the bench, drive it from an adjustable supply, and hang
a meter on every node and an ammeter in every branch. Now turn the supply slowly up from
zero to twenty volts while somebody watches the meters.

Nothing surprising happens, and that is the point. Every needle leaves zero at the same
moment and rises smoothly, all of them together, each holding a fixed ratio to all the
others. A node that reads 1.00 V when the supply is on 4 V reads 2.00 V when the supply is
on 8 V and 4.50 V when it is on 18 V. Nothing lags, nothing sticks, nothing reverses, and
no node ever needs the supply to reach some threshold before it starts to respond.

That behaviour is not universal, and seeing what it is *not* true of is the fastest way to
see what is being claimed. Turn the same knob with a filament lamp in the circuit and the
current falls behind: the filament heats, its resistance climbs, and doubling the voltage
gives distinctly less than double the current. Put a silicon diode in the loop and for the
first half-volt essentially nothing flows at all, then over the next hundred millivolts the
current climbs by a factor of ten. Those circuits respond; they just do not respond *in
proportion*.

A circuit that does respond in proportion is called **linear**, and the property is worth
naming because most of what follows, in this course and in the ones after it, is built on
it.

## The two halves of the property

Write $f(\,\cdot\,)$ for "what the circuit does" — feed in a set of source values, get back
some particular response, say the voltage at node A or the current in the third resistor.
(The letter $R$ is spoken for in this subject, so it is $f$ here.) Linearity is two
statements about that map.

**Scaling.** Multiply every source by the same number $k$, and every response is multiplied
by $k$:

$$f(k s) = k\,f(s)$$

**Adding.** Feed in one set of source values, then another, then their sum, and the third
response is the sum of the first two:

$$f(s_a + s_b) = f(s_a) + f(s_b)$$

The second is the whole of superposition, hiding in one line. The rest of this module is
about cashing it in. But the first is immediately useful on its own, and it is the easier
of the two to get a feel for, so take it first.

## Why a resistor network has the property

You already have the proof; module 7 wrote it out without calling it one.

Nodal analysis takes an unknown voltage at each node and writes KCL there. Every term in
those equations is one of exactly two things: a resistor current $(v_i - v_j)/R$, or a
current-source value — and a node that a voltage source touches is not an unknown at all,
it is pinned to a number the source supplies. Look at what that means for the shape of the
equations. Each unknown appears to the first power and never multiplied by
another unknown — there is no $v^2$, no $v_1 v_2$, no $\sqrt{v}$, because Ohm's law has none
of those in it. Collect the terms and the whole system reads

$$G\,\mathbf{v} = \mathbf{b}$$

where $G$ is built entirely from conductances $1/R$ and $\mathbf{b}$ is built entirely from
the source values. Solving is $\mathbf{v} = G^{-1}\mathbf{b}$, and $G^{-1}$ does not contain
a single source value — it is made of resistors and nothing else.

So every node voltage is a fixed set of weights applied to the sources:

$$v_A = a_1 E_1 + a_2 E_2 + \cdots$$

with each $a$ a pure number, or a resistance if the corresponding source is a current
source, determined by the resistor values alone. Double every $E$ and $v_A$ doubles, because
the $a$'s did not move. That is scaling. Add two sets of sources and the responses add,
because the expression is a sum of separate terms. That is adding. Both halves fall out of
the same observation: a resistor obeys a law with no powers in it.

## Worked: a divider, three ways round

Take the simplest network there is. A supply $E = 12.0$ V, a 2.00 kΩ resistor from it down
to node A, and a 1.00 kΩ resistor from A to ground.

```text
    R_total  =  2.00 + 1.00                  =  3.00 kohm
    I        =  12.0 V / 3.00 kohm           =  4.00 mA
    V_A      =  4.00 mA * 1.00 kohm          =  4.00 V
    P_total  =  12.0 V * 4.00 mA             =  48.0 mW
```

Now change one thing at a time.

**Double the supply, to 24.0 V.** Every source in the circuit has been scaled by 2, so
every voltage and every current scales by 2:

```text
    I    =  8.00 mA          V_A  =  8.00 V
    P    =  24.0 V * 8.00 mA =  192 mW        <- four times, not twice
```

The power went up by $2^2$. It had to: $P = VI$ and both factors doubled. Power is not a
response in the sense above — it is a *product* of two responses — and that single fact is
responsible for most of the mistakes people make with this material. Hold on to it.

**Double both resistances instead, to 4.00 kΩ and 2.00 kΩ, with the supply back on 12.0 V.**

```text
    R_total  =  6.00 kohm
    I        =  2.00 mA                       <- halved
    V_A      =  2.00 mA * 2.00 kohm  =  4.00 V   <- unchanged
    P_total  =  12.0 V * 2.00 mA     =  24.0 mW  <- halved
```

Node A has not moved at all. That is worth staring at, because it shows that "linear" is a
statement about the *sources*, not about the resistors. Scale the sources and everything
scales with them. Scale the resistors and the voltages sit exactly where they were while
the currents halve — a useful piece of scaling in its own right, and not the same piece.
The response is not a linear function of resistance; resistance sits in the denominator,
which is about as far from linear as an expression gets.

## Worked: assume the answer, then scale it

Here is the trick the scaling half of linearity buys you, and it turns an unpleasant ladder
into six lines of arithmetic with no simultaneous equations anywhere.

The ladder: a supply, then along the top $R_1 = 1$ kΩ to node A, $R_3 = 1$ kΩ from A to
node B, $R_5 = 1$ kΩ from B to node C; and down to ground, $R_2 = 5$ kΩ at A, $R_4 = 3$ kΩ
at B, $R_6 = 2$ kΩ at C. The supply is set to 18.0 V. What does node C sit at?

Forwards, that means collapsing the whole ladder from the far end, dividing at every node,
and hoping the fractions stay tidy. Backwards, it means nothing of the sort. Start by
*assuming* the answer, choosing the value that makes the arithmetic pleasant:

```text
ASSUME  C = 1.000 V, and work back towards the supply

    R6 = 2k carries      1.000 / 2      =  0.500 mA
    R5 = 1k carries the same 0.500 mA (nothing joins between B and C)
      and drops          0.500 * 1      =  0.500 V
    B  =  1.000 + 0.500                 =  1.500 V

    R4 = 3k carries      1.500 / 3      =  0.500 mA
    R3 = 1k carries      0.500 + 0.500  =  1.000 mA
      and drops          1.000 * 1      =  1.000 V
    A  =  1.500 + 1.000                 =  2.500 V

    R2 = 5k carries      2.500 / 5      =  0.500 mA
    R1 = 1k carries      1.000 + 0.500  =  1.500 mA
      and drops          1.500 * 1      =  1.500 V
    supply needed  =  2.500 + 1.500     =  4.000 V
```

Volts, kilohms and milliamps are consistent with one another — one volt across one kilohm
is one milliamp — so no factor of a thousand can go missing in any of those lines.

Nothing was ever unknown there. Every line is one Ohm's law or one addition at a node,
because working inwards you always already have the number you need. What the walk proves
is that **4.000 V in produces 1.000 V out**, so the circuit's weight on its one source is
$1/4$. The supply is actually on 18.0 V, and by scaling

$$v_C = 18.0 \times \tfrac{1}{4} = 4.50 \text{ V}$$

and every current in the ladder is $18.0/4.000 = 4.5$ times what the walk-back said: 6.75
mA from the supply, 2.25 mA in each of the three shunts. Check one of those against Ohm's
law directly — node C at 4.50 V across $R_6 = 2$ kΩ is 2.25 mA — and it holds.

## The mistake, and why it is tempting

The mistake is to hear "the circuit is linear" and conclude that everything about it is
proportional to everything else. Three things are not, and each catches somebody.

**Power is not.** It is a product of two quantities that each scale, so it scales as the
square. Raise a supply by 40% and the heat goes up by $1.4^2 = 1.96$ — very nearly double.

**Resistance is not a source.** Doubling a resistor does not double anything; it usually
changes some voltages up, some down, and some not at all, and the dependence is a ratio
rather than a proportion.

**A source is not automatically an input.** Linearity relates the *responses* to the
*sources*. If the thing you are varying is a resistance — a potentiometer, a thermistor, a
sensor whose resistance is the measurement — then you are outside the property, and you
must solve the circuit again rather than scale the answer.

The power case is the tempting one, because it feels like the same kind of statement and
for the whole of the arithmetic above it very nearly behaves like one: powers do scale,
just by the square. It is only when two *different* sources are involved that the failure
becomes total rather than a factor, and that case gets a section of its own later in this
module.

## Where linearity stops

It stops at the components. Everything above rests on Ohm's law being a straight line
through the origin, and real parts leave that line in four common ways.

**A junction.** Diodes, LEDs, transistors: the current is exponential in the voltage, not
proportional to it. A circuit containing one is not linear anywhere, and superposition on it
gives a number that is simply not the circuit's.

**Heat.** A filament lamp at operating temperature has roughly ten times the resistance it
has cold. Even an ordinary resistor drifts a little — tens to hundreds of parts per million
per degree, depending on how it is made — which matters when it is dissipating enough to
warm itself up.

**A limit.** Every real bench supply has a current limit, and every real current source has
a compliance range — a largest voltage it can put across itself. Ask for more than either
can give and the source stops being the thing your equations described.

**Saturation of the material.** An inductor with an iron core is linear until the core
saturates, at which point its inductance collapses. Nothing in this DC course depends on
that, but it is the same failure.

What replaces linearity out there is either a small-signal approximation — linearise the
part about its operating point, and everything in this module applies again to the
*changes* around that point, which is what the whole of amplifier design is built on — or
iteration: guess, solve, correct, repeat. Neither is in this course. What is in this course
is the reason it is worth doing so much work on the linear case: you make circuits linear
on purpose, because a linear circuit can be reasoned about, and one that is not has to be
simulated.
''',
                },
                {
                    "title": "One source at a time",
                    "minutes": 15,
                    "body": r'''
Here is the circuit that makes the question unavoidable. A 10.0 V supply reaches node A
through 2.00 kΩ. An 8.00 V supply reaches the same node A through 1.00 kΩ. And 2.00 kΩ runs
from A down to ground. Nodal analysis takes about a line and a half and says node A sits at
6.50 V.

Fine. But now suppose the 8 V rail is not a supply you chose — suppose it is a neighbouring
circuit's rail leaking in through a shared resistor, and your job is to get rid of it. How
much of that 6.50 V is the leak? Nodal analysis will not tell you. It gives one number and
no breakdown, and the breakdown is the thing you actually need.

## The claim

Module 8 ended by pointing at this and the last section proved it: for a network of
resistors and fixed sources, every response is a weighted sum of the sources,

$$v_A = a_1 E_1 + a_2 E_2$$

with $a_1$ and $a_2$ depending only on the resistors. Now put $E_2 = 0$ and look at what is
left: $v_A = a_1 E_1$. That is the first supply's contribution, on its own, and it can be
obtained by *solving a circuit* — the same circuit with the second source set to zero —
rather than by finding $a_1$ symbolically. Do the same the other way round for $a_2 E_2$.
Then add them.

That is superposition, and it is not a new law. It is linearity, used backwards.

## What "set a source to zero" means on the bench

This is the only part of the method with a rule to memorise, and it is where nearly every
wrong answer comes from, so it is worth deriving rather than remembering.

A source is defined by the constraint it imposes, and killing it means imposing the
zero version of that same constraint.

**A voltage source** insists that the potential difference between its two terminals is
$E$, whatever current flows. Set $E = 0$ and it insists the two terminals are at the same
potential whatever current flows. There is a component that does exactly that: a piece of
wire. **A dead voltage source is a short circuit.**

**A current source** insists that the current through it is $I$, whatever voltage appears
across it. Set $I = 0$ and it insists no current flows, whatever voltage appears. There is a
component that does exactly that too: a gap. **A dead current source is an open circuit.**

They are duals, and the pair is worth learning together, because swapping them does not
give a slightly wrong answer — it gives the answer to an unrelated circuit.

## The rule underneath the rule

Only the source is killed. **Every resistor stays exactly where it is.**

That includes the resistor in series with the source you just killed, and it includes the
source's own internal resistance if module 6 taught you to draw one. A real 8 V supply with
0.5 Ω of internal resistance becomes, when killed, a 0.5 Ω resistor to ground — not
nothing, and not a wire either.

The reason this is worth saying twice is that "kill the source" reads, to the eye, like
"delete that part of the circuit". The branch and the source occupy the same region of the
drawing. But the 1 kΩ feeding node A is soldered to the board and is not going anywhere; all
that has changed is what its far end is connected to. Before, it went to an 8 V rail. Now it
goes to ground. It is still a path from node A to somewhere, it still loads the node, and
leaving it out changes the answer by a large factor.

## Worked: two supplies into one node

The circuit from the top. $E_1 = 10.0$ V through $R_1 = 2.00$ kΩ to node A; $E_2 = 8.00$ V
through $R_2 = 1.00$ kΩ to node A; $R_3 = 2.00$ kΩ from A to ground.

```text
STEP 1 — kill E2: a wire in its place. R2 now runs from A to ground.

    below A:   R2 || R3  =  1*2/(1+2)          =  0.667 kohm
    a divider: R1 = 2 kohm on top, 0.667 below

    v_A(1)  =  10.0 * 0.667/(2.00 + 0.667)     =  10.0 * 0.250  =  2.50 V

STEP 2 — kill E1 instead: a wire there, R1 now runs from A to ground.

    below A:   R1 || R3  =  2*2/(2+2)          =  1.00 kohm
    a divider: R2 = 1 kohm on top, 1.00 below

    v_A(2)  =  8.00 * 1.00/(1.00 + 1.00)       =  8.00 * 0.500  =  4.00 V

STEP 3 — add.

    v_A  =  2.50 + 4.00                        =  6.50 V
```

Check it against nodal, which is what you would have done if you only wanted the number.
Currents leaving A must sum to zero:

```text
    (6.50 - 10.0)/2  +  (6.50 - 8.00)/1  +  6.50/2
      = -1.75  -  1.50  +  3.25   =  0        closes
```

Now read the breakdown, because that was the point of the exercise. The 8 V supply is
responsible for 4.00 of the 6.50 V and the 10 V supply for only 2.50, even though it is the
larger source. The reason is the resistance in the way: the 8 V rail reaches the node
through 1 kΩ and the 10 V rail through 2 kΩ, and what a source contributes falls as its own
series resistance rises. If that 8 V rail were interference, the fix is now obvious — raise
$R_2$, or lower $R_3$, either of which cuts $a_2$ — and it was not obvious from the number
6.50.

Currents superpose too, and it is worth doing one to see that the method is not restricted
to node voltages. The current in $R_2$, taken positive when it flows from the supply towards
node A:

```text
    with E2 alone   (8.00 - 4.00)/1.00        =  +4.00 mA
    with E1 alone   (0 - 2.50)/1.00           =  -2.50 mA     <- backwards, into the wire
    sum                                        =  +1.50 mA

    directly, both live:  (8.00 - 6.50)/1.00  =  +1.50 mA     agrees
```

Notice the second contribution is negative. Nothing is wrong: with $E_2$ killed the far end
of $R_2$ is at ground and node A is at 2.50 V, so that resistor is carrying current *away*
from A. A contribution that comes out negative is a contribution that opposes, and the
arithmetic handles it with no special treatment.

## Worked: a supply and a load

The second source need not be a supply at all. A chip that draws a fixed current from a rail
regardless of what the rail does is a current source, and treating it as one is how you find
out how far the rail sags.

A 12.0 V rail feeds node A through $R_1 = 2.00$ kΩ. From A, $R_2 = 6.00$ kΩ runs to ground.
Also hanging on A is a chip drawing a constant 3.00 mA.

```text
STEP 1 — kill the current source: remove it, leave the gap. Nothing else changes.

    a plain divider now
    v_A(1)  =  12.0 * 6.00/(2.00 + 6.00)      =  9.00 V

STEP 2 — kill the voltage source: a wire in its place. R1 now runs from A to ground.

    the 3.00 mA has only resistors to flow through, and it sees
        R1 || R2  =  2*6/(2+6)                 =  1.50 kohm
    it is drawn OUT of node A, so it pulls the node down

    v_A(2)  =  -3.00 mA * 1.50 kohm            =  -4.50 V

STEP 3 — add.

    v_A  =  9.00 - 4.50                        =  4.50 V
```

Check by KCL at A, with all three elements live:

```text
    into A from the rail   (12.0 - 4.50)/2.00  =  3.75 mA
    out through R2          4.50/6.00          =  0.75 mA
    out through the chip                       =  3.00 mA
    3.75  =  0.75 + 3.00                          closes
```

The unloaded rail would have sat at 9.00 V and the load pulled it to 4.50 V — a sag of
exactly the $-4.50$ V that superposition attributed to it. That is the number a designer
wants, because it is what tells you the divider is far too weak for the load it is carrying,
and by how much.

## The mistake people actually make

Deleting the branch instead of shorting the source.

In the two-supply example above, delete $R_2$ along with the 8 V supply and step 1 becomes a
plain 2 kΩ / 2 kΩ divider: $10.0 \times 0.5 = 5.00$ V instead of 2.50 V. The total then
comes out at 9.00 V, which is not what the circuit does and is not close.

It is tempting for a physical reason, not a careless one. "Turn that supply off" sounds like
"disconnect it", and if you actually unplugged the 8 V bench supply and pulled its lead out,
the branch really would be open — the resistor would be dangling. The distinction
superposition needs is that a supply turned down to zero volts is still *connected*, still
holding its terminals together, still a path to ground. A supply *unplugged* is a different
circuit. Superposition is about turning it down, not pulling it out; what happens when you
pull it out is an equally reasonable question with an entirely different answer.

The tell is the count: kill a source and the number of resistors in the drawing must not
change. If a resistor disappeared, you did the wrong thing.

## Where superposition stops

**Power.** It does not superpose, at all, ever. It gets its own section next.

**Anything nonlinear.** The derivation used $\mathbf{v} = G^{-1}\mathbf{b}$ and there is no
such expression for a circuit with a diode in it. Superposition on a rectifier gives an
answer that is not merely inaccurate but meaningless.

**Dependent sources.** A source whose value is set by a voltage or current elsewhere in the
circuit — the model of a transistor, an op-amp, an amplifier stage — keeps the circuit
linear, so superposition still applies. But a dependent source is *never* killed. It is not
one of the inputs; it is part of the network, like a resistor, and it must be left in and
allowed to respond in every one of the sub-circuits. Kill only the independent sources, one
at a time. That is a second-year distinction and this course's circuits contain none of
them, but it is the rule people get wrong first when they meet one.

**Effort.** Three sources means three complete solutions of the circuit and then an
addition, where nodal analysis would have needed one. If all you want is the number, use
nodal. Reach for superposition when you want to know whose number it is.
''',
                },
                {
                    "title": "Why power is different, and what the weights are worth",
                    "minutes": 13,
                    "body": r'''
Two claims are left. The first is that the method breaks completely on power, which sounds
like a footnote and is not. The second is that its real value is not speed — nodal analysis
is faster — but that the intermediate results it produces are the numbers a designer
actually wants. Both are best seen on circuits with numbers in them.

## Where the power goes wrong

Take one resistor $R$ with two contributions of voltage across it, $v_1$ from one source and
$v_2$ from another. The voltage superposes, so the actual voltage across it is $v_1 + v_2$
and the actual power is

$$P = \frac{(v_1 + v_2)^2}{R} = \frac{v_1^2}{R} + \frac{v_2^2}{R} + \frac{2 v_1 v_2}{R}$$

The first two terms are the powers the two sources would each produce alone. The third term
is the whole problem. It is called the **cross term**, it has no home in either source's
account, and it is not small: its size is twice the geometric mean of the other two, so
when the two contributions are comparable it is the largest of the three.

It also has a sign. If $v_1$ and $v_2$ push the same way it adds; if they oppose, it
subtracts, and the true power can be far *less* than either source would produce on its own.
Here is that case with real numbers, on the circuit from the previous section.

$E_1 = 10.0$ V through $R_1 = 2.00$ kΩ to node A; $E_2 = 8.00$ V through $R_2 = 1.00$ kΩ to
node A; $R_3 = 2.00$ kΩ from A to ground. Ask for the power in $R_2$, the 1 kΩ.

```text
Contributions to the voltage ACROSS R2, measured from node A to the supply end:

    E1 alone (E2 shorted):  A is at 2.50 V, supply end at 0
                            v_1  =  2.50 - 0     =  +2.50 V
    E2 alone (E1 shorted):  A is at 4.00 V, supply end at 8.00
                            v_2  =  4.00 - 8.00  =  -4.00 V

    sum                     v    =  2.50 - 4.00  =  -1.50 V
    directly, both live:    6.50 - 8.00          =  -1.50 V     agrees
```

Now the powers.

```text
    from v_1 alone      2.50^2 / 1.00k   =   6.25 mW
    from v_2 alone      4.00^2 / 1.00k   =  16.00 mW
    naive sum                            =  22.25 mW     <- wrong, by a factor of ten

    cross term          2*(2.50)*(-4.00) / 1.00k  =  -20.00 mW

    true power          22.25 - 20.00    =   2.25 mW
    check:  1.50^2 / 1.00k               =   2.25 mW     agrees
```

Two contributions that would separately have dissipated 6.25 mW and 16.00 mW combine to
dissipate 2.25 mW, because they very nearly cancel. Adding the powers overstates the answer
by very nearly ten times. There is no fudge factor and no correction to apply: the only
correct procedure is to superpose the **voltages**, or the **currents**, and square at the
very end.

That rule is worth stating as a discipline rather than a caution. Do all the superposing in
volts and amps. Get the total. *Then* compute power, once, from the total.

The one situation where the cross term genuinely vanishes is worth knowing because it is
coming in the next courses: if $v_1$ and $v_2$ vary with time in ways whose product averages
to zero — sine waves at different frequencies, for instance — then $\overline{2v_1v_2} = 0$
and the *average* powers do add. That is why a signal's power and an interfering tone's
power can be added at the end of a noise budget. It is a property of the signals, not of the
circuit, and it is false for the DC case here, where $v_1$ and $v_2$ are constants and their
product is emphatically not zero.

## What the weights are worth: a level shifter

Now the other claim. Here is a circuit whose entire purpose is the breakdown superposition
produces.

A sensor puts out a signal $v_s$ that swings from 0 to 6.00 V. The converter it must drive
accepts 2.50 V to 3.50 V and nothing else. Three resistors fix it: $R_1 = 3.00$ kΩ from the
sensor to node A, $R_2 = 1.00$ kΩ from a fixed 5.00 V reference to node A, and $R_3 = 1.50$
kΩ from A to ground.

```text
CONTRIBUTION OF THE SIGNAL   (reference shorted, R2 stays and runs A to ground)

    below A:  R2 || R3  =  1.00*1.50/2.50   =  0.600 kohm
    v_A(s)  =  v_s * 0.600/(3.00 + 0.600)   =  v_s * 0.1667  =  v_s / 6

CONTRIBUTION OF THE REFERENCE   (signal source shorted, R1 stays and runs A to ground)

    below A:  R1 || R3  =  3.00*1.50/4.50   =  1.00 kohm
    v_A(r)  =  5.00 * 1.00/(1.00 + 1.00)    =  2.50 V

TOTAL

    v_A  =  v_s/6  +  2.50 V
```

Read that as a specification and the design is finished. The circuit has a **gain** of
$1/6$ on the signal and an **offset** of 2.50 V, so an input span of 0 to 6.00 V arrives as
2.50 V to 3.50 V, exactly the window the converter wants. Check the ends:

```text
    v_s = 0.00 V    ->  0.000 + 2.50  =  2.50 V
    v_s = 3.00 V    ->  0.500 + 2.50  =  3.00 V
    v_s = 6.00 V    ->  1.000 + 2.50  =  3.50 V
```

Solve the same circuit by nodal analysis at $v_s = 6.00$ V and you get 3.50 V — one number,
correct, and useless for design, because it does not tell you which part of the 3.50 V is
gain and which is offset. Superposition hands over both weights separately, and the two
weights are the two knobs you have: $R_1$ against $R_2 \parallel R_3$ sets the gain, and the
reference voltage then scales the offset without disturbing the gain at all. That is why
this method survives in a subject where nodal analysis is faster.

(A detail worth noticing in passing: at $v_s = 3.00$ V the node also sits at 3.00 V, so the
signal source is delivering no current at all at that point. Above it the sensor sources
current; below it the sensor sinks it. Nothing in the analysis cares, but it is the kind of
thing that surprises people on the bench.)

## The same weights, read as sensitivity

A supply rail is never exactly what its label says. Take a 12.0 V rail with 0.40 V of
ripple on it — a 50 or 100 Hz remnant of the mains, riding on the DC — feeding a divider of
9.00 kΩ on top and 3.00 kΩ below.

Superposition splits the rail into two sources in series: a clean 12.0 V and a 0.40 V
disturbance. Both see the same weight, because it is the same circuit:

```text
    weight  =  3.00/(9.00 + 3.00)         =  0.250

    DC out      12.0 * 0.250   =  3.00 V
    ripple out   0.40 * 0.250  =  0.100 V

    total: 3.00 V with 0.100 V of ripple on it
```

Solve it as one circuit at 12.4 V and you get 3.10 V, which is true and answers a question
nobody asked. The useful statement is that a quarter of whatever appears on that rail
appears on the output, so 100 mV of ripple is what you have to live with and dividing harder
will not help — the ratio is the same for the wanted part and the unwanted part. If 100 mV
is too much, the divider is the wrong tool and the rail needs filtering instead. That
conclusion is a superposition argument from beginning to end.

## Where all of this stops

Everything above is downstream of linearity, so it fails exactly where linearity fails, and
it is worth being precise about which failure is which.

**Nonlinear parts.** With a diode or a transistor in the loop there are no fixed weights, so
there is no breakdown to compute. The replacement is the small-signal method: linearise the
part about its operating point and apply every idea in this module to the small changes
about that point. That is how amplifiers are analysed, and it is why this module matters far
beyond the resistor networks it was taught on.

**Dependent sources.** They keep the circuit linear and must be left alive in every
sub-circuit. Only independent sources get killed.

**Power, always.** Not sometimes, not approximately. Superpose voltages and currents, then
compute power once at the end. It is the rule this module is most often broken on, and the
one that costs the most when it is.
''',
                },
            ],
            "derive": {
                "title": "Two supplies into one node, once and for all",
                "minutes": 14,
                "vars": ["V_1", "V_2", "R_1", "R_2", "R_3"],
                "brief": r'''
The circuit from the reading, with letters instead of numbers, because it is the shape you
meet most often: two rails arriving at the same point through their own resistances, with a
third resistance from that point to ground.

A supply $V_1$ reaches node A through $R_1$. A supply $V_2$ reaches the same node A through
$R_2$. And $R_3$ runs from A down to ground. Everything is measured with respect to ground,
and both supplies have their negative terminals there.

Do it by superposition — kill one, solve, kill the other, solve, add — and you will finish
with a formula worth carrying, plus a check on it that costs nothing.
''',
                "steps": [
                    {
                        "prompt": "Kill $V_2$: a wire in its place, and $R_2$ stays where it is, now running from node A to ground. What single resistance is there from A to ground?",
                        "answer": "\\frac{R_2 R_3}{R_2 + R_3}",
                        "placeholder": "two resistors in parallel",
                        "hint": "$R_2$ and $R_3$ now both run from the same node to the same place, so they are in parallel. Product over sum.",
                    },
                    {
                        "prompt": "That leaves an ordinary divider: $R_1$ on top, and what you just found underneath. Write $V_1$'s contribution to the node voltage, as a single fraction with nothing nested inside it.",
                        "answer": "\\frac{V_1 R_2 R_3}{R_1 R_2 + R_1 R_3 + R_2 R_3}",
                        "placeholder": "\\frac{\\text{something}}{R_1R_2 + R_1R_3 + R_2R_3}",
                        "hint": "Start from $V_1 \\cdot \\dfrac{R_2R_3/(R_2+R_3)}{R_1 + R_2R_3/(R_2+R_3)}$ and multiply top and bottom by $R_2 + R_3$.",
                        "deconstruct": [
                            "Top becomes $V_1 R_2 R_3$.",
                            "Bottom becomes $R_1(R_2 + R_3) + R_2R_3$, which expands to $R_1R_2 + R_1R_3 + R_2R_3$.",
                        ],
                    },
                    {
                        "prompt": "Now kill $V_1$ instead, leaving $R_1$ in place running from A to ground. Write $V_2$'s contribution the same way.",
                        "answer": "\\frac{V_2 R_1 R_3}{R_1 R_2 + R_1 R_3 + R_2 R_3}",
                        "placeholder": "the same shape, with the labels swapped",
                        "hint": "Nothing new to do. The circuit is the previous one with $R_1$ and $R_2$ exchanged and $V_2$ driving, so exchange them in the answer as well. The denominator is symmetric and does not change.",
                    },
                    {
                        "prompt": "Add the two contributions. Write the node voltage $v_A$ with both supplies live.",
                        "answer": "\\frac{V_1 R_2 R_3 + V_2 R_1 R_3}{R_1 R_2 + R_1 R_3 + R_2 R_3}",
                        "placeholder": "one fraction, two terms on top",
                        "hint": "Both contributions already sit over the same denominator, so there is nothing to do but add the numerators.",
                    },
                    {
                        "prompt": "Sanity check. Take the shunt away by letting $R_3 \\to \\infty$, so the only path between the two supplies is $R_1$ then $R_2$. What does $v_A$ become?",
                        "answer": "\\frac{V_1 R_2 + V_2 R_1}{R_1 + R_2}",
                        "placeholder": "a weighted average of the two supplies",
                        "hint": "Divide every term on the top and the bottom by $R_3$, then let the remaining $1/R_3$ terms go to zero.",
                        "deconstruct": [
                            "Top over $R_3$: $V_1R_2 + V_2R_1$, with no $R_3$ left in it.",
                            "Bottom over $R_3$: $R_1R_2/R_3 + R_1 + R_2$, and the first term vanishes.",
                            "The result is a weighted average of the two supplies — which is what a single resistor chain between two rails must give.",
                        ],
                    },
                    {
                        "prompt": "Back to the full formula, and put the numbers in: $V_1 = 10$ V through $R_1 = 2$ kΩ, $V_2 = 8$ V through $R_2 = 1$ kΩ, and $R_3 = 2$ kΩ. What is $v_A$, in volts?",
                        "answer": "6.5",
                        "placeholder": "a number of volts",
                        "hint": "Work in kilohms throughout and the units look after themselves — every term on the top is volts times kilohms squared, and every term on the bottom is kilohms squared.",
                        "deconstruct": [
                            "Denominator: $2 \\times 1 + 2 \\times 2 + 1 \\times 2 = 2 + 4 + 2 = 8$.",
                            "Numerator: $10 \\times 1 \\times 2 + 8 \\times 2 \\times 2 = 20 + 32 = 52$.",
                        ],
                    },
                ],
                "closing": r'''
Three things to take from that formula before it goes in the notebook.

**It is Millman's theorem.** Divide the top and the bottom of the full result by
$R_1R_2R_3$ and it turns into

$$v_A = \frac{\dfrac{V_1}{R_1} + \dfrac{V_2}{R_2}}{\dfrac{1}{R_1} + \dfrac{1}{R_2} + \dfrac{1}{R_3}}$$

which reads as plain English: each supply pushes in a current $V/R$ as though the node were
at ground, and the node settles at whatever voltage the total conductance needs to carry
that total current away. Written that way it extends to any number of branches by
inspection — one more term on top per supply, one more on the bottom per resistor — and the
grounded shunt $R_3$ is just the branch whose supply happens to be 0 V.

**The weights are the design.** Split the numbers out of the worked case and

$$v_A = 0.250\,V_1 + 0.500\,V_2$$

Node A follows the 8 V rail twice as strongly as the 10 V rail, purely because it reaches
the node through half the resistance. If $V_2$ were interference rather than signal, that
0.500 is the number to attack, and the formula says exactly how: raise $R_2$, or lower
$R_3$, both of which shrink it.

**Check the denominator against the last module.** $R_1R_2 + R_1R_3 + R_2R_3$ is the same
symmetric combination that came out of module 8's mesh derivation on a different circuit
with different unknowns. That is not a coincidence — it is $R_1R_2R_3$ divided by
$R_1 \parallel R_2 \parallel R_3$ — and that parallel combination is about to become the
most reused quantity in the course. The next module gives it a name: it is the Thévenin
resistance looking back into node A, and the numerator over the denominator is the Thévenin
voltage. Everything you just derived is one worked case of the theorem that comes next.
'''
            },
            "blanks": [
                {
                    "title": "Kill one, then the other",
                    "minutes": 9,
                    "caption": "the method, step by step, on a circuit with two rails",
                    "lang": "text",
                    "brief": r"""
A different pair of supplies from the ones in the reading, so the arithmetic is fresh:
6.00 V arrives at node A through 1.00 kΩ, 8.00 V arrives at the same node through 2.00 kΩ,
and 2.00 kΩ runs from A down to ground.

Everything below is in volts, kilohms and milliamps, which are consistent with one another.
Fill in what each step needs.
""",
                    "listing": """V1 = 6 V  ---[ R1 = 1k ]---+
                           |
V2 = 8 V  ---[ R2 = 2k ]---+--- node A ---[ R3 = 2k ]--- ground


step 1   kill V2: put ___ where it was.  R2 does not move.

         below A now:   R2 || R3   =  ___ kohm

         V1's share  =  6 * (that)/(1 + that)              =  ___ V


step 2   kill V1: a wire there too.  R1 does not move.

         below A now:   R1 || R3   =  2/3 kohm

         V2's share  =  8 * (2/3)/(2 + 2/3)                =  ___ V


step 3   both supplies live:      node A  =  ___ V
""",
                    "blanks": [
                        {
                            "prompt": "What goes in the place of a killed voltage source?",
                            "hole": "?",
                            "opts": ["an open circuit — leave the gap", "a wire", "a 2 kΩ resistor", "the same source, reversed"],
                            "a": 1,
                            "why": "A wire. A voltage source set to zero still insists its two terminals are at the "
                                   "same potential whatever current flows, and that is exactly what a short circuit "
                                   "does. Leaving a gap is how you kill a *current* source — it forces zero current "
                                   "instead of zero volts, which is a different constraint and a different circuit.",
                        },
                        {
                            "prompt": "With V2 shorted, R2 runs from A to ground alongside R3. What is the pair in parallel?",
                            "hole": "?",
                            "opts": ["4", "0.5", "1", "2"],
                            "a": 2,
                            "why": "$2 \\times 2/(2+2) = 1$ kΩ. Both resistors are 2 kΩ and both now run from node A to "
                                   "ground, so the pair is half of one of them. The figure 4 kΩ would be the two in "
                                   "series, which is what you would get if the current had to pass through both one "
                                   "after the other — it does not; it has a choice of two routes.",
                        },
                        {
                            "prompt": "So what does V1 contribute to node A?",
                            "hole": "?",
                            "opts": ["2.00", "3.00", "4.00", "6.00"],
                            "a": 1,
                            "why": "$6 \\times 1/(1+1) = 3.00$ V. With 1 kΩ on top and 1 kΩ underneath, the supply "
                                   "splits in half. The figure 4.00 V is what you get by deleting R2 along with its "
                                   "supply — that leaves 1 kΩ over 2 kΩ and two thirds of 6 V — and it is the single "
                                   "commonest error in this method.",
                        },
                        {
                            "prompt": "And what does V2 contribute?",
                            "hole": "?",
                            "opts": ["4.00", "2.67", "2.00", "1.33"],
                            "a": 2,
                            "why": "$8 \\times (2/3)/(8/3) = 8 \\times 0.25 = 2.00$ V. Note how little the larger supply "
                                   "manages: it has to come through 2 kΩ while the node is held down by an effective "
                                   "2/3 kΩ, so three quarters of it is lost on the way. The figure 4.00 V would be its "
                                   "share if R1 were not there at all.",
                        },
                        {
                            "prompt": "Both live, then. Where does node A sit?",
                            "hole": "?",
                            "opts": ["14.00", "5.00", "7.00", "3.50"],
                            "a": 1,
                            "why": "$3.00 + 2.00 = 5.00$ V, and the contributions simply add. Check it with KCL at A: "
                                   "$(5-6)/1 + (5-8)/2 + 5/2 = -1 - 1.5 + 2.5 = 0$. The figure 14.00 V is the two "
                                   "supplies added, which no node in this circuit could ever reach — a passive "
                                   "resistor network cannot produce a voltage larger than the largest source in it.",
                        },
                    ],
                },
                {
                    "title": "What scales with what",
                    "minutes": 9,
                    "caption": "linearity, applied without solving anything",
                    "lang": "text",
                    "brief": r"""
No circuit is drawn here on purpose, because you do not need one. A network of resistors is
driven by two **voltage** supplies, $E_1$ and $E_2$, and contains nothing else — no current
sources, no diodes, nothing that is not a resistor or one of those two supplies.

Three measurements have been taken as it stands. Each part below changes one thing and asks
what those measurements become. Every answer follows from linearity alone; none of them
requires knowing a single resistor value.
""",
                    "listing": """AS IT STANDS

    node A  =  6.00 V        R5 carries  1.50 mA        R5 dissipates  4.50 mW


1   both supplies doubled, every resistor left alone

        node A = ___ V          R5 carries ___ mA        R5 dissipates ___ mW


2   every resistance doubled, both supplies left alone

        node A = ___ V          R5 carries ___ mA


3   E1 doubled, E2 left exactly where it was

        node A = ___
""",
                    "blanks": [
                        {
                            "prompt": "Both supplies doubled: the node voltage.",
                            "hole": "?",
                            "opts": ["6.00", "24.00", "12.00", "3.00"],
                            "a": 2,
                            "why": "12.00 V. Every response is a weighted sum of the sources with weights made only of "
                                   "resistances, so scaling every source by two scales every voltage in the circuit by "
                                   "two. Nothing about which resistors are where enters into it.",
                        },
                        {
                            "prompt": "Both supplies doubled: the current in R5.",
                            "hole": "?",
                            "opts": ["3.00", "1.50", "6.00", "0.75"],
                            "a": 0,
                            "why": "3.00 mA. Currents are responses in exactly the same sense that voltages are — each "
                                   "is a weighted sum of the sources — so they scale by the same factor of two.",
                        },
                        {
                            "prompt": "Both supplies doubled: the power in R5.",
                            "hole": "?",
                            "opts": ["9.00", "4.50", "36.00", "18.00"],
                            "a": 3,
                            "why": "18.00 mW, four times as much. Power is a product of two things that each doubled, "
                                   "so it goes up by $2^2$. The figure 9.00 mW assumes power scales like the sources, "
                                   "which is the mistake this whole module is built around warning you about.",
                        },
                        {
                            "prompt": "Every resistance doubled instead: the node voltage.",
                            "hole": "?",
                            "opts": ["12.00", "6.00", "3.00", "1.50"],
                            "a": 1,
                            "why": "Still 6.00 V, unchanged. Doubling every resistance halves every conductance, so "
                                   "every nodal KCL equation is multiplied through by one half — and an equation "
                                   "multiplied by a constant has the same solution. The node voltages do not move. "
                                   "This is why a divider's output depends on the *ratio* of its resistors and not on "
                                   "their size.",
                        },
                        {
                            "prompt": "Every resistance doubled: the current in R5.",
                            "hole": "?",
                            "opts": ["0.75", "1.50", "3.00", "0.375"],
                            "a": 0,
                            "why": "0.75 mA, halved. The voltage across R5 is unchanged and its resistance has doubled, "
                                   "so Ohm's law halves the current. Every current in the circuit halves, and every "
                                   "power with it — which is the usual reason for scaling a divider up: same output "
                                   "voltage, less current wasted.",
                        },
                        {
                            "prompt": "Only E1 doubled, E2 untouched: the node voltage.",
                            "hole": "?",
                            "opts": [
                                "12.00 V",
                                "9.00 V",
                                "somewhere between 6.00 V and 12.00 V, but what is given does not fix it",
                                "still 6.00 V",
                            ],
                            "a": 2,
                            "why": "It cannot be pinned down. Node A is $a_1E_1 + a_2E_2 = 6.00$ V and doubling $E_1$ "
                                   "makes it $6.00 + a_1E_1$ — you have to know how much of the original 6.00 V was "
                                   "$E_1$'s doing, and that is precisely what the measurements do not say. The bounds "
                                   "are firm, though: a resistor network driven by one positive supply puts every node "
                                   "between ground and that supply, so both contributions are somewhere in $[0, 6.00]$ "
                                   "and the new value lands between 6.00 V and 12.00 V. Getting the exact figure needs "
                                   "one superposition solve, which is the entire reason the method exists.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One rule, one multiplication",
                    "minutes": 6,
                    "brief": r'''
A three-rung ladder on the bench, fed by an adjustable supply. Somebody has already
measured it once: with the supply set to **4.00 V**, the probe at the far end read
**1.00 V**.

The supply has since been turned up to the 30.0 V shown on the drawing, and nothing else
has been touched — same resistors, same wiring, same probe.

You could collapse the ladder from the far end and divide at every node. You do not have to.
''',
                    "prompt": "With the supply on 30.0 V, what does the probe read?",
                    "note": "In volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 30},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 8, "y": 7, "rot": 1, "value": 5000},
                            {"id": "g1", "kind": "GND", "x": 8, "y": 10},
                            {"id": "r3", "kind": "R", "x": 11, "y": 4, "value": 1000},
                            {"id": "r4", "kind": "R", "x": 13, "y": 7, "rot": 1, "value": 3000},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 10},
                            {"id": "r5", "kind": "R", "x": 16, "y": 4, "value": 1000},
                            {"id": "r6", "kind": "R", "x": 18, "y": 7, "rot": 1, "value": 2000},
                            {"id": "g3", "kind": "GND", "x": 18, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 20, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [8, 4]},
                            {"a": [8, 4], "b": [8, 6]},
                            {"a": [8, 8], "b": [8, 10]},
                            {"a": [8, 4], "b": [10, 4]},
                            {"a": [12, 4], "b": [13, 4]},
                            {"a": [13, 4], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [17, 4], "b": [18, 4]},
                            {"a": [18, 4], "b": [18, 6]},
                            {"a": [18, 8], "b": [18, 10]},
                            {"a": [18, 4], "b": [20, 4]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, as drawn", "value": "30.0 V"},
                        {"label": "Series resistors, in order", "value": "1.00 kΩ, 1.00 kΩ, 1.00 kΩ"},
                        {"label": "Shunts, in order", "value": "5.00 kΩ, 3.00 kΩ, 2.00 kΩ"},
                        {"label": "Measured earlier", "value": "1.00 V at the probe, supply on 4.00 V"},
                    ],
                    "aside": "One source, and nothing but resistors besides. Every voltage in a circuit "
                             "like that is proportional to the source, so one measurement fixes the whole "
                             "ladder for every setting the supply can reach.",
                    "answer": 7.5,
                    "tol": 0.02,
                    "unit": "V",
                    # Nothing is restated from the prompt: the schematic carries the 30 V setting and
                    # the check simply reads the probe, so an edited supply value or an edited resistor
                    # would move this number and the gate would catch it.
                    "check": "return c.vout();",
                    "hint": "The supply went up by a factor of 30.0/4.00. Nothing else changed, so every "
                            "voltage and every current in the ladder went up by that same factor.",
                    "wrong": "If you got 1.00, that is the reading at the old setting rather than the new "
                             "one. If you got 4.50, that is what this ladder gives at 18.0 V, which is the "
                             "setting worked through in the reading and not the one on the drawing. If you "
                             "got 3.75, that is the current in milliamps in the last shunt rather than the "
                             "voltage across it.",
                    "why": r'''
The supply is 7.5 times what it was, so every voltage in the circuit is 7.5 times what it
was, and $1.00 \times 7.5 = 7.50$ V. That is the whole answer, and it took one
multiplication because the circuit contains one source and nothing but resistors.

If you want the reading confirmed from the resistor values alone, the cheap route is to
*assume* the output and work inwards. Take the far node to be 1.000 V and see what supply
that needs:

```
    the 2k shunt carries      1.000/2       =  0.500 mA
    the 1k in front carries the same, dropping           0.500 V
    middle node               1.000 + 0.500 =  1.500 V

    the 3k shunt carries      1.500/3       =  0.500 mA
    the 1k in front carries   0.500 + 0.500 =  1.000 mA, dropping  1.000 V
    first node                1.500 + 1.000 =  2.500 V

    the 5k shunt carries      2.500/5       =  0.500 mA
    the 1k at the top carries 1.000 + 0.500 =  1.500 mA, dropping  1.500 V
    supply                    2.500 + 1.500 =  4.000 V
```

So 4.000 V in gives 1.000 V out, which agrees with the measurement that was handed to you,
and the ladder's weight on its source is $1/4$. At 30.0 V the probe reads
$30.0/4 = 7.50$ V, the supply delivers $1.500 \times 7.5 = 11.25$ mA, and each of the three
shunts carries $0.500 \times 7.5 = 3.75$ mA. Check the last of those directly: 7.50 V across
2.00 kΩ is 3.75 mA, which it is.

Every line of that walk was one Ohm's law or one addition at a node, and nothing was ever
unknown — which is the advantage of working inwards from an assumed answer. Collapsing the
ladder forwards gets the same 7.50 V; it just needs three parallel combinations and three
divisions to do it, and the fractions are less kind.
''',
                },
                {
                    "title": "One source's share of the answer",
                    "minutes": 8,
                    "brief": r"""
    The circuit this comes from has two supplies in it, 10 V on the left and 8 V on the
    right, and with both of them live the probed node sits at 6.50 V. The question is not
    what that node does — it is how much of the 6.50 V each supply is responsible for.

    So the 8 V supply has been killed the way superposition requires, and the result is
    the schematic below. Look at what did **not** leave with it: the 1 kΩ that used to
    feed the node from the right is still there, still soldered to the node, now running
    to ground instead of to a supply. What the probe reads on this circuit is the 10 V
    supply's share of the 6.50 V.
    """,
                    "prompt": "With the 8 V supply replaced by a wire, what does the probe read?",
                    "note": "Two decimal places. The killed supply's 1 kΩ is still in the circuit.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 4, "value": 2000},
                            {"id": "r3", "kind": "R", "x": 9, "y": 8, "rot": 1, "value": 2000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 5},
                            {"id": "r2", "kind": "R", "x": 14, "y": 4, "value": 1000},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 8},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [7, 4]},
                            {"a": [9, 4], "b": [9, 7]},
                            {"a": [9, 9], "b": [9, 10]},
                            {"a": [9, 5], "b": [11, 5]},
                            {"a": [9, 4], "b": [13, 4]},
                            {"a": [15, 4], "b": [17, 4]},
                            # the wire that replaced the 8 V supply: its 1 kΩ now ends at ground
                            {"a": [17, 4], "b": [17, 8]},
                        ],
                    },
                    "given": [
                        {"label": "Left supply", "value": "10.00 V through 2.00 kΩ"},
                        {"label": "Right branch", "value": "1.00 kΩ, its 8 V supply killed"},
                        {"label": "Shunt to ground", "value": "2.00 kΩ"},
                        {"label": "Probe reads with both supplies live", "value": "6.50 V"},
                    ],
                    "aside": "Killing the right-hand supply leaves its 1 kΩ running from the "
                             "probed node to ground, where it sits in parallel with the 2 kΩ that "
                             "was already there.",
                    "answer": 2.5,
                    "tol": 0.02,
                    "unit": "V",
                    # The drawn circuit IS the one the question is about — the 8 V supply is
                    # already a wire — so the reading asked for is just the probed node.
                    "check": "return c.vout();",
                    "hint": "The circuit in front of you is an ordinary divider: 2 kΩ on top, and "
                            "1 kΩ in parallel with 2 kΩ below.",
                    "wrong": "If you got 5 V, you have treated the 1 kΩ as gone rather than "
                             "grounded — that is the divider you get when the whole branch is "
                             "deleted, and it is the commonest superposition mistake there is. If "
                             "you got 6.50 V, that is the reading with both supplies live, which "
                             "is the total this contribution is one part of.",
                    "why": "$1\\text{k}\\parallel2\\text{k} = 667$ Ω, so the probe reads "
                           "$10 \\times 667/(2000+667) = 2.50$ V. Repeating the exercise with the "
                           "10 V supply killed instead — a wire in its place, its 2 kΩ left "
                           "running from the node to ground — gives "
                           "$2\\text{k}\\parallel2\\text{k} = 1$ "
                           "kΩ and $8 \\times 1000/2000 = 4.00$ V, and $2.50 + 4.00$ is the 6.50 V "
                           "the probe reads with both of them alive. Note which supply dominates: "
                           "the 8 V one is "
                           "the smaller source but reaches the node through the smaller resistance, "
                           "and that is what decides the split.",
                },
                {
                    "title": "The branch you were tempted to delete",
                    "minutes": 10,
                    "brief": r'''
An 18.0 V rail reaches node A through 3.00 kΩ. From A, 6.00 kΩ runs down to ground. Also
hanging on A is a chip that draws a constant 3.00 mA whatever the node does. With all of
that live, node A sits at 6.00 V.

The drawing shows the same circuit with the **18 V supply killed** — a wire where it was —
so the 3.00 kΩ, which has gone nowhere, now runs from node A straight to ground. What is
left is the chip's own contribution, and the question is about the resistor most people
would have deleted.
''',
                    "prompt": "In the circuit as drawn, how much current does the 3.00 kΩ carry?",
                    "note": "In milliamps, to two decimal places. Give the size; the direction is worth "
                            "thinking about and is discussed afterwards.",
                    "diagram": {
                        "parts": [
                            {"id": "r1", "kind": "R", "x": 5, "y": 6, "rot": 1, "value": 3000},
                            {"id": "g0", "kind": "GND", "x": 5, "y": 9},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "i1", "kind": "I", "x": 13, "y": 6, "rot": 1, "value": 0.003},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 9},
                        ],
                        "wires": [
                            # the top rail IS node A; the 18 V supply used to sit at the left of it
                            {"a": [5, 5], "b": [13, 5]},
                            {"a": [5, 7], "b": [5, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [13, 7], "b": [13, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Rail (killed here)", "value": "18.0 V"},
                        {"label": "R1, rail to node A", "value": "3.00 kΩ"},
                        {"label": "R2, node A to ground", "value": "6.00 kΩ"},
                        {"label": "Chip on node A", "value": "3.00 mA, constant"},
                        {"label": "Node A with everything live", "value": "6.00 V"},
                    ],
                    "aside": "With the supply shorted, the 3 kΩ and the 6 kΩ are simply two resistors in "
                             "parallel across the current source. Find what the node does first, then use "
                             "Ohm's law on the branch you were asked about.",
                    "answer": 2.0,
                    "tol": 0.02,
                    "unit": "mA",
                    # The quantity asked for is a branch current, not a node voltage, so the check
                    # solves the circuit and applies Ohm's law to the resistor by its id, reading both
                    # its value and its two node numbers off the netlist rather than restating them.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r1'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1000;
''',
                    "hint": "The two resistors are in parallel: $3 \\parallel 6 = 2.00$ kΩ. The chip pulls "
                            "3.00 mA out of the node through that, so start by working out what the node "
                            "sits at — it will not be a positive number.",
                    "wrong": "If you got 3.00 mA, that is the whole of the chip's current, which the 3 kΩ "
                             "would only carry if the 6 kΩ were not in the circuit. If you got 1.00 mA you "
                             "have the split the wrong way round — of two parallel resistors the *smaller* "
                             "takes the larger share. If you got 4.00, that is what the same resistor "
                             "carries with the supply live as well, which is the total this contribution "
                             "is one half of. If you got 6.00, that is a voltage rather than a current.",
                    "why": r'''
```
    with the supply shorted, both resistors run from A to ground

    R1 || R2      =  3*6/(3+6)          =  2.00 kohm
    node A        = -3.00 mA * 2.00 k   = -6.00 V
    in the 3 kohm =  6.00/3.00          =  2.00 mA
```

or straight from the current-divider rule, since 3.00 mA arrives at a junction of 3 kΩ and
6 kΩ: the 3 kΩ takes the fraction $6/(6+3) = 2/3$ of it, which is 2.00 mA. The 6 kΩ takes
the remaining 1.00 mA, and $2.00 + 1.00 = 3.00$ closes.

**Which way is it going?** Node A is at $-6.00$ V, below ground, so current flows *from*
ground *up* through the 3 kΩ *into* node A. In this sub-circuit the killed supply's resistor
is feeding the node rather than draining it, which is exactly the behaviour you would lose
by deleting it.

Now put the piece back where it belongs. Superposition applies to currents as well as
voltages, so take the current in that 3 kΩ as positive when it flows from the rail end
towards node A:

```
    chip killed (open), supply live:   node A = 18.0 * 6/(3+6)  =  12.00 V
                                       current = (18.0 - 12.0)/3 =   2.00 mA

    supply killed (this drawing):      current = (0 - (-6.00))/3 =   2.00 mA

    both live:                         2.00 + 2.00               =   4.00 mA
    check directly:  (18.0 - 6.00)/3.00                          =   4.00 mA
```

And the node itself: $12.00 + (-6.00) = 6.00$ V, the figure you were given. Two
contributions, one of them negative, and both of them larger in size than parts of the
total — which is normal, and is why a contribution is not a share in the everyday sense of
the word.
''',
                },
                {
                    "title": "How much heat in the 1 kΩ?",
                    "minutes": 11,
                    "brief": r'''
The two-supply circuit again, both of them live this time: 10.0 V arrives at the probed
node through 2.00 kΩ, 8.00 V arrives at the same node through 1.00 kΩ, and 2.00 kΩ runs
from the node to ground. The probe reads 6.50 V, of which 2.50 V is the 10 V supply's doing
and 4.00 V is the 8 V supply's.

The question is about the 1.00 kΩ — the resistor the 8 V supply comes through — and it is a
question about power, so be careful. The two contributions you already have are voltages.
''',
                    "prompt": "What power does the 1.00 kΩ dissipate?",
                    "note": "In milliwatts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 4, "value": 2000},
                            {"id": "r3", "kind": "R", "x": 9, "y": 8, "rot": 1, "value": 2000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 5},
                            {"id": "r2", "kind": "R", "x": 14, "y": 4, "value": 1000},
                            {"id": "v2", "kind": "V", "x": 18, "y": 7, "rot": 1, "value": 8},
                            {"id": "g2", "kind": "GND", "x": 18, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [7, 4]},
                            {"a": [9, 4], "b": [9, 7]},
                            {"a": [9, 9], "b": [9, 10]},
                            {"a": [9, 5], "b": [11, 5]},
                            {"a": [9, 4], "b": [13, 4]},
                            {"a": [15, 4], "b": [18, 4]},
                            {"a": [18, 4], "b": [18, 6]},
                            {"a": [18, 8], "b": [18, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Left supply", "value": "10.0 V through 2.00 kΩ"},
                        {"label": "Right supply", "value": "8.00 V through 1.00 kΩ"},
                        {"label": "Shunt to ground", "value": "2.00 kΩ"},
                        {"label": "Probe reads", "value": "6.50 V"},
                        {"label": "Its two contributions", "value": "2.50 V and 4.00 V"},
                    ],
                    "aside": "Superpose voltages, then square. Never square, then superpose — the two "
                             "give different answers here by a factor of nearly ten, and only one of them "
                             "is what the resistor gets warm by.",
                    "answer": 2.25,
                    "tol": 0.03,
                    "unit": "mW",
                    # The power is computed from the solved node voltages and the resistor's own value,
                    # so nothing here restates a number the prompt or the drawing already carries.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r2'; })[0];
const v = d.v[r.n1] - d.v[r.n2];
return v * v / r.value * 1000;
''',
                    "hint": "The node is at 6.50 V and the far end of that resistor is held at 8.00 V, so "
                            "there is 1.50 V across it. One resistor, one voltage, one value: $P = V^2/R$.",
                    "wrong": "If you got 22.25 mW, you have found each supply's power in that resistor and "
                             "added the two — which is exactly the thing superposition cannot do, and it "
                             "overstates the answer by a factor of nearly ten here. If you got 42.25 mW, "
                             "you have used the node's own 6.50 V rather than the voltage across the "
                             "resistor — that is the voltage from the node to ground, and neither end of "
                             "this resistor is at ground. If you got 1.50, that is the current through it "
                             "in milliamps, one step short of the answer.",
                    "why": r'''
```
    voltage across the 1 kohm  =  8.00 - 6.50   =  1.50 V
    power                      =  1.50^2/1.00k  =  2.25 mW
```

Now watch what happens if the two contributions are handled as powers instead. Measure the
voltage across that resistor from the node end to the supply end, and superpose:

```
    10 V supply alone (8 V shorted):   node 2.50 V, far end 0        v =  +2.50 V
     8 V supply alone (10 V shorted):  node 4.00 V, far end 8.00     v =  -4.00 V
                                       sum                           v =  -1.50 V   correct

    but as powers:   2.50^2/1k  =   6.25 mW
                     4.00^2/1k  =  16.00 mW
                     added      =  22.25 mW     <- ten times too big
```

The missing piece is the cross term. Squaring a sum gives
$(v_1+v_2)^2 = v_1^2 + v_2^2 + 2v_1v_2$, and here

$$\frac{2 v_1 v_2}{R} = \frac{2 \times 2.50 \times (-4.00)}{1000} = -20.0 \text{ mW}$$

so $22.25 - 20.00 = 2.25$ mW, which is the right answer arrived at the long way round. The
two contributions oppose each other across this resistor — one pushes current towards the
node, the other away — and almost cancel, which is why the true dissipation is so much
smaller than either would produce alone.

There is no version of this that works. Superposition is a statement about a *linear* map
from sources to responses, and squaring is not linear. Add the volts, add the amps, and
compute watts exactly once, at the end, from the totals.

For completeness, the rest of the circuit's budget at 6.50 V:

```
    in the 2 kohm from the 10 V rail:  (10.0-6.50)/2  =  1.75 mA,  P = 6.13 mW
    in the 1 kohm from the  8 V rail:  (8.00-6.50)/1  =  1.50 mA,  P = 2.25 mW
    in the 2 kohm shunt:                6.50/2        =  3.25 mA,  P = 21.1 mW
    KCL:  1.75 + 1.50  =  3.25                                         closes
    supplied:  10.0*1.75 + 8.00*1.50  =  17.5 + 12.0  =  29.5 mW
    dissipated: 6.13 + 2.25 + 21.1                    =  29.5 mW       closes
```
''',
                },
                {
                    "title": "The load comes on: what must the supply give?",
                    "minutes": 14,
                    "brief": r'''
A 20.0 V supply feeds node A through 2.00 kΩ. From A, 2.00 kΩ runs to ground and another
2.00 kΩ runs across to node B, where the probe sits; from B, 2.00 kΩ runs to ground.

With nothing else connected, that network is easy: node A sits at 8.00 V, node B at 4.00 V,
and the supply delivers 6.00 mA.

Now a chip is switched on at node B, drawing a constant 2.50 mA. The chip does not care what
node B does, and node B is about to move a long way.
''',
                    "prompt": "With the 2.50 mA load running, what current does the 20.0 V supply deliver?",
                    "note": "In milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 20},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 7, "y": 4, "value": 2000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 7, "rot": 1, "value": 2000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 10},
                            {"id": "r3", "kind": "R", "x": 13, "y": 4, "value": 2000},
                            {"id": "r4", "kind": "R", "x": 16, "y": 7, "rot": 1, "value": 2000},
                            {"id": "g2", "kind": "GND", "x": 16, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 18, "y": 4},
                            {"id": "i1", "kind": "I", "x": 20, "y": 7, "rot": 1, "value": 0.0025},
                            {"id": "g3", "kind": "GND", "x": 20, "y": 10},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [6, 4]},
                            {"a": [8, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 6]},
                            {"a": [9, 8], "b": [9, 10]},
                            {"a": [9, 4], "b": [12, 4]},
                            {"a": [14, 4], "b": [16, 4]},
                            {"a": [16, 4], "b": [16, 6]},
                            {"a": [16, 8], "b": [16, 10]},
                            {"a": [16, 4], "b": [20, 4]},
                            {"a": [20, 4], "b": [20, 6]},
                            {"a": [20, 8], "b": [20, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "20.0 V"},
                        {"label": "Every resistor", "value": "2.00 kΩ"},
                        {"label": "Load at node B", "value": "2.50 mA, constant"},
                        {"label": "With the load off", "value": "A at 8.00 V, B at 4.00 V, supply 6.00 mA"},
                    ],
                    "aside": "Two unknown nodes and two sources of different kinds. Superposition splits it "
                             "into two easy circuits: the supply alone is the network you already have the "
                             "answer to, and the load alone sees nothing but resistors.",
                    "answer": 6.5,
                    "tol": 0.03,
                    "unit": "mA",
                    # The quantity asked for is the current in the source itself, which the solver carries
                    # as an unknown of its own. The source is found by kind rather than by name so that
                    # the check does not depend on the id in the drawing.
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
return Math.abs(d.currents[src.id]) * 1000;
''',
                    "hint": "The supply's contribution is the 6.00 mA you were given. For the load's "
                            "contribution, short the supply: node A then has 2 kΩ and 2 kΩ both running to "
                            "ground, which is 1.00 kΩ, with the rest of the ladder hanging off it.",
                    "wrong": "If you got 8.50 mA you have added the whole of the load current to the "
                             "supply's 6.00 mA, as though every milliamp the chip takes has to come from "
                             "the supply — most of it comes from the two shunts instead, which sag. If you "
                             "got 6.00 mA that is the reading with the load off. If you got 3.50 mA you "
                             "have subtracted rather than added, and a load can only ever increase what a "
                             "supply gives.",
                    "why": r'''
Superposition, with the two sources taken one at a time.

```
SUPPLY ALONE   (load removed, leaving the gap)

    B end of the ladder:  2k + 2k = 4k,  in parallel with the 2k at A  =  1.333 k
    node A  =  20.0 * 1.333/(2.00 + 1.333)   =   8.00 V
    node B  =   8.00 * 2/(2+2)               =   4.00 V
    supply current  =  (20.0 - 8.00)/2.00    =   6.00 mA        <- as given

LOAD ALONE     (supply replaced by a wire; all four resistors stay)

    at node A the 2k to the supply and the 2k to ground are now in parallel:  1.00 k
    looking from B:   2.00 (its own shunt)  ||  (2.00 across + 1.00)  =  2*3/5 = 1.20 k
    node B  =  -2.50 mA * 1.20 k             =  -3.00 V
    node A  =  -3.00 * 1.00/(2.00 + 1.00)    =  -1.00 V
    current the supply branch carries, from the wire end towards A:
              (0 - (-1.00))/2.00             =   0.50 mA

BOTH

    supply current  =  6.00 + 0.50           =   6.50 mA
    node A  =  8.00 - 1.00  =  7.00 V        node B  =  4.00 - 3.00  =  1.00 V
```

Check it without superposition, straight from the two node voltages: $(20.0 - 7.00)/2.00 =
6.50$ mA, and KCL at B reads $(1.00-7.00)/2 + 1.00/2 + 2.50 = -3.00 + 0.50 + 2.50 = 0$.

The number worth keeping is the 0.50 mA. A chip drawing 2.50 mA made the supply give only
0.50 mA more — the other 2.00 mA was released by the two shunt resistors as the nodes fell:
the 2 kΩ at A went from 4.00 mA to 3.50 mA, and the 2 kΩ at B from 2.00 mA down to 0.50 mA,
which is 2.00 mA between them. The load did not so much draw current from the supply as
divert current that was already circulating.

And notice what it cost. Node B fell from 4.00 V to 1.00 V — a 75% collapse for a load of
two and a half milliamps — which is the same lesson module 4 taught about weak dividers,
arrived at from the other direction. If node B were supposed to be a 4 V reference, this
circuit does not work, and superposition has told you both that and by how much.
''',
                },
            ],
            "build": {
                "title": "Take the circuit apart: one source's contribution",
                "minutes": 24,
                "brief": r'''
The canvas opens with a finished circuit: a 12 V supply through 1 kΩ and a 3 V supply
through another 1 kΩ, meeting at node A, with a third 1 kΩ from A down to ground. The
probe reads 5.00 V, and one line of nodal analysis confirms it.

Take it apart. Redraw it as the circuit that produces **the 12 V supply's contribution
alone**, with the 3 V supply killed, so that the probe then reads **4.00 V**.

## What killing it means, exactly

Replace the 3 V supply with a piece of wire. A source of zero volts holds its two
terminals at the same potential, and a wire is the component that does that.

The thing not to do is delete the branch. That 1 kΩ is still soldered to the board and
still connected to node A; it simply now runs to ground instead of to a supply. Leave
it in and the probe reads 4 V. Take it out and you get 6 V, which is the correct answer
to a different question.

If you then repeat the exercise with the 12 V supply killed instead, you will find
1.00 V — and $4 + 1 = 5$, which is the reading you started from.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "value": 1000},
                        {"id": "p3", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 6},
                        {"id": "p6", "kind": "R", "x": 14, "y": 5, "value": 1000},
                        {"id": "p7", "kind": "V", "x": 17, "y": 6, "rot": 1, "value": 3},
                        {"id": "p8", "kind": "GND", "x": 17, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [9, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [9, 6], "b": [11, 6]},
                        {"a": [9, 5], "b": [13, 5]},
                        {"a": [15, 5], "b": [17, 5]},
                        {"a": [17, 7], "b": [17, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "value": 1000},
                        {"id": "p3", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 6},
                        {"id": "p6", "kind": "R", "x": 14, "y": 5, "value": 1000},
                        {"id": "p8", "kind": "GND", "x": 17, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [9, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [9, 6], "b": [11, 6]},
                        {"a": [9, 5], "b": [13, 5]},
                        {"a": [15, 5], "b": [17, 5]},
                        {"a": [17, 5], "b": [17, 9]},
                    ],
                },
                "checks": [
                    {"name": "only the 12 V supply is left alive", "code": r'''
c.assert(c.count('V') === 1,
  'One source at a time is the whole method: this circuit should contain exactly one ' +
  'voltage source, and it found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.002, 'the surviving supply');
'''},
                    {"name": "all three 1 kΩ resistors are still in the circuit", "code": r'''
const rs = c.values('R');
c.assert(rs.length === 3,
  'Killing a source does not remove its resistor. Three 1 kΩ resistors should remain; ' +
  'found ' + rs.length + '.');
rs.forEach(function (r) {
  c.assert(Math.abs(r - 1000) <= 10, 'Every resistor here is 1 kΩ — found one of ' + c.fmt(r, 'Ω') + '.');
});
'''},
                    {"name": "the killed branch now runs from node A to ground", "code": r'''
const out = c.outNode();
const toGround = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(toGround.length === 2,
  'With the 3 V supply replaced by a wire, two resistors should run from the probed ' +
  'node down to ground — its own and the original one. Found ' + toGround.length + '.');
'''},
                    {"name": "the probe reads 4.00 V", "code": r'''
c.close(c.vout(), 4.0, 0.01,
  'the 12 V supply’s contribution — 12 V across 1 kΩ in series with two 1 kΩ in parallel');
'''},
                    {"name": "and the supply is delivering 8 mA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
c.close(Math.abs(cur[ids[0]]), 0.008, 0.02,
  'the supply current — (12 - 4) V across the 1 kΩ feeding node A');
'''},
                ],
                "hints": [
                    "Delete the 3 V source symbol, then draw a wire from where its + terminal was down to a ground symbol. The 1 kΩ that fed it stays exactly where it is.",
                    "The circuit that is left is a divider: 1 kΩ on top, and two 1 kΩ in parallel (500 Ω) below.",
                    "$12 \\times 500/(1000+500) = 4$ V, and the current is $12/1500 = 8$ mA.",
                    "If the probe reads 6 V you have removed the resistor along with the source, which leaves a two-resistor divider instead of a three-resistor one.",
                ],
            },
            "quiz": {
                "title": "One source at a time",
                "minutes": 8,
                "questions": [
                    {
                        "q": "To find one source's contribution, what do you do with a 5 V supply elsewhere in the circuit?",
                        "opts": [
                            "remove it and leave the gap open",
                            "replace it with a wire",
                            "leave it at 5 V but ignore its current",
                            "replace it with a resistor equal to the load",
                        ],
                        "a": 1,
                        "why": r'''
Replace it with a wire. Killing a voltage source means setting it to zero volts, and a
component with zero volts across it whatever the current is precisely a short circuit.
Leaving a gap where it was would be killing it in the wrong way — that forces zero
*current* through the branch, which is what you do to a current source, and it gives a
different and wrong circuit.
''',
                    },
                    {
                        "q": "And what do you do with a current source you are killing?",
                        "opts": [
                            "replace it with a wire",
                            "replace it with a resistor of the same value in ohms",
                            "remove it, leaving the branch open",
                            "reverse it",
                        ],
                        "a": 2,
                        "why": r'''
Take it out and leave the gap. Zero amps through a branch, whatever voltage appears
across it, is exactly what an open circuit does. The two rules are duals of each other
and it is worth learning them as a pair: a dead voltage source is a wire, a dead
current source is a gap. Getting them the wrong way round is the classic error, and it
produces answers that are not merely inaccurate but unrelated.
''',
                    },
                    {
                        "q": "One source alone puts 3 V across a 1 kΩ resistor; a second alone puts 3 V across the same resistor. With both live, what power does that resistor dissipate?",
                        "opts": ["9 mW", "18 mW", "36 mW", "4.5 mW"],
                        "a": 2,
                        "why": r'''
The voltages superpose to 6 V, so the power is $6^2/1000 = 36$ mW — four times the
9 mW that either source produced alone, not twice. Power is a square, and squares do
not superpose. Add the voltages first and square afterwards, never the other way round:
this is the one place where the method genuinely does not apply, and it catches people
who have been using it successfully for an hour.
''',
                    },
                    {
                        "q": "A node is fed by a 12 V supply and a 3 V supply. The 12 V alone puts 4 V on it and the 3 V alone puts 1 V on it. What does the node sit at with both connected?",
                        "opts": ["5 V", "15 V", "4 V", "3 V"],
                        "a": 0,
                        "why": r'''
5 V — the contributions simply add, which is the whole content of superposition. The
answer is not 15 V: neither supply produces anything like its own voltage at the node,
because in each case the other supply's resistor is still in the circuit acting as a
load. And notice the node ends up above the 3 V supply, so in the complete circuit that
supply is absorbing current rather than delivering it, even though its contribution to
the node voltage is a positive 1 V.
''',
                    },
                    {
                        "q": "Every source in a resistive circuit is doubled. What happens to the node voltages?",
                        "opts": [
                            "they all double",
                            "they are unchanged",
                            "they all quadruple",
                            "it depends on the resistor values",
                        ],
                        "a": 0,
                        "why": r'''
Every one of them doubles, and every branch current does too. That is what linearity
means: each response is a weighted sum of the sources, so scaling all the sources
scales every response by the same factor, whatever the resistors happen to be. The
powers, being squares, go up fourfold. Doubling every *resistance* instead would leave
the voltages exactly where they are and halve every current, which is a different and
equally useful piece of scaling to have at hand.
''',
                    },
                ],
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "Thévenin, Norton and the matched load",
            "summary": "Any two terminals, whatever is behind them, behave like one source and one resistor. Finding those two numbers is the most reused trick in the subject.",
            "concepts": [
                "Any network of resistors and fixed sources, however large, looked at from two terminals behaves exactly like a single voltage source $V_{Th}$ in series with a single resistance $R_{Th}$. No measurement made at those terminals can tell the difference.",
                "$V_{Th}$ is the open-circuit voltage — what a perfect voltmeter reads with nothing else connected.",
                "$R_{Th}$ is the resistance looking in with every source killed: voltage sources shorted, current sources opened. On a bench, where you cannot reach inside, it is $V_{oc}/I_{sc}$ instead, and the two definitions always agree.",
                "The Norton form is the same fact stated the other way round: a current source $I_N = V_{Th}/R_{Th}$ in parallel with the same $R_{Th}$. Source transformation converts between them in one step.",
                "The payoff is that any load becomes one divider: $V_L = V_{Th}R_L/(R_{Th}+R_L)$. One hard calculation is done once, and every load question afterwards is a line of arithmetic.",
                "A load takes the most power when $R_L = R_{Th}$, and at that point exactly half of what leaves the source is burnt inside it. Maximum power and maximum efficiency are different targets and they disagree.",
            ],
            "read": [
                {
                    "title": "Whatever is in the box, it is one source and one resistor",
                    "minutes": 15,
                    "body": r'''
On the bench in front of you is a sealed metal box with two terminals on the front and
nothing else. Inside it might be a battery and a resistor. It might be four supplies,
eleven resistors and two current sources wired into something nobody can draw from
memory. You are not allowed to open it, and you are about to be asked what it will do
with a load you have not chosen yet.

That sounds like an impossible position, and it is the ordinary one. Every output of
every circuit you will ever meet is a pair of terminals with something complicated
behind it — a sensor bridge, a divider on a board, the output of a regulator, the pins
of a chip. What this module says is that the complication does not matter. From the
terminals, every one of those boxes is a battery and a resistor, and finding *which*
battery and *which* resistor is two calculations you do once.

## Measure it, and the answer arrives on its own

You have a stock of load resistors and a meter. Hang a load on the box, note the current
$I$ that flows out of the top terminal and the voltage $V$ across it, and repeat with a
different load. Plot $V$ against $I$.

The plot is a straight line, sloping down. It was a straight line in module 6 for a
torch cell, and here — with a box full of unknown circuitry rather than a lump of
chemistry — it is still a straight line. A straight line has an intercept and a slope,
which is two numbers, and two numbers is all the terminals will ever give you. The
intercept has units of volts. The slope has units of volts per amp, which is ohms.

So the model is not a simplification of the box. It is a complete account of everything
the box can do at those two terminals, and there is nothing else to know.

## Why the line is straight

Module 9 did the hard part of this already. A network of resistors and fixed sources is
linear: every voltage and every current in it is a weighted sum of the source values,
with weights made only of resistances.

Take the box with some load on it, drawing a current $I$ with $V$ across the terminals.
Now do something that looks like a cheat and is not: throw the load away and replace it
with an ideal current source set to exactly the $I$ it was carrying. Nothing inside the
box can tell. Every component still has the same voltage across it and the same current
through it as it had a moment ago, so every equation still balances. A branch may be
replaced by a source that imposes the values that branch already had.

The box now contains its own sources plus one test source, all linear, so superposition
applies. Take the two contributions to the terminal voltage in turn.

**The internal sources alone**, with the test source dead. A dead current source is an
open circuit, so this is the box with nothing connected, and the terminal voltage is
whatever the box produces open-circuit. Call it $V_{oc}$.

**The test source alone**, with every internal source dead — voltage sources shorted,
current sources opened. All that is left inside is resistance, some single equivalent
value; call it $R_{Th}$. The test source is pulling $I$ out of the top terminal and back
in at the bottom, so it drives $I$ up through that resistance from the bottom terminal to
the top, and the top terminal sits *below* the bottom one by $IR_{Th}$. This contribution
is $-IR_{Th}$.

Add them:

$$V = V_{oc} - I R_{Th}$$

That is the equation of the straight line, derived rather than measured, and it is also
the equation of an ideal source $V_{oc}$ with a resistor $R_{Th}$ in series. There was no
step in the argument that cared what was in the box. That is **Thévenin's theorem**, and
the surprising part is not the result but how little it took.

The two numbers get the names $V_{Th}$ — identical to $V_{oc}$, and the two are used
interchangeably — and $R_{Th}$.

## The recipe

1. **Decide which two terminals.** The equivalent is of the network *as seen from a
   chosen pair of points*, and moving them changes both numbers. Usually the choice is
   made for you: cut the load out and look back at the two ends you have just exposed.
2. **Find $V_{Th}$.** The voltage across those terminals with the load removed. Nothing
   is connected, so no current flows in whatever chain of parts leads out to them — which
   is often the step that makes an awkward network easy.
3. **Find $R_{Th}$.** Kill every independent source — a voltage source becomes a wire, a
   current source becomes a gap — leave every resistor exactly where it is, and work out
   the resistance between the two terminals with series and parallel combining.
4. **Put the load back**, on the equivalent rather than on the original. It is now one
   divider: $V_L = V_{Th}R_L/(R_{Th}+R_L)$.

The payoff is in the last line. Steps 2 and 3 are done once. Every question about every
load afterwards is a single division.

## Worked: a divider with a resistor on the way out

A 20.0 V rail feeds $R_1 = 5.00$ kΩ down to node A, and $R_2 = 20.0$ kΩ carries on from A
to ground. From A, a further $R_3 = 2.00$ kΩ runs out to the terminals where loads get
connected.

```text
STEP 2 - the open-circuit voltage

  with nothing connected, R3 carries no current at all, so it drops
  nothing, and the terminals sit at whatever node A sits at

    V(A)   =  20.0 * 20.0/(5.00 + 20.0)      =  16.0 V
    V(Th)  =  16.0 V                            R3 drops zero

STEP 3 - the resistance looking in

  kill the 20 V supply: it becomes a wire, so the top of R1 is now
  grounded and R1 runs from A to ground, right beside R2

    R1 || R2  =  (5.00 * 20.0)/(5.00 + 20.0)  =  4.00 kohm
    R(Th)     =  4.00 + 2.00                  =  6.00 kohm
                                                 R3 is in series with that
```

The box is 16.0 V behind 6.00 kΩ. Now the loads, each one line:

```text
    R(L) = 2.00 kohm:  V(L) = 16.0 * 2/(6+2)   =  4.00 V   I = 2.000 mA
    R(L) = 6.00 kohm:  V(L) = 16.0 * 6/(6+6)   =  8.00 V   I = 1.333 mA
    R(L) = 18.0 kohm:  V(L) = 16.0 * 18/(6+18) =  12.0 V   I = 0.667 mA
```

Worth checking one of those the long way, because the whole claim is that the two routes
agree. With the 2.00 kΩ load fitted, $R_3$ and the load are in series — 4.00 kΩ — and
that pair hangs beside $R_2$:

```text
    below A:  20.0 || 4.00  =  80/24            =  3.333 kohm
    total:    5.00 + 3.333                      =  8.333 kohm
    supply:   20.0 / 8.333                      =  2.400 mA
    V(A)   =  2.400 * 3.333                     =  8.00 V
    branch =  8.00 / 4.00                       =  2.00 mA
    V(L)   =  2.00 * 2.00                       =  4.00 V     agrees
```

Four lines against one, and that is for a single load. Answer the same question for six
loads and the equivalent has paid for itself several times over.

Notice also what $R_3$ did and did not do. It had no effect on $V_{Th}$, because no
current flowed in it while the terminals were open. It added its full 2.00 kΩ to
$R_{Th}$. A part can matter enormously to one of the two numbers and not at all to the
other, which is why they are worked out separately rather than in one pass.

## Worked: two sources, and the equivalent earns its keep

Now a box the divider formula cannot touch. A 12.0 V rail reaches node A through
$R_1 = 3.00$ kΩ. $R_2 = 6.00$ kΩ runs from A to ground. Also hanging on A is a chip that
draws a constant 2.00 mA out of the node whatever the voltage there does — a current
source, pointing down. The terminals are node A and ground.

```text
STEP 2 - the open-circuit voltage, by superposition

  the rail alone (current source opened):
    12.0 * 6.00/(3.00 + 6.00)                   =  8.00 V

  the chip alone (rail shorted, so R1 and R2 both run A to ground):
    R1 || R2  =  (3.00 * 6.00)/9.00             =  2.00 kohm
    2.00 mA drawn OUT of A, through 2.00 kohm   = -4.00 V

    V(Th)  =  8.00 - 4.00                       =  4.00 V

STEP 3 - the resistance looking in

  kill both: the rail becomes a wire, the chip becomes a gap.
  R1 and R2 are then both from A to ground.

    R(Th)  =  3.00 || 6.00                      =  2.00 kohm
```

4.00 V behind 2.00 kΩ. Two loads:

```text
    R(L) = 2.00 kohm:  V(L) = 4.00 * 2/(2+2)    =  2.00 V   I = 1.000 mA
    R(L) = 8.00 kohm:  V(L) = 4.00 * 8/(2+8)    =  3.20 V   I = 0.400 mA
```

Check the first by nodal analysis on the whole circuit, currents leaving node A, in
volts, kilohms and milliamps:

```text
    (vA - 12)/3  +  vA/6  +  2.00  +  vA/2  =  0
    multiply by 6:
    2vA - 24  +  vA  +  12  +  3vA          =  0
    6vA                                     =  12
    vA                                      =  2.00 V     agrees
```

And the second, with the 8.00 kΩ load: $8(v_A-12) + 4v_A + 48 + 3v_A = 0$ after
multiplying by 24, so $15v_A = 48$ and $v_A = 3.20$ V. Also agrees. Two complete nodal
solves, replaced by two divisions.

## The mistake people actually make

**Leaving the load connected while working out $R_{Th}$.** This is the big one. "The
resistance looking into the terminals" sounds like it ought to describe the circuit as it
stands, load and all, and it emphatically does not. $R_{Th}$ belongs to the box. The load
is the thing the box is going to be asked about, and if you fold it into $R_{Th}$ you have
put the answer into the question. In the first worked example, including the 2.00 kΩ load
would give $R_{Th} = 4.00 + (2.00 \parallel 2.00) = 5.00$ kΩ, and every prediction after
that would be wrong.

The tell is a definition worth holding on to: $R_{Th}$ is a property of the network with
the terminals **open**. If the load appears anywhere in the calculation, you are not
computing it.

**Deleting the resistor along with the source.** Killing a 12 V supply makes its terminals
one node; it does not remove the resistor that was connected to it. In the second example
above, dropping $R_1$ when the rail was shorted would give $R_{Th} = 6.00$ kΩ instead of
2.00 kΩ, and a load of 2 kΩ would then be predicted at 1.00 V instead of 2.00 V. Module 9
made the same point about superposition, and it is the same mistake because it is the same
operation. Count the resistors before and after: the number must not change.

**Believing in the internal node.** The equivalent has a node between $V_{Th}$ and
$R_{Th}$, and it does not exist. There is no point inside the real box sitting at 16.0 V.
Nor is $R_{Th}$ a component: it is a slope, drawn as a resistor because a drawing has to
be made of something.

## Where the theorem stops

**It needs linearity.** The proof used superposition, and superposition needs a network
whose parts obey laws with no powers in them. A box with a diode, a lamp filament or a
transistor in it does not have a straight $V$–$I$ line, so it has no single $V_{Th}$ and
$R_{Th}$. What replaces the theorem there is a *small-signal* equivalent: linearise about
one operating point and the whole of this module applies again to small changes around it.
That is how amplifier output impedance is defined, and it is a different claim — good near
one point rather than everywhere.

**It is a statement about exactly two terminals.** A network with three terminals brought
out is not covered; it takes a different and larger model. And an equivalent found at one
pair of terminals tells you nothing about any other pair.

**The equivalent is right outside and wrong inside.** It reproduces every voltage and
current at the terminals exactly, and it says nothing true about what is happening within
the box. $I^2R_{Th}$ is not the heat the real network is making. If you need to know how
hot something inside is getting, you need the original circuit.

**Independent sources only get killed.** A source whose value is set by a voltage or
current elsewhere in the same circuit — a transistor's model, an op-amp stage — leaves the
network linear, so it still has a Thévenin equivalent, but it must be left alive while you
find $R_{Th}$. The kill-and-look method fails on it. The next reading has the method that
does not, and it is worth knowing that such a network can even come out with a *negative*
$R_{Th}$, which is how oscillators are made.

**This is direct current.** With capacitors and inductors in the box the slope becomes a
complex impedance $Z_{Th}$ that depends on frequency, and every idea here carries across
unchanged with resistance replaced by impedance. That is EE102's problem, and it will be
easier for having been done once with real numbers.
''',
                },
                {
                    "title": "The same fact upside down, and a way to walk through a circuit",
                    "minutes": 13,
                    "body": r'''
The last reading left the box described by a source in series with a resistor. There is a
second description, it looks nothing like the first, and no measurement made at the
terminals can tell them apart. Module 6 met the pair for a battery. Here it applies to
anything at all, and it turns into a technique for getting through circuits that series
and parallel combining cannot touch.

## Rearranging one line

The Thévenin form obeys

$$V = V_{Th} - I R_{Th}$$

Solve it for $I$ instead, which is nothing more than algebra:

$$I = \frac{V_{Th}}{R_{Th}} - \frac{V}{R_{Th}}$$

Now read that as a description of a circuit rather than as a formula. It says: a fixed
current of $V_{Th}/R_{Th}$ is on offer, and whatever voltage $V$ ends up at the terminals
diverts $V/R_{Th}$ of it somewhere else. That is exactly a current source of
$V_{Th}/R_{Th}$ with a resistance $R_{Th}$ sitting across it, the load taking whatever is
left over.

$$I_N = \frac{V_{Th}}{R_{Th}}, \qquad R_N = R_{Th}$$

That is the **Norton equivalent**. It is the same straight line, written with the axes
swapped, and converting between the two forms is one multiplication or one division.

Two special values name themselves. Open the terminals and no current flows, so all of
$I_N$ goes through $R_{Th}$ and the terminals sit at $I_N R_{Th} = V_{Th}$ — the
open-circuit voltage, as it must be. Short the terminals and the whole of $I_N$ takes the
short in preference to nothing, so

$$I_{sc} = I_N = \frac{V_{Th}}{R_{Th}}, \qquad\text{and therefore}\qquad
R_{Th} = \frac{V_{oc}}{I_{sc}}$$

That last equation is the second way of finding $R_{Th}$, and it is the important one,
because it never asks you to reach inside. It cannot disagree with the kill-the-sources
method: both are descriptions of one straight line, and a line through the same two points
is the same line.

It is also the method that survives dependent sources, which the kill-and-look method does
not. Any box, however strange inside, can have its open-circuit voltage and its
short-circuit current measured or calculated, and their ratio is $R_{Th}$.

## Worked: walking a two-stage ladder to its equivalent

Here is what the transformation is for. A 18.0 V supply sits behind $R_1 = 3.00$ kΩ. From
that node, $R_2 = 6.00$ kΩ goes to ground and $R_3 = 4.00$ kΩ carries on to a second node.
From the second node, $R_4 = 3.00$ kΩ goes to ground and $R_5 = 1.00$ kΩ carries on to the
output terminals. What is the equivalent there?

The trick is to convert to whichever form lets you *merge* something, merge it, and
convert back. A Norton form merges with a shunt resistor; a Thévenin form merges with a
series one.

```text
    18.0 V in series with 3.00 kohm
      -> Norton:  18.0/3.00                     =  6.00 mA  ||  3.00 kohm

    that 3.00 kohm now sits beside R2 = 6.00 kohm, and parallel
    resistances merge

      3.00 || 6.00 = 18/9                       =  2.00 kohm
      -> still 6.00 mA, now || 2.00 kohm
      -> Thevenin: 6.00 mA * 2.00 kohm          =  12.0 V in series with 2.00 kohm

    R3 = 4.00 kohm is in series, so it merges straight in

      2.00 + 4.00                               =  6.00 kohm
      -> 12.0 V in series with 6.00 kohm

    -> Norton again:  12.0/6.00                 =  2.00 mA  ||  6.00 kohm

    that 6.00 kohm sits beside R4 = 3.00 kohm

      6.00 || 3.00 = 18/9                       =  2.00 kohm
      -> Thevenin: 2.00 mA * 2.00 kohm          =  4.00 V in series with 2.00 kohm

    and R5 = 1.00 kohm is the last series part

      2.00 + 1.00                               =  3.00 kohm
```

The terminals are **4.00 V behind 3.00 kΩ**, and the whole ladder has been walked in one
direction with no simultaneous equations anywhere.

Check both numbers independently. With the terminals open, $R_5$ carries nothing, so the
second node has only $R_4$ hanging on it:

```text
    seen from the first node:  4.00 + 3.00      =  7.00 kohm  (R3 then R4)
    beside R2:  7.00 || 6.00 = 42/13            =  3.2308 kohm
    with R1:    3.00 + 3.2308                   =  6.2308 kohm
    supply:     18.0 / 6.2308                   =  2.8889 mA
    node 1:     18.0 - 2.8889 * 3.00            =  9.3333 V
    node 2:     9.3333 * 3.00/7.00              =  4.0000 V     V(Th) confirmed

    kill the supply and look in from the terminals:
    3.00 || 6.00 = 2.00;  + 4.00 = 6.00;  || 3.00 = 2.00;  + 1.00
                                                =  3.00 kohm    R(Th) confirmed
```

Both agree. And now every load question is one line: a 3.00 kΩ load takes
$4.00 \times 3/6 = 2.00$ V and 0.667 mA; a 1.00 kΩ load takes $4.00 \times 1/4 = 1.00$ V
and 1.00 mA; and no load can ever take more than $4.00^2/(4 \times 3000) = 1.33$ mW.

## A third way to get $R_{Th}$: push and see

There are now two methods for $R_{Th}$ — kill the sources and combine, or divide $V_{oc}$
by $I_{sc}$ — and there is a third that contains both. Kill the independent sources, apply
a **test source** of your own at the terminals, and see what the network does with it.
Push in 1 A and the terminals rise by $R_{Th}$ volts. Apply 1 V and the current that flows
in is $1/R_{Th}$ amps.

On the ladder above: with the 18 V supply replaced by a wire, push 1.00 mA into the
terminals and they rise to $1.00\ \text{mA} \times 3.00\ \text{k}\Omega = 3.00$ V, so
$R_{Th} = 3.00\ \text{V}/1.00\ \text{mA} = 3.00$ kΩ. For a network you can combine by
inspection this is the same work in a longer coat, and there is no reason to prefer it.

It earns its place on the networks you cannot combine by inspection, because it turns
"what is the resistance of this?" into "solve this circuit", which is a thing you already
know how to do. Write the test source into a nodal analysis and the answer falls out with
no series-parallel reasoning at all. And it is the method that copes with a **dependent**
source, which the kill-and-look method cannot touch: dependent sources are not killed, so
they sit in the network responding to the test source, and only a solve can say what they
do. That is a second-year problem, but it is worth knowing now that the machinery already
handles it — and that a network with a dependent source in it can return a *negative*
$R_{Th}$, meaning the terminals push back harder the more you load them, which is the
beginning of how an oscillator works.

## Worked: the box you are not allowed to open

Everything above assumed you could see inside. On a bench you often cannot, and then the
$V_{oc}/I_{sc}$ relation is the whole method.

A sealed module. A meter across it reads 9.00 V with nothing else connected — that is
$V_{Th}$ directly, because a decent voltmeter draws so little current that the $IR_{Th}$
term is negligible. Now put a 3.00 kΩ resistor across it and the meter falls to 6.00 V.

```text
    the load is taking       6.00 / 3.00        =  2.00 mA
    the missing volts are    9.00 - 6.00        =  3.00 V
    and those volts were dropped inside, by that current

    R(Th)  =  3.00 V / 2.00 mA                  =  1.50 kohm
```

Or in one step, rearranging the divider: $R_{Th} = R_L(V_{oc}/V_L - 1) = 3.00(9.00/6.00 -
1) = 1.50$ kΩ. The Norton form of the same module is $9.00/1.50 = 6.00$ mA in parallel with
1.50 kΩ, and its short-circuit current is that same 6.00 mA.

Two things about that measurement matter in practice.

**Do not short it to find $I_{sc}$.** The formula says $I_{sc} = V_{oc}/R_{Th}$ and the
bench says a shorted output is how equipment dies. A load resistor and a voltmeter give
the same information with nothing at risk, and the load-resistor version also works on
sources whose behaviour changes when they are abused.

**There is a version that needs no arithmetic at all.** Make the load adjustable and turn
it until the meter reads exactly half the open-circuit voltage. At that point the load and
$R_{Th}$ are splitting the voltage equally, so they are equal, and $R_{Th}$ is whatever the
decade box says. This is the classic half-voltage method, and it is how you measure the
output resistance of anything with two terminals and a dial.

Then predictions, from the two numbers alone:

```text
    R(L) = 500 ohm:    V = 9.00 * 0.5/(1.5+0.5)  =  2.25 V    I = 4.50 mA
    R(L) = 13.5 kohm:  V = 9.00 * 13.5/15.0      =  8.10 V    I = 0.600 mA
```

Neither of those loads has ever been connected, and neither needs to be.

## The mistake people actually make

**Transforming across a node you still need an answer about.** This is the one that costs
real time. Every transformation destroys a node: converting an 18 V source behind 3 kΩ
into 6 mA beside 3 kΩ means the point between the source and the resistor no longer
appears anywhere in the drawing. In the ladder above, the first node genuinely sat at
9.3333 V, and after the second step there is nothing in the transformed circuit at that
voltage. The transformed circuit is not wrong; it has simply stopped answering that
question. Decide what you want *before* you start collapsing, keep the terminals you care
about outside the collapse, and never read an internal voltage off a transformed drawing.

It is a tempting mistake because the two drawings feel like the same circuit redrawn. They
are the same *box*, and only from the outside.

**Getting the Norton direction wrong.** $I_N$ is the current that flows through a short
placed across the terminals, and it flows in the direction the short-circuit current
actually goes. Flip it and every load voltage comes out with the wrong sign — an answer
that is not slightly off but negated.

**Reading the internal dissipation off whichever form is convenient.** Module 6 worked
this one out in detail and it applies to any network, not just a battery: the two forms
put entirely different powers in $R_{Th}$ while delivering identical power to the load.
Use either form for anything outside the terminals; use neither for anything inside.

## Where the transformation stops

**An ideal voltage source has no Norton form.** Its $R_{Th}$ is zero, so $I_N =
V_{Th}/R_{Th}$ is infinite. Likewise an ideal current source has $R_{Th} = \infty$ and no
Thévenin form. The two idealisations sit exactly at the two ends where the conversion
breaks, and every real source is somewhere in between.

**The resistor has to be genuinely in series with the source.** A resistor that merely
looks adjacent on the page, but has a third connection on the node between it and the
source, is not in series with it and cannot be swept into a transformation. Trace the
wire; count what touches the node.

**Merging only works where something is actually parallel or series.** A ladder collapses
because at every stage there was a shunt to merge with or a series part to add. A bridge
does not: no two components in it are in series or in parallel, so no transformation gets
started, and the equivalent has to come from nodal analysis or from $V_{oc}$ and $I_{sc}$
computed separately. Reach for nodal when the transformations stall — the answer is still
a Thévenin equivalent, it just has to be worked out rather than walked to.

**And all of it is still linearity.** Merging current sources by adding them, merging
resistances, superposing contributions: every step assumed straight lines, and none of it
survives a diode.
''',
                },
                {
                    "title": "Output resistance, and what it costs to make it small",
                    "minutes": 13,
                    "body": r'''
The two numbers are not only an analysis trick. $R_{Th}$ is a specification — it appears
on the data sheet of every signal source, every reference, every sensor, usually called
*output resistance* or *output impedance* — and it is the number that tells you in advance
how much a circuit will be spoiled by whatever gets connected to it. This reading is what
the equivalent is for.

## Sag, in one expression

Hang a load $R_L$ on a source of $V_{Th}$ and $R_{Th}$:

$$V_L = V_{Th}\,\frac{R_L}{R_{Th}+R_L}, \qquad
\frac{V_{Th}-V_L}{V_{Th}} = \frac{R_{Th}}{R_{Th}+R_L}$$

The fractional error is not about the size of either resistance on its own; it is about
their **ratio**. A load ten times $R_{Th}$ costs you 9.1%. A hundred times, 0.99%. A
thousand times, 0.1%. That single line is the design rule the rest of this reading is
built on: *to keep the error below $1/n$, make the load at least $n$ times the output
resistance.*

## Worked: a 3.00 V reference off a 12.0 V rail, three ways

A divider is the cheapest possible reference, and a divider's Thévenin resistance is
$R_1 \parallel R_2$ — the two resistors in parallel, because with the supply killed they
both run from the output to ground. That fact is worth having by heart.

Take a 12.0 V rail and a wanted 3.00 V, so the lower resistor is always a quarter of the
chain. A 10.0 kΩ load will be hung on it.

```text
DESIGN A     R1 = 9.00 kohm,  R2 = 3.00 kohm

    V(Th)  =  12.0 * 3/12                       =  3.00 V
    R(Th)  =  9.00 || 3.00 = 27/12              =  2.25 kohm
    idle current  =  12.0 / 12.0 kohm           =  1.00 mA    -> 12.0 mW
    with 10.0 kohm on it:
        V   =  3.00 * 10.0/(2.25 + 10.0)        =  2.449 V    18.4% low

DESIGN B     R1 = 900 ohm,   R2 = 300 ohm       same ratio, ten times smaller

    R(Th)  =  900 || 300 = 270000/1200          =  225 ohm
    idle current  =  12.0 / 1200                =  10.0 mA    -> 120 mW
    with 10.0 kohm on it:
        V   =  3.00 * 10000/(225 + 10000)       =  2.934 V    2.20% low

DESIGN C     R1 = 390 ohm,   R2 = 130 ohm       real E24 parts, ratio 3:1

    V(Th)  =  12.0 * 130/520                    =  3.00 V
    R(Th)  =  390 * 130/520                     =  97.5 ohm
    idle current  =  12.0 / 520                 =  23.1 mA    -> 277 mW
    with 10.0 kohm on it:
        V   =  3.00 * 10000/(97.5 + 10000)      =  2.971 V    0.97% low
```

Read the three together and the trade is completely explicit. Each factor of ten off
$R_{Th}$ buys a factor of ten off the error and costs a factor of ten in idle current, and
therefore in wasted power. There is no cleverness available: for a plain divider,
stiffness is bought with current, at a fixed exchange rate.

That is also the honest answer to "why not just use a divider" for a real power rail. To
supply 100 mA at 3 V with 1% regulation you would need $R_{Th}$ near 300 mΩ, which means
an idle current of tens of amps. A regulator gets an output resistance in the milliohms
while drawing almost nothing, and that — not the voltage — is what you are buying.

## Worked: two dividers in a row, and the answer everyone gets wrong

A 10.0 V rail. Divider one: 10.0 kΩ and 10.0 kΩ, output at the middle. Divider two, hung
on that output: another 10.0 kΩ and 10.0 kΩ, output at *its* middle. Two halvings, so
2.50 V. That is the answer, and it is wrong.

```text
    stage 1 on its own:   V(Th) = 5.00 V,  R(Th) = 10.0 || 10.0  =  5.00 kohm
    stage 2, seen from its input, is just two resistors in series =  20.0 kohm

    so stage 2 loads stage 1 with 20.0 kohm:

        node between them  =  5.00 * 20.0/(5.00 + 20.0)   =  4.00 V
        stage 2 halves it  =  4.00 / 2                    =  2.00 V
```

2.00 V, not 2.50 V — a 20% error, from a circuit that looks like it cannot go wrong. The
naive answer multiplies the two ratios, and multiplying ratios is only legal when each
stage is driven by something stiff enough not to notice the next one.

Two fixes, and they are the two fixes for this in general. Make stage two's resistors far
larger — a megohm each gives an input resistance of 2.00 MΩ, so the node sits at
$5.00 \times 2000/2005 = 4.988$ V and the output at 2.494 V, 0.25% low. Or put a buffer
between them, which is an amplifier's job and this course's sequel's subject. The general
rule reads: **each stage's input resistance must be much larger than the previous stage's
output resistance**, and the error is roughly the ratio of the two.

## The same arithmetic, done by your meter

Your instruments are loads too, and they have the input resistance printed on them for
exactly this reason.

A node whose Thévenin resistance is 100 kΩ — an ordinary enough divider — measured three
ways:

```text
    10 Mohm digital multimeter:  10.0/(10.0 + 0.1)      =  0.990   1.0% low
    1 Mohm oscilloscope input:   1.00/(1.00 + 0.1)      =  0.909   9.1% low
    10:1 scope probe, 10 Mohm:   10.0/(10.0 + 0.1)      =  0.990   1.0% low
```

The scope reading is 9% low and the scope is working perfectly. It is the circuit that has
changed, because connecting the instrument changed it. This is the most common way for a
bench measurement to be quietly wrong, and the defence is to know the node's $R_{Th}$
before you probe it. If the instrument's input resistance is not at least a hundred times
that, you are measuring your own instrument as much as the circuit.

## The load does not have to be linear

One restriction that is easy to over-apply: Thévenin's theorem needs the *network* to be
linear. It says nothing at all about the load. That is not a technicality — it is what
makes the equivalent the standard first move in problems that are otherwise unpleasant.

An LED is about as nonlinear as a component gets: below roughly 1.8 V it conducts almost
nothing, and over the next two hundred millivolts its current climbs by orders of
magnitude. Put one across a network of nine resistors and three supplies and there is no
formula for the answer. Replace the network by its equivalent — say it comes out at
$V_{Th} = 9.00$ V and $R_{Th} = 330\ \Omega$ — and the whole problem is two statements
about one pair of numbers $(V, I)$:

```text
    the network says     I  =  (9.00 - V) / 330        a straight line
    the LED says         I  =  whatever its curve says at V
```

Plot both on the same axes and the operating point is where they cross. The straight line
is called the **load line**, and it is the only thing the entire network contributes to
the problem. For a red LED sitting near 2.0 V:

```text
    at V = 2.0 V:   I  =  (9.00 - 2.0)/330            =  21.2 mA
    if that current in fact holds it at 2.05 V:
                    I  =  (9.00 - 2.05)/330           =  21.1 mA
```

Two passes and it has converged, because the line is steep compared with the device curve
— which is exactly why a series resistor is what sets an LED's current and the LED's own
voltage barely matters. The same construction sets a transistor's operating point, a
diode's, a solar panel's. In every case the work is: reduce everything linear to two
numbers, draw the line, intersect.

## The ceiling on power, and why it is usually the wrong target

One more thing the two numbers settle. A load takes

$$P = \frac{V_{Th}^2 R_L}{(R_{Th}+R_L)^2}$$

which is zero at both extremes — a huge load gets the full voltage but no current, a tiny
one gets the full current but no voltage — so somewhere between there is a maximum. The
derivation unit in this module works out where without calculus; the answer is $R_L =
R_{Th}$, and there

$$P_{max} = \frac{V_{Th}^2}{4R_{Th}}$$

For design A above, $3.00^2/(4 \times 2250) = 1.00$ mW is the most any load will ever get
out of that reference, whatever it is made of. That is a fact about the source, not about
the load.

Two consequences are worth carrying.

**The peak is broad.** Writing $k = R_L/R_{Th}$, the fraction of the maximum a load takes
is $4k/(1+k)^2$. At $k = 2$ or $k = \tfrac12$ that is $8/9$, which is 89% of the best
possible; at $k = 10$ or $k = \tfrac1{10}$ it is still 33%. Being a factor of two out
costs 11%, so nobody chooses a matching resistor to three figures.

**At the match, half the energy goes into the source.** Equal resistances carry the same
current, so they dissipate equally, and the efficiency is exactly 50%. That is a fine
bargain when the available power is fixed and tiny — an antenna, a thermocouple, a
photodiode, a piezo harvester — because half of a small thing is the most you were ever
getting. It is a terrible bargain for anything with a power budget, where you want
$R_{Th}$ small and $R_L$ large, an efficiency near 100%, and a delivered power far below
the theoretical ceiling.

The two are different questions and confusing them is the classic error here. Maximum
power asks: *$V_{Th}$ and $R_{Th}$ are fixed, what $R_L$?* Efficiency asks: *$R_L$ is
fixed, what $R_{Th}$?* — and that second question has no interior answer at all, only
"as small as you can afford".

## Where this stops

**Direct current only.** With reactance in the network, $R_{Th}$ becomes $Z_{Th}$ and
depends on frequency, and the load that takes the most power is the complex conjugate of
$Z_{Th}$ rather than a copy of it. Everything else in this reading survives the
translation with resistance replaced by impedance.

**Matching a transmission line is a different problem with the same number.** At radio
frequencies a cable is terminated in its characteristic impedance to stop the signal
reflecting off the far end, which is a statement about waves rather than about power
transfer; the two conditions coincide for a resistive line and are argued for on
completely different grounds.

**An active output has an $R_{Th}$ that is not a resistor.** A regulator or an op-amp
output behaves like a few milliohms because feedback holds the voltage up as the current
rises, not because a small resistor is fitted. Thévenin still describes it — the terminals
still show a straight line over the working range — but the number is a behaviour, and it
collapses the moment the feedback runs out of range or the current limit trips.

**And a nonlinear source has no fixed matched load.** A solar panel's best operating point
moves with sunlight and temperature, which is why every solar inverter runs a maximum
power point tracker rather than a fixed resistance. The idea survives; the fixed number
does not.
''',
                },
            ],
            "quiz": {
                "title": "Two numbers for any network",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A sealed box measures 10.00 V open-circuit, and 5.00 mA when its terminals are shorted. What is its Thévenin resistance?",
                        "opts": ["50 Ω", "2 kΩ", "500 Ω", "50 kΩ"],
                        "a": 1,
                        "why": r'''
$R_{Th} = V_{oc}/I_{sc} = 10/0.005 = 2$ kΩ. Shorting the terminals puts the whole
open-circuit voltage across the Thévenin resistance alone, since the load contributes
nothing, so the short-circuit current measures that resistance directly. It is the
standard method for a box you cannot open — though on real equipment a large load
rather than a dead short is safer, and two loads give the same information.
''',
                    },
                    {
                        "q": "A 12 V rail feeds two 10 kΩ resistors in series, and the output is taken from the midpoint. What is the Thévenin equivalent at that output?",
                        "opts": [
                            "6 V in series with 20 kΩ",
                            "12 V in series with 10 kΩ",
                            "6 V in series with 5 kΩ",
                            "6 V in series with 10 kΩ",
                        ],
                        "a": 2,
                        "why": r'''
Open-circuit, the midpoint of two equal resistors sits at half the rail: 6 V. For the
resistance, kill the supply — replace it with a wire — and the two 10 kΩ resistors
are then both connected between the output and ground, in parallel: 5 kΩ. That is why a
divider sags under load, and it says by exactly how much: hanging 5 kΩ on this output
halves it to 3 V.
''',
                    },
                    {
                        "q": "When finding $R_{Th}$ by killing the sources, what happens to the resistors that were in series with them?",
                        "opts": [
                            "they are removed along with their sources",
                            "they stay, and are part of the resistance you are working out",
                            "they are doubled",
                            "they are replaced by open circuits",
                        ],
                        "a": 1,
                        "why": r'''
They stay. Killing a source neutralises the source and nothing else — the resistance
of the network is exactly what you are trying to measure, so removing part of it would
be measuring something else. In the divider example the supply becomes a wire, and that
is precisely what puts the upper resistor in parallel with the lower one instead of in
series with it.
''',
                    },
                    {
                        "q": "A network has $V_{Th} = 6$ V and $R_{Th} = 5$ kΩ. What is the most power any load can ever take from it?",
                        "opts": ["7.2 mW", "0.9 mW", "3.6 mW", "1.8 mW"],
                        "a": 3,
                        "why": r'''
The maximum is $V_{Th}^2/4R_{Th} = 36/20000 = 1.8$ mW, reached with a 5 kΩ load: that
load sees 3 V and takes 0.6 mA, which is 1.8 mW. Nothing else does better — a 1 kΩ
load draws more current but at only 1 V, and a 25 kΩ load sees 5 V but draws almost
nothing. The figure 7.2 mW is $V^2/R$ with the internal resistance ignored, which is
the power a *perfect* 6 V source would deliver into 5 kΩ.
''',
                    },
                    {
                        "q": "Why is a mains power supply not designed with its output resistance matched to its load?",
                        "opts": [
                            "because matching only works for one load value",
                            "because a matched source wastes half its energy heating itself",
                            "because matching would make the output voltage unstable in time",
                            "because the maximum power theorem does not apply to mains equipment",
                        ],
                        "a": 1,
                        "why": r'''
At the match, the source resistance and the load carry the same current through equal
resistances, so they dissipate equally: half the energy drawn goes into warming the
supply. Where energy is plentiful and only the load matters — an antenna, a
thermocouple, a sensor whose signal cannot be made bigger — that trade is worth it,
and matching is exactly what you want. Where energy is being paid for, you want
$R_{Th}$ as small as you can make it and a load far larger than it, which delivers less
than the theoretical maximum power at an efficiency near 100%.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "Two numbers, and then every load is one line",
                    "minutes": 9,
                    "caption": "the open-circuit voltage, the resistance looking in, and three loads answered",
                    "lang": "text",
                    "brief": r'''
The same network appears four times below, and only the first two calculations are any
work. Everything after them is one division, which is the entire reason for doing the
first two.

Watch which resistor turns up in which calculation. The one on the way out to the
terminals is absent from $V_{Th}$ altogether and adds its full value to $R_{Th}$; the
supply is central to $V_{Th}$ and is deleted before $R_{Th}$ is even started.
''',
                    "listing": r'''
18 V, a 6.0k/3.0k divider, and 2.0k on the way out to the terminals
--------------------------------------------------------------------

  V(Th) first.  Nothing is connected, so the 2.0 kohm carries no
  current and therefore drops nothing.  The terminals sit exactly
  where the divider puts the node above them.

    V(Th)     =  18 * 3000/(6000 + 3000)
              =  ___ V

  R(Th) next.  Kill the supply: it becomes a wire, so the top of the
  6.0 kohm is grounded and the two divider resistors end up side by
  side between that node and ground.

    6k || 3k  =  (6000 * 3000)/(6000 + 3000)
              =  ___ ohm            below 3000, as a parallel pair must be

    R(Th)     =  that pair, plus the 2.0 kohm which is in series with it
              =  ___ ohm

  the box is now two numbers, and every load is a single division

    with 12 kohm:   V(L)  =  V(Th) * 12000/(R(Th) + 12000)
                          =  ___ V
                    I(L)  =  that / 12000                 =  0.375 mA

    with 4.0 kohm:  V(L)  =  V(Th) * 4000/(R(Th) + 4000)  =  3.00 V
                    P(L)  =  3.00^2 / 4000                =  ___ mW

  that last load happens to equal R(Th), so no other load anywhere
  takes more power than the figure on that line.
''',
                    "blanks": [
                        {
                            "prompt": "18 V split by 6.0 kΩ above and 3.0 kΩ below. What do the open terminals show?",
                            "hole": "?",
                            "opts": ["12.0", "6.00", "4.91", "18.0"],
                            "a": 1,
                            "why": "$18 \\times 3/(6+3) = 6.00$ V. The lower resistor is a third of the "
                                   "chain, so it keeps a third of the supply. A value of 12.0 puts the "
                                   "upper resistor on top of the fraction, which is the other resistor's "
                                   "share. A value of 4.91 comes from counting the 2.0 kΩ into the "
                                   "divider — $18 \\times 3/11$ — and it is the tempting error here: the "
                                   "2.0 kΩ really is in the circuit, but with the terminals open no "
                                   "current passes through it, so it drops nothing and cannot be part of "
                                   "any division.",
                        },
                        {
                            "prompt": "6.0 kΩ and 3.0 kΩ in parallel. How many ohms?",
                            "hole": "?",
                            "opts": ["9000", "2000", "4500", "1500"],
                            "a": 1,
                            "why": "$(6000 \\times 3000)/9000 = 2000\\ \\Omega$. A value of 9000 is the "
                                   "two added, which is the series rule; 4500 is their average, which is "
                                   "not a rule at all. The check that catches both: a parallel pair "
                                   "always comes out below the smaller of the two, so anything at or "
                                   "above 3000 is wrong before you look at the arithmetic.",
                        },
                        {
                            "prompt": "That 2000 Ω pair, with the 2.0 kΩ output resistor in series. How many ohms?",
                            "hole": "?",
                            "opts": ["2000", "1000", "4000", "11000"],
                            "a": 2,
                            "why": "$2000 + 2000 = 4000\\ \\Omega$. Looking in from the terminals you meet "
                                   "the 2.0 kΩ first and the parallel pair behind it, one after the "
                                   "other, so they add. A value of 1000 puts them in parallel instead — "
                                   "the commonest slip in this calculation, because the previous line was "
                                   "a parallel one and the hand carries on. A value of 2000 forgets the "
                                   "output resistor altogether, which is exactly the resistor that was "
                                   "irrelevant to $V_{Th}$ and matters most here.",
                        },
                        {
                            "prompt": "6.00 V behind 4.00 kΩ, with a 12 kΩ load on it. How many volts?",
                            "hole": "?",
                            "opts": ["6.00", "4.50", "3.00", "1.50"],
                            "a": 1,
                            "why": "$6.00 \\times 12/(4+12) = 4.50$ V. The load takes three quarters of "
                                   "the open-circuit voltage because it is three quarters of the total "
                                   "resistance in the loop. A value of 6.00 assumes the load changes "
                                   "nothing, which is what an ideal source would do and what $R_{Th} = "
                                   "4$ kΩ says it does not; a value of 3.00 is what an equal load — "
                                   "4 kΩ — would see.",
                        },
                        {
                            "prompt": "3.00 V across 4000 Ω. How many milliwatts?",
                            "hole": "?",
                            "opts": ["9.00", "4.50", "2.25", "1.13"],
                            "a": 2,
                            "why": "$3.00^2/4000 = 0.00225$ W, which is 2.25 mW. It agrees with "
                                   "$V_{Th}^2/4R_{Th} = 36/16000$, as it must, because a load equal to "
                                   "$R_{Th}$ is the matched one. A value of 9.00 is $V_{Th}^2/R_{Th}$ "
                                   "with the division forgotten — the power a perfect 6 V source would "
                                   "put into 4 kΩ, and four times what is actually available.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "The voltage the terminals show before anything is connected",
                    "minutes": 5,
                    "brief": r'''
The first of the two numbers, on the simplest network that has anything to say. One
supply, two resistors making a divider, and a third resistor on the way out to the
terminals where a load will eventually go.

Nothing is connected to those terminals yet. That is not a detail of the wording, it is
the definition of the quantity being asked for, and it decides what the third resistor
does.
''',
                    "prompt": "What is the Thévenin voltage at the probed terminals?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 15},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 6000},
                            {"id": "p2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 3000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "p3", "kind": "R", "x": 15, "y": 6, "value": 1000},
                            {"id": "o0", "kind": "OUT", "x": 19, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 9], "b": [11, 11]},
                            {"a": [11, 6], "b": [14, 6]},
                            {"a": [16, 6], "b": [19, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "15.0 V"},
                        {"label": "R1, supply down to node A", "value": "6.00 kΩ"},
                        {"label": "R2, node A down to ground", "value": "3.00 kΩ"},
                        {"label": "R3, node A out to the terminals", "value": "1.00 kΩ"},
                        {"label": "Connected to the terminals", "value": "nothing"},
                    ],
                    "aside": "A resistor with no current in it drops no voltage. Decide which resistors "
                             "are carrying current before you decide which ones are in the division.",
                    "answer": 5.0,
                    "tol": 0.03,
                    "unit": "V",
                    # The probe is on the open terminals, so the open-circuit voltage is
                    # literally what the solver reads there.
                    "check": "return c.vout();",
                    "hint": "With the terminals open there is nowhere for current to go beyond node A, "
                            "so R3 carries none and drops none. The terminals are therefore at node A, "
                            "and node A is one divider away from the supply.",
                    "wrong": "If you got 4.50, R3 has been counted into the divider as though it were "
                             "part of the chain to ground: $15.0 \\times 3/(6+3+1)$. It is not — it "
                             "leads to an open circuit, so no current passes through it and it drops "
                             "nothing. If you got 10.0, the upper resistor has gone on top of the "
                             "fraction, which is the share R1 takes rather than the share R2 keeps.",
                    "why": r'''
```
nothing is connected to the terminals, so no current can flow past
node A into R3

    I(R3)      =  0
    drop(R3)   =  0 * 1000                      =  0 V

which leaves one divider, and it is the whole calculation

    V(Th)      =  15.0 * 3000/(6000 + 3000)
               =  15.0 * 0.3333                 =  5.00 V
```

5.00 V. Sanity check it two ways before moving on: the answer must lie between 0 V and
the 15.0 V supply, and it must be nearer whichever divider resistor is larger — the
6.00 kΩ is on top, so the output sits in the lower half, which 5.00 V does.

Now notice what R3 costs, because this is the point of drawing it at all. It contributed
nothing whatever to $V_{Th}$. It contributes its full value to the other number:

$$R_{Th} = (6.00 \parallel 3.00) + 1.00 = 2.00 + 1.00 = 3.00\ \text{k}\Omega$$

So this network is 5.00 V behind 3.00 kΩ, and hanging a 3.00 kΩ load on it would pull the
terminals down to 2.50 V. A part that is invisible in one of the two numbers can dominate
the other, which is why they are worked out in separate passes rather than in one.
''',
                },
                {
                    "title": "A module you are not allowed to open",
                    "minutes": 7,
                    "brief": r'''
No schematic this time, because there is nothing to draw: the thing is sealed, and two
meter readings are everything you are ever going to know about it.

That is not a handicap. Two readings are exactly two numbers, and two numbers are the
whole of what the terminals can express — so this measurement is not an approximation to
opening the case, it is complete.
''',
                    "prompt": "What is the module's Thévenin resistance?",
                    "note": "Give the answer in kilohms, to two decimal places.",
                    "figure": "A sealed module with two terminals. A voltmeter across it, with nothing "
                              "else connected, reads 12.00 V steadily. A 1.50 kΩ resistor is then "
                              "connected across the same two terminals, and the meter falls to 3.75 V "
                              "and stays there. The meter itself draws so little current that it can be "
                              "ignored.",
                    "given": [
                        {"label": "Open-circuit reading", "value": "12.00 V"},
                        {"label": "Load fitted", "value": "1.50 kΩ"},
                        {"label": "Reading with the load on", "value": "3.75 V"},
                        {"label": "Meter loading", "value": "negligible"},
                    ],
                    "aside": "The volts that went missing were dropped inside the module, by the "
                             "current the load is drawing. Volts over amps is ohms.",
                    "answer": 3.3,
                    "tol": 0.03,
                    "unit": "kΩ",
                    "hint": "Work out the load current from the load's own reading and its own "
                            "resistance — that is the one branch you know everything about. The "
                            "same current is flowing through $R_{Th}$, and the voltage across "
                            "$R_{Th}$ is whatever the open-circuit reading has lost.",
                    "wrong": "If you got 4.80, that is $R_{Th} + R_L$, the whole loop: 12.00 V over "
                             "2.50 mA is the total resistance the source is pushing against, and the "
                             "1.50 kΩ has still to be taken off it. If you got 1.50, that is the "
                             "load you fitted. If you got 0.68, the two voltages have swapped roles in "
                             "the ratio — $1.50 \\times 3.75/8.25$ instead of $1.50 \\times "
                             "8.25/3.75$ — and the answer fails the quickest check there is: the "
                             "terminals fell to under a third of their open-circuit value, so most of "
                             "the resistance in the loop must be inside, not outside.",
                    "why": r'''
```
start with the branch you know completely - the load

    I      =  3.75 V / 1500 ohm                 =  2.50 mA

that same current flows inside the module, and the volts it lost
on the way out are the ones missing from the open-circuit reading

    lost   =  12.00 - 3.75                      =  8.25 V

    R(Th)  =  8.25 V / 2.50 mA                  =  3300 ohm = 3.30 kohm
```

Or in one rearrangement of the divider, which is the same thing written shorter:
$R_{Th} = R_L(V_{oc}/V_L - 1) = 1.50 \times (12.00/3.75 - 1) = 1.50 \times 2.20 = 3.30$
kΩ.

Check it forwards: 12.00 V across $3.30 + 1.50 = 4.80$ kΩ gives 2.50 mA, and 2.50 mA
through the 1.50 kΩ load is 3.75 V. That closes.

The module is 12.00 V behind 3.30 kΩ, and its Norton form is
$12.00/3.30 = 3.64$ mA in parallel with the same 3.30 kΩ — which is also what a short
across the terminals would draw, though putting one there to find out is a poor idea when
a resistor and a voltmeter have just told you the same thing safely.

Notice how far the terminals fell: a 1.50 kΩ load took this module down to under a third
of its open-circuit voltage. That is what a Thévenin resistance of 3.30 kΩ *means*, and it
is why the number is worth measuring before you design anything around the module. A load
of 330 kΩ would have read 11.88 V and told you almost nothing.
''',
                },
                {
                    "title": "What the load actually gets",
                    "minutes": 8,
                    "brief": r'''
The load is fitted now, and the question is about the current in it. Two ways to the
answer: collapse the whole network the long way, or take the equivalent at the load's own
terminals and divide once.

Do it by the equivalent. The long way is drilled elsewhere in this course, and the point
here is the habit of cutting the load out first — because the two numbers you get by doing
that are reusable, and the long way's numbers are not.
''',
                    "prompt": "What current flows in R4, the 5.00 kΩ load?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 18},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 3000},
                            {"id": "p2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "p3", "kind": "R", "x": 15, "y": 6, "value": 1000},
                            {"id": "p4", "kind": "R", "x": 19, "y": 8, "rot": 1, "value": 5000},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 11},
                            {"id": "o0", "kind": "OUT", "x": 22, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 9], "b": [11, 11]},
                            {"a": [11, 6], "b": [14, 6]},
                            {"a": [16, 6], "b": [19, 6]},
                            {"a": [19, 6], "b": [19, 7]},
                            {"a": [19, 9], "b": [19, 11]},
                            {"a": [19, 6], "b": [22, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "18.0 V"},
                        {"label": "R1, supply down to node A", "value": "3.00 kΩ"},
                        {"label": "R2, node A down to ground", "value": "6.00 kΩ"},
                        {"label": "R3, node A across to the load", "value": "1.00 kΩ"},
                        {"label": "R4, the load", "value": "5.00 kΩ"},
                    ],
                    "aside": "Lift R4 out of the circuit before you start. What is left is the network "
                             "whose two numbers you want, and R4 comes back at the very end as the "
                             "second half of one divider.",
                    "answer": 1.5,
                    "tol": 0.02,
                    "unit": "mA",
                    # The prompt names R4, so the check measures R4: its drop and its own value
                    # both come out of the solve rather than being restated from the drawing.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'p4'; })[0];
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1000;
''',
                    "hint": "With R4 lifted out, R3 carries nothing, so $V_{Th}$ is just what the "
                            "3.00 k / 6.00 k divider makes. For $R_{Th}$, short the supply and the two "
                            "divider resistors fall side by side; R3 is then in series with that pair.",
                    "wrong": "If you got 2.40, $R_{Th}$ has been left out and the whole 12.0 V put "
                             "across the load alone. If you got 3.00, that is the supply current, "
                             "which splits between R2 and the load branch rather than going wholly "
                             "into either. If you got 1.71, R3 has been dropped from $R_{Th}$, leaving "
                             "2.00 kΩ instead of 3.00 — which is the same as hanging the load "
                             "straight on node A.",
                    "why": r'''
```
STEP 1 - lift R4 out.  R3 then carries nothing, so the terminals sit
at node A, and node A is one divider.

    V(Th)  =  18.0 * 6000/(3000 + 6000)         =  12.0 V

STEP 2 - kill the supply: it becomes a wire, so R1 now runs from node
A to ground, right beside R2.  R3 is in series with that pair.

    R1 || R2  =  (3.00 * 6.00)/9.00             =  2.00 kohm
    R(Th)     =  2.00 + 1.00                    =  3.00 kohm

STEP 3 - put R4 back, on the equivalent

    V(L)   =  12.0 * 5.00/(3.00 + 5.00)         =  7.50 V
    I(L)   =  7.50 / 5000                       =  1.50 mA
```

Now the long way, to prove the two agree:

```
    R3 + R4     =  1.00 + 5.00                  =  6.00 kohm
    beside R2   =  (6.00 * 6.00)/12.0           =  3.00 kohm
    with R1     =  3.00 + 3.00                  =  6.00 kohm
    supply      =  18.0 / 6.00                  =  3.00 mA
    node A      =  18.0 - 3.00 * 3.00           =  9.00 V
    load branch =  9.00 / 6.00                  =  1.50 mA
    R2 carries  =  9.00 / 6.00                  =  1.50 mA
                                                   -------
                                                   3.00 mA   KCL at A
```

Same 1.50 mA, and the KCL line at the bottom costs one addition and catches almost any
slip above it.

The reason to prefer the first route is not that it is shorter here — it is barely
shorter. It is that its two intermediate numbers, 12.0 V and 3.00 kΩ, answer every other
load as well. A 1.00 kΩ load takes $12.0/(3.00+1.00) = 3.00$ mA; a 21.0 kΩ load takes
$12.0/24.0 = 0.500$ mA. Neither needs the network looked at again. The long way's
intermediate numbers — 6.00 kΩ, 3.00 mA, 9.00 V — are true only for the 5.00 kΩ load and
have to be thrown away and recomputed for the next one.
''',
                },
                {
                    "title": "Two sources feeding one load, and how hot it gets",
                    "minutes": 10,
                    "brief": r'''
A second source, and it is not a supply: the circle with an arrow hanging below node A is
a current source, drawing a fixed 2.00 mA out of that node whatever the voltage there
turns out to be. That is how a chip's supply current gets modelled long before anyone
knows what is inside the chip.

Two sources means $V_{Th}$ takes two passes — superposition, one source at a time — but
$R_{Th}$ takes no longer than before, because killing two sources is no harder than
killing one. And the answer wanted is a power, so there is one more step after the divider
than there was last time.
''',
                    "prompt": "How much power does R4, the 2.00 kΩ load, turn into heat?",
                    "note": "Give the answer in milliwatts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 4000},
                            {"id": "p2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 12000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "i1", "kind": "I", "x": 7, "y": 8, "rot": 1, "value": 0.002},
                            {"id": "g3", "kind": "GND", "x": 7, "y": 11},
                            {"id": "p3", "kind": "R", "x": 15, "y": 6, "value": 3000},
                            {"id": "p4", "kind": "R", "x": 19, "y": 8, "rot": 1, "value": 2000},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 11},
                            {"id": "o0", "kind": "OUT", "x": 22, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 9], "b": [11, 11]},
                            {"a": [7, 7], "b": [7, 6]},
                            {"a": [7, 6], "b": [11, 6]},
                            {"a": [7, 9], "b": [7, 11]},
                            {"a": [11, 6], "b": [14, 6]},
                            {"a": [16, 6], "b": [19, 6]},
                            {"a": [19, 6], "b": [19, 7]},
                            {"a": [19, 9], "b": [19, 11]},
                            {"a": [19, 6], "b": [22, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "24.0 V"},
                        {"label": "R1, supply down to node A", "value": "4.00 kΩ"},
                        {"label": "R2, node A down to ground", "value": "12.0 kΩ"},
                        {"label": "Current drawn out of node A", "value": "2.00 mA, constant"},
                        {"label": "R3, node A across to the load", "value": "3.00 kΩ"},
                        {"label": "R4, the load", "value": "2.00 kΩ"},
                    ],
                    "aside": "Killing the current source means removing it and leaving the gap; killing "
                             "the supply means replacing it with a wire. Neither operation touches a "
                             "single resistor.",
                    "answer": 4.5,
                    "tol": 0.05,
                    "unit": "mW",
                    # A power is not a node of this circuit, so the check takes the drop across
                    # R4 and R4's own value out of the solve and squares the one over the other.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'p4'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
return drop * drop / r.value * 1000;
''',
                    "hint": "Lift R4 out first. For $V_{Th}$, do the rail on its own (open the current "
                            "source) and then the current source on its own (short the rail, which puts "
                            "R1 and R2 in parallel), and add the two — the second contribution is "
                            "negative, because the current is being taken *out* of the node. For "
                            "$R_{Th}$, kill both and look in through R3.",
                    "wrong": "If you got 18.0, the current source's contribution has been added instead "
                             "of subtracted, giving $V_{Th} = 24.0$ V and 6.00 V on the load. If you "
                             "got 72.0, $R_{Th}$ has been ignored and the whole 12.0 V put across the "
                             "load. If you got 13.5, the power has been taken on $R_{Th}$'s share of "
                             "the voltage rather than the load's — 9.00 V across 6.00 kΩ — which is "
                             "the heat the equivalent's resistor would make, and that resistor does "
                             "not exist.",
                    "why": r'''
```
STEP 1 - lift R4 out.  R3 then carries nothing, so the terminals sit
at node A.  Two sources, so V(Th) comes in two passes.

  the rail alone, current source opened:

    24.0 * 12.0/(4.00 + 12.0)                   =  18.0 V

  the current source alone, rail shorted, so R1 and R2 are both from
  node A to ground:

    R1 || R2  =  (4.00 * 12.0)/16.0             =  3.00 kohm
    2.00 mA taken OUT of A, through 3.00 kohm   = -6.00 V

    V(Th)     =  18.0 - 6.00                    =  12.0 V

STEP 2 - kill both and look in from the terminals

    R(Th)     =  (4.00 || 12.0) + 3.00
              =  3.00 + 3.00                    =  6.00 kohm

STEP 3 - put the load back, then square it

    V(L)      =  12.0 * 2.00/(6.00 + 2.00)      =  3.00 V
    P(L)      =  3.00^2 / 2000                  =  0.00450 W = 4.50 mW
```

Confirm it with a nodal solve of the whole circuit, currents leaving each node, in volts,
kilohms and milliamps:

```
    node A:  (vA - 24)/4  +  vA/12  +  2.00  +  (vA - vB)/3  =  0
    node B:  (vB - vA)/3  +  vB/2                            =  0

    clear B by 6:   2(vB - vA) + 3vB = 0        ->  5vB = 2vA
    clear A by 12:  3(vA - 24) + vA + 24 + 4(vA - vB) = 0
                    8vA - 4vB = 48              ->  2vA - vB = 12

    substitute:     2vA - 0.4vA = 12            ->  vA = 7.50 V
                                                    vB = 3.00 V
    P(R4)  =  3.00^2/2000                       =  4.50 mW    agrees
```

Two equations and a substitution, against one superposition and one divider. They cost
about the same here, and they stop costing the same the moment a second load value is
asked about.

One thing in that solve is worth looking at twice. Node A sits at 7.50 V with the load
fitted, and $V_{Th}$ came out at 12.0 V — the voltage node A sits at with the load
*removed*. Those are different numbers for the same point, and both are correct: the load
pulls the node down by 4.50 V, which is exactly the 1.50 mA it draws flowing through the
3.00 kΩ that $R_{Th}$ is made of on that side. If your $V_{Th}$ ever comes out equal to a
node voltage measured with the load still connected, the load has not really been lifted
out.
''',
                },
                {
                    "title": "How far up must the supply go for the best possible load?",
                    "minutes": 13,
                    "brief": r'''
The hardest arrangement in this module, and the answer is not a voltage anywhere in the
drawing — it is a setting on the front of the supply.

Nothing at all is connected to the terminals: the load has not been chosen yet, and
choosing it is part of the question. Work out what the terminals look like as they stand,
decide which load takes the most power from that, and then ask how far the supply has to
be turned up for that best load to reach the figure specified below.

Read the required power off the panel, not off the drawing. The drawing shows the circuit
as it is now, and as it is now it does not meet the specification.
''',
                    "prompt": "What must the supply be set to so that the best possible load takes exactly 15.0 mW?",
                    "note": "Give the answer in volts, to one decimal place. Every resistance stays "
                            "where it is.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 3000},
                            {"id": "p2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "p3", "kind": "R", "x": 15, "y": 6, "value": 2000},
                            {"id": "p4", "kind": "R", "x": 19, "y": 8, "rot": 1, "value": 6000},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 11},
                            {"id": "o0", "kind": "OUT", "x": 22, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 9], "b": [11, 11]},
                            {"a": [11, 6], "b": [14, 6]},
                            {"a": [16, 6], "b": [19, 6]},
                            {"a": [19, 6], "b": [19, 7]},
                            {"a": [19, 9], "b": [19, 11]},
                            {"a": [19, 6], "b": [22, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, at present", "value": "12.0 V, adjustable"},
                        {"label": "R1, supply down to node A", "value": "3.00 kΩ"},
                        {"label": "R2, node A down to ground", "value": "6.00 kΩ"},
                        {"label": "R3, node A across to node B", "value": "2.00 kΩ"},
                        {"label": "R4, node B down to ground", "value": "6.00 kΩ"},
                        {"label": "Connected to the terminals", "value": "nothing yet"},
                        {"label": "Required power in the best load", "value": "15.0 mW"},
                    ],
                    "aside": "R4 belongs to the network, not to the load — it is soldered down and "
                             "stays put whether a load is fitted or not, so it counts in both $V_{Th}$ "
                             "and $R_{Th}$. The best load is the one this module's derivation names, "
                             "and the power it receives is $V_{Th}^2/4R_{Th}$.",
                    "answer": 30.0,
                    "tol": 0.2,
                    "unit": "V",
                    # The probe is on the open terminals, so vout() is V(Th) at the setting drawn;
                    # R(Th) is built from the resistor values as declared, in the topology drawn.
                    # One source and a linear network, so power goes as the square of the setting
                    # and the factor to apply is a square root.
                    "check": r'''
const vth = c.vout();
const R = c.values('R');
const back = R[0] * R[1] / (R[0] + R[1]) + R[2];
const rth = back * R[3] / (back + R[3]);
const now = vth * vth / (4 * rth);
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
return src.value * Math.sqrt(0.015 / now);
''',
                    "hint": "Three things, in order. $V_{Th}$ at the setting drawn: with the terminals "
                            "open, R3 carries no current, so node B sits at whatever R4 divides down "
                            "from node A. $R_{Th}$: kill the supply, then R1 beside R2, plus R3, all "
                            "beside R4. Then $P_{max} = V_{Th}^2/4R_{Th}$ at the present setting, and "
                            "one source in a linear network means every power scales as the square of "
                            "the supply.",
                    "wrong": "If you got 12.0, that is the setting the circuit is drawn at, where the "
                             "best load takes 2.40 mW rather than 15.0. If you got 75.0, the supply has "
                             "been scaled in proportion to the power — but power goes as the "
                             "*square* of the voltage, so the factor is $\\sqrt{15.0/2.40} = 2.50$, not "
                             "$15.0/2.40$. If you got 38.7, $R_{Th}$ has been taken as 4.00 kΩ with R4 "
                             "left out of it; R4 is soldered to the network and stays there whether a "
                             "load is fitted or not. If you got 15.0, the factor of four in "
                             "$V_{Th}^2/4R_{Th}$ has gone missing.",
                    "why": r'''
```
STEP 1 - V(Th) at the setting drawn.  Nothing is connected, so R3
carries no current and node B is simply R4's share of node A.

    from node A, the right-hand branch is R3 + R4
              =  2.00 + 6.00                    =  8.00 kohm
    beside R2:   (8.00 * 6.00)/14.0             =  3.4286 kohm
    with R1:      3.00 + 3.4286                 =  6.4286 kohm
    supply current  =  12.0 / 6.4286            =  1.8667 mA
    node A          =  12.0 - 1.8667 * 3.00     =  6.400 V
    node B          =  6.400 * 6.00/8.00        =  4.800 V   <- V(Th) at 12.0 V

STEP 2 - R(Th).  Kill the supply and look in from the terminals.

    R1 || R2  =  (3.00 * 6.00)/9.00             =  2.00 kohm
    + R3      =  2.00 + 2.00                    =  4.00 kohm
    || R4     =  (4.00 * 6.00)/10.0             =  2.40 kohm

STEP 3 - the best load is R(Th) itself, 2.40 kohm, and it takes

    P(max)  =  V(Th)^2 / (4 R(Th))
            =  4.800^2 / (4 * 2400)             =  2.40 mW   at 12.0 V

STEP 4 - scale.  One source in a linear network, so every voltage is
proportional to the setting and every power to its square.

    power ratio needed  =  15.0 / 2.40          =  6.25
    voltage ratio       =  sqrt(6.25)           =  2.50
    supply              =  12.0 * 2.50          =  30.0 V
```

Confirm it forwards, which is quick because nothing but the supply has changed. At 30.0 V
the network is $4.800 \times 2.50 = 12.0$ V behind the same 2.40 kΩ. Fit the matched
2.40 kΩ load and it sees half of that, 6.00 V, drawing
$12.0/(2.40 + 2.40) = 2.50$ mA — so $6.00 \times 2.50 = 15.0$ mW. Exactly the
specification.

Three separate ideas had to be right at once for that to work, and it is worth naming
them. $R_{Th}$ includes R4, because R4 is part of the network and not part of the load —
leave it out and you get 4.00 kΩ and a wrong answer. The best load is $R_{Th}$ rather than
anything read off the drawing. And the last step is a square root rather than a
multiplication, because the thing being specified is a power while the thing being
adjusted is a voltage.

That scaling shortcut is worth being careful with. It works because the network is linear
and has exactly one source. Put a second source in — a bias rail, a sensor, a chip drawing
current — and it fails outright, because scaling one of two sources does not scale the
answer. Then there is no shortcut: work out $V_{Th}$ as a function of the setting by
superposition, and solve.
''',
                },
            ],
            "tune": {
                "title": "Match a load, and get 20 mW out of it",
                "minutes": 10,
                "brief": r"""
A 12 V bench supply with a resistor in series stands in for a real source: $R_1$ is the
source's own resistance and $R_2$ is the load hung on it. Both are yours to specify,
which is what makes this a design rather than a reading.

Two requirements, pulling in different directions. The load must be **matched** —
taking the most power this source can give it, which happens when it sees exactly half
the open-circuit voltage — and the power it takes must be at least 20 mW. The first
requirement fixes the *ratio* of the two resistors and says nothing about their size;
the second says they cannot both be large.
""",
                "prompt": "Match the load to the source, and draw at least 3.40 mA doing it.",
                "note": "The dashed line marks the matched output, half of the 12 V rail. Both constraints must hold together.",
                "model": "divider",
                "initial": {"r1": 4700, "r2": 2200},
                "constants": {"vin": 12},
                "plotKey": "vout",
                "constraints": [
                    {"k": "vout", "label": "Vout = 6.00 V ± 0.05 — matched", "eq": 6.0, "tol": 0.05},
                    {"k": "i", "label": "I ≥ 3.40 mA, so the load takes over 20 mW", "min": 3.40},
                ],
            },
            "derive": {
                "title": "The matched load, without calculus",
                "minutes": 14,
                "vars": ["V", "R_t", "R_L", "P", "D"],
                "brief": r'''
A source with open-circuit voltage $V$ and internal resistance $R_t$ — the Thévenin
equivalent of anything at all — drives a load $R_L$. Which load takes the most power?

The usual derivation differentiates and sets the result to zero. This one does not need
to: the algebra alone settles it, and it tells you more on the way.
''',
                "steps": [
                    {
                        "prompt": "Write the current in the loop, in terms of $V$, $R_t$ and $R_L$.",
                        "answer": "\\frac{V}{R_t+R_L}",
                        "hint": "One loop, two resistances in series, and the whole of $V$ across the pair.",
                    },
                    {
                        "prompt": "The power in the load is that current squared times $R_L$. Write $P$ in terms of $V$, $R_t$ and $R_L$.",
                        "answer": "\\frac{V^{2} R_L}{(R_t+R_L)^{2}}",
                        "hint": "Square the current — both its top and its bottom — and multiply by $R_L$.",
                    },
                    {
                        "prompt": "Rewrite that as $P = V^2/D$, so that everything depending on the load is gathered into $D$. What is $D$?",
                        "answer": "\\frac{(R_t+R_L)^{2}}{R_L}",
                        "hint": "Divide the top and the bottom of your expression by $R_L$. $P$ is largest exactly when $D$ is smallest, and $D$ contains no $V$ at all.",
                    },
                    {
                        "prompt": "Expand $D$ and subtract $4R_t$ from it. Write $D - 4R_t$ as a single fraction.",
                        "answer": "\\frac{(R_L-R_t)^{2}}{R_L}",
                        "hint": "Expand the square on top and divide each term by $R_L$; then look at what taking $4R_t$ away leaves, and see whether it is a square over $R_L$.",
                        "deconstruct": [
                            "$D = \\frac{R_L^2 + 2R_tR_L + R_t^2}{R_L} = R_L + 2R_t + \\frac{R_t^2}{R_L}$.",
                            "Subtracting $4R_t$ leaves $R_L - 2R_t + \\frac{R_t^2}{R_L}$, and multiplying that by $R_L$ gives $R_L^2 - 2R_tR_L + R_t^2$, which is a perfect square.",
                        ],
                    },
                    {
                        "prompt": "So $D = 4R_t + (R_L-R_t)^2/R_L$, and that second term can never be negative. Which load makes it zero?",
                        "answer": "R_t",
                        "hint": "A square is zero only when the quantity being squared is zero.",
                    },
                    {
                        "prompt": "With that load in place, $D$ is at its smallest. Write the power the load then receives, in terms of $V$ and $R_t$.",
                        "answer": "\\frac{V^{2}}{4R_t}",
                        "hint": "Put the minimum value of $D$ back into $P = V^2/D$.",
                    },
                ],
                "closing": r'''
The rearranged form says more than the answer does. Because
$D = 4R_t + (R_L-R_t)^2/R_L$, the power falls away only *slowly* on either side of the
match: a load 20% too large costs about 0.8% of the available power. Matching in
practice is therefore a rough business, not a precise one, and nobody chooses a
resistor to three figures for it.

It also says that $V^2/4R_t$ is a ceiling nothing can get past. However clever the load,
a source cannot be made to give up more than that, and the only way to raise the
ceiling is to lower $R_t$ — which is a statement about the source, and about half of
what analogue design is.
''',
            },
            "lab": {
                "title": "Two measurements, and every load answered",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
A sealed box with two terminals. You may measure its open-circuit voltage and its
short-circuit current, and from those two numbers alone you can predict what it will do
with any load ever connected to it. That is worth writing down once.

- `thevenin(voc, isc)` returns the tuple `(vth, rth)`.
- `load_voltage(vth, rth, rl)` returns the voltage across a load `rl`.
- `load_power(vth, rth, rl)` returns the power that load receives, in watts.
- `best_load(vth, rth)` returns `(rl, p)`: the load that takes the most power, and how
  much that is.

`load_power` should call `load_voltage` rather than rewrite the divider, and
`best_load` should use the result you derived rather than search for it.
''',
                "files": [{"name": "main.py", "content": r'''
"""Thevenin equivalents, and what any load will do with one."""


def thevenin(voc, isc):
    """(vth, rth) from an open-circuit voltage and a short-circuit current."""
    # TODO: vth is the open-circuit voltage; rth is what the short-circuit current implies.
    return (0.0, 0.0)


def load_voltage(vth, rth, rl):
    """Voltage across a load rl connected to this equivalent."""
    # TODO: one divider, with rth on top.
    return 0.0


def load_power(vth, rth, rl):
    """Power in watts delivered to that load."""
    # TODO: V squared over R, using the voltage the load actually sees.
    return 0.0


def best_load(vth, rth):
    """(rl, p) for the load that takes the most power."""
    # TODO: the matched load, and the power it receives.
    return (0.0, 0.0)


if __name__ == "__main__":
    vth, rth = thevenin(6.0, 0.0012)
    print("the box behaves as", vth, "V behind", rth, "ohms")
    print("into 5 k it gives", load_voltage(vth, rth, 5000.0), "V")
    print("which is", load_power(vth, rth, 5000.0), "W")
    print("and the best any load can do is", best_load(vth, rth))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Thevenin equivalents, and what any load will do with one."""


def thevenin(voc, isc):
    """(vth, rth) from an open-circuit voltage and a short-circuit current."""
    return (voc, voc / isc)


def load_voltage(vth, rth, rl):
    """Voltage across a load rl connected to this equivalent."""
    return vth * rl / (rth + rl)


def load_power(vth, rth, rl):
    """Power in watts delivered to that load."""
    v = load_voltage(vth, rth, rl)
    return v * v / rl


def best_load(vth, rth):
    """(rl, p) for the load that takes the most power."""
    return (rth, vth * vth / (4.0 * rth))


if __name__ == "__main__":
    vth, rth = thevenin(6.0, 0.0012)
    print("the box behaves as", vth, "V behind", rth, "ohms")
    print("into 5 k it gives", load_voltage(vth, rth, 5000.0), "V")
    print("which is", load_power(vth, rth, 5000.0), "W")
    print("and the best any load can do is", best_load(vth, rth))
'''}],
                "hints": [
                    "`thevenin` returns a tuple: the open-circuit voltage unchanged, and `voc / isc` for the resistance.",
                    "`load_voltage` is the divider formula with `rth` as the upper resistor: `vth * rl / (rth + rl)`.",
                    "`load_power` should call `load_voltage` and then use $V^2/R$ on the load — writing the whole squared expression out again is where sign and bracket errors come from.",
                    "`best_load` is `(rth, vth * vth / (4 * rth))`, straight from the derivation. No search is needed, and a search would only find the same answer more slowly.",
                ],
                "tests": [
                    {"name": "two measurements give the equivalent", "code": r'''
vth, rth = thevenin(10.0, 0.005)
assert abs(vth - 10.0) < 1e-12, f"vth is the open-circuit voltage, got {vth}"
assert abs(rth - 2000.0) < 1e-9, f"10 V over 5 mA is 2000 ohms, got {rth}"
'''},
                    {"name": "a 12 V rail divided by two 10 k resistors", "code": r'''
vth, rth = thevenin(6.0, 0.0012)
assert abs(vth - 6.0) < 1e-12, f"the midpoint of two equal resistors sits at half the rail, got {vth}"
assert abs(rth - 5000.0) < 1e-9, \
    f"shorting the midpoint leaves 12 V across the top 10 k, so 1.2 mA and rth = 5 k, got {rth}"
'''},
                    {"name": "a load is one divider away", "code": r'''
v = load_voltage(6.0, 5000.0, 5000.0)
assert abs(v - 3.0) < 1e-12, f"an equal load halves the open-circuit voltage, got {v}"
assert abs(load_voltage(6.0, 5000.0, 1e12) - 6.0) < 1e-6, \
    "a very light load should leave the open-circuit voltage almost untouched"
'''},
                    {"name": "the matched load takes 1.8 mW", "code": r'''
p = load_power(6.0, 5000.0, 5000.0)
assert abs(p - 0.0018) < 1e-12, f"3 V across 5 k is 1.8 mW, got {p}"
rl, best = best_load(6.0, 5000.0)
assert abs(rl - 5000.0) < 1e-9, f"the best load equals rth, got {rl}"
assert abs(best - 0.0018) < 1e-12, f"6 squared over 4 times 5000 is 1.8 mW, got {best}"
'''},
                    {"name": "nothing beats the matched load", "code": r'''
rl, best = best_load(9.0, 220.0)
for trial in [1.0, 10.0, 100.0, 200.0, 219.0, 221.0, 300.0, 1000.0, 1e5]:
    p = load_power(9.0, 220.0, trial)
    assert p <= best + 1e-12, \
        f"a {trial} ohm load took {p} W, which beats the supposed maximum {best} W"
assert abs(load_power(9.0, 220.0, rl) - best) < 1e-12, \
    "the power at the matched load should equal the maximum you report"
'''},
                ],
            },
        },
        # ---- M11 ----------------------------------------------------------
        {
            "title": "Wires, tolerances and the energy budget",
            "summary": "The last step from a correct calculation to a circuit that works: wire has resistance, resistors are not their printed value, and batteries run out.",
            "concepts": [
                "A wire is a resistor. Its resistance is $R = \\rho L/A$, and copper's resistivity is $1.68\\times10^{-8}$ Ω·m at 20 °C — so a metre of 0.5 mm² copper is about 34 mΩ, which is negligible at a milliamp and is 0.34 V at 10 A.",
                "The drop happens twice. Current goes out along one conductor and back along the other, so a cable whose cores are $r$ each costs the load $2Ir$, not $Ir$.",
                "A voltage measured to ground is not the voltage across the load when the return conductor has resistance, because the load's lower terminal is no longer at 0 V. Measure across the component, not from the component to ground.",
                "Resistors come from a preferred series with a tolerance attached: E24 steps by about 10% and is usually ±5%; E96 steps by about 2.4% and is ±1%. A '10 kΩ ±5%' part is anywhere between 9.5 and 10.5 kΩ, and a worst-case analysis assumes the least helpful value in that range.",
                "A ratio built from two resistors of the same tolerance is better than either part: two 10 kΩ ±5% resistors give a divider ratio of 0.5 with a worst-case error of ±5%, not ±10%, because the same part appears on the top and the bottom of the fraction.",
                "Resistance drifts with temperature. A metal-film part moves about 50 ppm/°C, so a 60 °C rise shifts it by 0.3% — small beside a 5% tolerance, and not small beside a 0.1% one.",
                "A cell is quoted in milliamp-hours: 2000 mAh at 100 mA is nominally 20 hours, less in practice because the terminal voltage sags as it empties. Efficiency is the fraction of the power drawn from the source that reaches the load, and everything else is warming something up.",
            ],
            "read": [
                {
                    "title": "The wire is not a wire",
                    "minutes": 15,
                    "body": r'''
On a schematic a wire is a line with no properties. Nothing is written on it, there is no
value to set, and two points joined by one are the same point — every calculation in this
course so far has quietly assumed exactly that. It is a good assumption most of the time.
It is never exactly true. Copper conducts well; it does not conduct perfectly. A wire is a
resistor whose value you did not choose and cannot see, and this reading is about the
places where that hidden resistor is large enough to change the answer.

## Where the formula comes from

Take a bar of some material, length $L$, uniform cross-section $A$, and push a current
through it end to end. Two facts about its resistance follow from module 3 with no new
physics at all.

Join two identical bars end to end. The same current has to pass through both, so they
are in series and their resistances add. Twice the length, twice the resistance:
$R \propto L$.

Now lay two identical bars side by side and join their ends together. Both have the same
voltage across them, so they are in parallel and their conductances add. Twice the area,
half the resistance: $R \propto 1/A$.

Put the two together and everything that is left over — everything about the *material*
rather than about its shape — collects into a single constant:

$$R = \rho\,\frac{L}{A}$$

That constant $\rho$ is the **resistivity**, and its units drop straight out of the
formula: ohms times metres squared, divided by metres, is $\Omega\cdot\text{m}$. Read it
as the resistance of a one-metre cube measured face to face. Nobody has ever measured
one, but it fixes the number, and the number is all that separates a busbar from a
heating element.

```text
    material              rho at 20 C (ohm.m)     relative to copper
    silver                  1.59e-8                   0.95
    copper                  1.68e-8                   1
    aluminium               2.65e-8                   1.6
    tin/lead solder         1.5e-7                    9
    stainless steel         6.9e-7                    41
    nichrome                1.1e-6                    65
```

Two of those rows are design decisions rather than trivia. Aluminium is worse than copper
per unit volume and better per unit *mass*, which is why every overhead transmission line
in the world is aluminium and no household cable is. Nichrome is sixty-five times worse
than copper, which is why a toaster element is nichrome: a heating element is a resistor
you wanted.

Rather than reaching for $\rho$ each time, carry one number. A metre of 1 mm² copper is

```text
    R = 1.68e-8 * 1 / 1e-6  =  0.0168 ohm  =  16.8 milliohm
```

so **copper is about 17 mΩ per metre per square millimetre**: divide 16.8 by the area in
mm², multiply by the length in m, and you have milliohms. A metre of 0.5 mm² is 34 mΩ. A
metre of 2.5 mm² is 6.7 mΩ. A metre of 6 mm² is 2.8 mΩ.

## The cable is in the loop twice

Current does not arrive and stay. It goes out along one conductor and comes back along
the other, and both of them are copper. A cable whose cores are $r$ ohms each puts $2r$
in the loop, and the voltage the load loses is $2Ir$, not $Ir$.

This is the single most common error in the whole subject, and it is tempting for a
specific reason: the return conductor is usually drawn as a ground symbol at each end
rather than as a wire. Two ground symbols look like the same node. They are the same
*net*, and in a circuit carrying real current they are not the same *potential*.

## Worked: five amps down ten metres

A 12.0 V supply feeds a light bar that draws 5.00 A. The cable is ten metres of two-core
1.5 mm², which is an ordinary choice and looks harmless.

```text
    per core:   R = 1.68e-8 * 10 / 1.5e-6      =  0.112 ohm
    in the loop: 2 * 0.112                     =  0.224 ohm

    lost in the cable:  5.00 * 0.224           =  1.12 V
    left at the load:   12.0 - 1.12            =  10.88 V      9.3% low

    the cable burns:    5.00 * 1.12            =  5.60 W
    the load receives:  5.00 * 10.88           =  54.4 W
    the supply delivers 5.00 * 12.0            =  60.0 W       so 90.7% arrives
```

Five and a half watts is being turned into warm cable, and the light bar is running at
91% of the voltage it was designed for. Now turn the problem round, which is how it is
actually met: suppose the drop must stay under 3% of 12.0 V, which is 0.36 V.

```text
    allowed loop resistance:  0.36 / 5.00      =  0.072 ohm
    allowed per core:         0.072 / 2        =  0.036 ohm
    area needed:  A = rho L / R
                    = 1.68e-8 * 10 / 0.036     =  4.67e-6 m^2  =  4.67 mm^2
```

4.67 mm² is not a size anyone sells, so you buy 6 mm² — the next one up — and check what
you actually got:

```text
    per core:   1.68e-8 * 10 / 6e-6            =  0.028 ohm
    drop:       5.00 * 2 * 0.028               =  0.28 V       2.3%
    cable burns 5.00 * 0.28                    =  1.40 W
```

Four times the copper for a quarter of the loss, which is the whole of cable sizing:
$P = I^2R$ and $R \propto 1/A$, so the wasted power falls in proportion to the metal you
pay for. There is no cleverness available and no other lever, except the one at the end
of this reading.

## Worked: the reading that changes when the motor starts

A 12.0 V board runs a motor drawing 2.00 A and, separately, a two-resistor divider of
10.0 kΩ and 10.0 kΩ that monitors the supply rail. Both return to the supply's negative
terminal along the *same* piece of copper — a shared ground track of 0.15 Ω. The divider's
midpoint goes to an ADC that measures against the supply's ground.

Call the shared return's far end, where the motor and the divider both sit, node G.
Everything that flows in either branch has to leave through the return, so

```text
    the divider draws under 0.600 mA, so the return carries
                               2.00 A + 0.0006 A          =  2.0006 A
    node G rises to            2.0006 * 0.15              =  0.300 V

    the divider still halves what is across it, but what is across it
    is 12.0 - 0.300 = 11.70 V, and it sits on top of node G:

    ADC sees  =  0.300 + 11.70/2                          =  6.150 V
```

The expected reading was 6.000 V. The ADC reads 6.150 V, is off by 150 mV — exactly half
the ground offset — and the number *moves* every time the motor starts and stops. The
supply has not moved at all. Nothing is broken. The reading is wrong because the two ends
of a piece of wire were assumed to be at the same voltage while two amps were going
through it.

The fix costs no components. Run the divider's return to the supply on its own conductor
rather than sharing the motor's. That conductor now carries 0.600 mA instead of 2.0006 A,
so even at the same 0.15 Ω it lifts node G by 90 µV and the error becomes 45 µV. Joining
each return separately at one point is called **star grounding**, and the reason it works
is entirely contained in $V = IR$: give the sensitive branch a conductor with almost no
current in it.

## The mistake, and why it is tempting

Two probes, not one. A voltmeter lead on the load's upper terminal, referred to ground,
does not measure the voltage across the load — it measures the load *plus* whatever the
return conductor has developed. In the worked build later in this module the probe reads
4.75 V while the load has 4.50 V across it, and both numbers are correct.

The reason this is tempting is that a schematic makes it look impossible. Ground is drawn
as one symbol, repeated, with no wire between the copies; there is nowhere for the extra
quarter-volt to be. And at a milliamp there genuinely is nowhere: 1 mA through 0.25 Ω is
250 µV, below the noise. The assumption is not wrong, it is *conditional*, and the
condition is the current.

## Where this stops holding

**Copper gets worse when it gets hot.** Its resistance rises about 0.393% per °C, so a
cable at 70 °C instead of 20 °C has 1.20 times the resistance it had on the data sheet,
and 20% more drop. A cable that is losing power is heating itself, so the drop you
calculate cold is always optimistic.

**The connectors are often larger than the wire.** A crimp, a screw terminal or a
connector pin runs a few milliohms when clean, and a corroded or loose one can run
hundreds. On a short run inside a box, $\rho L/A$ can be the smaller half of the total,
and no amount of thicker cable helps.

**At high frequency the area in the formula is not the area of the wire.** Alternating
current crowds towards the surface, to a depth of about 2.1 mm in copper at 1 kHz and
66 µm at 1 MHz. Above a megahertz or so a solid conductor is a hollow one as far as the
current is concerned, its resistance rises with $\sqrt{f}$, and for fast edges the loop's
*inductance* — around a microhenry per metre — matters far more than any of this.

**And over long distances you change the current instead of the copper.** The loss is
$I^2R$ but the power delivered is $VI$, so carrying the same power at ten times the
voltage is a tenth of the current and a hundredth of the loss. That is the entire reason
the grid runs at hundreds of kilovolts and steps down at the street, and it is the one
lever that beats buying more metal.
''',
                },
                {
                    "title": "What the data sheet does not promise",
                    "minutes": 16,
                    "body": r'''
Every number you have used in this course so far was exact. The 10 kΩ resistor was 10 kΩ,
the 5 V rail was 5 V, the battery lasted until you stopped caring. None of those is a
property of a real part. A resistor is a film of metal or carbon deposited on a ceramic
rod and then spiral-cut with a laser until a meter says stop, and the process lands *near*
a value rather than on it. What the manufacturer sells you is not a value; it is a value
and a promise about how far from it the part may be.

## Why the preferred values are spaced the way they are

If every part is within ±5% of its marking, then each marking covers a band of the number
line that is a fixed *fraction* wide — a factor of 1.05 above and 0.95 below — not a fixed
number of ohms. To cover the whole line with bands of constant fractional width, the
markings themselves must be in geometric progression. That is the whole design of the
E-series.

```text
    E24:  24 values per decade   step = 10^(1/24) = 1.1007    about 10%
          a 5% part spans 0.95x to 1.05x, and the next value up
          starts at 0.95 * 1.1007 = 1.0457x   -> the bands overlap

    E96:  96 values per decade   step = 10^(1/96) = 1.0243    about 2.4%
          a 1% part spans 0.99x to 1.01x, and the next value up
          starts at 0.99 * 1.0243 = 1.0140x   -> a 0.4% gap, and nobody minds
```

So E24 with ±5% and E96 with ±1% are not two arbitrary lists. Each is the coarsest set of
markings whose tolerance bands just about tile the line, which is why the tolerance and
the series always arrive together. When you cannot buy the value your algebra produced —
and you usually cannot — this is the reason.

One thing tolerance is *not*: a distribution. "±5%" is a guarantee about the boundary, not
a promise that the parts cluster in the middle. Manufacturers routinely measure a batch
and sell the best of it as 1% parts, so what is left and sold as 5% can have a hole where
the middle should be. Any argument that begins "the errors will mostly cancel" is
therefore unsafe unless you know how the parts were made.

## Worst-case analysis is a blunt instrument on purpose

The method: put every part at whichever end of its range makes the result worse, and see
whether the circuit still works. Two parts means four corners; usually only two are worth
evaluating, because you can see by inspection which way each one has to move.

Do a divider. Nominal output is $V_{in}R_2/(R_1+R_2)$, so the output rises when $R_2$ is
large and $R_1$ small, and falls at the opposite corner. Take two 10.0 kΩ ±5% parts on a
5.00 V rail:

```text
    highest:  5.00 * 10.5 / (9.5 + 10.5)   =  5.00 * 10.5/20.0  =  2.625 V
    lowest:   5.00 *  9.5 / (10.5 + 9.5)   =  5.00 *  9.5/20.0  =  2.375 V
    nominal                                                     =  2.500 V
```

±5%, not ±10%. Look at why: the two errors are equal and opposite, so the denominator
comes out at exactly 20.0 kΩ in both corners and only the numerator moved. The same part
value appears on the top and on the bottom of the fraction, and a ratio built from two
parts of the same tolerance is no worse than one of them.

That is a genuinely useful result, and it has a limit that is just as useful. Try a
divider that divides harder — 20.0 kΩ over 10.0 kΩ, ±1% parts, on the same 5.00 V rail,
nominal output 1.667 V:

```text
    highest:  5.00 * 10.10 / (19.80 + 10.10)  =  50.50/29.90  =  1.6890 V   +1.34%
    lowest:   5.00 *  9.90 / (20.20 +  9.90)  =  49.50/30.10  =  1.6445 V   -1.33%
```

1.33% from 1% parts. Not 1%, and not 2% either. The derivation unit in this module works
out where that number comes from; the answer is that the fractional error is
$2t\,R_1/(R_1+R_2)$, which is $t$ when the two resistors are equal and climbs towards
$2t$ as the divider divides harder. Check it: $2 \times 1\% \times 20/30 = 1.33\%$. A
ratio protects you completely only when it is a ratio of one to one.

## Worked: where the ratio does not save you at all

Set an LED's current with a series resistor. 5.00 V rail, an LED that sits somewhere near
1.8 V, a wanted 20.0 mA:

```text
    R = (5.00 - 1.8) / 0.0200  =  160 ohm      which is an E24 value, luckily
```

Now the corners, and this time there are three parts to move, not two: the rail is
specified ±5%, the resistor is ±5%, and the LED's forward voltage is quoted as
1.8 V ± 0.2 V, which is a bigger fraction than either.

```text
    most current:  rail high, Vf low, R low
        I = (5.25 - 1.6) / 152  =  3.65 / 152  =  24.0 mA

    least current: rail low, Vf high, R high
        I = (4.75 - 2.0) / 168  =  2.75 / 168  =  16.4 mA
```

16.4 mA to 24.0 mA from a design that says 20 mA on the drawing: roughly ±20%. Notice
which part did the damage. The resistor's own 5% is the *smallest* of the three
contributions, because the resistor is not part of a ratio here — nothing cancels it —
and because the 0.2 V of LED spread is being divided by only 3.2 V of headroom. Raise the
rail to 12 V and the same LED spread costs a third as much, which is exactly why LED
strings are run from a high rail or from a constant-current driver rather than from a
resistor on 5 V.

## Drift, and the second number on the data sheet

Tolerance is the value at the moment of manufacture, at 20 °C. Resistance also moves with
temperature, at a rate the data sheet calls the temperature coefficient, in parts per
million per degree.

```text
    metal film,   50 ppm/C, 60 C above calibration:  50e-6 * 60  =  0.0030  =  0.30%
    carbon film, 500 ppm/C, same 60 C:              500e-6 * 60  =  0.030   =  3.0%
```

Carbon film's coefficient is also negative — the part's value *falls* as it warms — while
metal film's is small and may be of either sign; the arithmetic above is the size of the
move, and the direction is a separate line on the data sheet.

Beside a 5% tolerance the metal-film figure is nothing. Beside a 0.1% precision divider it
is the dominant error, and it is why precision work either controls the temperature or
buys a *resistor network* — several resistors on one substrate, whose coefficients match,
so the drift cancels in the ratio the way the tolerance did. Note the condition hiding in
that sentence: the drifts cancel only if both parts are at the same temperature. A divider
with one resistor beside a hot regulator and the other across the board has no such
protection, and self-heating does the same thing on its own — a small surface-mount part
sitting in its own dissipation can run tens of degrees above the board it is soldered to.

## The energy budget, and what a milliamp-hour is not

A cell's capacity is quoted in milliamp-hours, and a milliamp-hour is exactly what it
says: one milliamp for one hour. It is a quantity of *charge* — 3.6 coulombs — and not a
quantity of energy. Energy is capacity times the voltage it comes out at, which is why a
2000 mAh AA alkaline (about 1.5 V) holds roughly 3 Wh and a 2000 mAh lithium cell (about
3.7 V) holds roughly 7.4 Wh. Comparing the mAh figures of two chemistries compares nothing
at all.

Worked, on a device that is entirely typical. A sensor node runs from a 3.00 V coin cell
rated 220 mAh. Its processor sleeps at 20.0 µA and wakes for 200 ms every 10.0 s, drawing
12.0 mA while awake.

```text
    duty cycle           =  0.200 / 10.0                    =  0.0200
    average current      =  0.0200 * 12.0 mA
                          + 0.980 * 20.0 uA
                         =  240 uA + 19.6 uA                =  259.6 uA
    life                 =  220 000 uAh / 259.6 uA          =  847 h  =  35.3 days
```

Now fit the battery monitor: two 10.0 kΩ resistors across the cell, so the processor can
read the remaining voltage. It is two components and nobody thinks about it.

```text
    divider current      =  3.00 / 20 000                   =  150 uA, always
    new average          =  259.6 + 150                     =  409.6 uA
    life                 =  220 000 / 409.6                 =  537 h  =  22.4 days
```

The monitor has taken 37% of the battery life, and it is drawing more than the whole rest
of the circuit averaged over time. Change it to two 1.0 MΩ resistors and it costs 1.5 µA,
which puts the life back to 843 h. The cost of that fix is module 10's subject: a
1 MΩ/1 MΩ divider has an output resistance of 500 kΩ, and an ADC's sample-and-hold cannot
charge from a source that stiff in the time it has — so the real design either puts a
capacitor across the lower resistor or switches the divider on with a transistor only
while sampling. All of that follows from noticing that two resistors have a running cost.

## Where this stops holding

**Worst case is deliberately pessimistic, and production does not use it alone.** With ten
independent parts, the chance of all ten sitting at their extreme corner at once is
negligible, so a manufacturer will combine tolerances as a root-sum-square instead and
accept a small failure rate. That is only legal when the parts really are independent and
their distributions are known — and binning, as above, is exactly what breaks both
assumptions. Worst case is what you use when the failure has to be impossible rather than
unlikely.

**Tolerance does not cover the rest of the part's life.** Ageing, humidity, mechanical
stress from the solder joint and repeated thermal cycling all move a resistor's value, and
precision parts quote a separate long-term stability figure for exactly that reason. A
0.1% part is 0.1% on the day it was tested.

**And a cell's capacity is a rating, not a promise.** The mAh number is measured at a
gentle, steady drain down to a stated cut-off voltage. Draw it faster and you get less:
the cell's own internal resistance — tens of ohms for a coin cell, rising as it empties —
turns a 12 mA pulse into a visible voltage dip, and the processor's brown-out detector may
call the cell flat while most of its charge is still in there. Cold does the same thing.
The budget above is the right first calculation and the right thing to argue from; it is
not the number you will measure.
''',
                },
            ],
            "quiz": {
                "title": "The gap between the calculation and the bench",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A two-core 0.5 mm² copper cable, 2 m long, carries 3 A to a load. Roughly how much voltage is lost in the cable?",
                        "opts": ["about 0.20 V", "about 1.2 V", "about 0.40 V", "about 0.02 V"],
                        "a": 2,
                        "why": r'''
The current travels 2 m out and 2 m back, so 4 m of copper is in the loop:
$R = 1.68\times10^{-8} \times 4 / (0.5\times10^{-6}) = 0.134$ Ω, and at 3 A that is
0.40 V. Answering 0.20 V is the mistake of counting the cable once instead of twice —
one of the most common sources of a supply that reads correctly at the bench and low at
the load.
''',
                    },
                    {
                        "q": "You replace that cable with one of the same length but twice the cross-sectional area. What happens to the voltage lost in it at the same current?",
                        "opts": ["it halves", "it doubles", "it is unchanged", "it falls by a factor of four"],
                        "a": 0,
                        "why": r'''
$R = \rho L/A$, so doubling $A$ halves the resistance and halves the drop at a fixed
current. The power wasted in the cable falls by four, since $P = I^2R$ and the current
has not changed. That is the whole of cable sizing: the thing being bought with copper
is a smaller number in the denominator.
''',
                    },
                    {
                        "q": "A divider is built from two 10 kΩ ±5% resistors on a 5.00 V rail. What is the worst-case range of its output?",
                        "opts": [
                            "2.50 V ± 10%",
                            "2.50 V exactly — the tolerances cancel completely",
                            "2.50 V ± 5%",
                            "2.50 V ± 2.5%",
                        ],
                        "a": 2,
                        "why": r'''
Push the top resistor to 9.5 kΩ and the bottom to 10.5 kΩ and the output is
$5 \times 10.5/20 = 2.625$ V; the opposite corner gives 2.375 V. That is ±5%, the same
as one resistor's tolerance rather than the sum of two, because both parts moving
together leaves the ratio alone and only their *difference* matters. They do not cancel
entirely, though — that would need the two errors to be identical, which is only true
of resistors made on the same substrate, and is exactly why a resistor network in one
package is worth paying for.
''',
                    },
                    {
                        "q": "A load draws 1 A down a cable whose return conductor has 0.25 Ω. A probe on the load's upper terminal, measured to ground, reads 4.75 V. What is actually across the load?",
                        "opts": ["4.75 V", "5.00 V", "4.50 V", "4.25 V"],
                        "a": 2,
                        "why": r'''
4.50 V. The load's lower terminal is not at ground: 1 A through the 0.25 Ω return
conductor lifts it to 0.25 V, and the voltage across the load is the difference between
its two ends, $4.75 - 0.25$. Every ground on the schematic is drawn as the same symbol,
which quietly suggests they are the same potential — and in any circuit carrying real
current they are not. Measuring across the component instead of from the component to
ground is the whole of the fix.
''',
                    },
                    {
                        "q": "A 2000 mAh cell runs a circuit that draws a steady 250 mA. Roughly how long before it is flat?",
                        "opts": ["8 hours", "80 hours", "0.8 hours", "500 hours"],
                        "a": 0,
                        "why": r'''
$2000/250 = 8$ hours, and the arithmetic is that simple because a milliamp-hour is
literally a milliamp for an hour. In practice it will be a little less: the rating is
quoted at a gentle discharge, the terminal voltage sags as the cell empties, and most
circuits stop working before the cell is truly finished. It is a budget, not a promise
— but it is the number every battery-powered design starts from.
''',
                    },
                    {
                        "q": "A metal-film resistor is specified at 50 ppm/°C. It sits in an enclosure running 60 °C above the temperature it was calibrated at. How much has its value moved?",
                        "opts": ["3%", "0.05%", "0.3%", "30%"],
                        "a": 2,
                        "why": r'''
$50\times10^{-6} \times 60 = 3\times10^{-3}$, which is 0.3%. Beside a 5% tolerance that
is nothing; beside a 0.1% precision divider it is the dominant error, and it is why
precision work either controls the temperature or uses parts whose coefficients are
matched so the drifts cancel in the ratio. The units are the whole question: parts per
million *per degree*, multiplied by degrees.
''',
                    },
                ],
            },
            "numeric": [
                {
                    "title": "How much resistance is hiding in the cable",
                    "minutes": 4,
                    "brief": r'''
The mechanical one, to get $R = \rho L/A$ under your fingers before anything is built on
top of it. One unknown, one rule, no circuit.

There is exactly one trap and it is the units. Cable is sold by cross-section in **square
millimetres**, because that is how it is drawn from the die; resistivity is quoted in
ohm-metres. One square millimetre is $10^{-6}$ square metres, not $10^{-3}$.
''',
                    "prompt": "What is the resistance of this single conductor, end to end?",
                    "note": "Give the answer in milliohms, to one decimal place.",
                    "figure": "One core of copper cable, 12.0 m long, of cross-sectional area "
                              "2.50 mm², at 20 °C. Nothing is connected to it; the question "
                              "is about the piece of metal on its own.",
                    "given": [
                        {"label": "Resistivity of copper at 20 °C", "value": "1.68×10⁻⁸ Ω·m"},
                        {"label": "Length", "value": "12.0 m"},
                        {"label": "Cross-sectional area", "value": "2.50 mm²"},
                    ],
                    "aside": "A useful number to carry: a metre of 1 mm² copper is 16.8 mΩ. "
                             "Divide that by the area in mm² and multiply by the length in metres "
                             "and you have the answer in milliohms without touching a power of ten.",
                    "answer": 80.6,
                    "tol": 0.3,
                    "unit": "mΩ",
                    "hint": "$A = 2.50\\ \\text{mm}^2 = 2.50\\times10^{-6}\\ \\text{m}^2$. Everything "
                            "else is one multiplication and one division.",
                    "wrong": "If you got 0.0806, that is the answer in ohms and the question asked "
                             "for milliohms. If you got 0.0806 *milliohms*, the area went in as "
                             "2.50×10⁻³ m² instead of 2.50×10⁻⁶ — a square millimetre is a "
                             "millimetre squared, so the conversion factor gets squared too, and "
                             "that is the mistake this question exists to catch.",
                    "why": r'''
```
A     = 2.50 mm^2  =  2.50e-6 m^2

R     = rho * L / A
      = 1.68e-8 * 12.0 / 2.50e-6
      = 2.016e-7 / 2.50e-6
      = 0.08064 ohm        =  80.6 milliohm
```

Eighty milliohms sounds like nothing, and at a milliamp it is nothing: 80 µV, which no
meter in the room would care about. At 20 A it is 1.6 V, and it is in the loop twice, so
it is 3.2 V — a quarter of a 12 V supply thrown away in cable that looks, on the drawing,
exactly like every other line.

That is the entire lesson of this module in one number. The resistance did not change; the
current did, and the current is what decides whether a wire is a wire or a resistor.
''',
                },
                {
                    "title": "Two cores and a load, in one loop",
                    "minutes": 6,
                    "brief": r'''
Now the same conductor in a circuit. The supply feeds the load down a two-core cable: the
current goes out along one core and comes back along the other, so both cores are in the
loop and both are drawn.

One loop means one current, everywhere in it. Add up what is in the loop and use Ohm's
law once.
''',
                    "prompt": "What current flows round the loop?",
                    "note": "Give the answer in amps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 6, "y": 5, "value": 0.2},
                            {"id": "p2", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 5.6},
                            {"id": "p3", "kind": "R", "x": 10, "y": 9, "value": 0.2},
                            {"id": "o0", "kind": "OUT", "x": 15, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 10]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                            {"a": [11, 9], "b": [13, 9]},
                            {"a": [3, 9], "b": [9, 9]},
                            {"a": [13, 5], "b": [15, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "Feed core", "value": "0.200 Ω"},
                        {"label": "Load", "value": "5.60 Ω"},
                        {"label": "Return core", "value": "0.200 Ω"},
                    ],
                    "aside": "0.200 Ω is about twelve metres of 1 mm² copper, which is an "
                             "unremarkable length of cable. The return core is drawn along the "
                             "bottom rather than replaced by a ground symbol, because that is what "
                             "is physically there.",
                    "answer": 2.0,
                    "tol": 0.02,
                    "unit": "A",
                    # The source's own value and the current the solver puts through it are both
                    # read back out of the solve, so a re-valued schematic is re-measured rather
                    # than compared with the numbers written here.
                    "check": r'''
const d = c.dc();
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
return Math.abs(d.currents[src.id]);
''',
                    "hint": "Three things in series carry the same current. Add all three "
                            "resistances — both cores and the load — and divide the supply "
                            "voltage by the total.",
                    "wrong": "If you got 2.07, only one core went into the total: the cable is in "
                             "the loop twice. If you got 2.14, neither core did.",
                    "why": r'''
```
    R(loop)  =  0.200 + 5.60 + 0.200            =  6.00 ohm
    I        =  12.0 / 6.00                     =  2.00 A
```

Worth following through, because the next two questions live here. At 2.00 A each core
drops $2.00 \times 0.200 = 0.400$ V, so the cable eats 0.800 V and the load gets
$12.0 - 0.800 = 11.2$ V — check it directly with Ohm's law:
$2.00 \times 5.60 = 11.2$ V, which agrees.

Now look at the probe. It sits on the load's *upper* terminal and reads that node against
ground, so it reads $12.0 - 0.400 = 11.6$ V, which is neither the supply voltage nor the
load voltage. The missing 0.400 V is the return core, sitting between the load's lower
terminal and ground. One probe cannot give you the voltage across a component; a voltage
across something is a difference between two points, and this is the circuit where that
stops being pedantry.
''',
                },
                {
                    "title": "What the cable costs in watts",
                    "minutes": 7,
                    "brief": r'''
Same shape, more current, and the question is about heat rather than voltage. The wasted
power is the number that decides whether a cable is merely inefficient or actually
dangerous, and it is the one that grows fastest: $P = I^2R$, so doubling the current
quadruples it.

Both cores are warm, not one.
''',
                    "prompt": "How much power is dissipated in the cable — both cores together?",
                    "note": "Give the answer in watts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 11},
                            {"id": "p1", "kind": "R", "x": 7, "y": 6, "value": 0.3},
                            {"id": "p2", "kind": "R", "x": 13, "y": 7, "rot": 1, "value": 5.4},
                            {"id": "p3", "kind": "R", "x": 7, "y": 10, "value": 0.3},
                            {"id": "o0", "kind": "OUT", "x": 15, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [6, 6]},
                            {"a": [8, 6], "b": [13, 6]},
                            {"a": [13, 6], "b": [15, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [8, 10], "b": [13, 10]},
                            {"a": [3, 10], "b": [6, 10]},
                            {"a": [3, 8], "b": [3, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "24.0 V"},
                        {"label": "Each core of the cable", "value": "0.300 Ω"},
                        {"label": "Load", "value": "5.40 Ω"},
                    ],
                    "aside": "There are three routes to this and they agree: $I^2R$ on the pair, "
                             "the cable's voltage times the current, or what the supply delivers "
                             "minus what the load receives. Doing two of them is the cheapest check "
                             "you will ever run.",
                    "answer": 9.6,
                    "tol": 0.05,
                    "unit": "W",
                    # "The cable" is every resistance that is not the load, and the load is
                    # identified as the largest resistance in the drawing rather than by its
                    # value, so the measurement follows a re-valued schematic instead of this text.
                    "check": r'''
const d = c.dc();
const rs = c.net.parts.filter(function (p) { return p.kind === 'R'; });
const load = rs.reduce(function (m, p) { return p.value > m.value ? p : m; });
let w = 0;
rs.forEach(function (p) {
  if (p === load) return;
  const dv = d.v[p.n1] - d.v[p.n2];
  w += dv * dv / p.value;
});
return w;
''',
                    "hint": "Find the loop current first — all three resistances are in series. "
                            "Then the cable's share of the heat is $I^2$ times the cable's share of "
                            "the resistance.",
                    "wrong": "If you got 4.80, that is one core. If you got 86.4, that is the load's "
                             "power rather than the cable's. If you got 96.0, that is everything the "
                             "supply delivers, and the load has not been taken off it.",
                    "why": r'''
```
    R(loop)   =  0.300 + 5.40 + 0.300          =  6.00 ohm
    I         =  24.0 / 6.00                   =  4.00 A

    R(cable)  =  0.300 + 0.300                 =  0.600 ohm
    P(cable)  =  I^2 R  =  4.00^2 * 0.600      =  9.60 W
```

Check it the other two ways. The cable drops $4.00 \times 0.600 = 2.40$ V, and
$2.40 \times 4.00 = 9.60$ W. And the supply hands over $24.0 \times 4.00 = 96.0$ W while
the load takes $4.00^2 \times 5.40 = 86.4$ W, leaving $96.0 - 86.4 = 9.60$ W with nowhere
else to go. Three routes, one number, and energy conserved.

Nine and a half watts is a hot cable. Notice how quickly it arrived: the same cable at
2.00 A would dissipate $2.00^2 \times 0.600 = 2.40$ W, a quarter as much, because the
current is squared and the resistance never changed. It is also worth seeing what fraction
this is — 9.60 W out of 96.0 W is exactly 10% of everything the supply produces, thrown
away as warmth in a component nobody drew a symbol for.
''',
                },
                {
                    "title": "How long the cell lasts once the monitor is fitted",
                    "minutes": 8,
                    "brief": r'''
No circuit theory here beyond Ohm's law, and it is still the question that kills more
battery-powered designs than any other: what is the *average* current, counting everything
that is connected, and how long does the cell hold out against it.

Two contributions. One is the processor, which is asleep almost all the time. The other is
a two-resistor divider that monitors the battery voltage, and which is never asleep at
all.
''',
                    "prompt": "How long will the cell last?",
                    "note": "Give the answer in hours, to the nearest hour.",
                    "figure": "A sensor node runs from a 3.00 V coin cell rated at 220 mAh. Its "
                              "processor sleeps at 20.0 µA and wakes for 200 ms in every 10.0 s, "
                              "drawing 12.0 mA while it is awake. A battery monitor is wired "
                              "permanently across the cell: two 10.0 kΩ resistors in series, with "
                              "the junction going to the processor's analogue input, which draws "
                              "nothing.",
                    "given": [
                        {"label": "Cell", "value": "3.00 V, 220 mAh"},
                        {"label": "Sleep current", "value": "20.0 µA"},
                        {"label": "Awake current", "value": "12.0 mA"},
                        {"label": "Awake for", "value": "200 ms in every 10.0 s"},
                        {"label": "Monitor divider", "value": "10.0 kΩ + 10.0 kΩ"},
                    ],
                    "aside": "A milliamp-hour is a milliamp for an hour, so mAh divided by mA is "
                             "hours with no conversion at all — as long as every current in the "
                             "sum has been put into the same prefix first.",
                    "answer": 537.0,
                    "tol": 3.0,
                    "unit": "h",
                    "hint": "Three steps. The duty cycle is 0.200/10.0. The processor's average is "
                            "the awake current times the duty cycle plus the sleep current times "
                            "the rest of the time. The divider's current is 3.00 V across 20.0 kΩ, "
                            "and it never stops.",
                    "wrong": "If you got 847, the divider was left out — and it is drawing more "
                             "than the processor. If you got 564, the sleep current was dropped as "
                             "too small to matter, and it is a twentieth of the total rather than "
                             "nothing. If you got 18.1, the 12.0 mA was treated as continuous.",
                    "why": r'''
```
duty cycle          =  0.200 / 10.0                      =  0.0200

processor, averaged over a whole cycle:
    awake           =  0.0200 * 12.0 mA                  =  240.0 uA
    asleep          =  0.9800 * 20.0 uA                  =   19.6 uA
                                                            -------
                                                            259.6 uA

the monitor, which is on all the time:
    divider         =  3.00 V / 20 000 ohm               =  150.0 uA

total average       =  259.6 + 150.0                     =  409.6 uA

life                =  220 000 uAh / 409.6 uA            =  537 h   (22.4 days)
```

Look at what the two resistors did. Without them the node averages 259.6 µA and lasts
847 hours — 35 days. With them it lasts 537 hours, so a component pair that nobody thinks
about twice has taken 37% of the battery life, and is drawing more current on its own than
the entire processor averaged over time.

The fix is to make the divider a hundred times weaker: two 1.0 MΩ resistors draw 1.5 µA
and the life goes back to 843 hours. That is not free either — a 1 MΩ/1 MΩ divider has an
output resistance of 500 kΩ, which is far too soft for an analogue-to-digital converter to
charge in the microsecond it has, so the real design adds a capacitor across the lower
resistor or switches the divider on only while it is being read. But the first step is
always this arithmetic: put every permanent current in one column and add it up, including
the ones that were drawn as an afterthought.
''',
                },
                {
                    "title": "The reading that moves when the heater turns on",
                    "minutes": 10,
                    "brief": r'''
The hardest one here, and the one that is met on a real bench most often. A 12.0 V supply
runs two things at once: a heater element, and a 10 kΩ/10 kΩ divider that monitors the
rail. Both return to the supply's negative terminal down the **same** conductor, and that
conductor is a real 0.100 Ω of copper rather than the perfect short a ground symbol
implies.

The divider still halves whatever is across it. What it is across, and what its lower end
is sitting at, are the two things the question is really about — so there are two unknown
node voltages here and neither can be written down without the other.

The naive answer is 6.00 V. It is wrong, and the size of the error is the point.
''',
                    "prompt": "What voltage does the probe read at the divider's midpoint, measured against the supply's ground?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 13},
                            {"id": "p1", "kind": "R", "x": 7, "y": 9, "rot": 1, "value": 5.9},
                            {"id": "p2", "kind": "R", "x": 13, "y": 8, "rot": 1, "value": 10000},
                            {"id": "p3", "kind": "R", "x": 13, "y": 11, "rot": 1, "value": 10000},
                            {"id": "p4", "kind": "R", "x": 5, "y": 12, "value": 0.1},
                            {"id": "o0", "kind": "OUT", "x": 15, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 13]},
                            {"a": [3, 6], "b": [13, 6]},
                            {"a": [7, 6], "b": [7, 8]},
                            {"a": [13, 6], "b": [13, 7]},
                            {"a": [13, 9], "b": [13, 10]},
                            {"a": [13, 9], "b": [15, 9]},
                            {"a": [7, 10], "b": [7, 12]},
                            {"a": [7, 12], "b": [13, 12]},
                            {"a": [6, 12], "b": [7, 12]},
                            {"a": [3, 12], "b": [4, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "Heater element", "value": "5.90 Ω"},
                        {"label": "Shared return conductor", "value": "0.100 Ω"},
                        {"label": "Divider", "value": "10.0 kΩ + 10.0 kΩ"},
                    ],
                    "aside": "The divider's own current is around 0.6 mA and the heater's is around "
                             "2 A, so the return conductor is carrying essentially the heater's "
                             "current. That does not make the divider a bystander — its lower end "
                             "is tied to the top of that conductor.",
                    "answer": 6.1,
                    "tol": 0.01,
                    "unit": "V",
                    # The probe is the quantity the prompt asks for, so the check reads the probe.
                    # Nothing in the drawing is restated.
                    "check": r'''
return c.vout();
''',
                    "hint": "Call the top of the return conductor node G and work out its voltage "
                            "first: nearly all of the heater's current passes through 0.100 Ω to "
                            "get to ground. Then the divider's midpoint sits half of the remaining "
                            "rail *above* node G, not above ground.",
                    "wrong": "If you got 6.00, the return conductor was treated as a perfect ground "
                             "— which is what the two ground symbols on a schematic invite you to "
                             "do. If you got 5.90, the 0.200 V of ground offset was subtracted "
                             "instead of added, and half of it at that.",
                    "why": r'''
Two unknowns: the voltage at node G, where the heater and the divider both return, and the
voltage at the divider's midpoint. Start with the current, because the heater dominates it.

```
the divider draws under 0.6 mA, a three-thousandth of what the heater draws,
so leave it out of the current sum and put it back at the end:

    heater loop       =  5.90 + 0.100                   =  6.00 ohm
    heater current    =  12.0 / 6.00                    =  2.00 A
    node G            =  2.00 * 0.100                   =  0.200 V

what the divider is actually across:

    top of divider    =  12.0 V
    bottom of divider =  0.200 V   (node G, not ground)
    across it         =  12.0 - 0.200                   =  11.80 V

    midpoint          =  0.200 + 11.80/2                =  6.10 V
```

6.10 V, and the expected 6.00 V is out by 100 mV — exactly half the ground offset, because
the divider passes half of everything it sees and passes *all* of the offset its lower end
is sitting on. Solved exactly, node G is 0.20006 V and the midpoint 6.10003 V; the 0.6 mA
of divider current moves the fourth figure and nothing you would measure.

The important part is what happens next. Switch the heater off and the return conductor
carries 0.6 mA instead of 2 A, node G falls to 60 µV, and the same probe reads 6.00 V. The
supply has not moved. The divider has not changed. A monitor whose reading depends on what
else is running is worse than no monitor, and the cause is a hundred milliohms of copper
that the schematic drew as two identical ground symbols.

The fix is the one from the reading and it costs nothing: give the divider its own return
to the supply's terminal, so that conductor carries only the divider's 0.6 mA. At the same
0.100 Ω that is 60 µV of offset and a 30 µV error. Star grounding is not a rule of thumb —
it is $V = IR$ applied to the piece of the circuit nobody drew.
''',
                },
            ],
            "build": {
                "title": "The volt the cable ate",
                "minutes": 24,
                "brief": r'''
A 5.00 V supply feeds a load down a two-core cable. Each core has 0.25 Ω of resistance
— about seven and a half metres of 0.5 mm² copper, which is nothing unusual — and
the current goes out along one core and back along the other, so the cable counts
twice.

The canvas has the supply, the feed core, and a probe on the far end of it. Add the
**load** and the **return core**, so that

- the supply delivers exactly **1.00 A**, and
- the load itself has exactly **4.50 V** across it.

## The part that catches people

The probe reads the voltage of its node relative to ground, and the load's lower
terminal is no longer at ground — the return core has a quarter of a volt across it.
So the probe will read **4.75 V** even when the circuit is exactly right, and the extra
quarter-volt is the return core, not an error. The voltage across a component is the
difference between its two ends, and one probe cannot give you a difference.

Work out the load resistance from the total: 5.00 V has to push 1.00 A through the two
cores and the load in series.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "value": 0.25},
                        {"id": "p6", "kind": "OUT", "x": 11, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [11, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "value": 0.25},
                        {"id": "p3", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4.5},
                        {"id": "p4", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 0.25},
                        {"id": "p5", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p6", "kind": "OUT", "x": 11, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [9, 5], "b": [11, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 5 V supply, two cable cores and one load", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 5, 0.002, 'the supply voltage');
const rs = c.values('R');
c.assert(rs.length === 3,
  'Two cable cores and one load makes three resistors; found ' + rs.length + '.');
const cores = rs.filter(function (r) { return Math.abs(r - 0.25) <= 0.005; });
c.assert(cores.length === 2,
  'Both cores of the cable are 0.25 Ω, and the return core is as real as the feed. ' +
  'Found ' + cores.length + ' of them.');
'''},
                    {"name": "the supply delivers 1.00 A", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
c.close(Math.abs(cur[ids[0]]), 1.0, 0.01, 'the current round the loop');
'''},
                    {"name": "the load itself has 4.50 V across it", "code": r'''
const dc = c.dc();
const load = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 0.25) > 0.005;
});
c.assert(load.length === 1,
  'Exactly one resistor should be the load — the other two are the 0.25 Ω cores. ' +
  'Found ' + load.length + '.');
const dv = Math.abs(dc.v[load[0].n1] - dc.v[load[0].n2]);
c.close(dv, 4.5, 0.01,
  'the voltage across the load itself, measured between its two terminals');
'''},
                    {"name": "and the probe, measured to ground, reads 4.75 V", "code": r'''
c.close(c.vout(), 4.75, 0.01,
  'the probe reading — it is the load voltage plus the drop in the return core, and ' +
  'that difference is the whole point of the exercise');
'''},
                ],
                "hints": [
                    "The loop is two cores and the load in series. 5.00 V at 1.00 A means the whole loop is 5.00 Ω.",
                    "The two cores account for 0.50 Ω of that, so the load is 4.50 Ω — and 1 A through it is the required 4.50 V.",
                    "Place the return core between the bottom of the load and the ground symbol. Wiring the load straight to ground instead gives 1.05 A round the loop and about 4.74 V across the load, and both checks will say so.",
                    "The probe stays where it is, on the upper terminal of the load. It will read 4.75 V, and that is correct — the load's lower terminal is sitting 0.25 V above ground.",
                ],
            },
            "blanks": [{
                "title": "Worst case, corner by corner",
                "minutes": 9,
                "caption": "a 5 V divider from two 10 kΩ ±5% resistors",
                "lang": "text",
                "brief": r"""
Worst-case analysis is not statistics. It asks a blunt question — if every part were
as unhelpful as its data sheet permits, would the circuit still work? — and answers it
by putting each value at whichever end of its range makes the result worse.

Two resistors, so four corners, and only two of them are worth evaluating: the output
rises when the bottom resistor is large and the top one small, and falls when the
reverse is true.
""",
                "listing": """5.00 V rail.  R1 = 10 k on top, R2 = 10 k on the bottom, both +/- 5%.
Each may be anywhere from 9.5 k to 10.5 k.

nominal:          Vout = 5.00 * 10.0 / (10.0 + 10.0)  = 2.500 V

highest output:   R1 at its ___ , R2 at its ___
                  Vout = 5.00 * 10.5 / (9.5 + 10.5)   = ___ V

lowest output:    R1 at 10.5 k, R2 at 9.5 k
                  Vout = 5.00 * 9.5 / (10.5 + 9.5)    = ___ V
""",
                "blanks": [
                    {
                        "prompt": "For the highest possible output, which end of its range does the top resistor go to?",
                        "hole": "?",
                        "opts": ["minimum, 9.5 k", "maximum, 10.5 k", "nominal, 10 k"],
                        "a": 0,
                        "why": "The output is $V_{in}R_2/(R_1+R_2)$, which gets larger as $R_1$ gets "
                               "smaller — less voltage is dropped above the output node. So the top "
                               "resistor goes to 9.5 k, its minimum. Sending it to its maximum instead "
                               "produces the *lowest* output, which is the other corner and equally "
                               "worth knowing, just not this one.",
                    },
                    {
                        "prompt": "And the bottom resistor?",
                        "hole": "?",
                        "opts": ["minimum, 9.5 k", "nominal, 10 k", "maximum, 10.5 k"],
                        "a": 2,
                        "why": "To its maximum, 10.5 k. The output is measured across it, so the larger "
                               "its share of the total resistance the larger its share of the rail. The "
                               "two extremes have to be taken together: it is the *combination* of a "
                               "small top and a large bottom that produces the worst case, and moving "
                               "only one of them understates the spread by half.",
                    },
                    {
                        "prompt": "So what is the highest output the circuit can produce?",
                        "hole": "?",
                        "opts": ["2.500", "2.750", "2.625", "2.550"],
                        "a": 2,
                        "why": "$5.00 \\times 10.5/20.0 = 2.625$ V. Notice the denominator: the two "
                               "errors are equal and opposite, so the total is still exactly 20 k, "
                               "which is why the arithmetic comes out clean. The result is 5% above "
                               "nominal — the tolerance of one resistor, not of two.",
                    },
                    {
                        "prompt": "And the lowest?",
                        "hole": "?",
                        "opts": ["2.375", "2.250", "2.475", "2.400"],
                        "a": 0,
                        "why": "$5.00 \\times 9.5/20.0 = 2.375$ V, again 5% from nominal. So the output "
                               "is 2.50 V ± 5%: a divider is no worse than the parts it is made of, "
                               "even though it contains two of them. Had the two resistors been "
                               "specified with different tolerances, the spread would have been the "
                               "sum of the two halves rather than a symmetric 5%.",
                    },
                ],
            }, {
                "title": "The cable's share, line by line",
                "minutes": 8,
                "caption": "a 12 V supply, a two-core cable and a 5.6 ohm load",
                "lang": "text",
                "brief": r"""
The same circuit the numeric ladder opens with, worked out one line at a time. Every line
is either the series rule or Ohm's law, and the only place there is anything to think
about is the very first one.

Fill the holes and read down the column: what the supply gives, what arrives, and what is
left warming the copper in between.
""",
                "listing": """12.0 V supply.  Two-core cable, each core 0.200 ohm.  Load 5.60 ohm.

The cable is in the loop ___ times: out along one core, back along the other.

    R(loop)     =  ___  +  5.60                     =  6.00 ohm
    I           =  12.0 / 6.00                      =  ___ A
    V(load)     =  2.00 * 5.60                      =  11.2 V
    P(cable)    =  2.00^2 * ___                     =  1.60 W
    efficiency  =  11.2 / 12.0                      =  ___
""",
                "blanks": [
                    {
                        "prompt": "How many of the cable's cores are in the loop the current takes?",
                        "hole": "?",
                        "opts": ["one", "two", "four"],
                        "a": 1,
                        "why": "Two. Charge is not consumed at the load, so every amp that goes "
                               "out along the feed core comes back along the return core, and both "
                               "of them are copper with resistance. Counting the cable once is the "
                               "commonest error in this whole module, and it is tempting because "
                               "the return is usually drawn as a ground symbol at each end rather "
                               "than as a wire.",
                    },
                    {
                        "prompt": "So what does the cable contribute to the loop resistance?",
                        "hole": "?",
                        "opts": ["0.200", "0.400", "0.800"],
                        "a": 1,
                        "why": "0.400 Ω — two cores of 0.200 Ω each, in series with the load "
                               "because the same current passes through both of them. Using 0.200 "
                               "makes the loop 5.80 Ω and the current 2.07 A, which is close enough "
                               "to look right and wrong enough to matter at higher currents.",
                    },
                    {
                        "prompt": "And the current round the loop?",
                        "hole": "?",
                        "opts": ["2.00", "0.500", "2.14", "6.00"],
                        "a": 0,
                        "why": "$12.0/6.00 = 2.00$ A. One loop means one current: the same 2.00 A "
                               "is in the feed core, in the load and in the return core, which is "
                               "what lets a single division answer for all three. 2.14 A is the "
                               "answer with no cable resistance at all, $12.0/5.60$.",
                    },
                    {
                        "prompt": "The cable's heat is $I^2R$ — but which R?",
                        "hole": "?",
                        "opts": ["0.200, one core", "0.400, both cores", "5.60, the load", "6.00, the whole loop"],
                        "a": 1,
                        "why": "Both cores, 0.400 Ω: $2.00^2 \\times 0.400 = 1.60$ W. Using one "
                               "core gives half the heat and is the same miscount as before, one "
                               "step further on. Using 6.00 Ω gives 24.0 W, which is everything "
                               "the supply delivers rather than the part of it that is wasted.",
                    },
                    {
                        "prompt": "What fraction of the supply's power reaches the load?",
                        "hole": "?",
                        "opts": ["0.933", "0.800", "1.07"],
                        "a": 0,
                        "why": "$11.2/12.0 = 0.933$, so 93.3%. The voltages alone give the "
                               "efficiency here because the current is common to both — "
                               "$P_{load}/P_{total} = VI/(V_{s}I)$ and the $I$ cancels. Check it "
                               "against the watts: the supply gives $12.0 \\times 2.00 = 24.0$ W, "
                               "the load takes $11.2 \\times 2.00 = 22.4$ W, and $22.4/24.0$ is "
                               "the same 0.933 with 1.60 W left over in the copper.",
                    },
                ],
            }],
            "derive": {
                "title": "How much of a resistor's tolerance a ratio actually inherits",
                "minutes": 14,
                "vars": ["V", "R_1", "R_2", "R", "t"],
                "brief": r'''
Two equal resistors of ±5% make a divider that is ±5%, not ±10% — the quiz says so and
the arithmetic in the blanks confirms it. That is a genuinely surprising result and it is
usually left there, as a fact to remember, which is a shame: the reason is three lines of
algebra and the general answer is more useful than the special one.

$R_1$ is on top, $R_2$ underneath, the output is taken across $R_2$, and both parts have
the same fractional tolerance $t$ (so $t = 0.05$ means ±5%). Nothing else is uncertain.

Write each answer as an expression in the symbols named. Fractions are fine and preferred.
''',
                "steps": [
                    {
                        "prompt": "Start with the nominal case, every part exactly at its marking. Write the output voltage in terms of $V$, $R_1$ and $R_2$.",
                        "answer": "\\frac{V R_2}{R_1+R_2}",
                        "hint": "The two resistors are in series, so the same current passes through both; the output is that current times $R_2$.",
                        "deconstruct": [
                            "The current in the chain is $V/(R_1+R_2)$.",
                            "The output is across $R_2$, so it is that current times $R_2$.",
                        ],
                    },
                    {
                        "prompt": "Now the corner that makes the output as large as possible. Decide which way each part has to move, then write that highest output in terms of $V$, $R_1$, $R_2$ and $t$.",
                        "answer": "\\frac{V R_2 (1+t)}{R_1 (1-t) + R_2 (1+t)}",
                        "placeholder": "\\frac{V \\cdot \\ldots}{\\ldots + \\ldots}",
                        "hint": "The output grows when $R_2$ grows and shrinks when $R_1$ grows, so send $R_2$ to $R_2(1+t)$ and $R_1$ to $R_1(1-t)$ — and remember that $R_2$ appears in the denominator as well as the numerator.",
                        "deconstruct": [
                            "Replace $R_2$ everywhere by $R_2(1+t)$ and $R_1$ everywhere by $R_1(1-t)$.",
                            "The numerator becomes $V R_2(1+t)$ and the denominator $R_1(1-t)+R_2(1+t)$.",
                            "Only two of the four corners are worth evaluating; this is the upper one and the other is the same expression with the signs of $t$ swapped.",
                        ],
                    },
                    {
                        "prompt": "That denominator is doing all the interesting work. Multiply it out and collect the terms in $t$, writing it in terms of $R_1$, $R_2$ and $t$.",
                        "answer": "R_1 + R_2 + t(R_2 - R_1)",
                        "hint": "$R_1 - tR_1 + R_2 + tR_2$. Two of those four terms have no $t$ in them and two do.",
                        "deconstruct": [
                            "$R_1(1-t) + R_2(1+t) = R_1 - tR_1 + R_2 + tR_2$.",
                            "Group: $(R_1+R_2) + t(R_2-R_1)$.",
                            "Notice what that says: the total resistance only moves at all if the two resistors are unequal, because the errors are in opposite directions.",
                        ],
                    },
                    {
                        "prompt": "Divide the highest output by the nominal one to get the worst-case ratio — the factor the output can be above its marked value. Write it in terms of $R_1$, $R_2$ and $t$; $V$ cancels.",
                        "answer": "\\frac{(1+t)(R_1+R_2)}{R_1 + R_2 + t(R_2 - R_1)}",
                        "hint": "Dividing by $\\frac{V R_2}{R_1+R_2}$ is multiplying by $\\frac{R_1+R_2}{V R_2}$, and both $V$ and $R_2$ then cancel out of the numerator.",
                        "deconstruct": [
                            "$\\frac{V R_2 (1+t)}{(R_1+R_2)+t(R_2-R_1)} \\times \\frac{R_1+R_2}{V R_2}$.",
                            "$V$ and $R_2$ both cancel, leaving $(1+t)(R_1+R_2)$ over the shifted denominator.",
                        ],
                    },
                    {
                        "prompt": "Test it on the case you already know the answer to: two equal resistors, $R_1 = R_2 = R$. Write the ratio in terms of $t$ alone.",
                        "answer": "1+t",
                        "hint": "With $R_1 = R_2$ the bracket $(R_2-R_1)$ is zero, so the denominator is just $2R$ — and the numerator is $(1+t)\\,2R$.",
                        "deconstruct": [
                            "Denominator: $2R + t \\cdot 0 = 2R$.",
                            "Numerator: $(1+t)(2R)$.",
                            "So the ratio is exactly $1+t$: a divider from two equal parts of tolerance $t$ is out by $t$, not by $2t$, and the result is exact rather than an approximation.",
                        ],
                    },
                    {
                        "prompt": "Now the opposite extreme: a divider that divides very hard, so $R_2$ is negligible beside $R_1$. Put $R_2 = 0$ in the ratio and write what is left, in terms of $t$ alone.",
                        "answer": "\\frac{1+t}{1-t}",
                        "hint": "With $R_2 = 0$ the denominator becomes $R_1 + t(0 - R_1) = R_1(1-t)$, and the numerator becomes $(1+t)R_1$.",
                        "deconstruct": [
                            "Numerator: $(1+t)(R_1+0) = (1+t)R_1$.",
                            "Denominator: $R_1 + 0 + t(0-R_1) = R_1(1-t)$.",
                            "$R_1$ cancels, leaving $\\frac{1+t}{1-t}$ — which for small $t$ is about $1+2t$, twice the error of the equal-resistor case.",
                        ],
                    },
                ],
                "closing": r'''
Put the two extremes side by side. A divider made from two parts of tolerance $t$ is
somewhere between $t$ and $2t$ out, depending only on how hard it divides: $t$ when the
two resistors are equal, approaching $2t$ as the output ratio goes to zero. It is never
worse than $2t$, and it is never better than $t$.

The expression in between is worth expanding once. For small $t$,

$$\frac{(1+t)(R_1+R_2)}{(R_1+R_2)+t(R_2-R_1)}
\approx (1+t)\left(1 - t\,\frac{R_2-R_1}{R_1+R_2}\right)
\approx 1 + t\,\frac{2R_1}{R_1+R_2}$$

so the fractional error is $2t\,R_1/(R_1+R_2)$ — twice the tolerance, scaled by the share
of the chain that sits *above* the output. Check it against the reading's example: 20.0 kΩ
over 10.0 kΩ with ±1% parts gives $2 \times 0.01 \times 20/30 = 1.33\%$, and the exact
corners came out at +1.34% and −1.33%.

Two things follow that are worth carrying out of this course.

The first is a design move. If a divider's accuracy matters and its ratio is far from
one-to-one, you can buy back most of the error by splitting the top resistor into two in
series, or by choosing a ratio nearer 1:1 and amplifying afterwards. The error is not a
property of the parts alone; it is a property of the parts *and* the ratio you asked them
for.

The second is a warning about what this argument does **not** cover. Every line above
assumed both resistors have the same tolerance and the same temperature coefficient, and
that they are at the same temperature. Mix a 1% part with a 5% part and the cancellation
mostly disappears — the spread becomes roughly the sum of the two halves. Put one of them
next to a regulator that runs warm and the drift no longer cancels either. The saving is
real, and it is a saving on *matched* parts.
''',
            },
            "lab": {
                "title": "A budget for the cable, the parts and the battery",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
Four small functions, each answering a question that comes up in every design and is
answered wrongly in a surprising number of them.

- `wire_resistance(rho, length_m, area_mm2)` — the resistance of a conductor. Note the
  units: the area is given in **square millimetres**, because that is how cable is sold,
  and $\rho$ is in ohm-metres. Convert.
- `voltage_at_load(vs, r_core, r_load)` — the voltage across a load fed down a two-core
  cable whose cores are `r_core` each. The current goes out and comes back.
- `worst_case_divider(vin, r_top, r_bottom, tol)` — returns `(lowest, highest)`, the two
  extremes of the output when both resistors have the fractional tolerance `tol`.
- `runtime_hours(capacity_mah, current_ma)` — how long a cell lasts at a steady drain.

`worst_case_divider` is the one worth thinking about before typing. The output rises
when the bottom resistor is at its largest and the top at its smallest, and falls at the
opposite corner; the other two corners are never the extremes and do not need
evaluating.
''',
                "files": [{"name": "main.py", "content": r'''
"""Cable drop, part tolerance and battery life: the arithmetic of a real build."""


def wire_resistance(rho, length_m, area_mm2):
    """Resistance of a conductor. rho in ohm-metres, area in square millimetres."""
    # TODO: R = rho * L / A, with A converted from mm^2 to m^2 (1 mm^2 = 1e-6 m^2).
    return 0.0


def voltage_at_load(vs, r_core, r_load):
    """Voltage across a load fed down a two-core cable of r_core per core."""
    # TODO: the cable is in the loop twice — out along one core and back along the other.
    return 0.0


def worst_case_divider(vin, r_top, r_bottom, tol):
    """(lowest, highest) output of a divider whose resistors both have tolerance `tol`."""
    # TODO: the output is highest with r_top small and r_bottom large.
    return (0.0, 0.0)


def runtime_hours(capacity_mah, current_ma):
    """How long a cell of this capacity lasts at this steady current."""
    # TODO: a milliamp-hour is a milliamp for an hour.
    return 0.0


if __name__ == "__main__":
    r = wire_resistance(1.68e-8, 7.5, 0.5)
    print("7.5 m of 0.5 mm2 copper:", r, "ohms")
    print("a 1 A load at the end of it sees", voltage_at_load(5.0, r, 4.5), "V")
    print("a 10k/10k divider on 5 V, 5% parts:", worst_case_divider(5.0, 10000.0, 10000.0, 0.05))
    print("2000 mAh at 250 mA lasts", runtime_hours(2000.0, 250.0), "hours")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Cable drop, part tolerance and battery life: the arithmetic of a real build."""


def wire_resistance(rho, length_m, area_mm2):
    """Resistance of a conductor. rho in ohm-metres, area in square millimetres."""
    return rho * length_m / (area_mm2 * 1e-6)


def voltage_at_load(vs, r_core, r_load):
    """Voltage across a load fed down a two-core cable of r_core per core."""
    return vs * r_load / (2.0 * r_core + r_load)


def worst_case_divider(vin, r_top, r_bottom, tol):
    """(lowest, highest) output of a divider whose resistors both have tolerance `tol`."""
    hi = vin * (r_bottom * (1 + tol)) / (r_top * (1 - tol) + r_bottom * (1 + tol))
    lo = vin * (r_bottom * (1 - tol)) / (r_top * (1 + tol) + r_bottom * (1 - tol))
    return (lo, hi)


def runtime_hours(capacity_mah, current_ma):
    """How long a cell of this capacity lasts at this steady current."""
    return capacity_mah / current_ma


if __name__ == "__main__":
    r = wire_resistance(1.68e-8, 7.5, 0.5)
    print("7.5 m of 0.5 mm2 copper:", r, "ohms")
    print("a 1 A load at the end of it sees", voltage_at_load(5.0, r, 4.5), "V")
    print("a 10k/10k divider on 5 V, 5% parts:", worst_case_divider(5.0, 10000.0, 10000.0, 0.05))
    print("2000 mAh at 250 mA lasts", runtime_hours(2000.0, 250.0), "hours")
'''}],
                "hints": [
                    "In `wire_resistance`, one square millimetre is $10^{-6}$ square metres. Multiply the area by `1e-6` before dividing, and check the answer against 34 mΩ for a metre of 0.5 mm² copper.",
                    "`voltage_at_load` is a divider whose upper resistance is `2 * r_core` — the feed core and the return core are both in the loop.",
                    "For `worst_case_divider`, build the two corner values with `(1 + tol)` and `(1 - tol)` and return them smallest first. With equal nominal resistors the denominators come out identical, which is a useful check that you have picked opposite corners.",
                    "`runtime_hours` is one division, and the units are already consistent: mAh divided by mA is hours.",
                ],
                "tests": [
                    {"name": "a metre of 0.5 mm2 copper is 34 milliohms", "code": r'''
r = wire_resistance(1.68e-8, 1.0, 0.5)
assert abs(r - 0.0336) < 1e-9, f"1.68e-8 * 1 / 5e-7 is 0.0336 ohms, got {r}"
'''},
                    {"name": "resistance grows with length and falls with area", "code": r'''
a = wire_resistance(1.68e-8, 4.0, 0.5)
assert abs(a - 0.1344) < 1e-9, f"4 m of 0.5 mm2 is 0.1344 ohms, got {a}"
assert abs(a * 3.0 - 0.4032) < 1e-9, "at 3 A that cable loses about 0.40 V"
b = wire_resistance(1.68e-8, 4.0, 1.0)
assert abs(b - a / 2) < 1e-12, "doubling the area should halve the resistance"
'''},
                    {"name": "the cable is in the loop twice", "code": r'''
v = voltage_at_load(5.0, 0.25, 4.5)
assert abs(v - 4.5) < 1e-12, \
    f"0.25 + 4.5 + 0.25 is 5 ohms, so 1 A flows and the load sees 4.5 V, got {v}"
assert abs(voltage_at_load(5.0, 0.0, 4.5) - 5.0) < 1e-12, \
    "with no cable resistance the load should see the whole supply"
'''},
                    {"name": "a 5% divider is 5% out, not 10%", "code": r'''
lo, hi = worst_case_divider(5.0, 10000.0, 10000.0, 0.05)
assert abs(hi - 2.625) < 1e-12, f"5 * 10.5/20 is 2.625 V, got {hi}"
assert abs(lo - 2.375) < 1e-12, f"5 * 9.5/20 is 2.375 V, got {lo}"
assert abs((hi - 2.5) / 2.5 - 0.05) < 1e-12, "the spread should be 5%, not 10%"
'''},
                    {"name": "the corners are right for unequal resistors too", "code": r'''
lo, hi = worst_case_divider(5.0, 20000.0, 10000.0, 0.01)
assert abs(hi - 5.0 * 10100.0 / (19800.0 + 10100.0)) < 1e-12, \
    f"highest output wants the top resistor low and the bottom high, got {hi}"
assert abs(lo - 5.0 * 9900.0 / (20200.0 + 9900.0)) < 1e-12, \
    f"lowest output is the opposite corner, got {lo}"
nom, _ = worst_case_divider(5.0, 20000.0, 10000.0, 0.0)
assert abs(nom - 5.0 / 3.0) < 1e-12, "with zero tolerance both extremes are the nominal value"
'''},
                    {"name": "the battery budget", "code": r'''
assert abs(runtime_hours(2000.0, 250.0) - 8.0) < 1e-12, "2000 mAh at 250 mA is 8 hours"
assert abs(runtime_hours(2000.0, 20.0) - 100.0) < 1e-12, "and at 20 mA it is 100 hours"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A solver for any resistor network",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
Everything in this course has been a network simple enough to reduce by inspection.
Most networks are not, so engineers solve them a different way: write Kirchhoff's
current law at every node at once, and let linear algebra do the rest. That method is
called **nodal analysis**, and it is what every circuit simulator in the world does
underneath. You are going to write one.

## The idea, in one paragraph

Number the nodes. Ground is node 0 and its voltage is defined as 0 V. For every other
node, KCL says the currents leaving it through the resistors attached to it add up to
zero. The current leaving node $a$ towards node $b$ through a resistance $R$ is
$(v_a - v_b)/R$ by Ohm's law. Writing that out for every node gives one linear
equation per unknown voltage, and a linear system is something a computer solves
without thinking. Where a supply holds a node at a fixed voltage, that node's equation
is simply $v = V$, and it replaces the KCL equation there.

`dcsolve.py` gives you `linsolve(A, b)`, which solves $Ax = b$ by Gaussian
elimination. You do not need to read it, and you may not edit it. Your work is
building `A` and `b` from the circuit — the physics — and then reading useful
quantities back out.

## What you are building

Represent a circuit as

```text
n_nodes    how many non-ground nodes there are, numbered 1..n_nodes
resistors  a list of (a, b, ohms) triples; node 0 means ground
fixed      a dict {node: volts} of nodes held at a known voltage by a supply
```

Then implement, in `main.py`:

1. `solve_network(n_nodes, resistors, fixed)` — returns a list of voltages of length
   `n_nodes + 1`, with `voltages[0] == 0.0` for ground.
2. `branch_current(voltages, a, b, ohms)` — the current flowing from node `a` to node
   `b` through that resistor.
3. `supply_current(voltages, resistors, node)` — the current a supply must push into
   `node`, which is the sum of the currents leaving that node through every resistor
   attached to it.
4. `power_report(voltages, resistors, fixed)` — returns the tuple
   `(supplied, dissipated)`: the total power out of all supplies, and the total power
   turned into heat by all resistors. If your solver is right these two agree to many
   decimal places, and that is the check you should run on every circuit you ever
   solve.
5. `bottom_for(vin, vout, r_top, r_load)` — the loaded-divider design function from
   module 4, brought along so the capstone can design a circuit and then verify it
   with the solver.

## Building the matrix

For each resistor `(a, b, R)` with conductance $g = 1/R$, add $g$ to the diagonal of
both `a` and `b`, and subtract $g$ from the two off-diagonal entries joining them —
skipping anything involving node 0, which has no row and no column because its
voltage is already known. That pattern is exactly KCL written out; work through a
two-node example by hand once and you will never need to look it up again.

Then, for each fixed node, throw away the row you just built for it and put a single
1 on its diagonal with the known voltage on the right-hand side.

## Suggested order

Get `solve_network` right on a single resistor first — one node, one equation, and you
can check the answer in your head. Then a divider, then the ladder in the tests. The
power report is the last thing to write and the first thing to trust.

The Python is a step up from the one-line labs, but only a step: a list of lists, a
couple of `for` loops, and a dictionary you walk with `.items()`. Nothing else, and
the hints spell out each piece. If those constructs are new, EE131 (Programming for
Engineers) covers them in its first weeks and runs alongside this course.
''',
        "deliverables": [
            "`solve_network`, building the conductance matrix from the resistor list and solving it, with ground fixed at 0 V and every supply node fixed at its stated voltage.",
            "`branch_current`, returning the current through one named resistor from the solved node voltages.",
            "`supply_current`, returning the current a supply pushes into a fixed node, by summing what leaves that node through the resistors.",
            "`power_report`, returning total supplied and total dissipated power, which must agree for any correct solution.",
            "`bottom_for`, the loaded-divider design function, plus a comment in `main.py` naming one circuit you designed with it and verified with `solve_network`.",
        ],
        "constraints": [
            "The standard library only. No NumPy, and certainly no circuit-simulation package — `linsolve` in `dcsolve.py` is the only linear algebra you need.",
            "Do not edit `dcsolve.py`.",
            "Node 0 is ground and always has voltage 0.0. It never gets a row or a column in the matrix.",
            "`solve_network` must work for any number of nodes, not just the sizes that appear in the checks.",
            "Do not special-case the test circuits. A solver that recognises a divider and returns the divider formula is not a solver.",
        ],
        "rubric": [
            {"criterion": "Matrix assembly", "weight": 30,
             "evidence": "Conductances are stamped on the diagonal and off-diagonal correctly, ground is excluded, and fixed nodes replace their own row — demonstrated on networks of one, two and three unknown nodes."},
            {"criterion": "Currents from voltages", "weight": 20,
             "evidence": "branch_current and supply_current return the right magnitude and the right sign on a divider and on a ladder, matching hand calculations."},
            {"criterion": "Power conservation", "weight": 25,
             "evidence": "power_report's two totals agree to within 1e-9 on every test network, which is only possible if the node voltages are genuinely correct."},
            {"criterion": "Design and verification", "weight": 25,
             "evidence": "bottom_for produces a resistor that, when fed back through solve_network as a real three-resistor circuit, gives the requested output voltage."},
        ],
        "hints": [
            "Build the matrix as a list of lists of floats, size `n_nodes` by `n_nodes`, and index node `k` at row and column `k - 1`.",
            "Guard every stamp with `if a:` and `if b:` — node 0 is ground and has no row.",
            "For a fixed node, overwrite its whole row with zeros and a single 1.0 on the diagonal, and set that entry of the right-hand side to the supply voltage. Do this after all the resistors are stamped, not before.",
            "`supply_current` should loop over the resistor list and pick out the ones with the node at either end, remembering that `(a, b, R)` might have the node in either position.",
            "If the two power totals disagree, the sign convention in `supply_current` is the usual culprit: the power a supply delivers is its voltage times the current flowing *out* of it into the network.",
        ],
        "files": [
            {"name": "dcsolve.py", "ro": True, "content": r'''
"""Gaussian elimination with partial pivoting. Do not edit.

This is the one piece of machinery the capstone hands you: given a square matrix A
and a right-hand side b, it returns the x that satisfies A x = b. Nothing in it knows
anything about circuits, which is the point — the physics is entirely in how you fill
A and b in.
"""


def linsolve(A, b):
    """Solve A x = b for x. A is a list of rows; b is a list. Returns a list."""
    n = len(b)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-15:
            raise ValueError(
                "singular matrix: node %d has no path to a known voltage" % (col + 1)
            )
        M[col], M[pivot] = M[pivot], M[col]
        for r in range(col + 1, n):
            f = M[r][col] / M[col][col]
            if f == 0.0:
                continue
            for k in range(col, n + 1):
                M[r][k] -= f * M[col][k]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n] - sum(M[i][k] * x[k] for k in range(i + 1, n))
        x[i] = s / M[i][i]
    return x
'''},
            {"name": "main.py", "content": r'''
"""Nodal analysis: Kirchhoff's current law, written once and solved for any network.

Designed and verified with this file:
    TODO: name a circuit you designed with bottom_for and checked with solve_network.
"""

from dcsolve import linsolve


def solve_network(n_nodes, resistors, fixed):
    """Node voltages of a resistor network.

    n_nodes    number of non-ground nodes, numbered 1..n_nodes
    resistors  list of (a, b, ohms); node 0 is ground
    fixed      dict {node: volts} for nodes held by a supply

    Returns a list of length n_nodes + 1 whose first entry is 0.0 (ground).
    """
    A = [[0.0] * n_nodes for _ in range(n_nodes)]
    b = [0.0] * n_nodes
    # TODO: stamp every resistor's conductance into A, skipping node 0.
    # TODO: replace the row of each fixed node with 1.0 on the diagonal.
    return [0.0] * (n_nodes + 1)


def branch_current(voltages, a, b, ohms):
    """Current flowing from node a to node b through a resistor of `ohms`."""
    # TODO: Ohm's law across the two node voltages.
    return 0.0


def supply_current(voltages, resistors, node):
    """Current a supply must push into `node` to hold it where it is."""
    # TODO: sum what leaves `node` through every resistor attached to it.
    return 0.0


def power_report(voltages, resistors, fixed):
    """Return (supplied, dissipated) in watts. They should be equal."""
    # TODO: supplies deliver V * I; resistors dissipate (dV)^2 / R.
    return (0.0, 0.0)


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor of a divider giving `vout` with `r_load` connected."""
    # TODO: the module 4 design formula.
    return 0.0


if __name__ == "__main__":
    # a 9 V supply, 20 k on top, 11.1 k below, feeding a 100 k load
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    net = [(1, 2, 20000.0), (2, 0, rb), (2, 0, 100000.0)]
    v = solve_network(2, net, {1: 9.0})
    print("node voltages:", [round(x, 6) for x in v])
    print("supply current:", supply_current(v, net, 1), "A")
    print("power (supplied, dissipated):", power_report(v, net, {1: 9.0}))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""Nodal analysis: Kirchhoff's current law, written once and solved for any network.

Designed and verified with this file:
    a 3.00 V rail for a 100 k load, taken from a 9 V battery with a 20 k top
    resistor. bottom_for gives 11111.11 ohms; solve_network on the resulting
    three-resistor circuit returns 3.000000 V at the load and 300 uA out of the
    battery, and the two halves of power_report agree to 1e-18.
"""

from dcsolve import linsolve


def solve_network(n_nodes, resistors, fixed):
    """Node voltages of a resistor network.

    n_nodes    number of non-ground nodes, numbered 1..n_nodes
    resistors  list of (a, b, ohms); node 0 is ground
    fixed      dict {node: volts} for nodes held by a supply

    Returns a list of length n_nodes + 1 whose first entry is 0.0 (ground).
    """
    A = [[0.0] * n_nodes for _ in range(n_nodes)]
    b = [0.0] * n_nodes

    for (a, bb, ohms) in resistors:
        g = 1.0 / ohms
        if a:
            A[a - 1][a - 1] += g
        if bb:
            A[bb - 1][bb - 1] += g
        if a and bb:
            A[a - 1][bb - 1] -= g
            A[bb - 1][a - 1] -= g

    for node, volts in fixed.items():
        A[node - 1] = [0.0] * n_nodes
        A[node - 1][node - 1] = 1.0
        b[node - 1] = float(volts)

    return [0.0] + list(linsolve(A, b))


def branch_current(voltages, a, b, ohms):
    """Current flowing from node a to node b through a resistor of `ohms`."""
    return (voltages[a] - voltages[b]) / ohms


def supply_current(voltages, resistors, node):
    """Current a supply must push into `node` to hold it where it is."""
    total = 0.0
    for (a, b, ohms) in resistors:
        if a == node:
            total += branch_current(voltages, a, b, ohms)
        elif b == node:
            total += branch_current(voltages, b, a, ohms)
    return total


def power_report(voltages, resistors, fixed):
    """Return (supplied, dissipated) in watts. They should be equal."""
    supplied = 0.0
    for node, volts in fixed.items():
        supplied += float(volts) * supply_current(voltages, resistors, node)
    dissipated = 0.0
    for (a, b, ohms) in resistors:
        dv = voltages[a] - voltages[b]
        dissipated += dv * dv / ohms
    return (supplied, dissipated)


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor of a divider giving `vout` with `r_load` connected."""
    ratio = vout / vin
    x = r_top * ratio / (1.0 - ratio)
    return 1.0 / (1.0 / x - 1.0 / r_load)


if __name__ == "__main__":
    # a 9 V supply, 20 k on top, 11.1 k below, feeding a 100 k load
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    net = [(1, 2, 20000.0), (2, 0, rb), (2, 0, 100000.0)]
    v = solve_network(2, net, {1: 9.0})
    print("node voltages:", [round(x, 6) for x in v])
    print("supply current:", supply_current(v, net, 1), "A")
    print("power (supplied, dissipated):", power_report(v, net, {1: 9.0}))
'''},
        ],
        "tests": [
            {"name": "one resistor across a supply", "code": r'''
net = [(1, 0, 3000.0)]
v = solve_network(1, net, {1: 12.0})
assert len(v) == 2, f"one non-ground node means two voltages including ground, got {len(v)}"
assert abs(v[0]) < 1e-12, "node 0 is ground and must be exactly 0 V"
assert abs(v[1] - 12.0) < 1e-9, f"the supply holds node 1 at 12 V, got {v[1]}"
i = branch_current(v, 1, 0, 3000.0)
assert abs(i - 0.004) < 1e-12, f"12 V across 3 k is 4 mA, got {i}"
'''},
            {"name": "a loaded divider matches the hand calculation", "code": r'''
net = [(1, 2, 20000.0), (2, 0, 10000.0), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 9.0})
assert abs(v[1] - 9.0) < 1e-9, f"node 1 is held at 9 V, got {v[1]}"
assert abs(v[2] - 2.8125) < 1e-9, \
    f"10k parallel 100k is 9090.9 ohms, so the output is 2.8125 V, got {v[2]}"
'''},
            {"name": "a three-node ladder", "code": r'''
net = [(1, 2, 1000.0), (2, 0, 1000.0), (2, 3, 1000.0), (3, 0, 1000.0)]
v = solve_network(3, net, {1: 10.0})
assert abs(v[2] - 4.0) < 1e-9, f"node 2 should sit at 4 V, got {v[2]}"
assert abs(v[3] - 2.0) < 1e-9, f"node 3 should sit at 2 V, got {v[3]}"
i = supply_current(v, net, 1)
assert abs(i - 0.006) < 1e-12, f"6 V across the first 1 k is 6 mA out of the supply, got {i}"
'''},
            {"name": "energy is conserved on the ladder", "code": r'''
net = [(1, 2, 1000.0), (2, 0, 1000.0), (2, 3, 1000.0), (3, 0, 1000.0)]
v = solve_network(3, net, {1: 10.0})
supplied, dissipated = power_report(v, net, {1: 10.0})
assert abs(supplied - 0.06) < 1e-12, f"10 V at 6 mA is 60 mW supplied, got {supplied}"
assert abs(supplied - dissipated) < 1e-9, \
    f"supplied {supplied} and dissipated {dissipated} must agree"
'''},
            {"name": "energy is conserved on the divider too", "code": r'''
net = [(1, 2, 20000.0), (2, 0, 11111.111111111111), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 9.0})
supplied, dissipated = power_report(v, net, {1: 9.0})
assert abs(supplied - 0.0027) < 1e-12, f"9 V at 300 uA is 2.7 mW, got {supplied}"
assert abs(supplied - dissipated) < 1e-12, \
    f"supplied {supplied} and dissipated {dissipated} must agree"
'''},
            {"name": "a design, verified by the solver", "code": r'''
rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
assert abs(rb - 11111.111111111111) < 1e-6, f"expected about 11.111 k, got {rb}"
net = [(1, 2, 20000.0), (2, 0, rb), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 9.0})
assert abs(v[2] - 3.0) < 1e-9, f"the designed divider should give 3.000 V, got {v[2]}"
i = supply_current(v, net, 1)
assert abs(i - 0.0003) < 1e-12, f"the battery should give 300 uA, got {i}"
'''},
            {"name": "a second design, on a different rail", "code": r'''
rb = bottom_for(5.0, 3.3, 33000.0, 100000.0)
net = [(1, 2, 33000.0), (2, 0, rb), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 5.0})
assert abs(v[2] - 3.3) < 1e-9, f"expected 3.3 V, got {v[2]}"
supplied, dissipated = power_report(v, net, {1: 5.0})
assert abs(supplied - dissipated) < 1e-12, "the power check must hold here as well"
'''},
            {"name": "the solver is general, not a divider in disguise", "code": r'''
net = [(1, 2, 500.0), (2, 3, 1500.0), (3, 0, 2000.0), (2, 0, 4000.0), (1, 3, 8000.0)]
v = solve_network(3, net, {1: 24.0})
assert abs(v[1] - 24.0) < 1e-9, "node 1 is fixed by the supply"
for k in (2, 3):
    leaving = 0.0
    for (a, b, r) in net:
        if a == k:
            leaving += branch_current(v, a, b, r)
        elif b == k:
            leaving += branch_current(v, b, a, r)
    assert abs(leaving) < 1e-9, \
        f"KCL must hold at node {k}: currents leaving sum to {leaving}, not 0"
supplied, dissipated = power_report(v, net, {1: 24.0})
assert supplied > 0, "the supply should be delivering power, not absorbing it"
assert abs(supplied - dissipated) < 1e-9, \
    f"supplied {supplied} and dissipated {dissipated} must agree"
'''},
        ],
    },
}
